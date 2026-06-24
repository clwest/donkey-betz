"""
DeliverableFactory — Single gateway for creating Deliverables.

Consolidates 23+ scattered Deliverable.objects.create() calls into one
factory with consistent metadata, workspace assignment, and provenance tracking.

Usage:
    from core.services.deliverable_factory import create_deliverable

    deliverable = create_deliverable(
        title="Market Analysis Report",
        content="## Findings\n...",
        agent_name="ResearchAgent",
        category="Research",
        user=request.user,
        # Optional:
        workspace_id=workspace.id,
        trace_id=trace_id,
        parent_execution_id=execution.id,
        tags=["research", "market"],
        content_format="markdown",
        quality_score=0.85,
        metadata={"source": "scheduled_run"},
    )
"""

import hashlib
import logging
import re
import uuid
from datetime import date
from typing import Any, Iterable, List, Optional

from django.conf import settings

logger = logging.getLogger(__name__)


# Session 1169 — Layer C Phase 1. Typed exception for quality-gate
# rejection. Callers that opt in via raise_on_gated=True can build
# structured error responses (with reason_code) instead of inferring
# the rejection from a silent None return. Default behavior preserved:
# create_deliverable still returns None on gate reject for callers
# that haven't opted in (the existing 27 production caller sites all
# stay on the legacy contract until Phase 2 migrates them in batches).
class DeliverableGatedError(Exception):
    """Raised when ``create_deliverable``'s quality gate rejects input.

    Attributes:
        reason: Human-readable reason ("smoke test pattern in title").
        reason_code: Machine-parseable code from the gate that fired.
            One of: gate_1_media_stub, gate_2_smoke_pattern,
            gate_3_min_length, gate_4_template_leak,
            gate_5_no_relevance, unknown_gate.
        title: The title that was rejected (truncated to 120 chars).
        agent_name: The agent_name argument that was passed in.
    """

    def __init__(
        self,
        reason: str,
        reason_code: str = 'unknown_gate',
        title: str = '',
        agent_name: str = '',
    ):
        self.reason = reason
        self.reason_code = reason_code
        self.title = (title or '')[:120]
        self.agent_name = agent_name or ''
        super().__init__(
            f"Deliverable gated: {reason} "
            f"(reason_code={reason_code}, "
            f"title={self.title!r}, agent={self.agent_name!r})"
        )


class DeliverableProvenanceMissingError(Exception):
    """Raised when ``create_deliverable`` is called for a non-PA-direct
    agent without ``parent_execution_id``.

    Session 1199 PR-D contract flip — replaces the Session 1184 PR-B
    soft WARN path with a hard exception. PA-direct contexts (e.g.,
    ``deliverable_tool.create`` from the chat UI) still synthesize an
    AgentExecution receipt and DO NOT raise. Non-PA agent-dispatch
    paths MUST pass ``parent_execution_id`` — that's the no-orphan
    provenance contract.

    24h WARN-volume watch (deliverable ``9d9db48a-…``) showed zero
    violations on local for the 24h window after PR #2376 merged, so
    the flip is safe.

    Attributes:
        agent_name: Agent that tried to create without provenance.
        title: Deliverable title (truncated to 120 chars).
        trigger_source: ``metadata['trigger_source']`` if known.
        caller: Caller fingerprint from ``_resolve_caller_fingerprint``.
    """

    def __init__(
        self,
        agent_name: str = '',
        title: str = '',
        trigger_source: str = 'unknown',
        caller: str = 'unknown',
    ):
        self.agent_name = agent_name or ''
        self.title = (title or '')[:120]
        self.trigger_source = trigger_source or 'unknown'
        self.caller = caller or 'unknown'
        super().__init__(
            f"Deliverable provenance missing for non-PA agent "
            f"(agent={self.agent_name!r}, trigger_source={self.trigger_source!r}, "
            f"caller={self.caller!r}, title={self.title!r}). "
            f"Caller MUST pass parent_execution_id. Session 1199 PR-D "
            f"contract — was a logger.warning() through Session 1198."
        )


def _content_hash(title: str, content: str, agent_name: str) -> str:
    """
    Generate a deterministic hash from deliverable content for dedup.
    Uses title + first 2000 chars of content + agent_name.
    """
    normalized = f"{title.strip().lower()}|{(content or '')[:2000].strip()}|{agent_name.strip().lower()}"
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:32]


# ── Session 1088: Quality gate — prevent noise deliverables ───────────

# Minimum content length for a deliverable to be worth persisting.
# Media agents (image/video/audio) produce short stubs like "Generated 1 image(s)"
# — those aren't useful deliverables. Smoke tests produce <200 char outputs.
MIN_CONTENT_LENGTH = 300

# Patterns that indicate the deliverable is a smoke test or diagnostic,
# not real user-requested work. Checked against lowercased title.
SMOKE_TEST_PATTERNS = [
    'smoke test', 'smoke-test', 'sanity check', 'heartbeat',
    'factory smoke', 'round 40', 'round 45', 'round 51',
    'pr1887', 'pr #1887', 'pr1893', 'one sentence status',
    'local ops smoke', 'dual-path test', 'direct router test',
    'ping test', 'verification —',
]

# Media stub agents — their "deliverables" are just "Generated 1 image(s)"
# stubs. The actual media is stored elsewhere (Cloudinary, etc.).
MEDIA_STUB_AGENTS = {'ImageAgent', 'VideoAgent', 'AudioAgent', 'ThreeDAgent'}

# Session 1224 P1 — Deliverables Hygiene initiative d8d6c0b2-…
# Template/prompt leak: when an agent (typically ResearchAgent on a Stage 1
# initiative call) titles a deliverable with the first N chars of its prompt,
# the title becomes the literal prompt body — including the binding directive
# the prompt builder injects. Audit found 9 such deliverables in main library;
# 2 were still `ready` (un-archived) on other initiatives so the bleed was
# ongoing. Block at the factory: any title containing one of these tokens is
# rejected with reason_code=gate_4_template_leak (callers see None / typed
# exception). Tokens are matched case-insensitive on the title only — content
# can legitimately reference these in a quoted example.
TEMPLATE_LEAK_TITLE_TOKENS = (
    'binding directive',
    'research this topic to advance the initiative',
    'your output must directly advance',
    'stay narrowly focused on this initiative',
    # Session 1226 P3 — surfaced by the Rigby+Claude verifier-loop audit
    # (deliverable e2964e4a-…). New leak pattern caught in the wild: a
    # 32-row cluster, 28 created in the last 7 days, titled
    # 'Research: This topic using EXTERNAL sources (web_search, spider_query).\n
    # DO NOT use query_internal_dat' — origin is the ResearchAgent prompt
    # builder's external-sources branch at core/tasks_initiatives.py, which
    # leaks through the title=f"Research: {task[:100]}" fallback at
    # core/agents/research_agent.py:1103. The substring match below was
    # verified against the actual stored 101-char-truncated title.
    'this topic using external sources',
)

# Session 1224 P1 — Relevance gate. ResearchAgent is the canonical case: when
# its `metadata.sources_count` is 0 the synthesis is built without evidence
# and shouldn't land in main deliverables. Other agents are gated by their
# own quality_score / content gates and aren't covered here yet.
RELEVANCE_GATED_AGENTS = {'ResearchAgent'}


# Session 1229 P4 — semantic research title builder.
#
# Upstream side of the TEMPLATE_LEAK_TITLE_TOKENS reactive gate. ResearchAgent
# (and friends) used to build titles via `title=f"Research: {task[:100]}"`,
# which silently leaked the full prompt body whenever `task` was a templated
# Stage-1 prompt rather than a clean user query. Audit deliverable
# e2964e4a-… §3.1 found a 32-row cluster all sharing the same leaked title.
# The gate above blocks the resulting rows from persisting; this helper stops
# the leak at the source.
#
# Markers that signal `task` is a leaked prompt body (we should NOT use it
# verbatim as a title). Match is case-insensitive substring.
_PROMPT_BODY_MARKERS = (
    'BINDING DIRECTIVE',
    '## Research Topic',
    '## Background Context',
    '## Required Output',
    '## Instructions',
    'EXTERNAL sources',
    'DO NOT use query_internal',
    'Research this topic to advance',
    'Research this topic using EXTERNAL',
)

# Capture the value of the `## Research Topic` section in a prompt body. The
# value runs until the next H2 (`\n##`) or end of string. Case-insensitive.
_RESEARCH_TOPIC_SECTION = re.compile(
    r'##\s*Research\s+Topic\s*\n(.+?)(?=\n##|\Z)',
    re.IGNORECASE | re.DOTALL,
)

# Strip the `[User Context: ...]` tail that research_agent.py:780 appends to
# `task` when user-context augmentation kicks in. We don't want that leaking
# into titles either.
_USER_CONTEXT_TAIL = re.compile(
    r'\s*\[User Context:.*?\]\s*$',
    re.DOTALL,
)


def _normalize_whitespace(s: str) -> str:
    """Collapse all whitespace runs (including newlines) into single spaces."""
    return re.sub(r'\s+', ' ', s).strip()


def _truncate_at_word(s: str, max_chars: int) -> str:
    """Truncate `s` to <= max_chars, breaking at the last word boundary.

    Falls back to a hard cut if there is no whitespace in the last 20 chars.
    Trailing punctuation is stripped to keep titles clean.
    """
    if len(s) <= max_chars:
        return s.rstrip(' ,;:.')
    cut = s[:max_chars]
    last_space = cut.rfind(' ')
    if last_space > max_chars - 20:
        cut = cut[:last_space]
    return cut.rstrip(' ,;:.')


def _looks_like_prompt_body(s: str) -> bool:
    """True if `s` contains any marker that identifies it as a prompt body."""
    s_lower = s.lower()
    return any(marker.lower() in s_lower for marker in _PROMPT_BODY_MARKERS)


def build_semantic_research_title(
    task: str,
    *,
    prefix: str = 'Research',
    topics_detected: Optional[Iterable[str]] = None,
    max_topic_chars: int = 80,
    today: Optional[date] = None,
) -> str:
    """Build a semantic title for a research deliverable.

    Robust to ``task`` being either a clean user query OR a leaked prompt
    body (from `tasks_initiatives.py` Stage 1 dispatch or similar).

    Resolution order:
      1. Extract the value of ``## Research Topic`` if `task` is a prompt
         body that includes it.
      2. Else if `task` does NOT look like a prompt body, use it directly.
      3. Else fall back to ``topics_detected[:3]`` joined with ``·``.
      4. Else default to ``"brief"``.

    Always strips the ``[User Context: ...]`` tail, normalizes whitespace,
    truncates at a word boundary at ``max_topic_chars``, and appends a
    ``— YYYY-MM-DD`` suffix for cross-day uniqueness (the audit surfaced
    32 rows with identical titles; the suffix bounds duplication to one
    per day per topic).

    The ``prefix`` argument lets `CustomerResearchAgent` reuse this helper
    with ``prefix='Customer Research'``.

    Examples::

        >>> build_semantic_research_title("What does HFT mean?", today=date(2026, 6, 24))
        'Research: What does HFT mean? — 2026-06-24'

        >>> build_semantic_research_title(
        ...     "Research this topic using EXTERNAL sources ...\\n## Research Topic\\nDecentralized HFT\\n\\n## Background Context\\n...",
        ...     today=date(2026, 6, 24),
        ... )
        'Research: Decentralized HFT — 2026-06-24'
    """
    task = (task or '').strip()
    task = _USER_CONTEXT_TAIL.sub('', task).strip()
    topics_list = [t for t in (topics_detected or []) if t]
    today = today or date.today()
    date_suffix = today.strftime('%Y-%m-%d')

    # 1) Try the explicit `## Research Topic` section.
    topic_text = ''
    section_match = _RESEARCH_TOPIC_SECTION.search(task)
    if section_match:
        topic_text = _normalize_whitespace(section_match.group(1))

    # 2) Use `task` directly if it doesn't look like a prompt body.
    if not topic_text and task and not _looks_like_prompt_body(task):
        topic_text = _normalize_whitespace(task)

    # 3) Topics fallback.
    if not topic_text and topics_list:
        topic_text = ' · '.join(str(t) for t in topics_list[:3])

    # 4) Final default — keep short so it doesn't read as a leaked template.
    if not topic_text:
        topic_text = 'brief'

    topic_text = _truncate_at_word(topic_text, max_topic_chars)

    return f'{prefix}: {topic_text} — {date_suffix}'


# Session 1226 P1 — agent_name write-time canonicalization. Audit deliverable
# e2964e4a-… §4.4 P1 'Enforcement' bullet. The companion migration 0365 cleans
# up history; this map prevents new variants from being introduced at write
# time. Keep this map in lockstep with `_ALIAS_MAP` in
# core/migrations/0365_session_1226_agent_name_canonicalization.py — if you
# add a row to one, add it to the other.
#
# Canonical reasoning anchored in audit §1c:
#   - 'Rigby' wins (101/102 existing rows already use it)
#   - 'claude-code' wins (matches autonomous engineer source field, Procfile
#     worker name, feedback-memory file naming)
_AGENT_NAME_ALIASES = {
    'rigby': 'Rigby',
    'ClaudeCode': 'claude-code',
}


def _canonicalize_agent_name(agent_name: Optional[str]) -> str:
    """Return the canonical spelling for `agent_name`, or the input unchanged.

    Empty/None inputs return ''. Unknown values pass through unchanged so the
    map stays a strict alias surface, not an opinion engine.
    """
    if not agent_name:
        return ''
    return _AGENT_NAME_ALIASES.get(agent_name, agent_name)


def _should_create_deliverable(
    title: str,
    content: str,
    agent_name: str,
    metadata: Optional[dict] = None,
) -> tuple[bool, str, str]:
    """
    Quality gate: decide whether this deliverable is worth persisting.

    Returns ``(should_create, reason, reason_code)``. If
    ``should_create`` is False, the factory logs the skip and either
    returns None (legacy contract) or raises
    ``DeliverableGatedError`` (Session 1169 opt-in via
    ``raise_on_gated=True``). The ``reason_code`` is machine-parseable:
    ``gate_1_media_stub`` / ``gate_2_smoke_pattern`` /
    ``gate_3_min_length`` / ``passed``.
    """
    content_len = len(content or '')
    title_lower = (title or '').lower()

    # Gate 1: Media stubs — tiny content from media agents
    if agent_name in MEDIA_STUB_AGENTS and content_len < MIN_CONTENT_LENGTH:
        return False, f"media stub ({content_len} chars from {agent_name})", "gate_1_media_stub"

    # Gate 2: Smoke tests — diagnostic titles that shouldn't persist
    if any(pattern in title_lower for pattern in SMOKE_TEST_PATTERNS):
        return False, f"smoke test pattern in title", "gate_2_smoke_pattern"

    # Gate 3: Minimum content length (skip for user-triggered work)
    trigger = (metadata or {}).get('trigger_source', '')
    if trigger not in ('user_request', 'pa_tool', 'user_chat', 'direct'):
        if content_len < MIN_CONTENT_LENGTH:
            return False, f"below minimum content length ({content_len} < {MIN_CONTENT_LENGTH})", "gate_3_min_length"

    # Gate 4: Template/prompt leak in title (Session 1224 P1)
    if any(token in title_lower for token in TEMPLATE_LEAK_TITLE_TOKENS):
        matched = next(t for t in TEMPLATE_LEAK_TITLE_TOKENS if t in title_lower)
        return (
            False,
            f"template-leak title (matched token: {matched!r})",
            "gate_4_template_leak",
        )

    # Gate 5: Relevance check — sources-count gate for ResearchAgent
    if agent_name in RELEVANCE_GATED_AGENTS:
        sources_count = (metadata or {}).get('sources_count')
        if sources_count is not None and int(sources_count) <= 0:
            return (
                False,
                f"no relevant sources ({agent_name} produced 0-source synthesis)",
                "gate_5_no_relevance",
            )

    return True, "passed", "passed"


# ── Session 1088: BLOCKED content detection ───────────────────────────

def _detect_blocked_content(content: str) -> Optional[str]:
    """
    Detect if agent output contains BLOCKED warnings indicating
    incomplete work due to missing evidence/data.

    Returns the blocked reason string if found, None if content is clean.

    Session 1206 (Finding B3): the pre-fix regex
    ``BLOCKED\\s*(?:ON)?[:\\s]*(.{10,150})`` (case-insensitive) matched
    the literal word "BLOCKED" anywhere in prose, including legitimate
    classification rubrics like "READY / WORKS-BUT-NEEDS-DATA / BROKEN /
    NOT-ROUTABLE / REROUTED / BLOCKED, producing a practical readiness
    map..." — which is normal text using BLOCKED as one of several
    enum values, NOT a blocker marker. ContentWriterAgent's wakeup-week
    document was rejected on this false positive.

    Strict markers (one must be present for the gate to fire):
      - ``**BLOCKED ON:**`` / ``**BLOCKED**`` (markdown bold preamble)
      - ``[BLOCKED]`` / ``[BLOCKED: reason]`` (bracketed tag)
      - Line-anchored ``BLOCKED ON: reason`` (start of a line, mandatory ``ON:``)
      - Line-anchored ``BLOCKED:`` (start of a line, mandatory colon)

    Inline mentions like ``...or BLOCKED, producing...`` no longer fire.
    """
    import re
    if not content:
        return None

    # Strict patterns — each must be a structural blocker marker, not
    # inline prose. Capture group 1 (or 2 for line-anchored) is the
    # human-readable reason.
    patterns = [
        # **BLOCKED ON:** reason  or  **BLOCKED:** reason  or  **BLOCKED** reason
        r'\*\*BLOCKED(?:\s+ON)?[:\s]\*\*\s*([^\n\*]{5,200})',
        # [BLOCKED: reason]  or  [BLOCKED] reason
        r'\[BLOCKED(?::\s*([^\]\n]{5,200}))?\](?:\s*([^\n]{5,200}))?',
        # Line-anchored: ^BLOCKED ON: reason   (multiline mode)
        r'(?m)^BLOCKED\s+ON[:\s]+([^\n]{5,200})',
        # Line-anchored: ^BLOCKED: reason
        r'(?m)^BLOCKED[:\s]+([^\n]{5,200})',
    ]

    for pattern in patterns:
        match = re.search(pattern, content)  # case-SENSITIVE — markers are uppercase
        if match:
            # Pick the first non-None capture group as the reason.
            groups = [g for g in match.groups() if g]
            return groups[0].strip() if groups else 'blocker marker present'

    return None


def _clean_deliverable_title(title: str, agent_name: str, content: str) -> str:
    """
    Generate a human-readable title from raw prompt text.

    Fixes multiple issues:
    1. Double-prefixing: "Research: Research current trends..." → "Research: current trends..."
    2. Raw prompts as titles: "Summarize this insight into 3 concrete next-steps..."
    3. Instruction leakage: "Do NOT do web research or tool calls..."
    4. Overly long titles
    """
    import re

    if not title:
        return f"{agent_name} Output"

    # Map of agent type prefixes used by _save_to_deliverable across agents.
    # Each agent does title=f"Prefix: {task[:80]}" — and when the task text
    # already starts with a similar word, you get "Research: Research..."
    AGENT_PREFIXES = [
        'Research: ', 'Trend Analysis: ', 'Thinking Analysis: ',
        'Competitor Analysis: ', 'Contrarian Analysis: ',
        'Creative Direction: ', 'CTO Analysis: ', 'COO Analysis: ',
        'Brand Strategy: ', 'Performance Analysis: ',
        'Market Intelligence: ', 'System Intelligence Report: ',
        'Topic Mining: ', 'blog_post: ', 'Generated Audio: ',
        'Generated Images: ', 'Generated Video: ', 'Generated Code: ',
        'Code Review: ', 'SEO Optimization: ', 'Full-Stack: ',
        'Brand Identity: ', 'Meeting Coordination: ',
        'Sharp Action: ', 'Social Media Strategy: ',
        'Debate Advocacy: ', 'Debate Skepticism: ',
        'Podcast Moderation: ', 'Market Movement: ',
        'Whale Watch: ', 'Customer Research: ',
    ]

    clean = title

    # Step 1: Strip the agent type prefix
    stripped_prefix = None
    for prefix in AGENT_PREFIXES:
        if clean.startswith(prefix):
            stripped_prefix = prefix.rstrip(': ')
            clean = clean[len(prefix):]
            break

    # Step 2: Strip duplicate verb prefixes from remaining text.
    # After stripping "Research: ", if clean starts with "Research current..."
    # or "Analyze competitor...", strip the redundant verb.
    verb_prefixes = [
        'Research ', 'Analyze ', 'Summarize ', 'Compile ', 'Extract ',
        'Pull ', 'Collect ', 'Scan ', 'Audit ', 'Run the ', 'Use the ',
        'Produce ', 'Identify ', 'Lead ', 'Investigate ',
        'This insight into ', 'This insight ',
    ]
    for vp in verb_prefixes:
        if clean.startswith(vp):
            clean = clean[len(vp):]
            break

    # Step 3: Strip instruction fragments that leak into titles
    instruction_patterns = [
        r'\s*\(one sentence each\)\.?',
        r'\s*Do NOT do web research.*$',
        r'\s*Do NOT do research.*$',
        r'\s*— just synthesize\.?.*$',
        r'\s*Focus on trends and audience.*$',
        r'\s*for a general audience.*$',
        r'\s*Use workspace \w[\w-]*',
    ]
    for pattern in instruction_patterns:
        clean = re.sub(pattern, '', clean, flags=re.IGNORECASE)

    # Step 4: If there's an "Insight: X" embedded, extract it as the topic
    # Check both title and content (insight data may be in either)
    insight_match = re.search(r'Insight:\s*(.{10,80}?)(?:\n|Detail:|$)', title)
    if not insight_match and content:
        insight_match = re.search(r'Insight:\s*(.{10,80}?)(?:\n|Detail:|$)', content)
    if insight_match:
        clean = insight_match.group(1).strip()

    # Step 5: Strip "about" preambles
    about_match = re.match(r'^(?:about\s+)"?(.+)"?$', clean, re.IGNORECASE)
    if about_match:
        clean = about_match.group(1).strip()

    # Step 6: If still empty or very short after cleanup, try content heading
    if len(clean.strip()) < 10 and content:
        heading_match = re.search(r'^##?\s+(.{10,80})$', content, re.MULTILINE)
        if heading_match:
            heading = heading_match.group(1).strip()
            if 'executive summary' not in heading.lower():
                clean = heading

    # Step 7: Capitalize first letter, truncate
    clean = clean.strip()
    if clean and clean[0].islower():
        clean = clean[0].upper() + clean[1:]
    if len(clean) > 100:
        clean = clean[:97] + '...'

    # Reconstruct with prefix — but NEVER double-prefix.
    # If clean already starts with an agent name or prefix, don't add another.
    display_prefix = stripped_prefix or agent_name
    if clean:
        # Idempotency: if clean already starts with the prefix, skip
        if clean.startswith(f"{display_prefix}:") or clean.startswith(f"{agent_name}:"):
            return clean[:120]
        return f"{display_prefix}: {clean}"[:120]
    return f"{agent_name} Output"


# =============================================================================
# Session 1095: publish_intent resolver
# =============================================================================
#
# Rigby's Session 1094 architectural guidance: default `publish_intent` to
# `internal_only` via the central creation helper, then override on the
# specific pipelines that truly publish. Defaulting here (not per-agent)
# means we have ONE place to tune as the platform learns which agents are
# user-facing vs internal.
#
# When an agent is added that publishes, add its name here. When uncertain,
# leave it out (default internal_only is safe).

_PUBLISH_INTENT_BY_AGENT = {
    # Initiative pipeline: the only agent that actually publishes today
    # (10 document-type deliverables all-time per Session 1094 investigation)
    'InitiativePipeline': 'publish_candidate',
    # Content pipeline: produces publish candidates that land as SelfBlog
    # or publish-candidate Deliverables. Gates still apply before publish.
    'ContentWriterAgent': 'publish_candidate',
    'BlogWriterAgent': 'publish_candidate',
    # Editor outputs are meant for publish. Not yet observed in publish
    # path on this platform, but the intent is clear from the name.
    'EditorAgent': 'publish_candidate',
}


def resolve_publish_intent(agent_name: str, explicit: Optional[str] = None) -> str:
    """Return the `publish_intent` value for a new Deliverable.

    Precedence:
      1. Explicit caller override (agent passed publish_intent=X)
      2. Per-agent lookup (known-publishing agents)
      3. Default: 'internal_only' (safest — most agent output is internal)
    """
    if explicit:
        return explicit
    return _PUBLISH_INTENT_BY_AGENT.get(agent_name or '', 'internal_only')


# =============================================================================
# Session 1184: Provenance receipt synthesis
# =============================================================================
#
# Deliverables created directly by Rigby/PA via deliverable_tool.create do not
# arrive with an AgentExecution context — the PA tool dispatcher executes the
# handler, not the agent_router. To honor the provenance contract ("every
# deliverable has an origin execution id"), the factory synthesizes a
# lightweight AgentExecution row marked status='completed' and attaches it via
# the Session 843 parent_object_type/parent_object_id fields.
#
# Synthesis is bounded to trigger sources we KNOW are direct (pa_tool,
# user_request, user_chat, direct) plus the PA_IDENTITY agent string. Other
# missing-parent cases (scheduled tasks, agent dispatch that forgot to pass
# parent_execution_id) get a WARN log with the caller info so we can sweep
# incrementally — see Q4 in pa-f4644aa2fd1b for the soft-enforce rationale.

_PA_DIRECT_TRIGGERS = {'pa_tool', 'user_request', 'user_chat', 'direct'}


# Session 1184 PR-B: walk the stack to find the FUNCTION that decided to
# write a deliverable, skipping helper plumbing (factory + base_agent path).
# Rigby's PR-A guardrail — gives PR-B sweep work a fast triage signal so we
# don't have to grep blindly for callers.
_CALLER_SKIP_FILES = (
    'core/services/deliverable_factory.py',
    'core/agents/base_agent.py',
    'core/services/deliverable_append_service.py',
)


def _resolve_caller_fingerprint() -> str:
    """Return ``<short_filename>:<lineno>:<funcname>`` for the first stack
    frame outside the deliverable plumbing. Returns ``'unknown'`` if it
    can't walk the stack (e.g. in odd async contexts)."""
    try:
        import sys
        frame = sys._getframe(1)
        while frame is not None:
            fname = frame.f_code.co_filename
            if not any(skip in fname for skip in _CALLER_SKIP_FILES):
                # Trim absolute path to project-relative for readable logs
                short = fname.rsplit('/unified-donkey-betz/', 1)[-1]
                return f"{short}:{frame.f_lineno}:{frame.f_code.co_name}"
            frame = frame.f_back
        return 'unknown'
    except Exception:
        return 'unknown'


def _is_pa_direct_context(agent_name: str, trigger_source: str) -> bool:
    """True when this create looks like a PA/user-initiated direct tool call."""
    from core.services.pa_identity import PA_IDENTITY
    if agent_name == PA_IDENTITY:
        return True
    return trigger_source in _PA_DIRECT_TRIGGERS


def _synthesize_pa_execution_receipt(
    agent_name: str,
    task_summary: str,
    trace_id: Optional[str],
    user,
    workspace_id: Optional[str],
    metadata: Optional[dict] = None,
) -> Optional[str]:
    """Create a lightweight AgentExecution row marking the PA/tool-direct
    creation of a Deliverable. Returns the new execution id as a string, or
    None if synthesis failed (the create proceeds without a parent link and a
    WARN is logged at the caller).

    Reuses the live AgentExecution table in core.models_unified_system (the
    one agent_router writes to). status='completed' from creation — this row
    represents a synchronous tool-call receipt, not an in-flight dispatch.
    """
    try:
        from django.utils import timezone
        from core.models_unified_system import Agent, AgentExecution

        agent_record, _created = Agent.objects.get_or_create(
            name=agent_name,
            defaults={
                'agent_type': 'tool_direct',
                'description': f'{agent_name} - direct tool-call receipts',
                'specialization': '',
                'is_active': True,
            },
        )

        normalized_trace = None
        if trace_id:
            try:
                normalized_trace = uuid.UUID(str(trace_id))
            except (ValueError, AttributeError):
                normalized_trace = None

        receipt = AgentExecution.objects.create(
            agent=agent_record,
            user=user,
            task=(task_summary or 'deliverable_tool.create')[:500],
            status='completed',
            input_data={
                'source': 'deliverable_factory.synthesized_pa_receipt',
                'trace_id': str(trace_id) if trace_id else None,
                'workspace_id': str(workspace_id) if workspace_id else None,
                'metadata': metadata or {},
            },
            output_data={'kind': 'deliverable_receipt'},
            trace_id=normalized_trace,
            owner_agent=agent_name,
            parent_object_type='deliverable_factory',
            last_heartbeat_at=timezone.now(),
            completed_at=timezone.now(),
        )
        return str(receipt.id)
    except Exception as exc:
        logger.warning(
            "[DeliverableFactory] PA receipt synthesis failed (%s: %s) — "
            "deliverable will have no parent_object_id link",
            type(exc).__name__, exc,
        )
        return None


def create_deliverable(
    title: str,
    content: str,
    agent_name: str,
    category: str = 'General',
    deliverable_type: str = 'document',
    user=None,
    workspace_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    parent_execution_id: Optional[str] = None,
    parent_object_type: str = '',
    tags: Optional[List[str]] = None,
    content_format: str = 'markdown',
    quality_score: float = 0.0,
    confidence_score: float = 0.0,
    is_saved: bool = False,
    is_pinned: bool = False,
    agent_task: str = '',
    metadata: Optional[dict] = None,
    initiative_id: Optional[str] = None,
    dream_id: Optional[str] = None,
    source_operation_id: Optional[str] = None,
    publish_intent: Optional[str] = None,  # Session 1095: explicit override
    raise_on_gated: bool = False,  # Session 1169: opt-in typed exception
    # Pass-through for any additional model fields
    **extra_fields,
) -> Any:
    """
    Create a Deliverable with consistent metadata and workspace assignment.

    This is the ONLY function that should create Deliverables going forward.
    All 23+ existing creation paths should migrate to this factory.

    Returns the created Deliverable instance, or ``None`` when the
    quality gate rejects (default behavior — legacy contract).

    Session 1169 — Layer C Phase 1: callers can opt in to typed
    rejection via ``raise_on_gated=True``. When set, gate rejection
    raises ``DeliverableGatedError`` carrying ``reason``, ``reason_code``,
    ``title``, and ``agent_name``. Default stays ``False`` so the 27
    existing production caller sites keep working unchanged. Phase 2
    migrates remaining callers in batches; Phase 3 (later) flips the
    default and removes the None return path.
    """
    from core.models_deliverables import Deliverable

    # --- Session 1226 P1: agent_name write-time canonicalization ---
    # Apply alias map BEFORE any other logic so all downstream calls (gate
    # checks, telemetry, dedupe, persistence) see the canonical name. Without
    # this, migration 0365's one-time cleanup gradually re-fragments as new
    # writes come in. If `_canonicalize_agent_name` rewrote the input, log
    # the swap once at INFO level so ops can see if any callers are still
    # passing the deprecated spellings.
    _raw_agent_name = agent_name
    agent_name = _canonicalize_agent_name(agent_name)
    if _raw_agent_name and _raw_agent_name != agent_name:
        logger.info(
            "[DeliverableFactory] agent_name canonicalized at write: "
            "%r → %r (caller can update to use canonical spelling)",
            _raw_agent_name, agent_name,
        )

    # --- Session 1200: factory-entry instrumentation ---
    # Single structured line emitted before any gating so the inference
    # accuracy watch can count (A) total calls, (B) eligible-for-inference
    # subset where initiative_id is None at entry, and (C) the existing
    # [INFERENCE-MATCH] emits below. Without this line, (B) is only
    # observable as the noisy "unlinked at rest" DB proxy because
    # inference may write the initiative_id before persistence.
    try:
        from core.services.tool_context import get_current_tool_context
        _tc = get_current_tool_context() or {}
        _tc_init = bool(_tc.get('initiative_id'))
    except Exception:
        _tc_init = False
    logger.info(
        "[DELIVERABLE-FACTORY-ENTRY] agent=%s workspace=%s "
        "initiative_id_present=%s tool_context_initiative_id_present=%s "
        "initiative_source=%s has_provenance=%s",
        agent_name, workspace_id,
        bool(initiative_id), _tc_init,
        'explicit_kwarg' if initiative_id else 'none',
        bool(parent_execution_id),
    )

    # --- Session 1088: Quality gate — reject noise before any DB work ---
    should_create, gate_reason, gate_reason_code = _should_create_deliverable(
        title=title, content=content, agent_name=agent_name, metadata=metadata,
    )
    if not should_create:
        logger.info(
            "[DeliverableFactory] GATE REJECT: %s — %s (title=%s)",
            agent_name, gate_reason, title[:60],
        )
        if raise_on_gated:
            raise DeliverableGatedError(
                reason=gate_reason,
                reason_code=gate_reason_code,
                title=title,
                agent_name=agent_name,
            )
        return None

    # --- Session 1206 (Finding B2): workspace_id existence validation ---
    # When an upstream caller (PA tool, dispatcher) passes a workspace_id
    # that doesn't actually exist in ProjectWorkspace, the deliverable
    # INSERT later fails on the FK constraint
    # `core_deliverables_workspace_id_4fb358f6_fk_core_proj`, which kills
    # the entire save and orphans the agent's work.
    #
    # Observed Session 1206 (Rigby's Wakeup Week): ContentWriterAgent
    # ran successfully and produced a 4KB document, but the deliverable
    # save died because workspace_id=`b4503364-9323-4e3e-b600-b7a5aa85fa5d`
    # (suffix-different from real DBZ `b4503364-2573-4401-9e28-61a739e0ce50`)
    # didn't exist. Likely an LLM-hallucinated UUID where the dispatcher
    # matched the prefix and corrupted the suffix.
    #
    # Defensive fix: validate workspace_id BEFORE any DB writes. If it
    # doesn't resolve, emit a structured WARN with audit fields and
    # treat as if workspace_id wasn't passed — existing fallback machinery
    # at line ~648 (`_get_active_workspace_id` → `Unassigned` bucket) takes
    # over so the deliverable still lands somewhere triage-able instead of
    # being lost. Fail-OPEN: an unrelated DB hiccup on the validation
    # query never blocks a real deliverable save.
    if workspace_id:
        try:
            from core.models_skin_layer import ProjectWorkspace
            workspace_exists = ProjectWorkspace.objects.filter(
                id=workspace_id,
            ).exists()
            if not workspace_exists:
                logger.warning(
                    "[DeliverableFactory] workspace_id_invalid=true "
                    "agent=%s workspace_id_received=%s "
                    "workspace_id_fallback_used=auto_resolve "
                    "title=%r — upstream caller passed a workspace_id that "
                    "does not exist in ProjectWorkspace. Likely an LLM-"
                    "hallucinated UUID (Session 1206 Finding B2). Falling "
                    "back to caller's user.active_workspace or Unassigned "
                    "bucket so the artifact isn't lost.",
                    agent_name, workspace_id, title[:80],
                )
                workspace_id = None
        except Exception as _ws_validation_exc:
            # Fail-OPEN: never block a real save on a validation hiccup.
            logger.debug(
                "[DeliverableFactory] workspace_id validation query failed "
                "(%s) — proceeding with caller's workspace_id=%s",
                _ws_validation_exc, workspace_id,
            )

    # --- Provenance dedupe guard ---
    # If a parent_execution_id is provided, check for existing deliverable
    # from the same execution to prevent duplicates from retries/replays.
    if parent_execution_id:
        existing = Deliverable.objects.filter(
            parent_object_type=parent_object_type or 'agent_execution',
            parent_object_id=parent_execution_id,
        ).first()
        if existing:
            logger.info(
                f"[DeliverableFactory] Dedupe: returning existing {existing.id} "
                f"for execution {parent_execution_id}"
            )
            # Update content if newer (idempotent upsert)
            if content and content != existing.content:
                existing.content = content
                existing.preview_content = content[:500]
                existing.quality_score = quality_score or existing.quality_score
                existing.confidence_score = confidence_score or existing.confidence_score
                existing.save(update_fields=[
                    'content', 'preview_content', 'quality_score',
                    'confidence_score', 'updated_at',
                ])
                logger.info(f"[DeliverableFactory] Updated content for {existing.id}")
            return existing

    # --- Title-based dedupe (4h window) ---
    # Same agent + same title within 4 hours = update instead of duplicate
    from django.utils import timezone as tz
    from datetime import timedelta
    dedup_window = tz.now() - timedelta(hours=4)
    title_existing = Deliverable.objects.filter(
        title=title[:500],
        agent_name=agent_name,
        created_at__gte=dedup_window,
    ).order_by('-created_at').first()
    if title_existing:
        title_existing.content = content or title_existing.content
        title_existing.preview_content = (content[:500] if content else '')
        title_existing.quality_score = quality_score or title_existing.quality_score
        title_existing.confidence_score = confidence_score or title_existing.confidence_score
        title_existing.metadata = metadata or title_existing.metadata
        title_existing.save(update_fields=[
            'content', 'preview_content', 'quality_score',
            'confidence_score', 'metadata', 'updated_at',
        ])
        logger.info(
            f"[DeliverableFactory] Title dedupe: updated {title_existing.id} "
            f"'{title[:60]}' by {agent_name}"
        )
        return title_existing

    # --- Content-hash dedupe (72h window) ---
    # Catches duplicates that slip past title-based dedupe (e.g., recurring
    # scheduled tasks producing identical content across runs > 4h apart).
    if content and len(content) > 50:  # Skip trivially short content
        c_hash = _content_hash(title, content, agent_name)
        hash_window = tz.now() - timedelta(hours=72)
        hash_existing = Deliverable.objects.filter(
            content_hash=c_hash,
            created_at__gte=hash_window,
        ).order_by('-created_at').first()
        if hash_existing:
            logger.info(
                f"[DeliverableFactory] Content-hash dedupe: returning existing "
                f"{hash_existing.id} '{title[:60]}' (hash={c_hash[:12]})"
            )
            return hash_existing

    # Auto-assign user if not provided (agent/Celery context)
    if not user:
        user = _get_default_user()

    # Auto-assign workspace if not provided — filters by allow_autonomous_writes
    # so autonomous/scheduled agents never silently inherit a personal/game
    # workspace just because the user marked it is_active in the UI.
    explicit_workspace = bool(workspace_id)
    if not workspace_id and user:
        workspace_id = _get_active_workspace_id(user)

    if not explicit_workspace and not workspace_id:
        # Session 1091 — fall back to a sentinel "Unassigned" workspace so the
        # orphan rate is zero by construction. Previously the factory just
        # logged a warning and created a deliverable with workspace=NULL,
        # which then disappeared from every workspace-scoped UI view. The
        # Unassigned bucket is auto-created on first use, marked
        # allow_autonomous_writes=True (so it qualifies for future
        # _get_active_workspace_id lookups too), and serves as a triage pile
        # for callers that didn't pass workspace_id explicitly.
        workspace_id = _get_or_create_unassigned_workspace_id(user)
        if workspace_id:
            logger.warning(
                "[DeliverableFactory] No eligible autonomous workspace for "
                "agent=%s title=%r — routing to Unassigned bucket (%s) for "
                "triage. Caller should pass workspace_id explicitly.",
                agent_name, title[:80], workspace_id,
            )
        else:
            logger.error(
                "[DeliverableFactory] No eligible autonomous workspace for "
                "agent=%s title=%r AND Unassigned-bucket fallback failed; "
                "deliverable will be orphaned. This should not happen — "
                "check ProjectWorkspace creation permissions.",
                agent_name, title[:80],
            )

    # --- Session 1088: Auto-tag trigger_source in metadata ---
    metadata = metadata or {}
    if 'trigger_source' not in metadata:
        # Infer trigger_source from available context
        task_lower = (agent_task or '').lower()
        if any(p in task_lower for p in SMOKE_TEST_PATTERNS):
            metadata['trigger_source'] = 'smoke_test'
        elif agent_name == 'PersonalAssistant':
            metadata['trigger_source'] = 'user_request'
        elif parent_execution_id:
            metadata['trigger_source'] = 'agent_execution'
        else:
            metadata['trigger_source'] = 'beat_task'

    # --- Session 1184: Provenance receipt for direct PA/tool creates ---
    # If no parent_execution_id was passed AND this looks like a PA/user-direct
    # tool call, synthesize an AgentExecution receipt so the deliverable still
    # carries a queryable origin id (Q4: soft-enforce, Q2: synthesize). For
    # autonomous agent-dispatch paths that *should* pass parent_execution_id
    # but don't, we WARN instead — sweep is incremental, not blast-radius.
    if not parent_execution_id:
        if _is_pa_direct_context(agent_name, metadata.get('trigger_source', '')):
            parent_execution_id = _synthesize_pa_execution_receipt(
                agent_name=agent_name,
                task_summary=agent_task or title or 'deliverable_tool.create',
                trace_id=trace_id,
                user=user,
                workspace_id=workspace_id,
                metadata=metadata,
            )
            if parent_execution_id:
                parent_object_type = parent_object_type or 'agent_execution'
                metadata['origin_execution_synthesized'] = True
        else:
            # Session 1199 PR-D contract flip — replaces the Session 1184
            # PR-B soft WARN with a hard exception. PA-direct contexts
            # synthesize a receipt above and never hit this branch. Any
            # non-PA agent-dispatch path that reaches here failed to pass
            # parent_execution_id, violating the no-orphan provenance
            # contract.
            #
            # 24h WARN-volume gate (deliverable 9d9db48a) elapsed
            # 2026-06-22; local grep across all celery logs returned zero
            # WARN lines for "No parent_execution_id for agent=", so the
            # flip is safe. If this raises in production, the caller's
            # entry point needs to plumb parent_execution_id through —
            # the previous WARN-log shape would have surfaced the same
            # caller but the create was succeeding silently with no
            # provenance link.
            raise DeliverableProvenanceMissingError(
                agent_name=agent_name,
                title=title,
                trigger_source=metadata.get('trigger_source', 'unknown'),
                caller=_resolve_caller_fingerprint(),
            )

    # --- Session 1088: BLOCKED content detection ---
    blocked_reason = _detect_blocked_content(content)
    if blocked_reason:
        status = 'blocked'
        metadata['blocked_reason'] = blocked_reason
        logger.info(
            "[DeliverableFactory] BLOCKED content detected for %s: %s (title=%s)",
            agent_name, blocked_reason[:80], title[:60],
        )
    # else status comes from the caller (default 'ready')

    # --- Session 1088: Clean up prompt-as-title ---
    title = _clean_deliverable_title(title, agent_name, content)

    # Build preview
    preview = content[:500] if content else ''

    # Auto-generate slug if not provided
    if 'slug' not in extra_fields:
        from django.utils.text import slugify
        import uuid as _uuid
        base_slug = slugify(title[:100]) if title else 'untitled'
        extra_fields['slug'] = f"{base_slug}-{_uuid.uuid4().hex[:8]}"

    # --- Session 1198 — §6.2 Phase 2 inference cascade ---
    # When the caller omitted ``initiative_id``, try to deduce it from
    # the agent's affinity map BEFORE the orphan-detection path runs.
    # See ``core/services/initiative_inference.py`` for the full
    # cascade. The function is pure + read-only, so it's safe to call
    # in the hot path.
    #
    # Session 1199 — read the propagated tool_context (set at the tool
    # dispatcher entry point via ``core/services/tool_context.py``).
    # This activates §6.2 Step 2 — when the outer tool call had an
    # ``initiative_id`` in its payload, deep callers don't need to
    # plumb it through explicitly; the contextvar carries it.
    #
    # Trace emission: every inference attempt (matched or unmatched)
    # writes a structured [INFERENCE-MATCH] log line at INFO so we can
    # monitor inference accuracy independently of the deliverable
    # record itself. The trace is NOT stored on the Deliverable —
    # diagnostic_payload (Plan C scope) is for orphan diagnostics, not
    # inference observability. Keep the channels separate.
    if not initiative_id and workspace_id:
        try:
            from core.services.initiative_inference import infer_initiative_id
            from core.services.tool_context import get_current_tool_context
            inferred_id, inference_trace = infer_initiative_id(
                payload={
                    'workspace_id': workspace_id,
                    'initiative_id': initiative_id,
                },
                tool_context=get_current_tool_context(),
                owner_agent=agent_name,
            )
            if inferred_id:
                initiative_id = inferred_id
                logger.info(
                    "[INFERENCE-MATCH] agent=%s workspace=%s initiative=%s step=%s confidence=%s reason=%s",
                    agent_name, workspace_id, inferred_id,
                    inference_trace.get('step'),
                    inference_trace.get('confidence'),
                    inference_trace.get('reason'),
                )
        except Exception as _inf_exc:
            # Defensive: inference is best-effort. Never block a
            # deliverable write because the affinity table query
            # failed or the inference module raised. Fall through
            # to orphan-detection / diagnostic path.
            logger.exception(
                "[DeliverableFactory] Initiative inference failed (%s) — "
                "falling through to orphan detection.",
                _inf_exc,
            )

    # Build creation kwargs
    kwargs = {
        'title': title[:500],  # Enforce max length
        'content': content,
        'agent_name': agent_name,
        'category': category,
        'deliverable_type': deliverable_type,
        'content_format': content_format,
        'preview_content': preview,
        'quality_score': quality_score,
        'confidence_score': confidence_score,
        'is_saved': is_saved,
        'is_pinned': is_pinned,
        'agent_task': agent_task,
        'tags': tags or [],
        'metadata': metadata or {},
        # Session 1095: resolve publish_intent via explicit kwarg (if caller
        # provided one) or per-agent default table. See resolve_publish_intent.
        'publish_intent': resolve_publish_intent(agent_name, publish_intent),
    }

    # Optional foreign keys
    if user:
        kwargs['user'] = user
    if workspace_id:
        kwargs['workspace_id'] = workspace_id
    if trace_id:
        # Apr 2026: trace_id is a UUIDField on Deliverable but tool_dispatcher
        # generates non-UUID trace IDs like "tool-1-6a55c355". Validate before passing.
        import uuid as _uuid_mod
        try:
            _uuid_mod.UUID(trace_id)
            kwargs['trace_id'] = trace_id
        except (ValueError, AttributeError):
            pass  # Skip non-UUID trace IDs
    if parent_execution_id:
        kwargs['parent_object_type'] = parent_object_type or 'agent_execution'
        kwargs['parent_object_id'] = parent_execution_id
    if initiative_id:
        # Session 1098 Fix B-minimal: validate the initiative exists before
        # we record the FK. If the caller passed an id that has since been
        # deleted (or was never valid), we drop the link and log a
        # structured warning so the deliverable lands in the workspace
        # bucket instead of raising a FK error. Rigby's rollout plan
        # (conversation pa-3c7ddc058db1) called this the "fallback
        # routing" — the full target_stream_id append semantics are
        # deferred to B-full (task #9 follow-up).
        try:
            from core.models import Initiative
            if Initiative.objects.filter(id=initiative_id).exists():
                kwargs['initiative_id'] = initiative_id
            else:
                logger.warning(
                    "[DeliverableFactory] initiative_id=%s not found — "
                    "dropping link and routing to workspace bucket. "
                    "agent=%s title=%r",
                    initiative_id, agent_name, title[:60],
                )
        except Exception as _init_lookup_exc:
            # Defensive: never block a deliverable write on an
            # initiative-lookup failure. Log and drop the link.
            logger.exception(
                "[DeliverableFactory] Initiative lookup failed (%s) — "
                "dropping initiative_id=%s and continuing.",
                _init_lookup_exc, initiative_id,
            )
    if dream_id:
        kwargs['dream_id'] = dream_id
    if source_operation_id:
        kwargs['source_operation_id'] = source_operation_id

    # --- Session 1195 — Plan C Phase 1: Initiatives-First no-orphan ---
    # When this create lands without an Initiative link, or with a
    # workspace that doesn't match the Initiative's target_workspace,
    # mark the row diagnostic (label + TTL only — never reject).
    # PR #3 implements auto-clear on the update path; PR #4 implements
    # the daily sweep that flips canonical status='archived' once TTL
    # passes (sweep records reason inside diagnostic_payload — it does
    # NOT set diagnostic_status='archived', avoiding semantic collision
    # with the existing lifecycle 'archived' status). Spec:
    # docs/specs/INITIATIVES_FIRST_BACKBONE.md §3.C / §6.1.
    diag_eval = _evaluate_initiative_alignment(
        initiative_id=kwargs.get('initiative_id'),
        workspace_id=workspace_id,
    )
    diag_payload_extras: Optional[dict] = None
    if diag_eval is not None:
        diag_code, expected_ws_id = diag_eval
        ttl_hours = getattr(settings, 'DELIVERABLE_DIAGNOSTIC_TTL_HOURS', 168)
        diag_now = tz.now()
        kwargs['diagnostic_status'] = 'diagnostic'
        kwargs['diagnostic_code'] = diag_code
        kwargs['diagnostic_marked_at'] = diag_now
        kwargs['diagnostic_expires_at'] = diag_now + timedelta(hours=ttl_hours)
        diag_payload_extras = {
            'initiative_id': str(kwargs.get('initiative_id')) if kwargs.get('initiative_id') else None,
            'expected_workspace_id': str(expected_ws_id) if expected_ws_id else None,
            'actual_workspace_id': str(workspace_id) if workspace_id else None,
            'agent_name': agent_name,
            'tool': metadata.get('trigger_source', 'deliverable_factory'),
            'trace_id': trace_id,
            'caller': _resolve_caller_fingerprint(),
            'reason': diag_code.replace('_', ' '),
            'marked_at': diag_now.isoformat(),
            'ttl_hours': ttl_hours,
        }
        kwargs['diagnostic_payload'] = diag_payload_extras

    # Content hash for dedup (stored on model for future lookups)
    if content and len(content) > 50:
        kwargs['content_hash'] = _content_hash(title, content, agent_name)

    # Merge any extra fields (for backward compat with existing callers)
    kwargs.update(extra_fields)

    # Session 1088: Override status if content is BLOCKED
    if blocked_reason:
        kwargs['status'] = 'blocked'

    # Session 1098 Fix B-minimal: wrap the create in a transaction so a
    # partial write (e.g., the row lands but a post-save signal raises)
    # rolls back cleanly. Prevents half-initialized rows with the wrong
    # initiative/workspace link from lingering in the DB. Full
    # SELECT-FOR-UPDATE race protection lands in B-full (task #9
    # follow-up) once the deliverable_appends table exists.
    from django.db import transaction as _df_transaction

    try:
        with _df_transaction.atomic():
            deliverable = Deliverable.objects.create(**kwargs)
        logger.info(
            f"[DeliverableFactory] Created: {deliverable.id} "
            f"'{title[:60]}' by {agent_name} "
            f"(workspace={workspace_id or 'none'}, user={getattr(user, 'id', 'none')}, "
            f"initiative={kwargs.get('initiative_id', 'none')})"
        )
        # Session 1195 — Plan C Phase 1: emit grep-friendly diagnostic
        # log AFTER the create so we have a real deliverable_id.
        if kwargs.get('diagnostic_status') == 'diagnostic' and diag_payload_extras is not None:
            if kwargs['diagnostic_code'] == 'missing_initiative_id':
                logger.warning(
                    "[ORPHAN-DELIVERABLE] code=missing_initiative_id "
                    "deliverable_id=%s agent_name=%s tool=%s caller=%s "
                    "trace_id=%s workspace_id=%s ttl_hours=%s",
                    str(deliverable.id),
                    agent_name,
                    diag_payload_extras['tool'],
                    diag_payload_extras['caller'],
                    diag_payload_extras['trace_id'] or '-',
                    str(workspace_id) if workspace_id else 'null',
                    diag_payload_extras['ttl_hours'],
                )
            else:  # workspace_mismatch
                logger.warning(
                    "[ORPHAN-DELIVERABLE] code=workspace_mismatch "
                    "deliverable_id=%s agent_name=%s tool=%s caller=%s "
                    "trace_id=%s initiative_id=%s "
                    "expected_workspace_id=%s actual_workspace_id=%s ttl_hours=%s",
                    str(deliverable.id),
                    agent_name,
                    diag_payload_extras['tool'],
                    diag_payload_extras['caller'],
                    diag_payload_extras['trace_id'] or '-',
                    diag_payload_extras['initiative_id'] or 'null',
                    diag_payload_extras['expected_workspace_id'] or 'null',
                    diag_payload_extras['actual_workspace_id'] or 'null',
                    diag_payload_extras['ttl_hours'],
                )
        return deliverable
    except Exception as e:
        logger.error(
            f"[DeliverableFactory] Failed to create deliverable: {e} "
            f"(title='{title[:60]}', agent={agent_name})"
        )
        raise


def _get_default_user():
    """Get the default user for agent/Celery-created deliverables (first superuser)."""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.filter(is_superuser=True).order_by('date_joined').first()
    except Exception as _e:
        logger.warning(
            "deliverable_factory._get_default_user: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
        return None


UNASSIGNED_WORKSPACE_NAME = "Unassigned"


def _get_or_create_unassigned_workspace_id(user) -> Optional[str]:
    """Session 1091 — sentinel workspace bucket for orphan prevention.

    Returns the id of the per-user "Unassigned" ProjectWorkspace, creating
    it on demand. Marked ``allow_autonomous_writes=True`` so subsequent
    factory calls without an explicit workspace land here too (and surface
    in autonomous-workspace lookups). Treated as a triage pile — anything
    here is by definition something an agent created without specifying a
    home, and the right action is to reassign it to the workspace that
    matches its content.
    """
    if not user:
        return None
    try:
        from core.models_skin_layer import ProjectWorkspace
        ws, _created = ProjectWorkspace.objects.get_or_create(
            user=user,
            name=UNASSIGNED_WORKSPACE_NAME,
            defaults={
                'description': (
                    'Triage bucket for deliverables created by agents that '
                    'did not pass workspace_id. Reassign each item to the '
                    'workspace that matches its content. Auto-created by '
                    'core/services/deliverable_factory.py (Session 1091).'
                ),
                'workspace_type': 'sandbox',
                'root_path': '/tmp',
                'is_active': False,
                'allow_autonomous_writes': True,
            },
        )
        return str(ws.id)
    except Exception as _e:
        # Log full traceback so this fallback failing isn't silent — losing
        # the bucket means we'd silently orphan again, defeating the patch.
        logger.exception(
            "deliverable_factory._get_or_create_unassigned_workspace_id "
            "failed (%s: %s) — returning None and orphans will leak",
            type(_e).__name__, _e,
        )
        return None


def _evaluate_initiative_alignment(
    initiative_id: Optional[str],
    workspace_id: Optional[str],
) -> Optional[tuple]:
    """Session 1195 — Plan C Phase 1: Initiative-alignment check.

    Returns:
        ``None`` if the (initiative, workspace) pair aligns (or
        alignment cannot be evaluated — e.g., initiative has no
        target_workspace_id yet; the initiative_create write-path
        enforcement is a separate side-quest in
        ``INITIATIVES_FIRST_BACKBONE.md``).
        ``(diag_code, expected_workspace_id)`` when the pair is
        misaligned and the deliverable should be marked diagnostic.

    Never raises — alignment-check failure must never block a
    deliverable write. On unexpected error, logs and returns None
    so the create path proceeds without a diagnostic mark.
    """
    if not initiative_id:
        return ('missing_initiative_id', None)
    try:
        from core.models import Initiative
        initiative = (
            Initiative.objects
            .only('id', 'target_workspace_id')
            .filter(id=initiative_id)
            .first()
        )
        if initiative is None:
            return ('missing_initiative_id', None)
        target_ws = (
            str(initiative.target_workspace_id)
            if initiative.target_workspace_id
            else None
        )
        if target_ws is None:
            return None
        actual_ws = str(workspace_id) if workspace_id else None
        if target_ws != actual_ws:
            return ('workspace_mismatch', target_ws)
        return None
    except Exception as _e:
        logger.exception(
            "[deliverable_factory] _evaluate_initiative_alignment failed "
            "(%s: %s) — skipping diagnostic mark for initiative_id=%s",
            type(_e).__name__, _e, initiative_id,
        )
        return None


def _get_active_workspace_id(user) -> Optional[str]:
    """Get the user's active workspace ID for autonomous fallback writes.

    Only returns workspaces flagged ``allow_autonomous_writes=True`` so
    personal/game/tool workspaces (Ironwood, MentorForge, etc.) can't
    accidentally receive scheduled agent output when they happen to be
    the user's currently-active workspace. Returns None if no eligible
    workspace exists — callers must handle the None case explicitly
    rather than silently landing deliverables somewhere wrong.
    """
    try:
        from core.models_skin_layer import ProjectWorkspace
        ws = ProjectWorkspace.objects.filter(
            user=user, is_active=True, allow_autonomous_writes=True,
        ).values_list('id', flat=True).first()
        if ws:
            return str(ws)
        # Secondary fallback: any content-safe workspace owned by user
        ws = ProjectWorkspace.objects.filter(
            user=user, allow_autonomous_writes=True,
        ).values_list('id', flat=True).first()
        return str(ws) if ws else None
    except Exception as _e:
        logger.warning(
            "deliverable_factory._get_active_workspace_id: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
        return None
