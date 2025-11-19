#!/usr/bin/env python3
"""
Clean up 3D models without local files - Session 131
Delete completed models that only have expired CDN URLs (no local GLB/STL files)
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
print("CLEANUP: 3D MODELS WITHOUT LOCAL FILES")
print("=" * 80)

all_models = MiniFigAsset.objects.filter(user=admin, status='completed').order_by('created_at')

to_delete = []

print("\n🔍 Scanning for models without local files...")
for model in all_models:
    all_models_list = list(MiniFigAsset.objects.filter(user=admin).order_by('created_at'))
    model_num = all_models_list.index(model) + 1

    has_glb = bool(model.glb_file) and model.glb_file.name
    has_stl = bool(model.stl_file) and model.stl_file.name

    if not (has_glb and has_stl):
        to_delete.append((model_num, model))
        print(f"   ❌ 3D Model #{model_num}: No local files (CDN URL expired)")

print(f"\n📊 Found {len(to_delete)} model(s) to delete")

if to_delete:
    print("\n" + "=" * 80)
    print("DELETING MODELS")
    print("=" * 80)

    for model_num, model in to_delete:
        print(f"\n❌ Deleting 3D Model #{model_num}:")
        print(f"   UUID: {model.id}")
        print(f"   Title: {model.title}")
        print(f"   Created: {model.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   3D File URL: {model.three_d_file[:60] if model.three_d_file else '(none)'}...")

        model.delete()
        print(f"   ✅ Deleted!")

    print("\n" + "=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)
    print(f"\n✅ Deleted {len(to_delete)} unrecoverable 3D model(s)")
else:
    print("\n✅ No models to delete! All completed models have local files.")

# Verify final state
remaining_completed = MiniFigAsset.objects.filter(user=admin, status='completed').count()
print(f"\n📊 Remaining completed 3D models: {remaining_completed}")
print(f"   These should all be visible in the UI now!")
