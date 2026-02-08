"""
Phase 4: Content Review Panel v2

3 structured reviewers for the content deliberation pipeline:
  - SkepticReviewer (always): challenges claims, generic content, hallucination risk
  - FactCheckReviewer (always): verifies claim IDs have URLs, checks freshness
  - DomainPersonaReviewer (0-1): selected by domain detection

Existing content_review_panel.py stays untouched — this is a parallel v2 path.
Reviewer failure -> synthetic FAIL verdict (not skip) so DecisionEnforcer sees it.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

REQUIRED_REVIEW_KEYS = {'reviewer', 'verdict', 'top_issues', 'required_changes',
                        'suggested_edits', 'confidence'}
VALID_VERDICTS = {'PASS', 'REVISE', 'FAIL'}
VALID_ISSUE_TYPES = {'missing_citation', 'weak_claim', 'hallucination_risk',
                     'generic', 'tone', 'structure', 'reviewer_error'}
VALID_SEVERITIES = {'low', 'med', 'high'}


def validate_review_payload(data: Any) -> Tuple[bool, List[str]]:
    """
    Validate structured reviewer output.

    Returns:
        (is_valid, list_of_error_messages)
    """
    errors: List[str] = []

    if not isinstance(data, dict):
        return False, ['payload is not a dict']

    missing = REQUIRED_REVIEW_KEYS - set(data.keys())
    if missing:
        errors.append(f'missing keys: {sorted(missing)}')

    if data.get('verdict') not in VALID_VERDICTS:
        errors.append(f"invalid verdict: {data.get('verdict')}")

    issues = data.get('top_issues')
    if not isinstance(issues, list):
        errors.append('top_issues is not a list')
    else:
        for i, issue in enumerate(issues):
            if not isinstance(issue, dict):
                errors.append(f'top_issues[{i}] is not a dict')
                continue
            if 'type' not in issue or 'detail' not in issue:
                errors.append(f'top_issues[{i}] missing type or detail')

    if not isinstance(data.get('required_changes'), list):
        errors.append('required_changes is not a list')
    if not isinstance(data.get('suggested_edits'), list):
        errors.append('suggested_edits is not a list')

    conf = data.get('confidence')
    if not isinstance(conf, (int, float)):
        errors.append('confidence is not numeric')

    return len(errors) == 0, errors


def _make_fail_payload(reviewer_name: str, reason: str) -> dict:
    """Synthetic FAIL payload for when validation or LLM call fails."""
    return {
        'reviewer': reviewer_name,
        'verdict': 'FAIL',
        'top_issues': [{
            'type': 'reviewer_error',
            'detail': reason,
            'claim_ids': [],
            'severity': 'high',
        }],
        'required_changes': [],
        'suggested_edits': [],
        'confidence': 0.0,
    }


# ── Reviewer system prompts ──

SKEPTIC_SYSTEM = """You are a ruthless content skeptic. Your job is to find:
1. Claims without evidence or citation markers [C-xxxxxxxxxx]
2. Generic filler that adds no value
3. Hallucination risk — assertions not grounded in the provided claims data
4. Logical leaps or unsupported conclusions

Output ONLY valid JSON (no markdown fences) matching this schema:
{
  "reviewer": "SkepticReviewer",
  "verdict": "PASS|REVISE|FAIL",
  "top_issues": [{"type":"missing_citation|weak_claim|hallucination_risk|generic|tone|structure",
                   "detail":"...", "claim_ids":["C-xxxxxxxxxx"], "severity":"low|med|high"}],
  "required_changes": ["..."],
  "suggested_edits": ["..."],
  "confidence": 0.0
}

PASS = publishable as-is. REVISE = fixable issues. FAIL = fundamental problems."""

FACTCHECK_SYSTEM = """You are a fact-checker. Your job is to:
1. Verify every claim ID [C-xxxxxxxxxx] in the draft maps to a URL in the claims data
2. Flag any factual assertion without a [C-...] marker as unsourced
3. Check freshness — claims older than 48h deserve a staleness note
4. Ensure the Sources section at the end maps claim IDs to URLs

Output ONLY valid JSON (no markdown fences) matching this schema:
{
  "reviewer": "FactCheckReviewer",
  "verdict": "PASS|REVISE|FAIL",
  "top_issues": [{"type":"missing_citation|weak_claim|hallucination_risk|generic|tone|structure",
                   "detail":"...", "claim_ids":["C-xxxxxxxxxx"], "severity":"low|med|high"}],
  "required_changes": ["..."],
  "suggested_edits": ["..."],
  "confidence": 0.0
}"""

DOMAIN_SYSTEM_TEMPLATE = """You are a {domain} domain expert reviewing content for accuracy and depth.
Check that the content demonstrates genuine {domain} knowledge:
1. Terminology used correctly
2. Claims are realistic for the {domain} space
3. Analysis goes beyond surface-level commentary
4. Recommendations are actionable for {domain} practitioners

Output ONLY valid JSON (no markdown fences) matching this schema:
{{
  "reviewer": "DomainPersonaReviewer-{domain}",
  "verdict": "PASS|REVISE|FAIL",
  "top_issues": [{{"type":"missing_citation|weak_claim|hallucination_risk|generic|tone|structure",
                   "detail":"...", "claim_ids":["C-xxxxxxxxxx"], "severity":"low|med|high"}}],
  "required_changes": ["..."],
  "suggested_edits": ["..."],
  "confidence": 0.0
}}"""


def _call_llm_reviewer(system_prompt: str, user_content: str, reviewer_name: str) -> dict:
    """Call LLM for a single reviewer, validate, return payload or synthetic FAIL."""
    try:
        from core.llm_providers import get_llm_provider

        provider = get_llm_provider('openai')
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_content},
        ]

        response = provider.chat_completion(
            messages=messages,
            model='gpt-4.1-mini',
            temperature=0.3,
            max_tokens=1500,
        )

        raw = response.get('content', '') if isinstance(response, dict) else str(response)

        # Strip markdown fences if present
        raw = raw.strip()
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[-1]
        if raw.endswith('```'):
            raw = raw.rsplit('```', 1)[0]
        raw = raw.strip()

        data = json.loads(raw)
        is_valid, errors = validate_review_payload(data)
        if not is_valid:
            logger.warning(f"[Phase 4] {reviewer_name} invalid output: {errors}")
            return _make_fail_payload(reviewer_name, f'validation errors: {errors}')

        return data

    except json.JSONDecodeError as e:
        logger.warning(f"[Phase 4] {reviewer_name} JSON parse error: {e}")
        return _make_fail_payload(reviewer_name, f'JSON parse error: {e}')
    except Exception as e:
        logger.warning(f"[Phase 4] {reviewer_name} LLM call failed: {e}")
        return _make_fail_payload(reviewer_name, f'LLM error: {e}')


def _detect_domain(topic: str) -> Optional[str]:
    """Use DomainContentContextBuilder to detect domain."""
    try:
        from core.services.domain_content_context import DomainContentContextBuilder
        builder = DomainContentContextBuilder()
        domain, confidence = builder.detect_domain(topic)
        if domain != 'general' and confidence >= 0.2:
            return domain
    except Exception as e:
        logger.warning(f"[Phase 4] Domain detection failed: {e}")
    return None


def run_reviews(
    draft: str,
    claims_pack,
    topic: str,
    domain: Optional[str] = None,
) -> List[dict]:
    """
    Run all reviewers against a draft + claims pack.

    Args:
        draft: The full blog text
        claims_pack: ClaimsPack instance (or None)
        topic: Blog topic
        domain: Optional pre-detected domain

    Returns:
        List of reviewer result dicts (always at least 2: Skeptic + FactCheck)
    """
    claims_block = ''
    if claims_pack is not None:
        claims_block = claims_pack.to_prompt_block()

    user_content = f"""TOPIC: {topic}

CLAIMS DATA:
{claims_block if claims_block else '(no claims data available)'}

DRAFT TO REVIEW:
{draft[:8000]}"""

    reviews: List[dict] = []

    # 1. SkepticReviewer (always)
    reviews.append(_call_llm_reviewer(SKEPTIC_SYSTEM, user_content, 'SkepticReviewer'))

    # 2. FactCheckReviewer (always)
    reviews.append(_call_llm_reviewer(FACTCHECK_SYSTEM, user_content, 'FactCheckReviewer'))

    # 3. DomainPersonaReviewer (0-1, based on domain)
    if domain is None:
        domain = _detect_domain(topic)

    if domain and domain != 'general':
        domain_prompt = DOMAIN_SYSTEM_TEMPLATE.format(domain=domain)
        reviews.append(_call_llm_reviewer(
            domain_prompt, user_content, f'DomainPersonaReviewer-{domain}'
        ))

    return reviews
