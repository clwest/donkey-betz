# Next Session — Start Here

---

## READ THIS — SESSION 3038 CLOSED. **S8 instrumentation + A3 classifier shipped. S3039 first action = S7 (ThinkingAgent root-cause).**

S3038 shipped two S3037-backlog remediations back-to-back on a two-PR slate: **S8** (WEDGE-BLOCKING instrumentation for the Rigby persistence-gap) and **A3** (LLMCallLog `error_type` auto-classifier + backfill). Both merged and recycled; 305 historical rows tagged; 3 remediation items remain from the S3037 backlog.

**HEAD at close:** filled at cascade merge (post-`80ac66499`).

### Two code PRs shipped

- **PR #3770 (`a29085b38`)** — `feat(s3038-s8): instrument deliverable_tool.create for persistence-gap isolation`. Paired `[PA_DELIVERABLES_INTENT]` + `[PA_DELIVERABLES_ENVELOPE]` log lines sharing `trace_id` with existing `[PA_TASK_SUMMARY]`. Cross-referencing the three signatures against `Deliverable` rows classifies the failure mode deterministically next time it fires. **Diagnostic finding:** ORM sweep of the S3037 audit window shows zero `pa_deliverables_tool` rows — the handler was never reached, so the fix is upstream (PA loop / prompt convergence). Validated with 4 synthetic dispatches, all persisted.
- **PR #3771 (`80ac66499`)** — `feat(s3038-a3): auto-classify LLMCallLog.error_type from error_message`. Pure regex classifier (11 patterns + `unknown_error` fallback), `LLMCallLog.save()` pre-persist hook (respects caller intent, fail-open), `manage.py backfill_llm_error_types [--apply]`. Backfill applied: **305/305 historical rows → `connection_error`**.

### One in-session artifact update

- **Rigby Tool Gap Ledger** (`5c84e75a-…`) — S8 discharge note appended (1,478 chars). 3rd trigger status flipped `open → mitigated`.

---

## S3039 primary directive (Chris's ratified pick)

**S7 — Root-cause `ThinkingAgent` 67% async failure.** ~1 session estimate. CRITICAL classification per S3037 Step 6 backlog.

**Approach:**
- Instrument each ORM call site in `.think()` — where does the sync/async boundary get crossed?
- Look for `SynchronousOnlyOperation` errors in an async context — the most likely shape is a missing `sync_to_async` wrapper at an ORM boundary.
- 67% failure rate is high enough that a rerun should reproduce quickly; if flaky, use `--iterations 10` on any exec harness to force the failure signature.
- S3037 Step 3 (Tool Reliability Matrix `ce9ca37b-…`) probably has the initial trace evidence — read it first.

**Standard opener:**
1. `context-kit orient` (auto-injected)
2. Absorb this file + MEMORY.md + CLAUDE.md
3. Read S3038 handoff (`docs/handoffs/SESSION_3038_S8_INSTRUMENTATION_A3_CLASSIFIER.md`)
4. Read the S7 line item in `c3cad098-6d29-447f-b949-456913f7d343` (S3037 audit remediation backlog Step 6) AND the ThinkingAgent findings in `ce9ca37b-c544-4672-be9f-5b29e14aa59d` (Step 3 Tool Reliability Matrix)
5. Optional state probes:
   - `git log --oneline -8` — should show `80ac66499` (A3) + `a29085b38` (S8) on top of the S3037 cascade
   - `python manage.py shell -c "from core.models_llm_routing import LLMCallLog; print(LLMCallLog.objects.filter(agent_name='ThinkingAgent', success=False).values('error_type').annotate(from django.db.models import Count; n=Count('id')).order_by('-n')[:10])"` — check current error_type distribution for ThinkingAgent post-A3-backfill
   - Trigger a fresh ThinkingAgent run to capture new INTENT/ENVELOPE + new `error_type` on any failure

---

## S3039 carry-forward seeds

### New from S3038

- **S8 instrumentation live** — next time `pa_deliverables_tool` source rows are missing for a dispatch that expected persistence, grep `celery-pa.log` for `PA_DELIVERABLES_INTENT trace_id=X` vs `PA_TASK_SUMMARY trace_id=X` to classify the failure mode.
- **A3 classifier live** — every new failed LLMCallLog auto-tags `error_type`. Monitor for `unknown_error` fallbacks (signal to widen the pattern table).
- **Rigby persistence-gap** — status = mitigated (instrumentation shipped). Next occurrence definitively diagnosable. Do NOT re-log to Tool Gap Ledger unless it fires and instrumentation catches it.

### Remaining audit backlog (from S3037 Step 6)

- **S7** (~1 session, CRITICAL) — ThinkingAgent 67% async failure. **S3039 first action.**
- **S9** (~1 session, HIGH) — Wire `was_downgraded` / `was_fallback` / `was_auto_selected` telemetry on LLMCallLog. S2853 shipping claim not empirically visible.
- **D10** (multi-session, DEFERRABLE) — Historical `LLMCallLog.workspace` backfill for 34,049 NULL rows. Reporting quality, not runtime.
- **A6 Phase 2** — Root-cause `lane_1_platform_readiness` underlying bug now that PR #3767 surfaces real exception. Trigger-driven; wait for next morning_brief failure.

### Carried from prior arcs — status preserved

- **T1 Fold future_trigger (typing.Literal[actor])** — 1st trigger (S3036)
- **A2 Fold future_trigger (actor-taxonomy vs frontend-palette drift)** — 1st trigger (S3036)
- **`did_X` semantics** — 2nd trigger (S3034); watch for 3rd
- **S3033 Fold B** — ledger persistence timing (1st trigger discharged; watch for 3rd)
- **S3030 prod deploy carry** — `backfill_canonical_drift --apply` on Railway prod
- **S3032 Fold E** — `orm_inspect_tool` allowlist accretion
- **S3031 Fold B** — spy fragility
- **S3034 A2 Folds** — subscriber wire-contract fragility + adjacent-axis superseded/experiment

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook **v0.11.0** (S3038 is remediation-shipping; PLAYBOOK-7.7.5 does not fire; no amendment this session).
- **ADR corpus:** ADR-0001 through ADR-0008.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **2× Flow B spec→ship** (S8 PR #3770, A3 PR #3771). Spec = audit remediation-backlog items.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **N/A** — direct Claude-execute-and-verify shape per S2988 precedent for ad-hoc remediation with unambiguous design.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Applied to session-open recommendation, A3 slide-in ask, close-cascade routing.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` after each merge. Events recorded in `logs/recycle_events.jsonl` sha=a29085b38ba4, sha=80ac6649965a.
- **Verify-before-build (Cycle 1A):** **23rd consecutive session** — S8 verified handler shape before instrumenting; A3 verified no existing LLMCallLog signal before choosing `save()` override + verified `backfill_*` naming before creating command.

---

## Wrapper pin note

Active PA conversation pin at S3038 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S3038 shipped 2 remediation PRs from the S3037 audit backlog. 5 of 10 original items now discharged (A1/A2/A6/S4/S5 at S3037; S8/A3 at S3038). 3 remain (S7/S9/D10) plus A6 Phase 2 trigger-driven. S7 is next.
