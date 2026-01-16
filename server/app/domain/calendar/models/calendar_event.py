"""
캘린더 이벤트 모델

구글 캘린더에서 동기화된 이벤트 정보를 관리합니다.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Integer, DateTime, Text, Boolean, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.core.database import Base

if TYPE_CHECKING:
    from server.app.domain.calendar.models.calendar_connection import CalendarConnection
    from server.app.domain.calendar.models.calendar_event_selection import CalendarEventSelection


class CalendarEvent(Base):
    """
    캘린더 이벤트

    구글 캘린더에서 동기화된 이벤트 정보를 저장합니다.
    """
    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    calendar_connection_id: Mapped[int] = mapped_column(
        ForeignKey("calendar_connections.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    google_event_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Event Details
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Attendees
    attendees_count: Mapped[int] = mapped_column(Integer, default=0)
    attendees_emails: Mapped[dict] = mapped_column(JSON, default=list)

    # Filtering & Selection
    is_filtered: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Timestamps
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    connection: Mapped["CalendarConnection"] = relationship("CalendarConnection", back_populates="events")
    selection: Mapped[Optional["CalendarEventSelection"]] = relationship(
        "CalendarEventSelection",
        back_populates="event",
        uselist=False,
        cascade="all, delete-orphan"
    )
