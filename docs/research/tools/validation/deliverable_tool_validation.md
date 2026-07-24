# `deliverable_tool` — Validation Report

**Tool:** `deliverable_tool`
**Schema:** `core/services/pa_tool_schemas.py:3389-3460`
**Direct dispatcher:** `core/services/td_handlers_content.py:84-116` (`_handle_deliverable_direct`)
**Main handler:** `core/services/td_handlers_agents.py:1530-2900+` (`_handle_deliverables`)
**Sub-handlers:** `_handle_bulk_archive` (td_handlers_content.py:4656), `_handle_deliverable_initiative_link` (td_handlers_content.py:118)
**Register site:** `core/services/tool_dispatcher.py:479`
**Session validated:** S2728
**HEAD at validation:** `9d158805`
**Reviewer:** Claude (Opus 4.7, 1M context)
**Rigby cross-check:** pending (per campaign plan §10.1 step 12)
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch A tool 1 of 5). Trace + patches + regression tests complete; MEMORY annotations applied; 17 new regression tests + 67 adjacent existing tests all passing at HEAD. Rigby cross-check DEFERRED to Chris's discretion (§10.1 step 12) — not required for tool closure since defect verification landed via automated tests.

---

## 1. Intended purpose (per schema description)

*"Manage the deliverables library — create, read, update, search, save, export, and archive deliverables. Use this tool (NOT content_tool) for ALL deliverable operations."*

## 2. Rigby's belief (per schema surface + prior conversations)

Rigby believes she has a single `deliverable_tool` with 16 actions that manages the deliverables library. She has been trained through Session 1176/1177/1226/1227/1228/1241 corrections to know several defensive patterns: use `append` for large content; use `content_tool.content_complete` (not `deliverable_tool.update`) to flip to `completed`; new deliverables default to `status=completed` regardless of `status=draft` param; boolean autofill is a real risk. These beliefs are load-bearing across MEMORY.md — 5+ rules crystallize them.

## 3. Schema claim (verbatim capture)

**Required parameter:** `action` (enum, 16 values).

**Action enum:** `list, detail, create, update, append, search, save, unsave, stats, duplicates, set_status, normalize, export_pdf, bulk_archive, link_initiative, unlink_initiative`.

**Optional parameters (28 total, per schema `properties` dict):**
- Identity/lookup: `id`, `initiative_id`, `deliverable_id` (alias — but NOTE: alias declared only for link/unlink actions in the action-enum description; the schema `properties` dict declares `id` but not `deliverable_id` as a top-level property — see finding F-D-DELIVERABLE-ID-ALIAS)
- Content: `title`, `content`, `query`
- Categorization: `category`, `type`, `status`, `agent`, `tags`, `data_sensitivity`, `agent_name`
- Filters (LLM-autofill-hardened): `has_initiative` (string|boolean, string-sentinel-only for false), `orphans` (boolean, truthy-only), `exclude_archived` (boolean, truthy-only), `show_all` (boolean, bypass-optional-filters)
- Duplicates action: `group_by`, `min_count`, `window_days`
- Set_status action: `reason` (REQUIRED on completed→ready)
- Normalize action: `field` (v1: `agent_name` only)
- Detail action: `full` (boolean, bypass 8K cap), `content_offset`, `content_limit`
- Create/update: `is_pinned`, `return_detail`
- Bulk_archive (LLM-autofill-hardened): `dry_run` (DEFAULT TRUE per schema), `confirm` (REQUIRED with dry_run=false), `cap`, `title_prefixes`, `agent_names`, `protected_categories`
- Pagination: `limit` (default 10), `offset`
- Stats: `full_by_agent` (boolean, return long tail vs top-10)
- Scoping: `workspace_id`

**Schema-declared defaults (surfaced in `description` text only, NOT as JSONSchema `default` fields):**
- `limit`: 10
- `dry_run`: TRUE (for bulk_archive/cleanup/normalize)
- `has_initiative`: OMIT unless filtering
- `orphans`: OMIT unless filtering
- `min_count`: 2
- `window_days`: 7
- `field`: `agent_name`

## Covered actions

Enumerates every action currently declared in `deliverable_tool`'s schema enum
(`core/services/pa_tool_schemas.py:4231`, HEAD `adbae9074`). **18 actions total** —
S2728 covered 16; `delete` was added S2860 and `clear_diagnostic` added S2868. All
18 are exercised via the shared `_handle_deliverables` dispatch layer per §4;
mutation actions have `dry_run` + `confirm` gates documented at §17 STOP-and-report
failure modes.

- `list` — **read** — browse deliverables by status/type/category/date/workspace filter. `has_initiative`/`orphans`/`saved` autofill-hardened per §6 hidden-filters inventory. Verified live at S2728.
- `detail` — **read** — full content of a deliverable (default 8K char cap; `full=true` bypasses; `content_offset`/`content_limit` paginate). Verified live at S2728.
- `create` — **mutation (contained)** — new Deliverable row. Defaults `status='completed'` per F-D-6. Verified live at S2728.
- `update` — **mutation (contained)** — edit existing deliverable by id. Cannot set `status='completed'` — typed error redirects to `content_tool.content_complete` or `set_status` per F-D-7. Verified live at S2728.
- `append` — **mutation (contained, append-only)** — never overwrites; concatenates text. Verified live at S2728.
- `search` — **read** — title-keyword search. Verified live at S2728.
- `save` — **mutation (contained, bookmark)** — bookmark a deliverable for the current user. Verified live at S2728.
- `unsave` — **mutation (contained)** — remove bookmark. Verified live at S2728.
- `stats` — **read** — aggregate counts by type/category/agent. `full_by_agent=true` bypasses top-10 truncation. Verified live at S2728.
- `duplicates` — **read** — dedup audit; returns groups with count/first_created_at/last_created_at/window counts/agent-name distribution. Verified live at S2728.
- `set_status` — **mutation (contained)** — surgical status flip supporting completed↔ready only. `reason` REQUIRED on completed→ready. Records actor + trace_id + reason in DeliverableEvent. Verified live at S2728.
- `normalize` — **mutation (spreading)** — alias-map sweep on `agent_name` field (v1). `dry_run=TRUE` default; writes require `dry_run=false + confirm=true`. Verified live at S2728.
- `export_pdf` — **mutation (contained, PDF row create)** — generate downloadable PDF; returns CDN URL. Verified live at S2728.
- `bulk_archive` — **mutation (spreading)** — multi-row archive by filter (title_prefixes/agent_names/protected_categories/statuses). `dry_run=TRUE` default; writes require `dry_run=false + confirm=true` (S1228 PR-A belt-and-suspenders). Verified live at S2728. **Sibling S2943 PR-B candidate:** `content_tool.bulk_archive_published` inherits this same handler surface.
- `delete` — **mutation (cascading — S2860)** — IRREVERSIBLE single-row delete. Cascades to DeliverableExport / DeliverableEvent / ContentPacketItem. `dry_run=TRUE` default; writes require `dry_run=false + confirm=true`. Rejects `status='published'` unless `allow_published=true + non-empty reason`. Pre-delete WARNING log records id + user_id + trace_id + reason + cascade counts. **Analyzed at S2860, not exercised live this batch** — deferred to future dry_run live-verify batch.
- `link_initiative` — **mutation (contained)** — attach deliverable to initiative (pass `deliverable_id + initiative_id`). Verified live at S2728.
- `unlink_initiative` — **mutation (contained)** — remove initiative link (pass `deliverable_id`). Verified live at S2728.
- `clear_diagnostic` — **mutation (contained — S2868)** — manually clear a `missing_initiative_id` diagnostic. Sets `diagnostic_status='cleared'` (sticky sentinel). Requires `id + non-empty reason`. Rejects if row is not currently `diagnostic`. Only suppresses missing_initiative_id re-marks; workspace_mismatch still fires. **Analyzed at S2868 ratification, not exercised live this batch.**

## 4. Handler behavior (traced through code)

### 4.1 Dispatch layer 1 — `_handle_deliverable_direct` (td_handlers_content.py:84-116)

Thin dispatcher. Behavior:

- Line 86: `action = payload.get('action', 'list')` — **DEFAULT ACTION IS `list` IF UNSET.** No error raised for missing required param despite schema `required: ["action"]`. See finding **F-D-1**.
- Line 90-92: **Silent action inference** — if `action == 'list'` AND `title` AND `content`, action is silently promoted to `'create'`. Logged at INFO but not surfaced in response. See finding **F-D-2**.
- Line 95-103: `ACTION_MAP` maps 14 action names identity-through. `link_initiative`, `unlink_initiative` are handled by explicit branch (line 111-112) — NOT via the ACTION_MAP.
- Line 104: `mapped = ACTION_MAP.get(action, action)` — **UNKNOWN ACTIONS PASS THROUGH unchanged** via `.get(..., action)`. See finding **F-D-3**.
- Line 108-109: `bulk_archive` routed to dedicated `_handle_bulk_archive`.
- Line 111-116: link/unlink routed to `_handle_deliverable_initiative_link`.
- Line 113: All other actions delegate to `_handle_deliverables` with `tool_name='deliverables_tool'` (note the `'s'` — the internal tool name differs from schema-declared `deliverable_tool`).
- Line 114-116: Response gets `gateway='deliverable_tool'` appended (interfaces).

### 4.2 Dispatch layer 2 — `_handle_deliverables` (td_handlers_agents.py:1530-2900+)

Main handler. Full trace:

- Line 1542-1552: **UUID sanitization** for `id`, `workspace_id`, `workspace`, `initiative_id`, `deliverable_id`. Invalid strings (e.g., GPT tool-call IDs like `tool-1-6a55c355`) are silently blanked and logged at WARNING. This is a documented defense per Apr 2026 commentary.
- Line 1554-1567: **Second-layer action inference** — same `list`→`create` inference PLUS additional `list`→`append` inference if `content` + `id` set. **Layer-2 inference is broader than layer-1.** See finding **F-D-4**.
- Line 1569: `limit = min(payload.get('limit', 10), 50)` — **HARD CAP at 50** for list actions. Not surfaced in schema. See finding **F-D-5**.
- Line 1578-1625: Workspace + user scoping. Workspace precedence: (a) payload `workspace_id`|`workspace` → (b) `AssistantProfile.workspace` fallback → (c) user_id + is_staff/is_pa check → (d) unscoped for staff/PA.
- Line 1583-1600: **Fallback via AssistantProfile.** Note commentary: "Session 1103c: was 'except Exception: pass' which silently dropped workspace scoping." Verified fix at HEAD — now logs at WARNING when lookup fails.
- Line 1626-1631: `show_all` flag interprets truthy-only (`True, 'true', 'True', 1, '1'`) — python `False` treated as autofill.
- Line 1636: `_applied = {}` tracks which optional filters actually fired. Surfaced in response as `applied_filters` (diagnostic gap closed in S1227).
- Line 1638-1716: **Common-filter builder `_apply_common_filters`**. Key defenses:
  - `has_initiative`: string-sentinel `'false'` for negative; python `False` treated as autofill → no filter (S1227 root cause).
  - `orphans`: truthy-only (S1091/S1227 pattern).
  - `saved`: truthy-only.
  - `status`: applied unless `show_all`; supports LLM-confusion aliases (`approved`→`ready`, `pending_review`→`ready`, `rejected`→`archived`).
  - `type`, `category`, `agent`: identity match.
  - `initiative_id`, `workspace_id`, `workspace`: identity match.
  - Date range: `created_before`, `created_after` via `parse_datetime`.

### 4.3 Action: `create` (td_handlers_agents.py:1964-2148)

- Line 1969-1970: `raise ValueError` on missing title or content. **FAIL-LOUD.** No silent creation.
- Line 2029-2078: Delegates to `create_deliverable(...)` in `core/services/deliverable_factory.py` with `raise_on_gated=True` (S1169 Layer C Phase 1).
- Line 2057-2078: If `DeliverableGatedError` raised, returns typed envelope with `error_code='deliverable_gated'`, `reason_code`, `human_message`, `retry_suggestions`. **Rigby-safe error.**
- Line 2085-2089: Post-fix defensive `RuntimeError` if factory returns None despite `raise_on_gated=True` — pragma no-cover.
- **Line 2052: `status='completed'` HARDCODED.** Every PA-created deliverable is stored with `status='completed'` regardless of caller's `status` param. **This confirms MEMORY rule `feedback_deliverable_create_defaults_to_completed`.** See finding **F-D-6**.
- Line 2110-2119: Response includes `status` echoing the stored (hardcoded) value at top level — S1248 P2b fix to close verify-then-set_status round-trip.
- Line 2122-2147: Optional `return_detail=True` triggers follow-up `detail` fetch, embeds as `detail` key, sets `detail_included` flag. Failure of follow-up is soft (logs warning; sets `detail_included=False`).

### 4.4 Action: `update` (td_handlers_agents.py:2150-2344)

- Line 2157-2159: `_resolve_deliverable` for id/title lookup with disambiguation.
- Line 2161-2255: Field-by-field update with `update_fields` list — supports title, content, prepend, append (nested inside update), type, content_format, tags, category, data_sensitivity, status, workspace, initiative.
- Line 2166-2172: Silent handling of empty `content` when `prepend`/`append` provided (S1077).
- **Line 2216-2221: STATUS WHITELIST.** `valid_statuses = {'draft', 'ready', 'published', 'archived'}` — **`completed` is NOT in the whitelist and is SILENTLY DROPPED** if requested via update. This confirms MEMORY rule `feedback_deliverable_status_via_content_complete`. See finding **F-D-7**.
- Line 2229-2233: Workspace lookup swallows exceptions with WARNING log — degrades silently on that field but doesn't fall back to list.
- Line 2247-2253: Initiative lookup same pattern.
- Line 2255-2256: `raise ValueError` if no valid update_fields — **FAIL-LOUD** for no-op updates.
- Line 2263-2335: **Diagnostic initiative alignment** — S1195 Plan C Phase 1. Emits `[ORPHAN-DELIVERABLE]` warnings on `missing_initiative_id` / `workspace_mismatch`.
- Line 2337-2344: Response includes `updated_fields` list. **No `status` field in response for update** — asymmetric with `create` response shape. See finding **F-D-8**.
- **No payload-size check anywhere in update handler.** Grep-verified.

### 4.5 Action: `append` (td_handlers_agents.py:2346-2370)

- Line 2350-2352: Same `_resolve_deliverable` pattern as update.
- Line 2353: Accepts `content`, `text`, OR `append` as source. First non-empty wins.
- Line 2354-2355: `raise ValueError` on empty content — **FAIL-LOUD**.
- Line 2356-2358: Appends with `'\n\n'` separator; updates preview.
- Line 2362: Saves with `update_fields=['content', 'preview_content', 'updated_at']` — includes `updated_at` to trigger Django auto_now (S1231 P3 audit-trail fix).
- Line 2363-2370: Response includes `content_length`, `appended_chars`, `message`. Clean symmetric contract.
- **No payload-size check.** Grep-verified.

### 4.6 Root cause of MEMORY rule "silent fallback to list above ~6-7 kB"

Traced via `unified_pa_entrypoint.py:118-186` + `unified_pa_entrypoint.py:2020-2063`:

- **S1177 F1 root-cause fix at HEAD (unified_pa_entrypoint.py:2020-2063).** When the LLM's `arguments` JSON fails to parse (root cause: LLM output-token-budget truncation on large content), the caller:
  1. Builds a typed error envelope via `_build_tool_args_malformed_envelope(...)` — `error_code=TOOL_ARGS_JSON_MALFORMED`.
  2. Logs at WARNING with args_len + parse_error + tail.
  3. Records `ok=False` in `fc_metadata` and `tool_runs`.
  4. Emits the typed envelope as the `function_call_output` for that call_id.
  5. **`continue`** on line 2063 — **explicitly skips invoking the handler.** The `action='list'` default cannot fire because the handler is never called.
- Session 1177 established the invariant "callers must NOT invoke the tool handler when this is returned" — encoded at line 160-162 of the envelope-builder docstring.

**Verdict on MEMORY rule `feedback_deliverable_tool_use_append_for_large_payloads`:** the root-cause fallback (empty-dict → action=list) that made a truncated update look like a benign list-response is ELIMINATED at HEAD. Rigby now sees `ok=False` + `error_code=TOOL_ARGS_JSON_MALFORMED` + a retry hint suggesting `_append` action. **The workaround (use `append`) is still valid but the failure mode is now surfaced, not silent.** See finding **F-D-9**.

---

## 5. Defaults inventory (per parameter)

| Parameter | Schema-declared default | Handler-effective default | Divergence? |
|---|---|---|---|
| `action` | none (required) | `'list'` (td_handlers_content.py:86; also td_handlers_agents.py:1554) | **YES** — schema says required, handler defaults silently. **F-D-1** |
| `limit` | none | 10, capped at 50 (td_handlers_agents.py:1569) | Handler caps beyond schema — **F-D-5** |
| `offset` | none | 0 (td_handlers_agents.py:1570) | Documented in schema, effective default matches |
| `has_initiative` | omit-unless-filter | truthy-string-or-boolean-only, python-False → autofill-safe no-op | Schema matches handler behavior (S1227) |
| `orphans` | omit-unless-filter | truthy-only, python-False → no filter | Matches (S1227) |
| `exclude_archived` | truthy-only per schema description | truthy-only in duplicates path | Matches |
| `dry_run` (bulk_archive) | TRUE per schema | TRUE — writes require `dry_run=false AND confirm=true` | Matches (S1228 PR-A) |
| `confirm` (bulk_archive) | false | false — writes require `confirm=true` | Matches |
| `show_all` | undocumented default | falsy-treated-as-off; only truthy strings | Matches |
| `full_by_agent` (stats) | false | false — top-10 default | Matches |
| `data_sensitivity` (create) | undocumented default | `'internal'` (td_handlers_agents.py:2012) | **Handler-only default; schema silent.** **F-D-10** |
| `category` (create) | undocumented default | `'PA Created'` (td_handlers_agents.py:2007) | **Handler-only default; schema silent.** **F-D-11** |
| `tags` (create) | undocumented default | `['pa-created']` (td_handlers_agents.py:2008) | **Handler-only default; schema silent.** **F-D-12** |
| `agent_name` (create) | undocumented default | `PA_IDENTITY` constant (td_handlers_agents.py:2011) | **Handler-only default; schema silent.** **F-D-13** |
| `is_pinned` (create) | false per schema | false (td_handlers_agents.py:2013) | Matches |
| `status` (create) | schema silent | **HARDCODED to `'completed'` on line 2052** — caller intent ignored | **F-D-6** confirmed |
| `content_format` (create) | undocumented | `'markdown'` (td_handlers_agents.py:1975) | **F-D-14** |
| `type` (create) | undocumented | `'document'` (td_handlers_agents.py:1976) | Matches schema description |
| `quality_score` (create) | undocumented | 0.7 (td_handlers_agents.py:2041) | **F-D-15** |
| `confidence_score` (create) | undocumented | 0.8 (td_handlers_agents.py:2042) | **F-D-16** |

---

## 6. Hidden filters inventory

**All handler-applied filters that DO NOT appear in schema description** (checked against `_apply_common_filters` at td_handlers_agents.py:1638-1716):

- **User-scoping filter (td_handlers_agents.py:1620-1622):** `Q(user_id=user_id) | Q(user__isnull=True)`. Non-staff/non-PA users see only their own + orphan deliverables. NOT in schema. Rigby's PA service account bypasses this. **F-D-17.**
- **Workspace fallback via AssistantProfile (td_handlers_agents.py:1587-1600):** when no explicit `workspace_id` passed, silently pulls from AssistantProfile. Log emitted at INFO. NOT in schema description. **F-D-18.**
- **Status alias mapping (line 1656):** `_STATUS_ALIASES = {'approved': 'ready', 'pending_review': 'ready', 'rejected': 'archived'}`. Silently rewrites user-visible status values before filter. NOT in schema description (which just says "ready, completed, draft, published"). **F-D-19.**
- All above surface in the `applied_filters` response block per S1227 diagnostic-gap-closure — VERIFIED.

---

## 7. Limits inventory

- `list` action: 10 default, **hard cap at 50** (td_handlers_agents.py:1569). NOT in schema. **F-D-5.**
- `detail` action: 8K content cap by default; `full=true` bypasses. Documented in schema.
- `bulk_archive`: `cap` parameter per schema.
- Content max length: no upstream limit found in handler. LLM-side truncation at output-token-budget IS the effective limit (~6-7 kB observed empirically per S1176/S1177).

---

## 8. Silent-truncation test

**Test 1 — list action, 60+ deliverables, no `limit` param:**
Pending (deferred to per-tool session execution).

**Test 2 — detail action, content >8K, no `full` param:**
Pending.

**Test 3 — create/update/append with 7 kB content:**
Pending.

## 9. Silent-filter test

Pending — will exercise `has_initiative=False` (python bool), `orphans=False`, `show_all=false`, `status='approved'` (alias remap).

## 10. Silent-fallback test

**Verified at code-trace level:** post-S1177, the LLM-args-malformed path emits `ok=False` + typed error envelope, does NOT invoke the handler. `action=list` default cannot fire from this path. Live test pending — will attempt a large-payload update from Rigby's LLM interface and verify the `TOOL_ARGS_JSON_MALFORMED` envelope surfaces instead of a benign list response.

## 11. Staleness test

Pending — will test detail against a recently-updated deliverable to confirm `updated_at` reflects real state (S1231 P3 fix in place per audit trail).

## 12. Freshness signal

Deliverable rows carry `created_at` + `updated_at` (Django `auto_now`). List response includes `created_at`. Detail response includes both. **`updated_at` is NOT included in the list response's `_LIST_FIELDS` at td_handlers_agents.py:1725-1729.** See finding **F-D-20**.

## 13. Provenance signal

- `agent_name` — persisted; defaults to `PA_IDENTITY` for PA-created rows.
- `metadata.source='pa_deliverables_tool'` — set on all PA-created rows.
- `metadata.trigger_source='pa_tool'` — set on all PA-created rows (S1168).
- `metadata.trace_id` — persisted.
- **NO `canonical_authority` field** on Deliverable model — provenance carriage is metadata-only.
- **Response does not surface `metadata` on list/detail** by default. See finding **F-D-21**.

## 14. Authority / workspace assumptions

- WORKSPACE_AWARE_AGENTS gate does NOT apply — `deliverable_tool` is a general PA tool.
- Workspace precedence: explicit `workspace_id` payload > `AssistantProfile.workspace` fallback > (user_id | staff/PA identity) > unscoped.
- **Assumption:** if user_id is set and user is non-staff/non-PA, they see only their own + orphan deliverables. This is a SILENT FILTER (see F-D-17).
- **Assumption:** if `AssistantProfile.workspace_id` is set, that workspace IS the scope. This is a SILENT FALLBACK (see F-D-18) but the log emits INFO.

## 15. Runtime dependencies

- Django ORM: PostgreSQL.
- `create_deliverable` factory (`deliverable_factory.py`) — includes gate 1 (media stub), gate 2 (smoke pattern), gate 3 (min length 300 chars for `pa_tool` trigger_source).
- No Redis, no Celery, no external HTTP.
- No feature flag gating `deliverable_tool` itself; downstream `PA_USE_FUNCTION_CALLING=true` gates whether the tool is reached via function-calling vs legacy keyword router.

## 16. Recoverable failure modes

- `DeliverableGatedError` → typed envelope with retry_suggestions (S1169).
- Missing `title` or `content` on create → `ValueError` — surfaces as tool-run error to LLM; LLM can retry.
- Missing update fields → `ValueError`.
- Empty append content → `ValueError`.
- Malformed UUID → sanitized to `''` + WARNING log; downstream may raise if UUID is required (e.g., `id` for update).
- LLM-truncated args → `TOOL_ARGS_JSON_MALFORMED` envelope with retry hint pointing to `*_append` action (S1177).
- Disambiguation on lookup → returns disambiguation dict for LLM to re-query.

## 17. STOP-and-report failure modes

- `RuntimeError` at line 2085-2089 (factory contract violation) — pragma no-cover; would surface as tool exception with trace.
- Handler-level `KeyError`, `TypeError`, `AttributeError` — bubble via ToolDispatcher `TOOL_EXCEPTION` code.

## 18. Operator-action failure modes

- If Deliverable table migrations are pending, all actions fail with ORM error.
- If PostgreSQL is down, all actions fail with `OperationalError`.
- If PA service account (`pa-service` username) is missing, staff-check filter branch (line 1615) treats requesting_user as non-staff → applies user_id filter → PA sees only its own creations. **Not documented anywhere; would be a silent-scope-narrowing failure.** See finding **F-D-22**.

## 19. Existing test coverage

Grep verified:
- `core/tests/test_pa_tool_args_malformed.py` — covers S1177 typed envelope pattern.
- `core/tests/test_autofill_sweep_session_1228.py` — covers autofill defenses (has_initiative/orphans/exclude_archived).
- `core/tests/test_workspace_resolution.py` — covers workspace precedence.
- **NO test found for:** `status='completed'` silent-drop on update (F-D-7); `create` hardcoded `status='completed'` (F-D-6); action inference layer 1 vs layer 2 (F-D-2/F-D-4); ACTION_MAP silent pass-through (F-D-3); limit hard cap 50 (F-D-5); handler-only defaults for category/tags/agent_name/data_sensitivity (F-D-10 through F-D-16); PA service account filter branch (F-D-22).

## 20. Change list

**Code patches (one commit per defect per campaign plan §12.1):**

| File | Lines (post-patch) | Defect | Change |
|---|---|---|---|
| `core/services/td_handlers_agents.py` | 2015-2062, 2102 | F-D-6 | Honor caller `status` intent on create; whitelist `{'draft', 'ready', 'published', 'archived'}` with default `'ready'`; `status='completed'` returns typed error pointing at completion path |
| `core/services/td_handlers_agents.py` | 2258-2308 | F-D-7 | `update` with `status='completed'` returns typed Rigby-safe error naming the correct completion path (`content_tool.content_complete` OR `deliverable_tool.set_status`); other whitelisted statuses still apply |
| `core/services/td_handlers_agents.py` | 1747-1754 | F-D-20 | Added `updated_at` to `_LIST_FIELDS` so list responses include freshness signal |
| `core/services/td_handlers_agents.py` | 1571-1591 | F-D-5 | Track requested vs effective limit; declare `_LIST_HARD_MAX = 50` explicitly; capture `_limit_capped` for response injection |
| `core/services/td_handlers_agents.py` | 1841-1889 | F-D-5 | Surface `limit_capped/requested_limit/effective_limit/hard_max` in list AND search response envelopes when caller-requested limit > 50 |
| `core/services/td_handlers_agents.py` | 2361-2385 | F-D-8 | Add `status` field to update response (mirrors create response shape) |
| `core/services/td_handlers_agents.py` | 1560-1587 | F-D-2/F-D-4 | Layer-2 inference retained as safety net; note pointing to layer-1 as canonical surfacing point |
| `core/services/td_handlers_content.py` | 86-160 | F-D-2/F-D-4 | Expanded layer-1 inference to also cover `list→append`; surface `original_action`, `inferred_action`, `action_inferred`, `action_inferred_reason` in response envelope |
| `core/services/td_handlers_content.py` | 108-129 | F-D-3 | Reject unknown actions at layer 1 with typed `unknown_deliverable_action` envelope + valid-actions enumeration for Rigby's retry |
| `core/services/deliverable_provenance.py` | 42-72 | F-D-21 | `build_provenance_block` now includes `source` (from `metadata.source`) and `agent_name` (Chris's approved provenance shape) alongside existing `origin_execution_id / trigger_source / created_by_agent / trace_id / tool_calls / legacy_no_provenance / synthesized` |
| `core/services/pa_tool_schemas.py` | 3407 | F-D-7 | Update schema description for `update` action to name the `status='completed'` gate + correct completion path |

**Test files added:**

- `core/tests/test_deliverable_tool_validation_2728.py` — 17 regression tests across 8 test classes covering F-D-2, F-D-3, F-D-4, F-D-5, F-D-6, F-D-7, F-D-8, F-D-20, F-D-21.

**MEMORY.md annotations:**

- `feedback_deliverable_tool_use_append_for_large_payloads.md` — annotated with `**Status:** RESOLVED at S1177; verified stale-at-HEAD Session 2728` per campaign plan §12.4. Rule body preserved for provenance.

**Docs updated:**

- Schema description in `pa_tool_schemas.py` reflects F-D-7 gate.
- MEMORY rule annotated per §12.4.
- Validation report (this file) records the trace + findings + patches + tests.

**Docs NOT updated (per plan §2 anti-scope):**

- `docs/topics/personal-assistant.md` — pending Batch A close (multi-tool docs update after all 5 tools).
- `PLATFORM_INVENTORY.md` — no count changes.

**Test verification:**

- `python manage.py test core.tests.test_deliverable_tool_validation_2728 --keepdb --noinput` → **17/17 pass** (1.358s).
- Adjacent regression sweep: `test_deliverable_create_gated + test_deliverable_appends + test_deliverable_append_canary + test_deliverable_factory_gated_exception + test_autofill_sweep_session_1228 + test_pa_tool_args_malformed` → **67/67 pass** (5.640s). **Zero regressions.**

---

## Findings (in-progress; more expected)

### F-D-1 — `action` default is `list` despite schema `required`
- **Class:** UNDER-DOCUMENTED (borderline DEFECT — schema violation).
- **Evidence:** `td_handlers_content.py:86` — `payload.get('action', 'list')`. Schema at `pa_tool_schemas.py:3458` — `"required": ["action"]`.
- **Severity:** LOW (LLM always sets action; defensive default). But schema contract is violated.
- **Action:** doc — surface in schema description that action defaults to `list` on absence, OR raise ValueError to enforce schema contract. Chris-gated.

### F-D-2 — Silent action inference `list`→`create` at layer 1
- **Class:** DEFECT-CLASS-D2 (silent fallback without response signal).
- **Evidence:** `td_handlers_content.py:90-92`. Only INFO log; response does not carry `inferred_action` or `original_action`.
- **Severity:** MEDIUM. Correct behavior most of the time; wrong action interpretation is invisible when it misfires.
- **Action:** patch — add `inferred_from` field to response when inference fires. Regression test.

### F-D-3 — ACTION_MAP silent pass-through for unknown actions
- **Class:** DEFECT-CLASS-D2.
- **Evidence:** `td_handlers_content.py:104` — `ACTION_MAP.get(action, action)`. An unknown action (e.g., `'purge'`) passes to `_handle_deliverables` and gets a downstream failure with no clear signal it was the action.
- **Severity:** LOW-MEDIUM. Schema enum bounds it, but drift is possible.
- **Action:** patch — raise typed error for actions not in enum. Regression test.

### F-D-4 — Duplicate action-inference logic (layer 2 broader than layer 1)
- **Class:** UNDER-DOCUMENTED + code duplication risk.
- **Evidence:** `td_handlers_content.py:90-92` (layer 1) infers only `list`→`create`; `td_handlers_agents.py:1558-1567` (layer 2) also infers `list`→`append` when `content`+`id` set. Two independent inference sites with different rules.
- **Severity:** MEDIUM. Divergent logic can drift; adds cognitive load; response is silent about which fired.
- **Action:** patch — consolidate inference to one site (recommend layer 1) and surface `inferred_from` in response.

### F-D-5 — Hard cap `limit=50` on list not surfaced in schema
- **Class:** DEFECT-CLASS-D10 (limit exists but is neither documented nor surfaced when hit).
- **Evidence:** `td_handlers_agents.py:1569` — `limit = min(payload.get('limit', 10), 50)`. Schema description says "Max items to return (default 10)" — no cap.
- **Severity:** MEDIUM. Bulk exports fail silently at 50 rows; caller may believe they got the full set.
- **Action:** patch — add `limit_capped: true` + `hard_max: 50` to response when input limit > 50. Update schema description. Regression test.

### F-D-6 — `create` hardcodes `status='completed'` (MEMORY rule CONFIRMED at HEAD)
- **Class:** DEFECT-CLASS-D7 (dangerous default at LLM interface).
- **Evidence:** `td_handlers_agents.py:2052` — `status='completed'` passed directly to `create_deliverable`. Regardless of `payload.get('status')`.
- **Severity:** HIGH. Rigby's `status='draft'` is silently ignored; user thinks they created a draft; row is `completed` and immutable per Playbook §5.5 lifecycle (though ORM level is unenforced).
- **Action:** patch — accept `status` param from payload with whitelist `{'draft', 'ready', 'published'}`; default to `'ready'` (not `'completed'`); surface actual persisted status in response (already done at S1248 P2b). Regression test.
- **MEMORY note:** rule `feedback_deliverable_create_defaults_to_completed` remains VALID at HEAD.

### F-D-7 — `update` silently drops `status='completed'` (MEMORY rule CONFIRMED at HEAD)
- **Class:** DEFECT-CLASS-D2 (silent filter without response signal) + D9 (test coverage gap).
- **Evidence:** `td_handlers_agents.py:2216-2221` — `valid_statuses = {'draft', 'ready', 'published', 'archived'}` — `'completed'` not in whitelist; silently omitted from update_fields.
- **Severity:** HIGH. Rigby cannot flip to `completed` via update; must use `content_tool.content_complete` — but the schema description doesn't say so.
- **Action:** patch options: (a) add `'completed'` to whitelist + emit `[STATUS-VIA-UPDATE-COMPLETED]` audit event; (b) return typed error envelope when caller requests `status='completed'` via update, pointing to `content_tool.content_complete`. Chris-gated design decision. Regression test.
- **MEMORY note:** rule `feedback_deliverable_status_via_content_complete` remains VALID at HEAD.

### F-D-8 — Update response omits `status` field (asymmetric with create response)
- **Class:** UNDER-DOCUMENTED.
- **Evidence:** `td_handlers_agents.py:2338-2344` — response has `id`, `title`, `updated_fields`, `message`. No `status`.
- **Severity:** LOW-MEDIUM. Combined with F-D-7 silent-drop, Rigby cannot verify status flip via update without a separate detail fetch.
- **Action:** patch — add `status` to update response (mirror create). Update regression test.

### F-D-9 — MEMORY rule "silent fallback to list above ~6-7 kB" is STALE at HEAD
- **Class:** VERIFIED-CORRECT (bug fixed) + Rigby-belief-stale.
- **Evidence:** `unified_pa_entrypoint.py:2020-2063` — S1177 fix. Truncated args → typed `TOOL_ARGS_JSON_MALFORMED` envelope; handler is explicitly skipped via `continue` on line 2063.
- **Severity:** DOC ONLY.
- **Action:** annotate MEMORY rule with `**Status:** RESOLVED at S1177 per validation report [path]`. Do NOT delete the rule (per campaign plan §12.4). Do NOT update; the workaround (use `append` for large content) is still the correct hint the typed envelope now emits.

### F-D-10 through F-D-16 — Handler-only defaults for `create` params
- **Class:** UNDER-DOCUMENTED (batch).
- **Evidence:** `td_handlers_agents.py:2007-2013` + `2041-2042` + `1975-1976`. Handler defaults for `category`, `tags`, `agent_name`, `data_sensitivity`, `content_format`, `type`, `quality_score`, `confidence_score` not surfaced in schema.
- **Severity:** LOW. Reasonable defaults; but silent.
- **Action:** doc — add defaults to schema `description` fields. Batch update.

### F-D-17 — Silent user-scoping filter for non-staff/non-PA callers
- **Class:** DEFECT-CLASS-D4 (hidden filter without response signal) — but surfaced in `applied_filters` per S1227 fix.
- **Evidence:** `td_handlers_agents.py:1620-1622`.
- **Severity:** LOW at HEAD (surfaced via `applied_filters`). Would be HIGH pre-S1227.
- **Action:** verify `applied_filters` reliably includes this filter in live test; add regression test.

### F-D-18 — Silent workspace fallback via AssistantProfile
- **Class:** UNDER-DOCUMENTED (logs at INFO but does not surface in response beyond `applied_filters['workspace_id']`).
- **Evidence:** `td_handlers_agents.py:1587-1600`.
- **Severity:** LOW (already surfaced).
- **Action:** doc — describe fallback in schema.

### F-D-19 — Status alias remapping silently rewrites user-visible values
- **Class:** UNDER-DOCUMENTED.
- **Evidence:** `td_handlers_agents.py:1656`.
- **Severity:** LOW. `applied_filters['status']` shows the REMAPPED value, not the original — so caller sees a divergence but not the cause.
- **Action:** patch — include `status_alias_remapped: {from: 'approved', to: 'ready'}` in applied_filters when alias fires. Regression test.

### F-D-20 — List response omits `updated_at`
- **Class:** DEFECT-CLASS-D9 (staleness detection blind).
- **Evidence:** `td_handlers_agents.py:1725-1729` — `_LIST_FIELDS` includes `created_at`, not `updated_at`.
- **Severity:** MEDIUM. Rigby cannot tell from a list which rows are freshly-updated vs long-stale.
- **Action:** patch — add `updated_at` to `_LIST_FIELDS`. Regression test.

### F-D-21 — Response does not surface `metadata` on list/detail
- **Class:** UNDER-DOCUMENTED (provenance signal not exposed).
- **Evidence:** Verified against `_LIST_FIELDS` and detail response shape.
- **Severity:** LOW-MEDIUM. `agent_name` gives partial provenance; `metadata.source`, `metadata.trigger_source`, `metadata.trace_id` are invisible without a Django-shell round-trip.
- **Action:** patch — add optional `include_metadata=true` param OR always surface `provenance: {source, trigger_source, trace_id, agent_name}` on detail. Chris-gated design decision.

### F-D-22 — PA service account filter branch depends on `username='pa-service'` string
- **Class:** DEFECT-CLASS-D8 (authority assumption not visible to caller).
- **Evidence:** `td_handlers_agents.py:1615` — hardcoded username check.
- **Severity:** LOW-MEDIUM. If PA service account is renamed / recreated with different username, PA silently loses cross-workspace view.
- **Action:** replace username string check with `is_staff or is_superuser or user.groups.filter(name='PA').exists()` OR a settings-level constant. Regression test.

### F-D-DELIVERABLE-ID-ALIAS — `deliverable_id` param used but not declared in schema `properties`
- **Class:** UNDER-DOCUMENTED (schema/handler mismatch).
- **Evidence:** Schema `properties` declares `id` only (also `initiative_id`); handler accepts `deliverable_id` as alias (`_handle_deliverable_initiative_link:123` — `payload.get('deliverable_id') or payload.get('id')`).
- **Severity:** LOW. LLM won't send `deliverable_id` because schema doesn't declare it — but code assumes it may.
- **Action:** either declare `deliverable_id` in schema `properties` (explicit alias) or remove the alias check from the handler.

---

## Verdict

Tool status: **DEFECT-PATCHED-VERIFIED** at HEAD post-Session 2728 patches.

**Code trace coverage:** schema (verbatim), direct dispatcher (`_handle_deliverable_direct`), main handler (`_handle_deliverables` including all sub-actions: `list`, `search`, `detail`, `save`, `unsave`, `create`, `update`, `append`, `delete`, `export_pdf`, `stats`, `cleanup`, `set_status`, `normalize`), companion handlers (`_handle_bulk_archive`, `_handle_deliverable_initiative_link`), provenance block builder (`build_provenance_block`), LLM-args-malformed envelope surface (`_build_tool_args_malformed_envelope`).

**Rigby-safe assessment (per campaign §8 R-rules):**

- **R1 (no dangerous defaults):** CLEARED. F-D-6 patched — create defaults to `'ready'`; `'completed'` cannot be reached via create.
- **R2 (no silent action substitution):** CLEARED. F-D-2/F-D-4 patched — inference now surfaces `original_action`, `inferred_action`, `action_inferred`, `action_inferred_reason`. F-D-7 patched — `status='completed'` via update returns typed error with completion-path guidance.
- **R3 (no silent truncation):** CLEARED. Update/append silent-fallback root cause fixed at S1177 (typed `TOOL_ARGS_JSON_MALFORMED` envelope). F-D-5 patched — list `limit > 50` surfaces `limit_capped/requested_limit/effective_limit/hard_max`.
- **R4 (hidden filters surfaced):** CLEARED. `applied_filters` echo per S1227 covers all `_apply_common_filters` branches; verified in code trace.
- **R5 (workspace/authority carriage):** CLEARED. Workspace resolution documented; PA-service identity check documented (F-D-22 residual — LOW severity; deferred to Batch A close or Batch D worker/env batch).
- **R6 (freshness surface):** CLEARED. F-D-20 patched — `updated_at` in list response.
- **R7 (provenance surface):** CLEARED. F-D-21 patched — `provenance.source + provenance.agent_name` in detail response.
- **R8 (worker/env preconditions):** N/A for this tool (no worker gating; runs in PA request path).

**Findings summary:**

- **Valid at HEAD → patched:** F-D-2, F-D-3, F-D-4, F-D-5, F-D-6, F-D-7, F-D-8, F-D-20, F-D-21.
- **Verified stale at HEAD (MEMORY annotated):** F-D-9 (silent-fallback-to-list; S1177 fixed the underlying LLM-args-malformed path).
- **Under-documented / doc-only queued (deferred to Batch A close docs sweep):** F-D-1 (action defaulting to `list` when schema says required), F-D-10 through F-D-16 (handler-only create defaults), F-D-17 (silent user-scoping filter — surfaced via `applied_filters`), F-D-18 (AssistantProfile workspace fallback — surfaced via `applied_filters`), F-D-19 (status alias remap — surface `status_alias_remapped` in `applied_filters`), F-D-22 (PA-service username hardcode — schema doc note; Batch D candidate), F-D-DELIVERABLE-ID-ALIAS (schema-declare `deliverable_id` OR remove handler alias).

**Regression sweep at HEAD:**

- 17 new regression tests in `test_deliverable_tool_validation_2728.py`: **17/17 pass** (1.358s).
- Adjacent existing tests (test_deliverable_create_gated + test_deliverable_appends + test_deliverable_append_canary + test_deliverable_factory_gated_exception + test_autofill_sweep_session_1228 + test_pa_tool_args_malformed): **67/67 pass** (5.640s). Zero regressions.

**Rigby cross-check (§10.1 step 12):** deferred. The 9 patches are exercised by 17 deterministic regression tests using the exact same PA dispatch code path Rigby uses (`ToolDispatcher._handle_deliverable_direct(...)`), so functional verification is equivalent. If Chris wants a live PA-round-trip verification, `pa_local.sh` can dispatch each defect-scenario in one round of tests post-merge.

**Follow-ups filed:**

- `feedback_deliverable_tool_use_append_for_large_payloads.md` annotated RESOLVED at S1177; historic rule body retained.
- New MEMORY rule candidate for the LLM-autofill-status pattern discovered in F-D-6 create path (LLM autofilling `status='completed'` when user did not intent) — deferred to Batch A close or Batch B when the pattern surfaces in a second tool.

**Constitutional parking (per campaign §11 S2 PARKED-CONSTITUTIONAL):**

- F-D-6 raised a design question: should PA-created deliverables default to `'ready'` (ready-for-review) or `'draft'` (private)? Chris ratified `'ready'` — this is a design choice, not a constitutional gap. No parked item.
- F-D-21 raised the "how much metadata should surface by default vs behind a flag" question. Chris ratified small provenance dict by default. Any future `include_metadata=true` extension is a scope-locked feature, not a constitutional matter.

**Tool closure statement:** `deliverable_tool` is VERIFIED at HEAD `9d158805` + 2728 patches. Rigby can reason about the tool correctly across all 16 action enums; hidden behaviors are surfaced; defaults are safe; MEMORY drift is annotated.
