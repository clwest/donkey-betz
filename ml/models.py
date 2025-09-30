"""
ML Django Models - Session 24
Model version tracking for retraining pipeline
"""

from django.db import models
from django.utils import timezone


class MLModelVersion(models.Model):
    """
    Track ML model versions and performance over time

    Each retrain creates a new version with performance metrics.
    Only one version per sport can be active at a time.
    """

    # Model identification
    sport_type = models.CharField(
        max_length=10,
        choices=[
            ('nfl', 'NFL'),
            ('nba', 'NBA'),
            ('mlb', 'MLB'),
            ('nhl', 'NHL'),
        ],
        help_text="Sport this model predicts"
    )
    model_name = models.CharField(
        max_length=100,
        help_text="Model identifier (e.g., 'nfl_predictor')"
    )
    version = models.IntegerField(
        help_text="Incremental version number"
    )

    # Training metadata
    trained_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When model was trained"
    )
    training_samples = models.IntegerField(
        help_text="Number of games used for training"
    )
    training_start_date = models.DateField(
        help_text="Earliest game date in training data"
    )
    training_end_date = models.DateField(
        help_text="Latest game date in training data"
    )

    # Performance metrics
    validation_accuracy = models.FloatField(
        help_text="Accuracy on validation set (0.0 to 1.0)"
    )
    test_accuracy = models.FloatField(
        help_text="Accuracy on test set (0.0 to 1.0)"
    )
    calibration_score = models.FloatField(
        help_text="Calibration quality (log loss)"
    )
    precision = models.FloatField(
        null=True,
        blank=True,
        help_text="Precision score (0.0 to 1.0)"
    )
    recall = models.FloatField(
        null=True,
        blank=True,
        help_text="Recall score (0.0 to 1.0)"
    )

    # Deployment
    is_active = models.BooleanField(
        default=False,
        help_text="Is this the currently deployed model?"
    )
    model_file_path = models.CharField(
        max_length=500,
        help_text="Path to saved model file"
    )

    # Additional metadata
    training_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional training details (hyperparameters, etc.)"
    )
    deployment_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When model was activated"
    )
    retired_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When model was deactivated"
    )

    class Meta:
        unique_together = ['sport_type', 'version']
        ordering = ['-version']
        indexes = [
            models.Index(fields=['sport_type', 'is_active']),
            models.Index(fields=['sport_type', '-version']),
        ]
        verbose_name = "ML Model Version"
        verbose_name_plural = "ML Model Versions"

    def __str__(self):
        active_str = " [ACTIVE]" if self.is_active else ""
        return f"{self.sport_type.upper()} v{self.version} ({self.test_accuracy:.1%}){active_str}"

    def activate(self):
        """
        Make this model active (deactivate all other versions for this sport)
        """
        # Deactivate all other versions for this sport
        MLModelVersion.objects.filter(
            sport_type=self.sport_type,
            is_active=True
        ).update(is_active=False, retired_date=timezone.now())

        # Activate this version
        self.is_active = True
        self.deployment_date = timezone.now()
        self.save()

    def deactivate(self):
        """
        Deactivate this model version
        """
        self.is_active = False
        self.retired_date = timezone.now()
        self.save()

    @classmethod
    def get_active_model(cls, sport_type: str):
        """
        Get the currently active model for a sport

        Args:
            sport_type: 'nfl', 'nba', 'mlb', or 'nhl'

        Returns:
            MLModelVersion instance or None
        """
        return cls.objects.filter(
            sport_type=sport_type,
            is_active=True
        ).first()

    @classmethod
    def get_version_history(cls, sport_type: str):
        """
        Get all versions for a sport

        Args:
            sport_type: 'nfl', 'nba', 'mlb', or 'nhl'

        Returns:
            QuerySet of MLModelVersion instances
        """
        return cls.objects.filter(sport_type=sport_type).order_by('-version')

    @property
    def accuracy_percentage(self):
        """Return test accuracy as percentage string"""
        return f"{self.test_accuracy * 100:.1f}%"

    @property
    def improvement_over_previous(self):
        """
        Calculate improvement over previous version

        Returns:
            Float representing percentage point improvement, or None
        """
        if self.version == 1:
            return None

        previous = MLModelVersion.objects.filter(
            sport_type=self.sport_type,
            version=self.version - 1
        ).first()

        if previous:
            return (self.test_accuracy - previous.test_accuracy) * 100

        return None

    @property
    def days_active(self):
        """
        Calculate how many days this model has been active

        Returns:
            Integer days, or None if not active
        """
        if not self.deployment_date:
            return None

        end_date = self.retired_date or timezone.now()
        delta = end_date - self.deployment_date
        return delta.days