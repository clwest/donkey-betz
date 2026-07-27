# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2997 CLOSED. Findings-surface v2 item #8 shipped + A2 polish.

**Two feature PRs merged this session** (Option B from S2996 close + Rigby A2 SIGN fold polish, both backend-only).

**PR #3663 (`c315aa4fc`) — v2 item #8: stale-ref AC injection at spec generation.** When a finding has `staleness=suspected` per S2995, `send-to-rigby` now produces a spec deliverable that surfaces the drift call-out. Belt-and-suspenders per Rigby T1 SIGN Ask #2: LLM prompt hint AND deterministic AC prepend. `generate_spec_body` accepts new `staleness_failed_refs` kwarg; `_inject_staleness_acs` prepends one verification AC per failed ref (deduped against LLM output; capped at 8); `_render_spec_markdown` adds a `## Staleness note` section. AC wording differs per prompt_shape (engineering: "supports the claim" / evidence: "supports the evidence assertion"). Extras metadata carries `staleness_failed_refs_injected: bool`. View forwards refs ONLY when `staleness=suspected` — fresh findings don't get spurious injection. 17 new tests + 67 pre-existing green. Rigby A2 SIGN dispatched the real `executor/models.py:271` stale finding via APIClient — produced deliverable `1060ab68-...` with first AC being the prepended verification line, LLM naturally wove complementary verification ACs (belt-and-suspenders paid off), Context section explicitly notes "the citation … failed re-verification at HEAD and must be checked."

**PR #3664 (`28c8547b0`) — Staleness note placement polish (A2 SIGN fold).** Rigby A2 zoom-out (b) flagged that `## Staleness note` rendered AFTER `## Acceptance criteria`, reading as an audit appendix rather than operational context. Moved to sit between `## Context` and `## Open question` so the reader knows "this finding's refs are suspect" BEFORE scanning ACs. Same-session polish PR (S2994→S2995 hotfix precedent).

**HEAD at close:** `28c8547b0` + docs cascade PR (this file + handoff + wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`). Recycle-all clean at `sha=28c8547b086a` post-both-PRs (backend-only, frontend rebuild skipped correctly).

Full context:
- `docs/handoffs/SESSION_2997_STALENESS_AC_INJECTION_V2_ITEM_8.md`
- `docs/handoffs/SESSION_2996_FINDINGS_TAB_STALENESS_SURFACE.md` (prior)

---

## S2998 primary directive — v2 arc is 8-of-8 done except #5-cookies + #7

**The findings-surface v2 arc is functionally complete for daily use.** Chris can audit → ingest classifies + staleness-checks → FindingsTab shows badges/filters → Send to Rigby produces spec with injected verification ACs and Staleness note. Full loop.

Four natural next paths — three "close the last v2 items" + one "pivot":

### Option A — v2 item #7: F-A2-equivalent for downstream consumers (~30–60 min, backend)

Verify that consumers referenced in Deliverable acceptance criteria actually exist (mirrors the S2989 F-A2 citation-path allowlist but for the downstream side). Consumes the S2995 `_check_staleness_at_head` helper directly. Same file-existence-at-HEAD pattern.

### Option B — v2 item #5 cookies half: `web_fetch_tool` session cookies (~1 session, backend + security)

Rigby A2 SIGN this session AND S2996 both hit 401s trying to verify backend endpoints. 2nd + 3rd trigger of a growing pain. Larger design change; needs security review (how to safely pass session cookies to a PA tool).

### Option C — Fold D from S2997: send-to-rigby re-dispatch guard (~30 min, backend)

Rigby A2 zoom-out (c). Endpoint currently allows re-dispatch when `deliverable_id` is already set — I had to manually clear it during A2 dispatch, sharp edge. Should refuse by default with a `force=true` escape hatch. Small backend PR.

### Option D — Pivot to fresh arc

The v2 arc's daily loop is complete. Chris may want to open a new arc (see MEMORY `project_2100_plus_queue_ranking` — 2100 RAG / 2200 Frontend / 2300 Mobile / 2400 Auth / 2500 API / 2600 PA).

### Ordered follow-on priorities (dependency-aware) after choice
5. **Fold F (S2997) — `orm_inspect_tool` JSON-path lookup support.** Rigby hit `metadata__<key>=value` unsupported; only `metadata__has_key` works. Rigby Tool Gap Ledger entry.
6. **Executable-prompt tightening (S2993 Fold C future_trigger).**
7. **Rigby Tool Gap Ledger — dry-run preview endpoint for send-to-rigby (S2993 Fold B).**
8. **Rigby Tool Gap Ledger — backend-ahead-of-UI pattern watch (S2994 Fold D).**
9. **Rigby Tool Gap Ledger — metadata accretion governance (S2995 Fold E).**
10. **Rigby Tool Gap Ledger — per-row Recheck button on FindingsTab (S2996 Fold E).**
11. **Toast staleness reinforcement (S2996 Fold C future_trigger).**
12. **Deliverables-tab type badge (S2994 Fold C future_trigger).**
13. **Staleness metadata → dedicated `staleness_detail` JSONField (S2995 Fold C future_trigger).** Trigger: metadata grows beyond one list of refs.
14. **Periodic staleness beat schedule (S2995 Fold D future_trigger).** Trigger: UI surface exists — now met.
15. **WorkspacePageNew param preservation (S2995 hotfix Fold F future_trigger).**

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read the S2997 handoff in full — especially the 6-fold classification block + real-dispatch A2 SIGN evidence.
4. Optional pre-response state probes:
   - `git log --oneline -6` — should show docs cascade → `28c8547b0` (PR #3664) → `c315aa4fc` (PR #3663) → `060cc49fb` (S2996 close) → `12e5400a2` (PR #3661) → `7b4b4adec` (S2995 close).
   - Rigby ORM-verify: `deliverable_tool action=detail id=1060ab68-3dd4-427b-9000-f62e9a615510` — the A2 SIGN evidence deliverable; should show `metadata.staleness_failed_refs_injected: true`, `## Staleness note` section between Context and Open question, first AC = prepended verification line.
   - Chris browser smoke: open FindingsTab, click "Verify evidence" on one of the 4 stale rows, see toast "Evidence-capture deliverable created (…)", then click "View deliverable" — should see `## Staleness note` section BEFORE `## Acceptance criteria` and the first AC = verification line.

**Suggested first-turn shape for S2998:** ask Chris "A / B / C / D?" — C is smallest and closes a real footgun; A is next-smallest and closes the last non-cookie v2 item; B is bigger but the pain is real (3rd trigger); D depends on Chris's readiness to open a new arc. Recommendation weight: C > A > B > D.

---

## S2998 carry-forward seeds (Chris picks whether to open — not gated on the v2 arc)

### New carry-forward from S2997

- **Fold B `future_trigger` — dedupe strictness.** Exact-string dedupe against LLM output is right for MVP. If we see repeated noise, dedupe by `(ref, verb)` deterministic key rather than fuzzy text similarity.
- **Fold D `future_trigger` — send-to-rigby re-dispatch guard.** Option C above. Endpoint should refuse re-dispatch by default with `force=true` escape hatch.
- **Fold E — Rigby Tool Gap Ledger (closed).** "Finding→spec pipeline needs staleness refs to survive into executor-facing ACs + rendered note" — deterministic injection fixed it.
- **Fold F — Rigby Tool Gap Ledger.** `orm_inspect_tool` doesn't support `metadata__<key>=value` JSON-path lookups (only `metadata__has_key`).

### Carry-forward from S2996 (STILL OPEN)

- **Fold A `informational` — 2nd trigger on v2 item #5 (`web_fetch_tool` cookies)** — now **3rd trigger** with S2997 A2 dispatch (I had to use APIClient because Rigby can't hit backend endpoints with auth). Priority climbing.
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

- **Signal-tweak follow-up for `finding_type` classifier** (2 acceptable-misses; combine into single PR if 2nd trigger surfaces).
- **Data-migration-vs-management-command pattern** (3rd-trigger check).

### Carry-forward from S2991 (STILL OPEN)

- **Dry-run counts pattern for future bulk-write migrations** (3rd-trigger check).
- **Contract-lock-in guardrail** on `close_mode`, `finding_type`, `spec_prompt_shape`, `finding_type_used`, `staleness`, `metadata.staleness_failed_refs`, `metadata.staleness_failed_refs_injected`.
- **Freshness axis 2nd-trigger clause** (still no 2nd trigger).

### Carry-forward from S2989-S2990 (STILL OPEN)

- **`web_fetch_tool` session cookies** — see Option B above (3rd trigger this session).
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
- **Spec→ship contract:** PLAYBOOK-7.7.1. S2997 was Flow B (Option B directive from S2996 close). Two PRs shipped: main feature + A2-fold placement polish (same-session, S2994→S2995 hotfix precedent).
- **SIGN evidence discipline:** PLAYBOOK-7.7.2 (tool_runs + line citations mandatory). T1 SIGN used real `orm_inspect_tool` on 1 stale row. A2 SIGN used `deliverable_tool detail` + `orm_inspect_tool filter` on the actual dispatched deliverable produced by a real gpt-5-mini roundtrip.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. No new decision required.
- **Cross-repo application:** PLAYBOOK-7.7.4. Not exercised.
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): `make recycle-all` after each merge. Both PRs backend-only → frontend rebuild skipped correctly via HEAD-range path-diff.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — Rigby A2 Ask #1 used `deliverable_tool detail` to independently verify substrate (metadata flags, section presence, AC ordering).
- **`feedback_zoom_out_ask_per_rigby_sign`** — A2 zoom-out surfaced Fold C `same_pr_mitigatable` that got mitigated same-session via polish PR. Canonical example of the zoom-out ask catching real critique that would otherwise ship as-is.

---

## Wrapper pin note

The active PA conversation pin at S2997 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S2997 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S2997 was Flow B with same-session polish following the S2994→S2995 hotfix pattern. That's now happened 3 times in a row (S2994 hotfix in S2995; S2997 polish; and the pattern where Rigby A2 zoom-out surfaces a `same_pr_mitigatable` fold that gets shipped as a polish PR). If a 4th instance surfaces, worth considering a Playbook rule around "same-session polish PR budget when A2 SIGN surfaces critique of shipped shape."
