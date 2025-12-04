"""
NOAA Spider - Weather & Climate Intelligence
=============================================

Session 343: Spider for NOAA API to track weather alerts and climate data.
Collects weather alerts, forecasts, and climate trends.

Uses NOAA_API_KEY from environment for authenticated requests.
"""

import aiohttp
import asyncio
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class NOAASpider(BaseIntelligenceSpider):
    """NOAA spider - weather alerts, forecasts, and climate data"""

    BASE_URL = "https://api.weather.gov"

    # US regions for alerts
    REGIONS = [
        'US',  # National
    ]

    # Major metro areas for forecasts
    METRO_POINTS = [
        ('40.7128', '-74.0060'),   # New York
        ('34.0522', '-118.2437'),  # Los Angeles
        ('41.8781', '-87.6298'),   # Chicago
        ('29.7604', '-95.3698'),   # Houston
        ('33.4484', '-112.0740'),  # Phoenix
    ]

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.api_key = os.getenv('NOAA_API_KEY', '')

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch weather data from NOAA"""
        try:
            all_alerts = []
            all_forecasts = []

            headers = {
                'User-Agent': 'DonkeyBetz-Spider/1.0 (contact@donkeybetz.com)',
                'Accept': 'application/geo+json'
            }

            async with aiohttp.ClientSession() as session:
                # Fetch active alerts (no API key needed for weather.gov)
                try:
                    url = f"{self.BASE_URL}/alerts/active"
                    params = {
                        'status': 'actual',
                        'message_type': 'alert',
                        'limit': 50
                    }

                    async with session.get(url, headers=headers, params=params, timeout=15) as response:
                        if response.status == 200:
                            data = await response.json()
                            features = data.get('features', [])

                            for feature in features:
                                props = feature.get('properties', {})
                                all_alerts.append({
                                    'id': props.get('id', ''),
                                    'event': props.get('event', ''),
                                    'headline': props.get('headline', ''),
                                    'description': props.get('description', '')[:500] if props.get('description') else '',
                                    'severity': props.get('severity', ''),
                                    'certainty': props.get('certainty', ''),
                                    'urgency': props.get('urgency', ''),
                                    'area_desc': props.get('areaDesc', ''),
                                    'sender': props.get('senderName', ''),
                                    'effective': props.get('effective', ''),
                                    'expires': props.get('expires', ''),
                                    'status': props.get('status', ''),
                                    'source': 'noaa',
                                    'type': 'weather_alert',
                                })
                        else:
                            self.logger.warning(f"NOAA alerts returned {response.status}")

                except Exception as e:
                    self.logger.warning(f"Error fetching alerts: {e}")

                await asyncio.sleep(0.3)

                # Fetch forecasts for major metros (sample)
                for lat, lon in self.METRO_POINTS[:2]:  # Limit to avoid rate limits
                    try:
                        # First get the grid point
                        point_url = f"{self.BASE_URL}/points/{lat},{lon}"

                        async with session.get(point_url, headers=headers, timeout=10) as response:
                            if response.status == 200:
                                point_data = await response.json()
                                forecast_url = point_data.get('properties', {}).get('forecast', '')

                                if forecast_url:
                                    async with session.get(forecast_url, headers=headers, timeout=10) as forecast_response:
                                        if forecast_response.status == 200:
                                            forecast_data = await forecast_response.json()
                                            periods = forecast_data.get('properties', {}).get('periods', [])

                                            for period in periods[:3]:  # Just next 3 periods
                                                all_forecasts.append({
                                                    'name': period.get('name', ''),
                                                    'temperature': period.get('temperature', ''),
                                                    'temperature_unit': period.get('temperatureUnit', ''),
                                                    'wind_speed': period.get('windSpeed', ''),
                                                    'wind_direction': period.get('windDirection', ''),
                                                    'short_forecast': period.get('shortForecast', ''),
                                                    'detailed_forecast': period.get('detailedForecast', ''),
                                                    'location': f"{lat},{lon}",
                                                    'source': 'noaa',
                                                    'type': 'forecast',
                                                })

                        await asyncio.sleep(0.5)

                    except Exception as e:
                        self.logger.warning(f"Error fetching forecast for {lat},{lon}: {e}")

            return {
                'alerts': all_alerts,
                'forecasts': all_forecasts,
                'source': 'noaa'
            }

        except Exception as e:
            self.logger.error(f"Error fetching NOAA data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process NOAA data into intelligence"""
        try:
            alerts = raw_data.get('alerts', [])
            forecasts = raw_data.get('forecasts', [])

            # Categorize alerts by severity
            severity_counts = {}
            for alert in alerts:
                severity = alert.get('severity', 'Unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            # Event types
            event_counts = {}
            for alert in alerts:
                event = alert.get('event', 'Unknown')
                event_counts[event] = event_counts.get(event, 0) + 1

            top_events = sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:10]

            # High priority alerts (Extreme/Severe)
            high_priority = [a for a in alerts if a.get('severity') in ['Extreme', 'Severe']]

            content = {
                'alerts': alerts,
                'forecasts': forecasts,
                'severity_breakdown': severity_counts,
                'top_events': top_events,
                'high_priority_alerts': high_priority,
                'total_alerts': len(alerts),
                'total_forecasts': len(forecasts),
            }

            quality_score = min(1.0, (len(alerts) + len(forecasts)) / 40 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='weather.gov',
                data_type='weather_intelligence',
                content=content,
                metadata={
                    'alert_count': len(alerts),
                    'forecast_count': len(forecasts),
                    'high_priority_count': len(high_priority),
                    'source': 'noaa',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['weather', 'alerts', 'forecast', 'climate', 'noaa', 'storms', 'temperature'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['operations_advisor', 'risk_analyst', 'logistics_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing NOAA data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['event', 'severity']

    def get_relevance_keywords(self) -> List[str]:
        return ['weather', 'forecast', 'alert', 'storm', 'temperature', 'climate', 'noaa']
