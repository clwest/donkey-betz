import React, { useState } from 'react';
import type { Platform } from './types';
import { ClipboardDocumentIcon, PencilIcon, BookmarkIcon, CheckIcon } from '@heroicons/react/24/outline';

interface SocialPostCardProps {
  platform: Platform;
  content: string;
  hashtags?: string[];
  index: number;
  onEdit?: (content: string) => void;
  onSave?: () => void;
}

const SocialPostCard: React.FC<SocialPostCardProps> = ({ 
  platform, 
  content, 
  hashtags = [], 
  index,
  onEdit,
  onSave
}) => {
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(content);

  const characterCount = editedContent.length;
  const isOverLimit = characterCount > platform.charLimit;
  const percentUsed = Math.min((characterCount / platform.charLimit) * 100, 100);

  const copyToClipboard = async () => {
    const fullContent = hashtags.length > 0 
      ? `${editedContent}\n\n${hashtags.join(' ')}`
      : editedContent;
    
    await navigator.clipboard.writeText(fullContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSave = () => {
    if (onEdit && editedContent !== content) {
      onEdit(editedContent);
    }
    setIsEditing(false);
  };

  const getPlatformGradient = (platformId: string) => {
    switch(platformId) {
      case 'twitter': return 'from-blue-500/20 to-blue-600/20';
      case 'linkedin': return 'from-blue-600/20 to-blue-700/20';
      case 'instagram': return 'from-purple-500/20 to-pink-500/20';
      case 'facebook': return 'from-blue-500/20 to-blue-600/20';
      case 'tiktok': return 'from-gray-600/20 to-gray-700/20';
      default: return 'from-gray-600/20 to-gray-700/20';
    }
  };

  return (
    <div className={`relative glass rounded-xl p-5 transition-all hover:bg-white/10 bg-gradient-to-br ${getPlatformGradient(platform.id)}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{platform.icon}</span>
          <div>
            <span className="font-medium text-foreground">{platform.name}</span>
            <span className="ml-2 text-xs text-muted-foreground">
              Variation {index + 1}
            </span>
          </div>
        </div>
        
        {/* Character Count */}
        <div className="text-right">
          <div className={`text-sm font-medium ${isOverLimit ? 'text-red-500' : 'text-muted-foreground'}`}>
            {characterCount.toLocaleString()} / {platform.charLimit.toLocaleString()}
          </div>
          {/* Progress Bar */}
          <div className="w-24 h-1 bg-dark-700 rounded-full mt-1 overflow-hidden">
            <div 
              className={`h-full transition-all ${
                isOverLimit ? 'bg-red-500' : percentUsed > 80 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${percentUsed}%` }}
            />
          </div>
        </div>
      </div>

      {/* Content */}
      {isEditing ? (
        <div className="mb-4">
          <textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            className={`w-full p-3 bg-card/50 border rounded-lg resize-none text-foreground 
                     placeholder-gray-500 focus:ring-2 focus:ring-primary-500 ${
              isOverLimit ? 'border-red-500/50' : 'border-dark-600'
            }`}
            rows={6}
          />
        </div>
      ) : (
        <p className="mb-4 text-foreground whitespace-pre-wrap leading-relaxed">
          {editedContent}
        </p>
      )}

      {/* Hashtags */}
      {hashtags.length > 0 && (
        <div className="mb-4 flex flex-wrap gap-2">
          {hashtags.slice(0, platform.hashtagLimit).map((tag, idx) => (
            <span
              key={idx}
              className="text-xs bg-primary-500/20 text-primary-300 px-2.5 py-1 rounded-full 
                       border border-primary-500/30"
            >
              {tag}
            </span>
          ))}
          {hashtags.length > platform.hashtagLimit && (
            <span className="text-xs text-muted-foreground">
              +{hashtags.length - platform.hashtagLimit} more
            </span>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2">
        <button
          onClick={copyToClipboard}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 
                   bg-card/50 hover:bg-dark-700/50 text-muted-foreground hover:text-foreground 
                   rounded-lg transition-all border border-dark-600"
        >
          {copied ? (
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

        {isEditing ? (
          <button
            onClick={handleSave}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 
                     bg-gradient-to-r from-primary-500 to-primary-600 text-foreground 
                     rounded-lg hover:shadow-lg hover:shadow-primary-500/25 transition-all"
          >
            <CheckIcon className="w-4 h-4" />
            <span className="text-sm">Save Edit</span>
          </button>
        ) : (
          <button
            onClick={() => setIsEditing(true)}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 
                     bg-card/50 hover:bg-dark-700/50 text-muted-foreground hover:text-foreground 
                     rounded-lg transition-all border border-dark-600"
          >
            <PencilIcon className="w-4 h-4" />
            <span className="text-sm">Edit</span>
          </button>
        )}

        {onSave && (
          <button
            onClick={onSave}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 
                     bg-card/50 hover:bg-dark-700/50 text-muted-foreground hover:text-foreground 
                     rounded-lg transition-all border border-dark-600"
          >
            <BookmarkIcon className="w-4 h-4" />
            <span className="text-sm">Save</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default SocialPostCard;