"""
Training Agents Package - Clean Architecture
=============================================

Session 280: Phase 3 - Agent Architecture Unification

Training agents for character training and LoRA generation.

Usage:
    from core.agents.training import CharacterTrainingAgent, TrainedCreationAgent

    agent = CharacterTrainingAgent(user=request.user)
    result = agent.execute(
        task="Train a new character model with these images",
        context={'name': 'my-character', 'trigger_word': 'MYCHAR'},
        scifi_context={},
        spider_context={}
    )
"""

from core.agents.training.character_training_agent import CharacterTrainingAgent
from core.agents.training.trained_creation_agent import TrainedCreationAgent

__all__ = [
    'CharacterTrainingAgent',
    'TrainedCreationAgent',
]
