from __future__ import annotations

from pathlib import Path

import pytest

from loom_agent.tools import ToolRegistry

from loom_run.config import Settings
from loom_run.tools.local import register_local_tools


@pytest.fixture
def tool_registry(tmp_path: Path) -> ToolRegistry:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("loom-runner checkpoint resume policy details", encoding="utf-8")
    (tmp_path / "README.md").write_text("# project", encoding="utf-8")
    settings = Settings(
        workspace=tmp_path,
        mock_llm=True,
        openai_api_key=None,
        openai_model="gpt-4o-mini",
        max_tool_calls=3,
        user_message="",
        mcp_config_path=None,
    )
    registry = ToolRegistry()
    register_local_tools(registry, settings)
    return registry


@pytest.mark.asyncio
async def test_read_file_success(tool_registry: ToolRegistry) -> None:
    result = await tool_registry.call_result("read_file", path="README.md")
    assert result.success is True
    assert "project" in result.payload["content"]


@pytest.mark.asyncio
async def test_read_file_path_escape_raises(tool_registry: ToolRegistry) -> None:
    with pytest.raises(PermissionError, match="path escapes workspace"):
        await tool_registry.call("read_file", path="../outside.txt")


@pytest.mark.asyncio
async def test_read_file_missing_raises(tool_registry: ToolRegistry) -> None:
    with pytest.raises(FileNotFoundError):
        await tool_registry.call("read_file", path="missing.txt")


@pytest.mark.asyncio
async def test_search_docs_finds_match(tool_registry: ToolRegistry) -> None:
    result = await tool_registry.call_result("search_docs", query="checkpoint")
    matches = result.payload["matches"]
    assert len(matches) >= 1
    assert any("guide.md" in match["path"] for match in matches)


@pytest.mark.asyncio
async def test_search_docs_no_matches(tool_registry: ToolRegistry) -> None:
    result = await tool_registry.call_result("search_docs", query="zzzznotfound9999")
    assert result.payload["matches"] == []


@pytest.mark.asyncio
async def test_run_tests_runs_pytest(tool_registry: ToolRegistry, tmp_path: Path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_ok.py").write_text("def test_passes():\n    assert True\n", encoding="utf-8")
    result = await tool_registry.call_result("run_tests", path="tests")
    assert result.success is True
    assert result.payload["exit_code"] == 0
