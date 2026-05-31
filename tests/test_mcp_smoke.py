from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from loom_run.tools.mcp_stdio import McpStdioClient, load_mcp_config


@pytest.fixture
def ci_mcp_config_path(tmp_path: Path) -> Path:
    """Build MCP config pointing at the in-repo mock stdio server."""
    repo_root = Path(__file__).resolve().parents[1]
    mock_server = repo_root / "tests" / "fixtures" / "mock_mcp_server.py"
    template = json.loads((repo_root / "tests" / "mcp.servers.ci.json").read_text(encoding="utf-8"))
    entry = template["mock-verifier"]
    entry["command"] = sys.executable
    entry["args"] = [str(mock_server)]
    config_path = tmp_path / "mcp.servers.json"
    config_path.write_text(json.dumps(template, indent=2), encoding="utf-8")
    return config_path


@pytest.mark.asyncio
async def test_mock_mcp_initialize_and_call(ci_mcp_config_path: Path) -> None:
    configs = load_mcp_config(str(ci_mcp_config_path))
    client = McpStdioClient(configs["mock-verifier"])
    try:
        result = await client.call_tool("run_tests", {"path": "."})
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert result.get("payload", {}).get("tool") == "run_tests"
    finally:
        await client.close()


@pytest.mark.skipif(not os.getenv("LOOM_RUN_MCP_CONFIG"), reason="MCP config not set")
@pytest.mark.asyncio
async def test_external_mcp_config_loads() -> None:
    configs = load_mcp_config(os.environ["LOOM_RUN_MCP_CONFIG"])
    assert configs
