import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Switch,
  Platform,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { theme } from '../styles/theme';
import { PremiumButton } from '../components/common/PremiumButton';
import { useAuthStore } from '../store/authStore';

interface SettingItem {
  id: string;
  title: string;
  icon: string;
  type: 'toggle' | 'action' | 'nav';
  value?: boolean;
  onPress?: () => void;
}

interface StatItem {
  label: string;
  value: string;
  icon: string;
}

export default function ProfileScreen({ navigation }: any) {
  const { user, logout } = useAuthStore();
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(true);
  const [autoSave, setAutoSave] = useState(true);
  const [highQuality, setHighQuality] = useState(true);

  const stats: StatItem[] = [
    { label: 'Contents', value: '1,274', icon: '📝' },
    { label: 'Images', value: '892', icon: '🎨' },
    { label: 'Videos', value: '43', icon: '🎬' },
    { label: 'Credits', value: '2,450', icon: '💎' },
  ];

  const handleLogout = () => {
    if (Platform.OS === 'web') {
      if (window.confirm('Are you sure you want to logout?')) {
        logout();
        // No need to navigate - App.tsx will handle auth state change
      }
    } else {
      Alert.alert(
        'Logout',
        'Are you sure you want to logout?',
        [
          { text: 'Cancel', style: 'cancel' },
          { 
            text: 'Logout', 
            style: 'destructive',
            onPress: () => {
              logout();
              // No need to navigate - App.tsx will handle auth state change
            }
          },
        ]
      );
    }
  };

  const handleUpgrade = () => {
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }
    navigation.navigate('Upgrade');
  };

  const settings: SettingItem[] = [
    {
      id: 'notifications',
      title: 'Push Notifications',
      icon: '🔔',
      type: 'toggle',
      value: notifications,
      onPress: () => setNotifications(!notifications),
    },
    {
      id: 'darkMode',
      title: 'Dark Mode',
      icon: '🌙',
      type: 'toggle',
      value: darkMode,
      onPress: () => setDarkMode(!darkMode),
    },
    {
      id: 'autoSave',
      title: 'Auto-Save',
      icon: '💾',
      type: 'toggle',
      value: autoSave,
      onPress: () => setAutoSave(!autoSave),
    },
    {
      id: 'highQuality',
      title: 'High Quality Outputs',
      icon: '✨',
      type: 'toggle',
      value: highQuality,
      onPress: () => setHighQuality(!highQuality),
    },
    {
      id: 'apiKeys',
      title: 'API Keys',
      icon: '🔑',
      type: 'nav',
      onPress: () => navigation.navigate('APIKeys'),
    },
    {
      id: 'billing',
      title: 'Billing & Credits',
      icon: '💳',
      type: 'nav',
      onPress: () => navigation.navigate('Billing'),
    },
    {
      id: 'support',
      title: 'Support',
      icon: '🆘',
      type: 'nav',
      onPress: () => navigation.navigate('Support'),
    },
    {
      id: 'about',
      title: 'About',
      icon: 'ℹ️',
      type: 'nav',
      onPress: () => navigation.navigate('About'),
    },
  ];

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#0A0A0F', '#1C1C25']}
        style={StyleSheet.absoluteFillObject}
      />
      
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
        >
          <Text style={styles.screenTitle}>Profile</Text>

          {/* Profile Card */}
          <View style={styles.profileCard}>
            <BlurView intensity={30} tint="dark" style={styles.blurCard}>
              <LinearGradient
                colors={['rgba(99, 102, 241, 0.1)', 'rgba(139, 92, 246, 0.05)']}
                style={styles.profileGradient}
              >
                <View style={styles.profileHeader}>
                  <View style={styles.avatarContainer}>
                    <LinearGradient
                      colors={theme.colors.primary.gradient}
                      style={styles.avatarGradient}
                    >
                      <Text style={styles.avatarText}>
                        {user?.name?.charAt(0).toUpperCase() || 'U'}
                      </Text>
                    </LinearGradient>
                  </View>
                  <View style={styles.profileInfo}>
                    <Text style={styles.userName}>{user?.name || 'Premium Creator'}</Text>
                    <Text style={styles.userEmail}>{user?.email || 'creator@studio.ai'}</Text>
                    <View style={styles.planBadge}>
                      <LinearGradient
                        colors={['#FFD700', '#FFA500']}
                        style={styles.planGradient}
                      >
                        <Text style={styles.planText}>PRO PLAN</Text>
                      </LinearGradient>
                    </View>
                  </View>
                </View>

                {/* Stats Grid */}
                <View style={styles.statsGrid}>
                  {stats.map((stat, index) => (
                    <View key={index} style={styles.statItem}>
                      <Text style={styles.statIcon}>{stat.icon}</Text>
                      <Text style={styles.statValue}>{stat.value}</Text>
                      <Text style={styles.statLabel}>{stat.label}</Text>
                    </View>
                  ))}
                </View>

                {/* Upgrade Button */}
                <TouchableOpacity style={styles.upgradeButton} onPress={handleUpgrade}>
                  <LinearGradient
                    colors={['#FFD700', '#FFA500', '#FF6347']}
                    style={styles.upgradeGradient}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 1 }}
                  >
                    <Text style={styles.upgradeIcon}>🚀</Text>
                    <Text style={styles.upgradeText}>Upgrade to Enterprise</Text>
                  </LinearGradient>
                </TouchableOpacity>
              </LinearGradient>
            </BlurView>
          </View>

          {/* Settings Section */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Settings</Text>
            {settings.map((setting) => (
              <TouchableOpacity
                key={setting.id}
                style={styles.settingItem}
                onPress={setting.onPress}
                activeOpacity={0.7}
              >
                <View style={styles.settingLeft}>
                  <Text style={styles.settingIcon}>{setting.icon}</Text>
                  <Text style={styles.settingTitle}>{setting.title}</Text>
                </View>
                {setting.type === 'toggle' ? (
                  <Switch
                    value={setting.value}
                    onValueChange={setting.onPress}
                    trackColor={{ 
                      false: theme.colors.background.tertiary, 
                      true: theme.colors.primary.main 
                    }}
                    thumbColor={setting.value ? '#FFFFFF' : '#888888'}
                  />
                ) : (
                  <Text style={styles.chevron}>›</Text>
                )}
              </TouchableOpacity>
            ))}
          </View>

          {/* Achievement Section */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Achievements</Text>
            <ScrollView 
              horizontal 
              showsHorizontalScrollIndicator={false}
              style={styles.achievementsScroll}
            >
              {[
                { icon: '🏆', title: 'Power User', desc: '100+ contents' },
                { icon: '🎨', title: 'Artist', desc: '50+ images' },
                { icon: '📝', title: 'Writer', desc: '25+ blogs' },
                { icon: '🚀', title: 'Early Adopter', desc: 'Beta tester' },
              ].map((achievement, index) => (
                <View key={index} style={styles.achievementCard}>
                  <LinearGradient
                    colors={['rgba(99, 102, 241, 0.2)', 'rgba(139, 92, 246, 0.1)']}
                    style={styles.achievementGradient}
                  >
                    <Text style={styles.achievementIcon}>{achievement.icon}</Text>
                    <Text style={styles.achievementTitle}>{achievement.title}</Text>
                    <Text style={styles.achievementDesc}>{achievement.desc}</Text>
                  </LinearGradient>
                </View>
              ))}
            </ScrollView>
          </View>

          {/* Logout Button */}
          <View style={styles.logoutContainer}>
            <PremiumButton
              title="Logout"
              onPress={handleLogout}
              variant="secondary"
              size="large"
              icon={<Text style={{ fontSize: 18 }}>👋</Text>}
            />
          </View>

          {/* Version Info */}
          <Text style={styles.versionText}>Donkey Betz Premium v2.0.0</Text>
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
  screenTitle: {
    ...theme.typography.headlineLarge,
    color: theme.colors.text.primary,
    paddingHorizontal: theme.spacing.lg,
    marginTop: theme.spacing.md,
    marginBottom: theme.spacing.lg,
  },
  profileCard: {
    marginHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.xl,
  },
  blurCard: {
    borderRadius: theme.borderRadius.xl,
    overflow: 'hidden',
  },
  profileGradient: {
    padding: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    borderRadius: theme.borderRadius.xl,
  },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.lg,
  },
  avatarContainer: {
    marginRight: theme.spacing.md,
  },
  avatarGradient: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  profileInfo: {
    flex: 1,
  },
  userName: {
    ...theme.typography.titleLarge,
    color: theme.colors.text.primary,
    marginBottom: 4,
  },
  userEmail: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
    marginBottom: 8,
  },
  planBadge: {
    alignSelf: 'flex-start',
  },
  planGradient: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  planText: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#000000',
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: theme.spacing.lg,
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statIcon: {
    fontSize: 24,
    marginBottom: 4,
  },
  statValue: {
    ...theme.typography.titleMedium,
    color: theme.colors.text.primary,
    fontWeight: 'bold',
  },
  statLabel: {
    ...theme.typography.labelSmall,
    color: theme.colors.text.secondary,
  },
  upgradeButton: {
    borderRadius: theme.borderRadius.md,
    overflow: 'hidden',
  },
  upgradeGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: theme.spacing.md,
  },
  upgradeIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  upgradeText: {
    ...theme.typography.titleMedium,
    color: '#000000',
    fontWeight: 'bold',
  },
  section: {
    marginBottom: theme.spacing.xl,
  },
  sectionTitle: {
    ...theme.typography.titleLarge,
    color: theme.colors.text.primary,
    paddingHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.md,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: theme.spacing.md,
    paddingHorizontal: theme.spacing.lg,
    backgroundColor: theme.colors.background.secondary,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border.secondary,
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingIcon: {
    fontSize: 20,
    marginRight: theme.spacing.md,
  },
  settingTitle: {
    ...theme.typography.bodyLarge,
    color: theme.colors.text.primary,
  },
  chevron: {
    fontSize: 24,
    color: theme.colors.text.tertiary,
  },
  achievementsScroll: {
    paddingHorizontal: theme.spacing.lg,
  },
  achievementCard: {
    width: 120,
    height: 120,
    marginRight: theme.spacing.md,
    borderRadius: theme.borderRadius.md,
    overflow: 'hidden',
  },
  achievementGradient: {
    flex: 1,
    padding: theme.spacing.md,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    borderRadius: theme.borderRadius.md,
  },
  achievementIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  achievementTitle: {
    ...theme.typography.labelLarge,
    color: theme.colors.text.primary,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  achievementDesc: {
    ...theme.typography.labelSmall,
    color: theme.colors.text.secondary,
    textAlign: 'center',
  },
  logoutContainer: {
    paddingHorizontal: theme.spacing.lg,
    marginTop: theme.spacing.md,
  },
  versionText: {
    ...theme.typography.labelSmall,
    color: theme.colors.text.tertiary,
    textAlign: 'center',
    marginTop: theme.spacing.xl,
    marginBottom: theme.spacing.md,
  },
});