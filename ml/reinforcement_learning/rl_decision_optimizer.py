"""
RL Decision Optimizer
=====================

Session 680: Phase 4 - Reinforcement Learning

Reinforcement Learning model for decision optimization in:
- Opportunity scoring (OpportunityScoringAgent)
- Arbitrage detection (ArbitrageDetector)
- Market decisions (PredictionMarketAnalyst)
- Strategic thinking (ThinkingAgent)

Features:
- Q-Learning for discrete action spaces
- Multi-armed bandit for exploration/exploitation
- Thompson Sampling for probabilistic action selection
- Fallback mode using UCB (Upper Confidence Bound) - no external deps required

Fallback Mode:
When deep RL libraries are not installed, uses:
- UCB1 algorithm for action selection
- Expected value estimation
- Epsilon-greedy exploration
"""

import logging
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)

# Check for deep RL libraries
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.info("PyTorch not available - RL will use fallback mode")


@dataclass
class DecisionPrediction:
    """
    Structured result from RL decision optimization.

    Attributes:
        success: Whether prediction succeeded
        recommended_action: The recommended action index or name
        action_values: Q-values or expected values for each action
        confidence: Confidence in the recommendation (0-1)
        exploration_bonus: Bonus applied for exploration
        action_probabilities: Probability distribution over actions
        expected_reward: Expected reward for recommended action
        metadata: Additional prediction metadata
        error: Error message if prediction failed
    """
    success: bool
    recommended_action: Union[int, str] = 0
    action_values: List[float] = field(default_factory=list)
    confidence: float = 0.0
    exploration_bonus: float = 0.0
    action_probabilities: List[float] = field(default_factory=list)
    expected_reward: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'recommended_action': self.recommended_action,
            'action_values': self.action_values,
            'confidence': self.confidence,
            'exploration_bonus': self.exploration_bonus,
            'action_probabilities': self.action_probabilities,
            'expected_reward': self.expected_reward,
            'metadata': self.metadata,
            'error': self.error,
        }


class QNetwork(nn.Module if TORCH_AVAILABLE else object):
    """Simple Q-Network for Deep Q-Learning."""

    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 64):
        if not TORCH_AVAILABLE:
            return
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
        )

    def forward(self, x):
        if not TORCH_AVAILABLE:
            return None
        return self.network(x)


class RLDecisionOptimizer:
    """
    Reinforcement Learning optimizer for decision-making.

    Supports multiple RL algorithms:
    - Q-Learning (tabular and deep)
    - Multi-Armed Bandit (UCB, Thompson Sampling)
    - Epsilon-Greedy exploration

    Use cases:
    - Action selection: Choose best action from discrete set
    - Opportunity scoring: Rank opportunities by expected value
    - Resource allocation: Optimize distribution of resources
    """

    DEFAULT_CONFIG = {
        # RL parameters
        'learning_rate': 0.01,
        'discount_factor': 0.95,
        'epsilon': 0.1,  # Exploration rate
        'epsilon_decay': 0.995,
        'epsilon_min': 0.01,

        # Network architecture (for Deep Q-Learning)
        'hidden_dim': 64,
        'batch_size': 32,
        'memory_size': 10000,

        # UCB parameters (fallback)
        'ucb_c': 2.0,  # Exploration constant

        # Thompson Sampling parameters
        'prior_alpha': 1.0,
        'prior_beta': 1.0,

        # General
        'default_actions': ['accept', 'reject', 'defer'],
        'min_observations': 5,
    }

    def __init__(self, model_name: str = "rl_decision_optimizer", config: Dict = None):
        self.model_name = model_name
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self.is_trained = False

        # Q-Learning components
        self._q_network = None
        self._target_network = None
        self._optimizer = None
        self._memory = []

        # Tabular Q-Learning
        self._q_table: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))

        # Multi-Armed Bandit statistics
        self._action_counts: Dict[int, int] = defaultdict(int)
        self._action_rewards: Dict[int, float] = defaultdict(float)
        self._action_squared_rewards: Dict[int, float] = defaultdict(float)
        self._total_steps = 0

        # Thompson Sampling parameters
        self._alpha: Dict[int, float] = defaultdict(lambda: self.config['prior_alpha'])
        self._beta: Dict[int, float] = defaultdict(lambda: self.config['prior_beta'])

        # Action mapping
        self._action_names = self.config['default_actions']
        self._num_actions = len(self._action_names)

    def _build_network(self, state_dim: int) -> None:
        """Build Q-Network for Deep Q-Learning."""
        if not TORCH_AVAILABLE:
            return

        self._q_network = QNetwork(state_dim, self._num_actions, self.config['hidden_dim'])
        self._target_network = QNetwork(state_dim, self._num_actions, self.config['hidden_dim'])
        self._target_network.load_state_dict(self._q_network.state_dict())
        self._optimizer = optim.Adam(
            self._q_network.parameters(),
            lr=self.config['learning_rate']
        )

    def select_action(
        self,
        state: Union[List[float], np.ndarray, Dict],
        actions: List[str] = None,
        explore: bool = True,
    ) -> DecisionPrediction:
        """
        Select the best action for a given state.

        Args:
            state: Current state/context features
            actions: Available actions (uses defaults if not provided)
            explore: Whether to use exploration (epsilon-greedy)

        Returns:
            DecisionPrediction with recommended action and values
        """
        # Setup actions
        if actions is not None:
            self._action_names = actions
            self._num_actions = len(actions)

        # Extract state features
        state_features = self._extract_state(state)

        if state_features is None:
            return DecisionPrediction(
                success=False,
                error="Could not extract state features",
            )

        if TORCH_AVAILABLE and self._q_network is not None:
            return self._select_action_deep(state_features, explore)
        else:
            return self._select_action_ucb(state_features, explore)

    def _select_action_deep(self, state: np.ndarray, explore: bool) -> DecisionPrediction:
        """Select action using Deep Q-Network."""
        state_tensor = torch.FloatTensor(state).unsqueeze(0)

        with torch.no_grad():
            q_values = self._q_network(state_tensor).squeeze().numpy()

        # Epsilon-greedy exploration
        if explore and np.random.random() < self.config['epsilon']:
            action = np.random.randint(self._num_actions)
            exploration_bonus = self.config['epsilon']
        else:
            action = int(np.argmax(q_values))
            exploration_bonus = 0.0

        # Calculate action probabilities (softmax)
        exp_q = np.exp(q_values - np.max(q_values))
        probabilities = (exp_q / exp_q.sum()).tolist()

        # Confidence based on Q-value gap
        sorted_q = np.sort(q_values)[::-1]
        confidence = min(1.0, (sorted_q[0] - sorted_q[1]) / (abs(sorted_q[0]) + 1e-8) + 0.5)

        return DecisionPrediction(
            success=True,
            recommended_action=self._action_names[action] if action < len(self._action_names) else action,
            action_values=q_values.tolist(),
            confidence=float(confidence),
            exploration_bonus=exploration_bonus,
            action_probabilities=probabilities,
            expected_reward=float(q_values[action]),
            metadata={
                'method': 'deep_q_learning',
                'epsilon': self.config['epsilon'],
                'action_index': action,
            },
        )

    def _select_action_ucb(self, state: np.ndarray, explore: bool) -> DecisionPrediction:
        """Select action using UCB1 algorithm (fallback)."""
        self._total_steps += 1

        # State key for tabular lookup
        state_key = self._state_to_key(state)

        # Calculate UCB values for each action
        ucb_values = []
        q_values = []

        for action in range(self._num_actions):
            count = self._action_counts[action]
            if count == 0:
                # Unexplored action - give high value
                ucb = float('inf')
                q_val = 0.0
            else:
                # Q-value (average reward)
                q_val = self._action_rewards[action] / count

                # UCB exploration bonus
                if explore:
                    ucb_bonus = self.config['ucb_c'] * math.sqrt(
                        math.log(self._total_steps + 1) / count
                    )
                else:
                    ucb_bonus = 0.0

                ucb = q_val + ucb_bonus

            ucb_values.append(ucb)
            q_values.append(q_val)

        # Select action with highest UCB value
        if any(v == float('inf') for v in ucb_values):
            # Explore unexplored actions first
            unexplored = [i for i, v in enumerate(ucb_values) if v == float('inf')]
            action = np.random.choice(unexplored)
            exploration_bonus = 1.0
        else:
            action = int(np.argmax(ucb_values))
            exploration_bonus = ucb_values[action] - q_values[action]

        # Normalize Q-values for probabilities
        q_array = np.array(q_values)
        if np.std(q_array) > 0:
            exp_q = np.exp(q_array - np.max(q_array))
            probabilities = (exp_q / exp_q.sum()).tolist()
        else:
            probabilities = [1.0 / self._num_actions] * self._num_actions

        # Confidence based on observation count and value gap
        min_obs = min(self._action_counts.values()) if self._action_counts else 0
        obs_confidence = min(1.0, min_obs / self.config['min_observations'])

        if len(set(q_values)) > 1:
            sorted_q = sorted(q_values, reverse=True)
            value_confidence = min(1.0, (sorted_q[0] - sorted_q[1]) / (abs(sorted_q[0]) + 1e-8) + 0.3)
        else:
            value_confidence = 0.3

        confidence = 0.4 * obs_confidence + 0.6 * value_confidence

        return DecisionPrediction(
            success=True,
            recommended_action=self._action_names[action] if action < len(self._action_names) else action,
            action_values=q_values,
            confidence=float(confidence),
            exploration_bonus=float(exploration_bonus) if exploration_bonus != float('inf') else 1.0,
            action_probabilities=probabilities,
            expected_reward=float(q_values[action]),
            metadata={
                'method': 'ucb1',
                'fallback_mode': True,
                'total_steps': self._total_steps,
                'action_counts': dict(self._action_counts),
                'action_index': action,
            },
        )

    def select_action_thompson(self, actions: List[str] = None) -> DecisionPrediction:
        """
        Select action using Thompson Sampling.

        Good for balancing exploration/exploitation with uncertainty.
        """
        if actions is not None:
            self._action_names = actions
            self._num_actions = len(actions)

        # Sample from Beta distribution for each action
        samples = []
        for action in range(self._num_actions):
            alpha = self._alpha[action]
            beta = self._beta[action]
            sample = np.random.beta(alpha, beta)
            samples.append(sample)

        # Select action with highest sample
        action = int(np.argmax(samples))

        # Calculate expected values (mean of Beta distribution)
        expected_values = [
            self._alpha[a] / (self._alpha[a] + self._beta[a])
            for a in range(self._num_actions)
        ]

        # Confidence based on concentration of Beta distribution
        total_obs = sum(self._alpha[a] + self._beta[a] - 2 for a in range(self._num_actions))
        confidence = min(1.0, total_obs / (self.config['min_observations'] * self._num_actions))

        return DecisionPrediction(
            success=True,
            recommended_action=self._action_names[action] if action < len(self._action_names) else action,
            action_values=expected_values,
            confidence=float(confidence),
            exploration_bonus=float(samples[action] - expected_values[action]),
            action_probabilities=samples,  # Sampled values as "probabilities"
            expected_reward=float(expected_values[action]),
            metadata={
                'method': 'thompson_sampling',
                'fallback_mode': True,
                'samples': samples,
                'alpha': dict(self._alpha),
                'beta': dict(self._beta),
                'action_index': action,
            },
        )

    def update(
        self,
        state: Union[List[float], np.ndarray, Dict],
        action: Union[int, str],
        reward: float,
        next_state: Union[List[float], np.ndarray, Dict] = None,
        done: bool = False,
    ) -> Dict[str, Any]:
        """
        Update the model with observed reward.

        Args:
            state: State where action was taken
            action: Action that was taken (index or name)
            reward: Observed reward
            next_state: Resulting state (for Q-learning)
            done: Whether episode is complete

        Returns:
            Update statistics
        """
        # Convert action name to index
        if isinstance(action, str):
            try:
                action_idx = self._action_names.index(action)
            except ValueError:
                action_idx = 0
        else:
            action_idx = action

        # Update bandit statistics
        self._action_counts[action_idx] += 1
        self._action_rewards[action_idx] += reward
        self._action_squared_rewards[action_idx] += reward ** 2

        # Update Thompson Sampling parameters
        # Treat reward as probability of success (0-1 scale)
        normalized_reward = max(0, min(1, (reward + 1) / 2))  # Map [-1, 1] to [0, 1]
        if normalized_reward > 0.5:
            self._alpha[action_idx] += normalized_reward
        else:
            self._beta[action_idx] += (1 - normalized_reward)

        # Update Q-table
        state_key = self._state_to_key(self._extract_state(state))
        old_q = self._q_table[state_key][action_idx]

        if next_state is not None and not done:
            next_state_key = self._state_to_key(self._extract_state(next_state))
            next_max_q = max(self._q_table[next_state_key].values()) if self._q_table[next_state_key] else 0
            target = reward + self.config['discount_factor'] * next_max_q
        else:
            target = reward

        # Q-learning update
        self._q_table[state_key][action_idx] = old_q + self.config['learning_rate'] * (target - old_q)

        # Decay epsilon
        self.config['epsilon'] = max(
            self.config['epsilon_min'],
            self.config['epsilon'] * self.config['epsilon_decay']
        )

        self.is_trained = True

        return {
            'action': action_idx,
            'reward': reward,
            'old_q': old_q,
            'new_q': self._q_table[state_key][action_idx],
            'epsilon': self.config['epsilon'],
        }

    def predict_with_fallback(
        self,
        data: Union[List, np.ndarray, Dict],
        actions: List[str] = None,
    ) -> DecisionPrediction:
        """
        Make a decision prediction with automatic fallback.

        This is the main entry point for decision making.

        Args:
            data: Input state/context - can be:
                - List of features
                - numpy array
                - Dict with 'state', 'features', 'context', or 'values' key
            actions: Available actions (uses defaults if not provided)

        Returns:
            DecisionPrediction with recommended action
        """
        # Extract state from data
        state = self._extract_state(data)

        if state is None or len(state) == 0:
            return DecisionPrediction(
                success=False,
                error="No valid state data provided",
            )

        # Setup actions
        if actions is None:
            # Try to get actions from data dict
            if isinstance(data, dict):
                actions = data.get('actions', data.get('choices', self._action_names))
            else:
                actions = self._action_names

        self._action_names = actions
        self._num_actions = len(actions)

        # Use appropriate method based on available libraries
        if TORCH_AVAILABLE and self._q_network is not None:
            return self.select_action(state, actions, explore=False)
        elif self._total_steps > 0:
            # Use UCB if we have some experience
            return self.select_action(state, actions, explore=True)
        else:
            # Use Thompson Sampling for cold start
            return self.select_action_thompson(actions)

    def rank_opportunities(
        self,
        opportunities: List[Dict],
        score_key: str = 'score',
    ) -> DecisionPrediction:
        """
        Rank opportunities using RL-based expected value estimation.

        Args:
            opportunities: List of opportunity dicts with features
            score_key: Key for existing score (if available)

        Returns:
            DecisionPrediction with ranked opportunities
        """
        if not opportunities:
            return DecisionPrediction(
                success=False,
                error="No opportunities to rank",
            )

        # Calculate expected value for each opportunity
        values = []
        for opp in opportunities:
            # Extract features
            features = self._extract_state(opp)
            if features is None:
                features = np.array([opp.get(score_key, 0.5)])

            # Get base score
            base_score = opp.get(score_key, 0.5)

            # Apply UCB-style exploration bonus based on uncertainty
            uncertainty = opp.get('uncertainty', 0.2)
            exploration_bonus = self.config['ucb_c'] * uncertainty

            # Combine for expected value
            expected_value = base_score + exploration_bonus * 0.1

            values.append(expected_value)

        # Rank by expected value
        ranked_indices = np.argsort(values)[::-1].tolist()

        # Normalize to probabilities
        values_array = np.array(values)
        exp_v = np.exp(values_array - np.max(values_array))
        probabilities = (exp_v / exp_v.sum()).tolist()

        return DecisionPrediction(
            success=True,
            recommended_action=ranked_indices[0],  # Best opportunity index
            action_values=values,
            confidence=0.6,
            action_probabilities=probabilities,
            expected_reward=values[ranked_indices[0]],
            metadata={
                'method': 'opportunity_ranking',
                'ranked_indices': ranked_indices,
                'num_opportunities': len(opportunities),
            },
        )

    def _extract_state(self, data: Any) -> Optional[np.ndarray]:
        """Extract state features from various input formats."""
        if isinstance(data, np.ndarray):
            return data.flatten() if data.ndim > 1 else data

        if isinstance(data, list):
            return np.array(data).flatten()

        if isinstance(data, dict):
            # Try various keys
            for key in ['state', 'features', 'context', 'values', 'data']:
                if key in data:
                    return self._extract_state(data[key])

            # Extract numeric values from dict
            numeric_values = []
            for v in data.values():
                if isinstance(v, (int, float)):
                    numeric_values.append(v)
                elif isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
                    numeric_values.extend(v)

            if numeric_values:
                return np.array(numeric_values)

        return None

    def _state_to_key(self, state: np.ndarray) -> str:
        """Convert state to hashable key for tabular Q-learning."""
        if state is None:
            return "default"
        # Discretize continuous states
        discretized = tuple(int(x * 10) / 10 for x in state[:10])  # First 10 features
        return str(discretized)

    def get_model_info(self) -> Dict[str, Any]:
        """Return model information."""
        return {
            'model_name': self.model_name,
            'is_trained': self.is_trained,
            'config': self.config,
            'torch_available': TORCH_AVAILABLE,
            'total_steps': self._total_steps,
            'action_counts': dict(self._action_counts),
            'num_actions': self._num_actions,
            'action_names': self._action_names,
            'method': 'deep_q' if TORCH_AVAILABLE and self._q_network else 'ucb_bandit',
        }

    def reset(self) -> None:
        """Reset the optimizer state."""
        self._q_table.clear()
        self._action_counts.clear()
        self._action_rewards.clear()
        self._action_squared_rewards.clear()
        self._alpha = defaultdict(lambda: self.config['prior_alpha'])
        self._beta = defaultdict(lambda: self.config['prior_beta'])
        self._total_steps = 0
        self.is_trained = False


# Singleton instance
_rl_optimizer = None


def get_rl_optimizer() -> RLDecisionOptimizer:
    """Get the singleton RL optimizer instance."""
    global _rl_optimizer
    if _rl_optimizer is None:
        _rl_optimizer = RLDecisionOptimizer()
    return _rl_optimizer
