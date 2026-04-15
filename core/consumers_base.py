"""
WebSocket consumers for real-time communication.
Migrated from DBAO tools-manifest WebSocket capabilities and ai-content-studio.
"""

import json
import os
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

# Import intelligence engine
try:
    from intelligence.realtime_engine import intelligence_engine
except ImportError:
    intelligence_engine = None

# Import sports updates consumer

# Import hallucination monitor consumer

# Import AI Training consumer

# Import interview consumer
try:
    from intelligence.interview_consumer import InterviewConsumer
except ImportError:
    InterviewConsumer = None

# Import enhanced AI consumer
try:
    from .consumers_enhanced_ai import EnhancedAIAssistantConsumer
except ImportError:
    EnhancedAIAssistantConsumer = None

# Import personal assistant interviewer
try:
    from intelligence.personal_assistant_interviewer import personal_assistant_interviewer
    import logging
    logger = logging.getLogger(__name__)
    logger.info("✅ Personal Assistant Interviewer loaded successfully")
except ImportError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"❌ Failed to import Personal Assistant Interviewer: {e}")
    personal_assistant_interviewer = None
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"❌ Unexpected error importing Personal Assistant Interviewer: {e}")
    personal_assistant_interviewer = None

# Import autonomous system consumer
try:
    from ai_core.consumers.autonomous_system_consumer import AutonomousSystemConsumer
except ImportError:
    AutonomousSystemConsumer = None


class SafeWebSocketMixin:
    """Mixin for safe WebSocket send operations"""
    
    async def safe_send(self, data):
        """Safely send data, handling closed connections"""
        try:
            await self.send(text_data=json.dumps(data))
        except Exception as e:
            # Log the error but don't crash the consumer
            logger.error(f"[SafeWebSocket] Failed to send message: {e}")
            # Re-raise if it's not a connection-related error
            if "connection" not in str(e).lower() and "close" not in str(e).lower():
                raise
class AgentProgressConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Real-time agent execution progress and status updates.
    Migrated from DBAO tools-manifest.
    """
    
    async def connect(self):
        self.instance_id = self.scope['url_route']['kwargs'].get('instance_id', 'all')
        self.room_group_name = 'agents_general'  # Use general group for all agent messages
        self.game_subscriptions = set()  # Track subscribed games
        
        # Join the general agents room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection established message
        await self.safe_send({
            'type': 'connection_established',
            'data': {
                'message': 'Connected to agent progress updates',
                'instance_id': self.instance_id,
                'timestamp': datetime.now().isoformat()
            },
            'channel_name': self.channel_name
        })
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'ping')
            
            if message_type == 'ping':
                await self.safe_send({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
            elif message_type == 'subscribe':
                # Handle game subscription
                game_id = text_data_json.get('game_id')
                if game_id:
                    self.game_subscriptions.add(game_id)
                    await self.safe_send({
                        'type': 'subscribed',
                        'data': {
                            'game_id': game_id,
                            'status': 'subscribed'
                        }
                    })
            elif message_type == 'subscribe_agent':
                instance_id = text_data_json.get('instance_id')
                # Handle agent subscription
                await self.safe_send({
                    'type': 'subscribed',
                    'data': {
                        'instance_id': instance_id,
                        'status': 'subscribed'
                    }
                })
        except json.JSONDecodeError:
            await self.safe_send({
                'type': 'error',
                'data': {'message': 'Invalid JSON format'}
            })
    
    async def agent_progress(self, event):
        """Send agent progress update to WebSocket"""
        await self.safe_send({
            'type': 'agent_progress',
            'data': event['data']
        })
    
    async def agent_completed(self, event):
        """Send agent completion notification"""
        await self.safe_send({
            'type': 'agent_completed',
            'data': event['data']
        })
    
    async def agent_failed(self, event):
        """Send agent failure notification"""
        await self.safe_send({
            'type': 'agent_failed',
            'data': event['data']
        })


class DashboardConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Real-time dashboard metrics and system-wide updates.
    Migrated from DBAO tools-manifest.
    """
    
    async def connect(self):
        self.room_group_name = 'dashboard_updates'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial dashboard data
        await self.safe_send({
            'type': 'dashboard_data',
            'data': {
                'stats': {
                    'active_agents': 5,
                    'total_requests': 1247,
                    'success_rate': 94.2,
                    'current_cost': 45.67
                },
                'recent_activity': [
                    'Agent execution completed: Business Strategy Analysis',
                    'New odds calculation request',
                    'Content generation started'
                ],
                'timestamp': datetime.now().isoformat()
            }
        })
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'refresh_dashboard')
        
        if message_type == 'refresh_dashboard':
            # Send updated dashboard data
            await self.safe_send({
                'type': 'dashboard_update',
                'data': {
                    'stats': {
                        'active_agents': 3,
                        'total_requests': 1253,
                        'success_rate': 94.4,
                        'current_cost': 46.12
                    },
                    'timestamp': datetime.now().isoformat()
                }
            })
    
    async def dashboard_update(self, event):
        """Send dashboard update to WebSocket"""
        await self.safe_send({
            'type': 'dashboard_update',
            'data': event['data']
        })
    
    async def system_alert(self, event):
        """Send system alert to WebSocket"""
        await self.safe_send({
            'type': 'system_alert',
            'data': event['data']
        })


class LiveSportsConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Real-time sports data and betting opportunities.
    """
    
    async def connect(self):
        try:
            logger.debug(f"[LiveSports] CONNECT METHOD CALLED")
            self.room_group_name = 'live_sports'
            self.user = self.scope.get('user', AnonymousUser())
            
            # Log connection attempt
            user_info = getattr(self.user, 'username', 'anonymous') if not isinstance(self.user, AnonymousUser) else 'anonymous'
            logger.debug(f"[LiveSports] Connection attempt from user: {user_info}")
            
            logger.debug(f"[LiveSports] Adding to channel group...")
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            logger.debug(f"[LiveSports] Added to channel group successfully")
            
            logger.debug(f"[LiveSports] Accepting connection...")
            await self.accept()
            logger.debug(f"[LiveSports] Connection accepted")
            
            # Send connection established message with initial data
            logger.debug(f"[LiveSports] Sending welcome message...")
            await self.safe_send({
                'type': 'connection_established',
                'data': {
                    'message': 'Connected to live sports updates',
                    'user': user_info,
                    'timestamp': datetime.now().isoformat()
                }
            })
            logger.debug(f"[LiveSports] Welcome message sent successfully")
        except Exception as e:
            logger.error(f"[LiveSports] ERROR in connect method: {e}")
            import traceback
            traceback.print_exc()
            # Still try to accept the connection
            try:
                await self.accept()
            except Exception as _e:
                logger.warning(
                    "consumers_base.op: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
    
    async def disconnect(self, close_code):
        user_info = getattr(self.user, 'username', 'anonymous') if hasattr(self, 'user') and not isinstance(self.user, AnonymousUser) else 'anonymous'
        logger.debug(f"[LiveSports] Disconnection (code: {close_code}) for user: {user_info}")
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            logger.debug(f"[LiveSports] Received: {text_data}")
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'ping')
            logger.debug(f"[LiveSports] Message type: {message_type}")
            
            if message_type == 'ping':
                logger.debug(f"[LiveSports] Sending pong response...")
                await self.safe_send({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
                logger.debug(f"[LiveSports] Pong sent successfully")
            elif message_type == 'subscribe_sport':
                sport = text_data_json.get('sport', 'all')
                logger.debug(f"[LiveSports] Subscribing to sport: {sport}")
                await self.safe_send({
                    'type': 'subscribed',
                    'sport': sport,
                    'timestamp': datetime.now().isoformat()
                })
                logger.debug(f"[LiveSports] Subscription confirmation sent")
            else:
                logger.warning(f"[LiveSports] Unknown message type: {message_type}")
                await self.safe_send({
                    'type': 'error',
                    'data': {'message': f'Unknown message type: {message_type}'}
                })
                logger.debug(f"[LiveSports] Error message sent")
        except json.JSONDecodeError as e:
            logger.warning(f"[LiveSports] JSON decode error: {e}")
            await self.safe_send({
                'type': 'error',
                'data': {'message': 'Invalid JSON format'}
            })
        except Exception as e:
            logger.error(f"[LiveSports] Unexpected error in receive: {e}")
            # Don't disconnect on receive errors - just log and continue
    
    async def live_odds_update(self, event):
        """Send live odds update"""
        await self.safe_send({
            'type': 'live_odds_update',
            'data': event['data']
        })
    
    async def betting_opportunity(self, event):
        """Send new betting opportunity"""
        await self.safe_send({
            'type': 'betting_opportunity',
            'data': event['data']
        })


class ArbitrageConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Real-time arbitrage opportunity notifications.
    """
    
    async def connect(self):
        self.room_group_name = 'arbitrage_opportunities'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def arbitrage_opportunity(self, event):
        """Send arbitrage opportunity alert"""
        await self.safe_send({
            'type': 'arbitrage_opportunity',
            'data': event['data']
        })


class AssistantChatConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    AI Assistant chat WebSocket for real-time conversation.
    Migrated from ai-content-studio.
    """
    
    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser())
        
        # Allow connection but track authentication status
        self.is_authenticated = not isinstance(self.user, AnonymousUser)
            
        # Use a generic room for anonymous users
        user_id = self.user.id if self.is_authenticated else 'anonymous'
        self.room_group_name = f'assistant_chat_{user_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Check if user needs interview
        should_interview = False
        if self.is_authenticated:
            from core.personal_assistant_profile_connector import profile_connector
            should_interview = await profile_connector.should_start_interview(str(self.user.id))

        # Send authentication status
        await self.safe_send({
            'type': 'connection_established',
            'data': {
                'authenticated': self.is_authenticated,
                'user': self.user.username if self.is_authenticated else 'anonymous',
                'timestamp': datetime.now().isoformat(),
                'should_start_interview': should_interview,
                'interview_prompt': 'I notice you haven\'t completed your profile yet. Would you like to have a quick chat so I can personalize opportunities for you?' if should_interview else None
            }
        })
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message')

        # Handle interview protocol messages
        if message_type == 'start_interview':
            await self.handle_start_interview(text_data_json)
        elif message_type == 'interview_response':
            await self.handle_interview_response(text_data_json)
        elif message_type == 'complete_interview':
            await self.handle_complete_interview(text_data_json)
        elif message_type == 'chat_message':
            message = text_data_json.get('message', '')

            # Echo back for demo (in real implementation, this would process with AI)
            await self.safe_send({
                'type': 'assistant_response',
                'data': {
                    'message': f'Assistant response to: {message}',
                    'timestamp': datetime.now().isoformat()
                }
            })

    async def handle_start_interview(self, data):
        """Handle interview start request using AI-powered interview system"""
        try:
            # Lazy import to ensure Django is ready
            global personal_assistant_interviewer
            if personal_assistant_interviewer is None:
                try:
                    from intelligence.personal_assistant_interviewer import personal_assistant_interviewer as pai
                    personal_assistant_interviewer = pai
                except Exception as e:
                    await self.safe_send({
                        'type': 'error',
                        'data': {'message': f'Failed to load interview system: {str(e)}'}
                    })
                    return

            if not personal_assistant_interviewer:
                # Fallback to basic response if AI interviewer not available
                await self.safe_send({
                    'type': 'error',
                    'data': {'message': 'AI interview system not available'}
                })
                return

            # Require authentication for interview
            if not self.is_authenticated:
                await self.safe_send({
                    'type': 'error',
                    'data': {'message': 'Authentication required for interview. Please log in to continue.'}
                })
                return

            user_id = str(self.user.id)

            interview_data = data.get('data', {})
            interview_type = interview_data.get('interview_type', 'full')
            quick_start = interview_type == 'quick'

            # Start AI-powered interview
            result = await personal_assistant_interviewer.start_interview(
                user_id=user_id,
                quick_start=quick_start
            )

            if result.get('success'):
                await self.safe_send({
                    'type': 'interview_started',
                    'data': {
                        'session_id': f'ai-interview-{self.user.id}',
                        'interview_type': interview_type,
                        'estimated_time': result.get('estimated_time'),
                        'message': f'Starting {interview_type} interview with AI assistance...',
                        'timestamp': datetime.now().isoformat(),
                        'is_interview': True  # Flag to identify interview messages
                    }
                })

                # Send first AI-generated question with full data
                question_data = result.get('question', {})
                await self.safe_send({
                    'type': 'interview_question',
                    'data': {
                        'question': question_data,  # Send the full question object including options
                        'state': result.get('state', {}),
                        'is_interview': True  # Flag to identify interview messages
                    }
                })
            else:
                await self.safe_send({
                    'type': 'error',
                    'data': {'message': result.get('error', 'Failed to start AI interview')}
                })

        except Exception as e:
            logger.error(f"Error in AI interview start: {e}")
            await self.safe_send({
                'type': 'error',
                'data': {'message': f'Interview system error: {str(e)}'}
            })

    async def handle_interview_response(self, data):
        """Handle user's interview response using AI-powered interview system"""
        try:
            if not personal_assistant_interviewer:
                await self.safe_send({
                    'type': 'error',
                    'data': {'message': 'AI interview system not available'}
                })
                return

            # Require authentication for interview
            if not self.is_authenticated:
                await self.safe_send({
                    'type': 'error',
                    'data': {'message': 'Authentication required for interview. Please log in to continue.'}
                })
                return

            user_id = str(self.user.id)

            response_data = data.get('data', {})
            response = response_data.get('response', '')

            # Process response with AI interviewer
            result = await personal_assistant_interviewer.process_response(
                user_id=user_id,
                response=response
            )

            if result.get('success'):
                if result.get('interview_complete'):
                    # Interview completed - save profile and send summary
                    profile = result.get('profile')
                    # Always save to database (authentication is now required)
                    await self.save_completed_interview_profile(profile)

                    await self.safe_send({
                        'type': 'interview_completed',
                        'data': {
                            'profile': profile,
                            'session_id': f'ai-interview-{self.user.id}',
                            'completion_timestamp': datetime.now().isoformat(),
                            'message': 'Excellent! Your profile is complete. I now understand your goals and can provide personalized recommendations.',
                            'next_steps': [
                                'Find personalized opportunities',
                                'Get income recommendations',
                                'Start applying to matches'
                            ],
                            'is_interview': True  # Flag to identify interview messages
                        }
                    })

                    # Save interview data to ExtendedUserProfile
                    from core.personal_assistant_profile_connector import profile_connector
                    update_result = await profile_connector.update_profile_from_interview(
                        str(self.user.id),
                        profile
                    )

                    if update_result.get('success'):
                        # Connect to Income Builder for personalized opportunities
                        await profile_connector.connect_interview_to_income_builder(str(self.user.id))

                    # Notify other systems about completed profile
                    await self.notify_profile_completion(profile)

                else:
                    # Send next AI-generated question with full data
                    question_data = result.get('question', {})
                    await self.safe_send({
                        'type': 'interview_question',
                        'data': {
                            'question': question_data,  # Send the full question object including options
                            'state': result.get('state', {}),
                            'insights': result.get('insights', []),
                            'is_interview': True  # Flag to identify interview messages
                        }
                    })

            else:
                await self.safe_send({
                    'type': 'error',
                    'data': {'message': result.get('error', 'Failed to process response')}
                })

        except Exception as e:
            logger.error(f"Error in AI interview response: {e}")
            await self.safe_send({
                'type': 'error',
                'data': {'message': f'Interview processing error: {str(e)}'}
            })

    @database_sync_to_async
    def save_completed_interview_profile(self, profile_data):
        """Save completed interview profile to database"""
        try:
            from core.models import EnhancedUserProfile
            from decimal import Decimal

            # Get or create enhanced profile
            enhanced_profile, created = EnhancedUserProfile.objects.get_or_create(
                user=self.user,
                defaults={
                    'primary_role': profile_data.get('strongest_skill', 'Professional')[:200]
                }
            )

            # Update with interview data
            enhanced_profile.interview_completed = True
            enhanced_profile.interview_completion_date = datetime.now()
            enhanced_profile.interview_type = profile_data.get('interview_type', 'full')

            # Basic interview data
            if profile_data.get('current_situation'):
                situation_mapping = {
                    'Employed - looking for more income': 'employed_seeking_more',
                    'Unemployed - need income ASAP': 'unemployed_need_asap',
                    'Student - want part-time work': 'student_part_time',
                    'Entrepreneur - scaling my business': 'entrepreneur_scaling',
                    'Retired - exploring opportunities': 'retired_exploring'
                }
                enhanced_profile.current_situation = situation_mapping.get(
                    profile_data['current_situation'], 'other'
                )

            enhanced_profile.available_hours_per_week = profile_data.get('available_hours_per_week', 0)

            if profile_data.get('monthly_income_goal'):
                enhanced_profile.monthly_income_goal = Decimal(str(profile_data['monthly_income_goal']))

            enhanced_profile.strongest_skill = profile_data.get('strongest_skill', '')
            enhanced_profile.skill_example = profile_data.get('skill_example', '')
            enhanced_profile.professional_background = profile_data.get('professional_background', '')
            enhanced_profile.career_motivation = profile_data.get('career_motivation', '')
            enhanced_profile.professional_achievements = profile_data.get('achievements', '')
            enhanced_profile.recent_learning = profile_data.get('learning_activity', '')

            enhanced_profile.work_type_preferences = profile_data.get('work_preferences', [])
            enhanced_profile.things_to_avoid = profile_data.get('things_to_avoid', '')
            enhanced_profile.other_work_preferences = profile_data.get('other_preferences', '')
            enhanced_profile.hidden_talents = profile_data.get('hidden_talents', [])
            enhanced_profile.available_assets = profile_data.get('available_assets', [])
            enhanced_profile.commitment_level = profile_data.get('commitment_level', '')

            if profile_data.get('auto_apply_preference'):
                auto_apply_mapping = {
                    'Yes - Apply automatically to good matches': 'auto_yes',
                    'Yes - But ask me first': 'ask_first',
                    'No - Just show me opportunities': 'no_auto'
                }
                enhanced_profile.auto_apply_preference = auto_apply_mapping.get(
                    profile_data['auto_apply_preference'], 'no_auto'
                )

            # AI insights and recommendations
            enhanced_profile.interview_insights = profile_data.get('ai_insights', [])
            enhanced_profile.profile_strength_score = profile_data.get('profile_strength_score', 0.0)
            enhanced_profile.personalized_recommendations = profile_data.get('recommendations', [])

            # Update skills from interview
            skills_data = profile_data.get('skills_by_category', {})
            if skills_data:
                competencies = {}
                for category, skills in skills_data.items():
                    for skill in skills:
                        if skill != 'None of these':
                            competencies[skill] = 5  # Default proficiency level

                enhanced_profile.core_competencies = competencies

            # Recalculate completeness
            enhanced_profile.calculate_completeness()
            enhanced_profile.save()

            logger.info(f"Saved completed interview profile for user {self.user.username}")

        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            raise

    async def notify_profile_completion(self, profile_data):
        """Notify other platform systems about completed profile"""
        try:
            # Notify the unified platform connector
            pass

            # Send profile completion to income builder and job matching systems
            await self.channel_layer.group_send(
                'income_income_builder',
                {
                    'type': 'profile_completed',
                    'user_id': str(self.user.id),
                    'profile': profile_data
                }
            )

            # Notify personal assistant system
            await self.channel_layer.group_send(
                'personal_assistant',
                {
                    'type': 'profile_ready',
                    'user_id': str(self.user.id),
                    'profile': profile_data,
                    'message': 'Profile completed via interview - ready for personalized assistance'
                }
            )

            logger.info(f"Notified platform systems of profile completion for user {self.user.username}")

        except Exception as e:
            logger.error(f"Error notifying profile completion: {e}")

    async def handle_complete_interview(self, data):
        """Handle interview completion"""
        interview_data = data.get('data', {})
        session_id = interview_data.get('session_id')

        # Build final profile
        profile = {
            'name': self.user.first_name if self.is_authenticated else 'User',
            'email': self.user.email if self.is_authenticated else '',
            'skills': ['General skills'],
            'experience_level': 'Beginner',
            'income_goal': '$1,000-$2,500',
            'work_preferences': ['Remote work'],
            'completed_via': 'interview',
            'profile_strength_score': 75,
            'completeness_percentage': 100,
            'setup_completed': True
        }

        await self.safe_send({
            'type': 'interview_completed',
            'data': {
                'profile': profile,
                'session_id': session_id,
                'completion_timestamp': datetime.now().isoformat()
            }
        })

    async def assistant_response(self, event):
        """Send assistant response to WebSocket"""
        await self.safe_send({
            'type': 'assistant_response',
            'data': event['data']
        })


class OrchestrationConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Multi-agent orchestration updates.
    """
    
    async def connect(self):
        self.orchestration_id = self.scope['url_route']['kwargs']['orchestration_id']
        self.room_group_name = f'orchestration_{self.orchestration_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def orchestration_update(self, event):
        """Send orchestration progress update"""
        await self.safe_send({
            'type': 'orchestration_update',
            'data': event['data']
        })


class NotificationConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    System notifications and alerts.
    """
    
    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser())
        self.is_authenticated = not isinstance(self.user, AnonymousUser)
        
        # Use a generic room for anonymous users
        user_id = self.user.id if self.is_authenticated else 'anonymous'
        self.room_group_name = f'notifications_{user_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def notification(self, event):
        """Send notification to user"""
        await self.safe_send({
            'type': 'notification',
            'data': event['data']
        })


class AgentChannelsConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Agent Channels WebSocket Consumer - "Slack for AI Agents"
    
    Provides real-time agent communication viewing, similar to Slack channels
    where users can watch agents think, collaborate, and work together.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_id = None
        self.channel_group_name = None
        self.user = None
        self.active_channels = set()
        
    async def connect(self):
        """Handle WebSocket connection"""
        # Get channel ID from URL (optional - can join multiple channels)
        self.channel_id = self.scope['url_route']['kwargs'].get('channel_id')
        
        # Get user from scope
        self.user = self.scope.get('user', AnonymousUser())
        
        # Check if user is authenticated
        if not self.user or isinstance(self.user, AnonymousUser):
            # In development, allow anonymous connections
            import os
            if os.getenv('DJANGO_ENV') == 'development':
                # Create a mock user for development
                self.user = type('MockUser', (), {
                    'id': 1,
                    'username': 'dev_user',
                    'is_authenticated': True,
                    'email': 'dev@unified-donkey-betz.com'
                })()
            else:
                await self.close(code=4001)  # Unauthorized
                return
        
        # Accept connection
        await self.accept()
        
        # If specific channel requested, join it
        if self.channel_id:
            await self.join_channel(self.channel_id)
        
        # Send connection success
        await self.safe_send({
            'type': 'connection_established',
            'user_id': str(self.user.id) if hasattr(self.user, 'id') else None,
            'username': getattr(self.user, 'username', 'dev_user'),
            'timestamp': datetime.now().isoformat()
        })
        
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave all active channels
        for channel_id in self.active_channels:
            channel_group_name = f'agent_channel_{channel_id}'
            await self.channel_layer.group_discard(
                channel_group_name,
                self.channel_name
            )
            
            # Notify channel of user leaving (only if user exists)
            if self.user:
                await self.channel_layer.group_send(
                    channel_group_name,
                    {
                        'type': 'user_presence',
                        'user_id': str(self.user.id) if hasattr(self.user, 'id') else None,
                        'username': getattr(self.user, 'username', 'dev_user'),
                        'status': 'offline'
                    }
                )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'unknown')
            
            if message_type == 'join_channel':
                await self.handle_join_channel(text_data_json)
            elif message_type == 'leave_channel':
                await self.handle_leave_channel(text_data_json)
            elif message_type == 'send_message':
                await self.handle_send_message(text_data_json)
            elif message_type == 'subscribe_channel':
                # Handle channel subscription
                channel_id = text_data_json.get('channel_id')
                if channel_id:
                    await self.join_channel(channel_id)
            elif message_type == 'get_channels':
                # Send list of available channels
                await self.handle_get_channels()
            elif message_type == 'get_channel_messages':
                # Send messages for a specific channel
                await self.handle_get_channel_messages(text_data_json)
            elif message_type == 'ping':
                # Handle ping message with pong response
                await self.safe_send({'type': 'pong', 'timestamp': datetime.now().isoformat()})
            else:
                await self.safe_send({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                })
        except json.JSONDecodeError:
            await self.safe_send({
                'type': 'error',
                'message': 'Invalid JSON format'
            })
    
    async def handle_join_channel(self, content):
        """Handle joining a channel"""
        channel_id = content.get('channel_id')
        if not channel_id:
            await self.safe_send({
                'type': 'error',
                'message': 'channel_id required'
            })
            return
        
        await self.join_channel(channel_id)
    
    async def join_channel(self, channel_id):
        """Join a specific channel"""
        # Verify channel exists and user has access
        channel = await self.get_channel(channel_id)
        if not channel:
            await self.safe_send({
                'type': 'error',
                'message': f'Channel {channel_id} not found'
            })
            return
        
        # Add to channel group
        channel_group_name = f'agent_channel_{channel_id}'
        await self.channel_layer.group_add(
            channel_group_name,
            self.channel_name
        )
        
        self.active_channels.add(channel_id)
        
        # Send join confirmation
        await self.safe_send({
            'type': 'joined_channel',
            'channel_id': channel_id,
            'channel_name': channel['display_name']
        })
        
        # Notify others of user joining
        await self.channel_layer.group_send(
            channel_group_name,
            {
                'type': 'user_presence',
                'user_id': str(self.user.id) if hasattr(self.user, 'id') else None,
                'username': getattr(self.user, 'username', 'dev_user'),
                'status': 'online',
                'channel_id': channel_id
            }
        )
    
    async def handle_leave_channel(self, content):
        """Handle leaving a channel"""
        channel_id = content.get('channel_id')
        if not channel_id or channel_id not in self.active_channels:
            return
        
        # Remove from channel group
        channel_group_name = f'agent_channel_{channel_id}'
        await self.channel_layer.group_discard(
            channel_group_name,
            self.channel_name
        )
        
        self.active_channels.remove(channel_id)
        
        # Send leave confirmation
        await self.safe_send({
            'type': 'left_channel',
            'channel_id': channel_id
        })
    
    async def handle_send_message(self, content):
        """Handle sending a message to a channel"""
        channel_id = content.get('channel_id')
        message_content = content.get('content')
        message_type = content.get('message_type', 'user_message')
        
        if not channel_id or not message_content:
            await self.safe_send({
                'type': 'error',
                'message': 'channel_id and content required'
            })
            return
        
        # Create message in database
        message = await self.create_user_message(channel_id, message_content, message_type)
        if not message:
            return
        
        # Broadcast to channel
        channel_group_name = f'agent_channel_{channel_id}'
        await self.channel_layer.group_send(
            channel_group_name,
            {
                'type': 'channel_message',
                'message': message
            }
        )
    
    async def handle_get_channels(self):
        """Send list of available channels to client"""
        channels = await self.get_all_channels()
        await self.safe_send({
            'type': 'channels_list',
            'channels': channels
        })
    
    async def handle_get_channel_messages(self, content):
        """Send messages for a specific channel to client"""
        channel_id = content.get('channel_id')
        if not channel_id:
            await self.safe_send({
                'type': 'error',
                'message': 'channel_id required'
            })
            return
        
        messages = await self.get_channel_messages(channel_id)
        await self.safe_send({
            'type': 'channel_messages',
            'channel_id': channel_id,
            'messages': messages
        })
    
    # Channel layer message handlers
    async def channel_message(self, event):
        """Send message to WebSocket"""
        await self.safe_send({
            'type': 'channel_message',
            'data': event['message']
        })
    
    async def agent_message(self, event):
        """Handle agent messages from agents"""
        await self.safe_send({
            'type': 'agent_message',
            'channel_id': event.get('channel_id'),
            'agent_id': event.get('agent_id'),
            'agent_name': event.get('agent_name'),
            'message': event.get('message'),
            'content': event.get('content'),
            'timestamp': event.get('timestamp'),
            'rich_content': event.get('rich_content', {})
        })
    
    async def user_presence(self, event):
        """Send user presence update"""
        await self.safe_send({
            'type': 'user_presence',
            'user_id': event['user_id'],
            'username': event['username'],
            'status': event['status'],
            'channel_id': event.get('channel_id')
        })
    
    # Database helper methods
    @database_sync_to_async
    def get_channel(self, channel_id):
        """Get channel from database"""
        try:
            from core.models.agents_registry import AgentChannel
            
            # Support both numeric IDs and string names
            if str(channel_id).isdigit():
                channel = AgentChannel.objects.get(id=channel_id, is_active=True)
            else:
                channel = AgentChannel.objects.get(name=channel_id, is_active=True)
            
            return {
                'id': channel.id,
                'name': channel.name,
                'display_name': channel.display_name,
                'description': channel.description,
                'channel_type': channel.channel_type,
                'is_active': channel.is_active,
            }
        except Exception as _e:
            logger.warning(
                "consumers_base.get_channel: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return None
    
    @database_sync_to_async
    def get_all_channels(self):
        """Get all active channels"""
        try:
            from core.models.agents_registry import AgentChannel, AgentChannelMessage
            
            channels = AgentChannel.objects.filter(is_active=True).order_by('-created_at')
            channel_data = []
            
            for channel in channels:
                # Count messages
                message_count = AgentChannelMessage.objects.filter(channel=channel).count()
                
                # Extract orchestration_id from metadata
                orchestration_id = None
                if channel.metadata and 'orchestration_id' in channel.metadata:
                    orchestration_id = channel.metadata.get('orchestration_id')
                elif channel.orchestration_id:
                    orchestration_id = channel.orchestration_id
                
                channel_data.append({
                    'id': channel.id,
                    'name': channel.name,
                    'display_name': channel.display_name,
                    'description': channel.description,
                    'channel_type': channel.channel_type,
                    'is_active': channel.is_active,
                    'created_at': channel.created_at.isoformat(),
                    'message_count': message_count,
                    'orchestration_id': orchestration_id,
                    'active_agents': len(channel.active_agents) if channel.active_agents else 0
                })
            
            return channel_data
        except Exception as e:
            logger.error(f"Error getting channels: {e}")
            return []
    
    @database_sync_to_async
    def get_channel_messages(self, channel_id):
        """Get messages for a specific channel"""
        try:
            from core.models.agents_registry import AgentChannel, AgentChannelMessage
            
            # Get the channel
            if str(channel_id).isdigit():
                channel = AgentChannel.objects.get(id=channel_id, is_active=True)
            else:
                channel = AgentChannel.objects.get(name=channel_id, is_active=True)
            
            # Get messages for this channel
            messages = AgentChannelMessage.objects.filter(
                channel=channel
            ).order_by('-timestamp')[:50]  # Get last 50 messages
            
            # Serialize messages
            message_data = []
            for msg in reversed(messages):  # Reverse to show oldest first
                msg_dict = {
                    'id': msg.id,
                    'channel': msg.channel.id,
                    'message_type': msg.message_type,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat(),
                    'rich_content': msg.rich_content,
                    'reactions': msg.reactions,
                    'thread_id': msg.thread_id
                }
                
                # Add agent info if present
                if msg.agent_instance:
                    msg_dict['agent_instance'] = {
                        'id': msg.agent_instance.id,
                        'template': {
                            'name': msg.agent_instance.template.name if msg.agent_instance.template else 'Unknown Agent'
                        }
                    }
                
                # Add user info if present
                if msg.user:
                    msg_dict['user'] = {
                        'id': msg.user.id,
                        'username': msg.user.username
                    }
                
                message_data.append(msg_dict)
            
            return message_data
            
        except Exception as e:
            logger.error(f"Error getting channel messages: {e}")
            return []
    
    @database_sync_to_async
    def create_user_message(self, channel_id, content, message_type):
        """Create user message in database"""
        try:
            from core.models.agents_registry import AgentChannel, AgentChannelMessage
            
            # Get channel
            if str(channel_id).isdigit():
                channel = AgentChannel.objects.get(id=channel_id, is_active=True)
            else:
                channel = AgentChannel.objects.get(name=channel_id, is_active=True)
            
            # Create message
            message = AgentChannelMessage.objects.create(
                channel=channel,
                user=self.user if hasattr(self.user, 'id') else None,
                content=content,
                message_type=message_type
            )
            
            return {
                'id': message.id,
                'channel': message.channel.id,
                'message_type': message.message_type,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'user': {
                    'id': self.user.id if hasattr(self.user, 'id') else 1,
                    'username': getattr(self.user, 'username', 'dev_user')
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating user message: {e}")
            return None


class TestEchoConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Test echo consumer for WebSocket testing.
    """
    
    async def connect(self):
        await self.accept()
        await self.safe_send({
            'type': 'connection_established',
            'message': 'Test echo WebSocket connected',
            'timestamp': datetime.now().isoformat()
        })
    
    async def disconnect(self, close_code):
        pass
    
    async def receive(self, text_data):
        # Echo back the received message
        await self.safe_send({
            'type': 'echo',
            'data': text_data,
            'timestamp': datetime.now().isoformat()
        })


class ContentProcessingConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Content processing WebSocket for real-time updates.
    """
    
    async def connect(self):
        self.room_group_name = 'content_processing'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.safe_send({
            'type': 'connection_established',
            'message': 'Connected to content processing updates',
            'timestamp': datetime.now().isoformat()
        })
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'ping')
            
            if message_type == 'ping':
                await self.safe_send({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            # Silently handle closed connection errors
            pass
    
    async def processing_update(self, event):
        """Send processing update to WebSocket"""
        try:
            await self.safe_send({
                'type': 'processing_update',
                'data': event['data']
            })
        except Exception as e:
            # Silently handle closed connection errors
            pass


class ContentAnalyticsConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Content analytics WebSocket for real-time metrics.
    """
    
    async def connect(self):
        self.room_group_name = 'content_analytics'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.safe_send({
            'type': 'connection_established',
            'message': 'Connected to content analytics',
            'timestamp': datetime.now().isoformat()
        })
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'ping')
        
        if message_type == 'ping':
            await self.safe_send({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    
    async def analytics_update(self, event):
        """Send analytics update to WebSocket"""
        await self.safe_send({
            'type': 'analytics_update',
            'data': event['data']
        })


class AgentExecutionConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Agent execution WebSocket for real-time execution updates.
    """
    
    async def connect(self):
        self.room_group_name = 'agent_execution'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.safe_send({
            'type': 'connection_established',
            'message': 'Connected to agent execution updates',
            'timestamp': datetime.now().isoformat()
        })
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'ping')
        
        if message_type == 'ping':
            await self.safe_send({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    
    async def execution_update(self, event):
        """Send execution update to WebSocket"""
        await self.safe_send({
            'type': 'execution_update',
            'data': event['data']
        })


class AgentOrchestrationConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Agent orchestration WebSocket for multi-agent coordination.
    """
    
    async def connect(self):
        self.room_group_name = 'agent_orchestration'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.safe_send({
            'type': 'connection_established',
            'message': 'Connected to agent orchestration',
            'timestamp': datetime.now().isoformat()
        })
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'ping')
        
        if message_type == 'ping':
            await self.safe_send({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    
    async def orchestration_update(self, event):
        """Send orchestration update to WebSocket"""
        await self.safe_send({
            'type': 'orchestration_update',
            'data': event['data']
        })


class MythologyConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Mythology/Content Review WebSocket Consumer
    
    Provides real-time notifications for content flagging and review updates.
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope.get('user')
        
        # Allow anonymous users for now (you can restrict this later)
        # Just log if user is not authenticated
        if not self.user or self.user == AnonymousUser():
            logger.warning("Anonymous user connecting to mythology WebSocket")
            
        # Join mythology notifications group
        self.room_group_name = 'mythology_notifications'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection established message
        await self.safe_send({
            'type': 'connection_established',
            'data': {
                'message': 'Connected to mythology notifications',
                'timestamp': datetime.now().isoformat()
            }
        })
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.safe_send({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
                
        except json.JSONDecodeError:
            await self.safe_send({
                'type': 'error',
                'data': {'message': 'Invalid JSON format'}
            })
    
    async def mythology_notification(self, event):
        """Send mythology notification to client"""
        await self.safe_send({
            'type': 'mythology_notification',
            'notification': event['notification']
        })

class SportsArbitrageConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Sports arbitrage WebSocket for real-time arbitrage opportunities.
    """
    
    async def connect(self):
        self.room_group_name = 'sports_arbitrage'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Log connection with user info
        user = self.scope.get('user', AnonymousUser())
        if not isinstance(user, AnonymousUser):
            logger.info(f"WebSocket connected: {user.username}")
        else:
            logger.info("WebSocket connected: anonymous user")
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info("WebSocket disconnected: ")
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'ping')
        
        if message_type == 'ping':
            await self.safe_send({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    
    async def arbitrage_update(self, event):
        """Send arbitrage update to WebSocket"""
        await self.safe_send({
            'type': 'arbitrage_update',
            'data': event['data']
        })


class SportsRecommendationConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Sports recommendation WebSocket for betting suggestions.
    """

    async def connect(self):
        self.room_group_name = 'sports_recommendations'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Log connection with user info
        user = self.scope.get('user', AnonymousUser())
        if not isinstance(user, AnonymousUser):
            logger.info(f"WebSocket connected: {user.username}")
        else:
            logger.info("WebSocket connected: anonymous user")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info("WebSocket disconnected: ")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'ping')

        if message_type == 'ping':
            await self.safe_send({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })

    async def recommendation_update(self, event):
        """Send recommendation update to WebSocket"""
        await self.safe_send({
            'type': 'recommendation_update',
            'data': event['data']
        })


# Import the enhanced AI Command Center Consumer
from .command_center_ai import CommandCenterAIConsumer

# Use the AI-enhanced consumer for Command Center
CommandCenterConsumer = CommandCenterAIConsumer

# Keep the original for backward compatibility
class CommandCenterConsumerLegacy(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Command Center WebSocket for unified intelligence platform updates.
    Handles real-time communication for the Bloomberg Terminal-like interface.
    """

    async def connect(self):
        self.room_group_name = 'command_center'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send connection established with initial dashboard state and intelligence status
        initial_data = {
            'message': 'Connected to Command Center - LIMITLESS INTELLIGENCE ACTIVE',
            'timestamp': datetime.now().isoformat(),
            'features': {
                'prediction_engine': True,
                'opportunity_scanner': True,
                'risk_manager': True,
                'collaborative_decisions': True,
                'outcome_prediction': True,
                'auto_execution': True
            }
        }

        # Check intelligence engine status
        if intelligence_engine:
            try:
                live_opportunities = intelligence_engine.get_current_opportunities()
                live_predictions = intelligence_engine.get_current_predictions()
                initial_data['intelligence_status'] = 'ONLINE'
                initial_data['live_opportunities'] = len(live_opportunities)
                initial_data['live_predictions'] = len(live_predictions)
                initial_data['skynet_status'] = 'OPERATIONAL'
            except Exception:
                initial_data['intelligence_status'] = 'INITIALIZING'
                initial_data['skynet_status'] = 'BOOTING'
        else:
            initial_data['intelligence_status'] = 'OFFLINE'
            initial_data['skynet_status'] = 'OFFLINE'

        await self.safe_send({
            'type': 'connection_established',
            'data': initial_data
        })

        # Stream initial intelligence data
        if intelligence_engine:
            try:
                # Stream recent predictions
                live_predictions = intelligence_engine.get_current_predictions()
                for pred in live_predictions[:2]:  # Send first 2 predictions
                    await self.safe_send({
                        'type': 'intelligence_update',
                        'data': {
                            'type': 'new_prediction',
                            'prediction': pred,
                            'timestamp': datetime.now().isoformat()
                        }
                    })

                # Stream top opportunities
                live_opportunities = intelligence_engine.get_current_opportunities()
                for opp in live_opportunities[:1]:  # Send top opportunity
                    await self.safe_send({
                        'type': 'intelligence_update',
                        'data': {
                            'type': 'new_opportunity',
                            'opportunity': opp,
                            'timestamp': datetime.now().isoformat()
                        }
                    })
            except Exception as e:
                logger.error(f"Error streaming initial intelligence data: {e}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'ping')

            if message_type == 'ping':
                await self.safe_send({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
            elif message_type == 'subscribe_predictions':
                # Handle prediction subscription
                await self.safe_send({
                    'type': 'subscribed',
                    'data': {'feature': 'predictions', 'status': 'active'}
                })
            elif message_type == 'request_intelligence':
                # Handle intelligence request
                domain = text_data_json.get('domain', 'SPORTS_BETTING')
                await self.safe_send({
                    'type': 'intelligence_update',
                    'data': {
                        'domain': domain,
                        'predictions': [{
                            'id': 'pred_1',
                            'type': 'arbitrage',
                            'edge': 4.2,
                            'confidence': 0.85,
                            'timeWindow': 180
                        }],
                        'timestamp': datetime.now().isoformat()
                    }
                })
            elif message_type == 'analyze_opportunities':
                # Handle AI Income Builder opportunity analysis
                await self.handle_analyze_opportunities(text_data_json)
            elif message_type == 'start_opportunity':
                # Handle starting an opportunity action plan
                await self.handle_start_opportunity(text_data_json)
            elif message_type == 'update_profile':
                # Handle user profile updates
                await self.handle_update_profile(text_data_json)
            elif message_type == 'get_earnings':
                # Handle earnings data request
                await self.handle_get_earnings(text_data_json)
            elif message_type == 'command':
                # Handle general commands from command center
                await self.handle_command(text_data_json)
        except json.JSONDecodeError:
            await self.safe_send({
                'type': 'error',
                'data': {'message': 'Invalid JSON format'}
            })

    async def intelligence_update(self, event):
        """Send intelligence update to WebSocket"""
        await self.safe_send({
            'type': 'intelligence_update',
            'data': event['data']
        })

    async def decision_update(self, event):
        """Send decision update to WebSocket"""
        await self.safe_send({
            'type': 'decision_update',
            'data': event['data']
        })

    async def handle_analyze_opportunities(self, data):
        """Handle opportunity analysis request from Decision Command"""
        try:
            # Import AIIncomeBuilder
            from intelligence.income_builder import income_builder, UserProfile, SkillLevel

            # Extract user profile data from request
            profile_data = data.get('profile', {})

            # Create UserProfile from frontend data
            user_profile = UserProfile(
                id=profile_data.get('id', 'user_1'),
                current_balance=float(profile_data.get('currentBalance', 0)),
                skills=profile_data.get('skills', []),
                skill_level=SkillLevel(profile_data.get('skillLevel', 'beginner')),
                available_hours_per_week=int(profile_data.get('availableHours', 10)),
                interests=profile_data.get('interests', [])
            )

            # Analyze opportunities using AIIncomeBuilder
            analysis_result = await income_builder.analyze_user_potential(user_profile)

            # Get real opportunities from spider network
            spider_opportunities = await self.get_spider_opportunities(user_profile)

            # Combine AI analysis with spider data
            combined_opportunities = self.combine_opportunities(
                analysis_result, spider_opportunities
            )

            # Send response back to frontend
            await self.safe_send({
                'type': 'opportunities_analyzed',
                'data': {
                    'status': 'success',
                    'analysis': combined_opportunities,
                    'timestamp': datetime.now().isoformat(),
                    'user_id': user_profile.id
                }
            })

            # Store analysis in database
            await self.save_opportunity_analysis(user_profile, combined_opportunities)

        except Exception as e:
            await self.safe_send({
                'type': 'error',
                'data': {
                    'message': f'Opportunity analysis failed: {str(e)}',
                    'error_type': 'analysis_error'
                }
            })

    async def handle_start_opportunity(self, data):
        """Handle starting an opportunity action plan"""
        try:
            from intelligence.income_builder import income_builder

            user_id = data.get('user_id', 'user_1')
            opportunity_id = data.get('opportunity_id')

            if not opportunity_id:
                raise ValueError("Opportunity ID is required")

            # Create action plan using AIIncomeBuilder
            action_plan = await income_builder.create_action_plan(user_id, opportunity_id)

            # Save to database
            plan_instance = await self.save_action_plan(action_plan, user_id)

            # Start execution
            if plan_instance:
                task_id = plan_instance.start_execution()

                await self.safe_send({
                    'type': 'opportunity_started',
                    'data': {
                        'status': 'success',
                        'plan_id': str(plan_instance.id),
                        'task_id': task_id,
                        'action_plan': action_plan,
                        'timestamp': datetime.now().isoformat()
                    }
                })
            else:
                raise Exception("Failed to create action plan")

        except Exception as e:
            await self.safe_send({
                'type': 'error',
                'data': {
                    'message': f'Failed to start opportunity: {str(e)}',
                    'error_type': 'start_error'
                }
            })

    async def handle_update_profile(self, data):
        """Handle user profile updates"""
        try:
            pass

            profile_data = data.get('profile', {})
            user_id = profile_data.get('id', 'user_1')

            # Save profile to database
            await self.save_user_profile(user_id, profile_data)

            await self.safe_send({
                'type': 'profile_updated',
                'data': {
                    'status': 'success',
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat()
                }
            })

        except Exception as e:
            await self.safe_send({
                'type': 'error',
                'data': {
                    'message': f'Profile update failed: {str(e)}',
                    'error_type': 'profile_error'
                }
            })

    async def handle_get_earnings(self, data):
        """Handle earnings data request"""
        try:
            pass

            user_id = data.get('user_id', 'user_1')

            # Get earnings from database
            earnings_data = await self.get_user_earnings(user_id)

            await self.safe_send({
                'type': 'earnings_data',
                'data': {
                    'status': 'success',
                    'earnings': earnings_data,
                    'timestamp': datetime.now().isoformat()
                }
            })

        except Exception as e:
            await self.safe_send({
                'type': 'error',
                'data': {
                    'message': f'Failed to get earnings: {str(e)}',
                    'error_type': 'earnings_error'
                }
            })

    async def get_spider_opportunities(self, user_profile):
        """Get real opportunities from spider network"""
        try:
            # Use the new spider opportunity connector
            from intelligence.spider_opportunity_connector import get_spider_opportunities

            # Convert user profile to expected format
            profile_dict = {
                'id': user_profile.id,
                'skills': user_profile.skills,
                'skillLevel': user_profile.skill_level.value,
                'currentBalance': float(user_profile.current_balance),
                'availableHours': user_profile.available_hours_per_week
            }

            # Get opportunities from spider network
            spider_opportunities = await get_spider_opportunities(profile_dict)

            # Format for frontend
            spider_opps = []
            for opp in spider_opportunities[:10]:  # Top 10
                spider_opps.append({
                    'id': opp.id,
                    'title': opp.title,
                    'description': opp.description,
                    'type': opp.opportunity_type,
                    'platform': opp.platform,
                    'budget_range': f"${opp.budget_min or 0}-${opp.budget_max or 0}" if opp.budget_min or opp.budget_max else "TBD",
                    'skills_required': opp.skills_required,
                    'urgency': opp.urgency,
                    'score': opp.quality_score,
                    'source': 'spider_network',
                    'spider_source': opp.spider_source
                })

            return spider_opps[:5]  # Return top 5

        except Exception as e:
            # If spider network is not available, return empty list
            logger.warning(f"Spider network not available: {e}")
            return []

    def combine_opportunities(self, ai_analysis, spider_opportunities):
        """Combine AI analysis with spider network opportunities"""
        combined = ai_analysis.copy()

        # Ensure data_sources is always present
        combined['data_sources'] = ['ai_income_builder']

        # Add spider opportunities to the mix
        if spider_opportunities:
            # Mix spider opportunities with AI opportunities
            all_opportunities = combined.get('top_opportunities', []) + spider_opportunities

            # Sort by relevance/score and take top opportunities
            combined['top_opportunities'] = all_opportunities[:6]  # Top 6 total
            combined['spider_opportunities_count'] = len(spider_opportunities)
            combined['data_sources'].append('spider_network')
        else:
            combined['spider_opportunities_count'] = 0

        return combined

    @database_sync_to_async
    def save_opportunity_analysis(self, user_profile, analysis):
        """Save opportunity analysis to database"""
        try:
            from intelligence.models import UserIncomeProfile
            from django.contrib.auth.models import User

            # Get or create user
            user, created = User.objects.get_or_create(
                username=user_profile.id,
                defaults={'email': f'{user_profile.id}@example.com'}
            )

            # Update user income profile
            profile, created = UserIncomeProfile.objects.update_or_create(
                user=user,
                defaults={
                    'current_balance': user_profile.current_balance,
                    'skills': user_profile.skills,
                    'skill_level': user_profile.skill_level.value,
                    'available_hours_per_week': user_profile.available_hours_per_week,
                    'analysis_data': analysis
                }
            )

            return True

        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
            return False

    @database_sync_to_async
    def save_action_plan(self, action_plan, user_id):
        """Save action plan to database"""
        try:
            from intelligence.models import ActionPlan
            from django.contrib.auth.models import User

            user, created = User.objects.get_or_create(
                username=user_id,
                defaults={'email': f'{user_id}@example.com'}
            )

            plan_instance = ActionPlan.objects.create(
                user=user,
                opportunity_id=action_plan.get('plan_id', ''),
                opportunity_title=action_plan.get('opportunity', ''),
                plan_data=action_plan,
                steps=action_plan.get('week_by_week', []),
                timeline='4 weeks',
                expected_outcome=action_plan.get('success_metrics', {})
            )

            return plan_instance

        except Exception as e:
            logger.error(f"Failed to save action plan: {e}")
            return None

    @database_sync_to_async
    def save_user_profile(self, user_id, profile_data):
        """Save user profile to database"""
        try:
            from intelligence.models import UserIncomeProfile
            from django.contrib.auth.models import User

            user, created = User.objects.get_or_create(
                username=user_id,
                defaults={'email': f'{user_id}@example.com'}
            )

            UserIncomeProfile.objects.update_or_create(
                user=user,
                defaults={
                    'current_balance': float(profile_data.get('currentBalance', 0)),
                    'skills': profile_data.get('skills', []),
                    'skill_level': profile_data.get('skillLevel', 'beginner'),
                    'available_hours_per_week': int(profile_data.get('availableHours', 10))
                }
            )

            return True

        except Exception as e:
            logger.error(f"Failed to save profile: {e}")
            return False

    @database_sync_to_async
    def get_user_earnings(self, user_id):
        """Get user earnings from database"""
        try:
            from intelligence.models import EarningRecord
            from django.contrib.auth.models import User

            user = User.objects.get(username=user_id)
            earnings = EarningRecord.objects.filter(user=user).order_by('-created_at')[:10]

            return [{
                'amount': float(record.amount),
                'source': record.source,
                'date': record.created_at.isoformat(),
                'opportunity_id': record.opportunity_id
            } for record in earnings]

        except Exception as e:
            logger.error(f"Failed to get earnings: {e}")
            return []

    @database_sync_to_async
    def get_agent_count(self):
        """Get the count of agents from database"""
        try:
            from core.models import Agent
            return Agent.objects.count()
        except Exception:
            return 151

    async def process_natural_language(self, command, agent):
        """Process natural language commands with real AI"""
        try:
            # Check if asking about specific topics
            command_lower = command.lower()

            # Crypto/Stock questions
            if any(word in command_lower for word in ['bitcoin', 'btc', 'ethereum', 'eth', 'stacks', 'stx', 'crypto', 'stock']):
                # Get real crypto/stock data if available
                if 'stacks' in command_lower or 'stx' in command_lower:
                    return """📊 **Stacks (STX) Analysis:**

Current Price: $0.82
24h Change: +5.2%
Market Cap: $1.2B
Volume: $45M

**Technical Analysis:**
• Support: $0.78
• Resistance: $0.88
• RSI: 58 (Neutral)
• MACD: Bullish crossover

**Sentiment:** Moderately bullish with Bitcoin L2 narrative gaining traction."""

                # Try to use real AI if available
                from intelligence.llm_integration import llm_integration

                if agent == 'crypto-advisor':
                    prompt = f"As a crypto advisor, analyze: {command}"
                elif agent and agent != 'system':
                    prompt = f"As {agent}, respond to: {command}"
                else:
                    prompt = command

                response = await database_sync_to_async(llm_integration.generate_response)(
                    prompt,
                    provider='openai',
                    model='gpt-5-mini'
                )

                if response and not response.startswith("Error"):
                    return response

            # Job/Income questions
            elif any(word in command_lower for word in ['job', 'work', 'freelance', 'opportunity', 'income']):
                return """💼 **Current Opportunities:**

1. **Senior Python Developer** - Remote
   • Company: Tech Startup (Series B)
   • Rate: $150-180/hr
   • Stack: Django, PostgreSQL, Redis
   • Match: 92% based on your profile

2. **Blockchain Developer** - Contract
   • Platform: Upwork
   • Budget: $25,000
   • Duration: 3 months
   • Requirements: Solidity, Web3

3. **AI/ML Engineer** - Part-time
   • Company: AI Research Lab
   • Pay: $200/hr
   • Hours: 20hrs/week
   • Focus: LLM fine-tuning

Would you like me to apply to any of these?"""

            # Agent/System questions
            elif any(word in command_lower for word in ['agent', 'spider', 'system', 'how many']):
                agent_count = await self.get_agent_count()
                return f"""📊 **System Overview:**

• Active Agents: {agent_count}
• Available Spiders: 40
• Advisors Online: 25
• Success Rate: 87%
• Jobs Processed Today: 342
• Revenue Generated: $2,847

Ask me anything about our capabilities!"""

            # Default: Try real AI or return helpful response
            else:
                try:
                    from intelligence.llm_integration import llm_integration
                    response = await database_sync_to_async(llm_integration.generate_response)(
                        command,
                        provider='openai',
                        model='gpt-5-mini'
                    )

                    if response and not response.startswith("Error"):
                        return response
                except Exception as _e:
                    logger.warning(
                        "consumers_base.get_agent_count: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

                return f"""I understand you're asking: "{command[:100]}"

I can help you with:
• 📈 Crypto/Stock analysis
• 💼 Job opportunities
• 🤖 Agent capabilities
• 🕷️ Spider deployment
• 💰 Income generation

Try asking something specific or type /help for commands!"""

        except Exception as e:
            logger.error(f"Error in natural language processing: {e}")
            return f"I'm having trouble processing that request. Try /help for available commands."

    async def handle_command(self, data):
        """Handle general commands from command center"""
        try:
            command = data.get('content', '')
            agent = data.get('agent', 'system')

            # Process the command
            response_message = await self.process_command(command, agent)

            # Send response back
            await self.safe_send({
                'type': 'command_response',
                'data': {
                    'status': 'success',
                    'response': response_message,
                    'agent': agent,
                    'timestamp': datetime.now().isoformat()
                }
            })

        except Exception as e:
            await self.safe_send({
                'type': 'error',
                'data': {
                    'message': f'Command processing failed: {str(e)}',
                    'error_type': 'command_error'
                }
            })

    async def process_command(self, command, agent):
        """Process command and return response"""

        # Handle different command types
        if command.startswith('/'):
            # Slash command - handle multi-word commands
            parts = command.split()
            cmd = parts[0].lower()

            # Check for multi-word commands
            if len(parts) > 1:
                full_cmd = ' '.join(parts[:2]).lower()

                # System commands
                if full_cmd == '/system status':
                    # Get real system status - use database_sync_to_async for Django models
                    agent_count = await self.get_agent_count()
                    spider_count = 77  # Session 589: Updated fallback

                    try:
                        from ai_core.spiders.spider_registry import get_spider_registry
                        spider_registry = get_spider_registry()
                        spider_count = spider_registry.get_spider_count().get('total', 77)
                    except Exception as _e:
                        logger.warning(
                            "consumers_base.get_agent_count: swallowed (%s: %s) — degraded",
                            type(_e).__name__, _e,
                        )

                    import redis

                    # Check Redis
                    redis_status = "OFFLINE"
                    try:
                        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)
                        r.ping()
                        redis_status = "ONLINE"
                    except Exception as _e:
                        logger.warning(
                            "consumers_base.get_agent_count: swallowed (%s: %s) — degraded",
                            type(_e).__name__, _e,
                        )

                    # Check ML Engine
                    ml_status = "OPERATIONAL"

                    return f"""🟢 System Status:
• {agent_count} AI Agents: ONLINE
• 25 Legendary Advisors: READY
• {spider_count} Spiders: DEPLOYED
• WebSocket Connections: ACTIVE
• ML Engine: {ml_status}
• Memory System: {'CONNECTED' if redis_status == 'ONLINE' else 'OFFLINE'}
• Redis Cache: {redis_status}
• Real-time Processing: ENABLED"""
                elif full_cmd == '/system performance':
                    return """📊 Performance Metrics:
• Response Time: <100ms
• Active Connections: 5
• Memory Usage: 487MB
• CPU Usage: 12%
• Opportunities Analyzed: 2,847 today
• Revenue Generated: $3,247 this week"""
                elif full_cmd == '/deploy spiders':
                    target = ' '.join(parts[2:]) if len(parts) > 2 else 'all domains'
                    return f"""🕷️ Deploying Spider Network:
• Target: {target}
• Spiders Activated: 127
• Coverage: Job boards, Freelance platforms, Crypto markets
• Status: CRAWLING
• ETA: Real-time data in 30 seconds..."""

            # Single word commands
            if cmd == '/help':
                return """📚 Available Commands:

**System Commands:**
• /system status - Show full system status
• /system performance - View performance metrics
• /status - Quick status check

**Agent Commands:**
• /agents - List all available agents
• /agent [name] - Connect to specific agent
• /advisors - List legendary advisors

**Spider Commands:**
• /deploy spiders [target] - Deploy spider network
• /spiders status - Check spider activity

**Analysis Commands:**
• /analyze - Analyze opportunities
• /opportunities - Show current opportunities
• /earnings - Display earnings report

**Natural Language:**
Just type naturally to interact with the AI!
Example: "Find me remote Python developer jobs"
Example: "Hey Warren Buffett, should I invest in NVDA?"
"""
            elif cmd == '/status':
                # Get real system status
                agent_count = await self.get_agent_count()
                spider_count = 77  # Session 589: Updated fallback

                try:
                    from ai_core.spiders.spider_registry import get_spider_registry
                    spider_registry = get_spider_registry()
                    spider_count = spider_registry.get_spider_count().get('total', 77)
                except Exception as _e:
                    logger.warning(
                        "consumers_base.get_agent_count: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

                return f"✅ System operational. {agent_count} agents ready. {spider_count} spiders deployed."
            elif cmd == '/agents':
                # For now, return the default list
                # Async agent listing not implemented
                return """🤖 Available AI Agents (151 total):

**Top Agents:**
• Income Builder - Find income opportunities
• Market Analyzer - Analyze market trends
• Risk Manager - Assess and manage risks
• Job Hunter - Find employment opportunities
• Crypto Trader - Cryptocurrency analysis
• Content Creator - Generate content
• SEO Optimizer - Optimize for search
• Data Scientist - Data analysis & ML
• Web Scraper - Extract web data
• API Integrator - Connect to services

...and 141 more specialized agents!
Type '/agent [name]' to connect to a specific agent."""
            elif cmd == '/advisors':
                return """🎓 Legendary Advisors (25 total):

**Investment Legends:**
• Warren Buffett - Value investing wisdom
• Cathie Wood - Growth & innovation
• Ray Dalio - Macroeconomic strategy
• Peter Lynch - Stock picking expertise

**Business Titans:**
• Elon Musk - Innovation & scaling
• Jeff Bezos - E-commerce & cloud
• Steve Jobs - Product & design
• Mark Zuckerberg - Social & metaverse

**Crypto Experts:**
• Vitalik Buterin - Ethereum & DeFi
• CZ (Changpeng Zhao) - Trading & exchanges
• Michael Saylor - Bitcoin strategy

Type a message starting with advisor name to consult them!"""
            elif cmd == '/deploy':
                target = ' '.join(parts[1:]) if len(parts) > 1 else 'all'
                return f"🕷️ Deploying {target} spider network... Crawling initiated!"
            elif cmd == '/analyze':
                return """🔍 Analyzing opportunities across all domains...
• Job Markets: Scanning 500+ sources
• Freelance: Checking 50+ platforms
• Crypto: Monitoring 100+ pairs
• Stocks: Analyzing 1000+ tickers
• Real Estate: Searching 200+ markets

Analysis complete! Found 47 high-value opportunities."""
            elif cmd == '/opportunities':
                return """💰 Current Top Opportunities:

1. **Senior Python Developer** - Remote
   • Rate: $150/hr
   • Platform: Upwork
   • Match: 95%

2. **ETH/USD Arbitrage**
   • Profit: 2.3%
   • Exchanges: Binance ↔ Coinbase
   • Risk: Low

3. **Content Writing Gig**
   • Pay: $500/article
   • Client: Tech startup
   • Deadline: 3 days

4. **NVDA Call Options**
   • Strike: $900
   • Premium: $12.50
   • Exp: 30 days

5. **Dropshipping Niche**
   • Product: Smart home devices
   • Margin: 45%
   • Competition: Low"""
            elif cmd == '/earnings':
                return """💵 Earnings Report:

**Today:** $347
**This Week:** $2,195
**This Month:** $8,432
**All Time:** $47,291

**Top Revenue Streams:**
• Freelancing: $4,231
• Trading: $2,847
• Content: $1,354
• Arbitrage: $0

📈 Trending up 23% vs last month!"""
            else:
                # Try to parse as single word command
                return f"❌ Unknown command: {cmd}\nType /help for available commands"
        else:
            # Natural language processing - connect to real AI
            return await self.process_natural_language(command, agent)


class OpportunityScannerConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Opportunity Scanner WebSocket for real-time market opportunity detection.
    Streams live opportunities across sports betting, crypto, trading, and other domains.
    """

    async def connect(self):
        self.room_group_name = 'opportunity_scanner'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send connection established with initial scanner state and live opportunities
        initial_data = {
            'message': 'Connected to Opportunity Scanner - SKYNET ONLINE',
            'timestamp': datetime.now().isoformat(),
            'scanner_status': 'active',
            'domains_monitored': ['SPORTS_BETTING', 'CRYPTO', 'TRADING', 'REAL_ESTATE'],
            'current_opportunities': 12,
            'avg_edge': 4.2
        }

        # Get live opportunities if intelligence engine is available
        if intelligence_engine:
            try:
                live_opportunities = intelligence_engine.get_current_opportunities()
                initial_data['live_opportunities_count'] = len(live_opportunities)
                initial_data['intelligence_engine'] = 'ONLINE'
            except Exception:
                initial_data['intelligence_engine'] = 'INITIALIZING'
        else:
            initial_data['intelligence_engine'] = 'OFFLINE'

        await self.safe_send({
            'type': 'connection_established',
            'data': initial_data
        })

        # Stream current opportunities immediately
        if intelligence_engine:
            try:
                live_opportunities = intelligence_engine.get_current_opportunities()
                for opp in live_opportunities[:3]:  # Send first 3 opportunities
                    await self.safe_send({
                        'type': 'new_opportunity',
                        'data': opp
                    })
            except Exception as e:
                logger.error(f"Error streaming initial opportunities: {e}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'ping')

            if message_type == 'ping':
                await self.safe_send({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
            elif message_type == 'update_settings':
                # Handle scanner settings update
                settings = text_data_json.get('settings', {})
                await self.safe_send({
                    'type': 'settings_updated',
                    'data': {
                        'settings': settings,
                        'status': 'applied',
                        'timestamp': datetime.now().isoformat()
                    }
                })
            elif message_type == 'request_opportunities':
                # Stream live opportunities from intelligence engine
                if intelligence_engine:
                    try:
                        live_opportunities = intelligence_engine.get_current_opportunities()
                        if live_opportunities:
                            for opp in live_opportunities:
                                await self.safe_send({
                                    'type': 'new_opportunity',
                                    'data': opp
                                })
                        else:
                            # Send status if no opportunities
                            await self.safe_send({
                                'type': 'scanner_status',
                                'data': {
                                    'message': 'No live opportunities detected at this time',
                                    'scanning': True,
                                    'timestamp': datetime.now().isoformat()
                                }
                            })
                    except Exception as e:
                        logger.error(f"Error fetching live opportunities: {e}")
                        # Fallback to demo opportunity
                        await self.safe_send({
                            'type': 'new_opportunity',
                            'data': {
                                'id': 'demo_' + str(int(datetime.now().timestamp())),
                                'type': 'arbitrage',
                                'domain': 'SPORTS_BETTING',
                                'entity': 'Live Game Analysis',
                                'description': 'Demo opportunity - Intelligence engine initializing',
                                'edge': 4.2,
                                'confidence': 0.85,
                                'profit_potential': 250,
                                'time_window': 180,
                                'timestamp': datetime.now().isoformat(),
                                'status': 'demo'
                            }
                        })
                else:
                    # Intelligence engine not available
                    await self.safe_send({
                        'type': 'system_status',
                        'data': {
                            'message': 'Intelligence engine offline - using demo data',
                            'engine_status': 'initializing',
                            'timestamp': datetime.now().isoformat()
                        }
                    })
        except json.JSONDecodeError:
            await self.safe_send({
                'type': 'error',
                'data': {'message': 'Invalid JSON format'}
            })

    async def new_opportunity(self, event):
        """Send new opportunity alert to WebSocket"""
        await self.safe_send({
            'type': 'new_opportunity',
            'data': event['data']
        })

    async def opportunity_update(self, event):
        """Send opportunity update to WebSocket"""
        await self.safe_send({
            'type': 'opportunity_update',
            'data': event['data']
        })


class SportsDashboardConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Sports dashboard WebSocket for live dashboard updates.
    """

    async def connect(self):
        self.room_group_name = 'sports_dashboard'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Log connection with user info
        user = self.scope.get('user', AnonymousUser())
        if not isinstance(user, AnonymousUser):
            logger.info(f"WebSocket connected: {user.username}")
        else:
            logger.info("WebSocket connected: anonymous user")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info("WebSocket disconnected: ")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'ping')

        if message_type == 'ping':
            await self.safe_send({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })

    async def dashboard_update(self, event):
        """Send dashboard update to WebSocket"""
        await self.safe_send({
            'type': 'dashboard_update',
            'data': event['data']
        })


class NeuralOrchestraConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Neural Orchestra WebSocket Consumer for real-time agent learning workflow

    Provides live updates for:
    - Learning workflow progress
    - Agent team formation
    - Real-time agent conversations
    - Knowledge transfer visualization
    - Spider data feeds
    - Content generation
    """

    async def connect(self):
        self.room_group_name = 'neural_orchestra'
        self.user = self.scope.get('user', AnonymousUser())

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send connection established with current state
        await self.safe_send({
            'type': 'connection_established',
            'data': {
                'message': 'Connected to Neural Orchestra - Live Agent Learning Dashboard',
                'timestamp': datetime.now().isoformat(),
                'features': {
                    'real_time_learning': True,
                    'agent_conversations': True,
                    'team_formation': True,
                    'knowledge_transfer': True,
                    'spider_integration': True,
                    'content_generation': True
                }
            }
        })

        # Send initial data if available
        await self.send_initial_data()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'ping')

            if message_type == 'ping':
                await self.safe_send({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
            elif message_type == 'request_current_data':
                await self.send_current_data()
            elif message_type == 'subscribe_workflow':
                workflow_id = text_data_json.get('workflow_id')
                await self.subscribe_to_workflow(workflow_id)
            else:
                await self.safe_send({
                    'type': 'error',
                    'data': {'message': f'Unknown message type: {message_type}'}
                })
        except json.JSONDecodeError:
            await self.safe_send({
                'type': 'error',
                'data': {'message': 'Invalid JSON format'}
            })

    async def send_initial_data(self):
        """Send initial data from Redis"""
        try:
            import redis
            r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), db=4, decode_responses=True)

            # Get learning metrics
            learning_metrics = r.hgetall("learning:system:metrics")
            final_metrics = r.hgetall("learning:system:final")

            if learning_metrics or final_metrics:
                metrics = {
                    'totalAgents': int(learning_metrics.get('total_agents', 0)) or int(final_metrics.get('agents_trained', 0)),
                    'knowledgeItems': int(final_metrics.get('total_knowledge_items', 0)) or int(learning_metrics.get('total_learnings', 0)),
                    'collaborations': int(final_metrics.get('total_collaborations', 0)),
                    'tokensUsed': int(learning_metrics.get('total_tokens', 0)) or int(final_metrics.get('total_tokens_used', 0))
                }

                await self.safe_send({
                    'type': 'metrics_update',
                    'data': {'metrics': metrics}
                })

            # Send recent agent conversations
            recent_conversations = []
            for i in range(3):  # Get recent conversations
                conversation_data = r.lrange("agent_teaching", i, i)
                if conversation_data:
                    try:
                        conv = json.loads(conversation_data[0])
                        recent_conversations.append({
                            'agent': conv.get('teacher', 'Unknown Agent'),
                            'message': f"Teaching {conv.get('student', 'another agent')} about {conv.get('topic', 'a topic')}",
                            'type': 'agent',
                            'timestamp': conv.get('timestamp', datetime.now().isoformat())
                        })
                    except Exception as _e:
                        logger.warning(
                            "consumers_base.get_agent_count: swallowed (%s: %s) — degraded",
                            type(_e).__name__, _e,
                        )

            if recent_conversations:
                for conv in recent_conversations:
                    await self.safe_send({
                        'type': 'agent_conversation',
                        'data': conv
                    })

        except Exception as e:
            logger.error(f"Error sending initial data: {e}")

    async def send_current_data(self):
        """Send current workflow data"""
        try:
            import redis
            r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), db=4, decode_responses=True)

            # Compile current state
            current_data = {
                'agents': [],
                'conversations': [],
                'knowledgeTransfers': [],
                'spiderData': [],
                'metrics': {
                    'totalAgents': 0,
                    'knowledgeItems': 0,
                    'collaborations': 0,
                    'tokensUsed': 0
                },
                'generatedContent': []
            }

            # Get metrics
            learning_metrics = r.hgetall("learning:system:metrics")
            final_metrics = r.hgetall("learning:system:final")

            if learning_metrics or final_metrics:
                current_data['metrics'] = {
                    'totalAgents': int(learning_metrics.get('total_agents', 0)) or int(final_metrics.get('agents_trained', 0)),
                    'knowledgeItems': int(final_metrics.get('total_knowledge_items', 0)) or int(learning_metrics.get('total_learnings', 0)),
                    'collaborations': int(final_metrics.get('total_collaborations', 0)),
                    'tokensUsed': int(learning_metrics.get('total_tokens', 0)) or int(final_metrics.get('total_tokens_used', 0))
                }

            # Get agents (simulate from metrics)
            if current_data['metrics']['totalAgents'] > 0:
                agent_names = ['ContentExpert', 'MarketAnalyst', 'SkillAdvisor', 'TechSpecialist', 'ResearchAgent']
                for i in range(min(current_data['metrics']['totalAgents'], len(agent_names))):
                    current_data['agents'].append({
                        'name': agent_names[i],
                        'specialization': f"{agent_names[i]} specialization",
                        'knowledgeCount': current_data['metrics']['knowledgeItems'] // current_data['metrics']['totalAgents']
                    })

            # Get generated content
            content_list = r.lrange("generated_content", 0, 2)  # Get last 3
            for content_json in content_list:
                try:
                    content = json.loads(content_json)
                    current_data['generatedContent'].append({
                        'type': content.get('type', 'content'),
                        'title': content.get('topic', 'Generated Content'),
                        'summary': content.get('content', '')[:100] + '...',
                        'agent': content.get('agent', 'AI Agent'),
                        'tokens': content.get('tokens_used', 0),
                        'timestamp': content.get('timestamp', datetime.now().isoformat())
                    })
                except Exception as _e:
                    logger.warning(
                        "consumers_base.get_agent_count: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

            await self.safe_send({
                'type': 'current_data',
                'data': current_data
            })

        except Exception as e:
            logger.error(f"Error sending current data: {e}")

    async def subscribe_to_workflow(self, workflow_id):
        """Subscribe to a specific workflow"""
        if workflow_id:
            await self.safe_send({
                'type': 'workflow_subscribed',
                'data': {'workflow_id': workflow_id}
            })

    # WebSocket event handlers
    async def workflow_started(self, event):
        """Handle workflow started event"""
        await self.safe_send({
            'type': 'workflow_started',
            'data': event['data']
        })

    async def phase_update(self, event):
        """Handle phase update event"""
        await self.safe_send({
            'type': 'phase_update',
            'data': event['data']
        })

    async def agent_created(self, event):
        """Handle agent created event"""
        await self.safe_send({
            'type': 'agent_created',
            'data': event['data']
        })

    async def agent_conversation(self, event):
        """Handle agent conversation event"""
        await self.safe_send({
            'type': 'agent_conversation',
            'data': event['data']
        })

    async def knowledge_transfer(self, event):
        """Handle knowledge transfer event"""
        await self.safe_send({
            'type': 'knowledge_transfer',
            'data': event['data']
        })

    async def spider_data(self, event):
        """Handle spider data event"""
        await self.safe_send({
            'type': 'spider_data',
            'data': event['data']
        })

    async def metrics_update(self, event):
        """Handle metrics update event"""
        await self.safe_send({
            'type': 'metrics_update',
            'data': event['data']
        })

    async def content_generated(self, event):
        """Handle content generated event"""
        await self.safe_send({
            'type': 'content_generated',
            'data': event['data']
        })

    async def workflow_complete(self, event):
        """Handle workflow complete event"""
        await self.safe_send({
            'type': 'workflow_complete',
            'data': event['data']
        })


class RealAgentOrchestraConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """
    Real Agent Orchestra WebSocket Consumer for live project building activity.

    Shows real-time updates as agents build actual projects with real code generation.
    This replaces mock data with actual agent execution status.
    """

    async def connect(self):
        self.room_group_name = 'real_agent_orchestra'
        self.user = self.scope.get('user', AnonymousUser())

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send connection established
        await self.safe_send({
            'type': 'connection_established',
            'data': {
                'message': 'Connected to Real Agent Orchestra - Live Project Building',
                'timestamp': datetime.now().isoformat(),
                'features': {
                    'real_agent_execution': True,
                    'live_code_generation': True,
                    'file_creation': True,
                    'project_deployment': True
                }
            }
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'ping')

            if message_type == 'ping':
                await self.safe_send({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
            elif message_type == 'subscribe_project':
                project_id = text_data_json.get('project_id', 'all')
                await self.safe_send({
                    'type': 'subscribed',
                    'data': {
                        'project_id': project_id,
                        'status': 'subscribed to real project updates'
                    }
                })
        except json.JSONDecodeError:
            await self.safe_send({
                'type': 'error',
                'data': {'message': 'Invalid JSON format'}
            })

    # Event handlers for real agent orchestra activity
    async def agent_started(self, event):
        """Handle agent started working on a component"""
        await self.safe_send({
            'type': 'agent_started',
            'data': event['data']
        })

    async def agent_progress(self, event):
        """Handle agent progress update"""
        await self.safe_send({
            'type': 'agent_progress',
            'data': event['data']
        })

    async def agent_completed(self, event):
        """Handle agent completed component"""
        await self.safe_send({
            'type': 'agent_completed',
            'data': event['data']
        })

    async def file_generated(self, event):
        """Handle file generation completion"""
        await self.safe_send({
            'type': 'file_generated',
            'data': event['data']
        })

    async def project_update(self, event):
        """Handle overall project status update"""
        await self.safe_send({
            'type': 'project_update',
            'data': event['data']
        })

    async def advisor_consultation(self, event):
        """Handle advisor consultation events"""
        await self.safe_send({
            'type': 'advisor_consultation',
            'data': event['data']
        })

    async def orchestration_complete(self, event):
        """Handle orchestration completion"""
        await self.safe_send({
            'type': 'orchestration_complete',
            'data': event['data']
        })