# Session 3033 — Engineering Playbook v0.11.0 RATIFIED

**Date:** 2026-07-28 · **HEAD at close:** PLACEHOLDER (filled at merge)

## What shipped

**Playbook v0.11.0 ratified.** 1 new [GR] rule PLAYBOOK-7.7.5 codifies the "A2 zoom-out sweep for drift/hardening class of change" pattern into constitutional governance. Version bump: v0.10.0 → v0.11.0 MINOR. Rule count: 211 → 212.

### The rule (PLAYBOOK-7.7.5 — condensed)

When a spec→ship T1 plan (per PLAYBOOK-7.7.1 Phase 2) declares its Substantive Intent as either (a) **drift-class closure** or (b) **hardening-class**:

- **Phase 2 plan MUST name the *shape signature* being closed** — an exact query predicate, ORM filter, function name, decorator, or field invariant sufficient for a mechanical repo-wide sweep.
- **Phase 7 A2 SIGN routing MUST include a repo-wide zoom-out sweep** enumerating, at minimum:
  1. Other production sites of the same shape signature (grep/AST/ORM query for the exact shape named).
  2. Adjacent classes with structurally similar risk, bounded to *same table/model OR same workflow stage OR same consumer boundary* — reviewer states axis inline.
  3. Downstream consumers of the changed invariant that would silently miss or misinterpret rows.
  4. Tests that lock in the old behavior and would fail-in-reverse.
- The (i)–(iv) enumeration is a **MINIMUM floor**; additional dimensions MAY be added.
- Sweep MUST be executed via `tool_runs` per PLAYBOOK-7.7.2 with results inline in the A2 attestation.
- A **clean sweep is first-class evidence of class closure**, not a null result.
- A sweep finding ≥1 previously-unknown site MUST fold back to Phase 6 for same-PR incorporation OR forward-carry with named trigger condition.

**EXTENDS:** PLAYBOOK-7.7.2 (SIGN evidence discipline) + PLAYBOOK-6.10.7 (joint SIGN zoom-out ask).

### Amendment PR

Shipped as single close-ceremony bundle per PLAYBOOK-7.4.1:
- `docs/ENGINEERING_PLAYBOOK.md` — frontmatter version bump + Chapter 7 stub refresh + new §7.7.5 body + §7.8 cross-refs
- `docs/research/implementation/RATIFICATION_2026-07-28_PLAYBOOK_V0_11_0.md` — full amendment provenance envelope (8 sections)
- `logs/zoom_out_classifications.jsonl` — Rigby T1 zoom-out fold persisted (backfilled per §6 constitutional-debt note; graceful-degradation precedent from v0.9.0)
- `CLAUDE.md` — constitutional-governance blockquote refresh with v0.11.0 anchor + ancestry line refresh + Last Updated line
- `00-START-NEXT-SESSION.md` — S3034 opener
- `docs/handoffs/SESSION_3033_PLAYBOOK_V0_11_0_RATIFIED.md` — this handoff

## Evidence — 3-cycle in-wild corpus

| Cycle | Session | PR | SHA | Sweep outcome | §Fold C classification |
|-------|---------|-----|-----|---------------|------------------------|
| 1st | S3029 | #3747 | `d0841a0f6` | **DISCOVERY** — 4th silent site in `core/tasks_ops.py:_impl_auto_approve_boardroom_items` caught (4 bulk `.update(status='canonical')` calls that PR #3746 missed) | `1st trigger` — codify A2-zoom-out-sweep pattern, watch for 2nd |
| 2nd | S3030 | #3749 | `e7fc79282` | **CLEAN** — 7 `repo_tool` searches: no lingering `.update(status='canonical')`, no kwargs-shape hiding, no adjacent `published/is_published` drift, no filter collision | `2nd cycle, no discovery` — pattern useful even when nothing found |
| 3rd | S3031 | #3751 | `d7bb28b4f` | **CLEAN** — 8 `repo_tool` searches: no other `promote_to_canonical` callers, no ungated broadcast callers, no `updated_at`-dependent consumers | `3rd cycle, no discovery` — arguably ready to codify with "clean-sweep-confirms-closure" framing |

**Codification threshold judgment:** the "clean-sweep-as-evidence" signal is a distinct codification pressure from "catches adjacent silent bug" — requiring only the latter would bias toward codifying gotchas that keep biting while missing rules whose value is *preventing misses*. Rigby T1 D2 AGREE.

## Rigby SIGN quality this session

**1 substantive T1 SIGN cycle. Tool-grounded (6 `repo_tool` operations inline). Zero hallucination.** **19-session zero-hallucination Rigby SIGN streak** (S3010 → S3033).

**Per-dimension verdicts:**

- **D1 Rule text clarity + normativity — AGREE** (with 1 `same_pr_mitigatable` — clarify "adjacent classes" boundary). Tool support: TR-4/5 anchored parent-rule framing. Ambiguity flagged; mitigation applied.
- **D2 Evidence sufficiency — AGREE**. Tool support: TR-1/2/3 confirmed 3-cycle handoff record. Hedge appropriately captured; no fold raised. Reasoning: requiring 2nd discovery would bias toward "gotchas that keep biting."
- **D3 Scope containment — AGREE**. Tool support: TR-4 confirmed §7.7 scope. §7.7.5 stays inside spec→ship contract, no general-PR legislation.
- **D4 EXTENDS discipline — AGREE**. Tool support: TR-5 confirmed 6.10.7/6.10.8 shapes. Both EXTENDS hold; no SUPERSEDE risk.
- **D5 Insertion + version-bump — AGREE**. Tool support: TR-4 confirmed clean slot. MINOR v0.10.0 → v0.11.0 matches prior single-rule cadence (v0.6.0/v0.7.0/v0.8.0).

**Zoom-out fold — `same_pr_mitigatable`.** (i)–(iv) risks ritualization if "shape being closed" isn't well-defined; adjacent-class boundary subjective. Four mitigations applied same-envelope at authoring:
1. **Shape signature naming** — Phase 2 plan MUST name exact predicate/filter/function/decorator/invariant.
2. **Adjacent-class boundary** — bounded to *same table/model OR same workflow stage OR same consumer boundary*; reviewer states axis inline.
3. **"At minimum" prefix** — (i)–(iv) explicitly framed as MINIMUM floor, not exhaustive.
4. **Clean-sweep-first-class explicit sentence** — added so future reviewers don't treat zero-findings as inadequate evidence.

## Chris D-verdict

Presented via Phase 5 plain-English framing per PLAYBOOK-7.7.3:
- **Do we lose anything?** No.
- **Is it more work later?** Yes if skipped.
- **≤1 decision:** ship or push back.

Chris verdict: **"ship it"**. RATIFIED 2026-07-28 S3033.

## Folds (pattern evidence)

### Fold A `same_pr_mitigatable` — Rule-text refinement (RESOLVED same-envelope)

See Rigby T1 zoom-out above. All four refinements folded at authoring. Persisted to `logs/zoom_out_classifications.jsonl` under arc `playbook_v0_11_0_a2_sweep_drift_hardening`. No forward carry.

### Fold B `procedural observation` — ledger persistence timing

Ledger `record_zoom_out_concern` call ran POST Chris D-verdict rather than BEFORE (PLAYBOOK-6.10.8 requires classify+persist before D-verdict is requested; graceful-degradation clause permits deferral only for tool failure, which did not occur). Backfilled inside ship bundle same-envelope per v0.9.0 §4.3 backfill precedent. Recorded as §6 constitutional-debt note in envelope, not as CD entry. **Watch for 2nd trigger** to determine whether a PLAYBOOK-6.10.8 sequencing sub-rule is warranted.

## Cycle 1A verify-before-build wins

**18th consecutive session.** Verify pass before dispatching T1 SIGN: read S3029/S3030/S3031 handoffs to confirm exact Fold C classifications + evidence SHAs; read Playbook §6.10.7 + §6.10.8 + §7.7 body to confirm EXTENDS relationships and insertion point; grep for rule-ID collisions; confirmed 3 evidence SHAs resolve via `git log`.

## Forward carries

### New from S3033

- **Fold B `procedural observation` — ledger persistence timing** — see above. Watch for 2nd trigger.

### Carried from S3032 (STATUS PRESERVED)

- **S3030 prod deploy carry** — still open: run `python manage.py backfill_canonical_drift --apply` against Railway prod when convenient (S3030 carry).
- **S3032 Fold E `2nd cycle, non-blocking accretion evidence`** — `orm_inspect_tool` allowlist growth pattern (7 accretion PRs since S2866, 18 entries). If N+2 more accretion PRs land in short succession, revisit periodic-sweep RFC.
- **S3031 Fold A `2nd trigger` (bool-return semantics discipline)** — carried unchanged.
- **S3031 Fold B `informational` (spy fragility)** — carried unchanged.
- **S3031 Fold D — RESOLVED at S3032**.

### Carried from S3029 → S3026 (STATUS PRESERVED)

- **S3026 Fold A `1st trigger`** — evidence-driven investigation. S3033 T1 SIGN is additional supporting evidence (Rigby T1 grounded in 6 `repo_tool` searches).
- **S3026 Fold B `informational`** — spec-invalidation watch.
- **S3026 Fold C `informational`** — `learning_reason` bare-string typing.
- **Design-arc candidate** — KnowledgeTransfer model realignment.

### Carried from S3025 / S3024 / older — all preserved from S3032 close 00-START.

## Cross-cutting workflow references

- **Constitutional governance chain:** CLAUDE.md Playbook v0.11.0 (this session's amendment).
- **ADR corpus:** ADR-0001 through ADR-0008 unchanged.
- **Spec→ship contract:** PLAYBOOK-7.7.1. **1× Flow A meta-spec→ship** this session — the Playbook amendment itself walked the 9-phase contract (Phase 1 spec receipt from S3031 forward-carry; Phase 2 verified premises via handoff reads; Phase 3 T1 SIGN; Phase 4 verdict processing + same-envelope refinements; Phase 5 Chris plain-English framing; Phase 6 implement — Playbook body + envelope + handoff + 00-START + CLAUDE.md; Phase 8 ship; Phase 9 close cascade). Amendment self-satisfies §7.7.1.
- **SIGN evidence discipline:** PLAYBOOK-7.7.2. **1× substantive T1 SIGN, 6 tool_runs inline. Zero rubber-stamp. 25 sessions continuous.**
- **Chris-facing decision framing:** PLAYBOOK-7.7.3. Applied at Phase 5 with (a) do we lose anything (b) more work later (c) ≤1 decision framing.
- **Recycle discipline (PLAYBOOK-7.4.4):** `make recycle-all` once post-merge; SHA recorded in `logs/recycle_events.jsonl`.
- **Fold classification (PLAYBOOK-6.10.8):** 1 fold `same_pr_mitigatable` (mitigated same-envelope, persisted post-D-verdict per graceful-degradation) + 1 fold `procedural observation` (Fold B — sequencing observation carried forward for 2nd trigger).
- **Verify-before-build (Cycle 1A):** 18th consecutive session — 3-handoff read + Playbook §7.7 body read + PLAYBOOK-6.10.7/6.10.8 grep + evidence-SHA `git log` verify before T1 dispatch.

## Wrapper pin note

Session-open pin was `pa-2ee8194337d14c2c` (minted at S3032 close). Close mints next pin; wrapper diff committed per `feedback_commit_wrapper_pin_bump_at_close`.

## What this amendment teaches about how to do amendments

1. **Three cycles of a workflow-shape pattern is a valid codification threshold when at least one cycle is a discovery.** The v0.9.0 amendment codified test-authoring rules from two triggers; v0.11.0 codifies a session-shape rule from one discovery + two clean sweeps. Distinct evidence class: workflow-shape rules can be validated by "clean sweeps continuing to hold" in a way that content-shape rules cannot.
2. **`same_pr_mitigatable` folds at T1 can reshape rule text without a T2 SIGN cycle** when the refinements are textual clarifications of the same normative content rather than scope changes.
3. **Ledger persistence timing matters for the constitutional record even when the D-verdict is uncontested.** PLAYBOOK-6.10.8's "persist before D-verdict" is a provenance-integrity rule. Backfill-inside-envelope preserves the record but changes the sequence; the graceful-degradation clause was written for tool failure, not for author oversight. Fold recorded pending 2nd trigger.
