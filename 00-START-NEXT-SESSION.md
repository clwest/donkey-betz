# Next Session — Start Here

---

## READ THIS FIRST — IOS ACTIVE V1.4; ARC I-0100 STAGE 1 P0 PREP IN FLIGHT

**Refreshed 2026-07-06 per IOS §15.15** — this file is co-committed to every arc-open PR, P0-prep PR, stage-transition PR, arc-close PR, and IOS / Research OS / Playbook patch PR. If any of the fields below disagree with `main` reality, `main` wins per §15.3 supersession — but §15.15 discipline is what keeps this file fresh in the first place.

### Phase

**`implementation`.** IOS status: `active v1.4` on `main` (this file's version). Research trajectory (T4 Group 1700 Observability arc-open per S2699 close) is **PAUSED** per IOS §15.3 phase-transition supersession rule. Re-entry only via explicit Chris Research OS command (`Start / Continue / Close research group NNNN`).

### Active arc

- **Arc ID:** `I-0100`
- **Slug:** `observability_spine_mission_evidence_substrate`
- **Scoping doc:** `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md`
- **First production implementation arc under IOS.**

### Current stage

- **Stage:** `1`
- **`stage_state`:** `p0-prep-in-flight` (per §4.3.0 v1.4 vocabulary — P0 prep PR #2948 open, not merged)

Rationale for `stage_state`: Stage 1 exit-gate cleared 2026-07-06 via #2945 (Arc I-0100 Stage 1 arc-open bundle merged). ADR corpus precondition satisfaction via Option (a) is in progress — P0 prep PR #2948 authored ADR-0001 + created `docs/adr/`; awaiting merge. Per §4.3 Stage 2 Entry gate (v1.4), Stage 2 opens on `docs/adr/` existing on `main` AND (Chris directive OR P0 prep merge for Option (a) arcs). P0 prep merge = Stage 2 opening event for this arc.

### Next executable action

**Sequence three steps in order:**

1. **Merge PR #2949** (this IOS v1.4 patch). Docs-only. Fresh-session Stage 2 readiness — B1–B6 refinements.
2. **Merge PR #2948** (IB-Q1-BOOT-01 P0 prep — establish ADR corpus + ADR-0001). Docs-only. Auto-opens Stage 2 per §4.3 Stage 2 Entry gate (v1.4) Option (a) auto-open clause.
3. **Housekeeping commit on merge of both:** flip scoping doc frontmatter per §4.3.0 discipline — `stage_state: p0-prep-in-flight → p0-prep-merged` on #2948 merge, then `stage: 1 → 2` + `stage_state: p0-prep-merged → active` at the Stage 2 opening commit. Flip BACKLOG IB-Q1-BOOT-01 `status: IN_ARC → SHIPPED` with inline `pr_refs: #2948` per §2.2 v1.4 Discipline B.

**Then Stage 2 ADR authoring begins:**

4. **Author ADR-0002** (`pa-write-shape-and-correlation-contract`) per Arc I-0100 scoping doc §9.1 line 2. Content: PA write shape (per-turn `AgentExecution` vs per-message span vs dedicated `PAAgentExecution` model) + PA↔`LLMCallEvent` correlation contract (keys + join path) per F5 fold. **F4 fold ratifies ADR-B FIRST**, then ADR-A, then optional ADR-C.
5. **Rigby SIGN Cycle 1 on ADR-0002** per §7.2 v1.4 implementation ADR SIGN cadence: one SIGN cycle on active arc pin (`pa-c5b235f7b15f45be`; no rotation), 4-Q typical (ADR-B has 2–3 decision axes + correlation contract). Chris ratification card via Rigby on same pin.
6. **Per §4.3 Stage 2 v1.4 design-prep equivalence:** verify scoping doc §9.1 pre-scoping is sufficient (decision question + options + constraints + consequences + verification implications). Arc I-0100 scoping §9.1 likely qualifies — no separate design-prep doc needed. Cite scoping §9.1 subsection as design-prep source in ADR PR body.
7. **Cascade co-located in ADR-0002 PR** per §12.5.a (ADRs are RAG-critical per §12.5.b) + §12.5.d evidence block + `00-START-NEXT-SESSION.md` refresh per §15.15 (Stage-transition PR type).

### Active SIGN pin

- **Arc pin:** `pa-c5b235f7b15f45be`
- **Label:** `ios-arc-open-I-0100`
- **Minted:** 2026-07-06 at Arc I-0100 open (S2700)
- **Rotated into `tools/pa_local.sh --conversation`:** yes, at Stage 1 SIGN Cycle 1 routing time.
- **Retirement due:** Stage 6 close per IOS §7.2 isolation-pin discipline.

**Paused-research pin preserved as header comment above `tools/pa_local.sh --conversation` line:** `pa-44a6eb70d8814e34` (T4 Group 1700 Observability research arc — from S2699 close). Restored on IOS phase exit per §15.14. Do NOT retire it during IOS activity.

**Retired pin (historical):** `pa-39d3694312ab4326` (`ios-part11-first-queue-ratification-v1`; retired at seed PR #2941 merge 2026-07-06).

### Pending PRs

| # | Title | State |
|---|-------|-------|
| **#2948** | Arc I-0100 IB-Q1-BOOT-01 P0 prep — establish ADR corpus + ADR-0001 | `OPEN` (awaiting Chris review + merge) |
| **#2949** | IOS v1.4 fresh-session Stage 2 readiness refinement (this patch — number assigned on push) | `OPEN` (this patch's own PR — will merge before #2948 per sequence above) |

No other implementation arcs open. No merged-but-frontmatter-unflipped PRs at present.

---

## Read as background (Level C step C.4–C.6 loads specific to Arc I-0100)

- `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` v1.4 (particularly §4.3.0 stage_state enum + §4.3 Stage 2 Entry gate + §4.3 Stage 2 design-prep equivalence + §7.2 implementation ADR SIGN cadence + §12.5 cascade discipline + §15.14 pin lifecycle + §15.15 this-file ownership).
- `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md` (arc scoping doc, especially §9.1 ADR-B pre-scoping which serves as design-prep per §4.3 Stage 2 v1.4 equivalence rule).
- `docs/research/implementation/BACKLOG.md` (IB-1799-T1-01/02/03 in `IN_ARC (I-0100)`; IB-Q1-BOOT-01 `IN_ARC` pending #2948 merge → `SHIPPED`).
- `docs/research/implementation/IMPLEMENTATION_DEBT.md` (IDBT-0001 PARTIAL_DISCHARGE HIGH — 1799 slice discharge in Arc I-0100 scope; IDBT-0002 TECH_DEBT_ACCRUED MEDIUM — RAG-owned embedding invalidation delegated to Group 2100 RAG — added by #2948).
- `docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md` (frozen Chris disposition; ratifier of Arc I-0100 first-arc override + T0 individual-gate posture).
- `docs/adr/ADR-0001-establish-adr-corpus.md` (recursive-bootstrap ADR — ships in #2948; establishes the ADR format ADR-0002 will follow).
- `docs/research/domains/observability/1799_observability_canonical_summary.md` (§1 verdict + §5 D74 + §8 T0/T1 tail).
- `docs/research/OPEN_ARCS.md` (Arc I-0100 row under `Currently in progress`; T4 Group 1700 paused).
- `docs/research/platform/cross_domain_integration_audit.md` (Arc I-0100 Stage 6 close must append §14.N per IOS §D10 hard gate).
- MEMORY rules: `feedback_session_open_with_orient`, `feedback_rigby_comms`, `feedback_claude_directs_rigby_then_verifies`, `feedback_docs_cascade_at_every_close`, `feedback_cascade_pr_must_include_embed_step`, `feedback_rigby_sign_worker_instability_recovery`.

---

## Session ready check (before authoring ADR-0002)

Only run this checklist AFTER both PR #2949 (this v1.4 patch) and PR #2948 (P0 prep) merge:

1. **First tool call: `context-kit orient`** per MEMORY workflow rule `feedback_session_open_with_orient`.
2. Verify `git log -3` shows both PR merges in expected order (v1.4 first, then P0 prep, or amend housekeeping commit that flipped `stage: 1 → 2`).
3. Run `git ls-tree main -- docs/adr/` — must show `ADR-0001-establish-adr-corpus.md`. If missing, do NOT open Stage 2; escalate.
4. `tools/pa_local.sh "platform_config_tool action=overview"` → verify `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` under arc pin `pa-c5b235f7b15f45be`.
5. Read `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md` in full — verify frontmatter now shows `stage: 2, stage_state: active`. Read §9.1 ADR-B pre-scoping (lines ~356–360) in detail.
6. Read `docs/adr/ADR-0001-establish-adr-corpus.md` §3 (Decision / format spec) + §3.3 (frontmatter schema) + §3.4 (body sections) — these are the exact templates ADR-0002 follows.
7. Read IOS §4.3 Stage 2 v1.4 Entry gate + Design-prep equivalence + §7.2 v1.4 implementation ADR SIGN cadence + §12.5 cascade + §15.15 this-file refresh.
8. Read 1799 xx99 §5 D74 + §8.2 T1 items 2–3 (PA→AgentExecution wire + MISSION_RUNNER + RIGBY_DELEGATION staged unlock) — context for ADR-B's correlation contract options.
9. Verify Arc I-0100 scoping doc §9.1 ADR-B pre-scoping satisfies §4.3 Stage 2 v1.4 design-prep equivalence criteria (decision question + options + constraints + consequences + verification implications). If sufficient, cite it in ADR-0002 PR body as design-prep source; if insufficient, draft standalone `I-0100_design_prep_adr_b_pa_write_shape.md` per §4.3 Stage 2 location rule.
10. Draft `docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md` per ADR-0001 §3.4 body-section shape + §3.3 frontmatter schema.
11. Route Rigby SIGN Cycle 1 on ADR-0002 per §7.2 v1.4 cadence: single-batch × 4-Q on arc pin `pa-c5b235f7b15f45be`. Do NOT rotate the pin. Do NOT mint a fresh SIGN pin.
12. Fold SIGN edits inline + present Chris ratification card via Rigby on arc pin.
13. Cascade co-located in ADR-0002 PR per §12.5.a; §12.5.d evidence block in PR body; refresh `00-START-NEXT-SESSION.md` per §15.15 (stage-transition PR type — but Stage 2 already opened; refresh reflects "ADR-B drafted, awaiting Chris ratify" state).

**Arc I-0100 Stage 2 opening short command (Chris — if auto-open via Option (a) is not preferred):** `Open implementation arc I-0100 Stage 2` per IOS §10 short commands + §4.3 Stage 2 Entry gate v1.4.

**ADR-0002 authoring short command (Chris):** `Author ADR-0002 pa-write-shape-and-correlation-contract for Arc I-0100 Stage 2` per IOS §4.3 Stage 2 + F4 fold ADR-B-first sequencing.
