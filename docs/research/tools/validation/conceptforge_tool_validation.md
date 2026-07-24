# `conceptforge_tool` — Validation Report (S2920)

**Tool:** `conceptforge_tool`
**Schema:** `core/services/pa_tool_schemas.py:4931`
**Handler:** `core/services/td_handlers_gateway.py:2210` (`_handle_conceptforge`)
**Register site:** `core/services/tool_dispatcher.py:587`
**Session:** S2920 (Slice 4 batch 3 — gateway medium-tier read-only trio: mobile + calendar + conceptforge; template-preservation swap)
**HEAD at validation:** `9561a1932` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2920 T0 SIGN AGREE — swap-in target after mutation-scan disqualified proactive + self_awareness (+ profile in follow-up); span 82 lines; 0/4 mutation verbs; 0/3 Appendix A/N first-hop literals in span 2210-2291.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`conceptforge_tool` surfaces telemetry for the ConceptForge pipeline — a multi-stage generative concept synthesizer whose runs, per-stage records, and produced artifacts land in three tables: `ConceptForgeRun` (top-level run — source_type, domain, status, quality_score, duration_ms), `ConceptForgeStageRun` (per-stage record with agent binding), `ConceptForgeArtifact` (deliverables produced per run, with a primary/secondary flag). Use it when the operator asks "what concept forge runs are in flight?" / "what did concept forge produce for run X?" / "aggregate concept forge quality + throughput?".

Distinct from `narrative_tool` (batch 2 — narrative/shift/evidence surface, not pipeline runs), from `campaign_tool` (batch 1 — client campaign lifecycle), and from `analytics_tool` (batch 1 — event-stream aggregates).

## Covered actions

- `runs` — **in scope this ship** — lists `ConceptForgeRun` rows ordered by `-created_at`. Supports `status` filter (via `payload.get('status')`). Returns `{action, count, runs: [{id, source_type, source_title, domain, status, quality_score, duration_ms, created_at}]}`.
- `run_detail` — **in scope this ship** — requires `run_id`. Fetches one `ConceptForgeRun` + its stages (ordered by `stage_order`) + its artifacts (ordered by `created_at`). Returns `{action, run: {...}, stages: [{stage_name, agent_used, status, duration_ms}], artifacts: [{id, name, kind, is_primary}]}` — no `count` on stages/artifacts.
- `stats` — **in scope this ship** — default action; aggregate rollup — `total_runs + avg_quality_score + by_status + by_source_type`. **NOT user-scoped** — system-wide aggregate.

Default action = `stats` (per `payload.get('action', 'stats')` at handler line 2212).

## 3. Schema notes

- **Required:** `action` (enum: `runs` / `run_detail` / `stats`).
- **Optional:** `run_id` (string — required in practice on `run_detail`; explicit `{'error': 'Provide run_id for run_detail'}` if missing at handler line 2243), `status` (string — only applied on `runs` action; silently ignored on other actions), `limit` (int; default 20, hard cap 50 via `min(int(payload.get('limit', 20)), 50)` at handler line 2213; applies to `runs` only — `run_detail` and `stats` return full data).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4929-4954`.
- **Envelope shape:** `runs` returns a `count` field; `run_detail` returns `run` + `stages` + `artifacts` lists without per-list counts; `stats` returns 4 top-level rollup fields. Same envelope-key asymmetry-across-actions pattern already at 3/3 triggered post-S2919 batch 2.
- **`limit` does not gate stages or artifacts on `run_detail`:** all stages + all artifacts for the requested run are returned regardless of `limit`.

## 4. Golden-path examples

**Example 1 — aggregate pipeline stats (most operator-common):**
```json
{"action": "stats"}
```
Expected envelope: `{"action": "stats", "total_runs": <int>, "avg_quality_score": <float>, "by_status": {"<status>": <int>, ...}, "by_source_type": {"<type>": <int>, ...}}`.

**Example 2 — recent runs filtered by status:**
```json
{"action": "runs", "status": "completed", "limit": 25}
```
Expected envelope: `{"action": "runs", "count": <int ≤ 50>, "runs": [{"id": ..., "source_type": ..., "source_title": ..., "domain": ..., "status": "completed", "quality_score": <float|null>, "duration_ms": <int|null>, "created_at": "<isoformat|null>"}, ...]}`.

**Example 3 — full drill-down on a single run:**
```json
{"action": "run_detail", "run_id": "<uuid>"}
```
Expected envelope: `{"action": "run_detail", "run": {"id": ..., "source_type": ..., "source_title": ..., "domain": ..., "status": ..., "quality_score": ..., "duration_ms": ...}, "stages": [{"stage_name": ..., "agent_used": ..., "status": ..., "duration_ms": ...}, ...], "artifacts": [{"id": ..., "name": ..., "kind": ..., "is_primary": <bool>}, ...]}`.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": "Unknown conceptforge_tool action: <action>"}` at handler line 2287. Not raised — in-envelope.
- **Handler exception:** caught at line 2289, logged via `logger.error(..., exc_info=True)` (CONCEPTFORGE log stream), returns `{"error": <str>}`. No `error_code` field — **legacy-error envelope** (15th corroborating instance post-S2919 batch 2's 12-instance count + mobile 13th + calendar 14th). Substrate arc still gated on explicit Chris directive per 00-START forbidden-list.
- **Missing `run_id` on `run_detail`:** returns `{"error": "Provide run_id for run_detail"}` at handler line 2243. In-envelope, not raised.
- **Unknown `run_id` on `run_detail`:** returns `{"error": "ConceptForgeRun <id> not found"}` at handler line 2246. In-envelope, not raised.
- **Empty result set:** returns `count: 0` + empty `runs` list, or zero-valued aggregate (`stats`), or empty `stages`/`artifacts` lists on `run_detail`. No error.
- **`status` filter ignored on non-`runs` actions:** silent — no schema-validation warning.
- **`stats` not user-scoped:** returns system-wide aggregate; pipeline is not multi-tenant in current schema. Not a defect — noted for documentation.
- **`limit` hard cap:** 50. No pagination cursor.
- **Truncation:** `source_title` truncated to 100 chars via `(r.source_title or '')[:100]` on `runs` (line 2231); full string returned on `run_detail`. Consumers doing exact-match on titles from `runs` output may need the `run_detail` fallback for full string.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `ConceptForgeRun.objects.order_by(...)` / `.filter(...)` / `.all()` | `read` | `td_handlers_gateway.py:2220-2224, 2244, 2275` | ORM SELECT; documented |
| `ConceptForgeStageRun.objects.filter(...).order_by(...)` | `read` | `td_handlers_gateway.py:2247` | ORM SELECT; documented |
| `ConceptForgeArtifact.objects.filter(...).order_by(...)` | `read` | `td_handlers_gateway.py:2248` | ORM SELECT; documented |
| `qs.aggregate(Avg)` + `qs.values_list(...).annotate(Count).values_list(...)` | `read` | `td_handlers_gateway.py:2276-2278` | ORM AGGREGATE; documented |

**Appendix N (Network-Preflight) — N/A.** No network first-hop.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop.

Both Appendices declared N/A per S2918 T0 SIGN Q2 gateway-wide DISAGREE (0/17 gateway tools with the three literal patterns). S2920 T0 SIGN Q2 per-tool confirmation: conceptforge span 2210-2291 contains none of these literals — grep receipts in Rigby T0 SIGN turn 2 (swap-in verification).

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification appended to the S2920 handoff. Expected shapes documented in §4 golden-path examples.

## Related

- **Adjacent tools:** `narrative_tool` (batch 2 — same gateway ORM-shape; downstream narrative surface); `campaign_tool` (batch 1 — client project lifecycle); `analytics_tool` (batch 1 — event-stream aggregates); `ats_tool` (batch 2 — same ORM aggregate shape).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1); models at `core/models_conceptforge.py` (`ConceptForgeRun`, `ConceptForgeStageRun`, `ConceptForgeArtifact`).
- **Prior ratifications:** S2892 Path B open, S2918 Slice 4 batch 1, S2919 Slice 4 batch 2 (discord/distribution/ats/narrative — same gateway ORM-direct shape).
- **Ledger rows relevant to this ship:**
  - **Legacy-error envelope 15th instance** — continued corroboration; still gated on explicit Chris directive per 00-START forbidden-list.
  - **Template-preservation swap 2nd instance (batch-level)** — batch 3 dropped proactive + self_awareness + profile after mutation-scan; conceptforge swapped in as a clean read-only replacement. Corroborates S2919 batch 2 vip_invite → narrative swap. Chris + Rigby aligned to codify swap-methodology at next-session close-cascade.
