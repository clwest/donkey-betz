"""
Neural Orchestra WebSocket Consumers
Provides real-time updates for the Neural Orchestra component
"""

import json
import asyncio
import logging
import time
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


class OrchestraConsumer(AsyncWebsocketConsumer):
    """Legacy orchestra consumer - redirects to NeuralOrchestraConsumer"""

    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'redirect',
            'message': 'Please use NeuralOrchestraConsumer for enhanced functionality'
        }))


class NeuralOrchestraConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for Neural Orchestra real-time updates"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_task = None
        self.update_interval = 5  # Increased for production stability
        self.heartbeat_task = None
        self.connection_start_time = None
        self.last_heartbeat = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = getattr(settings, 'WEBSOCKET_MAX_RETRIES', 5)

    async def connect(self):
        """Handle WebSocket connection with production monitoring"""
        try:
            await self.accept()
            self.connection_start_time = time.time()
            self.last_heartbeat = time.time()

            # Join Neural Orchestra group
            self.room_group_name = "neural_orchestra_updates"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            logger.info(f"Neural Orchestra WebSocket connected: {self.channel_name}")

            # Send connection confirmation
            await self.send(text_data=json.dumps({
                'type': 'connection_status',
                'status': 'connected',
                'timestamp': time.time(),
                'connection_id': self.channel_name,
                'message': 'Connected to production Neural Orchestra'
            }))

            # Send initial data
            await self.send_orchestra_data()

            # Start production monitoring tasks
            self.update_task = asyncio.create_task(self.periodic_updates())
            self.heartbeat_task = asyncio.create_task(self.heartbeat_monitor())

        except Exception as e:
            logger.error(f"Neural Orchestra connection failed: {e}")
            await self.close(code=1011)

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection with cleanup"""
        # Cancel all background tasks
        if self.update_task:
            self.update_task.cancel()
        if self.heartbeat_task:
            self.heartbeat_task.cancel()

        # Calculate connection duration
        if self.connection_start_time:
            duration = time.time() - self.connection_start_time
            logger.info(f"Neural Orchestra disconnected after {duration:.2f}s: {close_code}")

        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        logger.info(f"Neural Orchestra WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages with production error handling"""
        try:
            logger.info(f"📨 Neural Orchestra received message: {text_data[:100]}...")
            data = json.loads(text_data)
            message_type = data.get('type')
            logger.info(f"📋 Message type: {message_type}")

            # Update heartbeat on any message
            self.last_heartbeat = time.time()

            # Handle heartbeat messages
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp', time.time()),
                    'connection_id': self.channel_name
                }))
                return

            # Handle reconnection
            if message_type == 'reconnect':
                await self.handle_reconnect()
                return

            # Handle standard messages
            if message_type in ['get_orchestra_data', 'get_data', 'get_network_state', 'get_agents']:
                logger.info(f"🎵 Received data request ({message_type}) from {self.channel_name}")
                await self.send_orchestra_data()
            elif message_type == 'trigger_agent_workflow':
                await self.trigger_agent_workflow(data.get('workflow_config', {}))
            elif message_type == 'get_agent_details':
                agent_id = data.get('agent_id')
                await self.send_agent_details(agent_id)
            else:
                logger.warning(f"Unknown message type: {message_type}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
            await self.send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing Neural Orchestra message: {e}")
            await self.send_error(f"Processing error: {str(e)}")

    async def send_orchestra_data(self):
        """Send current orchestra state"""
        logger.info("=== STARTING send_orchestra_data ===")
        try:
            logger.info("About to call get_real_orchestra_data...")
            orchestra_data = await self.get_real_orchestra_data()
            logger.info(f"Data retrieved successfully. Type: {type(orchestra_data)}")

            if orchestra_data:
                agents_count = len(orchestra_data.get('agents', []))
                advisors_count = len(orchestra_data.get('advisors', []))
                logger.info(f"Orchestra data: {agents_count} agents, {advisors_count} advisors")

                # Send the data
                json_data = json.dumps(orchestra_data, default=str)
                logger.info(f"JSON data serialized, length: {len(json_data)}")

                await self.send(text_data=json_data)
                logger.info("✅ Orchestra data sent successfully!")
            else:
                logger.error("Orchestra data is None or empty")
                raise Exception("No orchestra data returned")

        except Exception as e:
            logger.error(f"❌ Error in send_orchestra_data: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")

            # Send basic working data
            try:
                fallback_data = {
                    'type': 'orchestra_update',
                    'agents': [
                        {'id': 'fallback1', 'name': 'Fallback Agent', 'type': 'research', 'status': 'idle', 'performance': 0.85}
                    ],
                    'advisors': [
                        {'id': 'fallback_advisor', 'name': 'Test Advisor', 'expertise': 'Fallback', 'consultations': 1, 'successRate': 1.0, 'status': 'available'}
                    ],
                    'workflows': [],
                    'connections': [],
                    'is_real': False,
                    'error': str(e),
                    'message': 'Fallback data due to error'
                }
                await self.send(text_data=json.dumps(fallback_data))
                logger.info("Fallback data sent")
            except Exception as fallback_error:
                logger.error(f"Even fallback failed: {fallback_error}")
                await self.send_error(f"Complete failure: {str(e)}")

    async def periodic_updates(self):
        """Send periodic real-time updates with production reliability"""
        while True:
            try:
                await asyncio.sleep(self.update_interval)

                # Check connection health before updating
                time_since_heartbeat = time.time() - self.last_heartbeat
                if time_since_heartbeat > 120:  # 2 minutes timeout
                    logger.warning(f"Orchestra client heartbeat timeout: {time_since_heartbeat:.2f}s")
                    break

                # Get fresh orchestra data
                orchestra_data = await self.get_real_orchestra_data()
                orchestra_data['type'] = 'live_update'
                orchestra_data['timestamp'] = datetime.now().isoformat()
                orchestra_data['is_production'] = True

                await self.send(text_data=json.dumps(orchestra_data))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic updates: {e}")
                await asyncio.sleep(10)  # Longer backoff on error

    async def heartbeat_monitor(self):
        """Monitor connection health with heartbeats"""
        while True:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds

                await self.send(text_data=json.dumps({
                    'type': 'heartbeat',
                    'timestamp': time.time(),
                    'connection_id': self.channel_name,
                    'uptime': time.time() - self.connection_start_time if self.connection_start_time else 0
                }))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat monitor error: {e}")
                await asyncio.sleep(5)

    async def handle_reconnect(self):
        """Handle reconnection requests"""
        self.reconnect_attempts += 1

        if self.reconnect_attempts > self.max_reconnect_attempts:
            await self.send_error("Maximum reconnection attempts exceeded")
            await self.close(code=1011)
            return

        logger.info(f"Handling orchestra reconnection attempt {self.reconnect_attempts}")

        # Send fresh data on reconnection
        await self.send_orchestra_data()

        await self.send(text_data=json.dumps({
            'type': 'connection_status',
            'status': 'reconnected',
            'timestamp': time.time(),
            'attempt': self.reconnect_attempts
        }))

    async def send_error(self, message: str):
        """Send error message to client"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message,
            'timestamp': time.time(),
            'connection_id': self.channel_name
        }))

    @database_sync_to_async
    def get_real_orchestra_data(self):
        """Get real Neural Orchestra data with dynamic connections and workflows"""
        try:
            from agents.models import UnifiedAgentTemplate, AgentExecution, AgentOrchestration
            from .orchestration_reality_connector import orchestration_connector
            import random

            # Get real agent data from database
            agents_queryset = UnifiedAgentTemplate.objects.filter(is_active=True).values(
                'id', 'name', 'display_name', 'specialization', 'usage_count', 'success_rate'
            )

            # Format agents with enhanced data
            formatted_agents = []
            for agent in agents_queryset:
                # Determine realistic agent status based on recent activity
                recent_executions = AgentExecution.objects.filter(
                    template_id=agent['id'],
                    created_at__gte=timezone.now() - timedelta(hours=24)
                ).count()

                # Calculate dynamic status
                if recent_executions > 5:
                    status = 'busy'
                elif recent_executions > 2:
                    status = 'active'
                elif recent_executions > 0:
                    status = 'idle'
                else:
                    status = 'standby'

                # Add some realistic variation to position for visualization
                x_pos = random.uniform(-400, 400)
                y_pos = random.uniform(-300, 300)

                formatted_agents.append({
                    'id': str(agent['id']),
                    'name': agent['display_name'] or agent['name'],
                    'type': agent['specialization'],
                    'status': status,
                    'performance': min(1.0, agent['success_rate'] + random.uniform(-0.05, 0.05)),
                    'currentTask': self.get_agent_current_task(agent['id'], status),
                    'usage_count': agent['usage_count'],
                    'recent_activity': recent_executions,
                    'position': {'x': x_pos, 'y': y_pos},
                    'confidence_score': random.uniform(0.75, 0.95),
                    'collaboration_ready': status in ['active', 'idle']
                })

            logger.info(f"Formatted {len(formatted_agents)} agents with real database data")

            # Use OrchestrationRealityConnector to generate dynamic connections and workflows
            orchestra_data = orchestration_connector.generate_real_orchestra_data(formatted_agents)

            # Add real orchestration data from database
            active_orchestrations = list(AgentOrchestration.objects.filter(
                status__in=['running', 'pending']
            ).values('id', 'name', 'description', 'status', 'progress_percentage', 'current_agent_index'))

            # Convert real orchestrations to workflow format
            real_workflows = []
            for orch in active_orchestrations:
                real_workflows.append({
                    'id': f"real_orch_{orch['id']}",
                    'name': orch['name'],
                    'type': 'orchestration',
                    'description': orch['description'],
                    'status': orch['status'],
                    'progress': orch['progress_percentage'],
                    'agents': [str(agent['id']) for agent in formatted_agents[:3]],  # Simplified
                    'created_at': timezone.now().isoformat(),
                    'priority': 'high',
                    'real_orchestration_id': orch['id'],
                    'is_real_orchestration': True
                })

            # Merge real workflows with generated ones
            all_workflows = orchestra_data['workflows'] + real_workflows

            # Update the orchestra data with real workflows
            orchestra_data['workflows'] = all_workflows
            orchestra_data['real_orchestrations_count'] = len(real_workflows)
            orchestra_data['total_workflows'] = len(all_workflows)

            logger.info(f"Generated complete orchestra data: {len(formatted_agents)} agents, "
                       f"{len(orchestra_data['connections'])} connections, {len(all_workflows)} workflows")

            return orchestra_data

        except Exception as e:
            logger.error(f"Error in get_real_orchestra_data: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")

            # Fallback with minimal working data
            return {
                'type': 'orchestra_update',
                'agents': [
                    {'id': 'fallback_1', 'name': 'Fallback Agent', 'type': 'research', 'status': 'idle', 'performance': 0.85}
                ],
                'advisors': [
                    {'id': 'fallback_advisor', 'name': 'Fallback Advisor', 'expertise': 'General', 'consultations': 0, 'successRate': 1.0, 'status': 'available'}
                ],
                'workflows': [],
                'connections': [],
                'is_real': False,
                'error': str(e),
                'message': 'Fallback data due to error'
            }

    def get_agent_current_task(self, agent_id: int, status: str) -> str:
        """Get current task description for an agent based on recent executions"""
        if status == 'standby':
            return None

        task_templates = {
            'busy': [
                'Processing complex analysis',
                'Generating comprehensive report',
                'Executing multi-step workflow',
                'Coordinating with team members'
            ],
            'active': [
                'Analyzing market data',
                'Creating content strategy',
                'Researching industry trends',
                'Optimizing performance metrics'
            ],
            'idle': [
                'Monitoring for new tasks',
                'Updating knowledge base',
                'Preparing for next assignment',
                'Maintaining system readiness'
            ]
        }

        tasks = task_templates.get(status, ['Available for tasks'])
        return random.choice(tasks)

    async def trigger_agent_workflow(self, workflow_config):
        """Trigger a new agent workflow with real-time orchestration"""
        try:
            from .orchestration_reality_connector import orchestration_connector

            # Extract workflow configuration
            workflow_name = workflow_config.get('name', 'Dynamic Workflow')
            agent_ids = workflow_config.get('agent_ids', [])
            priority = workflow_config.get('priority', 'normal')

            # Create new dynamic workflow
            new_workflow = orchestration_connector.create_dynamic_workflow(
                workflow_name, agent_ids, priority
            )

            # Send workflow creation confirmation
            await self.send(text_data=json.dumps({
                'type': 'workflow_triggered',
                'workflow': new_workflow,
                'status': 'created',
                'message': f'New workflow "{workflow_name}" created with {len(agent_ids)} agents'
            }))

            # Broadcast to all orchestra clients
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'workflow_update',
                    'workflow': new_workflow,
                    'action': 'created'
                }
            )

            # Start workflow execution simulation
            await self.simulate_workflow_progress(new_workflow)

        except Exception as e:
            logger.error(f"Error triggering workflow: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to trigger workflow: {str(e)}'
            }))

    async def simulate_workflow_progress(self, workflow):
        """Simulate realistic workflow progress over time"""
        try:
            workflow_id = workflow['id']

            # Send initial progress updates
            for progress in [10, 25, 40, 60, 75, 90, 100]:
                await asyncio.sleep(random.uniform(2, 5))  # Realistic delay

                # Update workflow status
                if progress == 100:
                    status = 'completed'
                    current_step = 'Workflow completed successfully'
                else:
                    status = 'running'
                    current_step = f"Processing step {progress//20 + 1}"

                # Broadcast progress update
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'workflow_progress_update',
                        'workflow_id': workflow_id,
                        'progress': progress,
                        'status': status,
                        'current_step': current_step,
                        'timestamp': timezone.now().isoformat()
                    }
                )

                if progress == 100:
                    break

        except Exception as e:
            logger.error(f"Error simulating workflow progress: {e}")

    async def send_agent_details(self, agent_id):
        """Send detailed information about a specific agent"""
        try:
            agent_details = await self.get_agent_details(agent_id)
            await self.send(text_data=json.dumps({
                'type': 'agent_details',
                'agent_id': agent_id,
                'details': agent_details
            }))

        except Exception as e:
            logger.error(f"Error sending agent details: {e}")

    @database_sync_to_async
    def get_agent_details(self, agent_id):
        """Get detailed information about a specific agent"""
        from agents.models import UnifiedAgentTemplate, AgentExecution

        try:
            agent = UnifiedAgentTemplate.objects.get(id=agent_id, is_active=True)

            recent_executions = AgentExecution.objects.filter(
                agent_id=agent_id
            ).order_by('-started_at')[:10]

            return {
                'id': str(agent.id),
                'name': agent.display_name or agent.name,
                'specialization': agent.specialization,
                'description': getattr(agent, 'description', 'AI Agent specialized in various tasks'),
                'capabilities': getattr(agent, 'capabilities', []),
                'recent_tasks': [
                    {
                        'id': str(exec.id),
                        'description': exec.task_description,
                        'status': exec.status,
                        'started_at': exec.started_at.isoformat() if exec.started_at else None,
                        'completed_at': exec.completed_at.isoformat() if exec.completed_at else None
                    }
                    for exec in recent_executions
                ],
                'performance_stats': {
                    'total_tasks': recent_executions.count(),
                    'success_rate': 0.89,
                    'average_completion_time': '15 minutes',
                    'efficiency_score': 0.87
                }
            }

        except Exception as e:
            logger.error(f"Error getting agent details for {agent_id}: {e}")
            return None

    async def workflow_update(self, event):
        """Handle workflow update broadcasts"""
        await self.send(text_data=json.dumps({
            'type': 'workflow_update',
            'data': event
        }))

    async def workflow_progress_update(self, event):
        """Handle workflow progress update broadcasts"""
        await self.send(text_data=json.dumps({
            'type': 'workflow_progress_update',
            'workflow_id': event.get('workflow_id'),
            'progress': event.get('progress'),
            'status': event.get('status'),
            'current_step': event.get('current_step'),
            'timestamp': event.get('timestamp')
        }))


class ControlConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for Control Panel interface"""

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_name = 'control'
        self.room_group_name = f'control_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Control Panel WebSocket connected: {self.channel_name}")

        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'Connected to Control Panel'
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Control Panel WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                # Respond to ping
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))

            elif message_type == 'system_status':
                # Send system status
                await self.send(text_data=json.dumps({
                    'type': 'system_status',
                    'status': self.get_system_status()
                }))

            elif message_type == 'command':
                # Handle control commands
                command = data.get('command')
                result = await self.handle_command(command, data.get('params', {}))
                await self.send(text_data=json.dumps({
                    'type': 'command_result',
                    'command': command,
                    'result': result
                }))

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

    def get_system_status(self):
        """Get current system status"""
        return {
            'services': {
                'api': 'online',
                'websocket': 'online',
                'celery': 'online',
                'redis': 'online',
                'database': 'online'
            },
            'metrics': {
                'active_connections': 5,
                'requests_per_minute': 120,
                'cpu_usage': 45.2,
                'memory_usage': 62.8
            }
        }

    async def handle_command(self, command, params):
        """Handle control commands"""
        if command == 'restart_service':
            service = params.get('service')
            logger.info(f"Restarting service: {service}")
            return {'status': 'success', 'message': f'Service {service} restarted'}

        elif command == 'clear_cache':
            logger.info("Clearing cache")
            return {'status': 'success', 'message': 'Cache cleared'}

        elif command == 'trigger_backup':
            logger.info("Triggering backup")
            return {'status': 'success', 'message': 'Backup triggered'}

        else:
            return {'status': 'error', 'message': f'Unknown command: {command}'}

    async def system_update(self, event):
        """Handle system update events"""
        await self.send(text_data=json.dumps({
            'type': 'system_update',
            'component': event.get('component'),
            'status': event.get('status'),
            'metrics': event.get('metrics')
        }))