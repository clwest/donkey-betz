# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2983 CLOSED. Workspace Home v1 PR1 (backend snapshot endpoint) + PR2 (frontend Home tab redesign) shipped per spec `5e1c702f-…` (initiative `1b9ef2c4-…`, exec plan `ab0c4872-…`).

**Two PRs merged into main this session:**

**PR1 — `107c4ad04` (#3621):** Backend snapshot endpoint at `GET /api/workspaces/<uuid:workspace_id>/home/` returning `workspace / now / active_work / library` per spec §3.1. Per-section try/except with logged empty defaults so partial rendering survives section failures. Caps at 20 per list. Owner-only auth via reused `_get_workspace()`. 9 unit tests: `USE_PGBOUNCER=0 python manage.py test core.tests.test_workspace_home_snapshot -v 2 --keepdb` → 9/9 pass in 0.5s.

**PR2 — `3652f6054` (#3622):** Frontend Home tab full-replace of the prior Session 1078 platform dashboard. New shape per spec §1.1 — greeting band + 2×2 grid of NOW / ACTIVE WORK / LIBRARY / GUIDED ACTIONS. GUIDED ACTIONS rendered as 4 disabled stub buttons with PR4 tooltips. Live smoke against Donkey Betz workspace returned 18 initiatives / 20 action items / 20 pinned / 27 new deliverables in last 24h.

**Design decisions (Claude+Rigby joint agreement):**
- PR2 Option A-prime+ picked over full-preserve options: full-replace + keep greeting band + keep hours-since-visit chip (orthogonal to spec but genuinely useful UX). All other prior HomeTab panels (vitals/celery/attention/deliv-stats) dropped — they're already covered by System sub-tabs.
- DemoPipelineCard is now dead code (only prior importer was old HomeTab). Not deleted yet — flagged for cleanup follow-up.

**Rigby cycle discipline validated:** 4 SIGN cycles this session (T1 pass 1 + pass 2 for PR1, joint design agreement for PR2, A2 for both PRs). 45+ tool_runs total with file:line citations. Two "REVISE on tool-scope" verdicts from Rigby (she can't run shell/vite/manage.py from her PA surface) — Claude verified those items independently (tsc clean, vite build 3.38s, live Django Client smoke 200 with real payload).

**Chris still owes:** browser visual check at `http://127.0.0.1:8000/workspace` (Home tab loads by default). Claude can't verify UI layout from CLI per CLAUDE.md rule. If layout is off, PR3 opens with a visual-fix patch commit before Library filters land.

**HEAD at close:** `3652f6054` (both PRs merged; docs cascade PR TBD; recycle-all clean at `sha=3652f60545b1`).

Full context: `docs/handoffs/SESSION_2983_WORKSPACE_HOME_V1_PR1_PR2.md`.

---

## S2984 first-action — WAIT FOR CHRIS

The reframe holds for the **fourteenth walk**. Same open shape:

1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2983_WORKSPACE_HOME_V1_PR1_PR2.md` in full — especially §"Three-part summary", §"Timeline" (31 turns), §"Fold classifications", §"Open follow-ups for S2984+".
4. **Optionally probe the shipped state:**
   - `git log --oneline -3` — should show `3652f6054` (PR2) → `107c4ad04` (PR1) → `7af3d4ceb` (S2982 close cascade).
   - `USE_PGBOUNCER=0 python manage.py test core.tests.test_workspace_home_snapshot -v 0 --keepdb` — 9/9 pass in <1s.
   - `curl -sf http://127.0.0.1:8000/workspace | head` — should return the Home tab HTML (if Daphne is running).
5. **Report readiness in one short message and wait.** Something like:
   "Oriented. S2983 closed — Workspace Home v1 PR1 (backend snapshot at #3621) + PR2 (frontend Home tab redesign at #3622) shipped in a single session per spec `5e1c702f-…`. Rigby cycle: 4 SIGN passes / 45+ tool_runs / A2 AGREE on both PRs (frontend A2 REVISE-on-scope, code-level AGREE). Fourteenth walk of the reframe. Ready when you have PR3 (Library filters) direction or want to open a different arc."
6. **Do NOT propose engineering work. Do NOT dispatch anything to Rigby proactively.** Chris opens Rigby chat first; you wait for the handoff.

**If Chris opens PR3 (Library filters + Canonical heuristic — spec §2.3 + §2.3.1):**
- Filter pills: Type (Spec/Decision/Research/Report/Content) × Status (draft/ready/published/archived/completed) × Pinned × Canonical
- Search bar (title + keyword)
- Canonical heuristic: `is_pinned==True OR (data_sensitivity in {internal, public} AND status in {ready, published, completed} AND title.startswith(one of {'ENGINEERING SPEC —', 'RATIFICATION_', 'DECISION_'}))`
- Existing DeliverablesTab filter UI (`frontend/src/pages/workspace/tabs/DeliverablesTab.tsx`) is the reuse candidate — pre-code sample it first
- Spec→ship contract applies: PLAYBOOK-7.7.1 Phases 1-9 by name. T1 SIGN with tool-grounded verification per PLAYBOOK-7.7.2

**If Chris opens PR4 (Guided Actions + Instrumentation — spec §2.4 + §5):**
- Wire 4 button handlers: Create Engineering Spec / Review Ready Items / Start Initiative from Spec / Run Shift Brief
- Instrumentation events: `workspace_home_viewed`, `guided_action_clicked`, `library_filter_applied`
- Extend `HomeSnapshot` TS interface if backend adds a `guided_actions` key
- Consider surfacing `"partial": true` + failed-section labels in the endpoint response (A2 forward-carry fold from PR1)

**When Chris hands you a Deliverable ID / title / spec pointer for a different arc:** the spec→ship contract is constitutional (PLAYBOOK-7.7.1). Follow Phases 1-9 by name. Pre-code sampling BEFORE T1 SIGN. T1 SIGN with tool-grounded file/line verify instructions per PLAYBOOK-7.7.2. Phase 5 Chris-facing framing per PLAYBOOK-7.7.3 ("do we lose anything?" + "is it more work later?" + ≤1 decision). A2 SIGN post-implementation. Ship via `gh pr merge --admin --squash --delete-branch`. **`make recycle-all` (NOT `make celery-recycle`) when frontend is touched** (per S2978 refinement to PLAYBOOK-7.4.4); recycle waiver per PLAYBOOK-7.4.4 diff-based clause when docs-only. Rigby verifies from her tool surface. Report three-part summary to Chris.

**For cross-repo work** (any repo other than unified-donkey-betz): PLAYBOOK-7.7.4 applies. Phase 0 MUST detect context-kit substrate — run `context-kit orient` + confirm `.context-kit/verify.yaml`. If missing, first action = `context-kit adopt` (dry-run → review → --write). Tag every SIGN finding with its verification surface (Layer 1 / Layer 2 / Claude-local-shell).

---

## S2984 high-value seeds (Chris picks whether to open)

**PR3 Workspace Home v1 — Library filters + Canonical heuristic (STILL OPEN from S2983).** Spec §2.3 + §2.3.1. See handoff §"Open follow-ups". ~1-2 sessions. Reuse DeliverablesTab filter UI patterns.

**PR4 Workspace Home v1 — Guided Actions + Instrumentation (STILL OPEN from S2983).** Spec §2.4 + §5. Wire 4 button handlers + 3 instrumentation events. ~1-2 sessions.

**Chris browser visual check on shipped S2983 PR2 Home tab (STILL OPEN from S2983).** ~5 min. Open `http://127.0.0.1:8000/workspace`. Verify: greeting band shows time-of-day + user name + hours-since-visit chip; 2×2 grid renders 4 modules; ACTIVE WORK shows real initiatives + action items; LIBRARY shows real pinned/recent deliverables; GUIDED ACTIONS buttons are disabled with hover tooltips. If anything is broken, patch before opening PR3.

**Live-dispatch smoke on shipped S2982 stage-doc guardrails (STILL OPEN from S2982).** Two probes worth ~15 min: (a) trigger a stage-doc generation from any of the 8 callsites and confirm the `AgentExecution` row exists via `AgentExecution.objects.filter(owner_agent='InitiativeStageDispatch').order_by('-created_at').first()`; (b) delete an initiative between enqueue and task pickup, confirm `mark_task_outcome` transitions the row to `failed`.

**Exercise PLAYBOOK-7.7.4 against a sibling repo (STILL OPEN from S2981).** Dry-run `context-kit adopt` against `mentorforge` or `character-os` (both in `/Users/donkeyking/development/`). Validates the adapter contract in reality.

**Browser UX smoke on shipped S2980 Theme Signals UX upgrade (STILL OPEN from S2980).** Load `/workspace?tab=intelligence&sub=theme-signals`. Verify colored Action chips + `All | Build-only` toggle + evidence multi-source rows.

**Phase B Theme Signals — "Why now" LLM summarizer (STILL OPEN from S2978).** Replace deterministic template with LLM-generated 1-2 sentence summary. Cache per cluster. ~1 session.

**Phase B Theme Signals — who-benefits/who-loses (STILL OPEN from S2978).** Sector map + example tickers for Investable cards. ~1-2 sessions.

**Theme Signals — sub-tab persistence via localStorage (STILL OPEN from S2978).** Trivial (~30 min).

**Rigby memory-store cap investigation (STILL OPEN from S2979).** ~30 min diagnostic.

**Rigby Tool Gap Ledger — Fold D from S2982 (STILL OPEN from S2982).** DB uniqueness constraint on `AgentExecution.celery_task_id`. ~30-60 min.

**Delete `DemoPipelineCard` dead code (NEW at S2983).** Only importer was the old HomeTab; PR2 replaced HomeTab entirely. Trivial cleanup (~10 min).

**Fold B `future_trigger` from v0.8.0 — fold-authoring evidence-admission helper.** 3-trigger threshold NOT yet met. Wait for signal.

**Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for both v0.9.0 and v0.10.0. ~15 min.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (post-v0.10.0 refresh). Points at Playbook v0.10.0 + version ancestry + workspace ratification records.
- **Spec→ship contract:** PLAYBOOK-7.7.1 (9 phases + abort-early clause). Session-shape contract for spec-originated implementation.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations mandatory for T1/A2). If Rigby returns empty tool_runs + generic AGREE, RE-ISSUE the routing. Note: "REVISE on tool-scope" (I-can't-run-shell) is NOT a rubber-stamp — it's honest scoping and doesn't count as an empty tool_runs violation.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3 (plain english; "do we lose anything?" + "is it more work later?" before yes/no; ≤1 decision).
- **Cross-repo application:** PLAYBOOK-7.7.4 (Layer 1 context-kit primitives / Layer 2 repo-local surfaces; tag every SIGN finding with verification surface).
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` (NOT `make celery-recycle`) for any PR touching `frontend/**`. Recycle-all uses HEAD-range diff detection — only fires frontend rebuild if changes are in HEAD range, so commit-then-recycle order matters.
- **Staged codification for enforcement:** PLAYBOOK-7.5.1.

---

## Wrapper pin note

The active PA conversation pin at S2983 close was `pa-f7a426d0dace4490`.
`session_lifecycle close` at S2983 close retires that pin and mints a fresh
one for S2984; wrapper `tools/pa_local.sh` is rewritten atomically. Commit
the wrapper diff in the S2983 close cascade PR per
`feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** If a spec-originated session
in S2984+ skips Phase 3 (T1 SIGN) or Phase 5 (Chris-facing framing) or Phase 7
(A2 SIGN), that is a PLAYBOOK-7.7.1 violation. Abort-early is legal but MUST
be recorded in a handoff. Phase-skipping is NOT legal once the session enters
Phase 6 implement.
