"""
POST /api/deploy/verify/ — lightweight deploy verification.

Runs a fixed set of HTTP checks against the platform's own endpoints to confirm
a deploy landed correctly.  Admin-only.
"""

import logging
import time

import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

logger = logging.getLogger(__name__)

# Hardcoded verification contracts — no user-supplied URLs for security
VERIFICATION_CHECKS = [
    ('health', 'GET', '/api/v1/health/', 200),
    ('manifest', 'GET', '/api/app/manifest/', 200),
    ('boardroom_stats', 'GET', '/api/boardroom/stats/', 200),
    ('governance_stats', 'GET', '/api/governance/stats/', 200),
    ('gallery_list', 'GET', '/api/v1/gallery/list/', 200),
    ('video_gallery', 'GET', '/api/v1/video/gallery/', 200),
    ('pa_context', 'GET', '/api/assistant/context/', 200),
    ('platform_mission', 'GET', '/api/platform/mission/', 200),
]


def run_verification(base_url: str, token: str | None = None) -> dict:
    """Execute all verification checks and return a summary.

    Used by both the REST endpoint and the management command.

    Args:
        base_url: e.g. ``https://donkey-betz-platform-production.up.railway.app``
        token: optional DRF token for authenticated endpoints
    """
    results = []
    headers = {}
    if token:
        headers['Authorization'] = f'Token {token}'

    for name, method, path, expected_status in VERIFICATION_CHECKS:
        url = base_url.rstrip('/') + path
        t0 = time.time()
        try:
            resp = requests.request(method, url, headers=headers, timeout=10)
            ok = resp.status_code == expected_status
            detail = f'{resp.status_code}'
            if not ok:
                detail += f' (expected {expected_status})'
        except requests.RequestException as exc:
            ok = False
            detail = str(exc)[:200]

        elapsed_ms = int((time.time() - t0) * 1000)
        results.append({
            'name': name,
            'ok': ok,
            'status_code': resp.status_code if 'resp' in dir() and hasattr(resp, 'status_code') else None,
            'detail': detail,
            'latency_ms': elapsed_ms,
        })

    passed = sum(1 for r in results if r['ok'])
    return {
        'all_ok': passed == len(results),
        'passed': passed,
        'total': len(results),
        'results': results,
    }


@api_view(['POST'])
@permission_classes([IsAdminUser])
def deploy_verify(request):
    base_url = request.build_absolute_uri('/').rstrip('/')
    # Use the requesting user's token for authenticated endpoints
    token = request.auth.key if hasattr(request.auth, 'key') else None
    data = run_verification(base_url, token=token)
    return Response(data)
