import React, { useState, useEffect } from 'react';
import { XMarkIcon, ClipboardDocumentIcon, CheckIcon } from '@heroicons/react/24/outline';
import { contentService } from '../../../services/content.service';
import { Logger } from '../../../utils/logger';
import { toast } from 'sonner';
import { FeedbackWidget } from '../../feedback/FeedbackWidget';

interface SocialViewerProps {
  socialPostId: number;
  isOpen: boolean;
  onClose: () => void;
}

interface SocialPost {
  id: number;
  topic: string;
  platforms: {
    [platform: string]: Array<{
      post_number: number;
      content: string;
      character_count: number;
      within_limit: boolean;
      hashtags: string[];
    }>;
  };
  tone: string;
  created_at: string;
}

export function SocialViewer({ socialPostId, isOpen, onClose }: SocialViewerProps) {
  
  const [socialPost, setSocialPost] = useState<SocialPost | null>(null);
  const [loading, setLoading] = useState(true);
  const [copiedPost, setCopiedPost] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('');

  useEffect(() => {
    if (isOpen && socialPostId) {
      loadSocialPost();
    }
  }, [isOpen, socialPostId]);


  const loadSocialPost = async () => {
    setLoading(true);
    console.log('Loading social post:', socialPostId);
    try {
      Logger.api('GET', `/api/content/social/${socialPostId}/`);
      const response = await contentService.getSocialPost(socialPostId);
      console.log('Raw API response:', response);
      
      // Handle nested response structure
      let postData = response.social_post_set || response;
      
      console.log('Initial postData:', postData);
      
      // Check if platforms contains another nested object instead of actual platform arrays
      if (postData && postData.platforms && typeof postData.platforms === 'object') {
        const platformsObj = postData.platforms;
        
        // Check if this is the actual platforms object (contains twitter, facebook, etc.)
        const platformKeys = Object.keys(platformsObj);
        const hasRealPlatforms = platformKeys.some(key => 
          ['twitter', 'facebook', 'linkedin', 'instagram', 'tiktok'].includes(key)
        );
        
        if (hasRealPlatforms) {
          console.log('Found real platforms directly');
        } else {
          // This means platforms contains another nested object - extract the real platforms
          console.log('Platforms is nested, extracting real platforms');
          console.log('Nested platforms keys:', platformKeys);
          
          // Look for the platforms property inside the nested object
          if (platformsObj.platforms && typeof platformsObj.platforms === 'object') {
            console.log('Found real platforms in nested structure');
            postData = {
              ...postData,
              platforms: platformsObj.platforms,
              // Preserve other fields from the nested object if they exist
              id: platformsObj.id || postData.id,
              topic: platformsObj.topic || postData.topic,
              created_at: platformsObj.created_at || postData.created_at
            };
          }
        }
      }
      
      console.log('Final processed post data:', postData);
      
      // Ensure tone field exists
      const normalizedData = {
        ...postData,
        tone: postData.tone || 'engaging'
      };
      setSocialPost(normalizedData);
      
      // Set first platform as active tab
      if (postData.platforms) {
        const firstPlatform = Object.keys(postData.platforms)[0];
        setActiveTab(firstPlatform);
      }
      
      Logger.state('SocialViewer', 'Social post loaded', { id: socialPostId });
    } catch (error: any) {
      Logger.error('SocialViewer.loadSocialPost', error);
      toast.error('Failed to load social posts');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (content: string, postId: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedPost(postId);
      setTimeout(() => setCopiedPost(null), 2000);
      toast.success('Copied to clipboard!');
    } catch (error) {
      toast.error('Failed to copy');
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch(platform) {
      case 'twitter': return '🐦';
      case 'linkedin': return '💼';
      case 'instagram': return '📷';
      case 'facebook': return '👥';
      case 'tiktok': return '🎵';
      default: return '📱';
    }
  };

  const getPlatformColor = (platform: string) => {
    switch(platform) {
      case 'twitter': return 'from-blue-500/20 to-blue-600/20';
      case 'linkedin': return 'from-blue-600/20 to-blue-700/20';
      case 'instagram': return 'from-purple-500/20 to-pink-500/20';
      case 'facebook': return 'from-blue-500/20 to-blue-600/20';
      case 'tiktok': return 'from-gray-600/20 to-gray-700/20';
      default: return 'from-gray-600/20 to-gray-700/20';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div className="fixed inset-0 transition-opacity" aria-hidden="true">
          <div className="absolute inset-0 bg-black opacity-75" onClick={onClose}></div>
        </div>

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-background rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-semibold text-foreground">
                {loading ? 'Loading...' : socialPost?.topic || 'Social Media Posts'}
              </h3>
              <button
                onClick={onClose}
                className="text-foreground hover:text-foreground transition-colors"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-4 max-h-[70vh] overflow-y-auto">
            {loading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
              </div>
            ) : socialPost ? (
              <div className="space-y-4">
                {/* Metadata */}
                <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                  <span>Tone: <span className="text-foreground">{socialPost.tone}</span></span>
                  <span>Created: <span className="text-foreground">
                    {new Date(socialPost.created_at).toLocaleDateString()}
                  </span></span>
                  <span>Platforms: <span className="text-foreground">
                    {Object.keys(socialPost.platforms).length}
                  </span></span>
                </div>

                {/* Platform Tabs */}
                <div className="border-b border-border">
                  <div className="flex gap-2 overflow-x-auto">
                    {Object.keys(socialPost.platforms).map(platform => (
                      <button
                        key={platform}
                        onClick={() => setActiveTab(platform)}
                        className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                          activeTab === platform
                            ? 'border-primary-500 text-primary-400'
                            : 'border-transparent text-muted-foreground hover:text-foreground'
                        }`}
                      >
                        <span className="text-lg">{getPlatformIcon(platform)}</span>
                        <span className="capitalize">{platform}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Posts */}
                {activeTab && socialPost.platforms[activeTab] && Array.isArray(socialPost.platforms[activeTab]) && (
                  <div className="space-y-4">
                    {socialPost.platforms[activeTab].map((post, index) => (
                      <div 
                        key={`${activeTab}-${index}`}
                        className={`glass rounded-xl p-5 bg-gradient-to-br ${getPlatformColor(activeTab)}`}
                      >
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <span className="text-2xl">{getPlatformIcon(activeTab)}</span>
                            <span className="text-sm text-muted-foreground">
                              Variation {post.post_number}
                            </span>
                          </div>
                          <div className={`text-sm ${
                            !post.within_limit ? 'text-red-500' : 'text-muted-foreground'
                          }`}>
                            {post.character_count} chars
                          </div>
                        </div>

                        <p className="text-foreground whitespace-pre-wrap mb-3">
                          {post.content}
                        </p>

                        {post.hashtags && post.hashtags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-3">
                            {post.hashtags.map((tag, idx) => (
                              <span 
                                key={idx}
                                className="text-xs bg-primary-500/20 text-primary-300 px-2 py-1 rounded-full"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}

                        <button
                          onClick={() => copyToClipboard(post.content, `${activeTab}-${index}`)}
                          className="flex items-center gap-2 px-3 py-1.5 bg-card/50 hover:bg-dark-700/50 
                                   text-muted-foreground hover:text-foreground rounded-lg transition-all border border-dark-600"
                        >
                          {copiedPost === `${activeTab}-${index}` ? (
                            <>
                              <CheckIcon className="w-4 h-4 text-green-500" />
                              <span className="text-sm text-green-500">Copied!</span>
                            </>
                          ) : (
                            <>
                              <ClipboardDocumentIcon className="w-4 h-4" />
                              <span className="text-sm">Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                No social posts found
              </div>
            )}
          </div>

          {/* Feedback Section */}
          {socialPost && (
            <div className="px-6 py-4 border-t border-border">
              <FeedbackWidget
                contentType="social"
                contentId={socialPost.id}
                contentTitle={socialPost.topic}
                inline={true}
                showStats={true}
              />
            </div>
          )}

          {/* Footer */}
          <div className="bg-card px-6 py-3">
            <div className="flex justify-end">
              <button
                onClick={onClose}
                className="px-4 py-2 bg-dark-700 text-muted-foreground rounded-lg hover:bg-dark-600 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}