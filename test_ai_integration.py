#!/usr/bin/env python
"""
Test AI Integration for Income Builder
Tests that AI providers are properly configured and working
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from content.ai_providers import AIProviderManager
from django.conf import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ai_providers():
    """Test AI provider configuration and functionality"""

    print("\n🔍 Testing AI Provider Integration...")
    print("=" * 50)

    # Check environment variables
    print("\n📋 Checking API Keys:")
    api_keys = settings.AI_PROVIDERS

    for provider, key in api_keys.items():
        if key:
            # Only show first 10 chars for security
            masked_key = key[:10] + "..." if len(key) > 10 else key
            print(f"✅ {provider}: Configured ({masked_key})")
        else:
            print(f"❌ {provider}: Not configured")

    # Initialize AI Provider Manager
    print("\n🤖 Initializing AI Provider Manager...")
    ai_manager = AIProviderManager()

    # Check available providers
    available_providers = ai_manager.get_available_providers()
    print(f"\n📦 Available providers: {available_providers}")

    if not available_providers:
        print("\n⚠️  No AI providers available!")
        print("Please configure at least one API key in your .env file:")
        print("  OPENAI_API_KEY=your-key-here")
        print("  ANTHROPIC_API_KEY=your-key-here")
        print("  GOOGLE_API_KEY=your-key-here")
        return False

    # Test content generation with each available provider
    print("\n🧪 Testing Content Generation:")
    print("-" * 40)

    test_prompt = "Create a 3-step plan to start freelance writing"

    for provider_name in available_providers:
        print(f"\n📝 Testing {provider_name}...")

        try:
            # Get available models for this provider
            models = ai_manager.get_available_models(provider_name)
            if models and models.get(provider_name):
                model_list = models[provider_name]
                # Use the first available model for testing
                test_model = model_list[0] if model_list else None

                if test_model:
                    print(f"   Using model: {test_model}")

                    # Generate content
                    result = ai_manager.generate_content(
                        provider=provider_name,
                        model=test_model,
                        system_prompt="You are a helpful assistant.",
                        user_prompt=test_prompt,
                        config={'max_tokens': 100}
                    )

                    if result.success:
                        print(f"   ✅ Success! Generated {len(result.content)} characters")
                        print(f"   Preview: {result.content[:100]}...")
                        print(f"   Cost: ${result.cost:.4f}")
                        print(f"   Time: {result.generation_time_ms}ms")
                    else:
                        print(f"   ❌ Failed: {result.error_message}")
                else:
                    print(f"   ⚠️  No models available for {provider_name}")
            else:
                print(f"   ⚠️  Could not get models for {provider_name}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Test the specific configuration used in Income Builder
    print("\n🎯 Testing Income Builder Configuration:")
    print("-" * 40)

    if 'openai' in available_providers:
        try:
            income_builder_prompt = """As an expert in AI-Assisted Content Writing, provide a comprehensive action plan for:

Task: Week 1: Research trending templates on Etsy

Please provide:
1. Detailed step-by-step instructions
2. Specific tools and platforms to use
3. Timeline and milestones
4. Success metrics to track
5. Common pitfalls to avoid
6. Real examples and case studies

Make it practical, specific, and immediately actionable."""

            result = ai_manager.generate_content(
                provider='openai',
                model='gpt-5',
                system_prompt="You are an expert business consultant and income generation specialist. Provide practical, actionable advice.",
                user_prompt=income_builder_prompt,
                config={'max_completion_tokens': 1500}
            )

            if result.success:
                print("✅ Income Builder AI integration is working!")
                print(f"   Generated {len(result.content)} characters")
                print(f"   Preview: {result.content[:200]}...")
            else:
                print(f"❌ Income Builder test failed: {result.error_message}")

        except Exception as e:
            print(f"❌ Income Builder test error: {e}")
    else:
        print("⚠️  OpenAI not available - Income Builder needs OpenAI API key")

    print("\n" + "=" * 50)
    print("Test complete!\n")

    return len(available_providers) > 0

if __name__ == "__main__":
    success = test_ai_providers()

    if not success:
        print("\n⚠️  To fix the AI integration:")
        print("1. Edit your .env file")
        print("2. Uncomment and add your OpenAI API key:")
        print("   OPENAI_API_KEY=sk-...")
        print("3. Restart your Django server")
        print("4. Run this test again\n")
        sys.exit(1)
    else:
        print("\n✅ AI Integration is working properly!\n")
        sys.exit(0)