/**
 * VIP Invite API — exchange magic-link tokens for API credentials.
 */

import http from './http';

export interface VIPCredentials {
  api_key: string;
  username: string;
  expires_at: string;
  role: string;
}

/**
 * Exchange a VIP invite token for API credentials.
 * This is the only public (unauthenticated) call in this module.
 */
export async function exchangeVIPToken(token: string): Promise<VIPCredentials> {
  const res = await http.post('/v1/vip-invites/exchange/', { token });
  return res.data;
}
