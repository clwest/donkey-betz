/// Settings Screen
///
/// Session 102 - Mobile Auth & Connection Settings
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/settings_provider.dart';
import '../../models/connection_status.dart';
import '../../core/app_theme.dart';
import '../leadership/coleadership_settings_screen.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  final _formKey = GlobalKey<FormState>();
  final _baseUrlController = TextEditingController();
  final _apiKeyController = TextEditingController();
  bool _obscureApiKey = true;

  @override
  void initState() {
    super.initState();
    // Load initial values
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final settings = ref.read(settingsControllerProvider);
      _baseUrlController.text = settings.apiBaseUrl ?? 'http://localhost:8000';
      _apiKeyController.text = settings.apiKey ?? '';
    });
  }

  @override
  void dispose() {
    _baseUrlController.dispose();
    _apiKeyController.dispose();
    super.dispose();
  }

  void _handleSave() {
    if (_formKey.currentState?.validate() ?? false) {
      ref.read(settingsControllerProvider.notifier).saveSettings(
            apiBaseUrl: _baseUrlController.text.trim(),
            apiKey: _apiKeyController.text.trim(),
          );
    }
  }

  void _handleTestConnection() {
    ref.read(settingsControllerProvider.notifier).testConnection();
  }

  void _handleClear() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear Settings'),
        content: const Text(
          'Are you sure you want to clear all settings? This will remove your API endpoint and key.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              ref.read(settingsControllerProvider.notifier).clearSettings();
              _baseUrlController.text = 'http://localhost:8000';
              _apiKeyController.clear();
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.errorColor,
            ),
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }

  Color _getStatusColor(ConnectionStatus? status) {
    if (status == null) return AppTheme.textSecondary;
    switch (status) {
      case ConnectionStatus.connected:
        return AppTheme.successColor;
      case ConnectionStatus.failed:
        return AppTheme.errorColor;
      case ConnectionStatus.notConfigured:
        return AppTheme.warningColor;
    }
  }

  IconData _getStatusIcon(ConnectionStatus? status) {
    if (status == null) return Icons.help_outline;
    switch (status) {
      case ConnectionStatus.connected:
        return Icons.check_circle;
      case ConnectionStatus.failed:
        return Icons.error;
      case ConnectionStatus.notConfigured:
        return Icons.warning;
    }
  }

  @override
  Widget build(BuildContext context) {
    final settings = ref.watch(settingsControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: _handleClear,
            tooltip: 'Clear Settings',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Connection Status Card
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            _getStatusIcon(settings.lastTestResult),
                            color: _getStatusColor(settings.lastTestResult),
                            size: 24,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Connection Status',
                                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                        fontWeight: FontWeight.w600,
                                      ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  settings.lastTestResult?.displayName ?? 'Unknown',
                                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                        color: _getStatusColor(settings.lastTestResult),
                                        fontWeight: FontWeight.w500,
                                      ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      if (settings.lastTestMessage != null) ...[
                        const SizedBox(height: 12),
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: _getStatusColor(settings.lastTestResult).withOpacity(0.1),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            settings.lastTestMessage!,
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ),
                      ],
                      if (settings.lastSuccessfulConnection != null) ...[
                        const SizedBox(height: 12),
                        Text(
                          'Last connected: ${_formatDateTime(settings.lastSuccessfulConnection!)}',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: AppTheme.textSecondary,
                              ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // API Base URL Field
              Text(
                'API Endpoint',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _baseUrlController,
                decoration: const InputDecoration(
                  hintText: 'http://localhost:8000',
                  prefixIcon: Icon(Icons.link),
                  helperText: 'Backend API base URL',
                ),
                keyboardType: TextInputType.url,
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'API base URL is required';
                  }
                  if (!value.startsWith('http://') && !value.startsWith('https://')) {
                    return 'URL must start with http:// or https://';
                  }
                  return null;
                },
              ),

              const SizedBox(height: 24),

              // API Key Field
              Text(
                'API Key',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _apiKeyController,
                decoration: InputDecoration(
                  hintText: 'Enter your API key',
                  prefixIcon: const Icon(Icons.key),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscureApiKey ? Icons.visibility : Icons.visibility_off,
                    ),
                    onPressed: () {
                      setState(() {
                        _obscureApiKey = !_obscureApiKey;
                      });
                    },
                  ),
                  helperText: 'API key for authentication',
                ),
                obscureText: _obscureApiKey,
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'API key is required';
                  }
                  if (value.trim().length < 10) {
                    return 'API key seems too short';
                  }
                  return null;
                },
              ),

              const SizedBox(height: 32),

              // Action Buttons
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: settings.isTesting ? null : _handleTestConnection,
                      icon: settings.isTesting
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.wifi_find),
                      label: Text(settings.isTesting ? 'Testing...' : 'Test Connection'),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: settings.isSaving ? null : _handleSave,
                      icon: settings.isSaving
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.save),
                      label: Text(settings.isSaving ? 'Saving...' : 'Save'),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // Info Card
              Card(
                color: AppTheme.infoColor.withOpacity(0.1),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(
                            Icons.info_outline,
                            color: AppTheme.infoColor,
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Configuration Help',
                            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                  fontWeight: FontWeight.w600,
                                  color: AppTheme.infoColor,
                                ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text(
                        '• Default development endpoint: http://localhost:8000\n'
                        '• For production, use your backend URL (e.g., https://api.example.com)\n'
                        '• The API key authenticates all requests to the backend\n'
                        '• Use "Test Connection" to verify your configuration',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // Other Settings Section
              Text(
                'Other Settings',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
              ),
              const SizedBox(height: 12),

              // Co-Leadership Preferences Link
              Card(
                child: ListTile(
                  leading: const Icon(
                    Icons.psychology,
                    color: AppTheme.primaryColor,
                  ),
                  title: const Text('Co-Leadership Preferences'),
                  subtitle: const Text('Customize AI partnership settings'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const CoLeadershipSettingsScreen(),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes} minute${difference.inMinutes == 1 ? '' : 's'} ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours} hour${difference.inHours == 1 ? '' : 's'} ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} day${difference.inDays == 1 ? '' : 's'} ago';
    } else {
      return '${dateTime.day}/${dateTime.month}/${dateTime.year}';
    }
  }
}
