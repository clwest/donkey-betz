"""
Agent System WebSocket Consumers

Real-time WebSocket consumers for agent orchestration including:
- Agent execution status updates
- Real-time orchestration events
- Agent performance monitoring
- System-wide agent analytics
"""

import json
import asyncio
import logging
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model
from django.conf import settings

# Session 392: Updated to use canonical import path
from core.models.agents_registry import (
    UnifiedAgentTemplate, AgentExecution, AgentRegistry,
    AgentStatus, AgentSpecialization
)

User = get_user_model()
logger = logging.getLogger(__name__)


class AgentBaseConsumer(AsyncWebsocketConsumer):
    """Base consumer with common agent functionality"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.groups = []
        
    async def connect(self):
        """Handle WebSocket connection"""
        # Get user from scope (set by AuthMiddleware)
        self.user = self.scope.get('user')
        
        # Check if WebSocket authentication is enabled (should always be True in production)
        enable_ws_auth = os.getenv('ENABLE_WEBSOCKET_AUTH', 'true').lower() == 'true'
        
        # Enforce authentication if enabled
        if enable_ws_auth and (not self.user or not self.user.is_authenticated):
            logger.warning(f"Unauthenticated WebSocket connection attempt from {self.scope.get('client', ['unknown'])[0]}")
            await self.close(code=4001)
            return
        
        await self.accept()
        
        # Add user to their personal group if authenticated
        if self.user and hasattr(self.user, 'id'):
            user_group = f"user_{self.user.id}"
            await self.channel_layer.group_add(user_group, self.channel_name)
            self.groups.append(user_group)
        
        logger.info(f"Agent WebSocket connected: {self.user.username if self.user and hasattr(self.user, 'username') else 'Anonymous'}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Remove from all groups
        for group in self.groups:
            await self.channel_layer.group_discard(group, self.channel_name)
        
        logger.info(f"Agent WebSocket disconnected: {self.user.username if self.user else 'anonymous'}")
    
    async def send_json_data(self, data: Dict[str, Any]):
        """Send JSON data with proper encoding"""
        await self.send(text_data=json.dumps(data, cls=DjangoJSONEncoder))
    
    async def send_error(self, message: str, error_code: str = "generic_error"):
        """Send error message"""
        await self.send_json_data({
            'type': 'error',
            'error_code': error_code,
            'message': message,
            'timestamp': timezone.now()
        })


class AgentExecutionConsumer(AgentBaseConsumer):
    """Consumer for real-time agent execution updates"""
    
    async def connect(self):
        """Connect to agent execution updates"""
        await super().connect()
        
        if not self.user:
            return
        
        # Join agent execution group
        execution_group = "agent_executions"
        await self.channel_layer.group_add(execution_group, self.channel_name)
        self.groups.append(execution_group)
        
        # Join user-specific execution group
        user_execution_group = f"agent_executions_{self.user.id}"
        await self.channel_layer.group_add(user_execution_group, self.channel_name)
        self.groups.append(user_execution_group)
        
        # Send initial execution data
        await self.send_initial_execution_data()
    
    async def send_initial_execution_data(self):
        """Send initial agent execution data"""
        try:
            # Get user's recent executions
            recent_executions = await self.get_user_executions()
            
            # Get active executions
            active_executions = await self.get_active_executions()
            
            await self.send_json_data({
                'type': 'initial_execution_data',
                'recent_executions': recent_executions,
                'active_executions': active_executions,
                'timestamp': timezone.now()
            })
        except Exception as e:
            logger.error(f"Error sending initial execution data: {str(e)}")
            await self.send_error("Failed to fetch execution data")
    
    @database_sync_to_async
    def get_user_executions(self):
        """Get user's recent agent executions"""
        try:
            executions = AgentExecution.objects.filter(
                user=self.user
            ).select_related('template').order_by('-created_at')[:10]
            
            return [
                {
                    'id': str(execution.id),
                    'agent_id': str(execution.template.id),
                    'agent_name': execution.template.name,
                    'status': execution.status,
                    'created_at': execution.created_at.isoformat(),
                    'started_at': execution.started_at.isoformat() if execution.started_at else None,
                    'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                    'progress_percentage': execution.progress_percentage,
                    'current_step': execution.current_step
                }
                for execution in executions
            ]
        except Exception as e:
            logger.error(f"Error getting user executions: {str(e)}")
            return []
    
    @database_sync_to_async
    def get_active_executions(self):
        """Get currently active agent executions"""
        try:
            active_executions = AgentExecution.objects.filter(
                status__in=[AgentStatus.PENDING, AgentStatus.RUNNING]
            ).select_related('template', 'user').order_by('-created_at')[:20]
            
            return [
                {
                    'id': str(execution.id),
                    'agent_id': str(execution.template.id),
                    'agent_name': execution.template.name,
                    'user_id': str(execution.user.id),
                    'username': execution.user.username,
                    'status': execution.status,
                    'progress_percentage': execution.progress_percentage,
                    'current_step': execution.current_step,
                    'started_at': execution.started_at.isoformat() if execution.started_at else None
                }
                for execution in active_executions
            ]
        except Exception as e:
            logger.error(f"Error getting active executions: {str(e)}")
            return []
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe_execution':
                execution_id = data.get('execution_id')
                if execution_id:
                    await self.subscribe_to_execution(execution_id)
            elif message_type == 'get_execution_logs':
                execution_id = data.get('execution_id')
                if execution_id:
                    await self.send_execution_logs(execution_id)
            elif message_type == 'cancel_execution':
                execution_id = data.get('execution_id')
                if execution_id:
                    await self.cancel_execution(execution_id)
            elif message_type == 'ping':
                await self.send_json_data({'type': 'pong', 'timestamp': timezone.now()})
            else:
                await self.send_error(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON", "invalid_json")
    
    async def subscribe_to_execution(self, execution_id):
        """Subscribe to specific execution updates"""
        try:
            execution = await self.get_execution(execution_id)
            if not execution:
                await self.send_error("Execution not found", "execution_not_found")
                return
            
            # Check if user owns the execution or has access
            if execution['user_id'] != str(self.user.id) and not self.user.is_staff:
                await self.send_error("Access denied", "access_denied")
                return
            
            execution_group = f"execution_{execution_id}"
            await self.channel_layer.group_add(execution_group, self.channel_name)
            self.groups.append(execution_group)
            
            await self.send_json_data({
                'type': 'subscribed',
                'subscription': 'execution',
                'execution_id': execution_id,
                'execution': execution
            })
            
        except Exception as e:
            logger.error(f"Error subscribing to execution: {str(e)}")
            await self.send_error("Failed to subscribe to execution")
    
    @database_sync_to_async
    def get_execution(self, execution_id):
        """Get execution details"""
        try:
            execution = AgentExecution.objects.select_related('template', 'user').get(id=execution_id)
            return {
                'id': str(execution.id),
                'agent_id': str(execution.template.id),
                'agent_name': execution.template.name,
                'user_id': str(execution.user.id),
                'username': execution.user.username,
                'status': execution.status,
                'progress_percentage': execution.progress_percentage,
                'current_step': execution.current_step,
                'created_at': execution.created_at.isoformat(),
                'started_at': execution.started_at.isoformat() if execution.started_at else None,
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None
            }
        except AgentExecution.DoesNotExist:
            return None
    
    async def send_execution_logs(self, execution_id):
        """Send execution logs"""
        try:
            logs = await self.get_execution_logs(execution_id)
            await self.send_json_data({
                'type': 'execution_logs',
                'execution_id': execution_id,
                'logs': logs
            })
        except Exception as e:
            logger.error(f"Error sending execution logs: {str(e)}")
            await self.send_error("Failed to fetch execution logs")
    
    @database_sync_to_async
    def get_execution_logs(self, execution_id):
        """Get execution logs from database"""
        try:
            execution = AgentExecution.objects.get(id=execution_id)
            return execution.execution_log
        except AgentExecution.DoesNotExist:
            return []
    
    async def cancel_execution(self, execution_id):
        """Cancel an execution"""
        try:
            success = await self.cancel_execution_db(execution_id)
            if success:
                await self.send_json_data({
                    'type': 'execution_cancelled',
                    'execution_id': execution_id,
                    'message': 'Execution cancelled successfully'
                })
            else:
                await self.send_error("Failed to cancel execution or access denied")
        except Exception as e:
            logger.error(f"Error cancelling execution: {str(e)}")
            await self.send_error("Failed to cancel execution")
    
    @database_sync_to_async
    def cancel_execution_db(self, execution_id):
        """Cancel execution in database"""
        try:
            execution = AgentExecution.objects.get(id=execution_id, user=self.user)
            if execution.status in [AgentStatus.PENDING, AgentStatus.RUNNING]:
                execution.status = AgentStatus.CANCELLED
                execution.completed_at = timezone.now()
                execution.save()
                return True
            return False
        except AgentExecution.DoesNotExist:
            return False
    
    # Message handlers for group messages
    async def execution_started(self, event):
        """Handle execution started events"""
        await self.send_json_data({
            'type': 'execution_started',
            'data': event['data'],
            'timestamp': timezone.now()
        })
    
    async def execution_progress(self, event):
        """Handle execution progress updates"""
        await self.send_json_data({
            'type': 'execution_progress',
            'data': event['data'],
            'timestamp': timezone.now()
        })
    
    async def execution_completed(self, event):
        """Handle execution completed events"""
        await self.send_json_data({
            'type': 'execution_completed',
            'data': event['data'],
            'timestamp': timezone.now()
        })
    
    async def execution_failed(self, event):
        """Handle execution failed events"""
        await self.send_json_data({
            'type': 'execution_failed',
            'data': event['data'],
            'timestamp': timezone.now()
        })
    
    async def execution_cancelled(self, event):
        """Handle execution cancelled events"""
        await self.send_json_data({
            'type': 'execution_cancelled',
            'data': event['data'],
            'timestamp': timezone.now()
        })


class AgentOrchestrationConsumer(AgentBaseConsumer):
    """Consumer for agent orchestration and system-wide events"""
    
    async def connect(self):
        """Connect to agent orchestration updates"""
        await super().connect()
        
        # Check if WebSocket authentication is enabled
        enable_ws_auth = os.getenv('ENABLE_WEBSOCKET_AUTH', 'true').lower() == 'true'
        
        # Require authentication if enabled
        if enable_ws_auth and not self.user:
            return
        
        # Join orchestration group - staff only in production, all in development
        if not enable_ws_auth or (self.user and (self.user.is_staff or settings.DEBUG)):
            orchestration_group = "agent_orchestration"
            await self.channel_layer.group_add(orchestration_group, self.channel_name)
            self.groups.append(orchestration_group)
        
        # Join agent registry updates group
        registry_group = "agent_registry"
        await self.channel_layer.group_add(registry_group, self.channel_name)
        self.groups.append(registry_group)
        
        # Send initial orchestration data
        await self.send_initial_orchestration_data()
    
    async def send_initial_orchestration_data(self):
        """Send initial orchestration data"""
        try:
            # Get agent registry
            agent_registry = await self.get_agent_registry()
            
            # Get system metrics
            system_metrics = await self.get_system_metrics()
            
            await self.send_json_data({
                'type': 'initial_orchestration_data',
                'agent_registry': agent_registry,
                'system_metrics': system_metrics,
                'timestamp': timezone.now()
            })
        except Exception as e:
            logger.error(f"Error sending initial orchestration data: {str(e)}")
            await self.send_error("Failed to fetch orchestration data")
    
    @database_sync_to_async
    def get_agent_registry(self):
        """Get available agents from registry"""
        try:
            agents = UnifiedAgentTemplate.objects.filter(is_active=True).order_by('name')
            return [
                {
                    'id': str(agent.id),
                    'name': agent.name,
                    'agent_type': agent.specialization,
                    'description': agent.description,
                    'version': agent.agent_version,
                    'is_active': agent.is_active,
                    'created_at': agent.created_at.isoformat(),
                    'last_updated': agent.updated_at.isoformat()
                }
                for agent in agents
            ]
        except Exception as e:
            logger.error(f"Error getting agent registry: {str(e)}")
            return []
    
    @database_sync_to_async
    def get_system_metrics(self):
        """Get system-wide agent metrics"""
        try:
            from django.db.models import Count, Avg
            
            # Get execution statistics
            execution_stats = AgentExecution.objects.values('status').annotate(count=Count('id'))
            stats_dict = {stat['status']: stat['count'] for stat in execution_stats}
            
            # Get active agents count
            active_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
            
            # Get average execution time (for completed executions)
            avg_execution_time = AgentExecution.objects.filter(
                status=AgentStatus.COMPLETED
            ).aggregate(
                avg_duration=Avg('execution_time_seconds')
            )['avg_duration']
            
            return {
                'active_agents': active_agents,
                'execution_stats': stats_dict,
                'average_execution_time': float(avg_execution_time or 0),
                'last_updated': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            return {}
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'get_agent_details':
                agent_id = data.get('agent_id')
                if agent_id:
                    await self.send_agent_details(agent_id)
            elif message_type == 'refresh_registry':
                await self.refresh_agent_registry()
            elif message_type == 'get_metrics':
                await self.send_system_metrics()
            elif message_type == 'ping':
                await self.send_json_data({'type': 'pong', 'timestamp': timezone.now()})
            else:
                await self.send_error(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON", "invalid_json")
    
    async def send_agent_details(self, agent_id):
        """Send detailed agent information"""
        try:
            agent_details = await self.get_agent_details(agent_id)
            if agent_details:
                await self.send_json_data({
                    'type': 'agent_details',
                    'agent_id': agent_id,
                    'details': agent_details
                })
            else:
                await self.send_error("Agent not found", "agent_not_found")
        except Exception as e:
            logger.error(f"Error sending agent details: {str(e)}")
            await self.send_error("Failed to fetch agent details")
    
    @database_sync_to_async
    def get_agent_details(self, agent_id):
        """Get detailed agent information"""
        try:
            agent = UnifiedAgentTemplate.objects.get(id=agent_id)
            
            # Get recent executions for this agent
            recent_executions = AgentExecution.objects.filter(
                template=agent
            ).order_by('-created_at')[:5]
            
            return {
                'id': str(agent.id),
                'name': agent.name,
                'agent_type': agent.specialization,
                'description': agent.description,
                'version': agent.agent_version,
                'is_active': agent.is_active,
                'configuration': agent.llm_config,
                'capabilities': agent.capabilities,
                'created_at': agent.created_at.isoformat(),
                'last_updated': agent.updated_at.isoformat(),
                'recent_executions': [
                    {
                        'id': str(exec.id),
                        'status': exec.status,
                        'created_at': exec.created_at.isoformat(),
                        'execution_time': exec.execution_time_seconds
                    }
                    for exec in recent_executions
                ]
            }
        except UnifiedAgentTemplate.DoesNotExist:
            return None
    
    async def refresh_agent_registry(self):
        """Refresh and send updated agent registry"""
        try:
            agent_registry = await self.get_agent_registry()
            await self.send_json_data({
                'type': 'registry_updated',
                'agent_registry': agent_registry,
                'timestamp': timezone.now()
            })
        except Exception as e:
            logger.error(f"Error refreshing agent registry: {str(e)}")
            await self.send_error("Failed to refresh agent registry")
    
    async def send_system_metrics(self):
        """Send updated system metrics"""
        try:
            metrics = await self.get_system_metrics()
            await self.send_json_data({
                'type': 'system_metrics',
                'metrics': metrics,
                'timestamp': timezone.now()
            })
        except Exception as e:
            logger.error(f"Error sending system metrics: {str(e)}")
            await self.send_error("Failed to fetch system metrics")
    
    # Message handlers for group messages
    async def agent_registered(self, event):
        """Handle new agent registration"""
        await self.send_json_data({
            'type': 'agent_registered',
            'data': event['data'],
            'timestamp': timezone.now()
        })
    
    async def agent_updated(self, event):
        """Handle agent updates"""
        await self.send_json_data({
            'type': 'agent_updated',
            'data': event['data'],
            'timestamp': timezone.now()
        })
    
    async def agent_deactivated(self, event):
        """Handle agent deactivation"""
        await self.send_json_data({
            'type': 'agent_deactivated',
            'data': event['data'],
            'timestamp': timezone.now()
        })
    
    async def orchestration_event(self, event):
        """Handle general orchestration events"""
        await self.send_json_data({
            'type': 'orchestration_event',
            'data': event['data'],
            'timestamp': timezone.now()
        })