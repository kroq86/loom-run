from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from loom_run.config import Settings
from loom_run.http import create_app


@pytest.fixture
def api_settings(tmp_path) -> Settings:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "loom.md").write_text("loom-runner checkpoint resume inspect policy", encoding="utf-8")
    return Settings(
        workspace=tmp_path,
        mock_llm=True,
        openai_api_key=None,
        openai_model="gpt-4o-mini",
        max_tool_calls=3,
        user_message="",
        mcp_config_path=None,
    )


@pytest.mark.asyncio
async def test_health_endpoint(api_settings: Settings, tmp_path) -> None:
    app = create_app(str(tmp_path / "runs.sqlite"), api_settings)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_chat_sse_completes(api_settings: Settings, tmp_path) -> None:
    app = create_app(str(tmp_path / "runs.sqlite"), api_settings)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        async with client.stream(
            "POST",
            "/chat",
            json={
                "message": "explain checkpoint policy",
                "run_id": "demo",
                "max_steps": 10,
            },
        ) as response:
            assert response.status_code == 200
            body = "".join([chunk async for chunk in response.aiter_text()])

    assert "event: started" in body
    assert "event: step" in body
    assert "event: completed" in body
    assert "checkpoint" in body.lower()
