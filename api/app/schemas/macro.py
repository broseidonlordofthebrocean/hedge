from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date, datetime


class MacroDataBase(BaseModel):
    # Dollar Index
    dxy_value: Optional[Decimal] = None
    dxy_change_1d: Optional[Decimal] = None
    dxy_change_ytd: Optional[Decimal] = None

    # Precious Metals
    gold_price: Optional[Decimal] = None
    silver_price: Optional[Decimal] = None
    platinum_price: Optional[Decimal] = None

    # Commodities
    oil_wti_price: Optional[Decimal] = None
    copper_price: Optional[Decimal] = None

    # Money Supply
    m2_supply_trillions: Optional[Decimal] = None
    m2_yoy_change: Optional[Decimal] = None

    # Interest Rates
    fed_funds_rate: Optional[Decimal] = None
    ten_year_yield: Optional[Decimal] = None

    # Inflation
    cpi_yoy: Optional[Decimal] = None
    pce_yoy: Optional[Decimal] = None


class MacroData(MacroDataBase):
    data_date: date

    # Currency Pairs
    eur_usd: Optional[Decimal] = None
    usd_jpy: Optional[Decimal] = None
    gbp_usd: Optional[Decimal] = None
    usd_cny: Optional[Decimal] = None

    created_at: datetime

    class Config:
        from_attributes = True


class MacroMetric(BaseModel):
    current: Optional[Decimal] = None
    change_1d: Optional[Decimal] = None
    change_ytd: Optional[Decimal] = None


class MacroRates(BaseModel):
    fed_funds: Optional[Decimal] = None
    ten_year: Optional[Decimal] = None


class MacroDashboard(BaseModel):
    dxy: MacroMetric
    gold: MacroMetric
    silver: MacroMetric
    m2: dict
    rates: MacroRates
    updated_at: str
