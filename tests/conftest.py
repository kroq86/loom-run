from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def workspace_with_docs(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "loom.md").write_text("loom-runner checkpoint resume inspect policy", encoding="utf-8")
    (tmp_path / "README.md").write_text("# loom-run test workspace", encoding="utf-8")
    return tmp_path
