/**
 * Calendar Domain API
 *
 * 캘린더 도메인의 API 통신 로직
 * apiClient를 사용하여 백엔드와 통신합니다.
 *
 * @important 컴포넌트에서 axios를 직접 사용하지 마세요!
 */

import { apiClient } from '@/core/api';
import type { ApiResponse } from '@/core/api';
import type {
    CalendarConnectionCreate,
    CalendarConnection,
    CalendarEvent,
    CalendarEventListResponse,
    CalendarEventListParams,
    CalendarSyncRequest,
    CalendarSyncResponse,
    EventSelectionRequest,
    EventSelectionResponse,
} from './types';

// ====================
// Calendar Connection API
// ====================

/**
 * 구글 캘린더 연동 생성
 *
 * @param data - 캘린더 연동 생성 요청
 * @returns 생성된 캘린더 연동 정보
 */
export async function connectCalendar(
    data: CalendarConnectionCreate
): Promise<CalendarConnection> {
    const response = await apiClient.post<ApiResponse<CalendarConnection>>(
        '/v1/calendar/connect',
        data
    );
    return response.data.data;
}

/**
 * 캘린더 연동 상태 조회
 *
 * @returns 현재 캘린더 연동 정보 (없으면 null)
 */
export async function getCalendarConnection(): Promise<CalendarConnection | null> {
    try {
        const response = await apiClient.get<ApiResponse<CalendarConnection>>(
            '/v1/calendar/connection'
        );
        return response.data.data;
    } catch (error: any) {
        // 404 에러는 연동이 없는 경우이므로 null 반환
        if (error.status === 404) {
            return null;
        }
        throw error;
    }
}

/**
 * 캘린더 연동 해제
 *
 * @returns void
 */
export async function disconnectCalendar(): Promise<void> {
    await apiClient.delete('/v1/calendar/connection');
}

// ====================
// Calendar Sync API
// ====================

/**
 * 캘린더 이벤트 동기화
 *
 * @param request - 동기화 요청 (옵션)
 * @returns 동기화 결과
 */
export async function syncCalendarEvents(
    request?: CalendarSyncRequest
): Promise<CalendarSyncResponse> {
    const response = await apiClient.post<ApiResponse<CalendarSyncResponse>>(
        '/v1/calendar/sync',
        request || {}
    );
    return response.data.data;
}

// ====================
// Calendar Event API
// ====================

/**
 * 캘린더 이벤트 목록 조회
 *
 * @param params - 쿼리 파라미터 (옵션)
 * @returns 이벤트 목록 및 통계
 */
export async function listCalendarEvents(
    params?: CalendarEventListParams
): Promise<CalendarEventListResponse> {
    const response = await apiClient.get<ApiResponse<CalendarEventListResponse>>(
        '/v1/calendar/events',
        { params }
    );
    return response.data.data;
}

/**
 * 캘린더 이벤트 단건 조회
 *
 * @param eventId - 이벤트 ID
 * @returns 이벤트 상세 정보
 */
export async function getCalendarEvent(eventId: number): Promise<CalendarEvent> {
    const response = await apiClient.get<ApiResponse<CalendarEvent>>(
        `/v1/calendar/events/${eventId}`
    );
    return response.data.data;
}

// ====================
// Event Selection API
// ====================

/**
 * 캘린더 이벤트 선택
 *
 * @param data - 선택할 이벤트 ID 목록
 * @returns 선택 결과
 */
export async function selectCalendarEvents(
    data: EventSelectionRequest
): Promise<EventSelectionResponse> {
    const response = await apiClient.post<ApiResponse<EventSelectionResponse>>(
        '/v1/calendar/events/select',
        data
    );
    return response.data.data;
}

/**
 * 캘린더 이벤트 선택 해제
 *
 * @param data - 선택 해제할 이벤트 ID 목록
 * @returns 선택 해제 결과
 */
export async function deselectCalendarEvents(
    data: EventSelectionRequest
): Promise<EventSelectionResponse> {
    const response = await apiClient.post<ApiResponse<EventSelectionResponse>>(
        '/v1/calendar/events/deselect',
        data
    );
    return response.data.data;
}

/**
 * 모든 이벤트 선택
 *
 * @param eventIds - 선택할 모든 이벤트 ID 목록
 * @returns 선택 결과
 */
export async function selectAllEvents(
    eventIds: number[]
): Promise<EventSelectionResponse> {
    return selectCalendarEvents({ event_ids: eventIds });
}

/**
 * 모든 이벤트 선택 해제
 *
 * @param eventIds - 선택 해제할 모든 이벤트 ID 목록
 * @returns 선택 해제 결과
 */
export async function deselectAllEvents(
    eventIds: number[]
): Promise<EventSelectionResponse> {
    return deselectCalendarEvents({ event_ids: eventIds });
}
