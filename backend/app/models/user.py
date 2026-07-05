import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.database import Base

# Universal UUID generator helper that works with both SQLite and Postgres
def generate_uuid():
    return uuid.uuid4()

class User(Base):
    __tablename__ = "users"

    # Use UUID class which falls back to String/CHAR(32) on SQLite and UUID type on PostgreSQL
    # Using String(36) is highly compatible with SQLite.
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=generate_uuid
    )
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="STUDENT", nullable=False) # STUDENT, STAFF, PARENT
    
    house_id: Mapped[int | None] = mapped_column(ForeignKey("houses.id", ondelete="SET NULL"), nullable=True)
    section_id: Mapped[int | None] = mapped_column(ForeignKey("sections.id", ondelete="SET NULL"), nullable=True)
    
    euros_balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    lifetime_euros: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_planet: Mapped[str] = mapped_column(String(50), default="Mercury", nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    last_active_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    house = relationship("House", back_populates="users")
    section = relationship("Section", back_populates="users")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    activity_completions = relationship(
        "ActivityCompletion",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.username} (role={self.role}, euros={self.euros_balance})>"
