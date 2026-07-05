from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    student_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    users = relationship("User", back_populates="section")

    def __repr__(self) -> str:
        return f"<Section {self.name} (students={self.student_count})>"
