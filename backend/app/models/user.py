"""
User model — identity, platform handles, cached stats, and unified Strata rating.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    # Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    college_id: Mapped[str] = mapped_column(String(100), nullable=True, default="")

    # Platform handles
    codeforces_handle: Mapped[str] = mapped_column(String(100), nullable=True, default="")
    codechef_handle: Mapped[str] = mapped_column(String(100), nullable=True, default="")
    github_handle: Mapped[str] = mapped_column(String(100), nullable=True, default="")
    kaggle_handle: Mapped[str] = mapped_column(String(100), nullable=True, default="")
    ctf_handle: Mapped[str] = mapped_column(String(100), nullable=True, default="")

    # Wing interests — stored as JSONB array: ["CP", "ML", "Web"]
    wings: Mapped[list] = mapped_column(JSONB, default=list)

    # Cached stats (refreshed via /api/user/refresh and daily cron)
    codeforces_rating: Mapped[int] = mapped_column(Integer, default=0)
    codechef_rating: Mapped[int] = mapped_column(Integer, default=0)
    total_solved: Mapped[int] = mapped_column(Integer, default=0)
    github_repos: Mapped[int] = mapped_column(Integer, default=0)

    # Unified cross-domain rating
    axios_rating: Mapped[int] = mapped_column(Integer, default=0)

    # Admin flag
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    shadow_memories = relationship("ShadowMemory", back_populates="user", lazy="selectin")
    upsolve_tasks = relationship("UpsolveTask", back_populates="user", lazy="selectin")

    def to_dict(self) -> dict:
        """Serialize to dict matching the Go/Gin JSON output shape for frontend compatibility."""
        return {
            "ID": self.id,
            "CreatedAt": self.created_at.isoformat() if self.created_at else None,
            "UpdatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "DeletedAt": self.deleted_at.isoformat() if self.deleted_at else None,
            "name": self.name,
            "email": self.email,
            "college_id": self.college_id or "",
            "codeforces_handle": self.codeforces_handle or "",
            "codechef_handle": self.codechef_handle or "",
            "github_handle": self.github_handle or "",
            "kaggle_handle": self.kaggle_handle or "",
            "ctf_handle": self.ctf_handle or "",
            "wings": self.wings or [],
            "codeforces_rating": self.codeforces_rating,
            "codechef_rating": self.codechef_rating,
            "total_solved": self.total_solved,
            "github_repos": self.github_repos,
            "axios_rating": self.axios_rating,
            "is_admin": self.is_admin,
        }
