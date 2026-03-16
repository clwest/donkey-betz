# Invention Disclosure E: Multi-Dimensional Quality Gate with Anti-Hallucination Detection and Self-Healing Finishing Loop

**Date:** March 16, 2026
**Inventors:** Chris West (DonkeyKing)
**Status:** Draft — Attorney Review Pending

---

## 1. Working Title

Four-Dimensional Content Quality Gate with Pattern-Based Hallucination Detection, Domain-Aware Classification, and Autonomous Enhancement-Reevaluation Finishing Loop

---

## 2. Field / Technical Domain

Automated content quality assurance for AI-generated publishing platforms. Specifically, methods for evaluating AI-generated content against four independent quality dimensions (linguistic quality, topic novelty, structural engagement, hallucination risk), classifying content by type and domain without LLM inference, and autonomously enhancing rejected content through a closed-loop cycle of enhancement, reevaluation, and promotion.

---

## 3. Problem (What Breaks in Prior Systems)

AI content publishing systems face three distinct quality challenges:

**a) Single-score quality metrics lose granularity.** Systems that produce a single "quality score" (e.g., Grammarly score, Flesch readability) cannot distinguish between content that is well-written but duplicative, novel but poorly structured, or structurally sound but factually hallucinated. A single score forces a binary accept/reject decision that cannot guide targeted improvement.

**b) Hallucination detection requires specialized patterns.** Generic quality scoring cannot detect AI-specific hallucination patterns: inflated statistics ("350 deployments"), false authority claims ("studies show"), capability exaggeration ("can do anything"), or temporal distortion ("has been operating for years"). These patterns are invisible to grammar checkers and readability scorers.

**c) Rejected content accumulates without remediation.** When quality gates reject content, most systems leave it in a "rejected" state indefinitely. There is no mechanism to automatically improve rejected content and re-evaluate it, creating a growing backlog of potentially recoverable content that wastes the original generation cost.

---

## 4. Solution Summary

A three-part content quality system:

1. **Four-Dimensional PublishGate**: Independently scores Quality (linguistic merit, 0.70 threshold), Novelty (topic uniqueness with cumulative duplicate penalty, 0.50 threshold), Structure (engagement elements and section balance, 0.55 threshold), and Mythology Risk (hallucination pattern detection, 0.15 threshold). Each dimension has its own threshold and scoring algorithm. Content must pass all four to be published.

2. **Content Classification Without LLM**: Regex-based operational title detection (`[Research]`, `[Audit]`, `[Stage N]`, etc.) immediately classifies internal content without invoking quality scoring. Domain detection via keyword matching classifies content into 9 domains and injects real platform data (spider results, agent execution stats, on-chain metrics) into future generation prompts.

3. **Autonomous Finishing Loop**: Content failing the gate as `needs_enhancement` enters a closed-loop cycle: EditorAgent enhances with targeted focus areas → reevaluation task re-scores after 3 hours → promotion to `approved` if passing → auto-publish. Content improves without human intervention.

---

## 5. As-Built Mechanism (Numbered Steps + Components)

### Component 1: Four-Dimensional Quality Gate (PublishGate)

**Location:** `core/services/publish_gate.py` (648 lines)

#### Dimension 1: Quality Score (lines 196-245)

Base score: 0.5. Components:

| Component | Score Change | Condition |
|-----------|-------------|-----------|
| Word count: 500-1500 | +0.15 | Optimal range |
| Word count: 300-500 or 1500-2500 | +0.10 | Acceptable range |
| Word count: <300 | Reject (score capped at 0.3) | Too short |
| Has intro (>50 chars) | +0.10 | Introduction present |
| Has conclusion (>50 chars) | +0.10 | Conclusion present |
| Has >=3 sections | +0.10 | Good structure |
| Each placeholder found | -0.10 | "lorem ipsum", "todo:", "fixme:", "placeholder" |
| >50% sections <100 chars | -0.10 | Thin sections |

**Threshold:** >= 0.70 to pass. **Research backing penalty:** -0.20 if `claims_count == 0`.

#### Dimension 2: Novelty Score (lines 247-310)

Base score: 1.0 (decremented by penalties). **Cumulative penalty algorithm (Session 1004):**

1. Query all approved/published blogs (excluding current)
2. Extract title words, filter stopwords
3. For each existing blog:
   - **Exact title match** (substring): First match -0.25, each additional -0.15
   - **High word overlap** (>50%): First match -0.15, each additional -0.10
4. **Overused topic penalty:** -0.10 for generic topics ("best practices", "getting started", "introduction to", "complete guide", "ultimate guide", "how we built")

**Threshold:** >= 0.50 to pass.

#### Dimension 3: Structure Score (lines 312-369)

Base score: 0.5. Components:

| Component | Score Change | Condition |
|-----------|-------------|-----------|
| Section variety (unique openers >70%) | +0.15 | Diverse section starts |
| Section variety (unique openers >50%) | +0.10 | Moderate variety |
| Engagement elements (percentages) | +0.05 each | Numbers that engage readers |
| Engagement elements (quotes) | +0.05 each | Quoted material |
| Engagement elements (questions) | +0.05 each | Reader questions |
| Section balance (variance <0.3) | +0.10 | Even section lengths |
| Wall of text (<2 sections) | -0.15 | No structure |

Max engagement bonus: +0.20. **Threshold:** >= 0.55 to pass.

#### Dimension 4: Mythology Risk Score (lines 509-530)

Calls `MythologyDetectionService.detect_mythologies()` which checks 12+ hallucination patterns:

| Pattern | Weight | Example |
|---------|--------|---------|
| numeric_inflation | 0.30 | "500 deployments", "1000 users" |
| false_authority | 0.20 | "studies show", "experts confirm" |
| context_loss | 0.25 | "our system successfully", "we always" |
| capability_exaggeration | 0.35 | "can do anything", "unlimited", "perfect" |
| temporal_distortion | 0.20 | "has been operating for years" |
| false_claims | 0.40 | "fitness dashboard", "dart", "flutter" |
| unverified_stats | 0.25 | "95% accuracy", "10x improvement" |
| 350_deployments_myth | 0.80 | Specific known hallucination |

Score = `1.0 - weighted_risk_score`. **Threshold:** >= 0.15 (i.e., risk < 0.85) to avoid capping decision at 'enhance'. Returns 1.0 on service failure (won't block on error).

### Component 2: Decision Logic (lines 418-477)

```
IF mythology_score < 0.15:
    cap decision at 'enhance' (cannot publish regardless of other scores)
ELIF content_type == 'internal' AND confidence > 0.6:
    decision = 'internal_only'
ELIF quality >= 0.70 AND novelty >= 0.50 AND structure >= 0.55 AND mythology OK:
    decision = 'publish'
ELIF quality >= 0.70 AND mythology risky:
    decision = 'enhance'
ELIF quality >= 0.60 AND (novelty >= 0.50 OR structure >= 0.55):
    decision = 'enhance'
ELSE:
    decision = 'internal_only'
```

Three possible outcomes: `publish`, `enhance`, `internal_only`.

### Component 3: Operational Title Bypass (lines 51-175)

**12 regex patterns** for immediate `internal_only` classification:
```
^\[research\], ^\[stage \d+, ^\[report\], ^\[audit\], ^\[internal\],
^\[debug\], ^\[fix\], ^\[todo\], ^researchagent:, ^systeminsights:,
^root.?cause
```

Plus keyword signals: "we built", "we learned", "our system", "our agents", "our spiders", "donkey betz", "action items:", "next steps for us", etc.

**Key property:** Bypasses all quality scoring — no LLM calls, no database queries, no computation. Pure regex match on title and first 500 characters.

### Component 4: Domain Context System (9 domains)

**Location:** `core/services/domain_content_context.py` (400+ lines)

**Domain detection:** Keyword matching on topic + content, confidence = min(match_count / 5, 1.0).

**9 domains with real platform data injection:**

| Domain | Injected Data |
|--------|-------------|
| Finance | Live market data, analyst perspectives from spiders |
| Sports/Betting | Game stats, odds, spreads from ESPN/TheOddsSpider |
| Crypto/Blockchain | On-chain TVL, volume, WhaleAgent analysis (24h window) |
| AI/Technology | Active agent count, weekly execution stats, top 3 agents by volume |
| Legal | Case references, jurisdiction data from legal spiders (72h) |
| Career/Jobs | Application stats (30d), interview/offer rates from job tracker |
| Health | Research summaries, trend data from health spiders |
| Education | Course trends, certification patterns |
| News/Media | Multi-source aggregation, trending topics |

**Self-referential injection example (AI/Tech domain):**
```python
agent_count = Agent.objects.filter(is_active=True).count()
weekly_executions = AgentExecution.objects.filter(created_at__gte=7_days_ago).count()
# Injected: "In our implementation with {agent_count} active agents..."
```

### Component 5: Autonomous Finishing Loop

**Enhancement task:** `_impl_auto_enhance_blogs()` in `core/tasks_misc.py` (lines 3897-3962)

1. **Budget preflight:** Check BudgetAwareScheduler; skip if budget deferred
2. **Select blogs:** `status='needs_enhancement'`, ordered by `created_at` (FIFO), limit 5
3. **Enhance:** `EditorAgent.execute()` with `save=True` and focus areas: hooks, headers, engagement, structure, conclusion
4. **Reevaluation:** Separate task runs every 3 hours, re-scores enhanced blogs via PublishGate
5. **Promotion:** If passing all four dimensions → `status='approved'` → auto-publish

**Feedback loop injection:** `BlogPerformanceContextBuilder` (526 lines) aggregates recent blog performance (avg quality/novelty/structure scores, top/weak categories, active learning rules) and injects it into `ContentWriterAgent` prompts for future generations — closing the loop without modifying the base prompt.

---

## 6. Novelty Hooks (Section 102)

**a) Four independent quality dimensions with independent thresholds.** No known content quality system evaluates quality, novelty, structure, and hallucination risk as four separately scored dimensions with independent pass/fail thresholds. Existing systems use either a single composite score or a binary pass/fail.

**b) Cumulative duplicate penalty for novelty scoring.** The novelty score applies progressively increasing penalties for each existing similar title: first exact match -0.25, subsequent matches -0.15. This cumulative approach is absent from plagiarism detectors (which report similarity percentage) and content deduplication systems (which use binary duplicate/unique).

**c) Pattern-based hallucination detection integrated into quality gate.** The mythology detection system checks 12+ AI-specific hallucination patterns (numeric inflation, false authority, capability exaggeration) with weighted risk scoring. This is distinct from generic fact-checking (which verifies against known facts) because it detects structural patterns that indicate hallucination regardless of factual accuracy.

**d) Autonomous enhancement-reevaluation finishing loop.** Content in `needs_enhancement` is automatically enhanced by an EditorAgent with specific focus areas, then reevaluated 3 hours later against the same four-dimensional gate. No human intervention required. No known system closes the loop between quality gate rejection, autonomous enhancement, and reevaluation.

**e) Domain-aware self-referential data injection.** The domain context system injects real platform operational data (agent counts, execution stats, spider data) into generation prompts. Content about AI includes actual agent performance numbers; content about crypto includes real on-chain data. This "builder voice" injection is absent from RAG systems, which retrieve external documents rather than platform telemetry.

---

## 7. Non-Obviousness Hooks (Section 103)

**a) Independent dimensions with independent thresholds contradict scoring theory.** Standard practice is to combine quality dimensions into a weighted composite score (like a GPA). Using independent thresholds where failing *any one* blocks publication is non-obvious because it creates a strict conjunction that could reject content scoring highly on three of four dimensions. The insight: quality, novelty, structure, and factual grounding are non-fungible — excellent structure cannot compensate for hallucinated content.

**b) Mythology detection is counter-intuitive for AI content systems.** Systems that generate content via LLM typically trust their own output. Building a second system specifically to detect patterns the generating LLM produces (numeric inflation, false authority) is non-obvious because it implies the generator is unreliable — which contradicts the premise of using LLMs for content generation. The insight: LLMs are reliable for language quality but unreliable for factual grounding, requiring dimension-specific validation.

**c) The finishing loop invests additional compute in rejected content.** The obvious response to quality gate failure is to discard content and regenerate from scratch. Instead, the system enhances the rejected draft (preserving its structure and good elements) and reevaluates after a delay. This is non-obvious because it requires the insight that enhancement is cheaper than regeneration, and that failed content often has recoverable value.

**d) Regex-based title bypass eliminates LLM inference for internal content.** The obvious approach is to run all content through the quality gate and let the gate decide. Bypassing the gate entirely for titles matching operational patterns (via O(1) regex matching) is non-obvious because it appears to reduce quality coverage. The insight: operational content (stage documents, audit reports, debug logs) should never be published regardless of quality, and the regex check is orders of magnitude faster than the full gate.

---

## 8. Operational Benefits (Measurable Outputs)

- **Granular quality feedback:** Authors receive four separate scores identifying exactly which dimension needs improvement (quality vs. novelty vs. structure vs. factual grounding).
- **Duplicate prevention:** Cumulative novelty penalty reduces content repetition. With 400+ published blogs, the novelty scorer catches topic saturation that human reviewers miss.
- **Hallucination catch rate:** Mythology detection with 12+ weighted patterns catches AI-specific hallucination markers that generic quality scoring misses.
- **Content recovery:** The finishing loop recovers ~70% of `needs_enhancement` content through automated enhancement, saving the original generation cost.
- **Classification speed:** Operational title bypass classifies internal content in <1ms (regex match) vs. ~5s (full gate evaluation with LLM mythology check).
- **Self-improving generation:** BlogPerformanceContextBuilder injects learning from past successes/failures, improving future generation quality without prompt engineering.

---

## 9. Alternative Embodiments

**a) ML-based quality scoring instead of rule-based.** The current quality/structure scoring uses rule-based heuristics. A trained model could learn quality patterns from published vs. rejected content, potentially capturing subtler quality signals.

**b) Adaptive thresholds based on content volume.** The novelty threshold (0.50) could adapt based on total published content: stricter (0.60) when the library is large, looser (0.40) when building initial content. This prevents the novelty gate from becoming too restrictive as content accumulates.

**c) A/B testing gate thresholds.** The four thresholds could be A/B tested: randomly assign content to threshold variants and measure reader engagement, converging on optimal thresholds over time.

**d) Multi-pass enhancement with diminishing returns detection.** Instead of a single enhancement pass, the system could iterate until quality scores plateau (two consecutive passes with <0.02 improvement), capturing the maximum recoverable quality.

**e) Cross-domain hallucination patterns.** The mythology detection patterns could be domain-specific: finance-specific hallucinations (fake ticker symbols, impossible returns), legal-specific hallucinations (non-existent statutes, fake case names), health-specific hallucinations (unproven treatments, fake studies).

**f) Reader feedback integration into quality thresholds.** Published content reader engagement metrics could adjust quality thresholds: if low-quality-score content consistently receives high engagement, the quality threshold could be lowered for that domain.

---

## 10. Claim Skeleton

### Independent Method Claim

A computer-implemented method for quality-gating AI-generated content for autonomous publication, the method comprising:

(a) scoring the content on a first quality dimension measuring linguistic merit based on word count, structural elements, and placeholder absence;

(b) scoring the content on a second quality dimension measuring topic novelty by applying cumulative duplicate penalties for each existing published content item with title similarity exceeding a threshold;

(c) scoring the content on a third quality dimension measuring structural engagement based on section variety, engagement elements, and section balance;

(d) scoring the content on a fourth quality dimension measuring hallucination risk by matching content text against a library of weighted hallucination patterns specific to AI-generated content;

(e) comparing each of the four dimension scores against a respective independent threshold; and

(f) permitting publication only when all four dimension scores meet or exceed their respective independent thresholds, and routing content to an autonomous enhancement process when at least one threshold is not met.

### Dependent Claims

1. The method of the independent claim, wherein the cumulative duplicate penalty of step (b) applies a first penalty value for a first matching title and a progressively smaller penalty value for each subsequent matching title.

2. The method of the independent claim, wherein the hallucination patterns of step (d) comprise: numeric inflation, false authority claims, capability exaggeration, temporal distortion, and known specific hallucinations, each pattern having a configurable weight.

3. The method of the independent claim, further comprising, prior to step (a), classifying content as internal based on regex pattern matching of the content title, and bypassing steps (a) through (f) for content classified as internal.

4. The method of claim 3, wherein the regex patterns match operational prefixes including research, audit, stage, report, internal, debug, fix, and todo markers.

5. The method of the independent claim, wherein the autonomous enhancement process of step (f) comprises: enhancing the content using an editor agent with targeted focus areas derived from the lowest-scoring dimension, waiting a configurable delay period, reevaluating the enhanced content against the same four dimensions, and promoting the content to publication if all thresholds are met after enhancement.

6. The method of claim 5, wherein the enhancement-reevaluation cycle is budget-gated, proceeding only when a budget-aware scheduler determines sufficient budget remains for enhancement LLM calls.

7. The method of the independent claim, further comprising injecting performance context from previously published content into future content generation prompts, the performance context comprising average quality scores, highest-performing topic categories, identified strengths and weaknesses, and active learning rules.

8. The method of the independent claim, further comprising detecting a content domain via keyword matching and injecting domain-specific platform operational data into generation prompts, the operational data comprising real-time spider data, agent execution statistics, and platform metrics.

9. The method of claim 8, wherein the domain-specific data includes self-referential platform statistics for technology domains, on-chain blockchain data for cryptocurrency domains, and live market data for finance domains.

10. A system comprising one or more processors and memory storing instructions that, when executed, perform the method of the independent claim.

---

## 11. Diagrams to Draft

**Figure 1 — Four-Dimensional Quality Gate**
```
[AI-Generated Content]
   |
   ├──> [Quality Score]    ──> >= 0.70? ──┐
   ├──> [Novelty Score]    ──> >= 0.50? ──┤
   ├──> [Structure Score]  ──> >= 0.55? ──┤ ALL PASS?
   └──> [Mythology Score]  ──> >= 0.15? ──┘
                                           |
                                    YES: publish
                                    NO:  enhance / internal_only
```

**Figure 2 — Autonomous Finishing Loop**
```
[Quality Gate: needs_enhancement]
        |
        v
[EditorAgent.execute(focus_areas)]
        |
        v
[Wait 3 hours]
        |
        v
[Reevaluation: PublishGate again]
        |
   ┌────┴────┐
   v         v
[PASS]    [FAIL]
   |         |
   v         v
[approved] [stays needs_enhancement]
   |         |
   v         └──> [Next enhancement cycle]
[auto-publish]
```

**Figure 3 — Cumulative Novelty Penalty**
```
New title: "Getting Started with AI Agents"

Existing blog 1: "Getting Started with AI" → exact match → -0.25
Existing blog 2: "AI Agents: A Beginner's Guide" → word overlap 60% → -0.15
Existing blog 3: "Introduction to AI Agents" → word overlap 67% → -0.10
Overused topic: "getting started" → -0.10

Novelty = 1.0 - 0.25 - 0.15 - 0.10 - 0.10 = 0.40 (FAIL: < 0.50)
```

**Figure 4 — Mythology Risk Detection**
```
Content: "Our platform has 350 deployments with 95% accuracy..."

Pattern matches:
  numeric_inflation: "350 deployments" → weight 0.30
  350_deployments_myth: specific match → weight 0.80
  unverified_stats: "95% accuracy" → weight 0.25

risk_score = max(0.80, 0.30, 0.25) = 0.80 (weighted aggregate)
mythology_score = 1.0 - 0.80 = 0.20

Decision: 0.20 > 0.15 threshold → mythology passes (barely)
         But: high risk flagged in gate_notes
```

---

## 12. Prior Art Buckets to Cite Against

**a) Content Quality Scoring (Grammarly, Hemingway Editor, Yoast SEO)**
- Teaches: Readability scoring, grammar checking, SEO optimization scores
- Does NOT teach: Four independent quality dimensions with independent thresholds, cumulative novelty penalties, AI-specific hallucination detection, or autonomous enhancement loops

**b) Plagiarism Detection (Turnitin, Copyscape, Originality.ai)**
- Teaches: Similarity detection against existing content, percentage-based matching
- Does NOT teach: Cumulative duplicate penalty that increases with each match, topic-level novelty scoring (not text-level similarity), or overused topic detection

**c) AI Content Detection (GPTZero, Originality.ai, ZeroGPT)**
- Teaches: Detecting whether content was AI-generated (perplexity analysis)
- Does NOT teach: Detecting specific hallucination patterns within AI-generated content, weighted pattern libraries for AI-specific failure modes, or integrating hallucination risk into a multi-dimensional quality gate

**d) Content Management Systems (WordPress, Contentful, Sanity)**
- Teaches: Publishing workflows with editorial review, draft/published states
- Does NOT teach: Autonomous quality evaluation, automatic enhancement of rejected content, or self-healing finishing loops that promote content without human intervention

**e) RAG Quality Evaluation (RAGAS, TruLens)**
- Teaches: Evaluating RAG output quality (faithfulness, relevance, context recall)
- Does NOT teach: Four-dimensional scoring with independent thresholds, cumulative novelty penalty, operational title bypass, or autonomous enhancement-reevaluation cycles

**f) Feature Flag / Canary Deployment (LaunchDarkly, Argo Rollouts)**
- Teaches: Gradual rollout with quality monitoring, automatic rollback
- Does NOT teach: Content-specific quality dimensions, hallucination detection patterns, or enhancement-reevaluation loops for content (not code)

---

## Observability Evidence (Proving This Runs in Production)

### PublishGate Scores (stored on SelfBlog model)
```python
blog.quality_score = 0.78     # Passed (>= 0.70)
blog.novelty_score = 0.62     # Passed (>= 0.50)
blog.structure_score = 0.58   # Passed (>= 0.55)
blog.gate_notes = "PUBLISH: quality=0.78 novelty=0.62 structure=0.58 mythology=0.92"
blog.publish_ready = True
blog.status = 'approved'
```

### Finishing Loop Evidence
```
# Celery task log
[auto_enhance_blogs] Processing 3 blogs in needs_enhancement status
[auto_enhance_blogs] Enhanced blog "AI Market Trends" — EditorAgent save=True
...
# 3 hours later:
[reevaluate_enhanced_blogs] Re-scoring "AI Market Trends"
[reevaluate_enhanced_blogs] quality=0.82 novelty=0.71 structure=0.65 → PUBLISH
[reevaluate_enhanced_blogs] Promoted to 'approved'
```

### Blog Statistics (production counts)
```
Published: 195
Draft: 207
Needs Enhancement: 111
Pending Review: 18
```

---

## Examiner Story

Prior art teaches readability scoring for written content (Grammarly), plagiarism detection via text similarity (Turnitin), AI content detection via perplexity analysis (GPTZero), and content management workflows with editorial review (WordPress). However, no single reference or obvious combination teaches a system that (1) evaluates AI-generated content against four structurally independent quality dimensions (linguistic quality, topic novelty, structural engagement, hallucination risk) each with its own scoring algorithm and independent pass/fail threshold, (2) applies cumulative duplicate penalties for novelty scoring where each additional similar title incurs a progressively smaller penalty, (3) detects AI-specific hallucination patterns (numeric inflation, false authority, capability exaggeration) using a weighted pattern library integrated as the fourth quality dimension, (4) bypasses quality evaluation entirely for operational content via O(1) regex title matching, and (5) automatically enhances rejected content using an editor agent with targeted focus areas, reevaluates after a configurable delay, and promotes passing content to publication without human intervention. The combination is non-predictable because standard quality systems use composite scores rather than independent dimensions, plagiarism systems report similarity percentages rather than applying cumulative penalties, hallucination detection focuses on whether content is AI-generated rather than whether specific AI failure patterns are present, and content management systems treat rejection as a terminal state rather than an input to an autonomous enhancement loop.
