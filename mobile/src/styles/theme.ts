// Premium $20k Theme Configuration
export const theme = {
  colors: {
    // Primary gradient colors
    primary: {
      gradient: ['#6366F1', '#8B5CF6', '#EC4899'] as const,
      main: '#6366F1',
      light: '#818CF8',
      dark: '#4F46E5',
      text: '#FFFFFF',
    },
    
    // Dark theme colors (premium feel)
    background: {
      primary: '#0A0A0F',    // Deep black
      secondary: '#13131A',   // Card background
      tertiary: '#1C1C25',    // Elevated surfaces
      glass: 'rgba(255, 255, 255, 0.05)', // Glass morphism
      overlay: 'rgba(0, 0, 0, 0.7)',
    },
    
    // Text colors
    text: {
      primary: '#FFFFFF',
      secondary: '#A1A1AA',
      tertiary: '#71717A',
      disabled: '#52525B',
      inverse: '#0A0A0F',
    },
    
    // Semantic colors
    success: {
      main: '#10B981',
      light: '#34D399',
      dark: '#059669',
      background: 'rgba(16, 185, 129, 0.1)',
    },
    
    warning: {
      main: '#F59E0B',
      light: '#FCD34D',
      dark: '#D97706',
      background: 'rgba(245, 158, 11, 0.1)',
    },
    
    error: {
      main: '#EF4444',
      light: '#F87171',
      dark: '#DC2626',
      background: 'rgba(239, 68, 68, 0.1)',
    },
    
    info: {
      main: '#3B82F6',
      light: '#60A5FA',
      dark: '#2563EB',
      background: 'rgba(59, 130, 246, 0.1)',
    },
    
    // Borders and dividers
    border: {
      primary: 'rgba(255, 255, 255, 0.1)',
      secondary: 'rgba(255, 255, 255, 0.05)',
      focus: '#6366F1',
    },
    
    // Special effects
    glow: {
      purple: 'rgba(139, 92, 246, 0.5)',
      blue: 'rgba(99, 102, 241, 0.5)',
      pink: 'rgba(236, 72, 153, 0.5)',
    },
  },
  
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
    xxxl: 64,
  },
  
  borderRadius: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
    xxl: 32,
    full: 9999,
  },
  
  typography: {
    // Display fonts
    displayLarge: {
      fontSize: 57,
      lineHeight: 64,
      fontWeight: '700' as const,
      letterSpacing: -0.25,
    },
    displayMedium: {
      fontSize: 45,
      lineHeight: 52,
      fontWeight: '700' as const,
      letterSpacing: 0,
    },
    displaySmall: {
      fontSize: 36,
      lineHeight: 44,
      fontWeight: '600' as const,
      letterSpacing: 0,
    },
    
    // Headlines
    headlineLarge: {
      fontSize: 32,
      lineHeight: 40,
      fontWeight: '600' as const,
      letterSpacing: 0,
    },
    headlineMedium: {
      fontSize: 28,
      lineHeight: 36,
      fontWeight: '600' as const,
      letterSpacing: 0,
    },
    headlineSmall: {
      fontSize: 24,
      lineHeight: 32,
      fontWeight: '600' as const,
      letterSpacing: 0,
    },
    
    // Title
    titleLarge: {
      fontSize: 22,
      lineHeight: 28,
      fontWeight: '500' as const,
      letterSpacing: 0,
    },
    titleMedium: {
      fontSize: 16,
      lineHeight: 24,
      fontWeight: '600' as const,
      letterSpacing: 0.15,
    },
    titleSmall: {
      fontSize: 14,
      lineHeight: 20,
      fontWeight: '600' as const,
      letterSpacing: 0.1,
    },
    
    // Body
    bodyLarge: {
      fontSize: 16,
      lineHeight: 24,
      fontWeight: '400' as const,
      letterSpacing: 0.5,
    },
    bodyMedium: {
      fontSize: 14,
      lineHeight: 20,
      fontWeight: '400' as const,
      letterSpacing: 0.25,
    },
    bodySmall: {
      fontSize: 12,
      lineHeight: 16,
      fontWeight: '400' as const,
      letterSpacing: 0.4,
    },
    
    // Label
    labelLarge: {
      fontSize: 14,
      lineHeight: 20,
      fontWeight: '500' as const,
      letterSpacing: 0.1,
    },
    labelMedium: {
      fontSize: 12,
      lineHeight: 16,
      fontWeight: '500' as const,
      letterSpacing: 0.5,
    },
    labelSmall: {
      fontSize: 11,
      lineHeight: 16,
      fontWeight: '500' as const,
      letterSpacing: 0.5,
    },
    
    // Caption
    caption: {
      fontSize: 12,
      lineHeight: 16,
      fontWeight: '400' as const,
      letterSpacing: 0.4,
    },
  },
  
  shadows: {
    sm: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.05,
      shadowRadius: 2,
      elevation: 2,
    },
    md: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.1,
      shadowRadius: 6,
      elevation: 4,
    },
    lg: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 10 },
      shadowOpacity: 0.15,
      shadowRadius: 20,
      elevation: 8,
    },
    xl: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 20 },
      shadowOpacity: 0.25,
      shadowRadius: 40,
      elevation: 12,
    },
    glow: {
      shadowColor: '#6366F1',
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: 0.5,
      shadowRadius: 20,
      elevation: 0,
    },
  },
  
  animation: {
    duration: {
      instant: 100,
      fast: 200,
      normal: 300,
      slow: 500,
      verySlow: 1000,
    },
    easing: {
      linear: [0, 0, 1, 1],
      easeIn: [0.42, 0, 1, 1],
      easeOut: [0, 0, 0.58, 1],
      easeInOut: [0.42, 0, 0.58, 1],
      spring: [0.175, 0.885, 0.32, 1.275],
    },
  },
};

export type Theme = typeof theme;