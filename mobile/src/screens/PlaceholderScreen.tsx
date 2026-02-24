import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

export default function PlaceholderScreen({ route }: any) {
  const path = route?.params?.manifestPath ?? 'unknown';
  const category = route?.params?.category ?? '';

  return (
    <View style={styles.container}>
      <Text style={styles.path}>{path}</Text>
      <Text style={styles.label}>Coming soon</Text>
      <Text style={styles.category}>{category}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0f',
    alignItems: 'center',
    justifyContent: 'center',
  },
  path: {
    color: '#6366f1',
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 8,
  },
  label: {
    color: '#6b7280',
    fontSize: 16,
    marginBottom: 4,
  },
  category: {
    color: '#4b5563',
    fontSize: 12,
  },
});
