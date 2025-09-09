export type Platform = {
  id: string;
  name: string;
  charLimit: number;
  hashtagLimit: number;
  icon: string;
  color: string;
  selected: boolean;
}

export type SocialPost = {
  platform: string;
  content: string;
  hashtags?: string[];
  characterCount: number;
  variations?: SocialPost[];
}

export type SocialGenerationRequest = {
  topic: string;
  platforms: string[];
  tone?: 'professional' | 'casual' | 'humorous' | 'inspirational' | 'educational' | 'technical' | 'marketing';
  variations?: number;
  includeHashtags?: boolean;
  includeEmojis?: boolean;
  targetAudience?: string;
  cta?: string;
}

export type SocialPostItem = {
  post_number: number;
  content: string;
  character_count: number;
  within_limit: boolean;
  hashtags: string[];
}

export type SocialGenerationResponse = {
  success: boolean;
  social_posts: {
    id: number;
    topic: string;
    platforms: {
      [platform: string]: SocialPostItem[];
    };
    created_at: string;
  };
  content_id: number;
}

export const PLATFORMS: Platform[] = [
  { 
    id: 'twitter', 
    name: 'Twitter/X', 
    charLimit: 280, 
    hashtagLimit: 3, 
    icon: '🐦', 
    color: 'border-blue-500/50 bg-blue-500/10 hover:bg-blue-500/20', 
    selected: true 
  },
  { 
    id: 'linkedin', 
    name: 'LinkedIn', 
    charLimit: 3000, 
    hashtagLimit: 5, 
    icon: '💼', 
    color: 'border-blue-600/50 bg-blue-600/10 hover:bg-blue-600/20', 
    selected: true 
  },
  { 
    id: 'instagram', 
    name: 'Instagram', 
    charLimit: 2200, 
    hashtagLimit: 30, 
    icon: '📷', 
    color: 'border-pink-500/50 bg-gradient-to-br from-purple-500/10 to-pink-500/10 hover:from-purple-500/20 hover:to-pink-500/20', 
    selected: true 
  },
  { 
    id: 'facebook', 
    name: 'Facebook', 
    charLimit: 63206, 
    hashtagLimit: 5, 
    icon: '👥', 
    color: 'border-blue-500/50 bg-blue-500/10 hover:bg-blue-500/20', 
    selected: false 
  },
  { 
    id: 'tiktok', 
    name: 'TikTok', 
    charLimit: 2200, 
    hashtagLimit: 10, 
    icon: '🎵', 
    color: 'border-gray-400/50 bg-gray-400/10 hover:bg-gray-400/20', 
    selected: false 
  }
];