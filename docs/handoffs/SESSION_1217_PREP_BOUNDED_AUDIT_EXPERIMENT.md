# Session 1217 Prep — Bounded Self-Direction Experiment + Audit Deliverable

**Status:** Audit deliverable shipped to Donkey Betz workspace. Chris picked 3 items for Session 1217 execution work. 2 placeholder deliverables filed for Items 2 + 3. Start-doc updated.
**Date:** 2026-06-23 (same day as Sessions 1214/1215/1216 — fourth single-day arc).
**Active conversation:** `pa-58737666f25741dc` — fresh thread spun by Rigby for the bounded experiment. Carries forward into Session 1217.
**Prior session:** [`SESSION_1216_OPENAI_CALLER_ALIGNMENT_PHASE_E.md`](./SESSION_1216_OPENAI_CALLER_ALIGNMENT_PHASE_E.md).
**Next session entry point:** Session 1217 — see 00-START-NEXT-SESSION.md §"FIRST THING Session 1217" for the 3 Chris-picked items.

## TL;DR

This isn't a normal feature/fix session — it's a meta-session. Chris asked: *"What would happen if we started a fresh session for both you and Rigby, and you guys just came up with your own plan?"*

We ran the bounded version of that experiment: ~2h budget, no code changes, no PRs (except 3 small docs PRs for thread repinning + plan capture). Output: ONE audit deliverable in the Donkey Betz workspace with Rigby's view (ops/governance/revenue) + Claude's view (code/architecture) + a directive top-5 explicitly framed as "what we'd surface IF forced to pick — Chris decides what's actually worth shipping."

Chris read the deliverable, picked 3 items, told us to queue them for Session 1217 execution.

## Session Manifest

### PRs merged (3 small docs)

| # | Title | Purpose |
|---|---|---|
| **#2503** | chore(session-1217): repin pa_local.sh to fresh Session 1217 thread | Pointed `tools/pa_local.sh` at `pa-58737666f25741dc`, retired `pa-e37fe30dc7b941a6` (Sessions 1214-1216 OpenAI alignment arc) in the comment ledger. |
| **#2504** | docs(session-1217): capture Chris-picked plan from self-directed audit | Updated `00-START-NEXT-SESSION.md` "FIRST THING Session 1217" with the 3 items Chris picked, deliverable IDs, canonical data sources, sequencing recommendation, and explicit do-not-touch list. |
| **(this PR)** | docs(session-1217-prep): bounded audit experiment handoff | This file. |

### Deliverables created (3 total)

| ID | Title | Status | Notes |
|---|---|---|---|
| `bec077ed-d89e-4c7c-935e-f06eefad7bec` | Self-directed audit — what Chris should look at next | shipped (read by Chris) | 22,457 chars. Rigby's A/B/C view + Claude's G/H view + cross-cutting Tier-1 cluster + directive Top-5 + budget/process notes. Workspace: Donkey Betz. Category: Platform Diagnostics. |
| `192a390c-ebb6-4574-8d29-6f6e60fd2778` | PA tool schema/handler delta classification — 59 surplus handlers (Session 1217 Item 2) | draft (placeholder) | Filed for Session 1217 Item 2 output. Category: Platform Capability Audit. |
| `b92c41d0-e886-4586-84c6-61206034668a` | PA tool top 10 failure signatures (Session 1217 Item 3) | draft (placeholder) | Filed for Session 1217 Item 3 output. Category: Platform Capability Audit. |

## What shipped — the bounded experiment

### Framing (Chris's words)

> "Right now I am trying to direct the ship, so I have you look into things or I ask questions and we have the /docs/ and stuff, but I have never just let you and Rigby dive into everything lol. What would happen if we started a fresh session for both you and Rigby, and you guys just came up with your own plan?"

Claude's recommendation: bounded, not free-range. Half-session budget. Output as deliverable. Chris picks from it, doesn't pre-commit.

### Setup

- Rigby spun fresh conversation `pa-58737666f25741dc` via `session_tool create_fresh` — title *"Session 1217 — Self-directed audit experiment"*. Old thread `pa-e37fe30dc7b941a6` (3-session OpenAI alignment arc) retired.
- `tools/pa_local.sh` repinned to new thread (PR #2503).
- Agreed on workspace: Donkey Betz (`b4503364-2573-4401-9e28-61a739e0ce50`).
- Title locked: *"Self-directed audit — what Chris should look at next"*.
- Per-finding template locked (Rigby's draft): **Finding** / **Evidence** (with pointers) / **Why it matters** / **Recommendation** / **Effort (S/M/L)**.

### Category split

Each owner takes categories where their tools have the strongest evidence:

| Owner | Category | Why their tools |
|---|---|---|
| Rigby | A. Ops health | Daily ops snapshot, queue depth, beat schedule, agent timeout signatures |
| Rigby | B. Autonomy governance | PA tool success rate, agent rotation cadence, autonomous task failure rate |
| Rigby | C. Revenue pipeline | Opportunity stats, action card freshness, deliverable workspace coverage |
| Claude | G. Code & debt | ruff, verify_doc_claims, direct-LLM lint, grep sweeps, AST analysis |
| Claude | H. Architecture & strategic | Patent disclosures, audit-doc-vs-runtime drift, load-bearing hub analysis, narrative staleness |

Categories D (content pipeline), E (sports desk), F (knowledge system) explicitly deferred — neither owner had time-budget to scan them in this experiment.

### Process — parallel discovery + Explore subagent delegation

Claude's lane (G + H) ran 2 Explore subagents in parallel to keep main-thread context lean:

- **G-track subagent:** ruff F401/F811/F821/F841/F541/E402/E722 sweep across `core/agents/`, `ai_core/agents/`, `core/services/`; correlated direct-LLM lint hits + 4 `verify_doc_claims` drift findings + Pyright noise.
- **H-track subagent:** read `docs/patents/README.md` + all disclosures, cross-referenced against `docs/PLATFORM_INVENTORY.md`, ran `build_*_audit` generator commands to find audit-doc drift, counted import refs to identify load-bearing hubs, read narrative frontmatter for staleness.

Rigby's lane (A + B + C) ran her ops tools live:

- `ops_tool.snapshot` — agent timeout rate, PA tool success rate, queue depths
- `ops_tool.beat_schedule` — disabled/stale beat tasks
- `task_manager_tool.stats` — opportunity counts, revenue pipeline
- `platform_config_tool.overview` — confirmed local context for tool runs

### Output structure

The merged deliverable contains:

1. **Rigby view (A/B/C):** 5 findings, each Finding/Evidence/Why/Rec/Effort
2. **Claude view (G/H):** 10 findings, same template
3. **Cross-cutting Tier-1 cluster (jointly authored):** Names the convergence — PA tool dispatch + LLM call layer is the platform's hottest unreliability + unobserved-from-Chris zone. Rigby's 74.5% PA tool success rate + Claude's 59-handler schema delta + 5 direct-LLM lint violations all point at the same root.
4. **Directive Top-5** ranked by leverage = impact × low effort + 1 wildcard. Explicitly framed as "what we'd surface IF forced — Chris decides."
5. **Explicit NOT-in-top-5 with reasoning** (avoids ambiguity about what's deferred).
6. **Budget + process notes** (so future bounded experiments can copy the pattern).

### Chris's picks (Session 1217 work)

After reading the deliverable, Chris picked 3 items:

| Item | From | Action |
|---|---|---|
| 1. Fix 2 undefined-variable bugs | Claude G1 + G2 | Fix only. 2 PRs, ~30 min each. |
| 2. Classify the 59-handler schema/handler delta | Claude H5 | Investigate, do NOT fix. Output → deliverable `192a390c-…`. |
| 3. Top 10 PA tool failure signatures | Reframe of Rigby B3 | Pull actual exceptions, not aggregate. Output → deliverable `b92c41d0-…`. |

Items 2 + 3 share data (the 59-list informs Item 3 handler classification). Sequencing: Item 1 first (~1h), Items 2+3 in parallel (Rigby pulls failures, Claude grinds schema audit).

### What Chris DIDN'T pick (explicit do-not-touch for Session 1217)

To prevent Session 1217 from re-litigating the audit:

- Promote `check-reasoning-contract.yml` to enforce mode (P2 carryover from spec close)
- Doc-vs-runtime drift triage (Claude H6 + H7 + H8 — services count 3x off, +12 mgmt commands, agent seed baseline)
- Critical-path hub markers (Claude H4 — agent_router, openai_client_factory, tool_dispatcher, celery)
- Narrative anchor refreshes (Claude H3 + H4 — 75-session staleness)
- Atlas fleet positioning (Claude H10)
- Beat schedule disabled tasks classification (Rigby A4)
- Revenue pipeline aggregation audit (Rigby C5)

These are all real and documented in the deliverable — they're deferred, not dismissed. Future sessions can revisit.

## What worked vs what to adjust

### What worked
- **Bounded scope** prevented runaway exploration. Real ~2h, not 6.
- **Parallel Explore subagents** kept Claude's main-thread context lean (~10K tokens added vs hundreds of K if I'd scanned everything inline).
- **Pre-locked per-finding template** stopped both owners from drifting into prose-y "thoughts." Every finding has a verifiable pointer.
- **Pre-locked workspace + title + IDs** meant no time wasted on placement decisions.
- **Cross-cutting cluster section** was a real value-add — Rigby's PA-tool 74.5% and Claude's 59-handler delta would have looked unrelated if presented separately. Naming the convergence makes the deliverable more decision-useful for Chris.

### What to adjust next time
- **Pre-agree which Explore subagent prompts** Claude will use BEFORE starting discovery. The H-track prompt was longer than the G-track because the H scope was less crisp going in.
- **More upfront calibration on terminology** ("schema/handler" was clear; "load-bearing" required explanation in the deliverable).
- **Time-check at half-budget** would have been a useful checkpoint. We hit it organically (~1h discovery + ~1h merge/format) but a 30-min midpoint sync could prevent overruns.

## 24h watch

None triggered. This was pure analysis — no code shipped, no behavior change. Session 1217's Item 1 will ship code; its watch (if any) comes from those PRs.

## Open follow-ups (Session 1217+ unless quick win)

| Priority | Item | Notes |
|---|---|---|
| **P1** | Session 1217 Items 1, 2, 3 (Chris's picks) | Captured in 00-START-NEXT-SESSION.md FIRST THING |
| **P2** | Promote `check-reasoning-contract.yml` to enforce mode | 1-line PR after 24h burn-in. Session 1218+. |
| **P2** | OpenAIProvider.generate() actually delete it | Session 1217 Item 1B is the fix-or-delete — lean is delete. |
| **P2** | Critical-path hub markers (4 files) | Audit finding H4. Tiny PR, big guardrail. |
| **P2** | Doc-vs-runtime drift triage (SERVICES.md, BACKEND_INVENTORY.md, load_all_agents) | Audit findings H6/H7/H8. Single docs PR could close all 3. |
| **P3** | Narrative refresh sweep | PLATFORM_WHAT_IT_IS 75-session gap + 13 narratives at Session 1158. |
| **P3** | Atlas fleet positioning audit | Strategic discussion not tactical fix. |
| **P3** | Beat schedule disabled tasks (5) classification | Rigby A4. |
| **P3** | Revenue pipeline aggregation audit | Rigby C5. |

## Session 1217 opener

**Start with Item 1 (~1h):** read `concrete_executor.py:511` + `agent_llm_integration.py:43-108`, decide delete vs fix per the leans documented in 00-START-NEXT-SESSION.md, ship as 2 PRs. Clears noise + warms up the session.

**Then Items 2 + 3 in parallel:**

- **Claude (Item 2):** populate `192a390c-…` via `deliverable_tool.append`. Schema source: grep `"name":` in `core/services/pa_tool_schemas.py`. Handler source: grep `self.register(` in `core/services/tool_dispatcher.py`. Diff → 59 handler names. For each, classify and cross-reference recent telemetry.

- **Rigby (Item 3):** populate `b92c41d0-…` via `deliverable_tool.append`. Query: `ops_tool.failure_signatures window=7d` → top failures. Then `ops_tool.execution_search status=failed window=7d` + `ops_tool.execution_detail` for exception class + handler.

**Cross-link:** When a top-10 failure handler appears in Item 2's 59-list, flag it in BOTH deliverables. That's the highest-leverage finding because it explains a chunk of the 74.5% success rate breach via the schema gap.

**Active conversation:** `pa-58737666f25741dc` (this thread). Continue here — has full audit + Chris's plan context.

---

**Closes:** The bounded self-direction experiment. Session 1217 opens with Chris's 3 picks + 2 placeholder deliverables ready to populate.
