"""
Views for AI Proposal Management
================================
Handles approval, rejection, and execution of AI-generated proposals.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from backend.intelligence.proposal_manager import ProposalManager, ProposalStatus
import json
import logging

logger = logging.getLogger(__name__)

# Initialize proposal manager
proposal_manager = ProposalManager()


@csrf_exempt
@require_http_methods(["POST"])
def approve_proposal(request):
    """Approve an AI proposal for execution"""
    try:
        data = json.loads(request.body)
        proposal_id = data.get('proposal_id')

        if not proposal_id:
            return JsonResponse({
                'success': False,
                'error': 'No proposal_id provided'
            }, status=400)

        # Approve the proposal
        success = proposal_manager.approve_proposal(proposal_id, approver="user")

        if success:
            # Optionally execute immediately for low-risk proposals
            proposal = proposal_manager.proposals.get(proposal_id)
            if proposal and proposal.risk_level.value == "low":
                result = proposal_manager.execute_proposal(proposal_id)
                return JsonResponse({
                    'success': True,
                    'message': 'Proposal approved and executed',
                    'execution_result': result
                })

            return JsonResponse({
                'success': True,
                'message': 'Proposal approved and queued for execution'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Proposal not found or already processed'
            }, status=404)

    except Exception as e:
        logger.error(f"Error approving proposal: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reject_proposal(request):
    """Reject an AI proposal"""
    try:
        data = json.loads(request.body)
        proposal_id = data.get('proposal_id')
        reason = data.get('reason', 'User rejected')

        if not proposal_id:
            return JsonResponse({
                'success': False,
                'error': 'No proposal_id provided'
            }, status=400)

        # Reject the proposal
        success = proposal_manager.reject_proposal(proposal_id, reason)

        if success:
            return JsonResponse({
                'success': True,
                'message': 'Proposal rejected'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Proposal not found or already processed'
            }, status=404)

    except Exception as e:
        logger.error(f"Error rejecting proposal: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_proposals(request):
    """Get all pending proposals"""
    try:
        status_filter = request.GET.get('status', 'pending')

        if status_filter == 'pending':
            proposals = proposal_manager.get_pending_proposals()
        elif status_filter == 'all':
            proposals = list(proposal_manager.proposals.values())
        else:
            # Filter by specific status
            proposals = [
                p for p in proposal_manager.proposals.values()
                if p.status.value == status_filter
            ]

        # Convert proposals to dict format
        proposals_data = []
        for proposal in proposals:
            proposals_data.append({
                'id': proposal.id,
                'title': proposal.title,
                'description': proposal.description,
                'category': proposal.category,
                'risk_level': proposal.risk_level.value,
                'status': proposal.status.value,
                'created_at': proposal.created_at.isoformat(),
                'impact_score': proposal.impact_score,
                'roi_estimate': proposal.roi_estimate,
                'confidence_score': proposal.confidence_score,
                'requires_approval': proposal.requires_human_approval,
                'affected_components': proposal.affected_components,
                'implementation_steps': proposal.implementation_steps
            })

        return JsonResponse({
            'success': True,
            'proposals': proposals_data,
            'stats': proposal_manager.get_proposal_stats()
        })

    except Exception as e:
        logger.error(f"Error getting proposals: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def execute_proposal(request):
    """Manually execute an approved proposal"""
    try:
        data = json.loads(request.body)
        proposal_id = data.get('proposal_id')

        if not proposal_id:
            return JsonResponse({
                'success': False,
                'error': 'No proposal_id provided'
            }, status=400)

        # Execute the proposal
        result = proposal_manager.execute_proposal(proposal_id)

        return JsonResponse({
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'result': result
        })

    except Exception as e:
        logger.error(f"Error executing proposal: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_proposal_stats(request):
    """Get statistics about proposals"""
    try:
        stats = proposal_manager.get_proposal_stats()
        return JsonResponse({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"Error getting proposal stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)