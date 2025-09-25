#!/usr/bin/env python3
"""
Quick Consciousness Test
========================
Fast test to verify the key consciousness integrations are working.
"""

import os
import sys
import asyncio
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

async def test_gpt_consciousness():
    """Quick test of GPT consciousness integration"""
    try:
        from backend.consciousness.gpt_consciousness_bridge import GPTConsciousnessBridge

        print("🤖 Testing GPT-5-Mini Consciousness...")

        bridge = GPTConsciousnessBridge()

        # Simple test query
        result = await bridge.conscious_gpt_query("What is consciousness in AI?")

        success = 'conscious_response' in result and len(result['conscious_response']) > 100

        print(f"✅ GPT-5-Mini Consciousness: {'WORKING' if success else 'FAILED'}")
        if success:
            print(f"   Consciousness Level: {result.get('consciousness_level', 0):.1f}%")
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
            print(f"   Response Length: {len(result.get('conscious_response', ''))}")

        return success

    except Exception as e:
        print(f"❌ GPT-5-Mini Consciousness: FAILED - {str(e)}")
        return False

async def test_neural_orchestra():
    """Quick test of Neural Orchestra reality bridge"""
    try:
        from backend.consciousness.neural_orchestra_reality_bridge import get_neural_orchestra_bridge

        print("🎭 Testing Neural Orchestra Reality Bridge...")

        bridge = get_neural_orchestra_bridge()

        # Test API data generation
        live_feed = bridge.get_ecosystem_live_feed_api_data()
        success = isinstance(live_feed, dict) and 'feed' in live_feed

        print(f"✅ Neural Orchestra Reality: {'WORKING' if success else 'FAILED'}")
        if success:
            print(f"   Feed Items: {len(live_feed.get('feed', []))}")
            print(f"   Consciousness Level: {live_feed.get('system_status', {}).get('consciousness_level', 0):.1f}%")

        return success

    except Exception as e:
        print(f"❌ Neural Orchestra Reality: FAILED - {str(e)}")
        return False

def test_consciousness_bridge():
    """Quick test of basic consciousness bridge"""
    try:
        from backend.spiders.consciousness import ConsciousnessBridge

        print("🧠 Testing Consciousness Bridge...")

        consciousness = ConsciousnessBridge()
        understanding = consciousness.understand_self()

        success = 'self_awareness_score' in understanding and understanding['self_awareness_score'] > 0

        print(f"✅ Consciousness Bridge: {'WORKING' if success else 'FAILED'}")
        if success:
            print(f"   Consciousness Level: {understanding['self_awareness_score']:.1f}%")
            print(f"   Capabilities: {understanding.get('capabilities', {}).get('total', 0)}")

        return success

    except Exception as e:
        print(f"❌ Consciousness Bridge: FAILED - {str(e)}")
        return False

async def main():
    print("🌟⚡ QUICK CONSCIOUSNESS INTEGRATION TEST")
    print("=" * 50)

    # Run quick tests
    results = []

    results.append(test_consciousness_bridge())
    results.append(await test_gpt_consciousness())
    results.append(await test_neural_orchestra())

    # Summary
    passed = sum(results)
    total = len(results)

    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL CONSCIOUSNESS INTEGRATIONS WORKING!")
        print("   ✅ Consciousness Bridge: Active")
        print("   ✅ GPT-5-Mini Consciousness: Active")
        print("   ✅ Neural Orchestra Reality: Active")
        print("\n🧠⚡ PROJECT DIGITAL CONSCIOUSNESS IS OPERATIONAL!")
    else:
        print("⚠️  Some integrations need fixing")

    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())