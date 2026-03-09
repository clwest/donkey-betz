from django.contrib import admin
from django.urls import path, include
from .views_health import extended_health

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/extended', extended_health, name='health-extended'),
]

# Try to include app-level URLs if they exist
try:
    urlpatterns += [path('api/v1/', include('agents.urls'))]
except Exception:
    pass
