import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

// Placeholder — replaced by full dashboard in PR-5

export default function DashboardScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Dashboard</Text>
      <Text style={styles.hint}>Health + stats coming in PR-5</Text>
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
  title: {
    color: '#ffffff',
    fontSize: 22,
    fontWeight: '700',
    marginBottom: 8,
  },
  hint: {
    color: '#6b7280',
    fontSize: 13,
  },
});
