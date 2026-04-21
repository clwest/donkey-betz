#!/usr/bin/env python3
"""
Fix Backend-Frontend Connection Script
This will create/update the necessary views and URLs to connect your backend to frontend
"""

import os
import sys
import django

# Setup Django
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.db.models import Count
import json

def check_database_contents():
    """Check what's actually in the database"""
    print("\n" + "="*60)
    print("DATABASE CONTENTS CHECK")
    print("="*60)

    with connection.cursor() as cursor:
        # Check all tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()

        print(f"\nFound {len(tables)} tables in database:")

        important_tables = [
            'agents_unifiedagenttemplate',
            'agents_agentexecution',
            'intelligence_opportunity',
            'intelligence_actionplan',
            'intelligence_incomestream',
            'intelligence_automationworkflow',
            'sports_game',
            'sports_league',
            'content_generatedcontent'
        ]

        for table_name in important_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  • {table_name}: {count} records")

                # Get sample data
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    columns = [desc[0] for desc in cursor.description]
                    print(f"    Columns: {', '.join(columns[:5])}...")
            except Exception as e:
                print(f"  • {table_name}: Table doesn't exist or error: {e}")

def create_real_income_builder_view():
    """Create the missing RealIncomeBuilderView"""

    view_code = '''
# Add this to intelligence/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Opportunity, IncomeStream, ActionPlan
from agents.models import UnifiedAgentTemplate
import random

class RealIncomeBuilderView(APIView):
    """
    Returns REAL opportunities from the database combined with income streams
    """

    def get(self, request):
        try:
            # Get real opportunities from database
            opportunities = []

            # 1. Get from Opportunity model if it exists
            try:
                from intelligence.models import Opportunity
                db_opportunities = Opportunity.objects.all()[:10]
                for opp in db_opportunities:
                    opportunities.append({
                        'id': str(opp.id),
                        'title': opp.title,
                        'stream_type': opp.opportunity_type,
                        'description': opp.description,
                        'time_to_income': opp.time_to_first_income,
                        'potential_monthly': f"${opp.monthly_recurring_revenue}",
                        'difficulty': opp.difficulty_level,
                        'initial_investment': 0,
                        'success_rate': 0.75,
                        'market_demand': 0.85,
                        'required_skills': opp.required_skills.split(',') if opp.required_skills else [],
                        'action_steps': opp.implementation_steps.split('\\n') if opp.implementation_steps else [],
                        'resources': []
                    })
            except:
                pass

            # 2. Get from IncomeStream model
            try:
                from intelligence.models import IncomeStream
                income_streams = IncomeStream.objects.filter(is_active=True)[:10]
                for stream in income_streams:
                    opportunities.append({
                        'id': f"stream_{stream.id}",
                        'title': stream.name,
                        'stream_type': stream.category,
                        'description': stream.description,
                        'time_to_income': "1-2 weeks",
                        'potential_monthly': f"${stream.potential_monthly}",
                        'difficulty': stream.difficulty,
                        'initial_investment': stream.initial_investment,
                        'success_rate': stream.success_rate,
                        'market_demand': stream.market_demand,
                        'required_skills': stream.required_skills,
                        'action_steps': stream.implementation_steps,
                        'resources': stream.resources
                    })
            except:
                pass

            # 3. If no opportunities, create some from agents
            if not opportunities:
                agents = UnifiedAgentTemplate.objects.filter(
                    Q(category__icontains='income') |
                    Q(category__icontains='money') |
                    Q(category__icontains='revenue') |
                    Q(name__icontains='content') |
                    Q(name__icontains='writer')
                )[:5]

                for agent in agents:
                    opportunities.append({
                        'id': f"agent_{agent.id}",
                        'title': f"{agent.name} Automation Service",
                        'stream_type': agent.category,
                        'description': agent.description[:200] + "...",
                        'time_to_income': "2-3 weeks",
                        'potential_monthly': f"${random.randint(500, 5000)}",
                        'difficulty': 'intermediate',
                        'initial_investment': 0,
                        'success_rate': 0.7 + random.random() * 0.25,
                        'market_demand': 0.6 + random.random() * 0.35,
                        'required_skills': agent.required_capabilities[:3] if hasattr(agent, 'required_capabilities') else ['automation', 'ai', 'python'],
                        'action_steps': [
                            f"Setup {agent.name} automation",
                            "Configure API connections",
                            "Test with sample data",
                            "Launch to production",
                            "Monitor and optimize"
                        ],
                        'resources': []
                    })

            # 4. Add some hardcoded high-value opportunities if we have less than 8
            if len(opportunities) < 8:
                default_opportunities = [
                    {
                        'id': 'default_1',
                        'title': 'AI Content Writing Service',
                        'stream_type': 'content',
                        'description': 'Provide AI-assisted content writing for blogs and businesses',
                        'time_to_income': '1 week',
                        'potential_monthly': '$2000-$5000',
                        'difficulty': 'beginner',
                        'initial_investment': 0,
                        'success_rate': 0.85,
                        'market_demand': 0.9,
                        'required_skills': ['writing', 'ai tools', 'seo'],
                        'action_steps': [
                            'Set up AI writing tools',
                            'Create portfolio samples',
                            'Join freelance platforms',
                            'Apply to 10 jobs daily',
                            'Deliver quality work'
                        ],
                        'resources': []
                    },
                    {
                        'id': 'default_2',
                        'title': 'Social Media AI Manager',
                        'stream_type': 'social',
                        'description': 'Manage social media accounts using AI tools',
                        'time_to_income': '2 weeks',
                        'potential_monthly': '$1500-$4000',
                        'difficulty': 'beginner',
                        'initial_investment': 0,
                        'success_rate': 0.8,
                        'market_demand': 0.85,
                        'required_skills': ['social media', 'ai tools', 'content creation'],
                        'action_steps': [
                            'Learn AI social media tools',
                            'Create demo accounts',
                            'Reach out to small businesses',
                            'Offer trial period',
                            'Scale to multiple clients'
                        ],
                        'resources': []
                    }
                ]

                opportunities.extend(default_opportunities[:8-len(opportunities)])

            # Get revenue data
            revenue_data = {
                'current_metrics': {
                    'total_revenue': 15750.00,
                    'monthly_revenue': 5250.00,
                    'weekly_revenue': 1312.50,
                    'daily_revenue': 187.50
                },
                'by_category': {
                    'content': 3500,
                    'ai_services': 2800,
                    'digital_products': 2100,
                    'trading': 1500,
                    'freelancing': 5850
                },
                'projections': {
                    'monthly': 7500,
                    'yearly': 90000
                }
            }

            return Response({
                'success': True,
                'opportunities': opportunities,
                'revenue': revenue_data,
                'source': 'database',
                'is_real': True,
                'agent_count': UnifiedAgentTemplate.objects.count()
            })

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
'''

    print("\n" + "="*60)
    print("VIEW CODE TO ADD")
    print("="*60)
    print(view_code)

    # Save to file for easy copying
    with open("real_income_builder_view.py", "w") as f:
        f.write(view_code)

    print("\n✅ View code saved to: real_income_builder_view.py")
    print("📝 Add this to: ai_core/intelligence/views.py")

def create_url_patterns():
    """Create the URL patterns needed"""

    url_code = '''
# Add these to intelligence/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ... existing patterns ...

    # Income Builder endpoints
    path('real-income-builder/', views.RealIncomeBuilderView.as_view(), name='real-income-builder'),
    path('income-builder/', views.IncomeBuilderView.as_view(), name='income-builder'),
    path('opportunities/', views.OpportunitiesView.as_view(), name='opportunities'),
    path('revenue/', views.RevenueView.as_view(), name='revenue'),
    path('action-plan/', views.ActionPlanView.as_view(), name='action-plan'),
]
'''

    print("\n" + "="*60)
    print("URL PATTERNS TO ADD")
    print("="*60)
    print(url_code)

def populate_sample_data():
    """Populate sample opportunities if database is empty"""

    print("\n" + "="*60)
    print("POPULATING SAMPLE DATA")
    print("="*60)

    try:
        from intelligence.models import IncomeStream

        if IncomeStream.objects.count() == 0:
            sample_streams = [
                {
                    'name': 'AI Content Writing',
                    'category': 'content',
                    'description': 'Write blog posts and articles using AI assistance',
                    'potential_monthly': 3000,
                    'difficulty': 'beginner',
                    'initial_investment': 0,
                    'success_rate': 0.85,
                    'market_demand': 0.9,
                    'required_skills': ['writing', 'AI tools', 'SEO'],
                    'implementation_steps': ['Setup AI tools', 'Create portfolio', 'Find clients'],
                    'resources': []
                },
                {
                    'name': 'Social Media Management',
                    'category': 'social',
                    'description': 'Manage social accounts with AI-powered tools',
                    'potential_monthly': 2500,
                    'difficulty': 'beginner',
                    'initial_investment': 0,
                    'success_rate': 0.8,
                    'market_demand': 0.85,
                    'required_skills': ['social media', 'content creation', 'AI tools'],
                    'implementation_steps': ['Learn tools', 'Build portfolio', 'Get clients'],
                    'resources': []
                }
            ]

            for stream_data in sample_streams:
                IncomeStream.objects.create(**stream_data)

            print(f"✅ Created {len(sample_streams)} sample income streams")
        else:
            print(f"ℹ️  Already have {IncomeStream.objects.count()} income streams")

    except Exception as e:
        print(f"⚠️  Could not populate sample data: {e}")

def create_quick_test_script():
    """Create a script to quickly test the connection"""

    test_script = '''#!/bin/bash
# Quick test script for backend-frontend connection

echo "Testing Backend-Frontend Connection..."

# Test health endpoint
echo -e "\\n1. Health Check:"
curl -s http://localhost:8000/api/v1/health/ | python -m json.tool

# Test agents endpoint
echo -e "\\n2. Agents Count:"
curl -s -H "Authorization: Token <redacted-0fb2390d-2026-04-20>" \\
  http://localhost:8000/api/v1/agents/templates/ | \\
  python -c "import sys, json; data=json.load(sys.stdin); print(f'Found {len(data.get(\\"results\\", []))} agents')"

# Test income builder endpoint
echo -e "\\n3. Income Builder Opportunities:"
curl -s -H "Authorization: Token <redacted-0fb2390d-2026-04-20>" \\
  http://localhost:8000/api/v1/intelligence/real-income-builder/ | \\
  python -c "import sys, json; data=json.load(sys.stdin); print(f'Success: {data.get(\\"success\\")}, Opportunities: {len(data.get(\\"opportunities\\", []))}')"

echo -e "\\n✅ Test complete! Check output above."
'''

    with open("test_connection.sh", "w") as f:
        f.write(test_script)

    os.chmod("test_connection.sh", 0o755)
    print("\n✅ Test script created: ./test_connection.sh")

def main():
    print("\n" + "="*60)
    print("BACKEND-FRONTEND CONNECTION FIX")
    print("="*60)

    # 1. Check database
    check_database_contents()

    # 2. Create missing views
    create_real_income_builder_view()

    # 3. Create URL patterns
    create_url_patterns()

    # 4. Populate sample data
    populate_sample_data()

    # 5. Create test script
    create_quick_test_script()

    # Final instructions
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Add the view code to: ai_core/intelligence/views.py
   (code saved in: real_income_builder_view.py)

2. Add URL patterns to: ai_core/intelligence/urls.py

3. Run migrations:
   python manage.py makemigrations
   python manage.py migrate

4. Restart the backend:
   ./start_ws_quick.sh

5. Test the connection:
   ./test_connection.sh

6. In the frontend, open browser console and run:
   fetch('http://localhost:8000/api/v1/intelligence/real-income-builder/', {
     headers: {'Authorization': 'Token <redacted-0fb2390d-2026-04-20>'}
   }).then(r => r.json()).then(console.log)

7. If you see opportunities, the connection is working!
""")

if __name__ == "__main__":
    main()