import React, { useRef, useEffect } from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  View,
  Animated,
  Platform,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import { theme } from '../../styles/theme';

interface PremiumButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'glass' | 'outline';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  style?: ViewStyle;
  textStyle?: TextStyle;
  haptic?: boolean;
  glow?: boolean;
}

export const PremiumButton: React.FC<PremiumButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  loading = false,
  disabled = false,
  icon,
  style,
  textStyle,
  haptic = true,
  glow = false,
}) => {
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const glowAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (glow && !disabled) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(glowAnim, {
            toValue: 1,
            duration: 1500,
            useNativeDriver: true,
          }),
          Animated.timing(glowAnim, {
            toValue: 0,
            duration: 1500,
            useNativeDriver: true,
          }),
        ])
      ).start();
    }
  }, [glow, disabled, glowAnim]);

  const handlePressIn = () => {
    if (!disabled && !loading) {
      Animated.spring(scaleAnim, {
        toValue: 0.95,
        useNativeDriver: true,
        speed: 50,
        bounciness: 10,
      }).start();
    }
  };

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true,
      speed: 50,
      bounciness: 10,
    }).start();
  };

  const handlePress = () => {
    if (!disabled && !loading) {
      if (haptic && Platform.OS !== 'web') {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      }
      onPress();
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return {
          button: styles.buttonSmall,
          text: styles.textSmall,
        };
      case 'large':
        return {
          button: styles.buttonLarge,
          text: styles.textLarge,
        };
      default:
        return {
          button: styles.buttonMedium,
          text: styles.textMedium,
        };
    }
  };

  const sizeStyles = getSizeStyles();
  const isDisabled = disabled || loading;

  const renderContent = () => (
    <View style={styles.contentContainer}>
      {loading ? (
        <ActivityIndicator 
          color={variant === 'primary' ? theme.colors.text.primary : theme.colors.primary.main} 
          size="small" 
        />
      ) : (
        <>
          {icon && <View style={styles.iconContainer}>{icon}</View>}
          <Text 
            style={[
              styles.text,
              sizeStyles.text,
              variant === 'primary' ? styles.textPrimary : styles.textSecondary,
              isDisabled && styles.textDisabled,
              textStyle,
            ]}
          >
            {title}
          </Text>
        </>
      )}
    </View>
  );

  const buttonContent = (
    <Animated.View
      style={[
        styles.button,
        sizeStyles.button,
        variant === 'glass' && styles.buttonGlass,
        variant === 'outline' && styles.buttonOutline,
        variant === 'secondary' && styles.buttonSecondary,
        isDisabled && styles.buttonDisabled,
        glow && !isDisabled && {
          shadowColor: theme.colors.primary.main,
          shadowOpacity: glowAnim.interpolate({
            inputRange: [0, 1],
            outputRange: [0.3, 0.6],
          }),
          shadowRadius: glowAnim.interpolate({
            inputRange: [0, 1],
            outputRange: [15, 25],
          }),
        },
        { transform: [{ scale: scaleAnim }] },
        style,
      ]}
    >
      {variant === 'primary' ? (
        <LinearGradient
          colors={theme.colors.primary.gradient}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={[styles.gradient, sizeStyles.button]}
        >
          {renderContent()}
        </LinearGradient>
      ) : (
        renderContent()
      )}
    </Animated.View>
  );

  return (
    <TouchableOpacity
      activeOpacity={0.8}
      onPress={handlePress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      disabled={isDisabled}
      style={styles.touchable}
    >
      {buttonContent}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  touchable: {
    overflow: 'visible',
  },
  button: {
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'center',
  },
  gradient: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonSmall: {
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.md,
    minHeight: 36,
  },
  buttonMedium: {
    paddingVertical: theme.spacing.md,
    paddingHorizontal: theme.spacing.lg,
    minHeight: 48,
  },
  buttonLarge: {
    paddingVertical: theme.spacing.lg - 4,
    paddingHorizontal: theme.spacing.xl,
    minHeight: 56,
  },
  buttonGlass: {
    backgroundColor: theme.colors.background.glass,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
  },
  buttonOutline: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: theme.colors.primary.main,
  },
  buttonSecondary: {
    backgroundColor: theme.colors.background.secondary,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  contentContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconContainer: {
    marginRight: theme.spacing.sm,
  },
  text: {
    fontWeight: '600',
    textAlign: 'center',
  },
  textSmall: {
    fontSize: 14,
  },
  textMedium: {
    fontSize: 16,
  },
  textLarge: {
    fontSize: 18,
  },
  textPrimary: {
    color: theme.colors.text.primary,
  },
  textSecondary: {
    color: theme.colors.primary.main,
  },
  textDisabled: {
    color: theme.colors.text.disabled,
  },
});