import { Platform } from 'react-native';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { registerExpoToken } from '../api/push';

const LAST_TOKEN_KEY = 'last_registered_push_token';

/**
 * Request notification permissions, obtain an Expo push token, and register
 * it with the backend. Skips re-registration if the token hasn't changed.
 *
 * Call this once after successful auth (e.g. in App.tsx or AppRoot).
 */
export async function registerPushToken(): Promise<string | null> {
  // Physical device required for push tokens
  if (!Device.isDevice) {
    console.log('[Push] Skipping — not a physical device');
    return null;
  }

  // Request permission
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;
  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }
  if (finalStatus !== 'granted') {
    console.log('[Push] Permission not granted');
    return null;
  }

  // Android notification channel
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'Default',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
    });
  }

  // Get Expo push token — projectId required for EAS standalone builds
  const projectId =
    Constants.expoConfig?.extra?.eas?.projectId ??
    '5fcd4ff0-bb20-40c6-b9f4-a0a6753a066d';
  const tokenData = await Notifications.getExpoPushTokenAsync({ projectId });
  const token = tokenData.data;

  // Skip if already registered with same token
  const lastToken = await AsyncStorage.getItem(LAST_TOKEN_KEY);
  if (lastToken === token) {
    console.log('[Push] Token unchanged, skipping registration');
    return token;
  }

  // Register with backend
  try {
    await registerExpoToken({
      expo_push_token: token,
      device_name: Device.deviceName ?? undefined,
      platform: Platform.OS as 'ios' | 'android',
    });
    await AsyncStorage.setItem(LAST_TOKEN_KEY, token);
    console.log('[Push] Token registered:', token.slice(0, 20) + '...');
  } catch (err) {
    console.warn('[Push] Registration failed:', err);
  }

  return token;
}

/**
 * Clear stored token on sign-out so re-auth triggers fresh registration.
 */
export async function clearPushTokenCache(): Promise<void> {
  await AsyncStorage.removeItem(LAST_TOKEN_KEY);
}
