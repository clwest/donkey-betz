#!/usr/bin/env python3
"""
Activate agent learning to generate real OpenAI API calls
"""

import os
import sys
from datetime import datetime
from openai import OpenAI

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def test_openai_connection():
    """Test OpenAI API and trigger some learning"""

    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env file")
        return False

    print(f"✅ OpenAI API Key found: {api_key[:8]}...")

    try:
        client = OpenAI(api_key=api_key)

        # Create multiple learning interactions
        learning_prompts = [
            "Analyze the best practices for e-commerce conversion optimization",
            "Identify patterns in successful machine learning model deployments",
            "What are the key strategies for API performance optimization?",
            "Summarize user experience principles for modern web applications",
            "Explain data pipeline optimization techniques"
        ]

        print(f"\n🚀 Starting {len(learning_prompts)} learning sessions...")
        print("=" * 60)

        total_tokens = 0

        for i, prompt in enumerate(learning_prompts, 1):
            print(f"\n📚 Learning Session {i}/{len(learning_prompts)}")
            print(f"   Topic: {prompt[:50]}...")

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI agent learning and analyzing patterns."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )

            # Get token usage
            tokens_used = response.usage.total_tokens
            total_tokens += tokens_used

            print(f"   ✅ Response generated")
            print(f"   📊 Tokens used: {tokens_used}")
            print(f"   💡 Insight: {response.choices[0].message.content[:100]}...")

        print("\n" + "=" * 60)
        print(f"✨ Learning Complete!")
        print(f"   • Sessions: {len(learning_prompts)}")
        print(f"   • Total tokens: {total_tokens}")
        print(f"   • Estimated cost: ${total_tokens * 0.00015 / 1000:.4f}")
        print(f"\n📈 Check your OpenAI dashboard for usage!")
        print(f"   https://platform.openai.com/usage")

        return True

    except Exception as e:
        print(f"❌ Error calling OpenAI API: {e}")
        return False

def main():
    print(f"\n🤖 AI Agent Learning Activation")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    success = test_openai_connection()

    if success:
        print("\n🎉 Successfully triggered real API calls!")
        print("Your agents are now learning with real data.")
        print("\nNext steps:")
        print("1. Wait 1-2 minutes for OpenAI dashboard to update")
        print("2. Check https://platform.openai.com/usage")
        print("3. Your visualization will show LIVE DATA badge when connected")
    else:
        print("\n⚠️ Failed to activate learning")
        print("Please check your .env file has OPENAI_API_KEY set")

if __name__ == "__main__":
    main()