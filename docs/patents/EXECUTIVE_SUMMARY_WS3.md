---
title: "Patent Workstream #3: Signal Intelligence Pipeline — Executive Summary"
kind: executive_summary
workstream: WS3 (Signal Intelligence)
status: draft (Attorney Review Pending)
last_updated: 2026-03-16
originating_session: pre-session-tracking (March 16, 2026 batch)
inventor: Chris West (DonkeyKing)
provenance_confidence: HIGH
provenance_note: Workstream #3 executive summary, covering disclosures G / H / I (signal-to-initiative provenance + clustering + circuit breaker). Frontmatter added Session 1160 (2026-05-26) as part of the patents preservation pass; body content unchanged from original March 16, 2026 draft.
maps_to_narratives:
  - docs/narratives/SIGNAL_INTELLIGENCE.md
covers_disclosures:
  - DISCLOSURE_G_SIGNAL_TO_INITIATIVE_PROVENANCE.md
  - DISCLOSURE_H_SIGNAL_CLUSTERING_PATTERN_DETECTION.md
  - DISCLOSURE_I_INITIATIVE_CIRCUIT_BREAKER.md
companion_docs:
  - docs/patents/README.md
---

# Patent Workstream #3: Signal Intelligence Pipeline — Executive Summary

**Date:** March 16, 2026
**Inventor:** Chris West (DonkeyKing)
**Platform:** Donkey Betz Unified AI Platform

---

## Three Invention Disclosures

### Disclosure G: End-to-End Signal-to-Initiative Provenance Pipeline
- **Core innovation:** 7-stage autonomous pipeline (spider → cluster → topic → conversation → decision → initiative → 5-stage pipeline) with full FK-linked provenance. Every initiative can trace back to the specific spider data that originated it.
- **Key differentiator:** Structural provenance via FK chains (not metadata), pattern-type-driven conversation routing, TRIAGE quarantine, embedding-based retroactive signal linking.
- **File:** `DISCLOSURE_G_SIGNAL_TO_INITIATIVE_PROVENANCE.md`

### Disclosure H: Multi-Source Signal Clustering with Pattern-Type Taxonomy
- **Core innovation:** 10-type business-relevant pattern taxonomy (demand_spike, trend_emergence, etc.) classified via keyword frequency, 8 independent quality metrics per cluster, 3-tier source confidence weighting (Reuters=1.0, Reddit=0.6, cat_facts=0.2), all computed without LLM inference.
- **Key differentiator:** Business-domain pattern classification via keyword frequency, source-tiered confidence, 8 independent metrics, zero LLM cost.
- **File:** `DISCLOSURE_H_SIGNAL_CLUSTERING_PATTERN_DETECTION.md`

### Disclosure I: Four-Gate Initiative Circuit Breaker with Jaccard Deduplication
- **Core innovation:** Four independent creation gates (env pause, DB pause, backlog threshold, daily limit), Jaccard keyword dedup (0.6 threshold) including recently completed initiatives, TRIAGE quarantine, and quality-gated ACTIVE promotion requiring owner + evidence.
- **Key differentiator:** Four-layer gate architecture, recently-completed inclusion in dedup, TRIAGE quarantine for auto-created projects, dual-requirement promotion (owner AND evidence).
- **File:** `DISCLOSURE_I_INITIATIVE_CIRCUIT_BREAKER.md`

---

## Running Total: 9 Disclosures Across 3 Workstreams

| WS | Focus | Disclosures | Independent Claims | Dependent Claims |
|----|-------|-------------|-------------------|-----------------|
| #1 | Ops Autopilot | A, B, C | 3 | 33 |
| #2 | Content/Decision Safety | D, E, F | 3 | 31 |
| #3 | Signal Intelligence | G, H, I | 3 | 24 |
| **Total** | | **9 disclosures** | **9** | **88** |

---

## Examiner Stories

### Disclosure G
Prior art teaches data pipeline orchestration (Airflow), topic modeling (BERTopic), and project management (Jira). However, no single reference teaches a system that clusters web-scraped data into signal patterns, generates qualified topics with stopword filtering, dispatches multi-agent conversations with FK provenance to originating signals, extracts decisions to create project initiatives with full provenance chains, and quarantines initiatives in triage status requiring quality-gated promotion.

### Disclosure H
Prior art teaches stream processing (Kafka), anomaly detection (Datadog), and topic modeling (BERTopic). However, no single reference teaches a system that classifies signal clusters into a 10-type business-relevant taxonomy via keyword frequency, computes 8 independent quality metrics per cluster including source-tiered confidence weighting, assigns pipeline tracks based on dominant scores, and computes all scores without language model inference.

### Disclosure I
Prior art teaches rate limiting (token buckets), circuit breakers (Hystrix), text deduplication (MinHash), and project workflows (Jira). However, no single reference teaches a system that evaluates creation requests against four independent gates at different control layers, deduplicates against active + triage + recently completed items using Jaccard similarity, quarantines auto-created projects in triage status, and promotes to active only upon verifying owner assignment and evidence linkage.
