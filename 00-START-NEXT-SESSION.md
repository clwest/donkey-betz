# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2924 CLOSE → SLICE 4 CLOSED at 17/17. **S2925 OPENS SLICE 5 (`tool_dispatcher.py` — 14 tools).** D6 MORATORIUM STILL IN FORCE.

**Refreshed 2026-07-23 (S2924 close).** Batch 7 shipped 2 tools per Chris D-verdict "ship it" on Claude+Rigby joint recommendation (a) proactive + profile spreading pair. Rigby T0 SIGN grounded in 10 `repo_tool` receipts; **zero rubber-stamp — Q3 corrected Claude's initial user-scoping rationale** (proactive `mark_read`+`dismiss` have NO `user_id` predicate; `bulk_ack` `user_id` filter is CONDITIONAL; profile is USER-SCOPED cleanly via `User.objects.filter(id=user_id).first()` gate). Also shipped standalone doc-fix PR (cockpit §6 step 8 threshold-aware reframing per S2923 post-close doc-fix candidate + Q4 (b) ratification) BEFORE batch 7 to keep review-scope clean on the closing batch.

**PRs shipped this session:**
- u-d-b PR [#3478](https://github.com/clwest/donkey-betz-platform/pull/3478) — cockpit doc §6 step 8 threshold-aware reframing (standalone tiny doc-fix), merged at `592f72214`.
- u-d-b PR [#3479](https://github.com/clwest/donkey-betz-platform/pull/3479) — Slice 4 batch 7 (proactive + profile spreading pair), merged at `2fc8c66ae`.
- u-d-b PR `<TBD>` — S2924 close cascade (handoff + 00-START refresh + wrapper pin bump + profile doc dev-env drift amendment + Ledger #33 add via Rigby).

**Tools shipped this session (2 — Slice 4 batch 7 pair; Slice 4 CLOSED at 17/17):**
- `proactive_tool` (8 actions: dashboard/alerts/notifications/suggestions/automations/mark_read/bulk_ack/dismiss). Handler at `td_handlers_gateway.py:1560`, 140 lines. Schema at `pa_tool_schemas.py:4718`. Register at `tool_dispatcher.py:580`.
- `profile_tool` (6 actions: profile/skills/learning_summary/preferences/update_preferences/desk_preferences). Handler at `td_handlers_gateway.py:2294`, 188 lines. Schema at `pa_tool_schemas.py:4960`.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3479 recycled clean at `sha=2fc8c66ae`: 5 fresh workers + beat, zero surviving old PIDs.
- Rigby dispatch **11/14 PASS · 2 SKIP · 2 pre-existing dev-env drift** across 8 proactive + 6 profile actions:
  - PASS: proactive dashboard/alerts/notifications/suggestions/automations/bulk_ack; profile profile/preferences/update_preferences(probe+restore)/desk_preferences.
  - SKIP: proactive mark_read/dismiss — no notifications in dev DB to select an id.
  - FAIL (dev-env drift, NOT batch 7 regression): profile skills + learning_summary hard-fail with `relation "core_userskill" does not exist`. UserSkill migration not applied to dev DB. **Rigby appended Ledger #33 (LOW) via deliverable_tool.append** (1193 chars) — 15-min migration replay to fix.
- profile_tool_validation.md §Covered actions + §6 amended in the close cascade to annotate skills/learning_summary as verify-blocked pending Ledger #33 resolution.

**Legacy-error envelope threshold crossed:** 21 corroborating instances (proactive = 20th, profile = 21st). Short "now systemic" note in handoff per Q5(iii) Chris ratification. **NOT** opening substrate arc — remains post-D6 gated per 00-START forbidden list.

**Slice 4 close artifact — §5a tier distribution (see handoff for full table):**
- **12/17 pure READ** (analytics/audit/campaign/experiment/discord/distribution/ats/narrative/mobile/calendar/conceptforge/podcast)
- **5/17 mutation-bearing:** self_awareness (`contained`) + vip_invite (`contained`+`spreading`) + cockpit (`external` PRIMARY) + proactive (`spreading`×3 gap-archetype) + profile (`spreading`×2 clean-archetype)
- Gateway-wide first-hop-literal count: **1/17** (cockpit's Celery `send_task` + `control.revoke` — sole gateway tool with first-hop network/broker dispatch).
- Appendix N (Network-Preflight) count: **0/17** gateway-wide.

**Sweep progress (post-S2924, gap-map regen at close):**
- **Slice 1 (`td_handlers_ops`):** unchanged.
- **Slice 2 (`td_handlers_agents`):** CLOSED at S2912.
- **Slice 3 (`td_handlers_core`):** CLOSED at S2917.
- **Slice 4 (`td_handlers_gateway`):** **CLOSED at S2924 (17/17).**
- **Slice 5 (`tool_dispatcher`, 14 tools):** OPEN — S2925 first slice.
- Total corpus untested: **30** post-batch-7 (from 32 pre-S2924).
- Gap map: **69 full · 10 partial · 7 unknown · 30 untested** (verified via `python manage.py build_pa_tool_audit --gap-only`).
- Session cumulative pace: 2 tools + 1 tiny doc-fix PR + full 3-PR close cascade in 1 session — matches S2922 batch 5 pace (2 tools/session pattern).

Full session context: `docs/handoffs/SESSION_2924_SLICE_4_CLOSE_BATCH_7.md`.

---

## S2925 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 5 (tool_dispatcher.py) composition SIGN cycle

**Slice 5 is a different substrate shape from Slices 1-4.** Slices 1-4 were per-handler-file organized (each `_handle_*` method on one gateway class). Slice 5's `tool_dispatcher.py` contains cross-cutting orchestration (retry/gateway routing/workspace-scope) + a smaller set of native handlers registered directly on the dispatcher itself.

**Recommended S2925 shape:** compact composition SIGN cycle with Rigby to:
- (a) Enumerate the 14 Slice 5 tools (grep `self.register("` in `tool_dispatcher.py`).
- (b) Categorize each as pure-orchestration wrapper vs substantive handler.
- (c) Recommend batch 1 composition (small quartet-style like S2918/S2919 to establish Slice 5 pattern rhythm).

**Q1 (Slice 5 batch 1 composition):** propose a tool set (likely 3-4 tools) that establishes Slice 5's shape without committing to a large ship prematurely.

**Q2 (Slice 5 substrate shape verification):** does the `_TEMPLATE §5a` 4-tier taxonomy shipped at S2921 map cleanly to orchestration-wrapper tools, or does Slice 5 need a §5a variant for wrappers that don't have their own mutations?

**Q3 (Slice 4 close-artifact reuse):** use the §5a distribution table in S2924 handoff as reference exemplar when Slice 5 authoring begins.

**Q4 (Ledger #33 fix — piggyback with Slice 5 batch 1?):** UserSkill migration replay is ~15 min. Worth folding into Slice 5 batch 1 open as a cleanup PR (so profile skills/learning_summary get re-verified live) OR defer to a batched "dev-env migration drift" engineering slate (with S2919 narrative_tool drift + potentially others)?

**Q5 zoom-out (required per feedback_zoom_out_ask_per_rigby_sign):**
- Slice 5 opens as Slice 4 closes at 17/17. Any coupling/drift risk from the tier shift (per-file-handler → cross-cutting-orchestration)?
- Legacy-error envelope at 21 corroborated instances — worth surfacing again to Chris at Slice 5 open as a "should we open the post-D6 substrate arc now" question, or leave post-D6-deferred until the corpus grows further?
- Anything about the Slice 4 close (pace / rhythm / SIGN discipline / doc-in-tree Ledger accretion) worth carrying forward or changing before Slice 5 opens?

### Alternative Step 1 candidates

- **Ledger #33 UserSkill migration replay** — small standalone engineering PR (~15 min). Restores profile skills + learning_summary live-verify.
- **orm_inspect_tool allowlist expansion** — Ledger #31 MEDIUM. ~1-2 hours; adds CeleryTaskEvent + PeriodicTask + HumanAttentionItem + VIPInvite + User to allowlist. Unblocks Rigby-side ORM cross-checks for future Slice 5 verify path.
- **Bundled dev-env drift fix slate** — group Ledger #33 + S2919 narrative drift + any others; single-session engineering slate.
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.

### What's forbidden at S2925 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.**
- No new gate/lint proposals.
- No agent-substrate validation arc.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.**
- **No entrypoint-side context-injection substrate arc without explicit Chris directive.**
- **No "schema-drift-fix Fold promotion" without explicit Chris directive.** 3/3 TRIGGERED at S2919 batch 2 + 4th confirming.
- **No `dry_run` infrastructure arc for mutation-class dispatchers without explicit Chris directive.**
- **No Concern C schema↔doc drift substrate arc.** Framing (a) still recommended for future post-D6 ratification.
- **No `post_save signal cascade` substrate arc without explicit Chris directive.** Doc-level authoring convention (S2923 cockpit codification) sufficient.
- **No harness-level soft_error accounting substrate arc without explicit Chris directive.**
- **No "metadata-classification-as-runtime-gate" substrate arc without explicit Chris directive.**
- **No "hidden network/LLM in read-shaped gateway" Fold promotion without 3rd confirmed instance.** 2/3.
- **No "cascade audit companion doc" pattern promotion without 2nd instance.** 1/2.
- **No "IRREVERSIBLE dry_run flag harness lint" Fold promotion without 3rd instance.** 2/3.
- **No `NEXT_HEADING_RE` parser fix without Chris directive or 3rd instance.** 2 instances.
- **No "observability-tracker as MUTATION vector" Fold promotion without 2nd instance.** 1st.
- **No "undocumented envelope field (`error_code: 'legacy_error'`)" substrate arc without explicit Chris directive.** **21 instances corroborated post-S2924** (19 pre-S2924 + proactive 20th + profile 21st). Threshold-crossed short note surfaced at S2924 close per Q5(iii); substrate arc still Chris-gated.
- **No "grep-before-claim" Fold promotion without 2nd instance.** 1st.
- **No "dispatcher re-entry" Fold promotion without 2nd instance.** 1st.
- **No "handler-forwarded param not in schema" Fold promotion without 2nd instance.** 1st.
- **No "contract asymmetry — single vs dual identifier in async envelopes" Fold promotion without 2nd instance.** 1st.
- **No "envelope-key asymmetry across actions" Fold promotion without explicit Chris directive.** 3/3 TRIGGERED. Still Chris-gated.
- **No "multi-tenant leak on detail/results action" Fold promotion without post-D6 evaluation.** 3+ instances absorbed by single-user pre-prod context. S2924 proactive mark_read/dismiss/bulk_ack scoping-gap absorbed under same rule.
- **No "template-preservation swap" Fold promotion without explicit Chris directive.** CODIFIED at S2921 as sweep-doc note.
- **No "mixed user-scoping within single response" Fold promotion without 2nd instance.** 1st.
- **No "filesystem-read handler shape (open + regex)" Fold promotion without 3rd instance.** 2/3.
- **No "limit does not gate nested lists" Fold promotion without 2nd instance.** 1st.
- **No "per-tool `limit` default divergence from gateway norm" Fold promotion without 2nd instance.** 1st (self_awareness). Cockpit + proactive + profile use gateway norm (default 20, cap 50) — no divergence.
- **No "envelope-representation asymmetry (write-as-0.0-read-as-null)" Fold promotion without 2nd instance.** 1st.
- **No "00-START span-math source-of-truth regen" Fold promotion.** Permanent close-ceremony step per S2921 Q5(b) Chris ratification. Validated 4 consecutive sessions (S2921 self_awareness + S2922 podcast + S2923 cockpit + S2924 proactive+profile).
- **S2923 forbidden entries (unchanged):**
  - **No "signal wiring exists but gate exempts tool's mutation shape → external not cascading" Fold promotion without 2nd instance.** 1st (cockpit).
  - **No "verify-protocol authoring SIGN checkpoint" Fold promotion without 2nd instance.** 1st (cockpit doc §6 step 8 authoring gap; addressed at S2924 via #3478 amendment).
  - **No "single-row FAILURE probe as latent-cascade test" Fold promotion.** CODIFIED at S2923 close as doc-fix candidate; shipped as #3478 at S2924.
- **NEW S2924 forbidden entries:**
  - **No "user-scoping gap on notification-inbox mutations" Fold promotion without 2nd instance.** 1st (proactive mark_read/dismiss/bulk_ack). Absorbed by single-user pre-prod; multi-tenant hardening deferred (would add `filter(user_id=user_id)` predicate to :1660/:1688 + make :1669–1670 unconditional).
  - **No "dismiss observable-idempotency divergence from mark_read" Fold promotion without 2nd instance.** 1st. Schema-consistency note.
  - **No "handler accepts bulk form but schema surfaces only single form" Fold promotion without 2nd instance.** 1st (profile.update_preferences `updates` bulk-dict).
  - **No "READ action name with side effect of new-row creation" Fold promotion without 2nd instance.** 1st (profile.preferences implicit get_or_create).
  - **No "error field embedded in success-shape envelope" Fold promotion without 2nd instance.** 1st (profile preferences/update_preferences/desk_preferences).
  - **No "silent whitelist filtering without per-item feedback" Fold promotion without 2nd instance.** 1st (profile.update_preferences).

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — unchanged.
- **Testing Discipline chapter candidacy** — Ledger row 154. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Unchanged (2/3 for post-D6 evaluation).
- **2-tier evidence template promotion** — Ledger row 160. Unchanged.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. CLOSED at S2904.
- **Response-level introspection field creep** — Ledger row 162. Unchanged.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate: `obs_tool_validation.md` §6.1** — unchanged.
- **S2908 Ledger candidate: `media_tool.delete` first IRREVERSIBLE action** — 2/3.
- **S2909-S2921 Ledger candidates** — unchanged.
- **S2922 batch 5 Ledger candidates** — unchanged.
- **S2923 batch 6 Ledger candidates** — unchanged.
- **NEW S2924 batch 7 Ledger candidates:**
  - **First Slice-4 exercise of §5a `spreading` "gap" vs "clean" archetype distinction** — proactive vs profile establishes the pattern. Documented in-tree.
  - **20th+21st legacy-error envelope corroborating instances** — threshold-crossed. Short note shipped this session.
  - **Ledger #33 (LOW) — UserSkill migration miss dev-env drift.** Appended by Rigby via deliverable_tool.append.
  - **Post-close pin management working via session_lifecycle close** — S2925 fresh pin `pa-a5fee83d2afb4932` minted atomically, wrapper rewritten. No stale-worker issues expected on S2925 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — unchanged.
- **Applicability metadata pattern (entry #28)** — unchanged.
- **Baseline lookback cap (entry #29)** — MITIGATED at PR #3423 (S2899).
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — unchanged.
- **Entry #31 (MEDIUM) — orm_inspect_tool allowlist gap** — unchanged this session. Slice 5 dependency check when Slice 5 batch 1 authoring begins.
- **Entry #32 (LOW) — static @receiver grep insufficient for signal-cascade classification** — unchanged.
- **NEW Entry #33 (LOW) — profile_tool skills + learning_summary dev-env drift (UserSkill migration miss).** Added this session by Rigby. Fix estimate ~15 min migration replay. Blocks re-verification of profile skills + learning_summary until resolved.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **S2919 narrative_tool dev-env drift** — unchanged; ~30 min migration replay + verification. Group with Ledger #33 as bundled dev-env drift fix candidate.
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
**Slice 4 — `td_handlers_gateway` (17 tools):** **CLOSED at S2924 (17/17).** Full §5a distribution table in S2924 handoff.

**Slice 5 — `tool_dispatcher` (14 tools):** **OPEN — S2925 first slice.**

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix). **S2921 §5a 4-tier taxonomy amendment** shipped as doc-only sweep substrate. **S2923 latent-cascade authoring convention** shipped as doc-level rationale-writing pattern (no template change). **S2924 Slice 4 §5a tier distribution artifact** shipped as slice-close reference for future slice-planning.

**Total remaining tools to close:** ~28. Post-S2924 pace: 2 tools + 1 tiny doc-fix PR + 3-PR close cascade in single session. Slice 5 open at S2925.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2924 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2924: zero A4 spend — pure sweep-batch engineering (2 tools + tiny doc-fix + close cascade).** A1 shipping spend was 3 PRs.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2924)

See:
- **S2924 handoff (current):** `docs/handoffs/SESSION_2924_SLICE_4_CLOSE_BATCH_7.md`
- **S2923 handoff:** `docs/handoffs/SESSION_2923_SLICE_4_BATCH_6_COCKPIT.md`
- **S2922 handoff:** `docs/handoffs/SESSION_2922_SLICE_4_BATCH_5_MIXED_PAIR.md`
- **S2921 handoff:** `docs/handoffs/SESSION_2921_SLICE_4_BATCH_4_SELF_AWARENESS_PILOT.md`
- **S2920 handoff:** `docs/handoffs/SESSION_2920_SLICE_4_BATCH_3.md`
- **S2919 handoff:** `docs/handoffs/SESSION_2919_SLICE_4_BATCH_2.md`
- **S2918 handoff:** `docs/handoffs/SESSION_2918_SLICE_4_BATCH_1.md`
- **S2917 handoff:** `docs/handoffs/SESSION_2917_SLICE_3_BATCH_7_CLOSE.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (§5a **4-tier blast-radius taxonomy** amended S2921 — unchanged S2924)
- **S2924 per-tool validation docs (batch 7):** `docs/research/tools/validation/{proactive,profile}_tool_validation.md`
- **S2923 per-tool validation doc:** `docs/research/tools/validation/cockpit_tool_validation.md` (§6 step 8 threshold-aware reframing shipped at #3478 this session)
- **S2922 per-tool validation docs (batch 5):** `docs/research/tools/validation/{podcast,vip_invite}_tool_validation.md`
- **S2921 per-tool validation doc:** `docs/research/tools/validation/self_awareness_tool_validation.md`
- **S2920 per-tool validation docs (batch 3):** `docs/research/tools/validation/{mobile,calendar,conceptforge}_tool_validation.md`
- **S2919 per-tool validation docs (batch 2):** `docs/research/tools/validation/{discord,distribution,ats,narrative}_tool_validation.md`
- **S2918 per-tool validation docs (batch 1):** `docs/research/tools/validation/{analytics,audit,campaign,experiment}_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 86 non-substrate post-S2924)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entry #33 added this session by Rigby via deliverable_tool.append).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
