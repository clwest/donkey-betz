# Session 461: Phase 3 - Advisor Intelligence Complete

**Date:** December 16, 2025
**Focus:** Activating advisor intelligence with auto-consultation, spider data access, and outcome learning

---

## Summary

Completed Phase 3 of the SYSTEM_FULL_ACTIVATION_PLAN which focused on making advisors smarter:

1. **Auto-Consultation for High-Risk Findings** - Advisors are now automatically consulted when audit coordinators detect critical alerts
2. **Advisor Spider Data Access** - Each advisor now receives fresh intelligence from their domain-specific spiders
3. **Advisor Learning from Outcomes** - System tracks consultation accuracy to improve advisor selection over time

---

## Changes Made

### 1. StockAuditCoordinator (`core/agents/stocks/stock_audit_coordinator.py`)

Added `_request_advisor_consultations()` method:
- Auto-consults Warren Buffett for CRITICAL/HIGH severity stock alerts
- Limited to 3 consultations per cycle (cost control)
- Adds `advisor_perspective` to each alert
- Tracks consultations for learning

### 2. BlockchainAuditCoordinator (`core/agents/blockchain/blockchain_audit_coordinator.py`)

Added `_request_blockchain_advisor_consultation()` method:
- Auto-consults Elon Musk for high-risk blockchain alerts
- Returns consultation in security report data
- Tracks consultations for learning

### 3. LLMAdvisor System (`advisors/llm_advisor_system.py`)

New features:
- `ADVISOR_DOMAIN_SPIDERS` mapping (13 domains → spider lists)
- `_get_domain_spider_intelligence()` method fetches relevant spider data
- Modified `_build_advisor_prompt()` to inject fresh intelligence

Domain mappings:
```python
ADVISOR_DOMAIN_SPIDERS = {
    'investing': ['yahoo_finance', 'coindesk', 'financial_news', ...],
    'value_investing': ['yahoo_finance', 'financial_news', 'sec_filings', ...],
    'tech_investing': ['techcrunch', 'the_verge', 'wired', 'axios', ...],
    'crypto': ['coindesk', 'cryptonews', 'etherscan_api', ...],
    'tech': ['techcrunch', 'the_verge', 'wired', 'mit_tech_review', ...],
    # ... 8 more domains
}
```

### 4. AdvisorFeedbackBridge (`core/learning_bridges/advisor_feedback_bridge.py`)

Added `AutoConsultationLearningLoop` class:
- `_get_system_user()`: Creates system user for anonymous tracking
- `track_auto_consultation()`: Records consultations with severity, type, response
- `record_outcome()`: Records whether predictions were correct
- `get_advisor_accuracy_stats()`: Returns accuracy metrics

Convenience function:
```python
from core.learning_bridges.advisor_feedback_bridge import track_audit_advisor_consultation

track_audit_advisor_consultation({
    'advisor': 'Warren Buffett (AI)',
    'ticker': 'AAPL',
    'severity': 'HIGH',
    'alert_type': 'stock_audit',
    'response': response_text,
    'confidence': 0.8,
})
```

### 5. Documentation (`docs/plans/SYSTEM_FULL_ACTIVATION_PLAN.md`)

- Marked Phase 3 as COMPLETED
- Added detailed implementation notes
- Updated success metrics (advisor utilization: 25% → 50%)
- Updated Quick Reference with completed items

---

## How It Works

### Auto-Consultation Flow

```
StockAuditCoordinator.execute()
    ↓
_run_all_sub_agents()
    ↓
_correlate_findings()
    ↓
_generate_unified_alerts()
    ↓
_request_advisor_consultations()  ← NEW
    │
    ├── Filter alerts: CRITICAL/HIGH only
    ├── Get Warren Buffett advisor
    ├── Build question from alert details
    ├── LLMAdvisorSystem.consult()
    │       │
    │       └── _get_domain_spider_intelligence()  ← NEW
    │               │
    │               └── Inject fresh financial spider data
    │
    ├── Add advisor_perspective to alerts
    └── track_audit_advisor_consultation()  ← NEW
            │
            └── Store in UserAgentLearning
```

### Learning Flow

```
Consultation Created
    ↓
track_audit_advisor_consultation()
    ↓
UserAgentLearning record created
    │
    ├── total_consultations: +1
    ├── by_alert_type: {stock_audit: 1}
    ├── by_severity: {HIGH: 1}
    └── recent_consultations: [{...}]

Later, when outcome known:
    ↓
record_outcome(advisor, ticker, was_correct)
    ↓
    ├── outcomes_tracked: +1
    ├── correct_predictions: +1 (if correct)
    └── accuracy: correct/tracked
```

---

## Testing

```bash
# Test advisor spider intelligence
.venv/bin/python -c "
from advisors.llm_advisor_system import LLMAdvisor

profile = {'name': 'Test', 'domain': 'investing', ...}
advisor = LLMAdvisor(profile)
intel = advisor._get_domain_spider_intelligence('AI stocks')
print(f'Found {len(intel)} items')
"

# Test auto-consultation tracking
.venv/bin/python -c "
from core.learning_bridges.advisor_feedback_bridge import (
    track_audit_advisor_consultation,
    auto_consultation_learning
)

consultation = {'advisor': 'Warren Buffett (AI)', 'ticker': 'TEST', ...}
track_audit_advisor_consultation(consultation)

stats = auto_consultation_learning.get_advisor_accuracy_stats('Warren Buffett')
print(stats)
"
```

---

## Files Changed

| File | Changes |
|------|---------|
| `core/agents/stocks/stock_audit_coordinator.py` | Added _request_advisor_consultations() |
| `core/agents/blockchain/blockchain_audit_coordinator.py` | Added _request_blockchain_advisor_consultation() |
| `advisors/llm_advisor_system.py` | Added spider data access + domain mappings |
| `core/learning_bridges/advisor_feedback_bridge.py` | Added AutoConsultationLearningLoop |
| `docs/plans/SYSTEM_FULL_ACTIVATION_PLAN.md` | Marked Phase 3 complete |

---

## Next Session

Remaining work from SYSTEM_FULL_ACTIVATION_PLAN:

**Phase 4: Cross-Domain Correlation**
- Stock/crypto correlation detection
- Multi-source opportunity scoring
- Prophecy generation system

**Quick Wins:**
- Create `/validate` Discord command
- Add Discord alerts for critical mythology events
- Create auto-verification Celery task
