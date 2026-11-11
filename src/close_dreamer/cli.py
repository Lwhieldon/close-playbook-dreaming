"""Command line: close-dreamer <command>.

Free commands (no API calls): estimate, lint, diff, transcripts.
Paid commands (print an estimate, ask before spending, honor --budget): dream, ask, evaluate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from . import config, memory
from . import transcripts as tx

STATE = config.OUTPUT / "dream_state.json"


def _probes() -> tuple[list[str], list[str]]:
    """The planted secret and injected instruction, so lint can prove they stayed out of memory."""
    gt = config.DATA / "ground_truth.yaml"
    if not gt.exists():
        return [], []
    data = yaml.safe_load(gt.read_text(encoding="utf-8"))
    return [data["secret"]["text"]], [data["injected_instruction"]["text"]]


def _state() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def _confirm(prompt: str, yes: bool) -> bool:
    if yes:
        return True
    try:
        return input(f"{prompt} [y/N] ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def _selection(args) -> list[tx.Transcript]:
    all_t = tx.load(config.TRANSCRIPTS)
    after = args.after
    if after is None and not getattr(args, "full", False):
        after = _state().get(str(Path(args.playbook).resolve()))
    return tx.select(all_t, through=args.through, after=after)


def cmd_transcripts(args) -> int:
    for t in tx.load(config.TRANSCRIPTS):
        print(f"{t.period or 'notes':<8} {t.size:>7,}  {t.name}  {t.title}")
    return 0


def cmd_estimate(args) -> int:
    from .dream import estimate

    chosen = _selection(args)
    print("\n".join(f"  {t.period or 'notes':<8} {t.name}" for t in chosen) or "  (none selected)")
    print(estimate(chosen, Path(args.playbook), config.Models())[1])
    return 0


def cmd_dream(args) -> int:
    chosen = _selection(args)
    if not chosen:
        print("No new transcripts for that range (use --full to re-dream everything).")
        return 1
    print("Transcripts to dream over:")
    print("\n".join(f"  {t.period or 'notes':<8} {t.name}" for t in chosen))

    if args.mode == "managed":
        from . import managed

        if not _confirm(f"Run on Managed Agents with a ${args.budget:.2f} budget?", args.yes):
            return 1
        out = managed.run(
            chosen,
            budget_usd=args.budget,
            store_id=args.store_id,
            **({"instructions": args.instructions} if args.instructions else {}),
        )
        secrets, injections = _probes()
        print(memory.lint(out, extra_secrets=secrets, extra_injections=injections).summary())
        return 0

    from .dream import dream, estimate

    est, text = estimate(chosen, Path(args.playbook), config.Models())
    print(text)
    if not _confirm(f"Spend up to ${args.budget:.2f} (estimate ${est:.2f})?", args.yes):
        return 1
    client = config.make_client()
    secrets, injections = _probes()
    result = dream(
        client,
        chosen,
        Path(args.playbook),
        config.SNAPSHOTS,
        budget_usd=args.budget,
        concurrency=args.concurrency,
        instructions=args.instructions,
        label=f"before-{args.through or 'all'}",
        extra_secrets=secrets,
        extra_injections=injections,
        on_event=print if args.verbose else _quiet,
    )
    print(result.report())
    periods = [t.period for t in chosen if t.period]
    if periods:
        state = _state() | {str(Path(args.playbook).resolve()): max(periods)}
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(f"Snapshot of the playbook before this dream: {result.snapshot}")
    print(f'See what changed:  close-dreamer diff --before "{result.snapshot}"')
    return 0


def _quiet(msg: str) -> None:
    if not msg.startswith("["):  # hide per-tool-call lines unless --verbose
        print(msg)


def cmd_lint(args) -> int:
    secrets, injections = _probes()
    rep = memory.lint(Path(args.playbook), extra_secrets=secrets, extra_injections=injections)
    print(rep.summary())
    return 0 if rep.ok else 2


def cmd_diff(args) -> int:
    before = Path(args.before) if args.before else _latest_snapshot()
    if before is None:
        print("No snapshot found; run a dream first or pass --before.")
        return 1
    print(f"Diff {before} -> {args.playbook}")
    print(memory.diff(before, Path(args.playbook)))
    return 0


def _latest_snapshot() -> Path | None:
    snaps = sorted(config.SNAPSHOTS.glob("*")) if config.SNAPSHOTS.exists() else []
    return snaps[-1] if snaps else None


def cmd_ask(args) -> int:
    from .evaluate import answer
    from .usage import UsageTracker

    client = config.make_client()
    tracker = UsageTracker(budget_usd=args.budget)
    print(
        answer(
            client,
            args.question,
            args.condition,
            models=config.Models(),
            tracker=tracker,
            transcripts_dir=config.TRANSCRIPTS,
            playbook_dir=Path(args.playbook),
        )
    )
    print(f"\n(cost ${tracker.total_usd:.4f})")
    return 0


def cmd_evaluate(args) -> int:
    from . import evaluate as ev

    questions = ev.load_questions(config.DATA / "eval_questions.yaml")
    if args.questions:
        wanted = set(args.questions.split(","))
        questions = [q for q in questions if q["id"] in wanted]
    conditions = tuple(args.conditions.split(","))
    bad = set(conditions) - set(ev.CONDITIONS)
    if bad:
        print(f"Unknown condition(s): {', '.join(sorted(bad))}")
        return 1
    n = len(questions) * len(conditions)
    if not _confirm(f"Answer and grade {n} question/condition pairs, budget ${args.budget:.2f}?", args.yes):
        return 1
    client = config.make_client()
    graded, tracker = ev.run(
        client,
        questions,
        conditions=conditions,
        transcripts_dir=config.TRANSCRIPTS,
        playbook_dir=Path(args.playbook),
        budget_usd=args.budget,
        concurrency=args.concurrency,
    )
    print(ev.summarize(graded, tracker))
    print(tracker.table())
    print(f"Saved: {ev.save(graded, tracker, config.RUNS)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="close-dreamer", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="command", required=True)

    def playbook_arg(sp):
        sp.add_argument("--playbook", default=str(config.PLAYBOOK), help="Playbook folder (default output/playbook)")

    def range_args(sp):
        sp.add_argument("--through", help="Last close period to include, e.g. 2026-09")
        sp.add_argument("--after", help="Only periods after this one (default: what this playbook already saw)")
        sp.add_argument("--full", action="store_true", help="Ignore what the playbook already saw")

    s = sub.add_parser("transcripts", help="List transcripts and their close periods (free)")
    s.set_defaults(func=cmd_transcripts)

    s = sub.add_parser("estimate", help="Estimate a dream's cost (free)")
    range_args(s)
    playbook_arg(s)
    s.set_defaults(func=cmd_estimate)

    s = sub.add_parser("dream", help="Dream over transcripts into the playbook (paid)")
    range_args(s)
    playbook_arg(s)
    s.add_argument("--mode", choices=["local", "managed"], default="local")
    s.add_argument("--budget", type=float, default=2.0, help="Stop when list-price spend passes this (USD)")
    s.add_argument("--concurrency", type=int, default=4)
    s.add_argument("--instructions", help="Extra emphasis for the analyzers and organizer")
    s.add_argument("--store-id", help="Managed mode: update this memory store instead of creating one")
    s.add_argument("--yes", action="store_true", help="Don't ask for confirmation")
    s.add_argument("--verbose", action="store_true", help="Print every tool call")
    s.set_defaults(func=cmd_dream)

    s = sub.add_parser("lint", help="Check the playbook's shape and safety (free)")
    playbook_arg(s)
    s.set_defaults(func=cmd_lint)

    s = sub.add_parser("diff", help="Show what a dream changed (free)")
    playbook_arg(s)
    s.add_argument("--before", help="Snapshot folder (default: the latest snapshot)")
    s.set_defaults(func=cmd_diff)

    s = sub.add_parser("ask", help="Ask the close assistant one question (paid)")
    s.add_argument("question")
    s.add_argument("--condition", choices=["none", "transcripts", "playbook"], default="playbook")
    s.add_argument("--budget", type=float, default=0.25)
    playbook_arg(s)
    s.set_defaults(func=cmd_ask)

    s = sub.add_parser("evaluate", help="Compare no memory, raw transcripts and the playbook (paid)")
    s.add_argument("--conditions", default="none,transcripts,playbook")
    s.add_argument("--questions", help="Comma-separated question ids (default: all)")
    s.add_argument("--budget", type=float, default=2.0)
    s.add_argument("--concurrency", type=int, default=4)
    s.add_argument("--yes", action="store_true")
    playbook_arg(s)
    s.set_defaults(func=cmd_evaluate)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except config.MissingCredentials as exc:
        print(exc, file=sys.stderr)
        return 3
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
