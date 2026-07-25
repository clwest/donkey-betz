# SESSION 2954 — Golden Evals arc open (Tier-1 ratified + Day-1 fault-injection scope)

**Date:** 2026-07-25
**Status:** CLOSED — PR #3549 merged, twin mirrors persisted + ORM-cleaned, arc-open scoping doc live.
**HEAD at close:** `9f25abdb1` (post-arc-open) → close-cascade PR will advance to next SHA
**Merge commit:** squash `9f25abdb1` (PR #3549, doc-only, no worker impact — no recycle required)
**Twin mirrors (this session):**
- **S2954 Golden Evals arc open** — Content mirror `1f79856a-9f9a-4c84-be17-d8884b72e65f` (Donkey Betz workspace, `initiative_phase_doc`, category `governance`, diagnostic ORM-cleared — Ledger #16 re-hit **7th time cumulative**); Ratification envelope `b38ba743-9050-476f-8f70-175cf8aafed6` (Donkey Betz workspace, `ratification_record`, `category='governance'`, diagnostic already null on create).

---

## What shipped

**S2954** — Golden Evals arc opened per S2953's ratified next-action. Tier-1 8-agent list ratified + Day-1 fault-injection commitment folded in (addresses Rigby's SIGN WARN "sunny-day theatre" concern). Arc-open scoping doc at `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md`.

### Session shape

1. **Opened per S2953 ratified first-action** — "S2954 first-action = open Golden Evals arc" (Chris `yes+A` at S2953 close). Session-open verifications: drift scanner shape (83/92/59/1 → 77+2), wrapper pin fresh (`pa-50542bacf8014a20`), gap-map lint (see §Gotcha below).
2. **Routed Tier-1 proposal to Rigby via PA chat** — requested (a) 30d `AgentExecution` volume grounding (b) Tier-1 candidate proposal for A1 Platform/ML/SRE+compliance buyer (c) mandatory zoom-out ask per `feedback_zoom_out_ask_per_rigby_sign`.
3. **Rigby SIGN turn 1** — real tool queries executed (`orm_inspect_tool count_by AgentExecution`); returned volume-grounded data with `tool_runs` populated (not rubber-stamping). Top 30d: PredictionMarketAnalyst 342, SportsOddsAnalyst 332, agent `0cfe523f` (ArbitrageDetector cluster) 307, Rigby 227, then long tail with SystemIntelligenceAgent 33, DevOps 11, LegalDoc 6.
4. **Rigby SIGN turn 2** — narrative Tier-1 proposal + zoom-out. **Verdict: WARN** (not F-BLOCKING) — list is sound but arc becomes theatre without Day-1 fault-injection + reliability contract.
5. **Reconciliation** — Claude verified all 8 Tier-1 names resolve in `core/agent_router.py` AGENT_MAP (both `WorkflowAgent` and `WorkflowOrchestrationAgent` exist; Rigby correctly picked orchestration as the "agentic glue"). Fault-injection commitment folded into arc scope as Day-1 (not phase-2). Joint recommendation to Chris.
6. **Chris D-verdict** — `yes` via Chat UI 2026-07-25. Ratifies Tier-1 list + Day-1 fault-injection scope.
7. **Ship** — PR #3549 (doc-only, 95 lines) → merge (`gh pr merge --admin`) → twin mirrors → ORM-cleanup on content mirror.

## PRs shipped this session

- u-d-b PR **#3549** — S2954 Golden Evals arc-open scoping doc (`docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md`, +95/-0). Doc-only, no worker impact.
- u-d-b PR **#TBD** — S2954 close cascade (handoff + 00-START refresh + wrapper pin bump).

## Files shipped this session (S2954 slice)

- **NEW** `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md` — arc-open scoping doc (7 sections: motivation / Tier-1 list ratified / Day-1 fault-injection scope / arc structure / Rigby SIGN cycle / deferred / limitations).

## Governance

- **Tier-1 8-agent list ratified:** `SystemIntelligenceAgent` / `ResearchAgent` / `DevOpsAgent` / `WorkflowOrchestrationAgent` / `LegalDocDrafterAgent` / `ContentWriterAgent` / `CompetitorAnalysisAgent` / `PersonalAssistant`
- **Explicitly EXCLUDED despite top-4 30d volume:** PredictionMarketAnalyst (342), SportsOddsAnalyst (332), ArbitrageDetector-cluster (307), Rigby-as-agent-row (227 — already Tier-1 as PersonalAssistant). Reason: sports-vertical for the A1 Platform/ML/SRE+compliance buyer; keep Tier-2 as "pipeline scale proof."
- **Day-1 fault-injection scope ratified:** 5 scenario categories per Tier-1 agent (happy path / tool timeout / data unavailable / ambiguous input / bad-malformed input); reliability contract required (output fields, citations, uncertainty markers, refusal behavior).

## Rigby Tool Gap Ledger updates

- **RE-HIT (Ledger #16, 7th time cumulative)** — `deliverable_tool.create` diagnostic-flag bug on `initiative_phase_doc`. S2954 content mirror `1f79856a` flagged with `diagnostic_status='diagnostic'` + `diagnostic_code='missing_initiative_id'` + full diagnostic_payload; cleared via ORM. Ratification envelope `b38ba743` was clean on create (matches the pattern that `ratification_record` doesn't trigger the initiative-id flag).
- **NEW — Ledger #17 candidate** — Rigby Chat UI doesn't relay Chris's ratification responses back to Claude terminal. Observed TWICE this session: Chris said `yes` (Tier-1 ratification) and later said `close` (S2954 next-move A/B) via Chat UI — Rigby only echoed his message back to him, did not route it back to the terminal-side conversation despite explicit "route it back to me verbatim" instruction in both dispatches. Chris had to relay manually via the terminal. Workaround-of-last-resort: Chris types response into terminal. Root cause hypothesis: Rigby's PA turn treats Chris's follow-up as a new conversation event, not as a routed-callback. Design task; do not need to work around at CLI level (Chris relays fine when the gap is known).

## Gap-map drift found at S2954 open

- 00-START-NEXT-SESSION.md `## READ THIS FIRST` asserted `100 validated_full / 0 untested`. Actual at HEAD `ee3bcf4c9`: `100 validated_full / **2 untested**`. Untested tools are `agent_capability_drift_tool` + `agent_job_status` — both S2953/S2952-shipped, untested-by-design at that point. **Not S2954-introduced.** Correction is folded into the S2954 close-cascade 00-START refresh.

## Cross-session sweep tally

This terminal session shipped **4 PRs**: #3545 (S2952 pre-A1 capability fixes) + #3546 (S2952 close cascade) + #3547 (S2953 drift scanner) + #3549 (S2954 arc-open doc). Three full close cascades will execute by end (S2952 + S2953 + S2954). Wrapper pin rotated three times: `pa-717acd2509014b97` → `pa-eca2a60d039541ac` → `pa-50542bacf8014a20` → (S2955 pin filled at S2954 close).

## Next session (S2955) opens

**S2955 first-action = author first Tier-1 agent's canonical prompt suite.**

**Recommended starting agent: `SystemIntelligenceAgent`** — highest 30d execution volume among Tier-1 (33 exec, meaningful signal); represents the "platform truth" class most directly evaluable by the A1 buyer.

**Artifact shape:**
- File: `evals/tier1/system_intelligence_agent.yaml` (new `evals/` tree at repo root; matches 00-START S2955+ spec).
- Contents: 5–20 prompts covering the 5 ratified scenario categories:
  - `happy_path`: canonical health/ops query; expected structured response
  - `tool_timeout`: downstream dependency exceeds budget; agent must degrade gracefully
  - `data_unavailable`: KB empty / spider stale; agent must respond with explicit uncertainty
  - `ambiguous_input`: under-specified query; agent must ask clarifying question, not guess
  - `bad_input`: schema-violating payload; agent must reject cleanly
- Each prompt: `id`, `category`, `input`, `expected_output_shape` (JSON Schema fragment), `acceptance_criteria` (list of reliability-contract checks: required fields, citation presence, uncertainty markers, refusal behavior).

**No validators or harness code yet** — those are S2956 (validators) and S2957 (`run_golden_evals` mgmt cmd + `GoldenEvalRun` model + beat task).

**Estimated 3–5 sessions minimum** to close the whole Golden Evals arc; S2955 is 1 agent's YAML = 1 session slice.

## Deferred queue (updated at S2954 close)

- **Curate `capabilities_exceptions.yaml`** (from S2953) — 77 active findings at HEAD `9f25abdb1`. Walk each; tier-classify or fix. Good parallel work during Golden Evals arc.
- **Fix `run_agent` dispatch-response agent-name echo** (from S2952) — echo mapping-canonical CamelCase, not input string.
- **Drift scanner invariant 4 (rerouted-must-be-labeled)** (from S2953) — requires `AgentRerouteEntry`-style queryable model.
- **Rigby Chat UI response-relay gap** (**NEW this session, Ledger #17 candidate**) — Chris's Chat UI responses aren't routed back to Claude terminal even when explicit instruction is present.
- All prior long-standing carry-forward from S2951/S2952/S2953 (see 00-START).

## Chris's 4 A1 Phase 1 gating questions (unchanged)

From scoping deliverable `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`. Still block Phase 1 code open after Golden Evals arc closes:

1. Minimum evidence standard we promise (run IDs + failure signature samples vs metrics only)?
2. Default turnaround SLA hittable without heroics?
3. Sell as agent-system audit (end-to-end) or toolchain reliability audit (tools/contracts) first?
4. Legal posture for customer logs (retention, deletion guarantee, allowed data types)?

## Twin-pointer summary (per `feedback_twin_pointer_docs_at_boundaries`)

| Artifact | Repo path | Workspace deliverable |
|---|---|---|
| S2954 arc-open scoping doc | `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md` | Content mirror `1f79856a-9f9a-4c84-be17-d8884b72e65f` (Donkey Betz workspace) |
| S2954 arc-open ratification | (this handoff §Governance) | Ratification envelope `b38ba743-9050-476f-8f70-175cf8aafed6` (Donkey Betz workspace) |
| S2954 handoff | `docs/handoffs/SESSION_2954_GOLDEN_EVALS_ARC_OPEN.md` | (this doc) |
| A1 Wedge scoping (unchanged, S2951) | — | `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6` |
| A1 Wedge ratification (unchanged, S2951) | — | `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b` |
| Rigby Tool Gap Ledger | — | `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`) |
