from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    key_hash = Column(String(255), nullable=False)
    key_prefix = Column(String(10), nullable=False, index=True)
    name = Column(String(100))

    # Rate limiting
    rate_limit_per_hour = Column(Integer, default=100)
    rate_limit_per_month = Column(Integer, default=10000)

    # Usage tracking
    requests_this_hour = Column(Integer, default=0)
    requests_this_month = Column(Integer, default=0)
    last_used_at = Column(String)

    is_active = Column(Boolean, default=True)
    expires_at = Column(String)

    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())

    # Relationship
    user = relationship("UserProfile", back_populates="api_keys")
