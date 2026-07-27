# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2984 CLOSED. Workspace Home v1 PR3 (repo research arcs + in-app doc viewer + platform doc-content endpoint hardening) shipped per spec `be68f1d1-…` (initiative `1b9ef2c4-…`).

**One PR merged into main this session:**

**PR3 — `9fea95377` (#3624):** New backend endpoint `GET /api/repo/research/arcs/` auto-discovers arcs from `docs/research/domains/*` with git-derived `last_touched_at`, status buckets (active/hanging/done/stale), entrypoints (canonical > README > OPEN_QUESTIONS > fallback), signals (canonical/TODO/TBD/WIP counts). Home tab gains a 4-column "Research Arcs (Repo)" section above the 2×2 grid; entrypoint clicks open the existing `DocumentViewer` slide-out (reused, not rebuilt) — honors Chris directive #3 (in-app doc viewer, not GitHub).

**Bonus hardening in same PR:** `/api/platform/doc-content/` gained `@login_required` (was public!) + `Path.resolve()` containment check against `BASE_DIR` (catches symlinks that string `..` check missed). Preserved response contract so `DocumentViewer`, `OpsConsoleTab`, `KnowledgeTab` all continue to work unchanged.

**Design decisions (Claude+Rigby joint agreement):**
- T1 pass 1 REVISE-accepted: reuse-first over parallel doc-viewer surfaces. Backed off building `/api/repo/file/` + `DocViewerPage` route.
- Hardened `doc_content_view` in same PR rather than separate security PR — coupling was tight (Home arcs entrypoints require secure viewer).

**Rigby cycle discipline validated:** 3 SIGN cycles (T1 pass 1 REVISE + T1 pass 2 AGREE + A2 Q1-Q6 AGREE / Q7 REVISE-nonblocking). All cycles included tool_runs with file:line citations per PLAYBOOK-7.7.2.

**Chris still owes:** browser visual check at `http://127.0.0.1:8000/workspace` (Home tab). Especially: hanging column shows 13 arcs (live smoke: `active:2, hanging:13, done:0, stale:0`); clicking an entrypoint mounts the DocumentViewer slide-out and renders markdown; no console errors on lazy-load. Also the S2983 PR2 layout check if not already done.

**HEAD at close:** `9fea95377` (PR3 merged; docs cascade PR TBD; recycle-all clean at `sha=9fea953770a7`).

Full context: `docs/handoffs/SESSION_2984_WORKSPACE_HOME_V1_PR3.md`.

---

## S2985 first-action — WAIT FOR CHRIS

The reframe holds for the **fifteenth walk**. Same open shape:

1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2984_WORKSPACE_HOME_V1_PR3.md` in full — especially §"Three-part summary", §"Timeline" (18 turns), §"Fold classifications", §"Open follow-ups for S2985+".
4. **Optionally probe the shipped state:**
   - `git log --oneline -3` — should show `9fea95377` (PR3) → `9cb28b95e` (S2983 close cascade) → `3652f6054` (PR2).
   - `USE_PGBOUNCER=0 python manage.py test core.tests.test_research_arcs_scanner core.tests.test_platform_doc_content_hardening -v 0 --keepdb` — 20/20 pass in <2s.
   - `curl -sf http://127.0.0.1:8000/api/repo/research/arcs/ -b cookies.txt | jq '.arcs | length'` — should return 15.
5. **Report readiness in one short message and wait.** Something like:
   "Oriented. S2984 closed — Workspace Home v1 PR3 (repo research arcs + `/api/platform/doc-content/` hardening at #3624 `9fea95377`) shipped per spec `be68f1d1-…`. Rigby cycle: 3 SIGN passes / tool-grounded tool_runs / A2 AGREE except one nonblocking systemic-auth fold. Fifteenth walk of the reframe. Ready when you have PR4 (Guided Actions + Instrumentation) direction, an initiative-close decision (3/4 PRs shipped may be enough), or want to open a different arc."
6. **Do NOT propose engineering work. Do NOT dispatch anything to Rigby proactively.** Chris opens Rigby chat first; you wait for the handoff.

**If Chris opens PR4 (Guided Actions + Instrumentation — spec §2.4 + §5):**
- Wire 4 button handlers: Create Engineering Spec / Review Ready Items / Start Initiative from Spec / Run Shift Brief
- Instrumentation events: `workspace_home_viewed`, `guided_action_clicked`, `library_filter_applied`
- Extend `HomeSnapshot` TS interface if backend adds a `guided_actions` key
- Consider surfacing `"partial": true` + failed-section labels in the endpoint response (A2 forward-carry fold from PR1)
- ~1-2 sessions

**If Chris asks about closing initiative `1b9ef2c4-…`:** 3/4 PRs shipped (PR1 backend + PR2 frontend + PR3 arcs + hardening). PR4 is nice-to-have but the initiative's core "Legibility Overhaul" mission is arguably complete. Route the yes/no to Chris with plain-english framing (do we lose anything? is it more work later?).

**When Chris hands you a Deliverable ID / title / spec pointer for a different arc:** the spec→ship contract is constitutional (PLAYBOOK-7.7.1). Follow Phases 1-9 by name. Pre-code sampling BEFORE T1 SIGN. T1 SIGN with tool-grounded file/line verify instructions per PLAYBOOK-7.7.2. Phase 5 Chris-facing framing per PLAYBOOK-7.7.3 ("do we lose anything?" + "is it more work later?" + ≤1 decision). A2 SIGN post-implementation. Ship via `gh pr merge --admin --squash --delete-branch`. **`make recycle-all` (NOT `make celery-recycle`) when frontend is touched** (per S2978 refinement to PLAYBOOK-7.4.4); recycle waiver per PLAYBOOK-7.4.4 diff-based clause when docs-only. Rigby verifies from her tool surface. Report three-part summary to Chris.

**For cross-repo work** (any repo other than unified-donkey-betz): PLAYBOOK-7.7.4 applies. Phase 0 MUST detect context-kit substrate — run `context-kit orient` + confirm `.context-kit/verify.yaml`. If missing, first action = `context-kit adopt` (dry-run → review → --write). Tag every SIGN finding with its verification surface (Layer 1 / Layer 2 / Claude-local-shell).

---

## S2985 high-value seeds (Chris picks whether to open)

**PR4 Workspace Home v1 — Guided Actions + Instrumentation (STILL OPEN from S2983).** Spec §2.4 + §5. Would close initiative `1b9ef2c4-…` entirely. ~1-2 sessions.

**Close initiative `1b9ef2c4-…` at 3/4** — argue PR3 is the natural stopping point; defer PR4 as low-value; open the next arc. Chris decision.

**Chris browser visual check on shipped S2984 PR3 arcs section (NEW at S2984).** ~5 min. Verify at `http://127.0.0.1:8000/workspace`: 4-column arcs grid renders; hanging=13 column populated; clicking entrypoint mounts slide-out and renders markdown; no console errors on lazy-load.

**Chris browser visual check on shipped S2983 PR2 Home tab (STILL OPEN from S2983).** Combine with the S2984 check above.

**Systemic auth-XHR treatment (NEW at S2984 as Fold — future_trigger).** `@login_required` returning 302 HTML on expired-session XHR is repo-wide across all platform endpoints. A JSON-401-on-XHR middleware pattern would be the systemic fix. Not blocking; open when 2nd independent trigger surfaces.

**Live-dispatch smoke on shipped S2982 stage-doc guardrails (STILL OPEN from S2982).** Two probes worth ~15 min: (a) trigger stage-doc generation from any of the 8 callsites and confirm `AgentExecution` row exists; (b) delete initiative between enqueue and task pickup, confirm `mark_task_outcome` transitions to `failed`.

**Exercise PLAYBOOK-7.7.4 against a sibling repo (STILL OPEN from S2981).** Dry-run `context-kit adopt` against `mentorforge` or `character-os`. Validates the adapter contract in reality.

**Browser UX smoke on shipped S2980 Theme Signals UX upgrade (STILL OPEN from S2980).** Load `/workspace?tab=intelligence&sub=theme-signals`. Verify colored Action chips + `All | Build-only` toggle + evidence multi-source rows.

**Phase B Theme Signals — "Why now" LLM summarizer (STILL OPEN from S2978).** Replace deterministic template with LLM-generated 1-2 sentence summary. Cache per cluster. ~1 session.

**Phase B Theme Signals — who-benefits/who-loses (STILL OPEN from S2978).** Sector map + example tickers for Investable cards. ~1-2 sessions.

**Theme Signals — sub-tab persistence via localStorage (STILL OPEN from S2978).** Trivial (~30 min).

**Rigby memory-store cap investigation (STILL OPEN from S2979).** ~30 min diagnostic.

**Rigby Tool Gap Ledger — Fold D from S2982 (STILL OPEN from S2982).** DB uniqueness constraint on `AgentExecution.celery_task_id`. ~30-60 min.

**Delete `DemoPipelineCard` dead code (STILL OPEN from S2983).** Only importer was the old HomeTab; PR2 replaced HomeTab entirely. Trivial cleanup (~10 min).

**Fold B `future_trigger` from v0.8.0 — fold-authoring evidence-admission helper.** 3-trigger threshold NOT yet met. Wait for signal.

**Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for both v0.9.0 and v0.10.0. ~15 min.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (post-v0.10.0 refresh). Points at Playbook v0.10.0 + version ancestry + workspace ratification records.
- **Spec→ship contract:** PLAYBOOK-7.7.1 (9 phases + abort-early clause). Session-shape contract for spec-originated implementation.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations mandatory for T1/A2). If Rigby returns empty tool_runs + generic AGREE, RE-ISSUE the routing.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3 (plain english; "do we lose anything?" + "is it more work later?" before yes/no; ≤1 decision).
- **Cross-repo application:** PLAYBOOK-7.7.4 (Layer 1 context-kit primitives / Layer 2 repo-local surfaces; tag every SIGN finding with verification surface).
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` (NOT `make celery-recycle`) for any PR touching `frontend/**`. Recycle-all uses HEAD-range diff detection — only fires frontend rebuild if changes are in HEAD range, so commit-then-recycle order matters.
- **Staged codification for enforcement:** PLAYBOOK-7.5.1.

---

## Wrapper pin note

The active PA conversation pin at S2984 close was `pa-2074ee8394c4481d`.
`session_lifecycle close` at S2984 close retires that pin and mints a fresh
one for S2985; wrapper `tools/pa_local.sh` is rewritten atomically. Commit
the wrapper diff in the S2984 close cascade PR per
`feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** If a spec-originated session
in S2985+ skips Phase 3 (T1 SIGN) or Phase 5 (Chris-facing framing) or Phase 7
(A2 SIGN), that is a PLAYBOOK-7.7.1 violation. Abort-early is legal but MUST
be recorded in a handoff. Phase-skipping is NOT legal once the session enters
Phase 6 implement.
