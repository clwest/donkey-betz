#!/usr/bin/env python3
"""
Test Bluesky Integration
Verify Bluesky AT Protocol implementation is working
"""

import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'spiders'))

from ai_core.spiders.bluesky_handler import bluesky_handler, bluesky_collector


async def test_bluesky():
    """Test Bluesky functionality"""
    print("\n" + "🦋"*30)
    print(" "*10 + "BLUESKY INTEGRATION TEST")
    print(" "*10 + "AT Protocol Implementation")
    print("🦋"*30)

    # Check if credentials are configured
    identifier = os.environ.get('BLUESKY_IDENTIFIER', '')
    password = os.environ.get('BLUESKY_PASSWORD', '')

    print("\n📋 CONFIGURATION CHECK:")
    print("="*50)

    if identifier and password:
        print("✅ Bluesky credentials found in environment")
        print(f"   Identifier: {identifier[:3]}...{identifier[-3:] if len(identifier) > 6 else ''}")
    else:
        print("❌ Bluesky credentials NOT configured")
        print("\n📝 TO CONFIGURE:")
        print("1. Add to your .env file:")
        print("   BLUESKY_IDENTIFIER=your-email@example.com")
        print("   BLUESKY_PASSWORD=your-app-password")
        print("\n2. To get an app password:")
        print("   - Go to Settings in Bluesky app/web")
        print("   - Click on 'App passwords'")
        print("   - Create a new app password")
        print("   - Use that password (NOT your main password)")
        print("\nBluesky is FREE and has NO API limits! 🎉")
        return False

    # Test authentication
    print("\n🔐 AUTHENTICATION TEST:")
    print("="*50)

    if await bluesky_handler.authenticate():
        print(f"✅ Successfully authenticated as @{bluesky_handler.session.handle}")
        print(f"   DID: {bluesky_handler.session.did[:20]}...")
        print(f"   Service: {bluesky_handler.session.service_endpoint}")
    else:
        print("❌ Authentication failed")
        print("   Check your credentials and try again")
        return False

    # Test post search
    print("\n🔍 SEARCH TEST:")
    print("="*50)

    search_terms = ['AI', 'technology', 'programming']
    for term in search_terms:
        print(f"\nSearching for '{term}'...")
        posts = await bluesky_handler.search_posts(term, limit=3)

        if posts:
            print(f"✅ Found {len(posts)} posts")
            for i, post in enumerate(posts[:2], 1):
                print(f"\n   Post {i}:")
                print(f"   Author: @{post['author']['handle']}")
                print(f"   Text: {post['text'][:100]}...")
                print(f"   Engagement: {post['metrics']['engagement']} (❤️ {post['metrics']['likes']} 🔁 {post['metrics']['reposts']} 💬 {post['metrics']['replies']})")
        else:
            print(f"⚠️ No posts found for '{term}'")

    # Test trending
    print("\n📈 TRENDING TEST:")
    print("="*50)

    trending = await bluesky_handler.get_trending()
    if trending:
        print(f"✅ Found {len(trending)} trending posts")

        # Show top 3 trending posts
        print("\n🔥 Top Trending Posts:")
        for i, post in enumerate(trending[:3], 1):
            print(f"\n   {i}. @{post['author']['handle']}")
            print(f"      {post['text'][:100]}...")
            print(f"      Engagement: {post['metrics']['engagement']}")
    else:
        print("⚠️ No trending posts found")

    # Test intelligence collector
    print("\n🧠 INTELLIGENCE COLLECTION TEST:")
    print("="*50)

    keywords = ['AI', 'machine learning', 'technology']
    print(f"Collecting intelligence for: {keywords}")

    intelligence = await bluesky_collector.collect_intelligence(keywords, max_posts_per_keyword=5)

    if intelligence['posts']:
        print(f"\n✅ Intelligence Report:")
        print(f"   Total Posts: {intelligence['metrics']['total_posts']}")
        print(f"   Total Engagement: {intelligence['metrics']['total_engagement']}")
        print(f"   Total Likes: {intelligence['metrics']['total_likes']}")
        print(f"   Total Reposts: {intelligence['metrics']['total_reposts']}")
        print(f"   Average Engagement: {intelligence['metrics']['avg_engagement']:.1f}")

        # Show sample posts
        print(f"\n📊 Sample Posts:")
        for post in intelligence['posts'][:3]:
            print(f"\n   @{post['author']['handle']}:")
            print(f"   {post['text'][:150]}...")
    else:
        print("⚠️ No intelligence collected")

    # Compare with Twitter
    print("\n🆚 BLUESKY vs TWITTER COMPARISON:")
    print("="*50)
    print("\n✅ BLUESKY ADVANTAGES:")
    print("   • FREE API - No expensive fees!")
    print("   • No rate limits for basic usage")
    print("   • Simple authentication (no OAuth dance)")
    print("   • Open AT Protocol (decentralized)")
    print("   • Growing tech community")
    print("   • Better signal-to-noise ratio")
    print("\n❌ TWITTER DISADVANTAGES:")
    print("   • $100+/month for basic API access")
    print("   • Strict rate limits")
    print("   • Complex OAuth 2.0 setup")
    print("   • Closed, centralized platform")
    print("   • API changes frequently")

    # Clean up
    await bluesky_handler.close()

    print("\n" + "="*50)
    print("🎉 BLUESKY INTEGRATION TEST COMPLETE!")
    print("="*50)

    return True


async def main():
    """Run Bluesky integration test"""
    try:
        success = await test_bluesky()

        if success:
            print("\n✅ Bluesky integration is working perfectly!")
            print("   Your spider army can now collect data from Bluesky")
            print("   No expensive Twitter API fees needed! 🎉")
        else:
            print("\n⚠️ Please configure Bluesky credentials to enable integration")
            print("   It's free and takes just 2 minutes to set up!")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting Bluesky Integration Test...")
    asyncio.run(main())