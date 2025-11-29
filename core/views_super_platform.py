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
from django.contrib.auth.mixins import LoginRequiredMixin

from core.super_platform import SuperPlatformCoordinator, QueryClassifier

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

            return JsonResponse(result.to_dict())

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
