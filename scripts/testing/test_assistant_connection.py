#!/usr/bin/env python
"""
Test Assistant Connection and Self-Awareness Integration
=========================================================

This script tests if the Personal Assistant is properly using
the self-awareness integration.
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize Django
django.setup()

def test_direct_integration():
    """Test the integration directly without HTTP"""
    print("\n" + "="*60)
    print("1. TESTING DIRECT INTEGRATION")
    print("="*60)

    from core.personal_assistant_integration import personal_assistant_integration

    # Test basic context enhancement
    context = personal_assistant_integration.enhance_assistant_context(
        message="What's the system status?",
        conversation_id="test_direct"
    )

    print(f"✓ System Awareness: {context['system_awareness']['platform_reality']}")
    print(f"✓ Operational: {context['system_awareness']['operational_percentage']}%")
    print(f"✓ Real Components: {', '.join(context['system_awareness']['real_components'][:3]) if context['system_awareness']['real_components'] else 'None'}")
    print(f"✓ Mock Components: {', '.join(context['system_awareness']['mock_components'][:3]) if context['system_awareness']['mock_components'] else 'None'}")
    print(f"✓ Recommendations: {len(context['recommendations'])} generated")

    return context


def test_django_view():
    """Test the Django view directly"""
    print("\n" + "="*60)
    print("2. TESTING DJANGO VIEW DIRECTLY")
    print("="*60)

    from django.test import RequestFactory
    from django.contrib.auth import get_user_model
    from core.views_assistant_intelligent import assistant_chat_intelligent as assistant_chat

    # Create a test request
    factory = RequestFactory()
    User = get_user_model()

    # Get or create test user
    try:
        user = User.objects.get(username='test_user')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='REDACTED'
        )

    # Create request with self-awareness enabled
    request = factory.post('/api/v1/assistant/chat/',
        data=json.dumps({
            'message': 'What is the system status?',
            'conversation_id': 'test_view',
            'use_self_awareness': True
        }),
        content_type='application/json'
    )
    request.user = user
    request.data = json.loads(request.body or b"{}")

    # Call the view
    try:
        response = assistant_chat(request)

        if hasattr(response, 'data'):
            data = response.data
        else:
            data = json.loads(response.content)

        print(f"✓ Response received")
        print(f"✓ Message: {data.get('message', 'No message')[:100]}...")

        if 'system_awareness' in data:
            print(f"✓ System Awareness PRESENT!")
            print(f"  - Operational: {data['system_awareness'].get('operational_percentage', 0)}%")
            print(f"  - Recommendations: {len(data['system_awareness'].get('recommendations', []))}")
        else:
            print(f"✗ System Awareness MISSING from response")
            print(f"  Response keys: {list(data.keys())}")

        return data

    except Exception as e:
        print(f"✗ Error calling view: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_http_endpoint():
    """Test the HTTP endpoint"""
    print("\n" + "="*60)
    print("3. TESTING HTTP ENDPOINT")
    print("="*60)

    # Start server if not running
    print("Note: Make sure Django server is running on port 8000")

    url = "http://localhost:8000/api/v1/assistant/chat/"

    # Try to get auth token
    try:
        # First try to login to get token
        login_response = requests.post(
            "http://localhost:8000/api/auth/login/",
            json={"username": "test_user", "password": "testpass123"}
        )

        if login_response.status_code == 200:
            token = login_response.json().get('token')
            headers = {'Authorization': f'Token {token}'}
        else:
            print("✗ Could not authenticate, trying without auth")
            headers = {}
    except:
        headers = {}

    payload = {
        'message': 'What is the system status?',
        'conversation_id': 'test_http',
        'use_self_awareness': True,
        'use_personal_assistant': True
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(f"✓ HTTP Response received")
            print(f"✓ Message: {data.get('message', 'No message')[:100]}...")

            if 'system_awareness' in data:
                print(f"✓ System Awareness PRESENT in HTTP response!")
                awareness = data['system_awareness']
                print(f"  - Operational: {awareness.get('operational_percentage', 0)}%")
                print(f"  - Recommendations: {awareness.get('recommendations', [])}")
            else:
                print(f"✗ System Awareness MISSING from HTTP response")
                print(f"  Response keys: {list(data.keys())}")
        else:
            print(f"✗ HTTP Error {response.status_code}: {response.text[:200]}")

    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Is it running?")
    except Exception as e:
        print(f"✗ HTTP Error: {e}")


def check_ai_provider_config():
    """Check if AI providers are configured"""
    print("\n" + "="*60)
    print("4. CHECKING AI PROVIDER CONFIGURATION")
    print("="*60)

    from content.ai_providers import AIProviderManager

    try:
        ai_manager = AIProviderManager()
        providers = ai_manager.get_available_providers()

        if providers:
            print(f"✓ AI Providers available: {', '.join(providers)}")
        else:
            print("✗ No AI providers configured")
            print("  Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_AI_API_KEY")

        return providers
    except Exception as e:
        print(f"✗ Error checking providers: {e}")
        return []


def main():
    print("\n" + "🤖 "*20)
    print("PERSONAL ASSISTANT CONNECTION & SELF-AWARENESS TEST")
    print("🤖 "*20)

    # Test 1: Direct integration
    direct_context = test_direct_integration()

    # Test 2: Django view
    view_response = test_django_view()

    # Test 3: HTTP endpoint
    test_http_endpoint()

    # Test 4: AI Provider config
    providers = check_ai_provider_config()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if direct_context:
        print("✅ Direct integration works")
    else:
        print("❌ Direct integration failed")

    if view_response and 'system_awareness' in view_response:
        print("✅ Django view includes self-awareness")
    else:
        print("❌ Django view missing self-awareness")

    if providers:
        print("✅ AI providers configured")
    else:
        print("⚠️  No AI providers - using mock responses")

    print("\n📋 Diagnosis:")
    if direct_context and not (view_response and 'system_awareness' in view_response):
        print("  Integration works but not reaching the view layer.")
        print("  Check: Is use_self_awareness flag being passed?")
    elif not direct_context:
        print("  Integration itself has issues.")
        print("  Check: Reality checker and component status.")

    print("\n🔧 Next Steps:")
    print("  1. Ensure Django server is running: make run-dev")
    print("  2. Check browser console for errors")
    print("  3. Verify frontend is sending use_self_awareness: true")
    print("  4. Check Django logs for any exceptions")


if __name__ == "__main__":
    main()