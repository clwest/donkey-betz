from rest_framework.routers import DefaultRouter

from .views import ProjectWorkspaceViewSet

router = DefaultRouter()
router.register(r"workspaces", ProjectWorkspaceViewSet, basename="workspace")

urlpatterns = router.urls
