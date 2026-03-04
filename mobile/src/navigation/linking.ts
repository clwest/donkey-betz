import type { LinkingOptions } from '@react-navigation/native';
import * as Linking from 'expo-linking';

// Screen name used in the navigator is the manifest path with leading slash
// stripped and slashes replaced with dashes. Example: '/boardroom' → 'boardroom'
// For nested params we use separate stack screens.

const prefix = Linking.createURL('/');

export const linking: LinkingOptions<any> = {
  prefixes: [prefix, 'donkeybetz://'],
  config: {
    screens: {
      // Top-level drawer screens (path matches manifest route)
      '/': 'command-center',
      '/dashboard': 'dashboard',
      '/boardroom': 'boardroom',
      '/governance': 'governance',
      '/workspace': 'workspace',
      '/content': 'content',
      '/betting': 'betting',
      '/stocks': 'stocks',
      '/initiatives': 'initiatives',
      '/intelligence': 'intelligence',
      '/agents': 'agents',
      '/portfolio': 'portfolio',
      '/settings': 'settings',

      // VIP magic-link accept (deep link)
      VIPAccept: {
        path: 'vip/accept',
        parse: { token: (token: string) => token },
      },

      // Detail screens (nested stacks added in future PRs)
      // 'boardroom/attention/:id': 'boardroom-attention-detail',
      // 'boardroom/decision/:id': 'boardroom-decision-detail',
      // 'governance/classification/:id': 'governance-classification-detail',
    },
  },
};
