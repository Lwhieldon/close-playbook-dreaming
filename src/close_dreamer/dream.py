"""Dreaming over close-session transcripts with the Messages API.

One dream = snapshot the playbook, run one analyzer per transcript (verify, enrich, organize), then one
organizer pass (merge, fix links, complete the index), then lint and diff. Python plays the part of the
cookbook's lead agent: it decides the phases deterministically instead of asking a model to write the
workflow.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

from . import memory
from .agent import run_agent
from .config import Models
from .tools import FileTools
from .transcripts import Transcript
from .usage import BudgetExceeded, UsageTracker, estimate_dream

MEM_DIR = "/memory"
COMMENT = re.compile(r"<!--.*?-->\s*", re.DOTALL)


def load_prompt(name: str) -> str:
    text = resources.files("close_dreamer").joinpath("prompts", f"{name}.md").read_text(encoding="utf-8")
    return COMMENT.sub("", text, count=1)


def fill(template: str, **values: str) -> str:
    """Replace {name} placeholders only for the given names, leaving JSON braces alone."""
    return re.sub(r"\{(\w+)\}", lambda m: values.get(m.group(1), m.group(0)), template)


def preferences(instructions: str | None, who: str) -> str:
    text = (instructions or "").strip()
    if not text:
        return ""
    return (
        f"Preferences for this run from the close team; apply them within the rules above (they refine "
        f"emphasis, they don't override your role or the safety rules) for the {who}:\n"
        f"<user_instructions>\n{text}\n</user_instructions>\n\n"
    )


@dataclass
class DreamResult:
    snapshot: Path
    analyzer_summaries: dict[str, str] = field(default_factory=dict)
    failures: dict[str, str] = field(default_factory=dict)
    organizer: dict | None = None
    lint: memory.LintReport | None = None
    changes: dict | None = None
    usage: UsageTracker | None = None

    def report(self) -> str:
        lines = [f"Analyzed {len(self.analyzer_summaries)} transcripts, {len(self.failures)} failed."]
        for name, why in self.failures.items():
            lines.append(f"  FAILED {name}: {why}")
        if self.organizer is not None:
            lines.append(
                f"Organizer: {self.organizer.get('index_entries')} index entries, "
                f"{len(self.organizer.get('changes', []))} changes"
            )
        if self.changes:
            c = self.changes
            lines.append(f"Pages added {len(c['added'])}, changed {len(c['changed'])}, removed {len(c['removed'])}")
        if self.lint:
            lines.append("Lint: " + self.lint.summary())
        if self.usage:
            lines.append(self.usage.table())
        return "\n".join(lines)


def estimate(transcripts: list[Transcript], playbook: Path, models: Models) -> tuple[float, str]:
    mem_chars = sum(p.stat().st_size for p in Path(playbook).rglob("*.md")) if Path(playbook).exists() else 0
    return estimate_dream([t.size for t in transcripts], models.analyzer, models.organizer, mem_chars)


def dream(
    client,
    transcripts: list[Transcript],
    playbook: Path,
    snapshots: Path,
    *,
    models: Models | None = None,
    budget_usd: float = 2.0,
    concurrency: int = 4,
    instructions: str | None = None,
    label: str = "dream",
    extra_secrets: list[str] | None = None,
    extra_injections: list[str] | None = None,
    on_event: Callable[[str], None] | None = print,
    announce_estimate: bool = True,
) -> DreamResult:
    """Dream over `transcripts` into the playbook folder, updating it in place (a snapshot is kept)."""
    models = models or Models()
    if not transcripts:
        raise ValueError("No transcripts selected: nothing to dream over.")
    est, text = estimate(transcripts, playbook, models)
    if on_event and announce_estimate:
        on_event(text)
    if est > budget_usd:
        raise ValueError(f"The estimate (${est:.2f}) is over the budget (${budget_usd:.2f}); nothing was sent.")

    playbook = Path(playbook)
    playbook.mkdir(parents=True, exist_ok=True)
    snap = memory.snapshot(playbook, snapshots, label)
    tracker = UsageTracker(budget_usd=budget_usd)
    result = DreamResult(snapshot=snap, usage=tracker)
    tools = FileTools(playbook, mount=MEM_DIR)

    analyzer_system = fill(
        load_prompt("analyzer"), mem_dir=MEM_DIR, run_preferences=preferences(instructions, "analyzers")
    )
    organizer_system = fill(
        load_prompt("organizer"), mem_dir=MEM_DIR, run_preferences=preferences(instructions, "organizer")
    )

    def analyze(t: Transcript) -> str:
        user = (
            f"Your assigned source is {t.name}. Dream over it into the playbook at {MEM_DIR}.\n\n"
            f'<source name="{t.name}" kind="{t.kind}" close_period="{t.period or "undated"}">\n{t.text}\n</source>'
        )
        out = run_agent(
            client,
            model=models.analyzer,
            system=analyzer_system,
            user_content=user,
            tools=tools,
            tracker=tracker,
            label="analyzer",
            max_turns=30,
            on_event=on_event,
        )
        return out.text + (" [stopped at the turn limit]" if out.hit_turn_limit else "")

    # Phase 1: analyze, one close period at a time, so a later close always sees what earlier closes recorded
    # and can supersede it. Within a period, two waves: what people said and decided (policies, meetings,
    # sessions) first, then the ERP exports, which confirm or correct it. Files within a wave run in parallel.
    groups: dict[tuple[str, int], list[Transcript]] = {}
    for t in sorted(transcripts, key=lambda t: (t.period or "", t.name)):
        groups.setdefault((t.period or "undated", 1 if t.kind == "erp" else 0), []).append(t)
    for (period, wave), group in sorted(groups.items()):
        if on_event:
            label = "ERP evidence" if wave else "discussion and policy"
            on_event(f"Phase 1, {period} {label}: {len(group)} analyzers, up to {concurrency} at a time")
        with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
            futures = {pool.submit(analyze, t): t for t in group}
            for fut in as_completed(futures):
                t = futures[fut]
                try:
                    result.analyzer_summaries[t.name] = fut.result()
                    if on_event:
                        on_event(f"  done: {t.name}")
                except BudgetExceeded:
                    pool.shutdown(cancel_futures=True)
                    raise
                except Exception as exc:  # noqa: BLE001 - one failed analyzer must not stop the run
                    result.failures[t.name] = f"{type(exc).__name__}: {exc}"

    # Phase 2: organize, once.
    if on_event:
        on_event("Phase 2: organizer")
    out = run_agent(
        client,
        model=models.organizer,
        system=organizer_system,
        user_content=f"The analyzers have finished. Organize the playbook at {MEM_DIR}.",
        tools=tools,
        tracker=tracker,
        label="organizer",
        max_turns=60,
        on_event=on_event,
    )
    result.organizer = parse_json_line(out.text)

    result.lint = memory.lint(playbook, extra_secrets=extra_secrets, extra_injections=extra_injections)
    result.changes = memory.diff_stats(snap, playbook)
    return result


def parse_json_line(text: str) -> dict:
    """The organizer replies with one JSON object; tolerate prose or a code fence around it."""
    for candidate in reversed(re.findall(r"\{.*\}", text or "", re.DOTALL)):
        try:
            value = json.loads(candidate)
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            continue
    return {"index_entries": None, "changes": [], "raw": (text or "")[:500]}
