"""
Context Tracking Helper for Agent Executions
Session 758: Centralized context injection tracking for Integration Health observability.

This module provides a helper function to build context tracking data that can be
added to AgentExecution.input_data from any execution entry point.

Usage:
    from core.services.context_tracking import build_context_tracking

    # When creating an AgentExecution:
    context_tracking = build_context_tracking(agent_name, task)
    execution = AgentExecution.objects.create(
        ...
        input_data={
            'task': task,
            'context_injected': context_tracking,
        }
    )
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def build_context_tracking(
    agent_name: str,
    task: str,
    include_full_context: bool = False
) -> Dict[str, Any]:
    """
    Build context tracking data for an agent execution.

    Session 758: This enables Integration Health to track context injection
    rates across all execution entry points.

    Args:
        agent_name: Name of the agent being executed
        task: The task being executed
        include_full_context: If True, also builds and returns the full context

    Returns:
        Dict with context injection summary for tracking
    """
    tracking = {
        'spider_data': False,
        'spider_trends': 0,
        'spider_discussions': 0,
        'learning_patterns': False,
        'advisor_insights': False,
        'performance_feedback': False,
        'scifi_context': False,
        'tracking_source': 'context_tracking_helper',
    }

    try:
        # Get spider context
        from core.services.spider_context_builder import get_spider_context_builder
        spider_builder = get_spider_context_builder()
        spider_context = spider_builder.build_context_for_agent(agent_name, task)

        if spider_context:
            tracking['spider_data'] = spider_context.get('has_data', False)
            tracking['spider_trends'] = len(spider_context.get('relevant_trends', []))
            tracking['spider_discussions'] = len(spider_context.get('discussions', []))

    except Exception as e:
        logger.debug(f"Spider context unavailable: {e}")

    try:
        # Get learning context
        from core.services.learning_pattern_engine import get_learning_pattern_engine
        learning_engine = get_learning_pattern_engine()
        learning_context = learning_engine.get_patterns_for_agent(agent_name, task)

        if learning_context:
            tracking['learning_patterns'] = learning_context.get('has_patterns', False)

    except Exception as e:
        logger.debug(f"Learning context unavailable: {e}")

    try:
        # Get advisor context
        from core.services.advisor_context_builder import get_advisor_context_builder
        advisor_builder = get_advisor_context_builder()
        advisor_context = advisor_builder.build_context_for_agent(agent_name, task)

        if advisor_context:
            tracking['advisor_insights'] = advisor_context.get('has_advice', False)

    except Exception as e:
        logger.debug(f"Advisor context unavailable: {e}")

    try:
        # Get feedback context
        from core.services.feedback_loop_engine import get_feedback_loop_engine
        feedback_engine = get_feedback_loop_engine()
        feedback_context = feedback_engine.get_feedback_for_agent(agent_name)

        if feedback_context:
            tracking['performance_feedback'] = feedback_context.get('has_feedback', False)

    except Exception as e:
        logger.debug(f"Feedback context unavailable: {e}")

    logger.debug(
        f"[Session 758] Context tracking for {agent_name}: "
        f"spider={tracking['spider_data']}, learning={tracking['learning_patterns']}, "
        f"advisor={tracking['advisor_insights']}, feedback={tracking['performance_feedback']}"
    )

    return tracking


def build_context_tracking_quick(agent_name: str) -> Dict[str, Any]:
    """
    Quick version that just marks tracking is enabled without full context lookup.
    Use this for health checks or when full context isn't needed.

    Args:
        agent_name: Name of the agent

    Returns:
        Minimal tracking dict
    """
    return {
        'spider_data': False,
        'spider_trends': 0,
        'spider_discussions': 0,
        'learning_patterns': False,
        'advisor_insights': False,
        'performance_feedback': False,
        'scifi_context': False,
        'tracking_source': 'quick_tracking',
        'is_health_check': True,
    }
