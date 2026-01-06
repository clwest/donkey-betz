"""
Prophet Seasonal Forecasting Model
==================================

Session 678: Phase 2 of Agent-Model Routing

Provides Prophet-based seasonal forecasting for:
- TrendAnalysisAgent
- PredictionMarketAnalyst
- WhaleWatcherAgent (whale activity patterns)

Uses Facebook Prophet for:
- Automatic seasonality detection (daily, weekly, yearly)
- Holiday effects modeling
- Trend changepoint detection
- Uncertainty intervals
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)

# Check for Prophet availability
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logger.warning("Prophet not available - will use fallback mode")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False


@dataclass
class ProphetPrediction:
    """Result from Prophet prediction."""
    success: bool
    predictions: List[float] = field(default_factory=list)
    lower_bounds: List[float] = field(default_factory=list)
    upper_bounds: List[float] = field(default_factory=list)
    dates: List[str] = field(default_factory=list)
    trend: str = ""  # 'increasing', 'decreasing', 'stable'
    trend_slope: float = 0.0
    seasonality: Dict[str, float] = field(default_factory=dict)  # weekly, yearly strength
    changepoints: List[str] = field(default_factory=list)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'predictions': self.predictions,
            'lower_bounds': self.lower_bounds,
            'upper_bounds': self.upper_bounds,
            'dates': self.dates,
            'trend': self.trend,
            'trend_slope': self.trend_slope,
            'seasonality': self.seasonality,
            'changepoints': self.changepoints,
            'confidence': self.confidence,
            'metadata': self.metadata,
            'error': self.error,
        }


class ProphetForecaster:
    """
    Prophet-based seasonal forecasting model.

    Features:
    - Automatic seasonality detection
    - Trend changepoint analysis
    - Uncertainty quantification
    - Holiday effects (optional)
    - Multiple seasonality modes (additive/multiplicative)
    """

    DEFAULT_CONFIG = {
        'prediction_days': 30,  # Days to forecast
        'yearly_seasonality': True,
        'weekly_seasonality': True,
        'daily_seasonality': False,
        'seasonality_mode': 'multiplicative',  # or 'additive'
        'changepoint_prior_scale': 0.05,  # Flexibility of trend
        'seasonality_prior_scale': 10,
        'interval_width': 0.8,  # Uncertainty interval
        'growth': 'linear',  # or 'logistic'
    }

    def __init__(
        self,
        model_name: str = "prophet_forecaster",
        config: Dict[str, Any] = None,
        model_dir: str = None,
    ):
        self.model_name = model_name
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self.model_dir = Path(model_dir or "ml/trained_models")
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.model = None
        self._is_trained = False
        self._last_training_data = None

    @property
    def is_trained(self) -> bool:
        return self._is_trained and self.model is not None

    def _prepare_dataframe(
        self,
        data: Union[np.ndarray, List[float], pd.DataFrame],
        dates: List[str] = None,
    ) -> pd.DataFrame:
        """
        Prepare data in Prophet's expected format (ds, y columns).

        Args:
            data: Time series values
            dates: Optional date strings (if not provided, will generate)

        Returns:
            DataFrame with 'ds' and 'y' columns
        """
        if not PANDAS_AVAILABLE:
            raise RuntimeError("Pandas required for Prophet")

        if isinstance(data, pd.DataFrame):
            if 'ds' in data.columns and 'y' in data.columns:
                return data
            elif 'date' in data.columns and 'value' in data.columns:
                return data.rename(columns={'date': 'ds', 'value': 'y'})
            else:
                # Assume first column is date, second is value
                df = data.copy()
                df.columns = ['ds', 'y'] + list(df.columns[2:])
                return df

        # Convert to array
        values = np.array(data) if not isinstance(data, np.ndarray) else data

        # Generate dates if not provided
        if dates is None:
            # Assume daily data ending today
            end_date = datetime.now()
            dates = [
                (end_date - timedelta(days=len(values) - i - 1)).strftime('%Y-%m-%d')
                for i in range(len(values))
            ]

        return pd.DataFrame({'ds': dates, 'y': values})

    def train(
        self,
        data: Union[np.ndarray, List[float], pd.DataFrame],
        dates: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Train the Prophet model on time-series data.

        Args:
            data: Time series values or DataFrame
            dates: Optional date strings

        Returns:
            Training result dict
        """
        if not PROPHET_AVAILABLE:
            return {'success': False, 'error': 'Prophet not available'}

        try:
            # Prepare data
            df = self._prepare_dataframe(data, dates)

            if len(df) < 30:
                return {
                    'success': False,
                    'error': f"Need at least 30 data points, got {len(df)}"
                }

            # Initialize Prophet model
            self.model = Prophet(
                yearly_seasonality=self.config['yearly_seasonality'],
                weekly_seasonality=self.config['weekly_seasonality'],
                daily_seasonality=self.config['daily_seasonality'],
                seasonality_mode=self.config['seasonality_mode'],
                changepoint_prior_scale=self.config['changepoint_prior_scale'],
                seasonality_prior_scale=self.config['seasonality_prior_scale'],
                interval_width=self.config['interval_width'],
                growth=self.config['growth'],
            )

            # Fit model (suppress Prophet's logging)
            with suppress_stdout_stderr():
                self.model.fit(df)

            self._is_trained = True
            self._last_training_data = df

            # Get training metrics
            changepoints = self.model.changepoints.dt.strftime('%Y-%m-%d').tolist() if hasattr(self.model, 'changepoints') else []

            # Save model
            self.save()

            return {
                'success': True,
                'data_points': len(df),
                'date_range': f"{df['ds'].min()} to {df['ds'].max()}",
                'changepoints_detected': len(changepoints),
                'changepoint_dates': changepoints[:5],  # First 5
            }

        except Exception as e:
            logger.error(f"Prophet training failed: {e}")
            return {'success': False, 'error': str(e)}

    def predict(
        self,
        periods: int = None,
        include_history: bool = False,
    ) -> ProphetPrediction:
        """
        Make future predictions.

        Args:
            periods: Number of days to forecast (default from config)
            include_history: Whether to include historical predictions

        Returns:
            ProphetPrediction with forecasts and analysis
        """
        if not self.is_trained:
            return ProphetPrediction(
                success=False,
                error="Model not trained. Call train() first."
            )

        try:
            periods = periods or self.config['prediction_days']

            # Create future dataframe
            future = self.model.make_future_dataframe(periods=periods)

            # Predict
            with suppress_stdout_stderr():
                forecast = self.model.predict(future)

            # Extract predictions (future only or all)
            if include_history:
                pred_df = forecast
            else:
                pred_df = forecast.tail(periods)

            predictions = pred_df['yhat'].tolist()
            lower_bounds = pred_df['yhat_lower'].tolist()
            upper_bounds = pred_df['yhat_upper'].tolist()
            dates = pred_df['ds'].dt.strftime('%Y-%m-%d').tolist()

            # Analyze trend
            trend_values = pred_df['trend'].values
            if len(trend_values) >= 2:
                trend_slope = (trend_values[-1] - trend_values[0]) / len(trend_values)
                if trend_slope > 0.001:
                    trend = 'increasing'
                elif trend_slope < -0.001:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend_slope = 0
                trend = 'stable'

            # Extract seasonality strengths
            seasonality = {}
            if 'weekly' in forecast.columns:
                seasonality['weekly'] = float(forecast['weekly'].std())
            if 'yearly' in forecast.columns:
                seasonality['yearly'] = float(forecast['yearly'].std())

            # Get changepoints
            changepoints = []
            if hasattr(self.model, 'changepoints') and self.model.changepoints is not None:
                changepoints = self.model.changepoints.dt.strftime('%Y-%m-%d').tolist()

            # Confidence based on interval width
            avg_interval = np.mean(np.array(upper_bounds) - np.array(lower_bounds))
            avg_value = np.mean(predictions)
            relative_interval = avg_interval / avg_value if avg_value != 0 else 1
            confidence = max(0.3, min(0.9, 1 - relative_interval))

            return ProphetPrediction(
                success=True,
                predictions=predictions,
                lower_bounds=lower_bounds,
                upper_bounds=upper_bounds,
                dates=dates,
                trend=trend,
                trend_slope=float(trend_slope),
                seasonality=seasonality,
                changepoints=changepoints,
                confidence=confidence,
                metadata={
                    'periods_forecast': periods,
                    'include_history': include_history,
                    'growth_type': self.config['growth'],
                    'seasonality_mode': self.config['seasonality_mode'],
                }
            )

        except Exception as e:
            logger.error(f"Prophet prediction failed: {e}")
            return ProphetPrediction(success=False, error=str(e))

    def predict_with_data(
        self,
        data: Union[np.ndarray, List[float], pd.DataFrame, Dict[str, Any]],
        dates: List[str] = None,
        periods: int = None,
    ) -> ProphetPrediction:
        """
        Train and predict in one call (convenience method).

        For quick predictions when you have new data.
        """
        # Extract from dict if needed
        if isinstance(data, dict):
            if 'prices' in data:
                data = data['prices']
            elif 'values' in data:
                data = data['values']
            elif 'data' in data:
                data = data['data']
            dates = data.get('dates') if isinstance(data, dict) else dates

        # Train on data
        train_result = self.train(data, dates)
        if not train_result['success']:
            return ProphetPrediction(success=False, error=train_result['error'])

        # Predict
        return self.predict(periods=periods)

    def predict_with_fallback(
        self,
        data: Union[np.ndarray, List[float], Dict[str, Any]],
        periods: int = None,
    ) -> ProphetPrediction:
        """
        Make predictions with fallback to simple analysis if Prophet unavailable.
        """
        # Extract from dict
        if isinstance(data, dict):
            if 'prices' in data:
                data = data['prices']
            elif 'values' in data:
                data = data['values']
            elif 'data' in data:
                data = data['data']

        data = np.array(data) if not isinstance(data, np.ndarray) else data
        periods = periods or self.config['prediction_days']

        # Try Prophet first
        if PROPHET_AVAILABLE:
            result = self.predict_with_data(data, periods=periods)
            if result.success:
                return result

        # Fallback: Simple trend + seasonality estimation
        if len(data) < 7:
            return ProphetPrediction(
                success=False,
                error="Need at least 7 data points"
            )

        try:
            # Simple linear trend
            x = np.arange(len(data))
            slope, intercept = np.polyfit(x, data, 1)

            # Simple weekly seasonality (if enough data)
            weekly_pattern = np.zeros(7)
            if len(data) >= 14:
                for i in range(7):
                    weekly_pattern[i] = np.mean(data[i::7]) - np.mean(data)

            # Generate predictions
            predictions = []
            lower_bounds = []
            upper_bounds = []
            dates = []

            start_date = datetime.now()
            volatility = np.std(data[-14:]) if len(data) >= 14 else np.std(data)

            for i in range(periods):
                future_x = len(data) + i
                trend_value = slope * future_x + intercept
                seasonal_value = weekly_pattern[i % 7] if len(data) >= 14 else 0
                pred = trend_value + seasonal_value

                predictions.append(float(pred))
                lower_bounds.append(float(pred - 1.96 * volatility))
                upper_bounds.append(float(pred + 1.96 * volatility))
                dates.append((start_date + timedelta(days=i)).strftime('%Y-%m-%d'))

            # Determine trend
            if slope > 0.001 * np.mean(data):
                trend = 'increasing'
            elif slope < -0.001 * np.mean(data):
                trend = 'decreasing'
            else:
                trend = 'stable'

            return ProphetPrediction(
                success=True,
                predictions=predictions,
                lower_bounds=lower_bounds,
                upper_bounds=upper_bounds,
                dates=dates,
                trend=trend,
                trend_slope=float(slope),
                seasonality={'weekly': float(np.std(weekly_pattern)) if len(data) >= 14 else 0},
                changepoints=[],
                confidence=0.4,  # Lower for fallback
                metadata={
                    'fallback_mode': True,
                    'method': 'linear_trend_with_weekly_seasonality',
                }
            )

        except Exception as e:
            logger.error(f"Fallback prediction failed: {e}")
            return ProphetPrediction(success=False, error=str(e))

    def get_components(self) -> Optional[Dict[str, Any]]:
        """Get decomposed components (trend, seasonality) from last fit."""
        if not self.is_trained or self._last_training_data is None:
            return None

        try:
            forecast = self.model.predict(self._last_training_data)
            return {
                'trend': forecast['trend'].tolist(),
                'weekly': forecast['weekly'].tolist() if 'weekly' in forecast else None,
                'yearly': forecast['yearly'].tolist() if 'yearly' in forecast else None,
            }
        except Exception as e:
            logger.error(f"Failed to get components: {e}")
            return None

    def save(self, path: str = None) -> bool:
        """Save model to disk."""
        if not JOBLIB_AVAILABLE:
            logger.warning("Joblib not available, cannot save model")
            return False

        try:
            save_path = Path(path) if path else self.model_dir / f"{self.model_name}"

            # Prophet models can be pickled directly
            if self.model is not None:
                joblib.dump(self.model, f"{save_path}_model.joblib")

            # Save config
            joblib.dump({
                'config': self.config,
                'is_trained': self._is_trained,
                'model_name': self.model_name,
            }, f"{save_path}_meta.joblib")

            logger.info(f"Saved Prophet model to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False

    def load(self, path: str = None) -> bool:
        """Load model from disk."""
        if not JOBLIB_AVAILABLE:
            return False

        try:
            load_path = Path(path) if path else self.model_dir / f"{self.model_name}"

            # Load metadata
            meta_path = f"{load_path}_meta.joblib"
            if os.path.exists(meta_path):
                meta = joblib.load(meta_path)
                self.config = meta.get('config', self.config)
                self._is_trained = meta.get('is_trained', False)

            # Load model
            model_path = f"{load_path}_model.joblib"
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                self._is_trained = True

            logger.info(f"Loaded Prophet model from {load_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


class suppress_stdout_stderr:
    """Context manager to suppress Prophet's verbose output."""
    def __init__(self):
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for _ in range(2)]
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        for fd in self.null_fds + self.save_fds:
            os.close(fd)


# Singleton instance
_prophet_model = None


def get_prophet_model(model_name: str = "prophet_forecaster") -> ProphetForecaster:
    """Get or create the Prophet model singleton."""
    global _prophet_model
    if _prophet_model is None or _prophet_model.model_name != model_name:
        _prophet_model = ProphetForecaster(model_name=model_name)
        _prophet_model.load()
    return _prophet_model
