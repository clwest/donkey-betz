#!/usr/bin/env python
"""
Test Complete Freelance Pipeline
Demonstrates the full flow from opportunity discovery to payment collection
"""
import os
import sys
import django
import asyncio
import json
from datetime import datetime
import redis

# Setup Django environment
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Now import after Django setup
from backend.spiders.freelance_opportunity_spider import FreelanceOpportunitySpider
from backend.agents.freelance_job_analyzer import FreelanceJobAnalyzer
from backend.agents.freelance_pipeline import FreelancePipeline


async def test_complete_freelance_flow():
    """Test the complete freelance pipeline from opportunity to payment"""
    print("\n" + "="*70)
    print("💼 FREELANCE PIPELINE TEST - Complete Flow")
    print("="*70)

    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Step 1: Spider finds opportunities
    print("\n📡 STEP 1: Spider Finding Freelance Opportunities...")
    print("-"*70)

    spider = FreelanceOpportunitySpider(redis_client=redis_client)
    await spider.initialize()

    opportunities = await spider.find_opportunities()

    print(f"\n✅ Found {len(opportunities)} suitable opportunities:\n")

    for i, opp in enumerate(opportunities[:3], 1):
        print(f"{i}. {opp.title}")
        print(f"   Platform: {opp.platform}")
        print(f"   Budget: ${opp.budget} ({opp.budget_type})")
        print(f"   Skills: {', '.join(opp.skills_required[:3])}")
        print(f"   Suitability: {opp.agent_suitability:.0%}")
        print(f"   Confidence: {opp.confidence_score:.0%}")
        print(f"   Agents: {', '.join(opp.recommended_agents[:2])}")
        print()

    # Step 2: Process best opportunity through pipeline
    if opportunities:
        best_opportunity = max(opportunities, key=lambda x: x.agent_suitability)

        print("\n🎯 Processing Best Opportunity:")
        print(f"   {best_opportunity.title}")
        print(f"   Expected profit: ${best_opportunity.budget * 0.8:.0f}")
        print()

        # Convert to dict for pipeline
        opp_dict = {
            'job_id': best_opportunity.job_id,
            'platform': best_opportunity.platform,
            'title': best_opportunity.title,
            'description': best_opportunity.description,
            'budget': best_opportunity.budget,
            'budget_type': best_opportunity.budget_type,
            'skills_required': best_opportunity.skills_required,
            'deadline': best_opportunity.deadline,
            'client_rating': best_opportunity.client_rating,
            'url': best_opportunity.url,
            'recommended_agents': best_opportunity.recommended_agents,
            'estimated_completion_time': best_opportunity.estimated_completion_time
        }

        # Initialize pipeline
        pipeline = FreelancePipeline(redis_client=redis_client)

        print("\n🚀 STARTING COMPLETE PIPELINE")
        print("="*70)

        # Process through complete pipeline
        project = await pipeline.process_opportunity(opp_dict)

        # Show final results
        print("\n" + "="*70)
        print("📊 PIPELINE RESULTS")
        print("="*70)

        print(f"\n📋 Project ID: {project['id']}")
        print(f"📌 Final Status: {project['status']}")

        # Show checkpoints
        print(f"\n✅ Completed Checkpoints ({len(project['checkpoints'])}):")
        for checkpoint in project['checkpoints']:
            print(f"   • {checkpoint['stage']}: {checkpoint['status']}")
            if 'decision' in checkpoint:
                print(f"     Decision: {checkpoint['decision']}")

        # Show financials
        if 'financial' in project:
            print(f"\n💰 Financial Summary:")
            print(f"   Revenue: ${project['financial']['budget']}")
            print(f"   Cost: ${project['financial']['cost']}")
            print(f"   Profit: ${project['financial']['profit']}")
            print(f"   Paid: {'✅' if project['financial']['paid'] else '❌'}")

        # Show deliverables
        if 'deliverables' in project:
            print(f"\n📦 Deliverables ({len(project['deliverables'])}):")
            for i, deliverable in enumerate(project['deliverables'][:3], 1):
                print(f"   {i}. {deliverable['task'][:50]}...")
                print(f"      Status: {deliverable['status']}")

    # Step 3: Show pipeline statistics
    print("\n" + "="*70)
    print("📈 PIPELINE STATISTICS")
    print("="*70)

    # Check pending approvals
    pending_approvals = await pipeline.get_pending_approvals()
    print(f"\n🔔 Pending Human Approvals: {len(pending_approvals)}")

    # Check Redis for stored data
    opportunity_keys = redis_client.keys('freelance:opportunity:*')
    project_keys = redis_client.keys('freelance:project:*')
    analysis_keys = redis_client.keys('freelance:analysis:*')

    print(f"\n📊 Data in System:")
    print(f"   Opportunities: {len(opportunity_keys)}")
    print(f"   Active Projects: {len(project_keys)}")
    print(f"   Analyses: {len(analysis_keys)}")

    # Show what agents would do
    print("\n" + "="*70)
    print("🤖 AGENT CAPABILITIES DEMONSTRATION")
    print("="*70)

    capabilities = {
        'content_creator_agent': [
            "Write SEO-optimized blog posts",
            "Create viral social media content",
            "Generate product descriptions"
        ],
        'code_generator_agent': [
            "Build REST APIs",
            "Create Python scripts",
            "Generate SQL queries"
        ],
        'data_analyst_agent': [
            "Analyze datasets",
            "Create visualizations",
            "Generate reports"
        ]
    }

    for agent, skills in capabilities.items():
        print(f"\n{agent}:")
        for skill in skills:
            print(f"   • {skill}")

    print("\n" + "="*70)
    print("✨ FREELANCE PIPELINE TEST COMPLETE")
    print("="*70)

    print("\n📌 Summary:")
    print("• Spiders find real freelance opportunities")
    print("• AI analyzes and creates project plans")
    print("• Human approves at key checkpoints")
    print("• Agents execute the actual work")
    print("• System handles delivery and payment")
    print("\n💰 Ready to generate real income!")

    await spider.cleanup()


if __name__ == '__main__':
    print("\n🚀 Starting Freelance Pipeline Test")
    print("This demonstrates the complete flow from finding jobs to getting paid")
    print("="*70)

    try:
        asyncio.run(test_complete_freelance_flow())
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()