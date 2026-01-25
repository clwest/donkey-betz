"""
Core Signals Package

Contains signal handlers for various core functionality.
"""

from .trigger_signals import (
    evaluate_triggers_for_spider_data,
    on_spider_data_created,
    connect_trigger_signals,
    evaluate_triggers_batch,
)

from .dream_signals import (
    track_dream_approval_change,
    trigger_dream_execution_on_approval,
    connect_dream_signals,
)

from .revenue_signals import (
    opportunity_pre_save,
    opportunity_post_save_create_revenue,
    connect_revenue_signals,
)

__all__ = [
    # Trigger signals
    'evaluate_triggers_for_spider_data',
    'on_spider_data_created',
    'connect_trigger_signals',
    'evaluate_triggers_batch',
    # Dream signals (Session 766)
    'track_dream_approval_change',
    'trigger_dream_execution_on_approval',
    'connect_dream_signals',
    # Revenue signals (Session 822)
    'opportunity_pre_save',
    'opportunity_post_save_create_revenue',
    'connect_revenue_signals',
]
