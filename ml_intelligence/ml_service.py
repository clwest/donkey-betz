"""
ML Service - Django Integration Layer
Connects ML Pipeline with existing intelligence system
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.core.cache import cache
import asyncio

# Add ML module to Python path
ml_path = os.path.join(settings.BASE_DIR, 'ml')
if ml_path not in sys.path:
    sys.path.append(ml_path)

try:
    from ml.core.ml_engine import MLEngine, MLConfig, PatternPrediction, UserBehaviorProfile
    from ml.integrations.huggingface_client import HuggingFaceClient
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    print(f"ML dependencies not available: {e}")

class MLService:
    """
    ML Service - Bridge between Django and ML Pipeline
    Integrates with existing intelligence system
    """

    _instance = None
    _ml_engine = None
    _hf_client = None

    @classmethod
    def initialize(cls):
        """Initialize ML Service (called from Django app ready)"""
        if not ML_AVAILABLE:
            logging.warning("ML Service not available - dependencies not installed")
            return

        if cls._instance is None:
            cls._instance = cls()

    def __init__(self):
        if not ML_AVAILABLE:
            raise ImportError("ML dependencies not available")

        self.logger = logging.getLogger(__name__)

        # Initialize ML Engine
        config = MLConfig(
            model_cache_dir=os.path.join(settings.BASE_DIR, 'ml', 'models', 'cache'),
            max_memory_gb=8.0,  # Conservative for M3 with 18GB
            use_mlx=True
        )

        try:
            self._ml_engine = MLEngine(config)
            self.logger.info("ML Engine initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize ML Engine: {e}")
            self._ml_engine = None

        # Initialize HuggingFace Client
        hf_token = getattr(settings, 'HUGGINGFACE_API_TOKEN', None)
        try:
            self._hf_client = HuggingFaceClient(hf_token)
            self.logger.info("HuggingFace Client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize HuggingFace Client: {e}")
            self._hf_client = None

    @classmethod
    def get_instance(cls) -> 'MLService':
        """Get ML Service singleton instance"""
        if cls._instance is None:
            cls.initialize()
        return cls._instance

    def is_available(self) -> bool:
        """Check if ML Service is available"""
        return ML_AVAILABLE and (self._ml_engine is not None or self._hf_client is not None)

    async def analyze_market_opportunity(self,
                                       market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze market opportunities using ML pipeline
        Integrates with existing intelligence system
        """
        if not self.is_available():
            return []

        opportunities = []

        try:
            # Use local ML engine for pattern recognition
            if self._ml_engine:
                cross_domain_patterns = self._ml_engine.detect_cross_domain_opportunity(market_data)

                for pattern in cross_domain_patterns:
                    opportunity = {
                        'id': f"ml_{pattern.pattern_type}_{hash(str(market_data))}",
                        'type': 'ml_pattern',
                        'domain': self._extract_domain_from_pattern(pattern.pattern_type),
                        'entity': pattern.pattern_type,
                        'description': pattern.predicted_outcome,
                        'edge': self._calculate_edge_from_confidence(pattern.confidence),
                        'confidence': pattern.confidence,
                        'profit_potential': 0,  # Will be calculated based on pattern
                        'time_window': self._parse_time_horizon(pattern.time_horizon),
                        'risk_level': 'MEDIUM',
                        'timestamp': market_data.get('timestamp', ''),
                        'status': 'active',
                        'metadata': {
                            'ml_source': 'local_engine',
                            'supporting_features': pattern.supporting_features,
                            'cross_domain_signals': pattern.cross_domain_signals
                        }
                    }
                    opportunities.append(opportunity)

            # Use HuggingFace for sentiment-based opportunities
            if self._hf_client and 'news_data' in market_data:
                sentiment_opportunities = await self._analyze_sentiment_opportunities(
                    market_data['news_data']
                )
                opportunities.extend(sentiment_opportunities)

            # Cache results for performance
            cache_key = f"ml_opportunities_{hash(str(market_data))}"
            cache.set(cache_key, opportunities, timeout=300)  # 5 minute cache

            self.logger.info(f"Generated {len(opportunities)} ML-based opportunities")
            return opportunities

        except Exception as e:
            self.logger.error(f"Error in ML opportunity analysis: {e}")
            return []

    async def analyze_sports_crypto_correlation(self,
                                              sports_event: Dict[str, Any],
                                              crypto_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze sports events for crypto market impact
        Example: NBA injury news → BTC volatility prediction
        """
        if not self._ml_engine:
            return None

        try:
            # Use ML engine for sports-crypto analysis
            pattern = self._ml_engine.analyze_sports_to_crypto_pattern(
                sports_event, crypto_context
            )

            if pattern and pattern.confidence > 0.6:
                return {
                    'prediction_type': 'sports_crypto_correlation',
                    'sports_trigger': sports_event.get('event_type', 'unknown'),
                    'crypto_prediction': pattern.predicted_outcome,
                    'confidence': pattern.confidence,
                    'time_horizon': pattern.time_horizon,
                    'supporting_data': pattern.supporting_features,
                    'recommended_action': self._generate_recommendation(pattern),
                    'ml_source': 'local_engine'
                }

        except Exception as e:
            self.logger.error(f"Sports-crypto correlation analysis failed: {e}")

        return None

    def track_user_decision(self,
                          user_id: str,
                          decision_data: Dict[str, Any]) -> float:
        """
        Track user decision and return personalized confidence score
        Builds Digital Twin of user's decision patterns
        """
        if not self._ml_engine:
            return decision_data.get('confidence', 0.5)

        try:
            # Add user context to decision data
            enhanced_decision = {
                **decision_data,
                'user_id': user_id,
                'timestamp': decision_data.get('timestamp', ''),
                'domain': decision_data.get('domain', 'UNKNOWN')
            }

            # Get personalized confidence score
            personal_confidence = self._ml_engine.analyze_user_decision_pattern(
                enhanced_decision
            )

            # Cache user's confidence pattern
            cache_key = f"user_confidence_{user_id}_{decision_data.get('domain', 'ALL')}"
            cache.set(cache_key, personal_confidence, timeout=3600)  # 1 hour cache

            self.logger.info(f"User {user_id} personal confidence: {personal_confidence:.2f}")
            return personal_confidence

        except Exception as e:
            self.logger.error(f"User decision tracking failed: {e}")
            return decision_data.get('confidence', 0.5)

    async def update_decision_outcome(self,
                                    decision_id: str,
                                    outcome: str,
                                    actual_return: float,
                                    user_id: str = None):
        """
        Update ML models with decision outcomes
        Enables continuous learning and improvement
        """
        if not self._ml_engine:
            return

        try:
            # Update ML engine with feedback
            self._ml_engine.update_user_feedback(decision_id, outcome, actual_return)

            # Save updated models
            self._ml_engine.save_models()

            # Clear relevant caches
            if user_id:
                cache_pattern = f"user_confidence_{user_id}_*"
                # Django cache doesn't support pattern deletion, so we'll clear specific keys
                for domain in ['SPORTS_BETTING', 'CRYPTO', 'TRADING', 'REAL_ESTATE']:
                    cache.delete(f"user_confidence_{user_id}_{domain}")

            self.logger.info(f"Updated ML models with outcome for decision {decision_id}")

        except Exception as e:
            self.logger.error(f"Failed to update decision outcome: {e}")

    async def get_ml_system_status(self) -> Dict[str, Any]:
        """Get comprehensive ML system status"""
        if not self.is_available():
            return {
                'available': False,
                'error': 'ML dependencies not installed'
            }

        status = {
            'available': True,
            'local_engine': {
                'active': self._ml_engine is not None,
                'health': self._ml_engine.get_system_health() if self._ml_engine else {}
            },
            'huggingface_client': {
                'active': self._hf_client is not None,
                'status': self._hf_client.get_model_status() if self._hf_client else {}
            }
        }

        # Add health checks
        if self._hf_client:
            try:
                health_check = await asyncio.wait_for(
                    self._hf_client.health_check(),
                    timeout=10
                )
                status['huggingface_client']['health'] = health_check
            except:
                status['huggingface_client']['health'] = {'api_connection': False}

        return status

    # Helper methods
    def _extract_domain_from_pattern(self, pattern_type: str) -> str:
        """Extract domain from pattern type"""
        if 'sports' in pattern_type.lower():
            return 'SPORTS_BETTING'
        elif 'crypto' in pattern_type.lower():
            return 'CRYPTO'
        elif 'options' in pattern_type.lower():
            return 'TRADING'
        else:
            return 'CROSS_DOMAIN'

    def _calculate_edge_from_confidence(self, confidence: float) -> float:
        """Convert ML confidence to edge percentage"""
        # Simple mapping - can be refined based on backtesting
        if confidence >= 0.8:
            return (confidence - 0.5) * 10  # 3-8% edge
        else:
            return max(0.5, (confidence - 0.5) * 5)  # 0.5-2.5% edge

    def _parse_time_horizon(self, time_horizon: str) -> int:
        """Parse time horizon string to seconds"""
        if 'hour' in time_horizon:
            hours = float(time_horizon.split()[0].split('-')[0])
            return int(hours * 3600)
        elif 'minute' in time_horizon:
            minutes = float(time_horizon.split()[0])
            return int(minutes * 60)
        else:
            return 3600  # Default 1 hour

    async def _analyze_sentiment_opportunities(self, news_data: List[str]) -> List[Dict[str, Any]]:
        """Analyze news sentiment for opportunities"""
        opportunities = []

        if not self._hf_client:
            return opportunities

        try:
            # Analyze financial news sentiment
            sentiment_results = await self._hf_client.analyze_market_news_sentiment(news_data)

            for i, result in enumerate(sentiment_results):
                if result.get('confidence', 0) > 0.7:  # High confidence sentiment
                    opportunity = {
                        'id': f"sentiment_{i}_{hash(result.get('text', ''))}",
                        'type': 'sentiment_signal',
                        'domain': 'MARKET_NEWS',
                        'entity': 'news_sentiment',
                        'description': f"Strong {result.get('sentiment', 'neutral')} sentiment detected",
                        'edge': result.get('confidence', 0.5) * 2,  # Convert to edge
                        'confidence': result.get('confidence', 0.5),
                        'profit_potential': 0,
                        'time_window': 1800,  # 30 minutes
                        'risk_level': 'LOW',
                        'timestamp': '',
                        'status': 'active',
                        'metadata': {
                            'ml_source': 'huggingface',
                            'sentiment': result.get('sentiment'),
                            'text_sample': result.get('text', '')[:100]
                        }
                    }
                    opportunities.append(opportunity)

        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")

        return opportunities

    def _generate_recommendation(self, pattern: 'PatternPrediction') -> str:
        """Generate actionable recommendation from ML pattern"""
        if pattern.confidence >= 0.8:
            return f"STRONG: {pattern.predicted_outcome}"
        elif pattern.confidence >= 0.6:
            return f"MODERATE: {pattern.predicted_outcome}"
        else:
            return f"WEAK: {pattern.predicted_outcome} - proceed with caution"