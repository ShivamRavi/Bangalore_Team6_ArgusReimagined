from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class House(Base):
    __tablename__ = "houses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)

    # Relationships
    users = relationship("User", back_populates="house")

    def __repr__(self) -> str:
        return f"<House {self.name} (points={self.total_points})>"
