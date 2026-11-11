"""Audit the synthetic corpus: every eval answer and fact must be backed by a source file.

Checks:
1. Every `evidence` text in ground_truth.yaml and eval_questions.yaml appears in the file its manifest key
   names (whitespace-insensitive; meeting transcripts are compared on their spoken text, without cue ids,
   timestamps or speaker tags).
2. Every superseded fact is replaced by a fact that became true later.
3. The planted injected instructions and secret exist in their sources, so the safety checks on dreamed
   memory are meaningful.
4. Every corpus file gets a close period.

Run:  python scripts/audit_data.py      (exit code 1 on any failure)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

DATA = Path(__file__).resolve().parent.parent / "data"
CORPUS = DATA / "corpus"
sys.path.insert(0, str(DATA.parent / "src"))


def normalize(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".vtt":
        text = " ".join(re.findall(r"<v [^>]+>(.*?)</v>", text))
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    from close_dreamer import transcripts as tx

    manifest = yaml.safe_load((DATA / "manifest.yaml").read_text(encoding="utf-8"))
    truth = yaml.safe_load((DATA / "ground_truth.yaml").read_text(encoding="utf-8"))
    evals = yaml.safe_load((DATA / "eval_questions.yaml").read_text(encoding="utf-8"))
    texts = {key: normalize(CORPUS / v["file"]) for key, v in manifest.items()}
    problems: list[str] = []

    def check(owner: str, evidence: list) -> None:
        for key, snippet in evidence:
            if key not in texts:
                problems.append(f"{owner}: unknown manifest key {key}")
            elif re.sub(r"\s+", " ", snippet).strip() not in texts[key]:
                problems.append(f"{owner}: evidence not found in {key}: {snippet!r}")

    facts = {f["id"]: f for f in truth["facts"]}
    for f in truth["facts"]:
        check(f"fact {f['id']}", f["evidence"])
        if newer_id := f.get("superseded_by"):
            newer = facts.get(newer_id)
            if not newer:
                problems.append(f"fact {f['id']}: superseded_by {newer_id} does not exist")
            elif str(newer["valid_from"]) <= str(f["valid_from"]):
                problems.append(f"fact {f['id']}: replacement {newer_id} is not later")

    for q in evals["questions"]:
        check(f"question {q['id']}", q["evidence"])
    ids = [q["id"] for q in evals["questions"]]
    if len(ids) != len(set(ids)):
        problems.append("duplicate question ids")

    for item in truth["injected_instructions"] + [truth["secret"]]:
        if re.sub(r"\s+", " ", item["text"]) not in texts.get(item["source"], ""):
            problems.append(f"probe not planted in {item['source']}: {item['text']!r}")

    undated = [t.name for t in tx.load(CORPUS) if t.period is None]
    if undated:
        problems.append(f"files without a close period: {undated}")

    if problems:
        print("\n".join(f"FAIL {p}" for p in problems))
        return 1
    print(
        f"OK: {len(truth['facts'])} facts and {len(ids)} questions are supported by {len(texts)} corpus files; "
        "safety probes planted; every file has a close period."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
