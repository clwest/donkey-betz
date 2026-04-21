# Backend Integration Testing Guide

## Overview
This guide provides instructions for testing the fully integrated React Native mobile app with the Django backend API.

## Prerequisites
1. **Backend Server Running**: Ensure the Django backend is running on `http://localhost:8001`
2. **Database Setup**: Make sure the PostgreSQL database is set up and migrations are applied
3. **Auth Token**: Test user credentials or auth token `<redacted-993f8273-2026-04-20>` should be available

## Running the Mobile App

### Web (Development)
```bash
cd ai-studio-premium
npm start --web
# or
expo start --web
```
Access at: http://localhost:8081

### iOS Simulator
```bash
expo start
# Then press 'i' for iOS simulator
```

### Android Emulator
```bash
expo start
# Then press 'a' for Android emulator
```

## Testing Features

### 1. Authentication Flow
- **Login**: Use credentials `testuser` / `testpass123`
- **Registration**: Create a new account
- **Token Persistence**: App should remember login state after restart
- **Logout**: Clear authentication and return to onboarding

**Test Steps:**
1. Open app (should show onboarding if not authenticated)
2. Try to login with test credentials
3. Verify home screen loads with user data
4. Close and reopen app (should stay authenticated)
5. Test logout functionality

### 2. Home Screen Integration
- **Dashboard Stats**: Real-time stats from backend API
- **Recent Content**: Shows latest user-generated content
- **Pull to Refresh**: Updates data from server
- **Quick Actions**: Navigation to different creation modes

**Test Steps:**
1. Check if stats display correctly (content count, images, API calls)
2. Pull down to refresh and verify data updates
3. Verify recent content shows actual user content
4. Test quick action buttons navigation

### 3. Content Generation
- **Text Generation**: Create blogs, social posts
- **Image Generation**: Generate images with different styles
- **Batch Generation**: Create multiple items at once
- **Progress Tracking**: Real-time generation progress

**Test Steps:**
1. Navigate to Studio screen
2. Try generating different content types
3. Verify progress indicators work
4. Check generated content appears in gallery/library

### 4. Gallery Management
- **Image Gallery**: View, favorite, delete images
- **Video Gallery**: Manage video content
- **Search & Filter**: Find content by type, tags, dates
- **Bulk Operations**: Select multiple items for actions

**Test Steps:**
1. Navigate to Gallery screen
2. Verify images load from backend
3. Test favoriting/unfavoriting items
4. Try search functionality
5. Test bulk selection and operations

### 5. Dashboard Analytics
- **Real-time Stats**: Live dashboard data
- **Activity Feed**: Recent user actions
- **Content Breakdown**: Charts and analytics
- **Auto Refresh**: Live updates every 30 seconds

**Test Steps:**
1. Open Dashboard screen
2. Verify stats load correctly
3. Check activity feed shows recent actions
4. Wait to see if stats auto-update
5. Pull to refresh for manual updates

### 6. Voice Studio Features
- **Audio Transcription**: Upload audio and get text
- **Voice-to-Content**: Convert speech to blogs/social posts
- **TTS Generation**: Convert text to speech
- **Voice History**: Manage previous recordings

**Test Steps:**
1. Navigate to Voice/Studio screen
2. Test audio recording (if device has microphone)
3. Try voice transcription features
4. Test text-to-speech functionality

## API Integration Points

### Core Services Created
1. **authService**: Login, logout, profile management
2. **contentService**: Content generation and management
3. **galleryService**: Media gallery operations
4. **voiceService**: Voice transcription and TTS
5. **dashboardService**: Analytics and statistics
6. **videoService**: Video generation and management

### State Management (Zustand Stores)
1. **useAuthStore**: Authentication state and user data
2. **useContentStore**: Content generation and library
3. **useGalleryStore**: Gallery management and operations
4. **useDashboardStore**: Dashboard analytics and stats

### Key Features Implemented
- **Offline Support**: Queued requests when offline
- **Error Handling**: User-friendly error messages
- **Loading States**: Progress indicators throughout
- **Token Management**: Automatic auth token handling
- **File Uploads**: Image and audio file uploading
- **Real-time Updates**: Live dashboard statistics
- **Pull-to-Refresh**: Update data from server
- **Platform Compatibility**: iOS, Android, and Web

## Troubleshooting

### Common Issues

1. **"Failed to fetch" errors**
   - Check backend server is running on port 8001
   - Verify network connectivity
   - Check CORS settings in Django

2. **Authentication failures**
   - Verify user credentials exist in database
   - Check auth token is valid
   - Clear AsyncStorage if needed

3. **Empty data displays**
   - Check user has generated content
   - Verify API endpoints return data
   - Check console for API errors

4. **Images not loading**
   - Check media files exist on server
   - Verify media URLs are correct
   - Check file permissions

### Debug Mode
Enable debug logging by checking console output:
- API requests and responses are logged
- Authentication status is tracked
- Error details are provided

### Testing with Mock Data
If backend is unavailable, the app gracefully handles errors:
- Shows empty states with helpful messages
- Provides retry mechanisms
- Maintains UI functionality

## Production Readiness

The mobile app includes production-ready features:
- **Error Boundaries**: Graceful error handling
- **Offline Queue**: Requests queued when offline
- **Token Refresh**: Automatic authentication renewal
- **Performance**: Optimized API calls and caching
- **Security**: Secure token storage and transmission
- **Accessibility**: Screen reader support
- **Platform Optimization**: Native feel on each platform

## Next Steps

For further development:
1. Add push notifications
2. Implement biometric authentication
3. Add app store deployment configs
4. Set up CI/CD pipelines
5. Add more comprehensive testing
6. Implement analytics tracking
7. Add deep linking support
8. Optimize for tablets

## Support

For issues or questions:
1. Check console logs for errors
2. Verify backend API is accessible
3. Test with provided auth token
4. Check network connectivity
5. Review API documentation in backend/api/urls.py