from sqlalchemy import Column, String, Integer, Date, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..database import Base


class ScoringRun(Base):
    __tablename__ = "scoring_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_date = Column(Date, nullable=False)

    # Stats
    companies_scored = Column(Integer)
    companies_failed = Column(Integer)
    avg_score = Column(Numeric(5, 2))
    median_score = Column(Numeric(5, 2))

    # Performance
    duration_seconds = Column(Integer)
    scoring_version = Column(String(20))

    # Status
    status = Column(String(20))
    error_message = Column(Text)

    started_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    completed_at = Column(String)
