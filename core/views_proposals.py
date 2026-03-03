"""
Views for AI Proposal Management
================================
Handles approval, rejection, and execution of AI-generated proposals.
"""

import json
import logging
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from ai_core.intelligence.proposal_manager import ProposalManager

logger = logging.getLogger(__name__)

# Initialize proposal manager
proposal_manager = ProposalManager()


@csrf_exempt
@require_http_methods(["POST"])
def approve_proposal(request):
    """Approve an AI proposal for execution"""
    try:
        data = json.loads(request.body or b"{}")
        proposal_id = data.get('proposal_id')

        if not proposal_id:
            return JsonResponse({
                'success': False,
                'error': 'No proposal_id provided'
            }, status=400)

        # Approve the proposal
        success = proposal_manager.approve_proposal(proposal_id, approver="user")

        if success:
            # Trigger consciousness system to generate new proposals
            try:
                import redis
                redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)
                # Clear the consciousness cache to force regeneration of proposals
                redis_client.delete('consciousness:ai_proposals')
                redis_client.delete('consciousness:current_level')
                logger.info(f"Triggered consciousness refresh after proposal {proposal_id} approval")

                # Trigger immediate WebSocket update to all connected clients
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync

                channel_layer = get_channel_layer()
                if channel_layer:
                    # Send update to consciousness stream
                    async_to_sync(channel_layer.group_send)(
                        'consciousness_stream',
                        {
                            'type': 'consciousness_update',
                            'message': {
                                'type': 'proposal_approved',
                                'approved_proposal_id': proposal_id,
                                'force_refresh': True
                            }
                        }
                    )
                    logger.info(f"Sent WebSocket update for proposal {proposal_id} approval")

            except Exception as e:
                logger.warning(f"Could not trigger consciousness refresh: {e}")

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
        data = json.loads(request.body or b"{}")
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

        # Reload from Redis to get fresh data
        proposal_manager.reload_from_redis()
        logger.info(f"🔵 GET_PROPOSALS: Reloaded from Redis, have {len(proposal_manager.proposals)} proposals")

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
            proposal_data = {
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
                'implementation_steps': proposal.implementation_steps,
                # Add execution data for completed/failed proposals
                'completion_percentage': proposal.completion_percentage,
                'execution_log': proposal.execution_log,
                'error_messages': proposal.error_messages
            }

            # Add approval data if available
            if proposal.approved_by:
                proposal_data['approved_by'] = proposal.approved_by
                proposal_data['approved_at'] = proposal.approved_at.isoformat() if proposal.approved_at else None

            # Add rejection data if available
            if proposal.rejection_reason:
                proposal_data['rejection_reason'] = proposal.rejection_reason

            proposals_data.append(proposal_data)

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
        data = json.loads(request.body or b"{}")
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


@csrf_exempt
@require_http_methods(["POST"])
def save_consciousness_proposals(request):
    """Save consciousness proposals to ProposalManager for persistence"""
    try:
        data = json.loads(request.body or b"{}")
        proposals = data.get('proposals', [])

        if not proposals:
            return JsonResponse({
                'success': False,
                'error': 'No proposals provided'
            }, status=400)

        # Reload from Redis to get current state
        proposal_manager.reload_from_redis()

        count = 0
        for proposal_data in proposals:
            # Convert consciousness proposal format to AIProposal format
            from ai_core.intelligence.proposal_manager import AIProposal, ProposalStatus, ProposalRisk
            from datetime import datetime
            import hashlib

            # Generate or use existing proposal ID
            proposal_id = proposal_data.get('id') or hashlib.md5(
                f"{proposal_data.get('title', '')}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:8]

            # Skip if proposal already exists in Redis (don't overwrite)
            if proposal_id in proposal_manager.proposals:
                logger.info(f"Proposal {proposal_id} already exists, skipping to preserve status")
                continue

            # Map complexity to estimated time
            complexity = proposal_data.get('complexity', 5)
            time_estimates = {
                3: "15 minutes",
                4: "30 minutes",
                5: "1 hour",
                6: "2 hours"
            }
            estimated_time = time_estimates.get(complexity, "1 hour")

            # Create AIProposal instance
            proposal = AIProposal(
                id=proposal_id,
                title=proposal_data.get('title', 'Consciousness Proposal'),
                description=proposal_data.get('description', ''),
                category=proposal_data.get('category', 'optimization'),
                risk_level=ProposalRisk.MEDIUM,  # Default to medium
                status=ProposalStatus.PENDING,
                created_at=timezone.now(),
                impact_score=proposal_data.get('impact', 5.0),
                roi_estimate=proposal_data.get('roi', 3.0),
                affected_components=proposal_data.get('affected_components', []),
                dependencies=proposal_data.get('dependencies', []),
                implementation_steps=proposal_data.get('implementation_steps', [
                    'Analyze current state',
                    'Implement improvements',
                    'Test changes',
                    'Monitor results'
                ]),
                estimated_time=estimated_time,
                rollback_plan='Revert to previous configuration if issues arise',
                evidence={
                    'source': 'consciousness',
                    'complexity': complexity
                },
                confidence_score=proposal_data.get('confidence', 0.85),
                ai_reasoning='Generated by consciousness analysis system'
            )

            # Add to proposal manager and persist to Redis
            proposal_manager.proposals[proposal_id] = proposal
            proposal_manager._save_proposal(proposal)  # Persist to Redis
            count += 1
            logger.info(f"Saved consciousness proposal: {proposal_id} - {proposal.title}")

        return JsonResponse({
            'success': True,
            'count': count,
            'message': f'Saved {count} consciousness proposals'
        })

    except Exception as e:
        logger.error(f"Error saving consciousness proposals: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)