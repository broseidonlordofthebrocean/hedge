from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from uuid import UUID


class HoldingBase(BaseModel):
    shares: Decimal
    cost_basis: Optional[Decimal] = None
    cost_per_share: Optional[Decimal] = None
    notes: Optional[str] = None


class HoldingCreate(HoldingBase):
    ticker: str


class HoldingUpdate(BaseModel):
    shares: Optional[Decimal] = None
    cost_basis: Optional[Decimal] = None
    notes: Optional[str] = None


class Holding(HoldingBase):
    id: UUID
    portfolio_id: UUID
    company_id: UUID
    ticker: str
    company_name: str
    current_price: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    gain_loss: Optional[Decimal] = None
    gain_loss_pct: Optional[Decimal] = None
    survival_score: Optional[Decimal] = None
    added_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PortfolioSummary(PortfolioBase):
    id: UUID
    is_primary: bool = False
    total_value: Optional[Decimal] = None
    survival_score: Optional[Decimal] = None
    holdings_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class PortfolioDetail(PortfolioSummary):
    holdings: list[Holding] = []
    scenario_gradual_score: Optional[Decimal] = None
    scenario_rapid_score: Optional[Decimal] = None
    scenario_hyper_score: Optional[Decimal] = None
    updated_at: datetime


class PortfolioAnalysis(BaseModel):
    overall_score: Optional[Decimal] = None
    weighted_by_value: Optional[Decimal] = None
    scenario_scores: dict[str, Optional[Decimal]]
    factor_breakdown: dict[str, dict]
    sector_allocation: list[dict]
    risk_concentrations: list[dict]
    recommendations: list[dict]


class ScenarioImpact(BaseModel):
    scenario: str
    portfolio_impact: dict
    holdings_impact: list[dict]
