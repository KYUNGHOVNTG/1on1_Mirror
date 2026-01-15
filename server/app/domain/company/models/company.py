from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.core.database import Base

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    business_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    domain: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="company", cascade="all, delete-orphan")
    departments: Mapped[List["Department"]] = relationship("Department", back_populates="company", cascade="all, delete-orphan")
