from sqlalchemy import Column, String, Boolean, Integer, Numeric, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    notes = Column(Text)
    target_score = Column(Numeric(5, 2))

    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())

    # Relationships
    user = relationship("UserProfile", back_populates="watchlist_items")
    company = relationship("Company", back_populates="watchlist_items")

    __table_args__ = (
        UniqueConstraint("user_id", "company_id", name="uq_user_watchlist_company"),
    )


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=True)

    alert_type = Column(String(50), nullable=False)

    # Conditions
    threshold_value = Column(Numeric(10, 2))
    threshold_direction = Column(String(10))
    change_percent = Column(Numeric(5, 2))

    # Status
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(String)
    trigger_count = Column(Integer, default=0)

    # Notification preferences
    notify_email = Column(Boolean, default=True)
    notify_push = Column(Boolean, default=True)

    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())

    # Relationships
    user = relationship("UserProfile", back_populates="alerts")
    company = relationship("Company", back_populates="alerts")
    portfolio = relationship("Portfolio", back_populates="alerts")
