"""
API Configuration for Spiders
Centralizes all API configurations and authentication
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class APIConfig:
    """Centralized API configuration for all spiders"""

    @staticmethod
    def get_bluesky_config() -> Dict[str, str]:
        """Get Bluesky API configuration"""
        return {
            'identifier': os.getenv('BLUESKY_IDENTIFIER', ''),
            'password': os.getenv('BLUESKY_PASSWORD', ''),
            'base_url': 'https://bsky.social/xrpc/'
        }

    @staticmethod
    def get_reddit_config() -> Dict[str, str]:
        """Get Reddit API configuration"""
        return {
            'client_id': os.getenv('REDDIT_CLIENT_ID', ''),
            'client_secret': os.getenv('REDDIT_CLIENT_SECRET', ''),
            'user_agent': 'UnifiedDonkeyBetz/1.0',
            'base_url': 'https://oauth.reddit.com'
        }

    @staticmethod
    def get_polygon_config() -> Dict[str, str]:
        """Get Polygon.io API configuration"""
        return {
            'api_key': os.getenv('POLYGON_API_KEY', ''),
            'base_url': 'https://api.polygon.io'
        }

    @staticmethod
    def get_alpha_vantage_config() -> Dict[str, str]:
        """Get Alpha Vantage API configuration"""
        return {
            'api_key': os.getenv('ALPHA_VANTAGE_API_KEY', ''),
            'base_url': 'https://www.alphavantage.co/query'
        }

    @staticmethod
    def get_finnhub_config() -> Dict[str, str]:
        """Get Finnhub API configuration"""
        return {
            'api_key': os.getenv('FINNHUB_API_KEY', ''),
            'base_url': 'https://finnhub.io/api/v1'
        }

    @staticmethod
    def get_newsapi_config() -> Dict[str, str]:
        """Get NewsAPI configuration"""
        return {
            'api_key': os.getenv('NEWS_API_KEY', ''),
            'base_url': 'https://newsapi.org/v2'
        }

    @staticmethod
    def get_binance_config() -> Dict[str, str]:
        """Get Binance API configuration"""
        return {
            'api_key': os.getenv('BINANCE_API_KEY', ''),
            'api_secret': os.getenv('BINANCE_API_SECRET', ''),
            'base_url': 'https://api.binance.com/api/v3'
        }

    @staticmethod
    def get_coinbase_config() -> Dict[str, str]:
        """Get Coinbase API configuration"""
        return {
            'api_key': os.getenv('COINBASE_API_KEY', ''),
            'api_secret': os.getenv('COINBASE_API_SECRET', ''),
            'base_url': 'https://api.coinbase.com/v2'
        }


# Singleton instance
api_config = APIConfig()