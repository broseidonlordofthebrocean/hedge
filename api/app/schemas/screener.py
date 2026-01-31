from pydantic import BaseModel
from typing import Optional


class ScreenerFilters(BaseModel):
    sectors: Optional[list[str]] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    min_market_cap: Optional[int] = None
    max_market_cap: Optional[int] = None
    min_foreign_revenue_pct: Optional[float] = None
    min_hard_assets_score: Optional[float] = None
    min_precious_metals_score: Optional[float] = None
    min_commodity_score: Optional[float] = None
    min_pricing_power_score: Optional[float] = None
    has_dividend: Optional[bool] = None
    countries: Optional[list[str]] = None
    tiers: Optional[list[str]] = None


class ScreenerRequest(BaseModel):
    filters: ScreenerFilters
    sort_by: str = "total_score"
    sort_order: str = "desc"
    page: int = 1
    limit: int = 50


class ScreenerPreset(BaseModel):
    id: str
    name: str
    description: str
    filters: ScreenerFilters


class FilterSummary(BaseModel):
    matched: int
    total_universe: int
