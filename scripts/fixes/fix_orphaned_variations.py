"""
Fix orphaned variations - Session 137
Associate the 4 orphaned variations with the correct project.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory, CreativeProject

# Get the project
project = CreativeProject.objects.get(id='2ef834f7-31f5-4689-aae9-710a55f90b72')
print(f'Project: {project.name}')

# Find orphaned variations
orphaned = ImageHistory.objects.filter(
    prompt__icontains='Variation',
    project__isnull=True
)

print(f'\nFound {orphaned.count()} orphaned variations')

# Fix them
for img in orphaned:
    print(f'  Fixing Image #{img.get_sequential_number()} | {img.prompt}')
    img.project = project
    img.save()
    print(f'    ✅ Associated with project {project.name}')

print(f'\n✅ Fixed {orphaned.count()} orphaned variations!')

# Verify
remaining_orphans = ImageHistory.objects.filter(
    prompt__icontains='Variation',
    project__isnull=True
).count()

print(f'\nVerification: {remaining_orphans} orphaned variations remaining (should be 0)')
