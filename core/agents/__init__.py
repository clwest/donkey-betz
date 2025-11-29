"""
Clean Architecture Agents Package
==================================

Session 268: Phase 1 - Foundation

This package contains the new clean architecture agents.
Each agent is isolated and has access ONLY to its domain-specific tools.

Architecture:
    User → Personal Assistant → Agent Router → Specialized Agents → Tools

Key Principles:
1. Each agent has ONLY its own tools (e.g., ImageAgent cannot generate video)
2. Agents receive sci-fi context (mood, memory, evolution) for rich behavior
3. Agents receive spider context (trends, market data) for informed decisions
4. All agents inherit TimeTravelMixin for debugging/replay

Usage:
    from core.agents import ImageAgent, AgentRouter

    router = AgentRouter()
    result = router.route("ImageAgent", "create a cyberpunk logo", context={})

Available Agents (Phase 1):
    - ImageAgent: Image generation ONLY

Coming in Phase 2:
    - VideoAgent: Video generation ONLY
    - AudioAgent: Audio generation ONLY
    - ThreeDAgent: 3D model generation ONLY
    - ImageEditingAgent: Image editing ONLY
    - VideoEditingAgent: Video editing ONLY
    - ResearchAgent: Web + spider search ONLY
    - WorkflowAgent: Orchestration (can delegate to other agents)
    - HiveMindAgent: Multi-agent synthesis
"""

from core.agents.base_agent import BaseAgent, AgentResult
from core.agents.image_agent import ImageAgent

__all__ = [
    'BaseAgent',
    'AgentResult',
    'ImageAgent',
]
