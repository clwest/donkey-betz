"""
Stock Audit Agent Group + Market Intelligence Desk
===================================================

Session 461: Autonomous Stock Market Security & Intelligence Monitoring
Session 462: Market Intelligence Desk - First Tier 1 Autonomous Situation

All agents in this module work together to:
1. Detect market anomalies, insider trading, price manipulation
2. Run bull vs bear debate for internal disagreement
3. Generate daily market intelligence briefs
4. Self-renew and track changes over time

Stock Audit Agents:
- StockAnalystAgent: Analyze SEC filings, fundamentals, valuations
- MarketMovementMonitorAgent: Watch for unusual price/volume movements
- InstitutionalWatcherAgent: Track insider trading & institutional activity
- MarketAnomalyDetectorAgent: Detect pump & dump, unusual options activity
- StockAuditCoordinator: Orchestrate all stock audit agents

Market Intelligence Desk Agents (NEW - Session 462):
- BullCaseAgent: Argues why stocks should go UP
- BearCaseAgent: Argues why stocks should go DOWN
- MarketIntelligenceCoordinator: Orchestrates debate, generates daily brief
"""

from .stock_analyst_agent import StockAnalystAgent
from .market_movement_monitor_agent import MarketMovementMonitorAgent
from .institutional_watcher_agent import InstitutionalWatcherAgent
from .market_anomaly_detector_agent import MarketAnomalyDetectorAgent
from .stock_audit_coordinator import StockAuditCoordinator, run_stock_audit_cycle

# Session 462: Market Intelligence Desk
from .bull_case_agent import BullCaseAgent
from .bear_case_agent import BearCaseAgent
from .market_intelligence_coordinator import MarketIntelligenceCoordinator, run_market_intelligence_desk

__all__ = [
    # Stock Audit System
    'StockAnalystAgent',
    'MarketMovementMonitorAgent',
    'InstitutionalWatcherAgent',
    'MarketAnomalyDetectorAgent',
    'StockAuditCoordinator',
    'run_stock_audit_cycle',

    # Market Intelligence Desk (Session 462)
    'BullCaseAgent',
    'BearCaseAgent',
    'MarketIntelligenceCoordinator',
    'run_market_intelligence_desk',
]
