import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { useDemoStore } from './demoStore';

export default function DemoBanner() {
  const enabled = useDemoStore((s) => s.enabled);
  if (!enabled) return null;

  return (
    <View style={styles.banner}>
      <Text style={styles.text}>VIP DEMO MODE</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    backgroundColor: '#6366f1',
    paddingVertical: 4,
    alignItems: 'center',
  },
  text: {
    color: '#ffffff',
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 1.5,
  },
});
