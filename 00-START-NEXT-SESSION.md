# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2922 CLOSE → S2922 SHIPPED Slice 4 batch 5 (mixed pair: podcast READ + vip_invite spreading mutation). **14/17 shipped.** **S2923 OPENS WITH SLICE 4 BATCH 6 (composition decision — 3 tools remaining: cockpit cascading, proactive spreading, profile spreading).** D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2922 close).** Batch 5 shipped 2 tools per Chris D-verdict "Yes" on Claude+Rigby joint recommendation (a) mixed batch: `podcast_tool` (pure-READ, 4 actions) + `vip_invite_tool` (first Slice-4 exercise of §5a `spreading` tier — create=`contained`, revoke=`spreading` cross-table VIPInvite+User). Rigby T0 SIGN 2-turn cycle grounded in 21 `repo_tool` receipts (8 turn 1 + 13 turn 2); zero rubber-stamp. Post-merge live verify: 6/8 dispatches clean at ≤16ms + idempotency guard verified at 8ms + envelope-level ORM proxy verification via `vip_invite_tool.list` (ORM-hard cross-checks partially blocked by `orm_inspect_tool` allowlist gap — logged as Rigby Tool Gap Ledger #31). Close-cascade discovery: Django-startup log revealed dynamic `post_save.connect(..., sender=CeleryTaskEvent, ...)` at `core/signals/failure_cluster_signals.py:183` that Rigby's static-@receiver grep missed → **cockpit reclassified from likely-`spreading` to `cascading` (first §5a `cascading` example) for batch 6**.

**PRs shipped this session:**
- u-d-b PR [#3474](https://github.com/clwest/donkey-betz-platform/pull/3474) — Slice 4 batch 5 (podcast + vip_invite), merged at `3078dd48b`.
- u-d-b PR `<TBD>` — S2922 close cascade (handoff + 00-START refresh + wrapper pin bump + legacy-error envelope framing corrections in both validation docs).

**Tools shipped (2 — Slice 4 batch 5 mixed pair):**
- `podcast_tool` (4 actions: shows/episodes/scripts/stats — all pure-ORM SELECT). Handler at `td_handlers_gateway.py:1959`, 87 lines actual body. No TOOL_DEFAULTS or TOOL_ACTION_METADATA entries; auto-classifier upgrades `untested → validated_full`.
- `vip_invite_tool` (3 actions: list=READ + create=`contained` mutation + revoke=`spreading` mutation). Handler at `td_handlers_gateway.py:941`, 78 lines actual body. First Slice-4 exercise of §5a `spreading` tier — cross-table VIPInvite.revoked_at flip + optional User.is_active flip on redeemed_by.

**Legacy-error envelope framing REFRAMED (S2922 close-cascade discovery):**
- Live-verify idempotency test returned `{"error": "Already revoked", "error_code": "legacy_error"}` — the `error_code` field IS present.
- Verified at `core/services/tool_dispatcher.py:862-885` — dispatcher auto-backfills `error_code='legacy_error'` when handler omits it (S2874 mixed-mode migration, S2876 breadcrumb telemetry).
- Corrected framing shipped in podcast_tool_validation.md + vip_invite_tool_validation.md §5: handler omits `error_code`; dispatcher backfills; final envelope observed by callers is `{"error": <str>, "error_code": "legacy_error"}`.
- "Legacy-error envelope" ledger substrate is actually a **count of un-migrated handlers**, not "handlers with no error_code". Value `'legacy_error'` is a first-class semantic signal (matches Rigby S2920 Q4(a) proposal — still Chris-gated post-D6 per S2921 Q5(c)).

**Rigby joint SIGN (2-turn cycle + Q5 zoom-out, zero rubber-stamp):**
- T0 SIGN turn 1: 8 `repo_tool` runs. Q1 AGREE (a) mixed batch (Claude+Rigby aligned first turn). vip_invite mutation shape grep-verified at HEAD 5983f5a23 (`td_handlers_gateway.py:1004-1010` cross-table flip). Cockpit Q4 pre-audit: static `@receiver(post_save, sender=CeleryTaskEvent)` grep clean across 25 signal files, with honest caveat re: dynamic `.connect()`.
- T0 SIGN turn 2: 13 `repo_tool` runs. Q2 first-hop-literal per-tool grep confirmed 0/2 (podcast + vip_invite). Notable side-observation: `td_handlers_gateway.py:1030` and `:1462` contain SELF-reference literals `'tool': 'cockpit_tool'` and `'tool': 'narrative_tool'` in help text — not outbound dispatches. Gateway-wide watch stays 0/17. Q3 spreading-tier docs shape confirmed via template file read at `_TEMPLATE_per_tool_validation.md:128-136`.
- Q5 zoom-out: (i) S2923/S2924 close horizon reasonable; (ii) span-math regen **promoted to permanent close-ceremony step**; (iii) cascading tier held for organic emergence (no synthetic force-surface); (iv) Ledger row 156 surfaced at Slice-4 close (S2923–S2924).
- Post-merge live verify: podcast 3/4 actions clean (scripts skipped — empty data); vip_invite 3/3 core actions clean + idempotency guard verified.

**Sweep progress (post-S2922, gap-map regen at close):**
- **Slice 4 (`td_handlers_gateway`):** 14/17 shipped. Batch 5 CLOSED as mixed pair.
- Remaining 3 with **verified** handler line counts (grep + boundary math against `td_handlers_gateway.py` at sha `3078dd48b`):
  - **cockpit** — handler 1022–1452 = **431 lines** — MUTATION **`cascading`** (first §5a `cascading` example — S2922 discovery confirms: `CeleryTaskEvent.save` at 1030-1039 → dynamic `post_save.connect()` at `failure_cluster_signals.py:183` → `escalate_failure_cluster` → `human_attention_bridge` downstream reach; only fires on FAILURE-status rows per dedup_window_min=30 gate).
  - **proactive** — handler 1560–1699 = **140 lines** — MUTATION `spreading` (update×3, bulk-ack up to 200 rows).
  - **profile** — handler 2294–2481 = **188 lines** — MUTATION `spreading` (get_or_create×2 + save×1).
- Total corpus untested: 33 → **31** post-batch-5 (2 additional flips: podcast + vip_invite).
- Gap map: **68 full · 10 partial · 7 unknown · 31 untested** (post-close-cascade projected; regen at S2923 open will confirm).
- Session cumulative pace: 2 tools / 1 session (with 2-turn SIGN + 21 repo_tool receipts + Chris-facing plain-English framing + post-merge live-dispatch + close-cascade dispatcher-backfill discovery + 2 ledger entries appended).

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3474 recycled clean at `sha=3078dd48b009`: 5 fresh workers (default + pa + long_running + broadcast + code_jobs) + beat, zero surviving old PIDs.

Full session context: `docs/handoffs/SESSION_2922_SLICE_4_BATCH_5_MIXED_PAIR.md`.

---

## S2923 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 4 batch 6 composition SIGN cycle

**No blocking Chris D-verdict from S2922 close.** Batch 6 composition is a joint Claude+Rigby recommendation → Chris yes/no.

**Batch 6 options — 3 remaining Slice 4 tools grouped by tier:**

Mutation `cascading` (§5a first exercise — confirmed via S2922 discovery): `cockpit` (431 lines).
Mutation `spreading` (§5a exercised at vip_invite S2922, needs 2nd + 3rd scale): `proactive` (140), `profile` (188).

**Options:**
- **(a) Cockpit solo (first `cascading` exercise, largest single-tool ship):** exercises new tier cleanly on the biggest handler; may need 2 SIGN turns for full signal-chain classification (CeleryTaskEvent.save → escalate_failure_cluster → human_attention_bridge reach breadth); batch 7 closes Slice 4 with proactive + profile spreading pair. Precedent: S2921 batch 4 self_awareness single-tool `contained` pilot.
- **(b) Proactive + profile spreading pair:** scales spreading tier from vip_invite pilot to 2 more tools in one batch; matches batch 5 mixed-pair success; leaves cockpit for batch 7 dedicated `cascading` ship. Slice 4 closes in 2 more sessions.
- **(c) Full trio (cockpit + proactive + profile):** Slice 4 CLOSE in one ship; largest batch; may need 2-3 SIGN turns; violates the "mutation-heavy single-tool batch pattern" (Ledger row 159, 2nd trigger candidate). Not recommended without explicit Chris directive.
- **(d) Proactive solo (bulk-multi-row spreading):** fast validation; batch 7 covers cockpit + profile.

Recommend **(a)** — cockpit solo exercises the `cascading` tier once cleanly on the biggest handler + signal-chain depth requires dedicated SIGN attention (dispatcher-backfill discovery this session + dynamic-connect discovery close-cascade both underscore that cockpit needs careful classification, not batching pressure). Precedent: S2921 batch 4 single-tool `contained` pilot succeeded with the same "exercise new tier once cleanly before scaling" argument. Batch 7 then closes Slice 4 with the spreading pair (proactive + profile).

**Q1 (batch 6 composition):** Pick option (a) / (b) / (c) / (d).

**Q2 (Appendix N/A applicability):** Continue gateway-wide 0/17 first-hop-literal watch. Per-tool grep for whichever batch wins. Note S2922 side-observation: gateway handlers contain SELF-reference `'tool': 'X_tool'` literals in help text — grep should exclude those from outbound-dispatch counts.

**Q3 (cascading-tier template exercise):** For (a) — confirm §5a cascading-tier docs shape for cockpit. Includes: full signal-chain grep (`escalate_failure_cluster` → `human_attention_bridge` → any further downstream), dedup-window gate confirmation (FAILURE-status only per `dedup_window_min=30`), Django-startup log cross-check (per new "static @receiver grep insufficient" ledger observation).

**Q4 (proactive + profile grep pre-audit — even if cockpit wins for batch 6):** Regardless of (a)/(b)/(c)/(d) winning, run proactive + profile mutation-verb + signal-chain grep on next Rigby SIGN turn to confirm both are `spreading` (bounded cross-row) not `cascading` (signal-firing). Determines batch 7 shape.

**Q5 zoom-out (required per feedback_zoom_out_ask_per_rigby_sign):**
- Slice 4 close horizon: 14/17 shipped in 5 sessions (S2918–S2922). 3 remaining. If (a) → batch 7 ships remaining 2 spreading tools → Slice 4 closes S2924. If (b) → batch 7 ships cockpit solo → Slice 4 closes S2924. If (c) → Slice 4 closes S2923 (aggressive; may need substrate follow-up if cascading tier documentation needs pass 2). If (d) → Slice 4 closes S2925 worst case. Reasonable close horizon: **S2924.**
- Legacy-error envelope framing corrected this session (dispatcher backfill discovery). Should the semantic-nuance refresh (`error_code='legacy_error'` as first-class un-migrated signal) be re-surfaced at Slice-4 close, or stay Chris-gated post-D6?
- orm_inspect_tool allowlist gap (Ledger #31 MEDIUM) blocked ORM-hard cross-checks for `spreading` tier full-exercise this session. Batch 6 spreading tools (proactive: user-scoped notifications; profile: EnhancedUserProfile) will need similar ORM verification. Should tool-surface expansion (add User + VIPInvite + related to allowlist) be a Slice-4-close deliverable, or defer as engineering item?
- Dynamic post_save.connect() discovery: 1st in-sweep instance. Should batch 6 SIGN template mandate combined-pattern grep (`@receiver` + `.connect(` + Django-startup log) for every signal-cascade classification, or wait for 2nd instance?

### Alternative Step 1 candidates

- **`narrative_tool` dev-env drift fix** — Rigby Tool Gap Ledger entry `5c84e75a` from S2919; requires ~30 min migration replay + verification. Engineering task, not sweep.
- **Legacy-error envelope substrate arc** — 18× corroborated post-S2922 (17=podcast + 18=vip_invite). Framing REFRAMED this session (dispatcher backfill discovery) — decision point sharper. **NOT to be opened without explicit Chris directive** (post-D6 evaluation candidate).
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.
- **orm_inspect_tool allowlist expansion** — engineering task from Ledger #31 MEDIUM. ~1-2 hours; unblocks cross-table `spreading`-tier full-exercise verification for future batches.

### What's forbidden at S2923 (D6 MORATORIUM still in force)

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
- **No `post_save signal cascade` substrate arc without explicit Chris directive.** S2922 discovery makes cockpit `cascading` the first in-scope example; batch 6 SIGN handles it inline per §5a.
- **No harness-level soft_error accounting substrate arc without explicit Chris directive.**
- **No "metadata-classification-as-runtime-gate" substrate arc without explicit Chris directive.**
- **No "hidden network/LLM in read-shaped gateway" Fold promotion without 3rd confirmed instance.** 2/3 (S2913 + S2914).
- **No "cascade audit companion doc" pattern promotion without 2nd instance.** 1/2 (S2915).
- **No "IRREVERSIBLE dry_run flag harness lint" Fold promotion without 3rd instance.** 2/3 (S2908 + S2915).
- **No `NEXT_HEADING_RE` parser fix without Chris directive or 3rd instance.** 2 instances (S2914 + S2915). Batch 6+ workaround = keep `###` only under §5b/appendices (AFTER Covered actions).
- **No "observability-tracker as MUTATION vector" Fold promotion without 2nd instance.** 1st (S2916).
- **No "undocumented envelope field (`error_code: 'legacy_error'`)" substrate arc without explicit Chris directive.** **18 instances corroborated post-S2922** (16 pre-batch + podcast=17 + vip_invite=18). **REFRAMED this session** — dispatcher backfill discovery at `tool_dispatcher.py:862-885`. Rigby S2920 Q4(a) semantic-nuance refresh (treat `error_code` values as first-class semantics) still deferred post-D6 per S2921 Q5(c) Chris ratification; may be worth re-surfacing at Slice-4 close.
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
- **No "per-tool `limit` default divergence from gateway norm" Fold promotion without 2nd instance.** 1st (S2921 self_awareness_tool). Watch continues into batch 6+.
- **No "envelope-representation asymmetry (write-as-0.0-read-as-null)" Fold promotion without 2nd instance.** 1st (S2921 self_awareness collect/metrics).
- **No "00-START span-math source-of-truth regen" Fold promotion.** Regeneration policy commitment at S2921 close per Chris Q5(b) ratification — now permanent close-ceremony step per Rigby Q5(ii) AGREE this session.
- **NEW S2922 forbidden entries:**
  - **No "schema description surface-documents cross-row side effect" Fold promotion without 2nd instance.** 1st (vip_invite `revoke` at `pa_tool_schemas.py:4544`). Recorded as authoring positive.
  - **No "`user_id` param IGNORED for admin-scoped mutation" Fold promotion without 2nd instance.** 1st (vip_invite `create` hardcodes first-superuser). Absorbed by single-user pre-prod.
  - **No "`total`-vs-`len(list)` divergence without `has_more`" Fold promotion without 2nd instance.** 1st (vip_invite `list`).
  - **No "static @receiver grep insufficient for signal-cascade classification" Fold promotion without 2nd instance.** 1st (S2922 close-cascade FAILURE_CLUSTER discovery). Ledger #32 LOW.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — unchanged.
- **Testing Discipline chapter candidacy** — Ledger row 154. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged; **worth surfacing at Slice-4 close per S2921 + S2922 Q5(iv) AGREE.**
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Reinforced by S2921 self_awareness pilot + S2922 vip_invite spreading first-exercise success — 2nd trigger candidate. If (b) or (c) wins batch 6, 3rd trigger could accumulate.
- **2-tier evidence template promotion** — Ledger row 160. Unchanged.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. CLOSED at S2904.
- **Response-level introspection field creep** — Ledger row 162. Unchanged.
- **S2905 metadata-pattern-selection lint** — batch 5 used no TOOL_DEFAULTS/TOOL_ACTION_METADATA. Not incrementing lint counter.
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
- **S2921 batch 4 Ledger candidates** — legacy-error envelope 18th (batch 5 both tools); §5a first `spreading` exercise (vip_invite this batch); `limit` default divergence still 1st.
- **NEW S2922 batch 5 Ledger candidates:**
  - **First §5a `spreading` exercise (vip_invite.revoke)** — cross-table VIPInvite+User bounded reach. Batch 6+ scales to proactive + profile.
  - **Dispatcher auto-backfill `error_code='legacy_error'` discovery** — formally named in-doc this session at `tool_dispatcher.py:862-885`.
  - **Mixed user-scoping ACROSS actions (podcast episodes vs shows/stats)** — cross-action variant of the calendar_tool.stats intra-response mix.
  - **Schema description surface-documents cross-row side effect (vip_invite revoke)** — 1st Slice-4 authoring-positive instance.
  - **`user_id` param IGNORED for admin-scoped mutation (vip_invite create)** — 1st Slice-4 instance.
  - **`total`-vs-`len(list)` divergence without `has_more` (vip_invite list)** — 1st Slice-4 instance.
  - **Dynamic post_save.connect() invisible to static @receiver grep** — Ledger #32 LOW.
  - **orm_inspect_tool allowlist gap for auth-scoped mutation validation** — Ledger #31 MEDIUM.
  - **Podcast script hard-truncation without pagination cursor** — 3000-char cap.
  - **00-START span-math regen validated 2nd time** — podcast 251→89 (162-line drift). Chris Q5(b) commitment now permanent per Rigby Q5(ii) AGREE.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — unchanged.
- **Applicability metadata pattern (entry #28)** — unchanged.
- **Baseline lookback cap (entry #29)** — MITIGATED at PR #3423 (S2899).
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — unchanged.
- **NEW Rigby Tool Gap Ledger entries this session:**
  - **Entry #31 (MEDIUM) — orm_inspect_tool missing VIPInvite + User from allowlist** — blocks ORM-hard cross-check for `spreading`-tier full-exercise verification.
  - **Entry #32 (LOW) — static @receiver grep insufficient for signal-cascade classification** — substrate observation from cockpit dynamic-connect discovery.
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

**Slice 4 — `td_handlers_gateway` (17 tools):** **OPEN — 14/17 shipped.**
- S2918 batch 1: 4 tools ✓ (gateway small-tier quartet — analytics/audit/campaign/experiment)
- S2919 batch 2: 4 tools ✓ (gateway small-tier read-only quartet — discord/distribution/ats/narrative; template-preservation swap #1)
- S2920 batch 3: 3 tools ✓ (gateway medium-tier read-only trio — mobile/calendar/conceptforge; template-preservation swap #2 with split-batch escalation)
- S2921 batch 4: 1 tool ✓ (self_awareness mutation-template pilot; §5a 4-tier blast-radius amendment shipped alongside)
- **S2922 batch 5: 2 tools ✓ (mixed pair — podcast READ + vip_invite spreading mutation; first §5a `spreading` exercise; legacy-error dispatcher-backfill discovery + dynamic post_save.connect discovery)**

**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix). **S2921 §5a 4-tier taxonomy amendment** shipped as doc-only sweep substrate.

**Total remaining tools to close:** ~31. Post-S2922 pace: 2 tools this session (mixed pair) with full mutation-verify + envelope-proxy cross-check + dispatcher-backfill discovery. Slice 4 CLOSE at ~2 more sessions (batch 6 = cockpit cascading OR spreading pair, batch 7 covers remainder).

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2922 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2922: zero A4 spend — pure sweep-batch engineering (2 tools + close cascade).** A1 shipping spend was 1 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2922)

See:
- **S2922 handoff (current):** `docs/handoffs/SESSION_2922_SLICE_4_BATCH_5_MIXED_PAIR.md`
- **S2921 handoff:** `docs/handoffs/SESSION_2921_SLICE_4_BATCH_4_SELF_AWARENESS_PILOT.md`
- **S2920 handoff:** `docs/handoffs/SESSION_2920_SLICE_4_BATCH_3.md`
- **S2919 handoff:** `docs/handoffs/SESSION_2919_SLICE_4_BATCH_2.md`
- **S2918 handoff:** `docs/handoffs/SESSION_2918_SLICE_4_BATCH_1.md`
- **S2917 handoff:** `docs/handoffs/SESSION_2917_SLICE_3_BATCH_7_CLOSE.md`
- **S2916 handoff:** `docs/handoffs/SESSION_2916_SLICE_3_BATCH_6.md`
- **S2915 handoff:** `docs/handoffs/SESSION_2915_SLICE_3_BATCH_5.md`
- **S2914 handoff:** `docs/handoffs/SESSION_2914_SLICE_3_BATCH_4.md`
- **S2913 handoff:** `docs/handoffs/SESSION_2913_SLICE_3_BATCHES_1_2_3.md`
- **S2912 handoff:** `docs/handoffs/SESSION_2912_SLICE_2_CLOSE.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (§5a **4-tier blast-radius taxonomy** amended S2921)
- **S2922 per-tool validation docs (this session's 2):** `docs/research/tools/validation/{podcast,vip_invite}_tool_validation.md`
- **S2921 per-tool validation doc:** `docs/research/tools/validation/self_awareness_tool_validation.md`
- **S2920 per-tool validation docs (batch 3):** `docs/research/tools/validation/{mobile,calendar,conceptforge}_tool_validation.md`
- **S2919 per-tool validation docs (batch 2):** `docs/research/tools/validation/{discord,distribution,ats,narrative}_tool_validation.md`
- **S2918 per-tool validation docs (batch 1):** `docs/research/tools/validation/{analytics,audit,campaign,experiment}_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 83 non-substrate post-S2922)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (entries #31 orm_inspect_tool allowlist gap + #32 static-@receiver-grep-insufficient appended S2922).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
