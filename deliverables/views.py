import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Deliverable
from .serializers import DeliverableSerializer

logger = logging.getLogger(__name__)

_ACTIVE_WORKSPACE_HEADER = 'HTTP_X_ACTIVE_WORKSPACE_ID'


def _resolve_workspace_id(request: Request):
    """Return workspace_id from query param or request header."""
    return (
        request.query_params.get('workspace')
        or request.META.get(_ACTIVE_WORKSPACE_HEADER)
    )


class DeliverableViewSet(ModelViewSet):
    serializer_class = DeliverableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Deliverable.objects.filter(user=self.request.user)
        workspace_id = _resolve_workspace_id(self.request)
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)
        return qs

    def _validate_workspace_access(self, workspace_id) -> bool:
        if workspace_id is None:
            return True
        from workspaces.models import Workspace
        user = self.request.user
        return Workspace.objects.filter(
            id=workspace_id
        ).filter(
            owner=user
        ).exists() or Workspace.objects.filter(
            id=workspace_id, members=user
        ).exists()

    def perform_create(self, serializer):
        workspace_id = (
            self.request.data.get('workspace_id')
            or self.request.META.get(_ACTIVE_WORKSPACE_HEADER)
        )
        if workspace_id and not self._validate_workspace_access(workspace_id):
            raise PermissionDenied('You do not have access to this workspace.')

        workspace = None
        if workspace_id:
            from workspaces.models import Workspace
            try:
                workspace = Workspace.objects.get(id=workspace_id)
            except Workspace.DoesNotExist:
                workspace = None

        serializer.save(user=self.request.user, workspace=workspace)
        logger.info(
            'Deliverable created: id=%s workspace=%s user=%s',
            serializer.instance.pk,
            workspace_id,
            self.request.user.pk,
        )

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request: Request) -> Response:
        qs = self.get_queryset()
        return Response({
            'total': qs.count(),
            'completed': qs.filter(status='completed').count(),
            'in_progress': qs.filter(status='in_progress').count(),
        })
