# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3018 CLOSED. **S3017 Fold A `1st trigger` shipped** — route-decorator invariant test locking the gate status of every URL pattern under a `PUBLIC_PATHS` bare-prefix. Snapshot-lock catches new drift at PR review time. 40/40 tests pass (38 prior + 2 new). Chris ratified Option A at S3017 close; Rigby T0 signed the design shape (AGREE-with-shape + 3 refinements); Rigby T1 REVISE-1 (split snapshot into gated + ungated files) folded same-PR after Chris "proceed." Baseline: 733 routes across 255 prefixes (29 token-required, 98 DRF, 606 gate:none). Rigby SIGN quality: 2 substantive cycles + 1 truncation-recovery re-issue, all tool-grounded, zero hallucination triggers (**10 sessions continuous**).

**1 feature PR shipped this session.**

**PR #3721 (`f81d84951`) — `test(s3018): route-decorator invariant test for PUBLIC_PATHS bare-prefixes (Fold A)`.**

- **NEW** `tests/security/public_paths_gate_snapshot_builder.py` — enumeration + gate detection (marker + `__wrapped__` unwrap traversal + DRF `permission_classes` fallback) + split-file read/write helpers.
- **NEW** `tests/security/public_paths_gate_snapshot_gated.json` (1027 lines, 127 rows) — high-signal diff surface.
- **NEW** `tests/security/public_paths_gate_snapshot_ungated.json` (4859 lines, 606 rows) — noise bucket.
- **NEW** `tests/security/test_public_paths_gate_invariant_s3018.py` — snapshot-lock + special new-ungated-route fail-path + S3017 sanity check.
- **NEW** `core/management/commands/refresh_public_paths_gate_snapshot.py` — regen command with `--dry-run`.
- **MODIFIED** `core/auth_middleware.py` — `_auth_gate = 'token_required'` marker on `token_auth_required`.
- **MODIFIED** `core/security/decorators.py` — `_auth_gate = 'superuser_required'` marker on `superuser_required`.
- **Test result:** 40/40 pass in 4.454s. Negative-path sanity confirms both failure branches fire correctly.

**HEAD at close:** docs cascade → `f81d84951` (PR #3721).

Full context:
- `docs/handoffs/SESSION_3018_PUBLIC_PATHS_GATE_INVARIANT.md` — full session close, 4 folds, forward carries.

---

## S3019 primary directive candidates

**No in-flight arc.** Chris directive-required. Options ranked:

### Option A — A.2 cross-user isolation (S3017 Fold C `future arc`)

New `scope_queryset_agent_memory` predicate on `core/security/object_authz.py` + row-scope the memory detail lookup. Currently any authenticated user with a valid UUID can still read/delete any memory row (only anon is closed by S3017). `AgentMemory` has no direct user FK today; scoping via `agent → user_assignments` M2M is possible but non-obvious.

**Recommend ADR** before implementation — model design choice + object_authz surface expansion warrants a written contract.

### Option B — S3018 Fold extensions (natural follow-on)

- **Fold B (S3018 REVISE-2):** test-time advisory telemetry for decorator-chain-break. Marker-defeated-by-outer-non-wraps risk. ~1 session.
- **Method-decorator detection extension:** catch `@method_decorator(superuser_required)` on CBV methods (currently `gate: none`). ~1 session.
- **Inline `request.user.is_authenticated` detection:** grep-based advisory extension. ~30 min.

### Option C — Fresh engineering (per bias-engineering-over-audit rule)

- **U4 candidate:** AgentDecisionSummary bulk-decide. Parallels U1 shape. ~1 session.
- **U5 candidate:** Post-create auto-link cluster ↔ initiative via `initiative_signal_linker.auto_link_initiative_signals()` after cluster→initiative create. ~30 min.
- **U6 candidate:** Bulk cluster → initiative UX polish — inline per-row name editing in confirm modal. ~1 session.

### Option D — S3016 zoom-out carries (still open)

- Middleware-order snapshot test candidate.
- DRF ViewSet auth-class parallel audit (2nd-trigger watch for Fold-G-shape).
- WebSocket auth-parity coverage class.
- `Bearer <token>` helper extension (~30 min).

### Option E — Housekeeping

- Dedupe `/api/celery/` PUBLIC_PATHS entry (~10 min).
- 9th test coupling from S3013 non-blocking carry (~15 min).

### Option F — Chris's own priority (supersedes A/B/C/D/E)

**Joint recommendation at close:** if you want to keep pressing on the auth-hardening trajectory, **Option A** (A.2 cross-user isolation via `scope_queryset_agent_memory` predicate) is the natural follow-on to close the "authenticated cross-user leak" that S3017's decorator gate doesn't cover. Recommend a small ADR first since it introduces a new predicate surface.

If bias-engineering rule wins, **U5** is fastest (~30 min).

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3018 handoff (`docs/handoffs/SESSION_3018_PUBLIC_PATHS_GATE_INVARIANT.md`).
4. Optional state probes:
   - `git log --oneline -6` — should show docs cascade → `f81d84951` (PR #3721) → docs cascade `092a28af0` → `09f6e91e7` (PR #3719 S3017 fix).
   - `python manage.py test tests.security.test_public_paths_gate_invariant_s3018 core.tests.test_s3013_bulk_attention_decide_mutation core.tests.test_s3014_create_initiative_from_cluster core.tests.test_s3015_bulk_create_initiatives_from_clusters core.tests.test_s3016_initiatives_list_auth_parity core.tests.test_s3017_memory_detail_auth_gate --keepdb` — should return 40/40 OK in ~4.5s.
   - `python manage.py refresh_public_paths_gate_snapshot --dry-run` — should return `733 in-scope routes across 255 prefixes` with 29/98/606 gate breakdown.

---

## S3019 carry-forward seeds

### New from S3018

- **Fold A `same_pr_actionable → resolved`** — snapshot split into gated + ungated files.
- **Fold B `future arc`** — test-time advisory telemetry for decorator-chain-break.
- **Fold C `informational`** — optional `@public_intentional` marker to shrink `gate: none` bucket.
- **Fold D `1st trigger`** — Rigby response-truncation trigger (first turn only 1 of intended tool_runs surfaced; second turn succeeded).
- **Method-decorator detection extension** — catch `@method_decorator(superuser_required)` on CBV methods.
- **Inline `.is_authenticated` detection extension** — grep-based advisory for views that gate inline.

### Carried from S3017 (STATUS UPDATED)

- **S3017 Fold A** — **CLOSED by S3018 PR #3721**.
- **S3017 Fold C (A.2 cross-user isolation)** — still open, future arc.
- **S3017 Fold D (Rigby Tool Gap Ledger — web_fetch_tool DELETE + http_smoke_test middleware-bypass)** — still open.

### Carried from S3016 (STATUS PRESERVED)

- **Dupe `/api/celery/` PUBLIC_PATHS entry** — housekeeping.
- **Fold D `1st trigger`** — doc-only PR + `make recycle-all` policy. Watch for 2nd trigger.
- **Zoom-out carries (from Fold E T0):**
  - Middleware-ordering snapshot test candidate.
  - DRF ViewSet auth-class parallel audit (2nd-trigger watch).
  - WebSocket auth-parity coverage class (likely S3020+).
  - `Bearer <token>` helper extension (~30 min).
- **Fold F `informational`** — inline-scoping classifier expansion for future Fold-G re-run if a silent-empty regression surfaces on an endpoint not using the tracked predicates.

### Carried from S3015 (STATUS PRESERVED)

- **S3015 Fold F `1st trigger`** — carry-forward retained (empty-state diagnostic tree still open).
- **U4 candidate:** AgentDecisionSummary bulk-decide.
- **U5 candidate:** post-create auto-link via `initiative_signal_linker`.
- **U6 candidate:** per-row name editing in bulk cluster confirm modal.
- **Fold A `1st trigger` (bulk-endpoint scope-limit-cap standard)** — carry-forward.
- **Fold B `informational`** — carry-forward.
- **Fold C `informational`** — carry-forward.
- **Fold D `3rd trigger` (Cycle 1A verify-before-build)** — carry-forward.
- **UI candidate:** progress bar during bulk create.

### Carried from S3014 (STATUS PRESERVED)

- **Rigby non-blocking A2 suggestion (S3013):** 9th test coupling.
- **Batch Defer for Governance (S3013):** needs new bulk endpoint.
- **Fold A `1st trigger` (S3014)** — "Diagnostic on create" invariant codification.
- **Fold B `informational` (S3014)** — `create_deliverable` factory `trigger_source` bypass documentation.
- **Fold C `informational` (S3014)** — Session 843 `parent_object_type/id` audit opportunity.
- **Fold D `2nd trigger` (rolled)** — Rigby web_fetch_tool auth clarification.

### Carried from S3013 (STATUS PRESERVED)

- **Fold A `3rd trigger`** — Cycle 1A verify-before-build.
- **Fold B `1st trigger`** — S2785 auth-regression mutation-path blind spot (partially addressed by S3016 Fold E + S3017 F-2/F-3 + S3018 invariant; not fully closed).
- **Fold D `future_trigger`** — `BulkAttentionDecideView` uses Family B envelope shape.
- **Fold E `informational`** — Bulk endpoint decision enum inconsistency.

### Carried from S3012 (STATUS PRESERVED)

- **Task #7 — Delete dead A/B testing handlers** per HALF_BUILT_FEATURES_AUDIT.
- **Task #8 — DRF-decorator refactor** for 15 auth guards in views_learning_loop.py.
- **Fold C `informational`** — `@superuser_required` decorator Family B → Family E migration candidate.

### Carried from S3011 (STATUS PRESERVED)

- **Fold B `5th trigger imminent → assess post-S3018`** — PLAYBOOK-7.4.5 amendment (`make restart` for Daphne). All recent sessions used `make recycle-all`. **Increment: S3018 used `make recycle-all` once → trigger imminent, not yet fired.**
- **Fold A `1st trigger` (S3009 LLM-hallucination ledger)** — ZERO hallucinations at S3010-S3018 (**10 sessions continuous**).
- **Fold C `1st trigger` (S3009 Rigby shell-exec ledger)** — still open.
- **Fold B `1st trigger` from S3008** (`repo_tool.search no total_matches`) — bundle candidate for repo_tool capability expansion arc.

### Carried from earlier sessions (STILL OPEN — unchanged this session)

- **Sports odds leak drain arc** — 32 DRF Response `str(e)` sites in `views_odds_sports.py` grandfathered.
- **future_str_e_variants** — `repr(e)` / `force_str(e)` / `f"{e!r}"` detection extension for B2 lint.
- **Fold C `future_trigger` from S3006** — DRF-decorator refactor for inline auth checks (superseded by Task #8).
- **Fold A/B/C `informational` (1st trigger) from S3005** — PLAYBOOK-7.7.1 abort-early clause / ADR-baseline drift / `refines:` frontmatter field.
- **Fold A `2nd trigger` from S3004** — Fold-Drain-Same-Surface pattern.
- **Fold B `informational` (1st trigger) from S3004** — shared-const derived-union frontend pattern.
- **Fold C `same_pr_mitigatable_deferred_to_next_arc` from S3004** — dedicated `/vip/expired` landing page.
- **Fold D `informational` (1st trigger) from S3004** — Rigby repo_tool line-1 read-display truncation false-positive.
- **Fold A `informational` (1st trigger) from S3003** — risk-gate T-slot vs T-ENVELOPE-N scoping.
- **Fold C `informational` (1st trigger) from S3003** — Django reverse-O2O test cache-bust pattern.
- **Fold C `informational` (T-ENVELOPE-0 dev-only) from S3002** — `componentDidCatch` fires twice in dev under StrictMode.
- **Fold D from S3002** — ADR successor discipline VALIDATED PATTERN.
- **Fold B `informational` from S3001** — future ADR-N misread risk.
- **Fold C `informational` (1st trigger) from S3001** — verify target research slot state before accepting scope.
- **Fold A `informational` (1st trigger) from S3000** — reproduce failure at thinnest interface.
- **Fold B `informational` from S3000** — residual APIClient-forcing shapes.
- **Fold B `active watch` from S2999** — metadata accretion governance.
- **Fold C from S2999** — Rigby Tool Gap Ledger, file:line-only scope of consumer verifier.
- **Fold A/B/C `future_trigger` from S2998** — force=true × factory dedupe / DeliverableEvent breadcrumb / Rigby Tool Gap Ledger.
- **Fold B `future_trigger` from S2997** — dedupe strictness on stale-ref ACs.
- **Fold F from S2997** — Rigby Tool Gap Ledger (`orm_inspect_tool` JSON-path lookups).
- **Fold C `future_trigger` from S2996** — staleness toast reinforcement.
- **Fold E from S2996** — Rigby Tool Gap Ledger (no in-UI Recheck action).
- **Fold C/D `future_trigger` from S2995** — staleness metadata + periodic staleness beat.
- **Fold E from S2995** — Rigby Tool Gap Ledger (metadata accretion governance).
- **Fold F `future_trigger` from S2995** — WorkspacePageNew param preservation.
- **Fold B/C/D `future_trigger` from S2994** — inline-helper density / Deliverables-tab type badge / Rigby Tool Gap Ledger.
- **Fold B/C ledger candidates from S2993** — dry-run preview for send-to-rigby / executable-prompt tightening.
- **Signal-tweak follow-up for `finding_type` classifier from S2992** (2 acceptable-misses).
- **Data-migration-vs-management-command pattern from S2992** (3rd-trigger check).
- **Dry-run counts pattern from S2991** (3rd-trigger check).
- **Contract-lock-in guardrail from S2991** — updated set.
- **F-D3-tracker-scope wire-up / F-D2-broad LLM-bypass audit / Chris 1805 cap-drift reconciliation / Canonical Briefing v2 scope toggle / _TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT substrate fix / Send-to-Rigby follow-ups from S2988** (S2989-S2990 batch).
- **Chris browser visual checks on S2984 arcs section + S2985 Canonical Briefing tab strip.**
- **Rigby `claude_code_tool` safeguards.** Log to Rigby Tool Gap Ledger.
- **Systemic auth-XHR treatment (S2984 Fold).**
- **Live-dispatch smoke on S2982 stage-doc guardrails.**
- **Exercise PLAYBOOK-7.7.4 against a sibling repo.**
- **Browser UX smoke on S2980 Theme Signals UX upgrade.**
- **Phase B Theme Signals — "Why now" LLM summarizer.**
- **Phase B Theme Signals — who-benefits/who-loses.**
- **Theme Signals sub-tab persistence via localStorage.**
- **Rigby Tool Gap Ledger — Fold D from S2982.** DB uniqueness constraint on `AgentExecution.celery_task_id`.
- **Fold B `future_trigger` from v0.8.0** — fold-authoring evidence-admission helper.
- **Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for v0.9.0 and v0.10.0.
- **Live browser smoke on S3004 VIP-expired modal.**
- **ADR-0007 twin-mirror deliverable.**
- **Batch 3 400→404 image/video not_found verification** (from S3009 forward-carry).
- **`superuser_required` decorator Family B → Family E migration candidate** (Fold C from S3012).
- **`agents/views_monitoring.py` 7 sites** using `core.api_responses.api_error`.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0007. No open ADR successor arcs.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship this session (invariant test + split refactor).**
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles + 1 truncation-recovery re-issue. Zero rubber-stamp signals. 10 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing this session: initial ratification of Option A + 1× scope-expansion ratification (split-snapshot fold).
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once — post-PR-3721 merge.
- **Verify-before-build (Cycle 1A):** implicit — pre-check confirmed `token_auth_required` / `superuser_required` were the only two auth decorators in the codebase before adding markers; DRF permission classes were the only other detectable gate mechanism.
- **Fold classification (PLAYBOOK-6.10.8):** 1× `same_pr_actionable → resolved` (Fold A — split snapshot). 1× `future arc` (Fold B — decorator-chain-break advisory). 1× `informational` (Fold C — `@public_intentional` marker). 1× `1st trigger` (Fold D — Rigby response truncation).

---

## Wrapper pin note

The active PA conversation pin at S3018 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3018 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3018 shipped a clean 1-PR arc following S3017's ratified Fold A directive. Snapshot-lock invariant now catches the class of leak that produced F-2 and F-3. S3019 opens with no in-flight arc.**
