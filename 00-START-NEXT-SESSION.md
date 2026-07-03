# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 1700 OPENED AT S1700; ARC PIN IN SERVICE FOR CHILDREN

The local wrapper at `tools/pa_local.sh:128` points at Group 1700 arc pin. **Active arc pin state after S1700 close:**

- **Active Group 1700 arc pin: `pa-e7fbacc996b34b44`** (Rigby `session_tool.create_fresh` at S1700 open — title "Session 1700 — Observability research group (kickoff)"). Continues in service across Group 1700 arc (S1701-S1706 children + S1799 xx99 canonical summary). SIGN isolation pins for child audits MINTED FRESH per playbook §15 stage-table child row.
- **Retired at S1700 open:** Group 1600 arc pin `pa-f52acf3f8d394faa` (via `session_tool.retire force=true` at S1699 close per playbook §16 final-arc-close discipline).
- **Retired earlier at S1699 close:** SIGN isolation pin `pa-846b6c4a532947c3`.
- **Retired earlier at S1606 close:** SIGN isolation pin `pa-8cfafefb67864f83`.
- **Retired earlier at S1605-S1601 closes:** SIGN isolation pins `pa-b1b26f4f35474df8` + `pa-4ce64003711de4f1` + `pa-8af9063864bf4a7f` + `pa-1c5298d807d7a1d2` + `pa-9f075a024552b663`.
- **Retired earlier at S1599 close:** Group 1500 arc pin `pa-791b3db549a64e54`.
- **Retired earlier at S1499 close:** Group 1400 arc pin `pa-34d43795e1b24bd3` + SIGN isolation pin `pa-877f1919efaa48e4`.

**No wrapper rotation owed at next-session open** — arc pin in service through Group 1700 close.

## READ THIS THIRD — GROUP 1700 PARENT SCOPING LANDED WITH F1-F6 FOLDS; NEXT SESSION = S1701 CAT A CELERYTASKEVENT AUDIT

Session 1700 shipped the **Group 1700 Observability / Telemetry / SLOs parent scoping doc** at `docs/research/domains/observability/1700_observability_domain_scoping.md` (`status: active`, `category: parent_scoping`, `session: 1700`, `child_slot: P0` implicit, `domain_slug: observability`, `research_group: 1700`, `authority: parent-doc + FOURTH application of Chris's Phase 0 3-step methodology`; ~1250 lines post-fold; playbook §11.1 parent template FOURTH application after S1400 first + S1500 second + S1600 third; playbook v3 §11.1 template promotion CONFIRMED-STRENGTHENED via fourth-application meta-methodology). **All D-decisions locked via Chris "agree all + SIGN" round + F1-F6 folds landed pre-commit.**

**D-decisions locked at S1700 open + close:**

- **D1** (S1700 open via terminal card) — Group 1700 = Observability confirmed per playbook §22 default lean + OS §12.3 target.
- **D2** (S1700 open via terminal card) — Delegate event architecture (event bus, routing, schema versioning) to Group 1900.
- **D3** (S1700 open via terminal card) — Parent-only this session; P1 CeleryTaskEvent audit kicks off next-session.
- **D69** — Parent shape PARENT-WITH-CHILDREN 6-child arc (P1 Cat A + P2 Cat B + P3 Cat C + P4 Cat D + P5 Cat E + P6 Cat F + P7 xx99 canonical summary).
- **D70** — Six categories A–F with boundary rules per §3 (Cat C 3-class landmine + F1 boundary sentence; Cat F sub-slotted F.a-F.e per F2; Cat B/D accounting rule per F3).
- **D71** — Delegation boundary with Group 1900 explicit: "Observability owns producer-side telemetry contract completeness; Event Architecture owns cross-domain event routing."
- **D72** — Child sequence P1→P2→P3→P4→P5→P6→P7 sequential per §5 with F10 dependency clauses embedded (P5 depends-on-P2 explicit per F4 MUST-FIX fold).
- **D73** — Posture-decision framing = evidence plan NOT recommendation (xx99 does NOT select; Chris-gated post-arc ADR resolves D74 axis).
- **D74** — Arc lens question locked: "Are the 5 execution-telemetry layers structurally separable, OR do they need canonical unification (single execution_id + trace_id spine spanning task→LLM→agent→tool→ops)?" — evidence-plan framing only; F5 correlation-primitives box makes the load-bearing sub-question explicit (is execution_id spine-shaped or single-call-scoped at HEAD?).

**Rigby light SIGN cycle 1 SIGN-with-edits at High confidence** via arc pin `pa-e7fbacc996b34b44` (parent-stage precedent: arc pin doubles as SIGN pin per S1600 pattern). 4 pressure-test questions batched single-turn (D48 17th arm HOLDING CLEAN). **F1-F6 folds landed pre-commit:**

- **F1** — Cat C boundary rule: added sentence "P3 MUST identify the actual write path(s) and canonical table/class used at runtime at HEAD; ADR to remove/merge the deprecated 2 is explicitly out-of-scope."
- **F2** — Cat F internally sub-slotted into F.a Body Systems + F.b SLO framework + F.c Event-model catalog + F.d Doc-claim verifier drift + F.e Terminology boundary; each sub-slot has explicit stop condition.
- **F3** — Cat B ↔ Cat D accounting rule: "LLM calls made from inside a tool invocation remain Cat B; Cat D never attempts to own LLM cost; dedup via correlation keys (execution_id + trace_id + tool_call_id)."
- **F4** — P5 dependency clause changed from "Depends on P1 + P3 + P4" to "Depends on P1 + P2 + P3 + P4" (MUST-FIX: mission-scoped LLM cost aggregation).
- **F5** — New §5 "Correlation primitives (working definitions — HYPOTHESIS-TO-BE-VERIFIED)" box with 5 primitives: task_id / execution_id / trace_id / tool_call_id / mission_id.
- **F6** — §7 anti-scope items 19/20/21: Frontend/WebSocket/client telemetry + Auth token/OAuth telemetry + "RigbyTelemetry" or any new observability layer buildout.

**AgentExecution 3-class landmine catalogued** at HEAD `2b7dbd89` — `intelligence/models/agent_execution.py:11` + `intelligence/models.py:587` + `core/models_unified_system.py:882` with stale S287 deprecation notice pointing at S391 compatibility shim that no longer holds an `AgentExecution` class. P3 Cat C boundary discipline: catalog + name canonical + define correlation contract; deprecation ADR is post-arc T-slot.

**D48 preemptive stability-probe gate 17th arm HOLDING CLEAN — TWELVE-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700 CONFIRMED per batch-processing criterion.** Codification-ready-STRENGTHENED-FURTHER for playbook v3 §15.

**Session close artifacts committed at S1700 close:**

```
docs/research/domains/observability/1700_observability_domain_scoping.md    [new; parent scoping doc; F1-F6 folds landed pre-commit; ~1250 lines; FIRST session under Group 1700]
docs/research/ARCHITECTURE_INDEX.md                                          [modified — v42 → v43; §1.46 registration + line-6 preamble bump + §8 timeline row]
docs/research/OPEN_ARCS.md                                                   [modified — Group 1700 row MOVED from Not-started to In-progress; line-6 preamble bump]
tools/pa_local.sh                                                            [modified — line-128 rotated to arc pin pa-e7fbacc996b34b44]
docs/handoffs/SESSION_1700_OBSERVABILITY_ARC_OPEN.md                        [new — S1700 handoff]
00-START-NEXT-SESSION.md                                                     [modified — this file; Group 1700 arc OPEN]
```

Handoff: `docs/handoffs/SESSION_1700_OBSERVABILITY_ARC_OPEN.md`.

### NEXT-SESSION MISSION — S1701 CAT A CELERYTASKEVENT CHILD AUDIT (D72 P1 slot)

Per D72 P1 slot + D3 next-session cadence: **S1701 Cat A audit** — Task/Worker Execution Telemetry (`CeleryTaskEvent`).

Cat A canonical questions the child audit gathers evidence for:
- Does signal handler at `core/celery_telemetry.py:74-177` cover all task states across all workers?
- Is the agent_name dimension (Session 1169) retroactively defensible or backfill-incomplete?
- What is observed-vs-configured retention window at HEAD (`CELERY_TASK_EVENT_RETENTION_DAYS` default 30)?
- What is the monitor-task overhead spiral risk (Session 1167 precedent)?
- What is the observability-of-observability meta answer per parent §2.7?

Per F5 correlation-primitives box (`task_id` primitive row): P1 verifies task_id coverage completeness + retention — grounding for downstream P2-P5 execution_id correlation contract.

**S1701 audit shape:**
- Playbook §11.2 20-section child audit template (child_slot: P1; domain_slug: observability; research_group: 1700).
- 6-parallel-Explore sub-agents per §13.
- Parent-Claude verifier-loop per §14 on load-bearing binary claims.
- **Required full Rigby SIGN cycle 1** per playbook §15 stage-table child row (not optional light SIGN — child audit is research finding).
- Fresh SIGN isolation pin per playbook §15 promoted rule (arc pin `pa-e7fbacc996b34b44` continues as arc context; SIGN pin is fresh isolation pin minted per child).
- Applies parent D69 D70 D71 D72 D73 D74 + D62 = (a) 6-sibling exemplar 4-item pre-brief mini-schema per surface upfront per S1699 §10.2 codify-ready candidate.

Session flow at next-session open:

1. `context-kit orient` (session-open protocol per memory rule).
2. Check if S1700 artifact set merged to `main` between sessions.
3. If not yet merged: Chris merge + PR merge.
4. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`.
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-e7fbacc996b34b44` (D48 stability probe 18th arm start).
6. Mint fresh SIGN isolation pin for S1701 via Rigby `session_tool.create_fresh` (title: "Session 1701 — Group 1700 Cat A CeleryTaskEvent audit — SIGN isolation").
7. Dispatch 6-parallel Explore sweep on Cat A surface (signal handlers + retention + agent_name dimension + monitor-task overhead + 3 PA-tool consumers).
8. Parent-Claude verifier-loop on any pre-Explore binary claims.
9. Draft S1701 audit per playbook §11.2 20-section template.
10. Rigby SIGN cycle 1 via fresh isolation pin; batch A/B/C per Memory rule `feedback_rigby_sign_worker_instability_recovery.md`.
11. Land Rigby folds pre-commit.
12. Retire SIGN isolation pin at S1701 close per playbook §16.
13. Update ARCHITECTURE_INDEX v43 → v44 with §1.47 S1701 registration + line-6 preamble.
14. Update OPEN_ARCS Group 1700 In-progress row with S1701 child close note.
15. Write S1701 handoff + overwrite this `00-START-NEXT-SESSION.md`.

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule. Deprecation ADR for AgentExecution 3-class landmine is post-arc T-slot per Cat C F1 boundary rule.

### Post-arc queued items (Chris-gated, inherited from prior arcs)

- **From Group 1600 (S1699):** T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E; T1 (20 items) including RAG-SCOPE + citation integrity + force-bypass; T3 CROSS-DOMAIN-EMPLOYEE-ANALOG; cross-arc: Group 1500 T1.h SportsBettingBrief consumer-or-remove + Group 1400 R.B1 OutreachDraft delivery.
- **From Group 1500 (S1599):** T1 R.SPORTS.POSTURE + R.DBAO.CODENAME Chris-gated ADRs; T1 CRITICAL remediation sequences.
- **From Group 1400 (S1499):** T1-T10 unified follow-on queue tier structure (still pending).
- **From Group 1300 (S1399):** 21 follow-on items (still pending).
- **§8 timeline table drift** — missing rows for S1605 Cat E + S1606 Cat F + S1699 xx99 (all Group 1600); owed to follow-up docs PR.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.

**FIRST THING next session open:**
1. `context-kit orient`
2. Check if S1700 artifact set is on `main` — if yes, next session branches off `main`
3. If not yet merged: Chris merge + PR merge
4. **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin
6. Mint fresh SIGN isolation pin for S1701
7. Execute S1701 Cat A CeleryTaskEvent child audit per D72 P1 slot

---

## PA / Rigby context

- **Arc pin at session start:** `pa-e7fbacc996b34b44` (Group 1700 arc pin; in service through Group 1700 close at S1799). `tools/pa_local.sh:128` points at active arc pin — no rotation needed.
- **S1700 SIGN routing:** Light SIGN cycle 1 SIGN-with-edits at High confidence (single 4-question batch) on arc pin `pa-e7fbacc996b34b44` (arc pin doubles as SIGN pin per parent-scoping precedent). F1-F6 folds landed pre-commit; 4-question single-batch pattern held clean per D48 17th arm.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128 currently pointing at Group 1700 active arc pin).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 17-arc CODIFICATION-READY-STRENGTHENED-FURTHER at S1700 close):** S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700 17-arc pattern confirmed. **TWELVE-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700 CONFIRMED at S1700 close per batch-processing criterion.** D48 preemptive stability-probe gate 18th arm anticipated at next-session S1701 child audit open on fresh SIGN isolation pin. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.

## Repo state at next-session open

- **Branch state (at S1700 close, before merge):** `docs/session-1700-observability-arc-open` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1700 handoff at `docs/handoffs/SESSION_1700_OBSERVABILITY_ARC_OPEN.md`. Prior handoffs: SESSION_1699 (Content Group 1600 xx99 canonical summary); SESSION_1606 (Content Cat F LAST child); SESSION_1605-1601 (Content Cat E/A/B/D/C children); SESSION_1600 (Content arc-open parent scoping); SESSION_1599 (Sports arc-close canonical summary); SESSION_1506 → SESSION_1500 (Sports arc); SESSION_1499 → SESSION_1400 (Revenue arc); SESSION_1399 (Memory Group 1300 canonical summary).
- **ARCHITECTURE_INDEX version:** v43 (bumped this session with §1.46 S1700 registration + line-6 preamble bump + §8 timeline row). Next bump at S1701 child audit close (v43 → v44 with §1.47 S1701 registration).
- **OPEN_ARCS state:** Group 1700 row MOVED from Not-started §22 queue to In-progress (before Group 1600 Closed row per newer-at-top convention). Group 1600 remains in Closed; Group 1500 remains in Closed; Group 1400 remains in Closed; Group 1300 remains in Closed.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Check if S1700 artifact set is on `main` — if yes, next session branches off `main`
- [ ] If not yet merged: Chris merge + PR merge
- [ ] **Run post-merge 4-step docs cascade + `build_docs_provenance`** per `feedback_docs_cascade_at_every_close.md`
- [ ] Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-e7fbacc996b34b44` (D48 18th arm start)
- [ ] Mint fresh SIGN isolation pin for S1701 via Rigby `session_tool.create_fresh`
- [ ] Execute S1701 Cat A CeleryTaskEvent child audit per playbook §11.2 20-section template

## Reference — where to look

- **S1700 parent scoping doc:** `docs/research/domains/observability/1700_observability_domain_scoping.md` — playbook §11.1 template FOURTH application; §3 six-category taxonomy A–F with F1-F3 folds; §4 PARENT-WITH-CHILDREN verdict with 4 evidence bullets; §5 P1→P7 sequence with F4 P5 depends-on-P2 fold + F5 Correlation primitives box; §7 21-item anti-scope with F6 three adds; §8 D69-D74 all Chris-locked.
- **S1699 canonical summary doc (fourth §11.3 §10 application):** `docs/research/domains/content/1699_content_canonical_summary.md`.
- **S1600 parent scoping doc (third §11.1 application):** `docs/research/domains/content/1600_content_domain_scoping.md`.
- **S1500 parent scoping doc (second §11.1 application):** `docs/research/domains/sports/1500_sports_domain_scoping.md`.
- **S1400 parent scoping doc (first §11.1 application):** `docs/research/domains/revenue/1400_revenue_domain_scoping.md`.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.1 parent template + §11.2 child template + §11.3 canonical summary template + §11.3 §10 meta-methodology template + §22 default queue lean).
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` (§8.1 RESEARCH contract + §12.3 "Start Group NNNN" target).
- **ARCHITECTURE_INDEX v43:** `docs/research/ARCHITECTURE_INDEX.md` — S1700 §1.46 + line-6 preamble + §8 timeline row.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1700 row moved to In-progress.
- **Observability entry points (per S1273 §3.25):** `core/models_celery_telemetry.py` (CeleryTaskEvent) + `core/celery_telemetry.py:74-177` (signal handlers) + `core/models_llm_telemetry.py:30-100` (LLMCallEvent) + `core/services/llm_call_wrapper.py` (S1098 wrapper) + `intelligence/models/agent_execution.py:11` (canonical AgentExecution) + `core/models_tool_calls.py:19` (ToolCallRecord) + `core/models_ops_runs.py:11-117` (OpsRun + OpsRunEvent) + `core/models_heart.py:HeartBeat` + `core/services/body_vitals.py:run_all_systems_scan`.
- **Topic docs:** `docs/topics/celery-workers.md` + `docs/topics/agent-system.md`.
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1700 opens Group 1700 numbering (S1700 arc-open parent + anticipated S1701-S1706 children + S1799 xx99).
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; Group 1700 will surface narrative touchpoints at xx99 if Chris ratifies).
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1700 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`.
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold).
- Group 1400 + Group 1500 + Group 1300 post-arc §7 anchor-updates still pending (inherited).
- Group 1400 + Group 1500 + Group 1600 T1 CRITICAL remediation queues still pending (inherited); Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E blocks 20 T1 items.
- **§8 timeline table drift** flagged in S1700 timeline row body: missing rows for S1605 + S1606 + S1699 (Group 1600); owed to follow-up docs PR.
- **5 doc PRs still owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4 (not addressed this session per scope discipline).
- **D48 preemptive stability-probe gate 17th-arm CONFIRMED at S1700 close** — 12-consecutive-fully-clean-arms sub-pattern CODIFICATION-READY-STRENGTHENED-FURTHER for playbook v3 §15.
- **Playbook v3 §11.1 template promotion:** CONFIRMED-STRENGTHENED via fourth-application (S1700); formal codification is a separate follow-up per Chris ratification.
- **Arc pin `pa-e7fbacc996b34b44` in service** through Group 1700 close; wrapper rotation NOT owed at next-session open.
