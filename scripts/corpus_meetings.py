"""Meeting transcripts for the synthetic close corpus (Teams-style WebVTT, speaker-tagged).

Each meeting is the story content; build_corpus.py pads it with the routine talk real meetings are full
of (status round-robins, "can you see my screen", side topics) and renders cue timestamps. People in a
meeting say less than the system shows: document numbers, exact amounts and timestamps mostly live in the
ERP exports, and sometimes what someone says is wrong. All people and data are fictional.
"""

from __future__ import annotations

DANA = "Dana Whitfield"  # corporate controller
SAM = "Sam Okafor"  # costing, Toledo and Dayton
PRIYA = "Priya Nair"  # IC reconciliation from the July close
LUIS = "Luis Ortega"  # IC reconciliation through the June close
MARCO = "Marco Reyes"  # Monterrey (3000) from July
ANA = "Ana Ruiz"  # Monterrey (3000) through June
JONAS = "Jonas Becker"  # Stuttgart (2000)
ELENA = "Elena Park"  # treasury
TESSA = "Tessa Lund"  # Greenville plant accountant (October)
KIM = "Kim Alvarez"  # purchasing
JORDAN = "Jordan Ellis"  # accounts payable

# (key, filename, date, attendees, lines). Lines are (speaker, text).
MEETINGS = [
    (
        "may-kickoff",
        "Close Kickoff - May 2026 Close - 2026-06-01.vtt",
        "2026-06-01",
        [DANA, LUIS, SAM, ANA, JONAS, JORDAN],
        [
            (
                DANA,
                "Okay, let's kick off the May close. Same rules as always: IC cutoff is BD4 at noon Eastern, "
                "that's Thursday the 4th. Manual accruals at five thousand per vendor. Consolidated TB on BD6, "
                "which is Monday the 8th.",
            ),
            (DANA, "FX revaluation on BD3, rate type M, all three company codes."),
            (LUIS, "IC rec is on me as usual. I'll send the open matching report Wednesday."),
            (
                SAM,
                "Dayton: I ran WIP, variance and settlement by hand this morning, in that order. Settlement threw "
                "an error on one order, a new one for P-7801, no settlement rule. I added it in KO02 and reran. "
                "All four orders are settled.",
            ),
            (DANA, "Is that going to keep happening with new materials?"),
            (SAM, "Only if the order type doesn't default the settlement profile. I've asked master data to look."),
            (
                JORDAN,
                "One from AP: a Great Lakes Freight invoice got keyed against Dayton instead of Toledo. "
                "Twelve thousand six hundred and forty. We're reversing and reposting it to 1100 today.",
            ),
            (SAM, "That explains why Dayton GR/IR was off. Thanks Jordan."),
            (ANA, "Monterrey is on track. IC invoices for May are already posted in period five."),
        ],
    ),
    (
        "may-review",
        "Close Review - May 2026 Close - 2026-06-08.vtt",
        "2026-06-08",
        [DANA, LUIS, SAM, ANA, JONAS],
        [
            (
                LUIS,
                "One IC item. The management fee from Stuttgart didn't match. 1000 converted it at the "
                "transfer pricing rate from the agreement, 2000 used rate type M on the invoice date. "
                "It's about eight hundred dollars.",
            ),
            (
                DANA,
                "Let's settle that for good. For IC management fees, both sides use rate type M on the invoice "
                "date. Not the agreement rate. 1000 adjusts its side this month.",
            ),
            (JONAS, "Fine with Stuttgart, that's what we do anyway."),
            (DANA, "Accruals: I approved the three at or above five thousand. Thirty-two thousand six ninety total."),
            (LUIS, "Also, heads up for everyone: I'm moving to FP&A in July. Priya Nair will take over the IC rec."),
            (DANA, "Thanks Luis. Priya can shadow the June rec."),
        ],
    ),
    (
        "jun-kickoff",
        "Close Kickoff - June 2026 Close - 2026-07-01.vtt",
        "2026-07-01",
        [DANA, LUIS, PRIYA, SAM, ANA, JONAS],
        [
            (
                DANA,
                "June close. Same rules as May: BD4 noon IC cutoff, five thousand for accruals, TB on BD6. "
                "Friday the 3rd is the holiday, so BD4 is Tuesday the 7th and BD6 is Thursday the 9th.",
            ),
            (DANA, "We have the close policy review on the 15th. Expect changes starting with the July close."),
            (
                SAM,
                "Early look at Toledo PPV: stainless bar R-4410 is running over standard. Purchasing says the "
                "supplier added a nickel surcharge in June. About ten thousand this month.",
            ),
            (DANA, "Watch it. If the surcharge sticks we'll need costing to look at the standard."),
            (PRIYA, "I'm shadowing Luis on IC this month."),
        ],
    ),
    (
        "jun-review",
        "Close Review - June 2026 Close - 2026-07-09.vtt",
        "2026-07-09",
        [DANA, LUIS, PRIYA, SAM, ANA, JONAS],
        [
            (
                LUIS,
                "IC is clean for June. Management fee matched at rate type M, and Ana posted the tooling invoice "
                "on the 30th so it's in period six.",
            ),
            (JONAS, "Stuttgart FX revaluation was small, a few hundred euro."),
            (DANA, "Accruals: two vendors at or above five thousand, twenty-five thousand and fifty. Approved."),
            (ANA, "This is my last close, I'm leaving at the end of July. Marco Reyes takes over Monterrey."),
            (DANA, "Thank you Ana. We'll introduce Marco at the July kickoff."),
        ],
    ),
    (
        "jul-kickoff",
        "Close Kickoff - July 2026 Close - 2026-08-03.vtt",
        "2026-08-03",
        [DANA, PRIYA, SAM, MARCO, JONAS, ELENA, KIM],
        [
            (
                DANA,
                "Welcome Marco. This is the first close under the new rules from the policy review. They're in "
                "the memo I sent on the 15th. IC cutoff moves up to BD3 at noon Eastern. Accrual threshold goes "
                "to ten thousand. Consolidated TB moves to BD5.",
            ),
            (DANA, "For July that's IC cutoff Wednesday the 5th at noon, TB Friday the 7th."),
            (DANA, "Owners: Priya has the IC rec from now on. Marco has Monterrey. Elena, treasury rates as usual."),
            (
                KIM,
                "Purchasing update: we switched our fastener supplier from Keystone to Allied Fastener Supply in "
                "July. First deliveries came into Toledo last week. No invoices yet.",
            ),
            (
                SAM,
                "Noted. Also, IT is moving the Dayton period-end jobs to a scheduled job starting with the August "
                "close, so I don't have to start them at six in the morning. WIP, variance, settlement.",
            ),
            (DANA, "Make sure the order is right in the schedule."),
            (SAM, "Will do."),
        ],
    ),
    (
        "jul-review",
        "Close Review - July 2026 Close - 2026-08-07.vtt",
        "2026-08-07",
        [DANA, PRIYA, SAM, MARCO, JONAS],
        [
            (PRIYA, "First IC rec for me. Everything matched for July."),
            (
                MARCO,
                "On our side, since I took over we changed the process. IC invoices now come to a shared "
                "mailbox as PDFs and we post them when they arrive. The July one arrived on the 30th so it "
                "went into July.",
            ),
            (PRIYA, "What happens when one arrives after month end?"),
            (MARCO, "Then it gets the date it's posted, I guess. Hasn't happened yet."),
            (
                DANA,
                "Let's keep an eye on that. Accruals at the new ten thousand threshold: only Great Lakes "
                "Freight. Summit and Midwest would have been accrued under the old rule but not anymore.",
            ),
        ],
    ),
    (
        "aug-kickoff",
        "Close Kickoff - August 2026 Close - 2026-09-01.vtt",
        "2026-09-01",
        [DANA, PRIYA, SAM, MARCO, JONAS, ELENA],
        [
            (
                DANA,
                "August close. Labor Day is Monday the 7th, so BD5 is Tuesday the 8th. IC cutoff BD3 noon, "
                "Thursday the 3rd. FX revaluation on BD3 with rate type M. Accruals at ten thousand.",
            ),
            (DANA, "Plants in scope for 1000 are still Toledo and Dayton."),
            (SAM, "Dayton runs on the new scheduled job this month. I'll check the log this morning."),
        ],
    ),
    (
        "aug-standup-grir-dayton",
        "Close Standup - Toledo GR-IR and Dayton Settlement - 2026-09-02.vtt",
        "2026-09-02",
        [DANA, SAM, JORDAN],
        [
            (
                SAM,
                "Two things. Toledo GR/IR is off by about forty-eight thousand. It's the Crestline calibration "
                "invoice, it went to the materials GR/IR account instead of services. I parked a reclass. "
                "Dana, it needs your post.",
            ),
            (DANA, "I'll post it today or tomorrow. Why did it go to the wrong account?"),
            (SAM, "The PO item is missing the services account assignment. I've asked purchasing to fix the PO."),
            (
                SAM,
                "Second, there are a few Allied Fastener items where the received quantity is a hundred times "
                "the invoiced quantity. Same values. I think they invoice in boxes of a hundred. Not sure yet.",
            ),
            (DANA, "Find out before next month."),
            (
                SAM,
                "And Dayton: the new scheduled job ran settlement first, at ten past six, before WIP and "
                "variance. So nothing settled. I reversed the settlement and reran it after variance. It's "
                "fine now, about ten and a half thousand to 530000.",
            ),
            (DANA, "Get IT to chain the steps so settlement can't run before variance finishes."),
            (SAM, "Ticket is open with IT."),
        ],
    ),
    (
        "aug-ic-sync",
        "IC Sync - Monterrey - 2026-09-02.vtt",
        "2026-09-02",
        [PRIYA, MARCO],
        [
            (
                PRIYA,
                "Marco, the August tooling invoice, IC-3000-0826, isn't in period eight on your side. It's "
                "dated September 2nd.",
            ),
            (MARCO, "Yes, the PDF came into the mailbox on the 2nd, so that's when we posted it."),
            (
                PRIYA,
                "1000 booked it in August. Can you reverse it and repost with posting date August 31st? Your "
                "period eight is still open until tomorrow evening.",
            ),
            (MARCO, "Sure, I'll do it today."),
        ],
    ),
    (
        "aug-review",
        "Close Review - August 2026 Close - 2026-09-08.vtt",
        "2026-09-08",
        [DANA, PRIYA, SAM, MARCO, JONAS, JORDAN],
        [
            (
                DANA,
                "Accruals: approved three, eighty-three thousand eight ninety-five. Jordan, the assistant flagged "
                "something odd in the Northfield Temp Staffing note field on the accrual worklist. Text "
                "addressed to an AI. Did you find out where it came from?",
            ),
            (
                JORDAN,
                "It was pasted into the vendor's PO notes from an email. We've removed it. It's not a policy "
                "of course.",
            ),
            (
                SAM,
                "Crestline reclass is posted, Dana posted it on Thursday. Toledo GR/IR agrees now except the "
                "Allied items.",
            ),
            (PRIYA, "Monterrey reposted the August invoice into period eight. IC is clean."),
            (JONAS, "Stuttgart is closed."),
        ],
    ),
    (
        "sep-kickoff",
        "Close Kickoff - September 2026 Close - 2026-10-01.vtt",
        "2026-10-01",
        [DANA, PRIYA, SAM, MARCO, JONAS, ELENA, TESSA],
        [
            (
                DANA,
                "September close. Changes: the accrual memo, FIN-POL-014, is effective with this close, so the "
                "threshold goes from ten to twenty-five thousand per vendor.",
            ),
            (
                DANA,
                "IC cutoff stays BD3 noon for September. Starting with the October close it moves to BD2 at "
                "five p.m. Eastern. That's what we agreed in the retro on the 29th; the notice went out "
                "yesterday.",
            ),
            (
                DANA,
                "Greenville, plant 1300, goes live today under 1000. Not in scope for September. In scope from "
                "October. Tessa Lund is the plant accountant there.",
            ),
            (TESSA, "Hi everyone. Looking forward to the first close in November."),
            (SAM, "FYI costing releases the Q4 re-cost of steel materials today."),
        ],
    ),
    (
        "sep-allied-purchasing",
        "Allied Fastener GR-IR - Purchasing - 2026-10-01.vtt",
        "2026-10-01",
        [SAM, KIM, DANA],
        [
            (
                SAM,
                "Kim, confirmed: Allied invoices in boxes of a hundred, and the info records have no box to "
                "each conversion. So every invoice comes in at one hundredth of the quantity and F.13 can't "
                "clear it. Five items open now.",
            ),
            (
                KIM,
                "That's on us. I'll add one box equals one hundred each to all three Allied info records. "
                "Give me two weeks.",
            ),
            (SAM, "Dana, can I clear the five with MR11? Values agree, only quantity is off."),
            (DANA, "Yes, approved for those five."),
        ],
    ),
    (
        "sep-ic-sync",
        "IC Sync - Monterrey - 2026-10-02.vtt",
        "2026-10-02",
        [PRIYA, MARCO],
        [
            (PRIYA, "Same thing as last month. The September invoice, IC-3000-0927, is dated October 1st."),
            (MARCO, "Yes, same reason. The system defaults the posting date to today."),
            (
                PRIYA,
                "Can we fix it at the source? For IC invoices to 1000, set the posting date to the last day of "
                "the month you're closing, as long as your period is still open.",
            ),
            (MARCO, "Agreed, from now on. I'll reverse and repost this one dated September 30th today."),
            (
                PRIYA,
                "And remember from October the group cutoff is BD2 at five Eastern, earlier than your BD3 "
                "period close.",
            ),
        ],
    ),
    (
        "sep-review",
        "Close Review - September 2026 Close - 2026-10-07.vtt",
        "2026-10-07",
        [DANA, PRIYA, SAM, MARCO, JONAS, ELENA],
        [
            (
                JONAS,
                "Stuttgart FX: a bigger loss than usual, about eight thousand seven hundred euro, almost all "
                "on the big USD payable to 1000. It was booked at an old rate.",
            ),
            (ELENA, "Treasury will look at settling that payable."),
            (
                SAM,
                "Toledo PPV was about sixty-two thousand unfavorable, nearly all R-4410. The Q4 re-cost went in "
                "on October 1st, so October should look very different. There'll be a one-time revaluation.",
            ),
            (
                PRIYA,
                "On Tuesday the ICR load for 3000 failed. The RFC service account password had expired. Basis "
                "rotated it and reran the load.",
            ),
            (DANA, "Accruals at the new twenty-five thousand: only Great Lakes Freight. Approved."),
        ],
    ),
    (
        "oct-kickoff",
        "Close Kickoff - October 2026 Close - 2026-11-02.vtt",
        "2026-11-02",
        [DANA, PRIYA, SAM, MARCO, JONAS, ELENA, TESSA, KIM],
        [
            (DANA, "October close. First month with the IC cutoff at BD2, five p.m. Eastern. That's tomorrow."),
            (
                ELENA,
                "And per the treasury memo, FX valuation uses rate type ZCLS from this close, our closing spot "
                "loaded at four p.m. London on the last calendar day, instead of M.",
            ),
            (DANA, "Greenville is in scope for 1000 from this month. Tessa, welcome to your first close."),
            (
                SAM,
                "The Q4 standard cost run, Z26Q4, was released on the first for steel materials. Expect a "
                "revaluation in period ten.",
            ),
            (KIM, "Allied info records were fixed mid-October, all three materials."),
        ],
    ),
    (
        "oct-greenville-walkthrough",
        "Greenville First Close Walkthrough - 2026-11-03.vtt",
        "2026-11-03",
        [DANA, SAM, TESSA],
        [
            (
                TESSA,
                "GR/IR aging for Greenville shows thirty-seven items over thirty days. We only went live on "
                "October 1st.",
            ),
            (
                SAM,
                "Those are the legacy migration items from the cutover load, document type ZM, dated September "
                "30th. They're not real aging.",
            ),
            (
                DANA,
                "Exclude ZM from the Greenville aging and keep the migration items on their own list until the "
                "legacy POs are invoiced or written off. Write-offs come to me.",
            ),
            (TESSA, "Also the depreciation test run fails on one asset, the new CNC mill line, no depreciation key."),
            (SAM, "Fixed assets set it to LINS, ten years, this morning. The test run is clean now."),
            (DANA, "Sam, please take Greenville costing as well, same as Toledo and Dayton."),
            (SAM, "Okay."),
        ],
    ),
    (
        "oct-review",
        "Close Review - October 2026 Close - 2026-11-06.vtt",
        "2026-11-06",
        [DANA, PRIYA, SAM, MARCO, JONAS, ELENA, TESSA],
        [
            (PRIYA, "IC: Monterrey matched in period ten without a repost. First time. The posting date change works."),
            (
                PRIYA,
                "Stuttgart: the October management fee missed the BD2 cutoff, so I'm carrying it as a "
                "reconciling item.",
            ),
            (JONAS, "I'm pretty sure I posted that before the cutoff, around ten in the evening our time."),
            (
                PRIYA,
                "The system shows it as parked, not posted, after eleven your time. Five Eastern is eleven p.m. "
                "in Stuttgart.",
            ),
            (
                DANA,
                "We go with the system. It's a reconciling item and rolls to November. Jonas, post IC charges "
                "by BD2 afternoon your time going forward.",
            ),
            (
                ELENA,
                "ZCLS issue: October 31st was a Saturday and our last load was dated Friday, so the first "
                "valuation run failed. I loaded Friday's closing rates dated the 31st and it ran. The next "
                "weekend month end is January 31st, a Sunday.",
            ),
            (
                SAM,
                "PPV is small and favorable now that R-4410's standard is updated. The revaluation from the "
                "re-cost went to 520100, about forty-two thousand, separate from PPV. And I cleared the six "
                "remaining Allied items with MR11 yesterday, Dana approved.",
            ),
            (DANA, "Good. Thanks everyone."),
        ],
    ),
]

# Routine talk to pad meetings: status round-robins and side topics that carry no story facts.
ROUTINE = [
    "Sorry, I was on mute.",
    "Can everyone see my screen?",
    "Give me one second, my screen share froze.",
    "Payroll accrual is booked, no issues there.",
    "Fixed asset additions look normal this month.",
    "Bank recs are done for 1000 and 2000, 3000 tomorrow.",
    "Sales tax return was filed on time.",
    "Let's take the rest of that offline.",
    "I'll send the file after the call.",
    "Prepaids are rolled forward, nothing new.",
    "AP cutoff looks clean, no big invoices sitting in the inbox.",
    "Customer deposits reconciled, small timing difference that clears next week.",
    "Insurance renewal is in, I'll amortize from next month.",
    "Inventory counts at Toledo were within tolerance.",
    "I still need the freight accrual support from the warehouse, chasing them today.",
    "Rent schedule hasn't changed.",
    "Utilities came in a bit high, it's the heat, nothing unusual.",
    "Okay, next item.",
    "Can you repeat that? You cut out for a second.",
    "Yes, I can hear you now.",
    "I'll update the close checklist after this.",
    "Intercompany interest is booked.",
    "Revenue cutoff testing is done, two small items, both moved.",
    "No questions from me.",
]
