"""
Self-Awareness Engine
Gives the system knowledge of its own state, capabilities, and performance

The system can now:
- Understand what it knows
- Know what it doesn't know
- Assess its own performance
- Identify its own limitations
- Recommend self-improvements
"""

import logging
from typing import Dict, List, Optional
from django.db.models import Count, Avg, Q, F
from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


class SelfAwarenessEngine:
    """
    System self-awareness and introspection

    Provides:
    - Capability inventory
    - Performance self-assessment
    - Knowledge gaps identification
    - Autonomous improvement suggestions
    - System health monitoring
    """

    def get_system_capabilities(self) -> Dict:
        """
        Comprehensive inventory of what the system can do

        Returns: Complete capability matrix
        """
        from core.models_unified_system import Agent
        from persistence.models import SpiderData

        capabilities = {
            'agent_capabilities': {},
            'data_capabilities': {},
            'learning_capabilities': {},
            'integration_capabilities': {},
            'total_capability_score': 0
        }

        # Agent capabilities
        agents = Agent.objects.all()
        capabilities['agent_capabilities'] = {
            'total_agents': agents.count(),
            'by_specialization': self._categorize_agents(agents),
            'operational_agents': agents.filter(is_active=True).count(),
            'agent_types': list(agents.values_list('agent_type', flat=True).distinct())
        }

        # Data capabilities
        spider_count = SpiderData.objects.values('spider_name').distinct().count()
        capabilities['data_capabilities'] = {
            'spider_types': spider_count,
            'total_data_points': SpiderData.objects.count(),
            'data_domains': self._identify_data_domains()
        }

        # Learning capabilities
        capabilities['learning_capabilities'] = self._assess_learning_capabilities()

        # Integration capabilities
        capabilities['integration_capabilities'] = self._assess_integrations()

        # Calculate total capability score
        capabilities['total_capability_score'] = self._calculate_capability_score(capabilities)

        return capabilities

    def _categorize_agents(self, agents) -> Dict:
        """Categorize agents by their capabilities"""
        categories = {}

        for agent in agents:
            spec = agent.specialization.lower() if agent.specialization else 'general'

            # Determine category
            if any(word in spec for word in ['research', 'analysis', 'data']):
                category = 'research_analysis'
            elif any(word in spec for word in ['content', 'writing', 'creative']):
                category = 'content_creation'
            elif any(word in spec for word in ['code', 'development', 'technical']):
                category = 'development'
            elif any(word in spec for word in ['strategy', 'planning', 'business']):
                category = 'strategy_planning'
            elif any(word in spec for word in ['automation', 'workflow', 'task']):
                category = 'automation'
            else:
                category = 'general'

            if category not in categories:
                categories[category] = {'count': 0, 'agents': []}

            categories[category]['count'] += 1
            categories[category]['agents'].append(agent.name)

        return categories

    def _identify_data_domains(self) -> List[str]:
        """Identify what data domains we have coverage for"""
        from persistence.models import SpiderData

        # Get unique spider names and categorize
        spider_names = SpiderData.objects.values_list('spider_name', flat=True).distinct()

        domains = set()
        for spider in spider_names:
            spider_lower = spider.lower()

            if any(word in spider_lower for word in ['job', 'freelance', 'work', 'guru', 'upwork']):
                domains.add('employment')
            if any(word in spider_lower for word in ['financial', 'market', 'stock', 'crypto']):
                domains.add('finance')
            if any(word in spider_lower for word in ['social', 'media', 'twitter', 'reddit']):
                domains.add('social_media')
            if any(word in spider_lower for word in ['news', 'article', 'blog']):
                domains.add('news_content')
            if any(word in spider_lower for word in ['sports', 'betting', 'odds']):
                domains.add('sports_analytics')
            if any(word in spider_lower for word in ['legal', 'law', 'court']):
                domains.add('legal')

        return list(domains)

    def _assess_learning_capabilities(self) -> Dict:
        """Assess the system's learning capabilities"""
        from core.models_unified_system import UserAgentLearning

        learning_caps = {
            'total_learning_records': UserAgentLearning.objects.count(),
            'learning_domains': list(
                UserAgentLearning.objects.values_list('learning_domain', flat=True).distinct()
            ),
            'high_confidence_learning': UserAgentLearning.objects.filter(
                confidence_score__gte=0.7
            ).count(),
            'learning_bridges_active': [
                'collaboration', 'agent_execution', 'spider_data',
                'revenue_attribution', 'application_outcome',
                'personalization', 'advisor_feedback', 'sports_betting'
            ]
        }

        return learning_caps

    def _assess_integrations(self) -> Dict:
        """Assess what integrations are active"""
        integrations = {
            'websocket_channels': ['personal_assistant', 'income_builder', 'monetization_hub'],
            'learning_orchestrator': True,
            'collaboration_optimizer': True,
            'self_awareness': True,
            'database_systems': ['PostgreSQL', 'Redis'],
            'llm_providers': ['OpenAI', 'Anthropic']
        }

        return integrations

    def _calculate_capability_score(self, capabilities: Dict) -> float:
        """Calculate overall capability score (0-100)"""
        score = 0

        # Agent coverage (40 points max)
        agent_count = capabilities['agent_capabilities']['total_agents']
        score += min(40, (agent_count / 200) * 40)

        # Data coverage (30 points max)
        data_points = capabilities['data_capabilities']['total_data_points']
        score += min(30, (data_points / 300000) * 30)

        # Learning capability (20 points max)
        learning_records = capabilities['learning_capabilities']['total_learning_records']
        score += min(20, (learning_records / 1000) * 20)

        # Integration completeness (10 points max)
        integrations = capabilities['integration_capabilities']
        active_count = sum(1 for v in integrations.values() if (isinstance(v, bool) and v) or (isinstance(v, list) and len(v) > 0))
        score += min(10, (active_count / len(integrations)) * 10)

        return round(score, 1)

    def assess_performance(self, user) -> Dict:
        """
        Self-assess system performance for a user

        Returns: Performance metrics and self-assessment
        """
        from core.models_unified_system import UserAgentLearning, AgentExecution

        assessment = {
            'overall_performance': 0,
            'strengths': [],
            'weaknesses': [],
            'improvement_areas': [],
            'confidence_level': 0
        }

        # Get learning data
        learning = UserAgentLearning.objects.filter(user=user)

        if not learning.exists():
            assessment['confidence_level'] = 0.1
            assessment['weaknesses'].append('No learning data - system needs usage to assess performance')
            return assessment

        # Calculate average confidence across all learning
        avg_confidence = learning.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0
        assessment['confidence_level'] = round(float(avg_confidence), 2)

        # Identify strengths (high confidence areas)
        strengths = learning.filter(confidence_score__gte=0.7).values('learning_domain').annotate(
            count=Count('id'),
            avg_conf=Avg('confidence_score')
        ).order_by('-avg_conf')[:5]

        for strength in strengths:
            assessment['strengths'].append({
                'domain': strength['learning_domain'],
                'confidence': round(float(strength['avg_conf']), 2),
                'learning_count': strength['count']
            })

        # Identify weaknesses (low confidence areas)
        weaknesses = learning.filter(confidence_score__lt=0.5).values('learning_domain').annotate(
            count=Count('id'),
            avg_conf=Avg('confidence_score')
        ).order_by('avg_conf')[:5]

        for weakness in weaknesses:
            assessment['weaknesses'].append({
                'domain': weakness['learning_domain'],
                'confidence': round(float(weakness['avg_conf']), 2),
                'issue': 'Low confidence - needs more successful executions'
            })

        # Calculate overall performance
        total_executions = AgentExecution.objects.filter(user=user).count()
        successful_executions = AgentExecution.objects.filter(
            user=user, status='completed'
        ).count()

        if total_executions > 0:
            success_rate = successful_executions / total_executions
            assessment['overall_performance'] = round(success_rate * 100, 1)

        # Identify improvement areas
        assessment['improvement_areas'] = self._identify_improvements(assessment)

        return assessment

    def _identify_improvements(self, assessment: Dict) -> List[Dict]:
        """Identify specific improvement areas"""
        improvements = []

        # Low overall performance
        if assessment['overall_performance'] < 70:
            improvements.append({
                'area': 'Overall Performance',
                'current': assessment['overall_performance'],
                'target': 85,
                'suggestion': 'Focus on high-confidence agents and tasks'
            })

        # Low confidence level
        if assessment['confidence_level'] < 0.6:
            improvements.append({
                'area': 'System Confidence',
                'current': assessment['confidence_level'],
                'target': 0.75,
                'suggestion': 'More agent executions needed to build confidence'
            })

        # Weaknesses identified
        for weakness in assessment['weaknesses'][:3]:
            improvements.append({
                'area': weakness['domain'],
                'current': weakness['confidence'],
                'target': 0.7,
                'suggestion': f"Practice {weakness['domain']} tasks to build confidence"
            })

        return improvements

    def identify_knowledge_gaps(self, user) -> Dict:
        """
        Identify what the system doesn't know or can't do well

        This is meta-cognition: knowing what we don't know
        """
        from core.models_unified_system import Agent, UserAgentLearning, AgentExecution

        gaps = {
            'unused_agents': [],
            'low_coverage_domains': [],
            'missing_capabilities': [],
            'data_gaps': []
        }

        # Unused agents (registered but never executed)
        all_agents = Agent.objects.all()
        executed_agents = AgentExecution.objects.filter(
            user=user
        ).values_list('agent__name', flat=True).distinct()

        for agent in all_agents:
            if agent.name not in executed_agents:
                gaps['unused_agents'].append({
                    'agent': agent.name,
                    'specialization': agent.specialization,
                    'reason': 'Never executed - capability unknown'
                })

        # Low coverage domains
        learning_domains = UserAgentLearning.objects.filter(
            user=user
        ).values('learning_domain').annotate(
            count=Count('id'),
            avg_conf=Avg('confidence_score')
        )

        for domain_data in learning_domains:
            if domain_data['count'] < 5 or float(domain_data['avg_conf'] or 0) < 0.5:
                gaps['low_coverage_domains'].append({
                    'domain': domain_data['learning_domain'],
                    'execution_count': domain_data['count'],
                    'confidence': round(float(domain_data['avg_conf'] or 0), 2),
                    'reason': 'Insufficient data or low confidence'
                })

        return gaps

    def recommend_self_improvements(self, user) -> List[Dict]:
        """
        Autonomous recommendations for system self-improvement

        The system recommends how to improve itself
        """
        recommendations = []

        # Get current capabilities and performance
        capabilities = self.get_system_capabilities()
        performance = self.assess_performance(user)
        gaps = self.identify_knowledge_gaps(user)

        # Recommend using unused agents
        if gaps['unused_agents']:
            recommendations.append({
                'priority': 'high',
                'category': 'capability_expansion',
                'action': 'activate_unused_agents',
                'details': f"Activate {len(gaps['unused_agents'][:5])} unused agents to expand capabilities",
                'agents': [a['agent'] for a in gaps['unused_agents'][:5]],
                'expected_benefit': 'Discover new capabilities and improve coverage'
            })

        # Recommend focusing on weaknesses
        if performance['weaknesses']:
            recommendations.append({
                'priority': 'medium',
                'category': 'performance_improvement',
                'action': 'strengthen_weak_domains',
                'details': f"Practice {len(performance['weaknesses'])} weak domains to build confidence",
                'domains': [w['domain'] for w in performance['weaknesses']],
                'expected_benefit': 'Increase overall system confidence and reliability'
            })

        # Recommend leveraging strengths
        if performance['strengths']:
            recommendations.append({
                'priority': 'low',
                'category': 'optimization',
                'action': 'leverage_strengths',
                'details': f"Prioritize {len(performance['strengths'])} strong domains for best results",
                'domains': [s['domain'] for s in performance['strengths']],
                'expected_benefit': 'Maximize success rate and user satisfaction'
            })

        # Recommend data collection
        if len(gaps['low_coverage_domains']) > 5:
            recommendations.append({
                'priority': 'high',
                'category': 'learning_enhancement',
                'action': 'increase_data_collection',
                'details': f"Execute tasks in {len(gaps['low_coverage_domains'])} low-coverage domains",
                'domains': [d['domain'] for d in gaps['low_coverage_domains'][:5]],
                'expected_benefit': 'Build comprehensive knowledge base'
            })

        return recommendations

    def generate_self_report(self, user) -> str:
        """
        Generate a comprehensive self-awareness report

        The system writes its own status report
        """
        capabilities = self.get_system_capabilities()
        performance = self.assess_performance(user)
        gaps = self.identify_knowledge_gaps(user)
        recommendations = self.recommend_self_improvements(user)

        report = f"""
# System Self-Awareness Report

## Overall Status
- **Capability Score:** {capabilities['total_capability_score']}/100
- **Performance:** {performance['overall_performance']}%
- **Confidence Level:** {performance['confidence_level']:.0%}

## What I Know I Can Do Well
"""

        for strength in performance['strengths'][:5]:
            report += f"- {strength['domain']} ({strength['confidence']:.0%} confidence, {strength['learning_count']} experiences)\n"

        report += "\n## What I Know I Can't Do Well\n"

        for weakness in performance['weaknesses'][:5]:
            report += f"- {weakness['domain']} ({weakness['confidence']:.0%} confidence - {weakness['issue']})\n"

        report += f"\n## What I Don't Know Yet\n"
        report += f"- {len(gaps['unused_agents'])} agents never used\n"
        report += f"- {len(gaps['low_coverage_domains'])} domains with low coverage\n"

        report += "\n## My Recommendations for Self-Improvement\n"

        for rec in recommendations[:5]:
            report += f"\n### {rec['category'].replace('_', ' ').title()} (Priority: {rec['priority']})\n"
            report += f"{rec['details']}\n"
            report += f"**Expected Benefit:** {rec['expected_benefit']}\n"

        report += "\n---\n"
        report += "*This report was autonomously generated by the Self-Awareness Engine*"

        return report


# Singleton instance
self_awareness = SelfAwarenessEngine()
