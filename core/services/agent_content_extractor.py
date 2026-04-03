"""
Agent Content Extractor
========================

Universal service that extracts meaningful deliverable content from
any agent's AgentResult. Each agent stores its real output in different
places within result.data — this service knows how to find and format
it into readable markdown.

The problem: most agents return result.message as a one-liner summary
("Topic mining complete", "SEO optimization completed") while the real
work is buried in result.data['tool_results'], result.data['recommendations'],
etc. Without proper extraction, deliverables end up as useless one-liners.

Usage:
    from core.services.agent_content_extractor import extract_deliverable_content
    content = extract_deliverable_content(agent_result)
    # Returns a markdown string with the REAL agent output
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def extract_deliverable_content(result) -> str:
    """
    Extract meaningful content from an AgentResult for saving as a deliverable.

    Tries agent-specific extraction first, then generic fallbacks.
    Always returns a non-empty string (falls back to result.message).
    """
    if not result:
        return ''

    agent_name = getattr(result, 'agent_name', '') or ''
    data = getattr(result, 'data', None) or {}
    message = str(getattr(result, 'message', '')) or ''

    # Try agent-specific extractors first
    extractors = {
        'ContentWriterAgent': _extract_content_writer,
        'EditorAgent': _extract_editor,
        'ResearchAgent': _extract_research,
        'TopicMinerAgent': _extract_topic_miner,
        'TrendAnalysisAgent': _extract_trend_analysis,
        'ContrarianAgent': _extract_contrarian,
        'ContentStrategyAgent': _extract_content_strategy,
        'SEOOptimizerAgent': _extract_seo_optimizer,
        'DistributionAgent': _extract_distribution,
        'PerformanceAnalystAgent': _extract_performance_analyst,
    }

    extractor = extractors.get(agent_name)
    if extractor:
        content = extractor(data, message)
        if content and len(content) > 50:
            return content

    # Generic extraction — try common patterns
    content = _extract_generic(data, message)
    if content and len(content) > 50:
        return content

    # Last resort — return message (the one-liner summary)
    return message


# ── Agent-Specific Extractors ────────────────────────────────────────────────

def _extract_content_writer(data: dict, message: str) -> str:
    """ContentWriterAgent stores content in data['content']['full_text']."""
    content = data.get('content', {})
    if isinstance(content, dict):
        full_text = content.get('full_text', '')
        if full_text:
            return full_text
        # Try assembling from parts
        parts = []
        if content.get('title'):
            parts.append(f"# {content['title']}\n")
        if content.get('intro'):
            parts.append(content['intro'])
        for section in content.get('sections', []):
            if isinstance(section, dict):
                if section.get('heading'):
                    parts.append(f"\n## {section['heading']}\n")
                if section.get('body'):
                    parts.append(section['body'])
        if content.get('conclusion'):
            parts.append(f"\n## Conclusion\n{content['conclusion']}")
        if parts:
            return '\n'.join(parts)
    if isinstance(content, str) and len(content) > 50:
        return content
    return message


def _extract_editor(data: dict, message: str) -> str:
    """EditorAgent stores in data['enhanced_content']."""
    enhanced = data.get('enhanced_content', {})
    if isinstance(enhanced, dict):
        parts = []
        if enhanced.get('title'):
            parts.append(f"# {enhanced['title']}\n")
        if enhanced.get('intro'):
            parts.append(enhanced['intro'])
        for section in enhanced.get('sections', []):
            if isinstance(section, dict):
                if section.get('heading'):
                    parts.append(f"\n## {section['heading']}\n")
                if section.get('body'):
                    parts.append(section['body'])
        if enhanced.get('conclusion'):
            parts.append(f"\n## Conclusion\n{enhanced['conclusion']}")
        changes = data.get('changes_made', [])
        if changes:
            parts.append(f"\n---\n**Changes made:** {', '.join(str(c) for c in changes)}")
        if parts:
            return '\n'.join(parts)
    if isinstance(enhanced, str) and len(enhanced) > 50:
        return enhanced
    return message


def _extract_research(data: dict, message: str) -> str:
    """ResearchAgent stores in data['results'] + data['key_insights']."""
    parts = ["# Research Findings\n"]

    # Key insights (top 5)
    insights = data.get('key_insights', [])
    if insights:
        parts.append("## Key Insights\n")
        for i, insight in enumerate(insights, 1):
            parts.append(f"{i}. {insight}")
        parts.append("")

    # Contract info
    contract = data.get('contract', {})
    if isinstance(contract, dict) and contract.get('status'):
        parts.append(f"**Status:** {contract.get('status')} | **Confidence:** {contract.get('confidence', 'N/A')}")
        if contract.get('blocked_on'):
            parts.append(f"**Blocked on:** {contract['blocked_on']}")
        parts.append("")

    # Results (sources/findings)
    results = data.get('results', [])
    if isinstance(results, list) and results:
        parts.append("## Sources & Findings\n")
        for r in results[:10]:
            if isinstance(r, dict):
                title = r.get('title', r.get('query', 'Finding'))
                content = r.get('content', r.get('snippet', r.get('text', '')))
                url = r.get('url', r.get('source', ''))
                parts.append(f"### {title}")
                if content:
                    parts.append(str(content)[:500])
                if url:
                    parts.append(f"*Source: {url}*")
                parts.append("")
            elif isinstance(r, str):
                parts.append(f"- {r[:300]}")

    # ML analysis
    ml = data.get('ml_analysis', {})
    if isinstance(ml, dict) and ml.get('ml_insights'):
        parts.append("## AI Analysis\n")
        for insight in ml['ml_insights']:
            parts.append(f"- {insight}")

    assembled = '\n'.join(parts)
    return assembled if len(assembled) > 100 else message


def _extract_topic_miner(data: dict, message: str) -> str:
    """TopicMinerAgent stores in data['tool_results'] with trends, scores, gaps."""
    parts = ["# Topic Mining Results\n"]

    for tool_result in data.get('tool_results', []):
        if not isinstance(tool_result, dict):
            continue

        # Trends
        trends = tool_result.get('trends', [])
        if trends:
            parts.append("## Trending Topics\n")
            for t in trends[:10]:
                if isinstance(t, dict):
                    title = t.get('title', 'Untitled')
                    source = t.get('source', '')
                    preview = t.get('content_preview', '')
                    parts.append(f"- **{title}** ({source})")
                    if preview:
                        parts.append(f"  {preview}")

        # Potential scores
        if tool_result.get('topic') and tool_result.get('potential_score'):
            parts.append(f"\n## Topic Potential: {tool_result['topic']}")
            parts.append(f"- **Score:** {tool_result['potential_score']}/100")
            parts.append(f"- **Recommendation:** {tool_result.get('recommendation', 'N/A')}")

        # Gaps
        gaps = tool_result.get('top_gaps', [])
        if gaps:
            parts.append("\n## Content Gaps (Underserved Topics)\n")
            for g in gaps:
                if isinstance(g, dict):
                    parts.append(f"- **{g.get('topic', '?')}** ({g.get('mention_count', 0)} mentions)")

    assembled = '\n'.join(parts)
    return assembled if len(assembled) > 100 else message


def _extract_trend_analysis(data: dict, message: str) -> str:
    """TrendAnalysisAgent stores in data['tool_results'] + data['provenance']."""
    parts = ["# Trend Analysis\n"]

    # Provenance
    provenance = data.get('provenance', {})
    if isinstance(provenance, dict):
        parts.append(f"**Data window:** {provenance.get('data_window', 'N/A')}")
        sources = provenance.get('sources', {})
        if sources:
            parts.append(f"**Sources:** {', '.join(f'{k} ({v} records)' for k, v in sources.items() if isinstance(v, (int, float)))}")
        parts.append("")

    # Tool results
    for tr in data.get('tool_results', []):
        if isinstance(tr, dict):
            tool_name = tr.get('tool', tr.get('name', ''))
            result_data = tr.get('result', tr)
            if tool_name:
                parts.append(f"## {tool_name}\n")
            parts.append(_format_dict_as_markdown(result_data, depth=0))

    # If message has the provenance block, use it
    if message and len(message) > 200:
        return message

    assembled = '\n'.join(parts)
    return assembled if len(assembled) > 100 else message


def _extract_contrarian(data: dict, message: str) -> str:
    """ContrarianAgent stores saturation, angles, rising topics in data['tool_results']."""
    parts = ["# Contrarian Analysis\n"]

    for tool_result in data.get('tool_results', []):
        if not isinstance(tool_result, dict):
            continue

        # Saturation check
        if tool_result.get('saturation_level'):
            parts.append(f"## Topic Saturation: {tool_result.get('topic', '')}")
            parts.append(f"- **Level:** {tool_result['saturation_level']}")
            parts.append(f"- **Trend:** {tool_result.get('trend', 'N/A')}")
            parts.append(f"- **Recommendation:** {tool_result.get('recommendation', '')}")
            parts.append("")

        # Unique angles
        angles = tool_result.get('unique_angles', [])
        if angles:
            parts.append("## Suggested Unique Angles\n")
            for a in angles:
                if isinstance(a, dict):
                    parts.append(f"### {a.get('angle', 'Angle')}")
                    parts.append(f"**Reasoning:** {a.get('reasoning', '')}")
                    parts.append(f"**Differentiation:** {a.get('differentiation', '')}")
                    parts.append("")

        # Rising topics
        rising = tool_result.get('rising_topics', [])
        if rising:
            parts.append("## Rising Topics\n")
            for r in rising:
                if isinstance(r, dict):
                    parts.append(f"- **{r.get('topic', '?')}** — {r.get('growth_rate', '')} ({r.get('recent_mentions', 0)} recent mentions)")

    assembled = '\n'.join(parts)
    return assembled if len(assembled) > 100 else message


def _extract_content_strategy(data: dict, message: str) -> str:
    """ContentStrategyAgent stores in data['recommendations']."""
    parts = ["# Content Strategy\n"]

    recs = data.get('recommendations', [])
    if isinstance(recs, list):
        for i, rec in enumerate(recs, 1):
            if isinstance(rec, dict):
                title = rec.get('title', rec.get('topic', f'Recommendation {i}'))
                parts.append(f"## {i}. {title}")
                for key in ('angle', 'approach', 'description', 'rationale', 'target_audience', 'format', 'tone'):
                    if rec.get(key):
                        parts.append(f"**{key.replace('_', ' ').title()}:** {rec[key]}")
                parts.append("")
            elif isinstance(rec, str):
                parts.append(f"{i}. {rec}")

    # Tool results fallback
    if not recs:
        for tr in data.get('tool_results', []):
            if isinstance(tr, dict):
                parts.append(_format_dict_as_markdown(tr, depth=0))

    assembled = '\n'.join(parts)
    return assembled if len(assembled) > 100 else message


def _extract_seo_optimizer(data: dict, message: str) -> str:
    """SEOOptimizerAgent stores in data['tool_results'] + data['ml_analysis']."""
    parts = ["# SEO Optimization\n"]

    # Tool results
    for tr in data.get('tool_results', []):
        if isinstance(tr, dict):
            tool_name = tr.get('tool', tr.get('name', 'Analysis'))
            result_data = tr.get('result', tr)
            parts.append(f"## {tool_name}\n")
            parts.append(_format_dict_as_markdown(result_data, depth=0))

    # ML analysis
    ml = data.get('ml_analysis', {})
    if isinstance(ml, dict):
        if ml.get('ml_insights'):
            parts.append("## AI Insights\n")
            for insight in ml['ml_insights']:
                parts.append(f"- {insight}")

    assembled = '\n'.join(parts)
    return assembled if len(assembled) > 100 else message


def _extract_distribution(data: dict, message: str) -> str:
    """DistributionAgent stores in data['full_text'] or data['optimization']."""
    # DistributionAgent already produces markdown in full_text
    full_text = data.get('full_text', '')
    if full_text and len(full_text) > 50:
        return full_text
    # Fall back to message which is also markdown
    return message


def _extract_performance_analyst(data: dict, message: str) -> str:
    """PerformanceAnalystAgent stores predictions and patterns."""
    parts = ["# Performance Analysis\n"]

    predictions = data.get('performance_predictions', [])
    if predictions:
        parts.append("## Predictions\n")
        parts.append(_format_dict_as_markdown(predictions, depth=0))

    patterns = data.get('historical_patterns', [])
    if patterns:
        parts.append("## Historical Patterns\n")
        parts.append(_format_dict_as_markdown(patterns, depth=0))

    for tr in data.get('tool_results', []):
        if isinstance(tr, dict):
            parts.append(_format_dict_as_markdown(tr, depth=0))

    assembled = '\n'.join(parts)
    return assembled if len(assembled) > 100 else message


# ── Generic Extraction ───────────────────────────────────────────────────────

def _extract_generic(data: dict, message: str) -> str:
    """Generic extractor — tries common data patterns."""
    if not isinstance(data, dict):
        return message

    # Try known content keys in priority order
    for key in ('full_text', 'text', 'output', 'report', 'content',
                'enhanced_content', 'findings', 'analysis', 'response'):
        val = data.get(key)
        if isinstance(val, str) and len(val) > 50:
            return val
        if isinstance(val, dict) and val.get('full_text'):
            return val['full_text']

    # Try tool_results — many agents use this pattern
    tool_results = data.get('tool_results', [])
    if isinstance(tool_results, list) and tool_results:
        parts = []
        for tr in tool_results:
            if isinstance(tr, dict):
                parts.append(_format_dict_as_markdown(tr, depth=0))
            elif isinstance(tr, str):
                parts.append(tr)
        assembled = '\n\n'.join(parts)
        if len(assembled) > 50:
            return assembled

    # Try recommendations
    recs = data.get('recommendations', [])
    if isinstance(recs, list) and recs:
        parts = []
        for i, r in enumerate(recs, 1):
            if isinstance(r, dict):
                parts.append(f"{i}. {json.dumps(r, indent=2, default=str)}")
            else:
                parts.append(f"{i}. {r}")
        return '\n'.join(parts)

    # Try formatting the whole data dict
    if data:
        formatted = _format_dict_as_markdown(data, depth=0)
        if len(formatted) > 50:
            return formatted

    return message


# ── Helpers ──────────────────────────────────────────────────────────────────

def _format_dict_as_markdown(obj: Any, depth: int = 0) -> str:
    """Recursively format a dict/list as readable markdown."""
    if depth > 3:
        return str(obj)[:200]

    if isinstance(obj, dict):
        parts = []
        for k, v in obj.items():
            if k in ('tool', 'name', 'type', 'action'):
                continue  # Skip meta keys
            label = str(k).replace('_', ' ').title()
            if isinstance(v, (dict, list)):
                parts.append(f"**{label}:**")
                parts.append(_format_dict_as_markdown(v, depth + 1))
            elif v is not None and str(v).strip():
                parts.append(f"- **{label}:** {v}")
        return '\n'.join(parts)

    if isinstance(obj, list):
        parts = []
        for item in obj[:15]:  # Cap at 15 items
            if isinstance(item, dict):
                parts.append(_format_dict_as_markdown(item, depth + 1))
                parts.append("")
            else:
                parts.append(f"- {item}")
        return '\n'.join(parts)

    return str(obj)[:500]
