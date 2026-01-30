"""
Session 882: Ensure Enhanced Profiles for All Users

This command creates EnhancedUserProfile records for all users who don't have one.
This is important because the interview system and personalization features require
an EnhancedUserProfile to function.

Run with: python manage.py ensure_enhanced_profiles
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import EnhancedUserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Ensure all users have an EnhancedUserProfile'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show details for each user',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        verbose = options.get('verbose', False)

        self.stdout.write("\n👤 ENHANCED PROFILE SETUP - Session 882")
        self.stdout.write("=" * 60)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made\n"))

        # Get all users
        all_users = User.objects.all()
        total_users = all_users.count()

        self.stdout.write(f"\n📊 Total users in system: {total_users}")

        # Get users without EnhancedUserProfile
        users_with_profile = EnhancedUserProfile.objects.values_list('user_id', flat=True)
        users_without_profile = all_users.exclude(id__in=users_with_profile)
        missing_count = users_without_profile.count()

        self.stdout.write(f"✅ Users with EnhancedUserProfile: {total_users - missing_count}")
        self.stdout.write(f"❌ Users without EnhancedUserProfile: {missing_count}")

        if missing_count == 0:
            self.stdout.write(self.style.SUCCESS("\n✨ All users already have EnhancedUserProfile!"))
            return

        self.stdout.write(f"\n🔧 Creating profiles for {missing_count} users...\n")

        created_count = 0
        error_count = 0

        for user in users_without_profile:
            try:
                if verbose:
                    self.stdout.write(f"  Creating profile for: {user.username} (ID: {user.id})")

                if not dry_run:
                    profile = EnhancedUserProfile.objects.create(
                        user=user,
                        # Set sensible defaults
                        communication_style='balanced',
                        decision_framework='analytical',
                        learning_style='mixed',
                        privacy_level='professional',
                        time_zone='America/Los_Angeles',
                    )

                    # If user has a first name, use it to set primary_role
                    if user.first_name:
                        profile.primary_role = f"{user.first_name}'s Profile"
                        profile.save()

                created_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Error creating profile for {user.username}: {e}")
                )

        self.stdout.write("\n" + "=" * 60)

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"\n🔍 Would create {created_count} profiles")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n✅ Created {created_count} EnhancedUserProfile records")
            )

        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to create {error_count} profiles")
            )

        # Show completeness summary
        if not dry_run:
            self.stdout.write("\n📈 Profile Completeness Summary:")
            low_completeness = 0
            medium_completeness = 0
            high_completeness = 0

            for profile in EnhancedUserProfile.objects.all():
                completeness = profile.calculate_completeness()
                if completeness < 30:
                    low_completeness += 1
                elif completeness < 70:
                    medium_completeness += 1
                else:
                    high_completeness += 1

            self.stdout.write(f"  🔴 Low (< 30%): {low_completeness} users")
            self.stdout.write(f"  🟡 Medium (30-70%): {medium_completeness} users")
            self.stdout.write(f"  🟢 High (> 70%): {high_completeness} users")

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n💡 Users with low completeness will be prompted to complete the interview "
                    f"when they next chat with the Personal Assistant."
                )
            )
