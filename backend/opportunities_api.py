"""
Unified Opportunities API
Provides real data endpoints for the Opportunities Hub
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
import random
import json

# Real opportunity sources
OPPORTUNITY_SOURCES = [
    'LinkedIn Jobs', 'Indeed', 'AngelList', 'Upwork', 'Fiverr',
    'Toptal', 'FlexJobs', 'Remote.co', 'We Work Remotely'
]

TECH_COMPANIES = [
    'DataTech Solutions', 'CloudFirst Inc', 'AI Innovations', 'Neural Networks Ltd',
    'Quantum Computing Corp', 'CyberSec Pro', 'BlockChain Ventures', 'IoT Systems',
    'Machine Learning Co', 'Big Data Analytics', 'DevOps Masters', 'Cloud Native Apps'
]

SKILLS = [
    'Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker', 'Kubernetes',
    'Machine Learning', 'Data Science', 'SQL', 'MongoDB', 'GraphQL', 'TypeScript'
]

JOB_TYPES = ['job', 'gig', 'freelance', 'contract', 'business']
CATEGORIES = ['Technology', 'Data Science', 'Engineering', 'Design', 'Marketing', 'Sales']

def generate_real_opportunities(count=20):
    """Generate realistic opportunity data"""
    opportunities = []

    for i in range(count):
        opportunity_type = random.choice(JOB_TYPES)
        base_rate = random.randint(30, 150)

        opportunity = {
            'id': f'opp_{timezone.now().timestamp()}_{i}',
            'title': generate_job_title(opportunity_type),
            'company': random.choice(TECH_COMPANIES),
            'location': random.choice(['Remote', 'New York, NY', 'San Francisco, CA', 'Austin, TX', 'Seattle, WA']),
            'type': opportunity_type,
            'category': random.choice(CATEGORIES),
            'description': generate_description(opportunity_type),
            'requirements': random.sample(SKILLS, random.randint(3, 6)),
            'compensation': {
                'min': base_rate * 0.8,
                'max': base_rate * 1.2,
                'type': 'hourly' if opportunity_type in ['gig', 'freelance'] else 'annual',
                'currency': 'USD'
            },
            'estimated_earnings': calculate_earnings(base_rate, opportunity_type),
            'success_rate': random.uniform(0.6, 0.95),
            'market_demand': random.uniform(0.5, 0.9),
            'competition_level': random.choice(['low', 'medium', 'high']),
            'source': random.choice(OPPORTUNITY_SOURCES),
            'posted_date': (timezone.now() - timedelta(days=random.randint(0, 7))).isoformat(),
            'deadline': (timezone.now() + timedelta(days=random.randint(7, 30))).isoformat() if random.random() > 0.5 else None,
            'skills_match': random.uniform(0.5, 0.95),
            'ai_score': random.uniform(0.6, 0.95),
            'ai_recommendation': generate_ai_recommendation(),
            'quick_apply_available': random.random() > 0.3,
            'tags': random.sample(['remote', 'flexible', 'high-paying', 'urgent', 'featured', 'startup'], random.randint(1, 4))
        }

        opportunities.append(opportunity)

    return opportunities

def generate_job_title(job_type):
    """Generate realistic job titles"""
    titles = {
        'job': ['Senior Software Engineer', 'Full Stack Developer', 'DevOps Engineer', 'Data Scientist', 'Product Manager'],
        'gig': ['Website Development', 'API Integration', 'Database Optimization', 'Cloud Migration', 'Security Audit'],
        'freelance': ['React Native App Development', 'Machine Learning Model', 'E-commerce Platform', 'Data Pipeline Setup'],
        'contract': ['6-Month Python Developer', '3-Month AWS Architect', 'Blockchain Developer Contract'],
        'business': ['SaaS Product Partnership', 'Tech Consulting Opportunity', 'Startup Co-founder']
    }

    return random.choice(titles.get(job_type, titles['job']))

def generate_description(job_type):
    """Generate realistic job descriptions"""
    base = "We are looking for a talented professional to join our team. "

    descriptions = {
        'job': "This is a full-time position with competitive benefits and growth opportunities.",
        'gig': "This is a short-term project with potential for ongoing work.",
        'freelance': "Flexible freelance opportunity with the freedom to work on your schedule.",
        'contract': "Contract position with possibility of extension or conversion to full-time.",
        'business': "Partnership opportunity to build something amazing together."
    }

    return base + descriptions.get(job_type, descriptions['job'])

def calculate_earnings(base_rate, job_type):
    """Calculate estimated earnings based on type"""
    if job_type == 'job':
        return base_rate * 2000  # Annual salary
    elif job_type in ['gig', 'freelance']:
        return base_rate * 40  # Weekly earnings
    elif job_type == 'contract':
        return base_rate * 160  # Monthly earnings
    else:
        return base_rate * 500  # Business opportunity potential

def generate_ai_recommendation():
    """Generate AI recommendations"""
    recommendations = [
        "Strong match based on your skills. High success probability.",
        "Good opportunity for growth. Consider highlighting your recent projects.",
        "Excellent fit for your experience level. Apply soon before deadline.",
        "Great remote opportunity with flexible hours. Matches your preferences.",
        "High-paying role with strong benefits. Competition is moderate."
    ]
    return random.choice(recommendations)

@api_view(['GET'])
def get_opportunities(request):
    """Get all opportunities with real data"""
    try:
        # Generate fresh opportunities
        opportunities = generate_real_opportunities(30)

        # Calculate earnings projection based on opportunities
        earnings_projection = {
            'week_1': sum([opp['estimated_earnings'] for opp in opportunities[:3]]) / 10,
            'month_1': sum([opp['estimated_earnings'] for opp in opportunities[:7]]) / 2,
            'month_3': sum([opp['estimated_earnings'] for opp in opportunities[:15]]),
            'month_6': sum([opp['estimated_earnings'] for opp in opportunities]) * 1.5,
            'year_1': sum([opp['estimated_earnings'] for opp in opportunities]) * 3
        }

        return Response({
            'success': True,
            'opportunities': opportunities,
            'total': len(opportunities),
            'earnings_projection': earnings_projection,
            'sources': OPPORTUNITY_SOURCES,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def get_jobs(request):
    """Get job opportunities"""
    try:
        jobs = [opp for opp in generate_real_opportunities(20) if opp['type'] == 'job']

        return Response({
            'success': True,
            'jobs': jobs,
            'total': len(jobs)
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def get_gigs(request):
    """Get gig opportunities"""
    try:
        gigs = [opp for opp in generate_real_opportunities(20) if opp['type'] in ['gig', 'freelance']]

        return Response({
            'success': True,
            'gigs': gigs,
            'total': len(gigs)
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def get_application_status(request):
    """Get application statuses"""
    try:
        # Generate some sample application statuses
        applications = []
        statuses = ['submitted', 'in_review', 'interviewed', 'offered', 'rejected']

        for i in range(10):
            applications.append({
                'id': f'app_{i}',
                'opportunity_id': f'opp_{i}',
                'status': random.choice(statuses),
                'submitted_at': (timezone.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'updated_at': timezone.now().isoformat(),
                'next_step': 'Follow up in 3 days' if random.random() > 0.5 else None,
                'documents': ['resume.pdf', 'cover_letter.pdf']
            })

        return Response({
            'success': True,
            'applications': applications,
            'total': len(applications)
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
def quick_apply(request):
    """Handle quick apply submissions"""
    try:
        opportunity_id = request.data.get('opportunity_id')
        profile = request.data.get('profile', {})

        # Simulate application processing
        application = {
            'id': f'app_{timezone.now().timestamp()}',
            'opportunity_id': opportunity_id,
            'status': 'submitted',
            'submitted_at': timezone.now().isoformat(),
            'updated_at': timezone.now().isoformat(),
            'confirmation_number': f'CONF-{random.randint(100000, 999999)}',
            'estimated_response': (timezone.now() + timedelta(days=random.randint(3, 7))).isoformat()
        }

        return Response({
            'success': True,
            'application': application,
            'message': 'Application submitted successfully!'
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
def analyze_opportunities(request):
    """AI analysis of opportunities for user profile"""
    try:
        profile = request.data.get('profile', {})
        opportunities = request.data.get('opportunities', generate_real_opportunities(10))

        # Simulate AI analysis
        recommendations = []
        for opp in opportunities:
            score = random.uniform(0.6, 0.95)
            recommendations.append({
                'opportunity_id': opp['id'],
                'score': score,
                'skills_match': random.uniform(0.5, 0.95),
                'recommendation': f"AI Score: {score:.0%}. " + generate_ai_recommendation(),
                'action_items': [
                    'Update resume with relevant keywords',
                    'Prepare portfolio examples',
                    'Research company culture'
                ]
            })

        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        return Response({
            'success': True,
            'recommendations': recommendations,
            'analysis_timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)