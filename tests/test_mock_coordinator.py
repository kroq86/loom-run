from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from loom_run.agents.chat_agent import build_runner_with_settings, make_initial_state
from loom_run.config import Settings


@pytest.fixture
def mock_settings(tmp_path: Path) -> Settings:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "loom.md").write_text("loom-runner checkpoint resume inspect policy", encoding="utf-8")
    return Settings(
        workspace=tmp_path,
        mock_llm=True,
        openai_api_key=None,
        openai_model="gpt-4o-mini",
        max_tool_calls=3,
        user_message="explain checkpoint policy",
        mcp_config_path=None,
    )


@pytest.mark.asyncio
async def test_mock_coordinator_completes(mock_settings: Settings) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = str(Path(tmp) / "runs.sqlite")
        runner = build_runner_with_settings(db, mock_settings)
        state = make_initial_state("explain checkpoint policy", max_tool_calls=3)
        result = await runner.start(run_id="demo", initial_state=state, max_steps=10)
        assert result.status == "completed"
        assert result.result is not None
        assert "answer" in result.result
        tool_calls = runner.get_tool_calls("demo")
        assert len(tool_calls) >= 1
        assert tool_calls[0].tool_name == "search_docs"


@pytest.mark.asyncio
async def test_resume_after_pause(mock_settings: Settings) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = str(Path(tmp) / "runs.sqlite")
        runner = build_runner_with_settings(db, mock_settings)
        state = make_initial_state("explain checkpoint policy", max_tool_calls=3)
        first = await runner.start(run_id="demo", initial_state=state, max_steps=1)
        assert first.status == "paused"
        second = await runner.resume(run_id="demo", max_steps=10)
        assert second.status == "completed"


@pytest.mark.asyncio
async def test_explain_run(mock_settings: Settings) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = str(Path(tmp) / "runs.sqlite")
        runner = build_runner_with_settings(db, mock_settings)
        state = make_initial_state("explain checkpoint policy", max_tool_calls=3)
        await runner.start(run_id="demo", initial_state=state, max_steps=10)
        explanation = runner.explain_run("demo")
        assert explanation.run_id == "demo"
        assert explanation.tool_call_count >= 1


@pytest.mark.skipif(not os.getenv("LOOM_RUN_MCP_CONFIG"), reason="MCP config not set")
@pytest.mark.asyncio
async def test_mcp_config_loads() -> None:
    from loom_run.tools.mcp_stdio import load_mcp_config

    configs = load_mcp_config(os.environ["LOOM_RUN_MCP_CONFIG"])
    assert configs
