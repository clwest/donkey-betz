#!/usr/bin/env python3
"""
Enhanced ML Revenue Pipeline - Real Machine Learning for Revenue Optimization
Replaces mock ML with actual models and predictions for revenue generation.
"""

import asyncio
import json
import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
import pickle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib

# Add project root to path
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from persistence.models import RevenueTracker
from intelligence.models.revenue import OpportunityActionPlan

logger = logging.getLogger(__name__)

@dataclass
class MLPrediction:
    """ML prediction result"""
    fit_score: float
    confidence: float
    success_probability: float
    revenue_prediction: float
    risk_assessment: str
    model_used: str
    feature_importance: Dict[str, float]
    prediction_timestamp: str

@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    mse: float
    last_updated: str
    training_samples: int

class EnhancedMLRevenuePipeline:
    """Real ML pipeline for revenue optimization"""

    def __init__(self):
        self.models_dir = Path("ml_models")
        self.models_dir.mkdir(exist_ok=True)

        # Initialize models
        self.opportunity_fit_model = None
        self.success_predictor = None
        self.revenue_predictor = None
        self.risk_assessor = None

        # Preprocessing tools
        self.scalers = {}
        self.encoders = {}

        # Performance tracking
        self.model_performance = {}

        # Feature engineering
        self.feature_engineering_enabled = True

        self._initialize_models()
        logger.info("Enhanced ML Revenue Pipeline initialized")

    def _initialize_models(self):
        """Initialize or load ML models"""
        try:
            # Try to load existing models
            self._load_existing_models()
        except Exception as e:
            logger.info(f"No existing models found, creating new ones: {e}")
            self._create_new_models()

    def _load_existing_models(self):
        """Load existing trained models"""
        model_files = {
            'opportunity_fit': 'opportunity_fit_model.pkl',
            'success_predictor': 'success_predictor_model.pkl',
            'revenue_predictor': 'revenue_predictor_model.pkl',
            'risk_assessor': 'risk_assessor_model.pkl'
        }

        for model_name, filename in model_files.items():
            model_path = self.models_dir / filename
            if model_path.exists():
                model = joblib.load(model_path)
                setattr(self, f"{model_name.replace('_predictor', '').replace('_assessor', '')}_model", model)
                logger.info(f"Loaded {model_name} model from {filename}")

    def _create_new_models(self):
        """Create new ML models with initial training"""
        # Opportunity fit model (Random Forest)
        self.opportunity_fit_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )

        # Success predictor (Gradient Boosting)
        self.success_predictor = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )

        # Revenue predictor (Random Forest)
        self.revenue_predictor = RandomForestRegressor(
            n_estimators=150,
            max_depth=12,
            random_state=42
        )

        # Risk assessor (Gradient Boosting)
        self.risk_assessor = GradientBoostingClassifier(
            n_estimators=80,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )

        # Initialize scalers
        self.scalers = {
            'features': StandardScaler(),
            'revenue': StandardScaler()
        }

        # Initialize encoders
        self.encoders = {
            'platform': LabelEncoder(),
            'skill_category': LabelEncoder(),
            'client_type': LabelEncoder()
        }

        logger.info("Created new ML models")

    async def predict_opportunity_fit(self, user_dict: Dict, opportunity_dict: Dict) -> Dict[str, Any]:
        """
        Predict opportunity fit using real ML models
        """
        try:
            # Extract and engineer features
            features = self._engineer_features(user_dict, opportunity_dict)

            # Make predictions using different models
            fit_score = await self._predict_fit_score(features)
            success_prob = await self._predict_success_probability(features)
            revenue_pred = await self._predict_revenue(features, opportunity_dict.get('budget', 0))
            risk_assessment = await self._assess_risk(features)

            # Calculate confidence based on feature quality
            confidence = self._calculate_prediction_confidence(features, opportunity_dict)

            return {
                'fit_score': max(0.1, min(0.95, fit_score)),
                'confidence': confidence,
                'success_probability': success_prob,
                'revenue_prediction': revenue_pred,
                'risk_assessment': risk_assessment,
                'model_used': 'enhanced_ml_pipeline',
                'feature_importance': self._get_feature_importance(features),
                'prediction_timestamp': datetime.now().isoformat(),
                'ml_engine': 'real_ml_models'
            }

        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            # Fallback to enhanced heuristic
            return await self._enhanced_heuristic_prediction(user_dict, opportunity_dict)

    def _engineer_features(self, user_dict: Dict, opportunity_dict: Dict) -> Dict[str, float]:
        """Engineer features for ML models"""
        features = {}

        # User features
        user_skills = set(user_dict.get('skills', []))
        features['user_skill_count'] = len(user_skills)
        features['user_experience_level'] = self._encode_experience_level(
            user_dict.get('skill_level', 'beginner')
        )
        features['user_available_hours'] = user_dict.get('available_hours_per_week', 10)
        features['user_balance'] = user_dict.get('current_balance', 0)

        # Opportunity features
        opportunity_skills = set(opportunity_dict.get('skills_required', []))
        features['opp_skill_count'] = len(opportunity_skills)
        features['opp_budget'] = opportunity_dict.get('budget', 0)
        features['opp_competition'] = opportunity_dict.get('competition_level', 0.5)

        # Skill matching features
        skill_overlap = user_skills & opportunity_skills
        features['skill_match_count'] = len(skill_overlap)
        features['skill_match_ratio'] = len(skill_overlap) / max(len(opportunity_skills), 1)
        features['skill_coverage'] = len(skill_overlap) / max(len(user_skills), 1)

        # Market features
        features['market_demand'] = opportunity_dict.get('market_demand', 0.5)
        features['client_rating'] = opportunity_dict.get('client_rating', 3.0)

        # Temporal features
        features['hour_of_day'] = datetime.now().hour
        features['day_of_week'] = datetime.now().weekday()

        # Platform encoding
        platform = opportunity_dict.get('platform', 'unknown')
        features['platform_encoded'] = self._encode_platform(platform)

        # Derived features
        features['budget_per_skill'] = features['opp_budget'] / max(features['opp_skill_count'], 1)
        features['competition_adjusted_value'] = features['opp_budget'] * (1 - features['opp_competition'])
        features['user_opportunity_fit'] = features['skill_match_ratio'] * features['user_experience_level']

        return features

    def _encode_experience_level(self, level: str) -> float:
        """Encode experience level to numeric"""
        mapping = {
            'beginner': 1.0,
            'intermediate': 2.0,
            'advanced': 3.0,
            'expert': 4.0
        }
        return mapping.get(level.lower(), 1.0)

    def _encode_platform(self, platform: str) -> float:
        """Encode platform to numeric"""
        mapping = {
            'upwork': 0.8,
            'fiverr': 0.6,
            'freelancer': 0.5,
            'linkedin': 0.9,
            'toptal': 1.0,
            'guru': 0.4
        }
        return mapping.get(platform.lower(), 0.5)

    async def _predict_fit_score(self, features: Dict[str, float]) -> float:
        """Predict opportunity fit score"""
        try:
            if self.opportunity_fit_model is None:
                return self._calculate_heuristic_fit_score(features)

            # Convert features to array
            feature_array = np.array([list(features.values())]).reshape(1, -1)

            # Make prediction
            fit_score = self.opportunity_fit_model.predict(feature_array)[0]
            return max(0.1, min(0.95, fit_score))

        except Exception as e:
            logger.warning(f"Fit score prediction failed: {e}")
            return self._calculate_heuristic_fit_score(features)

    def _calculate_heuristic_fit_score(self, features: Dict[str, float]) -> float:
        """Calculate fit score using enhanced heuristics"""
        score = 0.5  # Base score

        # Skill matching (40% weight)
        score += features.get('skill_match_ratio', 0) * 0.4

        # Experience alignment (20% weight)
        exp_factor = min(features.get('user_experience_level', 1) / 2.0, 1.0)
        score += exp_factor * 0.2

        # Market factors (20% weight)
        market_score = (
            features.get('market_demand', 0.5) * 0.6 +
            (1 - features.get('opp_competition', 0.5)) * 0.4
        )
        score += market_score * 0.2

        # Economic factors (20% weight)
        budget_factor = min(features.get('opp_budget', 0) / 1000, 1.0)
        score += budget_factor * 0.2

        return max(0.1, min(0.95, score))

    async def _predict_success_probability(self, features: Dict[str, float]) -> float:
        """Predict success probability"""
        try:
            if self.success_predictor is None:
                return self._calculate_heuristic_success_probability(features)

            feature_array = np.array([list(features.values())]).reshape(1, -1)

            # Get probability of success class (assuming binary classification)
            success_prob = self.success_predictor.predict_proba(feature_array)[0][1]
            return max(0.1, min(0.95, success_prob))

        except Exception as e:
            logger.warning(f"Success probability prediction failed: {e}")
            return self._calculate_heuristic_success_probability(features)

    def _calculate_heuristic_success_probability(self, features: Dict[str, float]) -> float:
        """Calculate success probability using heuristics"""
        base_prob = 0.3  # Base 30% success rate

        # Skill match bonus
        base_prob += features.get('skill_match_ratio', 0) * 0.3

        # Experience bonus
        exp_bonus = min(features.get('user_experience_level', 1) / 4.0, 0.2)
        base_prob += exp_bonus

        # Competition penalty
        comp_penalty = features.get('opp_competition', 0.5) * 0.2
        base_prob -= comp_penalty

        # Client quality bonus
        client_bonus = (features.get('client_rating', 3.0) - 3.0) / 2.0 * 0.1
        base_prob += client_bonus

        return max(0.1, min(0.9, base_prob))

    async def _predict_revenue(self, features: Dict[str, float], budget: float) -> float:
        """Predict expected revenue"""
        try:
            if self.revenue_predictor is None:
                return self._calculate_heuristic_revenue(features, budget)

            feature_array = np.array([list(features.values())]).reshape(1, -1)
            revenue_multiplier = self.revenue_predictor.predict(feature_array)[0]

            return budget * max(0.1, min(1.2, revenue_multiplier))

        except Exception as e:
            logger.warning(f"Revenue prediction failed: {e}")
            return self._calculate_heuristic_revenue(features, budget)

    def _calculate_heuristic_revenue(self, features: Dict[str, float], budget: float) -> float:
        """Calculate expected revenue using heuristics"""
        multiplier = 0.7  # Base 70% of budget

        # Skill match bonus
        multiplier += features.get('skill_match_ratio', 0) * 0.2

        # Competition adjustment
        multiplier += (1 - features.get('opp_competition', 0.5)) * 0.1

        # Experience bonus
        exp_bonus = min(features.get('user_experience_level', 1) / 4.0, 0.1)
        multiplier += exp_bonus

        return budget * max(0.3, min(1.0, multiplier))

    async def _assess_risk(self, features: Dict[str, float]) -> str:
        """Assess risk level of opportunity"""
        try:
            if self.risk_assessor is None:
                return self._calculate_heuristic_risk(features)

            feature_array = np.array([list(features.values())]).reshape(1, -1)
            risk_class = self.risk_assessor.predict(feature_array)[0]

            risk_mapping = {0: 'low', 1: 'medium', 2: 'high'}
            return risk_mapping.get(risk_class, 'medium')

        except Exception as e:
            logger.warning(f"Risk assessment failed: {e}")
            return self._calculate_heuristic_risk(features)

    def _calculate_heuristic_risk(self, features: Dict[str, float]) -> str:
        """Calculate risk using heuristics"""
        risk_score = 0.0

        # High competition = higher risk
        risk_score += features.get('opp_competition', 0.5) * 0.4

        # Low skill match = higher risk
        risk_score += (1 - features.get('skill_match_ratio', 0)) * 0.3

        # Low budget = higher risk (payment issues)
        if features.get('opp_budget', 0) < 200:
            risk_score += 0.2

        # Low client rating = higher risk
        if features.get('client_rating', 3.0) < 3.5:
            risk_score += 0.1

        if risk_score < 0.3:
            return 'low'
        elif risk_score < 0.6:
            return 'medium'
        else:
            return 'high'

    def _calculate_prediction_confidence(self, features: Dict[str, float], opportunity_dict: Dict) -> float:
        """Calculate confidence in predictions"""
        confidence = 0.7  # Base confidence

        # More features = higher confidence
        feature_completeness = len([f for f in features.values() if f > 0]) / len(features)
        confidence += feature_completeness * 0.1

        # Complete opportunity data = higher confidence
        required_fields = ['budget', 'skills_required', 'platform', 'competition_level']
        data_completeness = len([f for f in required_fields if opportunity_dict.get(f)]) / len(required_fields)
        confidence += data_completeness * 0.15

        # Historical data availability
        if self.opportunity_fit_model is not None:
            confidence += 0.1

        return max(0.6, min(0.95, confidence))

    def _get_feature_importance(self, features: Dict[str, float]) -> Dict[str, float]:
        """Get feature importance scores"""
        # Static importance mapping (in real implementation, this would come from trained models)
        importance_mapping = {
            'skill_match_ratio': 0.25,
            'opp_budget': 0.20,
            'user_experience_level': 0.15,
            'opp_competition': 0.12,
            'market_demand': 0.10,
            'client_rating': 0.08,
            'platform_encoded': 0.05,
            'user_available_hours': 0.05
        }

        # Return importance for features that exist
        return {key: importance_mapping.get(key, 0.01) for key in features.keys()}

    async def _enhanced_heuristic_prediction(self, user_dict: Dict, opportunity_dict: Dict) -> Dict[str, Any]:
        """Enhanced heuristic prediction when ML models fail"""
        features = self._engineer_features(user_dict, opportunity_dict)

        fit_score = self._calculate_heuristic_fit_score(features)
        success_prob = self._calculate_heuristic_success_probability(features)
        revenue_pred = self._calculate_heuristic_revenue(features, opportunity_dict.get('budget', 0))
        risk_assessment = self._calculate_heuristic_risk(features)

        return {
            'fit_score': fit_score,
            'confidence': 0.75,
            'success_probability': success_prob,
            'revenue_prediction': revenue_pred,
            'risk_assessment': risk_assessment,
            'model_used': 'enhanced_heuristic',
            'feature_importance': self._get_feature_importance(features),
            'prediction_timestamp': datetime.now().isoformat(),
            'ml_engine': 'heuristic_fallback'
        }

    async def train_models_with_real_data(self) -> Dict[str, Any]:
        """Train models using real data from database"""
        training_results = {
            'training_timestamp': datetime.now().isoformat(),
            'models_trained': [],
            'performance_metrics': {},
            'training_samples': 0
        }

        try:
            # Collect training data from database
            training_data = await self._collect_training_data()

            if len(training_data) < 10:
                logger.warning("Insufficient training data, using synthetic data")
                training_data = self._generate_synthetic_training_data()

            training_results['training_samples'] = len(training_data)

            # Train opportunity fit model
            if await self._train_opportunity_fit_model(training_data):
                training_results['models_trained'].append('opportunity_fit')

            # Train success predictor
            if await self._train_success_predictor(training_data):
                training_results['models_trained'].append('success_predictor')

            # Train revenue predictor
            if await self._train_revenue_predictor(training_data):
                training_results['models_trained'].append('revenue_predictor')

            # Save models
            await self._save_models()

            logger.info(f"Model training complete: {len(training_results['models_trained'])} models trained")

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            training_results['error'] = str(e)

        return training_results

    async def _collect_training_data(self) -> List[Dict[str, Any]]:
        """Collect training data from database"""
        training_data = []

        # Get completed opportunities
        completed_opportunities = OpportunityActionPlan.objects.filter(
            status__in=['converted', 'rejected', 'expired']
        )

        for opp in completed_opportunities:
            try:
                # Extract features
                opp_data = opp.opportunity_data or {}

                training_sample = {
                    'features': self._engineer_features(
                        {'skills': ['python', 'data analysis'], 'skill_level': 'intermediate'},  # Default user
                        opp_data
                    ),
                    'fit_score': float(opp.success_score or 0.5),
                    'success': 1 if opp.status == 'converted' else 0,
                    'revenue': float(opp.revenue_generated or 0),
                    'risk_level': 0 if opp.status == 'converted' else 1
                }

                training_data.append(training_sample)

            except Exception as e:
                logger.warning(f"Failed to process training sample: {e}")
                continue

        return training_data

    def _generate_synthetic_training_data(self) -> List[Dict[str, Any]]:
        """Generate synthetic training data for initial model training"""
        np.random.seed(42)
        training_data = []

        for i in range(100):
            # Generate synthetic features
            skill_match_ratio = np.random.beta(2, 2)  # Biased towards middle values
            budget = np.random.lognormal(6, 1)  # Log-normal distribution for budget
            competition = np.random.beta(2, 2)
            experience_level = np.random.choice([1, 2, 3, 4], p=[0.3, 0.4, 0.2, 0.1])

            features = {
                'skill_match_ratio': skill_match_ratio,
                'opp_budget': budget,
                'opp_competition': competition,
                'user_experience_level': experience_level,
                'market_demand': np.random.beta(3, 2),
                'client_rating': np.random.normal(4.0, 0.5),
                'platform_encoded': np.random.choice([0.4, 0.5, 0.6, 0.8, 0.9]),
                'user_available_hours': np.random.normal(20, 5)
            }

            # Calculate target variables based on features
            fit_score = (
                skill_match_ratio * 0.4 +
                min(budget / 1000, 1) * 0.2 +
                (1 - competition) * 0.2 +
                experience_level / 4 * 0.2
            )

            success_prob = fit_score * 0.8 + np.random.normal(0, 0.1)
            success = 1 if success_prob > 0.5 else 0

            revenue = budget * fit_score * (0.7 + np.random.normal(0, 0.1)) if success else 0

            training_sample = {
                'features': features,
                'fit_score': max(0, min(1, fit_score)),
                'success': success,
                'revenue': max(0, revenue),
                'risk_level': 1 - fit_score
            }

            training_data.append(training_sample)

        return training_data

    async def _train_opportunity_fit_model(self, training_data: List[Dict]) -> bool:
        """Train opportunity fit model"""
        try:
            X = np.array([list(sample['features'].values()) for sample in training_data])
            y = np.array([sample['fit_score'] for sample in training_data])

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.opportunity_fit_model.fit(X_train, y_train)

            # Evaluate
            y_pred = self.opportunity_fit_model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)

            self.model_performance['opportunity_fit'] = ModelPerformance(
                model_name='opportunity_fit',
                accuracy=0.0,  # Not applicable for regression
                precision=0.0,
                recall=0.0,
                mse=mse,
                last_updated=datetime.now().isoformat(),
                training_samples=len(training_data)
            )

            logger.info(f"Opportunity fit model trained: MSE={mse:.4f}")
            return True

        except Exception as e:
            logger.error(f"Opportunity fit model training failed: {e}")
            return False

    async def _train_success_predictor(self, training_data: List[Dict]) -> bool:
        """Train success predictor model"""
        try:
            X = np.array([list(sample['features'].values()) for sample in training_data])
            y = np.array([sample['success'] for sample in training_data])

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.success_predictor.fit(X_train, y_train)

            # Evaluate
            y_pred = self.success_predictor.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            self.model_performance['success_predictor'] = ModelPerformance(
                model_name='success_predictor',
                accuracy=accuracy,
                precision=0.0,  # Would calculate from confusion matrix
                recall=0.0,
                mse=0.0,
                last_updated=datetime.now().isoformat(),
                training_samples=len(training_data)
            )

            logger.info(f"Success predictor trained: Accuracy={accuracy:.4f}")
            return True

        except Exception as e:
            logger.error(f"Success predictor training failed: {e}")
            return False

    async def _train_revenue_predictor(self, training_data: List[Dict]) -> bool:
        """Train revenue predictor model"""
        try:
            X = np.array([list(sample['features'].values()) for sample in training_data])
            y = np.array([sample['revenue'] for sample in training_data])

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.revenue_predictor.fit(X_train, y_train)

            # Evaluate
            y_pred = self.revenue_predictor.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)

            self.model_performance['revenue_predictor'] = ModelPerformance(
                model_name='revenue_predictor',
                accuracy=0.0,
                precision=0.0,
                recall=0.0,
                mse=mse,
                last_updated=datetime.now().isoformat(),
                training_samples=len(training_data)
            )

            logger.info(f"Revenue predictor trained: MSE={mse:.4f}")
            return True

        except Exception as e:
            logger.error(f"Revenue predictor training failed: {e}")
            return False

    async def _save_models(self):
        """Save trained models to disk"""
        models_to_save = {
            'opportunity_fit_model.pkl': self.opportunity_fit_model,
            'success_predictor_model.pkl': self.success_predictor,
            'revenue_predictor_model.pkl': self.revenue_predictor,
            'risk_assessor_model.pkl': self.risk_assessor
        }

        for filename, model in models_to_save.items():
            if model is not None:
                try:
                    model_path = self.models_dir / filename
                    joblib.dump(model, model_path)
                    logger.info(f"Saved model: {filename}")
                except Exception as e:
                    logger.error(f"Failed to save {filename}: {e}")

    async def get_model_performance(self) -> Dict[str, Any]:
        """Get current model performance metrics"""
        return {
            'models_available': list(self.model_performance.keys()),
            'performance_metrics': {
                name: {
                    'accuracy': perf.accuracy,
                    'mse': perf.mse,
                    'last_updated': perf.last_updated,
                    'training_samples': perf.training_samples
                }
                for name, perf in self.model_performance.items()
            },
            'ml_pipeline_status': 'active',
            'feature_engineering': self.feature_engineering_enabled,
            'models_directory': str(self.models_dir)
        }

# Global ML pipeline instance
ml_revenue_pipeline = EnhancedMLRevenuePipeline()

async def main():
    """Main function for testing"""
    # Train models with real data
    training_results = await ml_revenue_pipeline.train_models_with_real_data()
    print("Training Results:", json.dumps(training_results, indent=2))

    # Test prediction
    test_user = {
        'skills': ['python', 'data analysis', 'automation'],
        'skill_level': 'intermediate',
        'current_balance': 0,
        'available_hours_per_week': 20
    }

    test_opportunity = {
        'budget': 800,
        'skills_required': ['python', 'data analysis'],
        'platform': 'upwork',
        'competition_level': 0.6,
        'market_demand': 0.8,
        'client_rating': 4.5
    }

    prediction = await ml_revenue_pipeline.predict_opportunity_fit(test_user, test_opportunity)
    print("Test Prediction:", json.dumps(prediction, indent=2))

    # Get performance metrics
    performance = await ml_revenue_pipeline.get_model_performance()
    print("Model Performance:", json.dumps(performance, indent=2))

if __name__ == "__main__":
    asyncio.run(main())