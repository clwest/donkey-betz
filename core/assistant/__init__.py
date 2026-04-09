"""
AI Assistant Package
====================

This package provides a modular Personal AI Assistant with tool execution,
context management, and multi-agent orchestration capabilities.

The assistant has been decomposed from a monolithic 7,000+ line file into
focused modules for better maintainability and testability.

Public API:
- PersonalAIAssistant: Base assistant class (from personal_ai_assistant.py)
- EnhancedPersonalAIAssistant: Full-featured assistant with all capabilities

Package Structure:
- base.py: Core assistant class with initialization and main interface
- tool_definitions.py: GPT-5.1 tool schemas for function calling
- tool_executor.py: Tool execution routing and handlers
- image_tools.py: Image generation and editing tool handlers
- video_tools.py: Video generation and editing tool handlers
- audio_tools.py: Audio generation tool handlers
- message_processor.py: Message processing and AI response generation
- context_manager.py: Conversation context and memory management
- utils.py: Shared utilities (ID resolution, range parsing)
- constants.py: Configuration constants

Session 184: Refactored from core/personal_ai_assistant_enhanced.py (6,905 lines)
"""

# Legacy PA classes removed — all traffic routes through Rigby
# EnhancedPersonalAIAssistant and PersonalAIAssistant no longer exported.

__all__ = []
