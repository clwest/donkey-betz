#!/usr/bin/env python3
"""
Setup script for OpenAI API configuration
This will help you configure your OpenAI API key for the Command Center
"""

import os
import sys
from pathlib import Path

def setup_openai():
    print("=" * 60)
    print("🤖 COMMAND CENTER AI SETUP")
    print("=" * 60)
    print("\nTo enable the AI-powered Command Center, you need an OpenAI API key.")
    print("\n1. Get your API key from: https://platform.openai.com/api-keys")
    print("2. Create a .env file in the project root")
    print("3. Add: OPENAI_API_KEY=your-actual-key-here\n")

    env_file = Path(".env")
    env_example = Path(".env.example")

    # Create example .env file
    if not env_example.exists():
        with open(env_example, 'w') as f:
            f.write("""# AI Configuration for Command Center
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Anthropic Claude API
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Redis Configuration (already set)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=4
""")
        print(f"✅ Created {env_example} as a template")

    # Check if .env exists
    if env_file.exists():
        print(f"📁 Found existing .env file")

        # Check if OpenAI key is configured
        with open(env_file, 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY=' in content and 'your-' not in content:
                print("✅ OpenAI API key appears to be configured")
                print("\n🚀 Your Command Center should now work with AI!")
                return True
            else:
                print("⚠️ OpenAI API key not properly configured in .env")
    else:
        print(f"❌ No .env file found")

    print("\n" + "=" * 60)
    print("QUICK SETUP:")
    print("=" * 60)

    # Offer to create .env from example
    if env_example.exists() and not env_file.exists():
        response = input("\nWould you like to create .env from the template? (y/n): ")
        if response.lower() == 'y':
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print(f"✅ Created .env file. Please edit it and add your API key.")
            print(f"\n   Run: nano .env")
            print(f"   Then add your OpenAI API key")

    print("\n" + "=" * 60)
    print("TESTING WITHOUT API KEY:")
    print("=" * 60)
    print("\nThe Command Center will work with limited functionality:")
    print("• ✅ Slash commands (/help, /system status, etc.)")
    print("• ✅ Agent selection and UI")
    print("• ❌ Natural language chat (requires OpenAI API)")
    print("• ❌ AI-powered responses")

    print("\n" + "=" * 60)
    print("FREE ALTERNATIVES:")
    print("=" * 60)
    print("\nFor testing without cost:")
    print("1. Use OpenAI's free trial credits ($5-$18 worth)")
    print("2. Use local LLMs like Ollama (requires setup)")
    print("3. Use the slash commands which don't require AI")

    return False

if __name__ == "__main__":
    print("\n🔍 Checking OpenAI API configuration...\n")

    # Check current environment
    current_key = os.environ.get('OPENAI_API_KEY', '')
    if current_key and current_key != 'your-key-here':
        print("✅ OpenAI API key is already configured in environment!")
        print("\n🚀 Your Command Center is ready to use with AI!")
        sys.exit(0)

    # Run setup
    if setup_openai():
        print("\n✅ Setup complete! Restart the server to apply changes.")
    else:
        print("\n⚠️ Please configure your OpenAI API key to enable AI features.")
        print("\nFor now, you can still use the Command Center with slash commands!")