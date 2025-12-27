"""
The Odds API Spider
Fetches sports betting odds from 40+ bookmakers across major sports leagues.

API: https://the-odds-api.com/
Tier: Paid (20k requests/month)

Sports covered:
- NFL, NBA, MLB, NHL (US major leagues)
- Soccer (EPL, La Liga, Champions League, MLS)
- UFC/MMA
- Tennis, Golf, Boxing
- College sports (NCAAF, NCAAB)
"""

import os
import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TheOddsSpider:
    """
    Spider for The Odds API - sports betting odds aggregator.
    Fetches odds from 40+ bookmakers for major sports.
    """

    name = "theodds"
    base_url = "https://api.the-odds-api.com/v4"

    # Popular sports to fetch (API sport keys)
    SPORTS = {
        # US Major Leagues
        'americanfootball_nfl': {'name': 'NFL', 'category': 'american_football', 'priority': 1},
        'basketball_nba': {'name': 'NBA', 'category': 'basketball', 'priority': 1},
        'baseball_mlb': {'name': 'MLB', 'category': 'baseball', 'priority': 1},
        'icehockey_nhl': {'name': 'NHL', 'category': 'hockey', 'priority': 1},

        # College Sports
        'americanfootball_ncaaf': {'name': 'NCAAF', 'category': 'american_football', 'priority': 2},
        'basketball_ncaab': {'name': 'NCAAB', 'category': 'basketball', 'priority': 2},

        # Soccer
        'soccer_epl': {'name': 'English Premier League', 'category': 'soccer', 'priority': 1},
        'soccer_spain_la_liga': {'name': 'La Liga', 'category': 'soccer', 'priority': 2},
        'soccer_germany_bundesliga': {'name': 'Bundesliga', 'category': 'soccer', 'priority': 2},
        'soccer_italy_serie_a': {'name': 'Serie A', 'category': 'soccer', 'priority': 2},
        'soccer_france_ligue_one': {'name': 'Ligue 1', 'category': 'soccer', 'priority': 2},
        'soccer_usa_mls': {'name': 'MLS', 'category': 'soccer', 'priority': 2},
        'soccer_uefa_champs_league': {'name': 'Champions League', 'category': 'soccer', 'priority': 1},

        # Combat Sports
        'mma_mixed_martial_arts': {'name': 'UFC/MMA', 'category': 'mma', 'priority': 1},
        'boxing_boxing': {'name': 'Boxing', 'category': 'boxing', 'priority': 2},

        # Other
        'tennis_atp_french_open': {'name': 'ATP French Open', 'category': 'tennis', 'priority': 2},
        'tennis_wta_french_open': {'name': 'WTA French Open', 'category': 'tennis', 'priority': 2},
        'golf_pga_championship': {'name': 'PGA Championship', 'category': 'golf', 'priority': 2},
    }

    # Preferred bookmakers (US-focused)
    PREFERRED_BOOKMAKERS = [
        'draftkings',
        'fanduel',
        'betmgm',
        'caesars',
        'pointsbetus',
        'bovada',
        'betonlineag',
    ]

    # Market types
    MARKETS = ['h2h', 'spreads', 'totals']  # Head-to-head, point spreads, over/under

    def __init__(self):
        self.api_key = os.getenv('THE_ODDS_API_KEY')
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
        })
        self.requests_remaining = None
        self.requests_used = None

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated API request."""
        if not self.api_key:
            logger.error("THE_ODDS_API_KEY not configured")
            return None

        url = f"{self.base_url}/{endpoint}"
        params = params or {}
        params['apiKey'] = self.api_key

        try:
            response = self.session.get(url, params=params, timeout=30)

            # Track API usage from headers
            self.requests_remaining = response.headers.get('x-requests-remaining')
            self.requests_used = response.headers.get('x-requests-used')

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.error("Invalid API key for The Odds API")
                return None
            elif response.status_code == 429:
                logger.warning("Rate limit exceeded for The Odds API")
                return None
            else:
                logger.error(f"The Odds API error {response.status_code}: {response.text[:200]}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {endpoint}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {str(e)}")
            return None

    def fetch_data(self, sports: List[str] = None, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Main entry point - fetch odds for specified sports.

        Args:
            sports: List of sport keys (e.g., ['americanfootball_nfl', 'basketball_nba'])
                   If None, fetches priority 1 sports
            max_results: Maximum number of events to return

        Returns:
            List of normalized event data with odds
        """
        results = []

        # Default to priority 1 sports if none specified
        if sports is None:
            sports = [k for k, v in self.SPORTS.items() if v.get('priority') == 1]

        # First, get list of in-season sports
        active_sports = self._get_active_sports()
        if not active_sports:
            logger.warning("Could not fetch active sports list")
            active_sports = sports  # Fall back to requested sports

        # Filter to only active sports
        sports_to_fetch = [s for s in sports if s in active_sports]

        for sport_key in sports_to_fetch:
            if len(results) >= max_results:
                break

            sport_info = self.SPORTS.get(sport_key, {})
            events = self._fetch_sport_odds(sport_key)

            if events:
                for event in events:
                    if len(results) >= max_results:
                        break

                    normalized = self._normalize_event(event, sport_key, sport_info)
                    if normalized:
                        results.append(normalized)

        # Add metadata
        results.append({
            'data_type': 'api_status',
            'spider_name': self.name,
            'requests_remaining': self.requests_remaining,
            'requests_used': self.requests_used,
            'timestamp': datetime.utcnow().isoformat(),
        })

        logger.info(f"TheOddsSpider fetched {len(results)-1} events, API requests remaining: {self.requests_remaining}")
        return results

    def _get_active_sports(self) -> List[str]:
        """Get list of currently active/in-season sports."""
        data = self._make_request('sports')
        if not data:
            return []

        return [sport['key'] for sport in data if sport.get('active', False)]

    def _fetch_sport_odds(self, sport_key: str) -> List[Dict]:
        """Fetch odds for a specific sport."""
        params = {
            'regions': 'us',
            'markets': ','.join(self.MARKETS),
            'oddsFormat': 'american',
            'dateFormat': 'iso',
        }

        data = self._make_request(f'sports/{sport_key}/odds', params)
        return data if data else []

    def _normalize_event(self, event: Dict, sport_key: str, sport_info: Dict) -> Optional[Dict]:
        """Normalize event data to standard format."""
        try:
            home_team = event.get('home_team', 'Unknown')
            away_team = event.get('away_team', 'Unknown')
            commence_time = event.get('commence_time', '')

            # Parse odds from bookmakers
            odds_data = self._extract_best_odds(event.get('bookmakers', []))

            # Calculate implied probabilities
            h2h = odds_data.get('h2h', {})
            home_prob = self._american_to_probability(h2h.get('home_odds'))
            away_prob = self._american_to_probability(h2h.get('away_odds'))

            # Determine favorite
            if home_prob and away_prob:
                if home_prob > away_prob:
                    favorite = home_team
                    favorite_prob = home_prob
                else:
                    favorite = away_team
                    favorite_prob = away_prob
            else:
                favorite = None
                favorite_prob = None

            return {
                'data_type': 'sports_odds',
                'spider_name': self.name,
                'source_platform': 'theodds',
                'source_url': f"https://the-odds-api.com/sports/{sport_key}",

                # Event info
                'event_id': event.get('id'),
                'sport_key': sport_key,
                'sport_name': sport_info.get('name', sport_key),
                'category': sport_info.get('category', 'sports'),
                'league': sport_info.get('name', sport_key),

                # Teams
                'home_team': home_team,
                'away_team': away_team,
                'title': f"{away_team} @ {home_team}",

                # Timing
                'commence_time': commence_time,
                'commence_time_formatted': self._format_time(commence_time),
                'is_live': self._is_live(commence_time),

                # Moneyline (H2H) odds
                'home_odds': h2h.get('home_odds'),
                'away_odds': h2h.get('away_odds'),
                'draw_odds': h2h.get('draw_odds'),
                'home_implied_prob': round(home_prob * 100, 1) if home_prob else None,
                'away_implied_prob': round(away_prob * 100, 1) if away_prob else None,

                # Spread odds
                'spread': odds_data.get('spreads', {}),
                'home_spread': odds_data.get('spreads', {}).get('home_point'),
                'away_spread': odds_data.get('spreads', {}).get('away_point'),

                # Totals (over/under)
                'totals': odds_data.get('totals', {}),
                'total_line': odds_data.get('totals', {}).get('point'),
                'over_odds': odds_data.get('totals', {}).get('over_odds'),
                'under_odds': odds_data.get('totals', {}).get('under_odds'),

                # Analysis
                'favorite': favorite,
                'favorite_probability': round(favorite_prob * 100, 1) if favorite_prob else None,
                'bookmaker_count': len(event.get('bookmakers', [])),
                'best_bookmaker': odds_data.get('best_bookmaker'),

                # Metadata
                'fetched_at': datetime.utcnow().isoformat(),
                'tags': self._generate_tags(event, odds_data, favorite_prob),
            }

        except Exception as e:
            logger.error(f"Error normalizing event: {str(e)}")
            return None

    def _extract_best_odds(self, bookmakers: List[Dict]) -> Dict:
        """Extract best odds from bookmaker data, preferring US books."""
        result = {
            'h2h': {},
            'spreads': {},
            'totals': {},
            'best_bookmaker': None,
        }

        if not bookmakers:
            return result

        # Sort bookmakers - preferred ones first
        sorted_books = sorted(
            bookmakers,
            key=lambda b: (
                0 if b.get('key') in self.PREFERRED_BOOKMAKERS else 1,
                self.PREFERRED_BOOKMAKERS.index(b.get('key')) if b.get('key') in self.PREFERRED_BOOKMAKERS else 99
            )
        )

        for bookmaker in sorted_books:
            book_key = bookmaker.get('key')

            for market in bookmaker.get('markets', []):
                market_key = market.get('key')
                outcomes = market.get('outcomes', [])

                if market_key == 'h2h' and not result['h2h']:
                    for outcome in outcomes:
                        name = outcome.get('name')
                        price = outcome.get('price')
                        if name and price:
                            # Match to home/away/draw
                            if 'Draw' in name or name == 'Draw':
                                result['h2h']['draw_odds'] = price
                            else:
                                # First non-draw is typically away, second is home
                                # But we need to match by name
                                if 'home_odds' not in result['h2h']:
                                    result['h2h']['home_odds'] = price
                                    result['h2h']['home_team'] = name
                                elif 'away_odds' not in result['h2h']:
                                    result['h2h']['away_odds'] = price
                                    result['h2h']['away_team'] = name

                    if result['h2h']:
                        result['best_bookmaker'] = book_key

                elif market_key == 'spreads' and not result['spreads']:
                    for outcome in outcomes:
                        name = outcome.get('name')
                        point = outcome.get('point')
                        price = outcome.get('price')
                        if point is not None:
                            if 'home_point' not in result['spreads']:
                                result['spreads']['home_point'] = point
                                result['spreads']['home_odds'] = price
                            else:
                                result['spreads']['away_point'] = point
                                result['spreads']['away_odds'] = price

                elif market_key == 'totals' and not result['totals']:
                    for outcome in outcomes:
                        name = outcome.get('name', '').lower()
                        point = outcome.get('point')
                        price = outcome.get('price')
                        if 'over' in name:
                            result['totals']['point'] = point
                            result['totals']['over_odds'] = price
                        elif 'under' in name:
                            result['totals']['under_odds'] = price

        return result

    def _american_to_probability(self, odds: int) -> Optional[float]:
        """Convert American odds to implied probability."""
        if odds is None:
            return None

        try:
            if odds > 0:
                return 100 / (odds + 100)
            else:
                return abs(odds) / (abs(odds) + 100)
        except:
            return None

    def _format_time(self, iso_time: str) -> str:
        """Format ISO time to readable string."""
        try:
            dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
            return dt.strftime('%b %d, %I:%M %p')
        except:
            return iso_time

    def _is_live(self, commence_time: str) -> bool:
        """Check if event is currently live."""
        try:
            dt = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo)
            # Consider live if started within last 4 hours
            return dt <= now <= dt + timedelta(hours=4)
        except:
            return False

    def _generate_tags(self, event: Dict, odds_data: Dict, favorite_prob: float) -> List[str]:
        """Generate tags for filtering and categorization."""
        tags = ['sports']

        if favorite_prob:
            if favorite_prob > 80:
                tags.append('heavy_favorite')
            elif favorite_prob > 65:
                tags.append('favorite')
            elif favorite_prob < 55:
                tags.append('toss_up')

        if odds_data.get('spreads', {}).get('home_point'):
            tags.append('has_spread')

        if odds_data.get('totals', {}).get('point'):
            tags.append('has_totals')

        if len(event.get('bookmakers', [])) >= 5:
            tags.append('multi_book')

        if self._is_live(event.get('commence_time', '')):
            tags.append('live')

        return tags

    def get_sport_odds(self, sport_key: str) -> List[Dict]:
        """Get odds for a specific sport."""
        if sport_key not in self.SPORTS:
            logger.warning(f"Unknown sport key: {sport_key}")

        return self.fetch_data(sports=[sport_key], max_results=50)

    def get_upcoming_events(self, hours: int = 24) -> List[Dict]:
        """Get events starting within specified hours."""
        all_events = self.fetch_data(max_results=200)

        cutoff = datetime.utcnow() + timedelta(hours=hours)
        upcoming = []

        for event in all_events:
            if event.get('data_type') != 'sports_odds':
                continue

            try:
                commence = event.get('commence_time', '')
                dt = datetime.fromisoformat(commence.replace('Z', '+00:00'))
                if datetime.utcnow().replace(tzinfo=dt.tzinfo) <= dt <= cutoff.replace(tzinfo=dt.tzinfo):
                    upcoming.append(event)
            except:
                continue

        return upcoming

    def get_best_bets(self) -> List[Dict]:
        """Get events with significant line value or close matchups."""
        all_events = self.fetch_data(max_results=100)

        best = []
        for event in all_events:
            if event.get('data_type') != 'sports_odds':
                continue

            # Look for toss-ups (45-55% implied probability)
            home_prob = event.get('home_implied_prob')
            if home_prob and 45 <= home_prob <= 55:
                best.append(event)

        return best

    def get_api_usage(self) -> Dict:
        """Get current API usage stats."""
        return {
            'requests_remaining': self.requests_remaining,
            'requests_used': self.requests_used,
            'monthly_limit': 20000,
        }
