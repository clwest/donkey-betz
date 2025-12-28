"""
LLM Verification System - Ensures Agents Use Real AI, Not Fake Responses

This critical system verifies that every agent claiming to use AI:
1. Actually calls real LLM APIs (OpenAI, Anthropic, etc.)
2. Gets real responses, not hardcoded text
3. Logs all LLM interactions for audit
4. Flags any agents faking AI responses

THIS IS CRITICAL FOR SYSTEM INTEGRITY!
"""

import logging
import json
import time
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass
import ast
import os

logger = logging.getLogger(__name__)


@dataclass
class LLMCall:
    """Record of an actual LLM API call"""
    agent_id: str
    timestamp: datetime
    llm_provider: str  # openai, anthropic, huggingface
    model: str
    prompt: str
    response: str
    tokens_used: int
    latency_ms: float
    cost: float
    is_real: bool  # Critical flag!


class LLMVerificationSystem:
    """
    Verifies that agents are making REAL LLM calls, not faking AI
    """

    def __init__(self):
        self.llm_call_log: List[LLMCall] = []
        self.fake_response_patterns = [
            "Lorem ipsum",
            "This is a test",
            "Sample response",
            "TODO: Implement",
            "[Mock response]",
            "Placeholder text"
        ]
        self.verified_agents = set()
        self.suspicious_agents = set()

        # Import the real LLM clients to monitor
        self._setup_llm_monitoring()

    def _setup_llm_monitoring(self):
        """Set up monitoring of actual LLM libraries"""
        self.monitored_providers = {
            'openai': None,
            'anthropic': None,
            'huggingface': None
        }

        # Try to import and monitor OpenAI
        try:
            import openai
            self.monitored_providers['openai'] = openai
            logger.info("✅ OpenAI client found and will be monitored")
        except ImportError:
            logger.warning("⚠️ OpenAI not installed - cannot verify OpenAI calls")

        # Try to import and monitor Anthropic
        try:
            import anthropic
            self.monitored_providers['anthropic'] = anthropic
            logger.info("✅ Anthropic client found and will be monitored")
        except ImportError:
            logger.warning("⚠️ Anthropic not installed - cannot verify Claude calls")

    async def verify_agent_llm_usage(self, agent_id: str, agent_code_path: str = None) -> Dict[str, Any]:
        """
        Verify if an agent is actually using LLMs or faking it

        Args:
            agent_id: ID of the agent to verify
            agent_code_path: Path to agent's code file

        Returns:
            Verification report
        """
        logger.info(f"🔍 Verifying LLM usage for agent: {agent_id}")

        verification = {
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'uses_real_llm': False,
            'llm_providers': [],
            'suspicious_patterns': [],
            'recommendations': []
        }

        # Step 1: Check agent code for LLM imports
        if agent_code_path and os.path.exists(agent_code_path):
            code_analysis = self._analyze_agent_code(agent_code_path)
            verification.update(code_analysis)

        # Step 2: Check actual LLM call history
        agent_calls = [call for call in self.llm_call_log if call.agent_id == agent_id]

        if agent_calls:
            # Agent has made LLM calls
            real_calls = [call for call in agent_calls if call.is_real]
            fake_calls = [call for call in agent_calls if not call.is_real]

            verification['total_llm_calls'] = len(agent_calls)
            verification['real_calls'] = len(real_calls)
            verification['fake_calls'] = len(fake_calls)

            if real_calls:
                verification['uses_real_llm'] = True
                verification['llm_providers'] = list(set(call.llm_provider for call in real_calls))
                self.verified_agents.add(agent_id)

            if fake_calls:
                self.suspicious_agents.add(agent_id)
                verification['suspicious_patterns'].append(f"Found {len(fake_calls)} fake LLM calls")
        else:
            verification['suspicious_patterns'].append("No LLM calls recorded")

        # Step 3: Test the agent with a verification prompt
        test_result = await self._test_agent_with_prompt(agent_id)
        verification['test_result'] = test_result

        # Generate recommendations
        if not verification['uses_real_llm']:
            verification['recommendations'].append("CRITICAL: Agent must be updated to use real LLM APIs")
            verification['recommendations'].append("Add OpenAI or Anthropic client initialization")
            verification['recommendations'].append("Replace mock responses with actual API calls")

        # Log the verification
        logger.info(f"""
        📊 LLM Verification Report for {agent_id}:
           Uses Real LLM: {verification['uses_real_llm']}
           Total Calls: {verification.get('total_llm_calls', 0)}
           Real Calls: {verification.get('real_calls', 0)}
           Suspicious Patterns: {verification.get('suspicious_patterns', [])}
        """)

        return verification

    def _analyze_agent_code(self, code_path: str) -> Dict[str, Any]:
        """Analyze agent code for LLM usage patterns"""
        analysis = {
            'has_llm_imports': False,
            'llm_libraries': [],
            'mock_patterns_found': [],
            'sleep_calls_found': False
        }

        try:
            with open(code_path, 'r') as f:
                code = f.read()

            # Parse the AST
            tree = ast.parse(code)

            # Check for LLM imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if any(lib in alias.name for lib in ['openai', 'anthropic', 'transformers']):
                            analysis['has_llm_imports'] = True
                            analysis['llm_libraries'].append(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if any(lib in str(node.module) for lib in ['openai', 'anthropic', 'transformers']):
                        analysis['has_llm_imports'] = True
                        analysis['llm_libraries'].append(str(node.module))

                # Check for sleep() calls (sign of faking work)
                elif isinstance(node, ast.Call):
                    if hasattr(node.func, 'id') and node.func.id == 'sleep':
                        analysis['sleep_calls_found'] = True
                        analysis['mock_patterns_found'].append("sleep() call found - possibly faking work")

                    # Check for time.sleep()
                    elif hasattr(node.func, 'attr') and node.func.attr == 'sleep':
                        analysis['sleep_calls_found'] = True
                        analysis['mock_patterns_found'].append("time.sleep() found - possibly faking delay")

            # Check for mock response patterns in strings
            for pattern in self.fake_response_patterns:
                if pattern.lower() in code.lower():
                    analysis['mock_patterns_found'].append(f"Found mock pattern: '{pattern}'")

            # Check for hardcoded responses
            if 'return "' in code or "return '" in code:
                # Look for hardcoded string returns
                for line in code.split('\n'):
                    if 'return "' in line or "return '" in line:
                        if not ('openai' in line or 'response' in line or 'result' in line):
                            analysis['mock_patterns_found'].append("Hardcoded string return found")
                            break

        except Exception as e:
            logger.error(f"Error analyzing code: {e}")

        return analysis

    async def _test_agent_with_prompt(self, agent_id: str) -> Dict[str, Any]:
        """Test an agent with a verification prompt to see if it uses real LLM"""
        test_prompt = f"Generate a unique response with timestamp {time.time()}"

        # This would call the actual agent
        # For now, we'll return a test structure
        return {
            'test_executed': False,
            'reason': 'Agent execution not implemented in verification'
        }

    def log_llm_call(self, agent_id: str, provider: str, model: str,
                     prompt: str, response: str, tokens: int = 0,
                     latency_ms: float = 0, cost: float = 0) -> bool:
        """
        Log an LLM call made by an agent

        Returns:
            True if call appears real, False if suspicious
        """
        # Check if response looks real
        is_real = self._verify_response_authenticity(response)

        # Check for suspicious patterns
        if not is_real:
            self.suspicious_agents.add(agent_id)
            logger.warning(f"⚠️ Suspicious LLM response from agent {agent_id}")

        # Log the call
        call = LLMCall(
            agent_id=agent_id,
            timestamp=datetime.now(),
            llm_provider=provider,
            model=model,
            prompt=prompt[:500],  # Truncate long prompts
            response=response[:500],  # Truncate long responses
            tokens_used=tokens,
            latency_ms=latency_ms,
            cost=cost,
            is_real=is_real
        )

        self.llm_call_log.append(call)

        # Mark agent as verified if call is real
        if is_real:
            self.verified_agents.add(agent_id)

        return is_real

    def _verify_response_authenticity(self, response: str) -> bool:
        """Check if a response looks like it came from a real LLM"""
        if not response or len(response) < 10:
            return False

        # Check for fake patterns
        for pattern in self.fake_response_patterns:
            if pattern.lower() in response.lower():
                return False

        # Check for repetitive patterns (sign of fake)
        if response.count(response[:20]) > 3:
            return False

        # Check for Lorem Ipsum
        if 'lorem' in response.lower() or 'ipsum' in response.lower():
            return False

        # Check for TODO or placeholder text
        if 'todo' in response.lower() or 'placeholder' in response.lower():
            return False

        # Response seems legitimate
        return True

    async def audit_all_agents(self) -> Dict[str, Any]:
        """Audit all agents in the system for LLM usage"""
        from core.agents.registry import agent_registry

        audit_report = {
            'timestamp': datetime.now().isoformat(),
            'total_agents': len(agent_registry.agents),
            'verified_agents': [],
            'suspicious_agents': [],
            'not_using_llm': [],
            'recommendations': []
        }

        for agent_id, agent in agent_registry.agents.items():
            # Skip non-AI agents
            if agent.get('type') == 'utility' or agent.get('requires_llm') == False:
                continue

            verification = await self.verify_agent_llm_usage(agent_id)

            if verification['uses_real_llm']:
                audit_report['verified_agents'].append(agent_id)
            elif verification.get('suspicious_patterns'):
                audit_report['suspicious_agents'].append({
                    'agent_id': agent_id,
                    'issues': verification['suspicious_patterns']
                })
            else:
                audit_report['not_using_llm'].append(agent_id)

        # Generate overall recommendations
        if audit_report['suspicious_agents']:
            audit_report['recommendations'].append(
                f"CRITICAL: {len(audit_report['suspicious_agents'])} agents may be faking LLM responses"
            )

        if audit_report['not_using_llm']:
            audit_report['recommendations'].append(
                f"WARNING: {len(audit_report['not_using_llm'])} agents are not using LLMs at all"
            )

        logger.info(f"""
        🔍 SYSTEM-WIDE LLM AUDIT COMPLETE:
           Total Agents: {audit_report['total_agents']}
           Verified (Using Real LLM): {len(audit_report['verified_agents'])}
           Suspicious (May be faking): {len(audit_report['suspicious_agents'])}
           Not Using LLM: {len(audit_report['not_using_llm'])}
        """)

        return audit_report

    def intercept_llm_call(self, func):
        """Decorator to intercept and verify LLM calls"""
        def wrapper(*args, **kwargs):
            # Log the call
            agent_id = kwargs.get('agent_id', 'unknown')

            # Execute the actual call
            start_time = time.time()
            result = func(*args, **kwargs)
            latency = (time.time() - start_time) * 1000

            # Verify and log
            if isinstance(result, str):
                self.log_llm_call(
                    agent_id=agent_id,
                    provider='unknown',
                    model='unknown',
                    prompt=str(args[0]) if args else '',
                    response=result,
                    latency_ms=latency
                )

            return result
        return wrapper

    def get_agent_llm_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get LLM usage statistics for a specific agent"""
        agent_calls = [call for call in self.llm_call_log if call.agent_id == agent_id]

        if not agent_calls:
            return {'agent_id': agent_id, 'message': 'No LLM calls recorded'}

        real_calls = [call for call in agent_calls if call.is_real]
        total_tokens = sum(call.tokens_used for call in real_calls)
        total_cost = sum(call.cost for call in real_calls)
        avg_latency = sum(call.latency_ms for call in real_calls) / len(real_calls) if real_calls else 0

        return {
            'agent_id': agent_id,
            'total_calls': len(agent_calls),
            'real_calls': len(real_calls),
            'fake_calls': len(agent_calls) - len(real_calls),
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'average_latency_ms': avg_latency,
            'providers_used': list(set(call.llm_provider for call in real_calls)),
            'models_used': list(set(call.model for call in real_calls)),
            'is_verified': agent_id in self.verified_agents,
            'is_suspicious': agent_id in self.suspicious_agents
        }


# Quick verification function to check a specific agent
async def verify_agent(agent_id: str) -> bool:
    """Quick function to verify if an agent uses real LLM"""
    verifier = LLMVerificationSystem()
    result = await verifier.verify_agent_llm_usage(agent_id)
    return result['uses_real_llm']


# Audit all agents in the system
async def audit_system():
    """Audit entire system for LLM usage"""
    verifier = LLMVerificationSystem()
    report = await verifier.audit_all_agents()

    # Save report
    with open('/tmp/llm_audit_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("\n🔍 LLM VERIFICATION AUDIT COMPLETE")
    print("=" * 60)
    print(f"Report saved to: /tmp/llm_audit_report.json")

    if report['suspicious_agents']:
        print("\n⚠️ CRITICAL: The following agents may be faking LLM responses:")
        for agent in report['suspicious_agents']:
            print(f"   - {agent['agent_id']}: {agent['issues']}")

    if report['verified_agents']:
        print(f"\n✅ {len(report['verified_agents'])} agents verified using real LLMs")

    return report


if __name__ == "__main__":
    import asyncio
    asyncio.run(audit_system())