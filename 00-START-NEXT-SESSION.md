# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2988 CLOSED. Canonical Briefing: bug fix + prompt tightening + Send-to-Rigby all shipped.

**Two feature PRs merged this session:**

**PR #3635 — `8580a67ba` (S2988 bug fix):** Canonical Briefing 500'd on every click since S2985 because `retrieve_scoped_chunks` referenced pgvector column `embedding` instead of the actual field `embedding_vector`. One-string swap + new `CanonicalBriefingRealORMRetrievalTests` seeding a real Document + DocumentEmbedding row + running un-mocked `retrieve_scoped_chunks` so a future field rename fails locally instead of shipping. 16/16 tests pass (was 15). Live-verified against `docs/research/domains/memory/1399_memory_canonical_summary.md`.

**PR #3636 — `81c61c40d` (S2988 usability follow-up after Chris's live browser use):**
- **Prompt tightening** — bullets were 20-30 words with meta-descriptive framing and unexpanded jargon (`Cat D` / `xx99` / `verdict cascade`). Added voice rules to `_build_prompt`: ≤ 20 words, one idea, plain English, expand or drop insider jargon, no stacked sub-clauses, no meta-descriptions. Bumped `PROMPT_VERSION` v1→v2 so cached briefings regenerate. Lowered `DEFAULT_MAX_BULLETS_PER_SECTION` 10→6. Live-verified: PA canonical briefing regenerated with 21 bullets, 0 over the cap.
- **Per-bullet "Send to Rigby" button** — new `POST /api/repo/canonical-briefing/send-to-rigby/` creates a `briefing_action_item` Deliverable in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) with the bullet + citations + source anchor as body content. Uses the same `deliverable_factory.create_deliverable` path Rigby's tool uses; the type is added to `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT` so the row is not diagnostic-flagged. Frontend `SendToRigbyButton` per bullet with idle→sending→sent/error states. Live smoke: 201 with clean deliverable (`diagnostic_status=None`). 21/21 tests pass (+5 from send-to-rigby coverage).

**Session shape (S2988):** Bug-report → diagnosis → PR1 → Chris visual confirm working → Chris usability asks → PR2 → close cascade. Bounded engineering, no Rigby SIGN cycles (per PLAYBOOK-7.7.2, SIGN is for spec-originated implementation; ad-hoc bug fixes + Chris-directed feature extensions with unambiguous design route straight through Claude direct→execute→verify).

**HEAD at close:** `81c61c40d` (PR3636 merged; docs cascade PR TBD; recycle-all clean at `sha=81c61c40d`, frontend `dist/` rebuilt at 10:52 via PLAYBOOK-7.4.4 HEAD-range path diff detection).

Full context:
- `docs/handoffs/SESSION_2988_CANONICAL_BRIEFING_FIX_AND_SEND_TO_RIGBY.md`
- `docs/handoffs/SESSION_2987_MEMORY_MAXIMALIZATION_PR2.md` (prior)

---

## S2989 first-action — WAIT FOR CHRIS VISUAL VERIFY

Chris visual confirmation of #3636 is still open at session close — the feature has been live-verified at service + endpoint layers and the frontend rebuild landed clean, but Chris will test the UI after this cascade. First move:

**Standard opener:**
1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2988_CANONICAL_BRIEFING_FIX_AND_SEND_TO_RIGBY.md` in full — especially §"Post-merge findings" (Chris visual verify pending) and §"Open follow-ups for S2989+".
4. **Ask Chris one thing:** how did the browser test go?
   - **If passed** — session opens with no queued arc. Top seeds (unchanged from S2987): F-D3-tracker-scope wire-up (highest leverage), F-D2-broad LLM-bypass audit, `memory_hygiene_audit --apply` on the 1805-row cap-drift, or fresh net-new engineering candidate.
   - **If issues surfaced** — triage the specific issue and route through Chris-directs / Claude-executes / Claude-verifies. Likely candidates: bullet formatting still off (further prompt iteration), Send-to-Rigby button click regression (check dist/ freshness + endpoint auth), deliverable not appearing in workspace UI (check `diagnostic_status` + workspace routing).
5. **Optionally probe the shipped state before Chris responds:**
   - `git log --oneline -3` — should show docs cascade sha → `81c61c40d` (S2988 PR2) → `8580a67ba` (S2988 PR1).
   - `USE_PGBOUNCER=0 python manage.py test core.tests.test_canonical_briefing -v 0 --keepdb` — 21/21 pass in ~1s.
   - Live endpoint smoke via `Client(HTTP_HOST='127.0.0.1:8000')` post-`force_login(superuser)` → POST `/api/repo/canonical-briefing/send-to-rigby/` with a real bullet → confirm 201 + `deliverable_type=briefing_action_item` + `diagnostic_status=None`.

---

## S2989 high-value seeds (Chris picks whether to open)

**F-D3-tracker-scope wire-up (NEW at S2987 close — highest-leverage seed, STILL OPEN).** Activate the OpsRun tracker for PA turns so the new `memory_injected` trace payload (retrieved_memory_ids + layer) actually lands in the audit stream. Currently `get_active_tracker()` returns None in PA turn context, so the event has fired zero times historically. Substrate is ready; only bridge is dormant. Est ~1 session.

**F-D2-broad audit spec (STILL OPEN from S2986).** Rigby's LLM-bypass sweep found 14+ `enforce_real_ai(` sites + 9 `client.responses.create(` + 80 `client.chat.completions.create(` non-PA callsites. Follow-up audit spec should evaluate user-facing personalization impact of each and decide preflight scope. Est ~1 session for the audit doc; each preflight wire-up is a small follow-up PR.

**Reconcile Chris's 1805 cap-drift via `memory_hygiene_audit --apply` (STILL OPEN from S2987).** Ongoing bypass is CLOSED; historical rows need tuned thresholds (defaults produce 0 stale for Chris because most rows are recent + importance>=5). Recommended one-off: `--stale-days 30 --stale-importance-lt 10 --apply` (superseding low-signal auto_promotion rows). ~30 min diagnostic + apply.

**Canonical Briefing v2 (STILL OPEN from S2985 — becoming more valuable now that briefings actually render).** Scope toggle Arc-Folder / All-Docs + default exclude-globs. Pure additive UI change (one dropdown) + one migration (`Document.file_path` index). ~1-2 hr.

**Send-to-Rigby follow-ups (NEW at S2988 close — only if Chris asks).** Natural v2 iterations: per-section "Send all" button; workspace routing inference from arc slug (e.g. `pa/` → PA-specific workspace); LLM-mediated deliverable creation (currently direct-ORM for cost/determinism; future v2 could route through Rigby's turn loop to exercise the natural-language surface).

**Substrate fix candidate for `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT` (STILL OPEN from `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`).** S2988 added `'briefing_action_item'` to the exempt list — the systemic fix (default `deliverable_type` from `category` + skip missing_initiative_id marker for governance-scoped categories) is still open. Each new caller-facing deliverable type will hit this until the substrate is fixed. Low priority; ~1 session.

**Rigby-tool-allowlist expansion (STILL OPEN from S2987 close).** Add `OpsRunEvent` + `UserMemoryContext` to `orm_inspect_tool` allowlist so future memory-related live-dispatch smokes can be done from Rigby without dropping to shell. Log to Rigby Tool Gap Ledger. Est ~15-30 min.

**Chris browser visual check on shipped S2985 Canonical Briefing tab strip / Refresh behavior (STILL OPEN from S2985).** ~5 min. Confirm Briefing tab defaults on canonical summaries, Refresh bypasses cache, non-canonical docs show NO tab strip.

**Rigby `claude_code_tool` safeguards (STILL OPEN from S2985 as future_trigger).** Runaway that opened S2985 was Rigby dispatching against a spec that explicitly said "Do not use claude_code_tool." Consider: (a) tool-surface pre-check scanning spec body, (b) opt-in flag on Deliverable, (c) per-session rate-limit / budget cap. Log to Rigby Tool Gap Ledger.

**Chris browser visual check on shipped S2984 arcs section (STILL OPEN from S2984).** ~5 min. Confirm 4-column arcs grid renders; hanging=13 column populated; clicking entrypoint mounts slide-out.

**Systemic auth-XHR treatment (STILL OPEN from S2984 as Fold — future_trigger).** `@login_required` returning 302 HTML on expired-session XHR is repo-wide across all platform endpoints. A JSON-401-on-XHR middleware pattern would be the systemic fix. Not blocking; open when 2nd independent trigger surfaces.

**Live-dispatch smoke on shipped S2982 stage-doc guardrails (STILL OPEN from S2982).** Two probes worth ~15 min: (a) trigger stage-doc generation from any of the 8 callsites and confirm `AgentExecution` row exists; (b) delete initiative between enqueue and task pickup, confirm `mark_task_outcome` transitions to `failed`.

**Exercise PLAYBOOK-7.7.4 against a sibling repo (STILL OPEN from S2981).** Dry-run `context-kit adopt` against `mentorforge` or `character-os`. Validates the adapter contract in reality.

**Browser UX smoke on shipped S2980 Theme Signals UX upgrade (STILL OPEN from S2980).** Load `/workspace?tab=intelligence&sub=theme-signals`. Verify colored Action chips + `All | Build-only` toggle + evidence multi-source rows.

**Phase B Theme Signals — "Why now" LLM summarizer (STILL OPEN from S2978).** Replace deterministic template with LLM-generated 1-2 sentence summary. Cache per cluster. ~1 session.

**Phase B Theme Signals — who-benefits/who-loses (STILL OPEN from S2978).** Sector map + example tickers for Investable cards. ~1-2 sessions.

**Theme Signals — sub-tab persistence via localStorage (STILL OPEN from S2978).** Trivial (~30 min).

**Rigby Tool Gap Ledger — Fold D from S2982 (STILL OPEN from S2982).** DB uniqueness constraint on `AgentExecution.celery_task_id`. ~30-60 min.

**Fold B `future_trigger` from v0.8.0 — fold-authoring evidence-admission helper.** 3-trigger threshold NOT yet met. Wait for signal.

**Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for both v0.9.0 and v0.10.0. ~15 min.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (post-v0.10.0 refresh). Points at Playbook v0.10.0 + version ancestry + workspace ratification records.
- **Spec→ship contract:** PLAYBOOK-7.7.1 (9 phases + abort-early clause). Session-shape contract for spec-originated implementation.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations mandatory for T1/A2). If Rigby returns empty tool_runs + generic AGREE, RE-ISSUE the routing.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3 (plain english; "do we lose anything?" + "is it more work later?" before yes/no; ≤1 decision). Applied twice this session for the density + Send-to-Rigby asks.
- **Cross-repo application:** PLAYBOOK-7.7.4 (Layer 1 context-kit primitives / Layer 2 repo-local surfaces; tag every SIGN finding with verification surface).
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` (NOT `make celery-recycle`) for any PR touching `frontend/**`. Recycle-all uses HEAD-range diff detection — only fires frontend rebuild if changes are in HEAD range, so commit-then-recycle order matters. Confirmed working this session — frontend rebuilt at 10:52 after PR #3636 merge.
- **Staged codification for enforcement:** PLAYBOOK-7.5.1.

---

## Wrapper pin note

The active PA conversation pin at S2988 close will be minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S2988 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** If a spec-originated session in S2989+ skips Phase 3 (T1 SIGN) or Phase 5 (Chris-facing framing) or Phase 7 (A2 SIGN), that is a PLAYBOOK-7.7.1 violation. Abort-early is legal but MUST be recorded in a handoff. Phase-skipping is NOT legal once the session enters Phase 6 implement. S2988 was NOT a spec-originated session (bug report → follow-up), so straight-through Claude direct→execute→verify was legitimate.
