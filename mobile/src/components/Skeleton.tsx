import React, { useEffect, useRef } from 'react';
import { Animated, StyleSheet, View, type ViewStyle } from 'react-native';

interface SkeletonProps {
  width?: number | string;
  height?: number;
  borderRadius?: number;
  style?: ViewStyle;
}

/**
 * Shimmering skeleton placeholder for loading states.
 * Drop-in replacement for content that hasn't loaded yet.
 */
export default function Skeleton({
  width = '100%',
  height = 16,
  borderRadius = 6,
  style,
}: SkeletonProps) {
  const opacity = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, { toValue: 0.7, duration: 800, useNativeDriver: true }),
        Animated.timing(opacity, { toValue: 0.3, duration: 800, useNativeDriver: true }),
      ]),
    );
    animation.start();
    return () => animation.stop();
  }, [opacity]);

  return (
    <Animated.View
      style={[
        styles.base,
        { width: width as any, height, borderRadius, opacity },
        style,
      ]}
    />
  );
}

/** Pre-built skeleton patterns for common UI elements */

export function SkeletonCard({ lines = 3 }: { lines?: number }) {
  return (
    <View style={styles.card}>
      <Skeleton width="40%" height={14} />
      <View style={{ height: 10 }} />
      {Array.from({ length: lines }).map((_, i) => (
        <View key={i} style={{ marginBottom: 8 }}>
          <Skeleton width={i === lines - 1 ? '60%' : '100%'} height={12} />
        </View>
      ))}
    </View>
  );
}

export function SkeletonStatRow({ count = 4 }: { count?: number }) {
  return (
    <View style={styles.statRow}>
      {Array.from({ length: count }).map((_, i) => (
        <View key={i} style={styles.statBox}>
          <Skeleton width={40} height={24} borderRadius={4} />
          <View style={{ height: 6 }} />
          <Skeleton width={50} height={10} borderRadius={3} />
        </View>
      ))}
    </View>
  );
}

export function SkeletonList({ rows = 4 }: { rows?: number }) {
  return (
    <View style={styles.card}>
      <Skeleton width="35%" height={14} style={{ marginBottom: 12 }} />
      {Array.from({ length: rows }).map((_, i) => (
        <View key={i} style={styles.listRow}>
          <Skeleton width={32} height={32} borderRadius={16} />
          <View style={{ flex: 1, marginLeft: 10 }}>
            <Skeleton width="70%" height={13} />
            <View style={{ height: 4 }} />
            <Skeleton width="45%" height={10} />
          </View>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  base: {
    backgroundColor: '#2a2a4a',
  },
  card: {
    backgroundColor: '#1a1a2e',
    borderRadius: 12,
    padding: 16,
    marginBottom: 10,
  },
  statRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 10,
  },
  statBox: {
    flex: 1,
    backgroundColor: '#1a1a2e',
    borderRadius: 10,
    padding: 12,
    alignItems: 'center',
  },
  listRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
  },
});
