"""
Django management command to ensure Quick Starts project exists for users

Session 97: Create default "Quick Starts" project for ad-hoc work
- Automatically created for every user
- All spontaneous sessions default here
- Can be run manually or integrated into user signup

Usage:
    python manage.py ensure_quick_starts_project           # For all users
    python manage.py ensure_quick_starts_project --user_id <id>  # For specific user
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from content.models import CreativeProject
import uuid

User = get_user_model()


class Command(BaseCommand):
    help = 'Ensure Quick Starts project exists for users (default ad-hoc work project)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user_id',
            type=int,
            help='User ID to create Quick Starts project for (optional, defaults to all users)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        dry_run = options.get('dry_run', False)

        # Get users to process
        if user_id:
            users = User.objects.filter(id=user_id)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f'❌ User with ID {user_id} not found'))
                return
        else:
            users = User.objects.all()

        created_count = 0
        existing_count = 0
        total_users = users.count()

        self.stdout.write(self.style.WARNING(f'\n🔍 Processing {total_users} user(s)...\n'))

        for user in users:
            # Check if user already has Quick Starts project
            existing_qs = CreativeProject.objects.filter(
                user=user,
                is_quick_starts=True
            ).first()

            if existing_qs:
                existing_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ User {user.id} ({user.username}) already has Quick Starts: "{existing_qs.name}"'
                    )
                )
                continue

            # Create Quick Starts project
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'🔄 [DRY RUN] Would create Quick Starts project for user {user.id} ({user.username})'
                    )
                )
                created_count += 1
            else:
                quick_starts = CreativeProject.objects.create(
                    id=uuid.uuid4(),
                    user=user,
                    name="Quick Starts",
                    description="Default project for spontaneous, ad-hoc creative work. Generate anything here without needing to create a specific project first!",
                    category="other",
                    is_quick_starts=True,
                    is_active=True,
                    status="active"
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'🎉 Created Quick Starts project for user {user.id} ({user.username}): {quick_starts.id}'
                    )
                )

        # Summary
        self.stdout.write(self.style.WARNING('\n' + '=' * 60))
        if dry_run:
            self.stdout.write(self.style.WARNING('📋 DRY RUN SUMMARY:'))
        else:
            self.stdout.write(self.style.WARNING('📊 SUMMARY:'))
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(f'Total users processed: {total_users}')
        self.stdout.write(self.style.SUCCESS(f'✅ Already had Quick Starts: {existing_count}'))

        if dry_run:
            self.stdout.write(self.style.WARNING(f'🔄 Would create Quick Starts: {created_count}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'🎉 Newly created Quick Starts: {created_count}'))

        self.stdout.write(self.style.WARNING('=' * 60 + '\n'))

        if created_count > 0 and not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    '✨ All users now have a Quick Starts project for ad-hoc creative work!'
                )
            )
