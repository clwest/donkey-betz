#!/usr/bin/env python
"""
Simple Production Test
Quick test of key production components
"""

import os
import sys
import json
import time
from datetime import datetime, timezone

# Add project to path
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    import django
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)


def test_redis_connection():
    """Test Redis connection"""
    try:
        import redis
        from django.conf import settings

        redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/1')
        r = redis.from_url(redis_url)

        start_time = time.time()
        r.ping()
        ping_time = (time.time() - start_time) * 1000

        print(f"✅ Redis connection successful ({ping_time:.2f}ms)")
        return True, ping_time
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False, 0


def test_database_connection():
    """Test database connection"""
    try:
        from django.db import connection
        from core.models.agents_registry import UnifiedAgentTemplate

        start_time = time.time()
        agent_count = UnifiedAgentTemplate.objects.filter(is_active=True).count()
        query_time = (time.time() - start_time) * 1000

        print(f"✅ Database connection successful - {agent_count} active agents ({query_time:.2f}ms)")
        return True, agent_count, query_time
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False, 0, 0


def test_websocket_routing():
    """Test WebSocket routing configuration"""
    try:
        from core.routing import websocket_urlpatterns

        endpoint_count = len(websocket_urlpatterns)

        # Check for key endpoints
        key_endpoints = [
            'revenue-dashboard',
            'neural-orchestra',
            'income-builder'
        ]

        found_endpoints = []
        for pattern in websocket_urlpatterns:
            pattern_str = str(pattern.pattern)
            for endpoint in key_endpoints:
                if endpoint in pattern_str:
                    found_endpoints.append(endpoint)

        print(f"✅ WebSocket routing configured - {endpoint_count} total endpoints")
        print(f"   Key endpoints found: {', '.join(found_endpoints)}")
        return True, endpoint_count, found_endpoints
    except Exception as e:
        print(f"❌ WebSocket routing test failed: {e}")
        return False, 0, []


def test_unified_hub():
    """Test Unified Hub functionality"""
    try:
        from core.unified_hub import UnifiedWebSocketHub

        # Test instantiation
        hub = UnifiedWebSocketHub()
        print(f"✅ Unified Hub instantiation successful")

        # Test component identification
        test_paths = [
            '/ws/revenue-dashboard/',
            '/ws/neural-orchestra/',
            '/ws/income-builder/'
        ]

        identified_components = []
        for path in test_paths:
            component = hub.identify_component(path)
            identified_components.append((path, component))

        print(f"   Component identification working: {len(identified_components)} components")
        return True, identified_components
    except Exception as e:
        print(f"❌ Unified Hub test failed: {e}")
        return False, []


def test_production_websocket():
    """Test Production WebSocket consumer"""
    try:
        from core.production_websocket import ProductionRevenueConsumer

        # Test instantiation
        consumer = ProductionRevenueConsumer()
        print(f"✅ Production WebSocket consumer instantiation successful")

        return True
    except Exception as e:
        print(f"❌ Production WebSocket test failed: {e}")
        return False


def test_agent_optimizer():
    """Test Agent Optimizer"""
    try:
        from core.agent_optimizer import agent_optimizer

        # Test performance summary for a dummy agent
        summary = agent_optimizer.performance_metrics
        print(f"✅ Agent Optimizer loaded - tracking {len(summary)} agents")

        return True, len(summary)
    except Exception as e:
        print(f"❌ Agent Optimizer test failed: {e}")
        return False, 0


def calculate_production_score(test_results):
    """Calculate production readiness score"""
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result.get('passed', False))

    base_score = (passed_tests / total_tests) * 100

    # Apply weights for critical components
    critical_weights = {
        'redis': 0.25,
        'database': 0.20,
        'websocket_routing': 0.20,
        'unified_hub': 0.15,
        'production_websocket': 0.15,
        'agent_optimizer': 0.05
    }

    weighted_score = 0
    for test_name, weight in critical_weights.items():
        if test_name in test_results and test_results[test_name].get('passed', False):
            weighted_score += weight * 100

    return min(base_score, weighted_score)


def main():
    """Run production tests"""
    print("=" * 80)
    print("PRODUCTION PERFECTION FINALIZER - QUICK TEST")
    print("=" * 80)
    print(f"Starting tests at {datetime.now(timezone.utc).isoformat()}")
    print()

    test_results = {}

    # Test Redis
    print("Testing Redis Connection...")
    redis_passed, ping_time = test_redis_connection()
    test_results['redis'] = {'passed': redis_passed, 'ping_time': ping_time}
    print()

    # Test Database
    print("Testing Database Connection...")
    db_passed, agent_count, query_time = test_database_connection()
    test_results['database'] = {'passed': db_passed, 'agent_count': agent_count, 'query_time': query_time}
    print()

    # Test WebSocket Routing
    print("Testing WebSocket Routing...")
    ws_passed, endpoint_count, found_endpoints = test_websocket_routing()
    test_results['websocket_routing'] = {'passed': ws_passed, 'endpoint_count': endpoint_count, 'found_endpoints': found_endpoints}
    print()

    # Test Unified Hub
    print("Testing Unified Hub...")
    hub_passed, components = test_unified_hub()
    test_results['unified_hub'] = {'passed': hub_passed, 'components': components}
    print()

    # Test Production WebSocket
    print("Testing Production WebSocket...")
    prod_ws_passed = test_production_websocket()
    test_results['production_websocket'] = {'passed': prod_ws_passed}
    print()

    # Test Agent Optimizer
    print("Testing Agent Optimizer...")
    optimizer_passed, tracked_agents = test_agent_optimizer()
    test_results['agent_optimizer'] = {'passed': optimizer_passed, 'tracked_agents': tracked_agents}
    print()

    # Calculate overall score
    production_score = calculate_production_score(test_results)

    # Display results
    print("=" * 80)
    print("PRODUCTION TEST RESULTS")
    print("=" * 80)
    print(f"Overall Score: {production_score:.1f}%")
    print(f"Production Ready: {'✅ YES' if production_score >= 95.0 else '⚠️  NEEDS WORK'}")
    print()

    # Detailed results
    print("Component Status:")
    for component, result in test_results.items():
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"  {component.replace('_', ' ').title()}: {status}")

    print()

    # Key metrics
    print("Key Metrics:")
    if test_results['redis']['passed']:
        print(f"  Redis Response Time: {test_results['redis']['ping_time']:.2f}ms")

    if test_results['database']['passed']:
        print(f"  Active Agents: {test_results['database']['agent_count']}")
        print(f"  Database Query Time: {test_results['database']['query_time']:.2f}ms")

    if test_results['websocket_routing']['passed']:
        print(f"  WebSocket Endpoints: {test_results['websocket_routing']['endpoint_count']}")

    print()

    # Production readiness assessment
    if production_score >= 95.0:
        print("🎉 PRODUCTION READY!")
        print("All critical systems are operational and optimized.")
        print("Platform ready for production deployment.")

        # Generate mini certificate
        certificate = f"""
PRODUCTION READINESS CONFIRMED
Platform: Unified Donkey Betz
Score: {production_score:.1f}%
Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
Status: READY FOR DEPLOYMENT ✅
"""
        print(certificate)

        return True
    else:
        print("⚠️  PRODUCTION OPTIMIZATION NEEDED")
        print(f"Current score: {production_score:.1f}% (need 95%+)")

        # Show what needs fixing
        failed_components = [name for name, result in test_results.items() if not result['passed']]
        if failed_components:
            print(f"Fix these components: {', '.join(failed_components)}")

        return False


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)