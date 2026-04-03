"""
Advisor API Endpoints
Handles advisor consultations and interactions.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from core.auth_middleware import token_auth_required
from django.utils import timezone

from core.models_unified_system import Advisor
from core.llm_enforcer import LLMEnforcer

logger = logging.getLogger(__name__)


def _json_body(request) -> dict:
    """Safely parse JSON body; return {} on empty, 400 on bad JSON."""
    if not request.body:
        return {}
    try:
        # request.body is bytes; json.loads accepts bytes
        return json.loads(request.body)
    except json.JSONDecodeError:
        raise


@token_auth_required
@csrf_exempt  # allow API clients without CSRF cookie
@require_http_methods(["POST"])
def advisor_consult(request):
    """
    POST /api/v1/advisors/consult/
    Body:
      {
        "advisor_id": "uuid",
        "question": "Your question here",
        "context": "Optional context"
      }
    """
    try:
        data = _json_body(request)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON in request body"}, status=400)

    advisor_id = (data.get("advisor_id") or "").strip()
    question = (data.get("question") or "").strip()
    context = (data.get("context") or "").strip()

    # Validation
    if not advisor_id:
        return JsonResponse({"success": False, "error": "advisor_id is required"}, status=400)
    if not question:
        return JsonResponse({"success": False, "error": "question is required"}, status=400)

    # Load advisor
    try:
        advisor = Advisor.objects.get(id=advisor_id, is_active=True)
    except Advisor.DoesNotExist:
        return JsonResponse({"success": False, "error": "Advisor not found"}, status=404)

    logger.info("Consultation request for %s: %.50s...", advisor.name, question)

    # Prompts
    system_prompt = (
        f"You are {advisor.name}, {advisor.title}.\n\n"
        f"Your expertise: {advisor.expertise}\n"
        f"Your wisdom: {advisor.wisdom}\n\n"
        f"Provide guidance in the style and perspective of {advisor.name}.\n"
        "Be insightful, practical, and draw from your areas of expertise.\n"
    )

    user_prompt_lines = [f"Question: {question}"]
    if context:
        user_prompt_lines.append(f"Context: {context}")
    user_prompt_lines.append("Please provide your expert guidance on this matter.")
    user_prompt = "\n\n".join(user_prompt_lines)

    # LLM call (with fallback)
    try:
        # Session 876: Increased tokens for GPT-5-mini reasoning headroom
        enforcer = LLMEnforcer()
        guidance = enforcer.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model="gpt-5.2",
            max_completion_tokens=4000,
        )
    except Exception as llm_error:  # noqa: BLE001 (we want to log & fallback)
        logger.error("LLM error during consultation: %s", llm_error, exc_info=True)
        guidance = (
            f'Thank you for consulting with me regarding: "{question}"\n\n'
            f"Based on my expertise in {advisor.expertise}, I recommend:\n\n"
            "1. Analyze the situation from multiple perspectives.\n"
            "2. Consider both short-term actions and long-term implications.\n"
            "3. Seek additional data or expert input where uncertainty exists.\n"
            "4. Make decisions that align with your core values and objectives.\n\n"
            f"{advisor.wisdom}\n\n"
            "I'm here to help guide you through this decision-making process."
        )

    # Update advisor stats
    Advisor.objects.filter(pk=advisor.pk).update(
        total_consultations=(advisor.total_consultations or 0) + 1,
        last_consultation=timezone.now(),
    )
    advisor.refresh_from_db(fields=["total_consultations", "last_consultation"])

    # (Optional) Persist consultation record when model exists
    # consultation = AdvisorConsultation.objects.create(
    #     advisor=advisor,
    #     user=request.user,
    #     question=question,
    #     guidance=guidance,
    #     context=context,
    # )

    return JsonResponse(
        {
            "success": True,
            "advisor": {
                "id": str(advisor.id),
                "name": advisor.name,
                "title": advisor.title,
                "expertise": advisor.expertise,
                "avatar_url": advisor.avatar_url,
            },
            "guidance": guidance,
            "question": question,
            "timestamp": timezone.now().isoformat(),
            # "consultation_id": str(consultation.id),
        }
    )


@csrf_exempt
@require_http_methods(["GET"])
def advisor_list(request):
    """GET /api/v1/advisors/list/ — list active advisors (public endpoint)."""
    try:
        qs = (
            Advisor.objects.filter(is_active=True)
            .values(
                "id",
                "name",
                "title",
                "expertise",
                "category",
                "avatar_url",
                "wisdom",
                "total_consultations",
                "influence_score",
            )
            .order_by("name")
        )
        return JsonResponse({"success": True, "count": qs.count(), "advisors": list(qs)})
    except Exception as e:  # noqa: BLE001
        logger.error("Error in advisor_list: %s", e, exc_info=True)
        return JsonResponse({"success": False, "error": "Failed to retrieve advisors"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def advisor_detail(request, advisor_id):
    """GET /api/v1/advisors/<advisor_id>/ — get advisor details (public endpoint)."""
    try:
        advisor = Advisor.objects.get(id=advisor_id, is_active=True)
    except Advisor.DoesNotExist:
        return JsonResponse({"success": False, "error": "Advisor not found"}, status=404)
    except Exception as e:  # noqa: BLE001
        logger.error("Lookup error in advisor_detail: %s", e, exc_info=True)
        return JsonResponse({"success": False, "error": "Failed to retrieve advisor details"}, status=500)

    return JsonResponse(
        {
            "success": True,
            "advisor": {
                "id": str(advisor.id),
                "name": advisor.name,
                "title": advisor.title,
                "expertise": advisor.expertise,
                "category": advisor.category,
                "avatar_url": advisor.avatar_url,
                "wisdom": advisor.wisdom,
                "total_consultations": advisor.total_consultations,
                "total_insights_provided": advisor.total_insights_provided,
                "influence_score": advisor.influence_score,
                "last_consultation": advisor.last_consultation.isoformat() if advisor.last_consultation else None,
            },
        }
    )