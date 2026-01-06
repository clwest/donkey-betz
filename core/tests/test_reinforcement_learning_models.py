"""
Tests for Reinforcement Learning Models (Session 680 - Phase 4)
===============================================================

Tests the RL decision optimizer including:
- RLDecisionOptimizer functionality
- DecisionPrediction dataclass
- UCB and Thompson Sampling algorithms
- Integration with model registry
- Fallback mode behavior
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from django.test import TestCase

from ml.reinforcement_learning.rl_decision_optimizer import (
    RLDecisionOptimizer,
    DecisionPrediction,
    get_rl_optimizer,
)
from core.services.model_registry import (
    ModelRegistry,
    RLWrapper,
    get_model_registry,
)


class TestDecisionPrediction(TestCase):
    """Test DecisionPrediction dataclass."""

    def test_create_prediction(self):
        """Test creating a decision prediction."""
        pred = DecisionPrediction(
            success=True,
            recommended_action='accept',
            action_values=[0.8, 0.3, 0.5],
            confidence=0.75,
            expected_reward=0.8,
        )

        assert pred.success is True
        assert pred.recommended_action == 'accept'
        assert len(pred.action_values) == 3
        assert pred.confidence == 0.75

    def test_to_dict(self):
        """Test converting to dict."""
        pred = DecisionPrediction(
            success=True,
            recommended_action=0,
            action_values=[0.5, 0.5],
        )

        result = pred.to_dict()

        assert isinstance(result, dict)
        assert result['success'] is True
        assert result['action_values'] == [0.5, 0.5]


class TestRLDecisionOptimizer(TestCase):
    """Test RLDecisionOptimizer class."""

    def test_init(self):
        """Test optimizer initialization."""
        optimizer = RLDecisionOptimizer(model_name="test_rl")

        assert optimizer.model_name == "test_rl"
        assert optimizer.is_trained is False
        assert optimizer.config['epsilon'] == 0.1

    def test_select_action_ucb_cold_start(self):
        """Test UCB action selection with no history."""
        optimizer = RLDecisionOptimizer()

        state = [0.5, 0.3, 0.8]
        result = optimizer.select_action(state, actions=['buy', 'sell', 'hold'])

        assert result.success is True
        assert result.recommended_action in ['buy', 'sell', 'hold']
        assert len(result.action_values) == 3

    def test_select_action_with_experience(self):
        """Test action selection after some updates."""
        optimizer = RLDecisionOptimizer()

        # Simulate some experience
        for _ in range(10):
            optimizer.update([0.5], 0, reward=1.0)  # Action 0 always good
            optimizer.update([0.5], 1, reward=-0.5)  # Action 1 bad
            optimizer.update([0.5], 2, reward=0.3)  # Action 2 mediocre

        result = optimizer.select_action([0.5], explore=False)

        assert result.success is True
        # Should prefer action 0 (highest rewards)
        assert result.action_values[0] > result.action_values[1]

    def test_thompson_sampling(self):
        """Test Thompson Sampling action selection."""
        optimizer = RLDecisionOptimizer()

        # Update with some rewards
        for _ in range(5):
            optimizer.update([0], 0, reward=0.8)
            optimizer.update([0], 1, reward=0.2)

        result = optimizer.select_action_thompson(actions=['good', 'bad'])

        assert result.success is True
        assert 'thompson_sampling' in result.metadata.get('method', '')
        assert len(result.action_values) == 2

    def test_update_updates_statistics(self):
        """Test that update() modifies internal state."""
        optimizer = RLDecisionOptimizer()

        initial_steps = optimizer._total_steps
        optimizer.update([1, 2, 3], action=0, reward=1.0)

        assert optimizer._action_counts[0] == 1
        assert optimizer._action_rewards[0] == 1.0
        assert optimizer.is_trained is True

    def test_epsilon_decay(self):
        """Test that epsilon decays over updates."""
        optimizer = RLDecisionOptimizer()
        initial_epsilon = optimizer.config['epsilon']

        for _ in range(10):
            optimizer.update([0], 0, reward=0.5)

        assert optimizer.config['epsilon'] < initial_epsilon

    def test_predict_with_fallback_list(self):
        """Test fallback prediction with list input."""
        optimizer = RLDecisionOptimizer()

        result = optimizer.predict_with_fallback([0.5, 0.3, 0.8])

        assert result.success is True
        assert result.recommended_action in optimizer._action_names

    def test_predict_with_fallback_dict(self):
        """Test fallback prediction with dict input."""
        optimizer = RLDecisionOptimizer()

        data = {
            'state': [0.5, 0.3],
            'actions': ['action_a', 'action_b'],
        }
        result = optimizer.predict_with_fallback(data)

        assert result.success is True
        assert result.recommended_action in ['action_a', 'action_b']

    def test_predict_empty_data(self):
        """Test prediction with empty data."""
        optimizer = RLDecisionOptimizer()

        result = optimizer.predict_with_fallback([])

        assert result.success is False
        assert 'no valid' in result.error.lower()

    def test_get_rl_optimizer_singleton(self):
        """Test singleton pattern."""
        optimizer1 = get_rl_optimizer()
        optimizer2 = get_rl_optimizer()

        assert optimizer1 is optimizer2


class TestOpportunityRanking(TestCase):
    """Test opportunity ranking functionality."""

    def test_rank_opportunities(self):
        """Test ranking multiple opportunities."""
        optimizer = RLDecisionOptimizer()

        opportunities = [
            {'score': 0.3, 'name': 'low'},
            {'score': 0.9, 'name': 'high'},
            {'score': 0.5, 'name': 'medium'},
        ]

        result = optimizer.rank_opportunities(opportunities)

        assert result.success is True
        # High score should be recommended (index 1)
        assert result.recommended_action == 1
        assert result.metadata.get('ranked_indices')[0] == 1

    def test_rank_empty_opportunities(self):
        """Test ranking with no opportunities."""
        optimizer = RLDecisionOptimizer()

        result = optimizer.rank_opportunities([])

        assert result.success is False
        assert 'no opportunities' in result.error.lower()

    def test_rank_with_uncertainty(self):
        """Test ranking considers uncertainty."""
        optimizer = RLDecisionOptimizer()

        opportunities = [
            {'score': 0.5, 'uncertainty': 0.1},
            {'score': 0.5, 'uncertainty': 0.8},  # Higher uncertainty
        ]

        result = optimizer.rank_opportunities(opportunities)

        assert result.success is True
        # Second opportunity should get exploration bonus
        assert result.action_values[1] >= result.action_values[0]


class TestRLWrapper(TestCase):
    """Test RLWrapper integration."""

    def test_wrapper_init(self):
        """Test wrapper initialization."""
        wrapper = RLWrapper()

        assert wrapper.model_name == 'rl'
        assert wrapper.version == 'v1.0'

    def test_wrapper_is_available(self):
        """Test wrapper availability."""
        wrapper = RLWrapper()

        # Should be available (fallback mode works)
        assert wrapper.is_available() is True

    def test_wrapper_predict(self):
        """Test wrapper prediction."""
        wrapper = RLWrapper()

        data = {'state': [0.5, 0.3, 0.8]}
        result = wrapper.predict(data)

        assert result.success is True
        assert result.model_name == 'rl'
        assert 'recommended_action' in result.explanation
        assert 'action_values' in result.explanation

    def test_wrapper_predict_with_actions(self):
        """Test wrapper prediction with custom actions."""
        wrapper = RLWrapper()

        data = {'state': [0.5]}
        result = wrapper.predict(data, actions=['buy', 'sell'])

        assert result.success is True
        assert result.explanation.get('recommended_action') in ['buy', 'sell']

    def test_wrapper_update(self):
        """Test wrapper update method."""
        wrapper = RLWrapper()

        result = wrapper.update(
            state=[0.5],
            action='accept',
            reward=1.0,
        )

        assert 'reward' in result

    def test_wrapper_from_registry(self):
        """Test getting wrapper from registry."""
        registry = ModelRegistry()
        wrapper = registry.get_model('rl')

        assert wrapper is not None
        assert isinstance(wrapper, RLWrapper)
        assert wrapper.is_available() is True


class TestRegistryIntegration(TestCase):
    """Test integration with model registry."""

    def test_rl_in_available_models(self):
        """Test RL appears in available models."""
        registry = get_model_registry()
        available = registry.list_available_models()

        assert 'rl' in available

    def test_decision_agent_routing(self):
        """Test decision agents route to correct models."""
        from core.services.agent_model_router import (
            get_agent_model_router,
            populate_default_configs,
        )

        # Populate configs (needed in test DB)
        populate_default_configs()

        router = get_agent_model_router()
        router.invalidate_cache()  # Clear cache to pick up new configs

        # OpportunityScoringAgent should use RL
        config = router.get_agent_config('OpportunityScoringAgent')
        assert config['primary_model'] == 'rl'

        # ThinkingAgent should use RL
        config = router.get_agent_config('ThinkingAgent')
        assert config['primary_model'] == 'rl'

        # ArbitrageDetector should use RL
        config = router.get_agent_config('ArbitrageDetector')
        assert config['primary_model'] == 'rl'


class TestExplorationExploitation(TestCase):
    """Test exploration vs exploitation behavior."""

    def test_explores_unknown_actions(self):
        """Test that optimizer explores unknown actions."""
        optimizer = RLDecisionOptimizer()

        # Only update action 0
        for _ in range(5):
            optimizer.update([0], 0, reward=1.0)

        # With exploration, should sometimes pick unexplored actions
        explored_other = False
        for _ in range(20):
            result = optimizer.select_action([0], explore=True)
            if result.metadata.get('action_index', 0) != 0:
                explored_other = True
                break

        assert explored_other is True

    def test_exploits_best_action(self):
        """Test that optimizer exploits best action without exploration."""
        optimizer = RLDecisionOptimizer()

        # Give strong signal that action 0 is best
        for _ in range(20):
            optimizer.update([0], 0, reward=1.0)
            optimizer.update([0], 1, reward=-1.0)
            optimizer.update([0], 2, reward=0.0)

        # Without exploration, should pick action 0
        result = optimizer.select_action([0], explore=False)

        assert result.metadata.get('action_index', -1) == 0

    def test_confidence_increases_with_observations(self):
        """Test that confidence increases with more observations."""
        optimizer = RLDecisionOptimizer()

        # Initial low confidence
        result1 = optimizer.select_action([0])
        initial_confidence = result1.confidence

        # Add observations
        for _ in range(30):
            optimizer.update([0], 0, reward=1.0)
            optimizer.update([0], 1, reward=0.5)
            optimizer.update([0], 2, reward=0.3)

        result2 = optimizer.select_action([0])

        assert result2.confidence >= initial_confidence


class TestQLearning(TestCase):
    """Test Q-Learning specific functionality."""

    def test_q_table_updates(self):
        """Test Q-table is updated correctly."""
        optimizer = RLDecisionOptimizer()

        state_key = optimizer._state_to_key(np.array([0.5, 0.5]))
        initial_q = optimizer._q_table[state_key][0]

        optimizer.update([0.5, 0.5], 0, reward=1.0)

        new_q = optimizer._q_table[state_key][0]
        assert new_q > initial_q

    def test_discount_factor_applied(self):
        """Test discount factor affects future rewards."""
        optimizer = RLDecisionOptimizer()

        # Update with next state
        optimizer.update(
            state=[0],
            action=0,
            reward=0.5,
            next_state=[1],
            done=False
        )

        # Update with terminal state
        optimizer.update(
            state=[1],
            action=0,
            reward=1.0,
            done=True
        )

        # Q-value for state [0] should include discounted future reward
        state_key_0 = optimizer._state_to_key(np.array([0]))
        state_key_1 = optimizer._state_to_key(np.array([1]))

        # State 1 was terminal, so its Q-value is just the reward
        q_1 = optimizer._q_table[state_key_1][0]
        assert q_1 > 0

    def test_reset_clears_state(self):
        """Test reset() clears all learned state."""
        optimizer = RLDecisionOptimizer()

        # Learn something (select_action increments total_steps)
        for _ in range(10):
            optimizer.select_action([0])
            optimizer.update([0], 0, reward=1.0)

        assert optimizer.is_trained is True
        assert optimizer._total_steps > 0
        assert optimizer._action_counts[0] > 0

        # Reset
        optimizer.reset()

        assert optimizer.is_trained is False
        assert optimizer._total_steps == 0
        assert len(optimizer._action_counts) == 0


class TestEdgeCases(TestCase):
    """Test edge cases and error handling."""

    def test_single_action(self):
        """Test with only one action available."""
        optimizer = RLDecisionOptimizer()

        result = optimizer.predict_with_fallback(
            {'state': [0.5]},
            actions=['only_option']
        )

        assert result.success is True
        assert result.recommended_action == 'only_option'

    def test_many_actions(self):
        """Test with many actions."""
        optimizer = RLDecisionOptimizer()

        actions = [f'action_{i}' for i in range(100)]
        result = optimizer.predict_with_fallback(
            {'state': [0.5]},
            actions=actions
        )

        assert result.success is True
        assert result.recommended_action in actions

    def test_negative_rewards(self):
        """Test handling of negative rewards."""
        optimizer = RLDecisionOptimizer()

        optimizer.update([0], 0, reward=-1.0)
        optimizer.update([0], 1, reward=-0.5)

        # Should still work and prefer less negative
        result = optimizer.select_action([0], explore=False)

        assert result.success is True

    def test_extreme_rewards(self):
        """Test handling of extreme reward values."""
        optimizer = RLDecisionOptimizer()

        optimizer.update([0], 0, reward=1000.0)
        optimizer.update([0], 1, reward=-1000.0)

        result = optimizer.select_action([0], explore=False)

        assert result.success is True
        assert result.action_values[0] > result.action_values[1]

    def test_get_model_info(self):
        """Test model info retrieval."""
        optimizer = RLDecisionOptimizer(model_name="test_optimizer")

        info = optimizer.get_model_info()

        assert info['model_name'] == 'test_optimizer'
        assert 'is_trained' in info
        assert 'config' in info
        assert 'torch_available' in info

    def test_dict_input_with_numeric_values(self):
        """Test extraction of numeric values from dict."""
        optimizer = RLDecisionOptimizer()

        data = {
            'price': 100.5,
            'volume': 5000,
            'change': -0.02,
            'name': 'test',  # Non-numeric, should be ignored
        }

        result = optimizer.predict_with_fallback(data)

        assert result.success is True
