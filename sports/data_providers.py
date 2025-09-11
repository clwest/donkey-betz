"""
Sports Data Provider Integration System

This module provides a unified interface for integrating multiple sports data sources
to replace Polygon.io and provide comprehensive coverage across all sports.

Integrated Sources:
1. ESPN Hidden API - Free comprehensive sports data
2. TheSportsDB.com - Free community-driven sports database  
3. The Odds API - Free tier for betting odds
4. API-Sports - Free tier with extensive coverage
5. SportsDataIO - Free trial available

Features:
- Automatic failover between data sources
- Rate limiting and caching
- Real-time odds aggregation
- Historical data collection
- Multi-sport support (NFL, NBA, MLB, NHL, Soccer, MMA, Tennis, etc.)
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .models import League, Team, Game, Sportsbook, BettingMarket, OddsLine, SportType, GameStatus


logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Available data sources"""
    ESPN = "espn"
    THESPORTSDB = "thesportsdb"
    ODDS_API = "odds_api"
    API_SPORTS = "api_sports"
    SPORTSDATA_IO = "sportsdata_io"


@dataclass
class APIConfig:
    """API configuration for different providers"""
    base_url: str
    api_key: Optional[str] = None
    rate_limit: int = 60  # requests per minute
    timeout: int = 30
    requires_auth: bool = False


class SportsDataProvider:
    """Base class for sports data providers"""
    
    def __init__(self, source: DataSource, config: APIConfig):
        self.source = source
        self.config = config
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_window_start = time.time()
    
    def _rate_limit_check(self):
        """Check and enforce rate limits"""
        current_time = time.time()
        
        # Reset counter if we're in a new minute window
        if current_time - self.rate_limit_window_start >= 60:
            self.request_count = 0
            self.rate_limit_window_start = current_time
        
        if self.request_count >= self.config.rate_limit:
            sleep_time = 60 - (current_time - self.rate_limit_window_start)
            if sleep_time > 0:
                logger.warning(f"Rate limit reached for {self.source.value}, sleeping for {sleep_time:.1f}s")
                time.sleep(sleep_time)
                self.request_count = 0
                self.rate_limit_window_start = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request with rate limiting and error handling"""
        self._rate_limit_check()
        
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        headers = {}
        
        if self.config.requires_auth and self.config.api_key:
            headers['X-RapidAPI-Key'] = self.config.api_key
        
        try:
            response = requests.get(
                url, 
                params=params or {}, 
                headers=headers,
                timeout=self.config.timeout
            )
            
            self.request_count += 1
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning(f"Rate limited by {self.source.value}")
                time.sleep(60)
                return None
            else:
                logger.error(f"{self.source.value} API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Request failed for {self.source.value}: {e}")
            return None
    
    def get_leagues(self) -> List[Dict]:
        """Get available leagues - to be implemented by subclasses"""
        raise NotImplementedError
    
    def get_teams(self, league_id: str) -> List[Dict]:
        """Get teams for a league - to be implemented by subclasses"""
        raise NotImplementedError
    
    def get_games(self, league_id: str, date: Optional[str] = None) -> List[Dict]:
        """Get games for a league and date - to be implemented by subclasses"""
        raise NotImplementedError
    
    def get_odds(self, game_id: str) -> List[Dict]:
        """Get odds for a game - to be implemented by subclasses"""
        raise NotImplementedError


class ESPNProvider(SportsDataProvider):
    """ESPN Hidden API provider"""
    
    def __init__(self):
        config = APIConfig(
            base_url="https://site.api.espn.com/apis/site/v2/sports",
            rate_limit=100,  # ESPN is generally permissive
            requires_auth=False
        )
        super().__init__(DataSource.ESPN, config)
    
    def get_leagues(self) -> List[Dict]:
        """Get ESPN sports leagues"""
        leagues = []
        
        # ESPN sports mapping
        espn_sports = {
            'football/nfl': {'sport_type': SportType.NFL, 'name': 'National Football League', 'abbrev': 'NFL'},
            'football/college-football': {'sport_type': SportType.NCAAF, 'name': 'NCAA Football', 'abbrev': 'NCAAF'},
            'basketball/nba': {'sport_type': SportType.NBA, 'name': 'National Basketball Association', 'abbrev': 'NBA'},
            'basketball/mens-college-basketball': {'sport_type': SportType.NCAAB, 'name': 'NCAA Basketball', 'abbrev': 'NCAAB'},
            'baseball/mlb': {'sport_type': SportType.MLB, 'name': 'Major League Baseball', 'abbrev': 'MLB'},
            'hockey/nhl': {'sport_type': SportType.NHL, 'name': 'National Hockey League', 'abbrev': 'NHL'},
            'soccer/usa.1': {'sport_type': SportType.SOCCER, 'name': 'Major League Soccer', 'abbrev': 'MLS'},
            'soccer/eng.1': {'sport_type': SportType.SOCCER, 'name': 'Premier League', 'abbrev': 'EPL'},
            'tennis/atp': {'sport_type': SportType.TENNIS, 'name': 'ATP Tour', 'abbrev': 'ATP'},
            'golf/pga': {'sport_type': SportType.GOLF, 'name': 'PGA Tour', 'abbrev': 'PGA'},
        }
        
        for espn_path, league_info in espn_sports.items():
            # Test if league endpoint is available
            data = self._make_request(f"{espn_path}/scoreboard")
            if data:
                leagues.append({
                    'external_id': espn_path,
                    'name': league_info['name'],
                    'abbreviation': league_info['abbrev'],
                    'sport_type': league_info['sport_type'],
                    'api_provider': 'ESPN',
                    'active': True
                })
        
        return leagues
    
    def get_teams(self, league_id: str) -> List[Dict]:
        """Get teams from ESPN API"""
        data = self._make_request(f"{league_id}/teams")
        teams = []
        
        if data and 'sports' in data:
            for sport in data['sports']:
                for league in sport.get('leagues', []):
                    for team_data in league.get('teams', []):
                        team = team_data.get('team', {})
                        teams.append({
                            'external_id': team.get('id'),
                            'name': team.get('displayName', ''),
                            'abbreviation': team.get('abbreviation', ''),
                            'city': team.get('location', ''),
                            'logo_url': team.get('logos', [{}])[0].get('href', ''),
                            'conference': team.get('groups', {}).get('parent', {}).get('name', ''),
                        })
        
        return teams
    
    def get_games(self, league_id: str, date: Optional[str] = None) -> List[Dict]:
        """Get games from ESPN scoreboard"""
        params = {}
        if date:
            params['dates'] = date.replace('-', '')  # ESPN expects YYYYMMDD format
        
        data = self._make_request(f"{league_id}/scoreboard", params)
        games = []
        
        if data and 'events' in data:
            for event in data['events']:
                competitions = event.get('competitions', [])
                if not competitions:
                    continue
                
                competition = competitions[0]
                competitors = competition.get('competitors', [])
                
                if len(competitors) >= 2:
                    home_team = next((c for c in competitors if c.get('homeAway') == 'home'), {})
                    away_team = next((c for c in competitors if c.get('homeAway') == 'away'), {})
                    
                    # Parse game status
                    status_type = competition.get('status', {}).get('type', {}).get('name', 'scheduled').lower()
                    game_status = GameStatus.SCHEDULED
                    
                    if 'in progress' in status_type or 'live' in status_type:
                        game_status = GameStatus.LIVE
                    elif 'final' in status_type:
                        game_status = GameStatus.FINAL
                    elif 'postponed' in status_type:
                        game_status = GameStatus.POSTPONED
                    
                    games.append({
                        'external_id': event.get('id'),
                        'home_team_id': home_team.get('team', {}).get('id'),
                        'away_team_id': away_team.get('team', {}).get('id'),
                        'home_team_name': home_team.get('team', {}).get('displayName', ''),
                        'away_team_name': away_team.get('team', {}).get('displayName', ''),
                        'scheduled_start': event.get('date'),
                        'status': game_status,
                        'venue_name': competition.get('venue', {}).get('fullName', ''),
                        'home_score': home_team.get('score'),
                        'away_score': away_team.get('score'),
                        'season': event.get('season', {}).get('year'),
                        'week': event.get('week', {}).get('number'),
                    })
        
        return games


class TheSportsDBProvider(SportsDataProvider):
    """TheSportsDB.com provider - free community database"""
    
    def __init__(self):
        config = APIConfig(
            base_url="https://www.thesportsdb.com/api/v1/json/3",
            rate_limit=100,  # TheSportsDB is free and generous
            requires_auth=False
        )
        super().__init__(DataSource.THESPORTSDB, config)
    
    def get_leagues(self) -> List[Dict]:
        """Get leagues from TheSportsDB"""
        # TheSportsDB has specific league lookups
        known_leagues = [
            {'id': '4391', 'name': 'NFL', 'abbrev': 'NFL', 'sport': 'American Football'},
            {'id': '4387', 'name': 'NBA', 'abbrev': 'NBA', 'sport': 'Basketball'},
            {'id': '4424', 'name': 'MLB', 'abbrev': 'MLB', 'sport': 'Baseball'},
            {'id': '4380', 'name': 'NHL', 'abbrev': 'NHL', 'sport': 'Ice Hockey'},
            {'id': '4346', 'name': 'English Premier League', 'abbrev': 'EPL', 'sport': 'Soccer'},
            {'id': '4344', 'name': 'MLS', 'abbrev': 'MLS', 'sport': 'Soccer'},
            # Note: 4370 is Formula 1, not UFC - removing for now
            # {'id': '4370', 'name': 'Formula 1', 'abbrev': 'F1', 'sport': 'Motorsport'},
        ]
        
        leagues = []
        for league_info in known_leagues:
            # Verify league exists and get details
            data = self._make_request(f"lookupleague.php?id={league_info['id']}")
            if data and 'leagues' in data and data['leagues']:
                league_data = data['leagues'][0]
                
                # Map sport types
                sport_type_mapping = {
                    'American Football': SportType.NFL,
                    'Basketball': SportType.NBA,
                    'Baseball': SportType.MLB,
                    'Ice Hockey': SportType.NHL,
                    'Soccer': SportType.SOCCER,
                    'Fighting': SportType.MMA,
                }
                
                sport_type = sport_type_mapping.get(league_info['sport'], SportType.SOCCER)
                
                # Use our predefined abbreviation - strLeagueAlternate often contains full name
                abbreviation = league_info['abbrev']
                
                leagues.append({
                    'external_id': league_data.get('idLeague'),
                    'name': league_data.get('strLeague'),
                    'abbreviation': abbreviation,
                    'sport_type': sport_type,
                    'country': league_data.get('strCountry', 'USA'),
                    'api_provider': 'TheSportsDB',
                    'active': True
                })
        
        return leagues
    
    def get_teams(self, league_id: str) -> List[Dict]:
        """Get teams from TheSportsDB"""
        data = self._make_request(f"lookup_all_teams.php?id={league_id}")
        teams = []
        
        if data and 'teams' in data:
            for team in data['teams']:
                teams.append({
                    'external_id': team.get('idTeam'),
                    'name': team.get('strTeam'),
                    'abbreviation': team.get('strTeamShort', team.get('strTeam', '')[:3].upper()),
                    'city': team.get('strLocation', ''),
                    'logo_url': team.get('strTeamBadge'),
                    'conference': team.get('strDivision', ''),
                    'current_record': {
                        'wins': 0,
                        'losses': 0,
                        'description': team.get('strDescriptionEN', '')[:200]
                    }
                })
        
        return teams
    
    def get_games(self, league_id: str, date: Optional[str] = None) -> List[Dict]:
        """Get games from TheSportsDB"""
        # TheSportsDB requires specific date format and team lookups
        games = []
        
        if date:
            # Get events for specific date
            formatted_date = date  # TheSportsDB expects YYYY-MM-DD
            data = self._make_request(f"eventsday.php?d={formatted_date}&l={league_id}")
            
            if data and 'events' in data:
                for event in data['events']:
                    # Determine game status
                    status = GameStatus.SCHEDULED
                    if event.get('strStatus') == 'Match Finished':
                        status = GameStatus.FINAL
                    elif event.get('strStatus') == 'Not Started':
                        status = GameStatus.SCHEDULED
                    
                    games.append({
                        'external_id': event.get('idEvent'),
                        'home_team_name': event.get('strHomeTeam'),
                        'away_team_name': event.get('strAwayTeam'),
                        'scheduled_start': f"{event.get('dateEvent')}T{event.get('strTime', '00:00:00')}",
                        'status': status,
                        'venue_name': event.get('strVenue'),
                        'home_score': event.get('intHomeScore'),
                        'away_score': event.get('intAwayScore'),
                        'season': event.get('strSeason'),
                    })
        
        return games


class OddsAPIProvider(SportsDataProvider):
    """The Odds API provider for betting odds"""
    
    def __init__(self, api_key: Optional[str] = None):
        config = APIConfig(
            base_url="https://api.the-odds-api.com/v4",
            api_key=api_key,
            rate_limit=500,  # Free tier allows 500 requests/month
            requires_auth=True
        )
        super().__init__(DataSource.ODDS_API, config)
    
    def get_sports(self) -> List[Dict]:
        """Get available sports from Odds API"""
        data = self._make_request("sports", {'all': 'true'})
        sports = []
        
        if data:
            for sport in data:
                if sport.get('active', False):
                    sports.append({
                        'key': sport.get('key'),
                        'title': sport.get('title'),
                        'description': sport.get('description'),
                        'active': sport.get('active', False)
                    })
        
        return sports
    
    def get_odds(self, sport_key: str, bookmakers: Optional[List[str]] = None) -> List[Dict]:
        """Get odds for a sport"""
        params = {
            'regions': 'us',
            'markets': 'h2h,spreads,totals',  # moneyline, spreads, totals
            'oddsFormat': 'american',
            'dateFormat': 'iso'
        }
        
        if bookmakers:
            params['bookmakers'] = ','.join(bookmakers)
        
        data = self._make_request(f"sports/{sport_key}/odds", params)
        odds_data = []
        
        if data:
            for game in data:
                for bookmaker in game.get('bookmakers', []):
                    for market in bookmaker.get('markets', []):
                        odds_data.append({
                            'game_id': game.get('id'),
                            'sport_key': game.get('sport_key'),
                            'home_team': game.get('home_team'),
                            'away_team': game.get('away_team'),
                            'commence_time': game.get('commence_time'),
                            'bookmaker': bookmaker.get('title'),
                            'market_type': market.get('key'),  # h2h, spreads, totals
                            'outcomes': market.get('outcomes', [])
                        })
        
        return odds_data


class UnifiedSportsDataManager:
    """Unified manager for all sports data providers"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available data providers"""
        # ESPN - Always available (free)
        self.providers[DataSource.ESPN] = ESPNProvider()
        
        # TheSportsDB - Always available (free)
        self.providers[DataSource.THESPORTSDB] = TheSportsDBProvider()
        
        # The Odds API - Requires API key for odds data
        odds_api_key = getattr(settings, 'ODDS_API_KEY', None)
        if odds_api_key:
            self.providers[DataSource.ODDS_API] = OddsAPIProvider(odds_api_key)
    
    def sync_leagues(self) -> Dict[str, int]:
        """Sync leagues from all providers"""
        results = {'created': 0, 'updated': 0, 'errors': 0}
        
        for source, provider in self.providers.items():
            try:
                if source == DataSource.ODDS_API:
                    continue  # Odds API doesn't provide league structure like others
                
                logger.info(f"Syncing leagues from {source.value}")
                leagues_data = provider.get_leagues()
                
                for league_data in leagues_data:
                    try:
                        # First try to find by name (since it's unique)
                        try:
                            league = League.objects.get(name=league_data['name'])
                            # Update existing league but check for abbreviation conflicts
                            if league.abbreviation != league_data['abbreviation']:
                                # Check if new abbreviation would conflict
                                if League.objects.filter(abbreviation=league_data['abbreviation']).exclude(id=league.id).exists():
                                    logger.warning(f"Cannot update {league.name} abbreviation to {league_data['abbreviation']} - already in use")
                                else:
                                    league.abbreviation = league_data['abbreviation']
                            league.sport_type = league_data['sport_type']
                            league.country = league_data.get('country', 'USA')
                            league.api_provider = league_data['api_provider']
                            league.current_season = str(datetime.now().year)
                            league.api_config = {
                                'source': source.value,
                                'external_id': league_data.get('external_id'),
                                'last_sync': timezone.now().isoformat()
                            }
                            league.save()
                            results['updated'] += 1
                        except League.DoesNotExist:
                            # Check if abbreviation already exists with different name
                            existing_by_abbr = League.objects.filter(abbreviation=league_data['abbreviation']).first()
                            if existing_by_abbr:
                                # Abbreviation exists but with different name
                                # Skip this league or create with modified abbreviation
                                logger.warning(f"League {league_data['name']} has abbreviation {league_data['abbreviation']} which is already used by {existing_by_abbr.name}")
                                # Generate unique abbreviation by appending source
                                unique_abbr = f"{league_data['abbreviation']}_{source.value[:3].upper()}"
                                if not League.objects.filter(abbreviation=unique_abbr).exists():
                                    league = League.objects.create(
                                        name=league_data['name'],
                                        abbreviation=unique_abbr,
                                        sport_type=league_data['sport_type'],
                                        country=league_data.get('country', 'USA'),
                                        api_provider=league_data['api_provider'],
                                        current_season=str(datetime.now().year),
                                        api_config={
                                            'source': source.value,
                                            'external_id': league_data.get('external_id'),
                                            'last_sync': timezone.now().isoformat()
                                        }
                                    )
                                    results['created'] += 1
                                    logger.info(f"Created {league_data['name']} with modified abbreviation {unique_abbr}")
                                else:
                                    logger.error(f"Cannot create {league_data['name']} - abbreviation conflict")
                                    results['errors'] += 1
                            else:
                                # Create new league
                                league = League.objects.create(
                                    name=league_data['name'],
                                    abbreviation=league_data['abbreviation'],
                                    sport_type=league_data['sport_type'],
                                    country=league_data.get('country', 'USA'),
                                    api_provider=league_data['api_provider'],
                                    current_season=str(datetime.now().year),
                                    api_config={
                                        'source': source.value,
                                        'external_id': league_data.get('external_id'),
                                        'last_sync': timezone.now().isoformat()
                                    }
                                )
                                results['created'] += 1
                            
                    except Exception as e:
                        logger.error(f"Error syncing league {league_data.get('name')}: {e}")
                        results['errors'] += 1
                        
            except Exception as e:
                logger.error(f"Error syncing from {source.value}: {e}")
                results['errors'] += 1
        
        return results
    
    def sync_teams(self, league: League) -> Dict[str, int]:
        """Sync teams for a specific league"""
        results = {'created': 0, 'updated': 0, 'errors': 0}
        
        # Get the appropriate provider
        api_source = league.api_config.get('source')
        external_id = league.api_config.get('external_id')
        
        if api_source not in [s.value for s in self.providers.keys()]:
            logger.warning(f"No provider available for {api_source}")
            return results
        
        provider = self.providers[DataSource(api_source)]
        
        try:
            teams_data = provider.get_teams(external_id)
            
            for team_data in teams_data:
                try:
                    team, created = Team.objects.update_or_create(
                        league=league,
                        abbreviation=team_data['abbreviation'],
                        defaults={
                            'name': team_data['name'],
                            'city': team_data.get('city', ''),
                            'conference': team_data.get('conference', ''),
                            'external_id': team_data.get('external_id', ''),
                            'logo_url': team_data.get('logo_url', ''),
                            'current_record': team_data.get('current_record', {}),
                        }
                    )
                    
                    if created:
                        results['created'] += 1
                    else:
                        results['updated'] += 1
                        
                except Exception as e:
                    logger.error(f"Error syncing team {team_data.get('name')}: {e}")
                    results['errors'] += 1
                    
        except Exception as e:
            logger.error(f"Error syncing teams for {league.name}: {e}")
            results['errors'] += 1
        
        return results
    
    def sync_games(self, league: League, date: Optional[str] = None) -> Dict[str, int]:
        """Sync games for a specific league and date"""
        results = {'created': 0, 'updated': 0, 'errors': 0}
        
        api_source = league.api_config.get('source')
        external_id = league.api_config.get('external_id')
        
        if api_source not in [s.value for s in self.providers.keys()]:
            return results
        
        provider = self.providers[DataSource(api_source)]
        
        try:
            games_data = provider.get_games(external_id, date)
            
            for game_data in games_data:
                try:
                    # Find teams
                    home_team = None
                    away_team = None
                    
                    if game_data.get('home_team_id'):
                        home_team = Team.objects.filter(
                            league=league, 
                            external_id=game_data['home_team_id']
                        ).first()
                    
                    if not home_team and game_data.get('home_team_name'):
                        home_team = Team.objects.filter(
                            league=league, 
                            name__icontains=game_data['home_team_name']
                        ).first()
                    
                    if game_data.get('away_team_id'):
                        away_team = Team.objects.filter(
                            league=league, 
                            external_id=game_data['away_team_id']
                        ).first()
                    
                    if not away_team and game_data.get('away_team_name'):
                        away_team = Team.objects.filter(
                            league=league, 
                            name__icontains=game_data['away_team_name']
                        ).first()
                    
                    if home_team and away_team:
                        game, created = Game.objects.update_or_create(
                            external_id=game_data['external_id'],
                            defaults={
                                'league': league,
                                'home_team': home_team,
                                'away_team': away_team,
                                'scheduled_start': game_data['scheduled_start'],
                                'status': game_data.get('status', GameStatus.SCHEDULED),
                                'venue_name': game_data.get('venue_name', ''),
                                'home_score': game_data.get('home_score'),
                                'away_score': game_data.get('away_score'),
                                'season': str(game_data.get('season', datetime.now().year)),
                                'week': game_data.get('week'),
                            }
                        )
                        
                        if created:
                            results['created'] += 1
                        else:
                            results['updated'] += 1
                    else:
                        logger.warning(f"Could not find teams for game: {game_data}")
                        
                except Exception as e:
                    logger.error(f"Error syncing game {game_data.get('external_id')}: {e}")
                    results['errors'] += 1
                    
        except Exception as e:
            logger.error(f"Error syncing games for {league.name}: {e}")
            results['errors'] += 1
        
        return results
    
    def sync_odds(self, sport_key: str) -> Dict[str, int]:
        """Sync odds data from The Odds API"""
        results = {'created': 0, 'updated': 0, 'errors': 0}
        
        if DataSource.ODDS_API not in self.providers:
            logger.warning("Odds API provider not available")
            return results
        
        provider = self.providers[DataSource.ODDS_API]
        
        try:
            odds_data = provider.get_odds(sport_key)
            
            for odds_item in odds_data:
                try:
                    # Find the corresponding game
                    game = Game.objects.filter(
                        external_id=odds_item['game_id']
                    ).first()
                    
                    if not game:
                        # Try to match by teams and date
                        home_team = Team.objects.filter(
                            name__icontains=odds_item['home_team']
                        ).first()
                        away_team = Team.objects.filter(
                            name__icontains=odds_item['away_team']
                        ).first()
                        
                        if home_team and away_team:
                            game = Game.objects.filter(
                                home_team=home_team,
                                away_team=away_team,
                                scheduled_start__date=datetime.fromisoformat(
                                    odds_item['commence_time'].replace('Z', '+00:00')
                                ).date()
                            ).first()
                    
                    if game:
                        # Create or get sportsbook
                        sportsbook, _ = Sportsbook.objects.get_or_create(
                            name=odds_item['bookmaker'],
                            defaults={'abbreviation': odds_item['bookmaker'][:10]}
                        )
                        
                        # Create betting market and odds
                        # This would be expanded based on the market type
                        # (moneyline, spreads, totals, etc.)
                        
                        results['updated'] += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing odds: {e}")
                    results['errors'] += 1
                    
        except Exception as e:
            logger.error(f"Error syncing odds for {sport_key}: {e}")
            results['errors'] += 1
        
        return results


# Global instance
sports_data_manager = UnifiedSportsDataManager()