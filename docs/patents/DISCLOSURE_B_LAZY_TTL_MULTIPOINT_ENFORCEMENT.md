# Invention Disclosure B: Lazy TTL Auto-Expire Agent Blocks with Distributed Multi-Point Enforcement

**Date:** March 16, 2026
**Inventors:** Chris West (DonkeyKing)
**Status:** Draft — Attorney Review Pending

---

## 1. Working Title

Lazy Time-to-Live Evaluation for Agent Execution Control Records with Distributed Enforcement Across Heterogeneous Execution Paths

---

## 2. Field / Technical Domain

Distributed systems control for multi-agent AI platforms. Specifically, methods for managing the operational state of autonomous software agents using database-backed control records with time-to-live semantics evaluated lazily at read time, and enforced consistently across multiple independent execution paths without centralized coordination or scheduled expiration tasks.

---

## 3. Problem (What Breaks in Prior Systems)

Multi-agent AI systems require temporary agent blocking (e.g., during remediation, after repeated failures, or during budget constraints). Existing approaches to temporary blocking have three structural problems:

**a) Scheduled expiration requires additional infrastructure.** Traditional TTL implementations (Redis key expiry, cron-based cleanup, Celery Beat tasks) require a separate scheduled process to check and expire blocks. If the scheduler fails, hangs, or is delayed, blocks persist beyond their intended duration, silently degrading system throughput.

**b) Cache-based TTL loses state on restart.** Redis-based blocking with TTL auto-expiry is fast but volatile. Worker restarts, Redis failovers, or memory pressure can evict blocking state, causing premature unblocking. Conversely, if Redis is unavailable, the system cannot check block status at all.

**c) Enforcement inconsistency across execution paths.** In systems where agents can be invoked through multiple paths (task queue, synchronous router, action dispatch, learning system), each path must independently know about blocks. Existing solutions typically enforce blocks at one entry point (e.g., the task queue), leaving other paths unprotected. Centralizing enforcement through a single gateway creates a bottleneck and single point of failure.

The result: temporary blocks either expire too early (cache eviction), too late (scheduler failure), or are enforced inconsistently (path-specific checking).

---

## 4. Solution Summary

A database-backed agent control record (`AgentControlEntry`) with time-to-live semantics that are evaluated lazily at read time by every enforcement point. No scheduled expiration task exists. Instead, each time any system component queries "which agents are blocked?", the query itself evaluates TTL for every blocked record, atomically unblocking expired entries as a side effect.

This creates an **eventually consistent, self-healing blocking system** where:
- Blocks are durable (survive restarts, failovers, and cache loss)
- Expiration happens automatically on next read (no scheduler dependency)
- Enforcement is consistent across all execution paths (shared table, independent queries)
- Audit trail is preserved (expired blocks remain as 'enabled' records with reason 'TTL expired')

---

## 5. As-Built Mechanism (Numbered Steps + Components)

### Component 1: AgentControlEntry Model

**Location:** `core/models_unified_system.py` (lines 49-105)

The `AgentControlEntry` model stores one record per agent with the following fields:

| Field | Type | Purpose |
|-------|------|---------|
| `agent_name` | CharField(unique, indexed) | Agent identifier, matches AGENT_MAP keys |
| `status` | CharField (blocked/enabled) | Current operational state |
| `reason` | CharField(255) | Human-readable explanation for block/unblock |
| `blocked_at` | DateTimeField(nullable) | Timestamp when block was applied |
| `blocked_by` | CharField(100) | Actor who applied block (system, rigby, claude-code, ops_autopilot, timeout_playbook, remediation_engine) |
| `ttl_hours` | IntegerField(nullable) | Auto-unblock duration; null = permanent block |
| `updated_at` | DateTimeField(auto_now) | Last modification timestamp |

### Component 2: Lazy TTL Evaluation

**Method:** `AgentControlEntry.get_blocked_names()` (lines 81-101)

```python
@classmethod
def get_blocked_names(cls) -> frozenset:
    blocked_qs = cls.objects.filter(status='blocked')
    names = set()
    now = timezone.now()
    for entry in blocked_qs:
        # LAZY TTL EVALUATION
        if entry.ttl_hours and entry.blocked_at:
            elapsed = (now - entry.blocked_at).total_seconds() / 3600
            if elapsed > entry.ttl_hours:
                # Atomically expire the block as a side effect of reading
                entry.status = 'enabled'
                entry.reason = f'TTL expired ({entry.ttl_hours}h)'
                entry.save(update_fields=['status', 'reason', 'updated_at'])
                continue  # Exclude from blocked set
        names.add(entry.agent_name)
    return frozenset(names)
```

**Key properties:**
1. **No scheduled task**: There is no cron job, Celery Beat task, or background thread that checks for expired blocks.
2. **Evaluation on every read**: Each call to `get_blocked_names()` evaluates TTL for *all* blocked entries.
3. **Atomic side-effect update**: Expired entries are updated to `status='enabled'` in the same query loop, persisting the unblock for future queries.
4. **Audit preservation**: The expired entry is not deleted — it remains as a record with `reason='TTL expired (Nh)'` and the original `blocked_at`, `blocked_by` fields intact.
5. **Immutable return type**: Returns `frozenset` to prevent accidental mutation by callers.
6. **Migration-safe fallback**: On exception (e.g., during migrations when table doesn't exist), returns `frozenset({'CodeGeneratorAgent'})` — a safe default that blocks only the known-dangerous agent.

**Convenience method:** `AgentControlEntry.is_blocked(agent_name)` (lines 103-105) wraps `get_blocked_names()` for single-agent checks.

### Component 3: Distributed Multi-Point Enforcement

The block is enforced at 4 independent execution paths, each querying the same `AgentControlEntry` table:

**Enforcement Point 1 — Celery Task Execution** (`core/tasks_agents.py:1648-1661`)
```python
from core.models_unified_system import AgentControlEntry
_BLOCKED_AGENTS = AgentControlEntry.get_blocked_names()
if agent_name in _BLOCKED_AGENTS:
    return {'status': 'blocked', 'agent': agent_name, 'reason': '...'}
```
Checked before the agent is instantiated in the Celery worker. Returns a blocked status dict instead of executing.

**Enforcement Point 2 — Synchronous Agent Router** (`core/agent_router.py:869-881`)
```python
if AgentControlEntry.is_blocked(agent_name):
    return AgentResult(success=False, message=f'{agent_name} disabled...')
```
Checked during synchronous `route()` calls (e.g., from PA tool handlers). Returns a failed `AgentResult`.

**Enforcement Point 3 — Action Item Dispatch** (`core/tasks_ops.py:3428-3430`)
```python
blocked = AgentControlEntry.get_blocked_names()
# Filter out blocked agents from initiative stage automation
```
Checked before dispatching initiative-driven action items to agents.

**Enforcement Point 4 — Learning Override** (`core/services/learning_read_service.py:184-195`)
```python
if AgentControlEntry.is_blocked(best_agent):
    # Don't suggest a blocked agent as the best match
```
Checked before recommending an agent based on learning history.

**Key property:** No enforcement point communicates with any other. There is no pub/sub, no event bus, no cache invalidation signal. Each point independently queries the database, and each query independently evaluates TTL. This means:
- A block applied at any source (PA, autopilot, system) is immediately visible to all enforcement points on their next query.
- A TTL expiry triggered by one enforcement point's query is immediately visible to all subsequent queries from any enforcement point.
- If one enforcement point fails (e.g., Celery worker crash), the remaining three continue enforcing.

### Component 4: Block Source Tracking

Six distinct actors can create blocks, tracked via the `blocked_by` field:

| Actor | Description | Typical TTL |
|-------|-------------|-------------|
| `system` | System-wide permanent blocks (e.g., CodeGeneratorAgent has no codebase access on Railway) | null (permanent) |
| `rigby` | PA (Rigby) via agent_control_tool, human-initiated | Varies |
| `claude-code` | Developer intervention via Claude Code session | Varies |
| `ops_autopilot` | Autonomous timeout spike containment policy | 0.5h (30 min) |
| `timeout_playbook` | Graduated timeout remediation ladder L3 | 4h |
| `remediation_engine` | Signature-based auto-remediation | Varies |

Each actor's blocks coexist in the same table. A single agent can only have one `AgentControlEntry` record (unique constraint on `agent_name`), so the most recent block overwrites the previous one. This prevents conflicting blocks from different actors and ensures a single source of truth.

### Component 5: PA Control Interface

**Schema:** `core/services/pa_tool_schemas.py` (lines 2089-2135)
**Handler:** `core/services/td_handlers_ops.py` (lines 697-810)

The `agent_control_tool` provides 4 actions via natural language:

| Action | Parameters | Effect |
|--------|-----------|--------|
| `list` | — | Returns all entries + currently blocked agents (triggers TTL evaluation) |
| `block` | agent_name, reason, ttl_hours, blocked_by | Creates/updates AgentControlEntry |
| `unblock` | agent_name, reason | Updates matching blocked entries to enabled |
| `audit_log` | limit (default 20, max 50) | Returns recent changes ordered by -updated_at |

**Note:** The `list` action itself triggers lazy TTL evaluation, meaning simply asking "which agents are blocked?" can cause expired blocks to auto-unblock.

---

## 6. Novelty Hooks (Section 102)

**a) Lazy TTL evaluation as a side effect of read operations.** The system has no scheduled expiration process. Block expiration occurs as a side effect of any component querying the control table. This is absent from known agent management systems, which universally rely on scheduled cleanup (cron, Celery Beat, Redis EXPIRE, TTL callbacks).

**b) Database-backed blocking with TTL semantics without database-level TTL support.** PostgreSQL does not natively support TTL on rows. The system implements TTL semantics in application code at the query layer, preserving expired records for audit while excluding them from active enforcement.

**c) Multi-point enforcement via shared table without coordination.** Four independent enforcement points query the same table without pub/sub, event propagation, or cache invalidation. No known multi-agent framework enforces operational controls this way — frameworks like LangChain, AutoGen, and CrewAI use centralized orchestrators.

**d) Immutable audit trail from expired blocks.** Expired blocks are not deleted but updated to `status='enabled'` with `reason='TTL expired (Nh)'`, preserving the full lifecycle (who blocked, when, why, when it expired) without a separate audit log table.

**e) Heterogeneous enforcement point types.** The four enforcement points serve fundamentally different execution models: asynchronous task queue (Celery), synchronous function call (router), batch dispatch (action items), and recommendation system (learning override). Consistent enforcement across these heterogeneous paths from a single control table is not taught by prior art.

---

## 7. Non-Obviousness Hooks (Section 103)

**a) Lazy evaluation contradicts standard TTL design.** The obvious implementation of TTL is either passive expiry (Redis EXPIRE, database TTL policies) or active cleanup (scheduled task). Implementing TTL as a side effect of read queries is counter-intuitive because it couples a mutation (updating the record) to a read operation. Engineers would not predictably choose this approach because it violates the principle of read operations being side-effect-free. The insight is that in a system where reads are frequent and evenly distributed across enforcement points, lazy evaluation provides more reliable expiry than any scheduled approach.

**b) Single-record-per-agent design prevents multi-actor conflicts.** The obvious design for multi-actor blocking would be one record per block event (allowing concurrent blocks from different actors). The single-record design (unique constraint on `agent_name`) is non-obvious because it means a new block overwrites a previous block — but this is intentional: the most recent actor's intent should dominate, and the previous block's audit trail is preserved via `updated_at` comparison.

**c) Enforcement without coordination is counter-intuitive in distributed systems.** The standard approach to distributing state changes across components is pub/sub (Redis Pub/Sub, Kafka), event sourcing, or cache invalidation. Relying on each component to independently query the database on every execution appears inefficient. The non-obvious insight is that for blocking decisions (which change infrequently relative to execution frequency), the database query cost is negligible compared to the agent execution cost, and eliminating coordination infrastructure removes an entire class of failure modes (missed messages, stale caches, split-brain).

**d) Migration-safe fallback preserves safety under schema changes.** The `get_blocked_names()` method catches exceptions and returns a hardcoded fallback set. This is non-obvious because it means the system maintains safety even when the control table doesn't exist (during migrations), without requiring a separate migration-aware blocking mechanism.

---

## 8. Operational Benefits (Measurable Outputs)

- **Zero scheduler dependency for expiration**: No Celery Beat task, cron job, or background thread required for block expiry. Eliminates an entire failure mode (scheduler hang → blocks persist indefinitely).
- **Durability through restarts**: Blocks survive Redis failovers, worker restarts, and deployments because they are stored in PostgreSQL, not volatile cache.
- **Consistent enforcement across 4 paths**: An agent blocked via any path is blocked on all paths. No "backdoor" execution paths exist.
- **Self-healing on read**: If a TTL-expired block was missed (e.g., no queries during off-peak hours), the first query from any enforcement point automatically cleans it up.
- **Audit completeness**: Every block lifecycle is recorded: who blocked, when, why, TTL duration, and when/how it was unblocked (TTL expiry, manual unblock, or rollback).
- **Operational simplicity**: The entire blocking system is one model, one class method, and four one-line checks. No message bus, no cache layer, no coordination protocol.

---

## 9. Alternative Embodiments

**a) Batch TTL evaluation with caching.** Instead of evaluating TTL on every query, the system could evaluate once per N seconds and cache the result in Redis with its own short TTL (e.g., 10 seconds). This reduces database queries under high concurrency while maintaining near-real-time expiry.

**b) Event-sourced control records.** Instead of updating records in place, each block/unblock could create a new event record, with the current state computed by replaying events. This provides a richer audit trail but increases query complexity.

**c) Hierarchical enforcement with override priority.** Blocks could have priority levels (system > autopilot > human), where a lower-priority block cannot override a higher-priority one. The current single-record design treats all actors equally.

**d) Distributed enforcement via change-data-capture.** In a multi-database deployment, PostgreSQL logical replication or CDC (Debezium) could propagate `AgentControlEntry` changes to read replicas, enabling enforcement points in different data centers to enforce blocks with minimal replication lag.

**e) TTL with grace period.** Instead of immediate expiry, the system could enter a "grace" state where the agent is unblocked but monitored for N minutes. If failures resume during grace, the block is automatically reinstated with a longer TTL.

**f) Probabilistic enforcement for high-throughput systems.** Under extreme concurrency, enforcement points could check the control table with a configurable probability (e.g., 90% of executions), reducing database load while maintaining statistical enforcement. The lazy TTL evaluation would still occur on checked executions.

---

## 10. Claim Skeleton

### Independent Method Claim

A computer-implemented method for controlling execution of software agents in a multi-agent system, the method comprising:

(a) storing, in a persistent relational database, an agent control record for a software agent, the record comprising an agent identifier, an operational status field, a block timestamp, and a time-to-live value;

(b) at each of a plurality of independent enforcement points in the system, prior to executing or recommending the software agent, querying the database for agent control records with a blocked operational status;

(c) for each queried record having a non-null time-to-live value and a block timestamp, computing an elapsed duration since the block timestamp;

(d) when the elapsed duration exceeds the time-to-live value, atomically updating the record's operational status to an unblocked state as a side effect of the query, without any scheduled expiration task;

(e) returning, from the query, a set of agent identifiers whose records remain in a blocked state after the lazy evaluation; and

(f) preventing execution of the software agent at the querying enforcement point when the agent's identifier is in the returned set.

### Dependent Claims

1. The method of the independent claim, wherein the plurality of independent enforcement points comprise an asynchronous task queue worker, a synchronous function router, a batch action dispatcher, and a machine learning recommendation service.

2. The method of the independent claim, wherein no enforcement point communicates the result of its query or TTL evaluation to any other enforcement point.

3. The method of the independent claim, wherein the atomic update of step (d) further comprises setting a reason field to a value indicating TTL expiry and preserving the original block timestamp and actor identifier for audit purposes.

4. The method of the independent claim, wherein the agent control record further comprises a block source identifier selected from a set of actor types including system, human operator, autonomous policy engine, and remediation engine.

5. The method of claim 4, wherein the agent control record is subject to a unique constraint on the agent identifier, such that only one control record exists per agent, and a new block from any actor overwrites the previous block.

6. The method of the independent claim, further comprising a migration-safe fallback wherein, if the database table does not exist, the query returns a hardcoded set of permanently blocked agent identifiers.

7. The method of the independent claim, further comprising a natural-language interface that, upon receiving a list command, triggers the lazy TTL evaluation of step (d) and returns the current set of blocked agents.

8. The method of the independent claim, wherein the return type of step (e) is an immutable frozen set, preventing mutation of the block list by calling code.

9. The method of the independent claim, wherein the time-to-live value is set by an autonomous policy engine based on the severity of the detected failure, with shorter TTL values for transient failures and longer TTL values for systemic failures.

10. A system comprising one or more processors and memory storing instructions that, when executed, perform the method of the independent claim.

---

## 11. Diagrams to Draft

**Figure 1 — Lazy TTL Evaluation Flow**
```
[Enforcement Point calls get_blocked_names()]
      |
[Query: SELECT * FROM agent_control WHERE status='blocked']
      |
[For each record:]
      |
[ttl_hours is NULL?] --YES--> [Add to blocked set (permanent)]
      |NO
[elapsed = (now - blocked_at) / 3600]
      |
[elapsed > ttl_hours?] --YES--> [UPDATE status='enabled', reason='TTL expired']
      |                           [Do NOT add to blocked set]
      |NO
[Add to blocked set (still active)]
      |
[Return frozenset(blocked set)]
```

**Figure 2 — Multi-Point Enforcement Architecture**
```
                     +---------------------------+
                     |   AgentControlEntry Table  |
                     |   (PostgreSQL, single      |
                     |    source of truth)         |
                     +---------------------------+
                    /       |         |           \
                   /        |         |            \
    +----------+ +--------+ +----------+ +----------+
    | Celery   | | Agent  | | Action   | | Learning |
    | Worker   | | Router | | Item     | | Override |
    | (async)  | | (sync) | | Dispatch | | (ML)     |
    +----------+ +--------+ +----------+ +----------+
         |            |           |            |
    [Each independently queries table]
    [Each independently evaluates TTL]
    [No inter-point communication]
```

**Figure 3 — Block Lifecycle (with TTL)**
```
[Block Created]
  blocked_by: 'ops_autopilot'
  blocked_at: T0
  ttl_hours: 0.5
  status: 'blocked'
      |
[T0 to T0+30min: All enforcement points see 'blocked']
      |
[T0+30min: First query after TTL expiry]
  --> Lazy evaluation: elapsed > ttl_hours
  --> UPDATE status='enabled', reason='TTL expired (0.5h)'
      |
[T0+30min+: All enforcement points see 'enabled']
[Record preserved for audit with original blocked_at, blocked_by]
```

**Figure 4 — Actor Overwrite Behavior**
```
Time T1: ops_autopilot blocks AgentX (ttl=0.5h)
  record: {status:'blocked', blocked_by:'ops_autopilot', ttl:0.5}

Time T2 (T1+10min): rigby blocks AgentX (ttl=null, permanent)
  record: {status:'blocked', blocked_by:'rigby', ttl:null}
  --> ops_autopilot's block is overwritten
  --> rigby's permanent block now governs

Time T3: rigby unblocks AgentX
  record: {status:'enabled', reason:'Unblocked via PA'}
```

---

## 12. Prior Art Buckets to Cite Against

**a) Redis TTL / Key Expiry (Redis EXPIRE, EXPIREAT)**
- Teaches: automatic key deletion after TTL
- Does NOT teach: database-backed TTL with audit preservation (Redis deletes the key entirely), lazy evaluation at read time (Redis uses background expiry threads), or multi-point enforcement from a single store

**b) Database Row-Level TTL (Cassandra TTL, DynamoDB TTL, MongoDB TTL indexes)**
- Teaches: automatic row deletion after TTL
- Does NOT teach: application-layer TTL evaluation (these use database-engine-level expiry), preservation of expired records for audit (these delete rows), or side-effect updates during read queries

**c) Feature Flag Systems (LaunchDarkly, Unleash)**
- Teaches: runtime toggling of features across services
- Does NOT teach: automatic TTL-based toggle expiry, lazy evaluation without polling, or block-source tracking with audit trail

**d) Service Mesh Circuit Breakers (Istio, Envoy, Linkerd)**
- Teaches: request-level circuit breaking at the proxy layer
- Does NOT teach: agent-level (not request-level) blocking, TTL evaluation at application read time, or enforcement across heterogeneous execution models (async queue, sync call, batch dispatch, ML recommendation)

**e) Kubernetes PodDisruptionBudget / Taints and Tolerations**
- Teaches: preventing pod scheduling based on node conditions
- Does NOT teach: time-limited scheduling restrictions with lazy expiry, multi-path enforcement, or audit preservation of expired restrictions

**f) Distributed Lock Managers (etcd, ZooKeeper, Consul)**
- Teaches: distributed locking with TTL and session expiry
- Does NOT teach: application-layer lazy evaluation (these use server-side session management), multi-point enforcement without client coordination, or lock records preserved after expiry for audit

---

## Observability Evidence (Proving This Runs in Production)

### Block Creation (any actor)
```sql
-- Record created/updated in PostgreSQL
SELECT agent_name, status, reason, blocked_at, blocked_by, ttl_hours, updated_at
FROM core_agentcontrolentry
WHERE agent_name = 'CustomerResearchAgent';
-- Result: ('CustomerResearchAgent', 'blocked', 'Timeout spike: 5 in 60min',
--          '2026-03-16 14:22:00', 'ops_autopilot', 0.5, '2026-03-16 14:22:00')
```

### Lazy TTL Expiry (triggered by any enforcement point query)
```sql
-- After TTL expiry, same query returns:
-- Result: ('CustomerResearchAgent', 'enabled', 'TTL expired (0.5h)',
--          '2026-03-16 14:22:00', 'ops_autopilot', 0.5, '2026-03-16 14:52:01')
-- Note: blocked_at preserved, updated_at shows when TTL evaluation occurred
```

### Multi-Point Enforcement Evidence
```
# Celery worker log
[execute_agent_task] BLOCKED: CustomerResearchAgent disabled on Railway

# Agent router log
[route] BLOCKED: CustomerResearchAgent disabled on Railway

# Both logs appear within seconds of each other for concurrent requests,
# proving independent enforcement from the same control table
```

### Migration Safety Evidence
```python
# During migration 0279 (before table exists):
AgentControlEntry.get_blocked_names()
# Returns: frozenset({'CodeGeneratorAgent'}) — hardcoded fallback
# No exception raised, system continues with safe default
```

---

## Examiner Story

Prior art teaches Redis key expiry for temporary state (EXPIRE command), database-level TTL for automatic row deletion (Cassandra, DynamoDB), and feature flag systems for runtime service toggling (LaunchDarkly). However, no single reference teaches a system that (1) stores agent blocking records in a relational database without native TTL support, (2) evaluates TTL lazily as a side effect of read queries rather than via scheduled expiration or database-engine mechanisms, (3) preserves expired records with expiry metadata for audit rather than deleting them, and (4) enforces the blocking state across four heterogeneous execution paths (async queue, sync router, batch dispatch, ML recommendation) via independent database queries with no inter-point coordination. The combination is non-predictable because standard distributed systems design mandates coordination mechanisms (pub/sub, event buses, cache invalidation) for cross-component state consistency; eliminating all coordination infrastructure while maintaining consistent enforcement is a non-obvious simplification that reduces failure modes at the cost of slightly increased database query frequency — a trade-off that engineers would not predictably choose without the specific insight that blocking state changes are rare relative to execution frequency.
