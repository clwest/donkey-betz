"""
Platform Command Center API - Session 815 + Session 824

Provides APIs for the Platform Command Center which serves as the main
control interface for system governance, mission tracking, and knowledge management.

Endpoints:
- GET /api/platform/mission/ - Current mission + metrics
- GET /api/platform/metrics/ - Detailed progress data
- GET /api/platform/governance/ - System owner + controls status
- POST /api/platform/emergency-halt/ - Trigger emergency halt
- GET /api/platform/canon/ - List canon documents
- GET /api/platform/playbooks/ - List playbooks

Session 824: Live Metrics & Self-Execution Control
- GET /api/platform/live-metrics/ - Real-time system metrics
- GET /api/platform/triggers/ - List trigger rules
- POST /api/platform/triggers/<name>/toggle/ - Toggle trigger rule
- POST /api/platform/triggers/run-now/ - Manual metrics check
- POST /api/platform/actions/run-spiders/ - Trigger spider run
- POST /api/platform/actions/run-remediation/ - Trigger remediation
- POST /api/platform/actions/run-self-audit/ - Trigger self-audit
- POST /api/platform/actions/agent-health-check/ - Trigger agent health check
- GET /api/platform/remediation/status/ - Remediation status
"""

import logging
import os
import re
from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Any

from django.conf import settings
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger(__name__)


def _get_docs_dir() -> Path:
    """Get the docs directory path."""
    return Path(settings.BASE_DIR) / 'docs'


def _parse_mission_file() -> Dict[str, Any]:
    """
    Parse the CURRENT_MISSION.md file to extract mission data.

    Returns:
        Dict with mission statement, goal, metrics, etc.
    """
    mission_path = _get_docs_dir() / 'missions' / 'CURRENT_MISSION.md'

    if not mission_path.exists():
        return {
            'status': 'not_found',
            'statement': 'No mission defined',
            'goal': None,
            'period': None,
            'session': None,
            'priorities': [],
            'metrics_targets': {},
        }

    try:
        content = mission_path.read_text()

        # Extract status, period, session from first line
        status_match = re.search(r'\*\*Status:\*\*\s*(\w+)', content)
        period_match = re.search(r'\*\*Period:\*\*\s*([\w\d\s]+)', content)
        session_match = re.search(r'\*\*Session:\*\*\s*(\d+)', content)

        # Extract mission statement (the quoted line)
        statement_match = re.search(r'>\s*\*\*([^*]+)\*\*', content)

        # Extract goal
        goal_match = re.search(r'\*\*Goal:\*\*\s*([^\n]+)', content)

        # Extract daily cost target
        cost_match = re.search(r'Current daily target:\s*<\s*\$(\d+)', content)

        # Extract metric targets from table
        metrics_targets = {
            'monthly_revenue': 10000,  # $10,000 MRR
            'daily_llm_cost': int(cost_match.group(1)) if cost_match else 50,
            'canon_docs': 20,
            'playbooks': 10,
        }

        return {
            'status': status_match.group(1).lower() if status_match else 'unknown',
            'statement': statement_match.group(1).strip() if statement_match else 'Transform Donkey Betz into revenue-generating product',
            'goal': goal_match.group(1).strip() if goal_match else '$10,000 MRR by Q1 2026',
            'period': period_match.group(1).strip() if period_match else 'Q1 2026',
            'session': int(session_match.group(1)) if session_match else None,
            'priorities': [
                {'rank': 1, 'name': 'Cost Optimization', 'why': "Can't grow if costs exceed value"},
                {'rank': 2, 'name': 'Canon Building', 'why': 'Reusable knowledge compounds'},
                {'rank': 3, 'name': 'Revenue Features', 'why': 'Direct path to mission goal'},
                {'rank': 4, 'name': 'System Stability', 'why': 'Foundation for everything else'},
                {'rank': 5, 'name': 'New Capabilities', 'why': 'Only after 1-4 are solid'},
            ],
            'metrics_targets': metrics_targets,
            'raw_content': content,
        }
    except Exception as e:
        logger.error(f"Error parsing mission file: {e}")
        return {
            'status': 'error',
            'statement': 'Error reading mission',
            'error': str(e),
        }


def _get_revenue_metrics() -> Dict[str, Any]:
    """
    Get current revenue metrics.

    Session 819: Fixed status filters to match actual Revenue model statuses.
    Revenue model uses: 'pending', 'completed', 'cancelled'
    """
    from core.models_unified_system import Revenue

    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Get monthly revenue (completed only)
    monthly = Revenue.objects.filter(
        created_at__gte=start_of_month,
        status='completed'
    ).aggregate(total=Sum('amount'))

    # Get total lifetime revenue (completed)
    lifetime = Revenue.objects.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))

    # Get pending revenue (awaiting completion)
    pending = Revenue.objects.filter(
        status='pending'
    ).aggregate(total=Sum('amount'))

    return {
        'monthly': float(monthly['total'] or 0),
        'lifetime': float(lifetime['total'] or 0),
        'pending': float(pending['total'] or 0),
    }


def _get_llm_cost_metrics() -> Dict[str, Any]:
    """Get LLM cost metrics."""
    from core.models_llm_routing import LLMCallLog

    now = timezone.now()
    past_24h = now - timedelta(hours=24)
    past_7d = now - timedelta(days=7)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Daily cost (last 24h)
    daily = LLMCallLog.objects.filter(
        created_at__gte=past_24h
    ).aggregate(
        total_cost=Sum('cost'),
        total_calls=Count('id'),
        total_tokens=Sum('total_tokens'),
    )

    # Weekly cost
    weekly = LLMCallLog.objects.filter(
        created_at__gte=past_7d
    ).aggregate(
        total_cost=Sum('cost'),
        total_calls=Count('id'),
    )

    # Monthly cost
    monthly = LLMCallLog.objects.filter(
        created_at__gte=start_of_month
    ).aggregate(
        total_cost=Sum('cost'),
        total_calls=Count('id'),
    )

    return {
        'daily': {
            'cost': float(daily['total_cost'] or 0),
            'calls': daily['total_calls'] or 0,
            'tokens': daily['total_tokens'] or 0,
        },
        'weekly': {
            'cost': float(weekly['total_cost'] or 0),
            'calls': weekly['total_calls'] or 0,
        },
        'monthly': {
            'cost': float(monthly['total_cost'] or 0),
            'calls': monthly['total_calls'] or 0,
        },
    }


def _count_canon_docs() -> Dict[str, Any]:
    """Count canon documents by category."""
    canon_dir = _get_docs_dir() / 'canon'

    if not canon_dir.exists():
        return {'total': 0, 'by_category': {}}

    categories = {}
    total = 0

    for item in canon_dir.iterdir():
        if item.is_dir():
            category_name = item.name
            md_files = list(item.glob('*.md'))
            count = len([f for f in md_files if f.name != 'INDEX.md'])
            if count > 0:
                categories[category_name] = count
                total += count
        elif item.suffix == '.md' and item.name not in ['INDEX.md', 'README.md']:
            if 'root' not in categories:
                categories['root'] = 0
            categories['root'] += 1
            total += 1

    return {
        'total': total,
        'by_category': categories,
    }


def _count_playbooks() -> Dict[str, Any]:
    """Count playbooks by category."""
    playbooks_dir = _get_docs_dir() / 'playbooks'

    if not playbooks_dir.exists():
        return {'total': 0, 'by_category': {}}

    categories = {}
    total = 0

    for item in playbooks_dir.iterdir():
        if item.is_dir():
            category_name = item.name
            md_files = list(item.glob('*.md'))
            count = len([f for f in md_files if f.name != 'INDEX.md'])
            if count > 0:
                categories[category_name] = count
                total += count
        elif item.suffix == '.md' and item.name not in ['INDEX.md', 'README.md']:
            if 'root' not in categories:
                categories['root'] = 0
            categories['root'] += 1
            total += 1

    return {
        'total': total,
        'by_category': categories,
    }


def _get_system_owner() -> Dict[str, Any]:
    """Get system owner information."""
    # This could be configurable in the future
    return {
        'name': 'Chris West',
        'authority': 'Absolute',
        'override_level': 'All Decisions',
        'contact': 'Discord @chriswest',
    }


def _get_emergency_status() -> Dict[str, Any]:
    """Get emergency control status."""
    from core.models_skin import SkinStatus
    from core.models_human_interface import HumanAttentionItem

    # Check if SKIN is in a "locked" state (damaged/healing = restricted)
    try:
        latest_skin = SkinStatus.objects.order_by('-timestamp').first()
        skin_locked = latest_skin and latest_skin.status in ['damaged', 'healing'] if latest_skin else False
        skin_status = latest_skin.status if latest_skin else 'unknown'
    except Exception:
        skin_locked = False
        skin_status = 'unknown'

    # Check for quarantined agents (agents with recent critical failures)
    quarantined_agents = []  # Would need a dedicated model for this

    # Check for system pause status (Celery status)
    system_paused = False  # Would check Celery status

    # Count pending critical decisions
    pending_critical = HumanAttentionItem.objects.filter(
        status='pending',
        urgency='critical'
    ).count()

    return {
        'skin_lock': skin_locked,
        'skin_status': skin_status,
        'quarantined_agents': quarantined_agents,
        'quarantined_count': len(quarantined_agents),
        'system_paused': system_paused,
        'pending_critical_decisions': pending_critical,
    }


def _get_pending_decisions() -> List[Dict[str, Any]]:
    """Get pending human decisions."""
    from core.models_human_interface import HumanAttentionItem

    pending = HumanAttentionItem.objects.filter(
        status='pending'
    ).order_by('-urgency', '-priority_score', '-created_at')[:20]

    return [{
        'id': str(item.id),
        'title': item.title,
        'summary': item.summary[:200] + '...' if len(item.summary) > 200 else item.summary,
        'urgency': item.urgency,
        'item_type': item.item_type,
        'source_type': item.source_type,
        'source_agent': item.source_agent,
        'created_at': item.created_at.isoformat(),
        'ml_recommendation': item.ml_recommendation,
    } for item in pending]


def _list_canon_docs() -> List[Dict[str, Any]]:
    """List all canon documents with metadata."""
    canon_dir = _get_docs_dir() / 'canon'

    if not canon_dir.exists():
        return []

    docs = []

    def _extract_title(content: str) -> str:
        """Extract title from markdown."""
        for line in content.split('\n')[:10]:
            if line.startswith('# '):
                return line[2:].strip()
        return None

    def _process_file(file_path: Path, category: str) -> Optional[Dict]:
        if file_path.name in ['INDEX.md', 'README.md']:
            return None

        try:
            content = file_path.read_text()
            title = _extract_title(content) or file_path.stem.replace('_', ' ').replace('-', ' ').title()

            # Get file stats
            stat = file_path.stat()

            return {
                'path': str(file_path.relative_to(settings.BASE_DIR)),
                'name': file_path.name,
                'title': title,
                'category': category,
                'size_bytes': stat.st_size,
                'modified_at': datetime.fromtimestamp(stat.st_mtime, tz=dt_timezone.utc).isoformat(),
                'lines': content.count('\n') + 1,
            }
        except Exception as e:
            logger.error(f"Error reading canon doc {file_path}: {e}")
            return None

    # Process root files
    for item in canon_dir.glob('*.md'):
        doc = _process_file(item, 'root')
        if doc:
            docs.append(doc)

    # Process category directories
    for cat_dir in canon_dir.iterdir():
        if cat_dir.is_dir():
            category = cat_dir.name
            for md_file in cat_dir.glob('*.md'):
                doc = _process_file(md_file, category)
                if doc:
                    docs.append(doc)

    # Sort by category, then title
    docs.sort(key=lambda d: (d['category'], d['title']))

    return docs


def _list_playbooks() -> List[Dict[str, Any]]:
    """List all playbooks with metadata."""
    playbooks_dir = _get_docs_dir() / 'playbooks'

    if not playbooks_dir.exists():
        return []

    playbooks = []

    def _extract_description(content: str) -> str:
        """Extract first paragraph as description."""
        lines = content.split('\n')
        desc_lines = []
        in_desc = False

        for line in lines:
            # Skip title line
            if line.startswith('#'):
                in_desc = True
                continue

            # Skip empty lines at start
            if not in_desc and not line.strip():
                continue

            # Start collecting description
            if in_desc:
                if not line.strip():
                    if desc_lines:
                        break
                    continue
                if line.startswith('#') or line.startswith('---') or line.startswith('|'):
                    break
                desc_lines.append(line.strip())

        return ' '.join(desc_lines)[:200] if desc_lines else ''

    def _process_playbook(file_path: Path, category: str) -> Optional[Dict]:
        if file_path.name in ['INDEX.md', 'README.md']:
            return None

        try:
            content = file_path.read_text()

            # Extract title
            title = None
            for line in content.split('\n')[:5]:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break

            if not title:
                title = file_path.stem.replace('_', ' ').replace('-', ' ').title()

            description = _extract_description(content)
            stat = file_path.stat()

            return {
                'path': str(file_path.relative_to(settings.BASE_DIR)),
                'name': file_path.name,
                'title': title,
                'description': description,
                'category': category,
                'size_bytes': stat.st_size,
                'modified_at': datetime.fromtimestamp(stat.st_mtime, tz=dt_timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error reading playbook {file_path}: {e}")
            return None

    # Process root files
    for item in playbooks_dir.glob('*.md'):
        pb = _process_playbook(item, 'root')
        if pb:
            playbooks.append(pb)

    # Process category directories
    for cat_dir in playbooks_dir.iterdir():
        if cat_dir.is_dir():
            category = cat_dir.name
            for md_file in cat_dir.glob('*.md'):
                pb = _process_playbook(md_file, category)
                if pb:
                    playbooks.append(pb)

    # Sort by category, then title
    playbooks.sort(key=lambda p: (p['category'], p['title']))

    return playbooks


def _get_recent_activity() -> List[Dict[str, Any]]:
    """Get recent agent activity for the command center feed."""
    from core.models_unified_system import AgentExecution

    recent = AgentExecution.objects.filter(
        status__in=['completed', 'failed']
    ).select_related('agent').order_by('-completed_at')[:10]

    results = []
    for ex in recent:
        # Extract summary from output_data if available
        output_summary = None
        tool_results = []
        if ex.output_data:
            # Try to get a summary or description from output
            if isinstance(ex.output_data, dict):
                output_summary = ex.output_data.get('summary') or ex.output_data.get('description') or ex.output_data.get('content', '')[:500]
                # Extract tool results if present
                if 'tool_results' in ex.output_data:
                    tool_results = ex.output_data.get('tool_results', [])[:5]  # Limit to 5 tools
                elif 'tools_used' in ex.output_data:
                    tool_results = ex.output_data.get('tools_used', [])[:5]

        results.append({
            'id': str(ex.id),
            'agent_name': ex.agent.name if ex.agent else 'Unknown',
            'agent_category': ex.agent.category if ex.agent else None,
            'task': ex.task[:100] if ex.task else 'Task completed',
            'task_full': ex.task if ex.task else 'Task completed',
            'completed_at': ex.completed_at.isoformat() if ex.completed_at else None,
            'success': ex.status == 'completed',
            'status': ex.status,
            'execution_time_ms': ex.execution_time_ms,
            'tokens_used': ex.tokens_used,
            'cost': float(ex.cost) if ex.cost else 0,
            'error_message': ex.error_message if ex.status == 'failed' else None,
            'output_summary': output_summary[:500] if output_summary else None,
            'tool_results': tool_results,
        })

    return results


# =============================================================================
# API Endpoints
# =============================================================================

@require_GET
def mission_view(request):
    """
    GET /api/platform/mission/

    Returns current mission with basic metrics summary.
    """
    mission = _parse_mission_file()
    revenue = _get_revenue_metrics()
    costs = _get_llm_cost_metrics()
    canon = _count_canon_docs()
    playbooks = _count_playbooks()

    targets = mission.get('metrics_targets', {})

    return JsonResponse({
        'mission': {
            'status': mission.get('status'),
            'statement': mission.get('statement'),
            'goal': mission.get('goal'),
            'period': mission.get('period'),
            'session': mission.get('session'),
            'priorities': mission.get('priorities', []),
        },
        'metrics_summary': {
            'revenue': {
                'current': revenue['monthly'],
                'target': targets.get('monthly_revenue', 10000),
                'progress_pct': min(100, (revenue['monthly'] / targets.get('monthly_revenue', 10000)) * 100) if targets.get('monthly_revenue') else 0,
            },
            'llm_cost': {
                'current': costs['daily']['cost'],
                'target': targets.get('daily_llm_cost', 50),
                'progress_pct': min(100, (costs['daily']['cost'] / targets.get('daily_llm_cost', 50)) * 100) if targets.get('daily_llm_cost') else 0,
            },
            'canon': {
                'current': canon['total'],
                'target': targets.get('canon_docs', 20),
                'progress_pct': min(100, (canon['total'] / targets.get('canon_docs', 20)) * 100) if targets.get('canon_docs') else 0,
            },
            'playbooks': {
                'current': playbooks['total'],
                'target': targets.get('playbooks', 10),
                'progress_pct': min(100, (playbooks['total'] / targets.get('playbooks', 10)) * 100) if targets.get('playbooks') else 0,
            },
        },
    })


@require_GET
def metrics_view(request):
    """
    GET /api/platform/metrics/

    Returns detailed metrics for the command center.
    """
    revenue = _get_revenue_metrics()
    costs = _get_llm_cost_metrics()
    canon = _count_canon_docs()
    playbooks = _count_playbooks()
    activity = _get_recent_activity()

    return JsonResponse({
        'revenue': revenue,
        'llm_costs': costs,
        'canon': canon,
        'playbooks': playbooks,
        'recent_activity': activity,
    })


@require_GET
def governance_view(request):
    """
    GET /api/platform/governance/

    Returns governance controls and system owner info.
    """
    owner = _get_system_owner()
    emergency = _get_emergency_status()
    decisions = _get_pending_decisions()

    return JsonResponse({
        'owner': owner,
        'emergency_controls': emergency,
        'pending_decisions': decisions,
        'pending_decisions_count': len(decisions),
        'authority_escalation_path': [
            {'level': 1, 'entity': 'Agent', 'scope': 'Routine tasks'},
            {'level': 2, 'entity': 'Thinking Agent', 'scope': 'Strategic decisions'},
            {'level': 3, 'entity': 'Human (Chris)', 'scope': 'All overrides'},
        ],
    })


@csrf_exempt
@require_POST
def emergency_halt_view(request):
    """
    POST /api/platform/emergency-halt/

    Trigger emergency halt of autonomous operations.
    This should:
    1. Set SKIN to "locked" state
    2. Signal Celery to pause autonomous tasks
    3. Create a critical attention item

    For now, this is a placeholder that creates an attention item.
    """
    from core.models_human_interface import HumanAttentionItem

    # Verify authentication (in production, add proper auth)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        # Create critical attention item
        item = HumanAttentionItem.objects.create(
            user=request.user,
            source_type='platform_command',
            source_id='emergency_halt',
            item_type='alert',
            title='EMERGENCY HALT TRIGGERED',
            summary='Emergency halt was triggered from Platform Command Center. All autonomous operations should be reviewed before resuming.',
            urgency=HumanAttentionItem.URGENCY_CRITICAL,
            priority_score=100.0,
            payload={
                'triggered_by': request.user.username,
                'triggered_at': timezone.now().isoformat(),
                'action': 'emergency_halt',
            },
        )

        logger.warning(f"EMERGENCY HALT triggered by {request.user.username}")

        return JsonResponse({
            'success': True,
            'message': 'Emergency halt triggered. Review pending items before resuming.',
            'attention_item_id': str(item.id),
        })
    except Exception as e:
        logger.error(f"Emergency halt failed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_GET
def canon_view(request):
    """
    GET /api/platform/canon/

    Returns list of canon documents.

    Query params:
    - category: Filter by category
    """
    docs = _list_canon_docs()
    counts = _count_canon_docs()

    category_filter = request.GET.get('category')
    if category_filter:
        docs = [d for d in docs if d['category'] == category_filter]

    return JsonResponse({
        'documents': docs,
        'total': counts['total'],
        'by_category': counts['by_category'],
        'filtered_count': len(docs),
    })


@require_GET
def playbooks_view(request):
    """
    GET /api/platform/playbooks/

    Returns list of playbooks.

    Query params:
    - category: Filter by category
    """
    playbooks = _list_playbooks()
    counts = _count_playbooks()

    category_filter = request.GET.get('category')
    if category_filter:
        playbooks = [p for p in playbooks if p['category'] == category_filter]

    return JsonResponse({
        'playbooks': playbooks,
        'total': counts['total'],
        'by_category': counts['by_category'],
        'filtered_count': len(playbooks),
    })


# =============================================================================
# Session 816: Audits API
# =============================================================================

def _count_audits() -> Dict[str, Any]:
    """Count audit documents by type."""
    audits_dir = _get_docs_dir() / 'audits'

    if not audits_dir.exists():
        return {'total': 0, 'by_type': {}}

    by_type: Dict[str, int] = {}
    total = 0

    for item in audits_dir.glob('*.md'):
        if item.is_file():
            # Categorize by filename prefix
            name = item.stem.lower()
            if name.startswith('session_'):
                audit_type = 'session'
            elif name.startswith('audit_'):
                audit_type = 'system'
            elif 'integration' in name:
                audit_type = 'integration'
            elif 'database' in name or 'db' in name:
                audit_type = 'database'
            elif 'archive' in name:
                audit_type = 'archive'
            else:
                audit_type = 'other'

            by_type[audit_type] = by_type.get(audit_type, 0) + 1
            total += 1

    return {'total': total, 'by_type': by_type}


def _list_audits() -> List[Dict[str, Any]]:
    """List all audit documents with metadata."""
    audits_dir = _get_docs_dir() / 'audits'

    if not audits_dir.exists():
        return []

    audits = []

    def _extract_title(content: str, filename: str) -> str:
        """Extract title from markdown content."""
        lines = content.split('\n')
        for line in lines[:10]:
            if line.startswith('# '):
                return line[2:].strip()
        # Fallback: convert filename to title
        return filename.replace('_', ' ').replace('.md', '').title()

    def _extract_summary(content: str) -> str:
        """Extract summary from markdown content."""
        lines = content.split('\n')
        in_summary = False
        summary_lines = []

        for line in lines:
            if line.strip().lower() in ['## summary', '## overview', '---']:
                if line.strip() == '---' and in_summary:
                    break
                in_summary = line.strip().lower() in ['## summary', '## overview']
                continue
            if in_summary and line.strip():
                summary_lines.append(line.strip())
                if len(summary_lines) >= 3:
                    break

        return ' '.join(summary_lines)[:200] if summary_lines else ''

    def _get_audit_type(name: str) -> str:
        """Determine audit type from filename."""
        name = name.lower()
        if name.startswith('session_'):
            return 'session'
        elif name.startswith('audit_'):
            return 'system'
        elif 'integration' in name:
            return 'integration'
        elif 'database' in name or 'db' in name:
            return 'database'
        elif 'archive' in name:
            return 'archive'
        return 'other'

    def _process_audit(file_path: Path) -> Optional[Dict[str, Any]]:
        """Process a single audit file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            stat = file_path.stat()

            return {
                'path': f"docs/audits/{file_path.name}",
                'name': file_path.name,
                'title': _extract_title(content, file_path.name),
                'summary': _extract_summary(content),
                'audit_type': _get_audit_type(file_path.stem),
                'size_bytes': stat.st_size,
                'modified_at': datetime.fromtimestamp(stat.st_mtime, tz=dt_timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error reading audit {file_path}: {e}")
            return None

    # Process all audit files
    for item in audits_dir.glob('*.md'):
        if item.is_file():
            audit = _process_audit(item)
            if audit:
                audits.append(audit)

    # Sort by modified date (newest first)
    audits.sort(key=lambda a: a['modified_at'], reverse=True)

    return audits


@require_GET
def audits_view(request):
    """
    GET /api/platform/audits/

    Returns list of audit documents.

    Query params:
    - type: Filter by audit type (session, system, integration, database, archive, other)
    """
    audits = _list_audits()
    counts = _count_audits()

    type_filter = request.GET.get('type')
    if type_filter:
        audits = [a for a in audits if a['audit_type'] == type_filter]

    return JsonResponse({
        'audits': audits,
        'total': counts['total'],
        'by_type': counts['by_type'],
        'filtered_count': len(audits),
    })


# =============================================================================
# Session 818: Document Content API
# =============================================================================

@csrf_exempt
@require_POST
def skin_lock_toggle_view(request):
    """
    POST /api/platform/skin-lock/

    Toggle the SKIN lock status. When locked, agents cannot write to workspaces.

    Session 818: Real emergency control for SKIN layer.
    """
    from core.models_skin import SkinStatus

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        import json
        body = json.loads(request.body) if request.body else {}
        action = body.get('action', 'toggle')  # 'lock', 'unlock', or 'toggle'

        # Get or create the singleton status (id=1)
        skin_status, created = SkinStatus.objects.get_or_create(id=1)
        current_locked = skin_status.status in ['damaged', 'healing']

        # Determine new status
        if action == 'lock':
            new_locked = True
        elif action == 'unlock':
            new_locked = False
        else:  # toggle
            new_locked = not current_locked

        # Update the singleton status
        new_status = 'damaged' if new_locked else 'healthy'
        skin_status.status = new_status
        skin_status.is_healthy = not new_locked
        skin_status.health_score = 0.0 if new_locked else 100.0
        skin_status.save()

        logger.info(f"SKIN {'LOCKED' if new_locked else 'UNLOCKED'} by {request.user.username}")

        return JsonResponse({
            'success': True,
            'locked': new_locked,
            'status': new_status,
            'message': f"SKIN {'locked' if new_locked else 'unlocked'} successfully"
        })
    except Exception as e:
        logger.error(f"SKIN lock toggle failed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def doc_content_view(request):
    """
    GET /api/platform/doc-content/

    Fetch the content of a documentation file.

    Query params:
    - path: Relative path to the document (e.g., 'docs/canon/example.md')

    Returns:
    - content: Raw markdown content
    - metadata: Title, lines, size, modified date
    """
    doc_path = request.GET.get('path', '')

    if not doc_path:
        return JsonResponse({
            'error': 'Missing path parameter'
        }, status=400)

    # Security: Only allow reading from docs/ directory
    if not doc_path.startswith('docs/'):
        return JsonResponse({
            'error': 'Invalid path - must be within docs/ directory'
        }, status=403)

    # Security: Prevent directory traversal
    if '..' in doc_path:
        return JsonResponse({
            'error': 'Invalid path - directory traversal not allowed'
        }, status=403)

    # Build full path
    full_path = Path(settings.BASE_DIR) / doc_path

    if not full_path.exists():
        return JsonResponse({
            'error': f'Document not found: {doc_path}'
        }, status=404)

    if not full_path.is_file():
        return JsonResponse({
            'error': 'Path is not a file'
        }, status=400)

    # Only allow markdown files
    if full_path.suffix.lower() not in ['.md', '.markdown']:
        return JsonResponse({
            'error': 'Only markdown files are supported'
        }, status=400)

    try:
        content = full_path.read_text(encoding='utf-8')
        stat = full_path.stat()

        # Extract title from content
        title = None
        for line in content.split('\n')[:10]:
            if line.startswith('# '):
                title = line[2:].strip()
                break

        if not title:
            title = full_path.stem.replace('_', ' ').replace('-', ' ').title()

        return JsonResponse({
            'content': content,
            'metadata': {
                'path': doc_path,
                'name': full_path.name,
                'title': title,
                'lines': content.count('\n') + 1,
                'size_bytes': stat.st_size,
                'modified_at': datetime.fromtimestamp(stat.st_mtime, tz=dt_timezone.utc).isoformat(),
            }
        })
    except Exception as e:
        logger.error(f"Error reading document {doc_path}: {e}")
        return JsonResponse({
            'error': f'Error reading document: {str(e)}'
        }, status=500)


# =============================================================================
# Session 819: Canon Promotion API
# =============================================================================

@csrf_exempt
@require_POST
def canon_promote_view(request):
    """
    POST /api/platform/canon/promote/

    Promote content to the Canon documentation.

    Session 819: Allows promoting high-quality agent outputs to canonical docs.

    Request body:
    {
        "title": "Document Title",
        "content": "Markdown content to promote",
        "category": "creative" | "technical" | "operational",
        "source_type": "agent_output" | "blog" | "document",
        "source_id": "optional source identifier",
        "tags": ["optional", "tags"]
    }

    Returns:
    {
        "success": true,
        "path": "docs/canon/creative/document_title.md",
        "message": "Successfully promoted to Canon"
    }
    """
    import json
    import re
    from slugify import slugify

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        body = json.loads(request.body) if request.body else {}

        # Required fields
        title = body.get('title', '').strip()
        content = body.get('content', '').strip()
        category = body.get('category', 'operational').lower()

        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)

        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)

        # Validate category
        valid_categories = ['creative', 'technical', 'operational']
        if category not in valid_categories:
            return JsonResponse({
                'error': f'Invalid category. Must be one of: {", ".join(valid_categories)}'
            }, status=400)

        # Optional fields
        source_type = body.get('source_type', 'document')
        source_id = body.get('source_id', '')
        tags = body.get('tags', [])

        # Generate filename from title
        try:
            filename = slugify(title, separator='_').upper() + '.md'
        except Exception:
            # Fallback if slugify not available
            filename = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_').upper() + '.md'

        # Build full path
        canon_dir = _get_docs_dir() / 'canon' / category
        canon_dir.mkdir(parents=True, exist_ok=True)
        doc_path = canon_dir / filename

        # Check if file already exists
        if doc_path.exists():
            return JsonResponse({
                'error': f'Document already exists: {filename}',
                'existing_path': str(doc_path.relative_to(settings.BASE_DIR))
            }, status=409)

        # Build document content with metadata header
        promoted_at = timezone.now().strftime('%Y-%m-%d')
        promoted_by = request.user.username

        doc_content = f"""# {title}

**Category:** {category.title()}
**Promoted:** {promoted_at} by {promoted_by}
**Source:** {source_type}
"""
        if source_id:
            doc_content += f"**Source ID:** {source_id}\n"

        if tags:
            doc_content += f"**Tags:** {', '.join(tags)}\n"

        doc_content += f"""
---

{content}
"""

        # Write the file
        doc_path.write_text(doc_content, encoding='utf-8')

        logger.info(f"Canon document created: {doc_path} by {promoted_by}")

        # Return relative path for display
        relative_path = f"docs/canon/{category}/{filename}"

        return JsonResponse({
            'success': True,
            'path': relative_path,
            'message': f'Successfully promoted "{title}" to Canon ({category})',
            'metadata': {
                'title': title,
                'category': category,
                'filename': filename,
                'promoted_at': promoted_at,
                'promoted_by': promoted_by,
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        logger.error(f"Canon promotion failed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 819: System Audit Trigger API
# =============================================================================

@csrf_exempt
@require_POST
def audit_run_view(request):
    """
    POST /api/platform/audits/run/

    Trigger a comprehensive system audit and save to docs/audits/.

    Session 819: Allows triggering audits from the UI.

    Returns:
    {
        "success": true,
        "audit_path": "docs/audits/SESSION_819_SYSTEM_AUDIT.md",
        "summary": {...},
        "message": "System audit completed"
    }
    """
    import subprocess
    import os

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        # Run the comprehensive system audit
        results = _run_system_audit()

        # Generate the audit report
        audit_filename = f"SESSION_819_SYSTEM_AUDIT_{timezone.now().strftime('%Y%m%d_%H%M%S')}.md"
        audit_path = _get_docs_dir() / 'audits' / audit_filename

        # Ensure audits directory exists
        audit_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate markdown report
        report_content = _generate_audit_report(results, request.user.username)

        # Save the report
        audit_path.write_text(report_content, encoding='utf-8')

        logger.info(f"System audit completed by {request.user.username}: {audit_path}")

        return JsonResponse({
            'success': True,
            'audit_path': f"docs/audits/{audit_filename}",
            'summary': {
                'passed': results['passed'],
                'failed': results['failed'],
                'warnings': results['warnings'],
                'total_checks': results['passed'] + results['failed'] + results['warnings'],
                'health_score': results.get('health_score', 0),
            },
            'message': f"System audit completed - {results['passed']} passed, {results['failed']} failed, {results['warnings']} warnings"
        })

    except Exception as e:
        logger.error(f"System audit failed: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _run_system_audit() -> Dict[str, Any]:
    """
    Run comprehensive system audit checks.

    Session 819: Adapted from system_health_check management command for API use.
    """
    import os
    import subprocess

    results = {
        'passed': 0,
        'failed': 0,
        'warnings': 0,
        'checks': [],
        'timestamp': timezone.now().isoformat(),
    }

    def _pass(category: str, check: str, detail: str = ""):
        results['passed'] += 1
        results['checks'].append({
            'status': 'pass',
            'category': category,
            'check': check,
            'detail': detail
        })

    def _fail(category: str, check: str, detail: str = ""):
        results['failed'] += 1
        results['checks'].append({
            'status': 'fail',
            'category': category,
            'check': check,
            'detail': detail
        })

    def _warn(category: str, check: str, detail: str = ""):
        results['warnings'] += 1
        results['checks'].append({
            'status': 'warn',
            'category': category,
            'check': check,
            'detail': detail
        })

    # === SERVICES ===
    # Redis
    try:
        import redis
        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
        r.ping()
        _pass('services', 'Redis connected')
    except Exception as e:
        _fail('services', 'Redis connection', str(e))

    # PostgreSQL
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        _pass('services', 'PostgreSQL connected')
    except Exception as e:
        _fail('services', 'PostgreSQL connection', str(e))

    # Daphne
    try:
        import requests
        resp = requests.get('http://localhost:8000/health/ping/', timeout=5)
        if resp.status_code == 200:
            _pass('services', 'Daphne/Django running')
        else:
            _fail('services', 'Daphne health check', f'Status {resp.status_code}')
    except Exception as e:
        _fail('services', 'Daphne connection', str(e))

    # === DATABASE ===
    try:
        from django.apps import apps
        model_count = len(apps.get_models())
        if model_count > 300:
            _pass('database', f'{model_count} Django models registered')
        else:
            _warn('database', f'Only {model_count} models (expected 300+)')
    except Exception as e:
        _fail('database', 'Model count', str(e))

    # Key tables
    try:
        from core.models_unified_system import Agent
        agent_count = Agent.objects.count()
        active_count = Agent.objects.filter(is_active=True).count()
        _pass('database', f'Agents: {active_count} active / {agent_count} total')
    except Exception as e:
        _fail('database', 'Agents table', str(e))

    try:
        from core.models import AgentDream
        dream_count = AgentDream.objects.count()
        _pass('database', f'Agent Dreams: {dream_count}')
    except Exception as e:
        _fail('database', 'Agent Dreams table', str(e))

    try:
        from core.models import AgentConversation
        conv_count = AgentConversation.objects.count()
        _pass('database', f'Agent Conversations: {conv_count}')
    except Exception as e:
        _fail('database', 'Agent Conversations table', str(e))

    try:
        from core.models import SelfBlog
        blog_count = SelfBlog.objects.count()
        _pass('database', f'Self Blogs: {blog_count}')
    except Exception as e:
        _fail('database', 'Self Blogs table', str(e))

    # === AGENTS ===
    try:
        from core.agent_router import AgentRouter
        _pass('agents', 'AgentRouter available')
    except Exception as e:
        _fail('agents', 'AgentRouter', str(e))

    # === SPIDERS ===
    try:
        from ai_core.spiders.spider_registry import get_spider_registry
        registry = get_spider_registry()
        spiders = registry.list_spiders()
        spider_count = len(spiders)
        if spider_count >= 70:
            _pass('spiders', f'{spider_count} spiders registered')
        else:
            _warn('spiders', f'Only {spider_count} spiders (expected 70+)')
    except Exception as e:
        _warn('spiders', 'Spider registry', str(e))

    # === CELERY ===
    try:
        result = subprocess.run(['pgrep', '-f', 'celery.*worker'], capture_output=True)
        if result.returncode == 0:
            worker_pids = result.stdout.decode().strip().split('\n')
            _pass('celery', f'{len(worker_pids)} Celery worker processes')
        else:
            _fail('celery', 'No Celery workers found')
    except Exception as e:
        _fail('celery', 'Celery worker check', str(e))

    try:
        result = subprocess.run(['pgrep', '-f', 'celery.*beat'], capture_output=True)
        if result.returncode == 0:
            _pass('celery', 'Celery beat scheduler running')
        else:
            _fail('celery', 'Celery beat not running')
    except Exception as e:
        _fail('celery', 'Celery beat check', str(e))

    # === CONTENT SYSTEM ===
    try:
        from core.models_autonomous_studio import ContentChannel, ChannelEpisode
        channels = ContentChannel.objects.filter(status='active').count()
        episodes = ChannelEpisode.objects.count()
        if channels > 0:
            _pass('content', f'{channels} active channels, {episodes} episodes')
        else:
            _warn('content', 'No active content channels')
    except Exception as e:
        _fail('content', 'Content system', str(e))

    # === PILOTS ===
    try:
        from core.models_pilot_readiness import PilotExecution, Experiment, PilotReadinessGate
        pilots = PilotExecution.objects.count()
        experiments = Experiment.objects.count()
        gates = PilotReadinessGate.objects.count()
        _pass('pilots', f'{pilots} pilots, {experiments} experiments, {gates} gates')
    except Exception as e:
        _fail('pilots', 'Pilot system', str(e))

    # === ML MODELS ===
    openai_key = os.environ.get('OPENAI_API_KEY')
    if openai_key and len(openai_key) > 10:
        _pass('ml', 'OpenAI API key configured')
    else:
        _fail('ml', 'OpenAI API key missing')

    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    if anthropic_key and len(anthropic_key) > 10:
        _pass('ml', 'Anthropic API key configured')
    else:
        _warn('ml', 'Anthropic API key not configured')

    # === BODY SYSTEMS ===
    body_systems = ['heart', 'lungs', 'circulatory', 'spine', 'immune', 'digestive', 'muscular', 'brain', 'skin']
    for system in body_systems:
        try:
            from core.models_body_vitals import BodySystemHealth
            health = BodySystemHealth.objects.filter(system_name=system).first()
            if health:
                if health.is_healthy:
                    _pass('body_systems', f'{system.upper()} system healthy')
                else:
                    _warn('body_systems', f'{system.upper()} system unhealthy')
            else:
                _warn('body_systems', f'{system.upper()} system status unknown')
        except Exception:
            _warn('body_systems', f'{system.upper()} system check failed')

    # Calculate health score
    total = results['passed'] + results['failed'] + results['warnings']
    if total > 0:
        results['health_score'] = int((results['passed'] / total) * 100)
    else:
        results['health_score'] = 0

    return results


def _generate_audit_report(results: Dict[str, Any], username: str) -> str:
    """
    Generate a markdown audit report.

    Session 819: Creates readable audit documents for docs/audits/.
    """
    timestamp = results.get('timestamp', timezone.now().isoformat())
    health_score = results.get('health_score', 0)
    passed = results['passed']
    failed = results['failed']
    warnings = results['warnings']
    total = passed + failed + warnings

    # Determine status
    if failed == 0 and warnings == 0:
        status = "HEALTHY"
        status_emoji = "✅"
    elif failed == 0:
        status = "WARNINGS"
        status_emoji = "⚠️"
    else:
        status = "ISSUES FOUND"
        status_emoji = "❌"

    report = f"""# System Audit Report

**Generated:** {timestamp}
**Triggered by:** {username}
**Status:** {status_emoji} {status}
**Health Score:** {health_score}%

---

## Summary

| Metric | Count |
|--------|-------|
| Total Checks | {total} |
| ✅ Passed | {passed} |
| ⚠️ Warnings | {warnings} |
| ❌ Failed | {failed} |

---

## Checks by Category

"""

    # Group checks by category
    categories = {}
    for check in results['checks']:
        cat = check['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(check)

    for category, checks in sorted(categories.items()):
        cat_passed = sum(1 for c in checks if c['status'] == 'pass')
        cat_failed = sum(1 for c in checks if c['status'] == 'fail')
        cat_warnings = sum(1 for c in checks if c['status'] == 'warn')

        report += f"### {category.upper().replace('_', ' ')}\n\n"
        report += f"*{cat_passed} passed, {cat_warnings} warnings, {cat_failed} failed*\n\n"

        for check in checks:
            if check['status'] == 'pass':
                emoji = "✅"
            elif check['status'] == 'warn':
                emoji = "⚠️"
            else:
                emoji = "❌"

            report += f"- {emoji} {check['check']}"
            if check.get('detail'):
                report += f" - {check['detail']}"
            report += "\n"

        report += "\n"

    # Add failed checks section if any
    failed_checks = [c for c in results['checks'] if c['status'] == 'fail']
    if failed_checks:
        report += """---

## Failed Checks (Action Required)

"""
        for check in failed_checks:
            report += f"- **[{check['category']}]** {check['check']}"
            if check.get('detail'):
                report += f" - {check['detail']}"
            report += "\n"

    # Add warnings section if any
    warning_checks = [c for c in results['checks'] if c['status'] == 'warn']
    if warning_checks:
        report += """
---

## Warnings (Review Recommended)

"""
        for check in warning_checks:
            report += f"- **[{check['category']}]** {check['check']}"
            if check.get('detail'):
                report += f" - {check['detail']}"
            report += "\n"

    report += f"""
---

*Generated by Session 819 System Audit API*
"""

    return report


# =============================================================================
# Session 824: Live Metrics API
# =============================================================================

@require_GET
def live_metrics_view(request):
    """
    GET /api/platform/live-metrics/

    Returns real-time system metrics by calling _gather_live_system_metrics().

    Session 824: Exposes the self-awareness metrics to the UI.
    """
    try:
        from core.tasks import _gather_live_system_metrics
        metrics = _gather_live_system_metrics()

        return JsonResponse({
            'success': True,
            'metrics': metrics,
        })
    except Exception as e:
        logger.error(f"Failed to gather live metrics: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


# =============================================================================
# Session 824: Trigger Rules API
# =============================================================================

@require_GET
def triggers_list_view(request):
    """
    GET /api/platform/triggers/

    Returns all trigger rules with their current status.

    Session 824: Exposes MetricsActionTrigger rules to the UI.
    """
    try:
        from core.services.metrics_action_trigger import MetricsActionTrigger

        trigger_service = MetricsActionTrigger()
        rules = trigger_service.get_rules_summary()

        return JsonResponse({
            'success': True,
            'rules': rules,
            'total': len(rules),
            'enabled_count': sum(1 for r in rules if r['enabled']),
        })
    except Exception as e:
        logger.error(f"Failed to list triggers: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@csrf_exempt
@require_POST
def trigger_toggle_view(request, rule_name: str):
    """
    POST /api/platform/triggers/<name>/toggle/

    Toggle a trigger rule's enabled state.

    Note: Currently rules are in-memory, so this toggle is session-scoped.
    For persistence, would need to store enabled state in database.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        from core.services.metrics_action_trigger import MetricsActionTrigger

        trigger_service = MetricsActionTrigger()

        # Find the rule
        rule_found = False
        for rule in trigger_service.rules:
            if rule.condition.name == rule_name:
                rule.enabled = not rule.enabled
                rule_found = True
                new_state = rule.enabled
                break

        if not rule_found:
            return JsonResponse({
                'success': False,
                'error': f'Rule not found: {rule_name}'
            }, status=404)

        logger.info(f"Trigger rule {rule_name} {'enabled' if new_state else 'disabled'} by {request.user.username}")

        return JsonResponse({
            'success': True,
            'rule_name': rule_name,
            'enabled': new_state,
            'message': f"Rule {'enabled' if new_state else 'disabled'}",
        })
    except Exception as e:
        logger.error(f"Failed to toggle trigger: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@csrf_exempt
@require_POST
def trigger_run_now_view(request):
    """
    POST /api/platform/triggers/run-now/

    Manually run the metrics check and trigger any matching actions.

    Session 824: Allows on-demand self-execution from the UI.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        from core.tasks import run_metrics_action_check

        # Run synchronously for immediate feedback
        result = run_metrics_action_check()

        logger.info(f"Manual metrics check triggered by {request.user.username}: {result.get('actions_triggered', 0)} actions")

        return JsonResponse({
            'success': True,
            'result': result,
            'message': f"Metrics check completed. {result.get('actions_triggered', 0)} actions triggered.",
        })
    except Exception as e:
        logger.error(f"Failed to run metrics check: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


# =============================================================================
# Session 824: Manual Actions API
# =============================================================================

@csrf_exempt
@require_POST
def action_run_spiders_view(request):
    """
    POST /api/platform/actions/run-spiders/

    Trigger spider network to collect fresh data.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        import json
        body = json.loads(request.body) if request.body else {}
        category = body.get('category')  # Optional: run specific category

        from core.tasks import run_spider_network, run_spider_by_category

        if category:
            run_spider_by_category.delay(category=category)
            message = f"Spider category '{category}' triggered"
        else:
            run_spider_network.delay()
            message = "Full spider network triggered"

        logger.info(f"{message} by {request.user.username}")

        return JsonResponse({
            'success': True,
            'message': message,
            'category': category,
        })
    except Exception as e:
        logger.error(f"Failed to run spiders: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@csrf_exempt
@require_POST
def action_run_remediation_view(request):
    """
    POST /api/platform/actions/run-remediation/

    Trigger autonomous remediation cycle.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        import json
        body = json.loads(request.body) if request.body else {}
        limit = body.get('limit', 5)  # Default to 5 findings

        from core.tasks import run_autonomous_remediation_cycle

        run_autonomous_remediation_cycle.delay(limit=limit)

        message = f"Remediation cycle triggered (limit: {limit})"
        logger.info(f"{message} by {request.user.username}")

        return JsonResponse({
            'success': True,
            'message': message,
            'limit': limit,
        })
    except Exception as e:
        logger.error(f"Failed to run remediation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@csrf_exempt
@require_POST
def action_agent_health_check_view(request):
    """
    POST /api/platform/actions/agent-health-check/

    Trigger agent health rotation check.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        from core.tasks import run_agent_health_rotation

        run_agent_health_rotation.delay()

        message = "Agent health rotation triggered"
        logger.info(f"{message} by {request.user.username}")

        return JsonResponse({
            'success': True,
            'message': message,
        })
    except Exception as e:
        logger.error(f"Failed to run agent health check: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@csrf_exempt
@require_POST
def action_run_self_audit_view(request):
    """
    POST /api/platform/actions/run-self-audit/

    Trigger system self-audit with live data.

    Session 824: Uses the enhanced self-audit from Session 823.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        from core.tasks import run_system_self_audit

        run_system_self_audit.delay()

        message = "System self-audit triggered (will save to docs/audits/)"
        logger.info(f"{message} by {request.user.username}")

        return JsonResponse({
            'success': True,
            'message': message,
        })
    except Exception as e:
        logger.error(f"Failed to run self-audit: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


# =============================================================================
# Session 824: Remediation Status API
# =============================================================================

@require_GET
def remediation_status_view(request):
    """
    GET /api/platform/remediation/status/

    Returns detailed remediation status including findings and tasks.

    Session 824: Exposes remediation status to the UI.
    """
    try:
        from core.models_audit_tracking import AuditFinding, AuditRemediationTask
        from django.db.models import Count

        # Findings by status
        findings_by_status = dict(
            AuditFinding.objects.values('status').annotate(
                count=Count('id')
            ).values_list('status', 'count')
        )

        # Findings by priority
        findings_by_priority = dict(
            AuditFinding.objects.values('priority').annotate(
                count=Count('id')
            ).values_list('priority', 'count')
        )

        # Tasks by status
        tasks_by_status = dict(
            AuditRemediationTask.objects.values('status').annotate(
                count=Count('id')
            ).values_list('status', 'count')
        )

        # Recent tasks
        recent_tasks = AuditRemediationTask.objects.order_by('-created_at')[:10]
        recent_tasks_list = [{
            'id': str(task.id),
            'finding_title': task.finding.title if task.finding else 'Unknown',
            'agent': task.assigned_agent,
            'status': task.status,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
        } for task in recent_tasks]

        # Agents with assignments
        agents_assigned = list(
            AuditRemediationTask.objects.filter(
                status__in=['assigned', 'in_progress']
            ).values('assigned_agent').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
        )

        return JsonResponse({
            'success': True,
            'findings': {
                'total': sum(findings_by_status.values()),
                'by_status': findings_by_status,
                'by_priority': findings_by_priority,
                'open': findings_by_status.get('open', 0),
                'fixed': findings_by_status.get('fixed', 0),
            },
            'tasks': {
                'total': sum(tasks_by_status.values()),
                'by_status': tasks_by_status,
                'recent': recent_tasks_list,
            },
            'agents_assigned': agents_assigned,
        })
    except Exception as e:
        logger.error(f"Failed to get remediation status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)
