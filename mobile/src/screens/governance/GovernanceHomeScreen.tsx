import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

// Placeholder — replaced by full governance in PR-7

export default function GovernanceHomeScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Governance</Text>
      <Text style={styles.hint}>Classification + Gates coming in PR-7</Text>
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
