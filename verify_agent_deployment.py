#!/usr/bin/env python3
"""
Verify Agent Deployment Status
Shows which agents are deployed and what they're working on
"""
import redis
import json
from datetime import datetime

def verify_deployments():
    """Check and display all deployed agents"""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    print("\n" + "="*60)
    print("🤖 AGENT DEPLOYMENT VERIFICATION")
    print("="*60)

    # Get all projects
    project_keys = r.keys('freelance:project:*')

    if not project_keys:
        print("❌ No projects found. Deploy some projects first!")
        return

    print(f"\n✅ Found {len(project_keys)} active projects\n")

    # Show each project and its assigned agent
    agents_deployed = []

    for i, project_key in enumerate(project_keys, 1):
        project_data = r.get(project_key)
        if project_data:
            project = json.loads(project_data)

            # Extract info
            project_id = project.get('id', 'unknown')
            opportunity = project.get('opportunity', {})
            title = opportunity.get('title', 'Unknown Task')
            budget = opportunity.get('budget', 0)
            platform = opportunity.get('platform', 'Unknown')
            agent_team = project.get('analysis', {}).get('agent_team', {})
            lead_agent = agent_team.get('lead_agent', 'Unknown Agent')
            supporting_agents = agent_team.get('supporting_agents', [])
            status = project.get('status', 'unknown')
            created = project.get('created_at', 'unknown')

            # Display
            print(f"📦 Project {i}: {project_id}")
            print(f"   Task: {title}")
            print(f"   Budget: ${budget} ({platform})")
            print(f"   Lead Agent: {lead_agent}")
            if supporting_agents:
                print(f"   Support Team: {', '.join(supporting_agents)}")
            print(f"   Status: {status}")
            print(f"   Created: {created[:19] if len(created) > 19 else created}")
            print()

            if status == 'active':
                agents_deployed.append({
                    'agent': lead_agent,
                    'task': title,
                    'budget': budget
                })

    # Summary
    print("="*60)
    print("📊 DEPLOYMENT SUMMARY")
    print("="*60)

    # Count unique agents
    unique_agents = list(set(a['agent'] for a in agents_deployed))
    total_value = sum(a['budget'] for a in agents_deployed)

    print(f"✅ {len(unique_agents)} unique agents deployed")
    print(f"💰 ${total_value} total project value")
    print(f"🤖 Active agents: {', '.join(unique_agents)}")

    print("\n🎯 TO VERIFY IN UI:")
    print("1. Open http://localhost:5173 in your browser")
    print("2. Check the '152 Agent Army - Live Activity Monitor'")
    print("3. You should see these agents marked as 'working':")
    for agent in agents_deployed:
        print(f"   - {agent['agent']} → {agent['task']}")

    print("\n💡 TIP: Open browser console (F12) to see real-time agent logs!")
    print("   Look for messages like:")
    print("   🤖 AGENT STATUS UPDATE")
    print("   ✅ AGENT DEPLOYED")
    print("   🚀 PROJECT DEPLOYED")

if __name__ == "__main__":
    verify_deployments()