# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2986 CLOSED. Memory System PR1 shipped per spec `ba968ac1`.

**One PR merged into main this session:**

**PR #3631 — `857633411`:** `remember_tool.save` now reliably persists memories with full audit-of-what-happened. Save-return includes `status` (`created` | `duplicate_updated`), `truncated`, `original_len` fields; cap-hit migrated to S2879 `_handler_error('save', 'cap_hit', …)` shape; pre-parse oversize gate at `unified_pa_entrypoint.py:2232-2272` rejects `remember_tool.save` calls with raw args >3000 chars BEFORE `json.loads` risks mid-stream truncation (the exact failure mode called out in the spec); PA prompt header renamed from "YOUR MEMORY (things the user asked you to remember):" → "PERSISTENT USER CONTEXT (use only if relevant; do not mention unless asked):" to reduce parroting; 10 new happy-path tests fill S2886 coverage gap; operator doc at `docs/topics/memory-system.md` names the three memory layers.

**Session shape:** PLAYBOOK-7.7.1 spec→ship, all 9 phases walked. 4 Rigby SIGN cycles (T1 pass 1 REVISE / T1 pass 2 REVISE / T1 pass 3 PROCEED / A2 PROCEED-TO-MERGE). 7 same-PR folds shipped (F-D1a/b/c/d/e + F-D5a + F-Z1). 4 future_triggers logged (F-ZO2 relevance filter, F-ZO3 structured citations, F-D2-broad non-PA sweep, F-D4-cap-drift discovered at post-merge smoke).

**Post-merge discovery:** Live-dispatch smoke revealed Chris's user has **1803 `UserMemoryContext` rows against a 200 cap** — auto-accumulation of "Event: Deploying" / "Version Build" content from some non-`remember_tool` code path. Cap-hit envelope is working correctly (S2879 shape live-verified); the 1803 count reveals a hidden accumulation that directly validates D4 hygiene urgency. Investigating + reconciling is in-scope for PR2's `memory_hygiene_audit` command.

**HEAD at close:** `857633411` (PR3631 merged; docs cascade PR TBD; recycle-all clean at `sha=85763341193d`).

Full context: `docs/handoffs/SESSION_2986_MEMORY_MAXIMALIZATION_PR1.md`.

---

## S2987 first-action — PR2 for spec `ba968ac1` (Memory Maximalization PR2)

**Chris ratified the 2-PR split at S2986 Phase 5.** PR2 scope (already agreed with Rigby via T1 SIGN passes):

**D3 — MemoryUtilizationTrace:**
- New event/log with layer discriminator: `user_memory_context` | `user_agent_learning` | `conversation_memory`.
- Payload: `retrieved_memory_ids`, `injected_chars`, `declared_used_memory_ids` (MVP = LLM self-report via prompt convention, structured-citation upgrade is future_trigger).
- Keyed by `trace_id`. Chris can ask "did memory influence this?" and get evidence.

**D4 — Memory hygiene:**
- Migration adds `UserMemoryContext.is_active`, `superseded_by` (FK), `superseded_at` fields. Supersede semantics = write new row + mark old inactive + link. NEVER DELETE.
- `memory_hygiene_audit` management command surfaces stale candidates (age >90d + low importance, low `accessed_count`, etc.) and likely conflicts (same tag + contradictory content).
- **New at S2986 close:** command MUST also surface the 1803-vs-200 cap drift on Chris's user + identify which non-`remember_tool` code path is auto-writing "Event: Deploying" / "Version Build" content.

**D2 (narrow MVP) — non-PA preflight:**
- Wire `MemoryContextService.get_prompt_context(user)` into `ProjectBuilderOrchestrator._build_project_with_llm_only()` at `core/project_builder_orchestrator.py:432+`.
- Only this single confirmed LLM-driven non-PA site. Rigby's sweep found dozens more (`personal_ai_assistant_enhanced.py`, `opportunity_ai_analyzer.py`, `channel_orchestrator.py`, `conversation_orchestrator.py`, etc.) — those go to a follow-up audit spec, not PR2.

**Follow contract**: PLAYBOOK-7.7.1 Phases 1-9. Pre-code sampling BEFORE T1 SIGN. T1 SIGN with tool-grounded verify per PLAYBOOK-7.7.2. Phase 5 Chris framing per PLAYBOOK-7.7.3 IF a decision surfaces (may not — scope is already agreed). A2 SIGN post-implementation. Ship via `gh pr merge --admin --squash --delete-branch`. `make recycle-all` waiver-check first (backend-only PR expected → `celery-recycle` sufficient, but `recycle-all` is safe default with diff detection).

**Standard opener:**
1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2986_MEMORY_MAXIMALIZATION_PR1.md` in full — especially §"Post-merge findings" (the 1803-vs-200 cap drift), §"Fold classifications" (what's queued vs shipped), §"Rigby cycle discipline" (what T1 pass 1/2/3 refined).
4. **Optionally probe the shipped state:**
   - `git log --oneline -3` — should show `857633411` (S2986 PR1) → cascade sha → `b281a0f03` (S2985).
   - `USE_PGBOUNCER=0 python manage.py test core.tests.test_s2986_remember_tool -v 0 --keepdb` — 10/10 pass.
5. **Report readiness in one short message and wait.** Something like:
   "Oriented. S2986 closed — Memory PR1 (`remember_tool.save` reliability + operator doc + PA header rename) shipped per spec `ba968ac1` at #3631 `857633411`. 4 Rigby SIGN cycles (T1×3 + A2), 7 folds shipped same-PR, 4 future_triggers logged including new F-D4-cap-drift from post-merge smoke (Chris at 1803 rows vs 200 cap). Ready when you have direction: open S2987 PR2 for spec `ba968ac1` (trace + hygiene + narrow preflight — Chris ratified scope at S2986 Phase 5), or something else."

---

## S2987 high-value seeds (Chris picks whether to open)

**PR2 for spec `ba968ac1` (NEW at S2986, primary queued arc).** Chris already ratified scope: D3 utilization trace + D4 hygiene + narrow D2 preflight. Est ~1-2 sessions. See §"S2987 first-action" above for concrete file targets.

**Chris browser visual check on shipped S2985 Canonical Briefing (STILL OPEN from S2985).** ~5 min. Open a canonical summary from Home → Research Arcs → verify Briefing tab defaults, bullets carry Evidence expandables, Refresh bypasses cache, non-canonical docs show NO tab strip.

**Broader D2 audit spec for non-PA LLM-bypass sites (NEW at S2986 as future_trigger).** Rigby's sweep found 14 `enforce_real_ai(` + 9 `client.responses.create(` + 80 `client.chat.completions.create(` non-PA callsites. Follow-up spec should audit user-facing personalization impact of each. Log to Rigby Tool Gap Ledger. Est ~1 session for the audit doc; each preflight wire-up is a small follow-up PR.

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

**Rigby memory-store cap investigation (STILL OPEN from S2979 — related to S2986 F-D4-cap-drift discovery).** ~30 min diagnostic. Overlaps with PR2 hygiene work; may be subsumed.

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

The active PA conversation pin at S2986 close was `pa-99aa806c19714720`.
`session_lifecycle close` at S2986 close retires that pin and mints a fresh
one for S2987; wrapper `tools/pa_local.sh` is rewritten atomically. Commit
the wrapper diff in the S2986 close cascade PR per
`feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** If a spec-originated session
in S2987+ skips Phase 3 (T1 SIGN) or Phase 5 (Chris-facing framing) or Phase 7
(A2 SIGN), that is a PLAYBOOK-7.7.1 violation. Abort-early is legal but MUST
be recorded in a handoff. Phase-skipping is NOT legal once the session enters
Phase 6 implement.
