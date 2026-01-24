"""
Session 800: Check Cloudinary migration status

Quick command to see how many images are on Cloudinary vs local storage.

Usage:
    python manage.py check_cloudinary_status
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Check how many images are on Cloudinary vs local storage'

    def handle(self, *args, **options):
        from content.models import ImageHistory
        from content.cloud_storage import CloudStorageManager

        # Check Cloudinary config
        is_configured, message = CloudStorageManager.is_configured()

        self.stdout.write('=' * 60)
        self.stdout.write('Cloudinary Migration Status')
        self.stdout.write('=' * 60)
        self.stdout.write(f'Cloudinary configured: {is_configured}')
        if not is_configured:
            self.stdout.write(self.style.WARNING(f'  {message}'))
        self.stdout.write('')

        # Count images by storage type
        total = ImageHistory.objects.count()
        cloudinary = ImageHistory.objects.filter(file_path__startswith='http').count()
        data_uri = ImageHistory.objects.filter(file_path__startswith='data:').count()
        local = total - cloudinary - data_uri

        self.stdout.write(f'Total images: {total}')
        self.stdout.write(f'  - Cloudinary (http): {cloudinary} ({cloudinary/total*100:.1f}%)' if total > 0 else f'  - Cloudinary: {cloudinary}')
        self.stdout.write(f'  - Data URI (base64): {data_uri} ({data_uri/total*100:.1f}%)' if total > 0 else f'  - Data URI: {data_uri}')
        self.stdout.write(f'  - Local storage: {local} ({local/total*100:.1f}%)' if total > 0 else f'  - Local: {local}')

        if local > 0:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(
                f'{local} images still on local storage - run migrate_images_to_cloudinary'
            ))
        else:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('All images migrated to Cloudinary!'))

        # Estimate egress savings
        if local > 0:
            avg_size_mb = 2.7  # Average from earlier analysis
            views_per_image = 10  # Estimated monthly views
            egress_gb = (local * avg_size_mb * views_per_image) / 1024
            savings = egress_gb * 0.10  # Railway egress cost per GB
            self.stdout.write('')
            self.stdout.write(f'Estimated monthly egress from local images:')
            self.stdout.write(f'  - {egress_gb:.1f} GB @ $0.10/GB = ${savings:.2f}/month')
