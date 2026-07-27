# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2989 CLOSED. Send-to-Rigby spec-shape + Audit Findings surface both shipped.

**Three feature PRs merged this session:**

**PR #3638 — `f3337f8e9` (S2989 hotfix opened session):** Dead-URL fix on S2988's per-bullet "Sent — deliverable" link — `frontend/src/components/platform/CanonicalBriefing.tsx:145` pointed at `/workspaces/{ws}/deliverables/{id}` (path-style plural), no such route in App.tsx → blank screen. One-line change to `/workspace?tab=deliverables&workspace={ws}` (query-string pattern already used at `WorkspaceDashboardPage.tsx:474,653,828`). No test coupling. Verified in rebuilt `DocumentViewer-*.js`.

**PR #3639 — `9c17a4775` (S2989 Phase A):** Send-to-Rigby now generates an execution-ready spec (Goal / Context / Open question / Files implicated / Acceptance criteria / Evidence) via gpt-5-mini instead of logging the raw bullet as a bookmark. New `core/services/briefing_spec_generator.py` with strict schema, per-field char caps, fail-open placeholder shape. Rigby SIGN Cycle 1 folds F-A1 (fallback preserves layout) + F-A2 (files_implicated citation-allowlist enforcement — LLM hallucinated paths downgrade to `_inferred — verify_`) + F-A3 (truncation warnings). 21 existing + 2 new tests = 23/23 pass in ~0.8s.

**PR #3640 — `d45d8a954` (S2989 Phase B):** New **Workspace → Intelligence → Findings** sub-tab. `DocResearchFinding` model + hand-written migration `0398_s2989_doc_research_finding.py` + `python manage.py index_doc_research_findings` command + 3 endpoints under `/api/repo/doc-research-findings/` (list / mark / send-to-rigby) + `FindingsTab.tsx` UI. v1 scope: `domains/**/*_{canonical_summary,audit}.md` + `implementation/IMPLEMENTATION_DEBT.md` ACTIVE rows. **Live ingest: 909 parsed → 900 created. 2 IDBT-active + 65 canonical-summary + 833 audit. 90 high / 255 medium / 555 low confidence.** Rigby SIGN Cycle 1 folds F-B1 (rows are truth, no doc markers) + F-B2 (confidence + source_heading tagging) + F-B3 (narrow scope at ingest layer, not model).

**Post-ship live verify:** Chris sent the "Half-wired drf-spectacular" finding from `docs/research/domains/api/2501_api_backend_contract_sot_design_prep_audit.md::Known Technical Debt` through Send-to-Rigby. Resulting Deliverable `9d5134ab-b454-431a-93fa-7f32f2deef82`:
- Goal, Context, Open question all clean and grounded.
- Files implicated: 1 citation + 2 inferred (`core/settings.py`, `core/urls.py`), correctly tagged. F-A2 held perfectly — LLM inferred plausible paths but did not fake them as citation-backed.
- 5 concrete testable acceptance criteria covering both fork branches (enable fully vs. remove).
- Chris quote: "That looks a lot better I think!!"

**Session shape (S2989):** Bug report (dead URL) → PR1 → Chris mental-model reframe ("this isn't the shape I wanted") → Chris chose A now + B same-day → Rigby SIGN Cycle 1 at pre-code design gate (7 substantive folds landed inline before any file was written) → PR2 → PR3 → recycle-all → Chris live verify → close cascade. Rigby's pre-code design SIGN routing at Chris's "loop Rigby in" mid-turn directive was NOT the usual Phase 3/7 SIGN pattern — reinforces `feedback_claude_directs_rigby_then_verifies` (Rigby is not just an executor).

**HEAD at close:** `d45d8a954` (Phase B merge; docs cascade PR TBD; recycle-all clean at `sha=d45d8a954ac6`, frontend `dist/` rebuilt at 11:44 via PLAYBOOK-7.4.4 HEAD-range path diff detection).

Full context:
- `docs/handoffs/SESSION_2989_SEND_TO_RIGBY_SPEC_SHAPE_AND_AUDIT_FINDINGS_SURFACE.md`
- `docs/handoffs/SESSION_2988_CANONICAL_BRIEFING_FIX_AND_SEND_TO_RIGBY.md` (prior)

---

## S2990 first-action — Findings loop first real use OR fresh engineering seed

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read the S2989 handoff in full — especially §"Post-merge live verify" (spec shape validated) and §"Open follow-ups for S2990+".
4. Optional pre-response state probes:
   - `git log --oneline -4` — should show docs cascade → `d45d8a954` → `9c17a4775` → `f3337f8e9`.
   - `USE_PGBOUNCER=0 python manage.py shell -c "from django.apps import apps; D=apps.get_model('core','DocResearchFinding'); print('open:', D.objects.filter(status='open').count(), 'high:', D.objects.filter(status='open',confidence='high').count())"` — 900 open (90 high) as of close.
   - Load `/workspace?tab=intelligence&sub=findings` (Chris view) — confirm Findings tab loads with defaults `status=open, min_confidence=medium+`.

**S2990 opens on Chris directive.** Two dominant flows depending on what Chris asks:

### Flow A — Real-use loop of the Findings surface (highest-leverage seed)

Chris picks 3-5 high-confidence findings from the UI, sends each to Rigby, and Claude executes them one by one. Loop closes when findings marked fixed via UI. This is the S2989 workflow going live — the point of building Phase B was to give Chris an entry into systematic audit-close work.

**Suggested initial picks (Chris chooses; these are examples):**
- IDBT-0001 (partial-discharge HIGH — first-queue leaf tail unenumerated). Substantial re-extraction; multi-session.
- IDBT-0002 (RAG-owned embed_documents no-op on content-change updates). Delegated to Group 2100 RAG arc per Chris directive; keep queued not executed.
- The "Half-wired drf-spectacular" finding (`4b92f6f0-b84b-47d1-976a-30246f3dbd3d`) — the one Chris already generated a spec for at S2989 close. Ready to execute if he wants a natural test run.
- Any `domain_slug=frontend` or `domain_slug=pa` finding at `confidence=high` — Chris uses those surfaces most.

**Execution pattern per finding:**
1. Load Deliverable from Donkey Betz workspace (already spec-shaped from Send-to-Rigby).
2. Read the Goal + Open question — if the fork is genuine, route to Chris for the yes/no.
3. If unambiguous, execute against Files implicated + Acceptance criteria.
4. Ship PR; Chris live-verifies; Chris marks finding `fixed` in UI.
5. Continue to next finding.

### Flow B — Fresh engineering seed (if Chris opens with something else)

Top seeds from S2988→2989 handoff carry-forward:
- **F-D3-tracker-scope wire-up (HIGHEST LEVERAGE, STILL OPEN from S2987).** Activate the OpsRun tracker for PA turns so the `memory_injected` trace payload actually lands in the audit stream. Est ~1 session.
- **F-D2-broad LLM-bypass audit spec (STILL OPEN from S2986).** 14+ `enforce_real_ai(` + 9 `client.responses.create(` + 80 `client.chat.completions.create(` non-PA callsites. Audit doc first; per-site preflight wire-up as follow-ups.
- **memory_hygiene_audit --apply on 1805 cap-drift (STILL OPEN from S2987).** ~30 min diagnostic + apply with `--stale-days 30 --stale-importance-lt 10 --apply`.
- **Canonical Briefing v2 scope toggle (STILL OPEN from S2985).** Arc-Folder vs All-Docs dropdown + `Document.file_path` index migration.

---

## S2990 high-value seeds from S2989 (Chris picks whether to open)

### Findings-surface follow-ups (NEW at S2989 close)

- **v2 ingest scope widening — `implementation/BACKLOG.md` parser** — the IOS-schema table has ~40+ intake rows in various statuses (`TRIAGED` / `IN_ARC` / `SHIPPED` / `LOCAL_ACCEPTED` / `PRODUCTION_DEFERRED`). Skip terminal statuses; surface actionable ones as findings. Needs 1-2 hours of IOS schema study first. Trigger: if Chris uses Findings for 2+ sessions and mentions "I know there's stuff in BACKLOG we should surface."
- **v2 ingest scope widening — `implementation/*/` subfolders** — design-prep + scoping docs have open items but noisier than domain audits. Trigger: if Chris explicitly asks about arc I-0100 / I-0200 / etc. open items and can't find them in the current surface.
- **v2 UI: per-doc "explore" mode** — click a doc to see all findings for that doc in one context view. Currently flat list. Est ~1-2 hours. Trigger: if Chris says "the flat list is hard to prioritize."
- **F-A2 test coverage widening** — one test currently covers file-path downgrade; add a test for `warnings[]` being populated on truncation of goal / context / open_question / AC. Est ~15 min.
- **Rigby SIGN Cycle 2 on Phase A+B shipped state** — DEFERRED at S2989 close because Chris asked for close cascade. Would exercise a second SIGN loop against the shipped surface (spec quality on real specs, ingest false-positive rate, UI defaults). Trigger: if Chris hits friction using Findings for 2+ sessions.
- **Send-to-Rigby follow-ups from S2988 (STILL OPEN)** — per-section "Send all", workspace routing inference from arc slug, LLM-mediated deliverable creation via Rigby's actual turn loop. Any of these need Chris explicit ask.

### Carry-forward from S2988 (STILL OPEN)

- **F-D3-tracker-scope wire-up** — activate OpsRun tracker for PA turns. ~1 session. Highest-leverage backend seed.
- **F-D2-broad LLM-bypass audit spec** — evaluate user-facing personalization impact of each `enforce_real_ai` / `chat.completions` / `responses.create` non-PA callsite. Est ~1 session for the audit doc; each preflight wire-up is a small follow-up PR.
- **Reconcile Chris's 1805 cap-drift via `memory_hygiene_audit --apply`.** ~30 min diagnostic + apply. Recommended one-off: `--stale-days 30 --stale-importance-lt 10 --apply`.
- **Canonical Briefing v2 scope toggle.** Arc-Folder / All-Docs + default exclude-globs. Additive UI + one migration (`Document.file_path` index). ~1-2 hr.
- **Substrate fix for `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`.** S2988 added `briefing_action_item`; systemic fix (default `deliverable_type` from `category` + skip missing_initiative_id marker for governance-scoped categories) still open. ~1 session.
- **Rigby tool allowlist expansion (STILL OPEN from S2987).** Add `OpsRunEvent` + `UserMemoryContext` + now `DocResearchFinding` to `orm_inspect_tool` allowlist. ~15-30 min. Log to Rigby Tool Gap Ledger.
- **Chris browser visual check on S2985 Canonical Briefing tab strip / Refresh behavior.** ~5 min.
- **Rigby `claude_code_tool` safeguards.** Log to Rigby Tool Gap Ledger.
- **Chris browser visual check on S2984 arcs section.** ~5 min.
- **Systemic auth-XHR treatment (STILL OPEN from S2984 as Fold).** JSON-401-on-XHR middleware pattern. Not blocking; open when 2nd independent trigger surfaces.
- **Live-dispatch smoke on S2982 stage-doc guardrails.** ~15 min.
- **Exercise PLAYBOOK-7.7.4 against a sibling repo.** Dry-run `context-kit adopt` against `mentorforge` or `character-os`.
- **Browser UX smoke on S2980 Theme Signals UX upgrade.** ~5 min.
- **Phase B Theme Signals — "Why now" LLM summarizer.** ~1 session.
- **Phase B Theme Signals — who-benefits/who-loses.** ~1-2 sessions.
- **Theme Signals — sub-tab persistence via localStorage.** ~30 min.
- **Rigby Tool Gap Ledger — Fold D from S2982.** DB uniqueness constraint on `AgentExecution.celery_task_id`. ~30-60 min.
- **Fold B `future_trigger` from v0.8.0 — fold-authoring evidence-admission helper.** 3-trigger threshold NOT yet met. Wait for signal.
- **Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for both v0.9.0 and v0.10.0. ~15 min.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (post-v0.10.0 refresh). Points at Playbook v0.10.0 + version ancestry + workspace ratification records.
- **Spec→ship contract:** PLAYBOOK-7.7.1 (9 phases + abort-early clause). Session-shape contract for spec-originated implementation.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations mandatory for T1/A2). If Rigby returns empty tool_runs + generic AGREE, RE-ISSUE the routing.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3 (plain english; "do we lose anything?" + "is it more work later?" before yes/no; ≤1 decision). Applied to the Phase A/B scope-choice + implementation/ inclusion decision this session.
- **Cross-repo application:** PLAYBOOK-7.7.4 (Layer 1 context-kit primitives / Layer 2 repo-local surfaces; tag every SIGN finding with verification surface).
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` (NOT `make celery-recycle`) for any PR touching `frontend/**`. Confirmed working this session — frontend rebuilt after PR #3638 (frontend href fix) and PR #3640 (Phase B UI); skipped after PR #3639 (backend-only).
- **Rigby SIGN pre-code at Chris directive** — `feedback_claude_directs_rigby_then_verifies` scope expanded this session: pre-code design-gate SIGN routing at Chris's "loop Rigby in" direction is legitimate and produced 7 substantive folds inline. Not codified into playbook yet; wait for second independent instance.

---

## Wrapper pin note

The active PA conversation pin at S2989 close will be minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S2989 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** If a spec-originated session in S2990+ skips Phase 3 (T1 SIGN) or Phase 5 (Chris-facing framing) or Phase 7 (A2 SIGN), that is a PLAYBOOK-7.7.1 violation. Abort-early is legal but MUST be recorded in a handoff. S2989 was NOT spec-originated (bug report → Chris reframe → feature extension), so straight-through Claude direct→execute→verify with Rigby pre-code design SIGN was legitimate.
