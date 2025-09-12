"""
Django management command to create a test authentication token
Usage: python manage.py create_test_token [username]
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates or retrieves an authentication token for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            nargs='?',
            default='testuser',
            help='Username to create token for'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        
        # Get or create user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@test.com',
                'is_active': True,
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        self.stdout.write(self.style.SUCCESS(f'\nToken for {username}: {token.key}'))
        self.stdout.write('\nAdd this to your .env file:')
        self.stdout.write(f'TEST_AUTH_TOKEN={token.key}')
