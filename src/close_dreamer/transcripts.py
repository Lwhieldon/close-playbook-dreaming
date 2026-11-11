"""Load the close corpus and assign each file to a close period.

A dream reads four kinds of source, by top-level folder:

- uploads/             meeting transcripts a team member uploaded (Teams .vtt): discussion and decisions
- erp/                 ERP exports (.csv): the system of record for what was posted, changed and when
- policies/            controller and treasury memos (.txt): authoritative rules
- assistant-sessions/  close-assistant session exports (.txt)

Each file belongs to the close it informs. ERP exports name their posting period (JE_Register_2026-08).
Other files carry a date (in the name, or the SESSION line): a date in the first ten days of a month belongs
to the previous month's close (close work happens right after month end); a later date belongs to that
month's close (a policy issued 7/15 is read in the dream after the July close).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SESSION_LINE = re.compile(r"^SESSION (\S+): (.*) \(agent .*; created (\d{4}-\d{2}-\d{2})T", re.MULTILINE)
DATE_IN_NAME = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
PERIOD_IN_NAME = re.compile(r"_(\d{4})-(\d{2})\.csv$")
SUFFIXES = {".txt", ".md", ".json", ".jsonl", ".log", ".vtt", ".csv"}
KINDS = {"uploads": "meeting", "erp": "erp", "policies": "policy", "assistant-sessions": "session"}
CLOSE_WORK_DAYS = 10  # dates on or before this day of the month belong to the previous month's close


@dataclass(frozen=True)
class Transcript:
    """One source file. (The name is historical: the first version read only assistant transcripts.)"""

    path: Path
    name: str  # path relative to the corpus root, with forward slashes
    kind: str  # meeting | erp | policy | session | other
    title: str
    period: str | None  # "YYYY-MM" close period this file informs
    session_id: str | None = None

    @property
    def text(self) -> str:
        return self.path.read_text(encoding="utf-8")

    @property
    def size(self) -> int:
        return self.path.stat().st_size


Source = Transcript


def close_period(year: int, month: int, day: int = 1) -> str:
    """The close a dated document informs."""
    if day > CLOSE_WORK_DAYS:
        return f"{year:04d}-{month:02d}"
    month -= 1
    if month == 0:
        year, month = year - 1, 12
    return f"{year:04d}-{month:02d}"


def load(folder: Path) -> list[Transcript]:
    folder = Path(folder)
    out = []
    for p in sorted(folder.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in SUFFIXES or p.stat().st_size == 0:
            continue
        rel = p.relative_to(folder).as_posix()
        kind = KINDS.get(rel.split("/", 1)[0], "other") if "/" in rel else "other"
        head = p.read_text(encoding="utf-8", errors="replace")[:2000]
        sid, title, period = None, p.stem, None
        m = SESSION_LINE.search(head)
        if m:
            sid, title = m.group(1), m.group(2)
            y, mo, d = (int(x) for x in m.group(3).split("-"))
            period = close_period(y, mo, d)
            kind = "session" if kind == "other" else kind
        elif pm := PERIOD_IN_NAME.search(p.name):
            period = f"{pm.group(1)}-{pm.group(2)}"
        elif dm := DATE_IN_NAME.search(p.name):
            period = close_period(int(dm.group(1)), int(dm.group(2)), int(dm.group(3)))
        out.append(Transcript(p, rel, kind, title, period, sid))
    return out


def select(transcripts: list[Transcript], through: str | None = None, after: str | None = None) -> list[Transcript]:
    """Sources for close periods in (after, through]. Undated files count as the earliest period, so they
    are included whenever `after` is None (the first dream)."""
    _check(through)
    _check(after)
    chosen = []
    for t in transcripts:
        if t.period is None:
            if after is None:
                chosen.append(t)
            continue
        if through and t.period > through:
            continue
        if after and t.period <= after:
            continue
        chosen.append(t)
    return chosen


def _check(period: str | None) -> None:
    if period is not None and not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", period):
        raise ValueError(f"close period must look like 2026-09, not {period!r}")
