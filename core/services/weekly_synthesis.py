"""
Session 555 - Phase C: Weekly Synthesis Service

Generates weekly executive summaries from artifact/execution data.
Uses GPT-5-mini for trend analysis and insights.

Delivered to Discord #boardroom every Sunday at 8 AM.
"""

import json
import logging
from datetime import timedelta
from typing import Dict, Any

from django.db.models import Avg, Count
from django.utils import timezone
from openai import OpenAI

logger = logging.getLogger(__name__)


class WeeklySynthesisService:
    """
    Generates weekly executive summaries from artifact/execution data.

    Flow:
    1. Aggregate artifact data (counts by type/status, top items)
    2. Aggregate decision data (approved/rejected/deferred)
    3. Aggregate execution data (success/failure rates)
    4. Get agent activity metrics
    5. Generate AI insights via GPT-5-mini
    6. Build markdown report
    7. Create WeeklySynthesis record
    """

    def __init__(self):
        self.client = OpenAI()

    def generate_weekly_synthesis(self, days_back: int = 7) -> 'WeeklySynthesis':
        """
        Generate synthesis for the specified period.

        Args:
            days_back: Number of days to analyze (default 7)

        Returns:
            WeeklySynthesis: The generated synthesis record
        """
        from core.models_conversation_artifacts import (
            WeeklySynthesis
        )

        period_end = timezone.now().date()
        period_start = period_end - timedelta(days=days_back)

        logger.info(f"📊 Generating weekly synthesis for {period_start} to {period_end}")

        # 1. Aggregate artifact data
        artifact_stats = self._aggregate_artifacts(period_start, period_end)

        # 2. Aggregate decision data
        decision_stats = self._aggregate_decisions(period_start, period_end)

        # 3. Aggregate execution data
        execution_stats = self._aggregate_executions(period_start, period_end)

        # 4. Get agent activity
        agent_stats = self._aggregate_agent_activity(period_start, period_end)

        # 5. Generate AI insights
        insights = self._generate_insights(
            artifact_stats, decision_stats, execution_stats, agent_stats
        )

        # 6. Build markdown report
        report = self._build_report(
            period_start, period_end,
            artifact_stats, decision_stats,
            execution_stats, agent_stats, insights
        )

        # 7. Create synthesis record
        synthesis = WeeklySynthesis.objects.create(
            period_start=period_start,
            period_end=period_end,
            artifacts_extracted=artifact_stats['total'],
            artifacts_by_type=artifact_stats['by_type'],
            artifacts_by_status=artifact_stats['by_status'],
            top_artifacts=artifact_stats['top_items'],
            decisions_approved=decision_stats['approved'],
            decisions_rejected=decision_stats['rejected'],
            decisions_deferred=decision_stats['deferred'],
            executions_total=execution_stats['total'],
            executions_succeeded=execution_stats['succeeded'],
            executions_failed=execution_stats['failed'],
            execution_success_rate=execution_stats['success_rate'],
            avg_execution_time_ms=execution_stats['avg_time_ms'],
            most_active_agents=agent_stats['most_active'],
            agent_success_rates=agent_stats['success_rates'],
            trend_analysis=insights.get('trend_analysis', ''),
            key_themes=insights.get('key_themes', []),
            recommendations=insights.get('recommendations', []),
            pending_high_priority=artifact_stats['pending_high_priority'],
            oldest_pending_days=artifact_stats['oldest_pending_days'],
            report_markdown=report,
        )

        logger.info(
            f"📊 Weekly synthesis generated: {artifact_stats['total']} artifacts, "
            f"{execution_stats['total']} executions"
        )

        return synthesis

    def _aggregate_artifacts(self, start, end) -> Dict[str, Any]:
        """Aggregate artifact statistics for the period."""
        from core.models_conversation_artifacts import ExtractedArtifact

        artifacts = ExtractedArtifact.objects.filter(
            extracted_at__date__gte=start,
            extracted_at__date__lte=end
        )

        # Count by type
        by_type = {}
        for t, _ in ExtractedArtifact.ARTIFACT_TYPES:
            by_type[t] = artifacts.filter(artifact_type=t).count()

        # Count by status
        by_status = {}
        for s, _ in ExtractedArtifact.STATUS_CHOICES:
            by_status[s] = artifacts.filter(status=s).count()

        # Top artifacts by composite score
        top = artifacts.order_by('-composite_score')[:5]
        top_items = [{
            'title': a.title,
            'type': a.artifact_type,
            'score': float(a.composite_score)
        } for a in top]

        # Pending items needing attention (across all time)
        pending = ExtractedArtifact.objects.filter(status='pending')
        high_priority = pending.filter(composite_score__gte=0.7).count()
        oldest = pending.order_by('extracted_at').first()
        oldest_days = (timezone.now() - oldest.extracted_at).days if oldest else 0

        return {
            'total': artifacts.count(),
            'by_type': by_type,
            'by_status': by_status,
            'top_items': top_items,
            'pending_high_priority': high_priority,
            'oldest_pending_days': oldest_days,
        }

    def _aggregate_decisions(self, start, end) -> Dict[str, Any]:
        """Aggregate decision statistics for the period."""
        from core.models_conversation_artifacts import ExtractedArtifact

        # Decisions are artifacts with decided_at in the period
        decisions = ExtractedArtifact.objects.filter(
            decided_at__date__gte=start,
            decided_at__date__lte=end
        )

        return {
            'approved': decisions.filter(status='approved').count(),
            'rejected': decisions.filter(status='rejected').count(),
            'deferred': decisions.filter(status='deferred').count(),
            'total': decisions.count(),
        }

    def _aggregate_executions(self, start, end) -> Dict[str, Any]:
        """Aggregate execution statistics for the period."""
        from core.models_conversation_artifacts import ArtifactExecution

        executions = ArtifactExecution.objects.filter(
            queued_at__date__gte=start,
            queued_at__date__lte=end
        )

        succeeded = executions.filter(status='completed').count()
        failed = executions.filter(status='failed').count()
        total = succeeded + failed

        # Average execution time for completed executions
        avg_time = executions.filter(
            status='completed',
            execution_time_ms__isnull=False
        ).aggregate(avg=Avg('execution_time_ms'))['avg'] or 0

        return {
            'total': total,
            'succeeded': succeeded,
            'failed': failed,
            'success_rate': succeeded / total if total > 0 else 0.0,
            'avg_time_ms': int(avg_time),
        }

    def _aggregate_agent_activity(self, start, end) -> Dict[str, Any]:
        """Aggregate agent activity statistics for the period."""
        from core.models_conversation_artifacts import ArtifactExecution

        executions = ArtifactExecution.objects.filter(
            queued_at__date__gte=start,
            queued_at__date__lte=end
        )

        # Most active agents
        agent_counts = (
            executions
            .values('agent_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        most_active = [
            {'agent': item['agent_name'], 'count': item['count']}
            for item in agent_counts
        ]

        # Success rates by agent
        success_rates = {}
        for agent_data in agent_counts:
            agent_name = agent_data['agent_name']
            agent_execs = executions.filter(agent_name=agent_name)
            completed = agent_execs.filter(status='completed').count()
            total = agent_execs.exclude(status__in=['queued', 'running']).count()
            success_rates[agent_name] = completed / total if total > 0 else 0.0

        return {
            'most_active': most_active,
            'success_rates': success_rates,
        }

    def _generate_insights(
        self,
        artifacts: Dict,
        decisions: Dict,
        executions: Dict,
        agents: Dict
    ) -> Dict[str, Any]:
        """
        Use GPT-5-mini to generate trend analysis and recommendations.

        Returns dict with:
        - trend_analysis: 2-3 sentence summary
        - key_themes: List of main themes
        - recommendations: List of action items
        """
        # Format data for the prompt
        type_summary = ', '.join(
            f"{k}: {v}" for k, v in artifacts['by_type'].items() if v > 0
        )
        status_summary = ', '.join(
            f"{k}: {v}" for k, v in artifacts['by_status'].items() if v > 0
        )
        top_agents = ', '.join(
            f"{a['agent']} ({a['count']})" for a in agents['most_active'][:5]
        )

        prompt = f"""Analyze this weekly Chief of Staff report data and provide insights.

ARTIFACTS EXTRACTED: {artifacts['total']}
By Type: {type_summary or 'None'}
By Status: {status_summary or 'None'}

DECISIONS MADE:
- Approved: {decisions['approved']}
- Rejected: {decisions['rejected']}
- Deferred: {decisions['deferred']}

EXECUTIONS:
- Total: {executions['total']}
- Succeeded: {executions['succeeded']}
- Failed: {executions['failed']}
- Success Rate: {executions['success_rate']:.1%}
- Avg Time: {executions['avg_time_ms']}ms

AGENT ACTIVITY:
- Most Active: {top_agents or 'None'}
- High Priority Pending: {artifacts['pending_high_priority']}
- Oldest Pending Item: {artifacts['oldest_pending_days']} days

Provide a JSON response with:
1. "trend_analysis": A 2-3 sentence summary of the week's activity patterns
2. "key_themes": A list of 3-5 main themes or patterns observed
3. "recommendations": A list of 3-5 actionable recommendations

Focus on:
- Activity patterns and trends
- Areas needing attention
- Opportunities for improvement
- Risk indicators

If data is sparse, note that and provide general guidance."""

        try:
            # Session 876: Increased tokens for GPT-5-mini reasoning headroom
            response = self.client.chat.completions.create(
                model="gpt-5.2",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Chief of Staff AI analyzing weekly operations data. "
                            "Provide concise, actionable insights in JSON format."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=4000,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            logger.info("📊 AI insights generated successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to generate AI insights: {e}")
            # Return fallback insights
            return {
                'trend_analysis': (
                    f"This week saw {artifacts['total']} artifacts extracted with "
                    f"{executions['success_rate']:.0%} execution success rate. "
                    "Review the data for detailed patterns."
                ),
                'key_themes': [
                    'Activity tracking in progress',
                    'Execution pipeline operational',
                    'Decision queue active'
                ],
                'recommendations': [
                    f"Review {artifacts['pending_high_priority']} high-priority pending items",
                    "Monitor execution success rates",
                    "Ensure timely decision-making on pending artifacts"
                ]
            }

    def _build_report(
        self,
        start,
        end,
        artifacts: Dict,
        decisions: Dict,
        executions: Dict,
        agents: Dict,
        insights: Dict
    ) -> str:
        """Build markdown report for Discord/storage."""
        # Format artifact types
        type_lines = [
            f"  - {k}: {v}" for k, v in artifacts['by_type'].items() if v > 0
        ]
        type_section = '\n'.join(type_lines) if type_lines else '  - None'

        # Format top artifacts
        top_lines = [
            f"  {i+1}. [{a['type']}] {a['title'][:50]} (score: {a['score']:.2f})"
            for i, a in enumerate(artifacts['top_items'][:3])
        ]
        top_section = '\n'.join(top_lines) if top_lines else '  - None'

        # Format themes
        themes = insights.get('key_themes', [])
        theme_lines = [f"- {t}" for t in themes]
        theme_section = '\n'.join(theme_lines) if theme_lines else '- No themes identified'

        # Format recommendations
        recs = insights.get('recommendations', [])
        rec_lines = [f"- {r}" for r in recs]
        rec_section = '\n'.join(rec_lines) if rec_lines else '- No recommendations'

        # Format agent activity
        agent_lines = [
            f"  - {a['agent']}: {a['count']} executions"
            for a in agents['most_active'][:5]
        ]
        agent_section = '\n'.join(agent_lines) if agent_lines else '  - No executions'

        return f"""# Weekly Synthesis: {start} to {end}

## Summary
{insights.get('trend_analysis', 'No analysis available.')}

## Artifacts Extracted: {artifacts['total']}

**By Type:**
{type_section}

**Top Items:**
{top_section}

## Decisions Made

| Status | Count |
|--------|-------|
| Approved | {decisions['approved']} |
| Rejected | {decisions['rejected']} |
| Deferred | {decisions['deferred']} |
| **Total** | **{decisions['total']}** |

## Execution Pipeline

- **Total Executions:** {executions['total']}
- **Succeeded:** {executions['succeeded']}
- **Failed:** {executions['failed']}
- **Success Rate:** {executions['success_rate']:.0%}
- **Avg Execution Time:** {executions['avg_time_ms']}ms

## Agent Activity

**Most Active:**
{agent_section}

## Key Themes

{theme_section}

## Recommendations

{rec_section}

## Attention Required

- **High Priority Pending:** {artifacts['pending_high_priority']} items
- **Oldest Pending Item:** {artifacts['oldest_pending_days']} days

---
*Generated by Chief of Staff Layer - Phase C | Session 555*
"""

    def get_latest_synthesis(self) -> 'WeeklySynthesis':
        """Get the most recent synthesis."""
        from core.models_conversation_artifacts import WeeklySynthesis
        return WeeklySynthesis.objects.first()

    def get_synthesis_history(self, limit: int = 10):
        """Get recent synthesis records."""
        from core.models_conversation_artifacts import WeeklySynthesis
        return list(WeeklySynthesis.objects.all()[:limit])


# Singleton instance
synthesis_service = WeeklySynthesisService()
