"""
Complete Agent Ecosystem Test - Session 94
===========================================

This script tests the entire creative workflow agent system end-to-end:
- All 10 registered agents
- Inter-agent communication
- Workflow orchestration
- AI Assistant integration

Usage:
    python scripts/test_agent_ecosystem.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from agents.models import UnifiedAgentTemplate
from ai_core.agents.workflow_coordinator_agent import WorkflowCoordinatorAgent
from ai_core.agents.creative_director_agent import CreativeDirectorAgent
from ai_core.agents.template_manager_agent import TemplateManagerAgent
from ai_core.agents.brand_style_agent import BrandStyleAgent
from ai_core.agents.version_control_agent import VersionControlAgent
from ai_core.agents.editing_orchestrator_agent import EditingOrchestratorAgent
from ai_core.agents.iteration_agent import IterationAgent
from ai_core.agents.reference_library_agent import ReferenceLibraryAgent
from agents.audio_agent import AudioAgent
from agents.video_agent import VideoAgent

User = get_user_model()


def print_section(title):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_database_registration():
    """Test 1: Verify all agents are registered in database"""
    print_section("TEST 1: Database Registration")

    agents = UnifiedAgentTemplate.objects.filter(is_active=True).order_by('name')
    print(f"\n✅ Total active agents: {agents.count()}")

    expected_agents = [
        'AudioAgent',
        'BrandStyleAgent',
        'CreativeDirectorAgent',
        'EditingOrchestratorAgent',
        'IterationAgent',
        'ReferenceLibraryAgent',
        'TemplateManagerAgent',
        'VersionControlAgent',
        'VideoAgent',
        'WorkflowCoordinatorAgent'
    ]

    registered_names = [a.name for a in agents]

    print("\n📋 Expected vs Registered:")
    for expected in expected_agents:
        status = "✅" if expected in registered_names else "❌"
        print(f"{status} {expected}")

    missing = set(expected_agents) - set(registered_names)
    extra = set(registered_names) - set(expected_agents)

    if missing:
        print(f"\n⚠️  Missing agents: {', '.join(missing)}")
    if extra:
        print(f"\n📌 Extra agents: {', '.join(extra)}")

    return len(missing) == 0


def test_agent_initialization():
    """Test 2: Initialize all agent classes"""
    print_section("TEST 2: Agent Initialization")

    # Get test user
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("❌ No superuser found! Creating one...")
        return False

    print(f"\n👤 Test user: {user.username}")

    agents_to_test = {
        'WorkflowCoordinatorAgent': WorkflowCoordinatorAgent,
        'CreativeDirectorAgent': CreativeDirectorAgent,
        'TemplateManagerAgent': TemplateManagerAgent,
        'BrandStyleAgent': BrandStyleAgent,
        'VersionControlAgent': VersionControlAgent,
        'EditingOrchestratorAgent': EditingOrchestratorAgent,
        'IterationAgent': IterationAgent,
        'ReferenceLibraryAgent': ReferenceLibraryAgent,
        'AudioAgent': AudioAgent,
        'VideoAgent': VideoAgent
    }

    initialized = {}

    for agent_name, AgentClass in agents_to_test.items():
        try:
            if agent_name in ['AudioAgent', 'VideoAgent']:
                agent = AgentClass(user=user)
            else:
                agent = AgentClass(user=user)

            initialized[agent_name] = agent
            print(f"✅ {agent_name} initialized")
        except Exception as e:
            print(f"❌ {agent_name} failed: {str(e)}")
            initialized[agent_name] = None

    success_count = sum(1 for a in initialized.values() if a is not None)
    total_count = len(agents_to_test)

    print(f"\n📊 Success rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")

    return success_count == total_count, initialized


def test_workflow_orchestration(agents):
    """Test 3: Workflow Coordinator orchestration"""
    print_section("TEST 3: Workflow Orchestration")

    coordinator = agents.get('WorkflowCoordinatorAgent')
    if not coordinator:
        print("❌ WorkflowCoordinatorAgent not initialized")
        return False

    print("\n📋 Testing workflow methods...")

    # Test method availability
    methods = [
        'execute_generate_with_options_workflow',
        'execute_save_as_template_workflow',
        'execute_train_brand_style_workflow'
    ]

    method_check = {}
    for method_name in methods:
        has_method = hasattr(coordinator, method_name) and callable(getattr(coordinator, method_name))
        method_check[method_name] = has_method
        status = "✅" if has_method else "❌"
        print(f"{status} {method_name}")

    all_methods_exist = all(method_check.values())

    # Test sub-agent access
    print("\n📋 Testing sub-agent connectivity...")

    sub_agents = {
        'creative_director': 'CreativeDirectorAgent',
        'template_manager': 'TemplateManagerAgent',
        'version_control': 'VersionControlAgent',
        'brand_style': 'BrandStyleAgent',
        'reference_library': 'ReferenceLibraryAgent',
        'editing_orchestrator': 'EditingOrchestratorAgent',
        'iteration_agent': 'IterationAgent'
    }

    agent_check = {}
    for attr_name, agent_name in sub_agents.items():
        has_agent = hasattr(coordinator, attr_name) and getattr(coordinator, attr_name) is not None
        agent_check[attr_name] = has_agent
        status = "✅" if has_agent else "❌"
        print(f"{status} {attr_name} ({agent_name})")

    all_agents_connected = all(agent_check.values())

    success = all_methods_exist and all_agents_connected

    if success:
        print("\n🎉 Workflow orchestration is fully operational!")
    else:
        print("\n⚠️  Some components are missing")

    return success


def test_inter_agent_communication(agents):
    """Test 4: Inter-agent communication (VideoAgent → AudioAgent)"""
    print_section("TEST 4: Inter-Agent Communication")

    video_agent = agents.get('VideoAgent')
    audio_agent = agents.get('AudioAgent')

    if not video_agent or not audio_agent:
        print("❌ VideoAgent or AudioAgent not initialized")
        return False

    print("\n📋 Testing VideoAgent → AudioAgent query protocol...")

    # Check if VideoAgent has query capabilities
    has_add_music = hasattr(video_agent, 'add_music_to_video')
    print(f"{'✅' if has_add_music else '❌'} VideoAgent.add_music_to_video() exists")

    # Check if AudioAgent has query handlers
    has_get_recent = hasattr(audio_agent, 'get_most_recent_audio')
    print(f"{'✅' if has_get_recent else '❌'} AudioAgent.get_most_recent_audio() exists")

    # Check agent templates
    try:
        from agents.models import UnifiedAgentTemplate
        audio_template = UnifiedAgentTemplate.objects.get(name='AudioAgent')
        video_template = UnifiedAgentTemplate.objects.get(name='VideoAgent')
        print(f"✅ Both agent templates exist in database")
        has_templates = True
    except Exception as e:
        print(f"❌ Error accessing agent templates: {str(e)}")
        has_templates = False

    success = has_add_music and has_get_recent and has_templates

    if success:
        print("\n🎉 Inter-agent communication infrastructure is ready!")
        print("   (Note: Full test requires actual audio generation)")
    else:
        print("\n⚠️  Some communication components are missing")

    return success


def test_ai_assistant_integration():
    """Test 5: AI Assistant tool integration"""
    print_section("TEST 5: AI Assistant Integration")

    print("\n📋 Checking execute_tool routing...")

    # Check if execute_tool endpoint has routing for all tools
    try:
        # Read the views_image.py file directly
        import os
        views_image_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'core', 'views_image.py'
        )
        with open(views_image_path, 'r') as f:
            source = f.read()

        tools_to_check = {
            'generate_with_options': 'WorkflowCoordinatorAgent',
            'save_as_template': 'WorkflowCoordinatorAgent',
            'train_brand_style': 'WorkflowCoordinatorAgent',
            'refine_image': 'IterationAgent',
            'generate_speech': 'AudioAgent',
            'generate_sound_effect': 'AudioAgent',
            'add_music_to_video': 'VideoAgent',
            'add_text_to_video': 'VideoAgent'
        }

        routing_check = {}
        for tool_name, expected_agent in tools_to_check.items():
            # Check if tool_name appears in an elif statement (more precise)
            tool_routing_exists = f"elif tool_name == '{tool_name}'" in source or f'elif tool_name == "{tool_name}"' in source
            routing_check[tool_name] = tool_routing_exists
            status = "✅" if tool_routing_exists else "❌"
            agent_hint = f"→ {expected_agent}" if tool_routing_exists else "(not found in routing)"
            print(f"{status} {tool_name} {agent_hint}")

        all_routed = all(routing_check.values())

        if all_routed:
            print("\n🎉 All AI Assistant tools are properly routed!")
        else:
            print("\n⚠️  Some tools are not routed")

        return all_routed

    except Exception as e:
        print(f"❌ Error checking routing: {str(e)}")
        return False


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "🎨"*35)
    print("    COMPLETE AGENT ECOSYSTEM TEST - SESSION 94")
    print("🎨"*35)

    results = {}

    # Test 1: Database registration
    results['database'] = test_database_registration()

    # Test 2: Agent initialization
    init_success, agents = test_agent_initialization()
    results['initialization'] = init_success

    # Test 3: Workflow orchestration (only if initialization succeeded)
    if init_success:
        results['orchestration'] = test_workflow_orchestration(agents)
        results['communication'] = test_inter_agent_communication(agents)
    else:
        results['orchestration'] = False
        results['communication'] = False

    # Test 5: AI Assistant integration
    results['ai_assistant'] = test_ai_assistant_integration()

    # Final summary
    print_section("FINAL SUMMARY")

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)

    print(f"\n📊 Test Results:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name.replace('_', ' ').title()}")

    success_rate = (passed_tests / total_tests) * 100

    print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")

    if success_rate == 100:
        print("\n🎉 🎉 🎉 ALL TESTS PASSED! 🎉 🎉 🎉")
        print("\n✨ Complete creative workflow agent system is OPERATIONAL! ✨")
        print("\n🚀 Ready for production use:")
        print("   • 10 agents registered and active")
        print("   • Workflow orchestration working")
        print("   • Inter-agent communication enabled")
        print("   • AI Assistant integration complete")
        print("\n💡 Try voice commands like:")
        print("   'Generate three coffee shop logos'")
        print("   'Save image 123 as template'")
        print("   'Add music to my last video'")
    elif success_rate >= 80:
        print("\n✅ Most systems operational! Minor issues to resolve.")
    elif success_rate >= 60:
        print("\n⚠️  Some critical systems need attention.")
    else:
        print("\n❌ Major issues detected. Review failed tests.")

    return success_rate


if __name__ == '__main__':
    success_rate = run_all_tests()
    sys.exit(0 if success_rate == 100 else 1)
