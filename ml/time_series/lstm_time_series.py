"""
LSTM Time-Series Model
======================

Session 678: Phase 2 of Agent-Model Routing

Provides LSTM-based time-series forecasting for:
- StockAnalystAgent
- MarketMovementMonitorAgent
- SignalScannerAgent

Uses TensorFlow/Keras for LSTM implementation with:
- Configurable sequence length and prediction horizon
- Multi-step forecasting capability
- Built-in data preprocessing and scaling
- Model persistence with joblib
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)

# Check for TensorFlow availability
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    from tensorflow.keras.optimizers import Adam
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logger.warning("TensorFlow not available - LSTM will use fallback mode")

try:
    from sklearn.preprocessing import MinMaxScaler
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class LSTMPrediction:
    """Result from LSTM prediction."""
    success: bool
    predictions: List[float] = field(default_factory=list)
    direction: str = ""  # 'up', 'down', 'neutral'
    confidence: float = 0.0
    trend_strength: float = 0.0
    volatility: float = 0.0
    support_level: float = 0.0
    resistance_level: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'predictions': self.predictions,
            'direction': self.direction,
            'confidence': self.confidence,
            'trend_strength': self.trend_strength,
            'volatility': self.volatility,
            'support_level': self.support_level,
            'resistance_level': self.resistance_level,
            'metadata': self.metadata,
            'error': self.error,
        }


class LSTMTimeSeriesModel:
    """
    LSTM model for time-series forecasting.

    Features:
    - Configurable architecture (layers, units, dropout)
    - Multi-step ahead forecasting
    - Automatic data scaling
    - Support/resistance level detection
    - Trend and volatility analysis
    """

    DEFAULT_CONFIG = {
        'sequence_length': 60,  # Look back window (e.g., 60 days)
        'prediction_horizon': 5,  # Forecast steps ahead
        'lstm_units': [128, 64],  # LSTM layer sizes
        'dense_units': [32],  # Dense layer sizes
        'dropout_rate': 0.2,
        'learning_rate': 0.001,
        'batch_size': 32,
        'epochs': 100,
        'early_stopping_patience': 10,
    }

    def __init__(
        self,
        model_name: str = "lstm_time_series",
        config: Dict[str, Any] = None,
        model_dir: str = None,
    ):
        self.model_name = model_name
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self.model_dir = Path(model_dir or "ml/trained_models")
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1)) if SKLEARN_AVAILABLE else None
        self._is_trained = False
        self.training_history = None

    @property
    def is_trained(self) -> bool:
        return self._is_trained and self.model is not None

    def _build_model(self, input_shape: Tuple[int, int]) -> "Sequential":
        """Build the LSTM model architecture."""
        if not TF_AVAILABLE:
            raise RuntimeError("TensorFlow not available for LSTM model")

        model = Sequential()

        # First LSTM layer
        lstm_units = self.config['lstm_units']
        model.add(LSTM(
            lstm_units[0],
            return_sequences=len(lstm_units) > 1,
            input_shape=input_shape
        ))
        model.add(BatchNormalization())
        model.add(Dropout(self.config['dropout_rate']))

        # Additional LSTM layers
        for i, units in enumerate(lstm_units[1:]):
            return_seq = i < len(lstm_units) - 2
            model.add(LSTM(units, return_sequences=return_seq))
            model.add(BatchNormalization())
            model.add(Dropout(self.config['dropout_rate']))

        # Dense layers
        for units in self.config['dense_units']:
            model.add(Dense(units, activation='relu'))
            model.add(Dropout(self.config['dropout_rate'] / 2))

        # Output layer
        model.add(Dense(self.config['prediction_horizon']))

        model.compile(
            optimizer=Adam(learning_rate=self.config['learning_rate']),
            loss='mse',
            metrics=['mae']
        )

        return model

    def _prepare_sequences(
        self,
        data: np.ndarray,
        sequence_length: int = None,
        prediction_horizon: int = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare sequences for LSTM training/prediction.

        Args:
            data: 1D or 2D array of time series data
            sequence_length: Look-back window size
            prediction_horizon: Number of steps to predict

        Returns:
            X: Input sequences (samples, timesteps, features)
            y: Target values (samples, prediction_horizon)
        """
        seq_len = sequence_length or self.config['sequence_length']
        pred_horizon = prediction_horizon or self.config['prediction_horizon']

        # Ensure data is 2D
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        # Scale data
        if self.scaler is not None:
            scaled_data = self.scaler.fit_transform(data)
        else:
            scaled_data = data

        X, y = [], []
        for i in range(len(scaled_data) - seq_len - pred_horizon + 1):
            X.append(scaled_data[i:i + seq_len])
            # For multi-feature, use first column as target
            y.append(scaled_data[i + seq_len:i + seq_len + pred_horizon, 0])

        return np.array(X), np.array(y)

    def train(
        self,
        data: Union[np.ndarray, List[float]],
        validation_split: float = 0.2,
        verbose: int = 1,
    ) -> Dict[str, Any]:
        """
        Train the LSTM model on time-series data.

        Args:
            data: Time series data (1D array or list)
            validation_split: Fraction for validation
            verbose: Training verbosity (0, 1, or 2)

        Returns:
            Training metrics dict
        """
        if not TF_AVAILABLE:
            return {'success': False, 'error': 'TensorFlow not available'}

        try:
            # Convert to numpy array
            data = np.array(data) if not isinstance(data, np.ndarray) else data

            if len(data) < self.config['sequence_length'] + self.config['prediction_horizon'] + 10:
                return {
                    'success': False,
                    'error': f"Insufficient data: need at least {self.config['sequence_length'] + self.config['prediction_horizon'] + 10} points"
                }

            # Prepare sequences
            X, y = self._prepare_sequences(data)

            if len(X) == 0:
                return {'success': False, 'error': 'No sequences generated from data'}

            # Build model
            input_shape = (X.shape[1], X.shape[2])
            self.model = self._build_model(input_shape)

            # Setup callbacks
            callbacks = [
                EarlyStopping(
                    monitor='val_loss',
                    patience=self.config['early_stopping_patience'],
                    restore_best_weights=True
                ),
            ]

            # Train
            history = self.model.fit(
                X, y,
                epochs=self.config['epochs'],
                batch_size=self.config['batch_size'],
                validation_split=validation_split,
                callbacks=callbacks,
                verbose=verbose
            )

            self._is_trained = True
            self.training_history = history.history

            # Save model
            self.save()

            return {
                'success': True,
                'epochs_trained': len(history.history['loss']),
                'final_loss': history.history['loss'][-1],
                'final_val_loss': history.history.get('val_loss', [0])[-1],
                'final_mae': history.history['mae'][-1],
            }

        except Exception as e:
            logger.error(f"LSTM training failed: {e}")
            return {'success': False, 'error': str(e)}

    def predict(
        self,
        data: Union[np.ndarray, List[float]],
        return_confidence: bool = True,
    ) -> LSTMPrediction:
        """
        Make predictions on time-series data.

        Args:
            data: Recent time series data (at least sequence_length points)
            return_confidence: Whether to compute confidence metrics

        Returns:
            LSTMPrediction with forecasts and analysis
        """
        if not self.is_trained:
            return LSTMPrediction(
                success=False,
                error="Model not trained. Call train() first or load a saved model."
            )

        try:
            # Convert to numpy
            data = np.array(data) if not isinstance(data, np.ndarray) else data

            seq_len = self.config['sequence_length']
            if len(data) < seq_len:
                return LSTMPrediction(
                    success=False,
                    error=f"Need at least {seq_len} data points, got {len(data)}"
                )

            # Use most recent sequence_length points
            recent_data = data[-seq_len:]

            # Scale and reshape
            if recent_data.ndim == 1:
                recent_data = recent_data.reshape(-1, 1)

            scaled = self.scaler.transform(recent_data) if self.scaler else recent_data
            X = scaled.reshape(1, seq_len, -1)

            # Predict
            scaled_predictions = self.model.predict(X, verbose=0)[0]

            # Inverse scale predictions
            if self.scaler:
                # Create dummy array for inverse transform
                dummy = np.zeros((len(scaled_predictions), recent_data.shape[1]))
                dummy[:, 0] = scaled_predictions
                predictions = self.scaler.inverse_transform(dummy)[:, 0]
            else:
                predictions = scaled_predictions

            # Analyze predictions
            current_value = data[-1] if data.ndim == 1 else data[-1, 0]
            predicted_final = predictions[-1]

            # Direction
            pct_change = (predicted_final - current_value) / current_value * 100
            if pct_change > 1:
                direction = 'up'
            elif pct_change < -1:
                direction = 'down'
            else:
                direction = 'neutral'

            # Trend strength (0-1)
            trend_strength = min(abs(pct_change) / 10, 1.0)

            # Volatility from recent data
            volatility = float(np.std(data[-20:]) / np.mean(data[-20:])) if len(data) >= 20 else 0.0

            # Support/Resistance levels
            support_level = float(np.min(data[-20:])) if len(data) >= 20 else float(np.min(data))
            resistance_level = float(np.max(data[-20:])) if len(data) >= 20 else float(np.max(data))

            # Confidence based on model consistency
            if return_confidence and len(predictions) > 1:
                # Higher confidence if predictions trend consistently
                pred_diff = np.diff(predictions)
                consistency = 1 - np.std(np.sign(pred_diff))
                confidence = min(0.5 + consistency * 0.3 + (1 - volatility) * 0.2, 0.95)
            else:
                confidence = 0.5

            return LSTMPrediction(
                success=True,
                predictions=predictions.tolist(),
                direction=direction,
                confidence=confidence,
                trend_strength=trend_strength,
                volatility=volatility,
                support_level=support_level,
                resistance_level=resistance_level,
                metadata={
                    'current_value': float(current_value),
                    'predicted_final': float(predicted_final),
                    'pct_change': float(pct_change),
                    'sequence_length': seq_len,
                    'prediction_horizon': self.config['prediction_horizon'],
                }
            )

        except Exception as e:
            logger.error(f"LSTM prediction failed: {e}")
            return LSTMPrediction(success=False, error=str(e))

    def predict_with_fallback(
        self,
        data: Union[np.ndarray, List[float], Dict[str, Any]],
    ) -> LSTMPrediction:
        """
        Make predictions with fallback to simple analysis if model unavailable.

        This method works even without TensorFlow by using statistical analysis.
        """
        # Extract data from dict if needed
        if isinstance(data, dict):
            if 'prices' in data:
                data = data['prices']
            elif 'values' in data:
                data = data['values']
            elif 'data' in data:
                data = data['data']
            else:
                return LSTMPrediction(
                    success=False,
                    error="Dict must contain 'prices', 'values', or 'data' key"
                )

        data = np.array(data) if not isinstance(data, np.ndarray) else data

        # Try trained model first
        if self.is_trained:
            return self.predict(data)

        # Fallback: Simple statistical analysis
        if len(data) < 5:
            return LSTMPrediction(
                success=False,
                error="Need at least 5 data points"
            )

        try:
            # Simple moving average prediction
            current = data[-1]
            ma_short = np.mean(data[-5:])
            ma_long = np.mean(data[-20:]) if len(data) >= 20 else np.mean(data)

            # Trend from moving averages
            if ma_short > ma_long * 1.01:
                direction = 'up'
                trend_strength = min((ma_short / ma_long - 1) * 10, 1.0)
            elif ma_short < ma_long * 0.99:
                direction = 'down'
                trend_strength = min((1 - ma_short / ma_long) * 10, 1.0)
            else:
                direction = 'neutral'
                trend_strength = 0.1

            # Simple linear extrapolation for predictions
            if len(data) >= 10:
                slope = (data[-1] - data[-10]) / 10
            else:
                slope = (data[-1] - data[0]) / len(data)

            predictions = [float(current + slope * (i + 1)) for i in range(5)]

            # Volatility
            volatility = float(np.std(data[-20:]) / np.mean(data[-20:])) if len(data) >= 20 else float(np.std(data) / np.mean(data))

            return LSTMPrediction(
                success=True,
                predictions=predictions,
                direction=direction,
                confidence=0.4,  # Lower confidence for fallback
                trend_strength=trend_strength,
                volatility=volatility,
                support_level=float(np.min(data[-20:])) if len(data) >= 20 else float(np.min(data)),
                resistance_level=float(np.max(data[-20:])) if len(data) >= 20 else float(np.max(data)),
                metadata={
                    'fallback_mode': True,
                    'method': 'moving_average_extrapolation',
                    'current_value': float(current),
                    'ma_short': float(ma_short),
                    'ma_long': float(ma_long),
                }
            )

        except Exception as e:
            logger.error(f"Fallback prediction failed: {e}")
            return LSTMPrediction(success=False, error=str(e))

    def save(self, path: str = None) -> bool:
        """Save model to disk."""
        try:
            save_path = Path(path) if path else self.model_dir / f"{self.model_name}"

            if TF_AVAILABLE and self.model is not None:
                self.model.save(f"{save_path}_model.keras")

            if self.scaler is not None:
                joblib.dump(self.scaler, f"{save_path}_scaler.joblib")

            # Save config
            joblib.dump({
                'config': self.config,
                'is_trained': self._is_trained,
                'model_name': self.model_name,
            }, f"{save_path}_meta.joblib")

            logger.info(f"Saved LSTM model to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False

    def load(self, path: str = None) -> bool:
        """Load model from disk."""
        try:
            load_path = Path(path) if path else self.model_dir / f"{self.model_name}"

            # Load metadata
            meta_path = f"{load_path}_meta.joblib"
            if os.path.exists(meta_path):
                meta = joblib.load(meta_path)
                self.config = meta.get('config', self.config)
                self._is_trained = meta.get('is_trained', False)

            # Load scaler
            scaler_path = f"{load_path}_scaler.joblib"
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)

            # Load Keras model
            if TF_AVAILABLE:
                model_path = f"{load_path}_model.keras"
                if os.path.exists(model_path):
                    self.model = load_model(model_path)
                    self._is_trained = True

            logger.info(f"Loaded LSTM model from {load_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


# Singleton instance
_lstm_model = None


def get_lstm_model(model_name: str = "lstm_time_series") -> LSTMTimeSeriesModel:
    """Get or create the LSTM model singleton."""
    global _lstm_model
    if _lstm_model is None or _lstm_model.model_name != model_name:
        _lstm_model = LSTMTimeSeriesModel(model_name=model_name)
        # Try to load existing model
        _lstm_model.load()
    return _lstm_model
