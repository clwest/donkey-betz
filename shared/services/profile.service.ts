import { apiClient } from './api.config';

interface UserProfile {
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

interface UserStats {
  content_breakdown: Record<string, number>;
  recent_activity: {
    last_7_days: number;
    last_30_days: number;
  };
  top_styles: Array<{ style?: string; 'metadata__style'?: string; count: number }>;
  storage: {
    images_mb: number;
    videos_mb: number;
    total_mb: number;
  };
}


class ProfileService {
  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get('/profile/');
    return response.data;
  }

  async updateProfile(data: Record<string, any>): Promise<{ message: string }> {
    const response = await apiClient.put('/profile/update/', data);
    return response.data;
  }

  async uploadAvatar(file: File): Promise<{ message: string; avatar_url: string }> {
    const formData = new FormData();
    formData.append('avatar', file);
    
    const response = await apiClient.post('/profile/avatar/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async deleteAvatar(): Promise<{ message: string }> {
    const response = await apiClient.delete('/profile/avatar/delete/');
    return response.data;
  }

  async getUserStats(): Promise<UserStats> {
    const response = await apiClient.get('/profile/stats/');
    return response.data;
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<{ message: string; token: string }> {
    const response = await apiClient.post('/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
    });
    return response.data;
  }
}

const profileService = new ProfileService();

// Export everything
export { profileService, type UserProfile, type UserStats };
export default profileService;