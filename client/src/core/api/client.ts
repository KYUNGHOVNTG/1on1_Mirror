/**
 * API Client Singleton
 *
 * 모든 HTTP 요청은 이 클라이언트를 통해 처리됩니다.
 * 컴포넌트에서 axios를 직접 사용하지 마세요.
 *
 * @example
 * import { apiClient } from '@/core/api/client';
 * const response = await apiClient.get('/users');
 */

import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse, AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { LoadingManager } from '../loading/LoadingManager';
import { ApiErrorHandler } from '../errors/ApiErrorHandler';
import { useAuthStore } from '../store/useAuthStore';

class ApiClient {
  private instance: AxiosInstance;
  private static _instance: ApiClient;
  private isRefreshing = false;
  private failedQueue: Array<{
    resolve: (value?: any) => void;
    reject: (error?: any) => void;
  }> = [];

  private constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  /**
   * Singleton 인스턴스 반환
   */
  public static getInstance(): ApiClient {
    if (!ApiClient._instance) {
      ApiClient._instance = new ApiClient();
    }
    return ApiClient._instance;
  }

  /**
   * 실패한 요청 큐 처리
   */
  private processQueue(error: any, token: string | null = null): void {
    this.failedQueue.forEach((prom) => {
      if (error) {
        prom.reject(error);
      } else {
        prom.resolve(token);
      }
    });

    this.failedQueue = [];
  }

  /**
   * Refresh Token을 사용하여 Access Token 갱신
   */
  private async refreshAccessToken(): Promise<string> {
    const { refreshToken, updateTokens, logout } = useAuthStore.getState();

    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/v1/auth/refresh`,
        { refresh_token: refreshToken }
      );

      const tokens = response.data;
      updateTokens(tokens);

      return tokens.access_token;
    } catch (error) {
      logout();
      throw error;
    }
  }

  /**
   * Request/Response Interceptors 설정
   *
   * 전역 Loading 및 Error 처리를 자동화합니다.
   */
  private setupInterceptors(): void {
    // Request Interceptor
    this.instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // 전역 로딩 시작
        // config.skipLoading이 true이면 로딩 표시 안 함
        if (!(config as any).skipLoading) {
          LoadingManager.show();
        }

        // 인증 토큰 추가
        const { accessToken } = useAuthStore.getState();
        if (accessToken && config.headers) {
          config.headers.Authorization = `Bearer ${accessToken}`;
        }

        return config;
      },
      (error) => {
        // 요청 실패 시 로딩 숨김
        LoadingManager.hide();
        return Promise.reject(error);
      }
    );

    // Response Interceptor
    this.instance.interceptors.response.use(
      (response) => {
        // 응답 성공 시 로딩 숨김
        LoadingManager.hide();
        return response;
      },
      async (error: AxiosError) => {
        // 응답 실패 시 로딩 숨김
        LoadingManager.hide();

        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        // 401 에러이고 재시도하지 않은 요청인 경우
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            // 이미 토큰 갱신 중이면 큐에 추가
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject });
            })
              .then((token) => {
                if (originalRequest.headers) {
                  originalRequest.headers.Authorization = `Bearer ${token}`;
                }
                return this.instance(originalRequest);
              })
              .catch((err) => {
                return Promise.reject(err);
              });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            const newAccessToken = await this.refreshAccessToken();
            this.processQueue(null, newAccessToken);

            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            }

            return this.instance(originalRequest);
          } catch (refreshError) {
            this.processQueue(refreshError, null);

            // 토큰 갱신 실패 시 로그인 페이지로 리다이렉트
            if (typeof window !== 'undefined') {
              window.location.href = '/login';
            }

            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        // 에러 처리
        const errorData = ApiErrorHandler.handle(error);

        // 인증 에러 처리 (토큰 갱신 시도 후에도 실패한 경우)
        if (ApiErrorHandler.isAuthError(error)) {
          console.warn('🔐 인증 에러:', errorData.message);
        }

        // 변환된 에러 데이터 반환
        return Promise.reject(errorData);
      }
    );
  }

  /**
   * GET 요청
   */
  public async get<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.instance.get<T>(url, config);
  }

  /**
   * POST 요청
   */
  public async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.instance.post<T>(url, data, config);
  }

  /**
   * PUT 요청
   */
  public async put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.instance.put<T>(url, data, config);
  }

  /**
   * PATCH 요청
   */
  public async patch<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.instance.patch<T>(url, data, config);
  }

  /**
   * DELETE 요청
   */
  public async delete<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.instance.delete<T>(url, config);
  }
}

// Singleton 인스턴스 export
export const apiClient = ApiClient.getInstance();
