# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3006 CLOSED. **T-ENVELOPE-2-DEPRECATION Batch 1 shipped (11 call-sites + lint gate).** S3007 opens with Batch 2 (auth_middleware.py, 10 sites) or Option B/C.

**1 PR merged this session** (Batch 1 migrations + lint gate).

**PR #3685 (`197174a60`) — T-ENVELOPE-2-DEPRECATION Batch 1.** 11 Family B error call-sites migrated to Family E across 2 files (`views_odds_sports.py`, `views_revenue_analytics.py`). Per-site pattern: `assign payload → logger.warning(reason+support+endpoint+hint) → JsonResponse`. Details payload dropped per safety-contract §3.1 allowlist; debuggability preserved via structured logging. New `scripts/lint_no_deprecated_family_b.py` file-scoped zero-tolerance lint + `.github/workflows/check-envelope-migration.yml` CI workflow.

**Rigby A2 SIGN quality signal:** 10+ real tool_runs across two turns. 2 STRENGTHEN applied pre-merge (guardrails cross-link + operator-context preservation via structured logging). Substantive per PLAYBOOK-7.7.2.

**HEAD at close:** `197174a60` + docs cascade PR (this file + handoff + INDEX + wrapper pin bump).

Full context:
- `docs/handoffs/SESSION_3006_T_ENVELOPE_2_DEPRECATION_BATCH_1.md` — single-PR close, 4 folds, forward carries
- `docs/adr/ADR-0007-layered-envelope-policy.md` — parent ADR (ratified S3005)
- `scripts/lint_no_deprecated_family_b.py` + `.github/workflows/check-envelope-migration.yml` — new lint gate

---

## S3007 primary directive — T-ENVELOPE-2-DEPRECATION Batch 2 (auth_middleware.py) or Option B/C

### Option A — T-ENVELOPE-2-DEPRECATION Batch 2 (recommended)

Migrate `core/auth_middleware.py` — 10 call-sites. Estimate ~1 session. Middleware placement invariants require extra scrutiny per PLAYBOOK 3.2.3-ish patterns (middleware runs on every request; regressions have larger blast radius than view-file changes). Rigby joint agreement on reason_code mapping + any middleware-invariant preservation should precede implementation.

**Pattern from Batch 1 (reuse):**
```python
payload = build_user_facing_envelope(reason_code=X)
logger.warning("envelope_emit reason=%s support=%s endpoint=%s [hint=%s]",
               payload['reason_code'], payload['support_code'], request.path,
               {redacted_hint})
return JsonResponse(payload, status=X)
```

**Fold-A candidate check for Batch 2:** if Batch 2 uses the same 3-line pattern 10 more times, that's the 2nd concrete instance (Batch 1 was 1st). Fold-B combined check: are we passing `status=X` explicitly when `ReasonCode.typical_status` is already in the enum? If both hold, propose helper extraction: `emit_error_envelope(reason_code, request, hint=None) → JsonResponse` (auto-infer status).

### Option B — Substrate helper extraction (Fold A/B follow-on if 2 batches ship)

If Batch 2 confirms the pattern, extract `emit_error_envelope()` helper at `core/security/error_envelope.py` before Batch 3. Reduces per-site code from ~5 lines to 1 line. ~30-60 min.

### Option C — T-ENVELOPE-6 Telemetry hookup (logs-only interim)

`componentDidCatch` at `frontend/src/components/ErrorBoundary.tsx` is annotated as T-ENVELOPE-6 hook-point. Handler at `queryClientErrorHandler.ts` could emit structured logs. **30-60 min estimate.**

### Option D — Different arc entirely

- v2 fold ledger drain (10+ items still open from S2991-S3005)
- Fresh research arc (2100 RAG / 2300 Mobile / 2600 PA)
- Chris's own priority

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3006 handoff.
4. Read `core/auth_middleware.py` if Batch 2 chosen — grep `api_error|api_unauthorized|api_forbidden` for the 10 call-sites.
5. Optional pre-response state probes:
   - `git log --oneline -8` — should show docs cascade → `197174a60` (PR #3685 Batch 1) → `8d2d64b13` (S3005 close cascade) → `957fee61f` (PR #3683 ADR-0007) → `f97501c3a` (S3004 close cascade) → `85fffdfc1` (PR #3681 §3.5 UX widening).
   - `python scripts/lint_no_deprecated_family_b.py --list` — confirm 2 tracked files.

**Joint recommendation at close:** Preferred order for S3007 is **A (Batch 2: auth_middleware.py)** > B (helper extraction, IF Batch 2 confirms the 3-line pattern) > C (T-ENVELOPE-6 telemetry) > D. Reason: momentum on T-ENVELOPE-2-DEPRECATION; smallest of the remaining 3 files; middleware invariants worth first-touch care. **Route to Rigby first before presenting to Chris.**

---

## S3007 carry-forward seeds

### New carry-forward from S3006

- **Fold A + Fold B combined** — helper extraction candidate: `emit_error_envelope(reason_code, request, hint=None) → JsonResponse` wrapping 3-line pattern + auto-inferring `status` from `ReasonCode.typical_status`. Watch for 2nd batch (Batch 2 = 2nd instance). If pattern confirmed, extract in Batch 3 or as separate refactor.
- **Fold C `future_trigger`** — DRF-decorator refactor for inline auth checks. 5 sites in views_revenue_analytics.py used `if not request.user.is_authenticated: return 401`. Idiomatic DRF replacement is decorator-based. Bigger behavioral surface; deferred; separate arc.
- **Fold D `informational` (3rd trigger)** — S3xxx continuous-cascade session-shape pattern. S3003→S3004 (Fold-Drain-Same-Surface), S3004→S3005 (Substrate-invalidation-cascade), S3005→S3006 (Implementation-of-just-ratified-ADR). Watch for 4th; if hits, propose Playbook rule codifying automatic batch-1 dispatch in ratifying session's close cascade.
- **Operator-envelope-from-explicit-emissions** wiring — full substrate change OR new helper. Currently: interim structured logging. Not on roadmap.

### T-ENVELOPE-2-DEPRECATION queue after Batch 1

- **Batch 2** (S3007): `core/auth_middleware.py` (10 sites) — ~1 session, middleware-invariant care
- **Batch 3** (S3008): `core/views_auto_distribution.py` (25 sites) — 2 sessions if verbose
- **Batch 4** (S3009-3010): `core/views_platform_integrations.py` (62 sites) — 2 sessions minimum
- **Batch 5** (post-2-4): `core/api_helpers.py` disposition — separate substrate arc

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

- **Fold A** — session-shape observation. **3rd concrete continuous-cascade** now (S3003→S3004 + S3004→S3005 + S3005→S3006). Watch for 4th.
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

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session. Candidate seeds from S3005 Folds A/B/C + S3006 Fold D (3rd trigger continuous-cascade) still awaiting further triggers before Playbook amendment proposal.
- **ADR corpus:** ADR-0001 through ADR-0007. ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION now 2-of-5 files migrated (Batch 1).
- **Spec→ship contract:** PLAYBOOK-7.7.1. 1× Flow B clean spec→ship: primary-directive → Rigby joint agreement → Chris course-correction opportunity → implementation → verification → A2 SIGN → merge → recycle → close.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. 1× Rigby A2-pre-merge SIGN with 10+ real tool_runs. 2 STRENGTHEN applied. Substantive.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Course-correction framing (variant on decision framing) used per `feedback_plain_english_decision_framing_for_chris`.
- **Recycle discipline:** backend-only diff → `make celery-recycle` (NOT `make recycle-all`) per `feedback_recycle_after_merge`.

---

## Wrapper pin note

The active PA conversation pin at S3006 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3006 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3006 is a clean single-focus implementation session executing the just-ratified ADR-0007's obligated Batch 1:** joint reason_code mapping agreement → Chris course-correction opportunity → 11 call-site migration + lint gate + CI workflow → Rigby A2 SIGN with 2 STRENGTHEN applied (guardrails cross-link + operator-context preservation via structured logging) → merge → celery-recycle → close cascade. ADR-0007 §4.3 T-ENVELOPE-2-DEPRECATION now 2-of-5 files complete; 3 files (97 call-sites) remain across Batches 2-4.
