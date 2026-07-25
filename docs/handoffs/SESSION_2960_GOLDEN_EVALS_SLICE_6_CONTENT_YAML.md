# SESSION 2960 — Golden Evals Tier-1 slice 6: ContentWriterAgent YAML

**Date:** 2026-07-25
**Session:** S2960
**Arc:** Golden Evals (S2954+ open)
**Slice:** 6 of 8 Tier-1 YAMLs
**HEAD at slice merge:** `10b6b3ab1`
**HEAD at close (post-cascade):** filled at close cascade merge
**PR shipped:** [#3561](https://github.com/clwest/donkey-betz-platform/pull/3561)

---

## What shipped

`evals/tier1/content_writer_agent.yaml` — 950 lines, 13 prompts, sixth canon_version=1 file.

**Coverage:** 5 happy path + 2 each tool_timeout / data_unavailable / ambiguous_input / bad_input.

**Substrate reference:** `evals/tier1/legal_doc_drafter_agent.yaml` @ `8fa60421f` (S2959 slice 5 canon).

**Agent under test:**
- Source: `core/agents/content_writer_agent.py:207` (ContentWriterAgent class).
- File size: 2,419 lines / 105.3 KB.
- Five execution routing branches in `execute()` at line 707 (all inside same agent contract, framed as routing branches per S2959 canon addition 10):
  - **(A) SELF-DESCRIPTION shortcut** — keyword-triggered at line 776-785 on "state your name" / "who are you" / etc. No LLM call.
  - **(B) DIAGNOSTIC mode** — triggered when `context.diagnostic_mode=true` at line 796-801. Dispatches to `_execute_diagnostic` at line 1649. Raw task→body assignment, no LLM rewrite (Session 1185 F1).
  - **(C) REWRITE mode** — triggered when `review_feedback + original_draft` present at line 824-851. Dispatches to `_execute_rewrite` at line 1463. Single LLM call, no `tool_calls`.
  - **(D) DIRECTED mode** — triggered when `research_summary + (editor_feedback OR required_checks)` present at line 853-868. Dispatches to `_execute_directed` at line 1722. Single LLM call, no `tool_calls`.
  - **(E) STANDARD mode** — default at line 870+. Single LLM call via `_generate_content` at line 2093.
- `tools = []` at line 257 by design — no `tool_calls` dispatch on any branch.
- 7 content types (`CONTENT_TYPES` at line 151-193): blog_post / podcast_script / video_script / article / social_thread / newsletter / internal_document.
- 14 aliases (`_CONTENT_TYPE_ALIASES` at line 901-916).
- 6 tone presets (`TONE_PRESETS` at line 197-204).

## Volume snapshot (DB-verified via direct ORM at authoring T0 + Rigby T2 SIGN)

- **30d executions** (`owner_agent="ContentWriterAgent"`, `created_at >= 2026-06-25T00:00:00Z`): **7 rows** (6 completed / 0 failed / 1 cancelled).
- **All-time**: **23 rows** (20 completed / 2 failed / 1 cancelled). Earliest 2026-06-19, latest 2026-07-24.
- **Real failures** (non-empty `error_message`, all-time): **3 rows**
  - 2× 60-min Celery watchdog kill (2026-06-19 Operator Edge newsletter, 2026-06-23 SMOKE_TEST)
  - 1× S2800 worker-restart cancellation (2026-07-24 brand video workflow doc)
- **30d task-shape distribution**: 5/7 are fitness-wearable brand video variants (video_script); 1× receipt test dispatch; 1× morning-brief workflow smoke test.

## Coverage limits (honestly called out in YAML header)

1. **THIN TRAFFIC** — 7 30d is 2nd-thickest in arc (SIA 37 / Research 37 / DevOps 13 / Workflow 9 / Legal 5).
2. **NARROW DOMAIN CONCENTRATION** — 5 of 7 30d prompts are the same fitness-wearable brand-video variant. Zero 30d against blog_post / podcast_script / article / social_thread / newsletter / internal_document.
3. **ZERO 30d AGENT-SIDE FAILURES** — the 1 30d cancellation was worker-restart (S2800), not agent-side. All 3 real all-time failures have platform-generic causes.
4. **CONTENT-DOMAIN BUYER-FACING RISK** — content hallucination (fabricated facts / stats / quotes / sources) has buyer cost; encoded as 5 domain-sensitivity acceptance predicates per S2959 canon addition 9.

**Actionable conclusion (per S2959 Rigby T2 fold 4 pattern):** treat as SCHEMA + HALLUCINATION-INVARIANT + BUYER-EXPECTATION validation, not performance/reliability assurance. Re-baseline at S2962 arc-close if traffic grows past 50 30d executions across ≥3 content types.

## Rigby SIGN cycle summary

### T1 tool-grounded verification

- **CLAIM 1 (ORM volume snapshot):** PASS — all 5 sub-claims confirmed via `orm_inspect_tool.filter` + `count_by`.
- **CLAIM 2 (line refs in content_writer_agent.py):** PARTIAL PASS — sub-claims (a-j) PASS via `repo_tool.read_file`; (k-p) UNVERIFIED at T1 (completed at T2).
- **CLAIM 3 (CONTENT_TYPES + aliases):** REJECT — I claimed 13 aliases; Rigby counted 14 in the source. **Correct.**
- **CLAIM 4 (YAML canon adherence):** UNVERIFIED at T1 (completed at T2).
- **CLAIM 5 (real failure replay):** UNVERIFIED at T1 (completed at T2, DISAGREE).

### T2 zoom-out folds

- **Fold A** — encoding 5 routing branches when 4 are zero-30d-traffic risks over-specifying low-evidence pathways. → **FORWARD-CARRY to S2962 arc-close** (canon-wide substrate question; contradicts S2959 canon addition 10 which framed routing branches as canonical; needs arc-close discussion).
- **Fold B** — 5 domain-sensitivity predicates is too granular for Tier-1 minimalism; collapse to 2-3. → **FORWARD-CARRY to S2962 arc-close** (canon-wide normalization: Legal has 7, Content has 5, DevOps/Workflow have 2-3; needs arc-close discussion).
- **Fold C** — "verbatim preservation contract" language for diagnostic mode is overstated given code is `body = task or ""`. → **ACCEPTED in-PR** (softened to "raw task→body assignment, no LLM rewrite" throughout).
- **Fold D** — line-number anchoring throughout YAML is brittle to formatter runs. → **FORWARD-CARRY to S2962 arc-close** (applies to all 5 shipped YAMLs; substrate refactor discipline).
- **Fold E** — `_CONTENT_TYPE_ALIASES` lives inside `execute()` (harder to test independently). → **RECORD-ONLY** (code-quality note about content_writer_agent.py, not a YAML content issue).

### T2 CLAIM 5 DISAGREE + resolution

Rigby caught that `content_timeout_01_watchdog_kill.input` was framed as "REAL FAILURE REPLAY — this exact prompt shape is the actual 2026-06-19 failure row" but the YAML text was a **reconstruction** rather than verbatim replay:
- DB row `5c103be3-92ff-49b0-9ef5-bcf6cc39fea3` `task` begins: `"Write the Operator Edge weekly newsletter for the week of June 12 – June 19, 2026. Use ONLY the evidence provided below. Do NOT invent sources.\n\n# Operator Edge — Weekly Intelligence Briefing\n**Week of June 12 – June 19, 2026**\n\nWrite an 900–1200 word briefing..."` (500+ chars with structured spec).
- YAML `input`: `"Write the Operator Edge weekly newsletter for the week of June 12–June 19, 2026. ... Include: subject line, preview text, greeting, 3 sections ..., CTA, and sign-off. Target 800 words."` (different structure, 800 vs 900-1200 word target, en-dash spacing differs).

**Resolution (Option 2 per Rigby's recommendation):** softened notes language from "REAL FAILURE REPLAY" to "REPRESENTATIVE OF REAL FAILURE PATTERN (not a verbatim replay)" with honest description of the shape delta. Preserves eval reproducibility without coupling to the specific historical smoke-test spec.

### In-PR fixes applied

1. **Alias count 13 → 14** (Rigby-counted from source at line 901-916).
2. **`_execute_rewrite` line ref 1465 → 1463** (3 occurrences fixed).
3. **"verbatim preservation contract" → "raw task→body assignment, no LLM rewrite"** (4 occurrences softened per Fold C).
4. **`content_timeout_01` notes softened** per T2 CLAIM 5 DISAGREE resolution.

### T3 verdict

**PASS** after in-PR fixes verified via `repo_tool.read_file` on the changed lines.

## Chris D-verdict

`yes` via terminal 2026-07-25. Ledger #17 count unchanged at 4 (Chris used terminal path, not Chat UI relay — consistent with S2957/S2958/S2959 pattern).

## Twin mirrors created

- **Content mirror** (initiative_phase_doc, category=governance): `74436669-345c-4234-9e21-7b4d5aebc9a6`
  - Ledger #16 re-hit **13th cumulative** — diagnostic-cleared via `deliverable_tool.clear_diagnostic` with reason "S2960 close-cascade: twin mirror initiative_phase_doc intentionally unlinked to an Initiative; suppress missing_initiative_id diagnostic per Ledger #16 expectation."
- **Ratification envelope** (ratification_record, category=governance): `c97d6dc8-3500-4bd1-9c4d-8947ea3b82cb`
  - Diagnostic clean on create (matches S2959 pattern for ratification_record deliverable_type).

## Post-merge

PR #3561 was spec-only (YAML config, no code changes) → **no `make celery-recycle` required** per PLAYBOOK-7.4.4 (which applies to code-shipping PRs).

## Deferred to S2962 arc-close

**New at S2960 (folds):**
- Fold A — 5-branch encoding vs traffic reality (canon-wide substrate question).
- Fold B — Domain-sensitivity predicate count discipline across Tier-1 (Legal 7 / Content 5 / DevOps 2-3 / Workflow 2-3 / Research 2-3 / SIA 2-3).
- Fold D — Line-number anchoring brittleness across all 5 shipped YAMLs.

**Carry forward from prior slices:**
- **S2959 fold 3** — Evidence-tier ladder mechanization (canon-wide, all 5 slices).
- **S2959 tool bug** — `orm_inspect_tool.count_by` group_by argument not propagating (Ledger #18 candidate).
- **S2958 F1** — WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR (can happen pre-S2963).
- **S2957 Fold #1** — `health_status` dual-path enum add for advisory-vs-config-gen agents.
- **S2956 Fold #5** — `health_status` derivation over-degrade for open-world agents.
- **S2955** — Bound-annotation discipline for volume claims.

## Golden Evals arc progress

- ✅ S2955 slice 1 — SystemIntelligenceAgent (PR #3551)
- ✅ S2956 slice 2 — ResearchAgent (PR #3553)
- ✅ S2957 slice 3 — DevOpsAgent (PR #3555)
- ✅ S2958 slice 4 — WorkflowOrchestrationAgent (PR #3557)
- ✅ S2959 slice 5 — LegalDocDrafterAgent (PR #3559)
- ✅ **S2960 slice 6 — ContentWriterAgent (PR #3561)**
- ⏭ S2961 slice 7 — CompetitorAnalysisAgent
- S2962 slice 8 — PersonalAssistant (Rigby) + arc-close review (canon uniformity + canon_version=2 open discussion — health_status open-world + dual-path enum concerns + arc-substrate tool_runs rule + evidence-tier ladder mechanization + 5-branch encoding + predicate count normalization + line-number anchoring discipline)

## S2961 first-action

Author `evals/tier1/competitor_analysis_agent.yaml` — 7th Tier-1 slice. Locate agent source via `grep -r "class CompetitorAnalysisAgent" core/agents/` and open the file. Pull 30d + all-time volume snapshot via direct ORM before authoring (mirror S2960 T0 shape).

## Files shipped this session

- **NEW** `evals/tier1/content_writer_agent.yaml` — 950 lines, 13 prompts (this session slice).
