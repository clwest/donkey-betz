import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { getManifest, type Manifest } from '../api/manifest';
import { resolveScreens, type ResolvedScreen } from './manifestRouter';
import { linking } from './linking';
import { useAuthStore } from '../auth/authStore';
import { ScreenErrorBoundary } from '../components/ScreenState';
import VIPAcceptScreen from '../screens/VIPAcceptScreen';

const Drawer = createDrawerNavigator();

// ── Category labels for drawer section headers ──────────────────────────────

const CATEGORY_LABELS: Record<string, string> = {
  command: 'Command',
  domain: 'Domain',
  intelligence: 'Intelligence',
  studio: 'Studio',
  reference: 'Reference',
  admin: 'Admin',
};

// ── Error boundary wrapper factory ───────────────────────────────────────────

const _boundaryCache = new Map<React.ComponentType<any>, React.ComponentType<any>>();

function wrapWithErrorBoundary(
  Component: React.ComponentType<any>,
  screenName: string,
): React.ComponentType<any> {
  const cached = _boundaryCache.get(Component);
  if (cached) return cached;

  const Wrapped = (props: any) => (
    <ScreenErrorBoundary screenName={screenName}>
      <Component {...props} />
    </ScreenErrorBoundary>
  );
  Wrapped.displayName = `ErrorBoundary(${screenName})`;
  _boundaryCache.set(Component, Wrapped);
  return Wrapped;
}

// ── Navigator ────────────────────────────────────────────────────────────────

export default function AppNavigator() {
  const user = useAuthStore((s) => s.user);
  const [screens, setScreens] = useState<ResolvedScreen[] | null>(null);
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const m = await getManifest();
        if (cancelled) return;

        // Validate manifest has the minimum required shape
        if (!m || !Array.isArray(m.routes)) {
          throw new Error(`Invalid manifest: routes is ${typeof m?.routes}`);
        }

        setManifest(m);

        // resolveScreens may throw if the manifest shape is unexpected
        const resolved = resolveScreens(m.routes);
        if (cancelled) return;

        if (!resolved || resolved.length === 0) {
          throw new Error('No screens resolved from manifest');
        }

        setScreens(resolved);
      } catch (e) {
        if (!cancelled) {
          const msg = e instanceof Error ? e.message : String(e);
          console.error('[AppNavigator] Manifest load failed:', msg);

          // If it's a 401, don't show error — the auth interceptor will sign out
          if (msg.includes('401') || msg.includes('Unauthorized')) {
            return;
          }

          setError(`Failed to load app manifest: ${msg}`);
        }
      }
    }

    load();
    return () => { cancelled = true; };
  }, [retryCount]);

  const handleRetry = useCallback(() => {
    setError(null);
    setScreens(null);
    setRetryCount((c) => c + 1);
  }, []);

  const handleSignOut = useCallback(async () => {
    try {
      const { signOut } = useAuthStore.getState();
      await signOut();
    } catch (e) {
      console.warn('[AppNavigator] signOut failed:', e);
    }
  }, []);

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{error}</Text>
        <Text style={styles.retryText} onPress={handleRetry}>
          Tap to retry
        </Text>
        <Text style={[styles.retryText, { marginTop: 16, color: '#ef4444' }]} onPress={handleSignOut}>
          Sign out and start fresh
        </Text>
      </View>
    );
  }

  if (!screens) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#6366f1" />
        <Text style={styles.loadingText}>Loading manifest...</Text>
      </View>
    );
  }

  // Wrap each screen component with ScreenErrorBoundary (stable refs via useMemo)
  const wrappedScreens = useMemo(
    () =>
      screens.map((screen) => ({
        ...screen,
        WrappedComponent: wrapWithErrorBoundary(screen.entry.component, screen.label),
      })),
    [screens],
  );

  return (
    <NavigationContainer linking={linking}>
      <Drawer.Navigator
        initialRouteName="/"
        screenOptions={{
          headerStyle: { backgroundColor: '#0a0a0f' },
          headerTintColor: '#ffffff',
          headerTitleStyle: { fontWeight: '600' },
          drawerStyle: { backgroundColor: '#0a0a0f', width: 280 },
          drawerActiveTintColor: '#6366f1',
          drawerInactiveTintColor: '#9ca3af',
          drawerLabelStyle: { fontSize: 15 },
        }}
      >
        {wrappedScreens.map((screen) => (
          <Drawer.Screen
            key={screen.path}
            name={screen.path}
            component={screen.WrappedComponent}
            options={{
              title: screen.label,
              drawerItemStyle: screen.category === 'admin' && manifest?.user_role !== 'admin'
                ? { display: 'none' }
                : undefined,
            }}
            initialParams={{ manifestPath: screen.path, category: screen.category }}
          />
        ))}
        {/* VIP Accept — hidden from drawer, accessible via deep link */}
        <Drawer.Screen
          name="VIPAccept"
          component={VIPAcceptScreen}
          options={{ drawerItemStyle: { display: 'none' }, title: 'VIP Invite' }}
        />
      </Drawer.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    backgroundColor: '#0a0a0f',
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    color: '#6b7280',
    fontSize: 14,
    marginTop: 12,
  },
  errorText: {
    color: '#ef4444',
    fontSize: 16,
    marginBottom: 12,
  },
  retryText: {
    color: '#6366f1',
    fontSize: 14,
    fontWeight: '600',
  },
});
