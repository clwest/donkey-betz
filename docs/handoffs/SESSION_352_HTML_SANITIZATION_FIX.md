# Session 352: HTML Sanitization Fix for Research Display

**Date:** December 4, 2025
**Status:** COMPLETE
**Branch:** `feature/session-52-ai-assistant`

---

## Summary

Fixed the `about:blank#blocked` issue and broken page layout caused by malformed HTML (unclosed `<a>` tags) in research summaries. Spider data from RSS feeds (Medium, ProductHunt, etc.) was including raw HTML that broke the UI when rendered.

---

## Problem

The "AI podcast for content creators" project was experiencing:
1. `about:blank#blocked` errors when clicking research links
2. Broken page layout with blue underlined links bleeding through all sections
3. Unclosed `<a href="...">` tags from spider data wrapping entire page sections

**Root Cause:** Spider data from RSS feeds included raw HTML content with `<a>` tags that:
- Had empty/invalid URLs (`url: ''`, `link: 'N/A'`)
- Were truncated mid-tag (unclosed)
- Were being rendered directly without sanitization

---

## Solution

### 1. URL Validation Helper (`getValidArticleUrl()`)

Added function to validate URLs before making them clickable:

```javascript
function getValidArticleUrl(article) {
    const possibleUrls = [article?.url, article?.link, article?.href];
    for (const url of possibleUrls) {
        if (url && typeof url === 'string' && url.trim() !== '' &&
            url.toLowerCase() !== 'n/a' && url.toLowerCase() !== 'none' &&
            (url.startsWith('http://') || url.startsWith('https://'))) {
            return url;
        }
    }
    return null; // No valid URL found
}
```

**Behavior:**
- Returns valid HTTP/HTTPS URLs
- Filters out empty strings, 'N/A', 'none'
- Returns `null` for invalid URLs (renders non-clickable text instead)

### 2. HTML Sanitization Helper (`sanitizeResearchSummary()`)

Added function to strip all HTML tags from research summaries:

```javascript
function sanitizeResearchSummary(html) {
    if (!html) return '';
    return html
        .replace(/<br\s*\/?>/gi, '\n')  // Convert <br> to newlines
        .replace(/<\/p>/gi, '\n\n')     // Convert </p> to double newlines
        .replace(/<[^>]*>/g, '')        // Strip all other HTML tags
        .replace(/&amp;/g, '&')         // Decode common entities
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&quot;/g, '"')
        .replace(/&#39;/g, "'");
}
```

### 3. Template Updates

**Research Summaries (line 31551):**
```javascript
${sanitizeResearchSummary(research.summary) || 'No analysis available.'}
```

**Research Articles (lines 31584-31606):**
- Uses `getValidArticleUrl()` to validate URLs
- Shows clickable link with ↗ icon for valid URLs
- Shows non-clickable span with 📄 icon for invalid URLs

### 4. Database Cleanup

Cleaned existing corrupted data in the AI podcast project:
```python
# Removed 2 unclosed <a> tags from trend_analysis summary
# Before: 1600 chars, After: 1361 chars
```

---

## Files Changed

| File | Changes |
|------|---------|
| `ai_core/templates/ai_image_studio.html` | Added `getValidArticleUrl()` and `sanitizeResearchSummary()` helpers (lines 31136-31164), updated research display templates |

---

## Testing

1. Open http://localhost:8000/ai-studio/
2. Go to Projects tab
3. Find "AI podcast for content creators" project
4. Expand Trend Analysis - should display cleanly without blue links
5. Click research article links - should not show `about:blank#blocked`

---

## Prevention

The `sanitizeResearchSummary()` function will automatically strip HTML from all future research summaries, preventing this issue from recurring even if spider data contains malformed HTML.

---

## Related Sessions

- Session 350: Business viability scoring ("Idiot Protector")
- Session 351: Agent Intelligence → Research Pipeline
