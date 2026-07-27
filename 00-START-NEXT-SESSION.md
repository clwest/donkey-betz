# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2991 CLOSED. Findings-surface v2 items #1 and #5 shipped.

**Two feature PRs merged this session (Flow B — spec-originated engineering work from S2990's v2 list).**

**PR #3647 (`6f9f298b5`) — v2 item #1: additive `close_mode` taxonomy.** Chris + Rigby joint framing agreement (Rigby SIGN caught axis confusion in Claude's original 6-value `status`-replacement proposal via real tool_runs — read model, checked endpoint, confirmed `dismissed` value already exists). Shipped shape is orthogonal: `status` stays lifecycle (`open/fixed/dismissed`), new nullable `close_mode` CharField carries closure mechanism (`fixed_via_pr`, `evidence_delivered`, `deferred_to_arc`, `informational`). Migration 0399 backfills the 3 S2990 canonical rows only — 897 open findings unaffected. Freshness axis (row #3's "stale-corrected") deferred to `resolution_note` until 2nd independent trigger (Rigby zoom-out fold). Serializer surfaces `close_mode`; mark endpoint accepts optional `close_mode` with enum validation. Existing UI + API validators keep working. Rigby A2 SIGN: AGREE-with-concerns (verification surface gate → resolved same session by PR #3648).

**PR #3648 (`7a895c871`) — v2 item #5 scoped: `DocResearchFinding` on `orm_inspect_tool` allowlist.** Same tool-gap blocker hit twice: S2990 close-marking + S2991 close_mode A2 verify. Two triggers in two sessions justify closing. Added to `_MODEL_POLICIES` at `td_handlers_agents.py:868-880` with `expensive_text_fields=(text, resolution_note)`, `sensitive=False`. 8 tests: 3 for close_mode field behavior + 5 for allowlist entry (list_models / describe / filter / count_by / expensive-text-field guardrail). Scope narrowed — the `web_fetch_tool` session-cookies half of the original v2 item #5 deferred as separate arc (bigger design decision, security review needed). Rigby A2 SIGN: AGREE — dogfooded end-to-end (`list_models`, `describe_model`, `filter status=fixed` → 3 rows, `count_by close_mode` → 897 null / 2 evidence_delivered / 1 fixed_via_pr).

**HEAD at close:** `7a895c871` + docs cascade PR (this file + handoff + wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`). Recycle-all clean at `sha=7a895c871a9f` post-PR-#3648.

Full context:
- `docs/handoffs/SESSION_2991_FINDINGS_SURFACE_V2_ITEMS_1_AND_5.md`
- `docs/handoffs/SESSION_2990_FINDINGS_SURFACE_FIRST_REAL_USE_LOOP.md` (prior)

---

## S2992 primary directive — Continue Findings-surface v2 sequence

**With #1 and #5 landed, item #2 (finding-type classifier at ingest) is the natural next opener** — it depends on #1's `close_mode` axis (so classifier output maps cleanly to `evidence_delivered` / `fixed_via_pr` close modes at ingest time) and is unblocked by #5's allowlist entry (so classifier impact can be verified via `count_by(close_mode)` deltas without Claude-side ORM shells).

### Highest-leverage next PR: v2 item #2 — finding-type classifier at ingest

Add `finding_type` column to `DocResearchFinding` + regex classifier at ingest in `index_doc_research_findings`. Regex signals:
- `Cat A boundary observation` + `Chris-D-verdict at S<NNNN> xx99` → `type=decision_evidence`
- `blocks downstream X` + error-at-file-line → `type=executable`
- Default: `type=unknown`

Migration adds `finding_type` column + batch-classifies existing 900 findings. **CRITICAL per Rigby's PR #3648 zoom-out fold: support `--dry-run` mode that reports classification distribution BEFORE writing.** Prevents accidental bulk backfill of all 897 rows if the regex signals turn out mis-tuned.

Estimated ~1-2 sessions. If it fits in one, Chris can pair with v2 item #3 (spec-generator prompt branching on `finding_type` — ~30-60 min).

### Ordered follow-on priorities (dependency-aware, gated behind #1 + #2 + #5)

3. **Fix spec-generator prompt** — branch on `finding_type=decision_evidence` to swap in `evidence_capture` template. Gated behind #2. ~30-60 min.
4. **Staleness detector at ingest** — walk `file:line` + identifier references, verify still-matches at HEAD, tag `staleness=suspected` on mismatch. Batch pass over existing 900 findings after landing. **Also needs `--dry-run` mode per Rigby's fold.** ~1 session.
5. **`web_fetch_tool` session cookies (deferred half of v2 item #5)** — the second half of the original spec; needs security-scoped design (Rigby could otherwise hit any authenticated endpoint). Not blocking; open when Chris signals we need HTTP-shape verification past the ORM boundary.
6. **Rigby-SIGN nudge in UI for `type=decision_evidence` findings** — gated behind #2. ~30 min.
7. **F-A2-equivalent for downstream consumers** — verify consumers referenced in ACs actually exist. ~30-60 min.
8. **Wire-through smoke-check AC for half-wired findings** — auto-add browser-session verification. ~30 min.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read the S2991 handoff in full — especially "v2 gaps surfaced" section for the three new carry-forward folds.
4. Optional pre-response state probes:
   - `git log --oneline -6` — should show docs cascade → `7a895c871` (PR #3648) → `6f9f298b5` (PR #3647) → `847c86c41` (S2990 close) → `6f78b285a` → `808c50603`.
   - Rigby can now query directly: `orm_inspect_tool action=count_by model=DocResearchFinding field=close_mode` should return `{null: 897, evidence_delivered: 2, fixed_via_pr: 1}`.
   - `curl -sS http://localhost:8000/api/schema/ | head -c 200` — S2990 drf-spectacular schema still live.

**Suggested first PR shape for S2992:** #2 (finding-type classifier) with `--dry-run` mode from the outset. Land the classifier + verify via `count_by(finding_type)` distribution BEFORE running the 900-row backfill. Sub-PR sequence: (a) column + classifier + `--dry-run`, (b) 900-row backfill after Rigby A2 verifies the dry-run distribution.

---

## S2992 carry-forward seeds (Chris picks whether to open — not gated on the v2 arc)

### New carry-forward from S2991

- **Dry-run counts pattern for future bulk-write migrations.** Rigby's PR #3648 zoom-out fold explicitly flagged v2 items #2 + #4 as at-risk for accidental bulk backfill of 897 rows. Pattern: `--dry-run` mode that reports distribution BEFORE writes; `--apply` flag required to persist. Codify as a substrate rule if it surfaces on a 2nd bulk-write migration.
- **Contract-lock-in guardrail on `close_mode`.** Now that `close_mode` is in serializer payload, renaming/removing values becomes breaking-change territory. Watch for consumers (frontend, PA tools) that read `close_mode` before any value expansion.
- **Freshness axis 2nd-trigger clause.** Codified twice this session (Rigby SIGN #1 + #2). If any future finding surfaces "stale-corrected" or "needs-reverify" state, add orthogonal `evidence_freshness` field; do NOT expand `close_mode` values.

### Carry-forward from S2989-S2990 (STILL OPEN)

- **`web_fetch_tool` session cookies** — deferred half of v2 item #5 (see #5 in v2 list above). Bigger design change.
- **F-D3-tracker-scope wire-up** — activate OpsRun tracker for PA turns. ~1 session. Highest-leverage backend seed.
- **F-D2-broad LLM-bypass audit spec** — evaluate user-facing personalization impact of each `enforce_real_ai` / `chat.completions` / `responses.create` non-PA callsite. Est ~1 session for the audit doc.
- **Reconcile Chris's 1805 cap-drift via `memory_hygiene_audit --apply`.** ~30 min diagnostic + apply.
- **Canonical Briefing v2 scope toggle.** Arc-Folder / All-Docs + default exclude-globs. ~1-2 hr.
- **Substrate fix for `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`.** ~1 session.
- **Send-to-Rigby follow-ups from S2988 (STILL OPEN).**

### Older carry-forward (STILL OPEN)

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
- **Fold B `future_trigger` from v0.8.0 — fold-authoring evidence-admission helper.** 3-trigger threshold NOT yet met.
- **Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for both v0.9.0 and v0.10.0. ~15 min.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **Spec→ship contract:** PLAYBOOK-7.7.1 (9 phases + abort-early clause). S2991 was Flow B (spec-originated from S2990's v2 list); joint framing → Chris yes/no → execute → A2 SIGN → merge → recycle for both PRs. No phase skipped.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations mandatory for T1/A2). Rigby returned real tool_runs on both framings + both A2 SIGNs. Her T1 DISAGREE on the initial 6-value `status`-replacement proposal was the highest-leverage moment of the session.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3 (plain english; "do we lose anything?" + "is it more work later?"; ≤1 decision). Both PRs surfaced as single yes/nos after Claude+Rigby joint agreement.
- **Cross-repo application:** PLAYBOOK-7.7.4. Not exercised this session.
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` after each merge. Both diffs backend-only, so HEAD-range path-diff detection correctly skipped frontend rebuild.

---

## Wrapper pin note

The active PA conversation pin at S2991 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S2991 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S2991 was Flow B (spec-originated). Joint framing (Claude+Rigby) → Chris yes/no → execute → A2 SIGN → merge → recycle was the shape for both PRs. Rigby's T1 DISAGREE on the initial framing (6-value `status` replacement) is the canonical example this session of PLAYBOOK-7.7.2 SIGN discipline preventing a wrong-shape ship — worth referencing in future framings when the proposal feels "obviously right."
