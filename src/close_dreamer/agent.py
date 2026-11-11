"""A small, explicit agent loop over the Messages API with client-side file tools.

This is the loop the Managed Agents platform runs for you in the cookbook. Writing it out keeps every
mechanic visible: the request, the tool calls, the tool results going back, prompt caching of the
growing conversation, the stop reasons, and the cost of each turn.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .tools import FileTools
from .usage import UsageTracker

MAX_TOKENS = 16_000


class AgentRefused(RuntimeError):
    pass


@dataclass
class AgentResult:
    text: str
    turns: int
    stop_reason: str
    hit_turn_limit: bool = False


def run_agent(
    client,
    *,
    model: str,
    system: str,
    user_content: str | list,
    tools: FileTools,
    tracker: UsageTracker,
    label: str,
    max_turns: int = 30,
    effort: str | None = None,
    on_event: Callable[[str], None] | None = None,
) -> AgentResult:
    """Run one agent until it stops calling tools (or hits max_turns). Raises BudgetExceeded via the
    tracker when the run's budget is spent, and AgentRefused on a refusal stop."""
    messages: list[dict] = [{"role": "user", "content": user_content}]
    extra = {"output_config": {"effort": effort}} if effort else {}
    log = on_event or (lambda _msg: None)
    text, stop = "", ""

    for turn in range(1, max_turns + 1):
        response = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=system,
            tools=tools.definitions(),
            messages=messages,
            # Automatic prompt caching: the API caches the conversation up to its last cacheable block,
            # so the transcript and earlier turns are read from cache (about a tenth of the input price)
            # on every later turn instead of being paid for again.
            cache_control={"type": "ephemeral"},
            **extra,
        )
        tracker.add(label, model, response.usage)
        stop = response.stop_reason or ""
        # Append the whole content (thinking blocks included, unchanged) so the next turn is valid.
        messages.append({"role": "assistant", "content": response.content})
        texts = [b.text for b in response.content if getattr(b, "type", "") == "text"]
        if texts:
            text = "\n".join(texts).strip()

        if stop == "refusal":
            details = getattr(response, "stop_details", None)
            raise AgentRefused(f"{label}: the model declined ({getattr(details, 'category', None)})")
        if stop == "pause_turn":
            continue

        tool_uses = [b for b in response.content if getattr(b, "type", "") == "tool_use"]
        if not tool_uses:
            if stop == "max_tokens":
                messages.append({"role": "user", "content": "You hit the output limit. Continue where you stopped."})
                continue
            return AgentResult(text=text, turns=turn, stop_reason=stop)

        results = []
        for block in tool_uses:
            args = block.input if isinstance(block.input, dict) else {}
            out, is_error = tools.call(block.name, args)
            log(f"[{label}] {block.name} {_brief(args)}{' -> error' if is_error else ''}")
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": out, "is_error": is_error})
        # All results from one assistant turn go back together in a single user message.
        messages.append({"role": "user", "content": results})

    return AgentResult(text=text, turns=max_turns, stop_reason=stop, hit_turn_limit=True)


def _brief(args: dict) -> str:
    keys = ("path", "pattern")
    shown = [f"{k}={args[k]!r}" for k in keys if k in args]
    return " ".join(shown)
