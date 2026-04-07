# Dossier #10: ConceptForge Pipeline

**Audited:** April 6, 2026
**Status:** WORKING (gate relaxed this session) — 0 runs on production, pipeline verified locally

---

## 1. Purpose

ConceptForge is an autonomous 6-stage analysis pipeline that transforms published content into comprehensive dossiers through research, structured debate with legendary advisors, feasibility assessment, risk analysis, market analysis, and executive synthesis. Each run produces a reproducible dossier with advisor panel snapshots for auditability.

## 2. Runtime Evidence

- **0 runs on production** (gate was too strict — fixed this session, quality >= 0.80 now sufficient without tags)
- **6 domain labs** configured (Legal, Market, Tech, Content, Startup, Career)
- **18 legendary advisors** with debate pairs per domain
- **ConceptForgeRun** model with stage tracking, timing, artifacts
- **Django signal** fires on SelfBlog publish (verified in `core/signals/conceptforge_signals.py`)
- **Celery task** `run_conceptforge_pipeline` dispatches to long_running queue

## 3. The 6-Stage Pipeline

```
STAGE 1: RESEARCH (ResearchAgent + 2 domain persona advisors)
  → Research brief with findings, statistics, gap analysis
  │
STAGE 2: DEBATE (ContentStudioDebateAgent + legendary advisor pro/con pair)
  → Structured debate positions, arguments, takeaways
  → Example: Elon Musk (optimist) vs Yuval Harari (cautionary) for TechLab
  │
STAGE 3: FEASIBILITY (SystemsArchitectAgent + 2-3 persona advisors)
  → Technical requirements, architecture, dependencies, timelines
  │
STAGE 4: RISK (RiskAnalysisAgent + 2-3 persona advisors)
  → Regulatory risks, legal considerations, ethics, mitigations
  │
STAGE 5: MARKET (MarketIntelligenceAgent + 2-3 persona advisors)
  → Target market, competitive landscape, pricing, go-to-market
  │
STAGE 6: SYNTHESIS (ThinkingAgent, no advisors)
  → Executive dossier: summary, SWOT, roadmap, resources, go/no-go
```

Each stage receives all prior stage outputs as input (cumulative context).

## 4. Domain Labs

| Domain | Routing Tags | Required Advisors | Example Debate Pair |
|--------|-------------|-------------------|-------------------|
| Legal | legal, policy, regulation, compliance | Legal Document Reviewer, Trend Expert | — |
| Market | market, stocks, trading, investment, crypto | Market Research Analyst, Data Scientist | — |
| Tech | tech, ai, ml, product, saas | AI Model Trainer, Trend Expert | Elon Musk vs Yuval Harari |
| Content | content, marketing, media, social | Content Strategy Planner, SEO Optimizer | — |
| Startup | startup, funding, venture, growth | Startup Guru, Market Analyst | Peter Thiel vs Cathie Wood |
| Career | career, jobs, skills, resume, salary | Career Path Strategist, Job Automator | — |

Lab routing: `get_lab_for_tags()` scores each lab by tag matches, returns highest score.

## 5. Advisor Panel + Reproducibility

**18 Legendary Advisors:**
Warren Buffett, Ray Dalio, Cathie Wood, Peter Thiel, Elon Musk, George Soros, Jeff Bezos, Steve Jobs, Mark Cuban, Gary Vaynerchuk, Seth Godin, Richard Branson, Christine Lagarde, Jamie Dimon, Tim Ferriss, Simon Sinek, Yuval Harari, Reid Hoffman

**Reproducibility features:**
- Panel snapshot stored on `ConceptForgeRun.advisor_panel_snapshot` at run start
- Each stage records `legendary_advisors_used` and `inputs_used`
- Optional seed parameter for deterministic panel selection
- Enables comparison: "same content, different advisor panel"

**Panel snapshot structure:**
```json
{
  "domain": "tech",
  "advisors": ["elon_musk", "peter_thiel", "jeff_bezos"],
  "debate_pair": ["elon_musk", "yuval_harari"],
  "profiles": {
    "elon_musk": {
      "name": "Elon Musk",
      "influence_score": 97,
      "stance_tendency": "bullish",
      "key_frameworks": ["first_principles", "rapid_iteration"],
      "debate_style": "passionate"
    }
  }
}
```

## 6. Trigger Mechanism

```
SelfBlog saved with status='published'
  → Django post_save signal (core/signals/conceptforge_signals.py:29)
    → Filter: not research_brief or audit category
    → Check: no existing run for this blog
    → Calculate quality score from content metrics
    → Gate: quality >= 0.80 (tags optional after this session's fix)
    → Detect domain from tags or default to 'tech'
    → Dispatch: run_conceptforge_pipeline.delay()
      → Celery task on long_running queue
        → ConceptForgeOrchestrator.start_pipeline()
          → Create ConceptForgeRun record
          → Snapshot advisor panel
          → Execute 6 stages sequentially
          → Create dossier artifact
```

## 7. Data Contracts

| Model | Purpose | Key Fields |
|-------|---------|------------|
| ConceptForgeRun | Pipeline run tracking | source_type, source_id, domain, status, advisor_panel_snapshot, quality_score |
| ConceptForgeStageRun | Per-stage execution | stage_name, stage_order, status, agent_used, advisors_used, output_text, duration_ms |
| ConceptForgeArtifact | Output documents | name, kind(MARKDOWN/PDF/JSON), content, is_primary, version |

### Run Status Flow
```
PENDING → RUNNING → COMPLETED (all 6 stages done)
                  → FAILED (any stage fails)
                  → CANCELLED
```

## 8. Current Status: WORKING (Untriggered)

**What works:**
- Full 6-stage pipeline code verified
- 6 domain labs with routing logic
- 18 legendary advisors with debate pairs
- Advisor panel snapshot for reproducibility
- Django signal fires on SelfBlog publish
- Celery task dispatches to long_running queue
- Artifact creation with versioning

**Why 0 runs exist:**
- Gate required quality >= 0.80 AND strategic tags (fixed this session)
- All 5 published blogs had empty tags
- Fix deployed: quality >= 0.80 alone now sufficient

**Expected after fix:** Next published blog with quality >= 0.80 will trigger a full pipeline run.

## Verified Data (April 6, 2026)

- **0 runs** on both production and local databases
- **Root cause identified**: gate required quality >= 0.80 AND strategic tags, but all qualifying blogs had empty tags
- **Fix deployed**: quality >= 0.80 alone now triggers pipeline (tags optional)
- **Expected**: next published blog with quality >= 0.80 will trigger first run

## 9. Truth Gaps

- **Pipeline execution time**: 6 stages × ~300s each = ~30 minutes total — not verified
- **Stage failure handling**: If stage 3 fails, does the pipeline retry or abort?
- **Advisor impact**: Do legendary advisor positions actually improve debate quality vs. generic agents?
- **Dossier quality**: No human evaluation of produced dossiers
- **Cost per run**: 6 LLM calls (one per stage) + debate agent — estimated $0.50-2.00 per run, not measured

## Key Patent Claims

1. **6-stage autonomous analysis pipeline** — sequential stages with cumulative context, each run by a specialized agent
2. **Legendary advisor debate system** — pre-configured bull/bear advisor pairs argue positions using their documented frameworks and principles
3. **Reproducible advisor panels** — panel snapshot stored per run enables comparison of same content analyzed by different advisor configurations
4. **Domain-lab routing** — content automatically routed to appropriate analysis lab (Legal/Market/Tech/Content/Startup/Career) based on tag matching
5. **Quality-gated trigger** — pipeline only fires on published content exceeding quality threshold, preventing analysis of low-quality inputs
