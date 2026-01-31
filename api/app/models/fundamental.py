from sqlalchemy import Column, String, Integer, BigInteger, Date, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class Fundamental(Base):
    __tablename__ = "fundamentals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer)
    report_type = Column(String(10))

    # Balance Sheet
    total_assets = Column(BigInteger)
    tangible_assets = Column(BigInteger)
    intangible_assets = Column(BigInteger)
    current_assets = Column(BigInteger)
    total_liabilities = Column(BigInteger)
    total_debt = Column(BigInteger)
    cash_and_equivalents = Column(BigInteger)

    # Debt Structure
    short_term_debt = Column(BigInteger)
    long_term_debt = Column(BigInteger)
    fixed_rate_debt_pct = Column(Numeric(5, 2))
    floating_rate_debt_pct = Column(Numeric(5, 2))
    avg_debt_maturity_years = Column(Numeric(4, 1))
    avg_interest_rate = Column(Numeric(5, 2))

    # Revenue Breakdown
    total_revenue = Column(BigInteger)
    domestic_revenue = Column(BigInteger)
    domestic_revenue_pct = Column(Numeric(5, 2))
    foreign_revenue = Column(BigInteger)
    foreign_revenue_pct = Column(Numeric(5, 2))

    # Geographic Revenue Detail
    revenue_by_region = Column(JSONB)

    # Commodity/Asset Exposure
    commodity_revenue = Column(BigInteger)
    commodity_revenue_pct = Column(Numeric(5, 2))
    precious_metals_revenue = Column(BigInteger)
    precious_metals_revenue_pct = Column(Numeric(5, 2))

    # For Mining Companies
    proven_reserves_oz = Column(BigInteger)
    probable_reserves_oz = Column(BigInteger)
    reserve_value_usd = Column(BigInteger)
    production_cost_per_oz = Column(Numeric(10, 2))

    # Profitability
    gross_profit = Column(BigInteger)
    gross_margin = Column(Numeric(5, 2))
    operating_income = Column(BigInteger)
    operating_margin = Column(Numeric(5, 2))
    net_income = Column(BigInteger)
    net_margin = Column(Numeric(5, 2))

    # Stability Metrics
    gross_margin_5yr_avg = Column(Numeric(5, 2))
    gross_margin_5yr_std = Column(Numeric(5, 2))
    revenue_growth_3yr_cagr = Column(Numeric(5, 2))

    # Source
    filing_url = Column(String(500))
    filing_date = Column(Date)

    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())

    # Relationship
    company = relationship("Company", back_populates="fundamentals")

    __table_args__ = (
        UniqueConstraint("company_id", "fiscal_year", "fiscal_quarter", name="uq_company_fiscal_period"),
    )
