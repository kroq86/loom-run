from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from loom_run.agents.chat_agent import build_runner_with_settings
from loom_run.agents.supervisor_agent import (
    build_supervisor_runner,
    make_supervisor_initial_state,
)
from loom_run.config import Settings


@pytest.fixture
def supervisor_settings(tmp_path: Path) -> Settings:
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
async def test_supervisor_delegates_and_completes(supervisor_settings: Settings) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = str(Path(tmp) / "runs.sqlite")
        runner = build_supervisor_runner(db, supervisor_settings)
        state = make_supervisor_initial_state("team-demo", "explain checkpoint policy")
        result = await runner.start(run_id="team-demo", initial_state=state, max_steps=10)

        assert result.status == "completed"
        assert result.result is not None
        assert "Supervisor merged" in result.result["answer"]

        child_run_id = "team-demo:sub:researcher"
        child_runner = build_runner_with_settings(db, supervisor_settings)
        child_explain = child_runner.explain_run(child_run_id)
        assert child_explain.tool_call_count >= 1


@pytest.mark.asyncio
async def test_supervisor_child_run_inspectable(supervisor_settings: Settings) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = str(Path(tmp) / "runs.sqlite")
        runner = build_supervisor_runner(db, supervisor_settings)
        state = make_supervisor_initial_state("team-demo", "explain checkpoint policy")
        await runner.start(run_id="team-demo", initial_state=state, max_steps=10)

        child_run_id = "team-demo:sub:researcher"
        child_runner = build_runner_with_settings(db, supervisor_settings)
        explanation = child_runner.explain_run(child_run_id)
        assert explanation.run_id == child_run_id
        assert explanation.tool_call_count >= 1
        assert explanation.status == "completed"
