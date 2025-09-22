#!/usr/bin/env python3
"""
Check and display completed work from agents
"""
import redis
import json
from datetime import datetime

def check_completed_projects():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    print("\n" + "="*60)
    print("🎯 COMPLETED AGENT WORK - READY FOR REVIEW")
    print("="*60)

    project_keys = r.keys('freelance:project:*')
    completed_projects = []

    for project_key in project_keys:
        project_data = r.get(project_key)
        if project_data:
            project = json.loads(project_data)

            if project.get('status') == 'completed':
                completed_projects.append(project)

    if not completed_projects:
        print("❌ No completed projects found yet.")
        print("   Projects are still in progress...")
        return

    print(f"\n✅ Found {len(completed_projects)} completed projects!\n")

    for i, project in enumerate(completed_projects, 1):
        print(f"{'='*60}")
        print(f"📦 COMPLETED PROJECT #{i}")
        print(f"{'='*60}")

        # Basic info
        print(f"ID: {project.get('id')}")
        print(f"Title: {project.get('opportunity', {}).get('title')}")
        print(f"Budget: ${project.get('opportunity', {}).get('budget')}")
        print(f"Platform: {project.get('opportunity', {}).get('platform')}")

        # Agent info
        agent_team = project.get('analysis', {}).get('agent_team', {})
        print(f"\n🤖 Lead Agent: {agent_team.get('lead_agent', 'Unknown')}")
        if agent_team.get('supporting_agents'):
            print(f"Support Team: {', '.join(agent_team['supporting_agents'])}")

        # Completion info
        print(f"\n✅ Status: {project.get('status')}")
        print(f"Progress: {project.get('progress', 0):.1f}%")
        if project.get('completed_at'):
            print(f"Completed: {project['completed_at'][:19]}")

        # Deliverable info
        deliverable = project.get('deliverable')
        if deliverable:
            print(f"\n📄 DELIVERABLE:")
            print(f"   Type: {deliverable.get('type', 'Unknown')}")
            print(f"   Title: {deliverable.get('title', 'Unknown')}")
            print(f"   Quality Score: {deliverable.get('quality_score', 0)*100:.1f}%")

            # Type-specific details
            if deliverable.get('lines_of_code'):
                print(f"   Lines of Code: {deliverable['lines_of_code']}")
                print(f"   Language: {deliverable.get('language', 'Unknown')}")
            elif deliverable.get('word_count'):
                print(f"   Word Count: {deliverable['word_count']}")
                print(f"   SEO Score: {deliverable.get('seo_score', 0)*100:.1f}%")
            elif deliverable.get('data_points'):
                print(f"   Data Points: {deliverable['data_points']}")
                print(f"   Insights: {deliverable.get('insights', 0)}")

            print(f"   Size: {deliverable.get('size', 0):,} bytes")
        else:
            print(f"\n⚠️  No deliverable information available")

        # Checkpoints
        checkpoints = project.get('checkpoints', [])
        if checkpoints:
            print(f"\n📊 WORK PROGRESS CHECKPOINTS:")
            for checkpoint in checkpoints[-3:]:  # Show last 3 checkpoints
                print(f"   • {checkpoint['progress']}% - {checkpoint['status']} ({checkpoint['timestamp'][:19]})")

    print(f"\n{'='*60}")
    print(f"💰 TOTAL VALUE: ${sum(p.get('opportunity', {}).get('budget', 0) for p in completed_projects)}")
    print(f"🏆 AGENTS DEPLOYED: {len(set(p.get('analysis', {}).get('agent_team', {}).get('lead_agent', 'Unknown') for p in completed_projects))}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    check_completed_projects()