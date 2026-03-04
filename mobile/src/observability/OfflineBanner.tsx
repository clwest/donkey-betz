import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import NetInfo from '@react-native-community/netinfo';

/**
 * Displays a banner at the top of the screen when the device is offline.
 * Automatically subscribes to network state changes.
 */
export default function OfflineBanner() {
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
    let unsubscribe: (() => void) | undefined;
    try {
      unsubscribe = NetInfo.addEventListener((state) => {
        try {
          setIsOffline(!(state.isConnected && state.isInternetReachable !== false));
        } catch (e) {
          console.warn('[OfflineBanner] Error processing network state:', e);
        }
      });
    } catch (e) {
      console.warn('[OfflineBanner] NetInfo.addEventListener failed:', e);
    }
    return () => {
      try { unsubscribe?.(); } catch { /* ignore cleanup errors */ }
    };
  }, []);

  if (!isOffline) return null;

  return (
    <View style={styles.banner}>
      <Text style={styles.text}>No internet connection</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    backgroundColor: '#dc2626',
    paddingVertical: 6,
    paddingHorizontal: 16,
    alignItems: 'center',
  },
  text: {
    color: '#ffffff',
    fontSize: 13,
    fontWeight: '600',
  },
});
