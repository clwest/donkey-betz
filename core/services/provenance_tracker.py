"""
Provenance Tracker Service
Session 472: Market Intelligence Architecture - Phase 5

Provides comprehensive data lineage tracking for the Market Intelligence pipeline.
Tracks the complete chain: Spider Data → Opportunity → Score → Validation → Decision → Outcome

Features:
- Automatic provenance creation at each pipeline stage
- Cryptographic integrity verification (blockchain-style hashing)
- Compliance rule evaluation
- Lineage query and visualization
- Audit logging for all actions
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


@dataclass
class ProvenanceResult:
    """Result of creating a provenance record."""
    success: bool
    provenance_id: Optional[str] = None
    audit_log_id: Optional[str] = None
    compliance_passed: bool = True
    compliance_issues: List[Dict] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.compliance_issues is None:
            self.compliance_issues = []


@dataclass
class LineageResult:
    """Result of a lineage query."""
    success: bool
    lineage: List[Dict] = None
    depth: int = 0
    root_entity: Optional[Dict] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.lineage is None:
            self.lineage = []


class ProvenanceTracker:
    """
    Provenance Tracker for Market Intelligence Pipeline.

    Session 472: Market Intelligence Architecture - Phase 5

    Tracks data lineage from spider crawl through to outcome,
    maintaining cryptographic integrity and compliance records.
    """

    def __init__(self):
        logger.info("📜 Provenance Tracker initialized")

    def _compute_content_hash(self, content: Dict[str, Any]) -> str:
        """Compute SHA-256 hash of content for integrity verification."""
        content_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def create_provenance(
        self,
        entity_type: str,
        entity_id: str,
        source_type: str,
        source_name: str = '',
        source_version: str = '',
        metadata: Dict = None,
        parent_provenance_id: str = None,
        user=None,
        data_timestamp: datetime = None,
        run_compliance: bool = True
    ) -> ProvenanceResult:
        """
        Create a provenance record for an entity.

        Args:
            entity_type: Type of entity (spider_data, opportunity, scoring_result, etc.)
            entity_id: ID of the entity
            source_type: Type of source (spider, api, ml_prediction, etc.)
            source_name: Name of the source
            source_version: Version of the source
            metadata: Additional metadata to capture
            parent_provenance_id: ID of parent provenance record (for lineage chain)
            user: User who triggered this (if applicable)
            data_timestamp: Original timestamp of the data
            run_compliance: Whether to run compliance checks

        Returns:
            ProvenanceResult with provenance ID and compliance status
        """
        from core.models_unified_system import DataProvenance

        try:
            with transaction.atomic():
                # Get parent provenance if specified
                parent = None
                if parent_provenance_id:
                    try:
                        parent = DataProvenance.objects.get(id=parent_provenance_id)
                    except DataProvenance.DoesNotExist:
                        logger.warning(f"Parent provenance {parent_provenance_id} not found")

                # Compute content hash
                content_for_hash = {
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'source_type': source_type,
                    'source_name': source_name,
                    'metadata': metadata or {},
                    'timestamp': (data_timestamp or timezone.now()).isoformat(),
                }
                content_hash = self._compute_content_hash(content_for_hash)

                # Create provenance record
                provenance = DataProvenance.objects.create(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    parent=parent,
                    source_type=source_type,
                    source_name=source_name,
                    source_version=source_version,
                    data_timestamp=data_timestamp or timezone.now(),
                    metadata=metadata or {},
                    content_hash=content_hash,
                    created_by=user,
                )

                logger.info(
                    f"📜 [Provenance] Created {entity_type}:{entity_id[:8]}... "
                    f"(depth={provenance.depth}, source={source_name})"
                )

                # Create audit log
                audit_log = self._create_audit_log(
                    action_type=self._get_action_type_for_entity(entity_type),
                    actor_type='user' if user else 'system',
                    actor_id=str(user.id) if user else 'system',
                    actor_name=user.username if user else 'System',
                    target_type=entity_type,
                    target_id=entity_id,
                    after_state=metadata or {},
                    provenance=provenance,
                )

                # Run compliance checks if requested
                compliance_issues = []
                if run_compliance:
                    compliance_issues = self._run_compliance_checks(provenance)

                    # Update compliance status based on results
                    if compliance_issues:
                        has_blocking = any(
                            issue.get('severity') in ('error', 'critical')
                            for issue in compliance_issues
                        )
                        provenance.compliance_status = 'non_compliant' if has_blocking else 'compliant'
                    else:
                        provenance.compliance_status = 'compliant'

                    provenance.compliance_checked_at = timezone.now()
                    provenance.save(update_fields=['compliance_status', 'compliance_checked_at'])

                return ProvenanceResult(
                    success=True,
                    provenance_id=str(provenance.id),
                    audit_log_id=str(audit_log.id) if audit_log else None,
                    compliance_passed=provenance.compliance_status == 'compliant',
                    compliance_issues=compliance_issues,
                )

        except Exception as e:
            logger.error(f"❌ [Provenance] Failed to create provenance: {e}")
            return ProvenanceResult(
                success=False,
                error=str(e)
            )

    def _get_action_type_for_entity(self, entity_type: str) -> str:
        """Map entity type to audit log action type."""
        mapping = {
            'spider_data': 'spider_crawl',
            'opportunity': 'data_import',
            'scoring_result': 'hybrid_score',
            'validation_request': 'validation_queued',
            'validation_decision': 'validation_approved',
            'outcome': 'outcome_recorded',
            'ml_model': 'model_deployed',
            'alert': 'alert_triggered',
        }
        return mapping.get(entity_type, 'data_import')

    def _create_audit_log(
        self,
        action_type: str,
        actor_type: str,
        actor_id: str,
        actor_name: str,
        target_type: str,
        target_id: str,
        before_state: Dict = None,
        after_state: Dict = None,
        provenance=None,
        context: Dict = None,
        reason: str = '',
        request_id: str = '',
        ip_address: str = None
    ):
        """Create an audit log entry."""
        from core.models_unified_system import AuditLog

        try:
            audit_log = AuditLog.objects.create(
                action_type=action_type,
                actor_type=actor_type,
                actor_id=actor_id,
                actor_name=actor_name,
                target_type=target_type,
                target_id=target_id,
                before_state=before_state or {},
                after_state=after_state or {},
                provenance=provenance,
                context=context or {},
                reason=reason,
                request_id=request_id,
                ip_address=ip_address,
            )

            logger.debug(
                f"📜 [Audit] Logged {action_type} by {actor_name} on {target_type}:{target_id[:8]}..."
            )

            return audit_log

        except Exception as e:
            logger.error(f"❌ [Audit] Failed to create audit log: {e}")
            return None

    def _run_compliance_checks(self, provenance) -> List[Dict]:
        """Run compliance checks on a provenance record."""
        from core.models_unified_system import ComplianceRule, ComplianceCheck

        issues = []

        # Get active rules for this entity type
        rules = ComplianceRule.get_active_rules(provenance.entity_type)

        for rule in rules:
            try:
                check_result = self._evaluate_rule(provenance, rule)

                # Create compliance check record
                ComplianceCheck.objects.create(
                    provenance=provenance,
                    check_type=rule.check_type,
                    rule_name=rule.name,
                    rule_version=rule.version,
                    rule_config=rule.config,
                    passed=check_result['passed'],
                    severity=rule.severity if not check_result['passed'] else 'info',
                    actual_value=check_result.get('actual_value'),
                    expected_value=check_result.get('expected_value'),
                    message=check_result.get('message', ''),
                    details=check_result.get('details', {}),
                    remediation_required=not check_result['passed'] and rule.severity in ('error', 'critical'),
                    remediation_action=check_result.get('remediation_action', ''),
                )

                if not check_result['passed']:
                    issues.append({
                        'rule_name': rule.name,
                        'check_type': rule.check_type,
                        'severity': rule.severity,
                        'message': check_result.get('message', ''),
                        'blocking': rule.blocking,
                    })

            except Exception as e:
                logger.error(f"❌ [Compliance] Failed to run rule {rule.name}: {e}")

        return issues

    def _evaluate_rule(self, provenance, rule) -> Dict:
        """Evaluate a single compliance rule against a provenance record."""
        check_type = rule.check_type
        config = rule.config

        if check_type == 'data_freshness':
            return self._check_data_freshness(provenance, config)
        elif check_type == 'source_attribution':
            return self._check_source_attribution(provenance, config)
        elif check_type == 'confidence_threshold':
            return self._check_confidence_threshold(provenance, config)
        elif check_type == 'human_review':
            return self._check_human_review_required(provenance, config)
        else:
            # Default pass for unknown check types
            return {'passed': True, 'message': 'No check implemented'}

    def _check_data_freshness(self, provenance, config) -> Dict:
        """Check if data is fresh enough."""
        max_age_hours = config.get('max_age_hours', 24)
        max_age = timedelta(hours=max_age_hours)

        data_time = provenance.data_timestamp or provenance.created_at
        age = timezone.now() - data_time

        passed = age <= max_age

        return {
            'passed': passed,
            'actual_value': age.total_seconds() / 3600,  # hours
            'expected_value': max_age_hours,
            'message': f"Data age is {age.total_seconds()/3600:.1f} hours (max: {max_age_hours}h)",
            'remediation_action': 'Refresh data from source' if not passed else '',
        }

    def _check_source_attribution(self, provenance, config) -> Dict:
        """Check if source attribution is complete."""
        required_fields = config.get('required_fields', ['source_type', 'source_name'])

        missing = []
        for field in required_fields:
            value = getattr(provenance, field, None)
            if not value:
                missing.append(field)

        passed = len(missing) == 0

        return {
            'passed': passed,
            'actual_value': {'missing_fields': missing},
            'expected_value': {'required_fields': required_fields},
            'message': f"Missing source attribution: {', '.join(missing)}" if missing else "Source attribution complete",
            'remediation_action': 'Add missing source attribution fields' if not passed else '',
        }

    def _check_confidence_threshold(self, provenance, config) -> Dict:
        """Check if confidence meets minimum threshold."""
        min_confidence = config.get('min_confidence', 50)

        # Get confidence from metadata
        confidence = provenance.metadata.get('confidence', 100)

        passed = confidence >= min_confidence

        return {
            'passed': passed,
            'actual_value': confidence,
            'expected_value': min_confidence,
            'message': f"Confidence {confidence}% {'meets' if passed else 'below'} minimum {min_confidence}%",
            'remediation_action': 'Requires human review for low confidence' if not passed else '',
        }

    def _check_human_review_required(self, provenance, config) -> Dict:
        """Check if human review is required based on criteria."""
        requires_review_for = config.get('requires_review_for', [])

        needs_review = provenance.entity_type in requires_review_for

        # Check if human review has occurred
        has_review = provenance.source_type == 'human_review'

        if needs_review and not has_review:
            return {
                'passed': False,
                'actual_value': {'has_human_review': has_review},
                'expected_value': {'requires_human_review': True},
                'message': f"{provenance.entity_type} requires human review",
                'remediation_action': 'Route to human review queue',
            }

        return {
            'passed': True,
            'message': 'Human review not required or already completed',
        }

    def get_lineage(self, entity_type: str, entity_id: str) -> LineageResult:
        """
        Get the complete lineage for an entity.

        Args:
            entity_type: Type of entity
            entity_id: ID of the entity

        Returns:
            LineageResult with full lineage chain
        """
        from core.models_unified_system import DataProvenance

        try:
            # Find the provenance record
            provenance = DataProvenance.objects.filter(
                entity_type=entity_type,
                entity_id=entity_id
            ).first()

            if not provenance:
                return LineageResult(
                    success=False,
                    error=f"No provenance found for {entity_type}:{entity_id}"
                )

            # Get full lineage
            lineage = provenance.get_lineage_summary()

            # Get root entity details
            root = lineage[0] if lineage else None

            return LineageResult(
                success=True,
                lineage=lineage,
                depth=provenance.depth,
                root_entity=root,
            )

        except Exception as e:
            logger.error(f"❌ [Provenance] Failed to get lineage: {e}")
            return LineageResult(
                success=False,
                error=str(e)
            )

    def get_descendants(self, provenance_id: str) -> List[Dict]:
        """Get all descendants of a provenance record."""
        from core.models_unified_system import DataProvenance

        try:
            provenance = DataProvenance.objects.get(id=provenance_id)

            descendants = DataProvenance.objects.filter(
                root=provenance
            ).order_by('depth', 'created_at')

            return [
                {
                    'id': str(d.id),
                    'entity_type': d.entity_type,
                    'entity_id': d.entity_id,
                    'source_type': d.source_type,
                    'source_name': d.source_name,
                    'depth': d.depth,
                    'created_at': d.created_at.isoformat(),
                    'compliance_status': d.compliance_status,
                }
                for d in descendants
            ]

        except DataProvenance.DoesNotExist:
            return []
        except Exception as e:
            logger.error(f"❌ [Provenance] Failed to get descendants: {e}")
            return []

    def verify_integrity(self, provenance_id: str) -> Dict[str, Any]:
        """
        Verify the integrity of a provenance chain.

        Checks:
        - Content hash integrity
        - Chain hash integrity (blockchain-style)
        - Timestamp ordering
        """
        from core.models_unified_system import DataProvenance

        try:
            provenance = DataProvenance.objects.get(id=provenance_id)
            lineage = provenance.get_full_lineage()

            issues = []

            for i, record in enumerate(lineage):
                # Verify content hash
                expected_hash = self._compute_content_hash({
                    'entity_type': record.entity_type,
                    'entity_id': record.entity_id,
                    'source_type': record.source_type,
                    'source_name': record.source_name,
                    'metadata': record.metadata,
                    'timestamp': record.data_timestamp.isoformat() if record.data_timestamp else record.created_at.isoformat(),
                })

                if record.content_hash != expected_hash:
                    issues.append({
                        'type': 'content_hash_mismatch',
                        'record_id': str(record.id),
                        'message': 'Content hash does not match computed hash',
                    })

                # Verify chain integrity
                if record.parent and record.previous_hash != record.parent.content_hash:
                    issues.append({
                        'type': 'chain_hash_mismatch',
                        'record_id': str(record.id),
                        'message': 'Previous hash does not match parent content hash',
                    })

                # Verify timestamp ordering
                if record.parent and record.created_at < record.parent.created_at:
                    issues.append({
                        'type': 'timestamp_order',
                        'record_id': str(record.id),
                        'message': 'Record created before parent',
                    })

            return {
                'valid': len(issues) == 0,
                'records_checked': len(lineage),
                'issues': issues,
            }

        except DataProvenance.DoesNotExist:
            return {
                'valid': False,
                'error': f"Provenance {provenance_id} not found",
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
            }

    def get_audit_trail(
        self,
        entity_type: str = None,
        entity_id: str = None,
        action_type: str = None,
        actor_id: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get audit trail with filtering.

        Args:
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            action_type: Filter by action type
            actor_id: Filter by actor ID
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum records to return

        Returns:
            List of audit log entries
        """
        from core.models_unified_system import AuditLog

        queryset = AuditLog.objects.all()

        if entity_type:
            queryset = queryset.filter(target_type=entity_type)
        if entity_id:
            queryset = queryset.filter(target_id=entity_id)
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        if actor_id:
            queryset = queryset.filter(actor_id=actor_id)
        if start_time:
            queryset = queryset.filter(timestamp__gte=start_time)
        if end_time:
            queryset = queryset.filter(timestamp__lte=end_time)

        queryset = queryset.order_by('-timestamp')[:limit]

        return [
            {
                'id': str(log.id),
                'action_type': log.action_type,
                'actor_type': log.actor_type,
                'actor_id': log.actor_id,
                'actor_name': log.actor_name,
                'target_type': log.target_type,
                'target_id': log.target_id,
                'timestamp': log.timestamp.isoformat(),
                'context': log.context,
                'reason': log.reason,
            }
            for log in queryset
        ]

    def get_compliance_summary(
        self,
        entity_type: str = None,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> Dict[str, Any]:
        """Get compliance summary statistics."""
        from core.models_unified_system import ComplianceCheck
        from django.db.models import Count, Q

        queryset = ComplianceCheck.objects.all()

        if entity_type:
            queryset = queryset.filter(provenance__entity_type=entity_type)
        if start_time:
            queryset = queryset.filter(checked_at__gte=start_time)
        if end_time:
            queryset = queryset.filter(checked_at__lte=end_time)

        # Get counts by status
        total = queryset.count()
        passed = queryset.filter(passed=True).count()
        failed = queryset.filter(passed=False).count()

        # Get counts by severity
        by_severity = dict(
            queryset.filter(passed=False)
            .values('severity')
            .annotate(count=Count('id'))
            .values_list('severity', 'count')
        )

        # Get counts by check type
        by_check_type = dict(
            queryset.values('check_type')
            .annotate(
                total=Count('id'),
                passed=Count('id', filter=Q(passed=True)),
                failed=Count('id', filter=Q(passed=False)),
            )
            .values_list('check_type', 'total')
        )

        # Remediation stats
        needs_remediation = queryset.filter(
            remediation_required=True,
            remediated=False
        ).count()

        return {
            'total_checks': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': round((passed / total * 100) if total > 0 else 0, 1),
            'by_severity': by_severity,
            'by_check_type': by_check_type,
            'needs_remediation': needs_remediation,
        }


# =============================================================================
# Convenience Functions
# =============================================================================


def create_spider_data_provenance(
    spider_data_id: str,
    spider_name: str,
    record_count: int,
    metadata: Dict = None,
    user=None
) -> ProvenanceResult:
    """Create provenance for spider data collection."""
    tracker = get_provenance_tracker()
    return tracker.create_provenance(
        entity_type='spider_data',
        entity_id=spider_data_id,
        source_type='spider',
        source_name=spider_name,
        metadata={
            'record_count': record_count,
            **(metadata or {}),
        },
        user=user,
    )


def create_opportunity_provenance(
    opportunity_id: str,
    spider_data_provenance_id: str,
    metadata: Dict = None,
    user=None
) -> ProvenanceResult:
    """Create provenance for opportunity creation."""
    tracker = get_provenance_tracker()
    return tracker.create_provenance(
        entity_type='opportunity',
        entity_id=opportunity_id,
        source_type='system',
        source_name='opportunity_engine',
        metadata=metadata or {},
        parent_provenance_id=spider_data_provenance_id,
        user=user,
    )


def create_scoring_provenance(
    scoring_id: str,
    opportunity_provenance_id: str,
    ml_score: float,
    rule_score: float,
    hybrid_score: float,
    confidence: float,
    model_version: str = '',
    metadata: Dict = None
) -> ProvenanceResult:
    """Create provenance for scoring result."""
    tracker = get_provenance_tracker()
    return tracker.create_provenance(
        entity_type='scoring_result',
        entity_id=scoring_id,
        source_type='ml_prediction',
        source_name='ml_scoring_engine',
        source_version=model_version,
        metadata={
            'ml_score': ml_score,
            'rule_score': rule_score,
            'hybrid_score': hybrid_score,
            'confidence': confidence,
            **(metadata or {}),
        },
        parent_provenance_id=opportunity_provenance_id,
    )


def create_validation_provenance(
    validation_id: str,
    scoring_provenance_id: str,
    decision: str,
    decided_by: str = None,
    override_score: float = None,
    metadata: Dict = None,
    user=None
) -> ProvenanceResult:
    """Create provenance for validation decision."""
    tracker = get_provenance_tracker()
    return tracker.create_provenance(
        entity_type='validation_decision',
        entity_id=validation_id,
        source_type='human_review' if decided_by else 'system',
        source_name=decided_by or 'auto_validation',
        metadata={
            'decision': decision,
            'override_score': override_score,
            **(metadata or {}),
        },
        parent_provenance_id=scoring_provenance_id,
        user=user,
    )


def create_outcome_provenance(
    outcome_id: str,
    validation_provenance_id: str,
    outcome_type: str,
    outcome_value: float,
    actual_revenue: float = None,
    metadata: Dict = None,
    user=None
) -> ProvenanceResult:
    """Create provenance for outcome recording."""
    tracker = get_provenance_tracker()
    return tracker.create_provenance(
        entity_type='outcome',
        entity_id=outcome_id,
        source_type='user_input' if user else 'system',
        source_name=user.username if user else 'outcome_tracker',
        metadata={
            'outcome_type': outcome_type,
            'outcome_value': outcome_value,
            'actual_revenue': actual_revenue,
            **(metadata or {}),
        },
        parent_provenance_id=validation_provenance_id,
        user=user,
    )


# =============================================================================
# Session 474: Narrative Drift + Content Studio Provenance Functions
# =============================================================================


def create_narrative_evidence_provenance(
    evidence_id: str,
    spider_data_provenance_id: str,
    narrative_id: str,
    evidence_strength: str,
    metadata: Dict = None,
) -> ProvenanceResult:
    """Create provenance for narrative evidence from spider data."""
    tracker = get_provenance_tracker()
    return tracker.create_provenance(
        entity_type='narrative_evidence',
        entity_id=evidence_id,
        source_type='system',
        source_name='narrative_drift_detector',
        metadata={
            'narrative_id': narrative_id,
            'evidence_strength': evidence_strength,
            **(metadata or {}),
        },
        parent_provenance_id=spider_data_provenance_id,
    )


def create_narrative_shift_provenance(
    shift_id: str,
    evidence_provenance_id: str = None,
    domain: str = '',
    confidence: float = 0.0,
    importance: float = 0.0,
    metadata: Dict = None,
) -> ProvenanceResult:
    """Create provenance for a detected narrative shift."""
    tracker = get_provenance_tracker()
    return tracker.create_provenance(
        entity_type='narrative_shift',
        entity_id=shift_id,
        source_type='ml_prediction',
        source_name='narrative_drift_coordinator',
        metadata={
            'domain': domain,
            'confidence': confidence,
            'importance': importance,
            **(metadata or {}),
        },
        parent_provenance_id=evidence_provenance_id,
    )


def create_content_episode_provenance(
    episode_id: str,
    parent_provenance_id: str = None,
    channel_name: str = '',
    content_type: str = '',
    trigger_source: str = '',
    metadata: Dict = None,
) -> ProvenanceResult:
    """Create provenance for auto-generated content episode."""
    tracker = get_provenance_tracker()
    return tracker.create_provenance(
        entity_type='content_episode',
        entity_id=episode_id,
        source_type='system',
        source_name='autonomous_content_studio',
        metadata={
            'channel_name': channel_name,
            'content_type': content_type,
            'trigger_source': trigger_source,
            **(metadata or {}),
        },
        parent_provenance_id=parent_provenance_id,
    )


# =============================================================================
# Singleton Instance
# =============================================================================


_provenance_tracker_instance: Optional[ProvenanceTracker] = None


def get_provenance_tracker() -> ProvenanceTracker:
    """Get singleton provenance tracker instance."""
    global _provenance_tracker_instance
    if _provenance_tracker_instance is None:
        _provenance_tracker_instance = ProvenanceTracker()
    return _provenance_tracker_instance
