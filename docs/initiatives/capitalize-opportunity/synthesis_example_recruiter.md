# Synthesis Example: Recruiter — Team Dispersion Sourcing Opportunity

```yaml
synthesis:
  meta:
    date: "2026-03-03"
    agent: "CustomerResearchAgent"
    desk: "talent"
    source_types:
      - spider_data
      - agent_execution

  summary: >
    A cluster of 6 Rust/systems engineers from CloudBase have signaled
    availability across HN and GitHub within 72 hours. One open req for a
    systems engineer (Rust/Go) is at day 24 with only 2 candidates in pipeline.
    This is a first-mover sourcing opportunity with a 7-day window.

  signals:
    - signal: "4 CloudBase engineers posted in 'Ask HN: Who is hiring?' thread within 48 hours"
      evidence: "HN spider detected 4 distinct users mentioning CloudBase departure, 2026-03-01 to 2026-03-02"
      confidence: 0.85
    - signal: "2 additional CloudBase engineers removed employer from GitHub profiles"
      evidence: "GitHub spider profile change detection, 2026-03-02"
      confidence: 0.75
    - signal: "CloudBase Glassdoor rating dropped from 3.8 to 3.2 in last quarter"
      evidence: "Reddit spider discussion thread referencing Glassdoor decline, 2026-02-28"
      confidence: 0.65
    - signal: "Our systems engineer req (Rust/Go) has been open 24 days with 2 candidates"
      evidence: "Platform Opportunity model, pipeline count from action items"
      confidence: 1.0

  insights:
    - insight: "This is a team dispersion event — CloudBase platform team is breaking up, not a general layoff"
      rationale: "All 6 signals are from platform/infrastructure roles, not across the company. Suggests team-specific issues."
      novelty: 0.7
    - insight: "First-mover window is approximately 7 days based on signal-to-LinkedIn-update lag"
      rationale: "HN posts appeared 3 days before any LinkedIn changes. Competing recruiters scan LinkedIn, not HN."
      novelty: 0.8
    - insight: "Rust engineers command a 15% premium over Go-only engineers in current market"
      rationale: "Adzuna data shows median Rust role at $172K vs Go at $150K for same experience level"
      novelty: 0.5

  recommended_actions:
    - action: "Build target list of CloudBase Rust contributors from their public GitHub org"
      owner: "Sourcer"
      expected_impact: "Identify 8-12 qualified candidates with verified skill evidence"
      effort: "low"
    - action: "Send personalized DMs to top 5 candidates referencing specific contributions"
      owner: "Recruiter"
      expected_impact: "Expected 40%+ response rate based on personalized + timely outreach"
      effort: "medium"
    - action: "Pre-schedule technical screen slots for this week"
      owner: "Recruiting Coordinator"
      expected_impact: "Reduce time-to-interview from 5 days to 2 days"
      effort: "low"
    - action: "Brief hiring manager on CloudBase dispersion and Rust salary premium"
      owner: "Recruiter"
      expected_impact: "HM prepared for faster decision-making and comp negotiation"
      effort: "low"

  risks:
    - risk: "CloudBase engineers may be relocating, not available for our geo/remote policy"
      mitigation: "Confirm location/remote preference in initial outreach"
    - risk: "Signal could be a reorganization, not departures — engineers may stay after re-org"
      mitigation: "Cross-reference HN posts with LinkedIn activity in 3-5 days"
    - risk: "Multiple recruiters reach same candidates simultaneously"
      mitigation: "Speed is the mitigation — outreach within 24 hours, before LinkedIn signals broadcast"

  citations_needed:
    - "CloudBase GitHub org contributor list — verify profiles are current employees"
    - "Glassdoor rating change — cross-reference with Blind posts for corroboration"
    - "Rust vs Go salary differential — verify with second source (Levels.fyi or similar)"

  quality_checks:
    passed:
      - "Signal sources are independent (HN, GitHub, Glassdoor via Reddit)"
      - "Confidence scores reflect source reliability"
      - "Actions are time-sequenced with clear owners"
      - "Risks include counter-scenario (reorg, not departure)"
    failed: []
    notes: "Moderate-high confidence. Key uncertainty is whether this is truly a team departure vs internal restructure. 3-day follow-up check recommended."

  decision_request:
    requested: false
    question: ""
    deadline: ""
    options: []
```
