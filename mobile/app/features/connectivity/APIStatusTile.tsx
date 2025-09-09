import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { theme } from '../../../src/styles/theme';

interface APIStatusTileProps {
  title: string;
  endpoint: string;
  onTest?: () => Promise<boolean>;
}

type APIStatus = 'idle' | 'testing' | 'success' | 'error';

export const APIStatusTile: React.FC<APIStatusTileProps> = ({
  title,
  endpoint,
  onTest,
}) => {
  const [status, setStatus] = useState<APIStatus>('idle');
  const [lastError, setLastError] = useState<string>('');
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  // Auto-test on mount
  useEffect(() => {
    if (onTest) {
      testConnection();
    }
  }, []);

  const testConnection = async () => {
    if (!onTest) return;

    setStatus('testing');
    setLastError('');
    
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }

    const startTime = Date.now();
    
    try {
      const success = await onTest();
      const endTime = Date.now();
      
      setResponseTime(endTime - startTime);
      setLastChecked(new Date());
      
      if (success) {
        setStatus('success');
        setLastError('');
        
        if (Platform.OS !== 'web') {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        }
      } else {
        setStatus('error');
        setLastError('API test returned false');
        
        if (Platform.OS !== 'web') {
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
        }
      }
    } catch (error) {
      setStatus('error');
      setLastError(error instanceof Error ? error.message : 'Unknown error');
      setResponseTime(null);
      setLastChecked(new Date());
      
      if (Platform.OS !== 'web') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      }
    }
  };

  const getBadgeColor = (): [string, string] => {
    switch (status) {
      case 'success':
        return [theme.colors.success.main, theme.colors.success.light];
      case 'error':
        return [theme.colors.error.main, theme.colors.error.light];
      case 'testing':
        return [theme.colors.warning.main, theme.colors.warning.light];
      default:
        return [theme.colors.text.tertiary, theme.colors.background.tertiary];
    }
  };

  const getBadgeText = (): string => {
    switch (status) {
      case 'success':
        return 'OK';
      case 'error':
        return 'Fail';
      case 'testing':
        return '...';
      default:
        return '?';
    }
  };

  const getStatusColor = (): string => {
    switch (status) {
      case 'success':
        return theme.colors.success.main;
      case 'error':
        return theme.colors.error.main;
      case 'testing':
        return theme.colors.warning.main;
      default:
        return theme.colors.text.secondary;
    }
  };

  const formatLastChecked = (): string => {
    if (!lastChecked) return 'Never';
    
    const now = new Date();
    const diff = now.getTime() - lastChecked.getTime();
    
    if (diff < 60000) {
      return `${Math.floor(diff / 1000)}s ago`;
    } else if (diff < 3600000) {
      return `${Math.floor(diff / 60000)}m ago`;
    } else {
      return lastChecked.toLocaleTimeString();
    }
  };

  if (!endpoint) {
    return (
      <View style={styles.container}>
        <BlurView intensity={30} tint="dark" style={styles.blurCard}>
          <LinearGradient
            colors={['rgba(239, 68, 68, 0.1)', 'rgba(220, 38, 38, 0.05)']}
            style={styles.warningCard}
          >
            <View style={styles.warningHeader}>
              <Text style={styles.warningIcon}>⚠️</Text>
              <Text style={styles.warningTitle}>API Not Configured</Text>
            </View>
            <Text style={styles.warningText}>
              {title} endpoint is not configured.
            </Text>
            <Text style={styles.warningSubtext}>
              Please check your environment variables.
            </Text>
          </LinearGradient>
        </BlurView>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <BlurView intensity={30} tint="dark" style={styles.blurCard}>
        <LinearGradient
          colors={['rgba(99, 102, 241, 0.1)', 'rgba(139, 92, 246, 0.05)']}
          style={styles.card}
        >
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.titleRow}>
              <Text style={styles.title}>{title}</Text>
              <LinearGradient
                colors={getBadgeColor()}
                style={styles.badge}
              >
                <Text style={styles.badgeText}>{getBadgeText()}</Text>
              </LinearGradient>
            </View>
            <Text style={styles.url} numberOfLines={2}>
              {endpoint}
            </Text>
          </View>

          {/* Status Info */}
          <View style={styles.statusSection}>
            <View style={styles.statusRow}>
              <Text style={styles.statusLabel}>Status:</Text>
              <Text style={[styles.statusValue, { color: getStatusColor() }]}>
                {status.toUpperCase()}
              </Text>
            </View>

            {responseTime !== null && (
              <View style={styles.statusRow}>
                <Text style={styles.statusLabel}>Response:</Text>
                <Text style={styles.statusValue}>
                  {responseTime}ms
                </Text>
              </View>
            )}

            <View style={styles.statusRow}>
              <Text style={styles.statusLabel}>Last Check:</Text>
              <Text style={styles.statusValue}>
                {formatLastChecked()}
              </Text>
            </View>

            {lastError ? (
              <View style={styles.errorSection}>
                <Text style={styles.errorLabel}>Error:</Text>
                <Text style={styles.errorText} numberOfLines={2}>
                  {lastError}
                </Text>
              </View>
            ) : null}
          </View>

          {/* Test Button */}
          <TouchableOpacity
            style={[styles.testButton, status === 'testing' && styles.testButtonDisabled]}
            onPress={testConnection}
            disabled={status === 'testing' || !onTest}
            activeOpacity={0.8}
          >
            <LinearGradient
              colors={theme.colors.primary.gradient}
              style={styles.testButtonGradient}
            >
              {status === 'testing' ? (
                <ActivityIndicator color="white" size="small" />
              ) : (
                <Text style={styles.testButtonText}>Test Connection</Text>
              )}
            </LinearGradient>
          </TouchableOpacity>
        </LinearGradient>
      </BlurView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginHorizontal: theme.spacing.lg,
    marginVertical: theme.spacing.md,
  },
  blurCard: {
    borderRadius: theme.borderRadius.xl,
    overflow: 'hidden',
  },
  card: {
    padding: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    borderRadius: theme.borderRadius.xl,
  },
  warningCard: {
    padding: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.error.main,
    borderRadius: theme.borderRadius.xl,
  },
  warningHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  warningIcon: {
    fontSize: 20,
    marginRight: theme.spacing.sm,
  },
  warningTitle: {
    ...theme.typography.titleMedium,
    color: theme.colors.error.main,
    flex: 1,
  },
  warningText: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.xs,
  },
  warningSubtext: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
  },
  header: {
    marginBottom: theme.spacing.md,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: theme.spacing.xs,
  },
  title: {
    ...theme.typography.titleLarge,
    color: theme.colors.text.primary,
    flex: 1,
  },
  badge: {
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: 4,
    borderRadius: theme.borderRadius.sm,
    minWidth: 40,
    alignItems: 'center',
  },
  badgeText: {
    ...theme.typography.labelSmall,
    color: theme.colors.text.primary,
    fontWeight: '600',
  },
  url: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
    fontFamily: Platform.select({
      ios: 'Menlo',
      android: 'monospace',
      default: 'monospace',
    }),
  },
  statusSection: {
    marginBottom: theme.spacing.md,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.xs,
  },
  statusLabel: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
    minWidth: 80,
  },
  statusValue: {
    ...theme.typography.bodyMedium,
    fontWeight: '600',
    color: theme.colors.text.primary,
  },
  errorSection: {
    marginTop: theme.spacing.sm,
  },
  errorLabel: {
    ...theme.typography.bodySmall,
    color: theme.colors.error.main,
    marginBottom: 2,
  },
  errorText: {
    ...theme.typography.bodySmall,
    color: theme.colors.error.light,
    fontFamily: Platform.select({
      ios: 'Menlo',
      android: 'monospace',
      default: 'monospace',
    }),
    backgroundColor: theme.colors.error.background,
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.sm,
  },
  testButton: {
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
  },
  testButtonDisabled: {
    opacity: 0.6,
  },
  testButtonGradient: {
    paddingVertical: theme.spacing.md,
    paddingHorizontal: theme.spacing.lg,
    alignItems: 'center',
  },
  testButtonText: {
    ...theme.typography.labelLarge,
    color: 'white',
    fontWeight: '700',
  },
});