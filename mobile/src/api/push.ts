import http from './http';

export interface RegisterTokenPayload {
  expo_push_token: string;
  device_name?: string;
  platform: 'ios' | 'android';
}

export async function registerExpoToken(
  payload: RegisterTokenPayload,
): Promise<{ success: boolean }> {
  const { data } = await http.post('/v1/mobile/push/register/', payload);
  return data;
}
