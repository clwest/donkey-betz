"""
Session 721: BRAIN SYSTEM - API Views

Endpoints for cognitive processing monitoring.
"""

import logging
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.services.brain import get_brain_service

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class BrainStatusView(View):
    """Get current brain status (cached)."""

    def get(self, request):
        """Return current brain status."""
        try:
            brain = get_brain_service()
            result = brain.think(force=False)
            return JsonResponse(result)
        except Exception as e:
            logger.error(f"Brain status error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BrainThinkView(View):
    """Run fresh brain check."""

    def get(self, request):
        """Run fresh brain check."""
        try:
            force = request.GET.get('force', 'false').lower() == 'true'
            brain = get_brain_service()
            result = brain.think(force=force)
            return JsonResponse(result)
        except Exception as e:
            logger.error(f"Brain think error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BrainVitalsView(View):
    """Get brain vitals (lightweight)."""

    def get(self, request):
        """Return brain vitals."""
        try:
            brain = get_brain_service()
            vitals = brain.get_vitals()
            return JsonResponse(vitals)
        except Exception as e:
            logger.error(f"Brain vitals error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BrainHistoryView(View):
    """Get brain pulse history."""

    def get(self, request):
        """Return brain pulse history."""
        try:
            hours = int(request.GET.get('hours', 24))
            limit = int(request.GET.get('limit', 100))

            brain = get_brain_service()
            history = brain.get_history(hours=hours, limit=limit)

            return JsonResponse({
                'success': True,
                'count': len(history),
                'history': history
            })
        except Exception as e:
            logger.error(f"Brain history error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BrainIsThinkingView(View):
    """Quick alive check - is brain thinking?"""

    def get(self, request):
        """Quick check if brain is active."""
        try:
            brain = get_brain_service()
            is_thinking = brain.is_thinking()
            return JsonResponse({
                'is_thinking': is_thinking,
                'status': 'thinking' if is_thinking else 'resting'
            })
        except Exception as e:
            return JsonResponse({
                'is_thinking': False,
                'status': 'offline',
                'error': str(e)
            }, status=500)
