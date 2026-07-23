# Session 2906 — Slice 2 Batch 2 · Actionless-Shape PA-Tools Sweep

**Date:** 2026-07-22 → 2026-07-23 (single terminal session, spans midnight UTC).
**Merged HEAD:** `40378bdf0` (PR [#3437](https://github.com/clwest/donkey-betz-platform/pull/3437)).
**Opened at HEAD:** `e59320017` (S2905 close cascade).
**Wrapper pin:** `pa-d4d24537a3bd4c53` (fresh from S2905 close; unchanged through S2906).
**Slice progression:** S2905 batch 1 (mixed pattern) → **S2906 batch 2 (actionless-only)** → S2907 batch 3 (small-actionful all-read-only, committed at T0 SIGN zoom-out fold).

---

## Ship shape

Doc-only per S2796 + one same-PR handler fix. 4 per-tool validation docs, 4 `TOOL_DEFAULTS` entries, 1 handler expansion, 1 gap-map + audit-doc regeneration.

**Files touched (9):**
- `core/services/td_handlers_agents.py` (M) — `_handle_system_alerts` bidirectional-param acceptance + enum-domain mapping; new class-level `_SEVERITY_SCHEMA_TO_INTERNAL` dict.
- `core/services/tool_action_metadata.py` (M) — 4 `TOOL_DEFAULTS` entries appended with batch-composition rationale + S2907 stress-test pointer in the S2906 block header.
- `docs/research/tools/validation/get_body_vitals_validation.md` (new)
- `docs/research/tools/validation/check_resource_budget_validation.md` (new)
- `docs/research/tools/validation/get_system_alerts_validation.md` (new)
- `docs/research/tools/validation/web_search_validation.md` (new)
- `docs/audits/PA_TOOLS_GAP_MAP.md` (M, autogen)
- `docs/PA_TOOL_AUDIT.md` (M, autogen)
- `docs/INDEX.md` (M, autogen)

---

## Gap-map delta

- `validated_full`: 16 → **20 (+4)**
- `untested`: 90 → **86 (-4)**
- `template_compliance pass`: 4 → **8 (+4)**
- `td_handlers_agents` untested slice: 21 → **17 (-4)**

Post-S2906 per-tool corpus: 30 per-tool validation docs (22 with explicit `## Covered actions`); 8 with `Template version: v1` marker.

---

## Scope discipline (per Rigby S2906 T0 SIGN AGREE-with-edits zoom-out fold)

Batch is intentionally uniform actionless. Validates three claims separated cleanly:

1. **Actionless doc shape under T1b template v1** — `## Covered actions` is intentionally empty because the schema exposes no action enum; §5 Findings + handler-trace evidence carry the load. All 4 docs include an explicit "3-part S2906 scope claim" paragraph in `## Covered actions` per Rigby T0 SIGN edit.
2. **`TOOL_DEFAULTS READ_ONLY` applicability when there is no action enum to iterate.** Uniform-only batch keeps the metadata-pattern-selection ledger clean — no per-action `TOOL_ACTION_METADATA` overrides added for actionless surfaces.
3. **Schema-vs-handler drift detection.** Three findings surfaced (see below); deferral of all three preserves batch-scope discipline.

**S2907 commitment:** small-actionful all-read-only tool (2-3 actions) to stress-test the handler-trace-evidence-required-for-`## Covered actions`-authoring claim under non-trivial action enumeration. Pointer recorded in all 4 docs' `## 6a. Next stress test`.

---

## Same-PR handler fix (per T0 SIGN §C + T1 SIGN B edit)

`_handle_system_alerts` at `core/services/td_handlers_agents.py:4822` now accepts BOTH:

- `severity` (schema-declared, preferred) — enum `critical/high/medium/low`.
- `severity_threshold` (legacy handler-only) — enum `info/warning/critical`.

Schema enum values map into the handler's internal domain via new class-level `_SEVERITY_SCHEMA_TO_INTERNAL`:

- `critical` → `critical`
- `high` → `warning`
- `medium` → `warning`
- `low` → `info`

Unknown values on BOTH paths (schema + legacy) normalize to the historical `warning` default. The legacy-path normalization is the **Rigby T1 SIGN B edit fold** — pre-B-edit, unknown legacy values fell through to `threshold_idx = 0` (silently downgrading to `info`), which was a subtle regression from stated intent. Post-fold, both paths converge on `warning`.

**Post-fold branch coverage (8-case simulation via `manage.py shell`):**

```
OK payload={}                                          -> warning
OK payload={'severity': 'critical'}                    -> critical
OK payload={'severity': 'high'}                        -> warning
OK payload={'severity': 'BOGUS'}                       -> warning
OK payload={'severity_threshold': 'critical'}          -> critical
OK payload={'severity_threshold': 'HIGH'}              -> warning   # B edit
OK payload={'severity_threshold': 'info'}              -> info
OK payload={'severity': 'critical', 'severity_threshold': 'info'} -> critical
```

**Post-merge live Rigby dispatch verification (3 cases):**

1. `get_system_alerts` (zero-arg): `severity_threshold=warning`, `alert_count=1` — legacy default path ✓
2. `get_system_alerts severity=critical`: `severity_threshold=critical`, `alert_count=0` — schema-preferred path ✓
3. `get_system_alerts severity=high`: `severity_threshold=warning`, `alert_count=1` — high→warning mapping ✓

Handler fix confirmed live in worker post-recycle.

---

## Ledger candidates surfaced this batch (deferred)

Three drift findings surfaced during handler-trace authoring; per Rigby T0 + T1 SIGN, deferring all three preserves batch-scope discipline. All three are documented in the respective tool's `## 5` Findings block with classification.

| Tool | Finding | Class |
|---|---|---|
| `get_body_vitals` | Schema declares empty `properties`; handler reads undeclared `systems` + `include_details`. | Silent-parameter-invisibility |
| `web_search` | Schema declares only `query`; handler reads undeclared `limit` + `num_results` (legacy alias). | Silent-parameter-expansion |
| `get_system_alerts` | Schema declares `limit`; handler ignores it. | Schema-declared-but-handler-ignored |

**Rigby T1 SIGN zoom-out — trend candidate:** "3 drift finds in 4 tools (75%) is not noise floor. Meaningful local signal that schema/handler drift is common in the unvalidated tool surface, especially in small handlers where 'optional knobs' get added ad hoc or schema fields become vestigial." Treated as systemic trend candidate; **NOT yet a substrate-arc trigger off a single 4-tool sample**. Watch across next 3-5 batches; if drift rate persists, promote to Playbook amendment (drift taxonomy + response rule) or dedicated cleanup arc.

**Substrate-arc-scope escalation trigger (recorded):** if 3-5 subsequent sweep batches sustain ≥50% drift-find rate, promote to arc. Below that threshold, treat as ambient tool-surface debt to bank via Ledger + doc §5.

---

## Rigby joint SIGN (S2906)

**T0 SIGN (routed pre-authoring):** AGREE-with-edits.

- A) AGREE — batch composition (4 actionless from `td_handlers_agents` untested slice).
- B) AGREE — actionless-shape claim confirmed via harness artifact reads.
- C) AGREE-with-edits — same-PR handler fix directed for `get_system_alerts` severity drift; `get_body_vitals` undeclared-params deferred to Ledger + doc §5.
- D) AGREE — `TOOL_DEFAULTS` READ_ONLY applicability correct for actionless surfaces.
- **Zoom-out (round 1):** Pushback — proposed swap of 3 actionless + 1 small actionful to stress handler-trace-evidence claim. Claude counter-proposed keeping 4-actionless-only this batch + committing to S2907 small-actionful stress test. Rigby T0.5 AGREE-with-edits: keep the 4-actionless batch, add explicit 3-part scope claim to each doc + S2907 stress-test pointer. Preserves ledger-risk discipline (mixed-pattern coexistence count stays at 1/2 sessions).

**T1 SIGN (routed post-authoring, 9 verification `tool_runs`):** AGREE-with-1-edit.

- A) AGREE — 3-part scope claim + S2907 pointer present in all 4 docs.
- B) AGREE-with-1-edit — handler fix behavior verified; legacy `severity_threshold` unknown-value normalization added same-PR to eliminate silent-info-downgrade regression.
- C) AGREE — `TOOL_DEFAULTS` shape correct + header comment carries rationale.
- D) AGREE — gap-map per-tool table matches claim.
- E) AGREE — Ledger candidate deferral correct given batch scope discipline.
- **Zoom-out (round 2):** systemic drift trend candidate, monitor across 3-5 batches.

Zero rubber-stamp SIGN across both rounds — every verdict grounded in a substantive `tool_run` (harness artifact reads, doc reads, gap-map grep, handler-code read, tool_action_metadata read).

---

## Metadata-pattern-selection ledger state (S2905 zoom-out)

- **Mixed-pattern sweep session count:** 1 (S2905) / total 2 post-substrate sweep sessions (S2905 + S2906).
- **S2906 contribution:** ZERO. Batch is uniform-TOOL_DEFAULTS only.
- **Distance to lint trigger (≥3 mixed sessions without rule-based justification):** 2 more mixed sessions.

Escalation deferred; no action required.

---

## Sweep progress after S2906

**Slice 1 — `td_handlers_ops`:** 13 tools ✓ (9 sweep + 4 substrate-adjacent post-Row 161).
**Slice 2 — `td_handlers_agents` (25 total):**
- Batch 1 (S2905): 4 tools ✓ (mixed-pattern proof).
- **Batch 2 (S2906): 4 tools ✓ (actionless-only proof).**
- Remaining: 17 untested. Small-actionful stress batch (S2907) → then continue at ~5 tools/session accelerated pace.
**Slice 3 — `td_handlers_core` (22 tools):** queued behind Slice 2.
**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Sweep pace observed post-substrate:** S2905 = 4 tools; S2906 = 4 tools. Extrapolated remaining ~12-16 sessions at 5 tools/batch accelerated pace once uniform-shape variance is fully exercised.

---

## S2907 opens with

**Recommended first action:** Slice 2 batch 3 — one small-actionful all-read-only tool from remaining `td_handlers_agents` untested list, per S2906 T0 SIGN zoom-out commitment. Candidates: `bpaas_tool`, `davinci_tool`, `reasoning_engine_tool` (need to inspect action enum + safety class per handler-trace before pick).

**Bundle:** 4-5 more actionless / small-actionful tools if pace holds. Aim for 5 tools/batch to sustain accelerated cadence.

**D6 MORATORIUM STILL IN FORCE.**

Alternative Step 1 candidates unchanged from S2905 close:
- Phase 0 heading fixes (8 tools) — doc-only PR that clears remaining parity mismatches.
- Slice 1.5b autopilot mutations — staged-enforcement session per pre-commit note.

**Recommend Slice 2 batch 3 (small-actionful stress test)** — closes the S2906 T0 SIGN zoom-out fold's next-batch commitment; then can bundle Phase 0 heading fixes + Slice 1.5b into S2908+.

---

## Forward-carry ledger rows (S2906 additions)

- **`get_body_vitals` schema empty properties + handler reads `systems` + `include_details`** — silent-parameter-invisibility class. Deferred; watch for pattern recurrence.
- **`web_search` undeclared `limit` + `num_results` (legacy alias)** — silent-parameter-expansion class. Deferred; sibling to above.
- **`get_system_alerts` schema-declared `limit` handler-ignored** — schema-declared-but-handler-ignored class. Deferred; inverted from the first two.
- **Systemic schema/handler drift trend** — 3/4 tools this batch. Trigger for Playbook amendment (drift taxonomy + response rule): sustained ≥50% drift-find rate across 3-5 additional sweep batches.

---

## For fuller S2892 → S2906 sweep arc context

See:
- **This handoff (current):** `docs/handoffs/SESSION_2906_SLICE_2_BATCH_2_ACTIONLESS_SWEEP.md`
- **S2905 handoff:** `docs/handoffs/SESSION_2905_SLICE_2_BATCH_1_ACCELERATED_SWEEP.md`
- **S2904 handoff:** `docs/handoffs/SESSION_2904_T1B_TEMPLATE_EXTRACTION.md`
- **S2903 handoff:** `docs/handoffs/SESSION_2903_T1A_PHASE_2_METADATA_SEED.md`
- **S2902 handoff:** `docs/handoffs/SESSION_2902_T1A_AUTO_HARNESS_SCAFFOLD.md`
- **S2901 handoff:** `docs/handoffs/SESSION_2901_T1C_LOW_SIGNAL_AUDIT.md`
- **S2900 handoff:** `docs/handoffs/SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md`
- **S2906 per-tool validation docs (this session):**
  - `docs/research/tools/validation/get_body_vitals_validation.md`
  - `docs/research/tools/validation/check_resource_budget_validation.md`
  - `docs/research/tools/validation/get_system_alerts_validation.md`
  - `docs/research/tools/validation/web_search_validation.md`
- **T1b canonical template:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` + `docs/research/tools/validation/*.md`
- **Rigby Tool Gap Ledger deliverable:** workspace `b4503364-2573-4401-9e28-61a739e0ce50`, deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`.
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`

For older session history (S1-S2891), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
