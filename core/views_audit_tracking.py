"""
Session 819: Audit Tracking API Views

API endpoints for managing audit findings and remediation workflow.
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def findings_list(request):
    """
    List audit findings with filtering.

    Query params:
        - status: open, in_progress, fixed, verified, wontfix, deferred
        - priority: P0, P1, P2, P3
        - category: security, authentication, etc.
        - audit_id: Filter by specific audit report
        - limit: Max results (default 50)
    """
    from core.models_audit_tracking import AuditFinding

    try:
        status = request.GET.get('status')
        priority = request.GET.get('priority')
        category = request.GET.get('category')
        audit_id = request.GET.get('audit_id')
        limit = int(request.GET.get('limit', 50))

        queryset = AuditFinding.objects.select_related('audit_report')

        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if category:
            queryset = queryset.filter(category=category)
        if audit_id:
            queryset = queryset.filter(audit_report_id=audit_id)

        findings = queryset[:limit]

        return JsonResponse({
            'success': True,
            'count': queryset.count(),
            'findings': [
                {
                    'id': str(f.id),
                    'title': f.title,
                    'description': f.description[:500],
                    'priority': f.priority,
                    'category': f.category,
                    'status': f.status,
                    'impact': f.impact,
                    'audit_report': {
                        'id': str(f.audit_report.id),
                        'title': f.audit_report.title,
                    },
                    'recommendation': f.recommendation[:500] if f.recommendation else '',
                    'assigned_agent': f.assigned_agent,
                    'fixed_by': f.fixed_by,
                    'created_at': f.created_at.isoformat(),
                    'updated_at': f.updated_at.isoformat(),
                }
                for f in findings
            ]
        })

    except Exception as e:
        logger.error(f"Error listing findings: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def finding_detail(request, finding_id):
    """Get full details of a specific finding."""
    from core.models_audit_tracking import AuditFinding

    try:
        finding = AuditFinding.objects.select_related('audit_report').get(id=finding_id)

        return JsonResponse({
            'success': True,
            'finding': {
                'id': str(finding.id),
                'finding_id': finding.finding_id,
                'title': finding.title,
                'description': finding.description,
                'priority': finding.priority,
                'category': finding.category,
                'status': finding.status,
                'impact': finding.impact,
                'affected_files': finding.affected_files,
                'affected_components': finding.affected_components,
                'recommendation': finding.recommendation,
                'remediation_notes': finding.remediation_notes,
                'fixed_by': finding.fixed_by,
                'fixed_at': finding.fixed_at.isoformat() if finding.fixed_at else None,
                'is_verified': finding.is_verified,
                'verified_at': finding.verified_at.isoformat() if finding.verified_at else None,
                'verification_notes': finding.verification_notes,
                'assigned_agent': finding.assigned_agent,
                'assigned_at': finding.assigned_at.isoformat() if finding.assigned_at else None,
                'raw_text': finding.raw_text,
                'metadata': finding.metadata,
                'audit_report': {
                    'id': str(finding.audit_report.id),
                    'title': finding.audit_report.title,
                    'file_path': finding.audit_report.file_path,
                    'audit_type': finding.audit_report.audit_type,
                },
                'remediation_tasks': [
                    {
                        'id': str(t.id),
                        'title': t.title,
                        'status': t.status,
                        'assigned_agent': t.assigned_agent,
                    }
                    for t in finding.remediation_tasks.all()
                ],
                'verification_runs': [
                    {
                        'id': str(v.id),
                        'verification_type': v.verification_type,
                        'passed': v.passed,
                        'result_summary': v.result_summary,
                        'executed_at': v.executed_at.isoformat(),
                    }
                    for v in finding.verification_runs.all()
                ],
                'created_at': finding.created_at.isoformat(),
                'updated_at': finding.updated_at.isoformat(),
            }
        })

    except AuditFinding.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Finding not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting finding detail: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def finding_update_status(request, finding_id):
    """
    Update finding status.

    Body:
        - status: open, in_progress, fixed, verified, wontfix, deferred
        - notes: Optional notes
        - fixed_by: Required if status is 'fixed' (e.g., "Session 820" or "PR #155")
    """
    import json
    from core.models_audit_tracking import AuditFinding

    try:
        data = json.loads(request.body)
        status = data.get('status')
        notes = data.get('notes', '')
        fixed_by = data.get('fixed_by', '')

        if not status:
            return JsonResponse({
                'success': False,
                'error': 'Status is required'
            }, status=400)

        finding = AuditFinding.objects.get(id=finding_id)

        if status == 'fixed':
            if not fixed_by:
                return JsonResponse({
                    'success': False,
                    'error': 'fixed_by is required when marking as fixed'
                }, status=400)
            finding.mark_fixed(fixed_by, notes)

        elif status == 'verified':
            finding.mark_verified(notes)

        elif status == 'wontfix':
            finding.mark_wontfix(notes or 'No reason provided')

        elif status == 'in_progress':
            finding.mark_in_progress(data.get('agent_name'))

        else:
            finding.status = status
            if notes:
                finding.remediation_notes = notes
            finding.save()

        return JsonResponse({
            'success': True,
            'finding': {
                'id': str(finding.id),
                'status': finding.status,
                'updated_at': finding.updated_at.isoformat(),
            }
        })

    except AuditFinding.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Finding not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error updating finding status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def finding_create_task(request, finding_id):
    """
    Create a remediation task for a finding.

    Body:
        - title: Task title
        - description: Task description
        - agent_name: Optional agent to assign
    """
    import json
    from core.services.audit_tracker import AuditTrackerService

    try:
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description', '')
        agent_name = data.get('agent_name')

        if not title:
            return JsonResponse({
                'success': False,
                'error': 'Title is required'
            }, status=400)

        service = AuditTrackerService()
        task = service.create_remediation_task(
            finding_id=finding_id,
            title=title,
            description=description,
            agent_name=agent_name
        )

        return JsonResponse({
            'success': True,
            'task': {
                'id': str(task.id),
                'title': task.title,
                'status': task.status,
                'assigned_agent': task.assigned_agent,
            }
        })

    except Exception as e:
        logger.error(f"Error creating remediation task: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def finding_verify(request, finding_id):
    """
    Run verification for a finding.

    Body:
        - verification_type: grep_check, api_test, manual
        - command: Optional verification command
    """
    import json
    from core.services.audit_tracker import AuditTrackerService

    try:
        data = json.loads(request.body)
        verification_type = data.get('verification_type', 'manual')
        command = data.get('command', '')

        service = AuditTrackerService()
        verification = service.verify_finding(
            finding_id=finding_id,
            verification_type=verification_type,
            command=command
        )

        return JsonResponse({
            'success': True,
            'verification': {
                'id': str(verification.id),
                'passed': verification.passed,
                'result_summary': verification.result_summary,
                'executed_at': verification.executed_at.isoformat(),
            }
        })

    except Exception as e:
        logger.error(f"Error verifying finding: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def findings_summary(request):
    """Get summary statistics of all findings."""
    from core.services.audit_tracker import AuditTrackerService

    try:
        service = AuditTrackerService()
        summary = service.get_finding_summary()

        return JsonResponse({
            'success': True,
            'summary': summary
        })

    except Exception as e:
        logger.error(f"Error getting findings summary: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def audit_reports_list(request):
    """List all audit reports."""
    from core.models_audit_tracking import AuditReport

    try:
        limit = int(request.GET.get('limit', 100))
        audit_type = request.GET.get('type')

        queryset = AuditReport.objects.all()

        if audit_type:
            queryset = queryset.filter(audit_type=audit_type)

        reports = queryset[:limit]

        return JsonResponse({
            'success': True,
            'count': queryset.count(),
            'reports': [
                {
                    'id': str(r.id),
                    'title': r.title,
                    'file_path': r.file_path,
                    'audit_type': r.audit_type,
                    'session_number': r.session_number,
                    'audit_date': r.audit_date.isoformat() if r.audit_date else None,
                    'total_findings': r.total_findings,
                    'open_findings': r.open_findings,
                    'p0_findings': r.p0_findings,
                    'p1_findings': r.p1_findings,
                    'fixed_findings': r.fixed_findings,
                    'created_at': r.created_at.isoformat(),
                }
                for r in reports
            ]
        })

    except Exception as e:
        logger.error(f"Error listing audit reports: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def audit_report_detail(request, report_id):
    """Get full details of an audit report."""
    from core.models_audit_tracking import AuditReport

    try:
        report = AuditReport.objects.get(id=report_id)

        return JsonResponse({
            'success': True,
            'report': {
                'id': str(report.id),
                'title': report.title,
                'slug': report.slug,
                'file_path': report.file_path,
                'audit_type': report.audit_type,
                'auditor': report.auditor,
                'session_number': report.session_number,
                'audit_date': report.audit_date.isoformat() if report.audit_date else None,
                'executive_summary': report.executive_summary,
                'total_findings': report.total_findings,
                'open_findings': report.open_findings,
                'fixed_findings': report.fixed_findings,
                'p0_findings': report.p0_findings,
                'p1_findings': report.p1_findings,
                'p2_findings': report.p2_findings,
                'findings': [
                    {
                        'id': str(f.id),
                        'title': f.title,
                        'priority': f.priority,
                        'status': f.status,
                        'category': f.category,
                    }
                    for f in report.findings.all()
                ],
                'created_at': report.created_at.isoformat(),
                'last_parsed_at': report.last_parsed_at.isoformat() if report.last_parsed_at else None,
            }
        })

    except AuditReport.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Audit report not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting audit report detail: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def import_audits(request):
    """
    Import/re-import audit files from docs/audits/.

    Body:
        - dry_run: If true, parse but don't save (default: false)
    """
    import json
    from core.services.audit_tracker import AuditTrackerService

    try:
        data = json.loads(request.body) if request.body else {}
        dry_run = data.get('dry_run', False)

        service = AuditTrackerService()
        results = service.import_all_audits(dry_run=dry_run)

        return JsonResponse({
            'success': True,
            'dry_run': dry_run,
            'results': results
        })

    except Exception as e:
        logger.error(f"Error importing audits: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def open_p0_findings(request):
    """
    Get all open P0 (critical) findings.
    Used by Human Interface to surface critical issues.
    """
    from core.models_audit_tracking import AuditFinding

    try:
        findings = AuditFinding.objects.filter(
            status='open',
            priority='P0'
        ).select_related('audit_report')

        return JsonResponse({
            'success': True,
            'count': findings.count(),
            'findings': [
                {
                    'id': str(f.id),
                    'title': f.title,
                    'description': f.description[:300],
                    'category': f.category,
                    'audit_title': f.audit_report.title,
                    'recommendation': f.recommendation[:300] if f.recommendation else '',
                    'created_at': f.created_at.isoformat(),
                }
                for f in findings
            ]
        })

    except Exception as e:
        logger.error(f"Error getting P0 findings: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
