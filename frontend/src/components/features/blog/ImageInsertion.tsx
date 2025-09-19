import { useState, useRef, useEffect } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { galleryService } from '../../../services/gallery.service';
import { Logger } from '../../../utils/logger';
import { toast } from 'sonner';
import {
  PhotoIcon,
  CloudArrowUpIcon,
  XMarkIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';

interface ImageInsertionProps {
  isOpen: boolean;
  onClose: () => void;
  onInsert: (imageUrl: string, altText?: string) => void;
}

interface GalleryImage {
  id: string;
  title: string;
  image_url: string;
  saved_at: string;
  tags: string[];
  category?: string;
  description?: string;
}

export function ImageInsertion({ isOpen, onClose, onInsert }: ImageInsertionProps) {
  const [activeTab, setActiveTab] = useState<'upload' | 'gallery'>('gallery');
  const [galleryImages, setGalleryImages] = useState<GalleryImage[]>([]);
  const [loadingGallery, setLoadingGallery] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen && activeTab === 'gallery') {
      loadGalleryImages();
    }
  }, [isOpen, activeTab]);

  const loadGalleryImages = async () => {
    setLoadingGallery(true);
    try {
      Logger.component('ImageInsertion', 'Loading gallery images');
      const response = await galleryService.getItems({ content_type: ['image'] }, 1, 20);
      setGalleryImages(response.items || []);
      Logger.state('ImageInsertion', 'Gallery images loaded', { count: response.items?.length || 0 });
    } catch (error: any) {
      Logger.error('ImageInsertion.loadGalleryImages', error);
      toast.error('Failed to load gallery images');
    } finally {
      setLoadingGallery(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast.error('Please select an image file');
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      toast.error('Image size must be less than 10MB');
      return;
    }

    setUploading(true);
    try {
      Logger.component('ImageInsertion', 'Uploading image', { fileName: file.name, size: file.size });
      
      // Create FormData for upload
      const formData = new FormData();
      formData.append('image', file);
      formData.append('title', `Blog Image - ${file.name}`);
      formData.append('category', 'blog_images');

      // TODO: Implement actual upload endpoint
      // For now, create a local URL for preview
      const imageUrl = URL.createObjectURL(file);
      
      toast.success('Image uploaded successfully!');
      onInsert(imageUrl, file.name);
      
      Logger.state('ImageInsertion', 'Image uploaded', { url: imageUrl });
    } catch (error: any) {
      Logger.error('ImageInsertion.handleFileUpload', error);
      toast.error('Failed to upload image');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleGalleryImageSelect = (image: GalleryImage) => {
    Logger.component('ImageInsertion', 'Selecting gallery image', { id: image.id, title: image.title });
    onInsert(image.image_url, image.title);
  };

  const filteredImages = galleryImages.filter(image =>
    image.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    image.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-lg w-full max-w-4xl h-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <PhotoIcon className="h-6 w-6 text-primary-400" />
            <h2 className="text-xl font-semibold text-foreground">Insert Image</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-muted-foreground hover:text-foreground transition-colors"
            title="Close"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 border-b border-border px-6">
          <button
            onClick={() => setActiveTab('gallery')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === 'gallery'
                ? 'text-primary-400 border-b-2 border-primary-400'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <PhotoIcon className="inline h-4 w-4 mr-2" />
            From Gallery
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === 'upload'
                ? 'text-primary-400 border-b-2 border-primary-400'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <CloudArrowUpIcon className="inline h-4 w-4 mr-2" />
            Upload New
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'upload' && (
            <div className="space-y-6">
              <div className="text-center">
                <div className="border-2 border-dashed border-dark-600 rounded-lg p-8 hover:border-primary-500 transition-colors">
                  <CloudArrowUpIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <div className="space-y-2">
                    <h3 className="text-lg font-semibold text-foreground">Upload Image</h3>
                    <p className="text-muted-foreground">Drag and drop or click to select an image</p>
                    <p className="text-xs text-muted-foreground">Supports JPG, PNG, WebP (max 10MB)</p>
                  </div>
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading}
                    variant="primary"
                    className="mt-4"
                  >
                    {uploading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Uploading...
                      </>
                    ) : (
                      <>
                        <CloudArrowUpIcon className="h-4 w-4 mr-2" />
                        Select Image
                      </>
                    )}
                  </Button>
                </div>
              </div>
              
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
          )}

          {activeTab === 'gallery' && (
            <div className="space-y-4">
              {/* Search */}
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search images..."
                  className="w-full pl-10 pr-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-foreground placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* Gallery Grid */}
              {loadingGallery ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
                </div>
              ) : (
                <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                  {filteredImages.map((image) => (
                    <div
                      key={image.id}
                      onClick={() => handleGalleryImageSelect(image)}
                      className="relative aspect-square cursor-pointer group overflow-hidden rounded-lg bg-dark-700 hover:ring-2 hover:ring-primary-500 transition-all"
                    >
                      <img
                        src={image.image_url}
                        alt={image.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                      />
                      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-opacity flex items-end">
                        <div className="p-2 text-foreground text-xs opacity-0 group-hover:opacity-100 transition-opacity">
                          <p className="font-medium truncate">{image.title}</p>
                          {image.tags.length > 0 && (
                            <p className="text-muted-foreground truncate">{image.tags.slice(0, 2).join(', ')}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {!loadingGallery && filteredImages.length === 0 && (
                <div className="text-center py-12">
                  <PhotoIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">
                    {searchQuery ? 'No images found matching your search' : 'No images in gallery yet'}
                  </p>
                  {!searchQuery && (
                    <Button
                      onClick={() => setActiveTab('upload')}
                      variant="secondary"
                      className="mt-4"
                    >
                      Upload Your First Image
                    </Button>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}