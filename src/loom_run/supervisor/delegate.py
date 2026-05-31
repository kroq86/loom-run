from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from loom_run.agents.chat_agent import build_runner_with_settings, make_initial_state
from loom_run.config import Settings

ToolFn = Callable[..., Awaitable[dict[str, Any]]]

DEFAULT_CHILD_MAX_STEPS = 20


def make_delegate_tool(
    db_path: str,
    settings: Settings,
    *,
    child_max_steps: int = DEFAULT_CHILD_MAX_STEPS,
) -> ToolFn:
    async def delegate_subagent(
        *,
        parent_run_id: str,
        agent_name: str,
        message: str,
    ) -> dict[str, Any]:
        child_run_id = f"{parent_run_id}:sub:{agent_name}"
        runner = build_runner_with_settings(db_path, settings)
        state = make_initial_state(message, max_tool_calls=settings.max_tool_calls)
        result = await runner.start(
            run_id=child_run_id,
            initial_state=state,
            max_steps=1,
        )
        remaining = child_max_steps - 1
        while result.status == "paused" and remaining > 0:
            result = await runner.resume(run_id=child_run_id, max_steps=1)
            remaining -= 1

        if result.status == "completed" and result.result is not None:
            answer = str(result.result.get("answer", ""))
            return {
                "success": True,
                "result_type": "subagent_delegate",
                "payload": {
                    "run_id": child_run_id,
                    "agent_name": agent_name,
                    "status": result.status,
                    "answer": answer,
                },
            }

        return {
            "success": False,
            "is_error": True,
            "result_type": "subagent_delegate",
            "payload": {
                "run_id": child_run_id,
                "agent_name": agent_name,
                "status": result.status,
                "answer": None,
            },
        }

    return delegate_subagent
