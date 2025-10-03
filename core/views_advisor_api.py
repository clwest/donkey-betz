"""
Advisor API Endpoints
Handles advisor consultations and interactions
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from core.models_unified_system import Advisor
from core.llm_enforcer import LLMEnforcer

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def advisor_consult(request):
    """
    Consult with an advisor

    POST /api/v1/advisors/consult/
    Body: {
        "advisor_id": "uuid",
        "question": "Your question here",
        "context": "Optional context"
    }

    Returns: {
        "success": true,
        "advisor": {...},
        "guidance": "Advisor's response",
        "consultation_id": "uuid"
    }
    """
    import json

    try:
        # Parse request data
        data = json.loads(request.body) if request.body else {}
        advisor_id = data.get('advisor_id')
        question = data.get('question', '').strip()
        context = data.get('context', '')

        # Validation
        if not advisor_id:
            return JsonResponse({
                'success': False,
                'error': 'advisor_id is required'
            }, status=400)

        if not question:
            return JsonResponse({
                'success': False,
                'error': 'question is required'
            }, status=400)

        # Get advisor from database
        try:
            advisor = Advisor.objects.get(id=advisor_id, is_active=True)
        except Advisor.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Advisor not found'
            }, status=404)

        logger.info(f"Consultation request for {advisor.name}: {question[:50]}...")

        # Create consultation prompt based on advisor's expertise
        system_prompt = f"""You are {advisor.name}, {advisor.title}.

Your expertise: {advisor.expertise}
Your wisdom: {advisor.wisdom}

Provide guidance in the style and perspective of {advisor.name}.
Be insightful, practical, and draw from your areas of expertise.
"""

        user_prompt = f"""Question: {question}

{f'Context: {context}' if context else ''}

Please provide your expert guidance on this matter."""

        # Get AI response using LLMEnforcer
        try:
            enforcer = LLMEnforcer()
            guidance = enforcer.generate_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model='gpt-4o-mini',  # Use GPT-4o-mini for advisor consultations
                temperature=0.7,
                max_tokens=1000
            )
        except Exception as llm_error:
            logger.error(f"LLM error during consultation: {llm_error}")
            # Fallback response if LLM fails
            guidance = f"""Thank you for consulting with me regarding: "{question}"

Based on my expertise in {advisor.expertise}, I recommend:

1. Take time to thoroughly analyze the situation from multiple perspectives
2. Consider both short-term actions and long-term implications
3. Seek additional data or expert input where uncertainty exists
4. Make decisions that align with your core values and objectives

{advisor.wisdom}

I'm here to help guide you through this decision-making process."""

        # Update advisor stats
        advisor.total_consultations += 1
        advisor.last_consultation = timezone.now()
        advisor.save(update_fields=['total_consultations', 'last_consultation'])

        # TODO: Create consultation record in database for history
        # consultation = AdvisorConsultation.objects.create(
        #     advisor=advisor,
        #     user=request.user,
        #     question=question,
        #     guidance=guidance,
        #     context=context
        # )

        return JsonResponse({
            'success': True,
            'advisor': {
                'id': str(advisor.id),
                'name': advisor.name,
                'title': advisor.title,
                'expertise': advisor.expertise,
                'avatar_url': advisor.avatar_url,
            },
            'guidance': guidance,
            'question': question,
            'timestamp': timezone.now().isoformat(),
            # 'consultation_id': str(consultation.id)  # When model exists
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in advisor_consult: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error during consultation'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def advisor_list(request):
    """
    List all active advisors

    GET /api/v1/advisors/list/

    Returns: {
        "success": true,
        "advisors": [...]
    }
    """
    try:
        advisors = Advisor.objects.filter(is_active=True).values(
            'id', 'name', 'title', 'expertise', 'category',
            'avatar_url', 'wisdom', 'total_consultations', 'influence_score'
        ).order_by('name')

        return JsonResponse({
            'success': True,
            'count': advisors.count(),
            'advisors': list(advisors)
        })
    except Exception as e:
        logger.error(f"Error in advisor_list: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve advisors'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def advisor_detail(request, advisor_id):
    """
    Get detailed information about a specific advisor

    GET /api/v1/advisors/<advisor_id>/

    Returns: {
        "success": true,
        "advisor": {...}
    }
    """
    try:
        advisor = Advisor.objects.get(id=advisor_id, is_active=True)

        return JsonResponse({
            'success': True,
            'advisor': {
                'id': str(advisor.id),
                'name': advisor.name,
                'title': advisor.title,
                'expertise': advisor.expertise,
                'category': advisor.category,
                'avatar_url': advisor.avatar_url,
                'wisdom': advisor.wisdom,
                'total_consultations': advisor.total_consultations,
                'total_insights_provided': advisor.total_insights_provided,
                'influence_score': advisor.influence_score,
                'last_consultation': advisor.last_consultation.isoformat() if advisor.last_consultation else None,
            }
        })
    except Advisor.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Advisor not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error in advisor_detail: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve advisor details'
        }, status=500)
