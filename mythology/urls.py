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

    # Session 1095 Tier 1: bulk review by pattern_type (unblocks FP backlog)
    path('bulk-review/', views.bulk_review, name='bulk_review'),
    
    # Recent events for Neural Scan section
    path('recent-events/', views.recent_events, name='recent_events'),
    
    # User reporting
    path('report/', views.report_content, name='report_content'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<uuid:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),

    # Session 972: Patterns and Guards (used by IntelligenceTab Safety sub-tab)
    path('patterns/', views.list_patterns, name='patterns_list'),
    path('guards/', views.list_guards, name='guards_list'),

    # Session 541: Mythology Quarantine API
    path('quarantine/', views.quarantine_list, name='quarantine_list'),
    path('quarantine/stats/', views.quarantine_stats, name='quarantine_stats'),
    path('quarantine/<uuid:quarantine_id>/', views.quarantine_detail, name='quarantine_detail'),
    path('quarantine/<uuid:quarantine_id>/approve/', views.quarantine_approve, name='quarantine_approve'),
    path('quarantine/<uuid:quarantine_id>/reject/', views.quarantine_reject, name='quarantine_reject'),
]