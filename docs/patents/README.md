---
title: "Patents — README + cross-link map"
status: active
last_updated: 2026-05-26
session: 1160
audience: Chris (IP owner) + future-Claude + attorney review handoff
provenance_confidence: HIGH
provenance_note: Written Session 1160 (2026-05-26) as the README for `docs/patents/`. Distilled from the Session 1158 recon doc (`docs/recons/REPORTS_PATENTS_RECON_2026_05_25.md`) which surveyed the 16 files and recommended preservation + cross-linking to narratives. All 16 underlying disclosures + executive summaries are dated March 16, 2026 ("pre-session-tracking" — predates the session-attribution rigor). Inventor: Chris West (DonkeyKing). Status across all 16 files: Draft — Attorney Review Pending.
companion_docs:
  - docs/recons/REPORTS_PATENTS_RECON_2026_05_25.md
  - docs/narratives/AGENTS_AND_AUTONOMY.md
  - docs/narratives/CONTENT_PIPELINE.md
  - docs/narratives/SIGNAL_INTELLIGENCE.md
  - docs/narratives/DECISION_COMMAND.md
  - docs/narratives/BODY_SYSTEMS.md
  - docs/narratives/WORKERS_AND_INFRASTRUCTURE.md
---

# Patents — README

> **What this directory is.** Twelve invention disclosures
> (A through L) plus four workstream executive summaries.
> All drafted March 16, 2026 by Chris West (DonkeyKing). All
> currently **Draft — Attorney Review Pending**. The disclosures
> cover platform-internal mechanisms across four workstreams
> spanning agent governance, content deliberation, signal
> intelligence, and budget enforcement. Together they describe
> the IP shape of subsystems documented in the Session 1158
> narrative slate.
>
> **Authoritative source for IP claims.** The disclosure files
> themselves. This README is a navigational aid; it does **not**
> add or amend any claim. Narratives reference patents (for
> "the IP shape of this milestone"), not the other way around.
>
> **Audience.** Chris (owner), future-Claude (orienting), and
> any attorney engaged to review or file. Treat this README as
> the entry point.

---

## At a glance

- **16 files total** — 12 invention disclosures (A–L) + 4 workstream executive summaries.
- **All dated** March 16, 2026 (single drafting batch, pre-session-attribution rigor).
- **Inventor** across all files: Chris West (DonkeyKing).
- **Status** across all files: Draft — Attorney Review Pending.
- **Coverage:** 11 of 12 disclosures map 1:1 onto Session 1158 narratives; disclosure L (self-tuning experimentation) is not yet narrative-covered.
- **Per memory rule [`feedback_docs_never_delete.md`]:** preserve all 16 files in place. They are draft legal material.

---

## Four workstreams

Each workstream groups related disclosures that share architecture, components, or claim themes.

### WS1 — Ops Autopilot (governance + autonomous control)

Covers how the platform autonomously governs its own agents — when to block, how to verify the block helped, how to escalate or de-escalate.

| Disclosure | Title | File |
|---|---|---|
| **A** | Evidence-Gated Blocking with Verification + Rollback | [DISCLOSURE_A_EVIDENCE_GATED_BLOCKING.md](DISCLOSURE_A_EVIDENCE_GATED_BLOCKING.md) |
| **B** | Lazy TTL Multi-Point Enforcement | [DISCLOSURE_B_LAZY_TTL_MULTIPOINT_ENFORCEMENT.md](DISCLOSURE_B_LAZY_TTL_MULTIPOINT_ENFORCEMENT.md) |
| **C** | Graduated Remediation Ladders | [DISCLOSURE_C_GRADUATED_REMEDIATION_LADDERS.md](DISCLOSURE_C_GRADUATED_REMEDIATION_LADDERS.md) |

Executive summary: [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)

### WS2 — Content Pipeline (claims-based deliberation + publish gate)

Covers how the platform generates publishable content by anchoring claims to evidence, structuring debate among LLM reviewers, and gating on quality before publish.

| Disclosure | Title | File |
|---|---|---|
| **D** | Claims-Based Deliberation | [DISCLOSURE_D_CLAIMS_BASED_DELIBERATION.md](DISCLOSURE_D_CLAIMS_BASED_DELIBERATION.md) |
| **E** | PublishGate Finishing Loop | [DISCLOSURE_E_PUBLISH_GATE_FINISHING_LOOP.md](DISCLOSURE_E_PUBLISH_GATE_FINISHING_LOOP.md) |
| **F** | Structured Debate Decision Enforcement | [DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md](DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md) |

Executive summary: [EXECUTIVE_SUMMARY_WS2.md](EXECUTIVE_SUMMARY_WS2.md)

### WS3 — Signal Intelligence (raw data → tracked work)

Covers how the platform turns spider-collected raw data into clustered signals, into topics, into tracked initiatives — with provenance preserved at every step and backlog throttled by a circuit breaker.

| Disclosure | Title | File |
|---|---|---|
| **G** | Signal-to-Initiative Provenance | [DISCLOSURE_G_SIGNAL_TO_INITIATIVE_PROVENANCE.md](DISCLOSURE_G_SIGNAL_TO_INITIATIVE_PROVENANCE.md) |
| **H** | Signal Clustering Pattern Detection | [DISCLOSURE_H_SIGNAL_CLUSTERING_PATTERN_DETECTION.md](DISCLOSURE_H_SIGNAL_CLUSTERING_PATTERN_DETECTION.md) |
| **I** | Initiative Circuit Breaker | [DISCLOSURE_I_INITIATIVE_CIRCUIT_BREAKER.md](DISCLOSURE_I_INITIATIVE_CIRCUIT_BREAKER.md) |

Executive summary: [EXECUTIVE_SUMMARY_WS3.md](EXECUTIVE_SUMMARY_WS3.md)

### WS4 — Budget Enforcement + Experimentation (steering spend, tuning behavior)

Covers how the platform enforces operational budgets at multiple granularities, schedules work under budget pressure, and self-tunes parameters based on observed outcomes.

| Disclosure | Title | File |
|---|---|---|
| **J** | Budget Enforcement QROI (Quality-weighted ROI) | [DISCLOSURE_J_BUDGET_ENFORCEMENT_QROI.md](DISCLOSURE_J_BUDGET_ENFORCEMENT_QROI.md) |
| **K** | Budget-Aware Scheduling | [DISCLOSURE_K_BUDGET_AWARE_SCHEDULING.md](DISCLOSURE_K_BUDGET_AWARE_SCHEDULING.md) |
| **L** | Self-Tuning Experimentation | [DISCLOSURE_L_SELF_TUNING_EXPERIMENTATION.md](DISCLOSURE_L_SELF_TUNING_EXPERIMENTATION.md) |

Executive summary: [EXECUTIVE_SUMMARY_WS4.md](EXECUTIVE_SUMMARY_WS4.md)

---

## Disclosure → Narrative cross-link map

For each disclosure, the Session 1158 narrative (and milestone where relevant) that documents the operator-facing shape of the same subsystem. **The patents claim the IP; the narratives explain the platform.** Cross-references go both ways: narratives may add "see also: docs/patents/DISCLOSURE_X" pointers (queued for a subsequent PR per the recon's recommendation).

| Disclosure | Narrative anchor | Specific tie-in |
|---|---|---|
| **A** | [AGENTS_AND_AUTONOMY.md](../narratives/AGENTS_AND_AUTONOMY.md) | Milestone 7 — governance & autonomy gates; `gate_hang` + rework/bounce gates |
| **B** | [AGENTS_AND_AUTONOMY.md](../narratives/AGENTS_AND_AUTONOMY.md) | `AgentControlEntry` + 4 enforcement points |
| **C** | [AGENTS_AND_AUTONOMY.md](../narratives/AGENTS_AND_AUTONOMY.md) + [BODY_SYSTEMS.md](../narratives/BODY_SYSTEMS.md) | `TimeoutRemediationPlaybook` + `BudgetController` + `ROIEnforcer` + LUNGS budget loop |
| **D** | [CONTENT_PIPELINE.md](../narratives/CONTENT_PIPELINE.md) | Milestone 2 — Session 964 deliberation watershed; ClaimsPack + deterministic IDs |
| **E** | [CONTENT_PIPELINE.md](../narratives/CONTENT_PIPELINE.md) | Milestones 6 + 7 — quality/novelty/structure gate + finishing loop (Session 1033) |
| **F** | [AGENTS_AND_AUTONOMY.md](../narratives/AGENTS_AND_AUTONOMY.md) + [DECISION_COMMAND.md](../narratives/DECISION_COMMAND.md) | Milestone 3 — DecisionEnforcerAgent + ResearchContract / ExecutionMandate / SynthesisContract |
| **G** | [SIGNAL_INTELLIGENCE.md](../narratives/SIGNAL_INTELLIGENCE.md) | Milestone 2 — Session 900 provenance chain |
| **H** | [SIGNAL_INTELLIGENCE.md](../narratives/SIGNAL_INTELLIGENCE.md) | `SignalAggregationService` + 10 pattern types |
| **I** | [SIGNAL_INTELLIGENCE.md](../narratives/SIGNAL_INTELLIGENCE.md) | Milestone 3 — circuit breaker + Jaccard dedup |
| **J** | [BODY_SYSTEMS.md](../narratives/BODY_SYSTEMS.md) | Milestone 2 (Session 702 LUNGS) — `can_breathe` + `record_breath` + QROI computation |
| **K** | [WORKERS_AND_INFRASTRUCTURE.md](../narratives/WORKERS_AND_INFRASTRUCTURE.md) | Celery routing + budget coupling |
| **L** | *(not yet narrative-covered)* | Experimentation / feedback loops; candidate for a future narrative addition |

---

## Status discipline

Per [`docs/narratives/EDITING_GUARDRAILS.md`](../narratives/EDITING_GUARDRAILS.md) and the no-fluff/verify-truth memory rule, claims about implementations should be verifiable at the runtime layer. The disclosures describe mechanisms that exist in code — see the "Components" or "Implementation" sections within each disclosure for class/file pointers. If a disclosure cites a component that has since been renamed or removed, the disclosure is **not** invalidated; the disclosure captures the invention at the time of drafting, which may pre-date refactors. Attorney review will reconcile claim language against current implementation.

**If you spot drift between a disclosure's component reference and current code:** update neither the disclosure nor the code in isolation. Either (a) note the drift in this README's "Open items" section below, (b) file an issue for attorney-review-time reconciliation, or (c) write a brief amendment doc in `docs/patents/amendments/` if the IP claim itself needs to track the code change. Direct edits to a disclosure to chase code drift would damage its provenance as a date-anchored disclosure.

---

## Open items (queued for future sessions)

1. **Narrative cross-linking from the other direction.** Add `See also: docs/patents/DISCLOSURE_X` pointers at the end of relevant milestones in narratives A / B / C / F + J + E. Queued for a subsequent PR per Session 1158 recon's recommended sequence.

2. **Disclosure L narrative coverage.** Self-tuning experimentation does not yet have a Session 1158 narrative. Either fold into an existing narrative (BODY_SYSTEMS? CONTENT_PIPELINE?) or write a new narrative when the subsystem matures enough to warrant operator-handbook treatment.

3. **Attorney engagement.** All 16 files carry "Draft — Attorney Review Pending." Engagement timing is a Chris-call, not a documentation issue.

4. **`amendments/` subdirectory if needed.** Not created yet. Add only when there's a concrete amendment to file; do not pre-create empty.

---

## Source

- Session 1158 recon: [`docs/recons/REPORTS_PATENTS_RECON_2026_05_25.md`](../recons/REPORTS_PATENTS_RECON_2026_05_25.md) §"docs/patents/ — file-by-file classification".
- The 16 underlying disclosure + executive-summary files (all March 16, 2026).
- Session 1158 narrative slate (provides the operator-handbook layer that the patents claim).
