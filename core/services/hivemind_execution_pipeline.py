"""
HiveMind Execution Pipeline
============================

Session 766: Connects HiveMind session syntheses to the Orchestration Layer.
Session 866: Enhanced to parse DecisionSummary and create Initiatives with agent tasks.

This service bridges the gap between HiveMind collective intelligence and execution:
1. When a HiveMind session completes with synthesis
2. Parses DecisionSummary to extract Proposed Feature and Next Steps
3. Creates an Initiative from the Proposed Feature (with 5-stage pipeline)
4. Generates a CustomWorkflow with steps for assigned agents
5. Triggers the Orchestration Engine

Solves Dead End #4: 321 HiveMind sessions with 182 syntheses, 0 acted upon.

Usage:
    from core.services.hivemind_execution_pipeline import hivemind_execution_pipeline

    # Execute a completed HiveMind session
    result = hivemind_execution_pipeline.execute_session(session)

    # Or process all unexecuted sessions
    results = hivemind_execution_pipeline.process_completed_sessions()
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.utils.text import slugify

logger = logging.getLogger(__name__)


class HiveMindExecutionPipeline:
    """
    Pipeline that converts HiveMind syntheses into executed workflows.

    Session 866 Enhancement: Now parses DecisionSummary to extract:
    - Proposed Feature (name, inputs, outputs, integration points)
    - Next Steps with specific agent assignments
    - Creates Initiatives and targeted agent workflows
    """

    # Map session modes to workflow templates (fallback if no Next Steps found)
    SESSION_MODE_WORKFLOWS = {
        'hive_mind': [
            ('ResearchAgent', 'Deep research on the collective insights'),
            ('ContentStrategyAgent', 'Develop action plan from synthesis'),
            ('ContentWriterAgent', 'Create implementation document'),
        ],
        'brainstorm_session': [
            ('ResearchAgent', 'Research and validate brainstorm ideas'),
            ('ContentStrategyAgent', 'Prioritize and plan implementation'),
            ('TechnicalDocumentAgent', 'Create technical specification'),
        ],
        'conversation': [
            ('ResearchAgent', 'Research conversation conclusions'),
            ('ContentWriterAgent', 'Summarize conversation outcomes'),
        ],
    }

    # Agent name normalization map (display name -> system name)
    AGENT_NAME_MAP = {
        'resume optimizer ai': 'ResumeOptimizerAgent',
        'resume optimizer': 'ResumeOptimizerAgent',
        'hidden job market explorer': 'HiddenJobMarketAgent',
        'arbitragedetector': 'ArbitrageDetectorAgent',
        'arbitrage detector': 'ArbitrageDetectorAgent',
        'seo content optimizer': 'SEOContentOptimizerAgent',
        'seo optimizer': 'SEOContentOptimizerAgent',
        'research agent': 'ResearchAgent',
        'content writer': 'ContentWriterAgent',
        'content strategy': 'ContentStrategyAgent',
        'technical document': 'TechnicalDocumentAgent',
        'market intelligence': 'MarketIntelligenceAgent',
        'trend analysis': 'TrendAnalysisAgent',
    }

    def __init__(self):
        self._orchestration_engine = None

    @property
    def orchestration_engine(self):
        """Lazy-load orchestration engine."""
        if self._orchestration_engine is None:
            from core.services.orchestration_engine import orchestration_engine
            self._orchestration_engine = orchestration_engine
        return self._orchestration_engine

    def execute_session(
        self,
        session,
        user=None,
        async_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a completed HiveMind session through the full pipeline.

        Session 866: Enhanced to parse DecisionSummary and create Initiatives.

        Args:
            session: HiveMindSession instance (must have synthesis)
            user: User triggering execution (defaults to system user)
            async_mode: Run orchestration in background (default True)

        Returns:
            Dict with project, initiative, workflow, and execution details
        """
        # Validate session has synthesis
        if not session.synthesis:
            raise ValueError(
                f"Session must have synthesis to execute. Session ID: {session.id}"
            )

        # Validate session is completed
        if session.status != 'completed':
            raise ValueError(
                f"Session must be completed to execute. Current status: {session.status}"
            )

        # Get user for ownership
        if user is None:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.filter(is_superuser=True).first()
                if not user:
                    user = User.objects.first()
            except Exception as e:
                logger.error(f"Could not determine user for session execution: {e}")
                raise ValueError("No user available for session execution")

        logger.info(f"Executing HiveMind session: {session.id}")

        try:
            with transaction.atomic():
                # Session 866: Parse DecisionSummary for structured extraction
                decision_summary = self._parse_decision_summary(session.synthesis)
                logger.info(f"Parsed DecisionSummary: {bool(decision_summary)}")

                # Step 1: Create project from session
                project = self._create_project_from_session(session, user)
                logger.info(f"Created project: {project.project_name} (ID: {project.id})")

                # Session 866: Create Initiative if Proposed Feature found
                initiative = None
                if decision_summary.get('proposed_feature'):
                    initiative = self._create_initiative_from_feature(
                        decision_summary['proposed_feature'],
                        session,
                        user
                    )
                    logger.info(f"Created initiative: {initiative.name} (ID: {initiative.id})")

                # Session 866: Create workflow from Next Steps or fallback to template
                next_steps = decision_summary.get('next_steps', [])
                if next_steps:
                    workflow = self._create_workflow_from_next_steps(
                        next_steps, session, project, initiative, user
                    )
                    logger.info(f"Created workflow from Next Steps: {workflow.name}")
                else:
                    workflow = self._create_workflow_from_session(session, project, user)
                    logger.info(f"Created workflow from template: {workflow.name}")

                # Step 3: Link session to project
                session.project = project
                session.save(update_fields=['project'])

                # Step 4: Execute workflow via orchestration
                execution = self.orchestration_engine.execute_workflow(
                    workflow=workflow,
                    user=user,
                    input_data={
                        'session_id': str(session.id),
                        'question': session.question,
                        'synthesis': session.synthesis,
                        'synthesis_summary': session.synthesis_summary,
                        'session_mode': session.session_mode,
                        'contribution_count': session.contribution_count,
                        'project_id': str(project.id),
                        'initiative_id': str(initiative.id) if initiative else None,
                        'decision_summary': decision_summary,
                    },
                    async_mode=async_mode
                )
                logger.info(f"Started orchestration execution: {execution.id}")

                return {
                    'success': True,
                    'session_id': str(session.id),
                    'project_id': str(project.id),
                    'initiative_id': str(initiative.id) if initiative else None,
                    'workflow_id': str(workflow.id),
                    'execution_id': str(execution.id),
                    'decision_summary_found': bool(decision_summary),
                    'next_steps_count': len(next_steps),
                    'message': f"HiveMind session is now being executed",
                }

        except Exception as e:
            logger.error(f"Failed to execute HiveMind session {session.id}: {e}")
            return {
                'success': False,
                'session_id': str(session.id),
                'error': str(e),
            }

    def _parse_decision_summary(self, synthesis: str) -> Dict[str, Any]:
        """
        Session 866: Parse DecisionSummary from synthesis text.

        Extracts:
        - insights: List of key insights
        - proposed_feature: Dict with name, inputs, outputs, integration
        - next_steps: List of dicts with agent and task

        Returns:
            Dict with parsed components or empty dict if not found
        """
        if not synthesis:
            return {}

        result = {
            'insights': [],
            'proposed_feature': None,
            'next_steps': [],
        }

        # Find DecisionSummary section
        decision_match = re.search(
            r'(?:===\s*)?DecisionSummary(?:\s*===)?\s*\n(.*?)(?:\n\n\n|\Z|(?=\n===))',
            synthesis,
            re.DOTALL | re.IGNORECASE
        )

        if not decision_match:
            # Try alternative format: "## Decision Summary" or similar
            decision_match = re.search(
                r'##?\s*Decision\s*(?:Summary|Gate)\s*\n(.*?)(?:\n##|\Z)',
                synthesis,
                re.DOTALL | re.IGNORECASE
            )

        if not decision_match:
            logger.debug("No DecisionSummary section found in synthesis")
            return result

        decision_text = decision_match.group(1)

        # Extract Insights
        insights_match = re.search(
            r'Insights?:\s*\n((?:\d+\.\s+.+\n?)+)',
            decision_text,
            re.IGNORECASE
        )
        if insights_match:
            insights_text = insights_match.group(1)
            # Parse numbered insights
            result['insights'] = re.findall(r'\d+\.\s+(.+?)(?=\n\d+\.|\Z)', insights_text, re.DOTALL)
            result['insights'] = [i.strip() for i in result['insights'] if i.strip()]

        # Extract Proposed Feature
        feature_match = re.search(
            r'Proposed\s+Feature:\s*\n(.*?)(?=\nNext\s+Steps?:|\Z)',
            decision_text,
            re.DOTALL | re.IGNORECASE
        )
        if feature_match:
            feature_text = feature_match.group(1)
            result['proposed_feature'] = self._extract_proposed_feature(feature_text)

        # Extract Next Steps
        next_steps_match = re.search(
            r'Next\s+Steps?:\s*\n((?:\d+\.\s+.+\n?)+)',
            decision_text,
            re.IGNORECASE
        )
        if next_steps_match:
            next_steps_text = next_steps_match.group(1)
            result['next_steps'] = self._extract_next_steps(next_steps_text)

        return result

    def _extract_proposed_feature(self, feature_text: str) -> Optional[Dict[str, Any]]:
        """
        Session 866: Extract Proposed Feature details from text.

        Parses format like:
        - Name: Persona Synthesis Engine
        - Inputs: Seed community posts, expanded scrapes...
        - Outputs: 3-5 validated persona cards...
        - Where it plugs into the system: Persona synthesis dashboard...
        """
        if not feature_text:
            return None

        feature = {
            'name': None,
            'inputs': [],
            'outputs': [],
            'integration_points': [],
            'raw_text': feature_text.strip()[:1000],
        }

        # Extract name
        name_match = re.search(r'-?\s*Name:\s*(.+?)(?:\n|$)', feature_text, re.IGNORECASE)
        if name_match:
            # Clean up name - remove parenthetical aliases
            name = name_match.group(1).strip()
            name = re.sub(r'\s*\(.*?\)\s*$', '', name)
            feature['name'] = name

        # Extract inputs
        inputs_match = re.search(
            r'-?\s*Inputs?:\s*(.+?)(?=\n-?\s*(?:Outputs?|Where|$))',
            feature_text,
            re.DOTALL | re.IGNORECASE
        )
        if inputs_match:
            inputs_text = inputs_match.group(1)
            # Split on commas or newlines
            feature['inputs'] = [
                i.strip() for i in re.split(r'[,\n]', inputs_text)
                if i.strip() and len(i.strip()) > 3
            ]

        # Extract outputs
        outputs_match = re.search(
            r'-?\s*Outputs?:\s*(.+?)(?=\n-?\s*(?:Where|Integration|$))',
            feature_text,
            re.DOTALL | re.IGNORECASE
        )
        if outputs_match:
            outputs_text = outputs_match.group(1)
            feature['outputs'] = [
                o.strip() for o in re.split(r'[,\n]', outputs_text)
                if o.strip() and len(o.strip()) > 3
            ]

        # Extract integration points
        integration_match = re.search(
            r'-?\s*(?:Where it plugs into the system|Integration\s*(?:Points?)?|System\s*Integration):\s*(.+?)(?=\n\n|\Z)',
            feature_text,
            re.DOTALL | re.IGNORECASE
        )
        if integration_match:
            integration_text = integration_match.group(1)
            feature['integration_points'] = [
                p.strip() for p in re.split(r'[,\n]', integration_text)
                if p.strip() and len(p.strip()) > 3
            ]

        # Return None if no name found
        if not feature['name']:
            return None

        return feature

    def _extract_next_steps(self, next_steps_text: str) -> List[Dict[str, Any]]:
        """
        Session 866: Extract Next Steps with agent assignments.

        Parses format like:
        1. Resume Optimizer AI: Build the ATS keyword mapping module...
        2. Hidden Job Market Explorer: Expand the dataset...
        """
        if not next_steps_text:
            return []

        steps = []

        # Parse numbered steps with agent: task format
        step_pattern = r'\d+\.\s+([^:]+?):\s*(.+?)(?=\n\d+\.|\Z)'
        matches = re.findall(step_pattern, next_steps_text, re.DOTALL)

        for agent_name, task in matches:
            agent_name = agent_name.strip()
            task = task.strip()

            # Normalize agent name
            normalized_agent = self._normalize_agent_name(agent_name)

            steps.append({
                'agent_display_name': agent_name,
                'agent_system_name': normalized_agent,
                'task': task,
            })

        return steps

    def _normalize_agent_name(self, display_name: str) -> str:
        """
        Session 866: Normalize display agent name to system agent name.

        Converts names like "Resume Optimizer AI" to "ResumeOptimizerAgent"
        """
        # Clean up the name
        clean_name = display_name.lower().strip()
        clean_name = re.sub(r'\s+ai$', '', clean_name)  # Remove trailing "AI"
        clean_name = re.sub(r'\s+agent$', '', clean_name)  # Remove trailing "Agent"

        # Check mapping
        if clean_name in self.AGENT_NAME_MAP:
            return self.AGENT_NAME_MAP[clean_name]

        # Try to construct agent name from display name
        # "Resume Optimizer" -> "ResumeOptimizerAgent"
        words = display_name.split()
        # Remove "AI" and "Agent" from words
        words = [w for w in words if w.lower() not in ('ai', 'agent')]
        if words:
            camel_case = ''.join(w.capitalize() for w in words)
            return f"{camel_case}Agent"

        # Fallback to ResearchAgent
        return 'ResearchAgent'

    def _create_initiative_from_feature(
        self,
        proposed_feature: Dict[str, Any],
        session,
        user,
        bypass_circuit_breaker: bool = False
    ) -> 'Initiative':
        """
        Session 866: Create an Initiative from the Proposed Feature.

        The Initiative will have the 5-stage pipeline for development:
        1. Research Brief
        2. Prototype Plan
        3. Evaluation
        4. Tech Design
        5. Pilot Execution
        """
        from core.models_document_registry import Initiative, InitiativeStage
        from core.services.initiative_title_generator import generate_initiative_title

        # Session 884: Circuit breaker check
        from core.services.initiative_circuit_breaker import can_create_initiative
        if not can_create_initiative(bypass_check=bypass_circuit_breaker):
            raise ValueError("Initiative creation paused by circuit breaker - backlog too high")

        # Session 905: Generate clean title from proposed feature
        # Use the extracted name if valid, otherwise generate from content
        raw_name = proposed_feature.get('name')
        raw_text = proposed_feature.get('raw_text', '')
        question = session.question if session.question else ''

        initiative_name = generate_initiative_title(
            content=raw_text or raw_name or '',
            topic_hint=raw_name or question,
            max_length=80,
            use_llm=True
        )

        # Dedup check: reuse existing similar initiative instead of creating duplicate
        from core.services.initiative_circuit_breaker import find_similar_initiative
        existing = find_similar_initiative(initiative_name)
        if existing:
            logger.info(f"[hivemind] Reusing similar initiative '{existing.name}' instead of creating duplicate")
            return existing

        # Create the initiative
        # Session 913: Include signal_cluster and auto_topic from HiveMind session
        initiative = Initiative.objects.create(
            name=initiative_name,
            description=f"""
Initiative created from HiveMind brainstorm session.

## Source
- Session ID: {session.id}
- Question: {session.question}

## Proposed Feature
{proposed_feature.get('raw_text', '')}

## Inputs
{chr(10).join('- ' + i for i in proposed_feature.get('inputs', [])[:10])}

## Outputs
{chr(10).join('- ' + o for o in proposed_feature.get('outputs', [])[:10])}

## Integration Points
{chr(10).join('- ' + p for p in proposed_feature.get('integration_points', [])[:10])}
            """.strip(),
            status='TRIAGE',  # Session 994: Auto-created → TRIAGE, not ACTIVE
            current_stage=1,
            created_by=f"HiveMind:{str(session.id)[:8]}",
            parent_topic=session.question[:200] if session.question else '',
            source_decision_id=session.id,
            # Session 913: Link to Signal Intelligence for Origin & Trigger
            signal_cluster=getattr(session, 'signal_cluster', None),
            auto_topic=getattr(session, 'auto_topic', None),
        )

        # Session 996: Auto-assign owner
        from core.services.initiative_integration_service import InitiativeIntegrationService
        InitiativeIntegrationService()._auto_assign_owner(initiative)

        # Create the 5 stages in PENDING status
        stage_names = {
            1: 'Research Brief',
            2: 'Prototype Plan',
            3: 'Evaluation',
            4: 'Tech Design',
            5: 'Pilot Execution',
        }

        for stage_num, stage_name in stage_names.items():
            InitiativeStage.objects.create(
                initiative=initiative,
                stage=stage_num,
                status='PENDING',
                notes=f"Auto-created for {initiative_name} from HiveMind session",
            )

        logger.info(
            f"Created Initiative '{initiative.name}' with 5 stages "
            f"from HiveMind session {session.id}"
        )

        # Session 915: Trigger Stage 1 document generation
        try:
            from core.tasks import generate_initiative_stage_document
            task = generate_initiative_stage_document.delay(str(initiative.id), 1)
            logger.info(f"[Session 915] Triggered Stage 1 document generation: task {task.id}")
        except Exception as e:
            logger.warning(f"[Session 915] Could not trigger Stage 1 generation: {e}")

        return initiative

    def _create_workflow_from_next_steps(
        self,
        next_steps: List[Dict[str, Any]],
        session,
        project,
        initiative,
        user
    ) -> 'CustomWorkflow':
        """
        Session 866: Create workflow from extracted Next Steps.

        Each Next Step becomes a workflow step assigned to the specified agent.
        """
        from core.models_unified_system import CustomWorkflow, CustomWorkflowStep

        # Create workflow
        question_slug = slugify(session.question[:30]) if session.question else 'hivemind'
        workflow = CustomWorkflow.objects.create(
            created_by=user,
            name=f"HiveMind Tasks: {session.question[:60]}",
            slug=f"hivemind-tasks-{question_slug}-{str(session.id)[:8]}",
            description=f"""
Workflow generated from HiveMind session Next Steps.

Session: {session.id}
Question: {session.question}

This workflow executes the specific agent tasks identified in the brainstorm:
{chr(10).join(f"- {s['agent_display_name']}: {s['task'][:80]}..." for s in next_steps)}
            """.strip(),
            content_type='hivemind_execution',
            category='auto_generated',
            status='active',
            execution_mode='sequential',
            max_retries=2,
            timeout_seconds=7200,  # 2 hours for multi-agent workflow
            require_approval_on_error=True,
            config={
                'source': 'hivemind_execution_pipeline',
                'enhanced': True,  # Session 866 flag
                'session_id': str(session.id),
                'project_id': str(project.id),
                'initiative_id': str(initiative.id) if initiative else None,
                'session_mode': session.session_mode,
                'next_steps_count': len(next_steps),
            }
        )

        # Create workflow steps from Next Steps
        for order, step in enumerate(next_steps, start=1):
            agent_name = step['agent_system_name']
            task = step['task']
            display_name = step['agent_display_name']

            CustomWorkflowStep.objects.create(
                workflow=workflow,
                order=order,
                name=f"Step {order}: {display_name}",
                description=f"""
Task assigned to {display_name} from HiveMind brainstorm:

{task}

Context from HiveMind Session:
- Question: {session.question[:300]}
- Mode: {session.session_mode}
- Initiative: {initiative.name if initiative else 'N/A'}
                """.strip(),
                agent=agent_name,
                config={
                    'hivemind_context': {
                        'question': session.question,
                        'synthesis_summary': session.synthesis_summary,
                        'mode': session.session_mode,
                        'contribution_count': session.contribution_count,
                        'assigned_task': task,
                        'original_agent_name': display_name,
                    },
                    'initiative_id': str(initiative.id) if initiative else None,
                },
                timeout_seconds=1200,  # 20 minutes per agent task
                requires_approval=False,
            )

        logger.info(
            f"Created workflow with {len(next_steps)} steps from Next Steps "
            f"for session {session.id}"
        )

        return workflow

    def _create_project_from_session(self, session, user) -> 'PartnershipProject':
        """Create a PartnershipProject from HiveMind session."""
        from core.models_partnership import PartnershipProject

        # Determine project type based on session mode
        project_type = 'research' if session.session_mode == 'hive_mind' else 'content_creation'

        # Create descriptive project name
        question_preview = session.question[:80] if session.question else 'HiveMind Session'

        project = PartnershipProject.objects.create(
            user=user,
            project_name=f"HiveMind: {question_preview}",
            project_type=project_type,
            description=f"""
Project created from HiveMind collective intelligence session.

## Question/Topic
{session.question}

## Context
{session.context or 'N/A'}

## Collective Synthesis
{session.synthesis}

## Session Summary
{session.synthesis_summary or 'N/A'}

## Session Stats
- Mode: {session.session_mode}
- Participants: {len(session.participant_ids)}
- Contributions: {session.contribution_count}
- Thinking Time: {session.total_thinking_time:.1f}s
            """.strip(),
            status='active',
            ai_contribution_percent=90,  # HiveMind is heavily AI-driven
            human_contribution_percent=10,
        )

        return project

    def _create_workflow_from_session(self, session, project, user) -> 'CustomWorkflow':
        """Create a CustomWorkflow based on session mode (fallback template)."""
        from core.models_unified_system import CustomWorkflow, CustomWorkflowStep

        # Get workflow template for this session mode
        workflow_template = self.SESSION_MODE_WORKFLOWS.get(
            session.session_mode,
            self.SESSION_MODE_WORKFLOWS['hive_mind']  # Default template
        )

        # Create workflow
        question_slug = slugify(session.question[:30]) if session.question else 'hivemind'
        workflow = CustomWorkflow.objects.create(
            created_by=user,
            name=f"HiveMind Execution: {session.question[:80]}",
            slug=f"hivemind-{question_slug}-{str(session.id)[:8]}",
            description=f"Workflow generated from HiveMind session synthesis",
            content_type='hivemind_execution',
            category='auto_generated',
            status='active',
            execution_mode='sequential',
            max_retries=2,
            timeout_seconds=3600,  # 1 hour
            require_approval_on_error=True,
            config={
                'source': 'hivemind_execution_pipeline',
                'session_id': str(session.id),
                'project_id': str(project.id),
                'session_mode': session.session_mode,
            }
        )

        # Create workflow steps
        for order, (agent_name, step_description) in enumerate(workflow_template, start=1):
            CustomWorkflowStep.objects.create(
                workflow=workflow,
                order=order,
                name=f"Step {order}: {step_description}",
                description=f"""
{step_description}

Context from HiveMind Session:
- Question: {session.question[:300]}...
- Synthesis: {session.synthesis[:500]}...
- Mode: {session.session_mode}
                """.strip(),
                agent=agent_name,
                config={
                    'hivemind_context': {
                        'question': session.question,
                        'synthesis': session.synthesis,
                        'summary': session.synthesis_summary,
                        'mode': session.session_mode,
                        'contribution_count': session.contribution_count,
                    }
                },
                timeout_seconds=600,  # 10 minutes per step
                requires_approval=False,
            )

        return workflow

    def process_completed_sessions(
        self,
        limit: int = 5,
        user=None
    ) -> List[Dict[str, Any]]:
        """
        Process completed HiveMind sessions that haven't been executed yet.

        Session 866: Now includes AgentConversations with brainstorm_session type.

        Args:
            limit: Maximum number of sessions to process
            user: User for project/workflow ownership

        Returns:
            List of execution results
        """
        from core.models_unified_system import HiveMindSession

        # Find completed sessions with synthesis that haven't been linked to projects
        completed_sessions = HiveMindSession.objects.filter(
            status='completed',
            project__isnull=True,  # Not yet linked to a project
        ).exclude(
            synthesis=''  # Must have synthesis
        ).order_by('-contribution_count', '-created_at')[:limit]

        results = []
        for session in completed_sessions:
            result = self.execute_session(session, user=user)
            results.append(result)

            if result['success']:
                logger.info(f"Successfully executed HiveMind session: {session.id}")
            else:
                logger.warning(
                    f"Failed to execute HiveMind session: {session.id} - {result.get('error')}"
                )

        return results

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about HiveMind execution pipeline."""
        from core.models_unified_system import HiveMindSession
        from core.models_orchestration import OrchestrationExecution
        from core.models_partnership import PartnershipProject
        from core.models_document_registry import Initiative

        total_sessions = HiveMindSession.objects.count()
        completed_sessions = HiveMindSession.objects.filter(status='completed').count()
        sessions_with_synthesis = HiveMindSession.objects.exclude(synthesis='').count()
        sessions_with_projects = HiveMindSession.objects.filter(
            status='completed',
            project__isnull=False
        ).count()

        # Get orchestration stats for HiveMind executions
        hivemind_executions = OrchestrationExecution.objects.filter(
            workflow__category='auto_generated',
            workflow__config__source='hivemind_execution_pipeline'
        ).count()

        # Session 866: Count enhanced executions and initiatives
        enhanced_executions = OrchestrationExecution.objects.filter(
            workflow__category='auto_generated',
            workflow__config__enhanced=True
        ).count()

        hivemind_initiatives = Initiative.objects.filter(
            created_by__startswith='HiveMind:'
        ).count()

        return {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'sessions_with_synthesis': sessions_with_synthesis,
            'sessions_with_projects': sessions_with_projects,
            'sessions_executed': hivemind_executions,
            'enhanced_executions': enhanced_executions,  # Session 866
            'initiatives_created': hivemind_initiatives,  # Session 866
            'pending_execution': sessions_with_synthesis - sessions_with_projects,
            'execution_rate': (
                (sessions_with_projects / sessions_with_synthesis * 100)
                if sessions_with_synthesis > 0 else 0
            ),
        }


# Singleton instance
hivemind_execution_pipeline = HiveMindExecutionPipeline()


def get_hivemind_execution_pipeline() -> HiveMindExecutionPipeline:
    """Get the singleton HiveMind execution pipeline instance."""
    return hivemind_execution_pipeline
