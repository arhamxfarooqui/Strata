"""
ShadowMemory model — per-user proficiency tracking with decay, confidence, and mistake patterns.

This is the "brain" that makes the AI personalized. Before every AI call, the system queries
the weakest concepts for this user+domain and injects them into the LLM system prompt.

Enhanced from Go version:
  - Proficiency is now float 0.0-1.0 (was int 1-10) for finer granularity
  - Confidence score tracks how certain we are about the proficiency
  - Mistake count tracks repeated failures
  - Decay rate enables time-based proficiency decay
"""

import math
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ShadowMemory(Base):
    __tablename__ = "shadow_memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    concept: Mapped[str] = mapped_column(String(255), nullable=False)

    # Proficiency: 0.0 (no knowledge) to 1.0 (mastery). Default 0.5 = mid-level.
    proficiency: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Confidence: 0.0 (no data) to 1.0 (very sure). Increases with more observations.
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.1)

    # Mistake count: running total of times the user struggled with this concept.
    mistake_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Decay rate: proficiency decays by this factor per week of inactivity.
    # effective_proficiency = proficiency * exp(-decay_rate * weeks_since_last_noted)
    decay_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.05)

    last_noted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="shadow_memories")

    @property
    def effective_proficiency(self) -> float:
        """Apply time-decay to get the current effective proficiency."""
        if self.last_noted_at is None:
            return self.proficiency

        now = datetime.now(self.last_noted_at.tzinfo)
        weeks_elapsed = (now - self.last_noted_at).total_seconds() / (7 * 24 * 3600)
        decayed = self.proficiency * math.exp(-self.decay_rate * weeks_elapsed)
        return max(0.0, min(1.0, decayed))

    @property
    def display_score(self) -> int:
        """Convert 0.0-1.0 proficiency to 1-10 int for frontend/API compatibility."""
        return max(1, min(10, round(self.effective_proficiency * 10)))

    def to_dict(self) -> dict:
        return {
            "ID": self.id,
            "CreatedAt": self.created_at.isoformat() if self.created_at else None,
            "UpdatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id,
            "domain": self.domain,
            "concept": self.concept,
            "proficiency": self.display_score,
            "last_noted_at": self.last_noted_at.isoformat() if self.last_noted_at else None,
        }
