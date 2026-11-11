"""Audit the synthetic data: every eval answer and fact must be backed by a transcript.

Checks:
1. Every `evidence` string in ground_truth.yaml and eval_questions.yaml appears in the named file
   (whitespace-insensitive).
2. Every superseded fact is replaced by a fact whose evidence comes from a later session.
3. The planted injected instruction and secret exist in their source transcripts (so the safety
   checks on dreamed memory are meaningful).

Run:  python scripts/audit_data.py      (exit code 1 on any failure)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

DATA = Path(__file__).resolve().parent.parent / "data"
TRANSCRIPTS = DATA / "transcripts"


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def session_order(name: str) -> int:
    return int(name.split("-", 1)[0])


def main() -> int:
    texts = {p.name: squash(p.read_text(encoding="utf-8")) for p in TRANSCRIPTS.iterdir()}
    truth = yaml.safe_load((DATA / "ground_truth.yaml").read_text(encoding="utf-8"))
    evals = yaml.safe_load((DATA / "eval_questions.yaml").read_text(encoding="utf-8"))
    problems: list[str] = []

    def check(owner: str, evidence: list) -> None:
        for fname, snippet in evidence:
            if fname not in texts:
                problems.append(f"{owner}: file not found: {fname}")
            elif squash(snippet) not in texts[fname]:
                problems.append(f"{owner}: evidence not found in {fname}: {snippet!r}")

    facts = {f["id"]: f for f in truth["facts"]}
    for f in truth["facts"]:
        check(f"fact {f['id']}", f["evidence"])
        if newer_id := f.get("superseded_by"):
            newer = facts.get(newer_id)
            if not newer:
                problems.append(f"fact {f['id']}: superseded_by {newer_id} does not exist")
                continue
            old_max = max(session_order(e[0]) for e in f["evidence"])
            new_max = max(session_order(e[0]) for e in newer["evidence"])
            if new_max <= old_max:
                problems.append(f"fact {f['id']}: replacement {newer_id} is not from a later session")

    for q in evals["questions"]:
        check(f"question {q['id']}", q["evidence"])

    for key in ("injected_instruction", "secret"):
        item = truth[key]
        if squash(item["text"]) not in texts.get(item["source"], ""):
            problems.append(f"{key}: not planted in {item['source']}")

    n_facts, n_q = len(truth["facts"]), len(evals["questions"])
    if problems:
        print("\n".join(f"FAIL {p}" for p in problems))
        return 1
    print(
        f"OK: {n_facts} facts and {n_q} questions are supported by {len(texts)} transcript files; "
        "safety probes planted."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
