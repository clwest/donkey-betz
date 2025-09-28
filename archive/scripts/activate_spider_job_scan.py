#!/usr/bin/env python
"""
Activate the Spider Army for Job Scanning
This connects the spider network to scan for jobs and present them for selection
"""

import os
import sys
import django
import asyncio
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from intelligence.unified_spider_job_bridge import UnifiedSpiderJobBridge
from ai_core.agents.intelligent_job_matcher import IntelligentJobMatcher


class SpiderJobScanner:
    """Orchestrates spider-based job scanning and agent matching"""

    def __init__(self):
        self.bridge = UnifiedSpiderJobBridge()
        self.matcher = None
        try:
            self.matcher = IntelligentJobMatcher()
        except Exception as e:
            print(f"⚠️ Intelligent matcher not fully available: {e}")

    async def scan_for_jobs(self, user_criteria: dict = None):
        """Deploy spiders to scan for job opportunities"""
        print("\n" + "="*70)
        print("🕷️ ACTIVATING SPIDER ARMY FOR JOB SCANNING")
        print("="*70)

        # Default search criteria if none provided
        if not user_criteria:
            user_criteria = {
                'keywords': ['python', 'AI', 'machine learning', 'remote', 'developer'],
                'locations': ['remote', 'worldwide'],
                'job_types': ['full-time', 'contract', 'freelance'],
                'min_budget': 1000,
                'experience_level': ['mid', 'senior']
            }

        print(f"\n🔍 Search Criteria:")
        for key, value in user_criteria.items():
            print(f"   {key}: {value}")

        # Deploy spider network
        print("\n🚀 Deploying Spider Network...")
        deployment = await self.bridge.activate_spider_deployment(
            user_request="Find high-value job opportunities",
            search_criteria=user_criteria
        )

        print(f"\n✅ Deployment Complete!")
        print(f"   - Deployment ID: {deployment['deployment_id']}")
        print(f"   - Spiders Activated: {deployment['spider_count']}")
        print(f"   - Jobs Found: {deployment['jobs_found']}")
        print(f"   - Sources: {', '.join(deployment['sources'])}")

        # Get the collected jobs
        from django.core.cache import cache
        jobs = cache.get('unified_live_jobs', [])

        return jobs

    async def match_agents_to_jobs(self, jobs: list):
        """Match agents to the collected jobs"""
        print("\n" + "="*70)
        print("🤖 MATCHING AGENTS TO JOBS")
        print("="*70)

        if not self.matcher:
            print("⚠️ Using simple matching (ML matcher not available)")
            return self._simple_match(jobs)

        matched_jobs = []
        for job in jobs[:10]:  # Process top 10 jobs
            print(f"\n📋 Analyzing: {job.get('title', 'Unknown')}")

            try:
                match = await self.matcher.match_job_with_learning(job)
                if match:
                    job['agent_match'] = match
                    matched_jobs.append(job)
                    print(f"   ✅ Matched to: {match['agent']['name']}")
                    print(f"   📊 Confidence: {match['confidence']:.0%}")
            except Exception as e:
                print(f"   ⚠️ Matching failed: {e}")

        return matched_jobs

    def _simple_match(self, jobs: list):
        """Simple fallback matching when ML matcher unavailable"""
        # Basic keyword-based matching
        agent_specialties = {
            'Python Developer': ['python', 'django', 'flask', 'backend'],
            'AI Specialist': ['AI', 'machine learning', 'ML', 'neural', 'deep learning'],
            'Frontend Developer': ['react', 'vue', 'javascript', 'frontend', 'UI'],
            'Data Scientist': ['data', 'analysis', 'statistics', 'pandas', 'numpy'],
            'Content Creator': ['content', 'writing', 'blog', 'article', 'copy'],
            'DevOps Engineer': ['devops', 'aws', 'docker', 'kubernetes', 'CI/CD']
        }

        matched_jobs = []
        for job in jobs[:10]:
            job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()

            best_agent = None
            best_score = 0

            for agent_name, keywords in agent_specialties.items():
                score = sum(1 for kw in keywords if kw.lower() in job_text)
                if score > best_score:
                    best_score = score
                    best_agent = agent_name

            if best_agent:
                job['agent_match'] = {
                    'agent': {'name': best_agent},
                    'confidence': min(0.9, best_score * 0.2),
                    'match_score': best_score / 10
                }
                matched_jobs.append(job)

        return matched_jobs

    async def present_for_selection(self, matched_jobs: list):
        """Present matched jobs for user selection"""
        print("\n" + "="*70)
        print("📌 JOBS READY FOR SELECTION")
        print("="*70)

        if not matched_jobs:
            print("❌ No jobs found matching your criteria")
            return []

        print(f"\n✨ Found {len(matched_jobs)} matched opportunities:\n")

        for i, job in enumerate(matched_jobs, 1):
            print(f"\n[{i}] {job.get('title', 'Unknown Title')}")
            print(f"    Company: {job.get('company', 'N/A')}")
            print(f"    Location: {job.get('location', 'N/A')}")
            print(f"    Budget/Salary: {job.get('budget', job.get('salary', 'N/A'))}")

            if 'agent_match' in job:
                agent = job['agent_match']['agent']['name']
                confidence = job['agent_match']['confidence']
                print(f"    🤖 Recommended Agent: {agent} ({confidence:.0%} confidence)")

            if job.get('description'):
                desc = job['description'][:150] + '...' if len(job['description']) > 150 else job['description']
                print(f"    Description: {desc}")

            print(f"    Source: {job.get('source', 'Spider Network')}")
            print(f"    URL: {job.get('url', 'N/A')}")

        # Simulate user selection
        print("\n" + "-"*70)
        print("💡 To select jobs, you would normally interact through the UI")
        print("   For now, let's simulate selecting jobs 1, 3, and 5")

        selected_indices = [0, 2, 4] if len(matched_jobs) >= 5 else list(range(min(3, len(matched_jobs))))
        selected_jobs = [matched_jobs[i] for i in selected_indices if i < len(matched_jobs)]

        print(f"\n✅ Selected {len(selected_jobs)} jobs for application")
        for job in selected_jobs:
            print(f"   - {job.get('title')}")

        return selected_jobs


async def main():
    """Main execution flow"""
    scanner = SpiderJobScanner()

    # Step 1: Deploy spiders to scan for jobs
    print("\n🕷️ SPIDER JOB SCANNING SYSTEM")
    print("="*70)

    # You can customize search criteria here
    search_criteria = {
        'keywords': ['python', 'AI', 'remote', 'developer', 'freelance'],
        'locations': ['remote', 'worldwide', 'USA'],
        'job_types': ['full-time', 'contract', 'freelance', 'part-time'],
        'min_budget': 500,
        'max_budget': 10000,
        'experience_level': ['entry', 'mid', 'senior']
    }

    # Scan for jobs using spiders
    jobs = await scanner.scan_for_jobs(search_criteria)

    if not jobs:
        # Create mock jobs for demonstration
        print("\n⚠️ No live spider data available - using demonstration data")
        jobs = [
            {
                'id': 'spider_1',
                'title': 'Senior Python AI Developer',
                'company': 'TechCorp (via Spider)',
                'location': 'Remote',
                'description': 'Build AI models and ML pipelines using Python and TensorFlow',
                'budget': '$5000-$8000/month',
                'source': 'Upwork Spider',
                'url': 'https://upwork.com/job/123',
                'tags': ['python', 'AI', 'tensorflow']
            },
            {
                'id': 'spider_2',
                'title': 'Content Writer for AI Blog',
                'company': 'AI Media',
                'location': 'Remote',
                'description': 'Write technical articles about AI and machine learning',
                'budget': '$500-$1000/article',
                'source': 'Freelancer Spider',
                'url': 'https://freelancer.com/job/456',
                'tags': ['writing', 'AI', 'content']
            },
            {
                'id': 'spider_3',
                'title': 'Full Stack Developer - Startup',
                'company': 'StartupX',
                'location': 'San Francisco, CA',
                'description': 'Join our team building the next unicorn with React and Node.js',
                'salary': '$150k-$200k',
                'source': 'Indeed Spider',
                'url': 'https://indeed.com/job/789',
                'tags': ['react', 'node.js', 'startup']
            },
            {
                'id': 'spider_4',
                'title': 'Freelance Data Scientist',
                'company': 'DataCo',
                'location': 'Remote',
                'description': 'Analyze customer data and build predictive models',
                'budget': '$75-$150/hour',
                'source': 'Fiverr Spider',
                'url': 'https://fiverr.com/gig/012',
                'tags': ['data science', 'python', 'analytics']
            },
            {
                'id': 'spider_5',
                'title': 'AI Chatbot Developer',
                'company': 'BotBuilders',
                'location': 'Remote',
                'description': 'Create conversational AI using GPT and LangChain',
                'budget': '$3000-$5000/project',
                'source': 'Upwork Spider',
                'url': 'https://upwork.com/job/345',
                'tags': ['AI', 'chatbot', 'langchain', 'GPT']
            }
        ]

    # Step 2: Match agents to jobs
    matched_jobs = await scanner.match_agents_to_jobs(jobs)

    # Step 3: Present for selection
    selected_jobs = await scanner.present_for_selection(matched_jobs)

    print("\n" + "="*70)
    print("🎯 NEXT STEPS")
    print("="*70)
    print("\n1. Selected jobs are ready for agent execution")
    print("2. Each agent would now apply to their assigned job")
    print("3. Applications would be tracked in the system")
    print("4. Results would update in real-time via WebSocket")

    print("\n💡 To fully activate:")
    print("   - Connect this to the frontend UI for selection")
    print("   - Enable real spider deployments with actual web scraping")
    print("   - Wire up agent execution for applications")
    print("   - Track results and learn from outcomes")


if __name__ == "__main__":
    asyncio.run(main())