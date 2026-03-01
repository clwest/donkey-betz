"""
PA Security Layer — Prompt Injection Defense + Enrichment Scrubbing.

Provides:
- scan_for_injection(): detect prompt injection attacks in user input
- scrub_enrichment_context(): sanitize enrichment sections before LLM injection

Usage:
    from core.services.pa_security import scan_for_injection, scrub_enrichment_context

    result = scan_for_injection(user_message, source='user_input')
    if result.severity == 'block':
        return blocked_response()

    clean_sections = scrub_enrichment_context(raw_sections)
"""

import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 8000


@dataclass
class InjectionResult:
    triggered: bool
    severity: str       # 'none' | 'warn' | 'block'
    pattern_name: str
    matched_text: str


# ── Block patterns (hard-block, unambiguous attacks) ─────────────────────────

_BLOCK_PATTERNS = [
    (
        'ignore_instructions',
        re.compile(
            r'ignore\s+(all\s+)?(previous|prior|above|earlier|preceding)\s+'
            r'(instructions|prompts|rules|directives|guidelines)',
            re.IGNORECASE,
        ),
    ),
    (
        'persona_hijack',
        re.compile(
            r'you\s+are\s+now\s+(a\s+)?(different|unrestricted|jailbroken|DAN|evil|unfiltered)',
            re.IGNORECASE,
        ),
    ),
    (
        'override_directive',
        re.compile(
            r'(forget|disregard|override|bypass)\s+'
            r'(everything|all|your|the)\s+'
            r'(instructions|system|rules|guidelines|constraints|programming)',
            re.IGNORECASE,
        ),
    ),
    (
        'delimiter_injection',
        re.compile(
            r'</system>|###\s*system|<\|im_start\|>|<\|im_end\|>|<\|endoftext\|>|\[INST\]|\[/INST\]',
            re.IGNORECASE,
        ),
    ),
]

# ── Warn patterns (log only, could be legit) ────────────────────────────────

_WARN_PATTERNS = [
    (
        'act_as',
        re.compile(r'act\s+as\s+a\s+', re.IGNORECASE),
    ),
    (
        'roleplay_directive',
        re.compile(r'(pretend|simulate)\s+(you\s+are|to\s+be)', re.IGNORECASE),
    ),
    (
        'base64_payload',
        re.compile(r'[A-Za-z0-9+/]{40,}={0,2}'),
    ),
    (
        'bidi_override',
        re.compile(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]'),
    ),
    (
        'internal_url',
        re.compile(
            r'(https?://)?(localhost|127\.0\.0\.\d+|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)',
            re.IGNORECASE,
        ),
    ),
]


def scan_for_injection(text: str, source: str = 'unknown') -> InjectionResult:
    """
    Scan text for prompt injection patterns.

    Args:
        text: The text to scan.
        source: Label for logging ('user_input', 'enrichment', etc.)

    Returns:
        InjectionResult with severity 'block', 'warn', or 'none'.
    """
    if not text:
        return InjectionResult(triggered=False, severity='none', pattern_name='', matched_text='')

    # Check block patterns first
    for name, pattern in _BLOCK_PATTERNS:
        match = pattern.search(text)
        if match:
            matched = match.group()[:120]
            logger.warning(
                f"[PA_SECURITY] BLOCK source={source} pattern={name} matched={matched!r}"
            )
            return InjectionResult(
                triggered=True,
                severity='block',
                pattern_name=name,
                matched_text=matched,
            )

    # Check warn patterns
    for name, pattern in _WARN_PATTERNS:
        match = pattern.search(text)
        if match:
            matched = match.group()[:120]
            logger.info(
                f"[PA_SECURITY] WARN source={source} pattern={name} matched={matched!r}"
            )
            return InjectionResult(
                triggered=True,
                severity='warn',
                pattern_name=name,
                matched_text=matched,
            )

    return InjectionResult(triggered=False, severity='none', pattern_name='', matched_text='')


def scrub_enrichment_context(sections: dict) -> dict:
    """
    Sanitize enrichment context sections before injection into LLM prompt.

    Runs PII/secret redaction via data_scrubber, then scans for injection
    patterns (warn-only — enrichment is system-generated, never blocked).

    Args:
        sections: Dict of enrichment section name -> content.

    Returns:
        Scrubbed copy of sections.
    """
    from core.services.data_scrubber import scrub_dict

    try:
        cleaned = scrub_dict(sections, max_depth=5)
    except Exception:
        cleaned = sections

    # Scan combined text for injection patterns (warn-only for enrichment)
    combined = ' '.join(
        str(v) for v in cleaned.values() if isinstance(v, str)
    )
    if combined:
        scan_for_injection(combined, source='enrichment')

    return cleaned
