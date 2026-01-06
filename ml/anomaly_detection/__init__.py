"""
Anomaly Detection Models Package
================================

Session 679: Phase 3 Anomaly Detection

Contains:
- vae_anomaly_detector.py: VAE model for anomaly detection
"""

from .vae_anomaly_detector import (
    VAEAnomalyDetector,
    AnomalyPrediction,
    get_vae_detector,
)

__all__ = [
    'VAEAnomalyDetector',
    'AnomalyPrediction',
    'get_vae_detector',
]
