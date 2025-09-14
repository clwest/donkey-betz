"""
🧠 INTELLIGENCE API VIEWS
REST API endpoints for the Real-Time Intelligence Engine
"""

import asyncio
import logging
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .realtime_engine import intelligence_engine

logger = logging.getLogger(__name__)


class SkynetStatusView(APIView):
    """🚀 Get Skynet Intelligence Engine Status"""

    def get(self, request):
        try:
            # Check engine status
            engine_status = 'ONLINE' if intelligence_engine.is_running else 'OFFLINE'

            # Get current data
            opportunities_count = len(intelligence_engine.get_current_opportunities())
            predictions_count = len(intelligence_engine.get_current_predictions())

            return Response({
                'skynet_status': engine_status,
                'intelligence_engine': engine_status,
                'live_opportunities': opportunities_count,
                'live_predictions': predictions_count,
                'scan_interval': intelligence_engine.scan_interval,
                'last_update': datetime.now().isoformat(),
                'features': {
                    'sports_intelligence': True,
                    'arbitrage_detection': True,
                    'value_betting': True,
                    'cross_domain_analysis': True,
                    'pattern_recognition': True
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Skynet status error: {e}")
            return Response({
                'error': 'Failed to get Skynet status',
                'skynet_status': 'ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LiveOpportunitiesView(APIView):
    """🎯 Get Live Market Opportunities"""

    def get(self, request):
        try:
            opportunities = intelligence_engine.get_current_opportunities()

            return Response({
                'opportunities': opportunities,
                'count': len(opportunities),
                'timestamp': datetime.now().isoformat(),
                'scanner_status': 'ACTIVE' if intelligence_engine.is_running else 'OFFLINE'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Live opportunities error: {e}")
            return Response({
                'error': 'Failed to get live opportunities',
                'opportunities': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LivePredictionsView(APIView):
    """🔮 Get Live Intelligence Predictions"""

    def get(self, request):
        try:
            predictions = intelligence_engine.get_current_predictions()

            return Response({
                'predictions': predictions,
                'count': len(predictions),
                'timestamp': datetime.now().isoformat(),
                'engine_status': 'ACTIVE' if intelligence_engine.is_running else 'OFFLINE'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Live predictions error: {e}")
            return Response({
                'error': 'Failed to get live predictions',
                'predictions': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)