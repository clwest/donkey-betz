import React from 'react';
import {
  ActivityIndicator,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import * as Sentry from '@sentry/react-native';
import { toast } from './Toast';

// ── ScreenState ─────────────────────────────────────────────────────────────
// Unified loading / error / empty / ready wrapper for all screens.
//
// Usage:
//   <ScreenState loading={isLoading} error={errorMsg} onRetry={refetch}>
//     <YourContent />
//   </ScreenState>
//
//   <ScreenState loading={isLoading} error={errorMsg} empty={items.length === 0}
//     emptyMessage="No items yet" onRetry={refetch}>
//     <ItemList items={items} />
//   </ScreenState>

interface Props {
  loading?: boolean;
  error?: string | null;
  empty?: boolean;
  emptyMessage?: string;
  onRetry?: () => void;
  children: React.ReactNode;
}

export default function ScreenState({
  loading,
  error,
  empty,
  emptyMessage = 'Nothing here yet',
  onRetry,
  children,
}: Props) {
  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#6366f1" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorIcon}>!</Text>
        <Text style={styles.errorText}>{error}</Text>
        {onRetry && (
          <TouchableOpacity style={styles.retryBtn} onPress={onRetry}>
            <Text style={styles.retryText}>Retry</Text>
          </TouchableOpacity>
        )}
        <TouchableOpacity
          style={styles.copyErrorBtn}
          onPress={() => {
            toast.info(error);
          }}
        >
          <Text style={styles.copyErrorText}>Copy Error</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (empty) {
    return (
      <View style={styles.center}>
        <Text style={styles.emptyText}>{emptyMessage}</Text>
        {onRetry && (
          <TouchableOpacity style={styles.retryBtn} onPress={onRetry}>
            <Text style={styles.retryText}>Refresh</Text>
          </TouchableOpacity>
        )}
      </View>
    );
  }

  return <>{children}</>;
}

// ── ErrorBoundary ───────────────────────────────────────────────────────────
// Class component that catches render errors and shows a recovery UI.
//
// Usage:
//   <ScreenErrorBoundary screenName="Dashboard">
//     <DashboardContent />
//   </ScreenErrorBoundary>

interface ErrorBoundaryProps {
  screenName: string;
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: string | null;
}

export class ScreenErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error: error.message };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    Sentry.captureException(error, {
      tags: { screen: this.props.screenName },
      extra: { componentStack: info.componentStack },
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.center}>
          <Text style={styles.errorIcon}>!</Text>
          <Text style={styles.errorTitle}>{this.props.screenName} crashed</Text>
          <Text style={styles.errorDetail}>{this.state.error}</Text>
          <TouchableOpacity
            style={styles.retryBtn}
            onPress={() => this.setState({ hasError: false, error: null })}
          >
            <Text style={styles.retryText}>Try Again</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.copyErrorBtn}
            onPress={() => {
              toast.info(`${this.props.screenName}: ${this.state.error}`);
            }}
          >
            <Text style={styles.copyErrorText}>Copy Error</Text>
          </TouchableOpacity>
        </View>
      );
    }

    return this.props.children;
  }
}

// ── Styles ──────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  center: {
    flex: 1,
    backgroundColor: '#0a0a0f',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  loadingText: {
    color: '#6b7280',
    fontSize: 14,
    marginTop: 12,
  },
  errorIcon: {
    color: '#ef4444',
    fontSize: 36,
    fontWeight: '800',
    width: 56,
    height: 56,
    lineHeight: 56,
    textAlign: 'center',
    borderWidth: 3,
    borderColor: '#ef4444',
    borderRadius: 28,
    marginBottom: 16,
  },
  errorTitle: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 8,
  },
  errorText: {
    color: '#ef4444',
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 16,
  },
  errorDetail: {
    color: '#9ca3af',
    fontSize: 13,
    textAlign: 'center',
    marginBottom: 20,
    maxWidth: '80%',
  },
  emptyText: {
    color: '#6b7280',
    fontSize: 15,
    textAlign: 'center',
    marginBottom: 12,
  },
  retryBtn: {
    backgroundColor: '#6366f1',
    borderRadius: 8,
    paddingHorizontal: 24,
    paddingVertical: 10,
    marginBottom: 10,
  },
  retryText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  copyErrorBtn: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  copyErrorText: {
    color: '#6b7280',
    fontSize: 12,
  },
});
