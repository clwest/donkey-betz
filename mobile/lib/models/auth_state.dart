/// Authentication State Models
///
/// Session 111 Part 3 - User Authentication
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'auth_state.freezed.dart';

/// User data from authentication
@freezed
class AuthUser with _$AuthUser {
  const factory AuthUser({
    required String id,
    required String username,
    required String email,
    @Default(0) int credits,
    @Default('free') String subscription,
  }) = _AuthUser;

  factory AuthUser.fromJson(Map<String, dynamic> json) {
    return AuthUser(
      id: json['id'] as String,
      username: json['username'] as String,
      email: json['email'] as String,
      credits: json['credits'] as int? ?? 0,
      subscription: json['subscription'] as String? ?? 'free',
    );
  }
}

/// Authentication state
@freezed
class AuthState with _$AuthState {
  const factory AuthState({
    AuthUser? user,
    String? token,
    @Default(false) bool isLoading,
    @Default(false) bool isAuthenticated,
    String? errorMessage,
  }) = _AuthState;
}
