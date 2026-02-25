"""
Session 1074: Executor Policy Engine — Tier A/B/C action classification.

See: docs/decisions/ADR-0002-moderate-dangerous-action-policy.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

Tier = Literal['A', 'B', 'C']

# ── Tier C: Blocked patterns ─────────────────────────────────────────────────

_TIER_C_PATTERNS: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r'\bsudo\b',
        r'\bsu\s',
        r'/var/run/docker\.sock',
        r'\bdocker\s+(run|exec|build|pull|push)',
        r'rm\s+(-rf?|--recursive)\s+(/|~|\.\.|/etc|/usr|/var)',
        r'>\s*/etc/',
        r'>\s*/usr/',
        r'>\s*/var/',
        r'>\s*\.env\b',
        r'\bkill\s+-9?\s*(1|$$)',
        r'\bpkill\s',
        r'\bnc\s+-l',
        r'python\s+-m\s+http\.server',
        r':(){ :|:& };:',  # fork bomb
        r'\bchmod\s+[47]77\s+/',
        r'\bchown\s+root',
        r'\bmount\b',
        r'\bcryptominer|xmrig|minerd\b',
    ]
]

# ── Tier B: Approval-required patterns ────────────────────────────────────────

_TIER_B_PATTERNS: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r'\bgit\s+commit\b',
        r'\bgit\s+push\b',
        r'\bgh\s+pr\s+(create|merge|close)',
        r'\bgh\s+issue\s+(create|close)',
        r'manage\.py\s+migrate\b',
        r'(settings|\.env|Dockerfile|Procfile|docker-compose|\.github/)',
        r'requirements.*\.txt',
        r'package\.json',
        r'\bpip\s+install\b(?!.*-r)',  # pip install (but not -r requirements)
        r'\bnpm\s+install\s+\S',  # npm install <specific package>
        r'railway\s+(up|deploy|redeploy)',
    ]
]

# ── Tier A: Explicitly safe patterns (informational, not used for gating) ─────

_TIER_A_EXAMPLES = [
    'cat', 'grep', 'find', 'ls', 'head', 'tail', 'wc',
    'git status', 'git diff', 'git log', 'git branch',
    'python -m pytest', 'npm test', 'npx tsc --noEmit',
    'flake8', 'ruff', 'eslint', 'prettier',
]


@dataclass
class PolicyResult:
    tier: Tier
    command: str
    reason: str


def classify_command(command: str) -> PolicyResult:
    """Classify a shell command into Tier A (auto), B (approval), or C (blocked)."""
    # Check Tier C first (blocked)
    for pattern in _TIER_C_PATTERNS:
        if pattern.search(command):
            return PolicyResult(
                tier='C',
                command=command,
                reason=f'Blocked: matches dangerous pattern {pattern.pattern!r}',
            )

    # Check Tier B (requires approval)
    for pattern in _TIER_B_PATTERNS:
        if pattern.search(command):
            return PolicyResult(
                tier='B',
                command=command,
                reason=f'Requires approval: matches pattern {pattern.pattern!r}',
            )

    # Default: Tier A (auto-allowed)
    return PolicyResult(
        tier='A',
        command=command,
        reason='Auto-allowed: no dangerous or approval-required patterns matched',
    )


def classify_plan(steps: list[dict]) -> dict:
    """Classify all steps in a plan. Returns summary with per-step results."""
    results = []
    blocked = []
    needs_approval = []

    for i, step in enumerate(steps):
        cmd = step.get('command', '')
        result = classify_command(cmd)
        results.append({
            'step': i,
            'command': cmd,
            'tier': result.tier,
            'reason': result.reason,
        })
        if result.tier == 'C':
            blocked.append(i)
        elif result.tier == 'B':
            needs_approval.append(i)

    return {
        'results': results,
        'blocked_steps': blocked,
        'approval_required_steps': needs_approval,
        'has_blocked': len(blocked) > 0,
        'needs_approval': len(needs_approval) > 0,
        'can_auto_run': len(blocked) == 0 and len(needs_approval) == 0,
    }
