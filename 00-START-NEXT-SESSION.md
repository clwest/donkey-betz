# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2921 CLOSE → S2921 SHIPPED Slice 4 batch 4 (self_awareness mutation-template pilot + §5a 4-tier blast-radius amendment). **12/17 shipped.** **S2922 OPENS WITH SLICE 4 BATCH 5 (composition decision — 3 tools available: podcast READ, +2 spreading mutation).** D6 MORATORIUM STILL IN FORCE

**Refreshed 2026-07-23 (S2921 close).** Batch 4 shipped 1 mutation-capable tool (`self_awareness_tool`, 5 actions in scope including the mutation action `collect` classified `contained`) as the deliberate template pilot for the §5a 4-tier blast-radius taxonomy amendment shipped in the same PR. Chris ratified both S2921-open decisions: (A) sweep-doc note only for template-preservation swap pattern with 3rd-trigger-outside-sweep Playbook-promotion rule; (B) single-tool self_awareness pilot per Rigby Q1(b). Rigby T0 SIGN 2-turn cycle grounded in 12 `repo_tool` receipts — corrected 2 of 4 mutation-verb claims in the S2920 close 00-START (vip_invite also flips User.is_active; profile = get_or_create×2 + save×1). Post-merge live verify: all 5 actions ≤60ms + follow-up cross-check + ORM-direct SystemMetrics count=1 with matching pk/timestamp/counts. `contained` classification 100% verified end-to-end.

**PRs shipped this session:**
- u-d-b PR [#3472](https://github.com/clwest/donkey-betz-platform/pull/3472) — Slice 4 batch 4 (self_awareness pilot + §5a 4-tier taxonomy), merged at `0ccf3450d`.
- u-d-b PR `<TBD>` — S2921 close cascade (handoff + 00-START refresh from live evidence per Chris Q5(b) + wrapper pin bump).

**Tools shipped (1 — Slice 4 batch 4 pilot):**
- `self_awareness_tool` (5 actions: metrics/reports/evolution/stats/collect — 4 pure-ORM SELECT + 1 mutation-INSERT classified `contained` per new §5a 4-tier taxonomy). Handler at `td_handlers_gateway.py:2482`, 118 lines. No TOOL_DEFAULTS or TOOL_ACTION_METADATA entries; auto-classifier upgrades `untested → validated_full`.

**Template amendment (this ship):**
- `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` §5a expanded with:
  - **4-tier blast-radius taxonomy** (`contained` / `spreading` / `cascading` / `external`) as recommended authoring enum. Doc-only per Rigby Q3 verdict (§5a already accommodated the schema; not Playbook-worthy — authoring taxonomy, not safety invariant).
  - **Mutation-scan-swap pattern** codified as sweep-doc note (2 in-sweep triggers: S2919 vip_invite→narrative + S2920 proactive+self_awareness+profile split-batch). Explicit **3rd-trigger-outside-sweep** Playbook-promotion rule per Rigby Q4 recommendation. Precedent: PLAYBOOK-6.10.6 (two-trigger sweep-note → three-trigger Playbook promotion pattern).
  - **Freeze-template-per-ship-session process hygiene note** — design-only + ship-only sessions when 2+ tools would need to ship under a changing template; pilot-single-tool exception documented.

**Rigby joint SIGN (2-turn cycle + Q5 zoom-out, zero rubber-stamp):**
- T0 SIGN turn 1: 10 `repo_tool` runs (1 repo-wide timeout + 9 with line-number receipts). Q1 initially DISAGREE with Claude's Q1(a) recommendation; T2 argument reversed Claude to Q1(b). Corrected 2 of 4 00-START claims (vip_invite user.is_active flip; profile actual verb shape).
- T0 SIGN turn 2: 2 more `repo_tool` runs (template file read + Playbook two-trigger precedent grep). Q3 AGREE §5a doc-only sufficient; Q4 AGREE sweep-doc note + 3rd-trigger-outside-sweep promotion rule (grounded in PLAYBOOK-6.10.6 precedent).
- Q5 zoom-out: (a) pace-acceleration sustainable short-term; process-thrash risk mitigated via freeze-template hygiene; (b) 00-START span-math regen at close (this session — done); (c) legacy-error semantic-nuance refresh deferred post-D6; (d) Q1(b) mitigates cockpit displacement risk vs Q1(a).
- Post-merge live verify: 5/5 actions ≤60ms; cross-check metrics after collect returned exact snapshot_id=1 row with matching timestamp + counts; ORM-direct SystemMetrics.objects.count() == 1. `contained` blast-radius holds end-to-end.

**Sweep progress (post-S2921 with live-evidence span-math regen — replaces S2920 close claims):**
- **Slice 4 (`td_handlers_gateway`):** 12/17 shipped. Batch 4 CLOSED as single-tool pilot.
- Remaining 5 with **verified** handler line counts (grep + boundary math against `td_handlers_gateway.py` at sha `0ccf3450d`):
  - **cockpit** — handler 1022–1452 = **431 lines** — **MUTATION** (3 verbs: `CeleryTaskEvent.objects.create` + `event.save(update_fields=['status'])` + `r.delete(...)` Redis-key). Prior S2920 Q4(d) "cockpit deferred until mutation-shape settled" now vindicated — cockpit is NOT pure-READ. `CeleryTaskEvent.save` may fire `post_save` signals — grep-verify at batch-open before classifying `spreading` vs `cascading`.
  - **podcast** — handler 1959–2047 = **89 lines** (S2920 close claimed 251 — **162-line span-math drift caught** via live evidence). **PURE READ** — no mutation verbs found in span.
  - **profile** — handler 2294–2481 = **188 lines** — MUTATION, `spreading` (get_or_create×2 + save×1 per Rigby S2921 turn 1 grep).
  - **proactive** — handler 1560–1699 = **140 lines** — MUTATION, `spreading` (update×3, bulk-ack up to 200 rows).
  - **vip_invite** — handler 941–1021 = **81 lines** — MUTATION, `spreading` (create + save×2 including `redeemed_by.is_active=False` cross-table flip per Rigby S2921 turn 1 correction).
- Total corpus untested: 36 → **35** (batch 4 pilot flipped 1 untested → full via auto-classifier).
- Gap map: **64 full · 10 partial · 7 unknown · 35 untested** (validation-doc counts post-regen).
- Session cumulative pace: 1 tool + 1 template amendment / 1 session (with 2-turn SIGN + mutation-scan grounding + Chris-facing framing pressure-test + post-merge live verify + ORM cross-check + span-math regen).

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3472 recycled clean at `sha=0ccf3450def1`: 5 fresh workers (default + pa + long_running + broadcast + code_jobs) + beat, zero surviving old PIDs.

Full session context: `docs/handoffs/SESSION_2921_SLICE_4_BATCH_4_SELF_AWARENESS_PILOT.md`.

---

## S2922 open sequence

### Step 1 (REQUIRED FIRST ACTION) — Slice 4 batch 5 composition SIGN cycle

**No blocking Chris D-verdict from S2921 close.** Batch 5 composition is a joint Claude+Rigby recommendation → Chris yes/no.

**Batch 5 options — 5 remaining Slice 4 tools grouped by shape:**

Pure-READ (S2796 doc-only shape, well-exercised): `podcast` (89 lines).
Mutation `spreading` (§5a taxonomy amended S2921, needs first exercise): `vip_invite` (81), `proactive` (140), `profile` (188).
Mutation shape TBD (needs grep at batch-open): `cockpit` (431 — big; `CeleryTaskEvent.save` may push into `cascading` tier via `post_save` signals).

**Options:**
- **(a) Mixed batch — podcast READ + vip_invite (smallest spreading mutation):** validates §5a `spreading` tier on the smallest mutation surface while shipping 2 tools. Preserves ship progress; exercises the new tier once before scaling to the full `spreading` trio. Cockpit stays deferred until its own dedicated batch (§7.x candidate).
- **(b) Full spreading trio — vip_invite + proactive + profile:** 3 mutation tools using the newly-exercised §5a `spreading` tier from batch 4's template pilot. Closes out all Slice-4 `spreading` mutations in one batch. Podcast + cockpit follow as batch 6 (or podcast slotted into cockpit batch as a low-cost pure-READ additional).
- **(c) Cockpit dedicated batch (431 lines):** ship cockpit alone once the `cockpit.CeleryTaskEvent.save` classification is grep-verified. Largest single-tool ship. Batch 6 covers podcast + remaining spreading trio.
- **(d) Podcast solo (fast close):** ship podcast alone as a small pure-READ tool. Slice 4 progress → 13/17 but leaves 4 mutation-capable tools unshipped. Not recommended as-primary but acceptable if Chris wants a light session.

Recommend **(a)** — validates the §5a `spreading` tier once cleanly (vip_invite's cross-table user.is_active flip is the archetype `spreading` case) before running it on 2 more tools in batch 6.

**Q1 (batch 5 composition):** Pick option (a) / (b) / (c) / (d).

**Q2 (Appendix N/A applicability):** Continue gateway-wide 0/17 first-hop-literal watch. Per-tool grep for whichever batch wins.

**Q3 (spreading-tier template exercise):** Confirm §5a spreading-tier docs shape for vip_invite (or proactive if (b) wins). Includes: cross-row mutation grep (both tables affected), user-scope confirmation, deferral-vs-ship-in-scope decision per action.

**Q4 (cockpit pre-audit):** Regardless of (a)/(b)/(d) winning, run cockpit mutation-verb grep on next Rigby SIGN turn to classify `CeleryTaskEvent.save` — `post_save` signal grep on the `CeleryTaskEvent` model. If signal-safe → `spreading`; if signal-firing → `cascading` (first §5a `cascading` example). Determines batch 6 shape.

**Q5 zoom-out (required per feedback_zoom_out_ask_per_rigby_sign):**
- Slice 4 pace: 12/17 shipped in 4 sessions (S2918–S2921). 5 remaining. If batch 5 ships 2 tools (a) + batch 6 ships remaining 3 (spreading trio + cockpit + podcast), Slice 4 closes in 2 more sessions. If (b) → 1 more session for cockpit + podcast. Reasonable close horizon: **S2923 or S2924.**
- 00-START span-math regen worked (podcast 251-claim vs 89-actual). Do we make this a permanent close-ceremony step, or a "run when triggered" hygiene rule? Note: not codified as Fold per S2921 close — still process commitment.
- 4-tier §5a taxonomy amendment lands unexercised for `spreading`/`cascading`/`external`. Batch 5+6 exercises `spreading`; `cascading` may hit at cockpit; `external` remains theoretical until a Slice 5+ tool surfaces it. Watch.
- Ledger row 156 (close-ceremony ledger-staleness gate) still deferred. Rigby last-touched at S2900. Worth surfacing at Slice-4 close?

### Alternative Step 1 candidates

- **`narrative_tool` dev-env drift fix** — Rigby Tool Gap Ledger entry `5c84e75a` from S2919; requires ~30 min migration replay + verification. Engineering task, not sweep.
- **Legacy-error envelope substrate arc** — 16× corroborated post-S2921. **NOT to be opened without explicit Chris directive** (post-D6 evaluation candidate); Rigby S2920 Q4(a) semantic-nuance refresh still deferred per S2921 Q5(c) Chris ratification.
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches. Still valid.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.

### What's forbidden at S2922 (D6 MORATORIUM still in force)

- No new strategic discovery arcs. No opportunity portfolio expansions. No evaluation frameworks. No layer-boundary design arcs.
- No R1a-shaped proposals (upgrading character-os to fleet HMAC).
- **No v2 → v3 harness schema bump WITHOUT substrate-arc-scoped SIGN.**
- No new gate/lint proposals.
- No agent-substrate validation arc.
- **No `minimal_safe_args_v2` arc opening without explicit Chris directive.**
- **No entrypoint-side context-injection substrate arc without explicit Chris directive.**
- **No "schema-drift-fix Fold promotion" without explicit Chris directive.** **3/3 TRIGGERED at S2919 batch 2 + 4th confirming.** No new instance this batch. Triggers evaluation — still requires Chris D-verdict.
- **No `dry_run` infrastructure arc for mutation-class dispatchers without explicit Chris directive.**
- **No Concern C schema↔doc drift substrate arc.** Framing (a) still recommended for future post-D6 ratification.
- **No `post_save signal cascade` substrate arc without explicit Chris directive.**
- **No harness-level soft_error accounting substrate arc without explicit Chris directive.**
- **No "metadata-classification-as-runtime-gate" substrate arc without explicit Chris directive.**
- **No "hidden network/LLM in read-shaped gateway" Fold promotion without 3rd confirmed instance.** 2/3 (S2913 conversation_tool.search + S2914 intelligence_tool.search). Watch continues into Slice 4 batch 5+.
- **No "cascade audit companion doc" pattern promotion without 2nd instance.** 1/2 (S2915 competitor_comparison_tool.delete).
- **No "IRREVERSIBLE dry_run flag harness lint" Fold promotion without 3rd instance.** 2/3 (S2908 media_tool.delete + S2915 competitor_comparison_tool.delete).
- **No `NEXT_HEADING_RE` parser fix without Chris directive or 3rd instance.** 2 instances (S2914 + S2915). Batch 5+ workaround = keep `###` only under §5b/appendices (AFTER Covered actions).
- **No "observability-tracker as MUTATION vector" Fold promotion without 2nd instance.** 1st (S2916 http_smoke_test OpsRunTracker).
- **No "undocumented envelope field (`error_code: 'legacy_error'`)" substrate arc without explicit Chris directive.** **16 instances corroborated post-S2921** (15 at S2920 + batch-4 pilot self_awareness). Rigby S2920 Q4(a) semantic-nuance refresh (treat `error_code` values as first-class semantics) deferred post-D6 per S2921 Q5(c) Chris ratification.
- **No "grep-before-claim" Fold promotion without 2nd instance.** 1st (S2916 fleet_health HMAC-claim).
- **No "dispatcher re-entry" Fold promotion without 2nd instance.** 1st observed (S2917 workflow_run_tool.start).
- **No "handler-forwarded param not in schema" Fold promotion without 2nd instance.** 1st (S2917 workflow_run_tool.start `focus_areas`).
- **No "contract asymmetry — single vs dual identifier in async envelopes" Fold promotion without 2nd instance.** 1st (S2917 studio single task_id vs workflow_run dual).
- **No "envelope-key asymmetry across actions" Fold promotion without explicit Chris directive.** 3/3 TRIGGERED at S2919 batch 2. No new distinct sub-pattern this batch. Still Chris-gated.
- **No "multi-tenant leak on detail/results action" Fold promotion without post-D6 evaluation.** 3 instances (S2918 campaign_tool.detail + experiment_tool.results + S2920 calendar_tool.upcoming); absorbed by single-user pre-prod context per `project_single_user_pre_prod_operating_context`.
- **No "template-preservation swap" Fold promotion without explicit Chris directive.** 2 in-sweep triggers (S2919 + S2920) — **CODIFIED at S2921 as sweep-doc note** with explicit 3rd-trigger-outside-sweep promotion rule. Chris D-verdict ratified.
- **No "mixed user-scoping within single response" Fold promotion without 2nd instance.** 1st (S2920 calendar_tool.stats: `total_channels` user-scoped, `total_episodes` un-scoped). 2nd instance triggers evaluation.
- **No "filesystem-read handler shape (open + regex)" Fold promotion without 3rd instance.** 2/3 (S2919 discord_tool + S2920 mobile_tool). 3rd instance triggers evaluation.
- **No "limit does not gate nested lists" Fold promotion without 2nd instance.** 1st (S2920 conceptforge_tool.run_detail: `limit` applies to top-level `runs` only, not `stages`/`artifacts`). 2nd instance triggers evaluation.
- **No "per-tool `limit` default divergence from gateway norm" Fold promotion without 2nd instance.** 1st (S2921 self_awareness_tool: default 10, cap 30 vs gateway norm default 20, cap 50). 2nd instance triggers evaluation.
- **No "envelope-representation asymmetry (write-as-0.0-read-as-null)" Fold promotion without 2nd instance.** 1st (S2921 self_awareness collect/metrics: 0.0-writes-return-null via Python falsy filter). 2nd instance triggers evaluation.
- **No "00-START span-math source-of-truth regen" Fold promotion.** Regeneration policy commitment at S2921 close per Chris Q5(b) ratification — not a Fold; close-ceremony hygiene step. Podcast 251-claim vs 89-actual (162-line drift) caught this ship via live-evidence regen.

### What's queued but deferred (do NOT open unless Chris directs)

- **Original character-os stand-by** — unchanged.
- **Testing Discipline chapter candidacy** — Ledger row 154. Unchanged.
- **Bridge call observability rename-risk** — Ledger row 155. Unchanged.
- **Close-ceremony ledger-staleness gate** — Ledger row 156. Unchanged; worth surfacing at Slice-4 close per S2921 Q5.
- **Sweep shape doc-only defers semantic assertions** — Ledger row 157. Unchanged.
- **Sweep batch cadence outcome gate** — Ledger row 158. Unchanged.
- **Mutation-heavy single-tool batch pattern** — Ledger row 159. Reinforced by S2921 self_awareness pilot success — 2nd trigger candidate.
- **2-tier evidence template promotion** — Ledger row 160. Unchanged.
- **Sweep-arc pace sustainability substrate arc** — Ledger row 161. CLOSED at S2904.
- **Response-level introspection field creep** — Ledger row 162. Unchanged.
- **S2905 metadata-pattern-selection lint** — batch 4 used no TOOL_DEFAULTS/TOOL_ACTION_METADATA. Not incrementing lint counter.
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
- **S2916 Ledger candidates (batch 6)** — legacy-error envelope 16× corroborated post-S2921; observability-tracker as MUTATION vector still 1/2; grep-before-claim still 1/2.
- **S2917 Ledger candidates (batch 7)** — contract asymmetry, undocumented handler-forwarded param, dispatcher re-entry — all still 1st instance.
- **S2918 batch 1 Ledger candidates** — envelope-key asymmetry 3/3 triggered at S2919; multi-tenant leak 3rd at S2920 (still single-user pre-prod absorbed); schema-drift-fix 3/3+4th; view-reuse `stage3_dashboard` still documented-not-verified.
- **S2919 batch 2 Ledger candidates** — divergent `limit` hard-cap (1st); N+1 query pattern (1st); envelope-shape intra-tool asymmetry (1st); `variations` truncation-to-3 (1st); `platform_account` stringified-UUID-not-name (1st) — all still 1st instances.
- **S2920 batch 3 Ledger candidates** — multi-tenant leak 3rd (single-user absorbed); mixed user-scoping 1st; filesystem-read shape 2/3; `limit` doesn't-gate-nested-lists 1st; 500-byte placeholder heuristic (usability, not defect-worthy).
- **NEW S2921 batch 4 Ledger candidates:**
  - **First mutation-shipped Slice 4 tool** — self_awareness.collect `contained` classification 100% verified end-to-end. Establishes 4-tier pattern in-doc. Batch 5 (spreading) is next exercise.
  - **Legacy-error envelope 16th instance** — self_awareness_tool return path. Substrate arc still Chris-gated.
  - **`limit` default divergence (default 10, cap 30)** — 1st Slice-4 instance vs gateway norm (default 20, cap 50). 2nd instance triggers evaluation.
  - **Envelope-representation asymmetry (write 0.0, read null)** — 1st. Python falsy filter on 0.0 numeric fields at handler line 2498. 2nd instance triggers evaluation.
  - **Podcast span-math drift caught via live evidence** — 251-claim vs 89-actual (162 lines). Vindicates Chris Q5(b) close-ceremony regen commitment.
- **Batched-items structural (Rigby Tool Gap Ledger entry #27)** — unchanged.
- **Applicability metadata pattern (entry #28)** — unchanged.
- **Baseline lookback cap (entry #29)** — MITIGATED at PR #3423 (S2899).
- **Ingest integrity vs downstream pipeline freshness separation (entry #30)** — unchanged.
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

**Slice 4 — `td_handlers_gateway` (17 tools):** **OPEN — 12/17 shipped.**
- S2918 batch 1: 4 tools ✓ (gateway small-tier quartet — analytics/audit/campaign/experiment)
- S2919 batch 2: 4 tools ✓ (gateway small-tier read-only quartet — discord/distribution/ats/narrative; template-preservation swap #1)
- S2920 batch 3: 3 tools ✓ (gateway medium-tier read-only trio — mobile/calendar/conceptforge; template-preservation swap #2 with split-batch escalation)
- S2921 batch 4: 1 tool ✓ (self_awareness mutation-template pilot; §5a 4-tier blast-radius amendment shipped alongside)

**Slice 5 — `tool_dispatcher` (14 tools):** queued.

**Substrate arcs CLOSED:** S2900-S2904 (Row 161 pace substrate) + S2909 (harness classifier + bridge preflight) + S2911 (reasoning_engine schema↔handler drift-fix). **S2921 §5a 4-tier taxonomy amendment** shipped as doc-only sweep substrate — not a formal arc close (didn't have an opening scoping doc), but the pattern is now in-tree and lint-compliant.

**Total remaining tools to close:** ~35. Post-S2921 pace: 1 tool + 1 template amendment this session with full mutation-verify + ORM cross-check. Slice 4 CLOSE at ~2-3 more sessions (batch 5 + batch 6 covering the 4 mutation-capable tools + 1 pure-READ). Cockpit's ultimate tier (`spreading` vs `cascading`) determines whether it can join batch 5 or needs its own dedicated ship.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged from S2907 close — see prior 00-START-NEXT-SESSION.md snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2921 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2921: zero A4 spend — pure sweep-batch engineering (1 pilot tool + 1 template amendment + close cascade).** A1 shipping spend was 1 PR + close cascade.
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions this session.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2921)

See:
- **S2921 handoff (current):** `docs/handoffs/SESSION_2921_SLICE_4_BATCH_4_SELF_AWARENESS_PILOT.md`
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
- **S2921 per-tool validation doc (this session's 1):** `docs/research/tools/validation/self_awareness_tool_validation.md`
- **S2920 per-tool validation docs (batch 3):** `docs/research/tools/validation/{mobile,calendar,conceptforge}_tool_validation.md`
- **S2919 per-tool validation docs (batch 2):** `docs/research/tools/validation/{discord,distribution,ats,narrative}_tool_validation.md`
- **S2918 per-tool validation docs (batch 1):** `docs/research/tools/validation/{analytics,audit,campaign,experiment}_tool_validation.md`
- **Playbook v0.9.0 ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-22_PLAYBOOK_V0_9_0.md`
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (per-tool validation docs; 81 non-substrate post-S2921)
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (S2919 narrative_tool dev-env drift entry still pending triage).

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
