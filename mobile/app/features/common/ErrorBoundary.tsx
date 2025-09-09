import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { theme } from '../../../src/styles/theme';

interface Props {
  children: ReactNode;
  fallback?: (error: Error, resetError: () => void) => ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null,
      errorId: `error_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo,
    });

    // Log error to storage for debugging
    this.logErrorToStorage(error, errorInfo);

    // Provide haptic feedback on error
    if (Platform.OS !== 'web') {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }
  }

  private async logErrorToStorage(error: Error, errorInfo: ErrorInfo) {
    try {
      const errorLog = {
        timestamp: new Date().toISOString(),
        errorId: this.state.errorId,
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        platform: Platform.OS,
        version: '1.0.0', // App version
      };

      // Store last 10 errors
      const existingLogs = await AsyncStorage.getItem('error_logs');
      const logs = existingLogs ? JSON.parse(existingLogs) : [];
      
      logs.unshift(errorLog);
      if (logs.length > 10) {
        logs.splice(10);
      }

      await AsyncStorage.setItem('error_logs', JSON.stringify(logs));
      console.log('Error logged to storage:', errorLog.errorId);
    } catch (storageError) {
      console.warn('Failed to log error to storage:', storageError);
    }
  }

  private resetError = () => {
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }
    
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
    });
  };

  private reportError = async () => {
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }

    // In a real app, you would send this to your error reporting service
    console.log('Error report requested for:', this.state.errorId);
    
    try {
      const errorReport = {
        errorId: this.state.errorId,
        message: this.state.error?.message,
        stack: this.state.error?.stack,
        componentStack: this.state.errorInfo?.componentStack,
        timestamp: new Date().toISOString(),
        platform: Platform.OS,
        userAgent: Platform.OS === 'web' ? navigator.userAgent : undefined,
      };

      // Store error report for later transmission
      await AsyncStorage.setItem(`error_report_${this.state.errorId}`, JSON.stringify(errorReport));
      console.log('Error report prepared:', this.state.errorId);
      
    } catch (error) {
      console.warn('Failed to prepare error report:', error);
    }
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback(this.state.error!, this.resetError);
      }

      // Default error UI
      return (
        <View style={styles.container}>
          <LinearGradient
            colors={['#0A0A0F', '#1C1C25']}
            style={StyleSheet.absoluteFillObject}
          />
          
          <ScrollView 
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
          >
            <View style={styles.errorCard}>
              <BlurView intensity={30} tint="dark" style={styles.blurCard}>
                <LinearGradient
                  colors={['rgba(239, 68, 68, 0.1)', 'rgba(220, 38, 38, 0.05)']}
                  style={styles.cardGradient}
                >
                  {/* Error Icon */}
                  <View style={styles.iconContainer}>
                    <Text style={styles.errorIcon}>⚠️</Text>
                  </View>

                  {/* Error Message */}
                  <Text style={styles.title}>Something went wrong</Text>
                  <Text style={styles.subtitle}>
                    The app encountered an unexpected error. Don't worry, your data is safe.
                  </Text>

                  {/* Error Details */}
                  {this.state.error && (
                    <View style={styles.detailsSection}>
                      <Text style={styles.detailsTitle}>Error Details:</Text>
                      <View style={styles.errorDetails}>
                        <Text style={styles.errorText}>
                          {this.state.error.message || 'Unknown error'}
                        </Text>
                        {this.state.errorId && (
                          <Text style={styles.errorId}>
                            Error ID: {this.state.errorId}
                          </Text>
                        )}
                      </View>
                    </View>
                  )}

                  {/* Action Buttons */}
                  <View style={styles.buttonContainer}>
                    <TouchableOpacity
                      style={styles.button}
                      onPress={this.resetError}
                      activeOpacity={0.8}
                    >
                      <LinearGradient
                        colors={theme.colors.primary.gradient}
                        style={styles.buttonGradient}
                      >
                        <Text style={styles.buttonText}>Try Again</Text>
                      </LinearGradient>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={[styles.button, styles.secondaryButton]}
                      onPress={this.reportError}
                      activeOpacity={0.8}
                    >
                      <Text style={styles.secondaryButtonText}>Report Error</Text>
                    </TouchableOpacity>
                  </View>

                  {/* Help Text */}
                  <Text style={styles.helpText}>
                    If this problem persists, try restarting the app or check your internet connection.
                  </Text>
                </LinearGradient>
              </BlurView>
            </View>
          </ScrollView>
        </View>
      );
    }

    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.xl,
  },
  errorCard: {
    marginBottom: theme.spacing.xl,
  },
  blurCard: {
    borderRadius: theme.borderRadius.xl,
    overflow: 'hidden',
  },
  cardGradient: {
    padding: theme.spacing.xl,
    borderWidth: 1,
    borderColor: theme.colors.error.main,
    borderRadius: theme.borderRadius.xl,
  },
  iconContainer: {
    alignItems: 'center',
    marginBottom: theme.spacing.lg,
  },
  errorIcon: {
    fontSize: 64,
  },
  title: {
    ...theme.typography.headlineMedium,
    color: theme.colors.text.primary,
    textAlign: 'center',
    marginBottom: theme.spacing.md,
  },
  subtitle: {
    ...theme.typography.bodyLarge,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: theme.spacing.xl,
  },
  detailsSection: {
    marginBottom: theme.spacing.xl,
  },
  detailsTitle: {
    ...theme.typography.titleSmall,
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.sm,
  },
  errorDetails: {
    backgroundColor: theme.colors.error.background,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.error.main,
  },
  errorText: {
    ...theme.typography.bodySmall,
    color: theme.colors.error.light,
    fontFamily: Platform.select({
      ios: 'Menlo',
      android: 'monospace',
      default: 'monospace',
    }),
    lineHeight: 18,
    marginBottom: theme.spacing.xs,
  },
  errorId: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.tertiary,
    fontFamily: Platform.select({
      ios: 'Menlo',
      android: 'monospace',
      default: 'monospace',
    }),
    fontSize: 11,
  },
  buttonContainer: {
    gap: theme.spacing.md,
    marginBottom: theme.spacing.lg,
  },
  button: {
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
  },
  buttonGradient: {
    paddingVertical: theme.spacing.md,
    alignItems: 'center',
  },
  buttonText: {
    ...theme.typography.labelLarge,
    color: 'white',
    fontWeight: '700',
  },
  secondaryButton: {
    backgroundColor: theme.colors.background.tertiary,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
  },
  secondaryButtonText: {
    ...theme.typography.labelLarge,
    color: theme.colors.text.secondary,
    fontWeight: '600',
    paddingVertical: theme.spacing.md,
    textAlign: 'center',
  },
  helpText: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.tertiary,
    textAlign: 'center',
    fontStyle: 'italic',
  },
});