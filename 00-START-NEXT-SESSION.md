# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2995 CLOSED. Findings-surface v2 item #4 shipped + S2994 hotfix.

**Three feature PRs merged this session** (Flow B — spec-originated + Chris-signaled UX hotfix; two backend + one frontend).

**PR #3657 (`2b9ba90cc`) — S2994 hotfix: post-dispatch View-deliverable link.** Chris hit a footgun on the S2994 Verify-evidence button — after dispatch it stayed clickable and would re-dispatch. Fixed by making the CTA shape-aware: once `finding.deliverable_id` is set, the button transforms into an emerald "View deliverable" link with `ExternalLink` icon + type-aware tooltip. Deep-links via a new `?deliverable=<id>` query param that `DeliverablesTab` now consumes to auto-`setSelectedId`. Mirrors the S2984 `?filter=` deep-link pattern.

**PR #3658 (`c4c814f27`) — v2 item #4 PR (a): schema + helper + serializer + tests.** Fourth orthogonal axis on `DocResearchFinding` — `staleness = fresh | suspected`. `_check_staleness_at_head(text, base_dir, file_index)` reuses `EXECUTABLE_FILE_LINE_RE` for extraction. Bare-filename refs (`foo.py:123` — common in real corpus) resolve via a `git ls-files` basename index built once per command invocation (Rigby T1 SIGN Fold A same-PR mitigation). Failed refs land in `metadata['staleness_failed_refs']` so v2 item #8 can consume without a second schema field. New `--recheck-staleness [--apply]` mode mirrors S2992's `--reclassify-existing` shape. Serializer + list filter surface `staleness`. 25 tests. Migration 0402 kept surgical (schema-only) per S2992 precedent.

**PR #3659 (`85d37d0fc`) — v2 item #4 PR (b): backfill on 900-row corpus.** Data migration 0403 re-runs `_check_staleness_at_head` over every existing row. **Distribution matches pre-merge dry-run exactly: 896 fresh (99.6%) / 4 suspected (0.4%) / 900 total.** All 4 suspected findings are real drift signals (refs to paths that don't exist in the repo layout: `models/conversations/`, `executor/`, `assistant/`, or a bare-file line-out-of-range). **Zero false positives** from the git-ls-files basename normalization — Rigby T1 SIGN Fold A paid off exactly as predicted.

**HEAD at close:** `85d37d0fc` + docs cascade PR (this file + handoff + wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`). Recycle-all clean at `sha=85d37d0fc106` post-PR-#3659.

Full context:
- `docs/handoffs/SESSION_2995_STALENESS_DETECTOR_V2_ITEM_4.md`
- `docs/handoffs/SESSION_2994_FINDINGS_TAB_EVIDENCE_NUDGE_V2_ITEM_6.md` (prior)

---

## S2996 primary directive — pick between three natural next openers

**With v2 items #1/#2/#3/#4/#5 (ORM half)/#6 all shipped, the sequence has drained to the smallest remaining items.** Two natural continuation paths:

### Option A — Extend FindingsTab UI with staleness badge + filter (~30 min)

Mirrors the S2994 finding_type UI treatment for the new staleness axis. Adds:
- Amber "Stale" badge on `staleness=suspected` rows (hidden for `fresh`)
- Filter dropdown "Staleness: Fresh / Suspected / Any"
- Optional: expanded-row detail shows `metadata.staleness_failed_refs`

This closes the loop between the backend detector and the human review path — right now Chris can filter via API/URL param but the UI doesn't visually differentiate the 4 suspected rows.

### Option B — v2 item #7: F-A2-equivalent for downstream consumers (~30–60 min)

Verify that consumers referenced in Deliverable acceptance criteria actually exist. Similar shape to the S2989 F-A2 fold (citation-path allowlist) but for the downstream side of the pipeline: when a spec deliverable lists "consumer X should be updated," we should verify X is a real code path before accepting the spec.

### Option C — v2 item #8: wire-through smoke-check AC for half-wired findings (~30 min)

Auto-add browser-session verification steps to spec deliverables whose findings have `staleness_failed_refs` — the failed ref list produced by S2995 directly feeds this. Naturally consumes S2995 output.

**Recommendation:** Option A is the smallest UI-visible win and closes the S2995 → human loop directly. Option C is the smallest backend win that consumes S2995 output. Option B is the biggest unlock but least urgent. Pick A if UI-visible progress matters; pick C if you want to keep the backend momentum.

### Ordered follow-on priorities (dependency-aware) after choice
4. **`web_fetch_tool` session cookies (deferred half of v2 item #5)** — bigger design change; security review needed.
5. **Executable-prompt tightening (S2993 Fold C future_trigger).**
6. **Rigby Tool Gap Ledger — dry-run preview endpoint for send-to-rigby (S2993 Fold B).**
7. **Rigby Tool Gap Ledger — backend-ahead-of-UI pattern watch (S2994 Fold D).**
8. **Rigby Tool Gap Ledger — metadata accretion governance (S2995 Fold E).** Reserve `metadata.detectors.*` or `metadata.sign.*` namespace convention; document allowed keys.
9. **Deliverables-tab type badge (S2994 Fold C future_trigger).**
10. **Staleness metadata → dedicated `staleness_detail` JSONField (S2995 Fold C future_trigger).** Trigger: metadata grows beyond one list of refs.
11. **Periodic staleness beat schedule (S2995 Fold D future_trigger).** Trigger: UI surface for stale findings exists.
12. **WorkspacePageNew param preservation (S2995 hotfix Fold F future_trigger).** Merge instead of replace on tab/sub setSearchParams so `?deliverable=` and future deep-link params survive tab clicks.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read the S2995 handoff in full — especially the 6-fold classification block + Rigby A2 SIGN verification of 896/4 distribution.
4. Optional pre-response state probes:
   - `git log --oneline -6` — should show docs cascade → `85d37d0fc` (PR #3659) → `c4c814f27` (PR #3658) → `2b9ba90cc` (PR #3657) → `6057819fe` (S2994 close) → `ddeb9e19f` (PR #3655).
   - Rigby ORM-verify: `orm_inspect_tool action=count_by model=DocResearchFinding field=staleness` — should return `{fresh: 896, suspected: 4}`.
   - Chris browser smoke: on the S2994 finding that originally triggered the hotfix, the button should now say "View deliverable" (emerald) and clicking it should land in DeliverablesTab with the correct deliverable's detail panel open.

**Suggested first-turn shape for S2996:** ask Chris "A, B, or C?" — all three are ≤1 hr; all three consume prior arc output. Recommendation weight: A (UI closes loop) > C (backend consumes staleness) > B (biggest unlock but least urgent).

---

## S2996 carry-forward seeds (Chris picks whether to open — not gated on the v2 arc)

### New carry-forward from S2995

- **Fold C `future_trigger` — staleness metadata → dedicated JSONField.** `metadata['staleness_failed_refs']` is currently the 3rd domain-specific key in `metadata` JSON (alongside spec_prompt_shape, finding_type_used). Rigby A2 flagged moderate long-term schema-drift risk. Promote to `staleness_detail` JSONField once it grows past "one list of refs" (e.g. failure_kinds, checked_refs, timestamps, head_sha). Not blocking; watch for 2nd trigger.
- **Fold D `future_trigger` — periodic staleness beat.** On-demand cadence right for now (0.4% signal rate + no UI surface). Revisit if UI surfaces stale findings and continuous freshness matters.
- **Fold E — Rigby Tool Gap Ledger.** Metadata accretion governance. Reserve namespace convention (`metadata.detectors.*` or `metadata.sign.*`) + document allowed keys + expected shapes. Logged.
- **Fold F `future_trigger` (S2994 hotfix) — WorkspacePageNew param preservation.** `setSearchParams({tab, sub}, {replace: true})` drops `?deliverable=` and future deep-link params on tab clicks. Fix would merge instead of replace, or explicitly whitelist pass-through params.

### Carry-forward from S2994 (STILL OPEN)

- **Fold B `future_trigger` — inline-helper density.** Amber decision-record helper renders on every open decision_evidence row. If Chris flags "noisy," next step is show-on-hover or show-once-per-session.
- **Fold C `future_trigger` — Deliverables-tab type badge.** Natural extension of #6 to WorkspacePageNew's deliverables tab so post-navigation context survives.
- **Fold D — Rigby Tool Gap Ledger entry.** Backend-semantics-shipped → UI-affordance-missing pattern (S2993 backend / S2994 UI one session later).

### Carry-forward from S2993 (STILL OPEN)

- **Fold B ledger candidate — dry-run preview for send-to-rigby.** Cheap endpoint that returns `would_use_shape / finding_type_used / spec_prompt_version` without calling the LLM.
- **Fold C future_trigger — executable-prompt tightening.** Open once we have quality stats on evidence_capture output.

### Carry-forward from S2992 (STILL OPEN)

- **Signal-tweak follow-up for `finding_type` classifier.** Two acceptable-misses (`boundary drift` → unknown; `VERIFIED at HEAD` → executable). Combine into a signal-tweak PR if a 2nd independent trigger surfaces.
- **Data-migration-vs-management-command pattern.** Codify the "data migration when reproducibility matters; --apply for signal iteration" split if the pattern surfaces on a 3rd bulk-write migration.

### Carry-forward from S2991 (STILL OPEN)

- **Dry-run counts pattern for future bulk-write migrations.** Third trigger check.
- **Contract-lock-in guardrail** on `close_mode`, `finding_type`, `spec_prompt_shape`, `finding_type_used`, and now **`staleness`** + `metadata.staleness_failed_refs`. All are user-visible payloads — renaming/removing values becomes breaking-change territory.
- **Freshness axis 2nd-trigger clause.** Still no 2nd trigger.

### Carry-forward from S2989-S2990 (STILL OPEN)

- **`web_fetch_tool` session cookies** — deferred half of v2 item #5.
- **F-D3-tracker-scope wire-up** — activate OpsRun tracker for PA turns. ~1 session.
- **F-D2-broad LLM-bypass audit spec** — ~1 session.
- **Reconcile Chris's 1805 cap-drift via `memory_hygiene_audit --apply`.** ~30 min.
- **Canonical Briefing v2 scope toggle.** ~1-2 hr.
- **Substrate fix for `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT`.** ~1 session.
- **Send-to-Rigby follow-ups from S2988 (STILL OPEN).**

### Older carry-forward (STILL OPEN)

- **Chris browser visual check on S2985 Canonical Briefing tab strip / Refresh behavior.** ~5 min.
- **Rigby `claude_code_tool` safeguards.** Log to Rigby Tool Gap Ledger.
- **Chris browser visual check on S2984 arcs section.** ~5 min.
- **Systemic auth-XHR treatment (STILL OPEN from S2984 as Fold).**
- **Live-dispatch smoke on S2982 stage-doc guardrails.** ~15 min.
- **Exercise PLAYBOOK-7.7.4 against a sibling repo.**
- **Browser UX smoke on S2980 Theme Signals UX upgrade.** ~5 min.
- **Phase B Theme Signals — "Why now" LLM summarizer.** ~1 session.
- **Phase B Theme Signals — who-benefits/who-loses.** ~1-2 sessions.
- **Theme Signals — sub-tab persistence via localStorage.** ~30 min.
- **Rigby Tool Gap Ledger — Fold D from S2982.** DB uniqueness constraint on `AgentExecution.celery_task_id`. ~30-60 min.
- **Fold B `future_trigger` from v0.8.0 — fold-authoring evidence-admission helper.** 3-trigger threshold NOT yet met.
- **Post-close housekeeping (LOW priority).** Fill Playbook front-matter `commit_sha` + `content_hash` PLACEHOLDER fields for both v0.9.0 and v0.10.0.

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session.
- **Spec→ship contract:** PLAYBOOK-7.7.1 (9 phases + abort-early clause). S2995 was Flow B (spec-originated from S2991 v2 list + Chris "A then B" directive at S2994 open). Three PRs shipped: S2994 hotfix (Chris-signaled mid-session) followed the same 7.7.1 shape; item #4 PRs (a) + (b) followed the S2992 sub-PR pattern.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations mandatory for T1/A2). Rigby returned real tool_runs on every SIGN cycle this session (T1 for item #4: `orm_inspect_tool` 20-row corpus sample; T1 for S2994 hotfix: `repo_tool` search; A2 for item #4: `count_by(staleness)` + `filter(staleness='suspected')`).
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Item #4 already ratified at S2994 open as "Option B"; S2994 hotfix routed with plain-english framing per Chris signal.
- **Cross-repo application:** PLAYBOOK-7.7.4. Not exercised.
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` after each merge. S2994 hotfix diff touched `frontend/**` → recycle-all correctly triggered frontend rebuild. Item #4 PRs are backend-only → recycle-all correctly skipped frontend rebuild via HEAD-range path-diff.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — Backfill dry-run verified via direct ORM before committing the data migration; 4 suspected rows spot-checked against real file paths to confirm real drift signals (not false positives) BEFORE Rigby A2 SIGN.
- **`feedback_local_truth_no_production`** — Path checks use local filesystem; `--apply` IS the deploy step.
- **`feedback_recycle_after_merge`** — S2994 hotfix triggered `make recycle-all` (frontend rebuild); backend-only item #4 PRs used same command (frontend rebuild skipped correctly via HEAD-range path-diff).

---

## Wrapper pin note

The active PA conversation pin at S2995 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S2995 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S2995 was Flow B (spec-originated + Chris-signaled mid-session hotfix). The mid-session hotfix pattern (Chris signal → T1 SIGN → code → PR → merge → recycle) is worth watching — this is the second session in a row where Chris real-use-of-a-just-shipped-feature surfaced a small footgun (S2994 helper density concerns → not blocking; S2995 hotfix here → blocking). If a third instance surfaces, consider whether a "same-session polish PR budget" pattern belongs in the Playbook.
