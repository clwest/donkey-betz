"""
Management command to sync NFL team metadata from ESPN API
"""

from django.core.management.base import BaseCommand
from sports.models import Team, League
import requests
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync NFL team metadata (logos, colors, conferences) from ESPN API'

    def handle(self, *args, **options):
        self.stdout.write("Syncing NFL team metadata from ESPN...")

        try:
            # Get or create NFL league
            nfl_league, _ = League.objects.get_or_create(
                sport_type='nfl',
                defaults={
                    'name': 'NFL',
                    'abbreviation': 'NFL',
                    'country': 'USA',
                    'is_active': True
                }
            )

            # ESPN Teams endpoint
            url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"

            self.stdout.write(f"Fetching teams from {url}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            teams_data = data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])

            teams_created = 0
            teams_updated = 0

            for team_wrapper in teams_data:
                team_data = team_wrapper.get('team', {})

                abbreviation = team_data.get('abbreviation', '')
                if not abbreviation:
                    self.stdout.write(self.style.WARNING(f"  Skipping team without abbreviation: {team_data.get('displayName')}"))
                    continue

                # Extract team metadata
                team_info = {
                    'name': team_data.get('displayName', ''),
                    'city': team_data.get('location', ''),
                    'is_active': True,
                }

                # Add logo URL if available
                if team_data.get('logos'):
                    team_info['logo_url'] = team_data['logos'][0].get('href', '')

                # Add colors if available
                if team_data.get('color'):
                    team_info['primary_color'] = f"#{team_data['color']}"
                if team_data.get('alternateColor'):
                    team_info['secondary_color'] = f"#{team_data['alternateColor']}"

                # Add venue information
                venue_data = team_data.get('venue', {})
                if venue_data:
                    team_info['venue_name'] = venue_data.get('fullName', '')
                    team_info['venue_city'] = venue_data.get('address', {}).get('city', '')
                    team_info['venue_state'] = venue_data.get('address', {}).get('state', '')

                # Add conference/division information
                groups = team_data.get('groups', {})
                if groups:
                    team_info['conference'] = groups.get('name', '')
                    # Division might be in a different structure
                    if 'parent' in groups:
                        team_info['division'] = groups['parent'].get('name', '')

                # Create or update team
                team, created = Team.objects.update_or_create(
                    league=nfl_league,
                    abbreviation=abbreviation,
                    defaults=team_info
                )

                if created:
                    teams_created += 1
                    self.stdout.write(f"  ✓ Created: {team.name} ({abbreviation})")
                else:
                    teams_updated += 1
                    self.stdout.write(f"  ↻ Updated: {team.name} ({abbreviation})")

            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Sync complete: {teams_created} teams created, {teams_updated} teams updated"
            ))

        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Failed to fetch teams from ESPN: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error syncing teams: {e}"))
            raise