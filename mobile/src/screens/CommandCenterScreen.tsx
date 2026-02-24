import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { useAuthStore } from '../auth/authStore';

// Placeholder — replaced by full PA chat implementation in PR-4

export default function CommandCenterScreen() {
  const user = useAuthStore((s) => s.user);

  return (
    <View style={styles.container}>
      <Text style={styles.greeting}>Welcome, {user?.username}</Text>
      <Text style={styles.subtitle}>Command Center</Text>
      <Text style={styles.hint}>PA chat coming in PR-4</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0f',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  greeting: {
    color: '#ffffff',
    fontSize: 22,
    fontWeight: '700',
    marginBottom: 8,
  },
  subtitle: {
    color: '#d1d5db',
    fontSize: 16,
    marginBottom: 16,
  },
  hint: {
    color: '#6b7280',
    fontSize: 13,
  },
});
