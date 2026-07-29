# Next Session — Start Here

---

## READ THIS — SESSION 3037 CLOSED. **First execution of the A1 Reliability Audit wedge, shipped on ourselves.**

S3037 executed the Reliability Audit v0 methodology (that Rigby scoped for herself at S2951 ~85 sessions ago) against Donkey Betz. **5 audit deliverables, 15 findings, 10-item remediation backlog** — of which **5 items shipped this session** (A1 + A2 + A6 + S4 + S5). Real reliability bugs surfaced, real fixes shipped, wedge proven.

**HEAD at close:** filled at cascade merge (post-`ced5b7ea0`).

### Two code PRs shipped

- **PR #3767 (`690ba8c6a`)** — `fix(s3037-a6): AGENT_MAP fallback fail-loud in workflow orchestrator`. Surfaces actual Python exception + agent_name + duration_ms on falsy `router.route` success instead of "Unknown error" fallback. Tomorrow's morning_brief failure will carry a real exception in the escalation deliverable's `error_tail`.
- **PR #3768 (`ced5b7ea0`)** — `feat(s3037-s4): cleanup_stale_ops_runs Celery beat task`. Mirrors AgentExecution 60-min cleanup pattern for OpsRun. Discharges "no lost dispatches" reliability rule violation. Beat live and scheduled `*/10 * * * *` on broadcast queue.

### Three in-session ORM fixes

- **A1** — 2 orphaned OpsRun rows (16d + 18d stuck) manually recovered
- **S5** — S3036 Chief of Staff Escalation `de861fe2-…` reopened with contradicting evidence (WiFi mis-attribution invalidated)
- **A2** — Chris `AutonomyConfiguration` row created (id `6d4aef2d-…`) — fills the Step 4 governance-artifact gap

### Rigby Tool Gap Ledger — 3rd trigger appended

Rigby persistence-gap (dispatches run tool_runs, don't persist deliverable) logged on `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`. Discharge path = S8 (30-45 min, WEDGE-BLOCKING).

---

## Audit artifacts (all in Donkey Betz workspace `b4503364-…`)

| Deliverable | Content |
|---|---|
| `aec0e6da-b2b4-4d28-8cca-b69da920b1f4` | Scope Card (Step 1) |
| `361e8209-c24c-4401-8a3d-f5387f972dea` | Step 2 — Telemetry Pull & Failure Signature Sweep |
| `ce9ca37b-c544-4672-be9f-5b29e14aa59d` | Step 3 — Tool Reliability Matrix |
| `1ac5f0dc-aa09-44da-8353-dea3e3cbdc2e` | Step 4 — Governance Posture |
| `c3cad098-6d29-447f-b949-456913f7d343` | Step 6 — Remediation Backlog (10 items) |

---

## S3038 primary directive candidates

**No forced pick — Chris picks fresh.** 5 remediation-backlog items still open:

### Highest-leverage remaining (from Step 6 deliverable)

- **S8** (30-45 min, **WEDGE-BLOCKING** cheap win) — Instrument `deliverable_tool.create` to isolate Rigby persistence-gap root cause. This is what blocks selling the wedge to a paying customer. Test with minimum-scope dispatch (single tool call, no exploration allowed) as first probe.
- **A3** (45-60 min, QUICK WIN) — Backfill `LLMCallLog.error_type` from `error_message` via regex classifier + save() hook. Closes silent-monitoring gap surfaced in Step 4.
- **A6 Phase 2** — Watch tomorrow's 7:00 AM MDT morning_brief run. If it fails, the escalation deliverable will now carry a real Python exception type (via PR #3767 fix). That's the trigger to root-cause the underlying bug in `lane_1_platform_readiness`. If it passes, note as "intermittent conditions cleared" and monitor.
- **S7** (~1 session, CRITICAL) — Root-cause ThinkingAgent 67% async failure. Instrument each ORM call site in `.think()`.
- **S9** (~1 session, HIGH) — Wire downgrade/fallback logic to populate `was_downgraded` / `was_fallback` fields on `LLMCallLog` that S2853 shipping claim implied. Right now 39,971 calls / 30d show zero downgrades.

### Also open (not from audit backlog)

- **`typing.Literal[actor]` enforcement** on emit helpers (S3036 T1 Fold future_trigger)
- **Actor-taxonomy vs frontend-palette drift guard** (S3036 A2 Fold future_trigger)
- **S3033 Fold B** ledger-persistence timing (watch for 3rd trigger)
- **S3030 prod deploy carry** — `backfill_canonical_drift --apply` on Railway prod
- **S3031 Fold B** spy fragility
- **S3032 Fold E** — `orm_inspect_tool` allowlist accretion pattern
- **S3034 A2 Fold** (subscriber wire-contract fragility) — carry preserved

### Chris's own priority (supersedes all above)

**Joint recommendation:** if unsure, **S8** is the cheapest strategic win of the audit backlog — 30-45 min instrumentation that unblocks selling the wedge. Alternatively, **A3** if you want another quick governance improvement in the same shape as A2.

**Standard opener:**
1. `context-kit orient` (auto-injected)
2. Absorb this file + MEMORY.md + CLAUDE.md
3. Read S3037 handoff (`docs/handoffs/SESSION_3037_RELIABILITY_AUDIT_V0_A6_S4_A2.md`)
4. Read audit remediation backlog (`c3cad098-6d29-447f-b949-456913f7d343` — 10 action items with PLAYBOOK-format ratification for top 3)
5. Ask Chris: "What would you like to work on?"
6. Optional state probes:
   - `git log --oneline -8` — should show `ced5b7ea0` (S4) + `690ba8c6a` (A6) on top of the S3036 cascade
   - `python manage.py shell -c "from django_celery_beat.models import PeriodicTask; print(PeriodicTask.objects.filter(task='core.tasks.cleanup_stale_ops_runs').first())"` — should show the new task
   - Check today's morning_brief run (fired at 7:00 AM MDT) — if failed, escalation deliverable now carries real exception in `error_tail`

---

## S3038 carry-forward seeds

### New from S3037

- **S8 (Rigby persistence-gap instrumentation)** — 3rd trigger logged to Tool Gap Ledger; wedge-blocking
- **A6 Phase 2 watch** — tomorrow's morning_brief failure now surfaces real exception; root-cause when it fires
- **AutonomyConfiguration** row now exists — monitor for cases where autonomy caps trip (require_approval_above=$25); tune if too tight
- **Wedge lessons applied to future customer pilots** — Snapshot underpriced at $500; hybrid execution (Rigby+Claude) needed until S8 fixed; mis-attribution catches are highest-value class

### Elevated from S3036

- **T1 Fold future_trigger (typing.Literal[actor])** — still 1st trigger
- **A2 Fold future_trigger (actor-taxonomy vs frontend-palette drift)** — still 1st trigger

### `did_X` semantics — 2nd trigger status preserved from S3034

- Watch for 3rd `did_X` method to codify as Playbook rule

### Carried from prior arcs — status preserved

- **S3033 Fold B** — ledger persistence timing (1st trigger discharged; watch for 3rd)
- **S3030 prod deploy carry** — `backfill_canonical_drift --apply` on Railway prod
- **S3032 Fold E** — `orm_inspect_tool` allowlist accretion
- **S3031 Fold B** — spy fragility
- **S3034 A2 Folds** (subscriber wire-contract fragility + adjacent-axis superseded/experiment as terminal states) — carried

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook **v0.11.0** (S3037 audit + fixes are net-new + bug fixes; PLAYBOOK-7.7.5 does not fire; no amendment this session).
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **2× Flow B spec→ship** (A6 PR #3767, S4 PR #3768). Spec = audit remediation-backlog items.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **N/A** — direct Claude-execute-and-verify shape used per S2988 precedent for ad-hoc bug fixes with unambiguous design.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Applied to every mid-flight decision routing (tier selection, workflow picks, execution mode, Step 5 skip, remediation ordering, close-readiness path).
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` after each merge. Events recorded in `logs/recycle_events.jsonl` sha=690ba8c6af90, sha=ced5b7ea01b6.
- **Verify-before-build (Cycle 1A):** **22nd consecutive session** — A6 verified S1234 D1 pattern before mirror; S4 verified `_impl_cleanup_stale_agent_executions` pattern before mirror.

---

## Wrapper pin note

Active PA conversation pin at S3037 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S3037 is the first arc to fully execute the A1 wedge on ourselves. 3 shipped remediations (A6/S4/A2) + 2 in-audit quick wins (A1/S5) + Rigby Tool Gap Ledger 3rd-trigger logged. The wedge is real; the biggest remaining blocker to selling it is S8 (Rigby persistence-gap instrumentation, 30-45 min).
