/**
 * Shared formatting utilities for consistent display across screens.
 */

/** Format a number as currency: $1,234 or -$567 */
export function formatMoney(n: number): string {
  if (n >= 0) return `$${Math.round(n).toLocaleString()}`;
  return `-$${Math.round(Math.abs(n)).toLocaleString()}`;
}

/** Format with cents: $1,234.56 or -$567.89 */
export function formatMoneyCents(n: number): string {
  if (n >= 0) return `$${n.toFixed(2)}`;
  return `-$${Math.abs(n).toFixed(2)}`;
}

/** Format a percentage: 60.8% */
export function formatPct(n: number, decimals = 1): string {
  return `${n.toFixed(decimals)}%`;
}

/** Format American odds: +135 or -110 */
export function formatOdds(odds: number): string {
  return odds > 0 ? `+${odds}` : String(odds);
}

/** Relative time: "just now", "5m ago", "2h ago", "3d ago" */
export function timeAgo(ts: string | Date): string {
  const d = ts instanceof Date ? ts : new Date(ts);
  const diff = Date.now() - d.getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

/** Short time: "2:14 PM" */
export function formatTime(ts: string | Date): string {
  const d = ts instanceof Date ? ts : new Date(ts);
  const h = d.getHours();
  const m = d.getMinutes();
  const ampm = h >= 12 ? 'PM' : 'AM';
  const h12 = h % 12 || 12;
  return `${h12}:${m < 10 ? '0' : ''}${m} ${ampm}`;
}

/** P/L color: green for positive, red for negative, gray for zero */
export function plColor(n: number): string {
  if (n > 0) return '#22c55e';
  if (n < 0) return '#ef4444';
  return '#6b7280';
}
