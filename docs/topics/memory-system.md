# Memory System

> **Operator-facing guide.** How Rigby remembers things, which layer holds what, and how to use the surfaces safely.
> **Written:** Session 2986 (2026-07-26) as part of spec `ba968ac1` PR1.

---

## The three memory layers

The platform stores memory in three distinct places. Each has a different lifetime, retrieval path, and audit surface. Do not confuse them.

| Layer | Model | Written by | Retrieved by | Lifetime |
|---|---|---|---|---|
| **UserMemoryContext** | `core.models.UserMemoryContext` | `remember_tool.save` (explicit "remember X" from Chris) + PA proactive detection | `MemoryContextService.get_prompt_context()` at PA turn start | Persistent; user-curated; cap `MEMORY_MAX_ITEMS` (default 200) |
| **ConversationMemory** | `core.models.ConversationMemory` | Auto-write at PA turn close | pgvector semantic search when user references past conversations | Persistent; not user-curated; embedding-indexed |
| **AgentMemory** (per-agent scratchpad) | `core.models_unified_system.AgentMemory` | Agent-side writes during execution | Injected into agent prompts | Per-agent; safety-class filtered |

**PR1 scope** covers the `UserMemoryContext` layer only. Trace/hygiene/preflight for the other two layers are PR2.

## remember_tool — quick reference

`remember_tool` is Rigby's PA tool surface on top of `UserMemoryContext`. Actions:

- `save` — write a new memory (or bump importance on an existing duplicate)
- `list` — top 20 by importance/recency
- `search` — case-insensitive substring match on `content`
- `delete` — by memory id

### save contract

Input:
- `content` **(required)** — the thing to remember, ≤500 chars stored. Longer input is truncated (see below).
- `memory_type` — one of `preference | goal | constraint | instruction | decision | context | skill | project`; default `preference`.
- `importance` — 1..10; default 7; clamped.
- `tags` — optional list of strings.

Return (success):
```json
{
  "action": "save",
  "status": "created",           // or "duplicate_updated"
  "memory_id": 12345,
  "memory_type": "preference",
  "importance": 7,
  "truncated": false,             // true if content was > 500 chars
  "original_len": 87,             // pre-truncation length
  "message": "Remembered: ..."
}
```

`status='duplicate_updated'` means dedupe hit — a memory with the same normalized content + memory_type already exists. Importance is bumped if the new value is higher; no new row is written.

### save contract — error envelopes

Every error return uses the S2879 shape `{success:false, error_code, error, action, ...fields}`:

| `error_code` | Trigger |
|---|---|
| `permission_denied` | No user context (`user_id=None`) |
| `invalid_params` | `save` without `content`, `delete` without `memory_id`, `search` without `query` |
| `cap_hit` **(S2986)** | User already has `MEMORY_MAX_ITEMS` memories; includes `current_count` + `max_items` |
| `unknown_action` | Action string not in the valid set |

### Oversized content — entrypoint-side gate (S2986)

If Rigby's LLM sends a `remember_tool.save` call whose raw `arguments` JSON exceeds 3000 characters, the PA agentic loop rejects it **before `json.loads`** with a typed envelope:

```json
{
  "ok": false,
  "error_code": "REMEMBER_CONTENT_TOO_LONG",
  "tool_name": "remember_tool",
  "message": "remember_tool.save content is too long. Summarize the memory to under 500 characters before saving...",
  "meta": {"arguments_len": 4123, "raw_max": 3000},
  "retry_hint": {"recommended_action": "remember_tool.save", "max_content_chars": 500}
}
```

**Why:** the LLM's tool-call arguments string is streamed one token at a time. When content is long, the args string can be truncated mid-stream by the output_tokens budget, producing a `TOOL_ARGS_JSON_MALFORMED` at the parse step. The pre-parse gate catches this earlier with a targeted retry hint. Threshold: 3000 raw chars ≈ 1500 chars of content plus JSON overhead. The handler-side clamp is 500 chars regardless, so anything above 1500 would be truncated on write anyway.

## Memory retrieval — how PA uses it

On every PA turn, `unified_pa_entrypoint._build_system_prompt` calls `MemoryContextService.get_prompt_context(user)` and appends it to the system prompt under a neutral header:

```
PERSISTENT USER CONTEXT (use only if relevant; do not mention unless asked):
<memory context block>
```

The service returns preferences, goals, and recent decisions with decay weighting (`e^(-age_days/21)`), capped at `MEMORY_MAX_TOKENS` (default ≈500 tokens = 2000 chars). Injection is quiet-by-default: the model should use it when relevant and NOT tell the user "you asked me to remember X" unless asked.

Every injection emits an OpsRun event:
```
memory_injected: {user_id, chars}
```

## Cap enforcement

`MEMORY_MAX_ITEMS` (env var, default `200`) caps the total number of `UserMemoryContext` rows per user. When hit, `remember_tool.save` returns the `cap_hit` error envelope. **PR1 does not implement supersede or hygiene** — those are PR2. For now, `remember_tool.delete <memory_id>` is the only way to make room.

## Auto-memory (auth-driven persistence)

Separate from `remember_tool`, the PA also runs `_detect_memory_intent()` on incoming user messages and, when it matches phrases like "remember X" or "note that I…", it saves to `UserMemoryContext` directly. This is the "user says remember, PA writes it" path — the LLM does not need to call `remember_tool` for these to persist.

## What's NOT in PR1 (see PR2)

- **MemoryUtilizationTrace** — will answer "did memory influence this response?" with layer-tagged retrieved/injected/used IDs.
- **`memory_hygiene_audit` management command** — surface stale + conflict candidates; supersede semantics.
- **Supersede fields on `UserMemoryContext`** — `is_active`, `superseded_by`, `superseded_at` migration.
- **Non-PA preflight** — currently only PA turn calls `MemoryContextService`. Direct LLM callers (e.g. `ProjectBuilderOrchestrator`) bypass it. PR2 wires MVP into `ProjectBuilderOrchestrator`; broader sweep is a follow-up spec.

## Related surfaces

| Surface | Purpose | Where |
|---|---|---|
| `remember_tool` PA tool | Rigby-callable save/list/search/delete | `core/services/td_handlers_core.py:_handle_remember` |
| `MemoryContextService` | Retrieval + prompt formatting + decay weighting + cache | `core/services/memory_context_service.py` |
| Auto-memory detector | Regex intent → auto-save | `core/services/unified_pa_entrypoint.py:_detect_memory_intent` |
| S2986 tests | Handler happy-path + dedupe + cap-hit + truncation | `core/tests/test_s2986_remember_tool.py` |
| S2886 tests | Handler error envelopes (5 sites) | `core/tests/test_s2886_core_error_envelope.py` |

## Session provenance

- **S2886** (2026-07-21) migrated the 5 handler-side error branches to the S2879 `_handler_error` envelope.
- **S2986** (2026-07-26, this arc) fixed the `remember_tool.save` reliability gaps: `cap_hit` envelope migration, save-return `status`/`truncated`/`original_len` signaling, entrypoint-side oversized-content gate, PA prompt header rename, happy-path test coverage, this doc.
- **S2986 PR2** (queued): trace + hygiene + supersede + narrow preflight.
