# Invention Disclosure G: End-to-End Signal-to-Initiative Provenance Pipeline with Autonomous Topic Generation and Conversation Dispatch

**Date:** March 16, 2026
**Inventors:** Chris West (DonkeyKing)
**Status:** Draft — Attorney Review Pending

---

## 1. Working Title

Autonomous Signal-to-Initiative Pipeline with Full Provenance Tracking from Data Collection Through Multi-Agent Conversation to Actionable Project Creation

---

## 2. Field / Technical Domain

Autonomous intelligence systems for AI platforms. Specifically, methods for transforming raw data signals from heterogeneous web sources into structured project initiatives through a multi-stage pipeline that preserves full provenance: data collection → pattern clustering → topic generation → agent conversation → decision extraction → initiative creation with 5-stage execution pipeline, where every downstream artifact links back to its originating signal sources.

---

## 3. Problem (What Breaks in Prior Systems)

Autonomous systems that monitor external data and generate internal projects face three provenance challenges:

**a) No traceable path from signal to action.** Systems that aggregate data and trigger workflows cannot answer "why was this initiative created?" The link between a trending topic on social media and a resulting project is lost in the pipeline.

**b) Topic generation is either manual or naive.** Systems either require humans to identify topics from data (expensive, slow) or use simple keyword matching (low quality, high false positive rate). There is no intermediate stage that clusters signals, detects patterns, generates qualified topics, and triggers appropriate specialist conversations.

**c) Conversation outcomes don't become trackable work.** Multi-agent conversations produce synthesis text but don't automatically create structured projects with stages, action items, owners, and deadlines. The gap between "agents discussed X" and "project X is underway" requires manual intervention.

---

## 4. Solution Summary

A 7-stage autonomous pipeline with full provenance:

1. **SpiderData Collection**: 79 spiders collect data from 18 categories, embedded as 1536-dim vectors via pgvector
2. **Signal Clustering**: `SignalAggregationService` extracts keywords/topics, clusters by similarity, detects 10 pattern types, scores strength/confidence/novelty/urgency
3. **Content Scoring**: Rule-based reach/intent/replicability scoring with 3-tier source confidence weighting assigns pipeline track (attention vs. intent)
4. **Topic Generation**: `generate_auto_topics()` creates qualified `AutoTopic` records with stopword-filtered names, suggested agents, conversation types, and 2-day expiry
5. **Conversation Dispatch**: `trigger_signal_driven_conversation()` creates `HiveMindSession` with signal_cluster + auto_topic FKs, dispatches multi-agent debate
6. **Decision Extraction**: Parses `=== DecisionSummary ===` from conversation synthesis, extracts proposed features and next steps
7. **Initiative Creation**: Creates `Initiative` in TRIAGE status with signal provenance FKs, 5-stage pipeline, auto-assigned owner, and auto-linked signal cluster

Every downstream record (AutoTopic, HiveMindSession, Initiative, InitiativeActionItem) carries foreign keys back to its originating SignalCluster and SpiderData sources.

---

## 5. As-Built Mechanism (Numbered Steps + Components)

### Stage 1: Data Collection and Embedding

**79 spiders** across 18 categories collect data into `SpiderData` records. Each record is embedded as a 1536-dimensional vector (OpenAI `text-embedding-3-small`) stored in pgvector.

- Backfill task runs every 10 minutes, batch-embedding up to 200 entries per cycle
- Empty entries marked `[NO_ITEMS]` to prevent infinite retry loops
- ~85% embedding coverage across all SpiderData records

### Stage 2: Signal Aggregation and Pattern Clustering

**Component:** `SignalAggregationService` (`core/services/signal_aggregation_service.py`, 657 lines)

1. Fetch recent SpiderData (configurable lookback, default 6h, limit 500)
2. Extract structured signals: keywords (pattern-type matching), topics (regex matching), text samples
3. Cluster by topic similarity: primary key = topic name, secondary key = `kw:{first_keyword}`
4. Filter: only clusters with `size >= MIN_CLUSTER_SIZE` (2) proceed
5. Calculate 4 metrics per cluster:
   - `strength = signal_factor(0.4) + diversity_factor(0.4) + relevance_factor(0.2)` where signal_factor = min(count/20, 1), diversity = min(sources/5, 1)
   - `confidence = min(source_count/4, 1)` if sources >= 2, else 0.3
   - `novelty = max(0, 1 - avg_age_hours/24)` — decays linearly over 24h
   - `pattern_type` = keyword-scored classification into 10 types
6. Create/update `SignalCluster` records: `status='active'` when strength >= 0.5 AND confidence >= 0.5

**10 pattern types:** demand_spike, trend_emergence, sentiment_shift, opportunity_window, knowledge_gap, competitive_signal, market_movement, skill_demand, content_gap, user_need

### Stage 3: Content Scoring (Rule-Based, No LLM)

**Component:** `ContentScoringService` (`core/services/content_scoring_service.py`, 167 lines)

Each active cluster receives 4 additional scores:
- `reach_score = 0.4*source_diversity + 0.3*keyword_reach + 0.3*strength`
- `intent_score = 0.5*keyword_intent + 0.3*pattern_intent + 0.2*urgency`
- `replicability_score = 0.5*is_evergreen + 0.3*has_multiple_sources + 0.2*is_recurring`
- `source_confidence` = weighted average of source tier weights (Tier 1: 1.0, Tier 2: 0.6, Tier 3: 0.2, Default: 0.3)

**Track assignment:** intent >= 0.6 → 'intent'; reach >= 0.6 → 'attention'; else 'unclassified'

### Stage 4: Topic Generation with Quality Gate

**Method:** `generate_auto_topics()` (lines 473-657)

1. Query active clusters with confidence >= 0.5, not already triggered, ordered by `-strength, -confidence`, limit 10
2. **Topic quality gate (Session 1010):** Filter keywords against stopword list (35+ words). Skip cluster if ALL keywords are stopwords.
3. Generate topic name from non-stopword keywords + pattern-type template (e.g., demand_spike → "Addressing {keywords} demand")
4. Generate description with signal count, source count, source names, key themes
5. Generate rationale with source breakdown, strength %, confidence %, sample text
6. Suggest agents by pattern type (base agents) + keyword matching (specialist agents for crypto, blockchain, stock, marketing, SEO, code, legal)
7. Map conversation type: demand_spike/trend_emergence/knowledge_gap → 'analytical', sentiment_shift → 'debate', opportunity_window/skill_demand → 'planning', content_gap → 'creative'
8. Create `AutoTopic` with status='pending', expires in 2 days

### Stage 5: Conversation Dispatch

**Task:** `trigger_signal_driven_conversation()` (`core/tasks_conversations.py:3330-3433`)

1. Fetch pending AutoTopic, validate status
2. Resolve suggested agent names → Agent objects (fallback: ContentStrategyAgent, ResearchAgent, TrendAnalysisAgent)
3. Create `HiveMindSession` with:
   - `session_mode='conversation'`
   - `signal_cluster` FK → originating cluster
   - `auto_topic` FK → originating topic
   - `trigger_confidence` = auto_topic.confidence
   - `conversation_type` from auto_topic
   - `objective` = "Discuss and provide actionable insights on: {topic}"
   - `success_criteria` = ["Identify key opportunities or risks", "Propose concrete next steps", "Reach consensus on recommendations"]
4. Mark AutoTopic as triggered (status='triggered', triggered_session_id=session.id)
5. Also mark SignalCluster as triggered (status='triggered')
6. Dispatch conversation execution via Celery

### Stage 6: Decision Extraction

**Component:** `HiveMindExecutionPipeline` (`core/services/hivemind_execution_pipeline.py`)

Parses `=== DecisionSummary ===` sections from synthesis text:
- `insights`: List of key insights
- `proposed_feature`: Dict with name, inputs, outputs, integration points
- `next_steps`: List of dicts with agent assignments and tasks

### Stage 7: Initiative Creation with Full Provenance

**Method:** `_create_initiative_from_feature()` (lines 424-556)

1. **Circuit breaker check** (4 gates — see Disclosure I)
2. **Title generation** via `generate_initiative_title()` (LLM-assisted, max 80 chars)
3. **Jaccard dedup** (0.6 threshold) against active/triage + recently completed initiatives
4. Create `Initiative` with:
   - `status='TRIAGE'` (auto-created, not reviewed)
   - `signal_cluster` FK → originating cluster
   - `auto_topic` FK → originating topic
   - `source_decision_id` = HiveMindSession UUID
   - `created_by` = `"HiveMind:{session_id[:8]}"`
5. Auto-set founder intent (execution_speed='balanced', risk_tolerance='balanced')
6. Auto-assign owner via `_auto_assign_owner()`
7. Auto-link signal cluster via `auto_link_initiative_signals()` (embedding-based, similarity >= 0.60)
8. Create 5 stages in PENDING status
9. Trigger Stage 1 document generation

### Provenance Chain (FK relationships)

```
SpiderData[uuid1, uuid2, ...] ← SignalCluster.spider_data_ids (JSON list)
SignalCluster ← AutoTopic.signal_cluster (FK)
AutoTopic ← HiveMindSession.auto_topic (FK)
SignalCluster ← HiveMindSession.signal_cluster (FK)
HiveMindSession ← Initiative.source_decision_id (UUID)
SignalCluster ← Initiative.signal_cluster (FK)
AutoTopic ← Initiative.auto_topic (FK)
```

Every initiative can trace: which spider data → which cluster → which topic → which conversation → which decision created it.

---

## 6. Novelty Hooks (Section 102)

**a) Full FK-linked provenance chain from raw data to project.** Every downstream artifact (AutoTopic, HiveMindSession, Initiative) carries FK references to its originating SignalCluster and SpiderData sources. No known system provides traceable provenance from web-scraped data through pattern detection through multi-agent conversation to structured project creation.

**b) Pattern-type-driven conversation routing.** The detected pattern type (demand_spike, sentiment_shift, etc.) determines both the conversation type (analytical, debate, planning, creative) and the suggested specialist agents. This domain-aware routing is absent from generic task orchestration systems.

**c) Topic quality gate with stopword filtering.** Auto-generated topics are filtered against a 35+ stopword list, preventing word-salad topic names. Clusters with all-stopword keywords are skipped entirely. This pre-generation quality gate is absent from topic modeling systems.

**d) Triage status with quality-gated promotion.** Auto-created initiatives start as TRIAGE (not ACTIVE), requiring owner assignment and evidence indicators before promotion. This prevents the pipeline from flooding the active queue with unvetted initiatives.

**e) Embedding-based retroactive signal linking.** Initiatives that aren't created directly from signals can be retroactively linked via `auto_link_initiative_signals()`, which computes cosine similarity between initiative descriptions and cluster keywords/samples. This bidirectional linking is absent from pipeline systems.

---

## 7. Non-Obviousness Hooks (Section 103)

**a) The 7-stage pipeline preserves provenance without centralized tracking.** Each stage creates records with FK references to the previous stage. There is no centralized "provenance service" — provenance emerges from the relational structure. This is non-obvious because distributed pipelines typically require explicit provenance tracking infrastructure.

**b) Pattern-type classification drives both topic naming and conversation routing.** Using the same classification for naming templates AND agent selection AND conversation type creates a unified semantic layer. This triple-use is non-obvious because naming, routing, and conversation structure are typically treated as independent concerns.

**c) TRIAGE → ACTIVE promotion gate prevents pipeline flooding.** The obvious design is to create initiatives in ACTIVE status. Requiring promotion through a quality gate (owner + evidence) is non-obvious because it deliberately slows the pipeline to improve quality.

**d) 2-day topic expiry with stopword filtering creates a self-pruning queue.** Topics that aren't triggered within 2 days expire automatically, and topics with all-stopword keywords are never created. This dual-pruning mechanism is non-obvious because it requires accepting that some detected patterns are not worth discussing.

---

## 8. Operational Benefits

- **Full traceability:** Any initiative can answer "why does this exist?" by following FK chain to originating spider data
- **Quality filtering:** Stopword gate + TRIAGE status + Jaccard dedup prevent low-quality and duplicate initiatives
- **Autonomous operation:** Pipeline runs 24/7 via Celery Beat without human intervention
- **Domain-aware routing:** Pattern types ensure specialist agents discuss topics in their domain
- **Self-pruning:** Expired topics and decayed clusters are automatically archived

---

## 9. Alternative Embodiments

**a) Graph-based provenance tracking.** Instead of FK chains, a dedicated provenance graph (Neo4j, knowledge graph) could track relationships between all pipeline artifacts, enabling complex provenance queries ("which spiders contributed to completed initiatives?").

**b) Confidence-weighted topic prioritization.** Topics could be prioritized not just by urgency/confidence but by predicted initiative success rate (ML model trained on historical signal→initiative→completion data).

**c) Multi-hop conversation chains.** Instead of single conversations, topics could trigger sequential conversations: initial exploration → focused analysis → action planning, each building on the previous.

**d) Real-time streaming pipeline.** Instead of batch processing (6h lookback, 10-min cycles), signals could flow through a streaming pipeline (Apache Kafka/Flink) for sub-minute topic generation.

**e) User preference-weighted signal scoring.** Signal scoring could incorporate user-specific weights: a user focused on crypto would see crypto signals scored higher, personalizing the initiative generation pipeline.

---

## 10. Claim Skeleton

### Independent Method Claim

A computer-implemented method for autonomously generating project initiatives from heterogeneous data signals, the method comprising:

(a) collecting data from a plurality of heterogeneous web sources into structured data records, each record embedded as a high-dimensional vector;

(b) clustering the data records by extracted keywords and topics into signal clusters, each cluster assigned a pattern type from a predefined taxonomy and scored on strength, confidence, novelty, and urgency;

(c) generating, from qualifying signal clusters, auto-topic records with qualified names filtered against a stopword list, suggested specialist agents based on the pattern type, and a suggested conversation type;

(d) dispatching a multi-agent conversation for each auto-topic, the conversation session linked via foreign key to both the originating signal cluster and the auto-topic;

(e) extracting a structured decision from the conversation synthesis, the decision comprising proposed features and next steps with agent assignments;

(f) creating a project initiative from the extracted decision, the initiative linked via foreign keys to the originating signal cluster, auto-topic, and conversation session; and

(g) initializing the initiative with a triage status, a multi-stage execution pipeline, and an auto-assigned owner, wherein promotion from triage to active status requires a quality gate verifying owner assignment and evidence linkage.

### Dependent Claims

1. The method of the independent claim, wherein the pattern type taxonomy comprises at least: demand spike, trend emergence, sentiment shift, opportunity window, knowledge gap, skill demand, and content gap.

2. The method of the independent claim, wherein the suggested conversation type is determined by the pattern type, mapping analytical patterns to analytical conversations, sentiment patterns to debate conversations, opportunity patterns to planning conversations, and content patterns to creative conversations.

3. The method of the independent claim, further comprising scoring each signal cluster on reach, intent, replicability, and source confidence using rule-based keyword matching and source tier weighting, and assigning a pipeline track based on the dominant score.

4. The method of the independent claim, wherein auto-topic names are generated by combining non-stopword keywords with pattern-type-specific templates, and topics with all-stopword keywords are skipped.

5. The method of the independent claim, further comprising retroactively linking initiatives not created from signals to matching signal clusters using embedding-based cosine similarity with a configurable threshold.

6. The method of the independent claim, wherein the auto-topic records expire after a configurable duration and expired topics are automatically marked with an expired status.

7. The method of the independent claim, further comprising deduplicating proposed initiatives against existing active and recently completed initiatives using Jaccard keyword similarity with a configurable threshold.

8. The method of the independent claim, wherein the multi-stage execution pipeline comprises five stages: research brief, prototype plan, evaluation protocol, technical design, and pilot execution.

9. A system comprising one or more processors and memory storing instructions that, when executed, perform the method of the independent claim.

---

## 11. Diagrams to Draft

**Figure 1 — Full Provenance Pipeline**
```
[79 Spiders] → [SpiderData + embedding]
                     ↓
[SignalAggregationService] → [SignalCluster]
  keywords, topics, metrics      pattern_type, strength
                                     ↓
[ContentScoringService] → reach, intent, replicability, track
                                     ↓
[generate_auto_topics()] → [AutoTopic]
  stopword filter, agent suggest     signal_cluster FK
                                     ↓
[trigger_signal_driven_conversation()] → [HiveMindSession]
  agent dispatch, debate                  signal_cluster FK, auto_topic FK
                                     ↓
[Decision Extraction] → proposed_feature, next_steps
                                     ↓
[Initiative Creation] → [Initiative (TRIAGE)]
  circuit breaker, dedup              signal_cluster FK, auto_topic FK
                                     ↓
[5-Stage Pipeline] → [InitiativeStage × 5]
  auto-progression, action items
```

**Figure 2 — FK Provenance Chain**
```
SpiderData ──(JSON list)──> SignalCluster
                               ├──(FK)──> AutoTopic
                               │              ├──(FK)──> HiveMindSession
                               │              │              └──(UUID)──> Initiative
                               ├──(FK)──> HiveMindSession
                               └──(FK)──> Initiative
```

---

## 12. Prior Art Buckets to Cite Against

**a) Data Pipeline Orchestrators (Airflow, Prefect, Dagster)** — Teach task orchestration but not signal clustering, pattern detection, or provenance from data to project.

**b) Topic Modeling (LDA, BERTopic, Top2Vec)** — Teach topic extraction but not pattern-type classification, topic quality gating, or automatic conversation dispatch.

**c) Project Management Tools (Jira, Linear, Asana)** — Teach project tracking but not autonomous project creation from data signals.

**d) Signal Intelligence (Recorded Future, Anomali)** — Teach threat signal detection but not multi-agent conversation dispatch or initiative creation.

**e) Knowledge Graphs (Neo4j, Amazon Neptune)** — Teach entity/relationship tracking but not the specific pipeline stages or autonomous conversation-to-project conversion.

---

## Examiner Story

Prior art teaches data pipeline orchestration (Airflow), topic modeling from text corpora (BERTopic), and project management with workflow tracking (Jira). However, no single reference teaches a system that (1) clusters heterogeneous web-scraped data into signal patterns classified by a 10-type taxonomy, (2) generates qualified topic records with stopword-filtered names and pattern-type-driven agent/conversation suggestions, (3) dispatches multi-agent conversations from auto-topics with FK provenance to originating signals, (4) extracts structured decisions from conversation synthesis and creates project initiatives with full FK provenance chain, and (5) initializes initiatives in a triage status requiring quality-gated promotion before active execution. The combination is non-predictable because data pipelines treat provenance as metadata not structural relationships, topic models don't drive conversation dispatch, and project tools require manual project creation.
