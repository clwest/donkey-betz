# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2987 CLOSED. Memory PR2 shipped per spec `ba968ac1` (arc closed).

**Two PRs merged this cascade (S2986 PR1 + S2987 PR2), closing the entire `ba968ac1` spec arc:**

**PR #3631 — `857633411` (S2986 PR1):** `remember_tool.save` reliability — save-return includes `status`/`truncated`/`original_len`, cap-hit migrated to S2879 shape, pre-parse oversize gate at `unified_pa_entrypoint.py:2232-2272`, PA prompt header rename to reduce parroting, 10 happy-path tests, operator doc.

**PR #3633 — `95d3cdc65` (S2987 PR2):** Memory utilization trace + supersede migration + hygiene command + auto-promotion cap-fix. `MemoryContextService.get_prompt_context_with_trace(user)` returns `(context, retrieved_ids, layer)`; `memory_injected` OpsRunEvent extended with `retrieved_memory_ids` + `layer` payload. `UserMemoryContext` gained `is_active` + `superseded_by` + `superseded_at` fields with composite index. `memory_promotion_service` at-cap DEMOTES oldest+lowest-importance auto_promotion row (SKIPS if none available with machine-readable `reason`). `memory_hygiene_audit` management command surfaces stale + cap-drift + conflicts with `--dry-run` default and `--apply` supersede (never DELETE). D2 (non-PA preflight) descoped after target `ProjectBuilderOrchestrator._build_project_with_llm_only` verified as dead-invocation code.

**Session shape (S2987):** PLAYBOOK-7.7.1 spec→ship, all 9 phases walked. 3 Rigby SIGN cycles (T1 REVISE / A2 pass 1 REVISE / A2 pass 2 PROCEED-TO-MERGE). 6 same-PR folds shipped (F-PR2-1/2 + F-A2-1/2/3 + F-D2-descope). 6 future_triggers logged including F-D3-tracker-scope (NEW at S2987 close from post-merge smoke — `memory_injected` OpsRunEvent has fired zero times ever because `get_active_tracker()` returns None in PA turn context; substrate is ready, only bridge is dormant).

**Post-merge live-dispatch smoke confirmed:**
- Migration landed cleanly (`is_active`/`superseded_by_id`/`superseded_at` columns present, 1805 rows preserved).
- `remember_tool.save` still enforces cap with S2879 envelope shape (`error_code='cap_hit'`).
- `memory_hygiene_audit --user chris` surfaced correct CAP-DRIFT (1805 active rows with source breakdown) + 12 CONFLICT tag-clusters (`project:infra` = 1249 rows, `project:ci` = 1161, `project:repo` = 1093, etc.).
- Chris's cap drift is still 1805 rows — ongoing bypass CLOSED; historical reconciliation via `memory_hygiene_audit --apply` with tuned thresholds (defaults produce 0 stale for Chris).

**HEAD at close:** `95d3cdc65` (PR3633 merged; docs cascade PR TBD; recycle-all clean at `sha=95d3cdc6534d`).

Full context:
- `docs/handoffs/SESSION_2986_MEMORY_MAXIMALIZATION_PR1.md`
- `docs/handoffs/SESSION_2987_MEMORY_MAXIMALIZATION_PR2.md`

---

## S2988 first-action — WAIT FOR CHRIS

The `ba968ac1` arc is now CLOSED (both PRs shipped, spec DoD satisfied). No queued arc.

**Standard opener:**
1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2987_MEMORY_MAXIMALIZATION_PR2.md` in full — especially §"Post-merge findings" (F-D3-tracker-scope discovery), §"Fold classifications" (6 future_triggers queued), §"Open follow-ups for S2988+".
4. **Optionally probe the shipped state:**
   - `git log --oneline -3` — should show `95d3cdc65` (S2987 PR2) → cascade sha → `857633411` (S2986 PR1).
   - `USE_PGBOUNCER=0 python manage.py test core.tests.test_s2987_memory_hygiene_and_trace core.tests.test_s2986_remember_tool -v 0 --keepdb` — 22/22 pass in ~37s.
   - `python manage.py memory_hygiene_audit --user chris` — cap-drift + conflict report, dry-run only.
5. **Report readiness in one short message and wait.** Something like:
   "Oriented. S2987 closed — Memory PR2 (trace + supersede + hygiene + promotion cap-fix) shipped per spec `ba968ac1` at #3633 `95d3cdc65`. Arc closed (D3+D4 both shipped, D2 descoped as dead code + rolled to F-D2-broad audit spec). 3 Rigby SIGN cycles (T1 REVISE + A2 pass 1 REVISE + A2 pass 2 PROCEED). 6 folds shipped, 6 future_triggers logged including F-D3-tracker-scope (memory_injected event never fires from PA turns — pre-existing OpsRun scope gap, not a PR2 regression). Ready when you have direction: F-D3-tracker-scope wire-up, F-D2-broad non-PA LLM-bypass audit, `memory_hygiene_audit --apply` on your rows, or a fresh arc."

---

## S2988 high-value seeds (Chris picks whether to open)

**F-D3-tracker-scope wire-up (NEW at S2987 close — highest-leverage seed).** Activate the OpsRun tracker for PA turns so the new `memory_injected` trace payload (retrieved_memory_ids + layer) actually lands in the audit stream. Currently `get_active_tracker()` returns None in PA turn context, so the event has fired zero times historically. Substrate is ready; only bridge is dormant. Est ~1 session.

**F-D2-broad audit spec (STILL OPEN from S2986).** Rigby's LLM-bypass sweep found 14+ `enforce_real_ai(` sites + 9 `client.responses.create(` + 80 `client.chat.completions.create(` non-PA callsites. Follow-up audit spec should evaluate user-facing personalization impact of each and decide preflight scope. Est ~1 session for the audit doc; each preflight wire-up is a small follow-up PR.

**Reconcile Chris's 1805 cap-drift via `memory_hygiene_audit --apply` (NEW at S2987 close).** Ongoing bypass is CLOSED; historical rows need tuned thresholds (defaults produce 0 stale for Chris because most rows are recent + importance>=5). Recommended one-off: `--stale-days 30 --stale-importance-lt 10 --apply` (superseding low-signal auto_promotion rows). ~30 min diagnostic + apply.

**Rigby-tool-allowlist expansion (NEW at S2987 close from Rigby self-flag).** Add `OpsRunEvent` + `UserMemoryContext` to `orm_inspect_tool` allowlist so future memory-related live-dispatch smokes can be done from Rigby without dropping to shell. Log to Rigby Tool Gap Ledger. Est ~15-30 min.

**Chris browser visual check on shipped S2985 Canonical Briefing (STILL OPEN from S2985).** ~5 min. Open a canonical summary from Home → Research Arcs → verify Briefing tab defaults, bullets carry Evidence expandables, Refresh bypasses cache, non-canonical docs show NO tab strip.

**Canonical Briefing v2 (STILL OPEN from S2985).** Scope toggle Arc-Folder / All-Docs + default exclude-globs. Pure additive UI change (one dropdown) + one migration (`Document.file_path` index). ~1-2 hr.

**Rigby `claude_code_tool` safeguards (STILL OPEN from S2985 as future_trigger).** Runaway that opened S2985 was Rigby dispatching against a spec that explicitly said "Do not use claude_code_tool." Consider: (a) tool-surface pre-check scanning spec body, (b) opt-in flag on Deliverable, (c) per-session rate-limit / budget cap. Log to Rigby Tool Gap Ledger.

**Chris browser visual check on shipped S2984 arcs section (STILL OPEN from S2984).** ~5 min. Confirm 4-column arcs grid renders; hanging=13 column populated; clicking entrypoint mounts slide-out.

**Systemic auth-XHR treatment (STILL OPEN from S2984 as Fold — future_trigger).** `@login_required` returning 302 HTML on expired-session XHR is repo-wide across all platform endpoints. A JSON-401-on-XHR middleware pattern would be the systemic fix. Not blocking; open when 2nd independent trigger surfaces.

**Live-dispatch smoke on shipped S2982 stage-doc guardrails (STILL OPEN from S2982).** Two probes worth ~15 min: (a) trigger stage-doc generation from any of the 8 callsites and confirm `AgentExecution` row exists; (b) delete initiative between enqueue and task pickup, confirm `mark_task_outcome` transitions to `failed`.

**Exercise PLAYBOOK-7.7.4 against a sibling repo (STILL OPEN from S2981).** Dry-run `context-kit adopt` against `mentorforge` or `character-os`. Validates the adapter contract in reality.

**Browser UX smoke on shipped S2980 Theme Signals UX upgrade (STILL OPEN from S2980).** Load `/workspace?tab=intelligence&sub=theme-signals`. Verify colored Action chips + `All | Build-only` toggle + evidence multi-source rows.

**Phase B Theme Signals — "Why now" LLM summarizer (STILL OPEN from S2978).** Replace deterministic template with LLM-generated 1-2 sentence summary. Cache per cluster. ~1 session.

**Phase B Theme Signals — who-benefits/who-loses (STILL OPEN from S2978).** Sector map + example tickers for Investable cards. ~1-2 sessions.

**Theme Signals — sub-tab persistence via localStorage (STILL OPEN from S2978).** Trivial (~30 min).

**Rigby memory-store cap investigation (SUBSUMED by S2987 D4 hygiene).** The `memory_hygiene_audit` command answers most of this. Close after Chris runs it.

**Rigby Tool Gap Ledger — Fold D from S2982 (STILL OPEN from S2982).** DB uniqueness constraint on `AgentExecution.celery_task_id`. ~30-60 min.

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

The active PA conversation pin at S2987 close was `pa-478cb62a2f774e57`.
`session_lifecycle close` at S2987 close retires that pin and mints a fresh
one for S2988; wrapper `tools/pa_local.sh` is rewritten atomically. Commit
the wrapper diff in the S2987 close cascade PR per
`feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** If a spec-originated session
in S2988+ skips Phase 3 (T1 SIGN) or Phase 5 (Chris-facing framing) or Phase 7
(A2 SIGN), that is a PLAYBOOK-7.7.1 violation. Abort-early is legal but MUST
be recorded in a handoff. Phase-skipping is NOT legal once the session enters
Phase 6 implement.
