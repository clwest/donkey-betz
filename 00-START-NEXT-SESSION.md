# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 1800 IN-PROGRESS; NEXT = S1804 P4 CAT D HUMAN-PREFERENCE + F5 NEVER-SAVED BUG + READER INVENTORY

The local wrapper at `tools/pa_local.sh:137` points at Group 1800 arc pin. **Active arc pin state after S1803 close:**

- **Active Group 1800 arc pin: `pa-ae5931ea706b4537`** (retained per playbook §16 through Group 1800 close at S1899). `tools/pa_local.sh:137` unchanged.
- **No SIGN isolation pin minted at S1803 open** (S1801+S1802 arc-pin routing precedent applied — durable-by-third-application; established as arc-standard behavior). `tools/pa_local.sh` wrapper default routes through arc pin cleanly.
- **Retired at S1801 close:** SIGN isolation pin `pa-43b5b8154c8e42d7` (minted via `session_tool.create_fresh` at S1801 open with title "Session 1801 — Group 1800 Cat A HumanAttentionItem core — SIGN isolation"; unrouted per `tools/pa_local.sh` wrapper default; SIGN cycle 1 landed on arc pin instead; retired at S1801 close per playbook §16 to keep pin ledger tidy).
- **Retired at S1799 close:** Group 1700 arc pin `pa-e7fbacc996b34b44` (Sessions 1700-1706 + S1799 Observability arc; 8-doc arc; retired via `session_tool.retire` at S1799 close per playbook §16).
- **Retired earlier at prior arc closes:** See `tools/pa_local.sh` comment block lines 26-140 for full ledger.

## READ THIS THIRD — S1803 CAT C CHILD AUDIT LANDED; NEXT = S1804 P4 CAT D HUMAN-PREFERENCE + F5 NEVER-SAVED BUG + READER INVENTORY (FOURTH CHILD UNDER GROUP 1800)

Session 1803 shipped the **Group 1800 Cat C Learning bridges + 10+ subclasses + duplicate-service inventory child audit** at `docs/research/domains/human_attention/1803_human_attention_cat_c_learning_bridges_child_audit.md` (`status: active`, `category: child_audit`, `session: 1803`, `child_slot: P3`, `domain_slug: human_attention`, `research_group: 1800`, `authority: child-audit for Category C per parent §5 D78 sequence + THIRD child under Group 1800`; ~1050 lines post-SIGN folds; playbook §11.2 20-section template EIGHTH application overall + THIRD under Group 1800).

**Rigby SIGN cycle 1 SIGN-with-edits at High confidence 0.84 2026-07-03** on arc pin `pa-ae5931ea706b4537`. **F2 language-softening + F4 explicit collision-mechanism + blast-radius per pair + F5 serialization-boundary caveat + F7 LearningPatternEngine catalog inclusion + F8 drift framing + Q4 compound-impact framing + R0 elevation folds landed pre-commit.** **D48 27th arm turn 1 CLEAN; 22nd consecutive-fully-clean-arms sub-pattern CONFIRMED** per single-batch 4-question criterion (S1799 §10.2 MC-2 CODIFICATION-READY promotion path advances toward CODIFICATION-CONFIRMED).

### 10 load-bearing findings F1-F10 (S1803 §14)

- **F1 (LOW)** parent §3.C 9-subclass claim CLARIFICATION (9 classes across 8 files — advisor_feedback_bridge.py hosts BOTH AdvisorFeedbackLearningLoop @ :50 AND AutoConsultationLearningLoop @ :250).
- **F2 (MED)** RedditLearningBridge + BlueskyLearningBridge do NOT inherit `LearningBridge` ABC — LABEL DRIFT with search-strategy caveat.
- **F3 (HIGH)** parent §3.C Q4 AgentLearningSession MULTI-DRIFT (migration is `0368_...` not `0002`; S1244 deleted `core.*` only; `ai_intelligence.AgentLearningSession` @ ai_core/intelligence/models.py:211 STILL ALIVE with writer @ persistent_learning_engine.py:65-77).
- **F4 (HIGH)** duplicate FILE name-collision — `BoardroomLearningService` x2 + `UnifiedLearningPipeline` x2 both alive with 11 total production consumers; explicit Python import-path collision mechanism + blast-radius per pair.
- **F5 (MED)** `learning_event_id` HYPOTHESIS REMAINS — **cross-system-primitive DISPROVEN** (4 hits across 2 files all in `ai_core/intelligence/`). Matches S1802 feedback_record_id FAIL pattern; SECOND CONSECUTIVE negative outcome. **MC-3 CODIFICATION-READY promotion path DOES NOT advance.** Meta-methodology finding candidate for xx99 §10.
- **F6 (MED)** writer-plane split not surfaced — Cat B FeedbackProcessor writes AgentLearning (2 sites); Cat C bridges write UserAgentLearning (22 sites); parent §3.C conflates as fungible.
- **F7 (HIGH)** parent §3.C "4+ duplicate service candidates" UNDER-COUNT — 16+ learning-service classes at HEAD, including SIGN-surfaced LearningPatternEngine.
- **F8 (MED)** LearningOrchestrator missing AutoConsultationLearningLoop from `_initialize_bridges()` — plausible drift framing.
- **F9 (LOW)** parent §3.C AgentExecutionLearningLoop cross-arc phrasing imprecise — bridge OUTPUT → Group 1300 only; Group 1700 shares source signal via separate Rigby receiver.
- **F10 (SPECULATIVE)** 4 cross-domain direct UserAgentLearning writers OUTSIDE bridge abstraction.

### 10 known technical debt D1-D10

D1 HIGH duplicate-file name-collision surface (F4 companion) | D2 MED zero `transaction.atomic()` on 25+ multi-model bridge writes | D3 MED signal handler silent Exception swallow (parallel-to-S1801-D5 + S1802-D3) | D4 MED missing observability signal on bridge dispatch (parallel-to-S1801-D5 + S1802-D4) | D5 MED best-effort silent-skip on FK lookups (parallel-to-S1802-D5) | D6 MED AutoConsultationLearningLoop system-user race condition | D7 MED retention SAVED-FOREVER across 8 target models | D8 LOW-MED missing `source_kind` provenance field | D9 LOW missing composite indexes | D10 LOW-SPEC dead lazy-import fallback in RedditLearningBridge.

### R0-R11 recommended future research (post-SIGN Chris-gate ordering: R0 → R1 → R2 → balance)

R0 (POST-ARC HIGH — Rigby SIGN Q4 fold-added top priority) unified learning-plane contract ADR | R1 duplicate-file consolidation ADR | R2 ai_intelligence.AgentLearningSession posture ADR | R3 LearningOrchestrator registry completeness | R4 F5 durability meta-methodology posture | R5 bridge dispatch observability signal | R6 non-bridge UserAgentLearning writers routing | R7 retention posture ADR paired with S1801 R1 + S1802 R1 | R8 `source_kind` schema field joint Group 1300 + 1800 ADR | R9 transaction atomicity | R10 Reddit/Bluesky ABC contract | R11 CODEOWNERS entry.

**Session close artifacts committed at S1803 close:**

```
docs/research/domains/human_attention/1803_human_attention_cat_c_learning_bridges_child_audit.md   [new; ~1050 lines post-SIGN folds; child audit EIGHTH application overall + THIRD under Group 1800]
docs/research/domains/human_attention/1800_human_attention_domain_scoping.md                         [modified — §2.6 F5 row #3 flipped to VERIFIED-PARTIAL-AT-CHILD with cross-system-primitive DISPROVEN]
docs/research/ARCHITECTURE_INDEX.md                                                                  [modified — v53 → v54 with §1.57 S1803 registration + §8 timeline S1803 row + line-6 v54 preamble; v53 preamble preserved]
docs/research/OPEN_ARCS.md                                                                           [modified — Group 1800 In-progress row current-child S1802→S1803 + next-expected S1804]
docs/handoffs/SESSION_1803_HUMAN_ATTENTION_CAT_C_LEARNING_BRIDGES_AUDIT.md                          [new — S1803 handoff]
00-START-NEXT-SESSION.md                                                                             [modified — this file; S1803 close; next-session priority = S1804 P4 Cat D]
```

Handoff: `docs/handoffs/SESSION_1803_HUMAN_ATTENTION_CAT_C_LEARNING_BRIDGES_AUDIT.md`.

### NEXT-SESSION MISSION — S1804 P4 CAT D HUMAN-PREFERENCE + F5 NEVER-SAVED BUG + READER INVENTORY CHILD AUDIT

Per D78 P4 slot + parent §5 sequence: **S1804 Cat D HumanPreference + F5 topic_weights/source_weights never-saved bug + reader inventory child audit** — fourth child under Group 1800. Applies playbook §11.2 20-section child template + §13 6-parallel-Explore + §14 verifier-loop REQUIRED (CODIFICATION-READY per S1799 §10.2 MC-1) pre-Explore + post-Explore + §15 Rigby SIGN cycle 1 (D48 28th arm; 23rd consecutive-fully-clean-arms sub-pattern anticipated).

**Cat D scope per parent §3.D:**
- HumanPreference model @ `core/models_human_interface.py:268-358`.
- `HumanPreference.update_learned_stats()` — F5 root cause: sets `topic_weights` / `source_weights` locally but never `.save()`s (per S1269 governance research §1.4).
- Reader inventory — grep for `HumanPreference.objects.get` or `.topic_weights` or `.source_weights` references at HEAD.
- **F5 correlation-primitive `user_pref_id` HYPOTHESIS FOURTH child verification** — verify at HEAD (parent §5 primitive row #4).
- Governance intersection — S1269 governance-plane implications at HEAD.
- Cross-arc handoffs to Group 1300 Memory + Group 1600 Content (personalization) + Group 1900 Event Architecture.

**Load-bearing question at Cat D:** does F5 silently miscompute personalization (readers exist) OR is F5 silent no-op (governance-visible only, zero readers)? Answer determines severity: HIGH if readers exist; MED if silently no-op.

**S1803 F5 durability check DISPROVED cross-system for learning_event_id (SECOND consecutive after S1802) — S1804 tests the DISCIPLINE holds THIRD consecutive time:** if S1804 verifies `user_pref_id` as a cross-system primitive with cross-domain read coverage similar to S1801 F5 HAI_item_id evidence — the primitive-box discipline continues to validate WITH a mixed pattern (1 of 4 passing). If NOT — the pattern of naming primitives that don't survive cross-system verification becomes a durable-at-three-instances meta-methodology finding for the xx99 §5 posture-decision brief + §10 retrospective.

**Session flow at next-session open:**

1. `context-kit orient` (session-open protocol per memory rule).
2. Check if S1803 artifact set + cascade refresh PR merged to `main`.
3. If not yet merged: Chris merge + PR merge.
4. Run post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (may be batched into S1804 close PR per Chris preference).
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-ae5931ea706b4537` (D48 28th arm start).
6. Skip fresh SIGN isolation pin per S1801+S1802+S1803 arc-pin routing precedent (durable-by-third-application; established as arc-standard).
7. Fire 6-parallel-Explore sub-agent sweep per playbook §13 on HumanPreference model + `update_learned_stats` writer + reader inventory + F5 reproduction + governance intersection + cross-arc handoffs to Groups 1300/1600/1900.
8. Apply pre-Explore + post-Explore verifier-loop discipline per playbook §14 REQUIRED.
9. Draft S1804 Cat D audit doc per playbook §11.2 20-section child template.
10. Route Rigby SIGN cycle 1 (single-batch 4-question pattern; D48 28th arm; 23rd consecutive-fully-clean-arms sub-pattern anticipated).
11. Land F1-Fn folds pre-commit.
12. No SIGN isolation pin retire unless minted (arc-pin routing precedent).
13. Update ARCHITECTURE_INDEX v54 → v55 with §1.58 S1804 registration + §8 timeline S1804 row + line-6 v55 preamble.
14. Update OPEN_ARCS Group 1800 In-progress row: current-child updated S1803 → S1804.
15. Update parent scoping doc §2.6 F5 `user_pref_id` HYPOTHESIS → VERIFIED-AT-CHILD IF cross-system verified, OR HYPOTHESIS REMAINS IF domain-internal.
16. Write S1804 handoff + overwrite this `00-START-NEXT-SESSION.md` to point at S1805 P5 Cat E next-session priority.

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule. All 10 D-slots + 12 R-slots (R0-R11) from S1803 remain post-arc T-slot items alongside S1802 + S1801 R-slots.

### Post-arc queued items (Chris-gated; inherited from S1803 + S1802 + S1801 + prior arcs)

- **From S1803 (this arc close):** R0-R11 with post-SIGN Chris-gate ordering R0 → R1 → R2 → balance (Rigby architecture-leverage ranking — R0 unified learning-plane contract ADR elevated as Q4 top priority).
- **From S1802:** R1-R10 with post-SIGN Chris-gate ordering R6 → R4 → R7 → R1.
- **From S1801:** R1 HAI retention posture ADR + R2 preference-aware producer factory + R3 auto-approve blocked_sources validation + R4 two-layer debt resolution + R5 S746 verification-trigger auto-scheduler + R6 deferred-until auto-reopen + R7 bulk decide upgrade + R8 legacy field migration + R9 F5 HumanPreference fix + R10 cross-domain HAI-consumer wiring.
- **From Group 1700 xx99 §8.1 T0/Gate** — R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.OBSERVABILITY.D74-SPINE-POSTURE.
- **From Group 1700 xx99 §8.2 T1 CRITICAL/HIGH** (9 items).
- **From Group 1700 xx99 §8.3 T2/T3** (38 items).
- **From Group 1600 xx99 §8.1 T0/Gate** — R.CONTENT.XX99-ADR-BUNDLE.
- **From Group 1500 (S1599)** — R.SPORTS.POSTURE + R.DBAO.CODENAME.
- **From Group 1400 (S1499)** — T1-T10.
- **From Group 1300 (S1399)** — 21 follow-on items (includes Cat H write-authority framework ADR that S1802 partially closes on the Cat B writer side + S1803 partially closes on the Cat C writer side).
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600); inherited.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — owed to Group 1700 xx99 anchor-update PR (unresolved).

**FIRST THING next session open:**

1. `context-kit orient`
2. Check if S1803 artifact set + cascade refresh PR are on `main`
3. Chris merge + PR merge if not
4. Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into S1804 close PR)
5. Verify `service_context: local` on arc pin `pa-ae5931ea706b4537` (D48 28th arm start)
6. Skip fresh SIGN isolation pin per S1801+S1802+S1803 arc-pin routing precedent (durable-by-third-application; established as arc-standard)
7. Execute S1804 P4 Cat D HumanPreference + F5 never-saved bug + reader inventory audit per playbook §11.2 20-section template + §13 6-parallel-Explore + §14 verifier-loop REQUIRED + §15 SIGN cycle 1
8. Land Rigby SIGN folds pre-commit

---

## PA / Rigby context

- **Arc pin at session start:** `pa-ae5931ea706b4537` (Group 1800 arc pin; in service through Group 1800 close at S1899). `tools/pa_local.sh:137` points at active arc pin — no rotation needed until S1899 close.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 156).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 27th arm HOLDING CLEAN at S1803 close):** 27 arms; 22-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN CONFIRMED at S1803 close per single-batch-4-question criterion. D48 28th arm start at S1804 open; 23rd consecutive-fully-clean-arms sub-pattern anticipated at S1804 P4 Cat D SIGN.
- **SIGN routing via arc pin precedent from S1801 + S1802 + S1803 (durable-by-third-application; established as arc-standard):** `tools/pa_local.sh` wrapper defaults to routing through arc pin. No fresh isolation pin minting required. All three prior child openings tested arc-pin routing successfully — no worker instability observed. **Established as arc-standard behavior**; will document explicitly at Group 1800 xx99 close as durable-by-third-application-across-three-child-arcs.

## Repo state at next-session open

- **Branch state (2026-07-03 post-S1803):** `main` at HEAD `69cf2dd1`; S1803 branch `research/session-1803-cat-c-learning-bridges-audit` pending Chris merge.
- **Head-commit ledger (2026-07-03 activity, oldest → newest):**
  - `47ab77f1` — PR #2850 S1799 Group 1700 Observability xx99 canonical summary + arc-close
  - `eef2280f` — PR #2851 S1800 parent scoping + arc-open discipline
  - `0c2288f6` — PR #2852 S1800 docs cascade refresh
  - `b66158a5` — PR #2853 S1801 Cat A HAI Core child audit
  - `9885ab01` — PR #2854 S1801 docs cascade refresh
  - `d2b58e94` — PR #2855 S1802 Cat B FeedbackProcessor + HumanFeedbackRecord child audit
  - `69cf2dd1` — PR #2856 S1802 docs cascade refresh (current main HEAD)
  - (S1803 commit — this session) — S1803 Cat C child audit + parent §2.6 F5 row #3 flip + INDEX v54 + OPEN_ARCS + handoff + start-here
- **Handoff continuity:** S1803 handoff at `docs/handoffs/SESSION_1803_HUMAN_ATTENTION_CAT_C_LEARNING_BRIDGES_AUDIT.md`. Prior: SESSION_1802 (Cat B FeedbackProcessor + HumanFeedbackRecord child audit) / SESSION_1801 (Cat A HAI Core child audit) / SESSION_1800 (arc-open parent scoping) / SESSION_1799 (Observability xx99).
- **ARCHITECTURE_INDEX version:** v54 (bumped this session with §1.57 S1803 registration + §8 timeline S1803 row + line-6 v54 preamble; v53 preamble preserved). Next bump at S1804 close (v54 → v55 with §1.58 S1804 registration).
- **OPEN_ARCS state:** Group 1800 row IN-PROGRESS; current-child field updated S1802 → S1803. Groups 1700/1600/1500/1400/1300 Closed.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Check if S1803 artifact set + cascade refresh PR are on `main`
- [ ] Chris merge + PR merge if not
- [ ] Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule (or batch into S1804 close)
- [ ] Verify `service_context: local` on arc pin `pa-ae5931ea706b4537` (D48 28th arm start)
- [ ] Skip fresh SIGN isolation pin per S1801+S1802+S1803 arc-pin routing precedent (durable-by-third-application)
- [ ] Execute S1804 P4 Cat D HumanPreference + F5 never-saved bug + reader inventory audit per playbook §11.2 + §13 + §14 REQUIRED + §15 SIGN cycle 1
- [ ] Land Rigby SIGN folds pre-commit
- [ ] Bump ARCHITECTURE_INDEX v54 → v55 with §1.58 S1804 registration
- [ ] Update OPEN_ARCS Group 1800 In-progress row: current-child updated S1803 → S1804
- [ ] Update parent scoping doc §2.6 F5 `user_pref_id` HYPOTHESIS → VERIFIED-AT-CHILD IF cross-system verified

## Reference — where to look

- **S1803 child audit doc:** `docs/research/domains/human_attention/1803_human_attention_cat_c_learning_bridges_child_audit.md` — playbook §11.2 20-section template EIGHTH application overall + THIRD under Group 1800; 10 findings F1-F10 + 10 debt D1-D10 (D1 HIGH; F3+F4+F7 HIGH) + R0-R11 with post-SIGN Chris-gate ordering R0→R1→R2→balance + §20.6 SIGN fold record + §20.7 F5 methodology interpretation note extended + §20.8 non-bridge UserAgentLearning writer catalog.
- **S1802 child audit doc:** `docs/research/domains/human_attention/1802_human_attention_cat_b_feedback_processor_child_audit.md` — playbook §11.2 20-section template SEVENTH application overall + SECOND under Group 1800.
- **S1801 child audit doc:** `docs/research/domains/human_attention/1801_human_attention_cat_a_human_attention_item_core_audit.md` — playbook §11.2 20-section template SIXTH application overall + FIRST under Group 1800.
- **S1800 parent scoping doc:** `docs/research/domains/human_attention/1800_human_attention_domain_scoping.md` — playbook §11.1 parent template FIFTH application; D75-D80 Chris-locked; §2.6 F5 row #1 HAI_item_id VERIFIED-AT-CHILD (S1801) + row #2 feedback_record_id VERIFIED-PARTIAL-AT-CHILD cross-system-primitive DISPROVEN (S1802) + row #3 learning_event_id VERIFIED-PARTIAL-AT-CHILD cross-system-primitive DISPROVEN (S1803 this session); rows #4-#5 remain HYPOTHESIS awaiting Cat D/E children.
- **S1799 xx99 canonical summary (fifth arc-close):** `docs/research/domains/observability/1799_observability_canonical_summary.md`.
- **Prior xx99 canonical summaries:** `1699_content_canonical_summary.md` + `1599_sports_canonical_summary.md` + `1499_revenue_canonical_summary.md` + `1399_memory_canonical_summary.md`.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`.
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`.
- **ARCHITECTURE_INDEX v54:** `docs/research/ARCHITECTURE_INDEX.md` — S1803 §1.57 + line-6 v54 preamble + §8 timeline S1803 row.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1800 In-progress row (current-child S1803).
- **S1273 baseline:** `docs/research/platform_architecture_inventory.md` §3.16 HumanAttention row + §4.7 canonical round-trip narrative.
- **S1274 baseline:** `docs/research/platform/cross_domain_integration_audit.md` §3.3 CRITICAL Failure Cluster → HAI + §3.8 MEDIUM Signal Pattern → HAI.
- **S1399 Memory arc close:** `docs/research/domains/memory/1399_memory_canonical_summary.md` §3 delegated "Cat H ↔ Cat B write-authority + TTL policy" ADR to post-S1399. **S1803 partially closes the Cat C writer side of this delegation** via §16 boundary-violation catalog + Cat C's autonomous writer plane into Group 1300 UserAgentLearning.
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.
- **Cat D canonical entry points for S1804 consumption:** HumanPreference model @ `core/models_human_interface.py:268-358` + `update_learned_stats()` writer + reader inventory via `HumanPreference.objects.get|.topic_weights|.source_weights` grep + F5 governance intersection.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1803 = Cat C third child; S1804 P4 Cat D next child.
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff.
- Docs cascade — cascade PR pending Chris merge; post-S1803 cascade will be batched into S1804 close PR OR standalone follow-up per Chris preference.
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — inherited from Group 1700 xx99 anchor-update PR (unresolved).
- Group 1400/1500/1600/1700 post-arc §7 anchor-updates still pending (inherited).
- Group 1400/1500/1600/1700 T1 CRITICAL remediation queues still pending; Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE + Group 1700 paired T0/Gate (RETENTION-UNIFIED-ADR + D74-SPINE-POSTURE) still gating.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600).
- **5 doc PRs still owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **D48 27th arm HOLDING CLEAN at S1803 close** — 22nd consecutive-fully-clean-arms sub-pattern CONFIRMED per single-batch-4-question criterion; 23rd anticipated at S1804 P4 Cat D SIGN.
- **Playbook v3 §11.2 template EIGHTH application at S1803** — child template durable at eight-consecutive-applications (S1601 + S1701 + S1801 first-under-arc + S1602 + S1702 second-under-arc + S1801/S1802/S1803 additional under Group 1800).
- **Playbook v3 §14 verifier-loop REQUIRED promotion (S1799 §10.2 MC-1 CODIFICATION-READY):** enforced at S1803 pre-Explore + post-Explore; also drove Rigby SIGN cycle 1 fold #2 discovery of MISSED LearningPatternEngine service.
- **F5 correlation-primitive `learning_event_id` HYPOTHESIS FOURTH application DISPROVED-CROSS-SYSTEM at S1803 close** — HYPOTHESIS REMAINS at parent §2.6 row #3 with cross-system-primitive DISPROVEN; MC-3 CODIFICATION-READY promotion path DOES NOT advance at S1803 close (SECOND CONSECUTIVE negative outcome); primitive-box DISCIPLINE itself remains CODIFICATION-CANDIDATE (meta-methodology finding candidate for xx99 §10: pattern of naming primitives that don't survive cross-system verification is a research signal in its own right).
- **Arc pin `pa-ae5931ea706b4537` in service** through Group 1800 close at S1899; retire owed at S1899 close per playbook §16.
- **SIGN isolation pin routing pattern (durable-by-third-application):** S1801 + S1802 + S1803 all routed SIGN via arc pin with no fresh isolation pin minted; established as arc-standard behavior; will document explicitly at Group 1800 xx99 close.
