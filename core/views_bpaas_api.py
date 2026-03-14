"""
BPaaS API — Build Packet as a Service endpoints.

Provides:
- POST /api/bpaas/create-from-packet/ — Create full project from build packet
- POST /api/bpaas/generate-close-pack/ — Generate SOW + checklist + proposal
- GET /api/bpaas/schema/ — Return the build packet JSON schema
- GET /api/bpaas/example/ — Return the Norman Handyman example packet
"""

import logging

from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(["GET"])
def bpaas_schema(request):
    """Return the Build Packet JSON schema."""
    from core.services.bpaas.build_packet_schema import BUILD_PACKET_SCHEMA
    return Response(BUILD_PACKET_SCHEMA)


@api_view(["GET"])
def bpaas_example(request):
    """Return the Norman Handyman example build packet."""
    from core.services.bpaas.build_packet_schema import NORMAN_HANDYMAN_EXAMPLE
    return Response(NORMAN_HANDYMAN_EXAMPLE)


@api_view(["POST"])
def create_from_packet(request):
    """
    Create a full BPaaS project from a build packet.

    Expects: { "workspace_id": "...", "packet": { ... } }

    Creates: WorkspaceProject + repos + env vars + preview env + magic link.
    Returns all created resource IDs + the magic link URL.
    """
    from core.models_skin_layer import ProjectWorkspace
    from core.services.bpaas.packet_service import create_project_from_packet

    workspace_id = request.data.get("workspace_id")
    packet = request.data.get("packet")

    if not workspace_id or not packet:
        return Response(
            {"error": "workspace_id and packet are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate minimum required fields
    if not packet.get("project", {}).get("name"):
        return Response(
            {"error": "packet.project.name is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not packet.get("acceptance_criteria"):
        return Response(
            {"error": "packet.acceptance_criteria is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        workspace = ProjectWorkspace.objects.get(id=workspace_id)
    except ProjectWorkspace.DoesNotExist:
        return Response(
            {"error": "Workspace not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    result = create_project_from_packet(
        workspace=workspace,
        packet=packet,
        created_by=request.user,
    )

    logger.info(
        "BPaaS project created: %s by %s",
        result["project"]["name"], request.user,
    )

    return Response(result, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def generate_close_pack(request):
    """
    Generate close pack documents (SOW, checklist, proposal) from a build packet.

    Expects: { "packet": { ... } }
    Returns: { "sow": {...}, "checklist": {...}, "proposal": {...} }
    """
    from core.services.bpaas.packet_service import generate_close_pack

    packet = request.data.get("packet")
    if not packet:
        return Response(
            {"error": "packet is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    close_pack = generate_close_pack(packet)
    return Response(close_pack)
