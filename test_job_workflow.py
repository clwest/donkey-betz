#!/usr/bin/env python
"""
Test the complete job scanning and selection workflow
"""

import django
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

import asyncio
import json
from datetime import datetime

# Sample jobs to test with
SAMPLE_JOBS = [
    {
        'id': '1',
        'title': 'Senior Python Developer - Remote',
        'company': 'TechCorp',
        'location': 'Remote',
        'description': 'Looking for experienced Python developer with Django and ML skills',
        'tags': ['python', 'django', 'machine learning', 'remote'],
        'salary': '$120k-$180k',
        'type': 'full-time'
    },
    {
        'id': '2',
        'title': 'AI Content Writer',
        'company': 'ContentAI',
        'location': 'Remote',
        'description': 'Create engaging AI-powered content for various platforms',
        'tags': ['writing', 'content', 'AI', 'remote'],
        'salary': '$60k-$90k',
        'type': 'contract'
    },
    {
        'id': '3',
        'title': 'Full Stack Engineer',
        'company': 'StartupX',
        'location': 'San Francisco, CA',
        'description': 'Build next-gen web applications with React and Node.js',
        'tags': ['javascript', 'react', 'node.js', 'typescript'],
        'salary': '$140k-$200k',
        'type': 'full-time'
    },
    {
        'id': '4',
        'title': 'Data Scientist',
        'company': 'DataCo',
        'location': 'New York, NY',
        'description': 'Analyze large datasets and build predictive models',
        'tags': ['python', 'data science', 'tensorflow', 'sql'],
        'salary': '$130k-$190k',
        'type': 'full-time'
    },
    {
        'id': '5',
        'title': 'DevOps Engineer',
        'company': 'CloudOps',
        'location': 'Remote',
        'description': 'Manage cloud infrastructure and CI/CD pipelines',
        'tags': ['aws', 'docker', 'kubernetes', 'terraform'],
        'salary': '$110k-$160k',
        'type': 'full-time'
    }
]

async def test_basic_job_scanning():
    """Test basic job scanning functionality"""
    print("\n" + "="*60)
    print("🔍 TESTING JOB SCANNING WORKFLOW")
    print("="*60)

    # Try to use the intelligent job matcher if available
    try:
        # Check if we can import without the missing ml_pipeline
        from agents.registry import agent_registry

        print(f"\n✅ Agent Registry loaded")
        print(f"📊 Total agents available: {len(agent_registry.agents)}")

        # List some agents
        agent_list = list(agent_registry.agents.items())[:5]
        print("\n🤖 Sample Agents:")
        for agent_id, agent in agent_list:
            print(f"  - {agent.get('name', 'Unknown')} ({agent.get('specialization', 'General')})")
    except Exception as e:
        print(f"⚠️ Agent registry not fully available: {e}")

    # Test job filtering and selection
    print(f"\n📋 Available Jobs: {len(SAMPLE_JOBS)}")
    for job in SAMPLE_JOBS:
        print(f"\n  Job: {job['title']}")
        print(f"  Company: {job['company']}")
        print(f"  Location: {job['location']}")
        print(f"  Salary: {job['salary']}")
        print(f"  Tags: {', '.join(job['tags'])}")

    return SAMPLE_JOBS

async def test_job_selection():
    """Test job selection and filtering"""
    print("\n" + "="*60)
    print("🎯 TESTING JOB SELECTION")
    print("="*60)

    # Simulate user selecting jobs
    selected_indices = [0, 2, 4]  # Select jobs 1, 3, and 5
    selected_jobs = [SAMPLE_JOBS[i] for i in selected_indices]

    print(f"\n✅ User selected {len(selected_jobs)} jobs:")
    for job in selected_jobs:
        print(f"  - {job['title']} at {job['company']}")

    return selected_jobs

async def test_agent_assignment():
    """Test assigning agents to selected jobs"""
    print("\n" + "="*60)
    print("🤖 TESTING AGENT ASSIGNMENT")
    print("="*60)

    selected_jobs = await test_job_selection()

    # Mock agent assignments (since full system might not be available)
    assignments = [
        {
            'job': selected_jobs[0],
            'agent': 'Python Development Specialist',
            'confidence': 0.92,
            'match_reason': 'Strong Python and Django experience'
        },
        {
            'job': selected_jobs[1],
            'agent': 'Full Stack Developer Agent',
            'confidence': 0.85,
            'match_reason': 'React and Node.js expertise'
        },
        {
            'job': selected_jobs[2],
            'agent': 'DevOps Automation Expert',
            'confidence': 0.88,
            'match_reason': 'Cloud infrastructure and CI/CD skills'
        }
    ]

    print("\n📊 Agent Assignments:")
    for assignment in assignments:
        print(f"\n  Job: {assignment['job']['title']}")
        print(f"  Assigned Agent: {assignment['agent']}")
        print(f"  Confidence: {assignment['confidence']:.0%}")
        print(f"  Reason: {assignment['match_reason']}")

    return assignments

async def test_application_tracking():
    """Test tracking applications"""
    print("\n" + "="*60)
    print("📈 TESTING APPLICATION TRACKING")
    print("="*60)

    assignments = await test_agent_assignment()

    # Simulate application status
    applications = []
    for i, assignment in enumerate(assignments):
        app_status = ['submitted', 'in_review', 'interview_scheduled'][i]
        applications.append({
            'job_id': assignment['job']['id'],
            'job_title': assignment['job']['title'],
            'company': assignment['job']['company'],
            'agent': assignment['agent'],
            'status': app_status,
            'submitted_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        })

    print("\n📊 Application Status:")
    for app in applications:
        status_emoji = {
            'submitted': '📨',
            'in_review': '👀',
            'interview_scheduled': '🎯'
        }.get(app['status'], '❓')

        print(f"\n  {status_emoji} {app['job_title']} at {app['company']}")
        print(f"     Status: {app['status']}")
        print(f"     Agent: {app['agent']}")

    return applications

async def main():
    """Run the complete workflow test"""
    print("\n🚀 STARTING JOB WORKFLOW TEST")
    print("=" * 70)

    # Step 1: Scan for jobs
    jobs = await test_basic_job_scanning()

    # Step 2: User selects jobs
    selected = await test_job_selection()

    # Step 3: Assign agents to jobs
    assignments = await test_agent_assignment()

    # Step 4: Track applications
    applications = await test_application_tracking()

    print("\n" + "="*70)
    print("✅ WORKFLOW TEST COMPLETE")
    print("="*70)
    print("\n📊 Summary:")
    print(f"  - Jobs scanned: {len(jobs)}")
    print(f"  - Jobs selected: {len(selected)}")
    print(f"  - Agents assigned: {len(assignments)}")
    print(f"  - Applications tracked: {len(applications)}")

    print("\n💡 Next Steps:")
    print("  1. Connect to real job APIs (Indeed, LinkedIn, etc.)")
    print("  2. Integrate with actual agent execution")
    print("  3. Implement real-time application tracking")
    print("  4. Add user profile matching")
    print("  5. Enable automated follow-ups")

if __name__ == "__main__":
    asyncio.run(main())