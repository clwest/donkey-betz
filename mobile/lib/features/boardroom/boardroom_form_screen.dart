/// Boardroom Form Screen - Start a new executive meeting
///
/// Session 100 Part 13 - Flutter Cockpit
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/app_theme.dart';
import '../../core/api_config.dart';
import '../../providers/boardroom_provider.dart';
import '../../providers/projects_provider.dart';
import 'boardroom_result_screen.dart';

class BoardroomFormScreen extends ConsumerStatefulWidget {
  const BoardroomFormScreen({super.key});

  @override
  ConsumerState<BoardroomFormScreen> createState() =>
      _BoardroomFormScreenState();
}

class _BoardroomFormScreenState extends ConsumerState<BoardroomFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _topicController = TextEditingController();
  String? _selectedProjectId;
  final Set<String> _selectedParticipants = {'CTOAgent', 'COOAgent'};

  @override
  void dispose() {
    _topicController.dispose();
    super.dispose();
  }

  Future<void> _startMeeting() async {
    if (!_formKey.currentState!.validate()) return;

    if (_selectedParticipants.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select at least one participant'),
          backgroundColor: AppTheme.errorColor,
        ),
      );
      return;
    }

    // Start the meeting
    await ref.read(boardroomControllerProvider.notifier).startMeeting(
          topic: _topicController.text.trim(),
          projectId: _selectedProjectId,
          participants: _selectedParticipants.toList(),
        );

    // Check result
    final state = ref.read(boardroomControllerProvider);

    if (state.error != null) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(state.error!),
          backgroundColor: AppTheme.errorColor,
        ),
      );
    } else if (state.result != null) {
      if (!mounted) return;
      // Navigate to result screen
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) =>
              BoardroomResultScreen(meeting: state.result!),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final boardroomState = ref.watch(boardroomControllerProvider);
    final projectsAsync = ref.watch(projectsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Start Executive Meeting'),
        backgroundColor: AppTheme.primaryColor,
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Topic Field
            TextFormField(
              controller: _topicController,
              decoration: const InputDecoration(
                labelText: 'Meeting Topic *',
                hintText: 'e.g., Q4 Product Launch Strategy',
                prefixIcon: Icon(Icons.topic),
              ),
              maxLines: 3,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter a meeting topic';
                }
                return null;
              },
            ),
            const SizedBox(height: 20),

            // Project Selection (Optional)
            projectsAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stack) => const SizedBox.shrink(),
              data: (projects) {
                if (projects.isEmpty) return const SizedBox.shrink();

                return DropdownButtonFormField<String>(
                  value: _selectedProjectId,
                  decoration: const InputDecoration(
                    labelText: 'Project (Optional)',
                    prefixIcon: Icon(Icons.folder),
                  ),
                  items: [
                    const DropdownMenuItem<String>(
                      value: null,
                      child: Text('No project'),
                    ),
                    ...projects.map((project) {
                      return DropdownMenuItem<String>(
                        value: project.projectId,
                        child: Text(project.name),
                      );
                    }).toList(),
                  ],
                  onChanged: (value) {
                    setState(() {
                      _selectedProjectId = value;
                    });
                  },
                );
              },
            ),
            const SizedBox(height: 20),

            // Participants Selection
            Text(
              'Select Participants *',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Choose which executives to include in the meeting',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.textSecondary,
                  ),
            ),
            const SizedBox(height: 12),

            // Participant Chips
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: ApiConfig.executiveAgents.map((agent) {
                final isSelected = _selectedParticipants.contains(agent);
                return FilterChip(
                  selected: isSelected,
                  label: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        AppTheme.getAgentIcon(agent),
                        size: 16,
                        color: isSelected ? Colors.white : AppTheme.primaryColor,
                      ),
                      const SizedBox(width: 4),
                      Text(ApiConfig.getAgentDisplayName(agent)),
                    ],
                  ),
                  onSelected: (selected) {
                    setState(() {
                      if (selected) {
                        _selectedParticipants.add(agent);
                      } else {
                        _selectedParticipants.remove(agent);
                      }
                    });
                  },
                  selectedColor: AppTheme.primaryColor,
                  labelStyle: TextStyle(
                    color: isSelected ? Colors.white : AppTheme.primaryColor,
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 24),

            // Start Meeting Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: boardroomState.isLoading ? null : _startMeeting,
                icon: boardroomState.isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor:
                              AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : const Icon(Icons.meeting_room),
                label: Text(
                  boardroomState.isLoading
                      ? 'Starting Meeting...'
                      : 'Start Meeting',
                ),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 50),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
