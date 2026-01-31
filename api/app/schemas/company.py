from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from uuid import UUID


class CompanyBase(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[int] = None
    country: str = "USA"
    exchange: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyCreate(CompanyBase):
    cik: Optional[str] = None


class CompanyWithScore(CompanyBase):
    id: UUID
    score: Optional[Decimal] = None
    tier: Optional[str] = None
    score_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class CompanyDetail(CompanyWithScore):
    cik: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    # Current score breakdown
    hard_assets_score: Optional[Decimal] = None
    precious_metals_score: Optional[Decimal] = None
    commodity_score: Optional[Decimal] = None
    foreign_revenue_score: Optional[Decimal] = None
    pricing_power_score: Optional[Decimal] = None
    debt_structure_score: Optional[Decimal] = None
    essential_services_score: Optional[Decimal] = None

    # Scenario scores
    scenario_gradual: Optional[Decimal] = None
    scenario_rapid: Optional[Decimal] = None
    scenario_hyper: Optional[Decimal] = None


class CompanySearch(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None
    score: Optional[Decimal] = None


class Pagination(BaseModel):
    page: int
    limit: int
    total: int
    pages: int


class CompanyList(BaseModel):
    data: list[CompanyWithScore]
    pagination: Pagination
