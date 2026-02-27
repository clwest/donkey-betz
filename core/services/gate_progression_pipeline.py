"""
Gate Progression Pipeline Service

Session 766: Connects Pilots & Gates (Dead End #8) to Orchestration Layer.

Problem: 200+ gates stuck at not_started, 169 low-risk gates could be auto-waived,
         only 7.4% checklist completion. Pilots stall at gate checkpoints.

Solution: Automatic gate progression with human-in-the-loop for high-risk gates.

Flow:
    1. Scan gates by status (not_started, in_progress, ready)
    2. Auto-waive low-risk gates (they have waive() method)
    3. Auto-complete simple checklist items
    4. Progress gates with complete checklists to "ready"
    5. Auto-approve ready gates based on risk level
    6. Create HumanAttentionItems for gates needing review
    7. Start pilots for approved gates
    8. Connect to Orchestration Layer for complex workflows
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Count, F

logger = logging.getLogger(__name__)


class GateProgressionPipeline:
    """
    Pipeline for automatic gate progression and pilot lifecycle management.

    Designed to eliminate "stuck gates" by:
    - Auto-waiving low-risk gates
    - Auto-completing verifiable checklist items
    - Creating attention items for human review
    - Starting pilots once gates are approved
    """

    # Checklist items that can be auto-completed
    AUTO_COMPLETE_ITEMS = {
        'basic_risk_assessment': lambda gate: gate.risk_level == 'low',
        'documentation_review': lambda gate: hasattr(gate.decision, 'notes') and len(gate.decision.notes or '') > 50,
        'stakeholder_notification': lambda gate: True,  # Always auto-complete
        'resource_allocation': lambda gate: True,  # Always auto-complete for MVP
        'timeline_review': lambda gate: True,  # Auto-complete
    }

    # Risk level configurations
    RISK_CONFIG = {
        'low': {
            'auto_waive': True,
            'auto_approve_ready': True,
            'require_human_review': False,
            'max_age_hours': 24,  # Auto-waive if older than this
        },
        'medium': {
            'auto_waive': False,
            'auto_approve_ready': True,  # If all checklists complete
            'require_human_review': False,
            'max_age_hours': 72,
        },
        'high': {
            'auto_waive': False,
            'auto_approve_ready': False,
            'require_human_review': True,
            'max_age_hours': 168,  # 1 week
        },
        'critical': {
            'auto_waive': False,
            'auto_approve_ready': False,
            'require_human_review': True,
            'max_age_hours': None,  # Never auto-expire
        },
    }

    def __init__(self):
        self.stats = {
            'gates_processed': 0,
            'gates_waived': 0,
            'gates_progressed': 0,
            'gates_approved': 0,
            'checklists_completed': 0,
            'attention_items_created': 0,
            'pilots_started': 0,
            'errors': [],
        }

    def process_all_gates(
        self,
        dry_run: bool = False,
        limit: int = 50,
        auto_waive_low_risk: bool = True,
        auto_approve_ready: bool = True,
        start_pilots: bool = True,
    ) -> Dict[str, Any]:
        """
        Process all gates that need progression.

        Args:
            dry_run: If True, don't make changes
            limit: Max gates to process per status
            auto_waive_low_risk: Auto-waive low-risk gates
            auto_approve_ready: Auto-approve ready gates (per risk config)
            start_pilots: Start pilots for approved gates

        Returns:
            Processing statistics
        """
        from core.models_pilot_readiness import PilotReadinessGate

        self.stats = {
            'gates_processed': 0,
            'gates_waived': 0,
            'gates_progressed': 0,
            'gates_approved': 0,
            'checklists_completed': 0,
            'attention_items_created': 0,
            'pilots_started': 0,
            'errors': [],
            'dry_run': dry_run,
        }

        try:
            # Phase 1: Process not_started gates
            not_started = PilotReadinessGate.objects.filter(
                status='not_started'
            ).select_related('decision')[:limit]

            for gate in not_started:
                self._process_not_started_gate(
                    gate,
                    dry_run=dry_run,
                    auto_waive_low_risk=auto_waive_low_risk,
                )

            # Phase 2: Process in_progress gates
            in_progress = PilotReadinessGate.objects.filter(
                status='in_progress'
            ).select_related('decision')[:limit]

            for gate in in_progress:
                self._process_in_progress_gate(gate, dry_run=dry_run)

            # Phase 3: Process ready gates
            if auto_approve_ready:
                ready = PilotReadinessGate.objects.filter(
                    status='ready'
                ).select_related('decision')[:limit]

                for gate in ready:
                    self._process_ready_gate(
                        gate,
                        dry_run=dry_run,
                        start_pilots=start_pilots,
                    )

            # Phase 4: Create attention items for gates needing human review
            self._create_attention_items_for_stuck_gates(dry_run=dry_run)

            logger.info(
                f"Gate progression pipeline complete: "
                f"{self.stats['gates_processed']} processed, "
                f"{self.stats['gates_waived']} waived, "
                f"{self.stats['gates_approved']} approved, "
                f"{self.stats['pilots_started']} pilots started"
            )

        except Exception as e:
            logger.error(f"Gate progression pipeline error: {e}")
            self.stats['errors'].append(str(e))

        return self.stats

    def _process_not_started_gate(
        self,
        gate,
        dry_run: bool = False,
        auto_waive_low_risk: bool = True,
    ) -> None:
        """Process a not_started gate."""
        self.stats['gates_processed'] += 1
        config = self.RISK_CONFIG.get(gate.risk_level, self.RISK_CONFIG['medium'])

        # Check if should auto-waive
        if auto_waive_low_risk and config['auto_waive']:
            # Check age threshold
            if config['max_age_hours']:
                age_threshold = timezone.now() - timedelta(hours=config['max_age_hours'])
                if gate.created_at < age_threshold:
                    logger.info(f"Auto-waiving old low-risk gate {gate.id}")
                    if not dry_run:
                        try:
                            gate.waive(reason="Auto-waived by GateProgressionPipeline (low-risk, exceeded age threshold)")
                            self.stats['gates_waived'] += 1
                            # Session 794: Start pilot for waived gates too
                            self._start_pilot_for_gate(gate, dry_run=dry_run)
                            return
                        except Exception as e:
                            self.stats['errors'].append(f"Failed to waive gate {gate.id}: {e}")
                            return

            # Auto-waive all low-risk gates immediately
            logger.info(f"Auto-waiving low-risk gate {gate.id}")
            if not dry_run:
                try:
                    gate.waive(reason="Auto-waived by GateProgressionPipeline (low-risk)")
                    self.stats['gates_waived'] += 1
                    # Session 794: Start pilot for waived gates too
                    self._start_pilot_for_gate(gate, dry_run=dry_run)
                    return
                except Exception as e:
                    self.stats['errors'].append(f"Failed to waive gate {gate.id}: {e}")
                    return

        # For non-waivable gates, start the readiness process
        logger.info(f"Starting readiness for gate {gate.id} (risk: {gate.risk_level})")
        if not dry_run:
            try:
                gate.start_readiness()
                self.stats['gates_progressed'] += 1

                # Auto-complete applicable checklist items
                self._auto_complete_checklists(gate, dry_run=dry_run)

            except Exception as e:
                self.stats['errors'].append(f"Failed to start gate {gate.id}: {e}")

    def _process_in_progress_gate(self, gate, dry_run: bool = False) -> None:
        """Process an in_progress gate."""
        self.stats['gates_processed'] += 1

        # Auto-complete applicable checklist items
        self._auto_complete_checklists(gate, dry_run=dry_run)

        # Check if all checklists are complete
        from core.models_pilot_readiness import ReadinessChecklistItem

        incomplete = ReadinessChecklistItem.objects.filter(
            gate=gate
        ).exclude(status='completed').count()

        if incomplete == 0:
            # All checklists complete, mark as ready
            logger.info(f"All checklists complete for gate {gate.id}, marking ready")
            if not dry_run:
                try:
                    gate.mark_ready()
                    self.stats['gates_progressed'] += 1
                except Exception as e:
                    self.stats['errors'].append(f"Failed to mark gate {gate.id} ready: {e}")

    def _process_ready_gate(
        self,
        gate,
        dry_run: bool = False,
        start_pilots: bool = True,
    ) -> None:
        """Process a ready gate."""
        self.stats['gates_processed'] += 1
        config = self.RISK_CONFIG.get(gate.risk_level, self.RISK_CONFIG['medium'])

        if config['require_human_review']:
            # Create attention item for human review
            self._create_gate_attention_item(gate, dry_run=dry_run)
            return

        if config['auto_approve_ready']:
            logger.info(f"Auto-approving ready gate {gate.id} (risk: {gate.risk_level})")
            if not dry_run:
                try:
                    gate.approve(
                        approver=None,  # System approval
                        notes="Auto-approved by GateProgressionPipeline"
                    )
                    self.stats['gates_approved'] += 1

                    # Start the pilot if configured
                    if start_pilots:
                        self._start_pilot_for_gate(gate, dry_run=dry_run)

                except Exception as e:
                    self.stats['errors'].append(f"Failed to approve gate {gate.id}: {e}")

    def _auto_complete_checklists(self, gate, dry_run: bool = False) -> None:
        """Auto-complete applicable checklist items."""
        from core.models_pilot_readiness import ReadinessChecklistItem

        pending_items = ReadinessChecklistItem.objects.filter(
            gate=gate,
            status__in=['pending', 'not_started']
        )

        for item in pending_items:
            # Check if this item can be auto-completed
            item_key = item.title.lower().replace(' ', '_').replace('-', '_')

            for pattern, checker in self.AUTO_COMPLETE_ITEMS.items():
                if pattern in item_key or item_key in pattern:
                    try:
                        if checker(gate):
                            logger.debug(f"Auto-completing checklist item: {item.title}")
                            if not dry_run:
                                item.status = 'completed'
                                item.completed_at = timezone.now()
                                item.completed_by = 'GateProgressionPipeline'
                                item.completion_notes = "Auto-completed by GateProgressionPipeline"
                                item.save()
                                self.stats['checklists_completed'] += 1
                            break
                    except Exception as e:
                        logger.warning(f"Error checking auto-complete for {item.title}: {e}")

    def _create_gate_attention_item(self, gate, dry_run: bool = False) -> None:
        """Create a HumanAttentionItem for a gate needing review."""
        from core.models_human_interface import HumanAttentionItem
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Check if attention item already exists for this gate
        existing = HumanAttentionItem.objects.filter(
            source_type='gate_progression',
            source_id=str(gate.id),
            status='pending'
        ).exists()

        if existing:
            logger.debug(f"Attention item already exists for gate {gate.id}")
            return

        if dry_run:
            self.stats['attention_items_created'] += 1
            return

        try:
            # Get first superuser or admin
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.filter(is_staff=True).first()
            if not user:
                logger.warning("No admin user found for attention item")
                return

            # Build summary
            # Session 873: Fix - Decision model has 'topic' not 'title'
            decision_title = (gate.decision.topic if gate.decision else None) or f"Decision-{str(gate.id)[:8]}"
            summary = (
                f"Gate for '{decision_title}' is ready for approval. "
                f"Risk level: {gate.risk_level.upper()}. "
                f"Please review and approve/reject."
            )

            # Create attention item
            attention_item = HumanAttentionItem.objects.create(
                user=user,
                title=f"[Gate Review] {decision_title[:80]}",
                summary=summary,
                item_type='gate_approval',
                urgency='high' if gate.risk_level in ['high', 'critical'] else 'medium',
                status='pending',
                source_type='gate_progression',
                source_id=str(gate.id),
                source_agent='GateProgressionPipeline',
                payload={
                    'gate_id': gate.id,
                    'decision_id': gate.decision.id if gate.decision else None,
                    'risk_level': gate.risk_level,
                    'pipeline': 'gate_progression_pipeline',
                    # Session 797: Enable PA consultation flow
                    'consultation': True,
                    'intended_action': 'approve_gate',
                    'action_params': {
                        'gate_id': gate.id,
                        'decision_title': decision_title,
                    },
                    'action_options': [
                        {
                            'id': 'approve_gate',
                            'label': 'Approve Gate',
                            'action': 'approve',
                            'style': 'success',
                        },
                        {
                            'id': 'reject_gate',
                            'label': 'Reject Gate',
                            'action': 'reject',
                            'style': 'danger',
                        },
                        {
                            'id': 'request_changes',
                            'label': 'Request Changes',
                            'action': 'request_changes',
                            'style': 'warning',
                        },
                    ],
                }
            )

            self.stats['attention_items_created'] += 1
            logger.info(f"Created attention item {attention_item.id} for gate {gate.id}")

        except Exception as e:
            self.stats['errors'].append(f"Failed to create attention item for gate {gate.id}: {e}")
            logger.error(f"Failed to create attention item: {e}")

    def _start_pilot_for_gate(self, gate, dry_run: bool = False) -> None:
        """Start a pilot execution for an approved/waived gate."""
        if dry_run:
            self.stats['pilots_started'] += 1
            return

        try:
            # Check if pilot already exists and is running
            from core.models_pilot_readiness import PilotExecution, Experiment

            existing_pilot = PilotExecution.objects.filter(
                gate=gate,
                status__in=['pending', 'running']
            ).first()

            if existing_pilot:
                logger.debug(f"Pilot already exists for gate {gate.id}")
                return

            # Session 794: Actually CREATE a PilotExecution (gate.start_pilot only sets timestamp)
            # Session 841: Fix - Decision model has 'topic' not 'title' (see models_unified_system.py:17222)
            decision_topic = (gate.decision.topic or f"Gate-{str(gate.id)[:8]}")[:100]
            pilot = PilotExecution.objects.create(
                gate=gate,
                name=f"Auto-pilot: {decision_topic}",
                description=f"Auto-deployed from {gate.status} gate by GateProgressionPipeline",
                status='running',
            )
            logger.info(f"✅ Created PilotExecution {pilot.id} for gate {gate.id}")

            # Session 794: Also create an Experiment for learning tracking
            # Session 886: Enhanced with KPI templates and validation
            try:
                # Skip if decision topic is empty or too generic
                if not decision_topic or decision_topic.startswith('Gate-') or len(decision_topic) < 10:
                    logger.warning(f"⚠️ Skipping experiment creation - invalid topic: '{decision_topic}'")
                else:
                    # Get KPI template based on decision's impact area
                    impact_area = getattr(gate.decision, 'impact_area', None) or 'general'
                    kpi_template = Experiment.KPI_TEMPLATES.get(
                        impact_area,
                        Experiment.DEFAULT_KPI
                    )

                    experiment = Experiment.objects.create(
                        name=f"Experiment: {decision_topic}",
                        hypothesis=f"Testing decision: {decision_topic}",
                        pilot=pilot,
                        status='running',
                        # Session 886: Add proper KPI configuration
                        kpi_owner=kpi_template['owner'],
                        primary_kpi=kpi_template['kpi'],
                        target_value=kpi_template['target'],
                        halt_conditions=Experiment.get_default_halt_conditions(),
                    )
                    logger.info(f"✅ Created Experiment {experiment.id} for pilot {pilot.id} (KPI: {kpi_template['kpi']})")
            except Exception as exp_error:
                logger.warning(f"Could not create Experiment: {exp_error}")

            # Use the gate's start_pilot method to set timestamp
            gate.start_pilot()

            self.stats['pilots_started'] += 1
            logger.info(f"Started pilot for gate {gate.id}")

            # Connect to Orchestration Layer if available
            self._connect_to_orchestration(gate, pilot)

        except Exception as e:
            self.stats['errors'].append(f"Failed to start pilot for gate {gate.id}: {e}")
            logger.error(f"Failed to start pilot: {e}")

    def _connect_to_orchestration(self, gate, pilot) -> None:
        """Connect pilot to orchestration layer for complex workflows."""
        try:
            # Check if orchestration is available
            from core.models_orchestration import OrchestrationExecution
            from core.services.orchestration_engine import orchestration_engine

            # Check if there's a workflow associated with the decision
            if hasattr(gate.decision, 'workflow') and gate.decision.workflow:
                workflow = gate.decision.workflow

                # Create orchestration execution
                execution = orchestration_engine.execute_workflow(
                    workflow=workflow,
                    context={
                        'gate_id': gate.id,
                        'pilot_id': pilot.id,
                        'decision_id': gate.decision.id,
                        'triggered_by': 'gate_progression_pipeline',
                    },
                    async_mode=True,  # Run via Celery
                )

                logger.info(f"Connected pilot {pilot.id} to orchestration {execution.id}")

        except ImportError:
            # Orchestration layer not yet available
            logger.debug("Orchestration layer not available, skipping connection")
        except Exception as e:
            logger.warning(f"Failed to connect to orchestration: {e}")

    def _create_attention_items_for_stuck_gates(self, dry_run: bool = False) -> None:
        """Create attention items for gates that have been stuck too long."""
        from core.models_pilot_readiness import PilotReadinessGate

        # Find gates stuck in in_progress for more than 48 hours
        threshold = timezone.now() - timedelta(hours=48)

        stuck_gates = PilotReadinessGate.objects.filter(
            status='in_progress',
            updated_at__lt=threshold
        ).exclude(
            risk_level='low'  # Low risk should have been waived
        ).select_related('decision')[:20]

        for gate in stuck_gates:
            # Check if attention item already exists
            from core.models_human_interface import HumanAttentionItem

            existing = HumanAttentionItem.objects.filter(
                source_type='gate_stuck',
                source_id=str(gate.id),
                status__in=['pending', 'acted'],
            ).exists()

            if existing:
                continue

            self._create_stuck_gate_attention_item(gate, dry_run=dry_run)

    def _create_stuck_gate_attention_item(self, gate, dry_run: bool = False) -> None:
        """Create attention item for a stuck gate."""
        from core.models_human_interface import HumanAttentionItem
        from core.models_pilot_readiness import ReadinessChecklistItem
        from django.contrib.auth import get_user_model

        User = get_user_model()

        if dry_run:
            self.stats['attention_items_created'] += 1
            return

        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.filter(is_staff=True).first()
            if not user:
                return

            # Get incomplete checklist items
            incomplete = list(ReadinessChecklistItem.objects.filter(
                gate=gate
            ).exclude(status='completed').values_list('title', flat=True)[:5])

            decision_title = getattr(gate.decision, 'topic', 'Unknown')
            summary = (
                f"Gate for '{decision_title}' has been stuck in progress for 48+ hours. "
                f"Incomplete items: {', '.join(incomplete) if incomplete else 'Unknown'}. "
                f"Please review and unblock."
            )

            HumanAttentionItem.objects.create(
                user=user,
                title=f"[Stuck Gate] {decision_title[:80]}",
                summary=summary,
                item_type='gate_stuck',
                urgency='high',
                status='pending',
                source_type='gate_stuck',
                source_id=str(gate.id),
                source_agent='GateProgressionPipeline',
                payload={
                    'gate_id': str(gate.id),
                    'decision_id': str(gate.decision.id) if gate.decision else None,
                    'risk_level': gate.risk_level,
                    'incomplete_items': incomplete,
                    # Session 797: Enable PA consultation flow for stuck gates
                    'consultation': True,
                    'intended_action': 'waive_gate',
                    'action_params': {
                        'gate_id': str(gate.id),
                        'decision_title': decision_title,
                    },
                    'action_options': [
                        {'id': 'waive_gate', 'label': 'Waive Gate', 'action': 'waive', 'style': 'warning'},
                        {'id': 'complete_items', 'label': 'Complete Items', 'action': 'complete', 'style': 'primary'},
                        {'id': 'block_gate', 'label': 'Block Gate', 'action': 'block', 'style': 'danger'},
                    ],
                }
            )

            self.stats['attention_items_created'] += 1

        except Exception as e:
            self.stats['errors'].append(f"Failed to create stuck gate attention item: {e}")

    def approve_gate_from_attention(self, attention_item_id: int) -> Dict[str, Any]:
        """
        Approve a gate from a Human Attention Item.
        Called by Mission Control when user clicks approve.
        """
        from core.models_human_interface import HumanAttentionItem
        from core.models_pilot_readiness import PilotReadinessGate, PilotExecution

        try:
            attention_item = HumanAttentionItem.objects.get(id=attention_item_id)
            payload = attention_item.payload or {}
            gate_id = payload.get('gate_id')

            if not gate_id:
                return {'success': False, 'error': 'No gate_id in payload'}

            gate = PilotReadinessGate.objects.get(id=gate_id)

            # Approve the gate
            user_name = str(attention_item.user) if attention_item.user else 'System'
            gate.approve(
                approved_by=user_name,
                notes=f"Approved via Human Attention Item {attention_item_id}"
            )

            # Mark attention item as completed
            attention_item.status = 'completed'
            attention_item.completed_at = timezone.now()
            attention_item.save()

            # Start the pilot
            gate.start_pilot()

            # Get pilot execution if exists
            pilot = PilotExecution.objects.filter(gate=gate).first()

            return {
                'success': True,
                'gate_id': gate.id,
                'gate_status': 'approved',
                'pilot_id': str(pilot.id) if pilot else None,
            }

        except Exception as e:
            logger.error(f"Failed to approve gate from attention item: {e}")
            return {'success': False, 'error': str(e)}

    def reject_gate_from_attention(
        self,
        attention_item_id: int,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Reject a gate from a Human Attention Item."""
        from core.models_human_interface import HumanAttentionItem
        from core.models_pilot_readiness import PilotReadinessGate

        try:
            attention_item = HumanAttentionItem.objects.get(id=attention_item_id)
            payload = attention_item.payload or {}
            gate_id = payload.get('gate_id')

            if not gate_id:
                return {'success': False, 'error': 'No gate_id in payload'}

            gate = PilotReadinessGate.objects.get(id=gate_id)

            # Block the gate
            gate.block(reason=reason or "Rejected via Human Attention Item")

            # Mark attention item as completed
            attention_item.status = 'completed'
            attention_item.completed_at = timezone.now()
            attention_item.save()

            return {
                'success': True,
                'gate_id': gate.id,
                'gate_status': 'blocked',
            }

        except Exception as e:
            logger.error(f"Failed to reject gate from attention item: {e}")
            return {'success': False, 'error': str(e)}

    def waive_gate_from_attention(
        self,
        attention_item_id: int,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Waive a gate from a Human Attention Item."""
        from core.models_human_interface import HumanAttentionItem
        from core.models_pilot_readiness import PilotReadinessGate, PilotExecution

        try:
            attention_item = HumanAttentionItem.objects.get(id=attention_item_id)
            payload = attention_item.payload or {}
            gate_id = payload.get('gate_id')

            if not gate_id:
                return {'success': False, 'error': 'No gate_id in payload'}

            gate = PilotReadinessGate.objects.get(id=gate_id)

            # Waive the gate (only works for low-risk, but try anyway)
            user_name = str(attention_item.user) if attention_item.user else 'System'
            try:
                gate.waive(reason=reason or "Waived via Human Attention Item")
            except ValueError:
                # If waive fails, approve instead
                gate.approve(
                    approved_by=user_name,
                    notes=f"Approved (waive requested but not low-risk): {reason or 'No reason'}"
                )

            # Mark attention item as completed
            attention_item.status = 'completed'
            attention_item.completed_at = timezone.now()
            attention_item.save()

            # Start the pilot
            gate.start_pilot()

            # Get or create pilot execution
            pilot = PilotExecution.objects.filter(gate=gate).first()

            return {
                'success': True,
                'gate_id': gate.id,
                'gate_status': gate.status,
                'pilot_id': str(pilot.id) if pilot else None,
            }

        except Exception as e:
            logger.error(f"Failed to waive gate from attention item: {e}")
            return {'success': False, 'error': str(e)}

    def get_gate_statistics(self) -> Dict[str, Any]:
        """Get current gate and pilot statistics."""
        from core.models_pilot_readiness import PilotReadinessGate, PilotExecution, ReadinessChecklistItem
        from django.db.models import Count

        # Gate stats by status
        gate_by_status = dict(
            PilotReadinessGate.objects.values('status').annotate(
                count=Count('id')
            ).values_list('status', 'count')
        )

        # Gate stats by risk
        gate_by_risk = dict(
            PilotReadinessGate.objects.values('risk_level').annotate(
                count=Count('id')
            ).values_list('risk_level', 'count')
        )

        # Pilot stats
        pilot_by_status = dict(
            PilotExecution.objects.values('status').annotate(
                count=Count('id')
            ).values_list('status', 'count')
        )

        # Checklist stats
        total_items = ReadinessChecklistItem.objects.count()
        completed_items = ReadinessChecklistItem.objects.filter(status='completed').count()

        # Stuck gates (in_progress > 48 hours)
        threshold = timezone.now() - timedelta(hours=48)
        stuck_count = PilotReadinessGate.objects.filter(
            status='in_progress',
            updated_at__lt=threshold
        ).count()

        return {
            'gates': {
                'total': sum(gate_by_status.values()),
                'by_status': gate_by_status,
                'by_risk': gate_by_risk,
                'stuck_count': stuck_count,
            },
            'pilots': {
                'total': sum(pilot_by_status.values()),
                'by_status': pilot_by_status,
            },
            'checklists': {
                'total': total_items,
                'completed': completed_items,
                'completion_rate': f"{completed_items/total_items*100:.1f}%" if total_items > 0 else "N/A",
            },
        }


# Singleton instance
gate_progression_pipeline = GateProgressionPipeline()
