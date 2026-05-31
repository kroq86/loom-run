# Environment variables

All settings can also be passed via CLI flags (see `loom-run --help`).

| Variable | Default | Description |
|----------|---------|-------------|
| `LOOM_RUN_MOCK_LLM` | `1` | Use deterministic MockLLM when `1`/`true`/`yes`/`on`. Ignored if `OPENAI_API_KEY` is set. |
| `OPENAI_API_KEY` | — | OpenAI API key. When set, MockLLM is disabled. |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model name for OpenAI client. |
| `LOOM_RUN_WORKSPACE` | current directory | Root for local `read_file`, `search_docs`, and `run_tests`. |
| `LOOM_RUN_MAX_TOOL_CALLS` | `3` | Tool-call budget per run (minimum 1). |
| `LOOM_RUN_USER_MESSAGE` | empty | Initial user message when using `examples/chat_agent.py` or programmatic entry points. |
| `LOOM_RUN_MCP_CONFIG` | — | Path to MCP servers JSON (see `mcp.servers.example.json`). Local tool fallbacks apply when unset. |
| `LOOM_RUN_DB` | `runs.sqlite` | Default SQLite checkpoint database path for CLI commands. |
| `LOOM_RUN_HOST` | `127.0.0.1` | Bind address for `loom-run serve`. |
| `LOOM_RUN_PORT` | `8765` | Port for `loom-run serve`. |

Copy [`.env.example`](../.env.example) as a starting point:

```bash
cp .env.example .env
```
