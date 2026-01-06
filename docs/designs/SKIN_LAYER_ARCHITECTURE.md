# SKIN Layer Architecture - Project Execution System

**Session:** 695
**Status:** Design Phase
**Purpose:** Connect the AI body (agents) to actual project workspaces where code gets written and executed

---

## The Problem

The current system has a complete "body" but no "skin" - no boundary layer where the AI actually touches and modifies the external world (projects):

```
Current State:
┌─────────────────────────────────────────────────────────────┐
│  HUMAN INTERFACE    → Reviews/approves                      │
│  BRAIN              → ThinkingAgent reasons                 │
│  NERVOUS SYSTEM     → Routes to agents                      │
│  ORGANS             → 72 agents generate TEXT               │
│  SENSORY            → 77 spiders gather data                │
│                                                              │
│     ↓ ↓ ↓  CODE AS TEXT GOES... NOWHERE  ↓ ↓ ↓              │
│                                                              │
│  GeneratedCode model: stores text, never executed           │
│  ai_generated_projects/: orphaned, disconnected             │
└─────────────────────────────────────────────────────────────┘
```

**Example of the Gap:**
```
User: "Add a dark mode toggle to Settings"
→ FullStackDeveloperAgent generates React component (as text)
→ Returns: {"code": "...", "files": [...]}
→ ??? WHERE DOES THIS GO ???
→ User sees text, has to manually copy/paste
```

---

## The Solution: SKIN Layer

The SKIN is the **boundary layer** where the AI system interfaces with actual project workspaces. It's the execution environment that turns AI-generated code into real, working software.

```
Complete Architecture:
┌─────────────────────────────────────────────────────────────┐
│                     HUMAN OPERATOR                           │
│          (Reviews, Approves, Overrides, Controls)            │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                  HUMAN INTERFACE LAYER                       │
│        Attention Aggregator │ Feedback │ Control Panel       │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      BRAIN LAYER                             │
│                    (ThinkingAgent)                           │
│            Autonomous reasoning & decision-making            │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                  NERVOUS SYSTEM LAYER                        │
│                  (Agent-Model Router)                        │
│         ML auto-selection, signal routing, optimization      │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      ORGAN LAYER                             │
│                 (72+ Specialized Agents)                     │
│    Research │ Content │ Code │ Stocks │ Blockchain │ Legal   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Generated Code/Content
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                                                              │
│                    ★ SKIN LAYER ★                            │
│               (Project Execution System)                     │
│                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │  Workspace  │ │    File     │ │   Build     │            │
│  │   Manager   │ │   Writer    │ │  Pipeline   │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │     Git     │ │    Test     │ │  Deployment │            │
│  │  Integrator │ │   Runner    │ │   Manager   │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
│                                                              │
│  Active Projects:                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ /Users/dev/my-saas-app        [React + Django]       │   │
│  │ /Users/dev/mobile-app         [React Native]         │   │
│  │ /Users/dev/unified-donkey-betz [This Platform]       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Actual Files Written
                            │ Tests Executed
                            │ Builds Run
                            ▼
                    ┌───────────────┐
                    │  REAL WORLD   │
                    │  File System  │
                    │  Git Repos    │
                    │  CI/CD        │
                    └───────────────┘
```

---

## Core Components

### 1. ProjectWorkspace Model

The **central model** that represents a target project the AI is working on.

```python
class ProjectWorkspace(models.Model):
    """
    A project workspace that agents can operate on.
    This is the 'SKIN' - the boundary between AI and the real world.
    """

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Location
    workspace_type = models.CharField(max_length=50, choices=[
        ('local', 'Local Directory'),
        ('git_remote', 'Git Remote Repository'),
        ('sandbox', 'Isolated Sandbox'),
        ('container', 'Docker Container'),
    ])
    root_path = models.CharField(max_length=500)  # /Users/dev/my-project
    git_remote_url = models.CharField(max_length=500, blank=True)

    # Tech Stack (what the project uses)
    tech_stack = models.JSONField(default=dict)
    # {
    #     "frontend": "react",
    #     "backend": "django",
    #     "database": "postgresql",
    #     "styling": "tailwind",
    #     "testing": "pytest"
    # }

    # Structure Understanding
    entry_points = models.JSONField(default=dict)
    # {
    #     "frontend_root": "frontend/src",
    #     "backend_root": "core",
    #     "tests": "tests",
    #     "config": "settings"
    # }

    # Permissions & Safety
    allow_file_write = models.BooleanField(default=True)
    allow_file_delete = models.BooleanField(default=False)
    allow_command_execution = models.BooleanField(default=True)
    allow_git_operations = models.BooleanField(default=True)
    protected_paths = models.JSONField(default=list)  # [".env", "secrets/"]

    # Current State
    is_active = models.BooleanField(default=True)
    last_operation_at = models.DateTimeField(null=True)
    current_branch = models.CharField(max_length=100, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_project_workspaces'
        ordering = ['-updated_at']
```

### 2. WorkspaceOperation Model

**Audit trail** of every operation performed on a workspace.

```python
class WorkspaceOperation(models.Model):
    """
    Record of every file/command operation performed by agents.
    Complete audit trail for debugging and rollback.
    """

    workspace = models.ForeignKey(ProjectWorkspace, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # What agent performed this?
    agent_name = models.CharField(max_length=100)
    agent_task = models.TextField()  # "Add dark mode toggle"

    # Operation Details
    operation_type = models.CharField(max_length=50, choices=[
        ('file_create', 'Create File'),
        ('file_modify', 'Modify File'),
        ('file_delete', 'Delete File'),
        ('command_exec', 'Execute Command'),
        ('git_commit', 'Git Commit'),
        ('git_branch', 'Git Branch'),
        ('build_run', 'Run Build'),
        ('test_run', 'Run Tests'),
        ('deploy', 'Deploy'),
    ])

    # File Operations
    file_path = models.CharField(max_length=500, blank=True)
    file_content_before = models.TextField(blank=True)  # For rollback
    file_content_after = models.TextField(blank=True)

    # Command Operations
    command = models.TextField(blank=True)
    command_output = models.TextField(blank=True)
    exit_code = models.IntegerField(null=True)

    # Result
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    execution_time_ms = models.IntegerField(null=True)

    # Human Review
    reviewed_by_human = models.BooleanField(default=False)
    human_approved = models.BooleanField(null=True)
    human_feedback = models.TextField(blank=True)

    # Rollback Support
    can_rollback = models.BooleanField(default=True)
    rolled_back = models.BooleanField(default=False)
    rollback_operation = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_workspace_operations'
        ordering = ['-created_at']
```

### 3. WorkspaceContext Model

**Cached understanding** of a project's structure for efficient agent operations.

```python
class WorkspaceContext(models.Model):
    """
    Cached understanding of a project's structure.
    Agents use this to know WHERE to put generated code.
    """

    workspace = models.OneToOneField(ProjectWorkspace, on_delete=models.CASCADE)

    # File Structure Map
    file_tree = models.JSONField(default=dict)
    # {
    #     "frontend/src/components": ["Button.tsx", "Modal.tsx", ...],
    #     "frontend/src/pages": ["Dashboard.tsx", "Settings.tsx", ...],
    #     "core/agents": ["image_agent.py", "research_agent.py", ...],
    # }

    # Key File Identification
    key_files = models.JSONField(default=dict)
    # {
    #     "main_entry": "frontend/src/App.tsx",
    #     "routes": "frontend/src/routes.tsx",
    #     "api_client": "frontend/src/api/client.ts",
    #     "models": "core/models.py",
    #     "urls": "core/urls.py",
    # }

    # Pattern Recognition
    coding_patterns = models.JSONField(default=dict)
    # {
    #     "component_pattern": "PascalCase.tsx in components/",
    #     "hook_pattern": "use*.ts in hooks/",
    #     "api_pattern": "REST with axios, base URL from env",
    # }

    # Dependencies
    dependencies = models.JSONField(default=dict)
    # {
    #     "frontend": {"react": "18.2.0", "tailwindcss": "3.3.0"},
    #     "backend": {"django": "5.0", "djangorestframework": "3.14"}
    # }

    # Last Scan
    last_scanned_at = models.DateTimeField(auto_now=True)
    scan_depth = models.IntegerField(default=5)
    total_files = models.IntegerField(default=0)

    class Meta:
        db_table = 'core_workspace_contexts'
```

---

## Core Services

### 1. WorkspaceManager Service

**Central orchestrator** for all workspace operations.

```python
class WorkspaceManager:
    """
    Central service for managing project workspaces.
    This is the main interface between agents and the file system.
    """

    def __init__(self, user: User):
        self.user = user
        self.file_writer = FileWriter()
        self.git_integrator = GitIntegrator()
        self.build_pipeline = BuildPipeline()
        self.test_runner = TestRunner()

    # ==================== Workspace Management ====================

    def register_workspace(self, root_path: str, name: str = None) -> ProjectWorkspace:
        """
        Register an existing project directory as a workspace.
        Scans and understands the project structure.
        """
        # Validate path exists
        path = Path(root_path)
        if not path.exists():
            raise ValueError(f"Path does not exist: {root_path}")

        # Auto-detect tech stack
        tech_stack = self._detect_tech_stack(path)

        # Create workspace
        workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name=name or path.name,
            root_path=str(path.resolve()),
            workspace_type='local',
            tech_stack=tech_stack,
        )

        # Scan and cache structure
        self._scan_workspace(workspace)

        return workspace

    def get_active_workspace(self) -> Optional[ProjectWorkspace]:
        """Get the user's currently active workspace."""
        return ProjectWorkspace.objects.filter(
            user=self.user,
            is_active=True
        ).first()

    def set_active_workspace(self, workspace_id: UUID) -> ProjectWorkspace:
        """Set a workspace as the active target for operations."""
        # Deactivate all others
        ProjectWorkspace.objects.filter(user=self.user).update(is_active=False)

        # Activate this one
        workspace = ProjectWorkspace.objects.get(id=workspace_id, user=self.user)
        workspace.is_active = True
        workspace.save()

        return workspace

    # ==================== Agent Interface ====================

    def execute_agent_output(
        self,
        workspace: ProjectWorkspace,
        agent_name: str,
        agent_result: Dict[str, Any],
        auto_apply: bool = False
    ) -> Dict[str, Any]:
        """
        Take an agent's output and apply it to the workspace.
        This is the KEY BRIDGE between agents and file system.

        Args:
            workspace: Target workspace
            agent_name: Which agent produced this output
            agent_result: The agent's return value with 'files' or 'code'
            auto_apply: If True, write immediately. If False, queue for review.

        Returns:
            Execution result with file paths and status
        """
        operations = []

        # Extract files from agent result
        files_to_write = self._extract_files_from_result(agent_result)

        for file_info in files_to_write:
            # Determine target path using workspace context
            target_path = self._resolve_file_path(workspace, file_info)

            # Check permissions
            if not self._check_write_permission(workspace, target_path):
                operations.append({
                    'file': target_path,
                    'status': 'blocked',
                    'reason': 'Path is protected'
                })
                continue

            if auto_apply:
                # Write immediately
                result = self.file_writer.write_file(
                    workspace=workspace,
                    file_path=target_path,
                    content=file_info['content'],
                    agent_name=agent_name
                )
                operations.append(result)
            else:
                # Queue for human review
                result = self._queue_for_review(
                    workspace=workspace,
                    file_path=target_path,
                    content=file_info['content'],
                    agent_name=agent_name
                )
                operations.append(result)

        return {
            'success': all(op.get('success', False) for op in operations),
            'operations': operations,
            'workspace': workspace.name,
            'agent': agent_name
        }

    def get_workspace_context_for_agent(
        self,
        workspace: ProjectWorkspace,
        agent_name: str,
        task: str
    ) -> Dict[str, Any]:
        """
        Get relevant workspace context for an agent to use.
        Agents call this to understand WHERE to put their output.
        """
        context = workspace.workspacecontext

        # Determine what parts of the project are relevant
        relevant_paths = self._get_relevant_paths(context, agent_name, task)

        return {
            'workspace_name': workspace.name,
            'root_path': workspace.root_path,
            'tech_stack': workspace.tech_stack,
            'key_files': context.key_files,
            'relevant_paths': relevant_paths,
            'coding_patterns': context.coding_patterns,
            'dependencies': context.dependencies,
            'protected_paths': workspace.protected_paths,
        }

    # ==================== File Operations ====================

    def read_file(self, workspace: ProjectWorkspace, file_path: str) -> Optional[str]:
        """Read a file from the workspace."""
        full_path = Path(workspace.root_path) / file_path
        if full_path.exists():
            return full_path.read_text()
        return None

    def write_file(
        self,
        workspace: ProjectWorkspace,
        file_path: str,
        content: str,
        agent_name: str
    ) -> WorkspaceOperation:
        """Write a file to the workspace with audit logging."""
        return self.file_writer.write_file(
            workspace=workspace,
            file_path=file_path,
            content=content,
            agent_name=agent_name
        )

    def list_files(self, workspace: ProjectWorkspace, pattern: str = "**/*") -> List[str]:
        """List files in the workspace matching a pattern."""
        root = Path(workspace.root_path)
        return [str(p.relative_to(root)) for p in root.glob(pattern) if p.is_file()]

    # ==================== Build & Test ====================

    def run_build(self, workspace: ProjectWorkspace) -> WorkspaceOperation:
        """Run the project's build command."""
        return self.build_pipeline.run_build(workspace)

    def run_tests(self, workspace: ProjectWorkspace, test_path: str = None) -> WorkspaceOperation:
        """Run project tests."""
        return self.test_runner.run_tests(workspace, test_path)

    def run_linter(self, workspace: ProjectWorkspace) -> WorkspaceOperation:
        """Run linter/formatter on the project."""
        return self.build_pipeline.run_linter(workspace)

    # ==================== Git Operations ====================

    def git_status(self, workspace: ProjectWorkspace) -> Dict[str, Any]:
        """Get git status of the workspace."""
        return self.git_integrator.status(workspace)

    def git_commit(
        self,
        workspace: ProjectWorkspace,
        message: str,
        agent_name: str
    ) -> WorkspaceOperation:
        """Create a git commit."""
        return self.git_integrator.commit(workspace, message, agent_name)

    def git_create_branch(self, workspace: ProjectWorkspace, branch_name: str) -> WorkspaceOperation:
        """Create a new branch for agent work."""
        return self.git_integrator.create_branch(workspace, branch_name)

    # ==================== Internal Methods ====================

    def _detect_tech_stack(self, path: Path) -> Dict[str, str]:
        """Auto-detect the tech stack of a project."""
        tech_stack = {}

        # Check for package.json (Node.js/React/Vue)
        if (path / 'package.json').exists():
            pkg = json.loads((path / 'package.json').read_text())
            deps = pkg.get('dependencies', {})

            if 'react' in deps:
                tech_stack['frontend'] = 'react'
            elif 'vue' in deps:
                tech_stack['frontend'] = 'vue'
            elif 'next' in deps:
                tech_stack['frontend'] = 'nextjs'

            if 'express' in deps:
                tech_stack['backend'] = 'express'

        # Check for requirements.txt or pyproject.toml (Python)
        if (path / 'requirements.txt').exists():
            reqs = (path / 'requirements.txt').read_text().lower()
            if 'django' in reqs:
                tech_stack['backend'] = 'django'
            elif 'fastapi' in reqs:
                tech_stack['backend'] = 'fastapi'
            elif 'flask' in reqs:
                tech_stack['backend'] = 'flask'

        # Check for manage.py (Django)
        if (path / 'manage.py').exists():
            tech_stack['backend'] = 'django'

        # Check for docker-compose.yml
        if (path / 'docker-compose.yml').exists():
            tech_stack['containerization'] = 'docker'

        return tech_stack

    def _scan_workspace(self, workspace: ProjectWorkspace):
        """Scan workspace and create/update WorkspaceContext."""
        root = Path(workspace.root_path)

        # Build file tree
        file_tree = {}
        key_files = {}

        for path in root.rglob('*'):
            if path.is_file():
                rel_path = path.relative_to(root)

                # Skip hidden and node_modules
                if any(part.startswith('.') for part in rel_path.parts):
                    continue
                if 'node_modules' in rel_path.parts:
                    continue
                if '__pycache__' in rel_path.parts:
                    continue

                dir_path = str(rel_path.parent)
                if dir_path not in file_tree:
                    file_tree[dir_path] = []
                file_tree[dir_path].append(rel_path.name)

                # Identify key files
                name = rel_path.name.lower()
                if name == 'app.tsx' or name == 'app.jsx':
                    key_files['main_entry'] = str(rel_path)
                elif name == 'routes.tsx' or name == 'router.tsx':
                    key_files['routes'] = str(rel_path)
                elif name == 'urls.py':
                    key_files['urls'] = str(rel_path)
                elif name == 'models.py':
                    key_files['models'] = str(rel_path)

        # Create or update context
        WorkspaceContext.objects.update_or_create(
            workspace=workspace,
            defaults={
                'file_tree': file_tree,
                'key_files': key_files,
                'total_files': sum(len(files) for files in file_tree.values())
            }
        )

    def _extract_files_from_result(self, agent_result: Dict) -> List[Dict]:
        """Extract file information from an agent's result."""
        files = []

        # Handle 'files' key (list of file dicts)
        if 'files' in agent_result:
            for f in agent_result['files']:
                files.append({
                    'filename': f.get('filename', 'unknown'),
                    'content': f.get('content', ''),
                    'language': f.get('language', 'text')
                })

        # Handle 'code' key (single code block)
        elif 'code' in agent_result:
            # Try to parse filename from content
            files.append({
                'filename': 'generated_code',
                'content': agent_result['code'],
                'language': 'auto'
            })

        return files

    def _resolve_file_path(self, workspace: ProjectWorkspace, file_info: Dict) -> str:
        """
        Intelligently determine where a file should go based on:
        - File extension/language
        - Workspace structure
        - Existing patterns
        """
        filename = file_info['filename']
        language = file_info.get('language', '')
        context = workspace.workspacecontext

        # Use existing patterns from workspace
        if filename.endswith('.tsx') or filename.endswith('.jsx'):
            # React component - put in components directory
            if 'components' in context.file_tree:
                return f"components/{filename}"
            elif 'frontend/src/components' in context.file_tree:
                return f"frontend/src/components/{filename}"

        elif filename.endswith('.py'):
            # Python file
            if 'core' in context.file_tree:
                return f"core/{filename}"

        # Default: put in project root
        return filename
```

### 2. FileWriter Service

```python
class FileWriter:
    """
    Handles safe file writing with rollback support.
    """

    def write_file(
        self,
        workspace: ProjectWorkspace,
        file_path: str,
        content: str,
        agent_name: str
    ) -> WorkspaceOperation:
        """Write a file with full audit trail."""
        full_path = Path(workspace.root_path) / file_path

        # Capture before state for rollback
        content_before = ''
        operation_type = 'file_create'
        if full_path.exists():
            content_before = full_path.read_text()
            operation_type = 'file_modify'

        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        try:
            full_path.write_text(content)
            success = True
            error = ''
        except Exception as e:
            success = False
            error = str(e)

        # Create operation record
        operation = WorkspaceOperation.objects.create(
            workspace=workspace,
            user=workspace.user,
            agent_name=agent_name,
            operation_type=operation_type,
            file_path=file_path,
            file_content_before=content_before,
            file_content_after=content,
            success=success,
            error_message=error,
        )

        return operation

    def rollback_operation(self, operation: WorkspaceOperation) -> WorkspaceOperation:
        """Rollback a file operation to its previous state."""
        if not operation.can_rollback:
            raise ValueError("This operation cannot be rolled back")

        full_path = Path(operation.workspace.root_path) / operation.file_path

        if operation.operation_type == 'file_create':
            # Delete the created file
            full_path.unlink()
        elif operation.operation_type == 'file_modify':
            # Restore previous content
            full_path.write_text(operation.file_content_before)

        operation.rolled_back = True
        operation.save()

        # Create rollback operation record
        rollback_op = WorkspaceOperation.objects.create(
            workspace=operation.workspace,
            user=operation.user,
            agent_name='system_rollback',
            operation_type='file_modify',
            file_path=operation.file_path,
            file_content_before=operation.file_content_after,
            file_content_after=operation.file_content_before,
            success=True,
        )

        operation.rollback_operation = rollback_op
        operation.save()

        return rollback_op
```

### 3. GitIntegrator Service

```python
class GitIntegrator:
    """Handles git operations on workspaces."""

    def status(self, workspace: ProjectWorkspace) -> Dict[str, Any]:
        """Get git status."""
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=workspace.root_path,
            capture_output=True,
            text=True
        )

        return {
            'branch': self._get_current_branch(workspace),
            'modified': [l[3:] for l in result.stdout.split('\n') if l.startswith(' M')],
            'added': [l[3:] for l in result.stdout.split('\n') if l.startswith('A ')],
            'untracked': [l[3:] for l in result.stdout.split('\n') if l.startswith('??')],
        }

    def commit(
        self,
        workspace: ProjectWorkspace,
        message: str,
        agent_name: str
    ) -> WorkspaceOperation:
        """Create a commit."""
        # Stage all changes
        subprocess.run(['git', 'add', '-A'], cwd=workspace.root_path)

        # Create commit with agent attribution
        full_message = f"{message}\n\n🤖 Generated by {agent_name}"
        result = subprocess.run(
            ['git', 'commit', '-m', full_message],
            cwd=workspace.root_path,
            capture_output=True,
            text=True
        )

        return WorkspaceOperation.objects.create(
            workspace=workspace,
            user=workspace.user,
            agent_name=agent_name,
            operation_type='git_commit',
            command=f'git commit -m "{message}"',
            command_output=result.stdout + result.stderr,
            exit_code=result.returncode,
            success=result.returncode == 0,
        )

    def create_branch(self, workspace: ProjectWorkspace, branch_name: str) -> WorkspaceOperation:
        """Create a new branch for agent work."""
        result = subprocess.run(
            ['git', 'checkout', '-b', branch_name],
            cwd=workspace.root_path,
            capture_output=True,
            text=True
        )

        workspace.current_branch = branch_name
        workspace.save()

        return WorkspaceOperation.objects.create(
            workspace=workspace,
            user=workspace.user,
            agent_name='workspace_manager',
            operation_type='git_branch',
            command=f'git checkout -b {branch_name}',
            command_output=result.stdout + result.stderr,
            exit_code=result.returncode,
            success=result.returncode == 0,
        )
```

---

## Integration with Agent System

### Modified Agent Base Class

```python
class BaseAgent:
    """Updated BaseAgent with SKIN layer integration."""

    def execute(self, task: str, context: Dict, workspace: ProjectWorkspace = None, **kwargs):
        """
        Execute agent task.

        If workspace is provided, agent output will be written to files.
        If not, agent returns code as text (legacy behavior).
        """
        # Get workspace context if available
        workspace_context = None
        if workspace:
            workspace_manager = WorkspaceManager(self.user)
            workspace_context = workspace_manager.get_workspace_context_for_agent(
                workspace=workspace,
                agent_name=self.name,
                task=task
            )

        # Build prompt with workspace context
        full_prompt = self._build_prompt(task, context, workspace_context)

        # Execute agent logic
        result = self._execute_internal(full_prompt)

        # If workspace provided, write files
        if workspace and result.get('files'):
            workspace_manager.execute_agent_output(
                workspace=workspace,
                agent_name=self.name,
                agent_result=result,
                auto_apply=kwargs.get('auto_apply', False)
            )

        return result
```

### PA Tool: `workspace_tool`

```python
# New PA tool for workspace operations
WORKSPACE_TOOL = {
    "type": "function",
    "function": {
        "name": "workspace_tool",
        "description": """Manage project workspaces that agents work on.

USE THIS WHEN:
- User wants to set up a project for AI to work on
- User asks "work on my project at /path/to/project"
- User wants to see what projects are registered
- User wants to switch between projects
""",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["register", "list", "set_active", "scan", "status"],
                    "description": "Action to perform"
                },
                "path": {
                    "type": "string",
                    "description": "Project path (for register action)"
                },
                "workspace_id": {
                    "type": "string",
                    "description": "Workspace ID (for set_active action)"
                }
            },
            "required": ["action"]
        }
    }
}
```

---

## User Flow Examples

### Example 1: Setting Up a Workspace

```
User: "I want you to work on my project at /Users/dev/my-saas-app"

PA: [Uses workspace_tool with action='register', path='/Users/dev/my-saas-app']

System Response:
✅ Registered workspace: my-saas-app
📁 Path: /Users/dev/my-saas-app
🔧 Detected tech stack:
   - Frontend: React (18.2.0)
   - Backend: Django (5.0)
   - Database: PostgreSQL
📊 Scanned 234 files
🎯 Set as active workspace
```

### Example 2: Agent Writing Code

```
User: "Add a dark mode toggle to the Settings page"

PA: [Routes to FullStackDeveloperAgent with workspace context]

FullStackDeveloperAgent:
1. Receives workspace context (knows project structure)
2. Generates DarkModeToggle.tsx
3. Knows to put it in frontend/src/components/
4. Generates Settings.tsx modification
5. Returns result with file paths

SKIN Layer:
1. Receives agent output
2. Writes frontend/src/components/DarkModeToggle.tsx
3. Modifies frontend/src/pages/Settings.tsx
4. Creates WorkspaceOperation records
5. Runs linter
6. Shows diff to user

Result:
✅ Created: frontend/src/components/DarkModeToggle.tsx (45 lines)
✅ Modified: frontend/src/pages/Settings.tsx (+12 lines)
🔍 Linter: Passed
📝 Changes ready for review. Run tests? [Yes/No]
```

### Example 3: Rollback

```
User: "That broke the build, undo it"

PA: [Uses workspace_tool to rollback last operations]

SKIN Layer:
1. Finds last operations by this user
2. Reads file_content_before
3. Restores files
4. Creates rollback record

Result:
⏪ Rolled back 2 operations:
   - Restored: frontend/src/components/DarkModeToggle.tsx (deleted)
   - Restored: frontend/src/pages/Settings.tsx (reverted to previous)
```

---

## API Endpoints

```
# Workspace Management
POST   /api/workspaces/                    # Register new workspace
GET    /api/workspaces/                    # List user's workspaces
GET    /api/workspaces/{id}/               # Get workspace details
PUT    /api/workspaces/{id}/activate/      # Set as active workspace
POST   /api/workspaces/{id}/scan/          # Rescan workspace structure
DELETE /api/workspaces/{id}/               # Unregister workspace

# Operations
GET    /api/workspaces/{id}/operations/    # List operations
POST   /api/workspaces/{id}/operations/{op_id}/rollback/  # Rollback operation
GET    /api/workspaces/{id}/operations/{op_id}/diff/      # View diff

# Files
GET    /api/workspaces/{id}/files/         # List files
GET    /api/workspaces/{id}/files/{path}/  # Read file
POST   /api/workspaces/{id}/files/{path}/  # Write file (manual)

# Build/Test
POST   /api/workspaces/{id}/build/         # Run build
POST   /api/workspaces/{id}/test/          # Run tests
POST   /api/workspaces/{id}/lint/          # Run linter

# Git
GET    /api/workspaces/{id}/git/status/    # Git status
POST   /api/workspaces/{id}/git/commit/    # Create commit
POST   /api/workspaces/{id}/git/branch/    # Create branch
```

---

## Security Considerations

1. **Path Validation** - All paths must be within workspace root (no `../` escapes)
2. **Protected Paths** - `.env`, `secrets/`, credentials never modified
3. **Permission Model** - Separate flags for read/write/delete/execute
4. **Audit Trail** - Every operation logged with before/after state
5. **Rollback** - Any operation can be undone
6. **Human Review** - Option to queue changes for approval before applying
7. **Sandboxing** - Option to run in Docker container for isolation

---

## Implementation Order

| Phase | Component | Effort | Priority |
|-------|-----------|--------|----------|
| 1 | ProjectWorkspace model | Low | Required |
| 2 | WorkspaceOperation model | Low | Required |
| 3 | WorkspaceContext model | Low | Required |
| 4 | WorkspaceManager service | High | Core |
| 5 | FileWriter service | Medium | Core |
| 6 | workspace_tool for PA | Medium | Core |
| 7 | GitIntegrator service | Medium | High |
| 8 | BuildPipeline service | Medium | High |
| 9 | TestRunner service | Medium | High |
| 10 | API endpoints | Medium | High |
| 11 | UI for workspace management | High | Enhancement |
| 12 | Rollback system | Medium | Enhancement |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Code written to files | 100% | Agent output → actual files |
| Build success rate | > 80% | Generated code compiles |
| Test pass rate | > 70% | Generated code passes tests |
| Rollback success | 100% | All operations reversible |
| Time to first file | < 30s | From request to file written |

---

## Relationship to Human Body

```
Complete Human Body Metaphor:

CONSCIOUSNESS     = Human Operator (you)
EYES/EARS         = Human Interface Layer (attention stream)
BRAIN             = ThinkingAgent (reasoning)
NERVOUS SYSTEM    = Agent-Model Router (signal routing)
ORGANS            = 72 Specialized Agents (work execution)
SENSORY           = 77 Spiders (data gathering)
HANDS/SKIN        = SKIN Layer (touching the world)
                    ↓
                    Actual files written
                    Git commits made
                    Tests run
                    Builds executed
```

The SKIN is where the AI body **interfaces with reality** - where thoughts become actions, where generated code becomes actual files in actual projects.
