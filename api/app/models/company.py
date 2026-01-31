from sqlalchemy import Column, String, BigInteger, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), index=True)
    industry = Column(String(100))
    market_cap = Column(BigInteger, index=True)
    country = Column(String(3), default="USA")
    exchange = Column(String(20))
    description = Column(Text)
    website = Column(String(500))
    logo_url = Column(String(500))
    cik = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())

    # Relationships
    scores = relationship("SurvivalScore", back_populates="company", cascade="all, delete-orphan")
    fundamentals = relationship("Fundamental", back_populates="company", cascade="all, delete-orphan")
    holdings = relationship("PortfolioHolding", back_populates="company")
    watchlist_items = relationship("WatchlistItem", back_populates="company", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="company", cascade="all, delete-orphan")
