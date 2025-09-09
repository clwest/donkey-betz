"""
URLs for odds calculation.
"""
from django.urls import path
from . import views

app_name = 'odds_calc'

urlpatterns = [
    path('kelly-criterion/', views.kelly_criterion, name='kelly-criterion'),
]