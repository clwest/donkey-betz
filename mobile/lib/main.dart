/// DonkeyOS Flutter Cockpit - Main Entry Point
///
/// Session 100 Part 13 - Human-AI Co-Leadership on Mobile
///
/// Created by: Claude Code + Chris Partnership
/// Date: November 15, 2025
library;

import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'providers/settings_provider.dart';
import 'app.dart';

void main() async {
  // Ensure Flutter bindings are initialized
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize SharedPreferences (required for settings provider from Session 102)
  final sharedPrefs = await SharedPreferences.getInstance();

  // Load environment variables
  try {
    await dotenv.load(fileName: '.env');
  } catch (e) {
    // If .env doesn't exist, that's ok - will use defaults
    debugPrint('Warning: .env file not found, using defaults');
  }

  // Run the app with Riverpod provider scope
  // Override the FutureProvider with the already-initialized instance
  runApp(
    ProviderScope(
      overrides: [
        sharedPreferencesProvider.overrideWith((ref) => Future.value(sharedPrefs)),
      ],
      child: const DonkeyOSApp(),
    ),
  );
}
