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

from .conceptforge_signals import (
    handle_selfblog_publish,
    connect_conceptforge_signals,
)

from .deliverable_status_signals import (
    classify_transition,
    stash_prior_status,
    record_status_transition,
    connect_deliverable_status_signals,
)

from .mythology_alert_signals import (
    bridge_mythology_alert_to_hai,
    connect_mythology_alert_signals,
)

from .document_processing_signals import (
    on_document_created,
    on_narrative_shift_created,
    connect_document_processing_signals,
)

from .initiative_diagnostic_signals import (
    mark_initiative_diagnostic_on_create,
    stash_prior_target_workspace_id,
    clear_initiative_diagnostic_on_workspace_set,
    connect_initiative_diagnostic_signals,
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
    # ConceptForge signals (Session 863)
    'handle_selfblog_publish',
    'connect_conceptforge_signals',
    # Deliverable status transition signals (Session 1095 — rework gate)
    'classify_transition',
    'stash_prior_status',
    'record_status_transition',
    'connect_deliverable_status_signals',
    # Mythology alert → HAI bridge (Session 1095 Tier 1b)
    'bridge_mythology_alert_to_hai',
    'connect_mythology_alert_signals',
    # Document + NarrativeShift processing signals (Session 1115 batch-7)
    'on_document_created',
    'on_narrative_shift_created',
    'connect_document_processing_signals',
    # Initiative no-orphan diagnostic signals (Session 1196 PR #2 + PR #3)
    'mark_initiative_diagnostic_on_create',
    'stash_prior_target_workspace_id',
    'clear_initiative_diagnostic_on_workspace_set',
    'connect_initiative_diagnostic_signals',
]
