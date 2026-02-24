"""
Management command: create (or verify) the PA service account.

Idempotent — safe to run on every deploy via the Procfile release command.
Creates a user ``pa-service`` with an unusable password and a DRF Token for
API access.  Prints the token so it can be captured as an env var.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create the PA service account (idempotent)'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username='pa-service',
            defaults={
                'email': 'pa-service@donkeybetz.internal',
                'is_active': True,
                'is_staff': False,
                'is_superuser': False,
            },
        )

        if created:
            user.set_unusable_password()
            user.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS('Created pa-service user'))
        else:
            self.stdout.write('pa-service user already exists')

        # Set platform_role if the profile field exists
        try:
            from core.models import EnhancedUserProfile
            profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)
            if getattr(profile, 'platform_role', None) != 'unified_user':
                profile.platform_role = 'unified_user'
                profile.save(update_fields=['platform_role'])
        except Exception:
            pass  # profile model may not have platform_role

        # Ensure a DRF token exists
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=user)

        self.stdout.write(f'PA_SERVICE_TOKEN={token.key}')
