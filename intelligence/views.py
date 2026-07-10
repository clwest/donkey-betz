"""
🧠 INTELLIGENCE API VIEWS
REST API endpoints for the Real-Time Intelligence Engine
"""

import asyncio
import logging
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from .realtime_engine import intelligence_engine
from .income_builder import income_builder, UserProfile, SkillLevel
from .models import ActionPlan
from .agent_instruction_parser import AgentInstructionParser
from .agent_execution_pipeline import execute_plan_async

logger = logging.getLogger(__name__)


def _iter_string_values(obj):
    """Yield every string leaf value under a nested dict/list JSON tree.

    Used by ownership checks (I-0301 Phase 3 Stage 2b) that need to
    compare a request-supplied filename basename against every stored
    file path in a plan's plan_data JSON.
    """
    if isinstance(obj, str):
        yield obj
        return
    if isinstance(obj, dict):
        for value in obj.values():
            yield from _iter_string_values(value)
        return
    if isinstance(obj, (list, tuple)):
        for item in obj:
            yield from _iter_string_values(item)


class SkynetStatusView(APIView):
    """🚀 Get Skynet Intelligence Engine Status"""

    def get(self, request):
        try:
            # Check engine status
            engine_status = 'ONLINE' if intelligence_engine.is_running else 'OFFLINE'

            # Get current data
            opportunities_count = len(intelligence_engine.get_current_opportunities())
            predictions_count = len(intelligence_engine.get_current_predictions())

            return Response({
                'skynet_status': engine_status,
                'intelligence_engine': engine_status,
                'live_opportunities': opportunities_count,
                'live_predictions': predictions_count,
                'scan_interval': intelligence_engine.scan_interval,
                'last_update': datetime.now().isoformat(),
                'features': {
                    'sports_intelligence': True,
                    'arbitrage_detection': True,
                    'value_betting': True,
                    'cross_domain_analysis': True,
                    'pattern_recognition': True
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Skynet status error: {e}")
            return Response({
                'error': 'Failed to get Skynet status',
                'skynet_status': 'ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LiveOpportunitiesView(APIView):
    """🎯 Get Live Market Opportunities"""

    def get(self, request):
        try:
            opportunities = intelligence_engine.get_current_opportunities()

            return Response({
                'opportunities': opportunities,
                'count': len(opportunities),
                'timestamp': datetime.now().isoformat(),
                'scanner_status': 'ACTIVE' if intelligence_engine.is_running else 'OFFLINE'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Live opportunities error: {e}")
            return Response({
                'error': 'Failed to get live opportunities',
                'opportunities': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LivePredictionsView(APIView):
    """🔮 Get Live Intelligence Predictions"""

    def get(self, request):
        try:
            predictions = intelligence_engine.get_current_predictions()

            return Response({
                'predictions': predictions,
                'count': len(predictions),
                'timestamp': datetime.now().isoformat(),
                'engine_status': 'ACTIVE' if intelligence_engine.is_running else 'OFFLINE'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Live predictions error: {e}")
            return Response({
                'error': 'Failed to get live predictions',
                'predictions': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IncomeBuilderAnalysisView(APIView):
    """💰 AI Income Builder - Start from $0"""

    def post(self, request):
        """Analyze user's income potential"""
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
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Income analysis error: {e}")
            return Response({
                'error': f'Failed to analyze income opportunities: {str(e)}',
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Get available income opportunities"""
        try:
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
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Get opportunities error: {e}")
            return Response({
                'error': f'Failed to get opportunities: {str(e)}',
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActionPlanPersistenceView(APIView):
    """📂 Save and retrieve action plans for persistence across sessions.

    I-0301 Phase 3 Stage 2b — Bucket B remediation (Rigby SIGN Q1: retire
    filesystem read path within I-0301 scope). The prior filesystem-glob
    GET was the cross-tenant leak: every anonymous request saw every user's
    action plans by walking ``income_builder_outputs/``. GET is now backed
    by the ``ActionPlan`` DB model, filtered by ``user=request.user`` —
    minimal safe queryset scoping per S2742 scoping SIGN §7.1 allowance.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get action plans owned by the requesting user (DB-scoped)."""
        try:
            plans = ActionPlan.objects.filter(
                user=request.user
            ).order_by('-created_at')[:10]

            serialized_plans = []
            for plan in plans:
                serialized_plans.append({
                    'id': str(plan.id),
                    'backend_id': str(plan.id),
                    'opportunity_id': plan.opportunity_id,
                    'opportunity_title': plan.opportunity_title,
                    'opportunity_data': plan.opportunity_data or {},
                    'plan_data': plan.plan_data or {},
                    'steps': plan.steps or [],
                    'resources': plan.resources or [],
                    'timeline': plan.timeline,
                    'expected_outcome': plan.expected_outcome,
                    'status': plan.status,
                    'progress': plan.progress,
                    'current_step': plan.current_step,
                    'completed_steps': plan.completed_steps or [],
                    'execution_logs': (plan.execution_logs or [])[-10:],
                    'results': plan.results or {},
                    'created_at': plan.created_at.isoformat(),
                    'started_at': plan.started_at.isoformat() if plan.started_at else None,
                    'completed_at': plan.completed_at.isoformat() if plan.completed_at else None,
                    'celery_task_id': plan.celery_task_id or None,
                })

            return Response({
                'success': True,
                'plans': serialized_plans,
                'count': len(serialized_plans)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error retrieving action plans: {e}")
            return Response({
                'error': str(e),
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """Save or update action plans"""
        try:
            plans_data = request.data.get('plans', [])
            saved_plans = []

            for plan_data in plans_data:
                # Check if plan exists
                plan_id = plan_data.get('backend_id') or plan_data.get('id')

                if plan_id:
                    try:
                        # Update existing plan
                        plan = ActionPlan.objects.get(id=plan_id)

                        # Update fields
                        plan.status = plan_data.get('status', plan.status)
                        plan.progress = plan_data.get('progress', plan.progress)
                        plan.current_step = plan_data.get('current_step', plan.current_step)
                        plan.completed_steps = plan_data.get('completed_steps', plan.completed_steps)
                        plan.execution_logs = plan_data.get('execution_logs', plan.execution_logs)
                        plan.results = plan_data.get('results', plan.results)

                        if plan_data.get('completed_at'):
                            plan.completed_at = datetime.fromisoformat(plan_data['completed_at'].replace('Z', '+00:00'))

                        plan.save()
                        saved_plans.append(str(plan.id))

                    except ActionPlan.DoesNotExist:
                        # Create new plan if ID doesn't exist
                        plan = self._create_new_plan(request, plan_data)
                        if plan:
                            saved_plans.append(str(plan.id))
                else:
                    # Create new plan
                    plan = self._create_new_plan(request, plan_data)
                    if plan:
                        saved_plans.append(str(plan.id))

            return Response({
                'success': True,
                'saved_plans': saved_plans,
                'message': f'Saved {len(saved_plans)} action plans'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error saving action plans: {e}")
            return Response({
                'error': str(e),
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_new_plan(self, request, plan_data):
        """Helper to create a new action plan.

        Rigby S2742 Stage 2b SIGN Q2 must-add: no anonymous ActionPlan
        creation paths remain. IsAuthenticated at the view level guarantees
        request.user.is_authenticated is True here — the previous
        "user = ... else None" fallback is dead.
        """
        try:
            # IsAuthenticated at view level guarantees this is a real user.
            user = request.user
            opportunity_id = plan_data.get('opportunity_id')

            plan = ActionPlan.objects.create(
                user=user,
                opportunity_id=opportunity_id,
                opportunity_title=plan_data.get('opportunity_title', ''),
                opportunity_data=plan_data.get('opportunity_data', {}),
                plan_data=plan_data.get('plan_data', plan_data),
                steps=plan_data.get('steps', []),
                resources=plan_data.get('resources', []),
                timeline=plan_data.get('timeline', ''),
                expected_outcome=plan_data.get('expected_outcome', ''),
                status=plan_data.get('status', 'created'),
                progress=plan_data.get('progress', 0),
                current_step=plan_data.get('current_step', 0),
                completed_steps=plan_data.get('completed_steps', []),
                execution_logs=plan_data.get('execution_logs', []),
                results=plan_data.get('results', {}),
                celery_task_id=plan_data.get('celery_task_id', '')
            )

            # Set timestamps if provided
            if plan_data.get('started_at'):
                plan.started_at = datetime.fromisoformat(plan_data['started_at'].replace('Z', '+00:00'))
            if plan_data.get('completed_at'):
                plan.completed_at = datetime.fromisoformat(plan_data['completed_at'].replace('Z', '+00:00'))

            plan.save()
            return plan

        except Exception as e:
            logger.error(f"Error creating action plan: {e}")
            return None


class IncomeActionPlanView(APIView):
    """📋 Create personalized action plan for income generation"""

    def post(self, request):
        """Create action plan for selected opportunity"""
        try:
            user_id = str(request.user.id) if request.user.is_authenticated else "anonymous"
            opportunity_id = request.data.get('opportunity_id')

            if not opportunity_id:
                return Response({
                    'error': 'opportunity_id is required',
                    'success': False
                }, status=status.HTTP_400_BAD_REQUEST)

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
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Action plan error: {e}")
            return Response({
                'error': f'Failed to create action plan: {str(e)}',
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExecuteActionPlanView(APIView):
    """🚀 Save and execute an action plan.

    I-0301 Phase 3 Stage 2b — Bucket B remediation. Prior AllowAny + the
    "user = ... else None" write path allowed anonymous plan creation
    with no ownership; the GET path had an explicit anonymous branch
    returning any recent user__isnull=True plan across all sessions
    (cross-tenant view). Both branches are removed; IsAuthenticated is
    the sole entry.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Save action plan to database and start execution."""
        try:
            plan_data = request.data.get('plan', {})
            opportunity = request.data.get('opportunity', {})

            if not plan_data or not opportunity:
                return Response({
                    'error': 'Missing plan or opportunity data',
                    'success': False
                }, status=status.HTTP_400_BAD_REQUEST)

            # Extract steps from plan_data
            steps = []

            # First check if there's a direct 'steps' field
            if 'steps' in plan_data and plan_data['steps']:
                steps = plan_data['steps']
            # Otherwise extract from week_by_week structure
            elif 'week_by_week' in plan_data:
                for week in plan_data['week_by_week']:
                    if 'tasks' in week:
                        for task in week['tasks']:
                            steps.append(f"Week {week.get('week', '?')}: {task}")
            # Fallback to daily_tasks if available
            elif 'daily_tasks' in plan_data:
                for time_period, tasks in plan_data['daily_tasks'].items():
                    for task in tasks:
                        steps.append(f"{time_period.capitalize()}: {task}")

            # If still no steps, create a basic set
            if not steps:
                steps = [
                    "Research and preparation",
                    "Initial implementation",
                    "Testing and refinement",
                    "Launch and monitor"
                ]

            # Create ActionPlan in database
            # IsAuthenticated guarantees request.user is a real user.
            action_plan = ActionPlan.objects.create(
                user=request.user,
                opportunity_id=opportunity.get('id', ''),
                opportunity_title=opportunity.get('title', 'Unknown Opportunity'),
                opportunity_data=opportunity,
                plan_data=plan_data,
                steps=steps,
                resources=plan_data.get('resources', []),
                timeline=plan_data.get('timeline', ''),
                expected_outcome=plan_data.get('expected_outcome', '')
            )

            # Start execution
            celery_task_id = action_plan.start_execution()

            return Response({
                'success': True,
                'plan_id': str(action_plan.id),
                'celery_task_id': celery_task_id,
                'status': action_plan.status,
                'message': 'Action plan saved and execution started'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Execute action plan error: {e}")
            return Response({
                'error': f'Failed to execute action plan: {str(e)}',
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Get status of action plans owned by the requesting user.

        Prior anonymous branch returning `user__isnull=True` recent 24h
        plans (cross-tenant view) removed per Rigby S2742 Stage 2b SIGN.
        """
        try:
            # IsAuthenticated at view level; scope to user's plans only.
            plans = ActionPlan.objects.filter(
                user=request.user
            ).order_by('-created_at')

            plans_data = []
            for plan in plans[:20]:  # Limit to 20 most recent
                plans_data.append({
                    'id': str(plan.id),
                    'opportunity_title': plan.opportunity_title,
                    'status': plan.status,
                    'progress': plan.progress,
                    'current_step': plan.current_step,
                    'total_steps': len(plan.steps) if plan.steps else 0,
                    'created_at': plan.created_at.isoformat(),
                    'started_at': plan.started_at.isoformat() if plan.started_at else None,
                    'completed_at': plan.completed_at.isoformat() if plan.completed_at else None,
                    'execution_logs': plan.execution_logs[-10:] if plan.execution_logs else [],  # Last 10 logs
                    'results': plan.results or {},  # Always include results for progressive updates
                    'steps': plan.steps,  # Include steps for display
                    'resources': plan.resources
                })

            return Response({
                'success': True,
                'plans': plans_data,
                'count': len(plans_data)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Get action plans error: {e}")
            return Response({
                'error': f'Failed to get action plans: {str(e)}',
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ViewGeneratedFileView(APIView):
    """View generated Income Builder files.

    I-0301 Phase 3 Stage 2b — Bucket B remediation with per-file
    ownership check (Rigby S2742 Stage 2b SIGN Q3 material amendment:
    exact basename match, not `endswith`). Prior AllowAny + shared
    filesystem read meant any anonymous caller could enumerate + read
    any user's generated files. Now:

    1. IsAuthenticated required.
    2. Filename param must exactly match the basename of a ``file_path``
       stored in ``plan_data`` on an ``ActionPlan`` owned by the
       requesting user. Foreign-owned filenames → 404 (per Rigby SIGN
       Q6 existence-oracle avoidance).
    3. Path traversal check retained.

    Filesystem migration to per-user subdirectories is out of Stage 2b
    scope (I-0302 / dedicated arc); ownership check via ActionPlan
    plan_data is the minimal safe scoping.
    """
    permission_classes = [IsAuthenticated]

    def _user_owns_filename(self, user, filename: str) -> bool:
        """Return True iff the requested filename basename matches the
        basename of a ``file_path`` in ``plan_data`` on any of the
        user's ActionPlans. Exact basename equality — no suffix match
        (Rigby SIGN Q3).
        """
        import os

        requested_basename = os.path.basename(filename)
        # Iterate the user's plans; extract every string-typed
        # file-path-adjacent value from plan_data and compare basenames.
        for plan in ActionPlan.objects.filter(user=user).only('plan_data'):
            plan_data = plan.plan_data or {}
            for value in _iter_string_values(plan_data):
                if os.path.basename(value) == requested_basename:
                    return True
        return False

    def get(self, request, filename):
        """Get content of a generated file, gated by ownership."""
        from pathlib import Path
        import os
        import urllib.parse

        try:
            # Decode URL-encoded filename (handles spaces and special characters)
            decoded_filename = urllib.parse.unquote(filename)

            # Ownership check BEFORE any filesystem access — foreign-owned
            # filenames get a 404 (not 403) to avoid existence oracle.
            if not self._user_owns_filename(request.user, decoded_filename):
                return Response({
                    'error': 'File not found',
                    'success': False
                }, status=status.HTTP_404_NOT_FOUND)

            # Security check - only allow files in income_builder_outputs
            file_path = Path("income_builder_outputs") / decoded_filename

            # Ensure the file is within the allowed directory (resolve to prevent path traversal)
            try:
                resolved_path = file_path.resolve()
                allowed_dir = Path("income_builder_outputs").resolve()
                if not str(resolved_path).startswith(str(allowed_dir)):
                    return Response({
                        'error': 'Invalid file path',
                        'success': False
                    }, status=status.HTTP_403_FORBIDDEN)
            except:
                return Response({
                    'error': 'Invalid file path',
                    'success': False
                }, status=status.HTTP_403_FORBIDDEN)

            # Check if file exists
            if not file_path.exists():
                # Try to find the file in a subdirectory
                # For files like AI-Powered_Social_Media_Management_Complete_Plan.md
                # that might be in "AI Social Media Management/" subdirectory

                # Try common subdirectory patterns
                possible_subdirs = [
                    "AI Social Media Management",
                    "AI-Powered Social Media Management",
                    "AI_Social_Media_Management"
                ]

                for subdir in possible_subdirs:
                    alt_path = Path("income_builder_outputs") / subdir / decoded_filename
                    if alt_path.exists():
                        file_path = alt_path
                        break

                # If still not found, try to find it by searching
                if not file_path.exists():
                    import glob
                    search_pattern = f"income_builder_outputs/**/{decoded_filename}"
                    matches = glob.glob(search_pattern, recursive=True)
                    if matches:
                        file_path = Path(matches[0])

            # Final check if file exists
            if not file_path.exists():
                return Response({
                    'error': 'File not found',
                    'success': False
                }, status=status.HTTP_404_NOT_FOUND)

            # Read file content
            with open(file_path, 'r') as f:
                content = f.read()

            return Response({
                'success': True,
                'filename': filename,
                'content': content,
                'size': os.path.getsize(file_path),
                'type': 'markdown' if filename.endswith('.md') else 'text'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error reading file {filename}: {e}")
            return Response({
                'error': f'Failed to read file: {str(e)}',
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RevenueOpportunitiesView(APIView):
    """API endpoint for submitting and listing revenue opportunities.

    I-0301 Phase 3 Stage 2b — Bucket B remediation. Prior AllowAny +
    ActionPlan creates without a user field left orphan rows and let the
    GET list every opportunity across all users. Now:

    1. IsAuthenticated required.
    2. POST attaches ``user=request.user`` on the created ActionPlan;
       OpportunityActionPlan inherits ownership via ``action_plan`` FK.
    3. GET filters via ``action_plan__user=request.user`` — Rigby S2742
       Stage 2b SIGN Q5 accepted empty list for users with no plans.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Submit a new revenue opportunity for processing"""
        try:
            from .revenue_integration import RevenueIncomeIntegration
            from intelligence.models import OpportunityActionPlan, ActionPlan

            integration = RevenueIncomeIntegration()
            opportunity_data = request.data

            # Process the opportunity asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                integration.process_opportunity(opportunity_data)
            )

            if result['success']:
                # Create database record
                plan_data = result['plan']
                # IsAuthenticated guarantees request.user is a real user;
                # attach ownership so OpportunityActionPlan inherits.
                action_plan = ActionPlan.objects.create(
                    user=request.user,
                    opportunity_id=opportunity_data.get('id', 'unknown'),
                    opportunity_title=opportunity_data.get('title', 'Unknown'),
                    opportunity_data=opportunity_data,
                    plan_data=plan_data,
                    status='created'
                )

                opp_plan = OpportunityActionPlan.objects.create(
                    opportunity_id=opportunity_data.get('id'),
                    platform=opportunity_data.get('platform', 'unknown'),
                    opportunity_data=opportunity_data,
                    action_plan=action_plan,
                    proposal_content=result['proposal'].get('content', ''),
                    bid_amount=result['proposal'].get('bid_amount'),
                    success_score=result.get('success_probability', 0),
                    status='plan_created'
                )

                return Response({
                    'success': True,
                    'opportunity_plan_id': str(opp_plan.id),
                    'action_plan_id': str(action_plan.id),
                    'proposal': result['proposal'],
                    'files': result['files'],
                    'success_probability': result.get('success_probability', 0)
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Failed to process opportunity')
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error processing revenue opportunity: {e}")
            return Response({
                'error': str(e),
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """List revenue opportunities owned by the requesting user."""
        try:
            from intelligence.models import OpportunityActionPlan

            # Get query parameters
            platform = request.query_params.get('platform')
            status_filter = request.query_params.get('status')
            limit = int(request.query_params.get('limit', 20))

            # Scope via action_plan__user (OpportunityActionPlan has no
            # direct user FK; ownership travels through ActionPlan).
            queryset = OpportunityActionPlan.objects.filter(
                action_plan__user=request.user
            )

            if platform:
                queryset = queryset.filter(platform=platform)
            if status_filter:
                queryset = queryset.filter(status=status_filter)

            opportunities = queryset[:limit]

            return Response({
                'success': True,
                'count': opportunities.count(),
                'opportunities': [
                    {
                        'id': str(opp.id),
                        'opportunity_id': opp.opportunity_id,
                        'platform': opp.platform,
                        'status': opp.status,
                        'success_score': opp.success_score,
                        'priority_level': opp.priority_level,
                        'revenue_generated': float(opp.revenue_generated),
                        'created_at': opp.created_at.isoformat(),
                        'submitted_at': opp.submitted_at.isoformat() if opp.submitted_at else None
                    }
                    for opp in opportunities
                ]
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error listing opportunities: {e}")
            return Response({
                'error': str(e),
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubmitProposalView(APIView):
    """API endpoint for submitting proposals to platforms.

    I-0301 Phase 3 Stage 2b — Bucket B remediation with per-object
    ownership check. Prior AllowAny + unfiltered
    ``OpportunityActionPlan.objects.get(id=...)`` let any authenticated
    (after IsAuthenticated) user submit ANY other user's proposal. Now
    scoped via ``action_plan__user=request.user``; foreign-owned rows
    return 404 (Rigby S2742 Stage 2b SIGN Q6 existence-oracle avoidance).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Submit a proposal to a platform (only if user owns it)."""
        try:
            from .revenue_integration import RevenueIncomeIntegration
            from intelligence.models import OpportunityActionPlan

            proposal_data = request.data
            opportunity_plan_id = proposal_data.get('opportunity_plan_id')

            if not opportunity_plan_id:
                return Response({
                    'error': 'opportunity_plan_id is required',
                    'success': False
                }, status=status.HTTP_400_BAD_REQUEST)

            # Ownership-scoped lookup; foreign-owned → 404 to avoid
            # existence oracle.
            try:
                opp_plan = OpportunityActionPlan.objects.get(
                    id=opportunity_plan_id,
                    action_plan__user=request.user,
                )
            except OpportunityActionPlan.DoesNotExist:
                return Response({
                    'error': 'Opportunity plan not found',
                    'success': False
                }, status=status.HTTP_404_NOT_FOUND)

            # Submit the proposal
            integration = RevenueIncomeIntegration()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            submission_result = loop.run_until_complete(
                integration.auto_submit_proposal({
                    'id': opp_plan.proposal_id or f"prop_{opp_plan.id}",
                    'platform': opp_plan.platform,
                    'content': opp_plan.proposal_content,
                    'bid_amount': str(opp_plan.bid_amount) if opp_plan.bid_amount else None
                })
            )

            if submission_result['success']:
                # Update the opportunity plan status
                opp_plan.update_status('proposal_submitted',
                                      proposal_id=submission_result.get('submission_id'))

                return Response({
                    'success': True,
                    'submission_id': submission_result.get('submission_id'),
                    'submitted_at': submission_result.get('submitted_at')
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': submission_result.get('error', 'Submission failed')
                }, status=status.HTTP_400_BAD_REQUEST)

        except OpportunityActionPlan.DoesNotExist:
            return Response({
                'error': 'Opportunity plan not found',
                'success': False
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error submitting proposal: {e}")
            return Response({
                'error': str(e),
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RevenueMetricsView(APIView):
    """API endpoint for revenue metrics and analytics.

    I-0301 Phase 3 Stage 2b — Bucket B remediation. Prior AllowAny +
    unfiltered aggregate query returned platform-wide revenue metrics
    to any anonymous caller (biggest cross-tenant leak in the intelligence
    module). Now scoped per-user via ``action_plan__user=request.user``
    (Rigby S2742 Stage 2b SIGN Q7 accepted per-user over staff-only).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get revenue metrics scoped to the requesting user."""
        try:
            from intelligence.models import OpportunityActionPlan, RevenueMetrics
            from django.db.models import Sum, Avg
            from django.utils import timezone
            from datetime import timedelta

            # Get date range
            days = int(request.query_params.get('days', 30))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)

            # Scope aggregation to the requesting user's opportunities.
            opportunities = OpportunityActionPlan.objects.filter(
                action_plan__user=request.user,
                created_at__date__gte=start_date,
            )

            metrics = {
                'total_opportunities': opportunities.count(),
                'proposals_submitted': opportunities.filter(
                    status__in=['proposal_submitted', 'awaiting_response',
                               'client_responded', 'negotiating', 'converted']
                ).count(),
                'responses_received': opportunities.filter(
                    status__in=['client_responded', 'negotiating', 'converted', 'rejected']
                ).count(),
                'conversions': opportunities.filter(status='converted').count(),
                'total_revenue': float(
                    opportunities.filter(status='converted').aggregate(
                        Sum('revenue_generated')
                    )['revenue_generated__sum'] or 0
                ),
                'average_deal_size': float(
                    opportunities.filter(status='converted').aggregate(
                        Avg('revenue_generated')
                    )['revenue_generated__avg'] or 0
                ),
                'platform_breakdown': {}
            }

            # Calculate rates
            if metrics['proposals_submitted'] > 0:
                metrics['response_rate'] = (
                    metrics['responses_received'] / metrics['proposals_submitted']
                ) * 100
            else:
                metrics['response_rate'] = 0

            if metrics['responses_received'] > 0:
                metrics['conversion_rate'] = (
                    metrics['conversions'] / metrics['responses_received']
                ) * 100
            else:
                metrics['conversion_rate'] = 0

            # Platform breakdown
            for platform in opportunities.values_list('platform', flat=True).distinct():
                platform_opps = opportunities.filter(platform=platform)
                metrics['platform_breakdown'][platform] = {
                    'count': platform_opps.count(),
                    'submitted': platform_opps.filter(
                        status__in=['proposal_submitted', 'awaiting_response',
                                   'client_responded', 'negotiating', 'converted']
                    ).count(),
                    'converted': platform_opps.filter(status='converted').count(),
                    'revenue': float(
                        platform_opps.filter(status='converted').aggregate(
                            Sum('revenue_generated')
                        )['revenue_generated__sum'] or 0
                    )
                }

            # Update daily metrics
            RevenueMetrics.update_metrics_for_date(timezone.now().date())

            return Response({
                'success': True,
                'metrics': metrics,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return Response({
                'error': str(e),
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExecuteAgentPlanView(APIView):
    """🤖 Execute an action plan through the agent network.

    I-0301 Phase 3 Stage 2b — Bucket B remediation. Prior AllowAny +
    unfiltered ``ActionPlan.objects.get(id=plan_id)`` let any
    authenticated user trigger execution of ANY other user's plan.
    Ownership check ``user=request.user`` applied on every lookup;
    foreign-owned rows return 404 to avoid existence oracle (Rigby
    S2742 Stage 2b SIGN Q8).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Trigger agent execution for a plan owned by the requesting user."""
        try:
            plan_id = request.data.get('plan_id')

            if not plan_id:
                return Response({
                    'error': 'plan_id is required',
                    'success': False
                }, status=status.HTTP_400_BAD_REQUEST)

            # Ownership-scoped lookup.
            try:
                plan = ActionPlan.objects.get(id=plan_id, user=request.user)
            except ActionPlan.DoesNotExist:
                return Response({
                    'error': 'Plan not found',
                    'success': False
                }, status=status.HTTP_404_NOT_FOUND)

            # Check if plan is ready for execution
            if plan.status != 'completed':
                # For now, allow execution of any plan with content
                if not plan.results or not plan.results.get('files_created'):
                    return Response({
                        'error': 'Plan must be completed before execution',
                        'success': False
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Trigger async execution through Celery
            result = execute_plan_async.delay(str(plan_id))

            # Update plan status
            plan.status = 'executing'
            plan.save()

            return Response({
                'success': True,
                'message': 'Agent execution started',
                'plan_id': str(plan_id),
                'task_id': str(result.id),
                'status': 'executing'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error triggering agent execution: {e}")
            return Response({
                'error': str(e),
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Get execution status for a plan owned by the requesting user."""
        try:
            plan_id = request.query_params.get('plan_id')

            if not plan_id:
                return Response({
                    'error': 'plan_id is required',
                    'success': False
                }, status=status.HTTP_400_BAD_REQUEST)

            # Ownership-scoped lookup per Rigby S2742 Stage 2b SIGN
            # "ownership checks on every object lookup" must-add.
            try:
                plan = ActionPlan.objects.get(id=plan_id, user=request.user)
            except ActionPlan.DoesNotExist:
                return Response({
                    'error': 'Plan not found',
                    'success': False
                }, status=status.HTTP_404_NOT_FOUND)

            # Parse instructions to show what would be executed
            parser = AgentInstructionParser()

            # Get plan content
            content = ""
            if plan.results and plan.results.get('files_created'):
                # Try to load the complete plan file
                files = plan.results.get('files_created', [])
                for file_path in files:
                    if 'Complete_Plan' in file_path:
                        try:
                            import os
                            full_path = os.path.join('income_builder_outputs', file_path.split('/')[-1])
                            if os.path.exists(full_path):
                                with open(full_path, 'r') as f:
                                    content = f.read()
                                break
                        except:
                            pass

            instructions = []
            if content:
                instructions = parser.parse_plan(content)

            # Get execution results if any
            agent_executions = plan.results.get('agent_executions', []) if plan.results else []

            return Response({
                'success': True,
                'plan_id': str(plan_id),
                'status': plan.status,
                'progress': plan.progress,
                'instructions_count': len(instructions),
                'instructions': parser.to_json() if instructions else [],
                'executions': agent_executions,
                'can_execute': len(instructions) > 0
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error getting execution status: {e}")
            return Response({
                'error': str(e),
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
