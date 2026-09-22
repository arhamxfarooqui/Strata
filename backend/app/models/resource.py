"""
Resource model — curated learning materials scoped to wings.
"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    title: Mapped[str] = mapped_column(String(500), nullable=True, default="")
    description: Mapped[str] = mapped_column(String(2000), nullable=True, default="")
    link: Mapped[str] = mapped_column(String(1000), nullable=True, default="")
    type: Mapped[str] = mapped_column(String(50), nullable=True, default="")
    year: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    subject: Mapped[str] = mapped_column(String(255), nullable=True, default="")

    wing_id: Mapped[str] = mapped_column(String(50), nullable=True, default="", index=True)
    submitted_by_id: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    upvotes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    difficulty_level: Mapped[str] = mapped_column(String(50), nullable=True, default="")

    def to_dict(self) -> dict:
        return {
            "ID": self.id,
            "CreatedAt": self.created_at.isoformat() if self.created_at else None,
            "UpdatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "title": self.title or "",
            "description": self.description or "",
            "link": self.link or "",
            "type": self.type or "",
            "year": self.year or 0,
            "subject": self.subject or "",
            "wing_id": self.wing_id or "",
            "submitted_by_id": self.submitted_by_id or 0,
            "upvotes": self.upvotes,
            "difficulty_level": self.difficulty_level or "",
        }
