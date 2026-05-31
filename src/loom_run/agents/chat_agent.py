from __future__ import annotations

from typing import Any

from loom_agent import AgentRunner, SQLiteCheckpointStore

from loom_run.config import Settings, load_settings
from loom_run.coordinator.llm_impl import create_llm
from loom_run.coordinator.step import make_step
from loom_run.state import (
    ChatState,
    decode_result,
    decode_state,
    encode_result,
    encode_state,
)
from loom_run.tools.build_registry import build_tool_registry


def initial_state() -> ChatState:
    settings = load_settings()
    messages = ()
    if settings.user_message:
        from loom_run.state import Message

        messages = (Message(role="user", content=settings.user_message),)
    return ChatState(
        user_message=settings.user_message,
        messages=messages,
        tool_calls_used=0,
        max_tool_calls=settings.max_tool_calls,
        final_answer=None,
        phase="think",
    )


def build_runner(db_path: str) -> AgentRunner[ChatState, dict[str, Any]]:
    settings = load_settings()
    registry = build_tool_registry(settings)
    llm = create_llm(
        mock_llm=settings.mock_llm,
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_model,
    )
    step = make_step(llm, registry)
    return AgentRunner(
        step=step,
        store=SQLiteCheckpointStore(db_path),
        encode_state=encode_state,
        decode_state=decode_state,
        encode_result=encode_result,
        decode_result=decode_result,
        tools=registry,
    )


def make_initial_state(user_message: str, *, max_tool_calls: int | None = None) -> ChatState:
    settings = load_settings()
    from loom_run.state import Message

    limit = max_tool_calls if max_tool_calls is not None else settings.max_tool_calls
    messages = (Message(role="user", content=user_message),) if user_message else ()
    return ChatState(
        user_message=user_message,
        messages=messages,
        tool_calls_used=0,
        max_tool_calls=limit,
        final_answer=None,
        phase="think",
    )


def build_runner_with_settings(
    db_path: str,
    settings: Settings,
    *,
    registry=None,
) -> AgentRunner[ChatState, dict[str, Any]]:
    from loom_agent.tools import ToolRegistry

    reg = registry or build_tool_registry(settings)
    llm = create_llm(
        mock_llm=settings.mock_llm,
        openai_api_key=settings.openai_api_key,
        openai_model=settings.openai_model,
    )
    step = make_step(llm, reg)
    return AgentRunner(
        step=step,
        store=SQLiteCheckpointStore(db_path),
        encode_state=encode_state,
        decode_state=decode_state,
        encode_result=encode_result,
        decode_result=decode_result,
        tools=reg,
    )
