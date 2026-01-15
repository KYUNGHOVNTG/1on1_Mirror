from datetime import datetime
from typing import Optional

from sqlalchemy import String, ForeignKey, Text, DateTime, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.core.database import Base

class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    criteria: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending") # pending, in_progress, completed, failed
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="goals")


class OneOnOneSession(Base):
    __tablename__ = "one_on_one_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="scheduled") # scheduled, completed, cancelled
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    report_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON or Text content
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    # Note: Explicit join conditions might be needed in queries if multiple FKs point to same table
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    manager: Mapped["User"] = relationship("User", foreign_keys=[manager_id])
    company: Mapped["Company"] = relationship("Company")
