import 'react-native-gesture-handler';
import React, { useEffect, useRef } from 'react';
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
import DemoBanner from './src/demo/DemoBanner';
import { useDemoStore } from './src/demo/demoStore';

// Initialize Sentry before any rendering — wrapped so a Sentry failure
// never prevents the app from starting. Catching both sync errors AND
// unhandled promise rejections from native module init.
try {
  initSentry();
} catch (e) {
  console.warn('[Sentry] initSentry() threw, continuing without Sentry:', e);
}

// Configure foreground notification display once at module level.
// This can crash on cold start if the native notification module
// isn't ready yet (common in TestFlight/EAS builds).
try {
  configureForegroundHandler();
} catch (e) {
  console.warn('[Notifications] configureForegroundHandler() threw:', e);
}

// Global unhandled promise rejection handler — prevents native crashes
// from async operations that throw before React error boundaries catch them.
const _origHandler = (global as any).ErrorUtils?.getGlobalHandler?.();
if ((global as any).ErrorUtils) {
  (global as any).ErrorUtils.setGlobalHandler((error: any, isFatal: boolean) => {
    console.error('[GlobalErrorHandler]', isFatal ? 'FATAL' : 'non-fatal', error);
    // Call original handler so Sentry/LogBox still work
    if (_origHandler) _origHandler(error, isFatal);
  });
}

function App() {
  const status = useAuthStore((s) => s.status);
  const user = useAuthStore((s) => s.user);
  const hydrate = useAuthStore((s) => s.hydrate);
  const pushRegistered = useRef(false);
  const hydrateDemo = useDemoStore((s) => s.hydrate);

  useEffect(() => {
    hydrate();
    hydrateDemo();
  }, [hydrate, hydrateDemo]);

  // Set Sentry user context on auth change
  useEffect(() => {
    try {
      if (status === 'signedIn' && user) {
        setSentryUser({ id: String(user.id), username: user.username, platform_role: user.platform_role });
      } else {
        setSentryUser(null);
      }
    } catch (e) {
      console.warn('[Sentry] setSentryUser failed:', e);
    }
  }, [status, user]);

  // Register push token after sign-in
  useEffect(() => {
    if (status === 'signedIn' && !pushRegistered.current) {
      pushRegistered.current = true;
      registerPushToken().catch((err) =>
        console.warn('[Push] registerPushToken failed:', err),
      );
      handleInitialNotification().catch((err) =>
        console.warn('[Push] handleInitialNotification failed:', err),
      );
    }
  }, [status]);

  // Listen for notification taps
  useEffect(() => {
    try {
      const cleanup = addNotificationResponseListener();
      return cleanup;
    } catch (e) {
      console.warn('[Push] addNotificationResponseListener failed:', e);
    }
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
      <DemoBanner />
      <OfflineBanner />
      <AppNavigator />
      <ToastBanner />
      <StatusBar style="light" />
    </GestureHandlerRootView>
  );
}

// Wrap root component with Sentry error boundary.
// If Sentry.wrap throws (e.g. Sentry not initialised, wrong version, etc.)
// fall back to the unwrapped App so the user can still use the app.
let WrappedApp: React.ComponentType;
try {
  WrappedApp = SentryErrorBoundary(App);
} catch (e) {
  console.warn('[Sentry] SentryErrorBoundary(App) failed, using unwrapped App:', e);
  WrappedApp = App;
}
export default WrappedApp;

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
