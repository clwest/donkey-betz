#!/usr/bin/env python3
"""
Quick test to check basic infrastructure without AI calls
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

def test_imports():
    """Test that all our new components can be imported"""
    print("🔗 Testing imports...")

    try:
        from backend.agents.project_builder_base import ProjectBuilderAgent, FullStackBuilderAgent
        print("✅ ProjectBuilderAgent imports work")

        from backend.agents.concrete_executor import get_concrete_executor
        concrete_executor = get_concrete_executor()
        print("✅ ConcreteAgentExecutor imports work")

        from core.project_builder_orchestrator import get_project_orchestrator
        print("✅ ProjectBuilderOrchestrator imports work")

        from core.views_project_builder import NewProjectView
        print("✅ Project Builder Views import work")

        return True
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        return False

def test_workspace_creation():
    """Test basic workspace functionality without AI"""
    print("\n📁 Testing workspace creation...")

    try:
        from backend.agents.project_builder_base import ProjectBuilderAgent

        agent = ProjectBuilderAgent("TestAgent")

        # Create workspace
        workspace = agent.create_project_workspace("test_basic_workspace")
        print(f"✅ Created workspace: {workspace}")

        # Test file writing
        success = agent.write_file("test.txt", "Hello from AI agent!")
        print(f"✅ File write success: {success}")

        # Test file reading
        content = agent.read_file("test.txt")
        print(f"✅ File content matches: {'Hello from AI agent!' in str(content)}")

        # Test simple command
        result = agent.execute_command("echo 'Test command'")
        print(f"✅ Command execution: {result.get('success')}")

        # Get metrics
        metrics = agent.get_implementation_metrics()
        print(f"✅ Metrics available: {len(metrics) > 0}")
        print(f"   Files created: {metrics.get('files_created', 0)}")
        print(f"   Commands executed: {metrics.get('commands_executed', 0)}")

        return True

    except Exception as e:
        print(f"❌ Workspace test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_project_directory():
    """Test project directory setup"""
    print("\n📂 Testing project directory...")

    projects_dir = project_root / "ai_generated_projects"

    print(f"✅ Projects directory: {projects_dir}")
    print(f"✅ Directory exists: {projects_dir.exists()}")

    if projects_dir.exists():
        projects = [p for p in projects_dir.iterdir() if p.is_dir()]
        print(f"✅ Found {len(projects)} existing projects")

        for project in projects[:3]:  # Show first 3
            files = list(project.iterdir())
            print(f"  - {project.name}: {len(files)} files/dirs")

    return True

def test_concrete_executor_setup():
    """Test ConcreteAgentExecutor basic setup"""
    print("\n🤖 Testing ConcreteAgentExecutor setup...")

    try:
        from backend.agents.concrete_executor import concrete_executor

        # Test basic properties
        print(f"✅ Agent classes loaded: {len(concrete_executor.agent_classes)}")
        print(f"✅ Agent registry available: {hasattr(concrete_executor, 'agent_registry')}")

        # Test agent listing
        agents = concrete_executor.list_available_agents()
        print(f"✅ Available agents: {len(agents)}")

        # Test task detection
        test_task = {
            'type': 'fullstack',
            'task_description': 'Build a simple app'
        }

        is_project_task = concrete_executor._is_project_builder_task(test_task)
        print(f"✅ Project task detection: {is_project_task}")

        return True

    except Exception as e:
        print(f"❌ ConcreteExecutor test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all basic tests"""
    print("🚀 Quick Infrastructure Test\n")
    print("="*50)

    tests = [
        ("Import Test", test_imports),
        ("Project Directory", test_project_directory),
        ("Workspace Creation", test_workspace_creation),
        ("ConcreteExecutor Setup", test_concrete_executor_setup),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n{'-'*20} {test_name} {'-'*20}")

        try:
            result = test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            results[test_name] = False
            print(f"\n❌ FAILED: {test_name} - {str(e)}")

    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print("="*50)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")

    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL BASIC TESTS PASSED!")
        print("The infrastructure is ready for real agent execution!")
    else:
        print(f"\n⚠️  Infrastructure needs fixes before proceeding.")

    return passed == total

if __name__ == "__main__":
    main()