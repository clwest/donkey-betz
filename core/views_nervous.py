"""
Session 724: NERVOUS SYSTEM API Views

WebSocket communication monitoring endpoints.

I-0301 Phase 3 Stage 3 PR A — Bucket D response-shape audit outcome
(Rigby S2742 Stage 3 SIGN Q2 concur):

  * 5 endpoints reclassified from Bucket D → Bucket B (require
    IsAuthenticated). They return operational telemetry (message counts,
    connection counts, latency, activity level, error rate) or internal
    IDs (History returns pulse UUIDs) that should not be exposed to
    anonymous callers even without tenant identifiers being present.
  * 1 endpoint (NervousIsResponsiveView) reclassified from Bucket D →
    Bucket A (genuinely public health check). Kept AllowAny with
    Rigby S2742 Stage 3 SIGN Q3 guardrails documented at the class
    docstring.
"""

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone

logger = logging.getLogger(__name__)


class NervousStatusView(APIView):
    """
    GET /api/nervous/status/
    Returns cached nervous system status (fast).

    I-0301 Phase 3 Stage 3 PR A — Bucket D → Bucket B. Prior AllowAny +
    authentication_classes=[] combination let anonymous callers read
    operational telemetry (connection counts, message throughput,
    latency, error rate). No tenant identifiers, but still an
    operational-capacity leak class.
    """
    permission_classes = [IsAuthenticated]

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

    I-0301 Phase 3 Stage 3 PR A — Bucket D → Bucket B. Same telemetry
    class as NervousStatusView + heavier compute path.
    """
    permission_classes = [IsAuthenticated]

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

    I-0301 Phase 3 Stage 3 PR A — Bucket D → Bucket B. Subset of the
    get_status shape; same telemetry leak class.
    """
    permission_classes = [IsAuthenticated]

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

    I-0301 Phase 3 Stage 3 PR A — Bucket D → Bucket B. Response includes
    per-pulse UUIDs; safety contract §9.2 prohibits UUIDs anywhere in
    public user-facing responses. Auth-gated.

    Rigby S2742 Stage 3 SIGN Q2 amendment (deferred, not blocking):
    consider stripping the ``id`` field from the response even for
    authenticated users as a UUID-exposure anti-pattern hardening.
    Tracked as follow-on.
    """
    permission_classes = [IsAuthenticated]

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
    Quick health check — genuinely public health-check endpoint.

    I-0301 Phase 3 Stage 3 PR A — Bucket D → Bucket A (Rigby S2742 Stage 3
    SIGN Q3). Response is constant-shape ``{is_responsive: bool,
    timestamp: ISO}`` — no version, no queue depth, no dependency health,
    no user/session variance. Rigby SIGN guardrails enforced at test-time
    in tests/security/test_nervous_public_health_check.py.

    Response contract for this Bucket A endpoint (frozen by regression):
      * NO UUIDs anywhere
      * NO provider names / model names
      * NO internal path / substrate references
      * NO variance by session cookie / auth header
      * Only two fields: ``is_responsive`` (bool) + ``timestamp`` (ISO)

    Adding fields to this response requires re-audit against §3.2 of the
    Failure-Data Safety Contract and re-classification.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        from core.services.nervous import get_nervous_service

        try:
            nervous = get_nervous_service()
            is_responsive = nervous.is_responsive()
            # Response shape is FROZEN by Bucket A regression suite; do
            # not add fields without re-audit.
            return Response({
                'is_responsive': is_responsive,
                'timestamp': timezone.now().isoformat(),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"[NERVOUS] IsResponsive view error: {e}")
            # 5xx path also stays constant-shape — no exception detail
            # leaks to the anonymous caller. The full exception context
            # is available in the operator envelope written by
            # RURErrorEnvelopeMiddleware (safety contract §6.1).
            return Response(
                {'is_responsive': False, 'timestamp': timezone.now().isoformat()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class NervousConsumersView(APIView):
    """
    GET /api/nervous/consumers/
    Get WebSocket consumers summary.

    I-0301 Phase 3 Stage 3 PR A — Bucket D → Bucket B. Rigby S2742
    scoping SIGN §4 flagged that consumer summaries may leak workspace
    scope of active connections; conservative auth-gate.
    """
    permission_classes = [IsAuthenticated]

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
