import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { useNavigation } from '@react-navigation/native';
import { theme } from '../styles/theme';

interface MenuItem {
  id: string;
  title: string;
  subtitle: string;
  icon: string;
  screen: string;
  category: string;
}

const menuItems: MenuItem[] = [
  // Sports & Betting
  {
    id: 'sports-betting',
    title: 'Sports Betting',
    subtitle: 'Live odds and Kelly calculations',
    icon: '💰',
    screen: 'SportsBetting',
    category: 'Sports & Betting',
  },
  {
    id: 'ncaaf',
    title: 'College Football',
    subtitle: 'NCAAF games and markets',
    icon: '🏈',
    screen: 'NCAAfBoard',
    category: 'Sports & Betting',
  },
  {
    id: 'odds-calc',
    title: 'Odds Calculator',
    subtitle: 'Convert and calculate odds',
    icon: '🎯',
    screen: 'OddsCalculator',
    category: 'Sports & Betting',
  },
  // Utilities
  {
    id: 'connectivity',
    title: 'System Status',
    subtitle: 'Monitor API and WebSocket health',
    icon: '📡',
    screen: 'ConnectivityMonitor',
    category: 'Utilities',
  },
  {
    id: 'assistant-test',
    title: 'Assistant Test',
    subtitle: 'WebSocket integration testing',
    icon: '🧪',
    screen: 'PersonalAssistantTest',
    category: 'Utilities',
  },
  {
    id: 'campaigns',
    title: 'Campaigns',
    subtitle: 'Marketing campaign management',
    icon: '📊',
    screen: 'Campaigns',
    category: 'Content',
  },
  {
    id: 'characters',
    title: 'Characters',
    subtitle: 'AI character profiles',
    icon: '👥',
    screen: 'Characters',
    category: 'Content',
  },
];

export default function MoreScreen() {
  const navigation = useNavigation<any>();

  const handleItemPress = (screen: string) => {
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    navigation.navigate(screen);
  };

  const groupedItems = menuItems.reduce((acc, item) => {
    if (!acc[item.category]) {
      acc[item.category] = [];
    }
    acc[item.category].push(item);
    return acc;
  }, {} as Record<string, MenuItem[]>);

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#0A0A0F', '#1C1C25']}
        style={StyleSheet.absoluteFillObject}
      />

      <SafeAreaView style={styles.safeArea}>
        <View style={styles.header}>
          <Text style={styles.title}>More Options</Text>
          <Text style={styles.subtitle}>Additional features and tools</Text>
        </View>

        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {Object.entries(groupedItems).map(([category, items]) => (
            <View key={category} style={styles.categorySection}>
              <Text style={styles.categoryTitle}>{category}</Text>
              
              {items.map((item) => (
                <TouchableOpacity
                  key={item.id}
                  style={styles.menuItem}
                  onPress={() => handleItemPress(item.screen)}
                  activeOpacity={0.7}
                >
                  <BlurView intensity={30} tint="dark" style={styles.menuItemBlur}>
                    <LinearGradient
                      colors={['rgba(99, 102, 241, 0.08)', 'rgba(139, 92, 246, 0.04)']}
                      style={styles.menuItemGradient}
                    >
                      <View style={styles.menuItemContent}>
                        <Text style={styles.menuItemIcon}>{item.icon}</Text>
                        <View style={styles.menuItemText}>
                          <Text style={styles.menuItemTitle}>{item.title}</Text>
                          <Text style={styles.menuItemSubtitle}>{item.subtitle}</Text>
                        </View>
                        <Text style={styles.chevron}>›</Text>
                      </View>
                    </LinearGradient>
                  </BlurView>
                </TouchableOpacity>
              ))}
            </View>
          ))}
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
  safeArea: {
    flex: 1,
  },
  header: {
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.xl,
    alignItems: 'center',
  },
  title: {
    ...theme.typography.headlineLarge,
    color: theme.colors.text.primary,
    textAlign: 'center',
    marginBottom: theme.spacing.sm,
  },
  subtitle: {
    ...theme.typography.bodyLarge,
    color: theme.colors.text.secondary,
    textAlign: 'center',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: theme.spacing.lg,
    paddingBottom: 100,
  },
  categorySection: {
    marginBottom: theme.spacing.xl,
  },
  categoryTitle: {
    ...theme.typography.titleMedium,
    color: theme.colors.text.secondary,
    marginBottom: theme.spacing.md,
    marginLeft: theme.spacing.xs,
  },
  menuItem: {
    marginBottom: theme.spacing.md,
  },
  menuItemBlur: {
    borderRadius: theme.borderRadius.xl,
    overflow: 'hidden',
  },
  menuItemGradient: {
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    borderRadius: theme.borderRadius.xl,
  },
  menuItemContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: theme.spacing.lg,
  },
  menuItemIcon: {
    fontSize: 28,
    marginRight: theme.spacing.lg,
  },
  menuItemText: {
    flex: 1,
  },
  menuItemTitle: {
    ...theme.typography.titleMedium,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.xs,
  },
  menuItemSubtitle: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
  },
  chevron: {
    fontSize: 24,
    color: theme.colors.text.tertiary,
    marginLeft: theme.spacing.md,
  },
});