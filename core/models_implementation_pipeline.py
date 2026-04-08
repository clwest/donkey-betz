"""
Implementation Pipeline Models
Session 690: Turn completed pilots into actual system changes

This module closes the loop between governance and execution:

    Pilot Completed (success) → Implementation Pipeline → Actual Changes

Implementation Types:
- AGENT_UPDATE: Route to agents for behavior/config changes
- CODE_GENERATION: Route to FullStackDeveloperAgent for new code
- WORKFLOW_UPDATE: Create/modify workflow templates
- PROMPT_UPDATE: Update central prompt registry
- TASK_CREATION: Create human task for manual implementation
- CONFIG_UPDATE: Update system configuration
"""

import uuid
import logging
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class ImplementationType(models.TextChoices):
    """Types of implementations that can be executed."""
    AGENT_UPDATE = 'agent_update', 'Agent Behavior Update'
    CODE_GENERATION = 'code_generation', 'Code Generation'
    WORKFLOW_UPDATE = 'workflow_update', 'Workflow Update'
    PROMPT_UPDATE = 'prompt_update', 'Prompt Update'
    CONFIG_UPDATE = 'config_update', 'Configuration Update'
    TASK_CREATION = 'task_creation', 'Human Task Creation'
    EXPERIMENT_SETUP = 'experiment_setup', 'Experiment Setup'


class ImplementationStatus(models.TextChoices):
    """Status of an implementation."""
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    REQUIRES_HUMAN = 'requires_human', 'Requires Human Action'
    SKIPPED = 'skipped', 'Skipped'


class PilotImplementation(models.Model):
    """
    Tracks the implementation of a completed pilot's recommendations.

    This is the missing link between "pilot succeeded" and "changes applied".
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the completed pilot
    pilot = models.OneToOneField(
        'core.PilotExecution',
        on_delete=models.CASCADE,
        related_name='implementation'
    )

    # Implementation details
    implementation_type = models.CharField(
        max_length=50,
        choices=ImplementationType.choices,
        default=ImplementationType.TASK_CREATION
    )
    status = models.CharField(
        max_length=50,
        choices=ImplementationStatus.choices,
        default=ImplementationStatus.PENDING
    )

    # What was implemented
    target_description = models.TextField(
        help_text="Human-readable description of what will be/was implemented"
    )
    implementation_plan = models.JSONField(
        default=dict,
        help_text="Structured plan for implementation"
    )

    # Execution details
    executed_by = models.CharField(
        max_length=255,
        blank=True,
        help_text="Agent or human who executed the implementation"
    )
    execution_result = models.JSONField(
        default=dict,
        help_text="Results of the implementation execution"
    )

    # Files/artifacts created or modified
    artifacts = models.JSONField(
        default=list,
        help_text="List of files, configs, or other artifacts created/modified"
    )

    # Error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pilot Implementation'
        verbose_name_plural = 'Pilot Implementations'

    def __str__(self):
        return f"Implementation: {self.pilot.name[:50]} [{self.status}]"

    def start_implementation(self):
        """Mark implementation as started."""
        self.status = ImplementationStatus.IN_PROGRESS
        self.started_at = timezone.now()
        self.save()

    def complete_implementation(self, result: dict, artifacts: list = None):
        """Mark implementation as completed with results."""
        self.status = ImplementationStatus.COMPLETED
        self.completed_at = timezone.now()
        self.execution_result = result
        if artifacts:
            self.artifacts = artifacts
        self.save()

        logger.info(f"Implementation completed: {self.pilot.name}")

    def fail_implementation(self, error: str):
        """Mark implementation as failed."""
        self.status = ImplementationStatus.FAILED
        self.error_message = error
        self.retry_count += 1
        self.save()

        logger.error(f"Implementation failed: {self.pilot.name} - {error}")

    def mark_requires_human(self, reason: str):
        """Mark implementation as requiring human action."""
        self.status = ImplementationStatus.REQUIRES_HUMAN
        self.execution_result = {'requires_human_reason': reason}
        self.save()

    @classmethod
    def create_from_pilot(cls, pilot) -> 'PilotImplementation':
        """
        Create an implementation record from a completed pilot.

        Analyzes the pilot's decision to determine:
        1. Implementation type (auto vs human)
        2. Target description
        3. Implementation plan
        """
        from core.models_pilot_readiness import PilotReadinessGate

        gate = pilot.gate
        if not gate or not gate.decision:
            raise ValueError(f"Pilot {pilot.id} has no linked decision")

        decision = gate.decision

        # Determine implementation type based on decision characteristics
        impl_type = cls._determine_implementation_type(decision)

        # Build implementation plan
        plan = cls._build_implementation_plan(decision, impl_type)

        # Create target description
        target_desc = decision.suggested_feature or decision.recommended_stance or f"Implement {decision.topic}"

        implementation = cls.objects.create(
            pilot=pilot,
            implementation_type=impl_type,
            target_description=target_desc[:1000],
            implementation_plan=plan
        )

        logger.info(f"Created implementation for pilot {pilot.name}: type={impl_type}")
        return implementation

    @staticmethod
    def _determine_implementation_type(decision) -> str:
        """
        Determine the best implementation type based on decision characteristics.

        Routing logic:
        - agents + experiment/policy → AGENT_UPDATE
        - workflow/pipeline + any → WORKFLOW_UPDATE
        - prompting + any → PROMPT_UPDATE
        - infrastructure + architecture → TASK_CREATION (needs human)
        - product + any → CODE_GENERATION or TASK_CREATION
        - security + any → TASK_CREATION (always needs human review)
        """
        impact = decision.impact_area
        dtype = decision.decision_type

        # Security always needs human review
        if impact == 'security':
            return ImplementationType.TASK_CREATION

        # Agent behavior changes
        if impact == 'agents' and dtype in ['experiment', 'policy', 'guideline']:
            return ImplementationType.AGENT_UPDATE

        # Workflow/pipeline changes
        if impact == 'workflow' or dtype == 'pipeline':
            return ImplementationType.WORKFLOW_UPDATE

        # Prompting strategy updates
        if impact == 'prompting':
            return ImplementationType.PROMPT_UPDATE

        # Experiments get special setup
        if dtype == 'experiment':
            return ImplementationType.EXPERIMENT_SETUP

        # Product features - try code generation for smaller features
        if impact == 'product' and dtype in ['product', 'guideline']:
            return ImplementationType.CODE_GENERATION

        # Infrastructure/architecture needs human
        if impact == 'infrastructure' or dtype == 'architecture':
            return ImplementationType.TASK_CREATION

        # Default to task creation for human review
        return ImplementationType.TASK_CREATION

    @staticmethod
    def _build_implementation_plan(decision, impl_type: str) -> dict:
        """Build a structured implementation plan based on decision and type."""
        plan = {
            'decision_type': decision.decision_type,
            'impact_area': decision.impact_area,
            'key_insights': decision.key_insights or [],
            'recommended_action': decision.recommended_stance,
            'suggested_feature': decision.suggested_feature,
            'rationale': decision.rationale,
            'steps': []
        }

        # Add type-specific steps
        if impl_type == ImplementationType.AGENT_UPDATE:
            plan['steps'] = [
                'Identify target agent(s) based on impact area',
                'Analyze current agent behavior/prompts',
                'Generate updated configuration or prompts',
                'Apply changes to agent',
                'Verify agent behavior change'
            ]
            plan['target_agents'] = _get_target_agents(decision.impact_area)

        elif impl_type == ImplementationType.CODE_GENERATION:
            plan['steps'] = [
                'Analyze feature requirements from suggested_feature',
                'Route to FullStackDeveloperAgent',
                'Generate implementation code',
                'Create pull request or apply changes',
                'Run tests to verify'
            ]

        elif impl_type == ImplementationType.WORKFLOW_UPDATE:
            plan['steps'] = [
                'Parse workflow requirements',
                'Create or update workflow template',
                'Configure workflow steps',
                'Test workflow execution',
                'Activate workflow'
            ]

        elif impl_type == ImplementationType.PROMPT_UPDATE:
            plan['steps'] = [
                'Identify affected prompts',
                'Generate updated prompt text',
                'Update prompt registry',
                'Test prompt effectiveness'
            ]

        elif impl_type == ImplementationType.EXPERIMENT_SETUP:
            plan['steps'] = [
                'Define experiment parameters',
                'Create experiment record',
                'Configure A/B testing if applicable',
                'Set up metrics tracking',
                'Start experiment'
            ]

        elif impl_type == ImplementationType.TASK_CREATION:
            plan['steps'] = [
                'Create actionable task for human review',
                'Include all decision context',
                'Set priority based on impact',
                'Notify relevant team members'
            ]

        return plan


def _get_target_agents(impact_area: str) -> list:
    """Get relevant agents for an impact area."""
    agent_mapping = {
        'agents': ['ThinkingAgent', 'WorkflowAgent'],
        'workflow': ['WorkflowAgent', 'WorkflowOrchestrationAgent'],
        'image': ['ImageAgent', 'ImageEditingAgent'],
        'video': ['VideoAgent', 'VideoEditingAgent'],
        'audio': ['AudioAgent'],
        'research': ['ResearchAgent', 'TrendAnalysisAgent'],
        'prompting': ['ThinkingAgent'],
        'product': ['FullStackDeveloperAgent', 'ContentStrategyAgent'],
        'spider': ['ResearchAgent'],
        'legal': ['LegalDocDrafterAgent'],
        'memory': ['ThinkingAgent'],
    }
    return agent_mapping.get(impact_area, ['ThinkingAgent'])


class ImplementationAction(models.Model):
    """
    Individual actions taken during an implementation.

    Provides audit trail of what was actually done.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    implementation = models.ForeignKey(
        PilotImplementation,
        on_delete=models.CASCADE,
        related_name='actions'
    )

    # Action details
    action_type = models.CharField(max_length=100)
    description = models.TextField()

    # What agent/service performed this
    performed_by = models.CharField(max_length=255)

    # Result
    success = models.BooleanField(default=False)
    result_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)

    # Artifacts
    files_created = models.JSONField(default=list)
    files_modified = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        status = "OK" if self.success else "FAIL"
        return f"{self.action_type} by {self.performed_by} [{status}]"
