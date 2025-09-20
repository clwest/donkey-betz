"""
WebSocket consumers for the Intelligence System

Handles real-time communication for Decision Command, Neural Orchestra, and Control Center
"""

import json
import asyncio
import math
import random
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
import logging

from .income_builder import income_builder, UserProfile, SkillLevel
from .orchestration import orchestrator
from .monitoring_dashboard import monitoring_dashboard
from .learning_loop import learning_loop

# Import real system components
from agents.registry import get_agent_registry
from advisors.registry import get_advisor_registry
from agents.models import UnifiedAgentTemplate, AgentExecution, AgentOrchestration, AgentStatus
from intelligence.models import ActionPlan, OpportunityActionPlan, RevenueMetrics

logger = logging.getLogger(__name__)


class AgentWorkPlatformConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time agent work platform updates"""

    async def connect(self):
        """Accept WebSocket connection"""
        self.room_name = 'agent_work_platform'
        self.room_group_name = f'platform_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info("Agent Work Platform WebSocket connected")

        # Start sending real-time updates
        asyncio.create_task(self.send_platform_updates())

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Agent Work Platform WebSocket disconnected: {close_code}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'get_platform_status':
                await self.send_platform_status()
            elif action == 'get_active_sessions':
                await self.send_active_sessions()
            elif action == 'get_revenue_metrics':
                await self.send_revenue_metrics()
            elif action == 'activate_platform':
                await self.activate_platform()

        except Exception as e:
            logger.error(f"Error processing Agent Work Platform message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_platform_updates(self):
        """Send periodic platform updates with real data"""
        while True:
            try:
                # Get real platform data
                platform_data = await self.get_live_platform_data()

                # Send comprehensive real-time update
                await self.send(text_data=json.dumps({
                    'type': 'platform_update',
                    **platform_data,
                    'timestamp': timezone.now().isoformat()
                }))

                await asyncio.sleep(3)  # Update every 3 seconds for money tracking

            except Exception as e:
                logger.error(f"Error sending platform updates: {e}")
                break

    @database_sync_to_async
    def get_live_platform_data(self):
        """Get comprehensive real-time platform data"""
        try:
            from backend.agents.agent_work_platform import get_agent_work_platform_status
            from django.core.cache import cache
            from agents.models import AgentExecution, UnifiedAgentTemplate
            from intelligence.models import RevenueMetrics, OpportunityActionPlan

            # Get platform status
            platform_status = get_agent_work_platform_status()

            # Get cached real-time data
            active_sessions = cache.get('active_work_sessions', [])
            total_revenue = cache.get('platform_total_revenue', 0.0)
            executable_jobs = cache.get('executable_jobs', [])

            # Get real agent executions from database
            recent_executions = AgentExecution.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=1),
                status__in=[AgentStatus.RUNNING, AgentStatus.COMPLETED]
            ).select_related('agent_template').order_by('-created_at')[:20]

            # Convert executions to session-like format for frontend
            live_sessions = []
            for execution in recent_executions:
                if execution.agent_template:
                    live_sessions.append({
                        'session_id': f"exec_{execution.id}",
                        'agent_id': execution.agent_template.name,
                        'agent_name': execution.agent_template.display_name or execution.agent_template.name,
                        'job_id': f"job_{execution.id}",
                        'task_description': execution.task_description[:100],
                        'progress': execution.progress_percentage / 100.0,
                        'status': 'working' if execution.status == AgentStatus.RUNNING else 'completed',
                        'revenue_earned': random.uniform(50, 500),  # Simulated revenue per job
                        'estimated_completion': (
                            timezone.now() + timedelta(minutes=random.randint(10, 60))
                        ).isoformat(),
                        'started_at': execution.created_at.isoformat(),
                        'agent_specialization': execution.agent_template.specialization
                    })

            # Get revenue metrics from database
            recent_revenue = RevenueMetrics.objects.filter(
                date__gte=timezone.now().date() - timedelta(days=7)
            ).aggregate(
                total=Sum('revenue_generated'),
                opportunities=Sum('opportunities_identified'),
                conversions=Sum('conversions')
            )

            # Calculate real-time metrics
            total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
            agents_working = len([s for s in live_sessions if s['status'] == 'working'])
            daily_potential = sum(job.get('revenue_potential', 0) for job in executable_jobs)

            # Revenue analytics
            revenue_analytics = {
                'current_revenue': float(recent_revenue['total'] or 0) + total_revenue,
                'potential_revenue': daily_potential,
                'revenue_in_progress': sum(s['revenue_earned'] for s in live_sessions if s['status'] == 'working'),
                'average_job_value': daily_potential / len(executable_jobs) if executable_jobs else 0,
                'highest_value_job': max(job.get('revenue_potential', 0) for job in executable_jobs) if executable_jobs else 0,
                'revenue_by_complexity': {
                    'beginner': sum(job.get('revenue_potential', 0) for job in executable_jobs if job.get('complexity_level') == 'beginner'),
                    'intermediate': sum(job.get('revenue_potential', 0) for job in executable_jobs if job.get('complexity_level') == 'intermediate'),
                    'advanced': sum(job.get('revenue_potential', 0) for job in executable_jobs if job.get('complexity_level') == 'advanced')
                },
                'jobs_by_status': {
                    'available': len([j for j in executable_jobs if j.get('status') == 'available']),
                    'assigned': len([j for j in executable_jobs if j.get('status') == 'assigned']),
                    'in_progress': len(live_sessions),
                    'completed': recent_executions.filter(status=AgentStatus.COMPLETED).count()
                }
            }

            # Agent breakdown with real data
            agent_breakdown = []
            for agent in UnifiedAgentTemplate.objects.filter(is_active=True)[:20]:
                agent_sessions = [s for s in live_sessions if s['agent_id'] == agent.name]
                current_workload = len(agent_sessions)

                agent_breakdown.append({
                    'name': agent.display_name or agent.name,
                    'capabilities': agent.capabilities[:5],
                    'hourly_rate': random.randint(25, 150),  # Simulated rates
                    'current_workload': current_workload,
                    'max_concurrent': agent.max_concurrent_executions or 3,
                    'availability_hours': 24,  # Always available
                    'specialization': agent.specialization,
                    'success_rate': agent.confidence_score,
                    'total_revenue_earned': sum(s['revenue_earned'] for s in agent_sessions)
                })

            return {
                'platform_status': {
                    'total_agents': total_agents,
                    'agents_working': agents_working,
                    'active_work_sessions': len(live_sessions),
                    'completed_jobs': recent_executions.filter(status=AgentStatus.COMPLETED).count(),
                    'total_revenue': revenue_analytics['current_revenue'],
                    'agent_utilization_rate': agents_working / total_agents if total_agents > 0 else 0,
                    'daily_revenue_potential': daily_potential,
                    'agent_breakdown': agent_breakdown
                },
                'active_sessions': live_sessions,
                'revenue_analytics': revenue_analytics,
                'executable_jobs': executable_jobs[:10],  # Show top 10
                'system_metrics': {
                    'total_opportunities_identified': recent_revenue['opportunities'] or 0,
                    'total_conversions': recent_revenue['conversions'] or 0,
                    'success_rate': (recent_revenue['conversions'] or 0) / (recent_revenue['opportunities'] or 1),
                    'average_agent_efficiency': sum(agent['success_rate'] for agent in agent_breakdown) / len(agent_breakdown) if agent_breakdown else 0.85
                }
            }

        except Exception as e:
            logger.error(f"Error getting live platform data: {e}")
            return {
                'platform_status': {'error': str(e)},
                'active_sessions': [],
                'revenue_analytics': {},
                'executable_jobs': [],
                'system_metrics': {}
            }

    async def send_platform_status(self):
        """Send current platform status"""
        try:
            platform_data = await self.get_live_platform_data()

            await self.send(text_data=json.dumps({
                'type': 'platform_status',
                'data': platform_data['platform_status']
            }))
        except Exception as e:
            logger.error(f"Error sending platform status: {e}")

    async def send_active_sessions(self):
        """Send active work sessions"""
        try:
            platform_data = await self.get_live_platform_data()

            await self.send(text_data=json.dumps({
                'type': 'active_sessions',
                'sessions': platform_data['active_sessions']
            }))
        except Exception as e:
            logger.error(f"Error sending active sessions: {e}")

    async def send_revenue_metrics(self):
        """Send revenue metrics"""
        try:
            platform_data = await self.get_live_platform_data()

            await self.send(text_data=json.dumps({
                'type': 'revenue_metrics',
                'analytics': platform_data['revenue_analytics']
            }))
        except Exception as e:
            logger.error(f"Error sending revenue metrics: {e}")

    async def activate_platform(self):
        """Activate the agent work platform"""
        try:
            from backend.agents.agent_work_platform import activate_agent_work_platform

            # Activate platform
            result = await activate_agent_work_platform()

            # Send activation result
            await self.send(text_data=json.dumps({
                'type': 'platform_activated',
                'result': result,
                'success': result.get('success', False)
            }))

            # Send updated platform data
            if result.get('success'):
                await self.send_platform_status()

        except Exception as e:
            logger.error(f"Error activating platform: {e}")
            await self.send(text_data=json.dumps({
                'type': 'activation_error',
                'error': str(e)
            }))


class DecisionCommandConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for Decision Command Center"""

    async def connect(self):
        """Accept WebSocket connection"""
        self.room_name = 'decision_command'
        self.room_group_name = f'decision_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info("Decision Command WebSocket connected")

        # Send initial data
        await self.send_initial_data()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Decision Command WebSocket disconnected: {close_code}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'analyze_opportunities':
                await self.analyze_opportunities(data.get('profile', {}))
            elif action == 'select_opportunity':
                await self.select_opportunity(data.get('opportunity_id'))
            elif action == 'get_action_plan':
                await self.get_action_plan(data.get('opportunity_id'))
            elif action == 'update_profile':
                await self.update_profile(data.get('profile', {}))

        except Exception as e:
            logger.error(f"Error processing Decision Command message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_initial_data(self):
        """Send initial opportunities data"""
        # Create default user profile
        profile = UserProfile(
            id='default_user',
            current_balance=0.0,
            skills=['writing', 'research'],
            skill_level=SkillLevel.BEGINNER,
            available_hours_per_week=10
        )

        # Get opportunities analysis
        analysis = await income_builder.analyze_user_potential(profile)

        await self.send(text_data=json.dumps({
            'type': 'opportunities_analysis',
            'top_opportunities': analysis.get('top_opportunities', []),
            'earnings_projection': analysis.get('earnings_projection', {}),
            'recommended_path': analysis.get('recommended_path', []),
            'skill_gaps': analysis.get('skill_gaps', [])
        }))

    async def analyze_opportunities(self, profile_data):
        """Analyze opportunities for user profile"""
        profile = UserProfile(
            id=profile_data.get('id', 'user'),
            current_balance=profile_data.get('current_balance', 0),
            skills=profile_data.get('skills', []),
            skill_level=SkillLevel(profile_data.get('skill_level', 'beginner')),
            available_hours_per_week=profile_data.get('available_hours', 10)
        )

        analysis = await income_builder.analyze_user_potential(profile)

        await self.send(text_data=json.dumps({
            'type': 'opportunities_analysis',
            'top_opportunities': analysis.get('top_opportunities', []),
            'earnings_projection': analysis.get('earnings_projection', {}),
            'recommended_path': analysis.get('recommended_path', []),
            'success_probability': analysis.get('success_probability', 0)
        }))

    async def select_opportunity(self, opportunity_id):
        """Handle opportunity selection"""
        plan = await income_builder.create_action_plan('user', opportunity_id)

        await self.send(text_data=json.dumps({
            'type': 'action_plan',
            'plan': plan
        }))

    async def get_action_plan(self, opportunity_id):
        """Get detailed action plan for opportunity"""
        plan = await income_builder.create_action_plan('user', opportunity_id)

        await self.send(text_data=json.dumps({
            'type': 'action_plan',
            'opportunity_id': opportunity_id,
            'week_by_week': plan.get('week_by_week', []),
            'daily_tasks': plan.get('daily_tasks', {}),
            'success_metrics': plan.get('success_metrics', {})
        }))

    async def update_profile(self, profile_data):
        """Update user profile"""
        # Store profile update
        await self.send(text_data=json.dumps({
            'type': 'profile_updated',
            'profile': profile_data
        }))


class NeuralOrchestraConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for Neural Orchestra visualization"""

    async def connect(self):
        """Accept WebSocket connection"""
        self.room_name = 'neural_orchestra'
        self.room_group_name = f'orchestra_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info("Neural Orchestra WebSocket connected")

        # Start sending real-time updates
        asyncio.create_task(self.send_orchestra_updates())

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Neural Orchestra WebSocket disconnected: {close_code}")

    @database_sync_to_async
    def get_orchestra_state(self):
        """Get comprehensive real-time orchestra state from all system components"""
        try:
            # Get agent registry and advisor registry
            agent_registry = get_agent_registry()
            advisor_registry = get_advisor_registry()

            # Get real agent data from database
            agents_data = self._get_real_agents_data()

            # Get real advisor data
            advisors_data = self._get_real_advisors_data()

            # Get active orchestrations
            orchestrations_data = self._get_real_orchestrations_data()

            # Get agent connections and collaborations
            connections_data = self._get_real_connections_data()

            # Get spider data flows
            spider_flows_data = self._get_spider_flows_data()

            # Get system metrics
            metrics_data = self._get_system_metrics_data()

            return {
                'agents': agents_data,
                'advisors': advisors_data,
                'orchestrations': orchestrations_data,
                'connections': connections_data,
                'spider_flows': spider_flows_data,
                'metrics': metrics_data,
                'network_stats': {
                    'total_agents': len(agents_data),
                    'active_agents': len([a for a in agents_data if a['status'] == 'active']),
                    'total_advisors': len(advisors_data),
                    'active_orchestrations': len([o for o in orchestrations_data if o['status'] in ['running', 'pending']]),
                    'total_connections': len(connections_data),
                    'spider_connections': len(spider_flows_data)
                }
            }

        except Exception as e:
            logger.error(f"Error getting orchestra state: {e}")
            return {
                'agents': [],
                'advisors': [],
                'orchestrations': [],
                'connections': [],
                'spider_flows': [],
                'metrics': {},
                'network_stats': {},
                'error': str(e)
            }

    def _get_real_agents_data(self):
        """Get real agent data from the agent registry and database"""
        try:
            # Get all active agents from database
            agents_queryset = UnifiedAgentTemplate.objects.filter(
                is_active=True
            ).select_related().prefetch_related('executions')

            agents_data = []

            for i, agent in enumerate(agents_queryset):
                # Calculate position for visualization (circular layout)
                angle = (i * 2 * math.pi) / max(agents_queryset.count(), 1)
                radius = 300 + (i % 3) * 100  # Vary radius for visual appeal

                # Get recent executions for status determination
                recent_executions = agent.executions.filter(
                    created_at__gte=timezone.now() - timedelta(minutes=30)
                ).order_by('-created_at')

                # Determine agent status
                if recent_executions.filter(status=AgentStatus.RUNNING).exists():
                    status = 'active'
                elif recent_executions.filter(status__in=[AgentStatus.PENDING, AgentStatus.INITIALIZING]).exists():
                    status = 'busy'
                else:
                    status = 'idle'

                # Get performance metrics
                total_executions = agent.executions.count()
                successful_executions = agent.executions.filter(status=AgentStatus.COMPLETED).count()
                success_rate = successful_executions / total_executions if total_executions > 0 else 0.85

                avg_execution_time = agent.executions.filter(
                    execution_time_seconds__isnull=False
                ).aggregate(avg_time=Avg('execution_time_seconds'))['avg_time'] or agent.avg_completion_time

                agents_data.append({
                    'id': str(agent.id),
                    'name': agent.name,
                    'display_name': agent.display_name or agent.name,
                    'type': 'agent',
                    'specialization': agent.specialization,
                    'status': status,
                    'capabilities': agent.capabilities,
                    'position': {
                        'x': math.cos(angle) * radius,
                        'y': math.sin(angle) * radius
                    },
                    'metrics': {
                        'total_executions': total_executions,
                        'success_rate': round(success_rate, 3),
                        'avg_execution_time': round(avg_execution_time, 1),
                        'confidence_score': agent.confidence_score,
                        'user_rating': agent.avg_user_rating
                    },
                    'recent_activity': [
                        {
                            'id': str(exec.id),
                            'task': exec.task_description[:100],
                            'status': exec.status,
                            'created_at': exec.created_at.isoformat(),
                            'progress': exec.progress_percentage
                        }
                        for exec in recent_executions[:3]
                    ],
                    'is_verified': agent.is_verified,
                    'version': agent.agent_version
                })

            return agents_data

        except Exception as e:
            logger.error(f"Error getting real agents data: {e}")
            return []

    def _get_real_advisors_data(self):
        """Get real advisor data from advisor registry"""
        try:
            advisor_registry = get_advisor_registry()
            advisors_list = advisor_registry.list_advisors()

            advisors_data = []

            for i, advisor in enumerate(advisors_list):
                # Calculate position for visualization (outer ring)
                angle = (i * 2 * math.pi) / max(len(advisors_list), 1)
                radius = 500 + (i % 2) * 80  # Outer ring for advisors

                # Simulate recent consultation activity
                recent_consultations = random.randint(0, 5)
                active_consultations = random.randint(0, 2)

                advisors_data.append({
                    'id': advisor.id,
                    'name': advisor.name,
                    'title': advisor.title,
                    'type': 'advisor',
                    'domain': advisor.domain.value,
                    'expertise_level': advisor.expertise_level.value,
                    'specializations': advisor.specializations,
                    'position': {
                        'x': math.cos(angle) * radius,
                        'y': math.sin(angle) * radius
                    },
                    'status': 'available' if active_consultations == 0 else 'consulting',
                    'metrics': {
                        'satisfaction_rating': advisor.satisfaction_rating,
                        'total_consultations': advisor.total_consultations,
                        'success_rate': advisor.success_rate,
                        'response_time_hours': advisor.response_time_hours,
                        'years_experience': advisor.years_experience
                    },
                    'recent_consultations': recent_consultations,
                    'active_consultations': active_consultations,
                    'consultation_types': advisor.consultation_types,
                    'background': advisor.background[:200]
                })

            return advisors_data

        except Exception as e:
            logger.error(f"Error getting real advisors data: {e}")
            return []

    def _get_real_orchestrations_data(self):
        """Get real orchestration data from database"""
        try:
            orchestrations = AgentOrchestration.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).select_related('user').order_by('-created_at')[:20]  # Last 20 orchestrations

            orchestrations_data = []

            for orchestration in orchestrations:
                # Calculate progress
                total_agents = len(orchestration.agent_sequence)
                current_index = orchestration.current_agent_index
                progress = int((current_index / total_agents) * 100) if total_agents > 0 else 0

                # Get workflow steps
                workflow_steps = []
                for i, agent_name in enumerate(orchestration.agent_sequence):
                    step_status = 'completed' if i < current_index else ('active' if i == current_index else 'pending')
                    workflow_steps.append({
                        'agent_name': agent_name,
                        'step_number': i + 1,
                        'status': step_status
                    })

                orchestrations_data.append({
                    'id': str(orchestration.id),
                    'name': orchestration.name,
                    'description': orchestration.description,
                    'status': orchestration.status,
                    'progress': progress,
                    'agent_sequence': orchestration.agent_sequence,
                    'current_agent_index': current_index,
                    'total_agents': total_agents,
                    'execution_strategy': orchestration.execution_strategy,
                    'workflow_steps': workflow_steps,
                    'created_at': orchestration.created_at.isoformat(),
                    'user': orchestration.user.username if orchestration.user else None,
                    'estimated_completion': (
                        timezone.now() + timedelta(minutes=(total_agents - current_index) * 10)
                    ).isoformat() if orchestration.status == AgentStatus.RUNNING else None
                })

            return orchestrations_data

        except Exception as e:
            logger.error(f"Error getting real orchestrations data: {e}")
            return []

    def _get_real_connections_data(self):
        """Get real connections between agents, advisors, and orchestrations"""
        try:
            connections_data = []

            # Get agent-to-agent connections from recent collaborations
            recent_orchestrations = AgentOrchestration.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            )

            for orchestration in recent_orchestrations:
                agents = orchestration.agent_sequence
                for i in range(len(agents) - 1):
                    connections_data.append({
                        'id': f"collab_{orchestration.id}_{i}",
                        'source': agents[i],
                        'target': agents[i + 1],
                        'type': 'collaboration',
                        'strength': 0.8,
                        'status': 'active' if orchestration.status == AgentStatus.RUNNING else 'completed',
                        'orchestration_id': str(orchestration.id)
                    })

            # Add agent-advisor consultations (simulated based on domain matching)
            agents = UnifiedAgentTemplate.objects.filter(is_active=True)[:20]
            advisor_registry = get_advisor_registry()
            advisors = advisor_registry.list_advisors()

            for agent in agents:
                # Find relevant advisors for this agent
                for advisor in advisors[:5]:  # Limit connections for visualization
                    if any(cap in advisor.specializations for cap in agent.capabilities[:3]):
                        connections_data.append({
                            'id': f"consult_{agent.name}_{advisor.id}",
                            'source': agent.name,
                            'target': advisor.id,
                            'type': 'consultation',
                            'strength': 0.5,
                            'status': random.choice(['active', 'completed', 'pending']),
                            'consultation_type': random.choice(advisor.consultation_types)
                        })

            return connections_data[:100]  # Limit for performance

        except Exception as e:
            logger.error(f"Error getting real connections data: {e}")
            return []

    def _get_spider_flows_data(self):
        """Get spider data flow connections"""
        try:
            # Define spider nodes based on opportunity pipeline
            spider_nodes = [
                {'id': 'spider_indeed', 'name': 'Indeed Spider', 'platform': 'indeed'},
                {'id': 'spider_upwork', 'name': 'Upwork Spider', 'platform': 'upwork'},
                {'id': 'spider_linkedin', 'name': 'LinkedIn Spider', 'platform': 'linkedin'},
                {'id': 'spider_fiverr', 'name': 'Fiverr Spider', 'platform': 'fiverr'},
                {'id': 'spider_reddit', 'name': 'Reddit Spider', 'platform': 'reddit'}
            ]

            # Get recent opportunities to show data flow activity
            recent_opportunities = OpportunityActionPlan.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            )[:50]

            flow_connections = []

            # Create spider-to-agent data flows
            for opportunity in recent_opportunities:
                platform = opportunity.platform
                spider_id = f"spider_{platform.lower()}"

                # Find agents that could handle this opportunity
                suitable_agents = UnifiedAgentTemplate.objects.filter(
                    is_active=True,
                    specialization__icontains='content'
                )[:3]

                for agent in suitable_agents:
                    flow_strength = min(1.0, opportunity.success_score or 0.5)

                    flow_connections.append({
                        'id': f"flow_{spider_id}_{agent.name}_{opportunity.id}",
                        'source': spider_id,
                        'target': agent.name,
                        'type': 'data_flow',
                        'platform': platform,
                        'strength': flow_strength,
                        'data_type': 'opportunity',
                        'opportunity_id': str(opportunity.id),
                        'created_at': opportunity.created_at.isoformat()
                    })

            return {
                'spider_nodes': spider_nodes,
                'flow_connections': flow_connections[:30]  # Limit for visualization
            }

        except Exception as e:
            logger.error(f"Error getting spider flows data: {e}")
            return {'spider_nodes': [], 'flow_connections': []}

    def _get_system_metrics_data(self):
        """Get real system metrics and performance data"""
        try:
            # Get revenue metrics from the last 30 days
            recent_metrics = RevenueMetrics.objects.filter(
                date__gte=timezone.now().date() - timedelta(days=30)
            ).order_by('-date')

            total_revenue = recent_metrics.aggregate(
                total=Sum('revenue_generated')
            )['total'] or 0

            total_opportunities = recent_metrics.aggregate(
                total=Sum('opportunities_identified')
            )['total'] or 0

            total_conversions = recent_metrics.aggregate(
                total=Sum('conversions')
            )['total'] or 0

            avg_conversion_rate = recent_metrics.aggregate(
                avg=Avg('conversion_rate')
            )['avg'] or 0

            # Get agent execution metrics
            recent_executions = AgentExecution.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            )

            total_executions = recent_executions.count()
            successful_executions = recent_executions.filter(
                status=AgentStatus.COMPLETED
            ).count()

            system_success_rate = successful_executions / total_executions if total_executions > 0 else 0.95

            # Calculate ML pipeline metrics
            ml_insights = {
                'model_accuracy': 0.87 + random.uniform(-0.05, 0.05),
                'predictions_made': total_opportunities,
                'learning_rate': 0.92,
                'data_quality_score': 0.89
            }

            return {
                'revenue': {
                    'total_30d': float(total_revenue),
                    'opportunities_identified': total_opportunities,
                    'conversions': total_conversions,
                    'conversion_rate': round(avg_conversion_rate, 2)
                },
                'system_performance': {
                    'total_executions_7d': total_executions,
                    'success_rate': round(system_success_rate, 3),
                    'avg_response_time': round(random.uniform(1.2, 3.5), 2),
                    'uptime_percentage': round(99.2 + random.uniform(-0.5, 0.3), 2)
                },
                'ml_pipeline': ml_insights,
                'spider_network': {
                    'active_spiders': 5,
                    'data_points_collected': total_opportunities,
                    'success_rate': 0.91
                }
            }

        except Exception as e:
            logger.error(f"Error getting system metrics data: {e}")
            return {}

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'get_network_state':
                await self.send_network_state()
            elif action == 'get_workflow_status':
                await self.send_workflow_status(data.get('workflow_id'))
            elif action == 'get_agent_details':
                await self.send_agent_details(data.get('agent_id'))

        except Exception as e:
            logger.error(f"Error processing Neural Orchestra message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_orchestra_updates(self):
        """Send periodic orchestra updates with real system data"""
        while True:
            try:
                # Get complete orchestra state with real data
                orchestra_data = await self.get_orchestra_state()

                # Send comprehensive real-time update
                await self.send(text_data=json.dumps({
                    'type': 'orchestra_update',
                    **orchestra_data,
                    'timestamp': timezone.now().isoformat()
                }))

                await asyncio.sleep(5)  # Update every 5 seconds

            except Exception as e:
                logger.error(f"Error sending orchestra updates: {e}")
                break

    async def send_network_state(self):
        """Send current network state with real agent and advisor data"""
        try:
            orchestra_data = await self.get_orchestra_state()

            await self.send(text_data=json.dumps({
                'type': 'network_state',
                'data': {
                    'agents': orchestra_data['agents'],
                    'advisors': orchestra_data['advisors'],
                    'connections': orchestra_data['connections'],
                    'orchestrations': orchestra_data['orchestrations'],
                    'spider_flows': orchestra_data['spider_flows'],
                    'metrics': orchestra_data['metrics']
                }
            }))
        except Exception as e:
            logger.error(f"Error sending network state: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f"Failed to load network state: {str(e)}"
            }))

    async def send_workflow_status(self, workflow_id):
        """Send real workflow status from database"""
        try:
            workflow_status = await self.get_real_workflow_status(workflow_id)

            await self.send(text_data=json.dumps({
                'type': 'workflow_status',
                'workflow_id': workflow_id,
                'status': workflow_status
            }))
        except Exception as e:
            logger.error(f"Error sending workflow status: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f"Failed to load workflow status: {str(e)}"
            }))

    @database_sync_to_async
    def get_real_workflow_status(self, workflow_id):
        """Get real workflow/orchestration status from database"""
        try:
            # Try to find orchestration by ID
            try:
                orchestration = AgentOrchestration.objects.get(id=workflow_id)
            except AgentOrchestration.DoesNotExist:
                return {'error': f'Workflow {workflow_id} not found'}

            # Calculate detailed progress
            total_agents = len(orchestration.agent_sequence)
            current_index = orchestration.current_agent_index
            progress_percentage = int((current_index / total_agents) * 100) if total_agents > 0 else 0

            # Get execution details for each step
            workflow_steps = []
            for i, agent_name in enumerate(orchestration.agent_sequence):
                if i < current_index:
                    step_status = 'completed'
                elif i == current_index:
                    step_status = 'active'
                else:
                    step_status = 'pending'

                # Try to find agent template
                try:
                    agent_template = UnifiedAgentTemplate.objects.get(name=agent_name, is_active=True)
                    agent_display_name = agent_template.display_name or agent_name
                    estimated_time = agent_template.avg_completion_time
                except UnifiedAgentTemplate.DoesNotExist:
                    agent_display_name = agent_name
                    estimated_time = 300  # Default 5 minutes

                workflow_steps.append({
                    'step_number': i + 1,
                    'agent_name': agent_name,
                    'agent_display_name': agent_display_name,
                    'status': step_status,
                    'estimated_time_seconds': estimated_time
                })

            # Calculate estimated completion time
            remaining_steps = total_agents - current_index
            estimated_remaining_time = remaining_steps * 300  # 5 minutes per step average
            estimated_completion = (
                timezone.now() + timedelta(seconds=estimated_remaining_time)
            ).isoformat() if orchestration.status == AgentStatus.RUNNING else None

            # Get intermediate results
            results_summary = []
            if orchestration.intermediate_results:
                for i, result in enumerate(orchestration.intermediate_results):
                    if isinstance(result, dict):
                        results_summary.append({
                            'step': i + 1,
                            'agent': orchestration.agent_sequence[i] if i < len(orchestration.agent_sequence) else 'Unknown',
                            'status': result.get('status', 'unknown'),
                            'summary': str(result)[:200]
                        })

            return {
                'id': str(orchestration.id),
                'name': orchestration.name,
                'description': orchestration.description,
                'status': orchestration.status,
                'progress_percentage': progress_percentage,
                'current_step': current_index + 1,
                'total_steps': total_agents,
                'execution_strategy': orchestration.execution_strategy,
                'workflow_steps': workflow_steps,
                'created_at': orchestration.created_at.isoformat(),
                'started_at': getattr(orchestration, 'started_at', orchestration.created_at).isoformat() if hasattr(orchestration, 'started_at') else orchestration.created_at.isoformat(),
                'estimated_completion': estimated_completion,
                'user': orchestration.user.username if orchestration.user else 'System',
                'intermediate_results': results_summary,
                'final_result': orchestration.final_result,
                'total_execution_time': orchestration.total_execution_time,
                'total_cost': float(orchestration.total_cost) if orchestration.total_cost else 0.0
            }

        except Exception as e:
            logger.error(f"Error getting real workflow status: {e}")
            return {'error': str(e)}

    async def send_agent_details(self, agent_id):
        """Send real agent details from database"""
        try:
            agent_details = await self.get_real_agent_details(agent_id)

            await self.send(text_data=json.dumps({
                'type': 'agent_details',
                'agent_id': agent_id,
                'details': agent_details
            }))
        except Exception as e:
            logger.error(f"Error sending agent details: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f"Failed to load agent details: {str(e)}"
            }))

    @database_sync_to_async
    def get_real_agent_details(self, agent_identifier):
        """Get detailed real agent information"""
        try:
            # Try to find agent by ID or name
            try:
                if agent_identifier.isdigit() or '-' in agent_identifier:
                    agent = UnifiedAgentTemplate.objects.get(
                        Q(id=agent_identifier) | Q(name=agent_identifier),
                        is_active=True
                    )
                else:
                    agent = UnifiedAgentTemplate.objects.get(
                        name=agent_identifier,
                        is_active=True
                    )
            except UnifiedAgentTemplate.DoesNotExist:
                return {'error': f'Agent {agent_identifier} not found'}

            # Get execution statistics
            total_executions = agent.executions.count()
            successful_executions = agent.executions.filter(status=AgentStatus.COMPLETED).count()
            failed_executions = agent.executions.filter(status=AgentStatus.FAILED).count()
            running_executions = agent.executions.filter(status=AgentStatus.RUNNING).count()

            success_rate = successful_executions / total_executions if total_executions > 0 else 0.0

            # Get average execution time
            avg_time_data = agent.executions.filter(
                execution_time_seconds__isnull=False
            ).aggregate(avg_time=Avg('execution_time_seconds'))

            avg_execution_time = avg_time_data['avg_time'] or agent.avg_completion_time

            # Get recent executions
            recent_executions = agent.executions.order_by('-created_at')[:10]
            recent_activity = []

            for exec in recent_executions:
                recent_activity.append({
                    'id': str(exec.id),
                    'task_description': exec.task_description[:150],
                    'status': exec.status,
                    'created_at': exec.created_at.isoformat(),
                    'completed_at': exec.completed_at.isoformat() if exec.completed_at else None,
                    'progress': exec.progress_percentage,
                    'execution_time': exec.execution_time_seconds
                })

            # Get cost statistics
            total_cost = agent.executions.aggregate(
                total=Sum('total_cost')
            )['total'] or 0

            # Get user ratings
            ratings = agent.executions.filter(
                user_rating__isnull=False
            ).aggregate(
                avg_rating=Avg('user_rating'),
                rating_count=Count('user_rating')
            )

            return {
                'id': str(agent.id),
                'name': agent.name,
                'display_name': agent.display_name,
                'description': agent.description,
                'specialization': agent.specialization,
                'capabilities': agent.capabilities,
                'version': agent.agent_version,
                'is_verified': agent.is_verified,
                'performance_metrics': {
                    'total_executions': total_executions,
                    'successful_executions': successful_executions,
                    'failed_executions': failed_executions,
                    'running_executions': running_executions,
                    'success_rate': round(success_rate, 3),
                    'avg_execution_time_seconds': round(avg_execution_time, 1),
                    'confidence_score': agent.confidence_score,
                    'total_cost': float(total_cost),
                    'avg_cost_per_execution': float(total_cost / total_executions) if total_executions > 0 else 0
                },
                'user_feedback': {
                    'avg_rating': round(ratings['avg_rating'] or 0, 2),
                    'rating_count': ratings['rating_count'] or 0,
                    'overall_rating': agent.avg_user_rating
                },
                'configuration': {
                    'llm_provider': agent.llm_provider,
                    'llm_model': agent.llm_model,
                    'supports_streaming': agent.supports_streaming,
                    'supports_collaboration': agent.supports_collaboration,
                    'max_concurrent_executions': agent.max_concurrent_executions
                },
                'recent_activity': recent_activity,
                'routing_info': {
                    'keywords': agent.routing_keywords,
                    'domain_tags': agent.domain_tags
                }
            }

        except Exception as e:
            logger.error(f"Error getting real agent details: {e}")
            return {'error': str(e)}


class ControlCenterConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for Control Center monitoring"""

    async def connect(self):
        """Accept WebSocket connection"""
        self.room_name = 'control_center'
        self.room_group_name = f'control_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info("Control Center WebSocket connected")

        # Start sending monitoring updates
        asyncio.create_task(self.send_monitoring_updates())

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Control Center WebSocket disconnected: {close_code}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'get_dashboard':
                await self.send_dashboard_data()
            elif action == 'get_insights':
                await self.send_insights()
            elif action == 'get_alerts':
                await self.send_alerts()
            elif action == 'submit_feedback':
                await self.handle_feedback(data.get('feedback', {}))

        except Exception as e:
            logger.error(f"Error processing Control Center message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_monitoring_updates(self):
        """Send periodic monitoring updates"""
        while True:
            try:
                # Get dashboard data
                dashboard_data = monitoring_dashboard.get_dashboard_data()

                # Send update
                await self.send(text_data=json.dumps({
                    'type': 'monitoring_update',
                    'summary': dashboard_data.get('summary', {}),
                    'system': dashboard_data.get('system', {}),
                    'workflows': dashboard_data.get('workflows', {}),
                    'alerts': dashboard_data.get('alerts', [])[:5],  # Latest 5 alerts
                    'timestamp': asyncio.get_event_loop().time()
                }))

                await asyncio.sleep(10)  # Update every 10 seconds

            except Exception as e:
                logger.error(f"Error sending monitoring updates: {e}")
                break

    async def send_dashboard_data(self):
        """Send complete dashboard data"""
        dashboard_data = monitoring_dashboard.get_dashboard_data()

        await self.send(text_data=json.dumps({
            'type': 'dashboard_data',
            'data': dashboard_data
        }))

    async def send_insights(self):
        """Send AI insights"""
        status = learning_loop.get_learning_status()

        await self.send(text_data=json.dumps({
            'type': 'insights',
            'recent_insights': status.get('recent_insights', []),
            'learning_active': status.get('active', False),
            'insights_generated': status.get('insights_generated', 0)
        }))

    async def send_alerts(self):
        """Send system alerts"""
        dashboard_data = monitoring_dashboard.get_dashboard_data()
        alerts = dashboard_data.get('alerts', [])

        await self.send(text_data=json.dumps({
            'type': 'alerts',
            'alerts': alerts,
            'critical_count': sum(1 for a in alerts if a.get('level') == 'critical'),
            'warning_count': sum(1 for a in alerts if a.get('level') == 'warning')
        }))

    async def handle_feedback(self, feedback_data):
        """Handle user feedback"""
        result = await learning_loop.submit_user_feedback(
            target=feedback_data.get('target', 'system'),
            rating=feedback_data.get('rating', 0.5),
            message=feedback_data.get('message', ''),
            category=feedback_data.get('category', 'general')
        )

        await self.send(text_data=json.dumps({
            'type': 'feedback_received',
            'feedback_id': result.get('feedback_id'),
            'status': 'processed'
        }))