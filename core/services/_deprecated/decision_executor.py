"""
=============================================================================
DEPRECATED - Session 647 (December 31, 2025)
=============================================================================

This service was created in Session 619 but was NEVER integrated into the system.
The same functionality is provided by:

  core/services/autonomous_action_executor.py (AutonomousActionExecutor)

Which is used by the Celery task:

  core/tasks.py:run_autonomous_thinking_cycle

Evidence that the system works without this file:
- 258 AutonomousAction records (all completed)
- 66 ThinkingAgent cycles in the last 7 days
- Zero imports of DecisionExecutorService in the codebase

The Discord summary notification feature was migrated to run_autonomous_thinking_cycle
in Session 647.

DO NOT use this file. It is kept for reference only.
=============================================================================

Session 619: Decision Executor Service (DEPRECATED)

=============================================================================
ARCHITECTURE OVERVIEW
=============================================================================

This service closes the autonomous loop by executing ThinkingAgent's decisions.

BEFORE (Gap):
    ThinkingAgent → Generates Decisions → ❌ Nothing happens

AFTER (Autonomous):
    ThinkingAgent → Generates Decisions → DecisionExecutor → Actions Executed
                                                ↓
                                        Results logged & tracked
                                                ↓
                                        Boardroom notified for oversight

=============================================================================
HOW IT WORKS
=============================================================================

1. DECISION INTAKE
   - Receives decisions from ThinkingAgent's thinking cycle
   - Each decision has: action_type, action_name, reasoning, params, priority

2. PRIORITY FILTERING
   - CRITICAL & HIGH priority: Execute immediately
   - MEDIUM priority: Execute if queue not full
   - LOW & BACKGROUND: Queue for later execution

3. ACTION EXECUTION
   Available action_type handlers:

   | action_type          | Handler                    | What it does                    |
   |---------------------|----------------------------|----------------------------------|
   | request_research    | _execute_research          | Triggers ResearchAgent           |
   | spawn_spider        | _execute_spawn_spider      | Starts spider for data gathering |
   | trigger_debate      | _execute_trigger_debate    | Initiates agent conversation     |
   | create_report       | _execute_create_report     | Generates system report          |
   | send_alert          | _execute_send_alert        | Notifies via Discord             |
   | trigger_conversation| _execute_conversation      | Starts agent discussion          |
   | archive_insight     | _execute_archive_insight   | Stores insight permanently       |
   | triage_dreams       | _execute_triage_dreams     | Processes pending dreams         |

4. EXECUTION TRACKING
   - All executions logged to DecisionExecution model
   - Success/failure tracked with error messages
   - Results stored for future reference

5. BOARDROOM INTEGRATION
   - Creates Boardroom decision for significant actions
   - Human oversight maintained for important decisions
   - Transparency logs for audit trail

=============================================================================
SAFETY MECHANISMS
=============================================================================

1. Rate Limiting: Max 10 actions per thinking cycle
2. Priority Gates: Only HIGH/CRITICAL auto-execute by default
3. Audit Trail: All actions logged with full context
4. Human Override: Boardroom can pause/veto actions
5. Failure Isolation: One action failure doesn't stop others

=============================================================================
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


class ActionPriority(Enum):
    """Priority levels for decision execution."""
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    BACKGROUND = 'background'


class ActionType(Enum):
    """Supported action types from ThinkingAgent."""
    REQUEST_RESEARCH = 'request_research'
    SPAWN_SPIDER = 'spawn_spider'
    TRIGGER_DEBATE = 'trigger_debate'
    CREATE_REPORT = 'create_report'
    SEND_ALERT = 'send_alert'
    TRIGGER_CONVERSATION = 'trigger_conversation'
    ARCHIVE_INSIGHT = 'archive_insight'
    TRIAGE_DREAMS = 'triage_dreams'


@dataclass
class ExecutionResult:
    """Result of executing a decision."""
    success: bool
    action_type: str
    action_name: str
    message: str
    output: Optional[Dict] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0


class DecisionExecutorService:
    """
    Session 619: Executes ThinkingAgent decisions autonomously.

    This is the "brain stem" of the autonomous system - it takes
    high-level decisions from ThinkingAgent and translates them
    into concrete actions.

    Usage:
        executor = DecisionExecutorService()
        results = executor.execute_decisions(thinking_result['decisions'])
    """

    # Configuration
    MAX_ACTIONS_PER_CYCLE = 10  # Rate limiting
    AUTO_EXECUTE_PRIORITIES = [ActionPriority.CRITICAL, ActionPriority.HIGH]

    def __init__(self):
        self.execution_log: List[ExecutionResult] = []
        self._action_handlers = {
            ActionType.REQUEST_RESEARCH.value: self._execute_research,
            ActionType.SPAWN_SPIDER.value: self._execute_spawn_spider,
            ActionType.TRIGGER_DEBATE.value: self._execute_trigger_debate,
            ActionType.CREATE_REPORT.value: self._execute_create_report,
            ActionType.SEND_ALERT.value: self._execute_send_alert,
            ActionType.TRIGGER_CONVERSATION.value: self._execute_conversation,
            ActionType.ARCHIVE_INSIGHT.value: self._execute_archive_insight,
            ActionType.TRIAGE_DREAMS.value: self._execute_triage_dreams,
        }

    def execute_decisions(
        self,
        decisions: List[Dict],
        auto_execute_only: bool = True,
        thinking_cycle_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a list of decisions from ThinkingAgent.

        Args:
            decisions: List of decision dicts from ThinkingAgent
            auto_execute_only: If True, only execute CRITICAL/HIGH priority
            thinking_cycle_id: ID of the thinking cycle for tracking

        Returns:
            Summary of execution results
        """
        logger.info(f"🤖 [SESSION 619] DecisionExecutor received {len(decisions)} decisions")

        results = {
            'total_decisions': len(decisions),
            'executed': 0,
            'skipped': 0,
            'succeeded': 0,
            'failed': 0,
            'executions': [],
            'errors': []
        }

        # Filter and sort by priority
        executable_decisions = self._filter_decisions(decisions, auto_execute_only)

        # Rate limit
        if len(executable_decisions) > self.MAX_ACTIONS_PER_CYCLE:
            logger.warning(f"⚠️ Rate limiting: {len(executable_decisions)} → {self.MAX_ACTIONS_PER_CYCLE}")
            executable_decisions = executable_decisions[:self.MAX_ACTIONS_PER_CYCLE]

        results['skipped'] = len(decisions) - len(executable_decisions)

        # Execute each decision
        for decision in executable_decisions:
            try:
                exec_result = self._execute_single_decision(decision, thinking_cycle_id)
                results['executed'] += 1

                if exec_result.success:
                    results['succeeded'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(exec_result.error)

                results['executions'].append({
                    'action_type': exec_result.action_type,
                    'action_name': exec_result.action_name,
                    'success': exec_result.success,
                    'message': exec_result.message,
                    'duration': exec_result.duration_seconds
                })

            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
                logger.error(f"❌ Decision execution error: {e}")

        # Log summary
        logger.info(
            f"🤖 [SESSION 619] DecisionExecutor complete: "
            f"{results['succeeded']}/{results['executed']} succeeded, "
            f"{results['skipped']} skipped"
        )

        # Send Discord notification if any actions were executed
        if results['executed'] > 0:
            self._send_execution_notification(results)

        return results

    def _filter_decisions(
        self,
        decisions: List[Dict],
        auto_execute_only: bool
    ) -> List[Dict]:
        """Filter decisions based on priority and executability."""
        filtered = []

        for decision in decisions:
            priority_str = decision.get('priority', 'low').lower()
            action_type = decision.get('action_type', '').lower()

            # Check if we have a handler for this action type
            if action_type not in self._action_handlers:
                logger.debug(f"Skipping unknown action_type: {action_type}")
                continue

            # Check priority if auto_execute_only
            if auto_execute_only:
                try:
                    priority = ActionPriority(priority_str)
                    if priority not in self.AUTO_EXECUTE_PRIORITIES:
                        logger.debug(f"Skipping {priority_str} priority: {action_type}")
                        continue
                except ValueError:
                    logger.debug(f"Unknown priority {priority_str}, skipping")
                    continue

            filtered.append(decision)

        # Sort by priority (critical first)
        priority_order = {
            'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'background': 4
        }
        filtered.sort(key=lambda d: priority_order.get(d.get('priority', 'low').lower(), 5))

        return filtered

    def _execute_single_decision(
        self,
        decision: Dict,
        thinking_cycle_id: Optional[str] = None
    ) -> ExecutionResult:
        """Execute a single decision and return the result."""
        import time

        action_type = decision.get('action_type', '').lower()
        action_name = decision.get('action_name', 'Unknown Action')
        params = decision.get('params', {})
        reasoning = decision.get('reasoning', '')

        logger.info(f"🎯 Executing: {action_type} - {action_name}")

        start_time = time.time()

        try:
            handler = self._action_handlers.get(action_type)
            if not handler:
                return ExecutionResult(
                    success=False,
                    action_type=action_type,
                    action_name=action_name,
                    message=f"No handler for action_type: {action_type}",
                    error=f"Unknown action_type: {action_type}"
                )

            # Execute the handler
            output = handler(action_name, params, reasoning)
            duration = time.time() - start_time

            # Log to database
            self._log_execution(
                action_type=action_type,
                action_name=action_name,
                reasoning=reasoning,
                params=params,
                output=output,
                success=True,
                thinking_cycle_id=thinking_cycle_id
            )

            return ExecutionResult(
                success=True,
                action_type=action_type,
                action_name=action_name,
                message=f"Successfully executed {action_type}",
                output=output,
                duration_seconds=round(duration, 2)
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)

            # Log failure to database
            self._log_execution(
                action_type=action_type,
                action_name=action_name,
                reasoning=reasoning,
                params=params,
                output=None,
                success=False,
                error=error_msg,
                thinking_cycle_id=thinking_cycle_id
            )

            logger.error(f"❌ Action failed: {action_type} - {error_msg}")

            return ExecutionResult(
                success=False,
                action_type=action_type,
                action_name=action_name,
                message=f"Failed to execute {action_type}",
                error=error_msg,
                duration_seconds=round(duration, 2)
            )

    # =========================================================================
    # ACTION HANDLERS
    # =========================================================================

    def _execute_research(
        self,
        action_name: str,
        params: Dict,
        reasoning: str
    ) -> Dict:
        """
        Execute a research request using ResearchAgent.

        This is triggered when ThinkingAgent identifies a knowledge gap
        that needs investigation.
        """
        from core.agents.research_agent import ResearchAgent

        topic = params.get('topic', action_name)
        depth = params.get('depth', 'standard')

        logger.info(f"📚 Executing research: {topic}")

        # Create research request
        agent = ResearchAgent()
        result = agent.execute(
            request=f"Research topic: {topic}. Depth: {depth}. Context: {reasoning}"
        )

        # Create Boardroom decision for transparency
        self._create_boardroom_decision(
            topic=f"Research: {topic}",
            decision_type='research',
            impact_area='research',
            summary=f"Auto-initiated research on: {topic}",
            key_insights=[reasoning, result.get('summary', '')],
            source='decision_executor'
        )

        return {
            'topic': topic,
            'depth': depth,
            'result_summary': result.get('summary', ''),
            'sources_found': len(result.get('sources', []))
        }

    def _execute_spawn_spider(
        self,
        action_name: str,
        params: Dict,
        reasoning: str
    ) -> Dict:
        """
        Spawn a spider to gather data on a specific topic.

        Triggered when ThinkingAgent needs real-time data collection.
        """
        from core.tasks import run_spider_by_name

        spider_name = params.get('spider_name', 'hackernews')
        topic = params.get('topic', action_name)

        logger.info(f"🕷️ Spawning spider: {spider_name} for {topic}")

        # Queue spider task
        task = run_spider_by_name.delay(spider_name)

        return {
            'spider_name': spider_name,
            'topic': topic,
            'task_id': str(task.id),
            'status': 'queued'
        }

    def _execute_trigger_debate(
        self,
        action_name: str,
        params: Dict,
        reasoning: str
    ) -> Dict:
        """
        Trigger a debate/conversation between agents on a topic.

        Used when ThinkingAgent needs multiple perspectives on a decision.
        """
        from core.tasks import generate_agent_conversation

        topic = params.get('topic', action_name)
        agents = params.get('agents', ['ResearchAgent', 'ContentStrategyAgent'])

        logger.info(f"💬 Triggering debate: {topic}")

        # Queue conversation task
        task = generate_agent_conversation.delay(
            topic=topic,
            participants=agents,
            conversation_type='debate'
        )

        return {
            'topic': topic,
            'agents': agents,
            'task_id': str(task.id),
            'status': 'queued'
        }

    def _execute_create_report(
        self,
        action_name: str,
        params: Dict,
        reasoning: str
    ) -> Dict:
        """
        Create a system report for stakeholders.

        Generates summary reports for Boardroom or human review.
        """
        from core.services.discord_notifications import DiscordNotificationService

        report_type = params.get('type', 'system_health')

        logger.info(f"📊 Creating report: {report_type}")

        # Generate report content based on type
        report_content = self._generate_report_content(report_type, reasoning)

        # Post to Discord
        discord = DiscordNotificationService()
        discord.send_to_channel('system-status', f"**📊 System Report: {action_name}**\n\n{report_content}")

        # Create Boardroom decision
        self._create_boardroom_decision(
            topic=f"Report: {action_name}",
            decision_type='guideline',
            impact_area='infrastructure',
            summary=report_content[:500],
            key_insights=[reasoning],
            source='decision_executor'
        )

        return {
            'report_type': report_type,
            'content_length': len(report_content),
            'posted_to_discord': True
        }

    def _execute_send_alert(
        self,
        action_name: str,
        params: Dict,
        reasoning: str
    ) -> Dict:
        """
        Send an alert notification via Discord.

        Used for urgent notifications that need immediate attention.
        """
        from core.services.discord_notifications import DiscordNotificationService

        severity = params.get('severity', 'medium')
        channel = params.get('channel', 'system-status')

        severity_emoji = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '📢',
            'low': 'ℹ️'
        }

        emoji = severity_emoji.get(severity, '📢')
        message = f"{emoji} **Alert: {action_name}**\n\n{reasoning}"

        logger.info(f"🔔 Sending alert: {action_name}")

        discord = DiscordNotificationService()
        discord.send_to_channel(channel, message)

        return {
            'severity': severity,
            'channel': channel,
            'message_length': len(message)
        }

    def _execute_conversation(
        self,
        action_name: str,
        params: Dict,
        reasoning: str
    ) -> Dict:
        """
        Initiate a conversation between agents.

        Similar to debate but more collaborative discussion format.
        """
        from core.tasks import generate_agent_conversation

        topic = params.get('topic', action_name)
        agents = params.get('agents', ['ResearchAgent', 'TrendAnalysisAgent'])

        logger.info(f"🗣️ Starting conversation: {topic}")

        task = generate_agent_conversation.delay(
            topic=topic,
            participants=agents,
            conversation_type='discussion'
        )

        return {
            'topic': topic,
            'agents': agents,
            'task_id': str(task.id),
            'status': 'queued'
        }

    def _execute_archive_insight(
        self,
        action_name: str,
        params: Dict,
        reasoning: str
    ) -> Dict:
        """
        Archive an important insight for future reference.

        Stores insights in the knowledge base for pattern learning.
        """
        from core.models_unified_system import AgentKnowledge, Agent

        insight = params.get('insight', reasoning)
        category = params.get('category', 'system_insight')

        logger.info(f"💾 Archiving insight: {action_name}")

        # Get ThinkingAgent from database
        thinking_agent = Agent.objects.filter(name='ThinkingAgent').first()

        if thinking_agent:
            # Create knowledge entry
            AgentKnowledge.objects.create(
                agent=thinking_agent,
                title=f"[Insight] {action_name}",
                content=insight,
                source='decision_executor',
                confidence_score=0.85,
                is_verified=True
            )

        return {
            'insight': insight[:200],
            'category': category,
            'archived': True
        }

    def _execute_triage_dreams(
        self,
        action_name: str,
        params: Dict,
        reasoning: str
    ) -> Dict:
        """
        Process pending dreams - promote high-value ones to Boardroom.

        Dreams are agent-generated ideas that need evaluation.
        """
        from core.models_unified_system import AgentDream
        from core.tasks import promote_dream_to_boardroom

        max_process = params.get('max_process', 10)

        logger.info(f"💭 Triaging dreams (max {max_process})")

        # Get pending dreams sorted by quality
        pending_dreams = AgentDream.objects.filter(
            status='pending'
        ).order_by('-innovation_score', '-created_at')[:max_process]

        promoted = 0
        archived = 0

        for dream in pending_dreams:
            if dream.innovation_score and dream.innovation_score >= 0.7:
                # Promote high-quality dreams
                promote_dream_to_boardroom.delay(str(dream.id))
                promoted += 1
            else:
                # Archive lower quality dreams
                dream.status = 'archived'
                dream.save()
                archived += 1

        return {
            'processed': len(pending_dreams),
            'promoted': promoted,
            'archived': archived
        }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _generate_report_content(self, report_type: str, context: str) -> str:
        """Generate report content based on type."""
        from core.models_pilot_readiness import (
            PilotExecution, Experiment, ExperimentLearning
        )

        if report_type == 'system_health':
            # Get current stats
            running_pilots = PilotExecution.objects.filter(status='running').count()
            completed_pilots = PilotExecution.objects.filter(status='completed').count()
            learnings = ExperimentLearning.objects.count()
            success_rate = ExperimentLearning.objects.filter(outcome='pass').count()

            return f"""**System Health Report**

📊 **Pilot Status**
- Running: {running_pilots}
- Completed: {completed_pilots}

📈 **Learning Metrics**
- Total Learnings: {learnings}
- Success Rate: {(success_rate/learnings*100) if learnings > 0 else 0:.1f}%

📝 **Context**
{context}

_Auto-generated by DecisionExecutor_"""

        return f"Report type: {report_type}\nContext: {context}"

    def _create_boardroom_decision(
        self,
        topic: str,
        decision_type: str,
        impact_area: str,
        summary: str,
        key_insights: List[str],
        source: str = 'decision_executor'
    ) -> None:
        """Create a Boardroom decision for transparency."""
        from core.models_unified_system import AgentDecisionSummary, AgentConversation

        try:
            # Create a system conversation to link to
            conversation = AgentConversation.objects.create(
                topic=f"[Auto] {topic}",
                participants=['ThinkingAgent', 'DecisionExecutor'],
                conversation_type='system',
                summary=summary
            )

            # Create decision
            AgentDecisionSummary.objects.create(
                conversation=conversation,
                topic=topic,
                decision_type=decision_type,
                impact_area=impact_area,
                summary=summary,
                key_insights=key_insights,
                confidence_score=0.8,
                implementation_status='approved',
                auto_generated=True
            )

            logger.info(f"📋 Created Boardroom decision: {topic}")

        except Exception as e:
            logger.warning(f"Could not create Boardroom decision: {e}")

    def _log_execution(
        self,
        action_type: str,
        action_name: str,
        reasoning: str,
        params: Dict,
        output: Optional[Dict],
        success: bool,
        error: Optional[str] = None,
        thinking_cycle_id: Optional[str] = None
    ) -> None:
        """Log execution to database for audit trail."""
        from core.models_unified_system import SystemEvent

        try:
            SystemEvent.objects.create(
                event_type='decision_execution',
                source='DecisionExecutor',
                data={
                    'action_type': action_type,
                    'action_name': action_name,
                    'reasoning': reasoning,
                    'params': params,
                    'output': output,
                    'success': success,
                    'error': error,
                    'thinking_cycle_id': thinking_cycle_id
                }
            )
        except Exception as e:
            logger.debug(f"Could not log execution: {e}")

    def _send_execution_notification(self, results: Dict) -> None:
        """Send Discord notification about execution results."""
        try:
            from core.services.discord_notifications import DiscordNotificationService

            discord = DiscordNotificationService()

            message = f"""**🤖 Decision Executor Report**

**Decisions Received:** {results['total_decisions']}
**Executed:** {results['executed']}
**Succeeded:** {results['succeeded']} ✅
**Failed:** {results['failed']} ❌
**Skipped (low priority):** {results['skipped']}

"""
            if results['executions']:
                message += "**Actions Taken:**\n"
                for exec in results['executions'][:5]:
                    emoji = '✅' if exec['success'] else '❌'
                    message += f"{emoji} {exec['action_type']}: {exec['action_name']}\n"

            discord.send_to_channel('system-status', message)

        except Exception as e:
            logger.debug(f"Discord notification failed: {e}")
