"""
ML Scoring Engine - LightGBM/XGBoost + SHAP Explainability
==========================================================

Session 470: Market Intelligence Architecture Implementation
Session 670: Phase 2 - 24 features with embedding, temporal, text quality
Session 670: Phase 3 - LightGBM with Optuna hyperparameter optimization

Policy: Hybrid rule + ML scoring with SHAP explainability

This engine provides:
1. Feature extraction from SpiderData (24 features)
2. LightGBM or XGBoost-based opportunity scoring
3. Optuna hyperparameter optimization
4. SHAP explanations for each prediction
5. Hybrid scoring: 60% ML + 40% rule-based
6. Confidence calibration
7. Model versioning and persistence

Usage:
    from core.services.ml_scoring_engine import get_ml_scoring_engine

    engine = get_ml_scoring_engine()
    result = engine.score_opportunity(spider_data)
    explanation = result.get_explanation()

    # Train with hyperparameter optimization
    engine.train_model_with_optimization(training_data, n_trials=50)
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
_lightgbm = None
_optuna = None
_shap = None
_sklearn = None


def _get_xgboost():
    global _xgboost
    if _xgboost is None:
        import xgboost as xgb
        _xgboost = xgb
    return _xgboost


def _get_lightgbm():
    global _lightgbm
    if _lightgbm is None:
        import lightgbm as lgb
        _lightgbm = lgb
    return _lightgbm


def _get_optuna():
    global _optuna
    if _optuna is None:
        import optuna
        # Suppress Optuna logging
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        _optuna = optuna
    return _optuna


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


# Model type constants
MODEL_TYPE_XGBOOST = 'xgboost'
MODEL_TYPE_LIGHTGBM = 'lightgbm'
DEFAULT_MODEL_TYPE = MODEL_TYPE_LIGHTGBM  # Session 670: LightGBM is now default


# Feature definitions (Session 670: Expanded to 24 features)
FEATURE_NAMES = [
    # Original features (15)
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

    # Session 670: Embedding similarity feature (1)
    'embedding_similarity',      # Semantic similarity to successful opportunities

    # Session 670: Temporal features (4)
    'hour_of_day',               # 0-23 hour when created
    'day_of_week',               # 0-6 (Monday=0)
    'is_weekend',                # Boolean: Saturday or Sunday
    'is_business_hours',         # Boolean: 9-17 weekday

    # Session 670: Text quality features (4)
    'description_length',        # Description character count
    'title_word_count',          # Number of words in title
    'has_numbers',               # Boolean: title contains numbers
    'has_question',              # Boolean: title is a question
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

# Keyword sets for feature extraction (Session 669: Expanded for better coverage)
AI_KEYWORDS = {
    'ai', 'ml', 'machine learning', 'deep learning', 'gpt', 'llm', 'neural', 'automation',
    'artificial intelligence', 'chatgpt', 'claude', 'openai', 'anthropic', 'copilot',
    'gemini', 'transformer', 'diffusion', 'midjourney', 'generative', 'agent',
    'embedding', 'fine-tune', 'prompt', 'model', 'algorithm', 'prediction',
    'classification', 'regression', 'nlp', 'computer vision', 'robotics'
}
TRENDING_KEYWORDS = {
    'viral', 'trending', 'hot', 'breaking', 'surge', 'boom', 'skyrocket',
    'exploding', 'soaring', 'rising', 'popular', 'best', 'top', 'leading',
    'fastest', 'record', 'unprecedented', 'massive', 'huge', 'major',
    'significant', 'breakthrough', 'revolutionary', 'disrupting', 'emerging'
}
URGENT_KEYWORDS = {
    'urgent', 'asap', 'immediate', 'now', 'today', 'limited', 'deadline',
    'expires', 'ending', 'last chance', 'hurry', 'quick', 'fast',
    'closing', 'final', 'soon', 'critical', 'emergency', 'alert', 'warning'
}
OPPORTUNITY_KEYWORDS = {
    'opportunity', 'potential', 'growth', 'profit', 'revenue', 'income',
    'earn', 'money', 'salary', 'remote', 'hiring', 'job', 'position',
    'role', 'career', 'freelance', 'contract', 'gig', 'project',
    'investment', 'roi', 'return', 'yield', 'gains', 'bonus', 'equity'
}


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

    Session 670: Now supports LightGBM (default) and XGBoost backends
    with Optuna hyperparameter optimization.

    Provides hybrid scoring combining:
    - LightGBM/XGBoost ML predictions (60% weight)
    - Rule-based heuristics (40% weight)
    - SHAP explanations for transparency
    """

    MODEL_DIR = Path(__file__).parent.parent / 'ml_models'
    MODEL_FILENAME = 'opportunity_scorer_{version}.joblib'

    # Hybrid scoring weights
    ML_WEIGHT = 0.6
    RULE_WEIGHT = 0.4

    def __init__(self, model_type: str = None):
        """
        Initialize the ML scoring engine.

        Args:
            model_type: 'lightgbm' or 'xgboost'. Defaults to LightGBM.
        """
        self.model = None
        self.model_version = "v1.0"
        self.model_type = model_type or DEFAULT_MODEL_TYPE
        self.explainer = None
        self._feature_scaler = None
        self._is_trained = False
        self._best_params = None  # Store optimized hyperparameters

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
                self.model_type = saved_data.get('model_type', MODEL_TYPE_XGBOOST)
                self._best_params = saved_data.get('best_params')
                self._is_trained = True

                # Create SHAP explainer (works for both XGBoost and LightGBM)
                shap = _get_shap()
                self.explainer = shap.TreeExplainer(self.model)

                logger.info(f"Loaded ML model {self.model_version} ({self.model_type}) from {model_path}")
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
                'model_type': self.model_type,
                'best_params': self._best_params,
                'trained_at': datetime.now().isoformat(),
                'feature_names': FEATURE_NAMES
            }, model_path)
            logger.info(f"Saved ML model {self.model_version} ({self.model_type}) to {model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False

    def _extract_text_content(self, spider_data) -> Tuple[str, str, bool]:
        """
        Extract title and description text from spider data.

        Session 669: Fixed to properly extract text from raw_data['items'] array
        structure used by spiders, not raw_data['title'] which doesn't exist.

        Returns: (title, description, has_url)
        """
        raw_data = spider_data.raw_data or {}
        title = ''
        description = ''
        has_url = False

        # Try direct fields first (legacy/simple structure)
        if raw_data.get('title'):
            title = raw_data['title']
            description = raw_data.get('description', '') or raw_data.get('content', '') or ''
            has_url = bool(raw_data.get('url'))
        else:
            # Extract from items array (current spider structure)
            items = raw_data.get('items', [])
            if items and isinstance(items, list):
                # Aggregate titles from first few items
                titles = []
                descriptions = []
                for item in items[:5]:  # First 5 items
                    if isinstance(item, dict):
                        # Try various title field names
                        item_title = (
                            item.get('title') or
                            item.get('headline') or
                            item.get('name') or
                            item.get('subject') or
                            ''
                        )
                        if item_title:
                            titles.append(str(item_title))

                        # Try various description field names
                        item_desc = (
                            item.get('description') or
                            item.get('summary') or
                            item.get('content') or
                            item.get('text') or
                            ''
                        )
                        if item_desc:
                            descriptions.append(str(item_desc)[:200])

                        # Check for URLs
                        if item.get('url') or item.get('link'):
                            has_url = True

                title = ' | '.join(titles) if titles else ''
                description = ' '.join(descriptions) if descriptions else ''

        # Also check processed_data as fallback
        if not title:
            processed = spider_data.processed_data or {}
            if isinstance(processed, dict):
                title = processed.get('title', '') or processed.get('summary', '') or ''

        # Use embedding_text as final fallback (often contains cleaned text)
        if not title and spider_data.embedding_text:
            title = spider_data.embedding_text[:500]

        return title, description, has_url

    def extract_features(self, spider_data) -> np.ndarray:
        """
        Extract features from a SpiderData instance.

        Returns a numpy array of shape (1, n_features)
        """
        from django.utils import timezone

        raw_data = spider_data.raw_data or {}

        # Session 669: Use proper text extraction
        title, description, has_url = self._extract_text_content(spider_data)
        title_lower = title.lower()
        all_text_lower = (title + ' ' + description).lower()

        # Calculate freshness
        age = timezone.now() - spider_data.created_at
        freshness_hours = age.total_seconds() / 3600

        # Determine category
        spider_name = spider_data.spider_name.lower()
        category = self._categorize_spider(spider_name)

        # Session 670: Extract temporal features
        created_at = spider_data.created_at
        hour_of_day = created_at.hour
        day_of_week = created_at.weekday()  # Monday=0, Sunday=6
        is_weekend = 1.0 if day_of_week >= 5 else 0.0
        is_business_hours = 1.0 if (9 <= hour_of_day <= 17 and day_of_week < 5) else 0.0

        # Session 670: Extract text quality features
        title_word_count = len(title.split()) if title else 0
        has_numbers = 1.0 if any(c.isdigit() for c in title) else 0.0
        has_question = 1.0 if '?' in title else 0.0

        # Extract features - use all_text for keyword detection for better coverage
        features = [
            # Original features (15)
            spider_data.relevance_score or 50,                          # relevance_score
            SOURCE_AUTHORITY.get(spider_name, SOURCE_AUTHORITY['default']),  # source_authority
            min(freshness_hours, 168),                                   # data_freshness_hours (cap at 1 week)
            min(len(title), 200),                                        # title_length
            1.0 if has_url else 0.0,                                    # has_url
            1.0 if category == 'tech' else 0.0,                         # category_tech
            1.0 if category == 'financial' else 0.0,                    # category_financial
            1.0 if category == 'jobs' else 0.0,                         # category_jobs
            1.0 if category == 'creative' else 0.0,                     # category_creative
            1.0 if category == 'news' else 0.0,                         # category_news
            1.0 if any(kw in all_text_lower for kw in AI_KEYWORDS) else 0.0,           # keyword_ai
            1.0 if any(kw in all_text_lower for kw in TRENDING_KEYWORDS) else 0.0,     # keyword_trending
            1.0 if any(kw in all_text_lower for kw in URGENT_KEYWORDS) else 0.0,       # keyword_urgent
            1.0 if any(kw in all_text_lower for kw in OPPORTUNITY_KEYWORDS) else 0.0,  # keyword_opportunity
            self._get_historical_success_rate(spider_name),             # historical_success_rate

            # Session 670: Embedding similarity (1)
            self._get_embedding_similarity(spider_data),                # embedding_similarity

            # Session 670: Temporal features (4)
            hour_of_day,                                                # hour_of_day (0-23)
            day_of_week,                                                # day_of_week (0-6)
            is_weekend,                                                 # is_weekend
            is_business_hours,                                          # is_business_hours

            # Session 670: Text quality features (4)
            min(len(description), 5000),                                # description_length
            title_word_count,                                           # title_word_count
            has_numbers,                                                # has_numbers
            has_question,                                               # has_question
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

    def _get_embedding_similarity(self, spider_data) -> float:
        """
        Session 670: Get semantic similarity to historically successful opportunities.

        Compares the spider data's embedding to embeddings from opportunities
        that resulted in 'won' outcomes, returning average cosine similarity.

        Returns:
            float: Similarity score 0.0-1.0 (0.5 = neutral/no data)
        """
        # Check if spider_data has an embedding
        embedding = None
        if hasattr(spider_data, 'embedding') and spider_data.embedding:
            embedding = spider_data.embedding
        elif hasattr(spider_data, 'embedding_vector') and spider_data.embedding_vector:
            embedding = spider_data.embedding_vector

        if not embedding:
            return 0.5  # Neutral default when no embedding

        try:
            from django.core.cache import cache

            cache_key = f"ml_embedding_sim_{spider_data.spider_name}"
            cached_embeddings = cache.get(cache_key)

            if cached_embeddings is None:
                from core.models_unified_system import SpiderData, OpportunityOutcome

                # Get embeddings from successful opportunities (won outcomes)
                successful_spider_ids = OpportunityOutcome.objects.filter(
                    outcome='won',
                    task__opportunity__spider_data__isnull=False
                ).values_list('task__opportunity__spider_data_id', flat=True)[:100]

                successful_embeddings = list(
                    SpiderData.objects.filter(
                        id__in=successful_spider_ids
                    ).exclude(
                        embedding__isnull=True
                    ).values_list('embedding', flat=True)[:50]
                )

                # Cache for 2 hours
                cache.set(cache_key, successful_embeddings, 7200)
                cached_embeddings = successful_embeddings

            if not cached_embeddings:
                return 0.5  # No successful embeddings to compare

            # Calculate average cosine similarity
            query_vec = np.array(embedding)
            if query_vec.ndim == 0 or len(query_vec) == 0:
                return 0.5

            similarities = []
            for emb in cached_embeddings:
                try:
                    target_vec = np.array(emb)
                    if target_vec.ndim == 0 or len(target_vec) == 0:
                        continue
                    if len(query_vec) != len(target_vec):
                        continue

                    # Cosine similarity
                    dot = np.dot(query_vec, target_vec)
                    norm_q = np.linalg.norm(query_vec)
                    norm_t = np.linalg.norm(target_vec)

                    if norm_q > 0 and norm_t > 0:
                        sim = dot / (norm_q * norm_t)
                        similarities.append(float(sim))
                except Exception:
                    continue

            if similarities:
                avg_sim = np.mean(similarities)
                # Normalize to 0-1 range (cosine sim is -1 to 1)
                return float(max(0, min(1, (avg_sim + 1) / 2)))

            return 0.5

        except Exception as e:
            logger.debug(f"Embedding similarity error: {e}")
            return 0.5

    # Default success rates as fallback when insufficient data
    DEFAULT_SUCCESS_RATES = {
        'remoteok': 0.65,
        'weworkremotely': 0.60,
        'hackernews': 0.55,
        'techcrunch': 0.50,
        'producthunt': 0.45,
        'coingecko': 0.40,
        'adzuna': 0.60,
        'github_jobs': 0.55,
        'default': 0.35
    }

    def _get_historical_success_rate(self, spider_name: str) -> float:
        """
        Get historical success rate for a spider source from actual outcome data.

        Session 669: Fixed to query actual OpportunityOutcome data instead of
        using hardcoded values. Falls back to defaults when <5 samples available.
        """
        from django.core.cache import cache

        cache_key = f"ml_spider_success_rate_{spider_name}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            from core.models_unified_system import OpportunityOutcome
            from django.db.models import Count

            # Query outcomes for this spider source
            outcomes = OpportunityOutcome.objects.filter(
                task__opportunity__spider_data__spider_name=spider_name
            ).values('outcome').annotate(count=Count('id'))

            total = sum(item['count'] for item in outcomes)

            if total < 5:
                # Insufficient data, use default
                rate = self.DEFAULT_SUCCESS_RATES.get(spider_name, self.DEFAULT_SUCCESS_RATES['default'])
                logger.debug(f"Spider {spider_name}: insufficient data ({total}), using default {rate}")
            else:
                # Calculate weighted success rate from actual outcomes
                outcome_weights = {
                    'won': 1.0,
                    'partial': 0.5,
                    'lost': 0.0,
                    'expired': 0.1,
                    'cancelled': 0.2,
                }

                weighted_sum = sum(
                    item['count'] * outcome_weights.get(item['outcome'], 0.3)
                    for item in outcomes
                )
                rate = weighted_sum / total
                logger.debug(f"Spider {spider_name}: actual rate {rate:.3f} from {total} outcomes")

            # Cache for 1 hour
            cache.set(cache_key, rate, 3600)
            return rate

        except Exception as e:
            logger.warning(f"Error getting historical success rate for {spider_name}: {e}")
            return self.DEFAULT_SUCCESS_RATES.get(spider_name, self.DEFAULT_SUCCESS_RATES['default'])

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

            # Session 669: Validation logging for feature quality monitoring
            if logger.isEnabledFor(logging.DEBUG):
                feature_dict = dict(zip(FEATURE_NAMES, features[0]))
                zero_features = [name for name, val in feature_dict.items() if val == 0]
                active_features = len(FEATURE_NAMES) - len(zero_features)
                logger.debug(
                    f"Features for {spider_data.spider_name}: "
                    f"{active_features}/{len(FEATURE_NAMES)} active, "
                    f"keywords=[ai:{feature_dict.get('keyword_ai', 0):.0f}, "
                    f"trend:{feature_dict.get('keyword_trending', 0):.0f}, "
                    f"opp:{feature_dict.get('keyword_opportunity', 0):.0f}]"
                )

            # Warn if too many features are zero (indicates extraction issues)
            zero_count = sum(1 for val in features[0] if val == 0)
            if zero_count > 10:
                logger.warning(
                    f"High zero-feature count for {spider_data.spider_name}: "
                    f"{zero_count}/{len(FEATURE_NAMES)} features are zero"
                )

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

    def _create_model(self, params: Dict[str, Any] = None):
        """
        Create a model instance based on model_type.

        Args:
            params: Hyperparameters for the model. If None, uses defaults.

        Returns:
            Model instance (LightGBM or XGBoost regressor)
        """
        if self.model_type == MODEL_TYPE_LIGHTGBM:
            lgb = _get_lightgbm()
            default_params = {
                'n_estimators': 200,
                'max_depth': 6,
                'learning_rate': 0.05,
                'num_leaves': 31,
                'min_child_samples': 20,
                'reg_alpha': 0.1,
                'reg_lambda': 0.1,
                'random_state': 42,
                'verbose': -1,
                'force_col_wise': True,
            }
            if params:
                default_params.update(params)
            return lgb.LGBMRegressor(**default_params)
        else:
            xgb = _get_xgboost()
            default_params = {
                'n_estimators': 100,
                'max_depth': 5,
                'learning_rate': 0.1,
                'random_state': 42,
                'objective': 'reg:squarederror',
            }
            if params:
                default_params.update(params)
            return xgb.XGBRegressor(**default_params)

    def optimize_hyperparameters(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_trials: int = 50,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        Use Optuna to find optimal hyperparameters.

        Args:
            X: Feature matrix
            y: Target values
            n_trials: Number of optimization trials
            cv_folds: Number of cross-validation folds

        Returns:
            Dict with best parameters and optimization results
        """
        optuna = _get_optuna()
        sklearn = _get_sklearn()

        def objective(trial):
            if self.model_type == MODEL_TYPE_LIGHTGBM:
                lgb = _get_lightgbm()
                params = {
                    'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                    'max_depth': trial.suggest_int('max_depth', 3, 10),
                    'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                    'num_leaves': trial.suggest_int('num_leaves', 10, 100),
                    'min_child_samples': trial.suggest_int('min_child_samples', 5, 50),
                    'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
                    'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
                    'random_state': 42,
                    'verbose': -1,
                    'force_col_wise': True,
                }
                model = lgb.LGBMRegressor(**params)
            else:
                xgb = _get_xgboost()
                params = {
                    'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                    'max_depth': trial.suggest_int('max_depth', 3, 10),
                    'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                    'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
                    'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                    'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                    'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
                    'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
                    'random_state': 42,
                    'objective': 'reg:squarederror',
                }
                model = xgb.XGBRegressor(**params)

            # Cross-validation
            scores = sklearn['model_selection'].cross_val_score(
                model, X, y, cv=cv_folds, scoring='r2'
            )
            return scores.mean()

        # Create and run study
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

        logger.info(f"Optuna optimization complete: best R2 = {study.best_value:.4f}")

        return {
            'best_params': study.best_params,
            'best_score': study.best_value,
            'n_trials': n_trials,
            'model_type': self.model_type
        }

    def train_model(
        self,
        training_data: List[Dict[str, Any]],
        version: str = None,
        model_type: str = None,
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Train the model on historical outcome data.

        Session 670: Now supports both LightGBM and XGBoost.

        Args:
            training_data: List of dicts with 'features' and 'outcome' keys
            version: Model version string
            model_type: 'lightgbm' or 'xgboost'. Uses instance default if None.
            params: Custom hyperparameters. Uses defaults if None.

        Returns:
            Training metrics dict
        """
        if len(training_data) < 10:
            return {
                'success': False,
                'error': f'Insufficient training data: {len(training_data)} samples (need 10+)'
            }

        # Update model type if specified
        if model_type:
            self.model_type = model_type

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

            # Create and train model
            self.model = self._create_model(params)
            self.model.fit(X_train_scaled, y_train)

            # Evaluate
            train_pred = self.model.predict(X_train_scaled)
            test_pred = self.model.predict(X_test_scaled)

            train_mse = sklearn['metrics'].mean_squared_error(y_train, train_pred)
            test_mse = sklearn['metrics'].mean_squared_error(y_test, test_pred)
            train_r2 = sklearn['metrics'].r2_score(y_train, train_pred)
            test_r2 = sklearn['metrics'].r2_score(y_test, test_pred)

            # Create SHAP explainer (works for both LightGBM and XGBoost)
            self.explainer = shap.TreeExplainer(self.model)

            # Update version
            if version:
                self.model_version = version
            else:
                # Auto-increment version
                current_num = int(self.model_version.replace('v', '').split('.')[0])
                self.model_version = f"v{current_num + 1}.0"

            self._is_trained = True
            self._best_params = params

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
                'model_type': self.model_type,
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

    def train_model_with_optimization(
        self,
        training_data: List[Dict[str, Any]],
        version: str = None,
        model_type: str = None,
        n_trials: int = 50,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        Train model with Optuna hyperparameter optimization.

        Session 670: Full training pipeline with automatic tuning.

        Args:
            training_data: List of dicts with 'features' and 'outcome' keys
            version: Model version string
            model_type: 'lightgbm' or 'xgboost'. Uses instance default if None.
            n_trials: Number of Optuna optimization trials
            cv_folds: Number of cross-validation folds

        Returns:
            Training metrics dict with optimization results
        """
        if len(training_data) < 10:
            return {
                'success': False,
                'error': f'Insufficient training data: {len(training_data)} samples (need 10+)'
            }

        # Update model type if specified
        if model_type:
            self.model_type = model_type

        sklearn = _get_sklearn()

        try:
            # Prepare data
            X = np.array([d['features'] for d in training_data])
            y = np.array([d['outcome'] for d in training_data])

            # Scale features for optimization
            scaler = sklearn['preprocessing'].StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Run hyperparameter optimization
            logger.info(f"Starting Optuna optimization with {n_trials} trials...")
            opt_results = self.optimize_hyperparameters(
                X_scaled, y, n_trials=n_trials, cv_folds=cv_folds
            )

            # Train final model with best params
            logger.info(f"Training final model with optimized params...")
            result = self.train_model(
                training_data,
                version=version,
                params=opt_results['best_params']
            )

            if result['success']:
                result['optimization'] = {
                    'n_trials': n_trials,
                    'cv_folds': cv_folds,
                    'best_cv_score': opt_results['best_score'],
                    'best_params': opt_results['best_params']
                }

            return result

        except Exception as e:
            logger.error(f"Training with optimization error: {e}")
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
# Session 1083 round 41: lock prevents two threads from racing into
# MLScoringEngine() concurrently — joblib.load(lightgbm) is NOT
# reentrant on macOS and the race triggered process-wide Abseil
# [mutex.cc : 452] RAW: Lock blocking deadlocks. tasks_agents uses
# ThreadPoolExecutor(max_workers=1) internally so even --pool=solo
# Celery workers have 2+ Python threads that can race here.
import threading as _ml_scoring_threading
_ml_scoring_lock = _ml_scoring_threading.Lock()


def get_ml_scoring_engine() -> MLScoringEngine:
    """Get singleton ML scoring engine instance. Thread-safe."""
    global _ml_scoring_engine
    if _ml_scoring_engine is None:
        with _ml_scoring_lock:
            # Double-checked locking pattern — re-read under the lock
            # so we don't instantiate twice if two threads both saw None
            # before either took the lock.
            if _ml_scoring_engine is None:
                _ml_scoring_engine = MLScoringEngine()
    return _ml_scoring_engine
