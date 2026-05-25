<!-- DOC-POINTER-V1 -->
> **⚠ HISTORICAL PLAN (Q4 2025 / Q1 2026 build phase).** Drafted during platform build-out; may be partially shipped, renamed in code, or quietly superseded. Preserved for historical reference, not current truth. For current truth see [`docs/INDEX.md`](../INDEX.md) + [`PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) + the latest handoff. See [`docs/plans/INDEX.md`](INDEX.md) for directory scope.

# SYSTEM INTELLIGENCE OPERATING GROUP  
## Autonomous Stock Market Audit & Intelligence System

**Status:** DESIGN LOCKED  
**Purpose:** Enable fully autonomous stock market monitoring, anomaly detection, and intelligence alerts using existing agent, spider, and orchestration infrastructure.

---

## WHY THIS EXISTS

We already have:
- Autonomous intelligence loops
- Agent orchestration
- Spider networks
- Discord alerting
- Cross-agent debate and learning

What we *lack* are **domain-specific operating groups** that continuously run on their own and create infinite situations, signals, and conversations.

This document defines the **Stock Audit Agent Group** as a reusable operating pattern that other domains (Blockchain, Real Estate, Legal, Cybersecurity, etc.) will follow.

---

## SYSTEM GOAL

Create a **24/7 autonomous stock intelligence system** that:

- Monitors markets continuously
- Detects suspicious activity (insider trading, pump & dump, abnormal volume)
- Analyzes SEC filings and institutional behavior
- Correlates signals across multiple data sources
- Produces actionable alerts without human input
- Feeds findings back into the learning loop

---

## HIGH-LEVEL ARCHITECTURE

---

## AGENT DEFINITIONS

### 1. StockAnalystAgent
**Role:** Deep analysis of company fundamentals and filings

**Responsibilities:**
- Analyze SEC filings (10-K, 10-Q, 8-K)
- Assess valuation metrics
- Compare peers
- Identify financial red flags

**Core Tools:**
- `analyze_filing()`
- `check_valuation()`
- `compare_peers()`
- `assess_risk()`

---

### 2. MarketMovementMonitorAgent
**Role:** Detect unusual price and volume activity

**Responsibilities:**
- Monitor price spikes
- Track abnormal volume
- Detect momentum anomalies
- Flag unexplained movements

**Core Tools:**
- `detect_volume_spike()`
- `track_momentum()`
- `alert_breakout()`

---

### 3. InstitutionalWatcherAgent
**Role:** Track large players and insider behavior

**Responsibilities:**
- Monitor Form 4 insider trades
- Track 13F institutional filings
- Identify large position changes
- Flag suspicious timing

**Core Tools:**
- `monitor_insiders()`
- `track_13f_filings()`
- `alert_large_position()`

---

### 4. MarketAnomalyDetectorAgent
**Role:** Identify manipulation and coordinated activity

**Responsibilities:**
- Detect pump-and-dump patterns
- Analyze unusual options flow
- Identify coordinated trading behavior
- Cross-reference anomalies across markets

**Core Tools:**
- `detect_pump_dump()`
- `analyze_options_flow()`
- `flag_manipulation()`

---

## COORDINATOR

### StockAuditCoordinator
**Role:** Orchestrates the entire operating group

**Responsibilities:**
- Receive findings from all agents
- Correlate multi-source signals
- Assign alert severity
- Decide when to escalate
- Trigger alerts and memory logging

---

## SPIDER NETWORK

### Existing / Extended Spiders

| Spider | Source | Purpose |
|------|-------|--------|
| SECEdgarSpider | SEC EDGAR | Filings, insider trades |
| YahooFinanceSpider | Yahoo Finance | Price, volume, fundamentals |
| FinvizSpider | Finviz | Screener data, insider activity |

Spiders **only collect data**.  
Agents **interpret meaning**.

---

## AUTONOMOUS LOOP INTEGRATION

This operating group plugs into the existing autonomous intelligence loop.

**New loop method:**
```python
check_stock_security()

Execution cadence:
	•	Runs every 15 minutes via Celery Beat
	•	Fully unattended
	•	No manual triggers required

⸻

ALERT SEVERITY MODEL
Severity
Trigger Example
CRITICAL
CEO sells 40–50% stake before earnings
HIGH
Massive unusual options activity
MEDIUM
Stock moves +20% with no news
LOW
Informational filing or position change


DISCORD OUTPUT FORMAT
📈 STOCK ALERT
━━━━━━━━━━━━━━━━━━━━━━
Severity: HIGH
Type: Insider Trading Activity

Company: ACME Corp (ACME)
Insider: John Smith (CEO)
Action: SELL
Shares: 500,000
Value: $12.5M
Filed: 2 hours ago

Analysis:
This represents ~40% of CEO holdings.
Recent guidance was mixed.
Pattern matches prior pre-earnings sell-offs.

🔗 Source: SEC EDGAR

FILE STRUCTURE (EXPECTED)

core/
 └─ agents/
    └─ stocks/
       ├─ stock_analyst_agent.py
       ├─ market_movement_monitor_agent.py
       ├─ institutional_watcher_agent.py
       ├─ market_anomaly_detector_agent.py
       ├─ stock_audit_coordinator.py
       └─ __init__.py

ai_core/
 └─ spiders/
    └─ specialized/
       └─ finviz_spider.py

DESIGN PRINCIPLES
	•	Agents never scrape
	•	Spiders never analyze
	•	Coordinators never hallucinate
	•	Alerts require correlation
	•	Everything feeds memory
	•	No human required to run

⸻

WHY THIS MATTERS

This system:
	•	Creates infinite autonomous scenarios
	•	Generates internal debates between agents
	•	Produces continuous intelligence value
	•	Scales horizontally into new domains
	•	Turns the platform into a living organism

This is not a feature.
This is an operating group pattern.

Once this exists, duplicating it for:
	•	Blockchain
	•	Cybersecurity
	•	Real estate
	•	Legal intelligence
	•	Geopolitics

…becomes trivial.

⸻

NEXT DOMAINS TO CLONE THIS PATTERN
	•	Blockchain Audit Agents ✅
	•	Crypto Fraud Detection
	•	Government Contract Monitoring
	•	Corporate Risk Intelligence
	•	Legal Abuse Pattern Detection

⸻
