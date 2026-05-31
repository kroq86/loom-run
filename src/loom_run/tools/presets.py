"""MCP server presets mapping loom-run tool names to external MCP tool names."""

VERIFIER_PRESET = {
    "run_tests": "run_tests",
    "read_file": "read_repo_file",
}

DOCS_MEMORY_PRESET = {
    "search_docs": "docs_search",
}

PRESETS = {
    "rule-based-verifier": VERIFIER_PRESET,
    "docs-memory": DOCS_MEMORY_PRESET,
}
