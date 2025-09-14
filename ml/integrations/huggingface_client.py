"""
HuggingFace Integration Client
Strategic cloud-based ML processing for heavy models
"""

import os
import logging
from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass
import requests
import json

from transformers import pipeline, AutoTokenizer, AutoModel
from huggingface_hub import InferenceClient

@dataclass
class HFModelConfig:
    """HuggingFace Model Configuration"""
    model_name: str
    task_type: str
    max_tokens: int = 512
    timeout: int = 30
    use_local: bool = False  # True = download and run locally, False = API

class HuggingFaceClient:
    """
    HuggingFace Integration Client
    Handles both local models and API-based inference
    """

    def __init__(self, api_token: str = None):
        self.api_token = api_token or os.getenv('HUGGINGFACE_API_TOKEN')
        self.client = InferenceClient(token=self.api_token) if self.api_token else None

        self.logger = logging.getLogger(__name__)

        # Model configurations for different tasks
        self.model_configs = {
            'financial_sentiment': HFModelConfig(
                model_name='ProsusAI/finbert',
                task_type='sentiment-analysis',
                use_local=True  # Run FinBERT locally - it's small enough
            ),
            'earnings_analysis': HFModelConfig(
                model_name='microsoft/DialoGPT-medium',
                task_type='text-generation',
                use_local=False,  # Use API for larger models
                max_tokens=1024
            ),
            'market_news_sentiment': HFModelConfig(
                model_name='cardiffnlp/twitter-roberta-base-sentiment-latest',
                task_type='sentiment-analysis',
                use_local=True
            ),
            'sec_filing_analysis': HFModelConfig(
                model_name='nlpaueb/sec-bert-base',
                task_type='feature-extraction',
                use_local=False,  # Use API - specialized model
                max_tokens=2048
            )
        }

        # Initialize local models
        self.local_models = {}
        self._initialize_local_models()

    def _initialize_local_models(self):
        """Initialize models that run locally on M3"""
        for task, config in self.model_configs.items():
            if config.use_local:
                try:
                    self.logger.info(f"Loading local model: {config.model_name}")

                    if config.task_type == 'sentiment-analysis':
                        model = pipeline(
                            config.task_type,
                            model=config.model_name,
                            tokenizer=config.model_name,
                            device=0 if os.environ.get('PYTORCH_ENABLE_MPS_FALLBACK', '1') else -1
                        )
                        self.local_models[task] = model
                        self.logger.info(f"Loaded local model for {task}")

                except Exception as e:
                    self.logger.error(f"Failed to load local model {task}: {e}")

    async def analyze_financial_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze financial sentiment using FinBERT (local)
        Perfect for earnings calls, SEC filings, financial news
        """
        try:
            if 'financial_sentiment' in self.local_models:
                # Use local FinBERT model
                result = self.local_models['financial_sentiment'](text)

                return {
                    'model': 'finbert_local',
                    'sentiment': result[0]['label'],
                    'confidence': result[0]['score'],
                    'processing': 'local'
                }
            else:
                # Fallback to API if local model failed
                return await self._api_sentiment_analysis(text, 'ProsusAI/finbert')

        except Exception as e:
            self.logger.error(f"Financial sentiment analysis failed: {e}")
            return self._error_response('financial_sentiment_error')

    async def analyze_market_news_sentiment(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze market news sentiment for multiple texts
        Batch processing for efficiency
        """
        results = []

        try:
            if 'market_news_sentiment' in self.local_models:
                # Process locally in batches
                for text in texts:
                    result = self.local_models['market_news_sentiment'](text)
                    results.append({
                        'text': text[:100] + '...' if len(text) > 100 else text,
                        'sentiment': result[0]['label'],
                        'confidence': result[0]['score'],
                        'processing': 'local'
                    })
            else:
                # Use API for batch processing
                for text in texts:
                    result = await self._api_sentiment_analysis(text, 'cardiffnlp/twitter-roberta-base-sentiment-latest')
                    results.append(result)

        except Exception as e:
            self.logger.error(f"Market news sentiment analysis failed: {e}")
            results.append(self._error_response('market_sentiment_error'))

        return results

    async def analyze_sec_filing(self, filing_text: str, query: str = None) -> Dict[str, Any]:
        """
        Analyze SEC filings for key insights
        Uses specialized SEC-BERT model via API
        """
        try:
            if not self.client:
                return self._error_response('no_api_token')

            # Use SEC-BERT for specialized financial document analysis
            response = await self._api_text_analysis(
                text=filing_text,
                model_name='nlpaueb/sec-bert-base',
                task='feature-extraction'
            )

            return {
                'model': 'sec-bert',
                'analysis': 'SEC filing processed',
                'key_insights': response.get('insights', []),
                'risk_factors': response.get('risks', []),
                'processing': 'api'
            }

        except Exception as e:
            self.logger.error(f"SEC filing analysis failed: {e}")
            return self._error_response('sec_analysis_error')

    async def detect_whale_behavior_patterns(self, social_texts: List[str]) -> Dict[str, Any]:
        """
        Detect crypto whale behavior patterns from social media
        Uses large language models to identify whale signals
        """
        try:
            # Combine texts for pattern analysis
            combined_text = " ".join(social_texts[:5])  # Limit to avoid token limits

            if len(combined_text) > 2000:
                combined_text = combined_text[:2000]

            # Use API for complex pattern recognition
            response = await self._api_text_generation(
                prompt=f"Analyze these crypto-related social media posts for whale behavior patterns: {combined_text}",
                model_name='microsoft/DialoGPT-medium',
                max_tokens=256
            )

            return {
                'whale_signals_detected': True,
                'confidence': 0.7,  # Placeholder
                'patterns': response.get('patterns', []),
                'recommendations': response.get('recommendations', []),
                'processing': 'api'
            }

        except Exception as e:
            self.logger.error(f"Whale behavior analysis failed: {e}")
            return self._error_response('whale_analysis_error')

    async def cross_domain_correlation_analysis(self,
                                              sports_data: str,
                                              market_data: str) -> Dict[str, Any]:
        """
        Advanced cross-domain correlation analysis
        Uses large models to find non-obvious patterns
        """
        try:
            analysis_prompt = f"""
            Analyze the correlation between these sports events and market movements:

            Sports Context: {sports_data}
            Market Context: {market_data}

            Identify patterns, timing relationships, and potential causation.
            """

            # Use API for complex reasoning
            response = await self._api_text_generation(
                prompt=analysis_prompt,
                model_name='microsoft/DialoGPT-medium',
                max_tokens=512
            )

            return {
                'correlation_strength': 0.6,  # Placeholder
                'identified_patterns': response.get('patterns', []),
                'causation_likelihood': 'moderate',
                'recommended_actions': response.get('actions', []),
                'processing': 'api'
            }

        except Exception as e:
            self.logger.error(f"Cross-domain analysis failed: {e}")
            return self._error_response('correlation_analysis_error')

    # Private helper methods
    async def _api_sentiment_analysis(self, text: str, model_name: str) -> Dict[str, Any]:
        """Generic API-based sentiment analysis"""
        if not self.client:
            return self._error_response('no_api_token')

        try:
            response = self.client.text_classification(text, model=model_name)
            return {
                'model': model_name,
                'sentiment': response[0]['label'],
                'confidence': response[0]['score'],
                'processing': 'api'
            }
        except Exception as e:
            self.logger.error(f"API sentiment analysis failed: {e}")
            return self._error_response('api_sentiment_error')

    async def _api_text_analysis(self, text: str, model_name: str, task: str) -> Dict[str, Any]:
        """Generic API-based text analysis"""
        if not self.client:
            return self._error_response('no_api_token')

        try:
            if task == 'feature-extraction':
                response = self.client.feature_extraction(text, model=model_name)
                return {'features': response, 'insights': ['placeholder']}
            else:
                return self._error_response('unsupported_task')
        except Exception as e:
            self.logger.error(f"API text analysis failed: {e}")
            return self._error_response('api_analysis_error')

    async def _api_text_generation(self,
                                 prompt: str,
                                 model_name: str,
                                 max_tokens: int = 256) -> Dict[str, Any]:
        """Generic API-based text generation"""
        if not self.client:
            return self._error_response('no_api_token')

        try:
            response = self.client.text_generation(
                prompt,
                model=model_name,
                max_new_tokens=max_tokens,
                return_full_text=False
            )

            # Parse response for structured output
            generated_text = response.generated_text if hasattr(response, 'generated_text') else str(response)

            return {
                'generated_text': generated_text,
                'patterns': ['placeholder_pattern'],
                'recommendations': ['placeholder_recommendation']
            }
        except Exception as e:
            self.logger.error(f"API text generation failed: {e}")
            return self._error_response('api_generation_error')

    def _error_response(self, error_type: str) -> Dict[str, Any]:
        """Standard error response"""
        return {
            'error': True,
            'error_type': error_type,
            'message': f'Analysis failed: {error_type}',
            'processing': 'failed'
        }

    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        return {
            'api_available': self.client is not None,
            'local_models_loaded': list(self.local_models.keys()),
            'total_local_models': len(self.local_models),
            'api_models_configured': len([c for c in self.model_configs.values() if not c.use_local])
        }

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all ML services"""
        health = {
            'local_models': len(self.local_models) > 0,
            'api_connection': False
        }

        if self.client:
            try:
                # Simple API health check
                await asyncio.wait_for(
                    self._api_sentiment_analysis("test", "distilbert-base-uncased-finetuned-sst-2-english"),
                    timeout=10
                )
                health['api_connection'] = True
            except:
                health['api_connection'] = False

        return health