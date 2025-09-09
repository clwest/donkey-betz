import React, { useState } from 'react';
import { PLATFORMS } from './types';
import type { Platform, SocialGenerationRequest, SocialGenerationResponse } from './types';
import PlatformSelector from './PlatformSelector';
import SocialPostCard from './SocialPostCard';
import { contentService } from '../../../services/content.service';
import { SparklesIcon } from '@heroicons/react/24/outline';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { toast } from 'sonner';

const SocialMediaGenerator: React.FC = () => {
  const [platforms, setPlatforms] = useState<Platform[]>(PLATFORMS);
  const [topic, setTopic] = useState('');
  const [tone, setTone] = useState<SocialGenerationRequest['tone']>('professional');
  const [variations, setVariations] = useState(3);
  const [includeHashtags, setIncludeHashtags] = useState(true);
  const [includeEmojis, setIncludeEmojis] = useState(true);
  const [targetAudience, setTargetAudience] = useState('');
  const [cta, setCta] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPosts, setGeneratedPosts] = useState<SocialGenerationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('');

  const handlePlatformToggle = (platformId: string) => {
    setPlatforms(prev => prev.map(p => 
      p.id === platformId ? { ...p, selected: !p.selected } : p
    ));
  };

  const handleGenerate = async () => {
    const selectedPlatforms = platforms.filter(p => p.selected);
    
    if (selectedPlatforms.length === 0) {
      setError('Please select at least one platform');
      return;
    }

    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setError(null);
    setIsGenerating(true);

    try {
      const request: SocialGenerationRequest = {
        topic,
        platforms: selectedPlatforms.map(p => p.id),
        tone,
        variations,
        includeHashtags,
        includeEmojis,
        targetAudience: targetAudience || undefined,
        cta: cta || undefined,
      };

      const response = await contentService.generateSocialPosts({
        topic: request.topic,
        platforms: request.platforms,
        tone: request.tone,
        variations: request.variations,
        hashtags: request.includeHashtags,
      });

      console.log('Social posts response:', response);
      setGeneratedPosts(response);
      // Set first platform as active tab
      if (response.social_posts?.platforms) {
        const firstPlatform = Object.keys(response.social_posts.platforms)[0];
        setActiveTab(firstPlatform || selectedPlatforms[0].id);
      }
      
      // Show success message
      toast.success('Social posts generated and saved to Content Library!');
    } catch (err) {
      console.error('Error generating social posts:', err);
      setError('Failed to generate social posts. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSavePost = async (platform: string, content: string, index: number) => {
    try {
      // Posts are automatically saved when generated
      // This is just for user feedback
      console.log('Post already saved:', { platform, content, index });
      toast.success(`${platform} post saved! View in Content Library.`);
    } catch (err) {
      console.error('Error:', err);
      toast.error('Failed to save post');
    }
  };

  const handleEditPost = (platform: string, index: number, newContent: string) => {
    if (!generatedPosts || !generatedPosts.social_posts) return;

    setGeneratedPosts(prev => {
      if (!prev || !prev.social_posts) return prev;
      
      const updated = { ...prev };
      if (updated.social_posts.platforms[platform] && 
          updated.social_posts.platforms[platform][index]) {
        updated.social_posts.platforms[platform][index].content = newContent;
        updated.social_posts.platforms[platform][index].character_count = newContent.length;
        const platformObj = platforms.find(p => p.id === platform);
        if (platformObj) {
          updated.social_posts.platforms[platform][index].within_limit = 
            newContent.length <= platformObj.charLimit;
        }
      }
      return updated;
    });
  };

  const selectedPlatformCount = platforms.filter(p => p.selected).length;

  return (
    <div className="space-y-6">
      {/* Platform Selection */}
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Select Platforms</h3>
        <PlatformSelector 
          platforms={platforms} 
          onPlatformToggle={handlePlatformToggle} 
        />
        <p className="text-sm text-gray-400 mt-3">
          {selectedPlatformCount} platform{selectedPlatformCount !== 1 ? 's' : ''} selected
        </p>
      </Card>

      {/* Generation Options */}
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Content Options</h3>
        
        <div className="space-y-4">
          {/* Topic Input */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Topic or Content Brief *
            </label>
            <textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Enter your topic or describe what you want to post about..."
              className="w-full px-4 py-3 bg-dark-800 border border-dark-700 rounded-lg 
                       text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500 
                       focus:border-primary-500 transition-all"
              rows={3}
            />
          </div>

          {/* Tone Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Tone
            </label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value as SocialGenerationRequest['tone'])}
              className="w-full px-4 py-3 bg-dark-800 border border-dark-700 rounded-lg 
                       text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="technical">Technical</option>
              <option value="marketing">Marketing</option>
              <option value="humorous">Humorous</option>
              <option value="inspirational">Inspirational</option>
              <option value="educational">Educational</option>
            </select>
          </div>

          {/* Variations Slider */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Variations per Platform: {variations}
            </label>
            <input
              type="range"
              min="1"
              max="5"
              value={variations}
              onChange={(e) => setVariations(Number(e.target.value))}
              className="w-full accent-primary-500"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>1</span>
              <span>2</span>
              <span>3</span>
              <span>4</span>
              <span>5</span>
            </div>
          </div>

          {/* Options Row */}
          <div className="flex flex-wrap gap-4">
            <label className="flex items-center gap-2 text-gray-300">
              <input
                type="checkbox"
                checked={includeHashtags}
                onChange={(e) => setIncludeHashtags(e.target.checked)}
                className="rounded bg-dark-800 border-dark-600 text-primary-500 
                         focus:ring-primary-500 focus:ring-2"
              />
              <span className="text-sm">Include Hashtags</span>
            </label>
            
            <label className="flex items-center gap-2 text-gray-300">
              <input
                type="checkbox"
                checked={includeEmojis}
                onChange={(e) => setIncludeEmojis(e.target.checked)}
                className="rounded bg-dark-800 border-dark-600 text-primary-500 
                         focus:ring-primary-500 focus:ring-2"
              />
              <span className="text-sm">Include Emojis</span>
            </label>
          </div>

          {/* Advanced Options */}
          <details className="border-t border-dark-700 pt-4">
            <summary className="cursor-pointer text-sm font-medium text-gray-300 mb-3 hover:text-white transition-colors">
              Advanced Options
            </summary>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Target Audience
                </label>
                <input
                  type="text"
                  value={targetAudience}
                  onChange={(e) => setTargetAudience(e.target.value)}
                  placeholder="e.g., marketers, developers, entrepreneurs"
                  className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-lg 
                           text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Call to Action
                </label>
                <input
                  type="text"
                  value={cta}
                  onChange={(e) => setCta(e.target.value)}
                  placeholder="e.g., Visit our website, Sign up today"
                  className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-lg 
                           text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>
          </details>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-3 bg-red-900/20 border border-red-500/50 text-red-400 rounded-lg">
            {error}
          </div>
        )}

        {/* Generate Button */}
        <Button
          onClick={handleGenerate}
          disabled={isGenerating || selectedPlatformCount === 0}
          variant="primary"
          className="mt-6 w-full"
        >
          {isGenerating ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
              <span>Generating...</span>
            </>
          ) : (
            <>
              <SparklesIcon className="w-5 h-5" />
              <span>Generate Social Posts</span>
            </>
          )}
        </Button>
      </Card>

      {/* Generated Posts */}
      {generatedPosts && generatedPosts.social_posts && (
        <Card>
          <h3 className="text-lg font-semibold text-white mb-4">Generated Posts</h3>
          
          {/* Platform Tabs */}
          <div className="border-b border-dark-700 mb-4">
            <div className="flex gap-2 overflow-x-auto">
              {Object.keys(generatedPosts.social_posts.platforms).map(platformId => {
                const platform = platforms.find(p => p.id === platformId);
                if (!platform) return null;
                
                return (
                  <button
                    key={platformId}
                    onClick={() => setActiveTab(platformId)}
                    className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                      activeTab === platformId
                        ? 'border-primary-500 text-primary-400'
                        : 'border-transparent text-gray-400 hover:text-gray-200'
                    }`}
                  >
                    <span className="text-lg">{platform.icon}</span>
                    <span>{platform.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Post Cards */}
          {activeTab && generatedPosts.social_posts.platforms[activeTab] && (
            <div className="space-y-4">
              {generatedPosts.social_posts.platforms[activeTab].map((post, index) => {
                const platform = platforms.find(p => p.id === activeTab);
                if (!platform) return null;
                
                return (
                  <SocialPostCard
                    key={`${activeTab}-${index}`}
                    platform={platform}
                    content={post.content}
                    hashtags={post.hashtags}
                    index={index}
                    onEdit={(newContent) => handleEditPost(activeTab, index, newContent)}
                    onSave={() => handleSavePost(activeTab, post.content, index)}
                  />
                );
              })}
            </div>
          )}
        </Card>
      )}
    </div>
  );
};

export default SocialMediaGenerator;