"""
Content Management System WebSocket Consumers

Real-time WebSocket consumers for content processing, generation, and workflow updates.
"""

import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from .models import (
    Document, ContentGeneration, WorkflowExecution, 
    ContentTemplate, KnowledgeBase
)

User = get_user_model()
logger = logging.getLogger(__name__)


class ContentProcessingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time content processing updates"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join user-specific content processing group
        self.group_name = f"content_processing_{self.user.id}"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to content processing updates',
            'user_id': str(self.user.id)
        }))
        
        logger.info(f"User {self.user.username} connected to content processing WebSocket")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        
        logger.info(f"User {getattr(self.user, 'username', 'unknown')} disconnected from content processing WebSocket")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', '')
            
            if message_type == 'subscribe_document':
                await self.handle_document_subscription(data)
            elif message_type == 'subscribe_generation':
                await self.handle_generation_subscription(data)
            elif message_type == 'subscribe_workflow':
                await self.handle_workflow_subscription(data)
            elif message_type == 'get_status':
                await self.handle_status_request(data)
            else:
                await self.send_error("Unknown message type")
        
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
            await self.send_error("Internal server error")
    
    async def handle_document_subscription(self, data):
        """Handle document processing subscription"""
        document_id = data.get('document_id')
        if not document_id:
            await self.send_error("Document ID required")
            return
        
        # Verify user has access to document
        document = await self.get_user_document(document_id)
        if not document:
            await self.send_error("Document not found or access denied")
            return
        
        # Join document-specific group
        document_group = f"document_{document_id}"
        await self.channel_layer.group_add(
            document_group,
            self.channel_name
        )
        
        # Send current status
        await self.send(text_data=json.dumps({
            'type': 'document_status',
            'document_id': document_id,
            'status': document.status,
            'progress': self.get_document_progress(document),
            'message': 'Subscribed to document updates'
        }))
    
    async def handle_generation_subscription(self, data):
        """Handle content generation subscription"""
        generation_id = data.get('generation_id')
        if not generation_id:
            await self.send_error("Generation ID required")
            return
        
        # Verify user owns generation
        generation = await self.get_user_generation(generation_id)
        if not generation:
            await self.send_error("Generation not found or access denied")
            return
        
        # Join generation-specific group
        generation_group = f"generation_{generation_id}"
        await self.channel_layer.group_add(
            generation_group,
            self.channel_name
        )
        
        # Send current status
        await self.send(text_data=json.dumps({
            'type': 'generation_status',
            'generation_id': generation_id,
            'status': generation.status,
            'progress': self.get_generation_progress(generation),
            'message': 'Subscribed to generation updates'
        }))
    
    async def handle_workflow_subscription(self, data):
        """Handle workflow execution subscription"""
        execution_id = data.get('execution_id')
        if not execution_id:
            await self.send_error("Execution ID required")
            return
        
        # Verify user owns execution
        execution = await self.get_user_execution(execution_id)
        if not execution:
            await self.send_error("Execution not found or access denied")
            return
        
        # Join execution-specific group
        execution_group = f"execution_{execution_id}"
        await self.channel_layer.group_add(
            execution_group,
            self.channel_name
        )
        
        # Send current status
        await self.send(text_data=json.dumps({
            'type': 'workflow_status',
            'execution_id': execution_id,
            'status': execution.status,
            'progress': execution.progress_percentage,
            'current_step': execution.current_step,
            'message': 'Subscribed to workflow updates'
        }))
    
    async def handle_status_request(self, data):
        """Handle status request for multiple items"""
        request_type = data.get('request_type')
        
        if request_type == 'user_activity':
            await self.send_user_activity_status()
        elif request_type == 'system_status':
            await self.send_system_status()
        else:
            await self.send_error("Unknown status request type")
    
    # WebSocket message handlers (called by group_send)
    
    async def document_update(self, event):
        """Handle document processing updates"""
        await self.send(text_data=json.dumps({
            'type': 'document_update',
            'document_id': event['document_id'],
            'status': event['status'],
            'progress': event.get('progress', 0),
            'step': event.get('step', ''),
            'message': event.get('message', ''),
            'timestamp': event.get('timestamp', '')
        }))
    
    async def generation_update(self, event):
        """Handle content generation updates"""
        await self.send(text_data=json.dumps({
            'type': 'generation_update',
            'generation_id': event['generation_id'],
            'status': event['status'],
            'progress': event.get('progress', 0),
            'content_preview': event.get('content_preview', ''),
            'tokens_used': event.get('tokens_used', 0),
            'cost': event.get('cost', 0.0),
            'message': event.get('message', ''),
            'timestamp': event.get('timestamp', '')
        }))
    
    async def workflow_update(self, event):
        """Handle workflow execution updates"""
        await self.send(text_data=json.dumps({
            'type': 'workflow_update',
            'execution_id': event['execution_id'],
            'status': event['status'],
            'progress': event.get('progress', 0),
            'current_step': event.get('current_step', 0),
            'step_name': event.get('step_name', ''),
            'step_result': event.get('step_result', {}),
            'message': event.get('message', ''),
            'timestamp': event.get('timestamp', '')
        }))
    
    async def system_notification(self, event):
        """Handle system-wide notifications"""
        await self.send(text_data=json.dumps({
            'type': 'system_notification',
            'level': event.get('level', 'info'),
            'title': event.get('title', ''),
            'message': event.get('message', ''),
            'timestamp': event.get('timestamp', '')
        }))
    
    # Helper methods
    
    async def send_error(self, message: str):
        """Send error message to client"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    async def send_user_activity_status(self):
        """Send user's recent activity status"""
        try:
            # Get recent documents
            recent_docs = await self.get_user_recent_documents()
            
            # Get recent generations
            recent_generations = await self.get_user_recent_generations()
            
            # Get active workflows
            active_workflows = await self.get_user_active_workflows()
            
            await self.send(text_data=json.dumps({
                'type': 'user_activity_status',
                'recent_documents': recent_docs,
                'recent_generations': recent_generations,
                'active_workflows': active_workflows
            }))
        
        except Exception as e:
            logger.error(f"Error sending user activity status: {str(e)}")
            await self.send_error("Failed to fetch user activity status")
    
    async def send_system_status(self):
        """Send system status information"""
        try:
            status = await self.get_system_status()
            await self.send(text_data=json.dumps({
                'type': 'system_status',
                **status
            }))
        
        except Exception as e:
            logger.error(f"Error sending system status: {str(e)}")
            await self.send_error("Failed to fetch system status")
    
    # Database helpers
    
    @database_sync_to_async
    def get_user_document(self, document_id):
        """Get document if user has access"""
        try:
            return Document.objects.get(
                id=document_id,
                owner=self.user
            )
        except Document.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_user_generation(self, generation_id):
        """Get generation if user owns it"""
        try:
            return ContentGeneration.objects.get(
                id=generation_id,
                user=self.user
            )
        except ContentGeneration.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_user_execution(self, execution_id):
        """Get execution if user owns it"""
        try:
            return WorkflowExecution.objects.get(
                id=execution_id,
                user=self.user
            )
        except WorkflowExecution.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_user_recent_documents(self):
        """Get user's recent documents"""
        documents = Document.objects.filter(
            owner=self.user
        ).order_by('-created_at')[:10]
        
        return [
            {
                'id': str(doc.id),
                'title': doc.title,
                'status': doc.status,
                'created_at': doc.created_at.isoformat(),
                'progress': self.get_document_progress(doc)
            }
            for doc in documents
        ]
    
    @database_sync_to_async
    def get_user_recent_generations(self):
        """Get user's recent generations"""
        generations = ContentGeneration.objects.filter(
            user=self.user
        ).order_by('-created_at')[:10]
        
        return [
            {
                'id': str(gen.id),
                'template_name': gen.template.display_name if gen.template else 'Custom',
                'status': gen.status,
                'created_at': gen.created_at.isoformat(),
                'progress': self.get_generation_progress(gen)
            }
            for gen in generations
        ]
    
    @database_sync_to_async
    def get_user_active_workflows(self):
        """Get user's active workflow executions"""
        executions = WorkflowExecution.objects.filter(
            user=self.user,
            status__in=['pending', 'processing']
        ).order_by('-created_at')
        
        return [
            {
                'id': str(exec.id),
                'workflow_name': exec.workflow.name,
                'status': exec.status,
                'progress': exec.progress_percentage,
                'current_step': exec.current_step,
                'started_at': exec.started_at.isoformat() if exec.started_at else None
            }
            for exec in executions
        ]
    
    @database_sync_to_async
    def get_system_status(self):
        """Get system-wide status information"""
        # This would include system metrics, active processes, etc.
        return {
            'active_users': 1,  # Placeholder
            'processing_queue': 0,  # Placeholder
            'system_health': 'healthy'
        }
    
    def get_document_progress(self, document):
        """Calculate document processing progress"""
        if document.status == 'pending':
            return 0
        elif document.status == 'processing':
            # Estimate progress based on processing log
            steps = len(document.processing_log)
            if steps > 0:
                return min(80, steps * 20)  # Max 80% while processing
            return 10
        elif document.status == 'processed':
            return 100
        elif document.status == 'failed':
            return -1  # Indicate failure
        else:
            return 0
    
    def get_generation_progress(self, generation):
        """Calculate content generation progress"""
        if generation.status == 'pending':
            return 0
        elif generation.status == 'processing':
            return 50  # Simple estimate
        elif generation.status == 'processed':
            return 100
        elif generation.status == 'failed':
            return -1  # Indicate failure
        else:
            return 0


class ContentAnalyticsConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time analytics updates"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join analytics group
        self.group_name = f"content_analytics_{self.user.id}"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial analytics data
        await self.send_analytics_dashboard()
        
        logger.info(f"User {self.user.username} connected to content analytics WebSocket")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', '')
            
            if message_type == 'get_dashboard':
                await self.send_analytics_dashboard()
            elif message_type == 'get_metrics':
                await self.send_metrics(data.get('metric_type', 'all'))
            else:
                await self.send_error("Unknown message type")
        
        except Exception as e:
            logger.error(f"Error in analytics WebSocket: {str(e)}")
            await self.send_error("Internal server error")
    
    async def send_analytics_dashboard(self):
        """Send analytics dashboard data"""
        try:
            dashboard_data = await self.get_dashboard_data()
            await self.send(text_data=json.dumps({
                'type': 'analytics_dashboard',
                **dashboard_data
            }))
        
        except Exception as e:
            logger.error(f"Error sending analytics dashboard: {str(e)}")
            await self.send_error("Failed to fetch analytics data")
    
    async def send_metrics(self, metric_type: str):
        """Send specific metrics"""
        try:
            metrics = await self.get_metrics_data(metric_type)
            await self.send(text_data=json.dumps({
                'type': 'metrics_update',
                'metric_type': metric_type,
                'metrics': metrics
            }))
        
        except Exception as e:
            logger.error(f"Error sending metrics: {str(e)}")
            await self.send_error("Failed to fetch metrics")
    
    async def analytics_update(self, event):
        """Handle analytics updates"""
        await self.send(text_data=json.dumps(event))
    
    async def send_error(self, message: str):
        """Send error message"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    @database_sync_to_async
    def get_dashboard_data(self):
        """Get analytics dashboard data"""
        # This would fetch real analytics data
        return {
            'total_documents': Document.objects.filter(owner=self.user).count(),
            'total_generations': ContentGeneration.objects.filter(user=self.user).count(),
            'total_workflows': WorkflowExecution.objects.filter(user=self.user).count(),
            'processing_stats': {
                'pending': 0,
                'processing': 1,
                'completed': 5,
                'failed': 0
            }
        }
    
    @database_sync_to_async
    def get_metrics_data(self, metric_type: str):
        """Get specific metrics data"""
        # This would fetch specific metrics
        return {
            'timestamp': '2024-01-01T00:00:00Z',
            'values': [1, 2, 3, 4, 5]
        }