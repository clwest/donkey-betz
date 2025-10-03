#!/usr/bin/env python3
"""
Agent Reality Checker
====================
Tests agents to determine if they're actually executing or just returning mock data.

Checks:
1. Does the agent make real API calls? (OpenAI, Serper, etc.)
2. Does it return unique/dynamic data or static responses?
3. Is it connected to learning bridges?
4. Does it have actual execution logic?

Usage:
    python scripts/agent_reality_checker.py
"""

import os
import sys
import django
import asyncio
import json
import random
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_core.agents.universal_agent_loader import get_all_agent_classes


class AgentRealityChecker:
    """Check if agents are real or mock"""

    def __init__(self):
        self.results = {
            'real_agents': [],
            'mock_agents': [],
            'broken_agents': [],
            'untested_agents': []
        }

    async def check_agent(self, agent_class):
        """Test a single agent for reality"""

        agent_name = agent_class.__name__

        try:
            # Instantiate the agent
            agent = agent_class()

            # Check 1: Does it have an execute method?
            if not hasattr(agent, 'execute'):
                return {
                    'name': agent_name,
                    'status': 'broken',
                    'reason': 'No execute method',
                    'reality_score': 0.0
                }

            # Check 2: Determine if this is a dynamic or hardcoded agent
            import inspect
            is_dynamic = False
            source = None

            try:
                source = inspect.getsource(agent_class)
            except (OSError, TypeError):
                # This is a dynamically created agent from database
                is_dynamic = True
                source = ""

            # Reality indicators (different for dynamic vs hardcoded)
            if is_dynamic:
                # For dynamic agents, check the instance attributes
                reality_indicators = {
                    'has_openai': hasattr(agent, 'generate_ai_text') or hasattr(agent, 'client'),
                    'has_api_calls': hasattr(agent, 'config') and bool(agent.config.get('configuration')),
                    'has_serper': False,  # Dynamic agents don't use Serper directly
                    'has_real_data': hasattr(agent, 'capabilities') and len(agent.capabilities) > 0,
                    'avoids_mock': True,  # Assume dynamic agents avoid mock
                    'has_async': asyncio.iscoroutinefunction(agent.execute),
                    'has_real_logic': hasattr(agent, 'specialization') and agent.specialization != 'general',
                }
            else:
                # For hardcoded agents, check source code
                reality_indicators = {
                    'has_openai': 'openai' in source.lower() or 'gpt-' in source.lower(),
                    'has_api_calls': 'client.' in source or 'api_key' in source.lower(),
                    'has_serper': 'serper' in source.lower(),
                    'has_real_data': 'requests.' in source or 'httpx.' in source or 'aiohttp.' in source,
                    'avoids_mock': 'mock' not in source.lower() or source.lower().count('mock') < 3,
                    'has_async': 'async def' in source,
                    'has_real_logic': len(source) > 1000,  # Substantial code
                }

            # Check 3: Try executing with a test instruction
            test_instruction = {
                'action': 'test_execution',
                'prompt': 'Generate a random 5-digit number',
                'agent_type': agent_name
            }

            execution_result = None
            execution_success = False
            is_dynamic = False

            try:
                # Try async execution
                if asyncio.iscoroutinefunction(agent.execute):
                    execution_result = await agent.execute(test_instruction)
                else:
                    execution_result = agent.execute(test_instruction)

                execution_success = True

                # Check if result is dynamic (contains current timestamp, random data, etc.)
                result_str = str(execution_result)
                is_dynamic = (
                    str(datetime.now().year) in result_str or
                    'random' in result_str.lower() or
                    len(result_str) > 100  # Substantial response
                )

            except Exception as exec_error:
                execution_result = f"Error: {exec_error}"
                execution_success = False

            # Calculate reality score (0.0 to 1.0)
            score = 0.0
            score += 0.3 if reality_indicators['has_openai'] else 0.0
            score += 0.2 if reality_indicators['has_api_calls'] else 0.0
            score += 0.1 if reality_indicators['has_serper'] else 0.0
            score += 0.1 if reality_indicators['has_real_data'] else 0.0
            score += 0.1 if reality_indicators['avoids_mock'] else 0.0
            score += 0.1 if execution_success else 0.0
            score += 0.1 if is_dynamic else 0.0

            # Classify the agent
            if score >= 0.7:
                status = 'real'
            elif score >= 0.4:
                status = 'partial'
            elif execution_success:
                status = 'mock'
            else:
                status = 'broken'

            return {
                'name': agent_name,
                'status': status,
                'reality_score': round(score, 2),
                'indicators': reality_indicators,
                'execution_success': execution_success,
                'is_dynamic_agent': is_dynamic,
                'code_size': len(source),
                'agent_type': getattr(agent, 'specialization', 'unknown') if is_dynamic else 'hardcoded'
            }

        except Exception as e:
            return {
                'name': agent_name,
                'status': 'broken',
                'reason': str(e),
                'reality_score': 0.0
            }

    async def audit_agents(self, sample_size=20):
        """Audit a random sample of agents"""

        print("=" * 80)
        print("🔍 AGENT REALITY CHECKER")
        print("=" * 80)
        print()

        # Get all agents
        all_agents_raw = get_all_agent_classes()

        # Convert to list if it's a dict or set
        if isinstance(all_agents_raw, dict):
            all_agents = list(all_agents_raw.values())
        elif isinstance(all_agents_raw, set):
            all_agents = list(all_agents_raw)
        else:
            all_agents = list(all_agents_raw)

        print(f"📊 Found {len(all_agents)} total agents")

        # Sample random agents
        if len(all_agents) <= sample_size:
            agents_to_test = all_agents
        else:
            agents_to_test = random.sample(all_agents, sample_size)

        print(f"🎲 Testing {len(agents_to_test)} random agents...")
        print()

        results = []
        for i, agent_class in enumerate(agents_to_test, 1):
            print(f"[{i}/{len(agents_to_test)}] Testing {agent_class.__name__}...", end=' ')

            result = await self.check_agent(agent_class)
            results.append(result)

            # Status emoji
            status_emoji = {
                'real': '✅',
                'partial': '⚠️',
                'mock': '🎭',
                'broken': '❌'
            }

            emoji = status_emoji.get(result['status'], '❓')
            print(f"{emoji} {result['status'].upper()} (score: {result['reality_score']})")

        # Categorize results
        real_agents = [r for r in results if r['status'] == 'real']
        partial_agents = [r for r in results if r['status'] == 'partial']
        mock_agents = [r for r in results if r['status'] == 'mock']
        broken_agents = [r for r in results if r['status'] == 'broken']

        # Print summary
        print()
        print("=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"✅ Real Agents:    {len(real_agents)} ({len(real_agents)/len(results)*100:.1f}%)")
        print(f"⚠️  Partial Agents: {len(partial_agents)} ({len(partial_agents)/len(results)*100:.1f}%)")
        print(f"🎭 Mock Agents:    {len(mock_agents)} ({len(mock_agents)/len(results)*100:.1f}%)")
        print(f"❌ Broken Agents:  {len(broken_agents)} ({len(broken_agents)/len(results)*100:.1f}%)")
        print()

        # Show details for each category
        if real_agents:
            print("✅ REAL AGENTS (Using actual APIs):")
            for agent in sorted(real_agents, key=lambda x: x['reality_score'], reverse=True)[:5]:
                print(f"   • {agent['name']} (score: {agent['reality_score']})")

        print()

        if partial_agents:
            print("⚠️  PARTIAL AGENTS (Some real logic, needs improvement):")
            for agent in sorted(partial_agents, key=lambda x: x['reality_score'], reverse=True):
                print(f"   • {agent['name']} (score: {agent['reality_score']})")

        print()

        if mock_agents:
            print("🎭 MOCK AGENTS (Returning fake data):")
            for agent in mock_agents[:5]:
                print(f"   • {agent['name']} (score: {agent['reality_score']})")

        print()

        if broken_agents:
            print("❌ BROKEN AGENTS (Need fixing):")
            for agent in broken_agents[:5]:
                reason = agent.get('reason', 'Unknown error')
                print(f"   • {agent['name']}: {reason}")

        print()
        print("=" * 80)
        print("🎯 RECOMMENDED FIXES")
        print("=" * 80)

        # Identify high-value targets for fixing
        needs_fixing = partial_agents + mock_agents
        if needs_fixing:
            print("Top agents to upgrade to real execution:")
            for agent in sorted(needs_fixing, key=lambda x: x['reality_score'], reverse=True)[:5]:
                print(f"   {agent['reality_score']*100:.0f}% → {agent['name']}")

        if broken_agents:
            print()
            print("Broken agents that need immediate attention:")
            for agent in broken_agents[:3]:
                print(f"   ❌ {agent['name']}")

        print()
        print("=" * 80)

        # Extrapolate to full agent population
        real_percentage = len(real_agents) / len(results) * 100
        estimated_real = int(len(all_agents) * (len(real_agents) / len(results)))
        estimated_fixable = int(len(all_agents) * (len(partial_agents + mock_agents) / len(results)))

        print("📈 SYSTEM-WIDE ESTIMATE (based on sample):")
        print(f"   • Total Agents: {len(all_agents)}")
        print(f"   • Estimated Real: ~{estimated_real} ({real_percentage:.1f}%)")
        print(f"   • Estimated Fixable: ~{estimated_fixable}")
        print(f"   • Potential After Fixes: ~{estimated_real + estimated_fixable} agents")
        print("=" * 80)

        # Save detailed results
        report_file = f"agent_reality_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_agents': len(all_agents),
                'tested': len(results),
                'results': results,
                'summary': {
                    'real': len(real_agents),
                    'partial': len(partial_agents),
                    'mock': len(mock_agents),
                    'broken': len(broken_agents)
                }
            }, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_file}")

        return results


async def main():
    """Run the agent reality check"""

    checker = AgentRealityChecker()

    # Test 20 random agents (adjust as needed)
    sample_size = 20
    if len(sys.argv) > 1:
        sample_size = int(sys.argv[1])

    results = await checker.audit_agents(sample_size=sample_size)

    print("\n🚀 Next Steps:")
    print("   1. Review the detailed report JSON file")
    print("   2. Pick top 5-10 agents to upgrade")
    print("   3. Add real API calls to partial/mock agents")
    print("   4. Re-run this checker to track progress")
    print()


if __name__ == '__main__':
    asyncio.run(main())
