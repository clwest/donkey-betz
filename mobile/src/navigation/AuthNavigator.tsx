import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';

interface AuthNavigatorProps {
  onAuthSuccess: () => void;
}

export default function AuthNavigator({ onAuthSuccess }: AuthNavigatorProps) {
  const [currentScreen, setCurrentScreen] = useState<'login' | 'register'>('login');

  const navigateToLogin = () => setCurrentScreen('login');
  const navigateToRegister = () => setCurrentScreen('register');

  return (
    <View style={styles.container}>
      {currentScreen === 'login' ? (
        <LoginScreen
          onNavigateToRegister={navigateToRegister}
          onLoginSuccess={onAuthSuccess}
        />
      ) : (
        <RegisterScreen
          onNavigateToLogin={navigateToLogin}
          onRegisterSuccess={onAuthSuccess}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});