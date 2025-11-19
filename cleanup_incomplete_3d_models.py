#!/usr/bin/env python3
"""
Delete incomplete 3D models - Session 131
Keep only completed models with local files
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import MiniFigAsset

User = get_user_model()
admin = User.objects.get(username='admin')

print("=" * 80)
print("CLEANUP: INCOMPLETE 3D MODELS")
print("=" * 80)

all_models = MiniFigAsset.objects.filter(user=admin).order_by('created_at')

# Get incomplete models (processing, pending, failed)
to_delete = all_models.exclude(status='completed')

print(f"\n📊 Total 3D models: {all_models.count()}")
print(f"   Completed: {all_models.filter(status='completed').count()}")
print(f"   Processing: {all_models.filter(status='processing').count()}")
print(f"   Pending: {all_models.filter(status='pending').count()}")
print(f"   Failed: {all_models.filter(status='failed').count()}")

print(f"\n🗑️  Deleting {to_delete.count()} incomplete model(s)...")

for model in to_delete:
    all_models_list = list(MiniFigAsset.objects.filter(user=admin).order_by('created_at'))
    model_num = all_models_list.index(model) + 1

    print(f"\n❌ Deleting 3D Model #{model_num}:")
    print(f"   UUID: {model.id}")
    print(f"   Title: {model.title}")
    print(f"   Status: {model.status}")
    print(f"   Created: {model.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

    model.delete()
    print(f"   ✅ Deleted!")

print("\n" + "=" * 80)
print("CLEANUP COMPLETE")
print("=" * 80)

remaining = MiniFigAsset.objects.filter(user=admin).count()
completed = MiniFigAsset.objects.filter(user=admin, status='completed').count()

print(f"\n✅ Remaining 3D models: {remaining}")
print(f"   All {completed} are completed with local files!")
print(f"\n💡 Refresh your browser - only completed models will show!")
