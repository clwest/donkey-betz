# Content Calendar Process

**Category:** Marketing
**Last Updated:** January 24, 2026
**Owner:** ContentStrategyAgent

---

## Overview

This playbook defines the process for planning, creating, and managing content across all channels. It ensures consistent output and strategic alignment with business goals.

---

## Content Pillars

### Primary Pillars
1. **Educational** - How-to guides, tutorials, explanations
2. **Thought Leadership** - Industry insights, predictions, opinions
3. **Product Updates** - Features, releases, improvements
4. **Community** - User stories, case studies, engagement

### Content Mix (Monthly)
| Pillar | Percentage | Pieces |
|--------|------------|--------|
| Educational | 40% | 8 |
| Thought Leadership | 25% | 5 |
| Product Updates | 20% | 4 |
| Community | 15% | 3 |

---

## Planning Cycle

### Monthly Planning (First Monday)

```
Agent: ContentStrategyAgent
Tasks:
1. Review previous month performance
2. Identify trending topics
3. Align with product roadmap
4. Generate content ideas
5. Assign to content pillars
6. Create draft calendar
```

#### Planning Meeting Agenda
- [ ] Review last month's metrics
- [ ] Discuss upcoming product releases
- [ ] Review spider insights for trends
- [ ] Brainstorm content ideas
- [ ] Assign priorities and dates
- [ ] Identify resource needs

### Weekly Review (Every Friday)

```
Agent: ContentStrategyAgent
Tasks:
1. Review week's published content
2. Check engagement metrics
3. Adjust next week if needed
4. Flag any blockers
```

---

## Content Creation Workflow

### Stage 1: Ideation (Day 1)

```
Agent: ResearchAgent
Output:
- Topic brief
- Target keywords
- Competitor analysis
- Audience insights
```

### Stage 2: Outline (Day 2)

```
Agent: ContentWriterAgent
Output:
- Content structure
- Key points
- Sources to cite
- CTA placement
```

### Stage 3: Draft (Days 3-4)

```
Agent: ContentWriterAgent
Output:
- Full draft
- Meta description
- Social snippets
```

### Stage 4: Review (Day 5)

```
Gate: Human Review Required
Checklist:
- [ ] Factual accuracy
- [ ] Brand voice consistency
- [ ] SEO optimization
- [ ] Grammar/spelling
- [ ] Links working
```

### Stage 5: Publish (Day 6)

```
Agent: SocialMediaAgent
Tasks:
- Schedule publication
- Create social posts
- Set up tracking
```

---

## Channel Strategy

### Blog (2x/week)
- **Day:** Tuesday, Thursday
- **Time:** 9 AM EST
- **Length:** 1,500-2,500 words
- **Format:** Long-form educational

### Newsletter (1x/week)
- **Day:** Wednesday
- **Time:** 10 AM EST
- **Length:** 500-800 words
- **Format:** Curated + original

### Social Media (Daily)
| Platform | Frequency | Best Time |
|----------|-----------|-----------|
| Twitter/X | 3-5x/day | 9 AM, 12 PM, 5 PM |
| LinkedIn | 1x/day | 8 AM, 12 PM |
| Discord | Continuous | -- |

### YouTube (1x/week)
- **Day:** Saturday
- **Time:** 10 AM EST
- **Length:** 8-15 minutes
- **Format:** Tutorial/explainer

### Podcast (2x/month)
- **Day:** 1st and 15th
- **Time:** 6 AM EST
- **Length:** 30-45 minutes
- **Format:** Interview/discussion

---

## Content Templates

### Blog Post Template
```markdown
# [Title - Include Primary Keyword]

[Hook paragraph - problem/question]

## [Section 1 - What/Why]

[Content]

## [Section 2 - How]

[Content with steps]

## [Section 3 - Examples]

[Real examples]

## Conclusion

[Summary + CTA]

---

*[Author bio]*
```

### Social Post Templates

**Twitter/X:**
```
[Hook - question or bold statement]

[Key insight - 1-2 sentences]

[CTA or link]
```

**LinkedIn:**
```
[Personal hook]

[Story/insight - 3-4 paragraphs]

[Lesson learned]

[Question for engagement]

#hashtags
```

---

## Metrics & KPIs

### Weekly Metrics
| Metric | Target |
|--------|--------|
| Blog views | 5,000 |
| Newsletter opens | 35% |
| Social engagement | 500 |
| New subscribers | 100 |

### Monthly Metrics
| Metric | Target |
|--------|--------|
| Organic traffic | 20,000 |
| Email list growth | 400 |
| Social followers | 500 |
| Backlinks | 10 |

---

## Tools & Resources

### AI Agents
| Agent | Use Case |
|-------|----------|
| ResearchAgent | Topic research, keyword analysis |
| ContentWriterAgent | Draft creation, editing |
| SEOOptimizerAgent | SEO optimization |
| SocialMediaAgent | Social scheduling |
| ImageAgent | Graphics, thumbnails |

### Platforms
- **CMS:** Django Admin / Custom
- **Email:** (TBD)
- **Social:** Buffer/Hootsuite
- **Analytics:** Google Analytics 4
- **SEO:** Ahrefs/SEMrush

---

## Content Approval Matrix

| Content Type | Approval Level |
|--------------|----------------|
| Blog post | Marketing Lead |
| Product announcement | Product + Marketing |
| Press release | Executive |
| Partnership content | Legal + Marketing |
| User-generated | Community Manager |

---

## Emergency Content Protocol

### Crisis Response
1. Pause scheduled content
2. Assess situation
3. Draft response (if needed)
4. Get executive approval
5. Coordinate across channels
6. Monitor reactions

### Breaking News
1. Verify information
2. Quick take draft (< 1 hour)
3. Fast approval track
4. Publish across channels
5. Follow up with deeper content

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-24 | 1.0 | Initial playbook |
