---
session: 1700
status: closed (Group 1700 Observability / Telemetry / SLOs arc OPENED — parent scoping doc landed `status: active` with Chris D69-D74 all locked via "agree all + SIGN" ratification round; Rigby light SIGN cycle 1 SIGN-with-edits at High confidence delivered F1-F6 folds all landed pre-commit — FOURTH application of playbook §11.1 parent template after S1400 first + S1500 second + S1600 third; playbook v3 §11.1 template promotion CONFIRMED-STRENGTHENED via fourth-application; D1-D2-D3 ratified at S1700 open via terminal card; D48 preemptive stability-probe gate 17th arm HOLDING CLEAN through parent SIGN; arc pin `pa-e7fbacc996b34b44` in service; `tools/pa_local.sh:128` rotated; `service_context: local` confirmed; ARCHITECTURE_INDEX v42 → v43 with §1.46 S1700 registration; OPEN_ARCS Group 1700 row MOVED from Not-started §22 queue to In-progress; next session: S1701 Cat A CeleryTaskEvent child audit per D72 P1 slot)
date: 2026-07-02
arc: Research Group 1700 (Observability / Telemetry / SLOs) — arc-open parent scoping session; FIRST session under Group 1700
---

# Session 1700 — Group 1700 Observability / Telemetry / SLOs Arc-Open Parent Scoping (FIRST session under Group 1700)

## What shipped

- **New parent scoping doc:** `docs/research/domains/observability/1700_observability_domain_scoping.md` (~1250 lines post-fold — 1071 pre-fold + ~200 lines added by F1-F6 folds; playbook §11.1 template FOURTH application after S1400 first + S1500 second + S1600 third; F1-F6 folds landed pre-commit; `status: active` Chris-locked).
- **New observability domain directory:** `docs/research/domains/observability/` (mkdir; first sibling under `docs/research/domains/`).
- **ARCHITECTURE_INDEX:** v42 → v43 bump with §1.46 S1700 registration + line-6 preamble bump (v43 preamble preserves prior v42 as "Prior v42 preamble (S1699 xx99 canonical summary)" marker). New §8 timeline row for S1700 arc-open prepended to current-block top. **Documented drift flagged:** §8 timeline missing rows for S1605 Cat E + S1606 Cat F + S1699 xx99 (all Group 1600) — owed to follow-up docs PR per Chris ratification, not in scope for S1700 parent-open.
- **OPEN_ARCS:** Group 1700 row MOVED from Not-started §22 queue to In-progress (before Group 1600 Closed row per newer-at-top convention). Not-started §22 queue row for Group 1700 struck through with pointer to In-progress detail. Line-6 preamble bumped S1699 close → S1700 open; prior S1699 preamble preserved.
- **Wrapper rotation:** `tools/pa_local.sh:128` rotated from retired Group 1600 arc pin `pa-f52acf3f8d394faa` to new Group 1700 arc pin `pa-e7fbacc996b34b44`. Retirement history comment expanded with Group 1600 retirement note.
- **Rigby light SIGN cycle 1:** SIGN-with-edits at High confidence via arc pin `pa-e7fbacc996b34b44` (parent stage precedent: arc pin doubles as SIGN pin per S1600 pattern). 4 pressure-test questions batched in single turn (no worker instability observed — D48 17th arm HOLDING CLEAN). Verdicts: Q1 CONFIRM High (parent-vs-single verdict); Q2 3 sub-verdicts (CONFIRM Medium-High + FLAG-EDIT Medium + FLAG-EDIT Medium); Q3 3 sub-verdicts (CONFIRM High + MUST-FIX High + CONFIRM Medium-High); Q4 MUST-FIX High + FLAG-EDIT Medium. **F1-F6 folds all landed pre-commit:**
  - **F1** — Cat C boundary rule: added sentence "P3 MUST identify the actual write path(s) and canonical table/class used at runtime at HEAD; ADR to remove/merge the deprecated 2 is explicitly out-of-scope for P3 and belongs to post-arc T-slot."
  - **F2** — Cat F internally sub-slotted into F.a Body Systems / HeartBeat + F.b SLO framework audit + F.c Event-model catalog + WRITE-ONLY-FORGOTTEN audit + F.d Doc-claim verifier drift + F.e Observability↔Event-Architecture terminology boundary; each sub-slot has explicit stop condition.
  - **F3** — Cat B ↔ Cat D accounting rule added: "LLM calls made from inside a tool invocation remain Cat B, regardless of caller; Cat D never attempts to 'own' LLM cost — dedup is performed via correlation keys (execution_id + trace_id + tool_call_id)."
  - **F4** — P5 dependency clause changed from "Depends on P1 + P3 + P4" to "Depends on P1 + P2 + P3 + P4" (F4 MUST-FIX: mission-scoped LLM cost aggregation requires P2 evidence).
  - **F5** — New §5 "Correlation primitives (working definitions — HYPOTHESIS-TO-BE-VERIFIED)" box with 5 primitives (task_id / execution_id / trace_id / tool_call_id / mission_id), each with working definition + which child audit verifies. Load-bearing rule for xx99 §5 posture-decision brief added: "if P1+P2 discover execution_id is scope-single-LLM-call at HEAD, D74 posture resolves in favor of canonical unification; if execution_id already spans agent-tool-LLM sequences, structural separability remains viable — xx99 does NOT select posture; correlation-primitive evidence goes into §5 evidence brief for Chris-gated ADR post-arc."
  - **F6** — §7 anti-scope items 19/20/21 added: Frontend/WebSocket/client telemetry + Auth token/external-integration telemetry + "RigbyTelemetry" or any new observability layer buildout (bounds activation of currently-disabled Rigby v0 intake explicitly OUT of audit scope).
- **Chris D-decisions locked:**
  - **D1** (S1700 open via terminal card) — Group 1700 = Observability confirmed per playbook §22 default lean + OS §12.3 target.
  - **D2** (S1700 open via terminal card) — Delegate event architecture (event bus, routing, schema versioning) to Group 1900.
  - **D3** (S1700 open via terminal card) — Parent-only this session; P1 CeleryTaskEvent audit kicks off next-session.
  - **D69** — Parent shape PARENT-WITH-CHILDREN 6-child arc (P1 Cat A + P2 Cat B + P3 Cat C + P4 Cat D + P5 Cat E + P6 Cat F + P7 xx99 canonical summary).
  - **D70** — Six categories A–F with boundary rules per §3 (Cat C 3-class landmine caught + F1 boundary sentence added; Cat F sub-slotted per F2; Cat B/D accounting rule per F3).
  - **D71** — Delegation boundary with Group 1900 explicit: "Observability owns producer-side telemetry contract completeness; Event Architecture owns cross-domain event routing."
  - **D72** — Child sequence P1→P2→P3→P4→P5→P6→P7 sequential per §5 with F10 dependency clauses embedded (P5 depends-on-P2 explicit per F4 MUST-FIX).
  - **D73** — Posture-decision framing = evidence plan NOT recommendation (xx99 does NOT select; Chris-gated post-arc ADR resolves D74 axis).
  - **D74** — Arc lens question locked: "Are the 5 execution-telemetry layers structurally separable (each layer owns a distinct concern with lightweight FK correlation), OR do they need canonical unification (single execution_id + trace_id spine spanning task→LLM→agent→tool→ops with unified write path)?" — evidence-plan framing only; F5 correlation-primitives box makes the load-bearing sub-question explicit (is execution_id spine-shaped or single-call-scoped at HEAD?).
- **Session close artifacts committed at S1700 close:**

```
docs/research/domains/observability/1700_observability_domain_scoping.md    [new; parent scoping doc; F1-F6 folds landed pre-commit; ~1250 lines; FIRST session under Group 1700]
docs/research/ARCHITECTURE_INDEX.md                                          [modified — v42 → v43; §1.46 registration + line-6 preamble bump + §8 timeline row]
docs/research/OPEN_ARCS.md                                                   [modified — Group 1700 row MOVED from Not-started to In-progress; line-6 preamble bump]
tools/pa_local.sh                                                            [modified — line-128 rotated to arc pin pa-e7fbacc996b34b44]
docs/handoffs/SESSION_1700_OBSERVABILITY_ARC_OPEN.md                        [new — S1700 handoff]
00-START-NEXT-SESSION.md                                                     [modified — this session close; next-session first-things Chris-gated at S1701 open]
```

## Key findings (per playbook §11.1 parent-scoping structure)

### §1 Why Phase 0

- Fourth application of Chris's Phase 0 F.i/F.ii/F.iii 3-step methodology (Domain Definition / Existing Knowledge Inventory / Success Criteria). Playbook v3 §11.1 promotion TRIGGERED at S1599 close; CONFIRMED-STRENGTHENED via S1699 fourth-application meta-methodology; Group 1700 methodology unchanged for four-consecutive-application confirmation.
- OS §12.3 "Start Group NNNN: Observability" target block explicitly names Observability as the exemplar arc-open command with 6-child suggested sequence. Chris typed the short command "Start research group 1700" — the FIRST library invocation matching OS §12.3 target verbatim.
- Three failure modes bounded at Phase 0: (i) scope-confusion between execution-telemetry and event-architecture (D2 bounds event bus OUT); (ii) AgentExecution 3-class landmine at HEAD 2b7dbd89 caught via parent verifier-loop grep (`intelligence/models/agent_execution.py:11` + `intelligence/models.py:587` + `core/models_unified_system.py:882` with stale S287 deprecation notice); (iii) Rigby v0 intake DISABLED (`RIGBY_EVENT_INTAKE_ENABLED=False` per S1273 line 1959) — bounded OUT of scope-magnet risk per §7 item 21 F6-fold.

### §3 Candidate subdomain taxonomy — six categories A–F

- **Cat A — Task/Worker Execution Telemetry** (`CeleryTaskEvent`); Celery signal-handler boundary; consumers = 3 PA tools; retention = 30 days default; baseline coverage = 415 tasks × 92 beat schedules.
- **Cat B — LLM Call Telemetry** (`LLMCallEvent`); S1098 llm_call_wrapper boundary; 6 LLM providers; cost + token + latency tracking.
- **Cat C — Agent Execution Telemetry** (`AgentExecution` — 3-class landmine catalogued); F1-fold boundary rule: P3 identifies canonical + deprecation ADR out-of-scope.
- **Cat D — Tool Call Telemetry** (`ToolCallRecord`); S970 BaseAgent auto-wrap; S1115 all-return-path fix; F3-fold Cat B/D accounting rule for LLM-in-tool calls.
- **Cat E — Ops/Mission Telemetry** (`OpsRun` + `OpsRunEvent`); S1250 PR3 introduction; MissionRunner integration reality check owed; WRITE-ONLY-FORGOTTEN detection per Group 1500 §14.3 precedent.
- **Cat F — Adjacent/Separation Boundaries** (F2-fold sub-slotted): F.a Body Systems / HeartBeat + F.b SLO framework audit + F.c Event-model catalog + F.d Doc-claim verifier drift + F.e Observability↔Event-Architecture terminology boundary. Each sub-slot has explicit stop condition.
- **21-item explicit non-candidates/anti-scope** (§3 + §7 combined): event bus/schema (Group 1900); DeliverableEvent consumer wiring (Group 1600 T0/Gate); Memory learning-loop internals (Group 1300 closed); Content Deliberation retry policies (Group 1600); Sports betting pattern types (Group 1500 closed); Revenue outreach delivery re-scope (Group 1400); Employee OS mission runner refactor; PA tool surface unification (Group 1600 Cat E LOCKED); BaseAgent refactor; AI provider selection; Body Systems cold-start reliability fix; Fleet application observability; Historical arc T-slot inheritance; Doc-claim verifier bug fixes; Governance Ratification Ledger observability; Rigby SIGN worker-instability D48 pattern investigation; AGENT_MAP agent retirement audit; **Frontend/WebSocket/client telemetry (F6 fold add)**; **Auth token/OAuth telemetry (F6 fold add)**; **"RigbyTelemetry" or any new observability layer buildout (F6 fold add)**.

### §4 Parent-vs-single verdict = PARENT-WITH-CHILDREN

Four evidence bullets per playbook §2 STAGE 0 criteria: (1) multi-substrate domain (5 execution-telemetry layers + HeartBeat + SLO + 14+ event-shaped adjacent + Ops Autopilot); (2) runtime surface exceeds single-audit capacity (415 tasks × 92 beat + 6 providers + 74 agents + 113 PA tool schemas + OpsRun + 9 body systems); (3) load-bearing dedup question requires per-child evidence before xx99 synthesis; (4) cross-arc handoffs owe per-child evidence to Group 1900 + Employee OS + closed Groups 1300/1400/1500/1600. Alternative "single-audit-then-defer" rejected per §4 as scope-abandonment (deferring 4 of 5 layers abandons S1273 §5.13 named mission scope).

Rigby SIGN Q1 verdict: CONFIRM (High) — no fold required.

### §5 Child mission sequence P1→P7

Six children + P7 xx99, sequential per D72 with explicit F10 dependency clauses embedded in rationale column:

- **P1 S1701 Cat A CeleryTaskEvent** — first child, no inbound deps; canonical execution boundary.
- **P2 S1702 Cat B LLMCallEvent** — depends on P1 execution_id contract; audits 6 providers + rogue-caller detection + cost accounting.
- **P3 S1703 Cat C AgentExecution** — depends on P1+P2; **catalogs 3-class landmine (boundary discipline: catalog + name canonical; deprecation ADR post-arc T-slot per F1 fold)**.
- **P4 S1704 Cat D ToolCallRecord** — depends on P1+P3; S1115 all-return-path regression check on 74 enabled agents.
- **P5 S1705 Cat E OpsRunEvent** — **depends on P1+P2+P3+P4** (F4 MUST-FIX fold: P2 explicitly added for mission-scoped LLM cost aggregation semantics).
- **P6 S1706 Cat F Adjacent/Separation** — depends on P1-P5 evidence base; internally sub-slotted F.a-F.e per F2 fold.
- **P7 S1799 xx99 canonical summary** — consumes P1-P6; **FIFTH application of playbook §11.3 §10 meta-methodology template** after S1399 first + S1499 second + S1599 third + S1699 fourth; §5 posture-decision evidence brief on D74 axis (structural-separability vs canonical-unification via execution_id/trace_id spine).

**F5 correlation-primitives box added at §5 head** with 5 HYPOTHESIS-TO-BE-VERIFIED primitives (task_id / execution_id / trace_id / tool_call_id / mission_id), each mapped to verifying child audit.

### §8 D-decisions locked

D69-D74 all locked via Chris "agree all + SIGN" round. SIGN-with-edits at High confidence delivered F1-F6 folds all landed pre-commit; no D-verdict override or edit required. Status flipped draft → active same-commit.

### D48 preemptive stability-probe gate 17th arm

HOLDING CLEAN through parent SIGN: 4-question single-batch on new arc pin `pa-e7fbacc996b34b44`; no worker instability observed. Extends 11-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699 → **TWELVE-CONSECUTIVE-FULLY-CLEAN-ARMS SUB-PATTERN S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700 CONFIRMED per batch-processing criterion**. Codification-ready-STRENGTHENED-FURTHER for playbook v3 §15.

### AgentExecution 3-class landmine cataloged

Independent parent-Claude verifier-loop grep at HEAD `2b7dbd89` confirmed 3 `class AgentExecution` definitions:
- `intelligence/models/agent_execution.py:11` — ActionPlan-scoped canonical per S1273 §3.25 mention.
- `intelligence/models.py:587` — duplicate class body, same fields, ActionPlan-scoped.
- `core/models_unified_system.py:882` — DEPRECATED per docstring ("Use agents.models.AgentExecution instead. This model is deprecated as of Session 287"). Docstring points at `agents.models` — but per S391 comment (`agents/models.py`), that path is now a compatibility shim to `core/models/agents_registry/` which contains no `AgentExecution` class. **Deprecation notice is stale/wrong at HEAD.** P3 Cat C boundary discipline (F1 fold): catalog + name canonical + define correlation contract; deprecation ADR is post-arc T-slot per §6.3 parked candidate.

## Notes on process

- **First library parent scoping doc to open on FIRST short-command invocation matching OS §12.3 target verbatim** — "Start research group 1700" → "Start Group NNNN: Observability" OS exemplar.
- **First library parent scoping doc to catalog a live model-class landmine (3-class AgentExecution) as scope-magnet risk with boundary discipline** — precedent for future domains with model-duplication.
- **First library parent scoping doc where D2 delegation boundary is ratified at Chris terminal card pre-parent-draft** (event architecture to Group 1900 delegation confirmed before parent §3/§4/§5 authored) — cleaner boundary demarcation than Group 1600 D65e-late-emergence pattern.
- **First library parent scoping doc where light SIGN was routed same-session pre-Chris-lock** — Chris ratified "agree all + SIGN" as ratification round; parent SIGN delivered 2 MUST-FIX + 4 FLAG-EDIT folds landed pre-commit before status flipped active. Precedent: Group 1600 landed 12 folds via SIGN cycle 1→2 but folds landed post-Chris-lock; Group 1700 F4 (P5 dep) + F5 (correlation primitives box) landed pre-lock and shaped the anchored evidence base.
- **First library parent scoping doc to introduce F5-style "correlation primitives working-definitions HYPOTHESIS-TO-BE-VERIFIED" box** — codify-ready candidate for playbook v3 §11.1 template addition. If Chris ratifies at xx99, this becomes the sixth codify-ready candidate for v3 (extending S1699 §10.2 seven candidates).

## Repo state at S1700 close

- Branch: `main` clean at S1700 open (`2b7dbd89`); S1700 close artifact set commits to fresh branch `docs/session-1700-observability-arc-open` — PR opens to `main` on push.
- ARCHITECTURE_INDEX version: v42 → v43 (bumped this session).
- OPEN_ARCS state: Group 1700 In-progress; Group 1600 remains Closed; Group 1500 remains Closed; Group 1400 remains Closed; Group 1300 remains Closed.
- Handoff continuity: S1699 → S1700. Next: S1701 Cat A CeleryTaskEvent child audit per D72 P1 slot.

## Doctor warnings to note

- Inventory freshness (unchanged this session — research doc; no runtime changes).
- Handoff numbering continuity — S1700 opens Group 1700 numbering (S1700 arc-open parent + anticipated S1701-S1706 children + S1799 xx99).
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 remains older than latest handoff (informational; Group 1700 will add narrative touchpoints at xx99 if Chris ratifies).
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1700 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`.
- CLAUDE.md 3-vs-4 employees narrative drift — still flagged; awaits subsequent `verify_doc_claims --only-drift` verifier PR (inherited from S1499 §7.2 fold).
- Group 1400 + Group 1500 + Group 1300 post-arc §7 anchor-updates still pending (inherited).
- Group 1400 + Group 1500 + Group 1600 T1 CRITICAL remediation queues still pending (inherited); Group 1600 T0/Gate R.CONTENT.XX99-ADR-BUNDLE-D65A-D65B-D65C-D65E blocks 20 T1 items.
- **5 doc PRs owed** for `auto_publish "daily 6 AM"` cross-arc CORRECTION per S1699 §7.4 (still open — not addressed this session per scope discipline).
- **§8 timeline table drift** flagged in the S1700 timeline row body: missing rows for S1605 Cat E + S1606 Cat F + S1699 xx99 (all Group 1600). Follow-up docs PR owed per Chris ratification.
- **D48 preemptive stability-probe gate 17th-arm CONFIRMED at S1700 close** — 12-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700 CODIFICATION-READY-STRENGTHENED-FURTHER for playbook v3 §15.
- **Playbook v3 §11.1 template promotion:** CONFIRMED-STRENGTHENED via fourth-application (S1700). Group 1700 methodology unchanged from S1600. Formal codification into v3 docs is a separate follow-up per Chris ratification.
- **Wrapper pin rotation done at `tools/pa_local.sh:128`** — currently at Group 1700 arc pin `pa-e7fbacc996b34b44`; next rotation owed at Group 1700 close (S1799 xx99 canonical summary) → future Group 1800.

## Next mission — S1701 Cat A CeleryTaskEvent child audit (Chris-gated)

Per D72 P1 slot + D3 next-session cadence: **S1701 Cat A audit** — Task/Worker Execution Telemetry (`CeleryTaskEvent`).

Cat A canonical questions the child audit gathers evidence for:
- Does signal handler at `core/celery_telemetry.py:74-177` cover all task states across all workers?
- Is the agent_name dimension (Session 1169) retroactively defensible or backfill-incomplete?
- What is observed-vs-configured retention window at HEAD (`CELERY_TASK_EVENT_RETENTION_DAYS` default 30)?
- What is the monitor-task overhead spiral risk (Session 1167 precedent)?
- What is the observability-of-observability meta answer per parent §2.7?

Per F5 correlation-primitives box (`task_id` primitive row): P1 verifies task_id coverage completeness + retention — grounding for downstream P2-P5 execution_id correlation contract.

Playbook §11.2 20-section child audit template + 6-parallel-Explore sub-agents per §13 + parent-Claude verifier-loop per §14. **Required full Rigby SIGN cycle 1** per playbook §15 stage table child row (not optional light SIGN — child audit is research finding not scoping deliverable). Use fresh SIGN isolation pin per playbook §15 promoted rule (arc pin `pa-e7fbacc996b34b44` continues as arc context; SIGN pin fresh per child).

D48 preemptive stability-probe gate 18th arm anticipated at S1701 open on arc pin. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply per child audit shape.
