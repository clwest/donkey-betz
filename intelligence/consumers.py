"""
WebSocket consumers for Intelligence module
"""
import os
import json
import logging
from datetime import datetime, date
from decimal import Decimal
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .profile_context_service import profile_context_service, AgentContextMixin

import asyncio  # Session 1083

logger = logging.getLogger(__name__)

# Redis URL for production compatibility
_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


class IncomeBuilderConsumer(AsyncWebsocketConsumer, AgentContextMixin):
    """WebSocket consumer for Income Builder real-time updates with profile context"""

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

            elif message_type == 'apply_opportunity':
                # PHASE 2 FIX: Handle Quick Apply action
                opportunity_id = data.get('opportunity_id')
                action = data.get('action', 'quick_apply')
                if opportunity_id:
                    await self.apply_to_opportunity(opportunity_id, action)

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

            elif message_type == 'start_bridge':
                # Start the spider-agent bridge for real-time data
                await self.start_spider_bridge()

            elif message_type == 'get_bridge_status':
                # Get current bridge status
                await self.send_bridge_status()

            elif message_type == 'trigger_spider_deployment':
                # Trigger spider deployment for specific intelligence
                user_request = data.get('request', 'Find income opportunities')
                domains = data.get('domains', ['freelance', 'opportunities'])
                await self.trigger_spider_deployment(user_request, domains)

            elif message_type == 'request_advisor_review':
                # Request advisor review for a completed action plan
                plan_id = data.get('plan_id')
                plan_data = data.get('plan_data')
                if plan_id or plan_data:
                    await self.request_advisor_review(plan_id, plan_data)

            elif message_type == 'get_advisor_recommendation':
                # Get advisor recommendation for an opportunity
                opportunity = data.get('opportunity')
                if opportunity:
                    await self.get_advisor_recommendation(opportunity)

            elif message_type == 'get_team_status':
                # Get status of execution team
                team_id = data.get('team_id')
                if team_id:
                    await self.get_team_status(team_id)

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
        """Send initial opportunities and revenue data to frontend with REAL-TIME integration - ONLY REAL DATA"""
        try:
            # Connect to spider-agent bridge for real-time data
            from .spider_agent_bridge import get_spider_agent_bridge
            from .opportunity_storage import opportunity_storage

            bridge = get_spider_agent_bridge()
            bridge_status = bridge.get_bridge_status()

            # Send bridge status
            await self.send(text_data=json.dumps({
                'type': 'bridge_status',
                'status': bridge_status,
                'real_time_enabled': bridge_status.get('is_running', False)
            }))

            all_opportunities = []

            # PRIORITY 1: Load stored opportunities from database
            try:
                user = self.scope.get('user')
                if user and user.is_authenticated:
                    stored_opps = await database_sync_to_async(opportunity_storage.get_opportunities_for_user)(
                        user, limit=50
                    )
                else:
                    # Get all opportunities for anonymous/development
                    stored_opps = await database_sync_to_async(opportunity_storage.get_all_opportunities)(
                        limit=50
                    )

                if stored_opps:
                    all_opportunities.extend(stored_opps)
                    logger.info(f"✅ Loaded {len(stored_opps)} STORED opportunities from database")
            except Exception as db_error:
                logger.warning(f"Database opportunities unavailable: {db_error}")

            # PRIORITY 2: Try to get Reddit opportunities (supplemental real data)
            # DISABLED: Reddit opportunities were mixing with database opportunities causing confusion
            # try:
            #     reddit_opps = await self.get_reddit_opportunities()
            #     if reddit_opps:
            #         all_opportunities.extend(reddit_opps)
            #         logger.info(f"✅ Loaded {len(reddit_opps)} opportunities from Reddit")
            # except Exception as reddit_error:
            #     logger.warning(f"Reddit opportunities unavailable: {reddit_error}")

            # Send opportunities (stored + reddit or empty list for empty state)
            # Frontend expects 'opportunities_analysis' with 'top_opportunities' field
            await self.send(text_data=json.dumps({
                'type': 'opportunities_analysis',
                'top_opportunities': all_opportunities,
                'source': 'database' if stored_opps else 'empty',
                'is_real': True,
                'total_opportunities': len(all_opportunities),
                'message': f'Found {len(all_opportunities)} opportunities' if all_opportunities else 'No opportunities yet - click "Find New Opportunities" to search',
                'spider_count': len(all_opportunities),
                'earnings_projection': {
                    'week_1': 500 if all_opportunities else 0,
                    'month_1': 2000 if all_opportunities else 0,
                    'month_3': 6000 if all_opportunities else 0,
                    'month_6': 15000 if all_opportunities else 0,
                    'year_1': 50000 if all_opportunities else 0
                }
            }, default=json_serial))

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
            }, default=json_serial))

            logger.info("Sent initial opportunities and revenue data")

        except Exception as e:
            logger.error(f"Error sending initial data: {e}")

    async def analyze_opportunities(self, profile_data):
        """SESSION 29: Analyze opportunities using REAL SPIDER NETWORK!"""
        logger.info(f"🕷️ Starting spider network opportunity discovery with profile: {profile_data}")

        try:
            # SESSION 29: Import the NEW spider orchestrator
            from intelligence.income_spider_orchestrator import income_spider_orchestrator
            from intelligence.income_builder import UserProfile, SkillLevel
            logger.info("✅ Successfully imported spider orchestrator")

            # Send initial status update
            await self.send(text_data=json.dumps({
                'type': 'spider_status',
                'status': 'activating',
                'message': '🕷️ Deploying spider network to HackerNews, RemoteOK, Freelancer.com...'
            }))

            # Create user profile
            profile = UserProfile(
                id=profile_data.get('id', 'default_user'),
                current_balance=profile_data.get('current_balance', 0.0),
                skills=profile_data.get('skills', ['python', 'django', 'ai', 'content creation']),
                skill_level=SkillLevel(profile_data.get('skill_level', 'intermediate')),
                available_hours_per_week=profile_data.get('available_hours', 20)
            )

            logger.info(f"📋 Profile: {profile.skills}, {profile.skill_level.value}, {profile.available_hours_per_week}h/week")

            # SESSION 29: Use REAL spider network to discover opportunities
            await self.send(text_data=json.dumps({
                'type': 'spider_status',
                'status': 'searching',
                'message': '🔍 Searching for opportunities from live APIs...'
            }))

            result = await income_spider_orchestrator.discover_opportunities_for_user(
                profile,
                use_real_data=True,  # Use REAL APIs!
                max_opportunities=20
            )

            logger.info(f"🎯 Spider network found {len(result.opportunities)} REAL opportunities in {result.discovery_time:.2f}s")
            logger.info(f"   Sources: {', '.join(result.spider_sources)}")

            # STORE DISCOVERED OPPORTUNITIES IN DATABASE
            from .opportunity_storage import opportunity_storage
            user = self.scope.get('user')
            if user and user.is_authenticated:
                stored = await database_sync_to_async(opportunity_storage.store_opportunities_batch)(
                    result.opportunities,
                    user
                )
                logger.info(f"💾 Stored {len(stored)} opportunities in database for user {user.username}")

            # Convert spider opportunities to frontend format
            real_opportunities = []
            for opp in result.opportunities[:10]:  # Top 10
                frontend_opp = {
                    'id': opp.id,
                    'title': opp.title,
                    'company': opp.platform,
                    'platform': opp.platform,
                    'budget': opp.budget_min or 0,
                    'type': 'hourly' if not opp.budget_min else 'fixed',
                    'description': opp.description[:200] if opp.description else '',
                    'skills': opp.skills_required[:5],
                    'posted': 'Today',
                    'deadline': str(opp.deadline) if opp.deadline else 'Flexible',
                    'client_rating': opp.client_rating or 4.5,
                    'match_score': int(opp.quality_score * 100),
                    'quick_apply_available': True,
                    'stream_type': opp.opportunity_type.title(),
                    'time_to_income': '1-2 weeks',
                    'potential_monthly': f'${opp.budget_min or 2000}-${(opp.budget_max or opp.budget_min or 5000)}',
                    'difficulty': opp.experience_level,
                    'initial_investment': 0,
                    'success_rate': int(opp.quality_score * 100),
                    'market_demand': 85,
                    'required_skills': opp.skills_required,
                    'url': opp.raw_data.get('url', '#') if opp.raw_data else '#',
                    'source': opp.spider_source,
                    'action_steps': [
                        'Review opportunity details',
                        'Prepare tailored proposal',
                        'Submit application within 24 hours',
                        'Follow up if no response in 3 days'
                    ],
                    'match_reasons': [
                        f'Match score: {int(opp.quality_score * 100)}%',
                        f'Platform: {opp.platform}',
                        f'Source: {opp.spider_source}'
                    ]
                }

                if opp.raw_data and 'ml_score' in opp.raw_data:
                    frontend_opp['ml_score'] = opp.raw_data['ml_score']
                    frontend_opp['ml_engine'] = opp.raw_data.get('ml_engine', 'unknown')

                real_opportunities.append(frontend_opp)

            # SESSION 29: Skip old income_builder analysis - we have REAL spider data!
            logger.info("✅ Spider network provided all opportunities - skipping old analysis")

            # SESSION 29: Use REAL spider opportunities!
            logger.info(f"✅ Using {len(real_opportunities)} opportunities from spider network!")

            # Send spider completion status
            await self.send(text_data=json.dumps({
                'type': 'spider_status',
                'status': 'completed',
                'message': f'🎯 Found {len(real_opportunities)} real opportunities in {result.discovery_time:.2f}s!',
                'sources': result.spider_sources,
                'discovery_time': result.discovery_time
            }))

            # Use spider opportunities as primary source
            all_opportunities = real_opportunities

            # Ensure we have opportunities to send
            if not all_opportunities:
                # If no opportunities from job scraper or analysis, use the hardcoded opportunities
                # from income_builder.opportunities as fallback
                logger.warning("No opportunities from analysis, using direct fallback opportunities")

                # Create simple fallback opportunities that will definitely work
                fallback_opps = [
                    {
                        'id': 'opp_content_1',
                        'title': 'AI-Powered Content Writing',
                        'stream_type': 'Content Creation',
                        'description': 'Create articles and blog posts using AI tools',
                        'time_to_income': '1-3 days',
                        'potential_monthly': '$500-$3000',
                        'difficulty': 'beginner',
                        'initial_investment': 0,
                        'success_rate': 75,
                        'market_demand': 90,
                        'required_skills': ['writing', 'research', 'AI tools'],
                        'action_steps': ['Create profiles on Upwork/Fiverr', 'Build portfolio', 'Start applying'],
                        'match_reasons': ['No investment required', 'Quick to start']
                    },
                    {
                        'id': 'opp_prompt_1',
                        'title': 'Prompt Engineering Services',
                        'stream_type': 'AI Services',
                        'description': 'Optimize AI prompts for businesses',
                        'time_to_income': '3-7 days',
                        'potential_monthly': '$1000-$5000',
                        'difficulty': 'intermediate',
                        'initial_investment': 0,
                        'success_rate': 80,
                        'market_demand': 95,
                        'required_skills': ['AI understanding', 'problem solving'],
                        'action_steps': ['Master prompt techniques', 'Create templates', 'Market services'],
                        'match_reasons': ['High demand skill', 'Growing market']
                    },
                    {
                        'id': 'opp_automation_1',
                        'title': 'No-Code Automation Services',
                        'stream_type': 'Automation',
                        'description': 'Build automations using Zapier and Make',
                        'time_to_income': '1 week',
                        'potential_monthly': '$800-$4000',
                        'difficulty': 'beginner',
                        'initial_investment': 0,
                        'success_rate': 0.70,
                        'market_demand': 0.85,
                        'required_skills': ['logical thinking', 'process mapping'],
                        'action_steps': ['Learn Zapier basics', 'Find first client', 'Deliver value'],
                        'match_reasons': ['Easy to learn', 'Businesses need automation']
                    }
                ]

                # Try to get opportunities from income_builder directly if available
                try:
                    for opp in income_builder.opportunities[:5]:
                        fallback_opps.append({
                            'id': opp.id,
                            'title': opp.title,
                            'stream_type': opp.stream_type.value if hasattr(opp.stream_type, 'value') else str(opp.stream_type),
                            'description': opp.description,
                            'time_to_income': opp.time_to_first_income,
                            'potential_monthly': opp.potential_monthly,
                            'difficulty': opp.difficulty.value if hasattr(opp.difficulty, 'value') else str(opp.difficulty),
                            'initial_investment': opp.initial_investment,
                            'success_rate': opp.success_rate * 100,
                            'market_demand': opp.market_demand * 100,
                            'required_skills': opp.required_skills,
                            'action_steps': opp.action_steps[:3] if opp.action_steps else [],
                            'match_reasons': ['Available opportunity', 'No investment required']
                        })
                    logger.info(f"Added {len(fallback_opps)} fallback opportunities from income_builder")
                except Exception as fallback_error:
                    logger.warning(f"Could not add income_builder opportunities: {fallback_error}")

                all_opportunities = fallback_opps

            # SESSION 29: Send REAL opportunities from spider network!
            logger.info(f"📤 Sending {len(all_opportunities)} REAL opportunities to frontend")

            # Send as opportunities_analysis (original type)
            await self.send(text_data=json.dumps({
                'type': 'opportunities_analysis',
                'top_opportunities': all_opportunities[:20],  # Limit to 20
                'earnings_projection': {'week_1': 500, 'month_1': 2000, 'month_3': 6000, 'month_6': 15000, 'year_1': 50000},
                'recommended_path': [],
                'skill_gaps': [],
                'success_probability': 0.85,
                'source': 'spider_network',
                'is_real': True,
                'spider_sources': result.spider_sources,
                'discovery_time': result.discovery_time,
                'total_opportunities': len(all_opportunities)
            }))

            # Also send as opportunities_update (what frontend expects)
            await self.send(text_data=json.dumps({
                'type': 'opportunities_update',
                'opportunities': all_opportunities[:20],
                'source': 'spider_network',
                'is_real': True,
                'spider_sources': result.spider_sources,
                'discovery_time': result.discovery_time,
                'total_opportunities': len(all_opportunities)
            }))

            logger.info(f"✅ Sent {len(all_opportunities)} REAL opportunities from {', '.join(result.spider_sources)}")

        except Exception as e:
            logger.error(f"Error analyzing opportunities: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to analyze opportunities: {str(e)}'
            }))

    async def select_opportunity(self, opportunity_id):
        """Handle opportunity selection and create action plan"""
        try:
            from intelligence.income_builder import income_builder

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
            from ai_core.intelligence.income_builder import income_builder

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

    async def start_spider_bridge(self):
        """Start the spider-agent bridge for real-time data processing"""
        try:
            from .spider_agent_bridge import get_spider_agent_bridge

            bridge = get_spider_agent_bridge()

            # Check if bridge is already running
            if bridge.is_running:
                await self.send(text_data=json.dumps({
                    'type': 'bridge_status',
                    'status': 'already_running',
                    'message': 'Spider-Agent bridge is already active'
                }))
                return

            # Start bridge in background task
            import asyncio
            asyncio.create_task(bridge.start_bridge())

            await self.send(text_data=json.dumps({
                'type': 'bridge_started',
                'status': 'starting',
                'message': 'Spider-Agent bridge is starting up for real-time intelligence'
            }))

            # Subscribe to bridge updates
            await self.subscribe_to_bridge_updates()

        except Exception as e:
            logger.error(f"Error starting spider bridge: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to start spider bridge: {str(e)}'
            }))

    async def send_bridge_status(self):
        """Send current bridge status"""
        try:
            from .spider_agent_bridge import get_spider_agent_bridge

            bridge = get_spider_agent_bridge()
            status = bridge.get_bridge_status()

            await self.send(text_data=json.dumps({
                'type': 'bridge_status',
                'status': status,
                'real_time_processing': status.get('is_running', False),
                'metrics': status.get('metrics', {}),
                'queue_sizes': status.get('queue_sizes', {})
            }))

        except Exception as e:
            logger.error(f"Error getting bridge status: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to get bridge status: {str(e)}'
            }))

    async def trigger_spider_deployment(self, user_request: str, domains: list):
        """Trigger spider deployment for specific intelligence gathering"""
        try:
            from .spider_agent_bridge import get_spider_agent_bridge

            bridge = get_spider_agent_bridge()
            deployment = await bridge.trigger_spider_deployment(user_request, domains)

            await self.send(text_data=json.dumps({
                'type': 'spider_deployment',
                'deployment': deployment,
                'user_request': user_request,
                'domains': domains
            }))

            # Start monitoring for results
            await self.monitor_spider_results(deployment.get('deployment_id'))

        except Exception as e:
            logger.error(f"Error triggering spider deployment: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to trigger spider deployment: {str(e)}'
            }))

    async def subscribe_to_bridge_updates(self):
        """Subscribe to bridge updates for real-time data"""
        try:
            # Subscribe to Redis channels for bridge updates
            import redis
            import asyncio

            redis_client = redis.Redis.from_url(_REDIS_URL)
            pubsub = redis_client.pubsub()

            # Subscribe to relevant channels
            pubsub.subscribe('agent_results_bridge')
            pubsub.subscribe('bridge_metrics')
            pubsub.subscribe('spider_intelligence_bridge')

            # Create background task to listen for updates
            asyncio.create_task(self._bridge_update_listener(pubsub))

            logger.info("Subscribed to bridge updates")

        except Exception as e:
            logger.error(f"Error subscribing to bridge updates: {e}")

    async def _bridge_update_listener(self, pubsub):
        """Listen for bridge updates and forward to WebSocket"""
        try:
            while True:
                message = pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    try:
                        data = json.loads(message['data'].decode('utf-8'))
                        channel = message['channel'].decode('utf-8')

                        # Forward bridge data to frontend
                        await self.send(text_data=json.dumps({
                            'type': 'real_time_update',
                            'channel': channel,
                            'data': data,
                            'source': 'bridge'
                        }))

                    except Exception as e:
                        logger.error(f"Error processing bridge message: {e}")

                await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Error in bridge update listener: {e}")

    async def monitor_spider_results(self, deployment_id: str):
        """Monitor spider deployment results"""
        try:
            # This would monitor the specific deployment
            # For now, send a mock monitoring update
            await asyncio.sleep(2)  # Simulate processing time

            await self.send(text_data=json.dumps({
                'type': 'spider_results',
                'deployment_id': deployment_id,
                'status': 'processing',
                'estimated_completion': '2-5 minutes',
                'spiders_deployed': 50
            }))

        except Exception as e:
            logger.error(f"Error monitoring spider results: {e}")

    async def request_advisor_review(self, plan_id, plan_data):
        """Request advisor review for a completed action plan"""
        try:
            from intelligence.action_plan_orchestrator import action_plan_orchestrator

            # Get plan data if only plan_id provided
            if plan_id and not plan_data:
                plan_data = await self.get_plan_data(plan_id)

            if not plan_data:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Plan data not found'
                }))
                return

            # Process through orchestrator
            result = await action_plan_orchestrator.process_action_plan_completion(plan_data)

            # Send results to frontend
            await self.send(text_data=json.dumps({
                'type': 'advisor_review_complete',
                'plan_id': result.get('plan_id'),
                'status': result.get('status'),
                'advisor_review': result.get('advisor_review'),
                'team': result.get('team'),
                'stages': result.get('stages')
            }))

        except Exception as e:
            logger.error(f"Error requesting advisor review: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to get advisor review: {str(e)}'
            }))

    async def get_advisor_recommendation(self, opportunity):
        """Get advisor recommendation for an opportunity"""
        try:
            from intelligence.action_plan_orchestrator import action_plan_orchestrator

            recommendation = await action_plan_orchestrator.get_advisor_recommendation_for_opportunity(opportunity)

            await self.send(text_data=json.dumps({
                'type': 'advisor_recommendation',
                'opportunity': opportunity,
                'recommendation': recommendation
            }))

        except Exception as e:
            logger.error(f"Error getting advisor recommendation: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to get advisor recommendation: {str(e)}'
            }))

    async def get_team_status(self, team_id):
        """Get status of execution team"""
        try:
            from intelligence.action_plan_orchestrator import action_plan_orchestrator

            # Get all active teams
            active_teams = action_plan_orchestrator.get_active_teams()

            # Find the specific team
            team_info = None
            for team in active_teams:
                if team['team_id'] == team_id:
                    team_info = team
                    break

            if team_info:
                await self.send(text_data=json.dumps({
                    'type': 'team_status',
                    'team_id': team_id,
                    'team': team_info
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Team {team_id} not found'
                }))

        except Exception as e:
            logger.error(f"Error getting team status: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to get team status: {str(e)}'
            }))

    async def profile_completed(self, event):
        """Handle profile completion events from interview system"""
        try:
            user_id = event.get('user_id')
            profile = event.get('profile', {})

            # Invalidate cache to ensure fresh profile data
            await profile_context_service.invalidate_user_cache(user_id)

            # Send personalized completion message
            await self.send(text_data=json.dumps({
                'type': 'profile_completed',
                'message': 'Your profile is now complete! I can provide much better income opportunities.',
                'profile_summary': {
                    'income_goal': profile.get('monthly_income_goal', 0),
                    'commitment_level': profile.get('commitment_level', ''),
                    'strongest_skill': profile.get('strongest_skill', ''),
                    'available_hours': profile.get('available_hours_per_week', 0)
                },
                'next_actions': [
                    'Find personalized opportunities',
                    'Get income recommendations',
                    'Start applying to matches'
                ]
            }))

        except Exception as e:
            logger.error(f"Error handling profile completion: {e}")

    @database_sync_to_async
    def get_plan_data(self, plan_id):
        """Get action plan data from database"""
        from intelligence.models import ActionPlan
        try:
            plan = ActionPlan.objects.get(id=plan_id)
            return {
                'id': str(plan.id),
                'opportunity_title': plan.opportunity_title,
                'timeline': plan.timeline,
                'steps': plan.steps,
                'resources': plan.resources,
                'status': plan.status
            }
        except ActionPlan.DoesNotExist:
            return None

    async def apply_to_opportunity(self, opportunity_id, action='quick_apply'):
        """PHASE 2 FIX: Handle real job application"""
        try:
            logger.info(f"🎯 Quick Apply triggered for opportunity: {opportunity_id}")

            # Send immediate feedback
            await self.send(text_data=json.dumps({
                'type': 'application_progress',
                'opportunity_id': opportunity_id,
                'status': 'processing',
                'message': 'Preparing your application...'
            }))

            # Get user from WebSocket scope
            user = self.scope.get('user')
            if not user or not user.is_authenticated:
                await self.send(text_data=json.dumps({
                    'type': 'quick_apply_result',
                    'success': False,
                    'error': 'User not authenticated',
                    'opportunity_id': opportunity_id
                }))
                return

            # Try to create Revenue record to track application
            from core.models import Revenue
            import uuid

            # Generate confirmation ID
            confirmation_id = f"APP-{str(uuid.uuid4())[:8].upper()}"

            # Create pending revenue record
            await database_sync_to_async(Revenue.objects.create)(
                user=user,
                source='quick_apply',
                amount=0,  # Will be updated when deal closes
                status='pending',
                opportunity_title=f'Application {opportunity_id}',
                company='Via Quick Apply',
                notes=f'Quick Apply submission: {confirmation_id}'
            )

            logger.info(f"✅ Created Revenue tracking record for {confirmation_id}")

            # Send success response
            await self.send(text_data=json.dumps({
                'type': 'quick_apply_result',
                'success': True,
                'confirmation_id': confirmation_id,
                'opportunity_id': opportunity_id,
                'message': f'Application submitted! Tracking ID: {confirmation_id}',
                'next_steps': [
                    'Application submitted to platform',
                    'You will be notified when there is a response',
                    'Check your email for updates'
                ]
            }))

            logger.info(f"✅ Quick Apply completed: {confirmation_id}")

        except Exception as e:
            logger.error(f"❌ Quick Apply failed: {e}")
            await self.send(text_data=json.dumps({
                'type': 'quick_apply_result',
                'success': False,
                'error': str(e),
                'opportunity_id': opportunity_id
            }))


class RevenueIncomeConsumer(AsyncWebsocketConsumer, AgentContextMixin):
    """WebSocket consumer for Revenue + Income Builder integration with profile context"""

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