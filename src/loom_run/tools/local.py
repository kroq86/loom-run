from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

from loom_agent.tools import ToolRegistry

from loom_run.config import Settings


def register_local_tools(registry: ToolRegistry, settings: Settings) -> None:
    workspace = settings.workspace

    async def read_file(path: str) -> dict:
        target = _resolve_workspace_path(workspace, path)
        text = target.read_text(encoding="utf-8")
        return {
            "success": True,
            "result_type": "file_read",
            "payload": {"path": str(target), "content": text[:8000]},
        }

    async def search_docs(query: str) -> dict:
        matches: list[dict[str, str]] = []
        for path in sorted(workspace.rglob("*.md")):
            if len(matches) >= 5:
                break
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if query.lower() in text.lower():
                idx = text.lower().find(query.lower())
                start = max(0, idx - 80)
                snippet = text[start : start + 200].replace("\n", " ")
                matches.append({"path": str(path.relative_to(workspace)), "snippet": snippet})
        return {
            "success": True,
            "result_type": "document_search",
            "payload": {"query": query, "matches": matches},
        }

    async def run_tests(path: str = ".") -> dict:
        proc = await asyncio.create_subprocess_exec(
            "python",
            "-m",
            "pytest",
            path,
            "-q",
            cwd=str(workspace),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        output = (stdout or b"").decode() + (stderr or b"").decode()
        ok = proc.returncode == 0
        return {
            "success": ok,
            "is_error": not ok,
            "result_type": "test_run",
            "payload": {"exit_code": proc.returncode, "output": output[-4000:]},
        }

    registry.register("read_file", read_file)
    registry.register("search_docs", search_docs)
    registry.register("run_tests", run_tests)


def _resolve_workspace_path(workspace: Path, path: str) -> Path:
    candidate = (workspace / path).resolve()
    if workspace not in candidate.parents and candidate != workspace:
        raise PermissionError(f"path escapes workspace: {path}")
    if not candidate.is_file():
        raise FileNotFoundError(path)
    return candidate


def run_tests_sync(workspace: Path, path: str = ".") -> dict:
    completed = subprocess.run(
        ["python", "-m", "pytest", path, "-q"],
        cwd=str(workspace),
        capture_output=True,
        text=True,
        check=False,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    ok = completed.returncode == 0
    return {
        "success": ok,
        "is_error": not ok,
        "result_type": "test_run",
        "payload": {"exit_code": completed.returncode, "output": output[-4000:]},
    }
