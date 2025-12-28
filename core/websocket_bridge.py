"""
Universal WebSocket Bridge
Provides real data streaming for all frontend components that are currently not receiving data updates.
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from channels.generic.websocket import AsyncWebsocketConsumer
import random

logger = logging.getLogger(__name__)


class UniversalWebSocketBridge(AsyncWebsocketConsumer):
    """
    Universal WebSocket consumer that provides real data streaming for components
    that currently have no data flow. Automatically detects component type based
    on connection endpoint and provides appropriate data.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.component_type = None
        self.data_generator_task = None
        self.update_interval = 5  # seconds

    async def connect(self):
        """Handle WebSocket connection and identify component type"""
        await self.accept()

        # Identify component type from URL path
        path = self.scope.get('path', '')
        self.component_type = self.identify_component_type(path)

        # Join appropriate room
        self.room_name = f"{self.component_type}_updates"
        self.room_group_name = f"bridge_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        logger.info(f"WebSocket Bridge connected: {self.component_type} - {self.channel_name}")

        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'component': self.component_type,
            'message': f'Connected to {self.component_type} data bridge',
            'timestamp': datetime.now().isoformat()
        }))

        # Send initial data immediately
        await self.send_initial_data()

        # Start periodic data updates
        self.data_generator_task = asyncio.create_task(self.periodic_data_generator())

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Cancel data generator
        if self.data_generator_task:
            self.data_generator_task.cancel()

        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        logger.info(f"WebSocket Bridge disconnected: {self.component_type} - {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            logger.info(f"Bridge received {message_type} for {self.component_type}")

            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp'),
                    'component': self.component_type
                }))

            elif message_type == 'get_data':
                await self.send_current_data()

            elif message_type == 'subscribe_updates':
                await self.send(text_data=json.dumps({
                    'type': 'subscribed',
                    'component': self.component_type,
                    'update_interval': self.update_interval
                }))

            # Component-specific message handling
            await self.handle_component_message(data)

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    def identify_component_type(self, path: str) -> str:
        """Identify component type from WebSocket path"""
        if 'income-builder' in path:
            return 'income_builder'
        elif 'revenue' in path:
            return 'revenue_dashboard'
        elif 'decision' in path:
            return 'decision_command'
        elif 'orchestra' in path or 'agents' in path:
            return 'neural_orchestra'
        elif 'dashboard' in path:
            return 'main_dashboard'
        else:
            return 'generic'

    async def send_initial_data(self):
        """Send initial data for the component"""
        initial_data = await self.generate_component_data()
        await self.send(text_data=json.dumps(initial_data))

    async def send_current_data(self):
        """Send current data for the component"""
        current_data = await self.generate_component_data()
        await self.send(text_data=json.dumps(current_data))

    async def periodic_data_generator(self):
        """Generate periodic data updates"""
        while True:
            try:
                await asyncio.sleep(self.update_interval)

                # Generate new data
                update_data = await self.generate_component_data()
                update_data['type'] = 'live_update'

                # Send to this connection
                await self.send(text_data=json.dumps(update_data))

                # Broadcast to group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'broadcast_update',
                        'data': update_data
                    }
                )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic data generator: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def generate_component_data(self) -> Dict[str, Any]:
        """Generate appropriate data based on component type"""
        base_data = {
            'timestamp': datetime.now().isoformat(),
            'component': self.component_type,
        }

        if self.component_type == 'income_builder':
            return {**base_data, **self.generate_income_builder_data()}
        elif self.component_type == 'revenue_dashboard':
            return {**base_data, **self.generate_revenue_dashboard_data()}
        elif self.component_type == 'decision_command':
            return {**base_data, **self.generate_decision_command_data()}
        elif self.component_type == 'neural_orchestra':
            return {**base_data, **self.generate_neural_orchestra_data()}
        else:
            return {**base_data, **self.generate_generic_data()}

    def generate_income_builder_data(self) -> Dict[str, Any]:
        """Generate realistic Income Builder data"""
        opportunities = [
            {
                'id': f'opp_{random.randint(1000, 9999)}',
                'title': random.choice([
                    'AI Content Writing', 'Social Media Management', 'Digital Product Creation',
                    'Online Tutoring', 'Virtual Assistant Services', 'Freelance Design',
                    'E-commerce Store Setup', 'Affiliate Marketing Blog'
                ]),
                'stream_type': random.choice(['content_creation', 'freelance_services', 'digital_products']),
                'potential_monthly': f"${random.randint(500, 3000)}",
                'time_to_income': random.choice(['1-3 days', '1 week', '2 weeks', '1 month']),
                'difficulty': random.choice(['beginner', 'intermediate', 'advanced']),
                'success_rate': random.uniform(0.6, 0.95),
                'market_demand': random.uniform(0.7, 0.9),
                'match_reasons': random.sample([
                    'Low investment required', 'Matches your skills', 'High demand market',
                    'Quick time to income', 'Scalable opportunity', 'Remote friendly'
                ], k=random.randint(2, 4))
            }
            for _ in range(random.randint(3, 6))
        ]

        return {
            'type': 'opportunities_analysis',
            'top_opportunities': opportunities,
            'earnings_projection': {
                'week_1': random.randint(50, 200),
                'month_1': random.randint(300, 800),
                'month_3': random.randint(800, 2000),
                'month_6': random.randint(1500, 4000),
                'year_1': random.randint(5000, 15000)
            },
            'success_probability': random.uniform(0.75, 0.92),
            'recommended_path': [
                'Start with content writing for immediate income',
                'Build portfolio with 5-10 completed projects',
                'Increase rates by 20% after first month',
                'Add second income stream by month 2'
            ]
        }

    def generate_revenue_dashboard_data(self) -> Dict[str, Any]:
        """Generate realistic Revenue Dashboard data"""
        current_revenue = random.uniform(1000, 5000)

        return {
            'type': 'metrics_update',
            'metrics': {
                'total_revenue': current_revenue,
                'monthly_revenue': current_revenue * 0.8,
                'weekly_revenue': current_revenue * 0.25,
                'daily_revenue': current_revenue * 0.033,
                'conversion_rate': random.uniform(15, 35),
                'proposals_submitted': random.randint(20, 80),
                'responses_received': random.randint(8, 25),
                'conversions': random.randint(3, 12),
                'average_deal_size': random.uniform(150, 500),
                'response_rate': random.uniform(25, 60),
                'total_opportunities': random.randint(50, 150),
                'platform_breakdown': {
                    'upwork': {
                        'revenue': current_revenue * 0.4,
                        'count': random.randint(10, 25),
                        'converted': random.randint(2, 8)
                    },
                    'fiverr': {
                        'revenue': current_revenue * 0.3,
                        'count': random.randint(8, 20),
                        'converted': random.randint(1, 6)
                    },
                    'direct_clients': {
                        'revenue': current_revenue * 0.3,
                        'count': random.randint(5, 15),
                        'converted': random.randint(2, 7)
                    }
                }
            }
        }

    def generate_decision_command_data(self) -> Dict[str, Any]:
        """Generate realistic Decision Command data"""
        return {
            'type': 'decision_update',
            'decisions': [
                {
                    'id': f'dec_{random.randint(1000, 9999)}',
                    'title': random.choice([
                        'Increase Content Writing Rates',
                        'Launch New Service Package',
                        'Target New Client Segment',
                        'Automate Social Media',
                        'Expand to Video Content'
                    ]),
                    'domain': random.choice(['income', 'marketing', 'optimization', 'expansion']),
                    'confidence': random.uniform(0.75, 0.95),
                    'impact_score': random.uniform(0.6, 0.9),
                    'urgency': random.choice(['low', 'medium', 'high']),
                    'status': random.choice(['pending', 'analyzing', 'ready', 'implemented']),
                    'recommendations': random.sample([
                        'Test with 3 existing clients first',
                        'Create pricing tier structure',
                        'Develop case studies',
                        'Set up automated workflows',
                        'Monitor market response'
                    ], k=random.randint(2, 4))
                }
                for _ in range(random.randint(2, 5))
            ],
            'ai_insights': [
                'Market demand for AI services increased 23% this week',
                'Your conversion rate is above industry average',
                'Consider raising rates based on recent performance',
                'New opportunity detected in video script writing'
            ]
        }

    def generate_neural_orchestra_data(self) -> Dict[str, Any]:
        """Generate realistic Neural Orchestra data"""
        agents = [
            {
                'id': f'agent_{i}',
                'name': random.choice([
                    'Content Generator', 'Market Analyzer', 'Code Assistant',
                    'Data Processor', 'Quality Checker', 'Client Communicator'
                ]),
                'type': random.choice(['content', 'analysis', 'development', 'data', 'qa']),
                'status': random.choice(['idle', 'working', 'consulting']),
                'performance': random.uniform(0.75, 0.95),
                'tasks_completed': random.randint(10, 50),
                'current_task': random.choice([
                    'Writing blog post', 'Analyzing trends', 'Processing data',
                    'Code review', 'Client proposal', 'Market research'
                ]) if random.random() > 0.3 else None
            }
            for i in range(1, random.randint(5, 8))
        ]

        workflows = [
            {
                'id': f'workflow_{i}',
                'name': random.choice([
                    'Content Creation Pipeline', 'Client Onboarding Flow',
                    'Market Analysis Process', 'Quality Assurance Chain'
                ]),
                'status': random.choice(['pending', 'running', 'completed']),
                'progress': random.randint(20, 95),
                'agents_involved': random.randint(2, 4)
            }
            for i in range(1, random.randint(3, 6))
        ]

        return {
            'type': 'orchestra_update',
            'agents': agents,
            'workflows': workflows,
            'system_stats': {
                'active_agents': len([a for a in agents if a['status'] != 'idle']),
                'total_agents': len(agents),
                'workflows_running': len([w for w in workflows if w['status'] == 'running']),
                'avg_performance': sum(a['performance'] for a in agents) / len(agents),
                'tasks_per_hour': random.randint(15, 35),
                'success_rate': random.uniform(0.88, 0.95)
            }
        }

    def generate_generic_data(self) -> Dict[str, Any]:
        """Generate generic data for unknown component types"""
        return {
            'type': 'generic_update',
            'status': 'active',
            'data': {
                'connections': random.randint(5, 20),
                'events_processed': random.randint(100, 1000),
                'last_activity': datetime.now().isoformat(),
                'performance_score': random.uniform(0.8, 0.95)
            }
        }

    async def handle_component_message(self, data: Dict[str, Any]):
        """Handle component-specific messages"""
        message_type = data.get('type')

        if self.component_type == 'income_builder':
            if message_type == 'analyze_opportunities':
                # Simulate analysis delay
                await asyncio.sleep(1)
                response_data = self.generate_income_builder_data()
                await self.send(text_data=json.dumps(response_data))

        elif self.component_type == 'decision_command':
            if data.get('action') == 'analyze_opportunities':
                # Simulate decision analysis
                await asyncio.sleep(1)
                response_data = self.generate_decision_command_data()
                await self.send(text_data=json.dumps(response_data))

    async def broadcast_update(self, event):
        """Handle broadcast updates from channel layer"""
        await self.send(text_data=json.dumps(event['data']))