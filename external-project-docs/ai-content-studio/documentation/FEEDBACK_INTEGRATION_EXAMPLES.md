# Feedback System Integration Examples

## Quick Integration Guide

The feedback system is now fully implemented and ready to use across all content types in the AI Content Studio. Here are examples of how to integrate it into your components.

## 1. Basic Inline Feedback Widget

For content that displays inline (like in a gallery or list):

```tsx
import { FeedbackWidget } from '../components/feedback/FeedbackWidget';

// In your component:
<FeedbackWidget
  contentType="image"
  contentId={imageId}
  contentTitle="generated image"
  inline={true}
  showStats={true}
/>
```

## 2. Floating Feedback Button

For full-page content views (like blog viewer, video player):

```tsx
import { FeedbackWidget } from '../components/feedback/FeedbackWidget';

// Add to your component (it will show a floating button):
<FeedbackWidget
  contentType="blog"
  contentId={blogId}
  contentTitle={blogTitle}
  inline={false}  // This creates a floating button
  showStats={true}
  onFeedbackSubmit={() => {
    // Optional: Refresh content or show notification
    console.log('Feedback submitted!');
  }}
/>
```

## 3. Quick Thumbs Up/Down Buttons

For simple quick feedback in content cards:

```tsx
import { feedbackService } from '../services/feedbackService';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import toast from 'react-hot-toast';

// In your component:
<div className="flex items-center gap-2">
  <button
    onClick={async () => {
      await feedbackService.quickFeedback('blog', blogId, true);
      toast.success('Thanks for your feedback!');
    }}
    className="p-2 hover:bg-green-600/20 rounded-lg transition-colors"
  >
    <ThumbsUp className="w-5 h-5 text-green-500" />
  </button>
  <button
    onClick={async () => {
      await feedbackService.quickFeedback('blog', blogId, false);
      toast.success('Thanks for your feedback!');
    }}
    className="p-2 hover:bg-red-600/20 rounded-lg transition-colors"
  >
    <ThumbsDown className="w-5 h-5 text-red-500" />
  </button>
</div>
```

## 4. Integration in Image Gallery

```tsx
// In GalleryPage.tsx or ImageCard component:
import { FeedbackWidget } from '../../components/feedback/FeedbackWidget';

{galleryImages.map((image) => (
  <div key={image.id} className="relative">
    <img src={image.url} alt={image.title} />
    
    {/* Feedback widget at bottom of image card */}
    <div className="mt-4">
      <FeedbackWidget
        contentType="image"
        contentId={image.id}
        contentTitle={image.title || 'this image'}
        inline={true}
        showStats={false}  // Keep it compact in gallery
      />
    </div>
  </div>
))}
```

## 5. Integration in Blog Viewer

```tsx
// In BlogViewer.tsx:
import { FeedbackWidget } from '../../components/feedback/FeedbackWidget';

export const BlogViewer = ({ blog }) => {
  return (
    <div>
      {/* Blog content */}
      <article>{blog.content}</article>
      
      {/* Feedback section at the end */}
      <div className="mt-8 pt-8 border-t border-gray-700">
        <h3 className="text-lg font-semibold mb-4">How was this article?</h3>
        <FeedbackWidget
          contentType="blog"
          contentId={blog.id}
          contentTitle={blog.title}
          inline={true}
          showStats={true}
        />
      </div>
      
      {/* Or use floating button */}
      <FeedbackWidget
        contentType="blog"
        contentId={blog.id}
        contentTitle={blog.title}
        inline={false}
      />
    </div>
  );
};
```

## 6. Integration in Video Player

```tsx
// In VideoPlayer.tsx:
import { FeedbackWidget } from '../../components/feedback/FeedbackWidget';

export const VideoPlayer = ({ video }) => {
  return (
    <div>
      <video src={video.url} controls />
      
      {/* Feedback below video */}
      <div className="mt-4">
        <FeedbackWidget
          contentType="video"
          contentId={video.id}
          contentTitle={video.title}
          inline={true}
          showStats={true}
          onFeedbackSubmit={() => {
            // Could trigger analytics update
            updateVideoAnalytics(video.id);
          }}
        />
      </div>
    </div>
  );
};
```

## 7. Content Type Mapping

Use these content types when calling the feedback service:

- `'text'` - For generated text content
- `'image'` - For generated images
- `'video'` - For generated videos
- `'blog'` - For blog posts
- `'social'` - For social media posts
- `'ebook'` - For eBooks
- `'voice'` - For voice transcriptions
- `'research'` - For research documents

## 8. Accessing Feedback Dashboard

The feedback analytics dashboard is available at `/feedback` in the app. It shows:

- Total feedback across all content
- Average ratings by content type
- Positive/negative feedback distribution
- Recent feedback with comments
- User contribution tracking
- Time-based analytics (7, 30, 90 days)

## 9. Programmatic Feedback Access

```tsx
import { feedbackService } from '../services/feedbackService';

// Get feedback for specific content
const feedback = await feedbackService.getContentFeedback('image', imageId);
console.log('Average rating:', feedback.stats?.average_rating);
console.log('Total reviews:', feedback.stats?.total_feedback);

// Get user's feedback history
const history = await feedbackService.getFeedbackHistory({
  content_type: 'blog',
  min_rating: 4,
  page: 1,
  per_page: 10
});

// Get analytics
const analytics = await feedbackService.getAnalytics(30, 'image');
console.log('Total feedback last 30 days:', analytics.total_feedback);
```

## 10. Feedback-Driven Features

You can use feedback data to:

1. **Sort content by rating**: Show highest-rated content first
2. **Filter by quality**: Only show content with 4+ stars
3. **Improve generation**: Use low-rated content to adjust prompts
4. **User recommendations**: Suggest content based on feedback patterns
5. **A/B testing**: Compare feedback between variations

## Testing the System

1. Start the backend server: `make dev`
2. Navigate to any content (images, blogs, etc.)
3. Click the feedback button or use inline ratings
4. Submit feedback with ratings and comments
5. Visit `/feedback` to see the analytics dashboard
6. Check that feedback persists and updates correctly

## API Endpoints

- `POST /api/feedback/submit/` - Submit detailed feedback
- `POST /api/feedback/quick/` - Quick thumbs up/down
- `GET /api/feedback/<type>/<id>/` - Get content feedback & stats
- `GET /api/feedback/history/` - User's feedback history
- `GET /api/feedback/analytics/` - Feedback analytics
- `PUT /api/feedback/<id>/` - Update feedback
- `DELETE /api/feedback/<id>/` - Delete feedback

## Common Issues & Solutions

### Issue: Feedback not saving
- Check that user is authenticated
- Verify content_type and content_id are valid
- Ensure rating is between 1-5

### Issue: Stats not showing
- Make sure at least one feedback exists for the content
- Check that the content_type matches exactly

### Issue: Analytics empty
- Feedback analytics update after each submission
- May need to wait for data to populate
- Check date range filters

## Next Steps

1. Add feedback buttons to all content generators
2. Create feedback-based content recommendations
3. Implement AI learning from feedback
4. Add feedback rewards/gamification
5. Export feedback reports for analysis

---

The feedback system is now fully operational and ready for integration throughout the platform!