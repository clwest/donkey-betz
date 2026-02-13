# project/urls.py
from django.urls import include, path

urlpatterns = [
    path('', include('intel.urls')),
    # ... other routes
]