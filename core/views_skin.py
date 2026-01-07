"""
Session 723: SKIN SYSTEM - API Views

Endpoints for project workspace health monitoring.
"""

import logging
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from core.services.skin import get_skin_service

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class SkinStatusView(View):
    """Get current skin status (cached)."""

    def get(self, request):
        """Return current skin status."""
        try:
            skin = get_skin_service()
            result = skin.get_status()
            return JsonResponse(result)
        except Exception as e:
            logger.error(f"Skin status error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SkinFeelView(View):
    """Run fresh skin health check."""

    def get(self, request):
        """Run fresh skin check."""
        try:
            force = request.GET.get('force', 'false').lower() == 'true'
            skin = get_skin_service()
            result = skin.feel(force=force)
            return JsonResponse(result)
        except Exception as e:
            logger.error(f"Skin feel error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SkinVitalsView(View):
    """Get skin vitals (lightweight)."""

    def get(self, request):
        """Return skin vitals."""
        try:
            skin = get_skin_service()
            vitals = skin.get_vitals()
            return JsonResponse(vitals)
        except Exception as e:
            logger.error(f"Skin vitals error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SkinHistoryView(View):
    """Get skin pulse history."""

    def get(self, request):
        """Return skin pulse history."""
        try:
            hours = int(request.GET.get('hours', 24))
            limit = int(request.GET.get('limit', 100))
            skin = get_skin_service()
            history = skin.get_history(hours=hours, limit=limit)
            return JsonResponse({
                'timestamp': timezone.now().isoformat(),
                'hours': hours,
                'count': len(history),
                'pulses': history,
            })
        except Exception as e:
            logger.error(f"Skin history error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SkinIsHealthyView(View):
    """Quick health check."""

    def get(self, request):
        """Return quick health status."""
        try:
            skin = get_skin_service()
            is_healthy = skin.is_healthy()
            return JsonResponse({
                'healthy': is_healthy,
                'timestamp': timezone.now().isoformat(),
            })
        except Exception as e:
            logger.error(f"Skin is_healthy error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SkinWorkspacesView(View):
    """Get workspace summaries."""

    def get(self, request):
        """Return workspace summaries."""
        try:
            skin = get_skin_service()
            workspaces = skin.get_workspaces_summary()
            return JsonResponse({
                'timestamp': timezone.now().isoformat(),
                'count': len(workspaces),
                'workspaces': workspaces,
            })
        except Exception as e:
            logger.error(f"Skin workspaces error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
