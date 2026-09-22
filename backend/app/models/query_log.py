"""
QueryLog model — anti-cheat audit trail for every AI query.
Tracks prompt flagging and whether the response leaked a direct solution.
Enables computing the "direct-answer retrieval rate" metric.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)

    # Anti-cheat fields
    flagged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    flag_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Routing fields
    domain_predicted: Mapped[str | None] = mapped_column(String(50), nullable=True)
    domain_actual: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Post-hoc solution leak detection
    response_leaked_solution: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
