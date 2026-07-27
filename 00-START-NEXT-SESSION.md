# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2996 CLOSED. FindingsTab staleness surface shipped end-to-end.

**One feature PR merged this session** (Flow B — Option A from S2995 close; frontend-only).

**PR #3661 (`12e5400a2`) — v2 Option A: FindingsTab surfaces staleness (badge + filter + failed-refs).** Extends the S2994 UI treatment to the S2995 staleness axis. Chris can now visually spot the 4 currently-suspected findings without needing the API param detour. New `StalenessBadge` (orange Clock icon + "Stale" text; hidden for `fresh` per hidden-for-default pattern). Filter dropdown "Staleness: Any / Fresh / Suspected stale" wires the S2995 `?staleness=` backend param. Expanded-row detail lists `metadata.staleness_failed_refs` as orange monospace chips (plain list, no clickable-URL coupling). Rigby T1 SIGN confirmed via `orm_inspect_tool` that all 4 suspected rows are `finding_type=executable` — informed color choice (orange stays distinguishable from amber Evidence + blue Executable). Rigby A2 SIGN verified substrate + additionally surfaced the deferred v2 item #5 half as a real ops gap (`web_fetch_tool` 401 on HTTP verify — expected; that gap now has 2nd trigger evidence).

**HEAD at close:** `12e5400a2` + docs cascade PR (this file + handoff + wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`). Recycle-all clean at `sha=12e5400a222a` post-PR-#3661 (frontend rebuild included per `feedback_recycle_after_merge` — 2303 modules transformed).

Full context:
- `docs/handoffs/SESSION_2996_FINDINGS_TAB_STALENESS_SURFACE.md`
- `docs/handoffs/SESSION_2995_STALENESS_DETECTOR_V2_ITEM_4.md` (prior)

---

## S2997 primary directive — v2 arc UI-side is functionally done; pick a substrate direction

**The findings-surface v2 UI-side is fully shipped.** All four axes (status/close_mode/finding_type/staleness) exist on the backend AND have visual surfaces on FindingsTab (badges hidden-for-default, filters, targeted CTAs). This is a natural arc-closure point.

Three remaining v2 items + three next-arc candidates:

### Option A — v2 item #7: F-A2-equivalent for downstream consumers (~30–60 min, backend)

Verify that consumers referenced in Deliverable acceptance criteria actually exist. Similar shape to the S2989 F-A2 fold (citation-path allowlist) but for the downstream side: when a spec deliverable lists "consumer X should be updated," verify X is a real code path before accepting the spec. Consumes the S2995 `_check_staleness_at_head` helper directly (same file-existence-at-HEAD pattern).

### Option B — v2 item #8: wire-through smoke-check AC for half-wired findings (~30 min, backend)

Auto-add browser-session verification steps to spec deliverables whose findings have `staleness_failed_refs`. Directly consumes the S2995 failed-refs output — for each stale ref, add an AC line like "Verify path X still exists at HEAD or update the citation."

### Option C — v2 item #5 (deferred half): `web_fetch_tool` session cookies (~1 session, backend + security)

Rigby's A2 SIGN this session hit 401 on `web_fetch_tool` HTTP verification of a backend endpoint — 2nd trigger of a known gap. Larger design change; needs security review (how to safely pass session cookies to a PA tool). Not blocking but the trigger count is climbing.

### Option D — Rigby Tool Gap Ledger: staleness recheck action (~30 min, frontend + endpoint)

S2996 Fold E ledger candidate. Add an authenticated "Recheck" button on `staleness=suspected` rows that calls a new endpoint wrapping the S2995 `--recheck-staleness --apply` mode scoped to a single finding. Sharpens the S2996 badge → action loop.

### Option E — Pivot to fresh arc

The v2 arc is functionally complete for daily use. Chris may want to open a new arc (see MEMORY `project_2100_plus_queue_ranking` — proposed queue includes 2100 RAG / 2200 Frontend / 2300 Mobile / 2400 Auth / 2500 API / 2600 PA).

### Ordered follow-on priorities (dependency-aware) after choice
5. **Executable-prompt tightening (S2993 Fold C future_trigger).**
6. **Rigby Tool Gap Ledger — dry-run preview endpoint for send-to-rigby (S2993 Fold B).**
7. **Rigby Tool Gap Ledger — backend-ahead-of-UI pattern watch (S2994 Fold D).**
8. **Rigby Tool Gap Ledger — metadata accretion governance (S2995 Fold E).** Reserve `metadata.detectors.*` / `metadata.sign.*` namespace convention.
9. **Toast staleness reinforcement (S2996 Fold C future_trigger).**
10. **Deliverables-tab type badge (S2994 Fold C future_trigger).**
11. **Staleness metadata → dedicated `staleness_detail` JSONField (S2995 Fold C future_trigger).** Trigger: metadata grows beyond one list of refs.
12. **Periodic staleness beat schedule (S2995 Fold D future_trigger).** Trigger: UI surface for stale findings exists — **now met at S2996**, so this is more actionable.
13. **WorkspacePageNew param preservation (S2995 hotfix Fold F future_trigger).** Merge instead of replace on tab/sub setSearchParams.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read the S2996 handoff in full — especially the fold classification section.
4. Optional pre-response state probes:
   - `git log --oneline -6` — should show docs cascade → `12e5400a2` (PR #3661) → `7b4b4adec` (S2995 close) → `85d37d0fc` (PR #3659) → `c4c814f27` (PR #3658) → `2b9ba90cc` (PR #3657).
   - Rigby ORM-verify: `orm_inspect_tool action=filter model=DocResearchFinding filters={"staleness":"suspected"} limit=5 fields=id,staleness,metadata` — should return the 4 rows with `staleness_failed_refs` populated.
   - Chris browser smoke: open FindingsTab, set filter Staleness=Suspected, confirm 4 orange "Stale" badges visible + expanding one shows failed-refs chip.

**Suggested first-turn shape for S2997:** ask Chris "A / B / C / D / E?" — B is smallest and directly consumes S2995 output; A is next-smallest and reuses S2995 helper; D closes the S2996 loop tighter; C is bigger but addresses a growing pain (2nd trigger). Recommendation weight: B > A > D > C > E (unless Chris signals fresh-arc pivot).

---

## S2997 carry-forward seeds (Chris picks whether to open — not gated on the v2 arc)

### New carry-forward from S2996

- **Fold A `informational` — 2nd trigger on v2 item #5 (`web_fetch_tool` cookies).** Rigby A2 hit 401 verifying backend endpoint. 2nd concrete occurrence; Rigby's HTTP-shape verification of backend endpoints is blocked by auth. Bumps priority of Option C above.
- **Fold C `future_trigger` — staleness toast reinforcement.** Toast copy for suspected findings could read "Evidence-capture created (staleness suspected)". Optional polish; watch for Chris signal.
- **Fold E — Rigby Tool Gap Ledger (sharpened).** No in-UI action to re-run staleness verification for a single finding from FindingsTab. Clear next-increment shape (Option D above).

### Carry-forward from S2995 (STILL OPEN)

- **Fold C `future_trigger` — staleness metadata → dedicated JSONField.** Watch for 2nd trigger.
- **Fold D `future_trigger` — periodic staleness beat.** **S2996 satisfies the "UI surface exists" precondition** so this is now actionable if daily continuous-freshness matters.
- **Fold E — Rigby Tool Gap Ledger.** Metadata accretion governance (namespace convention).
- **Fold F `future_trigger` (S2994 hotfix) — WorkspacePageNew param preservation.**

### Carry-forward from S2994 (STILL OPEN)

- **Fold B `future_trigger` — inline-helper density.**
- **Fold C `future_trigger` — Deliverables-tab type badge.**
- **Fold D — Rigby Tool Gap Ledger.** Backend-semantics-shipped → UI-affordance-missing pattern.

### Carry-forward from S2993 (STILL OPEN)

- **Fold B ledger candidate — dry-run preview for send-to-rigby.**
- **Fold C future_trigger — executable-prompt tightening.**

### Carry-forward from S2992 (STILL OPEN)

- **Signal-tweak follow-up for `finding_type` classifier** (2 acceptable-misses; combine into single PR if 2nd trigger surfaces).
- **Data-migration-vs-management-command pattern** (3rd-trigger check).

### Carry-forward from S2991 (STILL OPEN)

- **Dry-run counts pattern for future bulk-write migrations** (3rd-trigger check).
- **Contract-lock-in guardrail** on `close_mode`, `finding_type`, `spec_prompt_shape`, `finding_type_used`, `staleness`, `metadata.staleness_failed_refs`.
- **Freshness axis 2nd-trigger clause** (still no 2nd trigger).

### Carry-forward from S2989-S2990 (STILL OPEN)

- **`web_fetch_tool` session cookies** — see Option C above (2nd trigger this session).
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
- **Spec→ship contract:** PLAYBOOK-7.7.1. S2996 was Flow B (Option A directive from S2995 close). No phase skipped.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations mandatory). Both SIGN cycles this session used real `orm_inspect_tool` results. A2 additionally used `web_fetch_tool` which produced the 2nd-trigger evidence for the deferred v2 item #5 half.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. No new decision required; Option A already ratified.
- **Cross-repo application:** PLAYBOOK-7.7.4. Not exercised.
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` after each merge. Frontend diff → recycle-all correctly triggered frontend rebuild. `feedback_recycle_after_merge` compliance.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — Rigby A2 Ask #1 used raw ORM to confirm the 4 rows have `staleness_failed_refs` populated (the exact data the UI chips render).

---

## Wrapper pin note

The active PA conversation pin at S2996 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S2996 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S2996 was Flow B (Option A directive-in-hand). The v2 arc has been running Flow B end-to-end for 5 sessions straight (S2991 through S2996) — the pattern is stable. Notable this session: Rigby A2 SIGN naturally surfaced a 2nd trigger on an existing deferred item (v2 item #5 cookies) simply by trying to verify a backend endpoint. That's the SIGN-cycle-as-passive-signal-collection pattern paying off — worth watching for a 3rd occurrence to justify making it a Playbook rule.
