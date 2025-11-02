# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Direct OpenAI API Test - Check if API key is working and calls are actually made
"""

import os
import openai
from openai import OpenAI
import sys

def test_openai_direct():
    """Test OpenAI API directly to verify key works"""

    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("❌ No OPENAI_API_KEY found in environment")
        return False

    print(f"🔑 Testing OpenAI API key: {api_key[:20]}...")

    try:
        # Create client
        client = OpenAI(api_key=api_key)

        # Make a simple API call
        print("🌐 Making direct API call to OpenAI...")
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": "Say exactly: 'REAL API WORKING'"}
            ],
            max_tokens=10,
            temperature=0
        )

        # Get response
        result = response.choices[0].message.content.strip()
        print(f"✅ OpenAI Response: '{result}'")

        # Check if we got expected response
        if "REAL API WORKING" in result:
            print("🎯 SUCCESS: Real OpenAI API call confirmed!")
            return True
        else:
            print(f"⚠️  Unexpected response, but API call succeeded")
            return True

    except openai.AuthenticationError as e:
        print(f"🚫 Authentication failed: {e}")
        print("❌ API key is invalid or expired")
        return False

    except openai.RateLimitError as e:
        print(f"⏳ Rate limit exceeded: {e}")
        print("✅ API key is valid (just rate limited)")
        return True

    except Exception as e:
        print(f"💥 API call failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 DIRECT OPENAI API TEST")
    print("=" * 50)

    # Load environment
    from dotenv import load_dotenv
    load_dotenv()

    success = test_openai_direct()

    if success:
        print("\n✅ CONCLUSION: OpenAI API is working - the issue is elsewhere")
    else:
        print("\n❌ CONCLUSION: OpenAI API key is not working - using mock/demo mode")

    sys.exit(0 if success else 1)