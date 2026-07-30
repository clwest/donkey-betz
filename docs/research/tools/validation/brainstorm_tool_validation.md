# `brainstorm_tool` — Validation Report (S2910)

**Tool:** `brainstorm_tool`
**Schema:** `core/services/pa_tool_schemas.py:56`
**Handler:** `core/services/td_handlers_agents.py:6136` (`_handle_brainstorm`)
**Register site:** `core/services/tool_dispatcher.py` (via `AgentHandlersMixin`)
**Session:** S2910 (Path B systematic sweep — Slice 2 batch 5 of `td_handlers_agents`, second mixed-safety batch after S2908 shape-break precedent; first small-actionful mixed batch on the S2909-hardened harness)
**HEAD at validation:** `e642c7aa8` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; MUTATION action explicitly excluded — see §5a).
**Rigby SIGN:** S2910 T0 SIGN AGREE-with-edits (batch 5 composition + shape recommendation; Q4 zoom-out flagged heterogeneous risk surfaces + `schedule_followup` context coupling — see §Related). S2910 T1 SIGN pending.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Search + list surface over the platform's brainstorming corpus — Discussion panels, multi-agent debates, and BrainstormConversation rows produced by the ThinkingAgent / Boardroom pipeline. Answers "what have we brainstormed about X?" and "what were the recent panels/discussions?" without opening the full boardroom UI.

Distinct from `deliverable_tool` (which surfaces finalized workspace artifacts) and `intelligence_tool` (which routes across web/spider/agent sources). `brainstorm_tool` is read-primary; the one MUTATION action (`create`) dispatches a fresh ThinkingAgent brainstorm via Celery `long_running` and is out of scope for this ship (see §5a).

## Covered actions

**READ_ONLY actions covered only (6 of 7 total actions).** MUTATION action (1 excluded — see §5a Mutation containment for the named action, deferral rationale, and planned coverage slice) is out of scope for this ship.

- `list` — **in scope this ship** — verified live via T1a harness (`status_code=200`, `expected_outcome=success`). Returns `{action, conversations, has_more, limit, offset, total_count}` — paginated cross-type list (Discussion + Panel + BrainstormConversation) over `days_back` window.
- `recent` — **in scope this ship** — verified live via T1a harness (`success`). Returns `{action, discussions, panels, period_days, total_discussions, total_panels}` — recent brainstorming summaries split by type.
- `stats` — **in scope this ship** — verified live via T1a harness (`success`). Returns `{action, daily_breakdown, period_days, top_keywords, total_brainstorming, total_discussions, total_panels}` — activity aggregate.
- `search` — **in scope this ship** — verified live via T1a harness error path (`expected_outcome=error_captured`, requires `query`). Raises `ValueError('query is required for search action')` at handler line 6163.
- `details` — **in scope this ship** — verified live via T1a harness error path (`error_captured`, requires `conversation_id` | `id`). Raises `ValueError` at handler line 6190.
- `by_category` — **in scope this ship** — verified live via T1a harness error path (`error_captured`, requires `category`). Raises `ValueError` at handler line 6203.
- `create` — **mutation — deferred to Slice 2 write batch** — see §5a. Classified `MUTATION` in `TOOL_ACTION_METADATA`; harness reports `expected_outcome=skipped_mutation`. Dispatches a fresh ThinkingAgent brainstorm via Celery `long_running`.

## 3. Schema notes

- **Required:** `action` (enum: `list, search, recent, details, by_category, stats, create`).
- **Conditional required (handler-enforced, per action):**
  - `query` for `search` — fail-loud via `ValueError`.
  - `conversation_id` (or `id` alias) for `details` — fail-loud via `ValueError`.
  - `category` for `by_category` — fail-loud via `ValueError`.
  - `topic` (or `query` alias) for `create` — fail-loud via `ValueError`.
- **Optional:** `limit` (default 50 for list, 10 for search), `offset` (list pagination, default 0), `days` / `days_back` (default 30, Session 1228 PR-B autofill safety fills `days_back=30` when caller passes empty), `type` (filter: `discussion|panel`), `status` (conversation-status filter), `include_transcript` (list, default false), `include_full_content` (details, default false), `id` (alias for `conversation_id` on details).
- **Session 1228 PR-B autofill safety** at handler lines 6165/6178/6205/6216: `days_back = payload.get('days_back') or 30` — protects against empty-string / null-string autofill from callers that omit the field.
- **`list` limit clamp:** `min(payload.get('limit', 50), 200)` at handler line 6218 — hard cap at 200 per response.

## 4. Golden-path examples

**"What have we brainstormed recently?"**

```
brainstorm_tool  action=recent
```

**"Show me the last 20 panels/discussions this month:"**

```
brainstorm_tool  action=list  limit=20  days=30
```

**"Search for brainstorming around 'onboarding':"**

```
brainstorm_tool  action=search  query="onboarding"  limit=5
```

**"Get full details of one panel:"**

```
brainstorm_tool  action=details  conversation_id=<uuid>  include_full_content=true
```

**"How much have we brainstormed this quarter?"**

```
brainstorm_tool  action=stats  days=90
```

## 5. Failure / empty-state / pagination notes

- **`list` empty result** — returns `{action: 'list', conversations: [], has_more: false, limit, offset, total_count: 0}`. Consistent shape.
- **`recent` empty result** — returns zero-count arrays with `period_days` echoed.
- **`stats` with zero brainstorming** — returns `{action: 'stats', daily_breakdown: [], top_keywords: [], total_*: 0, period_days}`. Consistent shape.
- **`search` / `details` / `by_category` missing required arg** — raises `ValueError` → dispatcher wraps as `TOOL_EXCEPTION` at HTTP 500. Fail-loud, not silent. Contrast the inline `{ok: false}` envelope pattern of `orm_inspect_tool` (S2907 — FT-5 candidate substrate finding).
- **`list` pagination** — `offset` + `limit` (default 50, cap 200); `has_more` boolean flag on response. Cursor pattern is offset-based, not opaque-token.
- **`details` UUID not found** — `BrainstormSearchService.get_conversation_insights` returns whatever the underlying model lookup yields; handler does not add a "not found" branch. Runtime-not-executed this ship; consumers should not assume a standard "not found" envelope.
- **Unknown action** — raises `ValueError('Unknown action: {action}. Valid actions: list, search, recent, details, by_category, stats, create')` at handler line 6262 → `TOOL_EXCEPTION`.

## 5a. Mutation containment (per Rigby T0 SIGN edit — mandatory §5a)

- **Mutating action excluded this ship:**
  - `create` — dispatches `execute_agent_task.apply_async(['ThinkingAgent', ...])` on the `long_running` Celery queue at handler line 6246. Async side-effect: fresh brainstorm conversation created + ThinkingAgent LLM invoked (cost + time). Classified `MUTATION` in `TOOL_ACTION_METADATA` seed this ship — no confirmation flag, no dry-run mode.
- **Containment mechanism:** per-action `TOOL_ACTION_METADATA` record with `safety_class='MUTATION'` at `tool_action_metadata.py`; harness resolves via `resolve_safety()` and skips at dispatch (`expected_outcome=skipped_mutation` — verified in artifact §6.1).
- **dependency_surface note:** `internal` — Celery queue dispatch of ThinkingAgent through existing `execute_agent_task`. No external bridge.
- **Deferral rationale:** `create` requires (a) a real user/session (Celery task carries `user_id` in kwargs; harness runs anonymous) + (b) a topic/query payload + (c) tolerance for real LLM cost accrual and a `long_running`-queue slot. Doc-only sweep cannot exercise it safely. Deferred to a future MUTATION-coverage batch that pairs with a `dry_run` / seeded-conversation harness pattern (candidate — Rigby T1 SIGN can pressure-test whether MUTATION-coverage needs a dedicated sub-arc).

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness brainstorm_tool` at HEAD `e642c7aa8` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `list` | `success` | 200 | 23 ms | `action, conversations, has_more, limit, offset, total_count` |
| `search` | `error_captured` | 500 | 6 ms | — (`error_code=TOOL_EXCEPTION; msg=query is required for search action`) |
| `recent` | `success` | 200 | 12 ms | `action, discussions, panels, period_days, total_discussions, total_panels` |
| `details` | `error_captured` | 500 | 2 ms | — (`error_code=TOOL_EXCEPTION; msg=conversation_id (or id) is required for details action`) |
| `by_category` | `error_captured` | 500 | 2 ms | — (`error_code=TOOL_EXCEPTION; msg=category is required for by_category action`) |
| `stats` | `success` | 200 | 7 ms | `action, daily_breakdown, period_days, top_keywords, total_brainstorming, total_discussions, total_panels` |
| `create` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |

Artifact: `docs/audits/pa_tools/harness_output/brainstorm_tool.json`.

**Envelope-shape observation:** all 3 required-arg misses (`search` / `details` / `by_category`) raise `ValueError` → dispatcher wraps at `TOOL_EXCEPTION` (HTTP 500) → `error_captured`. **NOT** the inline `{ok: false, error_code, error}` envelope pattern that produced S2907's `orm_inspect_tool` residual `soft_error` cases at S2909 close (the FT-5 substrate candidate). `brainstorm_tool` is behaviorally cleaner: fail-loud via exception, no ambiguity between transport-success + envelope-failure and true success.

### 6.2 Runtime-not-executed — this ship

- **`list` with populated `days_back` filter** — not exercised against a real brainstorm corpus (would confirm the item shape per Discussion / Panel / BrainstormConversation type + the temporal ordering + `has_more`/`total_count` pagination arithmetic).
- **`search` with a real query** — not exercised (would confirm `BrainstormSearchService.search` result shape + score/relevance fields).
- **`details` with a real conversation UUID** — not exercised (would confirm type-specific detail shape + optional `include_full_content` payload expansion).
- **`by_category` with a real category** — not exercised (would confirm category filter propagation).
- **`create`** — MUTATION-skipped (see §5a).
- **`stats` daily_breakdown / top_keywords shape** — not exercised against populated corpus.

---

## Related

- **Ledger candidates surfaced this ship:** none new. Behavior is clean fail-loud; no drift-of-envelope pattern. Contrast the S2909 FT-5 candidate (orm_inspect_tool required-arg soft_error) — `brainstorm_tool` sits on the "correct-shape" side of that same class.
- **Adjacent tools:**
  - `deliverable_tool` — finalized workspace artifacts (different corpus).
  - `intelligence_tool` — multi-source routing (web/spider/agent); does NOT back-route through this handler.
  - `execution_history_tool` — surfaces `AgentExecution` rows; a `brainstorm_tool.create` dispatch produces one that shows up there.
- **Substrate context:** first small-actionful mixed-safety tool validated on the S2909-hardened harness (post-T1 soft_error classifier + T2 bridge preflight). Batch 5 peers: `web_fetch_tool` (uniform READ_ONLY, actionless), `schedule_followup` (uniform WRITE_GATED, actionless, PA-context gate), `legal_doc_drafter_agent` (uniform MUTATION, actionless, disclaimer gate). Rigby T0 SIGN Q4 flagged batch 5 as heterogeneous risk surfaces bundled — this doc is the READ_ONLY-heavy anchor of the batch; other 3 tools carry the write-shape complexity.
- **Metadata seed:** 7 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship (Pattern C — no `TOOL_DEFAULTS` entry; per-action records are the safety source, mirroring `bpaas_tool` / `session_tool` / `revenue_tracker_tool` precedent).
