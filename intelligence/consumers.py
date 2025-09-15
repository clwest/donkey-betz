"""
WebSocket consumers for Intelligence module
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class IncomeBuilderConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for Income Builder real-time updates"""

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_name = 'income_builder'
        self.room_group_name = f'income_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Income Builder WebSocket connected: {self.channel_name}")

        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'Connected to Income Builder updates'
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Income Builder WebSocket disconnected: {self.channel_name}")

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

            elif message_type == 'subscribe_plan':
                # Subscribe to specific plan updates
                plan_id = data.get('plan_id')
                if plan_id:
                    await self.channel_layer.group_add(
                        f'plan_{plan_id}',
                        self.channel_name
                    )
                    await self.send(text_data=json.dumps({
                        'type': 'subscribed',
                        'plan_id': plan_id
                    }))

            elif message_type == 'get_status':
                # Get status of a specific plan
                plan_id = data.get('plan_id')
                if plan_id:
                    plan_status = await self.get_plan_status(plan_id)
                    await self.send(text_data=json.dumps({
                        'type': 'plan_status',
                        'plan_id': plan_id,
                        'status': plan_status
                    }))

            elif message_type == 'analyze_opportunities':
                # Handle analyze opportunities request from frontend
                profile_data = data.get('profile', {})
                await self.analyze_opportunities(profile_data)

            elif message_type == 'select_opportunity':
                # Handle opportunity selection
                opportunity_id = data.get('opportunity_id')
                if opportunity_id:
                    await self.select_opportunity(opportunity_id)

            elif message_type == 'get_action_plan':
                # Get detailed action plan for opportunity
                opportunity_id = data.get('opportunity_id')
                if opportunity_id:
                    await self.get_action_plan(opportunity_id)

            elif message_type == 'update_profile':
                # Handle profile update
                profile_data = data.get('profile', {})
                await self.update_profile(profile_data)

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

    async def action_plan_update(self, event):
        """Handle action plan update events from channel layer"""
        # Send update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'action_plan_update',
            'plan_id': event.get('plan_id'),
            'status': event.get('status'),
            'progress': event.get('progress'),
            'current_step': event.get('current_step'),
            'execution_logs': event.get('execution_logs'),
            'results': event.get('results'),
            'completed_at': event.get('completed_at')
        }))

    async def new_opportunity(self, event):
        """Handle new opportunity events"""
        await self.send(text_data=json.dumps({
            'type': 'new_opportunity',
            'opportunity': event.get('opportunity')
        }))

    async def execution_log(self, event):
        """Handle execution log events"""
        await self.send(text_data=json.dumps({
            'type': 'execution_log',
            'plan_id': event.get('plan_id'),
            'log': event.get('log'),
            'timestamp': event.get('timestamp')
        }))

    @database_sync_to_async
    def get_plan_status(self, plan_id):
        """Get the status of an action plan"""
        from intelligence.models import ActionPlan
        try:
            plan = ActionPlan.objects.get(id=plan_id)
            return {
                'status': plan.status,
                'progress': plan.progress,
                'current_step': plan.current_step,
                'total_steps': len(plan.steps) if plan.steps else 0,
                'execution_logs': plan.execution_logs[-5:] if plan.execution_logs else []
            }
        except ActionPlan.DoesNotExist:
            return None

    async def analyze_opportunities(self, profile_data):
        """Analyze opportunities for user profile using real AI Income Builder"""
        try:
            # Import the actual working income builder
            from backend.intelligence.income_builder import income_builder, UserProfile, SkillLevel

            # Create user profile
            profile = UserProfile(
                id=profile_data.get('id', 'default_user'),
                current_balance=profile_data.get('current_balance', 0.0),
                skills=profile_data.get('skills', ['writing', 'research']),
                skill_level=SkillLevel(profile_data.get('skill_level', 'beginner')),
                available_hours_per_week=profile_data.get('available_hours', 10)
            )

            # Use the real income builder to analyze opportunities
            analysis = await income_builder.analyze_user_potential(profile)

            # Send the real analysis results to frontend
            await self.send(text_data=json.dumps({
                'type': 'opportunities_analysis',
                'top_opportunities': analysis.get('top_opportunities', []),
                'earnings_projection': analysis.get('earnings_projection', {}),
                'recommended_path': analysis.get('recommended_path', []),
                'skill_gaps': analysis.get('skill_gaps', []),
                'success_probability': analysis.get('success_probability', 0)
            }))

        except Exception as e:
            logger.error(f"Error analyzing opportunities: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to analyze opportunities: {str(e)}'
            }))

    async def select_opportunity(self, opportunity_id):
        """Handle opportunity selection and create action plan"""
        try:
            from backend.intelligence.income_builder import income_builder

            # Create action plan for the selected opportunity
            plan = await income_builder.create_action_plan('user', opportunity_id)

            await self.send(text_data=json.dumps({
                'type': 'action_plan',
                'plan': plan,
                'opportunity_id': opportunity_id
            }))

        except Exception as e:
            logger.error(f"Error selecting opportunity: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to select opportunity: {str(e)}'
            }))

    async def get_action_plan(self, opportunity_id):
        """Get detailed action plan for opportunity"""
        try:
            from backend.intelligence.income_builder import income_builder

            # Get detailed action plan
            plan = await income_builder.create_action_plan('user', opportunity_id)

            await self.send(text_data=json.dumps({
                'type': 'action_plan',
                'opportunity_id': opportunity_id,
                'week_by_week': plan.get('week_by_week', []),
                'daily_tasks': plan.get('daily_tasks', {}),
                'success_metrics': plan.get('success_metrics', {}),
                'full_plan': plan
            }))

        except Exception as e:
            logger.error(f"Error getting action plan: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to get action plan: {str(e)}'
            }))

    async def update_profile(self, profile_data):
        """Update user profile"""
        try:
            # Store profile update and send confirmation
            await self.send(text_data=json.dumps({
                'type': 'profile_updated',
                'profile': profile_data,
                'message': 'Profile updated successfully'
            }))

        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to update profile: {str(e)}'
            }))


class RevenueIncomeConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for Revenue + Income Builder integration real-time updates"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.integration = None

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_name = 'revenue_income'
        self.room_group_name = f'revenue_{self.room_name}'

        # Initialize integration service
        from .revenue_integration import RevenueIncomeIntegration
        self.integration = RevenueIncomeIntegration()

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Revenue Income WebSocket connected: {self.channel_name}")

        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'Connected to Revenue Income Integration'
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Revenue Income WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'new_opportunity':
                # Process new opportunity from spider network
                opportunity = data.get('opportunity')
                if opportunity:
                    result = await self.integration.process_opportunity(opportunity)

                    # Send result back to client
                    await self.send(text_data=json.dumps({
                        'type': 'opportunity_processed',
                        'result': result
                    }))

                    # Broadcast to group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'opportunity_update',
                            'opportunity': opportunity,
                            'result': result
                        }
                    )

            elif message_type == 'submit_proposal':
                # Submit proposal to platform
                proposal = data.get('proposal')
                if proposal:
                    submission_result = await self.integration.auto_submit_proposal(proposal)

                    await self.send(text_data=json.dumps({
                        'type': 'proposal_submitted',
                        'result': submission_result
                    }))

            elif message_type == 'check_responses':
                # Check for proposal responses
                responses = await self.integration.monitor_responses()

                await self.send(text_data=json.dumps({
                    'type': 'responses_update',
                    'responses': responses
                }))

            elif message_type == 'get_metrics':
                # Get revenue metrics
                metrics = await self.get_revenue_metrics()

                await self.send(text_data=json.dumps({
                    'type': 'metrics_update',
                    'metrics': metrics
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

    async def opportunity_update(self, event):
        """Handle opportunity update events from channel layer"""
        await self.send(text_data=json.dumps({
            'type': 'opportunity_update',
            'opportunity': event.get('opportunity'),
            'result': event.get('result')
        }))

    async def proposal_status_update(self, event):
        """Handle proposal status update events"""
        await self.send(text_data=json.dumps({
            'type': 'proposal_status_update',
            'proposal_id': event.get('proposal_id'),
            'status': event.get('status'),
            'details': event.get('details')
        }))

    async def revenue_generated(self, event):
        """Handle revenue generated events"""
        await self.send(text_data=json.dumps({
            'type': 'revenue_generated',
            'amount': event.get('amount'),
            'source': event.get('source'),
            'proposal_id': event.get('proposal_id')
        }))

    @database_sync_to_async
    def get_revenue_metrics(self):
        """Get revenue metrics from database"""
        # This will be implemented when we add the models
        return {
            'proposals_submitted': 0,
            'response_rate': 0,
            'revenue_generated': 0,
            'active_opportunities': 0
        }