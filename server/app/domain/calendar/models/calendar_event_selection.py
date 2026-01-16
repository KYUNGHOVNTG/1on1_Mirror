"""
캘린더 이벤트 선택 모델

사용자가 선택한 캘린더 이벤트와 1:1 세션의 연결을 관리합니다.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.core.database import Base

if TYPE_CHECKING:
    from server.app.domain.calendar.models.calendar_event import CalendarEvent


class CalendarEventSelection(Base):
    """
    캘린더 이벤트 선택

    사용자가 선택한 이벤트와 1:1 세션을 연결합니다.
    """
    __tablename__ = "calendar_event_selections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    calendar_event_id: Mapped[int] = mapped_column(
        ForeignKey("calendar_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True
    )
    one_on_one_session_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("one_on_one_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Timestamps
    selected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    event: Mapped["CalendarEvent"] = relationship("CalendarEvent", back_populates="selection")
