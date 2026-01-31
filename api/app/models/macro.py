from sqlalchemy import Column, String, Date, Numeric
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..database import Base


class MacroData(Base):
    __tablename__ = "macro_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_date = Column(Date, nullable=False, unique=True, index=True)

    # Dollar Index
    dxy_value = Column(Numeric(10, 4))
    dxy_change_1d = Column(Numeric(8, 4))
    dxy_change_ytd = Column(Numeric(8, 4))

    # Precious Metals
    gold_price = Column(Numeric(10, 2))
    silver_price = Column(Numeric(10, 2))
    platinum_price = Column(Numeric(10, 2))

    # Key Commodities
    oil_wti_price = Column(Numeric(10, 2))
    copper_price = Column(Numeric(10, 2))

    # Money Supply
    m2_supply_trillions = Column(Numeric(10, 3))
    m2_yoy_change = Column(Numeric(8, 4))

    # Interest Rates
    fed_funds_rate = Column(Numeric(5, 2))
    ten_year_yield = Column(Numeric(5, 2))

    # Inflation
    cpi_yoy = Column(Numeric(5, 2))
    pce_yoy = Column(Numeric(5, 2))

    # Currency Pairs
    eur_usd = Column(Numeric(10, 6))
    usd_jpy = Column(Numeric(10, 4))
    gbp_usd = Column(Numeric(10, 6))
    usd_cny = Column(Numeric(10, 6))

    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
