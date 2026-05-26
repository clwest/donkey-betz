---
title: "Invention Disclosure A: Evidence-Gated Autonomous Agent Blocking with Post-Action Verification and Rollback"
kind: invention_disclosure
disclosure_id: A
workstream: WS1 (Ops Autopilot)
status: draft (Attorney Review Pending)
last_updated: 2026-03-16
originating_session: pre-session-tracking (March 16, 2026 batch)
inventor: Chris West (DonkeyKing)
provenance_confidence: HIGH
provenance_note: One of 12 invention disclosures drafted as a single March 16, 2026 batch. Frontmatter added Session 1160 (2026-05-26) as part of the patents preservation pass; body content unchanged from original draft. See `docs/patents/README.md` for workstream organization and narrative cross-link map.
maps_to_narratives:
  - docs/narratives/AGENTS_AND_AUTONOMY.md
companion_docs:
  - docs/patents/README.md
  - docs/patents/EXECUTIVE_SUMMARY.md
---

# Invention Disclosure A: Evidence-Gated Autonomous Agent Blocking with Post-Action Verification and Rollback

**Date:** March 16, 2026
**Inventors:** Chris West (DonkeyKing)
**Status:** Draft — Attorney Review Pending

---

## 1. Working Title

Evidence-Gated Autonomous Blocking of Software Agents with Deferred Verification and Automatic Rollback

---

## 2. Field / Technical Domain

Autonomous operations management for multi-agent AI systems. Specifically, methods and systems for controlling the execution of heterogeneous software agents in a distributed task-processing environment, where blocking decisions are gated by evidentiary thresholds, verified post-hoc, and automatically rolled back upon verification failure.

---

## 3. Problem (What Breaks in Prior Systems)

In multi-agent AI platforms running hundreds of autonomous agents on distributed task queues, operational failures (timeouts, provider errors, resource exhaustion) require rapid containment. Prior approaches suffer from three critical deficiencies:

**a) Ungated blocking:** Existing agent management systems (Kubernetes pod restarts, Celery worker revocation, process supervisors) apply binary kill/restart decisions without requiring structured evidence. A single timeout or error triggers immediate termination, leading to false-positive shutdowns of healthy agents experiencing transient failures.

**b) No post-action verification:** Once an agent is blocked or restarted, no mechanism verifies whether the blocking action actually improved system health. The operator cannot distinguish between a correctly blocked runaway agent and an incorrectly blocked agent that was handling a legitimately long-running task.

**c) No automatic rollback:** When a blocking decision is wrong, human intervention is required to unblock the agent. In systems with 200+ agents running 24/7 across multiple queues, this creates an operational bottleneck where incorrect blocks accumulate silently.

The result: systems oscillate between under-reacting (letting runaway agents burn budget) and over-reacting (blocking healthy agents), with no closed-loop correction.

---

## 4. Solution Summary

A three-phase autonomous control loop for multi-agent systems:

1. **Evidence Collection**: Raw failures (timeouts, errors) are recorded as structured `FailureDetection` records linked to deduplicated `FailureSignature` entries. Evidence accumulates over time without triggering action.

2. **Evidence-Gated Blocking**: An autonomous policy engine (`OpsAutopilot`) evaluates whether accumulated evidence meets configurable thresholds (e.g., `require_evidence_count >= 3`) before proposing a block action. Pre-check rules enforce additional constraints (max concurrent blocks, minimum interval between actions on the same agent).

3. **Deferred Verification + Rollback**: After a block is applied, a deferred verification task is scheduled (via distributed task queue). The verifier checks whether the block improved system health (e.g., error rate dropped). If verification fails, the system automatically rolls back the block and restores the agent to its previous state.

All actions, verifications, and rollbacks are recorded in an audit trail accessible via natural-language PA interface.

---

## 5. As-Built Mechanism (Numbered Steps + Components)

### Phase 1: Evidence Collection

**Step 1 — Timeout Detection.** When an agent exceeds its per-type wall-clock timeout (enforced via `ThreadPoolExecutor` with `max_workers=1` in `core/tasks_agents.py:1856-1933`), the system catches `_FuturesTimeout` and calls `_record_timeout_signature()`.

**Step 2 — Signature Deduplication.** `_record_timeout_signature()` (`core/tasks.py:187-242`) computes a deterministic signature string `TIMEOUT_{source}_{agent_name}` and generates an MD5 hash via `FailureSignature.generate_hash()`. The system calls `get_or_create()` on `FailureSignature` (model in `core/models_diagnostic_pipeline.py:23-145`) using `signature_hash` as the uniqueness key.

**Step 3 — Occurrence Tracking.** `FailureSignature.increment_occurrence()` atomically increments `occurrence_count` and updates `last_seen_at`. This tracks frequency without creating duplicate records.

**Step 4 — Detection Recording.** A `FailureDetection` record (`core/models_diagnostic_pipeline.py:147-237`) is created with:
- `signature` FK linking to the deduplicated signature
- `source_type = 'agent_execution'`
- `source_id` = UUID of the `AgentExecution` record
- `context_snapshot` = JSON dict with `agent_name`, `timeout_source` ('wall_clock' | 'watchdog_cleanup' | 'celery_hard_limit'), `elapsed_seconds`, `task_name`

**Step 5 — Multi-Source Collection.** Evidence accumulates from three independent sources:
- Wall-clock guard (ThreadPoolExecutor timeout in execute_agent_task)
- Cleanup watchdog (stale execution scanner running every 30 minutes)
- Celery hard time limit (worker-level SIGKILL)

Each source tags its `timeout_source` field, enabling the policy engine to distinguish transient from systemic failures.

### Phase 2: Evidence-Gated Blocking

**Step 6 — Policy Evaluation.** The `OpsAutopilot._policy_timeout_spike_containment()` (`core/services/ops_autopilot/core.py:457-570`) runs on a 10-minute cycle. It queries `FailureSignature` records with `category='timeout'` and `last_seen_at` within the configured window (`TIMEOUT_SPIKE_WINDOW_MINUTES = 60`).

**Step 7 — Evidence Threshold Check.** For each agent with timeout signatures, the policy checks: `occurrence_count >= TIMEOUT_SPIKE_THRESHOLD` (default: 3). Agents below threshold are monitored but not acted upon.

**Step 8 — Pre-Check Validation.** Before proposing a block, the `ActionVerifier` (`core/services/ops_autopilot/verification.py:236-534`) enforces pre-check rules:
- `max_concurrent_blocks = 3`: No more than 3 agents may be blocked by autopilot simultaneously (queried via `AgentControlEntry.objects.filter(status='blocked', blocked_by='ops_autopilot')`)
- `min_interval_minutes = 15`: Cannot re-block the same agent within 15 minutes (queried via `AutopilotAction` records)
- `require_evidence_count = 3`: Must have >= 3 `FailureDetection` records for this signature

If any pre-check fails, the action is rejected with a structured reason and no block is applied.

**Step 9 — Block Execution.** Upon passing pre-checks, `_execute_block()` (`core/services/ops_autopilot/core.py:2715-2765`) creates or updates an `AgentControlEntry` record:
```
AgentControlEntry.update_or_create(
    agent_name=agent_name,
    defaults={
        status: 'blocked',
        reason: '<evidence summary, max 255 chars>',
        blocked_at: now(),
        blocked_by: 'ops_autopilot',
        ttl_hours: 0.5  (TIMEOUT_BLOCK_TTL_MINUTES / 60)
    }
)
```

**Step 10 — Multi-Point Enforcement.** The block takes effect at 4 independent enforcement points without requiring centralized coordination:
1. `core/tasks_agents.py:1648-1661` — `execute_agent_task()` checks `AgentControlEntry.get_blocked_names()` before Celery task execution
2. `core/agent_router.py:869-881` — `route()` checks `AgentControlEntry.is_blocked()` before synchronous agent instantiation
3. `core/tasks_ops.py:3428-3430` — Action item dispatch checks blocked agents before initiative stage automation
4. `core/services/learning_read_service.py:184-195` — Learning override checks if recommended agent is blocked before suggesting it

### Phase 3: Deferred Verification + Rollback

**Step 11 — Verification Scheduling.** `ActionVerifier.record_and_verify()` (`verification.py:411-445`) creates an `AutopilotAction` record with `verification_state='pending'` and schedules a deferred Celery task:
```
verify_autopilot_action.apply_async(
    args=[action.id],
    countdown=verify_delay_seconds  # configurable, default ~30 min
)
```

**Step 12 — Outcome Verification.** The deferred task calls `ActionVerifier.verify_action()` (`verification.py:462-534`). For `block_agent` actions, it checks:
- Did the error rate for this agent drop after the block was applied?
- Are there new timeout signatures since the block?
- Has the agent's TTL expired naturally (lazy evaluation)?

Verification produces one of: `verified_success`, `verified_partial`, `verified_failure`.

**Step 13 — Automatic Rollback.** On `verified_failure`, `_rollback_remediation()` (`verification.py:798-856`) executes the inverse action:
- For `block_and_wait` type: `AgentControlEntry.objects.filter(agent_name=agent_name).update(status='enabled')`
- For `timeout_adjust` type: Restores original timeout from `SystemConfiguration`
- For `model_fallback` type: Removes fallback flag from `SystemConfiguration`

The `AutopilotAction` record is updated with `verification_state='rolled_back'` and `rolled_back=True`.

**Step 14 — Audit Trail.** Every action, verification, and rollback is recorded in the `AutopilotAction` table with timestamps, evidence snapshots, and outcome codes. The PA tool `agent_control_tool` (action: `audit_log`) provides natural-language access to the full history.

---

## 6. Novelty Hooks (Section 102)

The following elements are present here and absent from any single known reference:

**a) Evidence-gated blocking with configurable thresholds.** The system requires a minimum number of structured failure detections (not raw log entries) linked to a deduplicated signature before permitting autonomous blocking. The evidence threshold is configurable per action type.

**b) Pre-check validation as a separate gate.** Even when evidence thresholds are met, a secondary validation layer (max concurrent blocks, minimum interval, evidence count) must pass. This two-gate architecture prevents cascade failures where the autopilot itself becomes a source of instability.

**c) Deferred asynchronous verification.** After applying a block, the system schedules a future verification task that checks whether the block improved system health — not whether the block was applied. This distinguishes "action taken" from "action effective."

**d) Automatic inverse-action rollback.** On verification failure, the system automatically reverses the block without human intervention, using action-type-specific rollback logic (unblock, restore timeout, remove fallback flag).

**e) Multi-source evidence collection with source tagging.** Evidence comes from 3 independent detection paths (wall-clock, watchdog, Celery hard limit), each tagged with its source. This enables the policy engine to distinguish transient from systemic failures.

---

## 7. Non-Obviousness Hooks (Section 103)

**a) Lazy TTL + deferred verification creates a novel dual-timer architecture.** Known systems use either TTL-based auto-expiry (e.g., Redis key expiry) or post-action health checks (e.g., Kubernetes readiness probes), but not both on the same blocking decision. The combination is non-obvious because TTL provides a safety net against verification task failures, while verification provides correctness that TTL alone cannot.

**b) Evidence gating + pre-check validation is counter-intuitive for autonomous systems.** The natural design for an autonomous ops system is to act quickly on any anomaly. Requiring accumulated evidence *and* passing constraint checks before acting introduces deliberate inaction periods — a design that operators would not predictably choose because it appears to slow response time. The insight is that slower, evidence-based responses reduce the total count of incorrect interventions.

**c) Multi-point enforcement without centralized coordination.** Each enforcement point independently queries the same `AgentControlEntry` table. There is no message bus, no event propagation, and no eventual consistency delay (beyond DB replication). This "shared-nothing enforcement" pattern is non-obvious because distributed systems typically require coordination protocols (pub/sub, consensus) to achieve consistent behavior across components.

**d) Verification checks effectiveness, not compliance.** The verifier does not check "was the block applied?" (which is trivially true). It checks "did the error rate decrease?" — a semantically different question that requires comparing pre-block and post-block failure rates. This outcome-oriented verification is non-obvious because most operational automation verifies action completion, not action effectiveness.

---

## 8. Operational Benefits (Measurable Outputs)

- **False-positive block rate reduced**: Evidence gating with `require_evidence_count=3` eliminates single-event blocking. Agents experiencing 1-2 transient timeouts continue operating.
- **Automatic recovery**: TTL-based blocks (default 30 min for spike containment, 4h for ladder L3) auto-expire without human intervention, preventing block accumulation.
- **Budget protection**: Blocking runaway agents prevents unbounded LLM API spend. Each blocked agent saves its per-execution cost ($0.01-$0.10) multiplied by its dispatch frequency.
- **Verification catch rate**: Deferred verification identifies incorrect blocks and rolls them back, reducing unnecessary agent downtime.
- **Concurrent block cap**: `max_concurrent_blocks=3` prevents the autopilot from blocking too many agents simultaneously, maintaining minimum system throughput.
- **Audit completeness**: Every block, verification, and rollback is recorded with timestamps, evidence snapshots, and actor IDs, enabling post-incident analysis.

---

## 9. Alternative Embodiments

**a) Database-backed circuit breaker instead of Redis.** The circuit breaker state (currently in Redis cache with `circuit:{agent}:{hash}:timeouts` keys) could be stored in the same `FailureSignature` table, eliminating Redis as a dependency. Trade-off: higher write latency but better durability.

**b) Adaptive evidence thresholds.** The `require_evidence_count` could be dynamically adjusted based on agent criticality (critical agents require more evidence before blocking) or time of day (lower thresholds during off-peak hours when human oversight is unavailable).

**c) Graduated verification windows.** Instead of a fixed `verify_delay_seconds`, the verification window could scale with the severity of the block: short delays for temporary blocks, longer delays for permanent blocks, allowing more time for the system to stabilize before measuring effectiveness.

**d) Peer-agent verification.** Instead of checking aggregate error rates, the verifier could dispatch a test task to the blocked agent (in a sandbox) to determine if the underlying issue has resolved, providing a direct rather than statistical verification.

**e) Federated enforcement across clusters.** In a multi-cluster deployment, `AgentControlEntry` records could be replicated across clusters via change-data-capture, enabling a block applied in one cluster to propagate to others without centralized coordination.

**f) Human-in-the-loop override with expiry.** A human override (via PA tool) could temporarily suspend autopilot blocking for a specific agent, with its own TTL that auto-expires the override, preventing forgotten overrides from accumulating.

---

## 10. Claim Skeleton

### Independent Method Claim

A computer-implemented method for autonomously controlling execution of software agents in a distributed multi-agent system, the method comprising:

(a) recording, by a plurality of independent failure detection sources, structured failure detection records linked to deduplicated failure signature entries in a persistent data store, each failure detection record comprising a source type identifier, a context snapshot, and a foreign key to a failure signature;

(b) evaluating, by an autonomous policy engine executing on a periodic cycle, whether accumulated failure detection records for a given agent meet a configurable evidence threshold;

(c) upon the evidence threshold being met, validating the proposed blocking action against a set of pre-check constraint rules including a maximum concurrent block count and a minimum interval since the last action on the same agent;

(d) upon passing the pre-check validation, creating or updating a blocking record in a shared control table, the blocking record comprising an agent identifier, a block status, a block source identifier, and a time-to-live value;

(e) enforcing the block at a plurality of independent enforcement points that each query the shared control table without inter-point coordination;

(f) scheduling a deferred verification task to evaluate whether the blocking action improved system health by comparing post-block failure rates to pre-block failure rates; and

(g) upon verification failure, automatically executing an inverse rollback action that restores the agent to its pre-block state and recording the rollback in an audit trail.

### Dependent Claims

1. The method of the independent claim, wherein the failure detection sources comprise a wall-clock timeout guard, a stale execution cleanup watchdog, and a worker-level hard time limit.

2. The method of claim 1, wherein each failure signature is deduplicated using a cryptographic hash of a normalized signature string comprising the failure source and agent name.

3. The method of the independent claim, wherein the pre-check constraint rules further comprise a minimum required count of failure detection records linked to the failure signature.

4. The method of the independent claim, wherein the time-to-live value is evaluated lazily at read time by each enforcement point, without requiring a scheduled expiration task.

5. The method of claim 4, wherein lazy evaluation comprises: upon querying the shared control table, computing elapsed time since block creation, and if the elapsed time exceeds the time-to-live value, atomically updating the blocking record to an unblocked status before returning the query result.

6. The method of the independent claim, wherein the deferred verification task checks whether aggregate failure detection records created after the block time are fewer than those created before the block time within a comparable window.

7. The method of the independent claim, wherein the inverse rollback action is selected from a mapping of action types to rollback operations, the mapping comprising: unblocking an agent, restoring a timeout configuration, and removing a model fallback flag.

8. The method of the independent claim, wherein the audit trail records comprise an action type, evidence snapshot, verification state, rollback flag, and timestamps for action, verification, and rollback events.

9. The method of the independent claim, further comprising exposing the audit trail through a natural-language conversational interface that accepts queries for listing blocked agents, blocking or unblocking agents, and viewing recent control changes.

10. A system comprising one or more processors and memory storing instructions that, when executed, perform the method of the independent claim.

11. A non-transitory computer-readable medium storing instructions that, when executed by one or more processors, perform the method of the independent claim.

---

## 11. Diagrams to Draft

**Figure 1 — Evidence Collection and Signature Deduplication Flow**
```
[Agent Execution] --timeout--> [_record_timeout_signature()]
                                      |
                               [FailureSignature.get_or_create(hash)]
                                      |
                               [FailureSignature.increment_occurrence()]
                                      |
                               [FailureDetection.create(signature_fk, context)]
```
Three source paths feeding into the same pipeline: Wall-Clock Guard, Cleanup Watchdog, Celery Hard Limit.

**Figure 2 — Evidence-Gated Blocking Decision Flow**
```
[Policy Engine (10-min cycle)]
      |
[Query FailureSignature where category=TIMEOUT, last_seen >= window]
      |
[For each agent: occurrence_count >= threshold?] --NO--> [Monitor only]
      |YES
[ActionVerifier.pre_check()]
      |
[max_concurrent_blocks <= 3?] --NO--> [Reject: too many blocks]
[min_interval >= 15 min?]     --NO--> [Reject: too recent]
[evidence_count >= 3?]        --NO--> [Reject: insufficient evidence]
      |ALL PASS
[AgentControlEntry.update_or_create(status='blocked', ttl_hours=0.5)]
      |
[Schedule deferred verification task]
```

**Figure 3 — Multi-Point Enforcement Architecture**
```
                    [AgentControlEntry Table]
                   /          |          |          \
            [Celery]    [Router]    [Dispatch]    [Learning]
            execute_    route()     action_item   learning_
            agent_task              dispatch      override
```
Each enforcement point independently queries the same table. No message bus or event propagation.

**Figure 4 — Verification and Rollback State Machine**
```
[Action Applied] --> [verification_state='pending']
                          |
                    [Deferred task fires after N seconds]
                          |
                    [Check: error rate decreased?]
                   /                              \
          [YES]                                [NO]
    [verified_success]                    [verified_failure]
                                               |
                                         [_rollback_remediation()]
                                               |
                                         [verification_state='rolled_back']
```

---

## 12. Prior Art Buckets to Cite Against

**a) AIOps / Autonomous Incident Response (PagerDuty, Datadog, OpsGenie)**
- Teaches: automated alerting, runbook execution, incident escalation
- Does NOT teach: evidence-gated blocking with configurable thresholds, pre-check validation as a separate gate, or deferred verification with automatic rollback

**b) Circuit Breaker Pattern (Netflix Hystrix, Resilience4j, Polly)**
- Teaches: failure counting, open/half-open/closed states, automatic recovery after timeout
- Does NOT teach: multi-source evidence collection with source tagging, pre-check constraint validation before state transition, or post-transition outcome verification

**c) Kubernetes Pod Management (liveness probes, readiness probes, HPA)**
- Teaches: health checking, automatic restart, horizontal scaling
- Does NOT teach: evidence accumulation before action, deferred verification of action effectiveness (probes check pod health, not whether the restart helped), or automatic rollback of restart decisions

**d) Agent Frameworks (LangChain, AutoGen, CrewAI)**
- Teaches: agent orchestration, tool calling, multi-agent conversation
- Does NOT teach: autonomous operational control of agents themselves (these frameworks control what agents do, not whether agents should be allowed to execute), evidence-gated blocking, or verification/rollback loops

**e) Distributed Task Queue Management (Celery, Temporal, Airflow)**
- Teaches: task routing, retry policies, dead-letter queues, worker management
- Does NOT teach: agent-level (not task-level) blocking with evidence requirements, multi-point enforcement from a shared control table, or outcome-oriented verification of blocking decisions

**f) Feature Flag Systems (LaunchDarkly, Unleash, Flagsmith)**
- Teaches: runtime toggling of features, percentage rollouts, kill switches
- Does NOT teach: autonomous evidence-based toggling (flags are manually controlled), pre-check validation before toggle, or automatic rollback based on post-toggle health metrics

---

## Observability Evidence (Proving This Runs in Production)

### Database Records Created on Each Timeout
- `FailureSignature` row: `signature='TIMEOUT_WALL_CLOCK_CustomerResearchAgent'`, `signature_hash='a3f2...d8e1'`, `occurrence_count=7`, `category='timeout'`
- `FailureDetection` row: `source_type='agent_execution'`, `source_id=<AgentExecution UUID>`, `context_snapshot={'agent_name': 'CustomerResearchAgent', 'timeout_source': 'wall_clock', 'elapsed_seconds': 1502.3}`

### Redis Keys Created on Each Timeout
- `flight:CustomerResearchAgent:a8c3f21e9b7d4501:1` (single-flight lock, 30-min TTL)
- `circuit:CustomerResearchAgent:a8c3f21e9b7d4501:timeouts` = `2` (timeout counter, 24h TTL)

### Database Records Created on Block Action
- `AgentControlEntry` row: `agent_name='CustomerResearchAgent'`, `status='blocked'`, `blocked_by='ops_autopilot'`, `ttl_hours=0.5`, `blocked_at='2026-03-16T14:22:00Z'`
- `AutopilotAction` row: `action_type='block_agent'`, `verification_state='pending'`, `evidence={'signature_count': 3, 'detection_count': 7}`

### Database Records Created on Verification/Rollback
- `AutopilotAction` updated: `verification_state='rolled_back'`, `rolled_back=True`, `verified_at='2026-03-16T14:52:00Z'`
- `AgentControlEntry` updated: `status='enabled'`, `reason='Rollback: verification failed'`

---

## Examiner Story

Prior art teaches circuit breakers that trip on failure counts (Hystrix), autonomous incident response that executes runbooks on alert thresholds (PagerDuty), and Kubernetes probes that restart unhealthy pods. However, no single reference or obvious combination teaches a system that (1) requires structured evidence accumulation from multiple independent detection sources before permitting an autonomous blocking action, (2) validates the proposed action against constraint rules (max concurrent blocks, minimum interval, minimum evidence count) as a separate gate from the evidence threshold, (3) applies the block at multiple independent enforcement points that query a shared control table without inter-point coordination, and (4) schedules a deferred verification task that checks action *effectiveness* (not mere action completion) and automatically rolls back the block if verification fails. The combination is non-predictable because existing systems optimize for speed of response (block immediately on anomaly), whereas this system deliberately delays action to accumulate evidence and then verifies effectiveness after acting — a counter-intuitive design that reduces total incorrect interventions at the cost of slower initial response.
