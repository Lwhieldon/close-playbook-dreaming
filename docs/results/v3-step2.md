# v3 step 2: a year of closes in real file formats (2026-11-19)

Step 2 kept step 1's scoring and dream shape and grew the record to the scale where reading it raw
should start to cost turns: twelve closes, twenty plants, and the file formats a close team really gets.

## What changed from step 1

- **A record about 3.5 times larger.** Twelve closes, November 2025 to October 2026, including the 2025
  year end. 20 plants in three company codes (US, Germany, Mexico). 129 files, about 979,000 characters.
- **Real file formats.** Excel exports (`.xlsx`), PDF memos and policies, a Word procedure (`.docx`),
  fixed-width SAP spool lists (`.txt`), a BAI2 bank statement (`.dat`), background job logs, CSV extracts,
  Teams `.vtt` transcripts and a few assistant sessions. The tools read each format as text.
- **36 questions** instead of 32, including problems that hide for months (Kansas City orders never set
  to TECO), a year-end count shortage seen only across a meeting, the JE register and the change log, and
  a January 2027 planning question.
- **A focused organizer.** It gets the list of pages the dream added or changed and starts there.

## Setup

| | |
|---|---|
| Corpus | 129 files, 979,024 characters, Nov 2025 to Oct 2026 closes |
| Questions | 36, with key points, asked as of the start of the November 2026 close |
| Models | Claude Haiku 5.5 for analyzers, organizer and answers; Claude Sonnet 5.5 as judge |
| Code | commit `6450e19` |

## Dreams

| Dream | Sources | Cost | Playbook after |
|---|---|---|---|
| `--through 2026-09` | 114 files, 872,208 characters | $2.60 (analyzers $1.95, organizer $0.64 over 31 turns) | 146,458 bytes |
| `--through 2026-10` | 15 files, 106,816 characters | $0.54 (analyzers $0.25, organizer $0.29 over 28 turns) | 40 pages (6 stubs), 34 index entries, 184,848 bytes |

**The playbook is 19% of its record**, under the 30% target, and lint found no issues, no leaked secret
and no copied injection.

**The focused organizer worked.** It used 31 and 28 turns, where step 1's organizer used most or all of
its 80. The dreams cost $3.14 in total against a pre-run estimate of $3.24; the estimate has since been
recalibrated on these two runs and now comes within 5% of each.

**Two files failed.** In each dream one analyzer stopped when the model passed a line range (`[28, 45]`,
`[8, 35]`) where the read tool expected one line number: `ICR_Matching_2026-02.csv` in the
`--through 2026-09` dream and `PPV_by_Material_1100_2026-10.csv` in the `--through 2026-10` dream. No
question or fact depends on either file, and the October standard cost change they mention (R-4410 at
$9.15) reached the playbook from other sources. Fixed after this run: a malformed argument now comes back
to the agent as an error it can correct, as other bad inputs already did.

## Evaluation: 12 tool turns

| Question type | No memory | Raw record | Playbook | Playbook + record |
|---|---|---|---|---|
| Buried detail | 0% | 98% | 98% | 93% |
| Evidence | 0% | 100% | 100% | 100% |
| History | 0% | 100% | 100% | 100% |
| Integrity | 33% | 92% | 75% | 100% |
| Process | 10% | 100% | 97% | 97% |
| Recurring trap | 7% | 91% | 88% | 88% |
| Stale fact | 0% | 93% | 98% | 100% |
| Synthesis | 0% | 83% | 70% | 83% |
| **All (judge score)** | **5%** | **94%** | **91%** | **95%** |
| 95% interval | 1-10% | 90-98% | 86-96% | 91-98% |
| Required details present | 14% | 97% | 97% | 100% |
| Answer tokens in (incl. cache) | 8,344 | 2,880,032 | 1,036,903 | 2,113,648 |
| Answer cost (USD) | 0.009 | 0.187 | 0.088 | 0.147 |

Evaluation cost: $1.11 (judge $0.68).

## Turn sweep

| Tool turns | Raw record | Playbook | Playbook + record |
|---|---|---|---|
| 2 | 85% (77-93%) | 89% (81-95%) | 92% (86-96%) |
| 4 | 91% (86-96%) | 89% (82-94%) | 92% (87-97%) |
| 8 | 96% (93-99%) | 90% (83-96%) | 93% (88-97%) |
| 12 | 94% (90-98%) | 91% (86-96%) | 95% (91-98%) |

| Tool turns | Answer cost: raw record | Playbook | Playbook + record |
|---|---|---|---|
| 2 | $0.125 | $0.081 | $0.126 |
| 4 | $0.153 | $0.063 | $0.119 |
| 8 | $0.176 | $0.064 | $0.120 |
| 12 | $0.187 | $0.088 | $0.147 |

| Tool turns | Synthesis: raw record | Playbook | Playbook + record |
|---|---|---|---|
| 2 | 48% | 67% | 68% |
| 4 | 78% | 67% | 68% |
| 8 | 83% | 67% | 73% |
| 12 | 83% | 70% | 83% |

Sweep cost: $2.62 ($0.87, $0.86 and $0.89).

## Compared with step 1

| | Step 1 (275K characters) | Step 2 (979K characters) |
|---|---|---|
| Playbook size | 79,661 bytes, 29% of the record | 184,848 bytes, 19% of the record |
| Dream cost | $1.97 | $3.14 |
| Raw record at 2 turns | 90% | 85% |
| Playbook at 2 turns | 94% | 89% |
| Answer cost at 12 turns: raw record | $0.108 | $0.187 (+73%) |
| Answer cost at 12 turns: playbook | $0.055 | $0.088 (+60%) |

## What this says

- **The larger record started to cost raw search turns, as expected.** At 2 tool turns the raw record fell
  from 90% to 85%, and on synthesis questions to 48%: q29 (what changed between June and October) scored 0
  because the answer gave a superseded $5,000 threshold as current, and q10 couldn't find the document
  number in two reads. With 8 turns raw search recovers to 96%.
- **Accuracy is still a statistical tie at every turn limit.** Every interval overlaps. With 36 questions,
  3 points is about one question. The playbook plus the record scored highest at 2, 4 and 12 turns.
- **The playbook's cost advantage grew with the record.** It answers for 35% to 65% of what raw search
  costs, and at 4 or more turns it reads 34% to 40% of the tokens. Its answer cost barely moves with the turn limit ($0.06 to
  $0.09); raw search's climbs with every turn it is given.
- **Synthesis is the playbook's weak spot, and it doesn't improve with more turns** (67% to 70%), because
  the answer can only be as good as the page. The judge's notes point to dream quality, not retrieval:
  - **q28 (January 2027) and q30 (open going into November):** the answers listed only some of the action
    items across plants. No page gathers loose ends across plants into one list.
  - **q26 (Monterrey):** the playbook blames the system's default posting date and leaves out the
    handover to Marco Reyes and the shared mailbox, so the cause is wrong.
  - **q12 (Allied Fastener)** still hedges on whether the fix is proven, as in step 1, and **q15 (ZCLS at a
    weekend month end)** still records only half the reason.
- **What would test the playbook next:** an organizer instruction to keep a running "open items and
  watch-outs" page and to state settled conclusions plainly, then a rerun of the `--through 2026-10`
  dream and the evaluation. That targets the synthesis and trap misses directly.

Raw outputs are in `output/runs/` from this run (not committed): `dream-2026-09-20261119T155353Z.json`,
`dream-2026-10-20261119T160356Z.json`, `eval-20261119T182532Z.json`, `eval-*-turns{2,4,8}.json`,
`sweep-20261119T184036Z.md`.
