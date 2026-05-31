from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import asdict
from typing import Any

from pydantic import BaseModel, Field

from loom_run.agents.chat_agent import build_runner_with_settings, make_initial_state
from loom_run.config import Settings


class ChatRequest(BaseModel):
    message: str
    run_id: str
    max_steps: int = Field(default=20, ge=1)
    max_tool_calls: int | None = None


def create_app(db_path: str, settings: Settings) -> Any:
    try:
        from fastapi import FastAPI
        from fastapi.responses import StreamingResponse
    except ImportError as exc:
        raise RuntimeError("install loom-run with api extra: pip install 'loom-run[api]'") from exc

    app = FastAPI(title="loom-run", version="0.2.1")
    runner = build_runner_with_settings(db_path, settings)

    async def chat_events(body: ChatRequest) -> AsyncIterator[str]:
        state = make_initial_state(body.message, max_tool_calls=body.max_tool_calls)
        yield _format_sse("started", {"run_id": body.run_id, "message": body.message})

        remaining = body.max_steps
        result = await runner.start(run_id=body.run_id, initial_state=state, max_steps=1)
        remaining -= 1
        yield _format_sse("step", _result_payload(result))

        while result.status == "paused" and remaining > 0:
            result = await runner.resume(run_id=body.run_id, max_steps=1)
            remaining -= 1
            yield _format_sse("step", _result_payload(result))

        if result.status == "completed":
            yield _format_sse("completed", _result_payload(result))
        elif result.status == "paused":
            yield _format_sse("paused", _result_payload(result))
        else:
            yield _format_sse("error", _result_payload(result))

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/chat")
    async def chat(body: ChatRequest) -> StreamingResponse:
        return StreamingResponse(chat_events(body), media_type="text/event-stream")

    return app


def _result_payload(result: Any) -> dict[str, Any]:
    data = asdict(result)
    if data.get("result") is not None:
        data["result"] = dict(data["result"])
    return data


def _format_sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"
