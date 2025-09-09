import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
  TouchableOpacity,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { theme } from '../styles/theme';
import { useDashboardStore } from '../store/dashboardStore';
import { useAuthStore } from '../store/authStore';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface StatCard {
  title: string;
  value: string | number;
  icon: string;
  gradient: string[];
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

export default function DashboardScreen() {
  const user = useAuthStore((state) => state.user);
  
  // Zustand stores
  const {
    stats,
    activities,
    contentBreakdown,
    isLoadingStats,
    isLoadingActivities,
    error,
    loadDashboardStats,
    loadRecentActivity,
    loadContentBreakdown,
    refreshDashboard,
    clearError,
    startLiveUpdates,
    stopLiveUpdates,
  } = useDashboardStore();

  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    // Load initial data
    refreshDashboard();
    
    // Start live updates for dashboard
    startLiveUpdates();
    
    // Cleanup on unmount
    return () => {
      stopLiveUpdates();
    };
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    clearError();
    
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    
    try {
      await refreshDashboard();
    } catch (error) {
      console.error('Error refreshing dashboard:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const renderStatCard = (card: StatCard) => (
    <TouchableOpacity
      key={card.title}
      style={styles.statCard}
      onPress={() => {
        if (Platform.OS !== 'web') {
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        }
      }}
      activeOpacity={0.8}
    >
      <LinearGradient
        colors={card.gradient}
        style={styles.statCardGradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      >
        <BlurView intensity={20} style={styles.statCardBlur}>
          <View style={styles.statCardContent}>
            <Text style={styles.statCardIcon}>{card.icon}</Text>
            <Text style={styles.statCardTitle}>{card.title}</Text>
            <Text style={styles.statCardValue}>{card.value}</Text>
            {card.trend && (
              <View style={styles.trendContainer}>
                <Text style={[
                  styles.trendText,
                  { color: card.trend.isPositive ? '#10B981' : '#EF4444' }
                ]}>
                  {card.trend.isPositive ? '↑' : '↓'} {Math.abs(card.trend.value)}%
                </Text>
              </View>
            )}
          </View>
        </BlurView>
      </LinearGradient>
    </TouchableOpacity>
  );

  if (isLoadingStats && !stats) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary.main} />
          <Text style={styles.loadingText}>Loading analytics...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error && !stats) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorIcon}>⚠️</Text>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => {
              clearError();
              refreshDashboard();
            }}
          >
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const statCards: StatCard[] = [
    {
      title: 'Total Content',
      value: stats?.total_content || 0,
      icon: '📊',
      gradient: ['#6366F1', '#8B5CF6'],
    },
    {
      title: 'Images',
      value: stats?.total_images || 0,
      icon: '🎨',
      gradient: ['#8B5CF6', '#EC4899'],
    },
    {
      title: 'Videos',
      value: stats?.total_videos || 0,
      icon: '🎬',
      gradient: ['#EC4899', '#F59E0B'],
    },
    {
      title: 'Blogs',
      value: stats?.total_blogs || 0,
      icon: '📝',
      gradient: ['#F59E0B', '#10B981'],
    },
    {
      title: 'API Calls Today',
      value: stats?.api_calls_today || 0,
      icon: '🚀',
      gradient: ['#10B981', '#14B8A6'],
    },
    {
      title: 'Storage Used',
      value: `${Math.round((stats?.storage_used || 0) / 1024 / 1024)} MB`,
      icon: '💾',
      gradient: ['#14B8A6', '#6366F1'],
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={theme.colors.primary.main}
            colors={[theme.colors.primary.main]}
          />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Analytics Dashboard</Text>
          <Text style={styles.headerSubtitle}>Real-time insights</Text>
        </View>

        {/* Stats Grid */}
        <View style={styles.statsGrid}>
          {statCards.map(renderStatCard)}
        </View>

        {/* Recent Activity */}
        {activities && activities.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Activity</Text>
            <View style={styles.activityList}>
              {activities.slice(0, 5).map((activity, index) => (
                <View key={activity.id || index} style={styles.activityItem}>
                  <View style={styles.activityDot} />
                  <View style={styles.activityContent}>
                    <Text style={styles.activityText}>
                      {activity.description || activity.action}
                    </Text>
                    <Text style={styles.activityTime}>
                      {new Date(activity.created_at).toLocaleTimeString()}
                    </Text>
                  </View>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Popular Styles */}
        {stats?.popular_styles && stats.popular_styles.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Popular Styles</Text>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              style={styles.stylesList}
            >
              {stats.popular_styles.map((style: string, index: number) => (
                <TouchableOpacity
                  key={index}
                  style={styles.styleChip}
                  onPress={() => {
        if (Platform.OS !== 'web') {
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        }
      }}
                >
                  <LinearGradient
                    colors={['#6366F1', '#8B5CF6']}
                    style={styles.styleChipGradient}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 0 }}
                  >
                    <Text style={styles.styleChipText}>{style}</Text>
                  </LinearGradient>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}

        {/* Trending Topics */}
        {stats?.trending_topics && stats.trending_topics.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Trending Topics</Text>
            <View style={styles.topicsList}>
              {stats.trending_topics.slice(0, 5).map((topic: string, index: number) => (
                <View key={index} style={styles.topicItem}>
                  <Text style={styles.topicNumber}>#{index + 1}</Text>
                  <Text style={styles.topicText}>{topic}</Text>
                </View>
              ))}
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 32,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: theme.colors.text.secondary,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  errorIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  errorText: {
    fontSize: 16,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    marginBottom: 24,
  },
  retryButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: theme.colors.primary.main,
    borderRadius: 8,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  header: {
    padding: 24,
    paddingTop: 16,
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: theme.colors.text.secondary,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    justifyContent: 'space-between',
  },
  statCard: {
    width: (SCREEN_WIDTH - 48) / 2,
    height: 140,
    marginBottom: 16,
    borderRadius: 16,
    overflow: 'hidden',
  },
  statCardGradient: {
    flex: 1,
    padding: 1,
    borderRadius: 16,
  },
  statCardBlur: {
    flex: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 15,
  },
  statCardContent: {
    flex: 1,
    padding: 16,
  },
  statCardIcon: {
    fontSize: 28,
    marginBottom: 8,
  },
  statCardTitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 4,
  },
  statCardValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  trendContainer: {
    marginTop: 8,
  },
  trendText: {
    fontSize: 12,
    fontWeight: '600',
  },
  section: {
    paddingHorizontal: 24,
    marginTop: 32,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 16,
  },
  activityList: {
    backgroundColor: theme.colors.background.secondary,
    borderRadius: 16,
    padding: 16,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  activityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: theme.colors.primary.main,
    marginRight: 12,
  },
  activityContent: {
    flex: 1,
  },
  activityText: {
    fontSize: 14,
    color: theme.colors.text.primary,
    marginBottom: 2,
  },
  activityTime: {
    fontSize: 12,
    color: theme.colors.text.secondary,
  },
  stylesList: {
    marginHorizontal: -24,
    paddingHorizontal: 24,
  },
  styleChip: {
    marginRight: 12,
    height: 36,
    borderRadius: 18,
    overflow: 'hidden',
  },
  styleChipGradient: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  styleChipText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  topicsList: {
    backgroundColor: theme.colors.background.secondary,
    borderRadius: 16,
    padding: 16,
  },
  topicItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  topicNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.primary.main,
    marginRight: 12,
    width: 30,
  },
  topicText: {
    fontSize: 14,
    color: theme.colors.text.primary,
    flex: 1,
  },
});