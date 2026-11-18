import re

import pytest
from conftest import FakeClient, response, text_block, tool_block

from close_dreamer import config
from close_dreamer import transcripts as tx
from close_dreamer.config import Models
from close_dreamer.dream import dream, parse_json_line
from close_dreamer.usage import BudgetExceeded

ASSIGNED = re.compile(r"assigned source is (.+?)\. Dream over")


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:60]


def scripted_dreamer(kwargs):
    """Analyzer: write one page per source, then stop. Organizer: glob, write _index.md, report JSON."""
    msgs = kwargs["messages"]
    system = kwargs["system"]
    turn = (len(msgs) + 1) // 2
    if "memory maintenance agent" in system:
        name = ASSIGNED.search(msgs[0]["content"]).group(1)
        s = slug(name)
        if turn == 1:
            page = f"---\nname: {s}\ndescription: Facts from {name}\n---\nDistilled from {name}.\n"
            return response(
                [tool_block("write", {"path": f"/memory/{s}.md", "content": page}, f"w-{s}")], stop="tool_use", cw=3000
            )
        return response([text_block(f"Recorded {name}.")], cr=3000)
    assert "organizer" in system
    if turn == 1:
        return response([tool_block("glob", {"pattern": "**/*.md"}, "g1")], stop="tool_use")
    if turn == 2:
        listing = msgs[-1]["content"][0]["content"]
        slugs = re.findall(r"/memory/(\S+)\.md", listing)
        index = "## Close\n" + "".join(f"[[{s}]] - page\n" for s in slugs if s != "_index")
        return response(
            [tool_block("write", {"path": "/memory/_index.md", "content": index}, "w-idx")], stop="tool_use"
        )
    return response([text_block('{"index_entries": 6, "changes": ["built index"]}')])


@pytest.fixture
def may():
    return tx.select(tx.load(config.CORPUS), through="2026-05", after="2026-04")


def test_dream_builds_a_clean_playbook(tmp_path, may):
    client = FakeClient(scripted_dreamer)
    pb = tmp_path / "playbook"
    result = dream(client, may, pb, tmp_path / "snaps", models=Models(), budget_usd=1.0, concurrency=3, on_event=None)
    assert not result.failures
    assert set(result.analyzer_summaries) == {t.name for t in may}
    assert result.organizer == {"index_entries": 6, "changes": ["built index"]}
    assert result.lint.ok, result.lint.summary()
    assert len(result.changes["added"]) == len(may) + 1  # pages + _index.md
    assert result.snapshot.exists()
    # every request asks for automatic prompt caching; the source travels inline with its kind and period
    assert all(c.get("cache_control") == {"type": "ephemeral"} for c in client.calls)
    first = next(c for c in client.calls if "JE_Register_2026-05.xlsx" in str(c["messages"][0]["content"]))
    assert 'kind="erp" close_period="2026-05"' in first["messages"][0]["content"]
    assert "5105599102" in first["messages"][0]["content"]
    assert result.usage.by_label["analyzer"].requests == 2 * len(may)


def test_periods_in_order_and_erp_after_discussion(tmp_path):
    order = []

    def script(kwargs):
        if "memory maintenance agent" in kwargs["system"]:
            order.append(ASSIGNED.search(kwargs["messages"][0]["content"]).group(1))
            return response([text_block("nothing new")])
        return response([text_block('{"index_entries": 0, "changes": []}')])

    corpus = tx.load(config.CORPUS)
    chosen = tx.select(corpus, through="2026-07")
    dream(FakeClient(script), chosen, tmp_path / "pb", tmp_path / "s", budget_usd=2.0, concurrency=4, on_event=None)
    by_name = {t.name: t for t in corpus}
    keys = [(by_name[n].period, by_name[n].kind == "erp") for n in order]
    assert keys == sorted(keys), "each period's discussion and policy first, then its ERP evidence"


def test_budget_stops_the_run(tmp_path, may):
    def expensive(kwargs):
        return response([text_block("done")], inp=50_000_000)  # far over $1 in one request

    with pytest.raises(BudgetExceeded):
        dream(FakeClient(expensive), may, tmp_path / "pb", tmp_path / "s", budget_usd=1.0, concurrency=1, on_event=None)


def test_estimate_over_budget_sends_nothing(tmp_path, may):
    client = FakeClient(lambda kw: pytest.fail("no request should be sent"))
    with pytest.raises(ValueError, match="over the budget"):
        dream(client, may, tmp_path / "pb", tmp_path / "s", budget_usd=0.0001, on_event=None)


def test_parse_json_line_tolerates_wrapping():
    wrapped = 'Done.\n```json\n{"index_entries": 3, "changes": []}\n```'
    assert parse_json_line(wrapped) == {"index_entries": 3, "changes": []}
    assert parse_json_line("no json")["index_entries"] is None
