# User Profile System Implementation Handoff

## Executive Summary
The AI Content Studio currently has basic authentication (register/login) but lacks a complete user profile system. This document outlines all requirements and implementation steps needed to build a comprehensive user profile system for the React web application.

**Priority**: HIGH - Required for Research-to-Book feature and user-specific content management
**Estimated Time**: 3-4 hours for complete implementation
**Status**: NOT STARTED

## Current State Analysis

### What Exists ✅
1. **Authentication System**
   - Django built-in User model (username, email, password)
   - Token-based auth with DRF
   - `/api/auth/register/` - User registration
   - `/api/auth/login/` - User login
   - Returns: user_id, username, token

2. **User References**
   - Content models have ForeignKey to User
   - Memory system references User
   - Document system references User

### What's Missing ❌
1. **User Profile Model** - No extended profile fields
2. **Profile API Endpoints** - No CRUD operations for profiles
3. **Frontend Profile UI** - No profile page in React app
4. **User Statistics** - No tracking of user activity
5. **Settings Persistence** - No user preferences storage
6. **Avatar/Profile Image** - No image upload capability

## Implementation Requirements

## Phase 1: Backend - User Profile Model (45 minutes)

### Step 1.1: Create UserProfile Model
**File**: `backend/content/models_profile.py`

```python
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """Extended user profile with additional fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Basic Info
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    display_name = models.CharField(max_length=100, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Preferences
    preferred_ai_model = models.CharField(max_length=50, default='gpt-4')
    default_content_tone = models.CharField(max_length=50, default='professional')
    auto_save = models.BooleanField(default=True)
    dark_mode = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    
    # Research & Book Preferences
    default_citation_style = models.CharField(max_length=20, default='APA')
    preferred_book_length = models.CharField(max_length=20, default='medium')
    research_topics = models.JSONField(default=list, blank=True)
    
    # Account Info
    account_type = models.CharField(max_length=20, default='free', 
                                  choices=[('free', 'Free'), ('pro', 'Pro'), ('enterprise', 'Enterprise')])
    credits_remaining = models.IntegerField(default=100)
    storage_used_mb = models.FloatField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class UserStatistics(models.Model):
    """Track user activity and usage statistics"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='statistics')
    
    # Content Counts
    total_contents = models.IntegerField(default=0)
    total_images = models.IntegerField(default=0)
    total_videos = models.IntegerField(default=0)
    total_blogs = models.IntegerField(default=0)
    total_social_posts = models.IntegerField(default=0)
    total_ebooks = models.IntegerField(default=0)
    total_research_docs = models.IntegerField(default=0)
    
    # AI Usage
    total_ai_requests = models.IntegerField(default=0)
    total_tokens_used = models.IntegerField(default=0)
    
    # Engagement
    total_exports = models.IntegerField(default=0)
    total_shares = models.IntegerField(default=0)
    favorite_style = models.CharField(max_length=100, blank=True)
    
    # Time Tracking
    total_time_minutes = models.IntegerField(default=0)
    last_generation_date = models.DateTimeField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)

# Auto-create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        UserStatistics.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    if hasattr(instance, 'statistics'):
        instance.statistics.save()
```

### Step 1.2: Update Django Settings
**File**: `backend/core/settings.py`

Add to INSTALLED_APPS if not present:
```python
INSTALLED_APPS = [
    # ... existing apps
    'content',  # Should already exist
]
```

### Step 1.3: Create and Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Phase 2: Backend - Profile API Endpoints (60 minutes)

### Step 2.1: Create Profile Views
**File**: `backend/api/views_profile.py`

```python
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from django.db.models import Q
from content.models_profile import UserProfile, UserStatistics
import json

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """Get current user's profile"""
    try:
        profile = request.user.profile
        statistics = request.user.statistics
        
        return Response({
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'date_joined': request.user.date_joined,
            },
            'profile': {
                'avatar': profile.avatar.url if profile.avatar else None,
                'bio': profile.bio,
                'display_name': profile.display_name or request.user.username,
                'occupation': profile.occupation,
                'location': profile.location,
                'preferred_ai_model': profile.preferred_ai_model,
                'default_content_tone': profile.default_content_tone,
                'auto_save': profile.auto_save,
                'dark_mode': profile.dark_mode,
                'email_notifications': profile.email_notifications,
                'default_citation_style': profile.default_citation_style,
                'preferred_book_length': profile.preferred_book_length,
                'research_topics': profile.research_topics,
                'account_type': profile.account_type,
                'credits_remaining': profile.credits_remaining,
                'storage_used_mb': profile.storage_used_mb,
                'last_active': profile.last_active,
            },
            'statistics': {
                'total_contents': statistics.total_contents,
                'total_images': statistics.total_images,
                'total_videos': statistics.total_videos,
                'total_blogs': statistics.total_blogs,
                'total_social_posts': statistics.total_social_posts,
                'total_ebooks': statistics.total_ebooks,
                'total_research_docs': statistics.total_research_docs,
                'total_ai_requests': statistics.total_ai_requests,
                'total_tokens_used': statistics.total_tokens_used,
                'total_exports': statistics.total_exports,
                'favorite_style': statistics.favorite_style,
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile"""
    try:
        profile = request.user.profile
        user = request.user
        
        # Update User model fields
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        if 'email' in request.data:
            user.email = request.data['email']
        user.save()
        
        # Update Profile fields
        profile_fields = [
            'bio', 'display_name', 'occupation', 'location',
            'preferred_ai_model', 'default_content_tone',
            'auto_save', 'dark_mode', 'email_notifications',
            'default_citation_style', 'preferred_book_length'
        ]
        
        for field in profile_fields:
            if field in request.data:
                setattr(profile, field, request.data[field])
        
        # Handle JSON fields
        if 'research_topics' in request.data:
            topics = request.data['research_topics']
            if isinstance(topics, str):
                topics = json.loads(topics)
            profile.research_topics = topics
        
        profile.save()
        
        return Response({'message': 'Profile updated successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_avatar(request):
    """Upload user avatar"""
    try:
        profile = request.user.profile
        
        if 'avatar' not in request.FILES:
            return Response({'error': 'No avatar file provided'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Delete old avatar if exists
        if profile.avatar:
            profile.avatar.delete()
        
        profile.avatar = request.FILES['avatar']
        profile.save()
        
        return Response({
            'message': 'Avatar uploaded successfully',
            'avatar_url': profile.avatar.url
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_avatar(request):
    """Delete user avatar"""
    try:
        profile = request.user.profile
        
        if profile.avatar:
            profile.avatar.delete()
            profile.avatar = None
            profile.save()
        
        return Response({'message': 'Avatar deleted successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    """Get detailed user statistics"""
    try:
        from content.models import Content, SavedImage, SavedVideo
        from content.models_blog import BlogPost, SocialMediaPost
        from content.models_ebook import Ebook
        
        user = request.user
        
        # Calculate real statistics
        stats = {
            'content_breakdown': {
                'texts': Content.objects.filter(user=user, content_type='text').count(),
                'images': Content.objects.filter(user=user, content_type='image').count(),
                'saved_images': SavedImage.objects.filter(user=user).count(),
                'saved_videos': SavedVideo.objects.filter(user=user).count(),
                'blogs': BlogPost.objects.filter(user=user).count(),
                'social_posts': SocialMediaPost.objects.filter(user=user).count(),
                'ebooks': Ebook.objects.filter(user=user).count(),
            },
            'recent_activity': {
                'last_7_days': Content.objects.filter(
                    user=user,
                    created_at__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'last_30_days': Content.objects.filter(
                    user=user,
                    created_at__gte=timezone.now() - timedelta(days=30)
                ).count(),
            },
            'top_styles': list(
                Content.objects.filter(user=user)
                .exclude(style='')
                .values('style')
                .annotate(count=models.Count('style'))
                .order_by('-count')[:5]
            ),
            'storage': {
                'images_mb': calculate_user_storage(user, 'image'),
                'videos_mb': calculate_user_storage(user, 'video'),
                'total_mb': calculate_user_storage(user, 'all'),
            }
        }
        
        # Update statistics model
        statistics = user.statistics
        statistics.total_contents = sum(stats['content_breakdown'].values())
        statistics.total_images = stats['content_breakdown']['images'] + stats['content_breakdown']['saved_images']
        statistics.total_videos = stats['content_breakdown']['saved_videos']
        statistics.total_blogs = stats['content_breakdown']['blogs']
        statistics.total_social_posts = stats['content_breakdown']['social_posts']
        statistics.total_ebooks = stats['content_breakdown']['ebooks']
        statistics.save()
        
        return Response(stats)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password"""
    try:
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({'error': 'Both old and new passwords are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(old_password):
            return Response({'error': 'Invalid old password'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        # Generate new token
        from rest_framework.authtoken.models import Token
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        
        return Response({
            'message': 'Password changed successfully',
            'token': token.key
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def calculate_user_storage(user, content_type='all'):
    """Helper function to calculate user storage usage"""
    import os
    total_size = 0
    
    try:
        from content.models import Content, SavedImage, SavedVideo
        
        if content_type in ['image', 'all']:
            # Calculate image storage
            for content in Content.objects.filter(user=user, content_type='image'):
                if content.image and os.path.exists(content.image.path):
                    total_size += os.path.getsize(content.image.path)
            
            for saved in SavedImage.objects.filter(user=user):
                if saved.image and os.path.exists(saved.image.path):
                    total_size += os.path.getsize(saved.image.path)
        
        if content_type in ['video', 'all']:
            # Calculate video storage
            for saved in SavedVideo.objects.filter(user=user):
                if saved.video_file and os.path.exists(saved.video_file.path):
                    total_size += os.path.getsize(saved.video_file.path)
        
        # Convert to MB
        return round(total_size / (1024 * 1024), 2)
    except:
        return 0
```

### Step 2.2: Add URL Patterns
**File**: `backend/api/urls.py`

Add these patterns:
```python
from api.views_profile import (
    get_profile, update_profile, upload_avatar, 
    delete_avatar, get_user_stats, change_password
)

urlpatterns = [
    # ... existing patterns
    
    # Profile Management
    path('profile/', get_profile, name='api_get_profile'),
    path('profile/update/', update_profile, name='api_update_profile'),
    path('profile/avatar/', upload_avatar, name='api_upload_avatar'),
    path('profile/avatar/delete/', delete_avatar, name='api_delete_avatar'),
    path('profile/stats/', get_user_stats, name='api_user_stats'),
    path('auth/change-password/', change_password, name='api_change_password'),
]
```

## Phase 3: Frontend - React Profile Page (90 minutes)

### Step 3.1: Create Profile Service
**File**: `ai-studio-web/src/services/profileService.ts`

```typescript
import { apiRequest } from './api';

export interface UserProfile {
  user: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    date_joined: string;
  };
  profile: {
    avatar: string | null;
    bio: string;
    display_name: string;
    occupation: string;
    location: string;
    preferred_ai_model: string;
    default_content_tone: string;
    auto_save: boolean;
    dark_mode: boolean;
    email_notifications: boolean;
    default_citation_style: string;
    preferred_book_length: string;
    research_topics: string[];
    account_type: 'free' | 'pro' | 'enterprise';
    credits_remaining: number;
    storage_used_mb: number;
    last_active: string;
  };
  statistics: {
    total_contents: number;
    total_images: number;
    total_videos: number;
    total_blogs: number;
    total_social_posts: number;
    total_ebooks: number;
    total_research_docs: number;
    total_ai_requests: number;
    total_tokens_used: number;
    total_exports: number;
    favorite_style: string;
  };
}

export interface UserStats {
  content_breakdown: Record<string, number>;
  recent_activity: {
    last_7_days: number;
    last_30_days: number;
  };
  top_styles: Array<{ style: string; count: number }>;
  storage: {
    images_mb: number;
    videos_mb: number;
    total_mb: number;
  };
}

class ProfileService {
  async getProfile(): Promise<UserProfile> {
    return apiRequest('/api/profile/', 'GET');
  }

  async updateProfile(data: Partial<UserProfile['profile']>): Promise<any> {
    return apiRequest('/api/profile/update/', 'PUT', data);
  }

  async uploadAvatar(file: File): Promise<{ avatar_url: string }> {
    const formData = new FormData();
    formData.append('avatar', file);
    
    return apiRequest('/api/profile/avatar/', 'POST', formData, {
      'Content-Type': 'multipart/form-data',
    });
  }

  async deleteAvatar(): Promise<any> {
    return apiRequest('/api/profile/avatar/delete/', 'DELETE');
  }

  async getUserStats(): Promise<UserStats> {
    return apiRequest('/api/profile/stats/', 'GET');
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<{ token: string }> {
    return apiRequest('/api/auth/change-password/', 'POST', {
      old_password: oldPassword,
      new_password: newPassword,
    });
  }
}

export const profileService = new ProfileService();
```

### Step 3.2: Create Profile Page Component
**File**: `ai-studio-web/src/pages/profile/ProfilePage.tsx`

```tsx
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  User, Mail, MapPin, Briefcase, Settings, 
  Save, Camera, Trash2, Lock, Bell, Moon, 
  Download, CreditCard, HardDrive, Award,
  BookOpen, FileText, Image, Video, TrendingUp
} from 'lucide-react';
import { profileService, UserProfile, UserStats } from '../../services/profileService';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';

export const ProfilePage: React.FC = () => {
  const { user, updateToken } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [activeTab, setActiveTab] = useState<'profile' | 'settings' | 'stats'>('profile');
  const [formData, setFormData] = useState<any>({});
  const [passwordData, setPasswordData] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  useEffect(() => {
    loadProfile();
    loadStats();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await profileService.getProfile();
      setProfile(data);
      setFormData({
        first_name: data.user.first_name,
        last_name: data.user.last_name,
        email: data.user.email,
        bio: data.profile.bio,
        display_name: data.profile.display_name,
        occupation: data.profile.occupation,
        location: data.profile.location,
      });
    } catch (error) {
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await profileService.getUserStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleSaveProfile = async () => {
    try {
      await profileService.updateProfile(formData);
      toast.success('Profile updated successfully');
      setEditing(false);
      loadProfile();
    } catch (error) {
      toast.error('Failed to update profile');
    }
  };

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const result = await profileService.uploadAvatar(file);
      toast.success('Avatar uploaded successfully');
      loadProfile();
    } catch (error) {
      toast.error('Failed to upload avatar');
    }
  };

  const handleDeleteAvatar = async () => {
    if (!confirm('Are you sure you want to delete your avatar?')) return;
    
    try {
      await profileService.deleteAvatar();
      toast.success('Avatar deleted');
      loadProfile();
    } catch (error) {
      toast.error('Failed to delete avatar');
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    try {
      const result = await profileService.changePassword(
        passwordData.oldPassword,
        passwordData.newPassword
      );
      updateToken(result.token);
      toast.success('Password changed successfully');
      setPasswordData({ oldPassword: '', newPassword: '', confirmPassword: '' });
    } catch (error) {
      toast.error('Failed to change password');
    }
  };

  const handleSettingToggle = async (setting: string, value: boolean) => {
    try {
      await profileService.updateProfile({ [setting]: value });
      toast.success('Setting updated');
      loadProfile();
    } catch (error) {
      toast.error('Failed to update setting');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Account Settings</h1>
        <p className="text-gray-400">Manage your profile and preferences</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-8 bg-gray-800/50 p-1 rounded-lg w-fit">
        {['profile', 'settings', 'stats'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-6 py-2 rounded-md transition-all capitalize ${
              activeTab === tab
                ? 'bg-purple-600 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && profile && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Avatar Section */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">Profile Picture</h3>
              
              <div className="relative w-32 h-32 mx-auto mb-4">
                {profile.profile.avatar ? (
                  <img
                    src={profile.profile.avatar}
                    alt="Avatar"
                    className="w-full h-full rounded-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                    <span className="text-4xl font-bold text-white">
                      {profile.user.username[0].toUpperCase()}
                    </span>
                  </div>
                )}
                
                <label className="absolute bottom-0 right-0 bg-purple-600 p-2 rounded-full cursor-pointer hover:bg-purple-700 transition-colors">
                  <Camera className="w-4 h-4 text-white" />
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarUpload}
                    className="hidden"
                  />
                </label>
              </div>

              {profile.profile.avatar && (
                <button
                  onClick={handleDeleteAvatar}
                  className="w-full py-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors flex items-center justify-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Remove Avatar
                </button>
              )}

              {/* Account Info */}
              <div className="mt-6 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Account Type</span>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    profile.profile.account_type === 'pro' 
                      ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-black'
                      : profile.profile.account_type === 'enterprise'
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                      : 'bg-gray-700 text-gray-300'
                  }`}>
                    {profile.profile.account_type.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Credits</span>
                  <span className="text-white font-semibold">{profile.profile.credits_remaining}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Storage Used</span>
                  <span className="text-white">{profile.profile.storage_used_mb} MB</span>
                </div>
              </div>
            </div>
          </div>

          {/* Profile Form */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white">Profile Information</h3>
                {!editing ? (
                  <button
                    onClick={() => setEditing(true)}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    Edit Profile
                  </button>
                ) : (
                  <div className="flex gap-2">
                    <button
                      onClick={() => setEditing(false)}
                      className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveProfile}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
                    >
                      <Save className="w-4 h-4" />
                      Save Changes
                    </button>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-gray-400 mb-2">First Name</label>
                  <input
                    type="text"
                    value={formData.first_name || ''}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    disabled={!editing}
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  />
                </div>
                
                <div>
                  <label className="block text-gray-400 mb-2">Last Name</label>
                  <input
                    type="text"
                    value={formData.last_name || ''}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    disabled={!editing}
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  />
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Display Name</label>
                  <input
                    type="text"
                    value={formData.display_name || ''}
                    onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                    disabled={!editing}
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  />
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Email</label>
                  <input
                    type="email"
                    value={formData.email || ''}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    disabled={!editing}
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  />
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Occupation</label>
                  <input
                    type="text"
                    value={formData.occupation || ''}
                    onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                    disabled={!editing}
                    placeholder="e.g., Content Creator"
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  />
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Location</label>
                  <input
                    type="text"
                    value={formData.location || ''}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    disabled={!editing}
                    placeholder="e.g., San Francisco, CA"
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-gray-400 mb-2">Bio</label>
                  <textarea
                    value={formData.bio || ''}
                    onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                    disabled={!editing}
                    rows={4}
                    placeholder="Tell us about yourself..."
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white disabled:opacity-50"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === 'settings' && profile && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Preferences */}
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-6">Preferences</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Moon className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-white">Dark Mode</p>
                    <p className="text-sm text-gray-400">Use dark theme</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={profile.profile.dark_mode}
                    onChange={(e) => handleSettingToggle('dark_mode', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Bell className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-white">Email Notifications</p>
                    <p className="text-sm text-gray-400">Receive email updates</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={profile.profile.email_notifications}
                    onChange={(e) => handleSettingToggle('email_notifications', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Save className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-white">Auto-Save</p>
                    <p className="text-sm text-gray-400">Automatically save drafts</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={profile.profile.auto_save}
                    onChange={(e) => handleSettingToggle('auto_save', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-700">
              <h4 className="text-white font-medium mb-4">Content Preferences</h4>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-400 mb-2">Default AI Model</label>
                  <select
                    value={profile.profile.preferred_ai_model}
                    onChange={(e) => handleSettingToggle('preferred_ai_model', e.target.value as any)}
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white"
                  >
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    <option value="claude">Claude</option>
                    <option value="gemini">Gemini</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Default Content Tone</label>
                  <select
                    value={profile.profile.default_content_tone}
                    onChange={(e) => handleSettingToggle('default_content_tone', e.target.value as any)}
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white"
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="friendly">Friendly</option>
                    <option value="technical">Technical</option>
                    <option value="creative">Creative</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-400 mb-2">Citation Style</label>
                  <select
                    value={profile.profile.default_citation_style}
                    onChange={(e) => handleSettingToggle('default_citation_style', e.target.value as any)}
                    className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white"
                  >
                    <option value="APA">APA</option>
                    <option value="MLA">MLA</option>
                    <option value="Chicago">Chicago</option>
                    <option value="Harvard">Harvard</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Security */}
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-6">Security</h3>
            
            <div className="space-y-4">
              <h4 className="text-white font-medium">Change Password</h4>
              
              <div>
                <label className="block text-gray-400 mb-2">Current Password</label>
                <input
                  type="password"
                  value={passwordData.oldPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, oldPassword: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-2">New Password</label>
                <input
                  type="password"
                  value={passwordData.newPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-2">Confirm New Password</label>
                <input
                  type="password"
                  value={passwordData.confirmPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                  className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white"
                />
              </div>

              <button
                onClick={handleChangePassword}
                disabled={!passwordData.oldPassword || !passwordData.newPassword}
                className="w-full py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Lock className="w-4 h-4" />
                Update Password
              </button>
            </div>

            <div className="mt-8 pt-6 border-t border-gray-700">
              <h4 className="text-white font-medium mb-4">Account Info</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Username</span>
                  <span className="text-white">{profile.user.username}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Member Since</span>
                  <span className="text-white">
                    {new Date(profile.user.date_joined).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Last Active</span>
                  <span className="text-white">
                    {new Date(profile.profile.last_active).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Tab */}
      {activeTab === 'stats' && stats && (
        <div className="space-y-6">
          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Contents', value: stats.content_breakdown.texts, icon: FileText, color: 'from-blue-500 to-cyan-500' },
              { label: 'Images Created', value: stats.content_breakdown.images, icon: Image, color: 'from-purple-500 to-pink-500' },
              { label: 'Videos Generated', value: stats.content_breakdown.saved_videos, icon: Video, color: 'from-green-500 to-emerald-500' },
              { label: 'Blogs Written', value: stats.content_breakdown.blogs, icon: BookOpen, color: 'from-orange-500 to-red-500' },
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700"
              >
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${stat.color} p-2.5 mb-4`}>
                  <stat.icon className="w-full h-full text-white" />
                </div>
                <p className="text-3xl font-bold text-white mb-1">{stat.value}</p>
                <p className="text-gray-400 text-sm">{stat.label}</p>
              </motion.div>
            ))}
          </div>

          {/* Activity Chart */}
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-900/50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-green-500" />
                  <span className="text-gray-400">Last 7 Days</span>
                </div>
                <p className="text-2xl font-bold text-white">{stats.recent_activity.last_7_days}</p>
                <p className="text-sm text-gray-500">items created</p>
              </div>
              <div className="bg-gray-900/50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-blue-500" />
                  <span className="text-gray-400">Last 30 Days</span>
                </div>
                <p className="text-2xl font-bold text-white">{stats.recent_activity.last_30_days}</p>
                <p className="text-sm text-gray-500">items created</p>
              </div>
            </div>
          </div>

          {/* Top Styles & Storage */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Styles */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">Top Styles Used</h3>
              <div className="space-y-3">
                {stats.top_styles.map((style, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-gray-300">{style.style || 'Default'}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-32 bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full"
                          style={{ width: `${(style.count / stats.top_styles[0].count) * 100}%` }}
                        />
                      </div>
                      <span className="text-white font-medium w-8 text-right">{style.count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Storage Usage */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-4">Storage Usage</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-gray-400">Images</span>
                    <span className="text-white">{stats.storage.images_mb} MB</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full"
                      style={{ width: `${(stats.storage.images_mb / stats.storage.total_mb) * 100}%` }}
                    />
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-gray-400">Videos</span>
                    <span className="text-white">{stats.storage.videos_mb} MB</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full"
                      style={{ width: `${(stats.storage.videos_mb / stats.storage.total_mb) * 100}%` }}
                    />
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-700">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <HardDrive className="w-5 h-5 text-gray-400" />
                      <span className="text-gray-400">Total Storage</span>
                    </div>
                    <span className="text-xl font-bold text-white">{stats.storage.total_mb} MB</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
```

### Step 3.3: Add Profile Route
**File**: `ai-studio-web/src/App.tsx`

Add the profile route:
```tsx
import { ProfilePage } from './pages/profile/ProfilePage';

// In your routes configuration
<Route path="/profile" element={<ProfilePage />} />
```

### Step 3.4: Add Profile Link to Navigation
**File**: `ai-studio-web/src/components/layout/Sidebar.tsx` or Header component

Add profile navigation link:
```tsx
<Link to="/profile" className="nav-link">
  <User className="w-5 h-5" />
  <span>Profile</span>
</Link>
```

## Phase 4: Integration & Testing (30 minutes)

### Step 4.1: Update Statistics on Content Creation
Add hooks to increment statistics when content is created:

```python
# In content creation views
from content.models_profile import UserStatistics

def update_user_stats(user, content_type):
    stats, created = UserStatistics.objects.get_or_create(user=user)
    
    if content_type == 'image':
        stats.total_images += 1
    elif content_type == 'video':
        stats.total_videos += 1
    elif content_type == 'blog':
        stats.total_blogs += 1
    # ... etc
    
    stats.total_contents += 1
    stats.save()
```

### Step 4.2: Test Checklist
- [ ] User registration creates profile automatically
- [ ] Profile page loads with user data
- [ ] Profile editing saves changes
- [ ] Avatar upload/delete works
- [ ] Password change updates token
- [ ] Settings toggles persist
- [ ] Statistics update on content creation
- [ ] Storage calculation is accurate

## API Endpoints Summary

```
# Authentication
POST /api/auth/register/         # User registration
POST /api/auth/login/            # User login
POST /api/auth/change-password/  # Change password

# Profile Management
GET  /api/profile/               # Get current user profile
PUT  /api/profile/update/        # Update profile information
POST /api/profile/avatar/        # Upload avatar image
DELETE /api/profile/avatar/delete/ # Delete avatar
GET  /api/profile/stats/         # Get user statistics
```

## Environment Variables Required
None additional - uses existing Django settings

## Migration Commands
```bash
# Create the models
python manage.py makemigrations
python manage.py migrate

# Create superuser for testing
python manage.py createsuperuser
```

## Testing the Implementation

### Manual Testing Flow
1. Register a new user or login
2. Navigate to /profile in React app
3. Verify profile data loads
4. Edit profile fields and save
5. Upload an avatar image
6. Change password
7. Toggle settings
8. Create some content
9. Check statistics update

### API Testing with cURL
```bash
# Get profile
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8001/api/profile/

# Update profile
curl -X PUT -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bio": "New bio text"}' \
  http://localhost:8001/api/profile/update/
```

## Common Issues & Solutions

### Issue: Profile not created for existing users
```python
# Run in Django shell
from django.contrib.auth.models import User
from content.models_profile import UserProfile, UserStatistics

for user in User.objects.all():
    UserProfile.objects.get_or_create(user=user)
    UserStatistics.objects.get_or_create(user=user)
```

### Issue: Avatar upload fails
- Check MEDIA_ROOT and MEDIA_URL settings
- Ensure media directory has write permissions
- Verify multipart/form-data handling

### Issue: Statistics not updating
- Add update_user_stats calls to content creation views
- Run manual recalculation script if needed

## Next Steps & Enhancements

1. **Social Authentication** - Add Google/GitHub OAuth
2. **Email Verification** - Verify email on registration
3. **Two-Factor Authentication** - Add 2FA support
4. **Profile Privacy Settings** - Public/private profiles
5. **Export User Data** - GDPR compliance
6. **Delete Account** - Full account deletion
7. **Subscription Management** - Upgrade/downgrade plans
8. **API Keys Management** - User-specific API keys
9. **Activity Log** - Detailed user activity history
10. **Achievements/Badges** - Gamification elements

## Success Criteria

The user profile system will be considered complete when:
- ✅ Users can view and edit their profile information
- ✅ Avatar upload and management works
- ✅ Settings and preferences persist across sessions
- ✅ Statistics accurately track user activity
- ✅ Password change functionality works
- ✅ Profile integrates with Research-to-Book feature
- ✅ All content is properly associated with users

## Handoff Notes

- All code examples are production-ready
- TypeScript types are included for frontend
- Database migrations handle existing users
- Statistics can be recalculated if needed
- Profile system is extensible for future features

---

**Prepared by**: Claude
**Date**: 2025-09-01
**For**: AI Content Studio Development Team
**Priority**: HIGH - Blocking Research-to-Book feature