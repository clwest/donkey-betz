# SESSION 2933 — A3 v1: Signal-triggered agent auto-dispatch

**Date:** 2026-07-24
**Merge SHA:** `68705a69e`
**PR:** [#3501](https://github.com/clwest/donkey-betz-platform/pull/3501)
**Shape:** Net-new engineering — 1,061-line insert-only diff (1 new model + 1 new service + 1 new task module + 20 tests + migration + manage command). ~90 min end-to-end.
**Ratification:** Chris "proceed with A3" (arc scope) + Chris "Proceed with Path 2" (code-defined mapping shape after Rigby zoom-out on rule-metastasis risk).

---

## What shipped

New reactive-orchestration primitive. Celery beat `scan-signal-dispatch-rules` fires every 5 min, scans code-defined `(SignalCluster.pattern_type → AGENT_MAP agent)` rules, enqueues one `dispatch_agent_for_signal_cluster` task per matching active cluster, and records the outcome in the new `SignalDispatch` audit table.

**v1 hard-coded rules** (`core.services.signal_dispatch_service.SIGNAL_DISPATCH_RULES`):

| Rule key | pattern_type | Agent | min_strength | min_confidence | max_per_day |
|---|---|---|---|---|---|
| `trend_emergence__trend_analysis` | `trend_emergence` | `TrendAnalysisAgent` | 0.5 | 0.5 | 10 |
| `content_gap__content_strategy` | `content_gap` | `ContentStrategyAgent` (post-S2932 fail-loud gate) | 0.5 | 0.5 | 10 |

**Path B ratified over Path A after Rigby zoom-out (S2933 SIGN Q6ii):** the mapping table is a Python constant, not a DB config row. The only DB row is `SignalDispatch` — audit / observability only. No admin editing surface in v1 to prevent the "rules-multiply-in-DB-rows" metastasis pattern. Migration path documented if we ever need runtime editing: `INSERT` dict values as rows + wire admin (est. ~1 hour).

**Safety nets per Rigby SIGN Q6i:**
- Global `SIGNAL_DISPATCH_MAX_PER_SCAN` cap (default 10, `settings`-overridable) — hard stop against dispatch storms.
- Per-rule `max_per_day` cap enforced by counting `SignalDispatch(rule_key=R, dispatched_at__gte=24h_ago)`.
- Gate on `SignalCluster.is_actionable` (status='active' AND strength ≥ 0.5 AND confidence ≥ 0.5) + rule's own floors.
- `SIGNAL_DISPATCH_ENABLED` kill switch (default True).

**Fire-once semantics per Rigby SIGN Q3 (F-BLOCKING constraint):**
- `SignalDispatch.outcome` + `error_summary` populated at dispatch-time — transient failure never strands a cluster silently.
- Dedup: succeeded/queued dispatch blocks re-fire for same (cluster, rule_key); a `failed` outcome does NOT block, so scanner naturally retries.
- Bounded manual retry: `python manage.py resend_signal_dispatch --dispatch-id <uuid>` or `--cluster-id X --rule-key R`. Creates a new SignalDispatch row (audit preserved).

## Flow diagram

```
beat 'scan-signal-dispatch-rules' (crontab '*/5', long_running queue)
  → tasks.scan_signal_dispatch_rules
  → SignalDispatchService.scan_and_dispatch()
  → for each rule × eligible cluster:
      create SignalDispatch(outcome='queued')
      enqueue dispatch_agent_for_signal_cluster.delay(dispatch_id)
  → dispatch_agent_for_signal_cluster (per-cluster task, long_running)
  → SignalDispatchService.execute_dispatch(dispatch_id)
  → AgentRouter.route(agent_name=rule.agent_name, task, context, trigger_source='signal_dispatch_v1')
  → SignalDispatch.outcome = succeeded|failed  + agent_execution_id
```

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

- PR #3501 recycled clean at `sha=68705a69e4f6` via `make recycle-all`.
- Rigby verification triad:
  - `orm_inspect_tool list_models` — platform loads clean.
  - `db_health_tool verify_table core_signaldispatch` — table exists with all 12 expected columns (id, rule_key, pattern_type, agent_name, outcome, error_summary, input_payload, agent_execution_id, scan_run_id, dispatched_at, completed_at, signal_cluster_id).
  - `scheduled_tasks_tool` filtered by `scan-signal-dispatch-rules` — enabled=True, `last_run=15:50:00`, `total_runs=1`. **Beat scheduler is already picking it up post-merge — first scan fired 5 min after merge.**
  - Smoke: `delegate_to_agent TrendAnalysisAgent` returned `task_id=da07b024-de4e-4467-8dbf-42b2940d3dff, mode=async` — confirms `AgentRouter.route(agent_name='TrendAnalysisAgent', ...)` path works end-to-end (same path `SignalDispatchService.execute_dispatch` uses).

**0 SignalDispatch rows created yet** — expected. Current SignalCluster snapshot (862 rows) has no rows in `status='active'` matching the two v1 rules' pattern_types; most fresh rows are `status='detecting'`. The `is_actionable` gate is intentionally strict — the pipeline is live and will fire the moment `SignalAggregationService` promotes a matching cluster to `active` with strength/confidence ≥ 0.5.

## Test suite

`core/tests/test_signal_dispatch_service.py` — **20 tests, all pass**:

- `TestSignalDispatchRulesRegistry` (4): v1 pair presence + get_rule for known/unknown
- `TestScanner` (11): enqueue, min_strength/min_confidence/status gates, dedup semantics (queued blocks, failed permits retry), global cap, per-rule daily cap, kill switch, DEFAULT constant sanity
- `TestExecuteDispatch` (5): succeeded / failed / rejected_agent_missing / rejected_unknown_rule / router-exception → failed (Rigby Q3 F-BLOCKING regression)
- `TestPayloadShape` (1): structured cluster fields in input_payload
- `TestDedupIsPerRulePerCluster` (1): two rules on same cluster both dispatch (proves dedup is per-rule, not per-cluster)

S2932 fail-loud gate tests still pass (5/5) — no regression on adjacent code. `python manage.py check` clean.

## Rigby SIGN highlights (pin `pa-7601320070104671`)

**Verdict:** substantive SIGN with 4 `agent_introspection_tool` verifications (non-rubber-stamp, per `feedback_verify_rigby_tool_runs_before_trusting_sign`). Two F-BLOCKING, one zoom-out that redirected the arc:

1. **[APPLIED — F-BLOCKING Q5(a)]** `market_research_agent` (my initial pick) does not exist in the registry. Rigby substituted `TrendAnalysisAgent` (110 executions, 100% 7d success, specialized for spider-intelligence trend briefs). Verified via `agent_introspection_tool`.
2. **[APPLIED — F-BLOCKING Q3 constraint]** Fire-once at dispatch-time is fine ONLY if outcome + error_summary + bounded retry are all wired. Without them, transient failure strands clusters in `triggered` forever. Constraint honored via `SignalDispatch.error_summary` + `resend_signal_dispatch` command + failed-dispatches-don't-block-retry dedup semantics.
3. **[APPLIED — Q6ii zoom-out reframed the arc]** DB config-table pattern historically metastasizes. Rigby proposed leaner shape: code-defined dict + audit-only DB row. Chris ratified "Proceed with Path 2" — the entire feature reshaped around Rigby's zoom-out before code touched.

## Governance

None this session. D6 moratorium unchanged. Zero new forbidden-entry candidates. Zero Fold candidates.

## Rigby Tool Gap Ledger

**One new observation, LOW severity, non-blocking.** During post-merge verification triad, Rigby noted that `SignalDispatch` and `django-celery-beat.PeriodicTask` are not in the `orm_inspect_tool` model allowlist. She fell back to `db_health_tool verify_table` (for the SignalDispatch shape) and `scheduled_tasks_tool` (for the beat row) — both succeeded, so no immediate harm. Suggested addition: extend the `orm_inspect_tool` allowlist to include these two models to unblock post-merge triads on any future audit-table + periodic-task shipping session. **Not opening as a new ledger entry** — the workaround was clean and the audit-table shape is exercised well enough by tests + db_health_tool. If a second session needs the same fallback, promote then.

## Deferred / non-scope

- Real live SignalDispatch row observation — depends on natural cluster promotion to `status='active'` matching the v1 pattern_types. Chris can eyeball rows via `db_health_tool verify_table core_signaldispatch` any time; live rows will accumulate as `SignalAggregationService` promotes clusters. Not something to force in this session.
- Rule 3/4/N addition — deliberately out of scope for v1. If Chris wants a third rule shipped, one-line addition to `SIGNAL_DISPATCH_RULES` + a smoke test.
- Admin surface for SignalDispatch review — could be added if/when Chris wants an inbox-style view of what dispatched today. Not needed for v1.
- Frontend widget — not scoped. Rigby can already answer "did any signal-dispatches fire in the last hour" via `db_health_tool` or a fresh `orm_inspect_tool` allowlist extension.

## Files changed

```
 M core/celery.py                                      (+11 lines — beat entry)
 M core/models/__init__.py                             (+3 lines — model import)
 M core/tasks.py                                       (+15 lines — 2 shared_task wrappers)
 A core/management/commands/resend_signal_dispatch.py  (+91 lines — retry lever)
 A core/migrations/0394_s2933_signal_dispatch.py       (+161 lines — CreateModel)
 A core/models_signal_dispatch.py                      (+122 lines — audit model)
 A core/services/signal_dispatch_service.py            (+270 lines — rules + service)
 A core/tasks_signal_dispatch.py                       (+42 lines — _impl_ layer)
 A core/tests/test_signal_dispatch_service.py          (+310 lines — 20 tests)
```

9 files changed, 1,061 insertions(+), 0 deletions.
