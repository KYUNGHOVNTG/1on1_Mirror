/**
 * Calendar Domain Exports
 *
 * 캘린더 도메인의 모든 공개 API를 내보냅니다.
 */

// Types
export type {
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

// API Functions
export {
    connectCalendar,
    getCalendarConnection,
    disconnectCalendar,
    syncCalendarEvents,
    listCalendarEvents,
    getCalendarEvent,
    selectCalendarEvents,
    deselectCalendarEvents,
    selectAllEvents,
    deselectAllEvents,
} from './api';

// Store
export { useCalendarStore } from './store';
