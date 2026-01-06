"""
VAE Anomaly Detector
====================

Session 679: Phase 3 - Anomaly Detection

Variational Autoencoder (VAE) for detecting anomalies in:
- Blockchain transactions (ExploitDetectorAgent)
- Market behavior (MarketAnomalyDetectorAgent)
- Trading patterns (BlockchainAuditCoordinator)

Features:
- Full VAE model with TensorFlow/Keras (when available)
- Fallback mode using statistical methods (no TensorFlow required)
- Reconstruction error-based anomaly scoring
- Configurable anomaly thresholds
- Support for both training and inference

Fallback Mode:
When TensorFlow is not installed, uses:
- Mahalanobis distance from centroid
- IQR-based outlier detection
- Z-score anomaly scoring
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)

# Check TensorFlow availability
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logger.info("TensorFlow not available - VAE will use fallback mode")


@dataclass
class AnomalyPrediction:
    """
    Structured result from VAE anomaly detection.

    Attributes:
        success: Whether prediction succeeded
        anomaly_scores: Per-sample anomaly scores (higher = more anomalous)
        is_anomaly: Boolean flags for each sample
        reconstruction_error: Raw reconstruction errors
        threshold: Anomaly threshold used
        confidence: Confidence in the prediction (0-1)
        anomaly_indices: Indices of detected anomalies
        severity: Severity classification ('low', 'medium', 'high', 'critical')
        metadata: Additional prediction metadata
        error: Error message if prediction failed
    """
    success: bool
    anomaly_scores: List[float] = field(default_factory=list)
    is_anomaly: List[bool] = field(default_factory=list)
    reconstruction_error: List[float] = field(default_factory=list)
    threshold: float = 0.0
    confidence: float = 0.0
    anomaly_indices: List[int] = field(default_factory=list)
    severity: str = 'low'
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'anomaly_scores': self.anomaly_scores,
            'is_anomaly': self.is_anomaly,
            'reconstruction_error': self.reconstruction_error,
            'threshold': self.threshold,
            'confidence': self.confidence,
            'anomaly_indices': self.anomaly_indices,
            'severity': self.severity,
            'metadata': self.metadata,
            'error': self.error,
        }


class VAEAnomalyDetector:
    """
    Variational Autoencoder for anomaly detection.

    Uses reconstruction error to identify anomalies:
    - Normal data: Low reconstruction error (VAE learned the pattern)
    - Anomalous data: High reconstruction error (outside learned distribution)

    Architecture (when TensorFlow available):
        Encoder: input → dense(128) → dense(64) → [mu, log_var]
        Decoder: z → dense(64) → dense(128) → output

    Fallback (no TensorFlow):
        Uses Mahalanobis distance and IQR-based outlier detection
    """

    DEFAULT_CONFIG = {
        # VAE architecture
        'latent_dim': 16,
        'encoder_layers': [128, 64],
        'decoder_layers': [64, 128],
        'activation': 'relu',
        'dropout_rate': 0.2,

        # Training
        'epochs': 50,
        'batch_size': 32,
        'learning_rate': 0.001,
        'validation_split': 0.1,

        # Anomaly detection
        'threshold_percentile': 95,  # Percentile for anomaly threshold
        'min_samples': 30,  # Minimum samples for training/detection

        # Fallback config
        'fallback_method': 'mahalanobis',  # 'mahalanobis', 'iqr', 'zscore'
        'zscore_threshold': 3.0,
        'iqr_multiplier': 1.5,
    }

    def __init__(self, model_name: str = "vae_anomaly_detector", config: Dict = None):
        self.model_name = model_name
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self.is_trained = False

        # VAE components (TensorFlow)
        self._encoder = None
        self._decoder = None
        self._vae = None

        # Fallback components (statistical)
        self._mean = None
        self._cov_inv = None
        self._std = None
        self._q1 = None
        self._q3 = None
        self._iqr = None

        # Anomaly threshold
        self._threshold = None

    def _build_vae(self, input_dim: int) -> None:
        """Build VAE model with TensorFlow/Keras."""
        if not TF_AVAILABLE:
            return

        latent_dim = self.config['latent_dim']
        encoder_layers = self.config['encoder_layers']
        decoder_layers = self.config['decoder_layers']
        activation = self.config['activation']
        dropout = self.config['dropout_rate']

        # Encoder
        encoder_inputs = keras.Input(shape=(input_dim,))
        x = encoder_inputs

        for units in encoder_layers:
            x = layers.Dense(units, activation=activation)(x)
            x = layers.Dropout(dropout)(x)

        # Latent space
        z_mean = layers.Dense(latent_dim, name='z_mean')(x)
        z_log_var = layers.Dense(latent_dim, name='z_log_var')(x)

        # Sampling layer
        def sampling(args):
            z_mean, z_log_var = args
            batch = tf.shape(z_mean)[0]
            dim = tf.shape(z_mean)[1]
            epsilon = tf.random.normal(shape=(batch, dim))
            return z_mean + tf.exp(0.5 * z_log_var) * epsilon

        z = layers.Lambda(sampling, name='z')([z_mean, z_log_var])

        self._encoder = keras.Model(encoder_inputs, [z_mean, z_log_var, z], name='encoder')

        # Decoder
        latent_inputs = keras.Input(shape=(latent_dim,))
        x = latent_inputs

        for units in decoder_layers:
            x = layers.Dense(units, activation=activation)(x)
            x = layers.Dropout(dropout)(x)

        decoder_outputs = layers.Dense(input_dim, activation='linear')(x)
        self._decoder = keras.Model(latent_inputs, decoder_outputs, name='decoder')

        # VAE model
        outputs = self._decoder(self._encoder(encoder_inputs)[2])
        self._vae = keras.Model(encoder_inputs, outputs, name='vae')

        # Custom loss (reconstruction + KL divergence)
        reconstruction_loss = keras.losses.MeanSquaredError()(encoder_inputs, outputs)
        reconstruction_loss *= input_dim

        kl_loss = 1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var)
        kl_loss = tf.reduce_mean(kl_loss) * -0.5

        vae_loss = reconstruction_loss + kl_loss
        self._vae.add_loss(vae_loss)

        self._vae.compile(optimizer=keras.optimizers.Adam(learning_rate=self.config['learning_rate']))

    def train(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Train the VAE on normal data.

        Args:
            data: Training data (should be "normal" samples)

        Returns:
            Training history and metrics
        """
        data = self._ensure_numpy(data)

        if len(data) < self.config['min_samples']:
            return {
                'success': False,
                'error': f"Need at least {self.config['min_samples']} samples, got {len(data)}",
            }

        # Normalize data
        self._mean = np.mean(data, axis=0)
        self._std = np.std(data, axis=0) + 1e-8
        normalized = (data - self._mean) / self._std

        if TF_AVAILABLE:
            return self._train_vae(normalized)
        else:
            return self._train_fallback(normalized, data)

    def _train_vae(self, normalized: np.ndarray) -> Dict[str, Any]:
        """Train full VAE model."""
        input_dim = normalized.shape[1]
        self._build_vae(input_dim)

        history = self._vae.fit(
            normalized, normalized,
            epochs=self.config['epochs'],
            batch_size=self.config['batch_size'],
            validation_split=self.config['validation_split'],
            verbose=0,
        )

        # Calculate threshold from training data
        reconstructed = self._vae.predict(normalized, verbose=0)
        errors = np.mean(np.square(normalized - reconstructed), axis=1)
        self._threshold = np.percentile(errors, self.config['threshold_percentile'])

        self.is_trained = True

        return {
            'success': True,
            'method': 'vae',
            'epochs': self.config['epochs'],
            'final_loss': float(history.history['loss'][-1]),
            'threshold': float(self._threshold),
            'samples_trained': len(normalized),
        }

    def _train_fallback(self, normalized: np.ndarray, original: np.ndarray) -> Dict[str, Any]:
        """Train fallback statistical model."""
        method = self.config['fallback_method']

        if method == 'mahalanobis':
            # Calculate covariance inverse for Mahalanobis distance
            try:
                cov = np.cov(normalized.T)
                if cov.ndim == 0:
                    cov = np.array([[cov]])
                self._cov_inv = np.linalg.inv(cov + np.eye(cov.shape[0]) * 1e-6)
            except Exception:
                # Fall back to simple distance if covariance is singular
                self._cov_inv = np.eye(normalized.shape[1])

            # Calculate distances for threshold
            distances = self._mahalanobis_distance(normalized)
            self._threshold = np.percentile(distances, self.config['threshold_percentile'])

        elif method == 'iqr':
            # IQR-based outlier detection
            self._q1 = np.percentile(original, 25, axis=0)
            self._q3 = np.percentile(original, 75, axis=0)
            self._iqr = self._q3 - self._q1
            self._threshold = self.config['iqr_multiplier']

        else:  # zscore
            self._threshold = self.config['zscore_threshold']

        self.is_trained = True

        return {
            'success': True,
            'method': f'fallback_{method}',
            'threshold': float(self._threshold) if not isinstance(self._threshold, np.ndarray) else self._threshold.tolist(),
            'samples_trained': len(normalized),
        }

    def _mahalanobis_distance(self, data: np.ndarray) -> np.ndarray:
        """Calculate Mahalanobis distance from centroid."""
        diff = data - np.mean(data, axis=0)
        distances = np.sqrt(np.sum(diff @ self._cov_inv * diff, axis=1))
        return distances

    def predict(self, data: np.ndarray) -> AnomalyPrediction:
        """
        Detect anomalies in data using trained model.

        Args:
            data: Input data to check for anomalies

        Returns:
            AnomalyPrediction with anomaly scores and flags
        """
        if not self.is_trained:
            return AnomalyPrediction(
                success=False,
                error="Model not trained. Call train() first.",
            )

        data = self._ensure_numpy(data)

        if len(data) == 0:
            return AnomalyPrediction(
                success=False,
                error="Empty data array",
            )

        # Normalize
        normalized = (data - self._mean) / self._std

        if TF_AVAILABLE and self._vae is not None:
            return self._predict_vae(normalized)
        else:
            return self._predict_fallback(normalized, data)

    def _predict_vae(self, normalized: np.ndarray) -> AnomalyPrediction:
        """Predict using full VAE model."""
        # Reconstruct
        reconstructed = self._vae.predict(normalized, verbose=0)
        errors = np.mean(np.square(normalized - reconstructed), axis=1)

        # Normalize scores to 0-1 range
        max_error = max(self._threshold * 3, np.max(errors))
        anomaly_scores = (errors / max_error).clip(0, 1).tolist()

        # Classify anomalies
        is_anomaly = (errors > self._threshold).tolist()
        anomaly_indices = [i for i, x in enumerate(is_anomaly) if x]

        # Calculate severity
        severity = self._calculate_severity(errors, self._threshold)

        # Confidence based on model training
        confidence = 0.75 if len(anomaly_indices) > 0 else 0.85

        return AnomalyPrediction(
            success=True,
            anomaly_scores=anomaly_scores,
            is_anomaly=is_anomaly,
            reconstruction_error=errors.tolist(),
            threshold=float(self._threshold),
            confidence=confidence,
            anomaly_indices=anomaly_indices,
            severity=severity,
            metadata={
                'method': 'vae',
                'num_anomalies': len(anomaly_indices),
                'anomaly_rate': len(anomaly_indices) / len(normalized),
            },
        )

    def _predict_fallback(self, normalized: np.ndarray, original: np.ndarray) -> AnomalyPrediction:
        """Predict using fallback statistical methods."""
        method = self.config['fallback_method']

        if method == 'mahalanobis':
            distances = self._mahalanobis_distance(normalized)
            max_dist = max(self._threshold * 3, np.max(distances))
            anomaly_scores = (distances / max_dist).clip(0, 1).tolist()
            is_anomaly = (distances > self._threshold).tolist()
            reconstruction_error = distances.tolist()

        elif method == 'iqr':
            # IQR-based outlier detection
            lower = self._q1 - self._threshold * self._iqr
            upper = self._q3 + self._threshold * self._iqr

            # Check if any feature is outside bounds
            below = original < lower
            above = original > upper
            outlier_mask = np.any(below | above, axis=1)

            # Score based on how far outside bounds
            deviations = np.maximum(
                np.maximum(lower - original, 0),
                np.maximum(original - upper, 0)
            )
            max_deviation = np.max(deviations) + 1e-8
            scores = np.max(deviations / max_deviation, axis=1)

            anomaly_scores = scores.tolist()
            is_anomaly = outlier_mask.tolist()
            reconstruction_error = np.sum(deviations, axis=1).tolist()

        else:  # zscore
            z_scores = np.abs(normalized)
            max_z = np.max(z_scores, axis=1)

            anomaly_scores = (max_z / (self._threshold * 2)).clip(0, 1).tolist()
            is_anomaly = (max_z > self._threshold).tolist()
            reconstruction_error = max_z.tolist()

        anomaly_indices = [i for i, x in enumerate(is_anomaly) if x]
        severity = self._calculate_severity(
            np.array(reconstruction_error),
            float(self._threshold) if not isinstance(self._threshold, np.ndarray) else np.mean(self._threshold)
        )

        return AnomalyPrediction(
            success=True,
            anomaly_scores=anomaly_scores,
            is_anomaly=is_anomaly,
            reconstruction_error=reconstruction_error,
            threshold=float(self._threshold) if not isinstance(self._threshold, np.ndarray) else float(np.mean(self._threshold)),
            confidence=0.5,  # Lower confidence for fallback
            anomaly_indices=anomaly_indices,
            severity=severity,
            metadata={
                'method': f'fallback_{method}',
                'fallback_mode': True,
                'num_anomalies': len(anomaly_indices),
                'anomaly_rate': len(anomaly_indices) / len(normalized) if len(normalized) > 0 else 0,
            },
        )

    def predict_with_fallback(self, data: Union[List, np.ndarray, Dict]) -> AnomalyPrediction:
        """
        Detect anomalies with automatic fallback and auto-training.

        This is the main entry point for anomaly detection.
        If not trained, trains on the provided data (assuming mostly normal).

        Args:
            data: Input data - can be:
                - List of values
                - numpy array
                - Dict with 'values', 'transactions', or 'features' key

        Returns:
            AnomalyPrediction with anomaly scores and classifications
        """
        # Extract data from various input formats
        data = self._extract_data(data)

        if data is None or len(data) == 0:
            return AnomalyPrediction(
                success=False,
                error="No valid data provided",
            )

        if len(data) < self.config['min_samples']:
            return AnomalyPrediction(
                success=False,
                error=f"Need at least {self.config['min_samples']} data points, got {len(data)}",
            )

        # Auto-train if not trained
        if not self.is_trained:
            train_result = self.train(data)
            if not train_result.get('success'):
                return AnomalyPrediction(
                    success=False,
                    error=f"Training failed: {train_result.get('error')}",
                )

        return self.predict(data)

    def _extract_data(self, data: Any) -> Optional[np.ndarray]:
        """Extract numpy array from various input formats."""
        if isinstance(data, np.ndarray):
            return data if data.ndim == 2 else data.reshape(-1, 1)

        if isinstance(data, list):
            arr = np.array(data)
            return arr if arr.ndim == 2 else arr.reshape(-1, 1)

        if isinstance(data, dict):
            for key in ['values', 'transactions', 'features', 'data', 'prices']:
                if key in data:
                    return self._extract_data(data[key])

        return None

    def _ensure_numpy(self, data: Any) -> np.ndarray:
        """Convert data to numpy array."""
        if isinstance(data, np.ndarray):
            return data if data.ndim == 2 else data.reshape(-1, 1)
        arr = np.array(data)
        return arr if arr.ndim == 2 else arr.reshape(-1, 1)

    def _calculate_severity(self, errors: np.ndarray, threshold: float) -> str:
        """Calculate overall severity of detected anomalies."""
        if len(errors) == 0:
            return 'low'

        max_error = np.max(errors)
        anomaly_rate = np.mean(errors > threshold)

        if max_error > threshold * 5 or anomaly_rate > 0.3:
            return 'critical'
        elif max_error > threshold * 3 or anomaly_rate > 0.2:
            return 'high'
        elif max_error > threshold * 1.5 or anomaly_rate > 0.1:
            return 'medium'
        else:
            return 'low'

    def get_model_info(self) -> Dict[str, Any]:
        """Return model information."""
        return {
            'model_name': self.model_name,
            'is_trained': self.is_trained,
            'config': self.config,
            'tensorflow_available': TF_AVAILABLE,
            'threshold': self._threshold,
            'method': 'vae' if TF_AVAILABLE and self._vae else f"fallback_{self.config['fallback_method']}",
        }


# Singleton instance
_vae_detector = None


def get_vae_detector() -> VAEAnomalyDetector:
    """Get the singleton VAE detector instance."""
    global _vae_detector
    if _vae_detector is None:
        _vae_detector = VAEAnomalyDetector()
    return _vae_detector
