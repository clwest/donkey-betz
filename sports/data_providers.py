"""
Sports Data Providers - Real API Integration

Connects to actual ESPN, TheSportsDB, and The Odds API endpoints
for live sports data, odds, and betting information.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
# from django.core.cache import cache
import time
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ESPNProvider:
    """ESPN Hidden API provider for live sports data"""
    
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
    
    SPORT_MAPPING = {
        'nfl': 'football/nfl',
        'ncaaf': 'football/college-football',
        'nba': 'basketball/nba',
        'ncaab': 'basketball/mens-college-basketball',
        'mlb': 'baseball/mlb',
        'nhl': 'hockey/nhl',
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; SportsBetting/1.0)',
            'Accept': 'application/json'
        })
    
    def get_scoreboard(self, sport: str, date: Optional[str] = None) -> Dict:
        """Get live scoreboard data for a sport"""
        # Simple in-memory cache for now (could use Redis later)
        cache_key = f"espn_scoreboard_{sport}_{date or 'today'}"
        
        try:
            sport_path = self.SPORT_MAPPING.get(sport, 'football/nfl')
            url = f"{self.BASE_URL}/{sport_path}/scoreboard"
            
            params = {}
            if date:
                # ESPN expects dates in YYYYMMDD format
                params['dates'] = date.replace('-', '')
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            # TODO: Implement proper caching later
            return data
            
        except Exception as e:
            logger.error(f"ESPN API error for {sport}: {e}")
            return {}
    
    def get_teams(self, sport: str) -> List[Dict]:
        """Get team information for a sport"""
        
        try:
            sport_path = self.SPORT_MAPPING.get(sport, 'football/nfl')
            url = f"{self.BASE_URL}/{sport_path}/teams"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            teams = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
            
            result = []
            for team_data in teams:
                team = team_data.get('team', {})
                result.append({
                    'id': team.get('id'),
                    'name': team.get('name'),
                    'abbreviation': team.get('abbreviation'),
                    'displayName': team.get('displayName'),
                    'logo': team.get('logos', [{}])[0].get('href') if team.get('logos') else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"ESPN teams API error for {sport}: {e}")
            return []


class TheOddsAPIProvider:
    """The Odds API provider for betting lines"""
    
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    SPORT_MAPPING = {
        'nfl': 'americanfootball_nfl',
        'ncaaf': 'americanfootball_ncaaf',
        'nba': 'basketball_nba',
        'ncaab': 'basketball_ncaab',
        'mlb': 'baseball_mlb',
        'nhl': 'icehockey_nhl',
    }
    
    def __init__(self):
        # Get API key from environment or settings (using THE_ODDS_API_KEY)
        self.api_key = os.getenv('THE_ODDS_API_KEY', getattr(settings, 'ODDS_API_KEY', 'demo'))
        self.session = requests.Session()
        
        if self.api_key != 'demo':
            logger.info(f"Using real Odds API key: {self.api_key[:8]}...")
        else:
            logger.warning("Using demo Odds API key - limited data available")
    
    def get_odds(self, sport: str, markets: List[str] = None) -> List[Dict]:
        """Get betting odds for a sport"""
        if self.api_key == 'demo':
            logger.warning("Using demo API key - limited data available")
            return self._get_demo_odds(sport)

        # Skip caching for now

        try:
            # Session 563: Support both short keys (nfl) and full keys (americanfootball_nfl)
            # If sport contains underscore, it's already a full Odds API key
            if '_' in sport:
                sport_key = sport
            else:
                sport_key = self.SPORT_MAPPING.get(sport, 'americanfootball_nfl')
            url = f"{self.BASE_URL}/sports/{sport_key}/odds"
            
            params = {
                'apiKey': self.api_key,
                'regions': 'us',
                'markets': ','.join(markets or ['h2h', 'spreads', 'totals']),
                'oddsFormat': 'american'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except Exception as e:
            logger.error(f"Odds API error for {sport}: {e}")
            return self._get_demo_odds(sport)
    
    def _get_demo_odds(self, sport: str) -> List[Dict]:
        """Return demo odds data when API key not available"""
        # Session 563: Support both short keys and full keys
        sport_key = sport if '_' in sport else self.SPORT_MAPPING.get(sport, 'americanfootball_nfl')
        return [
            {
                'id': 'demo_game_1',
                'sport_key': sport_key,
                'home_team': 'Home Team',
                'away_team': 'Away Team',
                'commence_time': datetime.utcnow().isoformat(),
                'bookmakers': [
                    {
                        'key': 'draftkings',
                        'title': 'DraftKings',
                        'markets': [
                            {
                                'key': 'h2h',
                                'outcomes': [
                                    {'name': 'Home Team', 'price': -110},
                                    {'name': 'Away Team', 'price': -110}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]


class SportRadarProvider:
    """SportRadar API provider for comprehensive sports data"""
    
    BASE_URL = "https://api.sportradar.us"
    
    SPORT_MAPPING = {
        'nfl': 'nfl/official/trial/v7/en',
        'ncaaf': 'ncaafb/trial/v4/en', 
        'nba': 'nba/trial/v8/en',
        'ncaab': 'ncaamb/trial/v8/en',
        'mlb': 'mlb/trial/v7/en',
        'nhl': 'nhl/trial/v7/en',
    }
    
    def __init__(self):
        self.api_key = os.getenv('SPORTRADAR_API_KEY', getattr(settings, 'SPORTRADAR_API_KEY', 'demo'))
        self.session = requests.Session()
        
        if self.api_key != 'demo':
            logger.info(f"Using real SportRadar API key: {self.api_key[:8]}...")
        else:
            logger.warning("Using demo SportRadar API key")
    
    def get_schedule(self, sport: str, season_year: int = 2024) -> Dict:
        """Get schedule for a sport"""
        if self.api_key == 'demo':
            return {'games': []}
        
        try:
            sport_path = self.SPORT_MAPPING.get(sport, 'nfl/official/trial/v7/en')
            url = f"{self.BASE_URL}/{sport_path}/games/{season_year}/REG/schedule.json"
            
            params = {'api_key': self.api_key}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"SportRadar schedule error for {sport}: {e}")
            return {'games': []}
    
    def get_game_summary(self, sport: str, game_id: str) -> Dict:
        """Get detailed game summary"""
        if self.api_key == 'demo':
            return {}
        
        try:
            sport_path = self.SPORT_MAPPING.get(sport, 'nfl/official/trial/v7/en')
            url = f"{self.BASE_URL}/{sport_path}/games/{game_id}/summary.json"
            
            params = {'api_key': self.api_key}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"SportRadar game summary error: {e}")
            return {}


class SportsDataManager:
    """Main manager for coordinating data from multiple providers"""
    
    def __init__(self):
        self.espn = ESPNProvider()
        self.odds_api = TheOddsAPIProvider()
        self.sportradar = SportRadarProvider()
    
    def sync_games(self, sport: str, date: Optional[str] = None) -> Dict:
        """Sync games from ESPN and merge with real odds data"""
        result = {
            'games': [],
            'odds_games': [],
            'success': True,
            'message': ''
        }
        
        try:
            # Get ESPN scoreboard data
            scoreboard = self.espn.get_scoreboard(sport, date)
            events = scoreboard.get('events', [])
            
            # Get real odds data from The Odds API
            odds_data = self.odds_api.get_odds(sport, ['h2h', 'spreads', 'totals'])
            logger.info(f"Retrieved {len(odds_data)} games with odds from The Odds API")
            
            # Create odds lookup by team names
            odds_map = {}
            for odds_game in odds_data:
                home_team = odds_game.get('home_team', '').lower()
                away_team = odds_game.get('away_team', '').lower()
                key = f"{away_team}@{home_team}"
                odds_map[key] = odds_game
            
            result['odds_games'] = odds_data  # Include raw odds data in result
            
            for event in events:
                competition = event.get('competitions', [{}])[0]
                competitors = competition.get('competitors', [])
                
                if len(competitors) >= 2:
                    home_team_name = competitors[0].get('team', {}).get('name', '')
                    away_team_name = competitors[1].get('team', {}).get('name', '')
                    
                    # Look up odds by team names
                    odds_key = f"{away_team_name.lower()}@{home_team_name.lower()}"
                    matched_odds = odds_map.get(odds_key, {})
                    
                    # Also try partial matching for team names
                    if not matched_odds:
                        for key, odds_game in odds_map.items():
                            odds_home = odds_game.get('home_team', '').lower()
                            odds_away = odds_game.get('away_team', '').lower()
                            
                            # Check if team names contain each other
                            if (any(word in odds_home for word in home_team_name.lower().split()) and 
                                any(word in odds_away for word in away_team_name.lower().split())):
                                matched_odds = odds_game
                                break
                    
                    # Extract game state details
                    status_info = event.get('status', {})
                    situation = competition.get('situation', {})

                    game_data = {
                        'external_id': event.get('id'),
                        'name': event.get('name'),
                        'date': event.get('date'),
                        'status': status_info.get('type', {}).get('name'),
                        'status_detail': status_info.get('type', {}).get('detail', ''),
                        'period': status_info.get('period', 0),
                        'display_clock': status_info.get('displayClock', ''),
                        'game_situation': {
                            'down': situation.get('down'),
                            'distance': situation.get('distance'),
                            'down_distance_text': situation.get('downDistanceText', ''),
                            'possession': situation.get('possession'),
                            'is_red_zone': situation.get('isRedZone', False),
                            'last_play': situation.get('lastPlay', {}).get('text', ''),
                            'timeouts_home': situation.get('homeTimeouts'),
                            'timeouts_away': situation.get('awayTimeouts')
                        },
                        'home_team': {
                            'id': competitors[0].get('id'),
                            'name': home_team_name,
                            'abbreviation': competitors[0].get('team', {}).get('abbreviation'),
                            'score': competitors[0].get('score'),
                            'winner': competitors[0].get('winner', False)
                        },
                        'away_team': {
                            'id': competitors[1].get('id'),
                            'name': away_team_name,
                            'abbreviation': competitors[1].get('team', {}).get('abbreviation'),
                            'score': competitors[1].get('score'),
                            'winner': competitors[1].get('winner', False)
                        },
                        'venue': competition.get('venue', {}).get('fullName'),
                        'odds': matched_odds,
                        'has_odds': bool(matched_odds)
                    }
                    result['games'].append(game_data)
            
            games_with_odds = sum(1 for game in result['games'] if game.get('has_odds'))
            result['message'] = f"Synced {len(result['games'])} games for {sport} ({games_with_odds} with live odds)"
            result['games_with_odds'] = games_with_odds
            logger.info(result['message'])
            
        except Exception as e:
            result['success'] = False
            result['message'] = f"Error syncing {sport} games: {str(e)}"
            logger.error(result['message'])
        
        return result
    
    def get_live_games(self) -> List[Dict]:
        """Get all live games across sports"""
        live_games = []
        
        for sport in ['nfl', 'nba', 'mlb', 'nhl', 'ncaaf', 'ncaab']:
            try:
                scoreboard = self.espn.get_scoreboard(sport)
                events = scoreboard.get('events', [])
                
                for event in events:
                    status = event.get('status', {}).get('type', {}).get('state')
                    if status == 'in':  # In progress
                        live_games.append({
                            'sport': sport,
                            'event': event
                        })
            except Exception as e:
                logger.error(f"Error getting live games for {sport}: {e}")
        
        return live_games


# Global instance
sports_data_manager = SportsDataManager()