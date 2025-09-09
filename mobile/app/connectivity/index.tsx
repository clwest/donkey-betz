import React from 'react';
import { View, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { theme } from '../../src/styles/theme';
import { ConnectivityDashboard } from '../features/connectivity/ConnectivityDashboard';

export default function ConnectivityMonitorScreen() {
  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#0A0A0F', '#1C1C25']}
        style={StyleSheet.absoluteFillObject}
      />

      <SafeAreaView style={styles.safeArea}>
        <ConnectivityDashboard />
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  safeArea: {
    flex: 1,
  },
});