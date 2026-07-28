# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3019 CLOSED. **ADR-0008 A.2 cross-user isolation shipped** — sixth predicate on `object_authz.py` closes the authenticated cross-user gap that S3017's decorator gate left open. 52/52 tests pass (40 prior + 12 new). Chris ratified ADR-0008 at S3019 open; Rigby T0 signed the ADR shape (Layer 1 AGREE + Layer 2 REVISE-3-changes); Rigby T1 signed the implementation (Layer 1 AGREE + Layer 2 AGREE). Live smoke post-recycle confirmed anon → 401 (S3017 decorator) + Chris → 200 (superuser null-assignment carve-out). Rigby SIGN quality: 2 substantive cycles, all tool-grounded, zero rubber-stamp (**11 sessions continuous**).

**1 feature PR shipped this session.**

**PR #3723 (`d516743c5`) — `feat(s3019): AgentMemory scope predicate (ADR-0008 A.2 cross-user isolation)`.**

- **NEW** `docs/adr/ADR-0008-agent-memory-scope-predicate.md` — accepted 2026-07-28. Sixth predicate on object_authz surface.
- **MODIFIED** `core/security/object_authz.py` — `can_read_agent_memory` + `scope_queryset_agent_memory` (M2M traversal + null-assignment superuser carve-out).
- **MODIFIED** `core/views_memory_palace.py` — 3 views wired to predicate (detail / connections / delete).
- **NEW** `core/tests/helpers/agent_assignment.py` — `assign_agent_to_user()` factory (ADR-0008 §3.4).
- **NEW** `core/tests/test_s3019_agent_memory_scope_predicate.py` — 12 tests (5 predicate + 7 view-wiring).
- **MODIFIED** `core/tests/test_s3017_memory_detail_auth_gate.py` — assign agent to test user (S3017 predated A.2 scoping).
- **Test result:** 52/52 pass in 7.177s.
- **Live smoke:** anon → 401 + superuser → 200 confirmed on real memory UUID.

**HEAD at close:** docs cascade → `d516743c5` (PR #3723).

Full context:
- `docs/handoffs/SESSION_3019_AGENT_MEMORY_SCOPE_PREDICATE.md` — full session close, 4 folds, forward carries.
- `docs/adr/ADR-0008-agent-memory-scope-predicate.md` — the accepted ADR.

---

## S3020 primary directive candidates

**No in-flight arc.** Chris directive-required. Options ranked:

### Option A — A.2 pattern generalization (S3019 Fold-forward candidate)

The four-session memory-palace arc (S3016 F-2 audit → S3017 A.1 decorator → S3018 invariant → S3019 A.2 predicate) closes ONE class of vulnerability. The same shape likely applies elsewhere:

- **AgentExecution detail endpoints** — already have `scope_queryset_agent_execution` but may have unscoped `.get()` sites.
- **MemoryConnection endpoints** — sibling substrate to AgentMemory; probably needs the same scope predicate.
- **MemoryPalaceRoom endpoints** — same shape.
- **Signal cluster / memory cluster endpoints** — check for direct `.get()` on ID.

**Recommended:** small audit script (parallel to `scripts/audit_public_paths_scoped_reads_s3016.py`) that greps `views_*.py` for `Model.objects...get(id=` patterns without a preceding `scope_queryset_*` call. ~1 session for audit + findings doc.

### Option B — Fresh engineering (per bias-engineering-over-audit rule)

- **U4 candidate:** AgentDecisionSummary bulk-decide. Parallels U1 shape. ~1 session.
- **U5 candidate:** Post-create auto-link cluster ↔ initiative via `initiative_signal_linker.auto_link_initiative_signals()` after cluster→initiative create. ~30 min.
- **U6 candidate:** Bulk cluster → initiative UX polish — inline per-row name editing in confirm modal. ~1 session.

### Option C — S3018 Fold extensions

- **Fold B (S3018 REVISE-2):** test-time advisory telemetry for decorator-chain-break. ~1 session.
- **Method-decorator detection extension:** catch `@method_decorator(superuser_required)` on CBV methods (currently `gate: none`). ~1 session.

### Option D — S3016 zoom-out carries (still open)

- Middleware-order snapshot test candidate.
- DRF ViewSet auth-class parallel audit (2nd-trigger watch for Fold-G-shape).
- WebSocket auth-parity coverage class.
- `Bearer <token>` helper extension (~30 min).

### Option E — Housekeeping

- Dedupe `/api/celery/` PUBLIC_PATHS entry (~10 min).
- 9th test coupling from S3013 non-blocking carry (~15 min).

### Option F — Chris's own priority (supersedes A/B/C/D/E)

**Joint recommendation at close:** if you want to keep the auth-hardening streak going, **Option A** (A.2 pattern audit) is the natural continuation. It applies the substrate-hardening trajectory to adjacent surfaces and probably surfaces 1-3 more `scope_queryset_*` predicates to author.

If bias-engineering rule wins, **U5** is fastest (~30 min).

Note: 4 consecutive substrate-hardening sessions (S3016 → S3017 → S3018 → S3019). Watch for engineering-vs-audit balance signal from Chris.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3019 handoff (`docs/handoffs/SESSION_3019_AGENT_MEMORY_SCOPE_PREDICATE.md`).
4. Optional state probes:
   - `git log --oneline -6` — should show docs cascade → `d516743c5` (PR #3723) → S3018 docs cascade `d1cb0d9a7` → `f81d84951` (PR #3721 invariant).
   - `python manage.py test core.tests.test_s3013_bulk_attention_decide_mutation core.tests.test_s3014_create_initiative_from_cluster core.tests.test_s3015_bulk_create_initiatives_from_clusters core.tests.test_s3016_initiatives_list_auth_parity core.tests.test_s3017_memory_detail_auth_gate tests.security.test_public_paths_gate_invariant_s3018 core.tests.test_s3019_agent_memory_scope_predicate --keepdb` — should return 52/52 OK in ~7s.

---

## S3020 carry-forward seeds

### New from S3019

- **A.2 pattern generalization audit** (Option A above) — check AgentExecution / MemoryConnection / MemoryPalaceRoom / cluster endpoints for unscoped `.get()` sites.
- **Fold B `informational`** — predicate-shape-table comment in `object_authz.py`.
- **Fold C `informational`** — implementation-bug caught by test-first discipline (superuser fall-through). Test-first paid off.

### Carried from S3018 (STATUS UPDATED)

- **S3018 Fold C (A.2 cross-user isolation)** — **CLOSED by S3019 PR #3723**.
- **S3018 Fold B (test-time advisory for decorator-chain-break)** — still open, future arc.
- **S3018 Fold D (Rigby response truncation 1st trigger)** — still at 1st trigger; S3019 T1 SIGN was NOT truncated.
- **Method-decorator detection extension** — still open.

### Carried from S3017 (STATUS UPDATED)

- **S3017 Fold A (route-decorator invariant)** — CLOSED by S3018.
- **S3017 Fold C (A.2 cross-user isolation)** — **CLOSED by S3019 PR #3723**.
- **S3017 Fold D (Rigby Tool Gap Ledger — web_fetch_tool DELETE + http_smoke_test middleware-bypass)** — still open.

### Carried from S3016 (STATUS PRESERVED)

- **Dupe `/api/celery/` PUBLIC_PATHS entry** — housekeeping.
- **Fold D `1st trigger`** — doc-only PR + `make recycle-all` policy. Watch for 2nd trigger.
- **Zoom-out carries (from Fold E T0):**
  - Middleware-ordering snapshot test candidate.
  - DRF ViewSet auth-class parallel audit (2nd-trigger watch).
  - WebSocket auth-parity coverage class (likely S3021+).
  - `Bearer <token>` helper extension (~30 min).
- **Fold F `informational`** — inline-scoping classifier expansion.

### Carried from S3015 (STATUS PRESERVED)

- **S3015 Fold F `1st trigger`** — carry-forward retained.
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
- **Fold B `1st trigger`** — S2785 auth-regression mutation-path blind spot (S3016 Fold E + S3017 F-2/F-3 + S3018 invariant + S3019 A.2 predicate all address this class; can now consider partial-close).
- **Fold D `future_trigger`** — `BulkAttentionDecideView` uses Family B envelope shape.
- **Fold E `informational`** — Bulk endpoint decision enum inconsistency.

### Carried from S3012 (STATUS PRESERVED)

- **Task #7 — Delete dead A/B testing handlers** per HALF_BUILT_FEATURES_AUDIT.
- **Task #8 — DRF-decorator refactor** for 15 auth guards in views_learning_loop.py.
- **Fold C `informational`** — `@superuser_required` decorator Family B → Family E migration candidate.

### Carried from S3011 (STATUS PRESERVED)

- **Fold B `5th trigger imminent → assess post-S3019`** — PLAYBOOK-7.4.5 amendment. All recent sessions used `make recycle-all`. **Increment: S3019 also used `make recycle-all` once → trigger imminent, not yet fired.**
- **Fold A `1st trigger` (S3009 LLM-hallucination ledger)** — ZERO hallucinations at S3010-S3019 (**11 sessions continuous**).
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
- **ADR corpus:** ADR-0001 through **ADR-0008 (new)**. Chris ratified ADR-0008 same-PR as the implementation per S3019 open sequence.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow B spec→ship this session (ADR-first-then-implementation).**
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **2× substantive Rigby SIGN cycles (T0 on ADR draft + T1 on implementation). Zero rubber-stamp signals. 11 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing this session: initial ADR ratification via three-part framing ("proceed with Option A for S3019" → "yes ratify and proceed").
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once — post-PR-3723 merge.
- **Verify-before-build (Cycle 1A):** implicit — pre-check confirmed the M2M `agent__user_assignments` traversal shape matched `scope_queryset_agent_execution`'s null-user carve-out pattern before authoring.
- **Fold classification (PLAYBOOK-6.10.8):** 2× `same_pr_actionable → resolved` (Fold A test helper, Fold D S3017 test migration). 2× `informational` (Fold B predicate-shape-table, Fold C implementation-bug-caught).

---

## Wrapper pin note

The active PA conversation pin at S3019 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3019 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3019 shipped a clean 1-PR arc following S3018's ratified Option A directive. The 4-session memory-palace auth trajectory is now fully closed: S3016 audit → S3017 decorator → S3018 invariant → S3019 predicate. S3020 opens with no in-flight arc.**
