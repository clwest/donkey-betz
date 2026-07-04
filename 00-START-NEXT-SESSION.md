# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 1800 OPEN AT S1800; NEXT = S1801 P1 CAT A HUMANATTENTIONITEM CORE AUDIT

The local wrapper at `tools/pa_local.sh:137` points at Group 1800 arc pin. **Active arc pin state after S1800 open:**

- **Active Group 1800 arc pin: `pa-ae5931ea706b4537`** (Rigby `session_tool.create_fresh` at S1800 open — title "Session 1800 — HumanAttention / Feedback / Learning research group (kickoff)"). Continues in service across Group 1800 arc (S1801-S1806 children pending + S1899 xx99 canonical summary pending). Arc pin retained per playbook §16 through Group 1800 close at S1899.
- **Retired at S1800 open:** Group 1700 arc pin `pa-e7fbacc996b34b44` (Sessions 1700-1706 + S1799 — Group 1700 Observability / Telemetry / SLOs arc; 8-doc arc; retired via `session_tool.retire` at S1799 close per playbook §16 arc-close discipline; updated_count: 31, retired: true, previously_active: true).
- **Retired earlier at prior arc closes:** See `tools/pa_local.sh` comment block lines 26-140 for full ledger of retired arc pins + SIGN isolation pins across Groups 1300-1700 arcs.

## READ THIS THIRD — S1800 ARC-OPEN PARENT SCOPING LANDED; NEXT = S1801 P1 CAT A HUMANATTENTIONITEM CORE AUDIT (FIRST CHILD UNDER GROUP 1800)

Session 1800 shipped the **Group 1800 HumanAttention / Feedback / Learning arc-open parent scoping** at `docs/research/domains/human_attention/1800_human_attention_domain_scoping.md` (`status: active`, `category: parent_scoping`, `session: 1800`, `child_slot: P0`, `domain_slug: human_attention`, `research_group: 1800`, `authority: parent-doc for Group 1800 research arc`; 904 lines; playbook §11.1 template FIFTH application after S1400 first + S1500 second + S1600 third + S1700 fourth).

**Chris D75-D80 all Chris-ratified at default lean (a) via "agree all" round 2026-07-03.** No Rigby light SIGN routed per Chris choice (parent scoping §15 stage-table default = "optional light SIGN"; Chris skipped SIGN this round). **D48 25th arm start reserved for S1801 P1 Cat A child audit SIGN.**

### Six D-verdicts Chris-ratified (D75-D80)

- **D75** — Parent shape: PARENT-WITH-CHILDREN 6-child arc + xx99 canonical summary.
- **D76** — Category count + boundary: Six categories A–F with Cat F sub-slotted F.a-F.e per S1706 SIGN F2 fold precedent.
- **D77** — Delegation boundary: Group 1800 owns HAI + Feedback + Learning-bridge WRITER contracts; Group 1300 Memory owns AgentLearning + UserAgentLearning + AgentKnowledgeSource internals; Groups 1400/1500/1600/1700 own respective source-domain business logic; Group 1900 Event Architecture owns event bus per S1274 §11.1; Employee OS owns MissionRunner correctness.
- **D78** — Child sequence: P1 Cat A → P2 Cat B → P3 Cat C → P4 Cat D → P5 Cat E → P6 Cat F → P7 S1899 xx99 sequential.
- **D79** — Posture-decision framing: xx99 produces evidence brief for D80 — NOT recommendation.
- **D80** — Load-bearing arc lens question: **"Is the human-in-the-loop attention queue (HumanAttentionItem) the canonical learning-signal aggregation surface, OR are learning bridges autonomous domain-specific consumers that bypass HAI?"** Four posture options: A Canonical Unification / B Structural Separability / C Hybrid / D Shared surface. xx99 evidence brief; Chris selects post-arc.

### Six-category taxonomy (parent §3)

- **Cat A** (S1801) — HumanAttentionItem core + producers + 8-state lifecycle + auto-escalate ladder
- **Cat B** (S1802) — Feedback processing (FeedbackProcessor + HumanFeedbackRecord + record_decision = **ONLY** round-trip w/ learning per S1274 §2.5)
- **Cat C** (S1803) — Learning bridges (10+ subclasses across 3 apps + 4+ duplicate learning-service inventory)
- **Cat D** (S1804) — HumanPreference + F5 never-saved bug per S1269 governance §1.4
- **Cat E** (S1805) — S746 verification loop + `record_verification` trigger discovery
- **Cat F** (S1806) — Adjacent / Separation Boundaries with F.a-F.e sub-slots (external Reddit/Bluesky bridges + 5+ cross-domain HAI-consumer integration gaps + PA-tool intersection + duplicate learning-service inventory + terminology boundary)

### §5 F5 correlation-primitive HYPOTHESIS box — SECOND APPLICATION

Five primitives labeled HYPOTHESIS-TO-BE-VERIFIED per S1700 parent §5 precedent (first application via Rigby SIGN cycle 1 F5 MUST-FIX fold): `HAI_item_id` (verify P1) + `feedback_record_id` (verify P2) + `learning_event_id` (verify P3) + `user_pref_id` (verify P4) + `verification_id` (verify P5).

**S1799 §10.2 MC-3 CODIFICATION-CANDIDATE promotion path:** two-triggers threshold MET at S1800 parent scoping. Promotion to CODIFICATION-READY at S1899 close if pattern holds durable across child audits.

**Session close artifacts committed at S1800 open:**

```
docs/research/domains/human_attention/1800_human_attention_domain_scoping.md   [new; 904 lines; parent scoping FIFTH application; D75-D80 Chris-ratified via "agree all" round]
docs/research/ARCHITECTURE_INDEX.md                                             [modified — v50 → v51 with §1.54 S1800 registration + §8 timeline S1800 row + line-6 v51 preamble]
docs/research/OPEN_ARCS.md                                                      [modified — Group 1800 row moved Not-started → In-progress; last_updated field bumped]
tools/pa_local.sh                                                               [modified — line 137 rotated to pa-ae5931ea706b4537; comment block updated for Group 1800 arc]
docs/handoffs/SESSION_1800_HUMAN_ATTENTION_ARC_OPEN.md                          [new — S1800 handoff]
00-START-NEXT-SESSION.md                                                        [modified — this file; S1800 arc-open; next-session priority = S1801 P1 Cat A]
```

Handoff: `docs/handoffs/SESSION_1800_HUMAN_ATTENTION_ARC_OPEN.md`.

### NEXT-SESSION MISSION — S1801 P1 CAT A HUMANATTENTIONITEM CORE CHILD AUDIT

Per D78 P1 slot + parent §5 sequence: **S1801 Cat A HumanAttentionItem core audit** — first child under Group 1800. Applies playbook §11.2 20-section child template + §13 6-parallel-Explore + §14 verifier-loop REQUIRED (per S1799 §10.2 MC-1 CODIFICATION-READY) + §15 Rigby SIGN cycle 1 (D48 25th arm start; 20th consecutive-fully-clean-arms sub-pattern anticipated).

**Cat A scope per parent §3.A:**
- HAI 8-state lifecycle producer/consumer inventory (pending/viewed/acted/deferred/ignored/expired/watching/verified)
- 20+ HAI producer sites at HEAD (grep + ORM verify)
- HumanAttentionLifecycleService auto-escalate ladder (LOW 72h → MEDIUM 48h → HIGH 24h → CRITICAL auto-dismiss 3d; 10-min beat)
- Two-layer lifecycle debt from S1273 §3.16 (HumanAttentionBridge vs HumanAttentionLifecycleService)
- 5+ cross-domain HAI-consumer integration MISSING catalog from S1274 §3.3 + §3.8 (Body Systems / Signal Engine / Revenue / Observability / Failure Cluster)
- Retention posture (does HAI have date-based retention? grep-verify)
- Load-bearing questions Q1-Q5 per parent §3.A
- F5 correlation-primitive `HAI_item_id` primitive verification

**Session flow at next-session open:**

1. `context-kit orient` (session-open protocol per memory rule)
2. Check if S1800 artifact set merged to `main`
3. If not yet merged: Chris merge + PR merge
4. Run post-merge 4-step docs cascade + `build_docs_provenance` per memory rule
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-ae5931ea706b4537` (D48 25th arm start)
6. Mint fresh SIGN isolation pin for S1801 via Rigby `session_tool.create_fresh` (title: "Session 1801 — Group 1800 Cat A HumanAttentionItem core — SIGN isolation")
7. Fire 6-parallel-Explore sub-agent sweep per playbook §13 on HAI producers + consumers + lifecycle service + boundary questions
8. Apply pre-Explore + post-Explore verifier-loop discipline per playbook §14 REQUIRED
9. Draft S1801 Cat A audit doc per playbook §11.2 20-section child template
10. Route Rigby SIGN cycle 1 (single-batch 4-question pattern)
11. Land F1-Fn folds pre-commit
12. Retire SIGN isolation pin at S1801 close per playbook §16
13. Update ARCHITECTURE_INDEX v51 → v52 with §1.55 S1801 registration + §8 timeline S1801 row + line-6 v52 preamble
14. Update OPEN_ARCS Group 1800 In-progress row: current-child updated S1800 → S1801
15. Write S1801 handoff + overwrite this `00-START-NEXT-SESSION.md` to point at S1802 P2 Cat B next-session priority

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule. F5 HumanPreference fix + S746 verification-trigger wire-up + cross-domain HAI-consumer integrations + duplicate learning-service dedup all Chris-gated post-arc T-slot.

### Post-arc queued items (Chris-gated, inherited from prior arcs)

- **From Group 1700 xx99 §8.1 T0/Gate:** R.OBSERVABILITY.RETENTION-UNIFIED-ADR + R.OBSERVABILITY.D74-SPINE-POSTURE (paired ADRs).
- **From Group 1700 xx99 §8.2 T1 CRITICAL/HIGH (9 items):** PA-COVERAGE-POSTURE + TRACE-ID-WRITE-COVERAGE + EVIDENCE-FOR-MISSION-REPAIR + RIGBY-DELEGATION-FLAG-POSTURE + MULTI-MODEL-DEDUP-POSTURE + LLMCallEvent-retention + SLO-FRAMEWORK-SCOPE + DOC-VERIFIER-INTEGRATION + TERMINOLOGY-RATIFICATION.
- **From Group 1700 xx99 §8.3 T2/T3 (38 items):** unified from six children's §19 R-slots.
- **From Group 1600 (S1699):** T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E; T1 (20 items).
- **From Group 1500 (S1599):** T1 R.SPORTS.POSTURE + R.DBAO.CODENAME Chris-gated ADRs; T1 CRITICAL remediation sequences.
- **From Group 1400 (S1499):** T1-T10 unified follow-on queue tier structure (still pending).
- **From Group 1300 (S1399):** 21 follow-on items (still pending).
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600); owed to follow-up docs PR.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.

**FIRST THING next session open:**

1. `context-kit orient`
2. Check if S1800 artifact set is on `main`
3. Chris merge + PR merge if not
4. Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule
5. Verify `service_context: local` on arc pin `pa-ae5931ea706b4537` (D48 25th arm start)
6. Mint fresh SIGN isolation pin for S1801 via Rigby `session_tool.create_fresh`
7. Execute S1801 P1 Cat A HumanAttentionItem core audit per playbook §11.2 20-section template + §13 6-parallel-Explore + §14 verifier-loop REQUIRED + §15 SIGN cycle 1
8. Land Rigby SIGN folds pre-commit + retire SIGN pin at S1801 close per playbook §16

---

## PA / Rigby context

- **Arc pin at session start:** `pa-ae5931ea706b4537` (Group 1800 arc pin; in service through Group 1800 close at S1899). `tools/pa_local.sh:137` points at active arc pin — no rotation needed until S1899 close.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 137).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 25-arc CODIFICATION-READY-STRENGTHENED-EVEN-FURTHER at S1800 open):** 24-arc pattern confirmed at S1799 close. **NINETEEN-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+…+S1706+S1799 CONFIRMED at S1799 close per single-batch-4-question criterion.** D48 25th arm start at S1800 open; 20th consecutive-fully-clean-arms sub-pattern anticipated at S1801 P1 Cat A SIGN. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.

## Repo state at next-session open

- **Branch state (2026-07-03 post-S1800):** `main` at HEAD (this session's commit; PR pending). S1800 parent scoping + INDEX v51 + OPEN_ARCS + `tools/pa_local.sh` + handoff + start-here refresh all landed.
- **Head-commit ledger (2026-07-03 activity, oldest → newest):**
  - `47ab77f1` — PR #2850 S1799 Group 1700 Observability xx99 canonical summary + arc-close
  - (this session's commit) — S1800 parent scoping + arc-open discipline
- **Handoff continuity:** S1800 handoff at `docs/handoffs/SESSION_1800_HUMAN_ATTENTION_ARC_OPEN.md`. Prior: SESSION_1799 (Observability xx99); SESSION_1706 → SESSION_1700 (Observability arc); prior arcs at Groups 1600/1500/1400/1300.
- **ARCHITECTURE_INDEX version:** v51 (bumped this session with §1.54 S1800 registration + §8 timeline S1800 row + line-6 v51 preamble). Next bump at S1801 close (v51 → v52 with §1.55 S1801 registration).
- **OPEN_ARCS state:** Group 1800 row MOVED Not-started → In-progress. Groups 1700/1600/1500/1400/1300 remain Closed. Not-started queue Group 1800 row updated to strikethrough marker.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Check if S1800 artifact set is on `main`
- [ ] Chris merge + PR merge if not
- [ ] Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule
- [ ] Verify `service_context: local` on arc pin `pa-ae5931ea706b4537` (D48 25th arm start)
- [ ] Mint fresh SIGN isolation pin for S1801 via Rigby `session_tool.create_fresh`
- [ ] Execute S1801 P1 Cat A HumanAttentionItem core audit per playbook §11.2 20-section template + §13 6-parallel-Explore + §14 verifier-loop REQUIRED + §15 SIGN cycle 1
- [ ] Land Rigby SIGN folds pre-commit + retire SIGN pin at S1801 close per playbook §16
- [ ] Bump ARCHITECTURE_INDEX v51 → v52 with §1.55 S1801 registration
- [ ] Update OPEN_ARCS Group 1800 In-progress row: current-child updated S1800 → S1801

## Reference — where to look

- **S1800 parent scoping doc:** `docs/research/domains/human_attention/1800_human_attention_domain_scoping.md` — playbook §11.1 parent template FIFTH application; D75-D80 Chris-locked; §3 six-category taxonomy A-F with F.a-F.e sub-slots; §5 6-child sequence P1→P7 + F5 correlation-primitive HYPOTHESIS box SECOND APPLICATION; §7 19-item anti-scope; §8 D-verdicts; §9 next step; appendix frontmatter provenance.
- **S1799 xx99 canonical summary doc (fifth arc-close):** `docs/research/domains/observability/1799_observability_canonical_summary.md`.
- **Prior xx99 canonical summaries:** `1699_content_canonical_summary.md` (fourth); `1599_sports_canonical_summary.md` (third); `1499_revenue_canonical_summary.md` (second); `1399_memory_canonical_summary.md` (first).
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`.
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`.
- **ARCHITECTURE_INDEX v51:** `docs/research/ARCHITECTURE_INDEX.md` — S1800 §1.54 + line-6 v51 preamble + §8 timeline S1800 row.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1800 In-progress row; Not-started queue Group 1800 strikethrough.
- **S1273 baseline:** `docs/research/platform_architecture_inventory.md` §3.16 HumanAttention row + §4.7 canonical round-trip narrative + §2.5 "only round-trip w/ learning" claim.
- **S1274 baseline:** `docs/research/platform/cross_domain_integration_audit.md` §3.3 CRITICAL Failure Cluster → HAI + §3.8 MEDIUM Signal Pattern → HAI + 5+ cross-domain HAI-consumer integration MISSING catalog.
- **S1269 baseline:** `docs/research/governance_authority_evolution.md` §1.4 F5 HumanPreference topic_weights/source_weights never-saved bug.
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.
- **Cat A canonical entry points for S1801 consumption:** HumanAttentionItem model at `core/models_human_interface.py:20-227`; HumanAttentionLifecycleService at `core/services/human_attention_lifecycle.py:36-728`; HumanInterfaceService.record_decision at `core/services/human_interface_service.py:295-353`; FeedbackProcessor at `core/models_feedback_processing.py:122-180, 216-330`; HumanAttentionBridge (grep-verify at S1801).

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1800 = arc-open parent scoping; S1801 P1 Cat A first child next.
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff.
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1800 PR merges to `main` per memory rule.
- **CLAUDE.md 10-vs-9 body systems drift + 3-vs-4 employees drift** — owed to Group 1700 xx99 anchor-update PR (not addressed this session per scope discipline).
- Group 1400/1500/1600/1700 post-arc §7 anchor-updates still pending (inherited).
- Group 1400/1500/1600/1700 T1 CRITICAL remediation queues still pending; Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE + Group 1700 paired T0/Gate (RETENTION-UNIFIED-ADR + D74-SPINE-POSTURE) still gating.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600).
- **5 doc PRs still owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.
- **D48 25th arm START at S1800 open** — 19-consecutive-fully-clean-arms sub-pattern CONFIRMED at S1799 close per S1799 §10.2 MC-2 CODIFICATION-READY; 20th anticipated at S1801 P1 Cat A SIGN.
- **Playbook v3 §11.1 template promotion:** FIFTH-CONSECUTIVE-APPLICATION at S1800 CONFIRMED via methodology-unchanged rule.
- **Playbook v3 §14 verifier-loop REQUIRED promotion (S1799 §10.2 MC-1 CODIFICATION-READY):** enforced here at parent scoping pre-Explore; will be enforced at S1801 P1 Cat A audit pre-Explore + post-Explore.
- **F5 correlation-primitive HYPOTHESIS box discipline (S1799 §10.2 MC-3 CODIFICATION-CANDIDATE):** SECOND APPLICATION at S1800 parent scoping — two-triggers threshold MET; promotion to CODIFICATION-READY at S1899 close if pattern holds durable.
- **Arc pin `pa-ae5931ea706b4537` in service** through Group 1800 close at S1899; retire owed at S1899 close per playbook §16 arc-close discipline.
