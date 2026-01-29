"""
ConceptForge: Autonomous Think Tank Pipeline
============================================

Session 863: Content → Intelligence → Strategy → Product

Transforms published content into comprehensive dossiers through
multi-stage analysis with persona agents and legendary advisors.

Architecture:
- Config-first labs and panels (not DB tables)
- Run tracking in database
- Advisor panel snapshots per run for reproducibility
- Gate triggers (quality_score >= 0.80 + strategic_tag)

Pipeline Stages:
1. Research - Spider-enriched research with trend analysis
2. Debate - Legendary advisors take positions (pro/con)
3. Feasibility - Technical/systems architecture assessment
4. Risk - Legal/compliance/ethics analysis
5. Market - Business opportunity sizing
6. Synthesis - ThinkingAgent combines all into dossier

Usage:
    from core.conceptforge import ConceptForgeOrchestrator

    orchestrator = ConceptForgeOrchestrator()
    run = orchestrator.start_pipeline(
        source_type='blog',
        source_id=blog.id,
        domain='legal'
    )
"""

from .labs import DOMAIN_LABS, get_lab_config, get_lab_for_tags, get_stage_names
from .panels import ADVISOR_PANELS, select_panel_for_domain, get_debate_positions
from .orchestrator import ConceptForgeOrchestrator

__all__ = [
    'DOMAIN_LABS',
    'get_lab_config',
    'get_lab_for_tags',
    'get_stage_names',
    'ADVISOR_PANELS',
    'select_panel_for_domain',
    'get_debate_positions',
    'ConceptForgeOrchestrator',
]
