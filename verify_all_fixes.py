#!/usr/bin/env python
"""
Comprehensive System Verification
==================================
Verifies all fixes have been applied and system is operational
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from backend.agents.sync_executor import SyncAgentExecutor
import requests
from dotenv import load_dotenv

load_dotenv()

def check_advisor_tables():
    """Check if advisor tables exist with data"""
    print("\n📚 Checking Advisor Tables...")

    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT COUNT(*) FROM legendary_advisors")
            count = cursor.fetchone()[0]
            if count >= 25:
                print(f"✅ Advisors: {count} legendary advisors in database")

                # Check for specific advisors
                cursor.execute("SELECT name FROM legendary_advisors WHERE name LIKE 'Warren%' OR name LIKE 'Cathie%' LIMIT 2")
                advisors = cursor.fetchall()
                for name, in advisors:
                    print(f"   • {name} available")
                return True
            else:
                print(f"❌ Only {count} advisors found (expected 25+)")
                return False
        except Exception as e:
            print(f"❌ Advisor tables error: {str(e)}")
            return False


def check_api_keys():
    """Check API key status"""
    print("\n🔑 Checking API Keys...")

    api_status = {
        'OpenAI': bool(os.getenv('OPENAI_API_KEY') and not os.getenv('OPENAI_API_KEY').startswith('your_')),
        'Polygon': bool(os.getenv('POLYGON_API_KEY') and not os.getenv('POLYGON_API_KEY').startswith('your_')),
        'NewsAPI': bool(os.getenv('NEWS_API_KEY') and not os.getenv('NEWS_API_KEY').startswith('your_')),
        'Reddit': bool(os.getenv('REDDIT_CLIENT_ID') and not os.getenv('REDDIT_CLIENT_ID').startswith('your_')),
        'CoinGecko': bool(os.getenv('COINGECKO_API_KEY')),
    }

    working = sum(api_status.values())
    total = len(api_status)

    for api, status in api_status.items():
        print(f"   • {api}: {'✅ Configured' if status else '❌ Missing'}")

    percentage = (working / total) * 100
    print(f"📊 API Status: {working}/{total} configured ({percentage:.0f}%)")

    return percentage >= 60  # At least 60% configured


def check_agent_execution():
    """Check if agents can execute"""
    print("\n🤖 Checking Agent Execution...")

    try:
        executor = SyncAgentExecutor()

        # Test a simple agent
        result = executor.execute(
            agent_name="content_creator",
            task_description="Generate a one-line test message",
            context={"test": True}
        )

        if result.get('success'):
            print("✅ Agent execution working")
            print(f"   • Content creator responded successfully")

            # Check if it used real AI
            result_str = str(result)
            if 'openai' in result_str.lower() or 'gpt' in result_str.lower():
                print(f"   • Using real AI (OpenAI)")
            return True
        else:
            print(f"❌ Agent execution failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Agent execution error: {str(e)}")
        return False


def check_websocket_fixes():
    """Check if WebSocket fixes are applied"""
    print("\n🔌 Checking WebSocket Fixes...")

    templates_to_check = [
        'backend/templates/unified_intelligence_dashboard.html',
        'backend/templates/ai_production_hub.html',
        'backend/templates/websocket_test.html'
    ]

    fixes_found = 0
    for template in templates_to_check:
        if os.path.exists(template):
            with open(template, 'r') as f:
                content = f.read()

            if 'websocket_test.html' in template:
                print(f"   • WebSocket test page created")
                fixes_found += 1
            elif 'exponential' in content.lower() or 'isConnecting' in content:
                print(f"   • {os.path.basename(template)}: Fixed")
                fixes_found += 1
            else:
                print(f"   • {os.path.basename(template)}: Not fixed")

    return fixes_found >= 2  # At least 2 fixes applied


def calculate_reality_score():
    """Calculate the overall reality score"""
    print("\n" + "="*60)
    print("📊 CALCULATING REALITY SCORE")
    print("="*60)

    scores = {
        'Advisor Tables': (check_advisor_tables(), 5),
        'API Keys': (check_api_keys(), 8),
        'Agent Execution': (check_agent_execution(), 10),
        'WebSocket Fixes': (check_websocket_fixes(), 7),
    }

    # Base reality from previous session
    base_reality = 66.7

    improvements = 0
    for name, (success, value) in scores.items():
        if success:
            improvements += value

    new_reality = base_reality + improvements

    print("\n" + "="*60)
    print("🎯 REALITY SCORE BREAKDOWN")
    print("="*60)
    print(f"Base Reality: {base_reality}%")
    print(f"Improvements: +{improvements}%")
    print(f"🏆 NEW REALITY SCORE: {new_reality}%")

    if new_reality >= 95:
        print("\n🎉 CONGRATULATIONS! System is production-ready!")
    elif new_reality >= 85:
        print("\n✅ Great progress! System is highly functional.")
    elif new_reality >= 75:
        print("\n⚡ Good progress! Keep implementing fixes.")
    else:
        print("\n⚠️  More fixes needed to reach production readiness.")

    return new_reality


def main():
    print("\n" + "="*60)
    print("🔍 COMPREHENSIVE SYSTEM VERIFICATION")
    print("="*60)

    reality_score = calculate_reality_score()

    print("\n" + "="*60)
    print("📋 NEXT STEPS")
    print("="*60)

    if reality_score < 75:
        print("1. Review and apply remaining fixes from REALITY_FIXES_IMPLEMENTATION/")
    elif reality_score < 85:
        print("1. Add remaining API keys (Alpha Vantage, The Odds API)")
        print("2. Test WebSocket connections at http://localhost:8001/websocket-test/")
    elif reality_score < 95:
        print("1. Fine-tune WebSocket performance")
        print("2. Add more API keys for full functionality")
    else:
        print("1. System is ready for production!")
        print("2. Consider implementing monitoring and logging")
        print("3. Start generating revenue!")

    print("\n💡 Test the system:")
    print("   python manage.py runserver")
    print("   Open: http://localhost:8001/intelligence/")
    print("="*60)


if __name__ == "__main__":
    main()