"""
SKIN Layer Models - Project Execution System

The SKIN is the boundary layer where the AI system interfaces with actual
project workspaces. It's the execution environment that turns AI-generated
code into real, working software.

Human Body Metaphor:
    CONSCIOUSNESS     = Human Operator
    EYES/EARS         = Human Interface Layer
    BRAIN             = ThinkingAgent
    NERVOUS SYSTEM    = Agent-Model Router
    ORGANS            = 72 Specialized Agents
    SENSORY           = 77 Spiders
    HANDS/SKIN        = THIS LAYER - touches the real world

Session: 695
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

User = get_user_model()


class ProjectWorkspace(models.Model):
    """
    A project workspace that agents can operate on.
    This is the 'SKIN' - the boundary between AI and the real world.

    Example:
        workspace = ProjectWorkspace.objects.create(
            user=user,
            name="my-saas-app",
            root_path="/Users/dev/my-saas-app",
            tech_stack={"frontend": "react", "backend": "django"}
        )
    """

    # Workspace Types
    WORKSPACE_TYPE_CHOICES = [
        ('local', 'Local Directory'),
        ('git_remote', 'Git Remote Repository'),
        ('sandbox', 'Isolated Sandbox'),
        ('container', 'Docker Container'),
    ]

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_workspaces'
    )
    name = models.CharField(
        max_length=200,
        help_text="Human-readable project name"
    )
    description = models.TextField(
        blank=True,
        help_text="Project description and notes"
    )

    # Location
    workspace_type = models.CharField(
        max_length=50,
        choices=WORKSPACE_TYPE_CHOICES,
        default='local'
    )
    root_path = models.CharField(
        max_length=500,
        help_text="Absolute path to project root (e.g., /Users/dev/my-project)"
    )
    git_remote_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Git remote URL if applicable"
    )

    # Tech Stack (auto-detected or manually specified)
    tech_stack = models.JSONField(
        default=dict,
        help_text="""
        Detected or configured tech stack. Example:
        {
            "frontend": "react",
            "backend": "django",
            "database": "postgresql",
            "styling": "tailwind",
            "testing": "pytest"
        }
        """
    )

    # Entry Points (where different types of code live)
    entry_points = models.JSONField(
        default=dict,
        help_text="""
        Key directories in the project. Example:
        {
            "frontend_root": "frontend/src",
            "backend_root": "core",
            "tests": "tests",
            "config": "settings"
        }
        """
    )

    # Permissions & Safety
    allow_file_write = models.BooleanField(
        default=True,
        help_text="Allow agents to create/modify files"
    )
    allow_file_delete = models.BooleanField(
        default=False,
        help_text="Allow agents to delete files (dangerous)"
    )
    allow_command_execution = models.BooleanField(
        default=True,
        help_text="Allow agents to run shell commands"
    )
    allow_git_operations = models.BooleanField(
        default=True,
        help_text="Allow agents to perform git operations"
    )
    protected_paths = ArrayField(
        models.CharField(max_length=200),
        default=list,
        blank=True,
        help_text="Paths that agents cannot modify (e.g., ['.env', 'secrets/'])"
    )
    require_human_review = models.BooleanField(
        default=False,
        help_text="Require human approval before applying changes"
    )

    # Current State
    is_active = models.BooleanField(
        default=False,
        help_text="Is this the currently active workspace for the user?"
    )
    last_operation_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When was the last operation performed?"
    )
    current_branch = models.CharField(
        max_length=100,
        blank=True,
        help_text="Current git branch"
    )

    # Statistics
    total_operations = models.IntegerField(
        default=0,
        help_text="Total operations performed on this workspace"
    )
    total_files_written = models.IntegerField(
        default=0,
        help_text="Total files created/modified"
    )
    total_commits = models.IntegerField(
        default=0,
        help_text="Total git commits made by agents"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_project_workspaces'
        ordering = ['-updated_at']
        verbose_name = 'Project Workspace'
        verbose_name_plural = 'Project Workspaces'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', '-updated_at']),
        ]
        constraints = [
            # Only one active workspace per user
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_active=True),
                name='unique_active_workspace_per_user'
            )
        ]

    def __str__(self):
        active_marker = " [ACTIVE]" if self.is_active else ""
        return f"{self.name}{active_marker} ({self.root_path})"

    def save(self, *args, **kwargs):
        # If setting this workspace as active, deactivate others
        if self.is_active:
            ProjectWorkspace.objects.filter(
                user=self.user,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @property
    def frontend_framework(self):
        """Get the frontend framework from tech stack."""
        return self.tech_stack.get('frontend', 'unknown')

    @property
    def backend_framework(self):
        """Get the backend framework from tech stack."""
        return self.tech_stack.get('backend', 'unknown')


class WorkspaceOperation(models.Model):
    """
    Record of every file/command operation performed by agents.
    Complete audit trail for debugging and rollback.

    Every operation stores before/after state to enable:
    - Full audit trail
    - Rollback to previous state
    - Learning from successful/failed operations
    """

    # Operation Types
    OPERATION_TYPE_CHOICES = [
        ('file_create', 'Create File'),
        ('file_modify', 'Modify File'),
        ('file_delete', 'Delete File'),
        ('file_rename', 'Rename File'),
        ('command_exec', 'Execute Command'),
        ('git_commit', 'Git Commit'),
        ('git_branch', 'Git Branch'),
        ('git_checkout', 'Git Checkout'),
        ('git_merge', 'Git Merge'),
        ('build_run', 'Run Build'),
        ('test_run', 'Run Tests'),
        ('lint_run', 'Run Linter'),
        ('deploy', 'Deploy'),
    ]

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        ProjectWorkspace,
        on_delete=models.CASCADE,
        related_name='operations'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workspace_operations'
    )

    # What agent performed this?
    agent_name = models.CharField(
        max_length=100,
        help_text="Name of the agent that performed this operation"
    )
    agent_task = models.TextField(
        blank=True,
        help_text="The task description that led to this operation"
    )

    # Operation Details
    operation_type = models.CharField(
        max_length=50,
        choices=OPERATION_TYPE_CHOICES
    )

    # File Operations
    file_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Relative path to the file (from workspace root)"
    )
    file_content_before = models.TextField(
        blank=True,
        help_text="File content before operation (for rollback)"
    )
    file_content_after = models.TextField(
        blank=True,
        help_text="File content after operation"
    )
    file_size_before = models.IntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes before operation"
    )
    file_size_after = models.IntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes after operation"
    )

    # Command Operations
    command = models.TextField(
        blank=True,
        help_text="Command that was executed"
    )
    command_output = models.TextField(
        blank=True,
        help_text="stdout from command execution"
    )
    command_error = models.TextField(
        blank=True,
        help_text="stderr from command execution"
    )
    exit_code = models.IntegerField(
        null=True,
        blank=True,
        help_text="Command exit code (0 = success)"
    )

    # Result
    success = models.BooleanField(
        default=False,
        help_text="Did the operation succeed?"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if operation failed"
    )
    execution_time_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="How long the operation took in milliseconds"
    )

    # Human Review
    requires_review = models.BooleanField(
        default=False,
        help_text="Does this operation require human review?"
    )
    reviewed_by_human = models.BooleanField(
        default=False,
        help_text="Has a human reviewed this operation?"
    )
    human_approved = models.BooleanField(
        null=True,
        blank=True,
        help_text="Did the human approve this operation?"
    )
    human_feedback = models.TextField(
        blank=True,
        help_text="Human feedback on the operation"
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When was this reviewed?"
    )

    # Rollback Support
    can_rollback = models.BooleanField(
        default=True,
        help_text="Can this operation be rolled back?"
    )
    rolled_back = models.BooleanField(
        default=False,
        help_text="Has this operation been rolled back?"
    )
    rollback_operation = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='rollback_of',
        help_text="The operation that rolled back this one"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_workspace_operations'
        ordering = ['-created_at']
        verbose_name = 'Workspace Operation'
        verbose_name_plural = 'Workspace Operations'
        indexes = [
            models.Index(fields=['workspace', '-created_at']),
            models.Index(fields=['workspace', 'operation_type']),
            models.Index(fields=['agent_name', '-created_at']),
            models.Index(fields=['workspace', 'file_path']),
            models.Index(fields=['requires_review', 'reviewed_by_human']),
        ]

    def __str__(self):
        status = "✅" if self.success else "❌"
        return f"{status} {self.operation_type}: {self.file_path or self.command[:50]}"

    @property
    def is_file_operation(self):
        """Check if this is a file-related operation."""
        return self.operation_type in ['file_create', 'file_modify', 'file_delete', 'file_rename']

    @property
    def is_git_operation(self):
        """Check if this is a git-related operation."""
        return self.operation_type.startswith('git_')

    @property
    def lines_changed(self):
        """Calculate approximate lines changed for file operations."""
        if not self.is_file_operation:
            return 0
        before_lines = len(self.file_content_before.split('\n')) if self.file_content_before else 0
        after_lines = len(self.file_content_after.split('\n')) if self.file_content_after else 0
        return abs(after_lines - before_lines)

    def get_diff(self):
        """Get a unified diff of the file changes."""
        import difflib
        if not self.is_file_operation:
            return None

        before_lines = self.file_content_before.splitlines(keepends=True)
        after_lines = self.file_content_after.splitlines(keepends=True)

        diff = difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile=f'a/{self.file_path}',
            tofile=f'b/{self.file_path}'
        )
        return ''.join(diff)


class WorkspaceContext(models.Model):
    """
    Cached understanding of a project's structure.
    Agents use this to know WHERE to put generated code.

    This is scanned and updated periodically to give agents
    context about the project they're working on.
    """

    # Identity
    workspace = models.OneToOneField(
        ProjectWorkspace,
        on_delete=models.CASCADE,
        related_name='context',
        primary_key=True
    )

    # File Structure Map
    file_tree = models.JSONField(
        default=dict,
        help_text="""
        Directory structure with files. Example:
        {
            "frontend/src/components": ["Button.tsx", "Modal.tsx"],
            "frontend/src/pages": ["Dashboard.tsx", "Settings.tsx"],
            "core/agents": ["image_agent.py", "research_agent.py"]
        }
        """
    )

    # Key File Identification
    key_files = models.JSONField(
        default=dict,
        help_text="""
        Important files that agents should know about. Example:
        {
            "main_entry": "frontend/src/App.tsx",
            "routes": "frontend/src/routes.tsx",
            "api_client": "frontend/src/api/client.ts",
            "models": "core/models.py",
            "urls": "core/urls.py",
            "settings": "core/settings.py"
        }
        """
    )

    # Pattern Recognition
    coding_patterns = models.JSONField(
        default=dict,
        help_text="""
        Recognized patterns in the codebase. Example:
        {
            "component_pattern": "PascalCase.tsx in components/",
            "hook_pattern": "use*.ts in hooks/",
            "api_pattern": "REST with axios, base URL from env",
            "test_pattern": "test_*.py in tests/"
        }
        """
    )

    # Dependencies
    dependencies = models.JSONField(
        default=dict,
        help_text="""
        Project dependencies. Example:
        {
            "frontend": {"react": "18.2.0", "tailwindcss": "3.3.0"},
            "backend": {"django": "5.0", "djangorestframework": "3.14"}
        }
        """
    )

    # Import Map (for understanding imports)
    import_aliases = models.JSONField(
        default=dict,
        help_text="""
        Import aliases/paths configured in the project. Example:
        {
            "@/components": "src/components",
            "@/utils": "src/utils",
            "@/api": "src/api"
        }
        """
    )

    # Directory Purposes
    directory_purposes = models.JSONField(
        default=dict,
        help_text="""
        What each directory is for. Example:
        {
            "frontend/src/components": "Reusable UI components",
            "frontend/src/pages": "Route page components",
            "frontend/src/hooks": "Custom React hooks",
            "core/agents": "AI agent implementations",
            "core/services": "Business logic services"
        }
        """
    )

    # Statistics
    total_files = models.IntegerField(
        default=0,
        help_text="Total files in workspace"
    )
    total_directories = models.IntegerField(
        default=0,
        help_text="Total directories in workspace"
    )
    total_lines_of_code = models.IntegerField(
        default=0,
        help_text="Approximate total lines of code"
    )

    # File Type Breakdown
    file_type_counts = models.JSONField(
        default=dict,
        help_text="""
        Count of files by extension. Example:
        {
            ".py": 234,
            ".tsx": 89,
            ".ts": 45,
            ".css": 12
        }
        """
    )

    # Scan Metadata
    last_scanned_at = models.DateTimeField(
        auto_now=True,
        help_text="When was this context last updated?"
    )
    scan_depth = models.IntegerField(
        default=5,
        help_text="How deep the directory scan went"
    )
    scan_duration_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="How long the scan took"
    )
    excluded_patterns = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text="Patterns excluded from scan (e.g., ['node_modules', '__pycache__'])"
    )

    class Meta:
        db_table = 'core_workspace_contexts'
        verbose_name = 'Workspace Context'
        verbose_name_plural = 'Workspace Contexts'

    def __str__(self):
        return f"Context for {self.workspace.name} ({self.total_files} files)"

    def get_directory_for_file_type(self, file_extension: str) -> str:
        """
        Suggest the best directory for a file based on its extension.
        Uses existing patterns in the codebase.
        """
        extension_to_dirs = {
            '.tsx': ['components', 'pages', 'src/components', 'frontend/src/components'],
            '.jsx': ['components', 'pages', 'src/components'],
            '.ts': ['utils', 'hooks', 'services', 'src/utils'],
            '.js': ['utils', 'lib', 'src'],
            '.py': ['core', 'services', 'agents', 'utils'],
            '.css': ['styles', 'css', 'src/styles'],
            '.scss': ['styles', 'scss', 'src/styles'],
        }

        preferred_dirs = extension_to_dirs.get(file_extension, [])

        # Check which preferred dirs exist in our file tree
        for dir_path in preferred_dirs:
            if dir_path in self.file_tree:
                return dir_path

        # Fallback: find any directory with this file type
        for dir_path, files in self.file_tree.items():
            if any(f.endswith(file_extension) for f in files):
                return dir_path

        # Ultimate fallback
        return '.'

    def get_similar_files(self, filename: str, limit: int = 5) -> list:
        """
        Find files with similar names in the workspace.
        Useful for understanding naming patterns.
        """
        similar = []
        name_parts = filename.lower().replace('.', ' ').replace('_', ' ').replace('-', ' ').split()

        for dir_path, files in self.file_tree.items():
            for f in files:
                f_parts = f.lower().replace('.', ' ').replace('_', ' ').replace('-', ' ').split()
                # Check for any common words
                common = set(name_parts) & set(f_parts)
                if common:
                    similar.append({
                        'path': f"{dir_path}/{f}",
                        'common_terms': list(common)
                    })

        return sorted(similar, key=lambda x: len(x['common_terms']), reverse=True)[:limit]
