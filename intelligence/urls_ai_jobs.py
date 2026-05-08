# BROKEN-BUT-UNREACHABLE — Session 1113 review (Session 1111 PR-C queue).
# Classification: import-broken URLConf, no active runtime caller.
# Why: smoke import raises
#   AttributeError: module 'intelligence.views' has no attribute 'get_spiders'
# All 5 named view functions (get_spiders, get_jobs, start_spiders,
# apply_to_job, get_application_status) are missing — `intelligence/views.py`
# uses CBVs and never defined them. This URLConf is also never `include()`-d
# from any active urls.py, so the broken import is never triggered at runtime.
# Looks like a pre-CBV migration relic.
# Decision pending: archive after the deeper-review queue confirms no
# revival is intended. Until then: preserved for product reference.
# See: docs/handoffs/SESSION_1111_DEEPER_REVIEW_MAP.md

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