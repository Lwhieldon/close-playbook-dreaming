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
        f"Variance Calculation: Production Orders   Plant {plant}   Period {period}   Version 000   Currency USD",
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


# --- Routine output that real sessions are full of (noise around the facts that matter) ----------------

TB_ACCOUNTS = [
    ("100100", "Petty cash"),
    ("113200", "Bank - payroll"),
    ("120000", "Trade receivables"),
    ("121000", "Allowance for doubtful accounts"),
    ("140000", "Prepaid expenses"),
    ("150000", "Land"),
    ("151000", "Buildings"),
    ("152000", "Machinery and equipment"),
    ("159000", "Accumulated depreciation"),
    ("200000", "Trade payables"),
    ("210000", "Payroll liabilities"),
    ("220000", "Sales tax payable"),
    ("230000", "Customer deposits"),
    ("250000", "Long-term debt"),
    ("300000", "Common stock"),
    ("310000", "Retained earnings"),
    ("400000", "Product revenue"),
    ("401000", "Service revenue"),
    ("410000", "Sales returns and allowances"),
    ("500000", "Cost of goods sold"),
    ("505000", "Freight in"),
    ("510000", "Direct labor"),
    ("515000", "Manufacturing overhead absorbed"),
    ("600000", "Salaries"),
    ("605000", "Benefits"),
    ("620000", "Rent"),
    ("630000", "Utilities"),
    ("640000", "Repairs and maintenance"),
    ("650000", "Travel"),
    ("660000", "Professional fees"),
    ("670000", "IT services"),
    ("680000", "Insurance"),
    ("700000", "Interest expense"),
    ("710000", "Bank charges"),
    ("800000", "Income tax expense"),
]

JOB_NAMES = [
    "FI_AP_PAYMENT_RUN",
    "FI_AR_DUNNING",
    "MM_MRP_RUN_{plant}",
    "CO_ASSESSMENT_CC",
    "CO_DISTRIBUTION",
    "FI_BANK_STMT_IMPORT",
    "FI_LOCKBOX",
    "SD_BILLING_DUE",
    "MM_GR_IR_REPORT",
    "BW_EXTRACT_FI_GL",
    "BW_EXTRACT_CO_PA",
    "FI_RECURRING_ENTRIES",
    "FI_ACCRUAL_REVERSAL",
    "HR_PAYROLL_POST",
    "MM_INVENTORY_SNAPSHOT",
    "QM_LOT_CLOSE",
    "PM_ORDER_SETTLE",
    "FI_TAX_REPORT",
    "CO_PC_ACTUAL_COSTING",
    "FI_INTEREST_CALC",
]


def trial_balance(*, seed: int, company_code: str, period: str, rows: int = 34) -> str:
    """A trial balance excerpt (S_ALR_87012277-style). Accounts that carry story facts are left out."""
    rng = random.Random(seed)
    name, cur = COMPANY_CODES[company_code]
    out = [
        "G/L Account Balances",
        f"Company code {company_code} {name}   Fiscal year 2026   Period {period}   Currency {cur}",
        "-" * 104,
        "| G/L acct | Description                      |    Balance carryfwd |    Period debit |   Period credit |",
        "-" * 104,
    ]
    for acct, desc in TB_ACCOUNTS[:rows]:
        bf = Decimal(rng.randint(-90_000_000, 90_000_000)) / 100
        dr = Decimal(rng.randint(0, 40_000_000)) / 100
        cr = Decimal(rng.randint(0, 40_000_000)) / 100
        out.append(f"| {acct}   | {desc:<32} | {money(bf):>19} | {money(dr):>15} | {money(cr):>15} |")
    out.append("-" * 104)
    out.append("* Excerpt; balances shown before consolidation adjustments")
    return "\n".join(out)


def job_overview(*, seed: int, date: str, plant: str = "1100", rows: int = 18) -> str:
    """Background job overview (SM37-style). All jobs finished; this is the routine noise of a close day."""
    rng = random.Random(seed)
    out = [
        f"Job Overview   Date {date}   User *   Status: scheduled, released, ready, active, finished, cancelled",
        "-" * 96,
        "| Job name                     | Start time | Duration (s) | Status    | Steps |",
        "-" * 96,
    ]
    names = rng.sample(JOB_NAMES, k=min(rows, len(JOB_NAMES)))
    for i, n in enumerate(sorted(names)):
        hh, mm = divmod(60 + i * 17 + rng.randint(0, 9), 60)
        out.append(
            f"| {n.format(plant=plant):<28} | {hh:02d}:{mm:02d}:00   | {rng.randint(4, 1900):>12} | finished  | {rng.randint(1, 4):>5} |"
        )
    out.append(f"* {len(names)} jobs")
    return "\n".join(out)
