#!/usr/bin/env python3
"""Minimal stdio MCP server for CI smoke tests."""

from __future__ import annotations

import json
import sys


def _respond(req_id: int, result: object) -> None:
    print(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}), flush=True)


def _error(req_id: int, message: str) -> None:
    print(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": message},
            }
        ),
        flush=True,
    )


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        message = json.loads(line)
        if "id" not in message:
            continue
        req_id = message["id"]
        method = message.get("method")
        if method == "initialize":
            _respond(
                req_id,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "serverInfo": {"name": "loom-run-mock-mcp", "version": "0.1.0"},
                },
            )
            continue
        if method == "tools/call":
            params = message.get("params", {})
            tool_name = str(params.get("name", ""))
            payload = {
                "success": True,
                "result_type": "mock_mcp",
                "payload": {"tool": tool_name, "arguments": params.get("arguments", {})},
            }
            _respond(req_id, {"content": [{"type": "text", "text": json.dumps(payload)}]})
            continue
        _error(req_id, f"unsupported method: {method}")


if __name__ == "__main__":
    main()
