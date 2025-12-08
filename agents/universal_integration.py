"""
Universal Agent Integration Framework

This module provides integration points for ALL 149+ agents across any project type,
enabling any agent to contribute to any project based on capabilities and requirements.
"""

import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
from django.db import transaction
from django.core.exceptions import ValidationError

from core.models.agents_registry import (
    UnifiedAgentTemplate,
    AgentExecution,
    AgentOrchestration,
    AgentRegistry,
    AgentChannel,
    AgentChannelMessage,
    AgentSpecialization
)
from core.models import GeneratedProject, GeneratedCode


class UniversalAgentCategories(Enum):
    """Categories covering ALL 149+ agents"""

    # Core Development (20+ agents)
    BACKEND_DEVELOPMENT = "backend-development"
    FRONTEND_DEVELOPMENT = "frontend-development"
    FULLSTACK_DEVELOPMENT = "fullstack-development"
    API_DEVELOPMENT = "api-development"
    DATABASE_DESIGN = "database-design"
    DEVOPS = "devops"

    # Machine Learning & AI (25+ agents)
    ML_ALGORITHMS = "ml-algorithms"
    DEEP_LEARNING = "deep-learning"
    NLP = "natural-language-processing"
    COMPUTER_VISION = "computer-vision"
    REINFORCEMENT_LEARNING = "reinforcement-learning"
    DATA_SCIENCE = "data-science"

    # Business & Strategy (15+ agents)
    BUSINESS_ANALYSIS = "business-analysis"
    MARKET_RESEARCH = "market-research"
    COMPETITIVE_INTELLIGENCE = "competitive-intelligence"
    PRODUCT_STRATEGY = "product-strategy"
    GROWTH_HACKING = "growth-hacking"

    # Content & Creative (20+ agents)
    CONTENT_CREATION = "content-creation"
    COPYWRITING = "copywriting"
    SEO_OPTIMIZATION = "seo-optimization"
    SOCIAL_MEDIA = "social-media"
    VIDEO_PRODUCTION = "video-production"
    GRAPHIC_DESIGN = "graphic-design"

    # Finance & Trading (15+ agents)
    FINANCIAL_ANALYSIS = "financial-analysis"
    TRADING_ALGORITHMS = "trading-algorithms"
    RISK_MANAGEMENT = "risk-management"
    PORTFOLIO_OPTIMIZATION = "portfolio-optimization"
    CRYPTO_ANALYSIS = "crypto-analysis"

    # Security & Compliance (10+ agents)
    SECURITY_AUDIT = "security-audit"
    PENETRATION_TESTING = "penetration-testing"
    COMPLIANCE_CHECK = "compliance-check"
    VULNERABILITY_SCAN = "vulnerability-scan"

    # Testing & QA (12+ agents)
    UNIT_TESTING = "unit-testing"
    INTEGRATION_TESTING = "integration-testing"
    PERFORMANCE_TESTING = "performance-testing"
    USER_TESTING = "user-testing"
    AUTOMATION_TESTING = "automation-testing"

    # Specialized Domains (20+ agents)
    SPORTS_ANALYTICS = "sports-analytics"
    HEALTHCARE_AI = "healthcare-ai"
    EDUCATION_TECH = "education-tech"
    GAMING_AI = "gaming-ai"
    IOT_SYSTEMS = "iot-systems"
    BLOCKCHAIN = "blockchain"

    # Meta & Orchestration (12+ agents)
    AGENT_ORCHESTRATION = "agent-orchestration"
    WORKFLOW_AUTOMATION = "workflow-automation"
    SYSTEM_INTEGRATION = "system-integration"
    MONITORING = "monitoring"
    SELF_AWARENESS = "self-awareness"


class UniversalAgentIntegrator:
    """
    Master integrator for connecting ANY agent to ANY project
    """

    def __init__(self):
        self.registry = self._get_or_create_registry()
        self.agent_capability_map = self._build_capability_map()

    def _get_or_create_registry(self):
        """Get or create the unified agent registry"""
        registry, _ = AgentRegistry.objects.get_or_create(
            registry_name='unified_agent_registry'
        )
        return registry

    def _build_capability_map(self) -> Dict[str, List[str]]:
        """
        Build a comprehensive map of all agent capabilities
        This maps project needs to agent capabilities
        """
        return {
            # E-commerce project needs
            'ecommerce': [
                'product-catalog-management',
                'shopping-cart-implementation',
                'payment-gateway-integration',
                'inventory-management',
                'order-processing',
                'customer-segmentation',
                'recommendation-engine',
                'dynamic-pricing',
                'fraud-detection',
                'shipping-calculator',
                'tax-computation',
                'multi-currency-support',
                'review-system',
                'wishlist-management',
                'discount-engine',
                'affiliate-tracking',
                'email-marketing',
                'abandoned-cart-recovery',
                'product-search',
                'analytics-dashboard'
            ],

            # Content platform needs
            'content_factory': [
                'content-generation',
                'seo-optimization',
                'keyword-research',
                'content-scheduling',
                'plagiarism-check',
                'grammar-correction',
                'tone-adjustment',
                'translation',
                'summarization',
                'content-categorization',
                'tag-generation',
                'image-generation',
                'video-creation',
                'podcast-production',
                'content-distribution',
                'performance-tracking',
                'competitor-analysis',
                'trend-identification',
                'content-personalization',
                'engagement-analytics'
            ],

            # Trading system needs
            'crypto_trading': [
                'market-data-collection',
                'technical-analysis',
                'fundamental-analysis',
                'sentiment-analysis',
                'risk-assessment',
                'portfolio-management',
                'order-execution',
                'backtesting',
                'strategy-optimization',
                'arbitrage-detection',
                'liquidity-analysis',
                'correlation-analysis',
                'volatility-prediction',
                'stop-loss-management',
                'position-sizing',
                'tax-reporting',
                'compliance-checking',
                'wallet-management',
                'defi-integration',
                'yield-farming'
            ],

            # Social media platform needs
            'social_media': [
                'user-authentication',
                'feed-algorithm',
                'content-moderation',
                'hashtag-trending',
                'influencer-identification',
                'engagement-prediction',
                'spam-detection',
                'community-management',
                'viral-prediction',
                'sentiment-monitoring',
                'crisis-detection',
                'content-recommendation',
                'story-creation',
                'live-streaming',
                'chat-implementation',
                'notification-system',
                'privacy-management',
                'ad-targeting',
                'analytics-reporting',
                'growth-optimization'
            ],

            # SaaS platform needs
            'saas': [
                'user-onboarding',
                'subscription-management',
                'billing-integration',
                'usage-tracking',
                'feature-flagging',
                'multi-tenancy',
                'api-rate-limiting',
                'webhook-management',
                'audit-logging',
                'role-based-access',
                'sso-integration',
                'data-export',
                'backup-management',
                'monitoring-alerts',
                'customer-support',
                'documentation-generation',
                'changelog-management',
                'upgrade-paths',
                'churn-prediction',
                'upsell-optimization'
            ],

            # Healthcare platform needs
            'healthcare': [
                'patient-management',
                'appointment-scheduling',
                'medical-records',
                'diagnosis-assistance',
                'treatment-planning',
                'drug-interaction-check',
                'insurance-verification',
                'telemedicine',
                'lab-integration',
                'prescription-management',
                'hipaa-compliance',
                'clinical-trials',
                'symptom-checker',
                'health-monitoring',
                'emergency-response',
                'referral-management',
                'billing-coding',
                'quality-metrics',
                'population-health',
                'research-analysis'
            ],

            # Education platform needs
            'education': [
                'course-creation',
                'student-management',
                'assignment-grading',
                'quiz-generation',
                'progress-tracking',
                'adaptive-learning',
                'content-recommendation',
                'plagiarism-detection',
                'video-conferencing',
                'discussion-forums',
                'certificate-generation',
                'attendance-tracking',
                'parent-portal',
                'library-management',
                'exam-proctoring',
                'learning-analytics',
                'curriculum-planning',
                'skill-assessment',
                'peer-review',
                'gamification'
            ],

            # Gaming platform needs
            'gaming': [
                'game-mechanics',
                'ai-opponents',
                'procedural-generation',
                'physics-simulation',
                'multiplayer-networking',
                'matchmaking',
                'anti-cheat',
                'leaderboards',
                'achievement-system',
                'inventory-management',
                'quest-system',
                'dialogue-trees',
                'save-system',
                'mod-support',
                'analytics-tracking',
                'monetization',
                'social-features',
                'tournament-system',
                'replay-system',
                'performance-optimization'
            ]
        }

    def discover_compatible_agents(
        self,
        project: GeneratedProject,
        context: Dict[str, Any] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Discover ALL agents that could contribute to a project

        Returns agents organized by category and relevance
        """
        project_type = project.project_type.lower()
        project_needs = self.agent_capability_map.get(project_type, [])

        # Parse project description for additional context
        description_keywords = self._extract_keywords(project.description)

        # Find all potentially compatible agents
        compatible_agents = {
            'perfect_match': [],      # Exact capability matches
            'highly_relevant': [],     # 80%+ relevance
            'relevant': [],            # 50-80% relevance
            'potentially_useful': [],  # 20-50% relevance
            'specialized': [],         # Domain-specific agents
            'support': []             # General support agents
        }

        # Query all active agents
        all_agents = UnifiedAgentTemplate.objects.filter(is_active=True)

        for agent in all_agents:
            relevance_score = self._calculate_relevance(
                agent=agent,
                project_needs=project_needs,
                keywords=description_keywords,
                context=context
            )

            # Categorize by relevance
            if relevance_score >= 0.95:
                compatible_agents['perfect_match'].append({
                    'agent': agent,
                    'score': relevance_score,
                    'reason': 'Perfect capability match for project needs'
                })
            elif relevance_score >= 0.8:
                compatible_agents['highly_relevant'].append({
                    'agent': agent,
                    'score': relevance_score,
                    'reason': 'Highly relevant capabilities'
                })
            elif relevance_score >= 0.5:
                compatible_agents['relevant'].append({
                    'agent': agent,
                    'score': relevance_score,
                    'reason': 'Relevant capabilities'
                })
            elif relevance_score >= 0.2:
                compatible_agents['potentially_useful'].append({
                    'agent': agent,
                    'score': relevance_score,
                    'reason': 'Could provide support functionality'
                })

            # Check for specialized agents
            if self._is_specialized_for_project(agent, project):
                compatible_agents['specialized'].append({
                    'agent': agent,
                    'score': 1.0,
                    'reason': f'Specialized for {project_type}'
                })

            # Include general support agents
            if agent.specialization in ['orchestration', 'self-awareness', 'monitoring']:
                compatible_agents['support'].append({
                    'agent': agent,
                    'score': 0.5,
                    'reason': 'General support and orchestration'
                })

        # Sort each category by score
        for category in compatible_agents:
            compatible_agents[category].sort(key=lambda x: x['score'], reverse=True)

        return compatible_agents

    def create_agent_integration_plan(
        self,
        project: GeneratedProject,
        selected_agents: List[str],
        integration_goals: List[str]
    ) -> Dict[str, Any]:
        """
        Create a comprehensive integration plan for selected agents
        """
        plan = {
            'project_id': str(project.id),
            'project_name': project.name,
            'integration_phases': [],
            'agent_dependencies': {},
            'execution_timeline': [],
            'resource_requirements': {},
            'success_metrics': []
        }

        # Phase 1: Foundation agents (backend, database, infrastructure)
        foundation_agents = [a for a in selected_agents if self._is_foundation_agent(a)]
        if foundation_agents:
            plan['integration_phases'].append({
                'phase': 1,
                'name': 'Foundation Setup',
                'agents': foundation_agents,
                'duration_estimate': '2-4 hours',
                'parallel_execution': False
            })

        # Phase 2: Core functionality agents
        core_agents = [a for a in selected_agents if self._is_core_agent(a) and a not in foundation_agents]
        if core_agents:
            plan['integration_phases'].append({
                'phase': 2,
                'name': 'Core Features',
                'agents': core_agents,
                'duration_estimate': '4-8 hours',
                'parallel_execution': True
            })

        # Phase 3: Enhancement agents (ML, optimization, analytics)
        enhancement_agents = [a for a in selected_agents if self._is_enhancement_agent(a)]
        if enhancement_agents:
            plan['integration_phases'].append({
                'phase': 3,
                'name': 'Advanced Features',
                'agents': enhancement_agents,
                'duration_estimate': '6-12 hours',
                'parallel_execution': True
            })

        # Phase 4: Testing and validation agents
        testing_agents = [a for a in selected_agents if self._is_testing_agent(a)]
        if testing_agents:
            plan['integration_phases'].append({
                'phase': 4,
                'name': 'Testing & Validation',
                'agents': testing_agents,
                'duration_estimate': '2-4 hours',
                'parallel_execution': True
            })

        # Phase 5: Monitoring and optimization agents
        monitoring_agents = [a for a in selected_agents if self._is_monitoring_agent(a)]
        if monitoring_agents:
            plan['integration_phases'].append({
                'phase': 5,
                'name': 'Monitoring & Optimization',
                'agents': monitoring_agents,
                'duration_estimate': '1-2 hours',
                'parallel_execution': False
            })

        # Build dependency graph
        plan['agent_dependencies'] = self._build_dependency_graph(selected_agents)

        # Create execution timeline
        plan['execution_timeline'] = self._create_execution_timeline(plan['integration_phases'])

        # Calculate resource requirements
        plan['resource_requirements'] = self._calculate_resources(selected_agents)

        # Define success metrics
        plan['success_metrics'] = self._define_success_metrics(project, integration_goals)

        return plan

    def execute_universal_deployment(
        self,
        project: GeneratedProject,
        integration_plan: Dict[str, Any],
        execution_mode: str = 'auto'
    ) -> AgentOrchestration:
        """
        Execute the universal agent deployment across all project types
        """
        with transaction.atomic():
            # Create master orchestration
            orchestration = AgentOrchestration.objects.create(
                name=f"Universal Deployment: {project.name}",
                description=f"Deploying {len(integration_plan['agent_dependencies'])} agents across {len(integration_plan['integration_phases'])} phases",
                workflow_definition=integration_plan,
                agent_sequence=self._flatten_agent_sequence(integration_plan),
                execution_strategy='adaptive',
                user=project.user
            )

            # Create communication channels for each phase
            for phase in integration_plan['integration_phases']:
                channel = AgentChannel.objects.create(
                    name=f"phase-{phase['phase']}-{project.id}",
                    display_name=f"Phase {phase['phase']}: {phase['name']}",
                    description=f"Agent collaboration for {phase['name']}",
                    channel_type='orchestration',
                    orchestration=orchestration,
                    metadata={
                        'phase': phase['phase'],
                        'agents': phase['agents'],
                        'parallel': phase['parallel_execution']
                    }
                )

                # Initial phase message
                AgentChannelMessage.objects.create(
                    channel=channel,
                    message_type='system_message',
                    content=f"Initiating Phase {phase['phase']}: {phase['name']} with {len(phase['agents'])} agents",
                    rich_content={'phase_details': phase}
                )

            # Update project metadata
            if not project.metadata:
                project.metadata = {}

            project.metadata['universal_deployment'] = {
                'orchestration_id': str(orchestration.id),
                'total_agents': len(integration_plan['agent_dependencies']),
                'phases': len(integration_plan['integration_phases']),
                'execution_mode': execution_mode,
                'started_at': datetime.now().isoformat()
            }

            # Add all agents to project tracking
            all_agents = self._flatten_agent_sequence(integration_plan)
            project.agents_used.extend(all_agents)
            project.save()

            return orchestration

    def _calculate_relevance(
        self,
        agent: UnifiedAgentTemplate,
        project_needs: List[str],
        keywords: List[str],
        context: Dict[str, Any] = None
    ) -> float:
        """Calculate relevance score for an agent"""
        score = 0.0

        # Check capability matches
        agent_capabilities = set(agent.capabilities)
        project_needs_set = set(project_needs)

        # Direct capability matches (highest weight)
        capability_matches = len(agent_capabilities.intersection(project_needs_set))
        if project_needs:
            score += (capability_matches / len(project_needs)) * 0.5

        # Keyword matches in routing keywords
        agent_keywords = set(agent.routing_keywords)
        keyword_matches = len(agent_keywords.intersection(set(keywords)))
        if keywords:
            score += (keyword_matches / len(keywords)) * 0.3

        # Specialization relevance
        if context and 'required_specialization' in context:
            if agent.specialization == context['required_specialization']:
                score += 0.2

        # Historical success rate bonus
        if agent.success_rate > 0.9:
            score *= 1.1

        return min(score, 1.0)

    def _extract_keywords(self, description: str) -> List[str]:
        """Extract relevant keywords from description"""
        # Simple keyword extraction (could be enhanced with NLP)
        import re

        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been'}

        # Extract words
        words = re.findall(r'\b\w+\b', description.lower())

        # Filter and return
        keywords = [w for w in words if w not in stop_words and len(w) > 3]

        return list(set(keywords))[:20]  # Return top 20 unique keywords

    def _is_specialized_for_project(self, agent: UnifiedAgentTemplate, project: GeneratedProject) -> bool:
        """Check if agent is specialized for this project type"""
        project_type = project.project_type.lower()

        # Check domain tags
        if project_type in agent.domain_tags:
            return True

        # Check specialization mapping
        specialization_map = {
            'ecommerce': ['business', 'marketing', 'financial'],
            'content_factory': ['content', 'creative', 'marketing'],
            'crypto_trading': ['financial', 'technical', 'risk-assessment'],
            'social_media': ['communication', 'content', 'marketing'],
            'healthcare': ['healthcare-ai', 'technical', 'compliance']
        }

        if project_type in specialization_map:
            return agent.specialization in specialization_map[project_type]

        return False

    def _is_foundation_agent(self, agent_name: str) -> bool:
        """Check if agent provides foundation functionality"""
        foundation_keywords = ['database', 'api', 'backend', 'infrastructure', 'setup', 'initialization']
        return any(keyword in agent_name.lower() for keyword in foundation_keywords)

    def _is_core_agent(self, agent_name: str) -> bool:
        """Check if agent provides core functionality"""
        core_keywords = ['core', 'main', 'primary', 'essential', 'basic', 'fundamental']
        return any(keyword in agent_name.lower() for keyword in core_keywords)

    def _is_enhancement_agent(self, agent_name: str) -> bool:
        """Check if agent provides enhancement functionality"""
        enhancement_keywords = ['ml', 'ai', 'optimization', 'advanced', 'premium', 'enhanced']
        return any(keyword in agent_name.lower() for keyword in enhancement_keywords)

    def _is_testing_agent(self, agent_name: str) -> bool:
        """Check if agent provides testing functionality"""
        testing_keywords = ['test', 'qa', 'quality', 'validation', 'verification', 'audit']
        return any(keyword in agent_name.lower() for keyword in testing_keywords)

    def _is_monitoring_agent(self, agent_name: str) -> bool:
        """Check if agent provides monitoring functionality"""
        monitoring_keywords = ['monitor', 'tracking', 'analytics', 'metrics', 'observability', 'logging']
        return any(keyword in agent_name.lower() for keyword in monitoring_keywords)

    def _build_dependency_graph(self, agents: List[str]) -> Dict[str, List[str]]:
        """Build dependency graph for agents"""
        dependencies = {}

        for agent in agents:
            deps = []

            # Database agents depend on nothing
            if 'database' in agent.lower():
                deps = []
            # API agents depend on database
            elif 'api' in agent.lower():
                deps = [a for a in agents if 'database' in a.lower()]
            # Frontend depends on API
            elif 'frontend' in agent.lower() or 'ui' in agent.lower():
                deps = [a for a in agents if 'api' in a.lower()]
            # ML agents depend on data infrastructure
            elif 'ml' in agent.lower() or 'ai' in agent.lower():
                deps = [a for a in agents if 'database' in a.lower() or 'data' in a.lower()]
            # Testing depends on implementation
            elif 'test' in agent.lower():
                deps = [a for a in agents if not 'test' in a.lower() and not 'monitor' in a.lower()]
            # Monitoring depends on everything
            elif 'monitor' in agent.lower():
                deps = [a for a in agents if a != agent]

            dependencies[agent] = deps

        return dependencies

    def _create_execution_timeline(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create execution timeline"""
        timeline = []
        current_time = 0

        for phase in phases:
            # Parse duration estimate
            duration_parts = phase['duration_estimate'].split('-')
            min_duration = int(duration_parts[0])
            max_duration = int(duration_parts[1].split()[0])
            avg_duration = (min_duration + max_duration) / 2

            timeline.append({
                'phase': phase['phase'],
                'name': phase['name'],
                'start_hour': current_time,
                'end_hour': current_time + avg_duration,
                'agents': len(phase['agents']),
                'parallel': phase['parallel_execution']
            })

            current_time += avg_duration

        return timeline

    def _calculate_resources(self, agents: List[str]) -> Dict[str, Any]:
        """Calculate resource requirements"""
        return {
            'estimated_tokens': len(agents) * 5000,  # Average tokens per agent
            'estimated_cost_usd': len(agents) * 0.10,  # Average cost per agent
            'estimated_time_hours': len(agents) * 0.5,  # Average time per agent
            'parallel_capacity': min(10, len(agents)),  # Max parallel executions
            'memory_requirement_mb': len(agents) * 100  # Memory per agent
        }

    def _define_success_metrics(self, project: GeneratedProject, goals: List[str]) -> List[Dict[str, Any]]:
        """Define success metrics"""
        metrics = [
            {
                'metric': 'agent_completion_rate',
                'target': 95,
                'unit': 'percentage',
                'description': 'Percentage of agents completing successfully'
            },
            {
                'metric': 'integration_time',
                'target': 24,
                'unit': 'hours',
                'description': 'Total time to complete all integrations'
            },
            {
                'metric': 'error_rate',
                'target': 5,
                'unit': 'percentage',
                'description': 'Maximum acceptable error rate'
            }
        ]

        # Add goal-specific metrics
        for goal in goals:
            if 'performance' in goal.lower():
                metrics.append({
                    'metric': 'performance_improvement',
                    'target': 50,
                    'unit': 'percentage',
                    'description': 'Performance improvement over baseline'
                })
            elif 'revenue' in goal.lower():
                metrics.append({
                    'metric': 'revenue_increase',
                    'target': 30,
                    'unit': 'percentage',
                    'description': 'Revenue increase from agent optimization'
                })
            elif 'user' in goal.lower():
                metrics.append({
                    'metric': 'user_satisfaction',
                    'target': 4.5,
                    'unit': 'rating',
                    'description': 'User satisfaction score'
                })

        return metrics

    def _flatten_agent_sequence(self, plan: Dict[str, Any]) -> List[str]:
        """Flatten agent sequence from phases"""
        sequence = []
        for phase in plan['integration_phases']:
            sequence.extend(phase['agents'])
        return sequence