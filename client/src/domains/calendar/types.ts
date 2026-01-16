/**
 * Calendar Domain Types
 *
 * 캘린더 도메인에서 사용하는 타입 정의
 * 백엔드 스키마와 1:1 매핑됩니다.
 */

// ====================
// Calendar Connection Types
// ====================

/**
 * 캘린더 연동 생성 요청
 */
export interface CalendarConnectionCreate {
  /** 구글 OAuth 인증 코드 */
  authorization_code: string;
  /** 리다이렉트 URI */
  redirect_uri: string;
}

/**
 * 캘린더 연동 정보
 */
export interface CalendarConnection {
  id: number;
  user_id: number;
  google_calendar_id: string;
  is_active: boolean;
  webhook_expires_at: string | null;
  created_at: string;
  updated_at: string;
}

// ====================
// Calendar Event Types
// ====================

/**
 * 캘린더 이벤트
 */
export interface CalendarEvent {
  id: number;
  google_event_id: string;
  summary: string;
  description: string | null;
  start_time: string;
  end_time: string;
  location: string | null;
  attendees_count: number;
  attendees_emails: string[];
  is_filtered: boolean;
  is_selected: boolean;
  synced_at: string;
}

/**
 * 캘린더 이벤트 목록 응답
 */
export interface CalendarEventListResponse {
  events: CalendarEvent[];
  total: number;
  filtered_count: number;
  selected_count: number;
}

// ====================
// Calendar Sync Types
// ====================

/**
 * 캘린더 동기화 요청
 */
export interface CalendarSyncRequest {
  /** 조회 시작 시간 (ISO 8601 형식) */
  time_min?: string;
  /** 조회 종료 시간 (ISO 8601 형식) */
  time_max?: string;
  /** 최대 조회 개수 (1-500) */
  max_results?: number;
}

/**
 * 캘린더 동기화 응답
 */
export interface CalendarSyncResponse {
  /** 동기화된 이벤트 수 */
  synced_count: number;
  /** 필터링된 이벤트 수 */
  filtered_count: number;
  /** 새로 추가된 이벤트 수 */
  new_count: number;
  /** 업데이트된 이벤트 수 */
  updated_count: number;
  /** 삭제된 이벤트 수 */
  deleted_count: number;
}

// ====================
// Event Selection Types
// ====================

/**
 * 이벤트 선택/해제 요청
 */
export interface EventSelectionRequest {
  /** 선택/해제할 이벤트 ID 목록 */
  event_ids: number[];
}

/**
 * 이벤트 선택/해제 응답
 */
export interface EventSelectionResponse {
  /** 선택/해제된 이벤트 수 */
  selected_count: number;
  /** 선택/해제된 이벤트 ID 목록 */
  event_ids: number[];
}

// ====================
// Query Parameter Types
// ====================

/**
 * 이벤트 목록 조회 쿼리 파라미터
 */
export interface CalendarEventListParams {
  /** 필터링 여부 */
  is_filtered?: boolean;
  /** 선택 여부 */
  is_selected?: boolean;
}
