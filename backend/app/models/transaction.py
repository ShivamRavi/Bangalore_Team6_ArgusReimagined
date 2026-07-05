import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def generate_uuid():
    return uuid.uuid4()

class CurrencyType(str, Enum):
    EUROS = "euros"
    HOUSE_POINTS = "house_points"

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=generate_uuid
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    currency_type: Mapped[CurrencyType] = mapped_column(SQLEnum(CurrencyType), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="transactions")
    activity_completion = relationship(
        "ActivityCompletion",
        back_populates="transaction",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<Transaction {self.id} (user_id={self.user_id}, type={self.currency_type}, amount={self.amount})>"
