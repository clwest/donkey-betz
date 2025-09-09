import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../styles/theme';

export default function CampaignScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Campaign Screen</Text>
      <Text style={styles.subtitle}>Multi-Channel Marketing</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
  },
  subtitle: {
    fontSize: 18,
    color: theme.colors.text.secondary,
    marginTop: 8,
  },
});