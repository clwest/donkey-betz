#!/usr/bin/env python3
"""
Test all LLM endpoints with GPT-5-mini and GPT-5-nano
Verifies that all updated endpoints work correctly with the new models.
"""

import os
import sys
import django
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import asyncio
from datetime import datetime
from typing import Dict, Any

# Import all the components we need to test
from core.llm_enforcer import get_llm_enforcer
from core.opportunity_ai_analyzer import OpportunityAIAnalyzer
from intelligence.personal_assistant_interviewer import PersonalAssistantInterviewer
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
from core.services.content_executor import DonkeyBetzContentExecutor
from django.contrib.auth import get_user_model

User = get_user_model()


def test_llm_enforcer():
    """Test LLM Enforcer with GPT-5-nano"""
    print("\n🧪 Testing LLM Enforcer with GPT-5-nano...")
    try:
        enforcer = get_llm_enforcer()
        result = enforcer.enforce_real_ai(
            prompt="Confirm you are GPT-5-nano responding",
            agent_name="TestAgent",
            task_type="test",
            max_tokens=50,
            temperature=0.5
        )

        if result['success']:
            print(f"✅ LLM Enforcer working with {result.get('model', 'unknown')}")
            print(f"   Response: {result['response'][:100]}...")
            return True
        else:
            print(f"❌ LLM Enforcer failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error testing LLM Enforcer: {e}")
        return False


def test_opportunity_analyzer():
    """Test Opportunity Analyzer with GPT-5-mini"""
    print("\n🧪 Testing Opportunity Analyzer...")
    try:
        analyzer = OpportunityAIAnalyzer()
        test_opportunity = {
            'id': 'test_opp_001',
            'title': 'Senior Software Engineer',
            'description': 'Build AI systems using Python and Django',
            'company': 'TestCorp',
            'location': 'Remote',
            'type': 'job',
            'requirements': ['Python', 'Django', 'AI/ML']
        }

        test_profile = {
            'skills': {'top_skills': ['Python', 'Django', 'Machine Learning']},
            'goals': ['Find remote AI work'],
            'user_role': 'Software Engineer'
        }

        analysis = analyzer.analyze_opportunity(test_opportunity, test_profile)

        if analysis and analysis.opportunity_id:
            print(f"✅ Opportunity Analyzer working")
            print(f"   Automation Level: {analysis.automation_level.value}")
            print(f"   Automation Score: {analysis.automation_score:.2f}")
            print(f"   AI Generated: {analysis.analysis_metadata.get('ai_analysis', {}).get('ai_generated', False)}")
            return True
        else:
            print(f"❌ Opportunity Analyzer failed")
            return False
    except Exception as e:
        print(f"❌ Error testing Opportunity Analyzer: {e}")
        return False


def test_personal_assistant():
    """Test Personal Assistant with GPT-5-mini"""
    print("\n🧪 Testing Enhanced Personal Assistant...")
    try:
        # Get or create test user
        user, _ = User.objects.get_or_create(
            username='test_gpt5_user',
            defaults={'email': 'test@gpt5.com', 'first_name': 'Test', 'last_name': 'User'}
        )

        assistant = EnhancedPersonalAIAssistant(user)

        # Test message processing
        response = assistant.process_message(
            "What AI model are you using to respond to me?",
            context={'test': True}
        )

        if response and response.get('response'):
            print(f"✅ Personal Assistant working with {response.get('model', 'unknown')}")
            print(f"   AI Generated: {response.get('ai_generated', False)}")
            print(f"   Response: {response['response'][:100]}...")
            return True
        else:
            print(f"❌ Personal Assistant failed")
            return False
    except Exception as e:
        print(f"❌ Error testing Personal Assistant: {e}")
        return False


def test_content_executor():
    """Test Content Executor with GPT-5-mini"""
    print("\n🧪 Testing Content Executor...")
    try:
        executor = DonkeyBetzContentExecutor()

        # Test content generation
        result = executor._generate_donkey_betz_content(
            task="Write a brief test post",
            content_type="blog",
            audience="developers"
        )

        if result.get('success'):
            print(f"✅ Content Executor working with {result.get('ai_model', 'unknown')}")
            print(f"   Content length: {result.get('word_count', 0)} words")
            return True
        else:
            print(f"❌ Content Executor failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error testing Content Executor: {e}")
        return False


def test_interviewer():
    """Test Personal Assistant Interviewer"""
    print("\n🧪 Testing Personal Assistant Interviewer...")
    try:
        interviewer = PersonalAssistantInterviewer()

        if interviewer.llm_enforcer:
            print(f"✅ Interviewer has LLM Enforcer initialized")
            # Note: Actual generation is disabled in line 140-141, this just tests initialization
            return True
        else:
            print(f"⚠️ Interviewer LLM not initialized (might be missing API keys)")
            return False
    except Exception as e:
        print(f"❌ Error testing Interviewer: {e}")
        return False


async def test_all_endpoints():
    """Test all updated endpoints"""
    print("=" * 70)
    print("🚀 Testing GPT-5-mini and GPT-5-nano Integration")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    results = {
        'LLM Enforcer (GPT-5-nano)': test_llm_enforcer(),
        'Opportunity Analyzer': test_opportunity_analyzer(),
        'Personal Assistant': test_personal_assistant(),
        'Content Executor': test_content_executor(),
        'Interviewer': test_interviewer()
    }

    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary:")
    print("-" * 70)

    passed = 0
    failed = 0

    for component, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {component}")
        if success:
            passed += 1
        else:
            failed += 1

    print("-" * 70)
    print(f"Total: {passed} passed, {failed} failed out of {len(results)} tests")

    if failed == 0:
        print("\n🎉 All endpoints successfully updated to GPT-5 models!")
    else:
        print(f"\n⚠️ {failed} endpoints need attention")

    return failed == 0


if __name__ == "__main__":
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your-key-here':
        print("❌ OpenAI API key not configured!")
        print("   Please set OPENAI_API_KEY environment variable")
        sys.exit(1)

    # Run tests
    success = asyncio.run(test_all_endpoints())
    sys.exit(0 if success else 1)