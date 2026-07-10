"""
Session 843: Trace Viewer API

Provides API endpoint to view all artifacts linked to a trace_id.
This enables debugging and visualization of complete workflow executions.

GET /api/traces/<trace_id>/ - View all artifacts linked to a trace

I-0302 Phase 3 Sub-phase B2c (2026-07-10) — trace-viewer is a debug/ops
surface (see file docstring). Superuser-gated + predicate-scoped like
the B2b cluster. Do not remove ``@method_decorator(superuser_required)``
without ratified policy change.
"""
import uuid
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.utils.decorators import method_decorator

from core.security import scope_queryset_agent_execution, superuser_required

logger = logging.getLogger(__name__)


class TraceViewerView(APIView):
    """
    View all artifacts linked to a specific trace_id.

    Returns:
        - artifacts: Dict of artifact types with their records
        - timeline: Chronological list of all events
        - wiring_defects: Any defects logged for this trace
        - summary: Statistics about the trace
    """
    permission_classes = [IsAuthenticated]

    @method_decorator(superuser_required)
    def get(self, request, trace_id):
        """Get all artifacts for a trace."""
        try:
            trace_uuid = uuid.UUID(str(trace_id))
        except ValueError:
            return Response({'error': 'Invalid trace_id format'}, status=400)

        result = {
            'trace_id': str(trace_uuid),
            'artifacts': {},
            'timeline': [],
            'wiring_defects': [],
            'summary': {},
        }

        # Query all artifact types
        # I-0302 Phase 3 Sub-phase B2c: pass request so helper can scope
        # AgentExecution reads via the predicate module.
        result['artifacts'] = self._gather_artifacts(trace_uuid, request)
        result['timeline'] = self._build_timeline(result['artifacts'])
        result['wiring_defects'] = self._get_defects(trace_uuid)
        result['summary'] = self._build_summary(result)

        return Response(result)

    def _gather_artifacts(self, trace_id: uuid.UUID, request) -> dict:
        """Gather all artifacts linked to trace_id.

        I-0302 Phase 3 Sub-phase B2c (2026-07-10): ``request`` added so
        AgentExecution reads can be scoped via ``scope_queryset_agent_execution``.
        Caller is guaranteed superuser (``@method_decorator(superuser_required)``
        on ``get``), so the predicate returns own + null-user Celery runs.
        """
        artifacts = {}

        # Agent Executions (from core.models_unified_system)
        try:
            from core.models_unified_system import AgentExecution
            executions = scope_queryset_agent_execution(
                request.user,
                AgentExecution.objects.filter(trace_id=trace_id),
            ).order_by('created_at')
            artifacts['agent_executions'] = [{
                'id': str(e.id),
                'agent': e.agent.name if e.agent else e.owner_agent,
                'task': e.task[:100] if e.task else '',
                'status': e.status,
                'created_at': e.created_at.isoformat() if e.created_at else None,
                'completed_at': e.completed_at.isoformat() if e.completed_at else None,
                'execution_time_ms': e.execution_time_ms,
            } for e in executions]
        except Exception as e:
            logger.warning(f"Error gathering agent executions: {e}")
            artifacts['agent_executions'] = []

        # Deliverables
        try:
            from core.models_deliverables import Deliverable
            deliverables = Deliverable.objects.filter(trace_id=trace_id).order_by('created_at')
            artifacts['deliverables'] = [{
                'id': str(d.id),
                'title': d.title,
                'type': d.deliverable_type,
                'agent': d.agent_name,
                'category': d.category,
                'status': d.status,
                'created_at': d.created_at.isoformat() if d.created_at else None,
            } for d in deliverables]
        except Exception as e:
            logger.warning(f"Error gathering deliverables: {e}")
            artifacts['deliverables'] = []

        # Extracted Artifacts
        try:
            from core.models_conversation_artifacts import ExtractedArtifact
            extracted = ExtractedArtifact.objects.filter(trace_id=trace_id).order_by('extracted_at')
            artifacts['extracted_artifacts'] = [{
                'id': str(a.id),
                'title': a.title,
                'type': a.artifact_type,
                'status': a.status,
                'importance_score': a.importance_score,
                'created_at': a.extracted_at.isoformat() if a.extracted_at else None,
            } for a in extracted]
        except Exception as e:
            logger.warning(f"Error gathering extracted artifacts: {e}")
            artifacts['extracted_artifacts'] = []

        # Audit Reports
        try:
            from core.models_audit_tracking import AuditReport
            reports = AuditReport.objects.filter(trace_id=trace_id).order_by('created_at')
            artifacts['audit_reports'] = [{
                'id': str(r.id),
                'title': r.title,
                'type': r.audit_type,
                'total_findings': r.total_findings,
                'open_findings': r.open_findings,
                'created_at': r.created_at.isoformat() if r.created_at else None,
            } for r in reports]
        except Exception as e:
            logger.warning(f"Error gathering audit reports: {e}")
            artifacts['audit_reports'] = []

        # Self Blogs
        try:
            from core.models_unified_system import SelfBlog
            blogs = SelfBlog.objects.filter(trace_id=trace_id).order_by('created_at')
            artifacts['self_blogs'] = [{
                'id': str(b.id),
                'title': b.title,
                'category': b.category,
                'status': b.status,
                'word_count': b.word_count,
                'created_at': b.created_at.isoformat() if b.created_at else None,
            } for b in blogs]
        except Exception as e:
            logger.warning(f"Error gathering self blogs: {e}")
            artifacts['self_blogs'] = []

        # Decision Summaries
        try:
            from core.models_unified_system import AgentDecisionSummary
            decisions = AgentDecisionSummary.objects.filter(trace_id=trace_id).order_by('created_at')
            artifacts['decision_summaries'] = [{
                'id': str(d.id),
                'topic': d.topic,
                'decision_type': d.decision_type,
                'impact_area': d.impact_area,
                'status': d.status,
                'is_canonical': d.is_canonical,
                'created_at': d.created_at.isoformat() if d.created_at else None,
            } for d in decisions]
        except Exception as e:
            logger.warning(f"Error gathering decision summaries: {e}")
            artifacts['decision_summaries'] = []

        return artifacts

    def _build_timeline(self, artifacts: dict) -> list:
        """Build chronological timeline from all artifacts."""
        events = []

        for artifact_type, items in artifacts.items():
            for item in items:
                timestamp = item.get('created_at')
                if timestamp:
                    events.append({
                        'type': artifact_type,
                        'id': item.get('id'),
                        'description': (
                            item.get('task') or
                            item.get('title') or
                            item.get('topic') or
                            'Unknown'
                        )[:100],
                        'status': item.get('status', ''),
                        'timestamp': timestamp,
                    })

        # Sort by timestamp
        events.sort(key=lambda x: x['timestamp'])

        return events

    def _get_defects(self, trace_id: uuid.UUID) -> list:
        """Get wiring defects for this trace."""
        try:
            from core.models_orchestration import WiringDefect
            defects = WiringDefect.objects.filter(trace_id=trace_id).order_by('-created_at')
            return [{
                'id': str(d.id),
                'type': d.defect_type,
                'object_type': d.object_type,
                'object_id': str(d.object_id),
                'agent_name': d.agent_name,
                'is_resolved': d.is_resolved,
                'resolved_at': d.resolved_at.isoformat() if d.resolved_at else None,
                'created_at': d.created_at.isoformat() if d.created_at else None,
            } for d in defects]
        except Exception as e:
            logger.warning(f"Error gathering wiring defects: {e}")
            return []

    def _build_summary(self, result: dict) -> dict:
        """Build summary statistics."""
        artifacts = result.get('artifacts', {})
        total = sum(len(v) for v in artifacts.values())

        # Calculate status breakdown
        status_counts = {}
        for artifact_type, items in artifacts.items():
            for item in items:
                status = item.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1

        # Get time span
        timeline = result.get('timeline', [])
        first_event = timeline[0] if timeline else None
        last_event = timeline[-1] if timeline else None

        return {
            'total_artifacts': total,
            'defect_count': len(result.get('wiring_defects', [])),
            'unresolved_defects': sum(
                1 for d in result.get('wiring_defects', []) if not d.get('is_resolved')
            ),
            'artifact_counts': {k: len(v) for k, v in artifacts.items()},
            'status_breakdown': status_counts,
            'first_event': first_event['timestamp'] if first_event else None,
            'last_event': last_event['timestamp'] if last_event else None,
        }


class WiringDefectsListView(APIView):
    """
    List all unresolved wiring defects.

    GET /api/wiring-defects/ - List defects
    GET /api/wiring-defects/?resolved=false - Filter by resolved status
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List wiring defects."""
        try:
            from core.models_orchestration import WiringDefect

            queryset = WiringDefect.objects.all()

            # Filter by resolved status
            resolved = request.query_params.get('resolved')
            if resolved is not None:
                is_resolved = resolved.lower() == 'true'
                queryset = queryset.filter(is_resolved=is_resolved)

            # Filter by defect type
            defect_type = request.query_params.get('type')
            if defect_type:
                queryset = queryset.filter(defect_type=defect_type)

            # Filter by object type
            object_type = request.query_params.get('object_type')
            if object_type:
                queryset = queryset.filter(object_type=object_type)

            # Limit results
            limit = min(int(request.query_params.get('limit', 100)), 500)
            defects = queryset.order_by('-created_at')[:limit]

            return Response({
                'count': queryset.count(),
                'defects': [{
                    'id': str(d.id),
                    'type': d.defect_type,
                    'object_type': d.object_type,
                    'object_id': str(d.object_id),
                    'trace_id': str(d.trace_id) if d.trace_id else None,
                    'agent_name': d.agent_name,
                    'is_resolved': d.is_resolved,
                    'resolved_at': d.resolved_at.isoformat() if d.resolved_at else None,
                    'resolution_notes': d.resolution_notes,
                    'created_at': d.created_at.isoformat() if d.created_at else None,
                } for d in defects]
            })
        except Exception as e:
            logger.error(f"Error listing wiring defects: {e}")
            return Response({'error': str(e)}, status=500)


class WiringDefectResolveView(APIView):
    """
    Mark a wiring defect as resolved.

    POST /api/wiring-defects/<defect_id>/resolve/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, defect_id):
        """Resolve a wiring defect."""
        try:
            from core.models_orchestration import WiringDefect

            defect_uuid = uuid.UUID(str(defect_id))
            defect = WiringDefect.objects.get(id=defect_uuid)

            notes = request.data.get('notes', '')
            defect.resolve(notes=notes)

            return Response({
                'success': True,
                'defect_id': str(defect.id),
                'resolved_at': defect.resolved_at.isoformat(),
            })
        except WiringDefect.DoesNotExist:
            return Response({'error': 'Defect not found'}, status=404)
        except ValueError:
            return Response({'error': 'Invalid defect_id format'}, status=400)
        except Exception as e:
            logger.error(f"Error resolving wiring defect: {e}")
            return Response({'error': str(e)}, status=500)


class CitationViolationsListView(APIView):
    """
    Session 846: List citation violations.

    GET /api/citation-violations/ - List violations
    GET /api/citation-violations/?resolved=false - Filter by resolved status
    GET /api/citation-violations/?agent=ResearchAgent - Filter by agent
    GET /api/citation-violations/?blocked=true - Filter by blocked status
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List citation violations."""
        try:
            from core.models_orchestration import CitationViolation

            queryset = CitationViolation.objects.all()

            # Filter by resolved status
            resolved = request.query_params.get('resolved')
            if resolved is not None:
                is_resolved = resolved.lower() == 'true'
                queryset = queryset.filter(is_resolved=is_resolved)

            # Filter by violation type
            violation_type = request.query_params.get('type')
            if violation_type:
                queryset = queryset.filter(violation_type=violation_type)

            # Filter by agent
            agent = request.query_params.get('agent')
            if agent:
                queryset = queryset.filter(agent_name=agent)

            # Filter by blocked status
            blocked = request.query_params.get('blocked')
            if blocked is not None:
                was_blocked = blocked.lower() == 'true'
                queryset = queryset.filter(was_blocked=was_blocked)

            # Limit results
            limit = min(int(request.query_params.get('limit', 100)), 500)
            violations = queryset.order_by('-created_at')[:limit]

            # Get summary stats
            stats = {
                'total': queryset.count(),
                'unresolved': queryset.filter(is_resolved=False).count(),
                'blocked_count': queryset.filter(was_blocked=True).count(),
                'by_type': {},
                'by_agent': {},
            }

            # Type breakdown
            for v in CitationViolation.VIOLATION_TYPES:
                count = queryset.filter(violation_type=v[0]).count()
                if count > 0:
                    stats['by_type'][v[0]] = count

            # Agent breakdown (top 10)
            from django.db.models import Count
            agent_counts = queryset.values('agent_name').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            for ac in agent_counts:
                stats['by_agent'][ac['agent_name']] = ac['count']

            return Response({
                'stats': stats,
                'violations': [{
                    'id': str(v.id),
                    'violation_type': v.violation_type,
                    'agent_name': v.agent_name,
                    'agent_category': v.agent_category,
                    'required_sources': v.required_sources,
                    'provided_sources': v.provided_sources,
                    'sources_detail': v.sources_detail,
                    'task_preview': v.task_description[:100] if v.task_description else '',
                    'trace_id': str(v.trace_id) if v.trace_id else None,
                    'was_blocked': v.was_blocked,
                    'is_resolved': v.is_resolved,
                    'resolved_at': v.resolved_at.isoformat() if v.resolved_at else None,
                    'resolution_action': v.resolution_action,
                    'created_at': v.created_at.isoformat() if v.created_at else None,
                } for v in violations]
            })
        except Exception as e:
            logger.error(f"Error listing citation violations: {e}")
            return Response({'error': str(e)}, status=500)


class CitationViolationResolveView(APIView):
    """
    Session 846: Mark a citation violation as resolved.

    POST /api/citation-violations/<violation_id>/resolve/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, violation_id):
        """Resolve a citation violation."""
        try:
            from core.models_orchestration import CitationViolation

            violation_uuid = uuid.UUID(str(violation_id))
            violation = CitationViolation.objects.get(id=violation_uuid)

            action = request.data.get('action', '')
            notes = request.data.get('notes', '')
            violation.resolve(action=action, notes=notes)

            return Response({
                'success': True,
                'violation_id': str(violation.id),
                'resolved_at': violation.resolved_at.isoformat(),
            })
        except CitationViolation.DoesNotExist:
            return Response({'error': 'Violation not found'}, status=404)
        except ValueError:
            return Response({'error': 'Invalid violation_id format'}, status=400)
        except Exception as e:
            logger.error(f"Error resolving citation violation: {e}")
            return Response({'error': str(e)}, status=500)
