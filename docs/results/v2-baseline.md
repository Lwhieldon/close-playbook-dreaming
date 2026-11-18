# v2 baseline: the close team's work record (2026-11-18)

v2 replaced the assistant-only transcripts with the close team's whole record: Teams meeting transcripts,
a monthly ERP evidence pack, policy memos and a few assistant sessions, across six closes. The questions
got harder (history, ERP-only evidence, a contradiction, synthesis) and a turn-limited run was added.

## Setup

| | |
|---|---|
| Corpus | 53 files, 274,974 characters: 17 meetings (.vtt), 26 ERP exports (.csv), 5 policy memos, 5 assistant sessions; May to October 2026 closes |
| Questions | 32 across 8 types |
| Models | Claude Haiku 5.5 for analyzers, organizer and answers; Claude Sonnet 5.5 as judge |
| Scoring | Judge grades each answer 0, 0.5 or 1; percentages are the mean |
| Code | commit `792b73e` |

## Dreams

| Dream | Playbook after |
|---|---|
| Through 2026-09, then 2026-10 | 57 pages (1 stub), 618 links, 56 index entries, 350,218 bytes |

The dream cost was not recorded (the terminal output was lost, and v2 did not save dream usage to disk;
v3 does).

**What the playbook got right:**
- **Settled open lines:** Allied Fastener's GR/IR is recorded as fixed on 10/14 (change log, ME12) and
  cleared on 11/05 (MR11 5000034412), not "pending".
- **Precedence:** on the Stuttgart management fee, it sided with the ERP timestamp (parked 23:10 CET, after
  the cutoff) over Jonas Becker's recollection, and recorded the controller's ruling.
- **The planted password stayed out.**

**What it got wrong:**
- **Bigger than its sources:** 350 KB of playbook from 275 KB of record (127%). Many pages are one per
  source per month (`account-recon-status-may-2026`, `close-review-june-2026`, `ic-matching-july-2026`)
  instead of one per topic.
- **The injected instruction was copied word for word** into two pages, each time with a note that it was
  not followed. Lint flags this: memory should describe an attack, not reproduce it.

## Evaluation: 12 tool turns

| Question type | No memory | Raw record | Playbook | Playbook + record |
|---|---|---|---|---|
| Buried detail | 0% | 100% | 90% | 100% |
| Evidence | 0% | 100% | 100% | 100% |
| History | 0% | 100% | 100% | 100% |
| Integrity | 50% | 100% | 100% | 100% |
| Process | 10% | 100% | 100% | 100% |
| Recurring trap | 17% | 83% | 67% | 50% |
| Stale fact | 0% | 100% | 100% | 100% |
| Synthesis | 0% | 100% | 100% | 90% |
| **All (judge score)** | **8%** | **98%** | **95%** | **94%** |
| Required details present | 16% | 97% | 97% | 94% |
| Answer tokens in (incl. cache) | 7,397 | 1,380,643 | 1,262,279 | 1,561,918 |
| Answer cost (USD) | 0.009 | 0.108 | 0.110 | 0.127 |

Evaluation cost: $0.79 (judge $0.43).

## Evaluation: 3 tool turns

| Question type | Raw record | Playbook | Playbook + record |
|---|---|---|---|
| Buried detail | 40% | 80% | 20% |
| Evidence | 50% | 100% | 50% |
| History | 50% | 100% | 100% |
| Integrity | 33% | 100% | 100% |
| Process | 40% | 60% | 80% |
| Recurring trap | 33% | 67% | 83% |
| Stale fact | 14% | 86% | 57% |
| Synthesis | 0% | 50% | 50% |
| **All (judge score)** | **28%** | **77%** | **62%** |
| Required details present | 28% | 81% | 62% |
| Answer cost (USD) | 0.064 | 0.067 | 0.083 |

## What we learned

- **With enough turns, raw search still finds nearly everything** in 275 KB (98% vs. 95% for the playbook).
- **Under a turn limit, the playbook scores almost three times higher than the raw record** (77% vs. 28%).
  This is the clearest evidence so far that dreamed memory pays off when an assistant can only look a few
  times.
- **But the turn-limited run partly measures running out of time:** 23 of the raw record's misses were "ran
  out of turns before answering", and so were 6 of the playbook's. v3 gives every agent one last tool-free
  turn to answer from what it has read.
- **The 0 / 0.5 / 1 scale is coarse:** naming two of six open items scored the same as a single small error.
  v3 scores each question by its key points.
- **Playbook + record did worse than the playbook alone:** a second folder invites more searching, which
  spends the turns.

v3 scores are not directly comparable with these: the scoring method and the turn-limit behavior both
changed. v3 reports v2's corpus again under the new method so the comparison is like for like.
