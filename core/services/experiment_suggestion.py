"""
Session 606: Experiment Suggestion Engine

Analyzes learning gaps and suggests new experiments to improve system confidence.

Features:
1. Identify themes with insufficient data (< 3 samples)
2. Calculate recommended sample sizes for confidence targets
3. Generate experiment ideas from high-value decisions
4. Surface patterns from successful experiments
"""

import logging
import math
from typing import Dict, List, Any, Optional
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Target confidence levels for experiments."""
    LOW = "low"          # 3-4 samples
    MEDIUM = "medium"    # 5-7 samples
    HIGH = "high"        # 8+ samples


@dataclass
class LearningGap:
    """Represents a gap in learning data."""
    theme: str
    current_samples: int
    needed_for_low: int
    needed_for_medium: int
    needed_for_high: int
    priority: str  # 'critical', 'high', 'medium', 'low'
    related_decisions: int
    suggestion: str


@dataclass
class ExperimentSuggestion:
    """A suggested experiment to run."""
    title: str
    hypothesis: str
    theme: str
    impact_area: str
    source: str  # 'learning_gap', 'high_value_decision', 'pattern'
    priority_score: int  # 0-100
    confidence_target: str
    suggested_kpi: str
    related_decision_id: Optional[str]
    rationale: str


class ExperimentSuggestionService:
    """
    Session 606: Suggests experiments based on learning gaps and patterns.

    Uses data from:
    - Existing experiments and their outcomes
    - Boardroom decisions (especially high-value ones)
    - Learning velocity data
    - Weighted learning patterns
    """

    # Confidence level sample requirements
    SAMPLE_REQUIREMENTS = {
        ConfidenceLevel.LOW: 3,
        ConfidenceLevel.MEDIUM: 5,
        ConfidenceLevel.HIGH: 8,
    }

    # Decision types that should have experiments
    EXPERIMENT_WORTHY_TYPES = ['product', 'pipeline', 'architecture', 'experiment']

    # High-value impact areas to prioritize
    PRIORITY_IMPACT_AREAS = ['product', 'workflow', 'agents', 'infrastructure']

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ExperimentSuggestionService")

    def get_suggestions(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get experiment suggestions based on learning gaps and patterns.

        Returns:
            Dict with:
                - gaps: Learning gaps by theme
                - suggestions: Prioritized experiment suggestions
                - coverage: Current experiment coverage stats
                - sample_size_guide: Recommended sample sizes
        """
        try:
            # Analyze current coverage
            coverage = self._analyze_coverage()

            # Find learning gaps
            gaps = self._find_learning_gaps(coverage)

            # Generate suggestions
            suggestions = self._generate_suggestions(gaps, coverage, limit)

            # Calculate sample size recommendations
            sample_guide = self._get_sample_size_guide()

            return {
                'success': True,
                'gaps': [self._gap_to_dict(g) for g in gaps],
                'suggestions': [self._suggestion_to_dict(s) for s in suggestions],
                'coverage': coverage,
                'sample_size_guide': sample_guide,
                'summary': self._generate_summary(gaps, suggestions, coverage),
                'timestamp': timezone.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error generating suggestions: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
            }

    def _analyze_coverage(self) -> Dict[str, Any]:
        """Analyze current experiment coverage by theme and type."""
        from core.models_pilot_readiness import Experiment
        from core.models_unified_system import AgentDecisionSummary

        experiments = Experiment.objects.all()
        decisions = AgentDecisionSummary.objects.all()

        # Count experiments by extracted themes
        theme_counts = defaultdict(int)
        type_counts = defaultdict(int)
        status_counts = defaultdict(int)

        for exp in experiments:
            status_counts[exp.status] += 1

            # Extract themes from experiment name/hypothesis
            themes = self._extract_themes(exp.name, exp.hypothesis)
            for theme in themes:
                theme_counts[theme] += 1

        # Count decisions by type and impact area
        decision_by_type = defaultdict(int)
        decision_by_area = defaultdict(int)

        for dec in decisions:
            decision_by_type[dec.decision_type] += 1
            decision_by_area[dec.impact_area] += 1

        # Calculate coverage ratios
        total_experiments = experiments.count()
        total_decisions = decisions.count()
        canonical_decisions = decisions.filter(is_canonical=True).count()

        return {
            'total_experiments': total_experiments,
            'experiments_by_status': dict(status_counts),
            'experiments_by_theme': dict(theme_counts),
            'total_decisions': total_decisions,
            'canonical_decisions': canonical_decisions,
            'decisions_by_type': dict(decision_by_type),
            'decisions_by_area': dict(decision_by_area),
            'experiment_coverage_ratio': round(
                (total_experiments / canonical_decisions * 100) if canonical_decisions > 0 else 0, 1
            ),
        }

    def _extract_themes(self, name: str, hypothesis: str = None) -> List[str]:
        """Extract themes from experiment name and hypothesis."""
        themes = []
        text = f"{name or ''} {hypothesis or ''}".lower()

        # Theme keywords
        theme_keywords = {
            'financial': ['financial', 'trading', 'investment', 'money', 'revenue'],
            'content': ['content', 'writing', 'blog', 'article', 'copy', 'marketing'],
            'product': ['product', 'feature', 'user', 'ux', 'interface'],
            'technical': ['code', 'api', 'infrastructure', 'architecture', 'system'],
            'research': ['research', 'analysis', 'data', 'insight', 'study'],
            'automation': ['automation', 'workflow', 'pipeline', 'process'],
            'ai': ['ai', 'model', 'agent', 'ml', 'learning', 'gpt'],
            'culture': ['culture', 'team', 'process', 'adaptive'],
        }

        for theme, keywords in theme_keywords.items():
            if any(kw in text for kw in keywords):
                themes.append(theme)

        return themes if themes else ['general']

    def _find_learning_gaps(self, coverage: Dict) -> List[LearningGap]:
        """Find themes and areas with insufficient learning data."""
        gaps = []

        # Check each theme for sample count
        theme_counts = coverage.get('experiments_by_theme', {})

        # Also check impact areas from decisions that don't have experiments
        decision_areas = coverage.get('decisions_by_area', {})

        # All themes we care about
        all_themes = set(theme_counts.keys()) | set(decision_areas.keys())

        for theme in all_themes:
            current = theme_counts.get(theme, 0)
            decisions = decision_areas.get(theme, 0)

            # Calculate needs
            low_need = max(0, self.SAMPLE_REQUIREMENTS[ConfidenceLevel.LOW] - current)
            medium_need = max(0, self.SAMPLE_REQUIREMENTS[ConfidenceLevel.MEDIUM] - current)
            high_need = max(0, self.SAMPLE_REQUIREMENTS[ConfidenceLevel.HIGH] - current)

            # Skip if already have high confidence
            if current >= self.SAMPLE_REQUIREMENTS[ConfidenceLevel.HIGH]:
                continue

            # Determine priority
            if current == 0:
                priority = 'critical'
                suggestion = f"No experiments for '{theme}' - start with a small pilot"
            elif current < self.SAMPLE_REQUIREMENTS[ConfidenceLevel.LOW]:
                priority = 'high'
                suggestion = f"Only {current} experiment(s) - need {low_need} more for basic confidence"
            elif current < self.SAMPLE_REQUIREMENTS[ConfidenceLevel.MEDIUM]:
                priority = 'medium'
                suggestion = f"Have {current} experiments - need {medium_need} more for medium confidence"
            else:
                priority = 'low'
                suggestion = f"Have {current} experiments - need {high_need} more for high confidence"

            # Boost priority if many decisions exist without experiments
            if decisions > 50 and current < 3:
                priority = 'critical'
                suggestion = f"{decisions} decisions but only {current} experiments - major gap!"

            gaps.append(LearningGap(
                theme=theme,
                current_samples=current,
                needed_for_low=low_need,
                needed_for_medium=medium_need,
                needed_for_high=high_need,
                priority=priority,
                related_decisions=decisions,
                suggestion=suggestion,
            ))

        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        gaps.sort(key=lambda g: (priority_order.get(g.priority, 4), -g.related_decisions))

        return gaps

    def _generate_suggestions(
        self,
        gaps: List[LearningGap],
        coverage: Dict,
        limit: int
    ) -> List[ExperimentSuggestion]:
        """Generate experiment suggestions based on gaps and patterns."""
        from core.models_unified_system import AgentDecisionSummary

        suggestions = []

        # 1. Suggestions from learning gaps (critical/high priority)
        critical_gaps = [g for g in gaps if g.priority in ('critical', 'high')]
        for gap in critical_gaps[:3]:
            suggestions.append(ExperimentSuggestion(
                title=f"Pilot: {gap.theme.title()} Strategy Validation",
                hypothesis=f"Testing approaches in the {gap.theme} domain will provide learnings for future decisions",
                theme=gap.theme,
                impact_area=gap.theme if gap.theme in self.PRIORITY_IMPACT_AREAS else 'product',
                source='learning_gap',
                priority_score=90 if gap.priority == 'critical' else 75,
                confidence_target='low',
                suggested_kpi=self._suggest_kpi(gap.theme),
                related_decision_id=None,
                rationale=gap.suggestion,
            ))

        # 2. Suggestions from high-value canonical decisions without experiments
        canonical_without_exp = AgentDecisionSummary.objects.filter(
            is_canonical=True,
            decision_type__in=self.EXPERIMENT_WORTHY_TYPES,
        ).order_by('-promoted_at')[:20]

        for decision in canonical_without_exp:
            # Check if already has related experiment
            themes = self._extract_themes(decision.topic, decision.recommended_stance)
            theme = themes[0] if themes else 'general'

            # Skip if we already have suggestions for this theme
            existing_themes = [s.theme for s in suggestions]
            if theme in existing_themes:
                continue

            suggestions.append(ExperimentSuggestion(
                title=f"Validate: {decision.topic[:50]}",
                hypothesis=f"Testing this canonical policy will provide measurable validation",
                theme=theme,
                impact_area=decision.impact_area,
                source='high_value_decision',
                priority_score=70,
                confidence_target='medium',
                suggested_kpi=self._suggest_kpi_from_decision(decision),
                related_decision_id=str(decision.id),
                rationale=f"Canonical policy in {decision.impact_area} - needs experimental validation",
            ))

            if len(suggestions) >= limit:
                break

        # 3. Suggestions from successful experiment patterns
        from core.models_pilot_readiness import Experiment
        successful = Experiment.objects.filter(status='success')

        for exp in successful:
            themes = self._extract_themes(exp.name, exp.hypothesis)
            for theme in themes:
                # Suggest similar experiments in this theme
                existing_themes = [s.theme for s in suggestions]
                if theme not in existing_themes:
                    suggestions.append(ExperimentSuggestion(
                        title=f"Expand: {theme.title()} Success Pattern",
                        hypothesis=f"Building on successful '{exp.name[:30]}...' pattern",
                        theme=theme,
                        impact_area='product',
                        source='pattern',
                        priority_score=65,
                        confidence_target='medium',
                        suggested_kpi=exp.primary_kpi or 'Engagement/Success rate',
                        related_decision_id=None,
                        rationale=f"Pattern from successful experiment - expand coverage in {theme}",
                    ))

        # Sort by priority score
        suggestions.sort(key=lambda s: s.priority_score, reverse=True)

        return suggestions[:limit]

    def _suggest_kpi(self, theme: str) -> str:
        """Suggest a KPI based on theme."""
        kpi_map = {
            'financial': 'ROI / Revenue impact',
            'content': 'Engagement rate / Conversion',
            'product': 'User satisfaction / Adoption rate',
            'technical': 'Performance improvement / Error reduction',
            'research': 'Insight quality / Actionability score',
            'automation': 'Time saved / Error reduction',
            'ai': 'Accuracy / Task completion rate',
            'culture': 'Team velocity / Process adherence',
        }
        return kpi_map.get(theme, 'Success rate / Goal achievement')

    def _suggest_kpi_from_decision(self, decision) -> str:
        """Suggest a KPI based on decision type and impact area."""
        type_kpis = {
            'product': 'User adoption / Satisfaction',
            'pipeline': 'Throughput / Error rate',
            'architecture': 'Performance / Scalability',
            'experiment': 'Success rate / Learning velocity',
        }
        return type_kpis.get(decision.decision_type, 'Goal achievement')

    def _get_sample_size_guide(self) -> Dict[str, Any]:
        """Provide sample size recommendations for different confidence levels."""
        return {
            'confidence_levels': {
                'low': {
                    'samples_needed': 3,
                    'description': 'Basic directional confidence',
                    'use_case': 'Initial validation, quick tests',
                },
                'medium': {
                    'samples_needed': 5,
                    'description': 'Reasonable confidence for decisions',
                    'use_case': 'Standard experiments, feature rollouts',
                },
                'high': {
                    'samples_needed': 8,
                    'description': 'High confidence for critical decisions',
                    'use_case': 'Major investments, irreversible changes',
                },
            },
            'formula': 'Confidence = (success_rate * sample_weight) where sample_weight increases with n',
            'recommendation': 'Start with low confidence (3 samples) and iterate based on results',
        }

    def _generate_summary(
        self,
        gaps: List[LearningGap],
        suggestions: List[ExperimentSuggestion],
        coverage: Dict
    ) -> Dict[str, Any]:
        """Generate a summary of the suggestion analysis."""
        critical_gaps = len([g for g in gaps if g.priority == 'critical'])
        high_gaps = len([g for g in gaps if g.priority == 'high'])

        return {
            'total_experiments': coverage['total_experiments'],
            'coverage_ratio': coverage['experiment_coverage_ratio'],
            'critical_gaps': critical_gaps,
            'high_priority_gaps': high_gaps,
            'suggestions_count': len(suggestions),
            'top_priority': suggestions[0].title if suggestions else None,
            'message': self._generate_message(critical_gaps, high_gaps, coverage),
        }

    def _generate_message(self, critical: int, high: int, coverage: Dict) -> str:
        """Generate a human-readable summary message."""
        total_exp = coverage['total_experiments']

        if critical > 0:
            return f"🚨 {critical} critical learning gaps! Only {total_exp} experiments covering {coverage['experiment_coverage_ratio']}% of canonical decisions."
        elif high > 0:
            return f"⚠️ {high} high-priority gaps. Consider running more experiments to improve confidence."
        elif total_exp < 10:
            return f"📊 System is learning! {total_exp} experiments so far. Keep running pilots to build confidence."
        else:
            return f"✅ Good experiment coverage ({total_exp} experiments). Focus on expanding to new themes."

    def _gap_to_dict(self, gap: LearningGap) -> Dict:
        """Convert LearningGap to dictionary."""
        return {
            'theme': gap.theme,
            'current_samples': gap.current_samples,
            'needed': {
                'for_low_confidence': gap.needed_for_low,
                'for_medium_confidence': gap.needed_for_medium,
                'for_high_confidence': gap.needed_for_high,
            },
            'priority': gap.priority,
            'related_decisions': gap.related_decisions,
            'suggestion': gap.suggestion,
        }

    def _suggestion_to_dict(self, suggestion: ExperimentSuggestion) -> Dict:
        """Convert ExperimentSuggestion to dictionary."""
        return {
            'title': suggestion.title,
            'hypothesis': suggestion.hypothesis,
            'theme': suggestion.theme,
            'impact_area': suggestion.impact_area,
            'source': suggestion.source,
            'priority_score': suggestion.priority_score,
            'confidence_target': suggestion.confidence_target,
            'suggested_kpi': suggestion.suggested_kpi,
            'related_decision_id': suggestion.related_decision_id,
            'rationale': suggestion.rationale,
        }


# Convenience function
def get_experiment_suggestions(limit: int = 10) -> Dict[str, Any]:
    """Get experiment suggestions."""
    service = ExperimentSuggestionService()
    return service.get_suggestions(limit=limit)
