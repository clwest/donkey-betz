# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Debug the empty RAG response issue
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

def test_ai_provider_directly():
    """Test the AI provider directly to see if it's working"""
    
    print("🧪 DEBUGGING AI PROVIDER RESPONSE")
    print("="*60)
    
    try:
        from content.ai_providers import AIProviderManager
        
        ai_manager = AIProviderManager()
        available_providers = ai_manager.get_available_providers()
        
        print(f"📊 Available providers: {available_providers}")
        
        if not available_providers:
            print("❌ No AI providers available")
            return False
            
        # Test with a simple message
        simple_message = "Hello, how are you?"
        simple_system = "You are a helpful assistant."
        
        print(f"\n🔸 Testing simple message: '{simple_message}'")
        
        result = ai_manager.generate_content(
            provider='openai',
            model='gpt-5-mini',
            system_prompt=simple_system,
            user_prompt=simple_message,
            config={'max_tokens': 100}
        )
        
        print(f"   Success: {result.success}")
        print(f"   Content: '{result.content}'")
        print(f"   Content length: {len(result.content) if result.content else 0}")
        print(f"   Error: {result.error_message}")
        print(f"   Token usage: {result.token_usage}")
        
        if not result.success:
            print(f"❌ Simple test failed")
            return False
            
        if not result.content or len(result.content.strip()) == 0:
            print(f"❌ Empty content returned")
            return False
            
        print(f"✅ Simple test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI provider: {e}")
        return False

def test_rag_context_build():
    """Test building RAG context"""
    
    print(f"\n🔸 Testing RAG context building")
    
    try:
        from core.views_assistant_rag_enhanced import RAGAssistant
        from django.contrib.auth.models import User
        
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        
        rag_assistant = RAGAssistant(user)
        
        test_query = "I am just trying to test out different parts of the system."
        context, sources = rag_assistant.build_context(test_query)
        
        print(f"   Query: '{test_query}'")
        print(f"   Sources found: {len(ources)}")
        print(f"   Context length: {len(context) if context else 0}")
        
        if sources:
            print(f"   Source titles: {[s.get('title', 'Unknown') for s in sources[:3]]}")
            
        if context:
            print(f"   Context preview: {context[:200]}...")
        else:
            print(f"   No context generated")
            
        return context, sources
        
    except Exception as e:
        print(f"❌ Error building RAG context: {e}")
        return None, []

def test_full_rag_flow():
    """Test the complete RAG flow like the assistant does"""
    
    print(f"\n🔸 Testing full RAG flow")
    
    try:
        from content.ai_providers import AIProviderManager
        from core.views_assistant_rag_enhanced import RAGAssistant
        from django.contrib.auth.models import User
        
        # Get test user
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        
        # Build context
        rag_assistant = RAGAssistant(user)
        message = "I am just trying to test out different parts of the system."
        context, sources = rag_assistant.build_context(message)
        
        print(f"   Built context with {len(ources)} sources")
        
        # Build system prompt like the assistant does
        system_prompt = f"""You are {user.username}'s personal AI assistant.

You have access to a comprehensive knowledge base with business intelligence, AI capabilities, and domain expertise.
Focus on providing helpful, accurate information based on the user's actual knowledge base and platform capabilities.

Key Platform Features:
- Advanced AI agent orchestration with 87+ specialized agents
- Multi-LLM provider integration (OpenAI, Anthropic, Google)
- RAG-powered knowledge management system
- Content creation and automation tools
- Real-time workflow orchestration
- Self-awareness and code understanding capabilities

Be helpful, accurate, and cite sources when available. Keep responses focused and actionable."""

        # Build enhanced message like the assistant does
        enhanced_message = message
        if context:
            enhanced_message = f"""Context from knowledge base:
{context}

User Question: {message}

Please answer based on the context provided above, citing sources when relevant."""
        
        print(f"   System prompt length: {len(ystem_prompt)}")
        print(f"   Enhanced message length: {len(enhanced_message)}")
        print(f"   Enhanced message preview: {enhanced_message[:300]}...")
        
        # Call AI provider
        ai_manager = AIProviderManager()
        config = {'max_tokens': 1000}
        
        result = ai_manager.generate_content(
            provider='openai',
            model='gpt-5-mini',
            system_prompt=system_prompt,
            user_prompt=enhanced_message,
            config=config
        )
        
        print(f"   Generation success: {result.success}")
        print(f"   Content length: {len(result.content) if result.content else 0}")
        print(f"   Token usage: {result.token_usage}")
        print(f"   Error: {result.error_message}")
        
        if result.content:
            print(f"   Content preview: {result.content[:200]}...")
        else:
            print(f"   ❌ EMPTY CONTENT - This is the bug!")
            
        return result
        
    except Exception as e:
        print(f"❌ Error in full RAG flow: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🐛 RAG RESPONSE DEBUGGING")
    print("="*80)
    
    # Test 1: Basic AI provider
    print("\n1️⃣ TESTING AI PROVIDER")
    basic_works = test_ai_provider_directly()
    
    # Test 2: RAG context building
    print("\n2️⃣ TESTING RAG CONTEXT")
    context, sources = test_rag_context_build()
    
    # Test 3: Full flow
    print("\n3️⃣ TESTING FULL RAG FLOW")
    full_result = test_full_rag_flow()
    
    print(f"\n" + "="*80)
    print("🔍 DEBUGGING SUMMARY")
    print("="*80)
    
    print(f"✅ Basic AI Provider: {'Working' if basic_works else 'Failed'}")
    print(f"✅ RAG Context Build: {'Working' if sources else 'Failed'}")
    print(f"✅ Full RAG Flow: {'Working' if full_result and full_result.content else 'Failed - EMPTY RESPONSE'}")
    
    if basic_works and sources and (not full_result or not full_result.content):
        print(f"\n🎯 ROOT CAUSE: The issue is in the full RAG flow!")
        print(f"   The AI provider works with simple messages")
        print(f"   RAG context is being built correctly") 
        print(f"   But the enhanced message with context is causing empty responses")
        print(f"\n💡 LIKELY CAUSES:")
        print(f"   - Context is too long for the model")
        print(f"   - Enhanced message format is confusing the model")
        print(f"   - GPT-5-mini has issues with the specific prompt structure")

if __name__ == "__main__":
    main()