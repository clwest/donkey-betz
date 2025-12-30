"""
Autonomous Action Executor - Executes decisions made by the ThinkingAgent

Session 544: This service takes the decisions from the ThinkingAgent and
actually executes them using the appropriate agents and services.
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
        synthesize_deliverables = params.get('synthesize_deliverables', True)  # Session 620.1
        owner_agent = params.get('owner_agent', 'ResearchAgent')
        deadline_hours = params.get('deadline_hours', 72)

        # Build comprehensive research task including deliverables
        task_parts = [f"Research topic: {topic}"]
        task_parts.append(f"Depth: {depth}")

        if deliverables:
            task_parts.append("\nRequired deliverables:")
            for i, deliverable in enumerate(deliverables, 1):
                task_parts.append(f"  {i}. {deliverable}")

        if reasoning:
            task_parts.append(f"\nContext: {reasoning}")

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

        # Session 620: Create a SelfBlog entry to persist research findings
        research_blog_id = None
        if research_successful:
            try:
                research_report = f"""# Research Report: {topic}

## Request Context
{reasoning}

## Deliverables Requested
{chr(10).join(f'- {d}' for d in deliverables) if deliverables else 'None specified'}

## Research Findings
{findings if findings else 'Research completed - see data below'}

## Data Sources Consulted
{', '.join(r.get('source', 'unknown') for r in research_data.get('results', [])) if isinstance(research_data, dict) else 'Multiple sources'}

---
*Auto-generated research report from ThinkingAgent autonomous action*
"""

                blog = SelfBlog.objects.create(
                    id=uuid.uuid4(),
                    title=f"[Research] {topic[:100]}",
                    intro=f"Autonomous research on: {topic}. Deliverables: {len(deliverables)}",
                    conclusion="Research findings saved for review. Execute follow-up actions as needed.",
                    full_text=research_report,
                    tone="analytical",
                    stats_snapshot={
                        'auto_generated': True,
                        'action_type': 'request_research',
                        'deliverables': deliverables,
                        'owner_agent': owner_agent,
                        'reasoning': reasoning[:200] if reasoning else '',
                    }
                )
                research_blog_id = str(blog.id)
                logger.info(f"Research report saved: {blog.id}")

            except Exception as e:
                logger.warning(f"Could not save research report: {e}")

        # =========================================================
        # Session 620.1: SYNTHESIS PHASE - Create actual deliverables
        # =========================================================
        synthesized_deliverables = []

        if synthesize_deliverables and deliverables and research_successful:
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
            'synthesized_deliverables': synthesized_deliverables
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

    def _synthesize_single_deliverable(
        self,
        content_writer,
        deliverable_name: str,
        topic: str,
        research_context: str,
        reasoning: str
    ) -> Dict[str, Any]:
        """
        Session 620.1: Synthesize a single deliverable using ContentWriterAgent.

        Creates a professional document based on the deliverable name and research context.
        """
        from core.models_unified_system import SelfBlog
        import uuid

        # Determine document type based on deliverable name
        doc_type = self._infer_document_type(deliverable_name)

        # Build the synthesis task
        synthesis_task = f"""Create a professional {doc_type} document for the following deliverable:

**Deliverable:** {deliverable_name}

**Parent Topic:** {topic}

**Purpose:** {reasoning}

{research_context}

---

**Instructions:**
1. Create a comprehensive, professional document that addresses "{deliverable_name}"
2. Use the research findings above to inform your content
3. Structure the document with clear sections and headers
4. Include specific recommendations, not just general guidance
5. Make it actionable and implementation-ready
6. Use markdown formatting for clarity
"""

        # Call ContentWriterAgent
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

            # Extract content from result
            # Session 620.1 Fix: ContentWriterAgent returns data['content'] as a dict
            # with 'full_text' containing the actual content
            content = ""
            if hasattr(result, 'data') and result.data:
                if isinstance(result.data, dict):
                    content_data = result.data.get('content', {})
                    if isinstance(content_data, dict):
                        # ContentWriterAgent returns content as a dict with 'full_text'
                        content = content_data.get('full_text', '') or content_data.get('raw_content', '')
                        if not content:
                            # Fallback: stringify the content dict
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

            logger.info(f"Extracted content length: {len(content)} chars")

            if not content or len(content) < 100:
                return {
                    'deliverable': deliverable_name,
                    'success': False,
                    'error': 'ContentWriterAgent returned insufficient content'
                }

            # Save to SelfBlog
            blog = SelfBlog.objects.create(
                id=uuid.uuid4(),
                title=f"[Deliverable] {deliverable_name[:80]}",
                intro=f"Synthesized deliverable for: {topic}. Document type: {doc_type}",
                conclusion=f"This document was auto-generated based on research findings. Review and customize as needed.",
                full_text=content,
                tone="professional",
                stats_snapshot={
                    'auto_generated': True,
                    'action_type': 'synthesized_deliverable',
                    'parent_topic': topic,
                    'deliverable_name': deliverable_name,
                    'doc_type': doc_type,
                    'content_length': len(content)
                }
            )

            logger.info(f"Deliverable saved to SelfBlog: {blog.id}")

            return {
                'deliverable': deliverable_name,
                'success': True,
                'blog_id': str(blog.id),
                'doc_type': doc_type,
                'content_length': len(content),
                'preview': content[:300] + '...' if len(content) > 300 else content
            }

        except Exception as e:
            logger.error(f"Error in ContentWriterAgent: {e}")
            return {
                'deliverable': deliverable_name,
                'success': False,
                'error': str(e)
            }

    def _infer_document_type(self, deliverable_name: str) -> str:
        """
        Session 620.1: Infer the document type from the deliverable name.

        Returns a document type string to guide content generation.
        """
        name_lower = deliverable_name.lower()

        if 'design doc' in name_lower or 'architecture' in name_lower:
            return 'technical design document'
        elif 'recommendation' in name_lower:
            return 'recommendations report'
        elif 'test' in name_lower or 'testing' in name_lower or 'framework' in name_lower:
            return 'testing framework specification'
        elif 'metric' in name_lower or 'telemetry' in name_lower or 'kpi' in name_lower:
            return 'metrics and monitoring specification'
        elif 'compliance' in name_lower or 'regulatory' in name_lower or 'mapping' in name_lower:
            return 'compliance mapping document'
        elif 'checklist' in name_lower:
            return 'checklist document'
        elif 'plan' in name_lower or 'roadmap' in name_lower:
            return 'implementation plan'
        elif 'guide' in name_lower or 'how-to' in name_lower:
            return 'guide document'
        elif 'policy' in name_lower:
            return 'policy document'
        elif 'analysis' in name_lower or 'report' in name_lower:
            return 'analysis report'
        else:
            return 'professional document'

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
