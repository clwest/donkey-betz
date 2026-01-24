"""
Context Summarizer Service
Session 806: Compresses verbose context sections into concise summaries.

This service:
1. Takes verbose context data structures
2. Extracts the most important information
3. Formats into compact summaries
4. Maintains 5-10x compression ratios

The goal is to reduce spider_intelligence from ~2,000 tokens to ~200 tokens
while preserving the key insights.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SummaryStats:
    """Statistics about a summarization operation."""
    original_chars: int
    summary_chars: int
    compression_ratio: float
    items_included: int
    items_excluded: int


class ContextSummarizer:
    """
    Session 806: Compresses verbose context into concise summaries.

    Usage:
        from core.services.context_summarizer import get_context_summarizer

        summarizer = get_context_summarizer()

        # Summarize spider intelligence
        spider_summary = summarizer.summarize_spider_context(full_spider_data)

        # Summarize learning patterns
        learning_summary = summarizer.summarize_learning_context(learning_data)
    """

    # Target token counts for each section type
    TARGET_TOKENS = {
        'spider_intelligence': 200,
        'learning_patterns': 150,
        'advisor_context': 100,
        'proactive_intelligence': 50,
        'workspace_context': 100,
        'pending_decisions': 100,
    }

    # Feature flag
    ENABLE_SUMMARIZATION = True

    def __init__(self):
        self._stats: Dict[str, SummaryStats] = {}

    def summarize_spider_context(
        self,
        spider_data: Dict[str, Any],
        max_trends: int = 5,
        max_discussions: int = 3
    ) -> str:
        """
        Summarize spider intelligence data into a compact string.

        Target: 2,000 tokens -> 200 tokens (10:1 compression)

        Args:
            spider_data: Full spider context from SpiderContextBuilder
            max_trends: Maximum trending topics to include
            max_discussions: Maximum discussions to include

        Returns:
            Compact summary string
        """
        if not spider_data or not spider_data.get('has_data'):
            return ""

        if not self.ENABLE_SUMMARIZATION:
            # Return the pre-built summary if summarization is disabled
            return spider_data.get('summary', '')

        parts = []

        # Trending topics (most important)
        trends = spider_data.get('relevant_trends', [])
        if trends:
            topic_names = [t.get('topic', '')[:30] for t in trends[:max_trends] if t.get('topic')]
            if topic_names:
                parts.append(f"Trending: {', '.join(topic_names)}")

        # Market data snapshot
        market = spider_data.get('market_data', {})
        if market:
            market_parts = []

            # Crypto summary
            crypto = market.get('crypto', [])
            if crypto:
                top_crypto = crypto[0]
                symbol = top_crypto.get('symbol', 'BTC')
                change = top_crypto.get('change_24h', 0)
                change_str = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
                market_parts.append(f"{symbol} {change_str}")

            # Stocks summary
            stocks = market.get('stocks', [])
            if stocks:
                top_stock = stocks[0]
                symbol = top_stock.get('symbol', 'SPY')
                change = top_stock.get('change', 0)
                change_str = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
                market_parts.append(f"{symbol} {change_str}")

            if market_parts:
                parts.append(f"Market: {', '.join(market_parts)}")

        # Creative trends (for creative agents)
        creative = spider_data.get('creative_trends', {})
        if creative:
            styles = creative.get('trending_styles', [])
            if styles:
                style_names = [s.get('style', '')[:20] for s in styles[:3] if s.get('style')]
                if style_names:
                    parts.append(f"Design: {', '.join(style_names)}")

        # Job market (for career-related queries)
        jobs = spider_data.get('job_data', {})
        if jobs and jobs.get('total_jobs', 0) > 0:
            parts.append(f"Jobs: {jobs['total_jobs']} listings")

        # Top discussion (just the headline)
        discussions = spider_data.get('discussions', [])
        if discussions:
            top_discussion = discussions[0]
            title = top_discussion.get('title', '')[:50]
            if title:
                parts.append(f"Hot: {title}")

        summary = " | ".join(parts) if parts else ""

        # Track stats
        original_str = str(spider_data)
        self._stats['spider_intelligence'] = SummaryStats(
            original_chars=len(original_str),
            summary_chars=len(summary),
            compression_ratio=len(original_str) / len(summary) if summary else 0,
            items_included=len(parts),
            items_excluded=(len(trends) - max_trends + len(discussions) - max_discussions)
        )

        logger.info(
            f"📝 [Session 806] Spider context summarized: "
            f"{len(original_str)} -> {len(summary)} chars "
            f"({len(original_str) // len(summary) if summary else 0}:1 compression)"
        )

        return summary

    def summarize_learning_context(
        self,
        learning_data: Dict[str, Any],
        max_patterns: int = 3
    ) -> str:
        """
        Summarize learning patterns into a compact string.

        Target: 800 tokens -> 150 tokens (5:1 compression)

        Args:
            learning_data: Full learning context from LearningPatternEngine
            max_patterns: Maximum patterns to include

        Returns:
            Compact summary string
        """
        if not learning_data or not learning_data.get('has_patterns'):
            return ""

        if not self.ENABLE_SUMMARIZATION:
            return learning_data.get('summary', '')

        parts = []

        # Effectiveness improvement
        improvement = learning_data.get('effectiveness_improvement', {})
        if improvement:
            if improvement.get('as_teacher') and improvement.get('as_student'):
                parts.append(
                    f"Effectiveness: +{improvement['as_teacher']}% teaching, "
                    f"+{improvement['as_student']}% learning"
                )
            elif improvement.get('as_teacher'):
                parts.append(f"Teaching: +{improvement['as_teacher']}% effective")
            elif improvement.get('as_student'):
                parts.append(f"Learning: +{improvement['as_student']}% improved")

        # Best collaborators
        collabs = learning_data.get('collaboration_insights', [])
        if collabs:
            # Extract just the names
            names = []
            for c in collabs[:2]:
                if 'Works well with' in c:
                    name = c.split('Works well with ')[1].split(' (')[0]
                    names.append(name)
            if names:
                parts.append(f"Best collaborators: {', '.join(names)}")

        # Success patterns
        success = learning_data.get('success_patterns', [])
        if success:
            task_types = list(set(p.get('task_type', '') for p in success[:3] if p.get('task_type')))
            if task_types:
                parts.append(f"Excels at: {', '.join(task_types[:2])}")

        # Best practices (just one)
        practices = learning_data.get('best_practices', [])
        if practices:
            parts.append(practices[0][:60])

        summary = " | ".join(parts) if parts else ""

        # Track stats
        original_str = str(learning_data)
        self._stats['learning_patterns'] = SummaryStats(
            original_chars=len(original_str),
            summary_chars=len(summary),
            compression_ratio=len(original_str) / len(summary) if summary else 0,
            items_included=len(parts),
            items_excluded=len(success) + len(collabs) - 4
        )

        return summary

    def summarize_advisor_context(
        self,
        advisor_data: Dict[str, Any],
        max_principles: int = 2
    ) -> str:
        """
        Summarize advisor wisdom into a compact string.

        Target: 600 tokens -> 100 tokens (6:1 compression)

        Args:
            advisor_data: Full advisor context from AdvisorContextBuilder
            max_principles: Maximum principles to include

        Returns:
            Compact summary string
        """
        if not advisor_data or not advisor_data.get('has_advice'):
            return ""

        if not self.ENABLE_SUMMARIZATION:
            return advisor_data.get('summary', '')

        parts = []

        # Advisor names
        advisors = advisor_data.get('relevant_advisors', [])
        if advisors:
            names = [a.get('name', '').split(' (')[0] for a in advisors[:2] if a.get('name')]
            if names:
                parts.append(f"Advisors: {', '.join(names)}")

        # Key frameworks
        frameworks = advisor_data.get('decision_frameworks', [])
        if frameworks:
            framework_names = [f.replace('_', ' ').title() for f in frameworks[:2]]
            parts.append(f"Framework: {', '.join(framework_names)}")

        # One key principle
        principles = advisor_data.get('key_principles', [])
        if principles:
            principle = principles[0][:60]
            parts.append(f"Key: {principle}")

        # Recommended approach
        approach = advisor_data.get('recommended_approach', '')
        if approach:
            parts.append(approach[:50])

        summary = " | ".join(parts) if parts else ""

        # Track stats
        original_str = str(advisor_data)
        self._stats['advisor_context'] = SummaryStats(
            original_chars=len(original_str),
            summary_chars=len(summary),
            compression_ratio=len(original_str) / len(summary) if summary else 0,
            items_included=len(parts),
            items_excluded=len(principles) + len(frameworks) - 4
        )

        return summary

    def summarize_proactive_context(
        self,
        proactive_data: Dict[str, Any]
    ) -> str:
        """
        Summarize proactive intelligence into a compact string.

        Target: 500 tokens -> 50 tokens (10:1 compression)

        Args:
            proactive_data: Proactive intelligence data

        Returns:
            Compact summary string
        """
        if not proactive_data:
            return ""

        if not self.ENABLE_SUMMARIZATION:
            return proactive_data.get('summary', '')

        # Count by priority
        situations = proactive_data.get('situations', [])
        if not situations:
            return ""

        priority_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for situation in situations:
            priority = situation.get('priority', 'medium').lower()
            if priority in priority_counts:
                priority_counts[priority] += 1

        parts = []

        # Alert counts
        alerts = []
        if priority_counts['critical'] > 0:
            alerts.append(f"{priority_counts['critical']} critical")
        if priority_counts['high'] > 0:
            alerts.append(f"{priority_counts['high']} high")
        if alerts:
            parts.append(f"Alerts: {', '.join(alerts)}")

        # Top situation
        if situations:
            top = situations[0]
            action_type = top.get('action_type', 'action')
            title = top.get('title', '')[:30]
            if title:
                parts.append(f"Top {action_type}: {title}")

        summary = " | ".join(parts) if parts else ""

        # Track stats
        original_str = str(proactive_data)
        self._stats['proactive_intelligence'] = SummaryStats(
            original_chars=len(original_str),
            summary_chars=len(summary),
            compression_ratio=len(original_str) / len(summary) if summary else 0,
            items_included=len(parts),
            items_excluded=len(situations) - 1
        )

        return summary

    def summarize_pending_decisions(
        self,
        decisions_data: Dict[str, Any],
        max_decisions: int = 3
    ) -> str:
        """
        Summarize pending human decisions.

        Target: 300 tokens -> 100 tokens (3:1 compression)

        Args:
            decisions_data: Pending decisions data
            max_decisions: Maximum decisions to show

        Returns:
            Compact summary string
        """
        if not decisions_data:
            return ""

        pending = decisions_data.get('pending_decisions', [])
        if not pending:
            return ""

        parts = []

        # Count and types
        parts.append(f"{len(pending)} pending decisions")

        # Top decisions
        for decision in pending[:max_decisions]:
            decision_type = decision.get('type', 'decision')[:15]
            title = decision.get('title', '')[:25]
            if title:
                parts.append(f"- {decision_type}: {title}")

        return "\n".join(parts) if parts else ""

    def summarize_workspace_context(
        self,
        workspace_data: Dict[str, Any]
    ) -> str:
        """
        Summarize workspace/project context.

        Target: 400 tokens -> 100 tokens (4:1 compression)

        Args:
            workspace_data: Workspace context data

        Returns:
            Compact summary string
        """
        if not workspace_data:
            return ""

        parts = []

        # Active workspace
        workspace = workspace_data.get('active_workspace', {})
        if workspace:
            name = workspace.get('name', 'workspace')[:30]
            parts.append(f"Workspace: {name}")

        # Recent files
        files = workspace_data.get('recent_files', [])
        if files:
            file_count = len(files)
            parts.append(f"{file_count} recent files")

        # Project status
        project = workspace_data.get('project', {})
        if project:
            status = project.get('status', 'active')
            parts.append(f"Status: {status}")

        return " | ".join(parts) if parts else ""

    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get summarization statistics."""
        return {
            section: {
                'original_chars': stats.original_chars,
                'summary_chars': stats.summary_chars,
                'compression_ratio': round(stats.compression_ratio, 1),
                'items_included': stats.items_included,
                'items_excluded': stats.items_excluded,
            }
            for section, stats in self._stats.items()
        }

    def get_total_savings(self) -> Dict[str, int]:
        """Get total character savings across all sections."""
        total_original = sum(s.original_chars for s in self._stats.values())
        total_summary = sum(s.summary_chars for s in self._stats.values())
        return {
            'original_chars': total_original,
            'summary_chars': total_summary,
            'chars_saved': total_original - total_summary,
            'estimated_tokens_saved': (total_original - total_summary) // 4,
        }

    @classmethod
    def set_summarization(cls, enabled: bool) -> None:
        """Enable or disable summarization globally."""
        cls.ENABLE_SUMMARIZATION = enabled
        logger.info(f"📝 [Session 806] Summarization {'enabled' if enabled else 'disabled'}")


# Singleton instance
_context_summarizer: Optional[ContextSummarizer] = None


def get_context_summarizer() -> ContextSummarizer:
    """Get the singleton ContextSummarizer instance."""
    global _context_summarizer
    if _context_summarizer is None:
        _context_summarizer = ContextSummarizer()
    return _context_summarizer
