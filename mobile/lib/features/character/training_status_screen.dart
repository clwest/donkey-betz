/// Training Status Screen - Monitor character training progress
/// Session 115 Part 4 - Full Feature Parity
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dart:async';
import '../../providers/api_provider.dart';

class TrainingStatusScreen extends ConsumerStatefulWidget {
  const TrainingStatusScreen({super.key});

  @override
  ConsumerState<TrainingStatusScreen> createState() => _TrainingStatusScreenState();
}

class _TrainingStatusScreenState extends ConsumerState<TrainingStatusScreen> {
  List<Map<String, dynamic>> _trainingJobs = [];
  bool _isLoading = false;
  String? _errorMessage;
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    _loadTrainingJobs();
    // Auto-refresh every 30 seconds
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      _loadTrainingJobs();
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadTrainingJobs() async {
    setState(() => _isLoading = true);

    try {
      final apiClient = ref.read(apiClientProvider);
      final response = await apiClient.get('/api/v1/character/status/');

      if (response['success'] == true && response['jobs'] != null) {
        setState(() {
          _trainingJobs = List<Map<String, dynamic>>.from(response['jobs']);
          _isLoading = false;
          _errorMessage = null;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'succeeded':
        return Colors.green;
      case 'processing':
      case 'training':
      case 'running':
        return Colors.orange;
      case 'failed':
      case 'canceled':
        return Colors.red;
      case 'queued':
      case 'starting':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  IconData _getStatusIcon(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'succeeded':
        return Icons.check_circle;
      case 'processing':
      case 'training':
      case 'running':
        return Icons.hourglass_bottom;
      case 'failed':
      case 'canceled':
        return Icons.error;
      case 'queued':
      case 'starting':
        return Icons.schedule;
      default:
        return Icons.help;
    }
  }

  String _formatDuration(int? seconds) {
    if (seconds == null) return 'N/A';
    final minutes = seconds ~/ 60;
    final secs = seconds % 60;
    if (minutes > 0) {
      return '${minutes}m ${secs}s';
    }
    return '${secs}s';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Training Status'),
        backgroundColor: Colors.brown,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadTrainingJobs,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _isLoading && _trainingJobs.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadTrainingJobs,
              child: _trainingJobs.isEmpty
                  ? _buildEmptyState()
                  : ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: _trainingJobs.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 12),
                      itemBuilder: (context, index) {
                        final job = _trainingJobs[index];
                        return _buildTrainingCard(job);
                      },
                    ),
            ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.school, size: 64, color: Colors.grey),
          const SizedBox(height: 16),
          const Text('No training jobs',
              style: TextStyle(fontSize: 18, color: Colors.grey)),
          const SizedBox(height: 8),
          const Text('Start training a character to see status here',
              style: TextStyle(fontSize: 12, color: Colors.grey)),
          const SizedBox(height: 24),
          if (_errorMessage != null)
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(_errorMessage!,
                  style: const TextStyle(color: Colors.red),
                  textAlign: TextAlign.center),
            ),
        ],
      ),
    );
  }

  Widget _buildTrainingCard(Map<String, dynamic> job) {
    final status = job['status'] ?? 'unknown';
    final progress = job['progress'] ?? 0.0;
    final characterName = job['character_name'] ?? 'Unknown';
    final triggerWord = job['trigger_word'] ?? 'N/A';
    final startedAt = job['started_at'] ?? 'N/A';
    final estimatedTime = job['estimated_time'];
    final trainingId = job['id'] ?? 'N/A';

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Icon(
                  _getStatusIcon(status),
                  color: _getStatusColor(status),
                  size: 28,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        characterName,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        'Trigger: $triggerWord',
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: _getStatusColor(status).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: _getStatusColor(status)),
                  ),
                  child: Text(
                    status.toUpperCase(),
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: _getStatusColor(status),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Progress Bar (if training)
            if (status.toLowerCase() == 'training' ||
                status.toLowerCase() == 'processing') ...[
              LinearProgressIndicator(
                value: progress,
                backgroundColor: Colors.grey.shade200,
                valueColor: AlwaysStoppedAnimation(_getStatusColor(status)),
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${(progress * 100).toInt()}% complete',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                  if (estimatedTime != null)
                    Text(
                      '~${_formatDuration(estimatedTime)} remaining',
                      style: const TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                ],
              ),
              const SizedBox(height: 12),
            ],

            // Details
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                children: [
                  _buildDetailRow('Training ID', trainingId.toString()),
                  const Divider(height: 16),
                  _buildDetailRow('Started', startedAt.toString()),
                  if (job['completed_at'] != null) ...[
                    const Divider(height: 16),
                    _buildDetailRow('Completed', job['completed_at'].toString()),
                  ],
                  if (job['error_message'] != null) ...[
                    const Divider(height: 16),
                    _buildDetailRow(
                      'Error',
                      job['error_message'].toString(),
                      isError: true,
                    ),
                  ],
                ],
              ),
            ),

            // Actions
            if (status.toLowerCase() == 'completed' ||
                status.toLowerCase() == 'succeeded') ...[
              const SizedBox(height: 12),
              ElevatedButton.icon(
                onPressed: () {
                  // Navigate to character generation
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Navigate to Character Generation screen'),
                    ),
                  );
                },
                icon: const Icon(Icons.auto_awesome, size: 18),
                label: const Text('Generate with Character'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.brown,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value, {bool isError = false}) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 90,
          child: Text(
            '$label:',
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: Colors.grey,
            ),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: TextStyle(
              fontSize: 12,
              color: isError ? Colors.red : Colors.black87,
            ),
          ),
        ),
      ],
    );
  }
}
