from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date, datetime
from uuid import UUID


class ScoreBase(BaseModel):
    total_score: Decimal
    confidence: Decimal = Decimal("0.5")
    tier: Optional[str] = None

    # Factor scores
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


class ScoreCreate(ScoreBase):
    company_id: UUID
    score_date: date
    scoring_version: Optional[str] = None


class Score(ScoreBase):
    id: UUID
    company_id: UUID
    score_date: date
    scoring_version: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScoreHistory(BaseModel):
    score_date: date
    total_score: Decimal
    tier: Optional[str] = None


class FactorBreakdown(BaseModel):
    hard_assets: Decimal
    precious_metals: Decimal
    commodities: Decimal
    foreign_revenue: Decimal
    pricing_power: Decimal
    debt_structure: Decimal
    essential_services: Decimal


class ScoringResult(BaseModel):
    total_score: Decimal
    factors: FactorBreakdown
    tier: str
    scenario_scores: dict[str, Decimal]
    confidence: Decimal
