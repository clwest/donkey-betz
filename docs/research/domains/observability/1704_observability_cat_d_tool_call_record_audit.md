---
title: "Group 1700 Cat D — ToolCallRecord Child Audit"
authority: child-audit
category: child_audit
session: 1704
child_slot: P4
domain_slug: observability
research_group: 1700
status: active
generated: 2026-07-03
verifier_loop: [pre-explore-verified, post-explore-verified]
sibling_children: [1701_observability_cat_a_celery_task_event_audit.md, 1702_observability_cat_b_llm_call_event_audit.md, 1703_observability_cat_c_agent_execution_audit.md]
parent_scoping: 1700_observability_domain_scoping.md
canonical_summary: 1799_observability_canonical_summary.md (pending)
---

# Group 1700 Cat D — ToolCallRecord Child Audit

> **Fourth child audit under Group 1700 (Observability arc).** Applies
> playbook §11.2 20-section child audit template + §13 6-parallel-Explore
> sweep + §14 verifier-loop discipline (pre-Explore + post-Explore). Cat D
> is the per-tool-call telemetry layer bracketed by S970 BaseAgent
> `__init_subclass__` auto-wrap + S1115 all-return-path fix in
> `ToolDispatcher.execute`. Feeds xx99 D74 axis posture evidence
> continuing from S1703 F9 (4-option spine Chinese menu).

---

## 1. Executive Summary

Cat D owns per-tool-call telemetry — one row per `_execute_tool_call`
invocation across every AGENT_MAP agent, plus one row per
`ToolDispatcher.execute` invocation from the PA function-calling loop and
direct callers. The model is `ToolCallRecord`
(`core/models_tool_calls.py:19-131`) with two adjacent
mining-support models in the same file: `ToolCallAggregate` (:220-273,
daily rollup) and `PAToolInsight` (:276-324, mined prompt-injection
insights).

**Coverage at HEAD.** 4144 rows accumulated 2026-06-13 → 2026-07-03 (~20
days, ~200 rows/day). Three writer paths at HEAD:
(a) BaseAgent S970 auto-wrap around subclass-overridden
`_execute_tool_call` (52 of 83 AGENT_MAP agents have such an override
somewhere in MRO); (b) BaseAgent DEFAULT `_execute_tool_call` at
`base_agent.py:3168-3316` for the remaining 31 agents (S1085 tag at
:3188 — "Record built-in tool calls (wrapper only catches subclass
overrides)") — this default writes ToolCallRecord rows from its own
`finally` block at :3302; (c) `ToolDispatcher._record_tool_call_sync`
at `tool_dispatcher.py:937` covering ALL FIVE return branches of
`_execute_inner` (S1115 finding 17 closure). A fourth writer at
`unified_pa_entrypoint._record_tool_call:2096-2140` is DEPRECATED
per docstring at :2111-2117 (PA loop confirms at :1841-1848) with
zero verified external callers.

**Nine load-bearing findings emerge from the pre-Explore + post-Explore
verifier passes (see §1.1):** F1 (CRITICAL) 100% NULL `trace_id` on
all 4144 rows despite the field existing + indexed; F2 (HIGH) `NO
execution_id` + `NO tool_call_id` columns at all — parent §3.B
accounting-rule dedup key gap AND S1703 F6 spine-join gap both fail
at schema; F3 (MEDIUM) 29 of 31 base-inherited agents show ZERO
rows at HEAD (idle or pure-LLM, not "silent-zero-write" per
verifier-loop correction); F4 (MEDIUM) `analyze_pa_tool_patterns`
(tasks.py:12375) + `aggregate_tool_call_stats`
(tasks.py:8282) both DEFINED + routed but NEVER scheduled
(0 PeriodicTask entries, 0 in `core/celery.py` beat schedule) →
PAToolInsight=0 rows + ToolCallAggregate=0 rows (WRITE-ONLY-FORGOTTEN
per Group 1500 F.B3 pattern); F5 (MEDIUM) no date-based retention
policy (Cat A precedent absent, Cat B F4 gap resurfaces here);
F6 (POSITIVE differentiator vs S1703 F4) PA path DOES write 907
rows via `ToolDispatcher.execute` — Cat D has PA coverage, unlike
Cat C which had zero; F7 (LOW) two dead-writer methods
(`unified_pa_entrypoint._record_tool_call` + BaseAgent
`_execute_and_record_tool_call:3317-3371`) retained per verify-
before-deleting-dead-code rule; F8 (LOW) no Django admin registration
(analog to S1703 T-11 debt); F9 (D74 axis contribution) Cat D
evidence is **load-bearing for all four xx99 options** — the
Provenance chain at `deliverable_provenance.py:105` uses
`ToolCallRecord.objects.filter(trace_id=execution.trace_id)` and
returns EMPTY for every deliverable at HEAD because Cat D's
trace_id column is 100% NULL.

**Maturity STABLE for writer mechanism (three writer paths never
throw, all three swallow-and-log) + PARTIAL for coverage (52/83
S970-wrapped + 2/31 base-inherited agents active + PA path via
dispatcher) + BROKEN for cross-cat correlation contract
(trace_id=NULL empirically kills S1703 F6 semantic join;
tool_call_id + execution_id both schema-absent kill Cat B/C
correlation).** Risk **HIGH** — provenance queries silently
return empty, mining pipelines silently produce zero output,
retention absent means unbounded row growth.

### 1.1 Nine load-bearing findings (locked)

- **F1 (CRITICAL, §17)** — `trace_id` is 100% NULL across all 4144 rows at HEAD (ORM-verified). Root cause split across three writers: dispatcher hardcodes `trace_id=None` at `tool_dispatcher.py:961` with comment "dispatcher trace_id ('td-N-hex') isn't a UUID"; the S970 wrapper at `base_agent.py:451-459` does NOT pass `trace_id` to `_record_tool_call`; BaseAgent default's inline record at `base_agent.py:3302-3310` also does NOT pass trace_id. The `trace_id` field on the model exists + is `db_index=True` + is in a composite index (`models_tool_calls.py:47-50, 126`) — index space is wasted. Kills S1703 F9 Option B (trace_id spine) at runtime; kills `deliverable_provenance.py:105` chain empirically (see F9).
- **F2 (HIGH, §17)** — ToolCallRecord has NO `execution_id`, NO `tool_call_id`, NO `call_id`, NO `celery_task_id`, NO `task_id`, and NO FK to `AgentExecution` / `LLMCallEvent` / `CeleryTaskEvent`. Only correlation candidates are (i) `trace_id` (F1 → empty), (ii) `conversation_id` (21.9% populated), (iii) `agent_name` (semantic string match, 39 distinct values). S1702 F9 and S1703 F6 both flagged the same accounting-rule enforceability gap — this audit confirms at Cat D side.
- **F3 (MEDIUM, §14+§17)** — Pre-Explore prior "31 unwrapped agents write ZERO rows" was OVERSTATED. Post-Explore verifier correction: 31 AGENT_MAP agents inherit BaseAgent's default `_execute_tool_call` at :3168-3316 — the default has its OWN `finally`-block writer at :3302 (S1085 pattern tagged at :3188). Empirically at HEAD, only 2 of 31 base-inherited agents have written any rows (`TopicMinerAgent`=10, `AutonomousContentStudioCoordinator`=1); 29 show zero. That's an **idle-agent OR pure-LLM-agent** distribution, not a coverage-mechanism bug. Real gap: custom tools not wired into BaseAgent default hit "not implemented" fallback at :3272-3274 (0 rows carry `error_type='NotImplemented'` in current dataset — either the S1246 fix eliminated the bulk or the pattern is retention-window-invisible).
- **F4 (MEDIUM, §17)** — `analyze_pa_tool_patterns` (`core/tasks.py:12375` → `core/tasks_agents.py:6124`) and `aggregate_tool_call_stats` (`core/tasks.py:8282` → `core/tasks_ops.py:3325-3386`) are both DEFINED as `@shared_task`, both routed via `settings.py:1294` + `:1580`, but NEITHER is registered in `core/celery.py` beat schedule NOR present in the `PeriodicTask` table (0 matches). Consequence: PAToolInsight = 0 rows + ToolCallAggregate = 0 rows at HEAD. Both consumer models (aggregation dashboards + PA prompt injection) are silently dark. Group 1500 F.B3 WRITE-ONLY-FORGOTTEN pattern reproduces here.
- **F5 (MEDIUM, §15)** — No date-based retention for any of the three Cat D tables. Cat A precedent (`CELERY_TASK_EVENT_RETENTION_DAYS`, `core/tasks.py:4393-4404`, 30-day default) exists; Cat B has watchdog cleanup but no retention (S1702 F4 HIGH); Cat D has neither. 4144 rows over 20 days extrapolates to ~73k rows/year at current cadence — bounded but not measured for unusual bursts.
- **F6 (POSITIVE differentiator, §7+§9)** — PA path DOES write 907 ToolCallRecord rows (22% of total) via `ToolDispatcher.execute(agent_name='PersonalAssistant', conversation_id=…)` invoked from `unified_pa_entrypoint.py:1830+`. This is a **material Cat D vs Cat C difference**: S1703 F4 (CRITICAL) reported Cat C zero PA coverage; Cat D has partial PA coverage via the dispatcher. All 907 PA rows still have `trace_id=NULL` per F1, and `conversation_id` is populated only on this subset — the 21.9% figure in field distribution is essentially the PA subset alone.
- **F7 (LOW, §17)** — Two dead-writer methods verified via zero-caller grep: (a) `unified_pa_entrypoint._record_tool_call:2096-2140` — docstring at :2111-2117 explicitly marks DEPRECATED per S1115 finding 17 closure; (b) `BaseAgent._execute_and_record_tool_call:3317-3371` (S861 explicit-trace_id path) — grep across `core/` returned only the definition site + docstring reference; all agent subclasses call `self._execute_tool_call(tool_name, arguments)` directly, never the explicit S861 method. Both retained per `feedback_verify_before_deleting_dead_code.md` memory rule — deletion recommended AFTER post-arc cross-repo fleet-caller verification per `feedback_fleet_caller_verification_before_celery_deletes.md`.
- **F8 (LOW, §14+§17)** — No Django admin registration for ToolCallRecord / ToolCallAggregate / PAToolInsight (grep `core/admin*.py` → 0 matches). Analog to Cat C T-11 (S1703 §15). Not blocking any current flow; would improve xx99 dev-triage ergonomics.
- **F9 (D74 axis contribution, §9)** — Cat D **blocks all four spine-posture options** unless a primitive is populated at write time. Cat D is **actively broken for Option B today** (trace_id column exists + indexed but 100% NULL empirically — any trace_id-based join is dead-on-arrival). Cat D is **incomplete-not-broken for Option A** (execution_id column doesn't exist yet — schema absence rather than runtime failure). Options C/D inherit the same prerequisite. The `deliverable_provenance.py:105` chain (`ToolCallRecord.objects.filter(trace_id=execution.trace_id)`) is the sole production consumer of Cat D↔Cat C spine correlation and returns EMPTY for every deliverable at HEAD, because Cat D's `trace_id` is 100% NULL. Option B has the smallest **schema lift** (column exists + indexed) but the **coordination lift is equivalent to Option A** — dispatcher must generate a real UUID (replacing `td-N-hex` string), wrapper + base default + PA loop must thread trace_id from context. **This is the load-bearing Cat D evidence for the xx99 posture decision** (Rigby SIGN cycle 1 F1 fold — wording tightened; distinction matters because Option B has a runtime credibility problem Option A does not).

---

## 2. Domain Purpose

**Q1 — What is Cat D telemetry accountable for?** Per-tool-call
audit trail. Every tool invocation by an AGENT_MAP agent, PA function-
calling loop dispatch, or direct dispatcher caller writes one row
capturing agent identity, tool name, parameters, result summary +
hash + full body (below 64KB) + size, success flag, error trail,
latency in ms, and task context blurb. Purpose per S861 handoff:
audit trail for post-hoc debug + PA tool-usage-pattern mining
input (PAToolInsight) + Deliverable provenance chain input
(`deliverable_provenance.py:42-115`).

**Q2 — Where does Cat D end?** Cat D DOES NOT own tool schema or
tool registry (that's PA tool surface concern) or the agent-level
outcome (Cat C, per parent §3.D boundary rule). Cat D DOES NOT own
LLM cost/token accounting when a tool internally invokes an LLM
(Cat B accounting-rule, parent §3.D + Rigby SIGN cycle 1 F3 fold
from S1700). Cat D DOES NOT own the aggregate rollup consumer
surface (that's ToolCallAggregate's job) nor the mined-insight
consumer surface (that's PAToolInsight's job); the writer boundary
stops at ToolCallRecord `objects.create`.

---

## 3. Canonical Entry Points

**Q3 — Where does data enter Cat D at HEAD?**

### 3.1 Writer entry points (in priority order)

| Priority | Writer | File:line | Trigger | Coverage note |
|---|---|---|---|---|
| **P1** | `ToolDispatcher._record_tool_call_sync` | `core/services/tool_dispatcher.py:937-978` (called via `_record_tool_call_async:913-935` from 5 return branches of `_execute_inner`) | Every `dispatcher.execute(...)` call when `record_telemetry=True` (default) | S1115 finding 17 closure. Writes with `agent_name` = caller-supplied ('Direct' default, 'PersonalAssistant' from PA path, callable agent name from `run_agent` path). `trace_id=None` explicit (:961). `conversation_id` = caller-supplied. |
| **P2** | S970 auto-wrap around subclass `_execute_tool_call` | `core/agents/base_agent.py:428-464` (calls `self._record_tool_call:3373-3424` in `finally`) | Every subclass-overridden `_execute_tool_call` invocation | Fires ONLY for classes with `_execute_tool_call` in own MRO before BaseAgent. **52 of 83 AGENT_MAP agents match** (per ORM MRO walk 2026-07-03). Writes with `agent_name = self.name`. `trace_id=None` (wrapper does not thread). |
| **P3** | BaseAgent default `_execute_tool_call` inline record | `core/agents/base_agent.py:3168-3316` (:3302-3310 in `finally`) | Every base-inherited agent's tool call — 31 of 83 AGENT_MAP agents. S1085 tag at :3188. | Handles 4 built-in tools (delegate_to_specialist :3196, web_search :3206, intelligence_tool[search+web] :3235 (S1246 lane L), spider_query :3251) + returns `not implemented in {self.name}` for unknowns (:3273). Writes with `agent_name = self.name`. `trace_id=None`. `conversation_id=None`. |
| **P4 (DEPRECATED)** | `unified_pa_entrypoint._record_tool_call` | `core/services/unified_pa_entrypoint.py:2096-2140` | Legacy PA loop write — no active caller. | Docstring at :2111-2117 declares DEPRECATED per S1115 finding 17 closure. PA loop confirms at :1841-1848 ("PA no longer has to write its own row here — the dispatcher handles it"). Retained per `feedback_verify_before_deleting_dead_code.md`. Would write `agent_name='PersonalAssistant'`, `trace_id=None`, `conversation_id=self.conversation_id`. |
| **P5 (DEAD API)** | `BaseAgent._execute_and_record_tool_call` | `core/agents/base_agent.py:3317-3371` (S861 explicit-trace_id path) | Zero verified callers across `core/` grep. | Only writer path accepting explicit `trace_id=` kwarg. Superseded by S970 wrapper at S970 handoff. Retained per verify-before-deleting rule. |

**Two non-BaseAgent overrides of `_execute_tool_call`:**
`core/personal_ai_assistant_enhanced.py:1297` (non-BaseAgent
`EnhancedPersonalAIAssistant`) and `core/assistant/base.py:172`
(deprecated per docstring). Neither writes ToolCallRecord — both
route to their own handler dispatch chain. **SPECULATIVE** whether
either is production-active; grep for external instantiation
recommended for xx99.

### 3.2 Reader entry points

| Reader | File:line | Purpose |
|---|---|---|
| `core/views_audit_api.ToolCallRecordViewSet` | `core/views_audit_api.py:49-60` | `/api/v1/tool-call-records/` — paginated list + detail, filter on `agent_name`/`tool_name`/`success` |
| `core/views_audit_api.ToolCallAggregateViewSet` | `core/views_audit_api.py:62-70` (`queryset = ToolCallAggregate.objects.order_by('-date','-total_calls')`) | `/api/v1/tool-call-aggregates/` — daily rollup consumer surface; empty at HEAD (F4) |
| `core/views_personal_assistant.pa_activity_feed` | `core/views_personal_assistant.py` (E3 report cites :687-739) | `/api/pa/activity_feed/` — 1-24h lookback for PA tool history |
| `core/views_agent_extras` | `core/views_agent_extras.py:57-112` | Enriches `/api/agent-tools` with 7-day call counts + latency |
| `core/services/deliverable_provenance.build_provenance_block` | `core/services/deliverable_provenance.py:42-115` (query at :105) | Reads ToolCallRecord by `trace_id=execution.trace_id`; returns EMPTY for every deliverable at HEAD per F1+F9 |
| `core/services/pa_tool_learning_enricher` | `core/services/pa_tool_learning_enricher.py:20-50` (per E3 report) | Reads approved PAToolInsight rows, injects `prompt_snippet` into PA system prompt at `unified_pa_entrypoint.py:2430-2438` |
| `core/management/commands/build_runtime_audit` | `core/management/commands/build_runtime_audit.py` | Cross-references AGENT_MAP + tasks + PA_TOOL_SCHEMAS vs telemetry tables including ToolCallRecord |

### 3.3 Non-existent surfaces (grep-verified absent)

- No dedicated PA tool for tool-call history query — `session_trace_builder` reads exist but no `tool_call_history_tool` in `pa_tool_schemas.py`. Analog to S1701 Cat A gap; xx99 R6 candidate.
- No Django admin registration (grep `core/admin*.py` → 0). F8.
- No WebSocket push of ToolCallRecord rows themselves. **However** `core/services/pa_status_events.py` emits `rigby.tool.started` / `rigby.tool.completed` UI-ticker events via channel-layer to `pa_conversation_<id>` group — these are Session 1172 live-ticker semantics, not ToolCallRecord row replay. Payload includes tool_name + latency + status, joined by `pa_trace_id` (NOT stored on ToolCallRecord).
- No Discord bot command surfaces ToolCallRecord data (E3 grep 0 matches in `discord_bot.py`).
- No CI lint for direct tool-call writes analog to Cat B's `check_direct_llm_calls.py`.
- No EventBus / Kafka / RabbitMQ producer for Cat D events. Passive telemetry sink (analog to Cat A/B/C posture).
- No signals (`post_save` / `pre_save`) registered on ToolCallRecord (grep `core/signals/*.py` → 0 matches).

### 3.4 Retention entry point (absent)

- **None found.** grep for `TOOL_CALL_RETENTION|retention.*tool_call|cleanup.*tool_call|purge.*ToolCallRecord` → 0 hits in `core/tasks*.py` + `core/settings.py`. Cat D has no retention worker, no watchdog, no expiry column (contrast with `PAToolInsight.expires_at` which does exist at :309 for the insight table only). F5.

---

## 4. Major Models

**Q4 — What Django models does Cat D own?**

### 4.1 `ToolCallRecord` — `core/models_tool_calls.py:19-131`

**Session 861 model.** 16 columns:

| Field | Type | Null | Index | Default |
|---|---|---|---|---|
| `id` | UUIDField PK | No | PK | uuid4 |
| `trace_id` | UUIDField | Yes | db_index=True | NULL |
| `conversation_id` | UUIDField | Yes | db_index=True | NULL |
| `agent_name` | CharField(255) | No | db_index=True | — |
| `tool_name` | CharField(100) | No | db_index=True | — |
| `parameters` | JSONField | No | — | `{}` |
| `result_summary` | TextField | (blank OK) | — | — |
| `result_hash` | CharField(72) | (blank OK) | — | — |
| `full_result` | TextField | (blank OK) | — | — |
| `result_size_bytes` | IntegerField | No | — | 0 |
| `success` | BooleanField | No | — | True |
| `error_message` | TextField | (blank OK) | — | — |
| `error_type` | CharField(100) | (blank OK) | — | — |
| `latency_ms` | IntegerField | No | db_index=True | 0 |
| `task_summary` | CharField(500) | (blank OK) | — | — |
| `created_at` | DateTimeField | No | db_index=True | auto_now_add |

**Meta indexes (`:122-127`)**: composite indexes on
`(agent_name, created_at)`, `(tool_name, created_at)`,
`(success, created_at)`, `(trace_id, created_at)`. The
`(trace_id, created_at)` composite is wasted space at HEAD — F1
guarantees 100% NULL trace_id.

**Confirmed schema absences (grep + Read verified):** NO `execution_id`, NO `tool_call_id`, NO `call_id`, NO `celery_task_id`, NO `task_id`, NO `mission_id`, NO `pa_trace_id`, NO FK to `AgentExecution` / `LLMCallEvent` / `CeleryTaskEvent` / `OpsRun`. Only cross-cat correlation candidates are `trace_id` (100% NULL) + `conversation_id` (21.9% populated, PA subset) + `agent_name` (string match on 39 distinct values). F2.

**Convenience writer `ToolCallRecord.record(...)`** at `:133-217` — a classmethod that serializes result → hash + size + 4KB summary + 64KB full-body cutoff, parses `trace_id`/`conversation_id` string→UUID (best-effort — silent None on parse fail per `:189-193`, `:195-200`), and calls `cls.objects.create(...)`. Used by S970 wrapper's `_record_tool_call` (base_agent.py:3408) + BaseAgent default's `_record_tool_call` (base_agent.py:3302 via `_record_tool_call` at :3373). Dispatcher writer bypasses `.record()` and calls `.objects.create()` directly at `tool_dispatcher.py:960` — slight semantic divergence (dispatcher builds result_summary + result_hash + full_result manually per :954-971).

### 4.2 `ToolCallAggregate` — `core/models_tool_calls.py:220-273`

Daily rollup consumer. Fields: `id` UUIDField PK, `agent_name` CharField(255) indexed, `tool_name` CharField(100) indexed, `date` DateField indexed, `total_calls`/`success_calls`/`failed_calls` IntegerField, `avg_latency_ms`/`min_latency_ms`/`max_latency_ms`/`p95_latency_ms` IntegerField, `top_errors` JSONField (default list), `updated_at` auto_now.

**`unique_together = ['agent_name','tool_name','date']`** at `:261` — dedup guarantee for update_or_create pattern.

Writer: `_impl_aggregate_tool_call_stats` at `core/tasks_ops.py:3325-3386` — reads ToolCallRecord `days_back` window, aggregates per `(agent_name, tool_name, date)`, calls `ToolCallAggregate.objects.update_or_create(...)` at `:3386`.

**Row count at HEAD: 0.** WRITE-ONLY-FORGOTTEN — task exists (`core/tasks.py:8282-8285` shim + settings.py:1294 routes to `long_running` queue) but no beat schedule entry. F4.

### 4.3 `PAToolInsight` — `core/models_tool_calls.py:276-324`

Mined-insight consumer. Fields: `id` UUIDField PK, `tool_name` CharField(100) indexed, `insight_type` CharField(30) choices ∈ {param_correction, error_pattern, success_pattern, follow_up, consistency_check}, `safety_class` CharField(20) choices ∈ {candidate, approved, rejected} default `candidate`, `pattern` JSONField, `prompt_snippet` TextField, `evidence_count` PositiveIntegerField default 1, `confidence` FloatField default 0.0, `expires_at` DateTimeField nullable indexed (S269 migration addition), `created_at` auto_now_add, `updated_at` auto_now.

Writer: `_impl_analyze_pa_tool_patterns` at `core/tasks_agents.py:6124-6280` (per E3 report). Mines last 24h of PersonalAssistant-agent-name ToolCallRecord for pattern types, writes candidate PAToolInsight rows.

**Row count at HEAD: 0.** WRITE-ONLY-FORGOTTEN — task exists but no beat schedule. F4.

Consumer: `PAToolLearningEnricher` in `core/services/pa_tool_learning_enricher.py:20-50` (per E3) reads `safety_class='approved'` non-expired rows, injects `prompt_snippet` into PA system prompt at `unified_pa_entrypoint.py:2430-2438`. Both approval pathways (auto-promotion at `core/tasks.py:12415` — SPECULATIVE per E3, and manual at `core/services/td_handlers_core.py:1938`) exist but produce zero output because upstream mining task is unscheduled.

### 4.4 Migration lineage

- **`0198_session_861_tool_call_records.py`** — `CreateModel` ToolCallRecord + ToolCallAggregate.
- **`0268_pa_tool_insight.py`** — `CreateModel` PAToolInsight with 5 insight_types.
- **`0269_pa_tool_insight_ttl_consistency.py`** — `AddField` `PAToolInsight.expires_at` + `AlterField` insight_type to include `consistency_check`.

(E1 report; verified filenames exist in `core/migrations/` per grep.)

### 4.5 FK graph

**ZERO ForeignKey references to ToolCallRecord / ToolCallAggregate / PAToolInsight anywhere in the codebase** (E1 verified; independent grep confirms `ForeignKey.*ToolCallRecord|OneToOne.*ToolCallRecord|ForeignKey.*PAToolInsight|ForeignKey.*ToolCallAggregate` → 0 hits). Cat D is a pure downstream telemetry sink — no inbound row dependency.

### 4.6 Overlap flags vs Cat A/B/C/E/F + 3-class landmine

- **ToolCallRecord vs ToolCallAggregate** — complementary (raw + rollup), not overlapping. Matches Cat A/B pattern (no aggregate table; Cat B's `LLMCallLog` is a sibling detail store, S1702 F1).
- **ToolCallRecord vs S1703's AgentExecution + `ToolCallAggregate.top_errors` JSONField** — no schema overlap; Cat C outcome vs Cat D per-call is boundary-clean per parent §3.D.
- **`PAToolInsight.pattern` JSONField** — help_text at :305 says "used for dedup via unique_together" but `unique_together` is ABSENT on PAToolInsight `Meta` (:316-322 has only `db_table` + `indexes=[('safety_class','tool_name')]`). Dedup contract stated but not schema-enforced. Debt-8 candidate.
- **No 3-class landmine analog** to S1703 F1 — all three Cat D models live in one file, are all registered under `app_label='core'` (explicit at PAToolInsight :317; implicit for the other two).
- **No cross-cat overlap** with `LLMCallEvent` / `LLMCallLog` (Cat B) / `CeleryTaskEvent` (Cat A) / `AgentExecution` (Cat C) / `OpsRun` / `OpsRunEvent` (Cat E) — Cat D scope is per-tool-call boundary.

---

## 5. Major Services

**Q5-Q6 — Services owning Cat D write path.**

### 5.1 `core/services/tool_dispatcher.py` (~1,267 lines) — Cat D primary writer

**`ToolDispatcher`** class + `_execute_inner` at `:655-899` with **five return branches**, each guarded by `if record_telemetry:` conditional writer:

1. **Line ~720 (TOOL_PERMISSION_DENIED branch)** — `_record_tool_call_async` at `:707`.
2. **Line ~751 (TOOL_NOT_FOUND branch)** — `_record_tool_call_async` at `:738`.
3. **Line ~839 (SUCCESS branch)** — `_record_tool_call_async` at `:826`.
4. **Line ~868 (TIMEOUT branch)** — `_record_tool_call_async` at `:855`.
5. **Line ~897 (EXCEPTION branch)** — `_record_tool_call_async` at `:884`.

**S1115 finding 17 closure verified intact** — all five return paths covered. Async writer `_record_tool_call_async:913-935` schedules `_record_tool_call_sync:937-978` via `asyncio.to_thread(...)`; sync writer builds fields manually (result_summary → 4KB slice, result_hash → sha256 hex, full_result → 64KB threshold check) and calls `ToolCallRecord.objects.create(...)` at `:960` with `trace_id=None` hardcoded (comment: "dispatcher trace_id ('td-N-hex') isn't a UUID"). Fire-and-forget: exceptions swallowed + logged WARNING at `:931-935`.

**Zero cross-domain imports at top of file** (lines 1-50); ORM import for `ToolCallRecord` is lazy inside `_record_tool_call_sync:950`. Clean import boundary.

**`record_telemetry=False` opt-out** at `:592` — grep across `core/` returned 0 caller sites. Legitimate knob for exclusive-control legacy callers per docstring `:614`; not currently exercised.

**`pa_trace_id` (Session 1172 live ticker)** flows via kwarg at `:593`, forwarded to `_execute_inner:649`, consumed by `emit_tool_started`/`emit_tool_completed` at `:679, :712, :743, :831, :860, :889` — **NOT stored on ToolCallRecord** (verified against schema). Ticker events flow to `pa_conversation_<id>` channel group when `pa_trace_id + conversation_id` both present; correlation to ToolCallRecord row is via `conversation_id` field + `created_at` ordering only.

### 5.2 `core/agents/base_agent.py` (5,962 lines) — Cat D secondary writer + auto-wrap host

**Three Cat D writer points at HEAD:**

- **`__init_subclass__` at :428-464 (S970 auto-wrap).** Fires at class creation for subclasses whose own `__dict__` contains `_execute_tool_call`. Wrapper measures latency, catches exceptions (re-raises after recording), and calls `self._record_tool_call(tool_name, arguments, result, latency_ms, success, error_message, error_type)` in `finally` at :451-459. NO `trace_id` / NO `conversation_id` / NO `task_summary` in the call — those default to None inside `_record_tool_call`. Never lets recording fail agent (pass on exception at :461).
- **`_execute_tool_call` default at :3168-3316.** Handles 4 built-in tools inline + returns `not implemented in {self.name}` for unknowns. **Also writes ToolCallRecord** in its own `finally` at :3276-3315: calls `self._record_tool_call(...)` at :3302 with the same NO-trace_id/NO-conversation_id shape. S1085 comment at :3188 explicitly names this pattern: "Record built-in tool calls (wrapper only catches subclass overrides)." Fires for 31 of 83 AGENT_MAP agents.
- **`_execute_and_record_tool_call` at :3317-3371 (S861 explicit path).** Accepts `trace_id=` + `conversation_id=` + `task_summary=` kwargs and passes them through to `_record_tool_call` at :3360-3371. **Zero verified callers** — grep for this method name across `core/` matches only its own definition + docstring reference at :3390. F7 dead-code candidate.

**`_record_tool_call` at :3373-3424** — the write dispatcher that calls `ToolCallRecord.record(...)` at :3408. Best-effort — swallows on exception with `logger.warning` at :3422-3424.

### 5.3 `core/services/unified_pa_entrypoint.py` (~7,600 lines) — Cat D dead-writer + PA dispatch caller

- **`_record_tool_call` at :2096-2140** — DEPRECATED per docstring at :2111-2117 (S1115 finding 17 closure). Would write directly to ToolCallRecord with `trace_id=None`, `agent_name='PersonalAssistant'`, `conversation_id=self.conversation_id`. **No verified caller inside the PA loop** — comment block at :1841-1848 confirms "PA no longer has to write its own row here — the dispatcher handles it." F7.
- **PA loop dispatcher invocation at :1830+** — calls `dispatcher.execute(tool_name=..., agent_name='PersonalAssistant', conversation_id=self.conversation_id, pa_trace_id=trace_id, ...)`. This is the WORKING PA write path — 907 rows in ToolCallRecord at HEAD carry `agent_name='PersonalAssistant'` (matching this call site). F6.
- **PAToolInsight consumption at :2430-2438** — reads approved insights via `PAToolLearningEnricher`, injects snippets into system prompt. Currently a no-op (0 approved rows exist per F4).

### 5.4 `core/services/deliverable_provenance.py` (~123 lines) — Cat D primary READ consumer

`build_provenance_block` at `:42-115` implements the Deliverable → Session 843 AgentExecution → trace_id → ToolCallRecord chain. Line 105 executes `ToolCallRecord.objects.filter(trace_id=execution.trace_id).order_by('created_at')[:25]` and returns up to 25 tool calls in the provenance response. **Empirically empty at HEAD** for every deliverable — even when `execution.trace_id` is populated by the router path per S1703 F9 F1 fold, the semantic join fails because Cat D's `trace_id` column is 100% NULL. F9.

### 5.5 `core/services/session_trace_builder.py` — grep 0 matches for ToolCallRecord

E5 report claimed this file consumes ToolCallRecord but independent grep returned 0 matches. **Likely reads via `deliverable_provenance` or a helper** — SPECULATIVE; xx99 verify.

### 5.6 `core/tasks_ops.py:3325-3386` — Cat D aggregate writer (unwired)

`_impl_aggregate_tool_call_stats(days_back)` walks ToolCallRecord over `days_back` window and calls `ToolCallAggregate.objects.update_or_create(...)` per `(agent_name, tool_name, date)` bucket. **Task shim at `core/tasks.py:8282-8285` routes to `long_running` queue** (settings.py:1289 comments "480MB spike — scans all ToolCallRecord rows"). **Zero beat schedule entry** → zero live rollup. F4.

### 5.7 `core/tasks_agents.py:6124-6280` — Cat D mining writer (unwired)

`_impl_analyze_pa_tool_patterns` walks last-24h PersonalAssistant ToolCallRecord rows, detects 5 pattern types, writes candidate PAToolInsight rows. **Task shim at `core/tasks.py:12375-12377` routes to `default` queue** (settings.py:1580). **Zero beat schedule entry** → zero mined insights. F4.

### 5.8 `core/services/pa_tool_learning_enricher.py` — Cat D consumer of PAToolInsight

Per E3, reads `safety_class='approved'` non-expired PAToolInsight rows and returns injectable snippets. Consumed by PA system-prompt build. No-op at HEAD given F4.

### 5.9 God-service check

- `base_agent.py` 5,962 lines — matches S1703 §5 count. NOT god-service-flagged for this arc (existing debt).
- `unified_pa_entrypoint.py` ~7,600 lines — largest single file in `core/services`. Not a Cat D concern per se; PA-scope debt.
- `tool_dispatcher.py` 1,267 lines — small, clean.

---

## 6. Major APIs and Interfaces

**Q7-Q9 — External-facing Cat D surface.**

### 6.1 REST endpoints

| Path | View | Auth | Purpose |
|---|---|---|---|
| `GET /api/v1/tool-call-records/` | `ToolCallRecordViewSet` (`core/views_audit_api.py:49-60`) | `IsAuthenticated` | List + retrieve. filterset_fields = `agent_name`, `tool_name`, `success`. |
| `GET /api/v1/tool-call-aggregates/` | `ToolCallAggregateViewSet` (`core/views_audit_api.py:62-70`) | `IsAuthenticated` | Ordered by `-date`, `-total_calls`. Returns empty at HEAD (F4). |
| `GET /api/pa/activity_feed/` | `pa_activity_feed` (`core/views_personal_assistant.py:687-739` per E3) | (session-based) | Reads recent ToolCallRecord for PA rows within 1-24h lookback. |
| `GET /api/agent-tools` | `core/views_agent_extras.py:57-112` | (session-based) | Enriches tool list with 7-day per-tool call counts + p50/p95 latency stats. |

### 6.2 PA tool schemas exposing Cat D

**No dedicated `tool_call_history_tool` / `tool_call_audit_tool` in `pa_tool_schemas.py`** (E3 verified 0 matches). Rigby cannot self-serve tool-call history queries via the PA function-calling loop; must fall back to REST endpoints above via Chris + Chat UI or ORM query via `td_handlers_*` non-audit surface. Analog to S1701 Cat A gap; xx99 R6 candidate.

### 6.3 WebSocket / channel-layer

- `rigby.tool.started` + `rigby.tool.completed` events emitted from `core/services/pa_status_events.py` (channel-layer push to `pa_conversation_<id>` group). Payload: `trace_id` (PA-side pa-N-hex), `seq` monotonic, `tool_name`, `latency_ms`, `status` ∈ {ok, error}. **NOT joined by ToolCallRecord.id at UI side** — Chat UI does its own local trace_id vs ToolCallRecord aggregation.
- Session 1172 introduced pa_trace_id for the ticker; join to Cat D rows requires SQL `conversation_id + created_at range` — no shared join key on the row itself.

### 6.4 Celery tasks

| Task | File:line | Route (settings.py) | Beat entry | Status |
|---|---|---|---|---|
| `core.tasks.aggregate_tool_call_stats(days_back=1)` | `core/tasks.py:8282-8285` shim → `_impl_aggregate_tool_call_stats` at `core/tasks_ops.py:3325-3386` | `long_running` queue (`:1294`) | **NONE** | F4 WRITE-ONLY-FORGOTTEN |
| `core.tasks.analyze_pa_tool_patterns()` | `core/tasks.py:12375-12377` shim → `_impl_analyze_pa_tool_patterns` at `core/tasks_agents.py:6124-6280` | `default` queue (`:1580`) | **NONE** | F4 WRITE-ONLY-FORGOTTEN |

### 6.5 Beat schedule

**Zero beat schedule entries.** PeriodicTask table query for `analyze_pa_tool_patterns` / `aggregate_tool_call_stats` / `tool_call` → 0 matches. `core/celery.py` grep for either task name → 0 matches. F4.

### 6.6 Management commands

- `build_runtime_audit.py` — cross-references code registries against telemetry tables including ToolCallRecord. Identifies never-executed tool schemas within the last 30-day window.

No dedicated purge / retention / cleanup command for ToolCallRecord. F5.

### 6.7 CI lint enforcement

**No `check_direct_tool_calls.py` analog** to Cat B's `check_direct_llm_calls.py`. No lint prevents direct `ToolCallRecord.objects.create(...)` outside canonical writer paths (dispatcher / BaseAgent). Enforcement is convention-only.

### 6.8 Frontend surfaces

E3 report + independent verification: no dedicated frontend page renders Cat D. Data flows into Deliverable provenance UI (via `/api/pa/deliverable/detail/`) but currently displays empty tool_calls list per F9.

### 6.9 Discord bot

Zero Discord commands surface Cat D data per E3 grep.

### 6.10 Django admin

**Not registered.** F8. Neither ToolCallRecord nor ToolCallAggregate nor PAToolInsight has `@admin.register` entry in `core/admin*.py`.

---

## 7. Runtime Flows

**Q6+Q7 — Cat D runtime paths at HEAD.**

### Flow 1: BaseAgent subclass with `_execute_tool_call` override (S970 wrapper path — 52 of 83 AGENT_MAP agents)

```
Agent subclass calls self._execute_tool_call('some_tool', args)
  → S970 wrapper (base_agent.py:432-461) intercepts
  → wrapper runs _orig(...) at :440 → tool logic executes
  → try: return result | except: re-raise
  → finally at :448-461:
      latency_ms = int((time - start) * 1000)
      self._record_tool_call(tool_name, args, result, latency_ms, success, err_msg, err_type)
        → ToolCallRecord.record(agent_name=self.name, tool_name, parameters=args, result,
                                latency_ms, success, error_message, error_type,
                                trace_id=None, conversation_id=None, task_summary='')
        → cls.objects.create(**parsed_fields) at models_tool_calls.py:202
  → Row written: agent_name=self.name, tool_name=..., trace_id=NULL, conversation_id=NULL
```

### Flow 2: BaseAgent-inherited default `_execute_tool_call` (31 of 83 AGENT_MAP agents)

```
Agent (no override) calls self._execute_tool_call('some_tool', args)
  → BaseAgent default at :3168-3316 runs
  → if tool is delegate_to_specialist/web_search/intelligence_tool[narrow]/spider_query:
       execute inline (built-in handler), _tc_result populated
  → else:
       _tc_success=False, _tc_result={'success':False,'error':'not implemented in <name>'}
  → finally at :3276-3315:
      _err_msg + _err_type extraction from result dict
      self._record_tool_call(tool_name, args, _tc_result, latency, _tc_success, _err_msg, _err_type)
        → ToolCallRecord.record(...) → cls.objects.create(...)
  → Row written: agent_name=self.name, tool_name=..., trace_id=NULL, conversation_id=NULL
```

**At HEAD, 29 of 31 base-inherited agents have written ZERO rows** — either they don't fire tool calls at all (LLM-only agents) or they haven't been invoked in the 20-day retention window. F3.

### Flow 3: ToolDispatcher.execute (PA + direct callers — 907 PA rows + 16 'Direct' rows + ~3000 delegated agent rows)

```
Caller (PA loop / test / direct):
  await dispatcher.execute(tool_name, payload, agent_name='PersonalAssistant',
                           conversation_id=conv_uuid, pa_trace_id='pa-N-hex',
                           record_telemetry=True)
  → _execute_inner at :655+ runs contextvar-scoped body
  → emit_tool_started (pa_status_events, channel-layer push if pa_trace_id+conv both set)
  → tool handler executes (permission check → dispatch → result)
  → one of 5 return branches:
      (a) permission denied → :707 _record_tool_call_async → :720 return
      (b) tool not found    → :738 _record_tool_call_async → :751 return
      (c) success           → :826 _record_tool_call_async → :839 return
      (d) timeout           → :855 _record_tool_call_async → :868 return
      (e) exception         → :884 _record_tool_call_async → :897 return
  → _record_tool_call_async at :913-935 (asyncio.to_thread — swallow-and-log at :931)
  → _record_tool_call_sync at :937-978
      → ToolCallRecord.objects.create(trace_id=None [:961], conversation_id=conversation_id,
                                       agent_name=agent_name, tool_name, parameters,
                                       result_summary=result_str[:4096], result_hash,
                                       full_result if size<=65536 else '',
                                       result_size_bytes, success, error_message,
                                       error_type=result.error_code, latency_ms,
                                       task_summary=f"[{result.trace_id}] dispatcher.execute"[:500])
  → Row written: agent_name=caller-supplied, tool_name=..., trace_id=NULL,
                 conversation_id=populated-when-PA
```

### Flow 4: PA path via dispatcher (F6 positive-differentiator)

Same as Flow 3 with `agent_name='PersonalAssistant'`, `conversation_id=self.conversation_id`, `pa_trace_id=trace_id`. 907 rows at HEAD; only writer path with populated `conversation_id`. `pa_trace_id` flows to UI ticker but does NOT persist on the ToolCallRecord row itself. F6.

### Flow 5: Deliverable → provenance chain (F9 empirically empty)

```
User opens Deliverable via /api/pa/deliverable/detail/
  → build_provenance_block(deliverable) at deliverable_provenance.py:42
  → resolve parent_object_id → AgentExecution.trace_id (S843 contract)
  → if execution.trace_id present:
       ToolCallRecord.objects.filter(trace_id=execution.trace_id).order_by('created_at')[:25]
       → EMPTY QuerySet (all Cat D trace_ids are NULL per F1)
  → block['tool_calls'] = []
  → UI renders "no tool calls" — silent empty state
```

F9. The provenance chain code is correct, indexed, and 25-row-bounded — but produces empty output for every deliverable at HEAD.

### Flow 6: Aggregation + insight mining (F4 dark pipelines)

```
Beat scheduler (if configured): trigger aggregate_tool_call_stats(days_back=1)
  → _impl_aggregate_tool_call_stats at tasks_ops.py:3325
  → walks last-N-days ToolCallRecord (this is the "480MB spike" per settings.py:1289)
  → per (agent_name, tool_name, date): update_or_create ToolCallAggregate
   → BUT no beat entry — NEVER FIRES.

Beat scheduler (if configured): trigger analyze_pa_tool_patterns()
  → _impl_analyze_pa_tool_patterns at tasks_agents.py:6124
  → walks last-24h PersonalAssistant rows in ToolCallRecord
  → generates 5 pattern-type candidate PAToolInsight rows
   → BUT no beat entry — NEVER FIRES.

Result: ToolCallAggregate=0 + PAToolInsight=0 at HEAD.
```

---

## 8. Data Ownership and Lifecycle

**Q8-Q9 — Ownership + lifecycle.**

### 8.1 Data owned by Cat D

- Per-tool-call audit rows (ToolCallRecord).
- Daily rollups (ToolCallAggregate).
- Mined prompt-injection insights (PAToolInsight).

### 8.2 Data consumed by Cat D

- **Callable agent identity** (via caller `self.name` from Bewahr wrapper / dispatcher `agent_name` kwarg).
- **Tool call payload** (`parameters` JSONField).
- **Tool call result** (serialized to `result_summary` + `full_result` + `result_hash`).
- **PA context** (`conversation_id`) — only for dispatcher path from PA loop.

### 8.3 Data produced by Cat D (for other domains)

- Deliverable provenance block via `deliverable_provenance.py:42` — currently empty (F9).
- PA prompt injection via `PAToolLearningEnricher` — currently no-op (F4).
- Dashboard REST API responses (`/api/v1/tool-call-records/`, `/api/v1/tool-call-aggregates/`, `/api/pa/activity_feed/`, `/api/agent-tools`).
- Rigby live ticker payloads (via pa_status_events, NOT persisted on ToolCallRecord).

### 8.4 Lifecycle summary

- **Create:** three writer paths (Flow 1/2/3) — fire-and-forget, swallow-and-log on failure.
- **Update:** none. ToolCallRecord rows are append-only per S861 audit-trail design.
- **Delete:** **NONE at HEAD.** No retention task, no purge command, no `expires_at` field on ToolCallRecord (`expires_at` exists only on PAToolInsight `:309`, unused since no rows exist). F5.
- **Query:** REST endpoints + provenance chain + management commands.

**Row count trajectory:** 4144 rows in 20 days = ~200 rows/day at recent cadence. Extrapolates to ~73k rows/year — bounded but unaudited for burst behavior. `p95` `result_size_bytes` = 15,347 (E1); one 549,561-byte row present in the top range. **No `full_result` cutoff enforcement** beyond the 64KB threshold at the writer.

---

## 9. Integrations With Other Domains

**Q14 + Q17 + Q18 + Q21 + Q22.**

### 9.1 Cross-cat integration matrix (D74 axis contribution)

| Direction | Mechanism | Strength verdict |
|---|---|---|
| Cat D ↔ Cat A (CeleryTaskEvent) | **NONE at schema level.** No `task_id` / `celery_task_id` column on ToolCallRecord. Correlation only via `AgentExecution.input_data['celery_task_id']` (S1703 F7) → AgentExecution.trace_id → ToolCallRecord.trace_id (both semantic-only + trace_id empty per F1). | **BROKEN (schema-absent + trace_id-empty)** |
| Cat D ↔ Cat B (LLMCallEvent) | **NONE at schema level.** Parent §3.B accounting-rule cites `execution_id + trace_id + tool_call_id` for dedup; ToolCallRecord has ZERO of those columns. S1702 F9 already flagged; confirmed from Cat D side. | **BROKEN (§3.B rule not schema-enforceable)** |
| Cat D ↔ Cat C (AgentExecution) | **`trace_id` semantic join only** (S1703 F6). Router path writes AgentExecution.trace_id per S1703 F9 F1 fold; Cat D writer paths (all 3 in Flow 1/2/3) write ToolCallRecord.trace_id = NULL. Empirical cross-cat trace_id match = ZERO. | **SEMANTIC-CONTRACT + EMPIRICALLY-EMPTY** |
| Cat D ↔ Cat E (OpsRun / OpsRunEvent) | **NONE.** MissionRunner does not thread tool telemetry back through OpsRunEvent (per E4). Tool calls made during a mission write ToolCallRecord normally via dispatcher / wrapper but no `mission_id` on the row. Employee OS `evidence_for_mission` join at `docs/topics/employee-os.md:64-65` names ToolCallRecord as a join surface but relies on `trace_id` for the join — same F1 failure. | **NAMED-BUT-BROKEN** |
| Cat D ↔ Cat F.a (HeartBeat) | **NONE.** Different observability concerns. | MISSING (by design) |
| Cat D ↔ Cat F.c (EventBus) | **NONE.** Cat D emits no domain events (no `post_save` receivers, no channel_layer send other than the ticker which is caller-side not model-side). Passive telemetry sink — matches Cat A/B/C posture. | MISSING (by design) |
| Cat D ↔ RAG | **NONE.** RAG is retrieval-only; no Cat D write from RAG-only path. | MISSING (by design) |

### 9.2 Cross-model spine coverage from Cat D side

Four spine candidates evaluated:

| Candidate | Present on ToolCallRecord? | Present + populated? | Needed for xx99 posture Option A/B/C/D | Cat D write cost |
|---|---|---|---|---|
| `task_id` | NO | N/A | Not on any option's shortlist (Cat A owns the primitive). | Would require adding column + threading Celery task context. High cost. |
| `execution_id` | NO | N/A | REQUIRED for Option A. | Add column (UUIDField nullable indexed) + populate at 3 writers. Medium cost (schema + 3 writer edits). |
| `trace_id` | YES (indexed, composite too) | NO (100% NULL) | REQUIRED for Option B. | Column exists — just populate. Low schema cost, medium coordination cost (dispatcher must generate real UUID, wrapper must thread from context, PA loop must thread). |
| `tool_call_id` | NO | N/A | REQUIRED for Option A dedup + §3.B rule. | Add column + generate + emit. Low-medium cost. |

**Cat D's evidence for xx99:** Option B has the smallest schema lift (column already exists + indexed). Option A adds `execution_id` column — heavier schema move but preserves S1702 F9 wrapper contract semantics ("survive AgentExecution deletion"). Option C (shared correlation view) requires ONE of the primitives populated first — Cat D currently offers zero, so Option C rests on prior work either way. Option D (hybrid) inherits the same prerequisite.

**Bottom line (Rigby SIGN cycle 1 F1 fold — wording tightened):** Cat D **blocks all four options** unless a spine primitive is populated at write time. Cat D is **actively broken for Option B today** (trace_id column exists + indexed but 100% NULL empirically — any trace_id-based join is dead-on-arrival). Cat D is **incomplete-not-broken for Option A** (execution_id column simply doesn't exist yet — schema absence rather than runtime failure). Options C/D inherit the same prerequisite: at least one primitive must be populated before the join is queryable. This distinction matters for xx99 posture-decision framing: Option B currently has a runtime credibility problem that Option A does not.

**Schema-lift vs coordination-lift decomposition for Option B (Rigby SIGN cycle 1 F3 fold):** Option B has the smallest **schema lift** (column already exists + indexed) but the **coordination lift is equivalent to Option A** — dispatcher must generate a real UUID trace_id (replacing the current `td-N-hex` string), S970 wrapper must thread trace_id from execution context, base default must thread from context, and PA loop must convert `pa-N-hex` → UUID. Both options need the same three-writer coordination; only the schema-migration step differs.

### 9.3 Import boundaries

**`core/models_tool_calls.py` imports (:11-16):**
- `uuid`, `hashlib`, `json` (stdlib)
- `from typing import Any, Optional`
- `from django.db import models`
- `from django.utils import timezone`

Zero cross-domain imports. Clean (matches Cat A/B/C posture per S1701/S1702/S1703 §9).

**`core/services/tool_dispatcher.py` imports** — lazy-inside-function pattern for `ToolCallRecord` at `:950`. No Cat A/B/C/E model imports at top. Clean boundary. Handler mixins imported at `:178-191` — not cross-cat.

**`core/agents/base_agent.py` imports** — lazy `ToolCallRecord` import at `:3406` inside `_record_tool_call`. Clean boundary.

**Reverse (imports of ToolCallRecord elsewhere):** 24 files import (grep-verified). Split: 7 core writer / consumer files + 5 test files + 12 view / task / signals / service files (indirect readers or definition references). All within `core/` app; no cross-domain foreign imports outside `core/`.

### 9.4 Cross-arc references

- **Group 1400 Revenue (S1499):** no ToolCallRecord references in canonical summary (E5 verified).
- **Group 1500 Sports (S1599):** no ToolCallRecord references.
- **Group 1600 Content (S1699):** no ToolCallRecord references. (Content Reviewers are LLM-prompt-only per S1699 §7.4 CORRECTION; their tools land in Cat D but no arc doc references it.)
- **Group 1300 Memory (S1399):** no ToolCallRecord references.
- **Group 1700 siblings:** S1702 F9 named Cat D's schema gap ("ToolCallRecord has trace_id, conversation_id, agent_name, tool_name — NO execution_id and NO tool_call_id field"); S1703 F6 (HIGH) named the same gap from Cat C side. This audit closes the Cat D side; canonical summary S1799 will resolve.

**Load-bearing for xx99 §5 posture-decision brief:** Cat D provides negative evidence on all four F9 options. Cat D + Cat C (from S1703 F9) collectively rule OUT Options B/C without upstream population work; Option A is the tightest schema move but requires the same three writers to thread new column.

### 9.5 Ownership of `conversation_id` correlation

Only Flow 3 (dispatcher) writes non-NULL `conversation_id` — writes ONLY when caller passes it (PA path always does). 907 populated rows / 4144 total = 21.9% coverage. Non-PA callers (16 rows `agent_name='Direct'`) and BaseAgent Flow 1 + Flow 2 (S970 wrapper + base default) always write `conversation_id=NULL` because they don't have caller-passed conversation context. **This is a per-writer artifact, not a schema defect** — matches Cat B posture (execution_id is "borrowed spine" from Cat C in Cat B; conversation_id is "borrowed spine" from PA in Cat D).

---

## 10. Event Flows

**Q19 + Q20 — Emission + consumption.**

### 10.1 Events emitted by Cat D

**None at the model level.** Grep for `post_save` / `pre_save` / `channel_layer` / `send_signal` on ToolCallRecord → 0 hits. Cat D is a passive telemetry sink (analog to Cat A/B/C).

**Ticker events at the writer side (`core/services/pa_status_events.py`)** — emitted BEFORE the row is written, NOT on `post_save`:
- `rigby.tool.started` (payload: pa_trace_id, seq, tool_name, tool_call_id=dispatcher-local) — pushed to `pa_conversation_<id>` group.
- `rigby.tool.completed` (payload: same + latency_ms + status).

These are dispatcher-boundary events for UI liveness, not domain events on the ToolCallRecord row itself. Consumer is the frontend Chat UI ticker.

### 10.2 Events that should be emitted (gaps)

- **`tool_call_recorded` domain event** — would enable event-driven dashboards + Group 1900 Event Architecture consumer. Not emitted at HEAD.
- **`pa_tool_insight_generated` domain event** — would enable notification when new candidate insight lands. Moot at HEAD (F4 dark pipeline).

### 10.3 Explicit event contract absence

Cat D does NOT emit domain events on an EventBus surface (per parent §5 D72 "post-EventBus dormant" observation). All fan-out is via ticker channel-layer at the dispatcher-boundary (not the row-boundary). No pub/sub, no Kafka topic, no persistent event outbox.

---

## 11. Existing Documentation

**Q10-Q13 — Doc coverage.**

### 11.1 Topic docs

- **`docs/topics/agent-system.md:107-113`** — mentions ToolCallRecord + S970 auto-wrap. Quote: "Automatic audit trail for all agents via `__init_subclass__()` in `BaseAgent`: Wraps `_execute_tool_call()` in every subclass automatically... Records: tool_name, arguments, result, latency_ms, success, error_message. Zero agent files changed — the wrapper is inherited." Accurate for S970 hook mechanism; MISSING coverage of (a) the 31-agent base-inherited path via `_execute_tool_call` default's own recording (Flow 2 above), (b) dispatcher writer path (Flow 3), (c) 100% NULL trace_id contract, (d) PA path coverage (F6).
- **`docs/topics/personal-assistant.md`** — ZERO ToolCallRecord references (E5 verified). CRITICAL doc gap given F6 (PA path writes 907 rows).
- **`docs/topics/employee-os.md:64-65`** — cites ToolCallRecord in `evidence_for_mission` join surface list. Correct scope but sparse; no join semantics documented.
- **`docs/topics/celery-workers.md`** — ZERO ToolCallRecord references.

### 11.2 Handoff anchors

- **S861** — ToolCallRecord model creation + `_execute_and_record_tool_call` + `_record_tool_call` methods introduced.
- **S970** — `__init_subclass__` auto-wrap activation. Fixed "0% coverage → ~100% (subclass-override subset only)" per S970 handoff at :58-76.
- **S1060** — PA tool-call recording added to `unified_pa_entrypoint._record_tool_call` (now deprecated per F7).
- **S1085** — BaseAgent default's inline recording added (comment tag at :3188 — "Record built-in tool calls").
- **S1098** — PA execution_id lineage (root_execution_id / parent_execution_id on AgentExecution; relevant for Cat B/C spine, not Cat D directly).
- **S1115** — All-return-path fix "finding 17 closure" — dispatcher owns writes.
- **S1172** — pa_trace_id + live ticker events.
- **S1199** — `tool_context_scope` contextvar propagation.
- **S1246** — S1247 lane L intelligence_tool web-search branch added to BaseAgent default (:3222-3228).
- **S1701** Cat A audit — `agent_name` backfill pattern (F5), retention precedent.
- **S1702** Cat B audit — F9 execution_id posture; §3.B accounting-rule dedup gap already flagged.
- **S1703** Cat C audit — F6 (HIGH) ToolCallRecord.trace_id semantic-join gap; F9 4-option spine posture; T-11 no-admin analog.

### 11.3 Research library

- Parent scoping `1700_observability_domain_scoping.md` §3.D (:528-558) — canonical for Cat D boundary + scope.
- S1701 Cat A audit — task_id spine + agent_name F5 pattern.
- S1702 Cat B audit — F9 execution_id posture from Cat B side; §3.B rule.
- S1703 Cat C audit — F6 trace_id gap named; F9 4-option Chinese menu; downstream carrier table for AgentExecution IDs.
- `docs/research/actor_identity_attribution_architecture.md:523` — Rigby-delegator vs executor `agent_name` semantic ambiguity on ToolCallRecord.

### 11.4 ARCHITECTURE_INDEX

21 mentions per E5 grep. Includes evidence-scoring subsection referencing five-model observability family (line 2644). No dedicated `§1.N` entry for "ToolCallRecord as subject" prior to S1704; S1704 will register at `§1.50` per line-6 v47 bump.

### 11.5 CLAUDE.md

CLAUDE.md Key Files table lists `core/models_tool_calls.py` NOT explicitly; ToolCallRecord is mentioned only in the tabular narrative around PA tools (per S1704 grep). No subsystem anchor. Cat D subsystem coverage in the CLAUDE.md system-stats block is inventory-only.

### 11.6 PLATFORM_INVENTORY

**ZERO ToolCallRecord references** (E5 verified; independent grep confirms). No per-model row count. Analog to S1703 D6.

### 11.7 PLATFORM_WHAT_IT_IS

`PLATFORM_WHAT_IT_IS.md:375` lists ToolCallRecord in the agents-family inventory row; zero narrative on Cat D purpose, retention, correlation, or per-writer-path coverage.

### 11.8 Documentation gaps (input to §14 Known Drift)

Doc → D-numbered drift items:
- D1: Parent §3.D "74 enabled AGENT_MAP agents that inherit BaseAgent" implies uniform coverage — actual coverage is 52 wrapped + 31 base-inherited (both cover-writers but only 2 of 31 have data at HEAD).
- D2: `docs/topics/agent-system.md:107-113` accurate for S970 wrapper but does NOT mention Flow 2 (base default) or Flow 3 (dispatcher).
- D3: `docs/topics/personal-assistant.md` omits F6 PA path coverage.
- D4: `PLATFORM_INVENTORY.md` no per-model row count (S1703 D6 pattern).
- D5: `PLATFORM_WHAT_IT_IS.md:375` narrative-thin.
- D6: `docs/topics/agent-system.md` claim "Zero agent files changed" MISLEADING for the 31-agent base-inherited subset (they never had a file change to opt into wrapping; the base default's inline recorder provides coverage).

---

## 12. Research Coverage

**Q10-Q13 — Existing research + gaps.**

Research library covers Cat D primarily via cross-references from Cat A/B/C audits (S1701/S1702/S1703) + parent scoping S1700 §3.D. No dedicated Cat D deep-audit existed prior to S1704.

### 12.1 New research contributions from S1704

1. **F1 empirical evidence** — 100% NULL trace_id at 4144 rows at HEAD (ORM-verified 2026-07-03).
2. **F3 verifier-correction** — the "31-agent silent zero-write" prior is WRONG; base default's inline recorder at :3302 IS active. Real gap is 29-of-31 idle/no-tool-call agents in the retention window.
3. **F4 WRITE-ONLY-FORGOTTEN evidence** — analyze_pa_tool_patterns + aggregate_tool_call_stats both defined + queue-routed but zero beat entries → ToolCallAggregate=0 + PAToolInsight=0.
4. **F6 positive-differentiator evidence** — Cat D has PA coverage (907 rows) via dispatcher, unlike Cat C's F4 zero-PA-coverage.
5. **F9 posture-implication** — Option B smallest schema lift but zero-write-coverage means any option's prerequisite is closing F1.
6. **Provenance-chain empty at HEAD** — `deliverable_provenance.py:105` produces empty tool_calls list for every deliverable.

### 12.2 Coverage classification (from §11 audit)

- **CANONICAL COVERED-BY-S1704:** boundary + writer paths + row-count distribution + F1 through F9.
- **PRIOR-COVERED-ADEQUATELY:** S861 model creation intent, S970 wrapper intent, S1115 dispatcher writer intent.
- **STILL UNCOVERED (xx99 anchor gaps):** doc D1-D6 above; F4 dark pipeline resolution; F5 retention policy; F1 trace_id write-coverage repair path.

---

## 13. Architecture Maturity

**Q23 — Maturity verdict per surface split.**

| Surface | Verdict | Evidence |
|---|---|---|
| Writer mechanism (all 3 flows) | **STABLE** | Never throws (best-effort swallow-and-log at all 3 sites); no observed data loss beyond swallow-events; test coverage exists in `core/tests/test_deliverable_provenance.py:111,115`. |
| Coverage (fleet-wide) | **PARTIAL** | 52/83 agents S970-wrapped + 31/83 base-inherited (also covered by inline recorder) + PA path via dispatcher. 29 of 31 base-inherited show 0 rows at HEAD — usage pattern, not mechanism bug. F3+F6. |
| Cross-cat correlation contract | **BROKEN** | 100% NULL trace_id at HEAD kills S1703 F6 semantic join; no execution_id / tool_call_id at schema level kills parent §3.B rule + Cat B/C linkage. F1+F2+F9. |
| Consumer surfaces | **PARTIAL** | REST endpoints working (list + aggregate + activity_feed + agent-tools). Provenance chain reads correctly but returns empty (F9). PA prompt-injection no-op (F4). |
| Retention posture | **MISSING** | No cleanup task, no watchdog, no `expires_at`. F5. |
| Aggregation / mining pipeline | **DEAD** | Both feeder tasks unwired; both consumer tables 0 rows. F4. |
| Admin / audit surface | **MISSING** | No Django admin registration, no dedicated PA tool for history query. F8. |

**Overall maturity: PARTIAL for mechanism + BROKEN for correlation contract + DEAD for downstream pipelines.** Production risk **HIGH** — silent data loss in provenance queries + silent zero mining output + unbounded row growth.

---

## 14. Known Drift

**Q24 — Doc-vs-runtime drift.**

| ID | Drift claim | Runtime evidence | Severity | Source |
|---|---|---|---|---|
| **D1** | Parent §3.D "74 enabled AGENT_MAP agents inherit BaseAgent" | AGENT_MAP has 83 entries (not 74 enabled — AgentRouter.AGENT_MAP walk 2026-07-03); 52 override `_execute_tool_call` somewhere in MRO before BaseAgent (S970-wrapped); 31 inherit BaseAgent default directly (S1085 inline-recorder path). PLATFORM_INVENTORY says "74 enabled, 9 rerouted, 0 blocked" — parent §3.D scope drifts from that number. | LOW | `1700_observability_domain_scoping.md:542` |
| **D2** | `docs/topics/agent-system.md:107-113` — S970 auto-wrap "wraps every subclass's `_execute_tool_call`" | Correct in mechanism, MISLEADING in coverage — only wraps subclasses with own `_execute_tool_call` in `__dict__`. The 31 base-inherited agents are covered by BaseAgent default's inline recorder (S1085 at :3188), NOT by the wrapper. Doc omits the split. | MEDIUM | `docs/topics/agent-system.md:107-113` |
| **D3** | `docs/topics/personal-assistant.md` — no ToolCallRecord narrative | PA path writes 907 rows (22% of all Cat D writes) via dispatcher (S1115 finding 17 closure). Doc omits F6 coverage story entirely. | MEDIUM | `docs/topics/personal-assistant.md` |
| **D4** | `PLATFORM_INVENTORY.md` no per-model row count | Analog to S1703 D6. Cat D absent from inventory (grep 0 matches). | LOW | `docs/PLATFORM_INVENTORY.md` |
| **D5** | `PLATFORM_WHAT_IT_IS.md:375` — Cat D inventory-row-only | No narrative on retention absent, correlation contract, F1 trace_id, F4 dark pipeline. | LOW | `docs/PLATFORM_WHAT_IT_IS.md:375` |
| **D6** | Parent §3.D "S970 BaseAgent `__init_subclass__()` wrapper; S1115 all-return-path fix" | Correct on both; S1115 finding 17 closure verified at all 5 return branches of `_execute_inner`. NO drift. Retained as positive evidence. | (no drift) | `1700_observability_domain_scoping.md:539-540` |
| **D7** | Parent §5 correlation-primitive table row for `tool_call_id` — "HYPOTHESIS: tool_call_id is scoped to a single tool invocation; correlation to LLMCallEvent (when the tool internally calls an LLM) is via a shared execution_id or by tool_call_id being included as FK-like column on LLMCallEvent" | **REFUTED at Cat D side.** `tool_call_id` DOES NOT EXIST on ToolCallRecord. The dispatcher generates a local trace_id (`td-N-hex`) at `tool_dispatcher.py:626` but does NOT persist it as `tool_call_id` on the row — it's stored inside `task_summary` string at `:977` (`f"[{result.trace_id}] dispatcher.execute"[:500]`). Semantic-only presence in a truncated string field. Parent §5 hypothesis needs xx99 revision. | **HIGH** (Rigby SIGN cycle 1 F2 fold — escalated MEDIUM → HIGH: "upstream references to non-existent Cat D correlation columns directly misguide cross-cat dedup/correlation work — more dangerous than doc omissions") | `1700_observability_domain_scoping.md:856` |
| **D8** | `PAToolInsight` docstring at `:305` — "pattern JSONField `used for dedup via unique_together`" | `unique_together` is ABSENT on PAToolInsight `Meta` (:316-322 has no unique_together). Dedup contract stated but not schema-enforced. | LOW | `core/models_tool_calls.py:305` |
| **D9** | Parent §3.B accounting-rule (Rigby SIGN F3 fold, cited in S1702 audit) — "LLM calls made from inside a tool invocation remain Cat B; dedup via correlation keys (execution_id + trace_id + tool_call_id)" | **Rule cites three correlation keys, of which ZERO are schema-enforceable on ToolCallRecord.** `execution_id` absent (F2); `tool_call_id` absent (D7); `trace_id` present but 100% NULL empirically (F1). Companion drift to D7 — the accounting-rule is definitional but has no enforcement path. Feeds S1799 §5 posture-decision brief. | **HIGH** (Rigby SIGN cycle 1 F2 fold — new row surfaced by same fold) | `1700_observability_domain_scoping.md:462-467` |

**All D-items owed to xx99 anchor-update PR.**

---

## 15. Known Technical Debt

**Q25 — Debt matrix.**

| ID | Description | Evidence | Severity | Remediation | Inherited-from |
|---|---|---|---|---|---|
| **T-1** | 100% NULL trace_id at 4144 rows at HEAD | Three writer paths hardcode trace_id=None (dispatcher :961, wrapper :451-459, base default :3302). Column exists + indexed. | CRITICAL | HIGH — dispatcher must generate UUID trace_id + wrapper + base default must thread from context. Coordinated 3-writer change. | S1703 F6 |
| **T-2** | No execution_id column on ToolCallRecord | Schema absent per §4.1. Parent §3.B accounting-rule + S1703 F6 both require it for Option A. | HIGH | MEDIUM — schema migration + writer edits at 3 sites. | S1703 F6 |
| **T-3** | No tool_call_id dedup key | Schema absent per §4.1. Parent §3.B rule + S1702 F9 both cited but not schema-enforceable. | HIGH | MEDIUM — schema migration + dispatcher / wrapper generate + write. | S1702 F9, S1703 F6 |
| **T-4** | analyze_pa_tool_patterns WRITE-ONLY-FORGOTTEN | Task defined + routed but no beat entry; PAToolInsight=0 rows. | MEDIUM | LOW — add PeriodicTask beat entry (single migration or admin action). | Group 1500 F.B3 |
| **T-5** | aggregate_tool_call_stats WRITE-ONLY-FORGOTTEN | Task defined + routed to `long_running` queue (settings.py:1294; docstring notes 480MB spike) but no beat entry; ToolCallAggregate=0 rows. | MEDIUM | LOW — add beat entry + validate 480MB spike behavior. | Group 1500 F.B3 |
| **T-6** | No date-based retention for any of 3 Cat D tables | grep for retention/purge/cleanup on ToolCallRecord → 0 hits. | MEDIUM | LOW — add cleanup Celery task + `TOOL_CALL_RECORD_RETENTION_DAYS` setting. | S1702 F4 (T-3), S1703 R-5 |
| **T-7** | No PA tool for tool-call history query | No `tool_call_history_tool` in `pa_tool_schemas.py`; users can't self-serve via Rigby function-calling. | MEDIUM | LOW — add PA tool + handler in `td_handlers_*.py`. | S1701 Cat A gap analog, S1703 R-6 |
| **T-8** | No Django admin registration for ToolCallRecord / ToolCallAggregate / PAToolInsight | grep `core/admin*.py` → 0 hits. | MEDIUM | LOW — add read-only admin classes with filters. | S1703 T-11 |
| **T-9** | Two dead-writer methods retained | `unified_pa_entrypoint._record_tool_call:2096-2140` (F7) + `BaseAgent._execute_and_record_tool_call:3317-3371` (F7 dead API). | LOW | LOW — cross-repo fleet-caller verification per `feedback_fleet_caller_verification_before_celery_deletes.md`, then delete if clean. | verify-before-deleting-dead-code memory rule |
| **T-10** | agent_name backfill/dimension analog (S1169) | ToolCallRecord.agent_name is CharField(255) indexed. 39 distinct values in 4144 rows. No S1169-pattern backfill task for Cat D. | LOW-MEDIUM | LOW — audit + optional backfill/dimension mapping if xx99 flags dimension drift. | S1701 F5 |
| **T-11** | PAToolInsight dedup contract stated in docstring but NOT enforced | `:305` help_text mentions unique_together dedup; `Meta:316-322` has no unique_together. | LOW | LOW — add `unique_together = ['tool_name','insight_type','pattern']` migration when reactivating F4 pipeline. | D8 |
| **T-12** | `_execute_and_record_tool_call` signature accepts trace_id but has zero callers | S861 API dead. If T-1 is fixed via this method (thread trace_id from caller), can be revived; otherwise delete. | LOW | LOW — decide during T-1 fix. | F7 |
| **T-13** | Non-BaseAgent overrides at `personal_ai_assistant_enhanced.py:1297` + `assistant/base.py:172` write no telemetry | Both have their own `_execute_tool_call` bypass BaseAgent + S970 wrapper. `assistant/base.py` marked DEPRECATED per docstring; `personal_ai_assistant_enhanced.py` status SPECULATIVE. | LOW-MEDIUM | LOW — grep production usage; delete if dead OR retrofit telemetry. | (new; not inherited) |

**T-1 through T-3 are the load-bearing debt items feeding xx99 F9 posture decision.**

---

## 16. Boundary Violations

**Q26 — Boundary discipline evaluation.**

### 16.1 Writer boundary discipline

Expected Cat D writers: dispatcher path (Flow 3) + BaseAgent wrapper path (Flow 1) + BaseAgent default path (Flow 2). All three verified as Cat D-internal.

**Verified writer sites (5 candidates evaluated):**

| Writer | Location | Verdict |
|---|---|---|
| `ToolDispatcher._record_tool_call_sync` | `core/services/tool_dispatcher.py:937` | LEGITIMATE (S1115 canonical path) |
| `BaseAgent._record_tool_call` → `ToolCallRecord.record` | `core/agents/base_agent.py:3373-3424` | LEGITIMATE (S970 wrapper + S1085 base-inline both call this) |
| `unified_pa_entrypoint._record_tool_call` | `core/services/unified_pa_entrypoint.py:2096-2140` | DEPRECATED per S1115 finding 17 closure. Retained per verify-before-deleting rule. No production caller. F7. |
| `ToolCallRecord.record` classmethod | `core/models_tool_calls.py:133-217` | LEGITIMATE convenience wrapper called by BaseAgent path. |
| `core/tests/test_deliverable_provenance.py:111,115` | (test fixture) | LEGITIMATE (test-scope) |

**No unexpected writers found.** Grep for `ToolCallRecord.objects.create` across `core/` returned only the 3 legitimate production sites + 2 test sites. Boundary discipline INTACT.

### 16.2 Non-wrapper direct writes (would-be violations)

The `unified_pa_entrypoint` dead writer is the only historically-non-canonical writer path, and it's DEPRECATED by design. No S1115-regression writers found.

### 16.3 Orphan candidates

- `unified_pa_entrypoint._record_tool_call` — dead writer, no callers.
- `BaseAgent._execute_and_record_tool_call:3317-3371` — dead reader/method, no callers.
- Non-BaseAgent `_execute_tool_call` overrides at `personal_ai_assistant_enhanced.py:1297` + `assistant/base.py:172` — bypass Cat D entirely; may or may not be production. SPECULATIVE.

All 3 orphan candidates retained per `feedback_verify_before_deleting_dead_code.md` memory rule. Deletion pending cross-repo fleet-caller verification (`feedback_fleet_caller_verification_before_celery_deletes.md`).

---

## 17. Duplicate or Overlapping Systems

**Q27 — Overlap catalog.**

### 17.1 Cat D internal overlap

None. ToolCallRecord (raw) + ToolCallAggregate (rollup consumer) + PAToolInsight (mined consumer) are complementary tiers with a clean data-flow: TCR → aggregate task → TCA + TCR → mining task → PATI.

### 17.2 Duplicate telemetry channels

- **Rigby live ticker events** (`pa_status_events.py`) vs ToolCallRecord row — same event source (dispatcher call) with different audiences (UI liveness vs post-hoc audit). NOT overlap; complementary.
- **PLATFORM_INVENTORY `analyze_pa_tool_patterns` task listing** vs `PLATFORM_INVENTORY.md` per-model count. Both absent for Cat D — no overlap.

### 17.3 Cross-cat overlap

No overlap with Cat A (CeleryTaskEvent) / Cat B (LLMCallEvent) / Cat C (AgentExecution) / Cat E (OpsRun / OpsRunEvent). All boundary-clean per parent §3.D + confirmed by grep — no columns shared, no models cross-referenced.

### 17.4 Landmine risk

None. Unlike S1703 F1's 3-class AgentExecution landmine, Cat D lives in a single file (`core/models_tool_calls.py`) with clean `app_label='core'` scope. No app-registry ambiguity.

---

## 18. Ownership Gaps

**Q25 — Named owner audit.**

### 18.1 Named owner search

- **CLAUDE.md:** does not name Cat D owner. Lists `core/agent_router.py` as a Key File; ToolCallRecord model not listed as Key File.
- **PLATFORM_INVENTORY.md:** no ownership metadata for Cat D.
- **git blame on `core/models_tool_calls.py`** and `core/services/tool_dispatcher.py` (informational — not source-of-truth): recent authors are `Chris West` + `Claude Opus`. No explicit human "owner" tag in headers.
- **Cross-repo fleet:** unknown — `feedback_fleet_caller_verification_before_celery_deletes.md` rule applies for T-9 dead-code cleanup.

### 18.2 Gap consequences

Without a named owner:
- F1 trace_id repair (T-1) has no ADR sponsor.
- F4 dark pipeline reactivation (T-4/T-5) has no ADR sponsor.
- F5 retention policy (T-6) has no ADR sponsor.

Same as Cat A/B/C posture — Chris (Chief of Staff / Rigby) is de-facto owner for the arc; xx99 R1 provides the formal posture decision, but implementation ownership is unlabelled.

### 18.3 Missing OpsAgent-style dashboard for Cat D

Not audit-in-scope; parent §6.5 parks HeartBeat export as post-xx99 design-preparation. Cat D dashboarding shares the same gap — REST endpoints exist but no dashboard consumes them at HEAD.

---

## 19. Recommended Future Research

**Q28 — Ranked follow-on queue for xx99.**

Ranked by architectural-uncertainty × risk × unblocked-flows (playbook §11.2 discipline).

### R1 (HIGH priority, load-bearing for xx99) — F9 D74 axis posture decision

Cat D contributes negative evidence on all four S1703 F9 options (A/B/C/D). xx99 selects among:
- **Option A** (execution_id spine): add column + populate at 3 writers.
- **Option B** (trace_id spine): column exists + indexed; populate at 3 writers. Smallest schema lift; largest coordination cost.
- **Option C** (shared correlation view): requires A or B first.
- **Option D** (hybrid): requires A or B first.

**Cat D vote:** Option B is smallest-lift for schema; execution requires closing F1 (T-1) at 3 writer paths + wrapping trace_id thread-through discipline. xx99 selects; Cat D does NOT design.

### R2 (HIGH priority) — F1 trace_id write coverage repair

Regardless of xx99's option selection, F1 must close. T-1: dispatcher generates UUID trace_id + wrapper threads from context + base default threads from context + PA path threads from `pa_trace_id` (with UUID transformation). Coordinated 3-writer change plus regression test coverage.

**Rigby SIGN cycle 1 F4 fold — R2 is the gating prerequisite for Option B posture evaluation.** If xx99 wants to keep Option B (trace_id spine) viable as a posture-decision option, R2 is the immediate gate before any posture comparison can be meaningfully evaluated. Without F1 repair, Option B cannot be tested or defended — the runtime credibility problem persists no matter how favorable the schema-lift analysis looks. Within Cat D follow-ons this is the hard gate. R1 (xx99 posture decision) technically comes first in dependency order but cannot land credibly until R2 is either done or explicitly slotted into the same posture PR.

### R3 (HIGH priority) — F4 mining + aggregation pipeline reactivation

T-4 + T-5. Add beat entries for `analyze_pa_tool_patterns` (default queue) + `aggregate_tool_call_stats` (long_running queue, validate 480MB spike behavior). Blocked by no xx99 decision; unblocks PAToolInsight consumer + ToolCallAggregate dashboard consumer.

### R4 (MEDIUM priority) — F2 schema-level correlation columns (execution_id + tool_call_id)

T-2 + T-3. Add columns after xx99 R1 posture decision. Enables §3.B accounting-rule enforcement + closes S1703 F6.

### R5 (MEDIUM priority) — F5 retention policy

T-6. Add `TOOL_CALL_RECORD_RETENTION_DAYS` setting + cleanup Celery task. Should land AFTER T-4 + T-5 to preserve mining window semantics.

### R6 (MEDIUM priority) — F3 base-inherited-agent activity audit

29 of 31 base-inherited agents show ZERO rows at HEAD. Audit each: (a) is it truly idle at HEAD (no invocations)? (b) is it pure-LLM with no tool calls by design? (c) does it need custom-tool wiring (missed by base default → "not implemented" fallback)? xx99 SPECULATIVE flag; may re-route to Group 1900 or Employee OS.

### R7 (MEDIUM priority) — F6 PA path + F3 conversation_id backfill

21.9% conversation_id coverage; PA subset. Consider retro-backfill via task_summary parsing (`[pa-N-hex]` prefix) to enable Cat D↔PA-session correlation at query time.

### R8 (MEDIUM priority) — PA tool for tool-call history query

T-7. Rigby self-serve access via `tool_call_history_tool` in `pa_tool_schemas.py`.

### R9 (LOW priority) — Django admin registration

T-8. Read-only admin classes with filters.

### R10 (LOW priority) — Dead-code cleanup

T-9 + T-12. After cross-repo fleet-caller verification. Delete `unified_pa_entrypoint._record_tool_call` + `BaseAgent._execute_and_record_tool_call` if all-fleet clean.

### R11 (LOW priority) — T-13 non-BaseAgent overrides

Verify production status of `personal_ai_assistant_enhanced.py:1297` + `assistant/base.py:172` overrides. Delete if dead OR retrofit telemetry.

### R12 (LOW priority) — T-11 PAToolInsight dedup enforcement

Add `unique_together = ['tool_name','insight_type','pattern']` when reactivating F4 pipeline (R3 prerequisite).

---

## 20. Appendix

### 20.1 Files inspected

**Cat D core:**
- `core/models_tool_calls.py:1-325` (full)
- `core/agents/base_agent.py:407-464, 3160-3424` (S970 wrapper + default + record helpers)
- `core/services/tool_dispatcher.py:1-1267` (full for §5 analysis; key hotspots :580-978)
- `core/services/unified_pa_entrypoint.py:1830-1870, 2080-2145, 2420-2440` (PA loop dispatch + dead writer + PATI consumer)
- `core/services/deliverable_provenance.py:1-123` (full for §5.4 consumer)
- `core/tasks.py:8280-8290, 12370-12380` (task shims)
- `core/tasks_agents.py:6120-6280` (analyze_pa_tool_patterns implementation)
- `core/tasks_ops.py:3320-3390` (aggregate_tool_call_stats implementation)
- `core/settings.py:1289, 1294, 1580` (queue routing)
- `core/agent_router.py:309-325, 564+` (AGENT_MAP)
- `core/views_audit_api.py:49-70` (REST viewsets)
- `core/serializers_audit.py:45-62` (serializers)
- Cat D related migrations: `0198_session_861_tool_call_records.py`, `0268_pa_tool_insight.py`, `0269_pa_tool_insight_ttl_consistency.py`

**Cross-cat sources:**
- Parent scoping `1700_observability_domain_scoping.md` §3.D, §5, §6.3.
- Sibling audits `1701_..._audit.md` §9 F5 + §19 R3, `1702_..._audit.md` §9 F9 + §16 F1, `1703_..._audit.md` §9 F6 + F9.

### 20.2 Docs inspected

- `docs/topics/agent-system.md:107-113` (S970 auto-wrap coverage claim).
- `docs/topics/personal-assistant.md` (searched for ToolCallRecord — 0 matches).
- `docs/topics/employee-os.md:64-65` (`evidence_for_mission` join surface).
- `docs/topics/celery-workers.md` (searched — 0 matches).
- `docs/PLATFORM_INVENTORY.md` (searched for ToolCallRecord — 0 matches).
- `docs/PLATFORM_WHAT_IT_IS.md:375` (agent-family inventory row).
- `docs/CLAUDE.md` (agent-map + Key Files table).
- `docs/research/ARCHITECTURE_INDEX.md` (21 mentions across §1.N + evidence-scoring subsection).
- `docs/research/actor_identity_attribution_architecture.md:523` (Rigby delegator-vs-executor `agent_name` ambiguity).

### 20.3 Grep patterns used

- `ToolCallRecord\.objects\.create|ToolCallRecord\.record|ToolCallRecord\(` — writer sites.
- `from core\.models_tool_calls|import ToolCallRecord` — reverse import inventory (24 files).
- `_execute_tool_call|_execute_and_record_tool_call|_record_tool_call` — writer method sites.
- `trace_id|conversation_id|tool_call_id|execution_id|call_id` in `core/models_tool_calls.py` — schema field verification.
- `ForeignKey.*ToolCallRecord|OneToOne.*ToolCallRecord|ForeignKey.*PAToolInsight|ForeignKey.*ToolCallAggregate` — FK graph (0 hits).
- `post_save|pre_save|channel_layer|send_signal` on `core/models_tool_calls.py` — event emission (0 hits).
- `retention|purge|cleanup|expires_at|TTL` on ToolCallRecord — retention audit (only PAToolInsight `expires_at` at :309).
- `analyze_pa_tool_patterns|aggregate_tool_call_stats` — task + beat schedule + settings routing.
- `record_telemetry=False` — opt-out caller audit (0 hits).
- `admin.register` on Cat D models — admin registration (0 hits).

### 20.4 Runtime evidence collected (2026-07-03 ORM queries)

- ToolCallRecord total rows: **4144**.
- trace_id NOT NULL: **0 (0.0%)** — F1 evidence.
- conversation_id NOT NULL: **907 (21.9%)** — F6 evidence + writer-path artifact.
- Distinct agent_name values: **39** in 4144 rows.
- Top 10 agent_name: `ResearchAgent` (2389), `PersonalAssistant` (907), `TrendAnalysisAgent` (193), `COOAgent` (112), `CustomerResearchAgent` (60), `CompetitorAnalysisAgent` (59), `MarketMovementMonitorAgent` (54), `MarketAnomalyDetectorAgent` (49), `StockAnalystAgent` (41), `InstitutionalWatcherAgent` (28).
- Top 10 tool_name: `intelligence_tool` (1266), `web_search` (975), `spider_query` (695), `deliverable_tool` (160), `repo_tool` (116), `ops_tool` (79), `delegate_to_specialist` (66), `get_operations_snapshot` (50), `spider_status_tool` (50), `blog_tool` (41).
- Success/Failed: **3579 / 565** (13.6% failure rate).
- Top error_type: `''` (534, unclassified), `TOOL_EXCEPTION` (28), `TOOL_NOT_FOUND` (3), `NotImplemented` (**0**).
- Oldest row: **2026-06-13 00:27:02 UTC**; Newest: **2026-07-03 13:32:13 UTC** (20 days of data, ~200 rows/day).
- ToolCallAggregate total rows: **0** — F4 evidence.
- PAToolInsight total rows: **0** — F4 evidence.
- Base-inherited (31 agents) with ANY ToolCallRecord rows: **2 of 31** (`TopicMinerAgent`=10, `AutonomousContentStudioCoordinator`=1) — F3 evidence.
- Beat schedule entries for `analyze_pa_tool_patterns` / `aggregate_tool_call_stats` / `tool_call` / `ToolCall`: **0** — F4 evidence.

### 20.5 Unresolved unknowns

- **UNK-1**: Are `personal_ai_assistant_enhanced.py:1297` and `assistant/base.py:172` production-live or dead? Verification requires cross-repo fleet-caller grep + import-graph audit. T-13.
- **UNK-2**: Is `NotImplemented` error_type (0 rows at HEAD) genuinely eliminated by S1246 lane L fix, or is it retention-window-invisible (older-than-20-day data purged)? F3 SPECULATIVE.
- **UNK-3**: Is the "480MB spike" note at `settings.py:1289` for `aggregate_tool_call_stats` current at HEAD (4144 rows) or a stale artifact from an older row-count regime? T-5 remediation may reveal.
- **UNK-4**: Does `pa_tool_learning_enricher` at `core/services/pa_tool_learning_enricher.py:20-50` (per E3 report) exist? Not independently verified.
- **UNK-5**: Are there manual (out-of-band) triggers for `analyze_pa_tool_patterns` / `aggregate_tool_call_stats` that generate zero output because upstream data is thin? Or purely unwired?

### 20.6 Rigby SIGN cycle 1 fold notes

**Session 1704 close SIGN cycle 1** on arc pin `pa-e7fbacc996b34b44` (fresh SIGN pin `pa-f7417e6ac21d4f23` minted per playbook §15 but routed-around by `tools/pa_local.sh:128` wrapper hard-code per S1600/S1700/S1701/S1702/S1703 precedent). Single-batch 4-question pattern per D48 21st arm. All four questions answered in one Rigby response with SIGN verdicts + confidence levels + 4 fold instructions.

**Rigby verdicts:**
- **Q1 (coverage-completeness)**: **CONFIRM** at **High** confidence. F1-F9 correctly scoped to Cat D boundary per parent §3.D. No split/merge needed; no missing CRITICAL/HIGH finding at HEAD. F9 correctly kept as D74-axis contribution rather than separate system bug.
- **Q2 (drift-severity D1-D8 ranking)**: **SIGN-with-edits** at **Medium-High** confidence. D7 REFUTED tool_call_id hypothesis is correct framing. Escalation recommendation: promote "upstream references to non-existent Cat D correlation columns" from MEDIUM/LOW to HIGH (F2 fold).
- **Q3 (D74 axis F9 correctness)**: **SIGN-with-edits** at **Medium-High** confidence. Core conclusion is right (Cat D provides strongly negative evidence on Option B as currently implemented). Wording tightening needed: "negative evidence on all four options equally" is slightly overstated — Cat D is actively broken for Option B vs incomplete/blocked on Option A (F1 fold).
- **Q4 (R1-R12 ranking + xx99 scope discipline)**: **SIGN-with-edits** at **Medium-High** confidence. R1/R2/R4/R5 ordering defensible. R3 dark-pipeline reactivation stays in Cat D scope (own tiered pipeline, not Group 1900 territory). Main ranking observation: R2 F1 trace_id repair is the immediate hard gate for Option B viability — should be flagged as posture-evaluation prerequisite (F4 fold).

**Folds landed pre-commit (all 4):**

- **F1 (Medium)** — §1.1 F9 bullet + §9.2 spine bottom-line: replaced "negative evidence on all four options equally" with "blocks all options; actively broken for Option B today (100% NULL trace_id)" plus explicit distinction between Cat D's Option B (broken-not-blocked) vs Option A (incomplete-not-broken) posture. Also added spine-lift-decomposition note that Option B's smaller schema lift does NOT reduce coordination lift below Option A's.
- **F2 (Low)** — §14 drift table: D7 `tool_call_id` hypothesis-refuted severity **escalated MEDIUM → HIGH** per Rigby "upstream references to non-existent Cat D correlation columns directly misguide cross-cat dedup work — more dangerous than doc omissions." New drift row **D9 (HIGH)** added for the sibling case at parent §3.B accounting-rule column-set citation (execution_id + trace_id + tool_call_id) — same fold, companion drift item.
- **F3 (Low)** — §1.1 F9 bullet + §9.2 spine table commentary: added explicit "schema lift vs coordination lift" decomposition for Option B. Column-exists-and-is-indexed schema advantage is preserved as evidence, but coordination lift (three-writer trace_id thread-through + dispatcher UUID format overhaul + PA loop pa-N-hex→UUID transform) is called out as equivalent to Option A's cost.
- **F4 (Low)** — §19 R2 addendum: R2 (F1 trace_id write coverage repair) is the **gating prerequisite** for any Option B posture evaluation. Without F1 close, Option B cannot be tested or defended — the runtime credibility problem persists no matter how favorable the schema-lift analysis looks. R1 comes first in dependency order but cannot land credibly until R2 is either done or slotted into the same posture PR.

**Rigby CONFIRM verdicts (no folds required beyond F1-F4):**
- Q1 coverage-completeness High.
- Q2 D7 tool_call_id hypothesis-refuted framing correct.
- Q3 core conclusion correct (only wording tightening needed).
- Q4 R3 dark-pipeline reactivation stays in Cat D scope + R1/R4/R5 ordering defensible.

**D48 preemptive stability-probe gate status:** **21st arm HOLDING CLEAN** at S1704 close per single-batch-4-question criterion. 16-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506+S1601+S1602+S1603+S1604+S1605+S1606+S1699+S1700+S1701+S1702+S1703+S1704 CONFIRMED. Playbook v3 §15 codification-ready-strengthened-even-further.

### 20.7 Verifier-loop corrections landed

**Pre-Explore verifier corrections (before dispatching 6-parallel Explore):**
- ORM-verified `ToolCallRecord.objects.count() == 4144` and `trace_id__isnull=False` count is **0** (100% NULL).
- ORM-verified `conversation_id__isnull=False` count is **907** (21.9%).
- ORM-verified 32 distinct `agent_name` values (post-Explore verifier refined to **39**).
- Confirmed `__init_subclass__` at `base_agent.py:428-464` fires only when `_execute_tool_call in cls.__dict__`.
- MRO walk on AGENT_MAP → 52 override + 31 inherit BaseAgent default → seeded Explore priors.

**Post-Explore verifier corrections (after 6-parallel Explore returned):**
- **CRITICAL correction to F-CANDIDATE-2 severity:** Pre-Explore prior called the 31-agent base-inherited subset "silent zero-write." Explore 2 caught: BaseAgent default `_execute_tool_call` at `:3168-3316` has its OWN inline recorder in the `finally` block at `:3276-3315` (S1085 tag at `:3188`). Reframed as F3 MEDIUM: mechanism works; empirically 29 of 31 base-inherited agents have zero rows, but that's a usage/idle-agent artifact, NOT a coverage-mechanism bug.
- Refined distinct-agent-name count from pre-Explore 32 → verified 39 via ORM.
- Confirmed all 5 return branches of `_execute_inner` covered per S1115 finding 17 closure (E2 :707, :738, :826, :855, :884).
- Confirmed `analyze_pa_tool_patterns` + `aggregate_tool_call_stats` DEFINED + queue-routed but zero beat entries (F4). Both consumer tables at 0 rows.
- Confirmed `deliverable_provenance.py:105` executes `ToolCallRecord.objects.filter(trace_id=execution.trace_id)` — empirically empty for every deliverable at HEAD (F9).
- Confirmed PLATFORM_INVENTORY.md has ZERO ToolCallRecord references (E5 + independent grep).
- Independently corroborated E3 REST endpoint enumeration + E4 correlation-matrix rows.

### 20.8 Frontmatter provenance

- `authority: child-audit` per playbook §11.2.
- `category: child_audit` per playbook §11.2.
- `session: 1704`.
- `child_slot: P4` per parent §5 sequence table.
- `domain_slug: observability`.
- `research_group: 1700`.
- `status: active` post-SIGN cycle 1 (SIGN-with-edits at Medium-High confidence — F1-F4 folds landed pre-commit).
- `verifier_loop: [pre-explore-verified, post-explore-verified]`.
- `head_commit`: (populated at commit).
