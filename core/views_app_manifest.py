"""
GET /api/app/manifest/ — RBAC-filtered frontend capabilities manifest.

Reads the build-time ``__manifest.json`` produced by the frontend postbuild
script and filters routes by the requesting user's role.  Falls back to a
hardcoded minimal route list if the file is missing.
"""

import json
import logging
import os

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)

# ── Cached manifest (loaded once per process) ────────────────────────────────

_MANIFEST_CACHE: dict | None = None


def _load_manifest() -> dict:
    global _MANIFEST_CACHE
    if _MANIFEST_CACHE is not None:
        return _MANIFEST_CACHE

    manifest_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'frontend', 'dist', '__manifest.json',
    )

    if os.path.isfile(manifest_path):
        try:
            with open(manifest_path) as f:
                _MANIFEST_CACHE = json.load(f)
                return _MANIFEST_CACHE
        except Exception as exc:
            logger.warning('Failed to load manifest: %s', exc)

    # Fallback: hardcoded minimal manifest
    _MANIFEST_CACHE = _fallback_manifest()
    return _MANIFEST_CACHE


def _fallback_manifest() -> dict:
    return {
        'build_sha': 'unknown',
        'build_timestamp': None,
        'env': os.getenv('RAILWAY_ENVIRONMENT', 'local'),
        'route_count': 30,
        'routes': [
            {'path': '/', 'label': 'Command Center', 'authRequired': True, 'category': 'command'},
            {'path': '/dashboard', 'label': 'Dashboard', 'authRequired': True, 'category': 'command'},
            {'path': '/workspace', 'label': 'Workspace', 'authRequired': True, 'category': 'command'},
            {'path': '/boardroom', 'label': 'Boardroom', 'authRequired': True, 'category': 'command'},
            {'path': '/governance', 'label': 'Governance', 'authRequired': True, 'category': 'command'},
            {'path': '/platform', 'label': 'Platform', 'authRequired': True, 'category': 'command'},
            {'path': '/billing', 'label': 'Billing', 'authRequired': True, 'category': 'command'},
            {'path': '/analytics', 'label': 'Analytics', 'authRequired': True, 'category': 'command'},
            {'path': '/image-studio', 'label': 'Image Studio', 'authRequired': True, 'category': 'studio'},
            {'path': '/video-studio', 'label': 'Video Studio', 'authRequired': True, 'category': 'studio'},
            {'path': '/intelligence', 'label': 'Intelligence', 'authRequired': True, 'category': 'intelligence'},
            {'path': '/agents', 'label': 'Agents', 'authRequired': True, 'category': 'intelligence'},
            {'path': '/advisors', 'label': 'Advisors', 'authRequired': True, 'category': 'intelligence'},
            {'path': '/neural-orchestra', 'label': 'Neural Orchestra', 'authRequired': True, 'category': 'intelligence'},
            {'path': '/content', 'label': 'Content', 'authRequired': True, 'category': 'domain'},
            {'path': '/betting', 'label': 'Betting', 'authRequired': True, 'category': 'domain'},
            {'path': '/stocks', 'label': 'Stock Intelligence', 'authRequired': True, 'category': 'domain'},
            {'path': '/portfolio', 'label': 'Portfolio', 'authRequired': True, 'category': 'domain'},
            {'path': '/legal', 'label': 'Legal', 'authRequired': True, 'category': 'domain'},
            {'path': '/government', 'label': 'Government', 'authRequired': True, 'category': 'domain'},
            {'path': '/documents', 'label': 'Documents', 'authRequired': True, 'category': 'domain'},
            {'path': '/docs-index', 'label': 'Docs Index', 'authRequired': True, 'category': 'reference'},
            {'path': '/how-it-works', 'label': 'How It Works', 'authRequired': True, 'category': 'reference'},
            {'path': '/admin', 'label': 'Admin', 'authRequired': True, 'roles': ['admin'], 'category': 'admin'},
            {'path': '/settings', 'label': 'Settings', 'authRequired': True, 'category': 'admin'},
            {'path': '/profile', 'label': 'Profile', 'authRequired': True, 'category': 'admin'},
            {'path': '/login', 'label': 'Login', 'authRequired': False, 'category': 'auth'},
        ],
        'studios': {
            'image': {'enabled': True, 'path': '/image-studio', 'models': ['stability-ai', 'dall-e-3', 'replicate'], 'endpoint': '/api/v1/gallery/'},
            'video': {'enabled': True, 'path': '/video-studio', 'models': ['runway-ml', 'ffmpeg-edit'], 'endpoint': '/api/v1/video/'},
            'audio': {'enabled': True, 'path': '', 'models': ['elevenlabs-tts'], 'endpoint': '/api/v1/audio/'},
        },
        'capabilities': {
            'pa_chat': True,
            'websocket': True,
            'media_library': True,
            'resolve_node': True,
            'deliberation_pipeline': True,
            'initiative_pipeline': True,
            'spider_network': True,
            'body_systems': True,
        },
    }


def _user_role(user) -> str:
    """Return the effective platform role for RBAC filtering."""
    if user.is_superuser or user.is_staff:
        return 'admin'
    try:
        from core.models import EnhancedUserProfile
        profile = EnhancedUserProfile.objects.filter(user=user).first()
        if profile and getattr(profile, 'platform_role', None):
            return profile.platform_role
    except Exception:
        pass
    return 'viewer'


def _filter_routes(routes: list, role: str) -> list:
    """Remove routes the user's role cannot access."""
    if role == 'admin':
        return routes  # admins see everything

    filtered = []
    for r in routes:
        required_roles = r.get('roles')
        if required_roles and role not in required_roles:
            continue
        # Non-admin users don't see admin-category routes
        if r.get('category') == 'admin' and role != 'admin':
            continue
        filtered.append(r)
    return filtered


def get_manifest_data(user) -> dict:
    """Return the full manifest dict, filtered for the given user.

    Used by both the REST endpoint and the PA tool handler (no HTTP round-trip).
    """
    manifest = _load_manifest()
    role = _user_role(user)
    routes = _filter_routes(manifest.get('routes', []), role)

    return {
        'build_sha': manifest.get('build_sha', 'unknown'),
        'build_timestamp': manifest.get('build_timestamp'),
        'env': manifest.get('env', 'unknown'),
        'route_count': len(routes),
        'routes': routes,
        'studios': manifest.get('studios', {}),
        'capabilities': manifest.get('capabilities', {}),
        'user_role': role,
        'user_id': user.id,
    }


# ── REST endpoint ────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def app_manifest(request):
    return Response(get_manifest_data(request.user))
