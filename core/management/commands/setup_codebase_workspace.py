"""
Session 884: Setup Codebase Workspace for Code Maintenance

Creates a ProjectWorkspace that points to the actual project codebase,
allowing CodeGeneratorAgent and CodeReviewAgent to read and modify
the real source code for maintenance purposes.

Unlike sandbox workspaces (generated_content/), this workspace:
- Points to the actual project root
- Has protected paths for sensitive files
- Allows controlled code modifications
- Is used for codebase maintenance, not content generation

Usage:
    # Local development
    python manage.py setup_codebase_workspace

    # Production (Railway)
    railway run python manage.py setup_codebase_workspace

    # Custom path
    python manage.py setup_codebase_workspace --path=/custom/path
"""

import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup a codebase workspace for code maintenance operations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help='Codebase root path (default: auto-detect based on environment)'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='donkey-betz-codebase',
            help='Workspace name (default: donkey-betz-codebase)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview without making changes'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Recreate workspace even if it exists'
        )
        parser.add_argument(
            '--read-only',
            action='store_true',
            help='Create as read-only (no file writes allowed)'
        )

    def handle(self, *args, **options):
        from core.models_skin_layer import ProjectWorkspace

        dry_run = options['dry_run']
        force = options['force']
        name = options['name']
        read_only = options['read_only']

        # Determine codebase path
        codebase_path = options['path']
        if not codebase_path:
            # Auto-detect based on environment
            if os.environ.get('RAILWAY_ENVIRONMENT'):
                # Railway: code is deployed to /app/
                codebase_path = '/app'
            else:
                # Local: use the Django project root
                codebase_path = str(Path(__file__).parent.parent.parent.parent)

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("CODEBASE WORKSPACE SETUP - Session 884"))
        self.stdout.write(self.style.NOTICE("=" * 60))

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY RUN MODE - No changes will be made\n"))

        self.stdout.write(f"\nConfiguration:")
        self.stdout.write(f"  Name: {name}")
        self.stdout.write(f"  Path: {codebase_path}")
        self.stdout.write(f"  Read-only: {read_only}")

        # Verify path exists
        if not os.path.exists(codebase_path):
            self.stdout.write(self.style.ERROR(f"\n  ERROR: Path does not exist: {codebase_path}"))
            return

        # Verify it looks like our codebase
        expected_markers = ['manage.py', 'core/', 'frontend/']
        found_markers = [m for m in expected_markers if os.path.exists(os.path.join(codebase_path, m))]
        if len(found_markers) < 2:
            self.stdout.write(self.style.WARNING(f"\n  WARNING: Path doesn't look like the codebase"))
            self.stdout.write(f"  Expected markers: {expected_markers}")
            self.stdout.write(f"  Found: {found_markers}")
            if not force:
                self.stdout.write(f"  Use --force to proceed anyway")
                return

        # Check if workspace already exists
        existing = ProjectWorkspace.objects.filter(name=name).first()
        if existing:
            if force:
                self.stdout.write(self.style.WARNING(f"\n  Existing workspace found - will be updated (--force)"))
            else:
                self.stdout.write(self.style.SUCCESS(f"\n  Workspace '{name}' already exists!"))
                self.stdout.write(f"  ID: {existing.id}")
                self.stdout.write(f"  Path: {existing.root_path}")
                self.stdout.write(f"  Active: {existing.is_active}")
                self.stdout.write(f"  Writable: {existing.allow_file_write}")
                self.stdout.write(f"\n  Use --force to recreate")
                return

        if dry_run:
            self.stdout.write(self.style.SUCCESS("\n[DRY RUN] Would create codebase workspace"))
            return

        # Get or create system user
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@donkey-betz.com',
                'is_active': True,
            }
        )

        # Protected paths - files/directories that should NEVER be modified
        protected_paths = [
            # Secrets and credentials
            '.env',
            '.env.local',
            '.env.production',
            'secrets/',
            'credentials/',
            '*.pem',
            '*.key',

            # Git internals
            '.git/',

            # Database files (if any)
            '*.sqlite3',
            'db.sqlite3',

            # Node modules and Python venvs (too large/dangerous)
            'node_modules/',
            'venv/',
            '.venv/',
            '__pycache__/',

            # Build artifacts
            'dist/',
            'build/',
            '*.pyc',

            # IDE settings
            '.idea/',
            '.vscode/',
        ]

        # Create or update the workspace
        if existing and force:
            existing.root_path = codebase_path
            existing.workspace_type = 'codebase'
            existing.is_active = True
            existing.allow_file_write = not read_only
            existing.allow_file_delete = False  # Never allow deletes in codebase
            existing.allow_git_operations = False  # Git ops should be manual
            existing.protected_paths = protected_paths
            existing.description = "Codebase workspace for code maintenance (Session 884)"
            existing.tech_stack = {
                'backend': 'django',
                'frontend': 'react',
                'database': 'postgresql',
                'purpose': 'codebase_maintenance',
            }
            existing.save()
            workspace = existing
            action = "Updated"
        else:
            workspace = ProjectWorkspace.objects.create(
                user=system_user,
                name=name,
                description="Codebase workspace for code maintenance (Session 884)",
                workspace_type='codebase',
                root_path=codebase_path,
                is_active=True,
                allow_file_write=not read_only,
                allow_file_delete=False,  # Never allow deletes in codebase
                allow_git_operations=False,  # Git ops should be manual
                protected_paths=protected_paths,
                tech_stack={
                    'backend': 'django',
                    'frontend': 'react',
                    'database': 'postgresql',
                    'purpose': 'codebase_maintenance',
                }
            )
            action = "Created"

        self.stdout.write(self.style.SUCCESS(f"\n{action} codebase workspace successfully!"))
        self.stdout.write(f"  ID: {workspace.id}")
        self.stdout.write(f"  Name: {workspace.name}")
        self.stdout.write(f"  Path: {workspace.root_path}")
        self.stdout.write(f"  Type: {workspace.workspace_type}")
        self.stdout.write(f"  Writable: {workspace.allow_file_write}")
        self.stdout.write(f"  Protected paths: {len(protected_paths)} patterns")

        # Verify some key files are readable
        self.stdout.write(self.style.NOTICE("\nVerifying codebase access..."))
        test_files = [
            'manage.py',
            'core/views/main.py',  # Session 1237 P2.b: was core/views.py (shadowed dead, deleted)
            'intelligence/tasks.py',
            'frontend/src/App.tsx',
        ]
        for test_file in test_files:
            full_path = os.path.join(codebase_path, test_file)
            if os.path.exists(full_path):
                self.stdout.write(f"  ✓ {test_file}")
            else:
                self.stdout.write(self.style.WARNING(f"  ✗ {test_file} (not found)"))

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("CODEBASE WORKSPACE SETUP COMPLETE!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        self.stdout.write(self.style.NOTICE("\n[USAGE]"))
        self.stdout.write("CodeGeneratorAgent and CodeReviewAgent can now access the codebase.")
        self.stdout.write("To switch an agent to codebase mode, the workspace manager will")
        self.stdout.write("automatically select this workspace for maintenance tasks.")
