#!/usr/bin/env python3
"""
Session 136 Part 2: Verify Cloudinary setup and configuration.

This script checks all prerequisites for cloud storage integration and guides
you through the setup process.

Usage:
    python verify_cloudinary_setup.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.cloud_storage import CloudStorageManager
from content.models import ImageHistory


def check_packages():
    """Check if required packages are installed."""
    print("=" * 80)
    print("📦 Checking Required Packages")
    print("=" * 80)
    print()

    packages = {
        'cloudinary': False,
        'django-cloudinary-storage': False
    }

    try:
        import cloudinary
        packages['cloudinary'] = True
        print("✅ cloudinary package installed")
    except ImportError:
        print("❌ cloudinary package NOT installed")
        print("   Run: pip install cloudinary")

    try:
        import cloudinary_storage
        packages['django-cloudinary-storage'] = True
        print("✅ django-cloudinary-storage package installed")
    except ImportError:
        print("❌ django-cloudinary-storage package NOT installed")
        print("   Run: pip install django-cloudinary-storage")

    print()
    return all(packages.values())


def check_environment():
    """Check if environment variables are set."""
    print("=" * 80)
    print("🔧 Checking Environment Variables")
    print("=" * 80)
    print()

    required_vars = [
        'CLOUDINARY_CLOUD_NAME',
        'CLOUDINARY_API_KEY',
        'CLOUDINARY_API_SECRET'
    ]

    all_set = True
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is NOT set")
            all_set = False

    print()

    if not all_set:
        print("To set these variables, add them to your .env file:")
        print()
        print("# Cloudinary Configuration (Session 136 Part 2)")
        print("CLOUDINARY_CLOUD_NAME=your_cloud_name_here")
        print("CLOUDINARY_API_KEY=your_api_key_here")
        print("CLOUDINARY_API_SECRET=your_api_secret_here")
        print()
        print("Get your credentials from: https://cloudinary.com/")
        print()

    return all_set


def check_cloudinary_config():
    """Check if Cloudinary is configured properly."""
    print("=" * 80)
    print("☁️  Checking Cloudinary Configuration")
    print("=" * 80)
    print()

    configured, message = CloudStorageManager.is_configured()

    if configured:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

    print()
    return configured


def check_database_migration():
    """Check if database migration was applied."""
    print("=" * 80)
    print("🗄️  Checking Database Migration")
    print("=" * 80)
    print()

    try:
        # Check if cloud_url field exists
        test_img = ImageHistory.objects.first()
        if test_img:
            _ = test_img.cloud_url
            print("✅ Database migration applied (cloud_url field exists)")
            return True
    except AttributeError:
        print("❌ Database migration NOT applied")
        print("   Run: python manage.py migrate content")
        print()
        return False
    except Exception as e:
        print(f"⚠️  Could not verify migration: {str(e)}")
        return False

    print()


def check_image_status():
    """Check status of images in database."""
    print("=" * 80)
    print("📊 Image Status Report")
    print("=" * 80)
    print()

    total_images = ImageHistory.objects.count()
    images_with_cloud_urls = ImageHistory.objects.exclude(cloud_url__isnull=True).exclude(cloud_url='').count()
    images_with_files = sum(1 for img in ImageHistory.objects.all() if img.file_exists())
    orphaned_images = total_images - images_with_files

    print(f"Total images in database:      {total_images}")
    print(f"Images with cloud URLs:        {images_with_cloud_urls}")
    print(f"Images with local files:       {images_with_files}")
    print(f"Orphaned images (no file):     {orphaned_images}")

    if orphaned_images > 0:
        percentage = (orphaned_images / total_images * 100) if total_images > 0 else 0
        print()
        print(f"⚠️  {percentage:.1f}% of images are orphaned (database record exists but file is missing)")

    print()

    if images_with_cloud_urls == 0 and images_with_files > 0:
        print("💡 You have images ready to migrate to Cloudinary!")
        print(f"   Run: python migrate_images_to_cloud.py")
        print()

    return {
        'total': total_images,
        'cloud': images_with_cloud_urls,
        'local': images_with_files,
        'orphaned': orphaned_images
    }


def main():
    """Run all checks and provide summary."""
    print()
    print("=" * 80)
    print("☁️  CLOUDINARY SETUP VERIFICATION")
    print("=" * 80)
    print()

    checks = {
        'packages': check_packages(),
        'environment': check_environment(),
        'cloudinary': False,
        'migration': False
    }

    # Only check Cloudinary config if packages and env vars are set
    if checks['packages'] and checks['environment']:
        checks['cloudinary'] = check_cloudinary_config()

    # Only check migration if Cloudinary is configured
    if checks['packages']:
        checks['migration'] = check_database_migration()

    # Always show image status
    image_stats = check_image_status()

    # Summary
    print("=" * 80)
    print("📋 Setup Summary")
    print("=" * 80)
    print()

    setup_steps = [
        ("1. Install packages", checks['packages']),
        ("2. Set environment variables", checks['environment']),
        ("3. Verify Cloudinary config", checks['cloudinary']),
        ("4. Apply database migration", checks['migration']),
        ("5. Migrate images to cloud", image_stats['cloud'] > 0)
    ]

    for step, completed in setup_steps:
        status = "✅" if completed else "⬜"
        print(f"{status} {step}")

    print()

    if all(checks.values()):
        if image_stats['cloud'] == image_stats['total']:
            print("🎉 Setup complete! All images are in Cloudinary!")
        elif image_stats['local'] > 0 and image_stats['cloud'] == 0:
            print("✅ Setup ready! Now migrate your images:")
            print("   python migrate_images_to_cloud.py")
        else:
            print("✅ Setup complete! Some images still need migration:")
            print("   python migrate_images_to_cloud.py")
    else:
        print("⚠️  Setup incomplete. Follow the steps above to complete setup.")
        print()
        print("Quick Start:")
        if not checks['packages']:
            print("   1. pip install cloudinary django-cloudinary-storage")
        if not checks['environment']:
            print("   2. Add Cloudinary credentials to .env file")
            print("      Get them from: https://cloudinary.com/")
        if not checks['migration']:
            print("   3. python manage.py migrate content")

    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
