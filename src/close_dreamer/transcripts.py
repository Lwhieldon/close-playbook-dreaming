"""Load close-assistant transcripts and select them by close period.

A session's close period is the month before the session was created: a session on 2026-09-02 works
on the August (2026-08) close. Files without a SESSION line (pasted notes) belong to the earliest
period, so they are read on the first dream.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SESSION_LINE = re.compile(r"^SESSION (\S+): (.*) \(agent .*; created (\d{4})-(\d{2})-\d{2}T", re.MULTILINE)
SUFFIXES = {".txt", ".md", ".json", ".jsonl", ".log"}


@dataclass(frozen=True)
class Transcript:
    path: Path
    name: str
    session_id: str | None
    title: str
    period: str | None  # "YYYY-MM" close period, None for notes

    @property
    def text(self) -> str:
        return self.path.read_text(encoding="utf-8")

    @property
    def size(self) -> int:
        return self.path.stat().st_size


def close_period(year: int, month: int) -> str:
    """The close a session created in year/month works on: the previous month."""
    month -= 1
    if month == 0:
        year, month = year - 1, 12
    return f"{year:04d}-{month:02d}"


def load(folder: Path) -> list[Transcript]:
    out = []
    for p in sorted(Path(folder).iterdir()):
        if p.suffix.lower() not in SUFFIXES or not p.is_file() or p.stat().st_size == 0:
            continue
        head = p.read_text(encoding="utf-8")[:2000]
        m = SESSION_LINE.search(head)
        if m:
            out.append(Transcript(p, p.name, m.group(1), m.group(2), close_period(int(m.group(3)), int(m.group(4)))))
        else:
            first = head.splitlines()[0].lstrip("# ").strip() if head else p.name
            out.append(Transcript(p, p.name, None, first, None))
    return out


def select(transcripts: list[Transcript], through: str | None = None, after: str | None = None) -> list[Transcript]:
    """Transcripts for close periods in (after, through]. Notes count as the earliest period, so they are
    included whenever `after` is None (the first dream)."""
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
