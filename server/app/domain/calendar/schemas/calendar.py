"""
캘린더 관련 스키마

구글 캘린더 연동 및 이벤트 관리를 위한 요청/응답 스키마를 정의합니다.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ====================
# Calendar Connection Schemas
# ====================

class CalendarConnectionCreate(BaseModel):
    """캘린더 연동 생성 요청"""

    authorization_code: str = Field(..., description="구글 OAuth 인증 코드")
    redirect_uri: str = Field(..., description="리다이렉트 URI")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "authorization_code": "4/0AY0e-g7...",
                "redirect_uri": "http://localhost:3000/calendar/callback"
            }
        }
    )


class CalendarConnectionResponse(BaseModel):
    """캘린더 연동 정보 응답"""

    id: int
    user_id: int
    google_calendar_id: str
    is_active: bool
    webhook_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "google_calendar_id": "primary",
                "is_active": True,
                "webhook_expires_at": "2026-01-23T10:00:00Z",
                "created_at": "2026-01-16T10:00:00Z",
                "updated_at": "2026-01-16T10:00:00Z"
            }
        }
    )


# ====================
# Calendar Event Schemas
# ====================

class CalendarEventResponse(BaseModel):
    """캘린더 이벤트 응답"""

    id: int
    google_event_id: str
    summary: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees_count: int
    attendees_emails: List[str]
    is_filtered: bool
    is_selected: bool
    synced_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "google_event_id": "abc123def456",
                "summary": "1on1 미팅 with John",
                "description": "주간 1:1 미팅",
                "start_time": "2026-01-20T14:00:00Z",
                "end_time": "2026-01-20T15:00:00Z",
                "location": "회의실 A",
                "attendees_count": 2,
                "attendees_emails": ["user@example.com", "john@example.com"],
                "is_filtered": True,
                "is_selected": False,
                "synced_at": "2026-01-16T10:00:00Z"
            }
        }
    )


class CalendarEventListResponse(BaseModel):
    """캘린더 이벤트 목록 응답"""

    events: List[CalendarEventResponse]
    total: int
    filtered_count: int
    selected_count: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "events": [],
                "total": 10,
                "filtered_count": 5,
                "selected_count": 2
            }
        }
    )


# ====================
# Calendar Sync Schemas
# ====================

class CalendarSyncRequest(BaseModel):
    """캘린더 동기화 요청"""

    time_min: Optional[datetime] = Field(None, description="조회 시작 시간 (기본: 현재 시각)")
    time_max: Optional[datetime] = Field(None, description="조회 종료 시간 (기본: 3개월 후)")
    max_results: int = Field(default=100, description="최대 조회 개수", ge=1, le=500)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "time_min": "2026-01-16T00:00:00Z",
                "time_max": "2026-04-16T23:59:59Z",
                "max_results": 100
            }
        }
    )


class CalendarSyncResponse(BaseModel):
    """캘린더 동기화 응답"""

    synced_count: int = Field(..., description="동기화된 이벤트 수")
    filtered_count: int = Field(..., description="필터링된 이벤트 수")
    new_count: int = Field(..., description="새로 추가된 이벤트 수")
    updated_count: int = Field(..., description="업데이트된 이벤트 수")
    deleted_count: int = Field(..., description="삭제된 이벤트 수")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "synced_count": 10,
                "filtered_count": 5,
                "new_count": 3,
                "updated_count": 2,
                "deleted_count": 0
            }
        }
    )


# ====================
# Event Selection Schemas
# ====================

class EventSelectionRequest(BaseModel):
    """이벤트 선택 요청"""

    event_ids: List[int] = Field(..., description="선택할 이벤트 ID 목록")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_ids": [1, 2, 3]
            }
        }
    )


class EventSelectionResponse(BaseModel):
    """이벤트 선택 응답"""

    selected_count: int = Field(..., description="선택된 이벤트 수")
    event_ids: List[int] = Field(..., description="선택된 이벤트 ID 목록")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "selected_count": 3,
                "event_ids": [1, 2, 3]
            }
        }
    )
