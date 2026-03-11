"""
SKIN Layer API - Workspace Management REST Endpoints
Session 695-696: Expose workspace functionality for UI

This provides REST API access to the WorkspaceManager service,
enabling proper workspace management UI in the React frontend.
"""

import logging
from typing import Optional
from uuid import UUID

from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from core.models_skin_layer import (
    ProjectWorkspace,
    WorkspaceOperation,
    WorkspaceContext,
)
from core.services.workspace_manager import get_workspace_manager

logger = logging.getLogger(__name__)


# =============================================================================
# Serializers
# =============================================================================

from rest_framework import serializers


class WorkspaceContextSerializer(serializers.ModelSerializer):
    """Serializer for cached workspace context/structure"""

    class Meta:
        model = WorkspaceContext
        fields = [
            'total_files',
            'total_directories',
            'total_lines_of_code',
            'file_type_counts',
            'file_tree',
            'key_files',
            'coding_patterns',
            'dependencies',
            'import_aliases',
            'directory_purposes',
            'last_scanned_at',
            'scan_duration_ms',
        ]
        read_only_fields = fields


class ProjectWorkspaceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for workspace list views"""

    context_summary = serializers.SerializerMethodField()

    class Meta:
        model = ProjectWorkspace
        fields = [
            'id',
            'name',
            'description',
            'workspace_type',
            'root_path',
            'is_active',
            'tech_stack',
            'current_branch',
            'total_operations',
            'total_files_written',
            'total_commits',
            'last_operation_at',
            'created_at',
            'updated_at',
            'context_summary',
        ]
        read_only_fields = fields

    def get_context_summary(self, obj):
        """Get summary of workspace context if available"""
        try:
            ctx = obj.context
            return {
                'total_files': ctx.total_files,
                'total_directories': ctx.total_directories,
                'total_lines_of_code': ctx.total_lines_of_code,
                'last_scanned_at': ctx.last_scanned_at,
            }
        except WorkspaceContext.DoesNotExist:
            return None


class ProjectWorkspaceDetailSerializer(serializers.ModelSerializer):
    """Full serializer for workspace detail views"""

    context = WorkspaceContextSerializer(read_only=True)
    recent_operations_count = serializers.SerializerMethodField()
    pending_reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = ProjectWorkspace
        fields = [
            'id',
            'name',
            'description',
            'workspace_type',
            'root_path',
            'git_remote_url',
            'tech_stack',
            'entry_points',
            'allow_file_write',
            'allow_file_delete',
            'allow_command_execution',
            'allow_git_operations',
            'protected_paths',
            'require_human_review',
            'is_active',
            'current_branch',
            'total_operations',
            'total_files_written',
            'total_commits',
            'last_operation_at',
            'created_at',
            'updated_at',
            'context',
            'recent_operations_count',
            'pending_reviews_count',
        ]
        read_only_fields = [
            'id', 'total_operations', 'total_files_written',
            'total_commits', 'last_operation_at', 'created_at', 'updated_at',
            'context', 'recent_operations_count', 'pending_reviews_count',
        ]

    def get_recent_operations_count(self, obj):
        """Count operations in last 24 hours"""
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(hours=24)
        return obj.operations.filter(created_at__gte=cutoff).count()

    def get_pending_reviews_count(self, obj):
        """Count operations pending review"""
        return obj.operations.filter(
            requires_review=True,
            reviewed_by_human=False
        ).count()


class WorkspaceOperationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for operation list views"""

    workspace_name = serializers.CharField(source='workspace.name', read_only=True)

    class Meta:
        model = WorkspaceOperation
        fields = [
            'id',
            'workspace',
            'workspace_name',
            'agent_name',
            'agent_task',  # Session 834: Added for grouping related operations
            'operation_type',
            'file_path',
            'success',
            'error_message',
            'execution_time_ms',
            'requires_review',
            'reviewed_by_human',
            'human_approved',
            'can_rollback',
            'rolled_back',
            'created_at',
        ]
        read_only_fields = fields


class WorkspaceOperationDetailSerializer(serializers.ModelSerializer):
    """Full serializer for operation detail with diff support"""

    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    diff = serializers.SerializerMethodField()
    lines_changed = serializers.SerializerMethodField()
    is_file_operation = serializers.SerializerMethodField()
    is_git_operation = serializers.SerializerMethodField()
    # Session 855: Add agent execution time from related AgentExecution
    agent_execution_time_ms = serializers.SerializerMethodField()

    class Meta:
        model = WorkspaceOperation
        fields = [
            'id',
            'workspace',
            'workspace_name',
            'user',
            'agent_name',
            'agent_task',
            'operation_type',
            'file_path',
            'file_content_before',
            'file_content_after',
            'file_size_before',
            'file_size_after',
            'command',
            'command_output',
            'command_error',
            'exit_code',
            'success',
            'error_message',
            'execution_time_ms',
            'agent_execution_time_ms',  # Session 855
            'requires_review',
            'reviewed_by_human',
            'human_approved',
            'human_feedback',
            'reviewed_at',
            'can_rollback',
            'rolled_back',
            'rollback_operation',
            'created_at',
            'diff',
            'lines_changed',
            'is_file_operation',
            'is_git_operation',
        ]
        read_only_fields = fields

    def get_diff(self, obj):
        """Get unified diff for file operations"""
        if obj.is_file_operation:
            return obj.get_diff()
        return None

    def get_lines_changed(self, obj):
        """Get lines changed count"""
        return obj.lines_changed

    def get_is_file_operation(self, obj):
        return obj.is_file_operation

    def get_is_git_operation(self, obj):
        return obj.is_git_operation

    def get_agent_execution_time_ms(self, obj):
        """Session 855: Get agent execution time from related AgentExecution"""
        return obj.agent_execution_time_ms


class WorkspaceRegisterSerializer(serializers.Serializer):
    """
    Session 792: Enhanced serializer for registering workspaces.
    Supports local paths OR GitHub URLs (including private repos with token).
    """

    # Option 1: Local path
    path = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Absolute path to local project root"
    )

    # Option 2: GitHub URL
    github_url = serializers.CharField(
        max_length=500,
        required=False,
        help_text="GitHub URL to clone (e.g., https://github.com/user/repo.git)"
    )
    github_token = serializers.CharField(
        max_length=200,
        required=False,
        write_only=True,
        help_text="GitHub Personal Access Token for private repos (optional)"
    )

    # Common fields
    name = serializers.CharField(
        max_length=200,
        required=False,
        help_text="Display name (auto-detected if not provided)"
    )
    description = serializers.CharField(
        max_length=1000,
        required=False,
        help_text="Project description"
    )
    set_active = serializers.BooleanField(
        default=True,
        help_text="Set as active workspace"
    )

    def validate_github_url(self, value):
        """Session 798: Validate GitHub URL format"""
        import re
        if value:
            # Normalize common mistakes
            value = value.strip()

            # Add https:// if missing but looks like github.com
            if value.startswith('github.com/'):
                value = 'https://' + value

            # Check for valid GitHub URL pattern
            pattern = r'^https?://github\.com/[^/]+/[^/]+'
            if not re.match(pattern, value):
                display_value = value[:50] + '...' if len(value) > 50 else value
                raise serializers.ValidationError(
                    f"Invalid GitHub URL. Expected format: https://github.com/username/repository "
                    f"(received: '{display_value}')"
                )
        return value

    def validate(self, data):
        """Ensure either path or github_url is provided"""
        if not data.get('path') and not data.get('github_url'):
            raise serializers.ValidationError(
                "Either 'path' (local) or 'github_url' (GitHub) must be provided"
            )
        if data.get('path') and data.get('github_url'):
            raise serializers.ValidationError(
                "Provide either 'path' or 'github_url', not both"
            )
        return data


class WorkspaceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating workspace settings"""

    class Meta:
        model = ProjectWorkspace
        fields = [
            'name',
            'description',
            'allow_file_write',
            'allow_file_delete',
            'allow_command_execution',
            'allow_git_operations',
            'protected_paths',
            'require_human_review',
        ]


class FileWriteSerializer(serializers.Serializer):
    """Serializer for writing a file"""

    path = serializers.CharField(max_length=500, help_text="Relative path from workspace root")
    content = serializers.CharField(help_text="File content to write")
    agent_name = serializers.CharField(max_length=100, default="WebUI", help_text="Name of agent/source")


class GitCommitSerializer(serializers.Serializer):
    """Serializer for git commit"""

    message = serializers.CharField(max_length=500, help_text="Commit message")
    agent_name = serializers.CharField(max_length=100, default="WebUI", help_text="Name of agent for attribution")


class GitBranchSerializer(serializers.Serializer):
    """Serializer for creating git branch"""

    branch_name = serializers.CharField(max_length=200, help_text="Name for new branch")


class OperationReviewSerializer(serializers.Serializer):
    """Serializer for reviewing an operation"""

    approved = serializers.BooleanField(help_text="Whether to approve the operation")
    feedback = serializers.CharField(required=False, default="", help_text="Optional feedback")


# =============================================================================
# Pagination
# =============================================================================

class OperationPagination(PageNumberPagination):
    """Pagination for operations list"""
    page_size = 100  # Session 918: Increased from 20 to show more operations
    page_size_query_param = 'page_size'
    max_page_size = 500


# =============================================================================
# ViewSets
# =============================================================================

class ProjectWorkspaceViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing project workspaces.

    Endpoints:
    - GET /api/workspaces/ - List all workspaces
    - POST /api/workspaces/ - Register new workspace
    - GET /api/workspaces/{id}/ - Get workspace details
    - PATCH /api/workspaces/{id}/ - Update workspace settings
    - DELETE /api/workspaces/{id}/ - Delete workspace
    - POST /api/workspaces/{id}/activate/ - Set as active
    - POST /api/workspaces/{id}/scan/ - Rescan workspace
    - GET /api/workspaces/{id}/files/ - Browse files
    - GET /api/workspaces/{id}/file/ - Read file content
    - POST /api/workspaces/{id}/write/ - Write file
    - GET /api/workspaces/{id}/git-status/ - Get git status
    - POST /api/workspaces/{id}/git-commit/ - Create commit
    - POST /api/workspaces/{id}/git-branch/ - Create branch
    - GET /api/workspaces/{id}/operations/ - List operations
    - GET /api/workspaces/{id}/stats/ - Get statistics
    - GET /api/workspaces/active/ - Get active workspace
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter to user's workspaces only"""
        return ProjectWorkspace.objects.filter(
            user=self.request.user
        ).select_related('context').order_by('-updated_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectWorkspaceListSerializer
        elif self.action == 'create':
            return WorkspaceRegisterSerializer
        elif self.action in ['update', 'partial_update']:
            return WorkspaceUpdateSerializer
        return ProjectWorkspaceDetailSerializer

    def create(self, request):
        """
        Session 792: Register a new workspace - local path or GitHub URL.
        Supports private GitHub repos with Personal Access Token.
        """
        import subprocess
        import os
        import re

        serializer = WorkspaceRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        manager = get_workspace_manager(request.user)

        try:
            # Determine if this is a local path or GitHub clone
            if data.get('github_url'):
                github_url = data['github_url']
                github_token = data.get('github_token')

                # Determine workspace name from URL if not provided
                name = data.get('name')
                if not name:
                    # Extract repo name from URL
                    match = re.search(r'/([^/]+?)(?:\.git)?$', github_url)
                    name = match.group(1) if match else 'github-project'

                # Determine clone directory
                base_dir = os.environ.get('WORKSPACE_BASE_DIR', '/app/workspaces')
                if not os.path.exists(base_dir):
                    try:
                        os.makedirs(base_dir, exist_ok=True)
                    except Exception:
                        base_dir = '/tmp/workspaces'
                        os.makedirs(base_dir, exist_ok=True)

                root_path = os.path.join(base_dir, name)

                # Check if already exists
                if os.path.exists(root_path):
                    return Response(
                        {'error': f'Directory already exists: {root_path}. Choose a different name.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Build clone URL (with token for private repos)
                clone_url = github_url
                if github_token:
                    # Build authenticated URL for git clone
                    # Token is used transiently, never stored in database
                    clone_url = self._build_authenticated_clone_url(github_url, github_token)

                # Clone the repository
                logger.info(f"Cloning {github_url} to {root_path}")
                result = subprocess.run(
                    ['git', 'clone', clone_url, root_path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode != 0:
                    error_msg = result.stderr
                    # Don't expose the token in error messages
                    if github_token:
                        error_msg = error_msg.replace(github_token, '***TOKEN***')
                    return Response(
                        {'error': f'Git clone failed: {error_msg}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                logger.info(f"Successfully cloned to {root_path}")

                # Register the workspace with git_remote type
                workspace = manager.register_workspace(
                    root_path=root_path,
                    name=name,
                    set_active=data.get('set_active', True),
                )

                # Update with GitHub-specific fields
                workspace.workspace_type = 'git_remote'
                workspace.git_remote_url = github_url  # Store original URL (without token)
                workspace.description = data.get('description', f'Cloned from {github_url}')
                workspace.save()

            else:
                # Local path registration
                workspace = manager.register_workspace(
                    root_path=data['path'],
                    name=data.get('name'),
                    set_active=data.get('set_active', True),
                )
                if data.get('description'):
                    workspace.description = data['description']
                    workspace.save()

            return Response(
                ProjectWorkspaceDetailSerializer(workspace).data,
                status=status.HTTP_201_CREATED
            )

        except subprocess.TimeoutExpired:
            return Response(
                {'error': 'Git clone timed out. The repository may be too large.'},
                status=status.HTTP_408_REQUEST_TIMEOUT
            )
        except FileNotFoundError:
            return Response(
                {'error': 'Git is not installed on the server.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"Error registering workspace: {e}")
            return Response(
                {'error': f'Failed to register workspace: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _build_authenticated_clone_url(self, github_url: str, token: str) -> str:
        """
        Session 792: Build authenticated GitHub clone URL with token.

        For private repos, git clone requires authentication. We insert the token
        into the URL temporarily for the clone operation only - it's never stored.

        Input: https://github.com/user/repo.git
        Output: https://TOKEN@github.com/user/repo.git
        """
        import re
        # Match https://github.com/... pattern
        pattern = r'^(https?://)(github\.com/.+)$'
        match = re.match(pattern, github_url)
        if match:
            protocol = match.group(1)  # "https://"
            rest = match.group(2)       # "github.com/user/repo.git"
            # Insert token after protocol
            return f"{protocol}{token}@{rest}"
        # If pattern doesn't match, return original (clone will fail with auth error)
        return github_url

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get the currently active workspace"""
        manager = get_workspace_manager(request.user)
        workspace = manager.get_active_workspace()

        if not workspace:
            return Response(
                {'error': 'No active workspace', 'detail': 'Register a workspace first'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(ProjectWorkspaceDetailSerializer(workspace).data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Set workspace as active"""
        workspace = self.get_object()
        manager = get_workspace_manager(request.user)

        try:
            workspace = manager.set_active_workspace(workspace.id)
            return Response(ProjectWorkspaceDetailSerializer(workspace).data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def scan(self, request, pk=None):
        """Rescan workspace to update context"""
        workspace = self.get_object()
        manager = get_workspace_manager(request.user)

        try:
            # For git_remote workspaces, wait for clone or return 202
            result = manager.scanner.ensure_repo_present_or_wait(
                workspace, wait_seconds=20, poll_interval=0.5,
            )
            if not result['ready']:
                return Response(
                    {
                        'status': 'cloning',
                        'workspace_id': str(workspace.id),
                        'clone_started_at': result.get('clone_started_at'),
                        'retry_after_seconds': 5,
                        'message': 'Repository clone in progress. Retry shortly.',
                    },
                    status=202,
                    headers={'Retry-After': '5'},
                )

            context = manager.rescan_workspace(workspace)
            return Response({
                'success': True,
                'message': f'Scanned {context.total_files} files in {context.total_directories} directories',
                'context': WorkspaceContextSerializer(context).data
            })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"Error scanning workspace: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def files(self, request, pk=None):
        """Browse workspace files - returns hierarchical tree structure"""
        workspace = self.get_object()

        # Check if tree format is requested (default to tree)
        format_type = request.query_params.get('format', 'tree')
        max_depth = int(request.query_params.get('max_depth', 3))

        try:
            # Get workspace context which has the scanned file tree
            try:
                context = workspace.context
            except WorkspaceContext.DoesNotExist:
                # No scan yet - return empty tree
                return Response({
                    'workspace_id': str(workspace.id),
                    'workspace_name': workspace.name,
                    'tree': [],
                    'total_files': 0,
                    'total_directories': 0,
                    'message': 'Workspace not scanned yet. Use POST /scan/ to scan.'
                })

            if format_type == 'flat':
                # Return flat list (old behavior)
                manager = get_workspace_manager(request.user)
                pattern = request.query_params.get('pattern', '**/*')
                limit = int(request.query_params.get('limit', 100))
                files = manager.list_files(workspace, pattern=pattern)[:limit]
                return Response({
                    'workspace_id': str(workspace.id),
                    'workspace_name': workspace.name,
                    'pattern': pattern,
                    'total_matches': len(files),
                    'files': files
                })

            # Build hierarchical tree from file_tree dict
            # file_tree is { "dir_path": ["file1.py", "file2.js"], ... }
            file_tree = context.file_tree or {}

            def build_tree(base_path='', depth=0):
                """Recursively build tree structure"""
                if depth > max_depth:
                    return []

                nodes = []
                dirs_added = set()

                # Get files in current directory
                current_files = file_tree.get(base_path or '.', [])
                for filename in sorted(current_files):
                    file_path = f"{base_path}/{filename}" if base_path else filename
                    nodes.append({
                        'name': filename,
                        'path': file_path,
                        'type': 'file'
                    })

                # Get subdirectories
                for dir_path, files in file_tree.items():
                    if dir_path == '.' or dir_path == base_path:
                        continue

                    # Check if this directory is a direct child
                    if base_path:
                        if not dir_path.startswith(base_path + '/'):
                            continue
                        relative = dir_path[len(base_path) + 1:]
                    else:
                        relative = dir_path

                    # Get immediate child directory
                    parts = relative.split('/')
                    immediate_child = parts[0]

                    if immediate_child and immediate_child not in dirs_added:
                        dirs_added.add(immediate_child)
                        child_path = f"{base_path}/{immediate_child}" if base_path else immediate_child
                        children = build_tree(child_path, depth + 1)
                        nodes.append({
                            'name': immediate_child,
                            'path': child_path,
                            'type': 'directory',
                            'children': children
                        })

                # Sort: directories first, then files
                nodes.sort(key=lambda x: (0 if x['type'] == 'directory' else 1, x['name'].lower()))
                return nodes

            tree = build_tree()

            return Response({
                'workspace_id': str(workspace.id),
                'workspace_name': workspace.name,
                'tree': tree,
                'total_files': context.total_files,
                'total_directories': context.total_directories,
                'last_scanned': context.last_scanned_at
            })
        except Exception as e:
            logger.exception(f"Error getting workspace files: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def file(self, request, pk=None):
        """Read a file from workspace"""
        workspace = self.get_object()
        manager = get_workspace_manager(request.user)

        path = request.query_params.get('path')
        if not path:
            return Response(
                {'error': 'path query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            content = manager.read_file(workspace, path)
            if content is None:
                return Response(
                    {'error': f'File not found: {path}'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Truncate very large files
            max_size = 100000  # 100KB
            truncated = len(content) > max_size

            return Response({
                'workspace_id': str(workspace.id),
                'path': path,
                'content': content[:max_size] if truncated else content,
                'size': len(content),
                'truncated': truncated,
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def write(self, request, pk=None):
        """Write a file to workspace"""
        workspace = self.get_object()

        if not workspace.allow_file_write:
            return Response(
                {'error': 'File writing is disabled for this workspace'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = FileWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        manager = get_workspace_manager(request.user)

        try:
            operation = manager.write_file(
                workspace=workspace,
                file_path=serializer.validated_data['path'],
                content=serializer.validated_data['content'],
                agent_name=serializer.validated_data.get('agent_name', 'WebUI'),
            )

            return Response({
                'success': operation.success,
                'operation_id': str(operation.id),
                'file_path': operation.file_path,
                'operation_type': operation.operation_type,
                'error_message': operation.error_message if not operation.success else None,
            })
        except Exception as e:
            logger.exception(f"Error writing file: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='git-status')
    def git_status(self, request, pk=None):
        """Get git status for workspace"""
        workspace = self.get_object()
        manager = get_workspace_manager(request.user)

        try:
            git_status = manager.git_status(workspace)
            return Response({
                'workspace_id': str(workspace.id),
                'workspace_name': workspace.name,
                **git_status
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='git-commit')
    def git_commit(self, request, pk=None):
        """Create a git commit"""
        workspace = self.get_object()

        if not workspace.allow_git_operations:
            return Response(
                {'error': 'Git operations are disabled for this workspace'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = GitCommitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        manager = get_workspace_manager(request.user)

        try:
            operation = manager.git_commit(
                workspace=workspace,
                message=serializer.validated_data['message'],
                agent_name=serializer.validated_data.get('agent_name', 'WebUI'),
            )

            return Response({
                'success': operation.success,
                'operation_id': str(operation.id),
                'operation_type': operation.operation_type,
                'error_message': operation.error_message if not operation.success else None,
            })
        except Exception as e:
            logger.exception(f"Error creating commit: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='git-branch')
    def git_branch(self, request, pk=None):
        """Create a new git branch"""
        workspace = self.get_object()

        if not workspace.allow_git_operations:
            return Response(
                {'error': 'Git operations are disabled for this workspace'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = GitBranchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        manager = get_workspace_manager(request.user)

        try:
            operation = manager.git_create_branch(
                workspace=workspace,
                branch_name=serializer.validated_data['branch_name'],
            )

            return Response({
                'success': operation.success,
                'operation_id': str(operation.id),
                'branch_name': serializer.validated_data['branch_name'],
                'error_message': operation.error_message if not operation.success else None,
            })
        except Exception as e:
            logger.exception(f"Error creating branch: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def operations(self, request, pk=None):
        """List operations for this workspace"""
        workspace = self.get_object()

        # Filtering
        queryset = workspace.operations.all()

        # Session 864: Exclude warmups by default
        include_warmups = request.query_params.get('include_warmups', 'false')
        if include_warmups.lower() != 'true':
            queryset = queryset.filter(is_warmup=False)

        # Filter by run_mode if specified
        run_mode = request.query_params.get('run_mode')
        if run_mode:
            queryset = queryset.filter(run_mode=run_mode)

        operation_type = request.query_params.get('type')
        if operation_type:
            queryset = queryset.filter(operation_type=operation_type)

        agent_name = request.query_params.get('agent')
        if agent_name:
            queryset = queryset.filter(agent_name__icontains=agent_name)

        success = request.query_params.get('success')
        if success is not None:
            queryset = queryset.filter(success=success.lower() == 'true')

        pending_review = request.query_params.get('pending_review')
        if pending_review is not None and pending_review.lower() == 'true':
            queryset = queryset.filter(requires_review=True, reviewed_by_human=False)

        queryset = queryset.order_by('-created_at')

        # Pagination
        paginator = OperationPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = WorkspaceOperationListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = WorkspaceOperationListSerializer(queryset[:50], many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get workspace statistics"""
        workspace = self.get_object()

        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        ops = workspace.operations

        stats = {
            'workspace_id': str(workspace.id),
            'workspace_name': workspace.name,
            'totals': {
                'operations': workspace.total_operations,
                'files_written': workspace.total_files_written,
                'commits': workspace.total_commits,
            },
            'last_24h': {
                'operations': ops.filter(created_at__gte=last_24h).count(),
                'successful': ops.filter(created_at__gte=last_24h, success=True).count(),
                'failed': ops.filter(created_at__gte=last_24h, success=False).count(),
            },
            'last_7d': {
                'operations': ops.filter(created_at__gte=last_7d).count(),
                'by_type': dict(
                    ops.filter(created_at__gte=last_7d)
                    .values_list('operation_type')
                    .annotate(count=Count('id'))
                ),
                'by_agent': dict(
                    ops.filter(created_at__gte=last_7d)
                    .values_list('agent_name')
                    .annotate(count=Count('id'))
                ),
            },
            'pending_reviews': ops.filter(
                requires_review=True,
                reviewed_by_human=False
            ).count(),
            'rollback_available': ops.filter(
                can_rollback=True,
                rolled_back=False
            ).count(),
        }

        # Add context stats if available
        try:
            ctx = workspace.context
            stats['project'] = {
                'total_files': ctx.total_files,
                'total_directories': ctx.total_directories,
                'total_lines_of_code': ctx.total_lines_of_code,
                'file_types': ctx.file_type_counts,
                'last_scanned': ctx.last_scanned_at,
            }
        except WorkspaceContext.DoesNotExist:
            stats['project'] = None

        return Response(stats)


class WorkspaceOperationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for workspace operations (audit trail).

    Endpoints:
    - GET /api/workspace-operations/ - List all operations (with filtering)
    - GET /api/workspace-operations/{id}/ - Get operation details with diff
    - POST /api/workspace-operations/{id}/rollback/ - Rollback operation
    - POST /api/workspace-operations/{id}/review/ - Approve/reject operation
    """

    permission_classes = [IsAuthenticated]
    pagination_class = OperationPagination

    def get_queryset(self):
        """Filter to user's operations only"""
        queryset = WorkspaceOperation.objects.filter(
            user=self.request.user
        ).select_related('workspace').order_by('-created_at')

        # Session 864: Exclude warmups by default (unless explicitly requested)
        # This keeps the Operations tab meaningful by hiding exercise/warmup runs
        include_warmups = self.request.query_params.get('include_warmups', 'false')
        if include_warmups.lower() != 'true':
            queryset = queryset.filter(is_warmup=False)

        # Filter by run_mode if specified
        run_mode = self.request.query_params.get('run_mode')
        if run_mode:
            queryset = queryset.filter(run_mode=run_mode)

        # Filtering
        workspace_id = self.request.query_params.get('workspace')
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        operation_type = self.request.query_params.get('type')
        if operation_type:
            queryset = queryset.filter(operation_type=operation_type)

        agent_name = self.request.query_params.get('agent')
        if agent_name:
            queryset = queryset.filter(agent_name__icontains=agent_name)

        success = self.request.query_params.get('success')
        if success is not None:
            queryset = queryset.filter(success=success.lower() == 'true')

        pending_review = self.request.query_params.get('pending_review')
        if pending_review is not None and pending_review.lower() == 'true':
            queryset = queryset.filter(requires_review=True, reviewed_by_human=False)

        file_path = self.request.query_params.get('file_path')
        if file_path:
            queryset = queryset.filter(file_path__icontains=file_path)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return WorkspaceOperationListSerializer
        return WorkspaceOperationDetailSerializer

    @action(detail=True, methods=['post'])
    def rollback(self, request, pk=None):
        """Rollback an operation"""
        operation = self.get_object()

        if not operation.can_rollback:
            return Response(
                {'error': 'This operation cannot be rolled back'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if operation.rolled_back:
            return Response(
                {'error': 'This operation has already been rolled back'},
                status=status.HTTP_400_BAD_REQUEST
            )

        manager = get_workspace_manager(request.user)

        try:
            rollback_op = manager.file_writer.rollback_operation(operation)
            return Response({
                'success': rollback_op.success,
                'original_operation_id': str(operation.id),
                'rollback_operation_id': str(rollback_op.id),
                'message': f'Rolled back {operation.operation_type} on {operation.file_path}',
            })
        except Exception as e:
            logger.exception(f"Error rolling back operation: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Approve or reject an operation pending review"""
        operation = self.get_object()

        if not operation.requires_review:
            return Response(
                {'error': 'This operation does not require review'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if operation.reviewed_by_human:
            return Response(
                {'error': 'This operation has already been reviewed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = OperationReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        manager = get_workspace_manager(request.user)

        try:
            if serializer.validated_data['approved']:
                result = manager.approve_operation(
                    operation,
                    feedback=serializer.validated_data.get('feedback', '')
                )
                return Response({
                    'success': True,
                    'approved': True,
                    'operation_id': str(operation.id),
                    'message': 'Operation approved and applied',
                })
            else:
                result = manager.reject_operation(
                    operation,
                    feedback=serializer.validated_data.get('feedback', '')
                )
                return Response({
                    'success': True,
                    'approved': False,
                    'operation_id': str(operation.id),
                    'message': 'Operation rejected',
                })
        except Exception as e:
            logger.exception(f"Error reviewing operation: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =============================================================================
# Standalone API Views
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workspace_dashboard(request):
    """
    Dashboard overview of all workspaces and recent activity.

    GET /api/workspaces/dashboard/
    """
    user = request.user

    workspaces = ProjectWorkspace.objects.filter(user=user)
    active_workspace = workspaces.filter(is_active=True).first()

    from django.utils import timezone
    from datetime import timedelta

    last_24h = timezone.now() - timedelta(hours=24)

    recent_ops = WorkspaceOperation.objects.filter(
        user=user,
        created_at__gte=last_24h
    ).order_by('-created_at')[:10]

    pending_reviews = WorkspaceOperation.objects.filter(
        user=user,
        requires_review=True,
        reviewed_by_human=False
    ).count()

    return Response({
        'workspaces': {
            'total': workspaces.count(),
            'active': ProjectWorkspaceListSerializer(active_workspace).data if active_workspace else None,
            'list': ProjectWorkspaceListSerializer(workspaces[:5], many=True).data,
        },
        'activity': {
            'operations_24h': recent_ops.count(),
            'recent_operations': WorkspaceOperationListSerializer(recent_ops, many=True).data,
            'pending_reviews': pending_reviews,
        },
        'totals': {
            'total_operations': sum(w.total_operations for w in workspaces),
            'total_files_written': sum(w.total_files_written for w in workspaces),
            'total_commits': sum(w.total_commits for w in workspaces),
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def file_history(request, workspace_id):
    """
    Get operation history for a specific file.

    GET /api/workspaces/{workspace_id}/file-history/?path=src/App.tsx
    """
    workspace = get_object_or_404(
        ProjectWorkspace,
        id=workspace_id,
        user=request.user
    )

    file_path = request.query_params.get('path')
    if not file_path:
        return Response(
            {'error': 'path query parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    manager = get_workspace_manager(request.user)
    operations = manager.get_file_history(workspace, file_path)

    return Response({
        'workspace_id': str(workspace.id),
        'file_path': file_path,
        'total_operations': len(operations),
        'operations': WorkspaceOperationListSerializer(operations, many=True).data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_reviews(request):
    """
    Get all operations pending human review.

    GET /api/workspace-operations/pending-reviews/
    """
    manager = get_workspace_manager(request.user)
    operations = manager.get_pending_reviews()

    return Response({
        'total': len(operations),
        'operations': WorkspaceOperationDetailSerializer(operations, many=True).data,
    })
