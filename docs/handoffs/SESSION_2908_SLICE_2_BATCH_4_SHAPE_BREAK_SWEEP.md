# Session 2908 — Slice 2 batch 4 shape-break sweep (4 tools)

**Date:** 2026-07-23
**Merged PR:** [#3441](https://github.com/clwest/donkey-betz-platform/pull/3441)
**Merge commit:** `a17aa0ba6`
**Ship shape:** Doc-only (S2796) + metadata seed (`tool_action_metadata.py`) — no schema or handler changes.
**Session outcome:** First **SHAPE-BREAK batch** post-substrate-arc, per Chris-ratified Fold A commitment from S2907 close. 4 mixed-safety tools scoped to READ_ONLY subset.

---

## What shipped

### 4 validation docs (T1b sweep variant, v1)

- `docs/research/tools/validation/bpaas_tool_validation.md` — 2 R covered (`get_schema`, `get_example`), 2 M excluded (`create_project`, `generate_close_pack`)
- `docs/research/tools/validation/davinci_tool_validation.md` — 5 R covered (`health`, `status`, `result`, `jobs`, `grades`), 1 M excluded (`render`)
- `docs/research/tools/validation/obs_tool_validation.md` — 3 R covered (`health`, `status`, `last`), 3 M excluded (`start`, `stop`, `upload_last`)
- `docs/research/tools/validation/media_tool_validation.md` — 3 R covered (`list`, `detail`, `stats`), 1 IRREVERSIBLE excluded (`delete` — **first IRREVERSIBLE in sweep corpus**)

Total: 13 READ_ONLY actions covered, 7 mutation actions excluded via §5a Mutation containment (per Rigby T0 SIGN edit — MANDATORY §5a for any tool with excluded mutations).

### Metadata seed

`core/services/tool_action_metadata.py` — Pattern C (per-action records for all 20 actions; **no** `TOOL_DEFAULTS` additions this ship).

- 13 READ_ONLY records (2 bpaas + 5 davinci + 3 obs + 3 media)
- 6 MUTATION records (bpaas 2 + davinci 1 + obs 3)
- 1 IRREVERSIBLE record (media.delete)

Pattern C rationale (documented in the seed comment block at ~line 335): chosen over Pattern A (`TOOL_DEFAULTS` + mutation overrides) to keep S2908 UNIFORM per-action. Does **not** increment the S2905 metadata-pattern-selection lint counter — mixed-pattern coexistence stays at 1/3 sweep sessions (distance to trigger: 2 more mixed sessions).

### Gap map update

Regenerated via `python manage.py build_pa_tool_audit --gap-only`:

- **untested:** 83 → **79** (-4)
- **validated_partial:** 3 → **7** (+4)
- **validated_full:** 23 (unchanged — correctly distinct from S2907 which used validated_full for all-READ_ONLY-covered tools)
- **Total corpus classified:** 27 tools validated_partial+full, 7 doc-unknown, 79 untested + 44 agent_via_run_agent + 1 meta_no_handler = 161 ✓

### Harness output

- Per-tool artifacts: `docs/audits/pa_tools/harness_output/{bpaas,davinci,obs,media}_tool.json`
- Corpus summary: `docs/audits/pa_tools/harness_output/summary.json` — 116 tools, 76 READ_ONLY dispatched (up from 63; +13 this batch), 480 skipped for missing metadata

---

## Post-merge live-dispatch verification (per PLAYBOOK-7.4.4)

Workers recycled via `make celery-recycle` after merge; single READ_ONLY dispatch per tool through Rigby:

1. **`bpaas_tool` action=get_schema** → SUCCESS, `{success, action, schema}` (BUILD_PACKET_SCHEMA returned). 5ms.
2. **`davinci_tool` action=grades** → SUCCESS, `{action, count: 11, grades: [...]}` (COLOR_GRADE_PRESETS returned). 9ms.
3. **`obs_tool` action=health** → error envelope `{ok: false, action, error: {code: OBS_DISABLED}, error_code: legacy_error}`. No crash. 2ms. (`_obs_enabled()` false in local env — expected short-circuit path.)
4. **`media_tool` action=stats** → SUCCESS, `{action, images: 10, videos: 0, audio: 4, total: 14}`. 21ms.

All 4 tools' `TOOL_ACTION_METADATA` seed is live in worker.

---

## Rigby joint SIGN cycle (both rounds tool-grounded — zero rubber-stamp)

### T0 SIGN (batch composition + shape-break framing)

**Verdict:** AGREE-with-edits. 12 verification tool_runs — Rigby caught a Q2 count ambiguity in the initial dispatch ("2/6/6/4" ambiguous between READ_ONLY-count and total-actions); clarified same-round without proceeding to AGREE prematurely.

**Edits ratified:**
1. Use existing `validated_partial` gap-map category (already at §17); no schema proliferation needed.
2. §5a Mutation containment MUST include when a tool has excluded mutations; MAY omit only if schema-pure READ_ONLY or full-action coverage.
3. `dependency_surface` doc note (`internal | external_bridge | third_party_api`) — kept as validation-doc annotation this ship, NOT a metadata field.
4. Keep 4-tool batch (13 READ_ONLY actions parity with S2907); enforce one-dispatch-per-action-per-tool-per-harness-run.

### T1 SIGN (authored docs + metadata seed + gap map)

**Verdict:** AGREE. 5 verification tool_runs — 2 docs read end-to-end (bpaas + davinci), metadata seed block, gap map headline, obs_tool row search.

### Zoom-out folds captured (per PLAYBOOK-6.10.7)

- **Fold Q6 (T0):** Coupling / precedent risks named — (a) category ambiguity debt (solved by adopting validated_partial), (b) doc-section ratchet creep (solved by conditional-mandatory §5a rule), (c) harness semantics drift (long-term direction: move safety classification to code-truth via `tool_action_metadata.py`, keep docs as evidence narrative). Rigby's Q6 folds shaped the T0 edits.
- **Fold Q4 (T1):** Fold B drift-rate data point #3 — rate DROPPED from 87.5% (S2906+S2907) to 75% this batch. Rigby's batch-selection-bias hypothesis PARTIALLY supported: uniform-safe-args probably inflated the number, but drift IS systemic across shape variants (>50% sustained across all 3 data points). Joint Claude+Rigby recommendation for S2909: open systemic-drift cleanup arc scoped to (1) harness outcome classifier fix + (2) bridge availability precheck.

---

## Substrate findings — deferred (§Related in docs, NOT new arc scope)

- **T1a harness classification drift, second batch of instances** — 5 more instances this ship (`davinci_tool.health` + `davinci_tool.jobs`; `obs_tool.health` + `obs_tool.status` + `obs_tool.last`) confirming the S2907 orm_inspect pattern (`status_code=200` + `{ok:false, error, error_code}` inline envelope misclassified as `success`). Cumulative: 9 instances across 4 tools. Substrate-arc-scope; deferred.
- **Bridge-unreachable-during-harness detection gap** — davinci_tool + obs_tool both `external_bridge` surface; both surfaced bridge-unreachable envelopes at harness time. Harness has no bridge-availability precheck. Substrate-arc-scope; deferred.
- **First IRREVERSIBLE-classified action** (`media_tool.delete`) — no soft-delete, no confirm flag. Confirmation-flow ADR candidate flagged in `media_tool_validation.md` §Related. Design-arc-scope; deferred.
- **`obs_tool` OBS_DISABLED vs BRIDGE_UNREACHABLE envelope distinction** — post-merge dispatch showed `OBS_DISABLED` envelope shape (`_obs_enabled()` false short-circuits before hitting the bridge). Harness earlier surfaced the same shape; the doc §6.1 annotation is directionally correct but conflates the two error branches. Doc-fix-scope; deferred to S2909 as a small-doc-touch.

---

## Fold B drift-rate trend (3 data points)

| Session | Batch shape | Drift rate | Notes |
|---|---|---|---|
| S2906 | Uniform actionless (4 tools) | ~87.5% (combined with S2907) | Actionless-only proof |
| S2907 | Uniform small-actionful READ_ONLY (3 tools) | ~87.5% (combined with S2906) | Small-actionful proof; classification drift discovered |
| **S2908** | **Mixed-scoped-to-READ_ONLY-subset (4 tools)** | **75%** | **Shape-break proof; drift-rate PARTIALLY dropped** |

**Interpretation:** drift-rate dropped 12.5 points with mixed-scoped shape but stayed above 50%. Rigby's batch-selection-bias hypothesis is PARTIALLY confirmed — uniform-safe-args was inflating the number, but drift IS systemic across shape variants. Above the "3-data-point 50%" trigger — advance to remediation.

**S2909 recommendation (joint Claude+Rigby, awaiting Chris D-verdict):** open systemic-drift cleanup arc scoped to two highest-leverage sources:
1. **Harness outcome classifier fix** — treat `{error, error_code}` at HTTP 200 as `soft_error` outcome (not `success`). This alone would collapse most of the "classification drift" findings.
2. **Bridge availability precheck** — preflight `external_bridge` dependency surfaces (OBS bridge, resolve_node) so harness distinguishes "bridge down" vs "tool bug".

Secondary (optional experiment after fixes land): one reverse-control uniform-READ_ONLY batch to quantify whether drift-rate drops below 50% post-remediation.

---

## Sweep progress tracker

**Slice 2 — `td_handlers_agents` (25 tools):**
- S2905 batch 1: 4 tools ✓
- S2906 batch 2: 4 tools ✓
- S2907 batch 3: 3 tools ✓
- **S2908 batch 4: 4 tools ✓** (SHAPE-BREAK — mixed-scoped-to-READ_ONLY-subset)
- **Remainder:** 10 tools untested (was 14 at S2907 close; -4 this ship).

**Total corpus remaining:** ~61 tools untested + partials. Post-substrate sweep pace observed: S2905=4, S2906=4, S2907=3, S2908=4. Extrapolated ~10-13 more sessions at 4-5 tools/batch accelerated pace.

---

## References

- **Parent commitment:** `project_s2908_batch_4_shape_break_commitment` (memory)
- **Parent zoom-out fold ledger:** S2907 Fold A + Fold B captures in `SESSION_2907_SLICE_2_BATCH_3_SMALL_ACTIONFUL_SWEEP.md`
- **T1b canonical template:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **Playbook v0.9.0:** `docs/ENGINEERING_PLAYBOOK.md` (§6.10.7 zoom-out ask discipline; §7.4.4 recycle-after-merge)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- **S2907 handoff:** `docs/handoffs/SESSION_2907_SLICE_2_BATCH_3_SMALL_ACTIONFUL_SWEEP.md`

## Workspace mirrors (Rigby-authored at close per `feedback_rigby_writes_workspace_deliverables`)

- **S2908 Content Mirror:** _(pending — Rigby to author at close in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)_
- **S2908 Ratification Envelope:** _(pending — same workspace)_
- **S2907 workspace mirrors** (Rigby-authored at S2908 open — pending Rigby dispatch this session or S2909 open): still owed per `feedback_twin_deliverable_at_every_ratification`.
