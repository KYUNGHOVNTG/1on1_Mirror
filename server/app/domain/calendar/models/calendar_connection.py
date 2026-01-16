"""
캘린더 연동 모델

사용자별 구글 캘린더 연동 정보를 관리합니다.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Integer, DateTime, Text, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.core.database import Base

if TYPE_CHECKING:
    from server.app.domain.user.models.user import User
    from server.app.domain.calendar.models.calendar_event import CalendarEvent


class CalendarConnection(Base):
    """
    캘린더 연동 정보

    사용자별로 구글 캘린더 연동 정보와 OAuth 토큰을 관리합니다.
    """
    __tablename__ = "calendar_connections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    google_calendar_id: Mapped[str] = mapped_column(String(255), nullable=False, default="primary")

    # OAuth Tokens
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False)
    token_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Webhook (Push Notifications)
    channel_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    webhook_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="calendar_connections")
    events: Mapped[List["CalendarEvent"]] = relationship(
        "CalendarEvent",
        back_populates="connection",
        cascade="all, delete-orphan"
    )
