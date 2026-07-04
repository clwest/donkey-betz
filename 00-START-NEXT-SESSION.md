# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 1800 IN-PROGRESS; NEXT = S1802 P2 CAT B FEEDBACKPROCESSOR + HUMANFEEDBACKRECORD AUDIT

The local wrapper at `tools/pa_local.sh:137` points at Group 1800 arc pin. **Active arc pin state after S1801 close:**

- **Active Group 1800 arc pin: `pa-ae5931ea706b4537`** (retained per playbook §16 through Group 1800 close at S1899). `tools/pa_local.sh:137` unchanged.
- **Retired at S1801 close:** SIGN isolation pin `pa-43b5b8154c8e42d7` (minted via `session_tool.create_fresh` at S1801 open with title "Session 1801 — Group 1800 Cat A HumanAttentionItem core — SIGN isolation"; unrouted per `tools/pa_local.sh` wrapper default at line 156 — SIGN cycle 1 landed on arc pin instead; retire owed at S1801 close per playbook §16 to keep pin ledger tidy).
- **Retired at S1799 close:** Group 1700 arc pin `pa-e7fbacc996b34b44` (Sessions 1700-1706 + S1799 Observability arc; 8-doc arc; retired via `session_tool.retire` at S1799 close per playbook §16).
- **Retired earlier at prior arc closes:** See `tools/pa_local.sh` comment block lines 26-140 for full ledger.

## READ THIS THIRD — S1801 CAT A CHILD AUDIT LANDED; NEXT = S1802 P2 CAT B FEEDBACKPROCESSOR + HUMANFEEDBACKRECORD AUDIT (SECOND CHILD UNDER GROUP 1800)

Session 1801 shipped the **Group 1800 Cat A HumanAttentionItem Core child audit** at `docs/research/domains/human_attention/1801_human_attention_cat_a_human_attention_item_core_audit.md` (`status: active`, `category: child_audit`, `session: 1801`, `child_slot: P1`, `domain_slug: human_attention`, `research_group: 1800`, `authority: child-audit for Category A per parent §5 D78 sequence + FIRST child under Group 1800`; ~1800 lines post-SIGN folds; playbook §11.2 20-section template SIXTH application overall + FIRST under Group 1800).

**Rigby SIGN cycle 1 SIGN-with-edits at High confidence 2026-07-03** on arc pin `pa-ae5931ea706b4537`. **F1/D5/F5 folds landed pre-commit** (F1 §20.8 appendix enumeration 28 production direct-create sites + D5 severity MED→HIGH promotion record_verification learning-loop decoupling + F5 two-triggers-met + parent-doc-update-owed rephrasing); **F3 no-change confirmed**. **D48 25th arm HOLDING CLEAN; 20th consecutive-fully-clean-arms sub-pattern CONFIRMED** per single-batch 4-question criterion (S1799 §10.2 MC-2 CODIFICATION-READY promotion path advances toward CODIFICATION-CONFIRMED).

### 8 load-bearing findings F1-F8 (S1801 §1)

- **F1** minor drift E1 25 vs grep 28 production direct-creates; §20.8 appendix enumeration landed via SIGN Q1 fold.
- **F2** minor drift parent §5 says :36-728 but file 732 lines; 4-line drift owed to xx99.
- **F3** minor drift qualification (mark_viewed called from view layer views_human_interface.py:100 NOT from services; §1 kept succinct per Rigby ratification).
- **F4** medium structural two-layer lifecycle debt (5 overlap + 3 gaps + 6 dedup candidates).
- **F5** medium correlation-primitive HYPOTHESIS SECOND application (HAI_item_id verified cross-system across 8-10 domains; MC-3 two-triggers threshold MET; parent §5 flip landed at S1801 close; CODIFICATION-READY promotion path eligible pending S1802 durability check).
- **F6** medium retention posture SAVED-FOREVER divergent from LLMCallEvent 30-day baseline.
- **F7** medium ownership gap 3 unowned state transitions.
- **F8** LOW cross-domain 4/5 S1274 baseline still MISSING at HEAD.

### 9 known technical debt D1-D9

D1 MED item.save no update_fields race @ human_attention_lifecycle.py:322 | D2 MED zero-preference-respect across 43 producers | D3 LOW-MED auto-approve bypasses blocked_sources/trusted_agents | D4 LOW auto-dismiss asymmetric no HumanFeedbackRecord | **D5 HIGH** record_verification emits no signal/event/HAI_item_id log (SIGN Q3 promotion MED→HIGH) | D6 LOW-MED deferred_until never auto-re-opened | D7 MED retention SAVED-FOREVER | D8 MED bulk decide bypasses record_decision | D9 LOW 6 producer sites legacy field names.

### R1-R10 recommended future research

R1 HAI retention posture ADR paired w/ LLMCallEvent | R2 preference-aware producer factory | R3 auto-approve blocked_sources validation | R4 two-layer debt resolution (D80 axis input) | R5 S746 verification-trigger auto-scheduler (Cat E scope) | R6 deferred-until auto-reopen | R7 bulk decide upgrade | R8 legacy field migration | R9 F5 HumanPreference fix (Cat D scope) | R10 cross-domain HAI-consumer wiring (cross-arc scope).

**Session close artifacts committed at S1801 close:**

```
docs/research/domains/human_attention/1801_human_attention_cat_a_human_attention_item_core_audit.md   [new; ~1800 lines post-SIGN folds; child audit SIXTH application overall + FIRST under Group 1800]
docs/research/domains/human_attention/1800_human_attention_domain_scoping.md                          [modified — §2.6 F5 HAI_item_id HYPOTHESIS → VERIFIED-AT-CHILD]
docs/research/ARCHITECTURE_INDEX.md                                                                   [modified — v51 → v52 with §1.55 S1801 registration + §8 timeline S1801 row + line-6 v52 preamble]
docs/research/OPEN_ARCS.md                                                                            [modified — Group 1800 In-progress row current-child S1800→S1801; row remains In-progress]
docs/handoffs/SESSION_1801_HUMAN_ATTENTION_CAT_A_HAI_CORE_AUDIT.md                                    [new — S1801 handoff]
00-START-NEXT-SESSION.md                                                                              [modified — this file; S1801 close; next-session priority = S1802 P2 Cat B]
```

Handoff: `docs/handoffs/SESSION_1801_HUMAN_ATTENTION_CAT_A_HAI_CORE_AUDIT.md`.

### NEXT-SESSION MISSION — S1802 P2 CAT B FEEDBACKPROCESSOR + HUMANFEEDBACKRECORD CHILD AUDIT

Per D78 P2 slot + parent §5 sequence: **S1802 Cat B FeedbackProcessor + HumanFeedbackRecord child audit** — second child under Group 1800. Applies playbook §11.2 20-section child template + §13 6-parallel-Explore + §14 verifier-loop REQUIRED (CODIFICATION-READY per S1799 §10.2 MC-1) pre-Explore + post-Explore + §15 Rigby SIGN cycle 1 (D48 26th arm; 21st consecutive-fully-clean-arms sub-pattern anticipated).

**Cat B scope per parent §3.B:**
- FeedbackProcessor semantics at `core/models_feedback_processing.py:122-180, 216-330` — `process_human_feedback(attention_item_id, decision, ...)` classification logic + positive/negative dispatchers + `_reinforce_positive` + `_learn_from_negative` → `AgentLearning` + `LearningInsight` writes.
- `HumanFeedbackRecord` model definition @ `core/models_human_interface.py:230-265` full semantics (Cat A physical location; Cat B semantic ownership).
- `@receiver(post_save, sender='core.HumanFeedbackRecord')` @ `models_feedback_processing.py:372` signal wire from HAI decision → FeedbackProcessor.
- **F5 correlation-primitive `feedback_record_id` HYPOTHESIS SECOND child verification** — verify at HEAD (parent §5 primitive row #2).
- Interaction with Cat A auto-approve (HumanAttentionLifecycleService `auto_approve_item` @ `:325-334` creates HumanFeedbackRecord → post_save signal fires → FeedbackProcessor consumed).
- Interaction with Cat A manual decision (`HumanInterfaceService.record_decision` @ `:325-337` also creates HumanFeedbackRecord).
- Cross-cat write patterns: is FeedbackProcessor solely Cat B's owner, or does anything write positive/negative feedback bypassing FeedbackProcessor?
- Missing consumption cases: what happens when HumanFeedbackRecord.`fed_to_ml=False` remains stale forever? Retention posture?
- `_feed_to_ml()` invocation surface (Cat A → Cat B/C boundary).

**S1801 F5 durability check anticipation for MC-3 promotion:** if S1802 verifies `feedback_record_id` as a cross-system primitive with cross-domain read/write coverage similar to F5 F1's HAI_item_id evidence — MC-3 promotes to CODIFICATION-READY. If NOT (e.g., feedback_record_id is domain-internal only), MC-3 remains CANDIDATE pending further child evidence.

**Session flow at next-session open:**

1. `context-kit orient` (session-open protocol per memory rule).
2. Check if S1801 artifact set + PR #2852 cascade refresh merged to `main`.
3. If not yet merged: Chris merge + PR merge.
4. Run post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (may be batched into S1802 close PR per Chris preference).
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-ae5931ea706b4537` (D48 26th arm start).
6. Mint fresh SIGN isolation pin for S1802 via Rigby `session_tool.create_fresh` (title: "Session 1802 — Group 1800 Cat B FeedbackProcessor + HumanFeedbackRecord — SIGN isolation") — OR skip fresh pin per `tools/pa_local.sh` wrapper default routing precedent from S1801.
7. Fire 6-parallel-Explore sub-agent sweep per playbook §13 on FeedbackProcessor + HumanFeedbackRecord + post_save signal wire + AgentLearning writes + LearningInsight writes + _feed_to_ml boundary.
8. Apply pre-Explore + post-Explore verifier-loop discipline per playbook §14 REQUIRED.
9. Draft S1802 Cat B audit doc per playbook §11.2 20-section child template.
10. Route Rigby SIGN cycle 1 (single-batch 4-question pattern; D48 26th arm; 21st consecutive-fully-clean-arms sub-pattern anticipated).
11. Land F1-Fn folds pre-commit.
12. Retire SIGN isolation pin at S1802 close per playbook §16 (if minted).
13. Update ARCHITECTURE_INDEX v52 → v53 with §1.56 S1802 registration + §8 timeline S1802 row + line-6 v53 preamble.
14. Update OPEN_ARCS Group 1800 In-progress row: current-child updated S1801 → S1802.
15. Update parent scoping doc §2.6 F5 `feedback_record_id` HYPOTHESIS → VERIFIED-AT-CHILD IF verified.
16. Write S1802 handoff + overwrite this `00-START-NEXT-SESSION.md` to point at S1803 P3 Cat C next-session priority.

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule. All 9 D-slots + 10 R-slots from S1801 remain post-arc T-slot items.

### Post-arc queued items (Chris-gated; inherited from S1801 + prior arcs)

- **From S1801 (this arc close):** R1 HAI retention posture ADR + R2 preference-aware producer factory + R3 auto-approve blocked_sources validation + R4 two-layer debt resolution (D80 axis input) + R5 S746 verification-trigger auto-scheduler + R6 deferred-until auto-reopen + R7 bulk decide upgrade + R8 legacy field migration + R9 F5 HumanPreference fix + R10 cross-domain HAI-consumer wiring.
- **From Group 1700 xx99 §8.1 T0/Gate** — R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.OBSERVABILITY.D74-SPINE-POSTURE.
- **From Group 1700 xx99 §8.2 T1 CRITICAL/HIGH** (9 items).
- **From Group 1700 xx99 §8.3 T2/T3** (38 items).
- **From Group 1600 xx99 §8.1 T0/Gate** — R.CONTENT.XX99-ADR-BUNDLE.
- **From Group 1500 (S1599)** — R.SPORTS.POSTURE + R.DBAO.CODENAME.
- **From Group 1400 (S1499)** — T1-T10.
- **From Group 1300 (S1399)** — 21 follow-on items.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600); inherited.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — owed to Group 1700 xx99 anchor-update PR (unresolved).

**FIRST THING next session open:**

1. `context-kit orient`
2. Check if S1801 artifact set + PR #2852 cascade refresh are on `main`
3. Chris merge + PR merge if not
4. Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into S1802 close PR)
5. Verify `service_context: local` on arc pin `pa-ae5931ea706b4537` (D48 26th arm start)
6. Optionally mint fresh SIGN isolation pin for S1802 via Rigby `session_tool.create_fresh` (or route SIGN via arc pin per S1801 precedent)
7. Execute S1802 P2 Cat B FeedbackProcessor + HumanFeedbackRecord child audit per playbook §11.2 20-section template + §13 6-parallel-Explore + §14 verifier-loop REQUIRED + §15 SIGN cycle 1
8. Land Rigby SIGN folds pre-commit + retire SIGN pin at S1802 close per playbook §16

---

## PA / Rigby context

- **Arc pin at session start:** `pa-ae5931ea706b4537` (Group 1800 arc pin; in service through Group 1800 close at S1899). `tools/pa_local.sh:137` points at active arc pin — no rotation needed until S1899 close.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 156).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 25-arm HOLDING CLEAN at S1801 close):** 25 arms; 20-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN CONFIRMED at S1801 close per single-batch-4-question criterion. D48 26th arm start at S1802 open; 21st consecutive-fully-clean-arms sub-pattern anticipated at S1802 P2 Cat B SIGN.
- **SIGN routing via arc pin precedent from S1801:** `tools/pa_local.sh` wrapper defaults to routing through arc pin. Fresh isolation pin minting works but routing requires explicit `--conversation` override in the pa_chat.py call. S1801 tested arc-pin routing successfully — no worker instability observed.

## Repo state at next-session open

- **Branch state (2026-07-03 post-S1801):** `main` at HEAD; S1801 branch `research/session-1801-human-attention-item-core-audit` pending Chris merge; PR #2852 `docs/session-1800-cascade-refresh` pending Chris merge.
- **Head-commit ledger (2026-07-03 activity, oldest → newest):**
  - `47ab77f1` — PR #2850 S1799 Group 1700 Observability xx99 canonical summary + arc-close
  - `eef2280f` — PR #2851 S1800 parent scoping + arc-open discipline
  - `db53b4b1` (branch `docs/session-1800-cascade-refresh`) — PR #2852 docs cascade refresh
  - (S1801 commit — this session) — S1801 Cat A child audit + parent §2.6 F5 flip + INDEX + OPEN_ARCS + handoff + start-here
- **Handoff continuity:** S1801 handoff at `docs/handoffs/SESSION_1801_HUMAN_ATTENTION_CAT_A_HAI_CORE_AUDIT.md`. Prior: SESSION_1800 (arc-open) / SESSION_1799 (Observability xx99) / SESSION_1706 → SESSION_1700 (Observability arc).
- **ARCHITECTURE_INDEX version:** v52 (bumped this session with §1.55 S1801 registration + §8 timeline S1801 row + line-6 v52 preamble). Next bump at S1802 close (v52 → v53 with §1.56 S1802 registration).
- **OPEN_ARCS state:** Group 1800 row IN-PROGRESS; current-child field updated S1800 → S1801. Groups 1700/1600/1500/1400/1300 Closed.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Check if S1801 artifact set + PR #2852 cascade refresh are on `main`
- [ ] Chris merge + PR merge if not
- [ ] Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into S1802 close)
- [ ] Verify `service_context: local` on arc pin `pa-ae5931ea706b4537` (D48 26th arm start)
- [ ] Mint fresh SIGN isolation pin for S1802 via Rigby `session_tool.create_fresh` OR skip per S1801 arc-pin routing precedent
- [ ] Execute S1802 P2 Cat B FeedbackProcessor + HumanFeedbackRecord child audit per playbook §11.2 + §13 + §14 REQUIRED + §15 SIGN cycle 1
- [ ] Land Rigby SIGN folds pre-commit + retire SIGN pin at S1802 close per playbook §16
- [ ] Bump ARCHITECTURE_INDEX v52 → v53 with §1.56 S1802 registration
- [ ] Update OPEN_ARCS Group 1800 In-progress row: current-child updated S1801 → S1802
- [ ] Update parent scoping doc §2.6 F5 `feedback_record_id` HYPOTHESIS → VERIFIED-AT-CHILD IF verified

## Reference — where to look

- **S1801 child audit doc:** `docs/research/domains/human_attention/1801_human_attention_cat_a_human_attention_item_core_audit.md` — playbook §11.2 20-section template SIXTH application overall + FIRST under Group 1800; 8 findings F1-F8 + 9 debt D1-D9 (D5 HIGH from SIGN promotion) + 10 R-slots + §20.8 appendix 28 production direct-create sites enumeration + §20.6 post-SIGN fold record.
- **S1800 parent scoping doc:** `docs/research/domains/human_attention/1800_human_attention_domain_scoping.md` — playbook §11.1 parent template FIFTH application; D75-D80 Chris-locked; §2.6 F5 HAI_item_id → VERIFIED-AT-CHILD at S1801 close (this session); other 4 primitives remain HYPOTHESIS awaiting Cat B/C/D/E children.
- **S1799 xx99 canonical summary (fifth arc-close):** `docs/research/domains/observability/1799_observability_canonical_summary.md`.
- **Prior xx99 canonical summaries:** `1699_content_canonical_summary.md` + `1599_sports_canonical_summary.md` + `1499_revenue_canonical_summary.md` + `1399_memory_canonical_summary.md`.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`.
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`.
- **ARCHITECTURE_INDEX v52:** `docs/research/ARCHITECTURE_INDEX.md` — S1801 §1.55 + line-6 v52 preamble + §8 timeline S1801 row.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1800 In-progress row (current-child S1801).
- **S1273 baseline:** `docs/research/platform_architecture_inventory.md` §3.16 HumanAttention row + §4.7 canonical round-trip narrative + §2.5 "only round-trip w/ learning" claim.
- **S1274 baseline:** `docs/research/platform/cross_domain_integration_audit.md` §3.3 CRITICAL Failure Cluster → HAI + §3.8 MEDIUM Signal Pattern → HAI + 5+ cross-domain HAI-consumer integration MISSING catalog.
- **S1269 baseline:** `docs/research/governance_authority_evolution.md` §1.4 F5 HumanPreference topic_weights/source_weights never-saved bug (VERIFIED HERE at S1801 §4.3).
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.
- **Cat B canonical entry points for S1802 consumption:** FeedbackProcessor at `core/models_feedback_processing.py:122-180, 216-330`; HumanFeedbackRecord at `core/models_human_interface.py:230-265`; `@receiver(post_save, sender='core.HumanFeedbackRecord')` at `core/models_feedback_processing.py:372`; auto-approve HumanFeedbackRecord.create writer at `core/services/human_attention_lifecycle.py:325-334`; manual decision HumanFeedbackRecord.create writer at `core/services/human_interface_service.py:325-337`.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1801 = Cat A first child; S1802 P2 Cat B next child.
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff.
- Docs cascade — cascade PR #2852 pending Chris merge; post-S1801 cascade will be batched into S1802 close PR OR standalone follow-up per Chris preference.
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — inherited from Group 1700 xx99 anchor-update PR (unresolved).
- Group 1400/1500/1600/1700 post-arc §7 anchor-updates still pending (inherited).
- Group 1400/1500/1600/1700 T1 CRITICAL remediation queues still pending; Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE + Group 1700 paired T0/Gate (RETENTION-UNIFIED-ADR + D74-SPINE-POSTURE) still gating.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600).
- **5 doc PRs still owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **D48 25th arm HOLDING CLEAN at S1801 close** — 20th consecutive-fully-clean-arms sub-pattern CONFIRMED per single-batch-4-question criterion; 21st anticipated at S1802 P2 Cat B SIGN.
- **Playbook v3 §11.2 template SIXTH application at S1801** — child template durable at six-consecutive-application (S1601 + S1701 + S1801 first-under-arc + S1602 + S1702 second-under-arc + S1701/S1801 additional).
- **Playbook v3 §14 verifier-loop REQUIRED promotion (S1799 §10.2 MC-1 CODIFICATION-READY):** enforced at S1801 pre-Explore + post-Explore.
- **F5 correlation-primitive HAI_item_id HYPOTHESIS box SECOND application VERIFIED at S1801 close** — MC-3 two-triggers threshold MET; CODIFICATION-READY promotion path pending S1802 durability check.
- **Arc pin `pa-ae5931ea706b4537` in service** through Group 1800 close at S1899; retire owed at S1899 close per playbook §16.
- **SIGN isolation pin `pa-43b5b8154c8e42d7`** retire owed at S1801 close (unrouted this cycle; pin ledger tidy discipline).
