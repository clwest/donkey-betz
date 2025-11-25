"""
Agent Registry Module - Unified AI Agent Management System

This module provides comprehensive agent management for the unified platform.

Exports:
- BaseContentAgent: Base class for content generation agents
- AgentResult: Standard result structure for agent execution

Session 186: Added BaseContentAgent for Task 3.7 Agent System Cleanup
"""

from agents.base_agent import BaseContentAgent, AgentResult

default_app_config = 'agents.apps.AgentsConfig'

__all__ = ['BaseContentAgent', 'AgentResult']