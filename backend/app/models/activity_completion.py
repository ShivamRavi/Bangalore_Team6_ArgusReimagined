import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import ActivityType
from app.database import Base


def generate_uuid() -> uuid.UUID:
    return uuid.uuid4()


class ActivityCompletion(Base):
    """Tracks completed activities to prevent duplicate Euro payouts."""

    __tablename__ = "activity_completions"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "resource_id",
            "activity_type",
            name="uq_activity_completion_user_resource_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    activity_type: Mapped[ActivityType] = mapped_column(
        SQLEnum(ActivityType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    euros_awarded: Mapped[int] = mapped_column(Integer, nullable=False)
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transactions.id", ondelete="SET NULL"),
        nullable=True,
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    user = relationship("User", back_populates="activity_completions")
    transaction = relationship("Transaction", back_populates="activity_completion")

    def __repr__(self) -> str:
        return (
            f"<ActivityCompletion user={self.user_id} "
            f"resource={self.resource_id} type={self.activity_type.value}>"
        )
