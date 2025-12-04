"""
Open-Meteo Spider - Weather Data Intelligence
=============================================

Session 343: Phase 1 Spider Expansion
Open-Meteo provides free weather data with NO API key required.
"""

import aiohttp
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class OpenMeteoSpider(BaseIntelligenceSpider):
    """Open-Meteo weather spider - free weather data for any location"""

    BASE_URL = 'https://api.open-meteo.com/v1'

    # Major US cities with coordinates
    DEFAULT_LOCATIONS = {
        'new_york': {'lat': 40.7128, 'lon': -74.0060, 'name': 'New York'},
        'los_angeles': {'lat': 34.0522, 'lon': -118.2437, 'name': 'Los Angeles'},
        'chicago': {'lat': 41.8781, 'lon': -87.6298, 'name': 'Chicago'},
        'houston': {'lat': 29.7604, 'lon': -95.3698, 'name': 'Houston'},
        'denver': {'lat': 39.7392, 'lon': -104.9903, 'name': 'Denver'},
        'miami': {'lat': 25.7617, 'lon': -80.1918, 'name': 'Miami'},
        'seattle': {'lat': 47.6062, 'lon': -122.3321, 'name': 'Seattle'},
        'boston': {'lat': 42.3601, 'lon': -71.0589, 'name': 'Boston'},
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch weather data from Open-Meteo"""
        try:
            all_data = {
                'forecasts': [],
                'current_conditions': [],
            }

            async with aiohttp.ClientSession() as session:
                for city_key, location in self.DEFAULT_LOCATIONS.items():
                    weather = await self._fetch_weather(session, location, city_key)
                    if weather:
                        all_data['forecasts'].append(weather)

            return all_data

        except Exception as e:
            self.logger.error(f"Error fetching Open-Meteo data: {e}")
            return None

    async def _fetch_weather(self, session: aiohttp.ClientSession, location: Dict[str, Any], city_key: str) -> Optional[Dict[str, Any]]:
        """Fetch weather for a single location"""
        try:
            url = f"{self.BASE_URL}/forecast"
            params = {
                'latitude': location['lat'],
                'longitude': location['lon'],
                'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m',
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code',
                'temperature_unit': 'fahrenheit',
                'wind_speed_unit': 'mph',
                'precipitation_unit': 'inch',
                'timezone': 'America/Denver',
                'forecast_days': 7,
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    current = data.get('current', {})
                    daily = data.get('daily', {})

                    return {
                        'city': location['name'],
                        'city_key': city_key,
                        'latitude': location['lat'],
                        'longitude': location['lon'],
                        'current': {
                            'temperature': current.get('temperature_2m'),
                            'feels_like': current.get('apparent_temperature'),
                            'humidity': current.get('relative_humidity_2m'),
                            'precipitation': current.get('precipitation'),
                            'wind_speed': current.get('wind_speed_10m'),
                            'weather_code': current.get('weather_code'),
                            'condition': self._get_weather_condition(current.get('weather_code', 0)),
                        },
                        'forecast': self._process_forecast(daily),
                    }
        except Exception as e:
            self.logger.warning(f"Error fetching weather for {location['name']}: {e}")
        return None

    def _get_weather_condition(self, code: int) -> str:
        """Convert weather code to human-readable condition"""
        conditions = {
            0: 'Clear sky',
            1: 'Mainly clear',
            2: 'Partly cloudy',
            3: 'Overcast',
            45: 'Fog',
            48: 'Depositing rime fog',
            51: 'Light drizzle',
            53: 'Moderate drizzle',
            55: 'Dense drizzle',
            61: 'Slight rain',
            63: 'Moderate rain',
            65: 'Heavy rain',
            71: 'Slight snow',
            73: 'Moderate snow',
            75: 'Heavy snow',
            77: 'Snow grains',
            80: 'Slight rain showers',
            81: 'Moderate rain showers',
            82: 'Violent rain showers',
            85: 'Slight snow showers',
            86: 'Heavy snow showers',
            95: 'Thunderstorm',
            96: 'Thunderstorm with slight hail',
            99: 'Thunderstorm with heavy hail',
        }
        return conditions.get(code, 'Unknown')

    def _process_forecast(self, daily: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process daily forecast data"""
        forecasts = []
        times = daily.get('time', [])
        max_temps = daily.get('temperature_2m_max', [])
        min_temps = daily.get('temperature_2m_min', [])
        precip = daily.get('precipitation_sum', [])
        codes = daily.get('weather_code', [])

        for i in range(min(7, len(times))):
            forecasts.append({
                'date': times[i] if i < len(times) else None,
                'high': max_temps[i] if i < len(max_temps) else None,
                'low': min_temps[i] if i < len(min_temps) else None,
                'precipitation': precip[i] if i < len(precip) else None,
                'condition': self._get_weather_condition(codes[i] if i < len(codes) else 0),
            })
        return forecasts

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Open-Meteo weather data"""
        try:
            forecasts = raw_data.get('forecasts', [])

            # Find extremes
            hottest = max(forecasts, key=lambda x: x.get('current', {}).get('temperature', 0)) if forecasts else None
            coldest = min(forecasts, key=lambda x: x.get('current', {}).get('temperature', 100)) if forecasts else None
            rainiest = max(forecasts, key=lambda x: x.get('current', {}).get('precipitation', 0)) if forecasts else None

            content = {
                'forecasts': forecasts,
                'extremes': {
                    'hottest': {'city': hottest['city'], 'temp': hottest['current']['temperature']} if hottest else None,
                    'coldest': {'city': coldest['city'], 'temp': coldest['current']['temperature']} if coldest else None,
                    'rainiest': {'city': rainiest['city'], 'precip': rainiest['current']['precipitation']} if rainiest else None,
                },
                'summary': {
                    'cities_tracked': len(forecasts),
                    'average_temp': sum(f['current']['temperature'] for f in forecasts if f.get('current', {}).get('temperature')) / len(forecasts) if forecasts else 0,
                }
            }

            quality_score = min(1.0, len(forecasts) / 8 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='open-meteo.com',
                data_type='weather',
                content=content,
                metadata={
                    'cities_tracked': len(forecasts),
                    'source': 'open-meteo',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['weather', 'forecast', 'climate', 'temperature'],
                target_agents=['research_agent'],
                target_advisors=['weather_analyst']
            )

        except Exception as e:
            self.logger.error(f"Error processing Open-Meteo data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['city']

    def get_relevance_keywords(self) -> List[str]:
        return ['weather', 'forecast', 'temperature', 'rain', 'climate']
