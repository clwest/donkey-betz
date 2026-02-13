// ApiError class and helpers to normalize errors

import type { APIErrorPayload } from "../api/types";

export class ApiError extends Error {
  public status: number;
  public payload?: APIErrorPayload;

  constructor(message: string, status = 0, payload?: APIErrorPayload) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

/**
 * Safely parse JSON response. Returns undefined if no JSON body present.
 */
export async function safeParseJSON(response: Response): Promise<any | undefined> {
  const contentType = response.headers.get("content-type");
  if (!contentType) return undefined;
  if (contentType.includes("application/json")) {
    try {
      return await response.json();
    } catch {
      return undefined;
    }
  }
  return undefined;
}

/**
 * Convert a fetch Response into an ApiError
 */
export async function toApiError(response: Response): Promise<ApiError> {
  const payload = (await safeParseJSON(response)) as APIErrorPayload | undefined;
  const message = payload?.message ?? response.statusText ?? "Unknown error";
  return new ApiError(message, response.status, payload);
}