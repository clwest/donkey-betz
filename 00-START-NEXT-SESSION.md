# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3007 CLOSED. **T-ENVELOPE-2-DEPRECATION Batch 2 shipped (10 auth-middleware sites + lint gate extended).** S3008 opens with helper extraction (Fold A/B promoted) → prove on 1 test site → Batch 3.

**1 PR merged this session** (Batch 2 migrations + lint gate extension).

**PR #3687 (`d00dd5b05`) — T-ENVELOPE-2-DEPRECATION Batch 2.** 10 Family B error call-sites migrated to Family E in `core/auth_middleware.py` (`token_auth_required` decorator + `UnifiedTokenAuthenticationMiddleware.process_request` — session-auth path + token-auth path). Per-site pattern from Batch 1 reused verbatim: `payload → logger.warning(reason+support+endpoint+hint) → JsonResponse`. Details payload dropped per safety-contract §3.1 allowlist. Site 6 (`TokenValidationInfrastructureError` / 503) → `busy` (retryable=True, terminal_state=BUSY) preserves S1171 fix intent. Lint gate `MIGRATED_FILES` extended 2 → 3 files (machinery unchanged from S3006).

**Rigby SIGN quality signal:** A1 SIGN 4 substantive tool_runs (line-by-line site verification + reason_code enum + Batch 1 pattern), AGREE on mapping table + D1 (busy) + D2 (decorator in scope). A2 SIGN 4 substantive tool_runs (spot-check sites 1/6/10 + import surface + lint config), AGREE ship-ready, **no STRENGTHEN required**. Substantive per PLAYBOOK-7.7.2. Zoom-out asks yielded 3 folds (see handoff Folds A-E).

**Middleware-restart discipline discovered:** first live-smoke curl after `make celery-recycle` returned legacy Family B shape; second curl after `make restart` returned Family E. Middleware runs in Daphne, not Celery workers → `make celery-recycle` alone insufficient for middleware/URL/settings/installed-apps changes. Fold C `informational` (1st trigger) — watch for 2nd occurrence before proposing feedback rule refinement.

**HEAD at close:** `d00dd5b05` + docs cascade PR (this file + handoff + INDEX + wrapper pin bump).

Full context:
- `docs/handoffs/SESSION_3007_T_ENVELOPE_2_DEPRECATION_BATCH_2.md` — single-PR close, 5 folds (A/B/C/D/E), forward carries
- `docs/adr/ADR-0007-layered-envelope-policy.md` — parent ADR (ratified S3005)
- `scripts/lint_no_deprecated_family_b.py` — 3 files tracked (Batch 1 + Batch 2)

---

## S3008 primary directive — Extract `emit_error_envelope()` helper → prove on 1 test site → migrate Batch 3

### Option A — Helper extraction + Batch 3 (recommended, Chris ratified S3007 close)

**Phase 1 — Helper extraction (~30-60 min):**
Add to `core/security/error_envelope.py`:

```python
from django.http import JsonResponse
from core.security.reason_codes import get_reason

def emit_error_envelope(
    reason_code: str,
    request,
    hint: dict | None = None,
    status_code: int | None = None,
    retry_after_seconds: int | None = None,
) -> JsonResponse:
    """Emit a Family E user-facing envelope with structured operator log.

    Wraps the 3-line pattern used across T-ENVELOPE-2-DEPRECATION batches:
        payload = build_user_facing_envelope(reason_code=X)
        logger.warning("envelope_emit reason=%s support=%s endpoint=%s hint=%s", ...)
        return JsonResponse(payload, status=X)

    status_code defaults to ReasonCode.typical_status per Fold B — override
    only when caller has a legitimate reason (e.g., DRF Throttled semantics).
    """
    payload = build_user_facing_envelope(
        reason_code=reason_code,
        retry_after_seconds=retry_after_seconds,
    )
    if status_code is None:
        status_code = get_reason(reason_code).typical_status
    logger.warning(
        "envelope_emit reason=%s support=%s endpoint=%s hint=%s",
        payload['reason_code'], payload['support_code'], request.path,
        hint or {},
    )
    return JsonResponse(payload, status=status_code)
```

**Phase 2 — Prove on 1 test site (~15 min):**
Pick 1 site in the already-migrated `core/auth_middleware.py` (suggest site 5 or 7 — simplest, no user-context). Convert 5-line pattern → 1-line `return emit_error_envelope('not_authenticated', request, hint={'source': 'no_credentials'})`. Verify grep + lint + Django check + live-smoke curl still returns Family E. Do NOT rewrite all 10 sites — the point is helper proof-of-life, not Batch-2 rewrite.

**Phase 3 — Batch 3 (~1-2 sessions):**
Migrate `core/views_auto_distribution.py` (25 call-sites) using the new helper. All 25 sites should be 1-line `return emit_error_envelope(...)` — massive reduction from 5-line pattern.

**Rigby joint agreement needed BEFORE Phase 1:** helper signature (arg order, defaults, hint schema); Fold-B status-inference boundary (when to override typical_status).

### Option B — Batch 3 without helper

Skip helper; per-site 5-line pattern for all 25 sites in views_auto_distribution.py. Not recommended (Chris + Rigby + Claude joint agreement S3007 = extract first).

### Option C — T-ENVELOPE-6 Telemetry hookup (logs-only interim)

`componentDidCatch` at `frontend/src/components/ErrorBoundary.tsx` is annotated as T-ENVELOPE-6 hook-point. Handler at `queryClientErrorHandler.ts` could emit structured logs. **30-60 min estimate.** Deferred through S3006-S3007 — could pick up here if T-ENVELOPE-2 arc needs a breather.

### Option D — Different arc entirely

- Fold E from S3007: `RateLimitingMiddleware` inline 429 dict migration (~15 min + client-behavior surface)
- v2 fold ledger drain (12+ items still open from S2991-S3006)
- Fresh research arc (2100 RAG / 2300 Mobile / 2600 PA)
- Chris's own priority

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3007 handoff.
4. Read `core/security/error_envelope.py` (existing envelope infrastructure; helper lands there).
5. Read `core/auth_middleware.py` (pick test site for Phase 2).
6. Optional pre-response state probes:
   - `git log --oneline -8` — should show docs cascade → `d00dd5b05` (PR #3687 Batch 2) → `c8f608087` (S3006 close cascade) → `197174a60` (PR #3685 Batch 1) → `8d2d64b13` (S3005 close cascade) → `957fee61f` (PR #3683 ADR-0007) → `f97501c3a` (S3004 close cascade).
   - `python scripts/lint_no_deprecated_family_b.py --list` — confirm 3 tracked files.
   - `grep -c "envelope_emit reason=" core/auth_middleware.py` — confirm 10 envelope emits (Batch 2 landed).

**Joint recommendation at close:** Preferred order for S3008 is **A (helper extraction + Batch 3)** > D (Fold E: RateLimitingMiddleware) > B (Batch 3 without helper — not recommended) > C. Reason: Chris ratified helper-extraction defer at S3007 close specifically to open S3008 with it; 87 remaining sites (25 Batch 3 + 62 Batch 4) benefit from 1-line-per-site vs 5-line-per-site pattern. **Route helper signature to Rigby first before Phase 1 implementation.**

---

## S3008 carry-forward seeds

### New carry-forward from S3007

- **Fold A + Fold B combined** (PROMOTED to S3008 primary directive) — `emit_error_envelope(reason_code, request, hint=None, status_code=None, retry_after_seconds=None) → JsonResponse` helper wrapping 3-line pattern + auto-inferring `status` from `ReasonCode.typical_status`. **2nd concrete trigger** confirmed pattern is stable.
- **Fold C `informational` (1st trigger)** — `feedback_recycle_after_merge` middleware-restart class. Live-smoke evidence: `make celery-recycle` insufficient for Daphne-loaded code (middleware / URLs / settings / installed_apps). Watch for 2nd occurrence before proposing feedback rule refinement.
- **Fold D `4th continuous cascade` (class-distinguished)** — S3006→S3007 = queue-drain across batches of same T-slot. DIFFERENT class from prior three S3xxx cascades. Not sufficient for S3006 Fold D Playbook proposal (that targeted ratification→implementation specifically). Log as separate observation. If cascade classes proliferate beyond 3-4 distinct types, propose broader Playbook observation.
- **Fold E `future_trigger`** — `RateLimitingMiddleware.process_request` at `core/auth_middleware.py:915-925` has inline `JsonResponse({'success': False, 'error': {...}}, status=429)` — legacy Family B shape, NOT caught by regex-based lint (inline dict, not helper call). ~15 min migration but has 429-client-parsing behavior surface. Separate small PR candidate.

### T-ENVELOPE-2-DEPRECATION queue after Batch 2

- **S3008 (primary directive):** Helper extraction + Phase 2 proof + Batch 3 (`core/views_auto_distribution.py`, 25 sites) — 1-2 sessions with helper
- **Batch 4** (S3009-3010): `core/views_platform_integrations.py` (62 sites) — 2 sessions minimum, easier if helper is in place
- **Batch 5** (post-2-4): `core/api_helpers.py` disposition — separate substrate arc

### Carry-forward from S3006 (STILL OPEN)

- **Fold C `future_trigger`** — DRF-decorator refactor for inline auth checks. 5 sites in views_revenue_analytics.py used `if not request.user.is_authenticated: return 401`. Idiomatic DRF replacement is decorator-based. Bigger behavioral surface; deferred; separate arc.
- **Operator-envelope-from-explicit-emissions** wiring — full substrate change OR new helper. Currently: interim structured logging. Not on roadmap.

### Carry-forward from S3005 (STILL OPEN)

- **Fold A `informational` (1st trigger)** — PLAYBOOK-7.7.1 abort-early clause firing at pre-execution probe. Watch for 2nd.
- **Fold B `informational` (1st trigger)** — ADR-baseline post-ratification drift. Watch for 2nd.
- **Fold C `informational` (1st trigger)** — `refines:` frontmatter field for §-scoped amendment. Watch for 2nd.

### Carry-forward from S3004 (STILL OPEN)

- **Fold A `2nd trigger`** — Fold-Drain-Same-Surface pattern. Watch for 3rd.
- **Fold B `informational` (1st trigger)** — shared-const derived-union frontend pattern. Watch for 2nd.
- **Fold C `same_pr_mitigatable_deferred_to_next_arc`** — dedicated `/vip/expired` landing page.
- **Fold D `informational` (1st trigger)** — Rigby repo_tool line-1 read-display truncation false-positive. Watch for 2nd.

### Carry-forward from S3003 (STILL OPEN)

- **Fold A `informational` (1st trigger)** — risk-gate T-slot vs T-ENVELOPE-N scoping. Watch for 2nd.
- **Fold C `informational` (1st trigger)** — Django reverse-O2O test cache-bust pattern. Watch for 2nd.

### Carry-forward from S3002 (STILL OPEN)

- **Fold A** — session-shape observation. **4th concrete continuous-cascade** now with S3006→S3007 (class-distinguished; see S3007 Fold D). Watch for 5th.
- **Fold C `informational` (T-ENVELOPE-0 dev-only)** — `componentDidCatch` fires twice in dev under StrictMode.
- **Fold D — ADR successor discipline VALIDATED PATTERN.** ADR-0005 ↔ ADR-0006.

### Carry-forward from S3001 (STILL OPEN)

- **Fold B `informational`** — future ADR-N misread risk. "γ ratified" implying interceptor policy is preserved by §3.3 wording.
- **Fold C `informational` (1st trigger)** — potential Playbook rule candidate: verify target research slot state before accepting scope. Watch for 2nd.

### Carry-forward from S3000 (STILL OPEN)

- **Fold A `informational` (1st trigger)** — potential Playbook rule candidate: reproduce failure at thinnest interface. Watch for 2nd.
- **Fold B `informational`** — residual APIClient-forcing shapes.

### Carry-forward from S2999 (STILL OPEN)

- **Fold B `active watch`** — metadata accretion governance. 4 detector keys currently. Trigger: 5+ keys OR 2+ consumers.
- **Fold C** — Rigby Tool Gap Ledger. File:line-only scope of consumer verifier.

### Carry-forward from S2998 (STILL OPEN)

- **Fold A `future_trigger`** — force=true × factory dedupe semantic mismatch.
- **Fold B `future_trigger`** — force re-dispatch could emit DeliverableEvent breadcrumb.
- **Fold C** — Rigby Tool Gap Ledger.

### Carry-forward from S2997 (STILL OPEN)

- **Fold B `future_trigger`** — dedupe strictness on stale-ref ACs.
- **Fold F** — Rigby Tool Gap Ledger. `orm_inspect_tool` doesn't support `metadata__<key>=value` JSON-path lookups.

### Carry-forward from S2996 (STILL OPEN)

- **Fold C `future_trigger`** — staleness toast reinforcement.
- **Fold E** — Rigby Tool Gap Ledger (sharpened). No in-UI Recheck action.

### Carry-forward from S2995 (STILL OPEN)

- **Fold C `future_trigger`** — staleness metadata → dedicated JSONField.
- **Fold D `future_trigger`** — periodic staleness beat.
- **Fold E** — Rigby Tool Gap Ledger. Metadata accretion governance.
- **Fold F `future_trigger`** — WorkspacePageNew param preservation.

### Carry-forward from S2994 (STILL OPEN)

- **Fold B `future_trigger`** — inline-helper density.
- **Fold C `future_trigger`** — Deliverables-tab type badge.
- **Fold D** — Rigby Tool Gap Ledger.

### Carry-forward from S2993 (STILL OPEN)

- **Fold B ledger candidate** — dry-run preview for send-to-rigby.
- **Fold C future_trigger** — executable-prompt tightening.

### Carry-forward from S2992 (STILL OPEN)

- **Signal-tweak follow-up for `finding_type` classifier** (2 acceptable-misses).
- **Data-migration-vs-management-command pattern** (3rd-trigger check).

### Carry-forward from S2991 (STILL OPEN)

- **Dry-run counts pattern for future bulk-write migrations** (3rd-trigger check).
- **Contract-lock-in guardrail** — updated set as of S2991.

### Carry-forward from S2989-S2990 (STILL OPEN)

- **F-D3-tracker-scope wire-up** — ~1 session.
- **F-D2-broad LLM-bypass audit spec** — ~1 session.
- **Reconcile Chris's 1805 cap-drift via `memory_hygiene_audit --apply`.** ~30 min.
- **Canonical Briefing v2 scope toggle.** ~1-2 hr.
- **Substrate fix for `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`.** ~1 session.
- **Send-to-Rigby follow-ups from S2988 (STILL OPEN).**

### Older carry-forward (STILL OPEN)

- **Chris browser visual check on S2985 Canonical Briefing tab strip.** ~5 min.
- **Rigby `claude_code_tool` safeguards.** Log to Rigby Tool Gap Ledger.
- **Chris browser visual check on S2984 arcs section.** ~5 min.
- **Systemic auth-XHR treatment (STILL OPEN from S2984 as Fold).**
- **Live-dispatch smoke on S2982 stage-doc guardrails.** ~15 min.
- **Exercise PLAYBOOK-7.7.4 against a sibling repo.**
- **Browser UX smoke on S2980 Theme Signals UX upgrade.** ~5 min.
- **Phase B Theme Signals — "Why now" LLM summarizer.** ~1 session.
- **Phase B Theme Signals — who-benefits/who-loses.** ~1-2 sessions.
- **Theme Signals — sub-tab persistence via localStorage.** ~30 min.
- **Rigby Tool Gap Ledger — Fold D from S2982.** DB uniqueness constraint on `AgentExecution.celery_task_id`. ~30-60 min.
- **Fold B `future_trigger` from v0.8.0** — fold-authoring evidence-admission helper. 3-trigger threshold NOT yet met.
- **Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for both v0.9.0 and v0.10.0.
- **Live browser smoke on S3004 VIP-expired modal.** ~5 min.
- **ADR-0007 twin-mirror deliverable** — post-close Rigby dispatch to workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` for ratification-record provenance.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session. Candidate seeds from S3005 Folds A/B/C + S3006 Fold D + S3007 Fold C (middleware-restart) still awaiting further triggers before Playbook / feedback amendment proposal.
- **ADR corpus:** ADR-0001 through ADR-0007. ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION now 3-of-5 files migrated (Batches 1+2).
- **Spec→ship contract:** PLAYBOOK-7.7.1. 1× Flow B clean spec→ship: primary-directive → Rigby A1 joint agreement → Chris course-correction opportunity → implementation → Rigby A2 SIGN → merge → restart → live-smoke → close.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. 2× Rigby SIGN cycles (A1 + A2), 4+4 = 8 total real tool_runs. 0 STRENGTHENs needed. Substantive.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Two questions plainly asked for helper-extraction defer decision (per `feedback_plain_english_decision_framing_for_chris`).
- **Recycle discipline:** middleware/URL/settings/installed-apps diff → `make restart` (NOT `make celery-recycle`) per S3007 Fold C observation. Frontend diff → `make recycle-all` per existing `feedback_recycle_after_merge`.

---

## Wrapper pin note

The active PA conversation pin at S3007 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3007 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3007 is a clean single-focus implementation session executing ADR-0007's obligated Batch 2:** Rigby A1 joint agreement on reason_code mapping + 2 open decisions → Chris course-correction opportunity → 10 call-site migration + lint gate extension → Rigby A2 SIGN AGREE ship-ready (no STRENGTHEN) → merge → make restart (Daphne+Celery) → live-dispatch smoke confirming Family E envelope shape → close cascade. ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION now 3-of-5 files complete; 2 files (87 call-sites) remain across Batches 3-4. S3008 opens with helper extraction to compress remaining 87 sites from 5-line to 1-line per site.
