# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2985 CLOSED. Canonical Briefing v1 shipped per spec `6f6c4122-…`.

**One PR merged into main this session:**

**PR #3629 — `b281a0f03`:** New backend endpoint `POST /api/repo/canonical-briefing/` performs scope-filtered pgvector retrieval over `content.DocumentEmbedding` + one LLM call (structured JSON) producing five section cards (TL;DR / Decisions / State / Risks / Next Actions) with bullet-level citations. `DocumentViewer.tsx` gains a `Briefing | Raw` tab strip gated by `BRIEFING_ELIGIBLE_PATTERN` — only canonical summary docs under `docs/research/domains/**/*canonical_summary*.md` see the strip. Non-canonical docs unchanged. Bullets whose citation_keys don't map to a retrieved chunk collapse to "Insufficient support in canonical docs" (Z1 no-hallucination invariant, server-enforced). Redis singleton_lock prevents stampede on cold cache; 15-min TTL keyed by anchor mtime + prompt_version.

**Session shape:** PLAYBOOK-7.7.1 spec→ship, all 9 phases walked. 3 Rigby SIGN cycles (T1 pass 1 REVISE / T1 pass 2 PROCEED after 4 refinements folded / A2 PROCEED-TO-MERGE with 1 same-PR fold shipped). 8 same_pr_mitigatable folds all shipped (Z1/Z2/Z3 invariants + D1/D2/D3 refinements + ZO1 malformed-JSON flag). 2 future_trigger folds documented (C4/ZO3 file_path index + ZO2 lock TTL).

**Session opened with an incident:** Rigby had dispatched a runaway `claude_code_tool` job for the same spec (PID `55024`); it was killed before it did filesystem damage. Spec body explicitly said "Do not use claude_code_tool." Watch for a future_trigger to safeguard against repeat.

**Chris still owes:** browser visual check at `http://127.0.0.1:8000/workspace` → Home tab → click a hanging arc entrypoint that lands on a canonical summary → verify (a) Briefing tab defaults, (b) bullets render with Evidence expandables, (c) Refresh forces cache bypass, (d) non-canonical docs (open from Knowledge tab) show NO Briefing tab.

**HEAD at close:** `b281a0f03` (PR3629 merged; docs cascade PR TBD; recycle-all clean at `sha=b281a0f03762`).

Full context: `docs/handoffs/SESSION_2985_CANONICAL_BRIEFING_V1.md`.

---

## S2986 first-action — WAIT FOR CHRIS

The reframe holds for the **sixteenth walk**. Same open shape:

1. Run `context-kit orient` (auto-injected at session start; read the output).
2. Absorb this file + MEMORY.md + CLAUDE.md (auto-injected).
3. Read `docs/handoffs/SESSION_2985_CANONICAL_BRIEFING_V1.md` in full — especially §"Rigby cycle discipline", §"Fold classifications", §"Open follow-ups for S2986+".
4. **Optionally probe the shipped state:**
   - `git log --oneline -3` — should show `b281a0f03` (Canonical Briefing v1) → cascade sha → `9235cb7de` (S2984 PR4).
   - `USE_PGBOUNCER=0 python manage.py test core.tests.test_canonical_briefing -v 0 --keepdb` — 15/15 pass in <0.5s.
   - `curl -sf http://127.0.0.1:8000/api/repo/canonical-briefing/ -X POST -H 'Content-Type: application/json' -b cookies.txt -d '{"anchor_path": "docs/research/domains/docs_content_audit/2899_docs_content_canonical_summary.md"}' | jq '.sections | length'` — should return 5.
5. **Report readiness in one short message and wait.** Something like:
   "Oriented. S2985 closed — Canonical Briefing v1 (POST /api/repo/canonical-briefing/ + DocumentViewer Briefing tab) shipped per spec `6f6c4122-…` at #3629 `b281a0f03`. Rigby cycles: 3 SIGN passes (T1×2 + A2), tool-grounded citations throughout, 8 folds shipped same-PR / 2 documented as v2 future_trigger. Session opened with the runaway claude_code_tool kill — flagged for future safeguards. Ready when you have direction: browser visual check on S2985, browser visual check on S2984 carryovers, next arc, or S2986 seed."
6. **Do NOT propose engineering work. Do NOT dispatch anything to Rigby proactively.** Chris opens Rigby chat first; you wait for the handoff.

**When Chris hands you a Deliverable ID / title / spec pointer for a new arc:** the spec→ship contract is constitutional (PLAYBOOK-7.7.1). Follow Phases 1-9 by name. Pre-code sampling BEFORE T1 SIGN. T1 SIGN with tool-grounded file/line verify instructions per PLAYBOOK-7.7.2. Phase 5 Chris-facing framing per PLAYBOOK-7.7.3 ("do we lose anything?" + "is it more work later?" + ≤1 decision). A2 SIGN post-implementation. Ship via `gh pr merge --admin --squash --delete-branch`. **`make recycle-all` (NOT `make celery-recycle`) when frontend is touched** (per S2978 refinement to PLAYBOOK-7.4.4); recycle waiver per PLAYBOOK-7.4.4 diff-based clause when docs-only. Rigby verifies from her tool surface. Report three-part summary to Chris.

**If a spec body says "Do not use claude_code_tool" (as this session's did):** the manual Claude Code terminal dispatch IS the correct route. Never call `claude_code_tool` from Rigby against such a spec. This session opened with exactly that violation — Rigby dispatched the spec via `claude_code_tool` anyway, running unsupervised with `--dangerously-skip-permissions --max-turns 50`; Chris caught it seconds before real damage. Kill any live claude_code_tool process by PID before doing anything else, then take the spec via manual Claude Code.

**For cross-repo work** (any repo other than unified-donkey-betz): PLAYBOOK-7.7.4 applies. Phase 0 MUST detect context-kit substrate — run `context-kit orient` + confirm `.context-kit/verify.yaml`. If missing, first action = `context-kit adopt` (dry-run → review → --write). Tag every SIGN finding with its verification surface (Layer 1 / Layer 2 / Claude-local-shell).

---

## S2986 high-value seeds (Chris picks whether to open)

**Chris browser visual check on shipped S2985 Canonical Briefing (NEW at S2985).** ~5 min. Open a canonical summary from Home → Research Arcs → verify Briefing tab defaults, bullets carry Evidence expandables, Refresh bypasses cache, non-canonical docs show NO tab strip.

**Canonical Briefing v2 (STILL OPEN from S2985).** Scope toggle Arc-Folder / All-Docs + default exclude-globs. Pure additive UI change (one dropdown) + one migration (`Document.file_path` index). ~1-2 hr.

**Rigby `claude_code_tool` safeguards (NEW at S2985 as future_trigger).** The runaway that opened S2985 was Rigby dispatching against a spec that explicitly said "Do not use claude_code_tool." Consider: (a) tool-surface pre-check scanning spec body for that literal string, (b) opt-in flag on Deliverable, (c) per-session rate-limit / budget cap on `claude_code_tool` invocations. Log to Rigby Tool Gap Ledger.

**Chris browser visual check on shipped S2984 arcs section (STILL OPEN from S2984).** ~5 min. Confirm 4-column arcs grid renders; hanging=13 column populated; clicking entrypoint mounts slide-out.

**Systemic auth-XHR treatment (STILL OPEN from S2984 as Fold — future_trigger).** `@login_required` returning 302 HTML on expired-session XHR is repo-wide across all platform endpoints. A JSON-401-on-XHR middleware pattern would be the systemic fix. Not blocking; open when 2nd independent trigger surfaces.

**Live-dispatch smoke on shipped S2982 stage-doc guardrails (STILL OPEN from S2982).** Two probes worth ~15 min: (a) trigger stage-doc generation from any of the 8 callsites and confirm `AgentExecution` row exists; (b) delete initiative between enqueue and task pickup, confirm `mark_task_outcome` transitions to `failed`.

**Exercise PLAYBOOK-7.7.4 against a sibling repo (STILL OPEN from S2981).** Dry-run `context-kit adopt` against `mentorforge` or `character-os`. Validates the adapter contract in reality.

**Browser UX smoke on shipped S2980 Theme Signals UX upgrade (STILL OPEN from S2980).** Load `/workspace?tab=intelligence&sub=theme-signals`. Verify colored Action chips + `All | Build-only` toggle + evidence multi-source rows.

**Phase B Theme Signals — "Why now" LLM summarizer (STILL OPEN from S2978).** Replace deterministic template with LLM-generated 1-2 sentence summary. Cache per cluster. ~1 session.

**Phase B Theme Signals — who-benefits/who-loses (STILL OPEN from S2978).** Sector map + example tickers for Investable cards. ~1-2 sessions.

**Theme Signals — sub-tab persistence via localStorage (STILL OPEN from S2978).** Trivial (~30 min).

**Rigby memory-store cap investigation (STILL OPEN from S2979).** ~30 min diagnostic.

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

The active PA conversation pin at S2985 close was `pa-2bdac7a36a2748c6`.
`session_lifecycle close` at S2985 close retires that pin and mints a fresh
one for S2986; wrapper `tools/pa_local.sh` is rewritten atomically. Commit
the wrapper diff in the S2985 close cascade PR per
`feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** If a spec-originated session
in S2986+ skips Phase 3 (T1 SIGN) or Phase 5 (Chris-facing framing) or Phase 7
(A2 SIGN), that is a PLAYBOOK-7.7.1 violation. Abort-early is legal but MUST
be recorded in a handoff. Phase-skipping is NOT legal once the session enters
Phase 6 implement.
