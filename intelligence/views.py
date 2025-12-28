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
from rest_framework.permissions import AllowAny
from django.conf import settings

from .realtime_engine import intelligence_engine
from .income_builder import income_builder, UserProfile, SkillLevel
from .models import ActionPlan
from .agent_instruction_parser import AgentInstructionParser
from .agent_execution_pipeline import execute_plan_async

logger = logging.getLogger(__name__)


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
    """📂 Save and retrieve action plans for persistence across sessions"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get all action plans for the current user/session"""
        try:
            import os
            import glob
            from datetime import datetime, timedelta
            from django.utils import timezone

            # Load plans from filesystem (since database approach was disabled)
            plans_dir = os.path.join(settings.BASE_DIR, 'income_builder_outputs')

            # Find all Complete_Plan.md files (main plans)
            complete_plans = glob.glob(os.path.join(plans_dir, '*_Complete_Plan.md'))

            # Filter to recent plans (last 7 days)
            cutoff = timezone.now() - timedelta(days=7)
            recent_plans = []

            for plan_file in complete_plans:
                try:
                    # Get file modification time
                    mod_time = datetime.fromtimestamp(os.path.getmtime(plan_file))
                    mod_time = timezone.make_aware(mod_time)

                    if mod_time >= cutoff:
                        # Extract opportunity title from filename
                        filename = os.path.basename(plan_file)
                        opportunity_title = filename.replace('_Complete_Plan.md', '').replace('_', ' ')

                        # Check for associated QuickStart file
                        quickstart_file = plan_file.replace('_Complete_Plan.md', '_QuickStart.md')
                        has_quickstart = os.path.exists(quickstart_file)

                        # Count associated step files
                        step_pattern = plan_file.replace('_Complete_Plan.md', '_step_*.md')
                        step_files = glob.glob(step_pattern)

                        recent_plans.append({
                            'file_path': plan_file,
                            'opportunity_title': opportunity_title,
                            'created_at': mod_time,
                            'has_quickstart': has_quickstart,
                            'step_count': len(step_files),
                            'quickstart_path': quickstart_file if has_quickstart else None
                        })
                except Exception as e:
                    continue

            # Sort by creation time (newest first)
            recent_plans.sort(key=lambda x: x['created_at'], reverse=True)

            # Serialize plans for frontend
            serialized_plans = []
            for i, plan in enumerate(recent_plans[:10]):  # Limit to 10 most recent
                # Create a unique ID based on the filename and timestamp
                plan_id = f"file_{hash(plan['file_path'])}_{int(plan['created_at'].timestamp())}"

                serialized_plans.append({
                    'id': plan_id,
                    'backend_id': plan_id,
                    'opportunity_id': plan['opportunity_title'].lower().replace(' ', '_'),
                    'opportunity_title': plan['opportunity_title'],
                    'opportunity_data': {
                        'title': plan['opportunity_title'],
                        'description': f"AI-generated action plan for {plan['opportunity_title']}",
                        'file_path': plan['file_path'],
                        'step_count': plan['step_count']
                    },
                    'plan_data': {
                        'file_path': plan['file_path'],
                        'quickstart_path': plan.get('quickstart_path'),
                        'has_quickstart': plan['has_quickstart']
                    },
                    'steps': [f"Step {i+1}" for i in range(plan['step_count'])],
                    'resources': [],
                    'timeline': '4 weeks',
                    'expected_outcome': f"Complete {plan['opportunity_title']} implementation",
                    'status': 'completed',
                    'progress': 100,
                    'current_step': plan['step_count'],
                    'completed_steps': list(range(1, plan['step_count'] + 1)),
                    'execution_logs': [],
                    'results': {},
                    'created_at': plan['created_at'].isoformat(),
                    'started_at': plan['created_at'].isoformat(),
                    'completed_at': plan['created_at'].isoformat(),
                    'celery_task_id': None,
                    'file_path': f"/static/{os.path.basename(plan['file_path'])}",
                    'quickstart_file_path': f"/static/{os.path.basename(plan['quickstart_path'])}" if plan.get('quickstart_path') else None
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
        """Helper to create a new action plan"""
        try:
            # Handle user
            user = request.user if request.user.is_authenticated else None

            # For anonymous users, prefix the opportunity_id with session
            opportunity_id = plan_data.get('opportunity_id')
            if not user and request.session.session_key:
                opportunity_id = f"anon_{request.session.session_key}_{opportunity_id}"

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
    """🚀 Save and execute an action plan"""
    permission_classes = [AllowAny]  # Allow testing without authentication

    def post(self, request):
        """Save action plan to database and start execution"""
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
            action_plan = ActionPlan.objects.create(
                user=request.user if request.user.is_authenticated else None,
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
        """Get status of action plans"""
        try:
            # Get user's action plans
            if request.user.is_authenticated:
                plans = ActionPlan.objects.filter(user=request.user).order_by('-created_at')
            else:
                # For anonymous users, get recent plans (last 24 hours)
                from django.utils import timezone
                from datetime import timedelta
                cutoff = timezone.now() - timedelta(hours=24)
                plans = ActionPlan.objects.filter(
                    user__isnull=True,
                    created_at__gte=cutoff
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
    """View generated Income Builder files"""
    permission_classes = [AllowAny]

    def get(self, request, filename):
        """Get content of a generated file"""
        from pathlib import Path
        import os
        import urllib.parse

        try:
            # Decode URL-encoded filename (handles spaces and special characters)
            decoded_filename = urllib.parse.unquote(filename)

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
    """API endpoint for submitting and listing revenue opportunities"""
    permission_classes = [AllowAny]

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
                action_plan = ActionPlan.objects.create(
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
        """List all revenue opportunities"""
        try:
            from intelligence.models import OpportunityActionPlan

            # Get query parameters
            platform = request.query_params.get('platform')
            status_filter = request.query_params.get('status')
            limit = int(request.query_params.get('limit', 20))

            # Build query
            queryset = OpportunityActionPlan.objects.all()

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
    """API endpoint for submitting proposals to platforms"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Submit a proposal to a platform"""
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

            # Get the opportunity plan
            opp_plan = OpportunityActionPlan.objects.get(id=opportunity_plan_id)

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
    """API endpoint for revenue metrics and analytics"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get revenue metrics"""
        try:
            from intelligence.models import OpportunityActionPlan, RevenueMetrics
            from django.db.models import Sum, Avg
            from django.utils import timezone
            from datetime import timedelta

            # Get date range
            days = int(request.query_params.get('days', 30))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)

            # Calculate metrics
            opportunities = OpportunityActionPlan.objects.filter(
                created_at__date__gte=start_date
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
    """🤖 Execute an action plan through the agent network"""
    permission_classes = [AllowAny]

    def post(self, request):
        """Trigger agent execution for a plan"""
        try:
            plan_id = request.data.get('plan_id')

            if not plan_id:
                return Response({
                    'error': 'plan_id is required',
                    'success': False
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the plan
            try:
                plan = ActionPlan.objects.get(id=plan_id)
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
        """Get execution status for a plan"""
        try:
            plan_id = request.query_params.get('plan_id')

            if not plan_id:
                return Response({
                    'error': 'plan_id is required',
                    'success': False
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the plan
            try:
                plan = ActionPlan.objects.get(id=plan_id)
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
