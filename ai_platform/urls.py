from django.urls import path
from . import views

app_name = 'ai_platform'

urlpatterns = [
    # User Impact Verification APIs
    path('api/user-impact/metrics/', views.get_user_impact_metrics, name='user_impact_metrics'),
    path('api/user-impact/stories/', views.get_user_success_stories, name='user_success_stories'),
    path('api/user-impact/track/', views.track_user_outcome, name='track_outcome'),
    path('api/user-impact/verify/', views.verify_user_success, name='verify_success'),

    # Revenue Verification API
    path('api/revenue/verification/', views.get_revenue_verification, name='revenue_verification'),

    # Spider Verification API
    path('api/spider/verification/', views.get_spider_verification, name='spider_verification'),

    # System Reality Score API
    path('api/system/reality-score/', views.get_system_reality_score, name='reality_score'),

    # System Activity Verification API
    path('api/system/verify-activity/', views.verify_system_activity, name='verify_activity'),

    # Learning Status API
    path('api/learning/status/', views.get_learning_status, name='learning_status'),

    # Learning Details API
    path('api/learning/details/', views.get_learning_details, name='learning_details'),
]