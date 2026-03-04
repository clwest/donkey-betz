import React, { useCallback, useEffect, useRef } from 'react';
import { Animated, StyleSheet, Text, TouchableOpacity } from 'react-native';
import { create } from 'zustand';

// ── Store ────────────────────────────────────────────────────────────────────

interface ToastState {
  message: string;
  type: 'success' | 'error' | 'info';
  visible: boolean;
  show: (message: string, type?: 'success' | 'error' | 'info') => void;
  hide: () => void;
}

export const useToast = create<ToastState>((set) => ({
  message: '',
  type: 'info',
  visible: false,
  show: (message, type = 'info') => set({ message, type, visible: true }),
  hide: () => set({ visible: false }),
}));

/** Convenience — call from anywhere without hooks */
export const toast = {
  success: (msg: string) => useToast.getState().show(msg, 'success'),
  error: (msg: string) => useToast.getState().show(msg, 'error'),
  info: (msg: string) => useToast.getState().show(msg, 'info'),
};

// ── Component ────────────────────────────────────────────────────────────────

const COLORS = {
  success: '#22c55e',
  error: '#ef4444',
  info: '#818cf8',
} as const;

export default function ToastBanner() {
  const { message, type, visible, hide } = useToast();
  const translateY = useRef(new Animated.Value(-80)).current;

  const animateOut = useCallback(() => {
    Animated.timing(translateY, {
      toValue: -80,
      duration: 250,
      useNativeDriver: true,
    }).start(() => hide());
  }, [translateY, hide]);

  useEffect(() => {
    if (visible) {
      Animated.spring(translateY, {
        toValue: 0,
        useNativeDriver: true,
        friction: 8,
      }).start();

      const timer = setTimeout(animateOut, 3000);
      return () => clearTimeout(timer);
    }
  }, [visible, translateY, animateOut]);

  if (!visible) return null;

  return (
    <Animated.View
      style={[
        styles.container,
        { backgroundColor: COLORS[type] + '22', borderColor: COLORS[type] },
        { transform: [{ translateY }] },
      ]}
    >
      <TouchableOpacity onPress={animateOut} style={styles.inner} activeOpacity={0.8}>
        <Text style={[styles.text, { color: COLORS[type] }]}>{message}</Text>
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 54,
    left: 16,
    right: 16,
    borderRadius: 10,
    borderWidth: 1,
    zIndex: 9999,
  },
  inner: { padding: 12 },
  text: { fontSize: 13, fontWeight: '600', textAlign: 'center' },
});
