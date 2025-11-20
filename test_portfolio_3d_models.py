"""
Test portfolio API for 3D models - Session 137
Verify that 3D models are now included in the portfolio response.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from core.views_image import get_portfolio

User = get_user_model()

# Get admin user
user = User.objects.get(username='admin')
project_id = '2ef834f7-31f5-4689-aae9-710a55f90b72'

# Create a mock request
factory = RequestFactory()
request = factory.get(f'/api/portfolio/?project_id={project_id}')
request.user = user

print(f"Testing portfolio API for project {project_id}")
print(f"User: {user.username}\n")

# Call the view
response = get_portfolio(request)
data = response.data

print(f"Success: {data.get('success')}")
print(f"\nStats:")
print(f"  Total Items: {data['stats']['total_items']}")
print(f"  Images: {data['stats']['images']}")
print(f"  Videos: {data['stats']['videos']}")
print(f"  Audio: {data['stats']['audio']}")
print(f"  3D Models: {data['stats']['models']}")
print(f"  Favorites: {data['stats']['favorites']}")

# Count actual 3D models in portfolio
models_in_portfolio = [item for item in data['portfolio'] if item['type'] == '3d_model']
print(f"\n3D Models found in portfolio: {len(models_in_portfolio)}")

if models_in_portfolio:
    print("\n3D Models:")
    for model in models_in_portfolio:
        print(f"  - {model['prompt']}")
        print(f"    ID: {model['id']}")
        print(f"    URL: {model['content_url'][:80]}...")
        print(f"    Thumbnail: {model.get('thumbnail_url', 'None')[:80]}...")
        print(f"    Projects: {len(model.get('projects', []))}")
else:
    print("\n❌ No 3D models found in portfolio response!")
    print("\nThis is unexpected since we have 6 completed 3D models in the database.")
