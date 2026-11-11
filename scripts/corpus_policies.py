"""Policy memos for the synthetic close corpus. These are the authoritative rule texts; meetings and
sessions paraphrase them. Note what they leave out: the treasury memo says nothing about weekend month
ends, which is how the October ZCLS run failed. All content is fictional."""

POLICIES = [
    (
        "memo-close-calendar-2026-07",
        "Close Calendar and Cutoffs - Controller Memo - 2026-07-15.txt",
        "2026-07-15",
        """TARNWELL INDUSTRIES - CORPORATE CONTROLLER
MEMO: Month-end close calendar, cutoffs and accrual threshold
From: Dana Whitfield, Corporate Controller
To: Close team
Date: July 15, 2026
Effective: starting with the July 2026 close (period 07)

Following the close policy review on July 15, 2026, these rules apply starting with the July 2026 close:

1. Business days. Business day 1 (BD1) is the first working day after month end. US federal holidays are
   not business days.

2. Close target. The consolidated trial balance is due on BD5. (Previously BD6.)

3. Intercompany cutoff. BD3 at 12:00 noon Eastern Time. (Previously BD4 at 12:00 noon ET.) Intercompany
   invoices received after the cutoff roll to the next period and are carried as reconciling items.

4. Manual accruals. The manual accrual threshold is $10,000 per vendor per month. (Previously $5,000.)
   Below the threshold, do not book a manual accrual; the invoice is expensed when received.

5. Approvals. Any journal entry over $250,000 requires CFO approval (Rahul Mehta) before posting. MR11
   GR/IR write-offs and manual accruals require controller approval regardless of amount.

6. Posting periods. Company codes 2000 and 3000 close their posting period in OB52 at local BD3 18:00.
   Company code 1000 closes after consolidation on BD5.

Open item: whether to move the close target to BD4. No decision; we will revisit once intercompany is faster.
""",
    ),
    (
        "memo-owners-2026-07",
        "Close Owners and FX Procedure - 2026-07-22.txt",
        "2026-07-22",
        """TARNWELL INDUSTRIES - CLOSE OWNERS AND FX PROCEDURE
Date: July 22, 2026
Effective: starting with the July 2026 close

Owners
- Intercompany reconciliation: Priya Nair (from Luis Ortega, who moves to FP&A)
- Costing, Toledo (1100) and Dayton (1200): Sam Okafor
- Company code 3000 (Monterrey): Marco Reyes (from Ana Ruiz)
- Company code 2000 (Stuttgart): Jonas Becker
- Treasury exchange rates: Treasury team, Elena Park
- Approvals: CFO Rahul Mehta (JEs over $250,000); Corporate Controller Dana Whitfield (manual accruals,
  MR11 write-offs)

FX revaluation
- Transaction FAGL_FCV in company codes 1000, 2000 and 3000 on BD3.
- Valuation area US_GAAP. Exchange rate type M.
- Key date: last calendar day of the month. Postings to 541000 reverse on day 1 of the next period.
- Run a test run first; post after review.
""",
    ),
    (
        "memo-fin-pol-014",
        "FIN-POL-014 Manual Accrual Threshold - 2026-09-25.txt",
        "2026-09-25",
        """TARNWELL INDUSTRIES - FINANCE POLICY
FIN-POL-014  Manual Accruals
Version 2.0   Issued: September 25, 2026   Effective: September 2026 close (period 09) onward
Owner: Corporate Controller

1. Threshold. Manual accruals are booked for goods or services received but not invoiced when the
   estimated amount is $25,000 or more per vendor per month. This replaces the $10,000 threshold in the
   controller memo of July 15, 2026.
2. Below threshold. Amounts under $25,000 per vendor are not accrued; the invoice is expensed when received.
3. Support. Each accrual line references the open PO and goods receipts (manual accrual worklist).
4. Approval. All manual accruals require Corporate Controller approval before posting, regardless of amount.
5. Reversal. Manual accruals reverse on day 1 of the following period.
""",
    ),
    (
        "memo-ic-cutoff-2026-09",
        "IC Cutoff Change Notice - 2026-09-30.txt",
        "2026-09-30",
        """TARNWELL INDUSTRIES - NOTICE TO ALL COMPANY CODES
Subject: Intercompany cutoff moves to BD2
Date: September 30, 2026
From: Dana Whitfield, Corporate Controller

As agreed at the close retrospective on September 29, 2026, starting with the October 2026 close (period 10)
the intercompany cutoff is BD2 at 5:00 pm Eastern Time. (Previously BD3 at 12:00 noon ET; the September
2026 close still uses BD3 noon.)

Intercompany invoices must be posted, not parked, by the cutoff to count in the closing period. Documents
posted after the cutoff roll to the next period and are carried as reconciling items.

Company codes outside the US: convert the cutoff to local time each month. The offset changes when daylight
saving time starts or ends, and the US and Europe change on different dates.
""",
    ),
    (
        "memo-trs-2026-07",
        "TRS-2026-07 FX Valuation Rate Type - 2026-10-20.txt",
        "2026-10-20",
        """TARNWELL INDUSTRIES - TREASURY
TRS-2026-07  Exchange rate type for month-end FX valuation
Issued: October 20, 2026   Effective: October 2026 close (period 10) onward
Contact: Elena Park, Treasury

1. From the October 2026 close, month-end FX valuation (FAGL_FCV) in company codes 1000, 2000 and 3000
   uses exchange rate type ZCLS instead of M.
2. ZCLS is Treasury's closing spot rate, loaded at 4:00 pm London time on the last calendar day of the
   month.
3. Valuation area US_GAAP, key date the last calendar day of the month, and reversal on day 1 of the next
   period are unchanged.
""",
    ),
]
