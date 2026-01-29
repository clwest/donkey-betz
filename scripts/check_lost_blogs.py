#!/usr/bin/env python
"""
Session 860: Check for lost blogs - AgentMemory records that claim to have
created blog_post content but no corresponding SelfBlog exists.

Run on production:
    python manage.py shell < scripts/check_lost_blogs.py
"""
import os
import django

# Setup Django if running standalone
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

from core.models_unified_system import AgentMemory, SelfBlog
from django.db.models import Q

print("=" * 60)
print("LOST BLOGS REPORT - Session 860")
print("=" * 60)

# Find all AgentMemory records about blog creation
blog_memories = AgentMemory.objects.filter(
    Q(title__icontains='blog_post') |
    Q(title__icontains='Blog Post') |
    Q(content__icontains='Created Blog Post')
).order_by('-created_at')

print(f"\n📝 Found {blog_memories.count()} AgentMemory records about blog creation")

# Get all SelfBlog titles for comparison
selfblog_titles = set(SelfBlog.objects.values_list('title', flat=True))
print(f"📚 Found {len(selfblog_titles)} SelfBlog records total")

# Find lost blogs
lost_blogs = []
for memory in blog_memories:
    # Extract the blog title from the memory content
    content = memory.content or ""
    title_start = content.find('"')
    title_end = content.find('"', title_start + 1) if title_start >= 0 else -1

    extracted_title = ""
    if title_start >= 0 and title_end > title_start:
        extracted_title = content[title_start + 1:title_end]

    # Check if a similar blog exists
    blog_exists = False
    if extracted_title:
        for selfblog_title in selfblog_titles:
            # Check for partial match (first 30 chars)
            if extracted_title[:30].lower() in selfblog_title.lower():
                blog_exists = True
                break

    if not blog_exists and extracted_title:
        lost_blogs.append({
            'memory_id': str(memory.id),
            'memory_title': memory.title,
            'extracted_blog_title': extracted_title,
            'agent': memory.agent.name if memory.agent else 'Unknown',
            'created_at': memory.created_at.strftime('%Y-%m-%d %H:%M') if memory.created_at else 'Unknown',
        })

print(f"\n🔴 LOST BLOGS: {len(lost_blogs)}")
print("-" * 60)

for i, lost in enumerate(lost_blogs, 1):
    print(f"\n{i}. {lost['extracted_blog_title'][:60]}...")
    print(f"   Agent: {lost['agent']}")
    print(f"   Created: {lost['created_at']}")
    print(f"   Memory: {lost['memory_title'][:50]}...")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Total blog creation memories: {blog_memories.count()}")
print(f"Total SelfBlogs in database: {len(selfblog_titles)}")
print(f"Lost blogs (memory exists, SelfBlog missing): {len(lost_blogs)}")
print("\nNote: Lost blogs cannot be recovered - content was never saved.")
print("Fix deployed in PR #432 - future blogs will be persisted.")
