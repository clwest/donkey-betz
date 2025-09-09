import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Animated,
  Platform,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { theme } from '../styles/theme';
import { PremiumButton } from '../components/common/PremiumButton';
import { WsStatusTile } from '../components/WsStatusTile';
import { useAuthStore } from '../store/authStore';
import { useDashboardStore } from '../store/dashboardStore';
import { useContentStore } from '../store/contentStore';
import { HeaderConnectivityIndicator } from '../../app/features/common/ConnectivityIndicator';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface QuickAction {
  id: string;
  title: string;
  icon: string;
  gradient: string[];
  route: string;
}

interface RecentContent {
  id: number;
  type: 'blog' | 'image' | 'social' | 'video' | 'text';
  title: string;
  preview: string;
  timestamp: string;
  content_type?: string;
}

const quickActions: QuickAction[] = [
  {
    id: '1',
    title: 'Generate Blog',
    icon: '📝',
    gradient: ['#6366F1', '#8B5CF6'],
    route: 'Studio',
  },
  {
    id: '2',
    title: 'Create Image',
    icon: '🎨',
    gradient: ['#8B5CF6', '#EC4899'],
    route: 'Studio',
  },
  {
    id: '3',
    title: 'Voice Note',
    icon: '🎙️',
    gradient: ['#EC4899', '#F43F5E'],
    route: 'Studio',
  },
  {
    id: '4',
    title: 'Odds Calculator',
    icon: '🎯',
    gradient: ['#F43F5E', '#F97316'],
    route: 'OddsCalculator',
  },
  {
    id: '5',
    title: 'Campaign',
    icon: '📊',
    gradient: ['#F97316', '#EAB308'],
    route: 'Campaigns',
  },
];

// Helper function to format timestamps
const formatTimestamp = (dateString: string): string => {
  const now = new Date();
  const date = new Date(dateString);
  const diffInMs = now.getTime() - date.getTime();
  const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
  const diffInDays = Math.floor(diffInHours / 24);
  
  if (diffInHours < 1) return 'Just now';
  if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
  if (diffInDays < 7) return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
  return date.toLocaleDateString();
};

export default function HomeScreen({ navigation }: any) {
  const user = useAuthStore((state) => state.user);
  const [refreshing, setRefreshing] = useState(false);
  const [recentContent, setRecentContent] = useState<RecentContent[]>([]);
  
  // Zustand stores
  const { 
    stats, 
    isLoadingStats, 
    loadDashboardStats, 
    loadRecentActivity,
    activities,
    error: dashboardError,
    clearError: clearDashboardError
  } = useDashboardStore();
  
  const {
    contentItems,
    loadContent,
    isLoadingContent,
    error: contentError,
    clearError: clearContentError
  } = useContentStore();
  
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

  // Initialize data loading
  useEffect(() => {
    loadInitialData();
    
    // Start animations
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
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

  // Process content items to create recent content list
  useEffect(() => {
    if (contentItems && contentItems.length > 0) {
      const recent = contentItems.slice(0, 3).map(item => ({
        id: item.id,
        type: item.content_type === 'image' ? 'image' as const : 
              item.content_type === 'video' ? 'video' as const :
              item.title?.toLowerCase().includes('blog') ? 'blog' as const :
              item.title?.toLowerCase().includes('social') ? 'social' as const : 'text' as const,
        title: item.title || 'Untitled Content',
        preview: item.content ? 
          (item.content.substring(0, 50) + (item.content.length > 50 ? '...' : '')) : 
          'No preview available',
        timestamp: formatTimestamp(item.created_at),
        content_type: item.content_type,
      }));
      setRecentContent(recent);
    }
  }, [contentItems]);

  const loadInitialData = async () => {
    try {
      await Promise.all([
        loadDashboardStats(),
        loadContent(1, false),
        loadRecentActivity(10)
      ]);
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    clearDashboardError();
    clearContentError();
    
    try {
      await loadInitialData();
    } catch (error) {
      console.error('Error refreshing data:', error);
    } finally {
      setRefreshing(false);
    }
  }, []);

  const handleQuickAction = (action: QuickAction) => {
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    navigation.navigate(action.route, { mode: action.id });
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#0A0A0F', '#1C1C25']}
        style={StyleSheet.absoluteFillObject}
      />
      
      {/* Decorative gradient orbs */}
      <View style={styles.orbContainer}>
        <LinearGradient
          colors={theme.colors.primary.gradient}
          style={[styles.orb, styles.orb1]}
        />
        <LinearGradient
          colors={[...theme.colors.primary.gradient].reverse()}
          style={[styles.orb, styles.orb2]}
        />
      </View>

      <SafeAreaView style={styles.safeArea}>
        <ScrollView 
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.scrollContent}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor={theme.colors.primary.main}
              colors={[theme.colors.primary.main]}
            />
          }
        >
          {/* Header */}
          <Animated.View 
            style={[
              styles.header,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <View style={styles.headerLeft}>
              <Text style={styles.greeting}>{getGreeting()},</Text>
              <Text style={styles.userName}>{user?.name || 'Creator'} ✨</Text>
            </View>
            <View style={styles.headerRight}>
              <HeaderConnectivityIndicator 
                onPress={() => {/* TODO: Navigate to connectivity screen */}} 
              />
              <TouchableOpacity 
                style={styles.notificationButton}
                onPress={() => {
                  // Placeholder for notifications - coming soon
                  if (Platform.OS !== 'web') {
                    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
                  }
                }}
              >
                <Text style={styles.notificationIcon}>🔔</Text>
                <View style={styles.notificationBadge} />
              </TouchableOpacity>
            </View>
          </Animated.View>

          {/* Stats Card */}
          <Animated.View
            style={[
              styles.statsCard,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <BlurView intensity={30} tint="dark" style={styles.blurCard}>
              <LinearGradient
                colors={['rgba(99, 102, 241, 0.1)', 'rgba(139, 92, 246, 0.05)']}
                style={styles.statsGradient}
              >
                <View style={styles.statsRow}>
                  <View style={styles.statItem}>
                    <Text style={styles.statValue}>
                      {isLoadingStats ? '...' : (stats?.total_content || 0)}
                    </Text>
                    <Text style={styles.statLabel}>Contents</Text>
                  </View>
                  <View style={styles.statDivider} />
                  <View style={styles.statItem}>
                    <Text style={styles.statValue}>
                      {isLoadingStats ? '...' : (stats?.total_images || 0)}
                    </Text>
                    <Text style={styles.statLabel}>Images</Text>
                  </View>
                  <View style={styles.statDivider} />
                  <View style={styles.statItem}>
                    <Text style={styles.statValue}>
                      {isLoadingStats ? '...' : (stats?.api_calls_today || 0)}
                    </Text>
                    <Text style={styles.statLabel}>API Calls</Text>
                  </View>
                </View>
              </LinearGradient>
            </BlurView>
          </Animated.View>

          {/* WebSocket Status Tile */}
          <Animated.View
            style={[
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <WsStatusTile />
          </Animated.View>

          {/* Quick Actions */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Quick Actions</Text>
            <View style={styles.quickActionsGrid}>
              {quickActions.map((action, index) => (
                <Animated.View
                  key={action.id}
                  style={{
                    opacity: fadeAnim,
                    transform: [
                      {
                        translateY: slideAnim,
                      },
                      {
                        scale: fadeAnim.interpolate({
                          inputRange: [0, 1],
                          outputRange: [0.8, 1],
                        }),
                      },
                    ],
                  }}
                >
                  <TouchableOpacity
                    style={styles.quickActionCard}
                    onPress={() => handleQuickAction(action)}
                    activeOpacity={0.8}
                  >
                    <LinearGradient
                      colors={action.gradient}
                      style={styles.quickActionGradient}
                    >
                      <Text style={styles.quickActionIcon}>{action.icon}</Text>
                      <Text style={styles.quickActionTitle}>{action.title}</Text>
                    </LinearGradient>
                  </TouchableOpacity>
                </Animated.View>
              ))}
            </View>
          </View>

          {/* Recent Content */}
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Recent Creations</Text>
              <TouchableOpacity onPress={() => navigation.navigate('Gallery')}>
                <Text style={styles.seeAll}>See all →</Text>
              </TouchableOpacity>
            </View>
            
            {isLoadingContent && recentContent.length === 0 ? (
              <View style={styles.loadingContainer}>
                <Text style={styles.loadingText}>Loading recent content...</Text>
              </View>
            ) : recentContent.length === 0 ? (
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyText}>No content yet</Text>
                <Text style={styles.emptySubtext}>Start creating to see your work here</Text>
              </View>
            ) : recentContent.map((content, index) => (
              <Animated.View
                key={content.id}
                style={[
                  styles.contentCard,
                  {
                    opacity: fadeAnim,
                    transform: [
                      {
                        translateX: slideAnim.interpolate({
                          inputRange: [0, 50],
                          outputRange: [0, 100],
                        }),
                      },
                    ],
                  },
                ]}
              >
                <TouchableOpacity
                  style={styles.contentCardInner}
                  activeOpacity={0.8}
                  onPress={() => {
                    if (Platform.OS !== 'web') {
                      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
                    }
                    // Navigate to content detail or appropriate screen
                    if (content.type === 'image') {
                      navigation.navigate('Gallery', { selectedItem: content.id });
                    } else {
                      navigation.navigate('Studio', { contentId: content.id });
                    }
                  }}
                >
                  <View style={styles.contentIcon}>
                    <Text>
                      {content.type === 'blog' ? '📝' : 
                       content.type === 'image' ? '🎨' : 
                       content.type === 'social' ? '📱' : 
                       content.type === 'video' ? '🎬' : '📄'}
                    </Text>
                  </View>
                  <View style={styles.contentInfo}>
                    <Text style={styles.contentTitle}>{content.title}</Text>
                    <Text style={styles.contentPreview}>{content.preview}</Text>
                    <Text style={styles.contentTimestamp}>{content.timestamp}</Text>
                  </View>
                </TouchableOpacity>
              </Animated.View>
            ))}
          </View>

          {/* Create Button */}
          <View style={styles.createButtonContainer}>
            <PremiumButton
              title="Create Something Amazing"
              onPress={() => navigation.navigate('Studio')}
              variant="primary"
              size="large"
              glow
              icon={<Text style={{ fontSize: 20 }}>✨</Text>}
            />
          </View>
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  orbContainer: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    overflow: 'hidden',
  },
  orb: {
    position: 'absolute',
    borderRadius: 500,
    opacity: 0.1,
  },
  orb1: {
    width: 400,
    height: 400,
    top: -200,
    right: -100,
  },
  orb2: {
    width: 300,
    height: 300,
    bottom: -150,
    left: -50,
  },
  safeArea: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 100,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
  },
  headerLeft: {
    flex: 1,
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: theme.spacing.sm,
  },
  greeting: {
    ...theme.typography.bodyLarge,
    color: theme.colors.text.secondary,
  },
  userName: {
    ...theme.typography.headlineMedium,
    color: theme.colors.text.primary,
    marginTop: 4,
  },
  notificationButton: {
    position: 'relative',
    padding: theme.spacing.sm,
  },
  notificationIcon: {
    fontSize: 24,
  },
  notificationBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: theme.colors.error.main,
  },
  statsCard: {
    marginHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.xl,
  },
  blurCard: {
    borderRadius: theme.borderRadius.xl,
    overflow: 'hidden',
  },
  statsGradient: {
    padding: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    borderRadius: theme.borderRadius.xl,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statValue: {
    ...theme.typography.headlineMedium,
    color: theme.colors.text.primary,
  },
  statLabel: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
    marginTop: 4,
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: theme.colors.border.primary,
  },
  section: {
    marginBottom: theme.spacing.xl,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.md,
  },
  sectionTitle: {
    ...theme.typography.titleLarge,
    color: theme.colors.text.primary,
    paddingHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.md,
  },
  seeAll: {
    ...theme.typography.bodyMedium,
    color: theme.colors.primary.main,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: theme.spacing.md,
  },
  quickActionCard: {
    width: (SCREEN_WIDTH - theme.spacing.md * 3) / 2,
    height: 120,
    margin: theme.spacing.xs,
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
  },
  quickActionGradient: {
    flex: 1,
    padding: theme.spacing.md,
    justifyContent: 'center',
    alignItems: 'center',
  },
  quickActionIcon: {
    fontSize: 36,
    marginBottom: theme.spacing.sm,
  },
  quickActionTitle: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.primary,
    fontWeight: '600',
  },
  contentCard: {
    marginHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.md,
  },
  contentCardInner: {
    flexDirection: 'row',
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    borderWidth: 1,
    borderColor: theme.colors.border.secondary,
  },
  contentIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: theme.colors.background.tertiary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: theme.spacing.md,
  },
  contentInfo: {
    flex: 1,
  },
  contentTitle: {
    ...theme.typography.titleMedium,
    color: theme.colors.text.primary,
    marginBottom: 4,
  },
  contentPreview: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
    marginBottom: 4,
  },
  contentTimestamp: {
    ...theme.typography.labelSmall,
    color: theme.colors.text.tertiary,
  },
  createButtonContainer: {
    paddingHorizontal: theme.spacing.lg,
    marginTop: theme.spacing.md,
  },
  loadingContainer: {
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.xl,
    alignItems: 'center',
  },
  loadingText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
  },
  emptyContainer: {
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.xl,
    alignItems: 'center',
  },
  emptyText: {
    ...theme.typography.titleMedium,
    color: theme.colors.text.secondary,
    marginBottom: theme.spacing.xs,
  },
  emptySubtext: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.tertiary,
    textAlign: 'center',
  },
});