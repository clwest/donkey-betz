# Next Session — Start Here

---

## READ THIS FIRST — ARC I-0100 STAGE 2 OPEN; NEXT ACTION IS ADR-0002 AUTHORING

**Refreshed 2026-07-06 per IOS §15.15** (stage-transition PR type — Arc I-0100 Stage 1 → Stage 2 opening ceremony). If any field below disagrees with `main` reality, `main` wins per §15.3 supersession — but §15.15 discipline is what keeps this file fresh in the first place.

### Phase

**`implementation`.** IOS status: `active v1.4` on `main`. Research trajectory (T4 Group 1700 Observability arc-open per S2699 close) is **PAUSED** per IOS §15.3 phase-transition supersession rule. Re-entry only via explicit Chris Research OS command (`Start / Continue / Close research group NNNN`).

### Active arc

- **Arc ID:** `I-0100`
- **Slug:** `observability_spine_mission_evidence_substrate`
- **Scoping doc:** `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md`
- **First production implementation arc under IOS.**

### Current stage

- **Stage:** `2`
- **`stage_state`:** `active` (per §4.3.0 v1.4 vocabulary — Stage 2 opened 2026-07-06 via P0 prep PR #2948 merge auto-open per §4.3 Stage 2 Entry gate v1.4 Option (a) clause; frontmatter flipped in the housekeeping stage-transition PR)

### Next executable action

**Author `ADR-0002-pa-write-shape-and-correlation-contract.md`** per Arc I-0100 scoping doc §9.1 line 2. Content: PA write shape (per-turn `AgentExecution` vs per-message span vs dedicated `PAAgentExecution` model) + PA↔`LLMCallEvent` correlation contract (keys + join path) per F5 fold. **F4 fold ratifies ADR-B FIRST**, then ADR-A, then optional ADR-C.

Concrete sequence for the next session:

1. **First tool call:** `context-kit orient` per MEMORY workflow rule.
2. **Verify Stage 2 open** via scoping doc frontmatter grep (`stage: 2, stage_state: active`) and `git ls-tree main -- docs/adr/` (must show `ADR-0001-establish-adr-corpus.md`).
3. **Verify pin state:** `tools/pa_local.sh` `--conversation` line points at `pa-c5b235f7b15f45be`; paused-research pin `pa-44a6eb70d8814e34` preserved as comment above.
4. **Assess design-prep equivalence** per IOS §4.3 Stage 2 v1.4 rule: read Arc I-0100 scoping §9.1 ADR-B pre-scoping (lines ~356–360). It must contain decision question + options + constraints + consequences + verification implications. If sufficient → cite scoping §9.1 as design-prep source in ADR-0002 PR body. If insufficient → author standalone `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_b_pa_write_shape.md` first.
5. **Draft `docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md`** per `ADR-0001` §3.3 frontmatter schema + §3.4 body sections (§1 Status / §2 Context / §3 Decision / §4 Consequences / §5 Alternatives considered / §6 Reversibility / §7 Provenance).
6. **Route Rigby SIGN Cycle 1** per IOS §7.2 v1.4 implementation ADR SIGN cadence: single-batch × 4-Q on active arc pin `pa-c5b235f7b15f45be`. Do NOT rotate or mint a fresh pin.
7. **Fold SIGN edits inline** + present Chris ratification card via Rigby on same pin.
8. **On Chris ratification:** flip ADR frontmatter `status: proposed → accepted`; populate `ratified: YYYY-MM-DD`.
9. **Open ADR-0002 PR** with cascade co-located per §12.5.a + §12.5.d evidence block + `00-START-NEXT-SESSION.md` refresh per §15.15 (stage-transition PR type — even mid-Stage-2 ADR ratifications refresh this file per §15.15.b classification of "stage-transition" broadly interpreted).

### Active SIGN pin

- **Arc pin:** `pa-c5b235f7b15f45be`
- **Label:** `ios-arc-open-I-0100`
- **Minted:** 2026-07-06 at Arc I-0100 open (S2700)
- **Rotated into `tools/pa_local.sh --conversation`:** yes.
- **Retirement due:** Stage 6 close per IOS §7.2 isolation-pin discipline. **Do NOT rotate the pin between ADR-A/B/C** per §7.2 v1.4 shared-arc-pin rule.

**Paused-research pin preserved as header comment above `tools/pa_local.sh --conversation` line:** `pa-44a6eb70d8814e34` (T4 Group 1700 Observability research arc — from S2699 close). Restored on IOS phase exit per §15.14. Do NOT retire it during IOS activity.

**Retired pins (historical):** `pa-39d3694312ab4326` (`ios-part11-first-queue-ratification-v1`; retired at seed PR #2941 merge 2026-07-06).

### Pending PRs

| # | Title | State |
|---|-------|-------|
| _(none)_ | — | — |

All in-flight PRs (#2947 v1.3 + #2948 P0 prep + #2949 v1.4 + housekeeping stage-transition PR) merged 2026-07-06. Next PR opens for ADR-0002.

---

## Read as background (Level C step C.4–C.6 loads specific to Arc I-0100 Stage 2)

- `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` v1.4 (particularly §4.3.0 stage_state enum + §4.3 Stage 2 Entry gate + design-prep equivalence + §7.2 v1.4 implementation ADR SIGN cadence + §12.5 cascade discipline + §15.14 pin lifecycle + §15.15 this-file ownership).
- `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md` (arc scoping doc — frontmatter now `stage: 2, stage_state: active`; §9.1 ADR-B pre-scoping = candidate design-prep artifact per §4.3 Stage 2 v1.4 equivalence rule).
- `docs/adr/ADR-0001-establish-adr-corpus.md` (recursive-bootstrap ADR — accepted; establishes the format ADR-0002 follows; §3.3 frontmatter + §3.4 body-section template).
- `docs/research/implementation/BACKLOG.md` (IB-1799-T1-01/02/03 in `IN_ARC (I-0100)`; IB-Q1-BOOT-01 `SHIPPED` with `pr_refs: #2948` + `adr_ref: ADR-0001`).
- `docs/research/implementation/IMPLEMENTATION_DEBT.md` (IDBT-0001 PARTIAL_DISCHARGE HIGH — 1799 slice discharge in Arc I-0100 scope; IDBT-0002 TECH_DEBT_ACCRUED MEDIUM — RAG-owned embedding invalidation delegated to Group 2100 RAG).
- `docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md` (frozen Chris disposition; ratifier of Arc I-0100 first-arc override + T0 individual-gate posture).
- `docs/research/domains/observability/1799_observability_canonical_summary.md` (§1 verdict + §5 D74 + §8.2 T1 items 2–3 — PA→AgentExecution wire + MISSION_RUNNER + RIGBY_DELEGATION staged unlock — context for ADR-B correlation contract options).
- `docs/research/OPEN_ARCS.md` (Arc I-0100 row under `Currently in progress`; Stage 2 opened; T4 Group 1700 paused).
- `docs/research/platform/cross_domain_integration_audit.md` (Arc I-0100 Stage 6 close must append §14.N per IOS §D10 hard gate).
- MEMORY rules: `feedback_session_open_with_orient`, `feedback_rigby_comms`, `feedback_claude_directs_rigby_then_verifies`, `feedback_docs_cascade_at_every_close`, `feedback_cascade_pr_must_include_embed_step`, `feedback_rigby_sign_worker_instability_recovery`.

---

## Session ready check (before authoring ADR-0002)

1. **First tool call: `context-kit orient`** per MEMORY workflow rule `feedback_session_open_with_orient`.
2. `git log -8` — verify #2947 + #2948 + #2949 + housekeeping stage-transition PR all merged 2026-07-06.
3. `git ls-tree main -- docs/adr/` — must show `ADR-0001-establish-adr-corpus.md`. If missing, escalate to Chris; do NOT open Stage 2 work.
4. `grep '^stage:\|^stage_state:' docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md` — must show `stage: 2` + `stage_state: active`. If not, housekeeping stage-transition PR did not land; escalate.
5. `tools/pa_local.sh "platform_config_tool action=overview"` → verify `service_context: local` + `railway_environment: local` + `database_name: unified_donkey_betz` + `default_llm_provider: openai` under arc pin `pa-c5b235f7b15f45be`.
6. Read Arc I-0100 scoping doc §9.1 (ADR-B pre-scoping — the design-prep source under §4.3 Stage 2 v1.4 equivalence rule) + §7.2 (R1/R2/R3 risks + mitigations + rollback triggers) + Rigby SIGN Cycle 1 fold record for F4 (ADR-B first) + F5 (correlation contract).
7. Read `docs/adr/ADR-0001-establish-adr-corpus.md` §3.3 (frontmatter schema) + §3.4 (canonical §1-§7 body sections) — templates ADR-0002 follows.
8. Read IOS §4.3 Stage 2 (Entry gate + design-prep equivalence + Exit gate + cascade co-location per ADR PR) + §7.2 (implementation ADR SIGN cadence: one cycle per ADR, active arc pin, 2-Q min / 4-Q typical / 6-Q max, no rotation) + §12.5 (cascade discipline) + §15.15 (this file's ownership).
9. Read 1799 xx99 §5 D74 (six-axis correlation-spine options) + §8.2 T1 items 2–3 (PA→AgentExecution wire + MISSION_RUNNER staged unlock) — semantic context for ADR-B's correlation contract options.
10. Assess §4.3 Stage 2 v1.4 design-prep equivalence for scoping §9.1: does it contain decision question + options (per-turn AgentExecution / per-message span / dedicated PAAgentExecution model) + constraints (F5 correlation contract keys + join path; no dedup; retention constraints for F2) + consequences per option + verification implications (F7 verification-method interface at Stage 1, concrete queries at Stage 3)? If YES → §9.1 IS the design-prep artifact; cite in ADR-0002 PR body. If NO → author standalone design-prep doc first.
11. Draft `docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md` per ADR-0001 §3.3 frontmatter + §3.4 body-section shape.
12. Route Rigby SIGN Cycle 1 on ADR-0002 per §7.2 v1.4 cadence: single-batch × 4-Q on arc pin `pa-c5b235f7b15f45be`. Do NOT rotate the pin. Do NOT mint a fresh SIGN pin.
13. Fold SIGN edits inline + present Chris ratification card via Rigby on arc pin.
14. On Chris ratification: flip ADR-0002 frontmatter `status: proposed → accepted`; populate `ratified` date.
15. Open ADR-0002 PR with cascade co-located per §12.5.a + §12.5.d evidence block + this file refreshed per §15.15.

**ADR-0002 authoring short command (Chris):** `Author ADR-0002 pa-write-shape-and-correlation-contract for Arc I-0100 Stage 2` per IOS §4.3 Stage 2 + F4 fold ADR-B-first sequencing.
