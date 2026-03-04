import { registerRootComponent } from 'expo';
import { ErrorUtils } from 'react-native';

import App from './App';

// ── Global JS error handler ─────────────────────────────────────────────────
// Catches unhandled JS errors BEFORE they crash the app. React Native's
// default handler calls RCTFatalException which kills the process; this
// logs the error and swallows it so the app stays alive.
try {
  const defaultHandler = ErrorUtils.getGlobalHandler();
  ErrorUtils.setGlobalHandler((error: Error, isFatal?: boolean) => {
    console.error(`[GlobalErrorHandler] ${isFatal ? 'FATAL' : 'ERROR'}:`, error?.message ?? error);
    // Delegate to the default handler for non-fatal errors so the
    // LogBox / yellow-box still appears in dev.
    if (!isFatal && defaultHandler) {
      defaultHandler(error, isFatal);
    }
    // For fatal errors we intentionally do NOT re-throw — that would
    // trigger the native crash dialog. The error is already logged.
  });
} catch (e) {
  console.warn('[GlobalErrorHandler] Failed to install handler:', e);
}

// registerRootComponent calls AppRegistry.registerComponent('main', () => App);
// It also ensures that whether you load the app in Expo Go or in a native build,
// the environment is set up appropriately
try {
  registerRootComponent(App);
} catch (e) {
  console.error('[Startup] registerRootComponent failed:', e);
}
