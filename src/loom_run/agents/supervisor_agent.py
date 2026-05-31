from __future__ import annotations

from typing import Any

from loom_agent import AgentRunner, SQLiteCheckpointStore
from loom_agent.tools import ToolRegistry

from loom_run.config import Settings, load_settings
from loom_run.state import Message
from loom_run.supervisor.delegate import make_delegate_tool
from loom_run.supervisor.llm_impl import MockSupervisorLLM
from loom_run.supervisor.state import (
    SupervisorState,
    decode_result,
    decode_state,
    encode_result,
    encode_state,
)
from loom_run.supervisor.step import make_supervisor_step


def make_supervisor_initial_state(
    run_id: str,
    user_message: str,
    *,
    max_tool_calls: int | None = None,
) -> SupervisorState:
    settings = load_settings()
    limit = max_tool_calls if max_tool_calls is not None else settings.max_tool_calls
    messages = (Message(role="user", content=user_message),) if user_message else ()
    return SupervisorState(
        run_id=run_id,
        user_message=user_message,
        messages=messages,
        tool_calls_used=0,
        max_tool_calls=limit,
        final_answer=None,
        phase="think",
    )


def build_supervisor_runner(
    db_path: str,
    settings: Settings,
    *,
    child_max_steps: int = 20,
) -> AgentRunner[SupervisorState, dict[str, Any]]:
    registry = ToolRegistry()
    registry.register(
        "delegate_subagent",
        make_delegate_tool(db_path, settings, child_max_steps=child_max_steps),
    )
    llm = MockSupervisorLLM()
    step = make_supervisor_step(llm, registry)
    return AgentRunner(
        step=step,
        store=SQLiteCheckpointStore(db_path),
        encode_state=encode_state,
        decode_state=decode_state,
        encode_result=encode_result,
        decode_result=decode_result,
        tools=registry,
    )
