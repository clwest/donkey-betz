---
title: "Runtime Integration Tests — Celery Eager-Mode Integration Verification"
status: active
scope: platform
authority: CDR-003 §7 Gap 3 discharge; ratified via Chris directive 2026-07-09
predecessor_arc: CDR-002 §17.4 (deferred integration-test-harness) — DISCHARGED
related_governance:
  - PLAYBOOK-3.2.2 (acceptance-tests-first)
  - PLAYBOOK-2.2.2 (CDR discipline)
  - CDR-003 (`docs/research/platform/CDR_003_runtime_celery_integration_test_harness.md`)
  - Capability Graph §C5 (candidate chain: Celery Eager-Mode Integration Verification)
canonical_exemplars:
  - core/tests/test_hai_runtime_integration.py (HAI Inbox — CDR-003 bundle)
  - core/tests/test_deliverable_intake_subscriber.py::EagerModeEndToEndTests (Deliverable intake — S1250 vintage)
  - core/management/commands/delegation_lifecycle_smoke_test.py (Delegation lifecycle — Arc I-0100 P3)
---

# Runtime Integration Tests

## What this pattern is

When a campaign ships a Celery task, the standard acceptance test at
`captureOnCommitCallbacks(execute=True) + patch(_ENQUEUE_PATH)` neuters
`.delay(...)` — it verifies the receiver's on-commit gating but never
lets the task body run. That gap allowed **three latent
production-only defects** in Session 2737 (documented in
`docs/handoffs/SESSION_2737_PLAYBOOK_V0_2_0_RATIFIED.md` §10.8).

The **Celery Eager-Mode Integration Verification** pattern closes that
gap: mark the test `integration_celery`, use `TestCase` (savepoint
cleanup) + `self.captureOnCommitCallbacks(execute=True)` + do NOT
`patch` the enqueue site, and add:

```python
@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    # + any per-task kill switches to isolate to the task under test
)
```

Now `.delay(...)` inlines the task body, the task's ORM writes land in
the test DB, and the acceptance test can assert on the **real ORM side
effect** — not on `.delay.call_args`.

## When you MUST reach for this pattern

Any campaign that ships a `@shared_task` whose body calls
`.objects.create` / `.objects.update` / `.objects.filter(...).update(...)`
on a Django model. This includes:

- New signal receivers that enqueue Celery tasks
- Task bodies that import from any `core.models*` module
- Task bodies that write to models with `NOT NULL` / choice / `max_length`
  constraints that unit tests might not otherwise exercise

If the task body only calls external APIs (no ORM writes), the
receiver-side pattern with `.delay` patching remains sufficient — but
add a runtime smoke test on live workers per §Boundary below.

## Canonical exemplar

See `core/tests/test_hai_runtime_integration.py`:

```python
@pytest.mark.integration_celery
class HAIInboxEagerModeEndToEndTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(...)
        # Disconnect celery_telemetry signals for the test — under
        # ALWAYS_EAGER the task-request.delivery_info doesn't populate
        # queue routing-key, which trips a NOT-NULL constraint on
        # core_celerytaskevent(queue). Aborted psycopg2 transaction
        # then invalidates the connection for subsequent assertions.
        from celery.signals import task_prerun, task_postrun, task_failure
        from core.celery_telemetry import (
            on_task_prerun, on_task_postrun, on_task_failure,
        )
        task_prerun.disconnect(on_task_prerun)
        task_postrun.disconnect(on_task_postrun)
        task_failure.disconnect(on_task_failure)
        self.addCleanup(task_prerun.connect, on_task_prerun)
        self.addCleanup(task_postrun.connect, on_task_postrun)
        self.addCleanup(task_failure.connect, on_task_failure)

    @override_settings(
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_TASK_EAGER_PROPAGATES=True,
        HAI_DISCORD_DISPATCH_ENABLED=False,  # isolate to Inbox
        HAI_WEBPUSH_DISPATCH_ENABLED=False,
        HAI_INBOX_DISPATCH_ENABLED=True,
    )
    def test_task_body_produces_real_orm_side_effect(self):
        with self.captureOnCommitCallbacks(execute=True):
            HumanAttentionItem.objects.create(
                user=self.user, urgency='critical', ...,
            )
        # Assert on the real ORM row the task body wrote:
        log = HAIDispatchLog.objects.get(
            user=self.user, channel='inbox',
        )
        self.assertEqual(log.status, ChannelDispatchState.SUCCEEDED.value)
```

Additional exemplars (older):

- `core/tests/test_deliverable_intake_subscriber.py::EagerModeEndToEndTests`
  — S1250 subscriber that verifies task-body writes 1 `MissionRun` + 3
  `OpsRunEvent` rows.
- `core/management/commands/delegation_lifecycle_smoke_test.py` — a
  management-command variant per ADR-0003 §3.2 (Arc I-0100 P3) with
  savepoint rollback + `sys.exit(0)` marker.

## The `integration_celery` pytest marker

Registered in `pytest.ini` under `markers =` and in `tests/conftest.py`
via `config.addinivalue_line`. Discoverable via
`pytest --markers | grep integration_celery`. Select a subset via
`pytest -m integration_celery`.

## Setup requirements

1. `@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)`
   at the test-method decorator level.
2. Disconnect `celery_telemetry` signal receivers in `setUp` +
   reconnect in `addCleanup` (see exemplar). Under ALWAYS_EAGER the
   task-request's `delivery_info` does NOT populate the routing-key,
   which trips a NOT-NULL constraint on
   `core_celerytaskevent(queue)`. Failure to disconnect leaves the
   psycopg2 connection in an aborted state and subsequent assertions
   fail with `InterfaceError: connection already closed`.
3. Kill-switch every downstream channel your test does NOT need to
   exercise (e.g., `HAI_DISCORD_DISPATCH_ENABLED=False` to prevent
   real Discord HTTP during test).
4. Use `TestCase` + `self.captureOnCommitCallbacks(execute=True)` —
   NOT `TransactionTestCase`. The latter uses `TRUNCATE ... CASCADE`
   at teardown, which fails against the test DB's FK graph
   (`market_monitoring_session` FK-references `core_marketintelligencebrief`
   and does not truncate). `TestCase` uses savepoint rollback.

## Boundary — what this pattern does NOT do

Per Chris's ratification of CDR-003 §8 Option A (2026-07-09), this
pattern is **narrower than production-equivalent Celery verification**.
It catches:

- **Task-body import errors** (§10.8.2 class)
- **Invalid model-field values** (§10.8.3 class — `max_length`, choice
  set, NOT NULL)
- **Transaction-ordering defects** (on_commit fires before or after
  save)
- **ORM-side failures** in the task's happy path

It does **NOT replace**:

- **Worker task-registry verification** — that a task's module is in
  `app.conf.imports` and the worker sees the task name at
  `celery -A core inspect registered`. This class of bug (§10.8.1) is
  reachable only via a live worker.
- **`make celery-recycle`** after any change to task-module contents or
  `app.conf.imports`. Test-mode ALWAYS_EAGER runs the task in-process,
  bypassing the worker registry entirely.
- **`celery inspect registered`** — asks running workers what they've
  loaded. Test mode has no worker.
- **Queue-routing verification** — that `@shared_task(queue='...')` +
  `app.conf.task_routes` route the task to the intended queue in
  production. Test mode has no broker.
- **Serialization / concurrency verification** — production tasks
  serialize their args through the broker; test mode uses in-process
  Python object references. Pickling failures, argument-size limits,
  and concurrency guarantees are not exercised.
- **End-to-end runtime smoke tests on live workers** — the discipline
  documented in `SESSION_2737_PLAYBOOK_V0_2_0_RATIFIED.md` §10.8.4 that
  surfaced the three latent defects. Any wrap-up bundle that ships a
  Celery task MUST STILL run this discipline post-merge, regardless of
  whether an `integration_celery` test exists.

Those remain runtime-close requirements and are candidate input for a
future MINOR Playbook amendment on **Chapter 8 Runtime Discipline**
(currently STUB per `docs/ENGINEERING_PLAYBOOK.md`).

## Cost

- Each `integration_celery` test runs the task body inline. Latency
  = whatever the task body takes.
- Full test suite runs are slower than pure receiver tests. Use
  `-m 'not integration_celery'` to skip in fast CI passes; run in
  full CI + pre-merge.
- Do not use for tests whose subject is only receiver-side gating.
  The existing 10-site `captureOnCommitCallbacks(execute=True) +
  patch(_ENQUEUE_PATH)` pattern remains correct for those.

## When to add a NEW `integration_celery` exemplar to this doc

If a campaign ships a new Celery task family (e.g., a new subscriber
class) and adds an `integration_celery` test that exercises a
qualitatively different substrate than the three exemplars above,
append a new entry to the `canonical_exemplars` list in the
frontmatter. Do NOT delete existing entries — they remain valid
reference implementations.
