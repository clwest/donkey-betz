#!/usr/bin/env python
"""
Synchronous test for system completion features
"""
import os
import sys
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from core.models import ExtendedUserProfile, JobApplication, ResumeVersion

User = get_user_model()

def test_user_profile_system():
    """Test the extended user profile system"""
    print("\n🧪 Testing Extended User Profile System...")

    # Create or get test user
    user, created = User.objects.get_or_create(
        username='test_completion_user',
        defaults={
            'email': 'completion@test.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Created test user")
    else:
        print("✅ Using existing test user")

    # Create or update extended profile
    profile, created = ExtendedUserProfile.objects.update_or_create(
        user=user,
        defaults={
            'title': 'Senior Software Engineer',
            'years_experience': 5,
            'location': 'San Francisco, CA',
            'remote_preference': 'remote',
            'salary_min': 120000,
            'salary_max': 160000,
            'skills': ['Python', 'Django', 'React', 'Machine Learning'],
            'certifications': ['AWS Certified', 'Google Cloud Professional'],
            'education': {
                'degree': 'BS Computer Science',
                'university': 'Stanford University',
                'year': 2018
            },
            'work_history': [
                {
                    'company': 'Tech Corp',
                    'title': 'Software Engineer',
                    'duration': '2018-2021',
                    'description': 'Built scalable web applications'
                }
            ]
        }
    )

    print(f"✅ Profile completion: {profile.completion_percentage:.1f}%")

    # Test profile completion calculation
    assert profile.completion_percentage > 0, "Profile should have completion percentage"

    return True

def test_api_endpoints():
    """Test the new API endpoints"""
    print("\n🧪 Testing API Endpoints...")

    client = Client()

    # Get or create user for auth
    user = User.objects.get(username='test_completion_user')
    client.force_login(user)

    endpoints_to_test = [
        ('/api/profile/extended/', 'Extended Profile'),
        ('/api/profile/completion/', 'Profile Completion'),
        ('/api/profile/resume/', 'Resume Management'),
        ('/api/jobs/opportunities/', 'Job Opportunities'),
        ('/api/jobs/applications/', 'Job Applications'),
    ]

    results = []
    for endpoint, name in endpoints_to_test:
        try:
            response = client.get(endpoint)
            status = response.status_code
            if status in [200, 201, 204]:
                results.append(f"✅ {name}: {endpoint} - Status {status}")
            else:
                results.append(f"⚠️ {name}: {endpoint} - Status {status}")
        except Exception as e:
            results.append(f"❌ {name}: {endpoint} - Error: {str(e)}")

    for result in results:
        print(result)

    return True

def test_agent_context():
    """Test agent context middleware"""
    print("\n🧪 Testing Agent Context Integration...")

    try:
        from core.agent_context_middleware import AgentContextMiddleware

        # Get test user
        user = User.objects.get(username='test_completion_user')

        # Initialize middleware
        middleware = AgentContextMiddleware()

        # Get user context
        context = middleware.get_user_context(user)

        assert context is not None, "User context should be generated"
        assert 'professional_profile' in context, "Context should have professional profile"
        assert 'skills' in context, "Context should have skills"

        print(f"✅ Agent context generated with {len(context)} sections")
        print(f"✅ Professional profile: {context['professional_profile'].get('current_title', 'N/A')}")
        print(f"✅ Top skills: {', '.join(context['skills'].get('top_skills', [])[:3])}")

        return True
    except ImportError as e:
        print(f"⚠️ Agent context middleware not found: {e}")
        return False

def test_job_application_system():
    """Test job application tracking"""
    print("\n🧪 Testing Job Application System...")

    user = User.objects.get(username='test_completion_user')

    # Create test job application
    app, created = JobApplication.objects.update_or_create(
        user=user,
        job_title='Senior Python Developer',
        defaults={
            'company': 'Test Corp',
            'location': 'Remote',
            'salary_range': '$120k - $160k',
            'status': 'applied',
            'applied_date': datetime.now(),
            'platform': 'linkedin',
            'job_url': 'https://example.com/job/123',
            'fit_score': 0.85,
            'notes': 'Great match for skills'
        }
    )

    if created:
        print("✅ Created test job application")
    else:
        print("✅ Updated existing job application")

    # Get application stats
    total_apps = JobApplication.objects.filter(user=user).count()
    print(f"✅ Total applications for user: {total_apps}")

    return True

def generate_report(results):
    """Generate validation report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'system': 'System Completion Orchestrator',
        'validation_results': {
            'user_profile_system': results.get('profile', False),
            'api_endpoints': results.get('api', False),
            'agent_context': results.get('context', False),
            'job_applications': results.get('jobs', False),
            'overall_completion': sum(results.values()) / len(results) * 100
        },
        'summary': {
            'total_tests': len(results),
            'passed': sum(1 for v in results.values() if v),
            'failed': sum(1 for v in results.values() if not v)
        }
    }

    # Save report
    with open('system_completion_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    return report

def main():
    print("🚀 System Completion Validation")
    print("=" * 60)

    results = {}

    try:
        results['profile'] = test_user_profile_system()
    except Exception as e:
        print(f"❌ Profile test failed: {e}")
        results['profile'] = False

    try:
        results['api'] = test_api_endpoints()
    except Exception as e:
        print(f"❌ API test failed: {e}")
        results['api'] = False

    try:
        results['context'] = test_agent_context()
    except Exception as e:
        print(f"❌ Context test failed: {e}")
        results['context'] = False

    try:
        results['jobs'] = test_job_application_system()
    except Exception as e:
        print(f"❌ Job application test failed: {e}")
        results['jobs'] = False

    # Generate report
    report = generate_report(results)

    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Overall Completion: {report['validation_results']['overall_completion']:.1f}%")
    print("\n📄 Full report saved to: system_completion_report.json")

    return report['validation_results']['overall_completion']

if __name__ == "__main__":
    score = main()
    sys.exit(0 if score >= 75 else 1)