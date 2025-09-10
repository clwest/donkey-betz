"""
URL configuration for campaigns app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.campaigns_list, name='campaigns-list'),
    path('templates/', views.campaign_templates, name='campaign-templates'),
    path('from-template/', views.create_from_template, name='campaign-from-template'),
    path('<str:campaign_id>/', views.campaign_detail, name='campaign-detail'),
    path('<str:campaign_id>/simple-generate/', views.generate_simple_content, name='campaign-simple-generate'),
    path('<str:campaign_id>/batch-generate/', views.batch_generate_content, name='campaign-batch-generate'),
    path('<str:campaign_id>/launch/', views.launch_campaign, name='campaign-launch'),
]