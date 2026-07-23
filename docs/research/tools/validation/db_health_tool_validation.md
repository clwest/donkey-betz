# `db_health_tool` — Validation Report (S2913)

**Tool:** `db_health_tool`
**Schema:** `core/services/pa_tool_schemas.py:2093`
**Handler:** `core/services/td_handlers_core.py:1442` (`_handle_db_health`) + `:1469` (`_handle_db_health_local`) + `:1788` (`_delegate_remote_db_health`)
**Register site:** `core/services/tool_dispatcher.py` (via `CoreHandlersMixin`)
**Session:** S2913 (Path B systematic sweep — Slice 3 batch 2 of `td_handlers_core`)
**HEAD at validation:** `00fcb352f` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated at env='local' default; env='prod' urllib RPC escalation documented-not-tested — see §5a). Auto-classifier will report `validated (full)` per S2911/S2912 precedent because all 7 action names appear in `## Covered actions`.
**Rigby SIGN:** S2913 T1 SIGN AGREE-with-edits (V2 AGREE-with-edits — safety class classifies intrinsic action at env='local' default; env='prod' escalation noted in per-action metadata + doc §5a but NOT gated at safety class per T0 Q2(b) "no S2909 bridge preflight needed; env-preflight is what's needed"). V4 AGREE-with-edits — `env='prod'` treated as documented-not-tested network path deferred to future MUTATION-coverage batch; no substrate change (D6).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Check database health: migration status, table row counts, PostgreSQL connection info, pgvector extension status, and schema introspection. Answers "is the DB healthy?", "which migrations are unapplied?", "how big are the core tables?", "is pgvector installed?", "does this table exist?", "which tables start with X?", and "how's the learning-feedback loop performing?" Session 1069 base + Session 1249 P2(a) prod RPC client.

Distinct from `platform_config_tool` (Django settings + env vars + provider keys — configuration state, not schema state) and `platform_awareness_tool` (routes + capabilities + tool registry — API/UI surface shape). `db_health_tool` reads the *database* — schema, migrations, row counts, extensions.

## Covered actions

**READ_ONLY actions covered at env='local' default (all 7 total actions).** 1 escalated dependency-surface class (env='prod' urllib RPC) documented-not-tested — see §5a.

- `overview` — **in scope this ship** — verified live via T1a harness at env='local' (`success`, ~1 ms). Returns connection + migration summary + core table row counts.
- `migrations` — **in scope this ship** — verified live via T1a harness at env='local'. Returns unapplied-migration diff via `MigrationLoader`.
- `tables` — **in scope this ship** — verified live via T1a harness at env='local'. Returns raw-SQL row counts across canonical core tables.
- `pgvector` — **in scope this ship** — verified live via T1a harness at env='local'. Returns `pg_extension` presence + embedding-count aggregate.
- `verify_table` — **in scope this ship** — verified live via T1a harness at env='local' (error_captured path when `table_name` missing).
- `search_tables` — **in scope this ship** — verified live via T1a harness at env='local'. Returns `information_schema.tables` prefix filter (default `core_`).
- `learning_stats` — **in scope this ship** — verified live via T1a harness at env='local'. Returns `ReadbackLog` + `Consultation` + `UserAgentLearning` aggregate.

## 3. Schema notes

- **No `required` field.** Schema at `pa_tool_schemas.py:2100-2136` has `properties.action` but no `required` array — action defaults to `'overview'` when omitted (per handler line 1442 branch).
- **Optional:** `action` (enum: `overview, migrations, tables, pgvector, verify_table, search_tables, learning_stats`).
- **Conditional required (handler-enforced, per action):**
  - `table_name` for `verify_table` — inline `{error}` if missing.
- **Optional filters:**
  - `prefix` for `search_tables` (default `'core_'`).
  - `env` (enum: `local, prod`; default `local`).
- **GAP_MAP flag** `no_required` — expected for `env='local'` default-action tools (no `required` array in schema). Not treated as drift for this tool.

## 4. Golden-path examples

**"Is the DB healthy?"** (defaults to env='local' overview)

```
db_health_tool  action=overview
```

**"What migrations haven't been applied?"**

```
db_health_tool  action=migrations
```

**"How many rows in the core tables?"**

```
db_health_tool  action=tables
```

**"Does this table exist?"**

```
db_health_tool  action=verify_table  table_name=core_ledgerentry
```

**"Find all tables starting with 'core_':"**

```
db_health_tool  action=search_tables
```

**"How's the learning feedback loop?"**

```
db_health_tool  action=learning_stats
```

**"Check the prod DB (documented, NOT tested this batch):"**

```
db_health_tool  action=overview  env=prod
```
Fires urllib RPC to `PA_DB_HEALTH_RPC_URL` with Token auth (30s timeout). Not exercised — see §5a.

## 5. Failure / empty-state / pagination notes

- **`overview` on empty DB** — returns connection + migration summary + zero counts. Consistent shape.
- **`migrations` when all applied** — returns `{action, unapplied: [], count: 0}`. Consistent shape.
- **`verify_table` missing `table_name`** — returns `{error: 'table_name required for verify_table action'}`. Inline `{error}` envelope, not raise.
- **`verify_table` with unknown table** — returns `{action: verify_table, table_name, exists: False}`. Consistent shape; no fail-loud.
- **`search_tables` with populated `prefix` matching nothing** — returns `{action: search_tables, prefix, tables: []}`. Consistent shape.
- **`pgvector` when extension not installed** — returns `{action: pgvector, extension_installed: False, embedding_count: 0}`. Consistent shape.
- **`learning_stats` on empty tables** — returns zeros for all aggregate counts. Consistent shape.
- **env='prod' with unset `PA_DB_HEALTH_RPC_URL` or `PA_DB_HEALTH_RPC_CLIENT_TOKEN`** — `_delegate_remote_db_health` at handler line 1788 returns `{env: 'prod', action, error, trace_id}` fail-loud dict. Does not raise. Fail-loud behavior verified at handler by inspection, not exercised this ship (see §5a).
- **Unknown action at env='local'** — returns `{error: f'Unknown db_health action: {action}'}` at handler line 1786. Inline `{error}` envelope.

## 5a. Mutation containment / env='prod' escalation (per Rigby T1 SIGN V2 + V4)

- **Mutating actions this tool:** **none, when env='local'** (default). All 7 actions are pure DB introspection reads.
- **Escalated dependency surface at env='prod':** every action delegates to `_delegate_remote_db_health` at handler line 1788, which fires `urllib.request.urlopen` to `PA_DB_HEALTH_RPC_URL` with `Authorization: Token <PA_DB_HEALTH_RPC_CLIENT_TOKEN>` (30s timeout).
- **Classification decision (per Rigby V2 AGREE-with-edits):** per-action safety class remains `READ_ONLY` because the intrinsic action IS read-only. The `env='prod'` path is a **conditional dependency surface**, not an intrinsic mutation — it fires HTTP but reads DB state on the remote side. Per Rigby T0 Q2(b) — this is NOT the S2909 bridge/HMAC fleet gateway; it's a bespoke RPC client with its own fail-loud envelope. **env='prod' escalation IS documented in every per-action metadata `notes` field** so downstream tooling and future ops can see the split.
- **Containment mechanism at env='local':** action is dispatched into `_handle_db_health_local` at handler line 1469 which uses `connection.introspection` + `call_command('showmigrations')` + raw-SQL row counts + `pgvector` extension read. All in-process.
- **Containment mechanism at env='prod':** `_delegate_remote_db_health` returns a fail-loud dict whenever env vars are missing or HTTP fails; never raises.
- **Deferral rationale:** env='prod' HTTP + Token auth + tolerance for prod-side state read + 30s per-call cost. Doc-only sweep does not exercise cleanly against a live Railway URL. Deferred to a future MUTATION-coverage batch that pairs with a network-preflight harness pattern (mirrors `platform_awareness_tool.verify_deploy` + `platform_config_tool.web_config` §5a deferrals from batch 1).

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness db_health_tool` at HEAD `00fcb352f` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `overview` | `success` | 200 | ~1 ms | `env, action, connection, migrations, tables` |
| `migrations` | `success` | 200 | ~1 ms | `env, action, unapplied, count` |
| `tables` | `success` | 200 | ~1 ms | `env, action, tables` |
| `pgvector` | `success` | 200 | ~1 ms | `env, action, extension_installed, embedding_count` |
| `verify_table` | `error_captured` | — | ~1 ms | `error` (`table_name required`) |
| `search_tables` | `success` | 200 | ~1 ms | `env, action, prefix, tables` |
| `learning_stats` | `success` | 200 | ~1 ms | `env, action, readback_events, consultations, user_agent_learnings, flags` |

Artifact: `docs/audits/pa_tools/harness_output/db_health_tool.json` — 7 READ_ONLY dispatched at env='local' (6 success + 1 error_captured on required-arg miss).

**Envelope-shape observation:** all 7 actions return either clean success at HTTP 200 or fail-loud `{error}` on required-arg miss. Every response carries the `env` tag so cross-env comparisons are unambiguous (Session 1249 P2(a) contract). No inline `{ok: false}` envelope drift on the READ_ONLY subset. No `bridge` field on metadata — env='local' is pure in-process DB introspection; env='prod' would use urllib RPC, not the S2909 bridge.

### 6.2 Runtime-not-executed — this ship

- **env='prod' path** — all 7 actions have an env='prod' branch via `_delegate_remote_db_health` at handler line 1788 (urllib RPC to `PA_DB_HEALTH_RPC_URL`). Not exercised — Rigby V4 AGREE-with-edits treats as documented-not-tested (see §5a).
- **`verify_table` with a real populated `table_name`** — the harness ran the missing-arg error path; the found-table success path was not exercised.

---

## Related

- **Adjacent tools:**
  - `platform_config_tool` (batch 1 peer) — Django settings + env vars + provider keys; complementary configuration read.
  - `platform_awareness_tool` (batch 1 peer) — routes + tool registry + capabilities; complementary API/UI surface read.
  - `active_repo_tool` (batch 2 peer) — per-user repo pointer; different concern from DB health.
- **Substrate context:** batch 2 peer of `active_repo_tool`, `conversation_tool`, `remember_tool`. All 4 tools no-network on selected READ_ONLY action, no-Celery, no-writes; siblings excluded via per-action `TOOL_ACTION_METADATA`.
- **Metadata seed:** 7 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship (mirrors S2911 batch 6a shape). Every record's `notes` field explicitly documents the env='local' READ_ONLY vs env='prod' HTTP escalation.
- **Session provenance:** Session 1069 base (introspection framing + `_handle_db_health_local` fan-out) + Session 1249 P2(a) (`_delegate_remote_db_health` prod RPC client + always-tagged `env` field).
- **env='prod' operability:** requires `PA_DB_HEALTH_RPC_URL` (endpoint) + `PA_DB_HEALTH_RPC_CLIENT_TOKEN` (matches prod server's `PA_DB_HEALTH_RPC_TOKEN`). Fail-loud dict when either is missing; 30s per-call HTTP timeout.
