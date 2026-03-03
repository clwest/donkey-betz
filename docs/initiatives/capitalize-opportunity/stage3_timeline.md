# Stage 3 Timeline — Capitalize Opportunity

> 14-day pilot window with defined checkpoints and decision gates.

---

## Key Dates

| Milestone | Date | Owner |
|-----------|------|-------|
| **Pilot start** | 2026-03-04 (Tuesday) | Chris |
| **Midpoint check-in** | 2026-03-11 (Tuesday) | Chris + Rigby |
| **Final readout** | 2026-03-18 (Tuesday) | Chris |
| **Stage 3 gate decision** | 2026-03-18 | Chris |

---

## Daily Pulse (automated, every day)

Rigby's ops digest includes:
- Syntheses generated in last 24h
- ATR-24h rate (overall + by role)
- Any critical failures detected
- Event count by type

No human action needed unless ATR-24h drops below 15% (Rigby alerts Chris).

---

## Midpoint Check-in (Day 7 — March 11)

### Agenda
1. **ATR-24h review:** Is overall rate tracking toward >= 25%?
2. **Role breakdown:** Any role below 15%? Root cause?
3. **Rubric scores:** First week's 20-sample review results
4. **Template iteration:** Any changes needed based on early data?
5. **Go/no-go for second week:** Continue as-is, iterate, or pause?

### Decision Options
- **Continue:** Data is on track, no changes needed
- **Iterate:** Adjust templates/playbooks based on findings, continue pilot
- **Pause:** Fundamental issues require rethinking before proceeding

---

## Final Readout (Day 14 — March 18)

### Deliverables for Readout
1. **ATR-24h dashboard screenshot** (overall + by role)
2. **Rubric summary** (2-week aggregate: mean score, dimension pass rates, critical failures)
3. **Funnel analysis** (generated → viewed → saved → acted)
4. **Top-performing templates/agents** (which produced highest ATR)
5. **Recommendation:** advance to Stage 4 or iterate

### Stage 3 Gate Decision

| Outcome | Criteria | Next Step |
|---------|----------|-----------|
| **APPROVED** | ATR >= 25% overall, >= 15% per role, rubric >= 4.0, <= 2 critical failures | Advance to Stage 4 |
| **CONDITIONAL** | ATR >= 25% overall, one role below 15%, rubric >= 3.5 | Fix failing role, re-check in 7 days |
| **FAILED** | ATR < 20% overall, or 2+ roles < 10%, or >= 3 critical failures | Iterate on templates/playbooks, re-run Stage 3 |

---

## Stage 4 Preview (if approved)

Stage 4 = **Scale & Optimize**
- Expand pilot to additional initiative types (not just talent/career)
- Automate synthesis generation from live spider signals
- Build feedback loop: user actions feed back into signal weighting
- Target: 50+ syntheses/week with maintained ATR >= 25%
