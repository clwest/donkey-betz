---
title: "SESSION 3008 — T-ENVELOPE-2-DEPRECATION helper extraction + Phase 2 proof site"
session: 3008
date: 2026-07-27
type: single_pr_close
merge_shas:
  - "efdef79f8"   # PR #3689 — emit_error_envelope() helper + 1-site proof
prs:
  - 3689
related_arcs:
  - "ADR-0007 Layered Envelope Policy (ratified S3005)"
  - "I-0301 Failure-Data Safety Contract (Family E authorizing substrate)"
consumes:
  - "S3007 close cascade — Fold A+B promoted to S3008 primary directive"
  - "ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION T-slot (helper + Phase 2)"
---

# S3008 — T-ENVELOPE-2-DEPRECATION helper extraction (Phase 1 + Phase 2)

**Status:** CLOSED. 1 feature PR merged. `emit_error_envelope()` helper added to `core/security/error_envelope.py`; 1 proof site converted in `core/auth_middleware.py` (`no_credentials`/`not_authenticated`/401 path). Batch 3 (25 sites in `core/views_auto_distribution.py`) deferred to S3009. HEAD `efdef79f8`.

## Session shape

Single-focus, single-PR, one-session close. Clean Flow B execution of Chris-ratified Option A: primary-directive routing (S3007 close cascade) → Rigby A1 SIGN joint agreement on helper signature (7 real tool_runs, AGREE D1-D5) → implementation → Rigby A2 SIGN pre-merge (7 real tool_runs, AGREE on D1/D2/D4/D5; DISAGREE on D3 due to Rigby-tool-surface limitation, not code) → merge (`--admin` per billing gate) → **`make restart` (NOT just `make celery-recycle`)** per S3007 Fold C middleware discipline → live-dispatch smoke confirming helper is the emit source → close cascade. **5th consecutive S3xxx→S3xxx+1 continuous cascade** (see Fold D).

## PR #3689 (`efdef79f8`) — emit_error_envelope() helper + Phase 2 proof site

**Scope (2 files, +44 / -7):**

### Phase 1 — Helper extraction (`core/security/error_envelope.py`)

Added `emit_error_envelope()` at lines 117-154, positioned between `build_user_facing_envelope()` (lines 72-114) and `build_operator_envelope()` (lines 158+) to group user-facing envelope constructors.

```python
def emit_error_envelope(
    reason_code: str,
    request,
    hint: Optional[dict[str, Any]] = None,
    status_code: Optional[int] = None,
    retry_after_seconds: Optional[int] = None,
) -> JsonResponse:
    payload = build_user_facing_envelope(
        reason_code=reason_code,
        retry_after_seconds=retry_after_seconds,
    )
    if status_code is None:
        status_code = get_reason(reason_code).typical_status
    logger.warning(
        "envelope_emit reason=%s support=%s endpoint=%s hint=%s",
        payload["reason_code"],
        payload["support_code"],
        request.path,
        hint or {},
    )
    return JsonResponse(payload, status=status_code)
```

### Phase 2 — 1-site proof (`core/auth_middleware.py:665-672`)

Site 4 of the 10 Batch-2 sites: `UnifiedTokenAuthenticationMiddleware.process_request` token-auth path, `not_authenticated`/401 when no session and no token. Simplest per Rigby A1 D5 — hint is minimal (`{'source': 'no_credentials'}`), no user context.

**Before (10 lines):**
```python
if not token:
    logger.warning(f"No authentication provided for {request.path}")
    payload = build_user_facing_envelope(reason_code='not_authenticated')
    logger.warning(
        "envelope_emit reason=%s support=%s endpoint=%s hint=%s",
        payload['reason_code'], payload['support_code'], request.path,
        {'source': 'no_credentials'},
    )
    return JsonResponse(payload, status=401)
```

**After (6 lines):**
```python
if not token:
    logger.warning(f"No authentication provided for {request.path}")
    return emit_error_envelope(
        reason_code='not_authenticated',
        request=request,
        hint={'source': 'no_credentials'},
    )
```

Pre-envelope operator log (line 667) preserved per Rigby A1 D3 operational note.

### Import surface

Line 24: `from core.security.error_envelope import build_user_facing_envelope, emit_error_envelope` (kept `build_user_facing_envelope` since 9 unmigrated Batch-2 sites still call it directly).

## Design decisions ratified

### D1 — status_code auto-inference from ReasonCode.typical_status

`ReasonCode` dataclass at `core/security/reason_codes.py:41-46` has `typical_status: int` field. Rigby A1 D2 verified all 10 Batch-2 sites match their typical_status (permission_denied→403, not_authenticated→401, busy→503). Helper defaults `status_code=None → get_reason(reason_code).typical_status`; callers override only for legitimate divergence (e.g. DRF Throttled). Zero behavioral change at converted site (401 preserved via typical_status).

### D2 — retry_after_seconds pass-through (no gating in helper)

`build_user_facing_envelope` already gates `retry_after_seconds` emission to `terminal_state in {RATE_LIMITED, BUSY}` (lines 107-112). Helper is a pure pass-through — no need to duplicate gating. Rigby A1 D4 AGREE.

### D3 — Non-widening (deferred future extensions)

Rigby A1 Z1 flagged 3 likely Batch-3 extensions: (1) `headers: dict` for Retry-After/WWW-Authenticate, (2) non-JsonResponse returns (DRF Response), (3) richer per-site logging. Explicit decision: do NOT widen now; `headers` is first planned extension if Batch 3 reveals need.

## Rigby SIGN quality signal

**A1 SIGN (pre-implementation):** 7 substantive tool_runs — `repo_tool.read_file` on `reason_codes.py`, `error_envelope.py`, and 2 spans of `auth_middleware.py` covering all 10 Batch-2 sites; `repo_tool.search` for envelope_emit + build_user_facing_envelope call-sites. AGREE on D1-D5. Z1 zoom-out surfaced 3 future extensions without blocking Phase 1.

**A2 SIGN (pre-merge):** 7 substantive tool_runs — helper block read (lines 115-155), import line 24, converted site 650-730, 2 grep passes for envelope_emit, and reason_codes.py verification for typical_status=401. AGREE on D1/D2/D4/D5. **D3 DISAGREE** — Rigby's `repo_tool.search` sample matches are truncated (max 30 per query, max 5 per file) and don't return exact counts, so she couldn't verify the "10 → 9 exactly" claim from her tool surface. Not a code blocker: Claude verified via direct shell `grep -c` (10 → 9 confirmed). Substantive per PLAYBOOK-7.7.2 — Rigby explicitly refused to invent the count, offered follow-up narrower search.

**Zoom-out asks (per `feedback_zoom_out_ask_per_rigby_sign`):** A2 Z1 surfaced Batch-3-kickoff prediction — most likely S3009 question = "why didn't we migrate the other 9 Batch-2 sites now?" Pre-answered in this handoff: Phase 2 was scoped to helper proof-of-life, not Batch-2 rewrite (S3008 START-HERE line 67); the other 9 sites can be batch-migrated at S3009 opening if desired, or absorbed into Batch 3.

## Verifications performed

At HEAD `efdef79f8`:
- `grep -c "envelope_emit reason=" core/auth_middleware.py` → **9** (was 10 pre-merge; 1 site's log line now inlined via helper)
- `python scripts/lint_no_deprecated_family_b.py` → `✅ ADR-0007 Family B deprecation lint OK (3 files checked)`
- `python manage.py check` → `System check identified no issues (0 silenced)`
- `python -c "from core.security.error_envelope import emit_error_envelope"` → import resolves
- `make restart` post-merge — Daphne + Celery + beat all restarted cleanly
- **Live-dispatch smoke:** `curl -s http://127.0.0.1:8000/api/workspaces/` → HTTP 401 + `{"support_code": "RUR-AUTH-260728-69de", "reason_code": "not_authenticated", "human_message": "You must be signed in to do that.", "retryable": false, "terminal_state": "DENIED", "timestamp": "..."}` (Family E shape confirmed live)
- **Log-source proof:** `django_debug.log` shows two-line emission — first `WARNING ... auth_middleware ... No authentication provided for /api/workspaces/` (preserved f-string operator log, line 667), then `WARNING ... error_envelope ... envelope_emit reason=not_authenticated support=RUR-AUTH-260728-69de endpoint=/api/workspaces/ hint={'source': 'no_credentials'}` (structured emit now sourced from **error_envelope** module, not auth_middleware — proves helper is the emit source vs pre-merge 21:06:24 smoke where source was `auth_middleware`)

## γ mechanism state

Layer 1 + Layer 2 + Layer 3 all LIVE at HEAD `efdef79f8`. Same as S3007 close. ADR-0007 §4.3 T-slot progress:

- **Files migrated (fully or partially):** 3 of 5 (views_odds_sports, views_revenue_analytics, auth_middleware — auth_middleware now 1 of 10 sites using helper, 9 still on raw 3-line pattern)
- **Helper substrate:** SHIPPED (this PR). Auto-infers status from typical_status; retry_after_seconds pass-through; hint dict opaque
- **REMAINING call-sites:** 87 (9 in auth_middleware still on raw pattern; 25 in views_auto_distribution; 62 in views_platform_integrations = 96 total remaining, though the 9 in auth_middleware are Batch-2-file-already-migrated so lint gate covers them)
- **Estimate:** Batch 3 (25 sites) ~1-2 sessions with helper. Batch 4 (62 sites) ~2 sessions with helper. Optional Batch 2b (retrofit 9 remaining auth_middleware sites) ~30 min if desired at S3009 open

## Folds

- **Fold A `future_trigger`** — retrofit 9 remaining auth_middleware sites to the helper. ~30 min at S3009 open if desired. Rigby A2 Z1 flagged this as the most likely S3009 kickoff question. Pre-answer: intentional deferral per Phase 2 scoping (proof-of-life, not Batch-2 rewrite). Batch 3 kickoff options: (a) Include 9-site retrofit as small warm-up PR before Batch 3; (b) Absorb into Batch 3 PR; (c) Leave as legacy pattern until Batch 3 gate; (d) Skip forever (they're already Family E, just using the old 3-line pattern). Recommendation: (a) — small warm-up PR keeps Batch 3 focused on views_auto_distribution.

- **Fold B `informational` (1st trigger)** — **Rigby Tool Gap Ledger candidate.** `repo_tool.search` returns `sample_matches` truncated at 30 total / 5 per file and does NOT return exact match counts (no `total_matches` field). This forced A2 SIGN D3 to DISAGREE ("cannot verify exactly 10→9") even though the code change is correct. Chris's `feedback_verify_at_raw_orm_before_trusting_tool_no_data` covers the "verify at raw layer" side; the corresponding Rigby-tool-surface side is: `repo_tool.search` needs `count_only=True` or `total_matches: int` field. Log to Rigby Tool Gap Ledger workspace deliverable (`b4503364-2573-4401-9e28-61a739e0ce50`, `deliverable_type='engineering_backlog'`) per `feedback_rigby_tool_gap_ledger`. Substrate fix candidate for future PA-tools sweep slice.

- **Fold C `2nd trigger` — middleware-restart discipline.** S3007 Fold C was 1st trigger (celery-recycle insufficient for middleware). This session's live-smoke required `make restart` from the outset (per prior fold learning) and worked correctly first time — successful pattern application, not a new trigger. But this is the **2nd session where a middleware-adjacent change required `make restart`**. Fold class is now `active watch` for feedback-rule refinement. Proposed rule addition to `feedback_recycle_after_merge`: "Any change to files loaded by Daphne request path (middleware / URLs / settings / installed_apps) requires `make restart` or `make recycle-all`, not `make celery-recycle`." Watch for 3rd trigger before drafting formal Playbook amendment.

- **Fold D `5th continuous cascade`** — S3007→S3008 = **helper-extraction-after-batch-completion**. Same "queue-drain across batches of same T-slot" class as S3006→S3007, but a distinct sub-shape (substrate-improvement between batches, not just next-batch). Continuous-cascade pattern now at 5 instances across ≥3 classes. Not sufficient for the S3006 Fold D Playbook proposal (that rule targeted "ratification → next-session implementation" specifically). Broader observation stays on the queue: if cascade classes proliferate beyond 4-5 distinct types, propose Playbook rule about pipeline-mode session cadence.

- **Fold E `future_trigger`** (inherited from S3007) — `RateLimitingMiddleware.process_request` at `core/auth_middleware.py:915-925` inline Family B 429 dict migration. Now easier with helper: `emit_error_envelope(reason_code='rate_limited', request=request, retry_after_seconds=N)`. Separate small PR candidate for S3009 or later.

## Carry-forward

- **All S3007 carry-forwards CLOSED or REPROMOTED:**
  - Fold A + Fold B → **CLOSED** (helper shipped this session)
  - Fold C → **PROMOTED to 2nd trigger** (this session's Fold C above)
  - Fold D → **PROMOTED to 5th cascade** (this session's Fold D above)
  - Fold E → carried forward unchanged (this session's Fold E)

- **New S3008 carry-forwards:**
  - **Fold A `future_trigger`** — retrofit 9 remaining auth_middleware sites to helper. Small warm-up PR at S3009 open recommended.
  - **Fold B `informational` (1st trigger)** — Rigby Tool Gap Ledger candidate (`repo_tool.search` no exact-count field).
  - **Fold C `2nd trigger`** — middleware-restart discipline. Watch for 3rd before formal rule proposal.
  - **Fold D `5th continuous cascade`** — S3xxx pipeline-mode observation. Watch for cascade-class break.

- **T-ENVELOPE-2-DEPRECATION queue after S3008:**
  - **S3009 primary directive candidate:** Batch 3 (`core/views_auto_distribution.py`, 25 sites) using helper — 1-2 sessions. Optional 9-site auth_middleware retrofit as warm-up PR.
  - **Batch 4** (S3010-3011 candidate): `core/views_platform_integrations.py` (62 sites) — 2 sessions minimum with helper.
  - **Batch 5** (post-2-4): `core/api_helpers.py` disposition — separate substrate arc.

- **All S3005/S3004/S3003/S3002 carry-forwards STILL OPEN** (unchanged this session).

## Governance

No Playbook amendments this session. No ADR authored. ADR-0007 §4.3 continues to be executed via T-ENVELOPE-2-DEPRECATION batches; helper substrate is a mid-arc improvement, not an ADR-level change.

**Ratification workflow:**
- Rigby A1 joint agreement reached BEFORE Phase 1 implementation (per `feedback_claude_rigby_agree_first_chris_yes_no`) — 7 tool_runs, AGREE on D1-D5
- Chris D-verdict: Option A at S3007 close (already ratified pre-session)
- Rigby A2 SIGN pre-merge with 7 substantive tool_runs (per PLAYBOOK-7.7.2) — AGREE on 4-of-5; D3 DISAGREE explicitly attributed to Rigby-tool-surface limitation, not code
- Merge via `gh pr merge --admin --squash --delete-branch 3689` (per `feedback_gh_pr_merge_admin_until_billing_fixed`)
- Backend-middleware diff → **`make restart` used** (NOT `make celery-recycle`) per S3007 Fold C observation — successful 2nd-trigger application of learned pattern

## Wrapper pin

Retired at close: `pa-54f4e59a9a504c7b` (S3007 mint). Minted for S3009 by `session_lifecycle close --label s3008-emit-error-envelope-helper`. Wrapper `tools/pa_local.sh` atomically rewritten and committed in the S3008 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.
