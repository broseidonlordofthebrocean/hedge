from sqlalchemy import Column, String, Boolean, Numeric, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_primary = Column(Boolean, default=False)

    # Cached aggregate scores
    total_value = Column(Numeric(15, 2))
    survival_score = Column(Numeric(5, 2))
    scenario_gradual_score = Column(Numeric(5, 2))
    scenario_rapid_score = Column(Numeric(5, 2))
    scenario_hyper_score = Column(Numeric(5, 2))

    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())

    # Relationships
    user = relationship("UserProfile", back_populates="portfolios")
    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="portfolio", cascade="all, delete-orphan")


class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    shares = Column(Numeric(15, 4), nullable=False)
    cost_basis = Column(Numeric(15, 2))
    cost_per_share = Column(Numeric(15, 4))

    # Cached current values
    current_price = Column(Numeric(15, 4))
    current_value = Column(Numeric(15, 2))
    gain_loss = Column(Numeric(15, 2))
    gain_loss_pct = Column(Numeric(8, 4))

    notes = Column(Text)
    added_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    company = relationship("Company", back_populates="holdings")

    __table_args__ = (
        UniqueConstraint("portfolio_id", "company_id", name="uq_portfolio_company"),
    )
