"""
Agent Training Service
======================

Session 217B: Agent training, configuration, and capability management.

Provides:
- Agent configuration CRUD operations
- Capability management (add, remove, update)
- Knowledge base management
- Training history tracking
- Agent templates
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from uuid import uuid4

from django.db.models import Count, Avg
from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Agent configuration structure."""
    name: str
    display_name: str
    description: str
    capabilities: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4000
    system_prompt: str = ""
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'capabilities': self.capabilities,
            'domains': self.domains,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'system_prompt': self.system_prompt,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class TrainingRecord:
    """Record of a training session."""
    id: str
    agent_name: str
    training_type: str  # knowledge, capability, tuning
    description: str
    data_source: str
    status: str  # pending, in_progress, completed, failed
    created_at: datetime
    completed_at: Optional[datetime] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


# Available capability definitions
AVAILABLE_CAPABILITIES = {
    'image_generation': {
        'name': 'Image Generation',
        'description': 'Generate images using Stability AI',
        'domains': ['image', 'creative']
    },
    'video_generation': {
        'name': 'Video Generation',
        'description': 'Generate videos using RunwayML',
        'domains': ['video', 'creative']
    },
    'audio_generation': {
        'name': 'Audio Generation',
        'description': 'Generate audio using ElevenLabs',
        'domains': ['audio', 'creative']
    },
    'text_generation': {
        'name': 'Text Generation',
        'description': 'Generate text content',
        'domains': ['text', 'creative']
    },
    'research': {
        'name': 'Research',
        'description': 'Conduct research and gather information',
        'domains': ['research', 'analysis']
    },
    'code_generation': {
        'name': 'Code Generation',
        'description': 'Generate and review code',
        'domains': ['code', 'development']
    },
    'data_analysis': {
        'name': 'Data Analysis',
        'description': 'Analyze data and generate insights',
        'domains': ['data', 'analysis']
    },
    'brand_identity': {
        'name': 'Brand Identity',
        'description': 'Create brand identity elements',
        'domains': ['branding', 'creative']
    },
    'social_media': {
        'name': 'Social Media',
        'description': 'Create social media content',
        'domains': ['social', 'marketing']
    },
    'seo_optimization': {
        'name': 'SEO Optimization',
        'description': 'Optimize content for search engines',
        'domains': ['seo', 'marketing']
    },
    'collaboration': {
        'name': 'Collaboration',
        'description': 'Collaborate with other agents',
        'domains': ['collaboration', 'communication']
    },
    'workflow_execution': {
        'name': 'Workflow Execution',
        'description': 'Execute multi-step workflows',
        'domains': ['workflow', 'orchestration']
    }
}

# Agent templates
AGENT_TEMPLATES = {
    'creative_assistant': {
        'display_name': 'Creative Assistant',
        'description': 'Versatile creative agent for images, videos, and design',
        'capabilities': ['image_generation', 'video_generation', 'brand_identity'],
        'domains': ['creative', 'design'],
        'model': 'gpt-4',
        'temperature': 0.8,
        'system_prompt': 'You are a creative assistant specializing in visual content creation.'
    },
    'research_analyst': {
        'display_name': 'Research Analyst',
        'description': 'Agent specialized in research and data analysis',
        'capabilities': ['research', 'data_analysis'],
        'domains': ['research', 'analysis'],
        'model': 'gpt-4',
        'temperature': 0.3,
        'system_prompt': 'You are a research analyst providing accurate, data-driven insights.'
    },
    'content_writer': {
        'display_name': 'Content Writer',
        'description': 'Agent for creating written content',
        'capabilities': ['text_generation', 'seo_optimization', 'social_media'],
        'domains': ['content', 'marketing'],
        'model': 'gpt-4',
        'temperature': 0.7,
        'system_prompt': 'You are a skilled content writer creating engaging content.'
    },
    'developer_assistant': {
        'display_name': 'Developer Assistant',
        'description': 'Agent for code generation and development',
        'capabilities': ['code_generation', 'data_analysis'],
        'domains': ['development', 'code'],
        'model': 'gpt-4',
        'temperature': 0.2,
        'system_prompt': 'You are a skilled developer helping with code generation and review.'
    },
    'workflow_orchestrator': {
        'display_name': 'Workflow Orchestrator',
        'description': 'Agent for coordinating multi-step workflows',
        'capabilities': ['workflow_execution', 'collaboration'],
        'domains': ['orchestration', 'workflow'],
        'model': 'gpt-4',
        'temperature': 0.5,
        'system_prompt': 'You orchestrate complex workflows across multiple agents.'
    }
}


class AgentTrainingService:
    """
    Service for managing agent training, configuration, and capabilities.
    """

    def __init__(self, user=None):
        self.user = user

    # =========================================================================
    # AGENT CONFIGURATION
    # =========================================================================

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all agent configurations."""
        from core.models_unified_system import AgentPerformanceMetric

        agents = []

        # Get agents from performance metrics
        metrics = AgentPerformanceMetric.objects.all()

        for metric in metrics:
            agents.append({
                'name': metric.agent_name,
                'display_name': metric.agent_name.replace('_', ' ').title(),
                'total_executions': metric.total_executions,
                'successful_executions': metric.successful_executions,
                'quality_score': float(metric.quality_score),
                'specialization_scores': metric.specialization_scores or {},
                'capabilities': list(metric.specialization_scores.keys()) if metric.specialization_scores else [],
                'is_active': True,
                'last_activity': metric.last_activity.isoformat() if metric.last_activity else None
            })

        # Add template agents if not in database
        for template_name, template in AGENT_TEMPLATES.items():
            if not any(a['name'] == template_name for a in agents):
                agents.append({
                    'name': template_name,
                    'display_name': template['display_name'],
                    'total_executions': 0,
                    'successful_executions': 0,
                    'quality_score': 0.0,
                    'specialization_scores': {},
                    'capabilities': template['capabilities'],
                    'is_active': False,
                    'is_template': True
                })

        return agents

    def get_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific agent."""
        from core.models_unified_system import AgentPerformanceMetric

        try:
            metric = AgentPerformanceMetric.objects.get(agent_name=agent_name)

            return {
                'name': metric.agent_name,
                'display_name': metric.agent_name.replace('_', ' ').title(),
                'description': f"Agent specializing in {', '.join(list(metric.specialization_scores.keys())[:3]) if metric.specialization_scores else 'general tasks'}",
                'capabilities': list(metric.specialization_scores.keys()) if metric.specialization_scores else [],
                'domains': self._infer_domains(metric.specialization_scores),
                'total_executions': metric.total_executions,
                'successful_executions': metric.successful_executions,
                'quality_score': float(metric.quality_score),
                'is_active': True,
                'last_activity': metric.last_activity.isoformat() if metric.last_activity else None,
                'created_at': metric.created_at.isoformat() if hasattr(metric, 'created_at') else None
            }
        except AgentPerformanceMetric.DoesNotExist:
            # Check templates
            if agent_name in AGENT_TEMPLATES:
                template = AGENT_TEMPLATES[agent_name]
                return {
                    'name': agent_name,
                    'display_name': template['display_name'],
                    'description': template['description'],
                    'capabilities': template['capabilities'],
                    'domains': template['domains'],
                    'model': template['model'],
                    'temperature': template['temperature'],
                    'system_prompt': template['system_prompt'],
                    'is_active': False,
                    'is_template': True
                }

            return None

    def update_agent_config(
        self,
        agent_name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update agent configuration."""
        from core.models_unified_system import AgentPerformanceMetric

        try:
            metric, created = AgentPerformanceMetric.objects.get_or_create(
                agent_name=agent_name,
                defaults={
                    'total_executions': 0,
                    'successful_executions': 0,
                    'quality_score': 0.0
                }
            )

            if capabilities:
                # Update specialization scores
                metric.specialization_scores = {cap: 0.5 for cap in capabilities}

            metric.save()

            return {
                'success': True,
                'agent_name': agent_name,
                'message': 'Agent configuration updated' if not created else 'Agent created'
            }
        except Exception as e:
            logger.error(f"Error updating agent config: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================================================================
    # CAPABILITY MANAGEMENT
    # =========================================================================

    def get_available_capabilities(self) -> List[Dict[str, Any]]:
        """Get all available capabilities that can be assigned to agents."""
        return [
            {
                'id': cap_id,
                'name': cap['name'],
                'description': cap['description'],
                'domains': cap['domains']
            }
            for cap_id, cap in AVAILABLE_CAPABILITIES.items()
        ]

    def add_capability(self, agent_name: str, capability_id: str) -> Dict[str, Any]:
        """Add a capability to an agent."""
        if capability_id not in AVAILABLE_CAPABILITIES:
            return {
                'success': False,
                'error': f'Unknown capability: {capability_id}'
            }

        from core.models_unified_system import AgentPerformanceMetric

        try:
            metric, _ = AgentPerformanceMetric.objects.get_or_create(
                agent_name=agent_name,
                defaults={
                    'total_executions': 0,
                    'successful_executions': 0,
                    'quality_score': 0.0
                }
            )

            scores = metric.specialization_scores or {}
            scores[capability_id] = 0.5  # Initial score
            metric.specialization_scores = scores
            metric.save()

            return {
                'success': True,
                'agent_name': agent_name,
                'capability_added': capability_id,
                'capabilities': list(scores.keys())
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def remove_capability(self, agent_name: str, capability_id: str) -> Dict[str, Any]:
        """Remove a capability from an agent."""
        from core.models_unified_system import AgentPerformanceMetric

        try:
            metric = AgentPerformanceMetric.objects.get(agent_name=agent_name)

            scores = metric.specialization_scores or {}
            if capability_id in scores:
                del scores[capability_id]
                metric.specialization_scores = scores
                metric.save()

            return {
                'success': True,
                'agent_name': agent_name,
                'capability_removed': capability_id,
                'capabilities': list(scores.keys())
            }
        except AgentPerformanceMetric.DoesNotExist:
            return {
                'success': False,
                'error': f'Agent not found: {agent_name}'
            }

    # =========================================================================
    # AGENT TEMPLATES
    # =========================================================================

    def get_agent_templates(self) -> List[Dict[str, Any]]:
        """Get available agent templates."""
        return [
            {
                'id': template_id,
                'display_name': template['display_name'],
                'description': template['description'],
                'capabilities': template['capabilities'],
                'domains': template['domains'],
                'model': template['model']
            }
            for template_id, template in AGENT_TEMPLATES.items()
        ]

    def create_agent_from_template(
        self,
        template_id: str,
        custom_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new agent from a template."""
        if template_id not in AGENT_TEMPLATES:
            return {
                'success': False,
                'error': f'Unknown template: {template_id}'
            }

        template = AGENT_TEMPLATES[template_id]
        agent_name = custom_name or f"{template_id}_{uuid4().hex[:6]}"

        from core.models_unified_system import AgentPerformanceMetric

        try:
            metric, created = AgentPerformanceMetric.objects.get_or_create(
                agent_name=agent_name,
                defaults={
                    'total_executions': 0,
                    'successful_executions': 0,
                    'quality_score': 0.0,
                    'specialization_scores': {cap: 0.5 for cap in template['capabilities']}
                }
            )

            if not created:
                return {
                    'success': False,
                    'error': f'Agent already exists: {agent_name}'
                }

            return {
                'success': True,
                'agent_name': agent_name,
                'template_used': template_id,
                'capabilities': template['capabilities'],
                'message': f'Agent {agent_name} created from template {template_id}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # =========================================================================
    # TRAINING MANAGEMENT
    # =========================================================================

    def get_training_history(self, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get training history for agents."""
        from core.models_unified_system import SharedKnowledge

        query = SharedKnowledge.objects.all()
        if agent_name:
            query = query.filter(source_agent=agent_name)

        query = query.order_by('-created_at')[:50]

        return [
            {
                'id': str(k.id),
                'agent_name': k.source_agent,
                'type': 'knowledge',
                'title': k.title,
                'domain': k.domain,
                'effectiveness': float(k.effectiveness_score),
                'learned_by': len(k.learned_by_agents),
                'created_at': k.created_at.isoformat()
            }
            for k in query
        ]

    def get_training_stats(self) -> Dict[str, Any]:
        """Get overall training statistics."""
        from core.models_unified_system import (
            AgentPerformanceMetric,
            SharedKnowledge,
            CollaborationSession
        )

        total_agents = AgentPerformanceMetric.objects.count()
        active_agents = AgentPerformanceMetric.objects.filter(
            last_activity__gte=timezone.now() - timedelta(days=7)
        ).count()

        total_knowledge = SharedKnowledge.objects.count()
        recent_knowledge = SharedKnowledge.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()

        avg_quality = AgentPerformanceMetric.objects.aggregate(
            avg=Avg('quality_score')
        )['avg'] or 0

        # Capability distribution
        all_metrics = AgentPerformanceMetric.objects.all()
        capability_counts = {}
        for metric in all_metrics:
            for cap in (metric.specialization_scores or {}).keys():
                capability_counts[cap] = capability_counts.get(cap, 0) + 1

        return {
            'total_agents': total_agents,
            'active_agents': active_agents,
            'total_knowledge_items': total_knowledge,
            'recent_knowledge_items': recent_knowledge,
            'average_quality_score': round(float(avg_quality), 2),
            'capability_distribution': capability_counts,
            'available_templates': len(AGENT_TEMPLATES),
            'available_capabilities': len(AVAILABLE_CAPABILITIES)
        }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _infer_domains(self, specialization_scores: Dict[str, float]) -> List[str]:
        """Infer domains from specialization scores."""
        domains = set()
        for cap_id in (specialization_scores or {}).keys():
            if cap_id in AVAILABLE_CAPABILITIES:
                domains.update(AVAILABLE_CAPABILITIES[cap_id]['domains'])
        return list(domains)


def get_agent_training_service(user=None) -> AgentTrainingService:
    """Factory function to get agent training service instance."""
    return AgentTrainingService(user=user)
