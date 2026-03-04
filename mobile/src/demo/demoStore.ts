import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

const DEMO_KEY = 'vip_demo_mode';

interface DemoState {
  enabled: boolean;
  toggle: () => void;
  hydrate: () => Promise<void>;
}

export const useDemoStore = create<DemoState>((set, get) => ({
  enabled: false,

  toggle: () => {
    const next = !get().enabled;
    set({ enabled: next });
    AsyncStorage.setItem(DEMO_KEY, JSON.stringify(next)).catch(() => {});
  },

  hydrate: async () => {
    try {
      const raw = await AsyncStorage.getItem(DEMO_KEY);
      if (raw) set({ enabled: JSON.parse(raw) });
    } catch {
      // ignore
    }
  },
}));
