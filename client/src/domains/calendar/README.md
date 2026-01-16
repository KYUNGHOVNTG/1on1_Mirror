# Calendar Domain

구글 캘린더 연동 및 이벤트 관리 기능을 제공하는 도메인입니다.

## 📁 구조

```
calendar/
├── types.ts        # TypeScript 타입 정의
├── api.ts          # API 호출 함수
├── store.ts        # Zustand 상태 관리
├── index.ts        # 공개 API Export
└── README.md       # 문서 (현재 파일)
```

## 🚀 사용법

### 1. 캘린더 스토어 사용

```tsx
import { useCalendarStore } from '@/domains/calendar';

function CalendarPage() {
  const {
    connection,
    events,
    loading,
    error,
    connectCalendar,
    syncEvents,
    fetchEvents,
    selectEvents,
  } = useCalendarStore();

  // 캘린더 연동 상태 확인
  useEffect(() => {
    fetchConnection();
  }, [fetchConnection]);

  // 이벤트 목록 조회
  useEffect(() => {
    if (connection) {
      fetchEvents();
    }
  }, [connection, fetchEvents]);

  return (
    <div>
      {/* UI 구현 */}
    </div>
  );
}
```

### 2. API 직접 호출

```tsx
import * as calendarApi from '@/domains/calendar';

// 캘린더 연동
const connection = await calendarApi.connectCalendar({
  authorization_code: 'code',
  redirect_uri: 'http://localhost:3000/callback',
});

// 이벤트 동기화
const syncResult = await calendarApi.syncCalendarEvents({
  time_min: '2026-01-01T00:00:00Z',
  time_max: '2026-04-01T00:00:00Z',
  max_results: 100,
});

// 이벤트 목록 조회
const eventList = await calendarApi.listCalendarEvents({
  is_filtered: true,
});

// 이벤트 선택
await calendarApi.selectCalendarEvents({
  event_ids: [1, 2, 3],
});
```

## 📝 주요 기능

### 캘린더 연동

- ✅ 구글 캘린더 OAuth 인증 및 연동
- ✅ 연동 상태 조회
- ✅ 연동 해제

### 이벤트 동기화

- ✅ 구글 캘린더에서 이벤트 가져오기
- ✅ 기간별 이벤트 조회
- ✅ 자동 필터링 (1:1 미팅 감지)

### 이벤트 관리

- ✅ 이벤트 목록 조회 (필터링/선택 상태)
- ✅ 개별 이벤트 선택/해제
- ✅ 전체 선택/해제

## 🔄 상태 관리

### State

| 속성 | 타입 | 설명 |
|------|------|------|
| `connection` | `CalendarConnection \| null` | 캘린더 연동 정보 |
| `events` | `CalendarEvent[]` | 이벤트 목록 |
| `selectedEvents` | `CalendarEvent[]` | 선택된 이벤트 목록 |
| `totalCount` | `number` | 총 이벤트 수 |
| `filteredCount` | `number` | 필터링된 이벤트 수 |
| `selectedCount` | `number` | 선택된 이벤트 수 |
| `lastSyncResult` | `CalendarSyncResponse \| null` | 마지막 동기화 결과 |
| `loading` | `boolean` | 로딩 상태 |
| `error` | `string \| null` | 에러 메시지 |

### Actions

#### 연동 관리
- `connectCalendar(authorizationCode, redirectUri)` - 캘린더 연동
- `fetchConnection()` - 연동 상태 조회
- `disconnectCalendar()` - 연동 해제

#### 동기화
- `syncEvents(request?)` - 이벤트 동기화

#### 이벤트 조회
- `fetchEvents(params?)` - 이벤트 목록 조회
- `fetchFilteredEvents()` - 필터링된 이벤트만 조회
- `fetchSelectedEvents()` - 선택된 이벤트만 조회

#### 이벤트 선택
- `selectEvents(eventIds)` - 이벤트 선택
- `deselectEvents(eventIds)` - 이벤트 선택 해제
- `selectAllFilteredEvents()` - 필터링된 모든 이벤트 선택
- `deselectAllEvents()` - 모든 선택 해제

#### 유틸리티
- `clearError()` - 에러 초기화
- `reset()` - 스토어 초기화

## 🔗 백엔드 API 엔드포인트

### 연동 관리
- `POST /api/v1/calendar/connect` - 캘린더 연동
- `GET /api/v1/calendar/connection` - 연동 상태 조회
- `DELETE /api/v1/calendar/connection` - 연동 해제

### 동기화
- `POST /api/v1/calendar/sync` - 이벤트 동기화

### 이벤트 조회
- `GET /api/v1/calendar/events` - 이벤트 목록
- `GET /api/v1/calendar/events/:id` - 이벤트 상세

### 이벤트 선택
- `POST /api/v1/calendar/events/select` - 이벤트 선택
- `POST /api/v1/calendar/events/deselect` - 이벤트 선택 해제

## ⚠️ 주의사항

1. **apiClient 사용 필수**: `axios`를 직접 import하지 마세요. 반드시 `@/core/api`의 `apiClient`를 사용하세요.

2. **타입 안전성**: 모든 API 호출은 TypeScript 타입이 명시되어 있습니다. `any` 타입 사용을 피하세요.

3. **에러 처리**: API 에러는 `apiClient`에서 자동으로 처리됩니다. 필요시 `try-catch`로 추가 처리하세요.

4. **자동 갱신**: 선택/해제 등의 변경 작업 후 스토어는 자동으로 이벤트 목록을 갱신합니다.

5. **로딩 관리**: `LoadingManager`가 자동으로 적용됩니다. 특정 요청만 로딩 표시를 비활성화하려면 API 레벨에서 `skipLoading` 옵션을 사용하세요.

## 📦 타입 정의

모든 타입은 백엔드 Pydantic 스키마와 1:1 매핑됩니다.

```typescript
// 캘린더 이벤트
interface CalendarEvent {
  id: number;
  google_event_id: string;
  summary: string;
  description: string | null;
  start_time: string;  // ISO 8601
  end_time: string;    // ISO 8601
  location: string | null;
  attendees_count: number;
  attendees_emails: string[];
  is_filtered: boolean;  // 1:1 미팅 여부
  is_selected: boolean;  // 사용자 선택 여부
  synced_at: string;     // ISO 8601
}
```

자세한 타입 정의는 `types.ts`를 참고하세요.
