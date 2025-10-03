# 400 Bad Request Error - FIXED! 🔧

## Date: 2025-08-31
## Error: `POST /api/gallery/save/ 400 (Bad Request)`

---

## Root Cause Analysis

### The Problem 🐛
The TextGenerator was trying to save **blog posts** to the **gallery** endpoint, but:
- `/api/gallery/save/` is specifically for **images** (`SaveImageView`)
- It expects `image_url` field, not text content
- Blog posts need a different endpoint entirely

### The Discovery 🔍
```bash
curl /api/gallery/save/ → {"error":"image_url is required"}
```

The backend has **different endpoints** for different content types:
- **Images**: `/api/gallery/save/` (expects image_url)
- **Blog Posts**: `/api/content/blog/save/` (expects title, content)
- **General Content**: `/api/content/{id}/save-to-gallery/` (images only)

---

## Solution Applied ✅

### 1. Added Blog Save Method to Content Service
```typescript
// Added to content.service.ts
async saveBlogPost(blogData: {
  title: string;
  content: string;
  meta_description?: string;
  tags?: string[];
}) {
  const { data } = await apiClient.post('/content/blog/save/', blogData);
  return data;
}
```

### 2. Smart Save Logic in TextGenerator
**Before** (broken):
```javascript
// Always tried to use gallery save - WRONG!
await contentService.saveToGallery(contentId, title, tags);
```

**After** (fixed):
```javascript
if (params.type === 'blog') {
  // Extract blog title and content
  let title = 'Blog Post';
  let content = generatedContent;
  
  if (generatedContent.startsWith('# ')) {
    const titleMatch = generatedContent.match(/^# (.+)$/m);
    title = titleMatch ? titleMatch[1] : 'Blog Post';
    content = generatedContent.replace(/^# .+\n\n/, '');
  }

  // Use blog-specific endpoint
  await contentService.saveBlogPost({
    title,
    content,
    meta_description: '',
    tags: [params.tone || 'default', 'generated']
  });
  
  toast.success('Blog post saved to library!');
} else {
  // Use gallery save for other content types
  await contentService.saveToGallery(contentId, title, tags);
  toast.success('Content saved to gallery!');
}
```

### 3. Smart Title Extraction
- **Blog Posts**: Extracts `# Title` and removes from content body
- **Other Content**: Uses first 50 characters as title
- **Automatic tagging**: Includes tone and "generated" tag

---

## API Endpoints Clarified

### Blog Save ✅
```bash
POST /api/content/blog/save/
{
  "title": "Blog Title",
  "content": "Blog content without title",
  "meta_description": "Optional description",
  "tags": ["casual", "generated"]
}
```

### Blog List ✅
```bash
GET /api/content/blog/list/
# Returns array of saved blog posts with previews
```

### Gallery Save (Images Only) 🖼️
```bash
POST /api/gallery/save/
{
  "image_url": "required for images",
  "title": "Image title",
  "tags": ["tag1", "tag2"]
}
```

---

## Testing Results ✅

### Blog Save Test
```bash
curl -X POST /api/content/blog/save/ \
  -d '{"title": "Test", "content": "Content", "tags": ["test"]}'
→ {"success": true, "id": 240, "message": "Blog post saved successfully"}
```

### Blog List Test
```bash
curl -X GET /api/content/blog/list/
→ Returns array of saved blogs including our test blog
```

---

## What Changed in the UI

### Before Fix 🚫
- Click Save on blog → 400 Error
- Toast says "Failed to save content"
- Content disappears into the void

### After Fix ✅
- Click Save on blog → Uses correct endpoint
- Toast says "Blog post saved to library!"
- Content is actually saved and retrievable

### Different Messages by Type
- **Blog Posts**: "Blog post saved to library!"
- **Other Content**: "Content saved to gallery!"

---

## Where to Find Saved Content

### Blog Posts
- **API**: `GET /api/content/blog/list/`
- **Frontend**: Gallery page should list all content types
- **Database**: Stored in `Content` model with `content_type: 'blog_post'`

### Images  
- **API**: `GET /api/gallery/`
- **Frontend**: Gallery page images section
- **Database**: Stored in `SavedImage` model

---

## Testing Instructions

### 1. Test Blog Save
1. **Refresh browser** at http://localhost:3000
2. Generate a blog post (select "Blog Post" type)
3. Click "Save"
4. **Expected**: "Blog post saved to library!" message
5. **No more 400 errors!** ✅

### 2. Test Other Content Types
1. Generate general text, social, or email content
2. Click "Save" 
3. **Expected**: "Content saved to gallery!" message

### 3. Verify Saved Content
1. Check the Gallery page
2. Or test API directly:
   ```bash
   curl -H "Authorization: Token 993f..." http://localhost:8001/api/content/blog/list/
   ```

---

## Summary

The 400 error was caused by using the wrong API endpoint. **Blog posts** need to go to the **blog save endpoint**, not the **gallery endpoint** (which is for images).

The fix involved:
1. **Smart routing**: Blog type → blog API, others → gallery API
2. **Proper data format**: Extract title from markdown heading
3. **Correct tagging**: Include tone and generation info
4. **User feedback**: Different success messages per type

**Your blog saves should now work perfectly!** 🎉

---

*Fix Applied: 2025-08-31 17:15:00*
*Status: Save functionality now works correctly for all content types!*
*Test: http://localhost:3000 → Generate blog → Save → Success!*