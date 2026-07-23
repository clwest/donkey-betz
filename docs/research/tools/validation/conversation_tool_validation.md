# `conversation_tool` — Validation Report (S2913)

**Tool:** `conversation_tool`
**Schema:** `core/services/pa_tool_schemas.py:2396`
**Handler:** `core/services/td_handlers_core.py:1974` (`_handle_conversation`)
**Register site:** `core/services/tool_dispatcher.py` (via `CoreHandlersMixin`)
**Session:** S2913 (Path B systematic sweep — Slice 3 batch 2 of `td_handlers_core`)
**HEAD at validation:** `00fcb352f` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; 3 MUTATION actions `search` + `summary` + `pin_memory` explicitly excluded — see §5a).
**Rigby SIGN:** S2913 T1 SIGN AGREE-with-edits — V1 with Claude course-correction: **`search` reclassified from Rigby-assumed READ_ONLY to MUTATION** after Claude's direct handler read confirmed `EmbeddingService.create_embedding(query)` is invoked on every search call at line 2038 (LLM cost). Per `feedback_verify_rigby_tool_runs_before_trusting_sign` — this is a Claude verification catching a Rigby assumption before ship. V3 AGREE (Concern C count does not advance in batch 2).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Search and retrieve past PA conversations across threads. Answers "what did we discuss?", "do you remember X?", "what did I say about Y?", "show me the summary of conversation Z". Pull full conversation transcripts, semantic-search past discussions, dispatch async summarization, pin decisions as durable memory, or list recent conversations.

Distinct from `remember_tool` (which stores explicit user-declared preferences/goals as `UserMemoryContext` rows) and `deliverable_tool` (which manages first-class work artifacts). `conversation_tool` reads/writes `ChatConversation` turns and `ConversationMemory` embeddings — the substrate for cross-thread PA recall.

## Covered actions

**READ_ONLY actions covered only (2 of 5 total actions).** 3 MUTATION actions (`search` — LLM embedding cost; `summary` — async Celery LLM; `pin_memory` — row create + LLM embed — excluded — see §5a) are out of scope for this ship.

- `get` — **in scope this ship** — verified live via T1a harness (`error_captured` path when `conversation_id` missing; success path shape confirmed by handler trace). Returns `{action, conversation_id, session_title, turn_count, offset, page_size, has_more, turns}` — paginated ChatConversation slice (max 30 turns/page, 1000-char content cap per turn).
- `search` — **mutation — deferred (LLM embedding cost)** — see §5a
- `summary` — **mutation — deferred (async Celery LLM)** — see §5a
- `pin_memory` — **mutation — deferred (row create + LLM embed)** — see §5a
- `recent` — **in scope this ship** — verified live via T1a harness (`success`). Returns distinct `pa-*` conversation_ids with Max(`created_at`) as `last_activity`, user-scoped when `user_id` present.

## 3. Schema notes

- **Required:** `action` (enum: `get, search, summary, pin_memory, recent`).
- **Conditional required (handler-enforced, per action):**
  - `conversation_id` for `get` — inline `{error}` if missing.
  - `query` for `search` — inline `{error}` if missing.
  - `conversation_id` for `summary` — inline `{error}` if missing.
  - `pin_title` + `pin_content` for `pin_memory` (both non-empty after strip) — inline `{error}` if missing.
- **Optional:** `limit` (default 10; max 50), `offset` (for `get` pagination), `days_back` (for `search` recency filter), `pin_tags` (defaults to `['pa-memory']` for `pin_memory`).
- **Pagination shape (`get` only):** offset+page_size with `has_more` flag; page_size capped at `min(limit, 30)`; per-turn content cap at 1000 chars.
- **User-scoping:** all read paths apply `if user_id: qs = qs.filter(user_id=user_id)`. `pin_memory` writes `ConversationMemory` only when `user_id` present (else silent skip).

## 4. Golden-path examples

**"Get the full transcript of conversation pa-33e4d55d31b6:"**

```
conversation_tool  action=get  conversation_id=pa-33e4d55d31b6
```

**"List my most recent conversations:"**

```
conversation_tool  action=recent
```

**"Search past discussions about X:"** *(NOT exercised this ship — see §5a)*

```
conversation_tool  action=search  query=<phrase>
```

**"Summarize conversation X asynchronously:"** *(NOT exercised this ship — see §5a)*

```
conversation_tool  action=summary  conversation_id=<id>
```

**"Pin this decision as durable memory:"** *(NOT exercised this ship — see §5a)*

```
conversation_tool  action=pin_memory  pin_title=<title>  pin_content=<content>
```

## 5. Failure / empty-state / pagination notes

- **`get` missing `conversation_id`** — returns `{error: 'conversation_id required for get action'}`. Inline `{error}` envelope, not raise.
- **`get` for unknown conversation** — returns `{action: get, conversation_id, turns: [], message: 'No conversation found'}`. Consistent shape; no fail-loud.
- **`get` past-end pagination** — returns empty `turns` list with `has_more: False`. Consistent shape.
- **`recent` with no `pa-*` conversations** — returns `{action: recent, count: 0, conversations: []}`. Consistent shape.
- **`search` missing `query`** — returns `{error: 'query required for search action'}`. MUTATION-skipped at metadata layer this ship; error path verified by handler inspection.
- **`search` when embedding service fails** — inner try/except at handler lines 2034-2061 catches `Exception`, logs warning, and falls back to keyword search on `ChatConversation` only. Never raises.
- **`summary` missing `conversation_id`** — returns `{error: 'conversation_id required for summary action'}`. MUTATION-skipped at metadata layer this ship.
- **`pin_memory` missing `pin_title` or `pin_content`** — returns `{error: 'pin_title and pin_content required...'}`. MUTATION-skipped at metadata layer this ship.
- **`pin_memory` when embedding fails** — inner try/except at handler lines 2154-2168 catches, logs warning, and skips ConversationMemory create. Deliverable is still created (fail-partial semantic).
- **Unknown action** — returns `{error: f'Unknown action: {action}'}` at handler line 2208. Inline `{error}` envelope.

## 5a. Mutation containment (per Rigby T1 SIGN V1 + Claude V1 course-correction)

- **Mutating actions excluded this ship:**
  - `search` — invokes `EmbeddingService.create_embedding(query, agent_name='conversation_tool')` at handler line 2038 BEFORE the pgvector CosineDistance semantic search. This is the query-side embedding generation — every search call incurs LLM cost. **Classification correction:** Rigby's T1 SIGN V1 assumed search was "text/field search, not embedding generation." Claude direct handler read (`grep -n "EmbeddingService" td_handlers_core.py` + trace at :2038) confirmed the LLM call fires unconditionally. Reclassified as MUTATION per `feedback_verify_rigby_tool_runs_before_trusting_sign`.
  - `summary` — dispatches `summarize_conversation_task.apply_async_with_actor` at handler line 2119. Async Celery job; server-side LLM summarization. Classified `MUTATION`.
  - `pin_memory` — creates a `Deliverable` row via `create_deliverable` at handler line 2140 + creates a `ConversationMemory` row via `.objects.create` at handler line 2160 + fires `EmbeddingService.create_embedding` for the pinned content (LLM cost). Classified `MUTATION`.
- **Containment mechanism:** per-action `TOOL_ACTION_METADATA` records with `safety_class='MUTATION'` at `tool_action_metadata.py`; harness `resolve_safety()` skips at dispatch (`expected_outcome=skipped_mutation`).
- **dependency_surface note:** `internal + LLM` — `EmbeddingService` fires OpenAI-family embedding calls; `summarize_conversation_task` runs LLM summarization; `create_deliverable` writes ORM rows. No external bridge (S2909-class).
- **Deferral rationale:** LLM cost accumulates per invocation across `search` + `pin_memory` embed calls; `summary` is async so `task_id` is returned but no confirmation of completion; `pin_memory` creates durable Deliverable rows that are hard to clean up in test. Deferred to a future MUTATION-coverage batch that pairs with LLM-cost-cap + row-scoped-cleanup harness patterns.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness conversation_tool` at HEAD `00fcb352f` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `get` | `error_captured` | — | ~1 ms | `error` (`conversation_id required`) |
| `search` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `summary` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `pin_memory` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `recent` | `success` | 200 | ~1 ms | `action, count, conversations` |

Artifact: `docs/audits/pa_tools/harness_output/conversation_tool.json` — 2 READ_ONLY (1 success + 1 error_captured) + 3 MUTATION skipped.

**Envelope-shape observation:** `get` required-arg miss returns inline `{error}` envelope; `recent` returns clean success at HTTP 200. `search`, `summary`, and `pin_memory` cleanly metadata-skipped without handler invocation. The inline `{error}` envelope on `get`'s required-arg miss (vs raise) is drift-shape flagged as a broader ledger candidate but NOT specific to this tool.

### 6.2 Runtime-not-executed — this ship

- **`get` with a real populated `conversation_id`** — the harness ran the missing-arg error path; the found-conversation success path was not exercised (would confirm pagination + content-cap shape).
- **All 3 write actions (`search` / `summary` / `pin_memory`)** — MUTATION-skipped (see §5a). LLM cost + Celery dispatch not exercised.

---

## Related

- **Adjacent tools:**
  - `remember_tool` (batch 2 peer) — explicit user-declared memories as `UserMemoryContext` rows; different concern from ChatConversation transcript recall.
  - `deliverable_tool` — first-class work artifacts; `conversation_tool.pin_memory` creates a Deliverable but is a specialized surface for pinning conversation snippets.
- **Substrate context:** batch 2 peer of `active_repo_tool`, `db_health_tool`, `remember_tool`. All 4 tools no-network on selected READ_ONLY action, no-Celery, no-writes.
- **Metadata seed:** 5 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship.
- **Session 1086 provenance:** paginated `get` action via offset+page_size — `has_more` flag semantics.
- **Session S2757 B2 provenance:** `summary` action uses `apply_async_with_actor` at handler line 2119 — acting-user identity flows via Celery header, not kwarg (B1 stripping).
- **Course-correction ledger candidate:** Rigby T1 V1 assumed `conversation_tool.search` was pure ORM; Claude direct handler read caught the `EmbeddingService.create_embedding` call at :2038. Applied as unilateral safety-class correction with note in commit + PR body. Per `feedback_verify_rigby_tool_runs_before_trusting_sign`, this is a Claude-verification catching a Rigby-assumption before ship. Not a Playbook amendment trigger (single instance).
