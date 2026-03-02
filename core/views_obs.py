"""
OBS Bridge proxy endpoints.

Platform-side proxy that forwards requests to the local OBS Bridge service
via tunnel (ngrok/Cloudflare). Keeps bridge token server-side only.

Endpoints:
- GET  /api/cockpit/obs/health/   — bridge health (no OBS connection needed)
- GET  /api/cockpit/obs/status/   — recording status
- POST /api/cockpit/obs/start/    — start recording
- POST /api/cockpit/obs/stop/     — stop recording
- GET  /api/cockpit/obs/last/     — latest recording file info
- POST /api/cockpit/obs/upload/   — stop (optional) + upload latest recording
"""

import json
import logging
import os
import time
import urllib.error
import urllib.request

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


# ─── Configuration ─────────────────────────────────────────────────────────────

def _obs_enabled():
    return os.environ.get('OBS_ENABLED', '').lower() == 'true'


def _obs_config():
    return {
        'url': os.environ.get('OBS_BRIDGE_URL', '').rstrip('/'),
        'token': os.environ.get('OBS_BRIDGE_TOKEN', ''),
    }


# ─── Bridge HTTP client ───────────────────────────────────────────────────────

def _obs_bridge_request(method, path, body=None, timeout=15):
    """Make an authenticated request to the OBS bridge. Returns (status, data, latency_ms)."""
    cfg = _obs_config()
    url = f"{cfg['url']}{path}"

    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f"Bearer {cfg['token']}")
    req.add_header('Accept', 'application/json')
    req.add_header('ngrok-skip-browser-warning', '1')

    if body is not None:
        req.add_header('Content-Type', 'application/json')
        req.data = json.dumps(body).encode('utf-8')

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
            return resp.status, data, int((time.time() - start) * 1000)
    except urllib.error.HTTPError as e:
        try:
            data = json.loads(e.read())
        except Exception:
            data = {'error': str(e)}
        return e.code, data, int((time.time() - start) * 1000)
    except Exception as e:
        return 0, {'error': str(e)[:200]}, int((time.time() - start) * 1000)


def _guard(request):
    """Check auth + OBS enabled. Returns JsonResponse on failure, None on success."""
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'ok': False, 'error': {'code': 'UNAUTHORIZED', 'message': 'Authentication required'}}, status=401)
    if not _obs_enabled():
        return JsonResponse({'ok': False, 'error': {'code': 'OBS_DISABLED', 'message': 'OBS integration is not enabled'}}, status=503)
    cfg = _obs_config()
    if not cfg['url']:
        return JsonResponse({'ok': False, 'error': {'code': 'OBS_MISCONFIGURED', 'message': 'OBS_BRIDGE_URL not set'}}, status=503)
    return None


def _bridge_response(status_code, data, latency_ms):
    """Wrap bridge response for the client."""
    if status_code == 0:
        return JsonResponse({
            'ok': False,
            'bridgeReachable': False,
            'error': {'code': 'BRIDGE_UNREACHABLE', 'message': data.get('error', 'Bridge unreachable')},
            'latency_ms': latency_ms,
        }, status=502)

    if status_code == 401:
        return JsonResponse({
            'ok': False,
            'bridgeReachable': True,
            'error': {'code': 'BRIDGE_AUTH_FAILED', 'message': 'Bridge rejected token'},
            'latency_ms': latency_ms,
        }, status=502)

    return JsonResponse({
        'ok': data.get('ok', True),
        'bridgeReachable': True,
        'result': data,
        'latency_ms': latency_ms,
    }, status=200 if data.get('ok', True) else 502)


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@require_http_methods(["GET"])
def cockpit_obs_health(request):
    """GET /api/cockpit/obs/health/ — bridge health check (no OBS needed)."""
    err = _guard(request)
    if err:
        return err

    status_code, data, latency = _obs_bridge_request('GET', '/health', timeout=5)
    return _bridge_response(status_code, data, latency)


@require_http_methods(["GET"])
def cockpit_obs_status(request):
    """GET /api/cockpit/obs/status/ — OBS recording status."""
    err = _guard(request)
    if err:
        return err

    status_code, data, latency = _obs_bridge_request('GET', '/v1/recording/status')
    return _bridge_response(status_code, data, latency)


@csrf_exempt
@require_http_methods(["POST"])
def cockpit_obs_start(request):
    """POST /api/cockpit/obs/start/ — start OBS recording."""
    err = _guard(request)
    if err:
        return err

    status_code, data, latency = _obs_bridge_request('POST', '/v1/recording/start')
    return _bridge_response(status_code, data, latency)


@csrf_exempt
@require_http_methods(["POST"])
def cockpit_obs_stop(request):
    """POST /api/cockpit/obs/stop/ — stop OBS recording."""
    err = _guard(request)
    if err:
        return err

    status_code, data, latency = _obs_bridge_request('POST', '/v1/recording/stop')
    return _bridge_response(status_code, data, latency)


@require_http_methods(["GET"])
def cockpit_obs_last(request):
    """GET /api/cockpit/obs/last/ — latest recording file info."""
    err = _guard(request)
    if err:
        return err

    status_code, data, latency = _obs_bridge_request('GET', '/v1/recording/last')
    return _bridge_response(status_code, data, latency)


@csrf_exempt
@require_http_methods(["POST"])
def cockpit_obs_upload(request):
    """POST /api/cockpit/obs/upload/ — optionally stop recording + upload latest."""
    err = _guard(request)
    if err:
        return err

    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': {'code': 'INVALID_JSON', 'message': 'Invalid JSON body'}}, status=400)

    # Pass through only allowed fields
    bridge_body = {}
    if 'title' in body:
        bridge_body['title'] = body['title']
    if 'tags' in body:
        bridge_body['tags'] = body['tags']
    if body.get('stopIfRecording'):
        bridge_body['stopIfRecording'] = True

    status_code, data, latency = _obs_bridge_request(
        'POST', '/v1/recording/upload_last',
        body=bridge_body if bridge_body else None,
        timeout=60,
    )
    return _bridge_response(status_code, data, latency)
