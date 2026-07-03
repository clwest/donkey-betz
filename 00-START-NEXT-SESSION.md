# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token + arc pin).

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 1700 IN-PROGRESS; S1705 CAT E CLOSED; NEXT = S1706 CAT F (LAST CHILD BEFORE S1799 xx99)

The local wrapper at `tools/pa_local.sh:128` points at Group 1700 arc pin. **Active arc pin state after S1705 close:**

- **Active Group 1700 arc pin: `pa-e7fbacc996b34b44`** (Rigby `session_tool.create_fresh` at S1700 open — title "Session 1700 — Observability research group (kickoff)"). Continues in service across Group 1700 arc (S1701 CLOSED + S1702 CLOSED + S1703 CLOSED + S1704 CLOSED + S1705 CLOSED + S1706 child pending + S1799 xx99 canonical summary). SIGN routing at S1705 landed on arc pin per S1600/S1700/S1701/S1702/S1703/S1704 parent-scoping precedent (arc pin doubles as SIGN pin; fresh SIGN pin `pa-09c46ee3a0d34069` minted per playbook §15 but routed-around by wrapper hard-code at L128; fresh SIGN pin retired at S1705 close per §16 with `updated_count=1, retired=true, previously_active=true`).
- **Retired at S1705 close:** Fresh SIGN isolation pin `pa-09c46ee3a0d34069`.
- **Retired post-S1704 (mid-arc cross-domain refresh SIGN pin, 2026-07-03):** Fresh SIGN isolation pin `pa-99cacc35a73e4dbb` (NOT a Group 1700 artifact; cross-arc research-library maintenance).
- **Retired at S1704 close:** Fresh SIGN isolation pin `pa-f7417e6ac21d4f23`.
- **Retired at S1704 open:** Fresh SIGN isolation pin `pa-f1a30b7ed5bb4042` (S1703 owed-retire).
- **Retired at S1702 close:** Fresh SIGN isolation pin `pa-c3927ab78c52479a`.
- **Retired at S1701 close:** Fresh SIGN isolation pin `pa-3147aef9db4945ac`.
- **Retired at S1700 open:** Group 1600 arc pin `pa-f52acf3f8d394faa`.
- **Retired earlier at S1699 close:** SIGN isolation pin `pa-846b6c4a532947c3`.
- **Retired earlier at S1606 close:** SIGN isolation pin `pa-8cfafefb67864f83`.
- **Retired earlier at S1605-S1601 closes:** SIGN isolation pins `pa-b1b26f4f35474df8` + `pa-4ce64003711de4f1` + `pa-8af9063864bf4a7f` + `pa-1c5298d807d7a1d2` + `pa-9f075a024552b663`.
- **Retired earlier at S1599 close:** Group 1500 arc pin `pa-791b3db549a64e54`.
- **Retired earlier at S1499 close:** Group 1400 arc pin `pa-34d43795e1b24bd3` + SIGN isolation pin `pa-877f1919efaa48e4`.

**No wrapper rotation owed at next-session open** — arc pin in service through Group 1700 close at S1799.

## READ THIS THIRD — S1705 CAT E OPS RUN EVENT AUDIT LANDED; NEXT = S1706 CAT F ADJACENT/SEPARATION BOUNDARIES

Session 1705 shipped the **Group 1700 Cat E OpsRun + OpsRunEvent child audit** at `docs/research/domains/observability/1705_observability_cat_e_ops_run_event_audit.md` (`status: active`, `category: child_audit`, `session: 1705`, `child_slot: P5`, `domain_slug: observability`, `research_group: 1700`, `head_commit`: (this session's commit), `authority: child-audit`; 916 lines pre-fold + ~60 lines added by F1-F7 folds; playbook §11.2 20-section child audit template FIFTH application under Group 1700; playbook §13 6-parallel-Explore sweep + §14 verifier-loop applied pre-Explore + post-Explore; Rigby SIGN cycle 1 SIGN-with-edits at Medium/Medium-High confidence — F1-F7 folds landed pre-commit). **17-consecutive-fully-clean-arms sub-pattern CONFIRMED via D48 22nd arm** on arc pin `pa-e7fbacc996b34b44` (single-batch 4-question pattern per S1701/S1702/S1703/S1704 precedent).

**9 load-bearing findings locked in S1705 audit §1.1 Executive Summary:**

- **F1 (HIGH, §17)** — 0/224 OpsRunEvent rows carry cross-cat correlation IDs in `detail` JSON at HEAD (ORM-verified 2026-07-03: execution_id=0, trace_id=0, task_id=0, tool_call_id=0, agent_execution_id=0, llm_call_id=0, celery_task_id=0). DESIGN-INTENT writer at `core/signals/rigby_delegation_signals.py:79-84` (Session 1250 PR 8) IS built to populate `execution_id` in detail on delegated-execution post-save, but handler is gated by `settings.RIGBY_DELEGATION_ENABLED` (default `False` per `rigby_delegation_signals.py:22-25`). Distinct from S1704 F1 (Cat D schema+runtime failure): Cat E is intentionally-flag-gated (DESIGN-INTENT-LATENT).
- **F2 (HIGH, §17)** — Cat E schema has NO cross-cat correlation columns. Only `mission_id` (indexed, mission-domain only) + implicit `run` FK. Parallel to S1704 F2.
- **F3 (MEDIUM, verifier-loop-corrected, §14+§17)** — CLAUDE.md at :150-172 + PLATFORM_INVENTORY autoblock claim "3 Employees" but registry `_EMPLOYEES_BY_HANDLE` at `core/employees/jobs.py` has **4** handles verified via ORM: rigby (docs_manager), platform_auditor (platform_audit), chief_of_staff (morning_brief), **bug_triage_specialist (triage_daily — added S1267 PR 4.1)**. Runtime works correctly; drift on-doc-only. Owed to xx99 anchor-update.
- **F4 (POSITIVE differentiator vs S1704 F4, §7+§9)** — CTO/COO/Trend Analysis daily diagnostic pipelines EXIST at `core/services/diagnostics/{cto_daily,coo_daily}.py` + `core/services/scheduled_diagnostic_runner.py` AND ARE beat-wired at `core/celery.py:306-329` at 07:15/07:30/07:45 Denver (queue: long_running, expires: 7200). NOT WRITE-ONLY-FORGOTTEN. Material Cat E vs Cat D difference: S1704 F4 found two aggregation tasks beat-orphan; Cat E has three fully-wired daily aggregations.
- **F5 (MEDIUM, §9+§17)** — But those three daily aggregations do NOT consume OpsRunEvent (CTO reads CeleryTaskEvent + AgentExecution; COO reads Deliverable + ActionItem + Initiative backlog; Trend Analysis reads LegacySpiderData + SignalCluster). **OpsRunEvent has ZERO downstream aggregation consumer.** Resolves parent §5.E producer-vs-consumer question: OpsRunEvent is a **PRODUCER-ONLY primary source of mission telemetry**. Canonical verdict at HEAD per Rigby SIGN Q3(d) fold; could evolve if future work introduces cross-table correlation IDs + explicit aggregation pipeline — post-arc T-slot.
- **F6 (MEDIUM, §15)** — No date-based retention for OpsRun/OpsRunEvent. Parallel to S1704 F5 + S1702 F4. Current cadence: 36 OpsRun over 20 days → ~657/year projected; 224 OpsRunEvent → ~4,088/year projected. Small cadence but unaudited-headroom.
- **F7 (MEDIUM, §9+§17)** — `evidence_for_mission` join at `docs/topics/employee-os.md:64-65` EMPIRICALLY BROKEN for ToolCallRecord — two orthogonal write-gap paths (S1704 F1 100% NULL trace_id + Cat D dispatcher never threads `parameters.ops_run_id`). LLMCallEvent join by `metadata__ops_run_id` WORKS (`mission_verdict.py:117-150` populates). D4 HIGH held per Rigby SIGN Q2(b) fold (Chris-facing operator surface justifies HIGH even though upstream root cause is Cat D-side).
- **F8 (POSITIVE, §7+§13)** — MissionRunner nine invariants I1-I9 all VERIFIED at HEAD via source read + contract test at `test_mission_runner.MissionRunnerImportContractTests` @ `core/tests/test_mission_runner.py:181-250`. Cat E writer-mechanism maturity **STABLE**.
- **F9 (D74 axis contribution, §9)** — Cat E provides **LATENT-VIABLE-BUT-FLAG-GATED evidence** for spine correlation posture. Distinct axis cell from Cat D actively-broken (S1704 F1) + Cat C coverage-gap (S1703 F4). Cat E is NOT actively-broken and NOT schema-broken. Rigby SIGN Q3(b) fold nuance: flipping the Cat E flag DOES yield partial usefulness on the Cat E → Cat C axis via execution_id detail-JSON thread, even if Cat D remains broken; ToolCallRecord join (F7) remains blocking irrespective of flag state.

**§9 D74 axis-contribution:** Cat E adds a fourth axis cell (LATENT-VIABLE-BUT-FLAG-GATED) to the cross-cat correlation matrix. Cat E is the "cheapest to unblock" for Option B via `RIGBY_DELEGATION_ENABLED=True`, but by itself resolves nothing for the ToolCallRecord join.

**§16 Boundary violation matrix: 5 candidates all LEGITIMATE.** MissionRunner + OpsRunTracker + rigby_event_intake + rigby_delegation_signals (flag-gated) + mission_verdict PA tool — no unexpected writer sites via grep. BodyCoordinator NOT integrated (I9 boundary held). `tasks_ops.py` cross-imports from `core.tasks` are LEGITIMATE extraction artifact per file header.

**Maturity STABLE for writer mechanism (F8 I1-I9 verified) + PARTIAL for coverage + NAMED-BUT-BROKEN for cross-cat correlation contract (F7) + STRONG for downstream orthogonal (F4) + EMPTY for OpsRunEvent-consuming pipelines (F5) + Risk MEDIUM.**

**Rigby SIGN cycle 1 SIGN-with-edits at Medium/Medium-High confidence** on arc pin `pa-e7fbacc996b34b44` (fresh SIGN pin `pa-09c46ee3a0d34069` minted per playbook §15 but routed-around by `tools/pa_local.sh:128` wrapper hard-code — S1600/S1700/S1701/S1702/S1703/S1704 precedent applies; fresh SIGN pin retired at S1705 close per §16 with `updated_count=1, retired=true, previously_active=true`). **F1-F7 folds landed pre-commit:**

- **F1 (Q2(b) Medium)** — §14 D4 severity justification block (HIGH held for Chris-facing operator surface despite upstream root cause).
- **F2 (Q3(b) Medium-High)** — §1.1 F9 nuance about partial Cat E usefulness of flag flip via execution_id detail-JSON thread (unlocks Cat E → Cat C axis even if Cat D remains broken).
- **F3 (Q3(d) Medium)** — §1.1 F5 canonical verdict block (producer-only at HEAD; could evolve post-arc if future work adds correlation IDs + aggregation pipeline).
- **F4 (Q4(a) Medium)** — §19 R2 sequencing note (lowest-cost lever but should be sequenced after R1 D74 posture decision).
- **F5 (Q4(b) Medium)** — §19 R3 cross-cat remediation scope (HIGH held but remediation depends on S1704 R2 + S1703 R1).
- **F6 (Q4(c) Medium)** — §19 R6 1-2 sentence xx99 §7.4 scope discipline.
- **F7 (Q4(d) Medium)** — §19 R2 scope discipline per playbook §14.5 (record recommended toggle as evidence-plan decision, do NOT implement flag flip during xx99).

**Rigby CONFIRM verdicts:** Q1 coverage-completeness Medium-High (SIGN-clean) + Q2 drift-severity Medium (1 fold) + Q3 D74 axis correctness Medium-High (2 folds) + Q4 R1-R12 ranking + xx99 scope discipline Medium (4 folds).

**Session close artifacts committed at S1705 close:**

```
docs/research/domains/observability/1705_observability_cat_e_ops_run_event_audit.md  [new; ~975 lines post-fold; Cat E child audit; F1-F7 folds landed pre-commit; FIFTH child under Group 1700]
docs/research/ARCHITECTURE_INDEX.md                                                   [modified — v47 → v48 with §1.51 S1705 registration + §8 timeline S1705 row + line-6 v48 preamble]
docs/research/OPEN_ARCS.md                                                            [modified — Group 1700 In-progress row current-child updated S1704 → S1705]
docs/handoffs/SESSION_1705_OBSERVABILITY_CAT_E_OPS_RUN_EVENT_AUDIT.md                  [new — S1705 handoff]
00-START-NEXT-SESSION.md                                                              [modified — this file; S1705 Cat E CLOSED; next-session priority = S1706 Cat F Adjacent/Separation Boundaries]
```

Handoff: `docs/handoffs/SESSION_1705_OBSERVABILITY_CAT_E_OPS_RUN_EVENT_AUDIT.md`.

### NEXT-SESSION MISSION — S1706 CAT F ADJACENT/SEPARATION BOUNDARIES CHILD AUDIT (D72 P6 slot — LAST CHILD BEFORE S1799 xx99)

Per D72 P6 slot + parent §5 sequence: **S1706 Cat F audit** — Adjacent/Separation Boundaries. This is the **LAST child audit before S1799 xx99 canonical summary** (parent's 6-child sequence P1-P6 + xx99 P7 concludes).

Per parent §5.F six sub-slots (Rigby SIGN cycle 1 F2 fold at S1700 open established sub-slotting to prevent internal scope-magnet):

- **F.a HeartBeat / Body Systems** — `HeartBeat` model + BodyVitalsService + 9-body-system health scan. **Stop condition:** catalog export gap + cold-start correctness issue (S1273 lines 1964-1965); do NOT design the export pipeline or fix cold-start.
- **F.b SLO framework audit** — single ad-hoc `check_learning_loop_slo` task at `core/tasks.py:12492` (S1273 line 1969). **Stop condition:** catalog what SLO coverage exists today (single task; no meta-framework); do NOT design systemic SLO framework.
- **F.c Event-model catalog + WRITE-ONLY-FORGOTTEN audit** — 14+ event-shaped models from S1273 lines 1912-1917 (DeliverableEvent + ImpactEvent + EngagementEvent + TriggerEvent + FleetEvent + CockpitIncidentEvent + CockpitAutopilotEvent + ThreatEvent + ABTestEvent + ConversionEvent + BadContextEvent + RelationshipEvent + AuditLog + NotificationLog). **Stop condition:** catalog producer/consumer wiring per model; do NOT act on deprecation decisions (Group 1900 territory).
- **F.d Doc-claim verifier drift as meta-observability signal** — `core/services/doc_claim_verification.py` + `verify_doc_claims` command. **Stop condition:** catalog whether verifier drift is a telemetry-worthy signal; do NOT integrate verifier drift into observability infrastructure or fix verifier bugs.
- **F.e Observability↔Event-Architecture terminology boundary** — clarify where "Observability" ends and "Event System" begins. **Stop condition:** produce terminology recommendation for xx99 §5 posture-decision brief; do NOT rename subsystems or refactor terminology at HEAD.

Cat F canonical questions the child audit gathers evidence for:

- **Inherits from S1705 F6:** Does the retention-policy gap extend to any of the 14+ Cat F event-shaped models? Which have retention, which don't?
- **Inherits from S1705 F5:** Are any of the Cat F event-shaped models PRODUCER-ONLY vs consumer? Which have downstream aggregation pipelines?
- **Inherits from S1705 F4:** Are any Cat F event models beat-wired to CTO/COO/Trend Analysis daily (or analog)? Which are WRITE-ONLY-FORGOTTEN like S1704 F4?
- **Inherits from S1705 F1:** Does the HeartBeat export gap have DESIGN-INTENT-LATENT flag-gated writer or SCHEMA+RUNTIME failure like Cat D F1?
- **F.c cross-arc handoffs:** Group 1500 §14.3 SportsBettingBrief WRITE-ONLY-FORGOTTEN precedent detection + Group 1600 T0/Gate DeliverableEvent consumer-contract handoff.
- **F.e xx99 posture question:** Should Group 1700 catalog terminology boundary as strict / permeable / not-yet-decided?

**S1706 audit shape:**

- Playbook §11.2 20-section child audit template (child_slot: P6; domain_slug: observability; research_group: 1700).
- 6-parallel-Explore sub-agents per §13.
- Parent-Claude verifier-loop per §14 on load-bearing binary claims (pre-Explore + post-Explore).
- **Required full Rigby SIGN cycle 1** per playbook §15 stage-table child row (D48 23rd arm anticipated).
- Fresh SIGN isolation pin per playbook §15 promoted rule (arc pin `pa-e7fbacc996b34b44` continues as arc context; SIGN routing will land on arc pin per S1700-S1705 wrapper hard-code precedent).
- Applies parent D69-D74 + Cat A S1701 §9 axis evidence + Cat B S1702 F9 axis contribution + Cat C S1703 F9 axis contribution + Cat D S1704 F9 axis contribution + Cat E S1705 F9 axis contribution.

Session flow at next-session open:

1. `context-kit orient` (session-open protocol per memory rule).
2. Check if S1705 artifact set merged to `main` (audit doc + INDEX v48 + OPEN_ARCS + handoff + start-here).
3. If not yet merged: Chris merge + PR merge.
4. Run post-merge 4-step docs cascade + `build_docs_provenance` per memory rule `feedback_docs_cascade_at_every_close.md`.
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-e7fbacc996b34b44` (D48 23rd arm start).
6. Mint fresh SIGN isolation pin for S1706 via Rigby `session_tool.create_fresh` (title: "Session 1706 — Group 1700 Cat F Adjacent/Separation Boundaries audit — SIGN isolation").
7. Dispatch 6-parallel Explore sweep on Cat F surface (five sub-slots F.a-F.e).
8. Parent-Claude verifier-loop on any pre-Explore binary claims.
9. Draft S1706 audit per playbook §11.2 20-section template.
10. Rigby SIGN cycle 1 (single-batch 4-question pattern per S1701-S1705 precedent).
11. Land Rigby folds pre-commit.
12. Retire SIGN isolation pin at S1706 close per playbook §16.
13. Update ARCHITECTURE_INDEX v48 → v49 with §1.52 S1706 registration + §8 timeline row + line-6 preamble.
14. Update OPEN_ARCS Group 1700 In-progress row with S1706 child close note. **Prepare row for imminent transition to Awaiting summary** (Group 1700 arc reaches 7/8 = 87.5% at S1706 close; S1799 xx99 canonical summary next).
15. Write S1706 handoff + overwrite this `00-START-NEXT-SESSION.md` to point at S1799 xx99 canonical summary as next-session priority.

**Not next (unless Chris specifies):** any specific implementation work per playbook §14.5 no-implementation rule. HeartBeat export activation + SLO framework design + event-model deprecation decisions + doc-claim verifier integration + terminology renames are all post-arc T-slot per parent §6.

### Post-arc queued items (Chris-gated, inherited from prior arcs + additions from S1705)

- **From S1705 §19:** R1 (HIGH) F9 D74 axis posture decision (Cat E contribution: fourth axis cell LATENT-VIABLE-BUT-FLAG-GATED); R2 (HIGH) F1 rigby_delegation flag posture — **sequencing note per Rigby SIGN Q4(a) fold: after R1 posture decision** + **scope discipline per Q4(d) fold: no flip during xx99 per §14.5**; R3 (HIGH) F7 evidence_for_mission join repair — **cross-cat remediation scope per Q4(b) fold: depends on S1704 R2 + S1703 R1**; R4 (MEDIUM) F2 schema-level correlation columns; R5 (MEDIUM) F6 retention policy; R6 (MEDIUM) F5 producer-vs-consumer contract doc — **1-2 sentence canonical note in xx99 §7.4 per Q4(c) fold**; R7 (MEDIUM) F3 employee count drift regen (`generate_platform_inventory` + CLAUDE.md autoblock refresh); R8-R12 LOW.
- **From S1705 §14:** D1+D2 MEDIUM 3-vs-4 employees drift on CLAUDE.md + PLATFORM_INVENTORY autoblock + D3 LOW parent §5.E scope-clarification + D4 HIGH F7 named-but-broken evidence_for_mission ToolCallRecord join + D5 LOW migration additive-only confirmed + D6 LOW `tasks_ops.py` extraction status ambiguous + D7 INFORMATIONAL rigby_delegation flag OFF + D8 LOW ARCHITECTURE_INDEX §8 timeline drift (S1605/S1606/S1699 missing rows) — all owed to xx99 anchor-update PR.
- **From S1704 §19:** R1 (HIGH) F9 D74 posture decision + R2 (HIGH) F1 trace_id write coverage repair — gating prerequisite for Option B posture evaluation + R3 (HIGH) F4 mining + aggregation pipeline reactivation + R4-R12 additional.
- **From S1704 §14:** D1-D9 owed to xx99 anchor-update PR.
- **From S1703 §19:** R1 (HIGH) F4 PA path AgentExecution coverage + R2 (HIGH) F1 + F2 landmine + docstring cleanup ADR + R3 (HIGH) F6 ToolCallRecord ↔ AgentExecution correlation posture + R4-R10 additional.
- **From S1703 §14:** D1-D6 owed to xx99 anchor-update PR.
- **From S1702 §19:** R1 (HIGH) F2 PA path adoption + R2 (HIGH) F1 multi-model dedup posture + R3 (HIGH) F4 retention posture + R4-R10 additional.
- **From S1702 §14:** D1-D6 owed to xx99 anchor-update PR.
- **From S1701 §19:** R1 (HIGH) task_id ↔ execution_id spine posture is xx99 (S1799) scope + R2-R8 additional.
- **From S1701 §14:** D1 + D2 owed to xx99 anchor-update PR.
- **From S1701 §20.5:** `tools/pa_local.sh` wrapper enhancement to support per-child SIGN pin routing (nice-to-have; not blocking).
- **From Group 1600 (S1699):** T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E; T1 (20 items); T3 CROSS-DOMAIN-EMPLOYEE-ANALOG; cross-arc: Group 1500 T1.h SportsBettingBrief consumer-or-remove + Group 1400 R.B1 OutreachDraft delivery.
- **From Group 1500 (S1599):** T1 R.SPORTS.POSTURE + R.DBAO.CODENAME Chris-gated ADRs; T1 CRITICAL remediation sequences.
- **From Group 1400 (S1499):** T1-T10 unified follow-on queue tier structure (still pending).
- **From Group 1300 (S1399):** 21 follow-on items (still pending).
- **§8 timeline table drift** — missing rows for S1605 Cat E + S1606 Cat F + S1699 xx99 (all Group 1600); owed to follow-up docs PR.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4.

**FIRST THING next session open:**

1. `context-kit orient`
2. Check if S1705 artifact set is on `main`
3. Chris merge + PR merge if not
4. Run post-merge 4-step docs cascade + `build_docs_provenance` per memory rule
5. Verify `service_context: local` via `platform_config_tool overview` on arc pin
6. Mint fresh SIGN isolation pin for S1706 via Rigby `session_tool.create_fresh`
7. Execute S1706 Cat F Adjacent/Separation Boundaries child audit per D72 P6 slot

---

## PA / Rigby context

- **Arc pin at session start:** `pa-e7fbacc996b34b44` (Group 1700 arc pin; in service through Group 1700 close at S1799). `tools/pa_local.sh:128` points at active arc pin — no rotation needed.
- **S1705 SIGN routing:** SIGN-with-edits cycle 1 at Medium/Medium-High confidence (single-batch 4-question) on arc pin `pa-e7fbacc996b34b44` (S1600/S1700/S1701/S1702/S1703/S1704 parent-scoping precedent: arc pin doubles as SIGN pin; fresh SIGN pin `pa-09c46ee3a0d34069` minted per playbook §15 but routed-around by wrapper hard-code — retired at S1705 close per §16 with `updated_count=1, retired=true, previously_active=true`). F1-F7 folds landed pre-commit; single-batch 4-question pattern held clean per D48 22nd arm.
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + arc pin at line 128 currently pointing at Group 1700 active arc pin).
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (D48 22-arc CODIFICATION-READY-STRENGTHENED-EVEN-FURTHER at S1705 close):** S1405+S1406+S1499+S1501+S1502+S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702+S1703+S1704+S1705 22-arc pattern confirmed. **SEVENTEEN-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702+S1703+S1704+S1705 CONFIRMED at S1705 close per single-batch-4-question criterion.** D48 preemptive stability-probe gate 23rd arm anticipated at next-session S1706 child audit open. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.

## Repo state at next-session open

- **Branch state (2026-07-03 post-S1705):** `main` at HEAD (this session's commit). S1705 audit doc + INDEX v48 + OPEN_ARCS + handoff + start-here refresh all landed. Working tree clean; branch off `main` for S1706.
- **Head-commit ledger (2026-07-03 activity, oldest → newest):**
  - `690311df` — PR #2841 S1704 Cat D ToolCallRecord audit
  - `a69d7421` — PR #2842 S1704 cascade artifacts
  - `800fd957` — PR #2843 cross-domain-audit v3 append-only refresh (§14)
  - `09fa83f9` — PR #2844 cross-domain cascade artifacts
  - `a991971a` — PR #2845 start-here mid-arc cross-domain refresh context
  - (this session's commit) — S1705 Cat E audit + INDEX v48 + OPEN_ARCS + handoff + start-here
- **Handoff continuity:** S1705 handoff at `docs/handoffs/SESSION_1705_OBSERVABILITY_CAT_E_OPS_RUN_EVENT_AUDIT.md`. Prior handoffs: SESSION_1704 (Observability Cat D ToolCallRecord); SESSION_1703 (Observability Cat C AgentExecution); SESSION_1702 (Observability Cat B LLMCallEvent); SESSION_1701 (Observability Cat A CeleryTaskEvent); SESSION_1700 (Observability arc-open parent scoping); SESSION_1699 (Content Group 1600 xx99 canonical summary); SESSION_1606 (Content Cat F LAST child); SESSION_1605-1601 (Content Cat E/A/B/D/C children); SESSION_1600 (Content arc-open parent scoping); SESSION_1599 (Sports arc-close canonical summary); SESSION_1506 → SESSION_1500 (Sports arc); SESSION_1499 → SESSION_1400 (Revenue arc); SESSION_1399 (Memory Group 1300 canonical summary).
- **ARCHITECTURE_INDEX version:** v48 (bumped this session with §1.51 S1705 registration + §8 timeline S1705 row + line-6 v48 preamble). Next bump at S1706 child audit close (v48 → v49 with §1.52 S1706 registration).
- **OPEN_ARCS state:** Group 1700 row remains In-progress; current-child updated S1704 → S1705. **S1706 close will trigger Awaiting summary transition preparation** (S1799 xx99 is next after S1706). Group 1600 remains Closed; Group 1500 remains Closed; Group 1400 remains Closed; Group 1300 remains Closed.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Check if S1705 artifact set is on `main`
- [ ] Chris merge + PR merge if not
- [ ] Post-merge 4-step docs cascade + `build_docs_provenance` per memory rule
- [ ] Verify `service_context: local` via `platform_config_tool overview` on arc pin `pa-e7fbacc996b34b44` (D48 23rd arm start)
- [ ] Mint fresh SIGN isolation pin for S1706 via Rigby `session_tool.create_fresh`
- [ ] Execute S1706 Cat F Adjacent/Separation Boundaries child audit per playbook §11.2 20-section template

## Reference — where to look

- **S1705 Cat E audit doc:** `docs/research/domains/observability/1705_observability_cat_e_ops_run_event_audit.md` — playbook §11.2 20-section template FIFTH application under Group 1700; §1.1 F1-F9 lock-in table; §17 F1 0/224 rows execution_id-in-detail (ORM-verified); §17 F2 no execution_id/trace_id/tool_call_id/celery_task_id/task_id columns; §14 F3 4-vs-3 employee count verifier-loop-corrected drift; §7+§9 F4 CTO/COO/Trend Analysis daily fully beat-wired POSITIVE differentiator vs S1704 F4; §9 F5 producer-only canonical role resolution; §15 F6 no-retention; §9+§17 F7 evidence_for_mission ToolCallRecord join empirically broken; §7+§13 F8 MissionRunner I1-I9 all VERIFIED via source + contract test POSITIVE finding; §9 F9 D74 fourth axis cell LATENT-VIABLE-BUT-FLAG-GATED; §19 R1-R12 follow-on queue; §20.6 Rigby SIGN cycle 1 F1-F7 fold notes.
- **S1704 Cat D audit doc:** `docs/research/domains/observability/1704_observability_cat_d_tool_call_record_audit.md`.
- **S1703 Cat C audit doc:** `docs/research/domains/observability/1703_observability_cat_c_agent_execution_audit.md`.
- **S1702 Cat B audit doc:** `docs/research/domains/observability/1702_observability_cat_b_llm_call_event_audit.md`.
- **S1701 Cat A audit doc:** `docs/research/domains/observability/1701_observability_cat_a_celery_task_event_audit.md`.
- **S1700 parent scoping doc:** `docs/research/domains/observability/1700_observability_domain_scoping.md`.
- **S1699 canonical summary doc (fourth §11.3 §10 application):** `docs/research/domains/content/1699_content_canonical_summary.md`.
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.1 parent template + §11.2 child template + §11.3 canonical summary template + §11.3 §10 meta-methodology template + §22 default queue lean).
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` (§8.1 RESEARCH contract + §12.3 "Start Group NNNN" target).
- **ARCHITECTURE_INDEX v48:** `docs/research/ARCHITECTURE_INDEX.md` — S1705 §1.51 + line-6 v48 preamble + §8 timeline S1705 row.
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1700 In-progress row current-child S1705; S1706 close will trigger Awaiting summary transition preparation.
- **Cat F (Adjacent/Separation Boundaries) entry points for S1706:** Six sub-slots per parent §5.F — F.a HeartBeat: `core/models_heart.py:HeartBeat` + `core/services/heart.py` + `core/services/body_vitals.py:run_all_systems_scan`; F.b SLO framework: `core/tasks.py:12492:check_learning_loop_slo`; F.c 14+ event-shaped models: `docs/EVENT_SYSTEM_INVENTORY.md` + S1273 lines 1912-1917 catalog (DeliverableEvent + ImpactEvent + EngagementEvent + TriggerEvent + FleetEvent + CockpitIncidentEvent + CockpitAutopilotEvent + ThreatEvent + ABTestEvent + ConversionEvent + BadContextEvent + RelationshipEvent + AuditLog + NotificationLog); F.d doc-claim verifier: `core/services/doc_claim_verification.py` + `verify_doc_claims` command; F.e Observability↔Event-Architecture terminology boundary.
- **Topic docs:** `docs/topics/employee-os.md` (:64-65 evidence_for_mission gap per S1705 F7); `docs/topics/celery-workers.md` (Cat A entry); `docs/topics/agent-system.md` (Cat C/D entry).
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`.
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`.
- **Cross-domain refresh (mid-arc, 2026-07-03):** `docs/research/platform/cross_domain_integration_audit.md` §14 (line 1977+) — appended v3 refresh log; §14.8 reserved for Group 1700 xx99 close consumption at S1799.

## Doctor warnings to expect

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1705 = FIFTH child under Group 1700; S1706 child + S1799 xx99 anticipated.
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; Group 1700 xx99 anchor-update will surface narrative-anchor gap).
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1705 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`.
- **CLAUDE.md 3-vs-4 employees narrative drift — CONFIRMED via S1705 F3 (ORM-verified 4 handles).** Explicitly owed to xx99 anchor-update PR.
- Group 1400 + Group 1500 + Group 1300 post-arc §7 anchor-updates still pending (inherited).
- Group 1400 + Group 1500 + Group 1600 T1 CRITICAL remediation queues still pending (inherited); Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E blocks 20 T1 items.
- **§8 timeline table drift** — missing rows for S1605 + S1606 + S1699 (Group 1600); owed to follow-up docs PR.
- **5 doc PRs still owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4 (not addressed this session per scope discipline).
- **D48 preemptive stability-probe gate 22nd-arm CONFIRMED CLEAN at S1705 close** — 17-consecutive-fully-clean-arms sub-pattern CODIFICATION-READY-STRENGTHENED-EVEN-FURTHER for playbook v3 §15.
- **Playbook v3 §11.1 template promotion:** CONFIRMED-STRENGTHENED via fourth-application (S1700).
- **Playbook v3 §11.2 template promotion:** FIFTH application under Group 1700 (S1705) CONFIRMED — methodology durable across five child audits in one arc.
- **Arc pin `pa-e7fbacc996b34b44` in service** through Group 1700 close; wrapper rotation NOT owed at next-session open.
- **`tools/pa_local.sh:128` wrapper enhancement** — hard-codes arc pin with no runtime `--conversation` override. Fresh SIGN pins minted for child audits get routed to arc pin (S1600/S1700/S1701/S1702/S1703/S1704/S1705 precedent applies: arc pin doubles as SIGN pin). Nice-to-have follow-up.
