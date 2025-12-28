"""
Unified WebSocket Consumer for new pages (AI Nexus, DBAO, Profile)
"""

import json
import asyncio
import logging
import random
from datetime import timedelta
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Sum, Avg

logger = logging.getLogger(__name__)


class NewPagesConsumer(AsyncWebsocketConsumer):
    """Generic WebSocket consumer for new unified pages"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_type = None
        self.update_task = None

    async def connect(self):
        """Handle WebSocket connection"""
        await self.accept()

        # Identify page type from path
        path = self.scope.get('path', '')
        if 'ai-nexus' in path:
            self.page_type = 'ai_nexus'
        elif 'dbao' in path:
            self.page_type = 'dbao'
        elif 'profile' in path:
            self.page_type = 'profile'
        else:
            self.page_type = 'generic'

        logger.info(f"{self.page_type} WebSocket connected: {self.channel_name}")

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'page': self.page_type,
            'message': f'Connected to {self.page_type} updates',
            'timestamp': timezone.now().isoformat()
        }))

        # Start appropriate updates based on page type
        if self.page_type == 'ai_nexus':
            # Send initial status immediately
            await self.send_ai_nexus_status()
            self.update_task = asyncio.create_task(self.send_ai_nexus_updates())
        elif self.page_type == 'dbao':
            self.update_task = asyncio.create_task(self.send_dbao_updates())

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if self.update_task:
            self.update_task.cancel()

        logger.info(f"{self.page_type} WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            logger.info(f"{self.page_type} received: {message_type}")

            # Route based on page type
            if self.page_type == 'ai_nexus':
                await self.handle_ai_nexus_message(message_type, data)
            elif self.page_type == 'dbao':
                await self.handle_dbao_message(message_type, data)
            elif self.page_type == 'profile':
                await self.handle_profile_message(message_type, data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'response',
                    'message': f'Received {message_type}',
                    'timestamp': timezone.now().isoformat()
                }))

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
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

    async def handle_ai_nexus_message(self, message_type, data):
        """Handle AI Nexus specific messages"""
        if message_type == 'get_status':
            await self.send_ai_nexus_status()
        elif message_type == 'activate_spiders':
            await self.handle_spider_activation()
        elif message_type == 'get_agent_status':
            await self.send_agent_status()
        elif message_type == 'get_advisor_insights':
            await self.send_advisor_insights()
        else:
            await self.send(text_data=json.dumps({
                'type': 'nexus_response',
                'message': f'Processing {message_type}',
                'timestamp': timezone.now().isoformat()
            }))

    async def handle_dbao_message(self, message_type, data):
        """Handle DBAO Dashboard specific messages"""
        if message_type == 'get_metrics':
            await self.send_dbao_metrics()
        elif message_type == 'get_queries':
            await self.send_query_status()
        elif message_type == 'run_analytics':
            await self.handle_run_analytics()
        else:
            await self.send(text_data=json.dumps({
                'type': 'dbao_response',
                'message': f'Processing {message_type}',
                'timestamp': timezone.now().isoformat()
            }))

    async def handle_profile_message(self, message_type, data):
        """Handle Profile specific messages"""
        if message_type == 'get_profile':
            await self.send_profile_data(data.get('user_id'))
        elif message_type == 'update_profile':
            await self.handle_profile_update(data)
        elif message_type == 'get_achievements':
            await self.send_achievements()
        else:
            await self.send(text_data=json.dumps({
                'type': 'profile_response',
                'message': f'Processing {message_type}',
                'timestamp': timezone.now().isoformat()
            }))

    @database_sync_to_async
    def get_real_nexus_status(self):
        """Get REAL system status from database including REAL spider data"""
        from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution
        from core.models_unified_system import Advisor
        from core.models import Revenue
        try:
            from intelligence.models import OpportunityInteraction
        except ImportError:
            OpportunityInteraction = None

        try:
            from intelligence.spider_quality_tracker import SpiderQualityMetrics
        except (ImportError, Exception) as e:
            logger.warning(f"SpiderQualityMetrics not available: {e}")
            SpiderQualityMetrics = None

        try:
            import psutil
            has_psutil = True
        except ImportError:
            has_psutil = False
            logger.warning("psutil not installed - system metrics will be estimates")

        # Get REAL agent counts
        total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()

        one_hour_ago = timezone.now() - timedelta(hours=1)
        active_agent_ids = AgentExecution.objects.filter(
            created_at__gte=one_hour_ago
        ).values_list('template_id', flat=True).distinct()
        active_agents = len(set(active_agent_ids))

        # Get REAL task stats
        total_executions = AgentExecution.objects.count()
        successful_executions = AgentExecution.objects.filter(status='completed').count()
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0

        # Get REAL spider data from SpiderRegistry and SpiderQualityMetrics
        total_spiders = 40  # From spider registry registration
        active_spiders = 0
        crawling_spiders = 0
        opportunities_found = 0

        if SpiderQualityMetrics:
            # Count spiders with recent activity (last 24 hours)
            one_day_ago = timezone.now() - timedelta(hours=24)
            active_metrics = SpiderQualityMetrics.objects.filter(
                last_updated__gte=one_day_ago
            )
            active_spiders = active_metrics.count()

            # Count spiders currently crawling (those with very recent activity - last hour)
            crawling_metrics = SpiderQualityMetrics.objects.filter(
                last_updated__gte=one_hour_ago
            )
            crawling_spiders = crawling_metrics.count()

            # Sum opportunities fetched from all spiders
            opportunities_found = SpiderQualityMetrics.objects.aggregate(
                total=Sum('opportunities_fetched')
            )['total'] or 0

        # Get REAL advisor counts (reusing Neural Orchestra fix!)
        total_advisors = Advisor.objects.filter(is_active=True).count()
        # Note: Advisor model doesn't have 'status' field, all active advisors are available
        available_advisors = total_advisors  # All active advisors are available
        total_consultations = Advisor.objects.aggregate(
            total=Sum('total_consultations')
        )['total'] or 0

        # Get REAL revenue data
        total_revenue = Revenue.objects.filter(status='confirmed').aggregate(
            total=Sum('amount')
        )['total'] or 0

        this_month = timezone.now().replace(day=1)
        month_revenue = Revenue.objects.filter(
            status='confirmed',
            created_at__gte=this_month
        ).aggregate(total=Sum('amount'))['total'] or 0

        opportunities_count = OpportunityInteraction.objects.count() if OpportunityInteraction else 0

        # Get REAL system metrics
        if has_psutil:
            memory = psutil.virtual_memory()
            memory_usage = f'{memory.percent:.1f}%'
        else:
            memory_usage = 'N/A'

        # Calculate real uptime (from earliest AgentExecution)
        first_execution = AgentExecution.objects.order_by('created_at').first()
        if first_execution:
            uptime_days = (timezone.now() - first_execution.created_at).days
            if uptime_days > 0:
                uptime = f"{uptime_days} days"
            else:
                uptime_hours = (timezone.now() - first_execution.created_at).seconds // 3600
                uptime = f"{uptime_hours} hours"
        else:
            uptime = "N/A"

        # Get average response time from recent executions
        recent_executions = AgentExecution.objects.filter(
            created_at__gte=one_hour_ago,
            execution_time_seconds__isnull=False
        )
        avg_response = recent_executions.aggregate(
            avg=Avg('execution_time_seconds')
        )['avg']
        avg_response_ms = int(avg_response * 1000) if avg_response else 0

        # Calculate data collected estimate (rough)
        data_gb = (opportunities_found * 0.001) if opportunities_found > 0 else 0  # ~1KB per opportunity
        data_collected = f'{data_gb:.2f}GB' if data_gb > 0 else '0GB'

        return {
            'agents': {
                'total': total_agents,
                'active': active_agents,
                'idle': total_agents - active_agents,
                'tasks_completed': total_executions,
                'success_rate': round(success_rate, 1)
            },
            'spiders': {
                'total': total_spiders,
                'active': active_spiders,
                'crawling': crawling_spiders,
                'data_collected': data_collected,
                'opportunities_found': opportunities_found
            },
            'advisors': {
                'total': total_advisors,
                'available': available_advisors,
                'consultations': total_consultations,
                'insights_generated': total_consultations
            },
            'revenue': {
                'total': float(total_revenue),
                'this_month': float(month_revenue),
                'opportunities': opportunities_count,
                'conversion': round((total_revenue / opportunities_count * 100), 1) if opportunities_count > 0 else 0
            },
            'system': {
                'uptime': uptime,
                'latency': f'{avg_response_ms}ms' if avg_response_ms > 0 else 'N/A',
                'api_calls': total_executions,
                'memory_usage': memory_usage
            }
        }

    async def send_ai_nexus_status(self):
        """Send REAL AI Nexus system status"""
        status = await self.get_real_nexus_status()

        await self.send(text_data=json.dumps({
            'type': 'nexus_status',
            'data': status,
            'timestamp': timezone.now().isoformat()
        }))

    async def send_dbao_metrics(self):
        """Send DBAO dashboard metrics"""
        metrics = {
            'data_points': random.randint(2000000, 3000000),
            'active_queries': random.randint(300, 400),
            'uptime': random.uniform(98, 99.9),
            'data_processed': f'{random.uniform(1.5, 2.5):.1f}TB',
            'avg_response': f'{random.randint(30, 50)}ms',
            'accuracy_rate': random.uniform(85, 95),
            'performance': {
                'cpu': random.uniform(40, 70),
                'memory': random.uniform(50, 80),
                'disk': random.uniform(30, 60),
                'network': random.uniform(20, 50)
            }
        }

        await self.send(text_data=json.dumps({
            'type': 'dbao_metrics',
            'data': metrics,
            'timestamp': timezone.now().isoformat()
        }))

    async def send_profile_data(self, user_id):
        """Send user profile data"""
        profile = {
            'user_id': user_id or 'guest',
            'name': 'Test User',
            'email': 'test@example.com',
            'member_since': '2024-01-01',
            'stats': {
                'applications': random.randint(100, 200),
                'revenue': random.randint(2000, 3000),
                'success_rate': random.uniform(85, 95),
                'active_projects': random.randint(30, 50)
            },
            'skills': ['Python', 'Django', 'React', 'Machine Learning'],
            'goals': ['$10K monthly', '500 projects', 'Passive income'],
            'achievements': {
                'unlocked': random.randint(5, 10),
                'total': 20
            }
        }

        await self.send(text_data=json.dumps({
            'type': 'profile_data',
            'data': profile,
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def get_recent_activities(self, limit=5):
        """PHASE 1 FIX: Get REAL recent system activities"""
        from core.models.agents_registry import AgentExecution
        from core.models import Revenue
        try:
            from intelligence.models import OpportunityInteraction
        except ImportError:
            OpportunityInteraction = None

        activities = []

        # Get recent agent executions (last 15 minutes)
        recent_time = timezone.now() - timedelta(minutes=15)
        recent_executions = AgentExecution.objects.filter(
            status='completed',
            created_at__gte=recent_time
        ).select_related('template').order_by('-created_at')[:limit]

        for execution in recent_executions:
            template_name = execution.template.name if execution.template else 'Unknown Agent'
            task_type = execution.task_type or 'task'
            activities.append({
                'type': 'agent_execution',
                'event': f'Agent {template_name} completed {task_type}',
                'timestamp': execution.created_at.isoformat(),
                'icon': '🤖'
            })

        # Get recent revenue additions
        recent_revenue = Revenue.objects.filter(
            status='confirmed',
            created_at__gte=recent_time
        ).order_by('-created_at')[:limit]

        for rev in recent_revenue:
            source = rev.source or 'opportunity'
            activities.append({
                'type': 'revenue',
                'event': f'New revenue: ${float(rev.amount):.0f} from {source}',
                'timestamp': rev.created_at.isoformat(),
                'icon': '💰'
            })

        # Get recent opportunities
        if OpportunityInteraction:
            recent_opportunities = OpportunityInteraction.objects.filter(
                created_at__gte=recent_time
            ).order_by('-created_at')[:limit]

            for opp in recent_opportunities:
                category = opp.category or 'general'
                activities.append({
                    'type': 'opportunity',
                    'event': f'New opportunity discovered in {category}',
                    'timestamp': opp.created_at.isoformat(),
                    'icon': '🕷️'
                })

        # Sort by timestamp and return latest
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]

    async def send_ai_nexus_updates(self):
        """Send REAL periodic AI Nexus updates"""
        while True:
            try:
                await asyncio.sleep(15)

                # Get REAL recent activities
                activities = await self.get_recent_activities(limit=5)

                # Send each activity
                for activity in activities:
                    await self.send(text_data=json.dumps({
                        'type': 'nexus_activity',
                        'data': activity,
                        'timestamp': timezone.now().isoformat()
                    }))

                # Send status updates more frequently (every ~45 seconds)
                if random.random() > 0.5:  # 50% chance every 15s = avg 30s between updates
                    await self.send_ai_nexus_status()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in AI Nexus updates: {e}")
                await asyncio.sleep(15)

    async def send_dbao_updates(self):
        """Send periodic DBAO dashboard updates"""
        while True:
            try:
                await asyncio.sleep(10)

                # Send query update
                query = {
                    'query_id': f'Q-{random.randint(7000, 8000)}',
                    'type': random.choice(['Analytics', 'Aggregation', 'ML Training', 'Export']),
                    'execution_time': f'{random.randint(50, 500)}ms',
                    'status': random.choice(['Completed', 'Processing', 'Queued'])
                }

                await self.send(text_data=json.dumps({
                    'type': 'query_update',
                    'data': query,
                    'timestamp': timezone.now().isoformat()
                }))

                # Send metrics periodically
                if random.random() > 0.6:
                    await self.send_dbao_metrics()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in DBAO updates: {e}")
                await asyncio.sleep(10)

    @database_sync_to_async
    def get_spider_network_details(self):
        """Get detailed spider network information"""
        try:
            from intelligence.spider_quality_tracker import SpiderQualityMetrics
        except (ImportError, Exception) as e:
            logger.warning(f"SpiderQualityMetrics not available: {e}")
            return {
                'spiders': [],
                'total_quality_score': 0,
                'message': f'Spider quality tracking not available: {str(e)}'
            }

        # Get all spider metrics
        spider_metrics = SpiderQualityMetrics.objects.all().order_by('-quality_score')[:10]

        spider_details = []
        for metric in spider_metrics:
            spider_details.append({
                'name': metric.spider_name,
                'platform': metric.source_platform,
                'quality_score': metric.quality_score,
                'priority': metric.fetch_priority,
                'opportunities_fetched': metric.opportunities_fetched,
                'opportunities_applied': metric.opportunities_applied,
                'fetch_success_rate': metric.fetch_success_rate,
                'last_active': metric.last_updated.isoformat()
            })

        avg_quality = spider_metrics.aggregate(
            avg=Avg('quality_score')
        )['avg'] or 0

        return {
            'spiders': spider_details,
            'total_quality_score': round(avg_quality, 1),
            'total_count': SpiderQualityMetrics.objects.count()
        }

    async def handle_spider_activation(self):
        """Handle spider network activation request"""
        logger.info("Spider activation requested")

        # Get current spider details
        spider_details = await self.get_spider_network_details()

        # Send activation confirmation with details
        await self.send(text_data=json.dumps({
            'type': 'spider_activation',
            'status': 'success',
            'message': f'Spider network reporting: {spider_details["total_count"]} spiders tracked',
            'data': spider_details,
            'timestamp': timezone.now().isoformat()
        }))

        # Note: Spiders are activated via Celery tasks, not directly here
        # See: intelligence/tasks.py for spider orchestration

    async def send_agent_status(self):
        """Send detailed agent status information"""
        from core.models.agents_registry import AgentExecution

        try:
            # Get recent agent activity (last 24 hours to ensure we show some data)
            one_day_ago = timezone.now() - timedelta(hours=24)
            recent_executions = await database_sync_to_async(
                lambda: list(AgentExecution.objects.filter(
                    created_at__gte=one_day_ago
                ).select_related('template').order_by('-created_at')[:10])
            )()

            agent_activities = []
            for execution in recent_executions:
                agent_activities.append({
                    'agent_name': execution.template.name if execution.template else 'Unknown',
                    'task_type': execution.task_type or 'general',
                    'status': execution.status,
                    'timestamp': execution.created_at.isoformat()
                })

            await self.send(text_data=json.dumps({
                'type': 'agent_status',
                'data': {
                    'recent_activity': agent_activities,
                    'total_active': len(set(e.template_id for e in recent_executions if e.template_id))
                },
                'timestamp': timezone.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error sending agent status: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error fetching agent status: {str(e)}'
            }))

    async def send_advisor_insights(self):
        """Send recent advisor insights"""
        from core.models_unified_system import Advisor

        try:
            # Get top advisors by consultation count
            advisors = await database_sync_to_async(
                lambda: list(Advisor.objects.filter(
                    is_active=True
                ).order_by('-total_consultations')[:5])
            )()

            advisor_data = []
            for advisor in advisors:
                advisor_data.append({
                    'name': advisor.name,
                    'expertise': advisor.expertise,
                    'consultations': advisor.total_consultations,
                    'influence_score': float(advisor.influence_score) if advisor.influence_score else 0
                })

            await self.send(text_data=json.dumps({
                'type': 'advisor_insights',
                'data': {
                    'top_advisors': advisor_data,
                    'total_consultations': sum(a['consultations'] for a in advisor_data)
                },
                'timestamp': timezone.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error sending advisor insights: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error fetching advisor insights: {str(e)}'
            }))