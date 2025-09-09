import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import * as SplashScreen from 'expo-splash-screen';

// Navigation
import TabNavigator from './src/navigation/TabNavigator';
import AuthNavigator from './src/navigation/AuthNavigator';

// Store
import { useAuthStore } from './src/store/authStore';
import { theme } from './src/styles/theme';

// Error Boundary
import { ErrorBoundary } from './app/features/common/ErrorBoundary';

// Keep splash screen visible while loading
SplashScreen.preventAutoHideAsync();

// Suppress React Navigation logging in development
if (__DEV__) {
  const originalLog = console.log;
  const originalWarn = console.warn;
  
  console.log = (...args) => {
    // Filter out navigation action logs
    const message = args[0]?.toString() || '';
    if (message.includes('action') && (message.includes('REPLACE') || message.includes('NAVIGATE'))) {
      return;
    }
    originalLog.apply(console, args);
  };
  
  console.warn = (...args) => {
    // Filter out navigation warnings
    const message = args[0]?.toString() || '';
    if (message.includes('navigation')) {
      return;
    }
    originalWarn.apply(console, args);
  };
}

const Stack = createStackNavigator();

function LoadingScreen() {
  return (
    <View style={styles.loadingContainer}>
      <ActivityIndicator size="large" color={theme.colors.primary.main} />
      <Text style={styles.loadingText}>Initializing AI Studio...</Text>
      <StatusBar style="light" />
    </View>
  );
}

export default function App() {
  const [isAppReady, setIsAppReady] = useState(false);
  const { isAuthenticated, isLoading, checkAuth, user } = useAuthStore();

  useEffect(() => {
    async function initializeApp() {
      try {
        // Check authentication status
        await checkAuth();
        
        // Initialize offline queue processing
        // Process any queued requests when app starts
        const { apiClient } = await import('./src/services/apiClient');
        apiClient.processOfflineQueue();
        
      } catch (error) {
        // console.error('App initialization error:', error);
      } finally {
        setIsAppReady(true);
        await SplashScreen.hideAsync();
      }
    }

    initializeApp();
  }, []);

  // Show loading screen while app is initializing
  if (!isAppReady || isLoading) {
    return <LoadingScreen />;
  }

  return (
    <ErrorBoundary>
      <GestureHandlerRootView style={{ flex: 1 }}>
        <SafeAreaProvider>
          <NavigationContainer
            onStateChange={() => {
              // Suppress navigation state change logging
            }}
          >
            <StatusBar style="light" />
            <Stack.Navigator
              screenOptions={{
                headerShown: false,
                cardStyleInterpolator: ({ current, layouts }) => {
                  return {
                    cardStyle: {
                      transform: [
                        {
                          translateX: current.progress.interpolate({
                            inputRange: [0, 1],
                            outputRange: [layouts.screen.width, 0],
                          }),
                        },
                      ],
                      opacity: current.progress.interpolate({
                        inputRange: [0, 1],
                        outputRange: [0, 1],
                      }),
                    },
                  };
                },
              }}
            >
              {!isAuthenticated ? (
                <Stack.Screen name="Auth">
                  {() => (
                    <ErrorBoundary>
                      <AuthNavigator 
                        onAuthSuccess={async () => {
                          // Re-check auth status after successful login/register
                          await checkAuth();
                        }} 
                      />
                    </ErrorBoundary>
                  )}
                </Stack.Screen>
              ) : (
                <Stack.Screen name="Main">
                  {() => (
                    <ErrorBoundary>
                      <TabNavigator />
                    </ErrorBoundary>
                  )}
                </Stack.Screen>
              )}
            </Stack.Navigator>
          </NavigationContainer>
        </SafeAreaProvider>
      </GestureHandlerRootView>
    </ErrorBoundary>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: theme.colors.text.secondary,
    fontWeight: theme.typography.bodyMedium.fontWeight,
  },
});
