# Session 2907 — Slice 2 Batch 3 · Small-Actionful All-READ_ONLY PA-Tools Sweep

**Date:** 2026-07-23 (single terminal session).
**Merged HEAD:** `706e7d60a` (PR [#3439](https://github.com/clwest/donkey-betz-platform/pull/3439)).
**Opened at HEAD:** `b02f08016` (S2906 close cascade).
**Wrapper pin:** `pa-b8f868545b484b0c` (fresh from S2906 close; unchanged through S2907).
**Slice progression:** S2905 batch 1 (mixed pattern) → S2906 batch 2 (actionless-only) → **S2907 batch 3 (small-actionful all-READ_ONLY)** → S2908 batch 4 (shape-break required per Rigby T0 zoom-out E + Chris ratification).

---

## Ship shape

Doc-only per S2796. Zero same-PR handler fix required this batch (contrast S2906 which needed the `_handle_system_alerts` bidirectional-param fix). 3 per-tool validation docs, 3 `TOOL_DEFAULTS` entries, gap-map + audit-doc regeneration.

**Files touched (10):**
- `core/services/tool_action_metadata.py` (M) — 3 `TOOL_DEFAULTS` READ_ONLY entries appended after the S2906 batch, with S2907 batch header referencing S2906 T0 SIGN Fold A commitment + S2908 shape-break commitment.
- `docs/research/tools/validation/ml_analysis_validation.md` (new)
- `docs/research/tools/validation/voice_clone_tool_validation.md` (new)
- `docs/research/tools/validation/orm_inspect_tool_validation.md` (new)
- `docs/audits/PA_TOOLS_GAP_MAP.md` (M, autogen)
- `docs/PA_TOOL_AUDIT.md` (M, autogen)
- `docs/INDEX.md` (M, autogen)
- `docs/audits/pa_tools/harness_output/ml_analysis.json` (M, harness regen)
- `docs/audits/pa_tools/harness_output/voice_clone_tool.json` (M, harness regen)
- `docs/audits/pa_tools/harness_output/orm_inspect_tool.json` (M, harness regen)

---

## Gap-map delta

- `validated_full`: 20 → **23 (+3)**
- `untested`: 86 → **83 (-3)**
- `template_compliance pass`: 8 → **11 (+3)**
- `td_handlers_agents` untested slice: 17 → **14 (-3)**

Post-S2907 per-tool corpus: 33 per-tool validation docs (25 with explicit `## Covered actions`); 11 with `Template version: v1` marker.

---

## Batch composition ratified (Chris Option B, 2026-07-23)

Chris ratified **Option B** (3-tool tight-signal batch) over Option A (4-tool with `pipeline_orchestrator_tool` filler). Reasoning: the 1-action `pipeline_orchestrator_tool` didn't materially advance the stress-test claim (essentially actionless-in-spirit), so dropping it kept the batch signal cleaner without breaking the accelerated sweep pace narrative.

Selection criteria applied to remaining 17 `td_handlers_agents` untested tools:
1. **Uniform READ_ONLY safety class** — no mixed pattern (would push mixed-pattern count to 2/3 sweep sessions, materially closer to ≥3-session lint trigger).
2. **Small-actionful (2-5 actions with real enum)** — actionless-shape tools rejected (already covered S2906); mutation-mixed tools rejected (would need scope-limit doc mechanism deferred to S2908).
3. **Downstream verification-independent** — no handler branches requiring auth, external service dispatch, or file-system side effects beyond ORM reads.

**Rejected by mixed safety class (8):** `bpaas_tool`, `davinci_tool`, `obs_tool`, `brainstorm_tool`, `opportunity_manager_tool`, `task_manager_tool`, `media_tool`, `video_history_tool`.

**Rejected as actionless (5):** `reasoning_engine_tool`, `web_fetch_tool`, `schedule_followup`, `legal_doc_drafter_agent`, `universal_agent_tool`.

**Ratified batch (3):**
| Tool | Actions | Register site | Handler entry |
|---|---|---|---|
| `ml_analysis` | 3 (status, decision_pattern, detect_opportunity) | `tool_dispatcher.py:398` | `td_handlers_agents.py:1711` |
| `voice_clone_tool` | 5 (list, detail, clone_requests, marketplace, stats) | `tool_dispatcher.py:406` | `td_handlers_agents.py:4312` |
| `orm_inspect_tool` | 5 (list_models, describe_model, get, filter, count_by) | `tool_dispatcher.py:327` | `td_handlers_agents.py:592` (benchmark — S2866 substrate build) |

Total: 13 actions covered.

---

## Rigby joint SIGN (S2907)

**T0 SIGN (routed pre-authoring, 9+ verification `tool_runs`):** AGREE-with-edits.

- A) AGREE — batch composition genuinely uniform READ_ONLY.
- B) AGREE — pre-sweep drift signals accurate (`ml_analysis` `model_type`/`data` invisibility; `voice_clone_tool` marketplace `limit` clamp).
- C) AGREE-with-1-edit — `orm_inspect_tool` benchmark framing softened to "expected lower drift likelihood due to recent SIGN + explicit contract, audited with same rigor" (prevents selection-bias framing).
- D) AGREE — `TOOL_DEFAULTS` uniform READ_ONLY correct; no per-action override justified. Note: `orm_inspect_tool` is "sensitive read" in data-exposure terms but that's handled by allowlist/redaction, not safety-class metadata.
- **Zoom-out E:** substantive precedent-setting warning. See §Zoom-out folds below.

**T1 SIGN (routed post-authoring, 15+ verification `tool_runs` across T0+T1):** AGREE-with-2-edits.

- A) AGREE-with-1-edit — `voice_clone_tool` anonymous-user language softened from "fail-open" to "defense-in-depth conditional; would need audit before opening to un-authenticated callsites." Folded same-batch.
- B) AGREE — `TOOL_DEFAULTS` shape correct; uniform-only ratio maintained (2/3 post-substrate sweep sessions).
- C) AGREE — `## 6a. Next batch shape` accurately reflects S2908 shape-break commitment across all 3 docs.
- D) AGREE (defer both new substrate findings) — 1-edit refinement to `orm_inspect_tool` harness classification wording ("status_code-only heuristic misclassifies inline `{ok:false}` envelopes" rather than "harness semantically expected success"). Folded same-batch.
- **Zoom-out E:** substantive. See §Zoom-out folds.

Zero rubber-stamp SIGN across both rounds — every verdict grounded in substantive `tool_run` (harness artifact reads, 3 validation-doc reads, metadata file read, ORM cross-checks).

---

## Zoom-out folds captured (per PLAYBOOK-6.10.7)

### Fold A (T0 zoom-out E, `future_trigger` + Chris-ratified same-day commitment)

**Rigby T0 zoom-out E:** "You're starting to accrete a repeatable comfort pattern: uniform READ_ONLY + multi-action tools + stress-test Template v1. It's clean, safe, and great for validating the authoring format — but it risks overfitting the sweep to the easiest shape and building a false sense of closure." Three coupling risks identified:

1. **Template v1 gets implicitly optimized for uniform READ_ONLY batches.** Later mixed-safety or gated-write tools will feel like exceptions when they're actually the norm across remaining ~100 tools.
2. **Drift-find rate becomes selection-biased.** If we keep picking tools with obvious pre-signals, the "systemic drift trend" narrative inflates. If we keep avoiding harder surfaces, we under-detect real operational risk. Either direction, the metric becomes coupled to curation rather than ecosystem truth.
3. **The hard governance muscle stays unexercised** — mixed-safety tools where we cover only the READ_ONLY subset; gated-write tools where we cover only the dry_run path.

**Chris D-verdict 2026-07-23:** Option 1 ratified — ship S2907 batch 3 as-is (uniform 3 tools + T0 folds), but S2908 batch 4 MUST break the uniform pattern. *"if this is our Batch 3 let's go with 1 and knock it out but in our next session we need to change the shape."*

**S2908 acceptable shapes (Rigby T1 zoom-out ranking):**
- **PREFERRED:** Mixed-tool scoped to READ_ONLY subset only, documented in `## Covered actions`. Tests Template v1's mixed-pattern representation without taking write risk.
- Alternate: Gated-write tool covering only the dry_run path.

Both acceptable per Chris's ratification. Rigby preferred the mixed-tool shape because it "most directly breaks the 'uniform-only' precedent while staying safe and forcing the documentation template to handle mixed-safety tools honestly."

**Memory:** `project_s2908_batch_4_shape_break_commitment.md` (durable across session close).

### Fold B (T1 zoom-out E, `future_trigger`)

**Rigby T1 zoom-out E:** with 3/3 drift this batch and 87.5% average across S2906+S2907, it's tempting to treat "systemic drift" as fully proven — but some of that rate is plausibly driven by intentionally minimal-safe-args harness runs that specifically expose missing-arg schema/handler gaps. **Recommendation:** for S2908, don't optimize the batch pick to reinforce the drift-rate narrative; keep the shape-break exactly as ratified so we test the real hypothesis (uniform-shape overfitting hides mixed-surface realities), not the meta-narrative.

Recorded as `future_trigger`. Do NOT let S2908 batch pick optimize the drift-rate story; let it land honestly at whatever rate the mixed-surface batch produces.

---

## Drift findings surfaced this batch (deferred per batch-scope discipline + D6 moratorium)

3/3 tools (100%) surfaced at least one drift finding. Data point #2 for S2906 Fold B systemic-drift trend candidate. Cross-batch average across S2906+S2907: **87.5%** (7/8 tools).

| Tool | Finding | Class |
|---|---|---|
| `ml_analysis` | Schema declares `model_type` (handler ignores). Handler-required `data` schema-missing for `decision_pattern` + `detect_opportunity`. | Silent-parameter-invisibility (sibling to S2906 `get_body_vitals` / `web_search`) |
| `voice_clone_tool` | `marketplace` action silent `limit` clamp at 30. Plus `list` + `clone_requests` hard-cap at 20 / 10 in handler while schema declares tunable `limit`. | Silent-truncation (F-RT-2 class, sibling to `cost_telemetry_tool`) + schema-declared-but-handler-ignored |
| `orm_inspect_tool` | Tool itself clean. NEW substrate finding: T1a harness `status_code`-only heuristic misclassifies inline `{ok: false, error, error_code}` envelopes as `success`. 4/5 dispatches reported `expected_outcome=success` when they were validation errors. | Harness classification drift (S2907 novel — first batch to surface) |

**NEW harness-substrate ledger candidate:** MLEngine per-invocation NLP-model load stalls harness ~5min without `SKIP_NLP_MODELS=1`. Not a defect of `ml_analysis` — the T1a harness reboots MLEngine per invocation which triggers DistilBERT via `transformers.pipeline`. Remediation options: (a) T1a harness sets `SKIP_NLP_MODELS=1` when dispatching `ml_analysis`; (b) MLEngine lazy-loads `sentiment_analyzer` on first sentiment-scoring call. Deferred to substrate-arc scope.

**Substrate-arc-scope escalation trigger (from S2906):** if 3-5 subsequent sweep batches sustain ≥50% drift-find rate, promote to arc. S2906 = 75% + S2907 = 100% = 2/2 batches over threshold. One more batch past S2907 hits the 3-batch escalation floor. Do NOT act off two data points; watch S2908.

---

## Metadata-pattern-selection ledger state (S2905 zoom-out)

- **Mixed-pattern sweep session count:** 1 (S2905) / total 3 post-substrate sweep sessions (S2905 + S2906 + S2907).
- **S2907 contribution:** ZERO. Batch is uniform-`TOOL_DEFAULTS` only (no per-action `TOOL_ACTION_METADATA` overrides added).
- **Distance to lint trigger (≥3 mixed sessions without rule-based justification):** 2 more mixed sessions.

Escalation deferred; no action required. Note: S2908 shape-break commitment may add a mixed-tool entry — if that lands, mixed-pattern count moves to 2/4 sessions.

---

## Post-merge live verification

`bash tools/pa_local.sh` dispatches after `make celery-recycle` (per PLAYBOOK-7.4.4):

1. `orm_inspect_tool action=list_models` → clean allowlist return (Initiative, LLMCallLog, Deliverable, Agent, etc.). ✓
2. `voice_clone_tool action=stats` → clean aggregate `{my_voices: 0, marketplace_total: 0, my_total_uses: 0, my_total_revenue: "0"}`. ✓
3. `ml_analysis action=status` → clean `MLEngine` health snapshot `{mlx_available: false, device: mps, models_loaded: 4, user_profile_active: true, memory_usage: 8.0GB, nlp_models_ready: false}`. ✓ (8.5s latency — DistilBERT load on first post-recycle dispatch; caches thereafter).

All 3 tools dispatched successfully; TOOL_DEFAULTS seed is live in worker.

---

## Sweep progress after S2907

**Slice 1 — `td_handlers_ops`:** 13 tools ✓ (9 sweep + 4 substrate-adjacent post-Row 161).
**Slice 2 — `td_handlers_agents` (25 total):**
- Batch 1 (S2905): 4 tools ✓ (mixed-pattern proof).
- Batch 2 (S2906): 4 tools ✓ (actionless-only proof).
- **Batch 3 (S2907): 3 tools ✓ (small-actionful all-READ_ONLY proof).**
- Remaining: 14 untested. S2908 shape-break batch (mixed-scoped-to-READ_ONLY-subset OR gated-write-dry_run-only) → continue after.
**Slice 3 — `td_handlers_core` (22 tools):** queued behind Slice 2.
**Slice 4 — `td_handlers_gateway` (17 tools):** queued.
**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Sweep pace observed post-substrate:** S2905 = 4, S2906 = 4, S2907 = 3. Accelerated cadence sustained. Extrapolated remaining ~10-14 sessions at ~4-5 tools/batch once shape-break exercise completes at S2908-S2909.

---

## S2908 opens with

**Recommended first action (per Chris ratification 2026-07-23):** Slice 2 batch 4 — SHAPE-BREAK. Do NOT open with another uniform-READ_ONLY multi-action batch.

**Rigby-preferred shape (T1 zoom-out E ranking):** Pick one mixed-safety tool (both READ_ONLY and WRITE actions), cover only the READ_ONLY actions in the validation doc, document the scoping explicitly in `## Covered actions`.

Concrete candidates from the S2907 rejected-mixed list:
- `bpaas_tool` — cover `get_schema` + `get_example` only (skip `create_project` + `generate_close_pack` mutations).
- `davinci_tool` — cover `health` + `status` + `result` + `jobs` + `grades` only (skip `render` mutation).
- `obs_tool` — cover `health` + `status` + `last` only (skip `start` + `stop` + `upload_last` mutations).
- `media_tool` — cover `list` + `detail` + `stats` only (skip `delete` mutation).

**Alternate shape (Chris-ratified, Rigby-second-choice):** Pick one gated-write tool (dry_run/confirm pattern) and cover only the dry_run branch. Candidates: `autopilot_tool` (Slice 1.5b if paired with mutation staged-enforcement), `security_containment_plan` (S1228 PR-A gate — dry_run branch alone).

**Bundle:** 3-5 tools if pace holds. If S2908 batch spans multiple mixed-scoped tools, keep the `## Covered actions` explicit-scoping note consistent across each doc so the pattern is discoverable.

**D6 MORATORIUM STILL IN FORCE.**

Alternative Step 1 candidates unchanged from S2906/S2907 close:
- Phase 0 heading fixes (8 tools) — doc-only PR that clears remaining parity mismatches.
- Slice 1.5b autopilot mutations — staged-enforcement session per pre-commit note.

**Recommend Slice 2 batch 4 shape-break with mixed-scoped-to-READ_ONLY-subset composition** — closes both the Chris-ratified S2908 commitment AND advances Rigby's preferred zoom-out ranking. Phase 0 + Slice 1.5b can bundle into S2909+.

---

## Forward-carry ledger rows (S2907 additions)

- **`ml_analysis` schema-declared `model_type` unused + handler-required `data` schema-missing** — silent-parameter-invisibility class. Deferred; sibling to S2906 `get_body_vitals` / `web_search` (3 tools now confirmed with this pattern).
- **`voice_clone_tool` marketplace `limit` silent-clamp at 30 + `list` / `clone_requests` hard-cap at 20 / 10** — silent-truncation + schema-declared-but-handler-ignored classes. Deferred.
- **T1a harness classification drift — `status_code`-only heuristic misclassifies inline `{ok: false}` envelopes as success** — NEW substrate finding, S2907 novel. Remediation options: harness inspects response body for `ok: false` OR per-tool "response-envelope-shape" hint OR tool converts to TOOL_EXCEPTION (last option NOT recommended — breaks self-contained fallback design). Deferred to substrate-arc scope.
- **Harness-substrate: MLEngine NLP boot cost stalls harness ~5min** — deferred to substrate-arc scope.
- **Systemic schema/handler drift trend** — 3/3 tools this batch, 7/8 across S2906+S2907 (87.5%). Trigger for Playbook amendment (drift taxonomy + response rule): sustained ≥50% across 3-5 additional sweep batches. Current: 2 batches over threshold. One more past S2907 hits 3-batch floor.

---

## For fuller S2892 → S2907 sweep arc context

See:
- **This handoff (current):** `docs/handoffs/SESSION_2907_SLICE_2_BATCH_3_SMALL_ACTIONFUL_SWEEP.md`
- **S2906 handoff:** `docs/handoffs/SESSION_2906_SLICE_2_BATCH_2_ACTIONLESS_SWEEP.md`
- **S2905 handoff:** `docs/handoffs/SESSION_2905_SLICE_2_BATCH_1_ACCELERATED_SWEEP.md`
- **S2904 handoff:** `docs/handoffs/SESSION_2904_T1B_TEMPLATE_EXTRACTION.md`
- **S2903 handoff:** `docs/handoffs/SESSION_2903_T1A_PHASE_2_METADATA_SEED.md`
- **S2902 handoff:** `docs/handoffs/SESSION_2902_T1A_AUTO_HARNESS_SCAFFOLD.md`
- **S2901 handoff:** `docs/handoffs/SESSION_2901_T1C_LOW_SIGNAL_AUDIT.md`
- **S2900 handoff:** `docs/handoffs/SESSION_2900_ROW_161_SUBSTRATE_ARC_OPENED.md`
- **S2907 per-tool validation docs (this session):**
  - `docs/research/tools/validation/ml_analysis_validation.md`
  - `docs/research/tools/validation/voice_clone_tool_validation.md`
  - `docs/research/tools/validation/orm_inspect_tool_validation.md`
- **T1b canonical template:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` + `docs/research/tools/validation/*.md`
- **Rigby Tool Gap Ledger deliverable:** workspace `b4503364-2573-4401-9e28-61a739e0ce50`, deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`.
- **S2907 workspace mirrors** (authored by Rigby at S2907 open per `feedback_rigby_writes_workspace_deliverables` — to be updated for this batch at S2908 open):
  - S2906 Content Mirror: `f9578144-0020-4cf9-b532-bbde2b892623`
  - S2906 Ratification Envelope: `deeca50b-9fa4-47a2-8d3a-fe0a974856e4`
- **S2908 commitment memory:** `project_s2908_batch_4_shape_break_commitment.md`.
- **Parent strategic discovery:** `docs/research/platform/S2841_STRATEGIC_DISCOVERY_WHAT_DBZ_ACTUALLY_IS.md`

For older session history (S1-S2891), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
