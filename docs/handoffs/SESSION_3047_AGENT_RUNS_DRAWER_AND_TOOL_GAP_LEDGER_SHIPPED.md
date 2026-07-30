# Session 3047 — Agent Runs drawer Lineage & Fanout + Rigby Tool Gap Ledger tab SHIPPED

**Date:** 2026-07-30
**HEAD at close:** `4cc88e639` (post PR #3806 merge; wrapper pin bump commit follows)
**Session pin (retired at close):** `pa-173b972d6840475b`

---

## TL;DR

Two net-new engineering slices in one session. Both closed cleanly. Rigby's SIGN discipline caught two real issues (auth-leak future_trigger + response-key bug) that would have shipped to Chris otherwise — both discharged in-session. Zero open future_triggers attributable to S3047 arc.

**4 PRs shipped:**
1. **PR #3803** — `feat(s3047)`: Agent Runs drawer Lineage & Fanout section + shared compute helper (`agent_fanout.py`)
2. **PR #3804** — `fix(s3047)`: A2 SIGN Q4 fold discharge — scope child rows in fanout helper (upgrades `future_trigger` → `same_pr_mitigatable`)
3. **PR #3805** — `feat(s3047 slice 2)`: Tool Gap Ledger tab — Rigby engineering_backlog dashboard
4. **PR #3806** — `fix(s3047 slice 2)`: response-key alignment (`data.deliverables` / `data.deliverable`)

---

## Slice 1 — Agent Runs drawer Lineage & Fanout (PR #3803 + #3804)

### Why toward users

Chris ratified enhancing the existing `System → Agent Runs` tab rather than adding a new tab (S3042 Q3/Q4 tab-coherence). Direct operator visibility into what Rigby is dispatching, ties the S3046 `agent_job_status` fanout surface to a live UI.

### What shipped (PR #3803)

- **NEW** `core/services/agent_fanout.py` — `compute_fanout(execution)` helper factored from S3046 inline block. Single-codepath source for both the PA tool AND the REST view.
- **REFACTORED** `_handle_agent_job_status` — replaces inline ORM with `**compute_fanout(execution)` spread. Behavior preserved 1:1 (7 S3046 tests remain green).
- **EXTENDED** `execution_detail` REST view — merges helper output into `data.execution`.
- **EXTENDED** `AgentRunsTab.tsx`:
  - Typed `AgentRunChild` interface + 7 new fields on `AgentRunDetailResponse.execution`
  - New `IdChip` helper (truncated ID + copy-full-UUID affordance)
  - New "Lineage & Fanout" section in `DetailPanel` (parent/root cards, count tiles, expandable children list)
  - `onSelectExecution` prop wired → click parent/root/child IDs replaces drawer selection (single-panel navigation, no stack)
- **13 tests green** — 7 S3046 handler regression + 4 helper + 2 view (`children_truncated` invariant lockdown)
- **DOC** `agent_job_status_validation.md` §7.4 — notes shared helper location

### Rigby SIGN cycles

**T1 SIGN (pre-code):** All 5 dimensions AGREE + 4 `same_pr_mitigatable` folds — typed children shape / `children_truncated` invariant test / truncated IDs + copy / verify migration 0336 indexes. All discharged in envelope.

**A2 SIGN v1 (post-merge live):** All 4 dimensions AGREE. Single-codepath verified by:
- PA tool `agent_job_status(c2c60f72...)` returned 7 fanout fields
- REST `GET /api/v1/agents/execution/c2c60f72.../` returned identical values for the same 7 fields

**A2 SIGN v1 Q4 zoom-out fold — future_trigger:** Auth-leak concern. `execution_detail` scopes the parent via `scope_queryset_agent_execution` but `compute_fanout()` queried children unscoped. Cross-user child row could leak if `parent_execution_id` were bug-written cross-user. Not biting in single-owner but real for future multi-tenant graphs.

### Discharge (PR #3804)

- `compute_fanout(execution, *, scoped_queryset=None)` — kwargs-only optional; default None preserves S3046 behavior (matches PA tool caller path).
- REST view passes `scope_queryset_agent_execution(request.user, AgentExecution.objects.all())` → helper.
- 2 new scoping tests: (a) unscoped default returns cross-user child (backward-compat) (b) scoped filters cross-user child even when `parent_execution_id` points at visible parent.
- **All 15 tests green.**

**A2 SIGN v2 (post-discharge):** All 3 dimensions AGREE. Fold upgraded `future_trigger` → `same_pr_mitigatable`. Zero open future_triggers from slice 1.

---

## Slice 2 — Rigby Tool Gap Ledger tab (PR #3805 + #3806)

### Why toward users

Chris requested "let's do B" — Rigby's second S3047 candidate (Ledger tab). Now that Rigby's Tool Gap Ledger has been accumulating rows (14 total, 12 ready + 2 completed as of session open), there was no operator dashboard for reviewing status/what to slate/what to discharge.

### What shipped (PR #3805)

- **NEW** `frontend/src/pages/workspace/tabs/ToolGapLedgerTab.tsx` (~330 lines)
  - Hard-scoped to Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` via `TOOL_GAP_LEDGER_WORKSPACE_ID` constant (single edit point).
  - Reuses `deliverablesApi.list({type: 'engineering_backlog', workspace, per_page: 100})` — zero new backend.
  - Groups rows by status (ready → in_progress → draft → deferred → completed).
  - Row: title + category badge + created/updated relative time.
  - Row click → right-side detail drawer with ReactMarkdown + rehypeSanitize + remarkGfm body.
  - 30s refetch + explicit refresh button.
  - Header note: "stored in the Donkey Betz workspace" (transparency).
- **REGISTERED** in `tabs/index.ts` barrel export + `WorkspacePageNew.tsx` (nav entry + import + conditional render).

### Rigby SIGN cycles

**T1 SIGN (pre-code):** 3 `same_pr_mitigatable` folds + 1 **DISAGREE** on `priority` field (doesn't exist in deliverable list payload). Rigby snapshot: 14 rows, 12 ready + 2 completed, `priority` absent, `category` populated (`governance`, `engineering_backlog`, etc). Fix: dropped `priority`, added `category` badge. All folds discharged in envelope.

**A2 SIGN slice-2 (post-merge live):** Live-fetch on the exact URL the tab hits caught **response-key bug** — API returns `data.deliverables` (list) + `data.deliverable` (detail), but the tab destructured `data.results`/`data.items` + `data.results`/`data.data`. Effect: tab rendered "No ledger rows" for all 14 rows + detail drawer never populated.

### Discharge (PR #3806)

- `LedgerListResponse.deliverables?: LedgerRow[]`
- `LedgerDetailResponse.deliverable?: LedgerDetailRow`
- Reads `data.deliverables` (list) + `data.deliverable` (detail) — matches `DeliverablesTab.tsx:473 + :482` proven-in-prod shape.

**A2 SIGN slice-2 v2 (post-fix):** AGREE. Rigby verified live API returns 14 rows under `deliverables` key + frontend reads `data?.deliverables` at line 220. Production-ready.

---

## Constitutional signals

- **33rd consecutive Cycle 1A verify-before-build session.** Applied at least 4 times within-session:
  - Slice 1 open — gap map + Agent Runs surface discovery
  - Slice 1 spec — read existing S3046 fanout block before extraction
  - Slice 2 open — DeliverablesTab + `engineering_backlog` type + `deliverablesApi` inspection
  - Slice 2 fix — read `DeliverablesTab.tsx:473+:482` proven-in-prod shape before response-key fix
- **26th consecutive zero-hallucination Rigby SIGN streak.** 6 substantive cycles this session (T1 slice 1 + A2 v1 + A2 v2 slice 1 discharge + T1 slice 2 + A2 slice 2 + A2 v2 slice 2 fix). All with real `tool_runs` (line reads / grep / live web_fetch / dispatch payloads).
- **PLAYBOOK-7.7.1 (spec→ship)**: 2 arcs, both walked pre-code T1 + post-merge A2. Slice 1 additionally walked in-arc discharge (T1 → code → A2 v1 → fold code → A2 v2).
- **PLAYBOOK-7.7.2 (SIGN evidence)**: All SIGNs backed by tool_runs (Rigby explicitly cited line ranges + response payloads + grep results). Zero rubber-stamps.
- **PLAYBOOK-7.7.3 (Chris-facing framing)**: One Chris decision this session (ratify S3047 first-action A) + one continuation decision (do B too).
- **PLAYBOOK-7.7.5 (class-scoped A2 sweep)**: does not fire — both slices were net-new capability, not drift/hardening.
- **PLAYBOOK-3.2.3 (dispatcher-path tests)**: slice 1 tests use `TestCase` (helper direct-invoke) + `APIClient` (view test) — not handler dispatcher tests (compute_fanout isn't a handler).
- **feedback_recycle_after_merge**: Two `make recycle-all` runs (both slices touched frontend). Bundle hashes: `index-C7gpHFk7` → `index-Dv87Aivl` → `index-WK39JypS` → `index-D9gM74N9` (final).
- **feedback_engineering_bias_over_audit**: Both slices were net-new capability, not audit-shape.
- **feedback_workspace_over_command_center_for_new_ui**: Both slices extended Workspace tabs.
- **feedback_gh_pr_merge_admin_until_billing_fixed**: All 4 PRs merged with `--admin`.

---

## Substrate ledger changes

**Zero new rows.** Both A2 folds classified `same_pr_mitigatable` and discharged in-arc:
- Slice 1 A2 Q4 (auth-leak) — was `future_trigger`, upgraded to `same_pr_mitigatable` via PR #3804.
- Slice 2 A2 (response-key) — same-arc discharge via PR #3806.

**Existing rows carry forward unchanged.** No S3047 arc discharged any prior substrate ledger rows either (both slices were pure net-new capability).

---

## Known-in-flight forward carries

Unchanged from S3046:
- **Ledger row `d1182b61-…`** — AgentExecution lineage threading fix. 1785/1785 NULL confirmed. MEDIUM priority. **NOW MORE VALUABLE with the S3047 Agent Runs drawer live** — visible fanout counts stay stuck at 0 until this ships. Reasonable next-session pick.
- Odds API operationally degraded (Chris directive S3045).
- Skiplist re-validation (5 media/audio tools) — deferred.
- `agent_router.py:2131-2132` silent fallback — 1st future_trigger (S3043).
- T1 Fold future_trigger `typing.Literal[actor]` — 1st (S3036).
- A2 Fold future_trigger actor-taxonomy vs frontend-palette drift — 1st (S3036).
- `did_X` semantics — 2nd (S3034).
- S3033 Fold B ledger persistence timing — 1st discharged.
- S3030 prod deploy carry — `backfill_canonical_drift --apply` on Railway.
- S3032 Fold E — `orm_inspect_tool` allowlist accretion.
- S3031 Fold B — spy fragility.
- S3034 A2 Folds — subscriber wire-contract fragility + adjacent-axis superseded/experiment.
- S3042 arc Q3/Q4 — Spine Contract v1 §§1+3 (frontend event instrumentation + Workspace UI redo Arc C).
- `chris-personal` orphan-initiative cleanup pass — Spine Contract v1 §4.
- Stem-matcher warn-only lint (Option B) — S3044 row 1; 3-trigger threshold reached; deferred per Rigby T0 SIGN Q5.
- `/docs/` restructuring arc — queued (Chris directive S2800).
- T2 spec for `agent_router.py:2131-2132` silent fallback — deferred.

---

## Bundle hash tracking

Final bundle after PR #3806 recycle: `dist/assets/index-D9gM74N9.js` (2,861.91 kB / gzip 658.00 kB) + `dist/assets/index-Cf2ZOubx.css` (118.34 kB / gzip 17.72 kB). Wrapper pin bump commit (post-close) picks up the `core/templates/index.html` update to match.
