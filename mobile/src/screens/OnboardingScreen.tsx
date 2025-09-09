import React, { useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
  ScrollView,
  Animated,
  Platform,
  Image,
  TextInput,
  KeyboardAvoidingView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import { PremiumButton } from '../components/common/PremiumButton';
import { theme } from '../styles/theme';
import { useAuthStore } from '../store/authStore';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

interface OnboardingSlide {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  gradient: string[];
  icon: string;
}

const slides: OnboardingSlide[] = [
  {
    id: '1',
    title: 'AI-Powered Creation',
    subtitle: 'Create content in seconds',
    description: 'Generate blogs, social posts, images, and videos with cutting-edge AI technology',
    gradient: ['#6366F1', '#8B5CF6'],
    icon: '🚀',
  },
  {
    id: '2',
    title: 'Voice-First Design',
    subtitle: 'Speak your ideas into reality',
    description: 'Transform voice recordings into polished content with advanced transcription',
    gradient: ['#8B5CF6', '#EC4899'],
    icon: '🎙️',
  },
  {
    id: '3',
    title: 'Smart Memory',
    subtitle: 'Never lose an idea',
    description: 'AI remembers your preferences and learns from your style over time',
    gradient: ['#EC4899', '#F43F5E'],
    icon: '🧠',
  },
  {
    id: '4',
    title: 'Professional Results',
    subtitle: 'Studio-quality output',
    description: 'Create content that rivals $20k agencies with one-tap generation',
    gradient: ['#F43F5E', '#F97316'],
    icon: '✨',
  },
];

export default function OnboardingScreen({ navigation }: any) {
  const scrollX = useRef(new Animated.Value(0)).current;
  const scrollRef = useRef<ScrollView>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showLogin, setShowLogin] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuthStore();

  const handleScroll = Animated.event(
    [{ nativeEvent: { contentOffset: { x: scrollX } } }],
    {
      useNativeDriver: false,
      listener: (event: any) => {
        const index = Math.round(event.nativeEvent.contentOffset.x / SCREEN_WIDTH);
        setCurrentIndex(index);
      },
    }
  );

  const handleNext = () => {
    if (currentIndex < slides.length - 1) {
      scrollRef.current?.scrollTo({
        x: (currentIndex + 1) * SCREEN_WIDTH,
        animated: true,
      });
    } else {
      handleGetStarted();
    }
  };

  const handleGetStarted = () => {
    setShowLogin(true);
  };

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please enter email and password');
      return;
    }

    setIsLoading(true);
    try {
      // For demo, accept any credentials or use test credentials
      // In production, this would validate with your backend
      if (email === 'demo' || email === 'test') {
        await login('testuser', 'testpass123');
      } else {
        await login(email, password);
      }
      // Navigation happens automatically via auth state change
    } catch (error) {
      Alert.alert(
        'Login Failed',
        'Unable to connect. For demo, use:\nEmail: demo\nPassword: any',
        [{ text: 'OK' }]
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setIsLoading(true);
    try {
      await login('testuser', 'testpass123');
    } catch (error) {
      Alert.alert('Error', 'Unable to connect to demo account');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#0A0A0F', '#1C1C25']}
        style={StyleSheet.absoluteFillObject}
      />
      
      {/* Animated background gradient */}
      {slides.map((slide, index) => {
        const inputRange = [
          (index - 1) * SCREEN_WIDTH,
          index * SCREEN_WIDTH,
          (index + 1) * SCREEN_WIDTH,
        ];
        
        const opacity = scrollX.interpolate({
          inputRange,
          outputRange: [0, 1, 0],
          extrapolate: 'clamp',
        });

        return (
          <Animated.View
            key={slide.id}
            style={[StyleSheet.absoluteFillObject, { opacity }]}
          >
            <LinearGradient
              colors={[...slide.gradient, 'transparent']}
              style={[StyleSheet.absoluteFillObject, { opacity: 0.3 }]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
            />
          </Animated.View>
        );
      })}

      <SafeAreaView style={styles.safeArea}>
        {/* Skip button */}
        {currentIndex < slides.length - 1 && (
          <View style={styles.skipContainer}>
            <PremiumButton
              title="Skip"
              onPress={handleGetStarted}
              variant="glass"
              size="small"
            />
          </View>
        )}

        {/* Slides */}
        <ScrollView
          ref={scrollRef}
          horizontal
          pagingEnabled
          showsHorizontalScrollIndicator={false}
          onScroll={handleScroll}
          scrollEventThrottle={16}
        >
          {slides.map((slide, index) => (
            <View key={slide.id} style={styles.slide}>
              <View style={styles.slideContent}>
                {/* Icon with glow effect */}
                <View style={styles.iconContainer}>
                  <Text style={styles.icon}>{slide.icon}</Text>
                  <View style={styles.iconGlow} />
                </View>

                {/* Title */}
                <Text style={styles.title}>{slide.title}</Text>

                {/* Subtitle with gradient */}
                <LinearGradient
                  colors={slide.gradient}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={styles.subtitleContainer}
                >
                  <Text style={styles.subtitle}>{slide.subtitle}</Text>
                </LinearGradient>

                {/* Description */}
                <Text style={styles.description}>{slide.description}</Text>
              </View>
            </View>
          ))}
        </ScrollView>

        {/* Bottom section */}
        <View style={styles.bottomSection}>
          {/* Page indicators */}
          <View style={styles.pagination}>
            {slides.map((_, index) => {
              const inputRange = [
                (index - 1) * SCREEN_WIDTH,
                index * SCREEN_WIDTH,
                (index + 1) * SCREEN_WIDTH,
              ];

              const dotWidth = scrollX.interpolate({
                inputRange,
                outputRange: [8, 24, 8],
                extrapolate: 'clamp',
              });

              const opacity = scrollX.interpolate({
                inputRange,
                outputRange: [0.3, 1, 0.3],
                extrapolate: 'clamp',
              });

              return (
                <Animated.View
                  key={index}
                  style={[
                    styles.dot,
                    {
                      width: dotWidth,
                      opacity,
                      backgroundColor: slides[currentIndex].gradient[0],
                    },
                  ]}
                />
              );
            })}
          </View>

          {/* Action buttons */}
          <View style={styles.buttonContainer}>
            <PremiumButton
              title={currentIndex === slides.length - 1 ? 'Get Started' : 'Next'}
              onPress={handleNext}
              variant="primary"
              size="large"
              glow
              style={styles.nextButton}
            />
          </View>
        </View>
      </SafeAreaView>

      {/* Login Modal */}
      {showLogin && (
        <View style={styles.loginModal}>
          <BlurView intensity={80} tint="dark" style={StyleSheet.absoluteFillObject} />
          <KeyboardAvoidingView 
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            style={styles.loginContent}
          >
            <View style={styles.loginCard}>
              <Text style={styles.loginTitle}>Welcome to AI Studio</Text>
              <Text style={styles.loginSubtitle}>Sign in to continue</Text>
              
              <TextInput
                style={styles.input}
                placeholder="Email or username"
                placeholderTextColor={theme.colors.text.tertiary}
                value={email}
                onChangeText={setEmail}
                autoCapitalize="none"
                keyboardType="email-address"
                editable={!isLoading}
              />
              
              <TextInput
                style={styles.input}
                placeholder="Password"
                placeholderTextColor={theme.colors.text.tertiary}
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                editable={!isLoading}
              />
              
              <PremiumButton
                title={isLoading ? '' : 'Sign In'}
                onPress={handleLogin}
                variant="primary"
                size="large"
                glow
                disabled={isLoading}
                style={styles.loginButton}
              >
                {isLoading && <ActivityIndicator size="small" color="white" />}
              </PremiumButton>
              
              <View style={styles.divider}>
                <View style={styles.dividerLine} />
                <Text style={styles.dividerText}>OR</Text>
                <View style={styles.dividerLine} />
              </View>
              
              <PremiumButton
                title="Try Demo Account"
                onPress={handleDemoLogin}
                variant="secondary"
                size="large"
                disabled={isLoading}
                style={styles.demoButton}
              />
              
              <Text style={styles.helpText}>
                Demo credentials: Use 'demo' as email
              </Text>
            </View>
          </KeyboardAvoidingView>
        </View>
      )}
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
  skipContainer: {
    position: 'absolute',
    top: theme.spacing.md,
    right: theme.spacing.lg,
    zIndex: 10,
  },
  slide: {
    width: SCREEN_WIDTH,
    height: SCREEN_HEIGHT,
    justifyContent: 'center',
    alignItems: 'center',
  },
  slideContent: {
    paddingHorizontal: theme.spacing.xl,
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
  },
  iconContainer: {
    width: 120,
    height: 120,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: theme.spacing.xl,
    position: 'relative',
  },
  icon: {
    fontSize: 72,
    zIndex: 2,
  },
  iconGlow: {
    position: 'absolute',
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: theme.colors.glow.purple,
    opacity: 0.3,
    transform: [{ scale: 1.5 }],
  },
  title: {
    ...theme.typography.displaySmall,
    color: theme.colors.text.primary,
    textAlign: 'center',
    marginBottom: theme.spacing.md,
  },
  subtitleContainer: {
    paddingVertical: theme.spacing.xs,
    paddingHorizontal: theme.spacing.md,
    borderRadius: theme.borderRadius.full,
    marginBottom: theme.spacing.lg,
  },
  subtitle: {
    ...theme.typography.titleMedium,
    color: theme.colors.text.primary,
    textAlign: 'center',
  },
  description: {
    ...theme.typography.bodyLarge,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    maxWidth: 320,
    lineHeight: 24,
  },
  bottomSection: {
    position: 'absolute',
    bottom: theme.spacing.xl,
    left: 0,
    right: 0,
    paddingHorizontal: theme.spacing.xl,
  },
  pagination: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: theme.spacing.xl,
  },
  dot: {
    height: 8,
    borderRadius: 4,
    marginHorizontal: 4,
  },
  buttonContainer: {
    alignItems: 'center',
  },
  nextButton: {
    width: '100%',
    maxWidth: 320,
  },
  // Login Modal Styles
  loginModal: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 100,
  },
  loginContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.lg,
  },
  loginCard: {
    backgroundColor: theme.colors.background.secondary,
    borderRadius: theme.borderRadius.xl,
    padding: theme.spacing.xl,
    width: '100%',
    maxWidth: 400,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
  },
  loginTitle: {
    ...theme.typography.headlineMedium,
    color: theme.colors.text.primary,
    textAlign: 'center',
    marginBottom: theme.spacing.xs,
  },
  loginSubtitle: {
    ...theme.typography.bodyLarge,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    marginBottom: theme.spacing.xl,
  },
  input: {
    backgroundColor: theme.colors.background.tertiary,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.md,
    color: theme.colors.text.primary,
    fontSize: 16,
    borderWidth: 1,
    borderColor: theme.colors.border.secondary,
  },
  loginButton: {
    marginTop: theme.spacing.sm,
  },
  demoButton: {
    marginBottom: theme.spacing.md,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: theme.spacing.lg,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: theme.colors.border.secondary,
  },
  dividerText: {
    ...theme.typography.labelMedium,
    color: theme.colors.text.tertiary,
    paddingHorizontal: theme.spacing.md,
  },
  helpText: {
    ...theme.typography.bodySmall,
    color: theme.colors.text.tertiary,
    textAlign: 'center',
    marginTop: theme.spacing.sm,
  },
});