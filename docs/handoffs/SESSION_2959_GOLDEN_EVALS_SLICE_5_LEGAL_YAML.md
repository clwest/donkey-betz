# SESSION 2959 — Golden Evals Tier-1 slice 5: LegalDocDrafterAgent YAML

**Date:** 2026-07-25
**Session:** S2959
**Arc:** Golden Evals (S2954+ open)
**Slice:** 5 of 8 Tier-1 YAMLs
**HEAD at slice merge:** `8fa60421f`
**HEAD at close (post-cascade):** filled at close cascade merge
**PR shipped:** [#3559](https://github.com/clwest/donkey-betz-platform/pull/3559)

---

## What shipped

`evals/tier1/legal_doc_drafter_agent.yaml` — 794 lines, 13 prompts, fifth canon_version=1 file.

**Coverage:** 5 happy path + 2 each tool_timeout / data_unavailable / ambiguous_input / bad_input.

**Substrate reference:** `evals/tier1/devops_agent.yaml` @ `98ba0e06b` (S2957 slice 3 canon).

**Agent under test:**
- Source: `core/agents/legal/legal_doc_drafter_agent.py:474` (LegalDocDrafterAgent class).
- File size: 8,169 lines / 356.4 KB (largest agent file in Tier-1 arc).
- Two execution paths in `execute()` at line 1229:
  - **(A) STANDARD MODE** — GPT tool-selection at line 1297 across 10 declared tools (Core 6 + Session 404 4; agent's actual `tools` list also includes `check_order_attachment_required` at line 939 for 11 function-schema entries total).
  - **(B) DENIED MOTION ROUTING BRANCH** — auto-detected at line 1270 via `_detect_denied_motion_mode`; bypasses GPT tool-selection and forces direct dispatch through `_execute_denied_motion_pipeline` at line 1274. **Deliberately framed as routing branch, not "new shape"** — per Rigby T2 fold 2, to avoid canon_version=2 creep before S2962 arc-close.
- Post-validation: Mythology Enforcer (Session 409) at line 1481 validates output for hallucinations. `data.jurisdiction`, `data.focus_area`, `data.disclaimer_included` are hardcoded constants at lines 1424-1426; validators must not derive `health_status` from them.

## Volume snapshot (DB-verified via direct ORM at authoring T0, HEAD c0e87d2f8)

| Window | Executions | Completed | Failed | Notes |
|---|---|---|---|---|
| 30d (from 2026-06-25T00Z) | 5 | 5 | 0 | 100% "Draft a motion to modify visitation" variants |
| All-time | 12 | 12 | 0 | earliest 2026-06-23, latest 2026-07-17 |

All 12 rows have `error_message=''` (empty string, not null). Zero failure sample — all fault-injection cases in the YAML are constructed from LegalDocDrafterAgent's known dependency graph rather than replayed from production traces.

## Honestly called out coverage limits

1. **THIN** — 5 30d executions (comparable to Workflow's 9).
2. **NARROW** — 100% Colorado parenting-time modification variants; zero variety across the 10-tool surface.
3. **ZERO FAILURE SAMPLE** — every one of the 12 all-time rows completed successfully.
4. **LEGAL DOMAIN BUYER-FACING RISK** — hallucination invariants extra-sharp per S2959 arc-slice scope note.

**Actionable conclusion (per Rigby T2 fold 4):** treat this YAML as SCHEMA + HALLUCINATION-INVARIANT validation, not performance/reliability assurance. Re-baseline volume claims at S2962 arc-close if production traffic grows past 50 30d executions across ≥2 motion types.

## Legal-domain-specific acceptance predicates

Beyond the general `no_unsupported_claims` predicate, the YAML encodes:

| Predicate | Rationale (system_prompt source) |
|---|---|
| `no_statutory_citations` | Lines 566-570: map facts to CATEGORIES, never cite statute numbers |
| `no_outcome_predictions` | Lines 517-518: forbid "this will likely succeed" language |
| `no_strategy_language` | Lines 515-517: forbid "you should argue..." phrasing |
| `non_party_detected_when_present` | Lines 549-560: court cannot order relief against non-parties |
| `jdf_form_reference_correct_or_title_only` | Line 524: if uncertain, official title only + coloradojudicial.gov |
| `mythology_enforcer_passed` | Line 1481: Session 409 post-validation contract |
| `declaration_contains_penalty_of_perjury_language` | Colorado sworn-declaration statutory requirement |

## SIGN cycle T1→T3

**T1 (tool-grounded verification via Rigby ORM):**
- CLAIM 1 (volume): **PASS** — orm_inspect_tool.filter returned total_matching=5 30d + 12 all-time, all `completed`, all `error_message=''`.
- CLAIM 2 (line refs): **PASS** — repo_tool.read_file spot-checked class def at 474, `def execute` at 1229, `_validate_task` at 1252-1257, `message` at 1414, `data` block at 1424-1426, `_save_to_deliverable` title at 1464. All exact matches.
- CLAIM 3 (tool count): **DISAGREE** — my header said "9 tools", actual is 10 declared in system_prompt (+1 more in tools list). Fixed in-PR.
- CLAIMS 4, 5 (YAML structure + devops parity): **DISAGREE** for honest reason — Rigby didn't re-verify in T2 turn (no thread tool_runs). Independently confirmed via Claude's Python `yaml.safe_load` + branch/why structural check (0 missing whys, ≤2 branches on all one_of blocks).

**T2 zoom-out folds:** 4 surfaced.
1. Tool count 9 → 10 declared (11 total-schema) — **in-PR fix**.
2. "NEW SHAPE" → "routing branch" phrasing in header + `legal_happy_05` notes — **in-PR fix**.
3. Evidence-tier ladder mechanization (Fallback A/B/C prose vs. structured selectors for S2963 validators) — **forward-carry to S2962 arc-close** per Chris ratification.
4. Coverage-limits section — added one actionable conclusion line — **in-PR fix**.

**T3 disposition:** REVISE; all 3 in-PR fixes applied. Chris D-verdict via terminal: `"yes ship it and forward-carry fold 3"`.

## Rigby Tool Gap Ledger (this session)

- **RE-HIT expected at close cascade — Ledger #16 will hit for the 12th cumulative time** when `deliverable_tool.create` runs on the content-mirror deliverable (initiative_phase_doc + missing_initiative_id → sticky diagnostic → clear via `deliverable_tool.clear_diagnostic`).
- **NO CHANGE — Ledger #17 count remains 4** — Chris used terminal ratification path directly (`yes ship it and forward-carry fold 3`), bypassing Chat UI relay. Consistent with S2957 + S2958 precedent. Design task `f3f140f9-87bf-488b-8757-eab5d8058f45` remains valid for the Chat-UI-only path.
- **Rigby T1 tool_runs discipline HELD** — she ran real ORM queries + repo_tool reads at exact line refs (not rubber-stamp). Explicit DISAGREE on CLAIMS 4/5 for honest "no thread tool_runs" reason is a positive signal per `feedback_verify_rigby_tool_runs_before_trusting_sign` (opposite of rubber-stamp).

## Post-merge

Spec-only PR (YAML config, no code) → no worker impact → **no `make celery-recycle` required** (PLAYBOOK-7.4.4 applies to code-shipping PRs).

## Governance provenance

- **Chris D-verdict:** via terminal 2026-07-25 (`yes ship it and forward-carry fold 3`).
- **Content mirror deliverable:** filled at close cascade.
- **Ratification envelope deliverable:** filled at close cascade.

## Forward carry (queued for S2960+)

**New at S2959:**
- **Fold 3 — Evidence-tier ladder mechanization (canon-wide, all 5 slices)** — Rigby-flagged, Chris-ratified for S2962 arc-close discussion. Joins the two prior canon_v2 candidates parked at S2956 + S2957 (`health_status` open-world semantics + dual-path enum). Question: does S2963 validator implementation consume prose derivation_specs via text-parsing, or does canon need typed evidence-tier entries (selector + predicate + applicability)?

**Unchanged from S2958:**
- WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR (deferred; must land before S2963 to enable v1.1 tightening of `workflow_orchestration_agent.yaml`).
- Fold A (S2958) — arc-substrate must-have-tool_runs rule → S2962 arc-close.
- Fold C (S2958) — ambiguous_input vs bad_input remediation posture separation → apply as authoring discipline in remaining slices.

**Carry forward from S2957:** health_status dual-path enum for advisory-vs-config-gen agents (canon_v2 candidate for S2962).

**Carry forward from S2956:** Ledger #16 recipe drift dual-route documentation; `orm_inspect_tool` distinct-count guardrail; health_status derivation refactor for open-world agents (canon_v2 for S2962); Tier-1 canon uniformity review (S2962).

Complete carry-forward queue lives in `00-START-NEXT-SESSION.md`.

## Files touched this session

- **NEW** `evals/tier1/legal_doc_drafter_agent.yaml` — fifth Tier-1 canonical prompt suite (794 lines, 13 prompts, 5 categories).

Plus close-cascade files:
- **UPDATE** `00-START-NEXT-SESSION.md` — S2960 first-action = ContentWriterAgent YAML slice 6.
- **NEW** `docs/handoffs/SESSION_2959_GOLDEN_EVALS_SLICE_5_LEGAL_YAML.md` — this file.
- **UPDATE** `tools/pa_local.sh` — wrapper pin bump to S2960 pin.

## References

- S2955 slice 1 (SIA): `docs/handoffs/SESSION_2955_GOLDEN_EVALS_SLICE_1_SIA_YAML.md`
- S2956 slice 2 (Research): `docs/handoffs/SESSION_2956_GOLDEN_EVALS_SLICE_2_RESEARCH_YAML.md`
- S2957 slice 3 (DevOps): `docs/handoffs/SESSION_2957_GOLDEN_EVALS_SLICE_3_DEVOPS_YAML.md`
- S2958 slice 4 (Workflow): `docs/handoffs/SESSION_2958_GOLDEN_EVALS_SLICE_4_WORKFLOW_YAML.md`
- Arc open scoping: `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md`
- Rigby Tool Gap Ledger deliverable: `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- Chat UI relay design task: `f3f140f9-87bf-488b-8757-eab5d8058f45`
