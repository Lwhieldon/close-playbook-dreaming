import json

import pytest
from conftest import FakeClient, response, text_block

from close_dreamer import config
from close_dreamer import evaluate as ev
from close_dreamer.usage import UsageTracker


def test_questions_load_and_have_unique_ids():
    qs = ev.load_questions(config.DATA / "eval_questions.yaml")
    assert len(qs) == 36 and len({q["id"] for q in qs}) == 36


def test_must_include_is_case_insensitive():
    q = {"must_include": ["BD2", "5"]}
    assert ev.must_include_ok(q, "The cutoff is bd2 at 5:00 pm ET")
    assert not ev.must_include_ok(q, "BD3 at noon")


def test_run_with_fake_client(tmp_path):
    (tmp_path / "_index.md").write_text("[[x]] - x\n", encoding="utf-8")
    qs = ev.load_questions(config.DATA / "eval_questions.yaml")[:2]

    def script(kw):
        if "output_config" in kw:  # the judge
            pts = [{"n": i, "verdict": "met"} for i in range(1, 7)]
            verdict = {"points": pts, "fatal": False, "deductions_hit": [], "reason": "matches"}
            return response([text_block(json.dumps(verdict))])
        return response([text_block("BD2 at 5:00 pm ET; threshold $25,000")])

    graded, tracker = ev.run(
        FakeClient(script),
        qs,
        sources_dir=config.CORPUS,
        playbook_dir=tmp_path,
        budget_usd=1.0,
        concurrency=2,
        on_event=None,
    )
    assert len(graded) == 8
    assert all(g.judge_score == 1 for g in graded)
    table = ev.summarize(graded, tracker)
    assert "| none | sources | playbook | both |" in table and "95% interval" in table
    assert all(g.points and set(g.points) == {"met"} for g in graded)
    assert ev.save(graded, tracker, tmp_path / "runs").exists()


def test_playbook_condition_requires_a_playbook(tmp_path):
    with pytest.raises(FileNotFoundError):
        ev.run(FakeClient(lambda kw: None), [], sources_dir=config.CORPUS, playbook_dir=tmp_path / "none")


def test_unparseable_judge_scores_zero():
    client = FakeClient(lambda kw: response([text_block("not json")]))
    score, reason, verdicts, fatal = ev.judge(
        client, {"type": "t", "question": "q", "expected": "e"}, "a", models=config.Models(), tracker=UsageTracker()
    )
    assert score == 0 and "unparseable" in reason and verdicts is None


def test_every_question_has_key_points():
    for q in ev.load_questions(config.DATA / "eval_questions.yaml"):
        assert 2 <= len(q["key_points"]) <= 6, q["id"]
        assert q.get("points_needed", 1) <= len(q["key_points"]), q["id"]


def test_score_points():
    q = {"key_points": ["a", "b", "c", "d"]}
    assert ev.score_points(q, ["met", "met", "partial", "missed"], False, []) == 0.625
    assert ev.score_points(q, ["met"] * 4, True, []) == 0  # fatal
    q3 = {**q, "points_needed": 2}
    assert ev.score_points(q3, ["met", "met", "missed", "missed"], False, []) == 1  # capped
    qd = {**q, "deductions": ["lists a resolved item as open"]}
    assert ev.score_points(qd, ["met"] * 4, False, [1]) == 0.75
    assert ev.score_points(qd, ["met"] * 4, False, [9]) == 1  # unknown deduction ignored


def test_judge_maps_verdicts_by_number_and_missing_ones_are_missed():
    q = {"type": "t", "question": "q", "expected": "e", "key_points": ["a", "b", "c"]}
    out = {
        "points": [{"n": 3, "verdict": "met"}, {"n": 1, "verdict": "partial"}],
        "fatal": False,
        "deductions_hit": [],
        "reason": "r",
    }
    client = FakeClient(lambda kw: response([text_block(json.dumps(out))]))
    score, _, verdicts, _ = ev.judge(client, q, "a", models=config.Models(), tracker=UsageTracker())
    assert verdicts == ["partial", "missed", "met"] and score == 0.5


def test_interval_and_sweep_table():
    assert ev.interval([1.0] * 10) == "100-100%"
    lo, hi = (int(x) for x in ev.interval([0.0, 1.0] * 16).rstrip("%").split("-"))
    assert lo < 50 < hi
    g = lambda c, s: ev.Graded("q", "t", c, "", True, s, "")  # noqa: E731
    table = ev.sweep_table({2: [g("sources", 0.0), g("playbook", 1.0)], 8: [g("sources", 1.0), g("playbook", 1.0)]})
    assert "| 2 | 0% | 100% |" in table and "| 8 | 100% | 100% |" in table
