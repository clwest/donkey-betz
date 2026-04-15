"""
Temporary Intelligence API endpoints
This provides the skynet status endpoint for the frontend
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from datetime import datetime
import asyncio
import sys
import os

logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_core.intelligence.income_builder import income_builder, UserProfile, SkillLevel
from ai_core.intelligence.monetization_engine import monetization_engine

# Import the views we need to expose
from intelligence.views import ExecuteActionPlanView, ViewGeneratedFileView

# Create view instances
execute_action_plan_view = ExecuteActionPlanView.as_view()
view_generated_file = ViewGeneratedFileView.as_view()


@api_view(['GET'])
@permission_classes([AllowAny])  # Session 688: Allow public access for React frontend
def skynet_status(request):
    """Provide Skynet Intelligence Engine status with REAL data"""
    from django.utils import timezone
    from datetime import timedelta

    try:
        # Get real counts from database
        from core.models_unified_system import Opportunity, AgentPrediction
        from core.models_pilot_readiness import PilotReadinessGate, PilotExecution
        from ai_core.spiders.spider_registry import SpiderRegistry

        now = timezone.now()
        last_24h = now - timedelta(hours=24)

        # Real opportunity count (last 24h or total recent)
        opportunity_count = Opportunity.objects.filter(
            created_at__gte=last_24h
        ).count()
        if opportunity_count == 0:
            opportunity_count = Opportunity.objects.count()

        # Real prediction count
        prediction_count = AgentPrediction.objects.filter(
            created_at__gte=last_24h
        ).count()
        if prediction_count == 0:
            prediction_count = AgentPrediction.objects.count()

        # Real spider count.
        # Session 1103c: was a BARE 'except:' which catches
        # KeyboardInterrupt + SystemExit and silently fell back to
        # the hardcoded magic number 77. The /api/intelligence/
        # endpoint then reported a clean "77 spiders" even when the
        # registry was actually broken or empty. Now narrow to
        # Exception and log loudly.
        try:
            registry = SpiderRegistry()
            spider_count = len(registry.get_all_spiders())
        except Exception as e:
            logger.warning(
                "intelligence_api: SpiderRegistry lookup failed "
                "(%s: %s) — reporting hardcoded spider_count=77 as "
                "fallback. Real count unknown.",
                type(e).__name__, e,
            )
            spider_count = 77

        # Real pilot counts
        running_pilots = PilotExecution.objects.filter(status='running').count()
        pending_gates = PilotReadinessGate.objects.filter(
            status__in=['not_started', 'in_progress', 'ready']
        ).count()

        return Response({
            'skynet_status': 'ONLINE',
            'intelligence_engine': 'ONLINE',
            'live_opportunities': opportunity_count,
            'live_predictions': prediction_count,
            'spider_count': spider_count,
            'running_pilots': running_pilots,
            'pending_gates': pending_gates,
            'scan_interval': 30,
            'last_update': now.isoformat(),
            'features': {
                'sports_intelligence': True,
                'arbitrage_detection': True,
                'value_betting': True,
                'cross_domain_analysis': True,
                'pattern_recognition': True,
                'ml_pipeline': True,
                'advisor_network': True
            },
            'advisor_network': {
                'total_advisors': 25,
                'online_now': 18,
                'categories': ['Sports Betting', 'Crypto', 'Options', 'Real Estate']
            }
        })
    except Exception as e:
        return Response({
            'skynet_status': 'ERROR',
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])  # Session 688: Allow public access for React frontend
def live_opportunities(request):
    """Get live opportunities from database"""
    from django.utils import timezone
    from datetime import timedelta

    try:
        from core.models_unified_system import Opportunity

        # Get recent opportunities (last 7 days)
        last_week = timezone.now() - timedelta(days=7)
        opportunities = Opportunity.objects.filter(
            created_at__gte=last_week
        ).order_by('-created_at')[:20]

        # If no recent, get any opportunities
        if not opportunities.exists():
            opportunities = Opportunity.objects.order_by('-created_at')[:20]

        return Response({
            'success': True,
            'opportunities': [
                {
                    'id': str(opp.id),
                    'title': opp.title or opp.description[:50] if opp.description else 'Opportunity',
                    'type': getattr(opp, 'opportunity_type', 'general') or 'general',
                    'source': getattr(opp, 'source', 'system') or 'system',
                    # Session 688: Use match_score or overall_score from the model (not 'score')
                    'score': int(getattr(opp, 'match_score', 0) or getattr(opp, 'overall_score', 0) or 0),
                    'created_at': opp.created_at.isoformat() if opp.created_at else None,
                }
                for opp in opportunities
            ],
            'count': opportunities.count()
        })
    except Exception as e:
        return Response({
            'success': False,
            'opportunities': [],
            'error': str(e)
        })


@api_view(['GET'])
@permission_classes([AllowAny])  # Session 688: Allow public access for React frontend
def live_predictions(request):
    """Get live predictions from database"""
    from django.utils import timezone
    from datetime import timedelta

    try:
        from core.models_unified_system import AgentPrediction

        # Get recent predictions (last 7 days)
        last_week = timezone.now() - timedelta(days=7)
        predictions = AgentPrediction.objects.select_related('agent').filter(
            created_at__gte=last_week
        ).order_by('-created_at')[:20]

        # If no recent, get any predictions
        if not predictions.exists():
            predictions = AgentPrediction.objects.select_related('agent').order_by('-created_at')[:20]

        # Session 692: Return rich prediction data
        predictions_data = []
        for pred in predictions:
            # Calculate days until deadline
            days_remaining = None
            if pred.deadline:
                delta = pred.deadline - timezone.now()
                days_remaining = max(0, delta.days)

            predictions_data.append({
                'id': str(pred.id),
                'title': pred.title[:100] if pred.title else 'Prediction',
                'prediction': pred.prediction or '',  # Session 692: Return full prediction text, not truncated
                'probability': int((pred.confidence or 0.5) * 100),
                'category': pred.category or 'general',

                # Agent info
                'agent_name': pred.agent.name if pred.agent else 'AI Agent',
                'agent_type': pred.agent.agent_type if pred.agent else None,

                # Source info
                'source_type': pred.source or 'analysis',  # dream, analysis, pattern, etc.
                'source_reference': pred.source_reference or {},

                # Tags
                'tags': pred.tags[:5] if pred.tags else [],  # Limit to 5 tags

                # Timing
                'timeframe': pred.timeframe or 'quarter',
                'deadline': pred.deadline.isoformat() if pred.deadline else None,
                'days_remaining': days_remaining,
                'created_at': pred.created_at.isoformat() if pred.created_at else None,

                # Status & Verification
                'status': pred.status or 'pending',
                'is_featured': pred.is_featured,
                'verified_at': pred.verified_at.isoformat() if pred.verified_at else None,
                'accuracy_score': pred.accuracy_score,

                # Engagement
                'upvotes': pred.upvotes or 0,
                'views': pred.views or 0,
            })

        return Response({
            'success': True,
            'predictions': predictions_data,
            'count': len(predictions_data)
        })
    except Exception as e:
        return Response({
            'success': False,
            'predictions': [],
            'error': str(e)
        })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def income_builder_analysis(request):
    """💰 AI Income Builder - Start from $0"""

    if request.method == 'GET':
        # Get available income opportunities
        opportunities = []
        for opp in income_builder.opportunities:
            opportunities.append({
                'id': opp.id,
                'title': opp.title,
                'stream_type': opp.stream_type.value,
                'description': opp.description,
                'time_to_income': opp.time_to_first_income,
                'potential_monthly': opp.potential_monthly,
                'difficulty': opp.difficulty.value,
                'initial_investment': opp.initial_investment,
                'success_rate': opp.success_rate,
                'market_demand': opp.market_demand,
                'required_skills': opp.required_skills,
                'action_steps': opp.action_steps,
                'resources': opp.resources
            })

        return Response({
            'success': True,
            'opportunities': opportunities,
            'count': len(opportunities),
            'message': 'Start earning from $0 with AI assistance'
        })

    else:  # POST - Analyze user potential
        try:
            # Create user profile from request data
            user_data = request.data
            user_profile = UserProfile(
                id=str(request.user.id) if request.user.is_authenticated else "anonymous",
                current_balance=user_data.get('current_balance', 0.0),
                skills=user_data.get('skills', []),
                skill_level=SkillLevel[user_data.get('skill_level', 'BEGINNER').upper()],
                available_hours_per_week=user_data.get('available_hours', 10),
                interests=user_data.get('interests', [])
            )

            # Get income analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            analysis = loop.run_until_complete(
                income_builder.analyze_user_potential(user_profile)
            )

            return Response({
                'success': True,
                'analysis': analysis,
                'message': 'Income opportunities analyzed successfully'
            })

        except Exception as e:
            return Response({
                'error': f'Failed to analyze income opportunities: {str(e)}',
                'success': False
            })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def income_action_plan(request):
    """📋 Create personalized action plan for income generation"""
    try:
        user_id = str(request.user.id) if request.user.is_authenticated else "anonymous"
        opportunity_id = request.data.get('opportunity_id')

        if not opportunity_id:
            return Response({
                'error': 'opportunity_id is required',
                'success': False
            })

        # Create action plan
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        action_plan = loop.run_until_complete(
            income_builder.create_action_plan(user_id, opportunity_id)
        )

        return Response({
            'success': True,
            'action_plan': action_plan,
            'message': 'Action plan created successfully'
        })

    except Exception as e:
        return Response({
            'error': f'Failed to create action plan: {str(e)}',
            'success': False
        })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def monetization_opportunities(request):
    """💰 Unified Monetization - All Revenue Streams"""

    if request.method == 'GET':
        # Get revenue dashboard
        dashboard = monetization_engine.get_revenue_dashboard()

        return Response({
            'success': True,
            'dashboard': dashboard,
            'active_opportunities': len(monetization_engine.opportunities),
            'message': 'Multiple revenue streams available'
        })

    else:  # POST - Analyze best opportunities
        try:
            user_data = request.data
            user_profile = {
                'current_balance': user_data.get('current_balance', 0),
                'available_hours': user_data.get('available_hours', 20),
                'skills': user_data.get('skills', []),
                'interests': user_data.get('interests', [])
            }

            # Get best opportunities
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            opportunities = loop.run_until_complete(
                monetization_engine.analyze_best_opportunities(user_profile)
            )

            return Response({
                'success': True,
                'opportunities': [
                    {
                        'id': opp['opportunity'].id,
                        'title': opp['opportunity'].title,
                        'stream': opp['opportunity'].stream.value,
                        'potential_revenue': opp['opportunity'].potential_revenue,
                        'hours_required': opp['opportunity'].time_investment,
                        'roi': opp['roi'],
                        'score': opp['score'],
                        'ai_powered': opp['ai_powered'],
                        'highly_automated': opp['highly_automated'],
                        'quick_start': opp['quick_start']
                    }
                    for opp in opportunities
                ],
                'message': 'Opportunities analyzed successfully'
            })

        except Exception as e:
            return Response({
                'error': f'Failed to analyze opportunities: {str(e)}',
                'success': False
            })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_monetization_plan(request):
    """📋 Create Complete Monetization Plan"""
    try:
        selected_streams = request.data.get('streams', [])

        if not selected_streams:
            return Response({
                'error': 'Please select at least one revenue stream',
                'success': False
            })

        # Create monetization plan
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        plan = loop.run_until_complete(
            monetization_engine.create_monetization_plan(selected_streams)
        )

        return Response({
            'success': True,
            'plan': plan,
            'message': 'Monetization plan created successfully'
        })

    except Exception as e:
        return Response({
            'error': f'Failed to create plan: {str(e)}',
            'success': False
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def content_automation_plan(request):
    """🤖 Get Content Automation & Monetization Plan"""
    try:
        # Get automation plan
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        automation = loop.run_until_complete(
            monetization_engine.automate_content_monetization()
        )

        return Response({
            'success': True,
            'automation_plan': automation,
            'total_potential': '$200-950/day automated income',
            'message': 'Content automation plan ready'
        })

    except Exception as e:
        return Response({
            'error': f'Failed to get automation plan: {str(e)}',
            'success': False
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_revenue(request):
    """📊 Track Revenue from Any Stream"""
    try:
        stream = request.data.get('stream')
        amount = request.data.get('amount', 0)

        if not stream:
            return Response({
                'error': 'Stream is required',
                'success': False
            })

        # Track revenue
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            monetization_engine.track_revenue(stream, amount)
        )

        return Response({
            'success': True,
            'tracking': result,
            'message': f'Revenue tracked: ${amount} from {stream}'
        })

    except Exception as e:
        return Response({
            'error': f'Failed to track revenue: {str(e)}',
            'success': False
        })