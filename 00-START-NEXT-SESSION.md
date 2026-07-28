# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3005 CLOSED. **ADR-0007 ratified (Layered Envelope Policy). T-ENVELOPE-2 CLOSED-as-shipped; new T-ENVELOPE-2-DEPRECATION T-slot introduced.** S3006 opens with T-ENVELOPE-2-DEPRECATION migration or Option B/C/D.

**1 PR merged this session** (ADR-0007 governance ratification).

**PR #3683 (`957fee61f`) — ADR-0007 Layered Envelope Policy (refines ADR-0006 §3.2).** Spec-invalidation caught at S3005 open: EXCEPTION_HANDLER already wired (PR #3085 I-0301) emitting Family E (safety-contract envelope), not Family B (`APIResponseEnvelope`). ADR-0005 T-ENVELOPE-2 CLOSED-as-shipped. New layered policy: Family E for errors, Family B for success responses only. 12 Family B error methods DEPRECATED with pointers to ADR-0007. New T-ENVELOPE-2-DEPRECATION T-slot introduced for 108-call-site migration across 5 files.

**Rigby T1 SIGN quality signal:** 8 real tool_runs across three turns. 5 STRENGTHEN applied pre-merge (§8 citation, 108-count correction, CLOSED+new-slot framing, semantic-clarity note, class banner + lint obligation). Substantive per PLAYBOOK-7.7.2, not rubber-stamp.

**HEAD at close:** `957fee61f` + docs cascade PR (this file + handoff + INDEX + wrapper pin bump).

Full context:
- `docs/handoffs/SESSION_3005_ADR_0007_LAYERED_ENVELOPE_POLICY.md` — governance ratification close, 4 folds
- `docs/adr/ADR-0007-layered-envelope-policy.md` — the ratified ADR (9 sections)
- `docs/adr/ADR-0006-typed-error-envelope-contract-non-provisional.md` — refinement note added at §3

---

## S3006 primary directive — T-ENVELOPE-2-DEPRECATION migration or Option B/C/D

### Option A — T-ENVELOPE-2-DEPRECATION migration (ADR-0007 §4.3)

Migrate the 108 Family B error call-sites across 5 files to Family E via `build_user_facing_envelope`. Estimate 4-6 sessions total.

**Per-file batch order (recommended smallest-to-largest for early-signal-on-approach):**
1. `core/views_odds_sports.py` — 3 call-sites (~30 min; smallest, good for pattern establishment)
2. `core/views_revenue_analytics.py` — 8 call-sites (~1 hr)
3. `core/auth_middleware.py` — 10 call-sites (~1 hr; middleware — extra scrutiny for placement invariants)
4. `core/views_auto_distribution.py` — 25 call-sites (~2-3 hr, may span 2 sessions)
5. `core/views_platform_integrations.py` — 62 call-sites (~3-4 hr, likely 2 sessions)

**Sub-task:** author lint / CI-grep gate per ADR-0007 §4.2 (~30-60 min).

**Per-call-site pattern (ADR-0007 §4.3):**
`APIResponseEnvelope.error(message, error_code, status_code=X)` → `JsonResponse(build_user_facing_envelope(reason_code=Y), status=X)` where `Y` from `DRF_EXCEPTION_REASON_MAP` values.

**First-file scope (S3006):** ship files #1 + #2 (`views_odds_sports.py` + `views_revenue_analytics.py`) + lint gate = ~11 call-sites migrated + regression prevention in place. Chris D-verdict-question: which reason_code mapping for edge cases (e.g. `views_odds_sports.py:73` validation errors → `validation_error` or `invalid_input`?).

### Option B — T-ENVELOPE-6 Telemetry hookup (logs-only interim)

`componentDidCatch` at `frontend/src/components/ErrorBoundary.tsx` is annotated as T-ENVELOPE-6 hook-point. Handler at `queryClientErrorHandler.ts` could emit structured logs. **30-60 min estimate.**

### Option C — Different arc entirely

- v2 fold ledger drain (10+ items still open from S2991-S3004 + Fold C from S3004 `/vip/expired` landing page)
- Fresh research arc (2100 RAG / 2300 Mobile / 2600 PA — remaining from queue)
- Chris's own priority

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3005 handoff.
4. Read ADR-0007 §3–§4 (layered envelope policy) if T-ENVELOPE-2-DEPRECATION work chosen.
5. Optional pre-response state probes:
   - `git log --oneline -8` — should show docs cascade → `957fee61f` (PR #3683 ADR-0007) → `f97501c3a` (S3004 close cascade) → `85fffdfc1` (PR #3681 §3.5 UX widening) → `b9595c597` (S3003 close cascade) → `3bd3df386` (PR #3679 T-VIP-1).
   - `grep -c "APIResponseEnvelope" core/**/*.py` — sanity check for T-ENVELOPE-2-DEPRECATION scope (should still be 108+ pending migration).

**Joint recommendation at close:** Preferred order for S3006 is A.file#1+A.file#2 (T-ENVELOPE-2-DEPRECATION smallest files + lint gate) > A.file#3 (auth_middleware — needs extra middleware-invariant care) > B (T-ENVELOPE-6 telemetry) > C. Reason: T-ENVELOPE-2-DEPRECATION is the ADR-0007-obligated follow-through; shipping files #1+#2 establishes the migration pattern + lint gate prevents regression while the larger files remain pending. **Route to Rigby first before presenting to Chris.**

---

## S3006 carry-forward seeds

### New carry-forward from S3005

- **Fold A `informational` (1st trigger)** — PLAYBOOK-7.7.1 abort-early clause firing at pre-execution probe. Watch for 2nd trigger before proposing Playbook amendment codifying "pre-execution HEAD-verification probe REQUIRED for any T-slot spec authored more than N sessions ago".
- **Fold B `informational` (1st trigger)** — ADR-baseline post-ratification drift discovery (ADR-0005 §2 line 25 "EXCEPTION_HANDLER absent" was stale + line 316 "14 emission sites" was off-by-8x). Watch for 2nd.
- **Fold C `informational` (1st trigger)** — `refines:` frontmatter field as new governance framing between "supersedes" and "in-place amend" (ADR-0007 introduced this). Watch for 2nd; if recurs, propose formal `refines:` field addition to ADR-0001 §3.3.
- **Fold D `future_trigger`** — lint / CI-grep gate authoring obligation under T-ENVELOPE-2-DEPRECATION. Named at ADR-0007 §4.2/§4.3; must not slip during T-slot execution.
- **T-ENVELOPE-2-DEPRECATION** — 108 call-sites across 5 files, 4-6 sessions estimated (see Option A above for batch order).
- **Ratification twin-mirror deferred** — ADR-0007 workspace ratification record not minted this session (session_lifecycle --allow-no-mirror). Post-close Rigby dispatch to `deliverable_tool.create` in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` for provenance completeness.

### Carry-forward from S3004 (STILL OPEN)

- **Fold A `2nd trigger`** — Fold-Drain-Same-Surface pattern. Watch for 3rd.
- **Fold B `informational` (1st trigger)** — shared-const derived-union frontend pattern (`AUTH_FAILURE_KIND`). Watch for 2nd.
- **Fold C `same_pr_mitigatable_deferred_to_next_arc`** — dedicated `/vip/expired` landing page.
- **Fold D `informational` (1st trigger)** — Rigby repo_tool line-1 read-display truncation false-positive during A2 SIGN. Watch for 2nd.

### Carry-forward from S3003 (STILL OPEN)

- **Fold A `informational` (1st trigger)** — risk-gate T-slot vs T-ENVELOPE-N scoping. Watch for 2nd.
- **Fold C `informational` (1st trigger)** — Django reverse-O2O test cache-bust pattern. Watch for 2nd.

### Carry-forward from S3002 (STILL OPEN)

- **Fold A** — session-shape observation. Mid-terminal S<N>→S<N+1> continuous engineering cascade. **3rd concrete instance** now (S3001→S3002 + S3003→S3004 + S3004→S3005). Watch for 4th.
- **Fold C `informational` (T-ENVELOPE-0 dev-only)** — `componentDidCatch` fires twice in dev under StrictMode.
- **Fold D — ADR successor discipline VALIDATED PATTERN.** First bidirectional supersede link in repo (ADR-0005 ↔ ADR-0006).

### Carry-forward from S3001 (STILL OPEN)

- **Fold B `informational`** — future ADR-N misread risk. "γ ratified" implying interceptor policy is preserved by §3.3 wording.
- **Fold C `informational` (1st trigger)** — potential Playbook rule candidate: "When Chris quotes a prior-session scoping suggestion, verify the target research slot state before accepting the scope." Watch for 2nd.

### Carry-forward from S3000 (STILL OPEN)

- **Fold A `informational` (1st trigger)** — potential Playbook rule candidate: "Reproduce the failure at the thinnest interface before naming the carry-forward." Watch for 2nd.
- **Fold B `informational`** — residual APIClient-forcing shapes.

### Carry-forward from S2999 (STILL OPEN)

- **Fold B `active watch`** — metadata accretion governance. 4 detector keys currently. Trigger: 5+ keys OR 2+ independent consumers.
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
- **ADR-0007 twin-mirror deliverable** — post-close Rigby dispatch to `deliverable_tool.create` in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` for ratification-record provenance.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session. **New candidate seeds:** S3005 Fold A (pre-execution probe rule — 1st trigger) + S3005 Fold B (ADR-baseline post-ratification drift — 1st trigger) + S3005 Fold C (`refines:` frontmatter — 1st trigger). Prior candidates from S3000/S3001/S3002/S3003/S3004 all remain open.
- **ADR corpus:** ADR-0001 through **ADR-0007**. ADR-0007 refines (not supersedes) ADR-0006 §3.2. ADR-0006 §3.1/§3.3/§3.4/§3.5 remain canonical unchanged. ADR-0005 T-ENVELOPE-2 now CLOSED-as-shipped.
- **Spec→ship contract:** PLAYBOOK-7.7.1. 1× Flow B with abort-early clause exercised (spec-invalidation → route to Chris before proceeding). Clean spec→pre-execution-probe→abort→re-frame→ratify→ship.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. 1× Rigby T1-pre-merge SIGN with 8 real tool_runs across 3 turns. 5 STRENGTHEN applied. Substantive per PLAYBOOK-7.7.2.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. 1 Chris-facing decision moment framed with plain-English "do we lose anything? / is it more work later?" pair. Joint Claude+Rigby recommendation reached before Chris ratification.
- **Recycle discipline:** docs + annotation-only diff, no recycle needed. Correct per Chris's local-truth doctrine + `feedback_local_truth_no_production`.

---

## Wrapper pin note

The active PA conversation pin at S3005 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3005 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3005 is a governance ratification demonstrating the full spec→ship contract WITH abort-early clause exercised:** one directed T-slot → pre-execution HEAD probe → spec-invalidation discovered → Rigby joint diagnosis → three-part plain-English decision framing → Chris ratification → ADR authoring → Rigby T1 SIGN with 5 STRENGTHEN applied → merge → close cascade. ADR-0005 T-ENVELOPE-2 CLOSED-as-shipped; ADR-0007 layered policy ratified; T-ENVELOPE-2-DEPRECATION T-slot introduced for the next arc.
