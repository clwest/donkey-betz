import { ExpoConfig, ConfigContext } from 'expo/config';

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: 'DonkeyBetz',
  slug: 'donkeybetz',
  owner: 'donkeyking',
  version: '1.0.0',
  orientation: 'portrait',
  icon: './assets/icon.png',
  userInterfaceStyle: 'automatic',
  scheme: 'donkeybetz',
  // newArchEnabled disabled — was causing crashes on TestFlight builds
  // with @sentry/react-native and other native modules.
  // Re-enable after verifying all native deps support New Architecture.
  newArchEnabled: false,
  runtimeVersion: {
    policy: 'appVersion',
  },
  updates: {
    url: `https://u.expo.dev/${process.env.EAS_PROJECT_ID ?? '5fcd4ff0-bb20-40c6-b9f4-a0a6753a066d'}`,
    fallbackToCacheTimeout: 5000,
  },
  splash: {
    image: './assets/splash-icon.png',
    resizeMode: 'contain',
    backgroundColor: '#0a0a0f',
  },
  ios: {
    supportsTablet: true,
    bundleIdentifier: 'com.donkeybetz.app',
    infoPlist: {
      ITSAppUsesNonExemptEncryption: false,
      NSMicrophoneUsageDescription:
        'DonkeyBetz uses the microphone for voice commands to the Personal Assistant.',
    },
  },
  android: {
    adaptiveIcon: {
      foregroundImage: './assets/adaptive-icon.png',
      backgroundColor: '#0a0a0f',
    },
    package: 'com.donkeybetz.app',
    edgeToEdgeEnabled: true,
  },
  web: {
    favicon: './assets/favicon.png',
  },
  extra: {
    apiBaseUrl: process.env.EXPO_PUBLIC_API_BASE_URL ?? 'https://donkey-betz-platform-production.up.railway.app/api',
    buildSha: process.env.EAS_BUILD_GIT_COMMIT_HASH ?? process.env.EXPO_PUBLIC_BUILD_SHA ?? 'dev',
    eas: {
      projectId: process.env.EAS_PROJECT_ID ?? '5fcd4ff0-bb20-40c6-b9f4-a0a6753a066d',
      buildProfile: process.env.EAS_BUILD_PROFILE ?? 'unknown',
    },
  },
  plugins: [
    'expo-secure-store',
    [
      'expo-notifications',
      {
        icon: './assets/icon.png',
        color: '#6366f1',
      },
    ],
    // Sentry native plugin only included when DSN is configured.
    // Without a DSN, the native module can crash on startup before JS runs.
    ...(process.env.EXPO_PUBLIC_SENTRY_DSN
      ? [
          [
            '@sentry/react-native/expo',
            {
              organization: process.env.SENTRY_ORG ?? '',
              project: process.env.SENTRY_PROJECT ?? 'donkeybetz-mobile',
            },
          ] as const,
        ]
      : []),
  ],
});
