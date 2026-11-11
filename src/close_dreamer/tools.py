"""Sandboxed file tools for the dreaming agents (read, write, edit, glob, grep).

The agents see a virtual root, for example "/memory", that maps to one local folder. Every path is
resolved inside that folder; anything that would escape it (.., absolute paths elsewhere, symlinks out)
is refused. A read-only instance exposes only read, glob and grep, which is how the evaluator lets an
answering agent search the playbook or the raw transcripts without changing them.

These mirror the five file tools the Managed Agents cookbook gives its analyzer and organizer.
"""

from __future__ import annotations

import fnmatch
import re
import threading
from pathlib import Path

MAX_FILE_BYTES = 100_000  # same cap the cookbook prompts give memory files
MAX_READ_LINES = 2000
MAX_GREP_HITS = 200


class ToolError(Exception):
    """A tool call the agent made that can't be carried out. Returned to the model as an error result."""


class FileTools:
    def __init__(self, root: Path, mount: str = "/memory", read_only: bool = False):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.mount = "/" + mount.strip("/")
        self.read_only = read_only
        # One lock for all tool calls: concurrent analyzers each see a consistent file system, and the
        # prompts' "re-read before you edit, read back after you write" rules still matter.
        self._lock = threading.Lock()

    # -- paths ---------------------------------------------------------------------------------------

    def resolve(self, path: str) -> Path:
        if not isinstance(path, str) or not path.strip():
            raise ToolError("path is required")
        p = path.strip().replace("\\", "/")
        if p == self.mount or p.startswith(self.mount + "/"):
            p = p[len(self.mount) :]
        elif p.startswith("/"):
            raise ToolError(f"{path} is outside {self.mount}; every path must be under {self.mount}/")
        target = (self.root / p.lstrip("/")).resolve()
        if target != self.root and self.root not in target.parents:
            raise ToolError(f"{path} is outside {self.mount}")
        return target

    def display(self, target: Path) -> str:
        rel = target.relative_to(self.root).as_posix()
        return f"{self.mount}/{rel}" if rel != "." else self.mount

    # -- tools ---------------------------------------------------------------------------------------

    def read(self, path: str, offset: int = 1, limit: int = MAX_READ_LINES) -> str:
        target = self.resolve(path)
        if target.is_dir():
            raise ToolError(f"{path} is a directory; use glob to list it")
        if not target.exists():
            raise ToolError(f"{path} does not exist")
        lines = target.read_text(encoding="utf-8").splitlines()
        offset = max(1, int(offset or 1))
        limit = max(1, min(int(limit or MAX_READ_LINES), MAX_READ_LINES))
        chunk = lines[offset - 1 : offset - 1 + limit]
        numbered = "\n".join(f"{i:>5}\t{line}" for i, line in enumerate(chunk, start=offset))
        more = len(lines) - (offset - 1 + len(chunk))
        tail = f"\n[{more} more lines; read again with offset={offset + len(chunk)}]" if more > 0 else ""
        return (numbered or "(empty file)") + tail

    def write(self, path: str, content: str) -> str:
        self._writable()
        target = self.resolve(path)
        data = content if isinstance(content, str) else str(content)
        if len(data.encode("utf-8")) > MAX_FILE_BYTES:
            raise ToolError(f"content is over {MAX_FILE_BYTES:,} bytes; split it by sub-topic")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(data, encoding="utf-8", newline="\n")
        return f"Wrote {len(data):,} characters to {self.display(target)}"

    def edit(self, path: str, old_string: str, new_string: str, replace_all: bool = False) -> str:
        self._writable()
        target = self.resolve(path)
        if not target.exists():
            raise ToolError(f"{path} does not exist; use write to create it")
        text = target.read_text(encoding="utf-8")
        count = text.count(old_string) if old_string else 0
        if count == 0:
            raise ToolError("old_string was not found; re-read the file, it may have changed")
        if count > 1 and not replace_all:
            raise ToolError(f"old_string occurs {count} times; add context or set replace_all")
        updated = text.replace(old_string, new_string) if replace_all else text.replace(old_string, new_string, 1)
        if len(updated.encode("utf-8")) > MAX_FILE_BYTES:
            raise ToolError(f"the edit would take the file over {MAX_FILE_BYTES:,} bytes")
        target.write_text(updated, encoding="utf-8", newline="\n")
        return f"Edited {self.display(target)} ({count if replace_all else 1} replacement)"

    def glob(self, pattern: str = "**/*") -> str:
        pat = (pattern or "**/*").replace("\\", "/")
        if pat.startswith(self.mount):
            pat = pat[len(self.mount) :]
        pat = pat.lstrip("/") or "**/*"
        hits = sorted(
            p for p in self.root.rglob("*") if p.is_file() and _match(p.relative_to(self.root).as_posix(), pat)
        )
        if not hits:
            return "(no files match)"
        return "\n".join(f"{self.display(p)}  ({p.stat().st_size:,} bytes)" for p in hits)

    def grep(self, pattern: str, glob: str = "**/*", ignore_case: bool = True) -> str:
        try:
            rx = re.compile(pattern, re.IGNORECASE if ignore_case else 0)
        except re.error as exc:
            raise ToolError(f"invalid regex: {exc}") from exc
        pat = (glob or "**/*").replace("\\", "/").removeprefix(self.mount).lstrip("/") or "**/*"
        out = []
        for p in sorted(self.root.rglob("*")):
            if not p.is_file() or not _match(p.relative_to(self.root).as_posix(), pat):
                continue
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if rx.search(line):
                    out.append(f"{self.display(p)}:{i}: {line.strip()[:300]}")
                    if len(out) >= MAX_GREP_HITS:
                        return "\n".join(out) + f"\n[stopped at {MAX_GREP_HITS} matches; narrow the pattern]"
        return "\n".join(out) if out else "(no matches)"

    # -- dispatch ------------------------------------------------------------------------------------

    def definitions(self) -> list[dict]:
        """Tool definitions for the Messages API."""
        m = self.mount
        defs = [
            {
                "name": "read",
                "description": f"Read a text file under {m}/ with line numbers. Use offset/limit to page.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": f"File path under {m}/"},
                        "offset": {"type": "integer", "description": "First line (1-based)"},
                        "limit": {"type": "integer", "description": f"Max lines (<= {MAX_READ_LINES})"},
                    },
                    "required": ["path"],
                },
            },
            {
                "name": "glob",
                "description": f"List files under {m}/ matching a glob such as '**/*.md'.",
                "input_schema": {
                    "type": "object",
                    "properties": {"pattern": {"type": "string"}},
                    "required": ["pattern"],
                },
            },
            {
                "name": "grep",
                "description": f"Search files under {m}/ for a regular expression (case-insensitive by default).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "glob": {"type": "string", "description": "Limit to files matching this glob"},
                        "ignore_case": {"type": "boolean"},
                    },
                    "required": ["pattern"],
                },
            },
        ]
        if not self.read_only:
            defs += [
                {
                    "name": "write",
                    "description": f"Create or overwrite a file under {m}/ (max {MAX_FILE_BYTES:,} bytes).",
                    "input_schema": {
                        "type": "object",
                        "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                        "required": ["path", "content"],
                    },
                },
                {
                    "name": "edit",
                    "description": "Replace an exact string in a file. old_string must be unique unless "
                    "replace_all is true. Re-read the file first; it may have changed.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "old_string": {"type": "string"},
                            "new_string": {"type": "string"},
                            "replace_all": {"type": "boolean"},
                        },
                        "required": ["path", "old_string", "new_string"],
                    },
                },
            ]
        return defs

    def call(self, name: str, args: dict) -> tuple[str, bool]:
        """Run one tool call. Returns (text, is_error)."""
        allowed = {"read", "glob", "grep"} | (set() if self.read_only else {"write", "edit"})
        if name not in allowed:
            return f"Unknown or disabled tool: {name}", True
        if not isinstance(args, dict):
            return "Tool input must be an object", True
        try:
            with self._lock:
                return getattr(self, name)(**args), False
        except ToolError as exc:
            return f"Error: {exc}", True
        except TypeError as exc:  # missing or unexpected arguments
            return f"Error: bad arguments for {name}: {exc}", True

    def _writable(self) -> None:
        if self.read_only:
            raise ToolError("this file system is read-only")


def _match(rel: str, pattern: str) -> bool:
    if fnmatch.fnmatch(rel, pattern):
        return True
    # let "**/*.md" also match top-level files, and "*.md" match at any depth like most glob tools
    if pattern.startswith("**/") and fnmatch.fnmatch(rel, pattern[3:]):
        return True
    return "/" not in pattern and fnmatch.fnmatch(rel.rsplit("/", 1)[-1], pattern)


class MultiTools:
    """Read-only tools over several mounted folders at once (for example /sources and /playbook).

    read routes by path prefix; glob and grep search every mount unless the pattern names one.
    """

    def __init__(self, mounts: list[FileTools]):
        self.mounts = mounts
        self.read_only = True

    def definitions(self) -> list[dict]:
        roots = " and ".join(f"{m.mount}/" for m in self.mounts)
        defs = []
        for d in self.mounts[0].definitions():
            if d["name"] in ("read", "glob", "grep"):
                d = {**d, "description": d["description"].replace(f"{self.mounts[0].mount}/", roots)}
                defs.append(d)
        return defs

    def _owner(self, path: str) -> FileTools | None:
        p = (path or "").replace("\\", "/")
        return next((m for m in self.mounts if p == m.mount or p.startswith(m.mount + "/")), None)

    def call(self, name: str, args: dict) -> tuple[str, bool]:
        if name not in ("read", "glob", "grep") or not isinstance(args, dict):
            return f"Unknown or disabled tool: {name}", True
        if name == "read":
            owner = self._owner(args.get("path", ""))
            if owner is None:
                return f"Error: path must start with one of {[m.mount for m in self.mounts]}", True
            return owner.call(name, args)
        target = args.get("pattern", "") if name == "glob" else args.get("glob", "")
        owner = self._owner(target)
        outs = [owner.call(name, args)] if owner else [m.call(name, args) for m in self.mounts]
        texts = [t for t, _ in outs if not t.startswith("(no ")]
        return ("\n".join(texts) if texts else outs[0][0]), any(e for _, e in outs)
