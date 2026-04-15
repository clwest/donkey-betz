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
from django.views.decorators.http import require_GET, require_POST, require_http_methods

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


def _get_pending_decisions(user=None) -> List[Dict[str, Any]]:
    """
    Get pending human decisions.

    Session 848: Filter by user to ensure users only see items they can act on.
    Without user filter, the list would show all users' items, but record_decision
    only allows users to decide on their own items, creating a mismatch.
    """
    from core.models_human_interface import HumanAttentionItem

    queryset = HumanAttentionItem.objects.filter(status='pending')

    # Session 848: Filter by user if provided to match record_decision behavior
    if user and user.is_authenticated:
        queryset = queryset.filter(user=user)

    pending = queryset.order_by('-urgency', '-priority_score', '-created_at')[:20]

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
    """
    Get recent agent activity for the command center feed.

    Session 832: Enhanced to include:
    - All statuses (pending, in_progress, completed, failed)
    - created_at timestamp (when task started)
    - input_data summary (what parameters were passed)
    - user who triggered the execution
    """
    from django.db.models import Case, When, Value, IntegerField
    from core.models_unified_system import AgentExecution

    # Session 832: Include all statuses, prioritize in_progress, then recent
    recent = AgentExecution.objects.filter(
        status__in=['pending', 'in_progress', 'completed', 'failed']
    ).select_related('agent', 'user').annotate(
        # Prioritize in_progress tasks first
        status_priority=Case(
            When(status='in_progress', then=Value(0)),
            When(status='pending', then=Value(1)),
            When(status='failed', then=Value(2)),
            When(status='completed', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('status_priority', '-created_at')[:15]

    results = []
    for ex in recent:
        # Extract summary from output_data if available
        output_summary = None
        tool_results = []
        if ex.output_data:
            # Try to get a summary or description from output
            if isinstance(ex.output_data, dict):
                output_summary = ex.output_data.get('summary') or ex.output_data.get('description') or (ex.output_data.get('content') or '')[:500]
                # Extract tool results if present
                if 'tool_results' in ex.output_data:
                    tool_results = ex.output_data.get('tool_results', [])[:5]  # Limit to 5 tools
                elif 'tools_used' in ex.output_data:
                    tool_results = ex.output_data.get('tools_used', [])[:5]

        # Session 832: Extract input_data summary
        # Session 910: Send full input_data - let frontend handle display truncation
        input_data_full = None
        if ex.input_data and isinstance(ex.input_data, dict):
            # Send full input_data as proper dict (not str converted)
            # Frontend will handle display with expandable views
            input_data_full = ex.input_data

        # Session 832: Get agent category name (it's a ForeignKey)
        agent_category_name = None
        if ex.agent and ex.agent.category:
            agent_category_name = ex.agent.category.name if hasattr(ex.agent.category, 'name') else str(ex.agent.category)

        results.append({
            'id': str(ex.id),
            'agent_name': ex.agent.name if ex.agent else 'Unknown',
            'agent_category': agent_category_name,
            # Session 910: Send full task, use task_preview for list display
            'task': ex.task if ex.task else 'Task in progress',
            'task_preview': ex.task[:100] + '...' if ex.task and len(ex.task) > 100 else ex.task or 'Task in progress',
            # Session 832: Add created_at for when task started
            'created_at': ex.created_at.isoformat() if ex.created_at else None,
            'completed_at': ex.completed_at.isoformat() if ex.completed_at else None,
            'success': ex.status == 'completed',
            'status': ex.status,
            'execution_time_ms': ex.execution_time_ms,
            'tokens_used': ex.tokens_used,
            'cost': float(ex.cost) if ex.cost else 0,
            'error_message': ex.error_message if ex.status == 'failed' else None,
            'output_summary': output_summary[:500] if output_summary else None,
            'tool_results': tool_results,
            # Session 832/910: Full input_data as proper dict (not truncated string)
            'input_data': input_data_full,
            'triggered_by': ex.user.username if ex.user else 'system',
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

    Session 832: Added system_activity from RecentActivityService
    which includes dreams, conversations, decisions, and pilots.
    """
    revenue = _get_revenue_metrics()
    costs = _get_llm_cost_metrics()
    canon = _count_canon_docs()
    playbooks = _count_playbooks()
    activity = _get_recent_activity()

    # Session 832: Get broader system activity (dreams, convos, decisions, pilots)
    try:
        from core.services.recent_activity import get_recent_activity as get_system_activity
        system_activity = get_system_activity(limit=15, hours=72)
    except Exception as e:
        logger.warning(f"Failed to get system activity: {e}")
        system_activity = {'activities': [], 'counts': {}, 'total': 0}

    return JsonResponse({
        'revenue': revenue,
        'llm_costs': costs,
        'canon': canon,
        'playbooks': playbooks,
        'recent_activity': activity,
        # Session 832: Broader system activity feed
        'system_activity': system_activity,
    })


@require_GET
def governance_view(request):
    """
    GET /api/platform/governance/

    Returns governance controls and system owner info.
    """
    owner = _get_system_owner()
    emergency = _get_emergency_status()
    # Session 848: Pass user to filter decisions to only those they can act on
    decisions = _get_pending_decisions(user=request.user)

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


@require_GET
def decision_summary_detail_view(request, decision_id):
    """
    GET /api/platform/decision-summary/<uuid:decision_id>/

    Session 845: Get detail for a single AgentDecisionSummary.
    Session 848: Fixed field name mismatches causing 500 errors.
    Session 855: Also check HumanAttentionItem to avoid 404 on pending decisions.
    Used by DecisionDetailModal for System Activity items.
    """
    from core.models_unified_system import AgentDecisionSummary
    from core.models_human_interface import HumanAttentionItem

    decision = None
    attention_item = None

    # Try AgentDecisionSummary first
    try:
        decision = AgentDecisionSummary.objects.get(id=decision_id)
    except AgentDecisionSummary.DoesNotExist:
        pass

    # Session 855: Fall back to HumanAttentionItem if not found
    if not decision:
        try:
            attention_item = HumanAttentionItem.objects.get(id=decision_id)
        except HumanAttentionItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Decision not found'}, status=404)

    # If we found a HumanAttentionItem, return it in the expected format
    if attention_item:
        return JsonResponse({
            'success': True,
            'item': {
                'id': str(attention_item.id),
                'title': attention_item.title,
                'summary': attention_item.summary,
                'urgency': attention_item.urgency,
                'status': attention_item.status,
                'item_type': attention_item.item_type,
                'source_type': attention_item.source_type,
                'source_agent': attention_item.source_agent,
                'source_id': attention_item.source_id,
                'payload': attention_item.payload or {},
                'priority_score': attention_item.priority_score,
                'impact_estimate': attention_item.impact_estimate,
                'ml_prediction': attention_item.ml_prediction,
                'ml_confidence': attention_item.ml_confidence,
                'ml_recommendation': attention_item.ml_recommendation,
                'decision': attention_item.decision,
                'decision_feedback': attention_item.decision_feedback,
                'decision_confidence': attention_item.decision_confidence,
                'decided_at': attention_item.decided_at.isoformat() if attention_item.decided_at else None,
                'human_overrode_ml': attention_item.human_overrode_ml,
                'override_reason': attention_item.override_reason,
                'deferred_until': attention_item.deferred_until.isoformat() if attention_item.deferred_until else None,
                'created_at': attention_item.created_at.isoformat() if attention_item.created_at else None,
                'viewed_at': attention_item.viewed_at.isoformat() if attention_item.viewed_at else None,
                'expires_at': attention_item.expires_at.isoformat() if attention_item.expires_at else None,
                'verification_outcome': attention_item.verification_outcome,
                'verified_at': attention_item.verified_at.isoformat() if attention_item.verified_at else None,
                'verification_profit': float(attention_item.verification_profit) if attention_item.verification_profit else None,
                'verification_notes': attention_item.verification_notes,
            }
        })

    # Session 848: Use correct field names from AgentDecisionSummary model
    # - rationale (not reasoning)
    # - recommended_stance (not final_decision)
    # - participants (not lead_agent, contributing_agents)
    # - key_insights (not key_factors)
    participants = decision.participants or []
    lead_agent = participants[0] if participants else 'Multiple Agents'
    conversation_id = str(decision.conversation.id) if decision.conversation else None

    # Session 852: Include initiative data if linked
    initiative_data = None
    try:
        if decision.initiative:
            initiative = decision.initiative
            initiative_data = {
                'id': str(initiative.id),
                'name': initiative.name,
                'current_stage': initiative.current_stage,
                'status': initiative.status,
            }
    except Exception:
        pass  # Initiative may have been deleted or not exist

    # Build rich response
    try:
        return JsonResponse({
            'success': True,
            'item': {
                'id': str(decision.id),
                'title': decision.topic or 'Untitled Decision',
                'summary': decision.rationale or decision.recommended_stance or '',
                'urgency': 'medium',  # Default since AgentDecisionSummary doesn't have urgency
                'status': decision.status or 'draft',
                'item_type': 'decision_summary',
                'source_type': 'boardroom',
                'source_agent': lead_agent,
                'source_id': str(conversation_id) if conversation_id else None,
                'payload': {
                    'decision_type': decision.decision_type,
                    'impact_area': decision.impact_area,
                    'key_insights': decision.key_insights or [],
                    'recommended_stance': decision.recommended_stance,
                    'suggested_feature': decision.suggested_feature,
                    'rationale': decision.rationale,
                    'participants': participants,
                    'is_canonical': decision.is_canonical,
                    # Session 852: Initiative linkage
                    'initiative': initiative_data,
                    'has_suggested_feature': bool(decision.suggested_feature and len(decision.suggested_feature.strip()) >= 10),
                },
                'priority_score': 0.5,  # No confidence_level field
                'impact_estimate': None,
                'ml_prediction': None,
                'ml_confidence': None,
                'ml_recommendation': decision.recommended_stance,
                'decision': decision.status,
                'decision_feedback': None,
                'decision_confidence': None,
                'decided_at': decision.created_at.isoformat() if decision.created_at else None,
                'human_overrode_ml': False,
                'override_reason': None,
                'deferred_until': None,
                'created_at': decision.created_at.isoformat() if decision.created_at else None,
                'viewed_at': None,
                'expires_at': None,
                'verification_outcome': None,
                'verified_at': None,
                'verification_profit': None,
                'verification_notes': None,
            }
        })
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error serializing decision {decision_id}: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def create_initiative_from_decision_view(request, decision_id):
    """
    POST /api/platform/decision-summary/<uuid:decision_id>/create-initiative/

    Session 852: Create an Initiative from a decision's suggested_feature.
    This exposes the auto_link_initiative_for_decision functionality via API.
    """
    from core.models_unified_system import AgentDecisionSummary
    from core.services.decision_extractor import auto_link_initiative_for_decision
    import logging

    logger = logging.getLogger(__name__)

    # Verify authentication
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        decision = AgentDecisionSummary.objects.get(id=decision_id)
    except AgentDecisionSummary.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Decision not found'}, status=404)

    # Check if already linked to an initiative
    try:
        if decision.initiative:
            return JsonResponse({
                'success': False,
                'error': 'Decision already linked to an initiative',
                'initiative_id': str(decision.initiative.id),
                'initiative_name': decision.initiative.name,
            }, status=400)
    except Exception as _e:
        logger.warning(
            "views_platform_command.create_initiative_from_decision_view: swallowed (%s: %s) — degraded",
            type(_e).__name__, _e,
        )

    # Check if decision has a suggested feature
    if not decision.suggested_feature or len(decision.suggested_feature.strip()) < 10:
        return JsonResponse({
            'success': False,
            'error': 'Decision does not have a suggested feature to create an initiative from',
        }, status=400)

    try:
        # Use the existing auto_link function
        initiative = auto_link_initiative_for_decision(decision)

        if initiative:
            logger.info(f"Session 852: Created Initiative '{initiative.name}' from decision via API")
            return JsonResponse({
                'success': True,
                'message': f"Initiative '{initiative.name}' created successfully",
                'initiative': {
                    'id': str(initiative.id),
                    'name': initiative.name,
                    'current_stage': initiative.current_stage,
                    'status': initiative.status,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to create initiative - check logs for details',
            }, status=500)

    except Exception as e:
        logger.error(f"Session 852: Error creating initiative from decision {decision_id}: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


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

    Session 829: Added agent parameter and write_files support.
    Session 831: Auto-detect agent with most pending tasks if none specified.
    Session 831: Auto-assign open findings if no tasks exist.

    Parameters:
        limit: Maximum tasks to process (default: 20)
        agent: Specific agent to run (default: auto-detect from pending tasks)
        write_files: Whether to write generated files to workspace (default: true)
        assign_first: If true, assign open findings before executing (default: auto)
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        import json
        from django.db.models import Count
        from core.models_audit_tracking import AuditRemediationTask, AuditFinding

        body = json.loads(request.body) if request.body else {}
        limit = body.get('limit', 20)
        agent = body.get('agent')  # None = auto-detect
        write_files = body.get('write_files', True)
        assign_first = body.get('assign_first')  # None = auto-detect

        # Check if there are any assigned tasks
        total_assigned = AuditRemediationTask.objects.filter(status='assigned').count()

        # Session 831: If no assigned tasks, check for open findings and assign them
        # Session 833: Chain assignment with execution so user doesn't need to click twice
        if total_assigned == 0:
            open_findings_count = AuditFinding.objects.filter(
                status='open',
                assigned_agent=''
            ).count()

            if open_findings_count > 0:
                # Run assignment phase first, then chain execution
                logger.info(f"No assigned tasks, but {open_findings_count} open findings. Running assignment + execution...")
                from core.tasks import assign_and_execute_remediation

                # Session 833: Use combined task that assigns then executes
                assign_and_execute_remediation.delay(
                    limit=limit,
                    write_files=write_files
                )

                return JsonResponse({
                    'success': True,
                    'message': f'Assigning {min(limit, open_findings_count)} of {open_findings_count} open findings, then executing remediation.',
                    'phase': 'assignment_and_execution',
                    'open_findings': open_findings_count,
                    'tasks_available': min(limit, open_findings_count),
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No open findings or pending tasks to process',
                    'tasks_available': 0,
                    'open_findings': 0,
                })

        # Session 831: Auto-detect agent with most pending tasks
        if not agent:
            # Find agent with most assigned (pending) tasks
            top_agent = AuditRemediationTask.objects.filter(
                status='assigned'
            ).values('assigned_agent').annotate(
                count=Count('id')
            ).order_by('-count').first()

            if top_agent:
                agent = top_agent['assigned_agent']
                pending_count = top_agent['count']
                logger.info(f"Auto-selected {agent} with {pending_count} pending tasks")

        # Get count of tasks that will be processed
        tasks_available = AuditRemediationTask.objects.filter(
            assigned_agent=agent,
            status='assigned'
        ).count() if agent else total_assigned

        if tasks_available == 0:
            return JsonResponse({
                'success': False,
                'message': f'No pending tasks for {agent}' if agent else 'No pending tasks',
                'agent': agent,
                'tasks_available': 0,
            })

        from core.tasks import run_agent_remediation_batch

        run_agent_remediation_batch.delay(
            agent_name=agent,
            limit=limit,
            write_files=write_files
        )

        message = f"Remediation triggered: {agent} ({min(limit, tasks_available)} of {tasks_available} tasks, write_files: {write_files})"
        logger.info(f"{message} by {request.user.username}")

        return JsonResponse({
            'success': True,
            'message': message,
            'agent': agent,
            'limit': limit,
            'tasks_available': tasks_available,
            'write_files': write_files,
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
def action_agent_category_rotation_view(request):
    """
    POST /api/platform/actions/agent-category-rotation/

    Session 884: Trigger agent category rotation to generate Operations content.

    Body params:
        category: str - The category to rotate (content, research, system, financial, etc.)
                       Defaults to 'content' if not specified.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        import json
        from core.tasks import agent_category_rotation

        # Parse category from request body
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {}

        category = data.get('category', 'content')

        # Valid categories
        valid_categories = ['content', 'research', 'system', 'financial', 'development', 'creative', 'analysis']

        if category not in valid_categories:
            return JsonResponse({
                'success': False,
                'error': f"Invalid category: {category}. Valid options: {valid_categories}",
            }, status=400)

        result = agent_category_rotation.delay(category)

        message = f"Agent category rotation triggered for '{category}'"
        logger.info(f"{message} by {request.user.username} - task_id: {result.id}")

        return JsonResponse({
            'success': True,
            'message': message,
            'task_id': result.id,
            'category': category,
        })
    except Exception as e:
        logger.error(f"Failed to trigger agent category rotation: {e}")
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
    Session 829: Updated format for GovernanceTab Self-Healing Controls.
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
        recent_tasks = AuditRemediationTask.objects.select_related('finding').order_by('-completed_at', '-created_at')[:10]
        recent_tasks_list = [{
            'id': str(task.id),
            'finding_title': task.finding.title if task.finding else 'Unknown',
            'agent': task.assigned_agent,
            'status': task.status,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
        } for task in recent_tasks]

        # Agents with task counts (Session 829: for UI display)
        agents_by_task_count = list(
            AuditRemediationTask.objects.values('assigned_agent').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
        )
        agents_formatted = [
            {'agent': item['assigned_agent'], 'count': item['count']}
            for item in agents_by_task_count
        ]

        # Calculate progress (Session 829)
        total_tasks = sum(tasks_by_status.values())
        completed_tasks = tasks_by_status.get('completed', 0)
        percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

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
                'total': total_tasks,
                'by_status': tasks_by_status,
                'by_agent': agents_formatted,
            },
            'recent_tasks': recent_tasks_list,
            'progress': {
                'completed': completed_tasks,
                'total': total_tasks,
                'percentage': round(percentage, 1),
            },
        })
    except Exception as e:
        logger.error(f"Failed to get remediation status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_GET
def self_healing_progress_view(request):
    """
    GET /api/self-healing/progress/

    Session 830: Live self-healing progress endpoint for UI polling.
    Returns computed progress snapshot from DB (single source of truth).

    Response format:
    {
        "total_tasks": 742,
        "completed_tasks": 493,
        "progress_pct": 66.4,
        "by_agent": [
            {"agent": "CodeReviewAgent", "completed": 40, "total": 40, "pct": 100.0, "status": "DONE"},
            ...
        ],
        "recent_activity": {
            "completed_last_10m": 7,
            "in_progress": 3,
            "assigned": 246,
            "last_completed_at": "2026-01-25T23:30:00Z"
        },
        "updated_at": "2026-01-25T23:35:00Z"
    }
    """
    try:
        from core.models_audit_tracking import AuditRemediationTask
        from django.db.models import Count, Q, Max

        now = timezone.now()

        # Get task counts by agent and status in one efficient query
        agent_stats = AuditRemediationTask.objects.values('assigned_agent').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            assigned=Count('id', filter=Q(status='assigned')),
            failed=Count('id', filter=Q(status='failed')),
        ).order_by('-total')

        # Build by_agent list with computed fields
        by_agent = []
        total_tasks = 0
        completed_tasks = 0
        in_progress_count = 0
        assigned_count = 0

        for agent in agent_stats:
            agent_total = agent['total']
            agent_completed = agent['completed']
            agent_in_progress = agent['in_progress']
            agent_assigned = agent['assigned']

            total_tasks += agent_total
            completed_tasks += agent_completed
            in_progress_count += agent_in_progress
            assigned_count += agent_assigned

            # Determine status
            if agent_completed == agent_total:
                status = "DONE"
            elif agent_in_progress > 0:
                status = "RUNNING"
            elif agent_assigned > 0:
                status = "PENDING"
            else:
                status = "IDLE"

            pct = round((agent_completed / agent_total * 100), 1) if agent_total > 0 else 0

            by_agent.append({
                'agent': agent['assigned_agent'],
                'completed': agent_completed,
                'total': agent_total,
                'pct': pct,
                'status': status,
            })

        # Calculate overall progress
        progress_pct = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0

        # Recent activity - tasks completed in last 10 minutes
        ten_minutes_ago = now - timedelta(minutes=10)
        completed_last_10m = AuditRemediationTask.objects.filter(
            status='completed',
            completed_at__gte=ten_minutes_ago
        ).count()

        # Last completed task timestamp
        last_completed = AuditRemediationTask.objects.filter(
            status='completed'
        ).aggregate(last=Max('completed_at'))

        return JsonResponse({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'progress_pct': progress_pct,
            'by_agent': by_agent,
            'recent_activity': {
                'completed_last_10m': completed_last_10m,
                'in_progress': in_progress_count,
                'assigned': assigned_count,
                'last_completed_at': last_completed['last'].isoformat() if last_completed['last'] else None,
            },
            'updated_at': now.isoformat(),
        })

    except Exception as e:
        logger.error(f"Failed to get self-healing progress: {e}")
        return JsonResponse({
            'error': str(e),
            'total_tasks': 0,
            'completed_tasks': 0,
            'progress_pct': 0,
            'by_agent': [],
            'recent_activity': {},
            'updated_at': timezone.now().isoformat(),
        }, status=500)


@require_GET
def celery_debug_view(request):
    """
    GET /api/platform/celery-debug/

    Session 842: Debug endpoint to check Celery status and recent task activity.
    """
    from django.conf import settings
    from core.models_unified_system import AgentExecution
    from datetime import timedelta

    try:
        # Check Redis connection
        redis_ok = False
        redis_error = None
        try:
            from django.core.cache import cache
            cache.set('celery_debug_test', 'ok', 10)
            redis_ok = cache.get('celery_debug_test') == 'ok'
        except Exception as e:
            redis_error = str(e)

        # Get execution status breakdown
        now = timezone.now()
        one_hour_ago = now - timedelta(hours=1)
        two_hours_ago = now - timedelta(hours=2)

        total_in_progress = AgentExecution.objects.filter(status='in_progress').count()
        stale_2h = AgentExecution.objects.filter(
            status='in_progress',
            created_at__lt=two_hours_ago
        ).count()

        # Recent completions (evidence worker is working)
        recent_completions = AgentExecution.objects.filter(
            status='completed',
            completed_at__gte=one_hour_ago
        ).count()

        recent_failures = AgentExecution.objects.filter(
            status='failed',
            completed_at__gte=one_hour_ago
        ).count()

        # Get oldest in_progress task
        oldest_in_progress = AgentExecution.objects.filter(
            status='in_progress'
        ).order_by('created_at').first()

        oldest_age_hours = None
        if oldest_in_progress:
            oldest_age_hours = (now - oldest_in_progress.created_at).total_seconds() / 3600

        # Check Celery Beat schedule from database (DatabaseScheduler)
        beat_schedule = {}
        beat_db_tasks = {}
        try:
            from django_celery_beat.models import PeriodicTask
            # Get cleanup-related tasks from database
            cleanup_tasks = PeriodicTask.objects.filter(name__icontains='cleanup')
            for task in cleanup_tasks:
                beat_db_tasks[task.name] = {
                    'task': task.task,
                    'enabled': task.enabled,
                    'last_run_at': task.last_run_at.isoformat() if task.last_run_at else None,
                    'total_run_count': task.total_run_count,
                    'interval': str(task.interval) if task.interval else None,
                    'one_off': task.one_off,
                }
                # Calculate hours since last run
                if task.last_run_at:
                    hours_since_run = (now - task.last_run_at).total_seconds() / 3600
                    beat_db_tasks[task.name]['hours_since_last_run'] = round(hours_since_run, 1)
        except Exception as e:
            beat_db_tasks = {'error': str(e)}

        # Session 1007: Read from celery.py's app.conf.beat_schedule (authoritative source)
        try:
            from core.celery import app as celery_app
            schedule = getattr(celery_app.conf, 'beat_schedule', {})
            for name, config in schedule.items():
                if 'cleanup' in name.lower() or 'stale' in name.lower():
                    beat_schedule[name] = {
                        'task': config.get('task'),
                        'schedule': str(config.get('schedule', '')),
                    }
        except Exception as e:
            beat_schedule = {'error': str(e)}

        return JsonResponse({
            'success': True,
            'timestamp': now.isoformat(),
            'redis': {
                'connected': redis_ok,
                'error': redis_error,
            },
            'executions': {
                'total_in_progress': total_in_progress,
                'stale_over_2h': stale_2h,
                'completed_last_hour': recent_completions,
                'failed_last_hour': recent_failures,
                'oldest_in_progress_hours': round(oldest_age_hours, 1) if oldest_age_hours else None,
            },
            'celery_beat': {
                'settings_schedule': beat_schedule,
                'database_tasks': beat_db_tasks,
            },
            'diagnosis': {
                'worker_active': recent_completions > 0 or recent_failures > 0,
                'cleanup_needed': stale_2h > 0,
                'possible_issues': [
                    issue for issue in [
                        'Redis not connected' if not redis_ok else None,
                        f'{stale_2h} tasks stuck >2h (cleanup not running?)' if stale_2h > 0 else None,
                        'No task completions in last hour' if recent_completions == 0 and recent_failures == 0 else None,
                        # Check if cleanup task hasn't run in over 2 hours
                        next((
                            f"cleanup task '{name}' hasn't run in {info.get('hours_since_last_run', 'unknown')} hours"
                            for name, info in beat_db_tasks.items()
                            if isinstance(info, dict) and info.get('hours_since_last_run', 0) > 2
                        ), None) if isinstance(beat_db_tasks, dict) and 'error' not in beat_db_tasks else None,
                    ] if issue
                ]
            }
        })

    except Exception as e:
        logger.error(f"Celery debug failed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def cleanup_stale_executions_view(request):
    """
    POST /api/platform/cleanup-stale-executions/

    Session 842: Manually trigger cleanup of stale agent executions.
    Useful when Celery Beat is not running and tasks are stuck.

    Query params:
        hours_threshold: Hours before marking as stale (default 2)
    """
    try:
        from django.utils import timezone
        from datetime import timedelta
        from core.models_unified_system import AgentExecution

        hours_threshold = int(request.GET.get('hours_threshold', 2))
        cutoff_time = timezone.now() - timedelta(hours=hours_threshold)

        stale_tasks = AgentExecution.objects.filter(
            status='in_progress',
            created_at__lt=cutoff_time
        )

        count = stale_tasks.count()

        if count > 0:
            # Get details before updating
            stale_details = list(stale_tasks.values('id', 'agent__name', 'task', 'created_at')[:20])

            stale_tasks.update(
                status='failed',
                error_message=f'Session 842: Task timed out after {hours_threshold} hours - marked as failed by manual cleanup',
                completed_at=timezone.now()
            )
            logger.info(f"🧹 [SESSION 842] Manually cleaned up {count} stale agent executions")

            return JsonResponse({
                'success': True,
                'cleaned_count': count,
                'hours_threshold': hours_threshold,
                'sample_tasks': stale_details,
                'message': f'Cleaned up {count} stale executions older than {hours_threshold} hours',
            })
        else:
            return JsonResponse({
                'success': True,
                'cleaned_count': 0,
                'hours_threshold': hours_threshold,
                'message': f'No stale executions found older than {hours_threshold} hours',
            })

    except Exception as e:
        logger.error(f"Failed to cleanup stale executions: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def delete_failed_executions_view(request):
    """
    DELETE /api/platform/delete-failed-executions/

    Session 895: Delete old failed agent executions to clean up the UI.

    Query params:
        hours_old: Only delete failures older than this (default 1)
        limit: Max number to delete (default 100)
    """
    try:
        from django.utils import timezone
        from datetime import timedelta
        from core.models_unified_system import AgentExecution

        hours_old = int(request.GET.get('hours_old', 1))
        limit = int(request.GET.get('limit', 100))
        cutoff_time = timezone.now() - timedelta(hours=hours_old)

        failed_tasks = AgentExecution.objects.filter(
            status='failed',
            created_at__lt=cutoff_time
        ).order_by('created_at')[:limit]

        count = failed_tasks.count()

        if count > 0:
            # Get details before deleting
            sample_details = list(failed_tasks.values('id', 'agent__name', 'task', 'created_at')[:10])

            # Delete the failed executions
            deleted_ids = list(failed_tasks.values_list('id', flat=True))
            AgentExecution.objects.filter(id__in=deleted_ids).delete()

            logger.info(f"🗑️ [SESSION 895] Deleted {count} failed agent executions older than {hours_old}h")

            return JsonResponse({
                'success': True,
                'deleted_count': count,
                'hours_old': hours_old,
                'sample_deleted': sample_details,
                'message': f'Deleted {count} failed executions older than {hours_old} hours',
            })
        else:
            return JsonResponse({
                'success': True,
                'deleted_count': 0,
                'hours_old': hours_old,
                'message': f'No failed executions found older than {hours_old} hours',
            })

    except Exception as e:
        logger.error(f"Failed to delete failed executions: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)
