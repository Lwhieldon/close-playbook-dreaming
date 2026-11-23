# Results

Each version's measured results, kept as they were recorded. Numbers come from `close-dreamer evaluate`
and `close-dreamer dream` output; one run each, so read them as the shape of the effect, not its size.

| Version | Date | What changed | Headline |
|---|---|---|---|
| [v1 baseline](v1-baseline.md) | 2026-11-11 | 17 assistant sessions, 20 questions | Raw transcripts 100%, playbook 95%: the eval was too easy |
| [v2 baseline](v2-baseline.md) | 2026-11-18 | The team's work record (meetings, ERP, memos, sessions), 32 questions, turn limit | At 3 tool turns: playbook 77%, raw record 28% |
| [v3 step 1](v3-step1.md) | 2026-11-18 | Key-point scoring, final-answer turn, 2/4/8 turn sweep, topic-page dream with a size target | Accuracy ties (93-97%); the playbook is 29% of its record and halves answer cost |
| [v3 step 2](v3-step2.md) | 2026-11-19 | 12 closes, 20 plants, xlsx/pdf/docx/spool/BAI2/job-log files (129 files, about 979K characters), 36 questions, focused organizer | Still a tie on accuracy; raw search drops to 85% at 2 turns (synthesis 48%); the playbook is 19% of its record and answers at 35-65% of the cost |
| [v3 step 3](v3-step3.md) | 2026-11-23 | Watchlist, status and cause lines; "absence is not evidence" for the analyzers; 4 held-out questions | A first attempt backfired (88.8%); the fix holds level with step 2 (90-92% at every turn limit, 90.7% vs raw search's 85.5% at 2 turns) at 40-50% of raw search's answer cost; synthesis stays at 70% |
