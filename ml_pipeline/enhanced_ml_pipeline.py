"""
Enhanced ML Pipeline for Intelligent Job Matching
Provides ML-powered matching, learning, and optimization for job-agent pairing
"""

import logging
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pickle
import os
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

logger = logging.getLogger(__name__)


class EnhancedMLPipeline:
    """
    Enhanced ML Pipeline for job matching with continuous learning
    """

    def __init__(self, model_dir: str = "ml_models"):
        """
        Initialize the ML Pipeline

        Args:
            model_dir: Directory to store trained models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)

        # Initialize models
        self.match_predictor = None
        self.success_predictor = None
        self.feature_scaler = StandardScaler()

        # Model paths
        self.match_model_path = self.model_dir / "job_match_model.pkl"
        self.success_model_path = self.model_dir / "success_predictor.pkl"
        self.scaler_path = self.model_dir / "feature_scaler.pkl"

        # Training data storage
        self.training_data = []
        self.model_version = "1.0.0"

        # Feature importance tracking
        self.feature_importance = {}

        # Load existing models if available
        self._load_models()

        logger.info(f"🚀 Enhanced ML Pipeline initialized (version {self.model_version})")

    def _load_models(self):
        """Load pre-trained models if they exist"""
        try:
            if self.match_model_path.exists():
                self.match_predictor = joblib.load(self.match_model_path)
                logger.info("✅ Loaded existing match predictor model")
            else:
                # Create default model
                self.match_predictor = GradientBoostingRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    random_state=42
                )
                logger.info("📦 Created new match predictor model")

            if self.success_model_path.exists():
                self.success_predictor = joblib.load(self.success_model_path)
                logger.info("✅ Loaded existing success predictor model")
            else:
                # Create default model
                self.success_predictor = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                logger.info("📦 Created new success predictor model")

            if self.scaler_path.exists():
                self.feature_scaler = joblib.load(self.scaler_path)
                logger.info("✅ Loaded existing feature scaler")

        except Exception as e:
            logger.warning(f"Could not load models: {e}")
            self._initialize_default_models()

    def _initialize_default_models(self):
        """Initialize default models"""
        self.match_predictor = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )

        self.success_predictor = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )

        # Train with synthetic data to initialize
        self._train_with_synthetic_data()

    def _train_with_synthetic_data(self):
        """Train models with synthetic data for cold start"""
        logger.info("🎲 Training with synthetic data for cold start")

        # Generate synthetic training data
        n_samples = 1000
        np.random.seed(42)

        # Synthetic features
        X = np.random.randn(n_samples, 10)

        # Synthetic targets with some pattern
        y_match = 0.5 + 0.1 * X[:, 0] + 0.2 * X[:, 1] - 0.15 * X[:, 2] + 0.1 * np.random.randn(n_samples)
        y_match = np.clip(y_match, 0, 1)

        y_success = 0.4 + 0.15 * X[:, 3] + 0.25 * X[:, 4] + 0.1 * np.random.randn(n_samples)
        y_success = np.clip(y_success, 0, 1)

        # Fit models
        X_scaled = self.feature_scaler.fit_transform(X)
        self.match_predictor.fit(X_scaled, y_match)
        self.success_predictor.fit(X_scaled, y_success)

        logger.info("✅ Models initialized with synthetic data")

    async def predict_match_score(self, features: Dict[str, Any]) -> Dict[str, float]:
        """
        Predict match score for job-agent pairing

        Args:
            features: Feature dictionary containing job and agent characteristics

        Returns:
            Dictionary with match_score and confidence
        """
        try:
            # Extract and prepare features
            feature_vector = self._extract_features(features)

            # Scale features
            if len(self.feature_scaler.mean_) == 0:
                # Scaler not fitted yet, use raw features
                scaled_features = feature_vector
            else:
                scaled_features = self.feature_scaler.transform([feature_vector])[0]

            # Get prediction
            if self._is_model_trained(self.match_predictor):
                match_score = float(self.match_predictor.predict([scaled_features])[0])
            else:
                # Fallback to heuristic scoring
                match_score = self._heuristic_match_score(features)

            # Calculate confidence based on feature completeness
            confidence = self._calculate_confidence(features)

            return {
                'match_score': np.clip(match_score, 0, 1),
                'confidence': confidence,
                'model_version': self.model_version
            }

        except Exception as e:
            logger.warning(f"Prediction failed, using fallback: {e}")
            return {
                'match_score': 0.5,
                'confidence': 0.3,
                'model_version': self.model_version,
                'error': str(e)
            }

    def _extract_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Extract numerical features from feature dictionary"""
        # Core features for job matching
        feature_vector = []

        # Agent features
        feature_vector.append(features.get('agent_success_rate', 0.5))
        # Handle UUID or string agent ID
        agent_id = features.get('agent_id', '')
        if hasattr(agent_id, 'hex'):  # UUID object
            agent_id = str(agent_id)
        feature_vector.append(len(str(agent_id)) / 100)  # Normalized agent ID length

        # Job features
        job_category_map = {
            'senior': 0.8, 'mid-level': 0.5, 'junior': 0.3, 'management': 0.9
        }
        feature_vector.append(job_category_map.get(features.get('job_category', 'mid-level'), 0.5))

        seniority_map = {1: 0.3, 2: 0.5, 3: 0.8}
        feature_vector.append(seniority_map.get(features.get('job_seniority', 2), 0.5))

        feature_vector.append(min(features.get('required_skills_count', 5) / 10, 1.0))

        # Add embedding features if available
        embedding = features.get('job_embedding', [])
        if embedding and len(embedding) > 0:
            # Use first 5 embedding dimensions
            feature_vector.extend(embedding[:5])
        else:
            # Pad with zeros if no embedding
            feature_vector.extend([0.0] * 5)

        # Ensure consistent feature vector length
        while len(feature_vector) < 10:
            feature_vector.append(0.0)

        return np.array(feature_vector[:10])

    def _heuristic_match_score(self, features: Dict[str, Any]) -> float:
        """Calculate heuristic match score when ML model not available"""
        score = 0.5  # Base score

        # Boost for high agent success rate
        score += features.get('agent_success_rate', 0.5) * 0.2

        # Adjust for job seniority match
        if features.get('job_category') == 'senior':
            score += 0.1

        # Skill count consideration
        skills = features.get('required_skills_count', 0)
        if skills < 5:
            score += 0.1
        elif skills > 10:
            score -= 0.1

        return np.clip(score, 0, 1)

    def _calculate_confidence(self, features: Dict[str, Any]) -> float:
        """Calculate confidence based on feature completeness"""
        required_features = [
            'agent_id', 'job_category', 'job_seniority',
            'required_skills_count', 'agent_success_rate'
        ]

        available = sum(1 for f in required_features if f in features and features[f] is not None)
        base_confidence = available / len(required_features)

        # Boost confidence if embedding available
        if features.get('job_embedding'):
            base_confidence = min(1.0, base_confidence + 0.2)

        return base_confidence

    def _is_model_trained(self, model) -> bool:
        """Check if model has been trained"""
        try:
            return hasattr(model, 'n_features_in_') or hasattr(model, 'feature_importances_')
        except Exception as _e:
            logger.warning(
                "enhanced_ml_pipeline._is_model_trained: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False

    async def update_model(self, training_data: Dict[str, Any]):
        """
        Update model with new training data

        Args:
            training_data: Dictionary containing features, outcome, and feedback
        """
        try:
            # Store training data
            self.training_data.append({
                **training_data,
                'timestamp': datetime.now().isoformat()
            })

            # Retrain if enough new data
            if len(self.training_data) >= 50 and len(self.training_data) % 10 == 0:
                await self._retrain_models()

            logger.info(f"📊 Added training data (total: {len(self.training_data)} samples)")

        except Exception as e:
            logger.error(f"Failed to update model: {e}")

    async def _retrain_models(self):
        """Retrain models with accumulated data"""
        try:
            if len(self.training_data) < 20:
                logger.info("Not enough data for retraining")
                return

            logger.info(f"🔄 Retraining models with {len(self.training_data)} samples")

            # Prepare training data
            X = []
            y_match = []
            y_success = []

            for data in self.training_data:
                features = self._extract_features(data.get('features', {}))
                X.append(features)

                # Target for match score
                feedback = data.get('feedback_score', 0.5)
                y_match.append(feedback)

                # Target for success prediction
                outcome_map = {
                    'hired': 1.0, 'interview': 0.7,
                    'rejected': 0.2, 'pending': 0.5
                }
                outcome = outcome_map.get(data.get('outcome', 'pending'), 0.5)
                y_success.append(outcome)

            X = np.array(X)
            y_match = np.array(y_match)
            y_success = np.array(y_success)

            # Scale features
            X_scaled = self.feature_scaler.fit_transform(X)

            # Split data
            X_train, X_test, y_match_train, y_match_test = train_test_split(
                X_scaled, y_match, test_size=0.2, random_state=42
            )

            # Train match predictor
            self.match_predictor.fit(X_train, y_match_train)
            match_score = self.match_predictor.score(X_test, y_match_test)

            # Train success predictor
            self.success_predictor.fit(X_train, y_match_train)  # Using same targets for now

            # Update feature importance
            if hasattr(self.match_predictor, 'feature_importances_'):
                self.feature_importance['match'] = self.match_predictor.feature_importances_.tolist()

            # Save models
            self._save_models()

            # Update version
            self.model_version = f"1.{len(self.training_data)}.0"

            logger.info(f"✅ Models retrained (match R²: {match_score:.3f})")

        except Exception as e:
            logger.error(f"Retraining failed: {e}")

    def _save_models(self):
        """Save trained models to disk"""
        try:
            joblib.dump(self.match_predictor, self.match_model_path)
            joblib.dump(self.success_predictor, self.success_model_path)
            joblib.dump(self.feature_scaler, self.scaler_path)
            logger.info(f"💾 Models saved to {self.model_dir}")
        except Exception as e:
            logger.error(f"Failed to save models: {e}")

    async def get_feature_importance(self) -> Dict[str, Any]:
        """Get feature importance for interpretability"""
        importance = {
            'match_predictor': self.feature_importance.get('match', []),
            'feature_names': [
                'agent_success_rate', 'agent_id_norm', 'job_category',
                'job_seniority', 'skills_count', 'embedding_0',
                'embedding_1', 'embedding_2', 'embedding_3', 'embedding_4'
            ],
            'model_version': self.model_version
        }

        return importance

    async def predict_application_success(self, job_data: Dict, agent_data: Dict) -> float:
        """
        Predict success probability for a job application

        Args:
            job_data: Job information
            agent_data: Agent information

        Returns:
            Success probability (0-1)
        """
        try:
            # Combine features
            features = {
                'agent_id': agent_data.get('id', ''),
                'agent_success_rate': agent_data.get('success_rate', 0.5),
                'job_category': self._categorize_job(job_data),
                'job_seniority': self._extract_seniority(job_data),
                'required_skills_count': len(job_data.get('tags', [])),
                'job_embedding': job_data.get('embedding', [])
            }

            # Get prediction
            prediction = await self.predict_match_score(features)

            return prediction['match_score']

        except Exception as e:
            logger.warning(f"Success prediction failed: {e}")
            return 0.5

    def _categorize_job(self, job: Dict[str, Any]) -> str:
        """Categorize job into types"""
        title = job.get('title', '').lower()

        if 'senior' in title or 'lead' in title:
            return 'senior'
        elif 'junior' in title or 'entry' in title:
            return 'junior'
        elif 'manager' in title or 'director' in title:
            return 'management'
        else:
            return 'mid-level'

    def _extract_seniority(self, job: Dict[str, Any]) -> int:
        """Extract seniority level from job"""
        title = job.get('title', '').lower()

        if 'senior' in title or 'lead' in title:
            return 3
        elif 'mid' in title or not ('junior' in title or 'senior' in title):
            return 2
        else:
            return 1

    async def get_model_stats(self) -> Dict[str, Any]:
        """Get model statistics and health metrics"""
        return {
            'model_version': self.model_version,
            'training_samples': len(self.training_data),
            'match_model_trained': self._is_model_trained(self.match_predictor),
            'success_model_trained': self._is_model_trained(self.success_predictor),
            'feature_importance': self.feature_importance,
            'last_training': self.training_data[-1]['timestamp'] if self.training_data else None
        }


# Singleton instance
_ml_pipeline_instance = None


def get_ml_pipeline() -> EnhancedMLPipeline:
    """Get or create ML pipeline singleton"""
    global _ml_pipeline_instance
    if _ml_pipeline_instance is None:
        _ml_pipeline_instance = EnhancedMLPipeline()
    return _ml_pipeline_instance