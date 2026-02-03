# Session 918: Report Provenance and Structured Output

**Date:** February 2, 2026
**Status:** Complete
**PR:** #770

---

## Problem Statement

External feedback (from ChatGPT review) identified that sports and finance reports were making claims without binding them to:
- A data source
- A timestamp
- A freshness window
- A validation state

The review suggested several improvements, some valuable and some overengineered.

---

## What Was Implemented (High Value, Low Risk)

### 1. ReportProvenance Dataclass
Tracks data sources, timestamps, and validation status for every report:

```python
@dataclass
class ReportProvenance:
    report_type: str                    # sports_odds, stock_analysis, etc.
    generated_at_utc: str               # When report was generated
    generated_at_local: str
    agent_name: str
    sources: List[SourceInfo]           # Data sources with timestamps
    max_data_age_hours: float           # Freshness tracking
    validation_status: str              # verified/partially_verified/unverified/stale
    publishable: bool                   # Gate for publishing
    disclaimer: str                     # Legal disclaimer
```

### 2. Structured Output Schemas
JSON schemas alongside markdown for downstream processing:

- **SportsReportSchema**: Games by sport, signals, claims, recommendations, risk flags
- **FinanceReportSchema**: Ticker, scenarios (Bull/Base/Bear), decision drivers, blockers

### 3. Publishing Gates
Reports are marked `publishable: false` if:
- Data freshness exceeds threshold (2h for sports, 24h for finance)
- No data sources tracked
- No records analyzed

### 4. Provenance Header in Reports
Every report now includes a provenance block at the top:

```markdown
---
## Report Provenance

**Generated:** 2026-02-02 15:47:20 (UTC: 2026-02-02 22:47:20 UTC)
**Agent:** SportsOddsAnalyst v1.0
**Data Window:** 2026-02-02 21:47 UTC → 2026-02-02 22:17 UTC

### Data Sources
- **TheOddsSpider**: 25 records (1.0h ago)

**Total Records:** 25
**Max Data Age:** 1.00 hours
**Validation:** PARTIALLY_VERIFIED

**Publishable:** ✅ Yes

*Informational only. Odds must be verified with bookmakers before placing any bets.*

---
```

---

## What Was NOT Implemented (Overengineered)

### 1. "Model Line vs Market Line" Edge Calculation
This assumes we have a predictive model. We don't. We aggregate market data.
Our honest framing: "Market consensus vs outlier book" not "Our model vs market."

### 2. Kelly Sizing / Tiered Unit Recommendations
Requires calibrated probability estimates and historical validation. Without this, unit sizing is theater.

### 3. Scenario Probabilities for Finance
Adding "Bull 30% / Base 50% / Bear 20%" sounds rigorous but those numbers would be vibes, not data.
**Instead:** Qualitative scenario descriptions with explicit assumptions.

### 4. Freshness Grade A/B/C
Unnecessary abstraction. Just show the timestamp and let humans judge.

---

## Files Changed

| File | Changes |
|------|---------|
| `core/agents/report_schemas.py` | NEW - Schema definitions and helpers |
| `core/agents/markets/sports_odds_analyst.py` | Added provenance tracking, structured output |
| `core/agents/stocks/stock_analyst_agent.py` | Added provenance tracking, structured output |

---

## Key Design Decisions

1. **Be honest about data sources** - Track WHERE and WHEN data came from
2. **Don't fake precision** - No fake probabilities or model lines we don't have
3. **Publishing gates** - Automatically flag stale data as unpublishable
4. **JSON alongside markdown** - Enable downstream agent processing
5. **Clear disclaimers** - Every report type has appropriate legal language

---

## Usage

### AgentResult Now Contains

```python
result.data = {
    # ... existing fields ...
    'structured_report': structured_report.to_dict(),
    'provenance': provenance.to_dict(),
    'publishable': True/False,
    'validation_status': 'verified'/'partially_verified'/'unverified'/'stale',
}
```

### Accessing in Downstream Code

```python
# Check if report is safe to publish
if result.data.get('publishable'):
    publish_report(result.message)
else:
    save_as_draft(result.message)
    log_blockers(result.data['provenance']['publish_blockers'])
```

---

## Future Improvements

Once we have sufficient historical data:
1. Track pick outcomes over time
2. Calibrate confidence levels to actual success rates
3. THEN implement quantitative edge calculations

---

**Session 918 establishes the foundation for trustworthy, auditable agent reports.**
