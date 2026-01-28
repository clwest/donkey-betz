"""
Session 856: Diagnostic Pipeline Service

Main orchestrator for the diagnostic pipeline:
1. Detection Phase: Record failures, generate signatures, increment counts
2. Diagnosis Phase: Multi-source evidence gathering, root cause analysis
3. Prescription Phase: Generate ranked solutions, create remediation initiatives

Guardrails:
- Cooldown per signature: 6 hours (don't re-diagnose same issue)
- Minimum sample threshold: 3 failures (don't diagnose noise)
- Known outage detection: Skip if provider is degraded (don't blame ourselves)
- Evidence confidence threshold: 0.8 (stop gathering when confident)
"""

import logging
from datetime import timedelta
from typing import Dict, Any, Optional, List, Tuple
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class DiagnosticPipelineService:
    """
    Orchestrates the full diagnostic pipeline: Detection -> Diagnosis -> Prescription
    """

    # Configuration
    COOLDOWN_HOURS = 6
    MIN_SAMPLE_THRESHOLD = 3
    CONFIDENCE_THRESHOLD = 0.8

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    # ==================== PHASE 1: DETECTION ====================

    def detect_failure(
        self,
        error_message: str,
        source_type: str,
        error_code: str = None,
        provider: str = None,
        source_id: str = None,
        source_name: str = None,
        stack_trace: str = None,
        context: Dict[str, Any] = None
    ) -> 'FailureDetection':
        """
        Phase 1 - Record a failure and generate/update its signature.

        This is called whenever a failure occurs (experiment halt, agent error,
        spider failure, etc.). It:
        1. Generates a stable signature for the error
        2. Gets or creates the FailureSignature record
        3. Creates a FailureDetection record
        4. Increments the occurrence count

        Args:
            error_message: The error message
            source_type: experiment, agent_execution, spider, celery_task, api_call
            error_code: HTTP status or error code
            provider: Provider name (openai, anthropic, etc.)
            source_id: UUID of the failed entity
            source_name: Human-readable name of what failed
            stack_trace: Full stack trace if available
            context: Additional context dict

        Returns:
            The created FailureDetection record
        """
        from core.models_diagnostic_pipeline import (
            FailureSignature, FailureDetection
        )
        from core.services.failure_signature_generator import generate_failure_signature

        context = context or {}

        # Generate signature
        signature_str, category, description = generate_failure_signature(
            error_message=error_message,
            error_code=error_code,
            provider=provider,
            source_type=source_type,
            context=context
        )

        signature_hash = FailureSignature.generate_hash(signature_str)

        self.logger.info(f"[Session 856] Detecting failure: {signature_str}")

        with transaction.atomic():
            # Get or create signature
            signature, created = FailureSignature.objects.get_or_create(
                signature_hash=signature_hash,
                defaults={
                    'signature': signature_str,
                    'category': category,
                    'provider': provider or '',
                    'error_code': error_code or '',
                    'description': description,
                }
            )

            if not created:
                # Increment occurrence count
                signature.increment_occurrence()
            else:
                self.logger.info(f"[Session 856] New signature created: {signature_str}")

            # Create detection record
            detection = FailureDetection.objects.create(
                signature=signature,
                source_type=source_type,
                source_id=source_id,
                source_name=source_name or '',
                error_message=error_message,
                error_code=error_code or '',
                stack_trace=stack_trace or '',
                context_snapshot=context,
            )

        return detection

    # ==================== PHASE 2: DIAGNOSIS ====================

    def diagnose_signature(
        self,
        signature: 'FailureSignature',
        force: bool = False
    ) -> Optional['FailureDiagnosis']:
        """
        Phase 2 - Diagnose a signature using multi-source evidence.

        Guardrails applied:
        - Skip if signature is on cooldown (unless force=True)
        - Skip if sample count < threshold
        - Skip if provider is currently degraded (known outage)

        Args:
            signature: The FailureSignature to diagnose
            force: Bypass guardrails

        Returns:
            The FailureDiagnosis record, or None if skipped
        """
        from core.models_diagnostic_pipeline import (
            FailureSignature, FailureDetection, FailureDiagnosis
        )
        from core.services.evidence_gatherer import get_evidence_gatherer
        from core.services.provider_health_tracker import get_provider_health_tracker

        self.logger.info(f"[Session 856] Diagnosing signature: {signature.signature}")

        # Guardrail 1: Cooldown check
        if not force and signature.is_on_cooldown(self.COOLDOWN_HOURS):
            self.logger.info(
                f"[Session 856] Skipping {signature.signature} - on cooldown"
            )
            return None

        # Get undiagnosed detections
        detections = signature.detections.filter(is_diagnosed=False)
        detection_count = detections.count()

        # Guardrail 2: Minimum sample threshold
        if not force and detection_count < self.MIN_SAMPLE_THRESHOLD:
            self.logger.info(
                f"[Session 856] Skipping {signature.signature} - "
                f"only {detection_count} samples (need {self.MIN_SAMPLE_THRESHOLD})"
            )
            return None

        # Guardrail 3: Check if provider is in known outage
        if signature.provider:
            tracker = get_provider_health_tracker()
            if tracker.is_provider_degraded(signature.provider):
                self.logger.info(
                    f"[Session 856] Skipping {signature.signature} - "
                    f"provider {signature.provider} is degraded (known outage)"
                )
                signature.status = FailureSignature.Status.KNOWN_OUTAGE
                signature.save(update_fields=['status'])
                return None

        # Gather evidence
        evidence_gatherer = get_evidence_gatherer()
        evidence_result = evidence_gatherer.gather_evidence(
            signature=signature,
            detections=list(detections[:20]),  # Sample up to 20
            confidence_threshold=self.CONFIDENCE_THRESHOLD
        )

        # Create or update diagnosis
        with transaction.atomic():
            diagnosis, _ = FailureDiagnosis.objects.update_or_create(
                signature=signature,
                defaults={
                    'root_cause': evidence_result['root_cause'],
                    'root_cause_confidence': evidence_result['confidence'],
                    'evidence_sources': evidence_result['sources_used'],
                    'evidence_details': evidence_result['details'],
                    'blast_radius': self._assess_blast_radius(signature, detection_count),
                    'affected_components': evidence_result.get('affected_components', []),
                    'sample_count': detection_count,
                    'sample_time_range': {
                        'from': detections.last().detected_at.isoformat() if detections.exists() else None,
                        'to': detections.first().detected_at.isoformat() if detections.exists() else None,
                    },
                }
            )

            # Mark detections as diagnosed
            detections.update(
                is_diagnosed=True,
                diagnosed_at=timezone.now()
            )

            # Update signature status
            signature.mark_diagnosed()

        self.logger.info(
            f"[Session 856] Diagnosis complete: {signature.signature} "
            f"({evidence_result['confidence']:.0%} confidence)"
        )

        return diagnosis

    def _assess_blast_radius(
        self,
        signature: 'FailureSignature',
        detection_count: int
    ) -> str:
        """Assess the blast radius based on detection patterns."""
        from core.models_diagnostic_pipeline import FailureDiagnosis

        # Get unique affected components
        detections = signature.detections.all()
        unique_sources = detections.values('source_type').distinct().count()
        unique_names = detections.values('source_name').distinct().count()

        if unique_sources >= 3 or unique_names >= 10:
            return FailureDiagnosis.BlastRadius.CRITICAL
        elif unique_sources >= 2 or unique_names >= 5:
            return FailureDiagnosis.BlastRadius.WIDESPREAD
        elif unique_names >= 2:
            return FailureDiagnosis.BlastRadius.LIMITED
        else:
            return FailureDiagnosis.BlastRadius.ISOLATED

    # ==================== PHASE 3: PRESCRIPTION ====================

    def prescribe_solutions(
        self,
        diagnosis: 'FailureDiagnosis'
    ) -> List['FailurePrescription']:
        """
        Phase 3 - Generate ranked solutions for a diagnosis.

        Creates prescriptions in three scopes:
        - Immediate: Stop the bleeding (quick fixes)
        - Structural: Prevent recurrence (code/config changes)
        - Observability: Make obvious (monitoring/alerting)

        Args:
            diagnosis: The FailureDiagnosis to prescribe for

        Returns:
            List of created FailurePrescription records
        """
        from core.models_diagnostic_pipeline import FailurePrescription
        from core.services.solution_ranker import get_solution_ranker

        self.logger.info(
            f"[Session 856] Prescribing solutions for: {diagnosis.signature.signature}"
        )

        solution_ranker = get_solution_ranker()
        solutions = solution_ranker.generate_solutions(diagnosis)

        prescriptions = []
        with transaction.atomic():
            for solution in solutions:
                prescription = FailurePrescription.objects.create(
                    diagnosis=diagnosis,
                    title=solution['title'],
                    description=solution['description'],
                    scope=solution['scope'],
                    expected_impact=solution.get('impact', 'medium'),
                    effort=solution.get('effort', 'small'),
                    confidence=solution.get('confidence', 0.5),
                    technical_steps=solution.get('steps', []),
                    files_to_modify=solution.get('files', []),
                    commands_to_run=solution.get('commands', []),
                    success_criteria=solution.get('success_criteria', ''),
                    verification_steps=solution.get('verification', []),
                )
                prescriptions.append(prescription)

        self.logger.info(
            f"[Session 856] Created {len(prescriptions)} prescriptions"
        )

        return prescriptions

    def create_remediation_initiative(
        self,
        diagnosis: 'FailureDiagnosis',
        prescriptions: List['FailurePrescription']
    ) -> Optional['Initiative']:
        """
        Create an Initiative to track remediation of this diagnosis.

        Creates a 5-stage initiative:
        - Stage 1: Incident Brief (detection summary)
        - Stage 2: Remediation Plan (prescriptions)
        - Stage 3: Success Criteria (from prescription criteria)

        Args:
            diagnosis: The diagnosis to remediate
            prescriptions: The prescriptions to include

        Returns:
            The created Initiative, or None if creation failed
        """
        from core.services.initiative_integration_service import (
            get_initiative_integration_service
        )
        from core.models_document_registry import InitiativeStage

        if not prescriptions:
            return None

        service = get_initiative_integration_service()

        try:
            # Create initiative
            initiative, created = service.get_or_create_initiative(
                topic=f"Remediate: {diagnosis.signature.signature}",
                description=(
                    f"Auto-created remediation initiative for failure signature.\n\n"
                    f"**Root Cause:** {diagnosis.root_cause[:500]}\n\n"
                    f"**Confidence:** {diagnosis.root_cause_confidence:.0%}\n\n"
                    f"**Blast Radius:** {diagnosis.blast_radius}\n\n"
                    f"**Sample Count:** {diagnosis.sample_count} occurrences"
                ),
                created_by="DiagnosticPipeline"
            )

            if not created:
                self.logger.info(
                    f"[Session 856] Initiative already exists for {diagnosis.signature.signature}"
                )
                return initiative

            # Update Stage 1 with incident brief
            stage1 = initiative.stages.filter(stage=1).first()
            if stage1:
                stage1.notes = (
                    f"**Incident Brief**\n\n"
                    f"Signature: {diagnosis.signature.signature}\n"
                    f"Category: {diagnosis.signature.category}\n"
                    f"Occurrences: {diagnosis.signature.occurrence_count}\n"
                    f"First Seen: {diagnosis.signature.first_seen_at.isoformat()}\n"
                    f"Last Seen: {diagnosis.signature.last_seen_at.isoformat()}\n\n"
                    f"**Evidence Sources:** {', '.join(diagnosis.evidence_sources)}"
                )
                stage1.status = InitiativeStage.StageStatus.DRAFT
                stage1.save()

            # Update Stage 2 with remediation plan
            stage2 = initiative.stages.filter(stage=2).first()
            if stage2:
                plan_text = "**Remediation Plan**\n\n"
                for i, rx in enumerate(prescriptions, 1):
                    plan_text += (
                        f"{i}. [{rx.scope.upper()}] {rx.title}\n"
                        f"   Impact: {rx.expected_impact}, Effort: {rx.effort}\n"
                        f"   Confidence: {rx.confidence:.0%}\n\n"
                    )
                stage2.notes = plan_text
                stage2.status = InitiativeStage.StageStatus.DRAFT
                stage2.save()

            # Update Stage 3 with success criteria
            stage3 = initiative.stages.filter(stage=3).first()
            if stage3:
                criteria_text = "**Success Criteria**\n\n"
                for rx in prescriptions:
                    if rx.success_criteria:
                        criteria_text += f"- {rx.success_criteria}\n"
                stage3.notes = criteria_text
                stage3.status = InitiativeStage.StageStatus.PENDING
                stage3.save()

            # Link prescriptions to initiative
            for rx in prescriptions:
                rx.initiative = initiative
                rx.save(update_fields=['initiative'])

            self.logger.info(
                f"[Session 856] Created remediation Initiative: {initiative.name}"
            )

            return initiative

        except Exception as e:
            self.logger.error(f"[Session 856] Failed to create Initiative: {e}")
            return None

    # ==================== FULL PIPELINE ====================

    def run_full_pipeline(
        self,
        signature_id: str = None,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Run the full diagnostic pipeline for one or more signatures.

        If signature_id is provided, runs for that signature only.
        Otherwise, runs for all signatures with pending detections.

        Args:
            signature_id: Optional specific signature to process
            force: Bypass guardrails

        Returns:
            Summary of what was processed
        """
        from core.models_diagnostic_pipeline import FailureSignature

        results = {
            'signatures_processed': 0,
            'diagnoses_created': 0,
            'prescriptions_created': 0,
            'initiatives_created': 0,
            'skipped': [],
        }

        if signature_id:
            signatures = FailureSignature.objects.filter(id=signature_id)
        else:
            # Find signatures with undiagnosed detections above threshold
            signatures = FailureSignature.objects.filter(
                status=FailureSignature.Status.ACTIVE,
                detections__is_diagnosed=False
            ).distinct()

        for signature in signatures:
            # Check sample threshold before processing
            undiagnosed_count = signature.detections.filter(is_diagnosed=False).count()
            if not force and undiagnosed_count < self.MIN_SAMPLE_THRESHOLD:
                results['skipped'].append({
                    'signature': signature.signature,
                    'reason': f'Only {undiagnosed_count} samples'
                })
                continue

            # Run diagnosis
            diagnosis = self.diagnose_signature(signature, force=force)
            if not diagnosis:
                results['skipped'].append({
                    'signature': signature.signature,
                    'reason': 'Diagnosis skipped (cooldown or outage)'
                })
                continue

            results['signatures_processed'] += 1
            results['diagnoses_created'] += 1

            # Generate prescriptions
            prescriptions = self.prescribe_solutions(diagnosis)
            results['prescriptions_created'] += len(prescriptions)

            # Create remediation initiative
            initiative = self.create_remediation_initiative(diagnosis, prescriptions)
            if initiative:
                results['initiatives_created'] += 1

        self.logger.info(
            f"[Session 856] Pipeline complete: {results['signatures_processed']} signatures, "
            f"{results['prescriptions_created']} prescriptions"
        )

        return results

    # ==================== CONTEXT FOR THINKING AGENT ====================

    def get_diagnostic_context(self) -> Dict[str, Any]:
        """
        Get diagnostic pipeline context for ThinkingAgent.

        Returns summary of:
        - Active failure signatures with counts
        - Pending diagnoses
        - Unresolved prescriptions
        """
        from core.models_diagnostic_pipeline import (
            FailureSignature, FailureDiagnosis, FailurePrescription
        )

        # Active signatures (top 10 by occurrence)
        active_signatures = list(
            FailureSignature.objects.filter(
                status__in=[
                    FailureSignature.Status.ACTIVE,
                    FailureSignature.Status.DIAGNOSED
                ]
            ).order_by('-occurrence_count')[:10].values(
                'signature', 'category', 'provider', 'occurrence_count',
                'status', 'last_seen_at'
            )
        )

        # Pending diagnoses (signatures needing diagnosis)
        pending_diagnosis_count = FailureSignature.objects.filter(
            status=FailureSignature.Status.ACTIVE,
            detections__is_diagnosed=False
        ).distinct().count()

        # Recent diagnoses
        recent_diagnoses = []
        for diagnosis in FailureDiagnosis.objects.order_by('-diagnosed_at')[:5]:
            recent_diagnoses.append(diagnosis.to_summary_dict())

        # Unresolved prescriptions
        unresolved_prescriptions = []
        for rx in FailurePrescription.objects.filter(
            status__in=[
                FailurePrescription.Status.PROPOSED,
                FailurePrescription.Status.APPROVED,
                FailurePrescription.Status.IN_PROGRESS
            ]
        ).order_by('-priority_score')[:10]:
            unresolved_prescriptions.append(rx.to_summary_dict())

        return {
            'active_signatures': active_signatures,
            'pending_diagnosis_count': pending_diagnosis_count,
            'recent_diagnoses': recent_diagnoses,
            'unresolved_prescriptions': unresolved_prescriptions,
            'total_signatures': FailureSignature.objects.count(),
            'total_diagnoses': FailureDiagnosis.objects.count(),
        }


# Singleton instance
_pipeline_instance: Optional[DiagnosticPipelineService] = None


def get_diagnostic_pipeline_service() -> DiagnosticPipelineService:
    """Get the singleton DiagnosticPipelineService instance."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = DiagnosticPipelineService()
    return _pipeline_instance


# Convenience functions
def detect_failure(
    error_message: str,
    source_type: str,
    **kwargs
) -> 'FailureDetection':
    """Convenience function to detect a failure."""
    return get_diagnostic_pipeline_service().detect_failure(
        error_message=error_message,
        source_type=source_type,
        **kwargs
    )


def run_diagnostic_pipeline(
    signature_id: str = None,
    force: bool = False
) -> Dict[str, Any]:
    """Convenience function to run the diagnostic pipeline."""
    return get_diagnostic_pipeline_service().run_full_pipeline(
        signature_id=signature_id,
        force=force
    )


def get_diagnostic_context() -> Dict[str, Any]:
    """Convenience function to get diagnostic context for ThinkingAgent."""
    return get_diagnostic_pipeline_service().get_diagnostic_context()
