/**
 * Base Service Class
 * All services extend this for common functionality
 */

import { AxiosInstance, AxiosRequestConfig } from 'axios';
import { apiClient, apiHelpers } from '../api/client';
import { ApiResponse, PaginatedResponse, ApiError } from '../types/api.types';

export abstract class BaseService {
  protected client: AxiosInstance;
  protected basePath: string;

  constructor(basePath: string, client?: AxiosInstance) {
    this.basePath = basePath;
    this.client = client || apiClient;
  }

  /**
   * GET request
   */
  protected async get<T = any>(
    path: string = '',
    params?: Record<string, any>,
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.client.get<T>(
        `${this.basePath}${path}`,
        {
          params,
          ...config,
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * POST request
   */
  protected async post<T = any>(
    path: string = '',
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.client.post<T>(
        `${this.basePath}${path}`,
        data,
        config
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * PUT request
   */
  protected async put<T = any>(
    path: string = '',
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.client.put<T>(
        `${this.basePath}${path}`,
        data,
        config
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * PATCH request
   */
  protected async patch<T = any>(
    path: string = '',
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.client.patch<T>(
        `${this.basePath}${path}`,
        data,
        config
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * DELETE request
   */
  protected async delete<T = any>(
    path: string = '',
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.client.delete<T>(
        `${this.basePath}${path}`,
        config
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * GET request for paginated data
   */
  protected async getPaginated<T = any>(
    path: string = '',
    page: number = 1,
    limit: number = 20,
    filters?: Record<string, any>,
    config?: AxiosRequestConfig
  ): Promise<PaginatedResponse<T>> {
    const params = {
      ...apiHelpers.buildPaginationParams(page, limit),
      ...apiHelpers.buildFilterParams(filters || {}),
    };

    return this.get<PaginatedResponse<T>>(path, params, config);
  }

  /**
   * Upload file(s)
   */
  protected async upload<T = any>(
    path: string = '',
    files: File[] | any[],
    additionalData?: Record<string, any>,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const formData = apiHelpers.createFormData({
      ...additionalData,
      files,
    });

    return this.post<T>(path, formData, {
      ...config,
      headers: {
        ...config?.headers,
        'Content-Type': 'multipart/form-data',
      },
    });
  }

  /**
   * Handle API errors consistently
   */
  protected handleError(error: any): ApiError {
    // If already processed by interceptor
    if (error.code && error.message) {
      return error as ApiError;
    }

    // Otherwise, create a generic error
    return {
      message: error.message || 'An unexpected error occurred',
      code: 'UNKNOWN_ERROR',
      details: error,
    };
  }

  /**
   * Retry a request with exponential backoff
   */
  protected async withRetry<T>(
    fn: () => Promise<T>,
    maxAttempts?: number,
    delay?: number
  ): Promise<T> {
    return apiHelpers.retryRequest(fn, maxAttempts, delay);
  }

  /**
   * Check if service is available
   */
  public async healthCheck(): Promise<boolean> {
    try {
      await this.get('/health', {}, { timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }
}