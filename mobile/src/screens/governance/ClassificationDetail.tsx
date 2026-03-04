import React, { useState } from 'react';
import {
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import type { Artifact, ClassificationPayload } from '../../api/governance';
import * as governanceApi from '../../api/governance';
import CopyId from '../../components/CopyId';
import { toast } from '../../components/Toast';

// ── Option configs ───────────────────────────────────────────────────────────

const WHAT_OPTIONS: { value: ClassificationPayload['what_is_this']; label: string }[] = [
  { value: 'research_finding', label: 'Research Finding' },
  { value: 'actionable_recommendation', label: 'Actionable Recommendation' },
  { value: 'scope_change', label: 'Scope Change' },
  { value: 'risk_flag', label: 'Risk Flag' },
  { value: 'informational', label: 'Informational' },
];

const WHO_OPTIONS: { value: ClassificationPayload['who_is_it_for']; label: string }[] = [
  { value: 'platform', label: 'Platform' },
  { value: 'end_users', label: 'End Users' },
  { value: 'founder', label: 'Founder' },
  { value: 'agents', label: 'Agents' },
  { value: 'public', label: 'Public' },
];

const DATA_OPTIONS: { value: ClassificationPayload['data_allowed']; label: string }[] = [
  { value: 'public_only', label: 'Public Only' },
  { value: 'internal_ops', label: 'Internal Ops' },
  { value: 'api_data', label: 'API Data' },
  { value: 'user_data', label: 'User Data' },
  { value: 'all', label: 'All' },
];

const PHASE_OPTIONS: { value: ClassificationPayload['phase_approved']; label: string }[] = [
  { value: 'research', label: 'Research' },
  { value: 'prototype', label: 'Prototype' },
  { value: 'pilot', label: 'Pilot' },
  { value: 'production', label: 'Production' },
  { value: 'none', label: 'None' },
];

// ── Component ────────────────────────────────────────────────────────────────

interface Props {
  artifact: Artifact;
  canMutate: boolean;
  onBack: () => void;
  onClassified: () => void;
}

export default function ClassificationDetail({ artifact, canMutate, onBack, onClassified }: Props) {
  const [whatIs, setWhatIs] = useState<ClassificationPayload['what_is_this'] | null>(null);
  const [whoFor, setWhoFor] = useState<ClassificationPayload['who_is_it_for'] | null>(null);
  const [dataAllowed, setDataAllowed] = useState<ClassificationPayload['data_allowed'] | null>(null);
  const [phase, setPhase] = useState<ClassificationPayload['phase_approved'] | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const isComplete = whatIs && whoFor && dataAllowed && phase;

  const handleSubmit = async () => {
    if (!isComplete || submitting) return;
    setSubmitting(true);
    try {
      await governanceApi.classifyArtifact(artifact.id, {
        what_is_this: whatIs!,
        who_is_it_for: whoFor!,
        data_allowed: dataAllowed!,
        phase_approved: phase!,
      });
      toast.success('Artifact classified');
      onClassified();
    } catch {
      toast.error('Failed to classify artifact');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.topRow}>
        <TouchableOpacity onPress={onBack} style={styles.backBtn}>
          <Text style={styles.backText}>Back</Text>
        </TouchableOpacity>
        <CopyId value={artifact.id} label="Artifact ID" />
      </View>

      {/* Artifact info */}
      <Text style={styles.title}>{artifact.title}</Text>
      {artifact.content ? (
        <Text style={styles.body}>{artifact.content}</Text>
      ) : null}
      <View style={styles.metaRow}>
        {artifact.source_agent ? (
          <Text style={styles.metaText}>Agent: {artifact.source_agent}</Text>
        ) : null}
        <Text style={styles.metaText}>
          Score: {Math.round((artifact.composite_score ?? 0) * 100)}%
        </Text>
      </View>

      {/* Classification form */}
      {canMutate ? (
        <View style={styles.form}>
          <PickerSection
            label="What is this?"
            options={WHAT_OPTIONS}
            selected={whatIs}
            onSelect={setWhatIs}
          />
          <PickerSection
            label="Who is it for?"
            options={WHO_OPTIONS}
            selected={whoFor}
            onSelect={setWhoFor}
          />
          <PickerSection
            label="Data allowed"
            options={DATA_OPTIONS}
            selected={dataAllowed}
            onSelect={setDataAllowed}
          />
          <PickerSection
            label="Phase approved"
            options={PHASE_OPTIONS}
            selected={phase}
            onSelect={setPhase}
          />

          <TouchableOpacity
            style={[styles.submitBtn, (!isComplete || submitting) && styles.disabledBtn]}
            onPress={handleSubmit}
            disabled={!isComplete || submitting}
          >
            <Text style={styles.submitText}>
              {submitting ? 'Submitting...' : 'Submit Classification'}
            </Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.noPermission}>
          <Text style={styles.noPermText}>Classification requires admin permissions</Text>
        </View>
      )}

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

// ── Picker section ───────────────────────────────────────────────────────────

function PickerSection<T extends string>({
  label,
  options,
  selected,
  onSelect,
}: {
  label: string;
  options: { value: T; label: string }[];
  selected: T | null;
  onSelect: (v: T) => void;
}) {
  return (
    <View style={styles.pickerSection}>
      <Text style={styles.pickerLabel}>{label}</Text>
      <View style={styles.chipRow}>
        {options.map((opt) => (
          <TouchableOpacity
            key={opt.value}
            style={[styles.chip, selected === opt.value && styles.chipSelected]}
            onPress={() => onSelect(opt.value)}
          >
            <Text style={[styles.chipText, selected === opt.value && styles.chipTextSelected]}>
              {opt.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f' },
  content: { padding: 16 },

  topRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  backBtn: {},
  backText: { color: '#6366f1', fontSize: 14, fontWeight: '600' },

  title: { color: '#ffffff', fontSize: 20, fontWeight: '700', marginBottom: 10 },
  body: { color: '#d1d5db', fontSize: 14, lineHeight: 20, marginBottom: 12 },
  metaRow: { flexDirection: 'row', gap: 12, marginBottom: 20 },
  metaText: { color: '#6b7280', fontSize: 12 },

  form: { marginTop: 4 },
  pickerSection: { marginBottom: 18 },
  pickerLabel: { color: '#818cf8', fontSize: 13, fontWeight: '600', marginBottom: 8, textTransform: 'uppercase' },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: {
    backgroundColor: '#1a1a2e',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  chipSelected: {
    borderColor: '#6366f1',
    backgroundColor: 'rgba(99,102,241,0.15)',
  },
  chipText: { color: '#9ca3af', fontSize: 13 },
  chipTextSelected: { color: '#a5b4fc', fontWeight: '600' },

  submitBtn: {
    backgroundColor: '#6366f1',
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 8,
  },
  disabledBtn: { opacity: 0.4 },
  submitText: { color: '#ffffff', fontSize: 16, fontWeight: '700' },

  noPermission: {
    backgroundColor: 'rgba(234,179,8,0.1)',
    borderRadius: 8,
    padding: 16,
    marginTop: 16,
  },
  noPermText: { color: '#eab308', fontSize: 13, textAlign: 'center' },
});
