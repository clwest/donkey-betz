"""
Stock Audit Agent Group
=======================

Session 461: Autonomous Stock Market Security & Intelligence Monitoring

Mirrors the Blockchain Audit Agent Group architecture for stock market analysis.

Agents:
- StockAnalystAgent: Analyze SEC filings, fundamentals, valuations
- MarketMovementMonitorAgent: Watch for unusual price/volume movements
- InstitutionalWatcherAgent: Track insider trading & institutional activity
- MarketAnomalyDetectorAgent: Detect pump & dump, unusual options activity
- StockAuditCoordinator: Orchestrate all stock audit agents
"""

from .stock_analyst_agent import StockAnalystAgent
from .market_movement_monitor_agent import MarketMovementMonitorAgent
from .institutional_watcher_agent import InstitutionalWatcherAgent
from .market_anomaly_detector_agent import MarketAnomalyDetectorAgent
from .stock_audit_coordinator import StockAuditCoordinator

__all__ = [
    'StockAnalystAgent',
    'MarketMovementMonitorAgent',
    'InstitutionalWatcherAgent',
    'MarketAnomalyDetectorAgent',
    'StockAuditCoordinator',
]
