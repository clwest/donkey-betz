// Session 968: Scoped API helpers — inject X-UI-Scope header for request log filtering
import type { AxiosRequestConfig } from 'axios'
import { api } from './api'

export { getRequestLog, subscribeRequestLog, clearRequestLog } from './api'
export type { RequestLogEntry } from './api'

export function scopedGet<T = unknown>(
  url: string,
  scope: string,
  config?: AxiosRequestConfig
) {
  return api.get<T>(url, {
    ...config,
    headers: { ...config?.headers, 'X-UI-Scope': scope },
  })
}

export function scopedPost<T = unknown>(
  url: string,
  data: unknown,
  scope: string,
  config?: AxiosRequestConfig
) {
  return api.post<T>(url, data, {
    ...config,
    headers: { ...config?.headers, 'X-UI-Scope': scope },
  })
}
