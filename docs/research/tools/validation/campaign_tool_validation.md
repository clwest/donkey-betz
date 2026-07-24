# `campaign_tool` — Validation Report (S2918)

**Tool:** `campaign_tool`
**Schema:** `core/services/pa_tool_schemas.py:4872`
**Handler:** `core/services/td_handlers_gateway.py:2048` (`_handle_campaign`)
**Register site:** `core/services/tool_dispatcher.py:585`
**Session:** S2918 (Slice 4 batch 1 — gateway small-tier mixed pilot: analytics + audit + campaign + experiment)
**HEAD at validation:** `e1a09d8d0` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2918 T0 SIGN AGREE-with-edits — mixed-pilot batch composition ratified with 20+ `repo_tool` receipts; Rigby's initial "probable mutation surface" verdict was walked back after verb-scan showed no `.save()`/`.create(`/`.update(`/`.delete(` in handler body. All 3 actions are pure ORM SELECT.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`campaign_tool` reads client-campaign rows from `Campaign` and their attached deliverables from `CampaignDeliverable`. Use it when the operator asks "what campaigns are running?" / "what's the status of campaign X?" / "how many campaigns are in each tier?". It's a **read-only** surface for the campaign-orchestration domain; mutation flows for campaigns live in `core.agents.campaign_orchestrator_agent` and `core.views_campaign`, not in this tool.

Distinct from `deliverable_tool` (which reads generic `Deliverable` rows, not the `CampaignDeliverable` linkage) and from `campaign_orchestrator_agent` (which creates/mutates campaigns).

## Covered actions

- `list` — **in scope this ship** — default action; lists `Campaign` rows ordered by `-created_at`. Supports `status` filter. **User-scoped when `user_id` is set** — filters `Campaign.objects.filter(user_id=user_id)`. Truncates to `limit` (default 20, hard cap 50).
- `detail` — **in scope this ship** — requires `campaign_id`. Returns the campaign row + all attached `CampaignDeliverable` rows ordered by `created_at`. Not user-scoped in this action (no `user_id` filter applied when fetching by `campaign_id`).
- `stats` — **in scope this ship** — aggregate over all campaigns (user-scoped if `user_id` set). Returns `total_campaigns` + `by_status` dict + `by_budget_tier` dict.

Default action = `list` (per `payload.get('action', 'list')` at handler line 2050).

## 3. Schema notes

- **Required:** `action` (enum: `list` / `detail` / `stats`).
- **Optional:** `campaign_id` (UUID string — required for `detail`; ignored otherwise), `status` (string — filters `list` only, not `stats`), `limit` (int; default 20, hard cap 50 via `min(int(payload.get('limit', 20)), 50)` at handler line 2051).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4870-4895`.
- **Authority note:** `list` and `stats` respect `user_id` (multi-tenant filter applied); `detail` does NOT — it fetches by `campaign_id` globally. Under the single-user pre-prod operating context (per `project_single_user_pre_prod_operating_context`), this is not a bug today, but flagged for post-D6 review as a candidate multi-tenant leak if the platform moves to prod.

## 4. Golden-path examples

**Example 1 — list active campaigns for current user:**
```json
{"action": "list", "status": "active", "limit": 10}
```
Expected envelope: `{"action": "list", "count": <int ≤ 50>, "campaigns": [{id, name, status, budget_tier, client_name, product_name, progress_percent, created_at}, ...]}`.

**Example 2 — full campaign detail with deliverables:**
```json
{"action": "detail", "campaign_id": "<UUID>"}
```
Expected envelope: `{"action": "detail", "campaign": {id, name, status, budget_tier, client_name, product_name, progress_percent}, "deliverables": [{id, name, deliverable_type, status, platform}, ...]}`.

**Example 3 — aggregate stats:**
```json
{"action": "stats"}
```
Expected envelope: `{"action": "stats", "total_campaigns": <int>, "by_status": {<status>: <count>, ...}, "by_budget_tier": {<tier>: <count>, ...}}`.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": "Unknown campaign_tool action: <action>"}` at handler line 2121. In-envelope.
- **Handler exception:** any exception is caught at line 2123, logged via `logger.error(..., exc_info=True)`, returns `{"error": <str>}`. No `error_code` — legacy-error envelope (7th instance corroborating post-S2917).
- **`detail` missing `campaign_id`:** returns `{"error": "Provide campaign_id for detail"}` at line 2083. In-envelope, not raised.
- **`detail` with non-existent `campaign_id`:** returns `{"error": "Campaign <id> not found"}` at line 2086. In-envelope.
- **Empty result set on `list` or `stats`:** returns `count: 0` / `total_campaigns: 0` with empty containers. No error.
- **`limit` hard cap:** 50. No pagination cursor.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `Campaign.objects.order_by(...)` + `.filter(...)` | `read` | `td_handlers_gateway.py:2058-2064,2084,2109-2113` | ORM SELECT; documented |
| `CampaignDeliverable.objects.filter(...)` | `read` | `td_handlers_gateway.py:2087` | ORM SELECT; documented |

**Appendix N (Network-Preflight) — N/A.** No network first-hop.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop.

Both Appendices declared N/A per S2918 T0 SIGN Q2 DISAGREE verdict.

**Note on read-only classification:** Rigby's Q3 verb-scan probe searched for `.save()` / `.create(` / `.update(` / `.delete(` in the handler body and returned 0 matches. Combined with a direct read of lines 2048-2126, this handler is definitively pure ORM SELECT — no mutation vectors, no §5a deferral needed.

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification appended to the S2918 handoff. Expected shapes documented in §4.

## Related

- **Adjacent tools:** `analytics_tool` / `audit_tool` / `experiment_tool` (same slice batch); `deliverable_tool` (generic content, not campaign-scoped).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1); models at `core/models_campaign.py`.
- **Mutation surfaces (out of scope this tool):** `core/agents/campaign_orchestrator_agent.py` handles create/mutate; `core/views_campaign.py` exposes REST mutation endpoints. Neither is reachable through this tool.
- **Prior ratifications:** S2892 Path B open, S2917 Slice 3 CLOSE (22/22).
- **Ledger rows relevant to this ship:**
  - Legacy-error envelope 7th corroborating instance.
  - Multi-tenant leak candidate — `detail` action bypasses `user_id` filter. Post-D6 evaluation only (single-user pre-prod context still holds).
