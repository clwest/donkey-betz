import React, { useState, useEffect } from 'react';
import { Button } from '../../common/Button';
import { 
  XMarkIcon, 
  ArrowDownTrayIcon, 
  DocumentDuplicateIcon,
  TrashIcon,
  InformationCircleIcon,
  MagnifyingGlassPlusIcon,
  MagnifyingGlassMinusIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  HeartIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolid } from '@heroicons/react/24/solid';
import { toast } from 'sonner';
import { contentService } from '../../../services/content.service';
import { FeedbackWidget } from '../../feedback/FeedbackWidget';

interface ImageViewerProps {
  image: {
    id: string;
    url?: string;
    image_url?: string;
    title?: string;
    prompt?: string;
    metadata?: any;
    tags?: string[];
    saved_at?: string;
    created_at?: string;
  };
  images?: any[]; // Array of all images for navigation
  currentIndex?: number;
  isOpen: boolean;
  onClose: () => void;
  onDelete?: (id: string) => void;
  onFavorite?: (id: string) => void;
  onGenerateSimilar?: (prompt: string, style: string) => void;
}

export function ImageViewer({ 
  image, 
  images = [], 
  currentIndex = 0,
  isOpen, 
  onClose,
  onDelete,
  onFavorite,
  onGenerateSimilar
}: ImageViewerProps) {
  const [scale, setScale] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showInfo, setShowInfo] = useState(false);
  const [isFavorited, setIsFavorited] = useState(false);
  const [activeImageIndex, setActiveImageIndex] = useState(currentIndex);

  const activeImage = images.length > 0 ? images[activeImageIndex] : image;
  const imageUrl = activeImage.url || activeImage.image_url || activeImage.result;

  useEffect(() => {
    setActiveImageIndex(currentIndex);
  }, [currentIndex]);

  const handleDownload = async () => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${activeImage.title || 'image'}-${activeImage.id}.png`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('Image downloaded!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download image');
    }
  };

  const handleCopyPrompt = () => {
    if (activeImage.prompt) {
      navigator.clipboard.writeText(activeImage.prompt);
      toast.success('Prompt copied to clipboard!');
    }
  };

  const handleDelete = () => {
    if (onDelete && window.confirm('Are you sure you want to delete this image?')) {
      onDelete(activeImage.id);
      toast.success('Image deleted');
      onClose();
    }
  };

  const handleFavorite = () => {
    setIsFavorited(!isFavorited);
    if (onFavorite) {
      onFavorite(activeImage.id);
    }
    toast.success(isFavorited ? 'Removed from favorites' : 'Added to favorites!');
  };

  const handleGenerateSimilar = () => {
    if (onGenerateSimilar && activeImage.prompt) {
      const style = activeImage.metadata?.style || 'photorealistic';
      onGenerateSimilar(activeImage.prompt, style);
      toast.success('Generating similar image...');
      onClose();
    }
  };

  const handleZoomIn = () => {
    setScale(prev => Math.min(prev + 0.25, 3));
  };

  const handleZoomOut = () => {
    setScale(prev => Math.max(prev - 0.25, 0.5));
  };

  const handleResetZoom = () => {
    setScale(1);
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const navigatePrevious = () => {
    if (images.length > 0 && activeImageIndex > 0) {
      setActiveImageIndex(activeImageIndex - 1);
      setScale(1);
    }
  };

  const navigateNext = () => {
    if (images.length > 0 && activeImageIndex < images.length - 1) {
      setActiveImageIndex(activeImageIndex + 1);
      setScale(1);
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      
      switch(e.key) {
        case 'ArrowLeft':
          navigatePrevious();
          break;
        case 'ArrowRight':
          navigateNext();
          break;
        case 'Escape':
          onClose();
          break;
        case '+':
        case '=':
          handleZoomIn();
          break;
        case '-':
          handleZoomOut();
          break;
        case '0':
          handleResetZoom();
          break;
        case 'f':
          toggleFullscreen();
          break;
        case 'd':
          handleDownload();
          break;
        case 'c':
          handleCopyPrompt();
          break;
        case 'i':
          setShowInfo(!showInfo);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, activeImageIndex, showInfo]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal Content */}
      <div className="relative flex flex-col h-full bg-dark-900">
        {/* Header Toolbar */}
        <div className="flex items-center justify-between p-4 border-b border-dark-700">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold text-white">
              {activeImage.title || activeImage.prompt?.substring(0, 50) || 'Generated Image'}
            </h2>
            {images.length > 1 && (
              <span className="text-sm text-gray-400">
                {activeImageIndex + 1} / {images.length}
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            {/* Zoom Controls */}
            <div className="flex items-center gap-1 px-2 py-1 bg-dark-800 rounded-lg">
              <button
                onClick={handleZoomOut}
                className="p-1 text-gray-400 hover:text-white transition-colors"
                title="Zoom Out (-)"
              >
                <MagnifyingGlassMinusIcon className="h-4 w-4" />
              </button>
              <span className="text-sm text-gray-400 min-w-[3rem] text-center">
                {Math.round(scale * 100)}%
              </span>
              <button
                onClick={handleZoomIn}
                className="p-1 text-gray-400 hover:text-white transition-colors"
                title="Zoom In (+)"
              >
                <MagnifyingGlassPlusIcon className="h-4 w-4" />
              </button>
            </div>

            {/* Action Buttons */}
            <button
              onClick={handleFavorite}
              className={`p-2 transition-colors ${
                isFavorited ? 'text-red-500' : 'text-gray-400 hover:text-red-400'
              }`}
              title="Favorite"
            >
              {isFavorited ? <HeartSolid className="h-5 w-5" /> : <HeartIcon className="h-5 w-5" />}
            </button>

            <button
              onClick={() => setShowInfo(!showInfo)}
              className={`p-2 transition-colors ${
                showInfo ? 'text-primary-400' : 'text-gray-400 hover:text-white'
              }`}
              title="Toggle Info (I)"
            >
              <InformationCircleIcon className="h-5 w-5" />
            </button>

            <button
              onClick={handleCopyPrompt}
              className="p-2 text-gray-400 hover:text-white transition-colors"
              title="Copy Prompt (C)"
            >
              <DocumentDuplicateIcon className="h-5 w-5" />
            </button>

            <button
              onClick={handleDownload}
              className="p-2 text-gray-400 hover:text-white transition-colors"
              title="Download (D)"
            >
              <ArrowDownTrayIcon className="h-5 w-5" />
            </button>

            {onGenerateSimilar && (
              <button
                onClick={handleGenerateSimilar}
                className="p-2 text-gray-400 hover:text-primary-400 transition-colors"
                title="Generate Similar"
              >
                <SparklesIcon className="h-5 w-5" />
              </button>
            )}

            <button
              onClick={toggleFullscreen}
              className="p-2 text-gray-400 hover:text-white transition-colors"
              title="Fullscreen (F)"
            >
              {isFullscreen ? (
                <ArrowsPointingInIcon className="h-5 w-5" />
              ) : (
                <ArrowsPointingOutIcon className="h-5 w-5" />
              )}
            </button>

            {onDelete && (
              <button
                onClick={handleDelete}
                className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                title="Delete"
              >
                <TrashIcon className="h-5 w-5" />
              </button>
            )}

            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white transition-colors ml-2"
              title="Close (Esc)"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex relative overflow-hidden">
          {/* Navigation Arrows */}
          {images.length > 1 && (
            <>
              <button
                onClick={navigatePrevious}
                disabled={activeImageIndex === 0}
                className={`absolute left-4 top-1/2 -translate-y-1/2 z-10 p-3 bg-dark-800/80 rounded-full transition-all ${
                  activeImageIndex === 0 
                    ? 'opacity-30 cursor-not-allowed' 
                    : 'hover:bg-dark-700 hover:scale-110'
                }`}
                title="Previous (←)"
              >
                <ChevronLeftIcon className="h-6 w-6 text-white" />
              </button>
              
              <button
                onClick={navigateNext}
                disabled={activeImageIndex === images.length - 1}
                className={`absolute right-4 top-1/2 -translate-y-1/2 z-10 p-3 bg-dark-800/80 rounded-full transition-all ${
                  activeImageIndex === images.length - 1 
                    ? 'opacity-30 cursor-not-allowed' 
                    : 'hover:bg-dark-700 hover:scale-110'
                }`}
                title="Next (→)"
              >
                <ChevronRightIcon className="h-6 w-6 text-white" />
              </button>
            </>
          )}

          {/* Image Display */}
          <div className="flex-1 flex items-center justify-center p-8">
            <div 
              className="relative max-w-full max-h-full overflow-auto"
              style={{ cursor: scale > 1 ? 'move' : 'default' }}
            >
              <img
                src={imageUrl}
                alt={activeImage.title || 'Generated image'}
                className="max-w-full h-auto"
                style={{
                  transform: `scale(${scale})`,
                  transformOrigin: 'center',
                  transition: 'transform 0.2s ease-in-out'
                }}
                onDoubleClick={() => setScale(scale === 1 ? 2 : 1)}
              />
            </div>
          </div>

          {/* Info Panel */}
          {showInfo && (
            <div className="w-80 bg-dark-800 border-l border-dark-700 p-4 overflow-y-auto">
              <h3 className="text-lg font-semibold text-white mb-4">Image Information</h3>
              
              <div className="space-y-4">
                {activeImage.prompt && (
                  <div>
                    <label className="text-sm text-gray-400">Prompt</label>
                    <p className="text-sm text-gray-200 mt-1">{activeImage.prompt}</p>
                  </div>
                )}

                {activeImage.metadata && (
                  <>
                    {activeImage.metadata.style && (
                      <div>
                        <label className="text-sm text-gray-400">Style</label>
                        <p className="text-sm text-gray-200 mt-1 capitalize">{activeImage.metadata.style}</p>
                      </div>
                    )}

                    {activeImage.metadata.model && (
                      <div>
                        <label className="text-sm text-gray-400">Model</label>
                        <p className="text-sm text-gray-200 mt-1">{activeImage.metadata.model}</p>
                      </div>
                    )}

                    {(activeImage.metadata.width && activeImage.metadata.height) && (
                      <div>
                        <label className="text-sm text-gray-400">Resolution</label>
                        <p className="text-sm text-gray-200 mt-1">
                          {activeImage.metadata.width} × {activeImage.metadata.height}
                        </p>
                      </div>
                    )}

                    {activeImage.metadata.cfg_scale && (
                      <div>
                        <label className="text-sm text-gray-400">CFG Scale</label>
                        <p className="text-sm text-gray-200 mt-1">{activeImage.metadata.cfg_scale}</p>
                      </div>
                    )}

                    {activeImage.metadata.steps && (
                      <div>
                        <label className="text-sm text-gray-400">Steps</label>
                        <p className="text-sm text-gray-200 mt-1">{activeImage.metadata.steps}</p>
                      </div>
                    )}

                    {activeImage.metadata.seed && (
                      <div>
                        <label className="text-sm text-gray-400">Seed</label>
                        <p className="text-sm text-gray-200 mt-1 font-mono text-xs">{activeImage.metadata.seed}</p>
                      </div>
                    )}

                    {activeImage.metadata.negative_prompt && (
                      <div>
                        <label className="text-sm text-gray-400">Negative Prompt</label>
                        <p className="text-sm text-gray-200 mt-1">{activeImage.metadata.negative_prompt}</p>
                      </div>
                    )}
                  </>
                )}

                {activeImage.tags && activeImage.tags.length > 0 && (
                  <div>
                    <label className="text-sm text-gray-400">Tags</label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {activeImage.tags.map((tag: string, index: number) => (
                        <span
                          key={index}
                          className="px-2 py-1 text-xs bg-dark-700 text-gray-300 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {(activeImage.saved_at || activeImage.created_at) && (
                  <div>
                    <label className="text-sm text-gray-400">Created</label>
                    <p className="text-sm text-gray-200 mt-1">
                      {new Date(activeImage.saved_at || activeImage.created_at).toLocaleString()}
                    </p>
                  </div>
                )}

                {activeImage.id && (
                  <div>
                    <label className="text-sm text-gray-400">ID</label>
                    <p className="text-sm text-gray-200 mt-1 font-mono">{activeImage.id}</p>
                  </div>
                )}
              </div>

              {/* Feedback Section */}
              <div className="mt-6 pt-4 border-t border-dark-700">
                <FeedbackWidget
                  contentType="image"
                  contentId={parseInt(activeImage.id)}
                  contentTitle={activeImage.title || activeImage.prompt?.substring(0, 50) || 'Generated Image'}
                  inline={true}
                  showStats={true}
                />
              </div>

              {/* Keyboard Shortcuts */}
              <div className="mt-6 pt-4 border-t border-dark-700">
                <h4 className="text-sm font-semibold text-gray-400 mb-2">Keyboard Shortcuts</h4>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Navigate</span>
                    <span className="text-gray-400">← →</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Zoom</span>
                    <span className="text-gray-400">+ / - / 0</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Download</span>
                    <span className="text-gray-400">D</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Copy Prompt</span>
                    <span className="text-gray-400">C</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Toggle Info</span>
                    <span className="text-gray-400">I</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Fullscreen</span>
                    <span className="text-gray-400">F</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Close</span>
                    <span className="text-gray-400">Esc</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Thumbnail Strip (for multiple images) */}
        {images.length > 1 && (
          <div className="border-t border-dark-700 p-4">
            <div className="flex gap-2 overflow-x-auto">
              {images.map((img, index) => {
                const thumbUrl = img.url || img.image_url || img.result;
                return (
                  <button
                    key={img.id || index}
                    onClick={() => {
                      setActiveImageIndex(index);
                      setScale(1);
                    }}
                    className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-all ${
                      index === activeImageIndex
                        ? 'border-primary-500 scale-110'
                        : 'border-dark-700 hover:border-dark-600'
                    }`}
                  >
                    <img
                      src={thumbUrl}
                      alt={`Thumbnail ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}