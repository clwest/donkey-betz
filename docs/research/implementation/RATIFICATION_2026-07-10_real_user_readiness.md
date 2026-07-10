---
title: "Real User Readiness Campaign Ratification Record — parent campaign (2026-07-10)"
status: active
authority: ratification-record
session_added: 2742
ratification_date: 2026-07-10
ratifier: chris
routing: rigby-pa-chat + Chris direct in-session (S2742 D-verdict package)
program_id: RUR
parent_workspace: "Real User Readiness Campaign"
parent_workspace_id: 638e9e90-47b4-4bd4-a872-bf16181cf3b5
ratified_document: docs/research/implementation/real_user_readiness/CAMPAIGN.md
ratified_document_head_at_ratification: (see §1 Context — HEAD updated inside the ratification PR)
sign_sessions:
  - S2741 — SIGN-with-amendments (7 amendments applied)
  - S2742 — SIGN-PASS (9/10 items PASS, item 10 WEAK guard added, 1 material clarification applied)
supersedes: none (first Real User Readiness ratification)
superseded_by: (open; later revision ratifications will point here)
frozen: true
---

# Real User Readiness Campaign Ratification Record

This file is the **frozen** canonical record of Chris's ratification of the Real User Readiness parent engineering campaign on 2026-07-10. It captures the ratified document, the D-verdict package on nine open questions, the Rigby SIGN cycle across two sessions, and the explicit Wave 1 authorization boundary. It is append-only history; do NOT edit after commit.

Future revisions to the CAMPAIGN.md document that change §2 (Definition of Ready), §3 (Definition of Done), §4 (Campaign Map), or §5 (Dependency Graph) require a new ratification record dated on the amendment date, which references this record as its `supersedes` predecessor.

---

## §1. Context

- **Ratification date:** 2026-07-10 (America/Denver operator timezone)
- **Program:** Real User Readiness (RUR) — the engineering program to bring the Donkey Betz platform to a bar where an allowlisted alpha cohort can trust it.
- **Ratified document:** [`docs/research/implementation/real_user_readiness/CAMPAIGN.md`](real_user_readiness/CAMPAIGN.md)
- **Parent workspace:** `Real User Readiness Campaign` (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`, workspace_type `sandbox`, created S2741 via Rigby `workspace_tool`)
- **Research predecessor:** S2740 assessment (produced in-transcript during S2746; not persisted as a separate repo file; reconstruction path recorded in `CAMPAIGN.md §1 + §11`)
- **Prior state:** parent doc was `status: draft` / `authority: draft-planning` at merge of PR #3074 (commit `53cdaa20`). Ratification upgrades to `status: active` / `authority: constitutional`.

## §2. Ratified Document Frontmatter Upgrade

The parent CAMPAIGN.md frontmatter was upgraded as part of this ratification:

| Field | Pre-ratification (S2741 draft) | Post-ratification (S2742) |
|---|---|---|
| `status` | `draft` | `active` |
| `authority` | `draft-planning` | `constitutional` |
| `session_added` | `2741` | `2741` (unchanged) |
| `session_ratified` | (absent) | `2742` |
| `ratification_date` | (absent) | `2026-07-10` |
| `ratifier` | (absent) | `chris` |
| `ratification_record` | (absent) | `docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md` |
| `constraint` | `planning-only until Chris ratifies Wave 1 mission opens` | (removed; no longer accurate) |
| `sign_history` | 1 entry (S2741) | 2 entries (S2741 + S2742) |

## §3. Chris D-Verdict Package on §12 Open Questions

The nine open questions from the S2741 draft's §12 were resolved by Chris at S2742. Each verdict below is quoted or summarized from the S2742 in-session directive package.

### Q1 — Wave 1 prereq (RUR-C1 vs RUR-C2 parallelism)

**D-verdict:** **Staged overlap.**

RUR-C1 opens first. RUR-C2 does not need to wait for all RUR-C1 remediation to close, but it may not open until RUR-C1 has established and SIGN-confirmed the failure-data safety contract that governs user-visible failure artifacts.

The safety contract must prohibit user-facing error surfaces from exposing: foreign-workspace data, raw model payloads, user prompts/conversation contents (unless explicitly safe), filesystem paths, secrets/credentials, internal stack traces, raw exception values containing tenant data, unrestricted serialized objects, and internal provider request bodies.

User-facing failures may expose only: `support_code`, safe `reason_code`, safe `human_message`, `retryability`, terminal state, and timestamps where appropriate.

Detailed diagnostic context remains operator-only with tenant-aware access controls.

**Applied in:** CAMPAIGN.md §5 Wave structure diagram + §9.1 Boundary Before RUR-C2 Opens + §9.2 Failure-Data Safety Contract + §11 Div 1 resolution.

### Q2 — RUR-C1 structure (one arc or three)

**D-verdict:** **One parent campaign with three bounded child implementation arcs.**

- **I-0301** — HTTP + AllowAny Surface Remediation (also establishes the failure-data safety contract)
- **I-0302** — Object-Level Authorization (Deliverable, Initiative, ChatConversation, AgentExecution, Document)
- **I-0303** — Async Tenant-Boundary Enforcement

RUR-C1 remains the parent invariant. It closes only when ALL three child arcs pass the shared cross-tenant regression requirements. Closure of I-0301 alone is NOT closure of RUR-C1.

**Applied in:** CAMPAIGN.md §4 Campaign Map (RUR-C1 row + three child rows) + §11 Div 2 resolution.

### Q3 — Which campaign opens first

**D-verdict:** **RUR-C1 opens first, beginning with I-0301.**

Initial order: RUR-C1 parent opens → I-0301 opens → failure-data safety contract established and SIGN-confirmed → RUR-C2 may open. After the safety contract is signed, RUR-C2 / I-0400 may proceed; I-0302 and I-0303 may proceed; parallelism only if workspace / branch / ownership / SIGN / mission isolation rules make it safe. **Do not create parallelism merely to move faster.**

**Applied in:** CAMPAIGN.md §5 Dependency reasoning + §7 Wave 1 authorization (this record's §5).

### Q4 — Golden path candidate

**D-verdict:** **Candidate C — Rigby chat.**

Rejects Candidate A (content generation — content quality would become the readiness signal) and Candidate B (deliverable produce+approve — narrower substrate coverage). Rigby chat exercises the platform's primary assistant experience and crosses authentication, workspace context, async dispatch, Celery, WebSockets, failure signaling, traceability, persistence, and deliverable ownership.

11-step journey specified in CAMPAIGN.md §8. RUR-C7 must select one bounded task appropriate for repeatable E2E testing at Wave 4 open; the task must not be arbitrary at test time.

**Applied in:** CAMPAIGN.md §4 RUR-C7 row + §8 Expected user journey.

### Q5 — Cost enforcement cadence

**D-verdict:** **Keep full RUR-C6 in Wave 3. Add an interim alpha dispatch ceiling.**

RUR-C6 remains dependent on RUR-C2 (cap breaches require a safe user-visible failure surface). However, no user-facing alpha flow may have unbounded spend while permanent per-workspace enforcement is pending.

Early-wave mitigation uses existing configurable controls only: conservative global/allowlist dispatch limits; conservative per-run ceilings; restricted model/tool access for alpha; explicit confirmation for unusually expensive flows; disablement of known runaway paths. **Do not build the final RUR-C6 solution inside another campaign.**

**Applied in:** CAMPAIGN.md §4 RUR-C6 row + §8 Interim Alpha Cost Ceiling.

### Q6 — "Succeeded but wrong"

**D-verdict:** **Accepted as a managed semantic-quality risk for gated alpha, with a precise boundary.**

**Execution-correctness failures (OWNED by RUR-C2 postcondition verification):**
- Empty output
- Missing expected deliverable
- Malformed structured output
- Required schema absent or invalid
- Required postcondition not created
- Placeholder content
- Explicit provider/tool error normalized into success
- Output that fails a deterministic minimum structural contract

**Semantic-quality concerns (POST-ALPHA):**
- Weak writing
- Mediocre recommendations
- Low usefulness despite valid structure
- Subjective disagreement with the result
- Subtle factual or reasoning quality not detectable through deterministic checks

Alpha mitigation for the post-alpha class: operator review of early outputs; user feedback capture; clear separation of execution failure from quality dissatisfaction; evidence collection for a future output-quality campaign.

**Applied in:** CAMPAIGN.md §4 RUR-C2 scope + §11 Div 4 (updated with boundary).

### Q7 — Alpha cohort provisioning

**D-verdict:** **Up to 10 named active testers, launched in two stages.**

**Stage 1:** Chris + 2–3 trusted testers. Individual accounts + individual workspaces (unless a specific shared-workspace test is intentionally being performed). No shared credentials. Stage 1 must complete the golden path without a hard-blocker invariant violation before Stage 2 expansion.

**Stage 2:** Expand to no more than 10 active testers total. Architecture may support ~25 allowlist entries, but 25 active users are not the initial acceptance requirement.

Every alpha user must be individually revocable without a deployment. Cohort must include variation: new session, returning session, simultaneous use, retryable failure, denied access, expired/invalid authentication, user leaving and returning to a completed task.

**Applied in:** CAMPAIGN.md §8 Cohort provisioning.

### Q8 — Alpha operating mode

**D-verdict:** **Yes, use an explicit throttled alpha operating profile.**

Ten-point contract:
1. User-triggered work receives priority over scheduled autonomous work.
2. Nonessential autonomous schedules run at reduced cadence.
3. Nonessential spider ingestion is reduced or paused during planned cohort exercises.
4. Dispatch concurrency is conservatively capped.
5. Provider retries use bounded backoff and jitter where the existing substrate supports it.
6. Queue saturation must produce a safe, visible busy response rather than indefinite invisible waiting.
7. Busy response must include `support_code` and actionable retry guidance.
8. Throttles must be configuration-driven and reversible.
9. Configuration and rationale must be documented.
10. Alpha mode must not silently become the permanent production profile.

If the existing worker topology cannot guarantee user-job priority, document the limitation and apply the safest operational mitigation available before cohort access.

**Applied in:** CAMPAIGN.md §8 Alpha Operating Mode.

### Q9 — Numeric clean-observation threshold for cost

**D-verdict:** **A seven-day observation period is "clean" only if all seven conditions are true.**

1. Zero configured monthly-threshold breaches.
2. Projected monthly spend ≤ 80% of the $500 monitor threshold (max acceptable: $400/month).
3. Zero unexplained cost events lacking attribution to (user | workspace | mission/execution | explicitly-classified system activity).
4. Zero individual execution breaches of its applicable configured run/task ceiling.
5. Zero retry-amplification incidents exceeding 2× the expected provider-call count for one logical request.
6. Cost telemetry completeness is sufficient to support the calculation.
7. No known monitoring gap makes the result materially unreliable.

If attribution or telemetry completeness is insufficient, verdict is **Inconclusive — not clean**. Missing data is NOT zero spend or zero breaches. This threshold decides whether the observation gate is clean; it does NOT move permanent RUR-C6 out of Wave 3.

**Applied in:** CAMPAIGN.md §8 Cost-observation numeric gate.

---

## §4. Rigby SIGN Cycle Summary

### S2741 SIGN cycle (draft creation)

- **Verdict:** SIGN-with-amendments
- **Amendments applied (7):**
  1. Authority downgrade `constitutional` → `draft-planning` in frontmatter
  2. G7/G8 alpha-open vs campaign-close two-layer gate contract
  3. RUR-C2 rename `Async Fail-Loud` → `Async State + Fail-Loud + Traceability` with explicit scope-exclusion clause
  4. §5 dependency graph label `parallel-safe` → `parallel-possible pending Chris D-verdict`
  5. §11 Divergence 6 added (G7/G8 enabler-vs-blocker contradiction)
  6. §12 Q8 + Q9 added (alpha operating mode + cost-observation numeric threshold)
  7. §8 Alpha Operating Mode mitigation subsection added
- **Bonus:** E1–E11 rewritten with named probes (test file paths, snapshot lists, chaos hooks, numeric thresholds)

### S2742 re-SIGN cycle (post-D-verdicts)

- **Verdict:** SIGN-PASS
- **Item scores:** 9 of 10 PASS + 1 WEAK
  - PASS items: 1 (D-verdicts faithful), 2 (no false unresolved), 3 (staged-overlap coherent), 4 (RUR-C2 open guard), 5 (RUR-C1 parent close condition), 6 (Succeeded-but-wrong precise), 7 (gate contract noncontradictory), 8 (cost obs vs enforcement not conflated), 9 (Rigby chat exercises invariants)
  - WEAK item: 10 (no silent Wave 1 authorization) — applied by adding an "Authorization guard" clause to §6 clarifying that §6 templates do NOT authorize implementation
- **Material amendment applied:** §10 authority-line correctness — pre-fix said "Authority: constitutional (per frontmatter)" while frontmatter was `draft-planning`. Post-fix reflects current state.
- **Editorial fixes:** §4 → §8 reference correction for golden-path pointer.
- **NO D-verdict changed.** No campaign scope, dependency, hard gate, or Wave 1 authorization affected by any re-SIGN amendment. Ratification proceeds under the S2742 §4 escalation rule.

---

## §5. Wave 1 Authorization Boundary

**This ratification authorizes Wave 1 to open, beginning with RUR-C1 parent + I-0301 scoping only.**

Wave 1 opening is permission to:
1. Create or select the correct RUR-C1 workspace/sub-workspace using existing naming conventions.
2. Create the I-0301 scoping deliverable/document.
3. Link it to parent workspace + parent CAMPAIGN.md + RUR-C1 + I-0301 slot.
4. Perform required repository orientation + evidence pass.
5. Confirm actual endpoint denominator at current HEAD (rather than trusting the S2740 count of 26).
6. Produce an endpoint audit ledger.
7. Classify each endpoint (intentionally public / temporarily public and requiring remediation / obsolete or dead / ambiguous and requiring evidence).
8. Define the failure-data safety contract.
9. Define regression test denominator and verification approach.
10. Obtain Rigby scope SIGN before implementation begins.

**Wave 1 authorization is NOT:**
- Permission to skip the mission-open process
- Permission to begin broad auth fixes without scope SIGN
- Permission to open RUR-C2 before its safety-contract precondition
- Permission to open I-0302 or I-0303 before the safety-contract SIGN
- Permission to open Waves 2, 3, or 4
- Permission to modify any other RUR-C sub-campaign scope
- Permission to change any element of this ratified document

---

## §6. Explicit Non-Goals Recorded at Ratification

Per Chris S2742 §10 non-goals:

- Do NOT begin the `/docs/` information architecture audit.
- Do NOT rename `/docs/research/`.
- Do NOT patch every cascade tool by default (the S2741 cascade-tooling defect is recorded but not resolved by this campaign).
- Do NOT open RUR-C2 before its safety precondition.
- Do NOT open all seven RUR campaigns at once.
- Do NOT create new platform governance rules unrelated to readiness.
- Do NOT turn semantic output quality into a full campaign.
- Do NOT pull permanent cost enforcement into Wave 1.
- Do NOT treat alpha readiness as self-service readiness.
- Do NOT treat campaign ratification as implementation completion.

---

## §7. Cross-References

- Parent CAMPAIGN document: [`real_user_readiness/CAMPAIGN.md`](real_user_readiness/CAMPAIGN.md)
- Parent workspace: `638e9e90-47b4-4bd4-a872-bf16181cf3b5` (`Real User Readiness Campaign`)
- Research predecessor: S2740 assessment (in-transcript during S2746)
- Prior related implementation arcs: I-0100 (Observability Correlation Spine) closed 2026-07-07; I-0200 (RAG Corpus Substrate Maturity) closed 2026-07-07
- Next arc to open under this campaign: I-0301 (HTTP + AllowAny Surface Remediation + Failure-Data Safety Contract)

---

**End of Real User Readiness Campaign Ratification Record. This file is frozen; do NOT edit after commit.**
