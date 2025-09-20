#!/usr/bin/env python
"""
Test Reddit Integration with Income Builder
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.tools import ToolRegistry

def test_reddit_tool():
    """Test if Reddit tool is configured and working"""
    print("🔍 Testing Reddit Integration...")
    print("-" * 50)

    # Get Reddit tool
    reddit_tool = ToolRegistry.get_tool('reddit_api')

    if not reddit_tool:
        print("❌ Reddit tool not found in registry")
        return False

    print("✅ Reddit tool found in registry")

    # Check configuration
    if not reddit_tool.is_configured:
        print("❌ Reddit API not configured. Please check your .env file")
        print("   Required: REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
        return False

    print("✅ Reddit API configured")

    # Test search
    print("\n📊 Testing Reddit search for 'side hustle' opportunities...")
    result = reddit_tool.execute(
        query="side hustle OR passive income OR looking to hire",
        search_type="posts",
        subreddit="Entrepreneur+sidehustle+forhire",
        limit=5,
        sort="hot"
    )

    if result.get('success'):
        posts = result.get('data', [])
        print(f"✅ Found {len(posts)} opportunities on Reddit!")

        for i, post in enumerate(posts[:3], 1):
            print(f"\n{i}. {post.get('title', 'No title')}")
            print(f"   📈 Upvotes: {post.get('score', 0)}")
            print(f"   💬 Comments: {post.get('num_comments', 0)}")
            print(f"   📍 Subreddit: r/{post.get('subreddit', 'unknown')}")
            print(f"   🔗 URL: {post.get('url', 'No URL')}")

        return True
    else:
        print(f"❌ Search failed: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    print("\n🚀 Reddit Integration Test for Income Builder\n")
    success = test_reddit_tool()

    if success:
        print("\n✅ Reddit integration is working! Your Income Builder can now:")
        print("   • Discover opportunities from Reddit communities")
        print("   • Analyze market demand through upvotes")
        print("   • Find freelance gigs and business ideas")
        print("   • Track trending topics and pain points")
        print("\n💡 Open your Income Builder in the browser to see Reddit opportunities!")
    else:
        print("\n⚠️  Reddit integration needs configuration")
        print("   1. Make sure REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET are in .env")
        print("   2. Install praw: pip install praw>=7.7.1")
        print("   3. Restart Daphne server")