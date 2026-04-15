"""
ML Engine - Core Machine Learning Pipeline
Optimized for Apple M3 with MLX framework
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np

# Apple ML Stack
try:
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    logging.warning("MLX not available - falling back to standard frameworks")

# Session 985: Heavy ML libraries loaded lazily to avoid ~800MB in Celery parent process
# torch (~500MB), sklearn (~100MB), transformers (~200MB) now imported inside methods
import joblib  # lightweight, ok at module level

def _detect_device() -> str:
    """Detect best available device without loading torch at import time."""
    try:
        import torch
        return "mps" if torch.backends.mps.is_available() else "cpu"
    except ImportError:
        return "cpu"


@dataclass
class MLConfig:
    """ML Engine Configuration"""
    # Use /tmp in production (Railway) for writable cache, local path for development
    model_cache_dir: str = os.environ.get('ML_MODEL_CACHE_DIR', '/tmp/ml_models/cache' if os.environ.get('RAILWAY_ENVIRONMENT') else 'models/cache')
    use_mlx: bool = MLX_AVAILABLE
    max_memory_gb: float = 8.0  # Reserve 10GB for system
    inference_timeout: int = 5000  # 5 second timeout
    batch_size: int = 32
    device: str = ""  # Set in __post_init__

    def __post_init__(self):
        if not self.device:
            self.device = _detect_device()

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

    # Session 1102: attributes that require lazy init on first read. __init__
    # sets these to placeholder values so attribute lookup succeeds, then
    # __getattribute__ transparently runs _ensure_initialized() the first time
    # any of them is accessed.
    _LAZY_STATE_ATTRS = frozenset([
        'models', 'sport_models', 'scalers',
        'user_profile', 'sentiment_analyzer',
    ])

    def __getattribute__(self, name):
        if name in MLEngine._LAZY_STATE_ATTRS:
            init_done = object.__getattribute__(self, '_initialized')
            if not init_done:
                object.__getattribute__(self, '_ensure_initialized')()
        return object.__getattribute__(self, name)

    def __init__(self, config: MLConfig = None):
        # Session 1102: Cheap __init__ only — heavy ML/NLP init is deferred to
        # first public method call via _ensure_initialized(). Loading DistilBERT
        # + MPS device init in __init__ caused Celery worker mutex deadlocks on
        # macOS when MLEngine was instantiated from a scheduled task early in
        # worker startup (see docs/topics/celery-workers.md). The same rule
        # Session 985 already applied to module-level imports now extends to
        # instantiation-time side effects.
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
        self.sentiment_analyzer = None
        self._initialized = False

        # Initialize logging only — no heavy work here.
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _ensure_initialized(self):
        """Lazily load models + NLP pipelines on first use.

        Idempotent — safe to call from every public method entrypoint.
        Flag is flipped FIRST so that any self.models / self.user_profile
        access inside the init path doesn't re-enter via __getattribute__.
        """
        if self._initialized:
            return
        self._initialized = True
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
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor

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
        if os.environ.get('SKIP_NLP_MODELS', '').lower() in ('1', 'true', 'yes'):
            self.logger.info("SKIP_NLP_MODELS set — skipping DistilBERT sentiment model load")
            self.sentiment_analyzer = None
            return
        try:
            import torch
            from transformers import pipeline as hf_pipeline
            # Use DistilBERT for fast local sentiment analysis
            self.sentiment_analyzer = hf_pipeline(
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

    def predict_game(self, game_id: str, sport_type: str, agent=None) -> Dict[str, Any]:
        """
        Universal game prediction for any sport with optional agent learning

        Args:
            game_id: Game ID to predict
            sport_type: Sport type ('nfl', 'nba', 'mlb', 'nhl')
            agent: Optional UnifiedAgentTemplate instance for agent learning

        Returns:
            Dictionary with prediction results (includes agent adjustments if agent provided)
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

                # Check if model has predict_proba (classifiers)
                if hasattr(model, 'predict_proba'):
                    # Random Forest or other classifier - use probabilities
                    prediction_proba = model.predict_proba([features])
                    prediction_raw = prediction_proba[0][1]  # Probability of home win (class 1)
                else:
                    # MLP Regressor - returns single value
                    prediction_raw = model.predict([features])

                prediction = self._format_prediction(prediction_raw, game, config)

                # Apply agent learning if agent provided
                if agent:
                    prediction = self._apply_agent_learning(prediction, agent, sport_type)

                return prediction
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
            elif feature_name == 'goals_differential':
                # NHL: Goals per game differential
                features.append(home_stats['points_per_game'] - away_stats['points_per_game'])
            elif feature_name == 'goals_against_differential':
                # NHL: Goals against differential (defensive strength)
                features.append(away_stats['points_allowed'] - home_stats['points_allowed'])
            elif feature_name == 'recent_form_differential':
                # Recent form (last 5 games win rate)
                home_form = home_stats.get('recent_form', 0.5)
                away_form = away_stats.get('recent_form', 0.5)
                features.append(home_form - away_form)
            elif feature_name == 'goal_differential_variance':
                # Consistency: how consistent is the goal differential
                home_variance = home_stats.get('goal_variance', 0.0)
                away_variance = away_stats.get('goal_variance', 0.0)
                features.append(away_variance - home_variance)  # Lower variance = more consistent
            elif feature_name in ['back_to_back', 'pitcher_matchup_rating', 'weather_factor',
                                   'runs_differential', 'era_differential', 'batting_avg_differential',
                                   'bullpen_era_differential']:
                # Other sport-specific features (placeholder for now)
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
            'shots_per_game': 30,  # NHL average
            'powerplay_pct': 0.20,  # NHL average ~20%
            'penalty_kill_pct': 0.80,  # NHL average ~80%
        }

        if not recent_games.exists():
            return stats

        total_points = 0
        total_points_allowed = 0
        wins = 0
        total_goals_for = 0
        total_goals_against = 0

        for game in recent_games:
            is_home = game.home_team == team

            if is_home:
                total_points += game.home_score or 0
                total_points_allowed += game.away_score or 0
                total_goals_for += game.home_score or 0
                total_goals_against += game.away_score or 0
                if game.home_score > game.away_score:
                    wins += 1
            else:
                total_points += game.away_score or 0
                total_points_allowed += game.home_score or 0
                total_goals_for += game.away_score or 0
                total_goals_against += game.home_score or 0
                if game.away_score > game.home_score:
                    wins += 1

        count = recent_games.count()
        stats['points_per_game'] = total_points / count if count > 0 else 0
        stats['points_allowed'] = total_points_allowed / count if count > 0 else 0
        stats['win_rate'] = wins / count if count > 0 else 0

        # Calculate recent form and variance (useful for all sports, especially NHL)
        if count > 0:
            # Recent form: Win rate in last 5 games
            recent_5 = list(recent_games)[:min(5, count)]
            recent_wins = 0
            for g in recent_5:
                is_home = g.home_team == team
                if is_home and g.home_score > g.away_score:
                    recent_wins += 1
                elif not is_home and g.away_score > g.home_score:
                    recent_wins += 1
            stats['recent_form'] = recent_wins / len(recent_5) if recent_5 else 0.5

            # Goal differential variance: Measure consistency
            goal_diffs = []
            for g in recent_games:
                is_home = g.home_team == team
                if is_home:
                    goal_diff = (g.home_score or 0) - (g.away_score or 0)
                else:
                    goal_diff = (g.away_score or 0) - (g.home_score or 0)
                goal_diffs.append(goal_diff)

            if len(goal_diffs) > 1:
                mean_diff = sum(goal_diffs) / len(goal_diffs)
                variance = sum((x - mean_diff) ** 2 for x in goal_diffs) / len(goal_diffs)
                stats['goal_variance'] = variance
            else:
                stats['goal_variance'] = 0.0

        return stats

    def _calculate_goalie_save_percentage(self, team: 'Team', games: int = 10) -> float:
        """
        Calculate goalie save percentage for NHL teams.

        Uses recent games to estimate: Save% = 1 - (Goals Against / (Goals Against + Saves))
        Since we only have scores, we estimate: Save% ≈ 1 - (Goals Against / Estimated Shots Against)
        NHL average shots per game ≈ 30

        Args:
            team: Team object
            games: Number of recent games to analyze

        Returns:
            Save percentage (0.0 to 1.0), defaults to 0.900 (NHL average)
        """
        from sports.models import Game
        from django.db.models import Q

        # Get recent completed games
        recent_games = Game.objects.filter(
            Q(home_team=team) | Q(away_team=team),
            status='final',
            league__sport_type='nhl'
        ).order_by('-scheduled_start')[:games]

        if not recent_games.exists():
            return 0.900  # NHL average

        total_goals_against = 0
        total_estimated_shots_against = 0

        for game in recent_games:
            is_home = game.home_team == team

            # Goals against
            goals_against = game.away_score if is_home else game.home_score
            total_goals_against += goals_against or 0

            # Estimate shots against (NHL average is ~30 shots/game)
            # Better teams force fewer shots, worse teams face more
            estimated_shots = 30
            total_estimated_shots_against += estimated_shots

        # Calculate save percentage
        if total_estimated_shots_against > 0:
            saves = total_estimated_shots_against - total_goals_against
            save_pct = saves / total_estimated_shots_against
            return max(0.0, min(1.0, save_pct))  # Clamp between 0 and 1

        return 0.900  # Default to NHL average

    def _format_prediction(self, prediction_raw, game: 'Game', config) -> Dict:
        """
        Format raw prediction into sport-friendly output

        Works for any sport using SportConfig
        """
        # Convert model output to probability
        # If prediction_raw is already a probability (from Random Forest), use it directly
        if isinstance(prediction_raw, (float, np.floating)):
            home_win_prob = prediction_raw
        elif isinstance(prediction_raw, np.ndarray) and len(prediction_raw) == 1:
            # MLP Regressor output - apply sigmoid
            home_win_prob = 1 / (1 + np.exp(-prediction_raw[0]))
        else:
            # Fallback
            home_win_prob = 0.5

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

    def _apply_agent_learning(self, prediction: Dict, agent, sport_type: str) -> Dict:
        """
        Apply agent learning adjustments to base prediction

        Phase 3: Agent Learning Integration
        - Adjusts confidence based on agent's track record
        - Checks if agent should make this prediction
        - Adds agent specialization info to prediction

        Args:
            prediction: Base prediction dictionary
            agent: UnifiedAgentTemplate instance
            sport_type: Sport type ('nfl', 'nba', 'mlb', 'nhl')

        Returns:
            Enhanced prediction with agent learning applied
        """
        from intelligence.agent_learning import AgentLearningSystem

        try:
            learning_system = AgentLearningSystem(agent)

            # Check if agent should make this prediction
            if not learning_system.should_make_prediction(sport_type):
                self.logger.info(
                    f"Agent {agent.name} declining {sport_type.upper()} prediction due to poor track record"
                )
                prediction['agent_declined'] = True
                prediction['decline_reason'] = f"Agent has weak track record in {sport_type.upper()}"
                return prediction

            # Get confidence adjustment based on track record
            confidence_adjustment = learning_system.get_confidence_adjustment(sport_type)
            original_confidence = prediction['confidence']
            adjusted_confidence = original_confidence * confidence_adjustment

            # Clamp to valid range (0.5 to 1.0)
            adjusted_confidence = max(0.5, min(1.0, adjusted_confidence))

            # Get agent specializations
            specializations = learning_system.get_specializations()

            # Update prediction with agent learning data
            prediction['confidence'] = round(adjusted_confidence, 3)
            prediction['agent_learning'] = {
                'agent_name': agent.name,
                'original_confidence': round(original_confidence, 3),
                'confidence_adjustment': round(confidence_adjustment, 3),
                'adjusted_confidence': round(adjusted_confidence, 3),
                'agent_status': specializations.get('status', 'new_agent'),
                'total_predictions': specializations.get('total_predictions', 0),
                'specializations': specializations.get('specializations', []),
            }

            # Add note to key factors if confidence was adjusted
            if confidence_adjustment != 1.0:
                adjustment_type = "boosted" if confidence_adjustment > 1.0 else "reduced"
                prediction['key_factors'].insert(0,
                    f"Agent confidence {adjustment_type} based on {sport_type.upper()} track record"
                )

            self.logger.info(
                f"Agent {agent.name}: {sport_type.upper()} confidence adjusted "
                f"{original_confidence:.3f} → {adjusted_confidence:.3f} (x{confidence_adjustment:.2f})"
            )

            return prediction

        except Exception as e:
            self.logger.error(f"Error applying agent learning: {e}")
            # Return original prediction if agent learning fails
            prediction['agent_learning_error'] = str(e)
            return prediction

    # ========== END NFL PREDICTIONS ==========

    def _extract_decision_features(self, decision_data: Dict[str, Any]) -> np.ndarray:
        """Extract features from user decision data"""
        # Placeholder - implement based on decision structure
        return np.array([0.6, 0.5, 0.9])  # Mock features

    def _record_user_decision(self, decision_data: Dict[str, Any], confidence: float):
        """Record user decision for learning"""
        # Placeholder - implement decision tracking

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