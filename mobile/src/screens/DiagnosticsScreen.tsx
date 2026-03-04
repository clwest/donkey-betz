import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Clipboard,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import Constants from 'expo-constants';
import * as Application from 'expo-application';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuthStore } from '../auth/authStore';
import { toast } from '../components/Toast';
import { useScreenAnalytics } from '../observability/analytics';

interface DiagInfo {
  appVersion: string;
  nativeVersion: string;
  expoSdk: string;
  buildSha: string;
  buildChannel: string;
  deviceOs: string;
  apiBaseUrl: string;
  authStatus: string;
  username: string;
  platformRole: string;
  pushToken: string;
  activeConversation: string;
  lastRefresh: string;
  runtimeVersion: string;
}

export default function DiagnosticsScreen() {
  useScreenAnalytics('DiagnosticsScreen');
  const user = useAuthStore((s) => s.user);
  const status = useAuthStore((s) => s.status);
  const hydrate = useAuthStore((s) => s.hydrate);
  const [info, setInfo] = useState<DiagInfo | null>(null);
  const [revalidating, setRevalidating] = useState(false);

  async function handleRevalidate() {
    setRevalidating(true);
    try {
      await hydrate();
      toast.success('Token revalidated — user data refreshed');
    } catch {
      toast.error('Revalidation failed');
    } finally {
      setRevalidating(false);
    }
  }

  useEffect(() => {
    async function gather() {
      const pushToken = (await AsyncStorage.getItem('last_registered_push_token')) ?? 'none';
      const activeConvo = (await AsyncStorage.getItem('active_conversation_id')) ?? 'none';

      setInfo({
        appVersion: Constants.expoConfig?.version ?? 'unknown',
        nativeVersion: Application.nativeApplicationVersion ?? 'unknown',
        expoSdk: Constants.expoConfig?.sdkVersion ?? 'unknown',
        buildSha: Constants.expoConfig?.extra?.buildSha ?? process.env.EXPO_PUBLIC_BUILD_SHA ?? 'dev',
        buildChannel: (Constants as any).expoGoConfig?.debugMode ? 'development' : (Constants.expoConfig?.extra?.eas?.buildProfile ?? 'unknown'),
        deviceOs: `${Platform.OS} ${Platform.Version}`,
        apiBaseUrl: Constants.expoConfig?.extra?.apiBaseUrl ?? 'not set',
        authStatus: status,
        username: user?.username ?? 'anonymous',
        platformRole: user?.platform_role ?? 'unknown',
        pushToken: pushToken.length > 30 ? pushToken.slice(0, 30) + '...' : pushToken,
        activeConversation: activeConvo !== 'none' ? activeConvo.slice(0, 12) + '...' : 'none',
        lastRefresh: new Date().toLocaleString(),
        runtimeVersion: typeof Constants.expoConfig?.runtimeVersion === 'string'
          ? Constants.expoConfig.runtimeVersion
          : JSON.stringify(Constants.expoConfig?.runtimeVersion ?? 'unknown'),
      });
    }
    gather();
  }, [user, status]);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Diagnostics</Text>
      <Text style={styles.subtitle}>Read-only system information</Text>

      {info ? (
        <>
          <View style={styles.buttonRow}>
            <TouchableOpacity style={styles.copyBtn} onPress={() => {
              const debugText = [
                `App: ${info.appVersion} (${info.nativeVersion})`,
                `SDK: ${info.expoSdk} | Runtime: ${info.runtimeVersion}`,
                `Build: ${info.buildSha} | Channel: ${info.buildChannel}`,
                `Device: ${info.deviceOs}`,
                `API: ${info.apiBaseUrl}`,
                `User: ${info.username} (${info.platformRole})`,
                `Auth: ${info.authStatus}`,
              ].join('\n');
              Clipboard.setString(debugText);
              toast.success('Debug info copied');
            }}>
              <Text style={styles.copyBtnText}>Copy Debug Info</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.copyBtn, styles.revalidateBtn]}
              onPress={handleRevalidate}
              disabled={revalidating}
            >
              {revalidating
                ? <ActivityIndicator size="small" color="#ffffff" />
                : <Text style={styles.copyBtnText}>Revalidate Token</Text>
              }
            </TouchableOpacity>
          </View>

          <Section title="App">
            <Row label="Version" value={info.appVersion} />
            <Row label="Native Build" value={info.nativeVersion} />
            <Row label="Expo SDK" value={info.expoSdk} />
            <Row label="Runtime Version" value={info.runtimeVersion} />
            <Row label="Build SHA" value={info.buildSha} />
            <Row label="Channel" value={info.buildChannel} />
          </Section>

          <Section title="Device">
            <Row label="OS" value={info.deviceOs} />
          </Section>

          <Section title="Connection">
            <Row label="API Base URL" value={info.apiBaseUrl} />
          </Section>

          <Section title="Auth">
            <Row label="Status" value={info.authStatus} />
            <Row label="User" value={info.username} />
            <Row label="Role" value={info.platformRole} />
          </Section>

          <Section title="Push Notifications">
            <Row label="Expo Token" value={info.pushToken} />
          </Section>

          <Section title="State">
            <Row label="Active Conversation" value={info.activeConversation} />
            <Row label="Gathered At" value={info.lastRefresh} />
          </Section>
        </>
      ) : (
        <Text style={styles.muted}>Gathering diagnostics...</Text>
      )}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

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
      <Text style={styles.value} selectable>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f' },
  content: { padding: 16 },
  title: { color: '#ffffff', fontSize: 22, fontWeight: '700', marginBottom: 4 },
  subtitle: { color: '#6b7280', fontSize: 13, marginBottom: 20 },
  muted: { color: '#6b7280', fontSize: 14 },

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
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  label: { color: '#6b7280', fontSize: 13 },
  value: { color: '#d1d5db', fontSize: 13, fontWeight: '500', maxWidth: '60%', textAlign: 'right' },

  buttonRow: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 16,
  },
  copyBtn: {
    flex: 1,
    backgroundColor: '#6366f1',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
  },
  revalidateBtn: {
    backgroundColor: '#374151',
  },
  copyBtnText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
});
