# Playbook: Developer

> Role-specific playbook for individual developers using Donkey Betz platform intelligence to advance their career, find opportunities, and build leverage.

---

## 1. Who This Is For (ICP)

- Mid-to-senior engineers (3-10+ years) actively or passively exploring new opportunities
- Developers building side projects or freelance practices who need market intelligence
- Engineers evaluating job offers and needing real-time comp/market data
- Tech leads considering management track vs. IC track decisions
- Developers in at-risk positions (company struggling, stack declining, team shrinking)

---

## 2. Primary Jobs-to-Be-Done

1. **Know my market value in real-time** — access current salary data for my exact stack/experience/location without waiting for annual surveys
2. **Detect opportunities before they're public** — get signals about companies hiring, teams forming, or projects starting before the job posting goes live
3. **Time career moves strategically** — understand when the market favors candidates vs. employers for my skill set
4. **Build visible expertise** — identify trending topics and gaps where publishing/contributing creates outsized career leverage
5. **Evaluate companies with real data** — go beyond Glassdoor ratings to understand eng culture, tech debt, and team stability signals

---

## 3. Signals That Matter

| # | Signal | Source | Freshness |
|---|--------|--------|-----------|
| 1 | Job postings matching my stack spike in volume | Spider: adzuna, github_jobs | Daily |
| 2 | Salary ranges for my role shift significantly | Spider: adzuna, financial, reddit | Weekly |
| 3 | Company I'm interested in starts posting engineering roles | Spider: adzuna, github_jobs, crunchbase | Daily |
| 4 | My primary tech stack trending up/down in adoption | Spider: hackernews, github, stackoverflow | Weekly |
| 5 | Company I work at shows risk signals (layoffs, revenue decline, leadership changes) | Spider: techcrunch, business_news, sec_edgar | Real-time |
| 6 | New open-source project gaining traction in my domain | Spider: github, hackernews, producthunt | Weekly |
| 7 | Conference CFPs open in my expertise area | Spider: devto, producthunt | Monthly |
| 8 | Competitor companies raising funding (expanding teams) | Spider: crunchbase, venturebeat | Real-time |
| 9 | Blog posts/discussions about "hot" technical problems I can solve | Spider: hackernews, reddit, devto | Daily |
| 10 | Remote work policy changes at target companies | Spider: hackernews, reddit, business_news | Weekly |

---

## 4. Signal-to-Insight Rules

| # | IF (Signal) | THEN (Insight) | Confidence |
|---|-------------|-----------------|------------|
| 1 | Job postings for my stack increase >25% in 30 days AND salary ranges are rising | **Seller's market** — strong negotiating position; consider exploring if current comp is below new benchmarks | 0.80 |
| 2 | My company appears in negative news (layoffs, revenue miss) AND I haven't been promoted in 18+ months | **Elevated risk position** — start passive exploration; update resume and portfolio | 0.75 |
| 3 | Trending open-source project in my domain has <50 contributors AND >1000 stars | **Contribution opportunity** — early contributor status creates disproportionate visibility and networking | 0.70 |
| 4 | Target company posts 5+ engineering roles in 2 weeks AND recently raised funding | **Growth phase hiring** — less bureaucratic process, more equity upside, higher role flexibility | 0.75 |
| 5 | My primary framework/language declining in job postings by >15% year-over-year | **Stack risk** — invest in adjacent/emerging technology; don't wait for obsolescence | 0.70 |
| 6 | HN/Reddit discussion about a problem I've solved gets >200 points | **Thought leadership window** — write a blog post or detailed comment about my approach; high visibility moment | 0.65 |
| 7 | Multiple companies in my target list shift to remote-first policies | **Location arbitrage opportunity** — can target higher-comp roles without relocating | 0.70 |
| 8 | Conference CFP deadline in my domain is 30 days away AND I have relevant experience | **Speaking opportunity** — submit proposal; accepted talks are high-leverage career signals | 0.60 |

---

## 5. Actions to Take

### Within 15 Minutes
- Review daily signal digest; flag signals that directly affect your current position or target companies
- If seller's market signal: check your current comp against the updated benchmarks
- If risk position signal: don't panic — note it and plan exploration (not a fire drill)

### Within 24 Hours
- If contribution opportunity: fork the repo, read contributor guidelines, identify a good first issue
- If growth phase hiring at target company: research the team (who's there, what they're building, eng blog)
- If thought leadership window: draft a blog post outline or detailed HN/Reddit comment
- Update your "market position" notes: current comp, target comp, target companies, skills inventory

### Within 7 Days
- If stack risk: identify one adjacent technology, start a small learning project (not a full pivot)
- If speaking opportunity: write and submit CFP proposal
- If seller's market: update resume/portfolio, tell trusted contacts you're exploring
- Review and journal: what did the signals teach you about your market position this week?

---

## 6. Templates

### Outreach DM (to someone at a target company)
```
Hi [Name] — I've been following [Company]'s work on [project/product]. Your [blog post / talk / commit] on [topic] was really insightful.

I'm a [role] with [X] years working on [stack/domain]. I'd love to hear what it's like building at [Company] — would you be open to a 15-min coffee chat? No agenda beyond learning.
```

### Email (responding to a recruiter with leverage)
```
Subject: Re: [Role] at [Company]

Hi [Recruiter],

Thanks for reaching out. The role looks interesting — [specific thing about the role/company that caught your attention].

A few things that would help me evaluate fit:
1. What's the comp range for this level? (I'm currently benchmarked at $[X] based on [source].)
2. What does the eng team structure look like? (Team size, reporting, tech debt posture)
3. What's the timeline? I'm [actively looking / passively exploring], so I want to be upfront.

Happy to hop on a call if the above aligns.

Best,
[Your Name]
```

### Internal Note / Log Entry
```
Date: [YYYY-MM-DD]
Signal: [Type] — [brief description]
My assessment: [How this affects my position / opportunities]
Action taken: [What I did or plan to do]
Market position update: [Current comp: $X | Target: $Y | Gap: $Z]
Skills to invest in: [Based on trend signals]
Next review: [Date]
```

---

## 7. Success Metrics

### Leading Indicators
1. **Signal review rate** — % of weekly digests reviewed within 24h (target: >90%)
2. **Actions per week** — # of concrete career actions taken from signals (target: >2)
3. **Network expansion** — new meaningful connections per month from signal-driven outreach (target: >3)
4. **Content published** — blog posts/talks/contributions per quarter from trend signals (target: >2)

### Lagging Indicators
5. **Comp growth** — year-over-year compensation increase (target: >10%, market-adjusted)
6. **Opportunity quality** — % of inbound recruiter outreach that matches your target criteria (target: increases over time as profile sharpens)
7. **Time-to-offer** — days from active search start to offer accepted (target: <45 days)
8. **Career satisfaction** — self-assessed rating of role fit and growth trajectory (qualitative, quarterly review)

---

## 8. Failure Modes & Safeguards

| Failure Mode | How It Manifests | Safeguard |
|---|---|---|
| **Analysis paralysis** | Reading signals daily but never taking action | Track actions-per-week metric; set minimum of 2 actions/week |
| **Premature panic** | One negative company signal triggers immediate job search | Require 2+ corroborating signals before changing job search status |
| **Shiny object syndrome** | Every trending technology triggers a learning detour | Limit to 1 new technology exploration per quarter; finish before starting another |
| **Comp obsession** | Constant salary checking creates dissatisfaction without action | Review benchmarks monthly, not daily; focus on total comp + growth, not just base |
| **Public exposure risk** | "Open to work" signals visible to current employer | Use platform privately; never post public signals until ready |
| **Networking spam** | Outreach volume high but quality low — damages reputation | Cap at 3 outreach messages per week; personalization is mandatory |

---

## 9. Example Scenario Walkthrough

### Scenario: Stack Risk Detected, Turned Into Career Upgrade

**Week 1, Monday** — Developer reviews weekly digest. Signal: "Ruby on Rails job postings declined 18% year-over-year; Elixir/Phoenix postings up 45% in the same category." Signal-to-insight rule fires: "Primary framework declining >15% YoY → Stack risk — invest in adjacent technology."

**Week 1, Wednesday** — Developer doesn't panic. Checks current comp benchmark: $155K for senior Rails engineer. Checks Elixir benchmark: $170K for same experience level. Notes the $15K premium for a related but growing stack.

**Week 1, Saturday** — Starts an Elixir side project. Finds a trending open-source Elixir project on GitHub (800 stars, 30 contributors). Submits a small PR fixing a documentation issue — gets merged and thanked by the maintainer.

**Week 3** — Developer writes a blog post: "What a Rails Engineer Learned Building Their First Elixir Service." Posts to dev.to. Gets picked up by HN (180 points). Platform detects the thought leadership window signal.

**Week 4** — Three inbound recruiter messages arrive, two specifically mentioning the blog post. One is from a company on the developer's target list that just raised Series B (growth phase hiring signal detected 2 weeks earlier).

**Week 5** — Developer responds to the target company recruiter using the leverage email template. Includes current comp benchmark data. Negotiates from a position of strength.

**Week 7** — Offer received: $175K + equity. $20K above previous comp. Developer accepts.

**Result:** Stack risk signal → 7 weeks to career upgrade. The platform didn't find the job — it detected the trend, suggested the investment, and the developer's own actions (contribution, blog post) created the opportunity.
