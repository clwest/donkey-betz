/// App Configuration
///
/// Session 100 Part 13 - Flutter Cockpit
/// Session 107 - Donkey Cockpit v1 (Unified Mobile Home + Navigation)
/// Session 111 Part 3 - User Authentication
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/app_theme.dart';
import 'features/cockpit/donkey_cockpit_screen.dart';
import 'features/boardroom/boardroom_form_screen.dart';
import 'features/auth/login_screen.dart';
import 'providers/auth_provider.dart';

class DonkeyOSApp extends StatelessWidget {
  const DonkeyOSApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DonkeyOS Cockpit',
      theme: AppTheme.lightTheme,
      debugShowCheckedModeBanner: false,
      home: const AuthGate(),
      routes: {
        '/cockpit': (context) => const DonkeyCockpitScreen(),
        '/boardroom': (context) => const BoardroomFormScreen(),
        '/login': (context) => const LoginScreen(),
      },
    );
  }
}

/// Authentication gate - shows login or main app based on auth state
class AuthGate extends ConsumerWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authControllerProvider);

    // Show loading while checking auth
    if (authState.isLoading && !authState.isAuthenticated) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    // Show login screen if not authenticated
    if (!authState.isAuthenticated) {
      return const LoginScreen();
    }

    // Show main app if authenticated
    return const DonkeyCockpitScreen();
  }
}
