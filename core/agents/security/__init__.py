"""
Security Agents Package - Clean Architecture
=============================================

Session 280: Phase 3 - Agent Architecture Unification

Security agents for memory isolation and data protection.

Usage:
    from core.agents.security import MemoryIsolationAgent

    agent = MemoryIsolationAgent(user=request.user)
    result = agent.execute(
        task="Audit memory systems for cross-contamination",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

from core.agents.security.memory_isolation_agent import MemoryIsolationAgent

__all__ = [
    'MemoryIsolationAgent',
]
