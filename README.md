# loom-run

[![Loom stack](https://img.shields.io/badge/docs-loom--stack-8B7355)](https://kroq86.github.io/loom-stack/)

**Local-first durable chat agent** built on the [Loom stack](https://kroq86.github.io/loom-stack/): coordinator pattern from [agents_architecture](https://github.com/kroq86/agents_architecture) as a `loom-runner` step — not a full port of that backend.

```text
User message  →  coordinator step (LLM + tools)  →  loom-runner checkpoint/resume  →  flow-xray --trace
```

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

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Tests

```bash
python -m pytest -q
```

## License

MIT
