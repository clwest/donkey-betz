import * as Notifications from 'expo-notifications';
import * as Linking from 'expo-linking';

/**
 * Notification payload contract from backend:
 * {
 *   route: "/boardroom/attention/123",
 *   object_type: "boardroom_attention",
 *   object_id: "123",
 *   title: "New critical boardroom item",
 *   body: "..."
 * }
 */

/**
 * Configure how foreground notifications are presented.
 * Shows alert + badge + sound so the user sees them without leaving the app.
 */
export function configureForegroundHandler(): void {
  Notifications.setNotificationHandler({
    handleNotification: async (notification) => {
      const data = notification.request.content.data as
        | { object_type?: string }
        | undefined;

      // Suppress disruptive banner for media completions — the user
      // will see the result inline or in the Media gallery.
      if (data?.object_type === 'media_complete') {
        return {
          shouldShowAlert: false,
          shouldShowBanner: false,
          shouldShowList: true,
          shouldPlaySound: false,
          shouldSetBadge: true,
        };
      }

      return {
        shouldShowAlert: true,
        shouldShowBanner: true,
        shouldShowList: true,
        shouldPlaySound: true,
        shouldSetBadge: true,
      };
    },
  });
}

/**
 * Listen for notification taps (foreground + background/killed).
 * Extracts `route` from payload and navigates via deep link.
 *
 * Returns a cleanup function to remove the listener.
 */
export function addNotificationResponseListener(): () => void {
  const subscription = Notifications.addNotificationResponseReceivedListener(
    (response) => {
      const data = response.notification.request.content.data as
        | { route?: string }
        | undefined;

      if (data?.route) {
        // Convert backend route to deep link: /boardroom → donkeybetz://boardroom
        const deepLink = Linking.createURL(data.route);
        Linking.openURL(deepLink).catch((err) =>
          console.warn('[Push] Failed to open deep link:', err),
        );
      }
    },
  );

  return () => subscription.remove();
}

/**
 * Check if the app was opened from a killed state via notification.
 * Call once on app start to handle the initial notification.
 */
export async function handleInitialNotification(): Promise<void> {
  const response = await Notifications.getLastNotificationResponseAsync();
  if (response) {
    const data = response.notification.request.content.data as
      | { route?: string }
      | undefined;

    if (data?.route) {
      const deepLink = Linking.createURL(data.route);
      // Small delay to let navigation mount first
      setTimeout(() => {
        Linking.openURL(deepLink).catch((err) =>
          console.warn('[Push] Failed to open initial deep link:', err),
        );
      }, 500);
    }
  }
}
