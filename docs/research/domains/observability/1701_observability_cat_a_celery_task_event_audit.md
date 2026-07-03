---
title: "S1701 Group 1700 Cat A — Task/Worker Execution Telemetry (CeleryTaskEvent) Child Audit"
status: active (Rigby SIGN cycle 1 SIGN-with-edits at High confidence 2026-07-03 on arc pin pa-e7fbacc996b34b44 [S1600 parent-scoping precedent: arc pin doubles as SIGN pin; fresh SIGN isolation pin pa-3147aef9db4945ac minted per playbook §15 was routed-around by tools/pa_local.sh wrapper hard-coded arc pin at L128 — retired at S1701 close per §16]; F1-F3 folds landed pre-commit; Chris ratified P1 kickoff via "Start research group 1701" short command per playbook §21 short-command intent — interpreted as S1701 child under Group 1700 per parent D72 P1 slot)
authority: child-audit for Category A per parent §5 D72 sequence + FIRST child under Group 1700; applies D48 preemptive stability-probe gate 18th arm on fresh SIGN pin per playbook §15 stage-table child row
category: child_audit
session: 1701
date: 2026-07-03
domain_slug: observability
research_group: 1700
child_slot: P1
parent_doc: docs/research/domains/observability/1700_observability_domain_scoping.md
head_commit: b8194e24
authors: Claude Code (Chris directed via short command "Start research group 1701")
supersedes: none
related:
  - docs/research/domains/observability/1700_observability_domain_scoping.md         # parent scoping — Cat A boundary §3 A + load-bearing questions + F5 correlation-primitives box (task_id primitive row)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                        # §11.2 20-section child template + §13 six-parallel-Explore + §14 verifier-loop + §15 SIGN
  - docs/research/domains/content/1601_content_claims_pack_deliberation_pipeline_v2_audit.md  # first-child structural precedent under Group 1600 + frontmatter exemplar
  - docs/research/platform/cross_domain_integration_audit.md                          # S1274 §2 integration map baseline + §11.6 5-layer execution-telemetry dedup precedent
  - docs/topics/celery-workers.md                                                     # Session 983/1113/1165/1167/1169 observability sections + operator playbook
  - docs/topics/agent-system.md                                                       # cross-reference for agent-task dispatch path
  - docs/AUDIT_FINDINGS.md                                                            # §12 canonical Celery deferred-by-policy list (S1245 audit surface)
  - docs/handoffs/SESSION_983_CELERY_OBSERVABILITY_AND_SKIN_FIX.md                    # baseline: model + 3 signal handlers
  - docs/handoffs/SESSION_1165_COO_BACKLOG_TRIPLE_MUST_CLOSE.md                       # COO #1 close_old_connections + memory field wiring
  - docs/handoffs/SESSION_1167_COO_BACKLOG_5_AND_7_CLOSE.md                           # COO #5 memory sampling + COO #7 top_consumers + monitor-overhead operator playbook
  - docs/handoffs/SESSION_1169_CARRYOVER_QUEUE_CLOSE.md                               # agent_name dim (Item F) + monitor-task decorator timeouts (Item D)
  - docs/handoffs/SESSION_1245_P2_CELERY_CONNECTIVITY_AUDIT_PLUS_AUDIT_FINDINGS_12_VALIDATION.md  # zero-fire probe + retention caveat
  - docs/handoffs/SESSION_1246_S1245_BONUS_FINDINGS_CLOSED_PLUS_AUDIT_AXIS_PLUS_CONTENT_TASK_RETIREMENT_PLUS_FLEET_VERIFICATION.md  # task_name .name extraction fix + fleet caller verification
  - docs/PLATFORM_INVENTORY.md                                                        # runtime counts anchor
  - docs/PLATFORM_WHAT_IT_IS.md                                                       # narrative anchor
scope: Cat A per parent §3 A — Celery task lifecycle signal-handler-driven telemetry. Owns CeleryTaskEvent model + celery_telemetry.py signal handlers (prerun/postrun/failure/before_task_publish) + retention policy (`CELERY_TASK_EVENT_RETENTION_DAYS`) + cleanup task (`cleanup_celery_task_events`). Does NOT own LLM-call telemetry (Cat B), AgentExecution model semantics (Cat C — canonicalization is Cat C's job), tool-call telemetry (Cat D), or Ops/Mission telemetry (Cat E). Cross-cat writes from Cat A signal handlers to Cat C model (`on_agent_task_failure_bridge`) are IN-scope as boundary evidence; Cat C's response to that write is Cat C's scope.
boundary_rule: |
  Cat A owns *telemetry emitted by the Celery task lifecycle boundary* (signal-handler-driven writes on prerun/postrun/failure/before_task_publish).
  Cat A does NOT own telemetry emitted from inside a task body (LLM call → Cat B; tool call → Cat D; agent execution semantics → Cat C).
  Cat A does NOT own the AgentExecution 3-class canonicalization decision (parent §3 Cat C landmine).
  Cat A includes: `CeleryTaskEvent` model, `core/celery_telemetry.py` signal handlers, retention policy + cleanup task, agent_name dimension (S1169), priority-router telemetry fields (S1086), memory tracking fields (S1165), stamp_sent_at enqueue-time header (feeder to Cat A's downstream consumers but not itself a CeleryTaskEvent write).
  Cat A signal handler writing to a Cat C model (`on_agent_task_failure_bridge` at celery_telemetry.py:240-286) crosses the nominal boundary but is IN-scope for Cat A as **evidence of boundary posture**. The write itself is Cat A code; the schema being written to is Cat C. xx99 canonical summary owns the boundary-rule verdict.
load_bearing_questions:
  - Q1 (parent §3 Cat A "Coverage across task states"): Does CeleryTaskEvent cover all task states across all workers, and specifically — is QUEUED state materialized in any writer path, or is it a defined-but-never-written status choice?
  - Q2 (parent §3 Cat A "agent_name dimension defensibility"): Is the S1169 agent_name dimension retroactively defensible or backfill-incomplete? What percentage of rows carry `agent_name=''` at HEAD?
  - Q3 (parent §3 Cat A "retention window observed vs configured"): What is the observed-vs-configured retention window at HEAD given `CELERY_TASK_EVENT_RETENTION_DAYS` default 30 and the weekly cleanup task cadence?
  - Q4 (parent §3 Cat A "monitor-task overhead spiral"): What is the monitor-task overhead spiral risk state at HEAD per S1167 precedent (probe decomposition deferred, decorator-side timeouts landed S1169)?
  - Q5 (parent §3 Cat A "observability-of-observability"): What is the observability-of-observability meta answer — how would we detect if signal handlers silently stop firing? (S1245 accumulation-lag caveat + S1246 task_name extraction bug precedents.)
  - Q6 (parent §5 F5 correlation-primitives box, task_id row): Is task_id primitive coverage complete + retention-bounded? Is task_id declared as an FK anywhere, or purely string-based correlation to downstream Cat B/C/D/E models?
verifier_loop: |
  Pre-Explore load-bearing claims verified via file:line direct read before firing sub-agents (2026-07-03):
    - CeleryTaskEvent model at core/models_celery_telemetry.py:17 (confirmed; 102 lines total, 16 persistent fields + auto PK)
    - Signal handlers at core/celery_telemetry.py — 5 handlers verified NOT 3 as parent §3 A claims (`74-177` → actual `74-300`): on_task_prerun L74, on_task_postrun L115, on_task_failure L177, on_agent_task_failure_bridge L240, stamp_sent_at L289. Parent §3 A line-range drift is a §14 finding.
    - cleanup_celery_task_events at core/tasks.py:4394 IS @shared_task (L4394 decorator; L4395 def; Agent 1 UNKNOWN → resolved YES)
    - Beat schedule at core/celery.py:153-158 — 'cleanup-celery-task-events' → crontab(minute=50, hour=4, day_of_week='sunday') → queue='default', expires=3600. Weekly Sunday 04:50 UTC.
    - Signal handler wiring at core/celery.py:941 — `import core.celery_telemetry  # noqa: F401  — signal handlers connect on import`
    - REVOKED status IS written (Agent 3 UNKNOWN → resolved YES): 2 writers found — core/services/ops_autopilot.py:100 (stuck-task sweep) + core/services/td_handlers_gateway.py:1041 (user-initiated cockpit_tool.revoke_task).
    - QUEUED status IS written (parent §3 A gap-flag → resolved LEGITIMATE): 1 writer found — core/services/td_handlers_gateway.py:988 (cockpit_tool.trigger_task fills gap so status polling doesn't fall through to AsyncResult PENDING).
    - Priority-router fields written outside signal handlers: core/services/priority/enforce.py:307-313 (S1086 PR 3b — writes priority_matched/priority_name/throttle_class as separate call from prerun).
    - Retention setting at core/settings.py:102 — `CELERY_TASK_EVENT_RETENTION_DAYS = int(os.environ.get('CELERY_TASK_EVENT_RETENTION_DAYS', '30'))`.
  Six parallel Explore sub-agents fired per playbook §13 (2026-07-03). Findings folded into §3-§20 with attribution.
  Rigby SIGN cycle 1 SIGN-with-edits at High confidence 2026-07-03 (D48 18th arm HOLDING CLEAN; 4-question single-batch pattern). Three folds landed pre-commit: F1 MEDIUM boundary terminology (cross-cat exception vs parallel writer); F2 LOW 7→8 downstream celery_task_id count consistency; F3 LOW D10 severity footnote. See §20.5 for full fold notes.
methodology_ratifications:
  - D69 parent-with-children (Chris-locked S1700)
  - D70 six categories A-F with F1-F3 folds (Chris-locked S1700)
  - D71 delegation boundary vs Group 1900 explicit (Chris-locked S1700)
  - D72 P1 S1701 = Cat A CeleryTaskEvent (Chris-locked S1700)
  - D73 posture-decision framing = evidence plan NOT recommendation (Chris-locked S1700)
  - D74 arc lens question = correlation-primitive spine posture (evidence plan; Chris-locked S1700)
  - Playbook §11.2 20-section child template FIRST application under Group 1700
  - Playbook §13 6-parallel-Explore sweep applied
  - Playbook §14 verifier-loop applied pre-Explore + post-Explore on binary claims
  - D48 preemptive stability-probe gate 18th arm start on fresh SIGN pin pa-3147aef9db4945ac
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/topics/celery-workers.md
---

# Session 1701 — Group 1700 Cat A: Task/Worker Execution Telemetry (CeleryTaskEvent) Child Audit

> **What this doc is.** A child audit under the Group 1700 Observability
> / Telemetry / SLOs arc. FIRST child (P1) per parent §5 D72 sequence.
> Applies playbook §11.2 20-section template to Category A per parent
> §3 A — Celery task lifecycle telemetry emitted by signal handlers.
> Every load-bearing claim cites `file:line` at HEAD `b8194e24`
> (main branch, post-S1700 arc-open merge). Every load-bearing
> negative claim ("no beat entry", "no consumer", "no reader") is
> grep-verified with the grep pattern cited in §20.
>
> **What this doc is not.** A deep-dive on LLM-call telemetry
> (Cat B, S1702), AgentExecution semantics or the 3-class canonicalization
> landmine (Cat C, S1703), tool-call telemetry (Cat D, S1704),
> Ops/Mission telemetry (Cat E, S1705), or the omnibus cross-cutting
> audit (Cat F, S1706). Handoffs to sibling children are noted at the
> boundary via cross-references; not traversed.
>
> **What is deferred to xx99 (S1799).** The load-bearing D74 axis —
> "are the 5 execution-telemetry layers structurally separable OR do
> they need canonical unification (single execution_id + trace_id
> spine)?" — is an evidence-plan question, not a Cat-A verdict. This
> child audit contributes the task_id primitive's posture (§9 + §10);
> xx99 owns the axis resolution.

---

## 1. Executive Summary

Cat A (Task/Worker Execution Telemetry, `CeleryTaskEvent`) is **STABLE
with codified debt** at HEAD `b8194e24`. The `CeleryTaskEvent` model
(`core/models_celery_telemetry.py:17-102`, 16 persistent fields + auto
PK) is a lightweight, autonomous, FK-free telemetry sink populated by
5 Celery signal handlers at `core/celery_telemetry.py:74-300` (3 more
than parent §3 A's cited range `:74-177`). Signal handlers are all
defensively wrapped (`except Exception: log`) so telemetry can never
break task execution. The retention policy is enforced via a weekly
`@shared_task` cleanup at Sunday 04:50 UTC deleting rows older than
`CELERY_TASK_EVENT_RETENTION_DAYS` (default 30) — bounded work, safely
staggered to relieve the hour=4 :00 cluster (S1165 COO #3).

**Six load-bearing findings**:

1. **QUEUED status is NOT a ghost state** — one legitimate non-signal-handler
   writer exists at `core/services/td_handlers_gateway.py:988`
   (`cockpit_tool.trigger_task`) that creates the CeleryTaskEvent row
   with `status='QUEUED'` immediately post-dispatch so status polling
   doesn't fall through to AsyncResult PENDING. This is legitimate;
   parent §3 A "QUEUED gap" claim is resolved as **legitimate exception,
   codify in Cat A boundary rule**.
2. **Parent §3 A signal-handler line range (`:74-177`) is drift** — actual
   handlers span `:74-300` with 5 distinct handlers (2 more than cited).
   §14 finding; owed to xx99 anchor-update.
3. **REVOKED status is NOT a ghost state** — 2 legitimate non-signal-handler
   writers exist: `ops_autopilot.py:100` (stuck-task revocation sweep) and
   `td_handlers_gateway.py:1041` (user-initiated `cockpit_tool.revoke_task`).
4. **Cross-cat exception from Cat A signal handler to Cat C model**
   (`on_agent_task_failure_bridge` at `core/celery_telemetry.py:240-286`)
   is a **legitimate S1219 P1 correctness fix**, categorically distinct
   from the 4 parallel writers above (which write Cat A's own schema).
   This is a **fire-alarm circuit-breaker** bridging SoftTimeLimitExceeded
   gap; idempotent; scoped to `status IN ('running', 'in_progress')`.
   Hard-SIGKILL gap remains watchdog territory. Per Rigby SIGN cycle 1
   F1: terminology matters — "cross-cat exception" not "parallel writer",
   because Cat C S1703 audit will inherit this framing. xx99 should
   codify as documented Cat A/C carve-out and decide code-location
   posture (stays in Cat A code vs relocates to Cat C).
5. **agent_name backfill is intentional gradual-fill debt (S1169)** —
   `models_celery_telemetry.py:41-46` docstring: "no backfill — gradual
   fill per Rigby's skip-joins-in-v1 stance". Empty-string rows are
   filtered from `top_consumers(group_by='agent')` aggregates; % at HEAD
   UNKNOWN (requires ORM query).
6. **Monitor-task overhead debt (S1167) is PARTIALLY closed** — decorator-side
   timeouts landed S1169 (`monitor_celery_health` @shared_task with
   `soft_time_limit=60`, `time_limit=90`, `queue='broadcast'`);
   caller-site kwargs migration landed S1169 sweep. Probe-decomposition
   root fix per `docs/topics/celery-workers.md:255-276` remains deferred.

**Correlation primitive posture** (parent §5 F5 correlation-primitives
box, task_id row): `CeleryTaskEvent.task_id` is a
`CharField(unique=True, db_index=True)` at
`core/models_celery_telemetry.py:33`. **7 other models carry `celery_task_id`
as a scalar CharField, NOT as an FK.** JSON linkage to
`AgentExecution.input_data['celery_task_id']` (`core/tasks_agents.py:2179`)
is string-based, not relational. This is Cat A's contribution to xx99's
D74 axis: task_id is a **coverage-complete singleton primitive with
string-based downstream references**, not a spine.

**Coverage completeness**: task_id primitive covers all Celery-dispatched
task lifecycle events at HEAD with the exception of PUBLISH-only tasks
that never reach a worker (broker crash / queue full / expired before
prerun). That gap is not covered by CeleryTaskEvent; queue-depth
observation is via `cockpit_tool.queue_lengths` (broker inspect) not
the CeleryTaskEvent row surface.

**Retention posture**: 30-day default is under-instrumented for
zero-fire probes over long-tail (S1245 caveat — accumulation lag
means "never fired" claims from <30d windows are unsafe). S1245's
`audit_celery_zero_fire` mgmt command encodes the caveat via KNOWN_DEFERRED.

**Maturity classification**: STABLE (per playbook §12); Risk MEDIUM (Cat A silent-drift class is well-precedented — S1245 accumulation lag + S1246 `.name` extraction bug — but detection tooling exists via zero-fire probe + top_consumers monitor-task alerts).

**Research coverage**: MODERATE. Topic doc (`docs/topics/celery-workers.md:182-306`) covers the surface but pre-dates parent §5 correlation-primitives framing. Prior research library refs (S1273 §3.25 + S1274 §11.6) frame the 5-layer dedup problem but do not close Cat A specifically.

---

## 2. Domain Purpose

**Q1 (§9): What is Cat A for?** Cat A is the **Celery task lifecycle
telemetry sink** for the Donkey Betz platform — one persistent row per
Celery task invocation, populated by signal handlers so the platform
owns the observability data instead of depending on
`django_celery_results` (which requires
`CELERY_RESULT_BACKEND='django-db'` and returns empty QuerySets when
the backend is Redis).

**Q2 (§9): What problem does it solve?** The
`docs/topics/celery-workers.md:182-189` framing: "The `status_snapshot_tool`
was reporting 'Celery tasks: 0' as a false negative because Redis-backed
result store returns empty QuerySets." Cat A owns the Redis-independent
task-execution ledger — task_id, task_name, status, duration, memory,
priority-router decisions, and (since S1169) agent_name dimension. It
enables:

- Per-task-name volume, duration percentiles (p50/p95), and failure-rate
  aggregation over rolling windows (24h default per SLO consumers).
- Memory-delta observation (`rss_delta_mb`) with 50MB warning / 100MB
  error thresholds logged at task boundary (S1165 COO #5).
- Stuck-task detection (`ops_autopilot.py:88-113`) and revocation of
  tasks stuck in STARTED status past `STUCK_TASK_MINUTES` threshold.
- Zero-fire probing (S1245 `audit_celery_zero_fire` mgmt command) for
  registered-but-never-invoked tasks, retention-bounded.
- Priority-router SLO tracking (S1086 PR 3b — `priority_matched`,
  `priority_name`, `throttle_class` fields signal whether each dispatch
  hit the throttle lane).

The Cat A layer is **the only complete inventory of task lifecycle
events** for the platform. Other execution-telemetry layers (LLMCallEvent
= Cat B, AgentExecution = Cat C, ToolCallRecord = Cat D, OpsRunEvent = Cat E)
answer different questions inside the task body; only Cat A observes
the task boundary itself.

---

## 3. Canonical Entry Points

**Q3 (§9): Canonical entry points to Cat A.**

### Writer entry points (in priority order)

| # | Entry point | File:line | Trigger | Writes |
|---|---|---|---|---|
| 1 | `on_task_prerun` | `core/celery_telemetry.py:74-112` | Celery `task_prerun` signal | `update_or_create` row with status=STARTED, started_at, rss_mb_start, agent_name (S1169), queue, worker |
| 2 | `on_task_postrun` | `core/celery_telemetry.py:115-174` | Celery `task_postrun` signal | Update to state (SUCCESS default), finished_at, duration_seconds, rss_mb_end, rss_delta_mb; memory-spike warnings; `check_and_notify` hook; `close_old_connections` (S1165 COO #1) |
| 3 | `on_task_failure` | `core/celery_telemetry.py:177-237` | Celery `task_failure` signal | Update to FAILURE, error_type, error_message (1000-char truncated), finished_at, duration_seconds, rss delta; same memory warnings + notification + connection-close side effects |
| 4 | `on_agent_task_failure_bridge` | `core/celery_telemetry.py:240-286` | Celery `task_failure` signal (2nd handler) | Cross-cat write to **Cat C model** — filters `AgentExecution` rows with `input_data->>'celery_task_id'` matching task_id + status IN ('running', 'in_progress'); updates to `status='failed'`, error_message, completed_at. Idempotent. Handles S1219 SoftTimeLimitExceeded gap. |
| 5 | `stamp_sent_at` | `core/celery_telemetry.py:289-300` | Celery `before_task_publish` signal | Stamps `headers['sent_at'] = time.time()` — **does NOT write CeleryTaskEvent row**; feeds `cockpit_tool.queue_lengths` age computation via message header. |

**Signal handler wiring:** `core/celery.py:941` — `import core.celery_telemetry  # noqa: F401  — signal handlers connect on import`. Ordering is correct per parent §3 A note: import happens **after** `app.autodiscover_tasks()` at `core/celery.py:812`, so Celery app registry is populated before signal decorators fire.

### Non-signal-handler writers (legitimate exceptions to "signals own writes")

| # | Writer | File:line | Purpose | Status |
|---|---|---|---|---|
| A | `cockpit_tool.trigger_task` gateway | `core/services/td_handlers_gateway.py:988-995` | Creates row with `status='QUEUED'` immediately post-dispatch so task_status polling doesn't fall through to AsyncResult PENDING | **legitimate**; only writer of QUEUED status |
| B | `cockpit_tool.revoke_task` gateway | `core/services/td_handlers_gateway.py:1041-1042` | Updates existing row to `status='REVOKED'` after `celery_app.control.revoke()` | legitimate; guards on `status IN ('QUEUED', 'STARTED')` |
| C | `ops_autopilot` stuck-task sweep | `core/services/ops_autopilot.py:100-101` | Revokes tasks stuck in STARTED past `STUCK_TASK_MINUTES` cutoff; writes `status='REVOKED'` + `save(update_fields=['status'])` | legitimate; MAX_REVOKES_PER_RUN bounds volume |
| D | `PriorityRouter.enforce` | `core/services/priority/enforce.py:307-313` | Writes S1086 PR 3b fields (`priority_matched`, `priority_name`, `throttle_class`) on the CeleryTaskEvent row after prerun fires and PriorityRouter.check() completes | legitimate; separate call from prerun signal handler |

**Verifier note:** Full grep of `CeleryTaskEvent.objects.(create|update_or_create)` returns exactly 3 signal-handler locations + 1 gateway writer (item A above) + 3 test-only fixtures. Grep of `event.status = |event.priority_matched = |event.priority_name = |event.throttle_class = ` returns items B/C/D above plus the in-handler writes at `celery_telemetry.py:127` (postrun) and `:189` (failure). Total non-signal-handler writers to production CeleryTaskEvent rows: **4** (items A-D). All 4 are legitimate; each has clear per-case business logic that signal handlers cannot serve.

### Reader entry points (PA tool + REST + management commands + service layer)

See §6 (Major APIs) for PA tool + REST + management-command inventory. See §9 (Integrations) for service-layer readers (`ops_autopilot`, `nervous`, `td_handlers_*`, `views_diagnostics`).

### Retention entry point

| Location | File:line | Purpose |
|---|---|---|
| `cleanup_celery_task_events` @shared_task | `core/tasks.py:4394-4404` | Deletes rows where `started_at__lt=cutoff` (default 30 days); returns `{'deleted': count, 'retention_days': days_to_keep}` |
| Beat schedule entry | `core/celery.py:153-158` | `crontab(minute=50, hour=4, day_of_week='sunday')` — weekly Sunday 04:50 UTC; queue='default'; expires=3600. S1165 COO #3 staggering comment at L155. |
| Retention setting | `core/settings.py:102` | `CELERY_TASK_EVENT_RETENTION_DAYS = int(os.environ.get('CELERY_TASK_EVENT_RETENTION_DAYS', '30'))` |

---

## 4. Major Models

**Q4 (§9): Major models with file:line.**

### `CeleryTaskEvent` — `core/models_celery_telemetry.py:17-102`

Single model in Cat A. FK-free (zero inbound, zero outbound). 16 persistent fields + auto BigAutoField PK. Introduced S983 (Session 983 header docstring at `:1-11`).

**Field inventory (grouped by lineage):**

| Group | Field | File:line | Type | Constraints | Purpose |
|---|---|---|---|---|---|
| S983 baseline | `task_id` | `:33` | CharField(255) | unique=True, db_index=True | Celery task UUID; the load-bearing primitive (parent §5 F5) |
| S983 baseline | `task_name` | `:34` | CharField(255) | db_index=True | Fully-qualified task path (e.g. `core.tasks.check_system_health`) |
| S983 baseline | `queue` | `:48` | CharField(100) | blank=True, default='' | Routing key or exchange (extracted from `delivery_info` in prerun) |
| S983 baseline | `status` | `:49` | CharField(20) | choices=STATUS_CHOICES, default='STARTED', db_index=True | 5 choices: QUEUED, STARTED, SUCCESS, FAILURE, REVOKED |
| S983 baseline | `worker` | `:50` | CharField(255) | blank=True, default='' | Worker hostname (extracted from `task.request.hostname`) |
| S983 baseline | `started_at` | `:51` | DateTimeField | default=timezone.now, db_index=True | Retention key (`started_at__lt=cutoff` filter) |
| S983 baseline | `finished_at` | `:52` | DateTimeField | null=True, blank=True | Postrun/failure timestamp |
| S983 baseline | `duration_seconds` | `:53` | FloatField | null=True, blank=True | (finished_at - started_at) in seconds |
| S983 baseline | `error_type` | `:57` | CharField(255) | blank=True, default='' | Exception class name (S983) |
| S983 baseline | `error_message` | `:58` | TextField | blank=True, default='' | Truncated to 1000 chars in failure handler (`:193`) |
| **S1086 PR 3b** | `priority_matched` | `:67-74` | BooleanField | null=True, blank=True | `NULL` = router gate OFF or task not evaluated; T/F = PriorityRouter.check() verdict |
| **S1086 PR 3b** | `priority_name` | `:75-82` | CharField(120) | null=True, blank=True | Name of ActivePriority row that matched; `NULL` for user_chat_exempt, fail_open, no-match MISMATCH |
| **S1086 PR 3b** | `throttle_class` | `:83-90` | CharField(16) | null=True, choices=[matched/mismatched] | Which semaphore lane the dispatch ran in |
| **S1165** | `rss_mb_start` | `:54` | FloatField | null=True, blank=True | RSS at task begin (S1165 COO #5) |
| **S1165** | `rss_mb_end` | `:55` | FloatField | null=True, blank=True | RSS at task finish |
| **S1165** | `rss_delta_mb` | `:56` | FloatField | null=True, blank=True | (end - start) rounded to 2 decimals; drives 50MB/100MB memory-spike log warnings |
| **S1169** | `agent_name` | `:41-46` | CharField(255) | blank=True, default='', db_index=True | Extracted from task kwargs (S1169 order: agent_name → agent_class → agent (str only) → agent_type); `''` = non-agent task OR pre-migration row (no backfill) |

**Meta options** (`:92-98`):

- `ordering = ['-started_at']` — newest-first default
- 2 indexes:
  - `celery_evt_time_status` on `(-started_at, status)` — supports status-filtered time-window aggregations (24h SLO queries)
  - `celery_evt_name_time` on `(task_name, -started_at)` — supports per-task drilldown

### Migration lineage

| Migration file | Session | Change |
|---|---|---|
| `core/migrations/0235_celery_task_event.py` | S983 | CREATE model with 10 base fields + 2 indexes |
| `core/migrations/0255_celerytaskevent_memory_fields.py` | S1165 | ADD 3 memory fields (rss_*) |
| `core/migrations/0330_priority_router_telemetry_fields.py` | S1086 PR 3b | ADD 3 priority fields; depends on 0329_active_priority_model |
| `core/migrations/0355_session_1169_celerytaskevent_agent_name.py` | S1169 | ADD agent_name field (indexed); docstring specifies surgical extraction (no other drift) |

4 migrations over ~2.5 months (Feb–Apr 2026). No schema refactors, no backfills applied.

### FK graph

**Zero inbound FKs, zero outbound FKs.** CeleryTaskEvent is completely autonomous at schema level. Correlation to other models is JSON-based (`AgentExecution.input_data['celery_task_id']`) or scalar CharField (`AISeriesItem.celery_task_id`, `ContentPipelineRun.celery_task_id`, `SpiderExecution.celery_task_id`, `WorkflowExecution.celery_task_id`, `ScheduledImageGeneration.celery_task_id`, `WorkflowRun.celery_task_id`, `ExecutionRun.celery_task_id`). **8 downstream models reference celery_task_id by string; none declares an FK.** This is Cat A's contribution to xx99's D74 axis (correlation-primitive posture).

### Overlap flags vs Cat B/C/D/E/F telemetry models

**No field-level overlaps** with LLMCallEvent (Cat B), AgentExecution (Cat C), ToolCallRecord (Cat D), OpsRun/OpsRunEvent (Cat E), or HeartBeat (Cat F.a). Details in §9 (Integrations) and §17 (Duplicate/Overlapping Systems).

---

## 5. Major Services

**Q5 (§9): Major services.**

### `core/celery_telemetry.py` (301 lines) — Cat A production surface

Not a class-based service; a module with 5 signal handlers + 2 helper
functions. Runtime flow:

**`_get_rss_mb()`** (`:24-33`) — Returns current process RSS in MB via
`psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)`.
Failure mode: swallowed at `:28-33`, logs warning, returns None. Called
1-3× per task lifecycle (prerun + postrun/failure). Per-call overhead
sub-millisecond on Linux/macOS.

**`_extract_agent_name(task_kwargs)`** (`:36-57`) — Iterates
Rigby-ratified extraction order `('agent_name', 'agent_class', 'agent',
'agent_type')` (S1169 conv `pa-639751f029bc432f`). Constraints:

- `task_kwargs` must be dict, else returns `''` (`:49-50`)
- `agent` key accepts **only string** (`:55` `isinstance(val, str)`) — callers sometimes pass instance objects; we don't coerce repr
- Whitespace-stripped and 255-char capped (`:56`)
- Empty-string signals "not an agent task" to `top_consumers` aggregator

**`_extract_task_name(task, sender)`** (`:67-71`) — S1246 fix. Tries
`task.name` → `sender.name` → `str(sender)` fallback. Prevents useless
Task-repr artifacts (`"<@task: core.tasks.X of <app> at 0xADDR>"`) that
break `values_list('task_name').distinct()` aggregations downstream.

**Signal handlers 1-5** — Documented in §3 Canonical Entry Points writer
table + §7 Runtime Flows.

**Lazy imports pattern** — All 4 model-touching handlers use inline
`from core.models_celery_telemetry import CeleryTaskEvent` +
`from django.utils import timezone` at handler-body start (`:78-79`,
`:119-120`, `:181-182`, `:262-263`). Rationale: avoids circular imports
during Django app-registry bootstrap. Signal-decorator registration
happens at module import time (`:74`, `:115`, `:177`, `:240`, `:289`);
model access is delayed until handler fires (post-`ready()`).

### `core/tasks.py:4393-4404` — retention cleanup

`@shared_task` `cleanup_celery_task_events(days_to_keep: int = None)`.
Reads `CELERY_TASK_EVENT_RETENTION_DAYS` (default 30). Bulk-deletes
`CeleryTaskEvent.objects.filter(started_at__lt=cutoff)`. Returns
`{'deleted': count, 'retention_days': days_to_keep}`. Bounded work;
runs on default queue with 3600s expiry (S1165 COO #3 staggered to
Sunday 04:50 UTC to relieve hour=4:00 cluster).

### `core/services/priority/enforce.py:301-320` — S1086 PR 3b priority telemetry writer

`PriorityRouter.enforce_priority()` writes `priority_matched`,
`priority_name`, `throttle_class` fields onto the CeleryTaskEvent row
**after** prerun has fired. Uses direct field assignment +
`save(update_fields=[...])`. Legitimate parallel writer (see §3 item D).

### `core/services/task_notification.py` — postrun/failure notification hook

Called from `on_task_postrun:160` and `on_task_failure:226` via
`check_and_notify(task_id, state, result_or_error)`. Not a Cat A
persistence service; downstream consumer of task-boundary events for
Redis-backed PA conversation notification.

---

## 6. Major APIs and Interfaces

**Q6 (§9): Major APIs.**

### REST endpoints reading `CeleryTaskEvent`

| Endpoint | View file:line | Method | Purpose |
|---|---|---|---|
| `/api/celery/breakdown/` | `core/views_celery_api.py:256` (`TaskBreakdownView.get`) | GET | Task volume aggregates (by_task + by_agent) with p50/p95 percentiles; window param 15m/60m/2h/6h/24h |
| `/api/celery/breakdown/task/` | `core/views_celery_api.py:374` (`TaskBreakdownDetailView.get`) | GET | Per-task drilldown (recent executions for a task_name) |
| `/api/status/overview/` | `core/views_status_api.py:51` (`status_overview`) | GET | 24h task stats grouped by status (SUCCESS/FAILURE/STARTED counts) |

### PA tool schemas exposing Cat A data

| Tool | Schema file:line | Cat A exposure |
|---|---|---|
| `task_breakdown_tool` | `core/services/pa_tool_schemas.py:1414+` | Direct — wraps `/api/celery/breakdown/` (summary) + `/api/celery/breakdown/task/` (drilldown); returns count/percentiles/agent breakdown |
| `ops_tool` (action=`celery_task_history`) | `core/services/pa_tool_schemas.py:2480-2481` | Direct — recent task runs by task_name with window/limit/status filters |
| `ops_tool` (action=`top_consumers`) | `core/services/pa_tool_schemas.py:2491-2495` | Direct — per-task_name aggregation via PostgreSQL `percentile_cont` for p95_seconds; default window 24h; max limit 50 |
| `ops_tool` (action=`slo_status`) | `core/services/pa_tool_schemas.py:2437+` | Indirect — reads CeleryTaskEvent for success-rate / failure-rate SLO computation |
| `cockpit_tool` (multiple actions) | `core/services/pa_tool_schemas.py:3758+` | Mixed — `queue_lengths` reads broker (not CeleryTaskEvent); `trigger_task` writes QUEUED row; `revoke_task` writes REVOKED row; `task_status` reads CeleryTaskEvent |
| `diagnostics_tool` | `core/services/pa_tool_schemas.py:2365-2430` | Indirect — surfaces invocation counts + failure signatures via `td_handlers_ops.py:3441-3446` |
| `rigby_shift_brief_tool` | `core/services/pa_tool_schemas.py` (L489 dispatch) | Indirect — bundles Celery task metrics into shift handoff |
| `status_snapshot_tool` | `core/services/pa_tool_schemas.py:563-579` | Indirect — 24h aggregate via `td_handlers_ops.py:3887-3892` (total + failure count) |
| `system_health_tool` | **NOT FOUND** | Parent §3 A line 409 mention is a **doc drift** — no such tool exists in `pa_tool_schemas.py` or `tool_dispatcher.py`. Flagged §14. |

### WebSocket consumers reading `CeleryTaskEvent`

**ZERO WebSocket consumers reference `CeleryTaskEvent`.** Grep of
`core/consumers*.py` + `core/routing.py` yields no matches. Cat A
telemetry is **pull-only** — no realtime push to browser clients from
signal handlers. This is a §19 (Recommended Future Research) gap
candidate.

### Management commands

| Command | File | Cat A usage |
|---|---|---|
| `audit_celery_zero_fire` | `core/management/commands/audit_celery_zero_fire.py:254-338` | S1245 — identifies registered tasks with zero CeleryTaskEvent fires in retention window; KNOWN_DEFERRED hardcoded set mirrors AUDIT_FINDINGS.md §12 |
| `ops_verify` | `core/management/commands/ops_verify.py:88-93, 337-591` | Prod ops verification — worker memory, queue pressure, slow tasks, hang detection |
| `pa_acks_health` | `core/management/commands/pa_acks_health.py:337-591` | S1161 — PA platform acknowledgment health monitoring; multiple queries against CeleryTaskEvent |
| `build_runtime_audit` | `core/management/commands/build_runtime_audit.py` | Aggregation use (specific line context UNKNOWN; grep-confirmed reference only) |

---

## 7. Runtime Flows

**Q9 (§9): Major runtime flows.**

### Flow 1: Task publish → prerun → postrun (success path)

```
1. Caller: `task.delay(kwargs)` OR `task.apply_async(...)` OR `celery_app.send_task(...)`
   └─► Celery fires `before_task_publish` signal
       └─► `stamp_sent_at()` (celery_telemetry.py:289-300)
           → headers['sent_at'] = time.time() [only if not already set]
           → NO CeleryTaskEvent row created here

2. Task message hits broker (Redis); worker picks up; task_prerun fires
   └─► `on_task_prerun()` (celery_telemetry.py:74-112)
       → Extract queue from task.request.delivery_info
       → Extract worker from task.request.hostname
       → Extract agent_name via `_extract_agent_name(kwargs.get('kwargs'))`
       → Sample RSS via `_get_rss_mb()`
       → `CeleryTaskEvent.objects.update_or_create(task_id=..., defaults={
              status='STARTED', started_at=now, rss_mb_start=..., agent_name=...
          })`
       → Wrapped in try/except: logger.debug on failure; telemetry never breaks task

3. [Optional: PriorityRouter.enforce() may fire after prerun]
   └─► priority/enforce.py:307-313
       → event.priority_matched = decision.matched
       → event.priority_name = decision.name
       → event.throttle_class = 'matched'|'mismatched'
       → event.save(update_fields=['priority_matched', 'priority_name', 'throttle_class'])

4. Task body executes; task_postrun fires
   └─► `on_task_postrun()` (celery_telemetry.py:115-174)
       → Sample RSS via `_get_rss_mb()`
       → Fetch existing event; update:
              status = state or 'SUCCESS'
              finished_at = now
              duration_seconds = (now - started_at).total_seconds()
              rss_mb_end = ...
              rss_delta_mb = round(rss_end - rss_start, 2)
       → IF rss_delta_mb > 100: logger.error("[MEMORY] SPIKE")
       → ELIF rss_delta_mb > 50: logger.warning("[MEMORY] grew")
       → event.save(update_fields=['status', 'finished_at', 'duration_seconds', 'rss_mb_end', 'rss_delta_mb'])
       → [if event missing (eager-mode)] fallback create() at :145
       → check_and_notify(task_id, state, result) [Redis-backed PA notify]
       → close_old_connections() [S1165 COO #1 task-boundary hygiene]
```

### Flow 2: Task failure path

Structurally parallel to Flow 1 but on `task_failure` signal (`on_task_failure` at `celery_telemetry.py:177-237`). Additional writes:
- `error_type = type(exception).__name__`
- `error_message = str(exception)[:1000]`
- Same memory-spike logging + notification + connection-close hygiene
- **Second handler fires on same signal:** `on_agent_task_failure_bridge` (Flow 3).

### Flow 3: Agent-task failure bridge to Cat C model

```
task_failure signal fires (in addition to Flow 2's on_task_failure)
└─► `on_agent_task_failure_bridge()` (celery_telemetry.py:240-286)
    → Skip if no task_id (:259-260)
    → Import AgentExecution (Cat C model — lazy import at :262)
    → `updated = AgentExecution.objects.filter(
           status__in=('running', 'in_progress'),
           input_data__celery_task_id=str(task_id),
       ).update(
           status='failed',
           error_message=f'Celery task failed: {exc_name}: {exc_msg}'[:2000],
           completed_at=timezone.now(),
       )`
    → IF updated: logger.warning("[celery_telemetry] Bridged Celery task_failure → AgentExecution: rows=N")
    → EXCEPT: logger.exception (no re-raise)
```

**Boundary crossing note:** This handler is registered at Cat A boundary
(Celery signal) but writes to Cat C model (AgentExecution). Idempotent
(filter scoped to running/in_progress). Handles SoftTimeLimitExceeded
gap where task fails but agent execution row would otherwise stay
'in_progress' until the 30-min cleanup watchdog (`tasks_agents.py:1559`
per S1219 P1 handoff). Hard SIGKILL (`time_limit=3900`) cannot be
caught — worker dies, signal never fires; watchdog remains safety net.

### Flow 4: Stuck-task revocation sweep

```
1. `ops_autopilot.py:_impl_revoke_stuck_tasks` (called from ops_tool.autopilot beat)
   → cutoff = now() - timedelta(minutes=STUCK_TASK_MINUTES)
   → stuck = CeleryTaskEvent.objects.filter(
         status='STARTED',
         finished_at__isnull=True,
         started_at__lte=cutoff,
     ).order_by('started_at')[:MAX_REVOKES_PER_RUN]
   → For each event:
       → celery_app.control.revoke(event.task_id, terminate=True)
       → event.status = 'REVOKED'
       → event.save(update_fields=['status'])
       → append action record
       → logger.warning("[OpsAutopilot] Revoked stuck task ...")
```

### Flow 5: User-initiated revoke via `cockpit_tool.revoke_task`

```
1. PA tool dispatch → `_handle_cockpit(action='revoke_task', task_id=...)` in td_handlers_gateway.py
2. celery_app.control.revoke(task_id, terminate=True)
3. IF revoke succeeded:
   → Fetch CeleryTaskEvent(task_id=task_id).first()
   → IF event AND event.status IN ('QUEUED', 'STARTED'):
       → event.status = 'REVOKED'
       → event.save(update_fields=['status'])
4. Clean up any pending notification via Redis key delete
5. Return action record to PA
```

### Flow 6: Weekly cleanup

```
1. Celery beat schedule fires `cleanup-celery-task-events` at Sunday 04:50 UTC
   → task='core.tasks.cleanup_celery_task_events', queue='default', expires=3600
2. `cleanup_celery_task_events(days_to_keep=None)`:
   → days_to_keep = getattr(settings, 'CELERY_TASK_EVENT_RETENTION_DAYS', 30)
   → cutoff = timezone.now() - timedelta(days=days_to_keep)
   → count, _ = CeleryTaskEvent.objects.filter(started_at__lt=cutoff).delete()
   → logger.info(f"Cleaned up {count} CeleryTaskEvent records older than {days_to_keep} days")
   → return {'deleted': count, 'retention_days': days_to_keep}
```

### Flow 7: `stamp_sent_at` → `cockpit_tool.queue_lengths` consumer

```
1. Publisher fires before_task_publish
   → stamp_sent_at() adds headers['sent_at'] = time.time()
2. Message sits in broker queue
3. Consumer: `td_handlers_gateway.py:812-816` (in `_extract_timestamp` helper)
   → for field in ('sent_at', 'timestamp', 'enqueued_at'):
       if isinstance(headers.get(field), (int, float)):
           return float(v)
4. oldest_age_seconds = now - min(sent_at across messages in queue)
5. Classify queue state (GREEN/YELLOW/RED/CRITICAL) using depth + age thresholds
6. IF no timestamp found: parse_error='no_timestamp_field', fall back to depth-only classification
```

---

## 8. Data Ownership and Lifecycle

**Q16-18 (§9): Data ownership + consumption + production.**

### Data owned

Cat A owns the `CeleryTaskEvent` table exclusively. No other domain
writes to this table's schema; only 4 legitimate parallel writers (§3
items A-D) write specific fields for specific business cases. All
writes go through the same Django ORM (`update_or_create`, `create`,
`.filter().update()`, or `.save(update_fields=[...])`), which respects
the model's UNIQUE constraint on `task_id`.

### Data consumed

Cat A consumes **Celery signal payloads**:

- `task_prerun`: task_id, task (Task instance), sender, kwargs (dict with task's kwargs at `kwargs['kwargs']`)
- `task_postrun`: task_id, task, sender, state, retval, kwargs
- `task_failure`: task_id, sender, exception, traceback, kwargs
- `before_task_publish`: headers (dict), body, exchange, routing_key, ...

Cat A also consumes:
- `psutil` process memory info at handler-fire time
- Django `timezone.now()` for timestamps
- `celery_app.control.revoke()` external control-plane calls (indirectly via Flow 4/5)

### Data produced (for other domains)

- `CeleryTaskEvent` rows are consumed by:
  - **Diagnostics/Ops** — `td_handlers_ops.py` (20+ query sites), `views_status_api.py`, `views_celery_api.py`, `views_diagnostics.py`, `views_rag_embeddings.py:1515-1517`
  - **Priority Router** — `priority/enforce.py` reads `throttle_class` field back after writing it (in-process closure of the loop)
  - **Ops Autopilot** — `ops_autopilot.py` stuck-task detection + revocation
  - **Nervous system** — `nervous.py:405` messages-per-second rate calc
  - **PA tools** — `task_breakdown_tool`, `ops_tool`, `cockpit_tool`, `diagnostics_tool`, `rigby_shift_brief_tool`, `status_snapshot_tool`
  - **Management commands** — `audit_celery_zero_fire`, `ops_verify`, `pa_acks_health`, `build_runtime_audit`

- `on_agent_task_failure_bridge` produces status updates on `AgentExecution` rows (Cat C model) — see §3 Flow 3.

### Lifecycle summary

| Phase | When | Action | File:line |
|---|---|---|---|
| Create | Task prerun signal (or postrun/failure fallback for eager-mode; or gateway trigger_task for QUEUED) | `update_or_create` OR `create` | `celery_telemetry.py:98, 145, 209`, `td_handlers_gateway.py:988` |
| Update | Task postrun/failure signal OR ops_autopilot revoke OR gateway revoke OR PriorityRouter enforce | `save(update_fields=[...])` or `.filter().update()` | `celery_telemetry.py:139, 203`, `ops_autopilot.py:100-101`, `td_handlers_gateway.py:1041-1042`, `priority/enforce.py:307-313` |
| Read | Continuous | ORM queries via consumers listed above | multi-file |
| Delete | Weekly Sunday 04:50 UTC | `cleanup_celery_task_events` @shared_task | `core/tasks.py:4395` |

---

## 9. Integrations With Other Domains

**Q14 + Q17 + Q18 + Q21 + Q22 (§9): Integrations.**

### Cross-cat integration map at HEAD

| Integration | Direction | Mechanism | Strength |
|---|---|---|---|
| Cat A ↔ Cat B (LLMCallEvent) | none declared | `LLMCallEvent.execution_id` (Cat B UUIDField) does NOT correlate to Cat A task_id at schema level. Neither model has an FK; correlation is via `AgentExecution` as intermediary (Cat B.execution_id points to AgentExecution.id; AgentExecution.input_data has 'celery_task_id'). | **MISSING (by design)** — no direct correlation; requires Cat C join |
| Cat A ↔ Cat C (AgentExecution) | Cat A writes → Cat C | `on_agent_task_failure_bridge` (`celery_telemetry.py:240-286`) queries `AgentExecution.input_data->>'celery_task_id'` + updates status/error_message/completed_at | **WEAK (JSON-path lookup; cross-cat write)** — legitimate S1219 P1 correctness fix; not FK-backed |
| Cat A ↔ Cat D (ToolCallRecord) | none declared | ToolCallRecord has `trace_id`, `conversation_id`, no task_id | **MISSING (by design)** — ToolCallRecord scoped to inside-task-body |
| Cat A ↔ Cat E (OpsRun/OpsRunEvent) | none declared | Neither OpsRun nor OpsRunEvent has task_id | **MISSING** — Ops runs are orchestration-scoped, not task-scoped |
| Cat A ↔ Cat F.a (HeartBeat) | none | HeartBeat is a separate polling model | **MISSING** |
| Cat A ↔ 8 downstream models (see §4 FK graph) | scalar-string reference | 8 models declare `celery_task_id` CharField pointing at CeleryTaskEvent.task_id; no FK | **WEAK (string-based)** |

### Correlation primitive posture (parent §5 F5 task_id row)

Cat A owns `task_id` (`CeleryTaskEvent.task_id` = Celery task UUID
assigned at dispatch time by Celery core; `CharField(unique=True,
db_index=True)`). **task_id is a coverage-complete singleton primitive
for tasks that reach a worker.** Coverage gaps:

- **PUBLISH-only tasks** (never reach worker due to broker/queue failure) have no CeleryTaskEvent row. `stamp_sent_at` stamps the header but doesn't create a row. This is the only known coverage gap.
- **Signal-handler drift class** (S1245 accumulation lag; S1246 `.name` extraction bug) can cause task_id capture failures silently — the row is created but `task_name` may be a useless repr string until S1246 shipped.

**Downstream correlation posture:**

- **8 non-Cat-A models carry `celery_task_id` as scalar CharField** (see §4 FK graph list — `AISeriesItem`, `ContentPipelineRun`, `ConceptForgeRun`, `SpiderExecution`, `WorkflowExecution`, `ScheduledImageGeneration`, `WorkflowRun`, `ExecutionRun`). No FK constraints. This means:
  - Query cost: string equality only (indexed on `CeleryTaskEvent.task_id` side; unknown index status on the 8 downstream models — grep-worthy but outside this audit's scope).
  - Referential integrity: not enforced. Orphaned `celery_task_id` values (e.g. task_id retained after cleanup deletes the CeleryTaskEvent row) are silently allowed.
  - Direction: unidirectional; Cat A has no back-reference to any of the 8 downstream models.

- **`AgentExecution.input_data['celery_task_id']`** — JSON-path in JSONField (`input_data`). Not indexed by default (unless GIN-indexed on the JSONField, which requires separate migration verification — grep-worthy). Sub-Agent 4 identified this as the mechanism `on_agent_task_failure_bridge` uses; the bridge relies on this being findable.

**Cat A's D74 contribution:**

- task_id primitive is **complete + retention-bounded + non-FK'd**.
- Correlation to downstream models is **string-based + not enforced + at-worst-case unindexed**.
- If xx99 decides task_id → execution_id needs a canonical spine, the required work is (a) formalize the correlation via either FK migration or standardized JSON-path indexing, and (b) reconcile the 7 `celery_task_id` CharField consumers into either FK or a single correlation primitive.
- If xx99 decides layers stay structurally separate, current posture is defensible for a telemetry model — no changes required.

### Import boundaries

**`core/celery_telemetry.py` imports (top-of-file):**
- Standard library: `logging`, `os`
- Third-party: `psutil`
- Celery signals: `before_task_publish`, `task_failure`, `task_postrun`, `task_prerun`

Only cross-domain import is lazy inside `on_agent_task_failure_bridge` at `:262`:
- `from core.models_unified_system import AgentExecution`

This is a Cat A → Cat C import inside a boundary-crossing failsafe handler. Localized, lazy, documented in the handler's docstring. Not a boundary violation per parent §3 rule if we accept the S1219 P1 exception (xx99 verdict pending).

**`core/models_celery_telemetry.py` imports:**
- `from django.db import models`
- `from django.utils import timezone`

Zero cross-domain imports. Clean.

---

## 10. Event Flows

**Q19 + Q20 (§9): Events emitted + events that should be emitted.**

### Events emitted by Cat A

Cat A does **NOT emit downstream events** in the domain-event sense
(no Django signals `pre_save`/`post_save` publishers, no channel_layer
`group_send`, no WebSocket push, no Kafka/RabbitMQ producer). Cat A is
a **passive telemetry sink** — data is captured, stored, and read by
pull-based consumers (SQL queries).

**Side effects at handler boundary (not events per se):**

- `check_and_notify(task_id, state, result_or_error)` at `celery_telemetry.py:160, 226` — Redis-backed PA conversation notification hook. This is a downstream consumer call, not an event emission.
- `close_old_connections()` at `celery_telemetry.py:172, 235` — Django DB connection hygiene, not an event.
- Memory-spike log lines at `celery_telemetry.py:136, 138, 200, 202` — logger.error/warning; consumed by log aggregation, not event bus.

### Events that should be emitted (gaps)

**§14 gap candidates for xx99 evaluation:**

1. **Signal-handler-drift alert** — no event fires when `on_task_prerun` silently stops firing (S1245 accumulation-lag class + S1246 task_name extraction bug precedents). Detection today is via `audit_celery_zero_fire` mgmt command run manually or `top_consumers` looking for gaps — pull-based.

2. **QUEUED-to-STARTED-transition-timeout alert** — no event fires when a QUEUED row (from gateway trigger_task) never receives a subsequent prerun (worker never picked up). Detection today is via `ops_autopilot` stuck-task sweep at STARTED status only; QUEUED-stuck is uncovered.

3. **Retention-cleanup failure event** — if `cleanup_celery_task_events` fails (DB error, lock timeout), no event fires beyond the standard Celery task_failure signal (which itself creates a FAILURE row for the cleanup task — meta-observable but not alerted separately).

4. **`on_agent_task_failure_bridge` write count metric** — the bridge logs at `celery_telemetry.py:278-282` when it updates rows, but the count is only visible in logs. No metric surface counts bridge-writes over time, which would help detect a rise in SoftTimeLimitExceeded incidents.

5. **Cross-cat correlation-primitive-drift metric** — no metric counts how often a `celery_task_id` on a downstream model (8 candidates) points at a CeleryTaskEvent row that has been retention-deleted (orphaned reference). See §14 for the risk framing.

**All 5 event gaps are xx99-worthy and cross-cutting** (they may bind
to Group 1900 event-architecture-arc deliverables). Cat A should not
attempt to close these; they require design decisions about the event
bus itself (which is Group 1900's scope per D71).

---

## 11. Existing Documentation

**Q10 (§9): Existing documentation.**

| Doc | Coverage | Location |
|---|---|---|
| `docs/topics/celery-workers.md` §"Observability" | Signal handlers (3 named, not 5), field list (10 of 16 named), task volume breakdown (S1048), memory telemetry (S1167), wall-clock/top_consumers, monitor-task overhead operator playbook | `:182-306` |
| `docs/topics/agent-system.md` | **NO Cat A cross-reference** — agent tasks not documented as observability surface via CeleryTaskEvent | — |
| `docs/topics/infrastructure.md` | **NO Cat A cross-reference** — Celery infra documented but not signal-handler observability | — |
| `docs/PLATFORM_INVENTORY.md` | Celery task count (415) + PeriodicTask count (92 enabled) as autoblock claims; no Cat A specific narrative | Executive Summary section |
| `docs/PLATFORM_WHAT_IT_IS.md` | **NO Cat A narrative** — observability infrastructure not surfaced as a named platform component | — |
| `docs/AUDIT_FINDINGS.md` §12 | Canonical Celery deferred-by-policy list (feeds `audit_celery_zero_fire` KNOWN_DEFERRED); retention-bounded caveat noted | §12 |
| `docs/audit-2026/01-celery.md` | Audit-era snapshot — task success rate 100% (10,645/10,647), 59 agent-related task events; verified runtime | `:1-136` |
| Handoffs S983, S1064, S1113 (implied), S1165, S1167, S1169, S1219, S1245, S1246 | Session-level provenance for every Cat A field addition + behavioral change | `docs/handoffs/SESSION_*.md` |

### Documentation gaps (input to §14 known drift)

- **Signal-handler count drift** — parent §3 A + `celery-workers.md:186-189` both cite 3 signal handlers; actual is 5.
- **Field-set drift** — `celery-workers.md:187-189` cites 10 fields; actual is 16 (missing priority_matched/priority_name/throttle_class + rss_mb_start/rss_mb_end/rss_delta_mb + agent_name).
- **`on_agent_task_failure_bridge` (S1219) cross-cat write** — not documented in `celery-workers.md` or `agent-system.md`.
- **`stamp_sent_at` + queue-age computation** — not documented in `celery-workers.md`; only in-code docstring.
- **QUEUED / REVOKED writers** (gateway + ops_autopilot) — not documented in `celery-workers.md`.
- **Monitor-task decorator timeouts** — documented in `celery-workers.md:255-276` at signal-handler-adjacent level; probe-decomposition root fix flagged as deferred.
- **agent_name backfill posture** — documented in `models_celery_telemetry.py:43-46` docstring but not in `celery-workers.md` as a known limitation.
- **Retention-bounded zero-fire caveat** — documented only in `SESSION_1245_*.md` handoff; not surfaced in `celery-workers.md` or `AUDIT_FINDINGS.md`.
- **`system_health_tool` doc-fiction** — parent §3 A line 409 mentions `system_health_tool` as a PA tool consumer; no such tool exists in `pa_tool_schemas.py` or `tool_dispatcher.py`.

---

## 12. Research Coverage

**Q13 (§9): Research coverage.**

**MODERATE** per playbook §12.

Justification:
- ✓ 8+ sessions shipped Cat A infrastructure incrementally (S983 baseline, S1064 retention, S1086 priority fields, S1165 memory fields + connection hygiene, S1167 top_consumers + memory sampling, S1169 agent_name dim + decorator timeouts, S1219 bridge, S1245 zero-fire probe, S1246 `.name` fix)
- ✓ Topic doc `celery-workers.md` covers the surface at operator-playbook level
- ✓ Audit doc `audit-2026/01-celery.md` verified runtime behavior at Apr-2026 baseline
- ✗ No dedicated Cat A research doc prior to this audit (S1273 §3.25 + S1274 §11.6 frame the 5-layer dedup problem cross-domain but don't close Cat A specifically)
- ✗ Narrative anchor (`PLATFORM_WHAT_IT_IS.md`) has no observability-infrastructure section
- ✗ Correlation-primitive posture (parent §5) unaddressed prior to this audit

---

## 13. Architecture Maturity

**Q12 (§9): Architecture maturity.**

**STABLE** per playbook §12.

Justification:
- **Core contract proven** — task capture + status tracking works reliably across production (audit-2026 baseline: 10,645/10,647 = 99.98% success rate).
- **Signal handlers defensively wrapped** — every handler has `try/except: log; return` guards so telemetry cannot break task execution.
- **Retention enforced** — weekly bounded-work cleanup task with configurable window; no unbounded growth.
- **Boundary violations documented + accepted** — S1219 P1 cross-cat write formalized in docstring; gateway QUEUED-write documented in inline comment; 4 legitimate parallel writers (§3 items A-D) all have clear per-case justification.
- **Known debt scoped** — monitor-task overhead (S1167 partial close), agent_name backfill (intentional gradual fill), correlation-primitive-not-FK'd (design choice for telemetry model).

Not CANONICAL because:
- Documentation drift (5-vs-3 handler count; 16-vs-10 field count; missing surface docs for bridge/QUEUED/REVOKED writers)
- 5 event-gap candidates (§10) unclosed
- 8 downstream models declare `celery_task_id` CharField without unified FK contract

---

## 14. Known Drift

**Q27 (§9): Known drift.**

| # | Drift | Doc claim | Code reality | Severity |
|---|---|---|---|---|
| D1 | Signal-handler line range | Parent §3 A + `celery-workers.md:186-189`: "signal handlers at `celery_telemetry.py:74-177`" (3 handlers) | Actual: `:74-300` with 5 handlers (on_task_prerun L74, on_task_postrun L115, on_task_failure L177, on_agent_task_failure_bridge L240, stamp_sent_at L289) | MEDIUM |
| D2 | Field-set completeness | `celery-workers.md:187-189` lists 10 fields | Actual: 16 persistent fields (missing priority_matched/priority_name/throttle_class + rss_mb_start/rss_mb_end/rss_delta_mb + agent_name from doc list) | MEDIUM |
| D3 | `system_health_tool` PA tool | Parent §3 A line 409: named as Cat A consumer | Does NOT exist in `pa_tool_schemas.py` or `tool_dispatcher.py` | LOW (doc-fiction) |
| D4 | QUEUED status "never written" (Sub-Agent 4 initial claim) | Parent §3 A implies STARTED-first flow | Verified writer exists at `td_handlers_gateway.py:988` (legitimate gap-fill for status polling) | RESOLVED (initial finding wrong; QUEUED IS legitimately written by 1 source) |
| D5 | REVOKED status write path | UNKNOWN per Sub-Agent 3 initial claim | Verified: 2 writers — `ops_autopilot.py:100` (stuck-task sweep) + `td_handlers_gateway.py:1041` (cockpit revoke) | RESOLVED |
| D6 | `cleanup_celery_task_events` decorator | Sub-Agent 1 UNKNOWN | Verified `@shared_task` at `core/tasks.py:4394` | RESOLVED |
| D7 | agent_name backfill % | Documented as "gradual fill" (S1169) | Actual % at HEAD UNKNOWN — requires runtime ORM probe | ACCEPT AS UNKNOWN (§18) |
| D8 | Signal-handler wiring in `core/celery.py` | Parent §3 A: "Import this module in core/celery.py after autodiscover_tasks() to activate" | Verified `core/celery.py:941` (import placed after autodiscover_tasks at L812) | CLEAN |
| D9 | Beat schedule cadence | Not stated in parent §3 A or `celery-workers.md` | Weekly Sunday 04:50 UTC per `core/celery.py:153-158` (S1165 COO #3 staggered) | LOW — should be documented in `celery-workers.md` |
| D10 | Narrative anchor coverage | `PLATFORM_WHAT_IT_IS.md` implies observability is a first-class platform layer | No Cat A section in narrative anchor | LOW for Cat A runtime correctness; **likely elevated during xx99 narrative-anchor update prioritization** (per Rigby SIGN F3 2026-07-03) — this drift doesn't mislead Cat A runtime understanding, but Group 1700 xx99 anchor-update work will treat narrative-anchor coverage as a higher priority once all 6 children are complete. |

---

## 15. Known Technical Debt

**Q26 (§9): Known technical debt.**

| # | Debt | Severity | Session ref | Status |
|---|---|---|---|---|
| T1 | agent_name backfill gradual-fill | MEDIUM | S1169 docstring `:43-46` — "no backfill — gradual fill per Rigby's skip-joins-in-v1 stance" | ACCEPTED; % impact UNKNOWN at HEAD |
| T2 | Monitor-task overhead spiral (probe decomposition deferred) | HIGH | S1167 `celery-workers.md:255-276` + S1169 decorator timeouts (partial close) | PARTIALLY CLOSED — decorator-side timeouts + `broadcast` queue landed; probe-decomposition root fix deferred |
| T3 | `on_agent_task_failure_bridge` hard-SIGKILL gap | LOW | S1219 P1 docstring `celery_telemetry.py:251-254` | ACCEPTED — 30-min watchdog remains safety net; hard SIGKILL (`time_limit=3900`) can't be caught at signal boundary |
| T4 | RSS measurement platform-quirk visibility | MEDIUM (UNKNOWN) | No handoff reference; exception-swallow at `_get_rss_mb:28-33` | UNKNOWN — no test coverage of macOS/Linux/Railway psutil quirks |
| T5 | 8 downstream models with `celery_task_id` CharField (no FK) | LOW (design choice) | Multiple sessions (baseline) | ACCEPTED for telemetry model; xx99 D74 axis evidence |
| T6 | Retention window default (30 days) rationale undocumented | LOW | S1064 handoff mentions "unbounded table growth" motivation but 30-day choice rationale isn't documented | ACCEPTED; likely arbitrary starting point |
| T7 | Documentation drift D1-D3 above | LOW | This audit | Owed to xx99 anchor-update PR |
| T8 | 5 event-gap candidates (§10) | MEDIUM cross-cutting | This audit | Bind to Group 1900 event architecture arc (D71 delegation) |

---

## 16. Boundary Violations

**Q24 (§9): Services violating boundaries.**

### Violation candidates evaluated

| # | Candidate | Assessment | Verdict |
|---|---|---|---|
| B1 | `on_agent_task_failure_bridge` writes to AgentExecution (Cat C) from Cat A signal handler | Localized (single handler); lazy import; documented docstring; idempotent (filter-scoped); necessary correctness fix (S1219 P1) | **LEGITIMATE CROSS-CAT EXCEPTION (Cat A→Cat C)** — distinct terminology per Rigby SIGN F1: this is a fire-alarm circuit-breaker that writes to another category's schema, not a "parallel writer." xx99 should codify as documented Cat A/C boundary carve-out. |
| B2 | `td_handlers_gateway.py:988` creates CeleryTaskEvent row with `status='QUEUED'` from non-signal-handler context | Solves real problem (status polling gap between dispatch and prerun); inline comment documents intent; wrapped in try/except | **LEGITIMATE PARALLEL WRITER** — writes Cat A's own schema from a non-signal-handler code path (distinct from B1's cross-cat scope). xx99 should codify "signal handlers own SUCCESS/FAILURE/STARTED; gateway owns QUEUED; ops_autopilot + gateway own REVOKED" |
| B3 | `ops_autopilot.py:100` writes REVOKED from stuck-task sweep | Bounded (MAX_REVOKES_PER_RUN); observed only after signal handler fires prerun; guards on STARTED status | **LEGITIMATE PARALLEL WRITER** (Cat A-internal) |
| B4 | `td_handlers_gateway.py:1041` writes REVOKED after cockpit_tool.revoke_task | User-initiated; guards `event.status in ('QUEUED', 'STARTED')`; wrapped | **LEGITIMATE PARALLEL WRITER** (Cat A-internal) |
| B5 | `priority/enforce.py:307-313` writes S1086 priority router fields | Called after prerun; writes 3 dedicated fields; separate from lifecycle-status writes | **LEGITIMATE PARALLEL WRITER** (Cat A-internal) — priority fields are S1086's schema addition; PriorityRouter is their natural owner |

**Overall:** No violation to flag. Per Rigby SIGN cycle 1 F1 (2026-07-03), the 5 candidates split into two distinct categories:

- **4 LEGITIMATE PARALLEL WRITERS (Cat A-internal)** — B2/B3/B4/B5 write Cat A's own schema (`CeleryTaskEvent`) from non-signal-handler code paths. Their justification is business-case coverage that signals cannot serve (gateway QUEUED gap-fill, revoke_task lifecycle, ops_autopilot stuck-task sweep, priority-router metadata).
- **1 LEGITIMATE CROSS-CAT EXCEPTION (Cat A→Cat C)** — B1 is a **fire-alarm circuit-breaker** in Cat A code that writes to a Cat C schema (`AgentExecution`). This is materially different from parallel writers: it crosses category boundaries, not just handler boundaries.

**Recommendation for xx99:** codify Cat A boundary rule with 4 sub-clauses:

1. Signal handlers own lifecycle status transitions (STARTED / SUCCESS / FAILURE).
2. `cockpit_tool.trigger_task` gateway owns pre-prerun QUEUED gap-fill; `cockpit_tool.revoke_task` gateway + `ops_autopilot` stuck-task sweep own REVOKED.
3. `PriorityRouter.enforce_priority` owns the 3 S1086 PR 3b priority-router fields.
4. `on_agent_task_failure_bridge` is a **cross-cat exception**, not a parallel writer — it lives in Cat A signal-handler code but the target schema is Cat C. xx99 must decide whether the code stays in `celery_telemetry.py` or moves to Cat C's codebase.

The B1 cross-cat exception's terminology matters because future audits
(especially Cat C S1703) inherit this framing. Treating B1 as an
ordinary Cat A "parallel writer" would obscure the boundary decision
xx99 owes. xx99 should decide whether
this stays in `celery_telemetry.py` (Cat A code path, Cat C data)
or moves to Cat C's codebase with a Celery-signal-connect that Cat C
owns (moves the physical location of the code without changing runtime
behavior).

---

## 17. Duplicate or Overlapping Systems

**Q23 (§9): Models overlapping with other domains.**

**No field-level overlaps** between `CeleryTaskEvent` and any Cat B/C/D/E/F model. See §4 FK graph + §9 Integrations for the full analysis.

The **only structural overlap-adjacent pattern** is the 8 downstream models with `celery_task_id` CharField (see §4). These are consumer-side references, not schema overlaps — no duplicate task-lifecycle data lives in them. They are pointers, not duplicates.

**Comparison to sibling categories (Cat B/C/D/E) at HEAD:**

| Category | Model | Correlation field | FK'd? |
|---|---|---|---|
| Cat A | `CeleryTaskEvent` | `task_id` (unique, indexed) | — (root) |
| Cat B | `LLMCallEvent` | `execution_id` (UUIDField) | Implicit → `AgentExecution.id`; not declared as FK |
| Cat C | `AgentExecution` | multiple candidate PKs — parent §3 Cat C landmine (3 classes) | Canonical class determined by P3 audit |
| Cat D | `ToolCallRecord` | `trace_id`, `conversation_id` UUIDs | Not declared as FK |
| Cat E | `OpsRunEvent` | `run` FK → `OpsRun`; `execution_id`, `trace_id` scalars | `run` FK declared; other correlation scalars |

**Cat A is the only category with a scalar unique-index task-lifecycle
key at HEAD.** LLMCallEvent, ToolCallRecord, and OpsRunEvent all use
UUIDs; AgentExecution's canonical PK is TBD per Cat C landmine. This
is Cat A's D74 axis input: if xx99 decides on canonical execution_id
+ trace_id spine, Cat A's `task_id` primitive is the natural anchor
because it's the only one Celery-native and index-backed.

---

## 18. Ownership Gaps

**Q25 (§9): Ownership gaps.**

| Area | Owner? |
|---|---|
| `CeleryTaskEvent` model schema evolution | Implicit (whoever owns the S1086/S1165/S1167/S1169 migrations); no OWNER annotation on model or handoffs |
| Signal handler correctness + coverage | Implicit (Celery infra); most recent change S1246 by Claude Code |
| Retention window default | UNKNOWN — no OWNER for the 30-day choice; env-var configurable |
| Monitor-task overhead debt (T2) | S1170 caller-site migration sweep landed; probe-decomposition root fix UNASSIGNED |
| Documentation drift (T7) | UNASSIGNED for cross-doc updates (celery-workers.md + PLATFORM_INVENTORY.md + PLATFORM_WHAT_IT_IS.md); xx99 anchor-update PR will assign |
| Event-gap candidates (T8) | Cross-cutting to Group 1900 event architecture arc per D71 delegation |
| agent_name backfill % measurement (T1) | UNASSIGNED — should get an ORM probe management command |
| RSS measurement platform-quirk test coverage (T4) | UNASSIGNED |

---

## 19. Recommended Future Research

**Q28 (§9): Recommended future research.** Ranked by architectural
uncertainty × risk × unblocked flows.

### R1 (HIGH priority) — task_id ↔ execution_id ↔ trace_id correlation-primitive spine posture

Contribute Cat A's evidence to xx99's D74 axis:
- **Load-bearing question:** Are the 5 execution-telemetry layers (Cat A/B/C/D/E) structurally separable OR do they require canonical unification?
- **Cat A's input:** task_id is a coverage-complete singleton primitive; 8 downstream `celery_task_id` CharFields are string-based references without FK. If unification is chosen, task_id → execution_id spine work is a Cat A/C joint migration.
- **This is xx99 (S1799) scope, not P1 scope.** Cat A audit contributes the evidence; xx99 owns the axis resolution.

### R2 (HIGH priority) — Monitor-task probe-decomposition root fix (T2)

- **Precedent:** S1167 top_consumers exposed monitor tasks at p95=1048s / 1880s. S1169 partial close via decorator timeouts.
- **Root fix:** Decompose broker/Redis inspect() calls into non-blocking probes per `celery-workers.md:261`. Blocked on someone owning the design.
- **Impact:** Monitor overhead spiral risk persists until this ships.

### R3 (MEDIUM priority) — agent_name backfill % measurement + backfill decision

- **Ask:** What % of CeleryTaskEvent rows have `agent_name=''` at HEAD? Distribution by task_name?
- **Deliverable:** `manage.py audit_celery_agent_name_coverage` mgmt command that reports coverage % per top-100 task names, split by pre-S1169-migration-cutoff vs post.
- **Decision required:** If coverage < X%, ship a bulk backfill via `_extract_agent_name` re-run on `task_kwargs` retrieved from Celery result backend (if retrievable).

### R4 (MEDIUM priority) — Retention-cleanup failure detection (T3 event gap)

- Emit a specific event / alert when `cleanup_celery_task_events` fails, distinct from generic Celery task_failure.
- Alternatively: add a metric that tracks days-since-last-successful-cleanup; alert if >14 days.

### R5 (MEDIUM priority) — QUEUED-to-STARTED-transition timeout

- Extend `ops_autopilot` stuck-task sweep to cover QUEUED rows that never receive a prerun (indicates broker/worker crash between gateway create and worker pickup).

### R6 (LOW priority) — RSS measurement platform-quirk test coverage

- Add unit tests exercising `_get_rss_mb` with mocked psutil failures.
- Add integration test on Railway prod (Linux container) confirming RSS values are non-trivial and match expected process memory.

### R7 (LOW priority) — Realtime WebSocket push of task-lifecycle events

- Currently Cat A is pull-only (SQL queries). Realtime dashboards would benefit from a `channel_layer.group_send` from `on_task_prerun`/`postrun`/`failure`.
- **Design tradeoff:** WebSocket push adds coupling between signal-handler code and Channels infrastructure; may violate telemetry-must-never-break-task invariant.
- Not urgent; likely blocked on Group 1900 event architecture decisions.

### R8 (LOW priority) — 8 downstream models `celery_task_id` FK reconciliation

- Consider whether the 8 downstream models (`AISeriesItem`, `ContentPipelineRun`, `ConceptForgeRun`, `SpiderExecution`, `WorkflowExecution`, `ScheduledImageGeneration`, `WorkflowRun`, `ExecutionRun`) should all point at a common FK'd correlation primitive.
- **Constraint:** telemetry retention (30 days) means FK'd rows would need ON DELETE SET NULL or ON DELETE CASCADE semantics.
- Related to R1 spine posture.

---

## 20. Appendix

### 20.1 Files inspected

**Cat A production code:**
- `core/models_celery_telemetry.py` (102 lines) — read in full
- `core/celery_telemetry.py` (301 lines) — read in full
- `core/tasks.py:4386-4404` (cleanup task) — read
- `core/celery.py:150-158, 812, 941` (beat schedule + wiring) — read
- `core/settings.py:102` (retention setting) — grep-verified
- `core/services/priority/enforce.py:301-320` (S1086 writer) — grep-verified
- `core/services/ops_autopilot.py:85-113` (REVOKED writer + stuck-task sweep) — read
- `core/services/td_handlers_gateway.py:975-1042` (QUEUED + REVOKED writers) — read

**Cat A consumers (verified via grep for `CeleryTaskEvent.objects`):**
- `core/views_celery_api.py:256-410`
- `core/views_status_api.py:24-61`
- `core/views_diagnostics.py:1396-1402`
- `core/views_rag_embeddings.py:1515-1517`
- `core/services/td_handlers_ops.py` (~20 query sites)
- `core/services/td_handlers_content.py:3590-3592`
- `core/services/td_handlers_core.py:677-1075`
- `core/services/td_handlers_gateway.py:687-2192`
- `core/services/priority/enforce.py:301+`
- `core/services/nervous.py:405-406`
- `core/services/pa_tool_schemas.py` (schemas ref)
- `core/tasks.py:5607-5614` (diagnostic reader)
- `core/agents/workflow_orchestration_agent.py:4847-4849`
- `core/management/commands/audit_celery_zero_fire.py:254-338`
- `core/management/commands/ops_verify.py:88-93, 337-591`
- `core/management/commands/pa_acks_health.py:337-591`

**Migrations:**
- `core/migrations/0235_celery_task_event.py` — CREATE
- `core/migrations/0255_celerytaskevent_memory_fields.py` — ADD 3 memory fields
- `core/migrations/0330_priority_router_telemetry_fields.py` — ADD 3 priority fields
- `core/migrations/0355_session_1169_celerytaskevent_agent_name.py` — ADD agent_name

### 20.2 Docs inspected

- `docs/research/domains/observability/1700_observability_domain_scoping.md` (parent scoping)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §9, §11.2, §12, §13, §14
- `docs/topics/celery-workers.md` §"Observability" (`:182-306`)
- `docs/topics/agent-system.md` (grep for CeleryTaskEvent: no matches)
- `docs/topics/infrastructure.md` (grep for CeleryTaskEvent: no matches)
- `docs/audit-2026/01-celery.md` (`:1-136`)
- `docs/AUDIT_FINDINGS.md` §12 (canonical deferred list)
- `docs/PLATFORM_INVENTORY.md` executive summary
- `docs/PLATFORM_WHAT_IT_IS.md` (grep for CeleryTaskEvent narrative: no matches)
- `docs/handoffs/SESSION_983_CELERY_OBSERVABILITY_AND_SKIN_FIX.md`
- `docs/handoffs/SESSION_1165_COO_BACKLOG_TRIPLE_MUST_CLOSE.md`
- `docs/handoffs/SESSION_1167_COO_BACKLOG_5_AND_7_CLOSE.md`
- `docs/handoffs/SESSION_1169_CARRYOVER_QUEUE_CLOSE.md`
- `docs/handoffs/SESSION_1245_P2_CELERY_CONNECTIVITY_AUDIT_PLUS_AUDIT_FINDINGS_12_VALIDATION.md`
- `docs/handoffs/SESSION_1246_S1245_BONUS_FINDINGS_CLOSED_PLUS_AUDIT_AXIS_PLUS_CONTENT_TASK_RETIREMENT_PLUS_FLEET_VERIFICATION.md`

### 20.3 Grep patterns used

- `CeleryTaskEvent\.objects\.(create|update|update_or_create|filter.*update)` — writer inventory
- `event\.status\s*=|event\.priority_matched\s*=|event\.priority_name\s*=|event\.throttle_class\s*=` — field-level writers
- `ForeignKey.*CeleryTaskEvent|celery_task_event|celerytaskevent` — FK graph
- `CELERY_TASK_EVENT_RETENTION_DAYS` — retention setting + cleanup
- `'REVOKED'|"REVOKED"|status=.*REVOKED` — REVOKED writer verification
- `import.*celery_telemetry|core\.celery_telemetry` — wiring in `core/celery.py`
- `system_health_tool` in `core/services/pa_tool_schemas.py` + `core/services/tool_dispatcher.py` — doc-fiction verification

### 20.4 Unresolved unknowns

- U1 — % of CeleryTaskEvent rows at HEAD with `agent_name=''` (requires ORM probe)
- U2 — Actual data volume at HEAD given 30-day retention (requires ORM probe)
- U3 — RSS measurement reliability on Railway prod (Linux container) vs macOS dev
- U4 — Whether `AgentExecution.input_data` JSONField has GIN index for `input_data->>'celery_task_id'` lookup (grep-worthy but outside Cat A scope; P3 Cat C audit territory)
- U5 — Whether cleanup task hangs > 3600s expiry occur in production (would require Celery observability query)

### 20.5 Rigby SIGN cycle 1 fold notes

**Status: SIGN-with-edits at High confidence** (Rigby SIGN cycle 1 delivered 2026-07-03; D48 preemptive stability-probe gate 18th arm HOLDING CLEAN — 4-question single-batch pattern held for the 13th-consecutive-fully-clean arm per S1503–S1700+S1701 pattern).

**Pin nuance for xx99 provenance:** Fresh SIGN isolation pin `pa-3147aef9db4945ac` was minted via `session_tool.create_fresh` at S1701 open per playbook §15 promoted rule. However, `tools/pa_local.sh` wrapper does not support runtime `--conversation` override (it hard-codes the arc pin at L128); actual SIGN routing landed on the arc pin `pa-e7fbacc996b34b44`. This follows the S1600 parent-scoping precedent where the arc pin doubles as SIGN pin. The unused fresh SIGN pin `pa-3147aef9db4945ac` was minted but never received SIGN traffic; it is retired at S1701 close per playbook §16 discipline. Follow-up: wrapper enhancement to support per-child SIGN pin routing is a nice-to-have (not blocking).

**3 folds landed pre-commit:**

- **F1 (MEDIUM) — Boundary terminology clarity.**
  - **Driver:** Prevent scope confusion in Cat C S1703 audit + avoid misclassifying `on_agent_task_failure_bridge` as an ordinary Cat A "parallel writer."
  - **Affected sections:** §1 Executive Summary finding #4; §16 Boundary Violations B1 verdict cell + §16 overall verdict paragraph.
  - **Edit:** Labeled B1 as **"LEGITIMATE CROSS-CAT EXCEPTION (Cat A→Cat C)"** distinct from the 4 parallel writers (B2/B3/B4/B5) which write Cat A's own schema. §16 verdict paragraph now splits into 2 categories + adds a 4th sub-clause to xx99 boundary-rule recommendation.

- **F2 (LOW) — Downstream `celery_task_id` consumer count consistency.**
  - **Driver:** Avoid poisoning D74 handoff to P2 (Cat B) with a trivial counting ambiguity.
  - **Affected sections:** §4 FK graph, §9 Correlation primitive posture, §13 Architecture Maturity, §15 T5, §17 Duplicate/Overlapping Systems, §19 R8, §10 event-gap #5.
  - **Edit:** Replaced all "7 downstream" / "7 candidates" / "7 non-Cat-A models" language with "8" (correct enumeration: `AISeriesItem`, `ContentPipelineRun`, `ConceptForgeRun`, `SpiderExecution`, `WorkflowExecution`, `ScheduledImageGeneration`, `WorkflowRun`, `ExecutionRun`). Model list now spelled out inline at §9's primary claim.

- **F3 (LOW) — D10 severity footnote (Cat A vs xx99 priority).**
  - **Driver:** Preserve §14 severity ladder integrity while acknowledging likely xx99 prioritization.
  - **Affected sections:** §14 D10 row.
  - **Edit:** Added sentence to D10 severity cell: "LOW for Cat A runtime correctness; likely elevated during xx99 narrative-anchor update prioritization (per Rigby SIGN F3 2026-07-03)."

**Rigby SIGN cycle 1 CONFIRMED verdicts (no folds required):**

- **Q1 coverage completeness verdict** — CONFIRM (High). 5 candidates correctly framed as bounded, business-justified exceptions/parallel writers with F1 terminology fold applied.
- **Q2 documentation drift severity ladder** — CONFIRM (Medium-High). D1/D2 MEDIUM + D3 LOW appropriate for Cat A; D10 LOW appropriate for Cat A but flagged for xx99 elevation via F3.
- **Q3 correlation primitive posture completeness (D74 evidence)** — CONFIRM (High). §9 is complete for Cat A's contribution-only mandate. GIN-index question on `AgentExecution.input_data` is P3 (Cat C) territory, correctly captured as U4.
- **Q4 §19 R1-R8 ranking sanity check** — CONFIRM (Medium-High). R2 stays HIGH as separate follow-on ops/infra initiative (not bundled with xx99 anchor-update tranche). R7 correctly LOW given telemetry-must-never-break-task invariant + likely downstream of Group 1900 event-architecture decisions.

**No further SIGN cycles required for S1701; F1-F3 folds are pre-commit; audit ships at HEAD post-fold.**

### 20.6 Verifier-loop corrections landed

Pre-Explore verifier-loop corrections applied to Explore sub-agent prompts:
- Corrected signal-handler line-range claim (parent §3 A `:74-177` → actual `:74-300` with 5 handlers).
- Enumerated `_get_rss_mb`, `_extract_agent_name`, `_extract_task_name` helper functions.
- Enumerated known writer / reader / consumer targets for each Explore focus.

Post-Explore verifier-loop corrections applied to sub-agent findings:
- **Sub-Agent 1** UNKNOWN on `cleanup_celery_task_events` decorator → **resolved YES** (`@shared_task` at `core/tasks.py:4394`).
- **Sub-Agent 3** UNKNOWN on REVOKED writer → **resolved** (2 writers: `ops_autopilot.py:100`, `td_handlers_gateway.py:1041`).
- **Sub-Agent 4** initial claim of "zero non-signal-handler writers" → **corrected** to 4 legitimate parallel writers (`td_handlers_gateway.py:988` QUEUED, `:1041` REVOKED, `ops_autopilot.py:100` REVOKED, `priority/enforce.py:307-313` priority fields).
- **Sub-Agent 5** — `system_health_tool` PA tool doc-fiction confirmed (does not exist in `pa_tool_schemas.py` or `tool_dispatcher.py`).
- **Parent §3 A signal-handler line range** — drift confirmed and elevated to §14 D1.

---
