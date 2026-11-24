"""Token usage, list-price cost, budget guard and a pre-run estimate.

Prices are US dollars per million tokens at list price (the same table the Anthropic cookbook's helper
uses). Check https://platform.claude.com/docs/en/about-claude/pricing before relying on a figure.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field

PRICES = {
    "claude-opus-5-5": {"input": 4.00, "cache_write": 5.00, "cache_read": 0.20, "output": 20.00},
    "claude-sonnet-5-5": {"input": 2.00, "cache_write": 2.50, "cache_read": 0.10, "output": 10.00},
    "claude-haiku-5-5": {"input": 0.10, "cache_write": 0.125, "cache_read": 0.01, "output": 0.50},
}
# A Claude Haiku 5.5 request whose prompt is over 100,000 tokens pays these instead.
LONG_PROMPT = {"claude-haiku-5-5": (100_000, {"input": 0.50, "cache_write": 0.625, "cache_read": 0.05, "output": 2.50})}
FALLBACK_PRICED_AS = "claude-opus-5-5"  # unknown models are priced high so the budget guard errs safe

CHARS_PER_TOKEN = 3.2  # SAP extracts are dense with numbers and punctuation


class BudgetExceeded(RuntimeError):
    pass


def prices_for(model: str, prompt_tokens: int = 0) -> dict:
    if model in LONG_PROMPT and prompt_tokens > LONG_PROMPT[model][0]:
        return LONG_PROMPT[model][1]
    return PRICES.get(model, PRICES[FALLBACK_PRICED_AS])


@dataclass
class Tally:
    requests: int = 0
    input: int = 0
    cache_write: int = 0
    cache_read: int = 0
    output: int = 0
    usd: float = 0.0


@dataclass
class UsageTracker:
    """Adds up usage per label (analyzer, organizer, answer:playbook, judge...) and enforces a budget."""

    budget_usd: float | None = None
    by_label: dict[str, Tally] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def add(self, label: str, model: str, usage) -> float:
        inp = getattr(usage, "input_tokens", 0) or 0
        cw = getattr(usage, "cache_creation_input_tokens", 0) or 0
        cr = getattr(usage, "cache_read_input_tokens", 0) or 0
        out = getattr(usage, "output_tokens", 0) or 0
        p = prices_for(model, inp + cw + cr)
        cost = (inp * p["input"] + cw * p["cache_write"] + cr * p["cache_read"] + out * p["output"]) / 1e6
        with self._lock:
            t = self.by_label.setdefault(label, Tally())
            t.requests += 1
            t.input += inp
            t.cache_write += cw
            t.cache_read += cr
            t.output += out
            t.usd += cost
            total = self.total_usd
        if self.budget_usd is not None and total > self.budget_usd:
            raise BudgetExceeded(f"Spent ${total:.2f}, over the ${self.budget_usd:.2f} budget; stopping.")
        return cost

    @property
    def total_usd(self) -> float:
        return sum(t.usd for t in self.by_label.values())

    def table(self) -> str:
        rows = [f"{'label':<22}{'reqs':>6}{'input':>10}{'cache_w':>10}{'cache_r':>11}{'output':>9}{'USD':>9}"]
        for label, t in sorted(self.by_label.items()):
            rows.append(
                f"{label:<22}{t.requests:>6}{t.input:>10,}{t.cache_write:>10,}{t.cache_read:>11,}{t.output:>9,}"
                f"{t.usd:>9.3f}"
            )
        rows.append(f"{'total':<22}{'':>46}{self.total_usd:>9.3f}")
        return "\n".join(rows)

    def as_dict(self) -> dict:
        return {k: vars(v) for k, v in self.by_label.items()} | {"total_usd": round(self.total_usd, 4)}


ANALYZER_RULES_FACTOR = 1.12  # the step 3 analyzer prompt (evidence gaps, causes) writes about 12% more


def estimate_dream(
    transcript_chars: list[int],
    analyzer_model: str,
    organizer_model: str,
    memory_chars: int = 0,
    organizer_turns: int | None = None,
) -> tuple[float, str]:
    """A rough estimate for one dream, before any request is sent.

    Calibrated on the two measured v3 step 3 dreams (114 sources over an empty playbook, and 15 sources over
    a 136 KB playbook; Claude Haiku 5.5). An analyzer takes about 7 turns: it writes its source to the cache
    once, then each turn re-reads the source plus the playbook pages it has opened. The playbook grows while
    the analyzers run, so they are priced as if it had already grown by a quarter of the new sources.

    The organizer starts from the pages this dream touched (more when the dream was large) and its context
    grows each turn as it reads and edits pages, so late turns can cross 100,000 tokens and pay Haiku's
    long-prompt rates. It takes more turns after a larger dream (about 42 after 114 sources, 27 after 15);
    it is priced turn by turn.
    """
    total = 0.0
    if organizer_turns is None:
        organizer_turns = round(25 + 0.15 * len(transcript_chars))
    source_tokens = sum(transcript_chars) / CHARS_PER_TOKEN
    growing = memory_chars + 0.25 * sum(transcript_chars)  # the playbook as it grows during the dream
    for chars in transcript_chars:
        ctx = chars / CHARS_PER_TOKEN + 6_000 + 0.3 * growing / CHARS_PER_TOKEN
        a = prices_for(analyzer_model, int(ctx + 15_000))
        turn_cost = (ctx + 30_000) * a["cache_write"] + 7 * (ctx + 15_000) * a["cache_read"] + 13_000 * a["output"]
        total += ANALYZER_RULES_FACTOR * turn_cost / 1e6
    start = 6_000 + 0.235 * source_tokens + 0.29 * memory_chars / CHARS_PER_TOKEN
    step = 5_500 + 0.015 * source_tokens  # tokens added to the context per organizer turn
    for turn in range(organizer_turns):
        ctx = start + step * turn
        o = prices_for(organizer_model, int(ctx))
        total += (ctx * o["cache_read"] + step * o["cache_write"] + 2_200 * o["output"]) / 1e6
    text = (
        f"Estimate: {len(transcript_chars)} sources, {sum(transcript_chars):,} characters, analyzer "
        f"{analyzer_model}, organizer {organizer_model}: about ${total:.2f} (list price; calibrated on two "
        "measured dreams, which came within 4% of it)"
    )
    return total, text
