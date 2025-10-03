"""
Self-Development Module
Autonomous system improvement and learning orchestration

Components:
- AgentCollaborationOptimizer: Optimizes agent teamwork
- LearningOrchestrator: Connects all learning systems
- SelfAwarenessEngine: System introspection and self-knowledge

This module enables:
- Autonomous improvement cycles
- Agent-to-agent learning
- System self-awareness
- Optimal team formation
- Performance self-assessment
"""

from .agent_collaboration_optimizer import collaboration_optimizer
from .learning_orchestrator import learning_orchestrator, trigger_learning_cycle
from .self_awareness_engine import self_awareness

__all__ = [
    'collaboration_optimizer',
    'learning_orchestrator',
    'trigger_learning_cycle',
    'self_awareness'
]
