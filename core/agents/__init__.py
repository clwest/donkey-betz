"""
Clean Architecture Agents Package
==================================

Session 268: Phase 1 & 2 - Complete Agent Ecosystem

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
    from core.agents import ImageAgent, VideoAgent, WorkflowAgent
    from core.agent_router import AgentRouter

    router = AgentRouter(user=request.user)
    result = router.route("ImageAgent", "create a cyberpunk logo", context={})

Available Agents:
    Creation:
    - ImageAgent: Image generation (logos, banners, illustrations)
    - VideoAgent: Video generation (text-to-video, animations)
    - AudioAgent: Audio generation (TTS, voiceovers)
    - ThreeDAgent: 3D model generation

    Editing:
    - ImageEditingAgent: Image editing (upscale, remove bg, variations)
    - VideoEditingAgent: Video editing (trim, effects, text)

    Research:
    - ResearchAgent: Web search + spider network queries

    Orchestration:
    - WorkflowAgent: Multi-step workflow coordination (can delegate to other agents)
"""

from core.agents.base_agent import BaseAgent, AgentResult
from core.agents.image_agent import ImageAgent
from core.agents.video_agent import VideoAgent
from core.agents.audio_agent import AudioAgent
from core.agents.three_d_agent import ThreeDAgent
from core.agents.image_editing_agent import ImageEditingAgent
from core.agents.video_editing_agent import VideoEditingAgent
from core.agents.research_agent import ResearchAgent
from core.agents.workflow_agent import WorkflowAgent
from core.agents.personal_assistant_agent import PersonalAssistantAgent

__all__ = [
    # Base
    'BaseAgent',
    'AgentResult',

    # Creation Agents
    'ImageAgent',
    'VideoAgent',
    'AudioAgent',
    'ThreeDAgent',

    # Editing Agents
    'ImageEditingAgent',
    'VideoEditingAgent',

    # Research Agents
    'ResearchAgent',

    # Orchestration Agents
    'WorkflowAgent',

    # Entry Point Agent
    'PersonalAssistantAgent',
]
