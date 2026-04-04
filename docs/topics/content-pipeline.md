# Content Pipeline

The content pipeline transforms spider data into published blogs through a multi-agent deliberation process with claims-based citation, 3-reviewer panels, and quality gating.

## Pipeline Overview

```
SpiderData (72h) + SignalClusters (active)
  → ClaimsPack (deterministic claim IDs)
    → ContentWriterAgent (draft citing [C-xxxxxxxxxx])
      → 3-Reviewer Panel (Skeptic + FactCheck + DomainPersona)
        → DecisionEnforcer (PUBLISH / REVISE / KILL)
          → Rewrite pass (if REVISE)
            → PublishGate (quality/novelty/structure scoring)
              → SelfBlog (with stats_snapshot['deliberation'])
```

## ClaimsPack (Step 1)

`ClaimsPackBuilder` assembles evidence from recent data:
- **SpiderData (72h):** Items with description → factual claims (0.7 confidence). Title-only → speculative (0.3).
- **SignalClusters (active):** Sample signals → analytical claims (0.4 confidence).
- **Deduplication:** By normalized URL.
- **Cap:** Max 20 claims, sorted by freshness.

Each claim gets a deterministic ID: `C-{sha256(normalize_url(url) + title)[:10]}`. This enables citation tracking — every factual assertion in the blog traces back to a specific spider source with URL and timestamp.

## ContentWriterAgent (Step 2)

Generates draft with mandatory `[C-xxxxxxxxxx]` citations.

### Three Prompt Construction Methods

ContentWriterAgent has its OWN prompt-building system, separate from `BaseAgent._build_intelligent_prompt()`:

| Method | Type | Location | Purpose |
|--------|------|----------|---------|
| `_build_intelligent_system_prompt()` | System prompt | line ~280 | Evidence injection, platform summary, spider intelligence, domain context, performance feedback, temporal awareness |
| `_build_content_prompt()` | User prompt | line ~1321 | Content type instructions, research data, citation requirements, tone/audience/word count |
| `generate_flagship_injection()` | User prompt append | line ~851 | Distinctive voice injection from agent recoveries, dreams, learnings — skipped when evidence-first mode active |

**Important:** `BaseAgent._build_intelligent_prompt()` is used by most agents but NOT by ContentWriterAgent for content generation. ContentWriterAgent calls its own `_build_intelligent_system_prompt()` instead. Evidence injected into BaseAgent's method will NOT reach ContentWriterAgent.

### Spider Data Injection (4 Paths)

Spider URLs and data enter ContentWriterAgent through 4 separate paths:

1. **`_format_spider_intelligence()`** (line ~558) — formats `spider_context` dict into citable markdown (trends, discussions, articles, market data). Injected into system prompt.
2. **`BlogPerformanceContextBuilder`** — injects past blog performance metrics including blog URLs. Via enrichment pipeline.
3. **`get_domain_content_context()`** (line ~484) — injects domain-specific spider data (finance, sports, crypto, etc.). **Skipped when evidence exists** (Session 1103).
4. **`generate_flagship_injection()`** (line ~851) — injects spider-based content for distinctive voice. **Skipped when evidence-first mode active** (Session 1103).

Session 1103 added evidence-first suppression for paths 1 (via `_evidence_context_override`), 3, and 4. Path 2 (blog performance) can still surface spider URLs.

### System Prompt Includes
- **Evidence override** (Session 1103): Research evidence injected at top, overrides all other context
- **Performance feedback** (Session 886): Recent quality scores, strengths/weaknesses, learning rules
- **Domain context** (Session 891): Finance/sports/crypto/AI-specific platform data from 9 domains
- **User preferences** and platform capabilities

## 3-Reviewer Panel (Step 3)

Three specialized reviewers evaluate the draft:

| Reviewer | Mission | Always Runs |
|----------|---------|-------------|
| **SkepticReviewer** | Find uncited claims, generic filler, hallucination risk, logical leaps | Yes |
| **FactCheckReviewer** | Verify every `[C-xxxxxxxxxx]` maps to a real URL, check freshness (<48h) | Yes |
| **DomainPersonaReviewer** | Domain accuracy, correct terminology, actionable recommendations | Only if domain detected (confidence >= 0.2) |

Each returns structured JSON: `{reviewer, verdict (PASS/REVISE/FAIL), top_issues, required_changes, suggested_edits, confidence}`.

**Failure handling:** Invalid reviewer output → synthetic FAIL verdict (never skipped). LLM exceptions → same synthetic FAIL. This ensures the DecisionEnforcer always sees issues.

**LLM Provider (Session 988):** Reviewers use `core.services.llm_provider_registry` (`get_llm_provider_registry()` → `registry.complete(provider='openai', model_id='gpt-4.1-mini', request=LLMRequest(...))`). Do NOT use `core.llm_providers` (doesn't exist).

## DecisionEnforcer (Step 4)

The "Prefrontal Cortex" — forces a decision after review. Checks `ExecutionMandate.chosen_path` for PUBLISH/REVISE/KILL. Fallback: all PASS → PUBLISH, any FAIL → REVISE. Default: REVISE.

Forbidden phrases: "Further analysis recommended", "More research needed". Must output: chosen_path, reason, kill_criteria, deadline, rejected_paths, acknowledged_risks.

## Rewrite Pass (Step 5)

If decision is REVISE, ContentWriterAgent receives top 3 `required_changes` from each reviewer and rewrites once with the same ClaimsPack context preserved.

## PublishGate (Step 6)

Three quality dimensions with thresholds:

| Dimension | Threshold | Signals |
|-----------|-----------|---------|
| **Quality** | >= 0.75 | Word count 500-1500, has intro/conclusion, 3+ sections, no placeholders |
| **Novelty** | >= 0.60 | Title similarity vs existing blogs, word overlap check, overused topic detection |
| **Structure** | >= 0.55 | Section variety, engagement patterns (stats/quotes), section balance |

**Operational title bypass:** Titles starting with `[Research]`, `[Stage N]`, `[Audit]`, `[Internal]` → auto-classified as `internal_only`, skip quality checks.

**Content type classification:** Internal signals ("we built", "our system", technical density) vs public signals ("you should", "how to guide"). Internal score > 1.5x public → internal.

**Final gate decision:** `publish` (all pass), `enhance` (partial pass), `internal_only` (low quality or internal).

**Status promotion (Session 1000C):** `apply_to_blog()` now sets `blog.status = 'approved'` on `publish` decision (previously only set `publish_ready=True` without changing status).

## Blog Quality Fields (SelfBlog Model)

| Field | Type | Description |
|-------|------|-------------|
| quality_score | Float 0-1 | PublishGate quality dimension |
| novelty_score | Float 0-1 | PublishGate novelty dimension |
| structure_score | Float 0-1 | PublishGate structure dimension |
| publish_ready | Boolean | True if all thresholds passed |
| gate_notes | Text | PublishGate decision reasoning |
| content_type | Char | public / internal / strategic |
| status | Char | draft / pending_review / approved / published / needs_enhancement |
| stats_snapshot | JSON | Includes `{deliberation: {session_id, decision, claims_count, sources_count, reviewers, review_verdicts}, enhancement_count: N}` |

## Content Feedback Loop (Session 886)

`BlogPerformanceContextBuilder` injects past performance into future content generation:
- **Metrics:** Average quality/novelty/structure scores from last 10 blogs
- **Strengths/Weaknesses:** Auto-detected (e.g., "Good source attribution" or "Content feels generic")
- **Learning Rules:** Active `PipelineLearningInsight` entries (e.g., "PREFER: Long-form content 1200+ words")
- **Top/Weak Topics:** Grouped by category with sample sizes

This creates a feedback loop where the agent learns from its own past performance.

### PA-to-Agent Content Feedback (Session 990)

When the PA publishes, archives, or revises agent-created content, that decision is now recorded back to the originating agent:

1. **AgentMemory** (`memory_type='feedback'`, `tags=['pa_review']`) — valence mapped from action (publish→positive, archive→negative, revise→neutral). Surfaced to agents via `_get_agent_knowledge()` in multi-agent conversations.
2. **UserAgentLearning** — `record_success()` on publish, `record_failure()` on archive, per-user personalization.
3. **FeedbackLoopEngine** — `get_feedback_for_agent()` queries recent PA reviews → `pa_review_feedback` and `pa_review_summary` added to feedback context.
4. **Agent Router** — `gather_context()` extracts `pa_content_feedback` and `pa_review_summary` into `spider_context`, making PA decisions a first-class context field for every agent execution.

Data flow: `PA action → _record_content_feedback() → AgentMemory + UserAgentLearning → FeedbackLoopEngine → agent_router.gather_context() → spider_context`.

## Domain Content Context (Session 891)

9 domains auto-detected by keyword matching. Each injects real platform data:

| Domain | Example Context |
|--------|----------------|
| Finance | Spider price movements, analyst perspectives |
| Crypto | On-chain analysis from WhaleWatcher, DeFi trends |
| Sports | Live odds, game results, stats |
| AI/Tech | Active agent counts, execution patterns ("In our implementation...") |
| Legal | Case law from spider data, jurisdiction info |
| Career | Job application success rates from JobApplication model |

Max 2 domains per content piece. Gives content the "builder voice" — writing from direct experience.

## v1/v2 Coexistence

- **v1:** `content_review_panel.py` — original panel, still accessible, untouched
- **v2:** `content_review_panel_v2.py` + `ContentDeliberationRunner` — claims-based, structured validation
- Different entry points for A/B testing. v2 via `POST /api/v1/research/self-blog/generate-v2/`

## Content Review Automation (Session 1000C, updated Session 1033)

Scheduled tasks that move blogs through the pipeline without manual intervention:

| Task | Schedule | Queue | Action |
|------|----------|-------|--------|
| `evaluate_unscored_blogs` | Every 2h at :10 | content | Score draft blogs through PublishGate |
| `auto_enhance_blogs` | Every 4h at :45 | content | EditorAgent enhances oldest `needs_enhancement` blogs (limit 5, `save=True`) |
| `enhance_all_blogs_needing_enhancement` | Every 6h at :40 | long_running | EditorAgent improves needs_enhancement blogs (limit 5, max 3 rounds) |
| `reevaluate_enhanced_blogs` | Every 6h at :10 | content | Re-score enhanced blogs through PublishGate |
| `auto_publish_approved_blogs` | Daily 6 AM | content | Move approved+publish_ready blogs to published |

**Enhancement guard:** `stats_snapshot['enhancement_count']` tracks rounds per blog. After 3 unsuccessful rounds, the blog is skipped to prevent infinite loops.

### Content Finishing Loop (Session 1033)

Before Session 1033, blogs that reached `needs_enhancement` had no automatic path forward — EditorAgent existed but was never auto-triggered. 116 blogs were stuck.

**Complete pipeline now:**
```
draft → evaluate_unscored_blogs → needs_enhancement
  → auto_enhance_blogs (EditorAgent with save=True)
    → pending_review → reevaluate_enhanced_blogs (PublishGate re-scores)
      → approved → auto_publish_approved_blogs → published
```

**`auto_enhance_blogs` task** (`core/tasks.py`):
- Finds oldest `needs_enhancement` blogs, limit 5 per run
- Runs `EditorAgent.execute()` with `save=True` — enhanced content saved directly to SelfBlog
- Blog status moves to `pending_review` after enhancement
- Each enhancement takes ~18s via OpenAI (EditorAgent still uses gpt-4o-mini — candidate for upgrade)

**EditorAgent LLM fix (PR #1308):** EditorAgent's `_enhance_with_llm()` imported from nonexistent `core.services.llm_service`. Fixed to use `LLMProviderRegistry` + `LLMRequest` from `core.services.llm_provider_registry`.

**Production results (first run):** 6 blogs enhanced successfully (5/5 + 1 earlier test). All moved from `needs_enhancement` → `pending_review`. Blog status snapshot post-Session 1033: 207 draft, 195 published, 111 needs_enhancement, 18 pending_review.

## Deliverable Quality Scoring (Session 1033)

Prior to Session 1033, all 4,380 deliverables had a hardcoded default `quality_score` of 0.7 — no differentiation between good and bad output.

**`score_unscored_deliverables` task** (`core/tasks.py`):
- Runs every 6h at :15 on `default` queue
- Finds deliverables with `quality_score=0.7` (the default), processes 50 per batch
- Heuristic scoring via `_calculate_deliverable_quality()`:

| Factor | Score Contribution |
|--------|-------------------|
| Base | 0.45 |
| Word count >= 200 | +0.08 |
| Word count >= 500 | +0.07 |
| Word count >= 1000 | +0.05 |
| Word count > 5000 | -0.05 (too verbose) |
| Has headers (`##`, `**`) | +0.05 |
| Has lists (`- `, `* `, `1.`) | +0.05 |
| Has URLs | +0.05 |
| Agent confidence > 0.8 | +0.10 |
| Agent confidence > 0.6 | +0.05 |
| Word count < 50 | -0.20 (stub content) |

**Range:** 0.1 to 1.0. **Production results:** 884 deliverables scored in first batch, distribution 0.30–0.75.

## Operational Telemetry Grounding (Session 1001)

Blog generation now injects real operational data so ContentWriterAgent cites verifiable metrics instead of fabricating claims.

**`_build_operational_context()`** (in `core/tasks.py`) queries 4 telemetry models and returns a markdown block:

| Section | Model | Import Path | Data |
|---------|-------|-------------|------|
| Agent Executions (72h) | `AgentExecution` | `core.models` | Total/completed/failed, success rate, avg execution time, 3 recent executions |
| Background Tasks (72h) | `CeleryTaskEvent` | `core.models_celery_telemetry` | Total/success/failure, reliability %, avg duration, top 3 failing tasks |
| System Health | `HeartBeat` | `core.models_heart` | Latest score, status, component counts |
| Recent Decisions | `AgentDecisionSummary` | `core.models_unified_system` | 3 recent with topic, stance, insights, participants |

Each section in its own try/except -- graceful degradation if any model is unavailable.

**Injection points:**
- **Pipeline 1** (`generate_self_blog_task`): Appended to `blog_research` after all topic-category assembly
- **Pipeline 2** (`ContentDeliberationRunner._generate_draft()`): Appended to `research` after ClaimsPack

**Prompt changes:** All "add your own insights" / "expand with your perspective" language replaced with "Ground all claims in the data provided" / "cite these, do not invent". ContentWriterAgent's `## IMPORTANT` section now explicitly forbids fabricating operational metrics or incidents.
