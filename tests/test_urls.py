# tests/test_urls.py
"""
URL configuration for testing - includes all production routes.

Session 416: Updated to include all core URLs for golden-path testing.
"""
from django.contrib import admin
from django.urls import path, include

# Import all URLs from core app
from core.urls import urlpatterns as core_urls

urlpatterns = [
    path('admin/', admin.site.urls),
] + core_urls
