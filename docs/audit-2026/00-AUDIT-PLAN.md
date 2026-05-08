<!-- DOC-POINTER-V1 -->
> **⚠ HISTORICAL DOSSIER SERIES (April 2026).** This 13-file series is preserved as a time-bounded subsystem snapshot. The **current** audit workspace is [`docs/audit/`](../audit/) (see [`docs/AUDIT_INDEX.md`](../AUDIT_INDEX.md)). For current numbers always check [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md).

# Platform Reality Audit — April 2026 <sub>(historical)</sub>

**Purpose:** Document exactly how every subsystem works (not how we designed it) so Chris can hand this to a patent lawyer and explain to investors what the platform does.

**Rule:** Every claim must be backed by a task execution record, a DB row, a file artifact, or a request trace. If we can't prove it, it goes in "Truth Gaps."

---

## Subsystem Dossier Template

Each subsystem gets one dossier with these sections:

1. **Purpose** — What this subsystem is supposed to do (1-2 sentences)
2. **Runtime Evidence** — Proof it actually runs (logs, task IDs, timestamps, row counts)
3. **Entry Points** — How it gets triggered (UI buttons, API endpoints, Celery tasks, signals)
4. **Execution Chain** — Step-by-step code path with file:line references
5. **Data Contracts** — Tables written/read, file artifacts, embeddings
6. **External Dependencies** — APIs called (OpenAI, Stability, etc.), env vars needed
7. **Outputs/Artifacts** — What the user actually sees or gets
8. **Failure Modes** — What breaks, how often, what happens when it does
9. **Current Status** — Working / Degraded / Not Wired / Blocked
10. **Truth Gaps** — What we couldn't prove, what needs investigation

---

## Audit Order (execution backbone outward)

| # | Subsystem | Dossier | Status |
|---|-----------|---------|--------|
| 1 | Celery Orchestration | [01-celery.md](01-celery.md) | VERIFIED — 100% success rate (10,645 tasks) |
| 2 | Agent System | [02-agents.md](02-agents.md) | VERIFIED — 73 agents executed, 2,384 total runs |
| 3 | Spider Network | [03-spiders.md](03-spiders.md) | VERIFIED — 54 working, 24 broken, 20.1% embedded |
| 4 | Content Pipeline | [04-content-pipeline.md](04-content-pipeline.md) | VERIFIED — 5 published, 6 deliberation sessions |
| 5 | Prompt Assembly + Context Injection | [05-prompting.md](05-prompting.md) | VERIFIED — 10 of 11 layers active, XP budget applied |
| 6 | Embeddings + RAG | [06-embeddings-rag.md](06-embeddings-rag.md) | VERIFIED — 20.1% spider, 97.6% memory coverage |
| 7 | Learning Loops | [07-learning-loops.md](07-learning-loops.md) | VERIFIED — 8,143 applications, 99.9% effectiveness |
| 8 | Personal Assistant (Rigby) | [08-personal-assistant.md](08-personal-assistant.md) | VERIFIED — 98 schemas, 260K LLM calls, $1.12 total |
| 9 | Signal Intelligence + Initiatives | [09-signals-initiatives.md](09-signals-initiatives.md) | VERIFIED — 248 initiatives, 0 completed, 30 past stage 1 |
| 10 | ConceptForge Pipeline | [10-conceptforge.md](10-conceptforge.md) | VERIFIED — 0 runs, root cause fixed, awaiting trigger |
| 11 | Frontend + Workspace System | [11-frontend-workspaces.md](11-frontend-workspaces.md) | COMPLETE |
| 12 | Infrastructure (Django, Redis, Railway) | [12-infrastructure.md](12-infrastructure.md) | VERIFIED — $1.12 total LLM cost, 3 providers used |

---

---

## Truth Gap Verification Summary (April 6, 2026)

**Verified with production data queries against live database.**

| Claim | Verified? | Evidence |
|-------|-----------|----------|
| "413 Celery tasks" | YES | 10,647 task events logged, 100% success rate |
| "84 agents in AGENT_MAP" | YES | 73 unique agents have executed, 2,384 total runs |
| "86 spiders crawling" | PARTIAL | 78 have logs, 54 working, 24 broken (need cleanup) |
| "Learning loop is closed" | YES | 8,143 pattern applications, 99.9% effectiveness |
| "11-layer prompt injection" | YES | 10 of 11 layers verified active, XP budget applied (+76 tokens, +2.3s) |
| "Content deliberation pipeline" | YES | 6 deliberation sessions, 5 blogs published with quality gates |
| "Embeddings for semantic search" | PARTIAL | Memory 97.6% covered, SpiderData only 20.1% (gap) |
| "103 PA tool schemas" | MOSTLY | 98 verified in code, 5 may be dynamic |
| "19 initiatives" | UPDATED | 248 total, 0 completed, 30 past stage 1 |
| "ConceptForge pipeline" | BLOCKED | 0 runs — gate was too strict, now fixed |
| "Multiple LLM providers" | YES | OpenAI (260K calls), Anthropic (4), Together AI (2) |
| "Platform learns from execution" | YES | 120 patterns, 15 applied, 8,143 applications tracked |
| "$1.12 total LLM cost" | YES | Token conservation mode extremely effective |

### Key Risks for Patent/Investors (Honest)

1. **Spider embedding gap (20.1%)** — 80% of intelligence data not semantically searchable
2. **0 initiatives completed** — pipeline creates but doesn't finish work items
3. **24 broken spiders** — need audit and removal/fix
4. **149 dormant agents** — registered but never executed
5. **0 ConceptForge runs** — fixed but unproven in production
6. **Token conservation too aggressive** — no agent executions in last 30 days

---

## Key Questions for Patent Lawyer

- What is novel about the multi-agent orchestration with context injection?
- How does the spider-to-signal-to-initiative pipeline create autonomous business intelligence?
- What's unique about the content deliberation (multi-reviewer) process?
- How does the learning loop create a feedback cycle that improves over time?
- What IP exists in the PA's function-calling tool chain?

## Key Questions for Investors

- What actually runs autonomously without human intervention?
- What content has been produced and published end-to-end?
- What's the path from spider data to revenue?
- How many real users have interacted with the platform?
- What's the cost per output (LLM spend per deliverable)?
