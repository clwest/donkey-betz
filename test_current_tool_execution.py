#!/usr/bin/env python3
"""
Test Current Tool Execution - Verify what's actually working
Session 130 - Reality Check
"""

import os
import django
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory, VideoHistory, MiniFigAsset
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("TOOL EXECUTION REALITY CHECK - Session 130")
print("=" * 80)

# Get current counts
user = User.objects.first()
if not user:
    print("❌ No users found in database")
    exit(1)

print(f"\n👤 Testing with user: {user.username}")

# Current database state
print("\n📊 CURRENT DATABASE STATE:")
print(f"   Images: {ImageHistory.objects.count()}")
print(f"   Videos: {VideoHistory.objects.count()}")
print(f"   3D Models: {MiniFigAsset.objects.count()}")

# Get recent records
print("\n📝 RECENT RECORDS (last 5 of each):")

print("\n   Recent Images:")
for img in ImageHistory.objects.order_by('-created_at')[:5]:
    print(f"      #{img.id} - {img.prompt[:50]}... - {img.created_at.strftime('%H:%M:%S')}")

print("\n   Recent Videos:")
for vid in VideoHistory.objects.order_by('-created_at')[:5]:
    print(f"      #{vid.id} - Status: {vid.status} - {vid.created_at.strftime('%H:%M:%S')}")

print("\n   Recent 3D Models:")
for model in MiniFigAsset.objects.order_by('-created_at')[:5]:
    print(f"      #{model.id} - Status: {model.status} - {model.created_at.strftime('%H:%M:%S')}")

print("\n" + "=" * 80)
print("MANUAL TESTING GUIDE")
print("=" * 80)

print("""
🧪 Test these commands in the AI Studio (http://localhost:8000/ai-studio/):

1. IMAGE UPSCALING:
   "Upscale image 3"

   Expected:
   - ✅ AI responds with confirmation
   - ✅ New ImageHistory record created
   - ✅ Higher resolution image generated

   Verify:
   python3 -c "import django; django.setup(); from content.models import ImageHistory; print(f'Images: {ImageHistory.objects.count()}')"

2. BACKGROUND REMOVAL:
   "Remove background from image 3"

   Expected:
   - ✅ AI responds with confirmation
   - ✅ New ImageHistory record created
   - ✅ Image with transparent background

3. 3D CONVERSION:
   "Convert image 3 to 3D"

   Expected:
   - ✅ AI responds with confirmation
   - ✅ New MiniFigAsset record created
   - ✅ GLB + STL files generated (~60 seconds)

   Verify:
   python3 -c "import django; django.setup(); from content.models import MiniFigAsset; print(f'3D Models: {MiniFigAsset.objects.count()}')"

4. VIDEO ANIMATION:
   "Animate image 3"

   Expected:
   - ✅ AI responds with confirmation
   - ✅ New VideoHistory record created
   - ✅ Status changes: pending → processing → completed

   Verify:
   python3 -c "import django; django.setup(); from content.models import VideoHistory; print(f'Videos: {VideoHistory.objects.count()}')"
""")

print("\n" + "=" * 80)
print("BROWSER CONSOLE TESTING")
print("=" * 80)

console_test = """
// Open browser console (F12) and run this:

// Test 1: Check response structure
fetch('/api/assistant/chat/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: 'What features do you have?'})
}).then(r => r.json()).then(data => {
    console.log('📡 Response structure:', Object.keys(data));
    console.log('📝 Response data:', data);
    console.log('✅ Has success?', 'success' in data);
    console.log('✅ Has data?', 'data' in data);
    console.log('✅ Has response?', 'data' in data && 'response' in data.data);
});

// Test 2: Check tool call detection
fetch('/api/assistant/chat/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: 'Upscale image 3'})
}).then(r => r.json()).then(data => {
    console.log('📡 Upscale response:', data);
    console.log('🔧 Tool calls present?', 'tool_calls' in data || ('data' in data && 'tool_calls' in data.data));
    if (data.data && data.data.tool_calls) {
        console.log('🎯 Tool calls:', data.data.tool_calls);
    }
});
"""

print(console_test)

print("\n" + "=" * 80)
print("WHAT TO LOOK FOR")
print("=" * 80)

print("""
✅ WORKING SIGNS:
- Database counts increase after commands
- AI responds with specific confirmation (not generic)
- Browser console shows tool_calls (if applicable)
- Files appear in media/ directories

❌ BROKEN SIGNS:
- Database counts stay the same
- AI gives generic "I can help with that" responses
- No tool_calls in console
- No new files generated

📊 REPORT BACK:
After testing, tell me:
1. Which commands worked (database records created?)
2. Which commands failed (no records?)
3. What browser console showed (response structure, tool_calls?)
4. Any error messages?
""")

print("\n" + "=" * 80)
print("READY TO TEST!")
print("=" * 80)
print("\nServer: http://localhost:8000/ai-studio/")
print("Start with: 'Upscale image 3' and check if ImageHistory count increases\n")
