import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

// Placeholder — replaced by full boardroom in PR-6

export default function BoardroomHomeScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Boardroom</Text>
      <Text style={styles.hint}>Attention + Decisions coming in PR-6</Text>
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
