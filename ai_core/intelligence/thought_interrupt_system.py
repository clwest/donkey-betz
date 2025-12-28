"""
🧠 Random Thought Interrupt System for Learning Loop
=====================================================

Implements probabilistic "did we forget X?" interrupts during agent reasoning cycles
to catch blind spots and ensure completeness. Based on human-like intrusive thoughts
that surface unfinished business or overlooked steps.

Architecture:
1. Trigger: Random probability check during reasoning cycles
2. Interrupt: Meta-prompt for reflection on missing/forgotten steps
3. Memory Hook: Cross-reference with past memory anchors
4. Reintegration: Feed concerns back into main planner

Usage:
    from ai_core.intelligence.thought_interrupt_system import ThoughtInterruptSystem

    interrupt_system = ThoughtInterruptSystem(interrupt_probability=0.15)

    # During agent execution
    if interrupt_system.should_trigger():
        reflection = await interrupt_system.generate_reflection(context, memory)
        if reflection:
            context.add_concerns(reflection)
"""

import random
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ThoughtInterrupt:
    """Represents a thought interrupt event"""
    id: str
    timestamp: datetime
    context_summary: str
    reflection_prompt: str
    concerns_raised: List[str]
    memory_anchors_triggered: List[str]
    confidence: float
    reintegrated: bool = False
    action_taken: Optional[str] = None


@dataclass
class MemoryAnchor:
    """Memory anchor for pattern matching"""
    id: str
    pattern_type: str  # "incomplete_task", "forgotten_step", "missed_validation"
    keywords: List[str]
    context_embedding: Optional[List[float]] = None
    relevance_score: float = 0.0
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


class ThoughtInterruptSystem:
    """
    Probabilistic thought interrupt system for learning loops

    Triggers random reflections during reasoning to catch blind spots:
    - "Wait, did we validate X?"
    - "Did we check Y?"
    - "What about Z?"
    """

    def __init__(
        self,
        interrupt_probability: float = 0.15,
        min_cycles_between_interrupts: int = 3,
        memory_lookback_limit: int = 50
    ):
        """
        Initialize thought interrupt system

        Args:
            interrupt_probability: Base probability (0-1) of triggering interrupt
            min_cycles_between_interrupts: Minimum cycles between interrupts
            memory_lookback_limit: How many past items to check in memory
        """
        self.interrupt_probability = interrupt_probability
        self.min_cycles_between = min_cycles_between_interrupts
        self.memory_lookback = memory_lookback_limit

        # State tracking
        self.cycle_count = 0
        self.cycles_since_last_interrupt = 0
        self.interrupt_history: List[ThoughtInterrupt] = []
        self.memory_anchors: List[MemoryAnchor] = []

        # Performance metrics
        self.total_interrupts = 0
        self.useful_interrupts = 0  # Led to action
        self.false_positives = 0    # No action needed

        logger.info(f"🧠 Thought Interrupt System initialized (p={interrupt_probability})")

    def should_trigger(self) -> bool:
        """
        Determine if an interrupt should trigger this cycle

        Returns:
            True if interrupt should fire
        """
        self.cycle_count += 1
        self.cycles_since_last_interrupt += 1

        # Don't interrupt too frequently
        if self.cycles_since_last_interrupt < self.min_cycles_between:
            return False

        # Probabilistic trigger
        return random.random() < self.interrupt_probability

    async def generate_reflection(
        self,
        context: Dict[str, Any],
        memory: Optional[Dict[str, Any]] = None
    ) -> Optional[ThoughtInterrupt]:
        """
        Generate a reflection/interrupt based on current context

        Args:
            context: Current reasoning context
            memory: Access to memory system for pattern matching

        Returns:
            ThoughtInterrupt if concerns identified, else None
        """
        logger.info("🤔 Thought interrupt triggered - generating reflection...")

        # Build reflection prompt
        reflection_prompt = self._build_reflection_prompt(context, memory)

        # Query relevant memory anchors
        triggered_anchors = await self._query_memory_anchors(context, memory)

        # Generate reflection using LLM
        concerns = await self._generate_concerns(reflection_prompt, context, triggered_anchors)

        if not concerns:
            logger.debug("✓ No concerns identified - continuing")
            self.false_positives += 1
            return None

        # Create interrupt record
        interrupt = ThoughtInterrupt(
            id=f"interrupt_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            context_summary=self._summarize_context(context),
            reflection_prompt=reflection_prompt,
            concerns_raised=concerns,
            memory_anchors_triggered=[a.id for a in triggered_anchors],
            confidence=self._calculate_confidence(concerns, triggered_anchors)
        )

        # Reset cycle counter
        self.cycles_since_last_interrupt = 0
        self.total_interrupts += 1
        self.interrupt_history.append(interrupt)

        logger.info(f"⚠️ Reflection raised {len(concerns)} concern(s)")
        return interrupt

    def _build_reflection_prompt(
        self,
        context: Dict[str, Any],
        memory: Optional[Dict[str, Any]]
    ) -> str:
        """Build meta-prompt for reflection"""

        context_summary = self._summarize_context(context)

        prompt = f"""
Pause and reflect: What steps might have been missed, forgotten, or assumed in this process so far?

Current context: {context_summary}

Consider:
- Validations that should have been performed
- Dependencies that might have been overlooked
- Edge cases that weren't checked
- Prerequisites that might be missing
- Similar past scenarios that had issues

Past relevant memory: {self._format_memory_context(memory)}

List any genuine concerns about missing steps or overlooked items.
Return empty list if everything appears complete.
"""
        return prompt

    async def _query_memory_anchors(
        self,
        context: Dict[str, Any],
        memory: Optional[Dict[str, Any]]
    ) -> List[MemoryAnchor]:
        """
        Query memory for relevant anchors based on context

        Returns:
            List of triggered memory anchors
        """
        triggered = []

        context_text = str(context).lower()

        for anchor in self.memory_anchors:
            # Check if keywords appear in context
            matches = sum(1 for kw in anchor.keywords if kw.lower() in context_text)

            if matches > 0:
                anchor.relevance_score = matches / len(anchor.keywords)
                anchor.last_triggered = datetime.now()
                anchor.trigger_count += 1
                triggered.append(anchor)

        # Sort by relevance
        triggered.sort(key=lambda a: a.relevance_score, reverse=True)

        return triggered[:5]  # Top 5 most relevant

    async def _generate_concerns(
        self,
        prompt: str,
        context: Dict[str, Any],
        anchors: List[MemoryAnchor]
    ) -> List[str]:
        """
        Generate list of concerns using reflection

        In a real implementation, this would call an LLM.
        For now, we use heuristics based on context and anchors.
        """
        concerns = []

        # Check for common oversight patterns
        context_str = str(context).lower()

        # Pattern 1: Action taken without validation
        if "execute" in context_str or "apply" in context_str:
            if "validate" not in context_str and "verify" not in context_str:
                concerns.append("Action may be taken without validation - consider adding verification step")

        # Pattern 2: Data transformation without error handling
        if "transform" in context_str or "process" in context_str:
            if "error" not in context_str and "exception" not in context_str:
                concerns.append("Data processing may lack error handling")

        # Pattern 3: User interaction without feedback
        if "user" in context_str and ("send" in context_str or "notify" in context_str):
            if "feedback" not in context_str and "confirm" not in context_str:
                concerns.append("User interaction may lack feedback mechanism")

        # Pattern 4: Memory anchors suggest similar past issues
        for anchor in anchors:
            if anchor.trigger_count > 3:  # Frequently triggered = recurring issue
                concerns.append(f"Recurring pattern detected: {anchor.pattern_type} - review {anchor.keywords[0]}")

        # Pattern 5: Missing completion checks
        if "step" in context_str or "task" in context_str:
            if "complete" not in context_str and "done" not in context_str:
                concerns.append("Task tracking may be missing completion checks")

        return concerns[:3]  # Limit to 3 most important

    def _summarize_context(self, context: Dict[str, Any]) -> str:
        """Create human-readable context summary"""
        summary_parts = []

        if 'current_task' in context:
            summary_parts.append(f"Task: {context['current_task']}")

        if 'steps_completed' in context:
            summary_parts.append(f"Completed: {len(context.get('steps_completed', []))} steps")

        if 'agent_id' in context:
            summary_parts.append(f"Agent: {context['agent_id']}")

        return " | ".join(summary_parts) if summary_parts else "No context available"

    def _format_memory_context(self, memory: Optional[Dict[str, Any]]) -> str:
        """Format memory for prompt inclusion"""
        if not memory:
            return "No relevant past memory"

        # Extract recent similar situations
        if 'recent_similar' in memory:
            return f"Similar past cases: {len(memory['recent_similar'])} found"

        return "Memory available but no direct matches"

    def _calculate_confidence(
        self,
        concerns: List[str],
        anchors: List[MemoryAnchor]
    ) -> float:
        """Calculate confidence in the reflection"""

        # Base confidence from number of concerns
        base = min(len(concerns) / 3, 1.0)

        # Boost from memory anchor support
        anchor_boost = min(len(anchors) * 0.1, 0.3)

        return min(base + anchor_boost, 1.0)

    def reintegrate_interrupt(
        self,
        interrupt: ThoughtInterrupt,
        action_taken: str
    ):
        """
        Mark interrupt as reintegrated with action taken

        Args:
            interrupt: The interrupt to reintegrate
            action_taken: Description of action taken
        """
        interrupt.reintegrated = True
        interrupt.action_taken = action_taken

        if action_taken != "no_action":
            self.useful_interrupts += 1

        logger.info(f"✅ Interrupt reintegrated: {action_taken}")

    def add_memory_anchor(
        self,
        pattern_type: str,
        keywords: List[str],
        context_embedding: Optional[List[float]] = None
    ) -> MemoryAnchor:
        """
        Add a new memory anchor for pattern matching

        Args:
            pattern_type: Type of pattern (e.g., "incomplete_task")
            keywords: Keywords to match against
            context_embedding: Optional embedding vector

        Returns:
            Created MemoryAnchor
        """
        anchor = MemoryAnchor(
            id=f"anchor_{len(self.memory_anchors)}",
            pattern_type=pattern_type,
            keywords=keywords,
            context_embedding=context_embedding
        )

        self.memory_anchors.append(anchor)
        logger.debug(f"📌 Added memory anchor: {pattern_type} ({len(keywords)} keywords)")

        return anchor

    def get_interrupt_stats(self) -> Dict[str, Any]:
        """Get statistics on interrupt performance"""

        accuracy = (self.useful_interrupts / self.total_interrupts * 100) if self.total_interrupts > 0 else 0

        return {
            'total_cycles': self.cycle_count,
            'total_interrupts': self.total_interrupts,
            'useful_interrupts': self.useful_interrupts,
            'false_positives': self.false_positives,
            'accuracy_percentage': round(accuracy, 2),
            'interrupt_probability': self.interrupt_probability,
            'active_memory_anchors': len(self.memory_anchors),
            'recent_interrupts': [
                {
                    'timestamp': i.timestamp.isoformat(),
                    'concerns': len(i.concerns_raised),
                    'reintegrated': i.reintegrated,
                    'action': i.action_taken
                }
                for i in self.interrupt_history[-5:]
            ]
        }


# Global instance
_interrupt_system = None


def get_interrupt_system() -> ThoughtInterruptSystem:
    """Get or create global interrupt system"""
    global _interrupt_system
    if _interrupt_system is None:
        _interrupt_system = ThoughtInterruptSystem()
    return _interrupt_system


# Example usage in learning loop
async def learning_loop_with_interrupts(context, memory):
    """
    Example integration of thought interrupts into learning loop
    """
    interrupt_system = get_interrupt_system()

    steps = []
    while not task_complete(context):
        step = generate_next_step(context)
        steps.append(step)
        context.update(step)

        # Random thought interrupt (15% chance)
        if interrupt_system.should_trigger():
            reflection = await interrupt_system.generate_reflection(context, memory)
            if reflection:
                steps.append({"interrupt": reflection})

                # Process concerns
                for concern in reflection.concerns_raised:
                    new_step = address_concern(concern, context)
                    steps.append(new_step)
                    context.update(new_step)

                # Mark as reintegrated
                interrupt_system.reintegrate_interrupt(
                    reflection,
                    f"Added {len(reflection.concerns_raised)} concern steps"
                )

    return steps


def task_complete(context):
    """Check if task is complete"""
    return context.get('status') == 'complete'


def generate_next_step(context):
    """Generate next step in process"""
    return {'action': 'next_step', 'data': {}}


def address_concern(concern, context):
    """Address a concern raised by interrupt"""
    return {'action': 'address_concern', 'concern': concern}
