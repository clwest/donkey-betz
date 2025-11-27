"""
Real-Time Collaboration WebSocket Consumer

Session 220 Phase E: Enable multiple users to collaborate on projects
in real-time with presence indicators and synchronized updates.
"""

import json
import logging
import random
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

# Color palette for user presence
PRESENCE_COLORS = [
    '#3B82F6',  # Blue
    '#10B981',  # Green
    '#F59E0B',  # Amber
    '#EF4444',  # Red
    '#8B5CF6',  # Violet
    '#EC4899',  # Pink
    '#06B6D4',  # Cyan
    '#F97316',  # Orange
]


class CollaborationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time project collaboration.

    Events:
    - project:join - User joins project workspace
    - project:leave - User leaves project
    - content:update - Content was modified
    - cursor:move - User cursor position changed
    - selection:change - User selection changed
    - presence:update - Presence status changed
    - comment:add - New comment added
    - comment:resolve - Comment resolved
    """

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope.get('user')
        self.project_id = self.scope['url_route']['kwargs'].get('project_id')
        self.room_group_name = f'collab_{self.project_id}'
        self.presence_color = random.choice(PRESENCE_COLORS)

        # Join project room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Verify project access and create presence
        has_access = await self.verify_project_access()

        if has_access:
            # Create presence record
            await self.create_presence()

            # Notify others of new user
            await self.broadcast_presence_update('joined')

            # Send current state to new user
            await self.send_initial_state()

            logger.info(f"User {self.user} joined collaboration on project {self.project_id}")
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Access denied to this project'
            }))
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'project_id'):
            # Remove presence record
            await self.remove_presence()

            # Notify others
            await self.broadcast_presence_update('left')

            # Leave room
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            logger.info(f"User {self.user} left collaboration on project {self.project_id}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            handlers = {
                'content:update': self.handle_content_update,
                'cursor:move': self.handle_cursor_move,
                'selection:change': self.handle_selection_change,
                'presence:update': self.handle_presence_update,
                'comment:add': self.handle_comment_add,
                'comment:resolve': self.handle_comment_resolve,
                'get_presences': self.handle_get_presences,
                'get_activity': self.handle_get_activity,
                'ping': self.handle_ping,
            }

            handler = handlers.get(message_type)
            if handler:
                await handler(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Error in collaboration consumer: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    # ========== Handler Methods ==========

    async def handle_content_update(self, data):
        """Handle content update from user"""
        content_data = data.get('content', {})
        operation = data.get('operation', 'update')  # add, update, remove
        target_id = data.get('target_id')

        # Save to database
        await self.save_content_update(content_data, operation, target_id)

        # Log activity
        await self.log_activity('edited', {
            'operation': operation,
            'target_id': target_id
        })

        # Broadcast to all users in room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_content_update',
                'user_id': str(self.user.id) if self.user and self.user.is_authenticated else None,
                'username': self.user.username if self.user and self.user.is_authenticated else 'Anonymous',
                'operation': operation,
                'target_id': target_id,
                'content': content_data,
                'timestamp': datetime.now().isoformat()
            }
        )

    async def handle_cursor_move(self, data):
        """Handle cursor position update"""
        position = data.get('position', {})

        # Update presence with cursor position
        await self.update_presence_cursor(position)

        # Broadcast to others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_cursor_move',
                'user_id': str(self.user.id) if self.user and self.user.is_authenticated else None,
                'username': self.user.username if self.user and self.user.is_authenticated else 'Anonymous',
                'color': self.presence_color,
                'position': position
            }
        )

    async def handle_selection_change(self, data):
        """Handle user selection change"""
        selection = data.get('selection', {})

        # Update presence with selection
        await self.update_presence_selection(selection)

        # Broadcast to others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_selection_change',
                'user_id': str(self.user.id) if self.user and self.user.is_authenticated else None,
                'username': self.user.username if self.user and self.user.is_authenticated else 'Anonymous',
                'color': self.presence_color,
                'selection': selection
            }
        )

    async def handle_presence_update(self, data):
        """Handle presence status update (viewing, editing, idle)"""
        status = data.get('status', 'viewing')
        await self.update_presence_status(status)
        await self.broadcast_presence_update('status_changed')

    async def handle_comment_add(self, data):
        """Handle new comment"""
        comment_text = data.get('text', '')
        target_type = data.get('target_type', '')
        target_id = data.get('target_id', '')
        parent_id = data.get('parent_id')

        # Save comment
        comment = await self.save_comment(comment_text, target_type, target_id, parent_id)

        # Log activity
        await self.log_activity('commented', {
            'comment_id': str(comment.id) if comment else None,
            'target_type': target_type,
            'target_id': target_id
        })

        # Broadcast to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_comment_add',
                'comment': {
                    'id': str(comment.id) if comment else None,
                    'text': comment_text,
                    'target_type': target_type,
                    'target_id': target_id,
                    'user_id': str(self.user.id) if self.user and self.user.is_authenticated else None,
                    'username': self.user.username if self.user and self.user.is_authenticated else 'Anonymous',
                    'created_at': datetime.now().isoformat()
                }
            }
        )

    async def handle_comment_resolve(self, data):
        """Handle comment resolution"""
        comment_id = data.get('comment_id')

        # Resolve comment
        await self.resolve_comment(comment_id)

        # Broadcast to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_comment_resolve',
                'comment_id': comment_id,
                'resolved_by': self.user.username if self.user and self.user.is_authenticated else 'Anonymous',
                'resolved_at': datetime.now().isoformat()
            }
        )

    async def handle_get_presences(self, data):
        """Get all current presences for this project"""
        presences = await self.get_all_presences()
        await self.send(text_data=json.dumps({
            'type': 'presences',
            'presences': presences
        }))

    async def handle_get_activity(self, data):
        """Get recent activity for this project"""
        limit = data.get('limit', 20)
        activities = await self.get_recent_activity(limit)
        await self.send(text_data=json.dumps({
            'type': 'activity',
            'activities': activities
        }))

    async def handle_ping(self, data):
        """Keep-alive ping"""
        await self.update_presence_activity()
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': datetime.now().isoformat()
        }))

    # ========== Broadcast Methods ==========

    async def broadcast_content_update(self, event):
        """Send content update to client"""
        await self.send(text_data=json.dumps({
            'type': 'content:update',
            'user_id': event['user_id'],
            'username': event['username'],
            'operation': event['operation'],
            'target_id': event['target_id'],
            'content': event['content'],
            'timestamp': event['timestamp']
        }))

    async def broadcast_cursor_move(self, event):
        """Send cursor move to client (excluding sender)"""
        if event.get('user_id') != str(self.user.id if self.user and self.user.is_authenticated else None):
            await self.send(text_data=json.dumps({
                'type': 'cursor:move',
                'user_id': event['user_id'],
                'username': event['username'],
                'color': event['color'],
                'position': event['position']
            }))

    async def broadcast_selection_change(self, event):
        """Send selection change to client (excluding sender)"""
        if event.get('user_id') != str(self.user.id if self.user and self.user.is_authenticated else None):
            await self.send(text_data=json.dumps({
                'type': 'selection:change',
                'user_id': event['user_id'],
                'username': event['username'],
                'color': event['color'],
                'selection': event['selection']
            }))

    async def broadcast_presence(self, event):
        """Send presence update to client"""
        await self.send(text_data=json.dumps({
            'type': 'presence:update',
            'action': event['action'],
            'user': event['user']
        }))

    async def broadcast_comment_add(self, event):
        """Send new comment to client"""
        await self.send(text_data=json.dumps({
            'type': 'comment:add',
            'comment': event['comment']
        }))

    async def broadcast_comment_resolve(self, event):
        """Send comment resolution to client"""
        await self.send(text_data=json.dumps({
            'type': 'comment:resolve',
            'comment_id': event['comment_id'],
            'resolved_by': event['resolved_by'],
            'resolved_at': event['resolved_at']
        }))

    # ========== Database Methods ==========

    @database_sync_to_async
    def verify_project_access(self):
        """Check if user has access to project"""
        from core.models_unified_system import SharedProject, ProjectCollaborator

        if not self.user or not self.user.is_authenticated:
            return False

        try:
            project = SharedProject.objects.get(id=self.project_id)

            # Owner has access
            if project.owner_id == self.user.id:
                return True

            # Check collaborator access
            return ProjectCollaborator.objects.filter(
                project_id=self.project_id,
                user_id=self.user.id,
                status='accepted'
            ).exists()

        except SharedProject.DoesNotExist:
            return False

    @database_sync_to_async
    def create_presence(self):
        """Create presence record for user in project"""
        from core.models_unified_system import ProjectPresence

        if not self.user or not self.user.is_authenticated:
            return

        # Clean up any stale presences first
        ProjectPresence.cleanup_stale()

        # Create or update presence
        presence, created = ProjectPresence.objects.update_or_create(
            project_id=self.project_id,
            user_id=self.user.id,
            channel_name=self.channel_name,
            defaults={
                'is_active': True,
                'status': 'viewing',
                'color': self.presence_color
            }
        )
        return presence

    @database_sync_to_async
    def remove_presence(self):
        """Remove presence record"""
        from core.models_unified_system import ProjectPresence

        if not self.user or not self.user.is_authenticated:
            return

        ProjectPresence.objects.filter(
            project_id=self.project_id,
            user_id=self.user.id,
            channel_name=self.channel_name
        ).delete()

    @database_sync_to_async
    def update_presence_cursor(self, position):
        """Update cursor position in presence"""
        from core.models_unified_system import ProjectPresence

        if not self.user or not self.user.is_authenticated:
            return

        ProjectPresence.objects.filter(
            project_id=self.project_id,
            user_id=self.user.id,
            channel_name=self.channel_name
        ).update(cursor_position=position)

    @database_sync_to_async
    def update_presence_selection(self, selection):
        """Update selection in presence"""
        from core.models_unified_system import ProjectPresence

        if not self.user or not self.user.is_authenticated:
            return

        ProjectPresence.objects.filter(
            project_id=self.project_id,
            user_id=self.user.id,
            channel_name=self.channel_name
        ).update(selection=selection)

    @database_sync_to_async
    def update_presence_status(self, status):
        """Update presence status"""
        from core.models_unified_system import ProjectPresence

        if not self.user or not self.user.is_authenticated:
            return

        ProjectPresence.objects.filter(
            project_id=self.project_id,
            user_id=self.user.id,
            channel_name=self.channel_name
        ).update(status=status)

    @database_sync_to_async
    def update_presence_activity(self):
        """Update last activity timestamp"""
        from core.models_unified_system import ProjectPresence
        from django.utils import timezone

        if not self.user or not self.user.is_authenticated:
            return

        ProjectPresence.objects.filter(
            project_id=self.project_id,
            user_id=self.user.id,
            channel_name=self.channel_name
        ).update(last_activity=timezone.now())

    @database_sync_to_async
    def get_all_presences(self):
        """Get all active presences for project"""
        from core.models_unified_system import ProjectPresence

        presences = ProjectPresence.objects.filter(
            project_id=self.project_id,
            is_active=True
        ).select_related('user')

        return [{
            'user_id': str(p.user_id),
            'username': p.user.username,
            'status': p.status,
            'color': p.color,
            'cursor_position': p.cursor_position,
            'selection': p.selection,
            'connected_at': p.connected_at.isoformat()
        } for p in presences]

    async def broadcast_presence_update(self, action):
        """Broadcast presence update to room"""
        if not self.user or not self.user.is_authenticated:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_presence',
                'action': action,
                'user': {
                    'id': str(self.user.id),
                    'username': self.user.username,
                    'color': self.presence_color
                }
            }
        )

    @database_sync_to_async
    def save_content_update(self, content_data, operation, target_id):
        """Save content update to project"""
        from core.models_unified_system import SharedProject

        try:
            project = SharedProject.objects.get(id=self.project_id)

            # Update content based on operation
            current_content = project.content or {}

            if operation == 'add':
                if 'items' not in current_content:
                    current_content['items'] = []
                current_content['items'].append(content_data)
            elif operation == 'update' and target_id:
                if 'items' in current_content:
                    for i, item in enumerate(current_content['items']):
                        if item.get('id') == target_id:
                            current_content['items'][i] = content_data
                            break
            elif operation == 'remove' and target_id:
                if 'items' in current_content:
                    current_content['items'] = [
                        item for item in current_content['items']
                        if item.get('id') != target_id
                    ]

            project.content = current_content
            project.last_edited_by = self.user
            project.increment_version()

        except SharedProject.DoesNotExist:
            pass

    @database_sync_to_async
    def log_activity(self, action, details):
        """Log activity to project"""
        from core.models_unified_system import ProjectActivity

        if not self.user or not self.user.is_authenticated:
            return

        ProjectActivity.objects.create(
            project_id=self.project_id,
            user=self.user,
            action=action,
            details=details
        )

    @database_sync_to_async
    def get_recent_activity(self, limit):
        """Get recent activity for project"""
        from core.models_unified_system import ProjectActivity

        activities = ProjectActivity.objects.filter(
            project_id=self.project_id
        ).select_related('user').order_by('-created_at')[:limit]

        return [{
            'id': str(a.id),
            'user_id': str(a.user_id),
            'username': a.user.username,
            'action': a.action,
            'details': a.details,
            'created_at': a.created_at.isoformat()
        } for a in activities]

    @database_sync_to_async
    def save_comment(self, text, target_type, target_id, parent_id):
        """Save comment to project"""
        from core.models_unified_system import ProjectComment

        if not self.user or not self.user.is_authenticated:
            return None

        return ProjectComment.objects.create(
            project_id=self.project_id,
            user=self.user,
            text=text,
            target_type=target_type,
            target_id=target_id,
            parent_id=parent_id
        )

    @database_sync_to_async
    def resolve_comment(self, comment_id):
        """Resolve a comment"""
        from core.models_unified_system import ProjectComment
        from django.utils import timezone

        if not self.user or not self.user.is_authenticated:
            return

        ProjectComment.objects.filter(
            id=comment_id,
            project_id=self.project_id
        ).update(
            is_resolved=True,
            resolved_by=self.user,
            resolved_at=timezone.now()
        )

    async def send_initial_state(self):
        """Send initial project state to newly connected user"""
        project_data = await self.get_project_data()
        presences = await self.get_all_presences()
        activities = await self.get_recent_activity(10)
        comments = await self.get_project_comments()

        await self.send(text_data=json.dumps({
            'type': 'initial_state',
            'project': project_data,
            'presences': presences,
            'activities': activities,
            'comments': comments,
            'your_color': self.presence_color
        }))

    @database_sync_to_async
    def get_project_data(self):
        """Get project data for initial load"""
        from core.models_unified_system import SharedProject

        try:
            project = SharedProject.objects.get(id=self.project_id)
            return {
                'id': str(project.id),
                'name': project.name,
                'description': project.description,
                'content': project.content,
                'project_settings': project.project_settings,
                'version': project.version,
                'owner_id': str(project.owner_id),
                'updated_at': project.updated_at.isoformat()
            }
        except SharedProject.DoesNotExist:
            return None

    @database_sync_to_async
    def get_project_comments(self):
        """Get all comments for project"""
        from core.models_unified_system import ProjectComment

        comments = ProjectComment.objects.filter(
            project_id=self.project_id
        ).select_related('user', 'resolved_by').order_by('created_at')

        return [{
            'id': str(c.id),
            'text': c.text,
            'target_type': c.target_type,
            'target_id': c.target_id,
            'user_id': str(c.user_id),
            'username': c.user.username,
            'parent_id': str(c.parent_id) if c.parent_id else None,
            'is_resolved': c.is_resolved,
            'resolved_by': c.resolved_by.username if c.resolved_by else None,
            'resolved_at': c.resolved_at.isoformat() if c.resolved_at else None,
            'created_at': c.created_at.isoformat()
        } for c in comments]
