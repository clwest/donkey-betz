import { useState, useRef, useEffect } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { 
  VideoCameraIcon, 
  PlayIcon, 
  PhotoIcon,
  ClockIcon,
  ArrowDownTrayIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  SparklesIcon,
  SpeakerWaveIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { toast } from 'sonner';
import { contentService } from '../../../services/content.service';
import { galleryService } from '../../../services/gallery.service';
import { API_CONFIG, buildApiUrl } from '../../../config/api.config';
// import { voiceService } from '../../../services/voice.service'; // TODO: Enable when API is ready

interface VideoTask {
  id: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'SUCCESS' | 'FAILED' | 'processing' | 'completed' | 'failed';
  progress?: number;
  video_url?: string;
  created_at: string;
}

export function VideoGenerator() {
  const [mode, setMode] = useState<'text2video' | 'image2video'>('text2video');
  const [prompt, setPrompt] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState('');
  const [selectedGalleryImage, setSelectedGalleryImage] = useState<any>(null);
  const [duration, setDuration] = useState(5);
  const [style, setStyle] = useState('cinematic');
  const [quality, setQuality] = useState<'gen3a_turbo' | 'gen3a'>('gen3a_turbo');
  const [motion, setMotion] = useState('');
  const [enhancePrompt, setEnhancePrompt] = useState(true);
  const [enhancementLevel, setEnhancementLevel] = useState<'basic' | 'advanced' | 'expert'>('advanced');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentTask, setCurrentTask] = useState<VideoTask | null>(null);
  const [generatedVideos, setGeneratedVideos] = useState<VideoTask[]>([]);
  const [showGalleryModal, setShowGalleryModal] = useState(false);
  const [galleryImages, setGalleryImages] = useState<any[]>([]);
  const [galleryLoading, setGalleryLoading] = useState(false);
  const [useImageStyles, setUseImageStyles] = useState(false);
  const [imageStyles, setImageStyles] = useState<any[]>([]);
  const [selectedImageStyle, setSelectedImageStyle] = useState<string>('');
  const [includeVoiceover, setIncludeVoiceover] = useState(false);
  const [voiceoverScript, setVoiceoverScript] = useState('');
  const [selectedVoice, setSelectedVoice] = useState('default');
  const [voiceStyle, setVoiceStyle] = useState<'professional' | 'conversational' | 'narrative'>('narrative');
  const [isGeneratingVoice, setIsGeneratingVoice] = useState(false);
  const [voiceoverUrl, setVoiceoverUrl] = useState<string | null>(null);
  const [availableVoices, setAvailableVoices] = useState<any[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const styles = [
    { id: 'cinematic', name: 'Cinematic', desc: 'Professional film-like quality', icon: '🎬' },
    { id: 'realistic', name: 'Realistic', desc: 'Natural, lifelike appearance', icon: '📷' },
    { id: 'anime', name: 'Anime', desc: 'Japanese animation style', icon: '🎌' },
    { id: 'abstract', name: 'Abstract', desc: 'Artistic and experimental', icon: '🎨' },
    { id: 'fantasy', name: 'Fantasy', desc: 'Magical and otherworldly', icon: '🐉' },
    { id: 'documentary', name: 'Documentary', desc: 'Professional documentary style', icon: '📹' },
  ];

  const motionPresets = [
    { id: '', name: 'None', desc: 'Let AI decide motion' },
    { id: 'zoom_in', name: 'Zoom In', desc: 'Gradual zoom into scene' },
    { id: 'zoom_out', name: 'Zoom Out', desc: 'Pull back from subject' },
    { id: 'pan_left', name: 'Pan Left', desc: 'Camera moves left' },
    { id: 'pan_right', name: 'Pan Right', desc: 'Camera moves right' },
    { id: 'orbit', name: 'Orbit', desc: 'Circular camera movement' },
  ];

  // Load image styles on component mount
  useEffect(() => {
    const loadImageStyles = async () => {
      try {
        const response = await contentService.getStyles();
        if (response.categories) {
          // Flatten all styles from categories
          const allStyles: any[] = [];
          Object.entries(response.categories).forEach(([category, categoryStyles]: [string, any]) => {
            categoryStyles.forEach((style: any) => {
              allStyles.push({
                ...style,
                category,
                // Add video-friendly modifications to the prompt
                videoPrompt: `${style.prompt}, smooth motion, temporal consistency, cinematic movement`
              });
            });
          });
          setImageStyles(allStyles);
        }
      } catch (error) {
        console.error('Failed to load image styles:', error);
      }
    };
    loadImageStyles();
  }, []);

  // Load available voices
  useEffect(() => {
    // Set default voices for now since API endpoints don't exist yet
    setAvailableVoices([
      { voice_id: 'default', name: 'Default Voice', gender: 'neutral' },
      { voice_id: 'professional', name: 'Professional', gender: 'male' },
      { voice_id: 'friendly', name: 'Friendly', gender: 'female' },
      { voice_id: 'narrator', name: 'Narrator', gender: 'neutral' },
    ]);
    
    // TODO: Uncomment when voice API endpoints are implemented
    // const loadVoices = async () => {
    //   try {
    //     const voices = await voiceService.getVoices();
    //     setAvailableVoices(voices);
    //   } catch (error) {
    //     console.error('Failed to load voices:', error);
    //   }
    // };
    // loadVoices();
  }, []);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type.startsWith('image/')) {
        setImageFile(file);
        toast.success('Image uploaded successfully');
      } else {
        toast.error('Please upload a valid image file');
      }
    }
  };

  const handleGenerateVoiceover = async () => {
    if (!voiceoverScript.trim()) {
      toast.error('Please enter a voiceover script');
      return;
    }

    // TODO: Implement when voice API endpoints are ready
    toast.info('Voice generation API coming soon! Your script will be included with the video request.');
    
    // For now, just show a preview of the script
    setIsGeneratingVoice(true);
    setTimeout(() => {
      toast.success('Script saved! It will be used when generating the video.');
      setIsGeneratingVoice(false);
    }, 1000);
    
    // Uncomment when API is ready:
    // try {
    //   const response = await voiceService.generateVoice({
    //     text: voiceoverScript,
    //     voice: selectedVoice,
    //     style: voiceStyle,
    //     stability: 0.5,
    //     similarity_boost: 0.75,
    //   });
    //   if (response.success && response.audio_url) {
    //     setVoiceoverUrl(response.audio_url);
    //     toast.success('Voiceover generated successfully!');
    //   }
    // } catch (error) {
    //   console.error('Voiceover generation error:', error);
    //   toast.error('Voice service temporarily unavailable');
    // }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    if (mode === 'image2video' && !imageFile && !selectedGalleryImage) {
      toast.error('Please upload an image or select from gallery for image-to-video mode');
      return;
    }

    setIsGenerating(true);
    
    try {
      let videoPrompt = prompt;
      
      // Use image style if selected
      if (useImageStyles && selectedImageStyle) {
        const imageStyle = imageStyles.find(s => s.id === selectedImageStyle);
        if (imageStyle) {
          // Combine user prompt with image style prompt
          // Replace {prompt} placeholder if it exists
          if (imageStyle.prompt.includes('{prompt}')) {
            videoPrompt = imageStyle.prompt.replace('{prompt}', prompt);
          } else {
            videoPrompt = `${prompt}, ${imageStyle.prompt}`;
          }
          // Add video-specific enhancements
          videoPrompt = `${videoPrompt}, smooth motion, temporal consistency, cinematic movement`;
        }
      } else if (style && style !== 'realistic') {
        // Use traditional video style
        videoPrompt = `${prompt}, ${style} style`;
      }

      let result;
      if (mode === 'text2video') {
        result = await contentService.generateTextToVideo({
          type: 'text_to_video',
          prompt: videoPrompt,
          duration,
          quality,
          style,
          use_memory: true,
          enhance_prompt: enhancePrompt,
          enhancement_level: enhancementLevel,
          include_voiceover: includeVoiceover,
          voiceover_script: voiceoverScript,
          voiceover_voice: selectedVoice,
          voiceover_style: voiceStyle,
        });
      } else {
        // image-to-video mode
        const hasImageSource = selectedGalleryImage || imageFile || imageUrl;
        if (!hasImageSource) {
          toast.error('Please select an image or provide a public image URL');
          setIsGenerating(false);
          return;
        }
        
        // Note: Backend will now automatically convert local images to base64
        
        // Use imageUrl if provided, otherwise use gallery image
        const finalImageUrl = imageUrl || selectedGalleryImage?.file_url;
        
        if (!finalImageUrl) {
          toast.error('Please provide a valid public image URL');
          setIsGenerating(false);
          return;
        }
        
        result = await contentService.generateImageToVideo({
          type: 'image_to_video',
          image_url: finalImageUrl,
          image_id: selectedGalleryImage?.id,
          motion_prompt: videoPrompt,
          duration,
          quality,
          enhance_prompt: enhancePrompt,
          enhancement_level: enhancementLevel,
          include_voiceover: includeVoiceover,
          voiceover_script: voiceoverScript,
          voiceover_voice: selectedVoice,
          voiceover_style: voiceStyle,
        });
      }
      
      const task: VideoTask = {
        id: result.task_id,
        status: 'PENDING',
        created_at: new Date().toISOString(),
      };

      setCurrentTask(task);
      toast.success('Video generation started! This may take 5-10 minutes.');

      // Poll for status updates
      pollTaskStatus(result.task_id);

    } catch (error: any) {
      console.error('Video generation error:', error);
      toast.error(error.userMessage || 'Failed to start video generation');
      setIsGenerating(false);
    }
  };

  const pollTaskStatus = async (taskId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const status = await contentService.getVideoStatus(taskId);
        
        // Update current task with status info
        setCurrentTask(prev => prev ? { 
          ...prev, 
          status: status.status === 'completed' ? 'SUCCESS' : 
                  status.status === 'failed' ? 'FAILED' : 
                  status.status === 'processing' ? 'IN_PROGRESS' : prev.status,
          progress: status.progress,
          video_url: status.video_url 
        } : null);

        if (status.status === 'completed' && status.video_url) {
          clearInterval(pollInterval);
          setIsGenerating(false);
          
          // Create a proper VideoTask object for the history
          const completedTask: VideoTask = {
            id: taskId,
            status: 'SUCCESS',
            video_url: status.video_url,
            created_at: new Date().toISOString(),
            progress: 100
          };
          setGeneratedVideos(prev => [completedTask, ...prev]);
          
          // Auto-save video to gallery
          try {
            const videoTitle = mode === 'text2video' 
              ? `Text-to-Video: ${prompt.substring(0, 50)}...`
              : `Image-to-Video: ${prompt.substring(0, 50)}...`;
              
            await contentService.saveVideoToGallery({
              video_url: status.video_url,
              title: videoTitle,
              description: `Generated using ${mode === 'text2video' ? 'text-to-video' : 'image-to-video'} with ${style} style`,
              category: 'uncategorized',
              tags: [style, mode, 'ai-generated'],
              original_prompt: prompt,
              motion_prompt: mode === 'image2video' ? prompt : '',
              duration: duration,
              source_type: mode === 'text2video' ? 'text_to_video' : 'image_to_video',
              metadata: {
                style: style,
                quality: quality,
                model: 'gen3a_turbo',
                taskId: taskId
              },
              is_public: false
            });
            toast.success('Video generated and saved to gallery!');
          } catch (error) {
            console.error('Failed to save video to gallery:', error);
            toast.success('Video generated successfully!');
            toast.warning('Could not save to gallery, but video is ready');
          }
        } else if (status.status === 'failed') {
          clearInterval(pollInterval);
          setIsGenerating(false);
          toast.error('Video generation failed. Please try again.');
        }
      } catch (error) {
        console.error('Error polling status:', error);
        clearInterval(pollInterval);
        setIsGenerating(false);
        toast.error('Failed to check video status');
      }
    }, 5000); // Poll every 5 seconds

    // Stop polling after 20 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
      if (isGenerating) {
        setIsGenerating(false);
        toast.error('Video generation timed out');
      }
    }, 20 * 60 * 1000);
  };

  const handleDownload = (videoUrl: string, taskId: string) => {
    const link = document.createElement('a');
    link.href = videoUrl;
    link.download = `generated-video-${taskId}.mp4`;
    link.click();
    toast.success('Video download started');
  };

  // Helper function to ensure image URLs are absolute
  const getAbsoluteImageUrl = (url: string): string => {
    if (!url) return '';
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    // Remove leading slash if present and add backend base URL
    const cleanUrl = url.startsWith('/') ? url.substring(1) : url;
    return `${API_CONFIG.BASE_URL}/${cleanUrl}`;
  };

  const loadGalleryImages = async () => {
    setGalleryLoading(true);
    try {
      // Load from all 3 image storage locations:
      // 1. SavedImage (gallery) - 10 images
      // 2. Content (old model) - 176 images  
      // 3. GeneratedContent (universal) - 0 image types
      const [galleryResponse, oldContentResponse] = await Promise.all([
        fetch(buildApiUrl('/v1/gallery/list/?limit=200'), {
          headers: {
            'Authorization': `Token 993f8273f70877e23b5c7d2f92ed30562a089fe3`,
            'Content-Type': 'application/json',
          },
        }),
        fetch(buildApiUrl('/v1/content/list/?type=image&limit=200'), {
          headers: {
            'Authorization': `Token 993f8273f70877e23b5c7d2f92ed30562a089fe3`,
            'Content-Type': 'application/json',
          },
        })
      ]);
      
      const allImages: any[] = [];
      const seenUrls = new Set<string>();
      
      // Process gallery images
      if (galleryResponse.ok) {
        const galleryData = await galleryResponse.json();
        if (galleryData.success && galleryData.images) {
          galleryData.images.forEach((img: any) => {
            const absoluteUrl = getAbsoluteImageUrl(img.image_url);
            if (!seenUrls.has(absoluteUrl)) {
              seenUrls.add(absoluteUrl);
              allImages.push({
                id: `gallery-${img.id}`,
                title: img.title,
                content_type: 'image' as const,
                file_url: absoluteUrl,
                tags: img.tags || [],
                category: img.category,
                is_favorite: false,
                is_public: img.is_public,
                created_at: img.saved_at,
                updated_at: img.saved_at,
                metadata: {
                  style: img.style_used,
                  model: 'unknown',
                  source: 'gallery'
                }
              });
            }
          });
        }
      }
      
      // Process old Content model images (175 images)
      if (oldContentResponse.ok) {
        const oldContentData = await oldContentResponse.json();
        if (oldContentData.contents) {
          oldContentData.contents.forEach((img: any) => {
            if (img.type === 'image' && img.result) {
              const absoluteUrl = getAbsoluteImageUrl(img.result);
              if (!seenUrls.has(absoluteUrl)) {
                seenUrls.add(absoluteUrl);
                allImages.push({
                  id: `old-content-${img.id}`,
                  title: img.prompt ? img.prompt.substring(0, 50) + '...' : 'Generated Image',
                  content_type: 'image' as const,
                  file_url: absoluteUrl,
                  tags: [],
                  category: img.metadata?.style || 'generated',
                  is_favorite: false,
                  is_public: false,
                  created_at: img.created_at,
                  updated_at: img.created_at,
                  metadata: {
                    style: img.metadata?.style || 'unknown',
                    model: img.metadata?.model || 'unknown',
                    source: 'old-content-model',
                    mode: img.metadata?.mode || 'unknown'
                  }
                });
              }
            }
          });
        }
      }
      
      // Sort by creation date (newest first)
      allImages.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      
      setGalleryImages(allImages);
      console.log(`Loaded ${allImages.length} total images (${seenUrls.size} unique)`);
      
    } catch (error) {
      console.error('Error loading gallery images:', error);
      toast.error('Failed to load gallery images');
    } finally {
      setGalleryLoading(false);
    }
  };

  const handleGalleryImageSelect = (image: any) => {
    // Extract the numeric ID for database lookups, or use the image URL directly
    let numericId = null;
    if (image.id.startsWith('gallery-')) {
      numericId = image.id.replace('gallery-', '');
    } else if (image.id.startsWith('old-content-')) {
      numericId = image.id.replace('old-content-', '');
    }
    
    const selectedImage = {
      ...image,
      // Store both the original ID and numeric ID for backend compatibility
      originalId: image.id,
      id: numericId,
      // Ensure we have the image URL available
      image_url: image.file_url
    };
    
    setSelectedGalleryImage(selectedImage);
    setImageFile(null); // Clear uploaded file if gallery image is selected
    setShowGalleryModal(false);
    toast.success('Image selected from gallery');
  };

  return (
    <div className="space-y-6">
      {/* Mode Selection */}
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Video Generation Mode</h3>
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => setMode('text2video')}
            className={`p-4 rounded-lg border-2 transition-all duration-200 text-left ${
              mode === 'text2video'
                ? 'border-primary-500 bg-primary-500/10'
                : 'border-dark-700 hover:border-dark-600 hover:bg-white/5'
            }`}
          >
            <VideoCameraIcon className={`h-6 w-6 mb-2 ${
              mode === 'text2video' ? 'text-primary-400' : 'text-gray-400'
            }`} />
            <div className={`font-medium ${
              mode === 'text2video' ? 'text-white' : 'text-gray-300'
            }`}>
              Text to Video
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Generate video from text description
            </div>
          </button>

          <button
            onClick={() => setMode('image2video')}
            className={`p-4 rounded-lg border-2 transition-all duration-200 text-left ${
              mode === 'image2video'
                ? 'border-primary-500 bg-primary-500/10'
                : 'border-dark-700 hover:border-dark-600 hover:bg-white/5'
            }`}
          >
            <PhotoIcon className={`h-6 w-6 mb-2 ${
              mode === 'image2video' ? 'text-primary-400' : 'text-gray-400'
            }`} />
            <div className={`font-medium ${
              mode === 'image2video' ? 'text-white' : 'text-gray-300'
            }`}>
              Image to Video
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Animate an existing image
            </div>
          </button>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Generation Panel */}
        <Card>
          <h3 className="text-lg font-semibold text-white mb-4">Generate Video</h3>
          <div className="space-y-4">
            {/* Image Upload for Image2Video */}
            {mode === 'image2video' && (
              <div className="space-y-3">
                <label className="block text-sm text-gray-400 mb-2">Source Image</label>
                
                {/* Selected Gallery Image or Uploaded Image Preview */}
                {(selectedGalleryImage || imageFile) ? (
                  <div className="space-y-3">
                    <div className="relative">
                      <img 
                        src={selectedGalleryImage?.file_url || (imageFile ? URL.createObjectURL(imageFile) : '')} 
                        alt="Selected" 
                        className="w-full h-32 object-cover rounded-lg"
                      />
                      <button
                        onClick={() => {
                          setSelectedGalleryImage(null);
                          setImageFile(null);
                        }}
                        className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs"
                      >
                        ✕
                      </button>
                    </div>
                    <p className="text-sm text-gray-400 text-center">
                      {selectedGalleryImage ? selectedGalleryImage.title || 'Gallery Image' : imageFile?.name}
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() => {
                        setShowGalleryModal(true);
                        loadGalleryImages();
                      }}
                      className="p-4 border-2 border-dashed border-primary-600 rounded-lg hover:border-primary-500 transition-colors text-center bg-primary-500/5"
                    >
                      <div>
                        <PhotoIcon className="h-6 w-6 mx-auto mb-1 text-primary-400" />
                        <p className="text-xs text-primary-300">Select from Gallery</p>
                      </div>
                    </button>
                    
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="p-4 border-2 border-dashed border-dark-700 rounded-lg hover:border-dark-600 transition-colors text-center"
                    >
                      <div>
                        <PhotoIcon className="h-6 w-6 mx-auto mb-1 text-gray-500" />
                        <p className="text-xs text-gray-400">Upload Image</p>
                      </div>
                    </button>
                  </div>
                )}
                
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
                
                {/* Public URL Input */}
                <div className="mt-4">
                  <label className="block text-sm text-gray-400 mb-2">
                    Or use a Public Image URL
                  </label>
                  <input
                    type="url"
                    className="input"
                    placeholder="https://images.unsplash.com/photo-..."
                    value={imageUrl}
                    onChange={(e) => setImageUrl(e.target.value)}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    ✅ Gallery images and public URLs both work! Local images are automatically converted.
                  </p>
                </div>
              </div>
            )}

            {/* Prompt */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                {mode === 'text2video' ? 'Video Description' : 'Motion Description'}
              </label>
              <textarea
                className="input min-h-[120px]"
                placeholder={mode === 'text2video' 
                  ? "A majestic eagle soaring over snow-capped mountains at sunset..."
                  : "Camera slowly zooms in while the subject looks up at the sky..."
                }
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
            </div>

            {/* Style Selection */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm text-gray-400">Visual Style</label>
                <button
                  type="button"
                  onClick={() => {
                    setUseImageStyles(!useImageStyles);
                    if (!useImageStyles) {
                      setSelectedImageStyle('');
                      setStyle('');
                    } else {
                      setStyle('cinematic');
                    }
                  }}
                  className="flex items-center gap-2 px-3 py-1 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors"
                >
                  <SparklesIcon className="h-4 w-4 text-primary-400" />
                  <span className="text-xs font-medium text-gray-300">
                    {useImageStyles ? 'Use 54 Image Styles' : 'Use Video Styles'}
                  </span>
                </button>
              </div>

              {!useImageStyles ? (
                // Traditional Video Styles
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {styles.map((styleOption) => (
                    <button
                      key={styleOption.id}
                      onClick={() => setStyle(styleOption.id)}
                      className={`p-3 rounded-lg border-2 transition-all duration-200 text-left ${
                        style === styleOption.id
                          ? 'border-primary-500 bg-primary-500/10'
                          : 'border-dark-700 hover:border-dark-600 hover:bg-white/5'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-lg">{styleOption.icon}</span>
                        <span className={`font-medium text-sm ${
                          style === styleOption.id ? 'text-white' : 'text-gray-300'
                        }`}>
                          {styleOption.name}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500">
                        {styleOption.desc}
                      </p>
                    </button>
                  ))}
                </div>
              ) : (
                // Image Styles adapted for Video
                <div>
                  {imageStyles.length > 0 ? (
                    <>
                      <div className="mb-2">
                        <select
                          className="input w-full"
                          value={selectedImageStyle}
                          onChange={(e) => setSelectedImageStyle(e.target.value)}
                        >
                          <option value="">Select from 54 Image Styles...</option>
                          {Object.entries(
                            imageStyles.reduce((acc: any, style) => {
                              if (!acc[style.category]) acc[style.category] = [];
                              acc[style.category].push(style);
                              return acc;
                            }, {})
                          ).map(([category, categoryStyles]: [string, any]) => (
                            <optgroup key={category} label={category}>
                              {categoryStyles.map((style: any) => (
                                <option key={style.id} value={style.id}>
                                  {style.name || style.id} - {style.description}
                                </option>
                              ))}
                            </optgroup>
                          ))}
                        </select>
                      </div>
                      {selectedImageStyle && (
                        <div className="p-3 bg-dark-700 rounded-lg">
                          <p className="text-xs text-gray-400 mb-1">Selected Style:</p>
                          <p className="text-sm text-white font-medium">
                            {imageStyles.find(s => s.id === selectedImageStyle)?.name || selectedImageStyle}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {imageStyles.find(s => s.id === selectedImageStyle)?.description}
                          </p>
                          <div className="mt-2 p-2 bg-dark-800 rounded">
                            <p className="text-xs text-gray-400 mb-1">Style will add:</p>
                            <p className="text-xs text-primary-400 italic">
                              {imageStyles.find(s => s.id === selectedImageStyle)?.preview_prompt?.substring(0, 100)}...
                            </p>
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="p-4 bg-dark-700 rounded-lg text-center">
                      <p className="text-sm text-gray-400">Loading image styles...</p>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Settings */}
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Duration</label>
                <select 
                  className="input"
                  value={duration}
                  onChange={(e) => setDuration(parseInt(e.target.value))}
                >
                  <option value={5}>5 seconds</option>
                  <option value={10}>10 seconds</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Quality</label>
                <select 
                  className="input"
                  value={quality}
                  onChange={(e) => setQuality(e.target.value as 'gen3a_turbo' | 'gen3a')}
                >
                  <option value="gen3a_turbo">Fast</option>
                  <option value="gen3a">High Quality</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Motion</label>
                <select 
                  className="input"
                  value={motion}
                  onChange={(e) => setMotion(e.target.value)}
                >
                  {motionPresets.map(preset => (
                    <option key={preset.id} value={preset.id}>{preset.name}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Intelligent Prompting Settings */}
            <div className="space-y-4 border-t border-dark-700 pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Intelligent Prompting</label>
                  <p className="text-xs text-gray-500">AI enhances your prompts for better results</p>
                </div>
                <button
                  type="button"
                  onClick={() => setEnhancePrompt(!enhancePrompt)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-dark-800 ${
                    enhancePrompt ? 'bg-primary-600' : 'bg-dark-700'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      enhancePrompt ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              {enhancePrompt && (
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Enhancement Level</label>
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      type="button"
                      onClick={() => setEnhancementLevel('basic')}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                        enhancementLevel === 'basic'
                          ? 'bg-primary-600 text-white'
                          : 'bg-dark-700 text-gray-400 hover:bg-dark-600 hover:text-gray-300'
                      }`}
                    >
                      Basic
                    </button>
                    <button
                      type="button"
                      onClick={() => setEnhancementLevel('advanced')}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                        enhancementLevel === 'advanced'
                          ? 'bg-primary-600 text-white'
                          : 'bg-dark-700 text-gray-400 hover:bg-dark-600 hover:text-gray-300'
                      }`}
                    >
                      Advanced
                    </button>
                    <button
                      type="button"
                      onClick={() => setEnhancementLevel('expert')}
                      className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                        enhancementLevel === 'expert'
                          ? 'bg-primary-600 text-white'
                          : 'bg-dark-700 text-gray-400 hover:bg-dark-600 hover:text-gray-300'
                      }`}
                    >
                      Expert
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    {enhancementLevel === 'basic' && 'Simple enhancements for clarity'}
                    {enhancementLevel === 'advanced' && 'Balanced optimization with context'}
                    {enhancementLevel === 'expert' && 'Maximum creativity and detail'}
                  </p>
                </div>
              )}
            </div>

            {/* Voiceover Settings */}
            <div className="space-y-4 border-t border-dark-700 pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Add Voiceover</label>
                  <p className="text-xs text-gray-500">Generate AI narration for your video</p>
                </div>
                <button
                  type="button"
                  onClick={() => setIncludeVoiceover(!includeVoiceover)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-dark-800 ${
                    includeVoiceover ? 'bg-primary-600' : 'bg-dark-700'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      includeVoiceover ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              {includeVoiceover && (
                <div className="space-y-4">
                  {/* Voiceover Script */}
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Narration Script</label>
                    <textarea
                      className="input min-h-[100px]"
                      placeholder="Enter the narration text for your video. This will be converted to speech and synced with your video..."
                      value={voiceoverScript}
                      onChange={(e) => setVoiceoverScript(e.target.value)}
                    />
                    <div className="mt-2 flex items-center justify-between">
                      <p className="text-xs text-gray-500">
                        {voiceoverScript.length} characters
                      </p>
                      <button
                        type="button"
                        onClick={() => {
                          // Auto-generate script based on prompt
                          const script = `Welcome to this ${style} video. ${prompt}. Let's explore this visual journey together.`;
                          setVoiceoverScript(script);
                          toast.success('Generated script from prompt');
                        }}
                        className="text-xs text-primary-400 hover:text-primary-300"
                      >
                        Generate from prompt
                      </button>
                    </div>
                  </div>

                  {/* Voice Selection */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Voice</label>
                      <select
                        className="input"
                        value={selectedVoice}
                        onChange={(e) => setSelectedVoice(e.target.value)}
                      >
                        {availableVoices.map((voice) => (
                          <option key={voice.voice_id} value={voice.voice_id}>
                            {voice.name} {voice.gender ? `(${voice.gender})` : ''}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Style</label>
                      <select
                        className="input"
                        value={voiceStyle}
                        onChange={(e) => setVoiceStyle(e.target.value as any)}
                      >
                        <option value="narrative">Narrative</option>
                        <option value="professional">Professional</option>
                        <option value="conversational">Conversational</option>
                      </select>
                    </div>
                  </div>

                  {/* Voice Preview */}
                  <div className="flex items-center gap-2">
                    <Button
                      onClick={handleGenerateVoiceover}
                      loading={isGeneratingVoice}
                      size="small"
                      variant="secondary"
                    >
                      <SpeakerWaveIcon className="h-4 w-4" />
                      {isGeneratingVoice ? 'Generating...' : 'Preview Voice'}
                    </Button>

                    {voiceoverUrl && (
                      <>
                        <audio
                          controls
                          className="flex-1"
                          src={voiceoverUrl}
                        />
                        <button
                          onClick={() => {
                            setVoiceoverUrl(null);
                            toast.info('Voiceover removed');
                          }}
                          className="text-red-400 hover:text-red-300"
                        >
                          <XMarkIcon className="h-5 w-5" />
                        </button>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Generate Button */}
            <Button 
              onClick={handleGenerate}
              loading={isGenerating}
              className="w-full"
            >
              <PlayIcon className="h-4 w-4" />
              Generate Video
            </Button>
          </div>
        </Card>

        {/* Status/Results Panel */}
        <Card>
          <h3 className="text-lg font-semibold text-white mb-4">Generation Status</h3>
          
          {/* Current Task */}
          {currentTask ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                {currentTask.status === 'PENDING' && (
                  <ClockIcon className="h-5 w-5 text-yellow-400 animate-pulse" />
                )}
                {currentTask.status === 'IN_PROGRESS' && (
                  <div className="animate-spin h-5 w-5 border-2 border-blue-400 border-t-transparent rounded-full" />
                )}
                {currentTask.status === 'SUCCESS' && (
                  <CheckCircleIcon className="h-5 w-5 text-green-400" />
                )}
                {currentTask.status === 'FAILED' && (
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
                )}
                <div>
                  <p className="text-white font-medium">
                    {currentTask.status === 'PENDING' && 'Queued for processing...'}
                    {currentTask.status === 'IN_PROGRESS' && 'Generating video...'}
                    {currentTask.status === 'SUCCESS' && 'Video ready!'}
                    {currentTask.status === 'FAILED' && 'Generation failed'}
                  </p>
                  <p className="text-xs text-gray-400">
                    Task ID: {currentTask.id}
                  </p>
                </div>
              </div>

              {currentTask.progress && (
                <div className="w-full bg-dark-700 rounded-full h-2">
                  <div 
                    className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${currentTask.progress}%` }}
                  />
                </div>
              )}

              {currentTask.video_url && (
                <div className="space-y-3">
                  <video 
                    controls 
                    className="w-full rounded-lg bg-black"
                    poster="/api/placeholder/400/225"
                  >
                    <source src={currentTask.video_url} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                  <Button
                    onClick={() => handleDownload(currentTask.video_url!, currentTask.id)}
                    variant="secondary"
                    size="sm"
                    className="w-full"
                  >
                    <ArrowDownTrayIcon className="h-4 w-4" />
                    Download Video
                  </Button>
                </div>
              )}
            </div>
          ) : generatedVideos.length > 0 ? (
            <div className="space-y-4">
              <h4 className="font-medium text-white">Recent Videos</h4>
              {generatedVideos.slice(0, 3).map(video => (
                <div key={video.id} className="space-y-2">
                  {video.video_url && (
                    <video 
                      controls 
                      className="w-full rounded-lg bg-black"
                      poster="/api/placeholder/400/225"
                    >
                      <source src={video.video_url} type="video/mp4" />
                    </video>
                  )}
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-400">
                      {new Date(video.created_at).toLocaleString()}
                    </span>
                    {video.video_url && (
                      <Button
                        onClick={() => handleDownload(video.video_url!, video.id)}
                        variant="secondary"
                        size="sm"
                      >
                        <ArrowDownTrayIcon className="h-4 w-4" />
                        Download
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <VideoCameraIcon className="h-12 w-12 mx-auto mb-2 text-gray-600" />
              <p>Generated videos will appear here</p>
              <p className="text-xs mt-1">Generation typically takes 5-10 minutes</p>
            </div>
          )}
        </Card>
      </div>

      {/* Gallery Modal */}
      {showGalleryModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-dark-800 rounded-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-dark-700">
              <h3 className="text-xl font-semibold text-white">Select Image from Gallery</h3>
              <button
                onClick={() => setShowGalleryModal(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              {galleryLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin h-8 w-8 border-2 border-primary-400 border-t-transparent rounded-full"></div>
                  <span className="ml-3 text-gray-400">Loading gallery...</span>
                </div>
              ) : galleryImages.length > 0 ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                  {galleryImages.map((image) => (
                    <button
                      key={image.id}
                      onClick={() => handleGalleryImageSelect(image)}
                      className="relative group overflow-hidden rounded-lg bg-dark-700 hover:bg-dark-600 transition-all duration-200"
                    >
                      <img
                        src={image.file_url}
                        alt={image.title || 'Gallery Image'}
                        className="w-full h-32 object-cover group-hover:scale-105 transition-transform duration-200"
                        onError={(e) => {
                          e.currentTarget.src = '/api/placeholder/200/200';
                        }}
                      />
                      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all duration-200 flex items-end">
                        <div className="p-2 w-full">
                          <p className="text-white text-xs truncate opacity-0 group-hover:opacity-100 transition-opacity">
                            {image.title || 'Untitled'}
                          </p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <PhotoIcon className="h-12 w-12 mx-auto mb-4 text-gray-600" />
                  <p className="text-gray-400 text-lg mb-2">No images in gallery</p>
                  <p className="text-gray-500 text-sm">Generate some images first to use them for video creation!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}