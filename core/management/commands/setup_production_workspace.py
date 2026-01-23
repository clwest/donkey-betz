"""
Session 792: Setup Production Workspace for SKIN Layer

Creates a ProjectWorkspace for production deployments on Railway.
Uses a persistent volume path for file operations.

Usage:
    # On Railway (uses /app/workspace by default)
    railway run python manage.py setup_production_workspace

    # Custom path
    railway run python manage.py setup_production_workspace --path=/data/workspace

    # Local development
    python manage.py setup_production_workspace --path=/Users/dev/my-project --type=local
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup a production workspace for the SKIN layer'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help='Workspace root path (default: /app/workspace for Railway, or PROJECT_WORKSPACE_PATH env var)'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='donkey-betz-production',
            help='Workspace name (default: donkey-betz-production)'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['local', 'git_remote', 'sandbox', 'container'],
            default='container',
            help='Workspace type (default: container for Railway)'
        )
        parser.add_argument(
            '--git-url',
            type=str,
            default='https://github.com/clwest/donkey-betz-platform.git',
            help='Git remote URL (if applicable)'
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

    def handle(self, *args, **options):
        from core.models_skin_layer import ProjectWorkspace

        dry_run = options['dry_run']
        force = options['force']
        name = options['name']
        workspace_type = options['type']
        git_url = options['git_url']

        # Determine workspace path
        workspace_path = options['path']
        if not workspace_path:
            # Check environment variable first
            workspace_path = os.environ.get('PROJECT_WORKSPACE_PATH')
            if not workspace_path:
                # Default based on environment
                if os.environ.get('RAILWAY_ENVIRONMENT'):
                    workspace_path = '/app/workspace'
                else:
                    workspace_path = os.getcwd()

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("PRODUCTION WORKSPACE SETUP - Session 792"))
        self.stdout.write(self.style.NOTICE("=" * 60))

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY RUN MODE - No changes will be made\n"))

        self.stdout.write(f"\nConfiguration:")
        self.stdout.write(f"  Name: {name}")
        self.stdout.write(f"  Type: {workspace_type}")
        self.stdout.write(f"  Path: {workspace_path}")
        self.stdout.write(f"  Git URL: {git_url}")

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
                self.stdout.write(f"\n  Use --force to recreate")
                return

        if dry_run:
            self.stdout.write(self.style.SUCCESS("\n[DRY RUN] Would create workspace"))
            return

        # Create the workspace directory if it doesn't exist (for container type)
        if workspace_type == 'container' and not os.path.exists(workspace_path):
            try:
                os.makedirs(workspace_path, exist_ok=True)
                self.stdout.write(self.style.SUCCESS(f"\n  Created directory: {workspace_path}"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"\n  Could not create directory: {e}"))
                self.stdout.write("  (This may be fine if using a mounted volume)")

        # Get or create a system user for the workspace
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@donkey-betz.com',
                'is_active': True,
            }
        )

        # Create or update the workspace
        if existing and force:
            existing.root_path = workspace_path
            existing.workspace_type = workspace_type
            existing.git_remote_url = git_url
            existing.is_active = True
            existing.description = "Production workspace for agent file operations (Session 792)"
            existing.tech_stack = {
                'backend': 'django',
                'frontend': 'react',
                'database': 'postgresql',
                'deployment': 'railway',
            }
            existing.save()
            workspace = existing
            action = "Updated"
        else:
            workspace = ProjectWorkspace.objects.create(
                user=system_user,
                name=name,
                description="Production workspace for agent file operations (Session 792)",
                workspace_type=workspace_type,
                root_path=workspace_path,
                git_remote_url=git_url,
                is_active=True,
                tech_stack={
                    'backend': 'django',
                    'frontend': 'react',
                    'database': 'postgresql',
                    'deployment': 'railway',
                }
            )
            action = "Created"

        self.stdout.write(self.style.SUCCESS(f"\n{action} workspace successfully!"))
        self.stdout.write(f"  ID: {workspace.id}")
        self.stdout.write(f"  Name: {workspace.name}")
        self.stdout.write(f"  Path: {workspace.root_path}")
        self.stdout.write(f"  Type: {workspace.workspace_type}")
        self.stdout.write(f"  Active: {workspace.is_active}")

        # Verify SKIN can see it
        self.stdout.write(self.style.NOTICE("\nVerifying SKIN service..."))
        try:
            from core.services.skin import SkinService
            skin = SkinService()
            status = skin.get_status()
            self.stdout.write(f"  SKIN Status: {status.get('status', 'unknown')}")
            self.stdout.write(f"  Total Workspaces: {status.get('workspaces', {}).get('total', 0)}")
            self.stdout.write(f"  Active Workspaces: {status.get('workspaces', {}).get('active', 0)}")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  SKIN verification failed: {e}"))

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("WORKSPACE SETUP COMPLETE!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        # Railway-specific instructions
        if os.environ.get('RAILWAY_ENVIRONMENT') or workspace_type == 'container':
            self.stdout.write(self.style.NOTICE("\n[RAILWAY NOTE]"))
            self.stdout.write("For persistent file storage, add a Railway Volume:")
            self.stdout.write("  1. Go to Railway Dashboard > Your Service > Settings > Volumes")
            self.stdout.write("  2. Add Volume with mount path: /app/workspace")
            self.stdout.write("  3. Redeploy the service")
            self.stdout.write("\nFiles written to /app/workspace will persist across deployments.")
