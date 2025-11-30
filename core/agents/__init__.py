"""
Unified Agent System - Clean Architecture
==========================================

Session 268: Phase 1 & 2 - Complete Agent Ecosystem
Session 280: Phase 2 - Strategy and Executive Agents
Session 281: Phase 3 - Analysis, Training, and Security Agents

All agents inherit from BaseAgent and follow these principles:
1. Isolated tools - each agent only has access to its own tools
2. Time Travel Debugging - all decisions are recorded via TimeTravelMixin
3. Spider Context - agents receive relevant spider data (trends, market)
4. Sci-Fi Integration - mood, memory, evolution affect behavior

Architecture:
    User → Personal Assistant → Agent Router → Specialized Agents → Tools

Usage:
    # Direct import
    from core.agents import ImageAgent, VideoAgent

    # Sub-package import
    from core.agents.strategy import ContentStrategyAgent
    from core.agents.executive import CTOAgent
    from core.agents.analysis import TrendAnalysisAgent
    from core.agents.training import CharacterTrainingAgent
    from core.agents.security import MemoryIsolationAgent

    # Via AgentRouter (recommended)
    from core.agent_router import AgentRouter

    router = AgentRouter(user=request.user)
    result = router.route("ImageAgent", "create a cyberpunk logo", context={})

Available Agents (22 total):

    CREATION AGENTS (4):
        ImageAgent          - Image generation (logos, banners, illustrations)
        VideoAgent          - Video generation (text-to-video, animations)
        AudioAgent          - Audio generation (TTS, voiceovers)
        ThreeDAgent         - 3D model generation

    EDITING AGENTS (2):
        ImageEditingAgent   - Image editing (upscale, remove bg, variations)
        VideoEditingAgent   - Video editing (trim, effects, text)

    RESEARCH AGENTS (1):
        ResearchAgent       - Web search + spider network queries

    STRATEGY AGENTS (4) - Session 280:
        ContentStrategyAgent - Content recommendations from trends
        BrandIdentityAgent   - Brand colors, styles, consistency
        SEOOptimizerAgent    - Hashtags, metadata, keywords
        SocialMediaAgent     - Platform-specific content strategy

    EXECUTIVE AGENTS (4) - Session 280:
        CTOAgent              - Technical planning and analysis
        COOAgent              - Operations planning and risk analysis
        CreativeDirectorAgent - Creative guidance and prompt enhancement
        MeetingCoordinatorAgent - Coordinates meetings between agents

    ANALYSIS AGENTS (2) - Session 281:
        TrendAnalysisAgent      - Spider intelligence analysis
        OpportunityScoringAgent - Opportunity scoring engine

    TRAINING AGENTS (2) - Session 281:
        CharacterTrainingAgent  - FLUX LoRA character training
        TrainedCreationAgent    - LoRA image generation

    SECURITY AGENTS (1) - Session 281:
        MemoryIsolationAgent    - Memory isolation and security

    ORCHESTRATION AGENTS (1):
        WorkflowAgent           - Multi-step workflow coordination

    ENTRY POINT (1):
        PersonalAssistantAgent  - Main user interaction and routing

Legacy Compatibility:
    The old `agents` package still works but emits deprecation warnings:

    # OLD (deprecated, shows warning):
    from agents import ImageAgent

    # NEW (preferred, no warning):
    from core.agents import ImageAgent
"""

# Base classes
from core.agents.base_agent import BaseAgent, AgentResult

# Creation Agents
from core.agents.image_agent import ImageAgent
from core.agents.video_agent import VideoAgent
from core.agents.audio_agent import AudioAgent
from core.agents.three_d_agent import ThreeDAgent

# Editing Agents
from core.agents.image_editing_agent import ImageEditingAgent
from core.agents.video_editing_agent import VideoEditingAgent

# Research Agents
from core.agents.research_agent import ResearchAgent

# Orchestration Agents
from core.agents.workflow_agent import WorkflowAgent

# Entry Point Agent
from core.agents.personal_assistant_agent import PersonalAssistantAgent

# Strategy Agents (Session 280)
from core.agents.strategy import (
    ContentStrategyAgent,
    BrandIdentityAgent,
    SEOOptimizerAgent,
    SocialMediaAgent,
)

# Executive Agents (Session 280)
from core.agents.executive import (
    CTOAgent,
    COOAgent,
    CreativeDirectorAgent,
    MeetingCoordinatorAgent,
)

# Analysis Agents (Session 281)
from core.agents.analysis import (
    TrendAnalysisAgent,
    OpportunityScoringAgent,
)

# Training Agents (Session 281)
from core.agents.training import (
    CharacterTrainingAgent,
    TrainedCreationAgent,
)

# Security Agents (Session 281)
from core.agents.security import (
    MemoryIsolationAgent,
)

__all__ = [
    # Base
    'BaseAgent',
    'AgentResult',

    # Creation Agents (4)
    'ImageAgent',
    'VideoAgent',
    'AudioAgent',
    'ThreeDAgent',

    # Editing Agents (2)
    'ImageEditingAgent',
    'VideoEditingAgent',

    # Research Agents (1)
    'ResearchAgent',

    # Orchestration Agents (1)
    'WorkflowAgent',

    # Entry Point Agent (1)
    'PersonalAssistantAgent',

    # Strategy Agents (4) - Session 280
    'ContentStrategyAgent',
    'BrandIdentityAgent',
    'SEOOptimizerAgent',
    'SocialMediaAgent',

    # Executive Agents (4) - Session 280
    'CTOAgent',
    'COOAgent',
    'CreativeDirectorAgent',
    'MeetingCoordinatorAgent',

    # Analysis Agents (2) - Session 281
    'TrendAnalysisAgent',
    'OpportunityScoringAgent',

    # Training Agents (2) - Session 281
    'CharacterTrainingAgent',
    'TrainedCreationAgent',

    # Security Agents (1) - Session 281
    'MemoryIsolationAgent',
]
