import http from '../api/http';
import type { AuthUser } from './tokenStore';

// ── Login ────────────────────────────────────────────────────────────────────
// POST /api/v1/auth/login/
// Contract: { username, password } → { token, user }

export interface LoginResponse {
  token: string;
  user: AuthUser;
}

export async function login(
  username: string,
  password: string,
): Promise<LoginResponse> {
  const { data } = await http.post<LoginResponse>('/v1/auth/login/', {
    username,
    password,
  });
  return data;
}

// ── Logout ───────────────────────────────────────────────────────────────────
// POST /api/v1/auth/logout/

export async function logout(): Promise<void> {
  try {
    await http.post('/v1/auth/logout/');
  } catch {
    // Server-side logout is best-effort; token cleared locally regardless
  }
}

// ── Get current user ─────────────────────────────────────────────────────────
// GET /api/v1/auth/user/

export interface GetUserResponse {
  user: AuthUser;
}

export async function getUser(): Promise<AuthUser> {
  const { data } = await http.get<GetUserResponse>('/v1/auth/user/');
  return data.user;
}

// ── Validate token ───────────────────────────────────────────────────────────
// POST /api/v1/auth/validate-token/

export interface ValidateTokenResponse {
  valid: boolean;
  user?: AuthUser;
  error?: string;
}

export async function validateToken(token: string): Promise<ValidateTokenResponse> {
  const { data } = await http.post<ValidateTokenResponse>('/v1/auth/validate-token/', { token });
  return data;
}
