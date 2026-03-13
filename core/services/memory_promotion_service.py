"""
Durable Memory Promotion Service

Automatically detects project-critical operational facts in PA conversation
turns and promotes them to persistent memory. No manual "remember this" needed.

Promotion triggers:
  - Milestone language (deployed, shipped, live, submitted, rolled back, etc.)
  - Identifiers (bundle IDs, repo slugs, service names, URLs, versions)
  - Wiring/topology statements (service A calls service B, endpoint is X)

Scoring:
  - >=7: auto-save
  - 5-6: pending (logged, not auto-saved — future: ask-confirm)
  - <=4: ignore

Safety:
  - Never stores API keys, tokens, passwords, signing certs, private keys
  - Uses existing _redact_secrets for sanitization
  - Deduplicates against existing memories by content hash
"""

import hashlib
import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Milestone language patterns ──────────────────────────────────────────────

_MILESTONE_PATTERNS = [
    re.compile(r'\b(deploy(?:ed|ing|ment|s)?)\b', re.IGNORECASE),
    re.compile(r'\b(ship(?:ped|ping|s)?)\b', re.IGNORECASE),
    re.compile(r'\b(?:went|is|are|now)\s+(live)\b', re.IGNORECASE),
    re.compile(r'\b(launch(?:ed|ing)?)\b', re.IGNORECASE),
    re.compile(r'\b(submitted?\s+to\s+(?:TestFlight|App\s*Store|Google\s*Play|review))\b', re.IGNORECASE),
    re.compile(r'\b(roll(?:ed)?\s*back)\b', re.IGNORECASE),
    re.compile(r'\b(incident\s+resolved)\b', re.IGNORECASE),
    re.compile(r'\b(migration\s+(?:completed?|ran|applied|succeeded))\b', re.IGNORECASE),
    re.compile(r'\b(release(?:d)?)\s+(?:v[\d.]+|version)\b', re.IGNORECASE),
    re.compile(r'\b(merged?\s+(?:to|into)\s+(?:main|master|production))\b', re.IGNORECASE),
    re.compile(r'\b(cut\s+(?:a\s+)?release)\b', re.IGNORECASE),
    re.compile(r'\b(hotfix(?:ed)?)\b', re.IGNORECASE),
    re.compile(r'\b(provisioning\s+profile)\b', re.IGNORECASE),
    re.compile(r'\b(certificate\s+(?:created|installed|renewed))\b', re.IGNORECASE),
]

# ── Identifier patterns ─────────────────────────────────────────────────────

_IDENTIFIER_PATTERNS = {
    'bundle_id': re.compile(r'\b(com\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9._-]+)\b'),
    'android_package': re.compile(r'\b(com\.[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*){2,})\b'),
    'version_build': re.compile(r'\b(v?\d+\.\d+(?:\.\d+)?(?:\s*\(\d+\))?)\b'),
    'repo_slug': re.compile(r'\b([a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)(?:\.git)?\b'),
    'git_url': re.compile(r'((?:https?://|git@)(?:github|gitlab|bitbucket)[^\s]+)'),
    'commit_sha': re.compile(r'\b([0-9a-f]{7,40})\b'),
    'railway_service': re.compile(r'\b(railway\s+(?:service|env|project)\s*[:=]?\s*\S+)', re.IGNORECASE),
    'base_url': re.compile(r'(https?://[a-zA-Z0-9_.-]+\.(?:up\.railway\.app|herokuapp\.com|vercel\.app|netlify\.app|onrender\.com|fly\.dev)[/\w.-]*)'),
    'worker_queue': re.compile(r'\b(celery[-_](?:worker|pa|content|long[-_]running|broadcast|beat|ml))\b', re.IGNORECASE),
    'port_binding': re.compile(r'\b(?:port|PORT)\s*[:=]\s*(\d{4,5})\b'),
    'docker_image': re.compile(r'\b([a-z0-9_-]+(?:/[a-z0-9_.-]+)+:[a-z0-9._-]+)\b'),
}

# ── Wiring / topology patterns ──────────────────────────────────────────────

_WIRING_PATTERNS = [
    re.compile(r'\b(\S+\s+(?:calls?|talks?\s+to|connects?\s+to|sends?\s+(?:data\s+)?to|feeds?\s+into)\s+\S+)', re.IGNORECASE),
    re.compile(r'\b((?:endpoint|route|api)\s+(?:is|at|=)\s+\S+)', re.IGNORECASE),
    re.compile(r'\b(CI\s+(?:workflow|pipeline|action)\s+(?:is|runs?|uses?)\s+.{5,80})', re.IGNORECASE),
    re.compile(r'\b((?:start|build|deploy)\s+command\s*[:=]\s*.{5,120})', re.IGNORECASE),
    re.compile(r'\b(Procfile\s+(?:process|line|entry)\s+.{5,80})', re.IGNORECASE),
]

# ── Secret patterns (NEVER store these) ──────────────────────────────────────

_SECRET_PATTERNS = [
    re.compile(r'sk-[a-zA-Z0-9]{20,}'),
    re.compile(r'ghp_[a-zA-Z0-9]{36,}'),
    re.compile(r'xoxb-[a-zA-Z0-9\-]+'),
    re.compile(r'eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}'),
    re.compile(r'AKIA[A-Z0-9]{16}'),
    re.compile(r'-----BEGIN\s+(?:RSA\s+)?PRIV' + r'ATE\s+KEY-----'),
    re.compile(r'\b(?:password|passwd|secret)\s*[:=]\s*\S+', re.IGNORECASE),
    re.compile(r'\b(?:api[_-]?key|token|auth)\s*[:=]\s*["\']?\S{20,}', re.IGNORECASE),
]

# ── Tag inference rules ──────────────────────────────────────────────────────

_TAG_KEYWORDS = {
    'deploy': ['deploy', 'deployed', 'deployment', 'railway', 'heroku', 'vercel', 'fly.dev'],
    'release': ['release', 'released', 'version', 'build', 'shipped'],
    'mobile': ['testflight', 'app store', 'google play', 'bundle', 'ios', 'android', 'expo'],
    'repo': ['github', 'gitlab', 'bitbucket', 'repo', 'repository', 'git'],
    'infra': ['worker', 'queue', 'celery', 'redis', 'postgres', 'docker', 'port'],
    'ci': ['ci', 'pipeline', 'workflow', 'action', 'build'],
    'rollback': ['rollback', 'rolled back', 'reverted', 'hotfix'],
    'migration': ['migration', 'migrated', 'schema'],
    'railway': ['railway'],
    'testflight': ['testflight'],
}


def _contains_secret(text: str) -> bool:
    """Check if text contains any secret/credential patterns."""
    return any(p.search(text) for p in _SECRET_PATTERNS)


def _infer_tags(text: str) -> List[str]:
    """Infer tags from text content."""
    text_lower = text.lower()
    tags = []
    for tag, keywords in _TAG_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            tags.append(tag)
    return tags[:5]  # Cap at 5 tags


def score_for_promotion(text: str) -> Tuple[int, Dict]:
    """
    Score a text block for memory promotion.

    Returns (score, details) where:
      - score: 0-10 promotion score
      - details: dict with matched triggers, identifiers, wiring statements

    Scoring:
      +3 for milestone language
      +2 for each identifier type found (max +6)
      +2 for wiring/topology statement
      -10 if contains secrets (hard block)
    """
    if _contains_secret(text):
        return 0, {'blocked': 'contains_secret'}

    score = 0
    details: Dict = {
        'milestones': [],
        'identifiers': {},
        'wiring': [],
    }

    # Milestone language (+3)
    for pat in _MILESTONE_PATTERNS:
        m = pat.search(text)
        if m:
            details['milestones'].append(m.group(1))
            score += 3
            break  # Only count milestone once

    # Identifiers (+2 each, max +6)
    id_score = 0
    for id_type, pat in _IDENTIFIER_PATTERNS.items():
        matches = pat.findall(text)
        if matches:
            # Filter out commit SHAs that are too short or look like hex noise
            if id_type == 'commit_sha':
                matches = [m for m in matches if len(m) >= 7 and not m.isdigit()]
            if matches:
                details['identifiers'][id_type] = matches[:3]  # Keep top 3
                id_score += 2
    score += min(id_score, 6)

    # Wiring/topology (+2)
    for pat in _WIRING_PATTERNS:
        m = pat.search(text)
        if m:
            details['wiring'].append(m.group(1).strip())
            score += 2
            break  # Only count wiring once

    return min(score, 10), details


def extract_promotion_content(text: str, details: Dict) -> str:
    """
    Build a structured key-value memory content block from detected facts.
    """
    lines = []

    if details.get('milestones'):
        lines.append(f"Event: {', '.join(details['milestones'])}")

    for id_type, values in details.get('identifiers', {}).items():
        label = id_type.replace('_', ' ').title()
        lines.append(f"{label}: {', '.join(str(v) for v in values)}")

    if details.get('wiring'):
        lines.append(f"Topology: {'; '.join(details['wiring'])}")

    # If we have structured fields, use them; otherwise use a truncated version
    if lines:
        return '\n'.join(lines)
    return text[:300]


def check_and_promote(
    user_message: str,
    assistant_response: str,
    tool_runs: List[Dict],
    user,
    trace_id: str = '',
) -> Optional[Dict]:
    """
    Scan a conversation turn for promotable operational facts.

    Checks user message, assistant response, and tool results.
    Auto-saves if score >= 7. Logs if score 5-6 (pending promotion).

    Returns dict with promotion result, or None if nothing promoted.
    """
    # Combine all text sources for scanning
    text_blocks = [user_message, assistant_response]
    for run in (tool_runs or []):
        result = run.get('result')
        if isinstance(result, dict):
            # Extract text from tool results
            for key in ('message', 'content', 'summary', 'output', 'status'):
                val = result.get(key)
                if isinstance(val, str) and len(val) > 10:
                    text_blocks.append(val)
        elif isinstance(result, str) and len(result) > 10:
            text_blocks.append(result)

    combined = '\n'.join(text_blocks)

    # Score for promotion
    score, details = score_for_promotion(combined)

    if details.get('blocked'):
        logger.info(f"[{trace_id}] Memory promotion blocked: {details['blocked']}")
        return None

    if score <= 4:
        return None

    if 5 <= score <= 6:
        logger.info(
            f"[{trace_id}] Memory promotion PENDING (score={score}): "
            f"milestones={details.get('milestones')}, "
            f"identifiers={list(details.get('identifiers', {}).keys())}"
        )
        return {
            'action': 'pending',
            'score': score,
            'details': details,
        }

    # Score >= 7: auto-promote
    content = extract_promotion_content(combined, details)

    # Secret redaction
    from core.services.tool_dispatcher import _redact_secrets
    content = _redact_secrets(content)

    # Double-check after redaction
    if _contains_secret(content):
        logger.warning(f"[{trace_id}] Memory promotion blocked post-redaction")
        return None

    tags = _infer_tags(combined)

    try:
        from core.models import UserMemoryContext, EnhancedUserProfile
        from core.services.memory_context_service import get_memory_context_service

        profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)

        # Deduplication: hash of content + type
        content_hash = hashlib.sha256(
            f"{content.lower().strip()}:project".encode()
        ).hexdigest()[:16]

        existing = UserMemoryContext.objects.filter(
            user=user,
            context_metadata__content_hash=content_hash,
        ).first()

        if existing:
            # Update existing memory with changelog
            from django.utils import timezone
            changelog = existing.context_metadata.get('changelog', [])
            changelog.append({
                'date': timezone.now().isoformat()[:10],
                'prev': existing.content[:100],
            })
            existing.content = content
            existing.importance = max(existing.importance, 9)
            existing.tags = list(set(existing.tags + tags))
            existing.context_metadata['changelog'] = changelog[-5:]  # Keep last 5
            existing.context_metadata['trace_id'] = trace_id
            existing.save(update_fields=['content', 'importance', 'tags', 'context_metadata'])
            logger.info(f"[{trace_id}] Memory promotion UPDATED existing id={existing.id}")
            return {
                'action': 'updated',
                'memory_id': existing.id,
                'score': score,
                'content': content[:100],
                'tags': tags,
            }

        # Create new memory
        memory = UserMemoryContext.objects.create(
            user=user,
            profile=profile,
            memory_type='project',
            content=content[:500],
            importance=9,
            source='auto_promotion',
            tags=tags,
            context_metadata={
                'content_hash': content_hash,
                'trace_id': trace_id,
                'promotion_score': score,
                'milestones': details.get('milestones', []),
                'identifier_types': list(details.get('identifiers', {}).keys()),
            },
        )

        # Clear memory cache
        svc = get_memory_context_service()
        svc.clear_cache(user)

        logger.info(
            f"[{trace_id}] Memory promotion AUTO-SAVED id={memory.id} "
            f"score={score} tags={tags}"
        )
        return {
            'action': 'saved',
            'memory_id': memory.id,
            'score': score,
            'content': content[:100],
            'tags': tags,
        }

    except Exception as e:
        logger.warning(f"[{trace_id}] Memory promotion save failed: {e}")
        return {'action': 'error', 'error': str(e)}
