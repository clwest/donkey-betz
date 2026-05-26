---
title: "Patent Workstream #4: Budget-Aware Scheduling + ROI Throttling — Executive Summary"
kind: executive_summary
workstream: WS4 (Budget Enforcement + Experimentation)
status: draft (Attorney Review Pending)
last_updated: 2026-03-16
originating_session: pre-session-tracking (March 16, 2026 batch)
inventor: Chris West (DonkeyKing)
provenance_confidence: HIGH
provenance_note: Workstream #4 executive summary, covering disclosures J / K / L (multi-tier budget enforcement + budget-aware scheduling + self-tuning experimentation). Frontmatter added Session 1160 (2026-05-26) as part of the patents preservation pass; body content unchanged from original March 16, 2026 draft.
maps_to_narratives:
  - docs/narratives/BODY_SYSTEMS.md
  - docs/narratives/WORKERS_AND_INFRASTRUCTURE.md
covers_disclosures:
  - DISCLOSURE_J_BUDGET_ENFORCEMENT_QROI.md
  - DISCLOSURE_K_BUDGET_AWARE_SCHEDULING.md
  - DISCLOSURE_L_SELF_TUNING_EXPERIMENTATION.md
companion_docs:
  - docs/patents/README.md
---

# Patent Workstream #4: Budget-Aware Scheduling + ROI Throttling — Executive Summary

**Date:** March 16, 2026
**Inventor:** Chris West (DonkeyKing)
**Platform:** Donkey Betz Unified AI Platform

---

## Three Invention Disclosures

### Disclosure J: Multi-Tier Budget Enforcement with QROI Throttling
- **Core innovation:** Three-tier budget enforcement (normal → model downgrade → freeze) with purpose-based exemptions, plus quality-weighted ROI (QROI = ROI × quality_weight) per-agent throttling with graduated cooldowns, activated only during budget pressure.
- **Key differentiator:** Model downgrade as intermediate tier, multiplicative QROI metric, budget-tier-gated throttle activation, purpose-based (not agent-based) exemptions.
- **File:** `DISCLOSURE_J_BUDGET_ENFORCEMENT_QROI.md`

### Disclosure K: Budget-Aware Task Scheduling with Knob-Based Downscoping
- **Core innovation:** Three-tier task classification (heavy/moderate/light LLM), preflight decision engine (proceed/downscope/defer), per-task parameter knobs with pressure-level values, and attribution debt-gated portfolio reallocation with EWMA sensitivity adaptation.
- **Key differentiator:** Per-task downscoping knobs (not cancel/proceed binary), attribution debt blocking reallocation, EWMA alpha reduction under data quality degradation.
- **File:** `DISCLOSURE_K_BUDGET_AWARE_SCHEDULING.md`

### Disclosure L: Self-Tuning Policy Framework with A/B Experimentation
- **Core innovation:** PolicyOptimizer analyzing action history to auto-tune parameters (rate-limited: 1/eval, 2/day), ExperimentEngine A/B testing operational parameters with auto-promote (10% improvement) and auto-rollback (5% regression), PolicyArbitrator with priority-based conflict resolution, anti-flap detection (3+ changes/24h → lock), and per-cycle FinalAppliedOverrides snapshots.
- **Key differentiator:** Self-tuning ops parameters (not ML hyperparameters), A/B testing infrastructure parameters (not product features), anti-flap with hold-time enforcement, time-travel audit snapshots.
- **File:** `DISCLOSURE_L_SELF_TUNING_EXPERIMENTATION.md`

---

## Grand Total: 12 Disclosures Across 4 Workstreams

| WS | Focus | Disclosures | Independent Claims | Dependent Claims |
|----|-------|-------------|-------------------|-----------------|
| #1 | Ops Autopilot | A, B, C | 3 | 33 |
| #2 | Content/Decision Safety | D, E, F | 3 | 31 |
| #3 | Signal Intelligence | G, H, I | 3 | 24 |
| #4 | Budget/ROI/Scheduling | J, K, L | 3 | 22 |
| **Total** | | **12 disclosures** | **12** | **110** |

---

## Examiner Stories

### Disclosure J
Prior art teaches cloud cost alerting (AWS Budgets), API rate limiting (token buckets), and LLM model routing (LiteLLM). However, no single reference teaches three graduated budget tiers with intermediate model downgrade, per-agent QROI (ROI × quality) throttling activated only during budget pressure, and purpose-based exemptions that apply to invocation context not agent identity.

### Disclosure K
Prior art teaches scheduled task execution (Kubernetes CronJob), resource allocation (YARN), and cost attribution (Kubecost). However, no single reference teaches per-task preflight decisions based on LLM-cost-tier classification, task-specific parameter knobs for graceful degradation under budget pressure, and attribution debt-gated portfolio reallocation with adaptive EWMA smoothing.

### Disclosure L
Prior art teaches hyperparameter optimization (Optuna), A/B testing for features (Optimizely), distributed configuration (Consul), and policy engines (OPA). However, no single reference teaches autonomous policy parameter self-tuning with rate-limited application, A/B testing of operational parameters with auto-promote/rollback, multi-policy conflict arbitration with priority-ordered knob registries, and anti-flap detection that locks oscillating configuration keys with human escalation.
