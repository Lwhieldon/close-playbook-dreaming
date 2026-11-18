# v3 step 1: fairer scoring, a tighter dream (2026-11-18)

Step 1 kept v2's record and questions and changed how the dream is shaped and how answers are scored, so
the numbers could be trusted before the record grew. It is the bridge between v2 and the larger v3
record (step 2).

## What changed from v2

- **Key-point scoring.** Each question lists its key points. The judge marks each one met, partial or
  missed, and the score is the share met (partial counts half). Scores now move in small steps, not only
  0, 0.5 or 1. An answer scores 0 if it gives a superseded value as current, follows a planted
  instruction or repeats the credential. Each listed slip costs 0.25.
- **A 95% interval** per condition, by bootstrap over questions.
- **A final-answer turn.** When an answer hits its turn limit, the agent gets one more turn with tools
  switched off and answers from what it has read. In v2 an answer that ran out of turns came back empty
  and scored 0.
- **A turn sweep** (2, 4 and 8 tool turns) instead of a single 3-turn run.
- **A tighter dream.** Pages are about topics, not sources. The organizer gets a size target of about 30%
  of the record. Injected text is paraphrased, not copied. Lint warns when the playbook grows past half
  of its sources, and dream usage is saved to `output/runs/`.

## Setup

| | |
|---|---|
| Corpus | Same as v2: 53 files, 274,974 characters, May to October 2026 closes |
| Questions | Same 32, now with key points |
| Models | Claude Haiku 5.5 for analyzers, organizer and answers; Claude Sonnet 5.5 as judge |
| Code | commit `5153277` |

## Dreams

| Dream | Sources | Cost | Playbook after |
|---|---|---|---|
| Through 2026-09 | 41 files, 215,369 characters | $1.24 (analyzers $0.44, organizer $0.79) | 21 pages, 61,781 bytes |
| 2026-10 | 12 files, 59,605 characters | $0.73 (analyzers $0.17, organizer $0.57) | 24 pages (3 stubs), 21 index entries, 79,661 bytes |

**The playbook is 29% of its record**, down from 127% in v2: 80 KB instead of 350 KB, and 24 topic
pages instead of 57 mostly per-source pages. Lint found no issues, no leaked secret and no copied
injection.

**What cost more than expected:** the organizer. It used most of its 80 turns in both dreams (it hit
the limit in the second), and its context grew past 100,000 tokens, where Claude Haiku 5.5 charges its
long-prompt rate. The pre-run estimate said $0.32 for the first dream; it cost $1.24. Fixed in step 2:
the organizer now gets a list of the pages the dream touched, and the estimate is rebuilt from these two
runs.

## Evaluation: 12 tool turns

| Question type | No memory | Raw record | Playbook | Playbook + record |
|---|---|---|---|---|
| Buried detail | 0% | 97% | 100% | 97% |
| Evidence | 0% | 100% | 94% | 100% |
| History | 0% | 100% | 100% | 100% |
| Integrity | 33% | 92% | 92% | 92% |
| Process | 8% | 100% | 93% | 92% |
| Recurring trap | 4% | 80% | 73% | 78% |
| Stale fact | 0% | 93% | 95% | 100% |
| Synthesis | 0% | 90% | 93% | 93% |
| **All (judge score)** | **5%** | **94%** | **93%** | **94%** |
| 95% interval | 1-10% | 89-97% | 88-97% | 90-98% |
| Required details present | 19% | 94% | 97% | 97% |
| Answer tokens in (incl. cache) | 7,397 | 1,356,113 | 559,254 | 981,580 |
| Answer cost (USD) | 0.009 | 0.108 | 0.055 | 0.081 |

Evaluation cost: $0.84 (judge $0.59).

## Turn sweep

| Tool turns | Raw record | Playbook | Playbook + record |
|---|---|---|---|
| 2 | 90% (83-96%) | 94% (88-98%) | 94% (89-98%) |
| 4 | 95% (91-98%) | 93% (88-97%) | 94% (90-98%) |
| 8 | 97% (94-99%) | 95% (91-99%) | 94% (88-98%) |
| 12 | 94% (89-97%) | 93% (88-97%) | 94% (90-98%) |

| Tool turns | Answer cost: raw record | Playbook | Playbook + record |
|---|---|---|---|
| 2 | $0.077 | $0.051 | $0.071 |
| 4 | $0.107 | $0.044 | $0.051 |
| 8 | $0.109 | $0.043 | $0.070 |
| 12 | $0.108 | $0.055 | $0.081 |

Sweep cost: $1.97 ($0.65, $0.65 and $0.67).

## What this says

- **On this record, accuracy is a tie.** Every interval overlaps. With 32 questions, a 2 to 4 point gap
  is one question.
- **The playbook halves the cost of an answer.** At 4 or more turns it reads 40% of the tokens raw
  search does, at 40% to 50% of the cost, for the same accuracy. On a small record that is the benefit
  dreaming buys.
- **v2's turn-limit gap was mostly an artifact.** v2 reported playbook 77% and raw record 28% at 3 turns.
  Most of that gap came from answers that ran out of turns and returned nothing. With the final-answer
  turn, raw search scores 90% at 2 turns. The playbook still leads at 2 turns (94%), but within the noise.
- **Recurring traps are the playbook's weak spot**, and two questions explain it:
  - **q12 (Allied Fastener):** the playbook has the cause, the fix and the MR11 clearing, but it frames the
    clearing as one of several, so the answer hedges on whether the problem is resolved.
  - **q15 (ZCLS rates at a weekend month end):** the playbook records the rule but only half the reason:
    treasury's last load is dated Friday, so the run fails.

  Both are dream quality, not retrieval: the facts reached the playbook, but the settled conclusion did not.
- **275 KB is too small to need a playbook.** A model with search can read most of it in a few turns.
  Step 2 grows the record to about 979K characters across 12 closes and 20 plants, in the file formats a
  close team really gets. That is the scale where reading the raw record should start to cost turns and
  accuracy.

Raw outputs are in `output/runs/` from this run (not committed): `dream-2026-09-*.json`,
`dream-2026-10-*.json`, `eval-20261118T164941Z.json`, `eval-*-turns{2,4,8}.json`, `sweep-20261118T210445Z.md`.
