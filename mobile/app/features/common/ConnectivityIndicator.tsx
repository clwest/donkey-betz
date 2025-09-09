import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import { theme } from '../../../src/styles/theme';
import { 
  stateManager, 
  STATE_EVENTS,
  type AppState 
} from './stateManager';

interface ConnectivityIndicatorProps {
  variant?: 'compact' | 'detailed';
  showText?: boolean;
  onPress?: () => void;
}

export const ConnectivityIndicator: React.FC<ConnectivityIndicatorProps> = ({
  variant = 'compact',
  showText = true,
  onPress,
}) => {
  const [connectivity, setConnectivity] = useState<AppState['connectivity']>();
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const initializeState = async () => {
      await stateManager.waitForInitialization();
      const currentState = stateManager.getState();
      setConnectivity(currentState.connectivity);
      setIsLoaded(true);
    };

    initializeState();

    // Subscribe to connectivity changes
    const unsubscribeConnectivity = stateManager.on(
      STATE_EVENTS.CONNECTIVITY_CHANGED,
      (newConnectivity: AppState['connectivity']) => {
        setConnectivity(newConnectivity);
      }
    );

    return () => {
      unsubscribeConnectivity();
    };
  }, []);

  const handlePress = () => {
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
    onPress?.();
  };

  const getOverallStatus = (): 'healthy' | 'partial' | 'offline' | 'unhealthy' => {
    if (!connectivity || !isLoaded) return 'unhealthy';
    
    if (!connectivity.isOnline) return 'offline';
    
    const donkeyBetzHealthy = connectivity.donkeyBetz.apiStatus === 'healthy' || 
                           connectivity.donkeyBetz.apiStatus === 'unknown';
    const dbaoHealthy = connectivity.dbao.apiStatus === 'healthy' || 
                       connectivity.dbao.apiStatus === 'unknown';
    
    if (donkeyBetzHealthy && dbaoHealthy) return 'healthy';
    if (donkeyBetzHealthy || dbaoHealthy) return 'partial';
    return 'unhealthy';
  };

  const getStatusConfig = () => {
    const status = getOverallStatus();
    
    switch (status) {
      case 'healthy':
        return {
          colors: [theme.colors.success.main, theme.colors.success.light],
          icon: '●',
          text: 'All Systems Online',
          shortText: 'Online',
        };
      case 'partial':
        return {
          colors: [theme.colors.warning.main, theme.colors.warning.light],
          icon: '◐',
          text: 'Partial Service',
          shortText: 'Partial',
        };
      case 'offline':
        return {
          colors: [theme.colors.error.main, theme.colors.error.light],
          icon: '○',
          text: 'Offline',
          shortText: 'Offline',
        };
      case 'unhealthy':
      default:
        return {
          colors: [theme.colors.error.main, theme.colors.error.light],
          icon: '●',
          text: 'Service Issues',
          shortText: 'Issues',
        };
    }
  };

  const getServiceCount = () => {
    if (!connectivity) return { healthy: 0, total: 2 };
    
    const services = [connectivity.donkeyBetz, connectivity.dbao];
    const healthy = services.filter(service => 
      service.apiStatus === 'healthy' || service.apiStatus === 'unknown'
    ).length;
    
    return { healthy, total: services.length };
  };

  if (!isLoaded) {
    return (
      <View style={[styles.container, styles.containerLoading]}>
        <View style={styles.loadingIndicator}>
          <Text style={styles.loadingText}>●</Text>
        </View>
      </View>
    );
  }

  const statusConfig = getStatusConfig();
  const serviceCount = getServiceCount();

  const content = (
    <View style={[
      styles.container,
      variant === 'compact' ? styles.containerCompact : styles.containerDetailed
    ]}>
      <LinearGradient
        colors={[...statusConfig.colors, 'transparent']}
        style={styles.background}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
      />
      
      <View style={styles.content}>
        <Text style={[styles.icon, { color: statusConfig.colors[0] }]}>
          {statusConfig.icon}
        </Text>
        
        {showText && (
          <View style={styles.textContainer}>
            {variant === 'compact' ? (
              <Text style={styles.textCompact} numberOfLines={1}>
                {statusConfig.shortText}
              </Text>
            ) : (
              <>
                <Text style={styles.textPrimary} numberOfLines={1}>
                  {statusConfig.text}
                </Text>
                <Text style={styles.textSecondary} numberOfLines={1}>
                  {serviceCount.healthy}/{serviceCount.total} services
                </Text>
              </>
            )}
          </View>
        )}

        {variant === 'detailed' && (
          <View style={styles.serviceIndicators}>
            <View style={[
              styles.serviceIndicator,
              connectivity?.donkeyBetz.apiStatus === 'healthy' ? styles.serviceHealthy : styles.serviceUnhealthy
            ]}>
              <Text style={styles.serviceText}>DB</Text>
            </View>
            <View style={[
              styles.serviceIndicator,
              connectivity?.dbao.apiStatus === 'healthy' ? styles.serviceHealthy : styles.serviceUnhealthy
            ]}>
              <Text style={styles.serviceText}>AO</Text>
            </View>
          </View>
        )}
      </View>
    </View>
  );

  if (onPress) {
    return (
      <TouchableOpacity
        onPress={handlePress}
        activeOpacity={0.8}
        style={styles.touchable}
      >
        {content}
      </TouchableOpacity>
    );
  }

  return content;
};

const styles = StyleSheet.create({
  touchable: {
    borderRadius: theme.borderRadius.md,
  },
  container: {
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    overflow: 'hidden',
    position: 'relative',
  },
  containerCompact: {
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: theme.spacing.xs,
    minWidth: 80,
  },
  containerDetailed: {
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    minWidth: 160,
  },
  containerLoading: {
    backgroundColor: theme.colors.background.tertiary,
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: theme.spacing.xs,
    minWidth: 60,
  },
  background: {
    ...StyleSheet.absoluteFillObject,
    opacity: 0.1,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    fontSize: 12,
    marginRight: theme.spacing.xs,
    fontWeight: 'bold',
  },
  textContainer: {
    flex: 1,
  },
  textPrimary: {
    ...theme.typography.labelMedium,
    color: theme.colors.text.primary,
    fontWeight: '600',
  },
  textSecondary: {
    ...theme.typography.labelSmall,
    color: theme.colors.text.secondary,
    marginTop: 1,
  },
  textCompact: {
    ...theme.typography.labelSmall,
    color: theme.colors.text.primary,
    fontWeight: '600',
  },
  loadingIndicator: {
    alignItems: 'center',
  },
  loadingText: {
    ...theme.typography.labelSmall,
    color: theme.colors.text.tertiary,
    opacity: 0.6,
  },
  serviceIndicators: {
    flexDirection: 'row',
    marginLeft: theme.spacing.xs,
    gap: 2,
  },
  serviceIndicator: {
    width: 16,
    height: 16,
    borderRadius: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  serviceHealthy: {
    backgroundColor: theme.colors.success.main,
  },
  serviceUnhealthy: {
    backgroundColor: theme.colors.error.main,
  },
  serviceText: {
    ...theme.typography.labelSmall,
    color: 'white',
    fontSize: 8,
    fontWeight: '700',
  },
});

// Preset components for common use cases
export const CompactConnectivityIndicator: React.FC<{ onPress?: () => void }> = ({ onPress }) => (
  <ConnectivityIndicator variant="compact" onPress={onPress} />
);

export const DetailedConnectivityIndicator: React.FC<{ onPress?: () => void }> = ({ onPress }) => (
  <ConnectivityIndicator variant="detailed" onPress={onPress} />
);

export const HeaderConnectivityIndicator: React.FC<{ onPress?: () => void }> = ({ onPress }) => (
  <ConnectivityIndicator 
    variant="compact" 
    showText={false} 
    onPress={onPress} 
  />
);