# tests/test_urls.py
"""Minimal URL configuration for testing."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add any test-specific URLs here
]
