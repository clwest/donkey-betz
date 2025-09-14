"""
🧠 INTELLIGENCE API URLs
URL routing for the Real-Time Intelligence Engine
"""

from django.urls import path
from .views import SkynetStatusView, LiveOpportunitiesView, LivePredictionsView

urlpatterns = [
    # Skynet Intelligence Engine
    path('skynet/status/', SkynetStatusView.as_view(), name='skynet_status'),

    # Live Intelligence Data
    path('opportunities/', LiveOpportunitiesView.as_view(), name='live_opportunities'),
    path('predictions/', LivePredictionsView.as_view(), name='live_predictions'),
]