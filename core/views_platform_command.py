"""
Platform Command Center API - Session 815

Provides APIs for the Platform Command Center which serves as the main
control interface for system governance, mission tracking, and knowledge management.

Endpoints:
- GET /api/platform/mission/ - Current mission + metrics
- GET /api/platform/metrics/ - Detailed progress data
- GET /api/platform/governance/ - System owner + controls status
- POST /api/platform/emergency-halt/ - Trigger emergency halt
- GET /api/platform/canon/ - List canon documents
- GET /api/platform/playbooks/ - List playbooks
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
    """Get current revenue metrics."""
    from core.models import Revenue

    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Get monthly revenue (confirmed + received)
    monthly = Revenue.objects.filter(
        created_at__gte=start_of_month,
        status__in=['confirmed', 'received']
    ).aggregate(total=Sum('amount'))

    # Get total lifetime revenue
    lifetime = Revenue.objects.filter(
        status__in=['confirmed', 'received']
    ).aggregate(total=Sum('amount'))

    # Get pending revenue
    pending = Revenue.objects.filter(
        status__in=['potential', 'pending']
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
        status='completed'
    ).order_by('-completed_at')[:10]

    return [{
        'agent_name': ex.agent.name if ex.agent else 'Unknown',
        'task': ex.task[:100] if ex.task else 'Task completed',
        'completed_at': ex.completed_at.isoformat() if ex.completed_at else None,
        'success': ex.status == 'completed',
    } for ex in recent]


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
