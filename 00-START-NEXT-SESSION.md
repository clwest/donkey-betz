# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2993 CLOSED. Findings-surface v2 item #3 shipped end-to-end.

**One feature PR merged this session (Flow B — spec-originated engineering work from S2991's v2 list).**

**PR #3653 (`f533cacf8`) — v2 item #3: spec-generator prompt branches on `finding_type`.** `core/services/briefing_spec_generator.generate_spec_body` now accepts optional `finding_type` kwarg. `decision_evidence` findings get an evidence-capture prompt (records boundary/verdict; acceptance criteria become verification steps). `executable` / `unknown` / `None` / unrecognized values fall through to the pre-S2993 engineering-spec prompt. Same JSON schema + same markdown section headers so downstream renderers/consumers stay identical. Send-to-rigby view forwards `finding.finding_type`. Metadata extras carry `spec_prompt_shape` + `finding_type_used` for audit. Fail-open placeholder copy diverges per shape (evidence findings don't nudge to "author acceptance criteria"). 19 new tests + 44 pre-existing tests green. Rigby T1 SIGN sampled 3 real `decision_evidence` corpus rows via `orm_inspect_tool` before framing; verified rows read as boundary/contract evidence statements. Rigby A2 SIGN independently POSTed nothing — she ran `orm_inspect_tool filter model=Deliverable metadata__has_key=spec_prompt_shape` + `deliverable_tool detail` on the 3 real send-to-rigby deliverables I dispatched post-merge (real gpt-5-mini roundtrip; SERVER_NAME='localhost'); confirmed shape mapping AGREE per-row AND eyeballed the actual LLM output of the decision_evidence deliverable (`e51207dc-…`) — goal reads "Record that…" (capture, not implement); all 4 acceptance criteria are verification steps.

**HEAD at close:** `f533cacf8` + docs cascade PR (this file + handoff + wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`). Recycle-all clean at `sha=f533cacf8be0` post-PR-#3653.

Full context:
- `docs/handoffs/SESSION_2993_SPEC_PROMPT_BRANCHING_V2_ITEM_3.md`
- `docs/handoffs/SESSION_2992_FINDING_TYPE_CLASSIFIER_V2_ITEM_2.md` (prior)

---

## S2994 primary directive — pick between two natural next openers

With #1 (close_mode) + #2 (finding_type classifier + backfill) + #3 (prompt branching) + #5 (orm_inspect_tool allowlist) shipped, the remaining v2 sequence items are:

### Option A — v2 item #6: Rigby-SIGN nudge in UI for `finding_type=decision_evidence` (~30 min)

Now unblocked by S2993. The UI-side polish that lets Rigby surface a "verify evidence still holds" nudge for decision_evidence findings before dispatching a re-audit. Smallest remaining piece. Small React/frontend delta likely.

### Option B — v2 item #4: staleness detector at ingest (~1 session)

Walk `file:line` + identifier references, verify still-matches at HEAD, tag `staleness=suspected` on mismatch. Batch pass over existing 900 findings after landing. **Also needs `--dry-run` mode per PR #3648 zoom-out fold + `feedback_local_truth_no_production`.** Backend-only. Bigger unlock: it lets Rigby quickly flag when a `finding` may be pointing at code that's since moved/renamed.

**Recommendation:** Option A if you want a quick UI-visible win that closes the "surface finding_type value to human" loop; Option B if you want more backend leverage first (staleness = new orthogonal axis, useful in Rigby SIGN workflows). Both are cleanly scoped; pick one and skip framing debate.

### Ordered follow-on priorities (dependency-aware) after either choice
5. **`web_fetch_tool` session cookies (deferred half of v2 item #5)** — bigger design change; security review needed. Not blocking; open when Chris signals we need HTTP-shape verification past the ORM boundary.
6. **F-A2-equivalent for downstream consumers** — verify consumers referenced in ACs actually exist. ~30–60 min.
7. **Wire-through smoke-check AC for half-wired findings** — auto-add browser-session verification. ~30 min.
8. **Executable-prompt tightening (S2993 Fold C future_trigger)** — make `executable` acceptance_criteria more code-testable now that we've seen evidence_capture ship cleanly.
9. **Rigby Tool Gap Ledger entry from S2993 Fold B** — cheap dry-run preview endpoint for `send-to-rigby` that returns `would_use_shape / finding_type_used / spec_prompt_version` without calling the LLM. Would let Rigby preview a dispatch before burning tokens.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read the S2993 handoff in full — especially SIGN discipline section + fold classifications.
4. Optional pre-response state probes:
   - `git log --oneline -6` — should show docs cascade → `f533cacf8` (PR #3653) → `527f17664` (S2992 close) → `ab21d7a88` (PR #3651) → `5f4652f8d` (PR #3650) → `8debe2e5e` (S2991 close).
   - Rigby ORM-verify: `orm_inspect_tool action=filter model=Deliverable filters={"metadata__has_key":"spec_prompt_shape"} order_by=-created_at limit=5` — should return the 3 S2993 A2 SIGN deliverables (`6c43078e-…` / `3f42fefa-…` / `e51207dc-…`).
   - `curl -sS http://localhost:8000/api/schema/ | head -c 200` — drf-spectacular schema still live.

**Suggested first-turn shape for S2994:** ask Chris "A or B?" (Option A = UI nudge / Option B = staleness detector). Both are ~1-session-or-less; both consume the S2993 shape directly.

---

## S2994 carry-forward seeds (Chris picks whether to open — not gated on the v2 arc)

### New carry-forward from S2993

- **Fold B ledger candidate — dry-run preview for send-to-rigby.** Cheap endpoint that returns `would_use_shape / finding_type_used / spec_prompt_version` without calling the LLM. Would let Rigby (and the UI) preview a dispatch before spending tokens. Ledger, not blocking.
- **Fold C future_trigger — executable-prompt tightening.** Rigby correctly gated: don't tighten `executable` acceptance_criteria in the same PR as evidence-branching. Open as a distinct follow-on once we have quality stats on evidence_capture output (Rigby A2 sample was 1 deliverable; watch for the 2nd–3rd real dispatch to confirm the LLM stays on-shape).

### Carry-forward from S2992 (STILL OPEN)

- **Signal-tweak follow-up for `finding_type` classifier.** Two acceptable-misses surfaced during Rigby A2 SIGN at S2992: (1) `boundary drift` phrasing lands in `unknown` (regex expects `boundary (observation|violation)`); (2) `VERIFIED at HEAD` evidence records land in `executable` because they cite `file:line`. Neither blocking. Combine into a single signal-tweak PR if a 2nd independent trigger surfaces.
- **Data-migration-vs-management-command pattern.** PR #3651 chose data migration for cross-env reproducibility (matches migration 0399 backfill pattern). Alternative was live `--apply` invocation. If future one-shot backfills recur, codify the "data migration when reproducibility matters; --apply for signal iteration" split.

### Carry-forward from S2991 (STILL OPEN)

- **Dry-run counts pattern for future bulk-write migrations.** If pattern surfaces on a 3rd bulk-write migration, codify as a substrate rule.
- **Contract-lock-in guardrail on `close_mode`, `finding_type`, and now `spec_prompt_shape` + `finding_type_used`.** All are in Deliverable/finding payloads — renaming/removing values becomes breaking-change territory. Watch for frontend/PA consumers that read any of them.
- **Freshness axis 2nd-trigger clause.** Codified S2991; still no 2nd trigger. If any future finding surfaces "stale-corrected" state, add orthogonal `evidence_freshness` field; do NOT expand `close_mode` values.

### Carry-forward from S2989-S2990 (STILL OPEN)

- **`web_fetch_tool` session cookies** — deferred half of v2 item #5 (see #5 in follow-on list above).
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
- **Spec→ship contract:** PLAYBOOK-7.7.1 (9 phases + abort-early clause). S2993 was Flow B (spec-originated from S2991's v2 list); joint framing → Chris directive-already-ratified → execute → A2 SIGN → merge → recycle. No phase skipped.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations mandatory for T1/A2). Rigby returned real `orm_inspect_tool` tool_runs on T1 framing (3-row `decision_evidence` corpus sample), A2 verify (`orm_inspect_tool filter` + `deliverable_tool detail` on real send-to-rigby deliverables). Zero rubber-stamping across both SIGN cycles.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3 (plain english; "do we lose anything?" + "is it more work later?"; ≤1 decision). No new Chris decision required this session; the S2992-close directive was already ratified.
- **Cross-repo application:** PLAYBOOK-7.7.4. Not exercised this session.
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` after each merge. Backend-only diff, so HEAD-range path-diff detection correctly skipped frontend rebuild.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — Rigby T1 SIGN Ask #1 verified 3 real decision_evidence corpus rows via `orm_inspect_tool` before framing. Prevented shipping a prompt reframe against imaginary content.

---

## Wrapper pin note

The active PA conversation pin at S2993 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S2993 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S2993 was Flow B (spec-originated). Chris directive from S2992-close → Claude+Rigby joint framing → execute → Rigby A2 SIGN → merge → recycle was the shape. Rigby's T1 SIGN discipline (sampling 3 real `decision_evidence` corpus rows before I framed the reframe) is the canonical example this session of `feedback_verify_at_raw_orm_before_trusting_tool_no_data` — worth referencing in future prompt-shape work when spec directives describe LLM behavior without corpus grounding.
