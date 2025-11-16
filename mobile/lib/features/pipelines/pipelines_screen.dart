/// Pipelines Screen - Session 109
///
/// Shows available pipeline templates and recent runs.
/// Allows launching new pipeline runs and viewing run details.

library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:donkey_os_cockpit/core/app_theme.dart';
import 'package:donkey_os_cockpit/models/pipeline_template.dart';
import 'package:donkey_os_cockpit/models/pipeline_run.dart';
import 'package:donkey_os_cockpit/providers/pipelines_provider.dart';
import 'pipeline_run_detail_screen.dart';

class PipelinesScreen extends ConsumerStatefulWidget {
  const PipelinesScreen({super.key});

  @override
  ConsumerState<PipelinesScreen> createState() => _PipelinesScreenState();
}

class _PipelinesScreenState extends ConsumerState<PipelinesScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _showHintBanner = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);

    // Fetch templates and runs on mount
    WidgetsBinding.instance.addPostFrameCallback((_) {
      // Templates auto-fetch on provider creation
      ref.read(pipelineRunListProvider.notifier).fetchRuns(limit: 10);
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Creative Pipelines'),
        backgroundColor: AppTheme.primaryColor,
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Templates', icon: Icon(Icons.view_module)),
            Tab(text: 'Recent Runs', icon: Icon(Icons.history)),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildTemplatesTab(),
          _buildRunsTab(),
        ],
      ),
    );
  }

  // ============================================================================
  // TEMPLATES TAB
  // ============================================================================

  Widget _buildTemplatesTab() {
    final templatesState = ref.watch(pipelineTemplatesProvider);

    if (templatesState.isLoading && templatesState.templates.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Loading pipeline templates...'),
          ],
        ),
      );
    }

    if (templatesState.error != null && templatesState.templates.isEmpty) {
      return _buildErrorState(
        templatesState.error!,
        onRetry: () => ref.read(pipelineTemplatesProvider.notifier).refresh(),
      );
    }

    if (templatesState.templates.isEmpty) {
      return _buildEmptyTemplatesState();
    }

    return RefreshIndicator(
      onRefresh: () => ref.read(pipelineTemplatesProvider.notifier).refresh(),
      child: Column(
        children: [
          if (_showHintBanner) _buildHintBanner(),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: templatesState.templates.length,
              itemBuilder: (context, index) {
                final template = templatesState.templates[index];
                return _buildTemplateCard(template);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHintBanner() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.purple.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.purple.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.lightbulb_outline, color: Colors.purple, size: 20),
          const SizedBox(width: 12),
          const Expanded(
            child: Text(
              'Pro Tip: Try "Idea to Image Set" to go from idea to images in one tap.',
              style: TextStyle(fontSize: 13, color: AppTheme.textPrimary),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, size: 18),
            onPressed: () {
              setState(() {
                _showHintBanner = false;
              });
            },
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(),
          ),
        ],
      ),
    );
  }

  Widget _buildTemplateCard(PipelineTemplate template) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _showLaunchDialog(template),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    _getTemplateIcon(template.slug),
                    size: 28,
                    color: AppTheme.primaryColor,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          template.name,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          template.stepCountText,
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const Icon(Icons.play_circle_filled,
                      color: AppTheme.successColor, size: 32),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                template.description,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[700],
                  height: 1.4,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getTemplateIcon(String slug) {
    if (slug.contains('image')) return Icons.image;
    if (slug.contains('video')) return Icons.videocam;
    if (slug.contains('audio')) return Icons.audiotrack;
    return Icons.auto_awesome;
  }

  Widget _buildEmptyTemplatesState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.view_module_outlined,
              size: 80,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            const Text(
              'No Templates Available',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Pipeline templates will appear here when configured.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }

  // ============================================================================
  // RECENT RUNS TAB
  // ============================================================================

  Widget _buildRunsTab() {
    final runsState = ref.watch(pipelineRunListProvider);

    if (runsState.isLoading && runsState.runs.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Loading recent runs...'),
          ],
        ),
      );
    }

    if (runsState.error != null && runsState.runs.isEmpty) {
      return _buildErrorState(
        runsState.error!,
        onRetry: () => ref.read(pipelineRunListProvider.notifier).refresh(),
      );
    }

    if (runsState.runs.isEmpty) {
      return _buildEmptyRunsState();
    }

    return RefreshIndicator(
      onRefresh: () => ref.read(pipelineRunListProvider.notifier).refresh(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: runsState.runs.length,
        itemBuilder: (context, index) {
          final run = runsState.runs[index];
          return _buildRunCard(run);
        },
      ),
    );
  }

  Widget _buildRunCard(PipelineRun run) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _navigateToRunDetail(run.id),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Color(run.statusColor).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      run.statusIcon,
                      style: const TextStyle(fontSize: 20),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          run.templateName,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          run.statusText,
                          style: TextStyle(
                            fontSize: 12,
                            color: Color(run.statusColor),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const Icon(Icons.chevron_right, color: Colors.grey),
                ],
              ),
              if (run.isActive) ...[
                const SizedBox(height: 12),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: run.progressPercentage / 100.0,
                    backgroundColor: Colors.grey[200],
                    valueColor: AlwaysStoppedAnimation<Color>(
                      Color(run.statusColor),
                    ),
                    minHeight: 6,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  run.progressText,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyRunsState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.history_outlined,
              size: 80,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            const Text(
              'No Runs Yet',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Start your first pipeline from the Templates tab!',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => _tabController.animateTo(0),
              icon: const Icon(Icons.view_module),
              label: const Text('Browse Templates'),
            ),
          ],
        ),
      ),
    );
  }

  // ============================================================================
  // SHARED WIDGETS
  // ============================================================================

  Widget _buildErrorState(String error, {required VoidCallback onRetry}) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: AppTheme.errorColor,
            ),
            const SizedBox(height: 16),
            const Text(
              'Error loading data',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              error,
              textAlign: TextAlign.center,
              style: const TextStyle(color: AppTheme.errorColor),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('Try Again'),
            ),
          ],
        ),
      ),
    );
  }

  // ============================================================================
  // NAVIGATION & ACTIONS
  // ============================================================================

  void _navigateToRunDetail(String runId) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => PipelineRunDetailScreen(runId: runId),
      ),
    );
  }

  void _showLaunchDialog(PipelineTemplate template) {
    showDialog(
      context: context,
      builder: (context) => _LaunchPipelineDialog(template: template),
    );
  }
}

// ============================================================================
// LAUNCH PIPELINE DIALOG
// ============================================================================

class _LaunchPipelineDialog extends ConsumerStatefulWidget {
  final PipelineTemplate template;

  const _LaunchPipelineDialog({required this.template});

  @override
  ConsumerState<_LaunchPipelineDialog> createState() =>
      _LaunchPipelineDialogState();
}

class _LaunchPipelineDialogState
    extends ConsumerState<_LaunchPipelineDialog> {
  final _formKey = GlobalKey<FormState>();
  final _controllers = <String, TextEditingController>{};
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    // Create controllers for each input
    for (final key in widget.template.inputs.keys) {
      _controllers[key] = TextEditingController();
    }
  }

  @override
  void dispose() {
    for (final controller in _controllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Launch: ${widget.template.name}'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                widget.template.description,
                style: TextStyle(color: Colors.grey[700], fontSize: 14),
              ),
              const SizedBox(height: 24),
              ...widget.template.inputs.entries.map((entry) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: _buildInputField(entry.key, entry.value),
                );
              }),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isSubmitting ? null : () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _isSubmitting ? null : _submitPipeline,
          child: _isSubmitting
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Launch'),
        ),
      ],
    );
  }

  Widget _buildInputField(String key, dynamic config) {
    final isRequired = config is Map && config['required'] == true;
    final inputType = config is Map ? config['type'] as String? : 'string';

    return TextFormField(
      controller: _controllers[key],
      decoration: InputDecoration(
        labelText: _formatLabel(key),
        hintText: _getHintText(key, config),
        border: const OutlineInputBorder(),
      ),
      keyboardType: inputType == 'int' ? TextInputType.number : TextInputType.text,
      maxLines: key == 'idea' ? 3 : 1,
      validator: (value) {
        if (isRequired && (value == null || value.trim().isEmpty)) {
          return 'This field is required';
        }
        if (inputType == 'int' && value != null && value.isNotEmpty) {
          if (int.tryParse(value) == null) {
            return 'Please enter a valid number';
          }
        }
        return null;
      },
    );
  }

  String _formatLabel(String key) {
    return key.split('_').map((word) {
      return word[0].toUpperCase() + word.substring(1);
    }).join(' ');
  }

  String _getHintText(String key, dynamic config) {
    if (key == 'idea') {
      return 'Describe your creative concept...';
    }
    if (config is Map && config['default'] != null) {
      return 'Default: ${config['default']}';
    }
    return '';
  }

  Future<void> _submitPipeline() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      // Build input payload
      final inputPayload = <String, dynamic>{};
      for (final entry in _controllers.entries) {
        final value = entry.value.text.trim();
        if (value.isNotEmpty) {
          // Parse int values
          final config = widget.template.inputs[entry.key];
          final inputType = config is Map ? config['type'] as String? : 'string';
          if (inputType == 'int') {
            inputPayload[entry.key] = int.parse(value);
          } else {
            inputPayload[entry.key] = value;
          }
        }
      }

      // Call API to create run
      final createRun = ref.read(createPipelineRunProvider);
      final run = await createRun(
        templateSlug: widget.template.slug,
        inputPayload: inputPayload,
      );

      if (!mounted) return;

      // Close dialog
      Navigator.pop(context);

      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Pipeline "${widget.template.name}" started!'),
          backgroundColor: AppTheme.successColor,
          action: SnackBarAction(
            label: 'View',
            textColor: Colors.white,
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => PipelineRunDetailScreen(runId: run.id),
                ),
              );
            },
          ),
        ),
      );

      // Refresh runs list
      ref.read(pipelineRunListProvider.notifier).refresh();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error launching pipeline: $e'),
          backgroundColor: AppTheme.errorColor,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }
}
