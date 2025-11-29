"""
Super Platform - The Unified Intelligence Hub

This module contains the core coordination layer that unifies all platform
components into a single, coherent intelligence system.

Components:
- QueryClassifier: Understands user intent (question, creation, collaboration, etc.)
- PromptBuilder: Dynamically builds context-aware prompts
- ContextAggregator: Gathers context from spiders, memory, mood, relationships
- SuperPlatformCoordinator: The unified brain that orchestrates everything

Phase 2 (Spider-Agent Bridge):
- AgentContextService: Provides spider intelligence to agents
- SpiderContextMixin: Mixin for agents to access spider data

Session 264: Phase 1 Foundation + Phase 2 Spider-Agent Bridge
"""

from .query_classifier import QueryClassifier
from .prompt_builder import DynamicPromptBuilder
from .context_aggregator import ContextAggregator
from .coordinator import SuperPlatformCoordinator
from .agent_context_service import AgentContextService, AgentContext, get_agent_context_service
from .spider_context_mixin import SpiderContextMixin

__all__ = [
    # Phase 1: Foundation
    'QueryClassifier',
    'DynamicPromptBuilder',
    'ContextAggregator',
    'SuperPlatformCoordinator',
    # Phase 2: Spider-Agent Bridge
    'AgentContextService',
    'AgentContext',
    'get_agent_context_service',
    'SpiderContextMixin',
]
