#!/usr/bin/env python
"""
Quick Population Script - Match Actual Model Fields
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from intelligence.models import OpportunityTracking
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("💰 QUICK OPPORTUNITY POPULATION")
print("=" * 80)

# Get or create a user
user, _ = User.objects.get_or_create(username='demo_user', defaults={'email': 'demo@example.com'})

opportunities = [
    {
        'opportunity_id': 'sports_bet_001',
        'opportunity_title': 'NBA: Warriors vs Lakers - Warriors ML',
        'opportunity_type': 'sports_bet',
        'title': 'NBA: Warriors vs Lakers - Warriors ML (-150)',
        'description': 'Golden State Warriors have won 7 of last 10 matchups. Strong home court advantage. Expected Value: 12%, Kelly Criterion suggests $80 bet.',
        'potential_revenue': Decimal('125.00'),
        'confidence_score': 0.78,
        'match_score': 0.85,
        'status': 'discovered',
    },
    {
        'opportunity_id': 'job_python_001',
        'opportunity_title': 'Senior Python Developer - Remote',
        'opportunity_type': 'job',
        'title': 'Senior Python Developer (Remote) - AI/ML Focus',
        'description': 'Build cutting-edge AI systems with Django, FastAPI, and modern ML frameworks. $120k-$150k salary, fully remote.',
        'potential_revenue': Decimal('8500.00'),
        'confidence_score': 0.92,
        'match_score': 0.95,
        'status': 'discovered',
        'target_monthly': Decimal('12500.00'),
    },
    {
        'opportunity_id': 'freelance_api_001',
        'opportunity_title': 'Build Django API for SaaS Platform',
        'opportunity_type': 'freelance',
        'title': 'Build Django API for SaaS Platform',
        'description': 'Design and implement RESTful API with authentication, payments, and webhooks. Budget: $3,500, Duration: 2 weeks.',
        'potential_revenue': Decimal('3500.00'),
        'confidence_score': 0.82,
        'match_score': 0.87,
        'status': 'discovered',
    },
    {
        'opportunity_id': 'job_fullstack_001',
        'opportunity_title': 'Full-Stack Engineer - Django + React',
        'opportunity_type': 'job',
        'title': 'Full-Stack Engineer - Django + React',
        'description': 'Join fast-growing startup. Great benefits, equity, and work-life balance. $100k-$130k salary.',
        'potential_revenue': Decimal('7200.00'),
        'confidence_score': 0.88,
        'match_score': 0.90,
        'status': 'discovered',
    },
    {
        'opportunity_id': 'sports_bet_002',
        'opportunity_title': 'NFL: Chiefs vs Bills - Over 48.5',
        'opportunity_type': 'sports_bet',
        'title': 'NFL: Chiefs vs Bills - Over 48.5 (+110)',
        'description': 'Two high-powered offenses averaging 28+ PPG. Expected Value: 15%, Kelly suggests $100 bet.',
        'potential_revenue': Decimal('200.00'),
        'confidence_score': 0.72,
        'match_score': 0.80,
        'status': 'discovered',
    },
    {
        'opportunity_id': 'freelance_ai_001',
        'opportunity_title': 'AI Chatbot Integration - GPT-4',
        'opportunity_type': 'freelance',
        'title': 'AI Chatbot Integration - OpenAI + Custom Logic',
        'description': 'Integrate GPT-4 with custom prompt engineering and RAG system. Budget: $4,200, Duration: 10 days.',
        'potential_revenue': Decimal('4200.00'),
        'confidence_score': 0.90,
        'match_score': 0.92,
        'status': 'discovered',
    },
    {
        'opportunity_id': 'job_ai_platform_001',
        'opportunity_title': 'AI Content Platform Engineer',
        'opportunity_type': 'job',
        'title': 'AI Content Platform Engineer',
        'description': 'Build intelligent content generation systems. Work with GPT-4, Claude, and custom ML models. $110k-$140k.',
        'potential_revenue': Decimal('7800.00'),
        'confidence_score': 0.85,
        'match_score': 0.88,
        'status': 'discovered',
    },
    {
        'opportunity_id': 'sports_bet_003',
        'opportunity_title': 'MLB: Dodgers vs Giants - Dodgers -1.5',
        'opportunity_type': 'sports_bet',
        'title': 'MLB: Dodgers vs Giants - Dodgers -1.5 (+125)',
        'description': 'Dodgers ace pitcher on mound with 2.15 ERA. Expected Value: 10%, Kelly suggests $60 bet.',
        'potential_revenue': Decimal('150.00'),
        'confidence_score': 0.68,
        'match_score': 0.75,
        'status': 'discovered',
    },
]

created = 0
for opp in opportunities:
    try:
        OpportunityTracking.objects.create(
            user=user,
            **opp
        )
        print(f"✅ Created: {opp['opportunity_title']}")
        created += 1
    except Exception as e:
        print(f"❌ Failed: {opp['opportunity_title']} - {e}")

print(f"\n✅ Successfully created {created}/{len(opportunities)} opportunities!")
print("\n🚀 Next Steps:")
print("   1. Navigate to: http://localhost:8000/income/")
print("   2. See your Income Builder with REAL opportunities!")
print("\n")
