# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3013 CLOSED. **U1 Governance batch triage shipped** (PR #3706, `ecfcf8d1a`). Fresh engineering session per Chris bias-engineering rule after 5 consecutive envelope/substrate sessions (S3008→S3012). One bundled PR: frontend batch UI in Workspace → Governance tab + backend defect fix in `BulkAttentionDecideView` (would have 500'd on first click — Rigby A2 SIGN STRENGTHEN caught it) + 8-test mutation-path suite. Cycle 1A verify-before-build paid off HUGE — Rigby's tool_runs surfaced `BulkAttentionDecideView` already existed at S942, cutting spec scope in half. **S3014 opens with no in-flight arc** — fresh engineering or one of the queued follow-ups.

**1 feature PR shipped this session.**

**PR #3706 (`ecfcf8d1a`) — U1: Governance batch triage UI + BulkAttentionDecideView defect fix.**

- **Frontend:** batch selection (checkbox column + Select all/Deselect all + sticky action bar with Approve/Ignore/Reject) + urgency + item_type filter chips + confirm dialog for Reject (Rigby A1 SIGN guardrail against fat-finger mass-reject) + sublabel "Actions apply to Human Attention Items" (Rigby zoom-out mitigation for semantic clarity) + partial-failure handling. Reuses `FeedbackMessage` toast pattern + preserves existing `DecisionDetailModal` click path.
- **Backend (bundled per PLAYBOOK-6.10.8 same_pr_mitigatable):** `BulkAttentionDecideView` had 2 latent defects — wrote invalid status values (`'approved'`/`'rejected'` not in `STATUS_CHOICES`) + wrote to nonexistent `handled_at` field. Would have raised `FieldError` on first authenticated invocation. Fixed with `_BULK_DECISION_TO_MODEL` mapping matching `record_decision()` canonical semantics. API contract preserved (still accepts past-tense enum from UI); only persistence changed.
- **Tests:** new `core/tests/test_s3013_bulk_attention_decide_mutation.py` (156 lines, 8 tests). Extends S2785 auth-regression contract (which only covered blocking) with mutation-path coverage. Includes direct regression assertion `status ∈ STATUS_CHOICES` that would have caught the pre-fix bug. 8/8 PASS in 1.4s.

**Rigby SIGN quality this session:** 5 substantive SIGN cycles, all tool-grounded, ZERO hallucination triggers (matches S3010 + S3011 + S3012 pattern — **4 sessions continuous**).

**HEAD at close:** `ecfcf8d1a` + docs cascade PR (this file + handoff + INDEX regen + wrapper pin bump).

Full context:
- `docs/handoffs/SESSION_3013_U1_GOVERNANCE_BATCH_TRIAGE.md` — full session close, 5 folds (A/B/C/D/E), forward carries, Chris directive transcript.
- `frontend/src/pages/workspace/tabs/GovernanceTab.tsx` — new batch triage UI.
- `frontend/src/lib/api.ts` — `platformApi.bulkAttentionDecide()` method.
- `core/views_human_interface.py` — `BulkAttentionDecideView` defect fix.
- `core/tests/test_s3013_bulk_attention_decide_mutation.py` — new test suite.

---

## S3014 primary directive candidates

**No in-flight arc.** Chris directive-required to select. Options ranked:

### Option A — Fresh engineering (per bias-engineering rule)

Per `feedback_engineering_bias_over_audit`. Concrete candidates:
- Continue the "signal → action" theme (Rigby's U2 candidate from S3013 open — 1-click Initiative + Deliverable pipeline from a signal cluster).
- New spider / new agent capability / dashboard element.
- Chris raises specifics at S3014 open.

**Recommended.** U1 shipped ~1 session of user-facing progress; continuity into another user-facing net-new keeps the trajectory.

### Option B — Batch Defer for Governance tab (follow-up from S3013 U1)

**~1 session.** UI adds 4th action `[Defer N]` to sticky action bar; backend needs new bulk endpoint OR per-item iteration through `/api/human/attention/{id}/defer/`. Follow-up carry from S3013.

**Trade-off:** natural next step from U1; but Defer is less common than Approve/Ignore/Reject.

### Option C — 9th test coupling governance_view.pending_decisions[].id → HumanAttentionItem.id

**~15 min.** Rigby's non-blocking A2 suggestion. Would prevent silent drift if `_get_pending_decisions()` ever added a non-`HumanAttentionItem` source.

**Trade-off:** low-cost regression net; but pure test add.

### Option D — Task #7: Delete dead A/B testing handlers per HALF_BUILT_FEATURES_AUDIT

**~1 session at machine-speed.** Delete ~11 dead handlers in `core/views_ab_testing.py` L82-501 (~600 lines). Carried from S3012. Needs Chris ratification.

### Option E — Task #8: DRF-decorator refactor for 15 auth guards in views_learning_loop.py

**~1 session.** Pure aesthetic cleanup — 15 sites already migrated + working. Carried from S3012.

### Option F — S2785 auth-contract mutation-path sweep (Fold B from S3013)

**~2-3 sessions.** Systematic mutation-path smoke-test sweep of the 19 S2785 auth-inventoried endpoints. Would surface any other latent defects like the `BulkAttentionDecideView` one. Ledger candidate — needs Chris ratification for scope.

### Option G — Chris's own priority

Chris may have surfaced other work between sessions (email, discord, personal channels not in Claude context). Chris-driven directive supersedes A/B/C/D/E/F.

**Joint recommendation at close:** Option A (fresh engineering) as default — U1's shape (single-session user-facing PR with backend cleanup bundled) worked well and matches Chris's bias-engineering rule. If Chris wants continuity from U1, Option B (batch Defer) is the natural next step.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read S3013 handoff (`docs/handoffs/SESSION_3013_U1_GOVERNANCE_BATCH_TRIAGE.md`).
4. Optional state probes:
   - `git log --oneline -5` — should show docs cascade → `ecfcf8d1a` (PR #3706 U1 batch triage) → `455fd32e8` (S3012 close cascade).
   - `python manage.py test core.tests.test_s3013_bulk_attention_decide_mutation --keepdb` — should return 8/8 OK in ~1.5s.
   - Browser smoke: `http://localhost:8000/workspace` → Governance tab → verify checkbox column on Pending Decisions cards, filter chips visible, sticky action bar appears when ≥1 selected.

---

## S3014 carry-forward seeds

### New from S3013

- **Rigby non-blocking A2 suggestion:** 9th test asserting `governance_view.pending_decisions[].id` → `HumanAttentionItem.id`. ~10-line addition. Would prevent silent drift if `_get_pending_decisions()` ever added a non-`HumanAttentionItem` source.
- **Batch Defer capability:** UI has 3 actions (Approve/Ignore/Reject). Batch Defer would require a new bulk endpoint OR per-item iteration.
- **Fold A `1st trigger`** — Cycle 1A verify-before-build saved half a PR (see S3013 handoff). Watch for 2nd — likely already at multiple triggers historically.
- **Fold B `1st trigger`** — S2785 auth-regression contract has a mutation-path blind spot. `BulkAttentionDecideView` would have 500'd on first authenticated invocation because tests only cover blocking, not writes. **Ledger candidate:** mutation-path sweep of 19 S2785-inventoried endpoints.
- **Fold C `informational`** — Rigby's `web_fetch_tool` auth context is unclear (made A2 SIGN harder — she couldn't distinguish "endpoint broken" from "her tool can't reach it"). Rigby Tool Gap Ledger candidate (workspace `b4503364-2573-4401-9e28-61a739e0ce50`).
- **Fold D `future_trigger`** — `BulkAttentionDecideView` still uses Family B envelope shape (`{success, error}`). Candidate for post-T-ENVELOPE cleanup arc if T-ENVELOPE-4 opens.
- **Fold E `informational`** — Bulk endpoint decision enum ('approved'/'ignored'/'rejected') inconsistent with model DECISION_CHOICES ('approve'/'reject'/'ignore'). Fixed via mapping in this PR. Taxonomy unification is a nice-to-have.

### Carried from S3012 (STATUS PRESERVED)

- **Task #7 — Delete dead A/B testing handlers** per HALF_BUILT_FEATURES_AUDIT. ~11 handlers, ~600 lines. Needs Chris ratification.
- **Task #8 — DRF-decorator refactor** for 15 auth guards in views_learning_loop.py. ~1 session.
- **Fold A `1st trigger`** (S3012) — S3011 audit counted grep matches, not real callers. Watch for 2nd trigger.
- **Fold B `1st trigger`** (S3012) — Migration-script text-replacement without line-offset tracking. Ledger deliverable `505dbdc1-9184-478a-b186-1f9e3912807a`.
- **Fold C `informational`** — `@superuser_required` decorator is a Family B → Family E migration candidate. Separate T-slot arc — possibly T-ENVELOPE-4.
- **Fold D `1st trigger`** — Aggressive pipelining safe when audits are read-only.
- **Fold E `informational`** — Test-writing gotcha: handler branch ordering matters.

### Carried from S3011 (STATUS PRESERVED)

- **Fold B `5th trigger imminent → assess post-S3013`** — PLAYBOOK-7.4.5 amendment (`make restart` for Daphne request path). S3013 used `make recycle-all` (broader superset) — counts as event but doesn't necessarily satisfy Fold B's specific signal. Assess again when next Daphne-only issue surfaces.
- **Fold A `1st trigger` (S3009 LLM-hallucination ledger `f4e8481f-...`)** — ZERO hallucinations at S3010 + S3011 + S3012 + S3013 (**4 sessions continuous**). Watch continues.
- **Fold C `1st trigger` (S3009 Rigby shell-exec ledger `e6e7fd6d-...`)** — still open. Watch for 2nd.
- **Fold B `1st trigger` from S3008** (`repo_tool.search no total_matches`) — still open. Bundle candidate with `e6e7fd6d-...` for repo_tool capability expansion arc.

### Carried from earlier sessions (STILL OPEN — unchanged this session)

- **Sports odds leak drain arc** — 32 DRF Response `str(e)` sites in `views_odds_sports.py` grandfathered.
- **future_str_e_variants** — `repr(e)` / `force_str(e)` / `f"{e!r}"` detection extension for B2 lint.
- **Fold C `future_trigger` from S3006** — DRF-decorator refactor for inline auth checks. **Superseded by Task #8**.
- **Fold A/B/C `informational` (1st trigger) from S3005** — PLAYBOOK-7.7.1 abort-early clause / ADR-baseline drift / `refines:` frontmatter field. Watch for 2nd triggers.
- **Fold A `2nd trigger` from S3004** — Fold-Drain-Same-Surface pattern. Watch for 3rd.
- **Fold B `informational` (1st trigger) from S3004** — shared-const derived-union frontend pattern. Watch for 2nd.
- **Fold C `same_pr_mitigatable_deferred_to_next_arc` from S3004** — dedicated `/vip/expired` landing page.
- **Fold D `informational` (1st trigger) from S3004** — Rigby repo_tool line-1 read-display truncation false-positive. Watch for 2nd.
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
- **Fold A/B/C `future_trigger` from S2998** — force=true × factory dedupe semantic mismatch / force re-dispatch could emit DeliverableEvent breadcrumb / Rigby Tool Gap Ledger.
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
- **Chris browser visual checks on S2984 arcs section + S2985 Canonical Briefing tab strip (~5 min each).**
- **Rigby `claude_code_tool` safeguards.** Log to Rigby Tool Gap Ledger.
- **Systemic auth-XHR treatment (S2984 Fold).**
- **Live-dispatch smoke on S2982 stage-doc guardrails (~15 min).**
- **Exercise PLAYBOOK-7.7.4 against a sibling repo.**
- **Browser UX smoke on S2980 Theme Signals UX upgrade (~5 min).**
- **Phase B Theme Signals — "Why now" LLM summarizer (~1 session).**
- **Phase B Theme Signals — who-benefits/who-loses (~1-2 sessions).**
- **Theme Signals sub-tab persistence via localStorage (~30 min).**
- **Rigby Tool Gap Ledger — Fold D from S2982.** DB uniqueness constraint on `AgentExecution.celery_task_id` (~30-60 min).
- **Fold B `future_trigger` from v0.8.0** — fold-authoring evidence-admission helper (3-trigger threshold NOT yet met).
- **Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for v0.9.0 and v0.10.0.
- **Live browser smoke on S3004 VIP-expired modal (~5 min).**
- **ADR-0007 twin-mirror deliverable** — post-close Rigby dispatch to workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` for ratification-record provenance.
- **Batch 3 400→404 image/video not_found verification** (from S3009 forward-carry) — needs UserPlatformAccount test data setup for chris.
- **`superuser_required` decorator Family B → Family E migration candidate** (Fold C from S3012). Separate T-slot arc — possibly T-ENVELOPE-4.
- **`agents/views_monitoring.py` 7 sites** using `core.api_responses.api_error` (different helper). Separate arc.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **ADR corpus:** ADR-0001 through ADR-0007. No open ADR successor arcs.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× clean Flow B spec→ship this session** (A1→implement→A2-STRENGTHEN→fix→re-A2→ship→recycle-all post-merge).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **5× substantive Rigby SIGN cycles.** Zero hallucination triggers. **4 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris routing this session was arc-kickoff-only (approved U1). All PR-level shape decisions handled Claude ↔ Rigby.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` used both pre-merge (for live smoke) and post-merge (constitutional).
- **Verify-before-build (Cycle 1A):** paid off big this session — Rigby's tool_runs surfaced `BulkAttentionDecideView` already existed, cutting scope in half.
- **Fold classification (PLAYBOOK-6.10.8):** backend defect fix classified `same_pr_mitigatable` — bundled into same PR because active scope was increasing the bug's blast radius.

---

## Wrapper pin note

The active PA conversation pin at S3013 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3013 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3013 shipped a clean 1-PR arc following the S3013 00-START Option A (fresh engineering) primary directive:** U1 Governance batch triage + bundled `BulkAttentionDecideView` defect fix. **S3014 opens with no in-flight arc.**
