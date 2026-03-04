import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { Clipboard } from 'react-native';
import { useAuthStore } from '../auth/authStore';
import { useDemo } from '../demo/useDemo';
import { useScreenAnalytics } from '../observability/analytics';
import { toast } from '../components/Toast';
import {
  startCodeRun,
  getCodeRunStatus,
  getCodeRunLogs,
  type StatusResponse,
  type LogsResponse,
} from '../api/codeRunner';

// ── Types ────────────────────────────────────────────────────────────────────

type RunMode = 'dry_run' | 'apply';
type RunStatus = 'idle' | 'queued' | 'running' | 'completed' | 'failed';

const STATUS_COLORS: Record<RunStatus, { bg: string; text: string }> = {
  idle:      { bg: 'rgba(107,114,128,0.15)', text: '#9ca3af' },
  queued:    { bg: 'rgba(245,158,11,0.15)',  text: '#f59e0b' },
  running:   { bg: 'rgba(59,130,246,0.15)',  text: '#3b82f6' },
  completed: { bg: 'rgba(34,197,94,0.15)',   text: '#22c55e' },
  failed:    { bg: 'rgba(239,68,68,0.15)',   text: '#ef4444' },
};

// ── Component ────────────────────────────────────────────────────────────────

export default function CodeRunnerScreen() {
  useScreenAnalytics('CodeRunnerScreen');

  const user = useAuthStore((s) => s.user);
  const isDemo = useDemo();
  const isAdmin = user?.platform_role === 'admin' || (user as any)?.is_staff;

  // ── State ────────────────────────────────────────────────────────────────
  const [task, setTask] = useState('');
  const [mode, setMode] = useState<RunMode>('dry_run');
  const [confirmText, setConfirmText] = useState('');
  const [runId, setRunId] = useState<string | null>(null);
  const [status, setStatus] = useState<RunStatus>('idle');
  const [statusInfo, setStatusInfo] = useState<StatusResponse | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [totalLines, setTotalLines] = useState(0);
  const [truncated, setTruncated] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const logScrollRef = useRef<ScrollView>(null);

  // ── Cleanup polling on unmount ───────────────────────────────────────────
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  // ── Admin/VIP gate ───────────────────────────────────────────────────────
  if (isDemo) {
    return (
      <View style={styles.container}>
        <View style={styles.gateBox}>
          <Text style={styles.gateIcon}>🔒</Text>
          <Text style={styles.gateTitle}>Admin Only</Text>
          <Text style={styles.gateText}>
            Code Runner is not available in demo mode.
          </Text>
        </View>
      </View>
    );
  }

  if (!isAdmin) {
    return (
      <View style={styles.container}>
        <View style={styles.gateBox}>
          <Text style={styles.gateIcon}>🔒</Text>
          <Text style={styles.gateTitle}>Admin Access Required</Text>
          <Text style={styles.gateText}>
            You need admin privileges to use the Code Runner.
          </Text>
        </View>
      </View>
    );
  }

  // ── Handlers ─────────────────────────────────────────────────────────────

  const startPolling = (id: string) => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const [statusRes, logsRes] = await Promise.all([
          getCodeRunStatus(id),
          getCodeRunLogs(id),
        ]);

        setStatusInfo(statusRes);
        setStatus(statusRes.status as RunStatus);
        setLogs(logsRes.lines);
        setTotalLines(logsRes.total_lines);
        setTruncated(logsRes.truncated);

        // Auto-scroll to bottom
        setTimeout(() => logScrollRef.current?.scrollToEnd({ animated: false }), 100);

        // Stop polling when done
        if (statusRes.status === 'completed' || statusRes.status === 'failed') {
          if (pollRef.current) clearInterval(pollRef.current);
          pollRef.current = null;
        }
      } catch (err: any) {
        // Don't stop polling on transient errors
        console.warn('[CodeRunner] Poll error:', err?.message);
      }
    }, 1000);
  };

  const handleRun = async () => {
    if (!task.trim()) {
      toast.error('Enter a task description');
      return;
    }

    if (mode === 'apply' && confirmText !== 'APPLY') {
      toast.error('Type APPLY to confirm apply mode');
      return;
    }

    setError(null);
    setSubmitting(true);
    setLogs([]);
    setTotalLines(0);
    setTruncated(false);

    try {
      const res = await startCodeRun(task.trim(), mode);

      if (!res.run_id) {
        setError('Failed to start run — no run_id returned');
        setSubmitting(false);
        return;
      }

      setRunId(res.run_id);
      setStatus('queued');
      setConfirmText('');
      startPolling(res.run_id);
    } catch (err: any) {
      const msg =
        err?.response?.data?.error ||
        err?.response?.data?.detail ||
        err?.message ||
        'Failed to start run';
      const statusCode = err?.response?.status;

      if (statusCode === 403) {
        setError('Access denied (403). Admin privileges required.');
      } else if (statusCode === 409) {
        setError('A run is already in progress. Wait for it to finish.');
      } else {
        setError(msg);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleCopyLogs = async () => {
    if (logs.length === 0) {
      toast.info('No logs to copy');
      return;
    }
    Clipboard.setString(logs.join('\n'));
    toast.success('Logs copied to clipboard');
  };

  const isRunning = status === 'queued' || status === 'running';

  // ── Render ───────────────────────────────────────────────────────────────

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <Text style={styles.title}>Code Runner</Text>
      <Text style={styles.badge}>BETA</Text>
      <Text style={styles.subtitle}>
        Run code-agent tasks against the mobile workspace
      </Text>

      {/* Task Input */}
      <Text style={styles.label}>Task</Text>
      <TextInput
        style={styles.textArea}
        multiline
        numberOfLines={4}
        placeholder="Describe the task..."
        placeholderTextColor="#6b7280"
        value={task}
        onChangeText={setTask}
        editable={!isRunning}
        maxLength={5000}
      />
      <Text style={styles.charCount}>{task.length}/5000</Text>

      {/* Mode Selector */}
      <Text style={styles.label}>Mode</Text>
      <View style={styles.modeRow}>
        <TouchableOpacity
          style={[
            styles.modeBtn,
            mode === 'dry_run' && styles.modeBtnActive,
          ]}
          onPress={() => { setMode('dry_run'); setConfirmText(''); }}
          disabled={isRunning}
        >
          <Text style={[
            styles.modeBtnText,
            mode === 'dry_run' && styles.modeBtnTextActive,
          ]}>
            Dry Run
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[
            styles.modeBtn,
            mode === 'apply' && styles.modeBtnApply,
          ]}
          onPress={() => setMode('apply')}
          disabled={isRunning}
        >
          <Text style={[
            styles.modeBtnText,
            mode === 'apply' && styles.modeBtnTextApply,
          ]}>
            Apply
          </Text>
        </TouchableOpacity>
      </View>

      {/* Apply Warning + Confirmation */}
      {mode === 'apply' && (
        <View style={styles.applyWarning}>
          <Text style={styles.applyWarningIcon}>⚠️</Text>
          <Text style={styles.applyWarningText}>
            Apply mode can modify files. Type APPLY to confirm.
          </Text>
          <TextInput
            style={styles.confirmInput}
            placeholder="Type APPLY"
            placeholderTextColor="#6b7280"
            value={confirmText}
            onChangeText={setConfirmText}
            autoCapitalize="characters"
            editable={!isRunning}
          />
        </View>
      )}

      {/* Run Button */}
      <TouchableOpacity
        style={[
          styles.runBtn,
          (isRunning || submitting) && styles.runBtnDisabled,
          mode === 'apply' && confirmText === 'APPLY' && !isRunning && styles.runBtnApply,
        ]}
        onPress={handleRun}
        disabled={isRunning || submitting || !task.trim()}
      >
        {submitting ? (
          <ActivityIndicator color="#fff" size="small" />
        ) : (
          <Text style={styles.runBtnText}>
            {isRunning ? 'Running...' : mode === 'apply' ? 'Run (Apply)' : 'Run (Dry Run)'}
          </Text>
        )}
      </TouchableOpacity>

      {/* Error */}
      {error && (
        <View style={styles.errorBox}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* Status */}
      {status !== 'idle' && (
        <View style={styles.statusSection}>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Status</Text>
            <View style={[styles.statusChip, { backgroundColor: STATUS_COLORS[status].bg }]}>
              {isRunning && <ActivityIndicator size="small" color={STATUS_COLORS[status].text} style={{ marginRight: 4 }} />}
              <Text style={[styles.statusText, { color: STATUS_COLORS[status].text }]}>
                {status.toUpperCase()}
              </Text>
            </View>
          </View>

          {statusInfo && (
            <>
              <View style={styles.metaRow}>
                <Text style={styles.metaLabel}>Mode</Text>
                <Text style={styles.metaValue}>{statusInfo.mode}</Text>
              </View>
              <View style={styles.metaRow}>
                <Text style={styles.metaLabel}>Workspace</Text>
                <Text style={styles.metaValue}>{statusInfo.workspace}</Text>
              </View>
              {statusInfo.started_at && (
                <View style={styles.metaRow}>
                  <Text style={styles.metaLabel}>Started</Text>
                  <Text style={styles.metaValue}>
                    {new Date(statusInfo.started_at).toLocaleTimeString()}
                  </Text>
                </View>
              )}
              {statusInfo.finished_at && (
                <View style={styles.metaRow}>
                  <Text style={styles.metaLabel}>Finished</Text>
                  <Text style={styles.metaValue}>
                    {new Date(statusInfo.finished_at).toLocaleTimeString()}
                  </Text>
                </View>
              )}
              {statusInfo.exit_code !== null && (
                <View style={styles.metaRow}>
                  <Text style={styles.metaLabel}>Exit Code</Text>
                  <Text style={[
                    styles.metaValue,
                    { color: statusInfo.exit_code === 0 ? '#22c55e' : '#ef4444' },
                  ]}>
                    {statusInfo.exit_code}
                  </Text>
                </View>
              )}
            </>
          )}
        </View>
      )}

      {/* Logs */}
      {(logs.length > 0 || isRunning) && (
        <View style={styles.logsSection}>
          <View style={styles.logsHeader}>
            <Text style={styles.logsTitle}>
              Logs {totalLines > 0 ? `(${totalLines} lines${truncated ? ', truncated' : ''})` : ''}
            </Text>
            <TouchableOpacity onPress={handleCopyLogs} style={styles.copyBtn}>
              <Text style={styles.copyBtnText}>Copy</Text>
            </TouchableOpacity>
          </View>
          <ScrollView
            ref={logScrollRef}
            style={styles.logsContainer}
            nestedScrollEnabled
          >
            {logs.length === 0 && isRunning ? (
              <Text style={styles.logLine}>Waiting for output...</Text>
            ) : (
              logs.map((line, i) => (
                <Text key={i} style={styles.logLine}>{line}</Text>
              ))
            )}
          </ScrollView>
        </View>
      )}

      {/* Footer spacer */}
      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

// ── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0f',
  },
  content: {
    padding: 16,
  },
  title: {
    color: '#ffffff',
    fontSize: 24,
    fontWeight: '800',
    marginBottom: 2,
  },
  badge: {
    color: '#f59e0b',
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 1.5,
    marginBottom: 4,
  },
  subtitle: {
    color: '#9ca3af',
    fontSize: 13,
    marginBottom: 20,
  },
  label: {
    color: '#d1d5db',
    fontSize: 13,
    fontWeight: '600',
    marginBottom: 6,
    marginTop: 12,
  },
  textArea: {
    backgroundColor: '#1a1a2e',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#374151',
    color: '#e5e7eb',
    fontSize: 14,
    padding: 12,
    minHeight: 100,
    textAlignVertical: 'top',
    fontFamily: 'monospace',
  },
  charCount: {
    color: '#6b7280',
    fontSize: 11,
    textAlign: 'right',
    marginTop: 4,
  },

  // Mode selector
  modeRow: {
    flexDirection: 'row',
    gap: 8,
  },
  modeBtn: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#374151',
    alignItems: 'center',
  },
  modeBtnActive: {
    borderColor: '#3b82f6',
    backgroundColor: 'rgba(59,130,246,0.15)',
  },
  modeBtnApply: {
    borderColor: '#ef4444',
    backgroundColor: 'rgba(239,68,68,0.1)',
  },
  modeBtnText: {
    color: '#9ca3af',
    fontSize: 14,
    fontWeight: '600',
  },
  modeBtnTextActive: {
    color: '#3b82f6',
  },
  modeBtnTextApply: {
    color: '#ef4444',
  },

  // Apply warning
  applyWarning: {
    backgroundColor: 'rgba(239,68,68,0.08)',
    borderWidth: 1,
    borderColor: 'rgba(239,68,68,0.3)',
    borderRadius: 8,
    padding: 12,
    marginTop: 12,
  },
  applyWarningIcon: {
    fontSize: 18,
    marginBottom: 6,
  },
  applyWarningText: {
    color: '#fca5a5',
    fontSize: 13,
    marginBottom: 8,
  },
  confirmInput: {
    backgroundColor: '#1a1a2e',
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#ef4444',
    color: '#ef4444',
    fontSize: 14,
    fontWeight: '700',
    padding: 8,
    textAlign: 'center',
    letterSpacing: 2,
  },

  // Run button
  runBtn: {
    backgroundColor: '#3b82f6',
    borderRadius: 8,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 16,
  },
  runBtnApply: {
    backgroundColor: '#dc2626',
  },
  runBtnDisabled: {
    opacity: 0.5,
  },
  runBtnText: {
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '700',
  },

  // Error
  errorBox: {
    backgroundColor: 'rgba(239,68,68,0.1)',
    borderRadius: 8,
    padding: 12,
    marginTop: 12,
  },
  errorText: {
    color: '#fca5a5',
    fontSize: 13,
  },

  // Status
  statusSection: {
    marginTop: 20,
    backgroundColor: '#1a1a2e',
    borderRadius: 8,
    padding: 12,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusLabel: {
    color: '#9ca3af',
    fontSize: 13,
    fontWeight: '600',
  },
  statusChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  metaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  metaLabel: {
    color: '#6b7280',
    fontSize: 12,
  },
  metaValue: {
    color: '#d1d5db',
    fontSize: 12,
    fontFamily: 'monospace',
  },

  // Logs
  logsSection: {
    marginTop: 16,
  },
  logsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  logsTitle: {
    color: '#d1d5db',
    fontSize: 13,
    fontWeight: '600',
  },
  copyBtn: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 6,
    backgroundColor: 'rgba(59,130,246,0.15)',
  },
  copyBtnText: {
    color: '#3b82f6',
    fontSize: 12,
    fontWeight: '600',
  },
  logsContainer: {
    backgroundColor: '#0d0d14',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#1f2937',
    padding: 10,
    maxHeight: 400,
  },
  logLine: {
    color: '#a3e635',
    fontSize: 11,
    fontFamily: 'monospace',
    lineHeight: 16,
  },

  // Gate (admin-only / demo)
  gateBox: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 32,
  },
  gateIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  gateTitle: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 8,
  },
  gateText: {
    color: '#9ca3af',
    fontSize: 14,
    textAlign: 'center',
  },
});
