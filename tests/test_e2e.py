"""End-to-end tests: real subprocess invoking loom-run CLI."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from httpx import ASGITransport, AsyncClient

from loom_run.config import Settings
from loom_run.http import create_app


def _run_cli(db: str, workspace: str, *args: str) -> dict:
    cmd = [
        sys.executable,
        "-m",
        "loom_run.cli",
        *args,
        "--db",
        db,
        "--workspace",
        workspace,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert result.returncode == 0, (
        f"command failed: {' '.join(cmd)}\n"
        f"stderr:\n{result.stderr}\n"
        f"stdout:\n{result.stdout}"
    )
    return json.loads(result.stdout)


def test_e2e_chat_completes(workspace_with_docs: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = str(Path(tmp) / "runs.sqlite")
        ws = str(workspace_with_docs)
        out = _run_cli(
            db,
            ws,
            "chat",
            "explain checkpoint policy",
            "--run-id",
            "demo",
            "--mock-llm",
        )
        assert out["status"] == "completed"
        assert out["result"] is not None
        assert "answer" in out["result"]


def test_e2e_chat_pause_resume_explain(workspace_with_docs: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = str(Path(tmp) / "runs.sqlite")
        ws = str(workspace_with_docs)

        paused = _run_cli(
            db,
            ws,
            "chat",
            "explain checkpoint policy",
            "--run-id",
            "demo",
            "--mock-llm",
            "--max-steps",
            "1",
        )
        assert paused["status"] == "paused"
        assert paused["state"] is not None

        completed = _run_cli(
            db,
            ws,
            "resume",
            "--run-id",
            "demo",
            "--mock-llm",
            "--max-steps",
            "10",
        )
        assert completed["status"] == "completed"
        assert completed["result"] is not None

        explained = _run_cli(db, ws, "explain", "--run-id", "demo")
        assert explained["run_id"] == "demo"
        assert explained["status"] == "completed"
        assert explained["tool_call_count"] >= 1


def test_e2e_chat_trace_html(workspace_with_docs: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        db = str(tmp_path / "runs.sqlite")
        trace_path = tmp_path / "trace.html"
        ws = str(workspace_with_docs)

        out = _run_cli(
            db,
            ws,
            "chat",
            "explain checkpoint policy",
            "--run-id",
            "demo",
            "--mock-llm",
            "--trace",
            str(trace_path),
        )
        assert out["status"] == "completed"
        assert trace_path.is_file()
        assert trace_path.stat().st_size > 0


def test_e2e_supervise_delegate_explain_child(workspace_with_docs: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = str(Path(tmp) / "runs.sqlite")
        ws = str(workspace_with_docs)

        parent = _run_cli(
            db,
            ws,
            "supervise",
            "explain checkpoint policy",
            "--run-id",
            "team-demo",
            "--mock-llm",
        )
        assert parent["status"] == "completed"
        assert "Supervisor merged" in parent["result"]["answer"]

        child = _run_cli(db, ws, "explain", "--run-id", "team-demo:sub:researcher")
        assert child["run_id"] == "team-demo:sub:researcher"
        assert child["status"] == "completed"
        assert child["tool_call_count"] >= 1


@pytest.mark.asyncio
async def test_e2e_http_chat_sse(workspace_with_docs: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db = str(Path(tmp) / "runs.sqlite")
        settings = Settings(
            workspace=workspace_with_docs,
            mock_llm=True,
            openai_api_key=None,
            openai_model="gpt-4o-mini",
            max_tool_calls=3,
            user_message="",
            mcp_config_path=None,
        )
        app = create_app(db, settings)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            async with client.stream(
                "POST",
                "/chat",
                json={
                    "message": "explain checkpoint policy",
                    "run_id": "http-demo",
                    "max_steps": 10,
                },
            ) as response:
                assert response.status_code == 200
                body = "".join([chunk async for chunk in response.aiter_text()])

        assert "event: started" in body
        assert "event: completed" in body

        explained = _run_cli(db, str(workspace_with_docs), "explain", "--run-id", "http-demo")
        assert explained["status"] == "completed"
        assert explained["tool_call_count"] >= 1
