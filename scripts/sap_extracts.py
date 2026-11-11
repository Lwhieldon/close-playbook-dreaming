"""Deterministic generators for SAP-style report output used in the synthetic transcripts.

Everything here is synthetic. The report shapes imitate common SAP S/4HANA list output
(line-item lists, GR/IR open items, posting-period status, variance reports, FX valuation
logs) so the transcripts feel like a real manufacturing close. Company, vendor, people and
document numbers are invented. Not affiliated with SAP.

Each generator takes the "key rows" a story needs and pads them with seeded filler rows, so
the important detail is buried the way it would be in a real extract, and totals tie out.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from decimal import Decimal

COMPANY_CODES = {
    "1000": ("Tarnwell Industries Inc.", "USD"),
    "2000": ("Tarnwell Pumpen GmbH", "EUR"),
    "3000": ("Tarnwell de Mexico S. de R.L.", "MXN"),
}

PLANTS = {
    "1100": ("Toledo, OH", "1000"),
    "1200": ("Dayton, OH", "1000"),
    "1300": ("Greenville, SC", "1000"),
    "2100": ("Stuttgart", "2000"),
    "3100": ("Monterrey", "3000"),
}

GL_NAMES = {
    "113100": "Bank - operating",
    "130000": "Raw materials inventory",
    "131000": "Work in process",
    "132000": "Finished goods inventory",
    "191100": "GR/IR clearing - materials",
    "191110": "GR/IR clearing - services",
    "198000": "Intercompany receivable",
    "211000": "Accrued liabilities",
    "298000": "Intercompany payable",
    "520000": "Purchase price variance",
    "520100": "Inventory revaluation - standard cost change",
    "530000": "Production order variances",
    "541000": "Unrealized FX gain/loss",
    "610000": "Depreciation expense",
}

FILLER_VENDORS = [
    ("300112", "Midwest Steel Service"),
    ("300198", "Keystone Castings"),
    ("300233", "Lakeshore Packaging"),
    ("300301", "Ohio Valley Industrial Gas"),
    ("300388", "Precision Seal Co."),
    ("300402", "Buckeye Electric Motors"),
    ("300519", "Great Lakes Freight"),
    ("300620", "Summit Bearings"),
]

FILLER_TEXTS = [
    "Bar stock receipt",
    "Castings lot",
    "Crates and pallets",
    "Shielding gas",
    "O-ring kits",
    "Motor assemblies",
    "Inbound freight",
    "Bearing sets",
]


def money(value: Decimal | float | int) -> str:
    """Format like SAP list output: thousands separators, two decimals, trailing minus."""
    d = Decimal(str(value)).quantize(Decimal("0.01"))
    text = f"{abs(d):,.2f}"
    return f"{text}-" if d < 0 else f"{text} "


@dataclass
class Row:
    plant: str
    doc: str
    doc_type: str
    posting_date: str
    vendor: str
    po: str
    amount: Decimal
    text: str
    gl: str = ""


def _filler_rows(rng: random.Random, n: int, plant: str, month: str, doc_prefix: str) -> list[Row]:
    rows = []
    for _ in range(n):
        vid, _vname = rng.choice(FILLER_VENDORS)
        text = rng.choice(FILLER_TEXTS)
        day = rng.randint(1, 28)
        amt = Decimal(rng.randint(40_000, 2_400_000)) / 100
        sign = -1 if rng.random() < 0.5 else 1
        rows.append(
            Row(
                plant=plant,
                doc=f"{doc_prefix}{rng.randint(10000000, 99999999)}",
                doc_type=rng.choice(["WE", "WE", "RE"]),
                posting_date=f"{month}/{day:02d}/2026",
                vendor=vid,
                po=f"45000{rng.randint(10000, 99999)}",
                amount=Decimal(sign) * amt,
                text=text,
            )
        )
    return rows


def line_items(
    *,
    seed: int,
    company_code: str,
    gl: str,
    plant: str,
    month: str,
    key_rows: list[Row],
    filler: int = 24,
    key_date: str,
    title: str = "G/L Account Line Item Display",
) -> str:
    """An FBL3N-style line item list with key rows mixed among filler rows."""
    rng = random.Random(seed)
    rows = _filler_rows(rng, filler, plant, month, "51")
    for r in key_rows:
        rows.insert(rng.randint(min(4, len(rows)), len(rows)), r)
    name, cur = COMPANY_CODES[company_code]
    out = [
        f"{title}",
        f"Company code {company_code} {name}   Currency {cur}",
        f"G/L account {gl} {GL_NAMES.get(gl, '')}   Open items at key date {key_date}",
        "-" * 118,
        "| Plnt | DocumentNo | Typ | Pstng Date | Vendor | Purch.Doc.  |     Amount in LC | Text",
        "-" * 118,
    ]
    total = Decimal("0")
    for r in rows:
        total += r.amount
        out.append(
            f"| {r.plant} | {r.doc} | {r.doc_type:<3} | {r.posting_date} | {r.vendor} | {r.po:<11} |"
            f" {money(r.amount):>16} | {r.text}"
        )
    out.append("-" * 118)
    out.append(f"* Total open items {len(rows)}{'':>50}{money(total):>16} {cur}")
    return "\n".join(out)


def posting_periods(variant_rows: list[tuple[str, str, str, str, str]]) -> str:
    """OB52-style posting period status. Rows: (variant, account type, from, to, fiscal year)."""
    out = [
        "Posting Periods: Specify Time Intervals",
        "-" * 78,
        "| Var. | A | From acct | To account | From per.1 | Year | To period | Year |",
        "-" * 78,
    ]
    for var, acct_type, frm, to, period in variant_rows:
        out.append(f"| {var} | {acct_type} | {frm:<9} | {to:<10} | {period:>10} | 2026 | {period:>9} | 2026 |")
    return "\n".join(out)


def grir_open_items(*, seed: int, plant: str, key_date: str, key_items: list[tuple], filler: int = 18) -> str:
    """GR/IR open items by PO line with quantity and value differences (MR11-style worklist).

    key_items: (po, item, vendor, vendor_name, material, gr_qty, gr_uom, ir_qty, ir_uom, gr_val, ir_val, age)
    """
    rng = random.Random(seed)
    rows = []
    for _ in range(filler):
        vid, vname = rng.choice(FILLER_VENDORS)
        qty = rng.randint(10, 900)
        val = Decimal(rng.randint(30_000, 900_000)) / 100
        diff = Decimal(rng.choice([0, 0, 0, rng.randint(-5000, 5000)])) / 100
        rows.append(
            (
                f"45000{rng.randint(10000, 99999)}",
                f"{rng.choice([10, 20, 30]):05d}",
                vid,
                vname,
                f"R-{rng.randint(1000, 9999)}",
                qty,
                "EA",
                qty,
                "EA",
                val,
                val + diff,
                rng.randint(3, 45),
            )
        )
    for item in key_items:
        rows.insert(rng.randint(min(4, len(rows)), len(rows)), item)
    out = [
        f"GR/IR Account Maintenance worklist   Plant {plant}   Key date {key_date}",
        "-" * 140,
        "| Purch.Doc.  | Item  | Vendor | Vendor name                | Material | GR qty | UoM | IR qty | UoM |"
        "     GR value |     IR value | Age (d) |",
        "-" * 140,
    ]
    for po, it, vid, vname, mat, gq, gu, iq, iu, gv, iv, age in rows:
        out.append(
            f"| {po:<11} | {it} | {vid} | {vname:<26} | {mat:<8} | {gq:>6} | {gu:<3} | {iq:>6} | {iu:<3} |"
            f" {money(gv):>12} | {money(iv):>12} | {age:>7} |"
        )
    out.append("-" * 140)
    out.append(f"* {len(rows)} PO items with GR/IR differences")
    return "\n".join(out)


def ic_mismatch(*, period: str, pairs: list[tuple]) -> str:
    """Intercompany reconciliation (ICR-style) mismatch report.

    pairs: (cc_a, cc_b, doc_a, doc_b, ref, amt_a_usd, amt_b_usd, status, note)
    """
    out = [
        f"Intercompany Reconciliation - open matching   Period {period}   Group currency USD",
        "-" * 132,
        "| CoCd | Partner | Doc (CoCd) | Doc (Partner) | Reference    |   Amount CoCd |  Amount Partner |"
        " Status     | Note",
        "-" * 132,
    ]
    for a, b, da, db, ref, aa, ab, status, note in pairs:
        out.append(
            f"| {a} | {b}    | {da:<10} | {db:<13} | {ref:<12} | {money(aa):>13} | {money(ab):>15} |"
            f" {status:<10} | {note}"
        )
    return "\n".join(out)


def order_variances(*, plant: str, period: str, orders: list[tuple]) -> str:
    """Production order variance report (KKS2/KKBC-style). orders: (order, material, target, actual,
    variance, settled)."""
    out = [
        f"Variance Calculation: Production Orders   Plant {plant}   Period {period}   Version 000",
        "-" * 104,
        "| Order      | Material  |     Target cost |     Actual cost |        Variance |  Settled to 530000 |",
        "-" * 104,
    ]
    for order, mat, tgt, act, var, settled in orders:
        out.append(
            f"| {order} | {mat:<9} | {money(tgt):>15} | {money(act):>15} | {money(var):>15} | {money(settled):>18} |"
        )
    return "\n".join(out)


def fx_valuation(
    *, company_code: str, key_date: str, rate_type: str, items: list[tuple], test_run: bool = False
) -> str:
    """Foreign currency valuation (FAGL_FCV-style) log. items: (doc, gl, fc_amount, fc, old_rate,
    new_rate, lc_diff)."""
    name, cur = COMPANY_CODES[company_code]
    out = [
        "Foreign Currency Valuation" + ("  ** TEST RUN **" if test_run else ""),
        f"Company code {company_code} {name}   Valuation key date {key_date}   Valuation area US_GAAP",
        f"Exchange rate type {rate_type}   Postings to 541000 Unrealized FX gain/loss, reversal on first day of"
        " next period",
        "-" * 112,
        "| DocumentNo | G/L    |   Amount in FC | FC  |  Old rate |  New rate |   Valuation diff LC |",
        "-" * 112,
    ]
    total = Decimal("0")
    for doc, gl, fc_amt, fc, old, new, diff in items:
        total += Decimal(str(diff))
        out.append(f"| {doc} | {gl} | {money(fc_amt):>14} | {fc} | {old:>9} | {new:>9} | {money(diff):>19} |")
    out.append("-" * 112)
    out.append(f"* Total valuation difference {money(total)} {cur}")
    return "\n".join(out)


def ppv_report(*, plant: str, period: str, rows: list[tuple]) -> str:
    """Purchase price variance by material. rows: (material, description, qty, uom, std_price,
    invoice_price, ppv)."""
    out = [
        f"Purchase Price Variance by Material   Plant {plant}   Period {period}   Account 520000",
        "-" * 112,
        "| Material | Description                 |    Qty | UoM | Std price | Inv. price |            PPV |",
        "-" * 112,
    ]
    total = Decimal("0")
    for mat, desc, qty, uom, std, inv, ppv in rows:
        total += Decimal(str(ppv))
        out.append(f"| {mat:<8} | {desc:<27} | {qty:>6} | {uom:<3} | {std:>9} | {inv:>10} | {money(ppv):>14} |")
    out.append("-" * 112)
    out.append(f"* Total PPV {money(total)} USD (unfavorable = positive)")
    return "\n".join(out)
