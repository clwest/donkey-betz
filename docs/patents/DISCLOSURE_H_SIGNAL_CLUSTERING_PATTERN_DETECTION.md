---
title: "Invention Disclosure H: Multi-Source Signal Clustering with Pattern-Type Taxonomy and Source-Tiered Confidence Scoring"
kind: invention_disclosure
disclosure_id: H
workstream: WS3 (Signal Intelligence)
status: draft (Attorney Review Pending)
last_updated: 2026-03-16
originating_session: pre-session-tracking (March 16, 2026 batch)
inventor: Chris West (DonkeyKing)
provenance_confidence: HIGH
provenance_note: One of 12 invention disclosures drafted as a single March 16, 2026 batch. Frontmatter added Session 1160 (2026-05-26) as part of the patents preservation pass; body content unchanged from original draft. See `docs/patents/README.md` for workstream organization and narrative cross-link map.
maps_to_narratives:
  - docs/narratives/SIGNAL_INTELLIGENCE.md
companion_docs:
  - docs/patents/README.md
  - docs/patents/EXECUTIVE_SUMMARY_WS3.md
---

# Invention Disclosure H: Multi-Source Signal Clustering with Pattern-Type Taxonomy and Source-Tiered Confidence Scoring

**Date:** March 16, 2026
**Inventors:** Chris West (DonkeyKing)
**Status:** Draft — Attorney Review Pending

---

## 1. Working Title

Autonomous Signal Pattern Detection from Heterogeneous Web Sources with Taxonomy-Driven Classification, Multi-Metric Scoring, and Source-Tiered Confidence Weighting

---

## 2. Field / Technical Domain

Real-time signal intelligence for autonomous AI platforms. Specifically, methods for clustering data from heterogeneous web sources (news, social media, financial APIs, job boards, legal databases) into actionable signal patterns, classifying each pattern into a taxonomy of business-relevant types, and scoring pattern quality using source-tiered confidence weighting where different data sources contribute different levels of trust.

---

## 3. Problem

**a) Raw web data is noisy.** 79 spiders collecting from 18 categories produce thousands of data points per day. Without clustering, each data point is evaluated independently, missing cross-source patterns.

**b) Signal quality varies by source.** A Reuters article about market trends is more credible than a Reddit comment. Existing aggregation systems treat all sources equally or require manual source weighting.

**c) Pattern classification requires domain context.** A cluster of job postings indicates "skill demand"; a cluster of price movements indicates "market movement." Generic clustering (k-means, DBSCAN) doesn't provide business-relevant labels.

---

## 4. Solution Summary

A three-layer signal intelligence system:

1. **Clustering Layer**: Extracts keywords (pattern-type matching) and topics (regex matching) from SpiderData, clusters by topic/keyword similarity with a configurable minimum cluster size, and detects 10 pattern types via keyword frequency scoring.

2. **Multi-Metric Scoring Layer**: Each cluster receives 8 independent scores — strength (signal volume + source diversity + relevance), confidence (source count), novelty (age-decay), urgency (time-sensitivity), plus reach (viral potential), intent (commercial potential), replicability (repeatability), and source confidence (tier-weighted trust).

3. **Source-Tiered Confidence Layer**: Each spider/source is assigned to one of 3 trust tiers (Tier 1: 1.0x weight for Reuters, BBC, Nature; Tier 2: 0.6x for HackerNews, Reddit; Tier 3: 0.2x for novelty sources). The cluster's `source_confidence` is the weighted average of contributing sources' tier weights.

---

## 5. As-Built Mechanism

### Component 1: Signal Extraction

**File:** `core/services/signal_aggregation_service.py` (lines 151-241)

For each SpiderData record:
1. Extract readable text from `raw_data` (title, description, content, items array, embedding_text fallback)
2. Match text against **7 keyword lists** (one per primary pattern type), producing keyword hits
3. Match text against **10 topic regex patterns** (AI/ML, crypto, content/SEO, startup, remote work, etc.)
4. Output: `{spider_data_id, spider_name, keywords[max 10], topics[max 5], text_sample[200 chars], created_at, relevance_score}`

### Component 2: Keyword-Topic Clustering

**File:** `core/services/signal_aggregation_service.py` (lines 243-266)

- **Primary clustering key**: topic name (from regex match)
- **Secondary clustering key**: `kw:{first_keyword}` (when no topic matched)
- **Minimum cluster size**: 2 signals (configurable via `MIN_CLUSTER_SIZE`)
- **Deduplication**: One signal per cluster key per spider_name

### Component 3: Pattern-Type Classification

**File:** `core/services/signal_aggregation_service.py` (lines 435-448)

For each cluster, count keyword occurrences in each of 7 pattern-type keyword lists:

| Pattern Type | Keywords (subset) |
|-------------|------------------|
| demand_spike | need, want, looking for, seeking, demand, how to, recommend |
| trend_emergence | new, emerging, trending, rising, growing, breakthrough, innovative |
| sentiment_shift | changing, shift, moving away, no longer, prefer, better than, obsolete |
| opportunity_window | opportunity, chance, limited time, urgent, deadline, act fast |
| knowledge_gap | confused, unclear, don't understand, what is, explain, struggling |
| skill_demand | hiring, job, position, career, salary, remote, engineer, developer |
| content_gap | no good content, hard to find, underserved, missing, gap in |

Pattern type with highest keyword count wins. Default: `demand_spike`.

### Component 4: Multi-Metric Scoring

**8 independent scores per cluster (0-1 range):**

| Metric | Formula | Components |
|--------|---------|-----------|
| strength | `0.4*signal_factor + 0.4*diversity_factor + 0.2*relevance_factor` | signal_factor=min(count/20,1), diversity=min(sources/5,1), relevance=avg_score/100 |
| confidence | `min(source_count/4, 1)` if sources>=2, else 0.3 | Number of distinct spider sources |
| novelty | `max(0, 1 - avg_age_hours/24)` | Linear decay over 24 hours |
| urgency | Inherited from pattern urgency signals | Time-sensitivity of keywords |
| reach_score | `0.4*source_diversity + 0.3*keyword_reach + 0.3*strength` | Viral/audience potential |
| intent_score | `0.5*keyword_intent + 0.3*pattern_intent + 0.2*urgency` | Commercial potential |
| replicability_score | `0.5*is_evergreen + 0.3*has_multiple_sources + 0.2*0.5` | Repeatability |
| source_confidence | `sum(tier_weight * count) / total_count` | Tier-weighted source trust |

### Component 5: Source-Tiered Confidence

**File:** `core/services/content_scoring_service.py` (lines 120-135)

**3 tiers with 13/11/7 sources respectively:**

| Tier | Weight | Sources |
|------|--------|---------|
| **Tier 1** | 1.0 | reuters, bbc, techcrunch, nature, arxiv, espn, associated_press, bloomberg, wsj, nyt, guardian, coindesk, cointelegraph |
| **Tier 2** | 0.6 | hackernews, devto, reddit, venturebeat, medium, producthunt, ycombinator, substack, bluesky, mastodon, github_trending |
| **Tier 3** | 0.2 | giphy, spotify, noaa_weather, unsplash, random_user, cat_facts, dad_jokes |
| **Default** | 0.3 | Any unrecognized source |

**Calculation:** For a cluster with sources `{reuters: 3, reddit: 5, bluesky: 2}`:
```
source_confidence = (1.0*3 + 0.6*5 + 0.6*2) / (3+5+2) = (3.0+3.0+1.2)/10 = 0.72
```

### Component 6: Track Assignment

**File:** `core/services/content_scoring_service.py` (lines 137-147)

```
if intent >= 0.6: track = 'intent'      (commercially actionable)
elif reach >= 0.6: track = 'attention'   (audience-building)
elif intent >= 0.4 AND intent > reach: track = 'intent'
elif reach >= 0.4 AND reach > intent: track = 'attention'
else: track = 'unclassified'
```

### Component 7: Cluster Lifecycle

| Status | Meaning | Transition |
|--------|---------|-----------|
| detecting | Accumulating signals | → active when strength>=0.5 AND confidence>=0.5 |
| active | Pattern confirmed, actionable | → triggered when auto-topic dispatched |
| triggered | Conversation dispatched | Terminal for pipeline purposes |
| decayed | Pattern no longer relevant | After expiry (3 days default) |
| archived | Historical record | Cleanup task |

---

## 6. Novelty Hooks (Section 102)

**a) 10-type pattern taxonomy with keyword-frequency classification.** Signal clusters are classified into business-relevant types (demand_spike, trend_emergence, sentiment_shift, etc.) based on keyword frequency, not generic clustering. No known signal intelligence system provides this level of business-domain classification.

**b) Source-tiered confidence weighting.** Different data sources contribute different confidence weights based on a 3-tier trust hierarchy. A cluster dominated by Tier 1 sources (Reuters, BBC) scores higher than one dominated by Tier 3 sources (cat_facts). This source-aware scoring is absent from aggregation systems that treat sources equally.

**c) 8 independent scores per cluster.** Each cluster receives 8 scores measuring different quality dimensions. No known system scores signals on all of: strength, confidence, novelty, urgency, reach, intent, replicability, and source confidence simultaneously.

**d) Linear novelty decay over 24 hours.** Novelty score decays linearly based on average signal age, ensuring recent patterns score higher. This temporal decay integrated into cluster scoring is absent from static clustering approaches.

**e) Rule-based scoring without LLM inference.** All 8 scores use keyword matching, formula computation, and tier lookup — no LLM calls. This enables scoring thousands of clusters per minute at zero API cost.

---

## 7. Non-Obviousness Hooks (Section 103)

**a) Pattern-type classification via keyword frequency is non-obvious for signal intelligence.** The standard approach to classifying signal patterns is ML-based (clustering algorithms, transformers). Using keyword frequency matching against predefined lists is non-obvious because it appears too simple — but the insight is that business-relevant patterns map cleanly to keyword vocabularies, and the simplicity enables real-time classification without model training.

**b) Source-tiered confidence is non-obvious because it introduces editorial judgment into automated scoring.** The tier assignments (Reuters = 1.0, Reddit = 0.6, cat_facts = 0.2) encode human editorial judgment about source credibility. Automated systems typically avoid subjective source weighting. The insight: for business intelligence, not all sources are equal, and encoding this explicitly is more reliable than learning it from data.

**c) The combination of 8 independent metrics creates a non-obvious multi-axis evaluation.** Most scoring systems produce a single composite score. Using 8 independent scores enables nuanced filtering: "high reach but low intent" signals are treated differently from "high intent but low reach" signals. This multi-axis evaluation is non-obvious because it requires downstream consumers to handle multi-dimensional inputs.

---

## 8. Operational Benefits

- **Real-time pattern detection:** Signals are clustered within 6 hours of collection, enabling same-day response to trends
- **Zero LLM cost for scoring:** All 8 metrics computed via formulas and keyword matching
- **Source transparency:** `source_breakdown` field shows exactly which spiders contributed to each cluster
- **Temporal relevance:** 24h novelty decay ensures stale patterns naturally lose priority
- **Track routing:** Intent vs. attention classification enables different downstream processing

---

## 9. Alternative Embodiments

**a) ML-based pattern classification.** A trained classifier could replace keyword-frequency classification, potentially capturing subtler patterns at the cost of model maintenance.

**b) Dynamic source tier learning.** Instead of static tier assignments, source tiers could be learned from outcome data: sources whose signals lead to successful initiatives get promoted.

**c) Embedding-based clustering.** Instead of keyword/topic matching, signals could be clustered using embedding cosine similarity, potentially capturing semantic patterns missed by keyword matching.

**d) Hierarchical clustering.** Clusters could have parent-child relationships: a "crypto market movement" cluster containing sub-clusters for specific tokens.

**e) Cross-temporal pattern detection.** Instead of a single lookback window, the system could compare current patterns to historical patterns from the same time period (e.g., same day of week, same month last year).

---

## 10. Claim Skeleton

### Independent Method Claim

A computer-implemented method for detecting and classifying signal patterns from heterogeneous web data sources, the method comprising:

(a) collecting data records from a plurality of web sources across heterogeneous categories;

(b) extracting, from each data record, keywords by matching record text against a plurality of pattern-type keyword lists, and topics by matching record text against a plurality of topic regex patterns;

(c) clustering the data records by extracted keywords and topics, retaining only clusters meeting a configurable minimum size threshold;

(d) classifying each cluster into a pattern type from a predefined taxonomy by counting keyword occurrences in each pattern-type keyword list and selecting the type with the highest count;

(e) computing, for each cluster, a plurality of independent quality scores including at least a strength score based on signal volume and source diversity, a confidence score based on the number of distinct data sources, and a novelty score that decays linearly with average signal age; and

(f) computing a source confidence score for each cluster as a weighted average of tier weights assigned to contributing data sources, wherein each data source is assigned to one of a plurality of trust tiers with different weights.

### Dependent Claims

1. The method of the independent claim, wherein the pattern type taxonomy comprises at least: demand spike, trend emergence, sentiment shift, opportunity window, knowledge gap, skill demand, and content gap.

2. The method of the independent claim, wherein the trust tiers comprise at least three tiers: a first tier with weight 1.0 for authoritative news and research sources, a second tier with weight 0.6 for community and developer sources, and a third tier with weight 0.2 for novelty and entertainment sources.

3. The method of the independent claim, further comprising computing reach, intent, and replicability scores using keyword matching against domain-specific keyword lists.

4. The method of the independent claim, further comprising assigning each cluster to a pipeline track based on the dominant score among reach and intent.

5. The method of the independent claim, wherein the strength score is computed as a weighted sum of a signal count factor, a source diversity factor, and an average relevance factor.

6. The method of the independent claim, wherein clusters transition through a lifecycle of statuses: detecting, active, triggered, decayed, and archived.

7. The method of the independent claim, wherein all quality scores are computed using rule-based formulas and keyword matching without language model inference.

8. A system comprising one or more processors and memory storing instructions that, when executed, perform the method of the independent claim.

---

## 11. Diagrams to Draft

**Figure 1 — Signal Extraction and Clustering**
```
[SpiderData records (500 max)]
      |
[Extract keywords (pattern-type matching)]
[Extract topics (regex matching)]
      |
[Cluster by topic (primary) or keyword (secondary)]
      |
[Filter: size >= MIN_CLUSTER_SIZE]
      |
[SignalCluster records]
```

**Figure 2 — 8-Metric Scoring Dashboard**
```
SignalCluster: "AI Agent Demand Spike"
  strength:        0.72  ████████░░
  confidence:      0.85  █████████░
  novelty:         0.91  ██████████
  urgency:         0.45  █████░░░░░
  reach_score:     0.68  ███████░░░
  intent_score:    0.82  █████████░
  replicability:   0.60  ██████░░░░
  source_confidence: 0.74 ████████░░

  Track: intent (intent_score >= 0.6)
```

**Figure 3 — Source-Tiered Confidence**
```
Tier 1 (1.0x): [reuters] [bbc] [techcrunch] [nature] [arxiv]
Tier 2 (0.6x): [hackernews] [reddit] [devto] [medium]
Tier 3 (0.2x): [giphy] [cat_facts] [dad_jokes]

Cluster with {reuters:3, reddit:5, bluesky:2}:
  confidence = (1.0×3 + 0.6×5 + 0.6×2) / 10 = 0.72
```

---

## 12. Prior Art Buckets

**a) Stream Processing (Apache Kafka, Flink)** — Teaches event aggregation but not pattern-type taxonomy or source-tiered scoring.

**b) Anomaly Detection (Datadog, Splunk)** — Teaches threshold-based alerting but not multi-source signal clustering with business-relevant classification.

**c) Topic Modeling (BERTopic, LDA)** — Teaches unsupervised topic extraction but not keyword-frequency pattern classification or source confidence weighting.

**d) News Aggregation (Google News, Feedly)** — Teaches article grouping but not 8-metric scoring or source-tiered confidence.

**e) Threat Intelligence (Recorded Future)** — Teaches signal scoring for security but not business-domain pattern types or autonomous initiative generation.

---

## Examiner Story

Prior art teaches stream processing for event aggregation (Kafka), anomaly detection with threshold alerting (Datadog), and unsupervised topic modeling (BERTopic). However, no single reference teaches a system that (1) classifies signal clusters into a 10-type business-relevant taxonomy via keyword frequency scoring, (2) computes 8 independent quality metrics per cluster including source-tiered confidence weighting where different data sources contribute different trust weights, (3) assigns pipeline tracks (intent vs. attention) based on dominant metric scores, and (4) computes all scores using rule-based formulas without language model inference. The combination is non-predictable because signal intelligence systems typically use ML-based classification rather than keyword frequency, treat all sources equally rather than tiering them, and produce single composite scores rather than 8 independent metrics.
