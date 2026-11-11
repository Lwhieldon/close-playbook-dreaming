"""Paths, models and credentials."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "data"
CORPUS = DATA / "corpus"
TRANSCRIPTS = CORPUS  # older name
OUTPUT = REPO / "output"
PLAYBOOK = OUTPUT / "playbook"
SNAPSHOTS = OUTPUT / "snapshots"
RUNS = OUTPUT / "runs"

load_dotenv(REPO / ".env")


@dataclass(frozen=True)
class Models:
    # Defaults follow the cookbook: Haiku for the high-volume analyzers and the organizer. The answering
    # agent in the evaluation is Haiku too, so the comparison is about memory, not model strength; the
    # judge is Sonnet. Override any of them with the CLOSE_DREAMER_* environment variables.
    analyzer: str = os.getenv("CLOSE_DREAMER_ANALYZER_MODEL") or "claude-haiku-5-5"
    organizer: str = os.getenv("CLOSE_DREAMER_ORGANIZER_MODEL") or "claude-haiku-5-5"
    answer: str = os.getenv("CLOSE_DREAMER_ANSWER_MODEL") or "claude-haiku-5-5"
    judge: str = os.getenv("CLOSE_DREAMER_JUDGE_MODEL") or "claude-sonnet-5-5"


class MissingCredentials(RuntimeError):
    pass


def make_client():
    """An Anthropic client, or a clear error when no credentials are configured."""
    import anthropic

    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN") or os.getenv("ANTHROPIC_PROFILE")):
        # The SDK can also use an `ant auth login` profile; try it, and explain if nothing works.
        try:
            client = anthropic.Anthropic()
            client.models.retrieve("claude-haiku-5-5")
            return client
        except Exception as exc:  # noqa: BLE001 - any failure here means "not configured"
            raise MissingCredentials(
                "No Anthropic credentials found. Copy .env.example to .env and set ANTHROPIC_API_KEY "
                "(the .env file is gitignored), or run `ant auth login`."
            ) from exc
    return anthropic.Anthropic()
