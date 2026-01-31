from sqlalchemy import Column, String, Date, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class SurvivalScore(Base):
    __tablename__ = "survival_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    score_date = Column(Date, nullable=False)

    # Overall score
    total_score = Column(Numeric(5, 2), nullable=False)
    confidence = Column(Numeric(3, 2), default=0.5)
    tier = Column(String(20))

    # Individual factor scores
    hard_assets_score = Column(Numeric(5, 2))
    precious_metals_score = Column(Numeric(5, 2))
    commodity_score = Column(Numeric(5, 2))
    foreign_revenue_score = Column(Numeric(5, 2))
    pricing_power_score = Column(Numeric(5, 2))
    debt_structure_score = Column(Numeric(5, 2))
    essential_services_score = Column(Numeric(5, 2))

    # Scenario-specific scores
    scenario_gradual = Column(Numeric(5, 2))
    scenario_rapid = Column(Numeric(5, 2))
    scenario_hyper = Column(Numeric(5, 2))

    # Metadata
    scoring_version = Column(String(20))
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())

    # Relationship
    company = relationship("Company", back_populates="scores")

    __table_args__ = (
        UniqueConstraint("company_id", "score_date", name="uq_company_score_date"),
    )
