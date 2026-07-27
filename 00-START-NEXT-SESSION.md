# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2994 CLOSED. Findings-surface v2 item #6 shipped end-to-end.

**One feature PR merged this session (Flow B — spec-originated engineering work from S2991's v2 list; frontend-only).**

**PR #3655 (`ddeb9e19f`) — v2 item #6: `FindingsTab` differentiates decision_evidence findings in the UI.** Adds `finding_type` to Finding TS type + `FindingTypeBadge` (amber "Evidence" / blue "Executable" / hidden for `unknown`) on every row. New `finding_type` filter dropdown. Decision-evidence open findings get a distinct action-side treatment: tiny inline helper ("Decision record — verify boundary before re-audit."), Send-to-Rigby button relabels to "Verify evidence" with amber styling + tooltip ("Create a re-audit spec to confirm this boundary still holds"). Toast copy after dispatch differentiates: "Evidence-capture deliverable created (…)" vs "Engineering spec deliverable created (…)" — closes the mental-model loop between the send action and the S2993 backend prompt-shape. No backend changes. Rigby T1 SIGN AGREE all asks with real `deliverable_tool detail` tool_run confirming "Verify evidence" copy matches actual shipped S2993 A2 SIGN evidence deliverable output. Rigby A2 SIGN AGREE both substrate asks via `orm_inspect_tool` (finding_type distribution `{unknown: 623, decision_evidence: 139, executable: 138, 900 total}`; 3 recent Deliverables with `spec_prompt_shape` metadata confirming toast branches have real data).

**HEAD at close:** `ddeb9e19f` + docs cascade PR (this file + handoff + wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`). Recycle-all clean at `sha=ddeb9e19f46c` post-PR-#3655 (frontend rebuild included per `feedback_recycle_after_merge` — 2303 modules transformed, Daphne restarted).

Full context:
- `docs/handoffs/SESSION_2994_FINDINGS_TAB_EVIDENCE_NUDGE_V2_ITEM_6.md`
- `docs/handoffs/SESSION_2993_SPEC_PROMPT_BRANCHING_V2_ITEM_3.md` (prior)

---

## S2995 primary directive — Option B from S2994 open: v2 item #4 (staleness detector at ingest)

**Chris ratified "A then B" at S2994 open.** A shipped this session; B is up next.

### v2 item #4 — staleness detector at ingest (~1 session, backend-only)

Walk `file:line` + identifier references embedded in DocResearchFinding.text, verify they still match at HEAD, tag `staleness=suspected` on mismatch. Batch pass over the existing 900 findings after landing.

**Also needs `--dry-run` mode per PR #3648 zoom-out fold + `feedback_local_truth_no_production` — do NOT frame envelope §Limitations as "live E2E deferred to production Railway deploy"; local pass = shipped.**

**Sub-PR shape (likely 2 PRs):**
- PR (a): schema-only `staleness` field on `DocResearchFinding` (default `unstale`) + `_check_staleness_at_head` helper in the ingest command + tests. Migration 0402 schema-only with default.
- PR (b): backfill data migration (0403) re-runs the staleness check over all 900 existing rows.

**Ordered follow-on priorities (dependency-aware) after B**
5. **`web_fetch_tool` session cookies (deferred half of v2 item #5)** — bigger design change; security review needed. Not blocking; open when Chris signals we need HTTP-shape verification past the ORM boundary.
6. **F-A2-equivalent for downstream consumers** — verify consumers referenced in ACs actually exist. ~30–60 min.
7. **Wire-through smoke-check AC for half-wired findings** — auto-add browser-session verification. ~30 min.
8. **Executable-prompt tightening (S2993 Fold C future_trigger).**
9. **Rigby Tool Gap Ledger — dry-run preview endpoint (S2993 Fold B).**
10. **Rigby Tool Gap Ledger — backend-ahead-of-UI pattern watch (S2994 Fold D).** Any future finding_type-like axis should ship its UI affordance same session.
11. **Deliverables-tab type badge (S2994 Fold C future_trigger).** Extend the "Evidence-capture vs Engineering" distinction to the WorkspacePageNew Deliverables tab so post-navigation context survives.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read the S2994 handoff in full — especially SIGN discipline section + Fold D (Rigby Tool Gap Ledger backend-ahead-of-UI pattern).
4. Optional pre-response state probes:
   - `git log --oneline -6` — should show docs cascade → `ddeb9e19f` (PR #3655) → `bc141fd58` (S2993 close) → `f533cacf8` (PR #3653) → `527f17664` (S2992 close) → `ab21d7a88` (PR #3651).
   - Chris browser visual smoke on S2994 FindingsTab — should see (a) "Evidence" badge on decision_evidence rows; (b) "Type: Any" filter dropdown; (c) "Verify evidence" button + amber helper on decision_evidence open findings; (d) toast copy "Evidence-capture deliverable created (…)" when clicking Verify evidence. ~5 min.
   - Rigby ORM-verify: `orm_inspect_tool action=filter model=DocResearchFinding filters={"finding_type":"decision_evidence"} limit=1 fields=text` — confirms the row Chris will see the Verify evidence button on has real content.

**Suggested first-turn shape for S2995:** open item #4 with framing → Rigby T1 SIGN (ask her to sample 3 real findings with `file:line` references, verify the paths still exist at HEAD, and confirm the staleness check design catches the drift patterns you care about).

---

## S2995 carry-forward seeds (Chris picks whether to open — not gated on the v2 arc)

### New carry-forward from S2994

- **Fold B `future_trigger` — inline-helper density.** Helper renders on every open decision_evidence row; up to 139 with unfiltered view. If Chris flags "noisy," next step is show-on-hover or show-once-per-session. Watch for the signal; 2nd trigger threshold NOT yet met.
- **Fold C `future_trigger` — Deliverables-tab type badge.** Natural extension of #6 to WorkspacePageNew's deliverables tab so post-navigation context survives. Not blocking; open if Chris signals "I forgot which deliverables are which type."
- **Fold D — Rigby Tool Gap Ledger entry.** Pattern: "backend semantics shipped → UI affordance missing → user intent mismatch risk." S2993 shipped backend prompt branching; S2994 shipped UI affordance one session later. Watch for future finding_type-like axes and ship UI affordance same session or explicitly log the gap.

### Carry-forward from S2993 (STILL OPEN)

- **Fold B ledger candidate — dry-run preview for send-to-rigby.** Cheap endpoint that returns `would_use_shape / finding_type_used / spec_prompt_version` without calling the LLM. Ledger, not blocking.
- **Fold C future_trigger — executable-prompt tightening.** Rigby correctly gated: don't tighten `executable` acceptance_criteria in the same PR as evidence-branching. Open as a distinct follow-on once we have quality stats on evidence_capture output.

### Carry-forward from S2992 (STILL OPEN)

- **Signal-tweak follow-up for `finding_type` classifier.** Two acceptable-misses surfaced during Rigby A2 SIGN at S2992: (1) `boundary drift` phrasing lands in `unknown`; (2) `VERIFIED at HEAD` evidence records land in `executable` because they cite `file:line`. Combine into a single signal-tweak PR if a 2nd independent trigger surfaces.
- **Data-migration-vs-management-command pattern.** If future one-shot backfills recur, codify the "data migration when reproducibility matters; --apply for signal iteration" split.

### Carry-forward from S2991 (STILL OPEN)

- **Dry-run counts pattern for future bulk-write migrations.** If pattern surfaces on a 3rd bulk-write migration, codify as a substrate rule.
- **Contract-lock-in guardrail on `close_mode`, `finding_type`, `spec_prompt_shape`, `finding_type_used`, and now (implicitly) FindingsTab toast/badge copy.** All are in user-visible payloads — renaming/removing values becomes breaking-change territory.
- **Freshness axis 2nd-trigger clause.** Still no 2nd trigger.

### Carry-forward from S2989-S2990 (STILL OPEN)

- **`web_fetch_tool` session cookies** — deferred half of v2 item #5 (see #5 in follow-on list above).
- **F-D3-tracker-scope wire-up** — activate OpsRun tracker for PA turns. ~1 session.
- **F-D2-broad LLM-bypass audit spec** — evaluate user-facing personalization impact of each `enforce_real_ai` / `chat.completions` / `responses.create` non-PA callsite. ~1 session.
- **Reconcile Chris's 1805 cap-drift via `memory_hygiene_audit --apply`.** ~30 min.
- **Canonical Briefing v2 scope toggle.** Arc-Folder / All-Docs + default exclude-globs. ~1-2 hr.
- **Substrate fix for `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`.** ~1 session.
- **Send-to-Rigby follow-ups from S2988 (STILL OPEN).**

### Older carry-forward (STILL OPEN)

- **Chris browser visual check on S2985 Canonical Briefing tab strip / Refresh behavior.** ~5 min.
- **Rigby `claude_code_tool` safeguards.** Log to Rigby Tool Gap Ledger.
- **Chris browser visual check on S2984 arcs section.** ~5 min.
- **Systemic auth-XHR treatment (STILL OPEN from S2984 as Fold).** Not blocking; open when 2nd independent trigger surfaces.
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
- **Spec→ship contract:** PLAYBOOK-7.7.1 (9 phases + abort-early clause). S2994 was Flow B (spec-originated from S2991's v2 list + Chris "A then B" directive at S2994 open). Joint framing → Chris ratification-already-in-hand → execute → Rigby A2 SIGN → merge → recycle-all. No phase skipped.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations mandatory for T1/A2). Rigby T1 SIGN fetched the actual S2993 evidence deliverable content via `deliverable_tool detail` before I committed UI copy. A2 SIGN independently ran `orm_inspect_tool count_by` + `filter` to verify substrate. Zero rubber-stamping.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. No new Chris decision this session; "A then B" already ratified at S2994 open.
- **Cross-repo application:** PLAYBOOK-7.7.4. Not exercised.
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` after each merge. **Frontend-touching diff → recycle-all rebuilt frontend (2303 modules, 3.42s), NOT celery-recycle alone.** `feedback_recycle_after_merge` compliance.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — Rigby A2 SIGN verified `finding_type` distribution counts + `spec_prompt_shape` metadata via ORM before signing off.

---

## Wrapper pin note

The active PA conversation pin at S2994 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S2994 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S2994 was Flow B (spec-originated + Chris A/B ratification at S2994 open). Chris directive → Claude+Rigby joint framing → execute → Rigby A2 SIGN → merge → recycle-all was the shape. Frontend-only PR compliance with `feedback_recycle_after_merge` is the canonical example this session — `make recycle-all` rebuilt `frontend/dist/` and restarted Daphne so the UI is visible immediately post-merge. Do NOT default to `make celery-recycle` on a frontend diff.
