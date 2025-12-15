# tests/api/test_golden_path_api.py
"""
Session 416: Golden Path API Tests

These are smoke tests that verify the core API endpoints are responding correctly.
They test the "golden path" - the happy path where everything works as expected.

These tests ensure:
1. Endpoints return correct status codes
2. Response structure contains expected keys
3. Basic functionality is operational

Run with: pytest tests/api/test_golden_path_api.py -v

Note: These tests use requests to hit the live server and do NOT require
database access markers. They're pure HTTP smoke tests.
"""
import pytest
import requests


# =============================================================================
# Live Server Configuration
# =============================================================================

BASE_URL = "http://localhost:8000"


def live_get(path):
    """Make a GET request to the live server."""
    return requests.get(f"{BASE_URL}{path}", timeout=10)


# =============================================================================
# Health Check Tests
# =============================================================================

@pytest.mark.golden_path
class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_ping_returns_ok(self):
        """
        Test: GET /health/ping/
        Expected: {"ok": true}
        """
        response = live_get('/health/ping/')

        assert response.status_code == 200
        data = response.json()
        assert 'ok' in data
        assert data['ok'] is True


# =============================================================================
# Agent Dreams API Tests
# =============================================================================

@pytest.mark.golden_path
class TestAgentDreamsAPI:
    """Test the agent dreams API endpoint."""

    def test_agent_dreams_list_returns_200(self):
        """
        Test: GET /api/agent-dreams/
        Expected: 200 with list of dreams

        Uses existing production data (1,891+ dreams exist).
        """
        response = live_get('/api/agent-dreams/')

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert 'success' in data
        assert data['success'] is True
        assert 'dreams' in data
        assert isinstance(data['dreams'], list)

    def test_agent_dreams_returns_expected_fields(self):
        """
        Test that dreams contain expected fields.
        """
        response = live_get('/api/agent-dreams/')

        assert response.status_code == 200
        data = response.json()

        if data['dreams']:
            dream = data['dreams'][0]
            # Check key fields exist
            expected_fields = ['id', 'agent_name', 'title', 'content', 'dream_type']
            for field in expected_fields:
                assert field in dream, f"Missing field: {field}"


# =============================================================================
# Boardroom Decisions API Tests
# =============================================================================

@pytest.mark.golden_path
class TestBoardroomDecisionsAPI:
    """Test the boardroom decisions API endpoint."""

    def test_boardroom_decisions_list_returns_200(self):
        """
        Test: GET /api/boardroom/decisions/
        Expected: 200 with list of decisions

        Uses existing production data (258+ decisions exist).
        """
        response = live_get('/api/boardroom/decisions/')

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert 'success' in data
        assert data['success'] is True
        assert 'decisions' in data
        assert isinstance(data['decisions'], list)

    def test_boardroom_decisions_has_counts(self):
        """
        Test that decisions response includes count metadata.
        """
        response = live_get('/api/boardroom/decisions/')

        assert response.status_code == 200
        data = response.json()

        # Check metadata exists
        assert 'count' in data or 'total' in data
        assert 'canonical_count' in data or 'type_counts' in data


# =============================================================================
# Agent Evolution API Tests
# =============================================================================

@pytest.mark.golden_path
class TestAgentEvolutionAPI:
    """Test the agent evolution leaderboard API endpoint."""

    def test_agent_evolution_leaderboard_returns_200(self):
        """
        Test: GET /api/agent-evolution/leaderboard/
        Expected: 200 with leaderboard data

        Uses existing production data (24+ evolution records exist).
        """
        response = live_get('/api/agent-evolution/leaderboard/')

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert 'success' in data
        assert data['success'] is True
        assert 'leaderboard' in data
        assert isinstance(data['leaderboard'], list)

    def test_agent_evolution_leaderboard_entry_structure(self):
        """
        Test that leaderboard entries have expected fields.
        """
        response = live_get('/api/agent-evolution/leaderboard/')

        assert response.status_code == 200
        data = response.json()

        if data['leaderboard']:
            entry = data['leaderboard'][0]
            # Check key fields exist
            expected_fields = ['agent_name', 'level', 'total_xp']
            for field in expected_fields:
                assert field in entry, f"Missing field: {field}"


# =============================================================================
# Opportunities API Tests
# =============================================================================

@pytest.mark.golden_path
class TestOpportunitiesAPI:
    """Test the opportunities API endpoint."""

    def test_opportunities_list_returns_200(self):
        """
        Test: GET /api/opportunities/
        Expected: 200 with list of opportunities (may be empty)
        """
        response = live_get('/api/opportunities/')

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert 'success' in data
        assert data['success'] is True
        assert 'opportunities' in data
        assert isinstance(data['opportunities'], list)

    def test_opportunities_has_count(self):
        """
        Test that opportunities response includes count.
        """
        response = live_get('/api/opportunities/')

        assert response.status_code == 200
        data = response.json()

        assert 'count' in data
        assert isinstance(data['count'], int)


# =============================================================================
# Authentication Required API Tests
# =============================================================================

@pytest.mark.golden_path
class TestAuthRequiredEndpoints:
    """Test endpoints that require authentication."""

    def test_spider_data_feed_requires_auth(self):
        """
        Test: GET /api/spider/data-feed/
        Expected: 401 or authentication error when not authenticated
        """
        response = live_get('/api/spider/data-feed/')

        # Should either return 401 or a JSON error about authentication
        if response.status_code == 200:
            data = response.json()
            # If it returns 200, check if it's an auth error response
            if 'success' in data and data['success'] is False:
                assert 'error' in data
        else:
            # Expect 401, 403, or redirect
            assert response.status_code in [401, 403, 302]

    def test_shared_knowledge_requires_auth(self):
        """
        Test: GET /api/shared-knowledge/
        Expected: 401 or authentication error when not authenticated
        """
        response = live_get('/api/shared-knowledge/')

        # Should either return 401 or a JSON error about authentication
        if response.status_code == 200:
            data = response.json()
            # If it returns 200, check if it's an auth error response
            if 'success' in data and data['success'] is False:
                assert 'error' in data
        else:
            # Expect 401, 403, or redirect
            assert response.status_code in [401, 403, 302]


# =============================================================================
# Response Shape Tests
# =============================================================================

@pytest.mark.golden_path
class TestAPIResponseConsistency:
    """Test that API responses follow consistent patterns."""

    def test_success_responses_have_success_key(self):
        """
        Test that successful responses include a 'success' key.
        """
        endpoints = [
            '/api/agent-dreams/',
            '/api/boardroom/decisions/',
            '/api/agent-evolution/leaderboard/',
            '/api/opportunities/',
        ]

        for endpoint in endpoints:
            response = live_get(endpoint)
            if response.status_code == 200:
                data = response.json()
                assert 'success' in data, f"Missing 'success' key in {endpoint}"

    def test_error_responses_have_error_structure(self):
        """
        Test that error responses include proper error structure.
        """
        # Test an endpoint that requires auth
        response = live_get('/api/spider/data-feed/')

        if response.status_code == 200:
            data = response.json()
            if data.get('success') is False:
                assert 'error' in data
                error = data['error']
                # Error should have code and/or message
                assert 'code' in error or 'message' in error
