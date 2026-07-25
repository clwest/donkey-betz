# S2963 — Golden Evals arc close (canon_v2 ratification: 5 fold candidates + EvalRunContext guardrail)

**Session:** 2963
**Ratified:** 2026-07-25 (Chris `yes` via terminal after joint Claude+Rigby recommendation)
**Arc parent:** Golden Evals (opened S2954, Tier-1 spec-authoring phase closed S2962)
**HEAD at open:** `dc1ed658b`
**HEAD at merge:** filled at close cascade merge

---

## 1. What this doc ratifies

The Golden Evals Tier-1 spec-authoring phase shipped 8 canonical YAMLs across S2955–S2962. Along the way, Rigby SIGN cycles surfaced 5 zoom-out folds (P1/P2/S1/U1/V1) whose disposition was deferred to arc-close. S2963 arc-close ratifies those 5 folds as canon_v2 refinements, plus 1 additional guardrail (EvalRunContext evidence abstraction) surfaced by Rigby's S2963 T1 zoom-out fold. The 6 items collectively bind the shape of the S2964 validator harness before any harness code is written.

**Companion doc:** `docs/research/platform/S2954_GOLDEN_EVALS_ARC_OPEN.md` (Tier-1 list ratification + Day-1 fault-injection scope).

## 2. Tier-1 spec-authoring phase — what shipped

8 canonical `evals/tier1/*.yaml` files at canon_version=1, across 2 persistence substrates:

| Slice | Session | Agent | Substrate | 30d | All-time | Domain preds | Routing branches | Merged SHA |
|-------|---------|-------|-----------|----:|---------:|-------------:|-----------------:|------------|
| 1 | S2955 | SystemIntelligenceAgent | AgentExecution | 37 | 105 | 2-3 | 1 | `d2acf9c92` |
| 2 | S2956 | ResearchAgent | AgentExecution | 37 | 90 | 2-3 | 1 | `c8815cd38` |
| 3 | S2957 | DevOpsAgent | AgentExecution | 13 | 40+ | 2-3 | 2 | `98ba0e06b` |
| 4 | S2958 | WorkflowOrchestrationAgent | AgentExecution | 9 | 30+ | 2-3 | 2 | `e2b7e92c2` |
| 5 | S2959 | LegalDocDrafterAgent | AgentExecution | 5 | 10+ | 7 | 2 | `8fa60421f` |
| 6 | S2960 | ContentWriterAgent | AgentExecution | 7 | 23 | 5 | 5 | `10b6b3ab1` |
| 7 | S2961 | CompetitorAnalysisAgent | AgentExecution | 2 | 11 | 5 | 5 | `75f8da29a` |
| 8 | S2962 | Rigby (UnifiedPAEntrypoint) | **ChatConversation** | **508** | **1,018** | 6 | 1 | `6bf8d9a81` |

Slice 8 was the first Tier-1 file authored against a non-AgentExecution substrate — proves canon_version=1 abstracts cleanly over persistence substrate (the property this arc-close codifies at canon_v2).

**Canon_v1 informative additions accumulated across slices** (still in force at canon_v2, unchanged):

1. `schema_version: 1` + `canon_version` at file top.
2. `canonical_field_mapping` block declaring `mapping_source: native|derived` per canon field with named derivation rules.
3. `fault_injection` uses effect-based contract (`component` + `fault.{type, params}`) with `python.{...}` as backend-adapter appendix; prefer service-level selectors over library-internal Python paths.
4. `one_of` acceptance-criteria capped at ≤2 branches with mandatory `why` string per branch.
5. Canon substrate is portable across persistence substrates (proven S2962). Two shipped: AgentExecution (7 slices) + ChatConversation (1 slice).
6. Per-execution-shape evidence-tier requirements (S2958).
7. INTEGRATION EVIDENCE tier distinction — out-of-band DB inspection is not Tier-1 validator scope (S2958).
8. TRANSITIONAL marking pattern for slices documenting a fold requiring code follow-up (S2958).
9. Timeout-string brittleness avoidance — assert stable discriminator fields + broad substring patterns (S2958).
10. Domain-sensitivity acceptance predicates encoded alongside `no_unsupported_claims` (S2959).
11. Routing-branch framing — variant execution paths are routing branches inside the same agent contract, NOT new shapes (S2959).
12. Coverage-limits actionable conclusion — the coverage-caveat pile resolves to one actionable line per slice (S2959).
13. Substrate portability (informative form of canon_v2 #17 below) (S2962).
14. Source-stratification for multi-source substrates (informative form of canon_v2 #18 below) (S2962).
15. Receipt-contamination filter for AgentExecution queries (informative form of canon_v2 #20 below) (S2962).

## 3. Canon_v2 ratifications (this session)

All 6 items ratified 2026-07-25 by Chris via terminal after joint Claude+Rigby recommendation. Rigby T1 SIGN was tool-grounded (10 tool_runs — read every referenced YAML + handoff + source file) and returned 2 AGREE + 3 REVISE verdicts, plus 1 additional guardrail via zoom-out fold. Every REVISE narrowed the initial candidate to reduce scope creep or fix a factual error. All 6 REVISED forms below carry Chris's terminal ratification.

### Item 1 — orm_inspect_tool allowlist extension (Fold P2 / Candidate 1)

**Ratified form:** Add `ChatConversation` + `ToolCallRecord` to `_MODEL_POLICIES` in `core/services/td_handlers_agents.py` (currently 14 models at lines 733-831 of HEAD `dc1ed658b`). Net: **14 → 16 models**.

**Correction from initial candidate:** the initial 00-START framing said "14 → 17" including `LLMCallLog`. Rigby T1 caught + Claude verified via Grep + block-parse at `td_handlers_agents.py:733-831`: `LLMCallLog` is already present at lines 749-752. Correct delta is 14 → 16.

**Ship shape:** code change (~30 lines) at S2964 harness open. Same-PR as first harness commit so Rigby can dogfood the harness against slice 8 substrate immediately.

**Why:** without ChatConversation + ToolCallRecord in the allowlist, Rigby cannot tool-verify her own eval substrate. Every harness dogfood run would require dropping to Django shell — accretes tool-gap ledger #19 with each blocked run.

### Item 2 — Source-stratification as canon dimension (Fold S1 / Candidate 2)

**Ratified form:** For multi-source substrates (any substrate with a `source` discriminator like `ChatConversation.source IN ('web', 'pa', 'claude-code', …)`), Tier-1 slices MUST declare and filter to the buyer-facing surface. Principle: **same user_id ≠ same eval class**. A single user's `claude-code` turns are developer-tolerant; the same user's `web` / `pa` turns are buyer-facing — validators must not conflate the two trust surfaces.

**Ship shape:** doc-only; add to `canonical_field_mapping` block conventions. Enforced by convention at slice authoring; harness may lint the filter is declared for multi-source substrates.

**Why:** without stratification, validator pass-rate metrics get polluted (developer-tolerant traffic masks buyer-facing failures or vice versa).

### Item 3 — Opt-in `latency_ms` evidence class (Fold U1 / Candidate 3, revised framing)

**Ratified form:** Do NOT universally promote `response_time_ms` to a first-class evidence field. Instead: add an opt-in `latency_ms` evidence class with "may be present" semantics. Validators that are explicitly latency-sensitive (e.g., tool_timeout categories, PA-turn UX) opt in; correctness/grounding validators do not consume the field.

**Revision rationale (Rigby T1):** universal promotion would force per-slice YAML updates across all 8 shipped slices AND create false coupling — different substrates expose different latency semantics (`ChatConversation.response_time_ms` vs `AgentExecution.finished_at - started_at`). Opt-in resolves both.

**Ship shape:** doc-only canon_v2 spec; per-slice YAMLs adopt only where latency is a validator dimension. No retroactive updates to shipped slices.

### Item 4 — Receipt-contamination filter as canon-wide predicate (Fold P1 / Candidate 4)

**Ratified form:** Any Tier-1 query on `AgentExecution` (for real-usage sampling, evidence-pointer joins, or ground-truth selection) MUST exclude synthetic deliverable-factory receipts. A synthetic receipt is fingerprinted by the CONJUNCTION of two field values, so the exclusion predicate is:

```
NOT (parent_object_type = 'deliverable_factory'
     AND input_data.source = 'deliverable_factory.synthesized_pa_receipt')
```

Equivalent forms by De Morgan (all logically identical, use whichever reads clearest at the call site):

- `parent_object_type != 'deliverable_factory' OR input_data.source != 'deliverable_factory.synthesized_pa_receipt'`
- Django ORM: `.exclude(parent_object_type='deliverable_factory', input_data__source='deliverable_factory.synthesized_pa_receipt')`

The `NOT (A AND B)` form is the canonical intent statement — it directly encodes "exclude the synthetic-receipt fingerprint." The OR form and Django `.exclude(**kwargs)` form are permitted as they are logically identical; do NOT rewrite them to `A != x AND B != y` (that is a different, wrong predicate that excludes rows sharing either attribute individually).

**Ship shape:** doc-only canon dimension; harness implements as a shared query utility in S2964. Applies at both slice-authoring time (when sampling rows for verbatim replays) and validator run time (when joining evidence).

**Why:** without the filter, "real Rigby usage" queries on AgentExecution surface homogeneous synthetic receipts (`tokens_used=0`, `cost=0`, `output_data.kind='deliverable_receipt'`) that masquerade as real turns — silent dataset corruption at the first step.

### Item 5 — Fault-injection selector naming convention (Fold V1 / Candidate 5, revised framing)

**Ratified form:** Canonical `fault_injection.selector` values MUST be one of:
- **`module.Class.method`** — for service methods (e.g., `core.services.system_state_aggregator.SystemStateAggregator.get_attention_items`, precedent at `evals/tier1/system_intelligence_agent.yaml:211`).
- **`module.function`** — for module-level handlers.

Handler-registry keys (e.g., `_handle_workspace_lookup`) are **FORBIDDEN** as canonical selectors unless the S2964 harness ships an explicit adapter layer that maps registry keys to concrete injection points. Absent that adapter, use the underlying `module.Class.method` or `module.function` path.

**Ship shape:** doc-only canon convention; S2964 harness parser implements a single deterministic resolver for the two allowed shapes.

**Why:** without a single convention, the harness parser accumulates 3 naming schemes and validators spend cycles chasing "injection didn't apply" false negatives. Rigby T1 caught 1 nonexistent selector during S2962 T1 SIGN specifically because slice 8 tried a handler-registry key convention — the exact failure mode this item prevents.

**Same-session decision:** required before S2964 harness code opens.

### Item 6 — `EvalRunContext` evidence abstraction (Rigby zoom-out fold, new guardrail)

**Ratified form:** Before S2964 harness code, define a single normalized shape:

```python
@dataclass
class EvalRunContext:
    substrate_type: str          # 'agent_execution' | 'chat_conversation' | future substrates
    primary_row_id: str          # PK on the substrate table
    evidence_ledger_refs: list   # ToolCallRecord IDs, LLMCallLog IDs, related deliverable_factory rows
    finalized_at: datetime | None  # None → row is still in a mutable phase (e.g., ChatConversation pre-response)
    latency_ms: int | None       # opt-in per Item 3
```

All harness-side validators consume `EvalRunContext` instead of raw substrate row shapes. Per-substrate adapters normalize substrate-native rows into this shape.

**Rigby zoom-out framing:** without this guardrail, the harness must understand ChatConversation vs AgentExecution vs any-future substrate shape directly — accreting per-slice bespoke join logic + finalization-flake risk + line-number-anchor brittleness. Codifying `EvalRunContext` as canon_v2 solves all three in one shape.

**Ship shape:** doc-only canon spec this session; concrete Python dataclass lands at S2964 harness open in `core/services/golden_evals/` (path tentative). Validators built against `EvalRunContext` from day 1.

**Why:** the alternative is 8+ substrate-specific `if/else` branches per validator, growing with each new slice. One abstraction saves ~5-10 sessions of tech debt starting at S2964.

## 4. Arc structure (post-close)

- **S2964 (next)** — Validator harness core: `run_golden_evals` mgmt cmd + `GoldenEvalRun` table + per-substrate adapter (AgentExecution + ChatConversation) + JSON Schema executors + Pydantic acceptance-criteria runners. Dogfood against slice 8 (Rigby, ChatConversation) FIRST to force Item 1 allowlist fix + validate two-substrate adapter cleanly.
- **S2965+** — Nightly beat task + pass-rate drift dashboard.
- **Follow-up** — WorkflowOrchestrationAgent wrapper key-name mismatch code-fix PR (F1 from S2958), then v1.1 revision of `workflow_orchestration_agent.yaml`.
- **Post-arc parallel track** — Rigby-as-Claude-Code eval slice (per Item 2 — `source='claude-code'` deserves its own eval class); PA-turn AgentExecution eval slice (requires `PA_AGENT_EXECUTION_WRITE_ENABLED` flip + 2-4 weeks traffic).
- **After harness + drift dashboard land** — A1 Reliability Audit Phase 1 first-slice opens (Chris's 4 gating questions from scoping deliverable `7870eca9` still block Phase 1 code).

Estimated 2-4 sessions to close S2964 harness core.

## 5. Rigby SIGN cycle

**T1** — Rigby ran tool-grounded per-candidate SIGN (10 `tool_runs`: read every referenced YAML, handoff, and `td_handlers_agents.py` allowlist block). Verdicts:
- Candidate 1 → **REVISE** (LLMCallLog already present; correct delta 14→16 not 14→17). Claude verified via block-parse.
- Candidate 2 → **AGREE**.
- Candidate 3 → **REVISE** (opt-in `latency_ms` class, not universal `response_time_ms` promotion).
- Candidate 4 → **AGREE**.
- Candidate 5 → **REVISE** (formal ratification of `module.Class.method` + `module.function`; explicit forbid on handler-registry keys).

**Zoom-out fold (per S2771 rule)** — Rigby surfaced 4 accreting risks beyond the 5-candidate list: evidence-pointer join fragility, two-phase persistence lifecycle coupling, line-number anchor brittleness, canon-drift toward operational heuristics. Recommended `EvalRunContext` guardrail as one-shape mitigation. This became ratified Item 6.

**T1 factual claims independently verified by Claude:**
- `LLMCallLog` in `_MODEL_POLICIES` — confirmed (line 749-752 area; 14-model count).
- `module.Class.method` precedent at `system_intelligence_agent.yaml:211` — confirmed verbatim.

**T2** — Rigby verified this doc reflects all 6 T1 verdicts. 5 PASS + 1 FAIL: she flagged Item 4's OR-form predicate as "wrong boolean," proposing `NOT (A AND B)` as the fix. Claude verified via De Morgan proof + 3-row truth table that the OR form was logically identical to `NOT (A AND B)`, so no correctness bug. However, the misread itself was a signal that the OR form is easy to misparse — doc updated to lead with the `NOT (A AND B)` form as canonical intent statement, with the OR + Django `.exclude(**kwargs)` forms listed as equivalent alternatives. Update is doc-clarity, not correctness.

**T2b** — Rigby re-verified Item 4 after the clarity update. **Verdict: PASS.** All 6 items now cleared.

**Zoom-out learning (T2 substrate signal):** Rigby's initial T2 FAIL was well-intentioned and tool-grounded (she read both the doc + the source predicate), but she made a De Morgan slip — she noticed `A != … AND B != …` would be a different (wrong) predicate but didn't complete the transform to see that `A != … OR B != …` is exactly `NOT (A AND B)`. The doc rewrite to lead with `NOT (A AND B)` preempts the same misread by future readers (human or Rigby). Signal: complex boolean predicates in canon docs should ALWAYS lead with the intent form, even when logically equivalent alternatives are shorter. One trigger; not codifying as a separate canon item yet — watch for a second occurrence.

**Chris D-verdict:** `yes` via terminal 2026-07-25 (bundle: all 6 items). Would be 7th consecutive terminal ratification S2957→S2963.

## 6. Deferred / open

- **S2964 harness scope** — code implementation of Items 1 + 5 + 6 (allowlist code, selector parser, `EvalRunContext` dataclass + adapters) opens with harness kickoff. Items 2 + 3 + 4 are doc-only from this session forward.
- **Line-number anchoring brittleness** (Rigby zoom-out concern #3) — `EvalRunContext` helps validators avoid it; slice YAML author-side discipline still applies. Not codified as a separate canon item; monitor at S2964+ for a second trigger.
- **Two-phase persistence lifecycle** (Rigby zoom-out concern #2) — `EvalRunContext.finalized_at` is the harness-side hook; per-substrate adapter defines "finalized" semantics per substrate.
- **Rigby-as-Claude-Code eval track** and **PA-turn AgentExecution eval track** — post-S2964, per Item 2 canon.
- **Chris's 4 A1 Phase 1 gating questions** (unchanged, from `7870eca9`) — remain blockers for A1 Phase 1 code, unblocked here.

## 7. Rigby Tool Gap Ledger updates

- **Ledger #19** (proposed at S2962 arc-close, ratified as Item 1 this session) — status flip **CANDIDATE → RATIFIED**. Code fix opens with S2964 harness first commit.
- **Ledger #16** — no change this session (session was doc-only, no deliverable-create ratification path exercised).
- **Ledger #17** — no change (Chris used terminal ratification, consistent with the 6-session pattern S2957→S2962; this session extends the pattern to 7 consecutive).

## 8. Limitations

- The 6-item ratification is doc-only; the guardrails only bind future code (S2964+). Nothing in this session was executable code. Verification that the harness actually consumes canon_v2 correctly happens at S2964 dogfood.
- `EvalRunContext` (Item 6) is a shape ratification, not an interface contract. Concrete Python API (method names, error handling, invalidation semantics) lands at S2964 with implementation.
- 30d/all-time counts in the Section 2 table are snapshot values from prior sessions' handoffs; they will drift. Authoritative counts live in the individual slice YAMLs and were tool-verified at each slice's authoring session.
- Rigby T2 verification of this authored doc is scheduled post-Chris-D-verdict this session; if T2 catches a translation error between T1 verdicts and this doc's ratified forms, this doc will be amended in the same PR.
