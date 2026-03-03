# Stage 3 Rubric Review Runbook

> Weekly quality review process for synthesis outputs during the 14-day pilot.

---

## Review Cadence

- **Frequency:** Weekly (every Monday)
- **Sample size:** 20 syntheses per week (or all if fewer than 20 produced)
- **Reviewer:** Chris (product owner) + Rigby (automated pre-screen)
- **Results stored:** As DeliverableEvents with `event_type='action_taken'` and rubric scores in metadata

---

## Scoring Rubric (1-5 scale)

### Actionability Score

| Score | Definition | Example |
|-------|-----------|---------|
| **5** | Immediately actionable — user can execute within 15 minutes with no additional research | "Fork LiveDash, fix issue #42 (docs typo)" with link |
| **4** | Actionable within 24h — clear next step, minimal research needed | "Write blog post: 'What a Rails Engineer Learned in Elixir'" with outline |
| **3** | Directional — points to an opportunity but requires user judgment on how to act | "Elixir demand is growing 45% YoY" without specific next step |
| **2** | Informational only — interesting data but no clear action path | "Ruby on Rails still has maintenance demand" |
| **1** | Not actionable — vague, unsupported, or wrong audience | "Technology landscape is changing" |

### Quality Dimensions (tracked in metadata, not scored separately)

| Dimension | Pass Criteria |
|-----------|--------------|
| **Signal accuracy** | All cited data points are verifiable or have confidence scores |
| **Role fit** | Synthesis is clearly targeted at the correct role (manager/recruiter/developer) |
| **Timeliness** | Recommendations have a clear time window and aren't stale |
| **Risk awareness** | At least one risk + mitigation is included |
| **No hallucination** | No fabricated companies, projects, or statistics |

---

## Review Process

### Step 1: Rigby Pre-Screen (automated)
Rigby reviews each synthesis for:
- [ ] Has at least 2 signals with confidence scores
- [ ] Has at least 1 recommended action with an owner
- [ ] Has at least 1 risk with mitigation
- [ ] Quality checks section is present and passed
- [ ] Role tag matches content

Syntheses failing pre-screen are flagged as `critical_failure` in metadata.

### Step 2: Human Review (Chris)
For the 20-sample set:
1. Open each synthesis deliverable in Command Center
2. Score actionability 1-5
3. Check quality dimensions (pass/fail each)
4. Flag any critical failures (hallucination, wrong role, dangerous advice)
5. Record scores via `POST /api/deliverables/<id>/event/`:
   ```json
   {
     "event_type": "action_taken",
     "metadata": {
       "review_type": "rubric",
       "actionability_score": 4,
       "signal_accuracy": true,
       "role_fit": true,
       "timeliness": true,
       "risk_awareness": true,
       "no_hallucination": true,
       "critical_failure": false,
       "reviewer": "chris",
       "notes": "optional free text"
     }
   }
   ```

### Step 3: Weekly Summary
Rigby generates a weekly rubric summary:
- Mean actionability score
- Pass rate per quality dimension
- Critical failure count
- Trend vs. previous week
- Recommendations for template/playbook iteration

---

## Stage Gate Thresholds

| Metric | Pass | Conditional | Fail |
|--------|------|-------------|------|
| Mean actionability score | >= 4.0 | >= 3.5 | < 3.5 |
| Critical failures (per 20) | <= 1 | 2 | >= 3 |
| Role fit pass rate | >= 90% | >= 80% | < 80% |
| Signal accuracy pass rate | >= 85% | >= 75% | < 75% |

---

## Iteration Protocol

If a quality dimension consistently fails:
1. Identify which template section is producing the failure
2. Update the synthesis template schema with tighter constraints
3. Update the relevant playbook with clearer signal-to-insight rules
4. Re-run affected syntheses and re-score
5. Document changes in the next weekly summary
