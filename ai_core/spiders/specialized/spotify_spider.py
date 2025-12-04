"""
Spotify Spider - Music & Podcast Trends Intelligence
=====================================================

Session 343: Spider for Spotify API to track music and podcast trends.
Collects new releases, featured playlists, and podcast charts.

Uses SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET from environment.
"""

import aiohttp
import asyncio
import base64
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class SpotifySpider(BaseIntelligenceSpider):
    """Spotify spider - music trends, new releases, and podcast charts"""

    AUTH_URL = "https://accounts.spotify.com/api/token"
    BASE_URL = "https://api.spotify.com/v1"

    # Categories of interest
    CATEGORIES = [
        'toplists',
        'podcasts',
        'trending',
        'new_releases',
    ]

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID', '')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '')
        self.access_token = None

    async def _get_access_token(self, session: aiohttp.ClientSession) -> Optional[str]:
        """Get Spotify access token using client credentials flow"""
        if not self.client_id or not self.client_secret:
            return None

        try:
            auth_str = f"{self.client_id}:{self.client_secret}"
            auth_bytes = base64.b64encode(auth_str.encode()).decode()

            headers = {
                'Authorization': f'Basic {auth_bytes}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {'grant_type': 'client_credentials'}

            async with session.post(self.AUTH_URL, headers=headers, data=data, timeout=10) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('access_token')
                else:
                    self.logger.warning(f"Spotify auth failed: {response.status}")
                    return None

        except Exception as e:
            self.logger.error(f"Error getting Spotify token: {e}")
            return None

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch music and podcast trends from Spotify"""
        if not self.client_id or not self.client_secret:
            self.logger.warning("Spotify credentials not configured")
            return {'tracks': [], 'playlists': [], 'source': 'spotify', 'error': 'Credentials not configured'}

        try:
            all_tracks = []
            all_playlists = []
            all_albums = []

            async with aiohttp.ClientSession() as session:
                # Get access token
                self.access_token = await self._get_access_token(session)
                if not self.access_token:
                    return {'tracks': [], 'playlists': [], 'source': 'spotify', 'error': 'Auth failed'}

                headers = {'Authorization': f'Bearer {self.access_token}'}

                # Fetch new releases
                try:
                    url = f"{self.BASE_URL}/browse/new-releases"
                    params = {'limit': 20, 'country': 'US'}

                    async with session.get(url, headers=headers, params=params, timeout=15) as response:
                        if response.status == 200:
                            data = await response.json()
                            albums = data.get('albums', {}).get('items', [])

                            for album in albums:
                                all_albums.append({
                                    'name': album.get('name', ''),
                                    'artists': [a.get('name', '') for a in album.get('artists', [])],
                                    'release_date': album.get('release_date', ''),
                                    'total_tracks': album.get('total_tracks', 0),
                                    'url': album.get('external_urls', {}).get('spotify', ''),
                                    'image_url': album.get('images', [{}])[0].get('url', '') if album.get('images') else '',
                                    'album_type': album.get('album_type', ''),
                                    'source': 'spotify',
                                    'type': 'album',
                                })
                        else:
                            self.logger.warning(f"Spotify new releases returned {response.status}")

                except Exception as e:
                    self.logger.warning(f"Error fetching new releases: {e}")

                await asyncio.sleep(0.3)

                # Fetch featured playlists
                try:
                    url = f"{self.BASE_URL}/browse/featured-playlists"
                    params = {'limit': 20, 'country': 'US'}

                    async with session.get(url, headers=headers, params=params, timeout=15) as response:
                        if response.status == 200:
                            data = await response.json()
                            playlists = data.get('playlists', {}).get('items', [])

                            for playlist in playlists:
                                all_playlists.append({
                                    'name': playlist.get('name', ''),
                                    'description': playlist.get('description', ''),
                                    'url': playlist.get('external_urls', {}).get('spotify', ''),
                                    'image_url': playlist.get('images', [{}])[0].get('url', '') if playlist.get('images') else '',
                                    'tracks_count': playlist.get('tracks', {}).get('total', 0),
                                    'owner': playlist.get('owner', {}).get('display_name', ''),
                                    'source': 'spotify',
                                    'type': 'playlist',
                                })
                        else:
                            self.logger.warning(f"Spotify playlists returned {response.status}")

                except Exception as e:
                    self.logger.warning(f"Error fetching playlists: {e}")

                await asyncio.sleep(0.3)

                # Fetch categories
                try:
                    url = f"{self.BASE_URL}/browse/categories"
                    params = {'limit': 30, 'country': 'US'}

                    async with session.get(url, headers=headers, params=params, timeout=15) as response:
                        if response.status == 200:
                            data = await response.json()
                            categories = data.get('categories', {}).get('items', [])

                            # Store category names for trending analysis
                            category_names = [c.get('name', '') for c in categories]

                except Exception as e:
                    self.logger.warning(f"Error fetching categories: {e}")

            return {
                'albums': all_albums,
                'playlists': all_playlists,
                'source': 'spotify'
            }

        except Exception as e:
            self.logger.error(f"Error fetching Spotify data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Spotify data into intelligence"""
        try:
            albums = raw_data.get('albums', [])
            playlists = raw_data.get('playlists', [])

            # Extract artist frequency
            artist_counts = {}
            for album in albums:
                for artist in album.get('artists', []):
                    artist_counts[artist] = artist_counts.get(artist, 0) + 1

            top_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:15]

            # Album types distribution
            album_types = {}
            for album in albums:
                atype = album.get('album_type', 'unknown')
                album_types[atype] = album_types.get(atype, 0) + 1

            content = {
                'albums': albums,
                'playlists': playlists,
                'top_artists': top_artists,
                'album_types': album_types,
                'total_albums': len(albums),
                'total_playlists': len(playlists),
            }

            quality_score = min(1.0, (len(albums) + len(playlists)) / 30 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='spotify.com',
                data_type='music_intelligence',
                content=content,
                metadata={
                    'album_count': len(albums),
                    'playlist_count': len(playlists),
                    'source': 'spotify',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['spotify', 'music', 'albums', 'playlists', 'artists', 'trends', 'entertainment'],
                target_agents=['trend_analysis_agent', 'research_agent', 'content_strategy_agent'],
                target_advisors=['entertainment_analyst', 'trend_advisor', 'content_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Spotify data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['name', 'url']

    def get_relevance_keywords(self) -> List[str]:
        return ['spotify', 'music', 'album', 'playlist', 'artist', 'song', 'streaming']
