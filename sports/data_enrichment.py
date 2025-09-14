"""
Sports Data Enrichment Service

Fetches and stores comprehensive data from multiple sources:
- ESPN API: Team records, live scores, detailed stats
- The Odds API: Betting lines, spreads, totals
- TheSportsDB: Team logos, venue details
- WeatherAPI: Live weather for outdoor venues
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import Team, Game, BettingMarket, OddsLine, Sportsbook

logger = logging.getLogger(__name__)


class SportsDataEnricher:
    """Enriches sports data with comprehensive information from multiple sources"""

    def __init__(self):
        self.espn_base = "http://site.api.espn.com/apis/site/v2/sports"
        self.odds_api_key = getattr(settings, 'THE_ODDS_API_KEY', '')
        self.odds_base = "https://api.the-odds-api.com/v4/sports"
        self.sportsdb_base = "https://www.thesportsdb.com/api/v1/json/3"
        self.weather_api_key = getattr(settings, 'WEATHER_API_KEY', '')
        self.weather_base = "http://api.weatherapi.com/v1"
        self._team_logos_cache = {}

    def enrich_all_teams(self, league_abbr: str) -> Dict[str, Any]:
        """Fetch and store comprehensive team data"""
        results = {
            'teams_updated': 0,
            'logos_added': 0,
            'records_updated': 0,
            'errors': []
        }

        try:
            teams = Team.objects.filter(league__abbreviation=league_abbr)

            for team in teams:
                try:
                    # Fetch team record from ESPN (this also fetches logos)
                    record_data = self._fetch_team_record(team.name, league_abbr)
                    if record_data:
                        team.current_record = record_data
                        results['records_updated'] += 1

                    # Check if we got a logo from ESPN
                    if team.name in self._team_logos_cache:
                        logo_url = self._team_logos_cache[team.name]
                        if logo_url and logo_url != team.logo_url:
                            team.logo_url = logo_url
                            results['logos_added'] += 1
                    else:
                        # Fall back to TheSportsDB for logo
                        logo_url = self._fetch_team_logo(team.name, league_abbr)
                        if logo_url and logo_url != team.logo_url:
                            team.logo_url = logo_url
                            results['logos_added'] += 1

                    team.save()
                    results['teams_updated'] += 1

                except Exception as e:
                    error_msg = f"Error enriching team {team.name}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)

        except Exception as e:
            error_msg = f"Error fetching teams for {league_abbr}: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)

        return results

    def _fetch_team_logo(self, team_name: str, league: str) -> Optional[str]:
        """Fetch team logo from TheSportsDB"""
        try:
            # Map league to TheSportsDB format
            league_map = {
                'NFL': 'NFL',
                'NCAAF': 'NCAA Football',
                'NBA': 'NBA',
                'NCAAB': 'NCAA Basketball',
                'MLB': 'MLB',
                'NHL': 'NHL'
            }

            sportsdb_league = league_map.get(league.upper())
            if not sportsdb_league:
                return None

            # Search for team
            url = f"{self.sportsdb_base}/searchteams.php"
            params = {'t': team_name}
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                teams = data.get('teams', [])

                # Find matching team by league
                for team in teams:
                    if sportsdb_league in team.get('strLeague', ''):
                        logo = team.get('strTeamBadge') or team.get('strTeamLogo')
                        if logo:
                            # Add https if missing
                            if logo and not logo.startswith('http'):
                                logo = f"https://{logo}"
                            return logo

        except Exception as e:
            logger.warning(f"Could not fetch logo for {team_name}: {e}")

        return None

    def _fetch_team_record(self, team_name: str, league: str) -> Optional[Dict]:
        """Fetch team record from ESPN Teams API"""
        try:
            # First, we need to find the team's abbreviation
            # This is a simplified mapping - in production, you'd want a complete mapping
            team_abbr_map = {
                # NFL Teams
                'patriots': 'ne', 'bills': 'buf', 'dolphins': 'mia', 'jets': 'nyj',
                'ravens': 'bal', 'bengals': 'cin', 'browns': 'cle', 'steelers': 'pit',
                'texans': 'hou', 'colts': 'ind', 'jaguars': 'jax', 'titans': 'ten',
                'broncos': 'den', 'chiefs': 'kc', 'raiders': 'lv', 'chargers': 'lac',
                'cowboys': 'dal', 'giants': 'nyg', 'eagles': 'phi', 'commanders': 'wsh',
                'bears': 'chi', 'lions': 'det', 'packers': 'gb', 'vikings': 'min',
                'falcons': 'atl', 'panthers': 'car', 'saints': 'no', 'buccaneers': 'tb',
                'cardinals': 'ari', '49ers': 'sf', 'rams': 'lar', 'seahawks': 'sea',
                # NCAAF Teams (partial list - add more as needed)
                'ohio state': '194', 'buckeyes': '194',
                'michigan': '130', 'wolverines': '130',
                'alabama': '333', 'crimson tide': '333',
                'georgia': '61', 'bulldogs': '61',
                'lsu': '99', 'tigers': '99',
                'florida': '57', 'gators': '57',
                'notre dame': '87', 'fighting irish': '87',
                'texas a&m': '245', 'aggies': '245',
                'arkansas': '8', 'razorbacks': '8',
                'ole miss': '145', 'rebels': '145',
                'mississippi': '145',
                'wyoming': '2751', 'cowboys': '2751',
                'utah': '254', 'utes': '254',
                'vanderbilt': '238', 'commodores': '238',
                'south carolina': '2579', 'gamecocks': '2579',
                'illinois': '356', 'fighting illini': '356',
                'western michigan': '2711', 'broncos': '2711',
                'ohio': '195', 'bobcats': '195'
            }

            # Map league to ESPN format
            sport_map = {
                'NFL': 'football/nfl',
                'NCAAF': 'football/college-football',
                'NBA': 'basketball/nba',
                'NCAAB': 'basketball/mens-college-basketball',
                'MLB': 'baseball/mlb',
                'NHL': 'hockey/nhl'
            }

            sport_path = sport_map.get(league.upper())
            if not sport_path:
                return None

            # Find team abbreviation/ID
            team_key = team_name.lower()
            team_id = None

            # Try to find the team ID
            for key, value in team_abbr_map.items():
                if key in team_key or team_key in key:
                    team_id = value
                    break

            if not team_id:
                logger.warning(f"Could not find team ID for {team_name}")
                return None

            # Fetch team data from teams endpoint
            url = f"{self.espn_base}/{sport_path}/teams/{team_id}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                team_data = data.get('team', {})

                # Get logo URL while we're here
                logos = team_data.get('logos', [])
                if logos:
                    self._team_logos_cache[team_name] = logos[0].get('href')

                # Extract record
                record_data = team_data.get('record', {})
                items = record_data.get('items', [])

                for item in items:
                    if item.get('type') == 'total':
                        summary = item.get('summary', '0-0')
                        parts = summary.split('-')

                        record = {
                            'wins': int(parts[0]) if parts else 0,
                            'losses': int(parts[1]) if len(parts) > 1 else 0,
                            'record_string': summary
                        }

                        # Get additional stats
                        stats = item.get('stats', [])
                        for stat in stats:
                            stat_name = stat.get('name', '')
                            if stat_name == 'ties':
                                record['ties'] = int(stat.get('value', 0))
                            elif stat_name == 'winPercent':
                                record['win_pct'] = float(stat.get('value', 0))

                        logger.info(f"Fetched record for {team_name}: {record}")
                        return record

        except Exception as e:
            logger.warning(f"Could not fetch record for {team_name}: {e}")

        return None

    def enrich_game_odds(self, game_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Fetch and store betting odds for a game with caching"""
        results = {
            'odds_added': 0,
            'markets_created': 0,
            'errors': [],
            'from_cache': False
        }

        if not self.odds_api_key:
            results['errors'].append("The Odds API key not configured")
            return results

        try:
            game = Game.objects.get(id=game_id)

            # Check if we have recent odds (within 30 minutes for live games, 2 hours for upcoming)
            existing_markets = game.markets.filter(is_active=True)
            if existing_markets.exists() and not force_refresh:
                latest_update = existing_markets.latest('updated_at').updated_at
                time_since_update = timezone.now() - latest_update

                # Different cache durations based on game status
                if game.status in ['live', 'status_in_progress']:
                    cache_duration = timedelta(minutes=30)
                else:
                    cache_duration = timedelta(hours=2)

                if time_since_update < cache_duration:
                    results['from_cache'] = True
                    results['markets_created'] = existing_markets.count()
                    results['odds_added'] = OddsLine.objects.filter(
                        market__in=existing_markets
                    ).count()
                    logger.info(f"Using cached odds for game {game_id} (updated {time_since_update.total_seconds()/60:.1f} min ago)")
                    return results

            # Map league to The Odds API sport key
            sport_map = {
                'NFL': 'americanfootball_nfl',
                'NCAAF': 'americanfootball_ncaaf',
                'NBA': 'basketball_nba',
                'NCAAB': 'basketball_ncaab',
                'MLB': 'baseball_mlb',
                'NHL': 'icehockey_nhl'
            }

            sport_key = sport_map.get(game.league.abbreviation.upper())
            if not sport_key:
                results['errors'].append(f"Unsupported league: {game.league.abbreviation}")
                return results

            # Fetch odds
            url = f"{self.odds_base}/{sport_key}/odds"
            params = {
                'apiKey': self.odds_api_key,
                'regions': 'us',
                'markets': 'h2h,spreads,totals',
                'oddsFormat': 'american'
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                all_games = response.json()

                # Find matching game by teams
                for odds_game in all_games:
                    home_team = odds_game.get('home_team', '')
                    away_team = odds_game.get('away_team', '')

                    # Check if teams match (flexible matching)
                    if (self._teams_match(home_team, game.home_team.name) and
                        self._teams_match(away_team, game.away_team.name)):

                        # Process bookmakers
                        for bookmaker in odds_game.get('bookmakers', []):
                            self._save_bookmaker_odds(game, bookmaker)
                            results['odds_added'] += 1

                        results['markets_created'] += 1
                        break

            else:
                error_msg = f"The Odds API returned status {response.status_code}"
                logger.error(error_msg)
                results['errors'].append(error_msg)

        except Game.DoesNotExist:
            results['errors'].append(f"Game {game_id} not found")
        except Exception as e:
            error_msg = f"Error fetching odds: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)

        return results

    def _teams_match(self, name1: str, name2: str) -> bool:
        """Check if two team names match (flexible matching)"""
        # Simple containment check for now
        name1_lower = name1.lower()
        name2_lower = name2.lower()

        # Check if either name contains key parts of the other
        name1_parts = name1_lower.split()
        name2_parts = name2_lower.split()

        for part in name1_parts:
            if len(part) > 3 and part in name2_lower:
                return True

        for part in name2_parts:
            if len(part) > 3 and part in name1_lower:
                return True

        return False

    def _save_bookmaker_odds(self, game: Game, bookmaker_data: Dict):
        """Save bookmaker odds to database"""
        try:
            bookmaker_name = bookmaker_data.get('title', 'Unknown')

            # Get or create sportsbook
            sportsbook, _ = Sportsbook.objects.get_or_create(
                name=bookmaker_name,
                defaults={
                    'abbreviation': bookmaker_name[:20].lower().replace(' ', '_'),
                    'is_sharp': bookmaker_name.lower() in ['pinnacle', 'betcris'],
                    'is_active': True
                }
            )

            for market_data in bookmaker_data.get('markets', []):
                market_type = market_data.get('key', '')

                # Create or update market
                market, _ = BettingMarket.objects.update_or_create(
                    game=game,
                    market_type=market_type,
                    defaults={
                        'market_name': f"{market_type} - {bookmaker_name}",
                        'status': 'open',
                        'is_active': True
                    }
                )

                # Save outcomes as odds lines
                for outcome in market_data.get('outcomes', []):
                    # Determine if this is for home or away team
                    is_home = 'home' in outcome.get('name', '').lower()

                    OddsLine.objects.update_or_create(
                        market=market,
                        sportsbook=sportsbook,
                        defaults={
                            'home_odds': outcome.get('price', 0) if is_home and market_type == 'h2h' else None,
                            'away_odds': outcome.get('price', 0) if not is_home and market_type == 'h2h' else None,
                            'home_spread': outcome.get('point', 0) if is_home and market_type == 'spreads' else None,
                            'away_spread': outcome.get('point', 0) if not is_home and market_type == 'spreads' else None,
                            'total_line': outcome.get('point', 0) if market_type == 'totals' else None,
                            'over_odds': outcome.get('price', 0) if 'over' in outcome.get('name', '').lower() else None,
                            'under_odds': outcome.get('price', 0) if 'under' in outcome.get('name', '').lower() else None,
                            'is_current': True,
                            'is_active': True
                        }
                    )

        except Exception as e:
            logger.error(f"Error saving bookmaker odds: {e}")

    def enrich_game_weather(self, game_id: str) -> Dict[str, Any]:
        """Fetch and store weather data for outdoor venues"""
        results = {
            'weather_updated': False,
            'errors': []
        }

        if not self.weather_api_key:
            results['errors'].append("Weather API key not configured")
            return results

        try:
            game = Game.objects.get(id=game_id)

            # Only fetch weather for outdoor sports
            if game.league.sport_type not in ['nfl', 'ncaaf', 'mlb']:
                return results

            # Fetch weather for future and recently started games (within 4 hours)
            time_since_start = timezone.now() - game.scheduled_start
            if time_since_start.total_seconds() > 4 * 3600:  # More than 4 hours ago
                return results

            # Get venue location (simplified - would need geocoding in production)
            venue = game.venue_name
            if not venue:
                return results

            # Fetch weather - use current.json endpoint
            url = f"{self.weather_base}/current.json"
            params = {
                'key': self.weather_api_key,
                'q': venue
            }

            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()

                # Extract relevant weather data
                weather_data = {
                    'temperature': data.get('current', {}).get('temp_f'),
                    'condition': data.get('current', {}).get('condition', {}).get('text'),
                    'wind_mph': data.get('current', {}).get('wind_mph'),
                    'wind_direction': data.get('current', {}).get('wind_dir'),
                    'humidity': data.get('current', {}).get('humidity'),
                    'precipitation': data.get('current', {}).get('precip_in'),
                    'last_updated': datetime.now().isoformat()
                }

                game.weather_data = weather_data
                game.save()
                results['weather_updated'] = True

        except Game.DoesNotExist:
            results['errors'].append(f"Game {game_id} not found")
        except Exception as e:
            error_msg = f"Error fetching weather: {str(e)}"
            logger.warning(error_msg)
            results['errors'].append(error_msg)

        return results

    def enrich_league_odds_batch(self, league_abbr: str) -> Dict[str, Any]:
        """Batch enrich odds for all games in a league with a single API call"""
        results = {
            'games_enriched': 0,
            'odds_added': 0,
            'api_calls': 0,
            'from_cache': 0,
            'errors': []
        }

        if not self.odds_api_key:
            results['errors'].append("The Odds API key not configured")
            return results

        try:
            # Map league to The Odds API sport key
            sport_map = {
                'NFL': 'americanfootball_nfl',
                'NCAAF': 'americanfootball_ncaaf',
                'NBA': 'basketball_nba',
                'NCAAB': 'basketball_ncaab',
                'MLB': 'baseball_mlb',
                'NHL': 'icehockey_nhl'
            }

            sport_key = sport_map.get(league_abbr.upper())
            if not sport_key:
                results['errors'].append(f"Unsupported league: {league_abbr}")
                return results

            # Fetch ALL odds for this sport in one call
            url = f"{self.odds_base}/{sport_key}/odds"
            params = {
                'apiKey': self.odds_api_key,
                'regions': 'us',
                'markets': 'h2h,spreads,totals',
                'oddsFormat': 'american'
            }

            logger.info(f"Fetching batch odds for {league_abbr}...")
            response = requests.get(url, params=params, timeout=10)
            results['api_calls'] = 1

            if response.status_code == 200:
                all_odds_games = response.json()
                logger.info(f"Got {len(all_odds_games)} games with odds from API")

                # Get all games for this league
                games = Game.objects.filter(
                    league__abbreviation=league_abbr.upper(),
                    status__in=['scheduled', 'status_scheduled', 'live', 'status_in_progress', 'status_end_period']
                ).select_related('home_team', 'away_team')

                # Process each game
                for game in games:
                    # Check if game has recent odds
                    existing_markets = game.markets.filter(is_active=True)
                    if existing_markets.exists():
                        latest_update = existing_markets.latest('updated_at').updated_at
                        time_since_update = timezone.now() - latest_update

                        cache_duration = timedelta(minutes=30) if game.status in ['live', 'status_in_progress'] else timedelta(hours=2)

                        if time_since_update < cache_duration:
                            results['from_cache'] += 1
                            continue

                    # Find matching odds data
                    for odds_game in all_odds_games:
                        if (self._teams_match(odds_game.get('home_team', ''), game.home_team.name) and
                            self._teams_match(odds_game.get('away_team', ''), game.away_team.name)):

                            # Process bookmakers
                            for bookmaker in odds_game.get('bookmakers', []):
                                self._save_bookmaker_odds(game, bookmaker)
                                results['odds_added'] += 1

                            results['games_enriched'] += 1
                            break

                logger.info(f"Enriched {results['games_enriched']} games, {results['from_cache']} from cache")

            else:
                error_msg = f"The Odds API returned status {response.status_code}"
                logger.error(error_msg)
                results['errors'].append(error_msg)

        except Exception as e:
            error_msg = f"Error enriching league odds: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)

        return results

    def enrich_all_games(self, league_abbr: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Enrich all games with complete data"""
        results = {
            'games_enriched': 0,
            'odds_added': 0,
            'weather_added': 0,
            'errors': []
        }

        try:
            # Get games to enrich
            games_query = Game.objects.filter(league__abbreviation=league_abbr)

            if date:
                target_date = datetime.strptime(date, '%Y-%m-%d').date()
                games_query = games_query.filter(
                    scheduled_start__date=target_date
                )
            else:
                # Default to next 7 days
                end_date = timezone.now() + timedelta(days=7)
                games_query = games_query.filter(
                    scheduled_start__lte=end_date
                )

            games = games_query.all()

            for game in games:
                try:
                    # Enrich with odds
                    odds_result = self.enrich_game_odds(str(game.id))
                    if odds_result['odds_added'] > 0:
                        results['odds_added'] += odds_result['odds_added']

                    # Enrich with weather (for outdoor sports)
                    weather_result = self.enrich_game_weather(str(game.id))
                    if weather_result['weather_updated']:
                        results['weather_added'] += 1

                    results['games_enriched'] += 1

                except Exception as e:
                    error_msg = f"Error enriching game {game.id}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)

        except Exception as e:
            error_msg = f"Error enriching games: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)

        return results


# Singleton instance
data_enricher = SportsDataEnricher()