"""
Autonomous Action Executor - Executes decisions made by the ThinkingAgent

Session 544: This service takes the decisions from the ThinkingAgent and
actually executes them using the appropriate agents and services.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from django.utils import timezone

logger = logging.getLogger(__name__)


class AutonomousActionExecutor:
    """
    Executes autonomous actions decided by the ThinkingAgent.

    Each action type maps to a specific execution method that uses
    existing agents and services to carry out the action.
    """

    def __init__(self):
        self.action_handlers = {
            'spawn_spider': self._execute_spawn_spider,
            'generate_content': self._execute_generate_content,
            'trigger_debate': self._execute_trigger_debate,
            'create_report': self._execute_create_report,
            'send_alert': self._execute_send_alert,
            'request_research': self._execute_request_research,
            'trigger_conversation': self._execute_trigger_conversation,
            'archive_insight': self._execute_archive_insight,
            'update_strategy': self._execute_update_strategy,
            'schedule_followup': self._execute_schedule_followup,
            'triage_dreams': self._execute_triage_dreams,  # Session 564: Dream pipeline
        }

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single autonomous action.

        Args:
            action: Dictionary containing action details from ThinkingAgent

        Returns:
            Dictionary with execution result
        """
        action_type = action.get('action_type', '')
        action_name = action.get('action_name', 'Unnamed Action')
        params = action.get('params', {})

        logger.info(f"Executing autonomous action: {action_type} - {action_name}")

        handler = self.action_handlers.get(action_type)
        if not handler:
            logger.warning(f"Unknown action type: {action_type}")
            return {
                'success': False,
                'error': f"Unknown action type: {action_type}",
                'action_type': action_type,
                'action_name': action_name
            }

        try:
            result = handler(action_name, params, action.get('reasoning', ''))
            return {
                'success': True,
                'action_type': action_type,
                'action_name': action_name,
                'result': result,
                'executed_at': timezone.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {e}")
            return {
                'success': False,
                'error': str(e),
                'action_type': action_type,
                'action_name': action_name
            }

    def execute_actions(self, actions: List[Dict[str, Any]], max_actions: int = 5) -> List[Dict[str, Any]]:
        """
        Execute multiple actions, respecting the max limit.

        Args:
            actions: List of action dictionaries
            max_actions: Maximum number of actions to execute

        Returns:
            List of execution results
        """
        results = []

        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'background': 4}
        sorted_actions = sorted(
            actions,
            key=lambda a: priority_order.get(a.get('priority', 'medium'), 2)
        )

        for action in sorted_actions[:max_actions]:
            result = self.execute_action(action)
            results.append(result)

        return results

    def _execute_spawn_spider(self, name: str, params: Dict, reasoning: str) -> Dict[str, Any]:
        """Spawn a spider to gather data on a specific topic."""
        from core.tasks import execute_single_spider_lightweight

        topic = params.get('topic', 'trending')
        spider_type = params.get('spider_type', 'newsapi')

        # Queue the spider task
        task = execute_single_spider_lightweight.delay(spider_type)

        return {
            'task_id': str(task.id),
            'spider_type': spider_type,
            'topic': topic,
            'message': f"Spawned {spider_type} spider to gather data on: {topic}"
        }

    def _execute_generate_content(self, name: str, params: Dict, reasoning: str) -> Dict[str, Any]:
        """Generate content using the ContentWriterAgent."""
        from core.agents.content_writer_agent import ContentWriterAgent

        topic = params.get('topic', 'system insights')
        content_type = params.get('content_type', 'blog')
        tone = params.get('tone', 'professional')

        agent = ContentWriterAgent()
        # ContentWriterAgent.execute takes: task, context, scifi_context, spider_context
        result = agent.execute(
            task=f"Write a {content_type} about: {topic}. Tone: {tone}. Context: {reasoning}",
            context={'topic': topic, 'content_type': content_type, 'tone': tone, 'autonomous': True},
            scifi_context={},
            spider_context={}
        )

        return {
            'content_type': content_type,
            'topic': topic,
            'generated': result.success if hasattr(result, 'success') else True,
            'preview': str(result.content)[:200] if hasattr(result, 'content') and result.content else 'Content generated'
        }

    def _execute_trigger_debate(self, name: str, params: Dict, reasoning: str) -> Dict[str, Any]:
        """Trigger a boardroom debate between agents."""
        from core.models_unified_system import Agent, AgentKnowledgeSource
        import uuid

        topic = params.get('topic', 'System Strategy')
        participants = params.get('participants', [])

        # If no participants specified, pick relevant agents
        if not participants:
            agents = Agent.objects.filter(is_active=True)[:5]
            participants = [a.name for a in agents]

        # Store debate request as knowledge
        thinking_agent = Agent.objects.filter(name__icontains='thinking').first()
        if not thinking_agent:
            thinking_agent = Agent.objects.first()

        if thinking_agent:
            # Use correct field names for AgentKnowledgeSource
            debate_record = AgentKnowledgeSource.objects.create(
                id=uuid.uuid4(),
                agent=thinking_agent,
                title=f"[Debate Request] {topic}",
                summary=f"Debate requested on: {topic}\nParticipants: {', '.join(participants)}\nReasoning: {reasoning}",
                knowledge_type='opportunity',
                confidence_score=0.8,
                relevance_score=0.9,
                key_insights=[
                    {'type': 'debate_request', 'participants': participants, 'status': 'pending', 'auto_triggered': True}
                ]
            )
            return {
                'debate_id': str(debate_record.id),
                'topic': topic,
                'participants': participants,
                'message': f"Debate scheduled on: {topic}"
            }

        return {
            'success': False,
            'topic': topic,
            'message': 'Could not schedule debate - no agent found'
        }

    def _execute_create_report(self, name: str, params: Dict, reasoning: str) -> Dict[str, Any]:
        """Create a report summarizing insights from the latest thinking cycle."""
        from core.models_unified_system import SelfBlog, ThoughtRecord
        import uuid

        topic = params.get('topic', 'System Insights')

        # Get insights from params OR from the latest thought record
        insights = params.get('insights', [])
        patterns = []
        opportunities = []
        concerns = []
        context_summary = ""

        # If no insights provided, pull from latest thought record
        if not insights:
            latest_thought = ThoughtRecord.objects.order_by('-started_at').first()
            if latest_thought:
                insights = latest_thought.insights or []
                patterns = latest_thought.patterns or []
                opportunities = latest_thought.opportunities or []
                concerns = latest_thought.concerns or []
                context_summary = latest_thought.context_summary or ""

        # Build comprehensive report
        report_content = f"# {topic}\n\n"
        report_content += f"*Auto-generated by ThinkingAgent - Cycle #{latest_thought.cycle_number if latest_thought else '?'}*\n\n"

        if context_summary:
            report_content += f"## Context\n{context_summary}\n\n"

        report_content += f"## Executive Summary\n{reasoning}\n\n"

        # Key Insights
        report_content += "## Key Insights\n"
        if insights:
            for ins in insights:
                if isinstance(ins, dict):
                    cat = ins.get('category', 'insight').upper()
                    conf = ins.get('confidence', 0)
                    text = ins.get('insight', str(ins))
                    report_content += f"- **[{cat}]** ({conf:.0%} confidence): {text}\n"
                else:
                    report_content += f"- {ins}\n"
        else:
            report_content += "- No insights generated this cycle.\n"
        report_content += "\n"

        # Patterns Detected
        if patterns:
            report_content += "## Patterns Detected\n"
            for pat in patterns:
                if isinstance(pat, dict):
                    text = pat.get('pattern', str(pat))
                    evidence = pat.get('evidence', '')
                    report_content += f"- **{text}**\n"
                    if evidence:
                        report_content += f"  - Evidence: {evidence}\n"
                else:
                    report_content += f"- {pat}\n"
            report_content += "\n"

        # Opportunities
        if opportunities:
            report_content += "## Opportunities\n"
            for opp in opportunities:
                if isinstance(opp, dict):
                    text = opp.get('opportunity', str(opp))
                    impact = opp.get('potential_impact', '')
                    report_content += f"- {text}"
                    if impact:
                        report_content += f" *(Impact: {impact})*"
                    report_content += "\n"
                else:
                    report_content += f"- {opp}\n"
            report_content += "\n"

        # Concerns
        if concerns:
            report_content += "## Concerns\n"
            for con in concerns:
                if isinstance(con, dict):
                    text = con.get('concern', str(con))
                    severity = con.get('severity', '')
                    report_content += f"- {text}"
                    if severity:
                        report_content += f" *(Severity: {severity})*"
                    report_content += "\n"
                else:
                    report_content += f"- {con}\n"
            report_content += "\n"

        # Generate intro based on content
        intro = f"This report summarizes the autonomous reasoning cycle's analysis. "
        if concerns:
            high_concerns = [c for c in concerns if isinstance(c, dict) and c.get('severity') == 'high']
            if high_concerns:
                intro += f"**{len(high_concerns)} high-severity concern(s) identified.** "
        if opportunities:
            intro += f"{len(opportunities)} opportunities detected. "
        intro += "Review recommended actions below."

        blog = SelfBlog.objects.create(
            id=uuid.uuid4(),
            title=f"[Report] {topic}",
            intro=intro,
            conclusion="This report was auto-generated by the Autonomous Reasoning Engine. Actions have been queued based on these findings.",
            full_text=report_content,
            tone="analytical",
            stats_snapshot={
                'auto_generated': True,
                'reasoning': reasoning,
                'insights_count': len(insights),
                'patterns_count': len(patterns),
                'opportunities_count': len(opportunities),
                'concerns_count': len(concerns),
            }
        )

        return {
            'report_id': str(blog.id),
            'topic': topic,
            'message': f"Report created: {topic}",
            'insights_count': len(insights),
            'patterns_count': len(patterns)
        }

    def _execute_send_alert(self, name: str, params: Dict, reasoning: str) -> Dict[str, Any]:
        """Send an alert/notification to the user."""
        from core.services.discord_notifications import DiscordNotificationService

        message = params.get('message', 'System alert from ThinkingAgent')
        severity = params.get('severity', 'info')

        # Try Discord notification using send_status method
        try:
            discord = DiscordNotificationService()
            discord.send_status(
                title=f"[{severity.upper()}] {name}",
                message=f"{message}\n\nReasoning: {reasoning}",
                status_type='info' if severity == 'info' else 'warning'
            )
            sent_via = 'discord'
        except Exception as e:
            logger.warning(f"Could not send Discord alert: {e}")
            sent_via = 'logged'

        return {
            'message': message,
            'severity': severity,
            'sent_via': sent_via,
            'notification': f"Alert sent: {name}"
        }

    def _execute_request_research(self, name: str, params: Dict, reasoning: str) -> Dict[str, Any]:
        """Request deep research on a topic."""
        from core.agents.research_agent import ResearchAgent

        topic = params.get('topic', 'emerging trends')
        depth = params.get('depth', 'standard')

        agent = ResearchAgent()
        # ResearchAgent.execute takes: task, context, scifi_context, spider_context
        result = agent.execute(
            task=f"Research topic: {topic}. Depth: {depth}. Context: {reasoning}",
            context={'topic': topic, 'depth': depth, 'autonomous': True},
            scifi_context={},
            spider_context={}
        )

        return {
            'topic': topic,
            'depth': depth,
            'research_complete': result.success if hasattr(result, 'success') else False,
            'findings_preview': str(result.content)[:300] if hasattr(result, 'content') and result.content else 'Research initiated'
        }

    def _execute_trigger_conversation(self, name: str, params: Dict, reasoning: str) -> Dict[str, Any]:
        """Trigger a conversation between specific agents."""
        from core.models_unified_system import Agent, AgentConversation
        import uuid

        topic = params.get('topic', 'Cross-domain insights')
        agent_names = params.get('agents', [])

        # Find the agents
        if len(agent_names) >= 2:
            initiator = Agent.objects.filter(name__icontains=agent_names[0]).first()
            other_agent = Agent.objects.filter(name__icontains=agent_names[1]).first()
        else:
            # Pick two random active agents
            agents = list(Agent.objects.filter(is_active=True)[:2])
            initiator = agents[0] if agents else None
            other_agent = agents[1] if len(agents) > 1 else None

        if not initiator or not other_agent:
            return {
                'success': False,
                'message': 'Could not find suitable agents for conversation'
            }

        # Create conversation record using correct AgentConversation fields
        conversation = AgentConversation.objects.create(
            id=uuid.uuid4(),
            initiator=initiator,
            topic=f"[Auto] {topic}",
            conversation_type='knowledge_sharing',
            trigger_type='scheduled',  # Changed from trigger_context
        )
        # Add participants via ManyToMany
        conversation.participants.add(initiator, other_agent)

        return {
            'conversation_id': str(conversation.id),
            'initiator': initiator.name,
            'other_agent': other_agent.name,
            'topic': topic,
            'message': f"Conversation initiated between {initiator.name} and {other_agent.name}"
        }

    def _execute_archive_insight(self, name: str, params: Dict, reasoning: str) -> Dict[str, Any]:
        """Archive an important insight for future reference."""
        from core.models_unified_system import AgentKnowledgeSource, Agent
        import uuid

        insight = params.get('insight', '')
        category = params.get('category', 'autonomous_insight')
        importance = params.get('importance', 'high')

        # Find the ThinkingAgent record or create synthetic one
        thinking_agent = Agent.objects.filter(name__icontains='thinking').first()
        if not thinking_agent:
            thinking_agent = Agent.objects.first()

        if thinking_agent and insight:
            # Use correct field names for AgentKnowledgeSource
            knowledge = AgentKnowledgeSource.objects.create(
                id=uuid.uuid4(),
                agent=thinking_agent,
                title=f"[Insight] {name}",
                summary=insight,
                knowledge_type='opportunity',  # Map insight to opportunity type
                confidence_score=0.8 if importance == 'high' else 0.5,
                relevance_score=0.9 if importance == 'high' else 0.6,
                key_insights=[
                    {'category': category, 'reasoning': reasoning, 'auto_archived': True}
                ]
            )

            return {
                'knowledge_id': str(knowledge.id),
                'insight': insight[:100],
                'category': category,
                'message': 'Insight archived successfully'
            }

        return {
            'success': False,
            'message': 'Could not archive insight - missing data'
        }

    def _execute_update_strategy(self, name: str, params: Dict, reasoning: str) -> Dict[str, Any]:
        """Update system strategy based on insights."""
        from core.models_unified_system import ReasoningConfiguration

        strategy_area = params.get('area', 'general')
        adjustment = params.get('adjustment', '')

        # Log the strategy update (could be expanded to actually modify config)
        logger.info(f"Strategy update requested for {strategy_area}: {adjustment}")

        return {
            'area': strategy_area,
            'adjustment': adjustment,
            'message': f"Strategy consideration logged for: {strategy_area}",
            'note': 'Full strategy updates require human approval'
        }

    def _execute_schedule_followup(self, name: str, params: Dict, reasoning: str) -> Dict[str, Any]:
        """Schedule a follow-up thinking cycle on a specific topic."""
        from django.core.cache import cache

        topic = params.get('topic', '')
        delay_hours = params.get('delay_hours', 24)

        # Store in cache for next thinking cycle to pick up
        cache_key = f"thinking_followup_{topic.replace(' ', '_')}"
        cache.set(cache_key, {
            'topic': topic,
            'reasoning': reasoning,
            'scheduled_at': timezone.now().isoformat(),
            'due_after_hours': delay_hours
        }, timeout=delay_hours * 3600)

        return {
            'topic': topic,
            'delay_hours': delay_hours,
            'message': f"Follow-up scheduled on '{topic}' in {delay_hours} hours"
        }

    def _execute_triage_dreams(self, name: str, params: Dict, reasoning: str) -> Dict[str, Any]:
        """
        Session 564: Autonomous Dream Triage Pipeline

        Evaluates pending dreams and routes them:
        - HIGH VALUE (composite >= 0.65, actionability >= 0.6) -> Boardroom
        - INSPIRATION (composite >= 0.5, actionability < 0.5) -> Mark as shown
        - STALE LOW (older than 14 days, composite < 0.4) -> Archive
        """
        from core.models_unified_system import AgentDream
        from datetime import timedelta

        # Get thresholds from params or use defaults
        boardroom_threshold = params.get('boardroom_threshold', 0.65)
        boardroom_action_threshold = params.get('boardroom_action_threshold', 0.6)
        inspiration_threshold = params.get('inspiration_threshold', 0.5)
        archive_age_days = params.get('archive_age_days', 14)
        archive_score_threshold = params.get('archive_score_threshold', 0.4)
        max_to_process = params.get('max_to_process', 50)

        now = timezone.now()
        results = {
            'promoted_to_boardroom': [],
            'marked_as_inspiration': [],
            'archived': [],
            'skipped': 0
        }

        # Get all pending dreams
        pending = AgentDream.objects.filter(
            promoted_to_decision=False,
            shown_to_user=False
        ).select_related('agent').order_by('-composite_score')[:max_to_process]

        for dream in pending:
            age_days = (now - dream.dreamed_at).days

            # Route 1: HIGH VALUE -> Boardroom
            if (dream.composite_score >= boardroom_threshold and
                dream.actionability_score >= boardroom_action_threshold):
                dream.promoted_to_decision = True
                dream.promoted_at = now
                dream.save()
                results['promoted_to_boardroom'].append({
                    'id': str(dream.id),
                    'title': dream.title[:50],
                    'score': dream.composite_score,
                    'agent': dream.agent.name if dream.agent else 'Unknown'
                })

            # Route 2: STALE LOW -> Archive (mark as shown)
            elif age_days >= archive_age_days and dream.composite_score < archive_score_threshold:
                dream.shown_to_user = True
                dream.shown_at = now
                dream.user_feedback = 'auto_archived_stale'
                dream.save()
                results['archived'].append({
                    'id': str(dream.id),
                    'title': dream.title[:50],
                    'age_days': age_days,
                    'score': dream.composite_score
                })

            # Route 3: INSPIRATION (creative but not actionable)
            elif (dream.composite_score >= inspiration_threshold and
                  dream.actionability_score < boardroom_action_threshold):
                dream.shown_to_user = True
                dream.shown_at = now
                dream.user_feedback = 'inspiration_archive'
                dream.save()
                results['marked_as_inspiration'].append({
                    'id': str(dream.id),
                    'title': dream.title[:50],
                    'score': dream.composite_score,
                    'creativity': dream.creativity_score
                })
            else:
                results['skipped'] += 1

        # Summary
        total_processed = (
            len(results['promoted_to_boardroom']) +
            len(results['marked_as_inspiration']) +
            len(results['archived'])
        )

        logger.info(
            f"Dream triage complete: {len(results['promoted_to_boardroom'])} to boardroom, "
            f"{len(results['marked_as_inspiration'])} to inspiration, "
            f"{len(results['archived'])} archived, {results['skipped']} skipped"
        )

        return {
            'total_processed': total_processed,
            'promoted_to_boardroom': len(results['promoted_to_boardroom']),
            'marked_as_inspiration': len(results['marked_as_inspiration']),
            'archived': len(results['archived']),
            'skipped': results['skipped'],
            'details': results,
            'message': f"Triaged {total_processed} dreams: {len(results['promoted_to_boardroom'])} to Boardroom"
        }

    def register_concerns_from_thought(self, thought_record) -> Dict[str, Any]:
        """
        Register all concerns from a thinking cycle for tracking.

        Args:
            thought_record: The ThoughtRecord containing concerns

        Returns:
            Summary of registered concerns
        """
        from core.services.concern_tracker import get_concern_tracker

        tracker = get_concern_tracker()
        registered = tracker.register_concerns_from_cycle(thought_record)

        return {
            'total_concerns': len(registered),
            'new_concerns': sum(1 for r in registered if r.get('is_new')),
            'recurring_concerns': sum(1 for r in registered if not r.get('is_new')),
            'concerns': [
                {
                    'text': r['concern'].concern_text[:50],
                    'status': r['status'],
                    'is_new': r['is_new']
                }
                for r in registered
            ]
        }

    def link_action_to_concerns(self, action) -> Dict[str, Any]:
        """
        Link an executed action to concerns it might address.

        Args:
            action: The AutonomousAction that was executed

        Returns:
            Summary of linked concerns
        """
        from core.services.concern_tracker import get_concern_tracker

        tracker = get_concern_tracker()
        linked = tracker.link_action_to_concerns(action)

        return {
            'linked_count': len(linked),
            'concerns': [
                {
                    'id': str(c.id),
                    'text': c.concern_text[:50],
                    'status': c.status
                }
                for c in linked
            ]
        }

    def verify_concerns(self) -> Dict[str, Any]:
        """
        Run verification on all active concerns.

        Returns:
            Verification summary
        """
        from core.services.concern_tracker import get_concern_tracker

        tracker = get_concern_tracker()
        return tracker.verify_all_active_concerns()

    def get_concern_dashboard(self) -> Dict[str, Any]:
        """
        Get concern tracking dashboard data.

        Returns:
            Dashboard data for UI
        """
        from core.services.concern_tracker import get_concern_tracker

        tracker = get_concern_tracker()
        return tracker.get_concern_dashboard()
