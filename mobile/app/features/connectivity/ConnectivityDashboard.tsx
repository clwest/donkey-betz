import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Alert,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { theme } from '../../../src/styles/theme';
import { WSStatusTile } from './WSStatusTile';
import { APIStatusTile } from './APIStatusTile';
import { 
  donkeyBetz, 
  dbao, 
  healthMonitor, 
  apiConfig,
  type HealthStatus 
} from '../common/apiService';
import {
  createDonkeyBetzWebSocketClient,
  createDBAOWebSocketClient,
} from '../ws/client';
import { 
  stateManager, 
  useStateManager, 
  STATE_EVENTS,
  type AppState 
} from '../common/stateManager';

interface ConnectivityStatus {
  donkeyBetz: {
    api: HealthStatus | null;
    websocket: boolean;
  };
  dbao: {
    api: HealthStatus | null;
    websocket: boolean;
  };
  lastChecked: Date | null;
}

export const ConnectivityDashboard: React.FC = () => {
  const [refreshing, setRefreshing] = useState(false);
  const [status, setStatus] = useState<ConnectivityStatus>({
    donkeyBetz: { api: null, websocket: false },
    dbao: { api: null, websocket: false },
    lastChecked: null,
  });
  const [connectivity, setConnectivity] = useState<AppState['connectivity']>();

  // Subscribe to state changes
  useEffect(() => {
    const initializeState = async () => {
      await stateManager.waitForInitialization();
      const currentState = stateManager.getState();
      setConnectivity(currentState.connectivity);
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

  // Initial health check
  useEffect(() => {
    if (connectivity) {
      checkAllConnections();
    }
  }, [connectivity]);

  const checkAllConnections = useCallback(async () => {
    try {
      const healthResults = await healthMonitor.checkAllServices();
      
      // Update persistent state
      stateManager.updateDonkeyBetzConnectivity({
        apiStatus: healthResults.donkeyBetz.status === 'healthy' ? 'healthy' : 
                  healthResults.donkeyBetz.status === 'error' ? 'error' : 'unhealthy',
        lastError: healthResults.donkeyBetz.status !== 'healthy' ? 
                  healthResults.donkeyBetz.message || null : null,
      });

      stateManager.updateDBAOConnectivity({
        apiStatus: healthResults.dbao.status === 'healthy' ? 'healthy' : 
                  healthResults.dbao.status === 'error' ? 'error' : 'unhealthy',
        lastError: healthResults.dbao.status !== 'healthy' ? 
                  healthResults.dbao.message || null : null,
      });
      
      setStatus({
        donkeyBetz: {
          api: healthResults.donkeyBetz,
          websocket: false, // Will be updated by WS tiles
        },
        dbao: {
          api: healthResults.dbao,
          websocket: false, // Will be updated by WS tiles
        },
        lastChecked: new Date(),
      });
    } catch (error) {
      console.error('Failed to check connections:', error);
      
      // Update state with error
      stateManager.updateDonkeyBetzConnectivity({
        apiStatus: 'error',
        lastError: 'Failed to check Donkey Betz health',
      });

      stateManager.updateDBAOConnectivity({
        apiStatus: 'error',
        lastError: 'Failed to check DBAO health',
      });

      Alert.alert(
        'Connection Check Failed',
        'Unable to check all service connections. Please try again.',
        [{ text: 'OK' }]
      );
    }
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }
    
    await checkAllConnections();
    setRefreshing(false);
  };

  // Test functions for API tiles
  const testDonkeyBetzAPI = async (): Promise<boolean> => {
    try {
      const result = await donkeyBetz.checkHealth();
      return result.status === 'healthy';
    } catch (error) {
      console.error('Donkey Betz API test failed:', error);
      return false;
    }
  };

  const testDBAOAPI = async (): Promise<boolean> => {
    try {
      const result = await dbao.checkHealth();
      return result.status === 'healthy';
    } catch (error) {
      console.error('DBAO API test failed:', error);
      return false;
    }
  };

  const getOverallStatus = (): 'healthy' | 'partial' | 'unhealthy' => {
    if (!connectivity) return 'unhealthy';
    
    const donkeyBetzHealthy = connectivity.donkeyBetz.apiStatus === 'healthy' || 
                           connectivity.donkeyBetz.apiStatus === 'unknown';
    const dbaoHealthy = connectivity.dbao.apiStatus === 'healthy' || 
                       connectivity.dbao.apiStatus === 'unknown';
    
    if (donkeyBetzHealthy && dbaoHealthy && connectivity.isOnline) return 'healthy';
    if ((donkeyBetzHealthy || dbaoHealthy) && connectivity.isOnline) return 'partial';
    return 'unhealthy';
  };

  const getOverallStatusColor = (): [string, string] => {
    const overall = getOverallStatus();
    switch (overall) {
      case 'healthy':
        return [theme.colors.success.main, theme.colors.success.light];
      case 'partial':
        return [theme.colors.warning.main, theme.colors.warning.light];
      default:
        return [theme.colors.error.main, theme.colors.error.light];
    }
  };

  const getOverallStatusText = (): string => {
    const overall = getOverallStatus();
    switch (overall) {
      case 'healthy':
        return 'All Systems Operational';
      case 'partial':
        return 'Partial Service Available';
      default:
        return 'Service Issues Detected';
    }
  };

  const formatLastChecked = (): string => {
    if (!connectivity?.lastGlobalCheck) return 'Never';
    
    try {
      const lastCheck = new Date(connectivity.lastGlobalCheck);
      const now = new Date();
      const diff = now.getTime() - lastCheck.getTime();
      
      if (diff < 60000) {
        return `${Math.floor(diff / 1000)}s ago`;
      } else if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}m ago`;
      } else {
        return lastCheck.toLocaleTimeString();
      }
    } catch {
      return 'Never';
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
      }
      showsVerticalScrollIndicator={false}
    >
      {/* Overall Status Header */}
      <View style={styles.headerContainer}>
        <BlurView intensity={30} tint="dark" style={styles.headerBlur}>
          <LinearGradient
            colors={['rgba(99, 102, 241, 0.15)', 'rgba(139, 92, 246, 0.1)']}
            style={styles.headerCard}
          >
            <View style={styles.headerContent}>
              <View style={styles.headerTitleRow}>
                <Text style={styles.headerTitle}>System Connectivity</Text>
                <LinearGradient
                  colors={getOverallStatusColor()}
                  style={styles.headerBadge}
                >
                  <Text style={styles.headerBadgeText}>
                    {getOverallStatus().toUpperCase()}
                  </Text>
                </LinearGradient>
              </View>
              
              <Text style={styles.headerSubtitle}>
                {getOverallStatusText()}
              </Text>
              
              <Text style={styles.headerLastChecked}>
                Last checked: {formatLastChecked()}
              </Text>
            </View>
          </LinearGradient>
        </BlurView>
      </View>

      {/* Configuration Info */}
      <View style={styles.configContainer}>
        <BlurView intensity={20} tint="dark" style={styles.configBlur}>
          <LinearGradient
            colors={['rgba(75, 85, 99, 0.1)', 'rgba(55, 65, 81, 0.05)']}
            style={styles.configCard}
          >
            <Text style={styles.configTitle}>Configuration</Text>
            <View style={styles.configRow}>
              <Text style={styles.configLabel}>Platform:</Text>
              <Text style={styles.configValue}>{Platform.OS}</Text>
            </View>
            <View style={styles.configRow}>
              <Text style={styles.configLabel}>Donkey Betz:</Text>
              <Text style={styles.configValue} numberOfLines={1}>
                {apiConfig.donkeyBetzUrl || 'Not configured'}
              </Text>
            </View>
            <View style={styles.configRow}>
              <Text style={styles.configLabel}>DBAO:</Text>
              <Text style={styles.configValue} numberOfLines={1}>
                {apiConfig.dbaoUrl || 'Not configured'}
              </Text>
            </View>
            <View style={styles.configRow}>
              <Text style={styles.configLabel}>Auth Token:</Text>
              <Text style={styles.configValue}>
                {apiConfig.hasAuthToken ? '✓ Configured' : '✗ Missing'}
              </Text>
            </View>
          </LinearGradient>
        </BlurView>
      </View>

      {/* Donkey Betz Section */}
      <View style={styles.sectionContainer}>
        <BlurView intensity={15} tint="dark" style={styles.sectionBlur}>
          <LinearGradient
            colors={['rgba(34, 197, 94, 0.1)', 'rgba(21, 128, 61, 0.05)']}
            style={styles.sectionCard}
          >
            <Text style={styles.sectionTitle}>Donkey Betz</Text>
            <Text style={styles.sectionSubtitle}>
              Content generation, gallery, and voice services
            </Text>
          </LinearGradient>
        </BlurView>
      </View>

      {/* Donkey Betz API Status */}
      <APIStatusTile
        title="Donkey Betz REST API"
        endpoint={apiConfig.donkeyBetzUrl || ''}
        onTest={testDonkeyBetzAPI}
      />

      {/* Donkey Betz WebSocket Status */}
      <WSStatusTile 
        title="Donkey Betz WebSocket"
        clientFactory={() => createDonkeyBetzWebSocketClient('/ws/assistant/')}
      />

      {/* DBAO Section */}
      <View style={styles.sectionContainer}>
        <BlurView intensity={15} tint="dark" style={styles.sectionBlur}>
          <LinearGradient
            colors={['rgba(168, 85, 247, 0.1)', 'rgba(124, 58, 237, 0.05)']}
            style={styles.sectionCard}
          >
            <Text style={styles.sectionTitle}>DBAO (Agent Orchestra)</Text>
            <Text style={styles.sectionSubtitle}>
              Sports betting, agent orchestration, and analytics
            </Text>
          </LinearGradient>
        </BlurView>
      </View>

      {/* DBAO API Status */}
      <APIStatusTile
        title="DBAO REST API"
        endpoint={apiConfig.dbaoUrl || ''}
        onTest={testDBAOAPI}
      />

      {/* DBAO WebSocket Status */}
      <WSStatusTile 
        title="DBAO WebSocket"
        clientFactory={() => createDBAOWebSocketClient('/ws/assistant/')}
      />

      {/* Bottom padding */}
      <View style={styles.bottomPadding} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  headerContainer: {
    marginTop: theme.spacing.lg,
    marginHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.md,
  },
  headerBlur: {
    borderRadius: theme.borderRadius.xl,
    overflow: 'hidden',
  },
  headerCard: {
    padding: theme.spacing.xl,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    borderRadius: theme.borderRadius.xl,
  },
  headerContent: {
    alignItems: 'center',
  },
  headerTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    width: '100%',
    marginBottom: theme.spacing.sm,
  },
  headerTitle: {
    ...theme.typography.titleLarge,
    color: theme.colors.text.primary,
    fontWeight: '700',
    flex: 1,
  },
  headerBadge: {
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
    minWidth: 80,
    alignItems: 'center',
  },
  headerBadgeText: {
    ...theme.typography.labelMedium,
    color: theme.colors.text.primary,
    fontWeight: '700',
  },
  headerSubtitle: {
    ...theme.typography.bodyLarge,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    marginBottom: theme.spacing.xs,
  },
  headerLastChecked: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.tertiary,
    textAlign: 'center',
  },
  configContainer: {
    marginHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
  },
  configBlur: {
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
  },
  configCard: {
    padding: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border.secondary,
    borderRadius: theme.borderRadius.lg,
  },
  configTitle: {
    ...theme.typography.titleMedium,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.md,
    fontWeight: '600',
  },
  configRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  configLabel: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
    minWidth: 80,
  },
  configValue: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.primary,
    fontFamily: Platform.select({
      ios: 'Menlo',
      android: 'monospace',
      default: 'monospace',
    }),
    flex: 1,
    fontSize: 12,
  },
  sectionContainer: {
    marginHorizontal: theme.spacing.lg,
    marginBottom: theme.spacing.md,
  },
  sectionBlur: {
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
  },
  sectionCard: {
    padding: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    borderRadius: theme.borderRadius.lg,
  },
  sectionTitle: {
    ...theme.typography.titleMedium,
    color: theme.colors.text.primary,
    fontWeight: '600',
    marginBottom: theme.spacing.xs,
  },
  sectionSubtitle: {
    ...theme.typography.bodyMedium,
    color: theme.colors.text.secondary,
  },
  bottomPadding: {
    height: theme.spacing.xl,
  },
});