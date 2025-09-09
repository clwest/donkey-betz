import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { theme } from '../../../src/styles/theme';
import { WebSocketClient } from '../ws/client';
import { DEFAULT_AUTH_TOKEN } from '../../../src/services/apiConfig';

type WebSocketState = 'idle' | 'connecting' | 'open' | 'pong' | 'closed' | 'error';

interface WSStatusTileProps {
  title?: string;
  clientFactory: () => WebSocketClient;
}

export const WSStatusTile: React.FC<WSStatusTileProps> = ({ 
  title = 'WebSocket Status',
  clientFactory,
}) => {
  const [wsState, setWsState] = useState<WebSocketState>('idle');
  const [lastMessage, setLastMessage] = useState<string>('');
  const [lastError, setLastError] = useState<string>('');
  const [authToken, setAuthToken] = useState<string>('');
  const [wsUrl, setWsUrl] = useState<string>('');
  const clientRef = useRef<WebSocketClient | null>(null);

  // Load auth token and initialize client
  useEffect(() => {
    const initializeClient = async () => {
      try {
        // Try to get auth token from storage
        const token = await AsyncStorage.getItem('auth_token') || 
                     await AsyncStorage.getItem('authToken') || 
                     DEFAULT_AUTH_TOKEN;
        
        setAuthToken(token);

        // Create WebSocket client using factory function
        const client = clientFactory();
        
        // Configure client callbacks
        const originalOnStateChange = (client as any).onStateChange;
        const originalOnMessage = (client as any).onMessage;
        const originalOnError = (client as any).onError;
        
        // Override callbacks to update our state
        (client as any).onStateChange = (state: WebSocketState) => {
          setWsState(state);
          if (originalOnStateChange) originalOnStateChange(state);
        };
        
        (client as any).onMessage = (message: any) => {
          if (typeof message === 'string') {
            setLastMessage(message);
          } else {
            const msgText = message.message || JSON.stringify(message);
            setLastMessage(`${message.type}: ${msgText.length > 50 ? msgText.substring(0, 50) + '...' : msgText}`);
            
            // Handle specific message types
            if (message.type === 'connection_established') {
              setLastError(''); // Clear errors on successful connection
            } else if (message.type === 'error') {
              setLastError(message.message || 'Server error');
            } else if (message.type === 'context' || message.type === 'pong') {
              setLastMessage('Ping response received');
              setLastError(''); // Clear errors on successful ping
            }
          }
          
          if (originalOnMessage) originalOnMessage(message);
        };
        
        (client as any).onError = (error: string) => {
          setLastError(error);
          if (originalOnError) originalOnError(error);
        };

        clientRef.current = client;
        
        // Get URL for display
        const status = client.getStatus();
        setWsUrl(status.url);
        
        // Auto-connect
        client.connect();
        
      } catch (error) {
        console.error('Failed to initialize WebSocket client:', error);
        setLastError('Failed to initialize WebSocket client');
      }
    };

    initializeClient();

    return () => {
      if (clientRef.current) {
        clientRef.current.destroy();
      }
    };
  }, []);

  const handleButtonPress = (action: 'ping' | 'close' | 'reconnect') => {
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }

    const client = clientRef.current;
    if (!client) return;

    switch (action) {
      case 'ping':
        if (client.isConnected) {
          client.sendPing();
        } else {
          setLastError('Cannot send ping - not connected');
        }
        break;
      case 'close':
        client.close();
        break;
      case 'reconnect':
        client.connect();
        break;
    }
  };

  const getBadgeColor = (): [string, string] => {
    return clientRef.current?.isConnected && wsState !== 'error' 
      ? [theme.colors.success.main, theme.colors.success.light]
      : [theme.colors.error.main, theme.colors.error.light];
  };

  const getBadgeText = (): string => {
    return clientRef.current?.isConnected && wsState !== 'error' ? 'OK' : 'Fail';
  };

  const getStateColor = (): string => {
    switch (wsState) {
      case 'open':
      case 'pong':
        return theme.colors.success.main;
      case 'connecting':
        return theme.colors.warning.main;
      case 'error':
        return theme.colors.error.main;
      case 'closed':
        return theme.colors.text.secondary;
      default:
        return theme.colors.text.tertiary;
    }
  };

  // Use the URL from the client

  if (!wsUrl || wsUrl.includes('undefined')) {
    return (
      <View style={styles.container}>
        <BlurView intensity={30} tint="dark" style={styles.blurCard}>
          <LinearGradient
            colors={['rgba(239, 68, 68, 0.1)', 'rgba(220, 38, 38, 0.05)']}
            style={styles.warningCard}
          >
            <View style={styles.warningHeader}>
              <Text style={styles.warningIcon}>⚠️</Text>
              <Text style={styles.warningTitle}>WebSocket Not Configured</Text>
            </View>
            <Text style={styles.warningText}>
              EXPO_PUBLIC_WS_URL environment variable is not configured.
            </Text>
            <Text style={styles.warningSubtext}>
              Please set this variable to enable WebSocket connectivity monitoring.
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
              {wsUrl}
            </Text>
          </View>

          {/* Status Info */}
          <View style={styles.statusSection}>
            <View style={styles.statusRow}>
              <Text style={styles.statusLabel}>State:</Text>
              <Text style={[styles.statusValue, { color: getStateColor() }]}>
                {wsState.toUpperCase()}
              </Text>
            </View>

            {lastMessage ? (
              <View style={styles.messageSection}>
                <Text style={styles.messageLabel}>Last Message:</Text>
                <Text style={styles.messageText} numberOfLines={2}>
                  {lastMessage}
                </Text>
              </View>
            ) : null}

            {lastError ? (
              <View style={styles.errorSection}>
                <Text style={styles.errorLabel}>Error:</Text>
                <Text style={styles.errorText} numberOfLines={2}>
                  {lastError}
                </Text>
              </View>
            ) : null}
          </View>

          {/* Control Buttons */}
          <View style={styles.buttonRow}>
            <TouchableOpacity
              style={[styles.button, styles.pingButton]}
              onPress={() => handleButtonPress('ping')}
              activeOpacity={0.8}
              disabled={!clientRef.current?.isConnected}
            >
              <Text style={[
                styles.buttonText, 
                !clientRef.current?.isConnected && styles.buttonTextDisabled
              ]}>
                Ping
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.closeButton]}
              onPress={() => handleButtonPress('close')}
              activeOpacity={0.8}
              disabled={wsState === 'closed'}
            >
              <Text style={[
                styles.buttonText,
                wsState === 'closed' && styles.buttonTextDisabled
              ]}>
                Close
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.reconnectButton]}
              onPress={() => handleButtonPress('reconnect')}
              activeOpacity={0.8}
              disabled={wsState === 'connecting'}
            >
              <Text style={[
                styles.buttonText,
                wsState === 'connecting' && styles.buttonTextDisabled
              ]}>
                Reconnect
              </Text>
            </TouchableOpacity>
          </View>
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
    minWidth: 50,
  },
  statusValue: {
    ...theme.typography.bodyMedium,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  messageSection: {
    marginTop: theme.spacing.sm,
  },
  messageLabel: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.secondary,
    marginBottom: 2,
  },
  messageText: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.primary,
    fontFamily: Platform.select({
      ios: 'Menlo',
      android: 'monospace',
      default: 'monospace',
    }),
    backgroundColor: theme.colors.background.tertiary,
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.sm,
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
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: theme.spacing.sm,
  },
  button: {
    flex: 1,
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.md,
    borderRadius: theme.borderRadius.md,
    backgroundColor: theme.colors.background.tertiary,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    alignItems: 'center',
  },
  pingButton: {
    backgroundColor: theme.colors.info.background,
    borderColor: theme.colors.info.main,
  },
  closeButton: {
    backgroundColor: theme.colors.error.background,
    borderColor: theme.colors.error.main,
  },
  reconnectButton: {
    backgroundColor: theme.colors.success.background,
    borderColor: theme.colors.success.main,
  },
  buttonText: {
    ...theme.typography.labelMedium,
    color: theme.colors.text.primary,
    fontWeight: '600',
  },
  buttonTextDisabled: {
    color: theme.colors.text.disabled,
  },
});