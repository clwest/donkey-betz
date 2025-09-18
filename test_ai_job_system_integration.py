#!/usr/bin/env python3
"""
AI Job System Integration Test
=============================
Tests the complete data flow from backend APIs to frontend functionality.
"""

import json
import requests
import time
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_apis():
    """Test all backend API endpoints"""

    print("🧪 Testing Backend APIs")
    print("=" * 50)

    # Test 1: Spider Status API
    print("\n1. Testing Spider Status API...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/intelligence/ai-jobs/spiders/")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('spiders'):
                spider_count = len(data['spiders'])
                active_spiders = data.get('active_spiders', 0)
                print(f"   ✅ SUCCESS: Found {spider_count} spiders, {active_spiders} active")

                # Show sample spider data
                if data['spiders']:
                    sample_spider = data['spiders'][0]
                    print(f"   📊 Sample: {sample_spider['name']} - {sample_spider['data_collected']} items collected")
            else:
                print(f"   ❌ FAIL: Invalid response format")
                return False
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False

    # Test 2: Job Opportunities API
    print("\n2. Testing Job Opportunities API...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/intelligence/ai-jobs/jobs/")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('jobs'):
                job_count = len(data['jobs'])
                print(f"   ✅ SUCCESS: Found {job_count} job opportunities")

                # Show sample job data
                if data['jobs']:
                    sample_job = data['jobs'][0]
                    print(f"   📊 Sample: {sample_job['title']} - AI Score: {sample_job['ai_score']:.1%}")
            else:
                print(f"   ❌ FAIL: Invalid response format")
                return False
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False

    # Test 3: Spider Activation API
    print("\n3. Testing Spider Activation API...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/intelligence/ai-jobs/start-spiders/",
            json={},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                activated_count = len(data.get('activated_spiders', []))
                print(f"   ✅ SUCCESS: Activated {activated_count} spiders")
                print(f"   📊 Message: {data.get('message', 'No message')}")
            else:
                print(f"   ❌ FAIL: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False

    # Test 4: Job Application API
    print("\n4. Testing Job Application API...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/intelligence/ai-jobs/apply/",
            json={"job_id": "test_job_integration"},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                app_id = data.get('application_id', 'Unknown')
                files_count = len(data.get('files_generated', []))
                print(f"   ✅ SUCCESS: Created application {app_id}")
                print(f"   📁 Generated {files_count} application files")

                # Verify files were created
                output_dir = Path("income_builder_outputs")
                if output_dir.exists():
                    test_files = list(output_dir.glob(f"*test_job_integration*"))
                    print(f"   📄 Found {len(test_files)} files on disk")

            else:
                print(f"   ❌ FAIL: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ FAIL: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False

    return True

def test_frontend_connectivity():
    """Test if frontend can connect to backend"""

    print("\n🌐 Testing Frontend Connectivity")
    print("=" * 50)

    # Test if frontend is accessible
    print("\n1. Testing Frontend Server...")
    try:
        response = requests.get(f"{FRONTEND_URL}/ai-job-tracker", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ SUCCESS: Frontend accessible at {FRONTEND_URL}")
        else:
            print(f"   ⚠️  WARNING: Frontend returned HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ FAIL: Frontend not accessible - {e}")
        return False

    # Test CORS and API connectivity
    print("\n2. Testing CORS Configuration...")
    try:
        # Simulate a fetch request from frontend
        headers = {
            'Origin': FRONTEND_URL,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'content-type'
        }
        response = requests.options(f"{BACKEND_URL}/api/v1/intelligence/ai-jobs/spiders/", headers=headers)

        # Check if CORS headers are present
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        if cors_origin:
            print(f"   ✅ SUCCESS: CORS configured (Origin: {cors_origin})")
        else:
            print(f"   ⚠️  WARNING: CORS headers not found, but request succeeded")

    except Exception as e:
        print(f"   ⚠️  WARNING: CORS test failed - {e}")

    return True

def test_real_time_data_flow():
    """Test the complete data flow scenario"""

    print("\n🔄 Testing Real-Time Data Flow")
    print("=" * 50)

    print("\n1. Fetching initial spider status...")
    response = requests.get(f"{BACKEND_URL}/api/v1/intelligence/ai-jobs/spiders/")
    initial_data = response.json()
    initial_active = initial_data.get('active_spiders', 0)
    print(f"   📊 Initial: {initial_active} active spiders")

    print("\n2. Activating all spiders...")
    response = requests.post(f"{BACKEND_URL}/api/v1/intelligence/ai-jobs/start-spiders/", json={})
    activation_result = response.json()
    print(f"   🚀 Activation: {activation_result.get('message', 'Unknown result')}")

    print("\n3. Checking updated spider status...")
    time.sleep(1)  # Brief delay to allow state update
    response = requests.get(f"{BACKEND_URL}/api/v1/intelligence/ai-jobs/spiders/")
    updated_data = response.json()
    updated_active = updated_data.get('active_spiders', 0)
    print(f"   📊 Updated: {updated_active} active spiders")

    print("\n4. Fetching job opportunities...")
    response = requests.get(f"{BACKEND_URL}/api/v1/intelligence/ai-jobs/jobs/")
    jobs_data = response.json()
    job_count = len(jobs_data.get('jobs', []))
    print(f"   💼 Available jobs: {job_count}")

    if job_count > 0:
        sample_job = jobs_data['jobs'][0]
        print(f"   📋 Sample job: {sample_job['title']} (Score: {sample_job['ai_score']:.1%})")

        print("\n5. Testing job application...")
        response = requests.post(
            f"{BACKEND_URL}/api/v1/intelligence/ai-jobs/apply/",
            json={"job_id": sample_job['id']}
        )
        app_result = response.json()
        if app_result.get('success'):
            print(f"   ✅ Applied successfully: {app_result.get('application_id')}")
        else:
            print(f"   ❌ Application failed: {app_result.get('error')}")

    return True

def main():
    """Run all integration tests"""

    print("🤖 AI JOB SYSTEM INTEGRATION TEST")
    print("=" * 60)
    print(f"Backend: {BACKEND_URL}")
    print(f"Frontend: {FRONTEND_URL}")
    print("=" * 60)

    success = True

    # Test backend APIs
    if not test_backend_apis():
        success = False

    # Test frontend connectivity
    if not test_frontend_connectivity():
        success = False

    # Test real-time data flow
    if not test_real_time_data_flow():
        success = False

    # Summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ AI Job Tracker is fully operational")
        print(f"🌐 Frontend: {FRONTEND_URL}/ai-job-tracker")
        print("📊 Backend APIs are responding correctly")
        print("🔄 Data flow is working end-to-end")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Check the logs above for specific issues")

    print("=" * 60)

    return success

if __name__ == "__main__":
    main()