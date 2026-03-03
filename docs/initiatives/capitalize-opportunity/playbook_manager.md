# Playbook: Manager

> Role-specific playbook for engineering/product managers capitalizing on talent market intelligence via the Donkey Betz platform.

---

## 1. Who This Is For (ICP)

- Engineering managers (5–50 direct reports) at mid-to-large companies actively hiring or restructuring
- Product managers responsible for team velocity and delivery capacity
- VP/Director-level leaders managing multiple squads with budget authority
- Managers in high-turnover domains (fintech, AI/ML, DevOps) where signal speed matters
- Hiring managers who need to backfill critical roles within 30-day windows

---

## 2. Primary Jobs-to-Be-Done

1. **Spot talent market shifts before competitors** — detect when key engineers become available, when competitor teams shrink, or when salary benchmarks move
2. **Reduce time-to-fill for critical roles** — get actionable candidate signals within hours, not weeks
3. **Retain high-performers proactively** — detect flight-risk signals (LinkedIn activity, competitor poaching patterns) before resignation
4. **Optimize team composition** — identify skill gaps via market trend analysis and backfill strategically
5. **Make data-driven headcount decisions** — use market intelligence to justify budget requests or hiring freezes

---

## 3. Signals That Matter

| # | Signal | Source | Freshness |
|---|--------|--------|-----------|
| 1 | Competitor layoff announcements | Spider: techcrunch, hackernews, business_news | Real-time |
| 2 | Spike in job postings for a specific role/stack | Spider: adzuna, github_jobs | Daily |
| 3 | Senior engineer LinkedIn status changes | Spider: bluesky, reddit | Daily |
| 4 | Salary benchmark shifts (>5% in 90 days) | Spider: adzuna, financial | Weekly |
| 5 | Team member public activity spike (blog posts, conference talks, open-source) | Spider: devto, github, hackernews | Daily |
| 6 | Competitor funding round (hiring surge likely) | Spider: crunchbase, venturebeat | Real-time |
| 7 | Technology adoption trends (new framework gaining traction) | Spider: hackernews, stackoverflow, github | Weekly |
| 8 | Internal velocity/delivery metric decline | Platform: AgentExecution, CeleryTaskEvent | Continuous |
| 9 | Counter-offer market data (what competitors are paying for specific roles) | Spider: adzuna, financial | Weekly |
| 10 | Conference/meetup speaker lineups (talent identification) | Spider: devto, producthunt | Monthly |

---

## 4. Signal-to-Insight Rules

| # | IF (Signal) | THEN (Insight) | Confidence |
|---|-------------|-----------------|------------|
| 1 | Competitor announces layoffs AND you have open reqs for same stack | **Talent window open** — high-quality candidates entering market in 2-4 weeks | 0.85 |
| 2 | Job postings for your key roles increase >20% in 30 days | **Market heating up** — accelerate hiring or risk longer time-to-fill and higher salary expectations | 0.75 |
| 3 | Team member's public GitHub/blog activity spikes AND no internal project explains it | **Potential flight risk** — schedule 1:1, discuss growth path | 0.60 |
| 4 | Salary benchmarks for a role shift >5% quarter-over-quarter | **Comp adjustment needed** — review offers in pipeline, update bands, or risk losing candidates at offer stage | 0.80 |
| 5 | Competitor raises Series B+ AND starts posting 10+ engineering roles | **Poaching risk incoming** — expect recruiter outreach to your team within 30 days | 0.70 |
| 6 | Technology you use is declining in job postings while an alternative rises | **Stack migration signal** — evaluate reskilling investment vs. hiring for new stack | 0.65 |
| 7 | Multiple senior engineers from same company update LinkedIn within a week | **Team exodus in progress** — potential acqui-hire or team lift-out opportunity | 0.75 |
| 8 | Internal delivery metrics drop >15% over 2 sprints AND no scope change explains it | **Capacity problem** — investigate burnout, tooling issues, or headcount gap | 0.70 |

---

## 5. Actions to Take

### Within 15 Minutes
- Review the signal digest and tag relevant signals as "actionable" or "watch"
- If talent window signal: draft shortlist of target candidates from competitor's public team page
- If flight risk signal: block 30 min on your calendar for a 1:1 within 48 hours

### Within 24 Hours
- If talent window: activate recruiter outreach sequence (use DM/email templates below)
- If market heating: update job descriptions with current salary range data
- If comp adjustment needed: pull internal comp data and draft adjustment memo
- Share relevant signals with your recruiting partner via the platform

### Within 7 Days
- If stack migration signal: schedule tech lead discussion, commission a spike/POC
- If poaching risk: implement retention check-ins across team, review equity refresh timing
- Review and close out stale action items from previous digest cycles
- Post synthesis to governance for cross-team visibility

---

## 6. Templates

### Outreach DM (for sourcing candidates from competitor layoffs)
```
Hi [Name] — I saw [Company] is going through changes. Your work on [specific project/contribution] caught my attention.

We're building [brief description] and looking for someone with exactly your background in [skill]. Would you be open to a quick chat this week? No pressure, just exploring.
```

### Email (for recruiter handoff)
```
Subject: High-priority sourcing — [Role] candidates from [Competitor] transition

Hi [Recruiter],

[Competitor] announced [layoff/restructuring] on [date]. Based on our signal intelligence, we expect [N] engineers with [relevant stack] experience to be actively looking within 2-4 weeks.

Priority target profiles:
- [Profile 1: Role + years + specific skill]
- [Profile 2: Role + years + specific skill]

Current market rate for this role: $[X]-$[Y] (updated [date] via platform benchmarks).

Please prioritize outreach this week. I've tagged the relevant signals in the platform under Initiative [ID].
```

### Internal Note / Log Entry
```
Signal: [Signal type] detected [date]
Source: [Spider/agent name]
Confidence: [0.X]
Action taken: [What you did]
Outcome: [Result or pending]
Next review: [Date]
```

---

## 7. Success Metrics

### Leading Indicators
1. **Signal-to-action rate** — % of flagged signals that result in a concrete action within 24h (target: >60%)
2. **Time-to-first-outreach** — hours between talent window signal and first candidate contact (target: <48h)
3. **Signal accuracy** — % of signals confirmed by subsequent events (target: >70%)
4. **Digest engagement** — % of digests reviewed within 4 hours of posting (target: >80%)

### Lagging Indicators
5. **Time-to-fill reduction** — average days to fill roles vs. pre-platform baseline (target: 20% reduction)
6. **Offer acceptance rate** — % of offers accepted (target: >75%)
7. **Retention rate** — 12-month retention of team members where flight-risk signals were actioned (target: >90%)
8. **Cost-per-hire** — total hiring cost per role (target: 15% reduction via faster, more targeted sourcing)

---

## 8. Failure Modes & Safeguards

| Failure Mode | How It Manifests | Safeguard |
|---|---|---|
| **Signal noise** | Manager gets 50+ signals/day, stops reading them | Tune signal thresholds; only surface signals with confidence >0.6 and novelty >0.3 |
| **False flight-risk alerts** | 1:1s feel surveillance-like, damage trust | Never mention the platform signal to the employee; frame 1:1s as routine growth conversations |
| **Stale action items** | Action items pile up, never closed | Auto-cancel items older than 14 days with no activity; weekly digest includes overdue count |
| **Competitor signal lag** | Layoff happened 2 weeks ago, signal arrives late | Prioritize real-time sources (HN, Twitter/Bluesky); set up keyword alerts for top 5 competitors |
| **Over-reliance on automation** | Manager stops using judgment, blindly follows rules | Every action requires human confirmation; platform suggests, manager decides |
| **Salary data staleness** | Comp recommendations based on 6-month-old data | Flag benchmarks older than 90 days; require manual refresh before comp adjustment memos |

---

## 9. Example Scenario Walkthrough

### Scenario: Competitor Layoff Creates Talent Window

**Day 0, 9:15 AM** — Spider `techcrunch` detects article: "FinTech startup Payflow lays off 30% of engineering team." Signal confidence: 0.90. The signal is automatically tagged and included in the next ops digest.

**Day 0, 9:45 AM** — Manager opens Command Center, sees the digest. The signal-to-insight rule fires: "Competitor announces layoffs AND you have open reqs for same stack → Talent window open." The manager has 2 open reqs for backend engineers with Python/Django experience — exactly Payflow's stack.

**Day 0, 10:00 AM** — Manager uses the outreach DM template to contact 3 engineers from Payflow's public GitHub contributors list. Sends recruiter the email template with target profiles and updated salary benchmarks ($145K-$175K, refreshed via adzuna spider 3 days ago).

**Day 1** — 2 of 3 candidates respond positively. Recruiter schedules intro calls.

**Day 5** — First candidate completes technical interview. Strong match.

**Day 12** — Offer extended. Candidate accepts (comp was competitive because benchmarks were current).

**Day 14** — Manager closes the action item in the platform, logs the outcome. Synthesis template is filled and posted to governance for cross-team visibility.

**Result:** Role filled in 14 days (vs. 45-day baseline). Platform signal gave a 2-week head start over competitors who waited for LinkedIn profiles to update.
