"""
Initiative Title Generator
===========================

Session 905: Generates clean, concise titles for initiatives from raw content.

Problem: Initiative names were showing fragments like:
- "event taxonomy event stream, competitor content CSVs, and ≥5 external..."
- "quality scores, (4) exposes a validation workflow for ResearchAgent..."
- "driven Content Blueprint Generator: inputs = seed persona JSON..."

Solution: Smart title extraction with LLM fallback and heuristic cleanup.

Usage:
    from core.services.initiative_title_generator import generate_initiative_title
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

    title = generate_initiative_title(
        content="Long raw text with the actual topic buried somewhere...",
        topic_hint="Optional hint about what this is about",
        max_length=60
    )
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Session 943: Junk prefixes that leak from knowledge transfer and other sources
JUNK_PREFIXES = [
    '[Learned] ',
    '[Learned]',
    '[Synthesis] ',
    '[Synthesis]',
    'Learned: ',
    'Synthesis: ',
    'Discussion: ',
    'Panel: ',
    'Research: ',
    'Experiment: ',
    'Feature name: ',
    "Feature name: '",
]


def _strip_junk_prefixes(text: str) -> str:
    """
    Session 943: Strip common junk prefixes that leak into initiative names.

    These come from:
    - Knowledge transfer ([Learned])
    - Synthesis outputs ([Synthesis])
    - Conversation topics (Discussion:, Panel:)
    - Feature extraction (Feature name:)
    """
    if not text:
        return ""

    # Strip prefixes iteratively (they can be nested)
    changed = True
    while changed:
        changed = False
        for prefix in JUNK_PREFIXES:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                changed = True

    # Also strip trailing quotes that might be left over
    text = text.strip("'\"")

    return text.strip()


def generate_initiative_title(
    content: str,
    topic_hint: Optional[str] = None,
    max_length: int = 60,
    use_llm: bool = True
) -> str:
    """
    Generate a clean, concise title for an initiative.

    Args:
        content: Raw content text (could be messy/fragmented)
        topic_hint: Optional hint from conversation topic
        max_length: Maximum title length (default 60 chars)
        use_llm: Whether to use LLM for title generation (default True)

    Returns:
        Clean, properly capitalized title (max_length chars)
    """
    # Session 943: Pre-clean content and topic_hint to remove junk prefixes
    content = _strip_junk_prefixes(content) if content else ""
    topic_hint = _strip_junk_prefixes(topic_hint) if topic_hint else None

    # Step 1: Try to use the topic_hint if it's clean
    if topic_hint:
        cleaned_hint = _clean_title_text(topic_hint)
        if _is_valid_title(cleaned_hint, max_length):
            return cleaned_hint[:max_length]

    # Step 2: Try LLM generation
    if use_llm:
        llm_title = _generate_title_with_llm(content, topic_hint)
        if llm_title and _is_valid_title(llm_title, max_length):
            return llm_title[:max_length]

    # Step 3: Use heuristic extraction
    heuristic_title = _extract_title_heuristically(content, topic_hint)
    if heuristic_title:
        return heuristic_title[:max_length]

    # Step 4: Ultimate fallback
    return _create_fallback_title(content, topic_hint)[:max_length]


def _is_valid_title(title: str, max_length: int = 80) -> bool:
    """
    Check if a title is valid (not a fragment, reasonable length).

    Invalid patterns:
    - Starts with lowercase (likely fragment)
    - Starts with conjunctions/prepositions (except action verbs)
    - Contains technical fragments like "inputs =", "(4) exposes"
    - Too short (< 5 chars) or too long
    - Contains only punctuation/numbers
    - Session 943: Contains [Learned], [Synthesis], or other junk prefixes
    """
    if not title or len(title) < 5:
        return False

    if len(title) > max_length:
        return False

    # Session 943: Reject titles with junk prefixes that leaked through
    for prefix in JUNK_PREFIXES:
        if prefix.lower() in title.lower():
            return False

    # Session 943: Reject titles that look like truncated fragments
    # These end with partial words or have unbalanced quotes
    if title.count("'") == 1 or title.count('"') == 1:
        return False  # Unbalanced quotes = truncated
    if re.search(r"[a-z]{3,}$", title) and not title.endswith(('ing', 'tion', 'ment', 'ness', 'able', 'ible')):
        # Ends with lowercase letters but not a common suffix - might be truncated
        # Only flag if no space before the ending (definitely mid-word)
        last_space = title.rfind(' ')
        if last_space > 0 and len(title) - last_space > 15:
            return False  # Long word at end, likely truncated

    title_lower = title.lower().strip()

    # Allow titles starting with action verbs
    action_verbs = ['audit', 'investigate', 'analyze', 'build', 'create', 'design',
                    'implement', 'review', 'research', 'develop', 'test', 'fix',
                    'update', 'improve', 'optimize', 'validate', 'deploy', 'monitor']
    starts_with_action = any(title_lower.startswith(verb) for verb in action_verbs)

    # Check for fragment indicators
    # Note: These patterns are checked case-sensitively where it matters
    fragment_patterns_case_insensitive = [
        r'^\d+\.',  # Starts with numbered list
        r'^\(\d+\)',  # Starts with (1), (2), etc.
        r'inputs?\s*[=:]',  # Contains "inputs ="
        r'outputs?\s*[=:]',  # Contains "outputs ="
        r'\(\d+\)\s*\w+',  # Contains "(4) something"
        r';\s*\w+',  # Contains "; something" mid-text
        r'\.{3}',  # Contains ellipsis
    ]

    for pattern in fragment_patterns_case_insensitive:
        if re.search(pattern, title, re.IGNORECASE):
            return False

    # Case-sensitive patterns (must actually start with lowercase)
    fragment_patterns_case_sensitive = [
        r'^and\s',  # Starts with 'and'
        r'^or\s',  # Starts with 'or'
        r'^the\s[a-z]',  # Starts with 'the' + lowercase
        r'^to\s[a-z]',  # Starts with 'to' + lowercase
        r'^for\s[a-z]',  # Starts with 'for' + lowercase
        r'^with\s[a-z]',  # Starts with 'with' + lowercase
        r'^in\s[a-z]',  # Starts with 'in' + lowercase
        r'^of\s',  # Starts with 'of'
        r'^\s*-\s*',  # Starts with bullet point
        r'^[a-z]{2,}\s+[a-z]',  # Starts with lowercase words (fragment)
    ]

    for pattern in fragment_patterns_case_sensitive:
        if re.search(pattern, title):  # Case-sensitive!
            return False

    # Must start with capital letter or be an action verb title
    if not starts_with_action and re.match(r'^[a-z]', title):
        return False

    # Must contain at least one letter
    if not re.search(r'[a-zA-Z]', title):
        return False

    # Check it's not just a sentence fragment (contains common mid-sentence markers)
    mid_sentence_markers = [', and ', ', or ', ' that ', ' which ', ' where ', ' when ']
    marker_count = sum(1 for m in mid_sentence_markers if m in title.lower())
    if marker_count >= 2:
        return False

    return True


def _clean_title_text(text: str) -> str:
    """
    Clean up raw text to make it more title-like.
    """
    if not text:
        return ""

    # Remove markdown formatting
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # [text](link) -> text

    # Remove code blocks
    text = re.sub(r'`[^`]+`', '', text)

    # Remove leading bullets, dashes, numbers
    text = re.sub(r'^[\s\-*•→]+', '', text)
    text = re.sub(r'^\d+\.\s*', '', text)

    # Remove parenthetical content at the end
    text = re.sub(r'\s*\([^)]*\)\s*$', '', text)

    # Remove trailing punctuation (except ? and !)
    text = re.sub(r'[,;:\-]+\s*$', '', text)

    # Remove technical markers
    text = re.sub(r'\s*inputs?\s*[=:].*$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*outputs?\s*[=:].*$', '', text, flags=re.IGNORECASE)

    # Normalize whitespace
    text = ' '.join(text.split())

    return text.strip()


def _generate_title_with_llm(content: str, topic_hint: Optional[str] = None) -> Optional[str]:
    """
    Use LLM to generate a concise title from content.
    """
    try:
        import os

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.debug("No OpenAI API key found for title generation")
            return None

        client = get_openai_client(api_key=api_key)

        # Truncate content for token efficiency
        content_preview = content[:1500] if content else ""

        prompt = f"""Generate a clear, concise title (5-10 words max) for this initiative.

Content preview:
{content_preview}

{f'Topic hint: {topic_hint}' if topic_hint else ''}

Rules:
- Title should be action-oriented when possible (e.g., "Audit Experiment Halt Conditions")
- Use Title Case capitalization
- No punctuation at the end
- Must make sense standalone
- Maximum 60 characters

Return ONLY the title, nothing else."""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a title generator. Output only the title."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=50,
        )

        title = response.choices[0].message.content.strip()

        # Remove quotes if the model wrapped the title
        title = title.strip('"\'')

        # Remove any prefix like "Title:" that the model might add
        title = re.sub(r'^(?:Title|Name|Subject):\s*', '', title, flags=re.IGNORECASE)

        logger.debug(f"LLM generated title: {title}")
        return title

    except Exception as e:
        logger.warning(f"LLM title generation failed: {e}")
        return None


def _extract_title_heuristically(content: str, topic_hint: Optional[str] = None) -> Optional[str]:
    """
    Extract a title using heuristics when LLM is not available.
    """
    if not content:
        return None

    # Strategy 1: Look for a clear "Name:" or "Title:" line
    name_match = re.search(r'(?:Name|Title|Topic|Subject):\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
    if name_match:
        candidate = _clean_title_text(name_match.group(1))
        if _is_valid_title(candidate):
            return _capitalize_title(candidate)

    # Strategy 2: Look for markdown headers
    header_match = re.search(r'^#+\s*(.+?)$', content, re.MULTILINE)
    if header_match:
        candidate = _clean_title_text(header_match.group(1))
        if _is_valid_title(candidate):
            return _capitalize_title(candidate)

    # Strategy 3: Look for Research/Audit/Investigate patterns
    action_patterns = [
        r'((?:Research|Audit|Investigate|Analyze|Build|Create|Design|Implement|Review)\s+(?:[\w\s]+?)(?:for|of|and)?[\w\s]*?)(?:\.|,|\n|$)',
        r'((?:[\w]+\s+)?(?:Pipeline|Engine|System|Module|Service|Agent)(?:\s+for\s+[\w\s]+)?)',
    ]

    for pattern in action_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            candidate = _clean_title_text(match.group(1))
            if _is_valid_title(candidate):
                return _capitalize_title(candidate)

    # Strategy 4: Take first sentence and clean it
    first_sentence = re.split(r'[.\n]', content)[0]
    candidate = _clean_title_text(first_sentence)

    if len(candidate) > 60:
        # Take first few meaningful words
        words = candidate.split()
        shortened = ' '.join(words[:6])
        if _is_valid_title(shortened):
            return _capitalize_title(shortened)
    elif _is_valid_title(candidate):
        return _capitalize_title(candidate)

    # Strategy 5: Use topic_hint if available, even if imperfect
    if topic_hint:
        cleaned = _clean_title_text(topic_hint)
        words = cleaned.split()[:8]  # Take first 8 words
        candidate = ' '.join(words)
        if len(candidate) >= 5:
            return _capitalize_title(candidate)

    return None


def _capitalize_title(text: str) -> str:
    """
    Apply proper title case capitalization.
    """
    # Words that shouldn't be capitalized (unless first word)
    minor_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

    words = text.split()
    result = []

    for i, word in enumerate(words):
        if i == 0 or word.lower() not in minor_words:
            # Capitalize first letter, keep rest as-is (preserves acronyms)
            if word.isupper() and len(word) > 1:
                result.append(word)  # Keep acronyms
            else:
                result.append(word.capitalize())
        else:
            result.append(word.lower())

    return ' '.join(result)


def _create_fallback_title(content: str, topic_hint: Optional[str] = None) -> str:
    """
    Create a reasonable fallback title when all else fails.
    Includes a unique identifier to prevent duplicate key errors.
    """
    import uuid
    unique_suffix = str(uuid.uuid4())[:6]

    # Try to extract any meaningful noun phrase
    if content:
        # Look for capitalized phrases
        cap_phrases = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', content)
        if cap_phrases:
            for phrase in cap_phrases:
                if 5 <= len(phrase) <= 50:  # Leave room for suffix
                    return f"{phrase} ({unique_suffix})"

    # Try to extract key terms from content
    if content:
        # Look for common module/feature patterns
        patterns = [
            r'((?:Pipeline|Engine|Module|System|Service|Agent|Audit|Analysis)\s*)',
            r'((?:Enhancement|Generator|Validator|Builder|Creator)\s*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                term = match.group(1).strip().title()
                return f"{term} ({unique_suffix})"

    if topic_hint:
        # Take first 3 meaningful words from hint
        words = [w for w in topic_hint.split() if len(w) > 2][:3]
        if words:
            return f"Initiative: {' '.join(words).title()} ({unique_suffix})"

    # Ultimate fallback with timestamp and UUID
    from datetime import datetime
    timestamp = datetime.now().strftime("%m-%d %H:%M")
    return f"Initiative {timestamp} ({unique_suffix})"


# Quick test function
def test_title_generation():
    """Test the title generator with known problematic cases."""
    test_cases = [
        ("event taxonomy event stream, competitor content CSVs, and ≥5 external verification sources plus privacy/consent metadata; outputs include per-creat...", None),
        ("quality scores, (4) exposes a validation workflow for ResearchAgent review, and (5) writes validated artifacts into the agent learning/KB.", None),
        ("driven Content Blueprint Generator: inputs = seed persona JSON (motivations, pain points, channel_weights, preferred_formats, KPIs), competitor aud...", None),
        ("Audit failed experiments and halt conditions", None),
        ("# Research Brief: Investigate Repeated Experiment Halts\n\nThis document outlines...", None),
        ("- Name: Persona Synthesis Engine\n- Inputs: Seed community posts...", None),
    ]

    print("Testing title generator...")
    for content, hint in test_cases:
        title = generate_initiative_title(content, hint, use_llm=False)
        print(f"\nInput: {content[:60]}...")
        print(f"Output: {title}")


if __name__ == "__main__":
    test_title_generation()
