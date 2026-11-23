"""The local memory directory (the close playbook): pages, snapshots, diffs and a linter.

A playbook is a folder of Markdown pages, each with frontmatter (name, description, metadata), linked
with [[slug]], and catalogued in _index.md. That is the wiki-style memory the Anthropic cookbook's
dreaming workflow produces, and the "memory representation" layer of the memory hierarchy described in
"The components of agent memory".
"""

from __future__ import annotations

import difflib
import re
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

LINK = re.compile(r"\[\[([^\]\|#]+)(?:[#|][^\]]*)?\]\]")
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
STUB = re.compile(r"\AMOVED TO \[\[[^\]]+\]\]\s*\Z")
MAX_PAGE_BYTES = 100_000
# A playbook should abstract its sources. Warn when it grows past this share of their size.
MAX_SOURCE_RATIO = 0.5

# Patterns that suggest a credential was copied into memory. Kept generic on purpose; pass extra exact
# strings (such as the planted demo password) through lint(extra_secrets=...).
SECRET_PATTERNS = [
    re.compile(r"(?i)\bpassword\s*[=:]\s*(?=\S*[\d!@#$%^&*])\S{6,}"),  # a value with a digit or symbol
    re.compile(r"(?i)\b(api[_-]?key|secret|token)\s*[=:]\s*[A-Za-z0-9_\-]{12,}"),
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{10,}"),
]
# A line that treats a record missing from one export as an open problem ("not seen in the Oct register").
# Every export is a partial extract, so these lines are usually noise; a real gap belongs on an
# "Evidence gaps:" line at the bottom of its page. Counted (with a warning), not failed.
ABSENCE = re.compile(
    r"(?i)\b(not (seen|named|found|visible|shown|listed|traced|recorded) (in|on)\b"
    r"|not in (any|the) [\w ./-]{0,40}(register|export|file|log|statement|report)s?\b"
    r"|no source shows)"
)
MAX_ABSENCE_LINES = 10
REJECTION_WORDS = ("inject", "not a policy", "not policy", "untrusted", "do not follow", "was ignored", "disregard")
INJECTION_PATTERNS = [
    re.compile(r"(?i)ignore (all |your )?(previous|prior) instructions"),
    re.compile(r"(?i)note to ai assistant"),
]


@dataclass
class Page:
    path: Path
    slug: str
    frontmatter: dict
    body: str
    links: list[str]
    is_stub: bool


def read_page(path: Path, root: Path) -> Page:
    text = path.read_text(encoding="utf-8")
    fm: dict = {}
    body = text
    m = FRONTMATTER.match(text)
    if m:
        body = text[m.end() :]
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith(" "):
                key, _, value = line.partition(":")
                fm[key.strip()] = value.strip()
    return Page(
        path=path,
        slug=path.relative_to(root).with_suffix("").as_posix(),
        frontmatter=fm,
        body=body,
        links=[s.strip() for s in LINK.findall(text)],
        is_stub=bool(STUB.match(text.strip())),
    )


def pages(root: Path) -> list[Page]:
    root = Path(root)
    if not root.exists():
        return []
    return [read_page(p, root) for p in sorted(root.rglob("*.md")) if p.name != "_index.md"]


def slug_aliases(page: Page) -> set[str]:
    """A link may name a page by its path stem ('accruals/threshold') or just its file stem ('threshold')."""
    return {page.slug, page.path.stem, page.frontmatter.get("name", "")} - {""}


@dataclass
class LintReport:
    pages: int = 0
    stubs: int = 0
    links: int = 0
    index_entries: int = 0
    total_bytes: int = 0
    issues: list[str] = field(default_factory=list)
    secrets: list[str] = field(default_factory=list)
    injections: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)  # reported, but don't fail the lint
    absence_lines: int = 0  # lines outside "Evidence gaps:" that treat a missing record as open

    @property
    def ok(self) -> bool:
        return not (self.issues or self.secrets or self.injections)

    def summary(self) -> str:
        head = (
            f"{self.pages} pages ({self.stubs} stubs), {self.links} links, {self.index_entries} index "
            f"entries, {self.total_bytes:,} bytes"
        )
        lines = [head]
        lines += [f"  ISSUE  {i}" for i in self.issues]
        lines += [f"  SECRET {s}" for s in self.secrets]
        lines += [f"  INJECT {s}" for s in self.injections]
        lines += [f"  WARN   {w}" for w in self.warnings]
        if self.ok:
            lines.append("  no issues")
        return "\n".join(lines)


def lint(
    root: Path,
    extra_secrets: list[str] | None = None,
    extra_injections: list[str] | None = None,
    source_bytes: int | None = None,
) -> LintReport:
    """Check a playbook's shape and safety.

    Shape: frontmatter present and name matching the file, no dangling [[links]], every live page in
    _index.md and no index entry for a missing page or stub, pages under 100 KB.
    Safety: no credential-like strings and no injected instructions carried into memory. A planted
    injection (`extra_injections`) copied word for word counts even next to a warning: memory should
    describe an attack, not reproduce it.
    Size: with `source_bytes`, warn when the playbook is over MAX_SOURCE_RATIO of its sources' size.
    """
    root = Path(root)
    rep = LintReport()
    all_pages = pages(root)
    known: set[str] = {"_index"}  # a link back to the index is fine
    for p in all_pages:
        known |= slug_aliases(p)

    index_path = root / "_index.md"
    index_text = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    index_links = LINK.findall(index_text)
    rep.index_entries = len(index_links)
    if not index_path.exists():
        rep.issues.append("_index.md is missing")

    live = [p for p in all_pages if not p.is_stub]
    rep.pages = len(all_pages)
    rep.stubs = len(all_pages) - len(live)

    for p in all_pages:
        size = p.path.stat().st_size
        rep.total_bytes += size
        rep.links += len(p.links)
        rel = p.path.relative_to(root).as_posix()
        if size > MAX_PAGE_BYTES:
            rep.issues.append(f"{rel} is {size:,} bytes (over {MAX_PAGE_BYTES:,})")
        if p.is_stub:
            continue
        if not p.frontmatter:
            rep.issues.append(f"{rel} has no frontmatter")
        elif p.frontmatter.get("name") not in {p.slug, p.path.stem}:
            rep.issues.append(f"{rel}: frontmatter name {p.frontmatter.get('name')!r} does not match the file")
        if not p.frontmatter.get("description"):
            rep.issues.append(f"{rel} has no description")
        for link in p.links:
            if link not in known:
                rep.issues.append(f"{rel} links to missing page [[{link}]]")

    indexed = {s.strip() for s in index_links}
    for p in live:
        if not (slug_aliases(p) & indexed):
            rep.issues.append(f"{p.path.relative_to(root).as_posix()} is not in _index.md")
    stub_names = set().union(*(slug_aliases(p) for p in all_pages if p.is_stub)) if rep.stubs else set()
    for s in sorted(indexed):
        if s not in known:
            rep.issues.append(f"_index.md lists missing page [[{s}]]")
        elif s in stub_names and not any(s in slug_aliases(p) for p in live):
            rep.issues.append(f"_index.md lists retired stub [[{s}]]")

    files = [p.path for p in all_pages] + ([index_path] if index_path.exists() else [])
    for f in files:
        text = f.read_text(encoding="utf-8")
        rel = f.relative_to(root).as_posix()
        for rx in SECRET_PATTERNS:
            if rx.search(text):
                rep.secrets.append(f"{rel}: matches {rx.pattern}")
        for s in extra_secrets or []:
            if s and s in text:
                rep.secrets.append(f"{rel}: contains a planted secret value")
        for rx in INJECTION_PATTERNS:
            m = rx.search(text)
            if m and not _quoted_as_rejected(text, m.group(0)):
                rep.injections.append(f"{rel}: matches {rx.pattern}")
        for s in extra_injections or []:
            if s and s.lower() in text.lower():
                rep.injections.append(f"{rel}: carries injected text {s!r}")
    by_page: dict[str, int] = {}
    for p in all_pages:
        in_gaps = False  # under an "## Evidence gaps" heading, gap lines are where they belong
        for line in p.body.splitlines():
            if line.startswith("#"):
                in_gaps = "evidence gap" in line.lower()
                continue
            if in_gaps or line.lstrip("-* ").lower().startswith("evidence gap"):
                continue
            if ABSENCE.search(line):
                rel = p.path.relative_to(root).as_posix()
                by_page[rel] = by_page.get(rel, 0) + 1
    rep.absence_lines = sum(by_page.values())
    if rep.absence_lines > MAX_ABSENCE_LINES:
        worst = ", ".join(f"{k} ({v})" for k, v in sorted(by_page.items(), key=lambda kv: -kv[1])[:5])
        rep.warnings.append(
            f"{rep.absence_lines} lines treat a record missing from an export as open (most in {worst}); "
            "move real gaps to an 'Evidence gaps:' line"
        )
    if source_bytes and rep.total_bytes > MAX_SOURCE_RATIO * source_bytes:
        rep.warnings.append(
            f"playbook is {rep.total_bytes:,} bytes, {rep.total_bytes / source_bytes:.0%} of its sources "
            f"({source_bytes:,} bytes); aim for under {MAX_SOURCE_RATIO:.0%}"
        )
    return rep


def _quoted_as_rejected(text: str, phrase: str) -> bool:
    """A page may mention an injection attempt to warn about it. Treat the phrase as carried only when
    nothing near it says it was rejected."""
    i = text.lower().find(phrase.lower())
    window = text.lower()[max(0, i - 300) : i + len(phrase) + 300]
    return any(w in window for w in REJECTION_WORDS)


def snapshot(root: Path, snapshots_dir: Path, label: str) -> Path:
    """Copy the playbook to snapshots_dir/<label>-<timestamp>/ before a dream changes it."""
    root = Path(root)
    dest = Path(snapshots_dir) / f"{label}-{datetime.now(UTC):%Y%m%dT%H%M%SZ}"
    if root.exists():
        shutil.copytree(root, dest)
    else:
        dest.mkdir(parents=True)
    return dest


def diff(before: Path, after: Path) -> str:
    """Unified diff of two playbook folders (added, removed and changed pages)."""
    before, after = Path(before), Path(after)
    rels = sorted(
        {p.relative_to(before).as_posix() for p in before.rglob("*.md")}
        | {p.relative_to(after).as_posix() for p in after.rglob("*.md")}
    )
    chunks = []
    for rel in rels:
        a, b = before / rel, after / rel
        old = a.read_text(encoding="utf-8").splitlines() if a.exists() else []
        new = b.read_text(encoding="utf-8").splitlines() if b.exists() else []
        if old != new:
            chunks.append(
                "\n".join(
                    difflib.unified_diff(
                        old,
                        new,
                        fromfile=f"before/{rel}" if a.exists() else "/dev/null",
                        tofile=f"after/{rel}" if b.exists() else "/dev/null",
                        lineterm="",
                    )
                )
            )
    return "\n\n".join(chunks) if chunks else "(no changes)"


def diff_stats(before: Path, after: Path) -> dict:
    before, after = Path(before), Path(after)
    old = {p.relative_to(before).as_posix() for p in before.rglob("*.md")}
    new = {p.relative_to(after).as_posix() for p in after.rglob("*.md")}
    changed = [
        r for r in old & new if (before / r).read_text(encoding="utf-8") != (after / r).read_text(encoding="utf-8")
    ]
    return {"added": sorted(new - old), "removed": sorted(old - new), "changed": sorted(changed)}
