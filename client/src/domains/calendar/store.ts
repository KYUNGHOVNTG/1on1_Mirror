/**
 * Calendar Domain Store
 *
 * 캘린더 도메인의 상태 관리 (Zustand)
 *
 * @example
 * const { connection, events, syncEvents, selectEvents } = useCalendarStore();
 */

import { create } from 'zustand';
import type {
    CalendarConnection,
    CalendarEvent,
    CalendarSyncRequest,
    CalendarSyncResponse,
    CalendarEventListParams,
} from './types';
import * as calendarApi from './api';

interface CalendarState {
    // ===== State =====
    /** 캘린더 연동 정보 */
    connection: CalendarConnection | null;
    /** 캘린더 이벤트 목록 */
    events: CalendarEvent[];
    /** 선택된 이벤트 목록 */
    selectedEvents: CalendarEvent[];
    /** 총 이벤트 수 */
    totalCount: number;
    /** 필터링된 이벤트 수 */
    filteredCount: number;
    /** 선택된 이벤트 수 */
    selectedCount: number;
    /** 마지막 동기화 결과 */
    lastSyncResult: CalendarSyncResponse | null;
    /** 로딩 상태 */
    loading: boolean;
    /** 에러 메시지 */
    error: string | null;

    // ===== Calendar Connection Actions =====
    /**
     * 캘린더 연동 생성
     * @param authorizationCode - OAuth 인증 코드
     * @param redirectUri - 리다이렉트 URI
     */
    connectCalendar: (authorizationCode: string, redirectUri: string) => Promise<void>;

    /**
     * 캘린더 연동 상태 조회
     */
    fetchConnection: () => Promise<void>;

    /**
     * 캘린더 연동 해제
     */
    disconnectCalendar: () => Promise<void>;

    // ===== Calendar Sync Actions =====
    /**
     * 캘린더 이벤트 동기화
     * @param request - 동기화 요청 (옵션)
     */
    syncEvents: (request?: CalendarSyncRequest) => Promise<void>;

    // ===== Calendar Event Actions =====
    /**
     * 캘린더 이벤트 목록 조회
     * @param params - 쿼리 파라미터 (옵션)
     */
    fetchEvents: (params?: CalendarEventListParams) => Promise<void>;

    /**
     * 필터링된 이벤트만 조회
     */
    fetchFilteredEvents: () => Promise<void>;

    /**
     * 선택된 이벤트만 조회
     */
    fetchSelectedEvents: () => Promise<void>;

    // ===== Event Selection Actions =====
    /**
     * 이벤트 선택
     * @param eventIds - 선택할 이벤트 ID 목록
     */
    selectEvents: (eventIds: number[]) => Promise<void>;

    /**
     * 이벤트 선택 해제
     * @param eventIds - 선택 해제할 이벤트 ID 목록
     */
    deselectEvents: (eventIds: number[]) => Promise<void>;

    /**
     * 모든 (필터링된) 이벤트 선택
     */
    selectAllFilteredEvents: () => Promise<void>;

    /**
     * 모든 선택 해제
     */
    deselectAllEvents: () => Promise<void>;

    // ===== Utility Actions =====
    /**
     * 에러 초기화
     */
    clearError: () => void;

    /**
     * 스토어 초기화
     */
    reset: () => void;
}

export const useCalendarStore = create<CalendarState>((set, get) => ({
    // ===== Initial State =====
    connection: null,
    events: [],
    selectedEvents: [],
    totalCount: 0,
    filteredCount: 0,
    selectedCount: 0,
    lastSyncResult: null,
    loading: false,
    error: null,

    // ===== Calendar Connection Actions =====
    connectCalendar: async (authorizationCode: string, redirectUri: string) => {
        set({ loading: true, error: null });
        try {
            const connection = await calendarApi.connectCalendar({
                authorization_code: authorizationCode,
                redirect_uri: redirectUri,
            });
            set({ connection, loading: false });
        } catch (error: any) {
            set({ error: error.message || '캘린더 연동에 실패했습니다.', loading: false });
            throw error;
        }
    },

    fetchConnection: async () => {
        set({ loading: true, error: null });
        try {
            const connection = await calendarApi.getCalendarConnection();
            set({ connection, loading: false });
        } catch (error: any) {
            set({ error: error.message || '캘린더 연동 정보를 가져오는데 실패했습니다.', loading: false });
            throw error;
        }
    },

    disconnectCalendar: async () => {
        set({ loading: true, error: null });
        try {
            await calendarApi.disconnectCalendar();
            set({
                connection: null,
                events: [],
                selectedEvents: [],
                totalCount: 0,
                filteredCount: 0,
                selectedCount: 0,
                lastSyncResult: null,
                loading: false,
            });
        } catch (error: any) {
            set({ error: error.message || '캘린더 연동 해제에 실패했습니다.', loading: false });
            throw error;
        }
    },

    // ===== Calendar Sync Actions =====
    syncEvents: async (request?: CalendarSyncRequest) => {
        set({ loading: true, error: null });
        try {
            const syncResult = await calendarApi.syncCalendarEvents(request);
            set({ lastSyncResult: syncResult, loading: false });

            // 동기화 후 이벤트 목록 자동 갱신
            await get().fetchEvents();
        } catch (error: any) {
            set({ error: error.message || '캘린더 동기화에 실패했습니다.', loading: false });
            throw error;
        }
    },

    // ===== Calendar Event Actions =====
    fetchEvents: async (params?: CalendarEventListParams) => {
        set({ loading: true, error: null });
        try {
            const response = await calendarApi.listCalendarEvents(params);
            set({
                events: response.events,
                totalCount: response.total,
                filteredCount: response.filtered_count,
                selectedCount: response.selected_count,
                selectedEvents: response.events.filter((e) => e.is_selected),
                loading: false,
            });
        } catch (error: any) {
            set({ error: error.message || '이벤트 목록을 가져오는데 실패했습니다.', loading: false });
            throw error;
        }
    },

    fetchFilteredEvents: async () => {
        await get().fetchEvents({ is_filtered: true });
    },

    fetchSelectedEvents: async () => {
        await get().fetchEvents({ is_selected: true });
    },

    // ===== Event Selection Actions =====
    selectEvents: async (eventIds: number[]) => {
        set({ loading: true, error: null });
        try {
            await calendarApi.selectCalendarEvents({ event_ids: eventIds });
            set({ loading: false });

            // 선택 후 이벤트 목록 자동 갱신
            await get().fetchEvents();
        } catch (error: any) {
            set({ error: error.message || '이벤트 선택에 실패했습니다.', loading: false });
            throw error;
        }
    },

    deselectEvents: async (eventIds: number[]) => {
        set({ loading: true, error: null });
        try {
            await calendarApi.deselectCalendarEvents({ event_ids: eventIds });
            set({ loading: false });

            // 선택 해제 후 이벤트 목록 자동 갱신
            await get().fetchEvents();
        } catch (error: any) {
            set({ error: error.message || '이벤트 선택 해제에 실패했습니다.', loading: false });
            throw error;
        }
    },

    selectAllFilteredEvents: async () => {
        const { events } = get();
        const filteredEventIds = events
            .filter((e) => e.is_filtered && !e.is_selected)
            .map((e) => e.id);

        if (filteredEventIds.length > 0) {
            await get().selectEvents(filteredEventIds);
        }
    },

    deselectAllEvents: async () => {
        const { selectedEvents } = get();
        const selectedEventIds = selectedEvents.map((e) => e.id);

        if (selectedEventIds.length > 0) {
            await get().deselectEvents(selectedEventIds);
        }
    },

    // ===== Utility Actions =====
    clearError: () => {
        set({ error: null });
    },

    reset: () => {
        set({
            connection: null,
            events: [],
            selectedEvents: [],
            totalCount: 0,
            filteredCount: 0,
            selectedCount: 0,
            lastSyncResult: null,
            loading: false,
            error: null,
        });
    },
}));
