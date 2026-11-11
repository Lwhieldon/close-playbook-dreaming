import pytest

from close_dreamer import config
from close_dreamer import transcripts as tx


def test_close_period_is_previous_month():
    assert tx.close_period(2026, 9) == "2026-08"
    assert tx.close_period(2027, 1) == "2026-12"


def test_load_assigns_periods():
    loaded = {t.name: t for t in tx.load(config.TRANSCRIPTS)}
    assert loaded["00-controller-notes.md"].period is None
    assert loaded["02-aug-toledo-grir.txt"].period == "2026-08"
    assert loaded["16-oct-fx-zcls.txt"].period == "2026-10"
    assert loaded["02-aug-toledo-grir.txt"].session_id == "sesn_close_02"


def test_select_first_and_incremental():
    all_t = tx.load(config.TRANSCRIPTS)
    first = tx.select(all_t, through="2026-09")
    assert any(t.period is None for t in first)
    assert {t.period for t in first if t.period} == {"2026-08", "2026-09"}
    second = tx.select(all_t, through="2026-10", after="2026-09")
    assert {t.period for t in second} == {"2026-10"}


def test_bad_period_rejected():
    with pytest.raises(ValueError):
        tx.select([], through="Sept")
