#!/usr/bin/env python3
"""
Test Creative Pipelines API Integration
Session 109: Verify pipeline templates, runs, and execution
"""

import os
import sys
import django
import json
from time import sleep

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from pipelines.models import CreativePipelineTemplate, CreativePipelineRun
from pipelines.services import (
    get_available_templates,
    start_pipeline_run,
    run_pipeline
)

User = get_user_model()


def setup_test_user():
    """Create or get test user"""
    user, created = User.objects.get_or_create(
        username='pipeline_test_user',
        defaults={'email': 'pipeline_test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
    return user


def test_imports():
    """Test that all imports work"""
    print("=" * 70)
    print("TEST 1: Import Verification")
    print("=" * 70)

    try:
        # Test model imports
        from pipelines import models
        print("✅ pipelines.models imported")

        # Test service imports
        from pipelines import services
        print("✅ pipelines.services imported")

        # Test task imports
        from pipelines import tasks
        print("✅ pipelines.tasks imported")

        # Test view imports
        from pipelines import views
        print("✅ pipelines.views imported")

        # Test URL imports
        from pipelines import urls
        print("✅ pipelines.urls imported")

        print("\n✅ All imports successful!")
        return True

    except Exception as e:
        print(f"\n❌ Import error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_template_model():
    """Test CreativePipelineTemplate model"""
    print("\n" + "=" * 70)
    print("TEST 2: Template Model")
    print("=" * 70)

    try:
        # Check if templates exist from seeding
        templates = CreativePipelineTemplate.objects.filter(is_active=True)
        print(f"📋 Found {templates.count()} active templates:")

        for template in templates:
            print(f"\n  Template: {template.name}")
            print(f"  Slug: {template.slug}")
            print(f"  Steps: {len(template.config.get('steps', []))}")
            print(f"  Inputs: {list(template.config.get('inputs', {}).keys())}")
            print(f"  Outputs: {list(template.config.get('outputs', {}).keys())}")

        if templates.count() == 0:
            print("⚠️  No templates found. Run: python manage.py seed_pipelines")

        print("\n✅ Template model test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Template model test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_get_available_templates():
    """Test get_available_templates service function"""
    print("\n" + "=" * 70)
    print("TEST 3: Get Available Templates Service")
    print("=" * 70)

    try:
        user = setup_test_user()
        templates = get_available_templates(user)

        print(f"📋 Service returned {len(templates)} templates")

        for template in templates:
            print(f"  - {template.name} ({template.slug})")

        assert len(templates) > 0, "Should have at least one template"

        print("\n✅ get_available_templates test passed!")
        return True

    except Exception as e:
        print(f"\n❌ get_available_templates test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_api_list_templates():
    """Test GET /api/v1/pipelines/templates/"""
    print("\n" + "=" * 70)
    print("TEST 4: List Templates API Endpoint")
    print("=" * 70)

    try:
        user = setup_test_user()
        client = Client()
        client.force_login(user)

        response = client.get('/api/v1/pipelines/templates/')

        print(f"Status Code: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        print(f"Response keys: {list(data.keys())}")

        assert data.get('success') is True, "Response should have success=True"
        assert 'templates' in data, "Response should have templates key"
        assert isinstance(data['templates'], list), "Templates should be a list"

        print(f"\n📋 API returned {data['count']} templates:")
        for template in data['templates']:
            print(f"  - {template['name']} ({template['slug']})")
            print(f"    Steps: {template['total_steps']}")
            print(f"    Inputs: {list(template.get('inputs', {}).keys())}")

        print("\n✅ List templates API test passed!")
        return True

    except Exception as e:
        print(f"\n❌ List templates API test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_api_create_run():
    """Test POST /api/v1/pipelines/runs/"""
    print("\n" + "=" * 70)
    print("TEST 5: Create Run API Endpoint")
    print("=" * 70)

    try:
        user = setup_test_user()
        client = Client()
        client.force_login(user)

        # Get first available template
        templates = CreativePipelineTemplate.objects.filter(is_active=True)
        if not templates.exists():
            print("⚠️  No templates available, skipping create run test")
            return True

        template = templates.first()
        print(f"Using template: {template.name} ({template.slug})")

        # Build input payload
        input_payload = {}
        if 'idea' in template.config.get('inputs', {}):
            input_payload['idea'] = 'Test creative idea for automated testing'
        if 'num_images' in template.config.get('inputs', {}):
            input_payload['num_images'] = 3  # Use fewer images for testing

        print(f"Input payload: {input_payload}")

        # Create run via API
        response = client.post(
            '/api/v1/pipelines/runs/',
            data=json.dumps({
                'template_slug': template.slug,
                'input_payload': input_payload
            }),
            content_type='application/json'
        )

        print(f"Status Code: {response.status_code}")
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

        data = response.json()
        assert data.get('success') is True, "Response should have success=True"
        assert 'run' in data, "Response should have run key"

        run_data = data['run']
        print(f"\n✅ Run created:")
        print(f"  ID: {run_data['id']}")
        print(f"  Template: {run_data['template_name']}")
        print(f"  Status: {run_data['status']}")
        print(f"  Total Steps: {run_data['total_steps']}")

        # Store run ID for later tests
        global test_run_id
        test_run_id = run_data['id']

        print("\n✅ Create run API test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Create run API test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_api_list_runs():
    """Test GET /api/v1/pipelines/runs/"""
    print("\n" + "=" * 70)
    print("TEST 6: List Runs API Endpoint")
    print("=" * 70)

    try:
        user = setup_test_user()
        client = Client()
        client.force_login(user)

        response = client.get('/api/v1/pipelines/runs/?limit=10')

        print(f"Status Code: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data.get('success') is True, "Response should have success=True"
        assert 'runs' in data, "Response should have runs key"

        print(f"\n📋 Found {data['count']} runs (total: {data['total']}):")
        for run in data['runs'][:5]:  # Show first 5
            print(f"  - {run['template_name']}")
            print(f"    Status: {run['status']}")
            print(f"    Progress: {run['progress_percentage']}%")
            print(f"    Created: {run['created_at']}")

        print("\n✅ List runs API test passed!")
        return True

    except Exception as e:
        print(f"\n❌ List runs API test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_api_get_run_detail():
    """Test GET /api/v1/pipelines/runs/{id}/"""
    print("\n" + "=" * 70)
    print("TEST 7: Get Run Detail API Endpoint")
    print("=" * 70)

    try:
        user = setup_test_user()
        client = Client()
        client.force_login(user)

        # Get a run ID (from previous test or query)
        if 'test_run_id' in globals():
            run_id = test_run_id
        else:
            runs = CreativePipelineRun.objects.filter(user=user).order_by('-created_at')
            if not runs.exists():
                print("⚠️  No runs found, skipping detail test")
                return True
            run_id = str(runs.first().id)

        print(f"Fetching run: {run_id}")

        response = client.get(f'/api/v1/pipelines/runs/{run_id}/')

        print(f"Status Code: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data.get('success') is True, "Response should have success=True"
        assert 'run' in data, "Response should have run key"

        run = data['run']
        print(f"\n✅ Run details:")
        print(f"  ID: {run['id']}")
        print(f"  Template: {run['template']['name']}")
        print(f"  Status: {run['status']}")
        print(f"  Progress: {run['current_step']}/{run['total_steps']}")
        print(f"  Log entries: {len(run['log'].split(chr(10)))}")

        if run.get('error_message'):
            print(f"  Error: {run['error_message']}")

        if run.get('output_payload'):
            print(f"  Output keys: {list(run['output_payload'].keys())}")

        print("\n✅ Get run detail API test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Get run detail API test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_user_scoping():
    """Test that users can only see their own runs"""
    print("\n" + "=" * 70)
    print("TEST 8: User Scoping")
    print("=" * 70)

    try:
        # Create two users
        user1 = setup_test_user()
        user2, _ = User.objects.get_or_create(
            username='pipeline_test_user_2',
            defaults={'email': 'pipeline_test2@example.com'}
        )

        # Get runs for user1
        user1_runs = CreativePipelineRun.objects.filter(user=user1)
        user2_runs = CreativePipelineRun.objects.filter(user=user2)

        print(f"User1 runs: {user1_runs.count()}")
        print(f"User2 runs: {user2_runs.count()}")

        # Test API scoping
        client = Client()
        client.force_login(user1)

        response = client.get('/api/v1/pipelines/runs/')
        data = response.json()

        print(f"User1 API returned {data['count']} runs")

        # All returned runs should belong to user1
        for run_data in data['runs']:
            run = CreativePipelineRun.objects.get(id=run_data['id'])
            assert run.user == user1, "Run should belong to logged-in user"

        print("✅ User scoping verified!")

        # Test that user1 cannot access user2's runs (if any exist)
        if user2_runs.exists():
            user2_run_id = str(user2_runs.first().id)
            response = client.get(f'/api/v1/pipelines/runs/{user2_run_id}/')
            assert response.status_code == 404, "Should not access other user's run"
            print("✅ Cross-user access blocked!")

        print("\n✅ User scoping test passed!")
        return True

    except Exception as e:
        print(f"\n❌ User scoping test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 70)
    print("CREATIVE PIPELINES API TEST SUITE")
    print("Session 109 - Backend Integration Tests")
    print("=" * 70)

    tests = [
        ("Imports", test_imports),
        ("Template Model", test_template_model),
        ("Get Available Templates", test_get_available_templates),
        ("List Templates API", test_api_list_templates),
        ("Create Run API", test_api_create_run),
        ("List Runs API", test_api_list_runs),
        ("Get Run Detail API", test_api_get_run_detail),
        ("User Scoping", test_user_scoping),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {str(e)}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\n{passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")

    return passed_count == total_count


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
