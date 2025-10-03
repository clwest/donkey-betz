"""
Learning Orchestrator
Connects ALL learning systems together to create autonomous improvement

This is the MASTER CONTROLLER that:
- Connects all 8 learning bridges
- Routes insights to Personal Assistant
- Enables agent-to-agent learning
- Creates autonomous improvement cycles
- Builds self-awareness
"""

import logging
import asyncio
from typing import Dict, List, Optional
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


class LearningOrchestrator:
    """
    MASTER ORCHESTRATOR: Connects all learning systems for autonomous improvement

    Integration Points:
    1. Learning Bridges (8 bridges) → Collect insights
    2. Agent Collaboration Optimizer → Form optimal teams
    3. Personal Assistant → Deliver insights to user
    4. Agent Execution → Feed improvements back to agents
    5. Spider Network → Quality feedback loops
    """

    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.learning_bridges = self._initialize_bridges()

    def _initialize_bridges(self) -> Dict:
        """Initialize all learning bridge connections"""
        return {
            'collaboration': 'core.learning_bridges.collaboration_bridge',
            'agent_execution': 'core.learning_bridges.agent_execution_bridge',
            'spider_data': 'core.learning_bridges.spider_data_bridge',
            'revenue_attribution': 'core.learning_bridges.revenue_attribution_bridge',
            'application_outcome': 'core.learning_bridges.application_outcome_bridge',
            'personalization': 'core.learning_bridges.personalization_bridge',
            'advisor_feedback': 'core.learning_bridges.advisor_feedback_bridge',
            'sports_betting': 'core.learning_bridges.sports_betting_bridge'
        }

    async def orchestrate_learning_cycle(self, user, trigger_event: str, event_data: Dict):
        """
        Main learning orchestration cycle

        Flow:
        1. Receive trigger event (agent execution, collaboration, etc.)
        2. Process through relevant learning bridges
        3. Extract cross-bridge insights
        4. Generate optimization recommendations
        5. Send to Personal Assistant
        6. Auto-apply improvements where possible
        """
        logger.info(f"🧠 Orchestrating learning cycle: {trigger_event}")

        try:
            # 1. Collect insights from all relevant bridges
            insights = await self._collect_bridge_insights(user, trigger_event, event_data)

            # 2. Cross-correlate insights
            correlations = await self._correlate_insights(insights)

            # 3. Generate optimization recommendations
            optimizations = await self._generate_optimizations(user, correlations)

            # 4. Send insights to Personal Assistant
            await self._send_to_personal_assistant(user, optimizations)

            # 5. Auto-apply safe improvements
            applied = await self._auto_apply_improvements(user, optimizations)

            logger.info(f"✅ Learning cycle complete. Applied {len(applied)} improvements")

            return {
                'insights': insights,
                'correlations': correlations,
                'optimizations': optimizations,
                'applied': applied
            }

        except Exception as e:
            logger.error(f"Error in learning orchestration: {e}", exc_info=True)
            return {'error': str(e)}

    async def _collect_bridge_insights(self, user, trigger_event: str, event_data: Dict) -> Dict:
        """Collect insights from all relevant learning bridges"""
        insights = {}

        # Determine which bridges are relevant for this event
        relevant_bridges = self._get_relevant_bridges(trigger_event)

        for bridge_name in relevant_bridges:
            try:
                bridge_insights = await self._query_bridge(bridge_name, user, event_data)
                insights[bridge_name] = bridge_insights
            except Exception as e:
                logger.error(f"Error querying {bridge_name}: {e}")

        return insights

    def _get_relevant_bridges(self, trigger_event: str) -> List[str]:
        """Determine which bridges are relevant for this event"""
        relevance_map = {
            'agent_execution': ['agent_execution', 'collaboration', 'personalization'],
            'collaboration_completed': ['collaboration', 'agent_execution'],
            'application_submitted': ['application_outcome', 'revenue_attribution'],
            'spider_data_collected': ['spider_data', 'personalization'],
            'revenue_confirmed': ['revenue_attribution', 'application_outcome'],
            'advisor_consulted': ['advisor_feedback', 'agent_execution']
        }

        return relevance_map.get(trigger_event, ['agent_execution'])

    async def _query_bridge(self, bridge_name: str, user, event_data: Dict) -> Dict:
        """Query a specific learning bridge for insights"""
        from core.models_unified_system import UserAgentLearning

        # Get learning data for this bridge's domain (run in thread pool)
        def get_learning_records():
            return list(UserAgentLearning.objects.filter(
                user=user,
                learning_domain__icontains=bridge_name.split('_')[0]
            ).order_by('-confidence_score')[:10])

        learning_records = await asyncio.to_thread(get_learning_records)

        insights = {
            'bridge': bridge_name,
            'high_confidence_patterns': [],
            'improvement_opportunities': [],
            'success_factors': []
        }

        for record in learning_records:
            if record.confidence_score > 0.7:
                insights['high_confidence_patterns'].append({
                    'agent': record.agent_name,
                    'confidence': record.confidence_score,
                    'success_rate': record.success_rate if hasattr(record, 'success_rate') else 0,
                    'content': record.learning_content
                })

        return insights

    async def _correlate_insights(self, insights: Dict) -> Dict:
        """Cross-correlate insights from different bridges to find patterns"""
        correlations = {
            'agent_performance_patterns': [],
            'success_combinations': [],
            'failure_predictors': [],
            'optimization_opportunities': []
        }

        # Find agents that perform well across multiple domains
        agent_performance = {}

        for bridge_name, bridge_data in insights.items():
            for pattern in bridge_data.get('high_confidence_patterns', []):
                agent = pattern['agent']
                if agent not in agent_performance:
                    agent_performance[agent] = {
                        'domains': [],
                        'avg_success': 0,
                        'avg_confidence': 0
                    }

                agent_performance[agent]['domains'].append(bridge_name)
                agent_performance[agent]['avg_success'] += pattern.get('success_rate', 0)
                agent_performance[agent]['avg_confidence'] += pattern.get('confidence', 0)

        # Identify top performers
        for agent, data in agent_performance.items():
            domain_count = len(data['domains'])
            if domain_count > 1:  # Multi-domain success
                correlations['agent_performance_patterns'].append({
                    'agent': agent,
                    'domains': data['domains'],
                    'avg_success': data['avg_success'] / domain_count,
                    'pattern': 'multi_domain_excellence'
                })

        return correlations

    async def _generate_optimizations(self, user, correlations: Dict) -> Dict:
        """Generate optimization recommendations based on correlated insights"""
        from core.self_development.agent_collaboration_optimizer import collaboration_optimizer
        from core.models_unified_system import UserAgentLearning, AgentExecution

        optimizations = {
            'immediate_actions': [],
            'suggested_improvements': [],
            'learning_priorities': [],
            'team_recommendations': [],
            'learning_summary': {}
        }

        # Get learning summary stats (run in thread pool)
        def get_learning_stats():
            recent_executions = AgentExecution.objects.filter(user=user).count()
            total_learning = UserAgentLearning.objects.filter(user=user).count()

            # Get top confidence scores
            top_learning = list(UserAgentLearning.objects.filter(
                user=user
            ).order_by('-confidence_score')[:5])

            confidence_scores = [
                {
                    'agent': record.agent_name,
                    'confidence': record.confidence_score,
                    'domain': record.learning_domain
                }
                for record in top_learning
            ]

            return {
                'recent_executions': recent_executions,
                'total_learning_records': total_learning,
                'confidence_scores': confidence_scores
            }

        learning_stats = await asyncio.to_thread(get_learning_stats)
        optimizations['learning_summary'] = learning_stats

        # Get collaboration optimizations (run in thread pool)
        collab_opts = await asyncio.to_thread(
            collaboration_optimizer.auto_optimize_collaboration,
            user
        )

        # Merge collaboration recommendations
        optimizations['team_recommendations'] = collab_opts.get('recommended_teams', [])

        # Generate learning priorities from correlations
        for pattern in correlations.get('agent_performance_patterns', []):
            if pattern['avg_success'] > 0.8:
                optimizations['immediate_actions'].append({
                    'action': 'prioritize_agent',
                    'agent': pattern['agent'],
                    'reason': f"Excellent multi-domain performance ({pattern['avg_success']:.1%})",
                    'domains': pattern['domains']
                })

        return optimizations

    async def _send_to_personal_assistant(self, user, optimizations: Dict):
        """Send optimization insights to Personal Assistant WebSocket"""
        if not self.channel_layer:
            logger.warning("Channel layer not available")
            return

        try:
            # Format message for Personal Assistant
            message = self._format_assistant_message(optimizations)

            # Send via channel layer to user's Personal Assistant
            await self.channel_layer.group_send(
                f"user_{user.id}",
                {
                    'type': 'learning_insights',
                    'message': message,
                    'optimizations': optimizations
                }
            )

            logger.info(f"📨 Sent learning insights to Personal Assistant for user {user.id}")

        except Exception as e:
            logger.error(f"Error sending to Personal Assistant: {e}")

    def _format_assistant_message(self, optimizations: Dict) -> str:
        """Format optimizations as a friendly message for Personal Assistant"""
        message_parts = ["🧠 **Learning Insights:**\n"]

        # Show learning metrics (always visible)
        learning_summary = optimizations.get('learning_summary', {})
        if learning_summary:
            message_parts.append("\n**Current Learning:**")
            if learning_summary.get('confidence_scores'):
                top_agents = learning_summary['confidence_scores'][:3]
                for agent_data in top_agents:
                    confidence = agent_data['confidence'] * 100
                    message_parts.append(f"• {agent_data['agent']}: {confidence:.1f}% confidence")

            if learning_summary.get('recent_executions'):
                message_parts.append(f"\n📊 {learning_summary['recent_executions']} agent executions completed")

            if learning_summary.get('total_learning_records'):
                message_parts.append(f"📚 {learning_summary['total_learning_records']} learning records active")

        # Immediate actions
        if optimizations.get('immediate_actions'):
            message_parts.append("\n**Recommended Actions:**")
            for action in optimizations['immediate_actions'][:3]:
                message_parts.append(f"• {action['reason']}")

        # Team recommendations
        if optimizations.get('team_recommendations'):
            message_parts.append("\n**Optimal Teams:**")
            for team in optimizations['team_recommendations'][:2]:
                team_str = ', '.join(team['team'][:3])
                message_parts.append(f"• {team_str} for {', '.join(team['best_for'][:2])}")

        return '\n'.join(message_parts)

    async def _auto_apply_improvements(self, user, optimizations: Dict) -> List[Dict]:
        """Automatically apply safe improvements"""
        applied = []

        # Auto-apply high-confidence agent prioritization
        for action in optimizations.get('immediate_actions', []):
            if action['action'] == 'prioritize_agent':
                # Update agent priority in cache
                cache_key = f"agent_priority_{user.id}_{action['agent']}"
                cache.set(cache_key, {
                    'priority': 'high',
                    'reason': action['reason'],
                    'domains': action['domains']
                }, timeout=86400)  # 24 hours

                applied.append({
                    'type': 'agent_priority',
                    'agent': action['agent'],
                    'status': 'applied'
                })

        logger.info(f"✅ Auto-applied {len(applied)} improvements")
        return applied

    def get_system_learning_status(self, user) -> Dict:
        """Get comprehensive learning system status (sync method for API views)"""
        from core.models_unified_system import UserAgentLearning
        from django.db.models import Count, Avg

        status = {
            'total_learning_records': 0,
            'high_confidence_count': 0,
            'learning_by_domain': {},
            'top_performers': [],
            'learning_velocity': 0
        }

        # Get all learning records
        all_learning = UserAgentLearning.objects.filter(user=user)
        status['total_learning_records'] = all_learning.count()

        # High confidence learning
        status['high_confidence_count'] = all_learning.filter(
            confidence_score__gte=0.7
        ).count()

        # Learning by domain
        domain_stats = all_learning.values('learning_domain').annotate(
            count=Count('id'),
            avg_confidence=Avg('confidence_score')
        ).order_by('-count')[:10]

        for stat in domain_stats:
            status['learning_by_domain'][stat['learning_domain']] = {
                'count': stat['count'],
                'avg_confidence': float(stat['avg_confidence'] or 0)
            }

        # Top performers
        top_agents = all_learning.filter(
            confidence_score__gte=0.7
        ).values('agent_name').annotate(
            domains=Count('learning_domain', distinct=True),
            avg_confidence=Avg('confidence_score')
        ).order_by('-domains', '-avg_confidence')[:5]

        for agent in top_agents:
            status['top_performers'].append({
                'agent': agent['agent_name'],
                'domains': agent['domains'],
                'confidence': float(agent['avg_confidence'] or 0)
            })

        return status


# Singleton instance
learning_orchestrator = LearningOrchestrator()


# Helper function for synchronous access
def trigger_learning_cycle(user, event_type: str, event_data: Dict):
    """Synchronous wrapper for triggering learning cycle from Django views"""
    try:
        # Create new event loop for this thread (Django thread pool executor)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Run the async orchestration cycle
            result = loop.run_until_complete(
                learning_orchestrator.orchestrate_learning_cycle(user, event_type, event_data)
            )
            logger.info(f"✅ Learning cycle completed successfully")
            return result
        finally:
            # Clean up the event loop
            loop.close()

    except Exception as e:
        logger.error(f"Error triggering learning cycle: {e}", exc_info=True)
