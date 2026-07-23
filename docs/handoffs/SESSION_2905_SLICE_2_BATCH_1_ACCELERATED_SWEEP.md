# SESSION 2905 — Slice 2 batch 1 (`td_handlers_agents`) — first accelerated PA-tools sweep post-substrate

**Date:** 2026-07-22 (S2905 open + close, same day)
**Head at session close:** merged PR #3435 at `7d763b504`
**PR shipped:** [#3435](https://github.com/clwest/donkey-betz-platform/pull/3435) — `S2905 Slice 2 batch 1 — td_handlers_agents (first accelerated sweep post-substrate)`
**Session pin:** `pa-9eac10fed0454faa` (retired at close)
**Next session pin (wrapper bumped to):** `pa-d4d24537a3bd4c53`

---

## What shipped

First accelerated sweep batch after the Row 161 substrate arc close (T1c ✓ S2901 + T1a ✓ S2902-S2903 + T1b ✓ S2904). Four tools from `td_handlers_agents.py` validated end-to-end via the T1a auto-harness + T1b template v1 opt-in.

**Tools (4, 12 actions total):**

| Tool | Actions | Safety | Metadata pattern |
|------|---------|--------|------------------|
| `gates_tool` | list, stats, detail | all READ_ONLY | `TOOL_DEFAULTS` |
| `pilots_tool` | list, stats, detail | all READ_ONLY | `TOOL_DEFAULTS` |
| `cost_telemetry_tool` | summary, top_agents, recent_calls | all READ_ONLY | `TOOL_DEFAULTS` |
| `revenue_tracker_tool` | stats, list, create | 2 READ_ONLY + 1 MUTATION | per-action `TOOL_ACTION_METADATA` |

**Ship shape:** doc-only (S2796 shape). No regression tests written; T1a harness output artifacts are the runtime evidence.

## Substrate multiplier — validated

The batch validates the substrate-arc close claim (S2904 §Ledger row 161 mitigated). The T1a auto-harness + T1b template + gap-map lint substrate delivered exactly what the parent-scoping doc predicted:

- **Zero manual dispatch.** Harness generated per-action response-shape captures for all 12 actions in a single `python manage.py pa_tool_validate_harness <tool>` invocation per tool.
- **§Covered actions + §Golden-path pre-populated** from JSON artifacts + safety-class resolution. Author time went to interpretation + failure-mode analysis, not manual dispatch note-taking.
- **First 4 `pass` verdicts** appear in the gap map — the ratchet-and-warn lint transitions from theoretical to observed.

**Gap map delta:**

| Metric | Pre-batch | Post-batch | Delta |
|--------|-----------|------------|-------|
| `validated_full` | 12 | 16 | +4 |
| `template_compliance` pass | 0 | 4 | +4 |
| `untested` | 94 | 90 | -4 |
| Per-tool docs with `Template version:` marker | 0 | 4 | +4 |

## Rigby joint SIGN (S2905 T1)

Routed via `bash tools/pa_local.sh` — SIGN dispatch returned 6 verification tool_runs (Rigby read each of the 4 validation docs + `tool_action_metadata.py` + `revenue_tracker_tool.json` artifact + gap map). Zero rubber-stamp signal.

**Verdicts:**

- **A) Validation docs (v1 frontmatter + Covered actions):** AGREE
- **B) `tool_action_metadata.py` entries:** AGREE
- **C) Gap map `pass=4`:** AGREE
- **D) `revenue_tracker_tool.json` `create=skipped_mutation`:** AGREE
- **Zoom-out ask (PLAYBOOK-6.10.7):** **AGREE-with-edits** — folded same-PR before merge: added pattern-selection rule + coexistence risk statement to `core/services/tool_action_metadata.py` header comment block above `TOOL_DEFAULTS`. Rule: uniform-safety → `TOOL_DEFAULTS`; mixed-safety → per-action `TOOL_ACTION_METADATA`. Risk: without the rule stated, future authors mix arbitrarily; if drift emerges across ≥3 sweep sessions, promote to lint (flag per-action records shadowing tool-default with same safety class).
- **Ledger candidates (3):** AGREE to log (non-blocking).

## Zoom-out fold captured (per PLAYBOOK-6.10.7)

**Fold — mixed-pattern first-batch coupling risk** caught by Rigby SIGN zoom-out → `same_pr_mitigated`. Choosing 3 tools with `TOOL_DEFAULTS` + 1 tool with per-action metadata as the FIRST accelerated batch was intentional (exercise both patterns), but the mixed shape means the batch validates two things at once: substrate multiplier AND metadata-pattern comparison. Rigby's zoom-out reframed this as "risk of early normalization" — future authors could mix arbitrarily without a stated rule. Same-PR mitigation shipped: pattern-selection rule now lives in the code header, adjacent to the map itself. If ≥3 sweep sessions mix patterns without rule-based justification, promote to a lint (flag redundant per-action records shadowing tool-defaults with same safety class).

## Ledger candidates surfaced (3, non-blocking)

1. **`pilots_tool` undeclared `action=running`** — handler at `td_handlers_agents.py:5181` accepts `action='running'` (returns `PilotExecution.filter(status='running')`) but schema enum at `pa_tool_schemas.py:267` lists only `list, stats, detail`. Rigby cannot reach this branch via function-call dispatch (schema validation blocks). Two remediations: (a) drop the handler branch if unused, (b) add `running` to the schema enum. Operator impact today: zero. Deferred.
2. **`cost_telemetry_tool` silent `limit` cap at 50** — `min(payload.get('limit', 10), 50)` at `td_handlers_agents.py:4873` clamps silently. Same class as `repo_tool` F-RT-2/F-RT-5 silent-truncation patterns. Rigby scanning top spenders sees the top 50 even if she asked for 100 — no response signal. Deferred (cross-tool consistency batch-close).
3. **`revenue_tracker_tool` `status='confirmed'` default drift** — handler default at `td_handlers_agents.py:1690` is not in schema enum `[potential, pending, received, cancelled]`. `create` calls that omit `status` write `Revenue` rows with a status value that doesn't match the schema-declared set. Two remediations: (a) update handler default to `'potential'` or `'pending'` (schema-conformant), (b) extend schema enum to include `'confirmed'`. Deferred pending Rigby SIGN on which direction to take.

**Ledger disposition:** all 3 recorded for future triage. None block this batch's ship.

## Rigby workspace-mirror handoff

Twin workspace mirror still pending at this handoff's writing — Rigby to write:

- **Content mirror deliverable** (this handoff's engineering content), category `initiative_phase_doc`
- **Ratification envelope deliverable** (SIGN cycle + zoom-out fold + verdicts), category `governance`, deliverable_type `ratification_record`

Both into Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` per `feedback_rigby_writes_workspace_deliverables` (Chris directive S2835: Rigby writes workspace deliverables, Claude writes repo files).

## Files touched this ship

- `core/services/tool_action_metadata.py` — +47 lines: pattern-selection rule header + 3 TOOL_DEFAULTS + 3 per-action revenue_tracker_tool records
- `docs/audits/PA_TOOLS_GAP_MAP.md` — regenerated
- `docs/audits/pa_tools/harness_output/` — 5 artifacts (4 per-tool + 1 summary) refreshed
- `docs/research/tools/validation/gates_tool_validation.md` — new (T1b template v1)
- `docs/research/tools/validation/pilots_tool_validation.md` — new (T1b template v1)
- `docs/research/tools/validation/cost_telemetry_tool_validation.md` — new (T1b template v1)
- `docs/research/tools/validation/revenue_tracker_tool_validation.md` — new (T1b template v1)

## Next session (S2906)

**Recommended first action:** Slice 2 batch 2 — pick 4-5 more read-only tools from the 21 remaining in `td_handlers_agents.py`. Good candidates: `get_body_vitals` (0 actions), `check_resource_budget` (0 actions), `get_system_alerts` (0 actions), `web_search` (0 actions), `orm_inspect_tool` (10+ actions, larger surface). The 4-actionless-tools sub-batch would validate the T1b template shape for tools without action enums (§Covered actions handling).

**Alternative Step 1 candidates:**
- Phase 0 heading fixes (8 tools) — doc-only, would clear all remaining parity mismatches
- Slice 1.5b autopilot mutations — staged-enforcement session per pre-commit note (§00-START)

## D6 moratorium — still in force

No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs. No R1a-shaped proposals. No v1→v2 schema/template bump without substrate-arc-scoped SIGN. No agent-substrate validation arc.
