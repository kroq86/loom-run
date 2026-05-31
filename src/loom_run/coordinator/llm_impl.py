from __future__ import annotations

import json

from loom_run.coordinator.llm import LLMClient, LLMReply, LLMToolCall, LLMFinish
from loom_run.state import ChatState, Message


class MockLLM(LLMClient):
    """Deterministic scenario: search_docs then finish."""

    async def decide(self, state: ChatState, *, tool_names: list[str]) -> LLMReply:
        if state.tool_calls_used == 0 and "search_docs" in tool_names:
            return LLMReply(
                action="tool_call",
                tool_call=LLMToolCall(
                    name="search_docs",
                    arguments={"query": state.user_message or "loom stack"},
                ),
            )
        summary = _summarize_transcript(state)
        return LLMReply(
            action="finish",
            finish=LLMFinish(answer=summary or "Done."),
        )


def _summarize_transcript(state: ChatState) -> str:
    tool_msgs = [m for m in state.messages if m.role == "tool"]
    if tool_msgs:
        return f"Based on tool output: {tool_msgs[-1].content[:500]}"
    return f"Answer for: {state.user_message}"


class OpenAIClient(LLMClient):
    def __init__(self, *, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    async def decide(self, state: ChatState, *, tool_names: list[str]) -> LLMReply:
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise RuntimeError("install loom-run with openai extra: pip install 'loom-run[openai]'") from exc

        client = AsyncOpenAI(api_key=self._api_key)
        prompt = _build_prompt(state, tool_names)
        response = await client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": state.user_message},
            ],
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        action = data.get("action")
        if action == "tool_call":
            return LLMReply(
                action="tool_call",
                tool_call=LLMToolCall(
                    name=str(data["name"]),
                    arguments=dict(data.get("arguments", {})),
                ),
            )
        return LLMReply(
            action="finish",
            finish=LLMFinish(answer=str(data.get("answer", ""))),
        )


def create_llm(*, mock_llm: bool, openai_api_key: str | None, openai_model: str) -> LLMClient:
    if mock_llm:
        return MockLLM()
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY required when LOOM_RUN_MOCK_LLM=0")
    return OpenAIClient(api_key=openai_api_key, model=openai_model)


def _build_prompt(state: ChatState, tool_names: list[str]) -> str:
    from loom_run.coordinator.llm import SYSTEM_PROMPT

    transcript = "\n".join(f"{m.role}: {m.content}" for m in state.messages)
    base = SYSTEM_PROMPT.format(tools=", ".join(tool_names) or "(none)")
    if transcript:
        return f"{base}\nTranscript so far:\n{transcript}"
    return base
