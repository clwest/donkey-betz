"""
Test Spider → Income Builder Integration
Tests the complete data pipeline from spider discovery to action plans
"""

import asyncio
import logging
import sys
from datetime import datetime

# Setup Django environment
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from intelligence.income_builder import AIIncomeBuilder, UserProfile, SkillLevel
from intelligence.income_spider_orchestrator import (
    income_spider_orchestrator,
    get_opportunities_for_user,
    create_complete_income_plan
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_section(text: str):
    """Print formatted section"""
    print("\n" + "-" * 80)
    print(f"  {text}")
    print("-" * 80)


async def test_spider_discovery_basic():
    """Test 1: Basic spider opportunity discovery"""
    print_header("TEST 1: Basic Spider Discovery")

    # Create test user profile
    user_profile = UserProfile(
        id="test_user_spider_001",
        current_balance=0.0,
        skills=['python', 'writing', 'data analysis', 'automation'],
        skill_level=SkillLevel.INTERMEDIATE,
        available_hours_per_week=20,
        interests=['ai', 'freelancing', 'content creation']
    )

    logger.info("📋 User Profile:")
    logger.info(f"   Skills: {', '.join(user_profile.skills)}")
    logger.info(f"   Experience: {user_profile.skill_level.value}")
    logger.info(f"   Hours: {user_profile.available_hours_per_week}/week")

    # Test with REAL data
    print_section("Fetching REAL opportunities from APIs...")

    opportunities = await get_opportunities_for_user(user_profile, use_real_data=True)

    logger.info(f"✅ Found {len(opportunities)} opportunities from spider network")

    if opportunities:
        print_section("Top 5 Opportunities:")
        for i, opp in enumerate(opportunities[:5], 1):
            print(f"\n{i}. {opp.title}")
            print(f"   Platform: {opp.platform}")
            print(f"   Budget: ${opp.budget_min if opp.budget_min else 'Not specified'}")
            print(f"   Score: {opp.quality_score:.2f}")
            print(f"   Skills: {', '.join(opp.skills_required[:3])}...")
            print(f"   Source: {opp.spider_source}")

            if opp.raw_data and 'ml_score' in opp.raw_data:
                print(f"   ML Score: {opp.raw_data['ml_score']:.2f}")
                print(f"   ML Engine: {opp.raw_data.get('ml_engine', 'unknown')}")

    return len(opportunities) > 0


async def test_income_builder_integration():
    """Test 2: Income Builder with Spider Integration"""
    print_header("TEST 2: Income Builder + Spider Integration")

    income_builder = AIIncomeBuilder()

    user_profile = UserProfile(
        id="test_user_spider_002",
        current_balance=0.0,
        skills=['content writing', 'seo', 'research', 'ai tools'],
        skill_level=SkillLevel.BEGINNER,
        available_hours_per_week=15,
        interests=['content creation', 'freelancing']
    )

    logger.info("🤖 Testing Income Builder spider discovery method...")

    # Use the new discover_opportunities_with_spiders method
    result = await income_builder.discover_opportunities_with_spiders(
        user_profile,
        use_real_data=True
    )

    if result['success']:
        logger.info(f"✅ Spider discovery successful!")
        logger.info(f"   Total found: {result['total_found']}")
        logger.info(f"   Discovery time: {result['discovery_time']:.2f}s")
        logger.info(f"   Sources: {', '.join(result['spider_sources'])}")

        print_section("Discovered Opportunities:")
        for i, opp in enumerate(result['opportunities'][:3], 1):
            print(f"\n{i}. {opp['title']}")
            print(f"   Platform: {opp['platform']}")
            print(f"   Budget: ${opp['budget'] if opp['budget'] else 'TBD'}")
            print(f"   Match Score: {opp['score']:.2f}")
            if opp['ml_score']:
                print(f"   ML Score: {opp['ml_score']:.2f}")

        # Check if action plan was created
        if result.get('action_plan'):
            logger.info("\n📋 Action plan generated:")
            action_plan = result['action_plan']
            logger.info(f"   Plan ID: {action_plan.get('plan_id')}")
            logger.info(f"   Files created: {len(action_plan.get('files_created', []))}")
            for file_path in action_plan.get('files_created', []):
                logger.info(f"      - {file_path}")

        return True
    else:
        logger.error(f"❌ Spider discovery failed: {result.get('error')}")
        return False


async def test_complete_income_pipeline():
    """Test 3: Complete Income Pipeline (Spider + ML + Agents + Action Plan)"""
    print_header("TEST 3: Complete Income Pipeline")

    user_profile = UserProfile(
        id="test_user_pipeline_003",
        current_balance=0.0,
        skills=['python', 'automation', 'api integration', 'data analysis'],
        skill_level=SkillLevel.ADVANCED,
        available_hours_per_week=30,
        interests=['automation', 'ai', 'freelancing']
    )

    logger.info("🏗️ Creating complete income pipeline...")
    logger.info("   This tests: Spider Discovery → ML Scoring → Agent Analysis → Action Plan")

    # Use the convenience function
    plan = await create_complete_income_plan(user_profile, use_real_data=True)

    if plan.get('opportunities'):
        logger.info(f"✅ Pipeline complete!")

        print_section("Pipeline Results:")

        # Discovery metadata
        metadata = plan.get('discovery_metadata', {})
        print(f"\nDiscovery:")
        print(f"  - Sources: {', '.join(metadata.get('sources', []))}")
        print(f"  - Time: {metadata.get('discovery_time', 0):.2f}s")
        print(f"  - Total found: {metadata.get('total_found', 0)}")
        print(f"  - After filtering: {metadata.get('filtered_count', 0)}")

        # Top opportunities
        opportunities = plan.get('opportunities', [])
        print(f"\nTop 3 Opportunities:")
        for i, opp in enumerate(opportunities[:3], 1):
            print(f"\n  {i}. {opp['title']}")
            print(f"     Platform: {opp['platform']}")
            print(f"     Budget: ${opp['budget']}")
            print(f"     Score: {opp['quality_score']:.2f}")

        # Action plan
        if plan.get('action_plan'):
            action_plan = plan['action_plan']
            print(f"\nAction Plan:")
            print(f"  - Plan ID: {action_plan.get('plan_id')}")
            print(f"  - Opportunity: {action_plan.get('opportunity')}")
            print(f"  - Week-by-week plan: {len(action_plan.get('week_by_week', []))} weeks")
            print(f"  - Files created: {len(action_plan.get('files_created', []))}")

            # Show real opportunity details
            if action_plan.get('real_opportunity'):
                real_opp = action_plan['real_opportunity']
                print(f"\n  Real Opportunity Details:")
                print(f"    Title: {real_opp['title']}")
                print(f"    Platform: {real_opp['platform']}")
                print(f"    Budget: ${real_opp['budget']}")
                print(f"    Skills: {', '.join(real_opp['skills_required'][:3])}...")

        # Agent insights
        agent_insights = plan.get('agent_insights', [])
        if agent_insights:
            print(f"\nAgent Insights: {len(agent_insights)} insights generated")

        return True
    else:
        logger.error("❌ Pipeline failed to generate opportunities")
        return False


async def test_opportunity_scoring():
    """Test 4: Opportunity Scoring with ML"""
    print_header("TEST 4: ML-Based Opportunity Scoring")

    user_profile = UserProfile(
        id="test_user_scoring_004",
        current_balance=500.0,
        skills=['javascript', 'react', 'ui design', 'api integration'],
        skill_level=SkillLevel.INTERMEDIATE,
        available_hours_per_week=25,
        interests=['web development', 'frontend'],
        total_earned=1200.0,
        reputation_score=4.5
    )

    logger.info("📊 Testing ML-based opportunity scoring...")

    result = await income_spider_orchestrator.discover_opportunities_for_user(
        user_profile,
        use_real_data=True,
        max_opportunities=10
    )

    logger.info(f"   Found {len(result.opportunities)} opportunities")

    print_section("Scoring Analysis:")
    for i, opp in enumerate(result.opportunities[:5], 1):
        print(f"\n{i}. {opp.title}")
        print(f"   Combined Score: {opp.quality_score:.3f}")

        if opp.raw_data:
            ml_score = opp.raw_data.get('ml_score')
            ml_engine = opp.raw_data.get('ml_engine')
            ml_confidence = opp.raw_data.get('ml_confidence')

            if ml_score:
                print(f"   ML Score: {ml_score:.3f}")
                print(f"   ML Engine: {ml_engine}")
                print(f"   ML Confidence: {ml_confidence:.2f}")

        # Analyze why it scored high/low
        print(f"   Skills Match: {len(set(user_profile.skills) & set(opp.skills_required))}/{len(opp.skills_required)}")
        print(f"   Budget: ${opp.budget_min if opp.budget_min else 'Not specified'}")
        print(f"   Experience Level: {opp.experience_level}")

    return len(result.opportunities) > 0


async def test_spider_performance():
    """Test 5: Spider Network Performance"""
    print_header("TEST 5: Spider Network Performance")

    user_profile = UserProfile(
        id="test_user_perf_005",
        current_balance=0.0,
        skills=['python', 'data analysis'],
        skill_level=SkillLevel.BEGINNER,
        available_hours_per_week=10
    )

    # Test with real data
    logger.info("⏱️ Testing spider performance with REAL data...")
    start_time = datetime.now()

    result = await income_spider_orchestrator.discover_opportunities_for_user(
        user_profile,
        use_real_data=True,
        max_opportunities=20
    )

    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()

    print_section("Performance Metrics:")
    print(f"\nTotal Time: {total_time:.2f}s")
    print(f"Discovery Time (internal): {result.discovery_time:.2f}s")
    print(f"Opportunities Found: {result.total_found}")
    print(f"After Filtering: {result.filtered_count}")
    print(f"Spider Sources: {', '.join(result.spider_sources)}")
    print(f"Avg Time per Opportunity: {total_time / max(result.filtered_count, 1):.3f}s")

    # Test with mock data (should be faster)
    logger.info("\n⏱️ Testing spider performance with MOCK data...")
    start_time_mock = datetime.now()

    result_mock = await income_spider_orchestrator.discover_opportunities_for_user(
        user_profile,
        use_real_data=False,
        max_opportunities=20
    )

    end_time_mock = datetime.now()
    total_time_mock = (end_time_mock - start_time_mock).total_seconds()

    print(f"\nMock Data Performance:")
    print(f"Total Time: {total_time_mock:.2f}s")
    print(f"Opportunities Found: {result_mock.total_found}")
    print(f"Speed Improvement: {total_time / max(total_time_mock, 0.01):.1f}x faster with mock data")

    return True


async def run_all_tests():
    """Run all integration tests"""
    print_header("SPIDER → INCOME BUILDER INTEGRATION TESTS")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    tests = [
        ("Basic Spider Discovery", test_spider_discovery_basic),
        ("Income Builder Integration", test_income_builder_integration),
        ("Complete Income Pipeline", test_complete_income_pipeline),
        ("Opportunity Scoring", test_opportunity_scoring),
        ("Spider Performance", test_spider_performance),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            logger.info(f"\n▶️ Running: {test_name}")
            passed = await test_func()
            results.append((test_name, passed))
            logger.info(f"{'✅ PASSED' if passed else '❌ FAILED'}: {test_name}\n")
        except Exception as e:
            logger.error(f"❌ ERROR in {test_name}: {e}", exc_info=True)
            results.append((test_name, False))

    # Print summary
    print_header("TEST SUMMARY")
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {test_name}")

    print(f"\n{'=' * 80}")
    print(f"Result: {passed_count}/{total_count} tests passed")
    print(f"Success Rate: {(passed_count/total_count)*100:.1f}%")
    print(f"{'=' * 80}\n")

    if passed_count == total_count:
        logger.info("🎉 ALL TESTS PASSED! Spider integration is working!")
    else:
        logger.warning(f"⚠️ {total_count - passed_count} test(s) failed")

    return passed_count == total_count


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}", exc_info=True)
        sys.exit(1)