"""
RoutingLog model — tracks domain routing accuracy for benchmarking.
Each row logs what domain the orchestrator predicted for a sub-task
and what the validated/ground-truth domain was (if available).
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RoutingLog(Base):
    __tablename__ = "routing_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    query_id: Mapped[int] = mapped_column(Integer, ForeignKey("query_logs.id"), nullable=True)
    sub_task: Mapped[str] = mapped_column(Text, nullable=True)

    predicted_domain: Mapped[str] = mapped_column(String(50), nullable=False)
    validated_domain: Mapped[str | None] = mapped_column(String(50), nullable=True)
    correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
