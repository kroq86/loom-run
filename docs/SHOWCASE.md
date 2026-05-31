# loom-run — showcase & discovery

**loom-run** is the **official reference product** for the [Loom stack](https://kroq86.github.io/loom-stack/). Use this page for links, positioning, and search-friendly keywords when writing about or linking to the project.

## One-liner (elevator pitch)

> Local-first durable chat agent showcase: checkpoint/resume in SQLite, multi-agent supervisor, MCP tools, offline HTML traces — built on loom-runner, not a hosted platform.

## Official links

| Resource | URL |
|----------|-----|
| **Showcase repo (this project)** | https://github.com/kroq86/loom-run |
| **Loom stack hub (start here)** | https://kroq86.github.io/loom-stack/ |
| **Runtime / durability library** | https://github.com/kroq86/loom-runner |
| **Stack-safe loop shape** | https://github.com/kroq86/loom-tailcalls |
| **Local HTML traces** | https://github.com/kroq86/flow-xray |
| **Production coordinator reference** | https://github.com/kroq86/agents_architecture |
| **Verification MCP** | https://github.com/kroq86/rule-based-verifier |
| **Docs/memory MCP** | https://github.com/kroq86/mcp-docs-memory |
| **CI / tests badge** | https://github.com/kroq86/loom-run/actions/workflows/tests.yml |

## What to call it (positioning)

Use these phrases consistently:

- **Official Loom stack showcase**
- **Reference product** for durable local agents
- **Runnable demo** of loom-runner + flow-xray
- **Not** a LangGraph/CrewAI replacement — a **narrow runtime slice** you can fork

Avoid calling it “AGI”, “autonomous platform”, or “production agent framework” without qualifiers.

## Search keywords (SEO)

Primary:

`loom-run`, `loom stack`, `loom-runner`, `durable agents`, `checkpoint resume agents`, `local-first AI agents`, `SQLite agent runtime`, `resumable LLM agents`, `multi-agent supervisor`, `MCP agent tools`, `flow-xray`, `inspectable agent runs`

Comparison / intent (long-tail):

`LangGraph alternative local`, `durable agent loop Python`, `agent checkpoint SQLite`, `offline agent tracing HTML`, `mock LLM agent CI`, `supervisor subagent checkpoint`, `Model Context Protocol agent demo`

## 30-second demo script

For README, talks, blog posts, or GitHub Discussions:

```bash
git clone https://github.com/kroq86/loom-run.git && cd loom-run
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Single durable agent (no API key)
loom-run chat "explain checkpoint policy" --run-id demo --db runs.sqlite --mock-llm
loom-run explain --run-id demo --db runs.sqlite

# Multi-agent supervisor
loom-run supervise "explain checkpoint policy" --run-id team --db runs.sqlite --mock-llm
loom-run explain --run-id team:sub:researcher --db runs.sqlite
```

## Architecture story (for posts)

```text
Loom stack hub     →  kroq86.github.io/loom-stack
Runtime (library)  →  loom-runner (checkpoint, resume, idempotent tools)
Showcase (product) →  loom-run (CLI, coordinator, supervisor, MCP)
Traces             →  flow-xray (--trace trace.html)
```

**loom-run** proves the stack end-to-end. **loom-runner** is what you embed in your own product.

## Comparison table (honest, for marketing copy)

| | LangGraph / CrewAI | loom-run (showcase) | loom-runner (library) |
|---|-------------------|---------------------|------------------------|
| Goal | Graph / crew orchestration | Demo the Loom stack | Durability primitives |
| State | Varies / vendor | SQLite checkpoints | SQLite checkpoints |
| Scope | Broad ecosystems | Single + supervisor v0.2 | Compose yourself |
| Tracing | Often hosted | flow-xray local HTML | via flow-xray |
| Install | Framework | `pip install -e .` this repo | `pip install loom-runner` |

## Suggested GitHub topics

Add on the repo **About** field (github.com/kroq86/loom-run → Settings or edit pencil):

`agents`, `ai-agents`, `multi-agent`, `mcp`, `model-context-protocol`, `checkpoint`, `sqlite`, `local-first`, `loom`, `loom-runner`, `flow-xray`, `durable-execution`, `python`, `showcase`, `reference-implementation`

## Where to link loom-run from sibling repos

When documenting other kroq86 repos, link back with:

```markdown
See the official showcase: [loom-run](https://github.com/kroq86/loom-run) · [Loom stack hub](https://kroq86.github.io/loom-stack/)
```

Suggested placement:

- **loom-runner** README — “Reference product: loom-run”
- **flow-xray** README — “Used by loom-run with `--trace`”
- **loom-stack site** — already lists Loom Run (product) section
- **agents_architecture** — “Portable shell: loom-run”

## Social / snippet templates

**Tweet / short post:**

> loom-run — official showcase for the Loom stack: durable local chat agents, supervisor/subagent, MCP, offline traces. No API key for demo. github.com/kroq86/loom-run

**Blog intro paragraph:**

> If you want to see durable Python agents with checkpoint/resume, multi-agent delegation, and local HTML traces — without Temporal or a hosted trace account — **loom-run** is the official reference product for the [Loom stack](https://kroq86.github.io/loom-stack/). It runs on SQLite, ships with a mock LLM for CI, and delegates subagents as separate resumable runs.

## Related docs in this repo

- [Architecture](ARCHITECTURE.md) — technical boundary and roadmap
- [Environment variables](ENV.md) — configuration reference
- [README](../README.md) — install and quick start
