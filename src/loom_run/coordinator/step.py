from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from loom_agent import Complete, Continue, RunContext

from loom_agent.tools import ToolRegistry

from loom_run.coordinator.llm import BUDGET_EXCEEDED_MSG, LLMClient
from loom_run.state import ChatState, Message


StepFn = Callable[[ChatState, RunContext], Awaitable[Continue[ChatState] | Complete[dict[str, Any]]]]


def make_step(llm: LLMClient, tools: ToolRegistry) -> StepFn:
    async def step(state: ChatState, ctx: RunContext) -> Continue[ChatState] | Complete[dict]:
        if state.phase == "done" and state.final_answer is not None:
            return Complete({"answer": state.final_answer, "tool_calls_used": state.tool_calls_used})

        if state.tool_calls_used >= state.max_tool_calls:
            return Complete(
                {
                    "answer": BUDGET_EXCEEDED_MSG,
                    "tool_calls_used": state.tool_calls_used,
                }
            )

        reply = await llm.decide(state, tool_names=tools.names())

        if reply.action == "finish":
            answer = reply.finish.answer if reply.finish else ""
            done = ChatState(
                user_message=state.user_message,
                messages=state.messages + (Message(role="assistant", content=answer),),
                tool_calls_used=state.tool_calls_used,
                max_tool_calls=state.max_tool_calls,
                final_answer=answer,
                phase="done",
            )
            return Complete({"answer": answer, "tool_calls_used": state.tool_calls_used})

        tool_call = reply.tool_call
        if tool_call is None:
            return Complete({"answer": "LLM returned tool_call without payload", "tool_calls_used": state.tool_calls_used})

        payload = await ctx.call_tool(tool_call.name, **tool_call.arguments)
        tool_text = _format_tool_payload(payload)
        next_state = ChatState(
            user_message=state.user_message,
            messages=state.messages
            + (
                Message(role="assistant", content=f"tool:{tool_call.name}"),
                Message(role="tool", content=tool_text, tool_name=tool_call.name),
            ),
            tool_calls_used=state.tool_calls_used + 1,
            max_tool_calls=state.max_tool_calls,
            final_answer=None,
            phase="think",
        )
        return Continue(next_state)

    return step


def _format_tool_payload(payload: object) -> str:
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        matches = payload.get("matches")
        if isinstance(matches, list) and matches:
            first = matches[0]
            if isinstance(first, dict):
                snippet = first.get("snippet") or first.get("content") or str(first)
                return str(snippet)[:2000]
        return str(payload)[:2000]
    return str(payload)[:2000]
