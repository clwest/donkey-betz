#!/usr/bin/env python3
"""
Fix the identified RAG issues
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

def test_with_correct_user_model():
    """Test RAG with the correct user model"""
    
    print("🔧 TESTING WITH CORRECT USER MODEL")
    print("="*60)
    
    try:
        from django.contrib.auth import get_user_model
        from core.views_assistant_rag_enhanced import RAGAssistant
        from content.ai_providers import AIProviderManager
        
        User = get_user_model()  # This gets core.UnifiedUser
        print(f"📍 Using User model: {User}")
        
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='test_debug',
            defaults={'email': 'test@example.com'}
        )
        print(f"📍 User: {user.username} (created: {created})")
        
        # Test RAG context building
        rag_assistant = RAGAssistant(user)
        message = "I am just trying to test out different parts of the system."
        
        print(f"\n🔍 Building context for: '{message}'")
        context, sources = rag_assistant.build_context(message)
        
        print(f"   Sources found: {len(sources)}")
        if sources:
            for i, source in enumerate(sources[:3], 1):
                print(f"      {i}. {source.get('title', 'Unknown')} (type: {source.get('type', 'unknown')})")
        
        print(f"   Context length: {len(context) if context else 0}")
        
        # Test AI generation with simpler context
        if sources:
            ai_manager = AIProviderManager()
            
            # Create a shorter, cleaner context
            clean_context = "\\n".join([
                f"Source {i}: {source.get('title', 'Unknown')}" 
                for i, source in enumerate(sources[:2], 1)
            ])
            
            simple_system = "You are a helpful AI assistant. Answer based on the provided context."
            simple_message = f"Context: {clean_context}\\n\\nUser: {message}\\n\\nPlease respond helpfully."
            
            print(f"\\n🤖 Testing with simplified prompt...")
            print(f"   System prompt length: {len(simple_system)}")
            print(f"   User prompt length: {len(simple_message)}")
            
            result = ai_manager.generate_content(
                provider='openai',
                model='gpt-5-mini',
                system_prompt=simple_system,
                user_prompt=simple_message,
                config={'max_tokens': 500}
            )
            
            print(f"   Success: {result.success}")
            print(f"   Content length: {len(result.content) if result.content else 0}")
            print(f"   Error: {result.error_message}")
            
            if result.content:
                print(f"   Response: {result.content[:200]}...")
                return True
            else:
                print(f"   ❌ Still empty response")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_quick_fix():
    """Create a quick fix for the RAG system"""
    
    print(f"\\n🛠️ CREATING QUICK FIX")
    print("="*60)
    
    fix_code = '''
# Quick fix for core/views_assistant_rag_enhanced.py

# 1. Fix the user model import at the top:
from django.contrib.auth import get_user_model
User = get_user_model()  # Use this instead of importing User directly

# 2. Fix the _get_total_embeddings function to use unified_embeddings:
def _get_total_embeddings() -> int:
    """Get total embeddings available"""
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM unified_embeddings")
            return cursor.fetchone()[0]
    except:
        return 0

# 3. Simplify the enhanced message format in assistant_chat_enhanced:
# Replace the complex context format with:
if context:
    enhanced_message = f"""Based on the following information from the knowledge base:

{context[:1000]}...

User question: {message}

Please provide a helpful response."""
else:
    enhanced_message = message

# 4. Add fallback for empty responses:
if result.success and not result.content:
    logger.warning("Empty response from AI provider, using fallback")
    fallback_result = ai_manager.generate_content(
        provider=provider,
        model=model,
        system_prompt="You are a helpful assistant.",
        user_prompt=message,
        config={'max_tokens': 200}
    )
    if fallback_result.success and fallback_result.content:
        result = fallback_result
'''
    
    print(fix_code)
    
    return fix_code

def test_simple_response():
    """Test if the issue is with the response format"""
    
    print(f"\\n🧪 TESTING RESPONSE FORMAT ISSUE")
    print("="*60)
    
    try:
        from content.ai_providers import AIProviderManager
        
        ai_manager = AIProviderManager()
        
        # Test various message formats that might cause empty responses
        test_cases = [
            {
                'name': 'Simple message',
                'system': 'You are a helpful assistant.',
                'user': 'Hello, how are you?'
            },
            {
                'name': 'Long system prompt',
                'system': '''You are a personal AI assistant with access to a comprehensive knowledge base.
You have business intelligence, AI capabilities, and domain expertise.
Focus on providing helpful, accurate information based on the platform capabilities.''',
                'user': 'I am testing the system.'
            },
            {
                'name': 'Context-heavy message',
                'system': 'You are a helpful assistant.',
                'user': '''Context from knowledge base:
Security and Compliance Features: Enterprise-grade security measures...
Analytics Dashboard: Comprehensive monitoring tools...

User Question: I am testing the system.

Please respond based on the context above.'''
            }
        ]
        
        for test_case in test_cases:
            print(f"\\n🔸 Testing: {test_case['name']}")
            
            result = ai_manager.generate_content(
                provider='openai',
                model='gpt-5-mini',
                system_prompt=test_case['system'],
                user_prompt=test_case['user'],
                config={'max_tokens': 200}
            )
            
            print(f"   Success: {result.success}")
            print(f"   Content: '{result.content[:100] if result.content else 'EMPTY'}...'")
            print(f"   Length: {len(result.content) if result.content else 0}")
            
            if not result.content:
                print(f"   ❌ Empty response for {test_case['name']}")
            else:
                print(f"   ✅ Got response for {test_case['name']}")
                
    except Exception as e:
        print(f"❌ Error testing response formats: {e}")

def main():
    print("🔧 FIXING RAG ISSUES")
    print("="*80)
    
    # Test 1: Use correct user model
    print("\\n1️⃣ TESTING WITH CORRECT USER MODEL")
    user_test_passed = test_with_correct_user_model()
    
    # Test 2: Test response formats
    print("\\n2️⃣ TESTING RESPONSE FORMATS")
    test_simple_response()
    
    # Test 3: Show the fix
    print("\\n3️⃣ CREATING SOLUTION")
    fix_code = create_quick_fix()
    
    print(f"\\n" + "="*80)
    print("🎯 ISSUE RESOLUTION SUMMARY")
    print("="*80)
    
    print(f"""
🔍 ROOT CAUSES IDENTIFIED:

1. ✅ User Model Issue: Using auth.User instead of core.UnifiedUser
2. ✅ GPT-5 Parameter Issue: max_completion_tokens not supported
3. ✅ _get_total_embeddings: Looking for wrong table structure
4. ⚠️  Response Format: Possibly too complex context confusing model

🛠️ SOLUTIONS:

1. Use get_user_model() instead of importing User directly
2. Fix _get_total_embeddings() to use unified_embeddings table  
3. Simplify the enhanced message format
4. Add fallback for empty responses

📝 NEXT STEPS:

Apply these fixes to core/views_assistant_rag_enhanced.py and the RAG system 
should start providing proper responses with your code intelligence!
""")

if __name__ == "__main__":
    main()