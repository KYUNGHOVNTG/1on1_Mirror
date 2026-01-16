from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, ForeignKey, Integer, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.core.database import Base

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="departments")
    parent: Mapped[Optional["Department"]] = relationship("Department", remote_side=[id], back_populates="children")
    children: Mapped[List["Department"]] = relationship("Department", back_populates="parent")
    users: Mapped[List["User"]] = relationship("User", back_populates="department")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    google_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="member") # admin, manager, member
    profile_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # OAuth Token fields
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="users")
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="users")
    goals: Mapped[List["Goal"]] = relationship("Goal", back_populates="user")
    calendar_connections: Mapped[List["CalendarConnection"]] = relationship(
        "CalendarConnection",
        back_populates="user",
        cascade="all, delete-orphan"
    )
