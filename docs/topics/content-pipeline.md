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

Generates draft with mandatory `[C-xxxxxxxxxx]` citations. The agent's system prompt includes:
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
| stats_snapshot | JSON | Includes `{deliberation: {session_id, decision, claims_count, sources_count, reviewers, review_verdicts}}` |

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
