"""
Pipeline Progress WebSocket Consumer
=====================================

Session 342: Real-time pipeline visualization updates.

This consumer broadcasts pipeline stage updates to connected clients,
enabling the Pipeline Visualizer UI to show real-time progress.

Stages tracked:
- Research Pipeline: initial_research, trend_analysis, competitor_analysis,
                     customer_research, brand_strategy, opportunity_scoring, synthesis
- Creative Pipeline: brief, creative_direction, image, video, audio, 3d,
                     editing, trained_character, seo, content_audit
"""

import json
import logging
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


class PipelineProgressConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time pipeline progress updates.

    Broadcasts stage transitions to connected Pipeline Visualizer UIs.
    """

    async def connect(self):
        """Join the pipeline progress group."""
        self.room_group_name = 'pipeline_progress'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to pipeline progress updates',
            'timestamp': datetime.now().isoformat()
        }))

    async def disconnect(self, close_code):
        """Leave the pipeline progress group."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming messages from clients."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'ping')

            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
            elif message_type == 'subscribe':
                # Subscribe to a specific pipeline run
                pipeline_id = data.get('pipeline_id')
                await self.send(text_data=json.dumps({
                    'type': 'subscribed',
                    'pipeline_id': pipeline_id,
                    'timestamp': datetime.now().isoformat()
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    async def pipeline_stage_started(self, event):
        """Broadcast when a pipeline stage starts."""
        await self.send(text_data=json.dumps({
            'type': 'stage_started',
            'pipeline_type': event.get('pipeline_type', 'research'),  # research or creative
            'stage': event['stage'],
            'stage_name': event.get('stage_name', event['stage']),
            'agent_name': event.get('agent_name'),
            'timestamp': event.get('timestamp', datetime.now().isoformat()),
            'project_id': event.get('project_id'),
            'business_idea': event.get('business_idea')
        }))

    async def pipeline_stage_completed(self, event):
        """Broadcast when a pipeline stage completes."""
        await self.send(text_data=json.dumps({
            'type': 'stage_completed',
            'pipeline_type': event.get('pipeline_type', 'research'),
            'stage': event['stage'],
            'stage_name': event.get('stage_name', event['stage']),
            'agent_name': event.get('agent_name'),
            'success': event.get('success', True),
            'duration_ms': event.get('duration_ms'),
            'timestamp': event.get('timestamp', datetime.now().isoformat()),
            'project_id': event.get('project_id'),
            'summary': event.get('summary')
        }))

    async def pipeline_stage_failed(self, event):
        """Broadcast when a pipeline stage fails."""
        await self.send(text_data=json.dumps({
            'type': 'stage_failed',
            'pipeline_type': event.get('pipeline_type', 'research'),
            'stage': event['stage'],
            'stage_name': event.get('stage_name', event['stage']),
            'agent_name': event.get('agent_name'),
            'error': event.get('error'),
            'timestamp': event.get('timestamp', datetime.now().isoformat()),
            'project_id': event.get('project_id')
        }))

    async def pipeline_completed(self, event):
        """Broadcast when entire pipeline completes."""
        await self.send(text_data=json.dumps({
            'type': 'pipeline_completed',
            'pipeline_type': event.get('pipeline_type', 'research'),
            'phases_completed': event.get('phases_completed', []),
            'total_duration_ms': event.get('total_duration_ms'),
            'success': event.get('success', True),
            'timestamp': event.get('timestamp', datetime.now().isoformat()),
            'project_id': event.get('project_id'),
            'summary': event.get('summary')
        }))


# ==================== Helper Functions ====================

def broadcast_stage_started(stage: str, pipeline_type: str = 'research',
                           agent_name: str = None, project_id: str = None,
                           business_idea: str = None):
    """
    Broadcast that a pipeline stage has started.

    Call this from research_orchestrator or creative_orchestrator.
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        try:
            async_to_sync(channel_layer.group_send)(
                'pipeline_progress',
                {
                    'type': 'pipeline_stage_started',
                    'stage': stage,
                    'stage_name': _format_stage_name(stage),
                    'pipeline_type': pipeline_type,
                    'agent_name': agent_name,
                    'project_id': project_id,
                    'business_idea': business_idea,
                    'timestamp': datetime.now().isoformat()
                }
            )
            logger.debug(f"Broadcast stage started: {stage}")
        except Exception as e:
            logger.warning(f"Failed to broadcast stage started: {e}")


def broadcast_stage_completed(stage: str, pipeline_type: str = 'research',
                             agent_name: str = None, success: bool = True,
                             duration_ms: int = None, project_id: str = None,
                             summary: str = None):
    """
    Broadcast that a pipeline stage has completed.

    Call this from research_orchestrator or creative_orchestrator.
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        try:
            async_to_sync(channel_layer.group_send)(
                'pipeline_progress',
                {
                    'type': 'pipeline_stage_completed',
                    'stage': stage,
                    'stage_name': _format_stage_name(stage),
                    'pipeline_type': pipeline_type,
                    'agent_name': agent_name,
                    'success': success,
                    'duration_ms': duration_ms,
                    'project_id': project_id,
                    'summary': summary,
                    'timestamp': datetime.now().isoformat()
                }
            )
            logger.debug(f"Broadcast stage completed: {stage}")
        except Exception as e:
            logger.warning(f"Failed to broadcast stage completed: {e}")


def broadcast_stage_failed(stage: str, pipeline_type: str = 'research',
                          agent_name: str = None, error: str = None,
                          project_id: str = None):
    """
    Broadcast that a pipeline stage has failed.
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        try:
            async_to_sync(channel_layer.group_send)(
                'pipeline_progress',
                {
                    'type': 'pipeline_stage_failed',
                    'stage': stage,
                    'stage_name': _format_stage_name(stage),
                    'pipeline_type': pipeline_type,
                    'agent_name': agent_name,
                    'error': error,
                    'project_id': project_id,
                    'timestamp': datetime.now().isoformat()
                }
            )
            logger.debug(f"Broadcast stage failed: {stage}")
        except Exception as e:
            logger.warning(f"Failed to broadcast stage failed: {e}")


def broadcast_pipeline_completed(pipeline_type: str = 'research',
                                phases_completed: list = None,
                                total_duration_ms: int = None,
                                success: bool = True,
                                project_id: str = None,
                                summary: str = None):
    """
    Broadcast that the entire pipeline has completed.
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        try:
            async_to_sync(channel_layer.group_send)(
                'pipeline_progress',
                {
                    'type': 'pipeline_completed',
                    'pipeline_type': pipeline_type,
                    'phases_completed': phases_completed or [],
                    'total_duration_ms': total_duration_ms,
                    'success': success,
                    'project_id': project_id,
                    'summary': summary,
                    'timestamp': datetime.now().isoformat()
                }
            )
            logger.info(f"Broadcast pipeline completed: {pipeline_type}")
        except Exception as e:
            logger.warning(f"Failed to broadcast pipeline completed: {e}")


def _format_stage_name(stage: str) -> str:
    """Format stage ID to human-readable name."""
    stage_names = {
        # Research stages
        'initial_research': 'Initial Research',
        'trend_analysis': 'Trend Analysis',
        'competitor_analysis': 'Competitor Analysis',
        'customer_research': 'Customer Research',
        'brand_strategy': 'Brand Strategy',
        'opportunity_scoring': 'Opportunity Scoring',
        'synthesis': 'Synthesis',
        # Creative stages
        'brief': 'Creative Brief',
        'creative_direction': 'Creative Direction',
        'image': 'Image Generation',
        'video': 'Video Generation',
        'audio': 'Audio Generation',
        '3d': '3D Generation',
        'editing': 'Editing',
        'trained_character': 'Trained Character',
        'seo': 'SEO Optimization',
        'content_audit': 'Content Audit'
    }
    return stage_names.get(stage, stage.replace('_', ' ').title())
