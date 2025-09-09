import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { theme } from '../styles/theme';
import { useAuthStore } from '../store/authStore';

interface LoginScreenProps {
  onNavigateToRegister: () => void;
  onLoginSuccess: () => void;
}

export default function LoginScreen({ onNavigateToRegister, onLoginSuccess }: LoginScreenProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  
  const { login, isLoading, error, clearError } = useAuthStore();

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('Error', 'Please enter both username and password');
      return;
    }

    try {
      await login(username, password);
      if (Platform.OS !== 'web') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }
      onLoginSuccess();
    } catch (error: any) {
      if (Platform.OS !== 'web') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      }
      Alert.alert('Login Failed', error.userMessage || 'Please check your credentials and try again.');
    }
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        {/* Header */}
        <LinearGradient
          colors={['#667eea', '#764ba2']}
          style={styles.header}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
        >
          <Text style={styles.headerTitle}>✨ Donkey Betz</Text>
          <Text style={styles.headerSubtitle}>Sign in to continue creating</Text>
        </LinearGradient>

        {/* Login Form */}
        <BlurView intensity={80} tint="dark" style={styles.formContainer}>
          <View style={styles.form}>
            <Text style={styles.formTitle}>Welcome Back</Text>
            
            {error && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorText}>{error}</Text>
                <TouchableOpacity onPress={clearError} style={styles.errorClose}>
                  <Text style={styles.errorCloseText}>×</Text>
                </TouchableOpacity>
              </View>
            )}

            {/* Username Input */}
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Username</Text>
              <TextInput
                style={styles.input}
                value={username}
                onChangeText={setUsername}
                placeholder="Enter your username"
                placeholderTextColor={theme.colors.text.secondary}
                autoCapitalize="none"
                autoCorrect={false}
              />
            </View>

            {/* Password Input */}
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Password</Text>
              <View style={styles.passwordContainer}>
                <TextInput
                  style={styles.passwordInput}
                  value={password}
                  onChangeText={setPassword}
                  placeholder="Enter your password"
                  placeholderTextColor={theme.colors.text.secondary}
                  secureTextEntry={!showPassword}
                  autoCapitalize="none"
                  autoCorrect={false}
                />
                <TouchableOpacity
                  style={styles.passwordToggle}
                  onPress={() => setShowPassword(!showPassword)}
                >
                  <Text style={styles.passwordToggleText}>
                    {showPassword ? '🙈' : '👁️'}
                  </Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Login Button */}
            <TouchableOpacity
              style={[styles.loginButton, isLoading && styles.loginButtonDisabled]}
              onPress={handleLogin}
              disabled={isLoading}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={theme.colors.primary.gradient}
                style={styles.loginButtonGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
              >
                {isLoading ? (
                  <ActivityIndicator size="small" color="white" />
                ) : (
                  <Text style={styles.loginButtonText}>Sign In</Text>
                )}
              </LinearGradient>
            </TouchableOpacity>

            {/* Register Link */}
            <View style={styles.registerContainer}>
              <Text style={styles.registerText}>Don't have an account? </Text>
              <TouchableOpacity onPress={onNavigateToRegister}>
                <Text style={styles.registerLink}>Sign up here</Text>
              </TouchableOpacity>
            </View>

            {/* Demo Note */}
            <View style={styles.demoContainer}>
              <Text style={styles.demoText}>
                📝 Demo Mode: Use username 'chris' or 'testuser' to explore the app
              </Text>
            </View>
          </View>
        </BlurView>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  scrollContainer: {
    flexGrow: 1,
  },
  header: {
    padding: 40,
    paddingTop: 80,
    alignItems: 'center',
    minHeight: 200,
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
    textAlign: 'center',
  },
  headerSubtitle: {
    fontSize: 18,
    color: 'rgba(255, 255, 255, 0.8)',
    textAlign: 'center',
  },
  formContainer: {
    flex: 1,
    margin: 20,
    marginTop: -20,
    borderRadius: 20,
    overflow: 'hidden',
    backgroundColor: Platform.OS === 'android' ? theme.colors.background.secondary : 'transparent',
  },
  form: {
    padding: 30,
    paddingTop: 40,
  },
  formTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    textAlign: 'center',
    marginBottom: 30,
  },
  errorContainer: {
    backgroundColor: '#ff4757',
    padding: 12,
    borderRadius: 8,
    marginBottom: 20,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  errorText: {
    color: 'white',
    fontSize: 14,
    flex: 1,
  },
  errorClose: {
    padding: 4,
  },
  errorCloseText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  inputContainer: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text.primary,
    marginBottom: 8,
  },
  input: {
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: theme.colors.text.primary,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
  },
  passwordContainer: {
    position: 'relative',
  },
  passwordInput: {
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: 12,
    padding: 16,
    paddingRight: 50,
    fontSize: 16,
    color: theme.colors.text.primary,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
  },
  passwordToggle: {
    position: 'absolute',
    right: 12,
    top: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    width: 40,
  },
  passwordToggleText: {
    fontSize: 18,
  },
  loginButton: {
    borderRadius: 12,
    overflow: 'hidden',
    marginTop: 10,
    marginBottom: 20,
  },
  loginButtonDisabled: {
    opacity: 0.6,
  },
  loginButtonGradient: {
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
  },
  loginButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  registerContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  registerText: {
    color: theme.colors.text.secondary,
    fontSize: 16,
  },
  registerLink: {
    color: theme.colors.primary.main,
    fontSize: 16,
    fontWeight: '600',
  },
  demoContainer: {
    backgroundColor: theme.colors.background.tertiary,
    padding: 12,
    borderRadius: 8,
    marginTop: 10,
  },
  demoText: {
    color: theme.colors.text.secondary,
    fontSize: 14,
    textAlign: 'center',
    lineHeight: 20,
  },
});