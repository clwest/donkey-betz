# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3017 CLOSED. **F-2 (Fold G finding from S3016) + F-3 (Rigby T1 zoom-out) both closed in one PR.** Single feature PR #3719 (`09f6e91e7`) — `@token_auth_required` gate on `/api/memory-palace/memory/<uuid>/` **and** its two sibling routes (`connections/`, `delete/`). 38/38 tests pass (32 prior + 6 new S3017). Chris ratified Option A.1 at S3016 close; Rigby T1 SIGN surfaced the sibling routes; Chris ratified same-PR fold. Live smoke: GET-detail / GET-connections / DELETE all return 401 + `not_authenticated` envelope against real memory UUIDs. Rigby SIGN quality: 2 substantive cycles, tool-grounded, zero hallucination triggers (**9 sessions continuous**).

**1 feature PR shipped this session.**

**PR #3719 (`09f6e91e7`) — `fix(s3017): @token_auth_required on memory-palace detail + siblings (F-2 + F-3)`.**

- **MODIFIED** `core/views_memory_palace.py` — `@token_auth_required` on `get_memory_detail` (F-2), `get_memory_connections` (F-3 read leak), `delete_memory` (F-3 anon-DELETE mutation leak — strictly worse than F-2).
- **NEW** `core/tests/test_s3017_memory_detail_auth_gate.py` — 6 tests: anon-401 + no-access_count-bump + session-200 + token-200 on detail; anon-401 on connections; anon-401 + row-survives on DELETE.
- **MODIFIED** `docs/audits/PUBLIC_PATHS_BARE_PREFIX_AUDIT_S3016.md` — F-2 CLOSED block + F-3 reference.
- **Test result:** 38/38 pass in 4.647s.

**HEAD at close:** docs cascade → `09f6e91e7` (PR #3719).

Full context:
- `docs/handoffs/SESSION_3017_MEMORY_PALACE_AUTH_GATE.md` — full session close, 4 folds, forward carries.

---

## S3018 primary directive candidates

**No in-flight arc.** Chris directive-required. Options ranked:

### Option A — Route-decorator invariant test (S3017 Fold A `1st trigger`)

Rigby's T1 zoom-out 5a: per-view gating under a public prefix is *correct but brittle*. Every sensitive view under a bare-prefix must remember to add `@token_auth_required`. One missed endpoint = another F-2-shape class bug.

**Recommended shape:** enumerate URL patterns whose prefix matches a `PUBLIC_PATHS` bare-prefix, inspect each view for a gating decorator (`@token_auth_required` / `@superuser_required` / DRF `authentication_classes` / equivalent), emit a test that FAILS if any new such view lands ungated. ~1 session.

### Option B — A.2 cross-user isolation (S3017 Fold C `future arc`)

New `scope_queryset_agent_memory` predicate on `core/security/object_authz.py` + row-scope the memory detail lookup. Currently any authenticated user with a valid UUID can still read/delete any memory row (only anon is closed). Requires model design — `AgentMemory` has no direct user FK today; scoping via `agent → user_assignments` M2M is possible but non-obvious. Recommend ADR. ~1-2 sessions.

### Option C — Fresh engineering (per bias-engineering-over-audit rule)

Continuation of the U-series bulk-shape trajectory:
- **U4 candidate:** AgentDecisionSummary bulk-decide. `pending_decisions` currently mixes HumanAttentionItem (which U1 handles) + AgentDecisionSummary (which nothing bulk-handles). Parallels U1 shape. ~1 session.
- **U5 candidate:** Post-create auto-link cluster ↔ initiative via `initiative_signal_linker.auto_link_initiative_signals()` after cluster→initiative create. ~30 min.
- **U6 candidate:** Bulk cluster → initiative UX polish — inline per-row name editing in confirm modal. ~1 session.

### Option D — S3016 zoom-out carries (S3017 didn't touch)

- Middleware-order snapshot test candidate.
- DRF ViewSet auth-class parallel audit (2nd-trigger watch for Fold-G-shape).
- WebSocket auth-parity coverage class.
- `Bearer <token>` helper extension (~30 min).

### Option E — Housekeeping

- Dedupe `/api/celery/` PUBLIC_PATHS entry (~10 min).
- 9th test coupling from S3013 non-blocking carry (~15 min).

### Option F — Chris's own priority (supersedes A/B/C/D/E)

**Joint recommendation at close:** **Option A** (route-decorator invariant test). Directly generalizes the S3017 F-2 + F-3 sweep — turns the ad-hoc "did I remember to gate this?" check into a compile-time / test-time invariant. Same-shape audit-then-lock trajectory as Fold E (test-based lock) + Fold G (audit script). Prevents the class of failure that produced both F-2 and F-3.

If Chris prefers engineering-forward per bias rule, U5 is fastest (~30 min).

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3017 handoff (`docs/handoffs/SESSION_3017_MEMORY_PALACE_AUTH_GATE.md`).
4. Optional state probes:
   - `git log --oneline -6` — should show docs cascade → `09f6e91e7` (PR #3719).
   - `python manage.py test core.tests.test_s3013_bulk_attention_decide_mutation core.tests.test_s3014_create_initiative_from_cluster core.tests.test_s3015_bulk_create_initiatives_from_clusters core.tests.test_s3016_initiatives_list_auth_parity core.tests.test_s3017_memory_detail_auth_gate --keepdb` — should return 38/38 OK in ~4.5s.

---

## S3018 carry-forward seeds

### New from S3017

- **Fold A `1st trigger`** — route-decorator invariant test (see Option A above).
- **Fold B `same_pr_actionable → resolved`** — F-3 sibling routes folded in same PR.
- **Fold C `future arc`** — A.2 cross-user isolation via `scope_queryset_agent_memory` predicate.
- **Fold D `1st trigger` × 2 (Rigby Tool Gap Ledger)** — `web_fetch_tool` DELETE support gap + `http_smoke_test` middleware-bypass gap. Both logged.

### Carried from S3016

- **S3016 Fold G F-2 remediation** — **CLOSED by S3017 PR #3719**.
- **Dupe `/api/celery/` PUBLIC_PATHS entry** — housekeeping.
- **Fold D `1st trigger`** — doc-only PR + `make recycle-all` policy. Watch for 2nd trigger.
- **Zoom-out carries (from Fold E T0):**
  - Middleware-ordering snapshot test candidate.
  - DRF ViewSet auth-class parallel audit (2nd-trigger watch).
  - WebSocket auth-parity coverage class (likely S3019+).
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
- **Fold B `1st trigger`** — S2785 auth-regression mutation-path blind spot (partially addressed by S3016 Fold E + S3017 F-2/F-3; not fully closed).
- **Fold D `future_trigger`** — `BulkAttentionDecideView` uses Family B envelope shape.
- **Fold E `informational`** — Bulk endpoint decision enum inconsistency.

### Carried from S3012 (STATUS PRESERVED)

- **Task #7 — Delete dead A/B testing handlers** per HALF_BUILT_FEATURES_AUDIT.
- **Task #8 — DRF-decorator refactor** for 15 auth guards in views_learning_loop.py.
- **Fold C `informational`** — `@superuser_required` decorator Family B → Family E migration candidate.

### Carried from S3011 (STATUS PRESERVED)

- **Fold B `5th trigger imminent → assess post-S3017`** — PLAYBOOK-7.4.5 amendment (`make restart` for Daphne). All recent sessions used `make recycle-all`. **Increment: S3017 also used `make recycle-all` once → trigger imminent, not yet fired.**
- **Fold A `1st trigger` (S3009 LLM-hallucination ledger)** — ZERO hallucinations at S3010-S3017 (**9 sessions continuous**).
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
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship this session (F-2 + F-3 fold).**
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles + 1 Claude-local close-out. Zero rubber-stamp signals. 9 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing this session: initial ratification of Option A.1 shape + 1× scope-expansion ratification (F-3 sibling fold) + 1× "Proceed" open.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once — post-PR-3719 merge.
- **Verify-before-build (Cycle 1A):** implicit — the `@token_auth_required` decorator was verified already present in `core/auth_middleware.py` before applying; existing S2789 pattern reused.
- **Fold classification (PLAYBOOK-6.10.8):** 1× `same_pr_actionable → resolved` (Fold B — F-3 sibling fold). 3× `1st trigger` (Fold A route-decorator invariant, Fold D tool-gap × 2). 1× `future arc` (Fold C — A.2 predicate).

---

## Wrapper pin note

The active PA conversation pin at S3017 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3017 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3017 shipped a clean 1-PR arc following S3016's ratified 00-START Option A.1. Same-PR fold caught F-3 (anon-DELETE-any-row) via Rigby T1 zoom-out. S3018 opens with no in-flight arc.**
