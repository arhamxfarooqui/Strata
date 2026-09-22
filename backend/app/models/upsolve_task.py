"""
UpsolveTask model — tracks failed Codeforces problems a user should re-attempt.
Populated by the cron/Celery background worker every 4 hours.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UpsolveTask(Base):
    __tablename__ = "upsolve_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem_url: Mapped[str] = mapped_column(String(500), nullable=True, default="")
    problem_name: Mapped[str] = mapped_column(String(255), nullable=True, default="")
    contest_id: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    rating: Mapped[int] = mapped_column(Integer, nullable=True, default=0)

    # Tags stored as JSON string: '["dp","graphs"]' — matches Go version behavior
    tags: Mapped[str] = mapped_column(Text, nullable=True, default="[]")

    # Status: "pending" (default), "solved", "skipped"
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    # Relationships
    user = relationship("User", back_populates="upsolve_tasks")

    def to_dict(self) -> dict:
        return {
            "ID": self.id,
            "CreatedAt": self.created_at.isoformat() if self.created_at else None,
            "UpdatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id,
            "problem_url": self.problem_url or "",
            "problem_name": self.problem_name or "",
            "contest_id": self.contest_id or 0,
            "rating": self.rating or 0,
            "tags": self.tags or "[]",
            "status": self.status,
        }
