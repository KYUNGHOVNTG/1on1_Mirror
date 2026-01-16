"""
캘린더 포맷터

캘린더 데이터를 API 응답 형식으로 변환합니다.
"""

from typing import List

from server.app.domain.calendar.models.calendar_event import CalendarEvent
from server.app.domain.calendar.models.calendar_connection import CalendarConnection
from server.app.domain.calendar.schemas.calendar import (
    CalendarEventResponse,
    CalendarConnectionResponse,
)


class CalendarEventFormatter:
    """
    캘린더 이벤트 포맷터

    CalendarEvent 모델을 API 응답 스키마로 변환합니다.
    """

    @staticmethod
    def format_event(event: CalendarEvent) -> CalendarEventResponse:
        """
        이벤트를 응답 스키마로 변환

        Args:
            event: 이벤트 모델

        Returns:
            CalendarEventResponse: 이벤트 응답 스키마
        """
        return CalendarEventResponse(
            id=event.id,
            google_event_id=event.google_event_id,
            summary=event.summary,
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
            attendees_count=event.attendees_count,
            attendees_emails=event.attendees_emails or [],
            is_filtered=event.is_filtered,
            is_selected=event.is_selected,
            synced_at=event.synced_at,
        )

    @staticmethod
    def format_events(events: List[CalendarEvent]) -> List[CalendarEventResponse]:
        """
        이벤트 목록을 응답 스키마 목록으로 변환

        Args:
            events: 이벤트 모델 목록

        Returns:
            List[CalendarEventResponse]: 이벤트 응답 스키마 목록
        """
        return [CalendarEventFormatter.format_event(event) for event in events]

    @staticmethod
    def format_connection(
        connection: CalendarConnection,
    ) -> CalendarConnectionResponse:
        """
        캘린더 연동 정보를 응답 스키마로 변환

        Args:
            connection: 캘린더 연동 모델

        Returns:
            CalendarConnectionResponse: 캘린더 연동 응답 스키마
        """
        return CalendarConnectionResponse(
            id=connection.id,
            user_id=connection.user_id,
            google_calendar_id=connection.google_calendar_id,
            is_active=connection.is_active,
            webhook_expires_at=connection.webhook_expires_at,
            created_at=connection.created_at,
            updated_at=connection.updated_at,
        )
