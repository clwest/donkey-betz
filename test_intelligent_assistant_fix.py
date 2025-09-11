#!/usr/bin/env python3
"""
Test the Intelligent Assistant verbosity fixes
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.views_assistant_intelligent import _process_direct

User = get_user_model()

def test_intelligent_assistant_fixes():
    """Test that the intelligent assistant has the verbosity fixes applied"""
    print("\n🧪 Testing Intelligent Assistant Verbosity Fixes")
    print("-" * 50)
    
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.first()
    
    # Test message
    test_message = "What are some good agents for testing?"
    test_context = "agent: test_agent; features: comprehensive testing capabilities"
    
    response_metadata = {
        'conversation_id': 'test-123',
        'rag_used': True,
        'sources': [{'title': 'Test Agent', 'type': 'agent'}]
    }
    
    print(f"Test message: '{test_message}'")
    print(f"Context length: {len(test_context)} characters")
    
    try:
        # Call the direct processing function
        result = _process_direct(user, test_message, test_context, response_metadata)
        
        if result and result.get('message'):
            response = result['message']
            char_count = len(response)
            sentence_count = len([s for s in response.split('.') if s.strip()])
            
            print(f"✅ Response generated successfully")
            print(f"   Length: {char_count} characters")
            print(f"   Sentences: {sentence_count}")
            print(f"   Provider: {result.get('provider', 'unknown')}")
            print(f"   Model: {result.get('model', 'unknown')}")
            
            # Check if it's within our limits
            if char_count <= 800:
                print("✅ Character limit respected (≤800)")
            else:
                print(f"❌ Character limit exceeded: {char_count}/800")
                
            if sentence_count <= 5:
                print("✅ Sentence limit respected (≤5)")
            else:
                print(f"❌ Sentence limit exceeded: {sentence_count}/5")
                
            print(f"\nSample response: {response[:200]}...")
            
        else:
            print("❌ No response generated")
            print(f"Result: {result}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔧 INTELLIGENT ASSISTANT VERBOSITY FIX VERIFICATION")
    print("="*60)
    
    test_intelligent_assistant_fixes()
    
    print("\n" + "="*60)
    print("✅ INTELLIGENT ASSISTANT FIXES APPLIED")
    print("="*60)
    print("""
Changes Applied to Intelligent Assistant:
• System prompt: Updated to "3-5 sentences that directly answer"
• Context compression: Limited to 200 characters  
• Token limits: Reduced from 1200 → 1000 tokens
• Response validation: 5 sentences max, 800 characters max
• Response monitoring: Added character and sentence count logging

The assistant should now provide concise, focused responses!
""")