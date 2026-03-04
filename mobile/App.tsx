import 'react-native-gesture-handler';
import { useEffect, useRef } from 'react';
import { StatusBar } from 'expo-status-bar';
import { ActivityIndicator, StyleSheet, View } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { useAuthStore } from './src/auth/authStore';
import LoginScreen from './src/screens/auth/LoginScreen';
import AppNavigator from './src/navigation/AppNavigator';
import { registerPushToken } from './src/push/registerPushToken';
import {
  configureForegroundHandler,
  addNotificationResponseListener,
  handleInitialNotification,
} from './src/push/notificationHandlers';
import { initSentry, setSentryUser, SentryErrorBoundary } from './src/observability/sentry';
import OfflineBanner from './src/observability/OfflineBanner';
import ToastBanner from './src/components/Toast';

// Initialize Sentry before any rendering
initSentry();

// Configure foreground notification display once at module level
configureForegroundHandler();

function App() {
  const status = useAuthStore((s) => s.status);
  const user = useAuthStore((s) => s.user);
  const hydrate = useAuthStore((s) => s.hydrate);
  const pushRegistered = useRef(false);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  // Set Sentry user context on auth change
  useEffect(() => {
    if (status === 'signedIn' && user) {
      setSentryUser({ id: String(user.id), username: user.username });
    } else {
      setSentryUser(null);
    }
  }, [status, user]);

  // Register push token after sign-in
  useEffect(() => {
    if (status === 'signedIn' && !pushRegistered.current) {
      pushRegistered.current = true;
      registerPushToken();
      handleInitialNotification();
    }
  }, [status]);

  // Listen for notification taps
  useEffect(() => {
    const cleanup = addNotificationResponseListener();
    return cleanup;
  }, []);

  if (status === 'loading') {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#6366f1" />
        <StatusBar style="light" />
      </View>
    );
  }

  if (status === 'signedOut') {
    return (
      <>
        <LoginScreen />
        <StatusBar style="light" />
      </>
    );
  }

  return (
    <GestureHandlerRootView style={styles.root}>
      <OfflineBanner />
      <AppNavigator />
      <ToastBanner />
      <StatusBar style="light" />
    </GestureHandlerRootView>
  );
}

// Wrap root component with Sentry error boundary
export default SentryErrorBoundary(App);

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
  loading: {
    flex: 1,
    backgroundColor: '#0a0a0f',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
