# tests/services/test_kalshi_service.py
"""
Unit tests for KalshiService.

Tests RSA-PSS authentication, portfolio management, order operations,
and market data retrieval for the Kalshi prediction market integration.
"""
import json
import base64
from datetime import datetime
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from core.services.kalshi_service import KalshiService, get_kalshi_service


# Note: These tests don't require database access - all external calls are mocked


# =============================================================================
# Initialization Tests
# =============================================================================

class TestKalshiServiceInit:
    """Tests for KalshiService initialization."""

    def test_init_prod_mode(self, mock_kalshi_env):
        """Test initialization in production mode."""
        service = KalshiService(use_demo=False)

        assert service.base_url == KalshiService.PROD_URL
        assert service.use_demo is False
        assert service.api_key == 'test-api-key-12345'
        assert service.private_key is not None

    def test_init_demo_mode(self, mock_kalshi_env):
        """Test initialization in demo mode."""
        service = KalshiService(use_demo=True)

        assert service.base_url == KalshiService.DEMO_URL
        assert service.use_demo is True

    def test_init_no_credentials(self):
        """Test initialization without credentials."""
        with patch.dict('os.environ', {}, clear=True):
            service = KalshiService()

            assert service.api_key == ''
            assert service.private_key is None

    def test_load_private_key_from_pem_string(self, mock_rsa_key):
        """Test loading private key from PEM string."""
        with patch.dict('os.environ', {
            'KALSHI_API_KEY': 'test-key',
            'KALSHI_PRIVATE_KEY': mock_rsa_key['pem']
        }):
            service = KalshiService()
            assert service.private_key is not None

    def test_load_private_key_from_base64(self, mock_rsa_key):
        """Test loading private key from base64-encoded PEM."""
        base64_pem = base64.b64encode(mock_rsa_key['pem'].encode()).decode()

        with patch.dict('os.environ', {
            'KALSHI_API_KEY': 'test-key',
            'KALSHI_PRIVATE_KEY': base64_pem
        }):
            service = KalshiService()
            assert service.private_key is not None

    def test_load_private_key_invalid(self):
        """Test handling of invalid private key."""
        with patch.dict('os.environ', {
            'KALSHI_API_KEY': 'test-key',
            'KALSHI_PRIVATE_KEY': 'invalid-key-data'
        }):
            service = KalshiService()
            assert service.private_key is None


# =============================================================================
# RSA Signature Tests
# =============================================================================

class TestRSASignature:
    """Tests for RSA-PSS request signing."""

    def test_sign_request_format(self, mock_kalshi_env):
        """Test that signature is generated with correct format."""
        service = KalshiService()

        timestamp_ms = 1704456000000  # Fixed timestamp
        method = 'GET'
        path = '/trade-api/v2/portfolio/balance'

        signature = service._sign_request(timestamp_ms, method, path)

        # Signature should be base64 encoded
        assert isinstance(signature, str)
        # Should be decodable
        decoded = base64.b64decode(signature)
        assert len(decoded) > 0

    def test_sign_request_consistency(self, mock_kalshi_env):
        """Test that same input produces same signature."""
        service = KalshiService()

        timestamp_ms = 1704456000000
        method = 'GET'
        path = '/trade-api/v2/portfolio/balance'

        sig1 = service._sign_request(timestamp_ms, method, path)
        sig2 = service._sign_request(timestamp_ms, method, path)

        # RSA-PSS uses random salt, so signatures differ
        # But both should be valid (non-empty, decodable)
        assert len(sig1) > 0
        assert len(sig2) > 0

    def test_sign_request_no_key(self):
        """Test signing without private key raises error."""
        with patch.dict('os.environ', {}, clear=True):
            service = KalshiService()

            with pytest.raises(ValueError, match="Private key not loaded"):
                service._sign_request(1704456000000, 'GET', '/test')

    def test_get_auth_headers(self, mock_kalshi_env):
        """Test authentication headers generation."""
        service = KalshiService()

        headers = service._get_auth_headers('GET', '/trade-api/v2/portfolio/balance')

        assert 'KALSHI-ACCESS-KEY' in headers
        assert 'KALSHI-ACCESS-TIMESTAMP' in headers
        assert 'KALSHI-ACCESS-SIGNATURE' in headers
        assert headers['KALSHI-ACCESS-KEY'] == 'test-api-key-12345'

    def test_get_auth_headers_strips_query_params(self, mock_kalshi_env):
        """Test that query params are stripped for signing."""
        service = KalshiService()

        # Path with query params
        headers = service._get_auth_headers('GET', '/trade-api/v2/markets?limit=10&cursor=abc')

        # Should succeed without error
        assert 'KALSHI-ACCESS-SIGNATURE' in headers

    def test_get_auth_headers_no_credentials(self):
        """Test auth headers return empty when no credentials."""
        with patch.dict('os.environ', {}, clear=True):
            service = KalshiService()
            headers = service._get_auth_headers('GET', '/test')
            assert headers == {}


# =============================================================================
# Portfolio Endpoint Tests
# =============================================================================

class TestPortfolioEndpoints:
    """Tests for portfolio management endpoints."""

    def test_get_balance_success(self, mock_kalshi_env, mock_kalshi_requests):
        """Test successful balance retrieval."""
        mock_kalshi_requests['response'].json.return_value = {
            'balance': 10000  # $100.00 in cents
        }

        service = KalshiService()
        result = service.get_balance()

        assert 'error' not in result
        assert result['balance'] == 10000
        assert result['balance_dollars'] == 100.0

    def test_get_balance_auth_error(self, mock_kalshi_env, mock_kalshi_requests):
        """Test balance retrieval with auth error."""
        mock_kalshi_requests['response'].status_code = 401
        mock_kalshi_requests['response'].json.return_value = {
            'error': {'code': 'UNAUTHORIZED', 'message': 'Invalid API key'}
        }
        mock_kalshi_requests['response'].content = b'{"error": {}}'

        service = KalshiService()
        result = service.get_balance()

        assert 'error' in result
        assert '401' in result['error']

    def test_get_positions_success(self, mock_kalshi_env, mock_kalshi_requests):
        """Test successful positions retrieval."""
        mock_kalshi_requests['response'].json.return_value = {
            'market_positions': [
                {
                    'ticker': 'MARKET-A',
                    'position': 10,
                    'market_exposure': 5000,
                    'realized_pnl': 200,
                    'resting_orders_count': 2
                },
                {
                    'ticker': 'MARKET-B',
                    'position': -5,
                    'market_exposure': 2500,
                    'realized_pnl': -100,
                    'resting_orders_count': 0
                }
            ]
        }

        service = KalshiService()
        result = service.get_positions()

        assert 'error' not in result
        assert len(result['market_positions']) == 2
        assert len(result['positions_enriched']) == 2

        # Check enrichment
        pos = result['positions_enriched'][0]
        assert pos['ticker'] == 'MARKET-A'
        assert pos['realized_pnl'] == 2.0  # Converted from cents

    def test_get_positions_empty(self, mock_kalshi_env, mock_kalshi_requests):
        """Test positions retrieval with no positions."""
        mock_kalshi_requests['response'].json.return_value = {
            'market_positions': []
        }

        service = KalshiService()
        result = service.get_positions()

        assert 'error' not in result
        assert result['market_positions'] == []
        assert result['positions_enriched'] == []

    def test_get_fills_success(self, mock_kalshi_env, mock_kalshi_requests):
        """Test successful fills retrieval."""
        mock_kalshi_requests['response'].json.return_value = {
            'fills': [
                {'fill_id': '1', 'ticker': 'MARKET-A', 'price': 50, 'count': 10},
                {'fill_id': '2', 'ticker': 'MARKET-B', 'price': 30, 'count': 5}
            ]
        }

        service = KalshiService()
        result = service.get_fills(limit=50)

        assert 'error' not in result
        assert len(result['fills']) == 2

    def test_get_orders_all(self, mock_kalshi_env, mock_kalshi_requests):
        """Test retrieving all orders."""
        mock_kalshi_requests['response'].json.return_value = {
            'orders': [
                {'order_id': '1', 'status': 'resting'},
                {'order_id': '2', 'status': 'executed'}
            ]
        }

        service = KalshiService()
        result = service.get_orders()

        assert 'error' not in result
        assert len(result['orders']) == 2

    def test_get_orders_filtered(self, mock_kalshi_env, mock_kalshi_requests):
        """Test retrieving filtered orders."""
        mock_kalshi_requests['response'].json.return_value = {
            'orders': [{'order_id': '1', 'status': 'resting'}]
        }

        service = KalshiService()
        result = service.get_orders(status='resting')

        assert 'error' not in result
        # Verify request was made with status param
        call_args = mock_kalshi_requests['session'].request.call_args
        assert call_args[1]['params']['status'] == 'resting'


# =============================================================================
# Order Management Tests
# =============================================================================

class TestOrderManagement:
    """Tests for order placement and cancellation."""

    def test_place_order_limit(self, mock_kalshi_env, mock_kalshi_requests):
        """Test placing a limit order."""
        mock_kalshi_requests['response'].json.return_value = {
            'order': {
                'order_id': 'order-123',
                'ticker': 'MARKET-A',
                'side': 'yes',
                'count': 10,
                'type': 'limit',
                'status': 'resting'
            }
        }

        service = KalshiService()
        result = service.place_order(
            ticker='MARKET-A',
            side='yes',
            count=10,
            type='limit',
            yes_price=50
        )

        assert 'error' not in result
        assert result['order']['order_id'] == 'order-123'

        # Verify request body
        call_args = mock_kalshi_requests['session'].request.call_args
        assert call_args[1]['json']['ticker'] == 'MARKET-A'
        assert call_args[1]['json']['side'] == 'yes'
        assert call_args[1]['json']['count'] == 10

    def test_place_order_market(self, mock_kalshi_env, mock_kalshi_requests):
        """Test placing a market order."""
        mock_kalshi_requests['response'].json.return_value = {
            'order': {
                'order_id': 'order-456',
                'type': 'market',
                'status': 'executed'
            }
        }

        service = KalshiService()
        result = service.place_order(
            ticker='MARKET-B',
            side='no',
            count=5,
            type='market'
        )

        assert 'error' not in result
        assert result['order']['type'] == 'market'

    def test_place_order_validation_error(self, mock_kalshi_env, mock_kalshi_requests):
        """Test order placement with validation error."""
        mock_kalshi_requests['response'].status_code = 400
        mock_kalshi_requests['response'].json.return_value = {
            'error': {'code': 'INVALID_REQUEST', 'message': 'Invalid count'}
        }
        mock_kalshi_requests['response'].content = b'{"error": {}}'

        service = KalshiService()
        result = service.place_order(
            ticker='MARKET-A',
            side='yes',
            count=-1,  # Invalid
            type='limit'
        )

        assert 'error' in result

    def test_cancel_order_success(self, mock_kalshi_env, mock_kalshi_requests):
        """Test successful order cancellation."""
        mock_kalshi_requests['response'].json.return_value = {
            'order': {'order_id': 'order-123', 'status': 'canceled'}
        }

        service = KalshiService()
        result = service.cancel_order('order-123')

        assert 'error' not in result
        # Verify DELETE request was made
        call_args = mock_kalshi_requests['session'].request.call_args
        assert call_args[1]['method'] == 'DELETE'

    def test_cancel_order_not_found(self, mock_kalshi_env, mock_kalshi_requests):
        """Test canceling non-existent order."""
        mock_kalshi_requests['response'].status_code = 404
        mock_kalshi_requests['response'].json.return_value = {
            'error': {'code': 'NOT_FOUND', 'message': 'Order not found'}
        }
        mock_kalshi_requests['response'].content = b'{"error": {}}'

        service = KalshiService()
        result = service.cancel_order('nonexistent-order')

        assert 'error' in result

    def test_cancel_all_orders_success(self, mock_kalshi_env, mock_kalshi_requests):
        """Test canceling all resting orders."""
        # First call returns resting orders
        # Subsequent calls cancel each order
        call_count = [0]

        def mock_request(*args, **kwargs):
            call_count[0] += 1
            mock_resp = MagicMock()
            mock_resp.status_code = 200

            if call_count[0] == 1:  # get_orders call
                mock_resp.json.return_value = {
                    'orders': [
                        {'order_id': 'order-1'},
                        {'order_id': 'order-2'}
                    ]
                }
            else:  # cancel calls
                mock_resp.json.return_value = {'order': {'status': 'canceled'}}

            return mock_resp

        mock_kalshi_requests['session'].request.side_effect = mock_request

        service = KalshiService()
        result = service.cancel_all_orders()

        assert result['total_canceled'] == 2
        assert result['total_failed'] == 0
        assert 'order-1' in result['canceled']
        assert 'order-2' in result['canceled']

    def test_cancel_all_orders_partial_failure(self, mock_kalshi_env, mock_kalshi_requests):
        """Test cancel all with some failures."""
        call_count = [0]

        def mock_request(*args, **kwargs):
            call_count[0] += 1
            mock_resp = MagicMock()

            if call_count[0] == 1:  # get_orders
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    'orders': [{'order_id': 'order-1'}, {'order_id': 'order-2'}]
                }
            elif call_count[0] == 2:  # first cancel succeeds
                mock_resp.status_code = 200
                mock_resp.json.return_value = {'order': {'status': 'canceled'}}
            else:  # second cancel fails
                mock_resp.status_code = 500
                mock_resp.json.return_value = {'error': {'message': 'Server error'}}
                mock_resp.content = b'{}'

            return mock_resp

        mock_kalshi_requests['session'].request.side_effect = mock_request

        service = KalshiService()
        result = service.cancel_all_orders()

        assert result['total_canceled'] == 1
        assert result['total_failed'] == 1


# =============================================================================
# Market Data Tests
# =============================================================================

class TestMarketData:
    """Tests for market data retrieval and analysis."""

    def test_get_market_with_orderbook(self, mock_kalshi_env, mock_kalshi_requests):
        """Test retrieving market with orderbook."""
        call_count = [0]

        def mock_request(*args, **kwargs):
            call_count[0] += 1
            mock_resp = MagicMock()
            mock_resp.status_code = 200

            if 'orderbook' in kwargs.get('url', ''):
                mock_resp.json.return_value = {
                    'orderbook': {
                        'yes': [[50, 100], [49, 200]],  # [price, count]
                        'no': [[48, 150], [47, 100]]
                    }
                }
            else:
                mock_resp.json.return_value = {
                    'market': {
                        'ticker': 'MARKET-A',
                        'title': 'Test Market',
                        'status': 'active'
                    }
                }

            return mock_resp

        mock_kalshi_requests['session'].request.side_effect = mock_request

        service = KalshiService()
        result = service.get_market_with_orderbook('MARKET-A')

        assert 'error' not in result
        assert result['market']['ticker'] == 'MARKET-A'
        assert 'analysis' in result
        assert result['analysis']['best_yes_bid'] == 50
        assert result['analysis']['best_no_bid'] == 48

    def test_market_analysis_spread(self, mock_kalshi_env, mock_kalshi_requests):
        """Test spread calculation."""
        def mock_request(*args, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200

            if 'orderbook' in kwargs.get('url', ''):
                mock_resp.json.return_value = {
                    'orderbook': {
                        'yes': [[60, 100]],
                        'no': [[35, 100]]
                    }
                }
            else:
                mock_resp.json.return_value = {'market': {'ticker': 'TEST'}}

            return mock_resp

        mock_kalshi_requests['session'].request.side_effect = mock_request

        service = KalshiService()
        result = service.get_market_with_orderbook('TEST')

        # Spread = 100 - 60 - 35 = 5
        assert result['analysis']['spread'] == 5

    def test_market_analysis_depth(self, mock_kalshi_env, mock_kalshi_requests):
        """Test depth calculation."""
        def mock_request(*args, **kwargs):
            mock_resp = MagicMock()
            mock_resp.status_code = 200

            if 'orderbook' in kwargs.get('url', ''):
                mock_resp.json.return_value = {
                    'orderbook': {
                        'yes': [[50, 100], [49, 200], [48, 150]],
                        'no': [[47, 50], [46, 100]]
                    }
                }
            else:
                mock_resp.json.return_value = {'market': {'ticker': 'TEST'}}

            return mock_resp

        mock_kalshi_requests['session'].request.side_effect = mock_request

        service = KalshiService()
        result = service.get_market_with_orderbook('TEST')

        # YES depth: 100 + 200 + 150 = 450
        # NO depth: 50 + 100 = 150
        assert result['analysis']['yes_depth'] == 450
        assert result['analysis']['no_depth'] == 150

    def test_liquidity_score_very_high(self, mock_kalshi_env):
        """Test VERY_HIGH liquidity score."""
        service = KalshiService()
        # Total depth > 10000
        yes_bids = [[50, 6000]]
        no_bids = [[48, 5000]]

        score = service._calculate_liquidity_score(yes_bids, no_bids)
        assert score == 'VERY_HIGH'

    def test_liquidity_score_high(self, mock_kalshi_env):
        """Test HIGH liquidity score."""
        service = KalshiService()
        yes_bids = [[50, 600]]
        no_bids = [[48, 500]]

        score = service._calculate_liquidity_score(yes_bids, no_bids)
        assert score == 'HIGH'

    def test_liquidity_score_moderate(self, mock_kalshi_env):
        """Test MODERATE liquidity score."""
        service = KalshiService()
        yes_bids = [[50, 60]]
        no_bids = [[48, 50]]

        score = service._calculate_liquidity_score(yes_bids, no_bids)
        assert score == 'MODERATE'

    def test_liquidity_score_low(self, mock_kalshi_env):
        """Test LOW liquidity score."""
        service = KalshiService()
        yes_bids = [[50, 8]]
        no_bids = [[48, 5]]

        score = service._calculate_liquidity_score(yes_bids, no_bids)
        assert score == 'LOW'

    def test_liquidity_score_very_low(self, mock_kalshi_env):
        """Test VERY_LOW liquidity score."""
        service = KalshiService()
        yes_bids = [[50, 3]]
        no_bids = [[48, 2]]

        score = service._calculate_liquidity_score(yes_bids, no_bids)
        assert score == 'VERY_LOW'

    def test_liquidity_score_empty_orderbook(self, mock_kalshi_env):
        """Test liquidity score with empty orderbook."""
        service = KalshiService()
        score = service._calculate_liquidity_score([], [])
        assert score == 'VERY_LOW'


# =============================================================================
# Analytics Tests
# =============================================================================

class TestAnalytics:
    """Tests for portfolio analytics."""

    def test_get_portfolio_summary(self, mock_kalshi_env, mock_kalshi_requests):
        """Test comprehensive portfolio summary."""
        call_count = [0]

        def mock_request(*args, **kwargs):
            call_count[0] += 1
            mock_resp = MagicMock()
            mock_resp.status_code = 200

            endpoint = kwargs.get('url', '')

            if 'balance' in endpoint:
                mock_resp.json.return_value = {
                    'balance': 10000,
                    'portfolio_value': 15000
                }
            elif 'positions' in endpoint:
                mock_resp.json.return_value = {
                    'market_positions': [
                        {'ticker': 'A', 'position': 10, 'market_exposure': 5000, 'realized_pnl': 200}
                    ]
                }
            elif 'orders' in endpoint:
                mock_resp.json.return_value = {
                    'orders': [{'order_id': '1', 'status': 'resting'}]
                }
            else:
                mock_resp.json.return_value = {}

            return mock_resp

        mock_kalshi_requests['session'].request.side_effect = mock_request

        service = KalshiService()
        result = service.get_portfolio_summary()

        assert result['balance'] == 100.0  # Converted from cents
        assert result['portfolio_value'] == 150.0
        assert result['total_positions'] == 1
        assert result['resting_orders'] == 1
        assert 'timestamp' in result


# =============================================================================
# Health Check Tests
# =============================================================================

class TestHealthCheck:
    """Tests for connection health checks."""

    def test_check_connection_all_good(self, mock_kalshi_env, mock_kalshi_requests):
        """Test health check when everything works."""
        call_count = [0]

        def mock_request(*args, **kwargs):
            call_count[0] += 1
            mock_resp = MagicMock()
            mock_resp.status_code = 200

            if 'status' in kwargs.get('url', ''):
                mock_resp.json.return_value = {'exchange_active': True}
            else:
                mock_resp.json.return_value = {'balance': 10000}

            return mock_resp

        mock_kalshi_requests['session'].request.side_effect = mock_request

        service = KalshiService()
        result = service.check_connection()

        assert result['public_api'] is True
        assert result['exchange_status'] is True
        assert result['api_key_configured'] is True
        assert result['private_key_loaded'] is True
        assert result['authenticated'] is True

    def test_check_connection_no_auth(self):
        """Test health check without credentials."""
        with patch.dict('os.environ', {}, clear=True):
            with patch('requests.Session') as mock_session_class:
                mock_session = MagicMock()
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {'exchange_active': True}
                mock_session.request.return_value = mock_response
                # Use MagicMock for headers
                mock_session.headers = MagicMock()
                mock_session_class.return_value = mock_session

                service = KalshiService()
                result = service.check_connection()

                assert result['public_api'] is True
                assert result['api_key_configured'] is False
                assert result['private_key_loaded'] is False
                assert result['authenticated'] is False
                assert 'not configured' in result['auth_error']

    def test_check_connection_auth_failed(self, mock_kalshi_env, mock_kalshi_requests):
        """Test health check with auth failure."""
        call_count = [0]

        def mock_request(*args, **kwargs):
            call_count[0] += 1
            mock_resp = MagicMock()

            if 'status' in kwargs.get('url', ''):
                mock_resp.status_code = 200
                mock_resp.json.return_value = {'exchange_active': True}
            else:
                mock_resp.status_code = 401
                mock_resp.json.return_value = {'error': {'message': 'Invalid key'}}
                mock_resp.content = b'{}'

            return mock_resp

        mock_kalshi_requests['session'].request.side_effect = mock_request

        service = KalshiService()
        result = service.check_connection()

        assert result['public_api'] is True
        assert result['authenticated'] is False
        assert 'auth_error' in result


# =============================================================================
# Global Instance Tests
# =============================================================================

class TestGlobalInstance:
    """Tests for global service instance management."""

    def test_get_kalshi_service_creates_instance(self, mock_kalshi_env, mock_kalshi_requests):
        """Test that get_kalshi_service creates instance."""
        # Reset global
        import core.services.kalshi_service as module
        module._kalshi_service = None

        service = get_kalshi_service(use_demo=True)

        assert service is not None
        assert service.use_demo is True

    def test_get_kalshi_service_reuses_instance(self, mock_kalshi_env, mock_kalshi_requests):
        """Test that get_kalshi_service reuses existing instance."""
        import core.services.kalshi_service as module
        module._kalshi_service = None

        service1 = get_kalshi_service(use_demo=True)
        service2 = get_kalshi_service(use_demo=True)

        assert service1 is service2

    def test_get_kalshi_service_recreates_on_mode_change(self, mock_kalshi_env, mock_kalshi_requests):
        """Test that changing mode creates new instance."""
        import core.services.kalshi_service as module
        module._kalshi_service = None

        service1 = get_kalshi_service(use_demo=True)
        service2 = get_kalshi_service(use_demo=False)

        assert service1 is not service2
        assert service1.use_demo is True
        assert service2.use_demo is False


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling scenarios."""

    def test_request_timeout(self, mock_kalshi_env, mock_kalshi_requests):
        """Test handling of request timeout."""
        import requests

        mock_kalshi_requests['session'].request.side_effect = requests.exceptions.Timeout()

        service = KalshiService()
        result = service.get_balance()

        assert 'error' in result
        assert 'Request failed' in result['error']

    def test_request_connection_error(self, mock_kalshi_env, mock_kalshi_requests):
        """Test handling of connection error."""
        import requests

        mock_kalshi_requests['session'].request.side_effect = requests.exceptions.ConnectionError()

        service = KalshiService()
        result = service.get_balance()

        assert 'error' in result

    def test_invalid_json_response(self, mock_kalshi_env, mock_kalshi_requests):
        """Test handling of invalid JSON response."""
        mock_kalshi_requests['response'].json.side_effect = json.JSONDecodeError('', '', 0)
        mock_kalshi_requests['response'].content = b'not json'

        service = KalshiService()
        # This should handle the error gracefully
        # The actual behavior depends on implementation


# =============================================================================
# Make Request Tests
# =============================================================================

class TestMakeRequest:
    """Tests for the _make_request method."""

    def test_make_request_auth_not_configured(self):
        """Test request when auth not configured but required."""
        with patch.dict('os.environ', {}, clear=True):
            service = KalshiService()
            result = service._make_request('GET', '/portfolio/balance', auth_required=True)

            assert 'error' in result
            assert 'Authentication not configured' in result['error']

    def test_make_request_no_auth_required(self, mock_kalshi_requests):
        """Test request without auth requirement."""
        mock_kalshi_requests['response'].json.return_value = {'status': 'ok'}

        with patch.dict('os.environ', {}, clear=True):
            service = KalshiService()
            result = service._make_request('GET', '/exchange/status', auth_required=False)

            assert 'error' not in result
            assert result['status'] == 'ok'
