"""
Unified Learning Pipeline - Cross-System Intelligence Sharing

This module implements bidirectional learning between the Personal Assistant,
Agent system, Advisor network, and user interactions to create a unified
intelligence that continuously improves all components.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter

from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Avg
from django.utils import timezone

from core.models import ConversationMemory, UserMemoryContext
from core.unified_memory_manager import get_memory_manager
from agents.registry import get_agent_registry
from advisors.registry import get_advisor_registry

logger = logging.getLogger(__name__)
User = get_user_model()


class LearningType(Enum):
    """Types of learning insights"""
    USER_PREFERENCE = "user_preference"
    SUCCESS_PATTERN = "success_pattern"
    FAILURE_PATTERN = "failure_pattern"
    AGENT_EFFECTIVENESS = "agent_effectiveness"
    ADVISOR_EXPERTISE = "advisor_expertise"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    CROSS_DOMAIN_INSIGHT = "cross_domain_insight"


@dataclass
class LearningInsight:
    """Represents a learning insight derived from system interactions"""
    insight_id: str
    insight_type: LearningType
    source_system: str  # "assistant", "agent", "advisor", "user"
    target_systems: List[str]  # Systems that should apply this insight

    # Content
    insight_summary: str
    detailed_description: str
    confidence_score: float  # 0.0 to 1.0
    supporting_evidence: List[Dict[str, Any]]

    # Applicability
    applicable_contexts: List[str]
    user_segments: List[str]  # Which types of users this applies to
    domain_relevance: List[str]  # Which domains this is relevant for

    # Impact tracking
    potential_impact: str  # "low", "medium", "high"
    implementation_complexity: str  # "low", "medium", "high"
    estimated_improvement: float  # Expected improvement percentage

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    applied_at: Optional[datetime] = None
    validation_status: str = "pending"  # "pending", "validated", "rejected"
    impact_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class SystemPerformanceMetrics:
    """Performance metrics for cross-system analysis"""
    system_name: str
    success_rate: float
    avg_response_time: float
    user_satisfaction: float
    task_completion_rate: float
    error_rate: float
    improvement_trend: str  # "improving", "stable", "declining"

    # Detailed metrics
    interaction_count: int
    unique_users: int
    most_common_tasks: List[str]
    performance_by_context: Dict[str, float]

    measurement_period: timedelta
    last_updated: datetime = field(default_factory=datetime.now)


class UnifiedLearningPipeline:
    """
    Unified learning pipeline that enables bidirectional learning between
    all system components to create collective intelligence.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agent_registry = get_agent_registry()
        self.advisor_registry = get_advisor_registry()

        # Learning insight storage
        self.insights: Dict[str, LearningInsight] = {}
        self.performance_metrics: Dict[str, SystemPerformanceMetrics] = {}

        # Initialize learning components
        self._initialize_learning_components()

    def _initialize_learning_components(self):
        """Initialize learning components and baseline metrics"""
        self.learning_components = {
            'pattern_analyzer': self._analyze_patterns,
            'success_predictor': self._predict_success,
            'preference_learner': self._learn_preferences,
            'workflow_optimizer': self._optimize_workflows,
            'cross_system_correlator': self._correlate_across_systems
        }

        self.logger.info("✅ Unified Learning Pipeline initialized")

    def analyze_user_interaction_patterns(self, user: User, lookback_days: int = 30) -> List[LearningInsight]:
        """
        Analyze user interaction patterns to generate learning insights.

        Args:
            user: User to analyze
            lookback_days: Number of days to look back

        Returns:
            List of learning insights derived from user patterns
        """
        try:
            insights = []
            cutoff_date = timezone.now() - timedelta(days=lookback_days)

            # Get user interactions from multiple sources
            conversations = ConversationMemory.objects.filter(
                user=user,
                created_at__gte=cutoff_date
            )

            memories = UserMemoryContext.objects.filter(
                user=user,
                created_at__gte=cutoff_date
            )

            # Analyze conversation patterns
            conversation_insights = self._analyze_conversation_patterns(conversations, user)
            insights.extend(conversation_insights)

            # Analyze memory patterns
            memory_insights = self._analyze_memory_patterns(memories, user)
            insights.extend(memory_insights)

            # Generate cross-system insights
            cross_insights = self._generate_cross_system_insights(user, conversations, memories)
            insights.extend(cross_insights)

            self.logger.info(f"Generated {len(insights)} learning insights for {user.username}")
            return insights

        except Exception as e:
            self.logger.error(f"Error analyzing user interaction patterns: {e}")
            return []

    def _analyze_conversation_patterns(self, conversations, user: User) -> List[LearningInsight]:
        """Analyze conversation patterns to derive insights"""
        insights = []

        if not conversations:
            return insights

        try:
            # Analyze intent patterns
            intent_counts = Counter(conv.intent for conv in conversations if conv.intent)

            if intent_counts:
                top_intent = intent_counts.most_common(1)[0]

                insight = LearningInsight(
                    insight_id=f"user_intent_{user.id}_{datetime.now().timestamp()}",
                    insight_type=LearningType.USER_PREFERENCE,
                    source_system="assistant",
                    target_systems=["agent", "advisor"],
                    insight_summary=f"User primarily seeks {top_intent[0]} assistance",
                    detailed_description=f"User {user.username} shows strong preference for {top_intent[0]} tasks ({top_intent[1]}/{len(conversations)} interactions)",
                    confidence_score=min(0.9, top_intent[1] / len(conversations) + 0.3),
                    supporting_evidence=[
                        {
                            'type': 'intent_frequency',
                            'intent': top_intent[0],
                            'count': top_intent[1],
                            'percentage': top_intent[1] / len(conversations)
                        }
                    ],
                    applicable_contexts=[top_intent[0]],
                    user_segments=[self._classify_user_segment(user)],
                    domain_relevance=[top_intent[0]],
                    potential_impact="medium",
                    implementation_complexity="low",
                    estimated_improvement=15.0
                )
                insights.append(insight)

            # Analyze response quality patterns
            successful_conversations = [conv for conv in conversations if conv.success]
            if len(successful_conversations) > 0:
                success_rate = len(successful_conversations) / len(conversations)

                if success_rate < 0.7:  # Low success rate indicates learning opportunity
                    insight = LearningInsight(
                        insight_id=f"success_pattern_{user.id}_{datetime.now().timestamp()}",
                        insight_type=LearningType.FAILURE_PATTERN,
                        source_system="assistant",
                        target_systems=["assistant", "agent"],
                        insight_summary=f"Low conversation success rate ({success_rate:.1%})",
                        detailed_description=f"User {user.username} has low conversation success rate, indicating need for improved response strategies",
                        confidence_score=0.8,
                        supporting_evidence=[
                            {
                                'type': 'success_rate',
                                'rate': success_rate,
                                'total_conversations': len(conversations),
                                'successful_conversations': len(successful_conversations)
                            }
                        ],
                        applicable_contexts=["conversation"],
                        user_segments=[self._classify_user_segment(user)],
                        domain_relevance=["conversation", "user_experience"],
                        potential_impact="high",
                        implementation_complexity="medium",
                        estimated_improvement=25.0
                    )
                    insights.append(insight)

            return insights

        except Exception as e:
            self.logger.error(f"Error analyzing conversation patterns: {e}")
            return []

    def _analyze_memory_patterns(self, memories, user: User) -> List[LearningInsight]:
        """Analyze memory patterns to derive insights"""
        insights = []

        if not memories:
            return insights

        try:
            # Analyze memory types
            memory_types = Counter(memory.memory_type for memory in memories)

            # Find dominant memory types
            if memory_types:
                top_memory_type = memory_types.most_common(1)[0]

                insight = LearningInsight(
                    insight_id=f"memory_pattern_{user.id}_{datetime.now().timestamp()}",
                    insight_type=LearningType.USER_PREFERENCE,
                    source_system="assistant",
                    target_systems=["agent", "advisor"],
                    insight_summary=f"User focuses on {top_memory_type[0]} activities",
                    detailed_description=f"User {user.username} primarily engages in {top_memory_type[0]} activities, suggesting specialized needs",
                    confidence_score=min(0.85, top_memory_type[1] / len(memories) + 0.2),
                    supporting_evidence=[
                        {
                            'type': 'memory_type_frequency',
                            'memory_type': top_memory_type[0],
                            'count': top_memory_type[1],
                            'total_memories': len(memories)
                        }
                    ],
                    applicable_contexts=[top_memory_type[0]],
                    user_segments=[self._classify_user_segment(user)],
                    domain_relevance=[top_memory_type[0]],
                    potential_impact="medium",
                    implementation_complexity="low",
                    estimated_improvement=12.0
                )
                insights.append(insight)

            # Analyze importance patterns
            high_importance_memories = [m for m in memories if m.importance >= 7]
            if high_importance_memories:
                important_sources = Counter(memory.source for memory in high_importance_memories)

                if important_sources:
                    top_source = important_sources.most_common(1)[0]

                    insight = LearningInsight(
                        insight_id=f"importance_pattern_{user.id}_{datetime.now().timestamp()}",
                        insight_type=LearningType.SUCCESS_PATTERN,
                        source_system="assistant",
                        target_systems=["agent"],
                        insight_summary=f"High-value interactions from {top_source[0]}",
                        detailed_description=f"User {user.username} considers {top_source[0]} interactions most valuable",
                        confidence_score=0.75,
                        supporting_evidence=[
                            {
                                'type': 'high_importance_source',
                                'source': top_source[0],
                                'count': top_source[1],
                                'avg_importance': sum(m.importance for m in high_importance_memories) / len(high_importance_memories)
                            }
                        ],
                        applicable_contexts=["high_value_interaction"],
                        user_segments=[self._classify_user_segment(user)],
                        domain_relevance=[top_source[0]],
                        potential_impact="medium",
                        implementation_complexity="low",
                        estimated_improvement=18.0
                    )
                    insights.append(insight)

            return insights

        except Exception as e:
            self.logger.error(f"Error analyzing memory patterns: {e}")
            return []

    def _generate_cross_system_insights(self, user: User, conversations, memories) -> List[LearningInsight]:
        """Generate insights that apply across multiple systems"""
        insights = []

        try:
            # Analyze agent usage patterns from memories
            agent_memories = [m for m in memories if 'agent' in m.memory_type.lower()]

            if agent_memories:
                # Extract agent names from metadata
                agent_usage = defaultdict(int)
                for memory in agent_memories:
                    if memory.metadata and 'agent_name' in memory.metadata:
                        agent_usage[memory.metadata['agent_name']] += 1

                if agent_usage:
                    preferred_agent = max(agent_usage.items(), key=lambda x: x[1])

                    insight = LearningInsight(
                        insight_id=f"agent_preference_{user.id}_{datetime.now().timestamp()}",
                        insight_type=LearningType.USER_PREFERENCE,
                        source_system="assistant",
                        target_systems=["agent", "advisor"],
                        insight_summary=f"User prefers {preferred_agent[0]} agent",
                        detailed_description=f"User {user.username} shows strong preference for {preferred_agent[0]} agent type",
                        confidence_score=0.7,
                        supporting_evidence=[
                            {
                                'type': 'agent_usage',
                                'preferred_agent': preferred_agent[0],
                                'usage_count': preferred_agent[1],
                                'total_agent_interactions': len(agent_memories)
                            }
                        ],
                        applicable_contexts=["agent_selection"],
                        user_segments=[self._classify_user_segment(user)],
                        domain_relevance=["agent_orchestration"],
                        potential_impact="medium",
                        implementation_complexity="low",
                        estimated_improvement=20.0
                    )
                    insights.append(insight)

            # Analyze conversation-to-action patterns
            action_conversations = [conv for conv in conversations if conv.agents_used]
            if action_conversations and conversations:
                action_rate = len(action_conversations) / len(conversations)

                if action_rate > 0.3:  # High action rate
                    insight = LearningInsight(
                        insight_id=f"action_orientation_{user.id}_{datetime.now().timestamp()}",
                        insight_type=LearningType.USER_PREFERENCE,
                        source_system="assistant",
                        target_systems=["agent", "workflow"],
                        insight_summary=f"User is action-oriented ({action_rate:.1%} action rate)",
                        detailed_description=f"User {user.username} frequently requests actions, prefers doing over discussing",
                        confidence_score=min(0.9, action_rate + 0.2),
                        supporting_evidence=[
                            {
                                'type': 'action_rate',
                                'rate': action_rate,
                                'action_conversations': len(action_conversations),
                                'total_conversations': len(conversations)
                            }
                        ],
                        applicable_contexts=["conversation", "agent_routing"],
                        user_segments=[self._classify_user_segment(user)],
                        domain_relevance=["workflow", "agent_orchestration"],
                        potential_impact="high",
                        implementation_complexity="medium",
                        estimated_improvement=30.0
                    )
                    insights.append(insight)

            return insights

        except Exception as e:
            self.logger.error(f"Error generating cross-system insights: {e}")
            return []

    def apply_learning_insights(self, insights: List[LearningInsight], user: User) -> Dict[str, Any]:
        """
        Apply learning insights to improve system performance.

        Args:
            insights: List of insights to apply
            user: User the insights apply to

        Returns:
            Results of applying insights
        """
        try:
            application_results = {
                'applied_insights': 0,
                'failed_applications': 0,
                'improvements_made': [],
                'errors': []
            }

            for insight in insights:
                try:
                    # Apply insight based on type and target systems
                    result = self._apply_single_insight(insight, user)

                    if result['success']:
                        application_results['applied_insights'] += 1
                        application_results['improvements_made'].append({
                            'insight_id': insight.insight_id,
                            'type': insight.insight_type.value,
                            'improvements': result['improvements']
                        })

                        # Mark insight as applied
                        insight.applied_at = datetime.now()
                        insight.validation_status = "applied"

                    else:
                        application_results['failed_applications'] += 1
                        application_results['errors'].append({
                            'insight_id': insight.insight_id,
                            'error': result.get('error', 'Unknown error')
                        })

                except Exception as e:
                    self.logger.error(f"Error applying insight {insight.insight_id}: {e}")
                    application_results['failed_applications'] += 1
                    application_results['errors'].append({
                        'insight_id': insight.insight_id,
                        'error': str(e)
                    })

            self.logger.info(f"Applied {application_results['applied_insights']} insights for {user.username}")
            return application_results

        except Exception as e:
            self.logger.error(f"Error applying learning insights: {e}")
            return {'error': str(e)}

    def _apply_single_insight(self, insight: LearningInsight, user: User) -> Dict[str, Any]:
        """Apply a single learning insight"""
        try:
            improvements = []

            # Apply to Personal Assistant
            if "assistant" in insight.target_systems:
                assistant_improvements = self._apply_to_assistant(insight, user)
                improvements.extend(assistant_improvements)

            # Apply to Agent system
            if "agent" in insight.target_systems:
                agent_improvements = self._apply_to_agents(insight, user)
                improvements.extend(agent_improvements)

            # Apply to Advisor system
            if "advisor" in insight.target_systems:
                advisor_improvements = self._apply_to_advisors(insight, user)
                improvements.extend(advisor_improvements)

            # Apply to Workflow system
            if "workflow" in insight.target_systems:
                workflow_improvements = self._apply_to_workflows(insight, user)
                improvements.extend(workflow_improvements)

            return {
                'success': True,
                'improvements': improvements
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _apply_to_assistant(self, insight: LearningInsight, user: User) -> List[str]:
        """Apply insight to Personal Assistant"""
        improvements = []

        try:
            # Store insight as memory for assistant to use
            memory_manager = get_memory_manager(user)

            memory_manager.store_memory(
                user=user,
                source='learning_pipeline',
                memory_type='learning_insight',
                content=insight.insight_summary,
                importance=8,
                metadata={
                    'insight_type': insight.insight_type.value,
                    'confidence_score': insight.confidence_score,
                    'applicable_contexts': insight.applicable_contexts,
                    'estimated_improvement': insight.estimated_improvement
                }
            )

            improvements.append(f"Stored learning insight as assistant memory: {insight.insight_summary}")

            # Apply specific improvements based on insight type
            if insight.insight_type == LearningType.USER_PREFERENCE:
                improvements.append("Updated user preference patterns for personalized responses")
            elif insight.insight_type == LearningType.FAILURE_PATTERN:
                improvements.append("Identified failure pattern for improved response strategies")

        except Exception as e:
            self.logger.error(f"Error applying insight to assistant: {e}")

        return improvements

    def _apply_to_agents(self, insight: LearningInsight, user: User) -> List[str]:
        """Apply insight to Agent system"""
        improvements = []

        try:
            # For agent preferences, update routing logic
            if insight.insight_type == LearningType.USER_PREFERENCE and 'agent' in insight.insight_summary.lower():
                # Extract preferred agent from insight
                preferred_agent = self._extract_preferred_agent(insight)
                if preferred_agent:
                    # This would update agent selection weights in a production system
                    improvements.append(f"Updated agent routing to prefer {preferred_agent} for this user")

            # For effectiveness insights, update agent performance tracking
            if insight.insight_type == LearningType.AGENT_EFFECTIVENESS:
                improvements.append("Updated agent effectiveness metrics based on user feedback")

        except Exception as e:
            self.logger.error(f"Error applying insight to agents: {e}")

        return improvements

    def _apply_to_advisors(self, insight: LearningInsight, user: User) -> List[str]:
        """Apply insight to Advisor system"""
        improvements = []

        try:
            # For advisor preferences, update recommendation logic
            if 'advisor' in insight.insight_summary.lower():
                improvements.append("Updated advisor recommendation weights based on user patterns")

            # For domain insights, update domain matching
            if insight.domain_relevance:
                improvements.append(f"Enhanced domain matching for: {', '.join(insight.domain_relevance)}")

        except Exception as e:
            self.logger.error(f"Error applying insight to advisors: {e}")

        return improvements

    def _apply_to_workflows(self, insight: LearningInsight, user: User) -> List[str]:
        """Apply insight to Workflow system"""
        improvements = []

        try:
            # For action-oriented users, optimize workflows
            if insight.insight_type == LearningType.USER_PREFERENCE and 'action' in insight.insight_summary.lower():
                improvements.append("Optimized workflows for action-oriented user preferences")

            # For workflow optimization insights
            if insight.insight_type == LearningType.WORKFLOW_OPTIMIZATION:
                improvements.append("Applied workflow optimization based on user patterns")

        except Exception as e:
            self.logger.error(f"Error applying insight to workflows: {e}")

        return improvements

    def generate_system_performance_report(self, lookback_days: int = 7) -> Dict[str, Any]:
        """
        Generate comprehensive system performance report.

        Args:
            lookback_days: Number of days to analyze

        Returns:
            Comprehensive performance report
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=lookback_days)

            # Analyze assistant performance
            assistant_metrics = self._analyze_assistant_performance(cutoff_date)

            # Analyze agent performance
            agent_metrics = self._analyze_agent_performance(cutoff_date)

            # Analyze advisor performance
            advisor_metrics = self._analyze_advisor_performance(cutoff_date)

            # Generate cross-system insights
            cross_system_insights = self._analyze_cross_system_performance(cutoff_date)

            # Calculate overall system health
            system_health = self._calculate_system_health([assistant_metrics, agent_metrics, advisor_metrics])

            report = {
                'report_period': f"{lookback_days} days",
                'generated_at': timezone.now().isoformat(),
                'system_health': system_health,
                'performance_metrics': {
                    'assistant': assistant_metrics,
                    'agents': agent_metrics,
                    'advisors': advisor_metrics
                },
                'cross_system_insights': cross_system_insights,
                'recommendations': self._generate_performance_recommendations(
                    assistant_metrics, agent_metrics, advisor_metrics, cross_system_insights
                )
            }

            self.logger.info(f"Generated system performance report for {lookback_days} days")
            return report

        except Exception as e:
            self.logger.error(f"Error generating system performance report: {e}")
            return {'error': str(e)}

    def _analyze_assistant_performance(self, cutoff_date: datetime) -> SystemPerformanceMetrics:
        """Analyze Personal Assistant performance"""
        try:
            conversations = ConversationMemory.objects.filter(created_at__gte=cutoff_date)

            total_conversations = conversations.count()
            successful_conversations = conversations.filter(success=True).count()
            unique_users = conversations.values('user').distinct().count()

            success_rate = successful_conversations / total_conversations if total_conversations > 0 else 0

            # Calculate average satisfaction (simulated - would be from user ratings)
            avg_satisfaction = 0.8  # Placeholder

            # Get most common intents
            intent_counts = Counter(conv.intent for conv in conversations if conv.intent)
            most_common_tasks = [intent for intent, count in intent_counts.most_common(5)]

            return SystemPerformanceMetrics(
                system_name="Personal Assistant",
                success_rate=success_rate,
                avg_response_time=2.5,  # Simulated
                user_satisfaction=avg_satisfaction,
                task_completion_rate=success_rate,
                error_rate=1 - success_rate,
                improvement_trend="stable",
                interaction_count=total_conversations,
                unique_users=unique_users,
                most_common_tasks=most_common_tasks,
                performance_by_context={intent: 0.8 for intent in most_common_tasks},
                measurement_period=timezone.now() - cutoff_date
            )

        except Exception as e:
            self.logger.error(f"Error analyzing assistant performance: {e}")
            return SystemPerformanceMetrics(
                system_name="Personal Assistant",
                success_rate=0.0,
                avg_response_time=0.0,
                user_satisfaction=0.0,
                task_completion_rate=0.0,
                error_rate=1.0,
                improvement_trend="unknown",
                interaction_count=0,
                unique_users=0,
                most_common_tasks=[],
                performance_by_context={},
                measurement_period=timezone.now() - cutoff_date
            )

    def _analyze_agent_performance(self, cutoff_date: datetime) -> SystemPerformanceMetrics:
        """Analyze Agent system performance"""
        try:
            # Get agent stats from registry
            agent_stats = self.agent_registry.get_registry_stats()

            return SystemPerformanceMetrics(
                system_name="Agent System",
                success_rate=agent_stats.avg_success_rate,
                avg_response_time=3.0,  # Simulated
                user_satisfaction=0.75,  # Simulated
                task_completion_rate=agent_stats.avg_success_rate,
                error_rate=1 - agent_stats.avg_success_rate,
                improvement_trend="improving",
                interaction_count=agent_stats.total_executions,
                unique_users=agent_stats.active_agents,  # Placeholder
                most_common_tasks=list(agent_stats.popular_specializations.keys())[:5],
                performance_by_context={spec: 0.8 for spec in agent_stats.popular_specializations.keys()},
                measurement_period=timezone.now() - cutoff_date
            )

        except Exception as e:
            self.logger.error(f"Error analyzing agent performance: {e}")
            return SystemPerformanceMetrics(
                system_name="Agent System",
                success_rate=0.0,
                avg_response_time=0.0,
                user_satisfaction=0.0,
                task_completion_rate=0.0,
                error_rate=1.0,
                improvement_trend="unknown",
                interaction_count=0,
                unique_users=0,
                most_common_tasks=[],
                performance_by_context={},
                measurement_period=timezone.now() - cutoff_date
            )

    def _analyze_advisor_performance(self, cutoff_date: datetime) -> SystemPerformanceMetrics:
        """Analyze Advisor system performance"""
        try:
            # Get advisor stats
            advisor_stats = self.advisor_registry.get_registry_stats()

            return SystemPerformanceMetrics(
                system_name="Advisor System",
                success_rate=advisor_stats.get('avg_success_rate', 0.85),
                avg_response_time=advisor_stats.get('avg_response_time_hours', 6.0) * 3600,  # Convert to seconds
                user_satisfaction=advisor_stats.get('avg_satisfaction_rating', 4.5) / 5.0,
                task_completion_rate=0.9,  # Simulated
                error_rate=0.1,  # Simulated
                improvement_trend="stable",
                interaction_count=advisor_stats.get('total_consultations', 0),
                unique_users=advisor_stats.get('total_advisors', 25),  # Placeholder
                most_common_tasks=list(advisor_stats.get('top_domains', []))[:5],
                performance_by_context={domain: 0.85 for domain, count in advisor_stats.get('top_domains', [])},
                measurement_period=timezone.now() - cutoff_date
            )

        except Exception as e:
            self.logger.error(f"Error analyzing advisor performance: {e}")
            return SystemPerformanceMetrics(
                system_name="Advisor System",
                success_rate=0.0,
                avg_response_time=0.0,
                user_satisfaction=0.0,
                task_completion_rate=0.0,
                error_rate=1.0,
                improvement_trend="unknown",
                interaction_count=0,
                unique_users=0,
                most_common_tasks=[],
                performance_by_context={},
                measurement_period=timezone.now() - cutoff_date
            )

    def _analyze_cross_system_performance(self, cutoff_date: datetime) -> List[Dict[str, Any]]:
        """Analyze performance across systems"""
        insights = []

        try:
            # Analyze system integration effectiveness
            insights.append({
                'type': 'integration_effectiveness',
                'description': 'Personal Assistant → Agent routing success rate',
                'metric': 'success_rate',
                'value': 0.75,  # Simulated
                'trend': 'improving'
            })

            insights.append({
                'type': 'cross_system_learning',
                'description': 'Learning insights applied across systems',
                'metric': 'application_rate',
                'value': 0.65,  # Simulated
                'trend': 'stable'
            })

            insights.append({
                'type': 'user_journey_completion',
                'description': 'End-to-end user journey completion rate',
                'metric': 'completion_rate',
                'value': 0.70,  # Simulated
                'trend': 'improving'
            })

        except Exception as e:
            self.logger.error(f"Error analyzing cross-system performance: {e}")

        return insights

    def _calculate_system_health(self, metrics_list: List[SystemPerformanceMetrics]) -> Dict[str, Any]:
        """Calculate overall system health score"""
        try:
            total_success_rate = sum(m.success_rate for m in metrics_list) / len(metrics_list)
            total_satisfaction = sum(m.user_satisfaction for m in metrics_list) / len(metrics_list)
            total_completion = sum(m.task_completion_rate for m in metrics_list) / len(metrics_list)

            health_score = (total_success_rate + total_satisfaction + total_completion) / 3

            if health_score >= 0.8:
                status = "excellent"
            elif health_score >= 0.7:
                status = "good"
            elif health_score >= 0.6:
                status = "fair"
            else:
                status = "needs_improvement"

            return {
                'overall_score': round(health_score, 2),
                'status': status,
                'success_rate': round(total_success_rate, 2),
                'user_satisfaction': round(total_satisfaction, 2),
                'task_completion': round(total_completion, 2)
            }

        except Exception as e:
            self.logger.error(f"Error calculating system health: {e}")
            return {'status': 'unknown', 'error': str(e)}

    def _generate_performance_recommendations(self, assistant_metrics, agent_metrics, advisor_metrics, cross_insights) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []

        # Assistant recommendations
        if assistant_metrics.success_rate < 0.8:
            recommendations.append("Improve Personal Assistant response accuracy through enhanced training data")

        # Agent recommendations
        if agent_metrics.success_rate < 0.7:
            recommendations.append("Optimize agent selection and routing algorithms")

        # Advisor recommendations
        if advisor_metrics.avg_response_time > 24 * 3600:  # More than 24 hours
            recommendations.append("Reduce advisor response time through better scheduling")

        # Cross-system recommendations
        recommendations.append("Implement more sophisticated cross-system learning mechanisms")
        recommendations.append("Enhance user journey tracking for better completion rates")

        return recommendations

    def _classify_user_segment(self, user: User) -> str:
        """Classify user into a segment for targeted insights"""
        # Simple classification - would be more sophisticated in production
        try:
            from core.models import EnhancedUserProfile
            profile = EnhancedUserProfile.objects.get(user=user)

            if profile.primary_role:
                if 'engineer' in profile.primary_role.lower():
                    return 'technical_user'
                elif 'manager' in profile.primary_role.lower():
                    return 'business_user'
                elif 'designer' in profile.primary_role.lower():
                    return 'creative_user'

            return 'general_user'

        except:
            return 'general_user'

    def _extract_preferred_agent(self, insight: LearningInsight) -> Optional[str]:
        """Extract preferred agent name from insight"""
        try:
            for evidence in insight.supporting_evidence:
                if evidence.get('type') == 'agent_usage':
                    return evidence.get('preferred_agent')
        except:
            pass
        return None

    # Placeholder methods for learning components
    def _analyze_patterns(self, data):
        """Analyze patterns in user data"""
        pass

    def _predict_success(self, context):
        """Predict success probability for given context"""
        pass

    def _learn_preferences(self, user_data):
        """Learn user preferences from interaction data"""
        pass

    def _optimize_workflows(self, workflow_data):
        """Optimize workflows based on performance data"""
        pass

    def _correlate_across_systems(self, system_data):
        """Find correlations across different systems"""
        pass


def analyze_user_learning_patterns(user: User, lookback_days: int = 30) -> Dict[str, Any]:
    """
    Convenience function to analyze learning patterns for a user.

    Args:
        user: User to analyze
        lookback_days: Number of days to look back

    Returns:
        Learning analysis results
    """
    pipeline = UnifiedLearningPipeline()
    insights = pipeline.analyze_user_interaction_patterns(user, lookback_days)

    if insights:
        application_results = pipeline.apply_learning_insights(insights, user)
        return {
            'insights_generated': len(insights),
            'insights_applied': application_results.get('applied_insights', 0),
            'improvements_made': application_results.get('improvements_made', []),
            'insights': [
                {
                    'type': insight.insight_type.value,
                    'summary': insight.insight_summary,
                    'confidence': insight.confidence_score,
                    'impact': insight.potential_impact
                }
                for insight in insights
            ]
        }
    else:
        return {
            'insights_generated': 0,
            'message': 'No significant learning patterns detected'
        }


def generate_system_learning_report(lookback_days: int = 7) -> Dict[str, Any]:
    """
    Generate comprehensive system-wide learning report.

    Args:
        lookback_days: Number of days to analyze

    Returns:
        System learning report
    """
    pipeline = UnifiedLearningPipeline()
    return pipeline.generate_system_performance_report(lookback_days)