# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2954 CLOSED. Golden Evals arc OPENED (PR #3549, HEAD `9f25abdb1`) as the third capability-substrate leg between S2953 Drift Scanner and A1 Reliability Audit Phase 1. Chris ratified Tier-1 8-agent list + Day-1 fault-injection scope via Chat UI 2026-07-25 after joint Claude+Rigby recommendation (Rigby T2 verdict WARN on "sunny-day theatre" concern → folded into Day-1 fault-injection commitment). Tier-1 list: `SystemIntelligenceAgent` / `ResearchAgent` / `DevOpsAgent` / `WorkflowOrchestrationAgent` / `LegalDocDrafterAgent` / `ContentWriterAgent` / `CompetitorAnalysisAgent` / `PersonalAssistant`. Explicitly EXCLUDED despite top-4 30d volume: PredictionMarketAnalyst (342), SportsOddsAnalyst (332), ArbitrageDetector-cluster (307), Rigby-as-agent-row (227 — already Tier-1 as PersonalAssistant). Reason: sports-vertical for A1 Platform/ML/SRE+compliance buyer. Day-1 fault-injection ratified as arc scope (5 scenario categories: happy path / tool timeout / data unavailable / ambiguous input / bad-malformed input) + reliability contract required (output fields, citations, uncertainty markers, refusal behavior). This terminal session shipped **4 PRs** total (#3545 + #3546 + #3547 + #3549) and executed **3 full close cascades**. **S2955 first-action = author `evals/tier1/system_intelligence_agent.yaml`** — highest 30d volume among Tier-1 (33 exec).

**Refreshed 2026-07-25 (S2954 close).** Gap-map headline: `100 validated_full / 2 untested` — the 2 are `agent_capability_drift_tool` (S2953-shipped) + `agent_job_status` (S2952-shipped), both untested-by-design at ship time. **S2953 handoff drift correction:** prior 00-START asserted `100/0`; actual is `100/2` (not S2954-introduced, correction folded here at S2954 close).

**PRs shipped this session (in-terminal, S2952 close + S2953 open+close + S2954 open+close):**
- u-d-b PR **#3545** — S2952 pre-A1 capability triage (3 files, +129/-8).
- u-d-b PR **#3546** — S2952 close cascade (3 files, +163/-56).
- u-d-b PR **#3547** — S2953 agent capability drift scanner (8 files, +927/-3, 9 tests).
- u-d-b PR **#3549** — S2954 Golden Evals arc-open scoping doc (1 file, +95/-0, doc-only).
- u-d-b PR **#TBD** — S2954 close cascade (handoff + this 00-START refresh + wrapper pin bump).

**Twin mirrors shipped this session (S2954 slice):**
- S2954 Golden Evals arc-open content mirror: `1f79856a-9f9a-4c84-be17-d8884b72e65f` (Donkey Betz workspace, `initiative_phase_doc`, `category='governance'`, diagnostic ORM-cleared per Ledger #16 re-hit)
- S2954 Golden Evals arc-open ratification envelope: `b38ba743-9050-476f-8f70-175cf8aafed6` (Donkey Betz workspace, `ratification_record`, `category='governance'`, diagnostic already null on create)

Full S2953 mirror IDs preserved in `docs/handoffs/SESSION_2953_DRIFT_SCANNER.md`.

**Files shipped this session (S2954 slice):**
- **NEW** `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md` — arc-open scoping doc (95 lines, 7 sections).

**Post-merge:** PR #3549 was doc-only, no worker impact → no `make celery-recycle` required (PLAYBOOK-7.4.4 applies to code-shipping PRs).

**Governance:** Golden Evals arc opened with Tier-1 list + Day-1 fault-injection scope ratified. Rigby SIGN turn 1 tool-grounded (real ORM query, tool_runs populated — not rubber-stamping). Rigby SIGN turn 2 verdict WARN on sunny-day-theatre concern → reconciled via Day-1 commitment.

**Rigby Tool Gap Ledger:**
- **RE-HIT (Ledger #16, 7th time cumulative)** — `deliverable_tool.create` diagnostic-flag bug on `initiative_phase_doc`. S2954 content mirror flagged; ORM-cleared.
- **NEW — Ledger #17 candidate** — Rigby Chat UI does NOT relay Chris's ratification responses back to Claude terminal even when explicit "route back verbatim" instruction is present in the dispatch. Observed twice this session (Chris `yes` on Tier-1; Chris `close` on next-move A/B). Chris relayed manually via terminal both times. Design task; no CLI workaround needed.

Full session context: `docs/handoffs/SESSION_2954_GOLDEN_EVALS_ARC_OPEN.md`.

---

## S2955 open sequence

**S2955 first-action = author `evals/tier1/system_intelligence_agent.yaml`** — first Tier-1 agent's canonical prompt suite. Highest 30d execution volume among Tier-1 (33 exec).

### Universal open sequence

1. **Live-verify S2953 drift scanner still healthy** (unchanged from S2954 open):
   - `bash tools/pa_local.sh "run agent_capability_drift_tool action=summary"` — expect shape (83/92/59/1 → 77+2 or drifted numbers with same shape).
   - `python manage.py scan_agent_capability_drift --json | jq .totals` — same from CLI.
2. **First-action lint pre-flight:** `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check` — confirm gap-map headline `100 validated_full / 2 untested`. The 2 untested (`agent_capability_drift_tool`, `agent_job_status`) are expected.
3. **Verify wrapper pin freshness:** `grep "^python tools/pa_chat.py" tools/pa_local.sh` — should show the S2955 pin (retired at S2954 close cascade).
4. **Open S2955 slice** — see scope below.

### S2955 arc-slice scope: SystemIntelligenceAgent YAML

**Target file:** `evals/tier1/system_intelligence_agent.yaml` (new `evals/` tree at repo root).

**YAML shape (per prompt):**
```yaml
- id: sia_happy_path_01
  category: happy_path            # or: tool_timeout / data_unavailable / ambiguous_input / bad_input
  input: "<the actual prompt to send to SystemIntelligenceAgent>"
  expected_output_shape:          # JSON Schema fragment
    type: object
    required: [summary, evidence_pointers, health_status]
    properties:
      summary: {type: string, minLength: 20}
      evidence_pointers: {type: array, minItems: 1}
      health_status: {enum: [healthy, degraded, unavailable]}
  acceptance_criteria:            # reliability-contract checks
    - required_fields_present
    - evidence_pointers_non_empty
    - no_unsupported_claims
```

**Coverage target:** 5–20 prompts total, at least 1 per scenario category. SystemIntelligenceAgent-specific happy-path candidates: "current celery worker health", "which agents have failed in last hour", "PostgreSQL connection pool status", "spider queue depth" — pull these from actual agent invocation patterns in production traffic.

**Out of scope for S2955:** validator code (JSON Schema executors, Pydantic model runners) and `run_golden_evals` mgmt cmd. Those are S2956 and S2957.

**Estimated 1 session** for this slice.

### Golden Evals arc structure (unchanged from S2954 open)

- **S2955** — SystemIntelligenceAgent YAML (this slice).
- **S2955+ 2nd** — ResearchAgent YAML.
- **S2955+ 3rd** — DevOpsAgent YAML.
- **... through 8th Tier-1 agent** — Content/Competitor/Legal/WorkflowOrch/Rigby YAMLs.
- **S2956** — Validators (JSON Schema execution + Pydantic model runners).
- **S2957** — Harness (`run_golden_evals` mgmt cmd + `GoldenEvalRun` table + nightly beat task).
- **After arc close** — A1 Phase 1 first-slice opens (Chris's 4 gating questions still block; see below).

### Capability Manifest — build spec (parallel-track from A1 Phase 1 start)

_(unchanged — see prior S2953 close snapshots; not part of Golden Evals arc)_

### A1 Phase 1 still ahead (after Golden Evals arc closes)

Chris's 4 open questions from scoping deliverable `7870eca9` still gate Phase 1 code:

1. **Minimum evidence standard** we promise? (run IDs + failure signature samples vs metrics only)
2. **Default turnaround SLA** we can consistently hit without heroics?
3. Sell as **agent-system audit** (end-to-end) or **toolchain reliability audit** (tools/contracts) first?
4. **Legal posture** for handling customer logs (retention window, deletion guarantee, allowed data types)?

### Deferred queue (updated at S2954 close)

**S2954 additions:**
- **Rigby Chat UI response-relay gap** (Ledger #17 candidate) — Chris's Chat UI responses aren't routed back to Claude terminal even when explicit instruction present. Design task.
- **00-START validated-full gap-map lint sync** — confirmed drift of 2 (S2953-untested-by-design). Consider CI check that the 00-START headline pulls from `build_pa_tool_audit` live rather than manual editing.

**S2953 additions (carry forward):**
- Drift scanner invariant 4 (rerouted-must-be-labeled) — requires `AgentRerouteEntry`-style queryable model.
- Curate `capabilities_exceptions.yaml` — 77 active findings at HEAD `9f25abdb1`. Walk each; tier-classify or fix.
- Fix run_agent dispatch-response agent-name echo (from S2952) — echo mapping-canonical CamelCase, not input string.

**S2952 carry-forward:**
- Schema/handler drift scanner (PA tool contract — separate from S2953's agent drift scanner).
- `agent_job_status` design gap harder fix (reserve `AgentExecution` row synchronously at dispatch).

**Signal-dispatch queue (from S2951, carry forward):**
- **(A11)** 6th signal-dispatch rule (`sentiment_shift` or `market_movement`) — no volume evidence yet.
- **(NEW-6)** Fair-share round-robin scanning in `scan_and_dispatch()`.
- **(NEW-7)** Persist `per_rule_diagnostics` per `scan_run_id`.
- **(NEW-8)** Per-pattern effectiveness attribution for reused agents.

**Long-standing (carry forward from S2951):**
- **(D)** Docs restructuring arc — Chris-ratified S2800, still queued.
- **(B)** Slice 5-hardening — 3-4 executable invariants deferred at S2928.
- **(E)** Tier 2 lint promotion — envelope-JSON top-level-key parse.
- **(H)** generate_newsletter dry_run default flip.
- **(I)** bulk_archive statuses autofill robustness — 2nd trigger at S2945.
- **Envelope enhancement** (record-only S2942) — `verify_hint` + `would_write_count` for dry_run.
- **Close-ceremony ledger-flip checklist** (meta-fix, record-only S2942).
- **Deliverable v1 template retrofit** (record-only S2943).

---

## What's forbidden at S2955 (D6 MORATORIUM still in force)

All prior forbidden entries carry forward. **S2954 new forbidden entries:** none.

---

## What's queued but deferred (do NOT open unless Chris directs)

**S2954 additions to the deferred queue:**
- Rigby Chat UI response-relay gap (Ledger #17 candidate).
- 00-START validated-full gap-map lint sync.

**S2953 additions (carry forward):**
- Drift scanner invariant 4 (rerouted-must-be-labeled).
- `capabilities_exceptions.yaml` curation.

**S2952 additions (carry forward):**
- Schema/handler drift scanner (PA tool contract).
- `agent_job_status` design gap harder fix.
- Dispatch-response agent-name echo cleanup.

**S2951 additions (carry forward):**
- `MarketIntelligenceCoordinator` rename — cosmetic only.
- `brainstorm_tool.create` real panel implementation.
- CompetitorAnalysisAgent spider sources (LangSmith/Langfuse/Helicone/Arize).

**Long-standing (carry forward from S2951):**
- Fair-share round-robin scanning.
- Persist per_rule_diagnostics in audit table.
- Advanced paste-UUID fallback for cluster picker.
- Server-side search + pagination on `/eligible/`.
- Z1/Z2/Z4 signal-dispatch UI polish (Rigby S2947 zoom-outs).
- Rank + cap + paginate follow-ups (Rigby S2946).
- Per-pattern-type diversity floors.
- Ledger candidates (S2945/2944/2943/2942 backlog).
- Docs restructuring arc (Chris-ratified S2800).
- W2 #1 / #2b / #2c pending Chris re-slate.
- LLMCallLog field splits.
- Bulk `workspace_budget_tool` operations.
- C4/C5/C6 character-os follow-ons.

---

## Sweep progress tracker (Path B ratified S2892)

**All ratified sweep scope discharged as of S2940.** Signal-dispatch (S2946-S2950) + A1 infra (S2951) + pre-A1 capability triage (S2952) + capability substrate (S2953 Drift Scanner) + Golden Evals arc-open (S2954) are adjacent-domain net-new engineering + arc substrate, not sweep work.

**Total remaining sweep tools: 0.**

---

## Autopilot Slice 1.5b pre-commit note

_(unchanged — see prior S2907 close snapshots in handoff)_

---

## Two-Claude concurrency safety envelope (still active from S2889)

_(unchanged — see prior 00-START snapshots)_

---

## A4 Warm-up Operating Constraints (Rigby-authored, S2846-ratified, still in force)

1. **Spend lane:** A4 warm-up uses separate budget lane/cap; must NOT consume A1 shipping spend.
2. **Evidence tag:** All A4 artifacts labeled "discovery-quality, not truth."
3. **Capability claims:** (a)…(uu) as ratified at S2887 close. No additions.
4. **Pilot framing only:** A4 messaging is pilot/early-access/concierge only.
5. **Hard throttle:** A4 warm-up constrained to fixed timebox + fixed send count (3-5 total intros).
6. **No bespoke follow-ups.**

---

## For fuller context (S2846 → S2954)

See:
- **S2954 handoff (current):** `docs/handoffs/SESSION_2954_GOLDEN_EVALS_ARC_OPEN.md`
- **S2954 shipped code:** `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md` (arc-open scoping doc, 95 lines)
- **S2953 handoff:** `docs/handoffs/SESSION_2953_DRIFT_SCANNER.md`
- **S2953 shipped code:**
  - `core/services/agent_capability_drift.py` — scanner service
  - `capabilities_exceptions.yaml` — allowlist
  - `core/management/commands/scan_agent_capability_drift.py` — CLI
  - `core/services/pa_tool_schemas.py` — `agent_capability_drift_tool` schema
  - `core/services/td_handlers_agents.py:6713-6764` — `_handle_agent_capability_drift`
  - `core/services/tool_dispatcher.py:406-408` — handler registration
  - `core/tests/test_agent_capability_drift.py` — 9 tests
- **S2952 handoff:** `docs/handoffs/SESSION_2952_PRE_A1_CAPABILITY_FIXES.md`
- **A1 Wedge scoping deliverable (unchanged, S2951):** `7870eca9-2bcc-4cb4-a7e1-6c2de7697ec6`
- **A1 Wedge ratification envelope (unchanged, S2951):** `3ad93ef9-48ef-4a3f-ac55-7678a9f5f28b`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50`)
- **Parent-workspace multi-Claude rulebook:** `/Users/donkeyking/Donkey_Betz/docs/MULTI_CLAUDE_COORDINATION.md`

For older session history (S1–S2849), see `docs/handoffs/` + `docs/research/OPEN_ARCS.md`.
