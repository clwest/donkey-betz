# Next Session — Start Here

---

## READ THIS FIRST — SESSION 3000 CLOSED. **v2 arc 12-of-12 COMPLETE.** web_fetch_tool user_auth shipped.

**One feature PR merged this session** (v2 item #5 corrected scope; backend-only).

**PR #3670 (`39a6a9c97`) — v2 item #5 (corrected scope): `web_fetch_tool` gains `use_user_auth`.** Chris asked before opening Option A: "what's actually wrong? Should we investigate first?" That instinct broke a 5-session mislabel. Carry-forward called it "web_fetch_tool session cookies" — actual gap was smaller: handler already had `user_id`, just never used it to look up the user's DRF Token. `use_user_auth: bool = False` new schema param; when True + `user_id` present, look up token via `Token.objects.filter(user_id=user_id).first()` and inject `Authorization: Token <key>`. Explicit override wins (case-insensitive header check). Fail-open if no token row. ~5-10 LOC net, ~30 min end-to-end.

**Historic A2 SIGN:** Rigby dispatched `web_fetch_tool` with `use_user_auth=true` against `/api/repo/doc-research-findings/?staleness=suspected` — **HTTP 200**, body contained all 4 known-suspected finding IDs (`56851590-...`, `e386eb18-...`, `956f8571-...`, `7d5f6797-...`). First A2 this entire arc where Rigby verified a backend endpoint without me falling back to APIClient.

**v2 sequence COMPLETE (12-of-12):** #1 close_mode / #2 finding_type / #3 prompt branching / #4 staleness detector + UI / #5 orm_inspect + web_fetch_tool auth / #6 UI nudge + View-deliverable hotfix / #7 downstream consumer verify / #8 stale-ref AC injection / S2997-Fold-D re-dispatch guard.

**HEAD at close:** `39a6a9c97` + docs cascade PR (this file + handoff + wrapper pin bump per `feedback_commit_wrapper_pin_bump_at_close`). Recycle-all clean at `sha=39a6a9c97bfe` post-PR-#3670.

Full context:
- `docs/handoffs/SESSION_3000_WEB_FETCH_TOOL_USER_AUTH_V2_ITEM_5.md` — includes the scope-mislabel post-mortem
- `docs/handoffs/SESSION_2999_AC_CONSUMER_VERIFIER_V2_ITEM_7.md` (prior)

---

## S3001 primary directive — v2 arc COMPLETE, pivot decision

**The findings-surface v2 arc is fully drained.** Every item shipped. Multiple natural next-arc candidates:

### Option A — Open a fresh research arc

Chris's own queue proposal (MEMORY `project_2100_plus_queue_ranking`): 2100 RAG / 2200 Frontend / 2300 Mobile / 2400 Auth / 2500 API / 2600 PA. Pick one and open.

### Option B — Drain some of the accumulated fold ledger

10+ ledger candidates + future_triggers accumulated over the v2 arc. Small backend items (~30-60 min each) that would tidy up the platform:
- Fold F (S2997) — `orm_inspect_tool` JSON-path lookup support (`metadata__<key>=value`)
- Fold A (S2998) — force=true × factory dedupe semantic mismatch (split flags or dedupe_mode enum)
- Fold B (S2997) — dedupe strictness `(ref, verb)` deterministic key
- Fold C (S2996) — staleness toast reinforcement
- Fold C (S2994) — Deliverables-tab type badge
- Fold F (S2995 hotfix) — WorkspacePageNew param preservation

### Option C — Formalize an emergent pattern into a Playbook amendment

S3000 Fold A surfaced a candidate rule: "Before carrying forward an investigation as a multi-session blocker, reproduce the failure at the thinnest interface (PA tool / HTTP call) and enumerate the missing affordance precisely." 1st concrete instance this session; not yet 2-trigger threshold for amendment. Watch, don't amend.

### Option D — Chris's own priorities

Chris may have work outside the v2 arc that's been queued. Ask.

**Standard opener:**
1. Run `context-kit orient` (auto-injected).
2. Absorb this file + MEMORY.md + CLAUDE.md.
3. Read the S3000 handoff in full — especially the scope-mislabel post-mortem and the v2 arc COMPLETE marker.
4. Optional pre-response state probes:
   - `git log --oneline -6` — should show docs cascade → `39a6a9c97` (PR #3670) → `2c3688817` (S2999 close) → `d48ddc493` (PR #3668) → `29ee89a3a` (S2998 close) → `d3ab2e889` (PR #3666).
   - Rigby web_fetch_tool self-test: dispatch `web_fetch_tool` with `use_user_auth=true` against any internal endpoint — should return 200 (regression check on S3000).

**Suggested first-turn shape for S3001:** ask Chris "A (fresh arc — which?) / B (drain ledger — pick 1-2) / D (your priority)?" — v2 arc is done, opening decision is genuinely Chris's. Recommendation weight: **D > A > B > C** (Chris probably has work in mind after 10 sessions of v2; if not, fresh arc is more valuable than ledger drain).

---

## S3001 carry-forward seeds

### New carry-forward from S3000

- **Fold A `informational` — potential Playbook rule candidate.** "Reproduce the failure at the thinnest interface before naming the carry-forward." 1st concrete instance. Watch for 2nd before proposing Playbook amendment.
- **Fold B `informational` — residual APIClient-forcing shapes.** Even with `use_user_auth`: (i) CSRF + session-cookie endpoints; (ii) multipart/form-data uploads; (iii) OAuth redirects; (iv) non-JSON POST bodies. None blocking; log for future arcs.
- **Fold C — Rigby Tool Gap Ledger entry CLOSED by S3000 PR.** Original gap "PA HTTP fetch couldn't hit auth-protected internal endpoints" resolved.

### Carry-forward from S2999 (STILL OPEN)

- **Fold B `active watch` — metadata accretion governance.** 4 detector keys currently. Trigger: 5+ keys OR 2+ independent consumers.
- **Fold C — Rigby Tool Gap Ledger.** File:line-only scope of consumer verifier — expectation-setting.

### Carry-forward from S2998 (STILL OPEN)

- **Fold A `future_trigger` — force=true × factory dedupe semantic mismatch.**
- **Fold B `future_trigger` — force re-dispatch could emit DeliverableEvent breadcrumb.**
- **Fold C — Rigby Tool Gap Ledger.** Semantic mismatch between endpoint override flag and downstream dedupe policy.

### Carry-forward from S2997 (STILL OPEN)

- **Fold B `future_trigger` — dedupe strictness on stale-ref ACs.**
- **Fold F — Rigby Tool Gap Ledger.** `orm_inspect_tool` doesn't support `metadata__<key>=value` JSON-path lookups.

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
- **Contract-lock-in guardrail** — updated set: `close_mode`, `finding_type`, `spec_prompt_shape`, `finding_type_used`, `staleness`, `metadata.staleness_failed_refs`, `metadata.staleness_failed_refs_injected`, `metadata.unverified_consumer_refs`, `reason_code`, **`use_user_auth`**.
- **Freshness axis 2nd-trigger clause** (still no 2nd trigger).

### Carry-forward from S2989-S2990 (STILL OPEN)

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

- **Constitutional governance chain:** CLAUDE.md constitutional blockquote (Playbook v0.10.0). No amendments this session. **Candidate seed:** S3000 Fold A "reproduce at thinnest interface" — watch for 2nd trigger.
- **Spec→ship contract:** PLAYBOOK-7.7.1. S3000 was Flow B with an investigation phase INSERTED before T1 SIGN because Chris challenged scope framing. Investigate → recommend scope → Chris ratifies → code → ship — a valid variant of the pattern.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. T1 SIGN skipped (design fully deterministic after Chris ratification). A2 SIGN was the strongest of the arc — Rigby used her own newly-shipped tool end-to-end.
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Chris's investigation ask was itself a decision route ("A or investigate first?"). Investigate-first delivered corrected scope + smaller ship in less time.
- **Close-ceremony PR discipline:** PLAYBOOK-7.4.1 through 7.4.4.
- **Recycle discipline** (S2978 refinement to PLAYBOOK-7.4.4): backend-only diff → frontend rebuild skipped correctly.
- **`feedback_verify_at_raw_orm_before_trusting_tool_no_data`** — this session's spiritual cousin: verify at raw CODE before trusting your own carry-forward framing. The T1 SIGN convention emphasizes tool-based verification of assumptions; S3000 showed that assumption-verification should also cover carry-forward LABELS, not just framing content.
- **`feedback_zoom_out_ask_per_rigby_sign`** — A2 zoom-out surfaced the rule-worthy pattern (Fold A) that would have been invisible from a "small win" narrative. Continuing to pay off across the arc.

---

## Wrapper pin note

The active PA conversation pin at S3000 close is minted by `session_lifecycle close` at close time and the wrapper `tools/pa_local.sh` rewritten atomically. Commit the wrapper diff in the S3000 close cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional. S3000 is a milestone.** 10-session Flow B arc (S2991–S3000) shipped 12 v2 items end-to-end, plus 1 S2994 hotfix, 1 S2997 polish PR, and now 1 scope-mislabel-correction PR. Every ship followed PLAYBOOK-7.7.1 shape with real-tool T1 SIGN and real-ops A2 SIGN. The pattern's biggest single validation was S3000: Chris's "investigate first" instinct converted a mislabeled ~1-session carry-forward into a ~30-min ship, AND Rigby's own tool surface now verifies the fix end-to-end without APIClient fallback. Whatever S3001 opens, this arc has trained a strong close-loop-with-real-ops muscle.
