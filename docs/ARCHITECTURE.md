# loom-run architecture

## Product boundary

`loom-run` is a **portable product shell**: one coordinator turn per `loom-runner` step, mock or OpenAI LLM, local tools with optional MCP overrides. It extracts the loop shape from [agents_architecture](https://github.com/kroq86/agents_architecture) without SQLAlchemy session state, OTel, or HITL queues.

## Positioning

| | loom-run v0.1 | Where the market is (2026) |
|---|---------------|----------------------------|
| Primary goal | Durable, inspectable **single-agent** runs | Durable **multi-agent** orchestration |
| State | SQLite checkpoints (`loom-runner`) | Same bet (LangGraph checkpointers, Temporal) |
| Tools | MCP optional + local fallbacks | MCP as shared tool standard |
| Scope today | One coordinator, 3 tools | Graphs / crews / supervisor + specialists |

**Trend check:** production agents moved from “one LLM loop” to **networks of specialists** with persistent state — LangGraph for graph control, CrewAI for role-based crews, MCP for portable tools. Durability and inspectability are table stakes, not differentiators anymore.

**Loom bet:** `loom-runner` owns durability (checkpoint, resume, idempotent tools); **loom-run** owns the coordinator step; a **supervisor layer** (next) owns multi-agent routing — delegate → sub-run → merge, each leaf checkpointed.

Comparable stacks: LangGraph (closest — graph + checkpoints), CrewAI (roles, less durability focus), OpenAI Assistants (hosted, opaque state). loom-run is the local runtime slice, not a finished multi-agent product yet.

## Multi-agent roadmap (planned)

```text
Supervisor step (route / delegate / merge)
  → subagent A: loom-run chat run (run_id=..., checkpoint)
  → subagent B: loom-run chat run
  → supervisor resumes until goal met
```

Not wired in v0.1. [`agents_architecture`](https://github.com/kroq86/agents_architecture) has production coordinator patterns to extract; OrgMCP leaf → step mapping is a candidate integration.

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

- **Multi-agent orchestration not wired yet** — v0.1 is single coordinator; supervisor/subagent graph is the next product boundary, not optional nice-to-have.
- **No unified memory contract** across SQL facts (agents_architecture), DuckDB (docs-memory), and loom-runner SQLite.
- **MCP bridge** is minimal stdio JSON-RPC — sufficient for presets, not a full MCP client library.
- **flow-xray** traces Python call graph; IDE/CodeClaw traces remain separate formats.

## Deferred (priority)

- **Supervisor / subagent runtime** — multi-agent orchestration on top of resumable coordinator runs
- OrgMCP leaf → loom-run step mapping
- Unified memory contract across stack repos

## Shipped in v0.1 hardening

- Tool edge-case tests (`read_file` path escape, `search_docs`, `run_tests`)
- MCP smoke via in-repo mock stdio server (CI opt-in: `.github/workflows/mcp-smoke.yml`)
- HTTP SSE `/chat` — [`src/loom_run/http.py`](../src/loom_run/http.py), `loom-run serve`
- Environment variable reference — [ENV.md](ENV.md)
