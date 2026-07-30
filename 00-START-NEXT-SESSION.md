# Next Session — Start Here

---

## READ THIS — SESSION 3041 CLOSED. **Ledger reconciliation + Option B meta-fix shipped in-session.**

S3041 opened planning a T1 spec for Ledger #5 fix; verify-before-build caught that the fix already shipped at S2938 (PR #3512). Downstream 7-entry sweep found #16 also stale (shipped at S2941 PR #3517). Both flipped in the ledger deliverable. Meta-fix (Option B) then shipped same-session per Chris directive ("if we can fix it now, let's address it while you have context"): new `core/services/ledger_reconciliation.py` substrate + standalone command + `session_lifecycle close` integration + 26 tests all pass. Rigby A2 SIGN AGREE 4/4 dimensions per PLAYBOOK-7.7.5.

**HEAD at close:** _(filled by close cascade)_

### PRs shipped this session

- **PR #_TBD_ (`_TBD_`)** — `feat(s3041): ledger reconciliation meta-fix — flip #5 + #16, ship Option B substrate`. Ledger deliverable status flips + new substrate module + command + close integration + 26 tests.

### Signals gathered

- **Verify-before-build caught 3 stale premises this session.** Slice 6 already done + Ledger #5 already shipped + Ledger #16 already shipped. 26th consecutive Cycle 1A session.
- **PLAYBOOK-7.7.1 abort-early clause fired cleanly.** First in-wild instance since v0.10.0 ratification (Ledger #5 T1 spec aborted at Phase 1 when Substantive Intent verification exposed spec-invalidation).
- **PLAYBOOK-7.7.5 class-scoped A2 sweep fired.** Option B build is drift-class closure; shape signature named + Rigby 4-dimension sweep AGREE with tool_runs per 7.7.2.
- **Meta-fix hit 4 triggers same-session (S2931 + S2942 flag + S3041 #5 + S3041 #16); Chris D-verdict ship-now not park.** Sets a cadence precedent: promote-to-code within the same session where recurrence is caught.

---

## S3042 primary directive — UI Workspace re-coherence arc (Step 3 of the S3040 sequence)

**Chris ratified at S3040 close (and unchanged this session): three-step arc = PA tools sweep → Rigby Tool Gap → UI Workspace.** Steps 1 + 2 closed at S3041. Step 3 now.

### Step 3 substrate (do NOT re-do)

The archaeology is already done and preserved as deliverable `7c5bc04d-6976-4f70-9c25-de373613023b` in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`. The 3 coupled questions are named:

1. **Is Workspace a filesystem boundary or a scoping lens?** (Today: both, uncomfortably.)
2. **Are Initiatives autonomous or manual?** (Today: manual, but originally autonomous.)
3. **Are Deliverables initiative outputs or standalone publish-control units?** (Today: standalone, drifted.)

The arc has both a **model side** (answer the 3 questions → decide shape) and a **UI side** (redo the Workspace UI per Chris directive). Sequence: model decisions first, then UI redo lands on top.

### Suggested S3042 opening move

1. Read the archaeology deliverable in full — do not summarize from CLAUDE.md alone.
2. Route to Rigby a scoping SIGN: which of the 3 questions is highest-cash-flow-leverage to answer FIRST? Rigby has evidence-side context (which deliverables/initiatives are currently in-flight vs abandoned) that Claude reading code alone can't infer.
3. Chris D-verdict on scoping answer → open T1 spec for the chosen sub-arc.

### Meta-fix dogfooding note

`session_lifecycle close` now supports `--handoff <path>` to enforce ledger reconciliation. S3042 close cascade should exercise it: pass `--handoff docs/handoffs/SESSION_3042_*.md`. If S3042 references any `Ledger #N` in its handoff, the ledger deliverable must have a matching `Ledger #N status flip` block, OR pass `--allow-ledger-drift`.

### Standard opener for S3042

1. `context-kit orient` (auto-injected)
2. Absorb this file + `MEMORY.md` + `CLAUDE.md`
3. Read S3041 handoff (`docs/handoffs/SESSION_3041_LEDGER_RECONCILIATION.md`)
4. `git log --oneline -8` — should show S3041 close cascade at top
5. Read archaeology deliverable `7c5bc04d-6976-4f70-9c25-de373613023b`
6. Route Rigby the scoping SIGN (which of the 3 W/D/I questions goes first)

---

## S3042 carry-forward seeds

### New from S3041

- **Meta-fix substrate shipped.** `core/services/ledger_reconciliation.py` + `core/management/commands/check_ledger_reconciliation.py` + `session_lifecycle close --handoff / --allow-ledger-drift` integration + 26 tests.
- **PLAYBOOK-7.7.1 abort-early clause** — first in-wild instance shipped in a handoff record. If it fires again next arc, that's a 2nd trigger for potential codification refinement.
- **Verify-at-code-before-trusting-doc-status pattern** — 1st explicit trigger (via 3-instance same-session cluster). Adjacent to `feedback_verify_at_raw_orm_before_trusting_tool_no_data`; watch for 2nd trigger.
- **Regex convention drift risk** — `Ledger #N` only; `ledger row #N` / `Entry #N` won't match. Watch for 2nd trigger before Shape D promotion.

### Parked / conditional (unchanged from S3040)

- **Odds API operationally degraded** — 2 periodic tasks `enabled=False`. Re-enable via ORM update if Odds API key renewed.
- **Silent-success bug in `_impl_generate_daily_betting_brief`** — noted, not fixed (task disabled). Re-open if re-enabling betting brief.
- **S9 producer follow-up** (~30 files) — parked; available anytime.
- **A6 Phase 2** — WAIT-STATE, no trigger this cycle.
- **D10 Phase 2** (conditional) — actual historical workspace backfill IF post-fix windows don't show `pa_workspace_lost` bucket evaporating.

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

- **Constitutional governance chain:** CLAUDE.md Playbook **v0.11.0**. S3041 was one substrate spec→ship arc (Option B / ledger reconciliation) with abort-early clause fired at Phase 1 for the initially-planned Ledger #5 arc. No amendments this session; no [GR] rule firings for methodology change.
- **ADR corpus:** ADR-0001 through ADR-0008 (unchanged).
- **Spec→ship contract (PLAYBOOK-7.7.1):** 1 spec→ship cycle this session (Option B), 1 abort-early (Ledger #5).
- **SIGN evidence discipline (PLAYBOOK-7.7.2):** Rigby A2 SIGN with tool_runs; 4 dimensions AGREE.
- **Class-scoped mandatory A2 sweep (PLAYBOOK-7.7.5):** fired for Option B (drift-class closure); shape signature named + 4 dimensions swept.
- **Chris-facing decision framing (PLAYBOOK-7.7.3):** applied 4 times this session (Step reframe, Option A vs B, Ledger #5 pick, Shape C-refined).
- **Recycle discipline (PLAYBOOK-7.4.4):** N/A (CLI-only code change; no Daphne / Celery / frontend touch).
- **Verify-before-build (Cycle 1A):** **26th consecutive session.** Three independent instances this session.

---

## Wrapper pin note

Active PA conversation pin at S3041 close is minted by `session_lifecycle close` at close time. Commit wrapper diff per `feedback_commit_wrapper_pin_bump_at_close`.

---

**Reminder — the workflow is constitutional.** S3041 closed as one substrate spec→ship arc (Option B / ledger reconciliation Shape C-refined) + one abort-early cycle (Ledger #5, already shipped) + two ledger status flips (#5 + #16). The meta-fix substrate ships at HEAD ready for S3042 dogfooding via `session_lifecycle close --handoff`. S3042 first-action = UI Workspace re-coherence (Step 3).
