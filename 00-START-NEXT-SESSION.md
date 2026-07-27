# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2998 CLOSED. send-to-rigby re-dispatch guard shipped (v2 Fold D).

**One feature PR merged this session** (Option C from S2997 close — Fold D re-dispatch guard; backend-only).

**PR #3666 (`d3ab2e889`) — v2 Fold D from S2997: send-to-rigby refuses re-dispatch by default; force=true escape hatch.** Closes the footgun I hit during S2997 A2 SIGN. **409 Conflict** when `finding.deliverable_id` is set AND request body doesn't include `{"force": true}`. **Strict boolean check** — truthy strings/integers rejected (`force is True` only). Response payload includes `existing_deliverable_id` so callers can navigate to what was already produced. `force=true` replaces `finding.deliverable_id` + emits WARNING log for audit. Old deliverable left as orphan (caller-driven cleanup). Frontend already dispatch-safe via S2995 hotfix; this is defense-in-depth for direct API / PA-tool / bulk-op paths. 11 new tests + 84 pre-existing green. Rigby A2 SIGN via real APIClient double-dispatch: Attempt 1 (fresh) → 201, Attempt 2 (no body) → 409, Attempt 3 (`"true"` string) → 409, Attempt 4 (`True` boolean) → 201 (but see Fold A below).

**HEAD at close:** `d3ab2e889` + docs cascade PR (this file + handoff + wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`). Recycle-all clean at `sha=d3ab2e8891c2` post-PR-#3666 (backend-only, frontend rebuild skipped correctly).

Full context:
- `docs/handoffs/SESSION_2998_SEND_TO_RIGBY_REDISPATCH_GUARD.md`
- `docs/handoffs/SESSION_2997_STALENESS_AC_INJECTION_V2_ITEM_8.md` (prior)

---

## S2999 primary directive — v2 arc is 10-of-12 done; three natural next paths

**The findings-surface v2 arc daily pipeline is defense-in-depth complete.** Only #5-cookies and #7 remain as v2 items. Three natural continuation paths:

### Option A — v2 item #7: F-A2-equivalent for downstream consumers (~30–60 min, backend)

Verify that consumers referenced in Deliverable acceptance criteria actually exist (mirrors the S2989 F-A2 citation-path allowlist but for the downstream side). Consumes the S2995 `_check_staleness_at_head` helper directly.

### Option B — v2 item #5 cookies half: `web_fetch_tool` session cookies (~1 session, backend + security)

Rigby's HTTP-shape verification of backend endpoints keeps hitting 401. **3rd trigger** at S2997. Larger design change; needs security review. Every time I want Rigby to verify an endpoint post-merge, I have to fall back to APIClient — which means she can't run real curl-shape smoke on the production surface she's supposed to demonstrate.

### Option C — Pivot to fresh arc

The v2 arc daily loop is complete. Chris may want to open a new arc (MEMORY `project_2100_plus_queue_ranking` suggests 2100 RAG / 2200 Frontend / 2300 Mobile / 2400 Auth / 2500 API / 2600 PA).

### Ordered follow-on priorities (dependency-aware) after choice
4. **Fold A (S2998) `future_trigger` — force=true × factory dedupe semantic mismatch.** Two future shapes: split into `force_guard=true` vs `force_new_deliverable=true` flags, OR add `dedupe_mode=<enum>` param. Doc-first per Rigby A2 advice. Only ship polish if operator friction surfaces.
5. **Fold C (S2997) `future_trigger` — dedupe strictness (`(ref, verb)` deterministic key).**
6. **Fold F (S2997) — `orm_inspect_tool` JSON-path lookup support** (Rigby Tool Gap Ledger).
7. **Executable-prompt tightening (S2993 Fold C future_trigger).**
8. **Rigby Tool Gap Ledger — dry-run preview endpoint for send-to-rigby (S2993 Fold B).**
9. **Rigby Tool Gap Ledger — backend-ahead-of-UI pattern watch (S2994 Fold D).**
10. **Rigby Tool Gap Ledger — metadata accretion governance (S2995 Fold E).**
11. **Rigby Tool Gap Ledger — per-row Recheck button on FindingsTab (S2996 Fold E).**
12. **Rigby Tool Gap Ledger — dedupe/override semantic mismatch (S2998 Fold C).**
13. **Toast staleness reinforcement (S2996 Fold C future_trigger).**
14. **Deliverables-tab type badge (S2994 Fold C future_trigger).**
15. **Staleness metadata → dedicated `staleness_detail` JSONField (S2995 Fold C future_trigger).** Trigger: metadata grows beyond one list of refs.
16. **Periodic staleness beat schedule (S2995 Fold D future_trigger).** Trigger: UI surface exists — now met.
17. **WorkspacePageNew param preservation (S2995 hotfix Fold F future_trigger).**

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read the S2998 handoff in full — especially the 3-fold classification block + real double-dispatch A2 SIGN evidence.
4. Optional pre-response state probes:
   - `git log --oneline -6` — should show docs cascade → `d3ab2e889` (PR #3666) → `b65418425` (S2997 close) → `28c8547b0` (PR #3664) → `c315aa4fc` (PR #3663) → `060cc49fb` (S2996 close).
   - Rigby ORM-verify: `orm_inspect_tool action=filter model=DocResearchFinding filters={"id":"00a142f2-b284-4ec4-a5de-d9b3955e548a"} limit=1 fields=id,deliverable_id` — should show `deliverable_id=9f617505-...` from the S2998 A2 SIGN dispatch.
   - Chris manual smoke (optional): `curl -X POST -b <session-cookie> "http://localhost:8000/api/repo/doc-research-findings/00a142f2-.../send-to-rigby/"` should return 409 with `reason_code=deliverable_already_exists`.

**Suggested first-turn shape for S2999:** ask Chris "A, B, or C?" — A is small and closes the last non-cookie v2 item; B is bigger but the pain is now 3rd trigger; C depends on Chris's readiness. Recommendation weight: **A > B > C** (finish v2 last item, then decide on B or fresh arc).

---

## S2999 carry-forward seeds (Chris picks whether to open — not gated on the v2 arc)

### New carry-forward from S2998

- **Fold A `future_trigger` — force=true × factory dedupe interaction.** `force=true` bypasses finding-level guard but `deliverable_factory.create_deliverable` has 4h title-dedupe + 72h content-hash-dedupe. Within window, same finding → same spec → dedupe returns existing deliverable. Not a bug (dedupe = cost-control) but a semantic mismatch: "force" past guard vs "force" new deliverable. Doc-first; ship polish only if operator friction surfaces. Two shapes to consider: split into `force_guard=true` vs `force_new_deliverable=true`, OR `dedupe_mode=<enum>`.
- **Fold B `future_trigger` — force re-dispatch could emit DeliverableEvent breadcrumb.** Non-destructive mark of OLD deliverable as superseded when force=true creates a new one. Not shipped.
- **Fold C — Rigby Tool Gap Ledger.** Semantic mismatch between endpoint override flag and downstream dedupe policy — footgun class.

### Carry-forward from S2997 (STILL OPEN)

- **Fold B `future_trigger` — dedupe strictness.** Exact-string dedupe on stale-ref ACs is right for MVP; watch for 2nd trigger.
- **Fold F — Rigby Tool Gap Ledger.** `orm_inspect_tool` doesn't support `metadata__<key>=value` JSON-path lookups (only `metadata__has_key`).

### Carry-forward from S2996 (STILL OPEN)

- **Fold A `informational` — 4th trigger on v2 item #5 (`web_fetch_tool` cookies)** — now 4th trigger with S2998 A2 dispatch (had to use APIClient again). Priority climbing further.
- **Fold C `future_trigger` — staleness toast reinforcement.**
- **Fold E — Rigby Tool Gap Ledger (sharpened).** No in-UI action to re-run staleness verification for a single finding from FindingsTab.

### Carry-forward from S2995 (STILL OPEN)

- **Fold C `future_trigger` — staleness metadata → dedicated JSONField.** Watch for 2nd trigger.
- **Fold D `future_trigger` — periodic staleness beat.** UI surface exists (S2996) so now actionable.
- **Fold E — Rigby Tool Gap Ledger.** Metadata accretion governance.
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
- **Contract-lock-in guardrail** — updated set: `close_mode`, `finding_type`, `spec_prompt_shape`, `finding_type_used`, `staleness`, `metadata.staleness_failed_refs`, `metadata.staleness_failed_refs_injected`, `reason_code`.
- **Freshness axis 2nd-trigger clause** (still no 2nd trigger).

### Carry-forward from S2989-S2990 (STILL OPEN)

- **`web_fetch_tool` session cookies** — see Option B above (4th trigger this session).
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
- **Spec→ship contract:** PLAYBOOK-7.7.1. S2998 was Flow B (Option C directive from S2997 close).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations mandatory). T1 SIGN used rationale-driven verdicts (no tool_run needed — spec was deterministic). A2 SIGN used real APIClient double-dispatch producing verifiable HTTP status codes + Rigby independently ran `orm_inspect_tool filter` on both finding and deliverable to confirm persistence.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. No new decision required.
- **Cross-repo application:** PLAYBOOK-7.7.4. Not exercised.
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` after each merge. Backend-only diff → frontend rebuild skipped correctly.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — Real APIClient dispatch verified guard behavior BEFORE Rigby A2 SIGN. **Fold A only surfaced because I used a real fresh finding** — the S2998 test fixture used a fake existing_deliverable_id UUID that doesn't hit the factory dedupe path.
- **`feedback_zoom_out_ask_per_rigby_sign`** — A2 zoom-out surfaced Fold A (documentable, not polish-worthy per Rigby). Doc-first outcome ≠ polish-PR outcome; both are valid A2 SIGN patterns.

---

## Wrapper pin note

The active PA conversation pin at S2998 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S2998 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S2998 was Flow B; the A2 SIGN pattern of "real dispatch surfaces folds that framing didn't" is now a repeating shape (S2996 hit 401 revealing #5-cookies pain; S2997 A2 revealed placement fold; S2998 A2 revealed factory-dedupe interaction). All three shipped clean because the pattern is: A2 SIGN via real ops → Rigby zoom-out classifies the fold → either same-session polish OR doc-first `future_trigger`. Worth watching for a 4th instance to consider whether this deserves a Playbook rule around "A2 SIGN real-ops must precede close cascade" (soft rule; currently just PLAYBOOK-7.7.2 SIGN evidence discipline).
