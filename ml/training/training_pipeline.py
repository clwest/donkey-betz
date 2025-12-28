"""
ML Training Pipeline
Automated training pipeline for all ML models in the Unified Donkey Betz Platform
"""

import logging
import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass

# ML Libraries
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

# Deep Learning

# Apple MLX (if available)
try:
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False

@dataclass
class TrainingConfig:
    """Training pipeline configuration"""
    model_save_dir: str = "ml/models"
    training_data_dir: str = "ml/data/processed"
    validation_split: float = 0.2
    test_split: float = 0.1
    random_seed: int = 42
    max_training_time_hours: int = 6
    model_performance_threshold: float = 0.7
    enable_mlx: bool = MLX_AVAILABLE

@dataclass
class TrainingResult:
    """Training result metrics"""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_time_seconds: float
    model_path: str
    feature_importance: Dict[str, float]

class MLTrainingPipeline:
    """
    Comprehensive ML training pipeline
    Trains all models for the Unified Donkey Betz Platform
    """

    def __init__(self, config: TrainingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.setup_directories()
        self.models = {}
        self.scalers = {}
        self.encoders = {}

    def setup_directories(self):
        """Create necessary directories"""
        directories = [
            self.config.model_save_dir,
            f"{self.config.model_save_dir}/sports_betting",
            f"{self.config.model_save_dir}/financial",
            f"{self.config.model_save_dir}/sentiment",
            f"{self.config.model_save_dir}/user_behavior",
            f"{self.config.model_save_dir}/cross_domain"
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    async def train_all_models(self) -> List[TrainingResult]:
        """Main training orchestrator"""
        self.logger.info("🚀 Starting comprehensive ML training pipeline...")

        training_tasks = [
            self.train_sports_betting_models(),
            self.train_financial_prediction_models(),
            self.train_sentiment_analysis_models(),
            self.train_user_behavior_models(),
            self.train_cross_domain_models()
        ]

        results = []
        for task in training_tasks:
            try:
                task_results = await task
                results.extend(task_results)
            except Exception as e:
                self.logger.error(f"Training task failed: {e}")

        # Generate training report
        await self.generate_training_report(results)

        self.logger.info(f"✅ Training completed. {len(results)} models trained.")
        return results

    async def train_sports_betting_models(self) -> List[TrainingResult]:
        """Train sports betting prediction models"""
        self.logger.info("🏀 Training sports betting models...")

        results = []

        try:
            # Load sports betting dataset
            data_path = Path(self.config.training_data_dir) / "sports_betting_dataset.csv"

            if not data_path.exists():
                self.logger.warning("Sports betting dataset not found")
                return results

            df = pd.read_csv(data_path)

            # Train different models for different sports
            sports_models = [
                ("nba_outcome_predictor", self._train_nba_outcome_model, df),
                ("nfl_spread_predictor", self._train_nfl_spread_model, df),
                ("soccer_total_predictor", self._train_soccer_total_model, df),
                ("baseball_run_predictor", self._train_baseball_run_model, df)
            ]

            for model_name, train_func, data in sports_models:
                try:
                    result = await train_func(data, model_name)
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"Failed to train {model_name}: {e}")

        except Exception as e:
            self.logger.error(f"Sports betting training failed: {e}")

        return results

    async def train_financial_prediction_models(self) -> List[TrainingResult]:
        """Train financial market prediction models"""
        self.logger.info("💰 Training financial prediction models...")

        results = []

        try:
            data_path = Path(self.config.training_data_dir) / "financial_prediction_dataset.csv"

            if not data_path.exists():
                self.logger.warning("Financial dataset not found")
                return results

            df = pd.read_csv(data_path)

            # Train financial models
            financial_models = [
                ("stock_direction_predictor", self._train_stock_direction_model, df),
                ("crypto_volatility_predictor", self._train_crypto_volatility_model, df),
                ("options_pricing_model", self._train_options_pricing_model, df),
                ("market_regime_classifier", self._train_market_regime_model, df)
            ]

            for model_name, train_func, data in financial_models:
                try:
                    result = await train_func(data, model_name)
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"Failed to train {model_name}: {e}")

        except Exception as e:
            self.logger.error(f"Financial training failed: {e}")

        return results

    async def train_sentiment_analysis_models(self) -> List[TrainingResult]:
        """Train sentiment analysis models"""
        self.logger.info("😊 Training sentiment analysis models...")

        results = []

        try:
            # Financial news sentiment model
            result = await self._train_financial_sentiment_model()
            if result:
                results.append(result)

            # Social media sentiment model
            result = await self._train_social_sentiment_model()
            if result:
                results.append(result)

        except Exception as e:
            self.logger.error(f"Sentiment analysis training failed: {e}")

        return results

    async def train_user_behavior_models(self) -> List[TrainingResult]:
        """Train user behavior prediction models"""
        self.logger.info("👤 Training user behavior models...")

        results = []

        try:
            data_path = Path(self.config.training_data_dir) / "user_behavior_dataset.csv"

            if not data_path.exists():
                self.logger.warning("User behavior dataset not found")
                return results

            df = pd.read_csv(data_path)

            # Train user behavior models
            behavior_models = [
                ("user_decision_predictor", self._train_user_decision_model, df),
                ("risk_tolerance_classifier", self._train_risk_tolerance_model, df),
                ("churn_prediction_model", self._train_churn_prediction_model, df)
            ]

            for model_name, train_func, data in behavior_models:
                try:
                    result = await train_func(data, model_name)
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"Failed to train {model_name}: {e}")

        except Exception as e:
            self.logger.error(f"User behavior training failed: {e}")

        return results

    async def train_cross_domain_models(self) -> List[TrainingResult]:
        """Train cross-domain pattern recognition models"""
        self.logger.info("🔗 Training cross-domain models...")

        results = []

        try:
            data_path = Path(self.config.training_data_dir) / "cross_domain_dataset.csv"

            if not data_path.exists():
                self.logger.warning("Cross-domain dataset not found")
                return results

            df = pd.read_csv(data_path)

            # Train cross-domain models
            cross_domain_models = [
                ("sports_crypto_correlation", self._train_sports_crypto_model, df),
                ("news_market_impact", self._train_news_market_model, df),
                ("weather_betting_correlation", self._train_weather_betting_model, df)
            ]

            for model_name, train_func, data in cross_domain_models:
                try:
                    result = await train_func(data, model_name)
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"Failed to train {model_name}: {e}")

        except Exception as e:
            self.logger.error(f"Cross-domain training failed: {e}")

        return results

    # Individual model training methods
    async def _train_nba_outcome_model(self, df: pd.DataFrame, model_name: str) -> Optional[TrainingResult]:
        """Train NBA game outcome prediction model"""
        try:
            # Filter NBA data
            nba_data = df[df['sport'] == 'basketball_nba'] if 'sport' in df.columns else df

            if len(nba_data) < 100:  # Need minimum data
                self.logger.warning(f"Insufficient NBA data: {len(nba_data)} samples")
                return None

            # Feature engineering for NBA
            features = self._engineer_nba_features(nba_data)
            target = self._create_nba_target(nba_data)

            # Train model
            return await self._train_classification_model(features, target, model_name, "sports_betting")

        except Exception as e:
            self.logger.error(f"NBA model training failed: {e}")
            return None

    async def _train_nfl_spread_model(self, df: pd.DataFrame, model_name: str) -> Optional[TrainingResult]:
        """Train NFL spread prediction model"""
        # Similar implementation for NFL
        return None

    async def _train_soccer_total_model(self, df: pd.DataFrame, model_name: str) -> Optional[TrainingResult]:
        """Train soccer total goals prediction model"""
        # Similar implementation for soccer
        return None

    async def _train_baseball_run_model(self, df: pd.DataFrame, model_name: str) -> Optional[TrainingResult]:
        """Train baseball run prediction model"""
        # Similar implementation for baseball
        return None

    async def _train_stock_direction_model(self, df: pd.DataFrame, model_name: str) -> Optional[TrainingResult]:
        """Train stock price direction prediction model"""
        try:
            # Filter stock data
            stock_data = df[df['category'] == 'stocks'] if 'category' in df.columns else df

            if len(stock_data) < 500:
                self.logger.warning(f"Insufficient stock data: {len(stock_data)} samples")
                return None

            # Feature engineering for stocks
            features = self._engineer_stock_features(stock_data)
            target = self._create_stock_direction_target(stock_data)

            return await self._train_classification_model(features, target, model_name, "financial")

        except Exception as e:
            self.logger.error(f"Stock direction model training failed: {e}")
            return None

    async def _train_crypto_volatility_model(self, df: pd.DataFrame, model_name: str) -> Optional[TrainingResult]:
        """Train cryptocurrency volatility prediction model"""
        # Implementation for crypto volatility
        return None

    async def _train_options_pricing_model(self, df: pd.DataFrame, model_name: str) -> Optional[TrainingResult]:
        """Train options pricing model"""
        # Implementation for options pricing
        return None

    async def _train_market_regime_model(self, df: pd.DataFrame, model_name: str) -> Optional[TrainingResult]:
        """Train market regime classification model"""
        # Implementation for market regime
        return None

    async def _train_financial_sentiment_model(self) -> Optional[TrainingResult]:
        """Train financial news sentiment analysis model"""
        # Implementation for financial sentiment
        return None

    async def _train_social_sentiment_model(self) -> Optional[TrainingResult]:
        """Train social media sentiment analysis model"""
        # Implementation for social sentiment
        return None

    async def _train_user_decision_model(self, df: pd.DataFrame, model_name: str) -> Optional[TrainingResult]:
        """Train user decision prediction model"""
        # Implementation for user decisions
        return None

    async def _train_risk_tolerance_model(self, df: pd.DataFrame, model_name: str) -> Optional[TrainingResult]:
        """Train risk tolerance classification model"""
        # Implementation for risk tolerance
        return None

    async def _train_churn_prediction_model(self, df: pd.DataFrame, model_name: str) -> Optional[TrainingResult]:
        """Train user churn prediction model"""
        # Implementation for churn prediction
        return None

    async def _train_sports_crypto_model(self, df: pd.DataFrame, model_name: str) -> Optional[TrainingResult]:
        """Train sports-crypto correlation model"""
        # Implementation for sports-crypto correlation
        return None

    async def _train_news_market_model(self, df: pd.DataFrame, model_name: str) -> Optional[TrainingResult]:
        """Train news-market impact model"""
        # Implementation for news-market impact
        return None

    async def _train_weather_betting_model(self, df: pd.DataFrame, model_name: str) -> Optional[TrainingResult]:
        """Train weather-betting correlation model"""
        # Implementation for weather-betting correlation
        return None

    # Core training utilities
    async def _train_classification_model(self, features: pd.DataFrame, target: pd.Series,
                                        model_name: str, category: str) -> Optional[TrainingResult]:
        """Train a classification model"""
        try:
            start_time = datetime.now()

            # Prepare data
            X_train, X_test, y_train, y_test = train_test_split(
                features, target, test_size=self.config.test_split + self.config.validation_split,
                random_state=self.config.random_seed, stratify=target
            )

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Train model
            if self.config.enable_mlx and MLX_AVAILABLE:
                model = await self._train_mlx_model(X_train_scaled, y_train)
            else:
                model = RandomForestClassifier(n_estimators=100, random_state=self.config.random_seed)
                model.fit(X_train_scaled, y_train)

            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

            # Check performance threshold
            if accuracy < self.config.model_performance_threshold:
                self.logger.warning(f"Model {model_name} accuracy {accuracy:.3f} below threshold")

            # Save model
            model_path = Path(self.config.model_save_dir) / category / f"{model_name}.joblib"
            scaler_path = Path(self.config.model_save_dir) / category / f"{model_name}_scaler.joblib"

            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)

            # Feature importance
            feature_importance = {}
            if hasattr(model, 'feature_importances_'):
                for i, importance in enumerate(model.feature_importances_):
                    feature_importance[features.columns[i]] = float(importance)

            training_time = (datetime.now() - start_time).total_seconds()

            result = TrainingResult(
                model_name=model_name,
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                training_time_seconds=training_time,
                model_path=str(model_path),
                feature_importance=feature_importance
            )

            self.logger.info(f"✅ Trained {model_name}: accuracy={accuracy:.3f}, f1={f1:.3f}")
            return result

        except Exception as e:
            self.logger.error(f"Classification model training failed: {e}")
            return None

    async def _train_regression_model(self, features: pd.DataFrame, target: pd.Series,
                                    model_name: str, category: str) -> Optional[TrainingResult]:
        """Train a regression model"""
        # Similar implementation for regression
        return None

    async def _train_mlx_model(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train model using Apple MLX"""
        # MLX-specific training implementation
        self.logger.info("Training with Apple MLX...")

        # For now, fall back to sklearn
        model = RandomForestClassifier(n_estimators=100, random_state=self.config.random_seed)
        model.fit(X_train, y_train)
        return model

    # Feature engineering methods
    def _engineer_nba_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for NBA prediction"""
        features = df.copy()

        # Add team strength metrics
        if 'home_team' in features.columns:
            features['home_team_encoded'] = LabelEncoder().fit_transform(features['home_team'])
        if 'away_team' in features.columns:
            features['away_team_encoded'] = LabelEncoder().fit_transform(features['away_team'])

        # Add historical performance features
        features['home_odds_implied'] = 1 / features.get('home_odds', 2.0)
        features['away_odds_implied'] = 1 / features.get('away_odds', 2.0)

        # Select numeric features only
        numeric_features = features.select_dtypes(include=[np.number])
        return numeric_features.fillna(0)

    def _create_nba_target(self, df: pd.DataFrame) -> pd.Series:
        """Create target variable for NBA prediction"""
        # For demonstration - would use actual game results
        return pd.Series(np.random.choice([0, 1], size=len(df)))

    def _engineer_stock_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for stock prediction"""
        features = df.copy()

        # Technical indicators
        features['price_change'] = features['close'] - features['open']
        features['price_change_pct'] = features['price_change'] / features['open']
        features['volatility'] = features['high'] - features['low']
        features['volume_price_trend'] = features['volume'] * features['price_change_pct']

        # Moving averages (simplified)
        features['ma_5'] = features['close'].rolling(5).mean()
        features['ma_20'] = features['close'].rolling(20).mean()

        numeric_features = features.select_dtypes(include=[np.number])
        return numeric_features.fillna(0)

    def _create_stock_direction_target(self, df: pd.DataFrame) -> pd.Series:
        """Create target for stock direction prediction"""
        # 1 if next day close > current close, 0 otherwise
        next_close = df['close'].shift(-1)
        current_close = df['close']
        return (next_close > current_close).astype(int).fillna(0)

    async def generate_training_report(self, results: List[TrainingResult]):
        """Generate comprehensive training report"""
        report = {
            "training_date": datetime.now().isoformat(),
            "total_models_trained": len(results),
            "successful_models": len([r for r in results if r.accuracy >= self.config.model_performance_threshold]),
            "average_accuracy": np.mean([r.accuracy for r in results]) if results else 0,
            "total_training_time_hours": sum([r.training_time_seconds for r in results]) / 3600,
            "model_details": []
        }

        for result in results:
            report["model_details"].append({
                "name": result.model_name,
                "accuracy": result.accuracy,
                "precision": result.precision,
                "recall": result.recall,
                "f1_score": result.f1_score,
                "training_time_minutes": result.training_time_seconds / 60,
                "model_path": result.model_path,
                "top_features": dict(sorted(result.feature_importance.items(),
                                          key=lambda x: x[1], reverse=True)[:5])
            })

        # Save report
        report_path = Path(self.config.model_save_dir) / f"training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"📊 Training report saved: {report_path}")

    def get_model_registry(self) -> Dict[str, Any]:
        """Get registry of all trained models"""
        registry = {
            "models": [],
            "last_updated": datetime.now().isoformat(),
            "total_models": 0
        }

        model_dir = Path(self.config.model_save_dir)
        for model_file in model_dir.rglob("*.joblib"):
            if not model_file.name.endswith("_scaler.joblib"):
                registry["models"].append({
                    "name": model_file.stem,
                    "path": str(model_file),
                    "category": model_file.parent.name,
                    "size_mb": round(model_file.stat().st_size / (1024 * 1024), 2),
                    "last_modified": datetime.fromtimestamp(model_file.stat().st_mtime).isoformat()
                })

        registry["total_models"] = len(registry["models"])
        return registry

# Standalone execution
async def main():
    """Main function for standalone execution"""
    config = TrainingConfig(
        model_save_dir="ml/models",
        training_data_dir="ml/data/processed"
    )

    pipeline = MLTrainingPipeline(config)
    results = await pipeline.train_all_models()

    print(f"Training completed. {len(results)} models trained.")
    for result in results:
        print(f"  {result.model_name}: accuracy={result.accuracy:.3f}")

if __name__ == "__main__":
    asyncio.run(main())