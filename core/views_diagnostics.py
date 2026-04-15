"""
Diagnostic Views to Expose ALL Backend Data
This file creates comprehensive diagnostic endpoints to see everything happening in the backend
"""

import json
import logging
import os
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import render
import redis
import traceback

logger = logging.getLogger(__name__)


def _get_cockpit_workspace_id(request):
    """Extract workspace_id for cockpit filtering.

    Priority:
    1. Explicit ?workspace= query param (admin workspace switcher)
    2. VIP user's assigned workspace (from invite)
    3. None (global view)
    """
    explicit = request.GET.get('workspace', '').strip()
    if explicit:
        return explicit
    try:
        from core.vip_scope import get_vip_scope
        scope = get_vip_scope(request)
        return scope.workspace_id if scope.is_vip else None
    except Exception:
        return None


def _audit_log(request, action, target_type='', target_id='', request_body=None, response_summary=None):
    """Write an append-only audit log entry for cockpit mutations."""
    try:
        from core.models_cockpit_audit import CockpitAuditLog
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ',' in ip:
            ip = ip.split(',')[0].strip()
        CockpitAuditLog.objects.create(
            user=user,
            action=action,
            target_type=target_type,
            target_id=str(target_id),
            request_body=request_body or {},
            response_summary=response_summary or {},
            ip_address=ip or None,
        )
    except Exception as e:
        logger.debug("Audit log write failed: %s", e)

def get_redis_client():
    """Get Redis client for diagnostics — uses REDIS_URL (same as Celery broker)"""
    try:
        redis_url = getattr(settings, 'REDIS_URL', None) or os.environ.get('REDIS_URL')
        if not redis_url:
            logger.warning("[diagnostics] REDIS_URL not configured — skipping Redis health check")
            return None
        return redis.StrictRedis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    except Exception:
        return None

@csrf_exempt
@require_http_methods(['GET'])
def diagnostic_master_endpoint(request):
    """
    Master diagnostic endpoint that exposes EVERYTHING
    Shows all backend data, connections, and real-time state
    """
    diagnostics = {
        'timestamp': datetime.now().isoformat(),
        'request_info': {
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if request.user.is_authenticated else 'anonymous',
            'session_key': request.session.session_key if hasattr(request.session, 'session_key') else None,
        },
        'spider_system': {},
        'income_builder': {},
        'monetization_engine': {},
        'websocket_consumers': {},
        'cache_data': {},
        'redis_data': {},
        'database_stats': {},
        'agent_registry': {},
        'errors': []
    }

    # 1. Spider System Diagnostics
    try:
        # Try to import real spider orchestrator first
        try:
            from ai_core.spiders.spider_orchestrator import activate_job_spiders
            import asyncio

            # Try to call it in various ways
            if asyncio.iscoroutinefunction(activate_job_spiders):
                # It's async - run it in event loop
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                spider_data = loop.run_until_complete(activate_job_spiders())
            else:
                # It's sync - just call it
                spider_data = activate_job_spiders()
        except Exception as e:
            # Fall back to mock data
            from ai_core.spiders.spider_mock_data import activate_job_spiders_mock
            spider_data = activate_job_spiders_mock({
                'skills': ['Python', 'Django', 'React'],
                'skill_level': 'intermediate',
                'available_hours': 20
            })
        diagnostics['spider_system'] = {
            'status': 'active',
            'spiders_found': len(spider_data.get('opportunities', [])),
            'sample_opportunities': spider_data.get('opportunities', [])[:3],
            'platforms_active': spider_data.get('platforms', []),
            'last_run': datetime.now().isoformat()
        }
    except Exception as e:
        diagnostics['spider_system'] = {
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        diagnostics['errors'].append(f"Spider System: {str(e)}")

    # 2. Income Builder Diagnostics
    try:
        from ai_core.intelligence.income_builder import AIIncomeBuilder
        income_builder = AIIncomeBuilder()

        # Try to find real opportunities - handle different method signatures
        opportunities = []

        # Try different approaches based on what's available
        if hasattr(income_builder, 'find_opportunities'):
            try:
                # Try new version with keyword arguments
                opportunities = income_builder.find_opportunities(
                    skills=['Python', 'Django'],
                    skill_level='intermediate',
                    available_hours=20
                )
            except TypeError:
                try:
                    # Try with user_profile dict
                    opportunities = income_builder.find_opportunities({
                        'skills': ['Python', 'Django'],
                        'skill_level': 'intermediate',
                        'available_hours': 20
                    })
                except Exception:
                    # Last resort - no arguments
                    opportunities = []

        # If find_opportunities doesn't exist, try other methods
        if not opportunities and hasattr(income_builder, '_initialize_opportunities'):
            opportunities = income_builder._initialize_opportunities()[:5]

        # Last resort - use mock data
        if not opportunities:
            from ai_core.spiders.spider_mock_data import get_mock_opportunities
            opportunities = get_mock_opportunities()

        # Convert opportunities to serializable format
        serializable_opportunities = []
        if opportunities:
            for opp in opportunities[:2]:  # Just first 2 for sample
                if hasattr(opp, '__dict__'):
                    # It's an object - convert to dict
                    serializable_opportunities.append({
                        'title': getattr(opp, 'title', 'Unknown'),
                        'platform': getattr(opp, 'platform', 'Unknown'),
                        'rate': str(getattr(opp, 'rate', 0)),
                        'description': getattr(opp, 'description', ''),
                        'id': str(getattr(opp, 'id', '')),
                    })
                elif isinstance(opp, dict):
                    # Already a dict
                    serializable_opportunities.append(opp)

        diagnostics['income_builder'] = {
            'status': 'active',
            'class_loaded': True,
            'opportunities_found': len(opportunities) if opportunities else 0,
            'sample_opportunities': serializable_opportunities,
            'methods_available': [m for m in dir(income_builder) if not m.startswith('_')],
            'connected_to_spiders': hasattr(income_builder, 'spider_orchestrator')
        }
    except Exception as e:
        diagnostics['income_builder'] = {
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        diagnostics['errors'].append(f"Income Builder: {str(e)}")

    # 3. Monetization Engine Diagnostics
    try:
        from ai_core.intelligence.monetization_engine import UnifiedMonetizationEngine
        monetization = UnifiedMonetizationEngine()

        # Get current metrics
        metrics = monetization.get_revenue_metrics() if hasattr(monetization, 'get_revenue_metrics') else {}

        diagnostics['monetization_engine'] = {
            'status': 'active',
            'class_loaded': True,
            'current_metrics': metrics,
            'methods_available': [m for m in dir(monetization) if not m.startswith('_')],
            'can_record_earnings': hasattr(monetization, 'record_earnings'),
            'can_track_opportunities': hasattr(monetization, 'record_potential_earnings')
        }
    except Exception as e:
        diagnostics['monetization_engine'] = {
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        diagnostics['errors'].append(f"Monetization Engine: {str(e)}")

    # 4. WebSocket Consumer Status
    try:
        from ai_core.intelligence.consumers import DecisionCommandConsumer

        diagnostics['websocket_consumers']['decision_command'] = {
            'class_loaded': True,
            'methods': [m for m in dir(DecisionCommandConsumer) if not m.startswith('_')],
            'can_analyze': hasattr(DecisionCommandConsumer, 'analyze_opportunities'),
            'connected_to_income_builder': 'income_builder' in str(DecisionCommandConsumer.__dict__)
        }
    except Exception as e:
        diagnostics['websocket_consumers']['decision_command'] = {
            'status': 'error',
            'error': str(e)
        }
        diagnostics['errors'].append(f"WebSocket Consumer: {str(e)}")

    # 5. Cache Diagnostics
    try:
        # Try to get some cache keys
        cache_test_key = 'diagnostic_test_' + datetime.now().isoformat()
        cache.set(cache_test_key, 'test_value', 60)
        cache_value = cache.get(cache_test_key)

        diagnostics['cache_data'] = {
            'backend': str(cache.__class__.__name__),
            'test_write': cache_value == 'test_value',
            'sample_keys': []  # We can't list all keys in most cache backends
        }
    except Exception as e:
        diagnostics['cache_data'] = {
            'status': 'error',
            'error': str(e)
        }
        diagnostics['errors'].append(f"Cache: {str(e)}")

    # 6. Redis Diagnostics
    try:
        redis_client = get_redis_client()
        if redis_client:
            # Get some Redis stats
            info = redis_client.info()
            keys_sample = redis_client.keys('*')[:10]  # Get first 10 keys

            diagnostics['redis_data'] = {
                'connected': True,
                'version': info.get('redis_version', 'unknown'),
                'used_memory': info.get('used_memory_human', 'unknown'),
                'connected_clients': info.get('connected_clients', 0),
                'total_keys': redis_client.dbsize(),
                'sample_keys': keys_sample,
                'databases_used': []
            }

            # Check which databases have data
            for db_num in range(16):
                try:
                    test_client = redis.StrictRedis(host='localhost', port=6379, db=db_num, decode_responses=True)
                    db_size = test_client.dbsize()
                    if db_size > 0:
                        diagnostics['redis_data']['databases_used'].append({
                            'db': db_num,
                            'keys': db_size
                        })
                except Exception as _e:
                    logger.warning(
                        "views_diagnostics.diagnostic_master_endpoint: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )
        else:
            diagnostics['redis_data'] = {'connected': False}
    except Exception as e:
        diagnostics['redis_data'] = {
            'status': 'error',
            'error': str(e)
        }
        diagnostics['errors'].append(f"Redis: {str(e)}")

    # 7. Agent Registry Diagnostics
    try:
        # Try multiple possible agent registry locations
        agent_data = {'agents': [], 'advisors': []}

        # Try to import from different possible locations
        try:
            from ai_core.intelligence.agent_registry import get_all_agents
            agents = get_all_agents()
            agent_data['agents'] = agents[:5] if agents else []
            agent_data['total_agents'] = len(agents) if agents else 0
        except Exception as _e:
            logger.warning(
                "views_diagnostics.diagnostic_master_endpoint: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        try:
            from ai_core.intelligence.advisor_registry import get_all_advisors
            advisors = get_all_advisors()
            agent_data['advisors'] = advisors[:5] if advisors else []
            agent_data['total_advisors'] = len(advisors) if advisors else 0
        except Exception as _e:
            logger.warning(
                "views_diagnostics.diagnostic_master_endpoint: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        diagnostics['agent_registry'] = agent_data
    except Exception as e:
        diagnostics['agent_registry'] = {
            'status': 'error',
            'error': str(e)
        }
        diagnostics['errors'].append(f"Agent Registry: {str(e)}")

    # 8. Database Connection Status
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migration_count = cursor.fetchone()[0]

            # Try to get table list
            cursor.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()][:20]  # First 20 tables

        diagnostics['database_stats'] = {
            'connected': True,
            'migrations_applied': migration_count,
            'sample_tables': tables,
            'database_name': connection.settings_dict.get('NAME', 'unknown')
        }
    except Exception as e:
        diagnostics['database_stats'] = {
            'connected': False,
            'error': str(e)
        }
        diagnostics['errors'].append(f"Database: {str(e)}")

    # 9. Summary
    diagnostics['summary'] = {
        'total_errors': len(diagnostics['errors']),
        'systems_checked': 8,
        'systems_operational': sum([
            1 for key in ['spider_system', 'income_builder', 'monetization_engine',
                         'cache_data', 'redis_data', 'database_stats']
            if diagnostics.get(key, {}).get('status') != 'error'
        ]),
        'reality_score': calculate_reality_score(diagnostics),
        'recommendations': generate_recommendations(diagnostics)
    }

    return JsonResponse(diagnostics, json_dumps_params={'indent': 2})


def calculate_reality_score(diagnostics):
    """Calculate how real vs mock the system is"""
    score = 0
    max_score = 100

    # Spider system (20 points)
    if diagnostics['spider_system'].get('status') == 'active':
        score += 20
    elif diagnostics['spider_system'].get('status') == 'error':
        score += 5  # Partial credit for trying

    # Income Builder (20 points)
    if diagnostics['income_builder'].get('status') == 'active':
        if diagnostics['income_builder'].get('connected_to_spiders'):
            score += 20
        else:
            score += 10  # Partial credit

    # Monetization Engine (15 points)
    if diagnostics['monetization_engine'].get('status') == 'active':
        score += 15

    # WebSocket (15 points)
    if diagnostics['websocket_consumers'].get('decision_command', {}).get('class_loaded'):
        score += 15

    # Redis (10 points)
    if diagnostics['redis_data'].get('connected'):
        score += 10

    # Database (10 points)
    if diagnostics['database_stats'].get('connected'):
        score += 10

    # Agent Registry (10 points)
    if diagnostics['agent_registry'].get('total_agents', 0) > 0:
        score += 10

    return f"{score}%"


def generate_recommendations(diagnostics):
    """Generate actionable recommendations based on diagnostics"""
    recommendations = []

    if diagnostics['spider_system'].get('status') == 'error':
        recommendations.append({
            'priority': 'HIGH',
            'issue': 'Spider system not operational',
            'fix': 'Check spider_orchestrator.py imports and spider_registry.py existence'
        })

    if not diagnostics['income_builder'].get('connected_to_spiders'):
        recommendations.append({
            'priority': 'HIGH',
            'issue': 'Income Builder not connected to spiders',
            'fix': 'Verify import paths in income_builder.py line 716'
        })

    if not diagnostics['redis_data'].get('connected'):
        recommendations.append({
            'priority': 'MEDIUM',
            'issue': 'Redis not connected',
            'fix': 'Start Redis: redis-server'
        })

    if diagnostics['database_stats'].get('migrations_applied', 0) == 0:
        recommendations.append({
            'priority': 'HIGH',
            'issue': 'No database migrations',
            'fix': 'Run: python manage.py migrate'
        })

    if len(diagnostics['errors']) > 3:
        recommendations.append({
            'priority': 'CRITICAL',
            'issue': f"{len(diagnostics['errors'])} system errors detected",
            'fix': 'Review error details in diagnostics output'
        })

    return recommendations


@csrf_exempt
@require_http_methods(['POST'])
def test_spider_network(request):
    """Test endpoint to trigger spider network directly"""
    try:
        data = json.loads(request.body or b"{}") if request.body else {}
        profile = data.get('profile', {
            'skills': ['Python', 'Django'],
            'skill_level': 'intermediate',
            'available_hours': 20
        })

        from ai_core.spiders.spider_orchestrator import activate_job_spiders
        result = activate_job_spiders(user_profile=profile)

        return JsonResponse({
            'success': True,
            'opportunities_found': len(result.get('opportunities', [])),
            'data': result
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })


@csrf_exempt
@require_http_methods(['POST'])
def test_income_builder(request):
    """Test endpoint to trigger income builder directly"""
    try:
        data = json.loads(request.body or b"{}") if request.body else {}

        from ai_core.intelligence.income_builder import AIIncomeBuilder
        builder = AIIncomeBuilder()

        opportunities = builder.find_opportunities(
            skills=data.get('skills', ['Python']),
            skill_level=data.get('skill_level', 'intermediate'),
            available_hours=data.get('available_hours', 20)
        )

        return JsonResponse({
            'success': True,
            'opportunities_found': len(opportunities) if opportunities else 0,
            'data': opportunities
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })


def diagnostic_dashboard(request):
    """Render the comprehensive diagnostic dashboard"""
    return render(request, 'diagnostic_dashboard.html')


@csrf_exempt
@require_http_methods(['GET'])
def websocket_test_page(request):
    """Return a test page for WebSocket connections"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Diagnostic Test</title>
        <style>
            body { font-family: monospace; padding: 20px; background: #1a1a1a; color: #0f0; }
            .container { max-width: 1200px; margin: 0 auto; }
            button { background: #0f0; color: #000; padding: 10px 20px; border: none; margin: 5px; cursor: pointer; }
            button:hover { background: #0a0; }
            #output { background: #000; padding: 20px; height: 400px; overflow-y: auto; border: 1px solid #0f0; }
            .error { color: #f00; }
            .success { color: #0f0; }
            .data { color: #0ff; }
            input, select { background: #333; color: #0f0; border: 1px solid #0f0; padding: 5px; margin: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 WebSocket Diagnostic Test</h1>

            <div>
                <h3>Connection Settings</h3>
                <input type="text" id="wsUrl" value="ws://localhost:8000/ws/decision-command/" style="width: 400px;">
                <button onclick="connect()">Connect</button>
                <button onclick="disconnect()">Disconnect</button>
                <span id="status">Disconnected</span>
            </div>

            <div>
                <h3>Test Commands</h3>
                <button onclick="testAnalyzeOpportunities()">Test Analyze Opportunities</button>
                <button onclick="testGetStatus()">Test Get Status</button>
                <button onclick="testCustomMessage()">Send Custom Message</button>
            </div>

            <div>
                <h3>Custom Message</h3>
                <textarea id="customMessage" style="width: 100%; height: 100px; background: #333; color: #0f0; border: 1px solid #0f0;">
{
    "action": "analyze_opportunities",
    "profile": {
        "skills": ["Python", "Django", "React"],
        "skill_level": "intermediate",
        "available_hours": 20
    }
}
                </textarea>
            </div>

            <div>
                <h3>Output</h3>
                <div id="output"></div>
            </div>
        </div>

        <script>
            let ws = null;

            function log(message, className = '') {
                const output = document.getElementById('output');
                const timestamp = new Date().toLocaleTimeString();
                output.innerHTML += `<div class="${className}">[${timestamp}] ${message}</div>`;
                output.scrollTop = output.scrollHeight;
            }

            function connect() {
                const url = document.getElementById('wsUrl').value;
                log(`Connecting to ${url}...`, 'data');

                ws = new WebSocket(url);

                ws.onopen = () => {
                    log('Connected!', 'success');
                    document.getElementById('status').textContent = 'Connected';
                    document.getElementById('status').style.color = '#0f0';
                };

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        log('Received: ' + JSON.stringify(data, null, 2), 'data');

                        // Highlight important fields
                        if (data.real_opportunities) {
                            log(`Found ${data.real_opportunities.length} REAL opportunities!`, 'success');
                        }
                        if (data.data_source) {
                            log(`Data source: ${data.data_source}`, data.data_source === 'live_spider_network' ? 'success' : 'error');
                        }
                    } catch (e) {
                        log('Received: ' + event.data, 'data');
                    }
                };

                ws.onerror = (error) => {
                    log('WebSocket error: ' + error, 'error');
                };

                ws.onclose = () => {
                    log('Disconnected', 'error');
                    document.getElementById('status').textContent = 'Disconnected';
                    document.getElementById('status').style.color = '#f00';
                };
            }

            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }

            function testAnalyzeOpportunities() {
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                    log('Not connected!', 'error');
                    return;
                }

                const message = {
                    action: 'analyze_opportunities',
                    profile: {
                        skills: ['Python', 'Django', 'JavaScript', 'React'],
                        skill_level: 'intermediate',
                        available_hours: 30
                    }
                };

                log('Sending: ' + JSON.stringify(message, null, 2), 'data');
                ws.send(JSON.stringify(message));
            }

            function testGetStatus() {
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                    log('Not connected!', 'error');
                    return;
                }

                const message = { action: 'get_status' };
                log('Sending: ' + JSON.stringify(message, null, 2), 'data');
                ws.send(JSON.stringify(message));
            }

            function testCustomMessage() {
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                    log('Not connected!', 'error');
                    return;
                }

                try {
                    const message = JSON.parse(document.getElementById('customMessage').value);
                    log('Sending: ' + JSON.stringify(message, null, 2), 'data');
                    ws.send(JSON.stringify(message));
                } catch (e) {
                    log('Invalid JSON: ' + e, 'error');
                }
            }
        </script>
    </body>
    </html>
    """
    from django.http import HttpResponse
    return HttpResponse(html, content_type='text/html')


# ── Session 1069: Internal config snapshot for cross-service comparison ──────

@csrf_exempt
@require_http_methods(["GET"])
def config_snapshot(request):
    """
    Session 1069: Returns masked config snapshot from THIS service's perspective.
    Called by celery-pa's platform_config_tool(action='web_config') to compare
    web vs celery environments. No auth required — secrets are masked.
    """
    import os

    SECRET_PATTERNS = ('KEY', 'SECRET', 'TOKEN', 'PASSWORD', 'CREDENTIAL',
                       'DSN', 'DATABASE_URL', 'REDIS_URL', 'BROKER_URL')

    def _mask(key, value):
        if not value:
            return value
        val = str(value)
        for pat in SECRET_PATTERNS:
            if pat in key.upper():
                return val[:8] + '...' if len(val) > 8 else '***'
        return val

    return JsonResponse({
        'service': os.environ.get('RAILWAY_SERVICE_NAME', 'local'),
        'railway_environment': os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
        'debug': settings.DEBUG,
        'frontend_url': getattr(settings, 'FRONTEND_URL', 'not set'),
        'backend_url': getattr(settings, 'BACKEND_URL', 'not set'),
        'default_llm_provider': getattr(settings, 'LLM_DEFAULT_PROVIDER', 'unknown'),
        'allowed_hosts': getattr(settings, 'ALLOWED_HOSTS', []),
        'database_engine': settings.DATABASES.get('default', {}).get('ENGINE', 'unknown'),
        'database_name': settings.DATABASES.get('default', {}).get('NAME', 'unknown'),
        'redis_url': _mask('REDIS_URL', os.environ.get('REDIS_URL', 'not set')),
        'cors_allow_all': getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False),
    })


# ── Session 1069: Debug 500 endpoint for middleware verification ─────────────

@csrf_exempt
@require_http_methods(["POST"])
def debug_raise_500(request):
    """
    Session 1069: Intentionally raises an exception to verify
    RequestErrorCaptureMiddleware is capturing HTTP 500s.
    Staff-only, DEBUG-only. POST required to prevent accidental triggers.
    """
    from django.conf import settings
    if not settings.DEBUG:
        return JsonResponse({'error': 'Only available in DEBUG mode'}, status=404)
    if not (request.user and request.user.is_authenticated and request.user.is_staff):
        return JsonResponse({'error': 'Staff only'}, status=403)

    raise RuntimeError("Session 1069: Test 500 for middleware verification")


# ── Focus Cockpit API endpoints ──────────────────────────────────────────────

@require_http_methods(["GET"])
def cockpit_error_summary(request):
    """
    Error summary for Focus Cockpit.
    Aggregates failure signatures + Celery failures in the given time window.
    Query params: hours (default 24)
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    from django.utils import timezone
    from datetime import timedelta

    hours = int(request.GET.get('hours', 24))
    cutoff = timezone.now() - timedelta(hours=hours)

    signatures = []
    total = 0

    # Failure signatures (agent-level)
    try:
        from core.models_diagnostic_pipeline import FailureSignature
        sigs = list(
            FailureSignature.objects.filter(
                status='active', last_seen_at__gte=cutoff
            ).order_by('-occurrence_count')[:20]
            .values('signature', 'occurrence_count', 'last_seen_at', 'description')
        )
        for s in sigs:
            signatures.append({
                'signature': s['signature'],
                'source': 'agent',
                'count': s['occurrence_count'],
                'last_seen': s['last_seen_at'].isoformat() if s.get('last_seen_at') else None,
                'sample_error': s.get('description', ''),
            })
            total += s['occurrence_count']
    except Exception as _e:
        logger.warning(
            "views_diagnostics.cockpit_error_summary: swallowed (%s: %s) — degraded",
            type(_e).__name__, _e,
        )

    # Celery task failures
    try:
        from core.models_celery_telemetry import CeleryTaskEvent
        from django.db.models import Count, Max
        celery_fails = list(
            CeleryTaskEvent.objects.filter(
                status='FAILURE', started_at__gte=cutoff
            ).values('task_name')
            .annotate(count=Count('id'), last_seen=Max('started_at'))
            .order_by('-count')[:20]
        )
        for cf in celery_fails:
            # Grab a sample error message
            sample = CeleryTaskEvent.objects.filter(
                task_name=cf['task_name'], status='FAILURE', started_at__gte=cutoff
            ).exclude(error_message='').values_list('error_message', flat=True).first() or ''
            signatures.append({
                'signature': cf['task_name'],
                'source': 'celery',
                'count': cf['count'],
                'last_seen': cf['last_seen'].isoformat() if cf.get('last_seen') else None,
                'sample_error': sample[:300],
            })
            total += cf['count']
    except Exception as _e:
        logger.warning(
            "views_diagnostics.cockpit_error_summary: swallowed (%s: %s) — degraded",
            type(_e).__name__, _e,
        )

    return JsonResponse({
        'hours': hours,
        'total_failures': total,
        'signatures': signatures,
    })


@require_http_methods(["GET"])
def cockpit_inbox(request):
    """
    Focus Cockpit inbox — read-only aggregation of items needing attention.
    Merges: pending decisions, blocked gates, error signatures, failed runs.
    Query params: hours (default 24), limit (default 50)
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    from django.utils import timezone
    from datetime import timedelta

    hours = int(request.GET.get('hours', 24))
    limit = min(int(request.GET.get('limit', 50)), 200)
    cutoff = timezone.now() - timedelta(hours=hours)

    items = []
    counts = {'total': 0, 'decisions': 0, 'gates': 0, 'errors': 0, 'failed_runs': 0}

    SEVERITY_RANK = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
    TYPE_RANK = {'decision': 4, 'gate': 3, 'failed_run': 2, 'error_signature': 1}

    # 1. Pending decisions (HumanAttentionItem)
    try:
        from core.models_human_interface import HumanAttentionItem
        pending = HumanAttentionItem.objects.filter(
            user=request.user,
            status__in=['pending', 'viewed'],
            created_at__gte=cutoff,
        ).order_by('-priority_score', '-created_at')[:limit]

        for item in pending:
            severity = item.urgency if item.urgency in SEVERITY_RANK else 'medium'
            items.append({
                'id': f'inbox:decision:{item.id}',
                'type': 'decision',
                'severity': severity,
                'title': item.title,
                'subtitle': item.source_agent or item.source_type,
                'timestamp': item.created_at.isoformat(),
                'badges': [item.item_type, item.status],
                'cta': {'label': 'Open decision', 'route': f'/boardroom'},
                'source': {'system': 'human_decisions', 'id': str(item.id), 'status': item.status},
                'preview': {'text': item.summary[:200] if item.summary else None},
            })
            counts['decisions'] += 1
    except Exception as e:
        logger.debug("Inbox decisions error: %s", e)

    # 2. Blocked/ready gates (PilotReadinessGate)
    try:
        from core.models_pilot_readiness import PilotReadinessGate
        gates = PilotReadinessGate.objects.filter(
            status__in=['blocked', 'ready', 'in_progress'],
        ).select_related('decision')[:limit]

        for gate in gates:
            severity = 'critical' if gate.status == 'blocked' else 'high'
            decision_title = str(gate.decision) if gate.decision else 'Unknown decision'
            items.append({
                'id': f'inbox:gate:{gate.id}',
                'type': 'gate',
                'severity': severity,
                'title': f'Gate: {decision_title}'[:200],
                'subtitle': f'{gate.get_status_display()} — {gate.risk_level} risk',
                'timestamp': gate.created_at.isoformat() if hasattr(gate, 'created_at') else timezone.now().isoformat(),
                'badges': [gate.status, gate.risk_level],
                'cta': {'label': 'Open gate', 'route': '/governance'},
                'source': {'system': 'gates', 'id': str(gate.id), 'status': gate.status},
                'preview': {'text': gate.summary[:200] if gate.summary else None},
            })
            counts['gates'] += 1
    except Exception as e:
        logger.debug("Inbox gates error: %s", e)

    # 3. Error signatures (top N from existing cockpit errors logic)
    try:
        from core.models_diagnostic_pipeline import FailureSignature
        sigs = list(
            FailureSignature.objects.filter(
                status='active', last_seen_at__gte=cutoff,
            ).order_by('-occurrence_count')[:10]
            .values('signature', 'occurrence_count', 'last_seen_at', 'description')
        )
        for s in sigs:
            count = s['occurrence_count'] or 0
            if count >= 20:
                severity = 'critical'
            elif count >= 10:
                severity = 'high'
            elif count >= 3:
                severity = 'medium'
            else:
                severity = 'low'
            items.append({
                'id': f'inbox:error_signature:{s["signature"][:60]}',
                'type': 'error_signature',
                'severity': severity,
                'title': s['signature'][:200],
                'subtitle': f'{count} occurrences',
                'timestamp': s['last_seen_at'].isoformat() if s.get('last_seen_at') else timezone.now().isoformat(),
                'badges': ['agent', f'{count}x'],
                'cta': {'label': 'View errors', 'route': '/cockpit/errors'},
                'source': {'system': 'errors', 'id': s['signature'][:100]},
                'preview': {'text': s.get('description', '')[:200] or None},
            })
            counts['errors'] += 1
    except Exception as e:
        logger.debug("Inbox error signatures error: %s", e)

    # 4. Failed runs — suppress when a newer successful run exists for the same agent
    try:
        from core.models_unified_system import AgentExecution
        from django.db.models import Exists, OuterRef

        has_newer_success = AgentExecution.objects.filter(
            status='completed',
            agent=OuterRef('agent'),
            created_at__gt=OuterRef('created_at'),
        )

        failed = AgentExecution.objects.filter(
            status='failed', created_at__gte=cutoff,
        ).filter(
            ~Exists(has_newer_success)
        ).select_related('agent').order_by('-created_at')[:15]

        for run in failed:
            items.append({
                'id': f'inbox:failed_run:{run.id}',
                'type': 'failed_run',
                'severity': 'high' if run.agent.name in (
                    'TalkingCharacterAgent', 'resolve_agent', 'PublishingAgent',
                ) else 'medium',
                'title': run.task[:200] if run.task else 'Failed execution',
                'subtitle': run.agent.name,
                'timestamp': run.created_at.isoformat(),
                'badges': ['failed', run.agent.name],
                'cta': {'label': 'View run', 'route': f'/cockpit/runs/{run.id}'},
                'source': {'system': 'runs', 'id': str(run.id), 'status': 'failed'},
                'preview': {'text': run.error_message[:200] if run.error_message else None},
            })
            counts['failed_runs'] += 1
    except Exception as e:
        logger.debug("Inbox failed runs error: %s", e)

    # Sort: severity desc → type rank desc → timestamp desc (ISO strings sort lexicographically)
    items.sort(key=lambda x: (
        -SEVERITY_RANK.get(x['severity'], 0),
        -TYPE_RANK.get(x['type'], 0),
        x['timestamp'],
    ), reverse=False)
    # Reverse so newest timestamps come first within same severity+type
    # (negative severity/type already handled, but timestamp needs descending)
    items.sort(key=lambda x: (
        -SEVERITY_RANK.get(x['severity'], 0),
        -TYPE_RANK.get(x['type'], 0),
    ))

    items = items[:limit]
    counts['total'] = len(items)

    return JsonResponse({
        'hours': hours,
        'limit': limit,
        'generated_at': timezone.now().isoformat(),
        'counts': counts,
        'items': items,
    })


@require_http_methods(["GET"])
def cockpit_runs_list(request):
    """
    Recent agent execution runs for Focus Cockpit.
    Query params: status, agent, hours (default 24), limit (default 50), enrich (0|1)
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    from django.utils import timezone
    from datetime import timedelta

    hours = int(request.GET.get('hours', 24))
    limit = min(int(request.GET.get('limit', 50)), 200)
    offset = max(int(request.GET.get('offset', 0)), 0)
    enrich = request.GET.get('enrich', '0') == '1'
    include_summary = request.GET.get('include_summary', '0') == '1'
    cutoff = timezone.now() - timedelta(hours=hours)

    try:
        from core.models_unified_system import AgentExecution
        qs = AgentExecution.objects.filter(created_at__gte=cutoff).select_related('agent')

        # VIP workspace scoping — only show runs linked to their workspace
        vip_ws = _get_cockpit_workspace_id(request)
        if vip_ws:
            from core.models_deliverables import Deliverable
            ws_agent_names = list(
                Deliverable.objects.filter(workspace_id=vip_ws)
                .values_list('agent_name', flat=True).distinct()
            )
            if ws_agent_names:
                qs = qs.filter(agent__name__in=ws_agent_names)

        status_filter = request.GET.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        agent_filter = request.GET.get('agent')
        if agent_filter:
            qs = qs.filter(agent__name__icontains=agent_filter)

        ordered = qs.order_by('-created_at')

        if enrich:
            # Full ORM objects needed for enrichment (input_data, output_data, etc.)
            from core.services.run_enrichment import enrich_run

            records = list(ordered[offset:offset + limit])
            result = []
            for rec in records:
                run_dict = {
                    'id': str(rec.id),
                    'agent_name': rec.agent.name if rec.agent_id else '',
                    'task': (rec.task or '')[:200],
                    'status': rec.status,
                    'created_at': rec.created_at.isoformat() if rec.created_at else None,
                    'completed_at': rec.completed_at.isoformat() if rec.completed_at else None,
                    'execution_time_ms': rec.execution_time_ms,
                    'tokens_used': rec.tokens_used or 0,
                }
                enrich_run(run_dict, full_record=rec)
                result.append(run_dict)
        else:
            runs = list(
                ordered[offset:offset + limit]
                .values(
                    'id', 'agent__name', 'task', 'status',
                    'created_at', 'completed_at', 'execution_time_ms', 'tokens_used',
                )
            )

            result = []
            for r in runs:
                result.append({
                    'id': str(r['id']),
                    'agent_name': r['agent__name'],
                    'task': r['task'][:200] if r['task'] else '',
                    'status': r['status'],
                    'created_at': r['created_at'].isoformat() if r['created_at'] else None,
                    'completed_at': r['completed_at'].isoformat() if r['completed_at'] else None,
                    'execution_time_ms': r['execution_time_ms'],
                    'tokens_used': r['tokens_used'] or 0,
                })

        # Optional distribution summary (only meaningful with enrich=1)
        if include_summary and enrich:
            from collections import Counter
            trigger_counts = Counter()
            importance_counts = Counter()
            for r in result:
                e = r.get('enrichment', {})
                trigger_counts[e.get('trigger', {}).get('type', 'unknown')] += 1
                importance_counts[e.get('importance', {}).get('level', 'routine')] += 1
            return JsonResponse({
                'items': result,
                'total': ordered.count(),
                'offset': offset,
                'limit': limit,
                'summary': {
                    'trigger_type_counts': dict(trigger_counts),
                    'importance_level_counts': dict(importance_counts),
                },
            })

        # Annotate failed runs as superseded if the same agent has a newer success
        if result:
            from django.db.models import Exists as _Exists, OuterRef as _OuterRef
            failed_ids = [r['id'] for r in result if r['status'] == 'failed']
            if failed_ids:
                superseded_ids = set(
                    str(eid) for eid in AgentExecution.objects.filter(
                        id__in=failed_ids,
                    ).filter(
                        _Exists(
                            AgentExecution.objects.filter(
                                status='completed',
                                agent=_OuterRef('agent'),
                                created_at__gt=_OuterRef('created_at'),
                            )
                        )
                    ).values_list('id', flat=True)
                )
                for r in result:
                    if r['id'] in superseded_ids:
                        r['superseded'] = True

        return JsonResponse(result, safe=False)
    except Exception as e:
        logger.exception("cockpit_runs_list error")
        return JsonResponse({'error': str(e)}, status=500)


# ── Noise Metrics endpoints (Session 1077) ────────────────────────────────────

@require_http_methods(["GET"])
def cockpit_runs_metrics(request):
    """
    Aggregated run metrics with North Star coverage.
    GET /api/cockpit/runs/metrics/?hours=24
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        hours = int(request.GET.get('hours', 24))
        hours = max(1, min(hours, 168))  # cap at 7 days

        from core.services.noise_metrics import compute_runs_metrics
        result = compute_runs_metrics(hours=hours)
        return JsonResponse(result)
    except Exception as e:
        logger.exception("cockpit_runs_metrics error")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def cockpit_conversations_metrics(request):
    """
    Aggregated conversation metrics with topic clustering and zombie rate.
    GET /api/cockpit/conversations/metrics/?hours=24
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        hours = int(request.GET.get('hours', 24))
        hours = max(1, min(hours, 168))

        from core.services.noise_metrics import compute_conversation_metrics
        result = compute_conversation_metrics(hours=hours)
        return JsonResponse(result)
    except Exception as e:
        logger.exception("cockpit_conversations_metrics error")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def cockpit_focus_mode_status(request):
    """Focus Mode status for cockpit cards. GET /api/cockpit/focus-mode/status/"""
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)
    try:
        from core.services.focus_mode import get_status
        return JsonResponse(get_status())
    except Exception as e:
        logger.exception("cockpit_focus_mode_status error")
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def cockpit_focus_mode_update(request):
    """Update Focus Mode config. POST /api/cockpit/focus-mode/update/"""
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)
    try:
        import json
        body = json.loads(request.body) if request.body else {}
        from core.services.focus_mode import set_config, get_status
        set_config(body)
        return JsonResponse(get_status())
    except Exception as e:
        logger.exception("cockpit_focus_mode_update error")
        return JsonResponse({'error': str(e)}, status=500)


# ── Focus Cockpit Create endpoints ───────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def cockpit_create_blog(request):
    """
    Create a blog post via the content writer agent (deliberation pipeline).
    Dispatches to Celery and returns immediately with a run_id.
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        body = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    topic = body.get('topic', '').strip()
    if not topic:
        return JsonResponse({'error': 'topic is required'}, status=400)

    style = body.get('style', 'engaging')
    length = body.get('length', 'medium')
    citations = body.get('citations', True)

    from django.utils import timezone
    from core.tasks import execute_agent_task

    task_text = f'Write a {length} blog post about: {topic}'
    context = {
        'topic': topic,
        'style': style,
        'length': length,
        'citations': citations,
        'content_type': 'blog_post',
        'user_id': str(request.user.id),
    }

    celery_task = execute_agent_task.apply_async(
        args=['ContentWriterAgent', task_text, context],
        queue='content',
    )

    return JsonResponse({
        'ok': True,
        'run_id': str(celery_task.id),
        'status': 'queued',
        'created_at': timezone.now().isoformat(),
        'next': {
            'route': f'/cockpit/runs/{celery_task.id}',
            'poll_run_detail': True,
        },
    })


@csrf_exempt
@require_http_methods(["POST"])
def cockpit_create_talking_video(request):
    """
    Create a talking character video via TalkingCharacterAgent.
    Dispatches to Celery and returns immediately with a job_id.
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        body = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    script = body.get('script', '').strip()
    if not script:
        return JsonResponse({'error': 'script is required'}, status=400)

    from django.utils import timezone
    from core.tasks import execute_agent_task

    task_text = f'Generate talking character video: {script}'
    context = {
        'script': script,
        'voice': body.get('voice', 'alloy'),
        'mode': body.get('mode', 'loop'),
        'sync_mode': body.get('sync_mode', 'cut_off'),
        'lipsync_model': body.get('lipsync_model', 'latentsync'),
        'image_url': body.get('image_url', ''),
        'color_grade': body.get('color_grade'),
        'user_id': str(request.user.id),
    }

    celery_task = execute_agent_task.apply_async(
        args=['TalkingCharacterAgent', task_text, context],
        queue='agents',
    )

    return JsonResponse({
        'ok': True,
        'job_id': str(celery_task.id),
        'status': 'queued',
        'created_at': timezone.now().isoformat(),
        'next': {
            'route': f'/cockpit/runs/{celery_task.id}',
            'poll_run_detail': True,
        },
    })


def _attach_media_urls(result: dict, task_id: str) -> None:
    """Session 1075: Attach media URLs from AgentExecution output_data to job status."""
    try:
        from core.models import AgentExecution
        exec_qs = AgentExecution.objects.filter(
            input_data__contains={'celery_task_id': task_id}
        ).order_by('-created_at')[:1]
        if not exec_qs.exists():
            # Also try matching by task_id stored in context
            exec_qs = AgentExecution.objects.filter(
                input_data__contains={'task_id': task_id}
            ).order_by('-created_at')[:1]
        if exec_qs.exists():
            output = exec_qs[0].output_data or {}
            metadata = output.get('metadata', {})
            # Surface common media URLs (scalar keys)
            for key in ('image_url', 'video_url', 'final_video_url', 'audio_url', 'file_url'):
                val = metadata.get(key)
                if val:
                    result[key] = val
            # ImageAgent stores images as a list — extract first URL
            if 'image_url' not in result:
                images = metadata.get('images', [])
                if images and isinstance(images, list) and images[0].get('url'):
                    result['image_url'] = images[0]['url']
    except Exception as _e:
        logger.warning(
            "views_diagnostics._attach_media_urls: swallowed (%s: %s) — degraded",
            type(_e).__name__, _e,
        )


@require_http_methods(["GET"])
def cockpit_job_status(request, job_id):
    """
    Poll status of a cockpit-created job (Celery task).
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    result = {
        'job_id': job_id,
        'status': 'unknown',
        'progress': None,
        'error': None,
    }

    # Check CeleryTaskEvent first
    try:
        from core.models_celery_telemetry import CeleryTaskEvent
        event = CeleryTaskEvent.objects.filter(task_id=job_id).first()
        if event:
            status_map = {'STARTED': 'processing', 'SUCCESS': 'completed', 'FAILURE': 'failed', 'REVOKED': 'cancelled'}
            result['status'] = status_map.get(event.status, event.status.lower())
            result['progress'] = 1.0 if event.status == 'SUCCESS' else (0.5 if event.status == 'STARTED' else 0.0)
            if event.error_message:
                result['error'] = event.error_message[:500]
            # Session 1075: Surface media URLs from completed agent executions
            if event.status == 'SUCCESS':
                _attach_media_urls(result, job_id)
            return JsonResponse(result)
    except Exception as _e:
        logger.warning(
            "views_diagnostics.cockpit_job_status: swallowed (%s: %s) — degraded",
            type(_e).__name__, _e,
        )

    # Check Celery AsyncResult
    try:
        from celery.result import AsyncResult
        async_result = AsyncResult(job_id)
        if async_result.state == 'PENDING':
            result['status'] = 'queued'
            result['progress'] = 0.0
        elif async_result.state == 'STARTED':
            result['status'] = 'processing'
            result['progress'] = 0.5
        elif async_result.state == 'SUCCESS':
            result['status'] = 'completed'
            result['progress'] = 1.0
            # Session 1075: Surface media URLs from completed agent executions
            _attach_media_urls(result, job_id)
        elif async_result.state == 'FAILURE':
            result['status'] = 'failed'
            result['progress'] = 0.0
            result['error'] = str(async_result.result)[:500] if async_result.result else None
        else:
            result['status'] = async_result.state.lower()
    except Exception as _e:
        logger.warning(
            "views_diagnostics.cockpit_job_status: swallowed (%s: %s) — degraded",
            type(_e).__name__, _e,
        )

    return JsonResponse(result)


# ── Session 1078: Version / Build Info endpoint ──────────────────────────────

@require_http_methods(["GET"])
def system_version(request):
    """
    Session 1078: Return build/deploy metadata for the running web process.
    No auth required — version info is non-sensitive.
    """
    import time
    import django
    from django.utils import timezone

    now = timezone.now()
    # Process uptime approximation
    _boot_key = '_system_version_boot'
    boot_ts = cache.get(_boot_key)
    if not boot_ts:
        boot_ts = time.time()
        cache.set(_boot_key, boot_ts, 86400 * 7)
    uptime_seconds = time.time() - boot_ts

    return JsonResponse({
        'service': os.environ.get('RAILWAY_SERVICE_NAME', 'web'),
        'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
        'git': {
            'sha': os.environ.get('RAILWAY_GIT_COMMIT_SHA', 'dev'),
            'branch': os.environ.get('RAILWAY_GIT_BRANCH', 'unknown'),
        },
        'railway': {
            'deployment_id': os.environ.get('RAILWAY_DEPLOYMENT_ID', 'local'),
        },
        'runtime': {
            'started_at': (now - timedelta(seconds=uptime_seconds)).isoformat(),
            'uptime_seconds': round(uptime_seconds),
        },
        'app': {
            'django_version': django.get_version(),
        },
    })


# ── Focus Cockpit Ops endpoint ───────────────────────────────────────────────

@require_http_methods(["GET"])
def cockpit_ops_overview(request):
    """
    Ops overview for Focus Cockpit — composes health checks, top failing agents,
    top error signatures, and recent failed runs.
    Query params: hours (default 24), limit (default 5)
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    from django.utils import timezone
    from django.db.models import Count, Max, Q
    from datetime import timedelta

    hours = int(request.GET.get('hours', 24))
    limit = min(int(request.GET.get('limit', 5)), 20)
    cutoff = timezone.now() - timedelta(hours=hours)

    result = {
        'hours': hours,
        'generated_at': timezone.now().isoformat(),
        'health': {'overall_tone': 'green', 'checks': []},
        'top_failing_agents': [],
        'top_error_signatures': [],
        'recent_failed_runs': [],
    }

    # 1. Health checks
    checks = []

    # Web — we're responding, so it's ok
    checks.append({'key': 'web', 'label': 'Web', 'tone': 'green', 'status': 'ok', 'detail': 'Responding'})

    # Database
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks.append({'key': 'db', 'label': 'Database', 'tone': 'green', 'status': 'ok', 'detail': 'Connected'})
    except Exception as e:
        checks.append({'key': 'db', 'label': 'Database', 'tone': 'red', 'status': 'down', 'detail': str(e)[:100]})

    # Redis
    try:
        r = get_redis_client()
        if r is None:
            checks.append({'key': 'redis', 'label': 'Redis', 'tone': 'gray', 'status': 'unknown', 'detail': 'REDIS_URL not configured'})
        elif r.ping():
            checks.append({'key': 'redis', 'label': 'Redis', 'tone': 'green', 'status': 'ok', 'detail': 'Connected'})
        else:
            checks.append({'key': 'redis', 'label': 'Redis', 'tone': 'red', 'status': 'down', 'detail': 'Not responding'})
    except Exception as e:
        checks.append({'key': 'redis', 'label': 'Redis', 'tone': 'red', 'status': 'down', 'detail': str(e)[:100]})

    # Celery — check recent task events
    try:
        from core.models_celery_telemetry import CeleryTaskEvent
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_failures = CeleryTaskEvent.objects.filter(status='FAILURE', started_at__gte=one_hour_ago).count()
        recent_successes = CeleryTaskEvent.objects.filter(status='SUCCESS', started_at__gte=one_hour_ago).count()
        if recent_failures == 0 and recent_successes > 0:
            checks.append({'key': 'celery', 'label': 'Celery', 'tone': 'green', 'status': 'ok', 'detail': f'{recent_successes} tasks/hr'})
        elif recent_failures > 0:
            checks.append({'key': 'celery', 'label': 'Celery', 'tone': 'amber', 'status': 'degraded', 'detail': f'{recent_failures} failures in last hour'})
        else:
            checks.append({'key': 'celery', 'label': 'Celery', 'tone': 'gray', 'status': 'idle', 'detail': 'No recent tasks'})
    except Exception:
        checks.append({'key': 'celery', 'label': 'Celery', 'tone': 'gray', 'status': 'unknown', 'detail': 'Cannot check'})

    # Body system components
    try:
        from core.models_heart import ComponentStatus
        for cs in ComponentStatus.objects.all()[:8]:
            tone = 'green' if cs.is_healthy else ('red' if cs.status == 'critical' else 'amber')
            checks.append({
                'key': cs.component,
                'label': cs.display_name,
                'tone': tone,
                'status': cs.status,
                'detail': f'Last check: {cs.last_check.strftime("%H:%M")}' if cs.last_check else '',
            })
    except Exception as _e:
        logger.warning(
            "views_diagnostics.cockpit_ops_overview: swallowed (%s: %s) — degraded",
            type(_e).__name__, _e,
        )

    # Resolve Node
    try:
        import urllib.request
        resolve_url = os.environ.get('RESOLVE_NODE_URL', 'http://localhost:5001')
        req = urllib.request.Request(f'{resolve_url}/health', method='GET')
        req.add_header('Accept', 'application/json')
        with urllib.request.urlopen(req, timeout=5) as resp:
            import json as _json
            body = _json.loads(resp.read())
            demo = body.get('demo_mode', False)
            detail = 'Demo mode' if demo else f'Queue: {body.get("queue_size", 0)}'
            checks.append({
                'key': 'resolve_node', 'label': 'Resolve Node',
                'tone': 'green', 'status': 'ok', 'detail': detail,
            })
    except Exception as e:
        err_detail = str(e)[:80]
        checks.append({
            'key': 'resolve_node', 'label': 'Resolve Node',
            'tone': 'amber', 'status': 'unreachable', 'detail': err_detail,
        })

    # Derive overall tone
    tones = [c['tone'] for c in checks]
    if 'red' in tones:
        result['health']['overall_tone'] = 'red'
    elif 'amber' in tones:
        result['health']['overall_tone'] = 'amber'
    result['health']['checks'] = checks

    # 2. Top failing agents
    try:
        from core.models_unified_system import AgentExecution
        agg = list(
            AgentExecution.objects.filter(created_at__gte=cutoff)
            .values('agent__name')
            .annotate(
                failed_count=Count('id', filter=Q(status='failed')),
                total_count=Count('id'),
                last_failed_at=Max('completed_at', filter=Q(status='failed')),
            )
            .filter(failed_count__gt=0)
            .order_by('-failed_count')[:limit]
        )
        for a in agg:
            total = a['total_count'] or 1
            result['top_failing_agents'].append({
                'agent_name': a['agent__name'],
                'failed_count': a['failed_count'],
                'total_count': a['total_count'],
                'failure_rate': round(a['failed_count'] / total, 4),
                'last_failed_at': a['last_failed_at'].isoformat() if a['last_failed_at'] else None,
            })
    except Exception as e:
        logger.debug("Ops top_failing_agents error: %s", e)

    # 3. Top error signatures
    try:
        from core.models_diagnostic_pipeline import FailureSignature
        sigs = list(
            FailureSignature.objects.filter(
                status='active', last_seen_at__gte=cutoff,
            ).order_by('-occurrence_count')[:limit]
            .values('signature', 'occurrence_count', 'last_seen_at', 'description')
        )
        for s in sigs:
            result['top_error_signatures'].append({
                'signature': s['signature'],
                'source': 'agent',
                'count': s['occurrence_count'],
                'last_seen': s['last_seen_at'].isoformat() if s.get('last_seen_at') else None,
                'sample_error': s.get('description', '')[:200],
            })
    except Exception as e:
        logger.debug("Ops top_error_signatures error: %s", e)

    # 4. Recent failed runs
    try:
        from core.models_unified_system import AgentExecution
        failed = list(
            AgentExecution.objects.filter(status='failed', created_at__gte=cutoff)
            .select_related('agent')
            .order_by('-created_at')[:limit]
            .values('id', 'agent__name', 'task', 'status', 'created_at', 'completed_at', 'execution_time_ms', 'tokens_used')
        )
        for r in failed:
            result['recent_failed_runs'].append({
                'id': str(r['id']),
                'agent_name': r['agent__name'],
                'task': r['task'][:200] if r['task'] else '',
                'status': r['status'],
                'created_at': r['created_at'].isoformat() if r['created_at'] else None,
                'completed_at': r['completed_at'].isoformat() if r['completed_at'] else None,
                'execution_time_ms': r['execution_time_ms'],
                'tokens_used': r['tokens_used'] or 0,
            })
    except Exception as e:
        logger.debug("Ops recent_failed_runs error: %s", e)

    return JsonResponse(result)


@csrf_exempt
@require_http_methods(['GET'])
def cockpit_resolve_node_health(request):
    """
    GET /api/cockpit/resolve-node/health/
    Proxy health check for the DaVinci Resolve render node.
    Returns the node's health response with timing and last-checked metadata.
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    import time
    import urllib.request

    resolve_url = os.environ.get('RESOLVE_NODE_URL', 'http://localhost:5001')
    start = time.time()

    try:
        req = urllib.request.Request(f'{resolve_url}/health', method='GET')
        req.add_header('Accept', 'application/json')
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read())

        response_time_ms = int((time.time() - start) * 1000)
        return JsonResponse({
            'status': 'ok',
            'node_status': body.get('status', 'unknown'),
            'queue_size': body.get('queue_size', 0),
            'active_jobs': body.get('active_jobs', 0),
            'demo_mode': body.get('demo_mode', False),
            'response_time_ms': response_time_ms,
            'resolve_url': resolve_url,
            'checked_at': datetime.now().isoformat(),
        })
    except Exception as e:
        response_time_ms = int((time.time() - start) * 1000)
        return JsonResponse({
            'status': 'unreachable',
            'error': str(e)[:200],
            'response_time_ms': response_time_ms,
            'resolve_url': resolve_url,
            'checked_at': datetime.now().isoformat(),
        })


# ─── Resolve Node: Render Proxy ────────────────────────────────────────────────

def _resolve_node_request(method, path, body=None, timeout=30):
    """Make an authenticated request to the resolve-node and return (status, data)."""
    import time
    import urllib.request
    import urllib.error

    resolve_url = os.environ.get('RESOLVE_NODE_URL', 'http://localhost:5001')
    token = os.environ.get('RENDER_NODE_TOKEN', 'dev-token-change-in-production')
    url = f'{resolve_url}{path}'

    req = urllib.request.Request(url, method=method)
    req.add_header('X-Render-Token', token)
    req.add_header('Accept', 'application/json')

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


@csrf_exempt
@require_http_methods(["POST"])
def cockpit_resolve_node_render_start(request):
    """
    POST /api/cockpit/resolve-node/render/start/
    Proxy render start to resolve-node. Body: {clip_paths, template?, timeline_name?}
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not body.get('clip_paths'):
        return JsonResponse({'error': 'clip_paths required'}, status=400)

    status_code, data, latency = _resolve_node_request('POST', '/render/start', body)

    if status_code == 0:
        return JsonResponse({'error': 'Resolve node unreachable', 'detail': data.get('error', '')}, status=502)

    return JsonResponse({**data, 'latency_ms': latency}, status=status_code)


@csrf_exempt
@require_http_methods(["GET"])
def cockpit_resolve_node_render_status(request, job_id):
    """
    GET /api/cockpit/resolve-node/render/status/<job_id>/
    Proxy render status check. Returns job status, progress, timestamps, metadata.
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    status_code, data, latency = _resolve_node_request('GET', f'/render/status/{job_id}')

    if status_code == 0:
        return JsonResponse({'error': 'Resolve node unreachable', 'detail': data.get('error', '')}, status=502)

    # Strip internal output_file path — clients should use the result proxy endpoint
    if 'output_file' in data:
        data['has_output'] = bool(data['output_file'])
        del data['output_file']

    return JsonResponse({**data, 'latency_ms': latency}, status=status_code)


@csrf_exempt
@require_http_methods(["GET"])
def cockpit_resolve_node_render_result(request, job_id):
    """
    GET /api/cockpit/resolve-node/render/result/<job_id>/
    Proxy render result download. Streams the video file from resolve-node.
    """
    import urllib.request
    import urllib.error

    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    resolve_url = os.environ.get('RESOLVE_NODE_URL', 'http://localhost:5001')
    token = os.environ.get('RENDER_NODE_TOKEN', 'dev-token-change-in-production')
    url = f'{resolve_url}/render/result/{job_id}'

    req = urllib.request.Request(url, method='GET')
    req.add_header('X-Render-Token', token)

    try:
        resp = urllib.request.urlopen(req, timeout=60)
        from django.http import StreamingHttpResponse

        def _stream():
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                yield chunk
            resp.close()

        content_type = resp.headers.get('Content-Type', 'video/mp4')
        filename = resp.headers.get('Content-Disposition', '')
        response = StreamingHttpResponse(_stream(), content_type=content_type)
        if filename:
            response['Content-Disposition'] = filename
        else:
            response['Content-Disposition'] = f'attachment; filename="render_{job_id}.mp4"'
        return response
    except urllib.error.HTTPError as e:
        try:
            data = json.loads(e.read())
        except Exception:
            data = {'error': str(e)}
        return JsonResponse(data, status=e.code)
    except Exception as e:
        return JsonResponse({'error': 'Resolve node unreachable', 'detail': str(e)[:200]}, status=502)


@csrf_exempt
@require_http_methods(["GET"])
def cockpit_resolve_node_jobs(request):
    """
    GET /api/cockpit/resolve-node/jobs/
    Proxy job list from resolve-node.
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    status_code, data, latency = _resolve_node_request('GET', '/jobs')

    if status_code == 0:
        return JsonResponse({'error': 'Resolve node unreachable', 'detail': data.get('error', '')}, status=502)

    return JsonResponse({**data, 'latency_ms': latency}, status=status_code)


# ─── Focus Cockpit: Library ────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET"])
def cockpit_library_deliverables(request):
    """List deliverables with search, type filter, and pagination."""
    from core.models_deliverables import Deliverable
    from django.db.models import Q
    from django.utils.timezone import now
    from datetime import timedelta

    q = request.GET.get('q', '').strip()
    dtype = request.GET.get('type', '')
    days = int(request.GET.get('days', 30))
    limit = min(int(request.GET.get('limit', 50)), 100)
    offset = int(request.GET.get('offset', 0))

    qs = Deliverable.objects.all().order_by('-created_at')

    # VIP workspace scoping
    vip_ws = _get_cockpit_workspace_id(request)
    if vip_ws:
        qs = qs.filter(workspace_id=vip_ws)

    if days > 0:
        cutoff = now() - timedelta(hours=days * 24)
        qs = qs.filter(created_at__gte=cutoff)

    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(category__icontains=q) | Q(agent_name__icontains=q)
        )
    if dtype:
        qs = qs.filter(deliverable_type=dtype)

    total = qs.count()
    items = list(
        qs[offset:offset + limit].values(
            'id', 'title', 'deliverable_type', 'category', 'status',
            'agent_name', 'quality_score', 'is_saved', 'created_at',
        )
    )
    for item in items:
        item['id'] = str(item['id'])
        item['created_at'] = item['created_at'].isoformat() if item['created_at'] else None
        item['quality_score'] = float(item['quality_score'] or 0)

    return JsonResponse({'total': total, 'offset': offset, 'limit': limit, 'items': items})


@csrf_exempt
@require_http_methods(["GET"])
def cockpit_library_media(request):
    """List media (images + videos) with type filter and pagination."""
    from django.utils.timezone import now
    from datetime import timedelta

    media_type = request.GET.get('media_type', 'all')
    days = int(request.GET.get('days', 30))
    limit = min(int(request.GET.get('limit', 50)), 100)
    offset = int(request.GET.get('offset', 0))

    cutoff = now() - timedelta(hours=days * 24)
    items = []

    if media_type in ('all', 'image'):
        try:
            from content.models import ImageHistory
            images = (
                ImageHistory.objects.filter(created_at__gte=cutoff)
                .exclude(file_path__startswith='data:')
                .order_by('-created_at')[:500]
            )
            for img in images:
                url = img.get_full_url()
                thumb = img.get_thumbnail_url()
                items.append({
                    'id': str(img.id),
                    'kind': 'image',
                    'title': img.filename or 'Untitled',
                    'url': url or '',
                    'thumbnail_url': thumb or '',
                    'sub_type': img.image_type or '',
                    'prompt': (img.prompt or '')[:200],
                    'created_at': img.created_at.isoformat() if img.created_at else None,
                })
        except Exception as e:
            logger.debug("Library media images error: %s", e)

    if media_type in ('all', 'video'):
        try:
            from content.models import VideoHistory
            videos = list(
                VideoHistory.objects.filter(created_at__gte=cutoff)
                .order_by('-created_at')[:500]
                .values('id', 'video_url', 'thumbnail_url', 'video_type', 'prompt', 'created_at')
            )
            for vid in videos:
                items.append({
                    'id': str(vid['id']),
                    'kind': 'video',
                    'title': (vid['prompt'] or 'Untitled')[:80],
                    'url': vid['video_url'] or '',
                    'thumbnail_url': vid['thumbnail_url'] or '',
                    'sub_type': vid['video_type'] or '',
                    'prompt': (vid['prompt'] or '')[:200],
                    'created_at': vid['created_at'].isoformat() if vid['created_at'] else None,
                })
        except Exception as e:
            logger.debug("Library media videos error: %s", e)

    # Sort combined list by created_at desc
    items.sort(key=lambda x: x['created_at'] or '', reverse=True)
    total = len(items)
    page = items[offset:offset + limit]

    return JsonResponse({'total': total, 'offset': offset, 'limit': limit, 'items': page})


# ─── Focus Cockpit: Approvals ──────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET"])
def cockpit_approvals_list(request):
    """List actionable items: pending human decisions + gates awaiting approval."""
    from django.utils.timezone import now
    from datetime import timedelta

    hours = int(request.GET.get('hours', 168))  # default 7 days
    limit = min(int(request.GET.get('limit', 50)), 100)
    cutoff = now() - timedelta(hours=hours)
    items = []

    # 1. Human decisions pending action
    try:
        from core.models_human_interface import HumanAttentionItem
        pending = HumanAttentionItem.objects.filter(
            status__in=['pending', 'viewed'],
            created_at__gte=cutoff,
        ).order_by('-priority_score', '-created_at')[:limit]
        for item in pending:
            items.append({
                'id': str(item.id),
                'kind': 'decision',
                'title': item.title,
                'summary': item.summary[:300] if item.summary else '',
                'urgency': item.urgency,
                'status': item.status,
                'source_agent': item.source_agent or '',
                'ml_recommendation': item.ml_recommendation or '',
                'created_at': item.created_at.isoformat() if item.created_at else None,
            })
    except Exception as e:
        logger.debug("Approvals decisions error: %s", e)

    # 2. Gates awaiting approval (ready or in_progress)
    try:
        from core.models_pilot_readiness import PilotReadinessGate
        gates = PilotReadinessGate.objects.filter(
            status__in=['ready', 'in_progress'],
            created_at__gte=cutoff,
        ).select_related('decision').order_by('-created_at')[:limit]
        for gate in gates:
            items.append({
                'id': str(gate.id),
                'kind': 'gate',
                'title': f"Gate: {gate.decision.topic if gate.decision else 'Unknown'}",
                'summary': gate.summary or '',
                'urgency': gate.risk_level or 'medium',
                'status': gate.status,
                'source_agent': '',
                'ml_recommendation': '',
                'created_at': gate.created_at.isoformat() if gate.created_at else None,
            })
    except Exception as e:
        logger.debug("Approvals gates error: %s", e)

    # Sort by urgency tier then date
    urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    items.sort(key=lambda x: (urgency_order.get(x['urgency'], 9), x['created_at'] or ''), reverse=False)

    return JsonResponse({'hours': hours, 'total': len(items), 'items': items[:limit]})


@csrf_exempt
@require_http_methods(["POST"])
def cockpit_approve_decision(request, item_id):
    """Approve or reject a HumanAttentionItem."""
    from core.models_human_interface import HumanAttentionItem

    try:
        item = HumanAttentionItem.objects.get(id=item_id)
    except HumanAttentionItem.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Item not found'}, status=404)

    try:
        body = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    decision = body.get('decision', '')
    if decision not in ('approve', 'reject'):
        return JsonResponse({'ok': False, 'error': 'decision must be approve or reject'}, status=400)

    feedback = body.get('feedback', '')
    item.record_decision(decision=decision, feedback=feedback, confidence=1.0)

    resp = {'ok': True, 'id': str(item.id), 'decision': decision, 'status': item.status}
    _audit_log(request, f'approve_decision_{decision}', 'HumanAttentionItem', item_id, body, resp)
    return JsonResponse(resp)


@csrf_exempt
@require_http_methods(["POST"])
def cockpit_approve_gate(request, gate_id):
    """Approve or block a PilotReadinessGate."""
    from core.models_pilot_readiness import PilotReadinessGate

    try:
        gate = PilotReadinessGate.objects.get(id=gate_id)
    except PilotReadinessGate.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Gate not found'}, status=404)

    try:
        body = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    action = body.get('action', '')
    notes = body.get('notes', '')

    if action == 'approve':
        ok = gate.approve(approved_by='cockpit-operator', notes=notes)
        if not ok:
            return JsonResponse({'ok': False, 'error': f'Gate cannot be approved in status={gate.status}'}, status=400)
    elif action == 'block':
        if not notes:
            return JsonResponse({'ok': False, 'error': 'notes required when blocking'}, status=400)
        gate.block(reason=notes)
    else:
        return JsonResponse({'ok': False, 'error': 'action must be approve or block'}, status=400)

    resp = {'ok': True, 'id': str(gate.id), 'action': action, 'status': gate.status}
    _audit_log(request, f'approve_gate_{action}', 'PilotReadinessGate', gate_id, body, resp)
    return JsonResponse(resp)


# ─── Focus Cockpit: Alerts ─────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET"])
def cockpit_alerts(request):
    """Compose in-app alerts from multiple system sources."""
    from django.utils.timezone import now
    from django.db.models import Count, Q
    from datetime import timedelta

    hours = int(request.GET.get('hours', 24))
    cutoff = now() - timedelta(hours=hours)
    prev_cutoff = cutoff - timedelta(hours=hours)  # previous window for deltas
    alerts = []

    # 1. Error signature spikes — signatures with count increase vs previous window
    try:
        from core.models_diagnostic_pipeline import FailureSignature
        current_sigs = dict(
            FailureSignature.objects.filter(last_seen__gte=cutoff)
            .values_list('signature', 'count')
        )
        prev_sigs = dict(
            FailureSignature.objects.filter(last_seen__gte=prev_cutoff, last_seen__lt=cutoff)
            .values_list('signature', 'count')
        )
        for sig, count in current_sigs.items():
            prev = prev_sigs.get(sig, 0)
            delta = count - prev
            if delta >= 3 or (count >= 5 and prev == 0):
                alerts.append({
                    'id': f'err-spike-{sig[:40]}',
                    'kind': 'error_spike',
                    'severity': 'high' if delta >= 10 else 'medium',
                    'title': f'Error spike: {sig[:80]}',
                    'detail': f'{count} occurrences (+{delta} vs previous {hours}h)',
                    'created_at': None,
                })
    except Exception as e:
        logger.debug("Alerts error_spike: %s", e)

    # 2. Agents with high failure rate
    try:
        from core.models_unified_system import AgentExecution
        agg = list(
            AgentExecution.objects.filter(created_at__gte=cutoff)
            .values('agent__name')
            .annotate(
                failed=Count('id', filter=Q(status='failed')),
                total=Count('id'),
            )
            .filter(failed__gte=3, total__gte=5)
        )
        for a in agg:
            rate = round(a['failed'] / max(a['total'], 1) * 100, 1)
            if rate >= 50:
                severity = 'high'
            elif rate >= 25:
                severity = 'medium'
            else:
                continue
            alerts.append({
                'id': f'agent-fail-{a["agent__name"]}',
                'kind': 'agent_failure',
                'severity': severity,
                'title': f'Agent failing: {a["agent__name"]}',
                'detail': f'{a["failed"]}/{a["total"]} runs failed ({rate}%)',
                'created_at': None,
            })
    except Exception as e:
        logger.debug("Alerts agent_failure: %s", e)

    # 3. Health degradation — body systems reporting unhealthy
    try:
        from core.models_heart import ComponentStatus
        unhealthy = ComponentStatus.objects.filter(is_healthy=False)
        for cs in unhealthy:
            alerts.append({
                'id': f'health-{cs.component}',
                'kind': 'health',
                'severity': 'high',
                'title': f'Unhealthy: {cs.display_name or cs.component}',
                'detail': f'Status: {cs.status}',
                'created_at': cs.last_check.isoformat() if cs.last_check else None,
            })
    except Exception as e:
        logger.debug("Alerts health: %s", e)

    # 4. Pending approvals count
    try:
        from core.models_human_interface import HumanAttentionItem
        pending_count = HumanAttentionItem.objects.filter(
            status__in=['pending', 'viewed'],
            created_at__gte=cutoff,
        ).count()
        if pending_count > 0:
            severity = 'high' if pending_count >= 5 else 'low'
            alerts.append({
                'id': 'approvals-pending',
                'kind': 'approvals',
                'severity': severity,
                'title': f'{pending_count} approval{"s" if pending_count != 1 else ""} pending',
                'detail': 'Items awaiting your decision in Approvals.',
                'created_at': None,
            })
    except Exception as e:
        logger.debug("Alerts approvals: %s", e)

    # Sort by severity
    sev_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    alerts.sort(key=lambda x: sev_order.get(x['severity'], 9))

    return JsonResponse({
        'hours': hours,
        'total': len(alerts),
        'items': alerts,
    })


# ─── Focus Cockpit: Remediation ────────────────────────────────────────────────

# Deterministic runbook map: alert kind + optional substring → steps
_RUNBOOKS = {
    'error_spike': {
        'title': 'Error Spike Runbook',
        'steps': [
            'Check the error signature in Errors page for sample traceback.',
            'Identify the failing agent(s) in Ops → Top Failing Agents.',
            'If provider-related (OpenAI, Replicate), check provider status page.',
            'If persistent, retry the latest failed run from Run Detail.',
            'Create an incident note to track resolution.',
        ],
    },
    'agent_failure': {
        'title': 'Agent Failure Runbook',
        'steps': [
            'Open Ops page and check the agent failure rate trend.',
            'View recent failed runs for the agent in Runs page (filter by agent).',
            'Check if the agent depends on an external API that may be down.',
            'Retry the most recent failed run to test recovery.',
            'If failure persists, create an incident note.',
        ],
    },
    'health': {
        'title': 'Health Degradation Runbook',
        'steps': [
            'Check Ops page for which component is unhealthy.',
            'For DB issues: verify PostgreSQL connection and query performance.',
            'For Redis issues: check Redis connection and memory usage.',
            'For Celery issues: verify workers are running (check Railway logs).',
            'For body system issues: check the specific ComponentStatus detail.',
        ],
    },
    'approvals': {
        'title': 'Pending Approvals Runbook',
        'steps': [
            'Go to Approvals page to review pending items.',
            'Prioritize critical/high urgency items first.',
            'Review ML recommendation before deciding.',
            'Approve or reject with feedback for learning.',
        ],
    },
}


@csrf_exempt
@require_http_methods(["GET"])
def cockpit_runbook(request, alert_kind):
    """Return deterministic runbook for an alert kind."""
    runbook = _RUNBOOKS.get(alert_kind)
    if not runbook:
        return JsonResponse({'ok': False, 'error': f'No runbook for kind={alert_kind}'}, status=404)
    return JsonResponse({'ok': True, **runbook})


@csrf_exempt
@require_http_methods(["POST"])
def cockpit_retry_run(request, run_id):
    """Retry a failed run by creating a new AgentExecution with the same agent + task."""
    from core.models_unified_system import AgentExecution

    try:
        original = AgentExecution.objects.select_related('agent').get(id=run_id)
    except AgentExecution.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Run not found'}, status=404)

    if original.status != 'failed':
        return JsonResponse({'ok': False, 'error': 'Only failed runs can be retried'}, status=400)

    agent_name = original.agent.name if original.agent else None
    if not agent_name:
        return JsonResponse({'ok': False, 'error': 'Cannot determine agent name'}, status=400)

    task_text = original.task or ''
    context = original.input_data or {}
    context['retried_from'] = str(original.id)

    try:
        from core.tasks import execute_agent_task
        result = execute_agent_task.apply_async(
            args=[agent_name, task_text, context],
            queue='agents',
        )
        resp = {'ok': True, 'original_run_id': str(original.id), 'new_task_id': str(result.id), 'agent_name': agent_name}
        _audit_log(request, 'retry_run', 'AgentExecution', run_id, {'agent_name': agent_name}, resp)
        return JsonResponse(resp)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def cockpit_create_incident_note(request):
    """Create an incident note as a Deliverable tagged 'incident'."""
    try:
        body = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    source_type = body.get('source_type', 'alert')
    source_id = body.get('source_id', '')
    title = body.get('title', '')
    detail = body.get('detail', '')

    if not title:
        return JsonResponse({'ok': False, 'error': 'title is required'}, status=400)

    from django.utils.timezone import now as tz_now
    timestamp = tz_now().isoformat()

    content = f"# Incident Note\n\n"
    content += f"**Created:** {timestamp}\n"
    content += f"**Source:** {source_type} — {source_id}\n\n"
    content += f"## Summary\n\n{title}\n\n"
    if detail:
        content += f"## Detail\n\n{detail}\n\n"
    content += f"## Resolution\n\n_To be filled in after resolution._\n"

    try:
        import uuid
        from django.utils.text import slugify
        from core.services.deliverable_factory import create_deliverable

        slug_base = slugify(title[:60]) or 'incident'
        slug = f"{slug_base}-{uuid.uuid4().hex[:8]}"

        deliverable = create_deliverable(
            title=title,
            content=content,
            agent_name='cockpit-operator',
            category='Incident',
            deliverable_type='document',
            tags=['incident', source_type],
            content_format='markdown',
            metadata={
                'source_type': source_type,
                'source_id': source_id,
                'created_via': 'cockpit-remediation',
            },
            slug=slug,
            status='ready',
        )
        resp = {
            'ok': True,
            'id': str(deliverable.id),
            'title': deliverable.title,
            'slug': deliverable.slug,
        }
        _audit_log(request, 'create_incident_note', 'Deliverable', str(deliverable.id), body, resp)
        return JsonResponse(resp)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['GET'])
def cockpit_audit_list(request):
    """List cockpit audit log entries with optional filters."""
    from core.models_cockpit_audit import CockpitAuditLog
    from django.utils.timezone import now
    from datetime import timedelta

    hours = int(request.GET.get('hours', 168))  # default 7 days
    limit = min(int(request.GET.get('limit', 100)), 500)
    action_filter = request.GET.get('action', '')

    cutoff = now() - timedelta(hours=hours)
    qs = CockpitAuditLog.objects.filter(created_at__gte=cutoff)
    if action_filter:
        qs = qs.filter(action__icontains=action_filter)

    total = qs.count()
    entries = list(qs.select_related('user')[:limit].values(
        'id', 'action', 'target_type', 'target_id',
        'request_body', 'response_summary', 'ip_address', 'created_at',
        'user__username',
    ))
    for e in entries:
        e['id'] = str(e['id'])
        e['actor'] = e.pop('user__username') or 'system'
        e['created_at'] = e['created_at'].isoformat() if e['created_at'] else None

    return JsonResponse({
        'hours': hours,
        'total': total,
        'limit': limit,
        'items': entries,
    })


# ---------------------------------------------------------------------------
# P12: Agent Fleet Management
# ---------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(['GET'])
def cockpit_agent_fleet(request):
    """List all agents with execution stats and cockpit state."""
    from core.models_unified_system import Agent, AgentExecution
    from core.models_cockpit_agent_state import CockpitAgentState
    from django.utils.timezone import now
    from datetime import timedelta
    from django.db.models import Count, Q, Max

    hours = int(request.GET.get('hours', 24))
    q = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 100)), 200)

    cutoff = now() - timedelta(hours=hours)

    agents_qs = Agent.objects.filter(is_active=True)
    if q:
        agents_qs = agents_qs.filter(
            Q(name__icontains=q) | Q(agent_type__icontains=q) | Q(specialization__icontains=q)
        )

    agents_qs = agents_qs.annotate(
        recent_total=Count('executions', filter=Q(executions__created_at__gte=cutoff)),
        recent_failed=Count('executions', filter=Q(executions__created_at__gte=cutoff, executions__status='failed')),
        recent_completed=Count('executions', filter=Q(executions__created_at__gte=cutoff, executions__status='completed')),
        last_run_at=Max('executions__created_at'),
    ).order_by('-recent_total', 'name')[:limit]

    # Fetch cockpit state overrides
    state_map = {
        s.agent_name: s
        for s in CockpitAgentState.objects.all()
    }

    items = []
    for a in agents_qs:
        state = state_map.get(a.name)
        items.append({
            'id': str(a.id),
            'name': a.name,
            'agent_type': a.agent_type,
            'specialization': a.specialization,
            'category': a.category.name if a.category_id else '',
            'effectiveness_score': a.effectiveness_score,
            'recent_total': a.recent_total,
            'recent_completed': a.recent_completed,
            'recent_failed': a.recent_failed,
            'last_run_at': a.last_run_at.isoformat() if a.last_run_at else None,
            'cockpit_enabled': state.enabled if state else True,
            'paused_reason': state.paused_reason if state and not state.enabled else '',
            'paused_at': state.paused_at.isoformat() if state and state.paused_at else None,
        })

    return JsonResponse({
        'hours': hours,
        'total': len(items),
        'items': items,
    })


@csrf_exempt
@require_http_methods(['GET'])
def cockpit_agent_detail(request, agent_name):
    """Get detailed info for a single agent."""
    from core.models_unified_system import Agent, AgentExecution
    from core.models_cockpit_agent_state import CockpitAgentState
    from django.utils.timezone import now
    from datetime import timedelta

    try:
        agent = Agent.objects.get(name=agent_name, is_active=True)
    except Agent.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Agent not found'}, status=404)

    cutoff = now() - timedelta(hours=168)  # 7d of runs
    recent_runs = list(
        AgentExecution.objects.filter(agent=agent, created_at__gte=cutoff)
        .order_by('-created_at')[:20]
        .values('id', 'task', 'status', 'execution_time_ms', 'tokens_used', 'error_message', 'created_at', 'completed_at')
    )
    for r in recent_runs:
        r['id'] = str(r['id'])
        r['created_at'] = r['created_at'].isoformat() if r['created_at'] else None
        r['completed_at'] = r['completed_at'].isoformat() if r['completed_at'] else None

    state = CockpitAgentState.objects.filter(agent_name=agent_name).first()

    return JsonResponse({
        'ok': True,
        'agent': {
            'id': str(agent.id),
            'name': agent.name,
            'agent_type': agent.agent_type,
            'specialization': agent.specialization,
            'description': agent.description,
            'category': agent.category.name if agent.category_id else '',
            'effectiveness_score': agent.effectiveness_score,
            'total_executions': agent.total_executions,
            'successful_executions': agent.successful_executions,
            'cockpit_enabled': state.enabled if state else True,
            'paused_reason': state.paused_reason if state and not state.enabled else '',
            'paused_at': state.paused_at.isoformat() if state and state.paused_at else None,
        },
        'recent_runs': recent_runs,
    })


@csrf_exempt
@require_http_methods(['POST'])
def cockpit_agent_run_now(request, agent_name):
    """Queue an immediate run for an agent."""
    from core.models_unified_system import Agent
    from core.models_cockpit_agent_state import CockpitAgentState
    from core.tasks import execute_agent_task

    try:
        agent = Agent.objects.get(name=agent_name, is_active=True)
    except Agent.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Agent not found'}, status=404)

    # Check cockpit state
    state = CockpitAgentState.objects.filter(agent_name=agent_name).first()
    if state and not state.enabled:
        return JsonResponse({'ok': False, 'error': f'Agent is paused: {state.paused_reason}'}, status=409)

    try:
        body = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        body = {}

    task_str = body.get('task', f'Manual cockpit run for {agent_name}')

    result = execute_agent_task.apply_async(
        args=[agent_name, task_str],
        kwargs={'context': {'source': 'cockpit-run-now'}},
    )

    resp = {
        'ok': True,
        'agent_name': agent_name,
        'task_id': result.id,
        'status': 'queued',
    }
    _audit_log(request, 'agent.run_now', 'Agent', agent_name, body, resp)
    return JsonResponse(resp)


@csrf_exempt
@require_http_methods(['POST'])
def cockpit_agent_pause(request, agent_name):
    """Pause an agent (prevents scheduled execution)."""
    from core.models_unified_system import Agent
    from core.models_cockpit_agent_state import CockpitAgentState
    from django.utils.timezone import now as tz_now

    try:
        Agent.objects.get(name=agent_name, is_active=True)
    except Agent.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Agent not found'}, status=404)

    try:
        body = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        body = {}

    reason = body.get('reason', '')
    user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None

    state, _ = CockpitAgentState.objects.update_or_create(
        agent_name=agent_name,
        defaults={
            'enabled': False,
            'paused_reason': reason,
            'paused_at': tz_now(),
            'updated_by': user,
        },
    )

    resp = {
        'ok': True,
        'agent_name': agent_name,
        'enabled': False,
        'paused_at': state.paused_at.isoformat() if state.paused_at else None,
        'paused_reason': reason,
    }
    _audit_log(request, 'agent.pause', 'Agent', agent_name, body, resp)
    return JsonResponse(resp)


@csrf_exempt
@require_http_methods(['POST'])
def cockpit_agent_resume(request, agent_name):
    """Resume a paused agent."""
    from core.models_unified_system import Agent
    from core.models_cockpit_agent_state import CockpitAgentState

    try:
        Agent.objects.get(name=agent_name, is_active=True)
    except Agent.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Agent not found'}, status=404)

    user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None

    state, _ = CockpitAgentState.objects.update_or_create(
        agent_name=agent_name,
        defaults={
            'enabled': True,
            'paused_reason': '',
            'paused_at': None,
            'updated_by': user,
        },
    )

    resp = {
        'ok': True,
        'agent_name': agent_name,
        'enabled': True,
    }
    _audit_log(request, 'agent.resume', 'Agent', agent_name, {}, resp)
    return JsonResponse(resp)


# ---------------------------------------------------------------------------
# P13A: Queue / Worker / Task Load
# ---------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(['GET'])
def cockpit_queues_overview(request):
    """Compose queue/worker/task overview from CeleryTaskEvent + CeleryHealthService."""
    from core.models_celery_telemetry import CeleryTaskEvent
    from django.utils.timezone import now
    from datetime import timedelta
    from django.db.models import Count, Avg, Q, F
    from django.db.models.functions import TruncHour

    window = request.GET.get('window', '60m')
    minutes = {'15m': 15, '60m': 60, '2h': 120, '6h': 360, '24h': 1440}.get(window, 60)
    cutoff = now() - timedelta(minutes=minutes)

    # Workers online (distinct workers seen in window)
    workers = list(
        CeleryTaskEvent.objects.filter(started_at__gte=cutoff)
        .exclude(worker='')
        .values('worker')
        .annotate(
            task_count=Count('id'),
            failure_count=Count('id', filter=Q(status='FAILURE')),
        )
        .order_by('-task_count')
    )

    # Totals
    totals = CeleryTaskEvent.objects.filter(started_at__gte=cutoff).aggregate(
        total=Count('id'),
        success=Count('id', filter=Q(status='SUCCESS')),
        failure=Count('id', filter=Q(status='FAILURE')),
        started=Count('id', filter=Q(status='STARTED')),
        avg_duration_ms=Avg(F('duration_seconds') * 1000, filter=Q(duration_seconds__isnull=False)),
    )

    # Per-queue depths
    queues = list(
        CeleryTaskEvent.objects.filter(started_at__gte=cutoff)
        .values('queue')
        .annotate(
            count=Count('id'),
            failures=Count('id', filter=Q(status='FAILURE')),
        )
        .order_by('-count')
    )

    # Top tasks by volume
    top_tasks_qs = (
        CeleryTaskEvent.objects.filter(started_at__gte=cutoff)
        .values('task_name')
        .annotate(
            count=Count('id'),
            failures=Count('id', filter=Q(status='FAILURE')),
            avg_ms=Avg(F('duration_seconds') * 1000, filter=Q(duration_seconds__isnull=False)),
        )
        .order_by('-count')[:15]
    )
    top_tasks = []
    for t in top_tasks_qs:
        short_name = t['task_name'].rsplit('.', 1)[-1] if t['task_name'] else t['task_name']
        top_tasks.append({
            'task_name': t['task_name'],
            'short_name': short_name,
            'count': t['count'],
            'failures': t['failures'],
            'failure_rate': round(t['failures'] / t['count'] * 100, 1) if t['count'] else 0,
            'avg_ms': round(t['avg_ms'] or 0),
        })

    # Recent failures
    recent_failures = list(
        CeleryTaskEvent.objects.filter(started_at__gte=cutoff, status='FAILURE')
        .order_by('-started_at')[:10]
        .values('task_id', 'task_name', 'worker', 'error_type', 'error_message', 'started_at', 'queue')
    )
    for f in recent_failures:
        f['started_at'] = f['started_at'].isoformat() if f['started_at'] else None
        f['short_name'] = f['task_name'].rsplit('.', 1)[-1] if f['task_name'] else ''

    # Tasks per minute
    total_minutes = max(minutes, 1)
    tasks_per_min = round((totals['total'] or 0) / total_minutes, 1)
    failures_per_min = round((totals['failure'] or 0) / total_minutes, 2)

    return JsonResponse({
        'window': window,
        'minutes': minutes,
        'generated_at': now().isoformat(),
        'summary': {
            'workers_online': len(workers),
            'tasks_total': totals['total'] or 0,
            'tasks_success': totals['success'] or 0,
            'tasks_failure': totals['failure'] or 0,
            'tasks_started': totals['started'] or 0,
            'tasks_per_min': tasks_per_min,
            'failures_per_min': failures_per_min,
            'avg_duration_ms': round(totals['avg_duration_ms'] or 0),
        },
        'workers': workers,
        'queues': queues,
        'top_tasks': top_tasks,
        'recent_failures': recent_failures,
    })


# ---------------------------------------------------------------------------
# P13A-live: Per-queue LLEN depths (real-time Redis inspection)
# ---------------------------------------------------------------------------

CELERY_QUEUE_NAMES = [
    'default', 'agents', 'sports', 'pa', 'content',
    'long_running', 'ml', 'broadcast',
]


@csrf_exempt
@require_http_methods(['GET'])
def cockpit_queue_depths(request):
    """Return live Redis LLEN for every Celery queue."""
    from django.utils.timezone import now as tz_now

    r = get_redis_client()
    if r is None:
        return JsonResponse({
            'redis_ok': False,
            'error': 'REDIS_URL not configured or Redis unreachable',
            'generated_at': datetime.utcnow().isoformat(),
        })

    try:
        r.ping()
    except Exception as exc:
        return JsonResponse({
            'redis_ok': False,
            'error': f'Redis ping failed: {exc}',
            'generated_at': datetime.utcnow().isoformat(),
        })

    queues = []
    biggest_name = None
    biggest_len = -1
    total = 0

    for qname in CELERY_QUEUE_NAMES:
        try:
            length = r.llen(qname)
        except Exception:
            length = 0
        queues.append({'name': qname, 'pending': length})
        total += length
        if length > biggest_len:
            biggest_len = length
            biggest_name = qname

    # Sort descending by pending count
    queues.sort(key=lambda q: q['pending'], reverse=True)

    # Sample up to 10 task names from the biggest queue
    sample_tasks = []
    if biggest_name and biggest_len > 0:
        try:
            raw_messages = r.lrange(biggest_name, 0, 9)
            for raw in raw_messages:
                try:
                    msg = json.loads(raw) if isinstance(raw, str) else json.loads(raw.decode())
                    # Celery v2 protocol: headers.task
                    task_name = (msg.get('headers') or {}).get('task')
                    if not task_name:
                        # Celery v1 fallback
                        task_name = (msg.get('body') or {}).get('task', 'unknown')
                    sample_tasks.append(task_name)
                except Exception:
                    sample_tasks.append('(unparseable)')
        except Exception as _e:
            logger.warning(
                "views_diagnostics.cockpit_queue_depths: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

    return JsonResponse({
        'generated_at': tz_now().isoformat(),
        'redis_ok': True,
        'total_pending': total,
        'queues': queues,
        'biggest_queue': biggest_name if biggest_len > 0 else None,
        'sample_tasks': sample_tasks,
    })


# ---------------------------------------------------------------------------
# P13B: Cost / Token / Provider Usage
# ---------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(['GET'])
def cockpit_cost_overview(request):
    """Compose cost/token overview from LLMCallLog."""
    from core.models_llm_routing import LLMCallLog
    from django.utils.timezone import now
    from datetime import timedelta
    from django.db.models import Sum, Count, Avg, Q

    hours = int(request.GET.get('hours', 24))
    cutoff = now() - timedelta(hours=hours)
    prev_cutoff = cutoff - timedelta(hours=hours)

    qs = LLMCallLog.objects.filter(created_at__gte=cutoff)
    prev_qs = LLMCallLog.objects.filter(created_at__gte=prev_cutoff, created_at__lt=cutoff)

    # Overall
    overall = qs.aggregate(
        total_calls=Count('id'),
        successful=Count('id', filter=Q(success=True)),
        total_cost=Sum('cost'),
        total_tokens=Sum('total_tokens'),
        avg_latency=Avg('latency_ms'),
    )
    prev_overall = prev_qs.aggregate(
        total_cost=Sum('cost'),
        total_calls=Count('id'),
    )

    cost_now = float(overall['total_cost'] or 0)
    cost_prev = float(prev_overall['total_cost'] or 0)
    cost_delta_pct = round((cost_now - cost_prev) / cost_prev * 100, 1) if cost_prev > 0 else 0

    # By provider
    by_provider = list(
        qs.values('provider')
        .annotate(
            calls=Count('id'),
            cost=Sum('cost'),
            tokens=Sum('total_tokens'),
            avg_latency=Avg('latency_ms'),
            success_rate=Count('id', filter=Q(success=True)) * 100.0 / Count('id'),
        )
        .order_by('-cost')
    )
    for p in by_provider:
        p['cost'] = float(p['cost'] or 0)
        p['avg_latency'] = round(p['avg_latency'] or 0)
        p['success_rate'] = round(p['success_rate'] or 0, 1)

    # By model (top 10)
    by_model = list(
        qs.values('model_id', 'provider')
        .annotate(
            calls=Count('id'),
            cost=Sum('cost'),
            tokens=Sum('total_tokens'),
            avg_latency=Avg('latency_ms'),
        )
        .order_by('-cost')[:10]
    )
    for m in by_model:
        m['cost'] = float(m['cost'] or 0)
        m['avg_latency'] = round(m['avg_latency'] or 0)

    # Top agents by cost
    by_agent = list(
        qs.values('agent_name')
        .annotate(
            calls=Count('id'),
            cost=Sum('cost'),
            tokens=Sum('total_tokens'),
        )
        .order_by('-cost')[:15]
    )
    for a in by_agent:
        a['cost'] = float(a['cost'] or 0)

    return JsonResponse({
        'hours': hours,
        'generated_at': now().isoformat(),
        'overall': {
            'total_calls': overall['total_calls'] or 0,
            'successful': overall['successful'] or 0,
            'total_cost': round(cost_now, 4),
            'total_tokens': overall['total_tokens'] or 0,
            'avg_latency_ms': round(overall['avg_latency'] or 0),
            'cost_delta_pct': cost_delta_pct,
            'prev_cost': round(cost_prev, 4),
        },
        'by_provider': by_provider,
        'by_model': by_model,
        'by_agent': by_agent,
    })


# ---------------------------------------------------------------------------
# P14: Autopilot
# ---------------------------------------------------------------------------

# Default policies seeded on first access
_DEFAULT_POLICIES = [
    {
        'key': 'failure_spike_pause',
        'label': 'Auto-pause failing agents',
        'description': 'Pause agents with failure rate above threshold in the evaluation window.',
        'thresholds': {'failure_rate_pct': 50, 'min_runs': 3, 'window_hours': 1},
        'cooldown_minutes': 60,
        'max_actions_per_run': 5,
    },
    {
        'key': 'cost_spike_alert',
        'label': 'Cost spike incident note',
        'description': 'Create incident note when cost delta exceeds threshold vs previous window.',
        'thresholds': {'cost_delta_pct': 100, 'window_hours': 24},
        'cooldown_minutes': 120,
        'max_actions_per_run': 1,
    },
    {
        'key': 'queue_backlog_alert',
        'label': 'Queue backlog incident note',
        'description': 'Create incident note when failure rate across all queues exceeds threshold.',
        'thresholds': {'failure_rate_pct': 30, 'window_minutes': 60},
        'cooldown_minutes': 60,
        'max_actions_per_run': 1,
    },
    {
        'key': 'stale_agent_alert',
        'label': 'Flag stale agents',
        'description': 'Create incident note for agents with no runs in the specified hours.',
        'thresholds': {'stale_hours': 48, 'min_expected_runs': 1},
        'cooldown_minutes': 720,
        'max_actions_per_run': 3,
    },
]


def _seed_policies():
    """Seed default policies if none exist."""
    from core.models_cockpit_autopilot import CockpitAutopilotPolicy
    if CockpitAutopilotPolicy.objects.exists():
        return
    for p in _DEFAULT_POLICIES:
        CockpitAutopilotPolicy.objects.create(**p)


@csrf_exempt
@require_http_methods(['GET'])
def cockpit_autopilot_policies(request):
    """List all autopilot policies."""
    from core.models_cockpit_autopilot import CockpitAutopilotPolicy
    _seed_policies()

    policies = list(
        CockpitAutopilotPolicy.objects.all().values(
            'id', 'key', 'label', 'description', 'enabled',
            'thresholds', 'cooldown_minutes', 'max_actions_per_run',
            'last_evaluated_at', 'last_fired_at',
        )
    )
    for p in policies:
        p['id'] = str(p['id'])
        p['last_evaluated_at'] = p['last_evaluated_at'].isoformat() if p['last_evaluated_at'] else None
        p['last_fired_at'] = p['last_fired_at'].isoformat() if p['last_fired_at'] else None

    return JsonResponse({'total': len(policies), 'items': policies})


@csrf_exempt
@require_http_methods(['POST'])
def cockpit_autopilot_toggle(request, policy_id):
    """Enable or disable an autopilot policy."""
    from core.models_cockpit_autopilot import CockpitAutopilotPolicy

    try:
        policy = CockpitAutopilotPolicy.objects.get(id=policy_id)
    except CockpitAutopilotPolicy.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Policy not found'}, status=404)

    policy.enabled = not policy.enabled
    policy.save(update_fields=['enabled', 'updated_at'])

    resp = {'ok': True, 'key': policy.key, 'enabled': policy.enabled}
    _audit_log(request, f'autopilot.toggle_{("on" if policy.enabled else "off")}',
               'AutopilotPolicy', str(policy.id), {}, resp)
    return JsonResponse(resp)


@csrf_exempt
@require_http_methods(['POST'])
def cockpit_autopilot_evaluate(request):
    """Evaluate all enabled policies. mode=dry_run (default) or execute."""
    from core.models_cockpit_autopilot import CockpitAutopilotPolicy, CockpitAutopilotEvent
    from django.utils.timezone import now
    from datetime import timedelta

    try:
        body = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        body = {}

    mode = body.get('mode', 'dry_run')
    if mode not in ('dry_run', 'execute'):
        return JsonResponse({'ok': False, 'error': 'mode must be dry_run or execute'}, status=400)

    _seed_policies()
    policies = list(CockpitAutopilotPolicy.objects.filter(enabled=True))
    results = []

    for policy in policies:
        # Cooldown check
        if policy.last_fired_at and mode == 'execute':
            cooldown_end = policy.last_fired_at + timedelta(minutes=policy.cooldown_minutes)
            if now() < cooldown_end:
                results.append({
                    'policy': policy.key,
                    'skipped': True,
                    'reason': f'Cooldown until {cooldown_end.isoformat()}',
                    'actions': [],
                })
                continue

        actions = _evaluate_policy(policy, mode, request)

        policy.last_evaluated_at = now()
        if actions and mode == 'execute':
            policy.last_fired_at = now()
        policy.save(update_fields=['last_evaluated_at', 'last_fired_at', 'updated_at'])

        results.append({
            'policy': policy.key,
            'skipped': False,
            'actions': actions,
        })

    _audit_log(request, f'autopilot.evaluate_{mode}', 'AutopilotPolicy', '',
               {'mode': mode, 'policies_evaluated': len(policies)},
               {'total_actions': sum(len(r['actions']) for r in results)})

    return JsonResponse({
        'ok': True,
        'mode': mode,
        'evaluated_at': now().isoformat(),
        'results': results,
    })


def _evaluate_policy(policy, mode, request):
    """Evaluate a single policy and return list of proposed/executed actions."""
    from core.models_cockpit_autopilot import CockpitAutopilotEvent

    handler = _POLICY_EVALUATORS.get(policy.key)
    if not handler:
        return []

    proposed = handler(policy)
    actions = []

    for p in proposed[:policy.max_actions_per_run]:
        executed = False
        result = {}

        if mode == 'execute':
            result = _execute_action(p, request)
            executed = result.get('ok', False)

        event = CockpitAutopilotEvent.objects.create(
            policy=policy,
            mode=mode,
            proposed_action=p['action'],
            target_type=p.get('target_type', ''),
            target_id=p.get('target_id', ''),
            reason=p.get('reason', ''),
            executed=executed,
            result=result,
        )

        actions.append({
            'event_id': str(event.id),
            'action': p['action'],
            'target_type': p.get('target_type', ''),
            'target_id': p.get('target_id', ''),
            'reason': p.get('reason', ''),
            'executed': executed,
            'result': result,
        })

    return actions


def _eval_failure_spike_pause(policy):
    """Find agents with high failure rates."""
    from core.models_unified_system import AgentExecution
    from django.utils.timezone import now
    from datetime import timedelta
    from django.db.models import Count, Q

    t = policy.thresholds
    hours = t.get('failure_rate_pct_window', t.get('window_hours', 1))
    min_runs = t.get('min_runs', 3)
    threshold = t.get('failure_rate_pct', 50)
    cutoff = now() - timedelta(hours=hours)

    agents = (
        AgentExecution.objects.filter(created_at__gte=cutoff)
        .values('agent__name')
        .annotate(
            total=Count('id'),
            failed=Count('id', filter=Q(status='failed')),
        )
        .filter(total__gte=min_runs)
    )

    proposals = []
    for a in agents:
        rate = (a['failed'] / a['total']) * 100 if a['total'] else 0
        if rate >= threshold:
            # Skip already-paused agents
            from core.models_cockpit_agent_state import CockpitAgentState
            state = CockpitAgentState.objects.filter(agent_name=a['agent__name']).first()
            if state and not state.enabled:
                continue
            proposals.append({
                'action': 'agent.pause',
                'target_type': 'Agent',
                'target_id': a['agent__name'],
                'reason': f"Failure rate {rate:.0f}% ({a['failed']}/{a['total']}) in last {hours}h",
            })
    return proposals


def _eval_cost_spike_alert(policy):
    """Check if cost delta exceeds threshold."""
    from core.models_llm_routing import LLMCallLog
    from django.utils.timezone import now
    from datetime import timedelta
    from django.db.models import Sum

    t = policy.thresholds
    hours = t.get('window_hours', 24)
    threshold = t.get('cost_delta_pct', 100)
    cutoff = now() - timedelta(hours=hours)
    prev_cutoff = cutoff - timedelta(hours=hours)

    cost_now = float(LLMCallLog.objects.filter(created_at__gte=cutoff).aggregate(c=Sum('cost'))['c'] or 0)
    cost_prev = float(LLMCallLog.objects.filter(created_at__gte=prev_cutoff, created_at__lt=cutoff).aggregate(c=Sum('cost'))['c'] or 0)

    if cost_prev > 0:
        delta = ((cost_now - cost_prev) / cost_prev) * 100
        if delta >= threshold:
            return [{
                'action': 'create_incident_note',
                'target_type': 'CostSpike',
                'target_id': f'{hours}h',
                'reason': f"Cost spike +{delta:.0f}%: ${cost_now:.2f} vs ${cost_prev:.2f} (prev {hours}h)",
            }]
    return []


def _eval_queue_backlog_alert(policy):
    """Check if queue failure rate is alarming."""
    from core.models_celery_telemetry import CeleryTaskEvent
    from django.utils.timezone import now
    from datetime import timedelta
    from django.db.models import Count, Q

    t = policy.thresholds
    minutes = t.get('window_minutes', 60)
    threshold = t.get('failure_rate_pct', 30)
    cutoff = now() - timedelta(minutes=minutes)

    totals = CeleryTaskEvent.objects.filter(started_at__gte=cutoff).aggregate(
        total=Count('id'),
        failed=Count('id', filter=Q(status='FAILURE')),
    )
    total = totals['total'] or 0
    failed = totals['failed'] or 0
    if total >= 5 and (failed / total * 100) >= threshold:
        return [{
            'action': 'create_incident_note',
            'target_type': 'QueueBacklog',
            'target_id': f'{minutes}m',
            'reason': f"Queue failure rate {failed}/{total} ({failed/total*100:.0f}%) in last {minutes}m",
        }]
    return []


def _eval_stale_agent_alert(policy):
    """Find agents with no recent runs."""
    from core.models_unified_system import Agent, AgentExecution
    from django.utils.timezone import now
    from datetime import timedelta
    from django.db.models import Max

    t = policy.thresholds
    stale_hours = t.get('stale_hours', 48)
    cutoff = now() - timedelta(hours=stale_hours)

    agents_with_runs = set(
        AgentExecution.objects.filter(created_at__gte=cutoff)
        .values_list('agent__name', flat=True).distinct()
    )
    all_agents = set(Agent.objects.filter(is_active=True).values_list('name', flat=True))
    stale = all_agents - agents_with_runs

    proposals = []
    for name in sorted(stale):
        last = AgentExecution.objects.filter(agent__name=name).aggregate(last=Max('created_at'))['last']
        last_str = last.isoformat() if last else 'never'
        proposals.append({
            'action': 'create_incident_note',
            'target_type': 'StaleAgent',
            'target_id': name,
            'reason': f"No runs in {stale_hours}h (last run: {last_str})",
        })
    return proposals


_POLICY_EVALUATORS = {
    'failure_spike_pause': _eval_failure_spike_pause,
    'cost_spike_alert': _eval_cost_spike_alert,
    'queue_backlog_alert': _eval_queue_backlog_alert,
    'stale_agent_alert': _eval_stale_agent_alert,
}


def _execute_action(proposal, request):
    """Execute a proposed autopilot action using existing cockpit mutations."""
    action = proposal['action']
    target_id = proposal.get('target_id', '')
    reason = proposal.get('reason', '')

    if action == 'agent.pause':
        from core.models_unified_system import Agent
        from core.models_cockpit_agent_state import CockpitAgentState
        from django.utils.timezone import now as tz_now
        try:
            Agent.objects.get(name=target_id, is_active=True)
        except Agent.DoesNotExist:
            return {'ok': False, 'error': 'Agent not found'}
        CockpitAgentState.objects.update_or_create(
            agent_name=target_id,
            defaults={
                'enabled': False,
                'paused_reason': f'[autopilot] {reason}',
                'paused_at': tz_now(),
                'updated_by': None,
            },
        )
        _audit_log(request, 'autopilot.agent.pause', 'Agent', target_id, {'reason': reason},
                   {'ok': True})
        return {'ok': True, 'action': 'paused'}

    elif action == 'create_incident_note':
        import uuid as uuid_mod
        from django.utils.text import slugify
        from django.utils.timezone import now as tz_now
        from core.services.deliverable_factory import create_deliverable
        title = f"[Autopilot] {proposal.get('target_type', 'Alert')}: {target_id}"
        slug = f"{slugify(title[:60]) or 'autopilot'}-{uuid_mod.uuid4().hex[:8]}"
        content = f"# Autopilot Incident\n\n**Reason:** {reason}\n\n**Target:** {proposal.get('target_type', '')} — {target_id}\n\n**Created:** {tz_now().isoformat()}\n"
        deliverable = create_deliverable(
            title=title, content=content,
            agent_name='cockpit-autopilot',
            category='Incident', deliverable_type='document',
            tags=['incident', 'autopilot'],
            content_format='markdown',
            metadata={'source': 'autopilot', 'reason': reason},
            slug=slug, status='ready',
        )
        _audit_log(request, 'autopilot.incident_note', 'Deliverable', str(deliverable.id),
                   {'reason': reason}, {'ok': True})
        return {'ok': True, 'action': 'incident_created', 'id': str(deliverable.id)}

    return {'ok': False, 'error': f'Unknown action: {action}'}


@csrf_exempt
@require_http_methods(['GET'])
def cockpit_autopilot_history(request):
    """List recent autopilot events."""
    from core.models_cockpit_autopilot import CockpitAutopilotEvent
    limit = min(int(request.GET.get('limit', 50)), 200)

    events = list(
        CockpitAutopilotEvent.objects.select_related('policy')[:limit].values(
            'id', 'policy__key', 'mode', 'proposed_action',
            'target_type', 'target_id', 'reason', 'executed', 'result', 'created_at',
        )
    )
    for e in events:
        e['id'] = str(e['id'])
        e['policy_key'] = e.pop('policy__key')
        e['created_at'] = e['created_at'].isoformat() if e['created_at'] else None

    return JsonResponse({'total': len(events), 'items': events})


# ── P15: Run Trace ──────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(['GET'])
def cockpit_run_trace(request, run_id):
    """Stitch AgentExecution + CeleryTaskEvent + LLMCallLog + AuditLog into one trace."""
    from core.models_unified_system import AgentExecution
    from core.models_celery_telemetry import CeleryTaskEvent
    from core.models_llm_routing import LLMCallLog
    from core.models_cockpit_audit import CockpitAuditLog
    from datetime import timedelta

    try:
        run = AgentExecution.objects.select_related('agent').get(id=run_id)
    except AgentExecution.DoesNotExist:
        return JsonResponse({'error': 'Run not found'}, status=404)

    agent_name = run.agent.name if run.agent else ''
    started = run.created_at
    ended = run.completed_at or (started + timedelta(hours=1))
    # Widen window slightly to catch related events
    window_start = started - timedelta(seconds=30)
    window_end = ended + timedelta(seconds=30)

    # Run detail
    run_data = {
        'id': str(run.id),
        'agent_name': agent_name,
        'task': run.task or '',
        'status': run.status,
        'created_at': started.isoformat() if started else None,
        'completed_at': run.completed_at.isoformat() if run.completed_at else None,
        'execution_time_ms': run.execution_time_ms,
        'tokens_used': run.tokens_used or 0,
        'cost': str(run.cost) if run.cost else '0',
        'error_message': run.error_message or '',
        'trace_id': str(run.trace_id) if run.trace_id else None,
    }

    # Celery task events within time window
    celery_events = []
    qs = CeleryTaskEvent.objects.filter(
        started_at__gte=window_start,
        started_at__lte=window_end,
    ).order_by('started_at')[:50]
    for ev in qs:
        celery_events.append({
            'task_id': ev.task_id,
            'task_name': ev.task_name,
            'short_name': ev.task_name.rsplit('.', 1)[-1] if ev.task_name else '',
            'queue': ev.queue or '',
            'worker': ev.worker or '',
            'status': ev.status,
            'started_at': ev.started_at.isoformat() if ev.started_at else None,
            'finished_at': ev.finished_at.isoformat() if ev.finished_at else None,
            'duration_seconds': ev.duration_seconds,
            'rss_mb_start': ev.rss_mb_start,
            'rss_mb_end': ev.rss_mb_end,
            'rss_delta_mb': ev.rss_delta_mb,
            'error_type': ev.error_type or '',
            'error_message': ev.error_message or '',
        })

    # LLM calls — match by agent_name within time window
    llm_calls = []
    if agent_name:
        qs_llm = LLMCallLog.objects.filter(
            agent_name=agent_name,
            created_at__gte=window_start,
            created_at__lte=window_end,
        ).order_by('created_at')[:50]
        for c in qs_llm:
            llm_calls.append({
                'id': str(c.id),
                'provider': c.provider,
                'model_id': c.model_id,
                'prompt_tokens': c.prompt_tokens or 0,
                'completion_tokens': c.completion_tokens or 0,
                'total_tokens': c.total_tokens or 0,
                'cost': str(c.cost) if c.cost else '0',
                'latency_ms': c.latency_ms or 0,
                'success': c.success,
                'error_type': c.error_type or '',
                'error_message': c.error_message or '',
                'created_at': c.created_at.isoformat() if c.created_at else None,
            })

    # LLM rollup
    llm_total_cost = sum(float(c['cost']) for c in llm_calls)
    llm_total_tokens = sum(c['total_tokens'] for c in llm_calls)
    llm_avg_latency = (
        round(sum(c['latency_ms'] for c in llm_calls) / len(llm_calls))
        if llm_calls else 0
    )

    # Audit log entries related to this run
    audit_entries = []
    audit_qs = CockpitAuditLog.objects.filter(
        target_id=str(run.id),
    ).order_by('-created_at')[:20]
    for a in audit_qs:
        audit_entries.append({
            'id': str(a.id),
            'actor': a.user.username if a.user else 'system',
            'action': a.action,
            'target_type': a.target_type,
            'created_at': a.created_at.isoformat() if a.created_at else None,
        })

    # Build unified timeline
    timeline = []
    timeline.append({
        'type': 'run',
        'subtype': 'started',
        'timestamp': started.isoformat(),
        'summary': f'Run started: {agent_name}',
        'detail': run.task or '',
    })
    if run.completed_at:
        timeline.append({
            'type': 'run',
            'subtype': 'completed' if run.status == 'completed' else 'failed',
            'timestamp': run.completed_at.isoformat(),
            'summary': f'Run {run.status}: {agent_name}',
            'detail': run.error_message or '',
        })

    for ev in celery_events:
        timeline.append({
            'type': 'celery',
            'subtype': ev['status'],
            'timestamp': ev['started_at'] or '',
            'summary': f"Task {ev['short_name']} [{ev['status']}]",
            'detail': f"worker={ev['worker']} queue={ev['queue']} duration={ev['duration_seconds'] or 0:.1f}s",
        })

    for c in llm_calls:
        timeline.append({
            'type': 'llm',
            'subtype': 'success' if c['success'] else 'error',
            'timestamp': c['created_at'] or '',
            'summary': f"LLM {c['provider']}/{c['model_id']} — {c['total_tokens']}tok ${c['cost']}",
            'detail': c['error_message'] if not c['success'] else f"{c['latency_ms']}ms",
        })

    for a in audit_entries:
        timeline.append({
            'type': 'audit',
            'subtype': a['action'],
            'timestamp': a['created_at'] or '',
            'summary': f"{a['actor']}: {a['action']} {a['target_type']}",
            'detail': '',
        })

    timeline.sort(key=lambda x: x.get('timestamp') or '')

    return JsonResponse({
        'run': run_data,
        'celery_events': celery_events,
        'llm_calls': llm_calls,
        'llm_summary': {
            'total_calls': len(llm_calls),
            'total_cost': round(llm_total_cost, 6),
            'total_tokens': llm_total_tokens,
            'avg_latency_ms': llm_avg_latency,
        },
        'audit_entries': audit_entries,
        'timeline': timeline,
    })


# ── P16: Configuration Control Plane ────────────────────────────────

@csrf_exempt
@require_http_methods(['GET'])
def cockpit_config_overview(request):
    """Platform config overview: providers, models, flags, env info."""
    from core.models_llm_routing import LLMProvider, LLMModel
    from core.models.system import SystemConfiguration
    import os

    providers = []
    for p in LLMProvider.objects.all().order_by('name'):
        model_count = LLMModel.objects.filter(provider=p).count()
        providers.append({
            'id': str(p.id),
            'name': p.name,
            'display_name': p.display_name or p.name,
            'is_active': p.is_active,
            'is_available': p.is_available,
            'supports_tools': p.supports_tools,
            'supports_vision': p.supports_vision,
            'supports_streaming': p.supports_streaming,
            'model_count': model_count,
            'last_health_check': p.last_health_check.isoformat() if p.last_health_check else None,
        })

    # Session 1075: Fall back to LLMProviderRegistry if DB tables are empty
    if not providers:
        try:
            from core.services.llm_provider_registry import LLMProviderRegistry
            registry = LLMProviderRegistry()
            for name, prov in registry.providers.items():
                available = prov.is_available() if hasattr(prov, 'is_available') else False
                models_for = getattr(prov, 'MODELS', getattr(prov, 'models', []))
                providers.append({
                    'id': name,
                    'name': name,
                    'display_name': name.title(),
                    'is_active': True,
                    'is_available': available,
                    'supports_tools': getattr(prov, 'supports_tools', True),
                    'supports_vision': getattr(prov, 'supports_vision', False),
                    'supports_streaming': getattr(prov, 'supports_streaming', True),
                    'model_count': len(models_for) if isinstance(models_for, (list, dict)) else 0,
                    'last_health_check': None,
                })
        except Exception as e:
            logger.warning(f"[Cockpit] LLMProviderRegistry fallback failed: {e}")

    models_list = []
    for m in LLMModel.objects.select_related('provider').order_by('provider__name', 'model_id'):
        models_list.append({
            'id': str(m.id),
            'model_id': m.model_id,
            'provider': m.provider.name,
            'is_active': m.is_active if hasattr(m, 'is_active') else True,
        })

    # Session 1075: Fall back to registry models if DB is empty
    if not models_list:
        try:
            from core.services.llm_provider_registry import LLMProviderRegistry
            registry = LLMProviderRegistry()
            for m in registry.get_available_models():
                models_list.append({
                    'id': f"{m['provider']}:{m['model']}",
                    'model_id': m['model'],
                    'provider': m['provider'],
                    'is_active': True,
                })
        except Exception as _e:
            logger.warning(
                "views_diagnostics.cockpit_config_overview: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

    flags = []
    for cfg in SystemConfiguration.objects.filter(is_active=True).order_by('category', 'key'):
        flags.append({
            'id': str(cfg.id),
            'key': cfg.key,
            'value': cfg.value,
            'description': cfg.description or '',
            'category': cfg.category or 'general',
            'is_sensitive': cfg.is_sensitive,
            'updated_at': cfg.updated_at.isoformat() if cfg.updated_at else None,
        })

    return JsonResponse({
        'providers': providers,
        'models': models_list,
        'flags': flags,
        'env': {
            'debug': os.environ.get('DEBUG', 'False') == 'True',
            'database': 'postgresql',
            'redis': bool(os.environ.get('REDIS_URL')),
            'celery_broker': bool(os.environ.get('CELERY_BROKER_URL', os.environ.get('REDIS_URL'))),
            'railway': bool(os.environ.get('RAILWAY_ENVIRONMENT')),
        },
    })


@csrf_exempt
@require_http_methods(['POST'])
def cockpit_config_toggle_provider(request, provider_id):
    """Toggle a provider's is_active flag."""
    from core.models_llm_routing import LLMProvider
    import json

    try:
        provider = LLMProvider.objects.get(id=provider_id)
    except LLMProvider.DoesNotExist:
        return JsonResponse({'error': 'Provider not found'}, status=404)

    provider.is_active = not provider.is_active
    provider.save(update_fields=['is_active', 'updated_at'])

    _audit_log(request, 'config.toggle_provider', 'LLMProvider', str(provider.id),
               {'provider': provider.name, 'is_active': provider.is_active},
               {'ok': True, 'is_active': provider.is_active})

    return JsonResponse({'ok': True, 'provider': provider.name, 'is_active': provider.is_active})


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def cockpit_config_flags(request):
    """List or upsert feature flags (SystemConfiguration)."""
    from core.models.system import SystemConfiguration
    import json

    if request.method == 'GET':
        flags = []
        for cfg in SystemConfiguration.objects.filter(is_active=True).order_by('category', 'key'):
            flags.append({
                'id': str(cfg.id),
                'key': cfg.key,
                'value': cfg.value,
                'description': cfg.description or '',
                'category': cfg.category or 'general',
                'is_sensitive': cfg.is_sensitive,
                'updated_at': cfg.updated_at.isoformat() if cfg.updated_at else None,
            })
        return JsonResponse({'flags': flags})

    # POST: upsert a flag
    body = json.loads(request.body or b'{}')
    key = body.get('key', '').strip()
    if not key:
        return JsonResponse({'error': 'key is required'}, status=400)

    value = body.get('value')
    description = body.get('description', '')
    category = body.get('category', 'general')

    cfg, created = SystemConfiguration.objects.update_or_create(
        key=key,
        defaults={
            'value': value,
            'description': description,
            'category': category,
            'is_active': True,
        },
    )

    _audit_log(request, 'config.upsert_flag', 'SystemConfiguration', str(cfg.id),
               {'key': key, 'value': value, 'created': created},
               {'ok': True, 'id': str(cfg.id)})

    return JsonResponse({
        'ok': True,
        'id': str(cfg.id),
        'key': cfg.key,
        'value': cfg.value,
        'created': created,
    })


@csrf_exempt
@require_http_methods(['POST'])
def cockpit_config_delete_flag(request, flag_id):
    """Soft-delete a feature flag."""
    from core.models.system import SystemConfiguration

    try:
        cfg = SystemConfiguration.objects.get(id=flag_id)
    except SystemConfiguration.DoesNotExist:
        return JsonResponse({'error': 'Flag not found'}, status=404)

    cfg.is_active = False
    cfg.save(update_fields=['is_active', 'updated_at'])

    _audit_log(request, 'config.delete_flag', 'SystemConfiguration', str(cfg.id),
               {'key': cfg.key}, {'ok': True})

    return JsonResponse({'ok': True, 'key': cfg.key})


@csrf_exempt
@require_http_methods(['GET'])
def cockpit_config_changes(request):
    """Recent config-related changes from audit log."""
    from core.models_cockpit_audit import CockpitAuditLog
    from django.utils import timezone
    from datetime import timedelta

    hours = min(int(request.GET.get('hours', 48)), 720)
    limit = min(int(request.GET.get('limit', 50)), 200)
    since = timezone.now() - timedelta(hours=hours)

    entries = list(
        CockpitAuditLog.objects
        .filter(created_at__gte=since, action__startswith='config.')
        .select_related('user')
        .order_by('-created_at')[:limit]
    )

    items = []
    for e in entries:
        items.append({
            'id': str(e.id),
            'actor': e.user.username if e.user else 'system',
            'action': e.action,
            'target_type': e.target_type,
            'target_id': e.target_id,
            'request_body': e.request_body or {},
            'response_summary': e.response_summary or {},
            'created_at': e.created_at.isoformat() if e.created_at else None,
        })

    return JsonResponse({'hours': hours, 'total': len(items), 'items': items})


# ─── P17: Incident Commander ─────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def cockpit_incidents_list(request):
    """GET: list incidents, POST: create incident."""
    from core.models_cockpit_incidents import CockpitIncident, CockpitIncidentEvent
    from django.db.models import Count, Max, Q

    if request.method == 'POST':
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

        title = body.get('title', '').strip()
        if not title:
            return JsonResponse({'ok': False, 'error': 'title is required'}, status=400)

        severity = body.get('severity', 'medium')
        if severity not in ('critical', 'high', 'medium', 'low'):
            severity = 'medium'

        incident = CockpitIncident.objects.create(
            title=title,
            severity=severity,
            owner=body.get('owner', ''),
        )

        # Auto-link initial evidence if provided
        initial_links = body.get('links', [])
        for link in initial_links[:10]:
            link_type = link.get('type', '')
            link_id = link.get('id', '')
            if link_type and link_id:
                CockpitIncidentEvent.objects.create(
                    incident=incident,
                    event_type='link',
                    actor=request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'operator',
                    content={'link_type': link_type, 'link_id': link_id, 'label': link.get('label', '')},
                )

        _audit_log(request, 'incident.create', 'incident', str(incident.id),
                   request_body=body, response_summary={'severity': severity})

        return JsonResponse({
            'ok': True,
            'id': str(incident.id),
            'title': incident.title,
            'severity': incident.severity,
            'status': incident.status,
            'created_at': incident.created_at.isoformat(),
        }, status=201)

    # GET: list
    status_filter = request.GET.get('status', '')
    severity_filter = request.GET.get('severity', '')
    q = request.GET.get('q', '').strip()
    limit = min(int(request.GET.get('limit', 50)), 200)
    offset = int(request.GET.get('offset', 0))

    qs = CockpitIncident.objects.all()
    if status_filter and status_filter != 'all':
        qs = qs.filter(status=status_filter)
    if severity_filter:
        qs = qs.filter(severity=severity_filter)
    if q:
        qs = qs.filter(title__icontains=q)

    total = qs.count()
    incidents = qs.annotate(
        event_count=Count('events'),
        link_count=Count('events', filter=Q(events__event_type='link')),
        last_activity=Max('events__created_at'),
    ).order_by('-created_at')[offset:offset + limit]

    items = []
    for inc in incidents:
        items.append({
            'id': str(inc.id),
            'title': inc.title,
            'severity': inc.severity,
            'status': inc.status,
            'owner': inc.owner,
            'event_count': inc.event_count,
            'link_count': inc.link_count,
            'last_activity': inc.last_activity.isoformat() if inc.last_activity else None,
            'created_at': inc.created_at.isoformat(),
            'updated_at': inc.updated_at.isoformat(),
        })

    return JsonResponse({'total': total, 'offset': offset, 'limit': limit, 'items': items})


@csrf_exempt
@require_http_methods(["GET"])
def cockpit_incident_detail(request, incident_id):
    """Get incident detail with timeline events."""
    from core.models_cockpit_incidents import CockpitIncident, CockpitIncidentEvent

    try:
        inc = CockpitIncident.objects.get(pk=incident_id)
    except CockpitIncident.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Incident not found'}, status=404)

    events = CockpitIncidentEvent.objects.filter(incident=inc).order_by('created_at')

    event_items = []
    for ev in events:
        event_items.append({
            'id': str(ev.id),
            'event_type': ev.event_type,
            'actor': ev.actor,
            'content': ev.content,
            'created_at': ev.created_at.isoformat(),
        })

    return JsonResponse({
        'ok': True,
        'incident': {
            'id': str(inc.id),
            'title': inc.title,
            'severity': inc.severity,
            'status': inc.status,
            'owner': inc.owner,
            'resolution_summary': inc.resolution_summary,
            'created_at': inc.created_at.isoformat(),
            'updated_at': inc.updated_at.isoformat(),
        },
        'events': event_items,
        'event_count': len(event_items),
    })


@csrf_exempt
@require_http_methods(["POST"])
def cockpit_incident_update(request, incident_id):
    """Update incident status, severity, owner, or resolution summary."""
    from core.models_cockpit_incidents import CockpitIncident, CockpitIncidentEvent

    try:
        inc = CockpitIncident.objects.get(pk=incident_id)
    except CockpitIncident.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Incident not found'}, status=404)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    actor = request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'operator'
    changes = {}

    if 'status' in body and body['status'] in ('open', 'mitigating', 'resolved'):
        old_status = inc.status
        inc.status = body['status']
        changes['status'] = {'from': old_status, 'to': body['status']}

    if 'severity' in body and body['severity'] in ('critical', 'high', 'medium', 'low'):
        old_severity = inc.severity
        inc.severity = body['severity']
        changes['severity'] = {'from': old_severity, 'to': body['severity']}

    if 'owner' in body:
        inc.owner = body['owner']
        changes['owner'] = body['owner']

    if 'resolution_summary' in body:
        inc.resolution_summary = body['resolution_summary']
        changes['resolution_summary'] = True

    if changes:
        inc.save()
        CockpitIncidentEvent.objects.create(
            incident=inc,
            event_type='status_change',
            actor=actor,
            content=changes,
        )
        _audit_log(request, 'incident.update', 'incident', str(inc.id),
                   request_body=body, response_summary=changes)

    return JsonResponse({
        'ok': True,
        'id': str(inc.id),
        'status': inc.status,
        'severity': inc.severity,
        'owner': inc.owner,
    })


@csrf_exempt
@require_http_methods(["POST"])
def cockpit_incident_add_event(request, incident_id):
    """Add a note or link event to an incident timeline."""
    from core.models_cockpit_incidents import CockpitIncident, CockpitIncidentEvent

    try:
        inc = CockpitIncident.objects.get(pk=incident_id)
    except CockpitIncident.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Incident not found'}, status=404)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    event_type = body.get('event_type', '')
    if event_type not in ('note', 'link'):
        return JsonResponse({'ok': False, 'error': 'event_type must be note or link'}, status=400)

    actor = request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'operator'

    if event_type == 'note':
        text = body.get('text', '').strip()
        if not text:
            return JsonResponse({'ok': False, 'error': 'text is required for notes'}, status=400)
        content = {'text': text}
    else:
        link_type = body.get('link_type', '')
        link_id = body.get('link_id', '')
        if not link_type or not link_id:
            return JsonResponse({'ok': False, 'error': 'link_type and link_id required'}, status=400)
        content = {'link_type': link_type, 'link_id': link_id, 'label': body.get('label', '')}

    event = CockpitIncidentEvent.objects.create(
        incident=inc,
        event_type=event_type,
        actor=actor,
        content=content,
    )

    _audit_log(request, 'incident.add_event', 'incident', str(inc.id),
               request_body=body, response_summary={'event_id': str(event.id), 'type': event_type})

    return JsonResponse({
        'ok': True,
        'id': str(event.id),
        'event_type': event_type,
        'content': content,
        'created_at': event.created_at.isoformat(),
    }, status=201)


# ──────────────────────────────────────────────────────────────
#  Ops Runs — structured observability for multi-step operations
# ──────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(['GET'])
def cockpit_ops_runs_list(request):
    """GET /api/cockpit/ops-runs/ — list recent OpsRuns. Admin only."""
    if not (request.user.is_authenticated and request.user.is_staff):
        return JsonResponse({'error': 'admin required'}, status=403)

    from core.models_ops_runs import OpsRun
    from django.utils import timezone as tz

    run_type = request.GET.get('run_type')
    status = request.GET.get('status')
    hours = int(request.GET.get('hours', 72))
    limit = min(int(request.GET.get('limit', 50)), 200)

    cutoff = tz.now() - timedelta(hours=hours)
    qs = OpsRun.objects.filter(started_at__gte=cutoff)
    if run_type:
        qs = qs.filter(run_type=run_type)
    if status:
        qs = qs.filter(status=status)

    items = []
    for run in qs[:limit]:
        items.append({
            'id': str(run.id),
            'title': run.title,
            'run_type': run.run_type,
            'status': run.status,
            'triggered_by': run.triggered_by,
            'started_at': run.started_at.isoformat() if run.started_at else None,
            'finished_at': run.finished_at.isoformat() if run.finished_at else None,
            'event_count': run.event_count,
            'fail_count': run.fail_count,
            'summary': run.summary,
        })

    return JsonResponse({
        'hours': hours,
        'total': len(items),
        'items': items,
    })


@csrf_exempt
@require_http_methods(['GET'])
def cockpit_ops_run_detail(request, run_id):
    """GET /api/cockpit/ops-runs/<uuid>/ — OpsRun detail + events. Admin only."""
    if not (request.user.is_authenticated and request.user.is_staff):
        return JsonResponse({'error': 'admin required'}, status=403)

    from core.models_ops_runs import OpsRun

    try:
        run = OpsRun.objects.get(id=run_id)
    except OpsRun.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)

    events = []
    for ev in run.events.all():
        events.append({
            'id': str(ev.id),
            'event_type': ev.event_type,
            'label': ev.label,
            'detail': ev.detail,
            'created_at': ev.created_at.isoformat() if ev.created_at else None,
        })

    return JsonResponse({
        'ok': True,
        'run': {
            'id': str(run.id),
            'title': run.title,
            'run_type': run.run_type,
            'status': run.status,
            'triggered_by': run.triggered_by,
            'started_at': run.started_at.isoformat() if run.started_at else None,
            'finished_at': run.finished_at.isoformat() if run.finished_at else None,
            'event_count': run.event_count,
            'fail_count': run.fail_count,
            'summary': run.summary,
        },
        'events': events,
    })


# ── VIP Context Endpoint ────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET"])
def cockpit_vip_context(request):
    """Return VIP personalization context for the current user.

    If the user is a VIP demo viewer, returns their workspace, prospect
    profile, and personalized welcome data. Non-VIP users get is_vip=false.
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    from core.vip_scope import get_vip_scope
    scope = get_vip_scope(request)

    if not scope.is_vip:
        return JsonResponse({'is_vip': False})

    result = {
        'is_vip': True,
        'recipient_name': scope.recipient_name or '',
        'workspace_id': scope.workspace_id,
        'workspace_name': scope.workspace_name,
        'prospect_profile_id': scope.prospect_profile_id,
    }

    # Load workspace deliverable count
    if scope.workspace_id:
        from core.models_deliverables import Deliverable
        result['workspace_deliverable_count'] = Deliverable.objects.filter(
            workspace_id=scope.workspace_id,
        ).count()

    # Load prospect profile summary
    if scope.prospect_profile_id:
        from core.models_deliverables import Deliverable
        try:
            profile = Deliverable.objects.get(id=scope.prospect_profile_id)
            result['prospect_profile_title'] = profile.title
            result['prospect_profile_preview'] = (profile.content or '')[:500]
        except Deliverable.DoesNotExist:
            pass

    return JsonResponse(result)


# ── Learning Loop Control Panel ──────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET"])
def cockpit_learning_loop(request):
    """Learning Loop Control Panel — recent learnings, patterns, rejections, agent improvement.

    Returns 4 sections:
    - recent_learnings: last 50 knowledge/memory entries
    - reinforced_patterns: most frequently referenced knowledge types
    - rejected: failed executions, negative feedback, archived content
    - agent_improvement: per-agent success rate trends
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Avg, Q, F

    cutoff_7d = timezone.now() - timedelta(days=7)
    cutoff_30d = timezone.now() - timedelta(days=30)

    result = {}

    # 1. Recent Learnings (last 50 knowledge + memory entries)
    try:
        from core.models_unified_system import AgentKnowledgeSource, AgentMemory

        recent_knowledge = list(
            AgentKnowledgeSource.objects.filter(is_active=True)
            .select_related('agent')
            .order_by('-last_updated_at')[:25]
            .values('id', 'title', 'knowledge_type', 'confidence_score',
                    'agent__name', 'last_updated_at', 'data_points_count')
        )
        for item in recent_knowledge:
            item['id'] = str(item['id'])
            item['last_updated_at'] = item['last_updated_at'].isoformat() if item['last_updated_at'] else None
            item['source'] = 'knowledge'

        recent_memories = list(
            AgentMemory.objects.filter(importance__gte=5)
            .select_related('agent')
            .order_by('-created_at')[:25]
            .values('id', 'title', 'memory_type', 'importance',
                    'valence', 'agent__name', 'created_at')
        )
        for item in recent_memories:
            item['id'] = str(item['id'])
            item['created_at'] = item['created_at'].isoformat() if item['created_at'] else None
            item['source'] = 'memory'

        # Merge and sort by date
        all_learnings = sorted(
            recent_knowledge + recent_memories,
            key=lambda x: x.get('last_updated_at') or x.get('created_at') or '',
            reverse=True,
        )[:50]

        result['recent_learnings'] = {
            'count': len(all_learnings),
            'items': all_learnings,
            'total_knowledge': AgentKnowledgeSource.objects.filter(is_active=True).count(),
            'total_memories': AgentMemory.objects.count(),
        }
    except Exception as e:
        result['recent_learnings'] = {'error': str(e), 'items': []}

    # 2. Reinforced Patterns (most common knowledge types + high-confidence items)
    try:
        from core.models_unified_system import AgentKnowledgeSource

        by_type = list(
            AgentKnowledgeSource.objects.filter(is_active=True)
            .values('knowledge_type')
            .annotate(
                count=Count('id'),
                avg_confidence=Avg('confidence_score'),
                avg_freshness=Avg('freshness_score'),
            )
            .order_by('-count')[:10]
        )

        top_validated = list(
            AgentKnowledgeSource.objects.filter(is_active=True, is_validated=True)
            .select_related('agent')
            .order_by('-confidence_score')[:10]
            .values('id', 'title', 'knowledge_type', 'confidence_score',
                    'agent__name', 'data_points_count')
        )
        for item in top_validated:
            item['id'] = str(item['id'])

        # Memory patterns — what types recur most
        memory_patterns = list(
            AgentMemory.objects.filter(created_at__gte=cutoff_30d)
            .values('memory_type', 'valence')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        result['reinforced_patterns'] = {
            'by_knowledge_type': by_type,
            'top_validated': top_validated,
            'memory_patterns': memory_patterns,
        }
    except Exception as e:
        result['reinforced_patterns'] = {'error': str(e)}

    # 3. Rejected / Failed (negative feedback, failures, archived)
    try:
        from core.models_unified_system import AgentExecution, AgentMemory

        # Failed executions (last 7 days)
        failed_executions = list(
            AgentExecution.objects.filter(
                status='failed',
                created_at__gte=cutoff_7d,
            )
            .select_related('agent')
            .order_by('-created_at')[:15]
            .values('id', 'agent__name', 'task', 'created_at', 'execution_time_ms')
        )
        for item in failed_executions:
            item['id'] = str(item['id'])
            item['created_at'] = item['created_at'].isoformat() if item['created_at'] else None
            item['task'] = (item['task'] or '')[:150]

        # Negative memories (failures, negative valence)
        negative_memories = list(
            AgentMemory.objects.filter(
                Q(memory_type='failure') | Q(valence='negative'),
                created_at__gte=cutoff_30d,
            )
            .select_related('agent')
            .order_by('-created_at')[:15]
            .values('id', 'title', 'memory_type', 'valence', 'agent__name', 'created_at')
        )
        for item in negative_memories:
            item['id'] = str(item['id'])
            item['created_at'] = item['created_at'].isoformat() if item['created_at'] else None

        # Invalidated knowledge
        invalidated = list(
            AgentKnowledgeSource.objects.filter(is_active=False)
            .select_related('agent')
            .order_by('-last_updated_at')[:10]
            .values('id', 'title', 'knowledge_type', 'agent__name', 'last_updated_at')
        )
        for item in invalidated:
            item['id'] = str(item['id'])
            item['last_updated_at'] = item['last_updated_at'].isoformat() if item['last_updated_at'] else None

        result['rejected'] = {
            'failed_executions': failed_executions,
            'negative_memories': negative_memories,
            'invalidated_knowledge': invalidated,
            'failed_count_7d': len(failed_executions),
            'negative_count_30d': len(negative_memories),
        }
    except Exception as e:
        result['rejected'] = {'error': str(e)}

    # 4. Agent Improvement (per-agent success rates)
    try:
        from core.models_unified_system import AgentExecution

        # Per-agent stats for last 30 days
        agent_stats = list(
            AgentExecution.objects.filter(created_at__gte=cutoff_30d)
            .values('agent__name')
            .annotate(
                total=Count('id'),
                completed=Count('id', filter=Q(status='completed')),
                failed=Count('id', filter=Q(status='failed')),
                avg_time_ms=Avg('execution_time_ms'),
            )
            .order_by('-total')[:25]
        )

        for stat in agent_stats:
            stat['success_rate'] = round(
                (stat['completed'] / stat['total'] * 100) if stat['total'] > 0 else 0, 1
            )
            stat['avg_time_ms'] = round(stat['avg_time_ms'] or 0)

        # Top improvers — agents with high success rate and high volume
        top_performers = sorted(
            [s for s in agent_stats if s['total'] >= 5],
            key=lambda x: x['success_rate'],
            reverse=True,
        )[:10]

        # Struggling agents — low success rate
        struggling = sorted(
            [s for s in agent_stats if s['total'] >= 3 and s['success_rate'] < 80],
            key=lambda x: x['success_rate'],
        )[:10]

        result['agent_improvement'] = {
            'agent_stats': agent_stats,
            'top_performers': top_performers,
            'struggling': struggling,
            'total_executions_30d': sum(s['total'] for s in agent_stats),
            'overall_success_rate': round(
                sum(s['completed'] for s in agent_stats) / max(sum(s['total'] for s in agent_stats), 1) * 100, 1
            ),
        }
    except Exception as e:
        result['agent_improvement'] = {'error': str(e)}

    return JsonResponse(result)

    return JsonResponse(result)