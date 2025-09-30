"""
Learning Dashboard WebSocket Consumer
======================================
Real-time display of user's AI learnings
"""

import json
import logging
from typing import Dict, Any, List
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.db.models import Avg, Sum

logger = logging.getLogger(__name__)


class LearningDashboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for Learning Dashboard page
    Shows user what the AI has learned about their preferences
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.room_name = None
        self.room_group_name = None

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope.get('user', AnonymousUser())

        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        self.room_name = f'learning_{self.user.id}'
        self.room_group_name = f'learning_dashboard_{self.user.id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        logger.info(f"✅ Learning Dashboard WebSocket connected for user {self.user.username}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        logger.info(f"Learning Dashboard WebSocket disconnected for user {self.user.username if self.user else 'unknown'}")

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'get_user_learnings':
                await self.send_user_learnings()
            elif action == 'get_collaborative_recommendations':
                await self.send_collaborative_recommendations()
            elif action == 'get_similar_users':
                await self.send_similar_users()
            elif action == 'get_learning_evolution':
                await self.send_learning_evolution(data.get('domain'))
            else:
                logger.warning(f"Unknown action: {action}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            await self.send_error("Invalid JSON data")
        except Exception as e:
            logger.error(f"Error in receive: {e}", exc_info=True)
            await self.send_error(str(e))

    async def send_user_learnings(self):
        """Send user's learnings and stats"""
        try:
            # Note: UserAgentLearning model needs to be created in database first
            # For now, send empty data with a helpful message
            learnings = []
            stats = {
                'total_learnings': 0,
                'avg_confidence': 0,
                'success_rate': 0,
                'total_usage': 0
            }

            # Try to get real learnings if table exists
            try:
                learnings = await self.get_learnings_from_db()
                stats = await self.calculate_stats()
            except Exception as e:
                logger.warning(f"Could not load learnings (table may not exist yet): {e}")

            await self.send(text_data=json.dumps({
                'type': 'user_learnings',
                'learnings': learnings,
                'stats': stats
            }))

            logger.info(f"📊 Sent {len(learnings)} learnings to user {self.user.username}")

        except Exception as e:
            logger.error(f"Error sending learnings: {e}", exc_info=True)
            await self.send_error("Could not load learnings")

    @database_sync_to_async
    def get_learnings_from_db(self) -> List[Dict[str, Any]]:
        """Get all learnings for current user from database"""
        try:
            from core.models import UserAgentLearning

            learnings = UserAgentLearning.objects.filter(
                user=self.user,
                is_active=True
            ).order_by('-confidence_score')

            return [
                {
                    'id': learning.id,
                    'agent_name': learning.agent_name,
                    'learning_domain': learning.learning_domain,
                    'learning_content': learning.learning_content,
                    'confidence_score': learning.confidence_score,
                    'validation_count': learning.validation_count,
                    'failure_count': learning.failure_count,
                    'success_rate': learning.success_rate,
                    'learning_source': learning.learning_source,
                    'usage_count': learning.usage_count,
                    'last_used': learning.last_used.isoformat() if learning.last_used else None,
                    'created_at': learning.created_at.isoformat() if hasattr(learning, 'created_at') else None,
                }
                for learning in learnings
            ]
        except Exception as e:
            logger.error(f"Error getting learnings from DB: {e}")
            return []

    @database_sync_to_async
    def calculate_stats(self) -> Dict[str, Any]:
        """Calculate overall learning statistics"""
        try:
            from core.models import UserAgentLearning

            learnings = UserAgentLearning.objects.filter(
                user=self.user,
                is_active=True
            )

            total_learnings = learnings.count()

            if total_learnings == 0:
                return {
                    'total_learnings': 0,
                    'avg_confidence': 0,
                    'success_rate': 0,
                    'total_usage': 0
                }

            stats = learnings.aggregate(
                avg_confidence=Avg('confidence_score'),
                avg_success_rate=Avg('success_rate'),
                total_usage=Sum('usage_count')
            )

            return {
                'total_learnings': total_learnings,
                'avg_confidence': stats['avg_confidence'] or 0,
                'success_rate': stats['avg_success_rate'] or 0,
                'total_usage': stats['total_usage'] or 0
            }
        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
            return {
                'total_learnings': 0,
                'avg_confidence': 0,
                'success_rate': 0,
                'total_usage': 0
            }

    async def send_error(self, message: str):
        """Send error message to client"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))

    @database_sync_to_async
    def get_collaborative_recommendations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get collaborative filtering recommendations"""
        try:
            from core.models import UserAgentLearning

            recommendations = UserAgentLearning.get_collaborative_recommendations(
                user=self.user,
                limit=limit
            )

            return recommendations

        except Exception as e:
            logger.error(f"Error getting collaborative recommendations: {e}")
            return []

    async def send_collaborative_recommendations(self):
        """Send 'Users like you also learned...' recommendations"""
        try:
            recommendations = await self.get_collaborative_recommendations(limit=10)

            await self.send(text_data=json.dumps({
                'type': 'collaborative_recommendations',
                'recommendations': recommendations,
                'count': len(recommendations)
            }))

            logger.info(f"📊 Sent {len(recommendations)} collaborative recommendations to user {self.user.username}")

        except Exception as e:
            logger.error(f"Error sending collaborative recommendations: {e}", exc_info=True)
            await self.send_error("Could not load recommendations")

    @database_sync_to_async
    def get_similar_users_data(self, min_similarity: float = 0.5) -> List[Dict[str, Any]]:
        """Get users with similar learning patterns"""
        try:
            from core.models import UserAgentLearning

            # Get any learning from current user to access cohort method
            learning = UserAgentLearning.objects.filter(
                user=self.user,
                is_active=True
            ).first()

            if not learning:
                return []

            similar_users = learning.get_learning_cohort(min_similarity=min_similarity)

            return similar_users

        except Exception as e:
            logger.error(f"Error getting similar users: {e}")
            return []

    async def send_similar_users(self):
        """Send similar users cohort"""
        try:
            similar_users = await self.get_similar_users_data(min_similarity=0.5)

            # Format for frontend (anonymize user data)
            formatted_users = [
                {
                    'user_id': str(user['user'].id),
                    'username': user['user'].username[:3] + '***',  # Partial anonymization
                    'similarity': user['similarity'],
                    'common_learnings': user['common_learnings']
                }
                for user in similar_users[:10]  # Top 10 similar users
            ]

            await self.send(text_data=json.dumps({
                'type': 'similar_users',
                'users': formatted_users,
                'count': len(formatted_users)
            }))

            logger.info(f"📊 Sent {len(formatted_users)} similar users to {self.user.username}")

        except Exception as e:
            logger.error(f"Error sending similar users: {e}", exc_info=True)
            await self.send_error("Could not load similar users")

    @database_sync_to_async
    def get_learning_evolution_data(self, domain: str = None) -> Dict[str, Any]:
        """Get learning evolution over time for analytics"""
        try:
            from core.models import UserAgentLearning
            from django.db.models import Count
            from django.utils import timezone
            from datetime import timedelta

            # Get all learnings for this user
            learnings_query = UserAgentLearning.objects.filter(
                user=self.user,
                is_active=True
            )

            if domain:
                learnings_query = learnings_query.filter(learning_domain=domain)

            learnings = learnings_query.order_by('created_at')

            if not learnings.exists():
                return {'timeline': [], 'domain_coverage': {}}

            # Build timeline of confidence evolution
            timeline = []
            for learning in learnings:
                timeline.append({
                    'timestamp': learning.created_at.isoformat() if hasattr(learning, 'created_at') else None,
                    'domain': learning.learning_domain,
                    'confidence': learning.confidence_score,
                    'success_rate': learning.success_rate,
                    'validations': learning.validation_count
                })

            # Calculate domain coverage
            domain_coverage = {}
            all_domains = UserAgentLearning.objects.filter(
                user=self.user,
                is_active=True
            ).values('learning_domain').annotate(count=Count('id'))

            for domain_data in all_domains:
                domain_coverage[domain_data['learning_domain']] = domain_data['count']

            return {
                'timeline': timeline,
                'domain_coverage': domain_coverage,
                'total_domains': len(domain_coverage)
            }

        except Exception as e:
            logger.error(f"Error getting learning evolution: {e}")
            return {'timeline': [], 'domain_coverage': {}}

    async def send_learning_evolution(self, domain: str = None):
        """Send learning evolution analytics"""
        try:
            evolution_data = await self.get_learning_evolution_data(domain)

            await self.send(text_data=json.dumps({
                'type': 'learning_evolution',
                'data': evolution_data
            }))

            logger.info(f"📊 Sent learning evolution data to {self.user.username}")

        except Exception as e:
            logger.error(f"Error sending learning evolution: {e}", exc_info=True)
            await self.send_error("Could not load learning evolution")
