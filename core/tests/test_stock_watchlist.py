"""Tests for Stock Watchlist API endpoints."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from core.models_unified_system import UserWatchlistItem

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass')


@pytest.fixture
def client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.mark.django_db(transaction=True)
class TestWatchlistAPI:

    def test_list_empty(self, client):
        resp = client.get('/api/stocks/watchlist/')
        assert resp.status_code == 200
        assert resp.json()['count'] == 0
        assert resp.json()['symbols'] == []

    def test_add_symbol(self, client):
        resp = client.post('/api/stocks/watchlist/add/', {'symbol': 'AAPL'}, format='json')
        assert resp.status_code == 201
        assert resp.json()['symbol'] == 'AAPL'

    def test_add_normalizes_uppercase(self, client):
        resp = client.post('/api/stocks/watchlist/add/', {'symbol': 'msft'}, format='json')
        assert resp.status_code == 201
        assert resp.json()['symbol'] == 'MSFT'

    def test_add_duplicate_is_idempotent(self, client):
        client.post('/api/stocks/watchlist/add/', {'symbol': 'TSLA'}, format='json')
        resp = client.post('/api/stocks/watchlist/add/', {'symbol': 'TSLA'}, format='json')
        assert resp.status_code == 200
        assert resp.json()['already_exists'] is True

    def test_add_empty_symbol_rejected(self, client):
        resp = client.post('/api/stocks/watchlist/add/', {'symbol': ''}, format='json')
        assert resp.status_code == 400

    def test_list_after_add(self, client):
        client.post('/api/stocks/watchlist/add/', {'symbol': 'AAPL'}, format='json')
        client.post('/api/stocks/watchlist/add/', {'symbol': 'GOOG'}, format='json')
        resp = client.get('/api/stocks/watchlist/')
        data = resp.json()
        assert data['count'] == 2
        symbols = [s['symbol'] for s in data['symbols']]
        assert 'AAPL' in symbols
        assert 'GOOG' in symbols

    def test_remove_symbol(self, client):
        client.post('/api/stocks/watchlist/add/', {'symbol': 'AAPL'}, format='json')
        resp = client.delete('/api/stocks/watchlist/AAPL/')
        assert resp.status_code == 200
        assert resp.json()['removed'] is True
        # Confirm removed
        resp = client.get('/api/stocks/watchlist/')
        assert resp.json()['count'] == 0

    def test_remove_nonexistent_returns_404(self, client):
        resp = client.delete('/api/stocks/watchlist/NOPE/')
        assert resp.status_code == 404

    def test_watchlist_is_per_user(self, db):
        user1 = User.objects.create_user(username='u1', password='p')
        user2 = User.objects.create_user(username='u2', password='p')
        UserWatchlistItem.objects.create(user=user1, symbol='AAPL')
        UserWatchlistItem.objects.create(user=user2, symbol='GOOG')

        c1 = APIClient()
        c1.force_authenticate(user=user1)
        resp = c1.get('/api/stocks/watchlist/')
        symbols = [s['symbol'] for s in resp.json()['symbols']]
        assert symbols == ['AAPL']

    def test_unauthenticated_rejected(self):
        c = APIClient()
        resp = c.get('/api/stocks/watchlist/')
        assert resp.status_code in (401, 403)
