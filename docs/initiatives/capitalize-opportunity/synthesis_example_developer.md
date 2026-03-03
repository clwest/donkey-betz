# Synthesis Example: Developer — Stack Risk and Career Pivot Opportunity

```yaml
synthesis:
  meta:
    date: "2026-03-03"
    agent: "ContentStrategyAgent"
    desk: "talent"
    source_types:
      - spider_data
      - platform_metric
      - manual_research

  summary: >
    Ruby on Rails job postings have declined 18% YoY while Elixir/Phoenix
    postings grew 45% in the same backend web category. A senior Rails
    developer with 6+ years experience faces a narrowing market but has a
    natural migration path to Elixir with a $15K+ comp premium. A trending
    open-source Elixir project presents an immediate visibility opportunity.

  signals:
    - signal: "Ruby on Rails job postings declined 18% year-over-year"
      evidence: "Adzuna spider, 12-month rolling comparison, backend web category"
      confidence: 0.80
    - signal: "Elixir/Phoenix job postings increased 45% year-over-year"
      evidence: "Adzuna spider, 12-month rolling comparison, same category"
      confidence: 0.80
    - signal: "Trending Elixir project 'LiveDash' has 800 stars, 30 contributors, active maintainer"
      evidence: "GitHub spider, trending repos filter, created 4 months ago"
      confidence: 0.90
    - signal: "Senior Elixir engineer median salary: $170K vs Senior Rails: $155K"
      evidence: "Adzuna + Levels.fyi cross-reference, US remote roles, March 2026"
      confidence: 0.75
    - signal: "HN discussion: 'Is Rails still worth learning in 2026?' — 340 points, mixed sentiment"
      evidence: "HN spider, 2026-02-25, 280+ comments"
      confidence: 0.70

  insights:
    - insight: "Rails is not dying but is entering a mature/declining demand phase — fewer new projects, more maintenance"
      rationale: "Posting decline is gradual (18%, not 50%); existing Rails codebases ensure years of maintenance demand, but new greenfield projects increasingly choose alternatives"
      novelty: 0.4
    - insight: "Elixir has a talent supply shortage — 45% demand growth with a much smaller talent pool creates premium pricing"
      rationale: "Elixir community is ~1/20th the size of Rails by GitHub contributor count, but demand is growing faster"
      novelty: 0.7
    - insight: "Early open-source contribution to LiveDash could create disproportionate visibility in the Elixir community"
      rationale: "30 contributors on an 800-star project means each contributor has outsized visibility. Rails equivalent would need 500+ stars to match."
      novelty: 0.8
    - insight: "The Rails-to-Elixir migration path is natural — both are full-stack web frameworks with similar MVC patterns"
      rationale: "Phoenix deliberately mirrors Rails conventions. Several high-profile Rails developers (Chris McCord, Jose Valim) built Elixir/Phoenix specifically for Rails developers."
      novelty: 0.3

  recommended_actions:
    - action: "Fork LiveDash, complete one meaningful PR (bug fix or feature, not just docs)"
      owner: "Developer"
      expected_impact: "Establishes credibility in Elixir community; visible on GitHub profile"
      effort: "medium"
    - action: "Write blog post: 'What a Rails Engineer Learned Building with Elixir'"
      owner: "Developer"
      expected_impact: "Positions developer as a bridge between communities; high HN/dev.to engagement potential"
      effort: "medium"
    - action: "Update resume and portfolio to highlight both Rails depth AND Elixir exploration"
      owner: "Developer"
      expected_impact: "Signals growth mindset to recruiters; eligible for both Rails maintenance and Elixir greenfield roles"
      effort: "low"
    - action: "Set platform alerts for Elixir roles at target companies"
      owner: "Developer"
      expected_impact: "First-mover on relevant postings"
      effort: "low"

  risks:
    - risk: "Investing in Elixir may not pay off if adoption plateaus"
      mitigation: "Elixir learning is not a full pivot — Rails skills remain marketable. Treat as portfolio diversification, not replacement."
    - risk: "Current employer may not value Elixir skills"
      mitigation: "Position as 'performance optimization research' internally; Elixir's concurrency model solves real problems in any stack"
    - risk: "Blog post could signal 'looking to leave' to current employer"
      mitigation: "Frame as technical exploration, not career pivot. Many engineers blog about technologies they find interesting."

  citations_needed:
    - "Rails vs Elixir posting growth — verify Adzuna data against Indeed/LinkedIn trends"
    - "Salary differential — cross-reference with Levels.fyi for Elixir-specific data points"
    - "LiveDash project health — check if maintainer is responsive and project is actively merging PRs"

  quality_checks:
    passed:
      - "Signals use multiple independent sources"
      - "Insights distinguish between signal (data) and interpretation (opinion)"
      - "Actions are concrete and achievable within 1-2 weeks"
      - "Novelty scores reflect genuine newness (stack decline is known = 0.4, contribution leverage is non-obvious = 0.8)"
    failed: []
    notes: "Moderate confidence synthesis. The core insight (stack transition opportunity) is well-supported. The specific timing recommendation (contribute to LiveDash now) depends on project health, which should be verified."

  decision_request:
    requested: false
    question: ""
    deadline: ""
    options: []
```
