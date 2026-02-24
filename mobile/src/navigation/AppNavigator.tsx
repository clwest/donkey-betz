import React, { useEffect, useState } from 'react';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createDrawerNavigator } from '@react-navigation/drawer';
import { getManifest, type Manifest } from '../api/manifest';
import { resolveScreens, type ResolvedScreen } from './manifestRouter';
import { linking } from './linking';
import { useAuthStore } from '../auth/authStore';

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

// ── Navigator ────────────────────────────────────────────────────────────────

export default function AppNavigator() {
  const user = useAuthStore((s) => s.user);
  const [screens, setScreens] = useState<ResolvedScreen[] | null>(null);
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const m = await getManifest();
        if (cancelled) return;
        setManifest(m);
        setScreens(resolveScreens(m.routes));
      } catch {
        if (!cancelled) setError('Failed to load app manifest');
      }
    }

    load();
    return () => { cancelled = true; };
  }, []);

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{error}</Text>
        <Text style={styles.retryText} onPress={() => { setError(null); setScreens(null); }}>
          Tap to retry
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
        {screens.map((screen) => (
          <Drawer.Screen
            key={screen.path}
            name={screen.path}
            component={screen.entry.component}
            options={{
              title: screen.label,
              drawerItemStyle: screen.category === 'admin' && manifest?.user_role !== 'admin'
                ? { display: 'none' }
                : undefined,
            }}
            initialParams={{ manifestPath: screen.path, category: screen.category }}
          />
        ))}
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
