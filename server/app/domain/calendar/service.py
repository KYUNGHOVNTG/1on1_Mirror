"""
캘린더 서비스

캘린더 연동 및 이벤트 동기화의 비즈니스 로직을 담당합니다.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.config import settings
from server.app.core.logging import get_logger
from server.app.domain.calendar.models.calendar_connection import CalendarConnection
from server.app.domain.calendar.models.calendar_event import CalendarEvent
from server.app.domain.calendar.repositories.calendar_repository import (
    CalendarConnectionRepository,
    CalendarEventRepository,
)
from server.app.domain.calendar.calculators.event_filter_calculator import (
    EventFilterCalculator,
)
from server.app.domain.calendar.formatters.calendar_formatter import (
    CalendarEventFormatter,
)
from server.app.domain.calendar.utils.google_calendar_client import (
    GoogleCalendarClient,
)
from server.app.domain.calendar.schemas.calendar import (
    CalendarConnectionResponse,
    CalendarEventListResponse,
    CalendarSyncResponse,
    EventSelectionResponse,
)

logger = get_logger(__name__)


class CalendarService:
    """
    캘린더 서비스

    캘린더 연동, 이벤트 동기화, 이벤트 선택 등의 비즈니스 로직을 제공합니다.
    """

    def __init__(self, db: AsyncSession):
        """
        Args:
            db: 데이터베이스 세션
        """
        self.db = db
        self.connection_repo = CalendarConnectionRepository(db)
        self.event_repo = CalendarEventRepository(db)
        self.filter_calculator = EventFilterCalculator()
        self.formatter = CalendarEventFormatter()

    async def create_connection(
        self,
        user_id: int,
        authorization_code: str,
        redirect_uri: str,
    ) -> CalendarConnectionResponse:
        """
        캘린더 연동 생성

        Args:
            user_id: 사용자 ID
            authorization_code: 구글 OAuth 인증 코드
            redirect_uri: 리다이렉트 URI

        Returns:
            CalendarConnectionResponse: 생성된 캘린더 연동 정보
        """
        logger.info(f"Creating calendar connection for user: {user_id}")

        # OAuth 토큰 교환
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=GoogleCalendarClient.SCOPES,
            redirect_uri=redirect_uri,
        )

        flow.fetch_token(code=authorization_code)
        credentials = flow.credentials

        # 기존 연동 확인
        existing_connection = await self.connection_repo.find_by_user_id(
            user_id=user_id,
            calendar_id="primary",
        )

        token_expires_at = datetime.utcnow() + timedelta(
            seconds=credentials.expiry.timestamp() - datetime.utcnow().timestamp()
        )

        if existing_connection:
            # 기존 연동 업데이트
            existing_connection.access_token = credentials.token
            existing_connection.refresh_token = credentials.refresh_token
            existing_connection.token_expires_at = token_expires_at
            existing_connection.is_active = True

            connection = await self.connection_repo.update(existing_connection)
        else:
            # 새로운 연동 생성
            connection = CalendarConnection(
                user_id=user_id,
                google_calendar_id="primary",
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_expires_at=token_expires_at,
                is_active=True,
            )
            connection = await self.connection_repo.create(connection)

        await self.db.commit()

        logger.info(f"Calendar connection created: {connection.id}")
        return self.formatter.format_connection(connection)

    async def sync_events(
        self,
        user_id: int,
        time_min: datetime | None = None,
        time_max: datetime | None = None,
        max_results: int = 100,
    ) -> CalendarSyncResponse:
        """
        캘린더 이벤트 동기화

        Args:
            user_id: 사용자 ID
            time_min: 조회 시작 시간
            time_max: 조회 종료 시간
            max_results: 최대 조회 개수

        Returns:
            CalendarSyncResponse: 동기화 결과
        """
        logger.info(f"Syncing calendar events for user: {user_id}")

        # 캘린더 연동 조회
        connection = await self.connection_repo.find_by_user_id(
            user_id=user_id,
            calendar_id="primary",
        )

        if not connection or not connection.is_active:
            raise ValueError("No active calendar connection found")

        # 토큰 갱신 (필요시)
        await self._refresh_token_if_needed(connection)

        # 구글 캘린더 API 클라이언트 생성
        client = GoogleCalendarClient(
            access_token=connection.access_token,
            refresh_token=connection.refresh_token,
            token_expires_at=connection.token_expires_at,
        )

        # 이벤트 조회
        google_events = client.list_events(
            calendar_id="primary",
            time_min=time_min,
            time_max=time_max,
            max_results=max_results,
        )

        # 이벤트 동기화
        synced_count = 0
        new_count = 0
        updated_count = 0
        filtered_count = 0

        for google_event in google_events:
            google_event_id = google_event.get("id")
            summary = google_event.get("summary", "")
            description = google_event.get("description", "")

            # 시작/종료 시간 파싱
            start_time = GoogleCalendarClient.parse_event_datetime(
                google_event.get("start", {})
            )
            end_time = GoogleCalendarClient.parse_event_datetime(
                google_event.get("end", {})
            )

            # 참석자 정보 추출
            attendees_count, attendees_emails = GoogleCalendarClient.extract_attendees(
                google_event
            )

            # 필터링 여부 판단
            is_filtered = self.filter_calculator.is_one_on_one_event(
                summary=summary,
                description=description,
                attendees_count=attendees_count,
            )

            if is_filtered:
                filtered_count += 1

            # 기존 이벤트 확인
            existing_event = await self.event_repo.find_by_google_event_id(
                connection_id=connection.id,
                google_event_id=google_event_id,
            )

            if existing_event:
                # 기존 이벤트 업데이트
                existing_event.summary = summary
                existing_event.description = description
                existing_event.start_time = start_time
                existing_event.end_time = end_time
                existing_event.location = google_event.get("location")
                existing_event.attendees_count = attendees_count
                existing_event.attendees_emails = attendees_emails
                existing_event.is_filtered = is_filtered

                await self.event_repo.update(existing_event)
                updated_count += 1
            else:
                # 새 이벤트 생성
                event = CalendarEvent(
                    calendar_connection_id=connection.id,
                    google_event_id=google_event_id,
                    summary=summary,
                    description=description,
                    start_time=start_time,
                    end_time=end_time,
                    location=google_event.get("location"),
                    attendees_count=attendees_count,
                    attendees_emails=attendees_emails,
                    is_filtered=is_filtered,
                    is_selected=False,
                )
                await self.event_repo.create(event)
                new_count += 1

            synced_count += 1

        await self.db.commit()

        logger.info(
            f"Calendar sync completed: synced={synced_count}, new={new_count}, "
            f"updated={updated_count}, filtered={filtered_count}"
        )

        return CalendarSyncResponse(
            synced_count=synced_count,
            filtered_count=filtered_count,
            new_count=new_count,
            updated_count=updated_count,
            deleted_count=0,
        )

    async def list_events(
        self,
        user_id: int,
        is_filtered: bool | None = None,
        is_selected: bool | None = None,
    ) -> CalendarEventListResponse:
        """
        캘린더 이벤트 목록 조회

        Args:
            user_id: 사용자 ID
            is_filtered: 필터링 여부
            is_selected: 선택 여부

        Returns:
            CalendarEventListResponse: 이벤트 목록
        """
        logger.info(f"Listing calendar events for user: {user_id}")

        # 캘린더 연동 조회
        connection = await self.connection_repo.find_by_user_id(
            user_id=user_id,
            calendar_id="primary",
        )

        if not connection:
            raise ValueError("No calendar connection found")

        # 이벤트 조회
        events = await self.event_repo.find_by_connection_id(
            connection_id=connection.id,
            is_filtered=is_filtered,
            is_selected=is_selected,
        )

        # 통계 계산
        total = await self.event_repo.count_by_connection_id(connection.id)
        filtered_count = await self.event_repo.count_by_connection_id(
            connection.id, is_filtered=True
        )
        selected_count = await self.event_repo.count_by_connection_id(
            connection.id, is_selected=True
        )

        return CalendarEventListResponse(
            events=self.formatter.format_events(events),
            total=total,
            filtered_count=filtered_count,
            selected_count=selected_count,
        )

    async def select_events(
        self,
        user_id: int,
        event_ids: List[int],
    ) -> EventSelectionResponse:
        """
        캘린더 이벤트 선택

        Args:
            user_id: 사용자 ID
            event_ids: 선택할 이벤트 ID 목록

        Returns:
            EventSelectionResponse: 선택 결과
        """
        logger.info(f"Selecting calendar events for user: {user_id}")

        # 이벤트 선택 상태 업데이트
        await self.event_repo.update_selection_status(
            event_ids=event_ids,
            is_selected=True,
        )

        await self.db.commit()

        logger.info(f"Selected {len(event_ids)} events")

        return EventSelectionResponse(
            selected_count=len(event_ids),
            event_ids=event_ids,
        )

    async def deselect_events(
        self,
        user_id: int,
        event_ids: List[int],
    ) -> EventSelectionResponse:
        """
        캘린더 이벤트 선택 해제

        Args:
            user_id: 사용자 ID
            event_ids: 선택 해제할 이벤트 ID 목록

        Returns:
            EventSelectionResponse: 선택 해제 결과
        """
        logger.info(f"Deselecting calendar events for user: {user_id}")

        # 이벤트 선택 상태 업데이트
        await self.event_repo.update_selection_status(
            event_ids=event_ids,
            is_selected=False,
        )

        await self.db.commit()

        logger.info(f"Deselected {len(event_ids)} events")

        return EventSelectionResponse(
            selected_count=0,
            event_ids=event_ids,
        )

    async def _refresh_token_if_needed(
        self,
        connection: CalendarConnection,
    ) -> None:
        """
        필요시 토큰 갱신

        Args:
            connection: 캘린더 연동 정보
        """
        # 토큰이 만료되었거나 10분 이내에 만료될 경우 갱신
        if connection.token_expires_at < datetime.utcnow() + timedelta(minutes=10):
            logger.info(f"Refreshing token for connection: {connection.id}")

            credentials = Credentials(
                token=connection.access_token,
                refresh_token=connection.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
            )

            credentials.refresh(Request())

            # 토큰 업데이트
            connection.access_token = credentials.token
            if credentials.refresh_token:
                connection.refresh_token = credentials.refresh_token
            connection.token_expires_at = datetime.utcnow() + timedelta(
                seconds=credentials.expiry.timestamp() - datetime.utcnow().timestamp()
            )

            await self.connection_repo.update(connection)
            await self.db.commit()

            logger.info(f"Token refreshed for connection: {connection.id}")
