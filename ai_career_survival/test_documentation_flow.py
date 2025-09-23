#!/usr/bin/env python3
"""
Test Documentation Flow
=======================

Verifies that:
1. Spiders collect data
2. Agents process it
3. Content Creation Agent documents the AI project
"""

import redis
import json
import time
from datetime import datetime
from content_documentation_agent import AIProjectDocumentationAgent


def inject_test_data():
    """
    Inject test data to simulate project activity
    """
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    print("💉 Injecting test project data...")

    # Simulate a freelance project
    project_id = f"test_proj_{int(time.time())}"
    r.hset(f"freelance:project:{project_id}", mapping={
        'title': 'AI-Powered Content Generation System',
        'description': 'Building an AI system that generates marketing content',
        'client': 'TechStartup Inc',
        'budget': '5000',
        'status': 'in_progress',
        'created_at': datetime.now().isoformat()
    })

    # Simulate agent task
    r.set(f"agent:task:content_generator_{int(time.time())}",
          json.dumps({
              'task': 'Generate blog posts about AI trends',
              'agent': 'content_creator',
              'status': 'completed',
              'output': 'Created 5 blog posts about AI in freelancing'
          }))

    # Simulate collaboration
    collab_id = f"collab_{int(time.time())}"
    r.lpush(f"collaboration:events:{collab_id}",
            json.dumps({
                'event': 'agents_working',
                'agents': ['content_creator', 'keyword_researcher', 'market_analyzer'],
                'task': 'Creating SEO-optimized content',
                'timestamp': datetime.now().isoformat()
            }))

    r.set(f"collaboration:completed:{collab_id}",
          json.dumps({
              'feature': 'Automated Content Pipeline',
              'result': 'Successfully created 10 pieces of content',
              'value_generated': 750
          }))

    print("✅ Test data injected")


def verify_data_flow():
    """
    Verify the complete data flow
    """
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    print("\n🔍 Verifying Data Flow:")
    print("="*50)

    # Check for spider data
    spider_keys = r.keys('spider:data:*')
    print(f"1. Spider Data Points: {len(spider_keys)}")

    # Check for freelance opportunities
    freelance_keys = r.keys('freelance:opportunity:*')
    print(f"2. Freelance Opportunities: {len(freelance_keys)}")

    # Check for agent activity
    agent_keys = r.keys('agent:*:activity')
    active_agents = []
    for key in agent_keys:
        agent_name = key.split(':')[1]
        active_agents.append(agent_name)
    print(f"3. Active Agents: {', '.join(active_agents) if active_agents else 'None'}")

    # Check for collaborations
    collab_keys = r.keys('collaboration:*')
    print(f"4. Agent Collaborations: {len(collab_keys)}")

    # Check for documentation
    doc_keys = r.keys('documentation:*')
    print(f"5. Documentation Created: {len(doc_keys)}")

    print("="*50)

    return len(spider_keys) > 0 or len(freelance_keys) > 0


def test_documentation_agent():
    """
    Test the documentation agent briefly
    """
    print("\n📚 Testing Documentation Agent...")

    agent = AIProjectDocumentationAgent()

    # Get and document any available project updates
    updates = agent.get_project_updates()
    if updates:
        print(f"   Found {len(updates)} project updates to document")
        for update in updates[:2]:  # Document first 2
            agent.document_project_progress(update)

    # Get and document completed features
    features = agent.get_completed_features()
    if features:
        print(f"   Found {len(features)} completed features to document")
        for feature in features[:1]:  # Document first one
            agent.create_feature_documentation(feature)

    # Check for collaborations
    collabs = agent.get_agent_collaborations()
    if collabs:
        print(f"   Found {len(collabs)} collaborations to document")
        agent.document_agent_interactions(collabs[:2])

    # Create summary if we have documentation
    if agent.documented_projects:
        summary = agent.create_project_summary()
        if summary:
            print(f"\n📊 Documentation Summary:")
            print(f"   Total Documents: {summary['total_documents']}")
            print(f"   Total Value: ${summary['total_value']}")


def main():
    """
    Main test flow
    """
    print("="*60)
    print("TESTING AI PROJECT DOCUMENTATION FLOW")
    print("="*60)

    # Inject test data
    inject_test_data()

    # Verify data exists
    has_data = verify_data_flow()

    if has_data:
        # Test documentation
        test_documentation_agent()
        print("\n✅ Documentation flow test complete!")
    else:
        print("\n⚠️ No data to document. Run spiders first:")
        print("   python start_spider_pipeline.py")


if __name__ == "__main__":
    main()