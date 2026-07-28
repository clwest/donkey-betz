# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3008 CLOSED. **`emit_error_envelope()` helper shipped + 1-site proof (Phase 1 + Phase 2 in single PR).** S3009 opens with Batch 3 (`core/views_auto_distribution.py`, 25 sites) using the new helper.

**1 PR merged this session** (helper extraction + Phase 2 proof site in `core/auth_middleware.py`).

**PR #3689 (`efdef79f8`) — emit_error_envelope() helper + Phase 2 proof.** Added `emit_error_envelope(reason_code, request, hint=None, status_code=None, retry_after_seconds=None) → JsonResponse` to `core/security/error_envelope.py` (lines 117-154). Auto-infers `status_code` from `ReasonCode.typical_status` when None. Pass-through for `retry_after_seconds` (already gated inside `build_user_facing_envelope`). Phase 2: converted 1 site at `core/auth_middleware.py:665-672` (no_credentials / not_authenticated / 401) from 10-line pattern to 6-line helper call. 9 remaining Batch-2 sites in the same file still use raw 3-line pattern (deferred per S3008 Phase 2 scoping = helper proof-of-life, not Batch-2 rewrite).

**Rigby SIGN quality signal:** A1 SIGN 7 substantive tool_runs (line-by-line verification of all 10 Batch-2 sites + reason_codes.py + error_envelope.py), AGREE D1-D5. A2 SIGN 7 substantive tool_runs (helper block + import + converted site + 2 grep passes + typical_status verification), AGREE D1/D2/D4/D5; **D3 DISAGREE explicitly attributed to Rigby-tool-surface limitation** (`repo_tool.search` doesn't return exact counts — Fold B / Rigby Tool Gap Ledger candidate), not code. Substantive per PLAYBOOK-7.7.2.

**Live-smoke log-source proof:** post-merge curl to `/api/workspaces/` returned Family E envelope with HTTP 401. `django_debug.log` shows two-line emission — first from `auth_middleware` module (preserved f-string operator log at line 667), then from `error_envelope` module (structured `envelope_emit` warning now sourced from helper, not inline). Compare with pre-merge 21:06:24 smoke where structured emit was sourced from `auth_middleware` — clean proof helper is now the emit source.

**HEAD at close:** `efdef79f8` + docs cascade PR (this file + handoff + INDEX + wrapper pin bump).

Full context:
- `docs/handoffs/SESSION_3008_T_ENVELOPE_2_DEPRECATION_HELPER_EXTRACTION.md` — single-PR close, 5 folds (A/B/C/D/E), forward carries
- `docs/adr/ADR-0007-layered-envelope-policy.md` — parent ADR (ratified S3005)
- `core/security/error_envelope.py:117-154` — helper implementation
- `scripts/lint_no_deprecated_family_b.py` — 3 files tracked (unchanged this session)

---

## S3009 primary directive — Batch 3 (`core/views_auto_distribution.py`, 25 sites) using the helper

### Option A — Batch 3 direct (recommended)

**Phase 1 — Rigby joint agreement on 25-site reason_code mapping (~15-30 min):**
Route full mapping table to Rigby for A1 SIGN. Each site: current status_code, proposed reason_code, hint dict, whether typical_status matches (auto-infer safe) or explicit override needed. Watch for Rigby A1 Z1 (S3008) shape predictions: `headers: dict` needed for Retry-After/WWW-Authenticate, non-JsonResponse returns, richer per-site logging. If any surface, decide widen-helper-first vs per-site workaround.

**Phase 2 — Migration (~1-2 sessions):**
25 sites → 25 × `return emit_error_envelope(reason_code=..., request=request, hint={...})`. Massive reduction from 5-line-per-site to 1-line-per-site. Add `core/views_auto_distribution.py` to `MIGRATED_FILES` in `scripts/lint_no_deprecated_family_b.py` (3 → 4 files tracked).

**Phase 3 — Ship + smoke:**
Standard: A2 SIGN → merge with `--admin` → `make restart` (views_auto_distribution loaded by Daphne — middleware-adjacent surface per S3007 Fold C 2nd-trigger discipline) → live-smoke a couple sites → close cascade.

### Option B — Warm-up: retrofit 9 remaining auth_middleware sites first

**Rigby A2 SIGN (S3008) Z1 flagged this as most likely S3009 kickoff question.** ~30 min small warm-up PR before Batch 3 — retrofit the 9 sites in `core/auth_middleware.py` that still use raw 3-line pattern to `emit_error_envelope()`. Reduces file from 9 remaining raw-pattern emit sites to 0. Keeps Batch 3 focused on views_auto_distribution. Pattern is identical to Phase 2 proof.

Alternative shapes:
- **B1** — Small warm-up PR (recommended if Chris wants Batch 3 unpolluted)
- **B2** — Absorb 9-site retrofit into Batch 3 PR (single larger PR)
- **B3** — Leave as legacy pattern indefinitely (they're already Family E, just verbose)

### Option C — Fold E: RateLimitingMiddleware inline 429 dict migration

Small separate PR (~15 min): migrate inline `JsonResponse({'success': False, 'error': {...}}, status=429)` at `core/auth_middleware.py:915-925` to `emit_error_envelope(reason_code='rate_limited', request=request, retry_after_seconds=N)`. Now trivial with helper. Has 429-client-parsing behavior surface — worth its own PR. Could pair with Option B warm-up.

### Option D — T-ENVELOPE-6 Telemetry hookup (inherited from S3007)

`componentDidCatch` at `frontend/src/components/ErrorBoundary.tsx` is annotated as T-ENVELOPE-6 hook-point. Handler at `queryClientErrorHandler.ts` could emit structured logs. ~30-60 min. Deferred through multiple sessions.

### Option E — Different arc entirely

- v2 fold ledger drain (12+ items still open from S2991-S3006)
- Fresh research arc (2100 RAG / 2300 Mobile / 2600 PA)
- Rigby Tool Gap Ledger drain (`repo_tool.search` exact-count field from S3008 Fold B)
- Chris's own priority

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3008 handoff.
4. Read `core/security/error_envelope.py:117-154` (helper — read the docstring, understand auto-inference semantics).
5. Read `core/views_auto_distribution.py` (target file for Batch 3 — scan the 25 error-return sites; understand hint shapes + status codes).
6. Optional pre-response state probes:
   - `git log --oneline -8` — should show docs cascade → `efdef79f8` (PR #3689 helper+proof) → `21ed05899` (S3007 close cascade) → `d00dd5b05` (PR #3687 Batch 2) → `c8f608087` (S3006 close cascade).
   - `python scripts/lint_no_deprecated_family_b.py --list` — confirm 3 tracked files (`views_odds_sports.py`, `views_revenue_analytics.py`, `auth_middleware.py`).
   - `grep -c "envelope_emit reason=" core/auth_middleware.py` — should return **9** (1 site converted to helper; 9 remaining raw).
   - `grep -c "api_error\|api_unauthorized\|api_forbidden" core/views_auto_distribution.py` — establish Batch 3 baseline site count.

**Joint recommendation at close:** Preferred order for S3009 is **B1+A (small 9-site retrofit warm-up PR then Batch 3)** > A (Batch 3 direct) > B2 (bundled retrofit+Batch 3) > C (Fold E RateLimiting standalone) > D (T-ENVELOPE-6) > E (other). Reason: Rigby A2 Z1 flagged the 9-retrofit as the most-likely first S3009 question; a ~30 min warm-up PR removes the ambiguity and lets Batch 3 land clean. Route Batch 3 mapping table to Rigby A1 SIGN BEFORE migration.

---

## S3009 carry-forward seeds

### New carry-forward from S3008

- **Fold A `future_trigger`** (PROMOTED to S3009 Option B recommendation) — retrofit 9 remaining auth_middleware sites to `emit_error_envelope()` helper. Small warm-up PR (~30 min) at S3009 open recommended before Batch 3.
- **Fold B `informational` (1st trigger)** — **Rigby Tool Gap Ledger candidate.** `repo_tool.search` returns `sample_matches` truncated (30 total / 5 per file) with no `total_matches: int` field. Forces DISAGREE on any exact-count verification even when the code is correct. Substrate fix: add `count_only=True` or `total_matches` to `repo_tool.search` response. Log to Rigby Tool Gap Ledger workspace `b4503364-2573-4401-9e28-61a739e0ce50` (`deliverable_type='engineering_backlog'`) per `feedback_rigby_tool_gap_ledger`.
- **Fold C `2nd trigger`** — middleware-restart discipline. S3007 = 1st trigger (learned rule); S3008 = 2nd trigger (successful pattern application, restart used from outset). Proposed rule refinement to `feedback_recycle_after_merge`: "Any change to files loaded by Daphne request path (middleware / URLs / settings / installed_apps) requires `make restart` or `make recycle-all`, not `make celery-recycle`." Watch for 3rd trigger before drafting formal Playbook amendment.
- **Fold D `5th continuous cascade` (class-distinguished sub-shape)** — S3007→S3008 = "helper-extraction-after-batch-completion" — sub-shape of "queue-drain across batches of same T-slot" class. Continuous-cascade pattern now at 5 instances across ≥3 classes. Broader observation stays on the queue; watch for cascade-class break.
- **Fold E `future_trigger`** (carried from S3007) — `RateLimitingMiddleware.process_request` inline Family B 429 dict at `core/auth_middleware.py:915-925`. Now trivial with helper (~15 min). Option C at S3009 or bundle with Option B.

### T-ENVELOPE-2-DEPRECATION queue after helper

- **S3009 (primary directive candidate):** Batch 3 (`core/views_auto_distribution.py`, 25 sites) — 1-2 sessions with helper. Optional 9-site auth_middleware retrofit as warm-up PR (Option B1).
- **Batch 4** (S3010-3011): `core/views_platform_integrations.py` (62 sites) — 2 sessions minimum with helper.
- **Batch 5** (post-2-4): `core/api_helpers.py` disposition — separate substrate arc.

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

- **Fold A** — session-shape observation. **5th concrete continuous-cascade** now with S3007→S3008 (class-distinguished sub-shape; see S3008 Fold D). Watch for cascade-class break.
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

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session. Candidate seeds from S3005 Folds A/B/C + S3006 Fold D + S3007 Fold C (middleware-restart) + S3008 Fold C (middleware-restart 2nd trigger) still awaiting further triggers before Playbook / feedback amendment proposal.
- **ADR corpus:** ADR-0001 through ADR-0007. ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION helper substrate SHIPPED; 3-of-5 files migrated (Batches 1+2). Batch 3 (views_auto_distribution 25 sites) + Batch 4 (views_platform_integrations 62 sites) remaining with helper.
- **Spec→ship contract:** PLAYBOOK-7.7.1. 1× Flow B clean spec→ship: primary-directive → Rigby A1 joint agreement → implementation → Rigby A2 SIGN → merge → restart → live-smoke → close.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. 2× Rigby SIGN cycles (A1 + A2), 7+7 = 14 total real tool_runs. 0 STRENGTHENs needed. 1× substantive DISAGREE (A2 D3) explicitly attributed to Rigby-tool-surface limitation, not code. Substantive.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Not exercised this session (Chris ratified Option A at S3007 close; no new decision routing).
- **Recycle discipline:** middleware/URL/settings/installed-apps diff → `make restart` (NOT `make celery-recycle`) per S3007 Fold C (now S3008 Fold C 2nd trigger). Frontend diff → `make recycle-all` per existing `feedback_recycle_after_merge`.

---

## Wrapper pin note

The active PA conversation pin at S3008 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3008 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3008 is a clean single-focus implementation session executing ADR-0007's mid-arc helper-substrate improvement:** Rigby A1 joint agreement on helper signature (7 tool_runs, AGREE D1-D5) → implementation → Rigby A2 SIGN AGREE 4-of-5 (D3 DISAGREE = Rigby-tool-surface limitation, not code) → merge → make restart (Daphne+Celery) → live-dispatch smoke with log-source proof (helper is the emit source) → close cascade. ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION helper substrate now SHIPPED; 87 remaining call-sites (25 Batch 3 + 62 Batch 4) will compress from 5-line-per-site to 1-line-per-site via the helper.
