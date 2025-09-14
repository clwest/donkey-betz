"""
WebSocket consumers for the Intelligence System

Handles real-time communication for Decision Command, Neural Orchestra, and Control Center
"""

import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import logging

from .income_builder import income_builder, UserProfile, SkillLevel
from .orchestration import orchestrator
from .monitoring_dashboard import monitoring_dashboard
from .learning_loop import learning_loop

logger = logging.getLogger(__name__)


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
        """Send periodic orchestra updates"""
        while True:
            try:
                # Get current orchestration state
                active_workflows = []
                for wf_id, wf in orchestrator.workflows.items():
                    if wf['status'].value in ['pending', 'running']:
                        active_workflows.append({
                            'id': wf_id,
                            'name': wf['name'],
                            'status': wf['status'].value,
                            'created_at': wf['created_at'].isoformat()
                        })

                # Send update
                await self.send(text_data=json.dumps({
                    'type': 'orchestra_update',
                    'active_workflows': len(active_workflows),
                    'workflows': active_workflows[:5],  # Top 5
                    'active_agents': len(orchestrator.active_contexts),
                    'timestamp': asyncio.get_event_loop().time()
                }))

                await asyncio.sleep(5)  # Update every 5 seconds

            except Exception as e:
                logger.error(f"Error sending orchestra updates: {e}")
                break

    async def send_network_state(self):
        """Send current network state"""
        # Get network state from orchestrator
        network_data = {
            'agents': [],
            'advisors': [],
            'connections': []
        }

        # Add mock data for visualization
        network_data['agents'] = [
            {'id': 'agent1', 'name': 'Content Writer', 'status': 'active'},
            {'id': 'agent2', 'name': 'Market Analyst', 'status': 'idle'},
            {'id': 'agent3', 'name': 'Risk Manager', 'status': 'active'}
        ]

        await self.send(text_data=json.dumps({
            'type': 'network_state',
            'data': network_data
        }))

    async def send_workflow_status(self, workflow_id):
        """Send workflow status"""
        if workflow_id and workflow_id in orchestrator.workflows:
            workflow = orchestrator.workflows[workflow_id]
            status = await orchestrator.get_workflow_status(workflow_id)

            await self.send(text_data=json.dumps({
                'type': 'workflow_status',
                'workflow_id': workflow_id,
                'status': status
            }))

    async def send_agent_details(self, agent_id):
        """Send agent details"""
        # Mock agent details
        details = {
            'id': agent_id,
            'performance': 0.85,
            'tasks_completed': 42,
            'average_time': 2.3,
            'success_rate': 0.92
        }

        await self.send(text_data=json.dumps({
            'type': 'agent_details',
            'agent_id': agent_id,
            'details': details
        }))


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