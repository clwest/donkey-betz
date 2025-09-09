import { useState } from 'react';
import { 
  HeartIcon,
  StarIcon,
  BookmarkIcon,
  HandThumbUpIcon,
  ArrowPathIcon,
  DocumentDuplicateIcon,
  ShareIcon,
  EyeIcon,
} from '@heroicons/react/24/outline';
import { 
  HeartIcon as HeartIconSolid,
  StarIcon as StarIconSolid,
  BookmarkIcon as BookmarkIconSolid,
} from '@heroicons/react/24/solid';
import { Button } from './Button';
import { useStyleMemoryStore } from '../../store/styleMemoryStore';
import clsx from 'clsx';

interface GeneratedImageProps {
  id: string;
  src: string;
  alt?: string;
  prompt?: string;
  parameters?: {
    cfg_scale?: number;
    steps?: number;
    model?: string;
    style?: string;
    size?: string;
  };
  className?: string;
  showStyleControls?: boolean;
  parentId?: string; // For tracking variations
}

export function GeneratedImage({ 
  id, 
  src, 
  alt = 'Generated image', 
  prompt,
  parameters = {},
  className,
  showStyleControls = true,
  parentId,
}: GeneratedImageProps) {
  const [rating, setRating] = useState(0);
  const [isLoved, setIsLoved] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [showControls, setShowControls] = useState(false);
  
  const { 
    captureInteraction, 
    generateSimilar, 
    viewLineage,
    isLoading,
  } = useStyleMemoryStore();

  const handleLove = async () => {
    if (!isLoved) {
      await captureInteraction(id, 'love', parentId);
      setIsLoved(true);
    }
  };

  const handleRate = async (stars: number) => {
    if (rating !== stars) {
      await captureInteraction(id, `rate_${stars}` as any, parentId);
      setRating(stars);
    }
  };

  const handleSave = async () => {
    if (!isSaved) {
      await captureInteraction(id, 'save', parentId);
      setIsSaved(true);
    }
  };

  const handleLike = async () => {
    if (!isLiked) {
      await captureInteraction(id, 'like', parentId);
      setIsLiked(true);
    }
  };

  const handleGenerateSimilar = async (variationType: 'subtle' | 'moderate' | 'creative') => {
    try {
      const result = await generateSimilar(id, variationType);
      // The parent component should handle displaying the new image
      // For now, we'll just capture the interaction
      await captureInteraction(id, 'generate_similar', parentId);
    } catch (error) {
      console.error('Generate similar failed:', error);
    }
  };

  const handleViewLineage = async () => {
    await viewLineage(id);
  };

  const handleCopyPrompt = () => {
    if (prompt) {
      navigator.clipboard.writeText(prompt);
    }
  };

  return (
    <div 
      className={clsx(
        'relative group rounded-lg overflow-hidden bg-dark-900 border border-dark-700',
        className
      )}
      onMouseEnter={() => setShowControls(true)}
      onMouseLeave={() => setShowControls(false)}
    >
      {/* Main Image */}
      <img 
        src={src} 
        alt={alt}
        className="w-full h-auto object-cover"
      />

      {/* Overlay Controls */}
      {showStyleControls && (
        <div className={clsx(
          'absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity duration-200',
          showControls ? 'opacity-100' : 'opacity-0 pointer-events-none'
        )}>
          {/* Top Row - Quick Actions */}
          <div className="absolute top-2 left-2 right-2 flex justify-between">
            <div className="flex gap-1">
              {/* Love Button */}
              <button
                onClick={handleLove}
                className={clsx(
                  'p-2 rounded-full backdrop-blur-xl transition-all duration-200 hover:scale-110',
                  isLoved 
                    ? 'bg-red-500/20 text-red-400 border border-red-500/50' 
                    : 'bg-white/10 text-white hover:bg-red-500/20 hover:text-red-400'
                )}
                title="❤️ Love this style"
              >
                {isLoved ? <HeartIconSolid className="h-5 w-5" /> : <HeartIcon className="h-5 w-5" />}
              </button>

              {/* Save Button */}
              <button
                onClick={handleSave}
                className={clsx(
                  'p-2 rounded-full backdrop-blur-xl transition-all duration-200 hover:scale-110',
                  isSaved 
                    ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50' 
                    : 'bg-white/10 text-white hover:bg-blue-500/20 hover:text-blue-400'
                )}
                title="💾 Save for later"
              >
                {isSaved ? <BookmarkIconSolid className="h-5 w-5" /> : <BookmarkIcon className="h-5 w-5" />}
              </button>

              {/* Like Button */}
              <button
                onClick={handleLike}
                className={clsx(
                  'p-2 rounded-full backdrop-blur-xl transition-all duration-200 hover:scale-110',
                  isLiked 
                    ? 'bg-green-500/20 text-green-400 border border-green-500/50' 
                    : 'bg-white/10 text-white hover:bg-green-500/20 hover:text-green-400'
                )}
                title="👍 Like this"
              >
                <HandThumbUpIcon className="h-5 w-5" />
              </button>
            </div>

            {/* View Lineage */}
            <button
              onClick={handleViewLineage}
              className="p-2 rounded-full bg-white/10 text-white hover:bg-primary-500/20 hover:text-primary-400 transition-all duration-200 hover:scale-110"
              title="🌳 View style lineage"
            >
              <EyeIcon className="h-5 w-5" />
            </button>
          </div>

          {/* Star Rating */}
          <div className="absolute top-12 left-2 flex gap-1">
            {[1, 2, 3, 4, 5].map((stars) => (
              <button
                key={stars}
                onClick={() => handleRate(stars)}
                className={clsx(
                  'p-1 rounded transition-all duration-200 hover:scale-110',
                  rating >= stars 
                    ? 'text-yellow-400' 
                    : 'text-gray-400 hover:text-yellow-300'
                )}
                title={`⭐ Rate ${stars} star${stars > 1 ? 's' : ''}`}
              >
                {rating >= stars ? <StarIconSolid className="h-4 w-4" /> : <StarIcon className="h-4 w-4" />}
              </button>
            ))}
          </div>

          {/* Bottom Row - Generation Controls */}
          <div className="absolute bottom-2 left-2 right-2">
            <div className="flex gap-1 mb-2">
              {/* Generate Similar Buttons */}
              <Button
                size="sm"
                variant="secondary"
                onClick={() => handleGenerateSimilar('subtle')}
                loading={isLoading}
                className="text-xs"
              >
                <ArrowPathIcon className="h-3 w-3" />
                Subtle
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => handleGenerateSimilar('moderate')}
                loading={isLoading}
                className="text-xs"
              >
                <ArrowPathIcon className="h-3 w-3" />
                Similar
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => handleGenerateSimilar('creative')}
                loading={isLoading}
                className="text-xs"
              >
                <ArrowPathIcon className="h-3 w-3" />
                Creative
              </Button>
            </div>

            {/* Utility Buttons */}
            <div className="flex gap-1">
              <Button
                size="sm"
                variant="ghost"
                onClick={handleCopyPrompt}
                className="text-xs flex-1"
              >
                <DocumentDuplicateIcon className="h-3 w-3" />
                Copy Prompt
              </Button>
              <Button
                size="sm"
                variant="ghost"
                className="text-xs"
              >
                <ShareIcon className="h-3 w-3" />
                Share
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Image Info */}
      {(prompt || Object.keys(parameters).length > 0) && (
        <div className="p-3 bg-dark-800/50 backdrop-blur-xl">
          {prompt && (
            <p className="text-sm text-gray-300 mb-2 line-clamp-2">{prompt}</p>
          )}
          {Object.keys(parameters).length > 0 && (
            <div className="flex flex-wrap gap-2 text-xs text-gray-400">
              {parameters.style && <span className="px-2 py-1 bg-primary-500/20 rounded-full">{parameters.style}</span>}
              {parameters.cfg_scale && <span>CFG: {parameters.cfg_scale}</span>}
              {parameters.steps && <span>Steps: {parameters.steps}</span>}
              {parameters.size && <span>{parameters.size}</span>}
            </div>
          )}
        </div>
      )}
    </div>
  );
}