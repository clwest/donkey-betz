# `self_awareness_tool` — Validation Report (S2921)

**Tool:** `self_awareness_tool`
**Schema:** `core/services/pa_tool_schemas.py:4989`
**Handler:** `core/services/td_handlers_gateway.py:2482` (`_handle_self_awareness`)
**Register site:** `core/services/tool_dispatcher.py:589`
**Session:** S2921 (Slice 4 batch 4 — mutation-capable template pilot; single-tool ship of `self_awareness` per Rigby Q1(b) + Chris ratification; other 3 mutation candidates — `vip_invite` / `proactive` / `profile` — deferred to batch 5 once the 4-tier blast-radius schema has been exercised on the cleanest mutation surface)
**HEAD at validation:** `28ffffa47` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape) + §5a mutation-containment filled with 4-tier blast-radius classification per _TEMPLATE §5a amendment shipped in the same PR. Post-merge live-dispatch verify per PLAYBOOK-7.4.4 on all 5 actions including the mutation action.
**Category upgrade target:** `untested` → `validated_full` (all 5 actions in scope this ship — 4 pure-read + 1 mutation classified `contained`)
**Rigby SIGN:** S2921 T0 SIGN AGREE — 2-turn cycle grounded in 12 `repo_tool` receipts (10 turn 1 + 2 turn 2); zero rubber-stamp; corrected 2 of 4 mutation-verb claims in the S2920 close 00-START (vip_invite = also flips `User.is_active`; profile = `get_or_create×2 + save×1`, not `save + get_or_create`); reversed Claude's initial Q1(a) recommendation via ship-progress-vs-template-purity argument; Q3 confirmed §5a as-shipped accommodates the 4-tier schema without template rewrite (schema is authoring taxonomy, not safety invariant → doc-only).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`self_awareness_tool` surfaces the platform's self-observation surface: 3 tables — `SystemMetrics` (per-snapshot CPU/memory/active-agent/pending-task/error-count/self-analysis-score row, produced by the `collect` action or by periodic beat schedules), `SelfAnalysisReport` (rolling analysis-type rows with `score` + `critical_issues` + `warning_issues` + `confidence`), and `SystemEvolution` (evolution-history rows with `evolution_type` + `status` + `title` + `confidence_score` + `priority`). Use it when the operator asks "what does the platform know about itself right now?" / "which self-analysis reports have run recently?" / "what evolution moves have we tried?" / "record a fresh system-metrics snapshot right now."

Distinct from `dashboard_tool` (external-facing operator dashboard, no self-observation semantics), from `system_health` handlers under `td_handlers_ops.py` (operational health checks — worker liveness, queue depth, DB freshness — not persistent self-analysis rows), and from `body_systems`-scoped tools (per-organ HEART/LUNGS/etc. — physiological metaphor over the same substrate but scoped by system, not aggregate).

## Covered actions

- `metrics` — **in scope this ship** — verified live. Returns latest `SystemMetrics` row (`.order_by('-timestamp').first()`). Envelope: `{action, metrics: {timestamp, cpu_usage, memory_usage, active_agents, pending_tasks, error_count, self_analysis_score}}` or `{action, metrics: null, message: 'No metrics recorded yet'}` when the table is empty.
- `reports` — **in scope this ship** — verified live. Returns most-recent `SelfAnalysisReport` rows (`.order_by('-timestamp')[:limit]`). Envelope: `{action, count, reports: [{id, analysis_type, score, critical_issues, warning_issues, confidence, timestamp}]}`.
- `evolution` — **in scope this ship** — verified live. Returns most-recent `SystemEvolution` rows (`.order_by('-timestamp')[:limit]`). Envelope: `{action, count, evolutions: [{id, evolution_type, status, title, confidence_score, priority, timestamp}]}`.
- `stats` — **in scope this ship** — verified live. Default action per `payload.get('action', 'stats')` at handler line 2484. Aggregate rollup — `total_reports + total_evolutions + latest_self_analysis_score`. No user-scope (all system-wide).
- `collect` — **in scope this ship — mutation, classified `contained`** — verified live. Writes 1 `SystemMetrics` row via `SystemMetrics.objects.create(...)` at handler lines 2573–2581. Reads `AgentExecution.filter(status='running', created_at__gte=one_hour).count()` + `CeleryTaskEvent` counts (SUCCESS / FAILURE / STARTED in the last hour) to populate the snapshot. See §5a for blast-radius classification + deferral-status transition rationale.

Default action = `stats` (per `payload.get('action', 'stats')` at handler line 2484).

## 3. Schema notes

- **Required:** `action` (enum: `metrics` / `reports` / `evolution` / `stats` / `collect`).
- **Optional:** `limit` (int; default 10 per schema description, hard cap 30 via `min(int(payload.get('limit', 10)), 30)` at handler line 2485; applies to `reports` / `evolution` only — `metrics` returns single row, `stats` returns aggregate, `collect` returns snapshot ID + counts).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4989-5016`.
- **Envelope shape:** `reports` / `evolution` return a `count` field + list. `metrics` returns a single `metrics` object (or `null` + `message`). `stats` returns 3 top-level rollup fields (`total_reports`, `total_evolutions`, `latest_self_analysis_score`) with no `count`. `collect` returns snapshot ID + timestamp + populated counts. Consistent with the envelope-key-asymmetry-across-actions pattern already at 3/3 triggered post-S2919 batch 2 (still Chris-gated; no new distinct sub-pattern this batch).
- **`limit` default divergence:** schema description says default 10; handler `min(int(payload.get('limit', 10)), 30)` matches. Both the default and the cap differ from the gateway norm (default 20, cap 50 elsewhere) — recording as an authoring detail, not a defect. First observation of this specific divergence in Slice 4; 2nd instance triggers Ledger evaluation as a "per-tool limit default divergence" candidate.

## 4. Golden-path examples

**Example 1 — aggregate self-awareness stats (most operator-common; default action):**
```json
{"action": "stats"}
```
Expected envelope: `{"action": "stats", "total_reports": <int>, "total_evolutions": <int>, "latest_self_analysis_score": <float|null>}`.

**Example 2 — latest system-metrics snapshot:**
```json
{"action": "metrics"}
```
Expected envelope (populated): `{"action": "metrics", "metrics": {"timestamp": "<isoformat>", "cpu_usage": <float|null>, "memory_usage": <float|null>, "active_agents": <int>, "pending_tasks": <int>, "error_count": <int>, "self_analysis_score": <float|null>}}`.
Empty state: `{"action": "metrics", "metrics": null, "message": "No metrics recorded yet"}`.

**Example 3 — recent self-analysis reports (bounded):**
```json
{"action": "reports", "limit": 5}
```
Expected envelope: `{"action": "reports", "count": <int ≤ 30>, "reports": [{"id": ..., "analysis_type": "...", "score": <float|null>, "critical_issues": <int>, "warning_issues": <int>, "confidence": <float|null>, "timestamp": "<isoformat|null>"}, ...]}`.

**Example 4 — record a fresh metrics snapshot (mutation; contained):**
```json
{"action": "collect"}
```
Expected envelope: `{"action": "collect", "snapshot_id": "<pk>", "timestamp": "<isoformat>", "active_agents": <int>, "pending_tasks": <int>, "completed_tasks_1h": <int>, "errors_1h": <int>, "message": "Metrics snapshot recorded"}`. Side effect: 1 new `SystemMetrics` row (cpu/memory/disk zeroed — comment at handler lines 2574–2576 says "not measurable on Railway"; the four count fields are live).

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": "Unknown self_awareness_tool action: <action>. Valid: metrics, reports, evolution, stats, collect"}` at handler line 2593. Not raised — in-envelope.
- **Handler exception:** caught at line 2595, logged via `logger.error(..., exc_info=True)` (SELF_AWARENESS log stream), returns `{"error": <str>}`. No `error_code` field — **legacy-error envelope** (16th corroborating instance post-S2920 batch 3's 15-instance count). Substrate arc still gated on explicit Chris directive per 00-START forbidden-list; Rigby S2920 Q4(a) semantic-nuance refresh (treat `error_code` values as first-class semantics) deferred post-D6 per S2921 Q5(c) Chris ratification.
- **Empty result set:** `metrics` returns explicit `{metrics: null, message: 'No metrics recorded yet'}`. `reports` / `evolution` return `count: 0` + empty list. `stats` returns zero-valued aggregate + `latest_self_analysis_score: null`.
- **`collect` in an empty environment:** `SystemMetrics.objects.create(...)` succeeds even when `AgentExecution` and `CeleryTaskEvent` tables are empty — the four `.count()` reads all return 0, and the row is written with zeros in every populated field. Not an error; the snapshot semantically represents "system was idle in the observed 1-hour window."
- **`limit` hard cap:** 30 (differs from gateway norm of 50). No pagination cursor.
- **No user scope:** unlike `calendar_tool` / `experiment_tool` / `campaign_tool`, `self_awareness_tool` is inherently system-wide. Every action reads global state; `collect` writes a global row. No `user_id` parameter surfaced or referenced in the handler. Multi-tenant leak candidate absent by design — this tool is a platform-scope introspection surface. Recording explicitly so a future workspace-scope pass doesn't try to add a user filter without redesigning the model layer.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1 — filled per 4-tier blast-radius amendment shipped this PR)

The `collect` action is the tool's only mutation action. Classification and rationale per the 4-tier blast-radius schema added to `_TEMPLATE_per_tool_validation.md` §5a in this ship (see the amendment for the full taxonomy).

| Action | Mutation type | Blast-radius tier | Rationale |
|---|---|---|---|
| `collect` | `SystemMetrics.objects.create(...)` — 1 row (handler line 2573) | `contained` | Single-row INSERT into an append-only telemetry table (`self_awareness.models.SystemMetrics`). No FK cascade, no `post_save` signal chain observed on the model (grep-verified), no cross-user reach (table is system-scope by design; no user FK), no bulk. Idempotent-in-effect (each call adds one snapshot; retries produce duplicate snapshots but do not corrupt existing rows). Safest possible mutation shape in Slice 4 — chosen deliberately as the batch-4 pilot per Rigby Q1(b) recommendation. |

**Deferral status:** NOT deferred. Ship-in-scope this batch — this ship exercises `collect` post-merge to verify the `contained` classification holds end-to-end. Slice-when-covered pointer = **S2921 batch 4 pilot** (this ship). If post-merge verify surfaces any cascade / signal / cross-table effect grep missed, tier is reclassified up and this doc is amended.

**Comparison to batch-5 candidates (deferred to next ship):**
- `vip_invite.revoke` — `spreading` (multi-row: invite row + `redeemed_by.is_active=False` at handler lines 1008–1009; user-account state affected across a second table).
- `proactive.bulk_ack` — `spreading` (bulk multi-row: up to 200 rows in `ProactiveNotification.filter(...).update(is_read=True)` at handler line 1677; user-scoped but broad within that user).
- `profile.update_preferences` — `spreading` (`get_or_create` may implicitly create the `EnhancedUserProfile` row at line 2394 + `enhanced.save()` at line 2415 persists preference changes; row is anchored by user FK, reachable across multiple contexts).

Rigby S2921 T0 SIGN turn 1 grep-verified these classifications against the handler line-ranges above. Batch 5 will fill §5a per-tool for each of the three `spreading` tools.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `SystemMetrics.objects.order_by(...).first()` / `.create(...)` | `read` / `db_write` | `td_handlers_gateway.py:2491, 2542, 2573` | ORM SELECT + INSERT; documented |
| `SelfAnalysisReport.objects.order_by(...).all()` | `read` | `td_handlers_gateway.py:2508, 2540` | ORM SELECT; documented |
| `SystemEvolution.objects.order_by(...).all()` | `read` | `td_handlers_gateway.py:2524, 2541` | ORM SELECT; documented |
| `AgentExecution.objects.filter(...).count()` | `read` | `td_handlers_gateway.py:2560` | ORM SELECT (COUNT); documented — only fires on `collect` action |
| `CeleryTaskEvent.objects.filter(...).count()` (×3) | `read` | `td_handlers_gateway.py:2563, 2566, 2569` | ORM SELECT (COUNT); documented — only fires on `collect` action |
| `timezone.now()` / `timedelta` | `read` | `td_handlers_gateway.py:2554–2555` | Clock read; documented |

**Appendix N (Network-Preflight) — N/A.** No network first-hop.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop.

Both Appendices declared N/A per S2918 T0 SIGN Q2 gateway-wide DISAGREE (0/17 gateway tools with the three literal patterns). S2921 T0 SIGN Q2 per-tool confirmation: self_awareness span 2482–2597 contains none of these literals — grep receipts in Rigby T0 SIGN turn 1 (`repo_tool.read_file` on the handler span).

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification on all 5 actions (including the mutation action `collect`) appended to the S2921 handoff. Expected envelope shapes documented in §4 golden-path examples.

**Post-merge verification protocol for `collect`:** Rigby dispatches `{"action": "collect"}`; response envelope contains `snapshot_id` + `timestamp`; ORM cross-check confirms exactly one new `SystemMetrics` row exists with the returned `pk` and populated counts matching the response payload. If the row is absent or counts mismatch, the `contained` classification is invalidated and the doc is amended to reflect the actual observed blast-radius.

## Related

- **Adjacent tools:** `dashboard_tool` (external-facing operator dashboard, no self-observation semantics), `analytics_tool` (batch 1 — same gateway ORM shape but distinct scope), `audit_tool` (batch 1 — audit-run introspection, not platform-metrics).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1 — §5a 4-tier blast-radius schema amended in this ship); models at `self_awareness/models.py` (`SystemMetrics`, `SelfAnalysisReport`, `SystemEvolution`).
- **Prior ratifications:** S2892 Path B open, S2918–S2920 Slice 4 batches 1–3 (all pure-read).
- **Ledger rows relevant to this ship:**
  - **Legacy-error envelope 16th instance** — continued corroboration; still gated on explicit Chris directive per 00-START forbidden-list. Semantic-nuance refresh (S2920 Q4(a)) deferred post-D6 per S2921 Q5(c) Chris ratification.
  - **First mutation-shipped Slice 4 tool** — establishes the 4-tier blast-radius pattern in-doc; batch 5 (vip_invite + proactive + profile) will populate `spreading` tier from the same template.
  - **Template-preservation swap codified as sweep-doc note (2 triggers now — S2919 + S2920)** — added to `_TEMPLATE_per_tool_validation.md` §5a in this ship with an explicit 3rd-trigger-outside-sweep Playbook-promotion rule per Rigby Q4 recommendation + Chris ratification.
  - **`limit` default divergence (default 10, cap 30)** — 1st Slice-4 instance of a per-tool `limit` cap that differs from the gateway norm (default 20, cap 50). 2nd instance triggers Ledger evaluation.
  - **00-START span-math burn (3rd consecutive session pattern watch)** — S2919 + S2920 burned on medium-tier claims; regeneration from `repo_tool` receipts landing in this session's close cascade per Rigby Q5(b) recommendation + Chris ratification.
