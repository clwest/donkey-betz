import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { useDemo } from '../demo/useDemo';

export type DataStatus = 'live' | 'cached' | 'offline' | 'error';

interface Props {
  status: DataStatus;
  lastUpdated?: Date | null;
}

const CONFIG: Record<DataStatus, { label: string; color: string; bg: string }> = {
  live:    { label: 'Live',    color: '#22c55e', bg: 'rgba(34,197,94,0.15)' },
  cached:  { label: 'Cached',  color: '#f59e0b', bg: 'rgba(245,158,11,0.15)' },
  offline: { label: 'Offline', color: '#6b7280', bg: 'rgba(107,114,128,0.15)' },
  error:   { label: 'Error',   color: '#ef4444', bg: 'rgba(239,68,68,0.15)' },
};

export default function DataStatusChip({ status, lastUpdated }: Props) {
  const isDemo = useDemo();

  if (isDemo) {
    return (
      <View style={[styles.chip, { backgroundColor: 'rgba(99,102,241,0.15)' }]}>
        <View style={[styles.dot, { backgroundColor: '#818cf8' }]} />
        <Text style={[styles.label, { color: '#818cf8' }]}>Demo</Text>
      </View>
    );
  }

  const cfg = CONFIG[status];
  const timeStr = lastUpdated
    ? `${(lastUpdated.getHours() % 12 || 12)}:${lastUpdated.getMinutes() < 10 ? '0' : ''}${lastUpdated.getMinutes()} ${lastUpdated.getHours() >= 12 ? 'PM' : 'AM'}`
    : null;

  return (
    <View style={[styles.chip, { backgroundColor: cfg.bg }]}>
      <View style={[styles.dot, { backgroundColor: cfg.color }]} />
      <Text style={[styles.label, { color: cfg.color }]}>{cfg.label}</Text>
      {timeStr && <Text style={styles.time}>{timeStr}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-end',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
    gap: 5,
    marginBottom: 6,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  label: {
    fontSize: 10,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  time: {
    fontSize: 10,
    color: '#6b7280',
  },
});
