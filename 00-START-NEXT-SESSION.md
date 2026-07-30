# Next Session — Start Here

---

## READ THIS — SESSION 3040 CLOSED. **Docs-only cadence pivot: odds api degraded + W/D/I archaeology seeded.**

S3040 opened with the 7am MDT trigger verify + Chris raising the workspace/deliverable/initiative concept-drift concern. Two operational carry-forwards shipped as PR #3778 (docs-only): Odds API marked degraded (2 periodic tasks disabled), W/D/I archaeology preserved as workspace deliverable for the future re-coherence arc. Zero code changes; zero recycle needed.

**HEAD at close:** `02dfbf0b4` (post-PR #3778 merge, docs-only).

### One PR shipped this session

- **PR #3778 (`02dfbf0b4`)** — `docs(s3040): seed carry-forward — odds api degraded + w/d/i archaeology`. Two operational carry-forwards + archaeology deliverable pointer + routine docs/INDEX.md autoregen. No code changes.

### Signals gathered

- **7am MDT trigger fired clean.** Morning brief `certified`, 0.95 confidence, deliverable `54f63f7b…`. All 4 lanes clean, no A6 lane_1 exception → A6 Phase 2 stays WAIT-STATE.
- **Sports betting silent-failure surfaced + triaged.** `generate_daily_betting_brief` returned `status='success'` while nothing landed (Odds API auth dead + NULL constraint on `predictions`). Resolved by disabling the 2 auto-firing periodic tasks.
- **Chris cash-flow signal.** New prioritization: cash flow > sports betting until Odds API key renewed. "Focus on what we have been" = keep the Rigby-substrate + engineering rhythm.
- **W/D/I archaeology.** Deferred formal re-coherence arc per Chris; artifact preserved as deliverable `7c5bc04d-6976-4f70-9c25-de373613023b` so we don't re-do the research when the arc opens.

---

## S3041 primary directive — today's sequenced work arc

**Chris ratified at S3040 close: today's arc = PA tools sweep → Rigby Tool Gap → UI Workspace, in that order.** Not three parallel options — a sequence. Each step gates the next.

### Step 1 — PA tools sweep (starts S3041, ~3–6 sessions)

Resume at **Slice 6 = `td_handlers_content.py`** (6 untested tools) per `project_s2935_resume_pa_tools_sweep`. Then Slice 7 for the 7-tool singleton bucket.

Constraints:
- `project_s2908_batch_4_shape_break_commitment` — batches after S2907 must break from uniform READ_ONLY (mixed-tool-scoped READ_ONLY subset OR gated-write dry_run-only). Slice 6 batches inherit this unless tool shape drives otherwise.
- Slice-doc template + prior slice examples in `docs/audits/pa_tools/`. Last sweep was S2907.

### Step 2 — Rigby Tool Gap ledger review (opens when Slice 6+7 close)

Review the Rigby Tool Gap Ledger in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`, `deliverable_type='engineering_backlog'`) per `feedback_rigby_tool_gap_ledger`. Pick 1–2 highest-leverage gaps for a fix slate.

Rationale: sweep surfaces new gaps; ledger accumulates known ones. Close the loop before moving on.

### Step 3 — UI Workspace re-coherence arc (opens when tool-gap slate ships)

Open the deferred Workspace/Deliverable/Initiative re-coherence arc using the archaeology deliverable `7c5bc04d-6976-4f70-9c25-de373613023b` as the substrate. Do not re-do the archaeology — the 3 coupled questions are already named:

1. Is Workspace a filesystem boundary or a scoping lens?
2. Are Initiatives autonomous or manual?
3. Are Deliverables initiative outputs or standalone publish-control units?

The arc has both a **model side** (answer the 3 questions → decide shape) and a **UI side** (redo the Workspace UI per Chris directive). Sequence: model decisions first, then UI redo lands on top.

### Why this sequence

- **"Focus on what we have been"** (Chris S3040) — Rigby-substrate work is the current rhythm; Slice 6 is the ratified continuation
- **"Cash flow priority"** (Chris S3040) — Rigby's tool surface = A1 SaaS + A4 consulting substrate; every verified tool is a customer path derisked
- **Tool gap review naturally follows sweep** — sweep surfaces gaps, ledger captures them, then triage
- **UI Workspace waits for tool-side confidence** — you don't redo the container until you know what belongs in it; the sweep + gap work sharpens that
- **Archaeology already done** — the Workspace arc can open without a research prelude

### Standard opener for S3041

1. `context-kit orient` (auto-injected)
2. Absorb this file + `MEMORY.md` + `CLAUDE.md`
3. Read S3040 handoff (`docs/handoffs/SESSION_3040_ODDS_DEGRADED_WDI_ARCHAEOLOGY_SEED.md`)
4. `git log --oneline -6` — should show S3040 close cascade + `02dfbf0b4` + S3039 4-PR arc at top
5. Read `project_s2935_resume_pa_tools_sweep` + `project_s2908_batch_4_shape_break_commitment` memories
6. Review `docs/audits/pa_tools/` for sweep-doc template and prior slice examples (S2907 was last one)
7. Open Slice 6 sweep: `td_handlers_content.py` (6 untested tools)

---

## S3041 carry-forward seeds

### New from S3040

- **Odds API operationally degraded** — 2 periodic tasks (`collect-sports-odds-intelligence`, `generate-daily-betting-brief`) `enabled=False` in DB. Ad-hoc callers unaffected (circuit breaker). Reason preserved in `PeriodicTask.description`. **To re-enable:** `PeriodicTask.objects.filter(name__in=['collect-sports-odds-intelligence','generate-daily-betting-brief']).update(enabled=True)`.
- **Silent-success bug in `_impl_generate_daily_betting_brief`** — noted, not fixed (task disabled, no cost). Re-open if re-enabling betting brief.
- **W/D/I archaeology deliverable** — `7c5bc04d-6976-4f70-9c25-de373613023b` in Donkey Betz workspace (`b4503364…`). Read BEFORE opening the deferred workspace-cleanup arc (see `project_donkey_betz_workspace_cleanup_and_ui_redo_deferred`). Do not re-do the archaeology.

### Parked / conditional

- **S9 producer follow-up** (~30 files, thread `was_auto_selected=True` through auto_route consumers) — parked behind today's 3-step arc; available anytime to close the S9 arc completely.
- **A6 Phase 2** — WAIT-STATE, no trigger this cycle. Root-cause `lane_1_platform_readiness` bug once next `morning_brief` failure surfaces with a live exception.
- **D10 Phase 2** (conditional) — actual historical workspace backfill IF post-fix windows don't show the `pa_workspace_lost` bucket evaporating. Watch trend before committing.
- **UI Workspace re-coherence** — no longer deferred; sequenced as Step 3 of today's arc (see primary directive above).

### Carried from prior arcs — status preserved

- **T1 Fold future_trigger (`typing.Literal[actor]`)** — 1st trigger (S3036)
- **A2 Fold future_trigger (actor-taxonomy vs frontend-palette drift)** — 1st trigger (S3036)
- **`did_X` semantics** — 2nd trigger (S3034); watch for 3rd
- **S3033 Fold B** — ledger persistence timing (1st trigger discharged; watch for 3rd)
- **S3030 prod deploy carry** — `backfill_canonical_drift --apply` on Railway prod
- **S3032 Fold E** — `orm_inspect_tool` allowlist accretion
- **S3031 Fold B** — spy fragility
- **S3034 A2 Folds** — subscriber wire-contract fragility + adjacent-axis superseded/experiment

---

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook **v0.11.0**. S3040 was docs-only + operational triage. No spec→ship arcs, no [GR] rule firings, no amendment triggers. PLAYBOOK-7.7.5 did not fire.
- **ADR corpus:** ADR-0001 through ADR-0008 (unchanged).
- **Spec→ship contract (PLAYBOOK-7.7.1):** No spec→ship cycles this session.
- **SIGN evidence discipline (PLAYBOOK-7.7.2):** No SIGN cycles this session (no substantive drift/hardening intent).
- **Chris-facing decision framing (PLAYBOOK-7.7.3):** Applied to Odds API degradation scope + S3041 first-action pick.
- **Recycle discipline (PLAYBOOK-7.4.4):** N/A (docs-only + DB flag flip; beat re-reads automatically).
- **Verify-before-build (Cycle 1A):** **25th consecutive session.** Verified Odds API caller scope before disabling.

---

## Wrapper pin note

Active PA conversation pin at S3040 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S3040 closed as a docs-only cadence pivot with no spec→ship arcs. Two operational carry-forwards + archaeology preserved. S3041 first-action = resume PA tools sweep Slice 6 (Chris ratified at close).
