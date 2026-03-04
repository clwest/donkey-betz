import { useDemoStore } from './demoStore';

/** Returns true when VIP demo mode is active. */
export function useDemo(): boolean {
  return useDemoStore((s) => s.enabled);
}
