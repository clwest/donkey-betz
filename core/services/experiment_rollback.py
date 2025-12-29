"""
Session 600: Experiment Rollback Service

Handles automatic rollback when experiments receive FAIL outcome classification.
Generates remediation checklists and tracks remediation progress.

Rollback Flow:
1. Experiment is halted (auto or manual) → outcome_classification = 'fail'
2. RollbackService triggered → generates rollback plan
3. Discord notification sent with remediation steps
4. Remediation progress tracked until complete
"""

import logging
from datetime import datetime
from typing import Optional
from django.utils import timezone

logger = logging.getLogger(__name__)


class ExperimentRollbackService:
    """
    Handles rollback operations for failed experiments.

    When an experiment receives FAIL outcome:
    1. Analyzes the halt reason to determine rollback scope
    2. Generates a remediation checklist
    3. Tracks remediation progress
    4. Sends Discord notifications
    """

    # Remediation templates based on halt condition types
    REMEDIATION_TEMPLATES = {
        'bias_detection_rate': {
            'title': 'Bias Detection Threshold Exceeded',
            'severity': 'high',
            'steps': [
                {'id': 1, 'action': 'Review flagged outputs for bias patterns', 'required': True},
                {'id': 2, 'action': 'Identify root cause (prompt, data, or model)', 'required': True},
                {'id': 3, 'action': 'Implement bias mitigation measures', 'required': True},
                {'id': 4, 'action': 'Update content guidelines if needed', 'required': False},
                {'id': 5, 'action': 'Re-run affected outputs with fixes', 'required': True},
                {'id': 6, 'action': 'Verify bias rate below threshold', 'required': True},
            ]
        },
        'user_trust_index': {
            'title': 'User Trust Index Below Minimum',
            'severity': 'high',
            'steps': [
                {'id': 1, 'action': 'Analyze user feedback patterns', 'required': True},
                {'id': 2, 'action': 'Identify quality issues causing low ratings', 'required': True},
                {'id': 3, 'action': 'Review recent changes that may have caused drop', 'required': True},
                {'id': 4, 'action': 'Implement quality improvements', 'required': True},
                {'id': 5, 'action': 'Communicate with affected users if needed', 'required': False},
                {'id': 6, 'action': 'Monitor trust index recovery', 'required': True},
            ]
        },
        'integrity_anomaly': {
            'title': 'Integrity Anomaly Detected',
            'severity': 'critical',
            'steps': [
                {'id': 1, 'action': 'IMMEDIATE: Stop all related processing', 'required': True},
                {'id': 2, 'action': 'Identify scope of integrity issue', 'required': True},
                {'id': 3, 'action': 'Review system logs for anomaly source', 'required': True},
                {'id': 4, 'action': 'Quarantine affected outputs', 'required': True},
                {'id': 5, 'action': 'Implement integrity safeguards', 'required': True},
                {'id': 6, 'action': 'Conduct post-mortem analysis', 'required': True},
                {'id': 7, 'action': 'Document incident and resolution', 'required': True},
            ]
        },
        'telemetry_kill_switch': {
            'title': 'External Kill Switch Activated',
            'severity': 'critical',
            'steps': [
                {'id': 1, 'action': 'Confirm kill switch source and reason', 'required': True},
                {'id': 2, 'action': 'Document trigger conditions', 'required': True},
                {'id': 3, 'action': 'Assess impact of immediate stop', 'required': True},
                {'id': 4, 'action': 'Coordinate with stakeholders', 'required': True},
                {'id': 5, 'action': 'Develop remediation plan', 'required': True},
                {'id': 6, 'action': 'Get approval for restart', 'required': True},
            ]
        },
        'error_rate': {
            'title': 'Error Rate Threshold Exceeded',
            'severity': 'medium',
            'steps': [
                {'id': 1, 'action': 'Analyze error logs for patterns', 'required': True},
                {'id': 2, 'action': 'Identify root cause of errors', 'required': True},
                {'id': 3, 'action': 'Implement error fixes', 'required': True},
                {'id': 4, 'action': 'Add error handling improvements', 'required': False},
                {'id': 5, 'action': 'Test fixes in staging environment', 'required': True},
                {'id': 6, 'action': 'Verify error rate below threshold', 'required': True},
            ]
        },
        'manual': {
            'title': 'Manual Halt Requested',
            'severity': 'medium',
            'steps': [
                {'id': 1, 'action': 'Review halt reason provided', 'required': True},
                {'id': 2, 'action': 'Assess experiment state at halt', 'required': True},
                {'id': 3, 'action': 'Determine if restart is appropriate', 'required': True},
                {'id': 4, 'action': 'Address issues that caused halt', 'required': True},
                {'id': 5, 'action': 'Document lessons learned', 'required': True},
            ]
        },
        'default': {
            'title': 'Experiment Failed - General Remediation',
            'severity': 'medium',
            'steps': [
                {'id': 1, 'action': 'Review experiment outcome', 'required': True},
                {'id': 2, 'action': 'Identify failure points', 'required': True},
                {'id': 3, 'action': 'Document what went wrong', 'required': True},
                {'id': 4, 'action': 'Propose corrective actions', 'required': True},
                {'id': 5, 'action': 'Decide on retry or abandon', 'required': True},
            ]
        }
    }

    def __init__(self, experiment):
        """
        Initialize with an experiment to process rollback for.

        Args:
            experiment: The Experiment model instance with FAIL outcome
        """
        self.experiment = experiment
        self.pilot = experiment.pilot
        self.decision = experiment.pilot.gate.decision

    def generate_rollback_plan(self) -> dict:
        """
        Generate a rollback plan based on the halt reason.

        Returns:
            dict with rollback plan details including:
                - title: Human-readable title
                - severity: critical/high/medium/low
                - halt_reason: The original reason
                - steps: List of remediation steps
                - estimated_effort: Rough effort estimate
        """
        halt_reason = self.experiment.halt_reason or ''

        # Determine which template to use based on halt reason
        template_key = self._determine_template_key(halt_reason)
        template = self.REMEDIATION_TEMPLATES.get(template_key, self.REMEDIATION_TEMPLATES['default'])

        rollback_plan = {
            'experiment_id': str(self.experiment.id),
            'experiment_name': self.experiment.name,
            'title': template['title'],
            'severity': template['severity'],
            'halt_reason': halt_reason,
            'halted_by': self.experiment.halted_by,
            'halted_at': self.experiment.halted_at.isoformat() if self.experiment.halted_at else None,
            'steps': [
                {
                    **step,
                    'completed': False,
                    'completed_at': None,
                    'notes': ''
                }
                for step in template['steps']
            ],
            'total_steps': len(template['steps']),
            'required_steps': len([s for s in template['steps'] if s['required']]),
            'status': 'pending',
            'created_at': timezone.now().isoformat(),
        }

        return rollback_plan

    def _determine_template_key(self, halt_reason: str) -> str:
        """Determine which remediation template to use based on halt reason."""
        halt_reason_lower = halt_reason.lower()

        if 'bias' in halt_reason_lower:
            return 'bias_detection_rate'
        elif 'trust' in halt_reason_lower:
            return 'user_trust_index'
        elif 'anomaly' in halt_reason_lower or 'integrity' in halt_reason_lower:
            return 'integrity_anomaly'
        elif 'kill' in halt_reason_lower or 'kill-switch' in halt_reason_lower:
            return 'telemetry_kill_switch'
        elif 'error' in halt_reason_lower:
            return 'error_rate'
        elif self.experiment.halted_by == 'manual':
            return 'manual'
        else:
            return 'default'

    def save_rollback_plan(self) -> dict:
        """
        Generate and save rollback plan to experiment metadata.

        Returns:
            The saved rollback plan
        """
        plan = self.generate_rollback_plan()

        # Store in experiment's extracted_metrics field (reusing existing JSONField)
        metrics = self.experiment.extracted_metrics or {}
        metrics['rollback_plan'] = plan
        self.experiment.extracted_metrics = metrics
        self.experiment.save()

        logger.info(f"[Session 600] Saved rollback plan for experiment {self.experiment.id}")

        return plan

    def get_rollback_plan(self) -> Optional[dict]:
        """Get the existing rollback plan if any."""
        metrics = self.experiment.extracted_metrics or {}
        return metrics.get('rollback_plan')

    def update_remediation_step(self, step_id: int, completed: bool, notes: str = '') -> dict:
        """
        Update the completion status of a remediation step.

        Args:
            step_id: The step number to update
            completed: Whether the step is completed
            notes: Optional notes about the completion

        Returns:
            Updated rollback plan
        """
        metrics = self.experiment.extracted_metrics or {}
        plan = metrics.get('rollback_plan')

        if not plan:
            raise ValueError("No rollback plan exists for this experiment")

        # Find and update the step
        for step in plan['steps']:
            if step['id'] == step_id:
                step['completed'] = completed
                step['completed_at'] = timezone.now().isoformat() if completed else None
                step['notes'] = notes
                break

        # Update overall status
        completed_count = len([s for s in plan['steps'] if s['completed']])
        required_completed = len([s for s in plan['steps'] if s['required'] and s['completed']])
        total_required = plan['required_steps']

        if required_completed >= total_required:
            plan['status'] = 'completed'
            plan['completed_at'] = timezone.now().isoformat()
        elif completed_count > 0:
            plan['status'] = 'in_progress'
        else:
            plan['status'] = 'pending'

        plan['completed_steps'] = completed_count
        plan['progress_percent'] = round((completed_count / plan['total_steps']) * 100, 1)

        # Save
        metrics['rollback_plan'] = plan
        self.experiment.extracted_metrics = metrics
        self.experiment.save()

        logger.info(f"[Session 600] Updated remediation step {step_id} for experiment {self.experiment.id}")

        return plan

    def get_remediation_progress(self) -> dict:
        """
        Get the current remediation progress.

        Returns:
            dict with progress details
        """
        plan = self.get_rollback_plan()
        if not plan:
            return {
                'has_plan': False,
                'status': 'no_plan',
                'progress_percent': 0,
            }

        completed_count = len([s for s in plan['steps'] if s['completed']])

        return {
            'has_plan': True,
            'status': plan.get('status', 'pending'),
            'progress_percent': round((completed_count / plan['total_steps']) * 100, 1),
            'completed_steps': completed_count,
            'total_steps': plan['total_steps'],
            'required_remaining': plan['required_steps'] - len([
                s for s in plan['steps'] if s['required'] and s['completed']
            ]),
            'severity': plan['severity'],
        }

    def generate_discord_notification(self) -> str:
        """
        Generate a Discord notification message for the rollback.

        Returns:
            Formatted Discord message
        """
        plan = self.get_rollback_plan() or self.generate_rollback_plan()

        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢',
        }

        steps_text = '\n'.join([
            f"{'✅' if s['completed'] else '⬜'} {s['id']}. {s['action']} {'(required)' if s['required'] else '(optional)'}"
            for s in plan['steps'][:5]  # Show first 5 steps
        ])

        if len(plan['steps']) > 5:
            steps_text += f"\n... and {len(plan['steps']) - 5} more steps"

        message = f"""**{severity_emoji.get(plan['severity'], '⚪')} ROLLBACK REQUIRED: {plan['title']}**

**Experiment:** {plan['experiment_name']}
**Halted by:** {plan['halted_by']}
**Severity:** {plan['severity'].upper()}

**Halt Reason:**
> {plan['halt_reason'][:200]}{'...' if len(plan['halt_reason']) > 200 else ''}

**Remediation Steps:**
{steps_text}

**Required Steps:** {plan['required_steps']} | **Total Steps:** {plan['total_steps']}

_Track progress in the Experiment Tracking Registry UI_
"""
        return message


def trigger_rollback(experiment) -> dict:
    """
    Trigger rollback for a failed experiment.

    This is the main entry point for rollback automation.
    Called when an experiment receives FAIL outcome classification.

    Args:
        experiment: Experiment with outcome_classification = 'fail'

    Returns:
        dict with rollback plan and notification status
    """
    service = ExperimentRollbackService(experiment)

    # Generate and save rollback plan
    plan = service.save_rollback_plan()

    # Generate Discord notification
    discord_message = service.generate_discord_notification()

    # Send Discord notification
    notification_sent = False
    try:
        from core.services.discord_notifications import DiscordNotificationService
        discord = DiscordNotificationService()
        discord.send_to_channel('system-status', discord_message)
        notification_sent = True
        logger.info(f"[Session 600] Sent rollback notification for experiment {experiment.id}")
    except Exception as e:
        logger.warning(f"[Session 600] Failed to send Discord notification: {e}")

    return {
        'success': True,
        'plan': plan,
        'notification_sent': notification_sent,
    }
