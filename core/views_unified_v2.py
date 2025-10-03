"""
Unified V2 Views - Fresh Start with Authentication Built-In

This module contains all views for the Session 22 UI Fresh Start.
Every view requires authentication and provides user context by default.
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from core.models_unified_system import Agent, Advisor, AgentExecution, Opportunity, SpiderData, UserAgentLearning


class AuthenticatedView(LoginRequiredMixin, TemplateView):
    """
    Base view for all authenticated pages.
    Automatically redirects to login if not authenticated.
    Provides user context to all templates.
    """
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_data'] = self.get_user_data()
        context['user_stats'] = self.get_user_stats()
        return context

    def get_user_data(self):
        """Get comprehensive user data for the current user"""
        user = self.request.user
        return {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name or user.username,
            'last_name': user.last_name,
            'full_name': user.get_full_name() or user.username,
        }

    def get_user_stats(self):
        """Get real-time statistics from the database"""
        user = self.request.user

        # Get counts
        agent_count = Agent.objects.filter(is_active=True).count()
        advisor_count = Advisor.objects.filter(is_active=True).count()
        execution_count = AgentExecution.objects.filter(user=user).count()

        # Try to get learning records
        try:
            learning_records = UserAgentLearning.objects.filter(user=user).count()
            avg_confidence = UserAgentLearning.objects.filter(user=user).aggregate(
                avg=Avg('confidence_score')
            )['avg'] or 0.0
        except:
            learning_records = 0
            avg_confidence = 0.0

        # Get spider data
        spider_data_count = SpiderData.objects.count()
        # Get count of unique spiders from spider_registry
        try:
            from ai_core.spiders.spider_registry import spider_registry
            active_spider_count = len(spider_registry.list_spiders())
        except:
            active_spider_count = 45  # Known count from system

        # Get opportunities
        opportunities_count = Opportunity.objects.filter(user=user).count()

        # Get recent execution data (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_executions = AgentExecution.objects.filter(
            user=user,
            created_at__gte=week_ago
        ).count()

        return {
            'agent_count': agent_count,
            'advisor_count': advisor_count,
            'execution_count': execution_count,
            'learning_records': learning_records,
            'avg_confidence': round(avg_confidence, 2),
            'spider_data_count': spider_data_count,
            'active_spider_count': active_spider_count,
            'opportunities_count': opportunities_count,
            'recent_executions': recent_executions,
        }


class DashboardView(AuthenticatedView):
    """
    Main dashboard - Welcome page with real-time stats
    """
    template_name = 'unified_v2/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get recent activity (last 10 executions)
        context['recent_activity'] = AgentExecution.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:10]

        # Get learning insights (top 5 agents by confidence)
        try:
            context['learning_insights'] = UserAgentLearning.objects.filter(
                user=self.request.user
            ).order_by('-confidence_score')[:5]
        except:
            context['learning_insights'] = []

        # Get recent opportunities
        context['recent_opportunities'] = Opportunity.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:5]

        return context


class PersonalAssistantView(AuthenticatedView):
    """
    Personal Assistant - Chat interface with agent orchestration
    """
    template_name = 'unified_v2/personal_assistant.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Load conversation history (placeholder - will implement with messages model)
        context['conversation_history'] = []

        # Suggested actions
        context['suggested_actions'] = [
            {'text': 'Find freelance work', 'intent': 'income_generation'},
            {'text': 'Get investment advice', 'intent': 'investment_advice'},
            {'text': 'Create content', 'intent': 'content_creation'},
            {'text': 'Analyze data', 'intent': 'data_analysis'},
        ]

        return context


class AgentMarketplaceView(AuthenticatedView):
    """
    Agent Marketplace - Browse and execute 160 agents
    """
    template_name = 'unified_v2/agent_marketplace.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all active agents with categories
        agents = Agent.objects.filter(is_active=True).values(
            'id', 'name', 'description', 'category'
        ).order_by('category', 'name')

        context['agents'] = list(agents)

        # Get unique categories for filtering
        categories = Agent.objects.filter(
            is_active=True
        ).values_list('category', flat=True).distinct().order_by('category')
        context['categories'] = list(categories)

        return context


class AgentDetailView(AuthenticatedView):
    """
    Agent Detail - View single agent with execution history
    """
    template_name = 'unified_v2/agent_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agent_id = kwargs.get('agent_id')

        try:
            agent = Agent.objects.get(id=agent_id, is_active=True)
            context['agent'] = agent

            # Get execution history for this agent
            context['execution_history'] = AgentExecution.objects.filter(
                user=self.request.user,
                agent=agent
            ).order_by('-created_at')[:20]

            # Get learning stats for this agent
            try:
                learning_stats = UserAgentLearning.objects.filter(
                    user=self.request.user,
                    agent=agent
                ).first()
                context['learning_stats'] = learning_stats
            except:
                context['learning_stats'] = None

        except Agent.DoesNotExist:
            context['agent'] = None
            context['error'] = 'Agent not found'

        return context


class AdvisorCouncilView(AuthenticatedView):
    """
    Advisor Council - Interface with 25 legendary advisors
    """
    template_name = 'unified_v2/advisor_council.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all active advisors
        advisors = Advisor.objects.filter(is_active=True).values(
            'id', 'name', 'title', 'expertise', 'category', 'influence_score',
            'avatar_url', 'wisdom', 'total_consultations', 'total_insights_provided',
            'last_consultation'
        ).order_by('name')

        context['advisors'] = list(advisors)

        # Get unique expertise areas for filtering
        expertise_areas = Advisor.objects.filter(
            is_active=True
        ).values_list('expertise', flat=True).distinct().order_by('expertise')
        context['expertise_areas'] = list(expertise_areas)

        return context


class AdvisorDetailView(AuthenticatedView):
    """
    Advisor Detail - View single advisor with consultation history
    """
    template_name = 'unified_v2/advisor_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        advisor_id = kwargs.get('advisor_id')

        try:
            advisor = Advisor.objects.get(id=advisor_id, is_active=True)
            context['advisor'] = advisor

            # Consultation history (placeholder - will implement with consultations model)
            context['consultation_history'] = []

        except Advisor.DoesNotExist:
            context['advisor'] = None
            context['error'] = 'Advisor not found'

        return context


class ContentStudioView(AuthenticatedView):
    """
    Content Studio - AI content creation interface
    Leverages existing APIs in core/views_content.py
    """
    template_name = 'unified_v2/content_studio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Load available image styles (70+ styles from content/image_generation.py)
        context['image_styles'] = self.get_image_styles()

        # Generation history (placeholder - will load from content generation records)
        context['generation_history'] = []

        return context

    def get_image_styles(self):
        """Get all available image generation styles"""
        return {
            'Photography': [
                {'value': 'photorealistic', 'label': 'Photorealistic - Ultra detailed photography'},
                {'value': 'portrait', 'label': 'Portrait - Professional headshot style'},
                {'value': 'landscape', 'label': 'Landscape - Scenic photography'},
                {'value': 'macro', 'label': 'Macro - Close-up detail shots'},
            ],
            'Art Styles': [
                {'value': 'anime', 'label': 'Anime - Studio Ghibli style'},
                {'value': 'cyberpunk', 'label': 'Cyberpunk - Neon lights, futuristic'},
                {'value': 'watercolor', 'label': 'Watercolor - Soft, flowing paint'},
                {'value': 'oil_painting', 'label': 'Oil Painting - Classical art style'},
                {'value': 'digital_art', 'label': 'Digital Art - Modern illustration'},
            ],
            'Specific Genres': [
                {'value': '3d_render', 'label': '3D Render - Computer-generated imagery'},
                {'value': 'pixel_art', 'label': 'Pixel Art - Retro game aesthetic'},
                {'value': 'comic_book', 'label': 'Comic Book - Bold lines, vibrant colors'},
                {'value': 'fantasy', 'label': 'Fantasy - Magical, otherworldly scenes'},
            ]
            # Note: Full 70+ styles will be loaded from image_generation service
        }


class IntelligenceHubView(AuthenticatedView):
    """
    Intelligence Hub - Spider network & data visibility
    """
    template_name = 'unified_v2/intelligence_hub.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get spider status from registry
        try:
            from ai_core.spiders.spider_registry import spider_registry
            spider_list = spider_registry.list_spiders()
            spiders = [{'name': name, 'description': f'{name} spider', 'spider_type': 'web'}
                      for name in spider_list]
            context['spiders'] = spiders
        except:
            context['spiders'] = []

        # Get recent spider data (last 50 items)
        recent_data = SpiderData.objects.all().order_by('-created_at')[:50]
        context['recent_spider_data'] = recent_data

        # Get opportunities
        opportunities = Opportunity.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:20]
        context['opportunities'] = opportunities

        # Data quality metrics
        total_data = SpiderData.objects.count()
        context['data_quality'] = {
            'total_items': total_data,
            'quality_score': 0.85,  # Placeholder - calculate from actual data quality
            'recent_items_24h': SpiderData.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).count(),
        }

        return context


class SportsbookView(AuthenticatedView):
    """
    Sportsbook - Live odds, game analysis, and betting intelligence
    """
    template_name = 'unified_v2/sportsbook.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Sports available (display name -> API key)
        context['sports'] = [
            {'name': 'NFL', 'key': 'nfl'},
            {'name': 'NCAAF', 'key': 'ncaaf'},
            {'name': 'NBA', 'key': 'nba'},
            {'name': 'NCAAB', 'key': 'ncaab'},
            {'name': 'MLB', 'key': 'mlb'},
            {'name': 'NHL', 'key': 'nhl'},
            {'name': 'Horse Racing', 'key': 'horseracing_aus_horse_racing'},
        ]

        # Betting features
        context['features'] = [
            {'name': 'Live Odds', 'endpoint': '/api/v1/sports/live-odds/'},
            {'name': 'Arbitrage Detection', 'endpoint': '/api/v1/odds/arbitrage/'},
            {'name': 'Kelly Criterion', 'endpoint': '/api/v1/odds/kelly-criterion/'},
            {'name': 'Game Analysis', 'endpoint': '/api/v1/sports/analyze-game/'},
            {'name': 'Bankroll Management', 'endpoint': '/api/v1/odds/bankroll/'},
        ]

        return context
