"""
ML Engine - Core Machine Learning Pipeline
Optimized for Apple M3 with MLX framework
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Apple ML Stack
try:
    import mlx.core as mx
    import mlx.nn as nn
    from mlx.utils import tree_flatten
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    logging.warning("MLX not available - falling back to standard frameworks")

# Core ML Libraries
import torch
import torch.nn as torch_nn
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib

# HuggingFace Integration
from transformers import pipeline, AutoTokenizer, AutoModel

@dataclass
class MLConfig:
    """ML Engine Configuration"""
    model_cache_dir: str = "models/cache"
    use_mlx: bool = MLX_AVAILABLE
    max_memory_gb: float = 8.0  # Reserve 10GB for system
    inference_timeout: int = 5000  # 5 second timeout
    batch_size: int = 32
    device: str = "mps" if torch.backends.mps.is_available() else "cpu"

@dataclass
class PatternPrediction:
    """Pattern Recognition Result"""
    pattern_type: str
    confidence: float
    predicted_outcome: str
    time_horizon: str
    supporting_features: Dict[str, float]
    cross_domain_signals: List[str]

@dataclass
class UserBehaviorProfile:
    """User Decision Pattern Profile"""
    risk_tolerance: float
    preferred_domains: List[str]
    decision_speed: str  # "fast", "moderate", "deliberate"
    confidence_calibration: Dict[str, float]
    success_rates: Dict[str, float]
    personal_edges: List[str]

class MLEngine:
    """
    Core ML Engine for Pattern Recognition and User Behavior Learning
    Optimized for Apple M3 with local-first architecture
    """

    def __init__(self, config: MLConfig = None):
        self.config = config or MLConfig()
        self.models = {}  # Keep for backward compatibility with non-sport models
        self.sport_models = {  # New: Sport-specific models
            'nfl': {},
            'nba': {},
            'mlb': {},
            'nhl': {}
        }
        self.scalers = {}
        self.user_profile = None

        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize local ML stack
        self._initialize_ml_stack()
        self._initialize_user_tracking()

    def _initialize_ml_stack(self):
        """Initialize the local ML stack"""
        self.logger.info(f"Initializing ML stack - MLX Available: {MLX_AVAILABLE}")

        # Create model cache directory
        os.makedirs(self.config.model_cache_dir, exist_ok=True)

        # Initialize pattern recognition models
        self._load_or_initialize_models()

        # Initialize HuggingFace pipelines for sentiment analysis
        self._initialize_nlp_models()

    def _load_or_initialize_models(self):
        """Load existing models or initialize new ones"""
        # Legacy non-sport models (backward compatibility)
        model_files = {
            'sports_crypto_lstm': 'sports_crypto_lstm.joblib',  # Keep for NFL backward compat
            'options_betting_nn': 'options_betting_nn.joblib',
            'user_behavior_rf': 'user_behavior_rf.joblib',
            'cross_domain_gb': 'cross_domain_gb.joblib'
        }

        for model_name, filename in model_files.items():
            model_path = os.path.join(self.config.model_cache_dir, filename)

            if os.path.exists(model_path):
                try:
                    self.models[model_name] = joblib.load(model_path)
                    self.logger.info(f"Loaded existing model: {model_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to load {model_name}: {e}")
                    self._create_default_model(model_name)
            else:
                self._create_default_model(model_name)

        # Load sport-specific models
        self._load_sport_models()

    def _create_default_model(self, model_name: str):
        """Create default model if none exists"""
        from sklearn.neural_network import MLPRegressor

        if model_name == 'sports_crypto_lstm':
            # Simple LSTM-like model using scikit-learn for now
            # Will upgrade to MLX LSTM when we have training data
            self.models[model_name] = MLPRegressor(
                hidden_layer_sizes=(128, 64, 32),
                activation='relu',
                solver='adam',
                max_iter=500,
                random_state=42
            )

        elif model_name == 'options_betting_nn':
            self.models[model_name] = MLPRegressor(
                hidden_layer_sizes=(64, 32),
                activation='tanh',
                solver='adam',
                max_iter=300,
                random_state=42
            )

        elif model_name == 'user_behavior_rf':
            self.models[model_name] = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )

        elif model_name == 'cross_domain_gb':
            self.models[model_name] = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )

        self.logger.info(f"Created default model: {model_name}")

    def _load_sport_models(self):
        """Load sport-specific prediction models"""
        from ml.core.sport_configs import SPORT_CONFIGS

        for sport_type, config in SPORT_CONFIGS.items():
            model_filename = f"{config.model_name}.joblib"
            model_path = os.path.join(self.config.model_cache_dir, model_filename)

            if os.path.exists(model_path):
                try:
                    self.sport_models[sport_type][config.model_name] = joblib.load(model_path)
                    self.logger.info(f"Loaded {config.name} model: {config.model_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to load {config.name} model: {e}")
            else:
                self.logger.info(f"{config.name} model not found (will use baseline predictions)")

    def save_sport_models(self):
        """Save all sport-specific models to disk"""
        from ml.core.sport_configs import SPORT_CONFIGS

        for sport_type, config in SPORT_CONFIGS.items():
            if config.model_name in self.sport_models[sport_type]:
                model_filename = f"{config.model_name}.joblib"
                model_path = os.path.join(self.config.model_cache_dir, model_filename)
                try:
                    joblib.dump(self.sport_models[sport_type][config.model_name], model_path)
                    self.logger.info(f"Saved {config.name} model: {config.model_name}")
                except Exception as e:
                    self.logger.error(f"Failed to save {config.name} model: {e}")

    def _initialize_nlp_models(self):
        """Initialize NLP models for sentiment analysis"""
        try:
            # Use DistilBERT for fast local sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if torch.backends.mps.is_available() else -1
            )
            self.logger.info("Initialized local sentiment analysis model")

        except Exception as e:
            self.logger.error(f"Failed to initialize NLP models: {e}")
            self.sentiment_analyzer = None

    def _initialize_user_tracking(self):
        """Initialize user behavior tracking"""
        # Load existing user profile if available
        profile_path = os.path.join(self.config.model_cache_dir, 'user_profile.joblib')

        if os.path.exists(profile_path):
            try:
                self.user_profile = joblib.load(profile_path)
                self.logger.info("Loaded existing user behavior profile")
            except Exception as e:
                self.logger.warning(f"Failed to load user profile: {e}")
                self._create_default_user_profile()
        else:
            self._create_default_user_profile()

    def _create_default_user_profile(self):
        """Create default user behavior profile"""
        self.user_profile = UserBehaviorProfile(
            risk_tolerance=0.5,  # Will be learned from decisions
            preferred_domains=['SPORTS_BETTING', 'CRYPTO'],
            decision_speed="moderate",
            confidence_calibration={
                'SPORTS_BETTING': 0.7,
                'CRYPTO': 0.6,
                'TRADING': 0.5,
                'REAL_ESTATE': 0.4
            },
            success_rates={},
            personal_edges=[]
        )
        self.logger.info("Created default user behavior profile")

    def analyze_sports_to_crypto_pattern(self,
                                       sports_data: Dict[str, Any],
                                       crypto_context: Dict[str, Any]) -> PatternPrediction:
        """
        Analyze sports outcomes to predict crypto patterns
        Example: NBA injury news timing → BTC volatility prediction
        """
        try:
            # Extract features from sports data
            features = self._extract_sports_features(sports_data)

            # Get crypto context features
            crypto_features = self._extract_crypto_features(crypto_context)

            # Combine features
            combined_features = np.concatenate([features, crypto_features])

            # Get prediction from model (placeholder for now)
            if 'sports_crypto_lstm' in self.models:
                # For now, return a mock prediction until we have training data
                confidence = np.random.uniform(0.6, 0.9)
                predicted_direction = "bullish" if np.random.random() > 0.5 else "bearish"

                return PatternPrediction(
                    pattern_type="sports_crypto_correlation",
                    confidence=confidence,
                    predicted_outcome=f"BTC {predicted_direction} in next 4-8 hours",
                    time_horizon="4-8 hours",
                    supporting_features={
                        "injury_severity": features[0] if len(features) > 0 else 0.5,
                        "market_volatility": crypto_features[0] if len(crypto_features) > 0 else 0.3,
                        "news_sentiment": 0.7  # Placeholder
                    },
                    cross_domain_signals=["NBA injury report", "BTC volume spike", "Social sentiment"]
                )

        except Exception as e:
            self.logger.error(f"Error in sports-crypto analysis: {e}")
            return PatternPrediction(
                pattern_type="error",
                confidence=0.0,
                predicted_outcome="Analysis failed",
                time_horizon="unknown",
                supporting_features={},
                cross_domain_signals=[]
            )

    def analyze_user_decision_pattern(self, decision_data: Dict[str, Any]) -> float:
        """
        Analyze user decision and return personalized confidence score
        This builds the "Digital Twin" of decision-making patterns
        """
        try:
            # Extract features from the decision
            features = self._extract_decision_features(decision_data)

            # Get personalized confidence score
            base_confidence = decision_data.get('confidence', 0.5)

            # Adjust based on user's historical performance in this domain
            domain = decision_data.get('domain', 'UNKNOWN')
            domain_performance = self.user_profile.confidence_calibration.get(domain, 0.5)

            # Personal confidence adjustment
            personal_confidence = (base_confidence * 0.7) + (domain_performance * 0.3)

            # Store this decision for learning
            self._record_user_decision(decision_data, personal_confidence)

            return min(max(personal_confidence, 0.1), 0.9)  # Clamp between 0.1-0.9

        except Exception as e:
            self.logger.error(f"Error in user decision analysis: {e}")
            return 0.5  # Default neutral confidence

    def detect_cross_domain_opportunity(self,
                                      market_data: Dict[str, Any]) -> List[PatternPrediction]:
        """
        Detect cross-domain opportunities using transfer learning
        Examples:
        - Options IV crush → Sports betting value detection
        - Crypto whale behavior → Real estate market timing
        """
        opportunities = []

        try:
            # Analyze different cross-domain patterns

            # 1. Options → Sports Betting
            if 'options_data' in market_data and 'sports_data' in market_data:
                sports_opp = self._analyze_options_to_sports(
                    market_data['options_data'],
                    market_data['sports_data']
                )
                if sports_opp:
                    opportunities.append(sports_opp)

            # 2. Crypto → Real Estate
            if 'crypto_data' in market_data and 'real_estate_data' in market_data:
                real_estate_opp = self._analyze_crypto_to_real_estate(
                    market_data['crypto_data'],
                    market_data['real_estate_data']
                )
                if real_estate_opp:
                    opportunities.append(real_estate_opp)

            # 3. Sports Timing → Stock Earnings
            if 'sports_schedule' in market_data and 'earnings_calendar' in market_data:
                earnings_opp = self._analyze_sports_to_earnings(
                    market_data['sports_schedule'],
                    market_data['earnings_calendar']
                )
                if earnings_opp:
                    opportunities.append(earnings_opp)

            return opportunities

        except Exception as e:
            self.logger.error(f"Error in cross-domain analysis: {e}")
            return []

    def update_user_feedback(self, decision_id: str, outcome: str, actual_return: float):
        """Update user behavior model based on decision outcomes"""
        try:
            # This will be implemented to update the user's Digital Twin
            # based on actual outcomes vs predictions
            self.logger.info(f"Recording feedback for decision {decision_id}: {outcome}")

            # Update user profile confidence calibration
            # This is where the personalized learning happens

        except Exception as e:
            self.logger.error(f"Error updating user feedback: {e}")

    def save_models(self):
        """Save all trained models"""
        try:
            for model_name, model in self.models.items():
                filename = f"{model_name}.joblib"
                model_path = os.path.join(self.config.model_cache_dir, filename)
                joblib.dump(model, model_path)

            # Save user profile
            profile_path = os.path.join(self.config.model_cache_dir, 'user_profile.joblib')
            joblib.dump(self.user_profile, profile_path)

            self.logger.info("Saved all models and user profile")

        except Exception as e:
            self.logger.error(f"Error saving models: {e}")

    def get_system_health(self) -> Dict[str, Any]:
        """Get ML system health status"""
        return {
            "mlx_available": MLX_AVAILABLE,
            "device": self.config.device,
            "models_loaded": len(self.models),
            "user_profile_active": self.user_profile is not None,
            "memory_usage": f"{self.config.max_memory_gb}GB allocated",
            "nlp_models_ready": self.sentiment_analyzer is not None
        }

    # Helper methods for feature extraction
    def _extract_sports_features(self, sports_data: Dict[str, Any]) -> np.ndarray:
        """Extract numerical features from sports data"""
        # Placeholder - implement based on your sports data structure
        return np.array([0.5, 0.7, 0.3])  # Mock features

    def _extract_crypto_features(self, crypto_data: Dict[str, Any]) -> np.ndarray:
        """Extract numerical features from crypto data"""
        # Placeholder - implement based on your crypto data structure
        return np.array([0.4, 0.8])  # Mock features

    # ========== NFL PREDICTIONS ==========
    # Added in Session 14 - NFL game prediction system

    def predict_game(self, game_id: str, sport_type: str) -> Dict[str, Any]:
        """
        Universal game prediction for any sport

        Args:
            game_id: Game ID to predict
            sport_type: Sport type ('nfl', 'nba', 'mlb', 'nhl')

        Returns:
            Dictionary with prediction results
        """
        from sports.models import Game
        from ml.core.sport_configs import get_sport_config
        from sklearn.exceptions import NotFittedError

        config = get_sport_config(sport_type)
        game = Game.objects.select_related('home_team', 'away_team').get(id=game_id)

        # Extract sport-specific features
        features = self._extract_sport_features(game, config)

        # Try to use sport-specific trained model
        model_name = config.model_name
        if model_name in self.sport_models[sport_type]:
            try:
                model = self.sport_models[sport_type][model_name]
                prediction_raw = model.predict([features])
                return self._format_prediction(prediction_raw, game, config)
            except NotFittedError:
                self.logger.info(f"{config.name} model not trained yet, using baseline")
                return self._generate_baseline_prediction(game, config)
            except Exception as e:
                self.logger.error(f"{config.name} prediction failed: {e}, using baseline")
                return self._generate_baseline_prediction(game, config)

        # No trained model found, use baseline
        return self._generate_baseline_prediction(game, config)

    def predict_nfl_game(self, game_id: str) -> Dict[str, Any]:
        """
        Predict NFL game (backward compatibility wrapper)

        This delegates to predict_game() for multi-sport support
        """
        return self.predict_game(game_id, 'nfl')

    def _extract_sport_features(self, game: 'Game', config) -> np.ndarray:
        """
        Extract features for any sport based on configuration

        Args:
            game: Game object with home_team and away_team
            config: SportConfig object with feature definitions

        Returns:
            numpy array of features
        """
        # Get team stats with sport-specific window
        home_stats = self._get_team_recent_performance(
            game.home_team,
            games=config.recent_games_window,
            sport_type=config.sport_type
        )
        away_stats = self._get_team_recent_performance(
            game.away_team,
            games=config.recent_games_window,
            sport_type=config.sport_type
        )

        # Build feature vector based on config
        features = []

        for feature_name in config.features:
            if feature_name == 'points_differential':
                features.append(home_stats['points_per_game'] - away_stats['points_per_game'])
            elif feature_name == 'yards_differential':
                features.append(home_stats.get('yards_per_game', 0) - away_stats.get('yards_per_game', 0))
            elif feature_name == 'defensive_strength':
                features.append(away_stats['points_allowed'] - home_stats['points_allowed'])
            elif feature_name == 'win_rate_differential':
                features.append(home_stats['win_rate'] - away_stats['win_rate'])
            elif feature_name == 'ats_differential':
                features.append(home_stats.get('ats_record', 0) - away_stats.get('ats_record', 0))
            elif feature_name == 'home_indicator':
                features.append(1.0)
            elif feature_name == 'rest_differential':
                features.append(home_stats.get('days_rest', 7) - away_stats.get('days_rest', 7))
            elif feature_name == 'division_game':
                is_division = game.home_team.conference == game.away_team.conference if hasattr(game.home_team, 'conference') else False
                features.append(1.0 if is_division else 0.0)
            elif feature_name in ['rebounds_differential', 'assists_differential', 'pace_differential']:
                # NBA-specific features (placeholder for now)
                features.append(0.0)
            elif feature_name == 'defensive_rating':
                # NBA defensive rating
                features.append(away_stats['points_allowed'] - home_stats['points_allowed'])
            elif feature_name in ['back_to_back', 'pitcher_matchup_rating', 'weather_factor',
                                   'runs_differential', 'era_differential', 'batting_avg_differential',
                                   'bullpen_era_differential', 'goals_differential', 'shots_differential',
                                   'save_percentage_differential', 'powerplay_differential',
                                   'penalty_kill_differential', 'goalie_matchup_rating']:
                # Sport-specific features (placeholder for now - will be enhanced with real data)
                features.append(0.0)
            else:
                # Unknown feature - use zero
                features.append(0.0)

        return np.array(features)

    def _extract_nfl_game_features(self, game: 'Game') -> np.ndarray:
        """
        Extract features for NFL game prediction

        Uses existing _extract_sports_features as foundation
        """
        # Get team stats
        home_stats = self._get_team_recent_performance(game.home_team)
        away_stats = self._get_team_recent_performance(game.away_team)

        features = [
            # Offensive metrics
            home_stats['points_per_game'] - away_stats['points_per_game'],
            home_stats['yards_per_game'] - away_stats['yards_per_game'],

            # Defensive metrics
            away_stats['points_allowed'] - home_stats['points_allowed'],

            # Win rates
            home_stats['win_rate'] - away_stats['win_rate'],
            home_stats['ats_record'] - away_stats['ats_record'],

            # Home field advantage
            1.0,  # Home team indicator

            # Rest differential
            home_stats['days_rest'] - away_stats['days_rest'],

            # Division game
            1.0 if game.home_team.conference == game.away_team.conference else 0.0,
        ]

        return np.array(features)

    def _get_team_recent_performance(self, team: 'Team', games: int = 10, sport_type: str = None) -> Dict:
        """
        Calculate team statistics from recent games (sport-agnostic)

        Args:
            team: Team object
            games: Number of recent games to analyze
            sport_type: Optional sport filter ('nfl', 'nba', 'mlb', 'nhl')
        """
        from sports.models import Game
        from django.db.models import Q

        query = Q(home_team=team) | Q(away_team=team)
        query &= Q(status='final')

        # Filter by sport if specified
        if sport_type:
            query &= Q(league__sport_type=sport_type)

        recent_games = Game.objects.filter(query).order_by('-scheduled_start')[:games]

        stats = {
            'points_per_game': 0,
            'points_allowed': 0,
            'yards_per_game': 0,
            'win_rate': 0,
            'ats_record': 0,
            'days_rest': 7,
        }

        if not recent_games.exists():
            return stats

        total_points = 0
        total_points_allowed = 0
        wins = 0

        for game in recent_games:
            is_home = game.home_team == team

            if is_home:
                total_points += game.home_score or 0
                total_points_allowed += game.away_score or 0
                if game.home_score > game.away_score:
                    wins += 1
            else:
                total_points += game.away_score or 0
                total_points_allowed += game.home_score or 0
                if game.away_score > game.home_score:
                    wins += 1

        count = recent_games.count()
        stats['points_per_game'] = total_points / count if count > 0 else 0
        stats['points_allowed'] = total_points_allowed / count if count > 0 else 0
        stats['win_rate'] = wins / count if count > 0 else 0

        return stats

    def _format_prediction(self, prediction_raw: np.ndarray, game: 'Game', config) -> Dict:
        """
        Format raw prediction into sport-friendly output

        Works for any sport using SportConfig
        """
        # Convert model output to probability
        home_win_prob = 1 / (1 + np.exp(-prediction_raw[0]))

        # Calculate derived metrics (sport-agnostic)
        predicted_spread = (home_win_prob - 0.5) * (config.home_advantage * 2 + 8)
        confidence = abs(home_win_prob - 0.5) * 2

        winner = game.home_team if home_win_prob > 0.5 else game.away_team

        return {
            'winner': winner.name,
            'winner_abbr': winner.abbreviation,
            'home_win_probability': round(home_win_prob, 3),
            'away_win_probability': round(1 - home_win_prob, 3),
            'predicted_spread': round(predicted_spread, 1),
            'confidence': round(confidence, 3),
            'model_used': config.model_name,
            'sport': config.sport_type,
            'key_factors': self._identify_key_factors_generic(game, config),
            'recommendation': self._generate_betting_recommendation(
                home_win_prob,
                predicted_spread,
                confidence,
                game
            )
        }

    def _identify_key_factors_generic(self, game: 'Game', config) -> List[str]:
        """Identify key factors for any sport"""
        factors = []

        # Get team stats
        home_stats = self._get_team_recent_performance(
            game.home_team,
            games=config.recent_games_window,
            sport_type=config.sport_type
        )
        away_stats = self._get_team_recent_performance(
            game.away_team,
            games=config.recent_games_window,
            sport_type=config.sport_type
        )

        # Offensive advantage
        if home_stats['points_per_game'] > away_stats['points_per_game'] + config.home_advantage:
            factors.append(f"{game.home_team.name} strong offense (avg {home_stats['points_per_game']:.1f} PPG)")
        elif away_stats['points_per_game'] > home_stats['points_per_game'] + config.home_advantage:
            factors.append(f"{game.away_team.name} strong offense (avg {away_stats['points_per_game']:.1f} PPG)")

        # Defensive advantage
        diff_threshold = config.home_advantage * 1.5
        if home_stats['points_allowed'] < away_stats['points_allowed'] - diff_threshold:
            factors.append(f"{game.home_team.name} superior defense")
        elif away_stats['points_allowed'] < home_stats['points_allowed'] - diff_threshold:
            factors.append(f"{game.away_team.name} superior defense")

        # Recent form
        if home_stats['win_rate'] > 0.7:
            games_won = int(home_stats['win_rate'] * config.recent_games_window)
            games_lost = config.recent_games_window - games_won
            factors.append(f"{game.home_team.name} hot streak ({games_won}-{games_lost} last {config.recent_games_window})")
        elif away_stats['win_rate'] > 0.7:
            games_won = int(away_stats['win_rate'] * config.recent_games_window)
            games_lost = config.recent_games_window - games_won
            factors.append(f"{game.away_team.name} hot streak ({games_won}-{games_lost} last {config.recent_games_window})")

        # Home advantage
        factors.append(f"Home advantage (~{config.home_advantage} points)")

        if len(factors) == 1:  # Only home advantage
            factors.append("Evenly matched teams")

        return factors

    def _format_nfl_prediction(self, prediction_raw: np.ndarray, game: 'Game') -> Dict:
        """Format raw prediction into NFL-friendly output"""

        # Convert model output to probability
        home_win_prob = 1 / (1 + np.exp(-prediction_raw[0]))

        # Calculate derived metrics
        predicted_spread = (home_win_prob - 0.5) * 14  # Rough spread estimation
        confidence = abs(home_win_prob - 0.5) * 2  # 0.5 = no confidence, 1.0 = certain

        winner = game.home_team if home_win_prob > 0.5 else game.away_team

        return {
            'winner': winner.name,
            'winner_abbr': winner.abbreviation,
            'home_win_probability': round(home_win_prob, 3),
            'away_win_probability': round(1 - home_win_prob, 3),
            'predicted_spread': round(predicted_spread, 1),
            'confidence': round(confidence, 3),
            'model_used': 'sports_crypto_lstm',
            'key_factors': self._identify_key_factors(game),
            'recommendation': self._generate_betting_recommendation(
                home_win_prob,
                predicted_spread,
                confidence,
                game
            )
        }

    def _identify_key_factors(self, game: 'Game') -> List[str]:
        """Identify key factors influencing prediction"""
        factors = []

        # Get team stats
        home_stats = self._get_team_recent_performance(game.home_team)
        away_stats = self._get_team_recent_performance(game.away_team)

        # Offensive advantage
        if home_stats['points_per_game'] > away_stats['points_per_game'] + 7:
            factors.append(f"{game.home_team.name} strong offense (avg {home_stats['points_per_game']:.1f} PPG)")
        elif away_stats['points_per_game'] > home_stats['points_per_game'] + 7:
            factors.append(f"{game.away_team.name} strong offense (avg {away_stats['points_per_game']:.1f} PPG)")

        # Defensive advantage
        if home_stats['points_allowed'] < away_stats['points_allowed'] - 5:
            factors.append(f"{game.home_team.name} superior defense")
        elif away_stats['points_allowed'] < home_stats['points_allowed'] - 5:
            factors.append(f"{game.away_team.name} superior defense")

        # Recent form
        if home_stats['win_rate'] > 0.7:
            factors.append(f"{game.home_team.name} hot streak ({int(home_stats['win_rate']*10)}-{int((1-home_stats['win_rate'])*10)} L10)")
        elif away_stats['win_rate'] > 0.7:
            factors.append(f"{game.away_team.name} hot streak ({int(away_stats['win_rate']*10)}-{int((1-away_stats['win_rate'])*10)} L10)")

        # Home field advantage
        factors.append("Home field advantage")

        if not factors:
            factors.append("Evenly matched teams")

        return factors

    def _generate_betting_recommendation(self, home_win_prob: float,
                                        predicted_spread: float,
                                        confidence: float,
                                        game: 'Game') -> Dict:
        """Generate betting recommendations based on prediction"""

        recommendations = []

        # Moneyline recommendation
        if confidence > 0.65:
            winner = game.home_team.name if home_win_prob > 0.5 else game.away_team.name
            recommendations.append({
                'bet_type': 'moneyline',
                'selection': winner,
                'confidence': confidence,
                'reasoning': f"Model projects {int(home_win_prob*100)}% win probability"
            })

        # Spread recommendation
        if abs(predicted_spread) > 3 and confidence > 0.6:
            if predicted_spread > 0:
                recommendations.append({
                    'bet_type': 'spread',
                    'selection': f"{game.home_team.name} -{abs(predicted_spread):.1f}",
                    'confidence': confidence,
                    'reasoning': f"Model projects {abs(predicted_spread):.1f} point margin"
                })
            else:
                recommendations.append({
                    'bet_type': 'spread',
                    'selection': f"{game.away_team.name} +{abs(predicted_spread):.1f}",
                    'confidence': confidence,
                    'reasoning': f"Model projects {abs(predicted_spread):.1f} point margin"
                })

        return {
            'recommended_bets': recommendations,
            'confidence_level': 'high' if confidence > 0.75 else 'moderate' if confidence > 0.6 else 'low'
        }

    def _generate_baseline_prediction(self, game: 'Game', config=None) -> Dict:
        """Generate baseline prediction when model unavailable"""
        # Use sport-specific home advantage if config provided
        if config:
            home_advantage = config.home_advantage
            spread = home_advantage
            home_prob = 0.50 + (home_advantage / 20)  # Rough estimate
        else:
            # NFL defaults (backward compatibility)
            home_advantage = 3.0
            spread = 3.0
            home_prob = 0.55

        return {
            'winner': game.home_team.name,
            'winner_abbr': game.home_team.abbreviation,
            'home_win_probability': round(home_prob, 3),
            'away_win_probability': round(1 - home_prob, 3),
            'predicted_spread': round(spread, 1),
            'confidence': 0.5,
            'model_used': 'baseline',
            'sport': config.sport_type if config else 'nfl',
            'key_factors': [f'Home advantage (~{home_advantage} points) - baseline prediction'],
            'recommendation': {
                'recommended_bets': [],
                'confidence_level': 'low'
            }
        }

    # ========== END NFL PREDICTIONS ==========

    def _extract_decision_features(self, decision_data: Dict[str, Any]) -> np.ndarray:
        """Extract features from user decision data"""
        # Placeholder - implement based on decision structure
        return np.array([0.6, 0.5, 0.9])  # Mock features

    def _record_user_decision(self, decision_data: Dict[str, Any], confidence: float):
        """Record user decision for learning"""
        # Placeholder - implement decision tracking
        pass

    def _analyze_options_to_sports(self, options_data: Dict, sports_data: Dict) -> Optional[PatternPrediction]:
        """Analyze options IV patterns for sports betting opportunities"""
        # Placeholder - implement options → sports analysis
        return None

    def _analyze_crypto_to_real_estate(self, crypto_data: Dict, real_estate_data: Dict) -> Optional[PatternPrediction]:
        """Analyze crypto patterns for real estate timing"""
        # Placeholder - implement crypto → real estate analysis
        return None

    def _analyze_sports_to_earnings(self, sports_schedule: Dict, earnings_calendar: Dict) -> Optional[PatternPrediction]:
        """Analyze sports timing patterns for earnings plays"""
        # Placeholder - implement sports → earnings analysis
        return None