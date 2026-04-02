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
from rest_framework.permissions import AllowAny, IsAuthenticated
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

    # Fallback: hardcoded minimal manifest — NOT cached so SHA stays fresh
    # (backend_sha is read from env each request in get_manifest_data)
    return _fallback_manifest()


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
            {'path': '/media', 'label': 'Media', 'authRequired': True, 'category': 'studio'},
            {'path': '/image-studio', 'label': 'Image Studio', 'authRequired': True, 'category': 'studio'},
            {'path': '/video-studio', 'label': 'Video Studio', 'authRequired': True, 'category': 'studio'},
            {'path': '/initiatives', 'label': 'Initiatives', 'authRequired': True, 'category': 'command'},
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
            {'path': '/diagnostics', 'label': 'Diagnostics', 'authRequired': True, 'category': 'admin'},
            {'path': '/profile', 'label': 'Profile', 'authRequired': True, 'category': 'admin'},
            {'path': '/code-runner', 'label': 'Code Runner', 'authRequired': True, 'roles': ['admin'], 'category': 'admin'},
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
        'api_dependencies': {},
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

    # Filter api_dependencies to only include routes the user can see
    visible_paths = {r['path'] for r in routes}
    api_deps = {
        k: v for k, v in manifest.get('api_dependencies', {}).items()
        if k in visible_paths
    }

    # Backend deploy identity from Railway env vars
    backend_sha = os.getenv('RAILWAY_GIT_COMMIT_SHA', '')
    deployment_id = os.getenv('RAILWAY_DEPLOYMENT_ID', '')
    service_name = os.getenv('RAILWAY_SERVICE_NAME', '')

    build_sha = manifest.get('build_sha', 'unknown')
    if build_sha == 'unknown' and backend_sha:
        build_sha = backend_sha

    # Latest applied migration
    latest_migration = None
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT app, name FROM django_migrations ORDER BY id DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if row:
                latest_migration = f"{row[0]}.{row[1]}"
    except Exception:
        pass

    return {
        'build_sha': build_sha,
        'backend_sha': backend_sha or None,
        'deployment_id': deployment_id or None,
        'service_name': service_name or None,
        'latest_migration': latest_migration,
        'build_timestamp': manifest.get('build_timestamp'),
        'env': manifest.get('env', 'unknown'),
        'route_count': len(routes),
        'routes': routes,
        'studios': manifest.get('studios', {}),
        'capabilities': manifest.get('capabilities', {}),
        'api_dependencies': api_deps,
        'user_role': role,
        'user_id': user.id,
    }


# ── REST endpoint ────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def app_manifest(request):
    # Unauthenticated callers get a minimal deploy-verification payload
    # (backend_sha, latest_migration, env) without RBAC-filtered routes.
    if not request.user or not request.user.is_authenticated:
        backend_sha = os.getenv('RAILWAY_GIT_COMMIT_SHA', '')
        latest_migration = None
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT app, name FROM django_migrations ORDER BY id DESC LIMIT 1"
                )
                row = cursor.fetchone()
                if row:
                    latest_migration = f"{row[0]}.{row[1]}"
        except Exception:
            pass
        manifest = _load_manifest()
        return Response({
            'backend_sha': backend_sha or None,
            'latest_migration': latest_migration,
            'env': manifest.get('env', 'unknown'),
            'route_count': len(manifest.get('routes', [])),
        })
    return Response(get_manifest_data(request.user))


def _summarize_tool_schemas():
    """Summarize PA_TOOL_SCHEMAS into a lightweight registry list."""
    from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS

    tools = []
    for schema in PA_TOOL_SCHEMAS:
        params = schema.get('parameters', {})
        props = params.get('properties', {})
        action_enum = props.get('action', {}).get('enum', [])
        tools.append({
            'name': schema.get('name', ''),
            'description': schema.get('description', '')[:200],
            'actions': action_enum if action_enum else None,
            'param_count': len(props),
        })
    return tools


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pa_tool_registry(request):
    """Return a summary of all PA tool schemas."""
    tools = _summarize_tool_schemas()
    return Response({'tools': tools, 'count': len(tools)})
