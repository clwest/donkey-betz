# Playbook: Position / Recruiter

> Role-specific playbook for recruiters and hiring specialists using Donkey Betz platform intelligence to source, evaluate, and close candidates faster.

---

## 1. Who This Is For (ICP)

- In-house technical recruiters sourcing for engineering, data, and product roles
- Agency recruiters specializing in tech placement with multiple client mandates
- Recruiting coordinators responsible for pipeline health and scheduling throughput
- Talent acquisition leads managing recruiter teams and tracking funnel metrics
- Sourcing specialists focused on passive candidate identification and engagement

---

## 2. Primary Jobs-to-Be-Done

1. **Build candidate pipelines before roles open** — use market signals to pre-source for likely upcoming reqs
2. **Identify passive candidates at inflection points** — detect when strong engineers are most likely to be receptive (company changes, project completions, market shifts)
3. **Calibrate compensation in real-time** — access current salary data to craft competitive offers without overpaying
4. **Reduce candidate drop-off** — use speed and relevance signals to prioritize the warmest leads
5. **Provide market intelligence to hiring managers** — arm HMs with data that accelerates decision-making

---

## 3. Signals That Matter

| # | Signal | Source | Freshness |
|---|--------|--------|-----------|
| 1 | New job postings from competitor companies (indicates role is open) | Spider: adzuna, github_jobs | Daily |
| 2 | Engineer publishes post/talk about "lessons learned" or "what I'd do differently" | Spider: devto, hackernews, medium | Daily |
| 3 | Company review sentiment shift on Glassdoor/Blind | Spider: reddit, bluesky | Weekly |
| 4 | Open-source contributor with high activity in target stack | Spider: github, huggingface | Weekly |
| 5 | Candidate profile views spike (they're shopping) | Spider: bluesky, reddit | Daily |
| 6 | Competitor hiring freeze or budget cut announcement | Spider: techcrunch, business_news | Real-time |
| 7 | Tech stack adoption curves (demand for specific skills) | Spider: hackernews, github, stackoverflow | Weekly |
| 8 | Conference speaker/attendee lists for target domains | Spider: devto, producthunt | Monthly |
| 9 | Salary survey releases or comp transparency posts | Spider: hackernews, reddit, business_news | Monthly |
| 10 | Internal req aging (open >21 days without pipeline) | Platform: Opportunity model, action items | Continuous |

---

## 4. Signal-to-Insight Rules

| # | IF (Signal) | THEN (Insight) | Confidence |
|---|-------------|-----------------|------------|
| 1 | Engineer posts "retrospective" or "what's next" content AND has >3 years at current company | **Transition window** — candidate likely evaluating next move within 60 days | 0.65 |
| 2 | Competitor posts same role you're filling AND their Glassdoor rating dropped in last quarter | **Counter-positioning opportunity** — highlight culture/stability in your outreach | 0.70 |
| 3 | GitHub contributor has 50+ commits/month in your target stack AND no employer listed | **Freelancer/contractor prospect** — may be open to full-time with right offer | 0.60 |
| 4 | Req open >21 days AND <3 candidates in pipeline | **Pipeline emergency** — escalate sourcing effort, consider broadening search criteria or adjusting comp | 0.85 |
| 5 | Salary data for target role shifts >8% in 60 days | **Market correction needed** — update all active offers and job descriptions; brief hiring manager | 0.80 |
| 6 | Multiple engineers from same company posting "open to work" signals | **Team dispersion event** — bulk source from this company immediately; first-mover advantage decays in ~7 days | 0.80 |
| 7 | Target candidate's company announces pivot to different tech stack | **Skill-mismatch trigger** — engineers in legacy stack may be receptive to roles where their skills are valued | 0.65 |
| 8 | Conference in target domain is 30 days away AND you have open reqs | **Event sourcing window** — prepare attendee outreach, sponsor booth, or host side event | 0.70 |

---

## 5. Actions to Take

### Within 15 Minutes
- Review daily signal digest; star candidates in "transition window" or "team dispersion" signals
- If pipeline emergency: flag to hiring manager with current market context
- If comp shift: update salary range in ATS and notify hiring manager

### Within 24 Hours
- For each starred candidate: research their work (GitHub, blog, talks), personalize outreach
- Send outreach using templates below (DM for warm, email for cold)
- If team dispersion event: build target list of 10-15 engineers from the company, prioritize by stack match
- Update pipeline metrics and share market intelligence brief with hiring manager

### Within 7 Days
- Follow up on unreplied outreach (one follow-up only — respect the candidate)
- If conference sourcing window: finalize attendee target list, prepare talking points
- Close out stale candidates (>14 days no response = archive)
- Post synthesis to platform for cross-team visibility and learning loop

---

## 6. Templates

### Outreach DM (Passive Candidate — Warm Signal)
```
Hey [Name] — I came across your [blog post / talk / project] on [topic]. Really sharp work, especially [specific detail].

We're hiring a [role] to work on [interesting problem]. Your experience with [skill] is a strong fit. Would you be up for a 15-min chat to see if there's mutual interest?

No strings — happy to share what we're building either way.
```

### Email (Cold Outreach — Stack Match)
```
Subject: [Skill] engineer — [Company] is building something you'd find interesting

Hi [Name],

I'm [Your Name], recruiting for [Company]. I found your profile through [source — GitHub contributions / conference talk / blog].

We're looking for a [role] to [one-sentence mission]. The stack is [languages/frameworks], and the team is [size] engineers working on [problem space].

Comp range: $[X]-$[Y] + [equity/benefits highlights].

Would a quick call this week work? I can share more about the role and answer any questions.

Best,
[Your Name]
```

### Internal Note / Log Entry
```
Candidate: [Name]
Source signal: [Signal type] — [date detected]
Outreach: [DM/email] sent [date]
Response: [Positive/No response/Declined]
Pipeline stage: [Sourced → Screen → Interview → Offer]
Comp calibration: $[X] (market rate as of [date])
Next step: [Action + date]
```

---

## 7. Success Metrics

### Leading Indicators
1. **Outreach response rate** — % of personalized outreach that gets a reply (target: >35%)
2. **Signal-to-outreach time** — hours between signal detection and first candidate contact (target: <24h)
3. **Pipeline coverage ratio** — candidates in pipeline per open req (target: >5:1)
4. **Market intel briefings delivered** — # of hiring manager briefings per week (target: 1 per active req)

### Lagging Indicators
5. **Time-to-fill** — days from req open to offer accepted (target: <30 days)
6. **Source quality** — % of platform-sourced candidates who reach final interview (target: >40%)
7. **Offer acceptance rate** — % of offers accepted (target: >80%)
8. **Cost-per-hire** — all-in cost per filled role (target: 20% below agency benchmark)

---

## 8. Failure Modes & Safeguards

| Failure Mode | How It Manifests | Safeguard |
|---|---|---|
| **Spray-and-pray outreach** | High volume, low personalization → response rate drops below 15% | Enforce personalization checklist: must reference specific work/project |
| **Signal overload** | Recruiter ignores daily digest because it's too noisy | Cap signals at top 10/day; filter by confidence >0.6 and stack match |
| **Stale pipeline** | Candidates sit in "contacted" stage for weeks with no follow-up | Auto-archive after 14 days; weekly pipeline hygiene report |
| **Comp miscalibration** | Offers rejected because salary data is outdated | Flag benchmark data older than 60 days; require refresh before offer stage |
| **Candidate experience damage** | Multiple recruiters from same company reach out to same person | De-dup outreach log in platform; check before contacting |
| **Over-indexing on passive signals** | Recruiter chases "transition window" candidates while ignoring active applicants | Dashboard shows active vs. passive pipeline balance; alert if ratio >70% passive |

---

## 9. Example Scenario Walkthrough

### Scenario: Team Dispersion Event at Target Company

**Day 0, 8:00 AM** — Spider `hackernews` detects discussion thread: "Ask HN: Leaving [TechCo] — what's the market like for Rust engineers?" Multiple commenters confirm layoffs in TechCo's platform team. Signal confidence: 0.80.

**Day 0, 8:30 AM** — Recruiter opens daily digest in Command Center. Signal-to-insight rule fires: "Multiple engineers from same company posting open-to-work signals → Team dispersion event — bulk source immediately." Recruiter has 1 open req for a systems engineer (Rust/Go).

**Day 0, 9:00 AM** — Recruiter builds target list: searches TechCo's public GitHub org for Rust contributors with >100 commits in the last year. Identifies 8 strong profiles. Cross-references with platform outreach log — none have been contacted before.

**Day 0, 11:00 AM** — Sends personalized DMs to top 5 candidates using the warm outreach template. Each message references a specific open-source contribution.

**Day 1** — 3 replies. Two interested in learning more, one declines (already accepted elsewhere — confirms the 7-day first-mover window).

**Day 3** — Hiring manager conducts intro calls with both interested candidates. Both advance to technical screen.

**Day 8** — First candidate completes technical interview. Strong hire recommendation.

**Day 11** — Offer extended at $168K (market rate confirmed via platform benchmarks refreshed 5 days ago). Candidate accepts.

**Day 12** — Recruiter logs outcome in platform, fills synthesis template, closes action items.

**Result:** Role filled in 12 days from signal detection. Platform gave recruiter a 48-hour head start over competitors who saw the LinkedIn updates a week later.
