# Session 2955 — Golden Evals Slice 1: SystemIntelligenceAgent YAML

**Session:** 2955
**Date:** 2026-07-25
**HEAD at open:** `c26c79d88`
**HEAD at close:** `d2acf9c92` (after PR #3551 merge, before close-cascade PR)
**Arc:** Golden Evals (S2954 open, this is arc-slice 1 of an 8-YAML Tier-1 build-out)

---

## Headline

Shipped `evals/tier1/system_intelligence_agent.yaml` (463 lines, PR #3551) — first Tier-1 canonical prompt suite. Establishes the `evals/` tree at repo root and locks in `canon_version=1` substrate precedent for the remaining 7 Tier-1 YAMLs. Rigby T1→T3 SIGN cycle. Chris D-verdict `yes` on both ship + substrate-freeze.

---

## What shipped

### PR #3551 — `feat(s2955): Golden Evals Tier-1 slice 1 — SystemIntelligenceAgent YAML`

Single new file at repo root:

- **`evals/tier1/system_intelligence_agent.yaml`** — 463 lines, 13 prompts, all 5 fault-injection categories covered (5 happy + 2 each of tool_timeout / data_unavailable / ambiguous_input / bad_input).

**Grounding:**
- 30d volume DB-verified via Rigby ORM 2026-07-25: 37 executions matching `owner_agent="SystemIntelligenceAgent"`, `created_at >= 2026-06-25T00:00:00Z`.
- Actual production prompt (37/37 30d, 44/44 all-time): `"Overnight platform health: SLO breaches, failing tasks, queue backlog, fleet degradation"` — covered as `sia_happy_05_production_autonomous`.
- Two observed real failure modes each get a dedicated test:
  - `"Connection error."` (OpenAI API mid-tool-call, 4 of 5 last failures) → `sia_timeout_02_openai_connection_error`
  - `"Task timed out after 60 minutes (no heartbeat)"` (Celery watchdog kill) → `sia_timeout_01_aggregator_slow`

**No worker impact** — pure spec file, `PLAYBOOK-7.4.4` recycle-after-merge does not apply.

---

## Arc-precedent substrate frozen at canon_version=1

Chris D-verdict `yes` on Decision 2 freezes these choices for the remaining 7 Tier-1 YAMLs:

1. **`schema_version: 1` + `canon_version: 1`** at file top.
2. **`canonical_field_mapping`** declares `native` vs `derived` per canon field:
   - `summary` = native from `AgentResult.message`
   - `evidence_pointers` = derived via rule `sia_v1_tool_calls_plus_item_ids`
   - `health_status` = derived via rule `sia_v1_counts_and_success` (4-way enum from success + critical_count + warning_count)
   - S2956 validators MUST consult this block — no invented mappings.
3. **`fault_injection` is effect-based**: `component` (`python_service | openai | db | ...`) + `fault.{type, params}` (`latency | unavailable | bad_payload | error`) with `python.{...}` as backend-adapter appendix. Portable to spider HTTP / Redis / Celery beyond Python-mock-only.
4. **`one_of` acceptance-criteria capped at ≤2 branches** with mandatory `why` strings — prevents S2957 harness debugging pain from combinatorial branch matching.

---

## Rigby SIGN cycle

- **T1 (tool-grounded verification)** — Rigby ran `orm_inspect_tool.describe_model` + `count_by` + `filter` on `AgentExecution`. **Verdict: F-BLOCKING** on my "30d volume = 33" claim; her DB query returned 37. Reconciliation: I used `now - timedelta(days=30)` bound (~29d 20h → 33); she used `>= 2026-06-25T00:00:00Z` bound (calendar 30d → 37). Both correct for their bounds; YAML now uses her authoritative full-30d.
- **T2 (zoom-out)** — **Verdict: WARN** on 4 arc-precedent risks:
  - (a) Validator-facing mapping in file header → could become the real API contract via silent shims. Fix: explicit `mapping_source: native|derived` per canon field with named derivation rules.
  - (b) `fault_injection` shape reads Python-mock-flavored (`exception`/`delay_ms`). Fix: effect-based contract (`component` + `fault.{type, params}`) with `python.{...}` as adapter appendix.
  - (c) `one_of` acceptance criteria could sprawl into combinatorial debugging pain. Fix: cap at ≤3 branches (I used ≤2), require `why` string per branch.
  - (d) YAML sets an implicit "prompt YAML is product contract" precedent. Fix: explicit `schema_version` + `canon_version`.
  - All 4 folded pre-ship.
- **T3 (revision verdict)** — **PASS**. One minor smell flagged (bound-annotation on "44 all-time / 8 distinct" claim); addressed inline.

---

## Chris D-verdict

Ratified `yes` on both decisions via Chat UI 2026-07-25:
- **Decision 1:** Ship this YAML as PR #3551.
- **Decision 2:** Freeze substrate precedent (schema_version=1, canon_version=1, canonical_field_mapping shape, fault_injection component/fault taxonomy, one_of ≤2-branches-with-why policy) for remaining 7 Tier-1 YAMLs.

---

## Twin mirrors (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)

- **Content mirror (engineering truth):** `1f90340e-8001-4632-ba1a-ead249074721` (`initiative_phase_doc`, `category='governance'`). **Ledger #16 re-hit** (8th cumulative) — flagged diagnostic on create; ORM-cleared post-create.
- **Ratification envelope (governance truth):** `0c73707c-6a05-43f8-a33d-abca3f000d20` (`ratification_record`, `category='governance'`). Diagnostic clean on create.

---

## Rigby Tool Gap Ledger

- **Ledger #16 (deliverable_tool.create diagnostic-flag on initiative_phase_doc)** — **8th cumulative hit** at Mirror 1 create. Established ORM-clear recipe applied.
- **Ledger #16 sub-observation** — the ORM-clear recipe attempts to clear 5 diagnostic_* fields (status, code, notes, detected_at, resolved_at). Only 2 exist on the current `Deliverable` model (`diagnostic_status`, `diagnostic_code`). The other 3 either never existed on this model or have been removed since the recipe was written. Recipe should be updated to reflect current model shape. Not blocking; noted for next model-drift audit.
- **Ledger #17 candidate (Chat UI relay gap, from S2954)** — **RE-HIT this session**. Chris ratified via Chat UI; Rigby did not relay back to terminal. Chris relayed manually. Second observation; the pattern is consistent enough to escalate from "candidate" to full ledger row at next opportunity.

---

## Post-merge state

- **HEAD:** `d2acf9c92`
- **Worker state:** unchanged. No `make celery-recycle` required.
- **Gap-map:** unchanged, `100 validated_full / 2 untested` (`agent_capability_drift_tool` + `agent_job_status`, both untested-by-design at ship time).
- **Drift scanner:** unchanged shape (83/92/59/1 → 77+2).

---

## For fuller context

- **Arc-open scoping doc:** `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md`
- **Arc-open handoff:** `docs/handoffs/SESSION_2954_GOLDEN_EVALS_ARC_OPEN.md`
- **This session's shipped file:** `evals/tier1/system_intelligence_agent.yaml`
- **A1 Wedge scoping deliverable (still open):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope:** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
