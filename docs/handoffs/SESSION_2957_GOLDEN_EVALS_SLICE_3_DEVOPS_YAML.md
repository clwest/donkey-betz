# SESSION 2957 — Golden Evals Tier-1 slice 3: DevOpsAgent YAML

**Date:** 2026-07-25
**Session:** S2957
**Arc:** Golden Evals (S2954+ open)
**Slice:** 3 of 8 Tier-1 YAMLs
**HEAD at close:** `98ba0e06b`
**PR shipped:** [#3555](https://github.com/clwest/donkey-betz-platform/pull/3555)

---

## What shipped

`evals/tier1/devops_agent.yaml` — 612 lines, 13 prompts, third canon_version=1 file.

**Coverage:** 5 happy path + 2 each tool_timeout / data_unavailable / ambiguous_input / bad_input.

**Substrate reference:** `evals/tier1/research_agent.yaml` @ `c8815cd38`.

---

## DB grounding

Via Rigby ORM T1 SIGN (2026-07-25):

| Claim | Value | Query |
|---|---|---|
| 30d execs (calendar-30d bound) | 13 (11 pass / 2 fail) | `owner_agent=DevOpsAgent, created_at>=2026-06-25T00:00:00Z` |
| All-time execs | 25 (23 pass / 2 fail) | `owner_agent=DevOpsAgent` |
| 30d distinct task strings | 13 (every prompt singleton) | client-side dedupe |
| All-time real failures | 2, both same failure mode | `error_message__gt=''` |
| Failed rows with empty error_message | 0 (CLAIM 5) | integrity check |

Both failures = same Celery watchdog kill on morning_brief smoke tests (2026-06-25). Modeled as `devops_timeout_01_watchdog_kill`.

## Honest coverage limits (called out in YAML header)

1. **Thin traffic** — 13 30d vs SIA's 37 and ResearchAgent's 37. Most fault-injection cases constructed from dependency graph rather than replayed from production.
2. **Shape mismatch** — 30d traffic is mostly advisory health-check queries (no-tool GPT path), NOT the config-generation tools that are DevOpsAgent's declared value proposition. Happy-path prompts cover BOTH shapes explicitly: `devops_happy_01` = real advisory prompt; `devops_happy_02..05` = config-generation dispatches exercising the tool path.
3. **Failure sample = 2** — both same task variant, same failure mode. Zero variety in observed failures.

---

## Rigby SIGN cycle T1→T3

**T1 (tool-grounded)** — all 5 claims TOOL-GROUNDED PASS via `orm_inspect_tool`. CLAIM 5 (0 failed rows with empty error_message) confirms "real failures = non-empty error_message" assumption holds for DevOpsAgent.

**T2 (zoom-out)** — 4 folds surfaced per S2771/S2782 discipline.

**T3 (fold dispositions):**

| Fold | Concern | Disposition |
|---|---|---|
| 1 | health_status dual-path (advisory vs config-gen) enum add | **DEFERRED to S2962 canon_v2** — mirrors S2956 Fold #5 pattern (health_status over-degrade for open-world agents); canon_version=1 substrate frozen at S2955 |
| 2 | acceptance_criteria strictness (exact 4-stage list) | **FOLDED IN-PR** — predicate renamed `_as_superset` + explicit LLM-variation note in `devops_happy_02.notes` |
| 3 | fault_injection selector Python-mock-specific | **FOLDED IN-PR** — moved `devops_data_unavail_01` selector from `openai.resources.chat.completions.Completions.create` → `core.agents.devops_agent.DevOpsAgent._create_docker_config` (service-level, matches SIA + ResearchAgent canon) |
| 4 | volume header timeout emphasis | **NO ACTION** — agrees with claim |

All 4 T3 PASS. Claude+Rigby agreed before Chris D-verdict route.

---

## Chris D-verdict

**Yes** via Chat UI 2026-07-25 (manual relay — **Ledger #17 4th observation**, promoted to full ledger row this session).

---

## Twin mirrors (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)

| # | Purpose | ID | Notes |
|---|---|---|---|
| OP 1 | Content mirror | `a9e6e865-21f6-4f1c-82e6-36e171e25a3c` | `initiative_phase_doc`, `category=governance`. Ledger #16 re-hit **10th cumulative** — sticky-cleared via `deliverable_tool.clear_diagnostic` |
| OP 2 | Ratification envelope | `2751b29b-824a-40cd-bb51-e6bc69fecf03` | `ratification_record` intent (Rigby normalized to `document`), `category=governance`. Diagnostic clean on create |
| OP 3 | Ledger #17 full-row promotion | `db316865-d08c-4cc1-9d8e-cfac249e8c89` | parent = Rigby Tool Gap Ledger `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` |
| OP 4 | Design task (Chat UI relay wiring) | `f3f140f9-87bf-488b-8757-eab5d8058f45` | parent = Rigby Tool Gap Ledger |

---

## Rigby Tool Gap Ledger updates

**RE-HIT — Ledger #16, 10th cumulative** — `deliverable_tool.create` diagnostic-flag bug on `initiative_phase_doc`. Sticky-cleared. Consistent behavior across 10 sessions.

**PROMOTED — Ledger #17 full-row** — Rigby Chat UI does NOT relay Chris ratification responses back to Claude terminal. Observed S2954 candidate → S2955 2nd → S2956 3rd → **S2957 4th (promoted)**. Design task queued as OP 4 above. Customer parallel: Rigby is A1 SaaS product surface + A4 consulting demo substrate — this UX gap = every A1 buyer who tries to approve a Rigby recommendation via Chat UI hits the same friction.

**Rigby residual observations (informative-only, not blocking):**
1. Calendar-30d boundary clarity — YAML text already says "calendar-30d anchored" per S2955 precedent; passes.
2. Failure-mode wording nuance — `devops_timeout_01` uses `SoftTimeLimitExceeded` (agent-side lens) matching ResearchAgent canon; the observable is cleanup-task-marked-failed (external lens). Both legitimate; canon-consistent.

---

## Deferred queue (updated at S2957 close)

**S2957 additions:**
- **Fold #1 (S2957 T2) — `health_status` dual-path enum add for advisory-vs-config-gen agents** — DevOpsAgent's advisory path (no tool_calls, message-only) currently collapses into `healthy`. Rigby suggests a distinct `healthy_no_tools_expected` enum value. Track for `canon_version=2` arc-close discussion at S2962 alongside S2956 Fold #5 (open-world agent over-degrade).

**Carry forward from S2956:**
- Ledger #16 recipe drift (dual-route documentation).
- `orm_inspect_tool` distinct-count guardrail (`distinct_values_capped` or `hash_distinct` action).
- Fold #5 (S2956) — `health_status` derivation over-degrade for open-world agents (canon_version=2 at S2962).
- Fold #6b (S2956) — Tier-1 canon uniformity review (arc-close S2962).

Full carry-forward from S2955/S2954 preserved in prior handoffs.

---

## Files shipped

| File | Change |
|---|---|
| `evals/tier1/devops_agent.yaml` | **NEW** — 612 lines, 13 prompts |

**Post-merge:** PR #3555 was spec-only (YAML config), no worker recycle required per PLAYBOOK-7.4.4 (applies to code-shipping PRs).

---

## S2958 first action

**S2958 first-action = author `evals/tier1/workflow_orchestration_agent.yaml`** — 4th of 8 Tier-1 slices. Substrate references: any of the 3 shipped canon_version=1 YAMLs (SIA, ResearchAgent, DevOpsAgent).

Fresh session should first-action verify wrapper pin freshness + run drift scanner + gap-map lint pre-flight (universal open sequence), then pull WorkflowOrchestrationAgent 30d + all-time volume snapshot via Rigby ORM before authoring.

---

## Reference

- **Arc-open scoping:** `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md`
- **S2955 handoff:** `docs/handoffs/SESSION_2955_GOLDEN_EVALS_SLICE_1_SIA_YAML.md`
- **S2956 handoff:** `docs/handoffs/SESSION_2956_GOLDEN_EVALS_SLICE_2_RESEARCH_YAML.md`
- **Substrate references:**
  - `evals/tier1/system_intelligence_agent.yaml` @ `d2acf9c92` (canon_version=1 original)
  - `evals/tier1/research_agent.yaml` @ `c8815cd38` (2nd reference, 26-prompt human-diverse shape)
  - `evals/tier1/devops_agent.yaml` @ `98ba0e06b` (3rd reference, thin-traffic + shape-mismatch coverage limits)
