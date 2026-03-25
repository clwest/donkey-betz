from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DeliverableViewSet

router = DefaultRouter()
router.register(r'deliverables', DeliverableViewSet, basename='deliverable')

urlpatterns = [
    path('', include(router.urls)),
]
