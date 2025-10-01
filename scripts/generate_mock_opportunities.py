#!/usr/bin/env python
"""
Generate Mock Opportunities for Development
Creates realistic opportunity data in the database for testing and development
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from intelligence.models import OpportunityTracking

User = get_user_model()


# Mock opportunity templates
OPPORTUNITY_TEMPLATES = [
    {
        'title': 'Full Stack Developer - AI SaaS Platform',
        'type': 'fulltime',
        'platform': 'LinkedIn',
        'source': 'linkedin_jobs',
        'budget_min': 80000,
        'budget_max': 120000,
        'skills': ['Python', 'React', 'PostgreSQL', 'Docker', 'AWS'],
        'quality_score': 0.85,
        'experience_level': 'intermediate',
        'description': 'Build and maintain AI-powered SaaS platform. Work with modern stack including Python/Django, React, and cloud infrastructure.',
    },
    {
        'title': 'Django Backend Engineer - Remote OK',
        'type': 'fulltime',
        'platform': 'RemoteOK',
        'source': 'remoteok_spider',
        'budget_min': 70000,
        'budget_max': 110000,
        'skills': ['Django', 'Python', 'REST APIs', 'PostgreSQL'],
        'quality_score': 0.90,
        'experience_level': 'intermediate',
        'description': 'Remote position building scalable backend systems. Strong Django and API development experience required.',
    },
    {
        'title': 'AI/ML Content Generation - Freelance',
        'type': 'freelance',
        'platform': 'Upwork',
        'source': 'upwork_spider',
        'budget_min': 5000,
        'budget_max': 8000,
        'skills': ['GPT-4', 'Python', 'Content Strategy', 'NLP'],
        'quality_score': 0.88,
        'experience_level': 'advanced',
        'description': 'Build AI content generation system using GPT-4 API. 3-month contract with potential for extension.',
    },
    {
        'title': 'Python Automation Specialist',
        'type': 'contract',
        'platform': 'Freelancer',
        'source': 'freelancer_spider',
        'budget_min': 3500,
        'budget_max': 6000,
        'skills': ['Python', 'Automation', 'Web Scraping', 'APIs'],
        'quality_score': 0.75,
        'experience_level': 'beginner',
        'description': 'Automate data collection and processing workflows. Experience with web scraping and API integration preferred.',
    },
    {
        'title': 'Tech Blog Writer - AI & Development',
        'type': 'freelance',
        'platform': 'Contently',
        'source': 'content_spider',
        'budget_min': 200,
        'budget_max': 500,
        'skills': ['Technical Writing', 'AI', 'Python', 'Software Development'],
        'quality_score': 0.70,
        'experience_level': 'beginner',
        'description': 'Write technical blog posts about AI, machine learning, and software development. $200-$500 per article.',
    },
    {
        'title': 'React + Django Full Stack Developer',
        'type': 'contract',
        'platform': 'Toptal',
        'source': 'toptal_spider',
        'budget_min': 95000,
        'budget_max': 135000,
        'skills': ['React', 'Django', 'TypeScript', 'GraphQL', 'Docker'],
        'quality_score': 0.92,
        'experience_level': 'advanced',
        'description': 'Senior full stack role for fintech startup. Equity + competitive salary. Modern tech stack.',
    },
    {
        'title': 'AI Prompt Engineer - ChatGPT Integration',
        'type': 'freelance',
        'platform': 'Upwork',
        'source': 'upwork_spider',
        'budget_min': 4000,
        'budget_max': 7000,
        'skills': ['Prompt Engineering', 'ChatGPT', 'Python', 'API Integration'],
        'quality_score': 0.82,
        'experience_level': 'intermediate',
        'description': 'Design and optimize prompts for ChatGPT-powered customer service system. 2-3 month project.',
    },
    {
        'title': 'PostgreSQL Database Optimization',
        'type': 'contract',
        'platform': 'Gun.io',
        'source': 'gunio_spider',
        'budget_min': 8000,
        'budget_max': 12000,
        'skills': ['PostgreSQL', 'Database Optimization', 'SQL', 'Python'],
        'quality_score': 0.78,
        'experience_level': 'advanced',
        'description': 'Optimize database performance for high-traffic application. Query optimization and indexing expertise required.',
    },
    {
        'title': 'FastAPI Microservices Developer',
        'type': 'fulltime',
        'platform': 'AngelList',
        'source': 'angellist_spider',
        'budget_min': 90000,
        'budget_max': 130000,
        'skills': ['FastAPI', 'Python', 'Microservices', 'Docker', 'Kubernetes'],
        'quality_score': 0.87,
        'experience_level': 'intermediate',
        'description': 'Build microservices architecture using FastAPI. Startup environment with growth potential.',
    },
    {
        'title': 'Web Scraping & Data Pipeline Engineer',
        'type': 'contract',
        'platform': 'Upwork',
        'source': 'upwork_spider',
        'budget_min': 5500,
        'budget_max': 9000,
        'skills': ['Python', 'Scrapy', 'BeautifulSoup', 'Data Engineering', 'AWS'],
        'quality_score': 0.80,
        'experience_level': 'intermediate',
        'description': 'Build robust web scraping pipelines and data processing workflows. Cloud deployment experience preferred.',
    },
]


def generate_mock_opportunities(count=250):
    """Generate mock opportunities in the database"""

    # Get or create first user
    user = User.objects.first()
    if not user:
        print("❌ No users found. Please create a user first.")
        return

    print(f"📊 Generating {count} mock opportunities for user: {user.username}")

    created_count = 0

    for i in range(count):
        # Pick a random template
        template = random.choice(OPPORTUNITY_TEMPLATES)

        # Add variation to make opportunities unique
        variation_suffix = f" #{i+1}"

        opportunity_data = {
            'id': f"mock_opp_{i+1}",
            'title': template['title'] + (variation_suffix if i >= len(OPPORTUNITY_TEMPLATES) else ''),
            'description': template['description'],
            'platform': template['platform'],
            'spider_source': template['source'],
            'url': f"https://example.com/jobs/mock_{i+1}",
            'budget_min': template['budget_min'],
            'budget_max': template['budget_max'],
            'skills_required': template['skills'],
            'quality_score': template['quality_score'] + random.uniform(-0.1, 0.1),  # Add randomness
            'experience_level': template['experience_level'],
            'opportunity_type': template['type'],
            'posted_at': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            'deadline': None,
        }

        # Create opportunity
        opp, created = OpportunityTracking.objects.get_or_create(
            opportunity_id=f"mock_opp_{i+1}",
            defaults={
                'user': user,
                'opportunity_title': opportunity_data['title'],
                'opportunity_type': template['type'],
                'opportunity_data': opportunity_data,
                'status': random.choice(['identified', 'identified', 'identified', 'analyzing']),  # Mostly identified
            }
        )

        if created:
            created_count += 1

        # Print progress
        if (i + 1) % 50 == 0:
            print(f"  ✅ Created {i+1}/{count} opportunities...")

    print(f"\n🎉 Successfully created {created_count} new opportunities!")
    print(f"📊 Total opportunities in database: {OpportunityTracking.objects.count()}")
    print(f"\n🌐 View them at: http://localhost:8000/unified/income-builder/")


if __name__ == '__main__':
    # Check command line args
    count = 250
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print("Usage: python generate_mock_opportunities.py [count]")
            sys.exit(1)

    generate_mock_opportunities(count)
