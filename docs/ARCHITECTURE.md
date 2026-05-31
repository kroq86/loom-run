# loom-run architecture

## Product boundary

`loom-run` is a **portable product shell**: one coordinator turn per `loom-runner` step, mock or OpenAI LLM, local tools with optional MCP overrides. It extracts the loop shape from [agents_architecture](https://github.com/kroq86/agents_architecture) without SQLAlchemy session state, OTel, or HITL queues.

## Positioning

| | loom-run | Typical agent framework |
|---|----------|-------------------------|
| Primary goal | Durable, inspectable runs | Fast demo / graph composition |
| State | SQLite checkpoints (`loom-runner`) | In-memory or vendor-hosted |
| Scope | Single coordinator, 3 tools | Multi-agent, large plugin ecosystems |
| MCP | Optional stdio bridge + local fallbacks | Often MCP-first or absent |

Comparable stacks: LangGraph/LangChain (graphs), OpenAI Assistants (hosted threads), Temporal+agent (workflow-grade durability). loom-run is lighter and local-first — a reference product for the Loom runtime, not a market competitor.

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
CLI (loom-run chat | serve)
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

- Subagent runtime
- OrgMCP leaf → loom-run step mapping
- Unified memory contract across stack repos

## Shipped in v0.1 hardening

- Tool edge-case tests (`read_file` path escape, `search_docs`, `run_tests`)
- MCP smoke via in-repo mock stdio server (CI opt-in: `.github/workflows/mcp-smoke.yml`)
- HTTP SSE `/chat` — [`src/loom_run/http.py`](../src/loom_run/http.py), `loom-run serve`
- Environment variable reference — [ENV.md](ENV.md)
