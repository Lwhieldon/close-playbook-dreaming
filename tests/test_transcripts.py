import pytest

from close_dreamer import config
from close_dreamer import transcripts as tx


def test_close_period_rule():
    assert tx.close_period(2026, 9, 2) == "2026-08"  # close work right after month end
    assert tx.close_period(2026, 7, 15) == "2026-07"  # a mid-month memo informs that month's close
    assert tx.close_period(2027, 1, 4) == "2026-12"


def test_load_assigns_kinds_and_periods():
    loaded = {t.name: t for t in tx.load(config.CORPUS)}
    kickoff = loaded["uploads/Close Kickoff - August 2026 Close - 2026-09-01.vtt"]
    assert (kickoff.kind, kickoff.period) == ("meeting", "2026-08")
    je = loaded["erp/JE_Register_2026-10.xlsx"]
    assert (je.kind, je.period) == ("erp", "2026-10")
    memo = loaded["policies/FIN-POL-014 Manual Accrual Threshold - 2026-09-25.pdf"]
    assert (memo.kind, memo.period) == ("policy", "2026-09")
    sessions = [t for t in loaded.values() if t.kind == "session"]
    assert len(sessions) == 5 and all(t.session_id.startswith("sesn_") for t in sessions)
    assert all(t.period for t in loaded.values())


def test_select_first_and_incremental():
    all_t = tx.load(config.CORPUS)
    first = tx.select(all_t, through="2026-09")
    months = ["2025-11", "2025-12"] + [f"2026-{m:02d}" for m in range(1, 10)]
    assert {t.period for t in first} == set(months)  # eleven closes, November 2025 to September 2026
    second = tx.select(all_t, through="2026-10", after="2026-09")
    assert {t.period for t in second} == {"2026-10"}
    assert {t.kind for t in second} == {"meeting", "erp", "policy", "session"}


def test_bad_period_rejected():
    with pytest.raises(ValueError):
        tx.select([], through="Sept")
