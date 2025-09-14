"""
Management command to sync sports data from external APIs
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from sports.models import League, Team, Game
from sports.data_providers import sports_data_manager
from dateutil import parser
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync sports data from ESPN and other external APIs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sport',
            type=str,
            default='ncaaf',
            help='Sport type to sync (nfl, ncaaf, nba, ncaab, mlb, nhl)'
        )
        parser.add_argument(
            '--date',
            type=str,
            help='Date to sync games for (YYYY-MM-DD format)'
        )
        parser.add_argument(
            '--all-sports',
            action='store_true',
            help='Sync all supported sports'
        )

    def handle(self, *args, **options):
        sport = options['sport']
        date = options['date']
        all_sports = options['all_sports']

        if all_sports:
            sports_to_sync = ['nfl', 'ncaaf', 'nba', 'ncaab', 'mlb', 'nhl']
        else:
            sports_to_sync = [sport]

        total_games_synced = 0
        
        for sport_type in sports_to_sync:
            self.stdout.write(f"\nSyncing {sport_type.upper()} games...")
            
            try:
                # Get or create league
                league, created = League.objects.get_or_create(
                    sport_type=sport_type,
                    defaults={
                        'name': sport_type.upper(),
                        'abbreviation': sport_type.upper(),
                        'country': 'USA',
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created league: {league.name}"))
                
                # Sync games from ESPN
                sync_result = sports_data_manager.sync_games(sport_type, date)
                
                if not sync_result['success']:
                    self.stdout.write(self.style.ERROR(f"Failed to sync {sport_type}: {sync_result.get('message')}"))
                    continue
                
                games_saved = 0
                for game_data in sync_result.get('games', []):
                    try:
                        # Get or create teams
                        home_team_data = game_data.get('home_team', {})
                        away_team_data = game_data.get('away_team', {})
                        
                        # Get or create teams using the unique constraint fields (league + abbreviation)
                        home_abbreviation = home_team_data.get('abbreviation', 'UNK')
                        home_team, _ = Team.objects.get_or_create(
                            league=league,
                            abbreviation=home_abbreviation,
                            defaults={
                                'name': home_team_data.get('name', 'Unknown'),
                                'city': '',
                                'is_active': True
                            }
                        )
                        
                        away_abbreviation = away_team_data.get('abbreviation', 'UNK')
                        away_team, _ = Team.objects.get_or_create(
                            league=league,
                            abbreviation=away_abbreviation,
                            defaults={
                                'name': away_team_data.get('name', 'Unknown'),
                                'city': '',
                                'is_active': True
                            }
                        )
                        
                        # Parse date
                        game_date = parser.parse(game_data.get('date', timezone.now().isoformat()))
                        
                        # Map ESPN status to our status
                        status_map = {
                            'STATUS_SCHEDULED': 'scheduled',
                            'STATUS_IN_PROGRESS': 'live',
                            'STATUS_FINAL': 'final',
                            'STATUS_POSTPONED': 'postponed',
                            'STATUS_CANCELED': 'cancelled',
                            'STATUS_HALFTIME': 'halftime',
                        }
                        
                        game_status = status_map.get(
                            game_data.get('status', 'STATUS_SCHEDULED'),
                            'scheduled'
                        )
                        
                        # Extract live game state data
                        game_situation = game_data.get('game_situation', {})
                        live_stats = {}

                        # Add situation data if available
                        if game_situation:
                            live_stats.update({
                                'down': game_situation.get('down'),
                                'distance': game_situation.get('distance'),
                                'down_distance_text': game_situation.get('down_distance_text'),
                                'possession': game_situation.get('possession'),
                                'is_red_zone': game_situation.get('is_red_zone'),
                                'last_play': game_situation.get('last_play'),
                                'timeouts_home': game_situation.get('timeouts_home'),
                                'timeouts_away': game_situation.get('timeouts_away')
                            })

                        # Create or update game
                        game, created = Game.objects.update_or_create(
                            external_id=game_data.get('external_id', f"espn_{game_data.get('name', '')}"),
                            defaults={
                                'league': league,
                                'home_team': home_team,
                                'away_team': away_team,
                                'scheduled_start': game_date,
                                'status': game_status,
                                'venue_name': game_data.get('venue', ''),
                                'home_score': home_team_data.get('score'),
                                'away_score': away_team_data.get('score'),
                                'current_period': str(game_data.get('period', '')) if game_data.get('period') else '',
                                'time_remaining': game_data.get('display_clock', ''),
                                'live_stats': live_stats,
                                'is_active': True
                            }
                        )
                        
                        if created:
                            games_saved += 1
                            self.stdout.write(f"  Created game: {away_team.name} @ {home_team.name}")
                        else:
                            self.stdout.write(f"  Updated game: {away_team.name} @ {home_team.name}")
                            
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  Error saving game: {e}"))
                        continue
                
                total_games_synced += games_saved
                self.stdout.write(self.style.SUCCESS(
                    f"Synced {games_saved} new games for {sport_type.upper()} "
                    f"(total: {len(sync_result.get('games', []))} games fetched)"
                ))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error syncing {sport_type}: {e}"))
                continue
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Total games synced: {total_games_synced}"))