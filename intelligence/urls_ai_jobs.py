from django.urls import path
from . import views

app_name = 'intelligence'

urlpatterns = [
    # AI Job System endpoints
    path('ai-jobs/spiders/', views.get_spiders, name='get_spiders'),
    path('ai-jobs/jobs/', views.get_jobs, name='get_jobs'),
    path('ai-jobs/start-spiders/', views.start_spiders, name='start_spiders'),
    path('ai-jobs/apply/', views.apply_to_job, name='apply_to_job'),
    path('ai-jobs/status/<str:job_id>/', views.get_application_status, name='application_status'),
]