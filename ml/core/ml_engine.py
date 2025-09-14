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
        self.models = {}
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
        model_files = {
            'sports_crypto_lstm': 'sports_crypto_pattern.joblib',
            'options_betting_nn': 'options_betting_edge.joblib',
            'user_behavior_rf': 'user_behavior_model.joblib',
            'cross_domain_gb': 'cross_domain_transfer.joblib'
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