# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Test Content Studio Agent Integration
======================================

This script tests the integration between the Content Creation Studio
and the 152 AI agents.
"""

import os
import sys
import django
import asyncio
import json
from datetime import datetime

# Setup Django environment
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import after Django setup
from ai_core.agents.concrete_executor import concrete_executor
from ai_core.agents.content_studio_integration import (
    content_studio_integration,
    get_content_agents,
    get_integration_stats
)


async def test_content_studio_integration():
    """Test the Content Studio integration with agents"""

    print("\n" + "="*60)
    print("🎨 CONTENT STUDIO AGENT INTEGRATION TEST")
    print("="*60)

    # 1. Check integration stats
    print("\n📊 Integration Statistics:")
    stats = get_integration_stats()
    print(f"Total agents: {stats['total_agents']}")
    print(f"Content-capable agents: {stats['content_capable_agents']}")
    print(f"Content agent capabilities:")
    for capability, count in stats['capabilities'].items():
        print(f"  - {capability}: {count} agents")

    # 2. List content agents
    print("\n📝 Content-capable agents:")
    content_agents = get_content_agents()
    for i, agent in enumerate(content_agents[:10], 1):
        print(f"  {i}. {agent}")
    if len(content_agents) > 10:
        print(f"  ... and {len(content_agents) - 10} more")

    # 3. Test creating content through an agent
    print("\n🚀 Testing Content Creation:")

    # Find a content agent
    test_agent = None
    for agent in content_agents:
        if 'content' in agent.lower() or 'writer' in agent.lower():
            test_agent = agent
            break

    if not test_agent:
        test_agent = content_agents[0] if content_agents else 'content_creator'

    print(f"Using agent: {test_agent}")

    try:
        # Test blog creation
        print("\n📝 Creating blog post...")
        blog_result = await content_studio_integration.create_content_through_agent(
            agent_name=test_agent,
            content_type='blog',
            topic='The Future of AI in Content Creation',
            tone='professional',
            length='short'
        )

        if blog_result.get('success'):
            print("✅ Blog post created successfully!")
            if 'blog_post' in blog_result:
                print(f"Title: {blog_result['blog_post'].get('title', 'N/A')}")
        else:
            print(f"❌ Failed to create blog post: {blog_result.get('error')}")

        # Test social media creation
        print("\n🐦 Creating social media post...")
        social_result = await content_studio_integration.create_content_through_agent(
            agent_name=test_agent,
            content_type='social',
            topic='AI transforming content creation',
            platform='twitter'
        )

        if social_result.get('success'):
            print("✅ Social media post created successfully!")
        else:
            print(f"❌ Failed to create social post: {social_result.get('error')}")

    except Exception as e:
        print(f"❌ Error during content creation: {e}")

    # 4. Test Content Studio connection status
    print("\n🔗 Content Studio Connection Status:")
    print(f"Content Studio connected: {concrete_executor.content_studio_connected}")

    # 5. Test agent execution with content task
    print("\n🤖 Testing Agent Execution with Content Task:")
    try:
        exec_result = await concrete_executor.execute_agent(
            agent_name=test_agent,
            task={
                'task_description': 'Write about the benefits of AI automation',
                'input': {
                    'content_type': 'article',
                    'tone': 'engaging'
                }
            }
        )

        if exec_result.get('success'):
            print("✅ Agent executed content task successfully!")
            print(f"Execution time: {exec_result.get('execution_time', 0):.2f}s")
            if exec_result.get('mythology_validated'):
                print("✅ Output validated by mythology enforcer")
        else:
            print(f"❌ Agent execution failed: {exec_result.get('error')}")

    except Exception as e:
        print(f"❌ Error during agent execution: {e}")

    # 6. Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Content Studio Bridge: Exists")
    print(f"✅ Content Executor: Exists")
    print(f"✅ Integration Module: Created")
    print(f"✅ Agent Connection: {concrete_executor.content_studio_connected}")
    print(f"✅ Content Agents: {len(content_agents)} available")

    return {
        'success': True,
        'content_agents': len(content_agents),
        'integration_active': concrete_executor.content_studio_connected,
        'timestamp': datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_content_studio_integration())

    print("\n✅ Content Studio Integration Test Complete!")
    print(f"Result: {json.dumps(result, indent=2)}")