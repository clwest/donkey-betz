import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  RefreshControl,
  TextInput,
  Modal,
  Alert,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { theme } from '../styles/theme';
import { galleryService, contentService } from '../services/api';

const { width } = Dimensions.get('window');
const HORIZONTAL_CARD_WIDTH = 280; // Fixed width for horizontal cards
const HORIZONTAL_CARD_HEIGHT = 200; // Fixed height for horizontal cards
const CARD_WIDTH = HORIZONTAL_CARD_WIDTH; // Backward compatibility

interface ContentItem {
  id: number;
  type: 'blog' | 'social' | 'image' | 'video' | 'voice' | 'podcast' | 'ebook';
  title: string;
  preview?: string;
  content?: string;
  image_url?: string;
  video_url?: string;
  audio_url?: string;
  created_at: string;
  updated_at: string;
  word_count?: number;
  tags?: string[];
  tone?: string;
  length?: string;
  visibility?: 'public' | 'private';
  thumbnail?: string;
}

interface ContentTransformModalProps {
  visible: boolean;
  item: ContentItem | null;
  onClose: () => void;
  onTransform: (type: 'social' | 'podcast' | 'ebook', item: ContentItem) => void;
}

const ContentTransformModal: React.FC<ContentTransformModalProps> = ({
  visible,
  item,
  onClose,
  onTransform,
}) => {
  const transformOptions = [
    {
      type: 'social' as const,
      title: 'Social Media',
      icon: '#️⃣',
      description: 'Create engaging social posts',
      gradient: ['#FF6B6B', '#FF8E53'],
    },
    {
      type: 'podcast' as const,
      title: 'Podcast Script',
      icon: '🎙️',
      description: 'Generate podcast episode',
      gradient: ['#4ECDC4', '#44A08D'],
    },
    {
      type: 'ebook' as const,
      title: 'eBook Chapter',
      icon: '📖',
      description: 'Expand into book content',
      gradient: ['#9B59B6', '#8E44AD'],
    },
  ];

  return (
    <Modal visible={visible} animationType="slide" transparent>
      <BlurView intensity={50} style={styles.modalOverlay}>
        <View style={styles.transformModal}>
          <View style={styles.transformHeader}>
            <Text style={styles.transformTitle}>✨ Transform Content</Text>
            <Text style={styles.transformSubtitle}>
              Turn "{item?.title}" into:
            </Text>
            <TouchableOpacity
              style={styles.closeButton}
              onPress={onClose}
            >
              <Text style={styles.closeButtonText}>×</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.transformOptions}>
            {transformOptions.map((option) => (
              <TouchableOpacity
                key={option.type}
                style={styles.transformOption}
                onPress={() => {
                  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
                  if (item) {
                    onTransform(option.type, item);
                  }
                  onClose();
                }}
              >
                <LinearGradient
                  colors={option.gradient}
                  style={styles.transformOptionGradient}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 1 }}
                >
                  <Text style={styles.transformOptionIcon}>{option.icon}</Text>
                  <View style={styles.transformOptionText}>
                    <Text style={styles.transformOptionTitle}>{option.title}</Text>
                    <Text style={styles.transformOptionDescription}>
                      {option.description}
                    </Text>
                  </View>
                </LinearGradient>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      </BlurView>
    </Modal>
  );
};

export default function GalleryScreen() {
  const [contentItems, setContentItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'blog' | 'social' | 'image' | 'video' | 'voice'>('all');
  const [transformModalVisible, setTransformModalVisible] = useState(false);
  const [selectedItem, setSelectedItem] = useState<ContentItem | null>(null);
  const [transforming, setTransforming] = useState(false);

  const loadContent = useCallback(async () => {
    try {
      const [galleryData, blogsData, socialData] = await Promise.all([
        galleryService.listGalleryItems({ limit: 50 }),
        contentService.listBlogPosts({ limit: 50 }).catch(() => ({ blog_posts: [] })),
        contentService.listSocialPosts({ limit: 50 }).catch(() => ({ results: [] })),
      ]);

      // Combine all content types
      const items: ContentItem[] = [
        // Gallery items (images, videos, audio)
        ...(galleryData?.results || []).map((item: any) => ({
          id: item.id,
          type: item.content_type?.includes('video') ? 'video' as const : 
               item.content_type?.includes('audio') ? 'voice' as const : 'image' as const,
          title: item.title || `${item.content_type} Content`,
          preview: item.description,
          image_url: item.file_url,
          video_url: item.content_type?.includes('video') ? item.file_url : undefined,
          audio_url: item.content_type?.includes('audio') ? item.file_url : undefined,
          created_at: item.created_at,
          updated_at: item.updated_at || item.created_at,
          thumbnail: item.thumbnail_url,
        })),
        // Blog posts
        ...(blogsData?.blog_posts || []).map((item: any) => ({
          id: item.id,
          type: 'blog' as const,
          title: item.title,
          preview: item.preview,
          content: item.content,
          created_at: item.created_at,
          updated_at: item.updated_at,
          word_count: item.word_count,
          tags: item.tags,
          tone: item.tone,
          length: item.length,
        })),
        // Social media posts
        ...(socialData?.social_posts || []).map((item: any) => ({
          id: item.id,
          type: 'social' as const,
          title: `${item.platforms?.[0] || 'Social'} Post`,
          preview: item.topic,
          content: item.content,
          created_at: item.created_at,
          updated_at: item.updated_at || item.created_at,
        })),
      ];

      // Sort by updated date
      items.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
      
      setContentItems(items);
    } catch (error) {
      console.error('Failed to load content:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadContent();
  }, [loadContent]);

  const handleRefresh = () => {
    setRefreshing(true);
    loadContent();
  };

  const handleTransform = async (type: 'social' | 'podcast' | 'ebook', item: ContentItem) => {
    if (item.type !== 'blog') {
      Alert.alert('Transform', 'Only blog posts can be transformed currently.');
      return;
    }

    setTransforming(true);
    
    try {
      let result;
      
      switch (type) {
        case 'social':
          result = await contentService.generateSocialPost({
            topic: item.title || 'Transform from blog content',
            content: item.content || item.preview || '',
            platform: 'multiple',
            tone: item.tone || 'professional',
          });
          break;
        case 'podcast':
          // For now, create a simple podcast transformation
          result = await contentService.generateSocialPost({
            topic: `🎙️ PODCAST: ${item.title}`,
            content: `${item.content || item.preview || ''}`,
            platform: 'twitter',
            tone: item.tone || 'professional',
          });
          break;
        case 'ebook':
          // For now, create a simple ebook transformation
          result = await contentService.generateSocialPost({
            topic: `📖 EBOOK CHAPTER: ${item.title}`,
            content: `${item.content || item.preview || ''}`,
            platform: 'linkedin',
            tone: item.tone || 'professional',
          });
          break;
      }

      if (result) {
        Alert.alert('Success', `Content transformed to ${type} successfully!`);
        loadContent(); // Refresh to show new content
      }
    } catch (error) {
      console.error('Transform failed:', error);
      Alert.alert('Error', 'Failed to transform content. Please try again.');
    } finally {
      setTransforming(false);
    }
  };

  const filteredItems = contentItems.filter((item) => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.preview?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = selectedFilter === 'all' || item.type === selectedFilter;
    return matchesSearch && matchesFilter;
  });

  const getContentIcon = (type: string) => {
    switch (type) {
      case 'blog': return '📝';
      case 'social': return '#️⃣';
      case 'image': return '🖼️';
      case 'video': return '🎥';
      case 'voice': return '🎙️';
      case 'podcast': return '📻';
      case 'ebook': return '📖';
      default: return '📄';
    }
  };

  const getContentGradient = (type: string) => {
    switch (type) {
      case 'blog': return ['#667eea', '#764ba2'];
      case 'social': return ['#f093fb', '#f5576c'];
      case 'image': return ['#4facfe', '#00f2fe'];
      case 'video': return ['#fa709a', '#fee140'];
      case 'voice': return ['#a8edea', '#fed6e3'];
      case 'podcast': return ['#4facfe', '#00f2fe'];
      case 'ebook': return ['#667eea', '#764ba2'];
      default: return ['#667eea', '#764ba2'];
    }
  };

  const renderHorizontalContentCard = (item: ContentItem) => (
    <TouchableOpacity
      key={item.id}
      style={styles.horizontalContentCard}
      onPress={() => {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        // TODO: Open content viewer/editor
      }}
    >
      <LinearGradient
        colors={getContentGradient(item.type)}
        style={styles.horizontalCardGradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.cardHeader}>
          <Text style={styles.cardIcon}>{getContentIcon(item.type)}</Text>
          <TouchableOpacity
            style={styles.transformButton}
            onPress={(e) => {
              e.stopPropagation();
              if (item.type === 'blog') {
                setSelectedItem(item);
                setTransformModalVisible(true);
                Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
              }
            }}
          >
            <Text style={styles.transformButtonText}>✨</Text>
          </TouchableOpacity>
        </View>

        {item.image_url && (
          <Image source={{ uri: item.image_url }} style={styles.horizontalCardImage} />
        )}

        <View style={styles.cardContent}>
          <Text style={styles.cardTitle} numberOfLines={2}>
            {item.title}
          </Text>
          {item.preview && (
            <Text style={styles.cardPreview} numberOfLines={3}>
              {item.preview}
            </Text>
          )}
          <View style={styles.cardFooter}>
            <Text style={styles.cardType}>{item.type.toUpperCase()}</Text>
            {item.word_count && (
              <Text style={styles.cardMeta}>{item.word_count} words</Text>
            )}
          </View>
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );

  const renderVerticalContentCard = (item: ContentItem) => (
    <TouchableOpacity
      key={item.id}
      style={styles.verticalContentCard}
      onPress={() => {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        // TODO: Open content viewer/editor
      }}
    >
      <LinearGradient
        colors={getContentGradient(item.type)}
        style={styles.verticalCardGradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.cardContent}>
          <View style={styles.cardHeader}>
            <View style={styles.cardHeaderLeft}>
              <Text style={styles.cardIcon}>{getContentIcon(item.type)}</Text>
              <View style={styles.cardTitleContainer}>
                <Text style={styles.cardTitle} numberOfLines={1}>
                  {item.title}
                </Text>
                <Text style={styles.cardType}>{item.type.toUpperCase()}</Text>
              </View>
            </View>
            <TouchableOpacity
              style={styles.transformButton}
              onPress={(e) => {
                e.stopPropagation();
                if (item.type === 'blog') {
                  setSelectedItem(item);
                  setTransformModalVisible(true);
                  Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
                }
              }}
            >
              <Text style={styles.transformButtonText}>✨</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.cardBody}>
            {item.image_url && (
              <Image source={{ uri: item.image_url }} style={styles.verticalCardImage} />
            )}
            <View style={styles.cardTextContent}>
              {item.preview && (
                <Text style={styles.cardPreview} numberOfLines={3}>
                  {item.preview}
                </Text>
              )}
              <View style={styles.cardFooter}>
                {item.word_count && (
                  <Text style={styles.cardMeta}>{item.word_count} words</Text>
                )}
                <Text style={styles.cardDate}>
                  {new Date(item.updated_at).toLocaleDateString()}
                </Text>
              </View>
            </View>
          </View>
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );

  const renderContentSections = () => {
    // Group content by type
    const contentByType = filteredItems.reduce((acc, item) => {
      if (!acc[item.type]) {
        acc[item.type] = [];
      }
      acc[item.type].push(item);
      return acc;
    }, {} as Record<string, ContentItem[]>);

    // If filter is applied and only one type, show all items in horizontal scroll
    if (selectedFilter !== 'all' && Object.keys(contentByType).length === 1) {
      const items = Object.values(contentByType)[0];
      return (
        <View style={styles.sectionContainer}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              {getContentIcon(selectedFilter)} {selectedFilter.charAt(0).toUpperCase() + selectedFilter.slice(1)} Content
            </Text>
            <Text style={styles.sectionCount}>{items.length} items</Text>
          </View>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.horizontalScrollContent}
            style={styles.horizontalScroll}
          >
            {items.map(renderHorizontalContentCard)}
          </ScrollView>
        </View>
      );
    }

    // Otherwise show sections by type with horizontal scrolling cards
    return Object.entries(contentByType).map(([type, items]) => (
      <View key={type} style={styles.sectionContainer}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>
            {getContentIcon(type)} {type.charAt(0).toUpperCase() + type.slice(1)} Content
          </Text>
          <Text style={styles.sectionCount}>{items.length} items</Text>
        </View>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.horizontalScrollContent}
          style={styles.horizontalScroll}
        >
          {items.map(renderHorizontalContentCard)}
        </ScrollView>
      </View>
    ));
  };

  const renderContentCard = (item: ContentItem) => (
    <TouchableOpacity
      key={item.id}
      style={styles.contentCard}
      onPress={() => {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        // TODO: Open content viewer/editor
      }}
    >
      <LinearGradient
        colors={getContentGradient(item.type)}
        style={styles.cardGradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <View style={styles.cardHeader}>
          <Text style={styles.cardIcon}>{getContentIcon(item.type)}</Text>
          <TouchableOpacity
            style={styles.transformButton}
            onPress={(e) => {
              e.stopPropagation();
              if (item.type === 'blog') {
                setSelectedItem(item);
                setTransformModalVisible(true);
                Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
              }
            }}
          >
            <Text style={styles.transformButtonText}>✨</Text>
          </TouchableOpacity>
        </View>

        {item.image_url && (
          <Image source={{ uri: item.image_url }} style={styles.cardImage} />
        )}

        <View style={styles.cardContent}>
          <Text style={styles.cardTitle} numberOfLines={2}>
            {item.title}
          </Text>
          {item.preview && (
            <Text style={styles.cardPreview} numberOfLines={3}>
              {item.preview}
            </Text>
          )}
          <View style={styles.cardFooter}>
            <Text style={styles.cardType}>{item.type.toUpperCase()}</Text>
            {item.word_count && (
              <Text style={styles.cardMeta}>{item.word_count} words</Text>
            )}
          </View>
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary.main} />
        <Text style={styles.loadingText}>Loading your content library...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <LinearGradient
        colors={['#667eea', '#764ba2']}
        style={styles.header}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <Text style={styles.headerTitle}>📚 Content Library</Text>
        <Text style={styles.headerSubtitle}>
          {contentItems.length} items • Transform with ✨
        </Text>
      </LinearGradient>

      {/* Search and Filters */}
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search content..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholderTextColor={theme.colors.text.secondary}
        />
      </View>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.filtersContainer}
        contentContainerStyle={styles.filtersContent}
      >
        {['all', 'blog', 'social', 'image', 'video', 'voice'].map((filter) => (
          <TouchableOpacity
            key={filter}
            style={[
              styles.filterButton,
              selectedFilter === filter && styles.filterButtonActive,
            ]}
            onPress={() => {
              setSelectedFilter(filter as any);
              Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
            }}
          >
            <Text
              style={[
                styles.filterButtonText,
                selectedFilter === filter && styles.filterButtonTextActive,
              ]}
            >
              {filter.charAt(0).toUpperCase() + filter.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Content Sections */}
      <ScrollView
        style={styles.contentScroll}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
      >
        {filteredItems.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyIcon}>🎨</Text>
            <Text style={styles.emptyTitle}>No content found</Text>
            <Text style={styles.emptySubtitle}>
              {searchQuery || selectedFilter !== 'all'
                ? 'Try adjusting your search or filters'
                : 'Start creating content to build your library'}
            </Text>
          </View>
        ) : (
          <View style={styles.sectionsContainer}>
            {renderContentSections()}
          </View>
        )}
      </ScrollView>

      {/* Transform Modal */}
      <ContentTransformModal
        visible={transformModalVisible}
        item={selectedItem}
        onClose={() => setTransformModalVisible(false)}
        onTransform={handleTransform}
      />

      {/* Loading Overlay */}
      {transforming && (
        <BlurView intensity={50} style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="white" />
          <Text style={styles.loadingOverlayText}>Transforming content...</Text>
        </BlurView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background.primary,
  },
  loadingText: {
    fontSize: 16,
    color: theme.colors.text.secondary,
    marginTop: 16,
  },
  header: {
    padding: 24,
    paddingTop: 60,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  searchContainer: {
    padding: 16,
  },
  searchInput: {
    backgroundColor: theme.colors.background.secondary,
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: theme.colors.text.primary,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
  },
  filtersContainer: {
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  filtersContent: {
    gap: 8,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: theme.colors.background.secondary,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
  },
  filterButtonActive: {
    backgroundColor: theme.colors.primary.main,
    borderColor: theme.colors.primary.main,
  },
  filterButtonText: {
    fontSize: 14,
    color: theme.colors.text.secondary,
    fontWeight: '500',
  },
  filterButtonTextActive: {
    color: 'white',
  },
  contentScroll: {
    flex: 1,
  },
  sectionsContainer: {
    paddingBottom: 24,
  },
  sectionContainer: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
  },
  sectionCount: {
    fontSize: 14,
    color: theme.colors.text.secondary,
  },
  horizontalScroll: {
    paddingLeft: 16,
  },
  horizontalScrollContent: {
    paddingRight: 16,
    gap: 16,
  },
  horizontalContentCard: {
    width: HORIZONTAL_CARD_WIDTH,
    height: HORIZONTAL_CARD_HEIGHT,
    borderRadius: 16,
    overflow: 'hidden',
  },
  horizontalCardGradient: {
    flex: 1,
    padding: 16,
  },
  horizontalCardImage: {
    width: '100%',
    height: 80,
    borderRadius: 8,
    marginBottom: 8,
  },
  verticalContentList: {
    paddingHorizontal: 16,
  },
  verticalContentCard: {
    width: width - 32,
    minHeight: 120,
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 16,
  },
  verticalCardGradient: {
    flex: 1,
    padding: 16,
  },
  cardHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  cardTitleContainer: {
    marginLeft: 12,
    flex: 1,
  },
  cardBody: {
    flexDirection: 'row',
    flex: 1,
    marginTop: 12,
  },
  verticalCardImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
    marginRight: 12,
  },
  cardTextContent: {
    flex: 1,
    justifyContent: 'space-between',
  },
  cardDate: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.7)',
  },
  contentGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    gap: 16,
    paddingBottom: 24,
  },
  contentCard: {
    width: width - 32,
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 16,
  },
  cardGradient: {
    padding: 16,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardIcon: {
    fontSize: 24,
  },
  transformButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  transformButtonText: {
    fontSize: 16,
  },
  cardImage: {
    width: '100%',
    height: 100,
    borderRadius: 8,
    marginBottom: 12,
  },
  cardContent: {
    flex: 1,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  cardPreview: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: 18,
    flex: 1,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
  },
  cardType: {
    fontSize: 10,
    color: 'rgba(255, 255, 255, 0.6)',
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  cardMeta: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.7)',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 48,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 16,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    lineHeight: 22,
  },
  modalOverlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  transformModal: {
    backgroundColor: theme.colors.background.primary,
    borderRadius: 20,
    padding: 24,
    width: '100%',
    maxWidth: 400,
    maxHeight: '80%',
  },
  transformHeader: {
    alignItems: 'center',
    marginBottom: 24,
    position: 'relative',
  },
  transformTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 8,
  },
  transformSubtitle: {
    fontSize: 16,
    color: theme.colors.text.secondary,
    textAlign: 'center',
  },
  closeButton: {
    position: 'absolute',
    top: -8,
    right: -8,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: theme.colors.background.secondary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    fontSize: 20,
    color: theme.colors.text.secondary,
  },
  transformOptions: {
    gap: 12,
  },
  transformOption: {
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 12,
  },
  transformOptionGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    gap: 16,
  },
  transformOptionIcon: {
    fontSize: 32,
  },
  transformOptionText: {
    flex: 1,
  },
  transformOptionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  transformOptionDescription: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingOverlayText: {
    fontSize: 18,
    color: 'white',
    marginTop: 16,
  },
});