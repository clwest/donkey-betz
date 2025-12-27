"""
Kalshi Prediction Markets Service
==================================

Session 558: Complete Kalshi API integration with RSA-PSS authentication.

This service provides:
- RSA-PSS signed authentication for protected endpoints
- Portfolio management (balance, positions, orders)
- Market data with analysis and enrichment
- Trading operations (place/cancel orders)

Authentication:
- Uses RSA-PSS with SHA-256 for request signing
- Requires KALSHI_API_KEY and KALSHI_PRIVATE_KEY environment variables
- Tokens refresh automatically

API Reference: https://docs.kalshi.com/
"""

import os
import base64
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class KalshiService:
    """
    Service for authenticated Kalshi API operations.

    Provides full access to Kalshi's prediction market platform including:
    - Portfolio management (balance, positions, fills)
    - Order management (place, cancel, amend)
    - Enhanced market data with orderbook depth
    - Trading analytics and history
    """

    # API Endpoints
    PROD_URL = "https://api.elections.kalshi.com/trade-api/v2"
    DEMO_URL = "https://demo-api.kalshi.co/trade-api/v2"

    def __init__(self, use_demo: bool = False):
        """
        Initialize Kalshi service.

        Args:
            use_demo: If True, use demo API for testing
        """
        self.base_url = self.DEMO_URL if use_demo else self.PROD_URL
        self.use_demo = use_demo

        # Load credentials from environment
        self.api_key = os.getenv('KALSHI_API_KEY', '')
        self.private_key_pem = os.getenv('KALSHI_PRIVATE_KEY', '')

        # Parse private key if provided
        self.private_key = None
        if self.private_key_pem:
            self._load_private_key()

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

        # Cache for rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms between requests

        logger.info(f"KalshiService initialized ({'DEMO' if use_demo else 'PROD'} mode)")

    def _load_private_key(self):
        """Load RSA private key from PEM string."""
        try:
            # Handle both file path and direct PEM content
            if self.private_key_pem.startswith('-----BEGIN'):
                key_data = self.private_key_pem.encode('utf-8')
            elif os.path.exists(self.private_key_pem):
                with open(self.private_key_pem, 'rb') as f:
                    key_data = f.read()
            else:
                # Assume it's base64 encoded PEM
                key_data = base64.b64decode(self.private_key_pem)

            self.private_key = serialization.load_pem_private_key(
                key_data,
                password=None,
                backend=default_backend()
            )
            logger.info("Kalshi private key loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load Kalshi private key: {e}")
            self.private_key = None

    def _sign_request(self, timestamp_ms: int, method: str, path: str) -> str:
        """
        Sign a request using RSA-PSS.

        Args:
            timestamp_ms: Request timestamp in milliseconds
            method: HTTP method (GET, POST, etc.)
            path: Request path (without query params)

        Returns:
            Base64-encoded signature
        """
        if not self.private_key:
            raise ValueError("Private key not loaded - cannot sign request")

        # Build message: timestamp + method + path (no query params)
        message = f"{timestamp_ms}{method}{path}"
        message_bytes = message.encode('utf-8')

        # Sign with RSA-PSS
        signature = self.private_key.sign(
            message_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return base64.b64encode(signature).decode('utf-8')

    def _get_auth_headers(self, method: str, path: str) -> Dict[str, str]:
        """
        Generate authentication headers for a request.

        Args:
            method: HTTP method
            path: Request path (will strip query params for signing)

        Returns:
            Dict of authentication headers
        """
        if not self.api_key or not self.private_key:
            return {}

        # Current timestamp in milliseconds
        timestamp_ms = int(datetime.now().timestamp() * 1000)

        # Strip query parameters from path for signing
        path_clean = path.split('?')[0]

        # Generate signature
        signature = self._sign_request(timestamp_ms, method, path_clean)

        return {
            'KALSHI-ACCESS-KEY': self.api_key,
            'KALSHI-ACCESS-TIMESTAMP': str(timestamp_ms),
            'KALSHI-ACCESS-SIGNATURE': signature,
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        data: Dict = None,
        auth_required: bool = True
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the Kalshi API.

        Args:
            method: HTTP method
            endpoint: API endpoint (e.g., '/portfolio/balance')
            params: Query parameters
            data: Request body data
            auth_required: Whether authentication is required

        Returns:
            Response JSON or error dict
        """
        url = f"{self.base_url}{endpoint}"
        path = f"/trade-api/v2{endpoint}"

        # Add auth headers if required
        headers = {}
        if auth_required:
            if not self.api_key or not self.private_key:
                return {
                    'error': 'Authentication not configured',
                    'message': 'Set KALSHI_API_KEY and KALSHI_PRIVATE_KEY environment variables'
                }
            headers = self._get_auth_headers(method, path)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=30
            )

            # Check for errors
            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                logger.error(f"Kalshi API error {response.status_code}: {error_data}")
                return {
                    'error': f"API Error {response.status_code}",
                    'message': error_data.get('error', {}).get('message', 'Unknown error'),
                    'code': error_data.get('error', {}).get('code'),
                }

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Kalshi request failed: {e}")
            return {'error': 'Request failed', 'message': str(e)}

    # ==================== Portfolio Endpoints ====================

    def get_balance(self) -> Dict[str, Any]:
        """Get account balance."""
        response = self._make_request('GET', '/portfolio/balance')

        if 'error' not in response:
            balance = response.get('balance', 0)
            # Balance is in cents
            response['balance_dollars'] = balance / 100
            logger.info(f"Kalshi balance: ${response['balance_dollars']:.2f}")

        return response

    def get_positions(self) -> Dict[str, Any]:
        """Get current positions."""
        response = self._make_request('GET', '/portfolio/positions')

        if 'error' not in response:
            positions = response.get('market_positions', [])
            logger.info(f"Kalshi positions: {len(positions)} markets")

            # Enrich positions with market data
            enriched = []
            for pos in positions:
                enriched.append({
                    'ticker': pos.get('ticker'),
                    'position': pos.get('position'),  # Positive = YES, Negative = NO
                    'market_exposure': pos.get('market_exposure'),
                    'realized_pnl': pos.get('realized_pnl', 0) / 100,  # Convert to dollars
                    'resting_orders_count': pos.get('resting_orders_count'),
                })
            response['positions_enriched'] = enriched

        return response

    def get_fills(self, limit: int = 100) -> Dict[str, Any]:
        """Get trade execution history."""
        response = self._make_request('GET', '/portfolio/fills', params={'limit': limit})

        if 'error' not in response:
            fills = response.get('fills', [])
            logger.info(f"Kalshi fills: {len(fills)} trades")

        return response

    def get_orders(self, status: str = None) -> Dict[str, Any]:
        """
        Get orders.

        Args:
            status: Filter by status ('resting', 'canceled', 'executed')
        """
        params = {}
        if status:
            params['status'] = status

        response = self._make_request('GET', '/portfolio/orders', params=params)

        if 'error' not in response:
            orders = response.get('orders', [])
            logger.info(f"Kalshi orders: {len(orders)}")

        return response

    # ==================== Order Management ====================

    def place_order(
        self,
        ticker: str,
        side: str,
        count: int,
        type: str = 'limit',
        yes_price: int = None,
        no_price: int = None,
        expiration_ts: int = None
    ) -> Dict[str, Any]:
        """
        Place an order.

        Args:
            ticker: Market ticker
            side: 'yes' or 'no'
            count: Number of contracts
            type: 'limit' or 'market'
            yes_price: Price for YES side (1-99 cents)
            no_price: Price for NO side (1-99 cents)
            expiration_ts: Order expiration timestamp (optional)

        Returns:
            Order response
        """
        order_data = {
            'ticker': ticker,
            'side': side,
            'count': count,
            'type': type,
            'action': 'buy',
        }

        if yes_price is not None:
            order_data['yes_price'] = yes_price
        if no_price is not None:
            order_data['no_price'] = no_price
        if expiration_ts is not None:
            order_data['expiration_ts'] = expiration_ts

        response = self._make_request('POST', '/portfolio/orders', data=order_data)

        if 'error' not in response:
            order = response.get('order', {})
            logger.info(f"Order placed: {order.get('order_id')} - {ticker} {side} x{count}")

        return response

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order."""
        response = self._make_request('DELETE', f'/portfolio/orders/{order_id}')

        if 'error' not in response:
            logger.info(f"Order canceled: {order_id}")

        return response

    def cancel_all_orders(self) -> Dict[str, Any]:
        """Cancel all resting orders."""
        # Get all resting orders
        orders_response = self.get_orders(status='resting')
        if 'error' in orders_response:
            return orders_response

        orders = orders_response.get('orders', [])
        canceled = []
        failed = []

        for order in orders:
            order_id = order.get('order_id')
            result = self.cancel_order(order_id)
            if 'error' in result:
                failed.append({'order_id': order_id, 'error': result.get('message')})
            else:
                canceled.append(order_id)

        return {
            'canceled': canceled,
            'failed': failed,
            'total_canceled': len(canceled),
            'total_failed': len(failed),
        }

    # ==================== Market Data (Enhanced) ====================

    def get_market_with_orderbook(self, ticker: str) -> Dict[str, Any]:
        """Get market data with full orderbook depth."""
        # Get market details
        market_response = self._make_request('GET', f'/markets/{ticker}', auth_required=False)

        if 'error' in market_response:
            return market_response

        # Get orderbook
        orderbook_response = self._make_request(
            'GET', f'/markets/{ticker}/orderbook', auth_required=False
        )

        market = market_response.get('market', {})
        orderbook = orderbook_response.get('orderbook', {})

        # Orderbook format is [[price, count], ...]
        yes_bids = orderbook.get('yes', [])
        no_bids = orderbook.get('no', [])

        # Best prices (first element, price is index 0)
        best_yes_bid = yes_bids[0][0] if yes_bids else None
        best_no_bid = no_bids[0][0] if no_bids else None

        # Spread calculation
        spread = None
        if best_yes_bid and best_no_bid:
            # YES bid + NO bid should sum close to 100 in a liquid market
            spread = 100 - best_yes_bid - best_no_bid

        return {
            'market': market,
            'orderbook': orderbook,
            'analysis': {
                'best_yes_bid': best_yes_bid,
                'best_no_bid': best_no_bid,
                'spread': spread,
                'yes_depth': sum(b[1] for b in yes_bids) if yes_bids else 0,
                'no_depth': sum(b[1] for b in no_bids) if no_bids else 0,
                'liquidity_score': self._calculate_liquidity_score(yes_bids, no_bids),
            },
            'timestamp': datetime.now().isoformat(),
        }

    def _calculate_liquidity_score(self, yes_bids: List, no_bids: List) -> str:
        """Calculate liquidity score based on orderbook depth."""
        # Orderbook format is [[price, count], ...]
        total_depth = sum(b[1] for b in yes_bids) + sum(b[1] for b in no_bids)

        if total_depth > 10000:
            return 'VERY_HIGH'
        elif total_depth > 1000:
            return 'HIGH'
        elif total_depth > 100:
            return 'MODERATE'
        elif total_depth > 10:
            return 'LOW'
        else:
            return 'VERY_LOW'

    # ==================== Analytics ====================

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get comprehensive portfolio summary."""
        balance = self.get_balance()
        positions = self.get_positions()
        orders = self.get_orders(status='resting')

        if 'error' in balance:
            return balance

        summary = {
            'balance': balance.get('balance_dollars', 0),
            'portfolio_value': balance.get('portfolio_value', 0) / 100 if balance.get('portfolio_value') else 0,
            'total_positions': len(positions.get('market_positions', [])),
            'resting_orders': len(orders.get('orders', [])),
            'positions': positions.get('positions_enriched', []),
            'timestamp': datetime.now().isoformat(),
        }

        # Calculate total exposure
        total_exposure = sum(
            abs(p.get('market_exposure', 0))
            for p in positions.get('market_positions', [])
        )
        summary['total_exposure'] = total_exposure / 100  # Convert to dollars

        # Calculate total unrealized P&L
        total_realized_pnl = sum(
            p.get('realized_pnl', 0)
            for p in summary['positions']
        )
        summary['total_realized_pnl'] = total_realized_pnl

        logger.info(f"Portfolio summary: ${summary['balance']:.2f} balance, "
                   f"{summary['total_positions']} positions")

        return summary

    def get_market_intelligence(self, categories: List[str] = None) -> Dict[str, Any]:
        """
        Get market intelligence summary for specified categories.

        Args:
            categories: List of categories to analyze

        Returns:
            Intelligence summary with trending markets and opportunities
        """
        from ai_core.spiders.specialized.kalshi_spider import KalshiSpider

        spider = KalshiSpider()
        markets = spider.fetch_data(max_results=200)

        # Filter to active markets only
        active_markets = [m for m in markets if m.get('data_type') == 'prediction_market']

        # Filter by category if specified
        if categories:
            active_markets = [
                m for m in active_markets
                if m.get('category') in categories
            ]

        # Sort by volume
        by_volume = sorted(
            active_markets,
            key=lambda m: m.get('volume', 0) or 0,
            reverse=True
        )[:10]

        # Find high-probability markets (>80%)
        high_prob = [
            m for m in active_markets
            if m.get('implied_probability_pct', 50) > 80
        ][:10]

        # Find low-probability markets (<20%)
        low_prob = [
            m for m in active_markets
            if m.get('implied_probability_pct', 50) < 20
        ][:10]

        # Find uncertain markets (40-60%)
        uncertain = [
            m for m in active_markets
            if 40 <= m.get('implied_probability_pct', 50) <= 60
        ][:10]

        # Category breakdown
        category_counts = {}
        for m in active_markets:
            cat = m.get('category', 'unknown')
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            'total_markets': len(active_markets),
            'trending_by_volume': by_volume,
            'high_probability': high_prob,
            'low_probability': low_prob,
            'uncertain': uncertain,
            'categories': category_counts,
            'timestamp': datetime.now().isoformat(),
        }

    # ==================== Health Check ====================

    def check_connection(self) -> Dict[str, Any]:
        """Check API connection and authentication status."""
        # Check public endpoint
        public_check = self._make_request('GET', '/exchange/status', auth_required=False)

        result = {
            'public_api': 'error' not in public_check,
            'exchange_status': public_check.get('exchange_active', False),
            'mode': 'DEMO' if self.use_demo else 'PROD',
            'api_key_configured': bool(self.api_key),
            'private_key_loaded': self.private_key is not None,
        }

        # Check authenticated endpoint if configured
        if self.api_key and self.private_key:
            auth_check = self.get_balance()
            result['authenticated'] = 'error' not in auth_check
            if 'error' in auth_check:
                result['auth_error'] = auth_check.get('message')
        else:
            result['authenticated'] = False
            result['auth_error'] = 'Credentials not configured'

        return result


# Global instance
_kalshi_service = None


def get_kalshi_service(use_demo: bool = False) -> KalshiService:
    """Get or create the global KalshiService instance."""
    global _kalshi_service
    if _kalshi_service is None or _kalshi_service.use_demo != use_demo:
        _kalshi_service = KalshiService(use_demo=use_demo)
    return _kalshi_service
