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

# Try zoneinfo (Python 3.9+), fall back to pytz
try:
    from zoneinfo import ZoneInfo
    MST = ZoneInfo('America/Denver')  # Mountain Time (handles DST automatically)
except ImportError:
    import pytz
    MST = pytz.timezone('America/Denver')

logger = logging.getLogger(__name__)


class TheOddsSpider:
    """
    Spider for The Odds API - sports betting odds aggregator.
    Fetches odds from 40+ bookmakers for major sports.
    """

    name = "theodds"
    base_url = "https://api.the-odds-api.com/v4"

    # Comprehensive sports coverage (API sport keys)
    SPORTS = {
        # ===== US MAJOR LEAGUES =====
        'americanfootball_nfl': {'name': 'NFL', 'category': 'american_football', 'priority': 1},
        'basketball_nba': {'name': 'NBA', 'category': 'basketball', 'priority': 1},
        'baseball_mlb': {'name': 'MLB', 'category': 'baseball', 'priority': 1},
        'icehockey_nhl': {'name': 'NHL', 'category': 'hockey', 'priority': 1},

        # ===== FUTURES / CHAMPIONSHIP WINNERS =====
        'americanfootball_nfl_super_bowl_winner': {'name': 'Super Bowl Winner', 'category': 'futures', 'priority': 1},
        'basketball_nba_championship_winner': {'name': 'NBA Championship', 'category': 'futures', 'priority': 1},
        'baseball_mlb_world_series_winner': {'name': 'World Series Winner', 'category': 'futures', 'priority': 1},
        'icehockey_nhl_championship_winner': {'name': 'Stanley Cup Winner', 'category': 'futures', 'priority': 1},
        'americanfootball_ncaaf_championship_winner': {'name': 'CFP Champion', 'category': 'futures', 'priority': 2},
        'basketball_ncaab_championship_winner': {'name': 'March Madness Winner', 'category': 'futures', 'priority': 2},

        # ===== NBA EVENTS =====
        'basketball_nba_all_stars': {'name': 'NBA All-Stars', 'category': 'basketball', 'priority': 1},

        # ===== COLLEGE SPORTS =====
        'americanfootball_ncaaf': {'name': 'NCAAF', 'category': 'american_football', 'priority': 1},
        'basketball_ncaab': {'name': 'NCAAB', 'category': 'basketball', 'priority': 1},

        # ===== SOCCER - TOP LEAGUES =====
        'soccer_epl': {'name': 'English Premier League', 'category': 'soccer', 'priority': 1},
        'soccer_spain_la_liga': {'name': 'La Liga', 'category': 'soccer', 'priority': 1},
        'soccer_germany_bundesliga': {'name': 'Bundesliga', 'category': 'soccer', 'priority': 2},
        'soccer_italy_serie_a': {'name': 'Serie A', 'category': 'soccer', 'priority': 2},
        'soccer_france_ligue_one': {'name': 'Ligue 1', 'category': 'soccer', 'priority': 2},
        'soccer_usa_mls': {'name': 'MLS', 'category': 'soccer', 'priority': 1},
        'soccer_uefa_champs_league': {'name': 'Champions League', 'category': 'soccer', 'priority': 1},
        'soccer_uefa_europa_league': {'name': 'Europa League', 'category': 'soccer', 'priority': 2},

        # ===== SOCCER - ADDITIONAL LEAGUES =====
        'soccer_england_league1': {'name': 'English League One', 'category': 'soccer', 'priority': 3},
        'soccer_england_efl_cup': {'name': 'EFL Cup', 'category': 'soccer', 'priority': 3},
        'soccer_brazil_campeonato': {'name': 'Brasileirão', 'category': 'soccer', 'priority': 3},
        'soccer_mexico_ligamx': {'name': 'Liga MX', 'category': 'soccer', 'priority': 2},
        'soccer_australia_aleague': {'name': 'A-League', 'category': 'soccer', 'priority': 3},

        # ===== COMBAT SPORTS =====
        'mma_mixed_martial_arts': {'name': 'UFC/MMA', 'category': 'mma', 'priority': 1},
        'boxing_boxing': {'name': 'Boxing', 'category': 'boxing', 'priority': 2},

        # ===== TENNIS =====
        'tennis_atp_aus_open': {'name': 'Australian Open (ATP)', 'category': 'tennis', 'priority': 2},
        'tennis_wta_aus_open': {'name': 'Australian Open (WTA)', 'category': 'tennis', 'priority': 2},
        'tennis_atp_french_open': {'name': 'French Open (ATP)', 'category': 'tennis', 'priority': 2},
        'tennis_wta_french_open': {'name': 'French Open (WTA)', 'category': 'tennis', 'priority': 2},
        'tennis_atp_wimbledon': {'name': 'Wimbledon (ATP)', 'category': 'tennis', 'priority': 2},
        'tennis_wta_wimbledon': {'name': 'Wimbledon (WTA)', 'category': 'tennis', 'priority': 2},
        'tennis_atp_us_open': {'name': 'US Open (ATP)', 'category': 'tennis', 'priority': 2},
        'tennis_wta_us_open': {'name': 'US Open (WTA)', 'category': 'tennis', 'priority': 2},

        # ===== GOLF =====
        'golf_masters_tournament_winner': {'name': 'Masters', 'category': 'golf', 'priority': 2},
        'golf_pga_championship_winner': {'name': 'PGA Championship', 'category': 'golf', 'priority': 2},
        'golf_us_open_winner': {'name': 'US Open (Golf)', 'category': 'golf', 'priority': 2},
        'golf_the_open_championship_winner': {'name': 'The Open', 'category': 'golf', 'priority': 2},

        # ===== POLITICS (when available) =====
        'politics_us_presidential_election_winner': {'name': 'US Presidential Election', 'category': 'politics', 'priority': 1},

        # ===== OTHER SPORTS =====
        'rugbyleague_nrl': {'name': 'NRL (Rugby)', 'category': 'rugby', 'priority': 3},
        'cricket_ipl': {'name': 'IPL (Cricket)', 'category': 'cricket', 'priority': 3},
        'cricket_test_match': {'name': 'Test Cricket', 'category': 'cricket', 'priority': 3},
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

    # Market types - expanded coverage
    MARKETS = ['h2h', 'spreads', 'totals']  # Head-to-head, point spreads, over/under
    MARKETS_FUTURES = ['outrights']  # For championship/winner markets
    MARKETS_PROPS = ['player_pass_tds', 'player_rush_yds', 'player_receptions']  # Player props (NFL example)

    # Regions for odds comparison (us is primary, others for arbitrage detection)
    REGIONS = ['us']  # Default region
    REGIONS_EXTENDED = ['us', 'us2', 'uk', 'eu', 'au']  # For comprehensive odds comparison

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

    def fetch_data(self, sports: List[str] = None, max_results: int = 200,
                   include_futures: bool = True, max_priority: int = 2,
                   extended_regions: bool = False) -> List[Dict[str, Any]]:
        """
        Main entry point - fetch odds for specified sports with expanded coverage.

        Args:
            sports: List of sport keys (e.g., ['americanfootball_nfl', 'basketball_nba'])
                   If None, fetches sports based on max_priority
            max_results: Maximum number of events to return (default 200 for broader coverage)
            include_futures: Whether to include futures/championship winner markets
            max_priority: Maximum priority level to include (1=core, 2=expanded, 3=all)
            extended_regions: Whether to fetch odds from multiple regions (more API calls)

        Returns:
            List of normalized event data with odds
        """
        results = []

        # Default to priority 1 and 2 sports if none specified
        if sports is None:
            sports = [k for k, v in self.SPORTS.items() if v.get('priority', 3) <= max_priority]

        # First, get list of in-season sports
        active_sports = self._get_active_sports()
        if not active_sports:
            logger.warning("Could not fetch active sports list")
            active_sports = sports  # Fall back to requested sports

        # Filter to only active sports from our list
        sports_to_fetch = [s for s in sports if s in active_sports]

        # Identify futures markets (need different market type)
        futures_sports = [s for s in sports_to_fetch if 'winner' in s or 'championship' in s]
        regular_sports = [s for s in sports_to_fetch if s not in futures_sports]

        logger.info(f"TheOddsSpider fetching {len(regular_sports)} regular sports, {len(futures_sports)} futures markets")

        # Fetch regular sports
        for sport_key in regular_sports:
            if len(results) >= max_results:
                break

            sport_info = self.SPORTS.get(sport_key, {})
            regions = self.REGIONS_EXTENDED if extended_regions else self.REGIONS
            events = self._fetch_sport_odds(sport_key, regions=regions)

            if events:
                for event in events:
                    if len(results) >= max_results:
                        break

                    normalized = self._normalize_event(event, sport_key, sport_info)
                    if normalized:
                        results.append(normalized)

        # Fetch futures/championship markets
        if include_futures:
            for sport_key in futures_sports:
                if len(results) >= max_results:
                    break

                sport_info = self.SPORTS.get(sport_key, {})
                events = self._fetch_futures_odds(sport_key)

                if events:
                    for event in events:
                        if len(results) >= max_results:
                            break

                        normalized = self._normalize_futures_event(event, sport_key, sport_info)
                        if normalized:
                            results.append(normalized)

        # Add metadata
        results.append({
            'data_type': 'api_status',
            'spider_name': self.name,
            'requests_remaining': self.requests_remaining,
            'requests_used': self.requests_used,
            'sports_fetched': len(sports_to_fetch),
            'futures_fetched': len(futures_sports) if include_futures else 0,
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

    def _fetch_sport_odds(self, sport_key: str, regions: List[str] = None) -> List[Dict]:
        """Fetch odds for a specific sport."""
        if regions is None:
            regions = self.REGIONS

        params = {
            'regions': ','.join(regions),
            'markets': ','.join(self.MARKETS),
            'oddsFormat': 'american',
            'dateFormat': 'iso',
        }

        data = self._make_request(f'sports/{sport_key}/odds', params)
        return data if data else []

    def _fetch_futures_odds(self, sport_key: str) -> List[Dict]:
        """Fetch futures/outrights odds for championship markets."""
        params = {
            'regions': ','.join(self.REGIONS),
            'markets': ','.join(self.MARKETS_FUTURES),
            'oddsFormat': 'american',
            'dateFormat': 'iso',
        }

        data = self._make_request(f'sports/{sport_key}/odds', params)
        return data if data else []

    def _normalize_futures_event(self, event: Dict, sport_key: str, sport_info: Dict) -> Optional[Dict]:
        """Normalize futures/championship market data."""
        try:
            # Futures markets have different structure - usually just outrights
            bookmakers = event.get('bookmakers', [])
            if not bookmakers:
                return None

            # Get all outcomes from first bookmaker
            outcomes = []
            best_bookmaker = None
            for bm in bookmakers:
                if bm.get('key') in self.PREFERRED_BOOKMAKERS:
                    for market in bm.get('markets', []):
                        if market.get('key') == 'outrights':
                            outcomes = market.get('outcomes', [])
                            best_bookmaker = bm.get('key')
                            break
                    if outcomes:
                        break

            # Fallback to first bookmaker
            if not outcomes and bookmakers:
                for market in bookmakers[0].get('markets', []):
                    if market.get('key') == 'outrights':
                        outcomes = market.get('outcomes', [])
                        best_bookmaker = bookmakers[0].get('key')
                        break

            if not outcomes:
                return None

            # Sort by odds (favorites first)
            sorted_outcomes = sorted(outcomes, key=lambda x: x.get('price', 0))

            # Top contenders
            top_contenders = []
            for outcome in sorted_outcomes[:10]:
                prob = self._american_to_probability(outcome.get('price'))
                top_contenders.append({
                    'name': outcome.get('name'),
                    'odds': outcome.get('price'),
                    'implied_prob': round(prob * 100, 1) if prob else None,
                })

            # Find favorite
            if top_contenders:
                favorite = top_contenders[0]
            else:
                favorite = {'name': None, 'odds': None, 'implied_prob': None}

            return {
                'data_type': 'futures_odds',
                'spider_name': self.name,
                'source_platform': 'theodds',
                'source_url': f"https://the-odds-api.com/sports/{sport_key}",

                # Market info
                'event_id': event.get('id'),
                'sport_key': sport_key,
                'sport_name': sport_info.get('name', sport_key),
                'category': 'futures',
                'market_type': 'championship_winner',
                'title': sport_info.get('name', sport_key),

                # Favorite
                'favorite': favorite.get('name'),
                'favorite_odds': favorite.get('odds'),
                'favorite_probability': favorite.get('implied_prob'),

                # All contenders
                'contenders': top_contenders,
                'total_outcomes': len(outcomes),

                # Metadata
                'bookmaker_count': len(bookmakers),
                'best_bookmaker': best_bookmaker,
                'fetched_at': datetime.utcnow().isoformat(),
                'tags': ['futures', 'championship', sport_info.get('category', 'sports')],
            }

        except Exception as e:
            logger.error(f"Error normalizing futures event: {str(e)}")
            return None

    def _normalize_event(self, event: Dict, sport_key: str, sport_info: Dict) -> Optional[Dict]:
        """Normalize event data to standard format."""
        try:
            home_team = event.get('home_team', 'Unknown')
            away_team = event.get('away_team', 'Unknown')
            commence_time = event.get('commence_time', '')

            # Parse odds from bookmakers - pass team names for accurate matching
            odds_data = self._extract_best_odds(event.get('bookmakers', []), home_team, away_team)

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

                # Per-bookmaker odds for arbitrage detection
                'h2h_odds': odds_data.get('all_bookmaker_odds', []),

                # Metadata
                'fetched_at': datetime.utcnow().isoformat(),
                'tags': self._generate_tags(event, odds_data, favorite_prob),
            }

        except Exception as e:
            logger.error(f"Error normalizing event: {str(e)}")
            return None

    def _extract_best_odds(self, bookmakers: List[Dict], home_team: str = None, away_team: str = None) -> Dict:
        """Extract best odds from bookmaker data, preferring US books.

        Args:
            bookmakers: List of bookmaker data from API
            home_team: The actual home team name (for accurate matching)
            away_team: The actual away team name (for accurate matching)
        """
        result = {
            'h2h': {},
            'spreads': {},
            'totals': {},
            'best_bookmaker': None,
            'all_bookmaker_odds': [],  # For arbitrage detection
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

        # Collect ALL bookmaker h2h odds for arbitrage detection
        # CRITICAL: Match by team name, not by order (bookmakers list teams differently)
        for bookmaker in bookmakers:
            book_key = bookmaker.get('key', 'unknown')
            book_title = bookmaker.get('title', book_key)

            for market in bookmaker.get('markets', []):
                if market.get('key') == 'h2h':
                    outcomes = market.get('outcomes', [])
                    book_odds = {
                        'bookmaker': book_title,
                        'bookmaker_key': book_key,
                    }

                    for outcome in outcomes:
                        name = outcome.get('name', '')
                        price = outcome.get('price')

                        if 'Draw' in name or name == 'Draw':
                            book_odds['draw_odds'] = price
                        elif home_team and self._teams_match(name, home_team):
                            # Match by team name (fuzzy)
                            book_odds['home_odds'] = price
                            book_odds['home_team'] = name
                        elif away_team and self._teams_match(name, away_team):
                            # Match by team name (fuzzy)
                            book_odds['away_odds'] = price
                            book_odds['away_team'] = name
                        elif not home_team or not away_team:
                            # Fallback to order-based if team names not provided
                            if 'home_odds' not in book_odds:
                                book_odds['home_odds'] = price
                                book_odds['home_team'] = name
                            elif 'away_odds' not in book_odds:
                                book_odds['away_odds'] = price
                                book_odds['away_team'] = name

                    if book_odds.get('home_odds') and book_odds.get('away_odds'):
                        result['all_bookmaker_odds'].append(book_odds)
                    break  # Only one h2h market per bookmaker

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
                            # Match to home/away/draw by team name (fuzzy)
                            if 'Draw' in name or name == 'Draw':
                                result['h2h']['draw_odds'] = price
                            elif home_team and self._teams_match(name, home_team):
                                result['h2h']['home_odds'] = price
                                result['h2h']['home_team'] = name
                            elif away_team and self._teams_match(name, away_team):
                                result['h2h']['away_odds'] = price
                                result['h2h']['away_team'] = name
                            elif not home_team or not away_team:
                                # Fallback to order-based
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
        except Exception as _e:
            logger.warning(
                "theodds_spider._american_to_probability: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return None

    def _teams_match(self, outcome_name: str, team_name: str) -> bool:
        """
        Check if outcome name matches team name using fuzzy matching.

        Handles cases like:
        - "Los Angeles Chargers" vs "LA Chargers"
        - "BYU Cougars" vs "BYU"
        - "Georgia Tech Yellow Jackets" vs "Georgia Tech"
        """
        if not outcome_name or not team_name:
            return False

        # Exact match
        if outcome_name == team_name:
            return True

        # Normalize for comparison
        outcome_lower = outcome_name.lower().strip()
        team_lower = team_name.lower().strip()

        # One contains the other
        if outcome_lower in team_lower or team_lower in outcome_lower:
            return True

        # Split into words and check for significant overlap
        outcome_words = set(outcome_lower.split())
        team_words = set(team_lower.split())

        # Remove common filler words
        filler_words = {'the', 'fc', 'sc', 'cf', 'afc', 'united'}
        outcome_words -= filler_words
        team_words -= filler_words

        # If at least 2 words match, or 1 word matches and it's a major identifier
        common_words = outcome_words & team_words
        if len(common_words) >= 2:
            return True

        # Check for abbreviation matching (LA = Los Angeles, NY = New York, etc.)
        abbrev_map = {
            'la': 'los angeles',
            'ny': 'new york',
            'sf': 'san francisco',
            'tb': 'tampa bay',
            'gb': 'green bay',
            'kc': 'kansas city',
            'lv': 'las vegas',
            'ne': 'new england',
        }

        for abbrev, full in abbrev_map.items():
            if abbrev in outcome_lower and full in team_lower:
                return True
            if full in outcome_lower and abbrev in team_lower:
                return True

        return False

    def _format_time(self, iso_time: str) -> str:
        """Format ISO time to readable string in MST (Mountain Time)."""
        try:
            # Parse UTC time
            dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
            # Convert to Mountain Time
            dt_mst = dt.astimezone(MST)
            return dt_mst.strftime('%b %d, %I:%M %p MST')
        except:
            return iso_time

    def _is_live(self, commence_time: str) -> bool:
        """Check if event is currently live."""
        try:
            dt = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo)
            # Consider live if started within last 4 hours
            return dt <= now <= dt + timedelta(hours=4)
        except Exception as _e:
            logger.warning(
                "theodds_spider._is_live: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
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

    def fetch_scores(self, sport_key: str, days_from: int = 3) -> List[Dict]:
        """
        Fetch game scores (completed and in-progress) from The Odds API.

        Uses the /v4/sports/{sport}/scores endpoint which returns the same
        event_id as odds data — no fuzzy team matching needed for joining.

        Args:
            sport_key: Sport key (e.g., 'basketball_nba')
            days_from: How many days back to fetch (max 3)

        Returns:
            List of events with scores (completed + live):
            [{event_id, home_team, away_team, home_score, away_score, completed}, ...]
        """
        params = {
            'daysFrom': min(days_from, 3),
            'dateFormat': 'iso',
        }

        data = self._make_request(f'sports/{sport_key}/scores', params)
        if not data:
            return []

        results = []
        for event in data:
            scores = event.get('scores', [])
            if not scores or len(scores) < 2:
                continue

            # Build score lookup by team name
            score_map = {s['name']: int(s['score']) for s in scores if s.get('score') is not None}

            home_team = event.get('home_team', '')
            away_team = event.get('away_team', '')
            home_score = score_map.get(home_team)
            away_score = score_map.get(away_team)

            if home_score is None or away_score is None:
                continue

            results.append({
                'event_id': event.get('id'),
                'sport_key': sport_key,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'completed': event.get('completed', False),
                'commence_time': event.get('commence_time', ''),
                'last_updated': event.get('last_updated'),
            })

        completed = sum(1 for r in results if r['completed'])
        live = len(results) - completed
        logger.info(f"TheOddsSpider fetched {len(results)} scores for {sport_key} ({completed} final, {live} live)")
        return results

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
