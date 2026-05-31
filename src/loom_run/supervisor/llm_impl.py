from __future__ import annotations

from loom_run.coordinator.llm import LLMFinish, LLMReply, LLMToolCall
from loom_run.supervisor.state import SupervisorState


class MockSupervisorLLM:
    """Deterministic scenario: delegate to researcher subagent, then merge."""

    async def decide(self, state: SupervisorState, *, tool_names: list[str]) -> LLMReply:
        if state.tool_calls_used == 0 and "delegate_subagent" in tool_names:
            return LLMReply(
                action="tool_call",
                tool_call=LLMToolCall(
                    name="delegate_subagent",
                    arguments={
                        "parent_run_id": state.run_id,
                        "agent_name": "researcher",
                        "message": state.user_message or "loom stack",
                    },
                ),
            )
        child_answer = _last_tool_answer(state)
        return LLMReply(
            action="finish",
            finish=LLMFinish(answer=f"Supervisor merged: {child_answer}"),
        )


def _last_tool_answer(state: SupervisorState) -> str:
    tool_msgs = [m for m in state.messages if m.role == "tool"]
    if tool_msgs:
        return tool_msgs[-1].content[:500]
    return "No subagent output."
