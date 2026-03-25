"""
Context Budget Manager Service
Session 806: Token tracking and allocation for Personal Assistant context.

This service:
1. Tracks token usage per context section using tiktoken
2. Enforces budget limits per section priority
3. Provides observability into token allocation
4. Enables smart truncation when budget is exceeded

The goal is to reduce context token usage from 6,000-10,000 tokens
down to ~1,300 tokens while preserving critical information.
"""

import logging
from typing import Dict, Any, Optional, List, Union
try:
    import tiktoken
    from tiktoken import Encoding
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    Encoding = None  # type: ignore
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class SectionPriority(Enum):
    """Priority levels for context sections."""
    CRITICAL = 1  # Never truncate, never skip (system_prompt_core, user_message)
    # Session 949: Reserved tier for risk-aware RAG - these are protected like CRITICAL
    RESERVED = 2  # Reserved budget for critical/incident docs - never skip
    HIGH = 3      # Truncate if needed, never skip (conversation_history, project_context)
    MEDIUM = 4    # Truncate or skip if budget exceeded (spider, learning, workspace)
    LOW = 5       # Skip first when budget is tight (advisor, proactive, operator)


@dataclass
class SectionBudget:
    """Budget configuration for a single context section."""
    name: str
    priority: SectionPriority
    max_tokens: int
    current_tokens: int = 0
    content: str = ""
    was_truncated: bool = False
    was_skipped: bool = False


@dataclass
class BudgetReport:
    """Report on token budget usage."""
    total_budget: int
    total_used: int
    budget_remaining: int
    over_budget: bool
    sections: Dict[str, Dict[str, Any]]
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SectionConfig:
    """Configuration for a context section."""
    priority: SectionPriority
    max_tokens: int


class ContextBudgetManager:
    """
    Session 806: Manages token budgets for context sections.

    Usage:
        from core.services.context_budget_manager import get_context_budget_manager

        manager = get_context_budget_manager()

        # Register sections with their budgets
        manager.start_request()
        manager.set_section('system_prompt_core', content, priority=SectionPriority.CRITICAL)
        manager.set_section('user_message', user_msg, priority=SectionPriority.CRITICAL)
        manager.set_section('spider_intelligence', spider_data, priority=SectionPriority.MEDIUM)

        # Get the budgeted context
        final_context = manager.build_budgeted_context()
        report = manager.get_budget_report()
    """

    # Default budget allocation (4,000 tokens total target)
    DEFAULT_BUDGETS: Dict[str, SectionConfig] = {
        'system_prompt_core': SectionConfig(SectionPriority.CRITICAL, 500),
        'user_message': SectionConfig(SectionPriority.CRITICAL, 500),
        # Session 949: Reserved sections for risk-aware RAG
        # These are protected - critical docs that should never be missed
        'critical_docs': SectionConfig(SectionPriority.RESERVED, 300),
        'incident_docs': SectionConfig(SectionPriority.RESERVED, 200),
        'audit_findings': SectionConfig(SectionPriority.RESERVED, 150),
        # Standard sections
        'conversation_history': SectionConfig(SectionPriority.HIGH, 800),
        'project_context': SectionConfig(SectionPriority.HIGH, 400),
        'spider_intelligence': SectionConfig(SectionPriority.MEDIUM, 600),
        'learning_patterns': SectionConfig(SectionPriority.MEDIUM, 300),
        'pending_decisions': SectionConfig(SectionPriority.HIGH, 200),
        'workspace_context': SectionConfig(SectionPriority.MEDIUM, 200),
        'advisor_context': SectionConfig(SectionPriority.LOW, 200),
        'proactive_intelligence': SectionConfig(SectionPriority.LOW, 200),
        'operator_mode': SectionConfig(SectionPriority.LOW, 100),
    }

    # Total budget target
    TOTAL_BUDGET = 4000

    # Feature flags
    ENABLE_ENFORCEMENT = True   # Truncate/skip sections that exceed budget
    ENABLE_LOGGING = True       # Log all budget usage

    def __init__(self, encoding_name: str = "cl100k_base"):
        """
        Initialize the budget manager.

        Args:
            encoding_name: tiktoken encoding to use (default is GPT-4/Claude compatible)
        """
        self._encoder: Optional[Any] = None
        self._use_approximate: bool = False
        self._encoding_name = encoding_name
        self._sections: Dict[str, SectionBudget] = {}
        self._request_id: Optional[str] = None
        self._warnings: List[str] = []

    def _ensure_encoder(self) -> None:
        """Lazy-load tiktoken encoder."""
        if self._encoder is not None or self._use_approximate:
            return

        if not TIKTOKEN_AVAILABLE:
            logger.warning("tiktoken not installed, using approximate token counting")
            self._use_approximate = True
            return

        try:
            self._encoder = tiktoken.get_encoding(self._encoding_name)
            logger.debug(f"Loaded tiktoken encoder: {self._encoding_name}")
        except Exception as e:
            logger.warning(f"Failed to load tiktoken: {e}, using approximate")
            self._use_approximate = True

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken or approximation.

        Args:
            text: Text to count tokens for

        Returns:
            Token count
        """
        if not text:
            return 0

        self._ensure_encoder()

        if self._use_approximate or self._encoder is None:
            # Approximate: ~4 chars per token for English
            return len(text) // 4

        try:
            return len(self._encoder.encode(text))
        except Exception as e:
            logger.debug(f"Token counting failed: {e}, using approximation")
            return len(text) // 4

    def start_request(self, request_id: Optional[str] = None) -> None:
        """
        Start tracking a new request.

        Args:
            request_id: Optional identifier for logging
        """
        self._sections = {}
        self._warnings = []
        self._request_id = request_id or datetime.now().strftime("%H%M%S")

        if self.ENABLE_LOGGING:
            logger.info(f"📊 [Session 806] Budget tracking started for request {self._request_id}")

    def set_section(
        self,
        name: str,
        content: str,
        priority: Optional[SectionPriority] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Register a context section with its content.

        Args:
            name: Section name
            content: Section content
            priority: Override priority (uses default if not provided)
            max_tokens: Override max tokens (uses default if not provided)

        Returns:
            Dict with section token usage info
        """
        # Get defaults
        defaults = self.DEFAULT_BUDGETS.get(
            name,
            SectionConfig(SectionPriority.MEDIUM, 300)
        )

        actual_priority = priority if priority is not None else defaults.priority
        actual_max = max_tokens if max_tokens is not None else defaults.max_tokens

        # Count tokens
        token_count = self.count_tokens(content)

        # Create section budget
        section = SectionBudget(
            name=name,
            priority=actual_priority,
            max_tokens=actual_max,
            current_tokens=token_count,
            content=content,
            was_truncated=False,
            was_skipped=False
        )

        # Check if over section budget
        if token_count > actual_max:
            if self.ENABLE_ENFORCEMENT:
                # Truncate content
                section.content = self._truncate_to_budget(content, actual_max)
                section.current_tokens = self.count_tokens(section.content)
                section.was_truncated = True
                self._warnings.append(
                    f"Section '{name}' truncated: {token_count} -> {section.current_tokens} tokens"
                )
            else:
                # Just log the overage
                self._warnings.append(
                    f"Section '{name}' over budget: {token_count}/{actual_max} tokens"
                )

        self._sections[name] = section

        return {
            'name': name,
            'tokens': section.current_tokens,
            'budget': actual_max,
            'over_budget': token_count > actual_max,
            'truncated': section.was_truncated,
        }

    def _truncate_to_budget(self, content: str, max_tokens: int) -> str:
        """
        Truncate content to fit within token budget.

        Args:
            content: Content to truncate
            max_tokens: Maximum tokens allowed

        Returns:
            Truncated content with ellipsis
        """
        self._ensure_encoder()

        if self._use_approximate or self._encoder is None:
            # Approximate truncation
            max_chars = max_tokens * 4
            if len(content) > max_chars:
                return content[:max_chars - 10] + "... [truncated]"
            return content

        try:
            tokens = self._encoder.encode(content)
            if len(tokens) <= max_tokens:
                return content

            # Keep first max_tokens-10 tokens and add truncation marker
            truncated_tokens = tokens[:max_tokens - 10]
            truncated_text = self._encoder.decode(truncated_tokens)
            return truncated_text + "... [truncated]"
        except Exception as e:
            logger.warning(f"Truncation failed: {e}")
            max_chars = max_tokens * 4
            return content[:max_chars - 10] + "... [truncated]"

    def get_total_tokens(self) -> int:
        """Get total tokens across all sections."""
        return sum(s.current_tokens for s in self._sections.values())

    def get_budget_remaining(self) -> int:
        """Get remaining budget."""
        return self.TOTAL_BUDGET - self.get_total_tokens()

    def is_over_budget(self) -> bool:
        """Check if total is over budget."""
        return self.get_total_tokens() > self.TOTAL_BUDGET

    def enforce_budget(self) -> List[str]:
        """
        Enforce the total budget by skipping/truncating sections.

        This is called when ENABLE_ENFORCEMENT is True and we need to
        fit within the total budget.

        Returns:
            List of actions taken
        """
        actions = []

        if not self.is_over_budget():
            return actions

        # Sort sections by priority (lowest first - these get cut)
        sections_by_priority = sorted(
            self._sections.values(),
            key=lambda s: (-s.priority.value, s.current_tokens),
            reverse=True  # Process lowest priority first
        )

        tokens_to_cut = self.get_total_tokens() - self.TOTAL_BUDGET

        for section in sections_by_priority:
            if tokens_to_cut <= 0:
                break

            if section.priority == SectionPriority.CRITICAL:
                # Never cut critical sections
                continue

            if section.priority == SectionPriority.RESERVED:
                # Session 949: Never cut reserved sections (risk-aware RAG)
                # These contain critical docs, incident reports, and audit findings
                continue

            if section.priority == SectionPriority.LOW:
                # Skip LOW priority sections entirely
                tokens_to_cut -= section.current_tokens
                section.content = ""
                section.current_tokens = 0
                section.was_skipped = True
                actions.append(f"Skipped '{section.name}' (saved {section.current_tokens} tokens)")
                continue

            if section.priority == SectionPriority.MEDIUM:
                # Truncate MEDIUM priority sections to half budget
                half_budget = section.max_tokens // 2
                if section.current_tokens > half_budget:
                    old_tokens = section.current_tokens
                    section.content = self._truncate_to_budget(section.content, half_budget)
                    section.current_tokens = self.count_tokens(section.content)
                    section.was_truncated = True
                    tokens_saved = old_tokens - section.current_tokens
                    tokens_to_cut -= tokens_saved
                    actions.append(
                        f"Truncated '{section.name}' from {old_tokens} to {section.current_tokens} tokens"
                    )

        return actions

    def build_budgeted_context(self) -> str:
        """
        Build the final context string from budgeted sections.

        Returns:
            Combined context string
        """
        if self.ENABLE_ENFORCEMENT and self.is_over_budget():
            actions = self.enforce_budget()
            for action in actions:
                logger.info(f"📊 [Session 806] Budget action: {action}")

        # Combine sections in order of priority
        ordered_sections = sorted(
            self._sections.values(),
            key=lambda s: s.priority.value
        )

        parts = []
        for section in ordered_sections:
            if section.content and not section.was_skipped:
                parts.append(section.content)

        return "\n\n".join(parts)

    def get_budget_report(self) -> BudgetReport:
        """
        Get a detailed budget report.

        Returns:
            BudgetReport with all usage details
        """
        total_used = self.get_total_tokens()

        sections_report = {}
        for name, section in self._sections.items():
            sections_report[name] = {
                'tokens': section.current_tokens,
                'budget': section.max_tokens,
                'priority': section.priority.value,
                'priority_name': section.priority.name,
                'percent_used': round(section.current_tokens / section.max_tokens * 100, 1)
                    if section.max_tokens > 0 else 0,
                'over_budget': section.current_tokens > section.max_tokens,
                'was_truncated': section.was_truncated,
                'was_skipped': section.was_skipped,
            }

        report = BudgetReport(
            total_budget=self.TOTAL_BUDGET,
            total_used=total_used,
            budget_remaining=self.TOTAL_BUDGET - total_used,
            over_budget=total_used > self.TOTAL_BUDGET,
            sections=sections_report,
            warnings=self._warnings.copy(),
        )

        if self.ENABLE_LOGGING:
            self._log_budget_report(report)

        return report

    def _log_budget_report(self, report: BudgetReport) -> None:
        """Log the budget report."""
        # Summary line
        status = "⚠️ OVER BUDGET" if report.over_budget else "✅ Within budget"
        logger.info(
            f"📊 [Session 806] Budget Report [{self._request_id}]: "
            f"{report.total_used}/{report.total_budget} tokens ({status})"
        )

        # Per-section breakdown if over budget or close to limit
        if report.over_budget or report.total_used > report.total_budget * 0.8:
            for name, data in sorted(
                report.sections.items(),
                key=lambda x: -x[1]['tokens']
            ):
                flags = []
                if data['over_budget']:
                    flags.append("OVER")
                if data['was_truncated']:
                    flags.append("TRUNC")
                if data['was_skipped']:
                    flags.append("SKIP")
                flag_str = f" [{','.join(flags)}]" if flags else ""

                logger.info(
                    f"  - {name}: {data['tokens']}/{data['budget']} "
                    f"({data['percent_used']}%){flag_str}"
                )

        # Warnings
        for warning in report.warnings:
            logger.warning(f"  ⚠️ {warning}")

    def get_section_tokens(self, name: str) -> int:
        """Get tokens for a specific section."""
        section = self._sections.get(name)
        return section.current_tokens if section else 0

    def get_sections_by_priority(self, priority: SectionPriority) -> List[str]:
        """Get section names by priority level."""
        return [
            name for name, section in self._sections.items()
            if section.priority == priority
        ]

    @classmethod
    def set_enforcement(cls, enabled: bool) -> None:
        """Enable or disable budget enforcement globally."""
        cls.ENABLE_ENFORCEMENT = enabled
        logger.info(f"📊 [Session 806] Budget enforcement {'enabled' if enabled else 'disabled'}")

    @classmethod
    def set_logging(cls, enabled: bool) -> None:
        """Enable or disable budget logging globally."""
        cls.ENABLE_LOGGING = enabled


# Singleton instance
_context_budget_manager: Optional[ContextBudgetManager] = None


def get_context_budget_manager() -> ContextBudgetManager:
    """Get the singleton ContextBudgetManager instance."""
    global _context_budget_manager
    if _context_budget_manager is None:
        _context_budget_manager = ContextBudgetManager()
    return _context_budget_manager
