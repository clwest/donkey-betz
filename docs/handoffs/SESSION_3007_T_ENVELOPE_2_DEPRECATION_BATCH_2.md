---
title: "SESSION 3007 — T-ENVELOPE-2-DEPRECATION Batch 2: 10 auth-middleware sites migrated + lint gate extended"
session: 3007
date: 2026-07-27
type: single_pr_close
merge_shas:
  - "d00dd5b05"   # PR #3687 — Batch 2 migrations + lint gate extension
prs:
  - 3687
related_arcs:
  - "ADR-0007 Layered Envelope Policy (ratified S3005)"
  - "I-0301 Failure-Data Safety Contract (Family E authorizing substrate)"
consumes:
  - "S3006 close cascade batch-2 recommendation (auth_middleware.py smallest of remaining 3 files)"
  - "ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION T-slot"
  - "ADR-0007 §4.2 lint gate (extended, not authored)"
---

# S3007 — T-ENVELOPE-2-DEPRECATION Batch 2

**Status:** CLOSED. 1 feature PR merged. 10 Family B error call-sites migrated to Family E in `core/auth_middleware.py`. Lint gate extended (2 → 3 files tracked). HEAD `d00dd5b05`.

## Session shape

Single-focus, single-PR, one-session close. Clean Flow B: primary-directive routing (Chris "yes go with option A") → Rigby A1 SIGN joint agreement on 10 reason_code mappings + 2 open decisions (D1 busy vs unavailable for site 6; D2 include decorator in scope) → implementation → Rigby A2 SIGN pre-merge (AGREE, no STRENGTHEN) → merge → **`make restart` (NOT just `make celery-recycle`)** → live-dispatch smoke → close cascade. **4th consecutive S3xxx→S3xxx+1 continuous cascade** (see Fold D).

## PR #3687 (`d00dd5b05`) — Batch 2 migrations + lint gate extension

**Scope (2 files, +83 / -14):**

### Migrations (10 call-sites in `core/auth_middleware.py`)

**`token_auth_required` decorator (site 1):**
- Line 85-91 (originally L79): `not_authenticated` (401) — decorator missing token. Hint: `{source: decorator_missing_token}`.

**`UnifiedTokenAuthenticationMiddleware.process_request` — session-auth path (sites 2-4):**
- Line 626-635 (originally L618): `permission_denied` (403) — session-authed non-staff on STAFF_REQUIRED_PATHS. Hint: `{source: session_staff_required, user}`.
- Line 638-646 (originally L623): `permission_denied` (403) — session-authed reviewer on REVIEWER_BLOCKED_PATHS. Hint: `{source: session_reviewer_blocked_path, user}`.
- Line 651-658 (originally L628): `permission_denied` (403) — session-authed reviewer, non-GET on /api/. Hint: `{source: session_reviewer_write_blocked, user, method}`.

**`UnifiedTokenAuthenticationMiddleware.process_request` — token-auth path (sites 5-10):**
- Line 668-674 (originally L638): `not_authenticated` (401) — no session, no token. Hint: `{source: no_credentials}`.
- Line 691-701 (originally L655): `busy` (503) — `TokenValidationInfrastructureError` (auth backend down). Hint: `{source: auth_backend_unavailable, exc_type}`. **S1171 fix intent preserved** — retryable=True, terminal_state=BUSY.
- Line 705-712 (originally L663): `not_authenticated` (401) — validate_token returned None. Hint: `{source: invalid_token}`.
- Line 717-725 (originally L669): `permission_denied` (403) — token-authed non-staff. Hint: `{source: token_staff_required, user}`.
- Line 729-736 (originally L674): `permission_denied` (403) — token-authed reviewer on blocked path. Hint: `{source: token_reviewer_blocked_path, user}`.
- Line 740-747 (originally L678): `permission_denied` (403) — token-authed reviewer non-GET. Hint: `{source: token_reviewer_write_blocked, user, method}`.

### Import surface

- Removed: `from .api_responses import api_unauthorized, api_forbidden, api_error`
- Added: `from core.security.error_envelope import build_user_facing_envelope`
- Existing (untouched): `from django.http import JsonResponse`

### Per-site pattern (Batch 1 verbatim reuse)

```python
payload = build_user_facing_envelope(reason_code=X)
logger.warning(
    "envelope_emit reason=%s support=%s endpoint=%s hint=%s",
    payload['reason_code'], payload['support_code'], request.path,
    {source_and_context_dict},
)
return JsonResponse(payload, status=X)
```

**Operator-context preservation:** existing f-string operator logs (`logger.warning(f"Staff access required for {path}, user: {username}")`, `logger.warning(f"No authentication provided for {path}")`, `logger.warning(f"Invalid authentication token for {path}")`, `logger.error("Auth backend unreachable while validating token for %s: %s", ...)`) kept **as-is**. `envelope_emit` structured log added as **second line** — additive, not replacement. Username / path / exc info preserved via both channels.

### Lint gate extended (ADR-0007 §4.2)

**`scripts/lint_no_deprecated_family_b.py` MIGRATED_FILES tuple:**
```python
MIGRATED_FILES: tuple[str, ...] = (
    # Batch 1 (S3006, ADR-0007 §4.3)
    "core/views_odds_sports.py",
    "core/views_revenue_analytics.py",
    # Batch 2 (S3007, ADR-0007 §4.3) — 10 sites in auth middleware +
    # token_auth_required decorator (same file, file-scoped lint).
    "core/auth_middleware.py",
)
```

Lint script + CI workflow (`.github/workflows/check-envelope-migration.yml`) authored S3006 — this session only appended to the tuple. Machinery unchanged.

## Design decisions ratified

### D1 — Site 6 reason_code (`busy` chosen over `unavailable`)

`core/security/reason_codes.py` has two ratified 503 codes:
- `busy`: retryable=True, terminal_state=BUSY, typical_status=503
- `unavailable`: retryable=False, terminal_state=FAILED, typical_status=503

`TokenValidationInfrastructureError` models a **transient infrastructure failure** (Postgres/Redis pressure — S1171 origin). Current message text was "please retry". `busy` is the semantic match:
- retryable=True → clients auto-retry with backoff (matches "please retry" wording + S1171 fix intent)
- terminal_state=BUSY → NOT permanent (unlike FAILED)
- Debuggability preservation: `auth_backend_unavailable` identity moves from `error_code` field → structured-log `hint`. Zero operator-diagnostic loss.

Rigby AGREE (A1 SIGN).

### D2 — `token_auth_required` decorator in Batch 2 scope

The decorator lives at module scope in `core/auth_middleware.py`, outside the `UnifiedTokenAuthenticationMiddleware` class. Same file → same file-scoped lint. Excluding the decorator would block adding `core/auth_middleware.py` to `MIGRATED_FILES`. Included in scope with same 3-line pattern.

Rigby AGREE (A1 SIGN).

## Rigby SIGN quality signal

**A1 SIGN (pre-implementation):** 4 substantive `repo_tool.read_file` runs — line-by-line verification of all 10 call-sites in `core/auth_middleware.py` (2 reads spanning lines 1-120 + 600-720), reason_code enum members in `core/security/reason_codes.py`, Batch 1 STRENGTHEN pattern verbatim in `core/views_odds_sports.py` lines 60-180. AGREE on mapping table + D1 + D2. No STRENGTHEN pre-code.

**A2 SIGN (pre-merge):** 4 substantive `repo_tool.read_file` + `repo_tool.search` runs — spot-check of sites 1 / 6 / 10 in migrated file, import-surface verification (line 24 new import present; deprecated import absent), lint config verification (3 files in MIGRATED_FILES tuple). AGREE ship-ready, **no STRENGTHEN required**. Substantive per PLAYBOOK-7.7.2, not rubber-stamp.

**Zoom-out asks (per `feedback_zoom_out_ask_per_rigby_sign`):** 3 questions posed at A2 SIGN — Q1 helper extraction timing, Q2 middleware invariant check, Q3 RateLimitingMiddleware inline dict scope-creep. Rigby answered all 3 with specific recommendations (see Folds).

## Verifications performed

At HEAD `d00dd5b05`:
- `python scripts/lint_no_deprecated_family_b.py` → `✅ ADR-0007 Family B deprecation lint OK (3 files checked)`
- `python manage.py check` → System check identified no issues (0 silenced)
- `grep -c "envelope_emit reason=" core/auth_middleware.py` → 10 log lines (matches 10 error returns)
- `grep "api_error\|api_unauthorized\|api_forbidden" core/auth_middleware.py` → 0 matches (excluding line 19 comment)
- `make restart` post-merge — Daphne + Celery + beat all restarted cleanly
- **Live-dispatch smoke:** `curl -s http://localhost:8000/api/v1/vip-invites/` → HTTP 401 + `{support_code, reason_code, human_message, retryable, terminal_state, timestamp}` (Family E shape confirmed live)

## γ mechanism state (unchanged from S3006 close)

Layer 1 + Layer 2 + Layer 3 still all LIVE at HEAD `d00dd5b05`. ADR-0005 T-slot progress:

- **CLOSED (S3005):** T-ENVELOPE-2 (as already-shipped by I-0301)
- **PROGRESS this session:** T-ENVELOPE-2-DEPRECATION Batch 2 (3-of-5 files complete, 21-of-108 call-sites migrated)
- **SHIPPED (prior sessions):** T-ENVELOPE-0/1/3 (S3002), T-VIP-1 (S3003), §3.5 UX widening (S3004), Batch 1 (S3006)
- **REMAINING T-ENVELOPE-2-DEPRECATION:** 2 files, 87 call-sites (views_auto_distribution 25 / views_platform_integrations 62). Estimate 4 more sessions (or 3 with helper extraction).
- **REMAINING T-slots:** T-ENVELOPE-4 (largely subsumed), T-ENVELOPE-5 (optional), T-ENVELOPE-6 (Group 1700 pending)

## Folds

- **Fold A `2nd trigger`** — per-site 3-line pattern (payload → envelope_emit log → JsonResponse) applied for the **2nd concrete batch**. Rigby recommendation: extract `emit_error_envelope(reason_code, request, hint=None) → JsonResponse` helper **BEFORE Batch 3**. Rationale: 25+62 remaining sites = 87 more copy-pastes if not extracted; refactor risk grows non-linearly with drift across batches. Chris ratified **defer to S3008** as the natural opener. Extract-first-then-Batch-3 is the primary S3008 directive.

- **Fold B `2nd trigger`** — reason_code-to-status_code coupling opportunity. All 21 sites across Batches 1+2 pass both `reason_code=X` AND `status=Y` explicitly, but `ReasonCode.typical_status` is already in the enum (`core/security/reason_codes.py:45`). Site 6 (Batch 2, `busy`/503) confirms typical_status matches actual emit for every code we've used so far. **Fold into Fold A** — the helper extraction (S3008) should auto-infer `status` from `ReasonCode.typical_status`; caller passes only `reason_code`.

- **Fold C `informational` (1st trigger)** — `feedback_recycle_after_merge` **middleware trigger class**. Current rule text focuses on `frontend/**` as the trigger requiring `make recycle-all` over `make celery-recycle`. Middleware changes (auth_middleware.py this session) are a NEW class where `make celery-recycle` is insufficient: middleware runs in Daphne, not in Celery workers. **Live evidence this session:** first curl after `make celery-recycle` returned legacy Family B shape; second curl after `make restart` returned Family E. Watch for 2nd occurrence (any Django settings / middleware / URL-config / installed-apps change). If confirmed, propose feedback rule refinement: "Any change to files loaded by Daphne request path (middleware / URLs / settings / installed_apps) requires `make restart` or `make recycle-all`, not `make celery-recycle`."

- **Fold D `4th continuous cascade`** — S3xxx series continuous-engineering pattern. Prior triggers: S3003→S3004 (Fold-Drain-Same-Surface), S3004→S3005 (Substrate-invalidation-cascade), S3005→S3006 (Implementation-of-just-ratified-ADR). This session S3006→S3007 = **queue-drain across batches of same T-slot** — DIFFERENT class from the prior three. **Class-distinguished 4th trigger.** Not sufficient for the S3006 Fold D Playbook proposal (that rule targeted "ratification → next-session implementation" specifically). Log as separate observation. Broader "S3xxx sessions naturally cascade" pattern now at 4 instances across 3 classes; watch for the pattern to break (S3007→S3008 will presumably continue with S3008 helper+Batch 3, so **5th cascade expected**). If cascade classes proliferate beyond 3-4 distinct types, propose a broader Playbook observation about pipeline-mode session cadence.

- **Fold E `future_trigger`** — `RateLimitingMiddleware.process_request` at `core/auth_middleware.py:915-925` has an inline `JsonResponse({'success': False, 'error': {'code': 'rate_limited', 'message': '...'}}, status=429)` — legacy Family B shape but NOT caught by `api_error / api_unauthorized / api_forbidden` grep (inline dict, not helper call). Same file as Batch 2, so it slipped past the file-scoped lint on structural grounds (regex targets helper-call patterns). Rigby recommendation: defer as Fold, not scope-creep this PR. Ticket: migrate inline 429 dict → Family E `build_user_facing_envelope(reason_code='rate_limited')` + `retry_after_seconds` hydration. ~15 min, but has 429-client-parsing behavior surface — worth its own PR + note in Batch 3 or as separate small refactor.

## Carry-forward

- **All S3006 carry-forwards unchanged EXCEPT:**
  - Fold A + Fold B (helper extraction candidate) — **PROMOTED to S3008 primary directive** (Chris ratified). Extract `emit_error_envelope(reason_code, request, hint=None) → JsonResponse` at `core/security/error_envelope.py` (auto-infers status from typical_status); prove on 1 test site; then Batch 3.
  - Fold C `future_trigger` (DRF-decorator refactor) — still open, still deferred.
  - Fold D `informational` (continuous cascade) — 4th trigger observed, class-distinguished (see Fold D above).

- **New S3007 carry-forwards:**
  - **Fold C `informational` (1st trigger)** — middleware-restart class for `feedback_recycle_after_merge`. Watch for 2nd.
  - **Fold E `future_trigger`** — `RateLimitingMiddleware` inline Family B 429 dict migration. Separate small PR; ~15 min but behavior-adjacent for 429 clients.

- **T-ENVELOPE-2-DEPRECATION queue after Batch 2:**
  - **S3008 primary directive:** Extract `emit_error_envelope()` helper (Fold A/B) → prove on 1 test site → migrate Batch 3 (`core/views_auto_distribution.py`, 25 call-sites) using the helper. Helper extraction ~30-60 min; Batch 3 ~1-2 sessions.
  - **Batch 4** (S3009-3010 candidate): `core/views_platform_integrations.py` (62 call-sites) — 2 sessions minimum, easier if helper is in place.
  - **Batch 5** (post-2-4): `core/api_helpers.py` disposition — separate substrate arc.

- **S3005 carry-forwards STILL OPEN** (unchanged):
  - Fold A/B/C `informational` (1st trigger each) — awaiting 2nd instance.

- **S3004 carry-forwards STILL OPEN** (unchanged).
- **S3003 carry-forwards STILL OPEN** (unchanged).
- **S3002 carry-forwards STILL OPEN** (unchanged).

## Governance

No Playbook amendments this session. No ADR authored. ADR-0007 §4.3 continues to be executed via T-ENVELOPE-2-DEPRECATION batches.

**Ratification workflow:**
- Rigby A1 joint agreement reached BEFORE implementation (per `feedback_claude_rigby_agree_first_chris_yes_no`) — mapping table + D1 + D2 all AGREE'd
- Chris D-verdict: "yes go with option A" (Batch 2 recommended path) + "let's do that" (defer helper extraction to S3008)
- Rigby A2 SIGN pre-merge with substantive tool_runs (per PLAYBOOK-7.7.2)
- Chris course-correction opportunity for Fold-A helper-extraction timing (per `feedback_plain_english_decision_framing_for_chris` — two questions plainly asked)
- Backend-middleware diff → **`make restart` used** (NOT `make celery-recycle`) per Fold C observation this session — informational rule refinement candidate

## Wrapper pin

Retired at close: `pa-03882637647b41a7` (S3006 mint). Minted for S3008 by `session_lifecycle close --label s3007-t-envelope-2-deprecation-batch-2`. Wrapper `tools/pa_local.sh` atomically rewritten and committed in the S3007 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.
