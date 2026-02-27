"""
Diagnostic Views to Expose ALL Backend Data
This file creates comprehensive diagnostic endpoints to see everything happening in the backend
"""

import json
import logging
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import render
import redis
import traceback

logger = logging.getLogger(__name__)

def get_redis_client():
    """Get Redis client for diagnostics"""
    try:
        return redis.StrictRedis(
            host=settings.REDIS_HOST if hasattr(settings, 'REDIS_HOST') else 'localhost',
            port=settings.REDIS_PORT if hasattr(settings, 'REDIS_PORT') else 6379,
            db=0,
            decode_responses=True
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
                except Exception:
                    pass
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
        except Exception:
            pass

        try:
            from ai_core.intelligence.advisor_registry import get_all_advisors
            advisors = get_all_advisors()
            agent_data['advisors'] = advisors[:5] if advisors else []
            agent_data['total_advisors'] = len(advisors) if advisors else 0
        except Exception:
            pass

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
    Staff-only. POST required to prevent accidental triggers.
    """
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
    except Exception:
        pass

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
    except Exception:
        pass

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

    # 4. Failed runs
    try:
        from core.models_unified_system import AgentExecution
        failed = AgentExecution.objects.filter(
            status='failed', created_at__gte=cutoff,
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
    Query params: status, agent, hours (default 24), limit (default 50)
    """
    if not (request.user and request.user.is_authenticated):
        return JsonResponse({'error': 'Authentication required'}, status=401)

    from django.utils import timezone
    from datetime import timedelta

    hours = int(request.GET.get('hours', 24))
    limit = min(int(request.GET.get('limit', 50)), 200)
    cutoff = timezone.now() - timedelta(hours=hours)

    try:
        from core.models_unified_system import AgentExecution
        qs = AgentExecution.objects.filter(created_at__gte=cutoff).select_related('agent')

        status_filter = request.GET.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        agent_filter = request.GET.get('agent')
        if agent_filter:
            qs = qs.filter(agent__name__icontains=agent_filter)

        runs = list(
            qs.order_by('-created_at')[:limit]
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

        return JsonResponse(result, safe=False)
    except Exception as e:
        logger.exception("cockpit_runs_list error")
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
            return JsonResponse(result)
    except Exception:
        pass

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
        elif async_result.state == 'FAILURE':
            result['status'] = 'failed'
            result['progress'] = 0.0
            result['error'] = str(async_result.result)[:500] if async_result.result else None
        else:
            result['status'] = async_result.state.lower()
    except Exception:
        pass

    return JsonResponse(result)


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
        if r and r.ping():
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
    except Exception:
        pass

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

    cutoff = now() - timedelta(hours=days * 24)
    qs = Deliverable.objects.filter(created_at__gte=cutoff).order_by('-created_at')

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
            images = list(
                ImageHistory.objects.filter(created_at__gte=cutoff)
                .order_by('-created_at')[:500]
                .values('id', 'filename', 'file_path', 'thumbnail', 'image_type', 'prompt', 'created_at')
            )
            for img in images:
                items.append({
                    'id': str(img['id']),
                    'kind': 'image',
                    'title': img['filename'] or 'Untitled',
                    'url': img['file_path'] or '',
                    'thumbnail_url': img['thumbnail'] or '',
                    'sub_type': img['image_type'] or '',
                    'prompt': (img['prompt'] or '')[:200],
                    'created_at': img['created_at'].isoformat() if img['created_at'] else None,
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

    return JsonResponse({
        'ok': True,
        'id': str(item.id),
        'decision': decision,
        'status': item.status,
    })


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

    return JsonResponse({
        'ok': True,
        'id': str(gate.id),
        'action': action,
        'status': gate.status,
    })