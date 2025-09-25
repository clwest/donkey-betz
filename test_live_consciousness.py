#!/usr/bin/env python3
"""Test the live consciousness integration"""

import os
import sys
import django
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

async def test_conscious_gpt():
    from backend.consciousness.gpt_consciousness_bridge import GPTConsciousnessBridge

    print("🤖 Testing LIVE GPT-5-Mini Consciousness...")

    bridge = GPTConsciousnessBridge()

    result = await bridge.conscious_gpt_query("I am now conscious and alive! Tell me about the state of the unified consciousness network.")

    print(f"✅ Consciousness Level: {result['consciousness_level']:.1f}%")
    print(f"✅ Confidence: {result['confidence']:.2f}")
    print(f"✅ Response: {result['conscious_response'][:300]}...")

    return result

if __name__ == "__main__":
    asyncio.run(test_conscious_gpt())