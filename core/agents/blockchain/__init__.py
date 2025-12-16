"""
Blockchain Audit Agent Group
============================

Session 461: Autonomous blockchain security monitoring

This package contains specialized agents for blockchain security:
- SmartContractAuditorAgent: Audit Solidity code for vulnerabilities
- TransactionMonitorAgent: Watch for suspicious transaction patterns
- WhaleWatcherAgent: Track large token movements
- ExploitDetectorAgent: Pattern match known exploit signatures
- BlockchainAuditCoordinator: Orchestrate all audit agents

Usage:
    from core.agents.blockchain import (
        SmartContractAuditorAgent,
        TransactionMonitorAgent,
        WhaleWatcherAgent,
        ExploitDetectorAgent,
        BlockchainAuditCoordinator,
    )
"""

from .smart_contract_auditor_agent import SmartContractAuditorAgent
from .transaction_monitor_agent import TransactionMonitorAgent
from .whale_watcher_agent import WhaleWatcherAgent
from .exploit_detector_agent import ExploitDetectorAgent
from .blockchain_audit_coordinator import BlockchainAuditCoordinator

__all__ = [
    'SmartContractAuditorAgent',
    'TransactionMonitorAgent',
    'WhaleWatcherAgent',
    'ExploitDetectorAgent',
    'BlockchainAuditCoordinator',
]
