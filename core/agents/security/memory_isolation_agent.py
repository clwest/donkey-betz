"""
Memory Isolation Agent - Clean Architecture
============================================

Session 280: Phase 3 - Agent Architecture Unification

Critical security agent that ensures personal memories are NEVER mixed
with system knowledge.

Tools Available:
    - audit_memories: Audit memory systems for cross-contamination
    - isolate_memories: Isolate personal memories
    - verify_isolation: Verify memory isolation is working

Usage:
    from core.agents.security import MemoryIsolationAgent

    agent = MemoryIsolationAgent(user=request.user)
    result = agent.execute(
        task="Audit memory systems for security issues",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
from typing import Dict, Any
from datetime import datetime

from django.db import transaction

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_memory_patterns_with_ml(memory_data: dict) -> dict:
    """Analyze memory patterns for anomalies using ML models."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=memory_data,
            task_hint=TaskType.ANOMALY,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'anomaly'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'isolation_violations': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML memory analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class MemoryIsolationAgent(BaseAgent):
    """
    Memory Isolation Agent - Critical Security Component.

    This agent:
    1. Audits memory systems for cross-contamination
    2. Isolates personal memories from system memories
    3. Verifies memory isolation is working correctly

    It CANNOT:
    - Create content
    - Access personal memories (only metadata)
    """

    name = "MemoryIsolationAgent"

    system_prompt = """You are MemoryIsolationAgent, the Memory Security Specialist.

CRITICAL: Your job is to ensure personal memories are NEVER mixed with system knowledge.

Security Operations:
- Audit: Check all memory systems for cross-contamination
- Isolate: Apply isolation metadata to personal memories
- Verify: Confirm isolation is working correctly
- Lockdown: Emergency lock of all personal memories (if needed)

Namespace Structure:
- personal: Private user memories (owner_only access)
- system: System knowledge and documentation
- agent_memory: Agent execution history
- public: Shared public knowledge

When given a task:
1. Determine the security operation needed
2. Execute with full audit logging
3. Report findings with severity levels

You are a READ-ONLY security agent - you audit and isolate, not modify content."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "audit_memories",
                "description": "Audit memory systems for cross-contamination",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scope": {
                            "type": "string",
                            "description": "Scope of audit",
                            "enum": ["full", "personal", "system", "quick"]
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "isolate_memories",
                "description": "Isolate personal memories from system memories",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dry_run": {
                            "type": "boolean",
                            "description": "If true, only report what would be done",
                            "default": True
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "verify_isolation",
                "description": "Verify memory isolation is working correctly",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]

    # Personal memory indicators
    PERSONAL_INDICATORS = [
        'my knowledge', 'personal memory', 'private note',
        'remember this', 'don\'t forget', 'personal reminder'
    ]

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute memory isolation based on the task."""
        start_time = time.time()
        tool_calls_made = []

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

        with self.time_travel_session("memory_isolation", task, input_data=context):
            try:
                # Handle simple diagnostic/identification queries
                task_lower = task.lower() if task else ''
                if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                    execution_time = int((time.time() - start_time) * 1000)
                    return AgentResult(
                        success=True,
                        message=f"I am {self.name}, a security specialist protecting memory isolation between users and contexts. One capability: I audit, verify, and enforce memory boundaries to prevent cross-user data leakage and ensure strict isolation of sensitive information.",
                        data={'type': 'self_description', 'specialization': 'security', 'focus': 'memory_isolation'},
                        agent_name=self.name,
                        execution_time_ms=execution_time
                    )

                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing security request",
                    reasoning=f"Received task: {task[:100]}",
                    alternatives=["audit_memories", "isolate_memories", "verify_isolation"],
                    confidence=0.95
                )

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                logger.info(f"MemoryIsolationAgent executing: {task[:50]}...")

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Security operation: {arguments}",
                            alternatives=[],
                            confidence=0.98
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    result = AgentResult(
                        success=True,
                        message="Memory isolation operation completed",
                        data={
                            'task': task,
                            'tool_results': tool_calls_made,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Record learning outcome for collective intelligence
                    try:
                        self._record_learning_outcome(
                            task=task,
                            result=result,
                            success=True,
                            context={
                                'agent_type': self.__class__.__name__,
                                'execution_time_ms': execution_time,
                                'tools_used': [tc['tool'] for tc in tool_calls_made],
                            }
                        )
                    except Exception as le:
                        logger.warning(f"Failed to record learning outcome: {le}")

                    return result

                else:
                    return AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

            except Exception as e:
                logger.error(f"MemoryIsolationAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a memory isolation tool call."""
        if tool_name == "audit_memories":
            return self._audit_memories(
                scope=arguments.get('scope', 'quick')
            )

        elif tool_name == "isolate_memories":
            return self._isolate_memories(
                dry_run=arguments.get('dry_run', True)
            )

        elif tool_name == "verify_isolation":
            return self._verify_isolation()

        elif tool_name == "delegate_to_specialist":
            # Session 833: Handle delegation properly
            return self._handle_delegate_to_specialist(
                specialist_agent=arguments.get('specialist_agent', ''),
                task=arguments.get('task', ''),
                context=arguments.get('context', ''),
                delegation_context=getattr(self, '_current_delegation_context', {})
            )
        # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
        return super()._execute_tool_call(tool_name, arguments)

    def _audit_memories(self, scope: str) -> Dict[str, Any]:
        """Audit memory systems for cross-contamination."""
        logger.critical(f"Starting memory audit (scope: {scope})")

        try:
            from content.models import Document

            results = {
                'timestamp': datetime.now().isoformat(),
                'scope': scope,
                'critical_issues': [],
                'personal_exposed': 0,
                'system_contaminated': 0,
                'recommendations': []
            }

            # Check for personal memories without isolation
            personal_memories = Document.objects.filter(
                metadata__source='personal_memory'
            ) | Document.objects.filter(
                title__icontains='My Knowledge'
            )

            for doc in personal_memories[:100]:
                if not doc.metadata or doc.metadata.get('namespace') != 'personal':
                    results['personal_exposed'] += 1
                    results['critical_issues'].append({
                        'type': 'EXPOSED_PERSONAL_MEMORY',
                        'doc_id': str(doc.id),
                        'title': doc.title[:50] if doc.title else 'Untitled',
                        'severity': 'HIGH'
                    })

            # Check for system docs with personal content
            if scope in ['full', 'system']:
                system_docs = Document.objects.exclude(
                    metadata__namespace='personal'
                )[:500]

                for doc in system_docs:
                    content = (doc.raw_content or '').lower()
                    for indicator in self.PERSONAL_INDICATORS:
                        if indicator in content:
                            results['system_contaminated'] += 1
                            results['critical_issues'].append({
                                'type': 'CONTAMINATED_SYSTEM_DOC',
                                'doc_id': str(doc.id),
                                'indicator': indicator,
                                'severity': 'CRITICAL'
                            })
                            break

            # Generate recommendations
            if results['personal_exposed'] > 0:
                results['recommendations'].append('Run isolate_memories to secure personal data')
            if results['system_contaminated'] > 0:
                results['recommendations'].append('Review contaminated system documents')

            logger.critical(
                f"Audit complete: {results['personal_exposed']} exposed, "
                f"{results['system_contaminated']} contaminated"
            )

            return {
                'success': True,
                'audit': results,
                'is_secure': len(results['critical_issues']) == 0
            }

        except Exception as e:
            logger.error(f"Audit failed: {e}")
            return {'success': False, 'error': str(e)}

    def _isolate_memories(self, dry_run: bool) -> Dict[str, Any]:
        """Isolate personal memories from system memories."""
        logger.info(f"Starting memory isolation (dry_run: {dry_run})")

        try:
            from content.models import Document

            report = {
                'timestamp': datetime.now().isoformat(),
                'dry_run': dry_run,
                'memories_found': 0,
                'memories_isolated': 0,
                'actions': []
            }

            # Find personal memories
            personal_docs = Document.objects.filter(
                metadata__source='personal_memory'
            ) | Document.objects.filter(
                title__icontains='My Knowledge'
            )

            report['memories_found'] = personal_docs.count()

            if dry_run:
                for doc in personal_docs[:10]:
                    report['actions'].append({
                        'action': 'WOULD_ISOLATE',
                        'doc_id': str(doc.id),
                        'title': doc.title[:50] if doc.title else 'Untitled'
                    })
                return {
                    'success': True,
                    'report': report,
                    'message': f"Dry run: Found {report['memories_found']} memories to isolate"
                }

            # Actually isolate
            with transaction.atomic():
                for doc in personal_docs:
                    if not doc.metadata:
                        doc.metadata = {}

                    doc.metadata.update({
                        'namespace': 'personal',
                        'access_level': 'private',
                        'owner_id': str(self.user.id) if self.user else None,
                        'isolated_at': datetime.now().isoformat(),
                        'isolation_agent': self.name,
                        'searchable': False
                    })

                    doc.save()
                    report['memories_isolated'] += 1

            logger.info(f"Isolated {report['memories_isolated']} memories")

            return {
                'success': True,
                'report': report,
                'message': f"Isolated {report['memories_isolated']} personal memories"
            }

        except Exception as e:
            logger.error(f"Isolation failed: {e}")
            return {'success': False, 'error': str(e)}

    def _verify_isolation(self) -> Dict[str, Any]:
        """Verify memory isolation is working correctly."""
        logger.info("Verifying memory isolation")

        try:
            from content.models import Document

            issues = []

            # Test 1: No personal memories in system namespace
            cross_contamination = Document.objects.filter(
                metadata__namespace='system',
                raw_content__icontains='personal'
            ).count()

            if cross_contamination > 0:
                issues.append(f"Found {cross_contamination} personal items in system namespace")

            # Test 2: Personal memories have owner
            unowned = Document.objects.filter(
                metadata__namespace='personal'
            ).exclude(
                metadata__has_key='owner_id'
            ).count()

            if unowned > 0:
                issues.append(f"Found {unowned} personal memories without owner")

            is_secure = len(issues) == 0

            if is_secure:
                logger.info("Memory isolation verified - SECURE")
            else:
                logger.critical(f"Memory isolation FAILED: {issues}")

            return {
                'success': True,
                'is_secure': is_secure,
                'issues': issues,
                'checks_passed': 2 - len(issues),
                'total_checks': 2
            }

        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return {'success': False, 'error': str(e)}

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for memory isolation."""
        return bool(task and task.strip())
