#!/usr/bin/env python3
"""
API Key Validation Script
Tests all API keys in .env and reports their status

Usage: python scripts/test_api_keys.py
"""

import os
import sys
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class APIKeyTester:
    def __init__(self):
        self.results = {
            'valid': [],
            'invalid': [],
            'error': [],
            'skipped': []
        }

    def test_openai(self) -> Tuple[str, str]:
        """Test OpenAI API key"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        try:
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=10
            )
            if response.status_code == 200:
                return 'valid', 'API key is active'
            elif response.status_code == 401:
                return 'invalid', 'Invalid API key or unauthorized'
            else:
                return 'error', f'HTTP {response.status_code}: {response.text[:100]}'
        except Exception as e:
            return 'error', str(e)

    def test_anthropic(self) -> Tuple[str, str]:
        """Test Anthropic (Claude) API key"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        try:
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json'
                },
                json={
                    'model': 'claude-3-haiku-20240307',
                    'max_tokens': 10,
                    'messages': [{'role': 'user', 'content': 'test'}]
                },
                timeout=10
            )
            if response.status_code == 200:
                return 'valid', 'API key is active'
            elif response.status_code == 401:
                return 'invalid', 'Invalid API key'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_groq(self) -> Tuple[str, str]:
        """Test Groq API key"""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        try:
            response = requests.get(
                'https://api.groq.com/openai/v1/models',
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=10
            )
            if response.status_code == 200:
                return 'valid', 'API key is active'
            elif response.status_code == 401:
                return 'invalid', 'Invalid API key'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_stability_ai(self) -> Tuple[str, str]:
        """Test Stability AI API key"""
        api_key = os.getenv('STABILITY_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        try:
            response = requests.get(
                'https://api.stability.ai/v1/user/account',
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=10
            )
            if response.status_code == 200:
                return 'valid', 'API key is active'
            elif response.status_code == 401 or response.status_code == 403:
                return 'invalid', 'Invalid API key or unauthorized'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_runway(self) -> Tuple[str, str]:
        """Test Runway API key"""
        api_key = os.getenv('RUNWAY_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        try:
            # Updated endpoint: api.dev.runwayml.com (not api.runwayml.com)
            # Requires X-Runway-Version header
            # Use /v1/organization endpoint to validate
            response = requests.get(
                'https://api.dev.runwayml.com/v1/organization',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'X-Runway-Version': '2024-11-06',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                credits = data.get('creditBalance', 'unknown')
                return 'valid', f'API key is active (Credits: {credits})'
            elif response.status_code == 401 or response.status_code == 403:
                return 'invalid', 'Invalid API key'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_elevenlabs(self) -> Tuple[str, str]:
        """Test ElevenLabs API key"""
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        try:
            response = requests.get(
                'https://api.elevenlabs.io/v1/user',
                headers={'xi-api-key': api_key},
                timeout=10
            )
            if response.status_code == 200:
                return 'valid', 'API key is active'
            elif response.status_code == 401:
                return 'invalid', 'Invalid API key'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_polygon(self) -> Tuple[str, str]:
        """Test Polygon.io API key"""
        api_key = os.getenv('POLYGON_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        try:
            # Use current date to avoid plan limitation errors
            from datetime import date, timedelta
            yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')

            response = requests.get(
                f'https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/{yesterday}/{yesterday}?apiKey={api_key}',
                timeout=10
            )
            if response.status_code == 200:
                return 'valid', 'API key is active'
            elif response.status_code == 401:
                return 'invalid', 'Invalid API key'
            elif response.status_code == 403:
                data = response.json()
                # Key is valid but plan limited
                if 'NOT_AUTHORIZED' in data.get('status', ''):
                    return 'valid', 'API key valid (plan limitation on data range)'
                return 'invalid', 'Invalid API key or expired'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_sec_api(self) -> Tuple[str, str]:
        """Test SEC API key"""
        api_key = os.getenv('SEC_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        try:
            response = requests.get(
                'https://api.sec-api.io/mapping/ticker/AAPL',
                headers={'Authorization': api_key},
                timeout=10
            )
            if response.status_code == 200:
                return 'valid', 'API key is active'
            elif response.status_code == 401 or response.status_code == 403:
                return 'invalid', 'Invalid API key'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_the_odds_api(self) -> Tuple[str, str]:
        """Test The Odds API key"""
        api_key = os.getenv('THE_ODDS_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        try:
            response = requests.get(
                f'https://api.the-odds-api.com/v4/sports/?apiKey={api_key}',
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return 'valid', f'API key is active ({len(data)} sports available)'
            elif response.status_code == 401:
                return 'invalid', 'Invalid API key'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_sportsradar(self) -> Tuple[str, str]:
        """Test SportsRadar API key"""
        api_key = os.getenv('SPORTSRADAR_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        # Note: SportsRadar requires sport-specific endpoints
        return 'skipped', 'Manual testing required (sport-specific endpoints)'

    def test_coinbase(self) -> Tuple[str, str]:
        """Test Coinbase API key"""
        api_key = os.getenv('COINBASE_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        # Coinbase CDP API requires special signing - skip for now
        return 'skipped', 'Requires special authentication (CDP API)'

    def test_etherscan(self) -> Tuple[str, str]:
        """Test Etherscan API key"""
        api_key = os.getenv('ETHERSCAN_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        try:
            # Updated to use V2 API endpoint
            response = requests.get(
                f'https://api.etherscan.io/v2/api?chainid=1&module=account&action=balance&address=0x0000000000000000000000000000000000000000&tag=latest&apikey={api_key}',
                timeout=15  # Increase timeout for Etherscan
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1':
                    return 'valid', 'API key is active (V2 API)'
                else:
                    # Check if it's just V1 deprecation message
                    if 'deprecated' in str(data.get('result', '')).lower():
                        return 'valid', 'API key is active (migrated to V2)'
                    return 'invalid', data.get('message', 'Unknown error')
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_coingecko(self) -> Tuple[str, str]:
        """Test CoinGecko API key"""
        api_key = os.getenv('COINGECKO_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        try:
            response = requests.get(
                'https://api.coingecko.com/api/v3/ping',
                headers={'x-cg-pro-api-key': api_key},
                timeout=10
            )
            if response.status_code == 200:
                return 'valid', 'API key is active'
            elif response.status_code == 401:
                return 'invalid', 'Invalid API key'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_reddit(self) -> Tuple[str, str]:
        """Test Reddit API credentials"""
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        username = os.getenv('REDDIT_USERNAME')
        password = os.getenv('REDDIT_PASSWORD')

        if not all([client_id, client_secret, username, password]):
            return 'skipped', 'Missing credentials'

        try:
            auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
            data = {
                'grant_type': 'password',
                'username': username,
                'password': password
            }
            headers = {'User-Agent': os.getenv('USER_AGENT', 'API Key Test/1.0')}

            response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                auth=auth,
                data=data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                token_data = response.json()
                if 'access_token' in token_data:
                    return 'valid', 'Reddit credentials are active'
                elif 'error' in token_data:
                    error = token_data.get('error')
                    if error == 'unauthorized_client':
                        return 'error', 'App must be "script" type (not "web app") at reddit.com/prefs/apps'
                    return 'invalid', f"Error: {token_data.get('error_description', error)}"
                else:
                    return 'invalid', 'Failed to get access token'
            elif response.status_code == 401:
                return 'invalid', 'Invalid credentials'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_stripe(self) -> Tuple[str, str]:
        """Test Stripe API key"""
        api_key = os.getenv('STRIPE_SECRET_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        try:
            response = requests.get(
                'https://api.stripe.com/v1/balance',
                auth=(api_key, ''),
                timeout=10
            )
            if response.status_code == 200:
                return 'valid', 'API key is active'
            elif response.status_code == 401:
                return 'invalid', 'Invalid API key'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_news_api(self) -> Tuple[str, str]:
        """Test News API key"""
        api_key = os.getenv('NEWS_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        try:
            response = requests.get(
                f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}',
                timeout=10
            )
            if response.status_code == 200:
                return 'valid', 'API key is active'
            elif response.status_code == 401:
                return 'invalid', 'Invalid API key'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_serper(self) -> Tuple[str, str]:
        """Test Serper API key (Google Search)"""
        api_key = os.getenv('SERPER_API_KEY')
        if not api_key:
            return 'skipped', 'No API key found'

        try:
            response = requests.post(
                'https://google.serper.dev/search',
                headers={'X-API-KEY': api_key, 'Content-Type': 'application/json'},
                json={'q': 'test'},
                timeout=10
            )
            if response.status_code == 200:
                return 'valid', 'API key is active'
            elif response.status_code == 401 or response.status_code == 403:
                return 'invalid', 'Invalid API key'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_github(self) -> Tuple[str, str]:
        """Test GitHub token"""
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            return 'skipped', 'No token found'

        try:
            response = requests.get(
                'https://api.github.com/user',
                headers={'Authorization': f'token {token}'},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return 'valid', f"Active for user: {data.get('login', 'unknown')}"
            elif response.status_code == 401:
                return 'invalid', 'Invalid token'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def test_huggingface(self) -> Tuple[str, str]:
        """Test Hugging Face API token"""
        token = os.getenv('HUGGING_FACE_API')
        if not token:
            return 'skipped', 'No token found'

        try:
            response = requests.get(
                'https://huggingface.co/api/whoami-v2',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )
            if response.status_code == 200:
                return 'valid', 'Token is active'
            elif response.status_code == 401:
                return 'invalid', 'Invalid token'
            else:
                return 'error', f'HTTP {response.status_code}'
        except Exception as e:
            return 'error', str(e)

    def run_all_tests(self):
        """Run all API key tests"""
        tests = [
            ('OpenAI', self.test_openai),
            ('Anthropic (Claude)', self.test_anthropic),
            ('Groq', self.test_groq),
            ('Stability AI', self.test_stability_ai),
            ('Runway ML', self.test_runway),
            ('ElevenLabs', self.test_elevenlabs),
            ('Polygon.io', self.test_polygon),
            ('SEC API', self.test_sec_api),
            ('The Odds API', self.test_the_odds_api),
            ('SportsRadar', self.test_sportsradar),
            ('Coinbase', self.test_coinbase),
            ('Etherscan', self.test_etherscan),
            ('CoinGecko', self.test_coingecko),
            ('Reddit', self.test_reddit),
            ('Stripe', self.test_stripe),
            ('News API', self.test_news_api),
            ('Serper (Google Search)', self.test_serper),
            ('GitHub', self.test_github),
            ('Hugging Face', self.test_huggingface),
        ]

        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}API Key Validation Report")
        print(f"{Fore.CYAN}Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.CYAN}{'='*70}\n")

        for name, test_func in tests:
            print(f"Testing {name}...", end=' ')
            status, message = test_func()

            if status == 'valid':
                print(f"{Fore.GREEN}✓ VALID{Style.RESET_ALL} - {message}")
                self.results['valid'].append((name, message))
            elif status == 'invalid':
                print(f"{Fore.RED}✗ INVALID{Style.RESET_ALL} - {message}")
                self.results['invalid'].append((name, message))
            elif status == 'error':
                print(f"{Fore.YELLOW}⚠ ERROR{Style.RESET_ALL} - {message}")
                self.results['error'].append((name, message))
            else:  # skipped
                print(f"{Fore.BLUE}○ SKIPPED{Style.RESET_ALL} - {message}")
                self.results['skipped'].append((name, message))

        self.print_summary()

    def print_summary(self):
        """Print summary of results"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}Summary")
        print(f"{Fore.CYAN}{'='*70}\n")

        print(f"{Fore.GREEN}✓ Valid Keys: {len(self.results['valid'])}")
        for name, msg in self.results['valid']:
            print(f"  - {name}")

        if self.results['invalid']:
            print(f"\n{Fore.RED}✗ Invalid Keys: {len(self.results['invalid'])} {Fore.RED}← NEEDS ATTENTION")
            for name, msg in self.results['invalid']:
                print(f"  - {name}: {msg}")

        if self.results['error']:
            print(f"\n{Fore.YELLOW}⚠ Errors: {len(self.results['error'])}")
            for name, msg in self.results['error']:
                print(f"  - {name}: {msg}")

        if self.results['skipped']:
            print(f"\n{Fore.BLUE}○ Skipped: {len(self.results['skipped'])}")
            for name, msg in self.results['skipped']:
                print(f"  - {name}: {msg}")

        print(f"\n{Fore.CYAN}{'='*70}\n")

        # Action items
        if self.results['invalid']:
            print(f"{Fore.RED}ACTION REQUIRED:")
            print(f"{Fore.RED}The following API keys need to be updated:")
            for name, msg in self.results['invalid']:
                print(f"{Fore.RED}  → {name}")
            print()

def main():
    """Main entry point"""
    # Check for required package
    try:
        import colorama
    except ImportError:
        print("Installing required package: colorama...")
        os.system(f"{sys.executable} -m pip install colorama --quiet")
        import colorama

    tester = APIKeyTester()
    tester.run_all_tests()

if __name__ == '__main__':
    main()
