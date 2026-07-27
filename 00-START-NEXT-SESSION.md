# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2992 CLOSED. Findings-surface v2 item #2 shipped end-to-end.

**Two feature PRs merged this session (Flow B — spec-originated engineering work from S2991's v2 list).**

**PR #3650 (`5f4652f8d`) — v2 item #2 PR (a): additive `finding_type` taxonomy + regex classifier at ingest.** Claude ran ORM-direct signal validation on the 900-row corpus BEFORE framing (spec's literal `"blocks downstream X"` had 0 matches). Rigby T1 SIGN sampled 10 real rows via `orm_inspect_tool` and flagged that plainly actionable findings without `.py:line` anchors were collapsing into `unknown` — widened `executable` regex to include imperative verbs (`rename|delete|remove|add|implement|wire|fix|refactor|migrate|bump|pin|extract|split|merge|backfill|deprecate`) before code. Shipped shape: `finding_type` = classification axis orthogonal to `status` (lifecycle) and `close_mode` (closure mechanism); 3 values (`decision_evidence` / `executable` / `unknown`); default `unknown`; `db_index=True`. Migration 0400 schema-only (default auto-populates 900 rows). `--reclassify-existing` command mode defaults to dry-run (`--apply` required to persist) per PR #3648 zoom-out fold. Serializer + list-endpoint filter surface `finding_type`. 21 tests. Rigby A2 SIGN: AGREE (real tool_runs: `describe_model` + `count_by` + 10-row sample; 8/10 gut-match with 2 acceptable misses noted for future signal tweak).

**PR #3651 (`ab21d7a88`) — v2 item #2 PR (b): backfill on 900-row corpus.** Data migration 0401 re-runs `_classify_finding_type` over every existing row via `apps.get_model(...).iterator(chunk_size=500)`; only flips rows whose classifier output differs. Reverse resets non-unknown rows to `unknown` (pragmatic — pre-migration state was uniformly `unknown`). Post-migration distribution matches pre-merge dry-run exactly: **139 decision_evidence (15.4%) / 138 executable (15.3%) / 623 unknown (69.2%) / 900 total**. Rigby final verify confirmed via `count_by(finding_type)`.

**HEAD at close:** `ab21d7a88` + docs cascade PR (this file + handoff + wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`). Recycle-all clean at `sha=ab21d7a8846b` post-PR-#3651.

Full context:
- `docs/handoffs/SESSION_2992_FINDING_TYPE_CLASSIFIER_V2_ITEM_2.md`
- `docs/handoffs/SESSION_2991_FINDINGS_SURFACE_V2_ITEMS_1_AND_5.md` (prior)

---

## S2993 primary directive — Continue Findings-surface v2 sequence

**With #1 (close_mode), #2 (finding_type classifier), and #5 (orm_inspect_tool allowlist) shipped, item #3 (spec-generator prompt branching on finding_type) is the natural next opener** — it's the smallest remaining item (~30–60 min per S2992 handoff estimate), directly consumes #2's `finding_type` axis, and unblocks Rigby-SIGN UX improvements downstream.

### Highest-leverage next PR: v2 item #3 — spec-generator prompt branching on finding_type

The `send-to-rigby` endpoint at `core/views_doc_research_findings.py:194` currently routes every finding through `generate_spec_body` with the same template regardless of shape. Branch on `finding_type`:
- **`decision_evidence`** — swap template to `evidence_capture` (or equivalent). These are decision-record findings; the spec output should capture the boundary/verdict, not propose new engineering work.
- **`executable`** — keep existing engineering-spec template. These are ready-to-implement action items.
- **`unknown`** — keep existing template (default).

Look at `core/services/briefing_spec_generator.generate_spec_body` signature + templates before deciding whether to add a new template file or parameterize the existing one.

**Sub-PR shape:** likely a single PR (~30–60 min). Includes 3–5 tests verifying template selection per `finding_type`. Rigby A2 SIGN post-merge: send 3 real findings via `send-to-rigby` (one per class) and verify the deliverable shape differs.

### Ordered follow-on priorities (dependency-aware)

4. **Staleness detector at ingest** — walk `file:line` + identifier references, verify still-matches at HEAD, tag `staleness=suspected` on mismatch. Batch pass over existing 900 findings after landing. **Also needs `--dry-run` mode per PR #3648 zoom-out fold.** ~1 session.
5. **`web_fetch_tool` session cookies (deferred half of v2 item #5)** — bigger design change; security review needed. Not blocking; open when Chris signals we need HTTP-shape verification past the ORM boundary.
6. **Rigby-SIGN nudge in UI for `finding_type=decision_evidence`** — surface a "verify evidence still holds" nudge. Now unblocked by #2. ~30 min.
7. **F-A2-equivalent for downstream consumers** — verify consumers referenced in ACs actually exist. ~30–60 min.
8. **Wire-through smoke-check AC for half-wired findings** — auto-add browser-session verification. ~30 min.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read the S2992 handoff in full — especially "v2 gaps surfaced" section for the two carry-forward signal-tweak candidates (`boundary drift`, `VERIFIED at HEAD`).
4. Optional pre-response state probes:
   - `git log --oneline -6` — should show docs cascade → `ab21d7a88` (PR #3651) → `5f4652f8d` (PR #3650) → `8debe2e5e` (S2991 close) → `7a895c871` → `6f9f298b5`.
   - Rigby can now query directly: `orm_inspect_tool action=count_by model=DocResearchFinding field=finding_type` should return `{unknown: 623, decision_evidence: 139, executable: 138}`.
   - `curl -sS http://localhost:8000/api/schema/ | head -c 200` — drf-spectacular schema still live.

**Suggested first PR shape for S2993:** #3 (prompt branching) as a single PR. Read the existing `generate_spec_body` first to decide template-file-per-class vs branching-inside-existing-template. Route framing through Rigby before code.

---

## S2993 carry-forward seeds (Chris picks whether to open — not gated on the v2 arc)

### New carry-forward from S2992

- **Signal-tweak follow-up for `finding_type` classifier.** Two acceptable-misses surfaced during Rigby A2 SIGN: (1) `boundary drift` phrasing lands in `unknown` (regex expects `boundary (observation|violation)`); (2) `VERIFIED at HEAD` evidence records land in `executable` because they cite `file:line`. Neither blocking. Combine into a single signal-tweak PR if a 2nd independent trigger surfaces.
- **Data-migration-vs-management-command pattern.** PR #3651 chose data migration for cross-env reproducibility (matches migration 0399 backfill pattern). Alternative was live `--apply` invocation. If future one-shot backfills recur, codify the "data migration when reproducibility matters; --apply for signal iteration" split.

### Carry-forward from S2991 (STILL OPEN)

- **Dry-run counts pattern for future bulk-write migrations.** PR #3651 followed this exactly (dry-run default; `--apply` required). If pattern surfaces on a 3rd bulk-write migration, codify as a substrate rule.
- **Contract-lock-in guardrail on `close_mode` and now `finding_type`.** Both are in serializer payload — renaming/removing values becomes breaking-change territory. Watch for frontend/PA consumers that read either.
- **Freshness axis 2nd-trigger clause.** Codified S2991; still no 2nd trigger. If any future finding surfaces "stale-corrected" state, add orthogonal `evidence_freshness` field; do NOT expand `close_mode` values.

### Carry-forward from S2989-S2990 (STILL OPEN)

- **`web_fetch_tool` session cookies** — deferred half of v2 item #5 (see #5 in v2 list above).
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
- **Spec→ship contract:** PLAYBOOK-7.7.1 (9 phases + abort-early clause). S2992 was Flow B (spec-originated from S2991's v2 list); joint framing → Chris yes/no → execute → A2 SIGN → merge → recycle for both PRs. No phase skipped.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations mandatory for T1/A2). Rigby returned real `orm_inspect_tool` tool_runs on T1 framing (10-row corpus sample), A2 verify (describe_model + count_by + 10-row classification cross-check), AND final post-PR-b verify. Zero rubber-stamping across three SIGN cycles.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3 (plain english; "do we lose anything?" + "is it more work later?"; ≤1 decision). Chris ratification was one yes/no after Claude+Rigby joint agreement.
- **Cross-repo application:** PLAYBOOK-7.7.4. Not exercised this session.
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` after each merge. Both diffs backend-only, so HEAD-range path-diff detection correctly skipped frontend rebuild.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — Claude ran ORM-direct signal validation BEFORE framing (spec's literal `"blocks downstream X"` had 0 matches). Prevented shipping a classifier that would over-collapse.

---

## Wrapper pin note

The active PA conversation pin at S2992 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S2992 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S2992 was Flow B (spec-originated). Joint framing (Claude+Rigby) → Chris yes/no → execute → A2 SIGN → merge → recycle was the shape for both PRs. Rigby's T1 SIGN fold (widen `executable` regex beyond `.py:line` to include imperative verbs) is the canonical example this session of PLAYBOOK-7.7.2 SIGN discipline preventing a suboptimal ship — worth referencing in future framings when spec signals don't match corpus reality (ORM-direct validation before framing catches this cheaply).
