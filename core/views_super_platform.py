"""
Super Platform API Views

Provides REST API endpoints for the Super Platform Coordinator.
This is the unified entry point for all AI interactions.

Session 264: Phase 1 Foundation
"""

import json
import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from core.super_platform import SuperPlatformCoordinator, QueryClassifier

# Session 483: Smart Suggestions for follow-up actions
try:
    from core.services.smart_suggestions import get_smart_suggestions_service
    SMART_SUGGESTIONS_AVAILABLE = True
except ImportError:
    SMART_SUGGESTIONS_AVAILABLE = False
    get_smart_suggestions_service = lambda session_id='default': None

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class SuperPlatformProcessView(View):
    """
    Main processing endpoint for the Super Platform.

    POST /api/super-platform/process/
    {
        "message": "user input here"
    }

    Returns the full coordinator result including:
    - response
    - classification
    - context used
    - agents used
    - artifacts
    """

    def post(self, request):
        try:
            # Parse request body
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON in request body'
                }, status=400)

            message = data.get('message', '').strip()
            if not message:
                return JsonResponse({
                    'success': False,
                    'error': 'Message is required'
                }, status=400)

            # Get user if authenticated
            user = request.user if request.user.is_authenticated else None

            # Process through the coordinator
            coordinator = SuperPlatformCoordinator(user=user)
            result = coordinator.process(message)

            # Convert to dict for response
            response_dict = result.to_dict()

            # Session 483: Add smart suggestions for follow-up actions
            if SMART_SUGGESTIONS_AVAILABLE and user and user.is_authenticated:
                try:
                    smart_suggestions = get_smart_suggestions_service(str(user.id))
                    response_text = response_dict.get('response', '')

                    # Detect action type from response
                    action_type = smart_suggestions.detect_action_from_response(response_text, [])

                    logger.info(f"🔍 Session 483: SuperPlatform detected action_type='{action_type}'")

                    if action_type:
                        # Record the action
                        smart_suggestions.record_action(action_type, output=response_text)

                        # Get suggestions
                        suggestions = smart_suggestions.get_suggestions(limit=3)

                        if suggestions:
                            # Get quick action buttons
                            quick_actions = smart_suggestions.get_quick_actions()
                            response_dict['quick_actions'] = quick_actions
                            response_dict['smart_suggestions'] = [s.text for s in suggestions]

                            logger.info(f"✨ Session 483: Added {len(quick_actions)} quick_actions to SuperPlatform response")
                except Exception as e:
                    logger.warning(f"⚠️ Session 483: SmartSuggestions error in SuperPlatform: {e}")

            # Session 494: Always ensure quick_actions is at least an empty array
            if 'quick_actions' not in response_dict:
                response_dict['quick_actions'] = []
            if 'smart_suggestions' not in response_dict:
                response_dict['smart_suggestions'] = []

            return JsonResponse(response_dict)

        except Exception as e:
            logger.error(f"Super Platform process error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SuperPlatformClassifyView(View):
    """
    Classification-only endpoint for debugging or preview.

    POST /api/super-platform/classify/
    {
        "message": "user input here"
    }

    Returns just the classification without executing.
    """

    def post(self, request):
        try:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON in request body'
                }, status=400)

            message = data.get('message', '').strip()
            if not message:
                return JsonResponse({
                    'success': False,
                    'error': 'Message is required'
                }, status=400)

            classifier = QueryClassifier()
            classification = classifier.classify(message)
            routing = classifier.get_routing_decision(classification)

            return JsonResponse({
                'success': True,
                'classification': classification.to_dict(),
                'routing': routing,
            })

        except Exception as e:
            logger.error(f"Classification error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SuperPlatformStatusView(View):
    """
    Status endpoint for the Super Platform.

    GET /api/super-platform/status/

    Returns current system status.
    """

    def get(self, request):
        try:
            user = request.user if request.user.is_authenticated else None
            coordinator = SuperPlatformCoordinator(user=user)

            status = coordinator.get_status()
            status['success'] = True

            # Add more system info
            status['version'] = 'v264-phase1'
            status['components'] = {
                'query_classifier': 'active',
                'prompt_builder': 'active',
                'context_aggregator': 'active',
                'coordinator': 'active',
            }

            return JsonResponse(status)

        except Exception as e:
            logger.error(f"Status error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SuperPlatformQuickAskView(View):
    """
    Quick ask endpoint for simple questions.

    POST /api/super-platform/ask/
    {
        "question": "What's trending in AI?"
    }

    Returns just the response text.
    """

    def post(self, request):
        try:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON in request body'
                }, status=400)

            question = data.get('question', '').strip()
            if not question:
                return JsonResponse({
                    'success': False,
                    'error': 'Question is required'
                }, status=400)

            user = request.user if request.user.is_authenticated else None
            coordinator = SuperPlatformCoordinator(user=user)

            response = coordinator.ask(question)

            return JsonResponse({
                'success': True,
                'response': response,
            })

        except Exception as e:
            logger.error(f"Quick ask error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


# URL patterns for this module
def get_urlpatterns():
    """Return URL patterns for the Super Platform API."""
    from django.urls import path

    return [
        path('api/super-platform/process/', SuperPlatformProcessView.as_view(), name='super_platform_process'),
        path('api/super-platform/classify/', SuperPlatformClassifyView.as_view(), name='super_platform_classify'),
        path('api/super-platform/status/', SuperPlatformStatusView.as_view(), name='super_platform_status'),
        path('api/super-platform/ask/', SuperPlatformQuickAskView.as_view(), name='super_platform_ask'),
    ]
