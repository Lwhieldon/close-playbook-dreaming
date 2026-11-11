import pytest

from close_dreamer.tools import FileTools


@pytest.fixture
def fs(tmp_path):
    return FileTools(tmp_path / "mem", mount="/memory")


def test_write_read_edit_roundtrip(fs):
    assert fs.call("write", {"path": "/memory/a.md", "content": "one\ntwo\n"})[1] is False
    text, err = fs.call("read", {"path": "/memory/a.md"})
    assert not err and "1\tone" in text
    _, err = fs.call("edit", {"path": "/memory/a.md", "old_string": "two", "new_string": "three"})
    assert not err
    assert "three" in fs.call("read", {"path": "a.md"})[0]


@pytest.mark.parametrize("path", ["/memory/../escape.md", "../escape.md", "/etc/passwd", "/memory/x/../../y.md"])
def test_paths_cannot_escape_the_root(fs, path):
    text, err = fs.call("write", {"path": path, "content": "x"})
    assert err and "outside" in text


def test_read_only_refuses_writes_and_hides_write_tools(tmp_path):
    ro = FileTools(tmp_path, mount="/playbook", read_only=True)
    names = {d["name"] for d in ro.definitions()}
    assert names == {"read", "glob", "grep"}
    text, err = ro.call("write", {"path": "/playbook/a.md", "content": "x"})
    assert err


def test_edit_requires_unique_match(fs):
    fs.call("write", {"path": "a.md", "content": "x x"})
    text, err = fs.call("edit", {"path": "a.md", "old_string": "x", "new_string": "y"})
    assert err and "2 times" in text
    _, err = fs.call("edit", {"path": "a.md", "old_string": "x", "new_string": "y", "replace_all": True})
    assert not err


def test_glob_and_grep(fs):
    fs.call("write", {"path": "gr-ir/allied.md", "content": "Vendor 300457 invoices in BX"})
    fs.call("write", {"path": "_index.md", "content": "[[allied]]"})
    assert "/memory/gr-ir/allied.md" in fs.call("glob", {"pattern": "**/*.md"})[0]
    assert "/memory/_index.md" in fs.call("glob", {"pattern": "*.md"})[0]
    hits = fs.call("grep", {"pattern": "300457"})[0]
    assert "allied.md:1" in hits


def test_size_cap(fs):
    text, err = fs.call("write", {"path": "big.md", "content": "x" * 100_001})
    assert err and "100,000" in text


def test_bad_arguments_are_errors_not_crashes(fs):
    text, err = fs.call("read", {"nope": 1})
    assert err
