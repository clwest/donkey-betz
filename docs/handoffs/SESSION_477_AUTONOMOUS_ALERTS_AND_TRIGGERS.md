# Session 477: Autonomous Alerts & Event-Driven Triggers

**Date:** December 17, 2025
**Status:** COMPLETE
**Commits:**
- `3596fbb` - Part 1: Tier 1 Autonomous Situations (Scheduled)
- `45f3f95` - Part 2: Event-Driven Situation Triggers

---

## Overview

Session 477 built a complete autonomous alerting system for Blockchain Security and Stock Market Intelligence. The system operates in two modes:

1. **Scheduled Monitoring** (Part 1) - Comprehensive analysis every 2-4 hours
2. **Event-Driven Triggers** (Part 2) - Immediate alerts when spider data matches conditions

---

## Part 1: Scheduled Autonomous Alerts

### Models Created

**BlockchainSecurityAlert** (`core/models_autonomous_alerts.py`)
- Alert types: whale_movement, suspicious_tx, contract_exploit, flash_loan, rug_pull, etc.
- Severity levels: critical, high, medium, low
- Fields: chain, address, token_symbol, value_usd, confidence_score, risk_score
- Discord integration fields: discord_sent, discord_message_id

**BlockchainMonitoringSession**
- Tracks each monitoring cycle
- Stats: spider_data_processed, transactions_analyzed, alerts_generated
- Timing: started_at, completed_at, next_session_scheduled

**StockMarketAlert**
- Alert types: earnings_surprise, analyst_upgrade/downgrade, insider_trading, etc.
- Fields: symbol, company_name, price_change_percent, volume_ratio
- Market context: market_cap, sector, market_sentiment

**StockMonitoringSession**
- Similar tracking to blockchain sessions
- Stats: stocks_analyzed, filings_reviewed, news_processed

### Celery Tasks

```python
# Runs every 2 hours
@shared_task
def run_blockchain_security_monitor():
    """Comprehensive blockchain security analysis."""

# Runs every 4 hours
@shared_task
def run_stock_market_intelligence():
    """Stock market analysis with bull/bear debate."""
```

### Celery Beat Schedules

```python
'blockchain-security-monitor': {
    'task': 'core.tasks.run_blockchain_security_monitor',
    'schedule': crontab(minute=0, hour='*/2'),  # Every 2 hours
},
'stock-market-intelligence': {
    'task': 'core.tasks.run_stock_market_intelligence',
    'schedule': crontab(minute=30, hour='*/4'),  # Every 4 hours
},
```

---

## Part 2: Event-Driven Situation Triggers

### The Problem

Scheduled monitoring has a gap: if a whale moves 1000 ETH at 10:05 AM, users won't know until the next scheduled run at 12:00 PM. That's nearly 2 hours of delay.

### The Solution

Event-driven triggers evaluate spider data **immediately** when it arrives and fire alerts within seconds.

### Models Created

**SituationTrigger** (`core/models_situation_triggers.py`)
```python
class SituationTrigger(models.Model):
    name = models.CharField(max_length=100)
    situation_type = models.CharField(choices=SituationType.choices)  # blockchain/stock_market/both
    trigger_type = models.CharField(choices=TriggerType.choices)
    target_spiders = models.JSONField(default=list)  # Which spiders to monitor
    target_field = models.CharField(max_length=100)  # JSON path like 'items.0.value'
    operator = models.CharField(choices=TriggerOperator.choices)  # gt, lt, contains, regex
    threshold_value = models.CharField(max_length=200)
    severity = models.CharField(choices=[...])
    cooldown_minutes = models.IntegerField(default=30)
    priority = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
```

**TriggerEvent**
```python
class TriggerEvent(models.Model):
    trigger = models.ForeignKey(SituationTrigger, ...)
    spider_data = models.ForeignKey('core.SpiderData', ...)
    matched_field = models.CharField(max_length=100)
    matched_value = models.CharField(max_length=500)
    raw_data_snapshot = models.JSONField(default=dict)
    alert_generated = models.BooleanField(default=False)
    alert_id = models.UUIDField(null=True)
    discord_sent = models.BooleanField(default=False)
    status = models.CharField(choices=[pending, processing, completed, failed, skipped])
```

### Signal Handler

```python
# core/signals/trigger_signals.py

@receiver(post_save, sender='core.SpiderData')
def on_spider_data_created(sender, instance, created, **kwargs):
    """Evaluate triggers when new spider data arrives."""
    if not created:
        return
    transaction.on_commit(
        lambda: evaluate_triggers_for_spider_data(instance)
    )
```

### Data Flow

```
Spider collects data
       ↓
SpiderData.objects.create()
       ↓
Django post_save signal fires
       ↓
on_spider_data_created() handler
       ↓
evaluate_triggers_for_spider_data()
       ↓
For each active trigger:
  - Check if spider matches target_spiders
  - Extract value from target_field (supports nested JSON paths)
  - Evaluate condition (operator + threshold)
       ↓
If match found:
  - Create TriggerEvent
  - Update trigger stats (total_fires, last_triggered_at)
       ↓
Queue Celery task: process_trigger_events([event_ids])
       ↓
process_trigger_events():
  - Create BlockchainSecurityAlert or StockMarketAlert
  - Send Discord notification
  - Update TriggerEvent status
```

### Default Triggers (11 Pre-configured)

| Name | Type | Target | Field | Operator | Threshold | Cooldown |
|------|------|--------|-------|----------|-----------|----------|
| Whale Movement (100+ ETH) | whale_movement | etherscan* | value | gt | 100 | 15 min |
| Mega Whale (1000+ ETH) | whale_movement | etherscan* | value | gt | 1000 | 5 min |
| Price Crash (>10% Drop) | price_crash | coingecko | price_change_percentage_24h | lt | -10 | 30 min |
| Severe Crash (>20% Drop) | price_crash | coingecko | price_change_percentage_24h | lt | -20 | 15 min |
| Exploit/Hack Keywords | exploit_keyword | hackernews, reddit | title | contains | exploit\|hack\|rug pull | 60 min |
| Stock Mover (>5% Change) | stock_mover | yahoo_finance | regularMarketChangePercent | gt | 5 | 30 min |
| Major Stock Move (>10%) | stock_mover | yahoo_finance | regularMarketChangePercent | gt | 10 | 15 min |
| Stock Crash (>5% Drop) | stock_mover | yahoo_finance | regularMarketChangePercent | lt | -5 | 30 min |
| SEC Filing (13F/13D) | sec_filing | sec_edgar | form | contains | 13F\|13D\|8-K | 60 min |
| Breaking Market News | breaking_news | business_news | title | contains | crash\|surge\|plunge | 30 min |
| Fed/Interest Rate News | breaking_news | business_news | title | contains | fed\|interest rate | 60 min |

### Operators Supported

- `gt` - Greater than (numeric)
- `gte` - Greater than or equal
- `lt` - Less than
- `lte` - Less than or equal
- `eq` - Equal to
- `neq` - Not equal to
- `contains` - Text contains (supports `|` for multiple keywords)
- `regex` - Regular expression match

### JSON Path Extraction

The `target_field` supports dot notation for nested data:
- `value` - Direct field access
- `items.0.value` - First item in array
- `data.price.current` - Nested object

---

## Files Created/Modified

### Part 1
- `core/models_autonomous_alerts.py` (469 lines) - NEW
- `core/tasks.py` (+405 lines) - Scheduled tasks
- `core/celery.py` (+28 lines) - Beat schedules
- `core/services/discord_notifications.py` (+237 lines) - Alert methods

### Part 2
- `core/models_situation_triggers.py` (555 lines) - NEW
- `core/signals/__init__.py` - NEW
- `core/signals/trigger_signals.py` (150 lines) - NEW
- `core/learning_bridges/apps.py` (+10 lines) - Signal connection
- `core/models.py` (+3 lines) - Import triggers

### Migration
- `core/migrations/0106_session_477_autonomous_alerts.py`
- `core/migrations/0108_session_477_situation_triggers.py`

---

## Testing

### Scheduled Alerts Test
```bash
# Run blockchain monitor manually
.venv/bin/python manage.py shell -c "
from core.tasks import run_blockchain_security_monitor
run_blockchain_security_monitor()
"
```

### Event-Driven Trigger Test
```python
# Create spider data that matches a trigger
from core.models import SpiderData

SpiderData.objects.create(
    spider_name='coingecko',
    source_url='https://api.coingecko.com/test',
    data_type='cryptocurrency',
    raw_data={
        'items': [{
            'symbol': 'TEST',
            'price_change_percentage_24h': -15.5,  # Triggers "Price Crash"
        }]
    }
)
# Signal fires automatically, creates TriggerEvent, queues alert
```

### Verify Trigger Events
```bash
DATABASE_URL=postgresql://postgres@localhost:5432/unified_donkey_betz \
.venv/bin/python manage.py shell -c "
from core.models_situation_triggers import TriggerEvent
for e in TriggerEvent.objects.all()[:5]:
    print(f'{e.trigger.name}: {e.matched_value} - {e.status}')
"
```

---

## Discord Channels

Alerts are sent to dedicated Discord channels:
- `#blockchain-alerts` - Blockchain security alerts
- `#stock-alerts` - Stock market alerts
- `#system-status` - Monitoring session summaries

---

## The 5 Autonomous Properties

This system implements all 5 properties of a Tier 1 Autonomous Situation:

1. **Persistent Context** - Sessions and events stored in database
2. **Incoming Signals** - Spider network feeds real-time data
3. **Internal Disagreement** - Bull vs Bear agents debate (stock alerts)
4. **Outputs with Consequences** - Alerts affect trading decisions
5. **Self-Renewal** - Scheduled tasks + event triggers run forever

---

## Next Steps (Session 478+)

1. Add trigger management Discord commands (`/trigger-list`, `/trigger-create`)
2. Add trigger analytics dashboard
3. Implement trigger chaining (one trigger can activate another)
4. Add user-specific triggers (personalized alerts)
5. Machine learning to auto-tune thresholds based on false positive rate
