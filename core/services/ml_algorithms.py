"""
ML Algorithm Integration for E-Commerce Projects

This module provides ML algorithm implementations that can be deployed
to e-commerce projects by specialized ML agents.

Session 728: Migrated from agents/ml_algorithms.py to core/services/
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any
from datetime import timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics.pairwise import cosine_similarity


import logging
logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    Collaborative and content-based recommendation system for e-commerce
    """

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.user_item_matrix = None
        self.product_features = None
        self.similarity_matrix = None

    def collaborative_filtering(
        self,
        user_interactions: pd.DataFrame,
        user_id: int,
        n_recommendations: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations using collaborative filtering

        Args:
            user_interactions: DataFrame with columns [user_id, product_id, rating]
            user_id: Target user for recommendations
            n_recommendations: Number of recommendations to generate

        Returns:
            List of recommended products with scores
        """
        # Create user-item matrix
        self.user_item_matrix = user_interactions.pivot_table(
            index='user_id',
            columns='product_id',
            values='rating',
            fill_value=0
        )

        # Calculate user similarities
        user_similarities = cosine_similarity(self.user_item_matrix)
        user_sim_df = pd.DataFrame(
            user_similarities,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
        )

        # Find similar users
        similar_users = user_sim_df[user_id].sort_values(ascending=False)[1:11]

        # Get products liked by similar users
        recommendations = []
        for similar_user, similarity_score in similar_users.items():
            user_products = self.user_item_matrix.loc[similar_user]
            liked_products = user_products[user_products > 3].index

            for product_id in liked_products:
                if self.user_item_matrix.loc[user_id, product_id] == 0:
                    recommendations.append({
                        'product_id': int(product_id),
                        'score': float(similarity_score * user_products[product_id]),
                        'reason': 'collaborative_filtering',
                        'similar_user': int(similar_user)
                    })

        # Sort and deduplicate
        recommendations = sorted(recommendations, key=lambda x: x['score'], reverse=True)
        seen_products = set()
        unique_recommendations = []

        for rec in recommendations:
            if rec['product_id'] not in seen_products:
                seen_products.add(rec['product_id'])
                unique_recommendations.append(rec)
                if len(unique_recommendations) >= n_recommendations:
                    break

        return unique_recommendations

    def content_based_filtering(
        self,
        product_features: pd.DataFrame,
        user_history: List[int],
        n_recommendations: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on product features

        Args:
            product_features: DataFrame with product features
            user_history: List of product IDs the user has interacted with
            n_recommendations: Number of recommendations

        Returns:
            List of recommended products with scores
        """
        self.product_features = product_features

        # Calculate product similarity matrix
        feature_columns = [col for col in product_features.columns if col != 'product_id']
        feature_matrix = product_features[feature_columns].values
        self.similarity_matrix = cosine_similarity(feature_matrix)

        # Get user's product profile
        user_indices = [
            product_features[product_features['product_id'] == pid].index[0]
            for pid in user_history
            if pid in product_features['product_id'].values
        ]

        if not user_indices:
            return []

        # Calculate average similarity scores
        avg_similarities = np.mean([self.similarity_matrix[idx] for idx in user_indices], axis=0)

        # Get recommendations
        recommendations = []
        for idx, score in enumerate(avg_similarities):
            product_id = int(product_features.iloc[idx]['product_id'])
            if product_id not in user_history and score > 0.5:
                recommendations.append({
                    'product_id': product_id,
                    'score': float(score),
                    'reason': 'content_based',
                    'similarity_threshold': 0.5
                })

        return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:n_recommendations]


class DynamicPricingOptimizer:
    """
    Dynamic pricing optimization using ML for e-commerce
    """

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.pricing_model = None
        self.scaler = StandardScaler()

    def train_pricing_model(
        self,
        historical_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Train a dynamic pricing model

        Args:
            historical_data: DataFrame with columns [product_id, price, demand,
                           competitor_price, season, day_of_week, inventory]

        Returns:
            Model training results
        """
        # Prepare features
        feature_columns = ['competitor_price', 'season', 'day_of_week', 'inventory']
        X = historical_data[feature_columns]
        y = historical_data['demand']

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.pricing_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.pricing_model.fit(X_scaled, y)

        # Calculate feature importance
        feature_importance = dict(zip(
            feature_columns,
            self.pricing_model.feature_importances_
        ))

        return {
            'model_type': 'RandomForestRegressor',
            'n_samples_trained': len(historical_data),
            'feature_importance': feature_importance,
            'training_score': float(self.pricing_model.score(X_scaled, y))
        }

    def optimize_price(
        self,
        product_id: int,
        current_price: float,
        competitor_price: float,
        inventory_level: int,
        season: int,
        day_of_week: int,
        price_elasticity: float = -1.5
    ) -> Dict[str, Any]:
        """
        Optimize price for a product

        Args:
            product_id: Product identifier
            current_price: Current product price
            competitor_price: Competitor's price
            inventory_level: Current inventory
            season: Season indicator (0-3)
            day_of_week: Day of week (0-6)
            price_elasticity: Price elasticity of demand

        Returns:
            Optimized pricing recommendation
        """
        # Test different price points
        price_points = np.linspace(
            current_price * 0.8,
            current_price * 1.2,
            20
        )

        optimal_price = current_price
        max_revenue = 0

        for test_price in price_points:
            # Prepare features
            features = np.array([[
                competitor_price,
                season,
                day_of_week,
                inventory_level
            ]])
            features_scaled = self.scaler.transform(features)

            # Predict demand
            predicted_demand = self.pricing_model.predict(features_scaled)[0]

            # Adjust demand based on price change
            price_change_ratio = (test_price - current_price) / current_price
            adjusted_demand = predicted_demand * (1 + price_elasticity * price_change_ratio)

            # Calculate expected revenue
            expected_revenue = test_price * max(0, adjusted_demand)

            if expected_revenue > max_revenue:
                max_revenue = expected_revenue
                optimal_price = test_price

        return {
            'product_id': product_id,
            'current_price': current_price,
            'recommended_price': float(optimal_price),
            'expected_revenue_increase': float((max_revenue - current_price * predicted_demand) / (current_price * predicted_demand)),
            'price_change_percentage': float((optimal_price - current_price) / current_price * 100),
            'factors_considered': {
                'competitor_price': competitor_price,
                'inventory_level': inventory_level,
                'season': season,
                'day_of_week': day_of_week
            }
        }


class CustomerSegmentation:
    """
    Customer segmentation using clustering algorithms
    """

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.clustering_model = None
        self.scaler = StandardScaler()
        self.segment_profiles = {}

    def segment_customers(
        self,
        customer_data: pd.DataFrame,
        n_segments: int = 5
    ) -> Dict[str, Any]:
        """
        Segment customers using K-means clustering

        Args:
            customer_data: DataFrame with customer features
            n_segments: Number of customer segments

        Returns:
            Segmentation results
        """
        # Select features for clustering
        feature_columns = [
            'total_purchases', 'average_order_value', 'frequency',
            'recency_days', 'customer_lifetime_value'
        ]

        # Ensure all required columns exist
        available_features = [col for col in feature_columns if col in customer_data.columns]
        X = customer_data[available_features]

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Perform clustering
        self.clustering_model = KMeans(
            n_clusters=n_segments,
            random_state=42,
            n_init=10
        )
        segments = self.clustering_model.fit_predict(X_scaled)

        # Add segments to dataframe
        customer_data['segment'] = segments

        # Profile each segment
        for segment_id in range(n_segments):
            segment_customers = customer_data[customer_data['segment'] == segment_id]

            self.segment_profiles[segment_id] = {
                'size': len(segment_customers),
                'percentage': float(len(segment_customers) / len(customer_data) * 100),
                'avg_purchases': float(segment_customers['total_purchases'].mean()),
                'avg_order_value': float(segment_customers['average_order_value'].mean()),
                'avg_lifetime_value': float(segment_customers.get('customer_lifetime_value', 0).mean()),
                'characteristics': self._describe_segment(segment_customers, available_features)
            }

        return {
            'n_segments': n_segments,
            'segment_profiles': self.segment_profiles,
            'features_used': available_features,
            'silhouette_score': self._calculate_silhouette_score(X_scaled, segments)
        }

    def _describe_segment(self, segment_data: pd.DataFrame, features: List[str]) -> str:
        """Generate human-readable segment description"""
        descriptions = []

        if 'total_purchases' in features:
            avg_purchases = segment_data['total_purchases'].mean()
            if avg_purchases > 10:
                descriptions.append("High frequency buyers")
            elif avg_purchases > 5:
                descriptions.append("Regular customers")
            else:
                descriptions.append("Occasional shoppers")

        if 'average_order_value' in features:
            avg_order = segment_data['average_order_value'].mean()
            if avg_order > 200:
                descriptions.append("premium spenders")
            elif avg_order > 50:
                descriptions.append("moderate spenders")
            else:
                descriptions.append("budget conscious")

        return ", ".join(descriptions) if descriptions else "Standard customers"

    def _calculate_silhouette_score(self, X: np.ndarray, labels: np.ndarray) -> float:
        """Calculate silhouette score for clustering quality"""
        from sklearn.metrics import silhouette_score
        try:
            return float(silhouette_score(X, labels))
        except Exception as _e:
            logger.warning(
                "ml_algorithms._calculate_silhouette_score: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0.0


class InventoryPredictor:
    """
    Demand forecasting and inventory optimization
    """

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.forecasting_model = None

    def forecast_demand(
        self,
        historical_sales: pd.DataFrame,
        product_id: int,
        forecast_days: int = 30
    ) -> Dict[str, Any]:
        """
        Forecast product demand

        Args:
            historical_sales: DataFrame with columns [date, product_id, quantity]
            product_id: Product to forecast
            forecast_days: Number of days to forecast

        Returns:
            Demand forecast
        """
        # Filter for specific product
        product_sales = historical_sales[
            historical_sales['product_id'] == product_id
        ].copy()

        # Add time features
        product_sales['date'] = pd.to_datetime(product_sales['date'])
        product_sales['day_of_week'] = product_sales['date'].dt.dayofweek
        product_sales['month'] = product_sales['date'].dt.month
        product_sales['day_of_month'] = product_sales['date'].dt.day

        # Prepare features
        feature_columns = ['day_of_week', 'month', 'day_of_month']
        X = product_sales[feature_columns]
        y = product_sales['quantity']

        # Train model
        self.forecasting_model = RandomForestRegressor(
            n_estimators=50,
            random_state=42
        )
        self.forecasting_model.fit(X, y)

        # Generate forecast
        forecast_dates = pd.date_range(
            start=product_sales['date'].max() + timedelta(days=1),
            periods=forecast_days
        )

        forecast_features = pd.DataFrame({
            'day_of_week': forecast_dates.dayofweek,
            'month': forecast_dates.month,
            'day_of_month': forecast_dates.day
        })

        predictions = self.forecasting_model.predict(forecast_features)

        return {
            'product_id': product_id,
            'forecast_period': forecast_days,
            'predictions': [
                {
                    'date': date.isoformat(),
                    'predicted_quantity': float(pred)
                }
                for date, pred in zip(forecast_dates, predictions)
            ],
            'total_predicted_demand': float(predictions.sum()),
            'avg_daily_demand': float(predictions.mean()),
            'peak_demand_day': forecast_dates[predictions.argmax()].isoformat()
        }

    def optimize_reorder_point(
        self,
        product_id: int,
        lead_time_days: int,
        service_level: float = 0.95,
        historical_demand: List[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate optimal reorder point

        Args:
            product_id: Product identifier
            lead_time_days: Lead time for orders
            service_level: Desired service level (0-1)
            historical_demand: Historical demand data

        Returns:
            Reorder point recommendation
        """
        if not historical_demand:
            historical_demand = np.random.poisson(10, 100)  # Placeholder

        # Calculate demand statistics
        avg_demand = np.mean(historical_demand)
        std_demand = np.std(historical_demand)

        # Calculate safety stock (assuming normal distribution)
        from scipy import stats
        z_score = stats.norm.ppf(service_level)
        safety_stock = z_score * std_demand * np.sqrt(lead_time_days)

        # Calculate reorder point
        reorder_point = (avg_demand * lead_time_days) + safety_stock

        return {
            'product_id': product_id,
            'reorder_point': float(reorder_point),
            'safety_stock': float(safety_stock),
            'avg_daily_demand': float(avg_demand),
            'lead_time_demand': float(avg_demand * lead_time_days),
            'service_level': service_level,
            'lead_time_days': lead_time_days
        }


class FraudDetector:
    """
    Fraud detection for e-commerce transactions
    """

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.fraud_model = None
        self.scaler = StandardScaler()

    def train_fraud_detector(
        self,
        transaction_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Train fraud detection model

        Args:
            transaction_data: DataFrame with transaction features

        Returns:
            Training results
        """
        # Select features
        feature_columns = [
            'amount', 'user_age_days', 'daily_transaction_count',
            'unusual_time', 'new_shipping_address', 'high_risk_country'
        ]

        # Ensure columns exist
        available_features = [col for col in feature_columns if col in transaction_data.columns]
        X = transaction_data[available_features]

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train Isolation Forest for anomaly detection
        self.fraud_model = IsolationForest(
            contamination=0.01,  # Expect 1% fraud
            random_state=42
        )
        self.fraud_model.fit(X_scaled)

        return {
            'model_type': 'IsolationForest',
            'features_used': available_features,
            'n_samples_trained': len(transaction_data),
            'expected_fraud_rate': 0.01
        }

    def detect_fraud(
        self,
        transaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect if a transaction is fraudulent

        Args:
            transaction: Transaction details

        Returns:
            Fraud detection result
        """
        # Extract features
        features = np.array([[
            transaction.get('amount', 0),
            transaction.get('user_age_days', 365),
            transaction.get('daily_transaction_count', 1),
            1 if transaction.get('unusual_time', False) else 0,
            1 if transaction.get('new_shipping_address', False) else 0,
            1 if transaction.get('high_risk_country', False) else 0
        ]])

        # Scale features
        features_scaled = self.scaler.transform(features)

        # Predict
        prediction = self.fraud_model.predict(features_scaled)[0]
        anomaly_score = self.fraud_model.score_samples(features_scaled)[0]

        # Determine risk level
        if prediction == -1:  # Anomaly detected
            if anomaly_score < -0.5:
                risk_level = 'high'
            else:
                risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'transaction_id': transaction.get('id', 'unknown'),
            'is_fraudulent': prediction == -1,
            'risk_level': risk_level,
            'anomaly_score': float(anomaly_score),
            'risk_factors': self._identify_risk_factors(transaction),
            'recommended_action': 'block' if risk_level == 'high' else ('review' if risk_level == 'medium' else 'approve')
        }

    def _identify_risk_factors(self, transaction: Dict[str, Any]) -> List[str]:
        """Identify specific risk factors in transaction"""
        risk_factors = []

        if transaction.get('amount', 0) > 1000:
            risk_factors.append('High transaction amount')
        if transaction.get('new_shipping_address', False):
            risk_factors.append('New shipping address')
        if transaction.get('high_risk_country', False):
            risk_factors.append('High risk country')
        if transaction.get('unusual_time', False):
            risk_factors.append('Unusual transaction time')
        if transaction.get('daily_transaction_count', 0) > 5:
            risk_factors.append('Multiple transactions today')

        return risk_factors
