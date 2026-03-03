# Synthesis Example: Manager — Competitor Layoff Talent Window

```yaml
synthesis:
  meta:
    date: "2026-03-03"
    agent: "CompetitorAnalysisAgent"
    desk: "talent"
    source_types:
      - spider_data
      - platform_metric
      - manual_research

  summary: >
    Payflow announced a 30% engineering reduction on March 1. Their platform
    team (12 engineers, Python/Django stack) is directly relevant to our 2 open
    backend reqs. Market data shows a 48-hour first-mover window before
    competitors begin outreach.

  signals:
    - signal: "Payflow lays off 30% of engineering (36 of 120 engineers)"
      evidence: "TechCrunch article 2026-03-01; confirmed by HN discussion thread (450+ points)"
      confidence: 0.95
    - signal: "3 Payflow platform engineers updated GitHub bios to remove employer"
      evidence: "GitHub profile monitoring via github spider, detected 2026-03-02"
      confidence: 0.80
    - signal: "Backend engineer job postings in Denver metro up 12% month-over-month"
      evidence: "Adzuna spider aggregation, 30-day rolling average"
      confidence: 0.75
    - signal: "Our 2 open backend reqs have been unfilled for 28 days"
      evidence: "Platform Opportunity model, req ages: 28 and 31 days"
      confidence: 1.0

  insights:
    - insight: "Talent window is open for 7-10 days before LinkedIn profile updates trigger broad recruiter outreach"
      rationale: "Historical pattern from 3 prior competitor layoff events: LinkedIn updates lag behind actual availability by 5-10 days"
      novelty: 0.6
    - insight: "Payflow's Django/Python stack is a direct match for our backend roles — minimal ramp-up time"
      rationale: "Their public GitHub repos confirm Django 4.x, PostgreSQL, Celery — identical to our stack"
      novelty: 0.3
    - insight: "Current market rate for this profile is $145K-$175K, $10K above our posted range"
      rationale: "Adzuna salary data refreshed 3 days ago; our job descriptions list $135K-$165K"
      novelty: 0.7

  recommended_actions:
    - action: "Identify top 5 Payflow platform engineers via GitHub contributor history"
      owner: "Recruiter"
      expected_impact: "Build pipeline of pre-qualified candidates before competition"
      effort: "low"
    - action: "Update salary range on both open reqs to $145K-$175K"
      owner: "Hiring Manager"
      expected_impact: "Avoid offer-stage rejection due to below-market comp"
      effort: "low"
    - action: "Send personalized outreach to top 5 candidates within 24 hours"
      owner: "Recruiter"
      expected_impact: "First-mover advantage; expect 40-60% response rate on personalized outreach"
      effort: "medium"
    - action: "Brief hiring manager with market context and candidate profiles"
      owner: "Recruiter"
      expected_impact: "Faster interview scheduling and hiring decision"
      effort: "low"

  risks:
    - risk: "Candidates may have non-compete or garden leave clauses"
      mitigation: "Ask about availability timeline in initial outreach; don't assume immediate start"
    - risk: "Payflow counter-offers to retain key engineers"
      mitigation: "Move fast — get candidates into interview process before counter-offers materialize"
    - risk: "Our comp adjustment may not be approved in time"
      mitigation: "Hiring manager pre-approves range before recruiter sends outreach with comp expectations"

  citations_needed:
    - "Payflow layoff percentage — verify 30% figure against SEC filing or official statement"
    - "Salary benchmark source and date — confirm adzuna data is from last 7 days"
    - "Candidate GitHub profiles — verify they are actually Payflow employees, not contractors"

  quality_checks:
    passed:
      - "All signals have identified sources"
      - "Confidence scores are calibrated (no blind 1.0s except platform data)"
      - "Actions have clear owners and effort estimates"
      - "At least one risk mitigation for each risk"
    failed: []
    notes: "High-confidence synthesis. Primary risk is speed of execution, not data quality."

  decision_request:
    requested: true
    question: "Approve salary range increase from $135K-$165K to $145K-$175K for the 2 open backend reqs?"
    deadline: "2026-03-04"
    options:
      - "Approve range increase to $145K-$175K"
      - "Approve partial increase to $140K-$170K"
      - "Keep current range, compete on other factors (equity, remote, mission)"
```
