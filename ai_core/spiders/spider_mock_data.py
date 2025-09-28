"""
Mock Spider Data Generator
Provides realistic mock data when real spiders aren't available
"""

import random
from datetime import datetime, timedelta


def get_mock_opportunities(platform=None):
    """Generate realistic mock opportunities for testing"""

    platforms_data = {
        'toptal': {
            'rates': range(100, 200),
            'titles': ['Senior Python Developer', 'AI/ML Engineer', 'Full Stack Architect', 'DevOps Lead'],
            'duration': ['3-6 months', '6+ months', 'Long-term'],
        },
        'guru': {
            'rates': range(50, 120),
            'titles': ['Python Developer', 'Django Expert', 'API Developer', 'Backend Engineer'],
            'duration': ['1-3 months', '3-6 months', 'Project-based'],
        },
        'flexjobs': {
            'rates': range(60, 140),
            'titles': ['Remote Python Dev', 'Django Developer', 'Software Engineer', 'Tech Lead'],
            'duration': ['Full-time', 'Part-time', 'Contract'],
        },
        'remoteok': {
            'rates': range(80, 160),
            'titles': ['Backend Developer', 'Python Engineer', 'API Specialist', 'Cloud Engineer'],
            'duration': ['Remote', 'Fully Remote', 'Remote-first'],
        },
        'peopleperhour': {
            'rates': range(40, 100),
            'titles': ['Quick Python Fix', 'Django Setup', 'API Integration', 'Bug Fixing'],
            'duration': ['Hours', 'Days', '1 week'],
        }
    }

    # Select platform
    if platform and platform in platforms_data:
        platforms = [platform]
    else:
        platforms = list(platforms_data.keys())

    opportunities = []

    for plat in platforms:
        data = platforms_data[plat]
        num_opportunities = random.randint(2, 5)

        for i in range(num_opportunities):
            rate = random.choice(list(data['rates']))
            title = random.choice(data['titles'])
            duration = random.choice(data['duration'])

            opportunity = {
                'id': f"{plat}_{random.randint(10000, 99999)}",
                'title': f"{title} - {random.choice(['Urgent', 'ASAP', 'Immediate', 'Flexible'])}",
                'platform': plat.title(),
                'rate': f"${rate}/hour",
                'estimated_earnings': rate * random.randint(10, 160),
                'budget_range': f"${rate * 10} - ${rate * 40}",
                'description': f"Seeking experienced {title} for exciting project. Must have strong Python/Django skills.",
                'skills_required': ['Python', 'Django', 'REST API', 'PostgreSQL', 'Docker'],
                'duration': duration,
                'posted': f"{random.randint(1, 48)} hours ago",
                'deadline': f"{random.randint(1, 14)} days",
                'url': f"https://{plat}.com/job/{random.randint(100000, 999999)}",
                'client_rating': round(random.uniform(4.0, 5.0), 1),
                'client_reviews': random.randint(5, 200),
                'applicants': random.randint(0, 50),
                'match_score': round(random.uniform(0.7, 0.95), 2),
                'source': 'spider_network',
                'real_data': False,  # Mark as mock for transparency
                'spider': f"{plat}_spider"
            }
            opportunities.append(opportunity)

    return opportunities


def get_spider_stats():
    """Get mock spider statistics"""
    return {
        'success': True,
        'spiders_activated': 5,
        'opportunities_collected': len(get_mock_opportunities()),
        'platforms': ['Toptal', 'Guru', 'FlexJobs', 'RemoteOK', 'PeoplePerHour'],
        'last_run': datetime.now().isoformat(),
        'next_run': (datetime.now() + timedelta(hours=1)).isoformat(),
        'data_source': 'mock_fallback',
        'opportunities': get_mock_opportunities()
    }


def activate_job_spiders_mock(user_profile=None):
    """Mock version of activate_job_spiders that always works"""
    return get_spider_stats()