# v3 step 3: open items, status and cause lines (2026-11-23)

Step 2 left the playbook tied with raw search on accuracy but weak on synthesis (70%): no page gathered
the loose ends across plants, a cause that spanned pages (Monterrey) was split, and settled conclusions
were hedged. Step 3 tried to fix that in the dream, in two attempts. The first made things worse; the
second recovered and is kept. Synthesis did not improve.

The corpus, the 36 scored questions, the models and the scoring are the same as in [step 2](v3-step2.md).

## Held-out questions

Before changing any prompt, four synthesis questions (q37 to q40) were written from the corpus only and
marked `holdout: true`: Keystone Castings' year-end invoice and duplicate payment, 2025 year-end lessons
for December 2026, the plants that started or stopped, and production order problems across plants. They
check that a prompt change doesn't help the 36 questions at the expense of questions nobody tuned for.
The step 2 playbook scored 100% on them, so they work as a "do no harm" check, not as evidence of a gain.
Scores below are on q01 to q36 unless marked; holdouts are reported separately.

**Answer key correction.** q39's key gave Greenville's go-live as 09/30/2026. The corpus says 10/01
("goes live today", September kickoff on 2026-10-01; "We only went live on October 1st", walkthrough);
09/30 is the date on its legacy cutover documents. The judge marked two correct answers fatal against the
wrong key (fix 3 at 12 turns in the playbook + record condition, and at 8 turns in the playbook
condition). The key is corrected; the scores below are as measured, with those two grades noted.

## Stage A: a watchlist, status lines and cause lines (failed)

**What changed.** The organizer was told to keep a `close-watchlist.md` page of open items and coming
risks, to start pages with a `Status (as of ...)` line, and to write a `Cause:` line where a problem's
explanation spans pages. The analyzers were told to keep the reason behind a rule and the cause of a
problem. A new `close-dreamer organize` command applied the new organizer instructions to the step 2
playbook in one organizer pass ($0.18), with no new dream.

**Result.**

| | Step 2 | Stage A |
|---|---|---|
| Playbook, q01 to q36 | 91.0% | 88.8% |
| Synthesis | 70% | 70% |
| Holdouts | 100% | 83% |
| Answer cost (36 questions) | $0.088 | $0.104 |

**Why it failed.** The step 2 pages held 23 lines that called something open only because a record was
missing from one export ("reversal not confirmed", "not seen in the October register"), even where a
signed-off reconciliation said it was done. The watchlist gathered those lines into a list of "open"
items, and status lines put "Open" at the top of process pages. The FX procedure page now started with
an open status, and q15 (the FX weekend check) fell from 0.88 to 0.25. The lint count of these lines rose
from 23 to 38. A tidier top layer amplified a flaw that was already in the pages.

## Fix 3: absence is not evidence (kept)

The fix went to the source of the flaw, the analyzers, rather than filtering what the organizer
gathered:

- **Absence is not evidence** (analyzer and organizer). Only positive evidence changes a claim. A
  signed-off reconciliation is ERP evidence. A real gap goes in an `Evidence gaps:` section, worded as a
  check, and never makes a problem open.
- **Status lines on problem pages only.** Process, rule, account, plant and owner pages keep their
  current rule first.
- **A short watchlist.** Only items a source states are still open, each with owner, page and source;
  usually under 12. Repeat checks go under "Coming up" as `Watch:` notes.
- **Lint counts the absence lines** outside evidence-gap sections, as a cheap check that the fix took.

Both dreams were rerun from an empty playbook with these prompts (code commit `c69a572`).

### Dreams

| Dream | Cost | Playbook after |
|---|---|---|
| `--through 2026-09` | $3.18 (analyzers $2.15, organizer $1.04 over 53 requests) | 31 pages, 135,755 bytes |
| `--through 2026-10` | $0.55 (analyzers $0.33, organizer $0.22) | 34 pages (1 stub), 33 index entries, 181,204 bytes, 19% of its record |

No analyzer failed and lint found no issues, no leaked secret and no copied injection. The
`--through 2026-09` dream cost 25% more than its $2.54 estimate: the analyzers wrote more under the new
rules and the organizer worked longer on a larger playbook.

**The watchlist** lists 13 open items going into the November close, each with an owner and the source
that last called it open: the Allied info records (Kim Alvarez), the Keystone payment-run duplicate check
with no owner, the exposed `ICR_RFC_SVC` password, the CC 3000 preparer still showing GTORRES, the
Stuttgart FX loss under treasury review. "Coming up" covers the 31 January 2027 weekend month end, the
year end and Greenville's next close. Settled items were dropped after the `--through 2026-10` dream.

**Absence lines** in page text: 21, against 23 in step 2 and 38 in stage A. Another 20 sit in
evidence-gap sections, where they belong. Most of the 21 are plain facts ("the amount is not in the job
log") rather than items made open by a gap, but the count did not reach the goal of under 10.

### Evaluation

| Tool turns | Raw record (step 2) | Playbook, step 2 | Playbook, fix 3 | Playbook + record, step 2 | Playbook + record, fix 3 |
|---|---|---|---|---|---|
| 2 | 85.5% (77-93%) | 88.8% (82-95%) | **90.7%** (85-96%) | 91.6% | 88.3% |
| 4 | 91.3% (86-96%) | 88.7% (82-95%) | **92.4%** (86-97%) | 92.4% | 92.7% |
| 8 | 95.9% (93-99%) | 90.1% (84-96%) | **91.0%** (86-96%) | 92.7% | 94.0% |
| 12 | 94.2% (90-98%) | 91.0% (86-96%) | **90.3%** (84-96%) | 94.5% | 91.0% |

| Tool turns | Answer cost, 36 questions: raw record | Playbook, step 2 | Playbook, fix 3 |
|---|---|---|---|
| 2 | $0.125 | $0.081 | $0.077 |
| 4 | $0.153 | $0.063 | $0.059 |
| 8 | $0.176 | $0.064 | $0.063 |
| 12 | $0.187 | $0.088 | $0.082 |

Fix 3's runs answered 40 questions; costs are scaled to 36 for comparison. The raw record was not rerun:
it reads the corpus, not the playbook, so step 2's figures stand.

| Tool turns | Synthesis: raw record | Playbook, step 2 | Playbook, fix 3 |
|---|---|---|---|
| 2 | 48% | 67% | 73% |
| 4 | 78% | 67% | 70% |
| 8 | 83% | 67% | 70% |
| 12 | 83% | 70% | 70% |

| Holdouts (q37 to q40), playbook | 2 turns | 4 turns | 8 turns | 12 turns |
|---|---|---|---|---|
| Fix 3 | 100% | 100% | 75%, one grade against the wrong q39 key | 96% |

Evaluation cost: $0.65 at 12 turns, $1.79 for the sweep.

## What this says

- **Fix 3 recovered stage A's losses and holds level with step 2.** It's within a point of step 2 at
  every turn limit, a little ahead at 2 and 4 turns, and slightly cheaper per answer. Every interval
  overlaps. It's kept because a close team would use the watchlist and the problem-page status lines, and
  they cost nothing in accuracy or answer cost.
- **The core result from step 2 stands.** At 2 tool turns the playbook scores 90.7% against raw search's
  85.5%, and 73% against 48% on synthesis. At 8 and 12 turns raw search scores 3 to 5 points higher, about
  one or two questions, within the intervals. The playbook answers for 40% to 50% of raw search's cost.
- **Synthesis did not improve.** The judge's notes show the facts are in the playbook but not where the
  answer looks first:
  - **q15 (FX weekend check, 0.88 to 0.50):** `fx-revaluation.md` explains the Friday-dated load, the
    failed run and the next weekend month end (31 January 2027), but in a section below the procedure. The
    answer read the procedure and stopped.
  - **q26 (Monterrey, 0.50 to 0.33):** the page says arrival-day posting started "from July 2026" and
    lists the August invoice dated 2 September, but never joins them to say the problem started in the
    August close. That join is what the `Cause:` line was meant to do; the organizer didn't write one.
  - **q10 (Stuttgart loss):** the page sets the 8,742.31 recon figure against the 10,210.50 posted
    document and calls the gap unexplained, so the answer hedged.
- **A tidier top layer amplifies whatever the pages get wrong.** Stage A's lesson: fix how the analyzers
  record facts before adding summaries that gather them.
- **The test can't see small gains.** One question is about 2.8 points of the 36-question score, and one
  synthesis question is 20 points of the synthesis score. Measuring a real synthesis gain needs more
  synthesis questions, not another prompt round.

## Not tried

- Put the reason and the dated risk in the first lines of a rule page (q15).
- Require a `Cause:` line where a problem follows an owner or process change (q26).
- A larger synthesis question set, so a gain of a few points can be told apart from noise.

Raw outputs are in gitignored folders: `output-v3-step3a/runs/` (stage A organize pass, holdout baseline
and evaluation) and `output/runs/` (fix 3 dreams, evaluation and sweep: `dream-2026-09-20261119T224822Z.json`,
`dream-2026-10-20261120T204209Z.json`, `eval-20261123T200617Z.json`, `eval-*-turns{2,4,8}.json`,
`sweep-20261123T202822Z.md`).
