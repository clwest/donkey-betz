# Session 862: PublishGate - Quality evaluation before publishing
# Session 864: Added operational title auto-classification, lowered structure threshold
# Implements content scoring and routing logic

import logging
import re
from dataclasses import dataclass
from typing import Optional, Tuple, List
from django.db.models import Q

logger = logging.getLogger(__name__)


@dataclass
class GateResult:
    """Result from PublishGate evaluation."""
    decision: str  # 'publish', 'enhance', 'internal_only'
    quality_score: float
    novelty_score: float
    structure_score: float
    content_type: str  # 'public', 'internal', 'strategic'
    notes: str
    mythology_score: float = 1.0  # 1.0 = clean, 0.0 = high mythology risk
    suggested_category: Optional[str] = None


class PublishGate:
    """
    Quality gate for content before publishing.

    Evaluates:
    1. Content quality (writing, completeness)
    2. Novelty (uniqueness vs existing content)
    3. Structure (formatting, hooks, sections)
    4. Content type (public vs internal)

    Returns decision:
    - 'publish': Ready for public publishing
    - 'enhance': Good content, needs editorial polish
    - 'internal_only': Should be internal note/build log
    """

    # Thresholds for publishing
    QUALITY_THRESHOLD = 0.70  # Session 1009: Raised from 0.65 back toward 0.75 — quality > throughput
    NOVELTY_THRESHOLD = 0.60  # Raised back from 0.50 — low threshold caused duplicate-topic blogs
    STRUCTURE_THRESHOLD = 0.55  # Session 864: Lowered from 0.65 to catch more legitimate content
    # Session 1003: Lowered from 0.5 — MythologyDetectionService gives 0.55-1.0 risk
    # on ALL AI-generated content, blocking every blog from publishing.
    MYTHOLOGY_THRESHOLD = 0.15

    # Session 864: Operational title prefixes that bypass quality checks -> internal_only
    # These are clearly internal documents and shouldn't be evaluated as public content
    OPERATIONAL_TITLE_PATTERNS = [
        r'^\[research\]',           # [Research] ...
        r'^\[stage \d+',            # [Stage 1 - Research Brief] ...
        r'^\[report\]',             # [Report] ...
        r'^\[audit\]',              # [Audit] ...
        r'^\[internal\]',           # [Internal] ...
        r'^\[debug\]',              # [Debug] ...
        r'^\[fix\]',                # [Fix] ...
        r'^\[todo\]',               # [TODO] ...
        r'^researchagent:',         # ResearchAgent: ...
        r'^systeminsights:',        # SystemInsights: ...
        r'^root.?cause',            # Root-cause analysis...
    ]

    # Signals indicating internal content
    INTERNAL_SIGNALS = [
        'we built', 'we learned', 'we discovered',
        'our system', 'our agents', 'our spiders',
        'internally', 'team reflection', 'build log',
        'action items:', 'next steps for us',
        'system reference:', 'internal note:',
        'donkey betz', 'donkeybetz',  # Platform brand name = internal
    ]

    # Signals indicating public content
    PUBLIC_SIGNALS = [
        'you should', 'you can', 'readers will',
        'in this article', 'we\'ll explore',
        'industry trends', 'market analysis',
        'best practices for', 'how to guide',
    ]

    # Technical density indicators (high = internal)
    TECHNICAL_INDICATORS = [
        'spider', 'agent', 'celery', 'django',
        'kalshi', 'pipeline', 'endpoint', 'migration',
        'database', 'redis', 'websocket', 'api',
    ]

    def evaluate(self, blog) -> GateResult:
        """
        Evaluate a SelfBlog for publishing readiness.

        Args:
            blog: SelfBlog instance

        Returns:
            GateResult with scores and decision
        """
        # Session 864: Check for operational title patterns first
        # These bypass quality checks and go straight to internal_only
        if self._is_operational_title(blog.title):
            logger.info(f"PublishGate: {blog.title[:50]}... -> internal_only (operational title pattern)")
            return GateResult(
                decision='internal_only',
                quality_score=0.0,  # Not scored
                novelty_score=0.0,
                structure_score=0.0,
                content_type='internal',
                notes='Operational content detected from title pattern; auto-classified as internal',
                suggested_category='internal_note',
            )

        # Get full text for analysis
        full_text = self._get_full_text(blog)

        # Score each dimension
        quality_score = self._score_quality(blog, full_text)
        novelty_score = self._score_novelty(blog, full_text)
        structure_score = self._score_structure(blog, full_text)
        mythology_score = self._score_mythology(blog, full_text)

        # Check research backing — penalize quality if no claims
        claims_count = self._check_research_backing(blog)
        if claims_count == 0:
            quality_score = max(0.0, quality_score - 0.20)
            logger.info(f"PublishGate: No research claims found, quality penalized to {quality_score:.2f}")

        # Determine content type
        content_type, type_confidence = self._classify_content_type(blog, full_text)

        # Make decision
        decision, notes = self._make_decision(
            quality_score, novelty_score, structure_score,
            content_type, type_confidence, mythology_score
        )

        # Suggest category if needed
        suggested_category = self._suggest_category(blog, content_type, decision)

        result = GateResult(
            decision=decision,
            quality_score=quality_score,
            novelty_score=novelty_score,
            structure_score=structure_score,
            content_type=content_type,
            notes=notes,
            mythology_score=mythology_score,
            suggested_category=suggested_category,
        )

        logger.info(f"PublishGate: {blog.title[:50]}... -> {decision} (Q:{quality_score:.2f}, N:{novelty_score:.2f}, S:{structure_score:.2f}, M:{mythology_score:.2f})")

        return result

    def _is_operational_title(self, title: str) -> bool:
        """
        Session 864: Check if title indicates operational/internal content.

        These patterns indicate documents that are clearly internal and
        shouldn't be evaluated for public publishing quality.
        """
        if not title:
            return False

        title_lower = title.lower().strip()

        for pattern in self.OPERATIONAL_TITLE_PATTERNS:
            if re.match(pattern, title_lower):
                return True

        return False

    def _get_full_text(self, blog) -> str:
        """Extract full text from blog for analysis."""
        parts = [
            blog.title or '',
            blog.meta_description or '',
            blog.intro or '',
        ]

        # Add sections
        if blog.sections:
            for section in blog.sections:
                if isinstance(section, dict):
                    parts.append(section.get('header', ''))
                    parts.append(section.get('content', ''))

        parts.append(blog.conclusion or '')
        parts.append(blog.full_text or '')

        return ' '.join(parts).lower()

    def _score_quality(self, blog, full_text: str) -> float:
        """
        Score content quality (0-1).

        Factors:
        - Word count (300-1500 is ideal)
        - Has intro and conclusion
        - Has meaningful sections
        - No placeholder text
        """
        score = 0.5  # Base score

        # Word count scoring — hard reject under 300 words
        word_count = blog.word_count or len(full_text.split())
        if word_count < 300:
            # Thin content can never pass quality gate
            return max(0.0, 0.3 - (300 - word_count) * 0.002)
        elif 500 <= word_count <= 1500:
            score += 0.15
        elif 300 <= word_count < 500 or 1500 < word_count <= 2500:
            score += 0.10

        # Has intro
        if blog.intro and len(blog.intro) > 50:
            score += 0.10

        # Has conclusion
        if blog.conclusion and len(blog.conclusion) > 50:
            score += 0.10

        # Has meaningful sections
        if blog.sections and len(blog.sections) >= 3:
            score += 0.10
        elif blog.sections and len(blog.sections) >= 2:
            score += 0.05

        # Penalize placeholder text
        placeholders = ['lorem ipsum', 'todo:', 'fixme:', 'placeholder', 'example text']
        for p in placeholders:
            if p in full_text:
                score -= 0.1

        # Penalize very short sections
        if blog.sections:
            short_sections = sum(1 for s in blog.sections
                               if isinstance(s, dict) and len(s.get('content', '')) < 100)
            if short_sections > len(blog.sections) / 2:
                score -= 0.1

        return max(0.0, min(1.0, score))

    def _score_novelty(self, blog, full_text: str) -> float:
        """
        Score novelty vs existing content (0-1).

        Session 1004: Strengthened to count ALL similar blogs and apply
        proportional penalties. Previous version broke after first match,
        allowing 19/40 published blogs on the same topic.

        Checks:
        - Title similarity to existing blogs (cumulative)
        - Topic keyword overlap across all existing blogs
        """
        from core.models_unified_system import SelfBlog

        score = 1.0

        # Check title similarity against ALL approved/published blogs
        existing = SelfBlog.objects.exclude(id=blog.id).filter(
            status__in=['approved', 'published']
        ).values_list('title', flat=True)[:200]

        title_lower = blog.title.lower() if blog.title else ''
        title_words = set(title_lower.split()) - {'the', 'a', 'an', 'in', 'of', 'and', 'to', 'for', 'on', 'is', 'at', 'by', 'with'}

        exact_matches = 0
        high_overlap_matches = 0

        for existing_title in existing:
            if not existing_title:
                continue
            existing_lower = existing_title.lower()

            # Check for substring containment (very similar titles)
            if title_lower in existing_lower or existing_lower in title_lower:
                exact_matches += 1
                continue

            # Check significant word overlap
            existing_words = set(existing_lower.split()) - {'the', 'a', 'an', 'in', 'of', 'and', 'to', 'for', 'on', 'is', 'at', 'by', 'with'}
            if not title_words or not existing_words:
                continue
            overlap = len(title_words & existing_words) / max(len(title_words), 1)

            if overlap > 0.5:
                high_overlap_matches += 1

        # Apply proportional penalties
        # First duplicate: -0.25, each additional: -0.15
        if exact_matches > 0:
            score -= 0.25 + (exact_matches - 1) * 0.15
        if high_overlap_matches > 0:
            score -= 0.15 + (high_overlap_matches - 1) * 0.10

        # Check for common overused topics
        overused_topics = [
            'best practices', 'getting started', 'introduction to',
            'complete guide', 'ultimate guide', 'how we built',
        ]
        for topic in overused_topics:
            if topic in title_lower:
                score -= 0.1
                break

        return max(0.0, min(1.0, score))

    def _score_structure(self, blog, full_text: str) -> float:
        """
        Score content structure and formatting (0-1).

        Factors:
        - Section variety (not all starting the same)
        - Has visual elements (callouts, stats mentioned)
        - Proper section length distribution
        """
        score = 0.5  # Base score

        # Check section variety
        if blog.sections and len(blog.sections) >= 2:
            headers = [s.get('header', '') for s in blog.sections if isinstance(s, dict)]

            # Check if sections have varied openings
            first_words = [h.split()[0] if h else '' for h in headers]
            unique_first_words = len(set(first_words))
            variety_ratio = unique_first_words / max(len(first_words), 1)

            if variety_ratio > 0.7:
                score += 0.15
            elif variety_ratio > 0.5:
                score += 0.10

        # Check for engagement elements
        engagement_patterns = [
            r'\d+%',  # Percentages
            r'\d+\+?',  # Numbers/stats
            r'[""].*?[""]',  # Quotes
            r'\?',  # Questions
        ]
        engagement_count = 0
        for pattern in engagement_patterns:
            if re.search(pattern, full_text):
                engagement_count += 1

        score += min(0.2, engagement_count * 0.05)

        # Check section balance
        if blog.sections:
            lengths = [len(s.get('content', '')) for s in blog.sections if isinstance(s, dict)]
            if lengths:
                avg_length = sum(lengths) / len(lengths)
                variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
                normalized_variance = variance / (avg_length ** 2 + 1)

                # Lower variance = more balanced = better
                if normalized_variance < 0.3:
                    score += 0.10
                elif normalized_variance < 0.5:
                    score += 0.05

        # Penalize wall-of-text (no sections, long intro)
        if not blog.sections or len(blog.sections) < 2:
            score -= 0.15

        return max(0.0, min(1.0, score))

    def _classify_content_type(self, blog, full_text: str) -> Tuple[str, float]:
        """
        Classify content as public, internal, or strategic.

        Returns:
            (content_type, confidence)
        """
        internal_score = 0
        public_score = 0

        # Check for internal signals
        for signal in self.INTERNAL_SIGNALS:
            if signal in full_text:
                internal_score += 1

        # Check for public signals
        for signal in self.PUBLIC_SIGNALS:
            if signal in full_text:
                public_score += 1

        # Check technical density
        technical_count = sum(1 for t in self.TECHNICAL_INDICATORS if t in full_text)
        if technical_count >= 5:
            internal_score += 2
        elif technical_count >= 3:
            internal_score += 1

        # Check category hints
        if blog.category in ['build_log', 'internal_note', 'playbook']:
            internal_score += 3
        elif blog.category in ['blog', 'research_brief']:
            public_score += 2
        elif blog.category in ['dossier', 'audit']:
            # Strategic content
            return ('strategic', 0.7)

        # Make decision
        total = internal_score + public_score + 1  # +1 to avoid division by zero

        if internal_score > public_score * 1.5:
            return ('internal', internal_score / total)
        elif public_score > internal_score * 1.5:
            return ('public', public_score / total)
        else:
            # Ambiguous - default to public but low confidence
            return ('public', 0.5)

    def _make_decision(
        self,
        quality: float,
        novelty: float,
        structure: float,
        content_type: str,
        type_confidence: float,
        mythology_score: float = 1.0
    ) -> Tuple[str, str]:
        """
        Make final publish decision.

        Returns:
            (decision, notes)
        """
        notes_parts = []

        # Session 997: Mythology check — very high risk caps decision at 'enhance'
        # Session 1003: Lowered threshold from 0.5 to MYTHOLOGY_THRESHOLD (0.15)
        # Old threshold blocked ALL AI-generated blogs (MythologyDetection too aggressive)
        if mythology_score < self.MYTHOLOGY_THRESHOLD:
            notes_parts.append(
                f"Mythology score {mythology_score:.2f} below {self.MYTHOLOGY_THRESHOLD}; "
                f"capped at 'enhance'"
            )

        # Internal content should not be published publicly
        if content_type == 'internal' and type_confidence > 0.6:
            notes_parts.append(f"Content classified as internal (confidence: {type_confidence:.0%})")
            notes_parts.append("Recommend keeping as build log or internal note")
            return ('internal_only', '; '.join(notes_parts))

        # Check quality thresholds
        passed_quality = quality >= self.QUALITY_THRESHOLD
        passed_novelty = novelty >= self.NOVELTY_THRESHOLD
        passed_structure = structure >= self.STRUCTURE_THRESHOLD

        if not passed_quality:
            notes_parts.append(f"Quality score {quality:.2f} below threshold {self.QUALITY_THRESHOLD}")
        if not passed_novelty:
            notes_parts.append(f"Novelty score {novelty:.2f} below threshold {self.NOVELTY_THRESHOLD}")
        if not passed_structure:
            notes_parts.append(f"Structure score {structure:.2f} below threshold {self.STRUCTURE_THRESHOLD}")

        # All thresholds passed
        if passed_quality and passed_novelty and passed_structure:
            if mythology_score < self.MYTHOLOGY_THRESHOLD:
                notes_parts.append("All quality checks passed but mythology risk too high")
                return ('enhance', '; '.join(notes_parts))
            notes_parts.append("All quality checks passed")
            return ('publish', '; '.join(notes_parts))

        # Good content but needs work
        if quality >= 0.6 and (passed_novelty or passed_structure):
            notes_parts.append("Content has potential but needs enhancement")
            return ('enhance', '; '.join(notes_parts))

        # Low quality - should be internal
        notes_parts.append("Quality too low for public publishing")
        return ('internal_only', '; '.join(notes_parts))

    def _suggest_category(self, blog, content_type: str, decision: str) -> Optional[str]:
        """Suggest appropriate category based on analysis."""

        if decision == 'internal_only':
            # Suggest internal categories
            if content_type == 'internal':
                if 'lesson' in blog.title.lower() or 'learned' in blog.title.lower():
                    return 'build_log'
                elif 'practice' in blog.title.lower() or 'playbook' in blog.title.lower():
                    return 'playbook'
                else:
                    return 'internal_note'

        if decision == 'enhance':
            # Keep current category but note it needs work
            return None

        # Published content stays as-is
        return None

    def _check_research_backing(self, blog) -> int:
        """Check if blog has research claims in deliberation metadata.
        Returns -1 if no deliberation metadata (non-pipeline blog), else claims count.
        """
        stats = getattr(blog, 'stats_snapshot', None)
        if not stats or not isinstance(stats, dict):
            return -1
        deliberation = stats.get('deliberation', {})
        return deliberation.get('claims_count', 0)

    def _score_mythology(self, blog, full_text: str) -> float:
        """
        Session 997: Score mythology risk (0-1, where 1.0 = clean).

        Uses MythologyDetectionService to find fabricated claims.
        Returns 1.0 on failure so mythology never blocks on error.
        """
        try:
            from mythology.services import MythologyDetectionService
            detection = MythologyDetectionService().detect_mythologies(
                full_text, source_type='publish_gate'
            )
            risk = detection.get('risk_score', 0.0)
            if risk > 0.1:
                logger.info(
                    f"PublishGate mythology: risk={risk:.2f} "
                    f"patterns={detection.get('patterns_found', [])}"
                )
            return max(0.0, min(1.0, 1.0 - risk))
        except Exception as e:
            logger.debug(f"Mythology scoring skipped: {e}")
            return 1.0

    def _check_envelope(self, blog) -> str:
        """
        Session 960 Phase 0: Check for AgentOutputEnvelope in blog metadata.
        Returns notes string if envelope is found and validated, empty string otherwise.
        """
        try:
            metadata = getattr(blog, 'metadata', None)
            if not metadata or not isinstance(metadata, dict):
                return ''
            envelope_data = metadata.get('envelope')
            if not envelope_data or not isinstance(envelope_data, dict):
                return ''

            from core.services.artifact_envelope import AgentOutputEnvelope, validate_envelope
            envelope = AgentOutputEnvelope.from_dict(envelope_data)
            result = validate_envelope(envelope, min_citation_ratio=0.0)

            parts = []
            if result.get('valid'):
                parts.append(f"Envelope: valid (citations: {result.get('citation_score', 0):.0%})")
            else:
                parts.append(f"Envelope: {len(result.get('violations', []))} issue(s)")
            return '; '.join(parts)
        except Exception as e:
            logger.debug(f"Envelope check skipped: {e}")
            return ''

    def apply_to_blog(self, blog, save: bool = True) -> GateResult:
        """
        Evaluate and optionally update blog with scores.

        Args:
            blog: SelfBlog instance
            save: Whether to save changes to database

        Returns:
            GateResult
        """
        result = self.evaluate(blog)

        # Session 960 Phase 0: If blog has an envelope in metadata, validate it
        envelope_notes = self._check_envelope(blog)
        if envelope_notes:
            result.notes = (result.notes + '; ' + envelope_notes) if result.notes else envelope_notes

        # Update blog fields
        blog.quality_score = result.quality_score
        blog.novelty_score = result.novelty_score
        blog.structure_score = result.structure_score
        blog.content_type = result.content_type
        blog.gate_notes = result.notes
        blog.publish_ready = (result.decision == 'publish')

        # Update status if needed
        if result.decision == 'internal_only':
            if blog.status in ['draft', 'pending_review']:
                blog.status = 'draft'
        elif result.decision == 'enhance':
            if blog.status in ['draft', 'pending_review']:
                blog.status = 'needs_enhancement'
        # Session 1000C: Promote publish-ready blogs to 'approved'
        elif result.decision == 'publish':
            if blog.status in ['draft', 'pending_review', 'needs_enhancement']:
                blog.status = 'approved'

        # Update category if suggested
        if result.suggested_category and blog.category == 'blog':
            blog.category = result.suggested_category
            logger.info(f"Changed category from 'blog' to '{result.suggested_category}'")

        if save:
            blog.save()
            logger.info(f"Updated blog {blog.id} with gate results")

        return result


# Convenience functions
def evaluate_blog(blog_id: str) -> GateResult:
    """Evaluate a blog by ID."""
    from core.models_unified_system import SelfBlog

    blog = SelfBlog.objects.get(id=blog_id)
    gate = PublishGate()
    return gate.apply_to_blog(blog)


def evaluate_all_drafts() -> List[Tuple[str, GateResult]]:
    """Evaluate all draft blogs."""
    from core.models_unified_system import SelfBlog

    gate = PublishGate()
    results = []

    drafts = SelfBlog.objects.filter(status='draft')
    for blog in drafts:
        result = gate.apply_to_blog(blog)
        results.append((str(blog.id), result))

    return results


def get_gate_summary() -> dict:
    """Get summary of gate evaluations."""
    from core.models_unified_system import SelfBlog
    from django.db.models import Count

    return {
        'total_blogs': SelfBlog.objects.count(),
        'publish_ready': SelfBlog.objects.filter(publish_ready=True).count(),
        'needs_enhancement': SelfBlog.objects.filter(status='needs_enhancement').count(),
        'internal_content': SelfBlog.objects.filter(content_type='internal').count(),
        'public_content': SelfBlog.objects.filter(content_type='public').count(),
        'by_category': dict(
            SelfBlog.objects.values('category').annotate(count=Count('id')).values_list('category', 'count')
        ),
    }
