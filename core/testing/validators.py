"""
Validation and Scoring Utilities for Agent Testing
===================================================

Session 334: Tools for validating agent outputs against expected results
and scoring the quality of business research.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from difflib import SequenceMatcher


@dataclass
class ValidationResult:
    """Result of validating an agent output."""
    valid: bool
    score: float  # 0-100
    issues: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompetitorMatch:
    """Result of matching found competitors against expected."""
    expected: str
    found: Optional[str]
    similarity: float
    matched: bool


class AgentOutputValidator:
    """Validates agent outputs against expected results."""

    def __init__(self, strict_mode: bool = False):
        """
        Initialize validator.

        Args:
            strict_mode: If True, require exact matches. If False, use fuzzy matching.
        """
        self.strict_mode = strict_mode

    def validate_competitor_analysis(
        self,
        output: Dict[str, Any],
        expected_competitors: List[str],
        expected_sections: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate competitor analysis output.

        Args:
            output: Agent output (the 'data' field from AgentResult)
            expected_competitors: List of competitor names we expect to find
            expected_sections: Optional list of sections the analysis should have

        Returns:
            ValidationResult with score and issues
        """
        issues = []
        details = {}
        score = 0.0

        if expected_sections is None:
            expected_sections = [
                'market overview',
                'competitors',
                'swot',
                'opportunities',
                'recommendations'
            ]

        # Check if output has analysis
        analysis = output.get('analysis', {})
        if isinstance(analysis, dict):
            analysis_text = analysis.get('analysis', '')
        else:
            analysis_text = str(analysis)

        if not analysis_text:
            issues.append("No analysis content found")
            return ValidationResult(valid=False, score=0, issues=issues)

        # Score 1: Check for expected sections (25 points)
        section_score = self._score_sections(analysis_text, expected_sections)
        details['section_score'] = section_score
        score += section_score * 0.25 * 100

        # Score 2: Check competitor mentions (35 points)
        competitor_matches = self._match_competitors(analysis_text, expected_competitors)
        details['competitor_matches'] = [
            {'expected': m.expected, 'found': m.found, 'matched': m.matched}
            for m in competitor_matches
        ]
        matched_count = sum(1 for m in competitor_matches if m.matched)
        if expected_competitors:
            competitor_score = matched_count / len(expected_competitors)
        else:
            competitor_score = 1.0
        details['competitor_score'] = competitor_score
        score += competitor_score * 35

        # Score 3: Analysis depth (20 points)
        depth_score = self._score_depth(analysis_text)
        details['depth_score'] = depth_score
        score += depth_score * 20

        # Score 4: Actionability (20 points)
        actionability_score = self._score_actionability(analysis_text)
        details['actionability_score'] = actionability_score
        score += actionability_score * 20

        # Add issues for missing elements
        if section_score < 0.5:
            issues.append(f"Missing expected sections (score: {section_score:.0%})")

        if competitor_score < 0.5:
            missing = [m.expected for m in competitor_matches if not m.matched]
            issues.append(f"Missing competitors: {', '.join(missing[:3])}")

        valid = score >= 50 and not (len(issues) > 2)

        return ValidationResult(
            valid=valid,
            score=min(score, 100),
            issues=issues,
            details=details
        )

    def validate_customer_research(
        self,
        output: Dict[str, Any],
        expected_pain_points: List[str],
        expected_segments: List[str]
    ) -> ValidationResult:
        """
        Validate customer research output.

        Args:
            output: Agent output (the 'data' field from AgentResult)
            expected_pain_points: List of pain points we expect to find
            expected_segments: List of customer segments we expect

        Returns:
            ValidationResult with score and issues
        """
        issues = []
        details = {}
        score = 0.0

        # Check if output has analysis
        analysis = output.get('analysis', {})
        if isinstance(analysis, dict):
            analysis_text = analysis.get('analysis', '')
        else:
            analysis_text = str(analysis)

        if not analysis_text:
            issues.append("No analysis content found")
            return ValidationResult(valid=False, score=0, issues=issues)

        # Score 1: Pain points coverage (30 points)
        pain_point_matches = self._fuzzy_match_list(
            analysis_text.lower(),
            [p.lower() for p in expected_pain_points]
        )
        details['pain_points_matched'] = pain_point_matches
        pain_score = pain_point_matches['match_ratio']
        score += pain_score * 30

        # Score 2: Customer segments (25 points)
        segment_matches = self._fuzzy_match_list(
            analysis_text.lower(),
            [s.lower() for s in expected_segments]
        )
        details['segments_matched'] = segment_matches
        segment_score = segment_matches['match_ratio']
        score += segment_score * 25

        # Score 3: Personas present (20 points)
        has_personas = self._check_personas(analysis_text)
        details['has_personas'] = has_personas
        score += 20 if has_personas else 5

        # Score 4: Quotes/Evidence (15 points)
        has_quotes = self._check_quotes(analysis_text)
        details['has_quotes'] = has_quotes
        score += 15 if has_quotes else 5

        # Score 5: Recommendations (10 points)
        has_recommendations = 'recommend' in analysis_text.lower()
        details['has_recommendations'] = has_recommendations
        score += 10 if has_recommendations else 0

        # Generate issues
        if pain_score < 0.5:
            issues.append("Missing key pain points in analysis")
        if segment_score < 0.5:
            issues.append("Missing expected customer segments")
        if not has_personas:
            issues.append("No customer personas found")

        valid = score >= 50

        return ValidationResult(
            valid=valid,
            score=min(score, 100),
            issues=issues,
            details=details
        )

    def _score_sections(self, text: str, expected_sections: List[str]) -> float:
        """Score based on presence of expected sections."""
        text_lower = text.lower()
        found = sum(1 for section in expected_sections if section in text_lower)
        return found / len(expected_sections) if expected_sections else 1.0

    def _match_competitors(
        self,
        text: str,
        expected: List[str]
    ) -> List[CompetitorMatch]:
        """Match found competitors against expected list."""
        matches = []
        text_lower = text.lower()

        for expected_name in expected:
            # Try exact match first
            if expected_name.lower() in text_lower:
                matches.append(CompetitorMatch(
                    expected=expected_name,
                    found=expected_name,
                    similarity=1.0,
                    matched=True
                ))
                continue

            # Try fuzzy match
            best_match = None
            best_similarity = 0.0

            # Extract potential competitor names (capitalized words)
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            for word in words:
                similarity = SequenceMatcher(
                    None, expected_name.lower(), word.lower()
                ).ratio()
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = word

            matched = best_similarity >= (0.9 if self.strict_mode else 0.7)
            matches.append(CompetitorMatch(
                expected=expected_name,
                found=best_match if matched else None,
                similarity=best_similarity,
                matched=matched
            ))

        return matches

    def _score_depth(self, text: str) -> float:
        """Score analysis depth based on length and structure."""
        # Word count
        word_count = len(text.split())

        # Structure indicators
        has_headers = bool(re.search(r'^#+\s+\w+', text, re.MULTILINE))
        has_lists = bool(re.search(r'^[-*•]\s+\w+', text, re.MULTILINE))
        has_numbers = bool(re.search(r'^\d+\.\s+\w+', text, re.MULTILINE))

        score = 0.0

        # Word count scoring
        if word_count >= 500:
            score += 0.4
        elif word_count >= 300:
            score += 0.3
        elif word_count >= 100:
            score += 0.2
        else:
            score += 0.1

        # Structure scoring
        if has_headers:
            score += 0.2
        if has_lists:
            score += 0.2
        if has_numbers:
            score += 0.2

        return min(score, 1.0)

    def _score_actionability(self, text: str) -> float:
        """Score how actionable the analysis is."""
        actionable_keywords = [
            'recommend', 'should', 'opportunity', 'action',
            'next step', 'strategy', 'focus on', 'prioritize',
            'consider', 'implement', 'develop', 'build'
        ]

        text_lower = text.lower()
        found = sum(1 for kw in actionable_keywords if kw in text_lower)

        # Score based on actionable language
        return min(found / 5, 1.0)  # Max out at 5 keywords

    def _fuzzy_match_list(
        self,
        text: str,
        expected_items: List[str]
    ) -> Dict[str, Any]:
        """Fuzzy match expected items in text."""
        found = []
        not_found = []

        for item in expected_items:
            # Check for key words from the item
            words = item.split()
            key_words = [w for w in words if len(w) > 3]

            if any(w in text for w in key_words):
                found.append(item)
            else:
                not_found.append(item)

        return {
            'found': found,
            'not_found': not_found,
            'match_ratio': len(found) / len(expected_items) if expected_items else 1.0
        }

    def _check_personas(self, text: str) -> bool:
        """Check if text contains customer personas."""
        persona_indicators = [
            'persona', 'customer type', 'buyer type',
            'target customer', 'user segment', 'demographic'
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in persona_indicators)

    def _check_quotes(self, text: str) -> bool:
        """Check if text contains customer quotes."""
        # Look for quoted text
        has_quotes = bool(re.search(r'"[^"]{10,}"', text))
        has_quote_mentions = 'quote' in text.lower() or 'said' in text.lower()
        return has_quotes or has_quote_mentions


class ResearchQualityScorer:
    """Scores overall quality of business research."""

    def __init__(self):
        self.validator = AgentOutputValidator()

    def score_research_result(
        self,
        result: Dict[str, Any],
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score a research result against scenario expectations.

        Args:
            result: The research result to score
            scenario: The test scenario with expectations

        Returns:
            Dict with overall score and breakdown
        """
        research_type = result.get('research_type', 'competitor')

        if research_type == 'competitor':
            validation = self.validator.validate_competitor_analysis(
                output=result,
                expected_competitors=scenario.get('expected_competitors', []),
            )
        else:
            validation = self.validator.validate_customer_research(
                output=result,
                expected_pain_points=scenario.get('expected_pain_points', []),
                expected_segments=scenario.get('expected_customer_segments', []),
            )

        # Add execution metrics
        execution_score = self._score_execution_metrics(result)

        # Combine scores
        overall_score = (
            validation.score * 0.7 +
            execution_score * 30
        )

        return {
            'overall_score': min(overall_score, 100),
            'validation_score': validation.score,
            'execution_score': execution_score * 100,
            'valid': validation.valid,
            'issues': validation.issues,
            'details': validation.details,
        }

    def _score_execution_metrics(self, result: Dict[str, Any]) -> float:
        """Score execution metrics (time, data points, etc.)."""
        score = 0.0

        # Data points analyzed
        data_points = result.get('data_points_analyzed', 0)
        if data_points >= 20:
            score += 0.4
        elif data_points >= 10:
            score += 0.3
        elif data_points > 0:
            score += 0.1

        # Sources used
        sources = result.get('sources_used', [])
        if len(sources) >= 3:
            score += 0.3
        elif len(sources) >= 2:
            score += 0.2
        elif len(sources) >= 1:
            score += 0.1

        # Has raw data for reference
        if result.get('raw_data'):
            score += 0.3

        return min(score, 1.0)


def quick_validate(
    output: Dict[str, Any],
    expected: Dict[str, Any]
) -> Tuple[bool, float, List[str]]:
    """
    Quick validation helper.

    Args:
        output: Agent output to validate
        expected: Dict with expected_competitors, expected_pain_points, etc.

    Returns:
        Tuple of (valid, score, issues)
    """
    validator = AgentOutputValidator()

    if 'expected_competitors' in expected:
        result = validator.validate_competitor_analysis(
            output=output,
            expected_competitors=expected['expected_competitors']
        )
    else:
        result = validator.validate_customer_research(
            output=output,
            expected_pain_points=expected.get('expected_pain_points', []),
            expected_segments=expected.get('expected_customer_segments', [])
        )

    return result.valid, result.score, result.issues
