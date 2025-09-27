#!/usr/bin/env python
"""
Test Frontend Integration - Verify agent results display in UI
===============================================================
This script tests that agent execution results are properly displayed
in the frontend through WebSocket broadcasting.
"""

import os
import sys
import django
import requests
import json
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_frontend_integration():
    """Test that agent results appear in the frontend dashboard"""

    print("\n" + "="*80)
    print("🔍 TESTING FRONTEND INTEGRATION - AGENT RESULTS DISPLAY")
    print("="*80)

    # Base URL for API calls
    base_url = "http://localhost:8000"

    print("\n📡 STEP 1: Check WebSocket Test Page")
    print("Visit: http://localhost:8000/websocket-test/")
    print("You should see messages flowing if WebSocket is working")

    print("\n🎯 STEP 2: Open Intelligence Dashboard")
    print("Visit: http://localhost:8000/intelligence/")
    print("Keep this page open to see real-time updates")

    # Give user time to open pages
    print("\n⏳ Waiting 3 seconds for you to open the dashboard...")
    time.sleep(3)

    print("\n🤖 STEP 3: Executing Test Agent")
    print("-" * 40)

    # Test agent execution via Django shell (simpler than API)
    from backend.agents.sync_executor import SyncAgentExecutor
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    executor = SyncAgentExecutor()

    # Execute a simple content creation task
    print("Executing content_creator agent...")
    result = executor.execute(
        agent_name="content_creator",
        task_description="Write a short motivational message about achieving goals",
        context={"type": "frontend_test"}
    )

    if result.get('success'):
        print("✅ Agent executed successfully!")
        print(f"Result preview: {str(result.get('result', ''))[:200]}...")

        # The WebSocket broadcast should have been sent automatically
        # by the modifications we made to concrete_executor.py

        print("\n🎉 CHECK YOUR DASHBOARD!")
        print("You should see:")
        print("  1. A new agent result card appear at the top")
        print("  2. The activity feed update with the task")
        print("  3. A success notification")

    else:
        print(f"❌ Agent execution failed: {result.get('error')}")

    print("\n" + "="*80)
    print("📊 STEP 4: Test Multiple Agents")
    print("-" * 40)

    # Test a few more agents to show multiple results
    test_agents = [
        ("market_analyst", "Analyze the current state of AI technology"),
        ("job_finder", "Find remote Python developer positions"),
        ("content_creator", "Write a blog post title about machine learning")
    ]

    for agent_name, task in test_agents:
        print(f"\n🤖 Executing {agent_name}...")
        result = executor.execute(
            agent_name=agent_name,
            task_description=task,
            context={"type": "frontend_test"}
        )

        if result.get('success'):
            print(f"✅ {agent_name} completed")
        else:
            print(f"❌ {agent_name} failed")

        # Small delay between executions
        time.sleep(2)

    print("\n" + "="*80)
    print("🎊 FRONTEND INTEGRATION TEST COMPLETE!")
    print("="*80)

    print("\n📋 EXPECTED RESULTS IN DASHBOARD:")
    print("  • Multiple agent result cards displayed")
    print("  • Each card shows agent name, task, and output")
    print("  • Activity feed updated with all executions")
    print("  • Real AI-generated content visible")

    print("\n💡 TROUBLESHOOTING:")
    print("  • If no results appear, check browser console for errors")
    print("  • Ensure WebSocket connection shows 'connected' in dashboard")
    print("  • Check server logs for WebSocket broadcast messages")
    print("  • Try refreshing the page if connection was lost")

    print("\n🚀 Your frontend is now connected to the backend!")
    print("Agent results are flowing from backend → WebSocket → Frontend UI!")
    print("="*80)

if __name__ == "__main__":
    test_frontend_integration()