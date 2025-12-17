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

__all__ = [
    'evaluate_triggers_for_spider_data',
    'on_spider_data_created',
    'connect_trigger_signals',
    'evaluate_triggers_batch',
]
