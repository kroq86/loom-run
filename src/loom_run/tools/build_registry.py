from __future__ import annotations

import json
from pathlib import Path

from loom_agent.tools import ToolRegistry

from loom_run.config import Settings
from loom_run.tools.local import register_local_tools
from loom_run.tools.mcp_stdio import McpStdioClient, load_mcp_config

_clients: list[McpStdioClient] = []


def build_tool_registry(settings: Settings) -> ToolRegistry:
    registry = ToolRegistry()
    register_local_tools(registry, settings)

    if settings.mcp_config_path and settings.mcp_config_path.is_file():
        _register_mcp_tools(registry, settings.mcp_config_path)

    return registry


def _register_mcp_tools(registry: ToolRegistry, config_path: Path) -> None:
    servers = load_mcp_config(str(config_path))
    for server_cfg in servers.values():
        mcp = McpStdioClient(server_cfg)
        _clients.append(mcp)
        for loom_name, mcp_name in server_cfg.tool_map.items():
            _wrap_mcp_tool(registry, loom_name, mcp, mcp_name)


def _wrap_mcp_tool(
    registry: ToolRegistry,
    loom_name: str,
    client: McpStdioClient,
    mcp_name: str,
) -> None:
    if loom_name in registry.names():
        return

    async def _call(**kwargs: object) -> dict:
        result = await client.call_tool(mcp_name, dict(kwargs))
        if isinstance(result, dict) and "success" in result:
            return result
        return {
            "success": True,
            "result_type": "mcp_tool",
            "payload": result if isinstance(result, dict) else {"value": result},
        }

    registry.register(loom_name, _call)


async def shutdown_mcp_clients() -> None:
    for client in _clients:
        await client.close()
    _clients.clear()


def read_mcp_config_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
