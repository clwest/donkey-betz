"""
Session 724: NERVOUS SYSTEM API Views

WebSocket communication monitoring endpoints.
"""

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone

logger = logging.getLogger(__name__)


class NervousStatusView(APIView):
    """
    GET /api/nervous/status/
    Returns cached nervous system status (fast).
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        from core.services.nervous import get_nervous_service

        try:
            nervous = get_nervous_service()
            result = nervous.get_status()
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"[NERVOUS] Status view error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NervousFeelView(APIView):
    """
    GET /api/nervous/feel/
    Run full nervous system health check.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        from core.services.nervous import get_nervous_service

        try:
            force = request.query_params.get('force', 'false').lower() == 'true'
            nervous = get_nervous_service()
            result = nervous.feel(force=force)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"[NERVOUS] Feel view error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NervousVitalsView(APIView):
    """
    GET /api/nervous/vitals/
    Get current nervous vitals for body coordinator.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        from core.services.nervous import get_nervous_service

        try:
            nervous = get_nervous_service()
            result = nervous.get_vitals()
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"[NERVOUS] Vitals view error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NervousHistoryView(APIView):
    """
    GET /api/nervous/history/
    Get nervous pulse history.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        from core.services.nervous import get_nervous_service

        try:
            hours = int(request.query_params.get('hours', 24))
            limit = int(request.query_params.get('limit', 100))

            nervous = get_nervous_service()
            result = nervous.get_history(hours=hours, limit=limit)
            return Response({
                'history': result,
                'count': len(result),
                'hours': hours,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"[NERVOUS] History view error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NervousIsResponsiveView(APIView):
    """
    GET /api/nervous/is-responsive/
    Quick health check.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        from core.services.nervous import get_nervous_service

        try:
            nervous = get_nervous_service()
            is_responsive = nervous.is_responsive()
            return Response({
                'is_responsive': is_responsive,
                'timestamp': timezone.now().isoformat(),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"[NERVOUS] IsResponsive view error: {e}")
            return Response(
                {'is_responsive': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NervousConsumersView(APIView):
    """
    GET /api/nervous/consumers/
    Get WebSocket consumers summary.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        from core.services.nervous import get_nervous_service

        try:
            nervous = get_nervous_service()
            result = nervous.get_consumers_summary()
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"[NERVOUS] Consumers view error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
