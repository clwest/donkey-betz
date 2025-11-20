#!/usr/bin/env python3
"""
Verify which 3D models actually have local files - Session 131
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
print("VERIFYING 3D MODEL LOCAL FILES")
print("=" * 80)

all_models = MiniFigAsset.objects.filter(user=admin, status='completed').order_by('created_at')

count_with_files = 0
count_without_files = 0

models_with_files = []
models_without_files = []

for model in all_models:
    all_models_list = list(MiniFigAsset.objects.filter(user=admin).order_by('created_at'))
    model_num = all_models_list.index(model) + 1

    has_glb = bool(model.glb_file) and model.glb_file.name
    has_stl = bool(model.stl_file) and model.stl_file.name

    if has_glb and has_stl:
        count_with_files += 1
        models_with_files.append((model_num, model))
        print(f"✅ 3D Model #{model_num}: HAS FILES")
        print(f"   GLB: {model.glb_file.name}")
        print(f"   STL: {model.stl_file.name}")
    else:
        count_without_files += 1
        models_without_files.append((model_num, model))
        print(f"❌ 3D Model #{model_num}: NO FILES")
        print(f"   GLB: {model.glb_file.name if model.glb_file else '(none)'}")
        print(f"   STL: {model.stl_file.name if model.stl_file else '(none)'}")
        print(f"   3D File URL: {model.three_d_file[:60] if model.three_d_file else '(none)'}...")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"\n✅ Models WITH local files: {count_with_files}")
print(f"❌ Models WITHOUT local files: {count_without_files}")
print(f"\nThe {count_with_files} models with local files should show in the UI.")
print(f"The {count_without_files} models without local files won't show (expired CDN URLs).")
