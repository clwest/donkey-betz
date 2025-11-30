# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Test Memory and Collaboration Integration

This script verifies that the shared memory system is fully integrated
with the agent collaboration tracking system.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from colorama import init, Fore, Style
import django

# Django setup
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from intelligence.collaboration_tracker import (
    CollaborationTracker,
    CollaborationType
)
from intelligence.shared_memory import (
    SharedMemorySystem,
    AgentMemoryInterface,
    AdvisorMemoryInterface
)

init(autoreset=True)


class MemoryCollaborationTest:
    """Test the integration between memory and collaboration systems"""

    def __init__(self):
        self.tracker = CollaborationTracker()
        self.memory = SharedMemorySystem()

    def print_section(self, title: str, color=Fore.CYAN):
        """Pretty print section headers"""
        print(f"\n{color}{'='*80}")
        print(f"{title.center(80)}")
        print(f"{'='*80}{Style.RESET_ALL}\n")

    async def test_memory_during_handoff(self):
        """Test that memories are created during agent handoffs"""
        self.print_section("TEST 1: MEMORY CREATION DURING HANDOFFS", Fore.YELLOW)

        # Start collaboration
        chain_id = self.tracker.start_collaboration(
            task_id="memory_test_1",
            initiator_agent="Data Collector",
            collaboration_type=CollaborationType.SEQUENTIAL_HANDOFF,
            context={"test": "memory_integration"}
        )

        print(f"📋 Started collaboration chain: {chain_id}")

        # Simulate handoff with data
        handoff_data = {
            "collected_data": ["item1", "item2", "item3"],
            "metrics": {"accuracy": 0.95, "confidence": 0.87}
        }

        # Record handoff (this should also store memory)
        self.tracker.record_handoff(
            chain_id=chain_id,
            source_agent="Data Collector",
            target_agent="Data Processor",
            data=handoff_data,
            context={"phase": "collection_to_processing"}
        )

        print(f"{Fore.GREEN}✓ Handoff recorded from Data Collector → Data Processor{Style.RESET_ALL}")

        # Check if memory was stored
        agent_memory = AgentMemoryInterface("Data Collector")
        recalled_memory = agent_memory.recall("handoff")

        if recalled_memory:
            print(f"\n{Fore.GREEN}✅ MEMORY STORED SUCCESSFULLY:{Style.RESET_ALL}")
            print(f"  • Memory Type: {recalled_memory.get('memory_type')}")
            print(f"  • Target Agent: {recalled_memory['content'].get('to')}")
            print(f"  • Data Items: {len(recalled_memory['content']['data'].get('collected_data', []))}")
            print(f"  • Chain ID: {recalled_memory['content'].get('chain_id')}")
        else:
            print(f"{Fore.RED}❌ Memory was not stored{Style.RESET_ALL}")

        return recalled_memory is not None

    async def test_experience_sharing(self):
        """Test that agents share experiences during collaboration"""
        self.print_section("TEST 2: EXPERIENCE SHARING BETWEEN AGENTS", Fore.MAGENTA)

        # Agent 1 shares an experience
        print(f"{Fore.CYAN}Agent 1 sharing experience...{Style.RESET_ALL}")
        self.memory.share_experience(
            entity_type='agent',
            entity_id='Analysis Agent',
            experience={
                'task': 'data_analysis',
                'technique': 'pattern_recognition',
                'improvement': '30% faster processing',
                'learned': 'Batch processing improves efficiency'
            }
        )
        print(f"  ✓ Experience shared by Analysis Agent")

        # Agent 2 learns from the experience
        print(f"\n{Fore.CYAN}Agent 2 learning from experiences...{Style.RESET_ALL}")
        experiences = self.memory.learn_from_experiences(
            entity_type='agent',
            entity_id='Processing Agent',
            limit=5
        )

        if experiences:
            print(f"\n{Fore.GREEN}✅ EXPERIENCE LEARNING SUCCESSFUL:{Style.RESET_ALL}")
            for exp in experiences:
                print(f"  • Source: {exp['source_entity']}")
                print(f"    Learned: {exp['experience'].get('learned', 'N/A')}")
                print(f"    Improvement: {exp['experience'].get('improvement', 'N/A')}")
        else:
            print(f"{Fore.RED}❌ No experiences learned{Style.RESET_ALL}")

        return len(experiences) > 0

    async def test_knowledge_graph_building(self):
        """Test that collaboration builds the knowledge graph"""
        self.print_section("TEST 3: KNOWLEDGE GRAPH CONSTRUCTION", Fore.GREEN)

        # Start a collaboration with multiple agents
        chain_id = self.tracker.start_collaboration(
            task_id="knowledge_graph_test",
            initiator_agent="Orchestrator",
            collaboration_type=CollaborationType.HIERARCHICAL_DELEGATION,
            context={"build": "knowledge_graph"}
        )

        # Create a network of handoffs
        handoffs = [
            ("Orchestrator", "Research Agent"),
            ("Research Agent", "Analysis Agent"),
            ("Analysis Agent", "Implementation Agent"),
            ("Orchestrator", "Quality Agent"),
            ("Quality Agent", "Implementation Agent")
        ]

        print(f"{Fore.CYAN}Creating collaboration network...{Style.RESET_ALL}")
        for source, target in handoffs:
            self.tracker.record_handoff(
                chain_id=chain_id,
                source_agent=source,
                target_agent=target,
                data={"task": f"from_{source}_to_{target}"},
                context={"building": "knowledge_graph"}
            )
            print(f"  → {source} → {target}")
            await asyncio.sleep(0.2)

        # Check the knowledge graph
        print(f"\n{Fore.CYAN}Checking knowledge graph for Orchestrator...{Style.RESET_ALL}")
        network = self.memory.get_entity_network("agent/Orchestrator")

        if network['outgoing'] or network['incoming']:
            print(f"\n{Fore.GREEN}✅ KNOWLEDGE GRAPH BUILT:{Style.RESET_ALL}")
            print(f"  Outgoing connections: {len(network['outgoing'])}")
            for edge in network['outgoing']:
                print(f"    → {edge['to']} ({edge['relationship']})")

            print(f"  Incoming connections: {len(network['incoming'])}")
            for edge in network['incoming']:
                print(f"    ← {edge['from']} ({edge['relationship']})")
        else:
            print(f"{Fore.RED}❌ Knowledge graph is empty{Style.RESET_ALL}")

        return len(network['outgoing']) > 0 or len(network['incoming']) > 0

    async def test_collective_learning(self):
        """Test collective learning from collaborations"""
        self.print_section("TEST 4: COLLECTIVE LEARNING", Fore.BLUE)

        # Multiple agents record learnings
        learnings = [
            ("Optimizer Agent", {"technique": "gradient_descent", "improvement": "15% faster convergence"}),
            ("Parser Agent", {"technique": "regex_patterns", "improvement": "50% fewer errors"}),
            ("Validator Agent", {"technique": "schema_validation", "improvement": "Caught 99% of issues"})
        ]

        print(f"{Fore.CYAN}Agents recording learnings...{Style.RESET_ALL}")
        for agent, learning in learnings:
            self.memory.record_learning(
                entity_type='agent',
                entity_id=agent,
                learning=learning
            )
            print(f"  • {agent}: {learning['technique']}")
            await asyncio.sleep(0.1)

        # Get collective learnings
        print(f"\n{Fore.CYAN}Retrieving collective learnings...{Style.RESET_ALL}")
        collective = self.memory.get_collective_learnings(limit=10)

        if collective:
            print(f"\n{Fore.GREEN}✅ COLLECTIVE LEARNINGS AVAILABLE:{Style.RESET_ALL}")
            for learning in collective:
                entity = learning.get('entity', 'Unknown')
                technique = learning['learning'].get('technique', 'N/A')
                improvement = learning['learning'].get('improvement', 'N/A')
                print(f"  • {entity}: {technique} → {improvement}")
        else:
            print(f"{Fore.RED}❌ No collective learnings found{Style.RESET_ALL}")

        return len(collective) > 0

    async def test_global_context_sharing(self):
        """Test global context sharing across entities"""
        self.print_section("TEST 5: GLOBAL CONTEXT SHARING", Fore.CYAN)

        # Multiple entities share context
        contexts = [
            ("agent", "Task Manager", {"current_task": "optimization", "priority": "high"}),
            ("agent", "Resource Monitor", {"cpu_usage": "45%", "memory": "2.3GB"}),
            ("advisor", "Warren Buffett", {"market_sentiment": "bullish", "recommendation": "hold"})
        ]

        print(f"{Fore.CYAN}Entities sharing context...{Style.RESET_ALL}")
        for entity_type, entity_id, context in contexts:
            self.memory.share_context(
                entity_type=entity_type,
                entity_id=entity_id,
                context=context
            )
            print(f"  • {entity_type}/{entity_id}: {list(context.keys())}")

        # Get global context
        print(f"\n{Fore.CYAN}Retrieving global context...{Style.RESET_ALL}")
        global_context = self.memory.get_global_context()

        if global_context.get('agents') or global_context.get('advisors'):
            print(f"\n{Fore.GREEN}✅ GLOBAL CONTEXT AVAILABLE:{Style.RESET_ALL}")

            agents_count = len(global_context.get('agents', {}))
            advisors_count = len(global_context.get('advisors', {}))

            print(f"  • Active Agents: {agents_count}")
            for agent_id, ctx in global_context.get('agents', {}).items():
                print(f"    - {agent_id}: {list(ctx.keys())}")

            print(f"  • Active Advisors: {advisors_count}")
            for advisor_id, ctx in global_context.get('advisors', {}).items():
                print(f"    - {advisor_id}: {list(ctx.keys())}")
        else:
            print(f"{Fore.RED}❌ No global context found{Style.RESET_ALL}")

        return bool(global_context.get('agents') or global_context.get('advisors'))

    async def run_all_tests(self):
        """Run all integration tests"""
        self.print_section("MEMORY-COLLABORATION INTEGRATION TEST SUITE", Fore.YELLOW)

        print(f"{Fore.CYAN}Testing integration between:")
        print(f"  • Shared Memory System")
        print(f"  • Collaboration Tracking System")
        print(f"  • Knowledge Graph")
        print(f"  • Collective Learning{Style.RESET_ALL}")

        results = {
            "Memory during handoff": await self.test_memory_during_handoff(),
            "Experience sharing": await self.test_experience_sharing(),
            "Knowledge graph": await self.test_knowledge_graph_building(),
            "Collective learning": await self.test_collective_learning(),
            "Global context": await self.test_global_context_sharing()
        }

        # Display summary
        self.print_section("TEST RESULTS SUMMARY", Fore.YELLOW)

        passed = sum(1 for v in results.values() if v)
        total = len(results)

        for test_name, success in results.items():
            status = f"{Fore.GREEN}✅ PASSED{Style.RESET_ALL}" if success else f"{Fore.RED}❌ FAILED{Style.RESET_ALL}"
            print(f"  {test_name}: {status}")

        print(f"\n{Fore.YELLOW}Overall: {passed}/{total} tests passed{Style.RESET_ALL}")

        if passed == total:
            print(f"\n{Fore.GREEN}🎉 SUCCESS! Memory and Collaboration systems are fully integrated!{Style.RESET_ALL}")
            print(f"\nKey Integration Points Verified:")
            print(f"  ✓ Memories are automatically created during collaborations")
            print(f"  ✓ Agents share and learn from experiences")
            print(f"  ✓ Knowledge graph tracks agent relationships")
            print(f"  ✓ Collective learning enables system-wide improvement")
            print(f"  ✓ Global context sharing enables coordination")
        else:
            print(f"\n{Fore.RED}⚠️ Some integration points need attention{Style.RESET_ALL}")


if __name__ == "__main__":
    test = MemoryCollaborationTest()
    asyncio.run(test.run_all_tests())