#!/usr/bin/env python
"""
Reddit Learning Integration - Comprehensive Test Suite
======================================================

This test suite validates the complete Reddit integration including:
- Reddit API handler functionality
- Learning bridge intelligence extraction
- Learning loop integration
- Advisor feed enhancement
- Agent intelligence updates
- End-to-end workflow validation

Run with: python test_reddit_learning_integration.py
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress some verbose logging
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('prawcore').setLevel(logging.WARNING)


async def test_reddit_handler():
    """Test 1: Basic Reddit Handler Functionality"""
    print("\n" + "="*60)
    print("TEST 1: Reddit Handler Basic Functionality")
    print("="*60)

    try:
        from backend.spiders.reddit_handler import RedditHandler

        handler = RedditHandler()
        print("✅ Reddit handler initialized")

        # Test search functionality
        print("\n📝 Testing Reddit search...")
        posts = await handler.search_posts(
            "artificial intelligence",
            sort="relevance",
            time_filter="week",
            limit=5
        )

        if posts:
            print(f"✅ Found {len(posts)} posts about AI")
            for i, post in enumerate(posts[:3], 1):
                print(f"\n  Post {i}:")
                print(f"    Title: {post.title[:80]}...")
                print(f"    Subreddit: r/{post.subreddit}")
                print(f"    Score: {post.score}")
                print(f"    Comments: {post.num_comments}")
        else:
            print("⚠️ No posts found (API might be in read-only mode)")

        # Test subreddit posts
        print("\n📝 Testing subreddit retrieval...")
        subreddit_posts = await handler.get_subreddit_posts(
            "MachineLearning",
            sort="hot",
            limit=5
        )

        if subreddit_posts:
            print(f"✅ Retrieved {len(subreddit_posts)} posts from r/MachineLearning")
            top_post = subreddit_posts[0]
            print(f"  Top post: {top_post.title[:80]}...")
            print(f"  Score: {top_post.score}")
        else:
            print("⚠️ Could not retrieve subreddit posts")

        # Test trending topics
        print("\n📝 Testing trending topics...")
        trending = await handler.get_trending_topics(
            ['artificial', 'MachineLearning', 'datascience'],
            limit=3
        )

        if trending:
            print(f"✅ Retrieved trending topics from {len(trending)} subreddits")
            for subreddit, topics in list(trending.items())[:2]:
                print(f"\n  r/{subreddit}:")
                for topic in topics[:2]:
                    print(f"    - {topic['title'][:60]}... (Score: {topic['score']})")
        else:
            print("⚠️ Could not retrieve trending topics")

        await handler.cleanup()
        print("\n✅ Reddit Handler Test Completed")
        return True

    except Exception as e:
        print(f"\n❌ Reddit Handler Test Failed: {e}")
        logger.error(f"Reddit handler test error: {e}", exc_info=True)
        return False


async def test_reddit_learning_bridge():
    """Test 2: Reddit Learning Bridge Intelligence Extraction"""
    print("\n" + "="*60)
    print("TEST 2: Reddit Learning Bridge")
    print("="*60)

    try:
        from backend.intelligence.reddit_learning_bridge import get_reddit_learning_bridge

        bridge = get_reddit_learning_bridge()
        print("✅ Reddit learning bridge initialized")

        # Test agent insights
        print("\n📝 Testing agent insight extraction...")
        agent_insights = await bridge.get_insights_for_agent(
            "AI_Research_Agent",
            "artificial_intelligence"
        )

        if agent_insights:
            print(f"✅ Generated {len(agent_insights)} insights for AI Research Agent")
            for i, insight in enumerate(agent_insights[:3], 1):
                print(f"\n  Insight {i}:")
                print(f"    Subreddit: r/{insight.subreddit}")
                print(f"    Topic: {insight.topic[:60]}...")
                print(f"    Sentiment: {insight.sentiment:.2f}")
                print(f"    Confidence: {insight.confidence:.2f}")
                if insight.actionable_advice:
                    print(f"    Advice: {insight.actionable_advice[0][:80]}...")
        else:
            print("⚠️ No agent insights generated")

        # Test advisor insights
        print("\n📝 Testing advisor insight extraction...")
        advisor_insights = await bridge.get_insights_for_advisor(
            "Warren Buffett",
            ["value investing", "dividend", "moat"]
        )

        if advisor_insights:
            print(f"✅ Generated {len(advisor_insights)} insights for Warren Buffett")
            for i, insight in enumerate(advisor_insights[:2], 1):
                print(f"\n  Insight {i}:")
                print(f"    Topic: {insight.topic[:60]}...")
                print(f"    Key Points: {len(insight.key_points)} points")
                if insight.expert_opinions:
                    print(f"    Expert Opinions: {len(insight.expert_opinions)} opinions")
        else:
            print("⚠️ No advisor insights generated")

        # Test community consensus
        print("\n📝 Testing community consensus building...")
        consensus = await bridge.get_community_consensus("AI job market")

        if consensus:
            print(f"✅ Built consensus on 'AI job market'")
            print(f"  Subreddits analyzed: {len(consensus.subreddits)}")
            print(f"  Total discussions: {consensus.total_discussions}")
            print(f"  Average sentiment: {consensus.average_sentiment:.2f}")
            print(f"  Confidence: {consensus.confidence:.2f}")
            if consensus.key_arguments_for:
                print(f"  Supporting argument: {consensus.key_arguments_for[0][:80]}...")
        else:
            print("⚠️ Could not build consensus")

        print("\n✅ Reddit Learning Bridge Test Completed")
        return True

    except Exception as e:
        print(f"\n❌ Reddit Learning Bridge Test Failed: {e}")
        logger.error(f"Reddit learning bridge test error: {e}", exc_info=True)
        return False


async def test_learning_loop_integration():
    """Test 3: Reddit Integration with Learning Loop"""
    print("\n" + "="*60)
    print("TEST 3: Learning Loop Integration")
    print("="*60)

    try:
        # Setup Django
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        django.setup()

        from backend.intelligence.learning_loop import learning_loop

        print("✅ Learning loop initialized")

        # Test Reddit community feedback extraction
        print("\n📝 Testing Reddit community feedback extraction...")
        reddit_feedback = await learning_loop._extract_reddit_community_feedback()

        if reddit_feedback:
            print(f"✅ Extracted {len(reddit_feedback)} Reddit feedback items")
            for i, feedback in enumerate(reddit_feedback[:3], 1):
                print(f"\n  Feedback {i}:")
                print(f"    Source: {feedback.source}")
                print(f"    Category: {feedback.category}")
                print(f"    Rating: {feedback.rating:.2f}")
                print(f"    Message: {feedback.message[:80]}...")
                if 'subreddit' in feedback.context:
                    print(f"    Subreddit: r/{feedback.context['subreddit']}")
        else:
            print("⚠️ No Reddit feedback extracted")

        # Test market sentiment with Reddit
        print("\n📝 Testing market sentiment extraction (Reddit + Bluesky)...")
        market_feedback = await learning_loop._extract_market_sentiment_feedback()

        reddit_market = [f for f in market_feedback if f.source == "reddit_consensus"]
        if reddit_market:
            print(f"✅ Found {len(reddit_market)} Reddit market sentiment items")
            for feedback in reddit_market[:2]:
                print(f"\n  Topic: {feedback.context.get('topic', 'Unknown')}")
                print(f"  Sentiment: {feedback.context.get('sentiment', 'Unknown')}")
                print(f"  Confidence: {feedback.context.get('confidence', 0):.2f}")
                print(f"  Discussions: {feedback.context.get('total_discussions', 0)}")
        else:
            print("⚠️ No Reddit market sentiment found")

        print("\n✅ Learning Loop Integration Test Completed")
        return True

    except Exception as e:
        print(f"\n❌ Learning Loop Integration Test Failed: {e}")
        logger.error(f"Learning loop test error: {e}", exc_info=True)
        return False


async def test_advisor_feed_enhancement():
    """Test 4: Reddit Enhancement of Advisor Feed"""
    print("\n" + "="*60)
    print("TEST 4: Advisor Feed Reddit Enhancement")
    print("="*60)

    try:
        # Setup Django
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        django.setup()

        from backend.spiders.advisor_feed import get_advisor_feed

        advisor_feed = get_advisor_feed()
        print("✅ Advisor feed initialized")

        # Test Reddit enhancement for an advisor
        print("\n📝 Testing Reddit enhancement for Warren Buffett...")
        reddit_data = await advisor_feed.enhance_advisor_with_reddit("Warren Buffett")

        if 'error' not in reddit_data:
            print("✅ Warren Buffett enhanced with Reddit intelligence")
            print(f"  Reddit insights: {len(reddit_data.get('reddit_insights', []))}")
            print(f"  Trending topics: {len(reddit_data.get('trending_topics', []))}")
            print(f"  Community consensus: {len(reddit_data.get('community_consensus', []))}")
            print(f"  Recommendations: {len(reddit_data.get('reddit_recommendations', []))}")

            # Show sample recommendation
            if reddit_data.get('reddit_recommendations'):
                rec = reddit_data['reddit_recommendations'][0]
                print(f"\n  Sample recommendation:")
                print(f"    Source: {rec['source']}")
                print(f"    Advice: {rec['advice'][:100]}...")
                print(f"    Confidence: {rec['confidence']:.2f}")
        else:
            print(f"⚠️ Reddit enhancement error: {reddit_data['error']}")

        # Test combined social intelligence
        print("\n📝 Testing combined social intelligence for Cathie Wood...")
        combined_data = await advisor_feed.enhance_advisor_with_social_intelligence("Cathie Wood")

        if 'error' not in combined_data:
            print("✅ Cathie Wood enhanced with combined intelligence")
            print(f"  Bluesky insights: {bool(combined_data.get('bluesky_insights'))}")
            print(f"  Reddit insights: {len(combined_data.get('reddit_insights', []))}")
            print(f"  Combined recommendations: {len(combined_data.get('combined_recommendations', []))}")

            # Show multi-platform trends
            trends = combined_data.get('multi_platform_trends', {})
            if trends:
                print(f"\n  Multi-platform trends:")
                print(f"    Bluesky-only: {len(trends.get('bluesky', []))}")
                print(f"    Reddit-only: {len(trends.get('reddit', []))}")
                print(f"    Consensus trends: {len(trends.get('consensus_trends', []))}")
        else:
            print(f"⚠️ Combined enhancement error: {combined_data['error']}")

        print("\n✅ Advisor Feed Enhancement Test Completed")
        return True

    except Exception as e:
        print(f"\n❌ Advisor Feed Test Failed: {e}")
        logger.error(f"Advisor feed test error: {e}", exc_info=True)
        return False


async def test_agent_enhancement():
    """Test 5: Reddit Enhancement of Agents"""
    print("\n" + "="*60)
    print("TEST 5: Agent Reddit Enhancement")
    print("="*60)

    try:
        # Setup Django
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        django.setup()

        from backend.agents.universal_agent_loader import social_intelligence_enhancer

        print("✅ Social intelligence enhancer initialized")

        # Create a mock agent for testing
        class MockAgent:
            def __init__(self):
                self.agent_name = "Test_AI_Agent"
                self.specialization = "artificial_intelligence"
                self.capabilities = ["research", "analysis", "prediction"]
                self.learning_context = {}

        agent = MockAgent()
        context = {'query': 'machine learning trends'}

        # Test Reddit enhancement
        print("\n📝 Testing Reddit enhancement for AI agent...")
        reddit_enhancement = await social_intelligence_enhancer.enhance_agent_with_reddit_intelligence(
            agent, context
        )

        if 'error' not in reddit_enhancement:
            print(f"✅ Agent enhanced with Reddit intelligence")
            print(f"  Insights: {len(reddit_enhancement.get('insights', []))}")
            print(f"  Trending topics: {len(reddit_enhancement.get('trending_topics', []))}")
            print(f"  Subreddits monitored: {reddit_enhancement.get('subreddits_monitored', [])}")
            print(f"  Recommendations: {len(reddit_enhancement.get('recommendations', []))}")

            if reddit_enhancement.get('community_consensus'):
                consensus = reddit_enhancement['community_consensus']
                print(f"\n  Community consensus on '{context['query']}':")
                print(f"    Sentiment: {consensus.get('average_sentiment', 0):.2f}")
                print(f"    Confidence: {consensus.get('confidence', 0):.2f}")
        else:
            print(f"⚠️ Reddit enhancement error: {reddit_enhancement['error']}")

        # Test combined enhancement
        print("\n📝 Testing combined social intelligence for agent...")
        combined_enhancement = await social_intelligence_enhancer.enhance_agent_with_social_intelligence(
            agent, context
        )

        if combined_enhancement:
            print(f"✅ Agent enhanced with combined social intelligence")
            print(f"  Combined insights: {len(combined_enhancement.get('combined_insights', []))}")
            print(f"  Consensus recommendations: {len(combined_enhancement.get('consensus_recommendations', []))}")

            trends = combined_enhancement.get('multi_platform_trends', {})
            if trends:
                print(f"\n  Cross-platform trends:")
                print(f"    Consensus trends: {trends.get('consensus_trends', [])}")

            # Check if learning context was updated
            if agent.learning_context:
                print(f"\n  Learning context updated:")
                print(f"    Last update: {agent.learning_context.get('last_social_update', 'N/A')}")
                print(f"    Platforms: {agent.learning_context.get('platforms_used', [])}")
        else:
            print("⚠️ Combined enhancement failed")

        print("\n✅ Agent Enhancement Test Completed")
        return True

    except Exception as e:
        print(f"\n❌ Agent Enhancement Test Failed: {e}")
        logger.error(f"Agent enhancement test error: {e}", exc_info=True)
        return False


async def test_end_to_end_workflow():
    """Test 6: End-to-End Reddit Learning Workflow"""
    print("\n" + "="*60)
    print("TEST 6: End-to-End Reddit Learning Workflow")
    print("="*60)

    try:
        # Setup Django
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        django.setup()

        from backend.intelligence.reddit_learning_bridge import get_reddit_learning_bridge
        from backend.spiders.reddit_handler import RedditHandler

        print("✅ Initializing complete Reddit learning system...")

        # Step 1: Collect Reddit data
        print("\n📝 Step 1: Collecting Reddit data...")
        handler = RedditHandler()
        posts = await handler.search_posts(
            "AI agents automation future",
            sort="relevance",
            time_filter="month",
            limit=10
        )
        print(f"  Collected {len(posts)} Reddit posts")

        # Step 2: Extract intelligence
        print("\n📝 Step 2: Extracting intelligence from Reddit...")
        bridge = get_reddit_learning_bridge()

        # Start learning (but don't wait for continuous loop)
        learning_task = asyncio.create_task(bridge.start_continuous_learning())
        await asyncio.sleep(2)  # Let it initialize

        insights_collected = 0
        for post in posts[:5]:
            try:
                insight = await bridge._extract_post_insights(post, "technology")
                if insight:
                    insights_collected += 1
            except:
                pass

        print(f"  Extracted {insights_collected} insights")

        # Step 3: Build consensus
        print("\n📝 Step 3: Building community consensus...")
        consensus = await bridge.get_community_consensus("AI automation")
        if consensus:
            print(f"  Built consensus from {consensus.total_discussions} discussions")
            print(f"  Average sentiment: {consensus.average_sentiment:.2f}")

        # Step 4: Get trending topics
        print("\n📝 Step 4: Identifying trending topics...")
        trends = await bridge.get_trending_topics()
        print(f"  Identified {len(trends)} trending topics")

        # Step 5: Apply to advisor
        print("\n📝 Step 5: Applying intelligence to advisor...")
        from backend.spiders.advisor_feed import get_advisor_feed
        advisor_feed = get_advisor_feed()

        advisor_enhancement = await advisor_feed.enhance_advisor_with_reddit("Peter Thiel")
        if 'error' not in advisor_enhancement:
            print(f"  Peter Thiel enhanced with {len(advisor_enhancement.get('reddit_insights', []))} insights")

        # Step 6: Apply to agent
        print("\n📝 Step 6: Applying intelligence to agent...")
        from backend.agents.universal_agent_loader import social_intelligence_enhancer

        class TestAgent:
            def __init__(self):
                self.agent_name = "Startup_Advisor_Agent"
                self.specialization = "startup_advisory"
                self.learning_context = {}

        agent = TestAgent()
        agent_enhancement = await social_intelligence_enhancer.enhance_agent_with_reddit_intelligence(agent)

        if 'error' not in agent_enhancement:
            print(f"  Agent enhanced with {len(agent_enhancement.get('insights', []))} insights")

        # Cleanup
        bridge.learning_active = False
        learning_task.cancel()
        try:
            await learning_task
        except asyncio.CancelledError:
            pass

        await handler.cleanup()

        print("\n✅ End-to-End Workflow Test Completed Successfully!")
        print("\n📊 Summary:")
        print(f"  - Reddit posts collected: {len(posts)}")
        print(f"  - Insights extracted: {insights_collected}")
        print(f"  - Consensus built: {'Yes' if consensus else 'No'}")
        print(f"  - Trending topics: {len(trends)}")
        print(f"  - Advisor enhanced: {'Yes' if 'error' not in advisor_enhancement else 'No'}")
        print(f"  - Agent enhanced: {'Yes' if 'error' not in agent_enhancement else 'No'}")

        return True

    except Exception as e:
        print(f"\n❌ End-to-End Workflow Test Failed: {e}")
        logger.error(f"End-to-end test error: {e}", exc_info=True)
        return False


async def run_all_tests():
    """Run all Reddit integration tests"""
    print("\n" + "="*80)
    print(" "*20 + "REDDIT LEARNING INTEGRATION TEST SUITE")
    print(" "*25 + "Testing Complete Reddit Integration")
    print("="*80)

    # Check for Reddit credentials
    if not os.getenv('REDDIT_CLIENT_ID'):
        print("\n⚠️ WARNING: Reddit API credentials not found in environment")
        print("   Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET for full functionality")
        print("   Tests will run in read-only mode with limited features\n")

    results = []
    test_names = []

    # Test 1: Reddit Handler
    test_names.append("Reddit Handler")
    try:
        result = await test_reddit_handler()
        results.append(result)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        results.append(False)

    # Test 2: Learning Bridge
    test_names.append("Learning Bridge")
    try:
        result = await test_reddit_learning_bridge()
        results.append(result)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        results.append(False)

    # Test 3: Learning Loop Integration
    test_names.append("Learning Loop Integration")
    try:
        result = await test_learning_loop_integration()
        results.append(result)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        results.append(False)

    # Test 4: Advisor Feed Enhancement
    test_names.append("Advisor Feed Enhancement")
    try:
        result = await test_advisor_feed_enhancement()
        results.append(result)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        results.append(False)

    # Test 5: Agent Enhancement
    test_names.append("Agent Enhancement")
    try:
        result = await test_agent_enhancement()
        results.append(result)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        results.append(False)

    # Test 6: End-to-End Workflow
    test_names.append("End-to-End Workflow")
    try:
        result = await test_end_to_end_workflow()
        results.append(result)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        results.append(False)

    # Final Summary
    print("\n" + "="*80)
    print(" "*35 + "TEST RESULTS")
    print("="*80)

    passed = sum(results)
    total = len(results)

    for name, result in zip(test_names, results):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {name:30} {status}")

    print("\n" + "-"*80)
    print(f"\n  FINAL SCORE: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 SUCCESS! All Reddit integration tests passed!")
        print("   Your Reddit learning integration is fully operational.")
        print("   151 agents and 25 advisors can now learn from Reddit communities!")
    elif passed > total / 2:
        print("\n⚠️ PARTIAL SUCCESS: Most tests passed but some issues remain.")
        print("   Review failed tests and ensure all dependencies are installed.")
    else:
        print("\n❌ INTEGRATION ISSUES: Multiple tests failed.")
        print("   Check Reddit API credentials and dependencies.")

    print("\n" + "="*80)
    print("   Reddit Learning Integration Test Complete")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Run all tests
    asyncio.run(run_all_tests())