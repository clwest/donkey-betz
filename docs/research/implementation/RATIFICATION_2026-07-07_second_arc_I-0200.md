---
title: "IOS Second-Arc Selection Ratification Record — Arc I-0200 (2026-07-07)"
status: active
authority: ratification-record
session_added: 2701
ratification_date: 2026-07-07
ratifier: chris
routing: rigby-pa-chat (per IOS v1.1 §11.2 Step 6 default routing)
selection_sign_pin: pa-6a4e2eff5594486b (ios-arc-open-I-0200-sign-review; retired 2026-07-07 post-Chris-Agree-All)
arc_scoped_pin: pa-1b76ee75adbf4031 (ios-arc-open-I-0200; minted 2026-07-07 at Stage 1 open; covers Stage 1 → Stage 6 arc lifecycle)
paused_research_pin: pa-44a6eb70d8814e34 (T4 Group 1700 Observability — preserved as comment above tools/pa_local.sh --conversation line per §15.14; restored on IOS phase exit)
snapshot_type: contingency-gated-seed (default IB-2199-T0-01 with severability fallback to IB-1999-T0-01; not a static single-arc pick)
supersedes: none (first second-arc ratification; RATIFICATION_2026-07-06_first_queue.md governs backlog band ratification)
superseded_by: (open; will point at any Stage 1 severability-outcome ratification that flips the default seed to the fallback)
frozen: true
---

# IOS Second-Arc Selection Ratification Record — Arc I-0200

This file is the **frozen** canonical record of Chris's ratification of the second implementation arc following Arc I-0100's full close. It captures Claude's mechanical ranking, Rigby's SIGN-with-edits pressure-test, and the Chris disposition per axis. It is append-only history; do NOT edit after commit. Subsequent ratifications (e.g., Stage 1 severability outcome) produce new dated records.

## 1. Context

- **IOS status at ratification:** `active v1.5` on `main` (v1.5 shipped 2026-07-06 via PR #2952 — design-prep first-class artifact rule).
- **Repo HEAD at ratification:** `678a75953190f05e419ac6e31d5204abd78cccb7` (`docs(observability): Arc I-0100 post-close cascade — refresh start-here + docs index/provenance (#2979)`).
- **Prior state:** Arc I-0100 (Observability Correlation Spine + Mission Evidence Substrate) FULLY CLOSED under LOCAL operating model 2026-07-07 (canonical close doc `I-010099_observability_spine_implementation_close.md` in PR #2976). All three T1 intakes terminal: `IB-1799-T1-01` SHIPPED (PR #2954 flag OFF); `IB-1799-T1-02` LOCAL_ACCEPTED / PRODUCTION_DEFERRED (PR #2955 + #2970 + acceptance #2973); `IB-1799-T1-03` LOCAL_ACCEPTED / PRODUCTION_DEFERRED (PR #2957 + #2974 + acceptance #2975). Both runtime flags `RIGBY_DELEGATION_ENABLED` and `PA_AGENT_EXECUTION_WRITE_ENABLED` remain env-driven `false`. PR #2972 LOCAL-only operating-model guardrail in force. No active arc at ratification time.
- **Session:** First-ever post-Arc-close IOS arc-selection ratification. Chris framed the workflow as "Route Claude's second-arc recommendation through Rigby SIGN before Chris ratifies," making explicit that first-arc-override discipline (§11.3) extends to subsequent arc-open selections via the same SIGN → ratify path.
- **Extraction basis:** `RATIFICATION_2026-07-06_first_queue.md` (first-queue band ratification); `BACKLOG.md` at HEAD 678a7595 (all T0 / T1 / T2 / T3 / DEFER rows); IOS `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` v1.5 §3.1 (six-dim scoring rubric) + §3.1.b (CX-P10 admissibility) + §3.2 (Chris ratification bands) + §3.3 (cross-domain +2 bump) + §5.1 rule 10 (UNKNOWN honesty) + §11.2 Step 6 (Rigby routing) + §11.3 (per-tier ratification + first-arc override + reversibility) + §11.4 (snapshot-not-plan discipline); Rigby's SIGN response on pin `pa-6a4e2eff5594486b`.

## 2. Ratification axes and Chris dispositions

Ratification presented via Rigby in PA chat on the fresh IOS-scoped SIGN pin `pa-6a4e2eff5594486b`. Rigby returned an overall `SIGN-with-edits — MED confidence` verdict with 8 folds (F1–F8) and a 7-axis contingency-gated ratification card. Chris responded via Chat UI with **"Agree All. Ratify Rigby's SIGN-with-edits card exactly as structured."**

### Axis 0 — Context snapshot (non-debatable inputs)

**Ask:** Ratify the fixed inputs (Arc I-0100 fully closed; PR #2972 LOCAL-only guardrail; mechanical elimination already applied).

**Chris disposition:** **Ratified via "Agree All".** Inputs unchanged from Claude/Rigby SIGN card.

**Ratified inputs:**
- Arc I-0100 closed 2026-07-07 (all 3 T1 intakes terminal).
- PR #2972 LOCAL-only operating-model guardrail in force.
- Mechanical elimination applied: SHIPPED / LOCAL_ACCEPTED / IN_ARC rows removed; all BLOCKED_ON_RESEARCH rows removed from arc-seed consideration; CX-P4 posture-pending T0 ADRs deferred (no CX-P4 arc opens without Chris naming precedence); CX-P1 runtime-owner assignment items deferred (ownership gate not ratified); `IB-Q1-BOOT-03` third-arc gated (not eligible).

### Axis 1 — Candidate pool (T0 dominates while non-empty)

**Ask:** Ratify the four surviving eligible T0 candidates as the arc-seed pool.

**Chris disposition:** **Ratified via "Agree All".**

**Ratified pool:**
1. `IB-2199-T0-01` — RAG corpus substrate maturity gradient.
2. `IB-1999-T0-01` — Authority per-plane posture (5/8 planes PERMEABLE-BROKEN).
3. `IB-2099-T0-01` — Event/Integration 10-plane substrate landscape.
4. `IB-2599-T0-01` — API surface topology (4-Cat).

All four route through **NEEDS_ADR** path per §3.1.b (`spec_ref` field absent in BACKLOG row schema → cannot upgrade to CX-P10 admissibility; downgrade to NEEDS_ADR intake path).

### Axis 2 — Default selection (with explicit contingency)

**Ask:** Ratify `IB-2199-T0-01` as default second-arc seed with an explicit Stage 1 severability gate against `IB-2199-BOR-01` (RAG `search_docs` + `kb_tool` retrieval end-to-end verification).

**Chris disposition:** **Ratified via "Agree All".**

**Ratified default seed:** `IB-2199-T0-01` — RAG corpus substrate maturity gradient.

**Ratified arc slug (default path):** `rag_corpus_substrate_maturity`.

**Ratified arc identifier:** `I-0200` (per IOS §4.2 `I-NNNN` prefix; sequential after `I-0100`).

**Ratified severability gate (must be answered in Stage 1 scoping):**
- **Question:** Is `IB-2199-T0-01` severable from `IB-2199-BOR-01`?
  - **If YES (severable):** proceed with `IB-2199-T0-01` as `I-0200` seed; slug remains `rag_corpus_substrate_maturity`.
  - **If NO (not severable):** reclassify `IB-2199-T0-01` as `BLOCKED_ON_RESEARCH`; automatically switch `I-0200` seed to `IB-1999-T0-01` (Authority per-plane posture); slug flips to `authority_per_plane_posture`.

### Axis 3 — Cross-domain bump constraint

**Ask:** Ratify F5 fold — do NOT apply §3.3 +2 cross-domain bump for RAG + memory unless positive cross-domain dependency evidence is cited (not "no visible disconnect").

**Chris disposition:** **Ratified via "Agree All".**

**Ratified constraint:** The prior Claude scoring pass claimed a +2 bump for `IB-2199-T0-01` on rag+memory cross-domain grounds; this bump is **withdrawn** absent positive evidence citation. IDBT-0001 PARTIAL_DISCHARGE HIGH acknowledged as reason: "no visible disconnect" is not equivalent to "enumerated and STRONG." Rescored `IB-2199-T0-01` total drops from 23 to 21 (still highest, but margin is 1 point over `IB-1999-T0-01` at 20 — thin enough that Rigby's Q5 argument that Authority may outrank RAG on a re-scored Attention-preservation dimension survives as a live consideration during Stage 1 severability determination).

### Axis 4 — Stage 1 scoping admission rules (no pre-commit)

**Ask:** Ratify F3 + F7 + F8 folds governing companion-row admission and blocker-type classification during Stage 1 scoping.

**Chris disposition:** **Ratified via "Agree All".**

**Ratified rules:**
- Stage 1 scoping MAY *evaluate* companion rows but does NOT admit them by default.
- **If seed = `IB-2199-T0-01`:** evaluate as candidate companion rows (not auto-admitted):
  - `IB-2199-T1-01` — retrieval-authority framework governance (post-2199 SPEC_COMPLETE).
  - `IB-CXP10-T1-03` — Wire RAG design-complete runtime scaffold.
  - Binary outcome at end of Stage 1: **admit into arc** (becomes in-arc scope, appears in Stage 2 sequence) OR **hold out** (remains backlog; may be re-tiered).
- **If seed = `IB-1999-T0-01`** (fallback path): Stage 1 must classify the blocker on `IB-1999-T1-01` (currently `BLOCKED_ON_RESEARCH` per BACKLOG:216) as either:
  - **posture-clarity blocker** → discharged by `IB-1999-T0-01` ratification → eligible to admit during Stage 1.
  - **unknown-fact blocker** → remains BOR-blocked → hold out; future research arc required before admission.

### Axis 5 — Automatic contingency mechanics (what "Agree All" ratifies)

**Ask:** Ratify F1 + F4 + F6 folds — the auto-switch mechanic from `IB-2199-T0-01` to `IB-1999-T0-01` on Stage 1 severability failure requires no additional Chris directive.

**Chris disposition:** **Ratified via "Agree All".**

**Ratified mechanic:**
- Stage 1 scoping produces a severability determination against `IB-2199-BOR-01`.
- **If severable:** seed remains `IB-2199-T0-01`; arc proceeds under slug `rag_corpus_substrate_maturity`.
- **If not severable:** Claude records the determination in the scoping doc; automatically reclassifies `IB-2199-T0-01` as `BLOCKED_ON_RESEARCH` (BACKLOG row flip); automatically switches `I-0200` seed to `IB-1999-T0-01`; arc slug flips to `authority_per_plane_posture`; arc folder rename discipline noted as a Stage 1 mechanical bookkeeping step. No additional Chris ratification required for the auto-switch — Chris's "Agree All" ratifies the outcome-conditional mechanic itself.
- Any Chris override of the auto-switch (e.g., "hold, ratify 2199 BOR path anyway" or "flip to Option C 2099 instead of 1999") requires an explicit Chris directive at Stage 1 severability determination time.

### Axis 6 — Cross-domain bump constraint (re-cited to lock)

**Ask:** Re-cite Axis 3's F5 constraint to lock against re-emergence during Stage 1 or Stage 2 scoring.

**Chris disposition:** **Ratified via "Agree All".**

**Ratified re-cite:** Neither Stage 1 companion-row admission decisions nor Stage 2 ADR-authoring decisions may reintroduce the withdrawn +2 bump. Positive cross-domain evidence citation is the ONLY re-entry path — and any such citation must be Chris-ratified via Rigby-routed SIGN before it can influence sequencing.

### Axis 7 — Chris disposition options (reply format)

**Ask (informational; not itself a disposition ask):** The card exposed four Chris reply options for record — "Agree All" (default), "Option B" (force-seed `IB-1999-T0-01`), "Option C: seed = `IB-2099-T0-01`" or "Option C: seed = `IB-2599-T0-01`", plus companion-row admission timing add-ons.

**Chris disposition selected:** **"Agree All"** — ratifies Axis 5 defaults + contingency + Axis 4 scoping rules + Axis 6 bump constraint. No Option B / C invoked. No companion-row admission timing override invoked.

## 3. Pin lifecycle for this ratification

Per IOS v1.5 §15.14 Rigby SIGN pin lifecycle:

- **Selection SIGN pin minted at second-arc SIGN request:** `pa-6a4e2eff5594486b` (label `ios-arc-open-I-0200-sign-review`) minted 2026-07-07 via `session_tool.create_fresh` on the T4 Group 1700 pin. Rigby SIGN response received on this pin (SIGN-with-edits MED with 8 folds).
- **Selection SIGN pin retired 2026-07-07 post-Chris-Agree-All:** `session_tool.retire conversation_id='pa-6a4e2eff5594486b' force=true` → `retired: true, updated_count: 4, previously_active: true, is_current_bound: false`. SECOND consecutive dedicated fresh SIGN pin retirement under IOS active discipline after `pa-39d3694312ab4326` (first-queue-ratification).
- **Paused research pin preserved:** `pa-44a6eb70d8814e34` (T4 Group 1700 Observability arc pin) unchanged; preserved as `# PRESERVED AS COMMENT` block above `tools/pa_local.sh --conversation` line per §15.14 phase-transition supersession rule.
- **Arc-scoped SIGN pin minted at Stage 1 open:** `pa-1b76ee75adbf4031` (label `ios-arc-open-I-0200`) minted 2026-07-07 via `session_tool.create_fresh`. Rotated into `tools/pa_local.sh --conversation` on the same edit as the paused-research preservation. Mirrors the `pa-c5b235f7b15f45be` role for Arc I-0100.
- **Arc-scoped pin lifecycle:** covers Stage 1 scoping SIGN Cycle 1 through Stage 6 implementation close. Retirement discharge at Arc I-0200 Stage 6 close, mirroring Arc I-0100 pattern (PR #2978).

## 4. What this ratification does NOT do

- Does NOT open Stage 2 of Arc I-0200. Stage 2 opens only after Stage 1 severability determination + Chris ratification of Stage 1 exit gate + (per IOS §4.3 Stage 2 Entry gate v1.5) ADR corpus precondition (already SATISFIED — `docs/adr/` on `main` per Arc I-0100 PR #2948).
- Does NOT ratify companion rows into the arc. `IB-2199-T1-01` and `IB-CXP10-T1-03` (default path) or `IB-1999-T1-01/-02/-03` (fallback path) remain backlog rows unless Stage 1 evaluation converts them via the explicit rules in Axis 4.
- Does NOT ratify individual T0 ADR authoring content. Whichever seed is ratified at Stage 1 severability determination, the resulting ADR (`ADR-000N` under `docs/adr/`) must be authored in Stage 2 and ratified via Chris per §8.3 + §4.3 Stage 2 discipline.
- Does NOT waive the LOCAL-only operating-model guardrail (PR #2972). Any prod-touching work in Arc I-0200 requires Chris explicitly providing a live prod access path.
- Does NOT waive `IDBT-0001` PARTIAL_DISCHARGE HIGH. The deep-late T1 leaf tail remains unenumerated; the +2 bump withdrawal in Axis 3 acknowledges this but does not discharge it. Full leaf re-extraction may happen incrementally during Arc I-0200 Stage 1 scoping for the ratified seed's domain.
- Does NOT modify Research OS trajectory. T4 Group 1700 Observability research arc remains open in `docs/research/OPEN_ARCS.md` — PAUSED via §15.14 phase-transition supersession, not cancelled. Chris re-enters research phase by explicit Research OS command per IOS §15.3.

## 5. Cross-references

- IOS: `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` v1.5 (§3.1 + §3.1.b + §3.2 + §3.3 + §5.1 rule 10 + §11.2 + §11.3 + §11.4 + §15.14).
- First-queue ratification: `docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md` (band-level ratification + Arc I-0100 first-arc override precedent).
- BACKLOG at HEAD 678a7595: `docs/research/implementation/BACKLOG.md` (all T0/T1 rows referenced above).
- Rigby SIGN response: retained on retired pin `pa-6a4e2eff5594486b` (canonical text captured in the Claude session record + this document's Axis 2–7 folds).
- Arc I-0200 Stage 1 scoping doc (to be authored in same PR): `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md` — default-path folder; renamed to `authority_per_plane_posture/` if fallback path triggers.
- Arc I-0100 Stage 6 close doc: `docs/research/implementation/observability_spine_mission_evidence_substrate/I-010099_observability_spine_implementation_close.md` (PR #2976).
- LOCAL-only guardrail: PR #2972.
- Paused research pin context: `tools/pa_local.sh:44-59` (preserved-as-comment block) + T4 Group 1700 Observability load-bearing inputs list.

## 6. Meta-observation for IOS §14.2 codification tracking

This is the **first execution** of the second-arc-selection SIGN-then-ratify workflow. Codification candidates surfacing:

1. **Contingency-gated arc seed pattern.** Arc I-0200 opens with a two-outcome seed (2199 default OR 1999 auto-switch) determined by Stage 1 severability determination. Prior Arc I-0100 opened with a single-outcome seed. Whether contingency-gated arc opens should be a codified IOS pattern versus a Chris-explicit-override case is a live question — awaiting second trigger before proposing IOS v1.6 §4.3 amendment. Codification candidate not yet ratified.

2. **Rigby's second consecutive stronger-than-Claude first-arc argument.** RATIFICATION_2026-07-06 §6 flagged this as single-trigger: "Rigby's first-arc recommendation should always accompany Claude's candidate ranking; Chris's default when Rigby and Claude diverge is Rigby's pick unless she flags Low confidence." At Arc I-0200 selection, Rigby again produced a meta-argument (Authority as sneak-strong fallback + F5 bump withdrawal) that Claude's rubric under-weighted. This is the SECOND independent trigger. Codification candidate now meets the §14.2 two-trigger threshold for IOS §11.3 amendment — proposal deferred to a dedicated IOS-patch session (do NOT bundle into Stage 1 arc-open scope).

3. **Bump-withdrawal discipline.** F5's "positive evidence, not absence of evidence" grounding of the §3.3 +2 bump is a candidate hardening of §3.3 itself. Single trigger. Not codified at v1.5; recorded here for the second trigger.

4. **Severability-gate as Stage 1 first-class exit condition.** IOS §4.3 Stage 1 exit gate does not currently name severability determination as a required exit-checklist item. Arc I-0200 introduces one. Single trigger. Not codified at v1.5.
