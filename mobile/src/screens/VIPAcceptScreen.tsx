/**
 * VIPAcceptScreen — handles magic-link token exchange.
 *
 * Opened via deep link: donkeybetz://vip/accept?token=xxx
 * Or web: https://donkeybetz.com/vip/accept?token=xxx
 *
 * Exchanges the token for API credentials, stores them, and navigates
 * to the Dashboard in VIP demo mode.
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ActivityIndicator,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { exchangeVIPToken } from '../api/vipInvite';
import { useDemoStore } from '../demo/demoStore';

type Status = 'loading' | 'success' | 'error';

export default function VIPAcceptScreen() {
  const route = useRoute();
  const navigation = useNavigation<any>();
  const [status, setStatus] = useState<Status>('loading');
  const [error, setError] = useState('');

  useEffect(() => {
    const token = (route.params as any)?.token;
    if (!token) {
      setStatus('error');
      setError('No invite token provided.');
      return;
    }

    (async () => {
      try {
        const creds = await exchangeVIPToken(token);
        // Store API key for authenticated requests
        await AsyncStorage.setItem('api_key', creds.api_key);
        await AsyncStorage.setItem('vip_username', creds.username);
        await AsyncStorage.setItem('vip_expires_at', creds.expires_at);

        // Enable demo mode automatically for VIP users
        useDemoStore.getState().toggle();

        setStatus('success');

        // Navigate to Dashboard after short delay
        setTimeout(() => {
          navigation.reset({ index: 0, routes: [{ name: 'Dashboard' }] });
        }, 2000);
      } catch (err: any) {
        setStatus('error');
        setError(err?.response?.data?.error || err?.message || 'Failed to accept invite.');
      }
    })();
  }, [route.params, navigation]);

  return (
    <View style={styles.container}>
      {status === 'loading' && (
        <>
          <ActivityIndicator size="large" color="#a855f7" />
          <Text style={styles.text}>Accepting your VIP invite...</Text>
        </>
      )}
      {status === 'success' && (
        <>
          <Text style={styles.checkmark}>✓</Text>
          <Text style={styles.title}>Welcome, VIP!</Text>
          <Text style={styles.text}>Your demo access is ready. Redirecting...</Text>
        </>
      )}
      {status === 'error' && (
        <>
          <Text style={styles.errorIcon}>✕</Text>
          <Text style={styles.title}>Invite Error</Text>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity
            style={styles.button}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.buttonText}>Go Back</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f23',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  checkmark: {
    fontSize: 64,
    color: '#22c55e',
    marginBottom: 16,
  },
  errorIcon: {
    fontSize: 64,
    color: '#ef4444',
    marginBottom: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#fff',
    marginBottom: 8,
  },
  text: {
    fontSize: 16,
    color: '#9ca3af',
    textAlign: 'center',
    marginTop: 12,
  },
  errorText: {
    fontSize: 16,
    color: '#fca5a5',
    textAlign: 'center',
    marginTop: 8,
  },
  button: {
    marginTop: 24,
    backgroundColor: '#a855f7',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
