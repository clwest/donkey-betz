"""
URL configuration for mythology lab dashboard.
"""

from django.urls import path
from . import views

app_name = 'mythology'

urlpatterns = [
    # Dashboard and statistics
    path('stats/', views.dashboard_stats, name='stats'),
    
    # Flagged content management  
    path('flagged-content/', views.flagged_content_list, name='flagged_content_list'),
    path('flagged-content/<uuid:content_id>/', views.flagged_content_detail, name='flagged_content_detail'),
    path('review/', views.submit_review, name='submit_review'),
    
    # Recent events for Neural Scan section
    path('recent-events/', views.recent_events, name='recent_events'),
    
    # User reporting
    path('report/', views.report_content, name='report_content'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<uuid:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]