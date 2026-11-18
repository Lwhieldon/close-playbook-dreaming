"""Build the synthetic close corpus in data/corpus/.

Run:  python scripts/build_corpus.py

What a dream reads after each close, shaped like real enterprise exports:

  data/corpus/uploads/             meeting transcripts a close team member uploaded to an agent session
                                   (Teams-style WebVTT with speaker tags)
  data/corpus/erp/                 the monthly close evidence pack, in the formats users pull it in:
                                   JE register and reconciliation status (.xlsx from the report grid),
                                   inventory and production variance by plant (.xlsx), GR/IR open items
                                   (fixed-width spool .txt), the bank statement (BAI2 .dat), PPV,
                                   intercompany matching and change logs (.csv), background job logs (.txt)
  data/corpus/policies/            controller and treasury memos (signed .pdf; one .docx)
  data/corpus/assistant-sessions/  a few close-assistant sessions, named by session id as exported

Story: Tarnwell Industries (fictional), 20 plants in three company codes, closes November 2025 through
October 2026, including the 2025 year end. Rules change more than once,
owners hand over, people in meetings say less than the system shows and sometimes misremember, the same
problems recur, and safety probes (injected instructions, a leaked credential) are planted. A manifest
mapping readable keys to files is written to data/manifest.yaml, outside the corpus folder, so an agent
searching the corpus never sees it. Everything is synthetic.
"""

from __future__ import annotations

import hashlib
import random
import re
import shutil
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import corpus_erp as erp  # noqa: E402
import corpus_org as org  # noqa: E402
import corpus_sessions as sessions  # noqa: E402
import formats  # noqa: E402
from corpus_early import EARLY_MEETINGS, EARLY_POLICIES  # noqa: E402
from corpus_meetings import MEETINGS, ROUTINE  # noqa: E402
from corpus_policies import POLICIES  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"
CORPUS = DATA / "corpus"


# --- Meetings -----------------------------------------------------------------------------------------


def _cues(text: str, max_words: int = 18) -> list[str]:
    """Teams splits long turns into several cues; split on sentences, then by length."""
    out, cur = [], []
    for sentence in re.split(r"(?<=[.?!])\s+", text.strip()):
        words = sentence.split()
        if cur and len(cur) + len(words) > max_words:
            out.append(" ".join(cur))
            cur = []
        cur += words
    if cur:
        out.append(" ".join(cur))
    return out


def _ts(seconds: float) -> str:
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"


# Status chatter about accounts that carry no story facts (never GR/IR, IC, accruals policy, PPV or FX).
STATUS_ACCOUNTS = [
    "prepaid insurance",
    "the payroll clearing account",
    "fixed asset additions",
    "sales tax payable",
    "customer deposits",
    "the inventory reserve",
    "the warranty reserve",
    "the bonus accrual",
    "401k liabilities",
    "the utilities accrual",
    "the rent schedule",
    "petty cash",
    "the lockbox account",
    "deferred revenue",
    "the scrap account",
    "property tax",
]
STATUS_STATE = [
    "done and reviewed",
    "reconciled, no exceptions",
    "rolled forward, nothing new",
    "tied out to the subledger",
    "waiting on support from the plant",
    "about eighty percent done",
    "ready for review",
]
STATUS_REASON = [
    "it's timing and clears next week",
    "a bank fee that posted late",
    "a duplicate entry I'm reversing",
    "a small rounding difference",
    "one invoice that came in after cutoff",
]
STATUS_CC = ["1000", "2000", "3000", *org.plant_names_for_status()]


def routine_line(rng: random.Random) -> str:
    roll = rng.random()
    if roll < 0.35:
        return rng.choice(ROUTINE)
    acct = rng.choice(STATUS_ACCOUNTS)
    if roll < 0.7:
        return f"For {rng.choice(STATUS_CC)}, {acct} is {rng.choice(STATUS_STATE)}."
    amount = f"{rng.randint(2, 900)} {rng.choice(['dollars', 'hundred dollars'])}"
    return f"On {acct} I have a difference of about {amount}, {rng.choice(STATUS_REASON)}."


def render_vtt(key: str, date: str, attendees: list[str], lines: list[tuple[str, str]]) -> str:
    rng = random.Random(f"vtt-{key}")
    host = attendees[0]
    big = len(attendees) >= 5  # kickoffs and reviews run long; one-topic syncs don't
    turns: list[tuple[str, str]] = [
        (host, "Okay, I think everyone's here. Let's get started."),
        (rng.choice(attendees[1:]), "Morning."),
    ]
    # Status round-robins before the real agenda (two rounds in the big meetings).
    for _ in range(2 if big else 1):
        for person in rng.sample(attendees, k=len(attendees)):
            for _ in range(rng.randint(2, 4) if big else rng.randint(1, 2)):
                turns.append((person, routine_line(rng)))
    for speaker, text in lines:
        turns.append((speaker, text))
        for _ in range(rng.choice([0, 0, 1, 2]) if big else rng.choice([0, 0, 1])):
            turns.append((rng.choice(attendees), routine_line(rng)))
    turns += [(rng.choice(attendees), routine_line(rng)) for _ in range(rng.randint(4, 10) if big else 2)]
    turns.append((host, "That's all I have. Thanks everyone."))

    out = ["WEBVTT", ""]
    t = rng.uniform(2.0, 6.0)
    guid = hashlib.md5(key.encode()).hexdigest()
    n = 0
    for speaker, text in turns:
        for cue in _cues(text):
            n += 1
            dur = max(1.2, len(cue.split()) / 2.6)
            out += [
                f"{guid[:8]}-{guid[8:12]}-{guid[12:16]}-{guid[16:20]}-{guid[20:]}/{n}-0",
                f"{_ts(t)} --> {_ts(t + dur)}",
                f"<v {speaker}>{cue}</v>",
                "",
            ]
            t += dur + rng.uniform(0.2, 1.4)
        t += rng.uniform(0.5, 3.0)
    return "\n".join(out)


# --- Build --------------------------------------------------------------------------------------------


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


RUN_BY = "DWHITFIELD"
DOCX_POLICIES = {"memo-owners-2026-07"}  # shared as a Word document; the rest are signed PDFs
GRIR_WIDTHS = [5, 10, 5, 6, 22, 8, 4, 10, 7, 3, 7, 3, 11, 11, 4]


def erp_files(period: str) -> dict[str, tuple[str, object]]:
    """manifest key -> (relative path, content). Content is text, or a callable that writes the file."""
    run_on = erp.CLOSE_START[period]
    sel = [f"Company codes 1000-3000, posting period {period}", f"Run {run_on} by {RUN_BY}"]
    files: dict[str, tuple[str, object]] = {}

    def je_xlsx(path: Path) -> None:
        extra = None
        if period == "2026-01":
            p13 = [r for doc in erp.PERIOD13_JES for r in doc]
            extra = [("Period 13 (2025)", ["Company code 1000, special period 13 of 2025 (audit adjustments)"], p13)]
        formats.xlsx_report(
            path,
            "Tarnwell Industries - Journal Entry Register",
            sel,
            erp.JE_COLUMNS,
            erp.je_register_rows(period),
            money=("Amount",),
            sheets=extra,
            sheet_name=f"Period {period[5:]} ({period[:4]})",
        )

    def recon_xlsx(path: Path) -> None:
        formats.xlsx_report(
            path, "Tarnwell Industries - Balance Sheet Reconciliation Status", sel, erp.RECON_COLUMNS,
            erp.recon_rows(period),
        )  # fmt: skip

    def inv_xlsx(path: Path) -> None:
        formats.xlsx_report(
            path, "Tarnwell Industries - Inventory and WIP by Plant (period end)", sel, org.INV_COLUMNS,
            org.inventory_rows(period), money=org.INV_MONEY,
        )  # fmt: skip

    def var_xlsx(path: Path) -> None:
        formats.xlsx_report(
            path, "Tarnwell Industries - Production Order Variance by Plant (KKS2/CO88 summary)", sel,
            org.VAR_COLUMNS, org.variance_rows(period), money=org.VAR_MONEY,
        )  # fmt: skip

    files[f"je-register-{period}"] = (f"erp/JE_Register_{period}.xlsx", je_xlsx)
    files[f"recon-status-{period}"] = (f"erp/Account_Recon_Status_{period}.xlsx", recon_xlsx)
    files[f"icr-matching-{period}"] = (f"erp/ICR_Matching_{period}.csv", erp.icr(period))
    files[f"plant-inventory-{period}"] = (f"erp/Inventory_WIP_by_Plant_{period}.xlsx", inv_xlsx)
    files[f"prod-variance-{period}"] = (f"erp/Production_Order_Variance_by_Plant_{period}.xlsx", var_xlsx)
    opening, tx = org.bank_transactions(period)
    files[f"bank-{period}"] = (
        f"erp/BAI2_FirstLakes_1000_Operating_{period}.dat",
        formats.bai2(
            sender="071000288",
            receiver="TARNWELL01",
            file_date=erp.LAST_DAY[period],
            account="4471209938",
            currency="USD",
            opening=opening,
            transactions=tx,
        ),
    )
    for plant in ("1100", "1300"):
        if (plant == "1100" and period in erp.ALLIED) or (plant == "1300" and period == "2026-10"):
            rows = erp.grir_rows(plant, period)
            files[f"grir-{plant}-{period}"] = (
                f"erp/GRIR_Open_Items_{plant}_{period}.txt",
                formats.spool_txt(
                    f"Tarnwell Industries  GR/IR clearing 191100 - open items (RFWERE00)  Plant {plant}",
                    [f"Key date {erp.LAST_DAY[period]}   Company code 1000   User {RUN_BY}   Run {run_on}"],
                    list(zip(erp.GRIR_COLUMNS, GRIR_WIDTHS, strict=True)),
                    rows,
                    f"{len(rows)} open items listed.",
                ),
            )
    if period in erp.PPV:
        files[f"ppv-1100-{period}"] = (f"erp/PPV_by_Material_1100_{period}.csv", erp.ppv(period))
    if period in erp.CHANGES:
        files[f"change-log-{period}"] = (f"erp/Change_Log_{period}.csv", erp.change_log(period))
    return files


JOB_LOGS = [
    ("joblog-dayton-2026-08", "erp/SM37_ZPP_PERIODEND_1200_2026-09-01.txt", org.job_log_dayton_aug),
    ("joblog-dayton-rerun-2026-08", "erp/SM37_ZPP_SETTLE_1200_RERUN_2026-09-02.txt", org.job_log_dayton_aug_rerun),
    ("joblog-kc-teco-2026-04", "erp/SM37_ZPP_TECO_1700_2026-05-01.txt", org.job_log_kc_apr),
]


def main() -> None:
    if CORPUS.exists():
        shutil.rmtree(CORPUS)
    manifest: dict[str, dict] = {}

    for key, fname, date, attendees, lines in sorted(EARLY_MEETINGS + MEETINGS, key=lambda m: m[2]):
        rel = f"uploads/{fname}"
        write(CORPUS / rel, render_vtt(key, date, attendees, lines))
        manifest[key] = {"file": rel, "kind": "meeting", "date": date}

    for key, fname, date, text in EARLY_POLICIES + POLICIES:
        stem = fname.rsplit(".", 1)[0]
        if key in DOCX_POLICIES:
            rel = f"policies/{stem}.docx"
            formats.docx_memo(CORPUS / rel, text)
        else:
            rel = f"policies/{stem}.pdf"
            signer = "Elena Park, Treasury" if key.startswith("memo-trs") else "Dana Whitfield, Corporate Controller"
            formats.pdf_memo(CORPUS / rel, text, signed_by=signer)
        manifest[key] = {"file": rel, "kind": "policy", "date": date}

    for period in erp.PERIODS:
        for key, (rel, content) in erp_files(period).items():
            if callable(content):
                (CORPUS / rel).parent.mkdir(parents=True, exist_ok=True)
                content(CORPUS / rel)
            else:
                write(CORPUS / rel, content)
            manifest[key] = {"file": rel, "kind": "erp", "period": period}
    for key, rel, fn in JOB_LOGS:
        write(CORPUS / rel, fn())
        manifest[key] = {"file": rel, "kind": "erp", "date": rel.rsplit("_", 1)[1][:10]}

    for key, fn in sessions.SESSIONS:
        text = fn()
        head = text.splitlines()[0]
        sid = head.split()[1].rstrip(":")
        rel = f"assistant-sessions/{sid}.txt"
        write(CORPUS / rel, text)
        manifest[key] = {"file": rel, "kind": "session", "date": head.rsplit("created ", 1)[1][:10]}

    write(
        DATA / "manifest.yaml",
        "# Readable keys for corpus files (kept outside data/corpus/ on purpose).\n"
        + yaml.safe_dump(manifest, sort_keys=False),
    )
    files = [p for p in CORPUS.rglob("*") if p.is_file()]
    print(f"Wrote {len(files)} files ({sum(p.stat().st_size for p in files):,} bytes on disk) to {CORPUS}")
    for kind in ("meeting", "erp", "policy", "session"):
        print(f"  {kind:<8} {sum(1 for v in manifest.values() if v['kind'] == kind)}")
    by_ext: dict[str, int] = {}
    for f in files:
        by_ext[f.suffix] = by_ext.get(f.suffix, 0) + 1
    print("  formats  " + ", ".join(f"{k} {v}" for k, v in sorted(by_ext.items())))


if __name__ == "__main__":
    main()
