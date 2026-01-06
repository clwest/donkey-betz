"""
Agent-Model Configuration Models
================================

Session 676-677: Agent-specific ML model routing

This module provides database models for configuring which ML models
each agent should use, tracking model performance, and logging training runs.

Key Models:
- AgentModelConfig: Maps agents to their optimal ML models
- ModelPerformanceLog: Tracks model performance metrics over time
- ModelTrainingRun: Logs model training sessions
"""

from django.db import models
from django.utils import timezone


class AgentModelConfig(models.Model):
    """
    Configuration for which ML models each agent uses.

    Each agent can have a primary and secondary model with configurable
    weights for ensemble predictions.

    Example:
        ResearchAgent: embeddings (90%) + lightgbm (10%)
        StockAnalystAgent: lstm (70%) + xgboost (30%)
        BlockchainAuditCoordinator: gnn (40%) + isolation_forest (30%) + autoencoder (30%)
    """

    # Available model choices
    MODEL_CHOICES = [
        # Currently available models
        ('lightgbm', 'LightGBM (Gradient Boosting)'),
        ('xgboost', 'XGBoost (Gradient Boosting)'),
        ('random_forest', 'Random Forest'),
        ('isolation_forest', 'Isolation Forest (Anomaly)'),
        ('kmeans', 'K-Means Clustering'),
        ('mlp', 'MLP Neural Network'),
        ('distilbert', 'DistilBERT (Sentiment)'),
        ('embeddings', 'OpenAI Embeddings'),
        ('cosine_similarity', 'Cosine Similarity'),
        ('rules', 'Rule-Based Heuristics'),
        # Future models (Phase 2-5)
        ('lstm', 'LSTM (Time Series)'),
        ('prophet', 'Prophet (Seasonal)'),
        ('gnn', 'Graph Neural Network'),
        ('autoencoder', 'VAE Autoencoder'),
        ('rl', 'Reinforcement Learning'),
        ('dbscan', 'DBSCAN Clustering'),
        ('transformer', 'Small Transformer'),
    ]

    # Agent category choices for grouping
    CATEGORY_CHOICES = [
        ('time_series', 'Time-Series Agents'),
        ('semantic', 'Semantic/Text Agents'),
        ('anomaly', 'Anomaly/Security Agents'),
        ('decision', 'Decision/Optimization Agents'),
        ('clustering', 'Segmentation/Clustering Agents'),
        ('general', 'General Purpose Agents'),
    ]

    agent_name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Name of the agent (e.g., 'ResearchAgent', 'StockAnalystAgent')"
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        help_text="Agent category for grouping similar agents"
    )

    primary_model = models.CharField(
        max_length=50,
        choices=MODEL_CHOICES,
        default='lightgbm',
        help_text="Primary ML model for this agent"
    )

    secondary_model = models.CharField(
        max_length=50,
        choices=MODEL_CHOICES,
        blank=True,
        default='rules',
        help_text="Secondary ML model for ensemble (optional)"
    )

    tertiary_model = models.CharField(
        max_length=50,
        choices=MODEL_CHOICES,
        blank=True,
        default='',
        help_text="Tertiary ML model for complex ensembles (optional)"
    )

    model_weights = models.JSONField(
        default=dict,
        help_text="Weights for model ensemble, e.g., {'lightgbm': 0.6, 'rules': 0.4}"
    )

    custom_params = models.JSONField(
        default=dict,
        help_text="Custom parameters for model configuration"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this configuration is active"
    )

    use_fallback = models.BooleanField(
        default=True,
        help_text="Fall back to default model on error"
    )

    fallback_model = models.CharField(
        max_length=50,
        choices=MODEL_CHOICES,
        default='lightgbm',
        help_text="Model to use if primary fails"
    )

    # Performance tracking
    performance_score = models.FloatField(
        default=0.0,
        help_text="Current performance score (0-100)"
    )

    total_predictions = models.IntegerField(
        default=0,
        help_text="Total predictions made with this config"
    )

    successful_predictions = models.IntegerField(
        default=0,
        help_text="Number of successful predictions"
    )

    avg_latency_ms = models.FloatField(
        default=0.0,
        help_text="Average prediction latency in milliseconds"
    )

    last_evaluated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When performance was last evaluated"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'agent_model_config'
        verbose_name = 'Agent Model Configuration'
        verbose_name_plural = 'Agent Model Configurations'
        indexes = [
            models.Index(fields=['agent_name', 'is_active']),
            models.Index(fields=['category']),
            models.Index(fields=['primary_model']),
        ]

    def __str__(self):
        weights = self.model_weights or {}
        primary_weight = weights.get(self.primary_model, 1.0)
        return f"{self.agent_name}: {self.primary_model} ({primary_weight:.0%})"

    def get_model_ensemble(self):
        """
        Get the list of models and their weights for this agent.

        Returns:
            List of tuples: [(model_name, weight), ...]
        """
        weights = self.model_weights or {}
        ensemble = []

        if self.primary_model:
            weight = weights.get(self.primary_model, 0.6)
            ensemble.append((self.primary_model, weight))

        if self.secondary_model:
            weight = weights.get(self.secondary_model, 0.3)
            ensemble.append((self.secondary_model, weight))

        if self.tertiary_model:
            weight = weights.get(self.tertiary_model, 0.1)
            ensemble.append((self.tertiary_model, weight))

        # Normalize weights
        total_weight = sum(w for _, w in ensemble)
        if total_weight > 0:
            ensemble = [(m, w / total_weight) for m, w in ensemble]

        return ensemble

    def record_prediction(self, success: bool, latency_ms: float):
        """Record a prediction result for performance tracking."""
        self.total_predictions += 1
        if success:
            self.successful_predictions += 1

        # Update rolling average latency
        if self.avg_latency_ms == 0:
            self.avg_latency_ms = latency_ms
        else:
            # Exponential moving average
            self.avg_latency_ms = 0.9 * self.avg_latency_ms + 0.1 * latency_ms

        # Update performance score
        if self.total_predictions > 0:
            self.performance_score = (self.successful_predictions / self.total_predictions) * 100

        self.save(update_fields=[
            'total_predictions', 'successful_predictions',
            'avg_latency_ms', 'performance_score', 'updated_at'
        ])


class ModelPerformanceLog(models.Model):
    """
    Track model performance over time for analysis and optimization.

    Stores periodic snapshots of model performance metrics to identify
    trends and trigger retraining when performance degrades.
    """

    METRIC_CHOICES = [
        ('accuracy', 'Accuracy'),
        ('precision', 'Precision'),
        ('recall', 'Recall'),
        ('f1', 'F1 Score'),
        ('rmse', 'Root Mean Square Error'),
        ('mae', 'Mean Absolute Error'),
        ('r2', 'R-Squared'),
        ('auc', 'Area Under Curve'),
        ('latency', 'Inference Latency'),
        ('throughput', 'Predictions per Second'),
    ]

    config = models.ForeignKey(
        AgentModelConfig,
        on_delete=models.CASCADE,
        related_name='performance_logs'
    )

    evaluation_date = models.DateTimeField(auto_now_add=True)

    metric_name = models.CharField(
        max_length=50,
        choices=METRIC_CHOICES,
        help_text="Name of the performance metric"
    )

    metric_value = models.FloatField(
        help_text="Value of the metric"
    )

    sample_count = models.IntegerField(
        default=0,
        help_text="Number of samples used for evaluation"
    )

    model_version = models.CharField(
        max_length=20,
        blank=True,
        help_text="Version of the model evaluated"
    )

    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata about the evaluation"
    )

    class Meta:
        db_table = 'model_performance_log'
        verbose_name = 'Model Performance Log'
        verbose_name_plural = 'Model Performance Logs'
        indexes = [
            models.Index(fields=['config', 'evaluation_date']),
            models.Index(fields=['metric_name', 'evaluation_date']),
        ]
        ordering = ['-evaluation_date']

    def __str__(self):
        return f"{self.config.agent_name} - {self.metric_name}: {self.metric_value:.4f}"


class ModelTrainingRun(models.Model):
    """
    Track model training runs for versioning and reproducibility.

    Records hyperparameters, metrics, and model artifacts for each
    training session.
    """

    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    model_type = models.CharField(
        max_length=50,
        help_text="Type of model being trained (e.g., 'lightgbm', 'lstm')"
    )

    version = models.CharField(
        max_length=20,
        help_text="Model version string (e.g., 'v1.0', 'v2.3')"
    )

    agent_configs = models.ManyToManyField(
        AgentModelConfig,
        related_name='training_runs',
        blank=True,
        help_text="Agent configurations this model serves"
    )

    started_at = models.DateTimeField(auto_now_add=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When training completed"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='queued'
    )

    hyperparameters = models.JSONField(
        default=dict,
        help_text="Hyperparameters used for training"
    )

    metrics = models.JSONField(
        default=dict,
        help_text="Training and validation metrics"
    )

    training_samples = models.IntegerField(
        default=0,
        help_text="Number of training samples"
    )

    validation_samples = models.IntegerField(
        default=0,
        help_text="Number of validation samples"
    )

    model_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to saved model file"
    )

    error_message = models.TextField(
        blank=True,
        help_text="Error message if training failed"
    )

    notes = models.TextField(
        blank=True,
        help_text="Notes about this training run"
    )

    class Meta:
        db_table = 'model_training_run'
        verbose_name = 'Model Training Run'
        verbose_name_plural = 'Model Training Runs'
        indexes = [
            models.Index(fields=['model_type', 'status']),
            models.Index(fields=['started_at']),
        ]
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.model_type} {self.version} ({self.status})"

    @property
    def duration_seconds(self):
        """Calculate training duration in seconds."""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def mark_completed(self, metrics: dict = None):
        """Mark training as completed with optional metrics."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if metrics:
            self.metrics = metrics
        self.save()

    def mark_failed(self, error_message: str):
        """Mark training as failed with error message."""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save()
