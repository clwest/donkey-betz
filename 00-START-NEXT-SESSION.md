# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3016 CLOSED. **Fold E (Token-auth parity coverage class) + Fold G (PUBLIC_PATHS bare-prefix audit for silent-empty reads) both shipped.** Second-half of the S3015 hotfix follow-up. 2 feature PRs (Fold E `ad84a847b` + Fold G `14b4a7ad4`), 32/32 tests PASS (was 28 pre-Fold E; +4 tests + shared `token_client_for()` helper + workspace-owner strengthening), audit yielded **0 critical findings** (1 false positive + 1 partial-degradation F-2 + 1 housekeeping dupe). Substrate hardening session after 3 consecutive user-facing sessions (S3013 U1 → S3014 U2 → S3015 U3). Chris's directive was two-part; both halves closed.

**2 feature PRs shipped this session.**

**PR #3716 (`ad84a847b`) — Fold E: Token-auth parity guards for user-facing endpoints.**

- **NEW** `core/tests/helpers/token_auth.py` — `token_client_for(user)` (DRF `Token.objects.get_or_create` + Client with `Authorization: Token …`, mirroring React frontend).
- **MODIFIED** S3013/S3014/S3015 test files — one parity test each. S3014+S3015 strengthened per Rigby T1 REVISE with `initiative.target_workspace.user_id == self.user.id` (anon can't resolve user's workspace, so an anon-fallthrough regression fails hard).
- **NEW** `core/tests/test_s3016_initiatives_list_auth_parity.py` — 3 tests locking the exact PR #3714 scenario: session/token count parity, Token-auth-alone non-empty, anon still returns empty 200 (OPTIONAL_AUTH_PATHS contract).
- **Test result:** 32/32 pass in 4.125s.

**PR #3717 (`14b4a7ad4`) — Fold G: PUBLIC_PATHS bare-prefix audit for silent-empty reads.**

- **NEW** `scripts/audit_public_paths_scoped_reads_s3016.py` — candidate generator (not a classifier). Walks `get_resolver().url_patterns × PUBLIC_PATHS`, greps view source for 5 canonical scope predicates.
- **NEW** `docs/audits/PUBLIC_PATHS_BARE_PREFIX_AUDIT_S3016.md` — findings doc. F-1 (false positive, `/api/celery/breakdown/` is `@superuser_required`), F-2 (unscoped memory detail row at `/api/memory-palace/memory/<uuid>/` — primary issue = row itself is public + secondary = silent enrichment drop), housekeeping dupe `/api/celery/`.
- **Substantive:** S3015 list-endpoint-empty class does **not** repeat elsewhere for the 5 tracked predicates. Fold E hotfix + parity tests correctly scoped.

**Rigby SIGN quality this session:** 6 substantive SIGN cycles (Fold E T0/T1/close-out + Fold G T0-implicit/T1/close-out), all tool-grounded, zero hallucination triggers. **Matches S3010–S3015 pattern — 8 sessions continuous.**

**HEAD at close:** `14b4a7ad4` (Fold G merged) + this docs cascade PR (handoff + 00-START refresh + INDEX regen + wrapper pin bump).

Full context:
- `docs/handoffs/SESSION_3016_FOLD_E_G_TOKEN_AUTH_SWEEP.md` — full session close, 6 folds, forward carries.
- `core/tests/helpers/token_auth.py` — reusable Token-auth test helper.
- `core/tests/test_s3016_initiatives_list_auth_parity.py` — PR #3714 regression guard.
- `scripts/audit_public_paths_scoped_reads_s3016.py` — reusable audit script.
- `docs/audits/PUBLIC_PATHS_BARE_PREFIX_AUDIT_S3016.md` — Fold G findings + F-2 remediation candidates.

---

## S3017 primary directive candidates

**No in-flight arc.** Chris directive-required. Options ranked:

### Option A — F-2 remediation (unscoped `/api/memory-palace/memory/<uuid>/`)

The Fold G audit found the memory detail row is publicly readable — anon with a valid UUID fetches the row + triggers access_count auto-increment. **Chris ratifies shape** among:

1. **`@token_auth_required` gate** (~30 min) — simplest, matches S2789 pattern for endpoints in PUBLIC_PATHS that need auth. Removes anon reachability entirely.
2. **New `scope_queryset_agent_memory` predicate** in `core/security/object_authz.py` + scope the lookup itself (~1 session) — strongest, but requires design addition to the object_authz surface. Aligns with the existing 5-predicate pattern.
3. **`execution_data_available` payload flag** (~15 min) — secondary only, does NOT fix the unscoped memory row leak. Not recommended in isolation.

**Recommended:** Option A.1 (`@token_auth_required` gate) — fastest, matches existing pattern, removes the leak. A.2 is stronger long-term but adds a new predicate to the object_authz surface which may want its own ADR.

### Option B — Fresh engineering (per bias-engineering-over-audit rule)

Continuation of the U-series bulk-shape trajectory:
- **U4 candidate:** AgentDecisionSummary bulk-decide. `pending_decisions` currently mixes HumanAttentionItem (which U1 handles) + AgentDecisionSummary (which nothing bulk-handles). Parallels U1 shape. ~1 session.
- **U5 candidate:** Post-create auto-link cluster ↔ initiative via `initiative_signal_linker.auto_link_initiative_signals()` after cluster→initiative create. ~30 min.
- **U6 candidate:** Bulk cluster → initiative UX polish — inline per-row name editing in confirm modal. ~1 session.

### Option C — Zoom-out carry from Fold E T0 SIGN

Four concerns Rigby flagged that Fold E did NOT defend against:
1. Middleware-ordering drift — Django test-client path may not match Daphne/ASGI in prod. Design candidate: middleware-order snapshot test.
2. DRF `authentication_classes` on ViewSets that bypass `UnifiedTokenAuthenticationMiddleware`. Parallel Fold-G-shape audit for the DRF stack.
3. WebSocket auth-parity coverage class — Fold E was HTTP READ scope only. Separate arc.
4. `Bearer <token>` header format — only `Token <key>` currently covered by helper. ~30 min extension.

### Option D — Housekeeping

- Dedupe `/api/celery/` PUBLIC_PATHS entry (~10 min).
- 9th test coupling from S3013 non-blocking carry (~15 min).

### Option E — Chris's own priority (supersedes A/B/C/D)

**Joint recommendation at close:** **Option A.1** (`@token_auth_required` gate on `/api/memory-palace/memory/<uuid>/`) — closes the unscoped-row leak F-2 identified, fastest option, matches existing pattern. If Chris wants to continue the U-series bulk-shape trajectory instead, U5 (auto-link) is the fastest at ~30 min.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3016 handoff (`docs/handoffs/SESSION_3016_FOLD_E_G_TOKEN_AUTH_SWEEP.md`).
4. Optional state probes:
   - `git log --oneline -6` — should show docs cascade → `14b4a7ad4` (PR #3717 Fold G) → `ad84a847b` (PR #3716 Fold E) → `d9ef9aa03` (S3015 close cascade).
   - `python manage.py test core.tests.test_s3013_bulk_attention_decide_mutation core.tests.test_s3014_create_initiative_from_cluster core.tests.test_s3015_bulk_create_initiatives_from_clusters core.tests.test_s3016_initiatives_list_auth_parity --keepdb` — should return 32/32 OK in ~4s.
   - `python manage.py shell < scripts/audit_public_paths_scoped_reads_s3016.py` — should re-produce 4 raw / 2 unique candidates.

---

## S3017 carry-forward seeds

### New from S3016

- **F-2 remediation candidate** — `@token_auth_required` gate OR new `scope_queryset_agent_memory` predicate on `/api/memory-palace/memory/<uuid>/`. See Option A above.
- **Dupe `/api/celery/` PUBLIC_PATHS entry** — housekeeping.
- **Fold D `1st trigger`** — doc-only PR + `make recycle-all` policy. Watch for 2nd trigger (does PLAYBOOK-7.4.4 need a "doc-only PR = recycle optional" clause?).
- **Zoom-out carries (from Fold E T0):**
  - Middleware-ordering snapshot test candidate.
  - DRF ViewSet auth-class parallel audit (2nd-trigger watch).
  - WebSocket auth-parity coverage class (likely S3018+).
  - `Bearer <token>` helper extension (~30 min).
- **Fold F `informational`** — inline-scoping classifier expansion for future Fold-G re-run if a silent-empty regression surfaces on an endpoint not using the tracked predicates.

### Carried from S3015 (STATUS UPDATED)

- **S3015 Fold E `1st trigger`** — **CLOSED by S3016 PR #3716**.
- **S3015 Fold F `1st trigger`** — carry-forward retained (empty-state diagnostic tree still open).
- **S3015 Fold G `informational`** — **CLOSED by S3016 PR #3717**.
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
- **Fold B `1st trigger`** — S2785 auth-regression mutation-path blind spot (partially addressed by S3016 Fold E; not fully closed).
- **Fold D `future_trigger`** — `BulkAttentionDecideView` uses Family B envelope shape.
- **Fold E `informational`** — Bulk endpoint decision enum inconsistency.

### Carried from S3012 (STATUS PRESERVED)

- **Task #7 — Delete dead A/B testing handlers** per HALF_BUILT_FEATURES_AUDIT.
- **Task #8 — DRF-decorator refactor** for 15 auth guards in views_learning_loop.py.
- **Fold C `informational`** — `@superuser_required` decorator Family B → Family E migration candidate.

### Carried from S3011 (STATUS PRESERVED)

- **Fold B `5th trigger imminent → assess post-S3016`** — PLAYBOOK-7.4.5 amendment (`make restart` for Daphne). All recent sessions used `make recycle-all`. **Increment: S3016 also used `make recycle-all` twice → trigger imminent, not yet fired.**
- **Fold A `1st trigger` (S3009 LLM-hallucination ledger)** — ZERO hallucinations at S3010-S3016 (**8 sessions continuous**).
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
- **Spec→ship contract:** PLAYBOOK-7.7.1. **2× Flow B spec→ship this session (Fold E + Fold G).**
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **6× substantive Rigby SIGN cycles. Zero rubber-stamp signals. 8 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing this session: initial anchor-correction ("I anchored on 00-START menu instead of your close summary") + 4× "proceed" ratifications + 1× "merge and recycle" directive.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` twice — post-Fold-E merge and post-Fold-G merge (constitutional consistency even on doc-only PR).
- **Verify-before-build (Cycle 1A):** implicit — the `token_client_for` helper was placed in `core/tests/helpers/` after confirming no prior helper pattern existed.
- **Fold classification (PLAYBOOK-6.10.8):** 3× `same_pr_actionable → resolved` (Folds A/B/C mitigated in same PR). 1× new `1st trigger` (Fold D — doc-only PR + recycle-all policy). 2× `informational` (Folds E/F zoom-out).

---

## Wrapper pin note

The active PA conversation pin at S3016 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3016 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3016 shipped a clean 2-PR arc following the S3016 00-START directive (correcting to Fold E + G per Chris's earlier close summary, not the 00-START Option A menu which had drifted). Substrate hardening after 3 consecutive user-facing sessions. S3017 opens with no in-flight arc.**
