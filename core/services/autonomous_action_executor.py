"""
Autonomous Action Executor - Executes decisions made by the ThinkingAgent

Session 544: This service takes the decisions from the ThinkingAgent and
actually executes them using the appropriate agents and services.

Session 804: Added _create_blog_attention_item() to surface auto-generated
blogs in the Human Interface. Previously, blogs were created but not visible
because HumanAttentionItem entries weren't being created.

Session 847: Added Initiative integration - every action now links to an
Initiative (5-stage project pipeline). This creates the "project spine"
that organizes floating documents into coherent workflows.
ChatGPT feedback: "You're missing the middle. ThinkingAgent -> Initiative -> Stages -> Documents"
"""

import logging
from typing import Dict, List, Any
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
            'auto_approve_gates': self._execute_auto_approve_gates,  # Session 654: Auto-approve low-risk gates
            'promote_initiative_stage': self._execute_promote_initiative_stage,  # Session 847: Initiative pipeline
            'review_initiatives': self._execute_review_initiatives,  # Session 847: Initiative health check
        }

    def _create_blog_attention_item(
        self,
        blog,
        content_type: str = 'report',
        agent_name: str = 'ThinkingAgent'
    ) -> bool:
        """
        Session 804: Create HumanAttentionItem for auto-generated SelfBlog entries.

        This ensures all auto-generated blogs surface in the Human Interface
        for review, just like blogs created by generate_self_blog_task.

        Args:
            blog: The SelfBlog instance that was created
            content_type: Type of content (report, research, deliverable)
            agent_name: Name of the agent that created it

        Returns:
            True if attention item was created, False otherwise
        """
        try:
            from core.services.human_attention_bridge import HumanAttentionBridge

            bridge = HumanAttentionBridge()

            # Build summary from blog intro or title
            summary = blog.intro[:200] if blog.intro else f"Auto-generated {content_type}: {blog.title}"

            bridge.create_content_review_attention(
                content_type=content_type,
                title=blog.title,
                summary=summary,
                content_id=str(blog.id),
                agent_name=agent_name,
                quality_score=75,  # Default score for auto-generated content
            )

            logger.info(f"📋 [Session 804] Created attention item for blog {blog.id}")
            return True

        except Exception as e:
            logger.warning(f"📋 [Session 804] Failed to create attention item for blog {blog.id}: {e}")
            return False

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single autonomous action.

        Session 847: Now integrates with Initiative pipeline - every action
        is linked to an Initiative for structured project tracking.

        Args:
            action: Dictionary containing action details from ThinkingAgent

        Returns:
            Dictionary with execution result
        """
        action_type = action.get('action_type', '')
        action_name = action.get('action_name', 'Unnamed Action')
        params = action.get('params', {})
        reasoning = action.get('reasoning', '')

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
            result = handler(action_name, params, reasoning)

            # Session 847: Link action to Initiative pipeline
            initiative_id = None
            try:
                initiative = self._link_to_initiative(action_type, action_name, params, reasoning, result)
                if initiative:
                    initiative_id = str(initiative.id)
                    logger.info(f"[Session 847] Linked action to Initiative: {initiative.name}")
            except Exception as init_err:
                logger.warning(f"[Session 847] Initiative linking failed (non-fatal): {init_err}")

            return {
                'success': True,
                'action_type': action_type,
                'action_name': action_name,
                'result': result,
                'initiative_id': initiative_id,  # Session 847: Track linked initiative
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

    def _link_to_initiative(
        self,
        action_type: str,
        action_name: str,
        params: Dict[str, Any],
        reasoning: str,
        result: Dict[str, Any]
    ):
        """
        Session 847: Link an executed action to the Initiative pipeline.

        This creates the "project spine" that connects:
        ThinkingAgent -> Initiative -> Stages -> Documents -> Actions

        Args:
            action_type: The type of action executed
            action_name: Human-readable action name
            params: Action parameters
            reasoning: Why this action was taken
            result: Execution result

        Returns:
            The Initiative that was linked/created, or None
        """
        from core.services.initiative_integration_service import get_initiative_integration_service

        # Skip actions that don't produce artifacts
        skip_actions = ['send_alert', 'update_strategy', 'schedule_followup']
        if action_type in skip_actions:
            return None

        service = get_initiative_integration_service()

        # Merge action_name into params if no topic
        merged_params = {**params}
        if 'topic' not in merged_params:
            merged_params['topic'] = action_name

        return service.link_action_to_initiative(
            action_type=action_type,
            action_params=merged_params,
            reasoning=reasoning,
            result=result
        )

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
        from core.services.spider_context_builder import SpiderContextBuilder

        topic = params.get('topic', 'system insights')
        content_type = params.get('content_type', 'blog')
        tone = params.get('tone', 'professional')

        # Session 936: Build real spider context instead of empty dict
        # This was the root cause of blogs only referencing "Kalshi spider"
        spider_context = {}
        try:
            context_builder = SpiderContextBuilder()
            spider_context = context_builder.build_context_for_agent(
                agent_name='ContentWriterAgent',
                task=f"{content_type} about {topic}",
                hours=48,
                max_trends=15,
                max_discussions=10,
                include_market_data=True
            )
            logger.info(f"[Session 936] Built spider context with {len(spider_context.get('data_sources', []))} data sources for content: {topic}")
        except Exception as e:
            logger.warning(f"[Session 936] Could not build spider context: {e}")

        agent = ContentWriterAgent()
        # ContentWriterAgent.execute takes: task, context, scifi_context, spider_context
        result = agent.execute(
            task=f"Write a {content_type} about: {topic}. Tone: {tone}. Context: {reasoning}",
            context={'topic': topic, 'content_type': content_type, 'tone': tone, 'autonomous': True},
            scifi_context={},
            spider_context=spider_context
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

        # Session 852: Set category='audit' so reports don't appear as blogs
        # Session 860: Added parent_topic for Initiative linking
        blog = SelfBlog.objects.create(
            id=uuid.uuid4(),
            title=f"[Report] {topic}",
            category='audit',  # Session 852: Use audit category for system reports
            intro=intro,
            conclusion="This report was auto-generated by the Autonomous Reasoning Engine. Actions have been queued based on these findings.",
            full_text=report_content,
            tone="analytical",
            stats_snapshot={
                'auto_generated': True,
                'parent_topic': topic,  # Session 860: Required for Initiative linking
                'reasoning': reasoning,
                'insights_count': len(insights),
                'patterns_count': len(patterns),
                'opportunities_count': len(opportunities),
                'concerns_count': len(concerns),
            }
        )

        # Session 804: Create attention item so report surfaces in Human Interface
        self._create_blog_attention_item(blog, content_type='report', agent_name='ThinkingAgent')

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
        """
        Request deep research on a topic with optional deliverable synthesis.

        Session 620: Fixed to properly use action name as topic and include deliverables.
        Session 620.1: Added synthesis phase - chains to ContentWriterAgent to create deliverables.

        Args:
            name: The action name (used as research topic if no topic in params)
            params: May include:
                - topic: Research topic (defaults to action name)
                - depth: Research depth (default: comprehensive)
                - deliverables: List of documents to create
                - synthesize_deliverables: Whether to create deliverable docs (default: True)
                - owner_agent: Agent responsible (default: ResearchAgent)
                - deadline_hours: Deadline for completion (default: 72)
            reasoning: Context for why this research was requested
        """
        from core.agents.research_agent import ResearchAgent
        from core.models_unified_system import SelfBlog
        import uuid

        # Session 620: Use action name as topic if no explicit topic in params
        topic = params.get('topic') or name
        depth = params.get('depth', 'comprehensive')
        deliverables = params.get('deliverables', [])

        # Session 893: Fix LLM output bug - ensure deliverables is always a list
        # ThinkingAgent's LLM sometimes outputs "deliverables": "filename" instead of ["filename"]
        # This caused character-by-character iteration creating docs with single-letter titles
        if isinstance(deliverables, str):
            deliverables = [deliverables] if deliverables else []
            logger.warning(f"[Session 893] Converted deliverables string to list: {deliverables}")

        synthesize_deliverables = params.get('synthesize_deliverables', True)  # Session 620.1
        owner_agent = params.get('owner_agent', 'ResearchAgent')
        deadline_hours = params.get('deadline_hours', 72)

        # Session 866: Inject internal data source context
        # This teaches the agent about available DonkeyBetz data sources
        from core.services.internal_data_registry import (
            build_agent_data_context,
            get_data_source_for_topic
        )

        # Check if this topic has internal data sources
        internal_sources = get_data_source_for_topic(topic)
        internal_data_context = ""
        if internal_sources:
            internal_data_context = build_agent_data_context(topic, max_sources=3)
            logger.info(f"[Session 866] Found {len(internal_sources)} internal data sources for topic: {topic}")

        # Build comprehensive research task including deliverables
        task_parts = [f"Research topic: {topic}"]
        task_parts.append(f"Depth: {depth}")

        if deliverables:
            task_parts.append("\nRequired deliverables:")
            for i, deliverable in enumerate(deliverables, 1):
                task_parts.append(f"  {i}. {deliverable}")

        if reasoning:
            task_parts.append(f"\nContext: {reasoning}")

        # Session 866: Add internal data context to task
        if internal_data_context:
            task_parts.append("\n" + internal_data_context)
            task_parts.append("\n**IMPORTANT:** Query the internal DonkeyBetz data sources above.")
            task_parts.append("Do NOT request BigQuery, Snowflake, or external database access.")

        full_task = "\n".join(task_parts)

        logger.info(f"Executing research request: {topic}")
        logger.info(f"Deliverables requested: {deliverables}")
        logger.info(f"Synthesize deliverables: {synthesize_deliverables}")

        agent = ResearchAgent()
        # ResearchAgent.execute takes: task, context, scifi_context, spider_context
        result = agent.execute(
            task=full_task,
            context={
                'topic': topic,
                'depth': depth,
                'autonomous': True,
                'deliverables': deliverables,
                'owner_agent': owner_agent,
                'deadline_hours': deadline_hours
            },
            scifi_context={},
            spider_context={}
        )

        # Extract findings from result
        findings = ""
        findings_detailed = []  # Session 620.1: More detailed findings for synthesis
        research_data = {}

        if hasattr(result, 'data') and result.data:
            research_data = result.data
            # Try to extract meaningful content from results
            if isinstance(result.data, dict):
                results_list = result.data.get('results', [])
                if results_list:
                    finding_parts = []
                    for r in results_list[:5]:  # Top 5 results
                        source = r.get('source', 'unknown')
                        data = r.get('data', {})
                        if isinstance(data, dict):
                            # Extract key info from each source
                            items = data.get('results', data.get('discussions', data.get('topics', [])))
                            if items and isinstance(items, list):
                                for item in items[:3]:
                                    if isinstance(item, dict):
                                        title = item.get('title', item.get('name', ''))
                                        snippet = item.get('snippet', item.get('description', item.get('selftext', '')))
                                        link = item.get('link', item.get('url', ''))
                                        if title:
                                            finding_parts.append(f"- [{source}] {title}")
                                            # Session 620.1: Store detailed findings for synthesis
                                            findings_detailed.append({
                                                'source': source,
                                                'title': title,
                                                'snippet': snippet[:500] if snippet else '',
                                                'link': link
                                            })
                    findings = "\n".join(finding_parts[:10]) if finding_parts else "Research completed, data gathered"

        if hasattr(result, 'message') and result.message:
            if not findings:
                findings = result.message

        if hasattr(result, 'content') and result.content:
            if not findings:
                findings = str(result.content)[:500]

        research_successful = result.success if hasattr(result, 'success') else False

        # Session 620.1: Debug logging for research result
        logger.info(f"Research result - hasattr success: {hasattr(result, 'success')}, success value: {result.success if hasattr(result, 'success') else 'N/A'}, research_successful: {research_successful}")

        # Session 866: Self-unblocking pattern - if research failed or data insufficient, try to unblock
        # Session 905: Enhanced to create ResearchResult record and schedule retry task
        unblock_result = None
        research_result_record = None
        data_insufficient = not findings or len(findings) < 50
        if not research_successful or data_insufficient:
            logger.warning(f"[Session 866] Research may need unblocking - success: {research_successful}, findings length: {len(findings) if findings else 0}")
            try:
                unblock_result = self._trigger_self_unblock(
                    topic=topic,
                    missing_data_type='spider' if data_insufficient else 'general'
                )
                logger.info(f"[Session 866] Self-unblock triggered: {unblock_result.get('unblock_type')}")

                # Session 905: Create ResearchResult record to track blocked state
                research_result_record = self._create_blocked_research_result(
                    topic=topic,
                    reasoning=reasoning,
                    findings=findings,
                    findings_detailed=findings_detailed,
                    owner_agent=owner_agent,
                    unblock_result=unblock_result
                )
                if research_result_record:
                    logger.info(f"[Session 905] Created blocked ResearchResult: {research_result_record.id}")

            except Exception as unblock_error:
                logger.warning(f"[Session 866] Self-unblock failed: {unblock_error}")

        # Session 620: Create a SelfBlog entry to persist research findings
        # Session 866: ChatGPT feedback - 3 fixes:
        #   1. Deliverables mismatch - only show section when deliverables exist
        #   2. Decision Gate - add actionable outputs at end
        #   3. System Bindings - map to actual DonkeyBetz tables
        research_blog_id = None
        if research_successful:
            try:
                # Session 866: Build deliverables section only if deliverables exist
                deliverables_section = ""
                if deliverables:
                    deliverables_section = f"""
## Deliverables Requested
{chr(10).join(f'- {d}' for d in deliverables)}
"""

                # Session 866: Extract actual system bindings from findings
                system_bindings = self._extract_system_bindings(findings, topic)
                bindings_section = ""
                if system_bindings:
                    bindings_section = f"""
## System Bindings (DonkeyBetz Integration)
{chr(10).join(f'- **{k}**: `{v}`' for k, v in system_bindings.items())}
"""

                # Session 866: Build decision gate with actionable outputs
                decision_gate = self._build_decision_gate(
                    topic=topic,
                    findings=findings,
                    deliverables=deliverables,
                    owner_agent=owner_agent
                )

                research_report = f"""# Research Report: {topic}

## Request Context
{reasoning}
{deliverables_section}
## Research Findings
{findings if findings else 'Research completed - see data below'}

## Data Sources Consulted
{', '.join(r.get('source', 'unknown') for r in research_data.get('results', [])) if isinstance(research_data, dict) else 'Multiple sources'}
{bindings_section}
{decision_gate}
---
*Auto-generated research report from ThinkingAgent autonomous action*
"""

                # Session 852: Set category='research_brief' so research doesn't appear as blogs
                # Session 860: Added parent_topic for Initiative linking
                blog = SelfBlog.objects.create(
                    id=uuid.uuid4(),
                    title=f"[Research] {topic[:100]}",
                    category='research_brief',  # Session 852: Use research_brief category
                    intro=f"Autonomous research on: {topic}. Deliverables: {len(deliverables)}",
                    conclusion="Research findings saved for review. Execute follow-up actions as needed.",
                    full_text=research_report,
                    tone="analytical",
                    stats_snapshot={
                        'auto_generated': True,
                        'parent_topic': topic,  # Session 860: Required for Initiative linking
                        'action_type': 'request_research',
                        'deliverables': deliverables,
                        'owner_agent': owner_agent,
                        'reasoning': reasoning[:200] if reasoning else '',
                    }
                )
                research_blog_id = str(blog.id)
                logger.info(f"Research report saved: {blog.id}")

                # Session 804: Create attention item so research surfaces in Human Interface
                self._create_blog_attention_item(blog, content_type='research', agent_name='ResearchAgent')

            except Exception as e:
                logger.warning(f"Could not save research report: {e}")

        # =========================================================
        # Session 620.1: SYNTHESIS PHASE - Create actual deliverables
        # =========================================================
        synthesized_deliverables = []

        if synthesize_deliverables and deliverables and research_successful:
            # Session 893: Double-check deliverables is a list before iteration
            if isinstance(deliverables, str):
                deliverables = [deliverables] if deliverables else []
                logger.warning(f"[Session 893] Synthesis phase - converted string to list: {deliverables}")

            logger.info(f"Starting synthesis phase for {len(deliverables)} deliverables")

            from core.agents.content_writer_agent import ContentWriterAgent
            content_writer = ContentWriterAgent()

            # Build research context for the content writer
            research_context = self._build_research_context(
                topic=topic,
                reasoning=reasoning,
                findings=findings,
                findings_detailed=findings_detailed
            )

            for i, deliverable in enumerate(deliverables, 1):
                logger.info(f"Synthesizing deliverable {i}/{len(deliverables)}: {deliverable}")

                try:
                    # Create the deliverable using ContentWriterAgent
                    deliverable_result = self._synthesize_single_deliverable(
                        content_writer=content_writer,
                        deliverable_name=deliverable,
                        topic=topic,
                        research_context=research_context,
                        reasoning=reasoning
                    )

                    if deliverable_result.get('success'):
                        synthesized_deliverables.append(deliverable_result)
                        logger.info(f"Successfully synthesized: {deliverable}")
                    else:
                        logger.warning(f"Failed to synthesize: {deliverable} - {deliverable_result.get('error')}")
                        synthesized_deliverables.append({
                            'deliverable': deliverable,
                            'success': False,
                            'error': deliverable_result.get('error', 'Unknown error')
                        })

                except Exception as e:
                    logger.error(f"Error synthesizing deliverable '{deliverable}': {e}")
                    synthesized_deliverables.append({
                        'deliverable': deliverable,
                        'success': False,
                        'error': str(e)
                    })

            logger.info(f"Synthesis complete: {sum(1 for d in synthesized_deliverables if d.get('success'))}/{len(deliverables)} successful")

        return {
            'topic': topic,
            'depth': depth,
            'deliverables_requested': deliverables,
            'research_complete': research_successful,
            'findings_preview': findings[:500] if findings else 'Research initiated',
            'sources_used': [r.get('source') for r in research_data.get('results', [])] if isinstance(research_data, dict) else [],
            'owner_agent': owner_agent,
            'deadline_hours': deadline_hours,
            'research_blog_id': research_blog_id,
            # Session 620.1: Synthesis results
            'synthesize_deliverables': synthesize_deliverables,
            'synthesized_count': len(synthesized_deliverables),
            'synthesized_success': sum(1 for d in synthesized_deliverables if d.get('success')),
            'synthesized_deliverables': synthesized_deliverables,
            # Session 866: Self-unblock result
            'self_unblock_triggered': unblock_result is not None,
            'self_unblock_result': unblock_result,
        }

    def _build_research_context(self, topic: str, reasoning: str, findings: str, findings_detailed: List[Dict]) -> str:
        """
        Session 620.1: Build a comprehensive research context for content synthesis.

        Formats research findings into a context string that ContentWriterAgent can use
        to create informed deliverables.
        """
        context_parts = [
            f"# Research Context: {topic}",
            "",
            "## Background",
            reasoning if reasoning else "No specific background provided.",
            "",
            "## Key Research Findings",
            findings if findings else "General research completed.",
            "",
        ]

        if findings_detailed:
            context_parts.append("## Detailed Sources")
            for finding in findings_detailed[:10]:  # Top 10 detailed findings
                context_parts.append(f"\n### {finding.get('title', 'Untitled')}")
                context_parts.append(f"**Source:** {finding.get('source', 'Unknown')}")
                if finding.get('snippet'):
                    context_parts.append(f"**Summary:** {finding['snippet']}")
                if finding.get('link'):
                    context_parts.append(f"**Reference:** {finding['link']}")

        return "\n".join(context_parts)

    def _extract_system_bindings(self, findings: str, topic: str) -> Dict[str, str]:
        """
        Session 866: Extract system bindings from research findings.
        ChatGPT Feedback Fix #3: Map generic database references to actual DonkeyBetz tables.

        Instead of generic mentions like "BigQuery" or "Snowflake", map to our actual
        database models for actionable integration.

        Enhanced: Now uses internal_data_registry for more specific mappings.
        """
        # Map of generic external terms to actual DonkeyBetz models/tables
        EXTERNAL_TO_INTERNAL_MAP = {
            # External DB references -> Internal
            'bigquery': 'Use: SpiderData, BusinessResearchResult (direct Django ORM)',
            'snowflake': 'Use: SpiderData, ContentMetrics (direct Django ORM)',
            'redshift': 'Use: SpiderData, AgentExecution (direct Django ORM)',
            'data warehouse': 'Use: SpiderData + ResearchResult + ContentMetrics',
            'csv export': 'Use: Django ORM queryset, export via management command',
            'parquet': 'Use: Django ORM queryset with pandas DataFrame export',

            # Generic terms -> Specific internal models
            'database': 'PostgreSQL + pgvector via Django ORM',
            'analytics': 'core.services.analytics_service + ContentMetrics model',
            'experiment data': 'Experiment model (status: running/success/failure/partial/inconclusive)',
            'experiment': 'Experiment model (core.models.Experiment)',
            'halt': 'Experiment.objects.filter(is_halted=True)',
            'failed': 'Experiment.objects.filter(status="failure") or AgentExecution.objects.filter(status="failed")',

            # Content
            'content': 'SelfBlog / Deliverable models',
            'blog': 'SelfBlog.objects.filter(category="blog")',
            'research report': 'SelfBlog.objects.filter(category="research_brief")',
            'document': 'Deliverable model',

            # Spider data
            'spider': 'SpiderData model (77 spiders available)',
            'crawl': 'SpiderData model',
            'scrape': 'ai_core.spiders (Scrapy framework)',
            'external data': 'SpiderData model',

            # Agent system
            'agent': 'AgentExecution model + core.agents/',
            'execution': 'AgentExecution model',
            'workflow': 'Initiative model (5-stage pipeline)',
            'pipeline': 'Initiative + ConceptForgeRun models',

            # Learning
            'ml': 'ml/ models + AgentModelRouter',
            'learning': 'AgentLearning model',
            'feedback': 'DecisionRecord, ToolCallRecord models',

            # User data
            'user': 'User + ExtendedUserProfile models',
            'customer': 'BusinessResearchResult (research_type="customer")',
        }

        bindings = {}
        findings_lower = (findings or '').lower()
        topic_lower = (topic or '').lower()
        combined_text = f"{findings_lower} {topic_lower}"

        # Check for matches in findings and topic
        for generic_term, donkey_binding in EXTERNAL_TO_INTERNAL_MAP.items():
            if generic_term in combined_text:
                bindings[generic_term.title()] = donkey_binding

        # Also check internal_data_registry for more specific matches
        try:
            from core.services.internal_data_registry import get_data_source_for_topic
            internal_sources = get_data_source_for_topic(topic)
            for source in internal_sources[:3]:  # Top 3 matches
                source_name = source.get('name', '')
                source_model = source.get('model', '')
                if source_name and source_model:
                    bindings[f"[Internal] {source_name}"] = source_model
        except Exception as e:
            logger.warning(f"Could not load internal data registry: {e}")

        return bindings

    def _build_decision_gate(
        self,
        topic: str,
        findings: str,
        deliverables: List[str],
        owner_agent: str
    ) -> str:
        """
        Session 866: Build Decision Gate section for research reports.
        ChatGPT Feedback: Add actionable outputs at the end of research reports.

        The Decision Gate provides:
        1. Summary verdict on research quality
        2. Recommended next actions
        3. Assigned ownership
        4. Data availability status
        """
        # Determine data availability
        data_available = bool(findings and len(findings) > 50)
        data_status = "✅ Data Available" if data_available else "⚠️ Insufficient Data - DataExportAgent may be needed"

        # Build recommended actions based on deliverables
        next_actions = []
        if deliverables:
            next_actions.append(f"✅ Synthesize {len(deliverables)} requested deliverable(s)")
        else:
            next_actions.append("📋 Define specific deliverables for this research")

        if data_available:
            next_actions.append("📊 Review findings and validate key insights")
            next_actions.append("🎯 Route to appropriate agent for content creation")
        else:
            next_actions.append("🔄 Trigger additional data collection (DataExportAgent)")
            next_actions.append("🕷️ Consider spawning focused spiders for this topic")

        next_actions.append(f"👤 Assign to {owner_agent} for follow-up")

        # Build the decision gate section
        decision_gate = f"""
## Decision Gate

### Data Status
{data_status}

### Recommended Actions
{chr(10).join(f'{i}. {action}' for i, action in enumerate(next_actions, 1))}

### Ownership
**Primary Owner:** {owner_agent}
**Status:** Pending Review
"""

        return decision_gate

    def _trigger_self_unblock(
        self,
        topic: str,
        missing_data_type: str = 'general'
    ) -> Dict[str, Any]:
        """
        Session 866: Self-unblocking pattern.
        ChatGPT Feedback Fix #2: Auto-spawn DataExportAgent when data is unavailable.

        When research cannot proceed due to missing data, this method
        automatically triggers data collection to unblock the pipeline.
        """
        logger.info(f"[Session 866] Self-unblock triggered for topic: {topic}, missing: {missing_data_type}")

        try:
            # Determine which agent to spawn based on missing data type
            if missing_data_type in ['spider', 'web', 'external']:
                # Spawn spider for external data
                spawn_result = self._execute_spawn_spider(
                    name=f"Data collection for: {topic[:50]}",
                    params={
                        'topic': topic,
                        'categories': ['tech', 'news', 'content'],
                        'reason': 'Self-unblock: Research blocked on missing data'
                    },
                    reasoning=f"Auto-spawned to unblock research on: {topic}"
                )
                return {
                    'unblock_type': 'spawn_spider',
                    'result': spawn_result,
                    'message': f"Spawned spider to collect data for: {topic}"
                }

            elif missing_data_type in ['internal', 'database', 'export']:
                # Trigger internal data aggregation via spider refresh
                try:
                    from core.services.unified_intelligence_search import get_unified_intelligence_search
                    search_service = get_unified_intelligence_search()
                    refresh_result = search_service.refresh_spiders_for_query(
                        query=topic,
                        categories=['tech', 'news', 'content', 'social']
                    )
                    return {
                        'unblock_type': 'data_refresh',
                        'result': refresh_result,
                        'message': f"Triggered data refresh for: {topic}"
                    }
                except Exception as refresh_error:
                    logger.warning(f"Data refresh failed: {refresh_error}")
                    return {
                        'unblock_type': 'data_refresh_failed',
                        'error': str(refresh_error),
                        'message': f"Data refresh failed for: {topic}"
                    }

            else:
                # Default: trigger comprehensive research request
                return {
                    'unblock_type': 'research_request',
                    'message': f"Research blocked - manual intervention may be needed for: {topic}"
                }

        except Exception as e:
            logger.error(f"[Session 866] Self-unblock failed: {e}")
            return {
                'unblock_type': 'failed',
                'error': str(e),
                'message': f"Could not auto-unblock: {topic}"
            }

    def _create_blocked_research_result(
        self,
        topic: str,
        reasoning: str,
        findings: str,
        findings_detailed: List[Dict],
        owner_agent: str,
        unblock_result: Dict[str, Any]
    ) -> Any:
        """
        Session 905: Create a ResearchResult record when research is blocked.
        Session 906: Enhanced to create proper tracking records (HiveMindSession, AgentExecution).

        This enables the self-unblock loop by:
        1. Creating a persistent record of blocked research
        2. Linking to the Initiative and Stage
        3. Scheduling a retry task
        4. Session 906: Creating HiveMindSession for Origin & Trigger tracking
        5. Session 906: Creating AgentExecution for agent participation tracking

        Args:
            topic: Research topic
            reasoning: Why research was requested
            findings: Partial findings collected
            findings_detailed: Detailed findings list
            owner_agent: Agent responsible
            unblock_result: Result from _trigger_self_unblock

        Returns:
            ResearchResult or None
        """
        try:
            from core.models_research import ResearchResult
            from core.models_document_registry import Initiative, InitiativeStage
            from core.models_unified_system import HiveMindSession, HiveMindContribution
            from core.models.agents_registry.models import AgentExecution, UnifiedAgentTemplate
            from core.tasks import retry_blocked_research
            from datetime import timedelta
            import uuid

            # Find or create the Initiative for this topic
            initiative = None
            initiative_stage = None
            hive_session = None

            # First try to find existing similar initiative (dedup)
            try:
                from core.services.initiative_circuit_breaker import find_similar_initiative
                from core.services.initiative_title_generator import generate_initiative_title
                initiative_name = generate_initiative_title(
                    content=reasoning[:1000] if reasoning else '',
                    topic_hint=topic,
                    max_length=80,
                    use_llm=True
                )
                initiative = find_similar_initiative(initiative_name)
            except Exception as e:
                logger.warning(f"Initiative dedup lookup failed for topic: {e}")
                initiative_name = topic[:80]

            if not initiative:
                # Circuit breaker check
                from core.services.initiative_circuit_breaker import can_create_initiative
                if not can_create_initiative():
                    logger.warning(
                        f"[circuit_breaker] Blocked initiative creation from autonomous executor "
                        f"for: {topic[:50]}"
                    )
                    # Skip initiative creation — research result is still valuable
                else:
                    # Create new initiative
                    try:
                        initiative = Initiative.objects.create(
                            name=initiative_name,
                            description=f"Auto-created from blocked research. {reasoning[:500]}",
                            status='TRIAGE',  # Session 1016: TRIAGE not ACTIVE — must pass quality gate
                            purpose='learning',
                            current_stage=1,
                            created_by='ResearchAgent'
                        )

                        # Session 1003: Auto-set founder intent so auto-progression works
                        initiative.set_founder_intent(
                            execution_speed='balanced',
                            risk_tolerance='balanced',
                            set_by='system_auto'
                        )

                        logger.info(f"[Session 906] Created new Initiative: {initiative.id}")

                        # Session 1016: Auto-link to signal cluster
                        try:
                            from core.services.initiative_signal_linker import auto_link_initiative_signals
                            auto_link_initiative_signals(initiative)
                        except Exception as e:
                            logger.debug(f"Signal auto-link skipped: {e}")

                        # Create all 5 stages
                        for stage_num in range(1, 6):
                            InitiativeStage.objects.create(
                                initiative=initiative,
                                stage=stage_num,
                                status='PENDING' if stage_num > 1 else 'BLOCKED'
                            )

                        # Session 906: Create HiveMindSession for tracking
                        try:
                            # Get ResearchAgent template for participant tracking
                            research_agent = UnifiedAgentTemplate.objects.filter(
                                name__icontains='Research'
                            ).first()
                            participant_ids = [str(research_agent.id)] if research_agent else []

                            hive_session = HiveMindSession.objects.create(
                                session_mode='autonomous',
                                question=f"Research blocked: {topic[:200]}",
                                context=reasoning[:1000] if reasoning else '',
                                conversation_topic=topic[:200],
                                conversation_type='analytical',
                                objective=f"Gather data for: {topic[:150]}",
                                success_criteria=['Sufficient data collected', 'Research unblocked'],
                                auto_selected_agents=True,
                                status='completed',
                                participant_ids=participant_ids,
                                synthesis=f"Research blocked due to insufficient data. Trigger: {unblock_result.get('unblock_type', 'unknown')}. {findings[:500] if findings else 'Awaiting data.'}",
                                synthesis_summary=f"Blocked research - awaiting spider data for: {topic[:100]}",
                                contribution_count=1,
                            )
                            logger.info(f"[Session 906] Created HiveMindSession: {hive_session.id}")

                            # Create a contribution record
                            if research_agent:
                                HiveMindContribution.objects.create(
                                    session=hive_session,
                                    agent_id=str(research_agent.id),
                                    agent_name=research_agent.name,
                                    content=f"Attempted research on '{topic[:100]}' but encountered insufficient data. Triggered self-unblock: {unblock_result.get('unblock_type', 'unknown')}",
                                    confidence_score=0.3,
                                    thinking_time=1.0,
                                )

                            # Session 906: Create AgentExecution record
                            if research_agent:
                                AgentExecution.objects.create(
                                    template=research_agent,
                                    execution_id=f"blocked-research-{uuid.uuid4().hex[:8]}",
                                    task_description=f"Research: {topic[:200]}",
                                    task_type='research',
                                    context={
                                        'initiative_id': str(initiative.id),
                                        'topic': topic[:200],
                                        'blocked_reason': 'insufficient_data',
                                    },
                                    status='completed',
                                    progress_percentage=100,
                                    current_step='Blocked - awaiting data',
                                    steps_completed=[
                                        'Research initiated',
                                        'Data sources queried',
                                        'Insufficient data detected',
                                        'Self-unblock triggered',
                                    ],
                                    result={
                                        'success': False,
                                        'blocked': True,
                                        'unblock_type': unblock_result.get('unblock_type'),
                                        'initiative_id': str(initiative.id),
                                    },
                                    metadata={
                                        'initiative_id': str(initiative.id),
                                        'hive_session_id': str(hive_session.id) if hive_session else None,
                                        'auto_created': True,
                                        'session': 906,
                                    },
                                )
                                logger.info(f"[Session 906] Created AgentExecution for {research_agent.name}")

                        except Exception as session_error:
                            logger.warning(f"[Session 906] Could not create tracking records: {session_error}")

                    except Exception as init_error:
                        logger.warning(f"[Session 906] Could not create Initiative: {init_error}")

            # Get Stage 1 if initiative exists
            if initiative:
                try:
                    initiative_stage = InitiativeStage.objects.get(
                        initiative=initiative,
                        stage=1
                    )
                    # Mark stage as BLOCKED
                    initiative_stage.status = 'BLOCKED'
                    initiative_stage.notes = f"Blocked: Insufficient data. Spider spawned: {unblock_result.get('unblock_type')}"
                    initiative_stage.save(update_fields=['status', 'notes', 'updated_at'])
                except InitiativeStage.DoesNotExist:
                    pass

            # Create the ResearchResult record
            research_result = ResearchResult.objects.create(
                id=uuid.uuid4(),
                initiative=initiative,
                initiative_stage=initiative_stage,
                topic=topic[:500],
                research_type='data_analysis',
                status='blocked',
                data_sufficient=False,
                blocked_reason=f"Insufficient data. Triggered: {unblock_result.get('unblock_type')}",
                retry_count=0,
                max_retries=3,
                retry_after=timezone.now() + timedelta(minutes=30),
                unblock_trigger='spider_data_arrival',
                queries=[topic],
                external_sources=findings_detailed[:10] if findings_detailed else [],
                findings={'partial': findings[:2000] if findings else 'No findings yet'},
                summary=f"Research blocked on: {topic}. Awaiting spider data.",
                conducted_by=owner_agent,
                confidence_score=0.2,
            )

            logger.info(f"[Session 905] Created blocked ResearchResult: {research_result.id}")

            # Schedule the retry task
            try:
                task = retry_blocked_research.apply_async(
                    args=[str(research_result.id)],
                    eta=research_result.retry_after
                )
                logger.info(f"[Session 905] Scheduled retry task: {task.id} for {research_result.retry_after}")
            except Exception as task_error:
                logger.warning(f"[Session 905] Could not schedule retry task: {task_error}")

            return research_result

        except Exception as e:
            logger.error(f"[Session 905] Failed to create blocked ResearchResult: {e}")
            return None

    def _synthesize_single_deliverable(
        self,
        content_writer,  # Legacy param, now uses TechnicalDocumentAgent
        deliverable_name: str,
        topic: str,
        research_context: str,
        reasoning: str
    ) -> Dict[str, Any]:
        """
        Session 620.1: Synthesize a single deliverable.
        Session 622: Updated to use TechnicalDocumentAgent with stage-aware naming.

        Creates a professional technical document based on the deliverable name
        and research context. Documents are now stage-aware and use formal
        language instead of blog-style content.
        """
        from core.models_unified_system import SelfBlog
        from core.agents.technical_document_agent import (
            TechnicalDocumentAgent,
            infer_stage_from_deliverable
        )
        import uuid

        # Session 622: Infer stage and document type
        stage_info = infer_stage_from_deliverable(deliverable_name)
        stage = stage_info['stage']
        doc_type = stage_info['doc_type']
        stage_name = stage_info['stage_name']
        stage_prefix = stage_info['prefix']

        logger.info(f"Synthesizing deliverable: {deliverable_name} as {stage_prefix}")

        # Build the synthesis task for TechnicalDocumentAgent
        synthesis_task = f"""Create a formal {stage_name} document for: {deliverable_name}

This is part of the product development lifecycle for: {topic}

The document should:
1. Use formal, professional language (NO blog-style phrasing)
2. Include specific, measurable criteria where applicable
3. Be structured for executive review and decision-making
4. Include governance and compliance considerations for Stage 3+ documents
"""

        # Session 622: Use TechnicalDocumentAgent instead of ContentWriterAgent
        try:
            technical_agent = TechnicalDocumentAgent()
            result = technical_agent.execute(
                task=synthesis_task,
                context={
                    'deliverable': deliverable_name,
                    'topic': topic,
                    'doc_type': doc_type,
                    'stage': stage,
                    'research_context': research_context,
                    'reasoning': reasoning,
                    'autonomous': True,
                    'classification': 'INTERNAL'
                },
                scifi_context={},
                spider_context={}
            )

            # Extract content from TechnicalDocumentAgent result
            content = ""
            if hasattr(result, 'data') and result.data:
                if isinstance(result.data, dict):
                    content_data = result.data.get('content', {})
                    if isinstance(content_data, dict):
                        content = content_data.get('full_text', '')
                    elif content_data:
                        content = str(content_data)
                else:
                    content = str(result.data)
            elif hasattr(result, 'message') and result.message:
                content = result.message

            logger.info(f"Extracted content length: {len(content)} chars for {stage_prefix}")

            if not content or len(content) < 100:
                # Fallback to ContentWriterAgent if TechnicalDocumentAgent fails
                logger.warning(f"TechnicalDocumentAgent returned insufficient content, falling back to ContentWriterAgent")
                return self._synthesize_with_fallback(
                    content_writer, deliverable_name, topic, research_context, reasoning, stage_info
                )

            # Session 622: Save with stage-aware title
            # Session 852: Set category='technical_document' so deliverables don't appear as blogs
            blog = SelfBlog.objects.create(
                id=uuid.uuid4(),
                title=f"[{stage_prefix}] {deliverable_name[:60]}",
                category='technical_document',  # Session 852: Use technical_document category
                intro=f"Synthesized deliverable for: {topic}. Stage {stage} of 5 - {stage_name}",
                conclusion=f"This document was auto-generated as part of the product development lifecycle. Review and customize as needed.",
                full_text=content,
                tone="professional",
                stats_snapshot={
                    'auto_generated': True,
                    'action_type': 'synthesized_deliverable',
                    'parent_topic': topic,
                    'deliverable_name': deliverable_name,
                    'doc_type': doc_type,
                    'stage': stage,
                    'stage_name': stage_name,
                    'stage_prefix': stage_prefix,
                    'content_length': len(content),
                    'has_governance': stage >= 3,  # Stage 3+ includes governance
                }
            )

            logger.info(f"Deliverable saved to SelfBlog: {blog.id} ({stage_prefix})")

            # Session 804: Create attention item so deliverable surfaces in Human Interface
            self._create_blog_attention_item(blog, content_type='deliverable', agent_name='TechnicalDocumentAgent')

            return {
                'deliverable': deliverable_name,
                'success': True,
                'blog_id': str(blog.id),
                'doc_type': doc_type,
                'stage': stage,
                'stage_name': stage_name,
                'stage_prefix': stage_prefix,
                'content_length': len(content),
                'preview': content[:300] + '...' if len(content) > 300 else content
            }

        except Exception as e:
            logger.error(f"Error in TechnicalDocumentAgent: {e}")
            # Fallback to ContentWriterAgent
            return self._synthesize_with_fallback(
                content_writer, deliverable_name, topic, research_context, reasoning, stage_info
            )

    def _synthesize_with_fallback(
        self,
        content_writer,
        deliverable_name: str,
        topic: str,
        research_context: str,
        reasoning: str,
        stage_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Session 622: Fallback synthesis using ContentWriterAgent if TechnicalDocumentAgent fails.
        """
        from core.models_unified_system import SelfBlog
        import uuid

        stage = stage_info['stage']
        doc_type = stage_info['doc_type']
        stage_name = stage_info['stage_name']
        stage_prefix = stage_info['prefix']

        synthesis_task = f"""Create a professional {stage_name} document for: {deliverable_name}

**Parent Topic:** {topic}
**Purpose:** {reasoning}

{research_context}

**Instructions:**
1. Create a comprehensive, professional document
2. Use formal language (avoid blog-style phrasing)
3. Structure with clear sections and headers
4. Include specific recommendations
5. Use markdown formatting
"""

        try:
            result = content_writer.execute(
                task=synthesis_task,
                context={
                    'deliverable': deliverable_name,
                    'topic': topic,
                    'doc_type': doc_type,
                    'autonomous': True,
                    'synthesis_mode': True
                },
                scifi_context={},
                spider_context={}
            )

            content = ""
            if hasattr(result, 'data') and result.data:
                if isinstance(result.data, dict):
                    content_data = result.data.get('content', {})
                    if isinstance(content_data, dict):
                        content = content_data.get('full_text', '') or content_data.get('raw_content', '')
                        if not content:
                            content = str(content_data)
                    elif content_data:
                        content = str(content_data)
                    else:
                        content = result.data.get('text', str(result.data))
                else:
                    content = str(result.data)
            elif hasattr(result, 'content') and result.content:
                content = str(result.content)
            elif hasattr(result, 'message') and result.message:
                content = result.message

            if not content or len(content) < 100:
                return {
                    'deliverable': deliverable_name,
                    'success': False,
                    'error': 'Both TechnicalDocumentAgent and ContentWriterAgent returned insufficient content'
                }

            # Session 852: Set category='technical_document' for fallback deliverables too
            blog = SelfBlog.objects.create(
                id=uuid.uuid4(),
                title=f"[{stage_prefix}] {deliverable_name[:60]}",
                category='technical_document',  # Session 852: Use technical_document category
                intro=f"Synthesized deliverable for: {topic}. Stage {stage} of 5 - {stage_name} (fallback)",
                conclusion=f"This document was auto-generated. Review and customize as needed.",
                full_text=content,
                tone="professional",
                stats_snapshot={
                    'auto_generated': True,
                    'action_type': 'synthesized_deliverable',
                    'parent_topic': topic,
                    'deliverable_name': deliverable_name,
                    'doc_type': doc_type,
                    'stage': stage,
                    'stage_name': stage_name,
                    'stage_prefix': stage_prefix,
                    'content_length': len(content),
                    'fallback_used': True,
                }
            )

            # Session 804: Create attention item so deliverable surfaces in Human Interface
            self._create_blog_attention_item(blog, content_type='deliverable', agent_name='ContentWriterAgent')

            return {
                'deliverable': deliverable_name,
                'success': True,
                'blog_id': str(blog.id),
                'doc_type': doc_type,
                'stage': stage,
                'stage_name': stage_name,
                'content_length': len(content),
                'fallback_used': True,
            }

        except Exception as e:
            logger.error(f"Fallback synthesis failed: {e}")
            return {
                'deliverable': deliverable_name,
                'success': False,
                'error': str(e)
            }

    def _infer_document_type(self, deliverable_name: str) -> str:
        """
        Session 620.1: Infer the document type from the deliverable name.
        Session 622: Now calls the enhanced infer_stage_from_deliverable() function.

        Returns a document type string to guide content generation.
        """
        from core.agents.technical_document_agent import infer_stage_from_deliverable
        stage_info = infer_stage_from_deliverable(deliverable_name)
        return stage_info['doc_type']

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

        # Session 1076: Spawn gate — dedup check before creating
        from core.tasks import _conversation_spawn_allowed
        full_topic = f"[Auto] {topic}"
        if not _conversation_spawn_allowed(full_topic, hours=6, log_prefix='[AUTO-ACTION]'):
            return {
                'success': False,
                'message': f'Spawn gate blocked: similar conversation exists for "{topic[:60]}"'
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
        Session 855: Enhanced with adaptive thresholds based on backlog size

        Evaluates pending dreams and routes them:
        - HIGH VALUE (composite >= 0.65, actionability >= 0.6) -> Boardroom
        - INSPIRATION (composite >= 0.5, actionability < 0.5) -> Mark as shown
        - STALE (older than freshness threshold) -> Archive
        - LOW SCORE (below threshold) -> Archive

        Session 855: When backlog exceeds 100 dreams or oldest > 48h,
        automatically uses more aggressive thresholds to clear the backlog.
        """
        from core.models_unified_system import AgentDream

        # Session 855: Check backlog health to determine if aggressive mode needed
        pending_count = AgentDream.objects.filter(
            promoted_to_decision=False,
            shown_to_user=False
        ).count()

        oldest_pending = AgentDream.objects.filter(
            promoted_to_decision=False,
            shown_to_user=False
        ).order_by('dreamed_at').first()

        oldest_age_hours = 0
        if oldest_pending:
            oldest_age_hours = (timezone.now() - oldest_pending.dreamed_at).total_seconds() / 3600

        # Session 855: Determine if aggressive mode needed
        aggressive_mode = pending_count > 100 or oldest_age_hours > 48

        if aggressive_mode:
            logger.info(
                f"[Session 855] Dream triage AGGRESSIVE mode activated: "
                f"{pending_count} pending, oldest {oldest_age_hours:.1f}h"
            )

        # Get thresholds from params or use defaults
        # Session 855: More aggressive defaults when backlog is large
        if aggressive_mode:
            boardroom_threshold = params.get('boardroom_threshold', 0.60)  # Was 0.65
            boardroom_action_threshold = params.get('boardroom_action_threshold', 0.5)  # Was 0.6
            inspiration_threshold = params.get('inspiration_threshold', 0.45)  # Was 0.5
            archive_age_hours = params.get('archive_age_hours', 48)  # 48h freshness threshold
            archive_score_threshold = params.get('archive_score_threshold', 0.5)  # Was 0.4
            max_to_process = params.get('max_to_process', 200)  # Was 50
        else:
            boardroom_threshold = params.get('boardroom_threshold', 0.65)
            boardroom_action_threshold = params.get('boardroom_action_threshold', 0.6)
            inspiration_threshold = params.get('inspiration_threshold', 0.5)
            archive_age_hours = params.get('archive_age_hours', 336)  # 14 days in hours
            archive_score_threshold = params.get('archive_score_threshold', 0.4)
            max_to_process = params.get('max_to_process', 50)

        # Support legacy archive_age_days param
        if 'archive_age_days' in params:
            archive_age_hours = params['archive_age_days'] * 24

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
            age_hours = (now - dream.dreamed_at).total_seconds() / 3600

            # Route 1: HIGH VALUE -> Boardroom
            if (dream.composite_score >= boardroom_threshold and
                dream.actionability_score >= boardroom_action_threshold):
                dream.promoted_to_decision = True
                dream.promoted_at = now
                dream.decision_outcome = 'pending'  # Session 855: Set initial outcome
                dream.save()
                results['promoted_to_boardroom'].append({
                    'id': str(dream.id),
                    'title': dream.title[:50],
                    'score': dream.composite_score,
                    'agent': dream.agent.name if dream.agent else 'Unknown'
                })

            # Route 2: STALE -> Archive (past freshness threshold)
            # Session 855: In aggressive mode, stale alone is enough reason to archive
            elif age_hours >= archive_age_hours:
                dream.shown_to_user = True
                dream.shown_at = now
                dream.user_feedback = 'auto_archived_stale'
                dream.save()
                results['archived'].append({
                    'id': str(dream.id),
                    'title': dream.title[:50],
                    'age_hours': round(age_hours, 1),
                    'score': dream.composite_score,
                    'reason': 'stale'
                })

            # Route 3: LOW SCORE -> Archive (below quality threshold)
            # Session 855: Archive low-score dreams regardless of age
            elif dream.composite_score < archive_score_threshold:
                dream.shown_to_user = True
                dream.shown_at = now
                dream.user_feedback = 'auto_archived_low_score'
                dream.save()
                results['archived'].append({
                    'id': str(dream.id),
                    'title': dream.title[:50],
                    'age_hours': round(age_hours, 1),
                    'score': dream.composite_score,
                    'reason': 'low_score'
                })

            # Route 4: INSPIRATION (creative but not actionable)
            # Session 855: In aggressive mode, skip inspiration route - be decisive
            elif (not aggressive_mode and
                  dream.composite_score >= inspiration_threshold and
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
                # Session 855: In aggressive mode, good dreams below boardroom threshold
                # still get skipped for now (they'll be promoted eventually or age out)
                results['skipped'] += 1

        # Summary
        total_processed = (
            len(results['promoted_to_boardroom']) +
            len(results['marked_as_inspiration']) +
            len(results['archived'])
        )

        mode_label = "AGGRESSIVE" if aggressive_mode else "normal"
        logger.info(
            f"Dream triage ({mode_label}): {len(results['promoted_to_boardroom'])} to boardroom, "
            f"{len(results['marked_as_inspiration'])} to inspiration, "
            f"{len(results['archived'])} archived, {results['skipped']} skipped"
        )

        return {
            'total_processed': total_processed,
            'promoted_to_boardroom': len(results['promoted_to_boardroom']),
            'marked_as_inspiration': len(results['marked_as_inspiration']),
            'archived': len(results['archived']),
            'skipped': results['skipped'],
            'aggressive_mode': aggressive_mode,
            'details': results,
            'message': f"Triaged {total_processed} dreams ({mode_label} mode): {len(results['promoted_to_boardroom'])} to Boardroom, {len(results['archived'])} archived"
        }

    # =========================================================================
    # Session 654: Autonomous Gate Approval
    # =========================================================================

    def _execute_auto_approve_gates(
        self,
        name: str,
        params: Dict[str, Any],
        reasoning: str
    ) -> Dict[str, Any]:
        """
        Session 654: Auto-approve low-risk gates and optionally deploy as pilots.
        Session 855: Enhanced with adaptive aggressive mode for gate backlogs.

        This action:
        1. Finds all 'not_started' gates with risk_level='low'
        2. Auto-waives them (using the built-in waive() method)
        3. Optionally creates and starts pilot executions
        4. Records learnings for ThinkingAgent feedback loop

        Session 855: When gate backlog exceeds 50 or oldest gate > 72h,
        automatically uses aggressive mode that also waives stale medium-risk gates.

        Safety Rails:
        - Default: ONLY processes 'low' risk gates
        - Aggressive: Also processes stale (>72h) medium-risk gates
        - High/critical always require human review
        - Maximum batch size to prevent runaway processing
        - All actions logged and tracked

        Args:
            name: Action name for logging
            params: {
                'max_gates': Maximum gates to process (default: 20, aggressive: 50),
                'auto_deploy': Whether to auto-start pilots (default: False),
                'dry_run': If True, just report what would happen (default: False),
                'include_stale_medium': Force include stale medium-risk (default: auto)
            }
            reasoning: Why this action was triggered

        Returns:
            Summary of gates processed
        """
        from core.models_pilot_readiness import PilotReadinessGate, PilotExecution
        from datetime import timedelta

        # Session 855: Check gate backlog health to determine if aggressive mode needed
        pending_count = PilotReadinessGate.objects.filter(status='not_started').count()

        oldest_gate = PilotReadinessGate.objects.filter(
            status='not_started'
        ).order_by('created_at').first()

        oldest_age_hours = 0
        if oldest_gate:
            oldest_age_hours = (timezone.now() - oldest_gate.created_at).total_seconds() / 3600

        # Session 855: Determine if aggressive mode needed
        aggressive_mode = pending_count > 50 or oldest_age_hours > 72
        include_stale_medium = params.get('include_stale_medium', aggressive_mode)

        if aggressive_mode:
            max_gates = params.get('max_gates', 50)  # Higher default in aggressive mode
            stale_threshold_hours = params.get('stale_hours', 72)
            logger.info(
                f"🚦 [Session 855] Gate approval AGGRESSIVE mode activated: "
                f"{pending_count} pending, oldest {oldest_age_hours:.1f}h"
            )
        else:
            max_gates = params.get('max_gates', 20)
            stale_threshold_hours = params.get('stale_hours', 72)

        auto_deploy = params.get('auto_deploy', False)
        dry_run = params.get('dry_run', False)

        logger.info(f"🚦 [Session 654/855] Auto-approving gates (max={max_gates}, aggressive={aggressive_mode}, auto_deploy={auto_deploy}, dry_run={dry_run})")

        # Find low-risk gates that haven't been started
        pending_gates = list(PilotReadinessGate.objects.filter(
            status='not_started',
            risk_level='low'
        ).select_related('decision').order_by('created_at')[:max_gates])

        # Session 855: In aggressive mode, also include stale medium-risk gates
        if include_stale_medium:
            stale_cutoff = timezone.now() - timedelta(hours=stale_threshold_hours)
            remaining_slots = max_gates - len(pending_gates)
            if remaining_slots > 0:
                stale_medium_gates = PilotReadinessGate.objects.filter(
                    status='not_started',
                    risk_level='medium',
                    created_at__lt=stale_cutoff
                ).select_related('decision').order_by('created_at')[:remaining_slots]
                pending_gates.extend(stale_medium_gates)
                logger.info(f"🚦 [Session 855] Added {len(stale_medium_gates)} stale medium-risk gates to processing queue")

        results = {
            'waived': [],
            'waived_stale_medium': [],  # Session 855: Track stale medium separately
            'deployed': [],
            'skipped': [],
            'errors': []
        }

        for gate in pending_gates:
            try:
                decision_topic = gate.decision.topic[:60] if gate.decision else 'Unknown'
                is_stale_medium = gate.risk_level == 'medium'  # Session 855

                # Session 847: Skip initiative-linked gates (require human review)
                if gate.initiative is not None:
                    results['skipped'].append({
                        'gate_id': str(gate.id),
                        'topic': decision_topic,
                        'reason': 'Linked to initiative - requires human review'
                    })
                    logger.info(f"[Session 847] Skipped initiative-linked gate: {decision_topic}")
                    continue

                if dry_run:
                    results['waived'].append({
                        'gate_id': str(gate.id),
                        'topic': decision_topic,
                        'action': 'would_waive'
                    })
                    continue

                # Auto-waive the gate (built-in method only works for low-risk)
                waived = gate.waive(
                    reason=f'Auto-waived by ThinkingAgent: {reasoning[:100]}',
                    waived_by='ThinkingAgent'
                )

                if waived:
                    waive_record = {
                        'gate_id': str(gate.id),
                        'topic': decision_topic,
                        'risk_level': gate.risk_level,
                        'waived_at': timezone.now().isoformat()
                    }
                    # Session 855: Track stale medium separately
                    if is_stale_medium:
                        results['waived_stale_medium'].append(waive_record)
                    else:
                        results['waived'].append(waive_record)

                    # Optionally auto-deploy as pilot
                    if auto_deploy:
                        try:
                            pilot = PilotExecution.objects.create(
                                gate=gate,
                                name=f"Auto-pilot: {decision_topic[:80]}",
                                description=f"Auto-deployed from low-risk gate. Reasoning: {reasoning[:200]}",
                                status='planned',
                                scope=gate.summary or decision_topic
                            )
                            pilot.start()

                            results['deployed'].append({
                                'gate_id': str(gate.id),
                                'pilot_id': str(pilot.id),
                                'topic': decision_topic
                            })
                        except Exception as e:
                            logger.error(f"Failed to deploy pilot for gate {gate.id}: {e}")
                            results['errors'].append({
                                'gate_id': str(gate.id),
                                'error': f'Pilot deployment failed: {str(e)}'
                            })
                else:
                    results['skipped'].append({
                        'gate_id': str(gate.id),
                        'topic': decision_topic,
                        'reason': 'waive() returned False - may not be low-risk'
                    })

            except Exception as e:
                logger.error(f"Error processing gate {gate.id}: {e}")
                results['errors'].append({
                    'gate_id': str(gate.id),
                    'error': str(e)
                })

        total_low_risk = len(results['waived'])
        total_stale_medium = len(results['waived_stale_medium'])
        total_processed = total_low_risk + total_stale_medium
        total_deployed = len(results['deployed'])

        # Session 855: Enhanced summary with aggressive mode info
        mode_label = "AGGRESSIVE" if aggressive_mode else "normal"
        summary_parts = [f"Auto-approved {total_low_risk} low-risk gates"]
        if total_stale_medium > 0:
            summary_parts.append(f"{total_stale_medium} stale medium-risk gates")
        if auto_deploy:
            summary_parts.append(f"deployed {total_deployed} pilots")
        summary_msg = f"({mode_label} mode) " + ", ".join(summary_parts)
        if dry_run:
            summary_msg = f"[DRY RUN] Would process {total_processed} gates"

        logger.info(f"🚦 [Session 654/855] {summary_msg}")

        return {
            'total_processed': total_processed,
            'total_low_risk': total_low_risk,
            'total_stale_medium': total_stale_medium,
            'total_deployed': total_deployed,
            'total_skipped': len(results['skipped']),
            'total_errors': len(results['errors']),
            'aggressive_mode': aggressive_mode,
            'dry_run': dry_run,
            'details': results,
            'message': summary_msg
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

    # =========================================================================
    # Session 847: Initiative Pipeline Actions
    # =========================================================================

    def _execute_promote_initiative_stage(
        self,
        name: str,
        params: Dict[str, Any],
        reasoning: str
    ) -> Dict[str, Any]:
        """
        Session 847: Promote an initiative stage to APPROVED status.

        This unlocks the next stage in the 5-stage pipeline.

        Args:
            name: Action name
            params: {
                'initiative_name': Name of the initiative,
                'stage': Stage number to promote (1-5),
                'auto_promote_all': If true, auto-promote all ready stages
            }
            reasoning: Why this promotion was triggered

        Returns:
            Summary of promotion results
        """
        from core.services.initiative_integration_service import get_initiative_integration_service
        from core.models_document_registry import Initiative

        initiative_name = params.get('initiative_name', '')
        stage = params.get('stage')
        auto_promote_all = params.get('auto_promote_all', False)

        logger.info(f"[Session 847] Promoting initiative stage: {initiative_name}, stage={stage}, auto_all={auto_promote_all}")

        service = get_initiative_integration_service()
        results = {
            'promoted': [],
            'skipped': [],
            'errors': []
        }

        try:
            # Get the initiative
            initiative = Initiative.objects.filter(name__icontains=initiative_name).first()
            if not initiative:
                return {
                    'success': False,
                    'error': f'Initiative not found: {initiative_name}',
                    'results': results
                }

            if auto_promote_all:
                # Auto-promote all ready stages
                promoted = service.auto_promote_if_ready(initiative)
                results['promoted'] = promoted
                message = f"Auto-promoted {len(promoted)} stages"
            elif stage:
                # Promote specific stage
                success = service.promote_stage(initiative, stage, approved_by="ThinkingAgent")
                if success:
                    results['promoted'] = [stage]
                    message = f"Promoted Stage {stage}"
                else:
                    results['skipped'] = [stage]
                    message = f"Could not promote Stage {stage}"
            else:
                return {
                    'success': False,
                    'error': 'Must specify stage or auto_promote_all',
                    'results': results
                }

            return {
                'success': True,
                'initiative_name': initiative.name,
                'initiative_id': str(initiative.id),
                'current_stage': initiative.current_stage,
                'completion_percentage': initiative.completion_percentage,
                'results': results,
                'message': message
            }

        except Exception as e:
            logger.error(f"[Session 847] Error promoting stage: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': results
            }

    def _execute_review_initiatives(
        self,
        name: str,
        params: Dict[str, Any],
        reasoning: str
    ) -> Dict[str, Any]:
        """
        Session 847: Review all initiatives and report on health.

        This surfaces stale, blocked, or completed initiatives.

        Args:
            name: Action name
            params: {
                'auto_archive_completed': Archive completed initiatives (default: False),
                'alert_on_stale': Generate alerts for stale initiatives (default: True)
            }
            reasoning: Why this review was triggered

        Returns:
            Dashboard summary of all initiatives
        """
        from core.services.initiative_integration_service import get_initiative_integration_service
        from core.models_document_registry import Initiative

        auto_archive = params.get('auto_archive_completed', False)
        alert_on_stale = params.get('alert_on_stale', True)

        logger.info(f"[Session 847] Reviewing initiatives: auto_archive={auto_archive}, alert_on_stale={alert_on_stale}")

        service = get_initiative_integration_service()
        dashboard = service.get_all_initiatives_dashboard()

        results = {
            'archived': [],
            'alerts_generated': [],
            'auto_promoted': []
        }

        # Process initiatives based on health
        for init_health in dashboard['initiatives']:
            initiative_id = init_health['initiative_id']

            try:
                initiative = Initiative.objects.get(id=initiative_id)

                # Auto-archive completed initiatives (100% completion)
                if auto_archive and init_health['completion_percentage'] == 100:
                    initiative.status = Initiative.Status.COMPLETED
                    initiative.save()
                    results['archived'].append(init_health['name'])
                    logger.info(f"[Session 847] Archived completed initiative: {init_health['name']}")

                # Generate alerts for stale/blocked initiatives
                if alert_on_stale and init_health['health'] in ['stale', 'blocked']:
                    alert_msg = f"Initiative '{init_health['name']}' is {init_health['health']}: {', '.join(init_health.get('health_issues', []))}"
                    results['alerts_generated'].append(alert_msg)
                    logger.warning(f"[Session 847] {alert_msg}")

                # Try auto-promoting ready stages
                promoted = service.auto_promote_if_ready(initiative)
                if promoted:
                    results['auto_promoted'].append({
                        'initiative': init_health['name'],
                        'stages_promoted': promoted
                    })

            except Exception as e:
                logger.error(f"[Session 847] Error processing initiative {initiative_id}: {e}")

        # Update dashboard with action results
        dashboard['action_results'] = results

        return {
            'success': True,
            'total_initiatives': dashboard['total'],
            'by_health': dashboard['by_health'],
            'archived_count': len(results['archived']),
            'alerts_count': len(results['alerts_generated']),
            'auto_promoted_count': len(results['auto_promoted']),
            'dashboard': dashboard,
            'message': f"Reviewed {dashboard['total']} initiatives: {dashboard['by_health']['healthy']} healthy, {dashboard['by_health']['stale']} stale, {dashboard['by_health']['blocked']} blocked"
        }
