"""
Test Content Studio Integration with Agent Tools
SESSION 30: Testing the complete flow from spider discovery to content creation
"""

import asyncio
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(asctime)s %(name)s %(funcName)s:%(lineno)d %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


async def test_content_studio_direct():
    """Test 1: Content Studio directly"""
    print("\n" + "="*80)
    print("  TEST 1: Content Studio Direct Generation")
    print("="*80 + "\n")

    try:
        from intelligence.content_creation_studio import (
            content_studio,
            ContentSpecification,
            ContentType,
            ContentQuality
        )

        # Create a specification for a blog post
        spec = ContentSpecification(
            content_type=ContentType.BLOG_POST,
            title="How AI is Transforming Freelance Work",
            topic="AI tools and automation in freelancing",
            keywords=['AI', 'automation', 'freelancing', 'productivity'],
            target_audience='freelancers and independent contractors',
            word_count=800,
            tone='professional yet engaging',
            quality_level=ContentQuality.STANDARD
        )

        print(f"📝 Generating blog post: {spec.title}")
        print(f"   Topic: {spec.topic}")
        print(f"   Target: {spec.target_audience}")
        print(f"   Keywords: {', '.join(spec.keywords)}")

        # Generate content
        result = await content_studio.generate_content(spec)

        print(f"\n✅ Content Generated!")
        print(f"   Words: {result.word_count}")
        print(f"   Quality Score: {result.quality_score:.2f}/1.0")
        print(f"   Estimated Value: ${result.estimated_value}")
        print(f"   Generator: {result.metadata.get('generator')}")

        print(f"\n📄 Content Preview (first 500 chars):")
        print("-" * 80)
        print(result.content[:500] + "...")
        print("-" * 80)

        return True

    except Exception as e:
        logger.error(f"❌ Test 1 failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_income_tools():
    """Test 2: Agent Income Tools with Content Studio"""
    print("\n" + "="*80)
    print("  TEST 2: Agent Income Tools Integration")
    print("="*80 + "\n")

    try:
        from intelligence.agent_income_tools import AgentIncomeTools

        # Initialize agent tools
        agent_tools = AgentIncomeTools()
        await agent_tools.initialize()

        print("✅ Agent Income Tools initialized")
        print(f"   Content Studio available: {agent_tools.content_studio is not None}")

        # Test content creation through agent tools
        specifications = {
            'title': 'Python Automation Scripts for Small Business',
            'topic': 'Python automation tools and scripts',
            'keywords': ['python', 'automation', 'scripting', 'business'],
            'target_audience': 'small business owners',
            'word_count': 600,
            'tone': 'helpful and practical'
        }

        print(f"\n🤖 Agent creating article...")
        print(f"   Title: {specifications['title']}")

        result = await agent_tools.create_content(
            content_type='article',
            specifications=specifications
        )

        if result['success']:
            print(f"\n✅ Agent successfully created content!")
            print(f"   Word Count: {result.get('word_count', 'N/A')}")
            print(f"   Quality Score: {result.get('quality_score', 'N/A')}")
            print(f"   Estimated Value: ${result.get('estimated_value', 'N/A')}")

            print(f"\n📄 Content Preview:")
            print("-" * 80)
            print(result['content'][:400] + "...")
            print("-" * 80)
            return True
        else:
            print(f"❌ Agent content creation failed: {result.get('error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Test 2 failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_content_types():
    """Test 3: Multiple content types"""
    print("\n" + "="*80)
    print("  TEST 3: Multiple Content Types")
    print("="*80 + "\n")

    try:
        from intelligence.agent_income_tools import AgentIncomeTools

        agent_tools = AgentIncomeTools()
        await agent_tools.initialize()

        content_types = [
            ('article', 'Understanding Machine Learning Basics'),
            ('code', 'REST API Client in Python'),
            ('social_media', 'AI Tools for Content Creators'),
            ('product_description', 'Smart Home Automation System')
        ]

        results = []

        for content_type, title in content_types:
            print(f"\n📝 Creating {content_type}: {title}")

            specifications = {
                'title': title,
                'topic': title,
                'keywords': title.split()[:3],
                'target_audience': 'general audience',
                'word_count': 400 if content_type == 'article' else None,
                'tone': 'professional'
            }

            result = await agent_tools.create_content(
                content_type=content_type,
                specifications=specifications
            )

            if result['success']:
                print(f"   ✅ {content_type} created successfully")
                print(f"   Size: {len(result['content'])} characters")
                if 'estimated_value' in result:
                    print(f"   Value: ${result['estimated_value']}")
                results.append(True)
            else:
                print(f"   ❌ {content_type} failed: {result.get('error')}")
                results.append(False)

        success_rate = sum(results) / len(results)
        print(f"\n📊 Success Rate: {success_rate*100:.0f}% ({sum(results)}/{len(results)})")

        return success_rate > 0.5

    except Exception as e:
        logger.error(f"❌ Test 3 failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_complete_pipeline():
    """Test 4: Complete pipeline from spider to content"""
    print("\n" + "="*80)
    print("  TEST 4: Complete Spider → Content Pipeline")
    print("="*80 + "\n")

    try:
        # Step 1: Get opportunities from spiders
        print("🕷️ Step 1: Discovering opportunities from spider network...")

        from intelligence.income_spider_orchestrator import income_spider_orchestrator
        from intelligence.income_builder import UserProfile, SkillLevel

        user_profile = UserProfile(
            id="test_content_creator",
            skills=['python', 'writing', 'content creation'],
            skill_level=SkillLevel.INTERMEDIATE,
            available_hours_per_week=20
        )

        opportunities = await income_spider_orchestrator.discover_opportunities_for_user(
            user_profile,
            use_real_data=True,
            max_opportunities=5
        )

        print(f"   Found {len(opportunities.opportunities)} opportunities")

        if not opportunities.opportunities:
            print("   ⚠️ No opportunities found, using mock data for pipeline test")
            opportunity = {
                'title': 'Content Writer for Tech Blog',
                'description': 'Write technical articles about AI and automation',
                'budget': 500,
                'skills': ['writing', 'AI', 'technical documentation']
            }
        else:
            # Use first real opportunity
            opp = opportunities.opportunities[0]
            opportunity = {
                'title': opp.title,
                'description': opp.description,
                'budget': opp.budget_min or 500,
                'skills': opp.required_skills
            }

        print(f"\n   Selected opportunity: {opportunity['title']}")
        print(f"   Budget: ${opportunity['budget']}")

        # Step 2: Create content for the opportunity
        print("\n✍️ Step 2: Creating content deliverable...")

        from intelligence.agent_income_tools import AgentIncomeTools

        agent_tools = AgentIncomeTools()
        await agent_tools.initialize()

        specifications = {
            'title': f"Sample: {opportunity['title']}",
            'topic': opportunity['description'],
            'keywords': opportunity.get('skills', ['writing'])[:5],
            'target_audience': 'hiring manager',
            'word_count': 600,
            'tone': 'professional and persuasive'
        }

        content_result = await agent_tools.create_content(
            content_type='article',
            specifications=specifications
        )

        if content_result['success']:
            print(f"   ✅ Content created successfully!")
            print(f"   Words: {content_result.get('word_count', 'N/A')}")
            print(f"   Value: ${content_result.get('estimated_value', 'N/A')}")
            print(f"   Quality: {content_result.get('quality_score', 'N/A')}")

            # Step 3: Show complete flow
            print("\n🎯 Step 3: Complete flow summary")
            print(f"   Opportunity: {opportunity['title']}")
            print(f"   Budget: ${opportunity['budget']}")
            print(f"   Deliverable: Article ({content_result.get('word_count', 0)} words)")
            print(f"   Estimated Value: ${content_result.get('estimated_value', 0)}")
            print(f"   Quality Score: {content_result.get('quality_score', 0):.2f}")

            profit_margin = opportunity['budget'] - content_result.get('estimated_value', 0)
            print(f"   Potential Profit: ${profit_margin:.2f}")

            print("\n✅ COMPLETE PIPELINE WORKING!")
            print("   Spiders → Opportunities → Content Creation → Revenue")

            return True
        else:
            print(f"   ❌ Content creation failed: {content_result.get('error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Test 4 failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  CONTENT STUDIO INTEGRATION TESTS")
    print("="*80)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    tests = [
        ("Content Studio Direct", test_content_studio_direct),
        ("Agent Income Tools Integration", test_agent_income_tools),
        ("Multiple Content Types", test_multiple_content_types),
        ("Complete Pipeline", test_complete_pipeline)
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80 + "\n")

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<50} {status}")

    passed_count = sum(results.values())
    total_count = len(results)
    success_rate = (passed_count / total_count * 100) if total_count > 0 else 0

    print(f"\n{'Total':.< 50} {passed_count}/{total_count} ({success_rate:.0f}%)")

    if success_rate == 100:
        print("\n🎉 ALL TESTS PASSED! Content Studio is fully integrated!")
    elif success_rate >= 75:
        print("\n✅ Most tests passed! System is operational.")
    elif success_rate >= 50:
        print("\n⚠️ Some tests failed. System needs fixes.")
    else:
        print("\n❌ Most tests failed. System needs significant work.")

    print("\n" + "="*80)


if __name__ == '__main__':
    asyncio.run(main())