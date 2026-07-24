# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2929 SHIPPED A1 BASEBUSINESSRESEARCHAGENT FOLD REMEDIATION + SURFACED 3 NEW 1ST-INSTANCE FOLD CANDIDATES. **S2930 OPENS WITH GOVERNANCE R1/R2/R3 DECISION on the S2928 Fold ratification** (verified 1/1 not 2/2 after ORM check).

**Refreshed 2026-07-24 (S2929 close).** Chris ratified Option A1 at S2929 open. Root cause pivoted twice mid-session (S2928 handoff shape description was wrong; CompetitorAnalysisAgent 1st-instance appears misclassified). Shipped as **PR #3493** — base-class-only fix. Real blast radius = `MarketingStrategyAgent` only (other subclasses either don't inherit unchanged execute() or route to a different class entirely). E2E verify PASSED: positive path unchanged, 12,651-char real analysis produced.

**PRs shipped this session:**
- u-d-b PR [#3493](https://github.com/clwest/donkey-betz-platform/pull/3493) — S2929 A1 BaseBusinessResearchAgent Content-Shape FAIL Fold remediation, merged at `1465df616`.
- u-d-b PR `<TBD>` — S2929 close cascade (handoff + 00-START refresh + wrapper pin bump).

**Code changed this session:**
- `core/agents/business/base_business_research_agent.py:485-517` — fail-loud gate on empty synthesis when data was gathered
- `core/agents/business/base_business_research_agent.py:685-698` — polymorphic content extraction in `_execute_gpt_loop` fallback (fixes `hasattr(dict, 'content')` bug)
- `core/tests/test_base_business_research_agent_synthesis_gate.py` (NEW, 5 tests, all pass)

**Post-merge live-dispatch (per PLAYBOOK-7.4.4):**
- PR #3493 recycled clean at `sha=1465df616`.
- Rigby dispatch 1 (`content_strategy_agent` execution `21460668-...`): surfaced routing anomaly — tool routes to `core.agents.strategy.ContentStrategyAgent` NOT to `core.agents.business.ContentStrategyAgent` (which has my fix). Not a valid E2E target.
- Rigby dispatch 2 (`marketing_strategy_agent` execution `86be25b0-...`): 101.8s completion, all 14 keys present, `data['analysis']` = 12,651 chars of real markdown. **GATE PASSED — positive path unchanged by fix.** Fail-loud branch stayed silent because GPT successfully called `synthesize_marketing_strategy` this time (invariant tests cover both branches).

Full session context: `docs/handoffs/SESSION_2929_A1_FOLD_REMEDIATION.md`.

---

## S2930 open sequence — GOVERNANCE DECISION REQUIRED

**Step 1 — Chris D-verdict on S2928 Fold ratification (see handoff Governance section for full framing):**

- **Option R1 (de-ratify):** Move Fold back to candidate status; require 2nd real instance. Formal but honest.
- **Option R2 (re-scope Fold class):** Narrow scope to "BaseBusinessResearchAgent subclasses inheriting unchanged base execute()" — that's `MarketingStrategyAgent` only. Fold-of-one; S2929 PR closes it. Cleaner artifact.
- **Option R3 (defer):** Leave as-is; watch for future BaseBusinessResearchAgent subclass FAILs.

Recommended: R2 (re-scope) — matches actual verified blast radius, closes the Fold cleanly, doesn't invalidate the S2928 ratification ceremony.

**Step 2 — Same 5-option S2930 arc scope surface (unchanged from S2929 open):**

- **(A) NET-NEW ENGINEERING** per Chris directive — propose 1-3 candidates
- **(B) Slice 5-hardening** — 3-4 executable invariants deferred at S2928 fork A
- **(C) Slice 6 sweep continuation** — `td_handlers_content.py` (6 tools)
- **(D) Docs restructuring arc** — unblocked at S2800, still queued
- **(E) Rigby tool-gap ledger slate** — S2928 entry `orm_inspect_tool` allowlist expansion (I fell back to Django shell 3× this session — real friction)

**Recommended framing for T0 SIGN:** Chris R1/R2/R3 first (2-min decision), then S2930 arc scope. Present as plain-English decision per `feedback_plain_english_decision_framing_for_chris`.

---

## What's forbidden at S2930 (D6 MORATORIUM still in force)

All S2925/S2926/S2927/S2928 forbidden entries carry forward.

**S2929 new forbidden entries (all 1st-instance — require corroborating trigger before promotion):**

- **No "handoff shape misclassification" Fold promotion without 2nd instance.** 1st (S2929 discovered S2928 handoff described `data.keys()=['query']` when actual shape had all 10 keys). Watch for 2nd handoff-vs-reality drift in future close cascades.
- **No "tool-to-class routing anomaly" Fold promotion without 2nd instance.** 1st (S2929 `content_strategy_agent` tool → `strategy.ContentStrategyAgent` not `business.ContentStrategyAgent`). Watch for 2nd cross-namespace dispatch collision.
- **No "Fold ratification over-count via unverified handoff description" Fold promotion without 2nd instance.** 1st (S2929 S2928 Fold 2/2 → verified 1/1 after ORM check). Watch for 2nd ratification-quality issue.

**S2928 forbidden entries carry forward** — S2928 promoted BaseBusinessResearchAgent Content-Shape FAIL Fold is now **REMEDIATED** for its actual verified surface (MarketingStrategyAgent). Governance status pending R1/R2/R3 above.

---

## What's queued but deferred (do NOT open unless Chris directs)

- **CompetitorAnalysisAgent hardening candidate** — S2929 Chris D-verdict deferred (no evidence of current FAIL after ORM verification). Revisit if future evidence surfaces.
- **`content_strategy_agent` tool-to-class routing anomaly** — S2929 substrate finding. `business.ContentStrategyAgent` is unreachable via tool dispatch (dead code from dispatch surface). Candidate for dead-code audit or explicit deprecation. Consider in docs restructuring arc scoping.
- **`orm_inspect_tool` allowlist expansion** (S2928 Ledger entry) — MEDIUM priority; friction confirmed at S2929 (fell back to Django shell 3×).
- **Slice 5-hardening session** — 3-4 executable invariants deferred at S2928 fork A. Unchanged.
- **Ledger #34 broader stale-model sweep** — multi-hour engineering.
- **Bundled dev-env drift slate** — S2919 narrative + S2925 Ledger #33/#34 legacy + AgentTaskExecution pre-existing pyright drift + S2927-observed `td_handlers_agents.py` pyright drift.
- **Phase 0 heading fixes (8 tools)** — doc-only PR that clears remaining parity mismatches.
- **Slice 1.5b autopilot mutations** — staged-enforcement session per pre-commit note.
- **S2907 harness-substrate: MLEngine per-invocation NLP-model load** — unchanged.
- **S2908 doc-fix candidate + Ledger candidate: media_tool.delete IRREVERSIBLE** — 2/3. Unchanged.
- **S2909-S2928 Ledger candidates** — unchanged.
- **Content-mirror auto-flagged as diagnostic (S2909 Ledger #31)** — unchanged.
- **FT-5 minimal_safe_args_v2 tracker (S2909 Ledger #32)** — unchanged.
- **S2919 narrative_tool dev-env drift** — unchanged.
- **S2925 Ledger #34 (LOW)** — broader stale-model latent bug; multi-hour cleanup deferred.
- **S2926 Ledger candidate — AgentTaskExecution pre-existing pyright drift** — bundled dev-env drift candidate.
- **R1 fleet reject-mode flip** — deferred.
- **Docs restructuring arc** (`project_docs_restructuring_arc_queued`) — Chris-ratified S2800, still queued.
- W2 #1 / #2b / #2c — pending Chris re-slate.
- W2-2b bounded attribution expansion — Chris skipped at S2849.
- LLMCallLog field splits — migration required.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os side follow-ons.

---

## Sweep progress tracker (Path B ratified S2892) — UNCHANGED at S2929

**Slice 1 — `td_handlers_ops` (17 registered tools):** UNCHANGED.
**Slice 2 — `td_handlers_agents` (25 tools):** CLOSED at S2912.
**Slice 3 — `td_handlers_core` (22 tools):** CLOSED at S2917 (22/22).
**Slice 4 — `td_handlers_gateway` (17 tools):** CLOSED at S2924 (17/17).
**Slice 5 — `tool_dispatcher` (14 tools):** CLOSED at S2928 (14/14). ✅

**Total remaining tools to close:** **15 across 8 handler files** (unchanged — S2929 shipped no PA-tools sweep work).

**Substrate arcs CLOSED at S2929:** none. S2929 shipped 1 engineering PR (agent correctness fix) + 3 new 1st-instance forbidden-entry candidates.

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force — refreshed at S2929 close)

1. **Spend lane:** A4 warm-up uses a separate budget lane/cap and must NOT consume or contend with A1 shipping spend. **S2929: zero A4 spend** — pure engineering (agent correctness fix + close cascade).
2. **Evidence tag:** All A4 artifacts are labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up is constrained to a fixed timebox and fixed send count (3-5 total intros).
6. **No bespoke follow-ups:** A4 warm-up prohibits custom follow-ups / custom research / custom deliverables.

---

## For fuller A1 W1 + W2 arc context (spans S2846 → S2929)

See:
- **S2929 handoff (current):** `docs/handoffs/SESSION_2929_A1_FOLD_REMEDIATION.md`
- **S2928 handoff:** `docs/handoffs/SESSION_2928_SLICE_5_CLOSE_BATCH_4.md`
- **S2927 handoff:** `docs/handoffs/SESSION_2927_SLICE_5_BATCH_3.md`
- **S2926 handoff:** `docs/handoffs/SESSION_2926_SLICE_5_BATCH_2.md`
- **S2925 handoff:** `docs/handoffs/SESSION_2925_SLICE_5_BATCH_1.md`
- **S2924 handoff:** `docs/handoffs/SESSION_2924_SLICE_4_CLOSE_BATCH_7.md`
- **Slice 5 CLOSE artifact:** `docs/audits/pa_tools/substrate/slice_5_close_artifact.md`
- **T1b canonical template file:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **S2929 regression test:** `core/tests/test_base_business_research_agent_synthesis_gate.py` (5 tests, all pass)
- **BaseBusinessResearchAgent content-shape FAIL Fold (RATIFIED S2928, REMEDIATED S2929, governance pending R1/R2/R3):** engineering item in Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` — deliverable `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5`.
- **Rigby Tool Gap Ledger deliverable:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (no new entries this session — existing `orm_inspect_tool` allowlist gap still valid).
- **PA tools sweep methodology:** `docs/audits/PA_TOOLS_GAP_MAP.md` + `docs/PA_TOOL_AUDIT.md` (both auto-generated) + `docs/research/tools/validation/*.md` (100 per-tool validation docs post-S2928)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1-S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
