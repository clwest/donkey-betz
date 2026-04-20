#!/usr/bin/env python
"""
Test script for Project Management API endpoints
Phase 3: Frontend Reality Fix - AI Production Hub
"""

import os
import django
import sys

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.views_projects_api import (
    projects_list, project_detail, project_agents, assign_agent_to_project
)
from core.models_partnership import PartnershipProject
from core.models.agents_registry import UnifiedAgentTemplate
from django.test import RequestFactory
from rest_framework.test import force_authenticate

User = get_user_model()

def test_projects_list():
    """Test GET /api/projects/ endpoint"""
    print("\n🧪 Testing /api/projects/ endpoint...")

    user = User.objects.first()
    if not user:
        print("❌ No users in database")
        return False

    print(f"✅ Testing with user: {user.username}")

    # Create fake request
    factory = RequestFactory()
    request = factory.get('/api/projects/')
    force_authenticate(request, user=user)

    # Call the view
    response = projects_list(request)

    # Check response
    if response.status_code == 200:
        data = response.data
        print(f"✅ API Response Success")
        print(f"   Total Projects: {data.get('data', {}).get('total_count', 0)}")
        print(f"   Completed: {data.get('data', {}).get('stats', {}).get('completed', 0)}")
        print(f"   In Progress: {data.get('data', {}).get('stats', {}).get('in_progress', 0)}")
        print(f"   Building: {data.get('data', {}).get('stats', {}).get('building', 0)}")

        projects = data.get('data', {}).get('projects', [])
        if projects:
            print(f"\n   Sample Project:")
            sample = projects[0]
            print(f"   - Name: {sample.get('name')}")
            print(f"   - Status: {sample.get('status')}")
            print(f"   - Progress: {sample.get('progress')}%")
            print(f"   - Agents Used: {len(sample.get('agents_used', []))}")

        return True
    else:
        print(f"❌ API returned status {response.status_code}")
        print(f"   Error: {response.data}")
        return False

def test_project_detail():
    """Test GET /api/projects/<id>/ endpoint"""
    print("\n🧪 Testing /api/projects/<id>/ endpoint...")

    user = User.objects.first()
    if not user:
        print("❌ No users in database")
        return False

    # Get a project
    project = PartnershipProject.objects.filter(user=user).first()
    if not project:
        print("⚠️  No projects found for user - creating test project...")
        project = PartnershipProject.objects.create(
            user=user,
            project_name="Test Project",
            project_type="content_creation",
            description="Test project for API testing",
            status="in_progress"
        )
        print(f"✅ Created test project: {project.project_name}")

    print(f"✅ Testing with project: {project.project_name}")

    # Create fake request
    factory = RequestFactory()
    request = factory.get(f'/api/projects/{project.id}/')
    force_authenticate(request, user=user)

    # Call the view
    response = project_detail(request, project.id)

    # Check response
    if response.status_code == 200:
        data = response.data
        proj = data.get('data', {}).get('project', {})
        print(f"✅ API Response Success")
        print(f"   Name: {proj.get('name')}")
        print(f"   Status: {proj.get('status')}")
        print(f"   Progress: {proj.get('progress')}%")
        print(f"   Key Features: {len(proj.get('key_features', []))}")
        print(f"   Agents Used: {len(proj.get('agents_used', []))}")

        testable = proj.get('testable_components', {})
        print(f"\n   Testable Components:")
        print(f"   - Is Complete: {testable.get('is_complete')}")
        print(f"   - Has Features: {testable.get('has_features')}")
        print(f"   - Feature Count: {testable.get('feature_count')}")

        return True
    else:
        print(f"❌ API returned status {response.status_code}")
        print(f"   Error: {response.data}")
        return False

def test_project_agents():
    """Test GET /api/projects/<id>/agents/ endpoint"""
    print("\n🧪 Testing /api/projects/<id>/agents/ endpoint...")

    user = User.objects.first()
    if not user:
        print("❌ No users in database")
        return False

    project = PartnershipProject.objects.filter(user=user).first()
    if not project:
        print("❌ No projects found for user")
        return False

    print(f"✅ Testing with project: {project.project_name}")

    # Create fake request
    factory = RequestFactory()
    request = factory.get(f'/api/projects/{project.id}/agents/')
    force_authenticate(request, user=user)

    # Call the view
    response = project_agents(request, project.id)

    # Check response
    if response.status_code == 200:
        data = response.data
        agents = data.get('data', {}).get('available_agents', [])
        total_registry = data.get('data', {}).get('total_agent_registry', 0)
        recommendation = data.get('data', {}).get('recommendation', '')

        print(f"✅ API Response Success")
        print(f"   Available Agents: {len(agents)}")
        print(f"   Total Registry: {total_registry}")
        print(f"   Recommendation: {recommendation[:80]}...")

        if agents:
            print(f"\n   Top Agent:")
            top = agents[0]
            print(f"   - Name: {top.get('name')}")
            print(f"   - Specialization: {top.get('specialization')}")
            print(f"   - Success Rate: {top.get('success_rate')*100:.1f}%")
            print(f"   - Recommended: {top.get('recommended')}")

        return True
    else:
        print(f"❌ API returned status {response.status_code}")
        print(f"   Error: {response.data}")
        return False

def test_assign_agent():
    """Test POST /api/projects/<id>/assign-agent/ endpoint"""
    print("\n🧪 Testing /api/projects/<id>/assign-agent/ endpoint...")

    user = User.objects.first()
    if not user:
        print("❌ No users in database")
        return False

    project = PartnershipProject.objects.filter(user=user).first()
    if not project:
        print("❌ No projects found for user")
        return False

    agent = UnifiedAgentTemplate.objects.filter(is_active=True).first()
    if not agent:
        print("❌ No active agents found")
        return False

    print(f"✅ Testing assignment of {agent.name} to {project.project_name}")

    # Create fake request
    factory = RequestFactory()
    request = factory.post(
        f'/api/projects/{project.id}/assign-agent/',
        data={
            'agent_id': str(agent.id),
            'improvement_type': 'enhance',
            'task_description': 'Test enhancement task'
        },
        content_type='application/json'
    )
    force_authenticate(request, user=user)

    # Call the view
    response = assign_agent_to_project(request, project.id)

    # Check response
    if response.status_code == 200:
        data = response.data
        details = data.get('data', {})

        print(f"✅ API Response Success")
        print(f"   Message: {details.get('message')}")
        print(f"   Real Execution: {details.get('real_execution')}")
        print(f"   Agent Registry Size: {details.get('agent_registry_size')}")

        exec_details = details.get('execution_details', {})
        print(f"\n   Execution Details:")
        print(f"   - Agent: {exec_details.get('agent_name')}")
        print(f"   - Specialization: {exec_details.get('specialization')}")
        print(f"   - Estimated Time: {exec_details.get('estimated_time')}s")

        verification = exec_details.get('verification', {})
        print(f"\n   Verification:")
        print(f"   - Using Real Agent: {verification.get('using_real_agent')}")
        print(f"   - Execution Created: {verification.get('execution_created')}")
        print(f"   - Execution Status: {verification.get('execution_status')}")

        return True
    else:
        print(f"❌ API returned status {response.status_code}")
        print(f"   Error: {response.data}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("🔬 PROJECT MANAGEMENT API TEST")
    print("="*60)

    list_ok = test_projects_list()
    detail_ok = test_project_detail()
    agents_ok = test_project_agents()
    assign_ok = test_assign_agent()

    print("\n" + "="*60)
    if list_ok and detail_ok and agents_ok and assign_ok:
        print("✅ ALL TESTS PASSED")
        print("Phase 3 project management endpoints are functional!")
    else:
        print("⚠️  SOME TESTS FAILED")
        print(f"   Projects List: {'✅' if list_ok else '❌'}")
        print(f"   Project Detail: {'✅' if detail_ok else '❌'}")
        print(f"   Project Agents: {'✅' if agents_ok else '❌'}")
        print(f"   Assign Agent: {'✅' if assign_ok else '❌'}")
    print("="*60)
