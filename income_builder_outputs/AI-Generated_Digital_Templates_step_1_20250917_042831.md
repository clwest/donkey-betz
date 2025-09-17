# Step 1: Week 1: Research trending templates on Etsy

Goal and objective
- Objective for Week 1: produce a validated research foundation that identifies the highest-potential Etsy-style digital template opportunities (categories, styles, keywords, pricing and product features) so Week 2 can begin rapid AI-generated prototype creation.
- Success criteria: a prioritized shortlist of 3–6 template opportunities, a dataset of competitive signals, SEO keyword list, moodboards and a pricing/revenue model for each shortlisted opportunity.

High-level approach
We will use only our internal platform tools and agent network to collect, analyze and synthesize marketplace signals that replicate the “Etsy trends” picture. Key internal tools: ML Analytics (Marketplace Insights module), Marketplace Signal Connector, AI Content Studio, design-agent, market-research-agent, marketing-agent, analytics-agent and Revenue Engine. The Publishing Automation System will be referenced for downstream listing strategy.

Week 1 detailed day-by-day action plan

Day 1 — Kickoff, scope and research brief
- Actions:
  - Run a 1-hour kickoff with assigned internal agents: market-research-agent, analytics-agent, design-agent, marketing-agent, and a project lead in our platform project dashboard.
  - Define target template types to evaluate (e.g., wedding invitations, Instagram templates, printable planners, business card templates, Lightroom presets, resume templates). Limit scope to 6 categories to keep analysis focused.
  - Create a research brief document in the platform (objectives, KPIs, data sources, timelines, owners).
- Tools:
  - Project Dashboard (assign owners + timeline)
  - market-research-agent (to confirm categories)
- Expected outcomes:
  - Finalized research brief and owner assignments.
  - Top 6 target template categories selected.

Day 2 — Data ingestion and raw signal collection
- Actions:
  - Use Marketplace Signal Connector + ML Analytics (Marketplace Insights module) to ingest public marketplace signals for the 6 target categories (title, tags, price, average rating, sales rank/volume estimations, reviews, visual thumbnails, listing age, image styles, and top seller lists).
  - Pull time-series search volume and category growth metrics for the last 12 months.
  - Export raw dataset into a shared dataset table (CSV and platform dashboard).
- Tools:
  - Marketplace Signal Connector (licensed connectors for public marketplace signals)
  - ML Analytics > Marketplace Insights (for normalized metrics and search trends)
  - analytics-agent (to run ingestion jobs and verify data quality)
- Expected outcomes:
  - Raw dataset with ~100 top listings per category and 12-month trend data.
  - Dashboard with basic visualizations (volume by category, top sellers).

Day 3 — Competitor mapping and feature extraction
- Actions:
  - Use analytics-agent to cluster listings into template subtypes and extract common product attributes (file formats included, customization level, number of pages/variations, included assets, mockup style).
  - Pull top customer review themes and pain points (e.g., “hard to customize,” “missing fonts”) using ML Analytics sentiment and topic extraction.
  - Use AI Content Studio to generate three moodboards (visual style comps) per category reflecting top visual trends found in thumbnails.
- Tools:
  - analytics-agent + ML Analytics (clustering, sentiment / topic extraction)
  - AI Content Studio (for moodboards and visual reference generation)
  - design-agent (to review and annotate moodboards)
- Expected outcomes:
  - Feature matrix per category (lists common features and “opportunity gaps”).
  - Three moodboards per category for design inspiration.

Day 4 — Keyword, SEO and demand signal deep dive
- Actions:
  - Use ML Analytics Keyword Explorer to generate search volume, seasonality, rising (and declining) keywords, and long-tail phrases for each target category and sub-type.
  - Have marketing-agent produce a prioritized list of 30 SEO tags and long-tail keywords per category, plus recommended listing titles and short descriptions optimized for conversions.
  - Validate top keywords against historical conversion correlation data in ML Analytics (which keywords have correlated with top-selling listings).
- Tools:
  - ML Analytics > Keyword Explorer
  - marketing-agent (for tag/title/description recommendations)
- Expected outcomes:
  - SEO kit per category: top 30 keywords, 6 title templates, 3 description snippets, and tag sets.
  - Seasonality calendar highlighting peak months and launch timing recommendations.

Day 5 — Pricing, revenue modeling and opportunity prioritization
- Actions:
  - Use Revenue Engine to run pricing simulations for licensing (single-use, commercial, extended), bundling (single vs. bundles vs. subscription), and expected conversion rates based on comparable listings.
  - Generate conservative, expected, and aggressive monthly revenue forecasts for each opportunity using data from ML Analytics (sales volume estimates) and Revenue Engine elasticities.
  - Convene a 60-minute prioritization meeting with design-agent, marketing-agent and analytics-agent to review findings and select the top 3–6 template concepts for Week 2 prototyping. Produce a prioritized backlog with rationale and acceptance criteria.
  - Create a concise “Week 1 Research Pack” including dataset exports, dashboards, moodboards, feature matrix, SEO kit, pricing models and prioritized backlog.
- Tools:
  - Revenue Engine (price simulator and revenue forecasting)
  - ML Analytics (supporting data)
  - design-agent + marketing-agent (for gating and prioritization)
- Expected outcomes:
  - Pricing strategy for each shortlisted template (recommended price points and licensing).
  - Revenue projection table (3 scenarios) per shortlisted opportunity.
  - Prioritized backlog and Week 2 plan (prototype briefs).

Deliverables at the end of Week 1
- Research brief and owner assignments.
- Raw dataset (CSV) and ML Analytics dashboards (market trends, top listings).
- Feature matrix and competitor mapping for the 6 categories.
- Moodboards (3 per category) created in AI Content Studio and annotated by design-agent.
- SEO kit: top keywords, title templates, descriptions and recommended tags.
- Pricing & monetization models from Revenue Engine (3 scenarios each).
- Prioritized backlog of 3–6 template concepts to prototype in Week 2.
- One-page executive summary with suggested go/no-go signals.

KPIs and quality checks
- Data coverage: at least 100 listings per category ingested and normalized.
- Keyword confidence: top 10 keywords per category should match both search volume and conversion correlation metrics in ML Analytics.
- Revenue forecast confidence: model includes sensitivity analysis (±20% of conversion rates).
- Design validation: at least one moodboard per selected concept that matches top visual trends from thumbnails and customer sentiment.

Owners and time estimates (example)
- Project lead: 4 hours (Day 1 setup, Day 5 review).
- analytics-agent: 18 hours (Day 2 ingestion, Day 3 clustering, Day 4 keyword validation).
- market-research-agent: 8 hours (Day 1 scoping, Day 2 context research).
- design-agent + AI Content Studio: 8 hours (Day 3 moodboards, Day 5 concept sketches).
- marketing-agent: 6 hours (Day 4 SEO kit, Day 5 messaging).
- Revenue Engine analyst: 4 hours (Day 5 pricing sims).
- Total approx. human/agent hours: 48 agent-hours across the week.

How this leverages internal platform advantages and saves cost
- All ingestion, analytics and creative work uses built-in tools (Marketplace Signal Connector, ML Analytics, AI Content Studio, Revenue Engine and agent network). This avoids external subscriptions, manual scraping setups, and disjointed tool billing.
- The integrated workflow (data → insights → creative briefs → pricing) reduces handoffs and time-to-prototype, and the platform APIs allow one-click handover to prototype generation, listing automation and revenue monitoring in Week 2–3.

Next immediate steps after Week 1
- Start Week 2 with the prioritized brief for prototype generation in AI Content Studio and automated A/B test plans in Publishing Automation System.
- Configure Revenue Engine to auto-track performance once listings go live and feed back into ML Analytics for iterative optimization.

If you’d like, I can now:
- Provision the Week 1 research project in the platform dashboard and auto-assign the agents and timelines, or
- Create the research brief template and start the Marketplace Signal Connector job to ingest the first category’s data. Which would you prefer?

## Real Data Used
- Web search: 2 results
- API calls: 1 endpoints
- Files created: 1
