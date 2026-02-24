import { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';
import { useAuthStore } from './src/auth/authStore';
import LoginScreen from './src/screens/auth/LoginScreen';

export default function App() {
  const status = useAuthStore((s) => s.status);
  const user = useAuthStore((s) => s.user);
  const hydrate = useAuthStore((s) => s.hydrate);
  const signOut = useAuthStore((s) => s.signOut);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  if (status === 'loading') {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#6366f1" />
        <StatusBar style="light" />
      </View>
    );
  }

  if (status === 'signedOut') {
    return (
      <>
        <LoginScreen />
        <StatusBar style="light" />
      </>
    );
  }

  // Signed in — placeholder until PR-3 adds manifest-driven navigation
  return (
    <View style={styles.container}>
      <Text style={styles.title}>DonkeyBetz</Text>
      <Text style={styles.greeting}>Welcome, {user?.username}</Text>
      <Text style={styles.role}>{user?.platform_role ?? 'viewer'}</Text>
      <Text style={styles.signOut} onPress={signOut}>
        Sign Out
      </Text>
      <StatusBar style="light" />
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
    fontSize: 28,
    fontWeight: '700',
    marginBottom: 8,
  },
  greeting: {
    color: '#d1d5db',
    fontSize: 18,
    marginBottom: 4,
  },
  role: {
    color: '#6b7280',
    fontSize: 14,
    marginBottom: 24,
  },
  signOut: {
    color: '#6366f1',
    fontSize: 16,
    fontWeight: '600',
  },
});
