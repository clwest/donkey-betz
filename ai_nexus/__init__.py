"""
AI Nexus - Intelligent Multi-Provider AI Orchestration System
=============================================================

The central hub for all AI operations in the Unified Platform.
Manages multiple AI providers, agent orchestration, and intelligent routing.
"""

__version__ = "1.0.0"
__author__ = "Unified Platform Team"

# Core components
from .orchestrator import AIOrchestrator
from .providers import ProviderRegistry
from .agents import AgentCoordinator
from .memory import MemorySystem
from .learning import LearningEngine

__all__ = [
    'AIOrchestrator',
    'ProviderRegistry',
    'AgentCoordinator',
    'MemorySystem',
    'LearningEngine'
]