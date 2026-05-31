# loom-run

[![Loom stack](https://img.shields.io/badge/docs-loom--stack-8B7355)](https://kroq86.github.io/loom-stack/)

**Local-first durable chat agent** on the [Loom stack](https://kroq86.github.io/loom-stack/).

Not a full port of [agents_architecture](https://github.com/kroq86/agents_architecture) — a portable shell with the same coordinator loop (LLM → tool or finish → checkpoint), without FastAPI/SQLAlchemy/OTel/HITL.

```text
User message  →  coordinator step (LLM + tools)  →  loom-runner checkpoint/resume  →  flow-xray --trace
```

## What it is for

Most agent frameworks optimize for a quick demo. **loom-run** optimizes for **inspectable, resumable runs**:

- crash mid-run → `loom-run resume` continues from SQLite checkpoint
- tool retries → idempotent calls via `loom-runner`
- “what happened?” → `explain`, tool-call history, optional HTML trace

**Good fit:** local development, CI without API keys (MockLLM), wiring MCP tools with local fallbacks.

**Not a fit:** multi-agent orchestration, hosted threads, IDE coding agents, production platform out of the box.

## Install

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Optional OpenAI:

```bash
pip install -e ".[dev,openai]"
export OPENAI_API_KEY=...
export LOOM_RUN_MOCK_LLM=0
```

## Quick start (mock LLM — no API key)

```bash
loom-run chat "explain checkpoint policy" --run-id demo --db runs.sqlite --mock-llm
loom-run resume --run-id demo --db runs.sqlite --max-steps 20
loom-run explain --run-id demo --db runs.sqlite
loom-run chat "explain checkpoint policy" --run-id demo2 --db runs.sqlite --mock-llm --trace trace.html
```

## Tools

| Tool | Default | With MCP |
|------|---------|----------|
| `read_file` | local workspace read | `rule-based-verifier` → `read_repo_file` |
| `search_docs` | grep `*.md` in workspace | `docs-memory` → `docs_search` |
| `run_tests` | `pytest -q` in workspace | `rule-based-verifier` → `run_tests` |

Copy [`mcp.servers.example.json`](mcp.servers.example.json) and set:

```bash
export LOOM_RUN_MCP_CONFIG=/path/to/mcp.servers.json
export LOOM_RUN_WORKSPACE=/path/to/project
```

## HTTP API (optional)

```bash
pip install -e ".[dev,api]"
loom-run serve --db runs.sqlite --mock-llm
curl -N -X POST http://127.0.0.1:8765/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"explain checkpoint policy","run_id":"demo","max_steps":20}'
```

SSE events: `started` → `step` (repeat) → `completed` | `paused` | `error`.

## Also via loom-runner CLI

```bash
loom-runner run examples/chat_agent.py --run-id demo --db runs.sqlite --max-steps 10
```

Set `LOOM_RUN_USER_MESSAGE` before running the example module.

## Stack map

| Layer | Repo |
|-------|------|
| Transitions | [loom-tailcalls](https://github.com/kroq86/loom-tailcalls) |
| Durability | [loom-runner](https://github.com/kroq86/loom-runner) |
| Traces | [flow-xray](https://github.com/kroq86/flow-xray) |
| Coordinator reference | [agents_architecture](https://github.com/kroq86/agents_architecture) |
| Verification MCP | [rule-based-verifier](https://github.com/kroq86/rule-based-verifier) |
| Memory/RAG MCP | [mcp-docs-memory](https://github.com/kroq86/mcp-docs-memory) |

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Environment variables](docs/ENV.md)

## Tests

```bash
python -m pytest -q
```

MCP smoke (mock stdio server, no external deps): `python -m pytest -q tests/test_mcp_smoke.py`

## License

MIT
