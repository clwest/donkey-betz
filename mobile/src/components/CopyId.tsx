import React from 'react';
import { Clipboard, StyleSheet, Text, TouchableOpacity } from 'react-native';
import { toast } from './Toast';

interface CopyIdProps {
  value: string;
  label?: string;
  /** Show truncated ID inline (default true) */
  showValue?: boolean;
}

export default function CopyId({ value, label = 'ID', showValue = true }: CopyIdProps) {
  const handleCopy = () => {
    Clipboard.setString(value);
    toast.success(`${label} copied`);
  };

  const display = value.length > 12 ? value.slice(0, 8) + '...' : value;

  return (
    <TouchableOpacity onPress={handleCopy} style={styles.container} activeOpacity={0.6}>
      {showValue && <Text style={styles.id}>{display}</Text>}
      <Text style={styles.copyHint}>copy</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  id: { color: '#6b7280', fontSize: 10, fontFamily: 'monospace' },
  copyHint: { color: '#6366f1', fontSize: 9, fontWeight: '600' },
});
