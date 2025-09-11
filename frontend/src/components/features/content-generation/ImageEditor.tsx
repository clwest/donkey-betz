import { useState, useRef, useCallback, useEffect } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { 
  PaintBrushIcon, 
  ArrowUpIcon, 
  ScissorsIcon,
  MagnifyingGlassPlusIcon,
  SparklesIcon,
  ArrowsPointingOutIcon,
  MagnifyingGlassIcon,
  CubeIcon,
  TrashIcon,
  PhotoIcon,
  ArrowDownTrayIcon,
  XMarkIcon,
  BookmarkIcon,
  RectangleGroupIcon,
} from '@heroicons/react/24/outline';
import { toast } from 'sonner';
import { contentService } from '../../../services/content.service';
import { apiClient } from '../../../services/api.config';
import { Logger } from '../../../utils/logger';

type EditTool = 'upscale' | 'remove_bg' | 'inpaint' | 'outpaint' | 'search_replace' | 'erase' | 'sketch' | '3d';

interface EditResult {
  id: string;
  tool: EditTool;
  image_url: string;
  created_at: string;
  is3D?: boolean;
}

export function ImageEditor() {
  useEffect(() => {
    Logger.component('ImageEditor', 'Mounting');
    return () => {
      Logger.component('ImageEditor', 'Unmounting');
    };
  }, []);

  const [selectedTool, setSelectedTool] = useState<EditTool>('upscale');
  const [originalImage, setOriginalImage] = useState<File | null>(null);
  const [originalImageUrl, setOriginalImageUrl] = useState<string>('');
  const [maskFile, setMaskFile] = useState<File | null>(null);
  const [maskUrl, setMaskUrl] = useState<string>('');
  const [prompt, setPrompt] = useState('');
  const [searchPrompt, setSearchPrompt] = useState('');
  const [replacePrompt, setReplacePrompt] = useState('');
  const [upscaleFactor, setUpscaleFactor] = useState<2 | 4>(2);
  const [creativity, setCreativity] = useState<'conservative' | 'creative'>('conservative');
  const [outpaintDirection, setOutpaintDirection] = useState<'up' | 'down' | 'left' | 'right' | 'all'>('all');
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<EditResult[]>([]);
  const [showGalleryModal, setShowGalleryModal] = useState(false);
  const [galleryImages, setGalleryImages] = useState<any[]>([]);
  const [loadingGallery, setLoadingGallery] = useState(false);
  const [showMaskDrawer, setShowMaskDrawer] = useState(false);
  const [brushSize, setBrushSize] = useState(20);
  const [isDrawing, setIsDrawing] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const maskInputRef = useRef<HTMLInputElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const maskCanvasRef = useRef<HTMLCanvasElement>(null);

  const tools = [
    { id: 'upscale', name: 'Upscale', icon: MagnifyingGlassPlusIcon, desc: '2x-4x enhancement' },
    { id: 'remove_bg', name: 'Remove BG', icon: ScissorsIcon, desc: 'Remove background' },
    { id: 'inpaint', name: 'Inpaint', icon: PaintBrushIcon, desc: 'Edit specific areas' },
    { id: 'outpaint', name: 'Outpaint', icon: ArrowsPointingOutIcon, desc: 'Expand canvas' },
    { id: 'search_replace', name: 'Replace', icon: MagnifyingGlassIcon, desc: 'Search & replace objects' },
    { id: 'erase', name: 'Erase', icon: TrashIcon, desc: 'Remove objects' },
    { id: 'sketch', name: 'Sketch', icon: SparklesIcon, desc: 'Sketch to image' },
    { id: '3d', name: '3D', icon: CubeIcon, desc: '2D to 3D model' },
  ] as const;

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      Logger.event('ImageEditor', 'Image uploaded', { fileName: file.name, size: file.size });
      setOriginalImage(file);
      setOriginalImageUrl(URL.createObjectURL(file));
      toast.success('Image uploaded successfully');
    } else {
      Logger.warn('ImageEditor', 'Invalid image upload attempt', { fileType: file?.type });
      toast.error('Please upload a valid image file');
    }
  };

  const handleMaskUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setMaskFile(file);
      setMaskUrl(URL.createObjectURL(file));
      toast.success('Mask uploaded successfully');
    } else {
      toast.error('Please upload a valid mask image');
    }
  };

  const requiresMask = (tool: EditTool) => {
    return ['inpaint', 'erase'].includes(tool);
  };

  const requiresPrompt = (tool: EditTool) => {
    return ['inpaint', 'outpaint', 'sketch', 'search_replace'].includes(tool);
  };

  const handleProcess = async () => {
    if (!originalImage) {
      toast.error('Please upload an image first');
      return;
    }

    if (requiresMask(selectedTool) && !maskFile) {
      toast.error('This tool requires a mask image');
      return;
    }

    if (requiresPrompt(selectedTool) && !prompt.trim() && selectedTool !== 'search_replace') {
      toast.error('This tool requires a prompt');
      return;
    }

    if (selectedTool === 'search_replace' && (!searchPrompt.trim() || !replacePrompt.trim())) {
      toast.error('Search & Replace requires both search and replace prompts');
      return;
    }

    setIsProcessing(true);

    try {
      let result;
      
      switch (selectedTool) {
        case 'upscale':
          Logger.api('POST', '/api/stability/upscale/', { factor: upscaleFactor, creativity });
          result = await contentService.upscaleImage(originalImage, upscaleFactor, creativity);
          break;
          
        case 'remove_bg':
          toast.info('Processing image... Large images will be resized to 1024x1024 for best results.');
          result = await contentService.removeBackground(originalImage);
          break;
          
        case 'inpaint':
          if (!maskFile) throw new Error('Mask required for inpainting');
          result = await contentService.inpaintImage(originalImage, maskFile, prompt);
          break;
          
        case 'outpaint':
          result = await contentService.outpaintImage(originalImage, outpaintDirection, prompt);
          break;
          
        case 'search_replace':
          result = await contentService.searchAndReplace(originalImage, searchPrompt, replacePrompt);
          break;
          
        case 'erase':
          if (!maskFile) throw new Error('Mask required for erasing');
          result = await contentService.eraseObject(originalImage, maskFile);
          break;
          
        case 'sketch':
          result = await contentService.sketchToImage(originalImage, prompt);
          break;
          
        case '3d':
          toast.info('Generating 3D model... This may take up to 2 minutes. Image will be resized if needed.');
          result = await contentService.generate3D(originalImage);
          break;
          
        default:
          throw new Error('Unknown tool');
      }

      // Handle different result types
      let resultUrl = '';
      let is3D = false;
      
      if (selectedTool === '3d') {
        // 3D models return file_url for GLB files
        resultUrl = result.file_url || result.url || '';
        is3D = true;
      } else {
        // Images return image_url
        resultUrl = result.image_url || result.url || '';
      }
      
      // Fix URL if it's a relative path
      if (resultUrl.startsWith('/media/')) {
        resultUrl = `http://localhost:8000${resultUrl}`;
      }
      
      const editResult: EditResult = {
        id: result.id || Date.now().toString(),
        tool: selectedTool,
        image_url: resultUrl,
        created_at: new Date().toISOString(),
        is3D: is3D,
      };

      setResults(prev => [editResult, ...prev]);
      
      if (is3D) {
        toast.success('3D model generated successfully! Click download to save the GLB file.');
      } else {
        toast.success('Image processed successfully!');
      }

    } catch (error: any) {
      console.error('Image processing error:', error);
      toast.error(error.userMessage || `Failed to process image with ${selectedTool}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = (imageUrl: string, tool: string, is3D?: boolean) => {
    const link = document.createElement('a');
    link.href = imageUrl;
    const extension = is3D ? 'glb' : 'png';
    link.download = `edited-${tool}-${Date.now()}.${extension}`;
    link.click();
    toast.success(is3D ? '3D model download started' : 'Image download started');
  };

  const handleSaveToGallery = async (result: EditResult) => {
    try {
      // Don't save 3D models to gallery (they're GLB files, not images)
      if (result.is3D) {
        toast.info('3D models are automatically saved. Use Download to get the GLB file.');
        return;
      }
      
      // Get the tool label for better title
      const toolLabel = tools.find(t => t.id === result.tool)?.label || result.tool;
      
      // Save directly using the gallery/save endpoint with image_url
      const response = await contentService.saveImageToGallery({
        image_url: result.image_url,
        title: `${toolLabel} Edit`,
        description: `Image edited using ${toolLabel}`,
        category: 'edited',
        tags: [result.tool, 'edited', 'ai-enhanced'],
        original_prompt: `Applied ${toolLabel} effect`,
        style_used: result.tool,
        is_public: false
      });
      
      toast.success('Saved to gallery!');
    } catch (error) {
      console.error('Failed to save to gallery:', error);
      toast.error('Failed to save to gallery');
    }
  };

  const clearImage = () => {
    setOriginalImage(null);
    setOriginalImageUrl('');
    setMaskFile(null);
    setMaskUrl('');
    setResults([]);
    setShowMaskDrawer(false);
  };

  const startDrawMask = () => {
    if (!originalImage) {
      toast.error('Please upload an image first');
      return;
    }
    setShowMaskDrawer(true);
  };

  const clearMask = () => {
    const canvas = maskCanvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'black';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }
    }
    setMaskFile(null);
    setMaskUrl('');
  };

  const saveMask = () => {
    const canvas = maskCanvasRef.current;
    if (!canvas) return;

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'mask.png', { type: 'image/png' });
        setMaskFile(file);
        setMaskUrl(URL.createObjectURL(file));
        setShowMaskDrawer(false);
        toast.success('Mask created successfully!');
      }
    }, 'image/png');
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDrawing(true);
    draw(e);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDrawing) return;
    draw(e);
  };

  const handleMouseUp = () => {
    setIsDrawing(false);
  };

  const draw = (e: React.MouseEvent) => {
    const canvas = maskCanvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(x, y, brushSize / 2, 0, 2 * Math.PI);
    ctx.fill();
  };

  const loadGalleryImages = async () => {
    setLoadingGallery(true);
    try {
      // Use the same API call that GalleryPage uses successfully
      const response = await apiClient.get('/content/list/', {
        params: {
          type: 'image',
          limit: 50
        }
      });
      
      const allContent = response.data?.contents || [];
      console.log('All content loaded:', allContent.length, 'items'); // Debug log
      
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
        
        console.log(`Item ${item.id}: type=${item.type}, url=${url}, isImage=${isImageFile}, is3D=${is3DFile}`);
        
        return isImageFile && !is3DFile;
      });
      
      console.log('Gallery images loaded:', imageContent.length, 'filtered from', allContent.length); // Debug log
      if (imageContent.length > 0) console.log('First image:', imageContent[0]);
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
      // Create a URL for the image (content list API returns result_url)
      let imageUrl = imageItem.result || imageItem.result_url || imageItem.image_url || imageItem.url;
      console.log('Selecting image with URL:', imageUrl); // Debug log
      
      if (!imageUrl) {
        toast.error('Image URL not found');
        return;
      }
      
      if (imageUrl.startsWith('http')) {
        // Already full URL
      } else if (imageUrl.startsWith('/media/')) {
        imageUrl = `http://localhost:8000${imageUrl}`;
      } else {
        imageUrl = `http://localhost:8000/media/${imageUrl}`;
      }
      
      // Load the image as a File object
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const fileName = imageItem.title || imageItem.prompt || `gallery-image-${Date.now()}.jpg`;
      const file = new File([blob], fileName, { type: blob.type });
      
      setOriginalImage(file);
      setOriginalImageUrl(imageUrl);
      setShowGalleryModal(false);
      
      toast.success('Image loaded from gallery!');
    } catch (error) {
      console.error('Failed to load image from gallery:', error);
      toast.error('Failed to load image from gallery');
    }
  };

  const selectedToolData = tools.find(t => t.id === selectedTool);

  return (
    <div className="space-y-6">
      {/* Tool Selection */}
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">AI Image Editor</h3>
        <p className="text-gray-400 mb-6">Professional image editing powered by Stability AI</p>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {tools.map((tool) => {
            const isSelected = selectedTool === tool.id;
            return (
              <button
                key={tool.id}
                onClick={() => setSelectedTool(tool.id)}
                className={`p-3 rounded-lg border-2 transition-all duration-200 text-center ${
                  isSelected
                    ? 'border-primary-500 bg-primary-500/10'
                    : 'border-dark-700 hover:border-dark-600 hover:bg-white/5'
                }`}
              >
                <tool.icon className={`h-6 w-6 mx-auto mb-1 ${
                  isSelected ? 'text-primary-400' : 'text-gray-400'
                }`} />
                <div className={`font-medium text-sm mb-1 ${
                  isSelected ? 'text-white' : 'text-gray-300'
                }`}>
                  {tool.name}
                </div>
                <div className="text-xs text-gray-500">
                  {tool.desc}
                </div>
              </button>
            );
          })}
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload & Settings Panel */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">
              {selectedToolData?.name} Settings
            </h3>
            {originalImage && (
              <Button
                onClick={clearImage}
                variant="secondary"
                size="sm"
              >
                <XMarkIcon className="h-4 w-4" />
                Clear
              </Button>
            )}
          </div>
          
          <div className="space-y-4">
            {/* Image Upload */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm text-gray-400">Source Image</label>
                <Button
                  onClick={handleLoadFromGallery}
                  variant="secondary"
                  size="sm"
                >
                  <RectangleGroupIcon className="h-4 w-4" />
                  Load from Gallery
                </Button>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="w-full p-4 border-2 border-dashed border-dark-700 rounded-lg hover:border-dark-600 transition-colors text-center"
              >
                {originalImageUrl ? (
                  <div className="space-y-2">
                    <img 
                      src={originalImageUrl} 
                      alt="Source" 
                      className="w-full h-32 object-cover rounded"
                    />
                    <p className="text-sm text-gray-400">{originalImage?.name}</p>
                  </div>
                ) : (
                  <div>
                    <PhotoIcon className="h-8 w-8 mx-auto mb-2 text-gray-500" />
                    <p className="text-gray-400">Click to upload image</p>
                  </div>
                )}
              </button>
            </div>

            {/* Mask Upload for tools that need it */}
            {requiresMask(selectedTool) && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm text-gray-400">
                    Mask Image (white = edit area, black = keep)
                  </label>
                  <Button
                    onClick={startDrawMask}
                    variant="secondary"
                    size="sm"
                    disabled={!originalImage}
                  >
                    <PaintBrushIcon className="h-4 w-4" />
                    Draw Mask
                  </Button>
                </div>
                <input
                  ref={maskInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleMaskUpload}
                  className="hidden"
                />
                <button
                  onClick={() => maskInputRef.current?.click()}
                  className="w-full p-4 border-2 border-dashed border-dark-700 rounded-lg hover:border-dark-600 transition-colors text-center"
                >
                  {maskUrl ? (
                    <div className="space-y-2">
                      <img 
                        src={maskUrl} 
                        alt="Mask" 
                        className="w-full h-24 object-cover rounded"
                      />
                      <p className="text-sm text-gray-400">{maskFile?.name}</p>
                    </div>
                  ) : (
                    <div>
                      <PaintBrushIcon className="h-6 w-6 mx-auto mb-2 text-gray-500" />
                      <p className="text-gray-400">Upload mask image or use Draw Mask</p>
                    </div>
                  )}
                </button>
              </div>
            )}

            {/* Tool-specific settings */}
            {selectedTool === 'upscale' && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Factor</label>
                  <select 
                    className="input"
                    value={upscaleFactor}
                    onChange={(e) => setUpscaleFactor(parseInt(e.target.value) as 2 | 4)}
                  >
                    <option value={2}>2x</option>
                    <option value={4}>4x</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Mode</label>
                  <select 
                    className="input"
                    value={creativity}
                    onChange={(e) => setCreativity(e.target.value as 'conservative' | 'creative')}
                  >
                    <option value="conservative">Conservative</option>
                    <option value="creative">Creative</option>
                  </select>
                </div>
              </div>
            )}

            {selectedTool === 'outpaint' && (
              <div>
                <label className="block text-sm text-gray-400 mb-2">Direction</label>
                <select 
                  className="input"
                  value={outpaintDirection}
                  onChange={(e) => setOutpaintDirection(e.target.value as any)}
                >
                  <option value="all">All Directions</option>
                  <option value="up">Up</option>
                  <option value="down">Down</option>
                  <option value="left">Left</option>
                  <option value="right">Right</option>
                </select>
              </div>
            )}

            {selectedTool === 'search_replace' && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Search For</label>
                  <input
                    className="input"
                    placeholder="dog"
                    value={searchPrompt}
                    onChange={(e) => setSearchPrompt(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Replace With</label>
                  <input
                    className="input"
                    placeholder="cat"
                    value={replacePrompt}
                    onChange={(e) => setReplacePrompt(e.target.value)}
                  />
                </div>
              </div>
            )}

            {/* Prompt for tools that need it */}
            {requiresPrompt(selectedTool) && selectedTool !== 'search_replace' && (
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  {selectedTool === 'inpaint' ? 'What to paint in the masked area' : 
                   selectedTool === 'outpaint' ? 'What to add (optional)' :
                   selectedTool === 'sketch' ? 'What this sketch represents' : 'Prompt'}
                </label>
                <textarea
                  className="input min-h-[80px]"
                  placeholder={
                    selectedTool === 'inpaint' ? 'a beautiful sunset' :
                    selectedTool === 'outpaint' ? 'more landscape, trees...' :
                    selectedTool === 'sketch' ? 'a detailed portrait of a person' :
                    'Describe what you want...'
                  }
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                />
              </div>
            )}

            {/* Process Button */}
            <Button 
              onClick={handleProcess}
              loading={isProcessing}
              disabled={!originalImage}
              className="w-full"
            >
              {selectedToolData && <selectedToolData.icon className="h-4 w-4" />}
              {isProcessing ? 'Processing...' : `Apply ${selectedToolData?.name}`}
            </Button>
          </div>
        </Card>

        {/* Results Panel */}
        <Card>
          <h3 className="text-lg font-semibold text-white mb-4">Results</h3>
          
          {results.length > 0 ? (
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {results.map((result) => (
                <div key={result.id} className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400 capitalize">
                      {result.tool.replace('_', ' ')} • {new Date(result.created_at).toLocaleTimeString()}
                    </span>
                    <div className="flex gap-2">
                      {!result.is3D && (
                        <Button
                          onClick={() => handleSaveToGallery(result)}
                          variant="primary"
                          size="sm"
                        >
                          <BookmarkIcon className="h-4 w-4" />
                          Save
                        </Button>
                      )}
                      <Button
                        onClick={() => handleDownload(result.image_url, result.tool, result.is3D)}
                        variant={result.is3D ? "primary" : "secondary"}
                        size="sm"
                      >
                        <ArrowDownTrayIcon className="h-4 w-4" />
                        {result.is3D ? 'Download 3D Model' : 'Download'}
                      </Button>
                    </div>
                  </div>
                  
                  <div className="relative">
                    {result.is3D ? (
                      <div className="w-full aspect-square bg-dark-900 rounded-lg flex flex-col items-center justify-center text-gray-400">
                        <CubeIcon className="h-24 w-24 mb-4" />
                        <p className="text-lg font-semibold">3D Model Generated</p>
                        <p className="text-sm mt-2">GLB Format</p>
                        <p className="text-xs mt-1 text-gray-500">Click Download to save the 3D file</p>
                      </div>
                    ) : (
                      <img 
                        src={result.image_url} 
                        alt={`${result.tool} result`}
                        className="w-full rounded-lg bg-dark-900"
                      />
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <SparklesIcon className="h-16 w-16 mx-auto mb-4 text-gray-600" />
              <p>Edited images will appear here</p>
              <p className="text-sm mt-2">
                Upload an image and select a tool to get started
              </p>
            </div>
          )}
        </Card>
      </div>

      {/* Gallery Modal */}
      {showGalleryModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-dark-800 rounded-xl border border-dark-700 w-full max-w-4xl max-h-[80vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-dark-700">
              <h3 className="text-lg font-semibold text-white">Select Image from Gallery</h3>
              <button
                onClick={() => setShowGalleryModal(false)}
                className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
              >
                <XMarkIcon className="h-5 w-5 text-gray-400" />
              </button>
            </div>
            
            <div className="p-4 overflow-y-auto max-h-[60vh]">
              {loadingGallery ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
                  <span className="ml-3 text-gray-400">Loading gallery...</span>
                </div>
              ) : galleryImages.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {galleryImages.map((image, index) => (
                    <button
                      key={image.id || index}
                      onClick={() => handleSelectGalleryImage(image)}
                      className="relative group aspect-square overflow-hidden rounded-lg border-2 border-dark-700 hover:border-primary-500 transition-colors"
                    >
                      <img
                        src={(() => {
                          const url = image.result || image.result_url || image.image_url || image.url;
                          console.log('Image URL:', url, 'for image:', image.id); // Debug log
                          if (!url) return '';
                          if (url.startsWith('http')) return url; // Already full URL
                          if (url.startsWith('/media/')) return `http://localhost:8000${url}`;
                          return `http://localhost:8000/media/${url}`; // Fallback
                        })()}
                        alt={image.title || image.prompt || 'Gallery image'}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          console.log('Image failed to load:', e.currentTarget.src);
                        }}
                      />
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                          <PhotoIcon className="h-6 w-6 text-white" />
                        </div>
                      </div>
                      {(image.title || image.prompt) && (
                        <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-xs p-1 truncate">
                          {image.title || image.prompt}
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <PhotoIcon className="h-16 w-16 mx-auto mb-4 text-gray-600" />
                  <p>No images in gallery</p>
                  <p className="text-sm mt-2">Generate some images first to use this feature</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Mask Drawing Modal */}
      {showMaskDrawer && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-dark-800 rounded-xl border border-dark-700 w-full max-w-4xl max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-dark-700">
              <h3 className="text-lg font-semibold text-white">Draw Mask</h3>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-400">Brush Size:</label>
                  <input
                    type="range"
                    min="5"
                    max="50"
                    value={brushSize}
                    onChange={(e) => setBrushSize(Number(e.target.value))}
                    className="w-20"
                  />
                  <span className="text-sm text-white w-8">{brushSize}</span>
                </div>
                <Button onClick={clearMask} variant="secondary" size="sm">
                  Clear
                </Button>
                <Button onClick={saveMask} variant="primary" size="sm">
                  Save Mask
                </Button>
                <button
                  onClick={() => setShowMaskDrawer(false)}
                  className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
                >
                  <XMarkIcon className="h-5 w-5 text-gray-400" />
                </button>
              </div>
            </div>
            
            <div className="p-4 overflow-auto max-h-[70vh] flex justify-center">
              <div className="relative inline-block">
                {originalImageUrl && (
                  <>
                    <img
                      src={originalImageUrl}
                      alt="Original"
                      className="max-w-full max-h-[60vh] object-contain rounded-lg"
                      onLoad={(e) => {
                        const img = e.currentTarget;
                        const canvas = maskCanvasRef.current;
                        if (canvas) {
                          canvas.width = img.naturalWidth;
                          canvas.height = img.naturalHeight;
                          canvas.style.width = img.offsetWidth + 'px';
                          canvas.style.height = img.offsetHeight + 'px';
                          
                          // Initialize with black background
                          const ctx = canvas.getContext('2d');
                          if (ctx) {
                            ctx.fillStyle = 'black';
                            ctx.fillRect(0, 0, canvas.width, canvas.height);
                          }
                        }
                      }}
                    />
                    <canvas
                      ref={maskCanvasRef}
                      className="absolute top-0 left-0 cursor-crosshair opacity-50 rounded-lg"
                      onMouseDown={handleMouseDown}
                      onMouseMove={handleMouseMove}
                      onMouseUp={handleMouseUp}
                      onMouseLeave={handleMouseUp}
                    />
                  </>
                )}
              </div>
            </div>

            <div className="p-4 border-t border-dark-700 bg-dark-900 text-center">
              <p className="text-sm text-gray-400">
                Paint <span className="text-white font-semibold">WHITE</span> areas where you want to edit. 
                <span className="text-black bg-gray-300 px-1 rounded">BLACK</span> areas will remain unchanged.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}