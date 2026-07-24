# `analytics_tool` — Validation Report (S2918)

**Tool:** `analytics_tool`
**Schema:** `core/services/pa_tool_schemas.py:4458`
**Handler:** `core/services/td_handlers_gateway.py:643` (`_handle_analytics`)
**Register site:** `core/services/tool_dispatcher.py:597`
**Session:** S2918 (Slice 4 batch 1 — gateway small-tier mixed pilot: analytics + audit + campaign + experiment)
**HEAD at validation:** `e1a09d8d0` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2918 T0 SIGN AGREE-with-edits — mixed-pilot batch composition ratified with 20+ `repo_tool` receipts; Appendix A/N declared N/A for gateway (0/17 first-hop literals in `td_handlers_gateway.py`).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`analytics_tool` surfaces DeliverableEvent-based behavioral analytics — event counts by type/source, time-windowed queries, and the full Stage 3 ATR-24h dashboard. Use it when the operator asks "how many actions today?" / "what events fired for deliverable X?" / "what does the ATR dashboard show?". It replaces writing SQL against `DeliverableEvent` or hitting the `stage3-dashboard` REST endpoint by hand.

Distinct from `audit_tool` (which queries `AuditFinding` / `WiringDefect` / `CitationViolation` — quality signals, not behavior) and from `deliverable_tool` (which reads deliverable content, not event streams around them).

## Covered actions

- `events_summary` — **in scope this ship** — default action; returns total event count + `by_type` + `by_source` breakdowns over a `days`-window (default 7). Pure aggregate over `DeliverableEvent.objects.filter(created_at__gte=since)`.
- `atr_dashboard` — **in scope this ship** — reuses `core.views_deliverables.stage3_dashboard` via `RequestFactory` + `AnonymousUser`. Returns the `dashboard` payload from that view. Note: `AnonymousUser` bypasses per-user filtering — this is a global dashboard, not user-scoped.
- `events_query` — **in scope this ship** — flexible query with `event_type` + `deliverable_id` filters, capped at `limit=200` (default 50). Returns event rows with metadata + optional resolved `deliverable_title` via `select_related`.

Default action = `events_summary` (per `payload.get('action', 'events_summary')` at handler line 649).

## 3. Schema notes

- **Required:** `action` (enum: `events_summary` / `atr_dashboard` / `events_query`).
- **Optional:** `days` (int; default 7 for `events_summary`+`events_query`), `event_type` (string filter — `events_query` only), `deliverable_id` (UUID string — `events_query` only), `limit` (int; default 50, hard cap 200 via `min(payload.get('limit', 50), 200)` at handler line 688).
- **Schema-drift observation (documented, not defect):** Schema declares a `role` parameter (`"Filter by role tag (manager, recruiter, developer)"`) but the handler ignores it — no `role` filter is applied in `events_query`, `events_summary`, or `atr_dashboard`. Passing `role` silently no-ops. Not fixed this ship (doc-only sweep); flagged for post-D6 evaluation as a schema↔handler drift candidate (2nd instance after S2911 `reasoning_engine` drift-fix).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4456-4481`.

## 4. Golden-path examples

**Example 1 — quick pilot-metric check (default):**
```json
{"action": "events_summary", "days": 7}
```
Expected envelope: `{"action": "events_summary", "days": 7, "total_events": <int>, "by_type": [...], "by_source": [...]}`.

**Example 2 — full ATR dashboard:**
```json
{"action": "atr_dashboard"}
```
Expected envelope: `{"action": "atr_dashboard", <...stage3_dashboard fields...>}`. The `dashboard` dict from `stage3_dashboard` is spread onto the response.

**Example 3 — events for a specific deliverable:**
```json
{"action": "events_query", "deliverable_id": "<UUID>", "limit": 25}
```
Expected envelope: `{"action": "events_query", "count": <int>, "events": [{id, event_type, deliverable_id, deliverable_title, source, created_at, metadata}, ...]}`.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": "Unknown analytics_tool action: <action>"}` at handler line 716. Not raised — surfaced in-envelope.
- **Handler exception:** any exception is caught at line 718 and returns `{"error": "analytics_tool error: <str>"}`. No traceback surfaced; no `error_code` field (this tool predates the S2874 structured-error envelope — legacy-error envelope pattern, 5th instance corroborating post-S2917 4× count).
- **Empty window:** `events_summary` returns `total_events: 0` + empty `by_type` / `by_source` lists. No error.
- **No pagination cursor:** `events_query` is offset-free — pass a larger `limit` (up to 200) or narrow `event_type` / `deliverable_id` to shrink the window. There is no continuation token.
- **Non-existent `deliverable_id` in `events_query`:** returns `count: 0` + empty events list (not an error). `deliverable_title` is `None` for events whose deliverable was hard-deleted.
- **`atr_dashboard` under-the-hood failure:** wrapped in the handler `try`; if `stage3_dashboard` raises, the surface is the same legacy-error envelope.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `DeliverableEvent.objects.filter(...)` | `read` | `td_handlers_gateway.py:658,691` | ORM SELECT; documented behavior |
| `Deliverable` (via `select_related`) | `read` | `td_handlers_gateway.py:712` | ORM JOIN; documented |
| `core.views_deliverables.stage3_dashboard` | `read` | `td_handlers_gateway.py:673-683` | View function reused via `RequestFactory` + `AnonymousUser`; returns aggregate — no write side-effect observed. Full audit of `stage3_dashboard` internals out of scope this ship (documented-not-verified); watch for hidden LLM/network per S2914 Ledger candidate "hidden network/LLM in read-shaped gateway" (this would be 3rd instance if hit — currently 2/3). |

**Appendix N (Network-Preflight) — N/A.** No `httpx` / `requests` / `urllib.request` / socket first-hop in handler.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` / Celery task first-hop in handler.

Both Appendices declared N/A per S2918 T0 SIGN Q2 DISAGREE verdict (Rigby grep of `td_handlers_gateway.py` returned 0/17 gateway tools with these literals). Gateway is ORM-direct / view-reuse shape, not first-hop-heavy.

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification appended to the S2918 handoff. Expected shape for `events_summary`: envelope keys `{action, days, total_events, by_type, by_source}` with `by_type[*]` = `{event_type, count}`, `by_source[*]` = `{source, count}`.

## Related

- **Adjacent tools:** `audit_tool` (quality signals over `AuditFinding` / `WiringDefect` / `CitationViolation`) — same slice batch; `deliverable_tool` (content, not events); `metrics_tool` (system-level ops metrics, not deliverable events).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1).
- **Prior ratifications:** S2892 Path B open (PA tools sweep), S2917 Slice 3 CLOSE (22/22).
- **Ledger rows relevant to this ship:**
  - Legacy-error envelope 5th corroborating instance (4-instance pattern from S2916/S2917 + this).
  - Schema-drift-fix candidate 2nd instance (`role` param declared but ignored — S2911 was 1st).
  - "Hidden network/LLM in read-shaped gateway" watch — `stage3_dashboard` reuse is documented-not-verified; if audit surfaces LLM/network, this is 3rd instance (2/3 currently after S2913 `conversation_tool.search` + S2914 `intelligence_tool.search`).
