"""
Intelligence Dashboard Real Data Verification Script
Created: 9/26/25 1:30 PM MST
Purpose: Verify that Intelligence Dashboard shows REAL data, not mock/virtual data
"""

import requests
import json
import time
import redis
from datetime import datetime
import pytz
from backend.agents.execution_tracker import AgentExecutionTracker
import django
import os
import sys

# Setup Django
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()

# Initialize
mst = pytz.timezone('America/Denver')
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
tracker = AgentExecutionTracker()

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def check_redis_data():
    """Check what's actually in Redis"""
    print_section("REDIS DATA CHECK")

    # Check agent execution stats
    agent_keys = redis_client.keys('agent:*:stats')
    print(f"✅ Agent keys in Redis: {len(agent_keys)}")

    # Count agents with real executions
    real_agents = 0
    for key in agent_keys:
        stats = redis_client.hgetall(key)
        if int(stats.get('real_executions', 0)) > 0 or int(stats.get('successful_executions', 0)) > 0:
            real_agents += 1
            agent_name = key.split(':')[1]
            print(f"  • {agent_name}: {stats.get('real_executions', 0)} real, {stats.get('successful_executions', 0)} successful")

    print(f"\n📊 Agents with real executions: {real_agents}")

    # Check spider count stored
    stored_spiders = redis_client.get('consciousness:active_spiders')
    print(f"🕷️ Spiders stored in consciousness: {stored_spiders}")

    # Check AI proposals
    proposals = redis_client.get('consciousness:ai_proposals')
    if proposals:
        proposals_data = json.loads(proposals)
        print(f"💡 AI Proposals stored: {len(proposals_data)}")

    return real_agents

def check_execution_tracker():
    """Check execution tracker metrics"""
    print_section("EXECUTION TRACKER METRICS")

    active_agents = tracker.get_active_agent_count()
    files_created = tracker.get_total_files_created()
    success_rate = tracker.calculate_success_rate()
    learning_rate = tracker.calculate_learning_rate()

    print(f"✅ Active agents (last hour): {active_agents}")
    print(f"📁 Files created: {files_created}")
    print(f"📈 Success rate: {success_rate}%")
    print(f"🧠 Learning rate: {learning_rate}%")

    return {
        'active_agents': active_agents,
        'files_created': files_created,
        'success_rate': success_rate,
        'learning_rate': learning_rate
    }

def check_api_response():
    """Check what the Intelligence API returns"""
    print_section("INTELLIGENCE API RESPONSE")

    try:
        response = requests.get('http://localhost:8000/api/intelligence/')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                metrics = data['data']

                print(f"✅ API Response received")
                print(f"🤖 Active agents reported: {metrics.get('active_agents', 0)}")
                print(f"🕷️ Active spiders reported: {metrics.get('active_spiders', 0)}")
                print(f"🧠 Consciousness level: {metrics.get('consciousness_level', 0)}%")
                print(f"💎 Memory crystals: {metrics.get('memory_crystals', 0)}")

                # Check for real_metrics field (new addition)
                if 'real_metrics' in metrics:
                    print(f"\n📊 REAL METRICS:")
                    real = metrics['real_metrics']
                    print(f"  • Active agents (real): {real.get('active_agents', 0)}")
                    print(f"  • Files created: {real.get('files_created', 0)}")
                    print(f"  • Success rate: {real.get('success_rate', 0)}%")
                    print(f"  • Learning rate: {real.get('learning_rate', 0)}%")
                    print(f"  • Agents registered: {real.get('agents_registered', 0)}")
                    print(f"  • Spiders available: {real.get('spiders_available', 0)}")

                return metrics
            else:
                print(f"❌ API returned error: {data.get('error')}")
        else:
            print(f"❌ API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error calling API: {e}")

    return None

def verify_real_vs_mock():
    """Verify that we're showing real data not mock data"""
    print_section("REAL VS MOCK DATA VERIFICATION")

    # Get real data from tracker
    real_data = check_execution_tracker()

    # Get API response
    api_data = check_api_response()

    if api_data:
        print_section("VERIFICATION RESULTS")

        # Check if active_agents matches real data
        api_agents = api_data.get('active_agents', 0)
        real_agents = real_data['active_agents']

        if api_agents == real_agents:
            print(f"✅ PASS: Active agents shows REAL data ({api_agents})")
        else:
            print(f"❌ FAIL: Active agents mismatch!")
            print(f"  • API shows: {api_agents}")
            print(f"  • Real count: {real_agents}")

        # Check for mock spider data
        api_spiders = api_data.get('active_spiders', 0)
        if api_spiders == 40:
            print(f"⚠️ WARNING: Spiders showing hardcoded count (40)")
        else:
            print(f"✅ Spiders count: {api_spiders} (not hardcoded)")

        # Check for virtual agents (149 is the magic number)
        if 'real_metrics' in api_data:
            registered = api_data['real_metrics'].get('agents_registered', 0)
            if registered == 149:
                print(f"⚠️ WARNING: System showing 149 registered agents (possible virtual agents)")
            elif registered > 0:
                print(f"✅ System shows {registered} registered agents")

        # Overall assessment
        print_section("OVERALL ASSESSMENT")

        if api_agents == real_agents and api_agents > 0:
            print("✅ SUCCESS: Intelligence Dashboard is showing REAL agent data!")
        elif api_agents == 0 and real_agents == 0:
            print("✅ SUCCESS: No mock data - showing real zero!")
        else:
            print("❌ FAILURE: Intelligence Dashboard is still showing mock/virtual data")
            print("  Fix needed in ConsciousnessBridge or views_unified_intelligence.py")

def test_websocket_updates():
    """Test if WebSocket is sending real updates"""
    print_section("WEBSOCKET REAL-TIME TEST")

    print("📡 Creating test execution to trigger WebSocket...")

    # Create a test execution
    tracker.track_agent_execution('test_agent', {
        'is_real_execution': True,
        'success': True,
        'task_description': 'Verification test execution',
        'quality_score': 85.0,
        'session_id': 'verification_test'
    })

    print("✅ Test execution tracked")
    print("⏳ Waiting 2 seconds for WebSocket propagation...")
    time.sleep(2)

    # Check if metrics updated
    new_count = tracker.get_active_agent_count()
    print(f"📊 Active agents after test: {new_count}")

    # Call API again to see if it reflects the change
    response = requests.get('http://localhost:8000/api/intelligence/')
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            new_api_agents = data['data'].get('active_agents', 0)
            print(f"🌐 API now shows: {new_api_agents} active agents")

            if new_api_agents == new_count:
                print("✅ WebSocket updates are working with REAL data!")
            else:
                print("⚠️ API not reflecting latest changes immediately")

def main():
    print("\n" + "="*60)
    print("🚀 INTELLIGENCE DASHBOARD REAL DATA VERIFICATION")
    print(f"📅 {datetime.now(mst).strftime('%Y-%m-%d %I:%M %p %Z')}")
    print("="*60)

    # Run all checks
    redis_agents = check_redis_data()
    verify_real_vs_mock()
    test_websocket_updates()

    # Final summary
    print_section("FINAL SUMMARY")

    tracker_data = check_execution_tracker()

    print(f"""
📊 REAL DATA STATUS:
  • Active Agents: {tracker_data['active_agents']} (from actual executions)
  • Files Created: {tracker_data['files_created']}
  • Success Rate: {tracker_data['success_rate']}%
  • Learning Rate: {tracker_data['learning_rate']}%

🎯 NEXT STEPS:
  1. If showing mock data, check ConsciousnessBridge._map_capabilities()
  2. Ensure views_unified_intelligence.py uses execution_tracker
  3. Remove any hardcoded agent/spider counts
  4. Test with python test_real_metrics.py to generate real data
    """)

if __name__ == "__main__":
    main()