"""
Super Platform - The Unified Intelligence Hub

This module contains the core coordination layer that unifies all platform
components into a single, coherent intelligence system.

Components:
- QueryClassifier: Understands user intent (question, creation, collaboration, etc.)
- PromptBuilder: Dynamically builds context-aware prompts
- ContextAggregator: Gathers context from spiders, memory, mood, relationships
- SuperPlatformCoordinator: The unified brain that orchestrates everything

Session 264: Phase 1 Foundation
"""

from .query_classifier import QueryClassifier
from .prompt_builder import DynamicPromptBuilder
from .context_aggregator import ContextAggregator
from .coordinator import SuperPlatformCoordinator

__all__ = [
    'QueryClassifier',
    'DynamicPromptBuilder',
    'ContextAggregator',
    'SuperPlatformCoordinator',
]
