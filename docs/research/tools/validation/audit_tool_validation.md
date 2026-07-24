# `audit_tool` — Validation Report (S2918)

**Tool:** `audit_tool`
**Schema:** `core/services/pa_tool_schemas.py:4901`
**Handler:** `core/services/td_handlers_gateway.py:2128` (`_handle_audit`)
**Register site:** `core/services/tool_dispatcher.py:586`
**Session:** S2918 (Slice 4 batch 1 — gateway small-tier mixed pilot: analytics + audit + campaign + experiment)
**HEAD at validation:** `e1a09d8d0` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2918 T0 SIGN AGREE-with-edits — mixed-pilot batch composition ratified with 20+ `repo_tool` receipts; Appendix A/N declared N/A for gateway (0/17 first-hop literals in `td_handlers_gateway.py`).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`audit_tool` surfaces quality-signal rows from three tables: `AuditFinding` (S2xxx-tracked findings with priority + status + assignment), `WiringDefect` (agent/object wiring gaps from the orchestration audit framework), and `CitationViolation` (agent responses that skipped required citations). Use it when the operator asks "what P0s are open?" / "which agents have wiring defects?" / "did anyone violate citation policy today?".

Distinct from `analytics_tool` (event-stream aggregates, not quality flags), from `deliverable_tool` (content search, not audit rows), and from `metrics_tool` (system ops metrics, not audit findings).

## Covered actions

- `findings` — **in scope this ship** — default action; lists `AuditFinding` rows ordered by `-created_at`. Supports `priority` + `status` filters. Truncates to `limit` (default 20, hard cap 50).
- `p0_summary` — **in scope this ship** — filters `AuditFinding` to `priority in [P0, P1]` and `status != resolved`. Same envelope as `findings`.
- `wiring_defects` — **in scope this ship** — lists `WiringDefect` rows. Supports `status=resolved|unresolved` filter (mapped internally to `is_resolved` boolean).
- `citations` — **in scope this ship** — lists `CitationViolation` rows. No secondary filter beyond `limit`.

Default action = `findings` (per `payload.get('action', 'findings')` at handler line 2130).

## 3. Schema notes

- **Required:** `action` (enum: `findings` / `wiring_defects` / `citations` / `p0_summary`).
- **Optional:** `priority` (string — only applied on `findings` action, not `p0_summary` which hard-codes `[P0, P1]`), `status` (string — behavior differs per action: `findings` filters `AuditFinding.status`; `wiring_defects` maps `resolved`/`unresolved` to `is_resolved` boolean; `citations` ignores it), `limit` (int; default 20, hard cap 50 via `min(int(payload.get('limit', 20)), 50)` at handler line 2131).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4899-4926`.
- **Envelope shape asymmetry:** `findings` and `p0_summary` return `{action, count, findings: [...]}` (key `findings`); `wiring_defects` returns `{action, count, defects: [...]}` (key `defects`); `citations` returns `{action, count, violations: [...]}` (key `violations`). Operator or downstream consumer must key-switch on action. Not a defect per se — matches the model naming — but a discoverability sharp edge.

## 4. Golden-path examples

**Example 1 — quick P0/P1 check (most operator-common):**
```json
{"action": "p0_summary"}
```
Expected envelope: `{"action": "p0_summary", "count": <int ≤ 50>, "findings": [{id, finding_id, title, priority, category, status, impact, assigned_agent}, ...]}`.

**Example 2 — findings by priority + status filter:**
```json
{"action": "findings", "priority": "P0", "status": "open", "limit": 10}
```
Expected envelope: same shape as example 1, filtered.

**Example 3 — unresolved wiring defects:**
```json
{"action": "wiring_defects", "status": "unresolved", "limit": 25}
```
Expected envelope: `{"action": "wiring_defects", "count": <int ≤ 50>, "defects": [{id, defect_type, agent_name, object_type, is_resolved, created_at}, ...]}`.

**Example 4 — recent citation violations:**
```json
{"action": "citations", "limit": 15}
```
Expected envelope: `{"action": "citations", "count": <int ≤ 50>, "violations": [{id, violation_type, agent_name, provided_sources, required_sources, was_blocked, is_resolved, created_at}, ...]}`.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": "Unknown audit_tool action: <action>"}` at handler line 2203. Not raised — in-envelope.
- **Handler exception:** any exception is caught at line 2205, logged via `logger.error(..., exc_info=True)` (BRAIN log stream), and returns `{"error": <str>}`. No `error_code` field — legacy-error envelope (6th instance corroborating post-S2917 4× pattern).
- **Empty result set:** returns `count: 0` + empty list under the action-specific key. No error.
- **`impact` truncation:** `findings`/`p0_summary` truncate `f.impact` to 200 chars via `(f.impact or '')[:200]`. Full impact requires direct ORM read (not exposed via this tool).
- **`limit` hard cap:** 50 (below-default of 20 is common). No pagination cursor; increase `limit` or narrow filters to shrink window.
- **`status` on `citations` action:** silently no-ops (the handler doesn't read `status` in the citations branch). Not raised — consumers who expect filtering get a full-window result.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `AuditFinding.objects.order_by(...)` + `.filter(...)` | `read` | `td_handlers_gateway.py:2136-2146` | ORM SELECT; documented |
| `WiringDefect.objects.order_by(...)` + `.filter(...)` | `read` | `td_handlers_gateway.py:2164-2170` | ORM SELECT; documented |
| `CitationViolation.objects.order_by(...)` | `read` | `td_handlers_gateway.py:2186-2187` | ORM SELECT; documented |

**Appendix N (Network-Preflight) — N/A.** No network first-hop.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop.

Both Appendices declared N/A per S2918 T0 SIGN Q2 DISAGREE verdict (Rigby grep of `td_handlers_gateway.py` returned 0/17 gateway tools with these literals). Gateway is ORM-direct shape.

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification appended to the S2918 handoff. Expected shapes documented in §4 golden-path examples.

## Related

- **Adjacent tools:** `analytics_tool` (behavioral events, not quality signals) — same slice batch; `deliverable_tool` (content, not findings); `observability_tool` / `metrics_tool` (ops, not audit).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1); models at `core/models_audit_tracking.py` (`AuditFinding`) + `core/models_orchestration.py` (`WiringDefect`, `CitationViolation`).
- **Prior ratifications:** S2892 Path B open, S2917 Slice 3 CLOSE (22/22).
- **Ledger rows relevant to this ship:**
  - Legacy-error envelope 6th corroborating instance (4-instance pattern from S2916/S2917 + analytics + this).
  - Envelope-key asymmetry across actions (`findings` / `defects` / `violations`) — not a defect, but a candidate for future harness-lint "consistent-list-key across actions" if 2nd instance surfaces.
  - Silent `status` ignore on `citations` action — schema-drift candidate (3rd instance if promoted; 2nd instance was analytics_tool `role`).
