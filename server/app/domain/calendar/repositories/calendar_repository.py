"""
캘린더 레포지토리

캘린더 데이터 조회 및 관리를 담당합니다.
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, and_, or_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.domain.calendar.models.calendar_connection import CalendarConnection
from server.app.domain.calendar.models.calendar_event import CalendarEvent
from server.app.domain.calendar.models.calendar_event_selection import (
    CalendarEventSelection,
)
from server.app.core.logging import get_logger

logger = get_logger(__name__)


class CalendarConnectionRepository:
    """
    캘린더 연동 레포지토리

    캘린더 연동 정보를 조회하고 관리합니다.
    """

    def __init__(self, db: AsyncSession):
        """
        Args:
            db: 데이터베이스 세션
        """
        self.db = db

    async def find_by_user_id(
        self,
        user_id: int,
        calendar_id: str = "primary",
    ) -> Optional[CalendarConnection]:
        """
        사용자 ID와 캘린더 ID로 연동 정보 조회

        Args:
            user_id: 사용자 ID
            calendar_id: 구글 캘린더 ID

        Returns:
            Optional[CalendarConnection]: 캘린더 연동 정보
        """
        result = await self.db.execute(
            select(CalendarConnection).where(
                and_(
                    CalendarConnection.user_id == user_id,
                    CalendarConnection.google_calendar_id == calendar_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def find_active_by_user_id(
        self,
        user_id: int,
    ) -> List[CalendarConnection]:
        """
        사용자의 활성 캘린더 연동 목록 조회

        Args:
            user_id: 사용자 ID

        Returns:
            List[CalendarConnection]: 활성 캘린더 연동 목록
        """
        result = await self.db.execute(
            select(CalendarConnection).where(
                and_(
                    CalendarConnection.user_id == user_id,
                    CalendarConnection.is_active == True,
                )
            )
        )
        return list(result.scalars().all())

    async def create(
        self,
        connection: CalendarConnection,
    ) -> CalendarConnection:
        """
        캘린더 연동 생성

        Args:
            connection: 캘린더 연동 정보

        Returns:
            CalendarConnection: 생성된 캘린더 연동 정보
        """
        self.db.add(connection)
        await self.db.flush()
        await self.db.refresh(connection)
        return connection

    async def update(
        self,
        connection: CalendarConnection,
    ) -> CalendarConnection:
        """
        캘린더 연동 업데이트

        Args:
            connection: 캘린더 연동 정보

        Returns:
            CalendarConnection: 업데이트된 캘린더 연동 정보
        """
        connection.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(connection)
        return connection

    async def deactivate(
        self,
        connection_id: int,
    ) -> None:
        """
        캘린더 연동 비활성화

        Args:
            connection_id: 캘린더 연동 ID
        """
        await self.db.execute(
            update(CalendarConnection)
            .where(CalendarConnection.id == connection_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )


class CalendarEventRepository:
    """
    캘린더 이벤트 레포지토리

    캘린더 이벤트를 조회하고 관리합니다.
    """

    def __init__(self, db: AsyncSession):
        """
        Args:
            db: 데이터베이스 세션
        """
        self.db = db

    async def find_by_connection_id(
        self,
        connection_id: int,
        is_filtered: Optional[bool] = None,
        is_selected: Optional[bool] = None,
    ) -> List[CalendarEvent]:
        """
        캘린더 연동 ID로 이벤트 목록 조회

        Args:
            connection_id: 캘린더 연동 ID
            is_filtered: 필터링 여부 (None이면 전체)
            is_selected: 선택 여부 (None이면 전체)

        Returns:
            List[CalendarEvent]: 이벤트 목록
        """
        conditions = [CalendarEvent.calendar_connection_id == connection_id]

        if is_filtered is not None:
            conditions.append(CalendarEvent.is_filtered == is_filtered)
        if is_selected is not None:
            conditions.append(CalendarEvent.is_selected == is_selected)

        result = await self.db.execute(
            select(CalendarEvent)
            .where(and_(*conditions))
            .order_by(CalendarEvent.start_time.desc())
        )
        return list(result.scalars().all())

    async def find_by_google_event_id(
        self,
        connection_id: int,
        google_event_id: str,
    ) -> Optional[CalendarEvent]:
        """
        구글 이벤트 ID로 이벤트 조회

        Args:
            connection_id: 캘린더 연동 ID
            google_event_id: 구글 이벤트 ID

        Returns:
            Optional[CalendarEvent]: 이벤트
        """
        result = await self.db.execute(
            select(CalendarEvent).where(
                and_(
                    CalendarEvent.calendar_connection_id == connection_id,
                    CalendarEvent.google_event_id == google_event_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        event: CalendarEvent,
    ) -> CalendarEvent:
        """
        이벤트 생성

        Args:
            event: 이벤트 정보

        Returns:
            CalendarEvent: 생성된 이벤트 정보
        """
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def update(
        self,
        event: CalendarEvent,
    ) -> CalendarEvent:
        """
        이벤트 업데이트

        Args:
            event: 이벤트 정보

        Returns:
            CalendarEvent: 업데이트된 이벤트 정보
        """
        event.updated_at = datetime.utcnow()
        event.synced_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def update_selection_status(
        self,
        event_ids: List[int],
        is_selected: bool,
    ) -> None:
        """
        이벤트 선택 상태 업데이트

        Args:
            event_ids: 이벤트 ID 목록
            is_selected: 선택 여부
        """
        await self.db.execute(
            update(CalendarEvent)
            .where(CalendarEvent.id.in_(event_ids))
            .values(is_selected=is_selected, updated_at=datetime.utcnow())
        )

    async def delete_by_google_event_ids(
        self,
        connection_id: int,
        google_event_ids: List[str],
    ) -> None:
        """
        구글 이벤트 ID 목록으로 이벤트 삭제

        Args:
            connection_id: 캘린더 연동 ID
            google_event_ids: 구글 이벤트 ID 목록
        """
        await self.db.execute(
            delete(CalendarEvent).where(
                and_(
                    CalendarEvent.calendar_connection_id == connection_id,
                    CalendarEvent.google_event_id.in_(google_event_ids),
                )
            )
        )

    async def count_by_connection_id(
        self,
        connection_id: int,
        is_filtered: Optional[bool] = None,
        is_selected: Optional[bool] = None,
    ) -> int:
        """
        캘린더 연동 ID로 이벤트 개수 조회

        Args:
            connection_id: 캘린더 연동 ID
            is_filtered: 필터링 여부 (None이면 전체)
            is_selected: 선택 여부 (None이면 전체)

        Returns:
            int: 이벤트 개수
        """
        from sqlalchemy import func

        conditions = [CalendarEvent.calendar_connection_id == connection_id]

        if is_filtered is not None:
            conditions.append(CalendarEvent.is_filtered == is_filtered)
        if is_selected is not None:
            conditions.append(CalendarEvent.is_selected == is_selected)

        result = await self.db.execute(
            select(func.count(CalendarEvent.id)).where(and_(*conditions))
        )
        return result.scalar_one()
