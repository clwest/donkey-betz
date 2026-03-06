"""
Session 1077: Server-side enrichment for cockpit runs.

Computes trigger, importance, summary, artifacts, and next_action
for AgentExecution records — no LLM, pure heuristics.
"""

import re
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Beat task patterns (task field often starts with these) ─────────────────

_BEAT_PATTERNS = re.compile(
    r'^\[?(daily|hourly|scheduled|beat|cron|auto[-_]|periodic|'
    r'run_all_desks|collect_sports|generate_game|update_game|'
    r'evaluate_completed|verify_betting|settle_user|'
    r'backfill_spider|run_spider|warm_up_spider|'
    r'evaluate_unscored|auto_enhance|auto_publish|'
    r'generate_self_blog|score_unscored|'
    r'run_learning_loop|mine_learning|discover_success|'
    r'process_hivemind|execute_approved_dreams|'
    r'coordinate_body|check_circulation|run_spine|'
    r'run_immune|run_digestive|run_muscular|heartbeat|'
    r'generate_human_attention|process_human_attention|'
    r'enrich_boardroom|process_gate_progression)',
    re.IGNORECASE,
)

_CONVERSATION_PATTERN = re.compile(
    r'\[Conversation\]', re.IGNORECASE,
)

# ── Artifact key scanning ──────────────────────────────────────────────────

_ARTIFACT_KEYS = {
    'deliverables': ['deliverable_id', 'deliverable_ids', 'deliverables'],
    'blogs': ['blog_id', 'blog_ids', 'self_blog_id'],
    'media': ['media_id', 'media_ids', 'image_id', 'video_id', 'audio_id',
              'audio_url', 'image_url', 'video_url'],
    'wagers': ['wager_id', 'wager_ids', 'placed_wager_id'],
    'initiatives': ['initiative_id', 'initiative_ids'],
}

# ── Agent display names ────────────────────────────────────────────────────

_AGENT_VERBS = {
    'ContentWriterAgent': 'wrote content',
    'EditorAgent': 'enhanced content',
    'ResearchAgent': 'researched',
    'ImageAgent': 'generated image',
    'VideoAgent': 'generated video',
    'AudioAgent': 'generated audio',
    'ThreeDAgent': 'generated 3D model',
    'GamePredictor': 'generated predictions',
    'SportsOddsAnalyst': 'analyzed odds',
    'ArbitrageDetector': 'scanned arbitrage',
    'TrendAnalysisAgent': 'analyzed trends',
    'MarketIntelligenceAgent': 'analyzed market',
    'MarketIntelligenceCoordinator': 'ran market desk',
    'StockAuditCoordinator': 'ran stock audit',
    'BlockchainAuditCoordinator': 'ran blockchain audit',
    'NarrativeDriftCoordinator': 'ran narrative desk',
    'ContentStrategyAgent': 'planned content strategy',
    'SEOOptimizerAgent': 'optimized SEO',
    'LegalDocDrafterAgent': 'drafted legal document',
    'SystemIntelligenceAgent': 'analyzed system',
    'CustomerResearchAgent': 'researched customers',
    'CompetitorAnalysisAgent': 'analyzed competitors',
    'BrandStrategyAgent': 'planned brand strategy',
    'TechnicalDocumentAgent': 'generated technical doc',
    'ThinkingAgent': 'synthesized analysis',
}


def enrich_run(run_dict: dict, full_record: Any = None) -> dict:
    """Add enrichment fields to a run dict.

    Args:
        run_dict: Serialized run (id, agent_name, task, status, etc.)
        full_record: Optional AgentExecution ORM instance for extra fields.
                     If None, enrichment uses only run_dict fields.

    Returns:
        dict with 'enrichment' key added.
    """
    input_data = {}
    output_data = {}
    parent_object_type = ''
    user_id = None
    cost = 0

    if full_record is not None:
        input_data = full_record.input_data or {}
        output_data = full_record.output_data or {}
        parent_object_type = full_record.parent_object_type or ''
        user_id = full_record.user_id
        cost = float(full_record.cost or 0)

    agent_name = run_dict.get('agent_name', '')
    task = run_dict.get('task', '')
    status = run_dict.get('status', '')

    trigger = _derive_trigger(task, input_data, parent_object_type, user_id)
    artifacts = _extract_artifacts(output_data)
    importance = _compute_importance(status, cost, artifacts, output_data)
    summary = _build_summary(agent_name, task, status, output_data, artifacts)
    next_action = _compute_next_action(status, artifacts, run_dict.get('id', ''))

    run_dict['enrichment'] = {
        'trigger': trigger,
        'importance': importance,
        'summary': summary,
        'artifacts': artifacts,
        'next_action': next_action,
    }
    if full_record is not None:
        run_dict['cost'] = cost
        run_dict['trace_id'] = str(full_record.trace_id) if full_record.trace_id else None

    return run_dict


# ── Trigger derivation ─────────────────────────────────────────────────────

def _derive_trigger(task: str, input_data: dict, parent_object_type: str, user_id) -> dict:
    # 1) Workflow / orchestration
    if parent_object_type:
        label_map = {
            'conversation': 'Multi-agent conversation',
            'orchestration': 'Orchestration workflow',
            'gate': 'Gate evaluation',
            'hivemind': 'HiveMind session',
            'dream': 'Dream execution',
        }
        label = label_map.get(parent_object_type, parent_object_type.replace('_', ' ').title())
        return {
            'type': 'workflow',
            'label': f'Workflow: {label}',
        }

    # 2) Conversation-spawned
    if _CONVERSATION_PATTERN.search(task):
        return {
            'type': 'workflow',
            'label': 'Spawned from conversation',
        }

    # 3) Scheduled / beat
    if _BEAT_PATTERNS.search(task):
        return {
            'type': 'scheduled',
            'label': f'Scheduled task',
        }

    # 4) Check input_data hints
    ctx = input_data.get('context_injected', {})
    if isinstance(ctx, dict):
        if ctx.get('autopilot') or ctx.get('policy_name'):
            policy = ctx.get('policy_name', 'autopilot')
            return {
                'type': 'autopilot',
                'label': f'Autopilot: {policy}',
            }
        if ctx.get('retry_of'):
            return {
                'type': 'retry',
                'label': f"Retry of {str(ctx['retry_of'])[:8]}",
            }

    # 5) Manual (user present, no other signal)
    if user_id:
        return {
            'type': 'manual',
            'label': 'Manual run',
        }

    # 6) Scheduled fallback (no user, no parent — most likely beat-dispatched)
    if not user_id and not parent_object_type:
        return {
            'type': 'scheduled',
            'label': 'Scheduled (autonomous)',
        }

    return {'type': 'unknown', 'label': 'Unknown trigger'}


# ── Artifact extraction ────────────────────────────────────────────────────

def _extract_artifacts(output_data: dict) -> dict:
    artifacts = {
        'deliverables': [],
        'blogs': [],
        'media': [],
        'wagers': [],
        'initiatives': [],
    }

    if not isinstance(output_data, dict):
        return artifacts

    _scan_dict_for_artifacts(output_data, artifacts, depth=0)
    return artifacts


def _scan_dict_for_artifacts(d: dict, artifacts: dict, depth: int):
    if depth > 3:
        return

    for key, val in d.items():
        for art_type, art_keys in _ARTIFACT_KEYS.items():
            if key in art_keys:
                if isinstance(val, str) and val:
                    artifacts[art_type].append({'id': val})
                elif isinstance(val, list):
                    for item in val[:10]:
                        if isinstance(item, str):
                            artifacts[art_type].append({'id': item})
                        elif isinstance(item, dict) and item.get('id'):
                            artifacts[art_type].append(item)

        # Recurse into nested dicts
        if isinstance(val, dict) and depth < 3:
            _scan_dict_for_artifacts(val, artifacts, depth + 1)

    # Check for tool_calls with media results
    tool_calls = d.get('tool_calls', [])
    if isinstance(tool_calls, list):
        for tc in tool_calls[:20]:
            if not isinstance(tc, dict):
                continue
            tool_name = tc.get('tool', '')
            result = tc.get('result', {})
            if not isinstance(result, dict):
                continue

            if tool_name in ('generate_image', 'generate_sfx', 'generate_video',
                             'generate_speech', 'text_to_video', 'image_to_video'):
                url = result.get('audio_url') or result.get('image_url') or result.get('video_url') or result.get('url', '')
                if url:
                    media_type = 'audio' if 'audio' in tool_name or 'speech' in tool_name or 'sfx' in tool_name else \
                                 'video' if 'video' in tool_name else 'image'
                    artifacts['media'].append({'url': url, 'media_type': media_type})


# ── Importance scoring ─────────────────────────────────────────────────────

def _compute_importance(status: str, cost: float, artifacts: dict, output_data: dict) -> dict:
    reasons = []

    # Failed → action required
    if status == 'failed':
        return {
            'level': 'action_required',
            'reasons': ['failed'],
        }

    # Check for pending review items in output
    if isinstance(output_data, dict):
        msg = output_data.get('message', '')
        if isinstance(msg, str) and ('pending_review' in msg or 'needs_enhancement' in msg):
            reasons.append('needs_review')

    # Created artifacts → high impact
    artifact_count = sum(len(v) for v in artifacts.values())
    if artifact_count > 0:
        reasons.append('created_artifacts')

    # Cost spike
    if cost > 0.25:
        reasons.append('cost_spike')

    if 'needs_review' in reasons:
        return {'level': 'action_required', 'reasons': reasons}
    if reasons:
        return {'level': 'high_impact', 'reasons': reasons}

    return {'level': 'routine', 'reasons': []}


# ── Summary generation ─────────────────────────────────────────────────────

def _build_summary(agent_name: str, task: str, status: str, output_data: dict, artifacts: dict) -> str:
    verb = _AGENT_VERBS.get(agent_name, 'ran')

    # Try to get a clean summary from output_data.message
    msg = ''
    if isinstance(output_data, dict):
        msg = output_data.get('message', '') or output_data.get('result_preview', '') or ''
        if isinstance(msg, str):
            msg = msg[:120].strip()

    # Build artifact suffix
    art_parts = []
    for art_type, items in artifacts.items():
        if items:
            count = len(items)
            label = art_type if count > 1 else art_type.rstrip('s')
            art_parts.append(f'{count} {label}')
    art_suffix = f" ({', '.join(art_parts)})" if art_parts else ''

    if status == 'failed':
        error = ''
        if isinstance(output_data, dict):
            error = output_data.get('error', '') or ''
        if error:
            return f'{agent_name} failed: {str(error)[:80]}'
        return f'{agent_name} failed'

    if msg:
        # Clean up [Conversation] prefixes
        clean_msg = re.sub(r'\[Conversation\]\s*', '', msg).strip()
        if len(clean_msg) > 10:
            return f'{clean_msg}{art_suffix}'

    # Fallback: agent + verb + task snippet
    task_snippet = re.sub(r'\[Conversation\]\s*', '', task).strip()[:60]
    if task_snippet:
        return f'{agent_name} {verb}: {task_snippet}{art_suffix}'

    return f'{agent_name} {verb}{art_suffix}'


# ── Next action CTA ────────────────────────────────────────────────────────

def _compute_next_action(status: str, artifacts: dict, run_id: str) -> dict:
    if status == 'failed':
        return {
            'type': 'investigate_failure',
            'label': 'Investigate',
            'href': f'/cockpit/runs/{run_id}',
            'priority': 'primary',
        }

    if artifacts.get('deliverables'):
        return {
            'type': 'review_deliverable',
            'label': 'Review deliverable',
            'href': f'/cockpit/runs/{run_id}',
            'priority': 'primary',
        }

    if artifacts.get('blogs'):
        return {
            'type': 'approve_content',
            'label': 'Review content',
            'href': f'/cockpit/runs/{run_id}',
            'priority': 'primary',
        }

    artifact_count = sum(len(v) for v in artifacts.values())
    if artifact_count > 0:
        return {
            'type': 'view_artifacts',
            'label': 'View output',
            'href': f'/cockpit/runs/{run_id}',
            'priority': 'secondary',
        }

    return {
        'type': 'no_action',
        'label': '',
        'href': '',
        'priority': 'secondary',
    }
