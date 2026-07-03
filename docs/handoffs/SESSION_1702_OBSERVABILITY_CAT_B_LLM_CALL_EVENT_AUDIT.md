---
session: 1702
status: closed (Group 1700 Cat B LLMCallEvent child audit LANDED — SECOND child under Group 1700 per parent D72 P2 slot; audit doc landed `status: active` post-fold; Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence on arc pin `pa-e7fbacc996b34b44` — fresh SIGN isolation pin `pa-c3927ab78c52479a` minted per playbook §15 but routed-around by `tools/pa_local.sh:128` wrapper hard-code (S1600/S1700/S1701 precedent: arc pin doubles as SIGN pin); fresh SIGN pin retired at S1702 close per §16 with `updated_count=1, retired=true`; F1-F3 folds landed pre-commit; D48 preemptive stability-probe gate 19th arm HOLDING CLEAN — 14-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702 CONFIRMED per single-batch-4-question criterion; ARCHITECTURE_INDEX v44 → v45 with §1.48 S1702 registration + §8 timeline row + line-6 v45 preamble; OPEN_ARCS Group 1700 In-progress row current-child updated S1701 → S1702; arc pin retained through Group 1700 close at S1799; next session: S1703 Cat C AgentExecution per D72 P3 slot)
date: 2026-07-03
arc: Research Group 1700 (Observability / Telemetry / SLOs) — Cat B LLMCallEvent child audit; SECOND child session under Group 1700 per D72 P2 slot
category: research (playbook §11.2 child audit template + §13 six-parallel-Explore + §14 verifier-loop + §15 SIGN cycle 1)
head_commit_before: 2bb196e8 (main; post-S1701 arc-open merge)
head_commit_after: (this commit)
authors: Claude Code (Chris directed via short command "Start research group 1702")
---

# Session 1702 — Group 1700 Cat B LLMCallEvent Child Audit

> **Second child audit under Group 1700 (Observability arc).** Playbook §11.2 20-section template SECOND application under Group 1700 arc (first was S1701 Cat A). 6-parallel-Explore sweep + parent-Claude verifier-loop applied both pre-Explore and post-Explore. Rigby SIGN cycle 1 delivered SIGN-with-edits at Medium-High confidence via single-batch 4-question pattern (D48 19th arm HOLDING CLEAN).

## What shipped

### 1. Audit doc

- **`docs/research/domains/observability/1702_observability_cat_b_llm_call_event_audit.md`** (NEW; ~1090 lines post-fold)
- `status: active` after Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence
- `authority: child-audit`, `category: child_audit`, `session: 1702`, `child_slot: P2`, `domain_slug: observability`, `research_group: 1700`
- Applies playbook §11.2 20-section child audit template + §13 6-parallel-Explore + §14 verifier-loop discipline

### 2. Rigby SIGN cycle 1 folds (F1-F3, all landed pre-commit)

- **F1 (LOW) — CostTracking added to §17 as third LLM-cost store.** Rigby surfaced `CostTracking` model at `core/models_unified_system.py:6665` via `repo_tool.search` during Q1 coverage-completeness verification. Reinforces F1 severity — at least three parallel LLM-cost/telemetry stores coexist (LLMCallEvent + LLMCallLog + CostTracking). Added §17 "Other overlap candidates" row + expanded xx99 recommendation option (d) to triangulate all three stores.
- **F2 (MEDIUM) — §9 D74 axis contribution reframed "upgrade execution_id to NOT NULL + FK" from mandatory step into option set.** Rigby caught that NOT NULL + FK conflicts with the docstring rationale at `models_llm_telemetry.py:56-60` ("so telemetry survives AgentExecution row deletion"). Reframed to option set: (e.i) NOT NULL + FK (breaks survival-of-deletion rationale) OR (e.ii) shared correlation-view / join contract preserving nullability + non-FK autonomy. Fold applied to §1 F9 + §9 D74 axis contribution.
- **F3 (LOW) — Verification that Cat B/Cat D correlation R-item was already at §19 R6.** Rigby suggested adding an R-item; verification confirmed R6 already present as MEDIUM priority. No additional fold needed; noted in §20.5 for provenance.

### 3. ARCHITECTURE_INDEX v44 → v45

- **§1.48 `domains/observability/1702_observability_cat_b_llm_call_event_audit.md`** — new entry inserted before §1.47
- **§8 timeline row** — S1702 row inserted after S1701 row
- **Line-6 v45 preamble** — S1702 close summary + prior v44 preamble moved to "Prior v44 preamble"

### 4. OPEN_ARCS.md updates

- **Group 1700 In-progress row** — current-child updated S1701 (Cat A child) → S1702 (Cat B child); arc pin `pa-e7fbacc996b34b44` retained through Group 1700 close at S1799
- **Line-6 preamble** — S1702 close summary + prior S1701 close preamble moved to "Prior last_updated (2026-07-03 S1701 close)"

### 5. Rigby SIGN isolation pin discipline

- **Minted at S1702 open** — fresh SIGN pin `pa-c3927ab78c52479a` via Rigby `session_tool.create_fresh` with title "Session 1702 — Group 1700 Cat B LLMCallEvent audit — SIGN isolation"
- **Routed-around by wrapper** — `tools/pa_local.sh:128` hard-codes arc pin `pa-e7fbacc996b34b44`; SIGN cycle 1 landed on arc pin per S1600/S1700/S1701 parent-scoping precedent (arc pin doubles as SIGN pin)
- **Retired at S1702 close** — per playbook §16 with `updated_count=1, retired=true`

## Load-bearing findings (§1 Executive Summary)

- **F1 (CRITICAL, §17) — Multi-model LLM telemetry duplication.** `LLMCallEvent` (S1098, `core/models_llm_telemetry.py:30-115`, 16 fields, NO `cost`/`total_tokens`/`latency_ms`) coexists at HEAD with `LLMCallLog` (S697, `core/models_llm_routing.py:297-362`, HAS `cost` [line 335], `total_tokens` [line 331], `latency_ms` [line 332]) AND a **third store `CostTracking` at `core/models_unified_system.py:6665`** (surfaced by Rigby SIGN cycle 1 F1 fold). Largest single dedup candidate for Cat B.
- **F2 (CRITICAL, §14) — PA agentic loop uncovered.** `core/services/unified_pa_entrypoint.py` + `core/llm_enforcer.py` both import zero wrapper symbols (verified grep). PA GPT-5.2 function-calling agentic loop generates 1-20 LLM calls per user message and writes zero LLMCallEvent rows. Largest single coverage gap.
- **F3 (MEDIUM, latent) — `_extract_usage` provider-shape gap.** Wrapper handles OpenAI + Anthropic + generic dict. Gemini uses `prompt_token_count`/`candidates_token_count` (`llm_provider_registry.py:847-848`); Ollama uses `prompt_eval_count`/`eval_count` (`:969-970`). LATENT because all 23 production wrapper call sites at HEAD use `provider='openai'` or `provider='anthropic'`.
- **F4 (HIGH, §15) — No date-based retention for LLMCallEvent.** `_impl_cleanup_stale_llm_calls` at `core/tasks_agents.py:1659` sweeps stuck STARTED rows on a 10-minute cadence (S1221 P2 Tier 2 watchdog). No analog to Cat A's 30-day `CELERY_TASK_EVENT_RETENTION_DAYS` retention exists.
- **F5 (MODERATE, §13) — Wrapper adoption is 23 production sites across 8 files.** Verified inventory: content_writer_agent (3), code_review_agent (5), devops_agent (5), tasks_initiatives (5), market_intelligence_agent (2), campaign_orchestrator_agent (1), thinking_agent (1 async), curated_action_card_generator (1). BaseAgent + agent_router import only `LLMCallCancelled` exception.
- **F6 (MEDIUM, §14) — Parent scoping §3.B field list is drift.** Root cause is F1 — parent claimed field names actually match LLMCallLog schema. §7.4 anchor-update owed by xx99.
- **F7 (MEDIUM, §15) — PR #3 cancel is PARTIAL.** Provider adapters do not yet abort in-flight sockets per wrapper docstring `:18-21`. Cancel signal races with httpx read timeout.
- **F8 (LOW, §15) — PR #4 nested dispatch budget NOT SHIPPED.** Documented deferred scope.
- **F9 (D74 axis contribution, §9) — Cat B does NOT own a cross-model spine analog to Cat A's task_id.** `call_id` is Cat B's LLM-call-level singleton primitive (0 downstream models carry `llm_call_id`); `execution_id` is Cat C-owned spine primitive tagged onto Cat B rows (nullable by design, non-FK'd). Cross-cat correlation to Cat A goes via 3-hop chain.

## Verifier-loop corrections landed

- **Pre-Explore** — Direct-read of `core/models_llm_telemetry.py` established that no `cost` column exists on LLMCallEvent, contradicting parent scoping §3.B field claim. Established F6 drift going into Explores.
- **Post-Explore** — Direct-read of `core/models_llm_routing.py:297-362` established `LLMCallLog` (F1 sibling) HAS cost + total_tokens + latency_ms. Reveals F6 drift as F1 root cause.
- **Post-Explore** — Direct grep of `unified_pa_entrypoint.py` + `llm_enforcer.py` for wrapper imports returned 0 hits in both files, confirming F2 CRITICAL PA-path bypass.
- **Post-Explore** — Direct read of `_impl_cleanup_stale_llm_calls` at `tasks_agents.py:1659-` confirmed it targets `LLMCallEvent` (S1221 P2 Tier 2 watchdog). Reconciled Explore 3 vs Explore 6 conflict: LLMCallEvent has 10-min stuck-STARTED sweep; LLMCallLog has 30-day retention; Cat B has NO retention analog — F4 CONFIRMED HIGH.
- **Post-Explore** — Direct grep + count of production `llm_call_span` / `llm_call_async` invocations across all files: **23 production sites across 8 files** (Explore 2's 28 was over-count).

## Session close artifacts committed at S1702 close

```
docs/research/domains/observability/1702_observability_cat_b_llm_call_event_audit.md   [new; ~1090 lines post-fold; Cat B child audit; F1-F3 folds landed pre-commit; SECOND child under Group 1700]
docs/research/ARCHITECTURE_INDEX.md                                                    [modified — v44 → v45 with §1.48 S1702 registration + §8 timeline S1702 row + line-6 v45 preamble]
docs/research/OPEN_ARCS.md                                                             [modified — Group 1700 In-progress row current-child updated S1701 → S1702; line-6 preamble bumped]
docs/handoffs/SESSION_1702_OBSERVABILITY_CAT_B_LLM_CALL_EVENT_AUDIT.md                  [new — this file]
00-START-NEXT-SESSION.md                                                                [modified — S1702 Cat B CLOSED; next-session priority = S1703 Cat C AgentExecution]
```

Handoff: this file.

## Next session (S1703 Cat C AgentExecution)

Per D72 P3 slot + parent §5 sequence: **S1703 Cat C audit** — AgentExecution (with 3-class landmine).

Cat C canonical questions the child audit gathers evidence for:

- Which of the 3 `AgentExecution` classes is the actual canonical audit trail at HEAD? (Parent §3.C landmine: `intelligence/models/agent_execution.py:11` + `intelligence/models.py:587` + `core/models_unified_system.py:882` with stale S287 deprecation notice.) Which class does BaseAgent's `route()` wrapper write to? What is the correlation between them (FK / trace_id / none)?
- Is the S287 deprecation notice stale (all callers migrated), a live orphan, or masking a migration incomplete?
- **Inherits from Cat B S1702 F9:** which AgentExecution class does `LLMCallEvent.execution_id` correlate to? BaseAgent primary path status is UNKNOWN per S1702 §20.4 UNK-1 — grep shows only `LLMCallCancelled` import at `base_agent.py:4723`, not span usage.
- Is the S843 trace_id field usable as the canonical arc-wide correlation spine?
- Boundary discipline per parent §3.C: **P3 catalogs the 3 classes + names canonical + defines correlation contract; deprecation ADR is post-arc T-slot** (per §6.3 parked candidate).

**S1703 audit shape:**

- Playbook §11.2 20-section child audit template (child_slot: P3; domain_slug: observability; research_group: 1700).
- 6-parallel-Explore sub-agents per §13.
- Parent-Claude verifier-loop per §14 on load-bearing binary claims (pre-Explore + post-Explore).
- **Required full Rigby SIGN cycle 1** per playbook §15 stage-table child row.
- Fresh SIGN isolation pin per playbook §15 (arc pin `pa-e7fbacc996b34b44` continues as arc context; SIGN routing will land on arc pin per S1700/S1701/S1702 wrapper hard-code precedent).
- Applies parent D69-D74 + Cat A S1701 §9 axis evidence + Cat B S1702 F9 axis contribution (task_id singleton at Cat A + call_id singleton at Cat B + execution_id is Cat C-owned spine).
