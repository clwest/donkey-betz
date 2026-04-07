# Dossier #4: Content Pipeline

**Audited:** April 6, 2026
**Status:** WORKING — full pipeline operational, token-conservation mode limits scheduled runs

---

## 1. Purpose

The Content Pipeline transforms raw spider intelligence into published, quality-gated content through a multi-stage deliberation process: claims assembly from real sources, AI draft generation, multi-reviewer critique, editorial debate, automated quality scoring, and structured publishing gates. This is the platform's primary value-creation engine.

## 2. Runtime Evidence

- **118 SelfBlog records** on production (5 published, 85 draft, 25 pending_review, 1 approved)
- **DeliberationSession** records track every review conversation
- **ClaimsPack** records link published content to source spider data
- **PublishGate** scores (quality, novelty, structure) stored on each blog
- **537 Deliverables** across 33 workspaces
- **5 ContentChannels** with episode tracking

## 3. Entry Points

| Trigger | Task | What Happens |
|---------|------|--------------|
| Celery Beat | `generate_self_blog_deliberation_task` | Full v2 deliberation pipeline (disabled for token conservation) |
| Celery Beat | `generate_self_blog_task` | Simpler v1 direct generation (disabled) |
| PA tool | `generate_blog` action | On-demand blog generation via Rigby |
| API | `POST /api/v1/research/self-blog/generate-v2/` | Direct API trigger |
| Django signal | `post_save(SelfBlog)` on publish | Triggers ConceptForge if quality >= 0.80 |

## 4. Execution Chain — The v2 Deliberation Pipeline

This is the primary content creation path and the most patent-relevant:

```
STAGE 1: CLAIMS ASSEMBLY
  core/services/claims_pack_builder.py:54-108
  │
  ├─ Source 1: SpiderData (last 72h)
  │   → Query recent spider records
  │   → Extract items from raw_data
  │   → Classify: 'factual' (confidence 0.7) vs 'speculative' (0.3)
  │
  ├─ Source 2: SignalCluster (active patterns)
  │   → Query active signal clusters
  │   → Extract sample_signals
  │   → All marked 'speculative' (confidence 0.4)
  │
  └─ Source 3: User Documents (RAG semantic search)
      → Generate query embedding
      → Cosine similarity search (min 0.4)
      → Marked 'factual' (confidence 0.8)
  │
  Output: ClaimsPack {claims[], sources[], stats{}}

STAGE 2: AI DRAFT GENERATION
  core/services/content_deliberation_runner.py:178-221
  │
  → ContentWriterAgent.execute()
  → Task: "Write a blog post about: {topic}"
  → Context includes claims as research block
  → Operational telemetry injected (Session 1001)
  │
  Output: (full_text, generated_content{title, sections, intro, conclusion})

STAGE 3: MULTI-REVIEWER CRITIQUE
  core/services/content_review_panel_v2.py:208-256
  │
  ├─ Reviewer 1: Skeptic (always)
  │   → Checks: missing citations, generic content, hallucination risk
  │   → Output: {verdict, top_issues, required_changes, confidence}
  │
  ├─ Reviewer 2: FactChecker (always)
  │   → Validates claim IDs map to real URLs
  │   → Flags unsourced assertions, stale claims (>48h)
  │
  └─ Reviewer 3: DomainPersona (conditional)
      → Only if domain != 'general' and confidence >= 0.2
      → Domain-specific expertise check
  │
  Output: review_results[] with per-reviewer verdicts

STAGE 4: EDITORIAL DEBATE
  core/conversation_orchestrator.py:902-1540
  │
  → Creates DeliberationSession
  → EditorAgent (advocate) vs ContentStrategyAgent (critic)
  → 4 turns of structured debate
  → Produces ExecutionMandate with chosen_path
  │
  Output: mandate_dict{chosen_path: PUBLISH|REVISE|KILL}

STAGE 5: DECISION + CONDITIONAL REWRITE
  core/services/content_deliberation_runner.py:266-334
  │
  → Extract decision from mandate (fallback: reviewer consensus)
  → If PUBLISH + 0 claims → downgrade to REVISE (no publish without evidence)
  → If REVISE → _rewrite_draft() with reviewer feedback incorporated
  │
  Output: final (draft_text, decision)

STAGE 6: PUBLISH GATE (quality scoring)
  core/services/publish_gate.py:27-606
  │
  ├─ Quality Score (threshold >= 0.70)
  │   Word count 300-1500 (+0.15), has intro (+0.10),
  │   has conclusion (+0.10), 3+ sections (+0.10)
  │
  ├─ Novelty Score (threshold >= 0.60)
  │   Checked against ALL existing published blogs
  │   Exact match: -0.25, high overlap (>50%): -0.15
  │
  ├─ Structure Score (threshold >= 0.55)
  │   Section variety, engagement elements, balance
  │
  └─ Mythology Score (threshold >= 0.15)
      MythologyDetectionService scans for unrealistic claims
  │
  Decision: PUBLISH (all pass) | ENHANCE (partial) | INTERNAL_ONLY (fail)

STAGE 7: SAVE + CLASSIFY
  core/services/content_deliberation_runner.py:349-420
  │
  → Create SelfBlog with full traceability:
    - deliberation session_id
    - claims_count, sources_count
    - reviewer names and verdicts
    - quality/novelty/structure scores
  → Status: published | needs_enhancement | draft | killed
  → Content type: public | internal | strategic
```

## 5. Data Contracts

| Model | File | Purpose |
|-------|------|---------|
| SelfBlog | `core/models_unified_system.py` | Published content with quality scores, traceability |
| DeliberationSession | `core/models_deliberation.py` | Review conversation records |
| ClaimsPack | In-memory (not persisted separately) | Assembled claims for a pipeline run |
| Deliverable | `core/models_deliverables.py` | Agent output envelope with workspace linkage |
| ContentPacket | `core/models_deliverables.py` | Groups deliverables from a single pipeline run |
| ContentPacketItem | `core/models_deliverables.py` | Links deliverable to packet with role (brief/draft/rewrite/etc.) |
| ContentChannel | `core/models_autonomous_studio.py` | Autonomous content series with scheduling |
| ChannelEpisode | `core/models_autonomous_studio.py` | Individual episode with performance metrics |

### SelfBlog Status Flow
```
draft → pending_review → needs_enhancement → approved → published
                                    ↑                       │
                                    └── (enhance cycle) ────┘
              killed (terminal)
```

### Deliverable Types
document, image, video, audio, code, analysis, report, template, research, strategy, plan, script

### ContentPacketItem Roles
brief, research, strategy, draft, edit_review, fact_check, rewrite, seo, distribution, other

## 6. External Dependencies

| Dependency | Used By | Purpose |
|------------|---------|---------|
| OpenAI GPT-5-mini | ContentWriterAgent, reviewers, editorial debate | Draft generation, critique, rewriting |
| OpenAI text-embedding-3-small | ClaimsPack RAG search | Document similarity for claims |
| SpiderData (internal) | ClaimsPack builder | Real-world evidence for claims |
| SignalCluster (internal) | ClaimsPack builder | Pattern-level evidence |

## 7. Outputs/Artifacts

| Output | Where Users See It | Format |
|--------|-------------------|--------|
| Published blogs | Build > Content Studio > Blogs | Markdown with sections |
| Draft blogs | Build > Content Studio > Blogs (filtered) | Same format, pending review |
| Deliverables | Work > Deliverables | Workspace-scoped library |
| Content Packets | Work > Deliverables (grouped) | Multi-deliverable bundles |
| Channel episodes | Build > Content Studio > Channels | Episode cards with performance |
| Newsletter issues | External (Substack manual paste) | HTML + metadata + checklist |

## 8. Failure Modes

| Failure | Cause | Impact | Mitigation |
|---------|-------|--------|------------|
| Empty ClaimsPack | No recent spider data | Blog published without evidence | Decision enforcer: PUBLISH + 0 claims → REVISE |
| Reviewer timeout | LLM API slow on critique | Partial review, may publish unchecked | Soft time limit 480s, fallback to reviewer consensus |
| Novelty gate blocks | Too similar to existing blog | Content stuck in needs_enhancement | Novelty threshold lowered to 0.60 (Session 1004) |
| Mythology false positive | AI content triggers myth detector | Good content blocked | Threshold lowered to 0.15 (Session 1003) |
| Concurrent deliberation | Two runs overlap | Duplicate blogs | Redis lock `deliberation_blog_running` (Session 1062) |
| Topic starvation | No trending spider data | Pipeline uses fallback topics | 10 hardcoded fallback topics (Session 969) |

## 9. Current Status: WORKING (On-Demand)

**What works:**
- Full v2 deliberation pipeline (claims → draft → review → gate → publish)
- PublishGate quality scoring with 4 dimensions
- Multi-reviewer critique (Skeptic + FactChecker + DomainPersona)
- Editorial debate via ConversationOrchestrator
- Deliverable creation with dedup guards
- Content Packets for grouping pipeline outputs
- Newsletter publisher (Substack manual provider)

**What's disabled (token conservation):**
- Scheduled blog generation (both v1 and v2)
- Content channel auto-episode creation
- Content research agent rotations

**What's partially working:**
- Newsletter pipeline: Publisher exists but manual paste required (no API integration)
- Content Packets: Model exists but UI shows flat list (packet detail page not built)
- Channel episodes: Model exists but no scheduled generation

## Verified Data (April 6, 2026)

- **1,260 total blogs**: 1,227 draft, 25 pending_review, 5 published, 2 needs_enhancement, 1 approved
- **6 deliberation sessions** recorded
- **5 published blogs** all have quality scores >= 0.7
- **Pipeline throughput**: Very low — only 5 blogs made it to published status
- **Deliberation sessions**: 6 total, all status=completed (100% completion rate)
- **Pipeline is functional but underused** — only 6 runs ever, all succeeded

## 10. Truth Gaps

- **End-to-end success rate**: How many pipeline runs produce PUBLISH vs REVISE vs KILL? No aggregate stats
- **Claims quality**: ClaimsPack assembles claims but no validation that claims are actually relevant to the topic
- **Reviewer agreement**: Do the 3 reviewers typically agree? No cross-reviewer analysis
- **Rewrite effectiveness**: When REVISE triggers a rewrite, does the rewritten version pass the gate? No tracking
- **PublishGate calibration**: Thresholds were adjusted multiple times — are current values optimal?
- **Newsletter delivery**: SubstackManualProvider prepares content but no tracking of actual sends/opens
- **Content Packet adoption**: ContentPacket model exists but unclear if pipeline actually creates packets or just individual deliverables
- **Channel performance feedback**: ChannelEpisode tracks views/likes but unclear if this feeds back to improve future episodes
- **Cost per published blog**: Full pipeline (claims + draft + 3 reviews + debate + rewrite) is expensive — cost not tracked per pipeline run
