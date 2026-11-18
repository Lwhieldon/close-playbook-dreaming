"""The six closes before May 2026: November 2025 through April 2026, including the 2025 year end.

Story threads that start here:
- Rules in force: IC cutoff BD4 noon ET, trial balance BD6, rate type M. The manual accrual threshold was
  $2,500 per vendor in 2025 and became $5,000 with the January 2026 close (2026 close calendar memo).
- Year end 2025: physical inventory counts at every plant on 12/31. Houston (1400) found a 186,420.55 USD
  shortage on V-2200 valve bodies: scrap at the valve body line was not reaching the ERP after the new MES
  interface went live in October 2025. Fixed 01/22/2026 (interface mapping); Q1 cycle counts were clean.
- Audit: Hartwell & Crane LLP proposed one adjustment, an unrecorded liability (Keystone Castings invoice
  77031, 64,300.00 USD, for December receipts, received 01/14/2026), posted in special period 13 of 2025
  as document 100038915. Lesson: search January invoices for December receipts before the year-end close.
- Kansas City (1700): production orders left released (REL) instead of technically completed (TECO), so
  variance calculation (KKS2) skipped them from January to March; fixed in the April close with a mass
  TECO and a 142,880.40 USD unfavorable catch-up; TECO added to the plant's checklist.
- Erie (1900): production stopped 03/31/2026; stock moved to Toledo; out of the close checks from April.
- A duplicate Keystone Castings payment (38,940.00) in March, found from the bank statement, refunded in
  April.
All content is fictional.
"""

from __future__ import annotations

DANA = "Dana Whitfield"
SAM = "Sam Okafor"
LUIS = "Luis Ortega"
ANA = "Ana Ruiz"
JONAS = "Jonas Becker"
ELENA = "Elena Park"
KIM = "Kim Alvarez"
JORDAN = "Jordan Ellis"
GRACE = "Grace Liu"  # Houston plant controller
DEREK = "Derek Holm"  # Kansas City plant controller
PAUL = "Paul Kowalski"  # Erie plant controller
OWEN = "Owen Bradley"  # Tulsa
NIA = "Nia Robinson"  # Charlotte
HANNAH = "Hannah Sato"  # Reno
MEGAN = "Megan Ross"  # audit senior, Hartwell & Crane LLP

EARLY_MEETINGS = [
    (
        "nov25-kickoff",
        "Close Kickoff - November 2025 Close - 2025-12-01.vtt",
        "2025-12-01",
        [DANA, LUIS, SAM, ANA, JONAS, JORDAN, GRACE],
        [
            (
                DANA,
                "Morning everyone, November close. Usual rules: IC cutoff is BD4 at noon Eastern, that's Thursday "
                "the 4th. Manual accruals at twenty-five hundred per vendor. Consolidated TB on BD6, Monday the 8th.",
            ),
            (DANA, "FX revaluation BD3 with rate type M, all three company codes."),
            (
                DANA,
                "And a heads up: year-end instructions go out mid-December. Physical counts at every plant on the "
                "31st, and the auditors are in the second half of January.",
            ),
            (LUIS, "IC rec as usual. Stuttgart's fee is already in, Monterrey's tooling invoice comes this week."),
            (
                GRACE,
                "Houston: our new MES went live in October for the valve body line. Production confirmations come "
                "over automatically now. Still getting used to it.",
            ),
            (SAM, "Toledo and Dayton are running the period-end jobs by hand as usual."),
        ],
    ),
    (
        "nov25-review",
        "Close Review - November 2025 Close - 2025-12-08.vtt",
        "2025-12-08",
        [DANA, LUIS, SAM, ANA, JONAS, JORDAN],
        [
            (LUIS, "IC matched for November. Fee at rate type M on both sides, tooling in period eleven."),
            (DANA, "Accruals: six vendors at or above twenty-five hundred, about forty-one thousand. Approved."),
            (ANA, "Monterrey closed on time."),
            (JONAS, "Stuttgart too. FX revaluation was a small gain."),
        ],
    ),
    (
        "dec25-kickoff",
        "Year-End Close Kickoff - December 2025 Close - 2026-01-02.vtt",
        "2026-01-02",
        [DANA, LUIS, SAM, ANA, JONAS, JORDAN, ELENA, GRACE, DEREK, PAUL],
        [
            (
                DANA,
                "Happy new year. This is the year-end close, so the year-end instructions apply on top of the "
                "usual calendar. IC cutoff BD4 noon, that's Wednesday the 7th. TB on BD6, Friday the 9th.",
            ),
            (
                DANA,
                "Accruals are still twenty-five hundred for December. The new calendar memo for 2026 raises it, "
                "but that starts with the January close, not this one.",
            ),
            (
                JORDAN,
                "AP is holding the unrecorded liabilities search open through January 20th, per the instructions. "
                "Any invoice dated after year end for December receipts gets flagged.",
            ),
            (DANA, "Counts: every plant counted on the 31st. Plant controllers, results to Sam by Monday."),
            (PAUL, "Erie counted, no surprises."),
            (DEREK, "Kansas City counted. Fine."),
            (GRACE, "Houston is still reconciling the count. I'll have it Monday, but it doesn't look small."),
        ],
    ),
    (
        "dec25-count",
        "Year-End Physical Inventory Results - 2026-01-06.vtt",
        "2026-01-06",
        [DANA, SAM, GRACE, KIM, OWEN, NIA, HANNAH],
        [
            (SAM, "Count results. Eighteen plants within tolerance. Houston is the exception."),
            (
                GRACE,
                "Houston came in about a hundred eighty-six thousand short, almost all valve bodies in the V "
                "twenty-two hundred series. The bins are just emptier than the system says.",
            ),
            (DANA, "Theft? Miscount?"),
            (
                GRACE,
                "Neither, we think. We recounted. The valve body line scraps a lot of castings, and since the MES "
                "went live in October the scrap quantity isn't coming across with the confirmations. The good "
                "quantity posts, the scrap doesn't, so the system still thinks we have those castings.",
            ),
            (SAM, "That fits. Houston's material usage variance went quiet in November and December."),
            (
                DANA,
                "Post the count difference this period. And I want the interface fixed before the January close. "
                "Grace, own it with IT.",
            ),
            (GRACE, "Will do. IT thinks it's a field mapping. They're aiming for the 22nd."),
        ],
    ),
    (
        "dec25-review",
        "Year-End Close Review - December 2025 Close - 2026-01-09.vtt",
        "2026-01-09",
        [DANA, LUIS, SAM, ANA, JONAS, JORDAN, ELENA, GRACE],
        [
            (SAM, "Houston count difference is posted, the MI07 document. One eighty-six four twenty."),
            (LUIS, "IC matched for December. Management fee and tooling both in period twelve."),
            (DANA, "Accruals: nine vendors at or above twenty-five hundred, approved."),
            (ELENA, "Year-end FX revaluation done with rate type M, posted on BD3."),
            (
                DANA,
                "Auditors start on the 19th. Keep special period thirteen open for any audit adjustments. Nothing "
                "posts to period thirteen without my approval.",
            ),
        ],
    ),
    (
        "jan26-kickoff",
        "Close Kickoff - January 2026 Close - 2026-02-02.vtt",
        "2026-02-02",
        [DANA, LUIS, SAM, ANA, JONAS, JORDAN, GRACE, DEREK],
        [
            (
                DANA,
                "January close, the first under the 2026 calendar memo. One change: the manual accrual threshold "
                "is now five thousand per vendor, up from twenty-five hundred. Everything else stays: IC cutoff BD4 "
                "noon, Thursday the 5th. TB BD6, Monday the 9th.",
            ),
            (
                DANA,
                "Audit wrap-up: Hartwell and Crane proposed one adjustment. A Keystone Castings invoice for "
                "December receipts, about sixty-four thousand, came in on January 14th and wasn't accrued. We "
                "booked it in period thirteen. It's the only adjustment, but it's the kind of thing we should "
                "catch ourselves.",
            ),
            (JORDAN, "For next year: search January invoices for December receipts before we close December."),
            (GRACE, "Houston: IT fixed the MES scrap mapping on the 22nd. Scrap is posting with confirmations now."),
            (
                DEREK,
                "Kansas City: WIP is up this month. Our skids take a while, lots of orders still open. Probably "
                "timing.",
            ),
        ],
    ),
    (
        "jan26-review",
        "Close Review - January 2026 Close - 2026-02-09.vtt",
        "2026-02-09",
        [DANA, LUIS, SAM, ANA, JONAS, DEREK],
        [
            (DANA, "Accruals at the new five thousand threshold: four vendors. Approved."),
            (LUIS, "IC matched."),
            (SAM, "Kansas City variances are oddly small. Next to nothing for a plant that size."),
            (DEREK, "Good month, I guess."),
        ],
    ),
    (
        "feb26-kickoff",
        "Close Kickoff - February 2026 Close - 2026-03-02.vtt",
        "2026-03-02",
        [DANA, LUIS, SAM, ANA, JONAS, JORDAN, DEREK, PAUL],
        [
            (DANA, "February close. IC cutoff BD4 noon, Thursday the 5th. TB Monday the 9th. Accruals at five thousand."),
            (
                DANA,
                "Erie: we announced last week that Erie stops production at the end of March. Paul, you'll move "
                "the stock to Toledo. The memo with the close procedures goes out mid-March.",
            ),
            (PAUL, "We'll run the stock transport orders the last week of March."),
            (DEREK, "Kansas City WIP is up again. A hundred eighteen open orders."),
        ],
    ),
    (
        "feb26-review",
        "Close Review - February 2026 Close - 2026-03-09.vtt",
        "2026-03-09",
        [DANA, LUIS, SAM, ANA, JONAS, DEREK],
        [
            (LUIS, "IC matched for February."),
            (
                SAM,
                "Kansas City again: variance is basically zero two months running and WIP keeps climbing. "
                "Something's off. Derek, can you send me the order status list?",
            ),
            (DEREK, "Sure, I'll send it today."),
            (DANA, "Accruals: three vendors at or above five thousand. Approved."),
        ],
    ),
    (
        "mar26-kickoff",
        "Close Kickoff - March 2026 Close - 2026-04-01.vtt",
        "2026-04-01",
        [DANA, LUIS, SAM, ANA, JONAS, JORDAN, DEREK, PAUL],
        [
            (DANA, "March close, quarter end. IC cutoff BD4 noon, that's Monday the 6th. TB on BD6, Wednesday the 8th."),
            (PAUL, "Erie stopped production yesterday. All stock is in Toledo. Only fixed assets left."),
            (
                SAM,
                "Kansas City: I found it. Their orders are delivered but never set to technically complete, so "
                "variance calculation skips them. They just sit in WIP. A hundred seventy-four orders now.",
            ),
            (DEREK, "We never had a TECO step. The old system closed orders on its own."),
            (
                DANA,
                "Fix it in the April close, not mid-quarter. Mass TECO before the WIP run, and put TECO on the "
                "Kansas City checklist from now on. Expect a catch-up variance.",
            ),
        ],
    ),
    (
        "mar26-review",
        "Close Review - March 2026 Close - 2026-04-08.vtt",
        "2026-04-08",
        [DANA, LUIS, SAM, ANA, JONAS, JORDAN, GRACE],
        [
            (GRACE, "Houston Q1 cycle counts are within tolerance. The scrap fix is holding."),
            (
                JORDAN,
                "Cash found something. Keystone Castings got paid twice for invoice 77120, thirty-eight thousand "
                "nine forty, in two payment runs on the same day. We've asked for a refund.",
            ),
            (DANA, "Block the vendor for duplicates until the refund is in. And I want the payment run check fixed."),
            (LUIS, "IC matched for March."),
        ],
    ),
    (
        "apr26-kickoff",
        "Close Kickoff - April 2026 Close - 2026-05-01.vtt",
        "2026-05-01",
        [DANA, LUIS, SAM, ANA, JONAS, JORDAN, DEREK],
        [
            (
                DANA,
                "April close. IC cutoff BD4 noon, Wednesday the 6th. TB BD6, Friday the 8th. Accruals at five "
                "thousand. Plants in scope for 1000 from this close: Toledo, Dayton, Houston, Tulsa, Charlotte, "
                "Kansas City and Reno. Erie is out, it's only asset disposals now.",
            ),
            (DEREK, "Kansas City ran the mass TECO this morning before WIP. A hundred seventy-four orders."),
            (SAM, "Then variances will catch up this month. I'll tell you the number at the review."),
            (JORDAN, "Keystone refund came in. Vendor unblocked."),
        ],
    ),
    (
        "apr26-review",
        "Close Review - April 2026 Close - 2026-05-08.vtt",
        "2026-05-08",
        [DANA, LUIS, SAM, ANA, JONAS, DEREK],
        [
            (
                SAM,
                "Kansas City catch-up variance: about one hundred forty-three thousand unfavorable, that's January "
                "through March landing at once. It's in the April numbers.",
            ),
            (DANA, "Fine, it's a one-time catch-up. Derek, TECO stays on your checklist every month."),
            (DEREK, "It's on there."),
            (LUIS, "IC matched for April. Heads up, Stuttgart has a new transfer pricing agreement from May."),
            (DANA, "Accruals: three vendors at or above five thousand. Approved."),
        ],
    ),
]

EARLY_POLICIES = [
    (
        "memo-year-end-2025",
        "Year-End Close Instructions 2025 - Controller Memo - 2025-12-15.pdf",
        "2025-12-15",
        """TARNWELL INDUSTRIES - CORPORATE CONTROLLER
MEMO: Year-end close instructions, fiscal year 2025
From: Dana Whitfield, Corporate Controller
To: Close team, plant controllers
Date: December 15, 2025

1. Physical inventory. Every plant counts on December 31, 2025. Count results to costing (Sam Okafor) by
   January 5. Post count differences in period 12 (transaction MI07) after review.

2. Calendar. The year-end close follows the normal calendar: IC cutoff BD4 at 12:00 noon ET; consolidated
   trial balance on BD6.

3. Manual accruals. Threshold $2,500 per vendor per month for the December close.

4. Unrecorded liabilities. Accounts payable keeps the search open through January 20, 2026: any invoice
   received after year end for goods or services received on or before December 31 is accrued in 2025.

5. Audit. Hartwell & Crane LLP fieldwork starts January 19, 2026. Audit adjustments post in special
   period 13 of 2025, only with controller approval.

6. FX revaluation. Rate type M, key date December 31, 2025, all company codes.
""",
    ),
    (
        "memo-close-calendar-2026-01",
        "2026 Close Calendar - Controller Memo - 2026-01-12.pdf",
        "2026-01-12",
        """TARNWELL INDUSTRIES - CORPORATE CONTROLLER
MEMO: 2026 close calendar and manual accrual threshold
From: Dana Whitfield, Corporate Controller
To: Close team
Date: January 12, 2026
Effective: starting with the January 2026 close (period 01)

1. Close target. The consolidated trial balance is due on BD6.

2. Intercompany cutoff. BD4 at 12:00 noon Eastern Time.

3. Manual accruals. The manual accrual threshold is $5,000 per vendor per month. (Previously $2,500.)

4. Approvals. Any journal entry over $250,000 requires CFO approval (Rahul Mehta) before posting. MR11
   GR/IR write-offs and manual accruals require controller approval regardless of amount.

5. FX revaluation. Rate type M, key date the last calendar day of the month.
""",
    ),
    (
        "memo-erie-2026-03",
        "Erie Plant Production Wind-Down - Close Procedures - 2026-03-16.pdf",
        "2026-03-16",
        """TARNWELL INDUSTRIES - CORPORATE CONTROLLER
MEMO: Erie plant (1900) production wind-down - close procedures
From: Dana Whitfield, Corporate Controller
To: Close team, Paul Kowalski (Erie), Sam Okafor (Toledo)
Date: March 16, 2026

1. Erie (plant 1900) stops production on March 31, 2026.

2. All stock moves to Toledo (plant 1100) by stock transport orders between March 24 and March 31.
   Toledo receives at standard cost; no revaluation.

3. Open production orders at Erie are completed and settled in the March close. No new orders after
   March 31.

4. From the April 2026 close, Erie is out of the production and inventory close checks. Fixed assets
   remain under company code 1000 until disposal; fixed assets owns the disposal accounting.
""",
    ),
]


def key_jes(je) -> dict[str, list]:
    """Key journal entries for the early periods, built with corpus_erp.je."""
    return {
        "2025-11": [
            je(
                "1000",
                "100035120",
                "SA",
                "11/30/2025",
                "12/04/2025",
                "15:12:40",
                "JELLIS",
                "Posted",
                "Nov manual accruals >= $2,500 per vendor, approved D. Whitfield",
                [
                    ("211000", -41380, "Nov manual accruals"),
                    ("640000", 6150, "Summit Bearings 300620"),
                    ("640000", 3920, "Precision Seal 300388"),
                    ("505000", 18740, "Great Lakes Freight 300519"),
                    ("630000", 2890, "Ohio Valley Industrial Gas 300301"),
                    ("500000", 7180, "Midwest Steel Service 300112"),
                    ("600000", 2500, "Northfield Temp Staffing 300871"),
                ],
                posted_by="DWHITFIELD",
                posted_on="12/04/2025",
            ),
        ],
        "2025-12": [
            je(
                "1000",
                "4900079915",
                "WI",
                "12/31/2025",
                "01/06/2026",
                "16:44:09",
                "SOKAFOR",
                "Posted",
                "Physical inventory 12/31/2025 count difference plant 1400 (MI07)",
                [
                    ("130000", -186420.55, "Count difference V-2200 valve bodies, plant 1400"),
                    ("525000", 186420.55, "Inventory differences - physical count"),
                ],
                posted_by="SOKAFOR",
                posted_on="01/06/2026",
            ),
            je(
                "1000",
                "100036840",
                "SA",
                "12/31/2025",
                "01/07/2026",
                "17:20:31",
                "JELLIS",
                "Posted",
                "Dec manual accruals >= $2,500 per vendor (year end), approved D. Whitfield",
                [
                    ("211000", -52610, "Dec manual accruals"),
                    ("505000", 21300, "Great Lakes Freight 300519"),
                    ("640000", 6150, "Summit Bearings 300620"),
                    ("500000", 9870, "Midwest Steel Service 300112"),
                    ("630000", 3140, "Ohio Valley Industrial Gas 300301"),
                    ("640000", 4410, "Precision Seal 300388"),
                    ("600000", 2980, "Northfield Temp Staffing 300871"),
                    ("650000", 2610, "Lakeshore Packaging 300233"),
                    ("660000", 2150, "Buckeye Electric Motors 300402"),
                ],
                posted_by="DWHITFIELD",
                posted_on="01/07/2026",
            ),
        ],
        "2026-01": [
            je(
                "1000",
                "100038120",
                "SA",
                "01/31/2026",
                "02/05/2026",
                "16:02:18",
                "JELLIS",
                "Posted",
                "Jan manual accruals >= $5,000 per vendor (new threshold per 2026 calendar memo)",
                [
                    ("211000", -45760, "Jan manual accruals"),
                    ("505000", 22410, "Great Lakes Freight 300519"),
                    ("640000", 6150, "Summit Bearings 300620"),
                    ("500000", 11420, "Midwest Steel Service 300112"),
                    ("600000", 5780, "Northfield Temp Staffing 300871"),
                ],
                posted_by="DWHITFIELD",
                posted_on="02/05/2026",
            ),
        ],
        "2026-03": [
            je(
                "1000",
                "100040215",
                "SA",
                "03/31/2026",
                "04/06/2026",
                "11:31:52",
                "JELLIS",
                "Posted",
                "Keystone Castings duplicate payment inv 77120 - receivable from vendor",
                [("128000", 38940, "Duplicate payment 03/18 F110, refund requested"), ("200000", -38940, "Keystone 300198")],
            ),
        ],
        "2026-04": [
            je(
                "1000",
                "100040988",
                "SA",
                "04/30/2026",
                "05/05/2026",
                "10:15:07",
                "JELLIS",
                "Posted",
                "Keystone Castings refund received 04/22 - clear vendor receivable",
                [("113100", 38940, "Refund dup pmt inv 77120"), ("128000", -38940, "Clear receivable")],
            ),
        ],
    }


# Special period 13 (2025): audit adjustments, exported on their own sheet of the January 2026 register.
def period13_jes(je) -> list:
    return [
        je(
            "1000",
            "100038915",
            "SA",
            "12/31/2025",
            "01/23/2026",
            "14:08:44",
            "JELLIS",
            "Posted",
            "AJE 1 Hartwell & Crane: unrecorded liability Keystone Castings inv 77031 (Dec receipts), period 13",
            [("500000", 64300, "Keystone Castings 300198 inv 77031 rec'd 01/14/2026"), ("211000", -64300, "Accrued AP")],
            posted_by="DWHITFIELD",
            posted_on="01/23/2026",
        ),
    ]


RECON_KEY = {
    "2025-12": [
        (
            "1000",
            "130000",
            "Raw materials inventory",
            "SOKAFOR",
            "Reconciled",
            "0.00",
            "Year-end counts posted. Plant 1400 count difference -186,420.55 (MI07 4900079915): MES interface not "
            "sending scrap since Oct go-live. G. Liu/IT to fix mapping before Jan close.",
        ),
    ],
    "2026-01": [
        (
            "1000",
            "211000",
            "Accrued liabilities",
            "JELLIS",
            "Reconciled",
            "0.00",
            "Includes AJE 1 (100038915, period 13 of 2025): Keystone inv 77031 64,300.00 unrecorded at year end. "
            "Reversed in P01 when invoice posted.",
        ),
    ],
    "2026-03": [
        (
            "1000",
            "128000",
            "Other receivables",
            "JELLIS",
            "Reconciled",
            "38,940.00",
            "Keystone Castings duplicate payment inv 77120 (two F110 runs 03/18). Refund requested 04/02.",
        ),
    ],
    "2026-04": [
        (
            "1000",
            "131000",
            "Work in process",
            "SOKAFOR",
            "Reconciled",
            "0.00",
            "Plant 1700: mass TECO 05/01 (174 orders) released Jan-Mar WIP to variance, catch-up 142,880.40 unfav. "
            "TECO added to KC checklist.",
        ),
        (
            "1000",
            "128000",
            "Other receivables",
            "JELLIS",
            "Reconciled",
            "0.00",
            "Keystone refund 38,940.00 received 04/22 (100040988).",
        ),
    ],
}

# Monthly management fee (2000 -> 1000, EUR 212,400) and tooling services (3000 -> 1000), all matched.
ICR = {
    "2025-11": [("1900019881", "1800003720", "IC-2000-1125", "222870.12"), ("1900019904", "3400014211", "IC-3000-1125", "68114.40")],
    "2025-12": [("1900020310", "1800003802", "IC-2000-1225", "224632.32"), ("1900020322", "3400014690", "IC-3000-1225", "72460.18")],
    "2026-01": [("1900020744", "1800003871", "IC-2000-0126", "225929.88"), ("1900020761", "3400015102", "IC-3000-0126", "66908.75")],
    "2026-02": [("1900021120", "1800003944", "IC-2000-0226", "226546.36"), ("1900021138", "3400015577", "IC-3000-0226", "69771.02")],
    "2026-03": [("1900021402", "1800004011", "IC-2000-0326", "227226.04"), ("1900021431", "3400016040", "IC-3000-0326", "71340.66")],
    "2026-04": [("1900021650", "1800004066", "IC-2000-0426", "227799.52"), ("1900021677", "3400016433", "IC-3000-0426", "70022.91")],
}  # fmt: skip

CHANGES = {
    "2026-01": [
        (
            "INTERFACE",
            "MES_CONF_1400 (MES confirmations to PP, plant 1400)",
            "Field mapping SCRAP_QTY",
            "(unmapped)",
            "AFRU-XMNGA (confirmed scrap)",
            "ITBASIS02",
            "01/22/2026",
            "18:05:41",
            "CST",
            "SM59/ZMES",
        ),
    ],
    "2026-03": [
        (
            "T001W",
            "1900 Erie",
            "Plant status",
            "Active",
            "Production stopped 03/31/2026 (no new orders)",
            "RKIM",
            "03/31/2026",
            "17:40:22",
            "EST",
            "OX10",
        ),
        (
            "LFA1",
            "300198 Keystone Castings",
            "Payment block",
            "",
            "R (duplicate payment, refund pending)",
            "APATEL",
            "04/02/2026",
            "09:30:15",
            "EST",
            "XK02",
        ),
    ],
    "2026-04": [
        (
            "LFA1",
            "300198 Keystone Castings",
            "Payment block",
            "R (duplicate payment, refund pending)",
            "",
            "APATEL",
            "04/23/2026",
            "08:52:40",
            "EST",
            "XK02",
        ),
        (
            "CHECKLIST",
            "Close checklist plant 1700",
            "Task added",
            "",
            "Mass TECO (COHV) before WIP run, every period",
            "DHOLM",
            "05/01/2026",
            "07:30:12",
            "CST",
            "ZCLOSE",
        ),
    ],
}
