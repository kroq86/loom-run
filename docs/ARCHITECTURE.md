# loom-run architecture

## Product boundary

`loom-run` is the **official Loom stack showcase** — a **portable reference product**: coordinator turn per `loom-runner` step, mock or OpenAI LLM, local tools with optional MCP overrides, sequential supervisor/subagent (v0.2). Marketing & links: [SHOWCASE.md](SHOWCASE.md) · hub: [loom-stack](https://kroq86.github.io/loom-stack/).

It extracts the loop shape from [agents_architecture](https://github.com/kroq86/agents_architecture) without SQLAlchemy session state, OTel, or HITL queues.

## Positioning

| | loom-run v0.2 | Where the market is (2026) |
|---|---------------|----------------------------|
| Primary goal | Durable single-agent + **sequential supervisor** | Durable multi-agent orchestration |
| State | SQLite checkpoints (`loom-runner`) | Same bet (LangGraph checkpointers, Temporal) |
| Tools | MCP optional + local fallbacks + `delegate_subagent` | MCP as shared tool standard |
| Scope today | One coordinator, supervisor → one subagent | Graphs / crews / parallel specialists |

**Loom bet:** `loom-runner` owns durability; **loom-run** owns coordinator + supervisor steps; each subagent leaf is a resumable chat run.

## Multi-agent (v0.2 — shipped, minimal)

```text
loom-run supervise
  → SupervisorStep (MockSupervisorLLM)
  → delegate_subagent(parent_run_id, agent_name, message)
  → child chat run: {parent_run_id}:sub:{agent_name}
  → supervisor merge → Complete
```

Implementation: [`src/loom_run/supervisor/`](../src/loom_run/supervisor/), [`src/loom_run/agents/supervisor_agent.py`](../src/loom_run/agents/supervisor_agent.py).

Child runs reuse the chat coordinator ([`make_step`](../src/loom_run/coordinator/step.py)). Inspect with `loom-run explain --run-id team-demo:sub:researcher`.

## kroq86 stack map

| Repo | Role in ecosystem | Wired in loom-run |
|------|-------------------|-------------------|
| **[loom-run](https://github.com/kroq86/loom-run)** | **Official stack showcase (this repo)** | — |
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
CLI (loom-run chat | supervise | serve)
  → Settings + ToolRegistry (local + optional MCP)
  → make_step / make_supervisor_step
  → AgentRunner.start/resume (SQLite)
  → optional flow-xray HTML
```

## State models

**ChatState** — single-agent coordinator: user message, transcript, tool budget, phase.

**SupervisorState** — adds `run_id`; tool `delegate_subagent` spawns child chat runs.

Each step: LLM → tool or finish → `RunContext.call_tool` → checkpoint.

## Integration gaps (honest)

- **Parallel subagents / fan-out** not wired — v0.2 is sequential delegate → merge only.
- **OpenAI supervisor LLM** not wired — MockSupervisor only for CI.
- **No unified memory contract** across SQL facts, DuckDB (docs-memory), and loom-runner SQLite.
- **MCP bridge** is minimal stdio JSON-RPC.
- **flow-xray** traces Python call graph; IDE/CodeClaw traces remain separate formats.

## Deferred (priority)

- Parallel subagents and supervisor routing graph
- OpenAI supervisor LLM
- OrgMCP leaf → loom-run step mapping
- Unified memory contract across stack repos
- HTTP `/supervise` SSE

## Shipped

**v0.1:** tool tests, MCP smoke, HTTP SSE `/chat`, [ENV.md](ENV.md)

**v0.2:** supervisor + `delegate_subagent`, `loom-run supervise`, [`tests/test_supervisor.py`](../tests/test_supervisor.py)
