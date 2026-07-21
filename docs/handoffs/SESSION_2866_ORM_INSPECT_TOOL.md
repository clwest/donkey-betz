# Session 2866 — Bounded ORM row inspector tool shipped

**Date:** 2026-07-21
**Session pin:** `pa-8005b98ba0524999` (label `s2866-orm-inspector-tool`)
**PR:** [#3351](https://github.com/clwest/donkey-betz-platform/pull/3351) `f52c1d854`
**Slate:** Rigby Tool Gap Ledger #3 / adjacent deliverable `b5a22ea7`

---

## What shipped

`orm_inspect_tool` — read-only, allowlist-scoped Django ORM row inspection. Internal-DB counterpart to S2865's `web_fetch_tool` (external endpoint verify → this = internal DB verify). Closes the **S2845-class false-negative gap** where a tool surface reports 'no data' but rows exist under a different filter path (140 AI-community clusters found via ORM after enum-restricted `source` param returned 0).

Rigby can now self-verify persisted state instead of a Claude drop-to-Django-shell trip.

### Files touched (5)

| File | Δ | Purpose |
|---|---|---|
| `core/services/pa_tool_schemas.py` | +100 | `orm_inspect_tool` schema after `web_fetch_tool` (schema 117 total) |
| `core/services/td_handlers_agents.py` | +390 | `_handle_orm_inspect` handler next to `_handle_web_fetch` |
| `core/services/tool_dispatcher.py` | +2 | Registration (handler 160 total) |
| `core/tests/test_s2866_orm_inspect_tool.py` | new (414) | 36 pytest cases across 9 classes; 36/36 pass in 113ms |
| `tools/pa_local.sh` | ±1 | Session pin bump `pa-ba8b342e1f12484d` → `pa-8005b98ba0524999` |

## Design contract (post-SIGN)

### Actions (4)

- `list_models` — enumerate the 8-model allowlist with sensitivity flags.
- `describe_model` — return field types, JSONField/TextField flags, sensitive-by-name flags for one model.
- `get` — fetch one row by pk, return projected fields.
- `filter` — fetch N rows via filter_kwargs (default 20, max 200), return total_matching + rows.

### v1 allowlist (8 models)

`SignalCluster`, `Deliverable`, `Initiative`, `LLMCallLog`, `Agent`, `AutopilotAction`, `Budget`, `OpsRun`.

High-sensitivity (default `include_json_fields=false`): `LLMCallLog`, `AutopilotAction`, `OpsRun`.

### Safety layers

1. **Read-only.** No `.save`/`.update`/`.delete` — queryset construction only.
2. **No FK traversal.** Deep `__` chains rejected (single lookup segment max).
3. **Two-layer sensitive-field detection:**
   - Composite substrings: `api_key`, `access_key`, `refresh_token`, `id_token`, `client_secret`, `private_key`, `ssh_key`, `rsa_key`, `set_cookie`, `auth_token`, `session_token`, `session_key`, `bearer_token`, `webhook_secret`, `webhook_key`, `pem_key`, `pem_cert`, `auth_header`, `authorization_header`, `x_api_key`, `openai_key`, `anthropic_key`, `github_pat`.
   - Word-boundary matching against `SENSITIVE_WORDS` after underscore-split: `password`, `secret`, `authorization`, `token`, `apikey`, `cookie`, `credential`, `creds`, `session`, `csrf`, `xsrf`, `signature`, `salt`, `nonce`, `encrypted`, `encryption`.
4. **Recursive JSON key redaction** on JSONField values (denylist: `token`, `api_key`, `authorization`, `cookie`, `secret`, `credential`, `password`, `refresh_token`, `id_token`, `private_key`, `auth`, `signature`, `bearer`, `session_token`, `client_secret`, `set_cookie`).
5. **Query-cost guardrails:**
   - Per-model `expensive_text_fields` reject `contains`/`icontains` (e.g., `Deliverable.content`, `Initiative.description`, `LLMCallLog.response_preview`).
   - `in` list capped at 100.
   - Row limit clamped to `[1, 200]`.
   - Per-field string truncation at 4KB with `<truncated:Nb>` marker.
6. **Safe lookup allowlist:** `exact`, `iexact`, `isnull`, `gt`, `gte`, `lt`, `lte`, `contains`, `icontains`, `startswith`, `istartswith`, `in`, `has_key`, `has_keys`.
7. **`order_by` allowlist:** `id`, `created_at`, `updated_at`, `detected_at`, `started_at`, `finished_at`, `first_seen`, `last_seen`, `signal_window_start`. Default `-created_at` or nearest-available, fallback `-id`.

## Working loop shape (3 SIGN cycles)

### Cycle 1 — pre-code SIGN (Rigby dispatch, tool-grounded per `feedback_verify_rigby_tool_runs_before_trusting_sign`)

Rigby ran `deliverable_tool.detail(id='b5a22ea7')` and `repo_tool.search(query='db_health_tool')` to validate:
- **Q1 F-AGREE with 2 gaps:** ledger scope matched; gaps = missing `order_by` param + missing per-model policy dict.
- **Q2 F-AGREE minor tweaks:** allowlist directionally right; suggested spider-model additions deferred to v2.
- **Q3 F-BLOCKING:** field-name blocklist too narrow; JSONField recursion + token-shape redaction required.
- **Q4 F-AGREE:** filter lookup surface right; add `startswith`/`istartswith`; tighten `contains`/`icontains` on expensive fields.
- **Q5 F-AGREE:** no existing PA tool overlaps; `db_health_tool` is adjacent (health/diagnostics), not row-level.
- **Q6 F-AGREE zoom-out:** bake in per-model policy, query-cost guardrails, structured redaction + audit logging, traversal constraints as first-class invariants.

All Q1/Q3/Q4/Q6 folds applied before writing code.

### Cycle 2 — post-code SIGN round 1 (Rigby live dispatch, 4 blocking cases)

- **Case 1 (list_models):** F-AGREE — 8 models, correct sensitivity flags.
- **Case 2 (S2845 has_key demo):** F-BLOCKING (framing only) — 0 rows returned. Ground-truth ORM check: 0 SignalClusters actually have `huggingface` in `source_breakdown` (827 total; sample keys are `kickstarter`/`producthunt`/`wired`/`theverge`/etc.). **Tool was doing its job — proving the persisted-state truth.** No code change needed; re-verification with real data followed in cycle 3.
- **Case 3 (LLMCallLog sensitive default):** F-BLOCKING (real bug) — `prompt_tokens`/`completion_tokens`/`total_tokens` returned `<redacted:field_name>` because naive `'token' in name.lower()` substring-matched. Fix applied: word-boundary matching. Regression test class `SensitiveFieldNameMatchingTests` added (3 tests).
- **Case 4 (reject paths):** F-AGREE — all rejects (non-allowlist, unsafe lookup, deep chain, expensive text field) return correct `ok=false`.

### Cycle 3 — post-code SIGN round 2 (verify fix + real-data spot check)

- **Case A (redaction fix):** F-AGREE — `describe_model LLMCallLog` shows `prompt_tokens`/`completion_tokens`/`total_tokens` all `sensitive_by_name=false`.
- **Case B (composite coverage):** F-AGREE with 2 additions — `authorization_header`, `session_key`. Folded.
- **Case C (real S2845 shape):** F-AGREE — `filter model='SignalCluster' filter_kwargs={'source_breakdown__has_key': 'hackernews'}` returned `total_matching=65`, rows populated with actual `source_breakdown` values including hackernews.

**Zoom-out asks (per `feedback_zoom_out_ask_per_rigby_sign`):**
- Round 1: FIRST verification workflow to rewrite → `SignalCluster` spot-check filters (JSONField key existence, confidence thresholds, detected_at windows). SECOND gap surfaced → aggregate group-by counts (next diagnostic rung after row inspection).
- Round 2: slip-through failure mode → euphemistic field names (`opaque`/`blob`/`payload`), secrets inside JSON keys with innocuous parent field name, provider-specific names. Mitigation shape already in v1 (JSONField-omission-default + recursive JSON key redaction as second net).

## v2 deferred (folded in handler docstring)

- Token-shape heuristic redaction (JWT-ish/Bearer/long-base64).
- Per-model per-field lookup allowlist + per-model `order_by` allowlist.
- Multi-tenant `workspace_id` enforcement (deferred per single-tenant pre-prod context; flip to required if multi-tenant ever ships).
- Euphemistic-name coverage (opaque/blob/payload — mitigated by JSONField omission-default on sensitive models until per-model `allowed_fields` ships).
- Aggregate group-by counts (next diagnostic rung after row inspection).

## Runtime impact

- **117 total PA tool schemas** (was 116); `_tool_handlers` count 160.
- Rigby has a second F-DELEGATED gap closure — external HTTP (S2865) + internal DB (S2866) both self-serviced.
- Post-merge live dispatches proved E2E: 8 models discoverable, `describe_model` returns clean field types, `filter` with `has_key` finds real rows, all reject paths correct.

## Working loop observations

- `feedback_verify_rigby_tool_runs_before_trusting_sign` — worked as designed all 3 cycles. Pre-code Rigby did real `deliverable_tool` + `repo_tool` runs; round 1 caught a real over-match bug via live `describe_model` inspection.
- `feedback_zoom_out_ask_per_rigby_sign` — produced substantive value both post-code rounds. Named the "aggregate counts" next-rung gap + euphemistic-name slip-through class. Both folded as v2 docstring notes.
- `feedback_local_truth_no_production` — recycle-before-live-verify + recycle-after-merge (PLAYBOOK-7.4.4) both honored.
- `feedback_gh_pr_merge_admin_until_billing_fixed` — used `--admin` flag on merge.
- Working loop shape: 3 SIGN cycles is one more than S2865's 2. First real bug caught by Rigby's post-code live dispatch (over-redaction) — worth ~15 min extra vs shipping broken redaction. Playbook-style loop cost was well-spent.

## Twin-pointer for S2866 artifacts (per `feedback_twin_pointer_docs_at_boundaries`)

**Repo canonical (Claude-authored):**
- PR #3351 `f52c1d854` — `orm_inspect_tool` schema + handler + registration + tests
- This handoff — `docs/handoffs/SESSION_2866_ORM_INSPECT_TOOL.md`
- Refresh — `00-START-NEXT-SESSION.md`

**Workspace canonical (Rigby-authored per `feedback_rigby_writes_workspace_deliverables`):**
- Rigby Tool Gap Ledger #3 (deliverable `b5a22ea7`) → marked Shipped, `shipped_in_pr_3351`.
- S2866 close ratification envelope → workspace `b4503364-2573-4401-9e28-61a739e0ce50` (Donkey Betz).

Session pin `pa-8005b98ba0524999` (labeled `s2866-orm-inspector-tool`) RETIRES at S2866 close.
