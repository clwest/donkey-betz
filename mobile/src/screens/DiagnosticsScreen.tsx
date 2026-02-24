import React, { useEffect, useState } from 'react';
import {
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import Constants from 'expo-constants';
import * as Application from 'expo-application';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuthStore } from '../auth/authStore';

interface DiagInfo {
  appVersion: string;
  nativeVersion: string;
  expoSdk: string;
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
  const user = useAuthStore((s) => s.user);
  const status = useAuthStore((s) => s.status);
  const [info, setInfo] = useState<DiagInfo | null>(null);

  useEffect(() => {
    async function gather() {
      const pushToken = (await AsyncStorage.getItem('last_registered_push_token')) ?? 'none';
      const activeConvo = (await AsyncStorage.getItem('active_conversation_id')) ?? 'none';

      setInfo({
        appVersion: Constants.expoConfig?.version ?? 'unknown',
        nativeVersion: Application.nativeApplicationVersion ?? 'unknown',
        expoSdk: Constants.expoConfig?.sdkVersion ?? 'unknown',
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
          <Section title="App">
            <Row label="Version" value={info.appVersion} />
            <Row label="Native Build" value={info.nativeVersion} />
            <Row label="Expo SDK" value={info.expoSdk} />
            <Row label="Runtime Version" value={info.runtimeVersion} />
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
});
