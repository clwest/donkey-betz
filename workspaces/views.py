from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Workspace
from .serializers import WorkspaceSerializer


class WorkspaceViewSet(ModelViewSet):
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            Workspace.objects.filter(owner=user)
            | Workspace.objects.filter(members=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
