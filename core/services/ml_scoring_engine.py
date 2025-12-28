"""
ML Scoring Engine - XGBoost + SHAP Explainability
==================================================

Session 470: Market Intelligence Architecture Implementation
Policy: Hybrid rule + ML scoring with SHAP explainability

This engine provides:
1. Feature extraction from SpiderData
2. XGBoost-based opportunity scoring
3. SHAP explanations for each prediction
4. Hybrid scoring: 60% ML + 40% rule-based
5. Confidence calibration
6. Model versioning and persistence

Usage:
    from core.services.ml_scoring_engine import get_ml_scoring_engine

    engine = get_ml_scoring_engine()
    result = engine.score_opportunity(spider_data)
    explanation = result.get_explanation()
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import joblib

logger = logging.getLogger(__name__)

# Lazy imports for ML libraries (may not always be needed)
_xgboost = None
_shap = None
_sklearn = None


def _get_xgboost():
    global _xgboost
    if _xgboost is None:
        import xgboost as xgb
        _xgboost = xgb
    return _xgboost


def _get_shap():
    global _shap
    if _shap is None:
        import shap
        _shap = shap
    return _shap


def _get_sklearn():
    global _sklearn
    if _sklearn is None:
        from sklearn import preprocessing, model_selection, metrics
        _sklearn = {'preprocessing': preprocessing, 'model_selection': model_selection, 'metrics': metrics}
    return _sklearn


# Feature definitions
FEATURE_NAMES = [
    'relevance_score',           # 0-100 from spider
    'source_authority',          # Source quality score
    'data_freshness_hours',      # Hours since creation
    'title_length',              # Title character count
    'has_url',                   # Boolean: has source URL
    'category_tech',             # One-hot: tech category
    'category_financial',        # One-hot: financial category
    'category_jobs',             # One-hot: jobs category
    'category_creative',         # One-hot: creative category
    'category_news',             # One-hot: news category
    'keyword_ai',                # Boolean: contains AI keywords
    'keyword_trending',          # Boolean: contains trending keywords
    'keyword_urgent',            # Boolean: contains urgency keywords
    'keyword_opportunity',       # Boolean: contains opportunity keywords
    'historical_success_rate',   # Past success rate for similar items
]

# Source authority scores (0-100)
SOURCE_AUTHORITY = {
    'techcrunch': 90,
    'hackernews': 85,
    'producthunt': 80,
    'reddit': 75,
    'devto': 70,
    'medium': 65,
    'remoteok': 75,
    'weworkremotely': 75,
    'coingecko': 80,
    'yahoo_finance': 85,
    'bbc': 90,
    'reuters_rss': 95,
    'default': 50
}

# Keyword sets for feature extraction
AI_KEYWORDS = {'ai', 'ml', 'machine learning', 'deep learning', 'gpt', 'llm', 'neural', 'automation'}
TRENDING_KEYWORDS = {'viral', 'trending', 'hot', 'breaking', 'surge', 'boom', 'skyrocket'}
URGENT_KEYWORDS = {'urgent', 'asap', 'immediate', 'now', 'today', 'limited', 'deadline'}
OPPORTUNITY_KEYWORDS = {'opportunity', 'potential', 'growth', 'profit', 'revenue', 'income'}


@dataclass
class SHAPExplanation:
    """SHAP explanation for a scoring prediction."""
    base_value: float
    shap_values: List[float]
    feature_names: List[str]
    feature_values: List[float]

    def get_top_features(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get top N features by absolute SHAP value."""
        indexed = list(enumerate(self.shap_values))
        sorted_features = sorted(indexed, key=lambda x: abs(x[1]), reverse=True)

        top = []
        for idx, shap_val in sorted_features[:n]:
            top.append({
                'feature': self.feature_names[idx],
                'value': self.feature_values[idx],
                'shap_value': round(shap_val, 4),
                'impact': 'positive' if shap_val > 0 else 'negative'
            })
        return top

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'base_value': round(self.base_value, 4),
            'shap_values': [round(v, 4) for v in self.shap_values],
            'feature_names': self.feature_names,
            'feature_values': [round(v, 4) if isinstance(v, float) else v for v in self.feature_values],
            'top_features': self.get_top_features(5)
        }


@dataclass
class MLScoringResult:
    """Result from ML scoring with explanations."""
    success: bool
    ml_score: float = 0.0
    rule_score: float = 0.0
    hybrid_score: float = 0.0
    confidence: float = 0.0

    # Component scores (1-100)
    profit_potential: int = 50
    competition_level: int = 50
    effort_required: int = 50
    time_sensitivity: int = 50

    # Explanations
    shap_explanation: Optional[SHAPExplanation] = None
    rule_reasoning: Dict[str, str] = field(default_factory=dict)

    # Metadata
    model_version: str = "v1.0"
    features_used: List[str] = field(default_factory=list)
    scoring_time_ms: int = 0

    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            'success': self.success,
            'scores': {
                'ml_score': round(self.ml_score, 2),
                'rule_score': round(self.rule_score, 2),
                'hybrid_score': round(self.hybrid_score, 2),
                'confidence': round(self.confidence, 2),
            },
            'components': {
                'profit_potential': self.profit_potential,
                'competition_level': self.competition_level,
                'effort_required': self.effort_required,
                'time_sensitivity': self.time_sensitivity,
            },
            'explanation': self.shap_explanation.to_dict() if self.shap_explanation else None,
            'rule_reasoning': self.rule_reasoning,
            'metadata': {
                'model_version': self.model_version,
                'features_used': self.features_used,
                'scoring_time_ms': self.scoring_time_ms,
            },
            'error': self.error
        }


class MLScoringEngine:
    """
    ML-based opportunity scoring engine with SHAP explainability.

    Provides hybrid scoring combining:
    - XGBoost ML predictions (60% weight)
    - Rule-based heuristics (40% weight)
    - SHAP explanations for transparency
    """

    MODEL_DIR = Path(__file__).parent.parent / 'ml_models'
    MODEL_FILENAME = 'opportunity_scorer_{version}.joblib'

    # Hybrid scoring weights
    ML_WEIGHT = 0.6
    RULE_WEIGHT = 0.4

    def __init__(self):
        """Initialize the ML scoring engine."""
        self.model = None
        self.model_version = "v1.0"
        self.explainer = None
        self._feature_scaler = None
        self._is_trained = False

        # Try to load existing model
        self._load_model()

    def _load_model(self) -> bool:
        """Load trained model from disk if available."""
        # First check database for active model version
        try:
            from core.models_unified_system import MLModelVersion
            active_model = MLModelVersion.objects.filter(is_active=True).first()
            if active_model:
                self.model_version = active_model.version
        except Exception as e:
            logger.debug(f"Could not check MLModelVersion: {e}")

        model_path = self.MODEL_DIR / self.MODEL_FILENAME.format(version=self.model_version)

        if model_path.exists():
            try:
                saved_data = joblib.load(model_path)
                self.model = saved_data['model']
                self._feature_scaler = saved_data.get('scaler')
                self.model_version = saved_data.get('version', 'v1.0')
                self._is_trained = True

                # Create SHAP explainer
                shap = _get_shap()
                self.explainer = shap.TreeExplainer(self.model)

                logger.info(f"Loaded ML model {self.model_version} from {model_path}")
                return True
            except Exception as e:
                logger.warning(f"Failed to load model: {e}")

        logger.info("No trained model found, will use rule-based scoring until trained")
        return False

    def save_model(self) -> bool:
        """Save trained model to disk."""
        if not self.model:
            return False

        self.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        model_path = self.MODEL_DIR / self.MODEL_FILENAME.format(version=self.model_version)

        try:
            joblib.dump({
                'model': self.model,
                'scaler': self._feature_scaler,
                'version': self.model_version,
                'trained_at': datetime.now().isoformat(),
                'feature_names': FEATURE_NAMES
            }, model_path)
            logger.info(f"Saved ML model to {model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False

    def extract_features(self, spider_data) -> np.ndarray:
        """
        Extract features from a SpiderData instance.

        Returns a numpy array of shape (1, n_features)
        """
        from django.utils import timezone

        raw_data = spider_data.raw_data or {}
        title = raw_data.get('title', '') or ''
        title_lower = title.lower()

        # Calculate freshness
        age = timezone.now() - spider_data.created_at
        freshness_hours = age.total_seconds() / 3600

        # Determine category
        spider_name = spider_data.spider_name.lower()
        category = self._categorize_spider(spider_name)

        # Extract features
        features = [
            spider_data.relevance_score or 50,                          # relevance_score
            SOURCE_AUTHORITY.get(spider_name, SOURCE_AUTHORITY['default']),  # source_authority
            min(freshness_hours, 168),                                   # data_freshness_hours (cap at 1 week)
            min(len(title), 200),                                        # title_length
            1.0 if raw_data.get('url') else 0.0,                        # has_url
            1.0 if category == 'tech' else 0.0,                         # category_tech
            1.0 if category == 'financial' else 0.0,                    # category_financial
            1.0 if category == 'jobs' else 0.0,                         # category_jobs
            1.0 if category == 'creative' else 0.0,                     # category_creative
            1.0 if category == 'news' else 0.0,                         # category_news
            1.0 if any(kw in title_lower for kw in AI_KEYWORDS) else 0.0,           # keyword_ai
            1.0 if any(kw in title_lower for kw in TRENDING_KEYWORDS) else 0.0,     # keyword_trending
            1.0 if any(kw in title_lower for kw in URGENT_KEYWORDS) else 0.0,       # keyword_urgent
            1.0 if any(kw in title_lower for kw in OPPORTUNITY_KEYWORDS) else 0.0,  # keyword_opportunity
            self._get_historical_success_rate(spider_name),             # historical_success_rate
        ]

        return np.array([features])

    def _categorize_spider(self, spider_name: str) -> str:
        """Categorize spider by name."""
        tech_spiders = {'hackernews', 'devto', 'techcrunch', 'medium', 'producthunt', 'github'}
        financial_spiders = {'coingecko', 'yahoo_finance', 'etherscan', 'finnhub', 'polygon_finance'}
        job_spiders = {'remoteok', 'weworkremotely', 'adzuna', 'github_jobs'}
        creative_spiders = {'behance', 'dribbble', 'unsplash', 'awwwards'}
        news_spiders = {'bbc', 'reuters_rss', 'npr', 'axios', 'google_news'}

        if spider_name in tech_spiders:
            return 'tech'
        elif spider_name in financial_spiders:
            return 'financial'
        elif spider_name in job_spiders:
            return 'jobs'
        elif spider_name in creative_spiders:
            return 'creative'
        elif spider_name in news_spiders:
            return 'news'
        return 'other'

    def _get_historical_success_rate(self, spider_name: str) -> float:
        """Get historical success rate for a spider source."""
        # TODO: Query OpportunityOutcome for actual rates
        # For now, use default rates based on source type
        default_rates = {
            'remoteok': 0.65,
            'weworkremotely': 0.60,
            'hackernews': 0.55,
            'techcrunch': 0.50,
            'producthunt': 0.45,
            'coingecko': 0.40,
            'default': 0.35
        }
        return default_rates.get(spider_name, default_rates['default'])

    def _calculate_rule_score(self, spider_data, features: np.ndarray) -> Tuple[float, Dict[str, str]]:
        """
        Calculate rule-based score (existing OpportunityScoringAgent logic).

        Returns (score, reasoning_dict)
        """
        raw_data = spider_data.raw_data or {}
        title = raw_data.get('title', '') or ''
        title_lower = title.lower()

        # Base from relevance
        base = (spider_data.relevance_score or 50) / 2 + 25

        # Profit potential
        profit = min(100, max(1, int(base + 10)))
        profit_reasoning = f"Base profit from relevance score ({spider_data.relevance_score})"

        # Competition level
        competition = 50
        competition_reasoning = "Market saturation at default level"
        if any(kw in title_lower for kw in AI_KEYWORDS):
            competition += 15
            competition_reasoning = "High competition in AI/ML space"

        # Effort required
        effort = 40
        effort_reasoning = "Standard effort for content creation"

        # Time sensitivity
        timing = 60
        timing_reasoning = "Moderate time sensitivity"
        if any(kw in title_lower for kw in TRENDING_KEYWORDS):
            timing += 15
            timing_reasoning = "High urgency due to trending signals"

        # Calculate overall (same formula as OpportunityScoringAgent)
        competition_score = 100 - competition
        effort_score = 100 - effort
        overall = int(
            profit * 0.35 +
            competition_score * 0.35 +
            effort_score * 0.20 +
            timing * 0.10
        )

        reasoning = {
            'profit': profit_reasoning,
            'competition': competition_reasoning,
            'effort': effort_reasoning,
            'timing': timing_reasoning
        }

        return min(100, max(1, overall)), reasoning

    def _calculate_component_scores(self, hybrid_score: float, features: np.ndarray) -> Dict[str, int]:
        """Calculate component scores from hybrid score and features."""
        # Use features to adjust component distribution
        relevance = features[0, 0]  # relevance_score
        source_auth = features[0, 1]  # source_authority
        is_ai = features[0, 10]  # keyword_ai
        is_trending = features[0, 11]  # keyword_trending

        # Distribute hybrid score across components
        base = hybrid_score / 100.0

        profit = int(min(100, max(1, base * 100 + relevance * 0.3)))
        competition = int(min(100, max(1, 50 + is_ai * 20)))  # Higher for AI
        effort = int(min(100, max(1, 40 + (100 - source_auth) * 0.3)))  # Lower for authoritative sources
        timing = int(min(100, max(1, 60 + is_trending * 25)))  # Higher for trending

        return {
            'profit_potential': profit,
            'competition_level': competition,
            'effort_required': effort,
            'time_sensitivity': timing
        }

    def score_opportunity(self, spider_data) -> MLScoringResult:
        """
        Score an opportunity using hybrid ML + rule-based approach.

        Args:
            spider_data: SpiderData instance to score

        Returns:
            MLScoringResult with scores and explanations
        """
        import time
        start_time = time.time()

        try:
            # Extract features
            features = self.extract_features(spider_data)

            # Calculate rule-based score
            rule_score, rule_reasoning = self._calculate_rule_score(spider_data, features)

            # Calculate ML score if model is trained
            ml_score = 50.0  # Default
            shap_explanation = None

            if self._is_trained and self.model is not None:
                try:
                    # Scale features if scaler exists
                    scaled_features = features
                    if self._feature_scaler:
                        scaled_features = self._feature_scaler.transform(features)

                    # Predict
                    ml_pred = self.model.predict(scaled_features)[0]
                    ml_score = float(min(100, max(1, ml_pred * 100)))

                    # Get SHAP explanation
                    if self.explainer:
                        shap_values = self.explainer.shap_values(scaled_features)
                        if isinstance(shap_values, list):
                            shap_values = shap_values[0]  # For multi-output

                        shap_explanation = SHAPExplanation(
                            base_value=float(self.explainer.expected_value) if not isinstance(self.explainer.expected_value, np.ndarray) else float(self.explainer.expected_value[0]),
                            shap_values=shap_values[0].tolist() if len(shap_values.shape) > 1 else shap_values.tolist(),
                            feature_names=FEATURE_NAMES,
                            feature_values=features[0].tolist()
                        )
                except Exception as e:
                    logger.warning(f"ML scoring failed, falling back to rules: {e}")
                    ml_score = rule_score  # Fallback

            # Calculate hybrid score
            if self._is_trained:
                hybrid_score = self.ML_WEIGHT * ml_score + self.RULE_WEIGHT * rule_score
            else:
                hybrid_score = rule_score  # Pure rule-based if no model

            # Calculate confidence
            confidence = self._calculate_confidence(features, ml_score, rule_score)

            # Calculate component scores
            components = self._calculate_component_scores(hybrid_score, features)

            scoring_time = int((time.time() - start_time) * 1000)

            return MLScoringResult(
                success=True,
                ml_score=ml_score,
                rule_score=rule_score,
                hybrid_score=hybrid_score,
                confidence=confidence,
                profit_potential=components['profit_potential'],
                competition_level=components['competition_level'],
                effort_required=components['effort_required'],
                time_sensitivity=components['time_sensitivity'],
                shap_explanation=shap_explanation,
                rule_reasoning=rule_reasoning,
                model_version=self.model_version if self._is_trained else "rule_only",
                features_used=FEATURE_NAMES,
                scoring_time_ms=scoring_time
            )

        except Exception as e:
            logger.error(f"Scoring error: {e}")
            return MLScoringResult(
                success=False,
                error=str(e)
            )

    def _calculate_confidence(self, features: np.ndarray, ml_score: float, rule_score: float) -> float:
        """Calculate confidence score based on multiple factors."""
        # Base confidence
        confidence = 70.0

        # Increase if ML and rules agree
        score_diff = abs(ml_score - rule_score)
        if score_diff < 10:
            confidence += 15
        elif score_diff < 20:
            confidence += 5
        else:
            confidence -= 10  # Disagreement reduces confidence

        # Increase for high-quality sources
        source_auth = features[0, 1]
        if source_auth > 80:
            confidence += 5

        # Increase for fresh data
        freshness = features[0, 2]
        if freshness < 24:  # Less than 24 hours old
            confidence += 5
        elif freshness > 72:  # More than 3 days old
            confidence -= 5

        return min(100, max(0, confidence))

    def train_model(
        self,
        training_data: List[Dict[str, Any]],
        version: str = None
    ) -> Dict[str, Any]:
        """
        Train the XGBoost model on historical outcome data.

        Args:
            training_data: List of dicts with 'features' and 'outcome' keys
            version: Model version string

        Returns:
            Training metrics dict
        """
        if len(training_data) < 10:
            return {
                'success': False,
                'error': f'Insufficient training data: {len(training_data)} samples (need 10+)'
            }

        xgb = _get_xgboost()
        sklearn = _get_sklearn()
        shap = _get_shap()

        try:
            # Prepare data
            X = np.array([d['features'] for d in training_data])
            y = np.array([d['outcome'] for d in training_data])

            # Split data
            X_train, X_test, y_train, y_test = sklearn['model_selection'].train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Scale features
            self._feature_scaler = sklearn['preprocessing'].StandardScaler()
            X_train_scaled = self._feature_scaler.fit_transform(X_train)
            X_test_scaled = self._feature_scaler.transform(X_test)

            # Train XGBoost
            self.model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42,
                objective='reg:squarederror'
            )
            self.model.fit(X_train_scaled, y_train)

            # Evaluate
            train_pred = self.model.predict(X_train_scaled)
            test_pred = self.model.predict(X_test_scaled)

            train_mse = sklearn['metrics'].mean_squared_error(y_train, train_pred)
            test_mse = sklearn['metrics'].mean_squared_error(y_test, test_pred)
            train_r2 = sklearn['metrics'].r2_score(y_train, train_pred)
            test_r2 = sklearn['metrics'].r2_score(y_test, test_pred)

            # Create SHAP explainer
            self.explainer = shap.TreeExplainer(self.model)

            # Update version
            if version:
                self.model_version = version
            else:
                # Auto-increment version
                current_num = int(self.model_version.replace('v', '').split('.')[0])
                self.model_version = f"v{current_num + 1}.0"

            self._is_trained = True

            # Save model
            self.save_model()

            # Get feature importance
            importance = self.model.feature_importances_
            feature_importance = sorted(
                zip(FEATURE_NAMES, importance),
                key=lambda x: x[1],
                reverse=True
            )

            return {
                'success': True,
                'version': self.model_version,
                'metrics': {
                    'train_mse': float(train_mse),
                    'test_mse': float(test_mse),
                    'train_r2': float(train_r2),
                    'test_r2': float(test_r2),
                    'samples_train': len(X_train),
                    'samples_test': len(X_test)
                },
                'feature_importance': [
                    {'feature': name, 'importance': float(imp)}
                    for name, imp in feature_importance[:10]
                ]
            }

        except Exception as e:
            logger.error(f"Training error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_training_data_from_outcomes(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Extract training data from OpportunityOutcome records.

        Args:
            days: Number of days to look back

        Returns:
            List of training samples
        """
        from django.utils import timezone

        try:
            from core.models_unified_system import OpportunityOutcome, SpiderData

            cutoff = timezone.now() - timedelta(days=days)

            outcomes = OpportunityOutcome.objects.filter(
                recorded_at__gte=cutoff
            ).select_related('opportunity')

            training_data = []
            for outcome in outcomes:
                opp = outcome.opportunity
                if not opp or not opp.spider_data_id:
                    continue

                try:
                    spider_data = SpiderData.objects.get(id=opp.spider_data_id)
                    features = self.extract_features(spider_data)[0].tolist()

                    # Normalize outcome to 0-1 scale
                    # Success = 1.0, Partial = 0.5, Failure = 0.0
                    outcome_score = {
                        'success': 1.0,
                        'partial': 0.5,
                        'applied': 0.6,
                        'rejected': 0.2,
                        'expired': 0.1,
                        'failure': 0.0
                    }.get(outcome.outcome_type, 0.3)

                    training_data.append({
                        'features': features,
                        'outcome': outcome_score,
                        'opportunity_id': str(opp.id)
                    })
                except SpiderData.DoesNotExist:
                    continue

            logger.info(f"Extracted {len(training_data)} training samples from {days} days")
            return training_data

        except Exception as e:
            logger.error(f"Error extracting training data: {e}")
            return []

    @property
    def is_trained(self) -> bool:
        """Check if model is trained and ready."""
        return self._is_trained


# Singleton instance
_ml_scoring_engine = None


def get_ml_scoring_engine() -> MLScoringEngine:
    """Get singleton ML scoring engine instance."""
    global _ml_scoring_engine
    if _ml_scoring_engine is None:
        _ml_scoring_engine = MLScoringEngine()
    return _ml_scoring_engine
