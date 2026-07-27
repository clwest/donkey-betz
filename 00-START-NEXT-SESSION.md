# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2999 CLOSED. v2 item #7 shipped; v2 arc is 11-of-12 done.

**One feature PR merged this session** (Option A from S2998 close — v2 item #7 downstream consumer verifier; backend-only).

**PR #3668 (`d48ddc493`) — v2 item #7: F-A2-equivalent for downstream consumers.** Post-LLM-validation walks every `acceptance_criterion`, extracts `file:line` refs, checks each against HEAD via S2995's `_check_staleness_at_head` helper. Failed refs → `unverified_consumer_refs:N` warning on `spec.warnings` (fires existing `## Warnings` section) + full list in `extras.unverified_consumer_refs`. Deliberately quiet per Rigby T1 SIGN Ask #2 — S2997 owns the loud injection pattern; this is the quiet downstream analogue of F-A2. File:line-only per Ask #1. Skips prepended staleness ACs (S2997) via `prepended_count` so they don't double-count. Lazy-imports S2995 helpers to avoid pulling management-command module into hot path; fail-open if imports unavailable. 14 new tests + 70 pre-existing green. Rigby A2 SIGN via 2 real APIClient force-dispatches (used S2998's `force=true` escape hatch): both `unverified_consumer_refs=[]` (LLM produced clean ACs, verifier ran + found nothing). Rigby verified via `orm_inspect_tool filter(metadata__has_key='unverified_consumer_refs')`.

**HEAD at close:** `d48ddc493` + docs cascade PR (this file + handoff + wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`). Recycle-all clean at `sha=d48ddc493729` post-PR-#3668 (backend-only, frontend rebuild skipped correctly).

Full context:
- `docs/handoffs/SESSION_2999_AC_CONSUMER_VERIFIER_V2_ITEM_7.md`
- `docs/handoffs/SESSION_2998_SEND_TO_RIGBY_REDISPATCH_GUARD.md` (prior)

---

## S3000 primary directive — v2 arc is 11-of-12 done; only #5-cookies remains

**The findings-surface v2 arc is functionally complete except v2 item #5 cookies half.** Two natural paths:

### Option A — v2 item #5 cookies half: `web_fetch_tool` session cookies (~1 session, backend + security)

Rigby's HTTP-shape verification of backend endpoints kept hitting 401 across S2996, S2997, S2998 (twice), S2999. **5 concrete triggers now.** Larger design change; needs security review (how to safely pass session cookies to a PA tool). Closing this lets Rigby demonstrate the FULL A2 SIGN pattern via her own tool surface without me falling back to APIClient every time.

### Option B — Pivot to fresh arc

The v2 arc daily loop is complete. Chris may want to open a new arc (MEMORY `project_2100_plus_queue_ranking` suggests 2100 RAG / 2200 Frontend / 2300 Mobile / 2400 Auth / 2500 API / 2600 PA).

### Ordered follow-on priorities (dependency-aware) after choice
3. **Fold A (S2998) `future_trigger` — force=true × factory dedupe semantic mismatch.** Doc-first per Rigby A2 advice. Only ship polish if operator friction surfaces.
4. **Fold B (S2999) active watch — metadata accretion governance (S2995 Fold E).** Threshold: 5+ detector keys OR 2+ independent consumers reading metadata in production paths. Currently at 4 keys, 0 independent consumers.
5. **Fold C (S2999) — Rigby Tool Gap Ledger.** "Downstream verification is file:line-only; empty `unverified_consumer_refs` list means no phantom **file:line** refs, not no phantom refs at all."
6. **Fold F (S2997) — Rigby Tool Gap Ledger.** `orm_inspect_tool` doesn't support `metadata__<key>=value` JSON-path lookups.
7. **Fold B (S2997) `future_trigger` — dedupe strictness `(ref, verb)` key.**
8. **Executable-prompt tightening (S2993 Fold C future_trigger).**
9. **Rigby Tool Gap Ledger — dry-run preview endpoint for send-to-rigby (S2993 Fold B).**
10. **Rigby Tool Gap Ledger — backend-ahead-of-UI pattern watch (S2994 Fold D).**
11. **Rigby Tool Gap Ledger — per-row Recheck button on FindingsTab (S2996 Fold E).**
12. **Rigby Tool Gap Ledger — dedupe/override semantic mismatch (S2998 Fold C).**
13. **Toast staleness reinforcement (S2996 Fold C future_trigger).**
14. **Deliverables-tab type badge (S2994 Fold C future_trigger).**
15. **Staleness metadata → dedicated `staleness_detail` JSONField (S2995 Fold C future_trigger).**
16. **Periodic staleness beat schedule (S2995 Fold D future_trigger).**
17. **WorkspacePageNew param preservation (S2995 hotfix Fold F future_trigger).**

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read the S2999 handoff in full — especially the 4-fold classification (2 informational, 1 active-watch upgrade, 1 ledger candidate).
4. Optional pre-response state probes:
   - `git log --oneline -6` — should show docs cascade → `d48ddc493` (PR #3668) → `29ee89a3a` (S2998 close) → `d3ab2e889` (PR #3666) → `b65418425` (S2997 close) → `28c8547b0` (PR #3664).
   - Rigby ORM-verify: `orm_inspect_tool action=filter model=Deliverable filters={"metadata__has_key":"unverified_consumer_refs"} order_by=-created_at limit=5 fields=id,metadata` — should return the 2 deliverables from S2999 A2 SIGN with the new extras key.

**Suggested first-turn shape for S3000:** ask Chris "A or B?" — A closes the last v2 item + fixes a real ops pain that keeps costing me APIClient fallback; B depends on Chris's readiness. Recommendation weight: **A > B** (drain v2 completely before pivot; the cookies gap is a real ops cost that's climbed to 5th trigger).

---

## S3000 carry-forward seeds (Chris picks whether to open — not gated on the v2 arc)

### New carry-forward from S2999

- **Fold A `informational` — verifier ran clean.** Zero false positives + zero true positives on 2 real dispatches. Good MVP signal; not proof of exhaustive coverage. Watch for quality issues before expanding scope to identifier grepping.
- **Fold B `active watch` — metadata accretion governance (upgrade of S2995 Fold E).** 4 detector keys now. Trigger: 5+ keys OR 2+ independent consumers.
- **Fold C — Rigby Tool Gap Ledger.** File:line-only scope expectation-setting.
- **Fold D — v2 item #5 cookies: 5th trigger.** Priority climbing further. See Option A above.

### Carry-forward from S2998 (STILL OPEN)

- **Fold A `future_trigger` — force=true × factory dedupe semantic mismatch.** Doc-first per Rigby.
- **Fold B `future_trigger` — force re-dispatch could emit DeliverableEvent breadcrumb.**
- **Fold C — Rigby Tool Gap Ledger.** Semantic mismatch between endpoint override flag and downstream dedupe policy.

### Carry-forward from S2997 (STILL OPEN)

- **Fold B `future_trigger` — dedupe strictness on stale-ref ACs.**
- **Fold F — Rigby Tool Gap Ledger.** `orm_inspect_tool` JSON-path lookup unsupported.

### Carry-forward from S2996 (STILL OPEN)

- **Fold C `future_trigger` — staleness toast reinforcement.**
- **Fold E — Rigby Tool Gap Ledger (sharpened).** No in-UI Recheck action.

### Carry-forward from S2995 (STILL OPEN)

- **Fold C `future_trigger` — staleness metadata → dedicated JSONField.** Watch for 2nd trigger.
- **Fold D `future_trigger` — periodic staleness beat.**
- **Fold E — Rigby Tool Gap Ledger.** Metadata accretion governance (now `active watch` per S2999 Fold B).
- **Fold F `future_trigger` (S2994 hotfix) — WorkspacePageNew param preservation.**

### Carry-forward from S2994 (STILL OPEN)

- **Fold B `future_trigger` — inline-helper density.**
- **Fold C `future_trigger` — Deliverables-tab type badge.**
- **Fold D — Rigby Tool Gap Ledger.** Backend-semantics-shipped → UI-affordance-missing pattern.

### Carry-forward from S2993 (STILL OPEN)

- **Fold B ledger candidate — dry-run preview for send-to-rigby.**
- **Fold C future_trigger — executable-prompt tightening.**

### Carry-forward from S2992 (STILL OPEN)

- **Signal-tweak follow-up for `finding_type` classifier** (2 acceptable-misses).
- **Data-migration-vs-management-command pattern** (3rd-trigger check).

### Carry-forward from S2991 (STILL OPEN)

- **Dry-run counts pattern for future bulk-write migrations** (3rd-trigger check).
- **Contract-lock-in guardrail** — updated set: `close_mode`, `finding_type`, `spec_prompt_shape`, `finding_type_used`, `staleness`, `metadata.staleness_failed_refs`, `metadata.staleness_failed_refs_injected`, `metadata.unverified_consumer_refs`, `reason_code`.
- **Freshness axis 2nd-trigger clause** (still no 2nd trigger).

### Carry-forward from S2989-S2990 (STILL OPEN)

- **`web_fetch_tool` session cookies** — Option A above (5th trigger this session).
- **F-D3-tracker-scope wire-up** — ~1 session.
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
- **Spec→ship contract:** PLAYBOOK-7.7.1. S2999 was Flow B (Option A directive from S2998 close).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. T1 SIGN used real `repo_tool` grep. A2 SIGN used real APIClient dispatch + Rigby's independent `orm_inspect_tool filter(metadata__has_key)` — 5 sessions in a row where Rigby had to fall back to APIClient because `web_fetch_tool` can't authenticate to backend endpoints.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. No new decision required.
- **Cross-repo application:** PLAYBOOK-7.7.4. Not exercised.
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` after each merge. Backend-only diff → frontend rebuild skipped correctly.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — A2 SIGN used real dispatch + ORM verify BEFORE Rigby signed off. Both dispatches produced empty `unverified_consumer_refs` legitimately.
- **`feedback_zoom_out_ask_per_rigby_sign`** — A2 zoom-out is now the primary vehicle for **carry-forward-priority-climbing signal** — this session bumped v2 item #5 cookies to 5th trigger, upgraded metadata governance to active watch, added a fresh ledger candidate.

---

## Wrapper pin note

The active PA conversation pin at S2999 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S2999 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S2999 closes a 9-session Flow B arc (S2991–S2999) where every session shipped ≥1 v2 item using the same shape: T1 SIGN with real tool_run → code → A2 SIGN with real ops → fold classification → close cascade. The consistent behavior of A2 SIGN surfacing folds (informational + future_trigger + ledger + priority-climbing) that the T1 framing didn't catch is the strongest signal we have that PLAYBOOK-7.7.2 SIGN evidence discipline is doing its job. **Watch for the moment we ship a v2-item-like PR WITHOUT a real-ops A2 SIGN** — that's when this pattern would break down.
