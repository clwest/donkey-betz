# Session 2860 — `deliverable_tool.delete` Exposed + Hardened (Ledger #10) Shipped

**Date:** 2026-07-20
**HEAD at close:** `00dfdaaed`
**PR:** [#3339](https://github.com/clwest/donkey-betz-platform/pull/3339)
**Prior session:** [SESSION_2859](SESSION_2859_DELIVERABLE_TOOL_GOTCHAS_LEDGER_8_9_SHIPPED.md)
**Session pin retired at close:** `pa-3da32ce5d13a4095`

---

## TL;DR

Shipped the Chris-selected S2860 slate #1 (Rigby Tool Gap Ledger entry #10) as **one PR / one commit**. The `delete` handler at `td_handlers_agents.py:2573` had existed since Session 1169 (hard `obj.delete()`) but was never in the `deliverable_tool` schema enum, so GPT-5.2 function calling had no valid path to it. Rigby fell back to `content_tool.content_reject` (soft-archive) when she wanted genuine hard-delete cleanup, surfaced at S2859 post-merge E2E as Ledger candidate #10.

**Fix was smaller than "build new action" — expose existing + harden.** Ships:

1. **Schema** — add `"delete"` to `deliverable_tool.action` enum + `allow_published` param.
2. **Handler hardening** — two-factor gate (`require_write_authorization` pattern from `bulk_archive`) + `status='published'` guard + pre-delete `logger.warning()` audit line + cascade counts surfaced in dry-run preview and live response.
3. **13 new pytest cases** covering two-factor gate, cascade counts, published guard (4 sub-cases), audit log line, dry-run does-not-emit-audit.
4. **1 pre-existing test** updated to pass `dry_run=False + confirm=True` (semantic preserved).

**126 tests green** across the broader deliverable-tool test surface. Post-recycle Rigby E2E validated all 4 steps end-to-end on the Donkey Betz workspace.

---

## Why this slate

Ledger #10 came from the S2859 post-merge E2E when Rigby had to fall back to `content_tool.content_reject` to clean up a smoke row because there was no valid `deliverable_tool.delete` call from her tool surface. Per `feedback_rigby_tool_gap_ledger`, Rigby's `deliverable_tool` IS the A1 SaaS product surface + A4 consulting demo substrate — every gap Rigby hits, a customer hits.

Chris pre-selected at S2860 open. Investigation at session open surfaced the true root cause (handler exists, schema enum omits `"delete"`), turning "build new action" into "expose existing + harden."

---

## What shipped

### 1. Schema exposure (`core/services/pa_tool_schemas.py`)

- Added `"delete"` to the `deliverable_tool.action` enum at line 3913, positioned before `"link_initiative"`.
- Enum docstring for `"delete"` warns IRREVERSIBLE + cascade to `DeliverableExport` / `DeliverableEvent` (audit trail erased) / `ContentPacketItem` (may break content packets); prefers `set_status='archived'` for reversible cleanup; documents the two-factor gate + `allow_published` escape hatch.
- Added `allow_published` boolean param (escape hatch for `status='published'` rows; additionally requires non-empty `reason`).
- Updated `confirm` param docstring to note S2860 extended the gate to single-row delete.

### 2. Handler hardening (`core/services/td_handlers_agents.py:2573`)

Replaced the 15-line unguarded `obj.delete()` branch with a 116-line hardened path:

```python
# S2860 Ledger #10 — schema exposure + hardening
from core.services.td_autofill_safety import require_write_authorization
dry_run, _write_ok = require_write_authorization(payload)

obj, disambiguation = _resolve_deliverable(_id_lookup_qs(), payload, 'delete')
if disambiguation:
    return disambiguation

cascades = {
    'exports_count': obj.exports.count(),
    'events_count': obj.events.count(),
    'packet_items_count': obj.packet_items.count(),
}

raw_reason = payload.get('reason')
reason = raw_reason.strip() if isinstance(raw_reason, str) else ''
allow_published = payload.get('allow_published') is True

# Published guard — reject by default; allow_published=true + reason is the
# explicit escape hatch (defence against LLM autofilling allow_published=True
# blindly on a published row).
if obj.status == 'published':
    if not allow_published:
        return {..., 'error_code': 'delete_published_requires_allow_published', ...}
    if not reason:
        return {..., 'error_code': 'delete_published_requires_reason', ...}

# Dry-run preview + live path with pre-delete logger.warning audit line
```

Key hardening choices:

- **Two-factor gate** via `require_write_authorization` (identical to `bulk_archive` at `td_handlers_content.py:4805`). `dry_run` defaults True; writes require `dry_run=false + confirm=true`. Autofill-defence: GPT-5.2 autofills declared optional booleans with Python `False`; the confirm second-factor catches this.
- **Cascade counts** computed via reverse relations: `obj.exports` (`related_name='exports'`), `obj.events` (`related_name='events'`), `obj.packet_items` (`related_name='packet_items'`). Surfaced in BOTH dry-run preview and live response so callers see the blast radius before and after.
- **Published guard** with two typed error codes (`delete_published_requires_allow_published` / `delete_published_requires_reason`). `.strip()` defence against whitespace-only reason.
- **Audit trail via pre-delete `logger.warning('[DELIVERABLE_DELETE]')`** with `deliverable_id / title / status / workspace_id / agent_name / user_id / trace_id / reason / cascades`. `DeliverableEvent` CASCADEs on `obj.delete()` (`core/models_deliverables.py:584-588`), so it cannot be relied on for post-delete audit — logs are the durable trail.

### 3. Tests (`core/tests/test_deliverable_tool_delete.py`)

13 new pytest cases in a dedicated file:

| Test | Purpose |
|---|---|
| `test_delete_defaults_to_dry_run_preview` | No `dry_run`/`confirm` → safe preview, row survives |
| `test_delete_dry_run_false_without_confirm_stays_preview` | `dry_run=False` alone → still preview (autofill defence) |
| `test_delete_confirm_true_without_dry_run_stays_preview` | `confirm=True` alone → still preview |
| `test_delete_dry_run_false_and_confirm_true_executes` | Both flags → row permanently deleted |
| `test_delete_dry_run_surfaces_cascade_counts` | Preview shows exports/events/packet_items counts |
| `test_delete_live_path_cascades_children` | `obj.delete()` cascades to all three child models |
| `test_delete_published_without_allow_returns_typed_error` | `published` rejected by default with `error_code` |
| `test_delete_published_with_allow_missing_reason_returns_typed_error` | `allow_published=True` still requires non-empty reason |
| `test_delete_published_with_allow_and_whitespace_reason_still_rejected` | `.strip()` defence works |
| `test_delete_published_with_allow_and_reason_executes` | Full escape hatch → row deleted |
| `test_delete_writes_audit_log_line_before_delete` | Live path emits `[DELIVERABLE_DELETE]` WARNING |
| `test_delete_dry_run_does_not_emit_audit_log` | Preview does NOT write audit line |

Plus 1 pre-existing test updated: `test_deliverable_orphan_mutations_symmetric.test_delete_finds_orphan_for_non_staff_owner` now passes `dry_run=False + confirm=True` to reflect the new gate. Semantic (orphan-lookup symmetry) preserved.

---

## Files touched

| File | Δ | Change |
|---|---|---|
| `core/services/pa_tool_schemas.py` | +6, -3 | add `"delete"` to enum + docstring; add `allow_published` param |
| `core/services/td_handlers_agents.py` | +115, -1 | replace 15-line delete branch with 116-line hardened path |
| `core/tests/test_deliverable_tool_delete.py` | +278 | 13 new pytest cases (new file) |
| `core/tests/test_deliverable_orphan_mutations_symmetric.py` | +4 | update existing delete test to pass gate |

**Net:** 399 insertions, 4 deletions across 4 files (1 new).

---

## Rigby SIGN loop

Two SIGN cycles, both grounded (no rubber-stamp per `feedback_verify_rigby_tool_runs_before_trusting_sign`).

### Pre-code SIGN + concurrence check

- 5 grounded `repo_tool.read_file` calls verifying all 4 pre-code claims (handler exists, schema omits, `bulk_archive` two-factor pattern, cascade FKs).
- Q1 AGREE-WITH-MODS: two-factor gate right, also block `status='published'` by default.
- Q2 AGREE-WITH-MODS: no archive prerequisite (breaks smoke workflow), but default-deny `published` unless explicit override.
- Q3 AGREE-WITH-MODS: `logger.warning` sufficient minimum; TODO for durable audit row (Ledger candidate).
- Q4 AGREE-WITH-MODS: `reason` optional in general, REQUIRED for higher-risk paths (published override).
- Q5 zoom-out AGREE-WITH-MODS: ship it with all hardening; flagged `ContentPacketItem` CASCADE = newsletter-artifact breakage risk (mitigated: `packet_items_count` surfaced in dry-run preview).

Concurrence check on v2 fold: **AGREE-TO-SHIP** on both deviations (packet_items reason-required deferred to future trigger; durable audit table deferred to Ledger #11). Two hardening emphases (both already in the plan): `require_write_authorization` non-negotiable; `.strip()` on reason.

### Post-code SIGN

- 6 grounded `repo_tool.read_file` calls covering schema + handler + both test files.
- All 5 F-BLOCKING questions AGREE-TO-SHIP.
- Non-blocking coupling risks flagged: (a) `packet_items` reverse relation validated by test; (b) logs-based audit → already recorded as Ledger #11.
- Verdict: "I'd sign this PR to merge after your recycle + E2E run."

Working loop pattern: `feedback_zoom_out_ask_per_rigby_sign` continues to catch substantive concerns (5 across pre-code SIGN, all folded).

---

## Post-merge E2E verify

Merged as `00dfdaaed`; `make celery-recycle` bounced all workers to HEAD-fresh state (pa worker pid_age 96s < commit time 4m ago; `started_before_head_commit=false`). Rigby executed the 4-step E2E on the Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`):

| Step | Action | Expected | Actual |
|---|---|---|---|
| 1 | `create` with title=`S2860_E2E_SMOKE_DELETE_20260720` | verbatim title (S2859 fix) | ✅ id `c695c040-2a1a-45ce-bc03-69b71c1b469c`, title unmodified |
| 2 | `delete` with no `dry_run`/`confirm` | dry_run=true + preview + row survives | ✅ dry_run=true, cascades={0 exports, 0 events, 0 packet_items}, will_delete=true, row still exists (detail fetch confirms) |
| 3 | `delete` with `dry_run=false + confirm=true` | live delete + response with cascades | ✅ dry_run=false, message="Permanently deleted \"S2860_E2E_SMOKE_DELETE_20260720\" (0 exports, 2 events, 0 packet items cascaded)", trace_id present |
| 4 | Same delete call again on now-deleted id | not-found error | ✅ "Deliverable c695c040-... not found" |

Note step 3 events_count=2 vs step 2 events_count=0 — a `status_transition` signal wrote 2 events between the dry-run preview and live delete (system-driven, not test artifact). Behavior expected + within tolerance.

---

## New Ledger candidates surfaced at S2860

One future candidate for the Rigby Tool Gap Ledger:

1. **Ledger #11 — Durable non-cascading audit table for deletes**. Current v1 uses `logger.warning('[DELIVERABLE_DELETE]')` as the audit trail because `DeliverableEvent` CASCADEs with the row. Logging-only is adequate for a first ship but has failure modes: log retention gaps, harder forensic queries, dependency on log aggregation pipeline. A dedicated append-only DB table (e.g., `DeliverableDeleteAudit`) would give durable structured queries. Deferred; awaits either a compliance/audit trigger or a genuine forensic need.

No Playbook amendment triggered.

---

## What's forbidden at S2861 (D6 moratorium still in force)

- No new strategic discovery arcs. No new opportunity portfolio expansions. No new evaluation frameworks. No layer-boundary design arcs. No re-opening the D4 wedge frame or picks.

---

## Substrate story after S2860 close

Every workspace including A4 has:
- $5/day default cap; operator-configurable via `set_cap` (immediate enforcement per S2850 #3.0a) or `set_default_cap` + `backfill_defaults`
- Freeze @ 100% / downgrade @ 70% auto-enforcement with hysteresis
- Full audit trail — cycle vs operator vs simulated attribution
- Simulated enforcement (S2857) — operators verify enforcement path without touching real spend
- Post-clear `status_context` inline on clear_* responses (S2858 PR#1)
- `list_caps include_defaults=false` scales O(1) on workspace count (S2858 PR#2)
- Ratification records land with verbatim titles + no spurious diagnostic mark (S2859)
- **NEW at S2860:** Rigby can permanently delete deliverables directly via `deliverable_tool.delete` — two-factor gated, published-guarded, cascade-previewed, WARNING-audit-logged. No fallback to `content_tool.content_reject` for hard cleanup.

Fleet auditability, downgrade savings estimates, pricing catalog canonicalization, evidence surfacing on autopilot history all still in force from prior arcs.
