#!/usr/bin/env python
"""
Test Quick Apply functionality to ensure real applications are submitted
"""

import os
import sys
import django
import json
import logging

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import ExtendedUserProfile, JobApplication
from core.real_job_submitter import real_job_submitter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()


def test_quick_apply():
    """Test the Quick Apply functionality"""

    print("\n" + "="*60)
    print("🧪 TESTING QUICK APPLY FUNCTIONALITY")
    print("="*60)

    # Get or create test user
    user, created = User.objects.get_or_create(
        username='test_applicant',
        defaults={'email': 'test@example.com'}
    )

    # Get or create extended profile
    profile, created = ExtendedUserProfile.objects.get_or_create(
        user=user,
        defaults={
            'full_name': 'Test Applicant',
            'phone': '555-0123',
            'location': 'San Francisco, CA',
            'current_title': 'Software Developer',
            'bio': 'Experienced developer with 5+ years building web applications',
            'skills': json.dumps(['Python', 'JavaScript', 'React', 'Django']),
            'email': 'test@example.com'
        }
    )

    print(f"\n✅ User Profile: {profile.full_name if profile.full_name else 'Test User'}")
    print(f"   Email: {user.email}")
    print(f"   Location: {profile.location if profile.location else 'Not set'}")

    # Test job data
    test_jobs = [
        {
            'id': 'test_job_001',
            'title': 'Senior Python Developer',
            'company': 'TechCorp',
            'platform': 'linkedin',
            'apply_url': 'https://www.linkedin.com/jobs/view/12345',
            'budget': 120000,
            'description': 'Looking for experienced Python developer',
            'required_skills': ['Python', 'Django', 'REST APIs']
        },
        {
            'id': 'test_job_002',
            'title': 'Full Stack Developer',
            'company': 'StartupCo',
            'platform': 'indeed',
            'apply_url': 'https://www.indeed.com/viewjob?jk=67890',
            'budget': 100000,
            'description': 'Build amazing web applications',
            'required_skills': ['React', 'Node.js', 'MongoDB']
        },
        {
            'id': 'test_job_003',
            'title': 'Python Web Scraping Expert',
            'company': 'DataMining Inc',
            'platform': 'upwork',
            'apply_url': 'https://www.upwork.com/jobs/~01234567',
            'budget': {'min': 500, 'max': 1500},
            'description': 'Need expert to build web scrapers',
            'required_skills': ['Python', 'BeautifulSoup', 'Scrapy']
        }
    ]

    # Test cover letter
    cover_letter = """
I am excited to apply for this position. With my 5+ years of experience
in software development and expertise in the required technologies,
I am confident I can make significant contributions to your team.

I have successfully delivered multiple projects using similar tech stacks
and am passionate about building high-quality solutions.

Looking forward to discussing how I can help achieve your goals.
"""

    # Test resume content
    resume_content = """
# Test Applicant
Email: test@example.com | Phone: 555-0123 | Location: San Francisco, CA

## Summary
Experienced software developer with 5+ years building scalable web applications.

## Skills
Python, JavaScript, React, Django, REST APIs, Docker, AWS

## Experience
**Senior Developer** at Previous Company
2020 - Present
- Built and maintained production applications
- Led team of 3 developers
- Improved performance by 40%

## Education
**BS Computer Science** - Tech University
Graduated: 2018
"""

    print("\n" + "-"*40)
    print("📋 TESTING JOB APPLICATIONS:")
    print("-"*40)

    for job in test_jobs:
        print(f"\n🎯 Testing: {job['title']} at {job['company']}")
        print(f"   Platform: {job['platform']}")

        try:
            # Test the real job submitter
            result = real_job_submitter.submit_application(
                job_data=job,
                profile=profile,
                cover_letter=cover_letter,
                resume_content=resume_content
            )

            if result.get('success'):
                print(f"   ✅ SUCCESS: {result.get('message')}")
                print(f"   Confirmation: {result.get('confirmation_id')}")
                print(f"   Method: {result.get('method')}")

                # Create application record
                application = JobApplication.objects.create(
                    user=user,
                    job_id=job['id'],
                    platform=job['platform'],
                    company=job['company'],
                    position=job['title'],
                    job_url=job.get('apply_url', ''),
                    application_method='quick_apply',
                    resume_version='Test Resume',
                    cover_letter_used=cover_letter,
                    status='applied',
                    match_score=85.0
                )
                print(f"   📝 Application record created: {application.id}")

            else:
                print(f"   ❌ FAILED: {result.get('error')}")

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")

    # Check application tracking
    print("\n" + "-"*40)
    print("📊 APPLICATION TRACKING:")
    print("-"*40)

    applications = JobApplication.objects.filter(user=user).order_by('-applied_date')
    for app in applications[:5]:
        print(f"\n   Job: {app.position} at {app.company}")
        print(f"   Status: {app.status}")
        print(f"   Applied: {app.applied_date}")
        print(f"   Platform: {app.platform}")
        print(f"   Match Score: {app.match_score}%")

    print("\n" + "="*60)
    print("✅ QUICK APPLY TEST COMPLETE!")
    print(f"   Total Applications: {applications.count()}")
    print(f"   Success Rate: Check logs for real submission status")
    print("="*60 + "\n")


if __name__ == '__main__':
    test_quick_apply()