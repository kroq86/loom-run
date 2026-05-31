from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    workspace: Path
    mock_llm: bool
    openai_api_key: str | None
    openai_model: str
    max_tool_calls: int
    user_message: str
    mcp_config_path: Path | None


def load_settings() -> Settings:
    mock_raw = os.environ.get("LOOM_RUN_MOCK_LLM", "1").strip().lower()
    mock_llm = mock_raw in {"1", "true", "yes", "on"}
    api_key = os.environ.get("OPENAI_API_KEY") or None
    if api_key:
        mock_llm = False

    workspace = Path(os.environ.get("LOOM_RUN_WORKSPACE", os.getcwd())).resolve()
    mcp_path = os.environ.get("LOOM_RUN_MCP_CONFIG")
    return Settings(
        workspace=workspace,
        mock_llm=mock_llm,
        openai_api_key=api_key,
        openai_model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        max_tool_calls=max(1, int(os.environ.get("LOOM_RUN_MAX_TOOL_CALLS", "3"))),
        user_message=os.environ.get("LOOM_RUN_USER_MESSAGE", ""),
        mcp_config_path=Path(mcp_path).resolve() if mcp_path else None,
    )
