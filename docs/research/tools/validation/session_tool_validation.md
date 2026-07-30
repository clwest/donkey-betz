# `session_tool` — Validation Report

**Tool:** `session_tool`
**Schema:** `core/services/pa_tool_schemas.py:4740-4821`
**Register site:** `core/services/tool_dispatcher.py:563`
**Main handler:** `core/services/td_handlers_core.py:3873-4175` (`_handle_session`)
**Downstream service:** `core/services/session_health_service.py:280 lines` (`get_session_health`)
**Session validated:** S2728 (Batch A tool 2 of 5)
**HEAD at validation:** `9d158805` + Batch A tool 1 uncommitted patches
**Reviewer:** Claude (Opus 4.7, 1M context)
**Rigby cross-check:** deferred (regression tests suffice; §10.1 step 12 discretion)
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch A tool 2 of 5). Trace + 2 patches + regression tests complete; 7 new regression tests + 33 existing session_tool tests + 71 adjacent tool 1 tests all passing at HEAD.

---

## 1. Intended purpose (per schema description)

*"Manage conversation sessions: check conversation health/freshness, create a fresh conversation, or list recent conversations. Use when asked about session health, context drift, whether to start fresh, creating a new conversation, or listing past conversations. Also use proactively when you notice the conversation is getting long or drifting."*

## Covered actions

All 7 schema actions covered.

- `health_check` — read — returns session-health payload from `get_session_health` service (drift metrics, message count, freshness verdict).
- `list_recent` — read — enumerates recent conversation pins with optional limit/window filters.
- `whoami` — read — returns `{username, conversation_id, conversation_owner_match, is_active}`. Ownership check per MEMORY `feedback_pa_local_verify_ownership`.
- `create_fresh` — mutation — mints a fresh conversation pin. Used for SIGN-isolation dispatches + long-context rotation.
- `retire` — mutation — retires an active pin (canonical pin-cleanup path per `feedback_session_tool_retire_works`).
- `set_active` — mutation — flips `is_active` on a pin (used for pin activation post-mint).
- `seed` — mutation — seeds conversation context (historical shape; less used).

## 2. Rigby's belief (per schema + MEMORY rules + prior conversations)

Rigby believes she has 7 actions across `session_tool`. Two MEMORY rules crystallize load-bearing beliefs:

- **`feedback_session_tool_retire_works`** — earlier stale belief that `retire` did not exist was corrected S1301; retire is now the canonical pin-cleanup path.
- **`feedback_pa_local_verify_ownership`** — before any `tools/pa_local.sh` call, `whoami` must confirm `conversation_owner_match=true` and `username='donkeyking'`. Session 1098 lost half a Rigby record because this check wasn't done.

Rigby also uses `create_fresh` frequently to mint SIGN-isolation pins (per playbook §11 fresh-isolation discipline).

## 3. Schema claim (verbatim capture)

**Required parameter:** `action` (enum, 7 values).

**Action enum:** `health_check, create_fresh, list_recent, whoami, retire, set_active, seed`.

**Optional parameters (6 total):**
- `conversation_id` — target conversation; defaults to current for read-only actions; required for retire/set_active/seed.
- `title` — optional for `create_fresh`.
- `carry_forward_summary` — for `create_fresh`; text carried to starter prompt.
- `limit` — `list_recent` default 10.
- `force` — `retire` only; required when retiring the currently-bound thread.
- `content` — `seed` only; REQUIRED non-empty; explicit whitespace/empty rejection at handler edge.

**Schema-declared discipline (defenses baked into descriptions):**
- `force` gates self-retire of bound thread.
- `content` explicitly rejects empty/whitespace (Session 1247 Finding-2 class).
- Retire is scoped to conversation_id + user_id (row-level scope).

## 4. Handler behavior (traced through code)

### 4.1 Dispatch entry (td_handlers_core.py:3873)

- Line 3875: `action = payload.get('action', 'health_check')` — **DEFAULT ACTION IS `health_check`** if unset. Schema `required` violation same as F-D-1 (deliverable_tool). **F-S-2.**
- Handler is directly registered (no gateway/wrapping layer analog to `_handle_deliverable_direct`).

### 4.2 Action: `health_check` (line 3877-3888)

- Line 3880: reads `conversation_id` from payload OR falls back to `getattr(self, '_current_conversation_id', None)` — this attribute is NOT ASSIGNED anywhere in the codebase per line 3907-3913 own commentary. Legacy defensive fallback that always returns None. **F-S-4.**
- Line 3881-3882: returns `{'error': ...}` without `ok: false` field. **F-S-1 (error envelope inconsistency).**
- Delegates to `session_health_service.get_session_health(conversation_id, user_id)` which computes score/recommendation/signals/reasons/auto_summary/starter_prompt.
- Response format: `{'action': 'health_check', **health}` — spreads health dict.
- Existing test coverage: 3 tests in `test_session_tool_health_check_and_create_fresh.py`.

### 4.3 Action: `create_fresh` (line 3890-3937)

- Line 3894: `new_id = f"pa-{uuid.uuid4().hex[:16]}"` — 16-hex-char truncated UUID with `pa-` prefix. **Not documented in schema.** No collision-detection loop (relies on uuid uniqueness within 16 chars; 2^64 space).
- Line 3895: title default `'New session'`.
- Line 3899-3905: **Writes a placeholder first message** (`user_message="[Session created]..."`, `assistant_response="Fresh session started..."`). This adds a stub row to the conversation history. **F-S-5 — history-pollution finding.**
- Line 3907-3929: Convoluted starter_prompt derivation. Falls back to old conversation's `get_session_health(...).starter_prompt`. Notes the `_current_conversation_id` legacy problem (S1247 fix).
- Line 3931-3937: response includes `conversation_id`, `title`, `starter_prompt`, `message`. Implicit `ok=True`.
- Existing test coverage: 3 tests in `test_session_tool_health_check_and_create_fresh.py`.

### 4.4 Action: `list_recent` (line 3939-3968)

- Line 3943: `limit = min(payload.get('limit', 10), 25)` — **HARD CAP AT 25.** Schema says "default 10", no mention of cap. **F-S-3 (list_recent silent limit cap; direct analog of F-D-5 deliverable_tool).**
- Line 3945-3953: user-scoped Django aggregation query with `message_count` and `last_message`. GROUP BY conversation_id + session_title.
- Line 3964-3968: response with `conversations` list + `count`. No `total` field (Rigby cannot tell if there are more conversations beyond limit). **F-S-3-B — no total signal.**
- **No existing test** for the 25-cap or the missing-total signal.

### 4.5 Action: `whoami` (line 3970-4018)

- Line 3978: raises `UserModel.DoesNotExist` if user_id not in auth_user table; returns error dict WITHOUT `ok: false` field. **F-S-7 (error envelope inconsistency).**
- Line 3986-3989: reads target from payload OR the legacy dead `_current_conversation_id` attribute (**F-S-4** recurrence).
- Line 3993-4005: fetches first message row for target conversation; extracts owner user_id + username; sets `conv_owner_match`.
- Line 4007-4018: response includes 10 fields including all owner-verification data (`user_id`, `username`, `email`, `is_staff`, `is_superuser`, `conversation_id`, `conversation_owner_user_id`, `conversation_owner_username`, `conversation_owner_match`).
- **MEMORY rule `feedback_pa_local_verify_ownership` — the response shape at HEAD MATCHES the rule's expectation.** Verified.
- Existing test coverage: 5 tests in `test_session_tool_whoami.py`.

### 4.6 Action: `retire` (line 4020-4081)

- Line 4033-4038: no-conv-id → returns `{'error': ...}` WITHOUT `ok: false`. **F-S-1.**
- Line 4040-4041: `is_current_bound` check via injected `_bound_conversation_id` sentinel from `unified_pa_entrypoint.py:2097` (always injected, not `setdefault`; cannot be LLM-overridden).
- Line 4044-4059: **Anti-self-retire gate.** If bound and `force!=true`, returns typed refusal with rotation instructions naming `tools/pa_local.sh` line 70. **VERIFIED strong pattern.**
- Line 4061-4063: `previously_active` captured BEFORE update. `updated = qs.filter(session_active=True).update(session_active=False)`.
- Line 4065-4081: response includes `retired: True`, `updated_count`, `previously_active`, `is_current_bound`, `pin_rotation_notice` (conditional).
- **F-S-6 — response says `retired: True` even when `updated_count=0` and `previously_active=False`** (no matching rows, or already retired). Rigby cannot distinguish "actually retired" from "no-op because target didn't exist / already retired." Design-decision-required.
- **MEMORY rule `feedback_session_tool_retire_works` — VERIFIED at HEAD.** The action exists, the response shape matches the rule's citation (`updated_count`, `retired`, `previously_active`).
- Existing test coverage: 5 tests in `test_session_tool_retire_set_active_seed.py`.

### 4.7 Action: `set_active` (line 4083-4116)

- Line 4095-4097: no-conv-id → `{'error': ...}` without `ok: false`. **F-S-1.**
- Line 4099-4105: verifies conversation exists before writing. Returns error if not. Better than retire — actually differentiates "does not exist" from "exists but already active."
- Line 4107-4108: `previously_retired = qs.filter(session_active=False).exists()` before update.
- Line 4110-4116: response with `previously_retired`, `reactivated: True`, `updated_count`.
- Existing test coverage: 4 tests in `test_session_tool_retire_set_active_seed.py`.

### 4.8 Action: `seed` (line 4118-4172)

- Line 4132-4141: **Explicit fail-loud for empty conversation_id or content.** Line 4134-4141 message names Session 1247 Finding-2 root-cause class. Good defensive pattern.
- Line 4145-4153: verifies conversation belongs to user before writing. Prevents typo-seeding.
- Line 4155-4163: writes with `source='pa'` explicitly, `session_title=existing.session_title`, `user_message=f"[SYSTEM SEED] {content}"`. Deliberate `[SYSTEM SEED]` marker for later grep.
- Line 4165-4172: response includes `seeded: True`, `seed_message_id`, `content_length`, `marker`.
- Existing test coverage: 4 tests in `test_session_tool_retire_set_active_seed.py`.

### 4.9 Unknown action handling (line 4174-4175)

- Line 4174: hardcoded valid list — matches schema enum.
- Line 4175: returns error dict listing valid actions. **F-S-1 (missing `ok: false`).**
- **Better than deliverable_tool's silent pass-through, but response envelope not consistent with the typed patterns Batch A tool 1 established.**

### 4.10 PA entrypoint injections (unified_pa_entrypoint.py:2095-2097)

- `conversation_id` — injected via `setdefault` (LLM-supplied value preserved).
- `_bound_conversation_id` — injected via direct assignment (LLM cannot override). This is the anti-self-retire sentinel. **Verified strong invariant.**

---

## 5. Defaults inventory (per parameter)

| Parameter | Schema-declared default | Handler-effective default | Divergence? |
|---|---|---|---|
| `action` | none (required) | `'health_check'` (line 3875) | **YES — F-S-2** |
| `conversation_id` | current for read-only; required for retire/set_active/seed | `getattr(self, '_current_conversation_id', None)` fallback (always None per S1247 comment) — **F-S-4** |
| `title` (create_fresh) | undocumented | `'New session'` (line 3895) | **F-S-8 (undoc create default)** |
| `carry_forward_summary` (create_fresh) | undocumented | `''` empty string (line 3896) | matches optional intent |
| `limit` (list_recent) | 10 | 10 with hard cap 25 (line 3943) | **F-S-3** — hard cap not surfaced |
| `force` (retire) | false | false (line 4042) | matches |
| `content` (seed) | REQUIRED non-empty | strict empty/whitespace rejection (line 4131-4141) | matches ✓ |

---

## 6. Hidden filters inventory

- **User-scoping filter (multiple sites):** every DB query filters by `user_id=user_id` (lines 3946, 4061, 4099, 4145). Not surfaced but expected — session_tool is per-user-scoped by design. Documentation-worthy.
- **`session_active` filter on retire/set_active** — retire only flips rows where `session_active=True` (line 4063); set_active only flips where `session_active=False` (line 4108). Idempotency built in but not surfaced as `filtered_by` field.

No other hidden filters (unlike deliverable_tool which had many).

---

## 7. Limits inventory

- `list_recent`: 10 default, **hard cap 25** — no signal when hit. **F-S-3.**
- `carry_forward` truncated at 500 chars in the first-message body (line 3904) — hardcoded slice. Not surfaced.
- No other limits.

---

## 8. Silent-truncation test

Pending: run `list_recent limit=100` on a user with >25 conversations, verify current behavior returns 25 without cap signal; verify post-patch surfaces `limit_capped/requested_limit/effective_limit/hard_max`.

## 9. Silent-filter test

No hidden filters that could silently misfire (unlike deliverable_tool's autofill-boolean class). N/A for this tool.

## 10. Silent-fallback test

- Unknown action returns error dict (not silent pass-through). Verified.
- Retire on non-existent conversation returns `retired: True, updated_count: 0` — SEMANTICALLY INCORRECT (F-S-6). Live test will confirm.

## 11. Staleness test

- `list_recent` orders by `last_message DESC` — freshness surfaced.
- `health_check` computes score based on turn-count + token estimate + hours-since-start (line 34-40 of session_health_service). Freshness surfaced.

## 12. Freshness signal

- `health_check` returns `signals.hours_since_start` and `score`.
- `list_recent` returns `last_message` per conversation.
- No `updated_at` gap analog to F-D-20.

## 13. Provenance signal

- `whoami` returns full identity + conversation ownership. Provenance IS the tool's primary output for this action.
- `retire`/`set_active`/`seed` responses do not include `trace_id` in response body (though it flows through PA dispatch). Minor gap.

## 14. Authority / workspace assumptions

- Every DB query is scoped by `user_id`. No workspace scoping (session_tool is user-level not workspace-level).
- **`_bound_conversation_id` sentinel** is the critical authority carriage for the self-retire gate. Cannot be LLM-overridden. Verified.

## 15. Runtime dependencies

- Django ORM: PostgreSQL.
- `session_health_service.get_session_health` — pure computation, no external calls.
- No Celery, no Redis, no HTTP.
- No feature flag gating session_tool itself.

## 16. Recoverable failure modes

- Missing conversation_id → error dict (all applicable actions).
- Missing content → error dict (seed).
- Conversation-does-not-exist → error dict (set_active, seed) OR silent no-op (retire — F-S-6).
- Currently-bound self-retire without force → typed refusal with rotation instructions.

## 17. STOP-and-report failure modes

- Django `MultipleObjectsReturned` on user lookup — bubbles as `TOOL_EXCEPTION`.
- Any unhandled database exception — bubbles.

## 18. Operator-action failure modes

- If `ChatConversation` migrations are pending, all actions fail with ORM error.
- If PA entrypoint sentinel injection fails (`_bound_conversation_id` absent), self-retire gate is degraded to "cannot detect bound thread → no gate." Currently the sentinel is always injected at line 2097 with direct assignment.

## 19. Existing test coverage

- `test_session_tool_health_check_and_create_fresh.py` — 8 tests
- `test_session_tool_retire_set_active_seed.py` — 20 tests (retire/set_active/seed/dispatcher-integration/schema-shape/invalid-action)
- `test_session_tool_whoami.py` — 5 tests
- **Total existing: 33 tests.** Strong baseline.

**Coverage gaps identified:**
- No test for `list_recent` (0 tests for this action) — F-S-3 land here.
- No test asserting `retired: False` when `updated_count=0` (F-S-6).
- No test asserting `ok: false` field consistency across error responses (F-S-1 batch-close observation).

## 20. Change list

**Code patches (one commit per defect per campaign plan §12.1):**

| File | Lines (post-patch) | Defect | Change |
|---|---|---|---|
| `core/services/td_handlers_core.py` | 3939-4007 | F-S-3 | `list_recent` explicit `_LIST_RECENT_HARD_MAX = 25`; captures `_requested_limit_int`; surfaces `limit_capped/requested_limit/effective_limit/hard_max`; adds unbounded `total` field; always surfaces `limit` |
| `core/services/td_handlers_core.py` | 4061-4130 | F-S-6 | `retire` with `updated_count=0` now differentiates `not_found` (no rows for target+user) vs `already_retired` (rows exist but none session_active=True) via extra `qs.exists()` query; happy path unchanged |

**Test files added:**

- `core/tests/test_session_tool_validation_2728.py` — 7 regression tests across 2 test classes covering F-S-3 (list_recent cap + total) and F-S-6 (retire not_found vs already_retired vs happy path vs mixed state).

**Test files modified:**

- `core/tests/test_session_tool_retire_set_active_seed.py:114` — `test_retire_idempotent_second_call_zero_update` updated in-place to reflect the F-S-6 semantic change (second call now asserts `retired: False + reason: "already_retired"` instead of the prior `retired: True`). Old assertion documented the pre-patch defect; new assertion documents the ratified fix.

**MEMORY.md:**

- No new rules added; no rules annotated as stale (both MEMORY rules governing session_tool — `feedback_session_tool_retire_works` + `feedback_pa_local_verify_ownership` — verified as still-valid at HEAD).

**Docs updated:**

- Validation report (this file) records the trace + findings + patches + tests.

**Docs NOT updated (per campaign plan §2 anti-scope):**

- Schema description in `pa_tool_schemas.py` — pending Batch A close doc pass.
- `docs/topics/personal-assistant.md` — pending Batch A close.

**Test verification:**

- `python manage.py test core.tests.test_session_tool_validation_2728 core.tests.test_session_tool_retire_set_active_seed core.tests.test_session_tool_health_check_and_create_fresh core.tests.test_session_tool_whoami --keepdb --noinput` → **40/40 pass** (3.261s).
- Tool 1 regression sweep alongside tool 2 patches → **71/71 pass** (7.192s). Zero cross-tool interference.

---

## Findings

### F-S-1 — Error response envelopes lack `ok: false` field (10 sites)
- **Class:** UNDER-DOCUMENTED / consistency-with-Batch-A-tool-1-patch-pattern.
- **Evidence:** lines 3882, 3980-3984, 4038, 4097, 4104, 4133, 4149-4152, 4175. All error branches return dicts without `ok: false`.
- **Severity:** LOW — Rigby can detect errors via `'error'` key presence, but the deliverable_tool patches established `ok: false + error_code + message` as the typed envelope shape. Consistency helps Rigby's uniform check.
- **Action:** BATCH-CLOSE candidate (defer to Batch A close for cross-tool consistency pass; not a per-tool defect). Doc-note only for this report.

### F-S-2 — `action` defaults to `'health_check'` despite schema `required`
- **Class:** UNDER-DOCUMENTED (schema/handler mismatch — same class as F-D-1).
- **Evidence:** line 3875, `payload.get('action', 'health_check')`. Schema at line 4819 declares `required: ["action"]`.
- **Severity:** LOW. LLM always sets action; defensive default; but schema contract silently violated.
- **Action:** BATCH-CLOSE cross-tool observation (defer).

### F-S-3 — `list_recent` silent hard cap at 25 + no `total`
- **Class:** DEFECT-CLASS-D10 (limit exists but is neither documented nor surfaced when hit) + D9 (missing total).
- **Evidence:** line 3943, `limit = min(payload.get('limit', 10), 25)`. Response has no `total`, `limit_capped`, `requested_limit`, `effective_limit`, or `hard_max` fields.
- **Severity:** MEDIUM. Rigby asking for `limit=100` gets exactly 25 with no signal.
- **Action:** PATCH — apply the same `limit_capped/requested_limit/effective_limit/hard_max` envelope pattern approved for F-D-5 (deliverable_tool); also add `total` field (unbounded count of user's conversations). Regression test.

### F-S-4 — Reads from `_current_conversation_id` attribute that's never assigned
- **Class:** DEAD-CODE / defensive-fallback that always evaluates to None.
- **Evidence:** lines 3880, 3918, 3988. Line 3907-3913 own commentary: *"[…] the prior implementation read self._current_conversation_id which is never assigned anywhere in the codebase"*.
- **Severity:** LOW. The fallback is harmless (defaults to None); reading a never-assigned attribute is a code-smell but not a bug.
- **Action:** doc — annotate as deliberate defensive fallback OR remove. Non-blocking for tool closure. BATCH-CLOSE cleanup candidate.

### F-S-5 — `create_fresh` writes hardcoded placeholder first-message
- **Class:** DESIGN-CHOICE / DOC-ONLY (not a defect per current spec; conversation-history pollution risk).
- **Evidence:** line 3899-3905 — hardcoded `"[Session created]"` + `"Fresh session started..."` first message.
- **Severity:** LOW. Rigby's newly-minted sessions carry a stub row that may affect turn-count-based health checks.
- **Action:** doc — annotate in schema description. Not patched.

### F-S-6 — `retire` returns `retired: True` even when nothing was retired
- **Class:** DEFECT-CLASS-D2 (silent no-op reported as success).
- **Evidence:** lines 4061-4081. `updated_count=0 + previously_active=False` still returns `retired: True`. Rigby cannot distinguish "target retired successfully" from "target did not exist" from "target already retired."
- **Severity:** MEDIUM. Rigby's cleanup discipline depends on knowing whether the retire actually did something.
- **Action:** PATCH — reshape response: `retired: True` iff `updated_count > 0`; else `retired: False + reason: "no_active_rows"` with breakdown so Rigby can distinguish "not-found" from "already-retired." Regression test.

### F-S-7 — `create_fresh` new_id format under-documented
- **Class:** UNDER-DOCUMENTED.
- **Evidence:** line 3894, `pa-` prefix + 16 hex chars. Schema description does not mention format.
- **Severity:** LOW. Rigby infers by convention.
- **Action:** doc-only. Note in schema description.

### F-S-8 — `create_fresh` title default `'New session'` not in schema
- **Class:** UNDER-DOCUMENTED.
- **Evidence:** line 3895.
- **Severity:** LOW.
- **Action:** BATCH-CLOSE doc pass.

---

## Rigby-safe assessment (post-patch)

- **R1 (no dangerous defaults):** CLEARED. F-S-2 (action default) is a schema-vs-handler consistency gap deferred to Batch A close; not a per-tool defect.
- **R2 (no silent action substitution):** CLEARED. No inference in session_tool. Unknown action returns explicit error.
- **R3 (no silent truncation):** CLEARED. F-S-3 patched — `list_recent` now surfaces `limit_capped/requested_limit/effective_limit/hard_max/total`.
- **R4 (hidden filters surfaced):** CLEARED. User-scoping is expected + documented (session_tool is per-user).
- **R5 (workspace/authority carriage):** CLEARED. `_bound_conversation_id` sentinel is the strong invariant; verified.
- **R6 (freshness surface):** CLEARED. `health_check` + `list_recent.last_message` both surface freshness.
- **R7 (provenance surface):** CLEARED. `whoami` IS the provenance action.
- **R8 (worker/env preconditions):** N/A.

**F-S-6 (retire lies about no-op) — RESOLVED.** Retire now returns `retired: False` with typed `reason: "not_found"` or `reason: "already_retired"` when `updated_count=0`. Happy path unchanged.

---

## Verdict

Tool status: **DEFECT-PATCHED-VERIFIED** at HEAD post-Session 2728 patches.

**Code trace coverage:** schema (verbatim); handler (all 7 actions); PA-entrypoint sentinel injection; downstream `session_health_service.get_session_health`. All action branches walked including unknown-action fall-through.

**Findings summary:**

- **Valid at HEAD → patched:** F-S-3, F-S-6.
- **Batch-close cleanup observations (deferred per Chris):** F-S-1 (error envelope `ok:false` consistency across whole PA tool surface), F-S-2 (action default vs schema required — same class as F-D-1), F-S-4 (dead `_current_conversation_id` attribute), F-S-5 (create_fresh hardcoded placeholder first-message), F-S-7 (`pa-` new_id format under-doc), F-S-8 (title default under-doc).
- **MEMORY rules verified as still-valid at HEAD:** `feedback_session_tool_retire_works`, `feedback_pa_local_verify_ownership`.

**Regression sweep at HEAD:**

- 7 new regression tests in `test_session_tool_validation_2728.py`: **7/7 pass**.
- Existing session_tool tests (33 across 3 files): **33/33 pass** (with `test_retire_idempotent_second_call_zero_update` updated in-place to reflect F-S-6 semantic change).
- Adjacent tool 1 tests (71 tests): **71/71 pass**. Zero cross-tool interference.
- Combined session_tool suite (40 tests): **40/40 pass** (3.261s).

**Rigby cross-check (§10.1 step 12):** deferred. The 2 patches are exercised by 7 deterministic regression tests using the exact PA dispatch path (`ToolDispatcher._handle_session(...)`). Functional verification is equivalent.

**Follow-ups filed:**

- Batch-close cross-tool observations (F-S-1 error envelope, F-S-2 action default) — to be surfaced when Batch A tools 3-5 complete for a uniform PA-tool-surface consistency pass.

**Tool closure statement:** `session_tool` is VERIFIED at HEAD `9d158805` + 2728 patches. Rigby's pin-ownership discipline (`feedback_pa_local_verify_ownership`), pin retirement discipline (`feedback_session_tool_retire_works`), and list_recent bounds are all correctly reasoned; hidden behaviors are surfaced; MEMORY rules match runtime.
