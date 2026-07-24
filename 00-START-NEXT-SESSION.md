# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2919 CLOSE → S2919 SHIPPED Slice 4 batch 2 (discord + distribution + ats + narrative) via template-preservation swap after Q3 mutation-scan disqualified vip_invite. **8/17 shipped.** **Post-merge live verify surfaced pre-existing narrative table dev-env drift** (logged as Rigby Tool Gap Ledger entry, not batch-2 defect). **S2920 OPENS WITH SLICE 4 BATCH 3** — D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2919 close).** Batch 2 shipped 4 pure-read gateway tools (discord 91 · distribution 93 · ats 93 · narrative 107 lines) via S2796 doc-only shape. Rigby T0 SIGN 2-turn cycle grounded in 15+ `repo_tool` receipts — zero rubber-stamp. Turn 1 DISAGREE walked back 00-START's `~80-line` small-tier framing (materially wrong when boundary math computed from full `_handle_*` census). Q3 verb-scan surfaced 3 mutations in the originally-proposed vip_invite (`.create` L973, `.save` L1006/1009), triggering template-preservation swap to narrative. Post-merge live verify: 3/4 clean (discord 5ms / distribution 14ms / ats 17ms all envelope-shape ✓); narrative surfaced pre-existing dev-env drift — `narrative` table missing from local DB despite migration recorded applied. Not batch-2 defect; logged as Rigby Tool Gap Ledger entry `5c84e75a` for engineering-backlog triage.

**PRs shipped this session:**
- u-d-b PR [#3468](https://github.com/clwest/donkey-betz-platform/pull/3468) — Slice 4 batch 2 (gateway small-tier read-only quartet), merged at `be14744153fe`.
- u-d-b PR `<TBD>` — S2919 close cascade (handoff + 00-START refresh + wrapper pin bump + narrative doc §6 amendment).

**Tools shipped (4 — Slice 4 batch 2):**
- `discord_tool` (3 actions: status/commands/cogs — filesystem read + regex parse) · `distribution_tool` (4 actions: platforms/listings/revenue/stats — pure ORM SELECT+Sum/Count) · `ats_tool` (4 actions: keywords/optimizations/templates/stats — pure ORM SELECT+Sum/Avg/Count) · `narrative_tool` (5 actions: narratives/shifts/evidence/alerts/help — pure ORM SELECT+FK JOIN). All at `td_handlers_gateway.py` (lines 723 / 1700 / 2600 / 1453 respectively). No TOOL_DEFAULTS or TOOL_ACTION_METADATA entries (all pure READ_ONLY; auto-classifier upgrades to `validated_full`).

**Rigby joint SIGN (2-turn cycle + Q4 zoom-out, zero rubber-stamp):**
- T0 SIGN turn 1: 10 `repo_tool` runs (per-tool `def _handle_*` census on all 13 remaining Slice 4 tools). Q1 DISAGREE — refused to sign batch composition on unverified spans; required corrected boundary math.
- T0 SIGN turn 2: 7 more `repo_tool` runs (completed missing anchors: narrative/proactive/self_awareness/profile/repo/analytics + paged read confirming total_lines=2693). Corrected span table showed 00-START right on cockpit=431 + vip_invite=81 + discord=91 + distribution=93 + conceptforge=84; WRONG on calendar (claimed 86, actual 166) + podcast (claimed 89, actual 251); OMITTED mobile/narrative/proactive/self_awareness/profile from small-tier classification. Q1 revised AGREE-with-edits (preserve batch-1 pure-read template + narrative swap for vip_invite). Q2 AGREE (0/4 first-hop literals). Q3 AGREE-with-edits (3 mutation verbs in vip_invite triggered narrative swap; final quartet 0/4 mutation verbs; narrative tail 1553-1560 verified clean). Q4 zoom-out: codify probe-first Q1 discipline + per-tool A/N confirm + post-merge live-verify latency budget; prune rigid 2-turn ritual; cockpit gets dedicated later batch.
- Post-merge live verify: 3/4 clean at ≤20ms; narrative surfaced dev-env drift (documented above).

**Sweep progress (post-S2919):**
- **Slice 4 (`td_handlers_gateway`):** 8/17 shipped. Batch 2 CLOSED.
- Remaining 9: calendar (166) · cockpit (431) · conceptforge (84) · mobile (127) · podcast (251) · proactive (140) · profile (188) · self_awareness (118) · vip_invite (81).
- Total corpus untested: 43 → **39** (batch 2 flipped 4 untested → full via auto-classifier).
- Gap map: **60 full · 10 partial · 7 unknown · 39 untested** (validation-doc counts post-regen).
- Session cumulative pace: 4 tools / 1 batch / 1 session (with in-depth 2-turn T0 SIGN + probe-first correction + narrative swap + 4-dispatch post-merge live verify + dev-env drift investigation).

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3468 recycled clean at `sha=be14744153fe`: 5 fresh workers (default + pa + long_running + broadcast + code_jobs) + beat, zero surviving old PIDs.

Full session context: `docs/handoffs/SESSION_2919_SLICE_4_BATCH_2.md`.

---

## S2920 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 4 batch 3 T0 SIGN

**No blocking Chris D-verdict.** Slice 4 batch 2 shipped clean (3/4 live-verified; narrative deferred to Rigby Tool Gap Ledger). 9 gateway tools remain untested. Route to Rigby with tool-grounded probe first:

**Q1 batch composition:** Pick 3-4 tools for Slice 4 batch 3. Corrected boundary-math span table from S2919 T0 SIGN turn 2:
- Small-tier: vip_invite (81, has 3 mutations per S2919) · conceptforge (84)
- Medium-tier read-only: self_awareness (118) · mobile (127) · proactive (140) · calendar (166) · profile (188)
- Large-tier: podcast (251) · cockpit (431)

Options:
- (a) medium-tier read-only pilot (mobile + self_awareness + proactive + calendar, 4 tools 118-166 lines) — tests batch-2 doc-only shape at 2x span
- (b) mix small+medium (conceptforge + self_awareness + proactive + calendar, 84/118/140/166) — hedges size drift
- (c) shape-break batch — vip_invite (mutation-capable, 3 verbs known) + 2-3 read-only companions — first Slice 4 mutation experience per S2914 precedent

Recommend (a) or (b); vip_invite mutation-batch should wait for cockpit-dedicated-batch shape ratification.

**Q2 Appendix N/A applicability continued watch:** Gateway-wide 0/17 first-hop literal established at S2918. Batch 2 per-tool grep confirmed 0/4. Re-confirm per-tool for batch 3 candidates.

**Q3 first-batch shape:** Doc-only S2796 shape as default. Verb-scan each candidate at `def _handle_*` boundary for `.save(`/`.create(`/`.update(`/`.delete(`. Any mutation-capable tool triggers §5a deferral or shape-break decision.

**Q4 zoom-out (required per feedback_zoom_out_ask_per_rigby_sign):**
- Legacy-error envelope now at 12× corroborated. Semantic nuance surfaced at S2919 live-verify: observed `error_code='legacy_error'` is a VALUE on a post-S2909 envelope field, not the ABSENCE of the field. Does this change the "wait for substrate arc" framing?
- Batch-2 template-preservation swap (vip_invite → narrative) worked cleanly. Should mutation-scan-swap become explicit template guidance?
- Any accretion risks going 8/17 → 12/17 (past the 2/3 mark of Slice 4)?
- Cockpit (431 lines) plan: still defer, or open dedicated batch alongside batch 3?

### Alternative Step 1 candidates

- **Cockpit-only batch** — 431 lines, dedicated batch shape per S2914 mutation-heavy-single-tool precedent. Not blocking; can wait until small/medium drained.
- **narrative_tool dev-env drift fix** — Rigby Tool Gap Ledger entry logged at S2919; requires ~30 min migration replay + verification. Engineering task, not sweep.
- **Legacy-error envelope substrate arc** — 8× corroborated post-S2918. **NOT to be opened without explicit Chris directive** (post-D6 evaluation candidate).
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.

### What's forbidden at S2920 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.**
- No new gate/lint proposals.
- No agent-substrate validation arc.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.**
- **No entrypoint-side context-injection substrate arc without explicit Chris directive.**
- **No "schema-drift-fix Fold promotion" without explicit Chris directive.** **3/3 TRIGGERED at S2919 batch 2.** Instances: S2911 reasoning_engine + S2918 analytics_tool `role` param + S2918 audit_tool `status` on `citations` + S2919 ats_tool `category` on non-`keywords` (3rd trigger) + S2919 narrative_tool `category`/`domain` dual-accept (4th confirming). Triggers evaluation — still requires Chris D-verdict.
- **No `dry_run` infrastructure arc for mutation-class dispatchers without explicit Chris directive.**
- **No Concern C schema↔doc drift substrate arc.** Framing (a) still recommended for future post-D6 ratification.
- **No `post_save signal cascade` substrate arc without explicit Chris directive.**
- **No harness-level soft_error accounting substrate arc without explicit Chris directive.**
- **No "metadata-classification-as-runtime-gate" substrate arc without explicit Chris directive.**
- **No "hidden network/LLM in read-shaped gateway" Fold promotion without 3rd confirmed instance.** 2/3 (S2913 conversation_tool.search + S2914 intelligence_tool.search). Batch 1 analytics_tool.atr_dashboard `stage3_dashboard` reuse is *documented-not-verified* — would be 3rd if audit surfaces LLM/network. Watch continues into Slice 4 batch 2.
- **No "cascade audit companion doc" pattern promotion without 2nd instance.** 1/2 (S2915 competitor_comparison_tool.delete).
- **No "IRREVERSIBLE dry_run flag harness lint" Fold promotion without 3rd instance.** 2/3 (S2908 media_tool.delete + S2915 competitor_comparison_tool.delete).
- **No `NEXT_HEADING_RE` parser fix without Chris directive or 3rd instance.** 2 instances (S2914 + S2915). Batch 6+7 workaround = keep `###` only under §5b/appendices (AFTER Covered actions).
- **No "observability-tracker as MUTATION vector" Fold promotion without 2nd instance.** 1st (S2916 http_smoke_test OpsRunTracker).
- **No "undocumented envelope field (`error_code: 'legacy_error'`)" substrate arc without explicit Chris directive.** **12 instances corroborated post-S2919** (8 at S2918 + batch-2's discord/distribution/ats/narrative). **Semantic nuance surfaced at S2919 live-verify**: the observed `error_code='legacy_error'` is a VALUE on a post-S2909 envelope field, not the ABSENCE of the field. Framing may need refresh — the "field-absence" concern seems partially mitigated post-S2909; the "value=legacy_error" enum indicates handler falling through to bare-error shape. Different substrate arc scope than originally framed. Still gated on explicit Chris directive.
- **No "grep-before-claim" Fold promotion without 2nd instance.** 1st (S2916 fleet_health HMAC-claim).
- **No "dispatcher re-entry" Fold promotion without 2nd instance.** 1st observed (S2917 workflow_run_tool.start via `_impl_run_source_pack_workflow` → `tool_dispatcher._handle_competitor_comparison` at `tasks_content.py:4050-4057`). 2nd instance triggers evaluation — candidate name Appendix D.
- **No "handler-forwarded param not in schema" Fold promotion without 2nd instance.** 1st (S2917 workflow_run_tool.start `focus_areas` at `td_handlers_core.py:3162`).
- **No "contract asymmetry — single vs dual identifier in async envelopes" Fold promotion without 2nd instance.** 1st (S2917 studio single task_id vs workflow_run dual).
- **No "envelope-key asymmetry across actions" Fold promotion without explicit Chris directive.** **3/3 TRIGGERED at S2919 batch 2.** Instances: S2918 audit_tool `findings/defects/violations` + S2918 experiment_tool `tests/test/total_tests` + S2919 distribution_tool `platforms/listings/revenue/stats` (revenue missing `count`). Triggers evaluation for candidate harness-lint "consistent-list-key across actions." Still requires Chris D-verdict.
- **No "multi-tenant leak on detail/results action" Fold promotion without post-D6 evaluation.** 2 instances observed (S2918 campaign_tool.detail + experiment_tool.results); currently absorbed by single-user pre-prod context per `project_single_user_pre_prod_operating_context`.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — unchanged.
- **Testing Discipline chapter candidacy** — Ledger row 154 `future_trigger`. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Unchanged.
- **2-tier evidence template promotion** — Ledger row 160. Unchanged.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. **CLOSED at S2904.** S2918 sustained pace (batch 1 = 4 tools + 2-turn SIGN + live verify in one session).
- **Response-level introspection field creep** — Ledger row 162. Unchanged.
- **S2905 metadata-pattern-selection lint** — batch 1 used no TOOL_DEFAULTS/TOOL_ACTION_METADATA (pure READ_ONLY quartet). Not incrementing lint counter.
- **S2906/S2907/S2908 Ledger candidates** — unchanged.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate: `obs_tool_validation.md` §6.1** — unchanged.
- **S2908 Ledger candidate: `media_tool.delete` first IRREVERSIBLE action** — 2/3.
- **S2909 FT-1 through FT-5** — unchanged.
- **S2910 FT-1 through FT-2** — unchanged.
- **S2911 Ledger #35-#37** — unchanged.
- **S2912 §5a mitigation note** — unchanged.
- **S2913 Ledger candidates (batches 2+3)** — unchanged.
- **S2914 Ledger candidates (batch 4)** — unchanged; "hidden network/LLM in read-shaped gateway" watch continues at 2/3.
- **S2915 Ledger candidates (batch 5)** — unchanged post-S2917 broadening; second IRREVERSIBLE action still at 2/3.
- **S2916 Ledger candidates (batch 6)** — legacy-error envelope 8× corroborated post-S2918; observability-tracker as MUTATION vector still 1/2; grep-before-claim still 1/2.
- **S2917 Ledger candidates (batch 7)** — contract asymmetry (single vs dual identifier) still 1st instance; undocumented handler-forwarded param still 1st; dispatcher re-entry still 1st.
- **S2918 batch 1 Ledger candidate — Envelope-key asymmetry across actions.** **3/3 TRIGGERED at S2919 batch 2** (distribution_tool `revenue` missing `count`). See forbidden-list.
- **S2918 batch 1 Ledger candidate — Multi-tenant leak on detail/results action (campaign_tool.detail + experiment_tool.results bypass user_id filter).** 2 instances; absorbed by single-user pre-prod context. Post-D6 evaluation only.
- **S2918 batch 1 Ledger candidate — Schema-drift-fix `role` param declared but ignored.** **3/3 TRIGGERED at S2919 batch 2** (ats_tool `category` on non-`keywords`; narrative_tool `category`/`domain` dual-accept is 4th confirming). See forbidden-list.
- **S2918 batch 1 Ledger candidate — View-reuse via RequestFactory + AnonymousUser as read-shaped-gateway-hides-side-effect risk (analytics_tool.atr_dashboard reuses stage3_dashboard).** Documented-not-verified. Would advance the "hidden network/LLM in read-shaped gateway" watch to 3/3 if `stage3_dashboard` internals audit surfaces LLM/network.
- **S2918 batch 1 Ledger candidate — Legacy-error envelope corroboration.** Now at **12 instances post-S2919**. Semantic nuance surfaced at live-verify (see forbidden-list).
- **NEW S2919 batch 2 Ledger candidate — Divergent `limit` hard-cap (30 vs 50).** narrative_tool 1st gateway-slice instance (30 vs sibling 50). 2nd instance triggers evaluation.
- **NEW S2919 batch 2 Ledger candidate — N+1 query pattern in narrative `narratives` action** (`evidence_count` per-row). 1st instance. 2nd instance triggers evaluation.
- **NEW S2919 batch 2 Ledger candidate — Envelope-shape intra-tool asymmetry (`total` vs `count`).** narrative_tool 1st instance (narratives uses `total`; siblings use `count`). Distinct from cross-action envelope-key asymmetry. 2nd instance triggers evaluation.
- **NEW S2919 batch 2 Ledger candidate — `variations` truncation-to-3 undeclared in ats_tool schema.** Usability sharp edge; 2nd similar instance triggers evaluation.
- **NEW S2919 batch 2 Ledger candidate — `platform_account` stringified-UUID-not-name in distribution_tool `revenue` grouping.** Usability sharp edge; 2nd similar instance triggers evaluation.
- **NEW S2919 Rigby Tool Gap Ledger entry — narrative_tool + shifts/evidence/alerts blocked (narrative* tables missing in local dev DB despite migrations recorded as applied).** Logged via `deliverable_tool.append` to `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`. MEDIUM priority; requires ~30 min migration replay + verification. Engineering task.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — unchanged.
- **Applicability metadata pattern (entry #28)** — unchanged.
- **Baseline lookback cap (entry #29)** — MITIGATED at PR #3423 (S2899).
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **R1 fleet reject-mode flip** — deferred.
- Docs restructuring arc (`project_docs_restructuring_arc_queued`) — behind sweep.
- W2 #1 / #2b / #2c — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris skipped at S2849.
- LLMCallLog field splits — migration required.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os side follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**Slice 1 — `td_handlers_ops` (17 registered tools):** UNCHANGED.
**Slice 2 — `td_handlers_agents` (25 tools):** **CLOSED at S2912.**
**Slice 3 — `td_handlers_core` (22 tools):** **CLOSED at S2917 (22/22).**

**Slice 4 — `td_handlers_gateway` (17 tools):** **OPEN — 8/17 shipped.**
- S2918 batch 1: 4 tools ✓ (gateway small-tier quartet — analytics/audit/campaign/experiment; §5b Appendix A + N declared N/A for gateway)
- S2919 batch 2: 4 tools ✓ (gateway small-tier read-only quartet — discord/distribution/ats/narrative; template-preservation swap after vip_invite mutation-scan; 3/4 live-verified + 1 surfaced pre-existing dev-env drift logged to Ledger)

**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix).

**Total remaining tools to close:** ~39. Post-S2919 pace: 4 tools this session with in-depth 2-turn SIGN + probe-first correction + narrative-swap + post-merge verify + dev-env drift investigation. If Slice 4 sustains 3-4 tools/batch pace, Slice 4 CLOSE at ~2-3 more sessions (9 remaining).

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2919 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2919: zero A4 spend — pure sweep-batch engineering (1 batch of 4 tools + close cascade + dev-env drift investigation).** A1 shipping spend was 1 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2919)

See:
- **S2919 handoff (current):** `docs/handoffs/SESSION_2919_SLICE_4_BATCH_2.md`
- **S2918 handoff:** `docs/handoffs/SESSION_2918_SLICE_4_BATCH_1.md`
- **S2917 handoff:** `docs/handoffs/SESSION_2917_SLICE_3_BATCH_7_CLOSE.md`
- **S2916 handoff:** `docs/handoffs/SESSION_2916_SLICE_3_BATCH_6.md`
- **S2915 handoff:** `docs/handoffs/SESSION_2915_SLICE_3_BATCH_5.md`
- **S2914 handoff:** `docs/handoffs/SESSION_2914_SLICE_3_BATCH_4.md`
- **S2913 handoff:** `docs/handoffs/SESSION_2913_SLICE_3_BATCHES_1_2_3.md`
- **S2912 handoff:** `docs/handoffs/SESSION_2912_SLICE_2_CLOSE.md`
- **S2911 handoff:** `docs/handoffs/SESSION_2911_SLICE_2_BATCH_6A_PLUS_DRIFT_FIX.md`
- **S2910 handoff:** `docs/handoffs/SESSION_2910_SLICE_2_BATCH_5_MIXED_COMPOSITION_SWEEP.md`
- **S2909 handoff:** `docs/handoffs/SESSION_2909_SUBSTRATE_CLEANUP_ARC_T1_T2_SHIPPED.md`
- **S2909 arc scoping doc:** `docs/audits/pa_tools/substrate/S2909_substrate_cleanup_arc_scoping.md`
- **S2908 handoff:** `docs/handoffs/SESSION_2908_SLICE_2_BATCH_4_SHAPE_BREAK_SWEEP.md`
- **S2907 handoff:** `docs/handoffs/SESSION_2907_SLICE_2_BATCH_3_SMALL_ACTIONFUL_SWEEP.md`
- **S2906 handoff:** `docs/handoffs/SESSION_2906_SLICE_2_BATCH_2_ACTIONLESS_SWEEP.md`
- **S2905 handoff:** `docs/handoffs/SESSION_2905_SLICE_2_BATCH_1_ACCELERATED_SWEEP.md`
- **S2904 handoff:** `docs/handoffs/SESSION_2904_T1B_TEMPLATE_EXTRACTION.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2919 per-tool validation docs (this session's 4):** at `docs/research/tools/validation/`
  - `discord_tool_validation.md`, `distribution_tool_validation.md`, `ats_tool_validation.md`, `narrative_tool_validation.md`
- **S2918 per-tool validation docs:** at `docs/research/tools/validation/`
  - `analytics_tool_validation.md`, `audit_tool_validation.md`, `campaign_tool_validation.md`, `experiment_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 77 non-substrate post-S2919)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (S2919 batch 2 added narrative_tool dev-env drift entry).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
