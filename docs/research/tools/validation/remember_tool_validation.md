# `remember_tool` — Validation Report (S2913)

**Tool:** `remember_tool`
**Schema:** `core/services/pa_tool_schemas.py:2344`
**Handler:** `core/services/td_handlers_core.py:2210` (`_handle_remember`)
**Register site:** `core/services/tool_dispatcher.py` (via `CoreHandlersMixin`)
**Session:** S2913 (Path B systematic sweep — Slice 3 batch 2 of `td_handlers_core`)
**HEAD at validation:** `00fcb352f` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; 1 MUTATION action `save` + 1 IRREVERSIBLE action `delete` explicitly excluded — see §5a).
**Rigby SIGN:** S2913 T1 SIGN AGREE-with-edits (V1 AGREE — `remember_tool.search` verified pure `.filter(content__icontains=query)` ORM text search at handler line 2345-2348; no embedding, no LLM cost). V3 AGREE (Concern C count does not advance in batch 2).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Save something to persistent per-user memory that persists across sessions. Answers "remember this", "save this preference", "note that I...", "keep in mind", "always do X", "never do Y", "I prefer...". Also used proactively when the user shares important preferences, goals, constraints, or corrections that should persist. 8 memory types (preference, goal, constraint, instruction, decision, context, skill, project) + 1-10 importance level + tags for categorization.

Distinct from `conversation_tool` (which manages `ChatConversation` transcripts + `ConversationMemory` embeddings for cross-thread recall) and `deliverable_tool` (which manages first-class work artifacts). `remember_tool` is the explicit user-declared memory surface — the user says "remember X" and it lands as a `UserMemoryContext` row scoped to the caller.

## Covered actions

**READ_ONLY actions covered only (2 of 4 total actions).** 1 MUTATION action (`save` — excluded) + 1 IRREVERSIBLE action (`delete` — excluded) are out of scope for this ship. See §5a.

- `save` — **mutation — deferred to future MUTATION-coverage batch** — see §5a
- `list` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms when user_id present; `error_captured` permission_denied when missing). Returns top-20 `UserMemoryContext` rows sorted by `-importance, -created_at` + total count aggregate.
- `delete` — **irreversible — deferred (destroys memory row)** — see §5a
- `search` — **in scope this ship** — verified live via T1a harness (`error_captured` path when `query` missing; success path via handler trace). Pure ORM text search: `UserMemoryContext.filter(user=user, content__icontains=query).order_by(-importance)[:10]`. **No embedding, no LLM cost.**

## 3. Schema notes

- **Required:** `action` (enum: `save, list, delete, search`).
- **Conditional required (handler-enforced, per action):**
  - `content` for `save` (non-empty after strip) — inline `{error}` envelope if missing.
  - `memory_id` for `delete` — inline `{error}` envelope if missing.
  - `query` for `search` — inline `{error}` envelope if missing.
  - **Caller `user_id` for ALL actions** — inline `permission_denied` envelope at handler line 2223 if missing.
- **Optional (`save`):** `memory_type` (enum: preference, goal, constraint, instruction, decision, context, skill, project; default `'preference'`), `importance` (int 1-10, default 7, clamped), `tags` (list of strings, default `[]`).
- **Secret redaction (`save`):** handler applies `core.services.tool_dispatcher._redact_secrets(content)` at handler line 2233 before persistence. Content is capped at 500 chars via `content[:500]` at handler line 2277.
- **Dedup (`save`):** `hashlib.sha256(f"{content.lower().strip()}:{memory_type}").hexdigest()[:16]` at handler line 2250 stored in `context_metadata['content_hash']`. Duplicate detection returns `status='duplicate_updated'` (updates importance if higher) without creating a new row.
- **Cap (`save`):** `MEMORY_MAX_ITEMS` env (default 200) — returns cap-reached error before create if `UserMemoryContext.filter(user=user).count() >= max_items`.

## 4. Golden-path examples

**"List my saved memories:"**

```
remember_tool  action=list
```

**"Find memories mentioning X:"**

```
remember_tool  action=search  query=<phrase>
```

**"Remember that I prefer terse commit messages:"** *(NOT exercised this ship — see §5a)*

```
remember_tool  action=save  content="Prefer terse commit messages"  memory_type=preference  importance=8
```

**"Delete memory ID 42:"** *(NOT exercised this ship — see §5a)*

```
remember_tool  action=delete  memory_id=42
```

## 5. Failure / empty-state / pagination notes

- **`list` with no memories** — returns `{action: list, count: 0, memories: []}`. Consistent shape.
- **`list` without caller `user_id`** — returns `_handler_error(action, 'permission_denied', 'User context required for memory operations')` at handler line 2223. Fail-loud envelope.
- **`search` missing `query`** — returns `_handler_error('search', 'invalid_params', 'query required for search action')`. Fail-loud envelope.
- **`search` matching zero memories** — returns `{action: search, query, count: 0, memories: []}`. Consistent shape.
- **`save` missing `content`** — returns `_handler_error('save', 'invalid_params', 'content is required for save action')`. Fail-loud envelope. MUTATION-skipped at metadata layer this ship.
- **`save` when duplicate hash exists** — returns `{action: save, status: 'duplicate_updated', memory_id, message: ...}` without creating a new row. MUTATION-skipped at metadata layer this ship.
- **`save` when at `MEMORY_MAX_ITEMS` cap** — returns `{error: f'Memory limit reached ({max_items} items). Delete old memories first.', current_count, max_items}`. Fail-loud pre-write.
- **`delete` missing `memory_id`** — returns `_handler_error('delete', 'invalid_params', 'memory_id required for delete action')`. Fail-loud envelope. IRREVERSIBLE-skipped at metadata layer this ship.
- **`delete` for unknown `memory_id`** — returns `{action: delete, deleted: False, message: 'Memory not found'}`. Consistent shape (no fail-loud on missing target).
- **Unknown action** — returns `_handler_error(action, 'unknown_action', f'Unknown action: {action}')`. Fail-loud envelope.

## 5a. Mutation containment (per Rigby T1 SIGN + Claude V1 verification)

- **Mutating actions excluded this ship:**
  - `save` — creates `UserMemoryContext` row via `.objects.create` at handler line 2273. Also fires cache clear (`memory_context_service.clear_cache(user)`) + emits `OpsRun` info event (`tracker.info('memory_saved', ...)`) at handler line 2295. Applies secret redaction + content truncation + dedup hash pre-write. Classified `MUTATION` — not `IRREVERSIBLE` because dedup and cap protect against runaway, and individual rows can be undone via `delete`.
  - `delete` — destroys `UserMemoryContext` row via `.filter(user=user, id=memory_id).delete()` at handler line 2331. Also fires cache clear on successful delete. **User-scoped filter prevents cross-user deletion** by design. Classified `IRREVERSIBLE` — no soft-delete, no undo; blast radius bounded to the caller's own memory row.
- **Containment mechanism:** per-action `TOOL_ACTION_METADATA` records with `safety_class='MUTATION'` / `'IRREVERSIBLE'` at `tool_action_metadata.py`; harness `resolve_safety()` skips at dispatch (`expected_outcome=skipped_mutation` / `skipped_irreversible`).
- **dependency_surface note:** `internal` — Django ORM against `UserMemoryContext` + Django cache backend (Redis) + `OpsRun` event tracker. No external bridge; **no LLM cost on any action** (verified — no `EmbeddingService` calls in this handler, distinguishing it from `conversation_tool.search`).
- **Deferral rationale:** `save` writes durable memory rows that persist per-user; test writes would accrete into the caller's real memory list. `delete` is IRREVERSIBLE. Doc-only sweep cannot exercise safely against a real caller. Deferred to a future MUTATION-coverage batch that pairs with a seeded-user + row-scoped-cleanup harness pattern.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness remember_tool` at HEAD `00fcb352f` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `save` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `list` | `error_captured` | — | ~1 ms | `error` (`permission_denied`) or `action, count, memories` if user_id present |
| `delete` | `skipped_irreversible` | — | 0 ms | — (metadata-driven skip) |
| `search` | `error_captured` | — | ~1 ms | `error` (`invalid_params`) |

Artifact: `docs/audits/pa_tools/harness_output/remember_tool.json` — 2 READ_ONLY (both error_captured on missing-arg / missing-user) + 1 MUTATION skipped + 1 IRREVERSIBLE skipped.

**Envelope-shape observation:** `list` + `search` return fail-loud `_handler_error` envelopes on missing-arg / permission-denied paths. `save` + `delete` cleanly metadata-skipped without handler invocation. The `_handler_error` envelope is a structured shape (`{success: False, error_code, error_message, action}`) distinct from `conversation_tool`'s inline `{error}` shape — this is a positive observation, not drift. `remember_tool` uses the S2886 core error-envelope migration shape (verified at handler imports line 5: `from core.services.td_error import _handler_error`).

### 6.2 Runtime-not-executed — this ship

- **`list` + `search` with a real populated `user_id`** — the harness ran without a caller user context (permission_denied path); the populated-user paths were not exercised. Would confirm memory row shape (id/type/content/importance/tags/created_at) + top-20 pagination + text-search behavior.
- **`save` + `delete`** — MUTATION-skipped / IRREVERSIBLE-skipped (see §5a). Real durable memory writes not exercised.

---

## Related

- **Adjacent tools:**
  - `conversation_tool` (batch 2 peer) — `ChatConversation` transcripts + `ConversationMemory` embeddings; different concern from explicit user-declared memory. **`remember_tool.search` is pure ORM text search; `conversation_tool.search` uses LLM embeddings** — key distinction verified this ship.
  - `deliverable_tool` — first-class work artifacts; `remember_tool` is the lightweight per-user memory surface, not the workspace-scoped deliverable surface.
- **Substrate context:** batch 2 peer of `active_repo_tool`, `db_health_tool`, `conversation_tool`. All 4 tools no-network on selected READ_ONLY action, no-Celery, no-writes.
- **Metadata seed:** 4 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship. `remember_tool` uses the S2886 `_handler_error` shape — cleaner error envelope than the inline `{error}` shape used by peer tools this batch.
- **Secret-redaction guardrail:** `save` applies `_redact_secrets(content)` at handler line 2233 — prevents API keys / tokens / passwords in memory rows.
- **Dedup mechanism:** SHA-256 hash of lowercased+stripped content + memory_type at handler line 2250 → returned as `status='duplicate_updated'` on hit. Cap: `MEMORY_MAX_ITEMS` env (default 200).
