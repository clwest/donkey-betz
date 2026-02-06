"""
Session 954: RAG Observability Service

Provides visibility into the risk-aware RAG system:
1. Document inventory by classification, risk level, and critical status
2. Retrieval channel effectiveness metrics
3. Context budget utilization tracking
4. Risk boost impact analysis

Built on Session 949's risk-aware RAG infrastructure.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import timedelta
from collections import defaultdict
from dataclasses import dataclass, field, asdict

from django.utils import timezone
from django.db.models import Count, Avg, Q, F
from django.db.models.functions import TruncDate, TruncHour

logger = logging.getLogger(__name__)


@dataclass
class DocumentInventoryStats:
    """Statistics about the document inventory for RAG."""
    total_documents: int = 0
    total_active: int = 0
    total_critical: int = 0

    # By risk level
    by_risk_level: Dict[str, int] = field(default_factory=dict)

    # By document class
    by_document_class: Dict[str, int] = field(default_factory=dict)

    # Critical docs breakdown
    critical_by_class: Dict[str, int] = field(default_factory=dict)

    # High-risk breakdown
    high_risk_by_class: Dict[str, int] = field(default_factory=dict)

    # Freshness metrics
    avg_age_days: float = 0.0
    newest_doc_age_days: float = 0.0
    oldest_critical_age_days: float = 0.0


@dataclass
class RetrievalChannelStats:
    """Statistics about retrieval channel usage."""
    total_retrievals: int = 0

    # Channel usage counts
    semantic_channel_count: int = 0
    critical_channel_count: int = 0
    incident_channel_count: int = 0
    constraint_channel_count: int = 0

    # Channel distribution percentages
    semantic_pct: float = 0.0
    critical_pct: float = 0.0
    incident_pct: float = 0.0
    constraint_pct: float = 0.0

    # Scope usage
    scope_active_count: int = 0
    scope_all_count: int = 0
    scope_repo_count: int = 0
    auto_expansion_count: int = 0
    auto_expansion_rate: float = 0.0


@dataclass
class RiskBoostStats:
    """Statistics about risk-aware re-ranking effectiveness."""
    total_results_boosted: int = 0
    total_results_unboosted: int = 0

    # Boost magnitudes
    avg_boost_applied: float = 0.0
    max_boost_applied: float = 0.0
    min_boost_applied: float = 0.0

    # Position changes
    avg_position_improvement: float = 0.0
    docs_moved_to_top_5: int = 0

    # By category
    boost_by_risk_level: Dict[str, float] = field(default_factory=dict)
    boost_by_document_class: Dict[str, float] = field(default_factory=dict)


@dataclass
class ContextBudgetStats:
    """Statistics about context budget utilization."""
    total_budget: int = 4000
    total_used: int = 0
    utilization_pct: float = 0.0

    # By priority tier
    critical_tier_tokens: int = 0
    reserved_tier_tokens: int = 0
    high_tier_tokens: int = 0
    medium_tier_tokens: int = 0
    low_tier_tokens: int = 0

    # Reserved tier breakdown (Session 949)
    critical_docs_tokens: int = 0
    incident_docs_tokens: int = 0
    audit_findings_tokens: int = 0

    # Section utilization
    section_usage: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Health indicators
    is_over_budget: bool = False
    sections_truncated: List[str] = field(default_factory=list)
    sections_skipped: List[str] = field(default_factory=list)


class RAGObservabilityService:
    """
    Service for RAG system observability and metrics.

    Provides dashboard data about:
    - Document inventory (classifications, risk levels, critical status)
    - Retrieval effectiveness (channel usage, scope distribution)
    - Risk boost impact (how much boosting affects rankings)
    - Context budget health (token utilization, truncation events)
    """

    def __init__(self):
        self._document_model = None
        self._context_budget_manager = None
        self._scoped_retrieval = None

    @property
    def Document(self):
        """Lazy-load Document model."""
        if self._document_model is None:
            from content.models import Document
            self._document_model = Document
        return self._document_model

    @property
    def context_budget_manager(self):
        """Lazy-load context budget manager."""
        if self._context_budget_manager is None:
            from core.services.context_budget_manager import get_context_budget_manager
            self._context_budget_manager = get_context_budget_manager()
        return self._context_budget_manager

    @property
    def scoped_retrieval(self):
        """Lazy-load scoped retrieval service."""
        if self._scoped_retrieval is None:
            from core.services.scoped_retrieval import get_scoped_retrieval
            self._scoped_retrieval = get_scoped_retrieval()
        return self._scoped_retrieval

    def get_document_inventory_stats(self) -> DocumentInventoryStats:
        """
        Get comprehensive statistics about the document inventory.

        Returns breakdown by risk level, document class, and critical status.
        """
        stats = DocumentInventoryStats()

        try:
            # Total counts
            all_docs = self.Document.objects.all()
            active_docs = all_docs.filter(status='processed')

            stats.total_documents = all_docs.count()
            stats.total_active = active_docs.count()
            stats.total_critical = active_docs.filter(is_critical=True).count()

            # By risk level
            risk_counts = active_docs.values('risk_level').annotate(
                count=Count('id')
            ).order_by('-count')
            stats.by_risk_level = {
                item['risk_level']: item['count']
                for item in risk_counts if item['risk_level']
            }

            # By document class
            class_counts = active_docs.exclude(
                document_class__isnull=True
            ).exclude(
                document_class=''
            ).values('document_class').annotate(
                count=Count('id')
            ).order_by('-count')
            stats.by_document_class = {
                item['document_class']: item['count']
                for item in class_counts
            }

            # Critical docs by class
            critical_by_class = active_docs.filter(
                is_critical=True
            ).exclude(
                document_class__isnull=True
            ).values('document_class').annotate(
                count=Count('id')
            )
            stats.critical_by_class = {
                item['document_class']: item['count']
                for item in critical_by_class
            }

            # High-risk docs by class
            high_risk_by_class = active_docs.filter(
                risk_level__in=['critical', 'high']
            ).exclude(
                document_class__isnull=True
            ).values('document_class').annotate(
                count=Count('id')
            )
            stats.high_risk_by_class = {
                item['document_class']: item['count']
                for item in high_risk_by_class
            }

            # Freshness metrics
            now = timezone.now()
            if active_docs.exists():
                newest = active_docs.order_by('-updated_at').first()
                if newest and newest.updated_at:
                    stats.newest_doc_age_days = (now - newest.updated_at).days

                # Average age
                ages = []
                for doc in active_docs.only('updated_at')[:100]:  # Sample
                    if doc.updated_at:
                        ages.append((now - doc.updated_at).days)
                if ages:
                    stats.avg_age_days = sum(ages) / len(ages)

                # Oldest critical doc
                oldest_critical = active_docs.filter(
                    is_critical=True
                ).order_by('updated_at').first()
                if oldest_critical and oldest_critical.updated_at:
                    stats.oldest_critical_age_days = (now - oldest_critical.updated_at).days

        except Exception as e:
            logger.error(f"Error getting document inventory stats: {e}")

        return stats

    def get_retrieval_channel_stats(self, days: int = 7) -> RetrievalChannelStats:
        """
        Get statistics about retrieval channel usage.

        Note: This returns estimated stats based on document availability
        since we don't yet have persistent retrieval logging.
        """
        stats = RetrievalChannelStats()

        try:
            active_docs = self.Document.objects.filter(status='processed')

            # Estimate channel availability based on document characteristics
            stats.critical_channel_count = active_docs.filter(is_critical=True).count()

            # Incident channel (postmortems + incident reports)
            stats.incident_channel_count = active_docs.filter(
                document_class__in=['postmortem', 'incident_report']
            ).count()

            # Constraint channel (audit findings, security, constraints)
            stats.constraint_channel_count = active_docs.filter(
                document_class__in=['security', 'constraint', 'audit_finding']
            ).count()

            # Semantic channel (all active docs)
            stats.semantic_channel_count = active_docs.count()

            # Calculate distribution
            total = (stats.critical_channel_count + stats.incident_channel_count +
                     stats.constraint_channel_count + stats.semantic_channel_count)
            if total > 0:
                stats.critical_pct = (stats.critical_channel_count / total) * 100
                stats.incident_pct = (stats.incident_channel_count / total) * 100
                stats.constraint_pct = (stats.constraint_channel_count / total) * 100
                stats.semantic_pct = (stats.semantic_channel_count / total) * 100

            stats.total_retrievals = total

        except Exception as e:
            logger.error(f"Error getting retrieval channel stats: {e}")

        return stats

    def get_risk_boost_stats(self) -> RiskBoostStats:
        """
        Get statistics about risk-aware re-ranking boost effectiveness.

        Calculates expected boost values based on document classifications.
        """
        stats = RiskBoostStats()

        # Boost values from scoped_retrieval.py
        RISK_BOOSTS = {
            'critical': 0.25,
            'high': 0.15,
            'medium': 0.0,
            'low': -0.05,
        }

        CLASS_BOOSTS = {
            'postmortem': 0.20,
            'incident_report': 0.15,
            'security': 0.15,
            'constraint': 0.10,
            'architecture': 0.05,
            'runbook': 0.05,
            'changelog': 0.0,
            'reference': 0.0,
        }

        CRITICAL_BOOST = 0.30

        try:
            active_docs = self.Document.objects.filter(status='processed')

            # Calculate boost by risk level
            for risk_level, boost in RISK_BOOSTS.items():
                count = active_docs.filter(risk_level=risk_level).count()
                stats.boost_by_risk_level[risk_level] = {
                    'count': count,
                    'boost': boost,
                    'total_boost_potential': count * boost,
                }

            # Calculate boost by document class
            for doc_class, boost in CLASS_BOOSTS.items():
                count = active_docs.filter(document_class=doc_class).count()
                if count > 0:
                    stats.boost_by_document_class[doc_class] = {
                        'count': count,
                        'boost': boost,
                        'total_boost_potential': count * boost,
                    }

            # Critical docs get the max boost
            critical_count = active_docs.filter(is_critical=True).count()
            stats.total_results_boosted = critical_count + active_docs.filter(
                Q(risk_level__in=['critical', 'high']) |
                Q(document_class__in=['postmortem', 'incident_report', 'security', 'constraint'])
            ).count()

            stats.total_results_unboosted = active_docs.count() - stats.total_results_boosted

            # Max and average boost
            stats.max_boost_applied = CRITICAL_BOOST  # is_critical gives +0.30

            # Calculate average expected boost across all boostable docs
            total_boost = 0
            boosted_count = 0
            for doc in active_docs.filter(
                Q(is_critical=True) |
                Q(risk_level__in=['critical', 'high']) |
                Q(document_class__in=list(CLASS_BOOSTS.keys()))
            ).only('is_critical', 'risk_level', 'document_class')[:500]:
                boost = 0
                if doc.is_critical:
                    boost += CRITICAL_BOOST
                if doc.risk_level:
                    boost += RISK_BOOSTS.get(doc.risk_level, 0)
                if doc.document_class:
                    boost += CLASS_BOOSTS.get(doc.document_class, 0)
                if boost > 0:
                    total_boost += boost
                    boosted_count += 1

            if boosted_count > 0:
                stats.avg_boost_applied = total_boost / boosted_count

        except Exception as e:
            logger.error(f"Error getting risk boost stats: {e}")

        return stats

    def get_context_budget_stats(self) -> ContextBudgetStats:
        """
        Get current context budget utilization stats.

        Uses the ContextBudgetManager to get allocation information.
        """
        stats = ContextBudgetStats()

        try:
            manager = self.context_budget_manager

            # Get default allocations
            allocations = manager.DEFAULT_BUDGETS
            stats.total_budget = manager.TOTAL_BUDGET

            # Calculate by priority tier
            for section, config in allocations.items():
                tokens = config.max_tokens if hasattr(config, 'max_tokens') else 0
                priority = config.priority.name if hasattr(config, 'priority') else 'LOW'

                if priority == 'CRITICAL':
                    stats.critical_tier_tokens += tokens
                elif priority == 'RESERVED':
                    stats.reserved_tier_tokens += tokens
                    # Track reserved tier breakdown
                    if section == 'critical_docs':
                        stats.critical_docs_tokens = tokens
                    elif section == 'incident_docs':
                        stats.incident_docs_tokens = tokens
                    elif section == 'audit_findings':
                        stats.audit_findings_tokens = tokens
                elif priority == 'HIGH':
                    stats.high_tier_tokens += tokens
                elif priority == 'MEDIUM':
                    stats.medium_tier_tokens += tokens
                elif priority == 'LOW':
                    stats.low_tier_tokens += tokens

                stats.section_usage[section] = {
                    'max_tokens': tokens,
                    'priority': priority,
                    'status': 'Active',
                }

            # Calculate totals
            stats.total_used = (
                stats.critical_tier_tokens +
                stats.reserved_tier_tokens +
                stats.high_tier_tokens +
                stats.medium_tier_tokens +
                stats.low_tier_tokens
            )

            if stats.total_budget > 0:
                stats.utilization_pct = (stats.total_used / stats.total_budget) * 100

            stats.is_over_budget = stats.total_used > stats.total_budget

        except Exception as e:
            logger.error(f"Error getting context budget stats: {e}")

        return stats

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive dashboard summary combining all metrics.

        Returns a dict suitable for JSON serialization and frontend display.
        """
        inventory = self.get_document_inventory_stats()
        retrieval = self.get_retrieval_channel_stats()
        boost = self.get_risk_boost_stats()
        budget = self.get_context_budget_stats()

        # Build health indicators
        health_indicators = []

        # Check critical docs coverage
        if inventory.total_critical == 0:
            health_indicators.append({
                'level': 'warning',
                'message': 'No documents marked as critical',
                'recommendation': 'Mark important docs with is_critical=True',
            })
        elif inventory.total_critical < 5:
            health_indicators.append({
                'level': 'info',
                'message': f'Only {inventory.total_critical} critical documents',
                'recommendation': 'Consider marking more key docs as critical',
            })
        else:
            health_indicators.append({
                'level': 'success',
                'message': f'{inventory.total_critical} critical documents protected',
            })

        # Check document classification coverage
        classified_count = sum(inventory.by_document_class.values())
        if classified_count < inventory.total_active * 0.5:
            health_indicators.append({
                'level': 'warning',
                'message': f'Only {classified_count}/{inventory.total_active} docs classified',
                'recommendation': 'Run classify_docs_for_rag to improve risk detection',
            })
        else:
            health_indicators.append({
                'level': 'success',
                'message': f'{classified_count} documents classified for risk-aware retrieval',
            })

        # Check reserved tier allocation
        reserved_pct = (budget.reserved_tier_tokens / budget.total_budget) * 100 if budget.total_budget > 0 else 0
        if reserved_pct < 10:
            health_indicators.append({
                'level': 'warning',
                'message': f'Reserved tier only {reserved_pct:.1f}% of budget',
                'recommendation': 'Critical/incident docs may be crowded out',
            })
        else:
            health_indicators.append({
                'level': 'success',
                'message': f'Reserved tier: {budget.reserved_tier_tokens} tokens ({reserved_pct:.1f}%)',
            })

        return {
            'timestamp': timezone.now().isoformat(),
            'document_inventory': asdict(inventory),
            'retrieval_channels': asdict(retrieval),
            'risk_boost': asdict(boost),
            'context_budget': asdict(budget),
            'health_indicators': health_indicators,
            'summary': {
                'total_documents': inventory.total_active,
                'critical_documents': inventory.total_critical,
                'classified_documents': sum(inventory.by_document_class.values()),
                'high_risk_documents': sum(inventory.high_risk_by_class.values()),
                'budget_utilization': budget.utilization_pct,
                'reserved_tier_tokens': budget.reserved_tier_tokens,
            },
        }

    def get_critical_docs_report(self) -> List[Dict[str, Any]]:
        """
        Get a detailed report of all critical documents.

        Useful for verifying critical doc coverage.
        """
        critical_docs = []

        try:
            docs = self.Document.objects.filter(
                status='processed',
                is_critical=True,
            ).order_by('-updated_at')

            for doc in docs:
                age_days = 0
                if doc.updated_at:
                    age_days = (timezone.now() - doc.updated_at).days

                critical_docs.append({
                    'id': str(doc.id),
                    'title': doc.title,
                    'path': doc.path,
                    'document_class': doc.document_class,
                    'risk_level': doc.risk_level,
                    'updated_at': doc.updated_at.isoformat() if doc.updated_at else None,
                    'age_days': age_days,
                    'retrieval_boost': doc.retrieval_boost,
                })
        except Exception as e:
            logger.error(f"Error getting critical docs report: {e}")

        return critical_docs

    def get_risk_distribution_report(self) -> Dict[str, Any]:
        """
        Get detailed risk distribution across documents.

        Shows how documents are distributed across risk levels and classes.
        """
        report = {
            'risk_matrix': {},
            'coverage_gaps': [],
            'recommendations': [],
        }

        try:
            active_docs = self.Document.objects.filter(status='processed')

            # Build risk matrix: risk_level x document_class
            risk_levels = ['critical', 'high', 'medium', 'low']
            doc_classes = [
                'postmortem', 'incident_report', 'security', 'constraint',
                'architecture', 'runbook', 'changelog', 'reference'
            ]

            for risk_level in risk_levels:
                report['risk_matrix'][risk_level] = {}
                for doc_class in doc_classes:
                    count = active_docs.filter(
                        risk_level=risk_level,
                        document_class=doc_class
                    ).count()
                    report['risk_matrix'][risk_level][doc_class] = count

            # Identify coverage gaps
            # Check for missing postmortems in critical/high risk
            high_risk_postmortems = active_docs.filter(
                risk_level__in=['critical', 'high'],
                document_class='postmortem'
            ).count()
            if high_risk_postmortems == 0:
                report['coverage_gaps'].append({
                    'type': 'missing_postmortems',
                    'message': 'No postmortems marked as critical/high risk',
                    'impact': 'Incident learnings may not surface in retrieval',
                })

            # Check for security docs
            security_docs = active_docs.filter(document_class='security').count()
            if security_docs == 0:
                report['coverage_gaps'].append({
                    'type': 'no_security_docs',
                    'message': 'No documents classified as security',
                    'impact': 'Security constraints may not be retrieved',
                })

            # Check for constraint docs
            constraint_docs = active_docs.filter(document_class='constraint').count()
            if constraint_docs == 0:
                report['coverage_gaps'].append({
                    'type': 'no_constraint_docs',
                    'message': 'No documents classified as constraints',
                    'impact': 'Policy/rule documents may not surface',
                })

            # Generate recommendations
            unclassified = active_docs.filter(
                Q(document_class__isnull=True) | Q(document_class='')
            ).count()
            if unclassified > 10:
                report['recommendations'].append({
                    'priority': 'high',
                    'action': f'Classify {unclassified} unclassified documents',
                    'command': 'python manage.py classify_docs_for_rag',
                })

            uncritical_incidents = active_docs.filter(
                document_class__in=['postmortem', 'incident_report'],
                is_critical=False
            ).count()
            if uncritical_incidents > 0:
                report['recommendations'].append({
                    'priority': 'medium',
                    'action': f'Consider marking {uncritical_incidents} incident docs as critical',
                    'reason': 'Incident learnings should always surface',
                })

        except Exception as e:
            logger.error(f"Error getting risk distribution report: {e}")

        return report


# Singleton instance
_service = None


def get_rag_observability_service() -> RAGObservabilityService:
    """Get or create the singleton RAGObservabilityService instance."""
    global _service
    if _service is None:
        _service = RAGObservabilityService()
    return _service
