import React, { useEffect, useState } from 'react';
import {
  Alert,
  Clipboard,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import Constants from 'expo-constants';
import * as Application from 'expo-application';
import * as Notifications from 'expo-notifications';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuthStore } from '../../auth/authStore';
import { clearToken, clearStoredUser } from '../../auth/tokenStore';

// ── Screen ───────────────────────────────────────────────────────────────────

export default function SettingsScreen() {
  const user = useAuthStore((s) => s.user);
  const signOut = useAuthStore((s) => s.signOut);

  const [pushToken, setPushToken] = useState<string>('');
  const [pushPermission, setPushPermission] = useState<string>('');

  useEffect(() => {
    (async () => {
      const stored = await AsyncStorage.getItem('last_registered_push_token');
      setPushToken(stored ?? 'not registered');

      const { status } = await Notifications.getPermissionsAsync();
      setPushPermission(status);
    })();
  }, []);

  const handleLogout = () => {
    Alert.alert('Log Out', 'Are you sure you want to log out?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Log Out', style: 'destructive', onPress: () => signOut() },
    ]);
  };

  const handleClearCache = () => {
    Alert.alert(
      'Clear Local Data',
      'This will clear cached data and sign you out. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear & Sign Out',
          style: 'destructive',
          onPress: async () => {
            await AsyncStorage.clear();
            await clearToken();
            await clearStoredUser();
            signOut();
          },
        },
      ],
    );
  };

  const copyToClipboard = (value: string, label: string) => {
    Clipboard.setString(value);
    Alert.alert('Copied', `${label} copied to clipboard`);
  };

  const apiBaseUrl = Constants.expoConfig?.extra?.apiBaseUrl ?? 'not set';
  const appVersion = Constants.expoConfig?.version ?? 'unknown';
  const nativeBuild = Application.nativeApplicationVersion ?? 'unknown';
  const expoSdk = Constants.expoConfig?.sdkVersion ?? 'unknown';

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Settings</Text>

      {/* Account */}
      <Section title="Account">
        <Row label="Username" value={user?.username ?? 'unknown'} />
        <Row label="Email" value={user?.email ?? 'unknown'} />
        <Row label="Role" value={user?.platform_role ?? 'unknown'} />
        <Row label="Subscription" value={user?.subscription ?? 'unknown'} />
        <Row label="Credits" value={String(user?.credits ?? 0)} />
      </Section>

      {/* Session */}
      <Section title="Session">
        <ActionRow label="Log Out" color="#ef4444" onPress={handleLogout} />
        <ActionRow label="Clear Local Data & Sign Out" color="#f97316" onPress={handleClearCache} />
      </Section>

      {/* Push Notifications */}
      <Section title="Push Notifications">
        <Row label="Permission" value={pushPermission} />
        <TouchableOpacity onPress={() => copyToClipboard(pushToken, 'Push token')}>
          <Row
            label="Token"
            value={pushToken.length > 30 ? pushToken.slice(0, 30) + '...' : pushToken}
          />
          <Text style={styles.copyHint}>Tap to copy</Text>
        </TouchableOpacity>
      </Section>

      {/* Build Info */}
      <Section title="Build">
        <Row label="Version" value={appVersion} />
        <Row label="Native Build" value={nativeBuild} />
        <Row label="Expo SDK" value={expoSdk} />
        <TouchableOpacity onPress={() => copyToClipboard(apiBaseUrl, 'API URL')}>
          <Row label="API Base URL" value={apiBaseUrl} />
          <Text style={styles.copyHint}>Tap to copy</Text>
        </TouchableOpacity>
      </Section>

      <View style={{ height: 60 }} />
    </ScrollView>
  );
}

// ── Components ──────────────────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {children}
    </View>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
    </View>
  );
}

function ActionRow({
  label,
  color,
  onPress,
}: {
  label: string;
  color: string;
  onPress: () => void;
}) {
  return (
    <TouchableOpacity style={styles.actionRow} onPress={onPress}>
      <Text style={[styles.actionLabel, { color }]}>{label}</Text>
    </TouchableOpacity>
  );
}

// ── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f' },
  content: { padding: 16 },
  title: { color: '#ffffff', fontSize: 22, fontWeight: '700', marginBottom: 16 },

  section: {
    backgroundColor: '#1a1a2e',
    borderRadius: 10,
    padding: 14,
    marginBottom: 10,
  },
  sectionTitle: {
    color: '#818cf8',
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
    marginBottom: 10,
  },

  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  label: { color: '#6b7280', fontSize: 13 },
  value: {
    color: '#d1d5db',
    fontSize: 13,
    fontWeight: '500',
    maxWidth: '60%',
    textAlign: 'right',
  },
  copyHint: {
    color: '#6366f1',
    fontSize: 10,
    textAlign: 'right',
    marginTop: 2,
    marginBottom: 4,
  },

  actionRow: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  actionLabel: {
    fontSize: 15,
    fontWeight: '600',
  },
});
