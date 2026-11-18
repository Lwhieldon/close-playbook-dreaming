# v1 baseline: assistant sessions only (2026-11-11)

The first version dreamed over 17 close-assistant session transcripts (August to October 2026 closes,
about 60 KB) and asked 20 questions. It proved the pipeline worked and that the playbook kept dated
history, but the evaluation could not tell the memory types apart.

## Setup

| | |
|---|---|
| Corpus | 17 assistant session transcripts, 60,552 characters (12 through September, 5 for October) |
| Questions | 20 (stale fact, buried detail, recurring trap, process, synthesis, integrity) |
| Models | Claude Haiku 5.5 for analyzers, organizer and answers; Claude Sonnet 5.5 as judge |
| Scoring | Judge grades each answer 0, 0.5 or 1; percentages are the mean |
| Tool turns | 12 per answer |

## Dreams

| Dream | Sources | Playbook after | Cost |
|---|---|---|---|
| Through 2026-09 | 12 sessions, 40,163 chars | 14 pages, 63 links, 47,815 bytes | $0.077 |
| Through 2026-10 | 5 sessions, 20,389 chars | 17 pages, 86 links, 68,046 bytes | $0.063 |

Both dreams together cost $0.14. Lint after the October dream: no issues.

## Evaluation

| Question type | No memory | Raw transcripts | Playbook |
|---|---|---|---|
| Buried detail | 0% | 100% | 100% |
| Integrity | 0% | 100% | 100% |
| Process | 12% | 100% | 100% |
| Recurring trap | 0% | 100% | 67% |
| Stale fact | 0% | 100% | 100% |
| Synthesis | 0% | 100% | 100% |
| **All (judge score)** | **2%** | **100%** | **95%** |
| Required details present | 10% | 95% | 100% |
| Answer tokens in (incl. cache) | 4,653 | 292,740 | 300,135 |
| Answer cost (USD) | 0.005 | 0.030 | 0.029 |

Evaluation cost: $0.24 (of which the judge was $0.17).

## What we learned

- The pipeline worked: superseded rules came out as current value plus dated history.
- The playbook left some lines unsettled ("expected", "not confirmed") even after later sessions settled
  them.
- The playbook (68 KB) ended up larger than its sources (60 KB).
- With 60 KB of clean transcripts, raw search scored 100%. The evaluation was too easy to show what memory
  adds. This led to v2: a realistic, multi-source close record and harder questions.
