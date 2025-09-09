import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Animated,
  Image,
  Dimensions,
  Alert,
  Modal,
  FlatList,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { theme } from '../styles/theme';
import { PremiumButton } from '../components/common/PremiumButton';
import api, { styleMemoryService, promptingService } from '../services/api';
import { StyleRating } from '../components/StyleMemory/StyleRating';
import { StyleSuggestions } from '../components/StyleMemory/StyleSuggestions';
import { PromptEnhancer } from '../components/IntelligentPrompting/PromptEnhancer';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface GenerationType {
  id: string;
  title: string;
  icon: string;
  gradient: string[];
  type: 'text' | 'image' | 'blog' | 'social' | 'video' | 'voice';
}

const generationTypes: GenerationType[] = [
  {
    id: 'blog',
    title: 'Blog Post',
    icon: '📝',
    gradient: ['#6366F1', '#8B5CF6'],
    type: 'blog',
  },
  {
    id: 'social',
    title: 'Social Media',
    icon: '📱',
    gradient: ['#8B5CF6', '#EC4899'],
    type: 'social',
  },
  {
    id: 'image',
    title: 'AI Image',
    icon: '🎨',
    gradient: ['#EC4899', '#F43F5E'],
    type: 'image',
  },
  {
    id: 'text',
    title: 'Custom Text',
    icon: '✍️',
    gradient: ['#F43F5E', '#F97316'],
    type: 'text',
  },
  {
    id: 'video',
    title: 'AI Video',
    icon: '🎥',
    gradient: ['#F97316', '#EAB308'],
    type: 'video',
  },
  {
    id: 'voice',
    title: 'Voice Note',
    icon: '🎙️',
    gradient: ['#EAB308', '#22C55E'],
    type: 'voice',
  },
];

const visualStyles = [
  { id: 'realistic', label: 'Realistic', icon: '📷' },
  { id: 'artistic', label: 'Artistic', icon: '🎨' },
  { id: 'anime', label: 'Anime', icon: '🎌' },
  { id: 'cyberpunk', label: 'Cyberpunk', icon: '🤖' },
  { id: 'fantasy', label: 'Fantasy', icon: '🐉' },
  { id: 'minimalist', label: 'Minimalist', icon: '⬜' },
];

const videoStyles = [
  { id: 'cinematic', label: 'Cinematic', icon: '🎬', description: 'Professional film-like quality' },
  { id: 'realistic', label: 'Realistic', icon: '📷', description: 'Natural, lifelike appearance' },
  { id: 'anime', label: 'Anime', icon: '🎌', description: 'Japanese animation style' },
  { id: 'abstract', label: 'Abstract', icon: '🎨', description: 'Artistic and experimental' },
  { id: 'fantasy', label: 'Fantasy', icon: '🐉', description: 'Magical and otherworldly' },
  { id: 'documentary', label: 'Documentary', icon: '📹', description: 'Professional documentary style' },
];

const socialPlatforms = [
  { id: 'twitter', label: 'Twitter', icon: '𝕏', limit: 280 },
  { id: 'linkedin', label: 'LinkedIn', icon: '💼', limit: 3000 },
  { id: 'instagram', label: 'Instagram', icon: '📸', limit: 2200 },
  { id: 'facebook', label: 'Facebook', icon: '👤', limit: 63206 },
];

export default function StudioScreen({ navigation }: any) {
  const [selectedType, setSelectedType] = useState<GenerationType>(generationTypes[0]);
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<any>(null);
  const [selectedStyle, setSelectedStyle] = useState('realistic');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['twitter']);
  const [tone, setTone] = useState<'professional' | 'casual' | 'technical' | 'marketing'>('professional');
  
  // Video-specific state
  const [videoMode, setVideoMode] = useState<'text-to-video' | 'image-to-video'>('text-to-video');
  const [videoDuration, setVideoDuration] = useState<5 | 10>(5);
  const [videoQuality, setVideoQuality] = useState<'gen3a_turbo' | 'gen3a'>('gen3a_turbo');
  const [videoProgress, setVideoProgress] = useState(0);
  const [currentVideoTaskId, setCurrentVideoTaskId] = useState<string | null>(null);
  const [selectedVideoStyle, setSelectedVideoStyle] = useState('cinematic');
  const [selectedImage, setSelectedImage] = useState<any>(null);
  const [showGalleryModal, setShowGalleryModal] = useState(false);
  const [galleryImages, setGalleryImages] = useState<any[]>([]);
  const [galleryLoading, setGalleryLoading] = useState(false);
  const [blogLength, setBlogLength] = useState<'short' | 'medium' | 'long'>('medium');
  const [enhancePrompt, setEnhancePrompt] = useState(true);
  const [enhancementLevel, setEnhancementLevel] = useState<'basic' | 'advanced' | 'expert'>('advanced');
  const [includeVoiceover, setIncludeVoiceover] = useState(false);
  const [voiceoverScript, setVoiceoverScript] = useState('');
  const [selectedVoiceStyle, setSelectedVoiceStyle] = useState<'narrative' | 'professional' | 'conversational'>('narrative');
  
  // Style Memory state
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [currentImageId, setCurrentImageId] = useState<string | null>(null);
  const [showStyleSuggestions, setShowStyleSuggestions] = useState(true);

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }),
      Animated.spring(slideAnim, {
        toValue: 0,
        speed: 12,
        bounciness: 8,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      Alert.alert('Error', 'Please enter a prompt or topic');
      return;
    }

    setIsGenerating(true);
    setGeneratedContent(null);

    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }

    try {
      let response;

      switch (selectedType.type) {
        case 'blog':
          response = await api.generateBlog({
            topic: prompt,
            tone,
            length: blogLength,
            include_meta: true,
            include_images: true,
          });
          break;

        case 'social':
          response = await api.generateSocialMedia({
            topic: prompt,
            platforms: selectedPlatforms as any,
            tone,
            variations_per_platform: 3,
            include_hashtags: true,
            include_emojis: true,
          });
          break;

        case 'image':
          response = await api.generateContent({
            prompt,
            type: 'image',
            style: selectedStyle,
            width: 1024,
            height: 1024,
            cfg_scale: 7,
            steps: 30,
          });
          break;

        case 'text':
          response = await api.generateContent({
            prompt,
            type: 'text',
            temperature: 0.7,
            max_tokens: 500,
          });
          break;

        case 'video':
          let videoPrompt = prompt;
          
          // Add style to prompt for better results
          if (selectedVideoStyle && selectedVideoStyle !== 'realistic') {
            videoPrompt = `${prompt}, ${selectedVideoStyle} style`;
          }
          
          if (videoMode === 'text-to-video') {
            response = await api.generateTextToVideo({
              prompt: videoPrompt,
              duration: videoDuration,
              quality: videoQuality,
              use_memory: true,
              enhance_prompt: enhancePrompt,
              enhancement_level: enhancementLevel,
              include_voiceover: includeVoiceover,
              voiceover_script: voiceoverScript || videoPrompt,
              voiceover_style: selectedVoiceStyle,
            });
          } else {
            // image-to-video mode
            if (!selectedImage) {
              Alert.alert('Image Required', 'Please select an image from the gallery for image-to-video generation.');
              setIsGenerating(false);
              return;
            }
            
            response = await api.generateImageToVideo({
              image_url: selectedImage.url || selectedImage.image_url,
              image_id: selectedImage.id,
              motion_prompt: videoPrompt,
              duration: videoDuration,
              enhance_prompt: enhancePrompt,
              enhancement_level: enhancementLevel,
              include_voiceover: includeVoiceover,
              voiceover_script: voiceoverScript || videoPrompt,
              voiceover_style: selectedVoiceStyle,
            });
          }
          
          if (response.success && response.data?.task_id) {
            setCurrentVideoTaskId(response.data.task_id);
            startVideoProgressTracking(response.data.task_id);
          }
          break;
      }

      if (response.success) {
        setGeneratedContent(response.data);
        if (Platform.OS !== 'web') {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        }
      } else {
        Alert.alert('Error', response.error || 'Failed to generate content');
      }
    } catch (error) {
      console.error('Generation error:', error);
      Alert.alert('Error', 'Failed to generate content. Please try again.');
    } finally {
      if (selectedType.type !== 'video') {
        setIsGenerating(false);
      }
    }
  };

  const startVideoProgressTracking = (taskId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await api.getVideoStatus(taskId);
        if (response.success && response.data) {
          const { status, progress, video_url } = response.data;
          
          if (progress !== undefined) {
            setVideoProgress(progress);
          }
          
          if (status === 'completed' && video_url) {
            setGeneratedContent({ video_url });
            setIsGenerating(false);
            setCurrentVideoTaskId(null);
            clearInterval(pollInterval);
            if (Platform.OS !== 'web') {
              Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
            }
          } else if (status === 'failed') {
            Alert.alert('Error', 'Video generation failed. Please try again.');
            setIsGenerating(false);
            setCurrentVideoTaskId(null);
            clearInterval(pollInterval);
          }
        }
      } catch (error) {
        console.error('Video status check error:', error);
      }
    }, 2000); // Check every 2 seconds

    // Clean up after 2 minutes max
    setTimeout(() => {
      clearInterval(pollInterval);
      if (currentVideoTaskId === taskId) {
        setIsGenerating(false);
        setCurrentVideoTaskId(null);
        Alert.alert('Timeout', 'Video generation is taking longer than expected. It may still complete in the background.');
      }
    }, 120000);
  };

  const loadGalleryImages = async () => {
    setGalleryLoading(true);
    try {
      const response = await api.getGalleryImages({ limit: 50 });
      if (response.success && response.data?.images) {
        setGalleryImages(response.data.images);
      }
    } catch (error) {
      console.error('Error loading gallery images:', error);
      Alert.alert('Error', 'Failed to load gallery images');
    } finally {
      setGalleryLoading(false);
    }
  };

  const handleImageSelect = (image: any) => {
    setSelectedImage(image);
    setShowGalleryModal(false);
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
  };

  const togglePlatform = (platformId: string) => {
    setSelectedPlatforms(prev => {
      if (prev.includes(platformId)) {
        return prev.filter(p => p !== platformId);
      }
      return [...prev, platformId];
    });
  };

  const renderContent = () => {
    if (!generatedContent) return null;

    if (selectedType.type === 'video' && generatedContent.video_url) {
      return (
        <Animated.View
          style={[
            styles.resultContainer,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }],
            },
          ]}
        >
          <View style={styles.videoContainer}>
            <Text style={styles.videoLabel}>Generated Video</Text>
            <TouchableOpacity
              style={styles.videoPlayButton}
              onPress={() => {
                // Open video in external player or full screen
                Alert.alert('Video Ready', 'Video generated successfully!', [
                  { text: 'OK' }
                ]);
              }}
            >
              <Text style={styles.videoPlayIcon}>▶️</Text>
              <Text style={styles.videoPlayText}>Play Video</Text>
            </TouchableOpacity>
            <Text style={styles.videoUrl} numberOfLines={1}>
              {generatedContent.video_url}
            </Text>
          </View>
          <TouchableOpacity
            style={styles.saveButton}
            onPress={() => {
              if (Platform.OS !== 'web') {
                Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
              }
              Alert.alert('Success', 'Video saved to gallery!');
            }}
          >
            <Text style={styles.saveButtonText}>Save to Gallery</Text>
          </TouchableOpacity>
        </Animated.View>
      );
    }

    if (selectedType.type === 'image' && generatedContent.image_url) {
      return (
        <Animated.View
          style={[
            styles.resultContainer,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }],
            },
          ]}
        >
          <Image
            source={{ uri: generatedContent.image_url }}
            style={styles.generatedImage}
            resizeMode="cover"
          />
          
          {/* Style Memory Actions */}
          <View style={styles.styleMemoryActions}>
            <TouchableOpacity
              style={styles.rateButton}
              onPress={() => {
                setCurrentImageId(generatedContent.id || Date.now().toString());
                setShowRatingModal(true);
              }}
            >
              <Text style={styles.rateButtonIcon}>⭐</Text>
              <Text style={styles.rateButtonText}>Rate Style</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.quickActionButton}
              onPress={async () => {
                Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
                await styleMemoryService.captureInteraction(
                  generatedContent.id || Date.now().toString(),
                  'love' as any
                );
                Alert.alert('✨', 'Loved! AI will remember this style.');
              }}
            >
              <Text style={styles.quickActionIcon}>❤️</Text>
              <Text style={styles.quickActionText}>Love (L)</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.quickActionButton}
              onPress={async () => {
                Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                const result = await styleMemoryService.generateSimilar({
                  content_id: generatedContent.id || Date.now().toString(),
                  variations: 1,
                } as any);
                Alert.alert('🎨', 'Generating similar style...');
              }}
            >
              <Text style={styles.quickActionIcon}>🔄</Text>
              <Text style={styles.quickActionText}>Similar (S)</Text>
            </TouchableOpacity>
          </View>
          
          <TouchableOpacity
            style={styles.saveButton}
            onPress={() => navigation.navigate('Gallery')}
          >
            <Text style={styles.saveButtonText}>Save to Gallery</Text>
          </TouchableOpacity>
        </Animated.View>
      );
    }

    return (
      <Animated.View
        style={[
          styles.resultContainer,
          {
            opacity: fadeAnim,
            transform: [{ translateY: slideAnim }],
          },
        ]}
      >
        <ScrollView style={styles.contentScroll}>
          <Text style={styles.generatedText}>
            {generatedContent.content || generatedContent.text || JSON.stringify(generatedContent, null, 2)}
          </Text>
        </ScrollView>
        <TouchableOpacity
          style={styles.saveButton}
          onPress={() => navigation.navigate('Gallery')}
        >
          <Text style={styles.saveButtonText}>Save Content</Text>
        </TouchableOpacity>
      </Animated.View>
    );
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#0A0A0F', '#1C1C25']}
        style={StyleSheet.absoluteFillObject}
      />
      
      <SafeAreaView style={styles.safeArea}>
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardView}
        >
          <ScrollView
            showsVerticalScrollIndicator={false}
            contentContainerStyle={styles.scrollContent}
          >
            <Animated.View
              style={[
                styles.header,
                {
                  opacity: fadeAnim,
                  transform: [{ translateY: slideAnim }],
                },
              ]}
            >
              <Text style={styles.screenTitle}>Donkey Betz Studio</Text>
              <Text style={styles.screenSubtitle}>Create Premium Content</Text>
            </Animated.View>

            {/* Generation Type Selector */}
            <View style={styles.typeSelector}>
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={styles.typeSelectorContent}
              >
                {generationTypes.map((type) => (
                  <TouchableOpacity
                    key={type.id}
                    style={[
                      styles.typeCard,
                      selectedType.id === type.id && styles.typeCardActive,
                    ]}
                    onPress={() => {
                      setSelectedType(type);
                      if (Platform.OS !== 'web') {
                        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                      }
                    }}
                  >
                    <LinearGradient
                      colors={type.gradient}
                      style={styles.typeGradient}
                    >
                      <Text style={styles.typeIcon}>{type.icon}</Text>
                      <Text style={styles.typeTitle}>{type.title}</Text>
                    </LinearGradient>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>

            {/* Style Suggestions - Only for image generation */}
            {selectedType.type === 'image' && showStyleSuggestions && (
              <StyleSuggestions
                prompt={prompt}
                onSelectStyle={(style) => {
                  setSelectedStyle(style);
                  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                }}
                compact
              />
            )}

            {/* Intelligent Prompting - For all content types */}
            {prompt.trim() && (
              <PromptEnhancer
                prompt={prompt}
                contentType={selectedType.type as any}
                onEnhanced={(enhancedPrompt) => {
                  setPrompt(enhancedPrompt);
                  Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
                }}
                compact
              />
            )}

            {/* Input Section */}
            <View style={styles.inputSection}>
              <BlurView intensity={30} tint="dark" style={styles.blurCard}>
                <View style={styles.inputContainer}>
                  <TextInput
                    style={styles.promptInput}
                    placeholder={`Enter your ${selectedType.type === 'blog' ? 'topic' : 'prompt'}...`}
                    placeholderTextColor={theme.colors.text.tertiary}
                    value={prompt}
                    onChangeText={setPrompt}
                    multiline
                    maxLength={500}
                  />
                  <Text style={styles.charCount}>{prompt.length}/500</Text>
                </View>
              </BlurView>
            </View>

            {/* Options based on type */}
            {selectedType.type === 'image' && (
              <View style={styles.optionsSection}>
                <Text style={styles.optionTitle}>Visual Style</Text>
                <ScrollView
                  horizontal
                  showsHorizontalScrollIndicator={false}
                  style={styles.styleScroll}
                >
                  {visualStyles.map((style) => (
                    <TouchableOpacity
                      key={style.id}
                      style={[
                        styles.styleChip,
                        selectedStyle === style.id && styles.styleChipActive,
                      ]}
                      onPress={() => setSelectedStyle(style.id)}
                    >
                      <Text style={styles.styleIcon}>{style.icon}</Text>
                      <Text
                        style={[
                          styles.styleLabel,
                          selectedStyle === style.id && styles.styleLabelActive,
                        ]}
                      >
                        {style.label}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </ScrollView>
              </View>
            )}

            {selectedType.type === 'video' && (
              <View style={styles.optionsSection}>
                <Text style={styles.optionTitle}>Video Settings</Text>
                
                {/* Video Mode Selection */}
                <View style={styles.videoModeContainer}>
                  <TouchableOpacity
                    style={[
                      styles.videoModeButton,
                      videoMode === 'text-to-video' && styles.videoModeButtonActive,
                    ]}
                    onPress={() => setVideoMode('text-to-video')}
                  >
                    <Text style={[
                      styles.videoModeText,
                      videoMode === 'text-to-video' && styles.videoModeTextActive,
                    ]}>🎬 Text to Video</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[
                      styles.videoModeButton,
                      videoMode === 'image-to-video' && styles.videoModeButtonActive,
                    ]}
                    onPress={() => setVideoMode('image-to-video')}
                  >
                    <Text style={[
                      styles.videoModeText,
                      videoMode === 'image-to-video' && styles.videoModeTextActive,
                    ]}>📸 Image to Video</Text>
                  </TouchableOpacity>
                </View>

                {/* Video Style Selection */}
                <Text style={styles.optionTitle}>Video Style</Text>
                <ScrollView
                  horizontal
                  showsHorizontalScrollIndicator={false}
                  style={styles.styleScroll}
                  contentContainerStyle={styles.styleScrollContent}
                >
                  {videoStyles.map((style) => (
                    <TouchableOpacity
                      key={style.id}
                      style={[
                        styles.videoStyleChip,
                        selectedVideoStyle === style.id && styles.videoStyleChipActive,
                      ]}
                      onPress={() => {
                        setSelectedVideoStyle(style.id);
                        if (Platform.OS !== 'web') {
                          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                        }
                      }}
                    >
                      <Text style={styles.styleIcon}>{style.icon}</Text>
                      <Text
                        style={[
                          styles.videoStyleLabel,
                          selectedVideoStyle === style.id && styles.videoStyleLabelActive,
                        ]}
                      >
                        {style.label}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </ScrollView>

                {/* Image Selection for Image-to-Video Mode */}
                {videoMode === 'image-to-video' && (
                  <View style={styles.imageSelectionContainer}>
                    <Text style={styles.optionTitle}>Source Image</Text>
                    {selectedImage ? (
                      <View style={styles.selectedImageContainer}>
                        <Image
                          source={{ uri: selectedImage.url || selectedImage.image_url }}
                          style={styles.selectedImagePreview}
                          resizeMode="cover"
                        />
                        <View style={styles.selectedImageActions}>
                          <TouchableOpacity
                            style={styles.changeImageButton}
                            onPress={() => {
                              setShowGalleryModal(true);
                              loadGalleryImages();
                            }}
                          >
                            <Text style={styles.changeImageText}>Change Image</Text>
                          </TouchableOpacity>
                          <TouchableOpacity
                            style={styles.removeImageButton}
                            onPress={() => setSelectedImage(null)}
                          >
                            <Text style={styles.removeImageText}>Remove</Text>
                          </TouchableOpacity>
                        </View>
                      </View>
                    ) : (
                      <TouchableOpacity
                        style={styles.selectImageButton}
                        onPress={() => {
                          setShowGalleryModal(true);
                          loadGalleryImages();
                        }}
                      >
                        <Text style={styles.selectImageIcon}>🖼️</Text>
                        <Text style={styles.selectImageText}>Select Image from Gallery</Text>
                      </TouchableOpacity>
                    )}
                  </View>
                )}

                {/* Video Duration */}
                <View style={styles.videoOptionRow}>
                  <Text style={styles.videoOptionLabel}>Duration:</Text>
                  <View style={styles.videoDurationContainer}>
                    <TouchableOpacity
                      style={[
                        styles.videoDurationButton,
                        videoDuration === 5 && styles.videoDurationButtonActive,
                      ]}
                      onPress={() => setVideoDuration(5)}
                    >
                      <Text style={[
                        styles.videoDurationText,
                        videoDuration === 5 && styles.videoDurationTextActive,
                      ]}>5s</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={[
                        styles.videoDurationButton,
                        videoDuration === 10 && styles.videoDurationButtonActive,
                      ]}
                      onPress={() => setVideoDuration(10)}
                    >
                      <Text style={[
                        styles.videoDurationText,
                        videoDuration === 10 && styles.videoDurationTextActive,
                      ]}>10s</Text>
                    </TouchableOpacity>
                  </View>
                </View>

                {/* Video Quality */}
                <View style={styles.videoOptionRow}>
                  <Text style={styles.videoOptionLabel}>Quality:</Text>
                  <View style={styles.videoQualityContainer}>
                    <TouchableOpacity
                      style={[
                        styles.videoQualityButton,
                        videoQuality === 'gen3a_turbo' && styles.videoQualityButtonActive,
                      ]}
                      onPress={() => setVideoQuality('gen3a_turbo')}
                    >
                      <Text style={[
                        styles.videoQualityText,
                        videoQuality === 'gen3a_turbo' && styles.videoQualityTextActive,
                      ]}>Fast</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={[
                        styles.videoQualityButton,
                        videoQuality === 'gen3a' && styles.videoQualityButtonActive,
                      ]}
                      onPress={() => setVideoQuality('gen3a')}
                    >
                      <Text style={[
                        styles.videoQualityText,
                        videoQuality === 'gen3a' && styles.videoQualityTextActive,
                      ]}>High Quality</Text>
                    </TouchableOpacity>
                  </View>
                </View>

                {/* Intelligent Prompting */}
                <View style={styles.enhancementSection}>
                  <View style={styles.enhancementHeader}>
                    <View>
                      <Text style={styles.videoOptionLabel}>Intelligent Prompting</Text>
                      <Text style={styles.enhancementDescription}>AI enhances your prompts for better results</Text>
                    </View>
                    <TouchableOpacity
                      style={[
                        styles.enhancementToggle,
                        enhancePrompt && styles.enhancementToggleActive,
                      ]}
                      onPress={() => {
                        setEnhancePrompt(!enhancePrompt);
                        if (Platform.OS !== 'web') {
                          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                        }
                      }}
                    >
                      <View style={[
                        styles.enhancementToggleThumb,
                        enhancePrompt && styles.enhancementToggleThumbActive,
                      ]} />
                    </TouchableOpacity>
                  </View>
                  
                  {enhancePrompt && (
                    <View style={styles.enhancementLevelContainer}>
                      <Text style={styles.enhancementLevelLabel}>Enhancement Level:</Text>
                      <View style={styles.enhancementLevelButtons}>
                        <TouchableOpacity
                          style={[
                            styles.enhancementLevelButton,
                            enhancementLevel === 'basic' && styles.enhancementLevelButtonActive,
                          ]}
                          onPress={() => setEnhancementLevel('basic')}
                        >
                          <Text style={[
                            styles.enhancementLevelText,
                            enhancementLevel === 'basic' && styles.enhancementLevelTextActive,
                          ]}>Basic</Text>
                        </TouchableOpacity>
                        <TouchableOpacity
                          style={[
                            styles.enhancementLevelButton,
                            enhancementLevel === 'advanced' && styles.enhancementLevelButtonActive,
                          ]}
                          onPress={() => setEnhancementLevel('advanced')}
                        >
                          <Text style={[
                            styles.enhancementLevelText,
                            enhancementLevel === 'advanced' && styles.enhancementLevelTextActive,
                          ]}>Advanced</Text>
                        </TouchableOpacity>
                        <TouchableOpacity
                          style={[
                            styles.enhancementLevelButton,
                            enhancementLevel === 'expert' && styles.enhancementLevelButtonActive,
                          ]}
                          onPress={() => setEnhancementLevel('expert')}
                        >
                          <Text style={[
                            styles.enhancementLevelText,
                            enhancementLevel === 'expert' && styles.enhancementLevelTextActive,
                          ]}>Expert</Text>
                        </TouchableOpacity>
                      </View>
                      <Text style={styles.enhancementHint}>
                        {enhancementLevel === 'basic' && 'Simple enhancements for clarity'}
                        {enhancementLevel === 'advanced' && 'Balanced optimization with context'}
                        {enhancementLevel === 'expert' && 'Maximum creativity and detail'}
                      </Text>
                    </View>
                  )}
                </View>

                {/* Voiceover Settings */}
                <View style={styles.voiceoverSection}>
                  <View style={styles.voiceoverHeader}>
                    <View style={styles.voiceoverInfo}>
                      <Text style={styles.videoOptionLabel}>Add Voiceover</Text>
                      <Text style={styles.voiceoverDescription}>AI narration for your video</Text>
                    </View>
                    <TouchableOpacity
                      style={[
                        styles.voiceoverToggle,
                        includeVoiceover && styles.voiceoverToggleActive,
                      ]}
                      onPress={() => {
                        setIncludeVoiceover(!includeVoiceover);
                        if (Platform.OS !== 'web') {
                          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                        }
                      }}
                    >
                      <View style={[
                        styles.voiceoverToggleThumb,
                        includeVoiceover && styles.voiceoverToggleThumbActive,
                      ]} />
                    </TouchableOpacity>
                  </View>
                  
                  {includeVoiceover && (
                    <View style={styles.voiceoverOptions}>
                      <TextInput
                        style={[styles.input, styles.voiceoverInput]}
                        placeholder="Enter narration script or it will be auto-generated from your prompt..."
                        placeholderTextColor={theme.colors.text.tertiary}
                        value={voiceoverScript}
                        onChangeText={setVoiceoverScript}
                        multiline
                        numberOfLines={3}
                      />
                      <View style={styles.voiceoverStyleButtons}>
                        <TouchableOpacity
                          style={[
                            styles.voiceoverStyleButton,
                            selectedVoiceStyle === 'narrative' && styles.voiceoverStyleButtonActive,
                          ]}
                          onPress={() => setSelectedVoiceStyle('narrative')}
                        >
                          <Text style={[
                            styles.voiceoverStyleText,
                            selectedVoiceStyle === 'narrative' && styles.voiceoverStyleTextActive,
                          ]}>📖 Narrative</Text>
                        </TouchableOpacity>
                        <TouchableOpacity
                          style={[
                            styles.voiceoverStyleButton,
                            selectedVoiceStyle === 'professional' && styles.voiceoverStyleButtonActive,
                          ]}
                          onPress={() => setSelectedVoiceStyle('professional')}
                        >
                          <Text style={[
                            styles.voiceoverStyleText,
                            selectedVoiceStyle === 'professional' && styles.voiceoverStyleTextActive,
                          ]}>💼 Professional</Text>
                        </TouchableOpacity>
                        <TouchableOpacity
                          style={[
                            styles.voiceoverStyleButton,
                            selectedVoiceStyle === 'conversational' && styles.voiceoverStyleButtonActive,
                          ]}
                          onPress={() => setSelectedVoiceStyle('conversational')}
                        >
                          <Text style={[
                            styles.voiceoverStyleText,
                            selectedVoiceStyle === 'conversational' && styles.voiceoverStyleTextActive,
                          ]}>💬 Conversational</Text>
                        </TouchableOpacity>
                      </View>
                    </View>
                  )}
                </View>

                {/* Video Progress */}
                {isGenerating && selectedType.type === 'video' && (
                  <View style={styles.videoProgressContainer}>
                    <Text style={styles.videoProgressLabel}>Generating Video... {Math.round(videoProgress)}%</Text>
                    <View style={styles.videoProgressBar}>
                      <View style={[styles.videoProgressFill, { width: `${videoProgress}%` }]} />
                    </View>
                  </View>
                )}
              </View>
            )}

            {selectedType.type === 'voice' && (
              <View style={styles.optionsSection}>
                <Text style={styles.optionTitle}>Voice Recording</Text>
                <View style={styles.voiceContainer}>
                  <TouchableOpacity
                    style={[styles.voiceButton, isGenerating && styles.voiceButtonRecording]}
                    onPress={() => {
                      Alert.alert(
                        'Voice Recording',
                        'Voice recording is currently available in the web version. Please use the web app to record voice notes.',
                        [{ text: 'OK' }]
                      );
                    }}
                  >
                    <Text style={styles.voiceButtonIcon}>🎙️</Text>
                    <Text style={styles.voiceButtonText}>
                      {isGenerating ? 'Recording...' : 'Tap to Record'}
                    </Text>
                  </TouchableOpacity>
                  <Text style={styles.voiceHelpText}>
                    Record your voice to create transcripts, notes, or content
                  </Text>
                </View>
              </View>
            )}

            {selectedType.type === 'social' && (
              <View style={styles.optionsSection}>
                <Text style={styles.optionTitle}>Platforms</Text>
                <View style={styles.platformGrid}>
                  {socialPlatforms.map((platform) => (
                    <TouchableOpacity
                      key={platform.id}
                      style={[
                        styles.platformChip,
                        selectedPlatforms.includes(platform.id) && styles.platformChipActive,
                      ]}
                      onPress={() => togglePlatform(platform.id)}
                    >
                      <Text style={styles.platformIcon}>{platform.icon}</Text>
                      <Text
                        style={[
                          styles.platformLabel,
                          selectedPlatforms.includes(platform.id) && styles.platformLabelActive,
                        ]}
                      >
                        {platform.label}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            )}

            {selectedType.type === 'blog' && (
              <View style={styles.optionsSection}>
                <Text style={styles.optionTitle}>Blog Settings</Text>
                <View style={styles.blogOptions}>
                  <View style={styles.optionRow}>
                    <Text style={styles.optionLabel}>Tone:</Text>
                    <View style={styles.toneButtons}>
                      {(['professional', 'casual', 'technical', 'marketing'] as const).map((t) => (
                        <TouchableOpacity
                          key={t}
                          style={[
                            styles.toneButton,
                            tone === t && styles.toneButtonActive,
                          ]}
                          onPress={() => setTone(t)}
                        >
                          <Text
                            style={[
                              styles.toneButtonText,
                              tone === t && styles.toneButtonTextActive,
                            ]}
                          >
                            {t.charAt(0).toUpperCase() + t.slice(1)}
                          </Text>
                        </TouchableOpacity>
                      ))}
                    </View>
                  </View>
                  <View style={styles.optionRow}>
                    <Text style={styles.optionLabel}>Length:</Text>
                    <View style={styles.toneButtons}>
                      {(['short', 'medium', 'long'] as const).map((l) => (
                        <TouchableOpacity
                          key={l}
                          style={[
                            styles.toneButton,
                            blogLength === l && styles.toneButtonActive,
                          ]}
                          onPress={() => setBlogLength(l)}
                        >
                          <Text
                            style={[
                              styles.toneButtonText,
                              blogLength === l && styles.toneButtonTextActive,
                            ]}
                          >
                            {l.charAt(0).toUpperCase() + l.slice(1)}
                          </Text>
                        </TouchableOpacity>
                      ))}
                    </View>
                  </View>
                </View>
              </View>
            )}

            {/* Generate Button */}
            <View style={styles.generateSection}>
              <PremiumButton
                title={isGenerating ? 'Generating...' : 'Generate Content'}
                onPress={handleGenerate}
                variant="primary"
                size="large"
                disabled={isGenerating || !prompt.trim()}
                glow
                icon={
                  isGenerating ? (
                    <ActivityIndicator size="small" color="#FFFFFF" />
                  ) : (
                    <Text style={{ fontSize: 20 }}>✨</Text>
                  )
                }
              />
            </View>

            {/* Generated Content */}
            {renderContent()}
          </ScrollView>
        </KeyboardAvoidingView>
      </SafeAreaView>
      
      {/* Gallery Modal */}
      <Modal
        visible={showGalleryModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowGalleryModal(false)}
      >
        <BlurView intensity={100} tint="dark" style={styles.modalContainer}>
          <SafeAreaView style={styles.modalSafeArea}>
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>Select Image</Text>
                <TouchableOpacity
                  onPress={() => setShowGalleryModal(false)}
                  style={styles.modalCloseButton}
                >
                  <Text style={styles.modalCloseText}>✕</Text>
                </TouchableOpacity>
              </View>
              
              {galleryLoading ? (
                <View style={styles.modalLoadingContainer}>
                  <ActivityIndicator size="large" color={theme.colors.primary.main} />
                  <Text style={styles.modalLoadingText}>Loading gallery...</Text>
                </View>
              ) : (
                <FlatList
                  data={galleryImages}
                  numColumns={2}
                  keyExtractor={(item) => item.id.toString()}
                  contentContainerStyle={styles.galleryGrid}
                  renderItem={({ item }) => (
                    <TouchableOpacity
                      style={styles.galleryImageContainer}
                      onPress={() => handleImageSelect(item)}
                    >
                      <Image
                        source={{ uri: item.image_url }}
                        style={styles.galleryImage}
                        resizeMode="cover"
                      />
                      <View style={styles.galleryImageOverlay}>
                        <Text style={styles.galleryImageTitle} numberOfLines={2}>
                          {item.title || 'Untitled'}
                        </Text>
                      </View>
                    </TouchableOpacity>
                  )}
                  ListEmptyComponent={
                    <View style={styles.emptyGalleryContainer}>
                      <Text style={styles.emptyGalleryIcon}>🖼️</Text>
                      <Text style={styles.emptyGalleryText}>No images in gallery</Text>
                      <Text style={styles.emptyGallerySubtext}>Generate some images first!</Text>
                    </View>
                  }
                />
              )}
            </View>
          </SafeAreaView>
        </BlurView>
      </Modal>

      {/* Style Rating Modal */}
      <Modal
        visible={showRatingModal}
        transparent
        animationType="slide"
        onRequestClose={() => setShowRatingModal(false)}
      >
        <BlurView intensity={80} tint="dark" style={StyleSheet.absoluteFillObject}>
          <SafeAreaView style={styles.modalContainer}>
            <View style={styles.modalContent}>
              <StyleRating
                contentId={currentImageId || ''}
                onRatingComplete={(rating, feedback) => {
                  setShowRatingModal(false);
                  Alert.alert(
                    '✨ Style Learned!',
                    `Your ${rating}-star rating helps improve AI suggestions.`
                  );
                }}
                onClose={() => setShowRatingModal(false)}
              />
            </View>
          </SafeAreaView>
        </BlurView>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  safeArea: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 100,
  },
  header: {
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
  },
  screenTitle: {
    ...theme.typography.headlineLarge,
    color: theme.colors.text.primary,
  },
  screenSubtitle: {
    ...theme.typography.bodyLarge,
    color: theme.colors.text.secondary,
    marginTop: 4,
  },
  typeSelector: {
    marginVertical: theme.spacing.md,
  },
  typeSelectorContent: {
    paddingHorizontal: theme.spacing.lg,
  },
  typeCard: {
    width: 100,
    height: 100,
    marginRight: theme.spacing.md,
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
  },
  typeCardActive: {
    transform: [{ scale: 1.05 }],
  },
  typeGradient: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  typeIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  typeTitle: {
    ...theme.typography.labelMedium,
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  inputSection: {
    marginHorizontal: theme.spacing.lg,
    marginVertical: theme.spacing.md,
  },
  blurCard: {
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
  },
  inputContainer: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: theme.borderRadius.lg,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    padding: theme.spacing.md,
  },
  promptInput: {
    ...theme.typography.bodyLarge,
    color: theme.colors.text.primary,
    minHeight: 100,
    textAlignVertical: 'top',
  },
  charCount: {
    ...theme.typography.labelSmall,
    color: theme.colors.text.tertiary,
    textAlign: 'right',
    marginTop: 8,
  },
  optionsSection: {
    marginVertical: theme.spacing.md,
  },
  optionTitle: {
    ...theme.typography.titleMedium,
    color: theme.colors.text.primary,
    paddingHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.md,
  },
  styleScroll: {
    paddingHorizontal: theme.spacing.lg,
  },
  styleChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.full,
    marginRight: theme.spacing.sm,
    borderWidth: 1,
    borderColor: theme.colors.border.secondary,
  },
  styleChipActive: {
    backgroundColor: theme.colors.primary.main,
    borderColor: theme.colors.primary.main,
  },
  styleIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  styleLabel: {
    ...theme.typography.labelMedium,
    color: theme.colors.text.secondary,
  },
  styleLabelActive: {
    color: '#FFFFFF',
  },
  platformGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: theme.spacing.lg,
  },
  platformChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.full,
    marginRight: theme.spacing.sm,
    marginBottom: theme.spacing.sm,
    borderWidth: 1,
    borderColor: theme.colors.border.secondary,
  },
  platformChipActive: {
    backgroundColor: theme.colors.primary.main,
    borderColor: theme.colors.primary.main,
  },
  platformIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  platformLabel: {
    ...theme.typography.labelMedium,
    color: theme.colors.text.secondary,
  },
  platformLabelActive: {
    color: '#FFFFFF',
  },
  blogOptions: {
    paddingHorizontal: theme.spacing.lg,
  },
  optionRow: {
    marginBottom: theme.spacing.md,
  },
  optionLabel: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
    marginBottom: theme.spacing.sm,
  },
  toneButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  toneButton: {
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.xs,
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.sm,
    marginRight: theme.spacing.xs,
    marginBottom: theme.spacing.xs,
    borderWidth: 1,
    borderColor: theme.colors.border.secondary,
  },
  toneButtonActive: {
    backgroundColor: theme.colors.primary.main,
    borderColor: theme.colors.primary.main,
  },
  toneButtonText: {
    ...theme.typography.labelSmall,
    color: theme.colors.text.secondary,
  },
  toneButtonTextActive: {
    color: '#FFFFFF',
  },
  generateSection: {
    paddingHorizontal: theme.spacing.lg,
    marginVertical: theme.spacing.lg,
  },
  resultContainer: {
    marginHorizontal: theme.spacing.lg,
    marginTop: theme.spacing.lg,
  },
  contentScroll: {
    maxHeight: 300,
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
  },
  generatedText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.primary,
    lineHeight: 24,
  },
  generatedImage: {
    width: '100%',
    height: SCREEN_WIDTH - theme.spacing.lg * 2,
    borderRadius: theme.borderRadius.lg,
    marginBottom: theme.spacing.md,
  },
  saveButton: {
    backgroundColor: theme.colors.success.main,
    paddingVertical: theme.spacing.md,
    borderRadius: theme.borderRadius.md,
    alignItems: 'center',
    marginTop: theme.spacing.md,
  },
  saveButtonText: {
    ...theme.typography.titleMedium,
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  // Video-specific styles
  videoContainer: {
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
  },
  videoLabel: {
    ...theme.typography.titleMedium,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.md,
    textAlign: 'center',
  },
  videoPlayButton: {
    backgroundColor: theme.colors.primary.main,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.lg,
    alignItems: 'center',
    marginBottom: theme.spacing.md,
  },
  videoPlayIcon: {
    fontSize: 32,
    marginBottom: theme.spacing.sm,
  },
  videoPlayText: {
    ...theme.typography.titleMedium,
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  videoUrl: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.tertiary,
    textAlign: 'center',
  },
  videoModeContainer: {
    flexDirection: 'row',
    marginBottom: theme.spacing.md,
  },
  videoModeButton: {
    flex: 1,
    paddingVertical: theme.spacing.md,
    paddingHorizontal: theme.spacing.sm,
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: theme.borderRadius.sm,
    marginRight: theme.spacing.xs,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: theme.colors.border.secondary,
  },
  videoModeButtonActive: {
    backgroundColor: theme.colors.primary.main,
    borderColor: theme.colors.primary.main,
  },
  videoModeText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
    textAlign: 'center',
  },
  videoModeTextActive: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  videoOptionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: theme.spacing.md,
  },
  videoOptionLabel: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.primary,
    fontWeight: '600',
  },
  videoDurationContainer: {
    flexDirection: 'row',
  },
  videoDurationButton: {
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: theme.borderRadius.sm,
    marginLeft: theme.spacing.xs,
    borderWidth: 1,
    borderColor: theme.colors.border.secondary,
  },
  videoDurationButtonActive: {
    backgroundColor: theme.colors.primary.main,
    borderColor: theme.colors.primary.main,
  },
  videoDurationText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
  },
  videoDurationTextActive: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  videoQualityContainer: {
    flexDirection: 'row',
  },
  videoQualityButton: {
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: theme.borderRadius.sm,
    marginLeft: theme.spacing.xs,
    borderWidth: 1,
    borderColor: theme.colors.border.secondary,
  },
  videoQualityButtonActive: {
    backgroundColor: theme.colors.primary.main,
    borderColor: theme.colors.primary.main,
  },
  videoQualityText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
  },
  videoQualityTextActive: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  videoProgressContainer: {
    marginTop: theme.spacing.md,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: theme.borderRadius.md,
  },
  videoProgressLabel: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.primary,
    textAlign: 'center',
    marginBottom: theme.spacing.sm,
  },
  videoProgressBar: {
    height: 4,
    backgroundColor: theme.colors.background.primary,
    borderRadius: 2,
    overflow: 'hidden',
  },
  videoProgressFill: {
    height: '100%',
    backgroundColor: theme.colors.primary.main,
    borderRadius: 2,
  },
  // Video style selection styles
  videoStyleChip: {
    alignItems: 'center',
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.md,
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.full,
    marginRight: theme.spacing.sm,
    marginBottom: theme.spacing.sm,
    borderWidth: 1,
    borderColor: theme.colors.border.secondary,
    minWidth: 80,
  },
  videoStyleChipActive: {
    backgroundColor: theme.colors.primary.main,
    borderColor: theme.colors.primary.main,
  },
  videoStyleLabel: {
    ...theme.typography.labelSmall,
    color: theme.colors.text.secondary,
    marginTop: 4,
    textAlign: 'center',
  },
  videoStyleLabelActive: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  // Image selection styles
  imageSelectionContainer: {
    marginTop: theme.spacing.md,
  },
  selectedImageContainer: {
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
  },
  selectedImagePreview: {
    width: '100%',
    height: 120,
    borderRadius: theme.borderRadius.sm,
    marginBottom: theme.spacing.md,
  },
  selectedImageActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  changeImageButton: {
    backgroundColor: theme.colors.primary.main,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.sm,
    flex: 1,
    marginRight: theme.spacing.sm,
  },
  changeImageText: {
    ...theme.typography.labelMedium,
    color: '#FFFFFF',
    textAlign: 'center',
    fontWeight: 'bold',
  },
  removeImageButton: {
    backgroundColor: theme.colors.error.main,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.sm,
    flex: 1,
    marginLeft: theme.spacing.sm,
  },
  removeImageText: {
    ...theme.typography.labelMedium,
    color: '#FFFFFF',
    textAlign: 'center',
    fontWeight: 'bold',
  },
  selectImageButton: {
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.lg,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: theme.colors.border.secondary,
    borderStyle: 'dashed',
  },
  selectImageIcon: {
    fontSize: 32,
    marginBottom: theme.spacing.sm,
  },
  selectImageText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
    textAlign: 'center',
  },
  // Gallery modal styles
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalSafeArea: {
    flex: 1,
    width: '100%',
  },
  modalContent: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
    margin: theme.spacing.lg,
    borderRadius: theme.borderRadius.xl,
    padding: theme.spacing.lg,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.lg,
    paddingBottom: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border.secondary,
  },
  modalTitle: {
    ...theme.typography.headlineSmall,
    color: theme.colors.text.primary,
    fontWeight: 'bold',
  },
  modalCloseButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: theme.colors.background.secondary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalCloseText: {
    ...theme.typography.labelLarge,
    color: theme.colors.text.secondary,
    fontWeight: 'bold',
  },
  modalLoadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalLoadingText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
    marginTop: theme.spacing.md,
  },
  galleryGrid: {
    paddingBottom: theme.spacing.lg,
  },
  galleryImageContainer: {
    flex: 1,
    margin: theme.spacing.xs,
    borderRadius: theme.borderRadius.md,
    overflow: 'hidden',
    backgroundColor: theme.colors.background.secondary,
  },
  galleryImage: {
    width: '100%',
    height: 120,
  },
  galleryImageOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    padding: theme.spacing.sm,
  },
  galleryImageTitle: {
    ...theme.typography.labelSmall,
    color: '#FFFFFF',
    fontWeight: '500',
  },
  emptyGalleryContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: theme.spacing.xl * 2,
  },
  emptyGalleryIcon: {
    fontSize: 48,
    marginBottom: theme.spacing.md,
  },
  emptyGalleryText: {
    ...theme.typography.titleMedium,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.sm,
  },
  emptyGallerySubtext: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
    textAlign: 'center',
  },
  enhancementSection: {
    marginTop: theme.spacing.md,
    paddingTop: theme.spacing.md,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border.secondary,
  },
  enhancementHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  enhancementDescription: {
    ...theme.typography.caption,
    color: theme.colors.text.secondary,
    marginTop: 2,
  },
  enhancementToggle: {
    width: 50,
    height: 28,
    borderRadius: 14,
    backgroundColor: theme.colors.background.tertiary,
    padding: 2,
    justifyContent: 'center',
  },
  enhancementToggleActive: {
    backgroundColor: theme.colors.primary.main,
  },
  enhancementToggleThumb: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#fff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  enhancementToggleThumbActive: {
    transform: [{ translateX: 22 }],
  },
  enhancementLevelContainer: {
    marginTop: theme.spacing.sm,
  },
  enhancementLevelLabel: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
    marginBottom: theme.spacing.xs,
  },
  enhancementLevelButtons: {
    flexDirection: 'row',
    gap: theme.spacing.xs,
  },
  enhancementLevelButton: {
    flex: 1,
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.md,
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: theme.borderRadius.md,
    alignItems: 'center',
  },
  enhancementLevelButtonActive: {
    backgroundColor: theme.colors.primary.main,
  },
  enhancementLevelText: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
    fontWeight: '500',
  },
  enhancementLevelTextActive: {
    color: '#fff',
  },
  enhancementHint: {
    ...theme.typography.caption,
    color: theme.colors.text.tertiary,
    marginTop: theme.spacing.xs,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  voiceoverSection: {
    marginTop: theme.spacing.md,
    paddingTop: theme.spacing.md,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border.secondary,
  },
  voiceoverHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  voiceoverInfo: {
    flex: 1,
  },
  voiceoverDescription: {
    ...theme.typography.caption,
    color: theme.colors.text.secondary,
    marginTop: 2,
  },
  voiceoverToggle: {
    width: 50,
    height: 28,
    borderRadius: 14,
    backgroundColor: theme.colors.background.tertiary,
    padding: 2,
    justifyContent: 'center',
  },
  voiceoverToggleActive: {
    backgroundColor: theme.colors.primary.main,
  },
  voiceoverToggleThumb: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#fff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 3,
  },
  voiceoverToggleThumbActive: {
    transform: [{ translateX: 22 }],
  },
  voiceoverOptions: {
    marginTop: theme.spacing.sm,
  },
  voiceoverInput: {
    minHeight: 80,
    textAlignVertical: 'top',
    marginBottom: theme.spacing.sm,
  },
  voiceoverStyleButtons: {
    flexDirection: 'row',
    gap: theme.spacing.xs,
  },
  voiceoverStyleButton: {
    flex: 1,
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.sm,
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: theme.borderRadius.md,
    alignItems: 'center',
  },
  voiceoverStyleButtonActive: {
    backgroundColor: theme.colors.primary.main,
  },
  voiceoverStyleText: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
    fontWeight: '500',
  },
  voiceoverStyleTextActive: {
    color: '#fff',
  },
  // Voice Recording Styles
  voiceContainer: {
    alignItems: 'center',
    paddingVertical: theme.spacing.xl,
  },
  voiceButton: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: theme.colors.background.tertiary,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 3,
    borderColor: theme.colors.border.secondary,
  },
  voiceButtonRecording: {
    backgroundColor: theme.colors.error.main,
    borderColor: theme.colors.error.main,
  },
  voiceButtonIcon: {
    fontSize: 40,
    marginBottom: theme.spacing.sm,
  },
  voiceButtonText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.primary,
    fontWeight: '600',
  },
  voiceHelpText: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
    marginTop: theme.spacing.lg,
    textAlign: 'center',
    paddingHorizontal: theme.spacing.xl,
  },
  // Style Memory styles
  styleMemoryActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 16,
    paddingHorizontal: 8,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border.primary,
  },
  rateButton: {
    alignItems: 'center',
    padding: 12,
    borderRadius: 12,
    backgroundColor: theme.colors.background.secondary,
    minWidth: 80,
  },
  rateButtonIcon: {
    fontSize: 24,
    marginBottom: 4,
  },
  rateButtonText: {
    fontSize: 12,
    color: theme.colors.text.secondary,
    fontWeight: '500',
  },
  quickActionButton: {
    alignItems: 'center',
    padding: 12,
    borderRadius: 12,
    backgroundColor: theme.colors.background.secondary,
    minWidth: 70,
  },
  quickActionIcon: {
    fontSize: 20,
    marginBottom: 4,
  },
  quickActionText: {
    fontSize: 11,
    color: theme.colors.text.secondary,
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    width: '90%',
    maxWidth: 400,
    backgroundColor: theme.colors.background.primary,
    borderRadius: 24,
    overflow: 'hidden',
  },
});