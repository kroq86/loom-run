from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from flow_xray import trace

from loom_run.agents.chat_agent import build_runner_with_settings, make_initial_state
from loom_run.config import Settings, load_settings


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "serve":
        return _run_serve(args)
    settings = _settings_from_args(args)
    runner = build_runner_with_settings(args.db, settings)

    async def execute() -> Any:
        if args.command == "chat":
            state = make_initial_state(args.message, max_tool_calls=args.max_tool_calls)
            return await runner.start(
                run_id=args.run_id,
                initial_state=state,
                max_steps=args.max_steps,
            )
        if args.command == "resume":
            return await runner.resume(run_id=args.run_id, max_steps=args.max_steps)
        if args.command == "explain":
            return runner.explain_run(args.run_id)
        raise ValueError(f"unknown command: {args.command}")

    if args.trace:
        result = trace.run(lambda: asyncio.run(execute()))
        result.to_html(args.trace)
        payload = result.return_value
    else:
        payload = asyncio.run(execute())

    print(json.dumps(_to_jsonable(payload), sort_keys=True, default=str))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="loom-run")
    sub = parser.add_subparsers(dest="command", required=True)

    chat = sub.add_parser("chat", help="Start a durable chat run")
    _add_common_args(chat)
    chat.add_argument("message")
    chat.add_argument("--run-id", required=True)
    chat.add_argument("--max-steps", type=int, default=20)
    chat.add_argument("--trace")

    resume = sub.add_parser("resume", help="Resume a chat run")
    _add_common_args(resume)
    resume.add_argument("--run-id", required=True)
    resume.add_argument("--max-steps", type=int, default=20)
    resume.add_argument("--trace")

    explain = sub.add_parser("explain", help="Explain a chat run")
    _add_common_args(explain)
    explain.add_argument("--run-id", required=True)

    serve = sub.add_parser("serve", help="Start HTTP server with SSE /chat")
    _add_common_args(serve)
    serve.add_argument("--host", default=os.environ.get("LOOM_RUN_HOST", "127.0.0.1"))
    serve.add_argument("--port", type=int, default=int(os.environ.get("LOOM_RUN_PORT", "8765")))

    return parser.parse_args(argv)


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db", default=os.environ.get("LOOM_RUN_DB", "runs.sqlite"))
    parser.add_argument("--mock-llm", action="store_true", default=False)
    parser.add_argument("--max-tool-calls", type=int, default=None)
    parser.add_argument("--mcp-config", default=os.environ.get("LOOM_RUN_MCP_CONFIG"))
    parser.add_argument("--workspace", default=os.environ.get("LOOM_RUN_WORKSPACE"))


def _settings_from_args(args: argparse.Namespace) -> Settings:
    if args.workspace:
        os.environ["LOOM_RUN_WORKSPACE"] = str(Path(args.workspace).resolve())
    if args.mcp_config:
        os.environ["LOOM_RUN_MCP_CONFIG"] = str(Path(args.mcp_config).resolve())
    if args.max_tool_calls is not None:
        os.environ["LOOM_RUN_MAX_TOOL_CALLS"] = str(args.max_tool_calls)
    if args.command == "chat":
        os.environ["LOOM_RUN_USER_MESSAGE"] = args.message
    if getattr(args, "mock_llm", False):
        os.environ["LOOM_RUN_MOCK_LLM"] = "1"
    settings = load_settings()
    if args.command == "chat" and not settings.user_message:
        settings = Settings(
            workspace=settings.workspace,
            mock_llm=settings.mock_llm,
            openai_api_key=settings.openai_api_key,
            openai_model=settings.openai_model,
            max_tool_calls=args.max_tool_calls or settings.max_tool_calls,
            user_message=args.message,
            mcp_config_path=settings.mcp_config_path,
        )
    return settings


def _run_serve(args: argparse.Namespace) -> int:
    if args.workspace:
        os.environ["LOOM_RUN_WORKSPACE"] = str(Path(args.workspace).resolve())
    if args.mcp_config:
        os.environ["LOOM_RUN_MCP_CONFIG"] = str(Path(args.mcp_config).resolve())
    if getattr(args, "mock_llm", False):
        os.environ["LOOM_RUN_MOCK_LLM"] = "1"
    settings = load_settings()
    try:
        import uvicorn
    except ImportError as exc:
        raise SystemExit("install api extra: pip install 'loom-run[api]'") from exc
    from loom_run.http import create_app

    app = create_app(args.db, settings)
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    return 0


def _to_jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        from dataclasses import asdict

        return asdict(value)
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    return value


if __name__ == "__main__":
    raise SystemExit(main())
