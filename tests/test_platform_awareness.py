"""
Acceptance tests for the Platform Awareness feature set.

Run against a live server:
    TEST_BASE_URL=https://... PA_SERVICE_TOKEN=... pytest tests/test_platform_awareness.py -v

Or locally:
    TEST_BASE_URL=http://localhost:8000 PA_SERVICE_TOKEN=<token> pytest tests/test_platform_awareness.py -v
"""

import os
import pytest
import requests

BASE_URL = os.environ.get('TEST_BASE_URL', 'http://localhost:8000').rstrip('/')
PA_TOKEN = os.environ.get('PA_SERVICE_TOKEN', '')
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', '')


def _headers(token=None):
    t = token or PA_TOKEN
    if t:
        return {'Authorization': f'Token {t}'}
    return {}


# ── Health (no auth) ─────────────────────────────────────────────────────────

class TestHealth:
    def test_health_no_auth(self):
        resp = requests.get(f'{BASE_URL}/api/v1/health/', timeout=10)
        assert resp.status_code == 200


# ── Manifest ─────────────────────────────────────────────────────────────────

class TestManifest:
    def test_manifest_returns_routes(self):
        resp = requests.get(f'{BASE_URL}/api/app/manifest/', headers=_headers(), timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert 'routes' in data
        assert len(data['routes']) > 0
        assert 'route_count' in data

    def test_manifest_has_studios(self):
        resp = requests.get(f'{BASE_URL}/api/app/manifest/', headers=_headers(), timeout=10)
        data = resp.json()
        studios = data.get('studios', {})
        assert 'image' in studios
        assert 'video' in studios

    def test_manifest_has_capabilities(self):
        resp = requests.get(f'{BASE_URL}/api/app/manifest/', headers=_headers(), timeout=10)
        data = resp.json()
        caps = data.get('capabilities', {})
        assert caps.get('pa_chat') is True
        assert caps.get('media_library') is True

    def test_manifest_requires_auth(self):
        resp = requests.get(f'{BASE_URL}/api/app/manifest/', timeout=10)
        assert resp.status_code in (401, 403)


# ── Deploy Verify ────────────────────────────────────────────────────────────

class TestDeployVerify:
    @pytest.mark.skipif(not ADMIN_TOKEN, reason='ADMIN_TOKEN not set')
    def test_deploy_verify_runs(self):
        resp = requests.post(
            f'{BASE_URL}/api/deploy/verify/',
            headers=_headers(ADMIN_TOKEN),
            timeout=60,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert 'all_ok' in data
        assert 'passed' in data
        assert 'total' in data
        assert data['total'] > 0

    def test_deploy_verify_requires_admin(self):
        # PA service token is non-admin, should get 403
        resp = requests.post(
            f'{BASE_URL}/api/deploy/verify/',
            headers=_headers(),
            timeout=10,
        )
        assert resp.status_code in (401, 403)


# ── Studio APIs ──────────────────────────────────────────────────────────────

class TestStudioAPIs:
    def test_gallery_list(self):
        resp = requests.get(
            f'{BASE_URL}/api/v1/gallery/list/',
            headers=_headers(),
            timeout=10,
        )
        assert resp.status_code == 200

    def test_video_gallery(self):
        resp = requests.get(
            f'{BASE_URL}/api/v1/video/gallery/',
            headers=_headers(),
            timeout=10,
        )
        assert resp.status_code == 200


# ── PA Service Account ───────────────────────────────────────────────────────

class TestPAServiceAccount:
    @pytest.mark.skipif(not PA_TOKEN, reason='PA_SERVICE_TOKEN not set')
    def test_pa_token_auth(self):
        """PA service token can access the manifest endpoint."""
        resp = requests.get(
            f'{BASE_URL}/api/app/manifest/',
            headers=_headers(PA_TOKEN),
            timeout=10,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get('route_count', 0) > 0
