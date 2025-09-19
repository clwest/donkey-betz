import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { GeneratedImage } from '../../common/GeneratedImage';
import { 
  PhotoIcon,
  AdjustmentsHorizontalIcon,
  ArrowPathIcon,
  RectangleStackIcon,
  CloudArrowUpIcon,
  XMarkIcon,
  RectangleGroupIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline';
import { contentService } from '../../../services/content.service';
import { stylesService, type VisualStyle } from '../../../services/styles.service';
import { apiClient } from '../../../services/api.config';
import { API_CONFIG, buildApiUrl } from '../../../config/api.config';
import { useStyleMemoryStore } from '../../../store/styleMemoryStore';
import { promptingService } from '../../../services/promptingService';
import { toast } from 'sonner';
import { Logger } from '../../../utils/logger';

interface ImageGenerationParams {
  prompt: string;
  style: string;
  cfg_scale: number;
  steps: number;
  width: number;
  height: number;
  model: string;
  negative_prompt: string;
  seed?: number;
  batch_size: number;
}

interface GeneratedImageData {
  id: string;
  url: string;
  prompt: string;
  parameters: any;
}

export function ImageGenerator() {
  const [availableStyles, setAvailableStyles] = useState<VisualStyle[]>([]);
  const [stylesLoading, setStylesLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  
  useEffect(() => {
    Logger.component('ImageGenerator', 'Mounting');
    loadStyles();
    loadPromptingSettings();
    return () => {
      Logger.component('ImageGenerator', 'Unmounting');
    };
  }, []);
  
  const loadPromptingSettings = async () => {
    try {
      const settings = await promptingService.getSettings();
      setEnhancePrompt(settings.enabled);
      setEnhancementLevel(settings.default_level);
      setUseMemory(settings.use_memory);
    } catch (error) {
      console.error('Failed to load prompting settings:', error);
    }
  };
  
  const loadStyles = async () => {
    try {
      setStylesLoading(true);
      const styles = await stylesService.getAllStyles();
      console.log('Loaded styles:', styles); // Debug log
      setAvailableStyles(styles);
      Logger.state('ImageGenerator', 'Styles loaded', { count: styles.length, styles });
      
      // If no styles loaded, use fallback
      if (styles.length === 0) {
        console.warn('No styles loaded from API, using fallback');
        const fallbackStyles = [
          { id: 'photorealistic', name: 'Photorealistic', category: 'Photo', description: 'Realistic photography' },
          { id: 'digital_art', name: 'Digital Art', category: 'Digital', description: 'Modern digital artwork' },
          { id: 'oil_painting', name: 'Oil Painting', category: 'Creative', description: 'Classic painted style' },
          { id: 'anime', name: 'Anime', category: 'Anime', description: 'Japanese animation style' },
          { id: 'cyberpunk', name: 'Cyberpunk', category: 'Digital', description: 'Futuristic neon aesthetic' },
          { id: 'watercolor', name: 'Watercolor', category: 'Creative', description: 'Soft watercolor painting' },
          { id: '3d_render', name: '3D Render', category: '3D', description: 'Three-dimensional rendering' },
          { id: 'sketch', name: 'Sketch', category: 'Creative', description: 'Hand-drawn pencil sketch' },
        ] as any[];
        setAvailableStyles(fallbackStyles);
      }
    } catch (error) {
      Logger.error('ImageGenerator.loadStyles', error);
      toast.error('Failed to load styles');
    } finally {
      setStylesLoading(false);
    }
  };

  const [params, setParams] = useState<ImageGenerationParams>({
    prompt: '',
    style: 'photorealistic',
    cfg_scale: 7,
    steps: 30,
    width: 1024,
    height: 1024,
    model: 'sd3',
    negative_prompt: 'blurry, low quality, distorted',
    batch_size: 1,
  });
  
  const [generatedImages, setGeneratedImages] = useState<GeneratedImageData[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [img2imgFile, setImg2imgFile] = useState<File | null>(null);
  const [img2imgPreview, setImg2imgPreview] = useState<string | null>(null);
  const [mode, setMode] = useState<'text2img' | 'img2img'>('text2img');
  const [img2imgStrength, setImg2imgStrength] = useState(0.7);  // Higher default for more visible changes
  const [showGalleryModal, setShowGalleryModal] = useState(false);
  const [galleryImages, setGalleryImages] = useState<any[]>([]);
  const [loadingGallery, setLoadingGallery] = useState(false);
  
  // Prompt enhancement state
  const [enhancePrompt, setEnhancePrompt] = useState(true);
  const [enhancementLevel, setEnhancementLevel] = useState<'basic' | 'advanced' | 'expert'>('advanced');
  const [useMemory, setUseMemory] = useState(true);
  
  const { insights } = useStyleMemoryStore();

  // Get unique categories from loaded styles
  const categories = ['all', ...new Set(availableStyles.map(s => s.category))];
  
  // Filter styles by selected category
  const filteredStyles = selectedCategory === 'all' 
    ? availableStyles 
    : availableStyles.filter(s => s.category === selectedCategory);
  
  // Debug log
  console.log('Available styles:', availableStyles.length, 'Filtered styles:', filteredStyles.length, 'Category:', selectedCategory);
  
  // Get popular styles for quick access
  const popularStyles = availableStyles.filter(s => s.popular).slice(0, 6);

  // SD3 supported resolutions (Stability AI documentation)
  const resolutions = [
    // Most common/recommended
    { width: 1024, height: 1024, label: 'Square (1:1)', popular: true, desc: 'Best for logos, profile pics' },
    { width: 1344, height: 768, label: 'Landscape (16:9)', popular: true, desc: 'Best for banners, headers' },
    { width: 768, height: 1344, label: 'Portrait (9:16)', popular: true, desc: 'Best for mobile, stories' },
    { width: 1536, height: 640, label: 'Ultra Wide (21:9)', popular: true, desc: 'Best for hero images' },
    { width: 640, height: 1536, label: 'Ultra Tall (9:21)', popular: false, desc: 'Best for infographics' },
    // Additional SD3 supported resolutions
    { width: 1152, height: 896, label: 'Photo (4:3)', popular: false, desc: 'Classic photo ratio' },
    { width: 896, height: 1152, label: 'Portrait Photo (3:4)', popular: false, desc: 'Portrait photos' },
  ];

  // Dropzone for img2img
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      Logger.event('ImageGenerator', 'File dropped for img2img', { fileName: file.name, size: file.size });
      setImg2imgFile(file);
      setMode('img2img');
      
      // Create preview URL
      const reader = new FileReader();
      reader.onloadend = () => {
        setImg2imgPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      
      toast.success(`Image loaded: ${file.name}`);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp']
    },
    multiple: false,
  });

  // Gallery functions
  const loadGalleryImages = async () => {
    setLoadingGallery(true);
    try {
      const response = await apiClient.get('/api/v1/content/list/', {
        params: {
          type: 'image',
          limit: 50
        }
      });
      
      const allContent = response.data?.contents || [];
      
      // Filter to only show actual images (not 3D files, etc.)
      const imageContent = allContent.filter(item => {
        // First check if it's explicitly marked as image type
        if (item.type && item.type !== 'image') {
          return false;
        }
        
        // Then check the URL for image extensions
        const url = item.result || item.result_url || item.image_url || item.url;
        if (!url) return false;
        
        // More robust extension checking (case insensitive)
        const urlLower = url.toLowerCase();
        const isImageFile = (
          urlLower.includes('.png') || 
          urlLower.includes('.jpg') || 
          urlLower.includes('.jpeg') || 
          urlLower.includes('.webp') ||
          urlLower.includes('.gif') ||
          urlLower.includes('.bmp') ||
          urlLower.includes('.svg')
        );
        
        // Exclude 3D files explicitly
        const is3DFile = (
          urlLower.includes('.glb') ||
          urlLower.includes('.gltf') ||
          urlLower.includes('.obj') ||
          urlLower.includes('.fbx')
        );
        
        return isImageFile && !is3DFile;
      });
      
      setGalleryImages(imageContent);
    } catch (error) {
      console.error('Failed to load gallery:', error);
      toast.error('Failed to load gallery images');
    } finally {
      setLoadingGallery(false);
    }
  };

  const handleLoadFromGallery = () => {
    setShowGalleryModal(true);
    loadGalleryImages();
  };

  const handleSelectGalleryImage = async (imageItem: any) => {
    try {
      let imageUrl = imageItem.result || imageItem.result_url || imageItem.image_url || imageItem.url;
      
      if (!imageUrl.startsWith('http')) {
        if (imageUrl.startsWith('/media/')) {
          imageUrl = `${API_CONFIG.BASE_URL}${imageUrl}`;
        } else {
          imageUrl = `${API_CONFIG.BASE_URL}/media/${imageUrl}`;
        }
      }

      // Fetch the image and convert to File object
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const fileName = `gallery-image-${imageItem.id}.${blob.type.split('/')[1] || 'jpg'}`;
      const file = new File([blob], fileName, { type: blob.type });

      setImg2imgFile(file);
      setImg2imgPreview(imageUrl);
      setMode('img2img');
      setShowGalleryModal(false);
      
      toast.success(`Image loaded from gallery: ${imageItem.title || imageItem.prompt || fileName}`);
    } catch (error) {
      console.error('Failed to load gallery image:', error);
      toast.error('Failed to load gallery image');
    }
  };

  const handleGenerate = async () => {
    if (!params.prompt.trim()) {
      Logger.warn('ImageGenerator', 'Generation attempted without prompt');
      toast.error('Please enter a prompt');
      return;
    }

    Logger.event('ImageGenerator', 'Starting generation', { mode, params });
    setIsGenerating(true);
    try {
      let result;
      
      if (mode === 'img2img' && img2imgFile) {
        // Image-to-image generation
        Logger.api('POST', '/api/content/img2img/', { 
          prompt: params.prompt, 
          style: params.style, 
          strength: img2imgStrength,
          enhance_prompt: enhancePrompt,
          enhancement_level: enhancementLevel,
          use_memory: useMemory
        });
        result = await contentService.imageToImage(img2imgFile, {
          prompt: params.prompt,
          style: params.style,
          cfg_scale: params.cfg_scale,
          steps: params.steps,
          width: params.width,
          height: params.height,
          model: params.model,
          negative_prompt: params.negative_prompt,
          strength: img2imgStrength,
          enhance_prompt: enhancePrompt,
          enhancement_level: enhancementLevel,
          use_memory: useMemory,
        });
      } else if (params.batch_size > 1) {
        // Batch generation
        Logger.api('POST', '/api/content/batch/', { 
          batchSize: params.batch_size, 
          prompt: params.prompt,
          enhance_prompt: enhancePrompt,
          enhancement_level: enhancementLevel,
          use_memory: useMemory
        });
        result = await contentService.generateImageBatch({
          ...params,
          variations: params.batch_size,
          enhance_prompt: enhancePrompt,
          enhancement_level: enhancementLevel,
          use_memory: useMemory,
        });
      } else {
        // Single image generation
        Logger.api('POST', '/api/content/create/', { 
          prompt: params.prompt, 
          style: params.style,
          enhance_prompt: enhancePrompt,
          enhancement_level: enhancementLevel,
          use_memory: useMemory
        });
        result = await contentService.generateImage({
          ...params,
          enhance_prompt: enhancePrompt,
          enhancement_level: enhancementLevel,
          use_memory: useMemory,
        });
      }
      
      // Handle the result (format may vary)
      console.log('Image generation result:', result); // Debug log
      
      let images = [];
      
      // Check if response has a content wrapper (from /api/content/create/)
      if (result.success && result.content) {
        const content = result.content;
        if (Array.isArray(content.images)) {
          // Multiple images in content
          images = content.images;
        } else if (content.results) {
          // Results array in content
          images = content.results;
        } else if (content.result) {
          // Single image URL in content
          images = [{
            id: content.id,
            url: content.result,
            image_url: content.result,
            metadata: content.metadata
          }];
        }
      } else if (Array.isArray(result.images)) {
        // Direct batch response
        images = result.images;
      } else if (result.result) {
        // Single image response
        images = [{
          id: result.id,
          url: result.result,
          image_url: result.result,
          metadata: result.metadata
        }];
      } else if (result.url) {
        // img2img response format
        images = [{
          id: result.id,
          url: result.url,
          image_url: result.url,
          metadata: result.metadata
        }];
      } else {
        // Direct response
        images = [result];
      }
      
      const newImages = images.map((img: any, index: number) => {
        let imageUrl = img.url || img.image_url || img.result || '';
        
        // Add server prefix if URL starts with /media/
        if (imageUrl.startsWith('/media/')) {
          imageUrl = `${API_CONFIG.BASE_URL}${imageUrl}`;
        }
        
        return {
          id: img.id || `generated-${Date.now()}-${index}`,
          url: imageUrl,
          prompt: img.prompt || params.prompt,
          parameters: params,
          metadata: img.metadata || {}
        };
      });
      
      // Filter out images without URLs
      const validImages = newImages.filter(img => img.url && img.url !== '');
      
      if (validImages.length > 0) {
        setGeneratedImages([...validImages, ...generatedImages]);
        Logger.state('ImageGenerator', 'Images generated', { count: validImages.length, images: validImages });
        toast.success(`Generated ${validImages.length} image${validImages.length > 1 ? 's' : ''}!`);
      } else {
        Logger.warn('ImageGenerator', 'No valid images returned', { result });
        toast.error('Image generation completed but no images were returned');
      }
    } catch (error: any) {
      Logger.error('ImageGenerator.handleGenerate', error);
      toast.error(error.userMessage || 'Failed to generate image');
    } finally {
      setIsGenerating(false);
    }
  };

  const applyStyleMemorySettings = () => {
    if (insights) {
      Logger.event('ImageGenerator', 'Applying style memory settings', { 
        cfg: insights.preferred_cfg, 
        steps: insights.preferred_steps 
      });
      setParams({
        ...params,
        cfg_scale: insights.preferred_cfg,
        steps: insights.preferred_steps,
        style: insights.favorite_styles[0]?.style || params.style,
      });
      toast.success('Applied your style preferences!');
    }
  };

  return (
    <div className="space-y-6">
      {/* Mode Selection */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-foreground">Generation Mode</h3>
          {insights && (
            <Button 
              size="sm" 
              variant="secondary" 
              onClick={applyStyleMemorySettings}
            >
              <ArrowPathIcon className="h-4 w-4" />
              Use My Style Preferences
            </Button>
          )}
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Text-to-Image */}
          <button
            onClick={() => setMode('text2img')}
            className={`p-4 rounded-lg border-2 transition-all duration-200 text-left ${
              mode === 'text2img'
                ? 'border-primary-500 bg-primary-500/10'
                : 'border-border hover:border-dark-600 hover:bg-white/5'
            }`}
          >
            <PhotoIcon className={`h-6 w-6 mb-2 ${
              mode === 'text2img' ? 'text-primary-400' : 'text-muted-foreground'
            }`} />
            <div className={`font-medium mb-1 ${
              mode === 'text2img' ? 'text-foreground' : 'text-muted-foreground'
            }`}>
              Text to Image
            </div>
            <div className="text-xs text-muted-foreground">
              Generate images from text descriptions
            </div>
          </button>

          {/* Image-to-Image */}
          <div
            {...getRootProps({
              className: `relative p-4 rounded-lg border-2 border-dashed transition-all duration-200 cursor-pointer overflow-hidden ${
                mode === 'img2img'
                  ? 'border-primary-500 bg-primary-500/10'
                  : isDragActive
                  ? 'border-primary-400 bg-primary-500/5'
                  : 'border-border hover:border-dark-600 hover:bg-white/5'
              }`
            })}
          >
            <input {...getInputProps()} />
            
            {/* Show preview if image is uploaded */}
            {img2imgPreview ? (
              <div className="relative">
                <img 
                  src={img2imgPreview} 
                  alt="Upload preview" 
                  className="w-full h-32 object-cover rounded mb-2"
                />
                <div className="absolute top-2 right-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setImg2imgFile(null);
                      setImg2imgPreview(null);
                      setMode('text2img');
                      toast.info('Image removed');
                    }}
                    className="bg-red-500 text-foreground p-1 rounded-full hover:bg-red-600"
                  >
                    <XMarkIcon className="h-4 w-4" />
                  </button>
                </div>
                <div className="text-center">
                  <div className="text-primary-400 font-medium text-sm">✓ Image loaded</div>
                  <div className="text-xs text-muted-foreground">{img2imgFile?.name}</div>
                  <div className="text-xs text-muted-foreground mt-1">Add a prompt to transform this image</div>
                </div>
              </div>
            ) : (
              <>
                <CloudArrowUpIcon className={`h-6 w-6 mb-2 mx-auto ${
                  mode === 'img2img' || isDragActive ? 'text-primary-400' : 'text-muted-foreground'
                }`} />
                <div className={`font-medium mb-1 text-center ${
                  mode === 'img2img' || isDragActive ? 'text-foreground' : 'text-muted-foreground'
                }`}>
                  Image to Image
                </div>
                <div className="text-xs text-muted-foreground text-center mb-3">
                  {isDragActive 
                    ? 'Drop image here...'
                    : 'Click to upload or drag & drop an image'
                  }
                </div>
                
                {/* Gallery Button */}
                <div className="flex justify-center">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleLoadFromGallery();
                    }}
                    className="flex items-center gap-2 px-3 py-2 text-xs bg-dark-700 hover:bg-dark-600 border border-dark-600 rounded-lg text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <RectangleGroupIcon className="h-4 w-4" />
                    Load from Gallery
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Generation Settings */}
        <div className="xl:col-span-2 space-y-6">
          <Card>
            <h3 className="text-lg font-semibold text-foreground mb-4">Generation Settings</h3>
            <div className="space-y-4">
              {/* Prompt */}
              <div>
                <label className="block text-sm text-muted-foreground mb-2">
                  {mode === 'img2img' ? 'Transformation Prompt' : 'Prompt'}
                </label>
                <textarea
                  className="input min-h-[100px]"
                  placeholder={mode === 'img2img' 
                    ? "Describe how to transform the image (e.g., 'make it cyberpunk style', 'add a sunset', 'turn into watercolor painting')"
                    : "Describe the image you want to create..."}
                  value={params.prompt}
                  onChange={(e) => setParams({ ...params, prompt: e.target.value })}
                />
              </div>

              {/* AI Enhancement Controls */}
              <div className="bg-card/30 rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CpuChipIcon className="h-4 w-4 text-purple-400" />
                    <span className="text-sm text-muted-foreground">AI Enhancement</span>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={enhancePrompt}
                      onChange={(e) => setEnhancePrompt(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                  </label>
                </div>

                {enhancePrompt && (
                  <>
                    <div className="flex items-center gap-2">
                      <label className="text-xs text-muted-foreground">Level:</label>
                      <select
                        value={enhancementLevel}
                        onChange={(e) => setEnhancementLevel(e.target.value as any)}
                        className="flex-1 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-foreground text-sm"
                      >
                        <option value="basic">Basic</option>
                        <option value="advanced">Advanced</option>
                        <option value="expert">Expert</option>
                      </select>
                    </div>

                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        id="useMemory"
                        checked={useMemory}
                        onChange={(e) => setUseMemory(e.target.checked)}
                        className="rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                      />
                      <label htmlFor="useMemory" className="text-xs text-muted-foreground">
                        Use memory context for consistency
                      </label>
                    </div>
                  </>
                )}
              </div>

              {/* Image-to-Image Strength Slider (only show in img2img mode) */}
              {mode === 'img2img' && img2imgFile && (
                <div className="p-4 bg-primary-500/10 border border-primary-500/30 rounded-lg">
                  <label className="block text-sm text-muted-foreground mb-2">
                    Transformation Strength: {img2imgStrength.toFixed(1)}
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.05"
                    value={img2imgStrength}
                    onChange={(e) => setImg2imgStrength(parseFloat(e.target.value))}
                    className="w-full accent-primary-500 mb-2"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground mb-2">
                    <span>Subtle</span>
                    <span>Balanced</span>
                    <span>Dramatic</span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {img2imgStrength <= 0.4 && "Subtle changes - Keeps original structure, minor style tweaks"}
                    {img2imgStrength > 0.4 && img2imgStrength <= 0.7 && "Moderate changes - Good balance, can add/modify objects"}
                    {img2imgStrength > 0.7 && img2imgStrength <= 0.9 && "Strong changes - Major transformations, can completely reimagine scene"}
                    {img2imgStrength > 0.9 && "🔥 MAXIMUM POWER - Total transformation, might be unrecognizable!"}
                  </div>
                </div>
              )}

              {/* Style Selection */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <label className="text-sm text-muted-foreground">Style ({availableStyles.length} available)</label>
                  {stylesLoading && <span className="text-xs text-muted-foreground">Loading styles...</span>}
                </div>
                
                {/* Category Filter */}
                <div className="flex gap-2 mb-3 overflow-x-auto scrollbar-thin scrollbar-thumb-dark-700">
                  {categories.map((cat) => (
                    <button
                      key={cat}
                      onClick={() => setSelectedCategory(cat)}
                      className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-all ${
                        selectedCategory === cat
                          ? 'bg-primary-500 text-foreground'
                          : 'bg-card text-muted-foreground hover:bg-dark-700'
                      }`}
                    >
                      {cat === 'all' ? `All (${availableStyles.length})` : `${cat} (${availableStyles.filter(s => s.category === cat).length})`}
                    </button>
                  ))}
                </div>
                
                {/* Popular Styles (Quick Access) */}
                {popularStyles.length > 0 && selectedCategory === 'all' && (
                  <div className="mb-3">
                    <div className="text-xs text-muted-foreground mb-2">⭐ Popular Styles</div>
                    <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
                      {popularStyles.map((style) => (
                        <button
                          key={style.id}
                          onClick={() => setParams({ ...params, style: style.id })}
                          className={`p-2 rounded-lg border text-center transition-all duration-200 ${
                            params.style === style.id
                              ? 'border-primary-500 bg-primary-500/10 text-primary-300'
                              : 'border-border hover:border-dark-600 hover:bg-white/5 text-muted-foreground'
                          }`}
                        >
                          <div className="text-xs font-medium">{style.emoji} {style.name.substring(0, 15)}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* All Styles Grid */}
                <div className="max-h-64 overflow-y-auto scrollbar-thin scrollbar-thumb-dark-700">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {filteredStyles.map((style) => (
                      <button
                        key={style.id}
                        onClick={() => setParams({ ...params, style: style.id })}
                        className={`p-3 rounded-lg border text-left transition-all duration-200 ${
                          params.style === style.id
                            ? 'border-primary-500 bg-primary-500/10 text-primary-300'
                            : 'border-border hover:border-dark-600 hover:bg-white/5 text-muted-foreground'
                        }`}
                      >
                        <div className="font-medium text-sm">
                          {style.emoji && <span className="mr-1">{style.emoji}</span>}
                          {style.name}
                        </div>
                        <div className="text-xs mt-1 opacity-75">{style.description || style.name}</div>
                        <div className="text-xs mt-1 opacity-50">{style.category}</div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Resolution */}
              <div>
                <label className="block text-sm text-muted-foreground mb-2">Resolution (SD3 Optimized)</label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {resolutions.filter(r => r.popular).map((res) => {
                    const isSelected = params.width === res.width && params.height === res.height;
                    return (
                      <button
                        key={`${res.width}x${res.height}`}
                        onClick={() => setParams({ ...params, width: res.width, height: res.height })}
                        className={`p-3 rounded-lg border text-left transition-all duration-200 ${
                          isSelected
                            ? 'border-primary-500 bg-primary-500/10 text-primary-300'
                            : 'border-border hover:border-dark-600 hover:bg-white/5 text-muted-foreground'
                        }`}
                      >
                        <div className="text-sm font-medium">{res.label}</div>
                        <div className="text-xs opacity-75">{res.width}×{res.height}</div>
                        {res.desc && <div className="text-xs mt-1 opacity-50">{res.desc}</div>}
                      </button>
                    );
                  })}
                </div>
                
                {/* Show more resolutions toggle */}
                <details className="mt-2">
                  <summary className="text-xs text-muted-foreground cursor-pointer hover:text-muted-foreground">Show more resolutions...</summary>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
                    {resolutions.filter(r => !r.popular).map((res) => {
                      const isSelected = params.width === res.width && params.height === res.height;
                      return (
                        <button
                          key={`${res.width}x${res.height}`}
                          onClick={() => setParams({ ...params, width: res.width, height: res.height })}
                          className={`p-3 rounded-lg border text-left transition-all duration-200 ${
                            isSelected
                              ? 'border-primary-500 bg-primary-500/10 text-primary-300'
                              : 'border-border hover:border-dark-600 hover:bg-white/5 text-muted-foreground'
                          }`}
                        >
                          <div className="text-sm font-medium">{res.label}</div>
                          <div className="text-xs opacity-75">{res.width}×{res.height}</div>
                          {res.desc && <div className="text-xs mt-1 opacity-50">{res.desc}</div>}
                        </button>
                      );
                    })}
                  </div>
                </details>
              </div>

              {/* Batch Size */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-muted-foreground mb-2">
                    {mode === 'img2img' ? 'Batch (disabled for img2img)' : 'Batch Size'}
                  </label>
                  <select 
                    className="input"
                    value={mode === 'img2img' ? 1 : params.batch_size}
                    onChange={(e) => setParams({ ...params, batch_size: parseInt(e.target.value) })}
                    disabled={mode === 'img2img'}
                  >
                    <option value={1}>1 image</option>
                    <option value={2}>2 images</option>
                    <option value={4}>4 images</option>
                    <option value={6}>6 images</option>
                    <option value={8}>8 images</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm text-muted-foreground mb-2">Model</label>
                  <select 
                    className="input"
                    value={params.model}
                    onChange={(e) => setParams({ ...params, model: e.target.value })}
                  >
                    <option value="sd3">Stable Diffusion 3 (Best)</option>
                    <option value="sdxl">SDXL (Fast)</option>
                    <option value="sd2">SD 2.1 (Classic)</option>
                  </select>
                </div>
              </div>

              {/* Advanced Settings */}
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                <AdjustmentsHorizontalIcon className="h-4 w-4" />
                Advanced Settings
              </button>

              {showAdvanced && (
                <div className="space-y-4 p-4 bg-background/50 rounded-lg border border-border">
                  <div>
                    <label className="block text-sm text-muted-foreground mb-2">
                      CFG Scale: {params.cfg_scale}
                    </label>
                    <input
                      type="range"
                      min="1"
                      max="20"
                      step="0.5"
                      value={params.cfg_scale}
                      onChange={(e) => setParams({ ...params, cfg_scale: parseFloat(e.target.value) })}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground mt-1">
                      <span>Creative</span>
                      <span>Precise</span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm text-muted-foreground mb-2">
                      Steps: {params.steps}
                    </label>
                    <input
                      type="range"
                      min="10"
                      max="50"
                      step="5"
                      value={params.steps}
                      onChange={(e) => setParams({ ...params, steps: parseInt(e.target.value) })}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground mt-1">
                      <span>Fast</span>
                      <span>Quality</span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm text-muted-foreground mb-2">Negative Prompt</label>
                    <textarea
                      className="input min-h-[60px]"
                      placeholder="What to avoid in the image..."
                      value={params.negative_prompt}
                      onChange={(e) => setParams({ ...params, negative_prompt: e.target.value })}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm text-muted-foreground mb-2">Seed (optional)</label>
                    <input
                      type="number"
                      className="input"
                      placeholder="Random seed for reproducible results"
                      value={params.seed?.toString() || ''}
                      onChange={(e) => {
                        const value = e.target.value;
                        setParams({
                          ...params,
                          seed: value === '' ? undefined : parseInt(value)
                        });
                      }}
                    />
                  </div>
                </div>
              )}

              {/* Generate Button */}
              <div className="flex gap-3">
                <Button 
                  onClick={handleGenerate}
                  loading={isGenerating}
                  className="flex-1"
                  disabled={mode === 'img2img' && !img2imgFile}
                >
                  <PhotoIcon className="h-4 w-4" />
                  {mode === 'img2img' 
                    ? (img2imgFile ? 'Transform Image' : 'Upload an image first')
                    : `Generate ${params.batch_size > 1 ? `${params.batch_size} Images` : 'Image'}`
                  }
                </Button>
                
                {generatedImages.length > 0 && (
                  <Button 
                    variant="secondary"
                    onClick={() => setGeneratedImages([])}
                  >
                    Clear All
                  </Button>
                )}
              </div>
            </div>
          </Card>
        </div>

        {/* Generated Images */}
        <div className="space-y-6">
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-foreground">Generated Images</h3>
              {generatedImages.length > 0 && (
                <span className="text-sm text-muted-foreground">{generatedImages.length} images</span>
              )}
            </div>
            
            {isGenerating ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin h-8 w-8 border-2 border-primary-500 border-t-transparent rounded-full" />
                <span className="ml-3 text-muted-foreground">Generating images...</span>
              </div>
            ) : generatedImages.length > 0 ? (
              <div className="space-y-4">
                {generatedImages.map((image) => (
                  <GeneratedImage
                    key={image.id}
                    id={image.id}
                    src={image.url}
                    prompt={image.prompt}
                    parameters={image.parameters}
                    showStyleControls={true}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                <PhotoIcon className="h-16 w-16 mx-auto mb-4 text-gray-600" />
                <p>Generated images will appear here</p>
              </div>
            )}
          </Card>
        </div>
      </div>

      {/* Gallery Modal */}
      {showGalleryModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card rounded-xl border border-border max-w-4xl w-full max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-border">
              <h3 className="text-lg font-semibold text-foreground">Select Image from Gallery</h3>
              <button
                onClick={() => setShowGalleryModal(false)}
                className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
              >
                <XMarkIcon className="h-5 w-5 text-muted-foreground" />
              </button>
            </div>
            
            <div className="p-4 overflow-y-auto max-h-[60vh]">
              {loadingGallery ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
                  <span className="ml-3 text-muted-foreground">Loading gallery...</span>
                </div>
              ) : galleryImages.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {galleryImages.map((image, index) => (
                    <button
                      key={image.id || index}
                      onClick={() => handleSelectGalleryImage(image)}
                      className="relative group aspect-square overflow-hidden rounded-lg border-2 border-border hover:border-primary-500 transition-colors"
                    >
                      <img
                        src={(() => {
                          const url = image.result || image.result_url || image.image_url || image.url;
                          if (!url) return '';
                          if (url.startsWith('http')) return url; // Already full URL
                          if (url.startsWith('/media/')) return `${API_CONFIG.BASE_URL}${url}`;
                          return `${API_CONFIG.BASE_URL}/media/${url}`; // Fallback
                        })()}
                        alt={image.title || image.prompt || 'Gallery image'}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          console.log('Image failed to load:', e.currentTarget.src);
                        }}
                      />
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                          <PhotoIcon className="h-6 w-6 text-foreground" />
                        </div>
                      </div>
                      {(image.title || image.prompt) && (
                        <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-foreground text-xs p-1 truncate">
                          {image.title || image.prompt}
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <PhotoIcon className="h-16 w-16 mx-auto mb-4 text-gray-600" />
                  <p>No images found in gallery</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}