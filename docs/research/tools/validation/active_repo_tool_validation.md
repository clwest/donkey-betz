# `active_repo_tool` — Validation Report (S2913)

**Tool:** `active_repo_tool`
**Schema:** `core/services/pa_tool_schemas.py:991`
**Handler:** `core/services/td_handlers_core.py:89` (`_handle_active_repo`)
**Register site:** `core/services/tool_dispatcher.py` (via `CoreHandlersMixin`)
**Session:** S2913 (Path B systematic sweep — Slice 3 batch 2 of `td_handlers_core`, second batch this session)
**HEAD at validation:** `00fcb352f` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; 2 MUTATION actions `set` + `clear` explicitly excluded — see §5a).
**Rigby SIGN:** S2913 T1 SIGN AGREE-with-edits (V1 side-effect-free scan clean — `get` is pure cache+ORM read with no durable writes; cache backend metrics treated as acceptable incidental instrumentation).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Persist or read the "currently working in repo X" pointer for a user, so multi-repo Claude Code workflows don't need to re-state context every turn. Per-user Redis-cached pointer with 7-day TTL. `set` scopes a conversation to a repo; `get` checks current scope; `clear` drops the pointer. Session 1119 carryover #4.

Distinct from `workspace_tool` (which manages workspaces as first-class entities — list/lookup/activate/create/delete). `active_repo_tool` is a *pointer* to a `ProjectWorkspace` — its state lives entirely in Redis with a 7-day TTL, and never affects Donkey Betz's own workspace (u-d-b stays the global active workspace by design).

## Covered actions

**READ_ONLY actions covered only (1 of 3 total actions).** 2 MUTATION actions (`set` + `clear` — excluded — see §5a) are out of scope for this ship.

- `get` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms). Returns `{action, active_repo, set, cache_key}` — `active_repo` is either the cached ProjectWorkspace snapshot dict or `None`.
- `set` — **mutation — deferred to future MUTATION-coverage batch** — see §5a
- `clear` — **mutation — deferred to future MUTATION-coverage batch** — see §5a

## 3. Schema notes

- **Required:** `action` (enum: `set, get, clear`).
- **Conditional required (handler-enforced, per action):**
  - `repo` for `set` (workspace name / repo_id) — inline `{ok: False, error}` if missing or if ProjectWorkspace lookup misses.
- **Optional:** none beyond `repo` for `set`.
- **`repo` lookup order (`set` only):** first `ProjectWorkspace.objects.filter(name=repo, user_id=user_id).first()`, then falls back to `.filter(name=repo).first()` if the user-scoped lookup misses. This fallback surfaces platform-shared repos to any operator with the name.

## 4. Golden-path examples

**"Which repo am I currently scoped to?"**

```
active_repo_tool  action=get
```

Response: `{action: get, active_repo: {repo_id, workspace_id, name, root_path, set_at, ttl_seconds} | None, set: bool, cache_key}`.

**"Scope this conversation to character-os:"** *(NOT exercised this ship — see §5a)*

```
active_repo_tool  action=set  repo=character-os
```

**"Drop the active repo pointer:"** *(NOT exercised this ship — see §5a)*

```
active_repo_tool  action=clear
```

## 5. Failure / empty-state / pagination notes

- **`get` when no pointer is set** — returns `{action: get, active_repo: None, set: False, cache_key}`. Consistent shape; no fail-loud.
- **`set` missing `repo`** — returns `{action: set, ok: False, error: 'Provide payload.repo (workspace name / repo_id)'}`. Inline `{ok: False, error}` envelope, not raise.
- **`set` with unknown repo name** — returns `{action: set, ok: False, error: f'No ProjectWorkspace named {repo!r} found'}`. Inline `{ok: False, error}` envelope.
- **`clear` when nothing was cached** — returns `{action: clear, cleared: False, cache_key}`. Consistent shape (`cleared: False` reports the empty-state; the delete call is still executed but is a no-op).
- **Unknown action** — returns `{action, ok: False, error: 'Unknown action ... Use set / get / clear.'}` at handler line 153-157. Inline `{ok: False, error}` envelope.

## 5a. Mutation containment (per Rigby T1 SIGN)

- **Mutating actions excluded this ship:**
  - `set` — writes to Redis cache via `cache.set(cache_key, value, _ACTIVE_REPO_TTL_SECONDS)` at handler line 150. TTL is 7 days. Classified `MUTATION` — not `IRREVERSIBLE` because the TTL expiry auto-clears; the operation itself only stores a snapshot (`{repo_id, workspace_id, name, root_path, set_at, ttl_seconds}`). Blast radius is per-user + reversible via `clear` or TTL expiry.
  - `clear` — writes to Redis cache via `cache.delete(cache_key)` at handler line 121. Classified `MUTATION` — not `IRREVERSIBLE` because the operation just drops the pointer; downstream tools default to the global active workspace when the pointer is absent.
- **Containment mechanism:** per-action `TOOL_ACTION_METADATA` records with `safety_class='MUTATION'` at `tool_action_metadata.py`; harness `resolve_safety()` skips at dispatch (`expected_outcome=skipped_mutation`).
- **dependency_surface note:** `internal` — Django cache backend (Redis) + `ProjectWorkspace` ORM. No external bridge.
- **Deferral rationale:** `set` and `clear` are per-user state mutations. Doc-only sweep should not commit real Redis state or drop a real operator's pointer. Deferred to a future MUTATION-coverage batch that pairs with an isolated-user-context harness pattern.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness active_repo_tool` at HEAD `00fcb352f` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `get` | `success` | 200 | ~1 ms | `action, active_repo, set, cache_key` |
| `set` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `clear` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |

Artifact: `docs/audits/pa_tools/harness_output/active_repo_tool.json` — 1 READ_ONLY dispatched + 2 MUTATION skipped.

**Envelope-shape observation:** `get` returns clean success at HTTP 200. `set` + `clear` cleanly metadata-skipped without handler invocation. No inline `{ok: false}` envelope drift on the READ_ONLY subset — `set` and `clear` DO use `{ok: false, error}` inline envelopes on their fail paths (see §5), which is drift-shape flagged as a broader ledger candidate but NOT specific to this tool.

### 6.2 Runtime-not-executed — this ship

- **`get` with an actual populated pointer** — the harness ran with an empty cache; the branch returning the full snapshot dict was not exercised.
- **`set` + `clear`** — MUTATION-skipped (see §5a). Real cache writes not exercised.

---

## Related

- **Adjacent tools:**
  - `workspace_tool` — first-class workspace management (list/lookup/activate/create/delete); `active_repo_tool` is a pointer TO a workspace, not a workspace manager itself.
  - `platform_config_tool` (batch 1 peer) — configuration snapshot including `service_context` env var; different concern from per-user repo scope.
- **Substrate context:** first tool in Slice 3 batch 2. Batch 2 peers: `db_health_tool` (7-action mixed with env-dependent MUTATION escalation), `conversation_tool` (5-action mixed R/M with LLM cost on `search`), `remember_tool` (4-action mixed R/M/IR).
- **Metadata seed:** 3 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship (mirrors S2911 batch 6a shape; no `TOOL_DEFAULTS` entry). Batch-uniform per-action pattern per Rigby T1 V2 explicit-action-pinning directive.
- **Session 1119 provenance:** the carryover-#4 framing + `ProjectWorkspace` pointer semantics + 7-day TTL + `_active_repo_cache_key(user_id)` helper are all Session 1119 arc.
- **Multi-repo workflow context:** `active_repo_tool` is the handshake substrate for the Fleet foundry pattern (docs/handoffs/SESSION_2842_S2841_RATIFIED_D0_D6.md) — enables Claude Code to run across the 7-sibling-app fleet without re-scoping every turn.
