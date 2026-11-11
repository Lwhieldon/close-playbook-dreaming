"""Shared test helpers: a scripted stand-in for the Anthropic client (no network, no key)."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def text_block(text):
    return SimpleNamespace(type="text", text=text)


def tool_block(name, args, id_):
    return SimpleNamespace(type="tool_use", name=name, input=args, id=id_)


def usage(inp=1000, out=200, cw=0, cr=0):
    return SimpleNamespace(
        input_tokens=inp, output_tokens=out, cache_creation_input_tokens=cw, cache_read_input_tokens=cr
    )


def response(blocks, stop="end_turn", **u):
    return SimpleNamespace(content=blocks, stop_reason=stop, usage=usage(**u), stop_details=None)


class FakeClient:
    """messages.create(**kwargs) returns whatever `script(kwargs)` returns; every call is recorded."""

    def __init__(self, script):
        self.calls = []
        self._script = script
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return self._script(kwargs)


@pytest.fixture
def bad_playbook():
    return ROOT / "tests" / "fixtures" / "playbook_bad"
