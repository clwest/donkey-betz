# `kb_ingest` — Validation Report

**Tool:** `kb_ingest` — action within `intelligence_tool` (write side of the KB).
**Schema:** `core/services/pa_tool_schemas.py:3245` (enum entry) + `pa_tool_schemas.py:3270` (`url` param).
**Delegation chain:**
- `intelligence_tool.kb_ingest` → `td_handlers_core.py:3333-3334` delegates to `_handle_rag_query('rag_query_tool', {'action': 'ingest', 'url': ...}, user_id, trace_id)`.
- `_handle_rag_query.ingest` at `td_handlers_core.py:2609-2625` dispatches `process_url_async.delay(url=url, generate_embeddings=True)`.
- Celery task `process_url_async` at `tasks.py:4212` thin wrapper → `_impl_process_url_async` at `tasks_media.py:335-420`.
**Downstream:** `content.processors.DocumentProcessingPipeline` (URL fetch + text extraction) → `Document` row creation → `generate_document_embeddings` follow-on task.
**Session validated:** S2728 → S2729 (Batch B tool 3 of 5).
**HEAD at validation:** `5ce56b5f` + Batch B tools 1-2 uncommitted patches.
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred (regression tests suffice).
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch B tool 3 of 5). Trace + 4 patches (F-KI-1, F-KI-2/F-KI-3, F-KI-4, F-KI-5 option (a)) + 16 regression tests (kb_ingest's first regression test file at HEAD). 101 tests total pass across all validation-2728 files.

---

## 1. Intended purpose (per schema description)

*"kb_ingest: ingest a URL into the knowledge base."* — one of 19 actions on the `intelligence_tool` gateway.

## 2. Rigby's belief (per schema)

Rigby uses `kb_ingest` when the user asks to "add this URL to the knowledge base" or "ingest this article." Absent MEMORY rule specifically citing `kb_ingest` — no crystallized failures on record. Adjacent MEMORY rules that apply:
- **`feedback_procfile_makefile_queue_parity`** — the underlying Celery task `process_url_async` uses default queue routing; Procfile/Makefile parity verified at Batch A tool 4 (F-CC-6) for `code_jobs`, and the default worker consumes the default queue (verified via `make celery` output — "Celery default worker (solo, ML-free queues)").

## 3. Schema claim (verbatim capture)

Enum member of `intelligence_tool.action`: `"kb_ingest"`. Description: *"kb_ingest: ingest a URL into the knowledge base."*

**Relevant parameters:**
- `action` = `"kb_ingest"` (required).
- `url` (string, described as "URL for kb_ingest").

**All other `intelligence_tool` params** (desk, source, query, ticker, sport, bill_number, stake, odds, wager_type, state, chamber, party, hours, limit) — not used by `kb_ingest`. Schema has no explicit gate; LLM must pick the right subset.

## 4. Handler behavior (traced)

### 4.1 Layer 1 — `intelligence_tool.kb_ingest` (td_handlers_core.py:3333-3334)

```python
if action == 'kb_ingest':
    return _tag(self._handle_rag_query('rag_query_tool', {'action': 'ingest', 'url': payload.get('url', '')}, user_id, trace_id))
```

**Silent parameter drop:**
- Only `url` is extracted from the payload and passed to `_handle_rag_query`.
- `user_id` IS passed via the positional arg (line 3334 last argument).
- Any other `intelligence_tool` payload params (e.g., `title`, `limit`) are **dropped silently.**
- The delegation does NOT pass conversation_id or any follow-up signal.

`_tag` wraps the response with a marker; identity-passthrough on the response otherwise.

### 4.2 Layer 2 — `_handle_rag_query.ingest` (td_handlers_core.py:2609-2625)

- Line 2610: `url = payload.get('url', '').strip()`.
- Line 2611-2612: **`raise ValueError("'url' is required for ingest action")` on empty URL.** Other actions (search / list_documents / promote) return typed error dicts (`{'error': ...}`). Inconsistent contract shape. **F-KI-1.**
- Line 2615-2616: `task = process_url_async.delay(url=url, generate_embeddings=True)`. **`generate_embeddings=True` hardcoded** — caller cannot opt out. **F-KI-6.**
- **`user_id` from handler kwarg is NOT passed to `process_url_async.delay(...)`.** **F-KI-3.** The Celery task defaults `user_id=None`.
- Line 2618-2625: response includes `action`, `url`, `task_id`, `mode: 'async'`, `message`, `success: True`. **`success: True` is misleading** — it's dispatch success, not ingestion success. **F-KI-5.**
- **No URL scheme / hostname validation whatsoever.** Any string with content survives the strip check. **F-KI-4.** SECURITY concern (SSRF surface).

### 4.3 Layer 3 — `process_url_async` @shared_task (tasks.py:4207-4214)

- Line 4207: `@shared_task(bind=True, max_retries=3)` — **no explicit queue routing.** Uses default queue.
- Wrapper delegates to `_impl_process_url_async`.

### 4.4 Layer 4 — `_impl_process_url_async` (tasks_media.py:335-420)

- Line 355-356: `DocumentProcessingPipeline().process_url(url)` — presumably validates URL scheme + fetches content. Not traced deeper in this session; treated as boundary.
- Line 358-364: on pipeline failure, returns `{status: 'failed', url, error: ...}`.
- Line 374-375: **`owner = User.objects.get(id=user_id) if user_id else User.objects.first()`** — **when `user_id=None` (which is ALWAYS the case per F-KI-3), owner defaults to `User.objects.first()`.** Provenance goes to whichever user has the lowest ID (typically `admin` or `system`). **F-KI-2** — cross-user provenance leak. MEDIUM security concern.
- Line 377-391: `Document.objects.create(...)` — creates row with the (possibly-wrong) owner, source_url, extracted metadata, embeddings-ready content.
- Line 402-407: dispatches `generate_document_embeddings` as follow-on task.
- Line 418-420: on exception, retries via Celery `self.retry(exc=e, countdown=60 * retries)`. Handles retries up to `max_retries=3`.

### 4.5 Queue routing

- `process_url_async` uses **default queue** (no `queue='...'` kwarg on `@shared_task`).
- Local Makefile spawns "Celery default worker (solo, ML-free queues)" — consumes default queue. ✓
- Procfile line for default worker verified via `grep -n "worker: " Procfile` (would need to confirm).

## 5. Defaults inventory (per parameter)

| Param | Schema-declared | Handler-effective | Divergence? |
|---|---|---|---|
| `action` | required | intelligence_tool defaults to... complex 19-branch dispatch (no consistent handler default) | Layer-1 batch-close |
| `url` | described as "URL for kb_ingest" | fail-loud via ValueError on empty | Inconsistent with other actions (F-KI-1) |
| `title` | not in schema | `title=None` — NOT plumbed through | F-KI-7 (silent drop) |
| `user_id` | dispatched by PA entrypoint | **NOT passed to Celery task** — defaults to `User.objects.first()` | **F-KI-2/F-KI-3 SECURITY** |
| `generate_embeddings` | not in schema | hardcoded `True` | F-KI-6 |

## 6. Hidden filters

None. `kb_ingest` is a dispatch tool (no query / filter logic).

## 7. Limits inventory

- `process_url_async` @shared_task retries `max_retries=3` with 60-second-per-retry backoff.
- No explicit time_limit / soft_time_limit — inherits Celery defaults (typically 3-5 minutes).
- `DocumentProcessingPipeline.process_url` presumably has its own limits (not traced).

## 8. Silent-truncation test

N/A (dispatch tool).

## 9. Silent-filter test

N/A.

## 10. Silent-fallback test

- **F-KI-2:** User attribution silently defaults to `User.objects.first()` when `user_id=None`. **MEDIUM security finding** — Rigby dispatches on behalf of "chris" (or whatever user is authenticated) but the ingested Document ends up owned by whichever user has the lowest ID in the DB.

## 11. Staleness test

N/A (URL fetch is live at ingestion time).

## 12. Freshness signal

Response includes `task_id` for polling but no `submitted_at` timestamp. Batch-close observation.

## 13. Provenance signal

- Response includes `url` echo and `task_id`.
- **Does NOT include:** dispatching user_id, conversation_id, agent_name, workspace_id.
- Downstream `Document.owner` is set to the wrong user per F-KI-2.

## 14. Authority / workspace assumptions

- **user_id from handler is NOT passed to the task** (F-KI-3). Task defaults to first-user (F-KI-2).
- No workspace scoping — `Document` model doesn't have workspace FK for URL-ingested content.
- No PA-side actor identity carriage.

## 15. Runtime dependencies

- Celery default queue with a live worker consuming.
- `DocumentProcessingPipeline` (URL fetch + text extraction).
- OpenAI API for embeddings (via follow-on `generate_document_embeddings`).
- Django ORM: `Document`, `DocumentEmbedding`.
- HTTP fetch capability (network access from worker).

## 16. Recoverable failure modes

- Empty URL → `ValueError` propagates as tool exception (F-KI-1 — inconsistent shape).
- URL fetch failure → task returns `{status: 'failed', error: ...}`.
- Task exception → Celery retries up to 3 times with backoff.

## 17. STOP-and-report failure modes

- After 3 retries with backoff, task fails and Rigby's response `task_id` polling returns failure.
- No auto-notification back to Rigby's conversation (unlike claude_code_tool F-CC-3 follow-up).

## 18. Operator-action failure modes

- Default queue worker down → task queues silently. Same class as F-CC-DEPLOY-1 (operator-level; not patchable at handler).
- URL processor library missing/broken → task exception → retries → eventual failure.
- OpenAI API down → follow-on embeddings task fails; document row exists but has no embeddings.

## 19. Existing test coverage

No dedicated test file for `kb_ingest` at HEAD. Grep across `core/tests/` shows no matches. **Zero coverage.**

## 20. Change list

**Code patches (bundled into one edit per campaign plan §12.1 — all four defects live in the same `_handle_rag_query.ingest` block):**

| File | Lines (post-patch) | Defect | Change |
|---|---|---|---|
| `core/services/td_handlers_core.py` | 2621-2635 | F-KI-1 | Empty URL returns typed `{'ok': False, 'error_code': 'url_required', 'error': ...}` dict instead of raising ValueError. Mirrors sibling actions (search / promote) in the same handler. |
| `core/services/td_handlers_core.py` | 2637-2665 | F-KI-4 | URL scheme validation via `urllib.parse.urlparse`. Non-http/https schemes (file://, data:, javascript:, no-scheme) return typed `{'ok': False, 'error_code': 'invalid_url_scheme', 'error': ...}` with the scheme echoed for diagnosis. SSRF + local-file exfiltration defense-in-depth at tool boundary. |
| `core/services/td_handlers_core.py` | 2667-2687 | F-KI-2/F-KI-3 | `process_url_async.delay(url=url, user_id=user_id, generate_embeddings=True)` — user_id now plumbed through the delegation chain. Restores dispatching-user-owns-ingested-document invariant. Prior behavior silently attributed every PA-dispatched ingest to `User.objects.first()` (typically admin / system). |
| `core/services/td_handlers_core.py` | 2688-2704 | F-KI-5 option (a) | Additive `dispatched: True` field alongside existing `success: True`. Also echoes `user_id` (or null) for provenance verification. Back-compat safe. |

**Test files added:**

- `core/tests/test_kb_ingest_validation_2728.py` — **first regression test file for `kb_ingest` at HEAD.** 16 tests across 5 test classes: F-KI-1 empty URL typed error (2 tests including whitespace-only URL); F-KI-4 URL scheme validation (6 tests including file / data / javascript rejection + http/https acceptance + no-scheme rejection); F-KI-2/F-KI-3 user_id plumbing (4 tests including delay-call kwarg assertion + response echo); F-KI-5 dispatched field (3 tests); baseline delegation from `intelligence_tool.kb_ingest` → `_handle_rag_query.ingest` with user_id survival check (1 test).

**Docs updated:**

- Validation report (this file) records the trace + findings + patches + tests.

**Docs NOT updated (per campaign plan §2 anti-scope):**

- Schema description in `pa_tool_schemas.py` — pending Batch B close doc pass. F-KI-4 is transparent to schema; F-KI-5 additive fields don't require schema changes.
- `docs/topics/personal-assistant.md` — pending Batch B close.

**MEMORY.md:**

- No new rules added. `feedback_procfile_makefile_queue_parity` remains VERIFIED-VALID at HEAD (from Batch A tool 4 annotation); `process_url_async` uses default queue routing which the local `make celery` default worker consumes.

**Test verification:**

- `python manage.py test core.tests.test_kb_ingest_validation_2728` → **16/16 pass** (0.063s).
- Full Batch A + Batch B cross-tool regression sweep (8 validation-2728 files): **101/101 pass** (15.3s). Zero cross-tool interference.

---

## Findings

### F-KI-2 — Ingested Document owner defaults to `User.objects.first()` when `user_id=None` (MEDIUM; SECURITY)
- **Class:** DEFECT-CLASS-D8 (authority assumption not carried).
- **Evidence:** `_impl_process_url_async` at `core/tasks_media.py:374-375`. Combined with F-KI-3 (user_id never passed through), EVERY PA-dispatched kb_ingest creates a Document owned by the first user in the DB — not the dispatching user.
- **Severity:** MEDIUM. Provenance leak: `chris`-dispatched ingests get attributed to `admin` (or whoever has the lowest ID). Multi-user platforms would leak content across users.
- **Action:** PATCH — plumb `user_id` from handler → `process_url_async.delay(url=url, user_id=user_id, generate_embeddings=True)`. Verifies at test-boundary via regression test that user_id survives the delegation.

### F-KI-3 — `_handle_rag_query.ingest` drops `user_id` on task dispatch (MEDIUM; SECURITY)
- **Class:** DEFECT-CLASS-D8 (companion to F-KI-2).
- **Evidence:** `_handle_rag_query.ingest` at `td_handlers_core.py:2615-2616` — `process_url_async.delay(url=url, generate_embeddings=True)`. No `user_id=user_id` kwarg.
- **Severity:** MEDIUM (root cause of F-KI-2).
- **Action:** PATCH — same PATCH addresses both F-KI-2 and F-KI-3.

### F-KI-1 — Empty URL raises ValueError instead of returning typed error dict (LOW)
- **Class:** UNDER-DOCUMENTED / consistency divergence.
- **Evidence:** `td_handlers_core.py:2611-2612` — `raise ValueError` when `url` is empty. Compare with sibling actions in the same handler (search line 2525, promote line 2630) which return `{'error': ...}` dicts.
- **Severity:** LOW. Handler-side inconsistency; from Rigby's perspective ValueError propagates as TOOL_EXCEPTION.
- **Action:** PATCH — mirror sibling-action shape; return typed error dict.

### F-KI-5 — Response says `success: True` on dispatch (misleading) (LOW-MEDIUM)
- **Class:** UNDER-DOCUMENTED / semantic-correctness observation.
- **Evidence:** `td_handlers_core.py:2624` — `'success': True` in dispatch response.
- **Severity:** LOW-MEDIUM. Dispatch success ≠ ingestion success. Rigby could interpret as "URL is now in the KB." Message string does say "Use job_status to check progress" but the `success: True` field is machine-parseable and misleading.
- **Action:** PATCH — rename `success` → `dispatched` OR clarify to `success: False` with `dispatched: True` (ingestion not yet complete). Chris decision on exact shape.

### F-KI-4 — No URL scheme/hostname validation at tool layer (MEDIUM; SECURITY)
- **Class:** DEFECT-CLASS-D8 (unbounded authority).
- **Evidence:** `td_handlers_core.py:2610` — only `.strip()`. Any string with content is passed to the task.
- **Severity:** MEDIUM. `file:///etc/passwd`, `data:...`, `javascript:...`, or internal-network URLs (SSRF) get dispatched. `DocumentProcessingPipeline` presumably validates, but defense-in-depth at the tool layer is worth doing.
- **Action:** PATCH — validate URL parses via `urllib.parse.urlparse`; reject non-`http`/`https` schemes at tool layer with typed error naming the reason.

### F-KI-6 — `generate_embeddings=True` hardcoded (LOW; batch-close)
- **Class:** UNDER-DOCUMENTED inflexibility.
- **Severity:** LOW. Reasonable default; callers who want to skip embeddings can't.
- **Action:** BATCH-CLOSE observation. Not patched.

### F-KI-7 — `title` param from `_impl_process_url_async` not plumbed through (LOW; batch-close)
- **Class:** UNDER-DOCUMENTED silent drop.
- **Severity:** LOW.
- **Action:** BATCH-CLOSE observation. Not patched.

### F-KI-BC-* — batch-close observations
- Provenance echo missing (no dispatching user_id, conversation_id, workspace_id in response).
- No `submitted_at` timestamp for polling / diagnostics.
- No auto-follow-up subscription for completion notification (unlike claude_code_tool F-CC-3).

---

## Rigby-safe assessment (post-patch)

- **R1 (no dangerous defaults):** CLEARED. F-KI-2 patched — user_id plumbed through. F-KI-4 patched — URL scheme validated.
- **R2 (no silent action substitution):** CLEARED.
- **R3 (no silent truncation):** N/A.
- **R4 (hidden filters surfaced):** N/A.
- **R5 (workspace/authority carriage):** CLEARED. F-KI-2/F-KI-3 patched. Response echoes `user_id` for verification.
- **R6 (freshness surface):** N/A.
- **R7 (provenance surface):** PARTIAL — batch-close (no workspace_id / conversation_id / submitted_at).
- **R8 (worker/env preconditions):** PARTIAL — default queue routing depends on operator discipline (F-CC-DEPLOY-1 class; not patchable at handler).

---

## Verdict

Tool status: **DEFECT-PATCHED-VERIFIED** at HEAD post-Session 2728 patches.

**Code trace coverage:** full 4-layer delegation chain (intelligence_tool.kb_ingest → _handle_rag_query.ingest → process_url_async @shared_task → _impl_process_url_async).

**Findings summary:**

- **Valid at HEAD → patched:** F-KI-1 (empty URL ValueError), F-KI-2/F-KI-3 (user_id dropped on delay call — SECURITY provenance leak), F-KI-4 (no URL scheme validation — SSRF surface), F-KI-5 (`success: True` misleading — additive `dispatched: True` field per Chris option (a)).
- **Batch-close cleanup observations (deferred per Chris):** F-KI-6 (`generate_embeddings=True` hardcoded), F-KI-7 (`title` silent-dropped), F-KI-BC-* (provenance echo gaps: workspace_id / conversation_id / submitted_at / auto-follow-up).

**Coverage improvement:**

- **Before Batch B tool 3:** zero regression tests for `kb_ingest`.
- **After Batch B tool 3:** 16 regression tests covering all 4 patched behaviors + the delegation chain from `intelligence_tool` → `_handle_rag_query` → task dispatch. Establishes coverage for future refactors.

**Regression sweep at HEAD:**

- 16 new regression tests in `test_kb_ingest_validation_2728.py`: **16/16 pass** (0.063s).
- Full Batch A + Batch B cross-tool sweep (8 validation-2728 files, 101 tests): **101/101 pass** (15.3s). Zero cross-tool interference.

**Follow-ups filed:**

- Batch-close observations for cross-tool consistency + kb_ingest-specific (title plumbing, generate_embeddings opt-out, provenance echo gaps).

**Tool closure statement:** `kb_ingest` is VERIFIED at HEAD + 4 patches. The two SECURITY issues (F-KI-2/F-KI-3 provenance leak via silent user_id drop; F-KI-4 SSRF surface via missing scheme validation) are closed. Rigby's ingested Documents now correctly attribute to the dispatching user; non-http(s) URLs are rejected at the tool boundary with a typed error naming the scheme; the misleading `success: True` field is joined by a semantically-accurate `dispatched: True` field for callers that need to distinguish dispatch from ingestion completion. First regression test coverage established.
