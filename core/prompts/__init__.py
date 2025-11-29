"""
Central Prompt Registry - Super Platform Intelligence System
============================================================

Session 266: Unified prompt architecture for the entire platform.

This module is the SINGLE SOURCE OF TRUTH for all system prompts.
All agents, assistants, and AI components pull their prompts from here.

Architecture:
- PLATFORM_CONTEXT: Shared context about what the platform can do
- PERSONAL_ASSISTANT: Main user-facing assistant prompt
- AGENT_PROMPTS: Individual agent system prompts
- ADVISOR_PROMPTS: Legendary advisor personalities
- CONVERSATION_ROLES: Agent-to-agent conversation roles
- TOOL_DESCRIPTIONS: GPT function calling descriptions
- COMMAND_CENTER_PROMPTS: AI Command Center WebSocket interface
- INTERVIEW_PROMPTS: Personal Assistant Interviewer
- DYNAMIC_PROMPT_SECTIONS: Context-aware prompt building
- SELF_AWARENESS_PROMPTS: System self-awareness features

Usage:
    from core.prompts import get_agent_prompt, get_platform_context
    from core.prompts import get_tool_description
    from core.prompts import get_command_center_prompt, get_interview_prompt

    prompt = get_agent_prompt('ResearchAgent')
    context = get_platform_context()
    tool_desc = get_tool_description('image_generation_agent')
    cc_prompt = get_command_center_prompt('main', agent_count=149)
"""

from .registry import (
    # Platform context
    PLATFORM_CONTEXT,
    get_platform_context,

    # Personal Assistant
    PERSONAL_ASSISTANT_PROMPT,
    build_personal_assistant_prompt,

    # Agent prompts
    AGENT_PROMPTS,
    get_agent_prompt,

    # Advisor prompts
    ADVISOR_PROMPTS,
    get_advisor_prompt,

    # Conversation roles (agent-to-agent)
    CONVERSATION_ROLES,
    get_conversation_role,

    # Task-type prompts
    TASK_TYPE_PROMPTS,
    get_task_prompt,

    # Command Center prompts
    COMMAND_CENTER_PROMPTS,
    get_command_center_prompt,

    # Interview prompts
    INTERVIEW_PROMPTS,
    get_interview_prompt,

    # Dynamic prompt sections
    DYNAMIC_PROMPT_SECTIONS,
    QUERY_TYPE_INTROS,
    get_dynamic_section,
    get_query_intro,

    # Self-awareness prompts
    SELF_AWARENESS_PROMPTS,
    get_self_awareness_prompt,

    # Utility functions
    list_available_agents,
    list_available_advisors,
    get_prompt_stats,
)

from .tool_descriptions import (
    # Tool descriptions for GPT function calling
    TOOL_DESCRIPTIONS,
    PARAM_DESCRIPTIONS,
    get_tool_description,
    get_param_description,
    list_available_tools,
)

__all__ = [
    # Registry - Core prompts
    'PLATFORM_CONTEXT',
    'get_platform_context',
    'PERSONAL_ASSISTANT_PROMPT',
    'build_personal_assistant_prompt',
    'AGENT_PROMPTS',
    'get_agent_prompt',
    'ADVISOR_PROMPTS',
    'get_advisor_prompt',
    'CONVERSATION_ROLES',
    'get_conversation_role',
    'TASK_TYPE_PROMPTS',
    'get_task_prompt',

    # Command Center
    'COMMAND_CENTER_PROMPTS',
    'get_command_center_prompt',

    # Interview
    'INTERVIEW_PROMPTS',
    'get_interview_prompt',

    # Dynamic prompts
    'DYNAMIC_PROMPT_SECTIONS',
    'QUERY_TYPE_INTROS',
    'get_dynamic_section',
    'get_query_intro',

    # Self-awareness
    'SELF_AWARENESS_PROMPTS',
    'get_self_awareness_prompt',

    # Utility
    'list_available_agents',
    'list_available_advisors',
    'get_prompt_stats',

    # Tool descriptions
    'TOOL_DESCRIPTIONS',
    'PARAM_DESCRIPTIONS',
    'get_tool_description',
    'get_param_description',
    'list_available_tools',
]
