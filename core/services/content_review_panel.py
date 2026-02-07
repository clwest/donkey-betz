"""
Content Review Panel - Session 961
===================================

Multi-agent content review panel that critiques blog posts before saving.

After ContentWriterAgent generates a blog, this panel:
1. Detects the content domain (finance, crypto, sports, etc.)
2. Assembles a 2-agent review panel (EditorAgent + domain expert)
3. Injects spider intelligence for grounding
4. Runs a critique conversation via ConversationOrchestrator
5. Extracts a publish/revise/kill decision from the ExecutionMandate

Uses existing infrastructure:
- ConversationOrchestrator.generate_conversation(conversation_type='critique')
- DecisionEnforcerAgent auto-triggers for critique conversations (Session 960)
- DomainContentContextBuilder.detect_domain()
- SpiderContextBuilder.build_context_for_agent()
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ReviewResult:
    """Result from the multi-agent content review panel."""
    decision: str                           # 'publish', 'revise', 'kill', 'draft' (fallback)
    enhanced_content: Optional[Dict] = None # Modified content dict (or None)
    review_notes: str = ''                  # Summary of panel critique
    confidence: float = 0.0                 # 0.0-1.0
    panel_composition: List[str] = field(default_factory=list)  # Agent names on the panel
    spider_data_used: bool = False          # Whether spider data was injected
    mandate: Optional[Dict] = None          # Full ExecutionMandate dict
    execution_time_ms: int = 0


# Mapping of content domains to specialist review agents.
# All agents below are verified code agents in AgentRouter.AGENT_MAP.
DOMAIN_REVIEW_AGENTS = {
    'finance':   ['TrendAnalysisAgent', 'MarketIntelligenceAgent'],
    'crypto':    ['BlockchainAuditCoordinator', 'TrendAnalysisAgent'],
    'sports':    ['OpportunityScoringAgent', 'TrendAnalysisAgent'],
    'betting':   ['OpportunityScoringAgent', 'ContrarianAgent'],
    'ai_tech':   ['TrendAnalysisAgent', 'ResearchAgent'],
    'legal':     ['ResearchAgent', 'ContentAuditAgent'],
    'career':    ['TrendAnalysisAgent', 'ResearchAgent'],
    'health':    ['ResearchAgent', 'ContentAuditAgent'],
    'education': ['ResearchAgent', 'ContentStrategyAgent'],
    'general':   ['ContentStrategyAgent', 'TrendAnalysisAgent'],
}

# Timeout ceiling for the entire review pipeline (seconds).
REVIEW_TIMEOUT_SECONDS = 90


class ContentReviewPanel:
    """
    Multi-agent content review panel.

    Orchestrates a 2-agent critique conversation to decide whether a blog
    post should be published, revised, or killed.
    """

    def __init__(self):
        self._domain_builder_instance = None
        self._spider_builder_instance = None
        self._orchestrator_instance = None

    # ------------------------------------------------------------------
    # Lazy-loaded dependencies
    # ------------------------------------------------------------------

    @property
    def _domain_builder(self):
        if self._domain_builder_instance is None:
            try:
                from core.services.domain_content_context import DomainContentContextBuilder
                self._domain_builder_instance = DomainContentContextBuilder()
            except ImportError:
                logger.warning("Session 961: Could not import DomainContentContextBuilder")
        return self._domain_builder_instance

    @property
    def _spider_builder(self):
        if self._spider_builder_instance is None:
            try:
                from core.services.spider_context_builder import get_spider_context_builder
                self._spider_builder_instance = get_spider_context_builder()
            except ImportError:
                logger.warning("Session 961: Could not import SpiderContextBuilder")
        return self._spider_builder_instance

    @property
    def _orchestrator(self):
        if self._orchestrator_instance is None:
            try:
                from core.conversation_orchestrator import ConversationOrchestrator
                self._orchestrator_instance = ConversationOrchestrator()
            except ImportError:
                logger.warning("Session 961: Could not import ConversationOrchestrator")
        return self._orchestrator_instance

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def review(
        self,
        content_data: Dict[str, Any],
        topic: str,
        tone: str = '',  # noqa: ARG002 - reserved for future panel context
        target_audience: str = '',  # noqa: ARG002 - reserved for future panel context
    ) -> ReviewResult:
        """
        Run *content_data* through a multi-agent critique panel.

        Returns a ReviewResult with a publish/revise/kill decision.
        On any failure the result falls back to ``decision='draft'``
        so the blog is still saved safely.
        """
        start = time.time()

        try:
            # Stage 1: Domain detection
            domain = self._detect_domain(content_data, topic)

            # Stage 2: Panel assembly
            panel = self._assemble_panel(domain)

            # Stage 3: Spider context
            spider_context, spider_used = self._get_spider_context(topic)

            # Stage 4: Critique conversation
            conversation = self._run_critique(content_data, topic, panel, spider_context)

            # Stage 5: Extract decision
            decision, confidence, mandate_dict = self._extract_decision(conversation)

            # Stage 6: Build review notes
            review_notes = self._build_review_notes(conversation)

            elapsed_ms = int((time.time() - start) * 1000)

            return ReviewResult(
                decision=decision,
                enhanced_content=None,
                review_notes=review_notes,
                confidence=confidence,
                panel_composition=[p['name'] for p in panel],
                spider_data_used=spider_used,
                mandate=mandate_dict,
                execution_time_ms=elapsed_ms,
            )

        except Exception as exc:
            elapsed_ms = int((time.time() - start) * 1000)
            logger.warning(f"Session 961: Review panel failed ({elapsed_ms}ms): {exc}")
            return ReviewResult(
                decision='draft',
                review_notes='Review panel unavailable',
                execution_time_ms=elapsed_ms,
            )

    # ------------------------------------------------------------------
    # Stage 1: Domain detection
    # ------------------------------------------------------------------

    def _detect_domain(self, content_data: Dict[str, Any], topic: str) -> str:
        """Detect the content domain using DomainContentContextBuilder."""
        if not self._domain_builder:
            return 'general'
        try:
            full_text = content_data.get('full_text', '')
            domain, _confidence = self._domain_builder.detect_domain(topic, full_text)
            return domain or 'general'
        except Exception as exc:
            logger.warning(f"Session 961: Domain detection failed: {exc}")
            return 'general'

    # ------------------------------------------------------------------
    # Stage 2: Panel assembly
    # ------------------------------------------------------------------

    def _assemble_panel(self, domain: str) -> List[Dict[str, str]]:
        """
        Assemble a 2-agent review panel.

        Always includes EditorAgent (structural reviewer) plus the first
        available domain specialist from DOMAIN_REVIEW_AGENTS.
        """
        candidates = DOMAIN_REVIEW_AGENTS.get(domain, DOMAIN_REVIEW_AGENTS['general'])
        expert = candidates[0] if candidates else 'ContentStrategyAgent'

        return [
            {'name': 'EditorAgent', 'type': 'EditorAgent'},
            {'name': expert, 'type': expert},
        ]

    # ------------------------------------------------------------------
    # Stage 3: Spider context
    # ------------------------------------------------------------------

    def _get_spider_context(self, topic: str) -> Tuple[str, bool]:
        """Fetch recent spider intelligence for the topic.

        Returns (context_string, was_spider_data_used).
        """
        if not self._spider_builder:
            return ('', False)
        try:
            context = self._spider_builder.build_context_for_agent(
                'ContentReviewPanel',
                f"Review blog about: {topic}",
                hours=48,
                max_trends=5,
            )
            summary = context.get('summary', '')
            return (summary, bool(summary))
        except Exception as exc:
            logger.warning(f"Session 961: Spider context failed: {exc}")
            return ('', False)

    # ------------------------------------------------------------------
    # Stage 4: Critique conversation
    # ------------------------------------------------------------------

    def _run_critique(
        self,
        content_data: Dict[str, Any],
        topic: str,
        panel: List[Dict[str, str]],
        spider_context: str,
    ) -> Dict[str, Any]:
        """Run a critique conversation between the two panel agents."""
        if not self._orchestrator:
            raise RuntimeError("ConversationOrchestrator unavailable")

        # Build the content brief
        title = content_data.get('title', topic)
        intro = content_data.get('intro', '')[:500]
        sections = content_data.get('sections', [])
        full_text = content_data.get('full_text', '')
        word_count = len(full_text.split()) if full_text else 0

        spider_block = f"\n\nSPIDER INTELLIGENCE:\n{spider_context[:1000]}" if spider_context else ""

        content_brief = (
            f"REVIEW THIS BLOG POST:\n"
            f"Title: {title}\n"
            f"Intro: {intro}\n"
            f"Sections: {len(sections)} sections\n"
            f"Word count: ~{word_count} words\n\n"
            f"FULL TEXT:\n{full_text[:3000]}"
            f"{spider_block}\n\n"
            f"CRITIQUE CRITERIA:\n"
            f"1. Are claims supported by data or sources?\n"
            f"2. Is the structure engaging (hook, flow, conclusion)?\n"
            f"3. Does it add value beyond generic advice?\n"
            f"4. Would you publish this on a professional platform?\n"
            f"5. What specific improvements would elevate this content?"
        )

        result = self._orchestrator.generate_conversation(
            agent1=panel[0],
            agent2=panel[1],
            topic=content_brief,
            conversation_type='critique',
            num_turns=4,
            objective="Decide whether to publish, revise, or kill this blog post",
            success_criteria=[
                "Identify at least 2 specific weaknesses",
                "Suggest concrete improvements",
                "Make a clear publish/revise/kill recommendation",
            ],
        )
        return result

    # ------------------------------------------------------------------
    # Stage 5: Extract decision
    # ------------------------------------------------------------------

    def _extract_decision(self, conversation: Dict[str, Any]) -> Tuple[str, float, Optional[Dict[str, Any]]]:
        """
        Extract the publish/revise/kill decision from the conversation.

        Checks execution_mandate first, then decision_summary, then
        scans the last few messages for keywords.

        Returns (decision, confidence, mandate_dict).
        """
        mandate_dict = conversation.get('execution_mandate')

        # Try execution mandate first (most authoritative)
        if mandate_dict:
            chosen = (mandate_dict.get('chosen_path', '') or '').upper()
            if 'PUBLISH' in chosen:
                return ('publish', 0.85, mandate_dict)
            if 'KILL' in chosen:
                return ('kill', 0.80, mandate_dict)
            if 'REVISE' in chosen:
                return ('revise', 0.75, mandate_dict)

        # Try decision_summary
        summary = conversation.get('decision_summary')
        if summary:
            decision_text = (summary.get('decision', '') or '').upper()
            if 'PUBLISH' in decision_text:
                return ('publish', 0.70, mandate_dict)
            if 'KILL' in decision_text:
                return ('kill', 0.65, mandate_dict)
            if 'REVISE' in decision_text:
                return ('revise', 0.60, mandate_dict)

        # Scan last messages for keywords
        messages = conversation.get('messages', [])
        if messages:
            last_text = ' '.join(
                (m.get('content', '') or '') for m in messages[-3:]
            ).upper()
            if 'PUBLISH' in last_text and 'KILL' not in last_text:
                return ('publish', 0.50, mandate_dict)
            if 'KILL' in last_text:
                return ('kill', 0.50, mandate_dict)

        # Default: revise (ambiguous outcome)
        return ('revise', 0.40, mandate_dict)

    # ------------------------------------------------------------------
    # Stage 6: Build review notes
    # ------------------------------------------------------------------

    def _build_review_notes(self, conversation: Dict[str, Any]) -> str:
        """Summarise the last few conversation messages into review notes."""
        messages = conversation.get('messages', [])
        if not messages:
            return 'No review conversation generated.'

        notes_parts = []
        for msg in messages[-4:]:
            agent = msg.get('agent', 'Unknown')
            content = (msg.get('content', '') or '')[:300]
            if content:
                notes_parts.append(f"[{agent}] {content}")

        return '\n\n'.join(notes_parts) if notes_parts else 'No substantive feedback.'
