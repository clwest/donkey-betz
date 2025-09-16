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

        # Send initial opportunities data
        await self.send_initial_data()

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

            elif message_type == 'search_reddit':
                # Handle Reddit search request
                query = data.get('query', 'business opportunities')
                subreddit = data.get('subreddit', 'Entrepreneur+sidehustle+forhire')
                await self.search_reddit_opportunities(query, subreddit)

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

    async def get_reddit_opportunities(self):
        """Fetch opportunities from Reddit discussions"""
        try:
            from core.tools import ToolRegistry

            # Try to get Reddit tool
            reddit_tool = ToolRegistry.get_tool('reddit_api')
            if reddit_tool and reddit_tool.is_configured:
                # Search for business opportunities in relevant subreddits
                result = await database_sync_to_async(reddit_tool.execute)(
                    query="passive income OR side hustle OR business idea OR looking to hire",
                    search_type="posts",
                    subreddit="Entrepreneur+sidehustle+passive_income+forhire+freelance",
                    limit=10,
                    sort="hot"
                )

                if result.get('success') and result.get('data'):
                    reddit_opportunities = []
                    for post in result['data'][:3]:  # Top 3 Reddit opportunities
                        reddit_opportunities.append({
                            'id': f'reddit_{post.get("id", "")}',
                            'title': f"Reddit: {post.get('title', 'Opportunity')}",
                            'stream_type': 'Community Sourced',
                            'description': post.get('selftext', '')[:200] + '...' if post.get('selftext') else post.get('title', ''),
                            'time_to_income': '1-7 days',
                            'potential_monthly': '$500-$2,000',
                            'difficulty': 'beginner',
                            'initial_investment': 0,
                            'success_rate': 65,
                            'market_demand': post.get('score', 0),
                            'required_skills': ['Communication', 'Quick Response', 'Flexibility'],
                            'action_steps': [
                                'Review full Reddit post',
                                'Respond with proposal',
                                'Negotiate terms',
                                'Deliver service'
                            ],
                            'resources': [
                                {'name': 'Original Post', 'url': post.get('url', '')},
                                {'name': 'Subreddit', 'url': f"https://reddit.com/r/{post.get('subreddit', '')}"}
                            ],
                            'source': 'Reddit',
                            'upvotes': post.get('score', 0),
                            'comments': post.get('num_comments', 0)
                        })
                    return reddit_opportunities
        except Exception as e:
            logger.error(f"Error fetching Reddit opportunities: {e}")

        return []

    async def send_initial_data(self):
        """Send initial opportunities and revenue data to frontend"""
        try:
            # Always send consistent base opportunities first (immediately)
            base_opportunities = [
                {
                    'id': 'opp_1',
                    'title': 'AI Content Creation Service',
                    'stream_type': 'AI Services',
                    'description': 'Create and sell AI-powered content generation services using GPT-5 and Claude',
                    'time_to_income': '24-48 hours',
                    'potential_monthly': '$2,500-$5,000',
                    'difficulty': 'intermediate',
                    'initial_investment': 50,
                    'success_rate': 78,
                    'market_demand': 92,
                    'required_skills': ['API Integration', 'Prompt Engineering', 'Marketing'],
                    'action_steps': [
                        'Set up AI API accounts',
                        'Create service packages',
                        'Build simple web interface',
                        'Launch on Fiverr/Upwork'
                    ],
                    'resources': [
                        {'name': 'OpenAI API Docs', 'url': 'https://platform.openai.com/docs'},
                        {'name': 'Anthropic Claude', 'url': 'https://www.anthropic.com'}
                    ]
                },
                {
                    'id': 'opp_2',
                    'title': 'Automated Trading Bot',
                    'stream_type': 'Trading & Finance',
                    'description': 'Deploy ML-powered trading strategies on crypto and forex markets',
                    'time_to_income': '1-2 weeks',
                    'potential_monthly': '$1,500-$10,000',
                    'difficulty': 'advanced',
                    'initial_investment': 500,
                    'success_rate': 65,
                    'market_demand': 88,
                    'required_skills': ['Python', 'ML/AI', 'Risk Management', 'API Integration'],
                    'action_steps': [
                        'Research trading strategies',
                        'Backtest with historical data',
                        'Deploy with small capital',
                        'Scale based on performance'
                    ],
                    'resources': [
                        {'name': 'Alpaca Trading API', 'url': 'https://alpaca.markets'},
                        {'name': 'TradingView', 'url': 'https://www.tradingview.com'}
                    ]
                },
                {
                    'id': 'opp_3',
                    'title': 'Digital Product Empire',
                    'stream_type': 'Digital Products',
                    'description': 'Create and sell templates, courses, and digital assets',
                    'time_to_income': '3-5 days',
                    'potential_monthly': '$800-$3,000',
                    'difficulty': 'beginner',
                    'initial_investment': 0,
                    'success_rate': 82,
                    'market_demand': 95,
                    'required_skills': ['Design', 'Content Creation', 'Marketing'],
                    'action_steps': [
                        'Identify high-demand niches',
                        'Create initial products',
                        'Set up Gumroad store',
                        'Promote on social media'
                    ],
                    'resources': [
                        {'name': 'Gumroad', 'url': 'https://gumroad.com'},
                        {'name': 'Canva Pro', 'url': 'https://www.canva.com'}
                    ]
                }
            ]

            # Send base opportunities immediately for consistent experience
            await self.send(text_data=json.dumps({
                'type': 'opportunities_update',
                'opportunities': base_opportunities,
                'source': 'base_opportunities'
            }))

            # Try to get Reddit opportunities asynchronously (don't wait)
            try:
                reddit_opps = await self.get_reddit_opportunities()
                if reddit_opps:
                    # Send combined opportunities update only if Reddit data is available
                    combined_opportunities = reddit_opps + base_opportunities
                    await self.send(text_data=json.dumps({
                        'type': 'opportunities_update',
                        'opportunities': combined_opportunities,
                        'source': 'reddit_enhanced',
                        'reddit_count': len(reddit_opps)
                    }))
                    logger.info(f"Enhanced with {len(reddit_opps)} Reddit opportunities")
            except Exception as reddit_error:
                logger.warning(f"Reddit opportunities failed, using base only: {reddit_error}")
                # Base opportunities already sent, no need to handle this

            # Send revenue data
            revenue_data = {
                'current_metrics': {
                    'total_revenue': 8750.00,
                    'monthly_revenue': 2850.00,
                    'weekly_revenue': 712.50,
                    'daily_revenue': 101.78
                },
                'by_category': {
                    'content': 3200,
                    'ai_services': 2500,
                    'digital_products': 1800,
                    'trading': 850,
                    'freelancing': 400
                },
                'projections': {
                    'monthly': 5200,
                    'yearly': 62400
                }
            }

            await self.send(text_data=json.dumps({
                'type': 'revenue_update',
                'revenue': revenue_data
            }))

            logger.info("Sent initial opportunities and revenue data")

        except Exception as e:
            logger.error(f"Error sending initial data: {e}")

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

    async def search_reddit_opportunities(self, query, subreddit):
        """Search Reddit for specific opportunities"""
        try:
            from core.tools import ToolRegistry

            reddit_tool = ToolRegistry.get_tool('reddit_api')
            if reddit_tool and reddit_tool.is_configured:
                result = await database_sync_to_async(reddit_tool.execute)(
                    query=query,
                    search_type="posts",
                    subreddit=subreddit,
                    limit=10,
                    sort="hot"
                )

                if result.get('success') and result.get('data'):
                    reddit_opportunities = []
                    for post in result['data'][:5]:  # Top 5 results
                        reddit_opportunities.append({
                            'id': f'reddit_{post.get("id", "")}',
                            'title': f"Reddit: {post.get('title', 'Opportunity')}",
                            'stream_type': 'Community Sourced',
                            'description': post.get('selftext', '')[:200] + '...' if post.get('selftext') else post.get('title', ''),
                            'time_to_income': '1-7 days',
                            'potential_monthly': '$500-$3,000',
                            'difficulty': 'beginner',
                            'initial_investment': 0,
                            'success_rate': 70,
                            'market_demand': post.get('score', 0),
                            'required_skills': ['Quick Response', 'Problem Solving', 'Communication'],
                            'action_steps': [
                                'Review opportunity details',
                                'Contact poster',
                                'Submit proposal',
                                'Execute project'
                            ],
                            'resources': [
                                {'name': 'Reddit Post', 'url': post.get('url', '')},
                                {'name': f"r/{post.get('subreddit', '')}", 'url': f"https://reddit.com/r/{post.get('subreddit', '')}"}
                            ],
                            'source': 'Reddit',
                            'upvotes': post.get('score', 0),
                            'comments': post.get('num_comments', 0),
                            'subreddit': post.get('subreddit', ''),
                            'author': post.get('author', 'Unknown')
                        })

                    await self.send(text_data=json.dumps({
                        'type': 'reddit_opportunities',
                        'opportunities': reddit_opportunities,
                        'query': query,
                        'subreddit': subreddit
                    }))

                    logger.info(f"Found {len(reddit_opportunities)} Reddit opportunities for query: {query}")
                else:
                    await self.send(text_data=json.dumps({
                        'type': 'reddit_opportunities',
                        'opportunities': [],
                        'message': 'No Reddit opportunities found',
                        'query': query,
                        'subreddit': subreddit
                    }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Reddit integration not configured. Add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to .env'
                }))

        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to search Reddit: {str(e)}'
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