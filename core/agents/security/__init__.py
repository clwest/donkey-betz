"""
Security Agents Package - Clean Architecture
=============================================

Session 280: Phase 3 - Agent Architecture Unification
Session 295: Added ContentAuditAgent for bias/ethics transparency

Security agents for memory isolation, data protection, and content safety.

Usage:
    from core.agents.security import MemoryIsolationAgent, ContentAuditAgent

    # Memory isolation
    agent = MemoryIsolationAgent(user=request.user)
    result = agent.execute(...)

    # Content audit for bias/ethics
    agent = ContentAuditAgent(user=request.user)
    result = agent.execute(
        task="Audit this prompt for bias: 'A beautiful exotic woman'",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

from core.agents.security.memory_isolation_agent import MemoryIsolationAgent
from core.agents.security.content_audit_agent import ContentAuditAgent

__all__ = [
    'MemoryIsolationAgent',
    'ContentAuditAgent',
]
