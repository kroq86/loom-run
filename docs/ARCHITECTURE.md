# loom-run architecture

## Product boundary

`loom-run` is a **portable product shell**: one coordinator turn per `loom-runner` step, mock or OpenAI LLM, local tools with optional MCP overrides. It extracts the loop shape from [agents_architecture](https://github.com/kroq86/agents_architecture) without FastAPI, SQLAlchemy session state, OTel, or HITL queues.

## kroq86 stack map

| Repo | Role in ecosystem | Wired in loom-run v0.1 |
|------|-------------------|------------------------|
| [loom-tailcalls](https://github.com/kroq86/loom-tailcalls) | Stack-safe `@tailrec` driver inside loom-runner | via pip dependency |
| [loom-runner](https://github.com/kroq86/loom-runner) | SQLite checkpoint/resume, idempotent tools, CLI inspect | core runtime |
| [flow-xray](https://github.com/kroq86/flow-xray) | Local HTML traces | `--trace` in CLI |
| [agents_architecture](https://github.com/kroq86/agents_architecture) | Production coordinator backend | pattern only (`orchestrator.py`) |
| [rule-based-verifier](https://github.com/kroq86/rule-based-verifier) | Policy + tests/lint MCP | optional MCP preset |
| [mcp-docs-memory](https://github.com/kroq86/mcp-docs-memory) | Semantic docs + memory MCP | optional MCP preset |
| [OrgMCP](https://github.com/kroq86/OrgMCP) | Human TDD plan engine | not wired |
| [ide](https://github.com/kroq86/ide) | Terminal IDE + CodeClaw | not wired |
| [data-engineering-runtime-lab](https://github.com/kroq86/data-engineering-runtime-lab) | Ops copilot MCP | not wired |

## Data flow

```text
CLI (loom-run chat)
  → Settings + ToolRegistry (local + optional MCP)
  → make_step(MockLLM | OpenAI)
  → AgentRunner.start/resume (SQLite)
  → optional flow-xray HTML
```

## State model

`ChatState` holds user message, transcript (`Message` tuples), tool budget, phase. Each step:

1. LLM returns `finish` or `tool_call`
2. Tools run through `RunContext.call_tool` (runner idempotency)
3. Checkpoint committed by loom-runner

## Integration gaps (honest)

- **No unified memory contract** across SQL facts (agents_architecture), DuckDB (docs-memory), and loom-runner SQLite.
- **MCP bridge** is minimal stdio JSON-RPC — sufficient for presets, not a full MCP client library.
- **Multi-agent graphs** deferred everywhere; supervisor would be a separate orchestration layer.
- **flow-xray** traces Python call graph; IDE/CodeClaw traces remain separate formats.

## Deferred

- FastAPI `/chat` SSE service
- Subagent runtime
- PyPI publish (after CI hardening)
- OrgMCP leaf → loom-run step mapping
