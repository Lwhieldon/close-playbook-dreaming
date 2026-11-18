"""Tarnwell's organization (20 plants in three company codes) and the plant-level exports in each close's
evidence pack: inventory and work in process by plant, production order variance by plant, the operating
bank account's BAI2 statement, and background job logs.

Most of these rows are routine, as in a real close. The story threads they carry:
- Houston (1400): the 2025 year-end physical inventory found a large shortage (scrap not reported).
- Kansas City (1700): production orders left released instead of technically completed, so variance
  calculation skipped them from January to March 2026; fixed in the April close with a catch-up.
- Erie (1900): production stopped 03/31/2026; inventory moved to Toledo; out of the close checks from April.
- Greenville (1300): goes live 09/30/2026 (legacy migration), in scope from the October close.
- Dayton (1200): the August 2026 scheduled period-end job ran settlement before WIP and variance.
All content is fictional.
"""

from __future__ import annotations

import random
from decimal import Decimal as D

# (plant, company code, name, kind, plant controller)
PLANTS = [
    ("1100", "1000", "Toledo", "Pumps, machining and assembly", "Sam Okafor"),
    ("1200", "1000", "Dayton", "Pump assembly", "Sam Okafor"),
    ("1300", "1000", "Greenville", "Valve machining (acquired, live 09/30/2026)", "Tessa Lund"),
    ("1400", "1000", "Houston", "Valve bodies and actuators", "Grace Liu"),
    ("1500", "1000", "Tulsa", "Industrial valves", "Owen Bradley"),
    ("1600", "1000", "Charlotte", "Pump seals and spares", "Nia Robinson"),
    ("1700", "1000", "Kansas City", "Fabricated skids", "Derek Holm"),
    ("1800", "1000", "Reno", "Pump motors", "Hannah Sato"),
    ("1900", "1000", "Erie", "Castings finishing (production stopped 03/31/2026)", "Paul Kowalski"),
    ("2100", "2000", "Stuttgart", "Precision pumps", "Jonas Becker"),
    ("2200", "2000", "Mannheim", "Control valves", "Katrin Vogel"),
    ("2300", "2000", "Dortmund", "Heavy pumps", "Felix Brandt"),
    ("2400", "2000", "Leipzig", "Valve assembly", "Anja Krueger"),
    ("2500", "2000", "Nuremberg", "Actuators", "Tobias Engel"),
    ("2600", "2000", "Bremen", "Marine pumps", "Lena Hoffmann"),
    ("3100", "3000", "Monterrey", "Tooling and castings", "Marco Reyes"),
    ("3200", "3000", "Saltillo", "Pump housings", "Diego Fuentes"),
    ("3300", "3000", "Queretaro", "Valve trim", "Sofia Herrera"),
    ("3400", "3000", "Guadalajara", "Electronics and controls", "Ramon Castillo"),
    ("3500", "3000", "Puebla", "Seals and gaskets", "Valeria Campos"),
]
CURRENCY = {"1000": "USD", "2000": "EUR", "3000": "MXN"}
PERIODS = [
    "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04",
    "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10",
]  # fmt: skip


def plant_active(plant: str, period: str) -> bool:
    if plant == "1300":
        return period >= "2026-10"
    if plant == "1900":
        return period <= "2026-03"
    return True


def plant_names_for_status() -> list[str]:
    return [name for _, _, name, _, _ in PLANTS if name not in ("Greenville", "Erie")]


# --- Inventory and WIP by plant ----------------------------------------------------------------------------

INV_COLUMNS = [
    "CompanyCode",
    "Plant",
    "PlantName",
    "Currency",
    "RawMaterials",
    "WorkInProcess",
    "FinishedGoods",
    "TotalInventory",
    "PriorMonthTotal",
    "ChangePct",
    "OpenProdOrders",
    "PlantControllerSignOff",
    "Comment",
]
INV_MONEY = ("RawMaterials", "WorkInProcess", "FinishedGoods", "TotalInventory", "PriorMonthTotal")

# Story overrides: (plant, period) -> fields
INV_STORY = {
    ("1400", "2025-12"): {
        "Comment": "Year-end physical inventory 12/31: count difference -186,420.55 posted MI07 (doc 4900079915). "
        "Valve bodies V-2200 series. See count results."
    },
    ("1400", "2026-03"): {"Comment": "Q1 cycle counts within tolerance (0.3%)."},
    ("1700", "2026-01"): {"Comment": "WIP up; 61 orders released, not TECO."},
    ("1700", "2026-02"): {"Comment": "WIP up again; 118 orders released, not TECO."},
    ("1700", "2026-03"): {"Comment": "WIP high; 174 orders released, not TECO. Under review with corporate."},
    ("1700", "2026-04"): {
        "Comment": "Mass TECO via COHV 05/01 before WIP run; WIP released to variance (catch-up 142,880.40 unfav)."
    },
    ("1900", "2026-03"): {
        "Comment": "Production stopped 03/31. Stock moved to Toledo 1100 by stock transport orders (STO) 03/24-03/31."
    },
    ("1100", "2026-03"): {"Comment": "Includes stock received from Erie 1900 (STO, 2,184,300.00 at standard)."},
    ("1300", "2026-10"): {"Comment": "First close after go-live 09/30. Opening balances from legacy migration."},
}
BASE_INV = {}  # plant -> base total (local currency)


def _base(plant: str, cc: str) -> D:
    rng = random.Random(f"base-{plant}")
    scale = {"1000": (2_500_000, 14_000_000), "2000": (1_800_000, 9_000_000), "3000": (30_000_000, 160_000_000)}[cc]
    return D(rng.randint(*scale))


def inventory_rows(period: str) -> list[dict]:
    idx = PERIODS.index(period)
    rows = []
    for plant, cc, name, _kind, ctl in PLANTS:
        if not plant_active(plant, period) and not (plant == "1900" and period == "2026-04"):
            continue
        rng = random.Random(f"inv-{plant}-{period}")
        prior_rng = random.Random(f"inv-{plant}-{PERIODS[idx - 1]}") if idx else None
        base = _base(plant, cc)

        def total(r, base=base):
            return (base * D(str(r.uniform(0.94, 1.06)))).quantize(D("0.01"))

        tot = total(rng)
        prior = total(prior_rng) if prior_rng else (base * D("0.98")).quantize(D("0.01"))
        wip_share = D(str(rng.uniform(0.12, 0.22)))
        if plant == "1700" and period in ("2026-01", "2026-02", "2026-03"):
            wip_share += D({"2026-01": "0.06", "2026-02": "0.11", "2026-03": "0.16"}[period])
        if plant == "1900" and period == "2026-04":
            tot, wip_share = D("0.00"), D("0")
        raw = (tot * D(str(rng.uniform(0.35, 0.5)))).quantize(D("0.01"))
        wip = (tot * wip_share).quantize(D("0.01"))
        fg = tot - raw - wip
        orders = 0 if tot == 0 else rng.randint(40, 260)
        if plant == "1700" and period in ("2026-01", "2026-02", "2026-03"):
            orders += {"2026-01": 61, "2026-02": 118, "2026-03": 174}[period]
        row = {
            "CompanyCode": cc,
            "Plant": plant,
            "PlantName": name,
            "Currency": CURRENCY[cc],
            "RawMaterials": raw,
            "WorkInProcess": wip,
            "FinishedGoods": fg,
            "TotalInventory": tot,
            "PriorMonthTotal": prior if not (plant == "1300" and period == "2026-10") else "",
            "ChangePct": f"{(tot - prior) / prior * 100:.1f}"
            if prior and not (plant == "1300" and period == "2026-10")
            else "",
            "OpenProdOrders": orders,
            "PlantControllerSignOff": ctl,
            "Comment": "",
        }
        if plant == "1900" and period == "2026-04":
            row["Comment"] = "No stock. Plant closed for production 03/31; asset disposals only."
            row["OpenProdOrders"] = 0
        row.update(INV_STORY.get((plant, period), {}))
        rows.append(row)
    return rows


# --- Production order variance by plant ------------------------------------------------------------------

VAR_COLUMNS = [
    "CompanyCode",
    "Plant",
    "PlantName",
    "OrdersSettled",
    "OrdersReleasedNotTECO",
    "TotalVariance",
    "Currency",
    "LargestOrder",
    "LargestOrderVariance",
    "Comment",
]
VAR_MONEY = ("TotalVariance", "LargestOrderVariance")
VAR_STORY = {
    ("1700", "2026-01"): {"OrdersReleasedNotTECO": 61, "TotalVariance": "312.18", "Comment": "KKS2 skipped 61 orders (status REL)."},
    ("1700", "2026-02"): {"OrdersReleasedNotTECO": 118, "TotalVariance": "-145.02", "Comment": "KKS2 skipped 118 orders (status REL)."},
    ("1700", "2026-03"): {"OrdersReleasedNotTECO": 174, "TotalVariance": "88.40", "Comment": "KKS2 skipped 174 orders (status REL)."},
    ("1700", "2026-04"): {
        "OrdersReleasedNotTECO": 0,
        "TotalVariance": "142880.40",
        "Comment": "Catch-up after mass TECO 05/01: Jan-Mar orders now in variance. TECO step added to checklist.",
    },
    ("1200", "2026-08"): {"Comment": "Settlement rerun 09/02 after scheduled job ran CO88 before KKAO/KKS2."},
    ("1300", "2026-10"): {"Comment": "First period; 3 orders, all settled."},
}  # fmt: skip


def variance_rows(period: str) -> list[dict]:
    rows = []
    for plant, cc, name, _kind, _ctl in PLANTS:
        if not plant_active(plant, period):
            continue
        rng = random.Random(f"var-{plant}-{period}")
        scale = 400_000 if cc == "3000" else 25_000
        var = D(rng.randint(-scale, scale * 2)) / 100 * 4
        n = rng.randint(30, 240) if plant != "1300" else 3
        big = D(rng.randint(scale // 4, scale)) / 100 * 3
        row = {
            "CompanyCode": cc,
            "Plant": plant,
            "PlantName": name,
            "OrdersSettled": n,
            "OrdersReleasedNotTECO": rng.choice([0, 0, 0, 1, 2]),
            "TotalVariance": f"{var:.2f}",
            "Currency": CURRENCY[cc],
            "LargestOrder": f"{plant[0]}{rng.randint(10000000, 19999999)}",
            "LargestOrderVariance": f"{big:.2f}",
            "Comment": "",
        }
        row.update(VAR_STORY.get((plant, period), {}))
        rows.append(row)
    return rows


# --- Bank statement (BAI2), company code 1000 operating account -------------------------------------------

BANK_CUSTOMERS = [
    "GULF COAST REFINING", "MIDLAND WATER AUTH", "NORTHSTAR CHEMICAL", "CASCADE PAPER MILLS", "PRAIRIE ETHANOL",
    "BLUE RIVER UTILITIES", "SUMMIT MINING CO", "HARBOR CITY MUNICIPAL", "IRONWOOD POWER", "LAKEVIEW DAIRY COOP",
]  # fmt: skip
BANK_VENDORS = [
    "MIDWEST STEEL SERVICE", "KEYSTONE CASTINGS", "LAKESHORE PACKAGING", "OHIO VALLEY IND GAS", "PRECISION SEAL CO",
    "BUCKEYE ELECTRIC MOTORS", "GREAT LAKES FREIGHT", "SUMMIT BEARINGS", "ALLIED FASTENER SUPPLY",
    "CRESTLINE ENGINEERING", "NORTHFIELD TEMP STAFF",
]  # fmt: skip


def bank_transactions(period: str) -> tuple[D, list[tuple[str, D, str, str]]]:
    rng = random.Random(f"bank-{period}")
    opening = D(rng.randint(18_000_000, 26_000_000)) / 100 * 10
    tx: list[tuple[str, D, str, str]] = []
    for _ in range(rng.randint(70, 95)):
        roll = rng.random()
        ref = f"{rng.randint(100000000, 999999999)}"
        if roll < 0.40:
            tx.append(
                (
                    "165",
                    D(rng.randint(500_000, 45_000_000)) / 100,
                    ref,
                    f"ACH CREDIT {rng.choice(BANK_CUSTOMERS)} REMIT",
                )
            )
        elif roll < 0.48:
            tx.append(
                ("195", D(rng.randint(2_000_000, 90_000_000)) / 100, ref, f"WIRE IN {rng.choice(BANK_CUSTOMERS)}")
            )
        elif roll < 0.85:
            tx.append(
                (
                    "455",
                    D(rng.randint(300_000, 30_000_000)) / 100,
                    ref,
                    f"ACH DEBIT {rng.choice(BANK_VENDORS)} PAYMENT RUN F110",
                )
            )
        elif roll < 0.95:
            tx.append(("475", D(rng.randint(50_000, 4_000_000)) / 100, ref, f"CHECK PAID {rng.randint(40000, 49999)}"))
        else:
            tx.append(("495", D(rng.randint(5_000_000, 60_000_000)) / 100, ref, "WIRE OUT PAYROLL FUNDING ADP"))
    tx.append(
        (
            "698",
            D(rng.randint(150_000, 210_000)) / 100,
            f"{rng.randint(100000000, 999999999)}",
            "ANALYSIS SERVICE CHARGE",
        )
    )
    if period == "2026-03":
        # A duplicate vendor payment, visible only in the bank file and recovered in April.
        tx.append(("455", D("38940.00"), "558201447", "ACH DEBIT KEYSTONE CASTINGS PAYMENT RUN F110 INV 77120"))
        tx.append(("455", D("38940.00"), "558201519", "ACH DEBIT KEYSTONE CASTINGS PAYMENT RUN F110 INV 77120"))
    if period == "2026-04":
        tx.append(("165", D("38940.00"), "604418822", "ACH CREDIT KEYSTONE CASTINGS REFUND DUP PMT INV 77120"))
    return opening, tx


# --- Background job logs (SM37) -----------------------------------------------------------------------------


def job_log_dayton_aug() -> str:
    return """Job log overview: job ZPP_PERIODEND_1200 (scheduled, user BATCH_PP)
Date       Time     Message text                                                         Msg class  No.
09/01/2026 06:10:02 Job started                                                          00         516
09/01/2026 06:10:02 Step 001 started (program RKO7CO88, variant ZSETTLE_1200, user BATCH_PP)  00   550
09/01/2026 06:10:44 Settlement period 008/2026, plant 1200: 212 orders selected               KD   701
09/01/2026 06:11:58 212 orders processed, 0 settled: no WIP or variance determined for period  KD   702
09/01/2026 06:11:58 Step 002 started (program SAPKKA12, variant ZWIP_1200, user BATCH_PP)     00   550
09/01/2026 06:14:31 WIP calculated for 212 orders                                             KA   410
09/01/2026 06:14:31 Step 003 started (program SAPKKS2, variant ZVAR_1200, user BATCH_PP)      00   550
09/01/2026 06:19:07 Variances calculated for 198 orders                                       KV   220
09/01/2026 06:19:07 Job finished                                                              00   517
"""


def job_log_dayton_aug_rerun() -> str:
    return """Job log overview: job ZPP_SETTLE_1200_RERUN (immediate, user SOKAFOR)
Date       Time     Message text                                                         Msg class  No.
09/02/2026 08:41:15 Job started                                                          00         516
09/02/2026 08:41:15 Step 001 started (program RKO7CO88, variant ZSETTLE_1200, user SOKAFOR)   00   550
09/02/2026 08:43:02 Settlement period 008/2026, plant 1200: 212 orders selected               KD   701
09/02/2026 08:44:40 212 orders processed, 212 settled (WIP and variances from 09/01 run)      KD   702
09/02/2026 08:44:40 Job finished                                                              00   517
"""


def job_log_kc_apr() -> str:
    return """Job log overview: job ZPP_TECO_1700 (immediate, user DHOLM)
Date       Time     Message text                                                         Msg class  No.
05/01/2026 07:02:10 Job started                                                          00         516
05/01/2026 07:02:10 Step 001 started (program COHV mass processing, function TECO, plant 1700) 00  550
05/01/2026 07:09:55 174 orders selected with status REL, delivered quantity reached           CO   120
05/01/2026 07:16:31 174 orders set to TECO                                                   CO   121
05/01/2026 07:16:31 Job finished                                                              00   517
"""
