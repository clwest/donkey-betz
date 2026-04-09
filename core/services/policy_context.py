"""
Policy Context Service
Session 323: Boardroom Decisions - Phase 3
Session 412: Updated with new impact areas (legal, research, spider) and agents

Retrieves canonical policies to inject into agent prompts.
This creates the feedback loop where agent decisions influence future agent behavior.
"""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class PolicyContextService:
    """Provides canonical policy context for agent prompts."""

    # Map agent names to relevant impact areas
    # Impact areas: prompting, memory, image, video, audio, workflow, agents,
    #               security, infrastructure, product, legal, research, spider
    AGENT_IMPACT_AREAS = {
        # Image agents
        'ImageAgent': ['image', 'workflow', 'prompting'],
        'ImageEditingAgent': ['image', 'workflow'],
        'image_generation_agent': ['image', 'workflow', 'prompting'],

        # Video agents
        'VideoAgent': ['video', 'workflow'],
        'video_generation_agent': ['video', 'workflow'],
        'VideoEditingAgent': ['video', 'workflow'],

        # Audio agents
        'AudioAgent': ['audio', 'workflow'],
        'AudioGenerationAgent': ['audio', 'workflow'],

        # Prompt/AI agents
        'PromptEngineeringAgent': ['prompting', 'agents'],
        'prompt_engineering_agent': ['prompting', 'agents'],

        # Memory agents
        'MemoryIsolationAgent': ['memory', 'security', 'agents'],

        # Creative agents
        'CreativeDirectorAgent': ['image', 'video', 'product', 'workflow'],
        'CreationAgent': ['image', 'video', 'audio', 'workflow'],
        'BrandIdentityAgent': ['image', 'product'],

        # Strategy agents
        'ContentStrategyAgent': ['product', 'workflow'],
        'SEOOptimizerAgent': ['product'],
        'SocialMediaAgent': ['product'],

        # Research agents
        'ResearchAgent': ['prompting', 'agents', 'research', 'spider'],
        'TrendAnalysisAgent': ['product', 'research', 'spider'],
        'CompetitorAnalysisAgent': ['product', 'research'],
        'CustomerResearchAgent': ['product', 'research'],
        'BrandStrategyAgent': ['product', 'research'],
        'MarketingStrategyAgent': ['product', 'research'],
        'BusinessContentStrategyAgent': ['product', 'research'],

        # Workflow agents
        'WorkflowOrchestrationAgent': ['workflow', 'agents'],
        'WorkflowAgent': ['workflow', 'agents'],

        # Executive agents
        'CTOAgent': ['architecture', 'infrastructure', 'security'],
        'COOAgent': ['workflow', 'product'],
        'MeetingCoordinatorAgent': ['agents', 'workflow'],

        # Legal agents (Session 403-410)
        'LegalDocDrafterAgent': ['legal', 'agents', 'prompting'],

        # Training agents
        'CharacterTrainingAgent': ['image', 'workflow'],
        'TrainedCreationAgent': ['image', 'workflow'],

        # 3D agents
        'ThreeDAgent': ['image', 'workflow'],

        # PersonalAssistantAgent removed — deprecated

        # Specialized
        'BookmakerAgent': ['prompting', 'agents'],
        'OpportunityScoringAgent': ['product', 'workflow'],
    }

    def get_policies_for_agent(
        self,
        agent_name: str,
        impact_areas: Optional[List[str]] = None,
        max_policies: int = 5
    ) -> str:
        """
        Get canonical policies relevant to an agent.

        Args:
            agent_name: Name of the agent requesting context
            impact_areas: Optional filter by impact area (overrides auto-detection)
            max_policies: Maximum number of policies to include

        Returns:
            Formatted policy context string for injection into prompts
        """
        from core.models_unified_system import AgentDecisionSummary

        # Auto-detect relevant areas if not specified
        if impact_areas is None:
            impact_areas = self.AGENT_IMPACT_AREAS.get(agent_name)
            # Always include 'agents' area as fallback for all agents
            if impact_areas:
                impact_areas = list(impact_areas) + ['agents']
            else:
                impact_areas = ['agents']  # Default to agents area

        queryset = AgentDecisionSummary.objects.filter(
            is_canonical=True
        ).order_by('-promoted_at')

        if impact_areas:
            queryset = queryset.filter(impact_area__in=impact_areas)

        policies = queryset[:max_policies]

        if not policies:
            # No area-specific policies, try getting any canonical policy
            policies = AgentDecisionSummary.objects.filter(
                is_canonical=True
            ).order_by('-promoted_at')[:max_policies]

        if not policies:
            logger.debug(f"No canonical policies found for agent {agent_name}")
            return ""

        context_parts = [
            "",
            "=" * 50,
            "CANONICAL POLICIES",
            "=" * 50,
            "The following policies have been established through agent deliberation.",
            "You should align your recommendations with these established policies.",
            ""
        ]

        for i, policy in enumerate(policies, 1):
            context_parts.append(policy.get_policy_context())

        context_parts.extend([
            "",
            "=" * 50,
            ""
        ])

        policy_context = '\n'.join(context_parts)
        logger.info(f"🏛️ [POLICY] Injecting {len(policies)} policies for {agent_name}")

        return policy_context

    def get_policies_by_area(self, impact_area: str) -> List:
        """Get all canonical policies for a specific impact area."""
        from core.models_unified_system import AgentDecisionSummary
        return list(
            AgentDecisionSummary.objects.filter(
                is_canonical=True,
                impact_area=impact_area
            ).order_by('-promoted_at')
        )

    def get_all_canonical_policies(self, max_policies: int = 10) -> str:
        """Get all canonical policies regardless of impact area."""
        from core.models_unified_system import AgentDecisionSummary

        policies = AgentDecisionSummary.objects.filter(
            is_canonical=True
        ).order_by('-promoted_at')[:max_policies]

        if not policies:
            return ""

        context_parts = [
            "",
            "=" * 50,
            "CANONICAL POLICIES",
            "=" * 50,
            "These policies have been established through agent governance:",
            ""
        ]

        for policy in policies:
            context_parts.append(policy.get_policy_context())

        context_parts.extend([
            "",
            "=" * 50,
            ""
        ])

        return '\n'.join(context_parts)

    def get_policy_summary(self) -> dict:
        """Get a summary of all canonical policies for dashboards."""
        from core.models_unified_system import AgentDecisionSummary
        from django.db.models import Count

        canonical = AgentDecisionSummary.objects.filter(is_canonical=True)

        return {
            'total_canonical': canonical.count(),
            'by_type': dict(
                canonical.values('decision_type')
                .annotate(count=Count('id'))
                .values_list('decision_type', 'count')
            ),
            'by_area': dict(
                canonical.values('impact_area')
                .annotate(count=Count('id'))
                .values_list('impact_area', 'count')
            ),
            'recent': list(
                canonical.order_by('-promoted_at')[:5]
                .values('topic', 'decision_type', 'promoted_at')
            )
        }


# Singleton instance
_policy_context_instance = None


def get_policy_context_service() -> PolicyContextService:
    """Get singleton policy context service."""
    global _policy_context_instance
    if _policy_context_instance is None:
        _policy_context_instance = PolicyContextService()
    return _policy_context_instance
