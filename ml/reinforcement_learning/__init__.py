"""
Reinforcement Learning Package
==============================

Session 680: Phase 4 Reinforcement Learning

Contains:
- rl_decision_optimizer.py: RL model for decision optimization

Note: Imports are lazy to avoid loading torch (~500MB) at package import time.
Use: from ml.reinforcement_learning.rl_decision_optimizer import get_rl_optimizer
"""


def __getattr__(name):
    """Lazy import to avoid loading torch at package import time."""
    if name in ('RLDecisionOptimizer', 'DecisionPrediction', 'get_rl_optimizer'):
        from .rl_decision_optimizer import RLDecisionOptimizer, DecisionPrediction, get_rl_optimizer
        return {'RLDecisionOptimizer': RLDecisionOptimizer,
                'DecisionPrediction': DecisionPrediction,
                'get_rl_optimizer': get_rl_optimizer}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    'RLDecisionOptimizer',
    'DecisionPrediction',
    'get_rl_optimizer',
]
