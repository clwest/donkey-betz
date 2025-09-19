#!/usr/bin/env python3
"""
Test AI provider directly to diagnose the empty response issue
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

def test_openai_directly():
    """Test OpenAI API directly"""
    
    print("🔍 TESTING OPENAI DIRECTLY")
    print("="*60)
    
    try:
        from content.ai_providers import OpenAIProvider
        from django.conf import settings
        
        # Get API key - try different methods
        api_key = None
        
        # Method 1: From settings
        if hasattr(settings, 'AI_PROVIDERS'):
            api_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY')
        
        # Method 2: From environment
        if not api_key:
            api_key = os.environ.get('OPENAI_API_KEY')
        
        # Method 3: Read from .env file directly
        if not api_key:
            with open('/Users/donkeyking/development/unified-donkey-betz/.env', 'r') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY=') and 'sk-' in line:
                        api_key = line.split('=', 1)[1].strip().strip('"')
                        if api_key and not line.startswith('#'):
                            break
        
        if not api_key:
            print("❌ No API key found")
            return False
            
        print(f"✅ API key found: {api_key[:20]}...")
        
        # Test with the provider
        provider = OpenAIProvider(api_key)
        
        # Test different prompts
        test_cases = [
            {
                'name': 'Simple test',
                'system': 'You are a helpful assistant.',
                'user': 'Say "Hello, I am working!"',
                'model': 'gpt-5-mini'
            },
            {
                'name': 'RAG-style prompt',
                'system': 'You are a helpful assistant with knowledge base access.',
                'user': '''Based on the following information from the knowledge base:

Source 1: Security features include authentication and encryption.

User question: Tell me about security.

Please provide a helpful response.''',
                'model': 'gpt-5-mini'
            }
        ]
        
        for test in test_cases:
            print(f"\n📝 Test: {test['name']}")
            print(f"   Model: {test['model']}")
            
            result = provider.generate_content(
                model=test['model'],
                system_prompt=test['system'],
                user_prompt=test['user'],
                config={'max_tokens': 200}
            )
            
            print(f"   Success: {result.success}")
            print(f"   Content: '{result.content[:100] if result.content else 'EMPTY'}'")
            print(f"   Content length: {len(result.content) if result.content else 0}")
            print(f"   Token usage: {result.token_usage}")
            print(f"   Error: {result.error_message}")
            
            if not result.content or len(result.content.strip()) == 0:
                print(f"   ❌ EMPTY RESPONSE DETECTED!")
                
                # Try to debug the raw response
                print(f"\n   🔍 Debugging raw API call...")
                try:
                    import openai
                    openai.api_key = api_key
                    client = openai.OpenAI(api_key=api_key)
                    
                    raw_response = client.chat.completions.create(
                        model=test['model'],
                        messages=[
                            {"role": "system", "content": test['system']},
                            {"role": "user", "content": test['user']}
                        ],
                        max_completion_tokens=100
                    )
                    
                    print(f"   Raw response type: {type(raw_response)}")
                    print(f"   Has choices: {hasattr(raw_response, 'choices')}")
                    if hasattr(raw_response, 'choices') and raw_response.choices:
                        choice = raw_response.choices[0]
                        print(f"   Choice type: {type(choice)}")
                        print(f"   Has message: {hasattr(choice, 'message')}")
                        if hasattr(choice, 'message'):
                            msg = choice.message
                            print(f"   Message type: {type(msg)}")
                            print(f"   Message content: '{msg.content}'")
                            print(f"   Message dict: {msg.model_dump() if hasattr(msg, 'model_dump') else 'N/A'}")
                    
                except Exception as e:
                    print(f"   Raw call error: {e}")
                    
            else:
                print(f"   ✅ Got response!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🐛 DIAGNOSING EMPTY RESPONSE ISSUE")
    print("="*80)
    
    test_openai_directly()
    
    print(f"\n" + "="*80)
    print("🔍 DIAGNOSIS COMPLETE")

if __name__ == "__main__":
    main()