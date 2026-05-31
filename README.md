[![Loom Stack](https://kroq86.github.io/loom-stack/assets/loom-stack-banner.png)](https://kroq86.github.io/loom-stack/)

# loom-run — official Loom stack showcase

[![PyPI](https://img.shields.io/pypi/v/loom-run)](https://pypi.org/project/loom-run/)
[![GitHub](https://img.shields.io/github/stars/kroq86/loom-run?style=social)](https://github.com/kroq86/loom-run)
[![Loom stack docs](https://img.shields.io/badge/Loom_stack-showcase-8B7355)](https://kroq86.github.io/loom-stack/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/kroq86/loom-run/actions/workflows/tests.yml/badge.svg)](https://github.com/kroq86/loom-run/actions/workflows/tests.yml)

> **Official reference product** for the [Loom stack](https://kroq86.github.io/loom-stack/) — not a generic agent framework, but the **runnable demo** that wires [loom-runner](https://github.com/kroq86/loom-runner) + [flow-xray](https://github.com/kroq86/flow-xray) into a local-first durable chat agent with multi-agent supervisor.

**Keywords:** durable agents · checkpoint resume · multi-agent orchestration · MCP tools · local-first · SQLite · inspectable runs · LangGraph alternative (runtime slice)

| | |
|---|---|
| **Showcase hub** | [kroq86.github.io/loom-stack](https://kroq86.github.io/loom-stack/) |
| **This repo** | [github.com/kroq86/loom-run](https://github.com/kroq86/loom-run) |
| **Runtime layer** | [github.com/kroq86/loom-runner](https://github.com/kroq86/loom-runner) |
| **Local traces** | [github.com/kroq86/flow-xray](https://github.com/kroq86/flow-xray) |
| **Ops product** | [github.com/kroq86/loom-ops](https://github.com/kroq86/loom-ops) — runbooks, HITL, incident response |

```text
User message  →  coordinator (LLM + tools)  →  loom-runner checkpoint/resume  →  flow-xray --trace
                      ↑ supervise → subagent runs (v0.2)
```

## What this repo is

| Role | Explanation |
|------|-------------|
| **Showcase / reference product** | End-to-end proof that the Loom stack works: CLI, mock LLM (CI-safe), tools, supervisor, E2E tests |
| **Not** | LangGraph, CrewAI, or a hosted agent platform |
| **Built on** | [loom-runner](https://github.com/kroq86/loom-runner) (durability), [loom-tailcalls](https://github.com/kroq86/loom-tailcalls) (loop shape), [flow-xray](https://github.com/kroq86/flow-xray) (HTML traces) |
| **Pattern from** | [agents_architecture](https://github.com/kroq86/agents_architecture) — coordinator loop only, not full backend |

If you want **libraries to compose** → start with [loom-runner](https://github.com/kroq86/loom-runner).  
If you want **see it all working in 30 seconds** → clone this repo.  
If you want **incident/deploy runbooks** (not dev chat) → [loom-ops](https://github.com/kroq86/loom-ops).

More: [Showcase guide](docs/SHOWCASE.md) · [Architecture](docs/ARCHITECTURE.md)

## Loom stack position

The stack is a pyramid, not five equal frameworks. Tail-call optimization is
the primitive, runner is the durable runtime, xray is the microscope, and the
apps prove the stack in real workflows.

| Layer | Project | Job |
| --- | --- | --- |
| Primitive | [loom-tailcalls](https://github.com/kroq86/loom-tailcalls) | Make async recursive/state-machine loops stack-safe |
| Runtime kernel | [loom-runner](https://github.com/kroq86/loom-runner) | Make those loops durable, resumable, idempotent |
| Microscope | [flow-xray](https://github.com/kroq86/flow-xray) | Show what actually happened in one offline HTML trace |
| Proof app | **loom-run** ← **this repo** | Chat agent reference implementation |
| Proof app | [loom-ops](https://github.com/kroq86/loom-ops) | Ops/runbook agent reference implementation |

`loom-run` is not `loom-runner`. `loom-runner` is the reusable runtime kernel;
this repo is the runnable chat/dev showcase that proves the kernel, traces, MCP
tools, and supervisor pattern work together.

## Install

**From PyPI:**

```bash
pip install "loom-run[api,openai]"
loom-run chat "explain checkpoint policy" --run-id demo --db runs.sqlite --mock-llm
```

**From source:**

```bash
git clone https://github.com/kroq86/loom-run.git
cd loom-run
python3.13 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,api,openai]"
```

Ecosystem map: [loom-stack ECOSYSTEM.md](https://github.com/kroq86/loom-stack/blob/main/docs/ECOSYSTEM.md)

## Demo commands (copy-paste)

**Single agent (mock LLM, no API key):**

```bash
loom-run chat "explain checkpoint policy" --run-id demo --db runs.sqlite --mock-llm
loom-run resume --run-id demo --db runs.sqlite --max-steps 20
loom-run explain --run-id demo --db runs.sqlite
loom-run chat "explain checkpoint policy" --run-id demo2 --db runs.sqlite --mock-llm --trace trace.html
```

**Multi-agent supervisor (v0.2):**

```bash
loom-run supervise "explain checkpoint policy" --run-id team-demo --db runs.sqlite --mock-llm
loom-run explain --run-id team-demo:sub:researcher --db runs.sqlite
```

**HTTP SSE (optional):**

```bash
loom-run serve --db runs.sqlite --mock-llm
curl -N -X POST http://127.0.0.1:8765/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"explain checkpoint policy","run_id":"demo","max_steps":20}'
```

## Tools

| Tool | Default | With MCP |
|------|---------|----------|
| `read_file` | local workspace read | [rule-based-verifier](https://github.com/kroq86/rule-based-verifier) → `read_repo_file` |
| `search_docs` | grep `*.md` in workspace | [mcp-docs-memory](https://github.com/kroq86/mcp-docs-memory) → `docs_search` |
| `run_tests` | `pytest -q` in workspace | rule-based-verifier → `run_tests` |
| `delegate_subagent` | supervisor → child chat run | — |

MCP config: [`mcp.servers.example.json`](mcp.servers.example.json) · env: [docs/ENV.md](docs/ENV.md)

## Extended ecosystem map

| Layer | Repo | Role |
|-------|------|------|
| **Dev showcase (this repo)** | [loom-run](https://github.com/kroq86/loom-run) | Reference chat agent + supervisor |
| **Ops product** | [loom-ops](https://github.com/kroq86/loom-ops) | Runbook supervisor (planner / executor / verifier) |
| Durability | [loom-runner](https://github.com/kroq86/loom-runner) | SQLite checkpoint, resume, idempotent tools |
| Transitions | [loom-tailcalls](https://github.com/kroq86/loom-tailcalls) | Stack-safe `@tailrec` driver |
| Traces | [flow-xray](https://github.com/kroq86/flow-xray) | Offline HTML execution traces |
| Coordinator reference | [agents_architecture](https://github.com/kroq86/agents_architecture) | Production backend patterns |
| Verification MCP | [rule-based-verifier](https://github.com/kroq86/rule-based-verifier) | Tests, lint, repo read |
| Docs/memory MCP | [mcp-docs-memory](https://github.com/kroq86/mcp-docs-memory) | Semantic docs search |

## Tests

```bash
python -m pytest -q              # 21 tests incl. subprocess E2E
python -m pytest -q tests/test_e2e.py
```

## Docs

- [Showcase & discovery](docs/SHOWCASE.md) — SEO, links, positioning
- [Architecture](docs/ARCHITECTURE.md)
- [Environment variables](docs/ENV.md)

## License

MIT · [kroq86](https://github.com/kroq86)
