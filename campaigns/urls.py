"""
URL configuration for campaigns app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.campaigns_list, name='campaigns-list'),
    path('templates/', views.campaign_templates, name='campaign-templates'),
]