# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2923 CLOSE → S2923 SHIPPED Slice 4 batch 6 (cockpit solo — first `external` PRIMARY + latent-cascade authoring pattern). **15/17 shipped.** **S2924 OPENS WITH SLICE 4 BATCH 7 (proactive + profile spreading pair — FINAL Slice 4 batch, CLOSES the slice).** D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2923 close).** Batch 6 shipped 1 tool per Chris D-verdict "a it is" on Claude+Rigby joint recommendation (a) cockpit solo. Rigby T0 SIGN + T1 SIGN + T2 SIGN 3-turn cycle grounded in 27 `repo_tool` receipts across S2923 (9 T0 + 9 T1 + 0 T2 amendments-only + 9 verify); zero rubber-stamp. **Reclassification substrate shipped alongside:** S2922 close 00-START pre-labeled cockpit as first Slice-4 `cascading` example based on FAILURE_CLUSTER dynamic-connect discovery. S2923 handler-line-range re-verification surfaced the S2922 handoff referenced line 1030-1039 as the "save" location — that's actually the help-payload text; actual mutation sites are line 1367 (`create(status='QUEUED')`) and line 1420 (`save(status='REVOKED')`). Both mutations trip the post_save signal but hit the gate at `failure_cluster_signals.py:141` (`if status != 'FAILURE': return`). Corrected classification: `external` PRIMARY (Celery send_task + control.revoke + Redis leaves process; highest tier) with cascading documented as gate-exempt side-effect and 5 explicit reclassify triggers enumerated.

**PRs shipped this session:**
- u-d-b PR [#3476](https://github.com/clwest/donkey-betz-platform/pull/3476) — Slice 4 batch 6 (cockpit solo), merged at `183d1eeef`.
- u-d-b PR `<TBD>` — S2923 close cascade (handoff + 00-START refresh + wrapper pin bump + Ledger #31 severity bump).

**Tools shipped (1 — Slice 4 batch 6 solo):**
- `cockpit_tool` (8 actions: help + beat_schedule + task_status + worker_health + recent_failures + queue_lengths + trigger_task + revoke_task). Handler at `td_handlers_gateway.py:1022`, 431 lines. Schema at `pa_tool_schemas.py:4562`. Register at `tool_dispatcher.py:571`.

**§5a authoring convention codified doc-level (not template-level) at S2923 T1 Q5(ii) AGREE:** for tools with latent-but-gated signal cascades, use "gate-quoted + reclassify-trigger enumerated" pattern. Cockpit's §5a is the reference exemplar. Not an unconditional "external always beats cascading" rule — guardrail preserved that classification is EFFECT-based, not merely wiring-based.

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3476 recycled clean at `sha=183d1eeef`: 5 fresh workers + beat, zero surviving old PIDs.
- Rigby dispatch 8/8 PASS across all cockpit actions. Two ORM-gated verifications (HAI cascade non-fire + latent-cascade probe) blocked by orm_inspect_tool allowlist gap → handled by Claude direct via `python manage.py shell`. HAI non-fire from cockpit's own mutations: PASS (0 failure_cluster HAI in 10min window post trigger/revoke). Receiver-wired confirmed via startup init log in celery.log + celery-long-running.log.

**Doc-authoring gap surfaced by verify:** doc §6 step 8 latent-cascade probe was authored assuming single-row FAILURE triggers cascade. Actual behavior: receiver runs but threshold gate returns early (needs ≥5 distinct task_ids for 'high' urgency). Step 8 cannot distinguish "receiver not wired" from "receiver wired + threshold-gated". Recorded as post-close doc-fix candidate + Ledger row per Rigby S2923 close AGREE — NOT a re-open of this ship.

**Rigby joint SIGN (3-turn cycle with grep-grounded reclassification, zero rubber-stamp):**
- T0 SIGN: 9 `repo_tool` runs. Q1 AGREE (a) cockpit solo. Q3 full cascading-tier signal-chain trace line-by-line (`escalate_failure_cluster` at `:123` → `transaction.on_commit(_dispatch(snapshot))` at `:173` → `attention_bridge.create_failure_cluster_attention` → `HumanInterfaceService.create_attention_item(source_type='failure_cluster')` → HumanAttentionItem inbox row; dedup 30min via two-key OR fails-safe to allow escalation). Q4 pre-audited proactive + profile confirmed as `spreading` (no signal receivers/`.connect(`/`transaction.on_commit` in handler regions).
- T1 SIGN: 9 `repo_tool` runs. Q1 AGREE `external` PRIMARY over `cascading` PRIMARY (all 5 grounding claims confirmed line-by-line). Q2 AGREE 11-item ALLOWED_TASKS enumeration (spot-checked `content_autonomy_loop` + `generate_self_blog_deliberation_task` — both have `BudgetAwareScheduler().preflight(...)`). Q5(i) flagged `check_content_diversity` as UNSAFE for verify (auto-creates content per `_impl_check_content_diversity` at `tasks_misc.py:3488-3503`); Claude swapped to `run_body_system_check` (snapshot-write, idempotent-in-effect). Q5(ii) codified authoring convention as doc-level rationale-writing pattern with guardrails. Q5(iii) latent-cascade prominence — bold callout added to §5a top + 5 reclassify triggers enumerated at end + step 8 dev-local scope + tagged task_name.
- T2 SIGN: AGREE Q1 + Q2 (amendments adequate + ready for gap-map regen + PR ship). Optional nicety applied: step 8 probe uses tagged task_name `__s2923_cockpit_probe__` for unambiguous log matching.

**Sweep progress (post-S2923, gap-map regen at close):**
- **Slice 4 (`td_handlers_gateway`):** 15/17 shipped. Batch 6 CLOSED as cockpit solo.
- Remaining 2 with **verified** handler line counts (grep + boundary math against `td_handlers_gateway.py` at sha `183d1eeef`):
  - **proactive** — handler 1560–1699 = **140 lines** — MUTATION `spreading` (ProactiveNotification.filter(...).update() for mark_read + bulk_ack + dismiss; bulk_ack capped at 200 rows).
  - **profile** — handler 2294–2481 = **188 lines** — MUTATION `spreading` (EnhancedUserProfile get_or_create × 2 + save × 1 for profile/update_preferences).
- Total corpus untested: 33 → **32** post-batch-6 (cockpit shift).
- Gap map: **67 full · 10 partial · 7 unknown · 32 untested** (verified via `python manage.py build_pa_tool_audit --gap-only`).
- Session cumulative pace: 1 tool / 1 session (single-tool batch matching S2921 self_awareness precedent + reclassification substrate + latent-cascade authoring pattern shipped alongside).

Full session context: `docs/handoffs/SESSION_2923_SLICE_4_BATCH_6_COCKPIT.md`.

---

## S2924 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 4 batch 7 (FINAL) composition SIGN cycle

**No blocking Chris D-verdict from S2923 close.** Batch 7 = final Slice 4 batch. Composition should be joint Claude+Rigby → Chris yes/no.

**Batch 7 candidates — 2 remaining Slice 4 tools (both `spreading` per S2923 pre-audit):**

- **proactive** (140 lines) — MUTATION `spreading`. Actions: dashboard/alerts/notifications/suggestions/automations/mark_read/bulk_ack/dismiss (verify actual enum at authoring). Bulk_ack capped at 200 rows.
- **profile** (188 lines) — MUTATION `spreading`. Actions: profile/update_preferences/history (verify actual enum at authoring). get_or_create × 2 + save × 1.

**Options:**
- **(a) Proactive + profile spreading pair (RECOMMENDED — SLICE 4 CLOSE):** ships batch 7 as final Slice 4 batch; matches batch 5 mixed-pair success + confirmed spreading via S2923 pre-audit. **Slice 4 CLOSES at S2924.**
- **(b) Proactive solo + profile deferred to S2925:** conservative pace; Slice 4 closes at S2925.
- **(c) Profile solo + proactive deferred to S2925:** same as (b) but reversed.

Recommend **(a)** — both tools pre-audited as `spreading` (bounded cross-row, no cascade); symmetric tier exercise; matches S2922 batch 5 successful mixed-pair shape (pure-READ + spreading mutation).

**Q1 (batch 7 composition):** Pick (a) / (b) / (c).

**Q2 (Appendix N/A applicability):** Continue gateway-wide 1/17 first-hop-literal watch. Per-tool grep for proactive + profile — expect 0 additions (both are pure-ORM writes per S2923 pre-audit). Gateway-wide count expected to stay 1/17 post-Slice-4.

**Q3 (spreading-tier §5a docs shape for both):** Confirm each mutation's cross-row reach:
- proactive.bulk_ack: 200-row cap on `ProactiveNotification.filter(...).update()` — bounded within single user.
- proactive.mark_read / .dismiss: single-row update.
- profile.update_preferences: `get_or_create` may implicitly create `EnhancedUserProfile` row + `save()` persists preferences — bounded to (user, profile-row) tuple.

**Q4 (post-close doc-fix companion PR — cockpit §6 step 8 threshold-aware probe reframing):** Should the cockpit doc amendment ship alongside batch 7 (bundled PR) or as its own tiny doc-fix PR? Reframing: step 8 becomes "receiver-wired check via startup init log grep" (immediate verify) + "cascade-fires check via ≥5-tagged-FAILURE-rows probe" (optional threshold-exceeding test). Small; ~30 lines of doc edit.

**Q5 zoom-out (required per feedback_zoom_out_ask_per_rigby_sign):**
- Slice 4 close horizon: (a) → S2924 close. Reasonable close ceremony? Would we want a Slice 4 close-cascade doc summarizing all 17 tools' §5a tier distribution (contained / spreading / cascading / external) + first-hop-literal count for future reference?
- orm_inspect_tool allowlist expansion (Ledger #31 MEDIUM bumped this session) — should this be Slice-4-CLOSE engineering task (blocking clean batch 7 post-merge verify), or defer to Slice 5?
- Legacy-error envelope 20th instance expected in both batch 7 tools (proactive + profile). At 20+ instances, worth re-surfacing dispatcher-backfill semantic-nuance refresh proposal at Slice-4 close for Chris D-verdict, or stay deferred post-D6?

### Alternative Step 1 candidates

- **cockpit doc §6 step 8 amendment** — described in Q4 above. Could be standalone tiny PR before batch 7 opens.
- **`narrative_tool` dev-env drift fix** — Rigby Tool Gap Ledger entry `5c84e75a` from S2919; ~30 min migration replay + verification. Engineering task.
- **orm_inspect_tool allowlist expansion** — Ledger #31 MEDIUM bumped. ~1-2 hours; unblocks cross-table `spreading`-tier full-exercise verification for batch 7 and future batches. Adds CeleryTaskEvent + PeriodicTask + HumanAttentionItem + VIPInvite + User to allowlist.
- **Legacy-error envelope substrate arc** — 19× corroborated post-S2923. **NOT to be opened without explicit Chris directive** (post-D6 evaluation candidate).
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.

### What's forbidden at S2924 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.**
- No new gate/lint proposals.
- No agent-substrate validation arc.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.**
- **No entrypoint-side context-injection substrate arc without explicit Chris directive.**
- **No "schema-drift-fix Fold promotion" without explicit Chris directive.** 3/3 TRIGGERED at S2919 batch 2 + 4th confirming. Triggers evaluation — still requires Chris D-verdict.
- **No `dry_run` infrastructure arc for mutation-class dispatchers without explicit Chris directive.**
- **No Concern C schema↔doc drift substrate arc.** Framing (a) still recommended for future post-D6 ratification.
- **No `post_save signal cascade` substrate arc without explicit Chris directive.** S2922 discovery + S2923 reclassification confirm the pattern is manageable via doc-level authoring convention (gate-quoted + reclassify-trigger enumerated); no substrate arc needed.
- **No harness-level soft_error accounting substrate arc without explicit Chris directive.**
- **No "metadata-classification-as-runtime-gate" substrate arc without explicit Chris directive.**
- **No "hidden network/LLM in read-shaped gateway" Fold promotion without 3rd confirmed instance.** 2/3 (S2913 + S2914).
- **No "cascade audit companion doc" pattern promotion without 2nd instance.** 1/2 (S2915).
- **No "IRREVERSIBLE dry_run flag harness lint" Fold promotion without 3rd instance.** 2/3 (S2908 + S2915).
- **No `NEXT_HEADING_RE` parser fix without Chris directive or 3rd instance.** 2 instances (S2914 + S2915). Batch 7+ workaround = keep `###` only under §5b/appendices (AFTER Covered actions).
- **No "observability-tracker as MUTATION vector" Fold promotion without 2nd instance.** 1st (S2916).
- **No "undocumented envelope field (`error_code: 'legacy_error'`)" substrate arc without explicit Chris directive.** **19 instances corroborated post-S2923** (18 pre-batch + cockpit = 19). Rigby S2920 Q4(a) semantic-nuance refresh (treat `error_code` values as first-class semantics) still deferred post-D6 per S2921 Q5(c) Chris ratification; **worth re-surfacing at Slice-4 close per S2923 Rigby Q5-close AGREE**.
- **No "grep-before-claim" Fold promotion without 2nd instance.** 1st (S2916).
- **No "dispatcher re-entry" Fold promotion without 2nd instance.** 1st (S2917).
- **No "handler-forwarded param not in schema" Fold promotion without 2nd instance.** 1st (S2917).
- **No "contract asymmetry — single vs dual identifier in async envelopes" Fold promotion without 2nd instance.** 1st (S2917).
- **No "envelope-key asymmetry across actions" Fold promotion without explicit Chris directive.** 3/3 TRIGGERED at S2919. Still Chris-gated.
- **No "multi-tenant leak on detail/results action" Fold promotion without post-D6 evaluation.** 3 instances; absorbed by single-user pre-prod context.
- **No "template-preservation swap" Fold promotion without explicit Chris directive.** CODIFIED at S2921 as sweep-doc note.
- **No "mixed user-scoping within single response" Fold promotion without 2nd instance.** 1st (S2920 calendar_tool.stats intra-response). **Candidate 2nd instance at S2922 (podcast episodes cross-action variant)** — related but distinct sub-pattern; evaluation-worthy at 3rd instance.
- **No "filesystem-read handler shape (open + regex)" Fold promotion without 3rd instance.** 2/3 (S2919 + S2920).
- **No "limit does not gate nested lists" Fold promotion without 2nd instance.** 1st (S2920 conceptforge_tool.run_detail).
- **No "per-tool `limit` default divergence from gateway norm" Fold promotion without 2nd instance.** 1st (S2921 self_awareness_tool). Cockpit uses gateway norm (default 20, cap 50) — no divergence. Watch continues.
- **No "envelope-representation asymmetry (write-as-0.0-read-as-null)" Fold promotion without 2nd instance.** 1st (S2921 self_awareness collect/metrics).
- **No "00-START span-math source-of-truth regen" Fold promotion.** Regeneration policy commitment at S2921 close per Chris Q5(b) ratification — permanent close-ceremony step. Validated on 3 consecutive sessions (S2921 self_awareness + S2922 podcast + S2923 cockpit).
- **NEW S2923 forbidden entries:**
  - **No "signal wiring exists but gate exempts tool's mutation shape → external not cascading" Fold promotion without 2nd instance.** 1st (S2923 cockpit both mutations). Codified as doc-level rationale-writing pattern at S2923 T1 Q5(ii); doc-level, not template-level. Future 2nd instance would trigger template-level codification evaluation.
  - **No "verify-protocol authoring SIGN checkpoint" Fold promotion without 2nd instance.** 1st (S2923 cockpit doc §6 step 8 authoring gap — probe couldn't distinguish "receiver not wired" from "wired + threshold-gated"). Rigby AGREE at S2923 close: record post-close, 2nd-instance evaluation.
  - **No "single-row FAILURE probe as latent-cascade test" Fold promotion.** CODIFIED at S2923 close as doc-fix candidate — step 8 requires threshold-aware reframing to distinguish receiver-wired from cascade-fires. Ledger row noted.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — unchanged.
- **Testing Discipline chapter candidacy** — Ledger row 154. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged; **worth surfacing at Slice-4 close per S2921 + S2922 + S2923 Q5(iv) AGREE.**
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Reinforced by S2921 self_awareness + S2923 cockpit both single-tool ships (2/3 for post-D6 evaluation).
- **2-tier evidence template promotion** — Ledger row 160. Unchanged.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. CLOSED at S2904.
- **Response-level introspection field creep** — Ledger row 162. Unchanged.
- **S2905 metadata-pattern-selection lint** — batch 6 used no TOOL_DEFAULTS/TOOL_ACTION_METADATA. Not incrementing lint counter.
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
- **S2915 Ledger candidates (batch 5)** — unchanged; second IRREVERSIBLE action still at 2/3.
- **S2916 Ledger candidates (batch 6)** — unchanged.
- **S2917 Ledger candidates (batch 7)** — all still 1st instance.
- **S2918 batch 1 Ledger candidates** — unchanged.
- **S2919 batch 2 Ledger candidates** — unchanged.
- **S2920 batch 3 Ledger candidates** — unchanged.
- **S2921 batch 4 Ledger candidates** — legacy-error envelope 19th (this session's cockpit); §5a first `spreading` exercise still S2922 vip_invite; `limit` default divergence still 1st.
- **S2922 batch 5 Ledger candidates** — unchanged.
- **NEW S2923 batch 6 Ledger candidates:**
  - **First §5a `external` PRIMARY tier exercise + first substantive Appendix A** — cockpit first-hop-literal count moves 0/17 → 1/17 gateway-wide.
  - **Signal wiring exists but gate exempts tool's mutation shape** — 1st observation of nuanced rationale-authoring pattern. Codified doc-level; 2nd instance triggers template-level evaluation.
  - **S2922 close 00-START pre-classification correction** — handler-line-range re-verification value observed for the 2nd time this arc (S2921 vip_invite mutation-verb count correction was 1st; S2923 cockpit tier reclassification is 2nd). Watch for 3rd for Fold candidacy.
  - **Cockpit cross-reference proxy pattern** — td_handlers_ops.py:295-296 + :905-914 proxy into `_handle_cockpit`. Intentional composition, not dispatcher re-entry. 1st observation in-sweep.
  - **11-item ALLOWED_TASKS allowlist audit surface** — recorded for future PR review.
  - **Doc §6 step 8 latent-cascade probe authoring gap** — single-row FAILURE probe can't distinguish "receiver not wired" from "wired + threshold-gated." Post-close doc-fix candidate + 1st instance of verify-protocol authoring SIGN checkpoint Fold.
  - **00-START span-math regen 3rd time** — cockpit 431 lines matched. Rigby Q5(ii) permanent close-ceremony step per S2922 close now validated on 3 consecutive sessions.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — unchanged.
- **Applicability metadata pattern (entry #28)** — unchanged.
- **Baseline lookback cap (entry #29)** — MITIGATED at PR #3423 (S2899).
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — unchanged.
- **Rigby Tool Gap Ledger entries updated this session:**
  - **Entry #31 (MEDIUM) — orm_inspect_tool allowlist gap — SEVERITY NOTE BUMPED.** Now blocks post-merge verification across MULTIPLE Slice 4 tools (S2922 vip_invite + S2923 cockpit). Additional required read-only models to add to allowlist: CeleryTaskEvent, PeriodicTask, HumanAttentionItem (retains S2922 VIPInvite + User). Impact: post-merge verify fragmented — Rigby dispatches tool actions, Claude drops to shell for ORM cross-checks. Expansion candidate for Slice-4-close engineering slate.
  - **Entry #32 (LOW) — static @receiver grep insufficient for signal-cascade classification** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **S2919 narrative_tool dev-env drift (Rigby Tool Gap Ledger)** — unchanged; MEDIUM priority; ~30 min migration replay + verification.
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

**Slice 4 — `td_handlers_gateway` (17 tools):** **OPEN — 15/17 shipped.**
- S2918 batch 1: 4 tools ✓ (gateway small-tier quartet — analytics/audit/campaign/experiment)
- S2919 batch 2: 4 tools ✓ (gateway small-tier read-only quartet — discord/distribution/ats/narrative; template-preservation swap #1)
- S2920 batch 3: 3 tools ✓ (gateway medium-tier read-only trio — mobile/calendar/conceptforge; template-preservation swap #2 with split-batch escalation)
- S2921 batch 4: 1 tool ✓ (self_awareness mutation-template pilot; §5a 4-tier blast-radius amendment shipped alongside)
- S2922 batch 5: 2 tools ✓ (mixed pair — podcast READ + vip_invite spreading mutation; first §5a `spreading` exercise; legacy-error dispatcher-backfill discovery + dynamic post_save.connect discovery)
- **S2923 batch 6: 1 tool ✓ (cockpit solo — first §5a `external` PRIMARY tier exercise + first substantive Appendix A + latent-cascade authoring pattern codified doc-level; reclassification substrate correcting S2922 pre-classification)**

**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix). **S2921 §5a 4-tier taxonomy amendment** shipped as doc-only sweep substrate. **S2923 latent-cascade authoring convention** shipped as doc-level rationale-writing pattern (no template change).

**Total remaining tools to close:** ~32. Post-S2923 pace: 1 tool this session with reclassification substrate + latent-cascade authoring pattern + full 3-turn SIGN discipline + Chris-facing plain-English decision framing + post-merge live-dispatch (Rigby + Claude direct) + 2 Ledger updates. Slice 4 CLOSE at S2924 (batch 7 = proactive + profile spreading pair — final Slice 4 batch).

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2923 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2923: zero A4 spend — pure sweep-batch engineering (1 tool + reclassification substrate + close cascade).** A1 shipping spend was 1 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2923)

See:
- **S2923 handoff (current):** `docs/handoffs/SESSION_2923_SLICE_4_BATCH_6_COCKPIT.md`
- **S2922 handoff:** `docs/handoffs/SESSION_2922_SLICE_4_BATCH_5_MIXED_PAIR.md`
- **S2921 handoff:** `docs/handoffs/SESSION_2921_SLICE_4_BATCH_4_SELF_AWARENESS_PILOT.md`
- **S2920 handoff:** `docs/handoffs/SESSION_2920_SLICE_4_BATCH_3.md`
- **S2919 handoff:** `docs/handoffs/SESSION_2919_SLICE_4_BATCH_2.md`
- **S2918 handoff:** `docs/handoffs/SESSION_2918_SLICE_4_BATCH_1.md`
- **S2917 handoff:** `docs/handoffs/SESSION_2917_SLICE_3_BATCH_7_CLOSE.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (§5a **4-tier blast-radius taxonomy** amended S2921 — unchanged S2923)
- **S2923 per-tool validation doc:** `docs/research/tools/validation/cockpit_tool_validation.md` (§5a doc-level latent-cascade authoring convention reference exemplar)
- **S2922 per-tool validation docs (batch 5):** `docs/research/tools/validation/{podcast,vip_invite}_tool_validation.md`
- **S2921 per-tool validation doc:** `docs/research/tools/validation/self_awareness_tool_validation.md`
- **S2920 per-tool validation docs (batch 3):** `docs/research/tools/validation/{mobile,calendar,conceptforge}_tool_validation.md`
- **S2919 per-tool validation docs (batch 2):** `docs/research/tools/validation/{discord,distribution,ats,narrative}_tool_validation.md`
- **S2918 per-tool validation docs (batch 1):** `docs/research/tools/validation/{analytics,audit,campaign,experiment}_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 84 non-substrate post-S2923)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entry #31 severity bumped S2923 with 3 additional required allowlist models: CeleryTaskEvent, PeriodicTask, HumanAttentionItem).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
