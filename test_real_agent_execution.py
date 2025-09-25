#!/usr/bin/env python3
"""
Test script to verify real agent execution capabilities
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from backend.agents.concrete_executor import concrete_executor
from backend.agents.project_builder_base import FullStackBuilderAgent
from core.project_builder_orchestrator import get_project_orchestrator

async def test_project_builder_agent():
    """Test the ProjectBuilderAgent directly"""
    print("🏗️ Testing ProjectBuilderAgent directly...")

    try:
        agent = FullStackBuilderAgent("TestFullStackBuilder")

        # Test project creation
        result = await agent.execute(
            "Build a simple todo list app",
            project_name="test_todo_app",
            tech_stack={'frontend': 'react', 'backend': 'node'},
            features=['task creation', 'task completion', 'task deletion']
        )

        print(f"✅ Direct agent test result: {result.get('success')}")
        print(f"📁 Project path: {result.get('project_path')}")
        print(f"📄 Files created: {len(result.get('files_created', []))}")

        # Get implementation metrics
        metrics = agent.get_implementation_metrics()
        print(f"📊 Implementation metrics:")
        print(f"  - Files created: {metrics.get('files_created', 0)}")
        print(f"  - Commands executed: {metrics.get('commands_executed', 0)}")
        print(f"  - Build output lines: {metrics.get('build_output_lines', 0)}")

        return result.get('success', False)

    except Exception as e:
        print(f"❌ Direct agent test failed: {str(e)}")
        return False

async def test_concrete_executor():
    """Test the ConcreteAgentExecutor with project building"""
    print("\n🤖 Testing ConcreteAgentExecutor...")

    try:
        task = {
            'type': 'fullstack',
            'task_description': 'Build a simple weather app',
            'input': {
                'project_name': 'weather_app',
                'tech_stack': {'frontend': 'react', 'backend': 'node', 'database': 'postgres'},
                'features': ['weather display', 'location search', 'forecast']
            }
        }

        result = await concrete_executor.execute_agent('weather_builder', task)

        print(f"✅ Executor test result: {result.get('success')}")
        print(f"🤖 Agent type: {result.get('agent_type')}")
        print(f"⚡ Real execution: {result.get('real_execution')}")

        if result.get('implementation_metrics'):
            metrics = result['implementation_metrics']
            print(f"📊 Implementation metrics:")
            print(f"  - Files created: {metrics.get('files_created', 0)}")
            print(f"  - Commands executed: {metrics.get('commands_executed', 0)}")
            print(f"  - Project path: {metrics.get('current_project')}")

        return result.get('success', False)

    except Exception as e:
        print(f"❌ Executor test failed: {str(e)}")
        return False

async def test_project_orchestrator():
    """Test the ProjectBuilderOrchestrator"""
    print("\n🎭 Testing ProjectBuilderOrchestrator...")

    try:
        orchestrator = get_project_orchestrator()

        result = await orchestrator.build_project(
            idea="Build a simple blog application",
            requirements=["post creation", "post editing", "user comments", "user authentication"],
            use_real_agents=True
        )

        print(f"✅ Orchestrator test result: {result.get('success')}")
        print(f"🔧 Real execution: {result.get('real_execution')}")
        print(f"📦 Project: {result.get('project_name')}")

        if result.get('files_created'):
            print(f"📄 Files created: {len(result['files_created'])}")

        if result.get('build_log'):
            print(f"📝 Build log entries: {len(result['build_log'])}")

        return result.get('success', False)

    except Exception as e:
        print(f"❌ Orchestrator test failed: {str(e)}")
        return False

async def test_workspace_creation():
    """Test workspace creation and file operations"""
    print("\n📁 Testing workspace creation...")

    try:
        from backend.agents.project_builder_base import ProjectBuilderAgent

        agent = ProjectBuilderAgent("TestAgent")

        # Create workspace
        workspace = agent.create_project_workspace("test_workspace")
        print(f"📁 Created workspace: {workspace}")

        # Test file writing
        success = agent.write_file("test.txt", "Hello from AI agent!")
        print(f"📝 File write success: {success}")

        # Test file reading
        content = agent.read_file("test.txt")
        print(f"📖 File content: {content[:50] if content else 'None'}...")

        # Test command execution
        result = agent.execute_command("echo 'Test command execution'")
        print(f"🔧 Command success: {result.get('success')}")
        print(f"📄 Command output: {result.get('stdout', '').strip()}")

        # Get metrics
        metrics = agent.get_implementation_metrics()
        print(f"📊 Final metrics: {metrics}")

        return True

    except Exception as e:
        print(f"❌ Workspace test failed: {str(e)}")
        return False

async def check_project_directory():
    """Check if projects are being created in the right place"""
    print("\n📂 Checking project directory...")

    projects_dir = project_root / "ai_generated_projects"

    print(f"Projects directory: {projects_dir}")
    print(f"Directory exists: {projects_dir.exists()}")

    if projects_dir.exists():
        projects = list(projects_dir.iterdir())
        print(f"Found {len(projects)} projects:")

        for project in projects[:5]:  # Show first 5
            if project.is_dir():
                files = list(project.iterdir())
                print(f"  - {project.name}: {len(files)} files/dirs")

async def main():
    """Run all tests"""
    print("🚀 Starting Real Agent Execution Tests\n")
    print("="*60)

    tests = [
        ("Workspace Creation", test_workspace_creation),
        ("Project Directory Check", check_project_directory),
        ("Direct Agent Test", test_project_builder_agent),
        ("Concrete Executor Test", test_concrete_executor),
        ("Project Orchestrator Test", test_project_orchestrator),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print("="*60)

        try:
            result = await test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            results[test_name] = False
            print(f"\n❌ FAILED: {test_name} - {str(e)}")

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Real agent execution is working!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check logs for details.")

    return passed == total

if __name__ == "__main__":
    asyncio.run(main())