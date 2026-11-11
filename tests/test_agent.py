import pytest
from conftest import FakeClient, response, text_block, tool_block

from close_dreamer.agent import AgentRefused, run_agent
from close_dreamer.tools import FileTools
from close_dreamer.usage import UsageTracker


def run(client, tmp_path, **kw):
    return run_agent(
        client,
        model="claude-haiku-5-5",
        system="s",
        user_content="go",
        tools=FileTools(tmp_path),
        tracker=UsageTracker(),
        label="t",
        **kw,
    )


def test_parallel_tool_results_go_back_in_one_message(tmp_path):
    def script(kw):
        if len(kw["messages"]) == 1:
            return response(
                [tool_block("glob", {"pattern": "*"}, "a"), tool_block("grep", {"pattern": "x"}, "b")], stop="tool_use"
            )
        last = kw["messages"][-1]["content"]
        assert [r["tool_use_id"] for r in last] == ["a", "b"]
        return response([text_block("ok")])

    assert run(FakeClient(script), tmp_path).text == "ok"


def test_tool_errors_are_returned_not_raised(tmp_path):
    def script(kw):
        if len(kw["messages"]) == 1:
            return response([tool_block("read", {"path": "/etc/passwd"}, "a")], stop="tool_use")
        assert kw["messages"][-1]["content"][0]["is_error"] is True
        return response([text_block("handled")])

    assert run(FakeClient(script), tmp_path).text == "handled"


def test_refusal_raises(tmp_path):
    with pytest.raises(AgentRefused):
        run(FakeClient(lambda kw: response([], stop="refusal")), tmp_path)


def test_turn_limit(tmp_path):
    client = FakeClient(lambda kw: response([tool_block("glob", {"pattern": "*"}, "a")], stop="tool_use"))
    out = run(client, tmp_path, max_turns=3)
    assert out.hit_turn_limit and len(client.calls) == 3


def test_max_tokens_without_tool_call_continues(tmp_path):
    def script(kw):
        if len(kw["messages"]) == 1:
            return response([text_block("partial")], stop="max_tokens")
        return response([text_block("finished")])

    assert run(FakeClient(script), tmp_path).text == "finished"


def test_usage_and_cost_use_long_prompt_rates_over_100k(tmp_path):
    tracker = UsageTracker()
    client = FakeClient(lambda kw: response([text_block("x")], inp=1_000_000, out=100_000, cr=1_000_000))
    run_agent(
        client,
        model="claude-haiku-5-5",
        system="s",
        user_content="go",
        tools=FileTools(tmp_path),
        tracker=tracker,
        label="t",
    )
    t = tracker.by_label["t"]
    assert t.requests == 1 and t.input == 1_000_000
    # a 2M-token prompt is priced at Haiku 5.5's long-prompt rates
    assert tracker.total_usd == pytest.approx((1e6 * 0.50 + 1e5 * 2.50 + 1e6 * 0.05) / 1e6)


def test_short_prompt_rates():
    tracker = UsageTracker()
    from conftest import usage

    tracker.add("t", "claude-haiku-5-5", usage(inp=10_000, out=1_000, cw=0, cr=50_000))
    assert tracker.total_usd == pytest.approx((10_000 * 0.10 + 1_000 * 0.50 + 50_000 * 0.01) / 1e6)
