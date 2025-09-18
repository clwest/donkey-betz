#!/usr/bin/env python
"""
Quick script to check LLM status and configure API keys if needed
"""

import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.llm_enforcer import LLMEnforcer

def check_llm_status():
    print("=" * 60)
    print("LLM STATUS CHECK")
    print("=" * 60)

    # Check environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')

    print(f"OpenAI API Key: {'✅ Set' if openai_key and openai_key != 'your-key-here' else '❌ Not configured'}")
    print(f"Anthropic API Key: {'✅ Set' if anthropic_key and anthropic_key != 'your-key-here' else '❌ Not configured'}")

    # Test LLMEnforcer
    print("\nTesting LLMEnforcer...")
    try:
        enforcer = LLMEnforcer()

        # Check if clients are initialized
        print(f"OpenAI Client: {'✅ Ready' if enforcer.openai_client else '❌ Not available'}")
        print(f"Anthropic Client: {'✅ Ready' if enforcer.anthropic_client else '❌ Not available'}")

        if not enforcer.openai_client and not enforcer.anthropic_client:
            print("\n⚠️  NO LLM CLIENTS AVAILABLE")
            print("This is why the Personal Assistant is using fallback responses!")
            print("\nTo fix this, set one of these environment variables:")
            print("export OPENAI_API_KEY='your-openai-key'")
            print("export ANTHROPIC_API_KEY='your-anthropic-key'")
            return False
        else:
            print("\n✅ LLM clients are available")
            return True

    except Exception as e:
        print(f"❌ Error initializing LLMEnforcer: {e}")
        return False

if __name__ == "__main__":
    llm_available = check_llm_status()

    if llm_available:
        print("\n🎉 LLM is ready! Personal Assistant should use real AI.")
    else:
        print("\n📋 Personal Assistant will use intelligent fallbacks until LLM is configured.")