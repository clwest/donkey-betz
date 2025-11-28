"""
Session 240: New Workflow Engine API

Philosophy: User's vision is sacred, system enhances it.

Endpoints:
- POST /api/v2/workflow/execute/  - Execute workflow with new engine
- POST /api/v2/workflow/parse/    - Parse user intent (for UI feedback)
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from agents.workflow_engine import WorkflowEngine, IntentParser, CONTENT_CONFIGS

logger = logging.getLogger(__name__)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def execute_workflow_v2(request):
    """
    Execute the new workflow engine.

    POST body:
    {
        "message": "Create a cartoon style logo for my tech startup",
        "project_id": "optional-uuid"
    }

    Returns:
    {
        "success": true,
        "content_type": "logo",
        "style_preserved": "cartoon",
        "subject_preserved": null,
        "images": [...],
        "enhancements_applied": {...},
        "message": "Created 3 cartoon style logos enhanced with trending colors"
    }
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        project_id = data.get('project_id')

        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Message is required'
            }, status=400)

        logger.info(f"🚀 Session 240 Workflow Engine: {message[:100]}...")

        # Execute the new workflow engine
        engine = WorkflowEngine(user=request.user, project_id=project_id)
        result = engine.execute(message)

        # Build user-friendly response message
        response_message = _build_response_message(result)
        result['message'] = response_message

        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.exception(f"Workflow engine error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def parse_intent(request):
    """
    Parse user intent for UI feedback before execution.

    Useful for showing the user what will be created before they confirm.

    POST body:
    {
        "message": "Research trending tech and create three images for social media"
    }

    Returns:
    {
        "success": true,
        "intent": {
            "content_type": "social_image",
            "content_type_label": "Social Media Images",
            "style": null,
            "subject": null,
            "purpose": "tech",
            "count": 3,
            "wants_research": true,
            "dimensions": "1080x1080"
        },
        "preview_message": "I'll research trending tech and create 3 social media images for you."
    }
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '')

        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Message is required'
            }, status=400)

        # Parse intent
        intent = IntentParser.parse(message)
        config = CONTENT_CONFIGS[intent.content_type]

        # Build human-readable labels
        content_labels = {
            'logo': 'Logo',
            'social_image': 'Social Media Image',
            'youtube_thumbnail': 'YouTube Thumbnail',
            'banner': 'Banner',
            'product_photo': 'Product Photo',
            'illustration': 'Illustration',
            'brand_identity': 'Brand Identity Asset',
        }

        # Build preview message
        style_text = f"{intent.style} style " if intent.style else ""
        subject_text = f"{intent.subject} " if intent.subject else ""
        research_text = "research and " if intent.wants_research else ""
        content_label = content_labels.get(intent.content_type.value, 'images')

        preview = f"I'll {research_text}create {intent.count} {style_text}{subject_text}{content_label.lower()}s for you."

        # Add enhancement note if research is involved
        if intent.wants_research:
            preview += " I'll enhance your design with trending colors and styles."

        return JsonResponse({
            'success': True,
            'intent': {
                'content_type': intent.content_type.value,
                'content_type_label': content_label,
                'style': intent.style,
                'subject': intent.subject,
                'purpose': intent.purpose,
                'count': intent.count,
                'wants_research': intent.wants_research,
                'dimensions': f"{config.width}x{config.height}",
                'allows_text': config.allows_text,
            },
            'preview_message': preview
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.exception(f"Intent parsing error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _build_response_message(result: dict) -> str:
    """Build a user-friendly response message."""
    content_type = result.get('content_type', 'images')
    style = result.get('style_preserved')
    subject = result.get('subject_preserved')
    images = result.get('images', [])
    enhancements = result.get('enhancements_applied', {})

    # Count successful images
    count = len([img for img in images if img.get('success')])

    # Build message parts
    parts = []

    if style:
        parts.append(f"{style} style")
    if subject:
        parts.append(f"{subject}")

    content_labels = {
        'logo': 'logo',
        'social_image': 'social media image',
        'youtube_thumbnail': 'YouTube thumbnail',
        'banner': 'banner',
        'product_photo': 'product photo',
        'illustration': 'illustration',
        'brand_identity': 'brand asset',
    }
    label = content_labels.get(content_type, 'image')
    plural = 's' if count != 1 else ''

    style_subject = ' '.join(parts) + ' ' if parts else ''
    base_msg = f"Created {count} {style_subject}{label}{plural}"

    # Add enhancement info
    exec_input = enhancements.get('executive_input', {})
    colors = exec_input.get('recommended_colors', [])
    if colors:
        base_msg += f" enhanced with trending colors ({', '.join(colors[:2])})"

    return base_msg + "."
