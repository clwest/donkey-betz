"""
Agent Output Contract
======================

Enforces standardized output quality for all agents. Every agent result
passes through this contract validator before being accepted.

The contract requires:
- A meaningful summary (not just "complete" or prompt fragments)
- Confidence score
- Provenance (what sources were used)
- Self-assessment of output quality

If an agent returns garbage (one-liners, prompt echoes, empty data),
the contract flags it and recommends retry or escalation.

Usage:
    from core.services.agent_output_contract import validate_agent_output, enrich_agent_result

    # Validate after agent execution
    validation = validate_agent_output(result, task_description)
    if not validation['valid']:
        # Handle: retry, escalate, or accept with warning

    # Enrich result with contract metadata
    enriched = enrich_agent_result(result, task_description, workspace_brief)
"""

import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Minimum thresholds for output quality
MIN_SUMMARY_LENGTH = 30          # Characters — "Topic mining complete" is too short
MIN_CONTENT_LENGTH = 100         # Characters of real content in data
MIN_CONFIDENCE_FOR_PROCEED = 0.3 # Below this = definitely retry
JUNK_PATTERNS = [
    r'^[\w\s]{1,20}\s+complete[d]?$',           # "Topic mining complete"
    r'^[\w\s]{1,20}\s+optimization completed$',  # "SEO optimization completed"
    r'^Generated \d+ \w+ recommendations$',       # "Generated 3 content recommendations"
    r'^Contrarian analysis complete$',
]
JUNK_REGEXES = [re.compile(p, re.IGNORECASE) for p in JUNK_PATTERNS]


def validate_agent_output(result, task_description: str = '') -> Dict[str, Any]:
    """
    Validate an agent's output against the contract.

    Returns:
        {
            'valid': bool,
            'quality_score': 0-100,
            'issues': ['Summary too short', ...],
            'recommendation': 'accept' | 'accept_with_warning' | 'retry' | 'escalate',
            'details': {...}
        }
    """
    issues = []
    quality_score = 100

    if not result:
        return {
            'valid': False,
            'quality_score': 0,
            'issues': ['No result returned'],
            'recommendation': 'retry',
        }

    message = str(getattr(result, 'message', '')) or ''
    data = getattr(result, 'data', None) or {}
    confidence = getattr(result, 'confidence', 0.0) or 0.0
    agent_name = getattr(result, 'agent_name', '') or ''

    # Check 1: Is the message a junk one-liner?
    is_junk_message = _is_junk_summary(message)
    if is_junk_message:
        issues.append(f'Summary is a generic one-liner: "{message[:60]}"')
        quality_score -= 30

    # Check 2: Is there real content in data?
    content_length = _estimate_content_depth(data)
    if content_length < MIN_CONTENT_LENGTH:
        issues.append(f'Data content too shallow ({content_length} chars, need {MIN_CONTENT_LENGTH}+)')
        quality_score -= 25

    # Check 3: Does the message echo the task description?
    if task_description and _is_echo(message, task_description):
        issues.append('Summary appears to echo the task description instead of reporting findings')
        quality_score -= 20

    # Check 4: Confidence check
    if confidence < MIN_CONFIDENCE_FOR_PROCEED and confidence > 0:
        issues.append(f'Low confidence ({confidence:.2f})')
        quality_score -= 15

    # Check 5: Are there tool results or sources?
    has_sources = bool(
        data.get('results') or data.get('tool_results') or
        data.get('provenance') or data.get('sources') or
        data.get('key_insights') or data.get('recommendations') or
        data.get('content') or data.get('enhanced_content') or
        data.get('optimization') or data.get('full_text')
    )
    if not has_sources:
        issues.append('No substantive data (no results, sources, or content)')
        quality_score -= 20

    # Determine recommendation
    quality_score = max(0, min(100, quality_score))

    if quality_score >= 60:
        recommendation = 'accept'
    elif quality_score >= 40:
        recommendation = 'accept_with_warning'
    elif quality_score >= 20:
        recommendation = 'retry'
    else:
        recommendation = 'escalate'

    return {
        'valid': quality_score >= 40,
        'quality_score': quality_score,
        'issues': issues,
        'recommendation': recommendation,
        'details': {
            'message_length': len(message),
            'content_depth': content_length,
            'is_junk_message': is_junk_message,
            'has_sources': has_sources,
            'confidence': confidence,
            'agent_name': agent_name,
        },
    }


def enrich_agent_result(result, task_description: str = '', workspace_brief: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Enrich an agent result with contract metadata.

    Adds validation results and provenance tracking to the result's data.
    Does NOT modify the original result — returns enrichment metadata.
    """
    validation = validate_agent_output(result, task_description)

    enrichment = {
        'contract_version': '1.0',
        'validation': validation,
        'task_description': task_description[:200],
        'workspace_topic': (workspace_brief or {}).get('topic', ''),
    }

    return enrichment


def _is_junk_summary(message: str) -> bool:
    """Check if a message is a generic one-liner that doesn't contain real information."""
    if not message or len(message) < MIN_SUMMARY_LENGTH:
        return True

    # Check against known junk patterns
    for regex in JUNK_REGEXES:
        if regex.match(message.strip()):
            return True

    # Check for very short messages with no substance
    words = message.split()
    if len(words) <= 5:
        return True

    return False


def _is_echo(message: str, task_description: str) -> bool:
    """Check if the message is just echoing back the task description."""
    if not message or not task_description:
        return False

    # Normalize both
    msg_lower = message.lower().strip()
    task_lower = task_description.lower().strip()

    # Direct echo (message is a substring of task or vice versa)
    if msg_lower[:100] in task_lower or task_lower[:100] in msg_lower:
        return True

    # High word overlap
    msg_words = set(msg_lower.split())
    task_words = set(task_lower.split())
    if len(msg_words) > 3 and len(task_words) > 3:
        overlap = len(msg_words & task_words) / max(len(msg_words), 1)
        if overlap > 0.7:
            return True

    return False


def _estimate_content_depth(data: Dict[str, Any]) -> int:
    """Estimate the amount of real content in the agent's data output."""
    if not isinstance(data, dict):
        return 0

    total = 0

    # Check common content locations
    for key in ('content', 'enhanced_content', 'full_text', 'text', 'output',
                'report', 'findings', 'analysis', 'response'):
        val = data.get(key)
        if isinstance(val, str):
            total += len(val)
        elif isinstance(val, dict):
            # Recursively estimate
            for v in val.values():
                if isinstance(v, str):
                    total += len(v)

    # Check tool_results depth
    tool_results = data.get('tool_results', [])
    if isinstance(tool_results, list):
        for tr in tool_results:
            if isinstance(tr, dict):
                for v in tr.values():
                    if isinstance(v, str):
                        total += len(v)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, (str, dict)):
                                total += len(str(item))

    # Check results list
    results = data.get('results', [])
    if isinstance(results, list):
        for r in results:
            total += len(str(r))

    # Check recommendations
    recs = data.get('recommendations', [])
    if isinstance(recs, list):
        for r in recs:
            total += len(str(r))

    # Check key_insights
    insights = data.get('key_insights', [])
    if isinstance(insights, list):
        for i in insights:
            if isinstance(i, str) and len(i) > 20:
                total += len(i)

    return total
