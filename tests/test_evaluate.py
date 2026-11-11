import json

import pytest
from conftest import FakeClient, response, text_block

from close_dreamer import config
from close_dreamer import evaluate as ev
from close_dreamer.usage import UsageTracker


def test_questions_load_and_have_unique_ids():
    qs = ev.load_questions(config.DATA / "eval_questions.yaml")
    assert len(qs) == 32 and len({q["id"] for q in qs}) == 32


def test_must_include_is_case_insensitive():
    q = {"must_include": ["BD2", "5"]}
    assert ev.must_include_ok(q, "The cutoff is bd2 at 5:00 pm ET")
    assert not ev.must_include_ok(q, "BD3 at noon")


def test_run_with_fake_client(tmp_path):
    (tmp_path / "_index.md").write_text("[[x]] - x\n", encoding="utf-8")
    qs = ev.load_questions(config.DATA / "eval_questions.yaml")[:2]

    def script(kw):
        if "output_config" in kw:  # the judge
            return response([text_block(json.dumps({"score": 1, "reason": "matches"}))])
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
    assert "| none | sources | playbook | both |" in table
    assert ev.save(graded, tracker, tmp_path / "runs").exists()


def test_playbook_condition_requires_a_playbook(tmp_path):
    with pytest.raises(FileNotFoundError):
        ev.run(FakeClient(lambda kw: None), [], sources_dir=config.CORPUS, playbook_dir=tmp_path / "none")


def test_unparseable_judge_scores_zero():
    client = FakeClient(lambda kw: response([text_block("not json")]))
    score, reason = ev.judge(
        client, {"type": "t", "question": "q", "expected": "e"}, "a", models=config.Models(), tracker=UsageTracker()
    )
    assert score == 0 and "unparseable" in reason
