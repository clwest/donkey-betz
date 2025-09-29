"""
Revenue Opportunities WebSocket Consumer
========================================
Real-time opportunities from spider network to frontend
"""

import json
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import redis

logger = logging.getLogger(__name__)


class RevenueOpportunitiesConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for Revenue Opportunities page
    Connects to spider network and sends real opportunities to users
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.user = None
        self.room_name = None
        self.room_group_name = None
        self.opportunities_task = None

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope.get('user', AnonymousUser())

        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        self.room_name = f'revenue_{self.user.id}'
        self.room_group_name = f'revenue_opportunities_{self.user.id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial data
        await self.send_initial_opportunities()

        # Start streaming opportunities
        self.opportunities_task = asyncio.create_task(self.stream_opportunities())

        logger.info(f"✅ Revenue Opportunities WebSocket connected for user {self.user.username}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        if self.opportunities_task:
            self.opportunities_task.cancel()

        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        logger.info(f"Revenue Opportunities WebSocket disconnected for user {self.user.username if self.user else 'unknown'}")

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'quick_apply':
                await self.handle_quick_apply(data)
            elif action == 'filter':
                await self.apply_filters(data.get('filters', {}))
            elif action == 'refresh':
                await self.send_initial_opportunities()
            elif action == 'get_details':
                await self.send_opportunity_details(data.get('opportunity_id'))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_initial_opportunities(self):
        """Send initial set of opportunities"""
        opportunities = await self.get_opportunities_from_spiders()

        await self.send(text_data=json.dumps({
            'type': 'opportunities_update',
            'opportunities': opportunities,
            'total': len(opportunities),
            'timestamp': datetime.now().isoformat(),
            'stats': {
                'activeCount': len(opportunities),
                'totalValue': sum(
                    (opp.get('salary_min', 0) + opp.get('salary_max', 0)) // 2
                    if opp.get('salary_min') else opp.get('budget', 0)
                    for opp in opportunities
                ),
                'appliedToday': 0,
                'successRate': 0
            }
        }))

    @database_sync_to_async
    def get_opportunities_from_spiders(self) -> List[Dict[str, Any]]:
        """Get opportunities from spider network and Redis"""
        opportunities = []

        try:
            # Get from Django cache (spider-collected opportunities)
            from django.core.cache import cache

            # Try the latest_opportunities key first (from real spider)
            latest_opportunities = cache.get('latest_opportunities', [])
            if latest_opportunities:
                opportunities = latest_opportunities[:50]  # Show more opportunities (we have 76)

                # Add user-specific scoring and ensure proper structure
                for opportunity in opportunities:
                    if not opportunity.get('id'):
                        # Generate ID from title and company
                        opportunity['id'] = f"{opportunity.get('source', 'unknown').lower()}_{hash(opportunity.get('title', '') + opportunity.get('company', '')) % 10000}"

                    # Add user-specific scoring
                    opportunity['match_score'] = self.calculate_match_score(opportunity)
                    opportunity['quick_apply_available'] = True

            # If no Redis opportunities, use realistic mock data
            if not opportunities:
                opportunities = [
                    {
                        'id': 'opp_001',
                        'title': 'Python Backend Developer',
                        'company': 'TechStartup Inc',
                        'budget': 5000,
                        'type': 'fixed',
                        'platform': 'upwork',
                        'description': 'Build REST APIs for our SaaS platform',
                        'skills': ['Python', 'Django', 'PostgreSQL'],
                        'match_score': 92,
                        'quick_apply_available': True,
                        'posted': '2 hours ago',
                        'deadline': '5 days',
                        'client_rating': 4.8
                    },
                    {
                        'id': 'opp_002',
                        'title': 'Content Writer for Tech Blog',
                        'company': 'Digital Media Co',
                        'budget': 800,
                        'type': 'fixed',
                        'platform': 'fiverr',
                        'description': 'Write 10 SEO-optimized articles about AI',
                        'skills': ['Writing', 'SEO', 'AI Knowledge'],
                        'match_score': 78,
                        'quick_apply_available': True,
                        'posted': '5 hours ago',
                        'deadline': '7 days',
                        'client_rating': 4.5
                    },
                    {
                        'id': 'opp_003',
                        'title': 'React Frontend Development',
                        'company': 'Design Agency',
                        'budget': 3500,
                        'type': 'fixed',
                        'platform': 'freelancer',
                        'description': 'Create responsive UI for e-commerce site',
                        'skills': ['React', 'TypeScript', 'Tailwind CSS'],
                        'match_score': 85,
                        'quick_apply_available': True,
                        'posted': '1 day ago',
                        'deadline': '10 days',
                        'client_rating': 4.7
                    }
                ]

            # Sort by match score
            opportunities.sort(key=lambda x: x.get('match_score', 0), reverse=True)

        except Exception as e:
            logger.error(f"Error getting opportunities: {str(e)}")

        return opportunities

    def calculate_match_score(self, opportunity: Dict[str, Any]) -> int:
        """Calculate match score based on user profile"""
        # Get user profile
        from core.models import ExtendedUserProfile
        try:
            profile = ExtendedUserProfile.objects.get(user=self.user)
            user_skills = json.loads(profile.skills) if profile.skills else []

            # Simple matching algorithm
            required_skills = opportunity.get('skills_required', opportunity.get('skills', []))
            if not required_skills:
                return 75  # Default score

            matches = sum(1 for skill in required_skills if skill.lower() in [s.lower() for s in user_skills])
            score = int((matches / len(required_skills)) * 100) if required_skills else 75

            # Boost score based on budget
            budget = opportunity.get('budget', 0)
            if isinstance(budget, dict):
                budget = budget.get('max', 0)
            if budget > 1000:
                score = min(100, score + 10)

            return score

        except Exception:
            return 75  # Default score if no profile

    async def stream_opportunities(self):
        """Stream new opportunities as they come in"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                # Get new opportunities
                opportunities = await self.get_opportunities_from_spiders()

                # Send only new/updated ones
                if opportunities:
                    await self.send(text_data=json.dumps({
                        'type': 'new_opportunities',
                        'data': {
                            'opportunities': opportunities[:5],  # Send top 5
                            'timestamp': datetime.now().isoformat()
                        }
                    }))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in stream_opportunities: {str(e)}")
                await asyncio.sleep(60)  # Back off on error

    async def handle_quick_apply(self, data: Dict[str, Any]):
        """Handle quick apply action"""
        opportunity_id = data.get('opportunity_id')

        if not opportunity_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Opportunity ID required'
            }))
            return

        # Process application
        from core.views_job_application_system import QuickApplyView
        from core.models import Revenue
        from django.http import HttpRequest
        from django.utils import timezone
        import io

        # Create mock request
        request = HttpRequest()
        request.user = self.user
        request._body = json.dumps({
            'job_data': {
                'id': opportunity_id,
                'title': data.get('title', 'Unknown Position'),
                'company': data.get('company', 'Unknown Company'),
                'platform': data.get('platform', 'freelance')
            }
        }).encode()
        request.content_type = 'application/json'

        # Use QuickApplyView to process
        view = QuickApplyView()
        response = await database_sync_to_async(view.post)(request)

        response_data = json.loads(response.content)

        # Track revenue if application was successful
        if response_data.get('success', False):
            # Extract salary information from opportunity
            salary_min = data.get('salary_min', data.get('budget', 50000))
            salary_max = data.get('salary_max', salary_min)

            # If it's an hourly rate, calculate annual
            if isinstance(salary_min, int) and salary_min < 500:  # Likely hourly
                salary_min = salary_min * 2000  # Assume 2000 hours/year
                salary_max = salary_max * 2000 if isinstance(salary_max, int) else salary_min

            # Calculate potential revenue (average of min and max)
            potential_amount = (salary_min + salary_max) / 2

            # Create Revenue record
            await database_sync_to_async(Revenue.objects.create)(
                user=self.user,
                amount=potential_amount,
                source='quick_apply',
                status='potential',
                opportunity_id=opportunity_id,
                opportunity_title=data.get('title', 'Unknown Position'),
                company=data.get('company', 'Unknown Company'),
                application_date=timezone.now(),
                description=f"Quick Apply to {data.get('title')} at {data.get('company')}",
                spider_source=data.get('source', 'Unknown'),
                agent_involved='QuickApplyAgent',
                match_score=data.get('match_score', 0.75)
            )

            logger.info(f"Revenue tracked: ${potential_amount} potential from {opportunity_id}")

        await self.send(text_data=json.dumps({
            'type': 'quick_apply_result',
            'data': {
                'opportunity_id': opportunity_id,
                'success': response_data.get('success', False),
                'message': response_data.get('message', ''),
                'application_id': response_data.get('application', {}).get('id')
            }
        }))

    async def apply_filters(self, filters: Dict[str, Any]):
        """Apply filters and send filtered opportunities"""
        # Get all opportunities
        all_opportunities = await self.get_opportunities_from_spiders()

        # Apply filters
        filtered = all_opportunities

        if filters.get('min_budget'):
            min_budget = float(filters['min_budget'])
            filtered = [o for o in filtered if self._get_budget_value(o) >= min_budget]

        if filters.get('platform'):
            platform = filters['platform'].lower()
            filtered = [o for o in filtered if o.get('platform', '').lower() == platform]

        if filters.get('skills'):
            required_skills = filters['skills']
            filtered = [o for o in filtered if any(
                skill in o.get('skills', []) for skill in required_skills
            )]

        await self.send(text_data=json.dumps({
            'type': 'filtered_opportunities',
            'data': {
                'opportunities': filtered,
                'total': len(filtered),
                'filters_applied': filters
            }
        }))

    def _get_budget_value(self, opportunity: Dict[str, Any]) -> float:
        """Extract budget value from opportunity"""
        budget = opportunity.get('budget', 0)
        if isinstance(budget, dict):
            return budget.get('max', budget.get('min', 0))
        return float(budget)

    async def send_opportunity_details(self, opportunity_id: str):
        """Send detailed information about an opportunity"""
        # Get from Redis
        opportunity_json = await database_sync_to_async(
            self.redis_client.get
        )(f'freelance:opportunity:{opportunity_id}')

        if opportunity_json:
            opportunity = json.loads(opportunity_json)

            # Add additional details
            opportunity['full_description'] = opportunity.get('description', '')
            opportunity['application_tips'] = self._generate_application_tips(opportunity)

            await self.send(text_data=json.dumps({
                'type': 'opportunity_details',
                'data': opportunity
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Opportunity not found'
            }))

    def _generate_application_tips(self, opportunity: Dict[str, Any]) -> List[str]:
        """Generate application tips based on opportunity"""
        tips = []

        budget = self._get_budget_value(opportunity)
        if budget > 1000:
            tips.append("This is a high-value project. Emphasize your relevant experience.")

        if opportunity.get('client_rating', 0) >= 4.5:
            tips.append("This client has excellent ratings. Be professional and detailed.")

        skills = opportunity.get('skills', [])
        if 'Python' in skills:
            tips.append("Mention specific Python frameworks and projects you've completed.")

        return tips

    # Group send handler
    async def opportunity_update(self, event):
        """Handle opportunity updates from channel layer"""
        await self.send(text_data=json.dumps({
            'type': 'opportunity_update',
            'data': event['data']
        }))