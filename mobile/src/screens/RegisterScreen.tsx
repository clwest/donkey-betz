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

interface RegisterScreenProps {
  onNavigateToLogin: () => void;
  onRegisterSuccess: () => void;
}

export default function RegisterScreen({ onNavigateToLogin, onRegisterSuccess }: RegisterScreenProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const { register, isLoading, error, clearError } = useAuthStore();

  const validateForm = () => {
    if (!name.trim()) {
      Alert.alert('Error', 'Please enter your name');
      return false;
    }
    
    if (!email.trim()) {
      Alert.alert('Error', 'Please enter your email');
      return false;
    }
    
    if (!email.includes('@')) {
      Alert.alert('Error', 'Please enter a valid email address');
      return false;
    }
    
    if (!password) {
      Alert.alert('Error', 'Please enter a password');
      return false;
    }
    
    if (password.length < 6) {
      Alert.alert('Error', 'Password must be at least 6 characters long');
      return false;
    }
    
    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return false;
    }
    
    return true;
  };

  const handleRegister = async () => {
    if (!validateForm()) return;

    try {
      await register(email, password, name);
      if (Platform.OS !== 'web') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }
      onRegisterSuccess();
    } catch (error: any) {
      if (Platform.OS !== 'web') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      }
      Alert.alert('Registration Failed', error.userMessage || 'Please check your information and try again.');
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
          <Text style={styles.headerSubtitle}>Create your account to get started</Text>
        </LinearGradient>

        {/* Register Form */}
        <BlurView intensity={80} tint="dark" style={styles.formContainer}>
          <View style={styles.form}>
            <Text style={styles.formTitle}>Create Account</Text>
            
            {error && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorText}>{error}</Text>
                <TouchableOpacity onPress={clearError} style={styles.errorClose}>
                  <Text style={styles.errorCloseText}>×</Text>
                </TouchableOpacity>
              </View>
            )}

            {/* Name Input */}
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Full Name</Text>
              <TextInput
                style={styles.input}
                value={name}
                onChangeText={setName}
                placeholder="Your full name"
                placeholderTextColor={theme.colors.text.secondary}
                autoCapitalize="words"
                autoCorrect={false}
              />
            </View>

            {/* Email Input */}
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Email</Text>
              <TextInput
                style={styles.input}
                value={email}
                onChangeText={setEmail}
                placeholder="your@email.com"
                placeholderTextColor={theme.colors.text.secondary}
                keyboardType="email-address"
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
                  placeholder="Create a password (min 6 chars)"
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

            {/* Confirm Password Input */}
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Confirm Password</Text>
              <View style={styles.passwordContainer}>
                <TextInput
                  style={styles.passwordInput}
                  value={confirmPassword}
                  onChangeText={setConfirmPassword}
                  placeholder="Confirm your password"
                  placeholderTextColor={theme.colors.text.secondary}
                  secureTextEntry={!showConfirmPassword}
                  autoCapitalize="none"
                  autoCorrect={false}
                />
                <TouchableOpacity
                  style={styles.passwordToggle}
                  onPress={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  <Text style={styles.passwordToggleText}>
                    {showConfirmPassword ? '🙈' : '👁️'}
                  </Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Register Button */}
            <TouchableOpacity
              style={[styles.registerButton, isLoading && styles.registerButtonDisabled]}
              onPress={handleRegister}
              disabled={isLoading}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={theme.colors.primary.gradient}
                style={styles.registerButtonGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
              >
                {isLoading ? (
                  <ActivityIndicator size="small" color="white" />
                ) : (
                  <Text style={styles.registerButtonText}>Create Account</Text>
                )}
              </LinearGradient>
            </TouchableOpacity>

            {/* Login Link */}
            <View style={styles.loginContainer}>
              <Text style={styles.loginText}>Already have an account? </Text>
              <TouchableOpacity onPress={onNavigateToLogin}>
                <Text style={styles.loginLink}>Sign in here</Text>
              </TouchableOpacity>
            </View>

            {/* Terms Note */}
            <View style={styles.termsContainer}>
              <Text style={styles.termsText}>
                By creating an account, you agree to our Terms of Service and Privacy Policy
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
  registerButton: {
    borderRadius: 12,
    overflow: 'hidden',
    marginTop: 10,
    marginBottom: 20,
  },
  registerButtonDisabled: {
    opacity: 0.6,
  },
  registerButtonGradient: {
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
  },
  registerButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  loginText: {
    color: theme.colors.text.secondary,
    fontSize: 16,
  },
  loginLink: {
    color: theme.colors.primary.main,
    fontSize: 16,
    fontWeight: '600',
  },
  termsContainer: {
    backgroundColor: theme.colors.background.tertiary,
    padding: 12,
    borderRadius: 8,
    marginTop: 10,
  },
  termsText: {
    color: theme.colors.text.secondary,
    fontSize: 12,
    textAlign: 'center',
    lineHeight: 18,
  },
});