#!/usr/bin/env python3
"""
Test Script - Verify ALL AI Components Use Real LLMs

This script tests that every component claiming to use AI
actually calls real OpenAI/Anthropic APIs.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_llm_enforcer():
    """Test the LLM enforcer directly"""
    from core.llm_enforcer import get_llm_enforcer, verify_llm_availability

    print("\n" + "="*60)
    print("🔍 TESTING LLM ENFORCER")
    print("="*60)

    # Check availability
    available = verify_llm_availability()
    if not available:
        print("❌ No LLM clients available! Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return False

    # Test generation
    enforcer = get_llm_enforcer()
    result = enforcer.enforce_real_ai(
        prompt="Say 'Hello from the real AI system' and include the current timestamp",
        agent_name="TestScript",
        task_type="general",
        max_tokens=50
    )

    if result['success']:
        print(f"✅ LLM Enforcer working!")
        print(f"   Provider: {result['provider']}")
        print(f"   Model: {result['model']}")
        print(f"   Response: {result['response'][:100]}...")
        print(f"   Tokens: {result['tokens']}")
        print(f"   Cost: ${result['cost']:.4f}")
        return True
    else:
        print(f"❌ LLM Enforcer failed: {result['error']}")
        return False


async def test_job_application_agent():
    """Test that job application agent uses real AI"""
    from ai_core.agents.job_application_agent import JobApplicationAgent

    print("\n" + "="*60)
    print("🔍 TESTING JOB APPLICATION AGENT")
    print("="*60)

    agent = JobApplicationAgent()

    # Test cover letter generation
    opportunity = {
        'title': 'Senior Python Developer',
        'company': 'TechCorp AI',
        'description': 'We need a Python expert for AI/ML projects',
        'salary': '$120k-150k'
    }

    applicant_info = {
        'name': 'Test User',
        'email': 'test@example.com',
        'skills': ['Python', 'Machine Learning', 'Django'],
        'years_experience': 5
    }

    try:
        cover_letter = agent._generate_cover_letter(opportunity, applicant_info)

        # Check if it's real AI (not template)
        if "I am writing to express my strong interest" in cover_letter and \
           "Key qualifications that make me an ideal candidate:" in cover_letter:
            print("❌ Job Application Agent is still using TEMPLATE!")
            return False
        else:
            print("✅ Job Application Agent generated UNIQUE cover letter")
            print(f"   Preview: {cover_letter[:200]}...")
            return True

    except Exception as e:
        print(f"⚠️ Job Application Agent error: {e}")
        return False


async def test_content_marketplace_agent():
    """Test that content marketplace agent uses real AI"""
    from ai_core.agents.content_marketplace_agent import ContentMarketplaceAgent

    print("\n" + "="*60)
    print("🔍 TESTING CONTENT MARKETPLACE AGENT")
    print("="*60)

    agent = ContentMarketplaceAgent()

    content = {
        'title': 'AI Revolution in Healthcare',
        'type': 'Blog Post',
        'word_count': 1500,
        'keywords': ['AI', 'healthcare', 'innovation'],
        'value': 150
    }

    try:
        description = agent._create_product_description(content)

        # Check if it's real AI (not template)
        if "🎯 AI Revolution in Healthcare" in description and \
           "✨ What You Get:" in description and \
           "💎 Perfect For:" in description:
            print("❌ Content Marketplace Agent is still using TEMPLATE!")
            return False
        else:
            print("✅ Content Marketplace Agent generated UNIQUE description")
            print(f"   Preview: {description[:200]}...")
            return True

    except Exception as e:
        print(f"⚠️ Content Marketplace Agent error: {e}")
        return False


async def test_real_content_creator():
    """Test that real content creator uses OpenAI"""
    from ai_core.agents.real_content_creator import RealContentCreatorAgent

    print("\n" + "="*60)
    print("🔍 TESTING REAL CONTENT CREATOR")
    print("="*60)

    agent = RealContentCreatorAgent()

    try:
        # Test blog post creation
        result = agent.create_blog_post(
            topic="The Future of Remote Work",
            keywords=["remote", "productivity"],
            word_count=100  # Small for testing
        )

        if result.get('success'):
            print("✅ Real Content Creator generated content")
            print(f"   Words: {result['word_count']}")
            print(f"   Value: ${result['value']}")
            print(f"   Preview: {result['content'][:150]}...")
            return True
        else:
            print(f"❌ Real Content Creator failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"⚠️ Real Content Creator error: {e}")
        return False


# test_job_orchestrator removed in Session 1086 PR 2:
# ai_core.agents.job_application_orchestrator was deleted as confirmed-orphan
# (zero production callers, stale core.agents.registry import path).


async def test_ai_enforced_base():
    """Test the AI enforced base class"""
    from ai_core.agents.ai_enforced_base import ExampleConvertedAgent

    print("\n" + "="*60)
    print("🔍 TESTING AI ENFORCED BASE CLASS")
    print("="*60)

    agent = ExampleConvertedAgent("TestEnforcedAgent")

    try:
        result = await agent.execute("Generate a creative tagline for an AI company")

        if result['success']:
            print("✅ AI Enforced Agent working")
            print(f"   Response: {result['response'][:100]}...")
            print(f"   Stats: {result['stats']}")

            # Verify AI was actually used
            if agent.verify_ai_usage():
                print("   ✅ Verified: Agent used real AI")
                return True
            else:
                print("   ❌ Agent did NOT use real AI")
                return False
        else:
            print(f"❌ AI Enforced Agent failed")
            return False

    except Exception as e:
        print(f"⚠️ AI Enforced Agent error: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🚀 TESTING REAL AI PIPELINE - ENSURING 100% REAL LLM USAGE")
    print("="*80)
    print(f"Started at: {datetime.now()}")

    # Check environment
    openai_key = os.getenv('OPENAI_API_KEY', '')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')

    print("\n📋 Environment Check:")
    print(f"   OpenAI API Key: {'✅ Set' if openai_key and openai_key != 'your-key-here' else '❌ Not set'}")
    print(f"   Anthropic API Key: {'✅ Set' if anthropic_key and anthropic_key != 'your-key-here' else '❌ Not set'}")

    if not openai_key and not anthropic_key:
        print("\n❌ CRITICAL: No API keys configured!")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        return

    # Run tests
    results = {
        'LLM Enforcer': await test_llm_enforcer(),
        'Job Application Agent': await test_job_application_agent(),
        'Content Marketplace Agent': await test_content_marketplace_agent(),
        'Real Content Creator': await test_real_content_creator(),
        'AI Enforced Base': await test_ai_enforced_base()
    }

    # Summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for component, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {component}: {status}")

    print("\n" + "="*80)
    if passed == total:
        print(f"🎉 SUCCESS: All {total} components using REAL AI!")
        print("   The system is now 100% powered by real LLMs")
    else:
        print(f"⚠️ PARTIAL: {passed}/{total} components using real AI")
        print(f"   {total - passed} components still need to be fixed")

    print(f"\nCompleted at: {datetime.now()}")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())