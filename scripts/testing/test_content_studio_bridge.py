#!/usr/bin/env python3
"""
Test script for Content Studio Bridge
Verifies that agents can access and use the Content Creation Studio
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.content_studio_bridge import (
    ContentStudioBridge,
    AgentContentCreator,
    agent_create_blog,
    agent_create_social,
    agent_create_image,
    agent_create_campaign
)
from core.models.agents_registry import UnifiedAgentTemplate


def test_content_studio_connection():
    """Test basic Content Studio connection"""
    print("\n" + "="*60)
    print("TESTING CONTENT STUDIO BRIDGE")
    print("="*60)

    # Get content agents
    content_agents = UnifiedAgentTemplate.objects.filter(name__icontains='content')
    print(f"\n✅ Found {content_agents.count()} content agents")

    # Get the main content agent
    agent = AgentContentCreator.get_content_agent()
    if agent:
        print(f"✅ Primary content agent: {agent.name}")
        print(f"   Description: {agent.description[:100]}...")
    else:
        print("❌ No content agent found")
        return False

    return True


def test_blog_creation():
    """Test blog post creation through the bridge"""
    print("\n" + "-"*40)
    print("Testing Blog Creation")
    print("-"*40)

    result = agent_create_blog(
        topic="How AI Agents Can Transform Content Creation",
        tone="professional",
        length="medium"
    )

    if result.get('success'):
        blog = result.get('blog_post', {})
        print(f"✅ Blog created successfully!")
        print(f"   Title: {blog.get('title')}")
        print(f"   Word count: {blog.get('metadata', {}).get('word_count', 'Unknown')}")
        print(f"   Status: {blog.get('status')}")
        return True
    else:
        print(f"❌ Blog creation failed: {result.get('error')}")
        return False


def test_social_media_creation():
    """Test social media post creation"""
    print("\n" + "-"*40)
    print("Testing Social Media Creation")
    print("-"*40)

    # Test Twitter post
    twitter_result = agent_create_social(
        topic="Announcing our new AI-powered content creation system",
        platform="twitter",
        tone="engaging"
    )

    if twitter_result.get('success'):
        post = twitter_result.get('social_post', {})
        print(f"✅ Twitter post created!")
        print(f"   Content: {post.get('content')}")
        print(f"   Hashtags: {', '.join(post.get('hashtags', []))}")
    else:
        print(f"❌ Twitter post failed: {twitter_result.get('error')}")

    # Test LinkedIn post
    linkedin_result = agent_create_social(
        topic="How businesses can leverage AI for content strategy",
        platform="linkedin",
        tone="professional"
    )

    if linkedin_result.get('success'):
        post = linkedin_result.get('social_post', {})
        print(f"✅ LinkedIn post created!")
        print(f"   Platform: {post.get('platform')}")
        print(f"   Character limit: {post.get('character_limit')}")
    else:
        print(f"❌ LinkedIn post failed: {linkedin_result.get('error')}")

    return twitter_result.get('success') or linkedin_result.get('success')


def test_image_generation():
    """Test image generation through the bridge"""
    print("\n" + "-"*40)
    print("Testing Image Generation")
    print("-"*40)

    result = agent_create_image(
        prompt="A futuristic AI assistant helping create content, digital art style",
        style="digital_art",
        size="1024x1024"
    )

    if result.get('success'):
        content = result.get('content', {})
        images = content.get('images', [])
        print(f"✅ Image generation successful!")
        print(f"   Generated {len(images)} images")
        print(f"   Style: {content.get('style')}")
        print(f"   Size: {content.get('metadata', {}).get('size')}")
        if images:
            print(f"   First image URL: {images[0].get('url', 'N/A')}")
        return True
    else:
        print(f"❌ Image generation failed: {result.get('error')}")
        return False


def test_multi_format_campaign():
    """Test multi-format campaign creation"""
    print("\n" + "-"*40)
    print("Testing Multi-Format Campaign")
    print("-"*40)

    result = agent_create_campaign(
        topic="Launching Our Revolutionary AI Platform",
        platforms=['blog', 'twitter', 'linkedin']
    )

    if result.get('success'):
        pieces = result.get('content_pieces', {})
        print(f"✅ Campaign created successfully!")
        print(f"   Topic: {result.get('campaign_topic')}")
        print(f"   Content pieces created:")

        for platform, content in pieces.items():
            if content.get('success'):
                print(f"     ✅ {platform}: Created successfully")
            else:
                print(f"     ❌ {platform}: Failed")

        return True
    else:
        print(f"❌ Campaign creation failed")
        return False


def test_content_library_access():
    """Test accessing the content library"""
    print("\n" + "-"*40)
    print("Testing Content Library Access")
    print("-"*40)

    # Get content agent and create bridge
    agent = AgentContentCreator.get_content_agent()
    if not agent:
        print("❌ No content agent available")
        return False

    bridge = ContentStudioBridge(agent=agent)

    # Get content library
    library = bridge.get_content_library(content_type='all')

    if library.get('success'):
        print(f"✅ Content library accessed!")
        print(f"   Total items: {library.get('count', 0)}")
        results = library.get('results', [])
        if results:
            print(f"   Recent items:")
            for item in results[:3]:
                print(f"     - {item.get('title', 'Untitled')} ({item.get('type')})")
        return True
    else:
        print(f"❌ Failed to access content library: {library.get('error')}")
        return False


def test_agent_execution_logging():
    """Test that agent executions are being logged"""
    print("\n" + "-"*40)
    print("Testing Agent Execution Logging")
    print("-"*40)

    from core.models.agents_registry import AgentExecution

    # Count executions before
    before_count = AgentExecution.objects.count()

    # Create some content
    result = agent_create_blog(
        topic="Test blog for execution logging",
        length="short"
    )

    # Count executions after
    after_count = AgentExecution.objects.count()

    if after_count > before_count:
        print(f"✅ Execution logged successfully!")
        print(f"   Executions before: {before_count}")
        print(f"   Executions after: {after_count}")

        # Get the latest execution
        latest = AgentExecution.objects.order_by('-created_at').first()
        if latest:
            print(f"   Latest execution:")
            print(f"     Agent: {latest.template.name if latest.template else 'Unknown'}")
            print(f"     Status: {latest.status}")
            print(f"     Action: {latest.input_data.get('action', 'Unknown')}")
        return True
    else:
        print(f"❌ No execution was logged")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("CONTENT STUDIO BRIDGE TEST SUITE")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")

    results = {
        'connection': test_content_studio_connection(),
        'blog': test_blog_creation(),
        'social': test_social_media_creation(),
        'image': test_image_generation(),
        'campaign': test_multi_format_campaign(),
        'library': test_content_library_access(),
        'logging': test_agent_execution_logging()
    }

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.capitalize():15} {status}")

    print("-"*40)
    print(f"Total: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Content Studio Bridge is fully operational!")
    elif passed_tests > 0:
        print(f"\n⚠️  {passed_tests} tests passed, but {total_tests - passed_tests} failed.")
    else:
        print("\n❌ All tests failed. Check configuration and dependencies.")

    # Save test report
    report = {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'summary': {
            'total': total_tests,
            'passed': passed_tests,
            'failed': total_tests - passed_tests
        }
    }

    with open('content_studio_bridge_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Test report saved to: content_studio_bridge_test_report.json")


if __name__ == "__main__":
    main()