"""
Partnership Views - Human-AI Collaboration Features

NEW (Session Pre-38): Views for partnership mode
These are SEPARATE from existing views - won't interfere with current functionality

IMPORTANT: This is independent from learning loop integration (Session 37-A)
- Learning loop: No views, backend only
- Partnership: Has views for user interaction
- NO interference
"""

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Avg
from decimal import Decimal

from .models_unified_system import Opportunity
from .models_partnership import PartnershipProject, CollaborativeContent

logger = logging.getLogger(__name__)


@login_required
def partnership_dashboard(request):
    """
    Main partnership dashboard showing human-AI collaboration metrics

    This is SEPARATE from the existing dashboard - both can coexist
    Users can toggle between traditional and partnership views
    """
    user = request.user

    # Active partnership projects
    active_projects = PartnershipProject.objects.filter(
        user=user,
        status__in=['planning', 'in_progress', 'review']
    ).select_related('opportunity')

    # Completed projects
    completed_projects = PartnershipProject.objects.filter(
        user=user,
        status='completed'
    ).select_related('opportunity')

    # Calculate aggregate metrics
    total_earned = completed_projects.aggregate(
        total=Sum('payment_received')
    )['total'] or Decimal('0.00')

    total_human_time = completed_projects.aggregate(
        total=Sum('human_time_actual')
    )['total'] or Decimal('0.00')

    total_ai_time = completed_projects.aggregate(
        total=Sum('ai_time_equivalent')
    )['total'] or Decimal('0.00')

    # Calculate partnership value
    if float(total_human_time) > 0:
        effective_rate = float(total_earned) / float(total_human_time)
        time_saved = float(total_ai_time)
        solo_hours = float(total_ai_time) + float(total_human_time)
        efficiency = solo_hours / float(total_human_time) if float(total_human_time) > 0 else 0
    else:
        effective_rate = 0
        time_saved = 0
        efficiency = 0

    avg_ai_contribution = completed_projects.aggregate(
        avg=Avg('ai_contribution_percent')
    )['avg'] or 0

    # Partnership opportunities (high collaboration potential)
    partnership_opportunities = Opportunity.objects.filter(
        user=user,
        collaboration_feasibility__in=['high', 'ideal'],
        status='active'
    ).order_by('-ai_contribution_potential')[:10]

    # Recent content created
    recent_content = CollaborativeContent.objects.filter(
        partnership_project__user=user
    ).order_by('-created_at')[:5]

    context = {
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'recent_content': recent_content,

        # The PROOF of partnership value
        'total_earned': total_earned,
        'effective_hourly_rate': round(effective_rate, 2),
        'time_saved_by_ai': round(time_saved, 1),
        'efficiency_multiplier': round(efficiency, 2),
        'avg_ai_contribution': round(avg_ai_contribution, 0),

        'partnership_opportunities': partnership_opportunities,

        # Stats
        'projects_completed': completed_projects.count(),
        'projects_active': active_projects.count(),
        'total_projects': completed_projects.count() + active_projects.count(),
    }

    return render(request, 'unified/partnership_dashboard.html', context)


@login_required
def start_partnership(request, opportunity_id):
    """
    Start a partnership project from an opportunity

    Creates PartnershipProject and initial workflow
    """
    opportunity = get_object_or_404(Opportunity, id=opportunity_id, user=request.user)

    if request.method == 'POST':
        project_name = request.POST.get('project_name', opportunity.title)
        project_type = request.POST.get('project_type', 'content_creation')

        # Create partnership project
        project = PartnershipProject.objects.create(
            opportunity=opportunity,
            user=request.user,
            project_name=project_name,
            project_type=project_type,
            description=opportunity.description,
            contract_value=opportunity.potential_revenue,
            workflow_steps=opportunity.partnership_workflow or [],
            status='planning'
        )

        logger.info(f"Started partnership project: {project.project_name} (ID: {project.id})")

        # Redirect to project detail
        return redirect('partnership-project-detail', project_id=project.id)

    # GET request - show confirmation page
    context = {
        'opportunity': opportunity,
        'partnership_metrics': opportunity.calculate_partnership_metrics(),
    }

    return render(request, 'unified/start_partnership.html', context)


@login_required
def partnership_project_detail(request, project_id):
    """
    Detail view for a partnership project

    Shows collaboration progress, contributions, metrics
    """
    project = get_object_or_404(
        PartnershipProject,
        id=project_id,
        user=request.user
    )

    # Calculate current metrics
    roi_metrics = project.calculate_partnership_roi()

    # Get all content pieces for this project
    content_pieces = project.content_pieces.all().order_by('-created_at')

    context = {
        'project': project,
        'roi_metrics': roi_metrics,
        'content_pieces': content_pieces,
        'ai_contributions': project.ai_contributions,
        'human_contributions': project.human_contributions,
    }

    return render(request, 'unified/partnership_project_detail.html', context)


@login_required
def add_ai_contribution(request, project_id):
    """
    API endpoint to track an AI contribution

    Called when AI agent completes a task
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    project = get_object_or_404(
        PartnershipProject,
        id=project_id,
        user=request.user
    )

    agent_name = request.POST.get('agent_name')
    task = request.POST.get('task')
    time_saved = request.POST.get('time_saved_hours', 0)
    output_summary = request.POST.get('output_summary')

    try:
        contribution = project.add_ai_contribution(
            agent_name=agent_name,
            task=task,
            time_saved_hours=float(time_saved),
            output_summary=output_summary
        )

        project.update_contribution_percentages()

        return JsonResponse({
            'success': True,
            'contribution': contribution,
            'ai_contribution_percent': project.ai_contribution_percent
        })

    except Exception as e:
        logger.error(f"Error adding AI contribution: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def add_human_contribution(request, project_id):
    """
    API endpoint to track a human contribution

    Called when user completes their part
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    project = get_object_or_404(
        PartnershipProject,
        id=project_id,
        user=request.user
    )

    task = request.POST.get('task')
    time_spent = request.POST.get('time_spent_hours', 0)
    value_added = request.POST.get('value_added')

    try:
        contribution = project.add_human_contribution(
            task=task,
            time_spent_hours=float(time_spent),
            value_added=value_added
        )

        project.update_contribution_percentages()

        return JsonResponse({
            'success': True,
            'contribution': contribution,
            'human_contribution_percent': project.human_contribution_percent
        })

    except Exception as e:
        logger.error(f"Error adding human contribution: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def complete_partnership(request, project_id):
    """
    Mark partnership project as complete and track payment
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    project = get_object_or_404(
        PartnershipProject,
        id=project_id,
        user=request.user
    )

    payment_received = request.POST.get('payment_received', project.contract_value)

    try:
        project.mark_completed(payment_received=payment_received)

        # Calculate final metrics
        roi_metrics = project.calculate_partnership_roi()

        # === SESSION 40: CREATE LEARNING ENTRY ===
        # Connect partnership success to learning loop
        try:
            from core.models_unified_system import UserAgentLearning

            # Create learning entry for partnership success
            learning_entry = UserAgentLearning.objects.create(
                user=request.user,
                agent_name='PartnershipOrchestrator',
                learning_domain='partnership_success',
                learning_source='performance_tracking',

                # Store all partnership data in learning_content JSONField
                learning_content={
                    # Partnership metadata
                    'context': {
                        'project_id': str(project.id),
                        'project_name': project.project_name,
                        'project_type': project.project_type,
                        'opportunity_id': str(project.opportunity.id) if project.opportunity else None,
                    },

                    # Outcome metrics
                    'outcomes': {
                        'payment_received': float(payment_received),
                        'ai_contribution_percent': project.ai_contribution_percent,
                        'human_contribution_percent': project.human_contribution_percent,
                        'efficiency_multiplier': float(roi_metrics['efficiency_multiplier']),
                        'effective_hourly_rate': float(roi_metrics['effective_hourly_rate']),
                        'time_saved_hours': float(roi_metrics['time_saved_hours']),
                    },

                    # Learning insights
                    'insights': {
                        'what_worked': project.what_worked,
                        'what_to_improve': project.what_to_improve,
                        'lessons_learned': project.lessons_learned,
                        'partnership_workflow': project.workflow_steps,
                    },

                    # Feedback metadata
                    'feedback_type': 'positive',  # Successful partnership
                    'strength': float(roi_metrics['efficiency_multiplier']),  # Stronger if more efficient
                },

                # Set confidence based on efficiency
                confidence_score=min(0.5 + (roi_metrics['efficiency_multiplier'] / 10), 1.0),
                validation_count=1,  # This partnership validated the approach
            )

            logger.info(
                f"✅ Created learning entry from partnership: "
                f"{project.ai_contribution_percent}% AI, "
                f"{roi_metrics['efficiency_multiplier']}x efficiency"
            )

        except Exception as learning_error:
            # Don't fail the completion if learning entry fails
            logger.error(f"Failed to create learning entry: {learning_error}")
        # === END SESSION 40 CODE ===

        logger.info(
            f"Partnership project completed: {project.project_name} - "
            f"${payment_received} earned in {project.human_time_actual}h "
            f"({roi_metrics['efficiency_multiplier']}x faster)"
        )

        return JsonResponse({
            'success': True,
            'roi_metrics': roi_metrics,
            'message': 'Partnership completed! 🎉'
        })

    except Exception as e:
        logger.error(f"Error completing partnership: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def partnership_opportunities_api(request):
    """
    API endpoint to get partnership opportunities with collaboration potential

    Returns opportunities sorted by AI contribution potential
    """
    user = request.user

    # Get opportunities with high collaboration potential
    opportunities = Opportunity.objects.filter(
        user=user,
        status='active',
        collaboration_feasibility__in=['medium', 'high', 'ideal']
    ).order_by('-ai_contribution_potential')[:20]

    # Serialize opportunities
    opportunities_data = []
    for opp in opportunities:
        metrics = opp.calculate_partnership_metrics()
        opportunities_data.append({
            'id': str(opp.id),
            'title': opp.title,
            'description': opp.description[:200],
            'potential_revenue': float(opp.potential_revenue),
            'opportunity_type': opp.opportunity_type,
            'partnership_mode': opp.partnership_mode,
            'ai_contribution_potential': opp.ai_contribution_potential,
            'collaboration_feasibility': opp.collaboration_feasibility,
            'metrics': metrics if metrics.get('available') else None,
        })

    return JsonResponse({
        'opportunities': opportunities_data,
        'count': len(opportunities_data)
    })


@login_required
def partnership_stats_api(request):
    """
    API endpoint to get aggregate partnership statistics

    Used for dashboard widgets and real-time updates
    """
    user = request.user

    # Get all completed projects
    completed = PartnershipProject.objects.filter(
        user=user,
        status='completed'
    )

    # Calculate totals
    total_earned = completed.aggregate(Sum('payment_received'))['payment_received__sum'] or Decimal('0.00')
    total_projects = completed.count()
    avg_ai_contribution = completed.aggregate(Avg('ai_contribution_percent'))['ai_contribution_percent__avg'] or 0

    # Active projects
    active = PartnershipProject.objects.filter(
        user=user,
        status__in=['planning', 'in_progress', 'review']
    ).count()

    return JsonResponse({
        'total_earned': float(total_earned),
        'projects_completed': total_projects,
        'projects_active': active,
        'avg_ai_contribution': round(avg_ai_contribution, 1),
    })


# Helper function (not a view)
def assess_opportunity_partnership_potential(opportunity):
    """
    Assess whether an opportunity is good for human-AI partnership

    This can be called by opportunity analyzers/spiders
    Returns updated opportunity with partnership fields set
    """
    # Simple heuristic-based assessment
    # Can be enhanced with ML/AI analysis later

    # Content creation opportunities are ideal for partnership
    content_types = ['content_creation', 'writing', 'blog_post', 'article', 'copywriting']
    if any(ct in opportunity.opportunity_type.lower() for ct in content_types):
        opportunity.collaboration_feasibility = 'ideal'
        opportunity.ai_contribution_potential = 70
        opportunity.partnership_mode = 'collaborative'

        # Estimate time savings
        # Assume AI can draft in 2 hours, human refines in 2 hours
        opportunity.estimated_solo_hours = Decimal('6.0')
        opportunity.estimated_partnership_hours = Decimal('2.0')

    # Data analysis / research
    elif 'data' in opportunity.opportunity_type.lower() or 'research' in opportunity.opportunity_type.lower():
        opportunity.collaboration_feasibility = 'high'
        opportunity.ai_contribution_potential = 60
        opportunity.partnership_mode = 'ai_assisted'

        opportunity.estimated_solo_hours = Decimal('8.0')
        opportunity.estimated_partnership_hours = Decimal('3.0')

    # Technical writing / documentation
    elif 'technical' in opportunity.opportunity_type.lower() or 'documentation' in opportunity.opportunity_type.lower():
        opportunity.collaboration_feasibility = 'high'
        opportunity.ai_contribution_potential = 65
        opportunity.partnership_mode = 'collaborative'

        opportunity.estimated_solo_hours = Decimal('10.0')
        opportunity.estimated_partnership_hours = Decimal('4.0')

    # Default: some AI assistance possible
    else:
        opportunity.collaboration_feasibility = 'medium'
        opportunity.ai_contribution_potential = 40
        opportunity.partnership_mode = 'ai_assisted'

    opportunity.save()
    return opportunity


@login_required
def partnership_health_check(request):
    """
    Health check endpoint for partnership system
    Returns system status and key metrics
    """
    from django.utils import timezone

    try:
        # Check database
        total_projects = PartnershipProject.objects.count()
        active_projects = PartnershipProject.objects.filter(
            status__in=['planning', 'in_progress', 'review']
        ).count()
        completed_projects = PartnershipProject.objects.filter(status='completed').count()

        # Check opportunities
        total_opps = Opportunity.objects.count()
        partnership_opps = Opportunity.objects.filter(
            collaboration_feasibility__in=['medium', 'high', 'ideal']
        ).count()

        return JsonResponse({
            'status': 'healthy',
            'projects': {
                'total': total_projects,
                'active': active_projects,
                'completed': completed_projects
            },
            'opportunities': {
                'total': total_opps,
                'partnership_ready': partnership_opps
            },
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)
