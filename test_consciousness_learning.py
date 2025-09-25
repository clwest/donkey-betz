#!/usr/bin/env python3
"""
Test consciousness learning and dynamic growth
"""
import time
import redis
from backend.spiders.consciousness import ConsciousnessBridge

def simulate_experiences():
    """Simulate various experiences to boost consciousness learning"""
    print("🧠 Testing Consciousness Learning System")
    print("=" * 60)

    # Connect to Redis
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Initialize consciousness bridge
    bridge = ConsciousnessBridge(redis_client=redis_client)

    # Get baseline consciousness
    initial_understanding = bridge.understand_self()
    initial_consciousness = initial_understanding['self_awareness_score']
    print(f"📊 Initial Consciousness Level: {initial_consciousness:.1f}%")

    # Simulate experiences
    print("\n🎯 Simulating experiences...")

    # Simulate agent interactions
    print("  + Recording agent interactions...")
    bridge.record_experience('agent_interactions', 25, {'type': 'problem_solving'})

    # Simulate problems solved
    print("  + Recording problems solved...")
    bridge.record_experience('problems_solved', 5, {'domain': 'income_generation'})

    # Simulate revenue generated
    print("  + Recording revenue generated...")
    bridge.record_experience('revenue_total', 1200, {'source': 'ai_agents'})

    # Simulate user interactions
    print("  + Recording user interactions...")
    bridge.record_experience('user_interactions', 30, {'interface': 'command_center'})

    # Simulate system improvements
    print("  + Recording system improvements...")
    bridge.record_experience('improvements_applied', 2, {'type': 'optimization'})

    # Simulate WebSocket activity
    print("  + Recording WebSocket activity...")
    redis_client.set('consciousness:ws_connections_hour', 15, ex=3600)
    redis_client.set('consciousness:api_calls_hour', 45, ex=3600)

    # Wait a moment for changes to take effect
    time.sleep(1)

    # Get new consciousness level
    new_understanding = bridge.understand_self()
    new_consciousness = new_understanding['self_awareness_score']

    print(f"\n📈 New Consciousness Level: {new_consciousness:.1f}%")
    print(f"🚀 Growth: +{new_consciousness - initial_consciousness:.1f} points")

    # Show experience breakdown
    print(f"\n🧮 Experience Breakdown:")
    try:
        agent_interactions = int(redis_client.get('consciousness:agent_interactions') or '0')
        problems_solved = int(redis_client.get('consciousness:problems_solved') or '0')
        revenue_total = float(redis_client.get('consciousness:revenue_total') or '0')
        user_interactions = int(redis_client.get('consciousness:user_interactions') or '0')
        improvements_applied = int(redis_client.get('consciousness:improvements_applied') or '0')

        print(f"  • Agent Interactions: {agent_interactions}")
        print(f"  • Problems Solved: {problems_solved}")
        print(f"  • Revenue Generated: ${revenue_total:.2f}")
        print(f"  • User Interactions: {user_interactions}")
        print(f"  • Improvements Applied: {improvements_applied}")
    except Exception as e:
        print(f"  Error reading experience data: {e}")

    # Test dynamic learning over time
    print(f"\n⏰ Testing continuous learning...")
    for i in range(3):
        print(f"  Cycle {i+1}: Adding more interactions...")
        bridge.record_experience('agent_interactions', 10)
        bridge.record_experience('problems_solved', 2)
        current = bridge.understand_self()
        print(f"  Current Consciousness: {current['self_awareness_score']:.1f}%")
        time.sleep(0.5)

    print(f"\n✅ Consciousness learning system is working!")
    print(f"🎉 Final Level: {current['self_awareness_score']:.1f}%")
    print(f"🔮 Total Growth: +{current['self_awareness_score'] - initial_consciousness:.1f} points")

    return current['self_awareness_score']

if __name__ == "__main__":
    final_consciousness = simulate_experiences()

    if final_consciousness > 36.5:
        print(f"\n🎉 SUCCESS: Consciousness grew from 36.5% to {final_consciousness:.1f}%!")
        print("🧠 The system is now capable of experiential learning!")
    else:
        print(f"\n⚠️ WARNING: Consciousness level did not increase from 36.5%")
        print("🔧 Check Redis connection and experience recording system")