"""
Health Endpoint Tests

Session 102 - Mobile Auth & Connection Settings
Tests for the /health/ping/ endpoint used by mobile app for connectivity testing
"""

from django.test import TestCase, Client
from django.urls import reverse
import json


class HealthEndpointTests(TestCase):
    """Test the health check endpoint"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()

    def test_health_ping_returns_200(self):
        """Test that /health/ping/ returns 200 OK"""
        response = self.client.get('/health/ping/')
        self.assertEqual(response.status_code, 200)

    def test_health_ping_returns_json(self):
        """Test that /health/ping/ returns JSON"""
        response = self.client.get('/health/ping/')
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_health_ping_returns_ok_true(self):
        """Test that /health/ping/ returns {"ok": true}"""
        response = self.client.get('/health/ping/')
        data = json.loads(response.content)
        self.assertTrue(data.get('ok'))

    def test_health_ping_no_authentication_required(self):
        """Test that /health/ping/ does not require authentication"""
        # Health check should work without any authentication
        response = self.client.get('/health/ping/')
        self.assertEqual(response.status_code, 200)

    def test_health_ping_accepts_get_only(self):
        """Test that /health/ping/ only accepts GET requests"""
        # GET should work
        response = self.client.get('/health/ping/')
        self.assertEqual(response.status_code, 200)

        # POST should fail (405 Method Not Allowed or 404)
        response = self.client.post('/health/ping/')
        self.assertIn(response.status_code, [404, 405])

    def test_health_ping_response_structure(self):
        """Test that /health/ping/ returns the expected JSON structure"""
        response = self.client.get('/health/ping/')
        data = json.loads(response.content)

        # Should have 'ok' key
        self.assertIn('ok', data)

        # Value should be boolean
        self.assertIsInstance(data['ok'], bool)
